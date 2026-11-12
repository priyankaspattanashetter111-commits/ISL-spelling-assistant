import express from 'express';
import {MongoClient} from 'mongodb';
import {readFile,writeFile,mkdir,rename} from 'node:fs/promises';
import {randomUUID} from 'node:crypto';
import {suggestions} from '../shared/core.mjs';
const app=express();app.use(express.json({limit:'2mb'}));
const mode=process.env.STORAGE||'json';let db,client,local={vocabulary:[],history:[],practice:[]};
await mkdir('data',{recursive:true});
if(mode==='mongo'){client=new MongoClient(process.env.MONGO_URI||'mongodb://127.0.0.1:27017',{serverSelectionTimeoutMS:5000});await client.connect();db=client.db('isl_spelling');await db.collection('vocabulary').createIndex({word:1},{unique:true});}
else {try{local=JSON.parse(await readFile('data/demo.json','utf8'))}catch(e){if(e.code!=='ENOENT')throw e}}
let queue=Promise.resolve();
function mutate(fn){const task=queue.then(async()=>{const result=await fn();if(!db){await writeFile('data/demo.tmp',JSON.stringify(local,null,2));await rename('data/demo.tmp','data/demo.json')}return result});queue=task.catch(()=>{});return task}
const list=async c=>db?db.collection(c).find({},{projection:{_id:0}}).sort({createdAt:-1}).limit(500).toArray():[...local[c]].reverse().slice(0,500);
const words='COVID HELLO HELP HOSPITAL INDIA INDIAN LANGUAGE SIGN SCHOOL COLLEGE COMPUTER SCIENCE STUDENT PROJECT THANKS THANK YOU PLEASE WATER FOOD DOCTOR EMERGENCY FAMILY FRIEND GOOD MORNING NAME WORLD WELCOME ACCESSIBLE SPELL SPELLING TEST BOOK LETTER LEARN'.split(' ');
const ml=process.env.ML_URL||'http://127.0.0.1:8000';
async function callML(path,body){const r=await fetch(ml+path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined,signal:AbortSignal.timeout(20000)});const j=await r.json();if(!r.ok){const e=new Error(j.detail||'ML service rejected the request');e.status=r.status;throw e}return j}
app.get('/api/health',async(req,res)=>{let recognition;try{recognition=await callML('/health')}catch{recognition={available:false,model:false}}res.json({storage:mode,recognition})});
app.get('/api/suggestions',async(req,res)=>res.json(suggestions(String(req.query.q||'').slice(0,64),[...words,...(await list('vocabulary')).map(x=>x.word)])));
for(const c of ['vocabulary','history','practice']){
 app.get('/api/'+c,async(req,res)=>res.json(await list(c)));
 app.post('/api/'+c,async(req,res)=>{const b=req.body;let doc={id:randomUUID(),createdAt:new Date().toISOString()};
  if(c==='vocabulary'){const word=String(b.word||'').trim().toUpperCase();if(!/^[A-Z][A-Z ]{0,63}$/.test(word))return res.status(400).json({error:'Use 1–64 English letters/spaces.'});doc={...doc,word};}
  if(c==='history'){const text=String(b.text||'').trim();if(!text||text.length>2000)return res.status(400).json({error:'Enter 1–2000 characters.'});doc={...doc,text}}
  if(c==='practice'){if(!/^[A-Z]$/.test(b.target)||!String(b.predicted||''))return res.status(400).json({error:'Target and prediction required'});doc={...doc,target:b.target,predicted:String(b.predicted).slice(0,64),correct:b.target===b.predicted}}
  await mutate(async()=>{if(db){if(c==='vocabulary')await db.collection(c).updateOne({word:doc.word},{$setOnInsert:doc},{upsert:true});else await db.collection(c).insertOne(doc)}else{if(c!=='vocabulary'||!local[c].some(x=>x.word===doc.word))local[c].push(doc)}});res.status(201).json(doc)
 });
 app.delete('/api/'+c+'/:id',async(req,res)=>{await mutate(async()=>{if(db)await db.collection(c).deleteOne({id:req.params.id});else local[c]=local[c].filter(x=>x.id!==req.params.id)});res.json({ok:true})});
}
for(const path of ['frame','sample','train'])app.post('/api/'+path,async(req,res)=>res.json(await callML('/'+path,req.body)));
app.use(express.static('dist'));
app.use((err,req,res,next)=>{console.error(err.message);res.status(err.status||503).json({error:err.message})});
app.listen(3001,'127.0.0.1',()=>console.log(`API ready http://127.0.0.1:3001 (${mode} storage)`));
