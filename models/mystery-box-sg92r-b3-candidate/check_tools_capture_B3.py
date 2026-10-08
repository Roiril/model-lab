from pathlib import Path
import sys,json,hashlib,math
R=Path(__file__).resolve().parent
exec((R/'check_local.py').read_text('utf8').split("report={'input_blend_sha256'")[0])
from cad_utils import cube,cyl,add,cut
activate('editable_cube_B3.blend')
cap=bpy.data.objects['21_separate_bolt_cap'];stop=bpy.data.objects['22_symmetric_cap_stop']
report={'input_blend_sha256':hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest(),'physical_tested':False,'tools_measured':False,'paths':{},'probes':{},'limits':['Assumed driver dimensions; no real tool/hand/table verification','Box upright and supported above85mm clearance for underbox tool/handle','Lowering bolt assumes gravity with lateral tool force removed; no physical friction/force measurement','Collision-free tool envelope does not prove convenient gripping or sufficient strength']}
def empty_box():
 restore();keyangle(90,-31)
 for o in unit:offset(o,z=100)
for bx,bz in [(0,0),(0,1.8),(2.95,1.8),(5.9,1.8),(5.9,0)]:
 for label,dx,dy,dz in [('below_floor',0,0,-bz-1),('above_roof',0,0,2),('front',0,-1,0),('rear',0,1,0)]:
  empty_box();offset(bolt,x=bx+dx,y=dy,z=bz+dz)
  report['probes'][f'bolt_x{bx}_z{bz}_{label}']=checks([bolt],[body,cap,stop])
for label,x,y,z in [('cap_X',1,0,0),('cap_Y',0,1,0),('cap_reverseY',0,-1,0),('cap_Z',0,0,.9)]:
 empty_box();offset(cap,x=x,y=y,z=z);report['probes'][label]=checks([cap],[body,bolt,stop])
for angle in [15,-15]:
 empty_box();T=Matrix.Translation(Vector((.0568,.0125,0)))@Matrix.Rotation(math.radians(angle),4,'Z')@Matrix.Translation(Vector((-.0568,-.0125,0)))
 stop.matrix_world=T@base[stop.name];report['probes'][f'stop22_rotate_{angle}_without_push']=checks([stop],[body,cap])
for dz in [-.3,-.4,-1]:
 empty_box();offset(stop,z=dz);report['probes'][f'stop22_down_{dz}']=checks([stop],[body,cap])
# A single tool is introduced per path. Blade pushes the slot roof and side faces.
def driver(name,cx,cy,wx,wy,tip):
 o=cube(name,(cx-wx/2,cy-wy/2,-7),(cx+wx/2,cy+wy/2,tip))
 add(o,cyl('assumed shaft',(cx,cy,-21),1.25,28.1,'Z'))
 add(o,cyl('assumed handle',(cx,cy,-57.5),5.,45.1,'Z'));return o
for mode in ['bolt','key13','stop22']:
 cx,cy=(45.2,18.2) if mode=='bolt' else (36.5,26.5) if mode=='key13' else (56.8,12.5)
 wx,wy=(.8,2.2) if mode=='bolt' else (1.6,.6) if mode=='stop22' else (3.,.8)
 tip=1.4 if mode=='bolt' else 1.0 if mode=='stop22' else 1.2
 tool=driver('ASSUMED '+mode+' tool',cx,cy,wx,wy,tip);T0=tool.matrix_world.copy()
 if mode=='bolt':
  states=[(0,i*.1,0) for i in range(19)]+[(i*.1,1.8,0) for i in range(60)]+[(5.9,1.8-i*.1,0) for i in range(19)]
 elif mode=='key13':states=[(0,0,a) for a in range(91)]
 else:states=[(0,i*.1,0) for i in range(19)]+[(0,1.8,a) for a in range(91)]+[(0,-i,90) for i in range(16)]
 rows=[]
 for x,z,a in states:
  restore()
  if mode=='bolt':offset(bolt,x=x,z=z)
  elif mode=='key13':offset(bolt,x=5.9);keyangle(a)
  else:
   for o in unit:offset(o,z=100)
   keyangle(90,-31)
   T=Matrix.Translation(Vector((cx,cy,0))*.001)@Matrix.Rotation(math.radians(a),4,'Z')@Matrix.Translation(Vector((-cx,-cy,0))*.001)
   stop.matrix_world=Matrix.Translation(Vector((0,0,z))*.001)@T@base[stop.name]
  T=Matrix.Translation(Vector((cx,cy,0))*.001)@Matrix.Rotation(math.radians(a),4,'Z')@Matrix.Translation(Vector((-cx,-cy,0))*.001)
  tool.matrix_world=Matrix.Translation(Vector((x,0,z))*.001)@T@T0
  hits=checks([tool],allobjs)
  if hits:rows.append({'x_mm':x,'z_mm':z,'angle_deg':a,'hits':hits})
 report['paths'][mode+'_driver']={'samples':len(states),'obstacles':rows,'assumed_blade_XY_mm':[wx,wy],'assumed_handle_diameter_mm':10};print(mode,'driver',len(states),len(rows),flush=True)
 bpy.data.objects.remove(tool,do_unlink=True)
# Bottom pusher through original key opening raises the unit's existing front rail.
pusher=cyl('ASSUMED bottom pusher',(36.5,16.4,-1.),1.5,37.8,'Z');T0=pusher.matrix_world.copy();rows=[]
for i in range(19):
 empty_box();pusher.matrix_world=Matrix.Translation(Vector((0,0,-18+i))*.001)@T0
 hits=checks([pusher],[body,bolt,cap,stop,speaker])
 if hits:rows.append({'raise_mm':i,'hits':hits})
report['paths']['bottom_pusher_entry']={'samples':19,'obstacles':rows,'assumed_tip_final_Z_mm':17.9,'front_rail_bottom_Z_mm':18.0,'pusher_diameter_mm':3.0}
bpy.data.objects.remove(pusher,do_unlink=True)
restore();bm=bmesh.new();bm.from_mesh(stop.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));vol=0.;moment=Vector((0,0,0))
for f in bm.faces:
 a,b,c=[stop.matrix_world@v.co for v in f.verts];v=a.dot(b.cross(c))/6;vol+=v;moment+=(a+b+c)*(v/4)
bm.free();cg=moment/vol*1000;report['stop22_uniform_CG_mm']=list(cg);report['stop22_CG_offset_from_axis_XY_mm']=[cg.x-56.8,cg.y-12.5]
(R/'tools_capture_audit_B3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('TOOLS AND CAPTURE SAVED',flush=True)
