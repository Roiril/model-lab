"""All support/interface bead samples against actual04/06 print meshes.
Run with Blender Python for BVH. Offline filament envelope screen only.
"""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET,re,collections,math,hashlib
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent;P=R/'slice_checks/plate_02_cassette/plate_02_cassette.3mf'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};PN='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
def matrix(text):
 a=np.array([float(v) for v in (text or '1 0 0 0 1 0 0 0 1 0 0 0').split()]);return a[:9].reshape(3,3),a[9:]
def load_stl(name):
 dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]);return np.frombuffer((R/'stl'/(name+'.stl')).read_bytes(),dtype=dt,offset=84)['v'].astype(float)
def bvh(tri):return BVHTree.FromPolygons([Vector(v) for v in tri.reshape(-1,3)],[tuple(range(i*3,i*3+3)) for i in range(len(tri))],all_triangles=True)
def inside_ray(point,mesh):
 direction=Vector((1,.173,.313)).normalized();origin=Vector(point);hits=0
 for i in range(80):
  h=mesh.ray_cast(origin,direction,1000.)
  if h[0] is None:break
  hits+=1;origin=h[0]+direction*.00005
 return hits%2==1
def cylinder_margin(point,triangle,xy_radius,zlo,zhi):
 poly=[v.copy() for v in triangle]
 for z,above in [(zlo,True),(zhi,False)]:
  out=[]
  if not poly:return None
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ia=a[2]>=z if above else a[2]<=z;ib=b[2]>=z if above else b[2]<=z
   if ia:out.append(a)
   if ia!=ib:out.append(a+(b-a)*(z-a[2])/(b[2]-a[2]))
  poly=out
 if not poly:return None
 p=point[:2];signs=[];distance=1e20;area=0
 for a,b in zip(poly,poly[1:]+poly[:1]):
  a=a[:2];b=b[:2];v=b-a;length=float(v@v);u=max(0,min(1,float((p-a)@v)/length)) if length>1e-15 else 0
  distance=min(distance,float(np.linalg.norm(p-a-u*v)));signs.append(v[0]*(p[1]-a[1])-v[1]*(p[0]-a[0]));area+=a[0]*b[1]-a[1]*b[0]
 if abs(area)>1e-8 and (all(v>=-1e-8 for v in signs) or all(v<=1e-8 for v in signs)):distance=0
 return distance-xy_radius
with zipfile.ZipFile(P) as z:
 settings=json.loads(z.read('Metadata/project_settings.config'));offset=settings.get('extruder_offset',['0x0'])[0].split('x');tool_offset=np.array([float(offset[0]),float(offset[1]),0.])
 root=ET.fromstring(z.read('3D/3dmodel.model'));objects={o.get('id'):o for o in root.findall('m:resources/m:object',NS)}
 config=ET.fromstring(z.read('Metadata/model_settings.config'));names={o.get('id'):next((x.get('value') for x in o.findall('metadata') if x.get('key')=='name'),'?') for o in config.findall('object')};boxes=[]
 for item in root.findall('m:build/m:item',NS):
  oid=item.get('objectid');component=objects[oid].find('m:components/m:component',NS)
  if component is None:continue
  child=ET.fromstring(z.read(component.get(PN+'path').lstrip('/')));ob=next(o for o in child.findall('m:resources/m:object',NS) if o.get('id')==component.get('objectid'))
  verts=np.array([[float(v.get(k)) for k in ('x','y','z')] for v in ob.findall('m:mesh/m:vertices/m:vertex',NS)]);mc,tc=matrix(component.get('transform'));mb,tb=matrix(item.get('transform'))
  local=verts@mc+tc;world=local@mb+tb;name=names[oid]
  if not name.startswith(('04','06')):continue
  tri=load_stl(name);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);nz=normal[:,2]/np.linalg.norm(normal,axis=1);center=tri.mean(axis=1)
  if name.startswith('04'):
   wy=center[:,1]+5.4;wz=67.3-center[:,0]
   top=np.all(abs(tri[:,:,2]-27.3)<.001,axis=1)
   recess=np.all(abs(tri[:,:,2]-2.7)<.001,axis=1)&(nz>.9)&(wy>=24.5-.001)&(wy<=55.5+.001)&(wz>=27-.001)&(wz<=41+.001)
   end=np.all(abs(tri[:,:,2]-8.4)<.001,axis=1)&(nz>.9)&(wy>=46.8-.001)&(wy<=51.3+.001)&(wz>=31-.001)&(wz<=43.3+.001)
   wire_land=np.all(abs(tri[:,:,2]-5.0)<.001,axis=1)&(nz>.9)&(wy>=46.8-.001)&(wy<=51.3+.001)&(wz>=27-.001)&(wz<=41+.001)
   allowed=top|recess|end|wire_land
  else:
   journal=tri[np.all(abs(tri[:,:,2])<.001,axis=1)]
   pts=np.unique(journal.reshape(-1,3),axis=0);xy=(pts[:,:2].min(axis=0)+pts[:,:2].max(axis=0))/2
   radii=np.linalg.norm(tri[:,:,:2]-xy,axis=2)
   allowed=np.all(abs(tri[:,:,2]-11.5)<.001,axis=1)&np.all(radii>=9.98,axis=1)
  boxes.append(dict(name=name,cup_center_xy=xy if name.startswith('06') else None,min=world.min(axis=0),max=world.max(axis=0),rotation_inv=np.linalg.inv(mb),translation=tb,local_min=local.min(axis=0),tri=tri,allowed=allowed,all_tree=bvh(tri),contained=[],protected=bvh(tri[~allowed]),protected_tri=tri[~allowed],horizontal=bvh(tri[abs(nz)>.9]),horizontal_allowed=allowed[abs(nz)>.9],horizontal_tri=tri[abs(nz)>.9],features=collections.Counter(),projections=collections.Counter(),widths=collections.Counter(),min_margin=1e10,projection_protected_z_gap=1e10,violations=[],projection_examples=[],zcounts=collections.Counter()))
 gcode=z.read('Metadata/plate_1.gcode').decode('utf8')
