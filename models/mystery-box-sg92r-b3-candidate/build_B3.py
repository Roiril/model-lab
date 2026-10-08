"""B2 local: independent slide cap and symmetric indexed assembly stop22.
Uses saved B1 local CAD, original19 horn retention remains unchanged.
All parts are diagnostic only until assembly/operation/removal checks pass.
"""
from pathlib import Path
import sys,math,json,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.dont_write_bytecode=True
import bpy,bmesh
from mathutils import Matrix
from cad_utils import *
import params as p
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_short_bolt_B1.blend'))
body=bpy.data.objects['01_body']
cut(bpy.data.objects['13_body_cross_key'],cube('speaker clearance on broad rear key arm',(0,p.KEY_ARM_REAR_Y*1000,9.2),(31.,36.,14.1)))
cut(bpy.data.objects['20_short_body_bolt'],cube('underside bolt tool groove',(44.65,16.9,-.1),(45.75,19.5,1.4)))
cut(body,cube('key withdrawal restored through whole new guide',(31.,3.2,-.2),(42.,45.,9.3)))
cut(body,cube('split upper guide and old upper load pad',(40.4,12.5,9.3),(55.4,23.,18.2)))
# T rails alongX hold the cap vertically. Roof load transfers to the old low pad.
add(body,cube('front T thick seating shelf',(42.,10.7,2.3),(48.5,14.8,9.3)))
for y0,y1,ly0,ly1 in [(9.5,10.7,9.5,14.8)]:
 add(body,cube('cap thick side rail root',(42.,y0,2.3),(48.5,y1,14.3)))
 add(body,cube('cap retaining T lip',(42.,ly0,11.9),(48.5,ly1,14.3)))
cut(body,cube('reopen bolt wing',(40.9,13.2,3.0),(51.,22.6,9.3)))
cut(body,cube('reopen lower bolt arm',(40.9,20.2,3.0),(51.,28.8,9.3)))
cut(body,cube('reopen bolt neck',(42.9,16.2,-.2),(53.4,20.8,9.3)))
cap=cube('21_separate_bolt_cap',(42.,11.0,9.3),(55.,20.2,11.1))
add(cap,cube('front rail load seating pad',(46.,15.1,11.0),(55.,18.9,17.9)))
add(cap,cube('cap stop tab',(53.4,9.1,9.3),(60.2,15.9,11.1)))
# Printed stop22 holds cap X independently of cross-key13/cassette; circular shaft
# has no torsion moment from ideal horizontal bearing force through its center.
cx,cy=56.8,12.5
add(body,cyl('stop22 floor boss',(cx,cy,4.75),5.6,4.9,'Z'))
cut(body,cube('cap tab side-entry corridor',(53.1,8.8,9.0),(67.5,16.2,11.4)))
cut(body,cube('wide head insertion through open guide',(40.9,15.4,-.2),(55.4,21.0,7.3)))
for xa,xb in [(43.9,46.5),(49.8,52.4)]:
 cut(body,cube('reopen primary index bottom pocket',(xa,13.2,-.2),(xb,15.7,1.9)))
cut(body,cube('reopen primary index upper track',(43.9,13.2,1.9),(52.4,15.7,7.9)))
cut(body,cyl('stop22 round head base recess',(cx,cy,2.35),2.6,5.1,'Z'))
cut(body,cyl('stop22 index turning chamber',(cx,cy,2.85),4.9,1.9,'Z'))
for axis in ['X','Y']:
 lo=(cx-4.9,cy-1.6,-.2) if axis=='X' else (cx-1.6,cy-4.9,-.2)
 hi=(cx+4.9,cy+1.6,1.9) if axis=='X' else (cx+1.6,cy+4.9,1.9)
 cut(body,cube('stop22 opposed index head pocket',lo,hi))
cut(body,cyl('stop22 stem bore',(cx,cy,5.15),2.2,4.3,'Z'))
cut(body,cyl('stop22 ear rotation chamber',(cx,cy,7.2),4.4,4.4,'Z'))
cut(body,cube('stop22 Y insertion',(cx-1.6,cy-4.4,-.2),(cx+1.6,cy+4.4,7.4)))
cut(body,cyl('stop22 upper shaft clearance',(cx,cy,10.85),2.2,7.9,'Z'))
cut(cap,cyl('stop22 cap bore',(cx,cy,9.7),2.2,3.0,'Z'))
stop=cyl('22_symmetric_cap_stop',(cx,cy,1.5),2.3,2.6,'Z')
add(stop,cyl('stop22 stem',(cx,cy,7.45),1.9,9.7,'Z'))
add(stop,cube('stop22 balanced thick capture ears',(cx-4.1,cy-1.3,5.3),(cx+4.1,cy+1.3,7.3)))
for xa,xb in [(cx-4.5,cx-1.4),(cx+1.4,cx+4.5)]:
 add(stop,cube('stop22 opposed rigid index feet',(xa,cy-1.3,.2),(xb,cy+1.3,1.8)))
cut(stop,cube('stop22 bottom tool slot',(cx-1.,cy-.45,-.1),(cx+1.,cy+.45,1.0)))
color(cap,'Cap',(.35,.35,.38));color(stop,'Cap stop',(.20,.20,.22))
audit=[]
for o in [body,bpy.data.objects['13_body_cross_key'],bpy.data.objects['20_short_body_bolt'],cap,stop]:
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume()*1e9
 seen=set();components=0
 for v in bm.verts:
  if v in seen:continue
  components+=1;seen.add(v);stack=[v]
  while stack:
   a=stack.pop()
   for e in a.link_edges:
    b=e.other_vert(a)
    if b not in seen:seen.add(b);stack.append(b)
 bm.free();assert bad==0 and vol>0 and components==1,(o.name,bad,vol,components)
 audit.append({'name':o.name,'components':components,'nonmanifold_edges':bad,'volume_mm3':vol})
bpy.ops.wm.save_as_mainfile(filepath=str(R/'editable_cube_B3.blend'))
report={'version':'B2-local-2','input_B1_sha256':hashlib.sha256((R/'editable_short_bolt_B1.blend').read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest(),'parts':22,'modified_meshes':audit,'cap_assembly_start_offset_X_mm':6.8,'stop22_center_mm':[cx,cy],'stop22_release':[{'Z_mm':1.8},{'rotation_Z_deg':90},{'Z_withdraw_mm':-15}],'normal_service':'bolt20 lift1.8 slideX5.9 lower; key13 rotate90 withdraw; lift complete19-part unit while21/22 remain on body','physical_tested':False,'print_ready':False}
report['version']='B3-integrated-3'
report['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(R/'build_result_B3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('B2 CAD SAVED',json.dumps(report,ensure_ascii=False),flush=True)
