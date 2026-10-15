"""Probe latest local STL files. Run check_local first; no parent build artifacts used."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import importlib.util
_spec=importlib.util.spec_from_file_location('sector_local_check',Path(__file__).with_name('check_local.py'))
C=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)
import json
from sector_flag_local.interface_checks import check
from sector_flag_local.evidence import require_meshes

evidence=require_meshes(C.HERE)
meter=C.Meter()
assert C.calibrate(meter)['pass']
manifest=json.loads((C.HERE/'module.json').read_text(encoding='utf-8'))
solids={p:C.Solid.load(p,C.HERE/'_local'/(p+'.stl')) for p in manifest['parts']}
result=check(meter,solids,manifest)
result['mesh_source_sha256']=evidence['source_sha256']
C.write_json(C.HERE/'_local/interfaces.json',result)
for kind in ('drive','retention'):
    print(kind.upper(),json.dumps(result[kind]),flush=True)
meter.dispose()
if not result['pass']: raise RuntimeError('Unresolved drive or retention interface')
