"""Three physical candidates, identical 153x153 grid, five poses, five views."""
import sys,importlib,importlib.util,types,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('C',HERE/'check_local.py')
C=importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
from sector_flag_local.shielding import check
from sector_flag_local import deep_geometry as D
from sector_flag_local import recipe
baseline=types.ModuleType('sector_arc_candidate')
baseline.__path__=[str(HERE/'candidates/arc60')]
sys.modules[baseline.__name__]=baseline
sys.modules[baseline.__name__+'.recipe']=recipe
A=importlib.import_module(baseline.__name__+'.geometry')
AK=importlib.import_module(baseline.__name__+'.kinematics')
sg=C.load(C.ROOT/'models/sg92r-photo/params.py','sg_compare')
interface=json.loads((HERE.parents[1]/'interface.json').read_text(encoding='utf-8'))
common=types.SimpleNamespace(ROOT=C.ROOT,SG=sg)
mechanism={'servo','horn','input_gear','sector_gear','hinge_pin'}
results={}
def measure(name,parts,angles,transforms):
    solids={p:C.solid(row['object'],p) for p,row in parts.items()}
    row=check(solids,transforms,angles,mechanism)
    row['opening_deg']=angles[-1]-angles[0]
    row['mesh_sha256']={p:hashlib.sha256(s.tris.tobytes()).hexdigest() for p,s in solids.items()}
    results[name]=row
    print(name,row['visible_hits'],'/',row['rays'],flush=True)
parts=A.build(interface,common)
measure('concentric_arc_60',parts,[60,75,90,105,120],AK.transforms)
# The conservative reduced-angle candidate adds a fixed roof to the existing
# concentric cover. Its residual outside teeth cannot be hidden by a fixed roof.
C.G.union(parts['panel']['object'],C.G.box(6.5,15.35,-24.5,6,0,1.2))
measure('fixed_roof_45',parts,[60,71.25,82.5,93.75,105],AK.transforms)
C.bpy.ops.object.select_all(action='SELECT'); C.bpy.ops.object.delete(use_global=False)
parts=D.build(interface,common)
measure('deep_axis_60',parts,[60,75,90,105,120],C.K.transforms)
C.write_json(HERE/'_local/shield_comparison.json',results)
