export function distance(a,b){const d=Array.from({length:a.length+1},(_,i)=>[i]);for(let j=1;j<=b.length;j++)d[0][j]=j;for(let i=1;i<=a.length;i++)for(let j=1;j<=b.length;j++)d[i][j]=Math.min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(a[i-1]===b[j-1]?0:1));return d[a.length][b.length]}
export function suggestions(prefix,words){prefix=prefix.toUpperCase();if(!prefix)return [];return [...new Set(words)].map(word=>({word,rank:word.startsWith(prefix)?-1:distance(prefix,word)})).filter(x=>x.rank<0||x.rank<=Math.max(1,Math.floor(prefix.length/3))).sort((a,b)=>a.rank-b.rank||a.word.length-b.word.length||a.word.localeCompare(b.word)).slice(0,6).map(x=>x.word)}
// A release gap is required even between identical letters (HELLO).
export class Stabilizer{
 constructor(){this.reset()}
 reset(){this.candidate=null;this.since=0;this.locked=false;this.blankSince=null}
 update(label,confidence,now,threshold=.8,hold=700){
  if(!label){this.candidate=null;if(this.blankSince===null)this.blankSince=now;if(now-this.blankSince>=350)this.locked=false;return null}
  this.blankSince=null;
  if(confidence<threshold){this.candidate=null;return null}
  if(this.locked)return null;
  if(this.candidate!==label){this.candidate=label;this.since=now;return null}
  if(now-this.since>=hold){this.locked=true;this.candidate=null;return label}return null
 }
}
