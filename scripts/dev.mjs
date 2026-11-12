import {spawn} from 'node:child_process';
const children=[spawn(process.execPath,['backend/server.mjs'],{stdio:'inherit'}),spawn(process.execPath,['node_modules/vite/bin/vite.js','--config','frontend/vite.config.js','--configLoader','native'],{stdio:'inherit'})];
function stop(){children.forEach(c=>c.kill())}process.on('SIGINT',()=>{stop();process.exit()});process.on('SIGTERM',stop);children.forEach(c=>c.on('exit',code=>{stop();process.exit(code||0)}));
