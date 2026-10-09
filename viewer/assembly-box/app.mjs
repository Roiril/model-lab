import * as THREE from './vendor/three.module.js';
import {OrbitControls} from './vendor/OrbitControls.js';
import {createAssembly,Playback,routeMesh} from './core.mjs';
import {meshGeometry} from './render_geometry.mjs';
import {STEPS,NAMES,STOCK,LIMITS,AUTO_HOLDS} from './steps.mjs';
const $=id=>document.getElementById(id), reduced=matchMedia('(prefers-reduced-motion: reduce)');
const player=new Playback(STEPS.length,reduced.matches,Object.keys(AUTO_HOLDS).map(Number));
let assembly,verified,renderer,scene,camera,orbit,groups={},labels={},rows={},ghosts=[],pathGroup,ready=false,selected=null,lastTime=0,lastPhase='',cameraGoal=null,lastStep=-1;
const idNames=Object.fromEntries([...NAMES.map((name,i)=>[String(i+1).padStart(2,'0'),name]),...STOCK.map(p=>[p.id,p.name])]);
const shellIds=new Set(['01','02','03']);
const edgesMaterial=new THREE.LineBasicMaterial({color:0x376173,transparent:true,opacity:.48});
const activeMaterial=new THREE.LineBasicMaterial({color:0xb77e13});
const laterMaterial=new THREE.LineDashedMaterial({color:0x8a9ea9,dashSize:.003,gapSize:.002,transparent:true,opacity:.6});
function state(id){return STEPS[player.index].ids.includes(id)?'current':assembly?.firstStep[id]<=player.index?'assembled':'later';}
function scopeText(s){
  if(player.index===0)return '初期配置は25個の一次外形の包囲箱が重ならないことを検査しています。参考配線は初期配置では非表示です。';
  return `表示経路は全${verified?.samples||'—'}点で離散検査。通常挿入1mm、底部0.1mm／1°、取り回し5mm／5°以下。公称メッシュ交差を検査（0.005mm³より大、交差最小幅0.00005mm以上）。組立済みの一次形状が対象。カセット内部対・後の部品・参考配線は除外。サンプル間と実物は未検証。${s.route.audit?'既存監査参照：'+s.route.audit+'。':''}詳細は「検証範囲」。`;
}
function renderInstructions(){
  const s=STEPS[player.index];$('step-number').textContent=String(player.index).padStart(2,'0');$('title').textContent=s.title;
  $('ids').textContent=s.ids.map(id=>`${id} ${idNames[id]}`).join(' / ');$('action').textContent=s.action;$('done').textContent=s.done;$('pending').textContent=s.pending;$('scope').textContent=scopeText(s);
  $('step-select').value=String(player.index);$('previous').disabled=player.index===0;$('next').disabled=player.index===STEPS.length-1;
  $('play').disabled=!ready;$('play').textContent=player.mode==='single'&&player.running?'この手順を一時停止':player.mode==='single'&&player.fraction<1?'この手順を再開':'この手順を再生';
  $('auto-play').disabled=!ready||player.phase==='gate'||(player.mode==='auto'&&player.phase==='complete');
  $('auto-play').textContent=player.mode==='auto'&&player.running?'自動進行を一時停止':player.mode==='auto'&&player.phase!=='complete'?'自動進行を再開':'全手順を自動再生';
  $('auto-hold').hidden=!(ready&&player.mode==='auto'&&player.phase==='gate');$('auto-hold-reason').textContent=AUTO_HOLDS[player.index]||'';
  const status=!ready?'3D停止中 · 読み込み・再試行後に再生できます':player.phase==='gate'?'確認待ち · 未解決の保留点で自動進行を停止':player.phase==='complete'?'全手順の表示が完了 · 停止しました（実物は未確認）':player.running?player.phase==='dwell'?`説明を見るため停止 · あと${Math.max(0,player.dwell-player.dwellElapsed).toFixed(1)}秒`:'再生中 · '+(player.mode==='auto'?'手順を自動で進めます':'この手順の終わりで停止'):player.mode==='auto'?'自動進行を一時停止 · 同じ位置から再開':player.fraction<1?'この手順を一時停止 · 同じ位置から再開':'停止中 · 初めから見るには「最初へ」→「全手順を自動再生」';
  $('play-status').textContent=status+(player.pauseReason?' · '+player.pauseReason:'')+(reduced.matches?' · 動きを減らす設定':'');
  for(const [id,row] of Object.entries(rows)){const st=state(id);row.className=`bom-row ${st}${selected===id?' selected':''}`;row.querySelector('.state').textContent=st==='current'?'◎ この手順':st==='assembled'?'✓ 組立済み':'○ これから';row.setAttribute('aria-pressed',String(selected===id));}
}
function makeBOM(){
  $('bom').replaceChildren();rows={};
  for(const [id,name] of Object.entries(idNames).sort((a,b)=>a[0].localeCompare(b[0]))){const button=document.createElement('button');button.className='bom-row';button.innerHTML='<b></b><span class="name"></span><span class="state"></span>';button.children[0].textContent=id;button.children[1].textContent=name;
    if(assembly){const small=document.createElement('small');small.textContent=assembly.byId[id].kind+' · '+assembly.byId[id].source;button.children[1].append(small);}
    button.onclick=()=>selectPart(id,true);$('bom').append(button);rows[id]=button;
  }
}
function selectPart(id,focus=false){selected=id;$('selection').textContent=`${id} · ${idNames[id]} · ${assembly?.byId[id]?.kind||''}`;renderInstructions();if(ready){paint();if(focus)focusPart(id);} }
function setStep(index){player.seek(index);lastPhase='';if(!selected)$('selection').textContent='部品を選ぶとIDと名前を表示';renderInstructions();if(ready){paint();makeGhosts();if($('auto-camera').checked)recommendCamera();} }
STEPS.forEach((s,i)=>{const o=document.createElement('option');o.value=String(i);o.textContent=`${String(i).padStart(2,'0')} · ${s.title}`;$('step-select').append(o);});
makeBOM();renderInstructions();
$('next').onclick=()=>setStep(player.index+1);$('previous').onclick=()=>setStep(player.index-1);$('reset').onclick=()=>{selected=null;setStep(0);if(ready)overview(true);};
$('step-select').onchange=e=>setStep(Number(e.target.value));
$('play').onclick=()=>{if(!ready)return;player.reduced=reduced.matches;if(player.running&&player.mode==='single')player.pause();else {player.pause();player.play();}renderInstructions();makeGhosts();if($('auto-camera').checked)recommendCamera();};
$('auto-play').onclick=()=>{if(!ready)return;player.reduced=reduced.matches;if(player.running&&player.mode==='auto')player.pause();else {player.pause();player.startAuto();}renderInstructions();};
$('continue-auto').onclick=()=>{if(!ready)return;player.continuePreview();renderInstructions();};
$('dwell').onchange=e=>{player.setDwell(Number(e.target.value));renderInstructions();};
$('speed').onchange=e=>player.setSpeed(Number(e.target.value));
$('shell').onchange=()=>{if(ready)paint();};$('wires').onchange=()=>{if(ready)paint();};
$('camera').onclick=()=>recommendCamera(true);$('overview').onclick=()=>overview(true);$('joint').onclick=()=>focusPart(selected||STEPS[player.index].ids[0]||'01',true);
document.addEventListener('keydown',e=>{if(e.target.matches('input,select,textarea,button,a,summary')||e.altKey||e.ctrlKey||e.metaKey)return;if(e.key==='ArrowRight'){e.preventDefault();setStep(player.index+1);}if(e.key==='ArrowLeft'){e.preventDefault();setStep(player.index-1);}if(e.key==='Home'){e.preventDefault();setStep(0);}if(e.key==='End'){e.preventDefault();setStep(STEPS.length-1);}if(e.code==='Space'){e.preventDefault();$('play').click();}});
reduced.addEventListener('change',e=>{player.reduced=e.matches;if(e.matches){player.pause();player.fraction=1;}renderInstructions();});
document.addEventListener('visibilitychange',()=>{lastTime=0;if(document.hidden&&player.running)player.pause('背景へ移動したため停止。戻っても自動再開しません。');renderInstructions();});
function setupScene(){
  scene=new THREE.Scene();scene.background=new THREE.Color(0xeaf1f6);
  camera=new THREE.PerspectiveCamera(38,1,.001,10);camera.up.set(0,0,1);
  renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
  $('viewport').prepend(renderer.domElement);
  renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();ready=false;player.pause();showError('WebGLの描画コンテキストが失われました。再試行してください。');});
  scene.add(new THREE.HemisphereLight(0xffffff,0x809bb0,2.2));const sun=new THREE.DirectionalLight(0xffffff,2.5);sun.position.set(.2,-.4,.8);scene.add(sun);
  const grid=new THREE.GridHelper(1.2,24,0xb0c3ce,0xcfdee7);grid.rotation.x=Math.PI/2;grid.position.set(-.1,.16,-.12);scene.add(grid);
  orbit=new OrbitControls(camera,renderer.domElement);orbit.enableDamping=true;orbit.dampingFactor=.12;orbit.minDistance=.025;orbit.maxDistance=2.7;
  orbit.addEventListener('start',()=>{cameraGoal=null;$('auto-camera').checked=false;});
  let down=null;renderer.domElement.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY];});
  renderer.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const r=renderer.domElement.getBoundingClientRect();const ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),camera);const hits=ray.intersectObjects(Object.values(groups),true).filter(h=>h.object.isMesh&&!h.object.userData.route&&h.object.visible&&h.object.parent.visible);if(hits[0])selectPart(hits[0].object.userData.id);down=null;});
  groups={};labels={};$('labels').replaceChildren();
  for(const item of assembly.items){
    const group=new THREE.Group();group.userData.id=item.id;
    for(const name of item.meshes){const part=assembly.cad.parts.find(p=>p.name===name),isRoute=routeMesh(name);const geometry=meshGeometry(part,item.center);const material=new THREE.MeshStandardMaterial({color:item.id==='S1'?0x3f6893:item.id==='S2'?0xe6e3d6:item.id==='S3'?0x627c82:0xd3e0e8,roughness:.7,metalness:.04,transparent:false,flatShading:true});const mesh=new THREE.Mesh(geometry,material);mesh.userData={id:item.id,route:isRoute};group.add(mesh);
      if(!isRoute){const edge=new THREE.LineSegments(new THREE.EdgesGeometry(geometry,27),edgesMaterial);edge.computeLineDistances();edge.userData={id:item.id,edge:true};group.add(edge);}
    }
    scene.add(group);groups[item.id]=group;
    const label=document.createElement('div');label.className='label';label.dataset.id=item.id;label.title=`${item.id} ${item.name}`;$('labels').append(label);labels[item.id]=label;
  }
  pathGroup=new THREE.Group();scene.add(pathGroup);
  new ResizeObserver(resize).observe($('viewport'));resize();overview(true);paint();makeGhosts();
}
function resize(){if(!renderer)return;const w=$('viewport').clientWidth,h=$('viewport').clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false);}
function paint(){
  const sample=assembly.sample(player.index,player.fraction);
  for(const item of assembly.items){const group=groups[item.id],p=sample.poses[item.id];group.position.fromArray(p.position);group.quaternion.fromArray(p.quaternion);const st=state(item.id),chosen=selected===item.id,hide=shellIds.has(item.id)&&$('shell').value==='hidden',alpha=shellIds.has(item.id)&&$('shell').value==='transparent'?.19:1;group.visible=!hide;
    for(const child of group.children){if(child.isMesh){child.visible=!child.userData.route||($('wires').checked&&player.fraction===1&&assembly.firstStep[item.id]<=player.index);child.material.opacity=alpha;child.material.transparent=alpha<1;child.material.depthWrite=alpha===1;child.material.emissive.setHex(chosen||st==='current'?0x422709:0);child.material.emissiveIntensity=chosen?.45:st==='current'?.25:0;}
      else if(child.userData.edge)child.material=chosen||st==='current'?activeMaterial:st==='later'?laterMaterial:edgesMaterial;
    }
  }
  if(sample.label!==lastPhase){$('phase').textContent=sample.label;lastPhase=sample.label;}
}
function makeGhosts(){if(!ready||!scene)return;for(const old of ghosts){scene.remove(old);old.traverse(o=>{if(o.userData.ghostGeometry){o.geometry.dispose();o.material.dispose();}});}ghosts=[];pathGroup.traverse(o=>{if(o.userData.ownedGeometry)o.geometry.dispose();if(o.material)o.material.dispose();});pathGroup.clear();
  const step=STEPS[player.index];const ids=step.ids.length>4?['04']:step.ids;
  for(const id of ids){const item=assembly.byId[id],end=assembly.snapshots[player.index][id],ghost=new THREE.Group();ghost.position.fromArray(end.position);ghost.quaternion.fromArray(end.quaternion);
    for(const child of groups[id].children){if(child.isMesh&&!child.userData.route){const g=new THREE.LineSegments(new THREE.EdgesGeometry(child.geometry,30),new THREE.LineBasicMaterial({color:0x2ba3b0,transparent:true,opacity:.65,depthTest:false}));g.userData.ghostGeometry=true;ghost.add(g);}}
    scene.add(ghost);ghosts.push(ghost);
    const points=assembly.transitions[player.index];if(!points)continue;
    for(let i=1;i<points.length;i++){const a=new THREE.Vector3(...points[i-1].poses[id].position),b=new THREE.Vector3(...points[i].poses[id].position);const delta=b.clone().sub(a),distance=delta.length();if(distance<1e-6)continue;const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([a,b]),new THREE.LineDashedMaterial({color:points[i].scope==='insertion'?0x248b9b:0xc79b50,dashSize:.003,gapSize:.003,transparent:true,opacity:.45}));line.userData.ownedGeometry=true;line.computeLineDistances();pathGroup.add(line);
      if(points[i].scope==='insertion')pathGroup.add(new THREE.ArrowHelper(delta.normalize(),a,distance,0x238d9b,Math.min(.006,distance*.3),Math.min(.003,distance*.2)));
    }
  }
}
function cameraTo(target,distance,instant=false,top=false){if(!ready&& !camera)return;const direction=top?new THREE.Vector3(0,-.04,1):new THREE.Vector3(1.05,1.4,1.2).normalize();const position=new THREE.Vector3(...target).addScaledVector(direction,distance);if(instant||reduced.matches){camera.position.copy(position);orbit.target.fromArray(target);cameraGoal=null;orbit.update();}else cameraGoal={position,target:new THREE.Vector3(...target)};}
function overview(instant=false){if(!assembly||!camera)return;const bbox=new THREE.Box3();for(const group of Object.values(groups))bbox.expandByObject(group);const center=bbox.getCenter(new THREE.Vector3()),size=bbox.getSize(new THREE.Vector3());const distance=Math.max(size.x/camera.aspect,size.y)*1.6+.18;cameraTo(center.toArray(),distance,instant,true);}
function recommendCamera(force=false){if(!ready)return;if(player.index===0){overview(force);return;}const unit=player.index>=5&&player.index<=23;const target=unit?[.215,.033,.042]:[.035,.03,.03];const bottom=[4,25,27,28].includes(player.index);if(bottom){const position=new THREE.Vector3(target[0]+.15,target[1]+.18,-.12);cameraGoal={position,target:new THREE.Vector3(...target)};if(force||reduced.matches){camera.position.copy(position);orbit.target.fromArray(target);cameraGoal=null;}}else cameraTo(target,.28,force);}
function focusPart(id,close=false){if(!ready||!groups[id])return;const p=assembly.snapshots[player.index][id].position;const size=assembly.byId[id].initialBounds;const max=Math.max(...size.max.map((n,i)=>n-size.min[i]));cameraTo(p,Math.max(close?.075:.13,max*2.3));}
function positionLabels(){if(!ready)return;const w=$('viewport').clientWidth,h=$('viewport').clientHeight,rects=[];const step=STEPS[player.index],current=step.ids.length>4?['02','04','05']:step.ids;
  const ids=player.index===0?assembly.items.map(p=>p.id):[...new Set([selected,...current].filter(Boolean))];
  for(const label of Object.values(labels))label.hidden=true;
  for(const id of ids){const group=groups[id];if(!group.visible)continue;const item=assembly.byId[id],p=group.position.clone().project(camera);if(p.z<-1||p.z>1||p.x<-1||p.x>1||p.y<-1||p.y>1)continue;const label=labels[id],st=state(id);label.hidden=false;label.className=`label ${st}${id===selected?' selected':''}`;label.textContent=player.index===0?(w<500?id:`${id} ${item.name}`):`${id} ${st==='current'?'◎':st==='assembled'?'✓':'○'} ${w<500?'':item.name}`;
    const lw=label.offsetWidth,lh=label.offsetHeight,x=Math.max(4,Math.min(w-lw-4,(p.x*.5+.5)*w-lw/2));let y=Math.max(4,Math.min(h-lh-4,(-p.y*.5+.5)*h+12));
    for(let tries=0;tries<35&&rects.some(r=>x<r.x+r.w+3&&x+lw+3>r.x&&y<r.y+r.h+3&&y+lh+3>r.y);tries++)y=Math.min(h-lh-4,y+lh+4);
    if(rects.some(r=>x<r.x+r.w+2&&x+lw+2>r.x&&y<r.y+r.h+2&&y+lh+2>r.y)){label.hidden=true;continue;}
    label.style.left=`${x}px`;label.style.top=`${y}px`;rects.push({x,y,w:lw,h:lh});
  }
}
function showError(message){$('loading').hidden=true;$('failure').hidden=false;$('failure-reason').textContent=message;renderInstructions();}
async function load(){
  $('failure').hidden=true;$('loading').hidden=false;ready=false;player.pause();renderInstructions();
  try{const [cad,manifest,audit]=await Promise.all(['assets/cad.json','assets/cad_parts.json','assets/path-audit-summary.json'].map(async path=>{const res=await fetch(path);if(!res.ok)throw Error(`${path}: HTTP ${res.status}`);return res.json();}));assembly=createAssembly(cad,manifest);if(audit.source_sha256!==cad.source_sha256)throw Error('経路検査の版がCADと一致しません。');verified=audit;makeBOM();
    if(renderer){renderer.dispose();renderer.domElement.remove();orbit.dispose();}
    setupScene();ready=true;paint();makeGhosts();overview(true);$('loading').hidden=true;renderInstructions();
  }catch(error){showError(error.message||String(error));}
}
$('retry').onclick=load;
function loop(time){requestAnimationFrame(loop);const dt=lastTime?Math.min(.1,(time-lastTime)/1000):0;lastTime=time;
  if(!ready)return;const previousIndex=player.index,previousPhase=player.phase,wasRunning=player.running;if(!document.hidden)player.tick(dt);if(player.index!==lastStep){lastStep=player.index;renderInstructions();makeGhosts();if($('auto-camera').checked)recommendCamera();}if(previousPhase!==player.phase||wasRunning&&!player.running||player.phase==='dwell')renderInstructions();paint();
  if(cameraGoal){const amount=1-Math.exp(-dt*4);camera.position.lerp(cameraGoal.position,amount);orbit.target.lerp(cameraGoal.target,amount);if(camera.position.distanceTo(cameraGoal.position)<.0005)cameraGoal=null;}
  orbit.update();renderer.render(scene,camera);positionLabels();
}
requestAnimationFrame(loop);load();
function shadingEvidence(){
  const meshes=Object.values(groups).flatMap(g=>g.children.filter(x=>x.isMesh));let unequalTriangles=0;
  for(const mesh of meshes){const normal=mesh.geometry.getAttribute('normal').array;for(let i=0;i<normal.length;i+=9)for(let k=0;k<3;k++)if(normal[i+k]!==normal[i+3+k]||normal[i+k]!==normal[i+6+k])unequalTriangles++;}
  return {meshes:meshes.length,allFlat:meshes.every(m=>m.material.flatShading),allNonIndexed:meshes.every(m=>m.geometry.index===null),unequalTriangles,transparentMeshes:meshes.filter(m=>m.material.opacity<1).length,ghostsWireframeOnly:ghosts.every(g=>g.children.every(x=>x.isLineSegments))};
}
// ローカル検査用の読取り専用スナップショット。UIの操作は実際のボタンで確認する。
window.__assemblyTest={get state(){return {ready,index:player.index,fraction:player.fraction,running:player.running,speed:player.speed,mode:player.mode,phase:player.phase,dwell:player.dwell,dwellElapsed:player.dwellElapsed,pauseReason:player.pauseReason,selected,groups:Object.keys(groups),poses:assembly?.sample(player.index,player.fraction).poses,renderedPoses:Object.fromEntries(Object.entries(groups).map(([id,g])=>[id,{position:g.position.toArray(),quaternion:g.quaternion.toArray()}]))};},get labelRects(){return Object.values(labels).filter(x=>!x.hidden).map(x=>({id:x.dataset.id,x:x.offsetLeft,y:x.offsetTop,w:x.offsetWidth,h:x.offsetHeight}));},get screenPoints(){const r=renderer.domElement.getBoundingClientRect();return Object.entries(groups).map(([id,g])=>{const p=g.position.clone().project(camera);return {id,x:r.x+(p.x*.5+.5)*r.width,y:r.y+(-p.y*.5+.5)*r.height};});}};
Object.defineProperty(window.__assemblyTest,'shading',{get:shadingEvidence});
