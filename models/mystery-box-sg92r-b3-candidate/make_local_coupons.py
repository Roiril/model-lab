"""Actual localized geometry, not extra parts in final assembly."""
from pathlib import Path
import sys,shutil,json,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.dont_write_bytecode=True
import bpy
from cad_utils import *
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_B3.blend'))
out=R/'coupons';out.mkdir(exist_ok=True);rows=[]
body=duplicate(bpy.data.objects['01_body'],'test_30_local_bottom_lock')
boolean(body,cube('actual local50x48x18window',(20,0,0),(70,48,18)),'INTERSECT')
rows.append({'name':body.name,'source':'01_body','window_mm':[[20,0,0],[70,48,18]],'bounds_mm':export(body,out/(body.name+'.stl')),'purpose':'Actual20/21/22guide, cavity side wall and key throat. Front/back floor strips keep coupon one connected solid. Same printZ orientation. Tests gravity return, indexing, cap insertion, removal and roof bridging; no strength qualification.'})
for n,label in [(13,'actual_key'),(20,'actual_bolt'),(21,'actual_cap'),(22,'actual_stop')]:
 src=next(o.name for o in bpy.data.objects if o.name.startswith(f'{n:02}_'))
 name=f'test_{n+20}_{label}';shutil.copy2(R/'stl'/(src+'.stl'),out/(name+'.stl'))
 rows.append({'name':name,'source':src,'reusable_in_assembly':True,'purpose':'Same candidate part, same orientation and clearance; test before full box. Stop if sticking, cracked or damaged.'})
(R/'coupon_manifest.json').write_text(json.dumps({'source_blend_sha256':hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest(),'physical_tested':False,'tests':rows},indent=2),encoding='utf8')
print('LOCAL COUPONS',len(rows),flush=True)
