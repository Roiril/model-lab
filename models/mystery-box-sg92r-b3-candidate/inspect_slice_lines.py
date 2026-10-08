"""Actual offline toolpaths at selected roots, and slice/source geometry consistency."""
from pathlib import Path
import zipfile,json,re,math,xml.etree.ElementTree as ET,hashlib
import numpy as np
R=Path(__file__).resolve().parent;NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};PN='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
def matrix(t):
 a=np.array([float(v) for v in (t or '1 0 0 0 1 0 0 0 1 0 0 0').split()]);return a[:9].reshape(3,3),a[9:]
def sliced(path):
 z=zipfile.ZipFile(path);cfg=json.loads(z.read('Metadata/project_settings.config'));off=np.array([*map(float,cfg.get('extruder_offset',['0x0'])[0].split('x')),0.])
 root=ET.fromstring(z.read('3D/3dmodel.model'));objs={o.get('id'):o for o in root.findall('m:resources/m:object',NS)};c=ET.fromstring(z.read('Metadata/model_settings.config'))
 names={o.get('id'):next((x.get('value') for x in o.findall('metadata') if x.get('key')=='name'),'?') for o in c.findall('object')};boxes=[];geometry=[]
 for it in root.findall('m:build/m:item',NS):
  oid=it.get('objectid');comp=objs[oid].find('m:components/m:component',NS)
  if comp is None:continue
  child=ET.fromstring(z.read(comp.get(PN+'path').lstrip('/')));ob=next(o for o in child.findall('m:resources/m:object',NS) if o.get('id')==comp.get('objectid'))
  vs=np.array([[float(v.get(k)) for k in ['x','y','z']] for v in ob.findall('m:mesh/m:vertices/m:vertex',NS)]);fs=np.array([[int(v.get(k)) for k in ['v1','v2','v3']] for v in ob.findall('m:mesh/m:triangles/m:triangle',NS)])
  mc,tc=matrix(comp.get('transform'));mb,tb=matrix(it.get('transform'));local=vs@mc+tc;lo=local.min(0);world=local@mb+tb
  name=names[oid];folder='coupons' if name.startswith('test_') else 'stl';src=R/folder/(name+'.stl')
  dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);tri=np.frombuffer(src.read_bytes(),dtype=dt,offset=84)['v'].astype(float)
  target=local[fs]-lo
  face_error=None
  if len(tri)==len(target):
   candidates=[np.max(abs(tri-np.roll(t,k,axis=1)),axis=(1,2)) for t in [target,target[:,::-1]] for k in range(3)]
   face_error=float(np.min(np.stack(candidates),axis=0).max())
  aa=np.round(tri.mean(1),4);bb=np.round(target.mean(1),4);aa=aa[np.lexsort(aa.T[::-1])];bb=bb[np.lexsort(bb.T[::-1])]
  # Independent check of triangle count/centroid and exact local bounds; slicer must preserve meshes.
  sorted_match=len(aa)==len(bb) and np.allclose(aa,bb,atol=.00021,rtol=0)
  same=face_error is not None and face_error<.00021
  geometry.append({'part':name,'triangles_source':len(aa),'triangles_slice':len(bb),'canonical_centroids_match':bool(sorted_match),'ordered_triangle_vertices_max_error_mm':face_error,'all_triangle_vertices_match':same,'source_stl_sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
  boxes.append({'name':name,'inv':np.linalg.inv(mb),'translation':tb,'lo':lo,'min':world.min(0),'max':world.max(0)})
 return z,z.read('Metadata/plate_1.gcode').decode('utf8'),boxes,off,geometry
specs=[('20_short_body_bolt',.8,[5.5,-.4,9,3.1],'y',2.0,[6.3,8.3],'20 の位置決め足／根元'),('22_symmetric_cap_stop',.8,[-.2,.5,4.1,4.2],'x',2.0,[1,3.6],'22 の位置決め足／根元'),('01_body',8.0,[40,8.5,50,12],'x',45,[9.5,10.7],'T 案内の 1.2 mm 根元'),('01_body',4.2,[53,7,63,18],'x',59.8,[11.2,13.8],'22 の下向き保持段差')]
traces=[[] for _ in specs];widths=[set() for _ in specs];counts=[[] for _ in specs];meshchecks=[];bridges={}
for path in sorted((R/'slice_checks').glob('*/*.3mf')):
 z,g,boxes,off,geo=sliced(path);meshchecks.append({'plate':path.stem,'objects':geo,'crc_ok':z.testzip() is None})
 selected={b['name']:b for b in boxes if b['name'] in {s[0] for s in specs}}
 if not selected:z.close();continue
 pos=np.zeros(4);absolute=True;relative_e=True;feature='';width=.42;bridge_max=0;support_segments=0
 for line in g.splitlines():
  if line.startswith('; FEATURE: '):feature=line[11:].strip();continue
  if line.startswith('; LINE_WIDTH:'):width=float(line.split(':')[1]);continue
  raw=line.split(';')[0].strip()
  if raw=='G90':absolute=True;continue
  if raw=='G91':absolute=False;continue
  if raw=='M82':relative_e=False;continue
  if raw=='M83':relative_e=True;continue
  if raw.startswith('G92 '):
   for k,v in re.findall(r'([XYZE])([-+0-9.]+)',raw):pos['XYZE'.index(k)]=float(v)
   continue
  if not re.match(r'^G[0123]\s',raw):continue
  old=pos.copy();val={k:float(v) for k,v in re.findall(r'([XYZE])([-+0-9.]+)',raw)}
  for k,v in val.items():pos['XYZE'.index(k)]=v if absolute or k=='E' else pos['XYZE'.index(k)]+v
  extrusion=val.get('E',0) if relative_e else pos[3]-old[3]
  if extrusion<=0:continue
  if feature.startswith('Support'):support_segments+=1
  points=[old[:3],pos[:3]]
  if raw.startswith(('G2 ','G3 ')):
   ij={k:float(v) for k,v in re.findall(r'([IJ])([-+0-9.]+)',raw)};cen=old[:2]+[ij.get('I',0),ij.get('J',0)];rad=np.linalg.norm(old[:2]-cen);a0=math.atan2(old[1]-cen[1],old[0]-cen[0]);a1=math.atan2(pos[1]-cen[1],pos[0]-cen[0]);sweep=(a1-a0)%(2*math.pi)
   if raw.startswith('G2 '):sweep=-((a0-a1)%(2*math.pi))
   points=[np.array([cen[0]+rad*math.cos(a0+sweep*t),cen[1]+rad*math.sin(a0+sweep*t),pos[2]]) for t in np.linspace(0,1,max(2,math.ceil(abs(sweep)*rad/.1)+1))]
  if feature=='Bridge':bridge_max=max(bridge_max,sum(np.linalg.norm(b[:2]-a[:2]) for a,b in zip(points,points[1:])))
  for b in selected.values():
   for i,(name,layer,roi,axis,cut,interval,label) in enumerate(specs):
    if b['name']!=name:continue
    pp=[(q+off-b['translation'])@b['inv']-b['lo'] for q in points]
    if abs(pp[-1][2]-layer)>.001:continue
    for a,c in zip(pp,pp[1:]):
     if max(a[0],c[0])<roi[0] or min(a[0],c[0])>roi[2] or max(a[1],c[1])<roi[1] or min(a[1],c[1])>roi[3]:continue
     traces[i].append([a[:2].tolist(),c[:2].tolist(),feature,width]);widths[i].add(width)
     k=0 if axis=='x' else 1;l=1-k;delta=c[k]-a[k]
     if abs(delta)>1e-8 and min(a[k],c[k])<=cut<=max(a[k],c[k]):
      t=(cut-a[k])/delta;v=a[l]+t*(c[l]-a[l])
      if interval[0]-.01<=v<=interval[1]+.01:counts[i].append((float(v),width))
 bridges[path.stem]={'max_single_bridge_extrusion_run_mm':bridge_max,'support_extrusion_segments':support_segments};z.close()
records=[]
for i,s in enumerate(specs):
 lanes={round(v,3):w for v,w in counts[i]};records.append({'part':s[0],'layer_Z_mm':s[1],'ROI_mm':s[2],'section_axis_position':[s[3],s[4]],'section_span_mm':s[5],'extrusion_centerline_crossings':len(lanes),'crossing_positions_width_mm':list(lanes.items()),'line_widths_mm':sorted(widths[i]),'trace_segments':len(traces[i]),'label':s[6]})
report={'physical_tested':False,'mesh_consistency':meshchecks,'root_layers':records,'bridge_and_support':bridges,'limits':'Actual offline centreline traces and nominal widths, not deposited-polymer effective strength. At0.2mm layers20/22 feet1.6mm=8 layers and21 base1.8mm=9layers. Root cross-sections20>=3.2mm2 and22>=4.16mm2 are CAD values; cracks/layer bonding/bridge sag untested.'}
(R/'slice_line_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
# Self-contained SVG of the actual selected toolpaths; coordinates are millimetres.
out=['<svg xmlns="http://www.w3.org/2000/svg" width="240mm" height="160mm" viewBox="0 0 240 160"><rect width="240" height="160" fill="#fbfbf8"/><style>text{font-family:Segoe UI,Meiryo,sans-serif;fill:#20313d} .title{font-size:5px;font-weight:700} .label{font-size:3.2px}</style><text x="10" y="12" class="title">B3 · 実際のスライス線を根元で確認</text><text x="10" y="19" class="label">0.4 mmノズル・0.2 mm層の診断。線は押出し中心線／実物の接着・強度は未検証。</text>']
for i,s in enumerate(specs):
 x=10+(i%2)*115;y=28+(i//2)*60;roi=s[2];scale=min(85/(roi[2]-roi[0]),32/(roi[3]-roi[1]));out.append(f'<rect x="{x}" y="{y}" width="105" height="54" rx="2" fill="#ffffff" stroke="#d3dbe0"/><text x="{x+4}" y="{y+7}" class="label">{s[6]}</text>')
 def clip(a,b):
  dx=b[0]-a[0];dy=b[1]-a[1];lo=0.;hi=1.
  for p,q in [(-dx,a[0]-roi[0]),(dx,roi[2]-a[0]),(-dy,a[1]-roi[1]),(dy,roi[3]-a[1])]:
   if abs(p)<1e-12:
    if q<0:return None
   elif p<0:lo=max(lo,q/p)
   else:hi=min(hi,q/p)
  if lo>hi:return None
  return [(a[0]+t*dx,a[1]+t*dy) for t in [lo,hi]]
 for a,b,f,w in traces[i]:
  points=clip(a,b)
  if points is None:continue
  vals=[(x+9+(v[0]-roi[0])*scale,y+42-(v[1]-roi[1])*scale) for v in points];col='#1d667b' if 'wall' in f.lower() else '#bf7139'
  out.append(f'<path d="M{vals[0][0]:.3f},{vals[0][1]:.3f} L{vals[1][0]:.3f},{vals[1][1]:.3f}" stroke="{col}" stroke-width=".22" fill="none"/>')
 out.append(f'<text x="{x+4}" y="{y+49}" class="label">Z {s[1]:.1f} mm · 断面を横切る線 {records[i]["extrusion_centerline_crossings"]} 本</text>')
out.append('<text x="10" y="154" class="label">穴・摺動面には支持を追加せず、詰まりや割れがあれば組み込まない。支持・橋渡しは試験片で確認。</text></svg>')
(R/'slice_root_lines.svg').write_text(''.join(out),encoding='utf8');print('SLICE_ROOT_REVIEW',[(r['part'],r['extrusion_centerline_crossings'],r['line_widths_mm']) for r in records],flush=True)
assert all(x['all_triangle_vertices_match'] for p in meshchecks for x in p['objects']),meshchecks
