from pathlib import Path
import sys,json,struct
import bpy
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from cad_utils import export
assert R.parent.name=='models' and R.name=='mystery-box-sg92r-v6'
bpy.ops.wm.open_mainfile(filepath=str(R/'editable_cube_v6.blend'))
D=json.loads((R/'assembly_manifest.json').read_text())
names=[x['name'] for x in D['parts']]+['REFERENCE SG92R body','REFERENCE SG92R horn','REFERENCE SG92R wire','REFERENCE exciter25x10']
payload=[];count=0;out=R/'preview_components';out.mkdir(exist_ok=True)
for i,name in enumerate(names):
    o=bpy.data.objects[name];fn=out/(str(i+1).zfill(2)+'_'+name.replace(' ','_')+'.stl');export(o,fn,normalize=False)
    data=fn.read_bytes();count+=struct.unpack_from('<I',data,80)[0];payload.append(data[84:])
target=R.parent.parent/'exports'/(R.name+'.stl')
target.write_bytes(b'ASSEMBLY PREVIEW ONLY | mm | use separate stl print parts'.ljust(80,b'\0')+struct.pack('<I',count)+b''.join(payload))
print('Preview-only repair complete',count,'triangles')
