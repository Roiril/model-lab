// Exercise the actual generated page's drawing and controls without a browser.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const html=fs.readFileSync(path.resolve(here,'../../prints/flag-box/preview.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
let fills=0, points=[];
const ctx={clearRect(){fills=0;points=[];},beginPath(){},moveTo(x,y){points.push([x,y]);},lineTo(x,y){points.push([x,y]);},closePath(){},fill(){fills++;},stroke(){}};
const elements=new Map();
function element(id=''){
  return {id,value:'0',checked:false,hidden:false,style:{},events:{},children:[],
    append(...children){this.children.push(...children);},replaceChildren(...children){this.children=children;},
    addEventListener(name,fn){this.events[name]=fn;},setAttribute(k,v){this[k]=v;},
    getBoundingClientRect(){return {width:375,height:320};},getContext(){return ctx;},setPointerCapture(){}};
}
const document={documentElement:element(),getElementById(id){if(!elements.has(id))elements.set(id,element(id));return elements.get(id);},createElement(){return element();}};
const sandbox={document,window:{devicePixelRatio:1,setInterval(){return 1;},clearInterval(){}},
  ResizeObserver:class {observe(){}},getComputedStyle(){return {getPropertyValue(){return '#191512';}};},console};
vm.createContext(sandbox);
new vm.Script(script,{filename:'generated-preview.js'}).runInContext(sandbox);
assert(fills>1000);
const initial=JSON.stringify(points);
elements.get('angle90').events.click();
assert.equal(elements.get('angleValue').value,'90°');
assert.notEqual(JSON.stringify(points),initial);
elements.get('hideExterior').checked=true;
elements.get('hideExterior').events.change();
const hiddenFills=fills;
elements.get('hideExterior').checked=false;
elements.get('hideExterior').events.change();
assert(fills>hiddenFills);
elements.get('assemblyTab').events.click();
assert.equal(elements.get('assemblyTab')['aria-selected'],'true');
let count=0;
for(let step=0;step<9;step++){
  elements.get('assemblyStep').value=String(step);
  elements.get('assemblyStep').events.change();
  for(const progress of ['0','100']){
    elements.get('assemblyProgress').value=progress;
    elements.get('assemblyProgress').events.input();
    assert(fills>0);
    assert(points.every(([x,y])=>Number.isFinite(x)&&Number.isFinite(y)&&x>=0&&x<=375&&y>=0&&y<=320));
    count++;
  }
}
assert.equal(elements.get('gateChecks').children.length,19);
const result={pass:true,method:'Node vm with DOM/canvas stubs; not a browser visual inspection',
  motion_output_changed:true,hide_exterior_reduced_faces:true,assembly_endpoints_within_canvas:count,
  final_triangles_drawn:fills,gate_rows:elements.get('gateChecks').children.length};
fs.writeFileSync(path.join(here,'build','preview_test.json'),JSON.stringify(result,null,1)+'\n','utf8');
console.log(result);
