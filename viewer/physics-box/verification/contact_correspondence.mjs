import {fileURLToPath} from 'node:url';
process.chdir(fileURLToPath(new URL('.',import.meta.url)));
import fs from 'node:fs';
const data=JSON.parse(fs.readFileSync('../assets/contact_profiles.json')),cad=JSON.parse(fs.readFileSync('../assets/cad.json'));
const phase=35*Math.PI/180,c=Math.cos(phase),s=Math.sin(phase),local=poly=>poly.map(p=>{const y=p[0]-.040,z=p[1]-.037;return [y*c+z*s,-y*s+z*c];});
const inner=local(data.reports[0].loops[1]),horn=local(data.reports[1].loops[0]);
function hits(poly,r){const h=[];for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length];if((a[0]>r)!==(b[0]>r))h.push(a[1]+(b[1]-a[1])*(r-a[0])/(b[0]-a[0]));}return h.sort((a,b)=>a-b);}
const world=(r,t)=>[.04025,.040+r*c-t*s,.037+r*s+t*c];
function prism(role,name,poly,x0,x1){return {role,name,vertices:[...poly.map(([r,t])=>{const v=world(r,t);v[0]=x0;return v;}),...poly.map(([r,t])=>{const v=world(r,t);v[0]=x1;return v;})].flat()};}
const patches=[],sections=[];
for(const [lo,hi,label]of [[-.016,-.010,'negative long arm'],[.010,.014,'positive long arm']]){
 const hl=hits(horn,lo),hh=hits(horn,hi),cl=hits(inner,lo),ch=hits(inner,hi);
 sections.push({label,radiusMm:[lo*1000,hi*1000],hornHalfWidthMm:[Math.max(...hl.map(Math.abs))*1000,Math.max(...hh.map(Math.abs))*1000],cupHalfWidthMm:[Math.max(...cl.map(Math.abs))*1000,Math.max(...ch.map(Math.abs))*1000]});
 patches.push(prism('rotor','CAD horn strip '+label,[[lo,hl[0]],[hi,hh[0]],[hi,hh.at(-1)],[lo,hl.at(-1)]],.0395,.041));
 for(const sign of [-1,1]){const i=sign===-1?0:cl.length-1,sl=(ch[i]-cl[i])/(hi-lo),tl=cl[i]-sl*.002,th=ch[i]+sl*.002,rlo=lo-.002,rhi=hi+.002,thick=.001*sign;patches.push(prism('cup','CAD cup face '+label+' '+sign,[[rlo,tl],[rhi,th],[rhi,th+thick],[rlo,tl+thick]],.0372,.0412));}
}
const model={method:'representative point plus optional CAD face strips',units:'metre',sourceSha256:cad.source_sha256,radialDistance:.014,pointRadius:.0015,nominalTangentialGap:.0003,closedPhaseDeg:35,axialCapture:'ideal constraint',fullCadFitValidated:false,patches,sections,notes:['Optional strips follow actual arm / pocket faces at x=39.900037 mm, in straight portions only','Internal horn holes are filled in contact strips. Tip curves, short arms, hub, journal and axial capture are omitted','Cup strips extend 2 mm beyond horn strip ends to avoid artificial end-face contact']};
fs.writeFileSync('../assets/contact_model.json',JSON.stringify(model,null,2));console.log(sections);
