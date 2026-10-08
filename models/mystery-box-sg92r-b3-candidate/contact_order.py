"""Fine first-contact study. Actual triangle surfaces, no volume threshold.
Conservative key XY bias disk <=0.339 mm sampled on rings, not measured fit.
Only key/bolt/speaker; impossible body-biased starts labeled separately.
"""
from pathlib import Path
import sys,math,json,hashlib
R=Path(__file__).resolve().parent;sys.dont_write_bytecode=True
import bpy,bmesh
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
main='editable_cube_B3.blend'
if '--' in sys.argv and len(sys.argv)>sys.argv.index('--')+1:main=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=str(R/main))
key=bpy.data.objects['13_body_cross_key'];base=key.matrix_world.copy()
targets=[bpy.data.objects[n] for n in ['01_body','20_short_body_bolt','REFERENCE exciter25x10']]
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True,epsilon=1e-10)
trees={o.name:tree(o) for o in targets}
def pose(a,x=0,y=0):
 T=Matrix.Translation(Vector((.0365,.0265,0)))@Matrix.Rotation(math.radians(a),4,'Z')@Matrix.Translation(Vector((-.0365,-.0265,0)))
 key.matrix_world=Matrix.Translation(Vector((x*.001,y*.001,0)))@T@base
 return tree(key)
def contact(a,x,y,o):
 if not pose(a,x,y).overlap(trees[o.name]):return False
 # A horizontal bearing face touching a floor does not block yaw.
 # Reject zero-thickness intersection slabs before calling it a stop.
 aa=key.copy();aa.data=key.data.copy();bpy.context.collection.objects.link(aa)
 mod=aa.modifiers.new('first finite overlap','BOOLEAN');mod.solver='EXACT';mod.operation='INTERSECT';mod.object=o
 bpy.context.view_layer.objects.active=aa;bpy.ops.object.modifier_apply(modifier=mod.name)
 bm=bmesh.new();bm.from_mesh(aa.data);vol=abs(bm.calc_volume())*1e9
 pts=[aa.matrix_world@v.co*1000 for v in bm.verts]
 depth=min(max(v[k] for v in pts)-min(v[k] for v in pts) for k in range(3)) if pts else 0
 bm.free();bpy.data.objects.remove(aa,do_unlink=True)
 return vol>1e-6 and depth>.00005
def first(sign,x,y,o):
 if contact(0,x,y,o):return {'start_intersection':True,'angle_abs_deg':0}
 for i in range(1,101):
  if contact(sign*i*.1,x,y,o):
   lo=(i-1)*.1;hi=i*.1
   for _ in range(12):
    mid=(lo+hi)/2
    if contact(sign*mid,x,y,o):hi=mid
    else:lo=mid
   return {'angle_abs_deg':hi,'bracket_deg':[lo,hi]}
 return {'angle_abs_deg':None,'clear_through_abs_deg':10}
rows=[]
biases=[(0,0)]+[(r*math.cos(i*math.tau/32),r*math.sin(i*math.tau/32)) for r in [.17,.339] for i in range(32)]
for x,y in biases:
 row={'bias_XY_mm':[x,y],'minus':{o.name:first(-1,x,y,o) for o in targets},'plus':{o.name:first(1,x,y,o) for o in targets}}
 rows.append(row)
 if len(rows)%8==1:print('bias study',len(rows),'/',len(biases),flush=True)
def stat(sign):
 valid=[r for r in rows if not any(v.get('start_intersection') for v in r[sign].values())]
 unsafe=[];margins=[]
 for r in valid:
  v=r[sign];b=v['20_short_body_bolt']['angle_abs_deg'];s=v['REFERENCE exciter25x10']['angle_abs_deg'];body=v['01_body']['angle_abs_deg']
  structural=min([x for x in [b,body] if x is not None],default=999)
  if s is not None:
   margins.append(s-structural)
   if structural>=s:unsafe.append(r['bias_XY_mm'])
 return {'valid_nonintersecting_start_biases':len(valid),'unsafe_first_speaker_biases':unsafe,'minimum_angle_margin_deg':min(margins) if margins else None}
report={'source_blend':main,'source_sha256':hashlib.sha256((R/main).read_bytes()).hexdigest(),'method':'BVH candidate then exact finite-solid intersections>1e-6mm3 and minimum overlap depth>0.00005mm; flat coplanar bearing touches excluded. coarse0.1 degree bracket then12 bisections (0.0000245 degree), numerical reporting only. Not physical contact force.', 'bias_disk_mm':.339,'bias_samples':len(biases),'nominal':rows[0],'minus_summary':stat('minus'),'plus_summary':stat('plus'),'rows':rows,'physical_tested':False}
out='contact_order_'+('B3' if 'B3' in main else 'B2')+'.json'
(R/out).write_text(json.dumps(report,indent=2),encoding='utf8')
print('CONTACT_ORDER',json.dumps({k:v for k,v in report.items() if k not in ['rows']},indent=2),flush=True)
