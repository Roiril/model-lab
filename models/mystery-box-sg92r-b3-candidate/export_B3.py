"""Print-coordinate export with double-precision area predicates, audited after save."""
from pathlib import Path
import sys,json,hashlib,math
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.dont_write_bytecode=True
import bpy,bmesh
from mathutils import Matrix,Quaternion
import cad_utils as c
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_B3.blend'))
baseline=json.loads((R/'baseline_manifest.json').read_text('utf8'))
Tc0=c.pivot_transform(*baseline['O'],math.radians(baseline['servo_range_deg'][0]))
manifest=[];old={p['name']:p for p in baseline['parts']}
for o in sorted([o for o in bpy.data.objects if o.type=='MESH' and o.name[:2].isdigit()],key=lambda x:x.name):
 row=dict(old.get(o.name,{'name':o.name,'group':'fixed','quantity':1,'print_axis':[1,0,0,0]}))
 T=Quaternion(row['print_axis']).to_matrix().to_4x4()
 state=o.matrix_world.copy()
 if row['group']=='crank':o.matrix_world=Tc0.inverted()@state
 row['print_bounds_mm']=c.export(o,R/'stl'/(o.name+'.stl'),T)
 o.matrix_world=state
 row['source_blend_sha256']=hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest()
 manifest.append(row);print('export',o.name,row['print_bounds_mm'],flush=True)
baseline.update(revision='B3',parts=manifest,physical_tested=False,center_screw_required=False,source_blend_sha256=hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest())
baseline['notes']=['22 tentative print parts; whole cube candidate with stock SG92R horn, no required metal links/pins/springs. Offline slices are diagnosis only.','Local20/22 index feet1.6mm, intentional+Z1.8 followed by translation/rotation. Normal service does not touch22.','Unmeasured printer/material fit: print local coupons first. Do not mix old versions.']
(R/'assembly_manifest.json').write_text(json.dumps(baseline,indent=2),encoding='utf8')
print('B3 EXPORT COMPLETE',len(manifest),flush=True)