position=np.zeros(4);absolute=True;relative_e=True;feature='';width=.42;height=.2;segments=0
for line in gcode.splitlines():
 if line.startswith('; FEATURE: '):feature=line[11:].strip();continue
 if line.startswith('; LINE_WIDTH:'):width=float(line.split(':')[1]);continue
 if line.startswith('; LAYER_HEIGHT:'):height=float(line.split(':')[1]);continue
 raw=line.split(';')[0].strip()
 if raw=='G90':absolute=True;continue
 if raw=='G91':absolute=False;continue
 if raw=='M82':relative_e=False;continue
 if raw=='M83':relative_e=True;continue
 if raw.startswith('G92 '):
  for k,v in re.findall(r'([XYZE])([-+0-9.]+)',raw):position['XYZE'.index(k)]=float(v)
  continue
 if not re.match(r'^G[0123]\s',raw):continue
 old=position.copy();values={k:float(v) for k,v in re.findall(r'([XYZE])([-+0-9.]+)',raw)}
 for k,v in values.items():
  j='XYZE'.index(k);position[j]=v if absolute or k=='E' else position[j]+v
 extrusion=values.get('E',0) if relative_e else position[3]-old[3]
 distance=np.linalg.norm(position[:2]-old[:2])
 if not feature.startswith('Support') or extrusion<=0 or distance<.0001:continue
 segments+=1;rad=math.sqrt((width/2+.06)**2+(height/2)**2)
 if raw.startswith(('G2 ','G3 ')):
  ij={k:float(v) for k,v in re.findall(r'([IJ])([-+0-9.]+)',raw)};centre=old[:2]+np.array([ij.get('I',0),ij.get('J',0)])
  radius=np.linalg.norm(old[:2]-centre);a0=math.atan2(old[1]-centre[1],old[0]-centre[0]);a1=math.atan2(position[1]-centre[1],position[0]-centre[0]);sweep=(a1-a0)%(2*math.pi)
  if raw.startswith('G2 '):sweep=-((a0-a1)%(2*math.pi))
  count=max(1,math.ceil(abs(sweep)*radius/.1));samples=[]
  for t in np.linspace(0,1,count+1):
   a=a0+sweep*t;samples.append(np.array([*(centre+radius*np.array([math.cos(a),math.sin(a)])),old[2]*(1-t)+position[2]*t]))
 else:
  count=max(1,math.ceil(distance/.1));samples=[old[:3]*(1-t)+position[:3]*t for t in np.linspace(0,1,count+1)]
 sample_bounds=np.array(samples);sample_min=sample_bounds.min(axis=0);sample_max=sample_bounds.max(axis=0)
 for box in boxes:
  if np.any(sample_max[:2]<box['min'][:2]-.7) or np.any(sample_min[:2]>box['max'][:2]+.7):continue
  for sample in samples:
   local=(sample+tool_offset-box['translation'])@box['rotation_inv']-box['local_min']
   pt=local.copy();pt[2]-=height/2
   nearest=box['all_tree'].find_nearest(Vector(pt))
   if (Vector(pt)-nearest[0]).dot(nearest[1])<-.001 and len(box['contained'])<10 and inside_ray(pt,box['all_tree']):box['contained'].append({'feature':feature,'bead_center_xyz':pt.tolist(),'gcode':raw})
   candidates=box['protected'].find_nearest_range(Vector(pt),rad+.01)
   for co,n,idx,d in candidates:
    margin=cylinder_margin(pt,box['protected_tri'][idx],width/2+.06,local[2]-height-.005,local[2]+.005)
    if margin is None:continue
    box['min_margin']=min(box['min_margin'],margin)
    if margin<-.001:
     example={'feature':feature,'gcode':raw,'sample_nozzle_xyz':local.tolist(),'width_mm':width,'height_mm':height,'expanded_bead_margin_mm':margin,'nearest_protected_point':list(co)}
     box['violations'].append(example);box['violations']=sorted(box['violations'],key=lambda x:x['expanded_bead_margin_mm'])[:30]
   box['features'][feature]+=1;box['widths'][str(width)]+=1;box['zcounts'][f'{local[2]:.2f}']+=1
   if feature=='Support interface':
    q=Vector(local)
    for co,n,idx,d in box['horizontal'].find_nearest_range(q,.65):
     if abs(co.z-local[2])>.6 or math.hypot(co.x-local[0],co.y-local[1])>width/2+.06:continue
     okay=bool(box['horizontal_allowed'][idx]);label='allowed_nonfunctional'
     if not okay and box['name'].startswith('06') and abs(co.z-11.9)<.001 and np.linalg.norm(np.array(co[:2])-box['cup_center_xy'])>=8.65:
      okay=True;label='unused_outer_transition_band_R8.65_plus'
     box['projections'][label if okay else 'other_or_protected']+=1
     if not okay:box['projection_protected_z_gap']=min(box['projection_protected_z_gap'],abs(co.z-local[2]))
     if not okay and len(box['projection_examples'])<10:box['projection_examples'].append({'nozzle_xyz':local.tolist(),'projected_surface_xyz':list(co),'surface_triangle':box['horizontal_tri'][idx].tolist()})
