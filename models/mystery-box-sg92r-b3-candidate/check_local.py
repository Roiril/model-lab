"""Actual closed triangle solids incl speaker; calibrated Boolean intersection.
No physical or continuous motion proof. Inputs recorded by hash.
"""
from pathlib import Path
import sys,json,math,hashlib,itertools
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.dont_write_bytecode=True
import bpy,bmesh
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
import params as p
USE_B2=True
MAIN='editable_cube_B3.blend' if USE_B2 else 'editable_short_bolt_B1.blend'
OUT='local_audit_B3.json' if USE_B2 else 'local_audit.json'
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True,epsilon=1e-9)
def intersection(a,b):
 aa=a.copy();aa.data=a.data.copy();bpy.context.collection.objects.link(aa)
 mod=aa.modifiers.new('actual solid overlap','BOOLEAN');mod.solver='EXACT';mod.operation='INTERSECT';mod.object=b
 bpy.context.view_layer.objects.active=aa;bpy.ops.object.modifier_apply(modifier=mod.name)
 bm=bmesh.new();bm.from_mesh(aa.data);bad=sum(not e.is_manifold for e in bm.edges);v=abs(bm.calc_volume())*1e9
 pts=[aa.matrix_world@x.co*1000 for x in bm.verts];bb=[[min(x[k] for x in pts) for k in range(3)],[max(x[k] for x in pts) for k in range(3)]] if pts else []
 bm.free();bpy.data.objects.remove(aa,do_unlink=True);return {'volume_mm3':v,'nonmanifold_edges':bad,'bounds_mm':bb}
def inside(a,t):
 point=a.matrix_world@a.data.vertices[0].co;n=t.find_nearest(point)
 if n[0] is None or n[3]<1e-7:return False
 d=Vector((1,.371,.193)).normalized();hits=0
 for _ in range(150):
  x=t.ray_cast(point,d)
  if x[0] is None:break
  hits+=1;point=x[0]+d*1e-7
 return hits%2==1
def checks(moving,static):
 hits=[]
 for a in moving:
  va=[a.matrix_world@v.co for v in a.data.vertices];ba=[[min(v[k] for v in va) for k in range(3)],[max(v[k] for v in va) for k in range(3)]];ta=tree(a)
  for b in static:
   if a==b:continue
   vb=[b.matrix_world@v.co for v in b.data.vertices];bb=[[min(v[k] for v in vb) for k in range(3)],[max(v[k] for v in vb) for k in range(3)]]
   if any(ba[1][k]<=bb[0][k]+1e-9 or bb[1][k]<=ba[0][k]+1e-9 for k in range(3)):continue
   tb=tree(b)
   if not ta.overlap(tb) and not inside(a,tb) and not inside(b,ta):continue
   x=intersection(a,b)
   # Numerically coplanar slabs do not represent a finite-depth solid collision.
   flat=x['bounds_mm'] and min(x['bounds_mm'][1][k]-x['bounds_mm'][0][k] for k in range(3))<.00005
   if x['nonmanifold_edges'] or (x['volume_mm3']>.005 and not flat):hits.append({'parts':[a.name,b.name],**x})
 return hits
def offset(o,x=0,y=0,z=0):o.matrix_world=Matrix.Translation(Vector((x,y,z))*.001)@base[o.name]
def keyangle(a,z=0,x=0):
 T=Matrix.Translation(Vector((p.KEY_X,p.KEY_Y,0)))@Matrix.Rotation(math.radians(a),4,'Z')@Matrix.Translation(Vector((-p.KEY_X,-p.KEY_Y,0)))
 key.matrix_world=Matrix.Translation(Vector((x,0,z))*.001)@T@base[key.name]
def restore():
 for o in allobjs:o.matrix_world=base[o.name].copy()
def activate(file):
 global allobjs,base,key,body,bolt,speaker,unit
 bpy.ops.wm.open_mainfile(filepath=str(R/file));allobjs=[o for o in bpy.data.objects if o.type=='MESH'];base={o.name:o.matrix_world.copy() for o in allobjs}
 key=bpy.data.objects['13_body_cross_key'];body=bpy.data.objects['01_body'];bolt=bpy.data.objects.get('20_short_body_bolt');speaker=bpy.data.objects['REFERENCE exciter25x10']
 unit=[o for o in allobjs if o not in [key,body,bolt,speaker] and not o.name.startswith(('21_','22_','REFERENCE speaker'))]
