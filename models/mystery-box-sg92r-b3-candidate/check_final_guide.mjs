import {spawn} from 'node:child_process';
import {writeFileSync,mkdtempSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
const root='C:/Users/kouga/Documents/Codex/2026-10-05/task/sg92r_cube_B3_20261008';
const profile=mkdtempSync(join(tmpdir(),'sg92r_B3_final_cdp_'));
const cp=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless','--remote-debugging-pipe','--disable-gpu','--disable-background-networking','--disable-extensions','--disable-component-update','--no-first-run',`--user-data-dir=${profile}`],{stdio:['ignore','pipe','pipe','pipe','pipe'],windowsHide:true});
let next=1,buf='',errors='';const pending=new Map();
cp.stderr.on('data',b=>errors+=b.toString());
cp.stdio[4].on('data',b=>{buf+=b.toString();let k;while((k=buf.indexOf('\0'))>=0){const t=buf.slice(0,k);buf=buf.slice(k+1);if(!t)continue;const m=JSON.parse(t);const p=pending.get(m.id);if(p){pending.delete(m.id);m.error?p.reject(new Error(JSON.stringify(m.error))):p.resolve(m.result);}}});
const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=next++;pending.set(id,{resolve,reject});cp.stdio[3].write(JSON.stringify({id,method,params,...sessionId?{sessionId}:{}})+'\0');});
const timeout=setTimeout(()=>{cp.kill();process.exitCode=1;},45000);
try {
 const target=await send('Target.createTarget',{url:'about:blank'});const {sessionId}=await send('Target.attachToTarget',{targetId:target.targetId,flatten:true});await send('Page.enable',{},sessionId);
 const checks=[];
 for(const width of [375,1280]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:1100,deviceScaleFactor:1,mobile:false},sessionId);
  await send('Page.navigate',{url:pathToFileURL(join(root,'B3_print_assembly_guide.html')).href},sessionId);
  const r=await send('Runtime.evaluate',{expression:`(async()=>{await new Promise(r=>document.readyState==='complete'?r():window.addEventListener('load',r,{once:true}));await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));const t=[...document.querySelectorAll('table')];return {viewport:innerWidth,bodyWidth:document.body.scrollWidth,documentWidth:document.documentElement.scrollWidth,images:[...document.images].map(i=>({complete:i.complete,naturalWidth:i.naturalWidth})),partsRows:t[t.length-1].querySelectorAll('tbody tr').length};})()`,awaitPromise:true,returnByValue:true},sessionId);
  const q=r.result.value;if(q.viewport!==width||q.bodyWidth>width||q.documentWidth>width||q.partsRows!==22||q.images.some(i=>!i.complete||i.naturalWidth===0))throw new Error(JSON.stringify(q));checks.push(q);
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},sessionId);writeFileSync(join(root,'docs',`guide_${width}px.png`),Buffer.from(shot.data,'base64'));
 }
 writeFileSync(join(root,'guide_visual_check.json'),JSON.stringify({checks,method:'Local Chrome DevTools; image decoding, 22-part table and viewport overflow checked'},null,2));console.log(JSON.stringify(checks));await send('Browser.close');
}catch(e){console.error(e.message);writeFileSync(join(root,'guide_check_stderr.txt'),errors);cp.kill();process.exitCode=1;}finally{clearTimeout(timeout);}