report={'physical_tested':False,'input_slice_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'input_plate_sha256':hashlib.sha256((R/'plates/plate_02_cassette.3mf').read_bytes()).hexdigest(),'support_extrusion_segments':segments,'method':'All normal-support/interface straight extrusion segments sampled <=0.1mm. Actual line width and layer height; enclosing sphere uses width/2+0.06mm and height/2. Covers nominal segment sampling laterally, not sag, fusing or printed deformation. All04/06 other facets conservatively protected. Interface upper/lower nominal Z-gap projections onto horizontal facets separately classified. Not proof of full deposited filament or removal.','objects':{}}
for box in boxes:
 report['objects'][box['name']]={'samples_by_feature':dict(box['features']),'line_width_sample_counts':dict(box['widths']),'min_protected_facet_expanded_bead_margin_mm':box['min_margin'],'bead_envelope_protected_examples':box['violations'],'interface_projection_facet_counts':dict(box['projections']),'interface_projection_other_examples':box['projection_examples'],'approved_surface_triangles':int(box['allowed'].sum()),'protected_other_triangles':int((~box['allowed']).sum()),'z_sample_counts':dict(box['zcounts'])}
 print('SUPPORT',box['name'],dict(box['features']),'margin',box['min_margin'],'projection',dict(box['projections']),flush=True)
 report['objects'][box['name']]['min_protected_facet_expanded_bead_margin_mm']=None if box['min_margin']==1e10 else box['min_margin']
 report['objects'][box['name']]['nominal_bead_protected_overlap_detected']=bool(box['violations'])
 report['objects'][box['name']]['projected_protected_min_vertical_gap_mm']=None if box['projection_protected_z_gap']==1e10 else box['projection_protected_z_gap']
 report['objects'][box['name']]['bead_center_inside_model_examples']=box['contained']
report['removal_review']={'04':'Sparse columns beneath U saddle can be trapped as one rigid piece. Before electronics, cut/break into3-5mm pieces and remove through open cradle (Y23.2..46.8 aboveZ43.3) or wire-side opening. Never pry on servo locating face, keeper slots, bearings or thrust face. Physical access/damage-free removal require cradle coupon and actual04 trial.','06':'Support around D12 journal can form a ring. Split into at least two pieces and peel radially outsideR10, before stock horn insertion. Protect D12 journal, A blind bearing, horn pocket and R6.3..8.5 capture annulus. Real bridging/flatness/removal not tested.','limits':'Geometry-based removal plan, not tested tool/snap mechanics. Stop if fused; change slicing rather than force a protected surface.'}
report['tool_xy_offset_mm']=tool_offset[:2].tolist()
report['method']+=' Extruder XY offset from actual sliced settings added before inverse object transform. Arcs sampled by I/J center; actual independent support layer heights used. Potential interface projection facets within0.6mm vertically and expanded bead width laterally, independent of support Z-gap rounding.'
report['method']+=' Sphere is only broad-phase. Each candidate protected triangle is clipped to nozzleZ-height-0.005..nozzleZ+0.005; XY distance to the clipped polygon is checked against width/2+0.06. This cylindrical envelope avoids sphere-only false corner contacts. A min-margin of1e10 means no nearby protected facet in the broad-phase, not a measured clearance.'
report['method']+=' Support transition paths also included; XY prefilter uses all arc sample points, not endpoint-only arc bounds.'
report['input_stl_sha256']={b['name']:hashlib.sha256((R/'stl'/(b['name']+'.stl')).read_bytes()).hexdigest() for b in boxes}
report['method']+=' Bead-centre containment candidates from nearest outward face are checked by ray parity; nearest-face sign alone is not used at concave/far corners.'
(R/'support_contact_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
