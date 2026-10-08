import {fileURLToPath} from 'node:url';
process.chdir(fileURLToPath(new URL('.',import.meta.url)));
import fs from 'node:fs';
const profile=JSON.parse(fs.readFileSync('../assets/contact_profiles.json'));
const cup=profile.reports[0].loops[1].map(([y,z])=>[(y-.040)*1000,(z-.037)*1000]);
const horn=profile.reports[1].loops[0].map(([y,z])=>[(y-.040)*1000,(z-.037)*1000]);
const inside=(p,poly)=>{let yes=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;};
function distance(p,poly){let best=Infinity;for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],dx=b[0]-a[0],dy=b[1]-a[1],t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)));best=Math.min(best,Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy));}return best;}
// Sample original outer-loop edges every <=0.1 mm. Section only; no 3D or continuous guarantee.
const samples=[];for(let i=0;i<horn.length;i++){const a=horn[i],b=horn[(i+1)%horn.length],n=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.1));for(let k=0;k<n;k++)samples.push(a.map((v,j)=>v+(b[j]-v)*k/n));}
function overlap(deg){const a=deg*Math.PI/180,c=Math.cos(a),s=Math.sin(a);let max=0,where=null;for(const p of samples){const q=[p[0]*c-p[1]*s,p[0]*s+p[1]*c];if(!inside(q,cup)){const d=distance(q,cup);if(d>max){max=d;where=q;}}}return {maxOutsideMm:max,whereYZmm:where};}
function first(sign){let lo=0,hi=3;for(let i=0;i<35;i++){const m=(lo+hi)/2;if(overlap(m*sign).maxOutsideMm>1e-5)hi=m;else lo=m;}return sign*hi;}
const records=[];for(const name of ['normal','cad_face_strips']){const data=JSON.parse(fs.readFileSync('test-results/'+name+'.json'));let max={maxOutsideMm:0};for(const r of data.log){const result=overlap(r.servoDeg-r.cupDeg);if(result.maxOutsideMm>max.maxOutsideMm)max={...result,t:r.t,lidDeg:r.lidDeg,relativeHornDeg:r.servoDeg-r.cupDeg};}records.push({name,samples:data.log.length,maxSectionOutside:max});}
const result={method:'Frozen CAD section x=39.900037mm, horn outer edge sampled at <=0.1mm; compare in cup coordinates using logged relative angle. Translation drift and out-of-plane rotation omitted.',firstContactRelativeDeg:{positive:first(1),negative:first(-1)},representative:{approximateFirstContactDeg:Math.asin(.3/14)*180/Math.PI,actionRadiusMm:14,ballRadiusMm:1.5},records,fullCadCollisionValidated:false,limitations:['Only one shaft-normal section; tip curves and long/short arms included at this section','Outside distance is geometric section overlap, not a Rapier contact manifold penetration','Positive residual means collision reduction misses earlier CAD contact; results are illustrative and need collider refinement or physical clearance measurements']};
fs.writeFileSync('../assets/contact_section_check.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
