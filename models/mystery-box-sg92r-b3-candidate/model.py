"""Rebuild B3 on Blender5.1. User SG92R reference is bundled for portability.
Printed parts remain22; reference envelopes are never print parts.
"""
from pathlib import Path
import runpy,shutil,json,hashlib,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));sys.dont_write_bytecode=True
if '--frozen-preview' in sys.argv:
 runpy.run_path(str(R/'export_native_preview.py'),run_name='__main__')
 raise SystemExit(0)
for name in ['baseline_model.py']:
 runpy.run_path(str(R/name),run_name='__main__')
shutil.copy2(R/'editable_cube_v6.blend',R/'baseline_reference.blend')
shutil.copy2(R/'assembly_manifest.json',R/'baseline_manifest.json')
for name in ['local_cad.py','build_B3.py','add_speaker_envelopes.py','export_B3.py','make_local_coupons.py']:
 runpy.run_path(str(R/name),run_name='__main__')
(R/'rebuild_provenance.json').write_text(json.dumps({'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in R.glob('*.py')},'blend_sha256':hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest(),'physical_tested':False},indent=2),encoding='utf8')
print('B3 REBUILD COMPLETE',flush=True)
if R.parent.name=='models' and (R.parent.parent/'lib/blender_utils.py').is_file():
 runpy.run_path(str(R/'export_native_preview.py'),run_name='__main__')
