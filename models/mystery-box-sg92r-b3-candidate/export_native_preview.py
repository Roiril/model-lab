"""Register frozen B3 in model-lab; assembly preview is NOT a print STL."""
from pathlib import Path
import sys,struct,json,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
import bpy
from cad_utils import export
assert R.parent.name=='models' and (R.parent.parent/'lib/blender_utils.py').is_file()
source=R/'editable_cube_B3.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
manifest=json.loads((R/'assembly_manifest.json').read_text(encoding='utf8'))
parts=[bpy.data.objects[p['name']] for p in manifest['parts']]
references=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('REFERENCE ')]
sys.path.insert(0,str(R.parent.parent/'lib'))
from blender_utils import export_stl
export_stl(R.name,only=parts+references)
out=R/'preview_components';out.mkdir(exist_ok=True);payload=[];count=0
for i,o in enumerate(parts+references):
 f=out/(f'{i:02}_'+o.name.replace(' ','_')+'.stl');export(o,f,normalize=False);b=f.read_bytes();count+=struct.unpack_from('<I',b,80)[0];payload.append(b[84:])
target=R.parent.parent/'exports'/(R.name+'.stl')
target.write_bytes(b'B3 ASSEMBLY PREVIEW ONLY | mm | 22 separate print STLs'.ljust(80,b'\0')+struct.pack('<I',count)+b''.join(payload))
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(R/'native_preview_record.json').write_text(json.dumps({'source_sha256':digest,'preview_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'print_parts':len(parts),'reference_objects':len(references),'source_unmodified':True},indent=2),encoding='utf8')
print('FROZEN B3 NATIVE PREVIEW',len(parts),count,flush=True)
