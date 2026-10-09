// 位置はm、元CADはZ上。各時刻を確定配置から再計算し、加算更新しない。
import { Quaternion, Vector3 } from './vendor/three.module.js';
import { NAMES, STOCK, UNIT, STEPS, SHA } from './steps.mjs';
export const IDENTITY=[0,0,0,1];
const v=a=>new Vector3(...a);
const q=a=>new Quaternion(...a).normalize();
const add=(a,b)=>a.map((n,i)=>n+b[i]);
const mm=a=>a.map(n=>n/1000);
const copy=x=>JSON.parse(JSON.stringify(x));
const pose=(position,quaternion=IDENTITY)=>({position:[...position],quaternion:[...quaternion]});
const routeMesh=name=>name==='REFERENCE SG92R wire'||name.startsWith('REFERENCE speaker lead');
export { routeMesh };
export function bounds(vertices){
  const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
  for(let i=0;i<vertices.length;i+=3)for(let j=0;j<3;j++){min[j]=Math.min(min[j],vertices[i+j]);max[j]=Math.max(max[j],vertices[i+j]);}
  return {min,max,center:min.map((n,i)=>(n+max[i])/2)};
}
export function createAssembly(cad,manifest){
  if(cad.source_sha256!==SHA||manifest.source_blend_sha256!==SHA)throw Error('CADの版がB3の確定版と一致しません。');
  const printed=manifest.parts.map((p,i)=>({id:p.name.slice(0,2),name:NAMES[i],source:p.name,kind:'印刷品',meshes:[p.name],printQ:[p.print_axis[1],p.print_axis[2],p.print_axis[3],p.print_axis[0]],quantity:p.quantity}));
  const items=[...printed,...STOCK.map(s=>({...s,source:s.meshes[0],kind:s.id==='S3'?'任意・参考外形':'実物部品',quantity:1,printQ:IDENTITY}))];
  if(printed.length!==22||new Set(items.map(p=>p.id)).size!==25)throw Error('部品数またはIDの不整合。');
  const owners=new Map();
  for(const item of items){
    const vertices=[];
    for(const name of item.meshes){const m=cad.parts.find(p=>p.name===name);if(!m||owners.has(name))throw Error(`メッシュの所有が不正: ${name}`);owners.set(name,item.id);if(!routeMesh(name))vertices.push(...m.vertices);}
    item.center=bounds(vertices).center;
    item.vertices=vertices;
    item.home=pose(item.center);
  }
  if(owners.size!==cad.parts.length)throw Error('所属のないCADメッシュがあります。');
  const byId=Object.fromEntries(items.map(p=>[p.id,p]));
  const initial={};
  items.forEach((item,i)=>{
    const verts=[];const orientation=q(item.printQ);
    for(let j=0;j<item.vertices.length;j+=3)verts.push(...v(item.vertices.slice(j,j+3)).sub(v(item.center)).applyQuaternion(orientation).toArray());
    const b=bounds(verts);const x=-.47+(i%5)*.103,y=.11+Math.floor(i/5)*.103;
    initial[item.id]=pose([x,y,-.108-b.min[2]],orientation.toArray());
    item.initialBounds={min:add(b.min,initial[item.id].position),max:add(b.max,initial[item.id].position)};
  });
  const home=(id,offset=[0,0,0],angle=0,pivot=null)=>{
    const item=byId[id];let center=[...item.center];const orient=new Quaternion().setFromAxisAngle(new Vector3(0,0,1),angle*Math.PI/180);
    if(pivot)center=v(center).sub(v(mm(pivot))).applyQuaternion(orient).add(v(mm(pivot))).toArray();
    return pose(add(center,mm(offset)),orient.toArray());
  };
  const snapshots=[copy(initial)],transitions=[[]];
  const firstStep={};
  const bench=[180,0,0];
  function frame(poses,label,scope='transport',audit=null){return {poses:copy(poses),label,scope,audit};}
  for(let index=1;index<STEPS.length;index++){
    const step=STEPS[index],r=step.route,ids=step.ids,previous=snapshots[index-1],points=[];
    const base={};for(const id of ids)base[id]=previous[id];
    points.push(frame(base,'開始位置'));
    const targetOffset=r.bench?bench:[0,0,0];
    function at(offset,angle=0,pivot=null){return Object.fromEntries(ids.map(id=>[id,home(id,add(targetOffset,offset),angle,pivot)]));}
    function append(poses,label,scope='transport'){points.push(frame(poses,label,scope,r.audit||null));}
    function carry(entry){
      // 持ち込みは公称挿入ストロークと区別。最初に十分上へ、空中で姿勢を揃える。
      const raised=Object.fromEntries(ids.map(id=>[id,pose([previous[id].position[0],previous[id].position[1],.25],previous[id].quaternion)]));
      append(raised,'取り上げる（取り回し未検証）');
      const rotated=Object.fromEntries(ids.map(id=>[id,pose(raised[id].position,entry[id].quaternion)]));
      append(rotated,'空中で向きを合わせる（未検証）');
      const above=Object.fromEntries(ids.map(id=>[id,pose([entry[id].position[0],entry[id].position[1],.25],entry[id].quaternion)]));
      append(above,'挿入位置の上へ運ぶ（未検証）');append(entry,'挿入の開始位置へ（持ち込み未検証）');
    }
    if(r.type==='place') {carry(at([0,0,100]));append(at([0,0,0]),'作業位置へ置く','placement');}
    if(r.type==='entry') {
      const off=[0,0,0];off['xyz'.indexOf(r.axis)]=r.travel;
      if(index===3){carry(at([6.8,5,0]));append(at(off),'箱内でYを合わせる（持ち込み未検証）');}
      else if(index===21){carry(at([40,0,0]));append(at(off),'蓋の外側から挿入位置へ（持ち込み未検証）');}
      else carry(at(off));
      append(at([0,0,0]),`−${r.axis.toUpperCase()}方向へ入れる`,'insertion');
    }
    if(r.type==='bolt-in') {carry(at([-1,1.6,20]));append(at([-1,1.6,3.7]),'Z+3.7まで下げる','insertion');append(at([-1,0,3.7]),'Yを戻す','insertion');append(at([0,0,3.7]),'Xを戻す','insertion');append(at([0,0,0]),'底へ下げる','insertion');}
    if(r.type==='bottom'){
      const id=ids[0],entry=home(id,[0,0,-15],90,r.pivot);
      const raised=pose([previous[id].position[0],previous[id].position[1],.25],previous[id].quaternion);
      append({[id]:raised},'取り上げる（未検証）');
      append({[id]:pose(raised.position,entry.quaternion)},'90°の向きにする（未検証）');
      append({[id]:pose([-.11,entry.position[1],.25],entry.quaternion)},'箱の外側へ回す（未検証）');
      append({[id]:pose([-.11,entry.position[1],-.08],entry.quaternion)},'箱の外側を通り、底より下へ（未検証）');
      append({[id]:pose([entry.position[0],entry.position[1],-.08],entry.quaternion)},'底の挿入位置へ回す（未検証）');
      append({[id]:entry},'底の開始位置へ（未検証）');
      append(at([0,0,0],90,r.pivot),'底から+Zへ入れる','insertion');
      if(r.lift)append(at([0,0,r.lift],90,r.pivot),'1.8mm持ち上げる','insertion');
      append(at([0,0,r.lift],0,r.pivot),'0°へ回す','insertion');
      if(r.lift)append(at([0,0,0]),'1.8mm下げる','insertion');
    }
    if(r.type==='release') {append(at([0,0,1.8]),'1.8mm持ち上げる','insertion');append(at([5.9,0,1.8]),'+Xへ5.9mm','insertion');append(at([5.9,0,0]),'下げてR','insertion');}
    if(r.type==='lock') {append(at([5.9,0,1.8]),'1.8mm持ち上げる','insertion');append(at([0,0,1.8]),'−Xへ5.9mm','insertion');append(at([0,0,0]),'横力を抜いて下げる','insertion');}
    if(r.type==='unit'){
      append(at([180,0,210]),'固定部を保持して上へ（未検証）');
      append(at([0,0,210]),'箱の真上へ（未検証）');
      append(at([0,0,76]),'垂直挿入の開始位置へ（未検証）');
      append(at([0,0,0]),'真上から76mm下げる','insertion');
    }
    if(points.length<2)throw Error(`手順${index}に配置がない。`);
    const final=copy(previous);Object.assign(final,copy(points.at(-1).poses));snapshots.push(final);transitions.push(points);
    for(const id of ids)if(firstStep[id]===undefined)firstStep[id]=index;
  }
  const freeze=x=>{Object.freeze(x);for(const y of Object.values(x))if(y&&typeof y==='object'&&!Object.isFrozen(y))freeze(y);return x;};
  freeze(snapshots);freeze(transitions);
  function sample(index,fraction=1){
    index=Math.max(0,Math.min(STEPS.length-1,Math.trunc(index)));fraction=Math.max(0,Math.min(1,fraction));
    if(index===0)return {poses:copy(snapshots[0]),label:'部品一覧',scope:'settled'};
    if(fraction===1)return {poses:copy(snapshots[index]),label:'この手順の完了位置',scope:'settled'};
    const points=transitions[index],time=fraction*(points.length-1),segment=Math.floor(time),u=time-segment,a=points[segment],b=points[segment+1];
    const poses=copy(snapshots[index-1]);
    for(const id of STEPS[index].ids){
      const p=a.poses[id],end=b.poses[id],orientation=q(p.quaternion).slerp(q(end.quaternion),u);
      let position=v(p.position).lerp(v(end.position),u);
      // 底部の回転では指定した軸を固定し、部品中心の直線補間で代用しない。
      if(STEPS[index].route.type==='bottom'&&b.scope==='insertion'&&q(p.quaternion).angleTo(q(end.quaternion))>1e-7){
        const pivot=v(mm(STEPS[index].route.pivot)),relative=v(byId[id].center).sub(pivot);
        const aCenter=relative.clone().applyQuaternion(q(p.quaternion)).add(pivot);
        const bCenter=relative.clone().applyQuaternion(q(end.quaternion)).add(pivot);
        const offset=v(p.position).sub(aCenter).lerp(v(end.position).sub(bCenter),u);
        position=relative.applyQuaternion(orientation).add(pivot).add(offset);
      }
      poses[id]=pose(position.toArray(),orientation.toArray());
    }
    return {poses,label:b.label,scope:b.scope,audit:b.audit,segment};
  }
  return {cad,items,byId,owners,snapshots,transitions,firstStep,sample};
}
export class Playback {
  constructor(count,reduced=false,gates=[]){this.count=count;this.reduced=reduced;this.gates=new Set(gates);this.index=0;this.fraction=1;this.running=false;this.speed=1;this.mode='single';this.phase='settled';this.dwell=2;this.dwellElapsed=0;this.pauseReason='';}
  seek(index){this.index=Math.max(0,Math.min(this.count-1,Math.trunc(index)));this.fraction=1;this.running=false;this.mode='single';this.phase='settled';this.dwellElapsed=0;this.pauseReason='';}
  play(){if(this.running)return;this.mode='single';this.pauseReason='';this.phase='motion';if(this.fraction===1){if(this.index===0)this.index=1;this.fraction=0;}if(this.reduced){this.fraction=1;this.running=false;this.phase='settled';}else this.running=true;}
  startAuto(){
    if(this.running&&this.mode==='auto')return;
    const resuming=this.mode==='auto';this.mode='auto';this.pauseReason='';
    if(resuming&&this.phase==='gate')return;
    if(resuming&&this.phase==='complete')return;
    if(!resuming){this.dwellElapsed=0;this.phase=this.fraction<1?'motion':'dwell';if(this.fraction===1&&this.gates.has(this.index)){this.phase='gate';this.running=false;return;}}
    this.running=true;
  }
  continuePreview(){if(this.mode!=='auto'||this.phase!=='gate')return;this.phase='dwell';this.dwellElapsed=0;this.pauseReason='';this.running=true;}
  pause(reason=''){this.running=false;this.pauseReason=reason;}
  setDwell(value){if(Number.isFinite(value))this.dwell=Math.max(.5,Math.min(15,value));}
  finishMotion(){
    this.fraction=1;
    if(this.mode==='single'){this.running=false;this.phase='settled';return;}
    if(this.gates.has(this.index)){this.running=false;this.phase='gate';return;}
    if(this.index===this.count-1){this.running=false;this.phase='complete';return;}
    this.phase='dwell';this.dwellElapsed=0;
  }
  tick(seconds){
    if(!this.running||!Number.isFinite(seconds)||seconds<0)return;
    // 1回の更新で境界を1つだけ進める。残り時間を次工程へ持ち越さない。
    if(this.phase==='motion'){this.fraction=this.reduced?1:Math.min(1,this.fraction+seconds*this.speed/9);if(this.fraction===1)this.finishMotion();return;}
    if(this.mode==='auto'&&this.phase==='dwell'){
      this.dwellElapsed=Math.min(this.dwell,this.dwellElapsed+seconds);
      if(this.dwellElapsed<this.dwell)return;
      if(this.index===this.count-1){this.running=false;this.phase='complete';return;}
      this.index++;this.fraction=0;this.phase='motion';this.dwellElapsed=0;
    }
  }
  setSpeed(value){if(Number.isFinite(value)&&value>0)this.speed=Math.max(.25,Math.min(4,value));}
}