report={'input_blend_sha256':hashlib.sha256((R/MAIN).read_bytes()).hexdigest(),'method':'BVH containment + EXACT sampled solid intersections >0.005 mm3; flat contact tolerance 0.00005 mm','physical_tested':False,'speaker_always_included':True,'paths':{},'probes':{},'baseline_compare':{}}
activate(MAIN)
report['closed_overlaps']=checks([body,key,bolt],[o for o in allobjs])
lift=p.BOLT_LIFT*1000;travel=p.BOLT_TRAVEL*1000
paths={
 'bolt_lift':[(0,z,0,0) for z in [lift*i/12 for i in range(13)]],
 'bolt_slide':[(x,lift,0,0) for x in [travel*i/59 for i in range(60)]],
 'bolt_lower_RELEASE':[(travel,lift*(1-i/12),0,0) for i in range(13)],
 'key_turn_RELEASE':[(travel,0,a,0) for a in range(91)],
 'key_withdraw_90':[(travel,0,90,-z) for z in range(31)]}
for name,states in paths.items():
 rows=[]
 for x,z,a,kz in states:
  restore();offset(bolt,x=x,z=z);keyangle(a,kz)
  hits=checks([key,bolt],[o for o in allobjs if o not in [key,bolt]])+checks([key],[bolt])
  if hits:rows.append({'bolt_x_mm':x,'bolt_z_mm':z,'key_deg':a,'key_z_mm':kz,'hits':hits})
 report['paths'][name]={'samples':len(states),'obstacles':rows};print(name,len(states),len(rows),flush=True)
 (R/OUT.replace('.json','_partial.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
for name,bx,bz,ka,kz in [('normal_key_positive5',0,0,5,0),('normal_key_negative5',0,0,-5,0),('key_turn_bolt_only_lifted',0,lift,5,0),('bolt_slide_without_lift',travel/2,0,0,0),('half_slide_lowered',travel/2,0,0,0),('key_withdraw_LOCK',0,0,0,-1),('bolt_up_overtravel',0,lift+1.,0,0),('bolt_down_after_key_removed',travel,-1.,90,-31),('bolt_X_overtravel',travel+1.,lift,90,-31),('bolt_X_reverse_overtravel',-1.,lift,0,0)]:
 restore();offset(bolt,x=bx,z=bz);keyangle(ka,kz)
 report['probes'][name]=checks([key,bolt],[o for o in allobjs if o not in [key,bolt]])+checks([key],[bolt])
# Direct normal torque direction probes against body guide, not first free Z.
for by in [-1.,1.]:
 restore();offset(bolt,y=by);report['probes'][f'bolt_tangential_Y{by}']=checks([bolt],[body,key])
# Full cassette and all independent horn stops remain together during vertical removal.
def removal(bolt_release):
 rows=[]
 for h in range(71):
  restore();keyangle(90,-31)
  if bolt:offset(bolt,x=bolt_release)
  for o in unit:offset(o,z=h)
  hits=checks(unit,[o for o in allobjs if o not in unit and o!=key])
  if hits:rows.append({'unit_lift_mm':h,'hits':hits})
 return {'samples':71,'obstacles':rows}
report['paths']['whole_unit_removal']=removal(travel)
print('whole_unit_removal',len(report['paths']['whole_unit_removal']['obstacles']),flush=True)
# Stem can translate within original cylindrical throat. Test a full conservative +X bias.
rows=[]
for a in range(91):
 restore();offset(bolt,x=travel);keyangle(a,x=.339)
 hits=checks([key],[bolt])
 if hits:rows.append({'key_deg':a,'key_x_bias_mm':.339,'hits':hits})
report['paths']['key_turn_RELEASE_bias_plus0p339']={'samples':91,'obstacles':rows,'note':'Conservative placement error for bolt clearance; not a proven full free-motion or manufacturing tolerance range'}
if not USE_B2:
 activate('baseline_reference.blend')
 report['baseline_compare']['whole_unit_removal']=removal(0)
 rows=[]
 for a in range(91):
  restore();keyangle(a)
  hits=checks([key],[o for o in allobjs if o!=key])
  if hits:rows.append({'key_deg':a,'hits':hits})
 report['baseline_compare']['key_turn']={'samples':91,'obstacles':rows}
else:
 report['baseline_compare']=json.loads((R/'local_audit.json').read_text('utf8'))['baseline_compare']
 cap=bpy.data.objects['21_separate_bolt_cap'];stop=bpy.data.objects['22_symmetric_cap_stop'];cx,cy=56.8,12.5
 def stopstate(a=0,z=0):
  T=Matrix.Translation(Vector((cx,cy,0))*.001)@Matrix.Rotation(math.radians(a),4,'Z')@Matrix.Translation(Vector((-cx,-cy,0))*.001)
  stop.matrix_world=Matrix.Translation(Vector((0,0,z))*.001)@T@base[stop.name]
 def empty_box():
  restore();keyangle(90,-31)
  for o in unit:offset(o,z=100)
 # Initial assembly is into empty box, with speaker already present.
 stages={
  'assembly_bolt_drop':[(20-i*.1,6.8,-20,90,-1,1.6) for i in range(164)],
  'assembly_bolt_realign_Y':[(3.7,6.8,-20,90,-1,1.6-i*.1) for i in range(17)],
  'assembly_bolt_realign_X':[(3.7,6.8,-20,90,-1+i*.1,0) for i in range(11)],
  'assembly_bolt_lower_intoLOCK':[(3.7-i*.1,6.8,-20,90,0,0) for i in range(38)],
  'assembly_cap_slide':[(0,6.8*(1-i/73),-20,90,0) for i in range(74)],
  'assembly_stop_insert90':[(0,0,-15+i,90,0) for i in range(16)],
  'assembly_stop_lift':[(0,0,z,90,0) for z in [i*.1 for i in range(19)]],
  'assembly_stop_turn_to_LOCK':[(0,0,1.8,90-i,0) for i in range(91)],
  'assembly_stop_lower_LOCK':[(0,0,1.8-i*.1,0,0) for i in range(19)]}
 for name,states in stages.items():
  rows=[]
  for row in states:
   bz,cxoff,sz,sa,bx=row[:5];by=row[5] if len(row)>5 else 0
   empty_box();offset(bolt,z=bz,x=bx,y=by);offset(cap,x=cxoff);stopstate(sa,sz)
   moving=[bolt] if name.startswith('assembly_bolt_') else [cap] if name=='assembly_cap_slide' else [stop]
   static=[o for o in allobjs if o not in moving and o not in unit and o!=key]
   hits=checks(moving,static)
   if hits:rows.append({'bolt_z_mm':bz,'bolt_x_mm':bx,'bolt_y_mm':by,'cap_x_mm':cxoff,'stop_z_mm':sz,'stop_deg':sa,'hits':hits})
  report['paths'][name]={'samples':len(states),'obstacles':rows};print(name,len(states),len(rows),flush=True)
 # Hold cap when key13 and complete unit are removed; retain bolt in all service states.
 for name,coff,stang,stz in [('cap_shift_blocked_by_stop',1,0,0),('stop_turn_without_lift',0,45,0),('stop_withdraw_LOCK',0,0,-1)]:
  empty_box();offset(cap,x=coff);stopstate(stang,stz)
  report['probes'][name]=checks([cap,stop],[body])+checks([cap],[stop])
 for bx,bz in [(0,0),(0,1.8),(2.95,1.8),(5.9,1.8),(5.9,0)]:
  for name,dx,dy,dz in [('down',0,0,-1),('up',0,0,2),('front',0,-1,0),('rear',0,1,0)]:
   empty_box();offset(bolt,x=bx+dx,y=dy,z=bz+dz)
   report['probes'][f'captive_bolt_x{bx}_z{bz}_{name}']=checks([bolt],[body,cap,stop])
(R/OUT).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('B1 LOCAL AUDIT SAVED',flush=True)
