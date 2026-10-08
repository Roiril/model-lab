import R from './vendor/rapier.mjs';
export const DEG=Math.PI/180;
// CAD and public data are SI. Rapier's convex-face tolerances require a millimetre solver scale for these tiny prisms.
// Length -> S; inertia and torque -> S^2; mass, time, angles and angular speed stay unchanged.
export const S=1000;
export const NUMERICAL_LIMITS=Object.freeze({maxPenetrationMm:.05,maxHingeDriftMm:.03});
export const DEFAULTS=Object.freeze({dt:1/960,iterations:12,contactFrequency:6000,contactMode:'cad_faces',torqueCap:.03,commandSpeed:12,friction:.25,bearingDamping:.00025,lidMassScale:1,frontLoadG:0,comShiftMm:0,hornBiasMm:0,contactSkinMm:.01,contactEnabled:true,gravity:9.80665,fixedBase:true,shaftBlock:false,powered:true,initialLid:0,openTarget:56.8,closedTarget:-12,rotorInertia:5e-7});
const V=a=>({x:a[0],y:a[1],z:a[2]}), A=v=>[v.x,v.y,v.z], add=(a,b)=>a.map((x,i)=>x+b[i]), sub=(a,b)=>a.map((x,i)=>x-b[i]);
const VS=a=>V(a.map(x=>x*S)),VI=a=>V(a.map(x=>x*S*S)),AS=v=>A(v).map(x=>x/S);
export function rotate(q,v){const u=[q.x,q.y,q.z],w=q.w;const c=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];const d=[u[1]*c[2]-u[2]*c[1],u[2]*c[0]-u[0]*c[2],u[0]*c[1]-u[1]*c[0]];return v.map((x,i)=>x+2*(w*c[i]+d[i]));}
const Q=a=>({x:Math.sin(a/2),y:0,z:0,w:Math.cos(a/2)}), ID=Q(0), conj=q=>({x:-q.x,y:-q.y,z:-q.z,w:q.w});
const mul=(a,b)=>({x:a.w*b.x+a.x*b.w+a.y*b.z-a.z*b.y,y:a.w*b.y-a.x*b.z+a.y*b.w+a.z*b.x,z:a.w*b.z+a.x*b.y-a.y*b.x+a.z*b.w,w:a.w*b.w-a.x*b.x-a.y*b.y-a.z*b.z});
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export function validateParameters(p){
 const limits={dt:[1/1920,1/240],iterations:[4,32],contactFrequency:[100,10000],torqueCap:[0,.24516625],commandSpeed:[1,120],friction:[0,1],bearingDamping:[0,.25],lidMassScale:[.1,10],frontLoadG:[0,1000],comShiftMm:[-10,10],hornBiasMm:[-.2,.2],contactSkinMm:[0,.1],gravity:[0,20],initialLid:[0,65],openTarget:[50,65],closedTarget:[-20,0],rotorInertia:[1e-7,2e-5]};
 for(const [k,[lo,hi]]of Object.entries(limits))if(!Number.isFinite(p[k])||p[k]<lo||p[k]>hi)throw Error(k+' must be '+lo+' to '+hi);
 if(!Number.isInteger(p.iterations))throw Error('iterations must be an integer');
 if(!['representative','cad_faces'].includes(p.contactMode))throw Error('Unknown contact mode');
 for(const k of ['contactEnabled','powered','fixedBase','shaftBlock'])if(typeof p[k]!=='boolean')throw Error(k+' must be boolean');
 return p;
}
function principal(matrix){
 const a=matrix.map(r=>[...r]),v=[[1,0,0],[0,1,0],[0,0,1]];
 for(let k=0;k<32;k++){let p=0,q=1;for(const ij of [[0,2],[1,2]])if(Math.abs(a[ij[0]][ij[1]])>Math.abs(a[p][q]))[p,q]=ij;if(Math.abs(a[p][q])<1e-16)break;const angle=.5*Math.atan2(2*a[p][q],a[q][q]-a[p][p]),c=Math.cos(angle),s=Math.sin(angle);const J=[[1,0,0],[0,1,0],[0,0,1]];J[p][p]=c;J[q][q]=c;J[p][q]=s;J[q][p]=-s;const mm=(x,y)=>x.map(r=>y[0].map((_,j)=>r.reduce((t,u,i)=>t+u*y[i][j],0)));const t=mm(a,J),u=mm(J[0].map((_,j)=>J.map(r=>r[j])),t);for(let i=0;i<3;i++)for(let j=0;j<3;j++)a[i][j]=u[i][j];const vv=mm(v,J);for(let i=0;i<3;i++)for(let j=0;j<3;j++)v[i][j]=vv[i][j];}
 // Matrix to unit quaternion; trace branches avoid instability near 180 degrees.
 const t=v[0][0]+v[1][1]+v[2][2];let x,y,z,w;
 if(t>0){const s=Math.sqrt(t+1)*2;w=s/4;x=(v[2][1]-v[1][2])/s;y=(v[0][2]-v[2][0])/s;z=(v[1][0]-v[0][1])/s;}
 else {let i=0;if(v[1][1]>v[i][i])i=1;if(v[2][2]>v[i][i])i=2;const j=(i+1)%3,k=(i+2)%3,s=Math.sqrt(1+v[i][i]-v[j][j]-v[k][k])*2,r=[0,0,0];r[i]=s/4;r[j]=(v[i][j]+v[j][i])/s;r[k]=(v[i][k]+v[k][i])/s;[x,y,z]=r;w=(v[k][j]-v[j][k])/s;}
 return {principal:[a[0][0],a[1][1],a[2][2]],frame:{x,y,z,w}};
}
export async function initPhysics(){await R.init({});}
export class BoxPhysics {
 constructor(cad,shapes,parameters={}){this.cad=cad;this.shapes=shapes;this.parameters={...DEFAULTS,...parameters};this.reset();}
 dispose(){this.world?.free();this.eventQueue?.free();this.world=null;this.eventQueue=null;}
 reset(parameters={}){
  const p=validateParameters({...this.parameters,...parameters});this.dispose();this.parameters=p;
  this.world=new R.World({x:0,y:0,z:-p.gravity*S});this.eventQueue=new R.EventQueue(true);const ip=this.world.integrationParameters;
  ip.dt=p.dt;ip.lengthUnit=.07*S;ip.normalizedAllowedLinearError=.00001;ip.normalizedPredictionDistance=.001;ip.numSolverIterations=p.iterations;ip.numInternalPgsIterations=2;ip.maxCcdSubsteps=4;ip.contact_natural_frequency=p.contactFrequency;
  this.bodies={};this.colliderMeta=new Map();this.joints=[];this.log=[];this.time=0;this.lastInspection=-1;this.lastLog=undefined;this.target=-10;this.destination=-10;this.integral=0;this.command='ready';this.paused=false;this.repeat=false;this.cycle=0;this.dwell=0;this.stable=0;this.peak={penetrationMm:0,hingeDriftMm:0,torqueNm:0};this.contactMarkers=[];this.missingRetention=false;
  const phi=p.initialLid*DEG,O=this.cad.pivots.O,H=this.cad.pivots.H,B=add(H,rotate(Q(phi),sub(this.cad.pivots.B,H)));
  const by=B[1]-O[1],bz=B[2]-O[2],d=Math.hypot(by,bz),L=.02925869387023603,r=.014;
  const theta=Math.atan2(bz,by)-Math.acos(clamp((d*d+r*r-L*L)/(2*d*r),-1,1));
  const cp=theta+10*DEG,Anew=add(O,[0,r*Math.cos(theta),r*Math.sin(theta)]);
  const linkAngle=Math.atan2(B[2]-Anew[2],B[1]-Anew[1])-Math.atan2(this.cad.pivots.B[2]-this.cad.pivots.A[2],this.cad.pivots.B[1]-this.cad.pivots.A[1]);
  const poses={lid:[Q(phi),H,H],cup:[Q(cp),O,O],rotor:[Q(cp),O,O],link:[Q(linkAngle),this.cad.pivots.A,Anew]};
  for(const [name,m] of Object.entries(this.cad.bodies)){
   const pose=poses[name]??[ID,[0,0,0],[0,0,0]],position=add(pose[2],rotate(pose[0],sub(m.com,pose[1])));
   let mass=m.mass,center=[0,0,0],inertia=m.inertia.map(r=>[...r]),props={principal:m.principal,frame:m.frame};
   if(name==='lid'){
    mass*=p.lidMassScale;inertia=inertia.map(r=>r.map(x=>x*p.lidMassScale));const front=p.frontLoadG/1000,offset=sub([m.com[0],.064,.069],m.com);center=[0,p.comShiftMm/1000,0];
    if(front>0){const firstMass=mass;center=add(center,offset.map(x=>x*front/(mass+front)));mass+=front;const a=center.map((x,i)=>x-(i===1?p.comShiftMm/1000:0)),b=sub(offset,center);for(let i=0;i<3;i++)for(let j=0;j<3;j++)inertia[i][j]+=firstMass*((i===j?a.reduce((s,x)=>s+x*x,0):0)-a[i]*a[j])+front*((i===j?b.reduce((s,x)=>s+x*x,0):0)-b[i]*b[j]);}
    props=principal(inertia);
   }
   if(name==='rotor'){inertia=inertia.map((r,i)=>r.map((x,j)=>x+(i===j?p.rotorInertia-5e-7:0)));props=principal(inertia);}
   const desc=((name==='base'||name==='frame')&&p.fixedBase?R.RigidBodyDesc.fixed():R.RigidBodyDesc.dynamic()).setTranslation(...position.map(x=>x*S)).setRotation(pose[0]);
   desc.setAdditionalMassProperties(mass,VS(center),VI(props.principal),props.frame).setCanSleep(false).setCcdEnabled(false);
   this.bodies[name]=this.world.createRigidBody(desc);
  }
  // The cassette attachment is an ideal fixture. It does not validate the strength of parts 13/20/21/22.
  const b=this.bodies;if(!p.fixedBase){this.fixture=this.world.createImpulseJoint(R.JointData.fixed(VS(sub(this.cad.bodies.frame.com,this.cad.bodies.base.com)),ID,VS([0,0,0]),ID),b.base,b.frame,true);this.fixture.setContactsEnabled(false);}
  const joint=(a,c,key)=>{const point=this.cad.pivots[key],data=R.JointData.revolute(VS(sub(point,this.cad.bodies[a].com)),VS(sub(point,this.cad.bodies[c].com)),{x:1,y:0,z:0});const j=this.world.createImpulseJoint(data,b[a],b[c],true);j.setContactsEnabled(true);this.joints.push({joint:j,a,c,point,key});return j;};
  this.servoJoint=joint('frame','rotor','O');joint('frame','cup','O');this.hingeJoint=joint('frame','lid','H');joint('cup','link','A');joint('link','lid','B');
  // Passive implicit joint damping is dissipative, including at large resistance values.
  // ForceBased damping is N m s/rad (converted to the scaled solver's torque units).
  for(const j of this.joints){if(j.c==='rotor')continue;j.joint.configureMotorModel(R.MotorModel.ForceBased);j.joint.configureMotorVelocity(0,p.bearingDamping*S*S);}
  // Explicit ideal closed stop, not an artificial open-angle constraint.
  this.hingeJoint.setLimits(0,75*DEG);this.servoJoint.setLimits(-15*DEG,85*DEG);
  // Single-axis contact reduction: a representative stock-horn action point and two cup faces.
  // These primitive contacts avoid numerical EPA failures at the seams of decomposed thin CAD meshes.
  // Their 0.30 mm tangential clearance is an estimate. No fixed joint connects rotor to cup.
  const phase=35*DEG,radial=[0,Math.cos(phase),Math.sin(phase)],tangent=[0,-Math.sin(phase),Math.cos(phase)],action=[.04025,O[1]+.014*radial[1],O[2]+.014*radial[2]],pointRadius=.0015;
  if(p.contactMode==='cad_faces'){
   if(!this.shapes.patches)throw Error('CAD contact patches missing');
   for(const patch of this.shapes.patches){const center=[0,0,0];for(let i=0;i<patch.vertices.length;i++)center[i%3]+=patch.vertices[i]/(patch.vertices.length/3);const v=patch.vertices.map((x,i)=>(x-center[i%3])*S),shape=R.ColliderDesc.convexHull(new Float32Array(v));if(!shape)throw Error('Invalid convex face '+patch.name);shape.setTranslation(...sub(center,this.cad.bodies[patch.role].com).map(x=>x*S)).setDensity(0).setFriction(p.friction).setContactSkin(p.contactSkinMm/1000*S).setActiveHooks(R.ActiveHooks.FILTER_CONTACT_PAIRS);const collider=this.world.createCollider(shape,b[patch.role]);this.colliderMeta.set(collider.handle,{name:patch.name,group:patch.role});}
  }else{
  const pointDesc=R.ColliderDesc.ball((pointRadius+p.hornBiasMm/1000)*S).setTranslation(...sub(action,this.cad.bodies.rotor.com).map(x=>x*S)).setDensity(0).setFriction(p.friction).setContactSkin(p.contactSkinMm/1000*S).setActiveHooks(R.ActiveHooks.FILTER_CONTACT_PAIRS);
  const pointCollider=this.world.createCollider(pointDesc,b.rotor);this.colliderMeta.set(pointCollider.handle,{name:'horn action point (r = 14 mm)',group:'rotor'});
  for(const sign of [-1,1]){const center=add(action,tangent.map(x=>x*sign*(pointRadius+.0003+.0005))),desc=R.ColliderDesc.cuboid(.002*S,.003*S,.0005*S).setTranslation(...sub(center,this.cad.bodies.cup.com).map(x=>x*S)).setRotation(Q(phase)).setDensity(0).setFriction(p.friction).setContactSkin(p.contactSkinMm/1000*S).setActiveHooks(R.ActiveHooks.FILTER_CONTACT_PAIRS);const c=this.world.createCollider(desc,b.cup);this.colliderMeta.set(c.handle,{name:'cup contact face '+sign,group:'cup'});}
  }
  const box=(name,group,min,max)=>{const center=min.map((x,i)=>(x+max[i])/2),half=min.map((x,i)=>(max[i]-x)/2),com=this.cad.bodies[group].com,desc=R.ColliderDesc.cuboid(...half.map(x=>x*S)).setTranslation(...sub(center,com).map(x=>x*S)).setDensity(0).setFriction(p.friction).setContactSkin(p.contactSkinMm/1000*S).setActiveHooks(R.ActiveHooks.FILTER_CONTACT_PAIRS);const c=this.world.createCollider(desc,b[group]);this.colliderMeta.set(c.handle,{name,group});};
  box('box-floor','base',[0,0,0],[.070,.070,.0024]);
  box('box-left','base',[0,0,.0024],[.0024,.070,.0672]);box('box-right','base',[.0676,0,.0024],[.070,.070,.0672]);
  box('box-back','base',[.0024,0,.0024],[.0676,.0024,.0672]);box('box-front','base',[.0024,.0676,.0024],[.0676,.070,.0672]);
  box('lid-skin','lid',[0,.0276,.0676],[.070,.070,.070]);
  const table=this.world.createCollider(R.ColliderDesc.cuboid(.20*S,.20*S,.003*S).setTranslation(.035*S,.035*S,-.00302*S).setFriction(.5).setDensity(0));this.colliderMeta.set(table.handle,{name:'table',group:'table'});
  if(p.shaftBlock){const d=R.ColliderDesc.cuboid(.002*S,.002*S,.002*S).setTranslation(.04025*S,(O[1]+.014*Math.cos(65*DEG))*S,(O[2]+.014*Math.sin(65*DEG))*S).setFriction(.25).setActiveHooks(R.ActiveHooks.FILTER_CONTACT_PAIRS);const c=this.world.createCollider(d);this.colliderMeta.set(c.handle,{name:'shaft-block',group:'block'});}
  this.hooks={filterContactPair:(c1,c2)=>{
   const a=this.colliderMeta.get(c1),c=this.colliderMeta.get(c2);if(!a||!c)return R.SolverFlags.COMPUTE_IMPULSE;
   const pair=[a.group,c.group].sort().join('/');
   if(pair==='base/frame')return null;
   if(pair==='cup/rotor'&&!this.parameters.contactEnabled)return null;
   // Ideal journal and joint seats exclude their mating surfaces. External lid/body and horn/cup contacts remain physical.
   if(pair==='frame/rotor'||pair==='cup/frame'||pair==='frame/lid'||pair==='frame/link'||pair==='cup/link'||pair==='lid/link')return null;
   return R.SolverFlags.COMPUTE_IMPULSE;
  }};
  for(const body of Object.values(b))body.recomputeMassPropertiesFromColliders();
  this.target=this.servoAngle();this.destination=this.target;this.record(true);
 }
 relativeAngle(name){const q=mul(conj(this.bodies.frame.rotation()),this.bodies[name].rotation());let a=2*Math.atan2(q.x,q.w);while(a>Math.PI)a-=2*Math.PI;while(a<-Math.PI)a+=2*Math.PI;return a/DEG;}
 servoAngle(){return this.relativeAngle('rotor')-10;}
 lidAngle(){return this.relativeAngle('lid');}
 cupAngle(){return this.relativeAngle('cup')-10;}
 commandTo(command){if(command==='stop'){this.destination=this.servoAngle();this.target=this.destination;this.integral=0;this.repeat=false;this.command='hold';this.stable=0;return;}this.paused=false;this.repeat=command==='repeat';this.destination=command==='close'?this.parameters.closedTarget:this.parameters.openTarget;this.command=command==='close'?'closing':'opening';this.startTime=this.time;this.stable=0;this.dwell=0;}
 powerOff(){this.parameters.powered=false;this.repeat=false;this.command='unpowered';this.integral=0;}
 step(){
  const p=this.parameters,b=this.bodies,dt=p.dt;for(const body of Object.values(b)){body.resetForces(false);body.resetTorques(false);}
  const axis=rotate(b.frame.rotation(),[1,0,0]),frameW=A(b.frame.angvel()),omega=A(b.rotor.angvel()).reduce((s,x,i)=>s+(x-frameW[i])*axis[i],0),angle=this.servoAngle();
  const move=p.commandSpeed*dt;this.target+=clamp(this.destination-this.target,-move,move);
  const error=(this.target-angle)*DEG;
  if(p.powered){this.integral=clamp(this.integral+error*dt,-.10,.10);}else this.integral=0;
  const requested=.30*error+.12*this.integral-.00030*omega;
  // Linear torque-speed approximation; only the two manufacturer endpoints are published.
  const available=Math.min(.24516625,p.torqueCap)*Math.max(0,1-Math.abs(omega)/10.471975512);
  let torque=p.powered?clamp(requested,-available,available):0;
  this.lastTorque=torque;this.availableTorque=available;this.requestedTorque=requested;this.peak.torqueNm=Math.max(this.peak.torqueNm,Math.abs(torque));
  const apply=(body,value)=>body.addTorque(V(axis.map(x=>x*value*S*S)),true);
  apply(b.rotor,torque);apply(b.frame,-torque);
  this.world.step(this.eventQueue,this.hooks);this.time+=dt;if(this.time-(this.lastInspection??-1)>=1/120){this.inspectContacts();this.lastInspection=this.time;}
  const lid=this.lidAngle();
  const reached=this.command==='opening'?Math.abs(lid-65)<.5:this.command==='closing'?Math.abs(lid)<.5:false;
  this.stable=reached?this.stable+dt:0;
  const recent=this.log.slice(-30).filter(r=>r.t>=this.time-.4),angleSpan=recent.length?Math.max(...recent.map(r=>r.lidDeg))-Math.min(...recent.map(r=>r.lidDeg)):Infinity;
  const accuracy=this.numericalAccuracy();
  if(this.stable>=.4&&angleSpan<.15){if(!accuracy.pass){this.command='precision_failed';this.repeat=false;}else if(this.repeat){if(this.dwell===0&&this.command==='closing'){this.target=this.servoAngle();this.destination=this.target;this.integral=0;}this.dwell+=dt;if(this.dwell>=.5){this.destination=this.command==='opening'?p.closedTarget:p.openTarget;this.command=this.command==='opening'?'closing':'opening';this.cycle++;this.startTime=this.time;this.stable=0;this.dwell=0;}}else {if(this.command==='closing'){this.target=this.servoAngle();this.destination=this.target;this.integral=0;}this.command=this.command==='opening'?'opened':'closed';}}
  if(['opened','closed'].includes(this.command)&&!accuracy.pass){this.command='precision_failed';this.repeat=false;}
  if(['opening','closing'].includes(this.command)&&this.time-(this.startTime??0)>14){this.command='incomplete';this.repeat=false;}
  this.record();return this.log.at(-1);
 }
 inspectContacts(){
  this.contactMarkers=[];let penetration=0;const colliders=[...this.colliderMeta.keys()];
  for(const h of colliders){const c=this.world.getCollider(h);this.world.contactPairsWith(c,other=>{if(other.handle<=h)return;this.world.contactPair(c,other,(m,flipped)=>{
   for(let i=0;i<m.numSolverContacts();i++){const distance=m.solverContactDist(i)/S*1000,point=m.solverContactPoint(i);penetration=Math.max(penetration,-distance);this.contactMarkers.push({point:AS(point),normal:A(m.normal()),distanceMm:distance,a:this.colliderMeta.get(h)?.name,b:this.colliderMeta.get(other.handle)?.name});}
  });});}
  let drift=0;for(const j of this.joints){const pa=add(AS(this.bodies[j.a].translation()),rotate(this.bodies[j.a].rotation(),sub(j.point,this.cad.bodies[j.a].com))),pb=add(AS(this.bodies[j.c].translation()),rotate(this.bodies[j.c].rotation(),sub(j.point,this.cad.bodies[j.c].com)));drift=Math.max(drift,Math.hypot(...sub(pa,pb))*1000);}
  this.penetrationMm=penetration;this.hingeDriftMm=drift;this.peak.penetrationMm=Math.max(this.peak.penetrationMm,penetration);this.peak.hingeDriftMm=Math.max(this.peak.hingeDriftMm,drift);this.peak.torqueNm=Math.max(this.peak.torqueNm,Math.abs(this.lastTorque??0));
 }
 numericalAccuracy(){const {penetrationMm,hingeDriftMm}=this.peak;return {pass:Number.isFinite(penetrationMm)&&Number.isFinite(hingeDriftMm)&&penetrationMm<=NUMERICAL_LIMITS.maxPenetrationMm&&hingeDriftMm<=NUMERICAL_LIMITS.maxHingeDriftMm,penetrationFailed:!Number.isFinite(penetrationMm)||penetrationMm>NUMERICAL_LIMITS.maxPenetrationMm,hingeDriftFailed:!Number.isFinite(hingeDriftMm)||hingeDriftMm>NUMERICAL_LIMITS.maxHingeDriftMm,limits:NUMERICAL_LIMITS};}
 record(force=false){if(!force&&this.time-(this.lastLog??-1)<1/60)return;this.lastLog=this.time;this.log.push({t:this.time,targetDeg:this.target,servoDeg:this.servoAngle(),cupDeg:this.cupAngle(),lidDeg:this.lidAngle(),torqueNm:this.lastTorque??0,availableNm:this.availableTorque??0,penetrationMm:this.penetrationMm??0,hingeDriftMm:this.hingeDriftMm??0,contacts:this.contactMarkers.length,command:this.command,numericalPass:this.numericalAccuracy().pass,poses:Object.fromEntries(Object.entries(this.bodies).map(([name,b])=>[name,{translationM:AS(b.translation()),rotation:b.rotation()}]))});if(this.log.length>18000)this.log.shift();}
 export(){return {schema:'model-lab B3 physics v1',numericalAccuracy:this.numericalAccuracy(),simulationTime:this.time,currentState:{targetDeg:this.target,servoDeg:this.servoAngle(),lidDeg:this.lidAngle(),command:this.command},sourceSha256:this.cad.source_sha256,engine:'Rapier 0.17.3',units:{cad:'m kg s kg*m^2',solverLengthScale:S,solverTorqueScale:S*S,log:'s degree N*m mm'},diagnosticSamplingHz:120,collisionApproximation:{mode:this.parameters.contactMode,details:this.parameters.contactMode==='cad_faces'?'Six convex prisms selected from straight CAD horn and cup faces; tips, hub, short arms and capture omitted':'One r1.5 mm ball at radius14 mm and two cup faces; nominal tangential gap0.30 mm',contactSkinMm:this.parameters.contactSkinMm,box:'five cuboid walls; lid skin cuboid; fixtures idealized'},parameters:this.parameters,massesKg:Object.fromEntries(Object.entries(this.bodies).map(([k,b])=>[k,b.mass()])),peaks:this.peak,assumptions:['Uniform solid PLA mass; rotor inertia, friction and motor controller are estimates','Motor drives stock horn only. Cup is driven through collision contact','Contact model is a partial approximation. Full CAD interference and actual fit are not validated','CAD face mode ignores hornBiasMm. Its six patches cover selected straight portions only','Bearing resistance is passive viscous damping. Static bearing stiction is omitted','Box shell and lid skin use cuboids. Ideal bearings, closed stop and fixtures exclude frame/moving-body contact','Retention strength, flex, creep, heat and fracture are not simulated'],log:this.log};}
}
