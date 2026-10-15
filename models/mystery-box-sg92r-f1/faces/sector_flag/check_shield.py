"""The identical 585225 first-hit rays used for all three candidates."""
import sys,importlib.util,json,math
from pathlib import Path
sys.dont_write_bytecode=True
_spec=importlib.util.spec_from_file_location('sector_local_check',Path(__file__).with_name('check_local.py'))
C=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(C)
from sector_flag_local.evidence import require_meshes
from sector_flag_local.shielding import check,VIEWS
evidence=require_meshes(C.HERE)
manifest=json.loads((C.HERE/'module.json').read_text(encoding='utf-8'))
solids={p:C.Solid.load(p,C.HERE/'_local'/(p+'.stl')) for p in manifest['parts']}
result=check(solids,C.K.transforms,[60,75,90,105,120],
             {'servo','horn','input_cup','input_gear','input_spindle','sector_gear','hinge_pin'},
             emit=lambda r:print('SHIELD',r['servo_deg'],r['view_degrees'],r['visible_mechanism_pixels'],flush=True))
result['mesh_source_sha256']=evidence['source_sha256']
result['exchange_key_heads']='The exterior operating heads are not internal mechanism parts.'
C.write_json(C.HERE/'_local/shield.json',result)
print('SHIELD_TOTAL',result['visible_hits'],'/',result['rays'],flush=True)
if not result['pass']:raise RuntimeError('Visible internal mechanism; see _local/shield.json')
dense=check(solids,C.K.transforms,[60,75,90,105,120],
            {'servo','horn','input_cup','input_gear','input_spindle','sector_gear','hinge_pin'},grid_mm=.1,
            views=VIEWS+((45,45),(45,-45),(-45,45),(-45,-45),
                         (-math.degrees(math.atan2(70,150)),math.degrees(math.atan2(50,150))),
                         (math.degrees(math.atan2(70,150)),-math.degrees(math.atan2(50,150)))))
dense['mesh_source_sha256']=evidence['source_sha256']
C.write_json(C.HERE/'_local/shield_dense.json',dense)
print('SHIELD_DENSE_TOTAL',dense['visible_hits'],'/',dense['rays'],flush=True)
if not dense['pass']:raise RuntimeError('Mechanism visible between primary grid lines; see _local/shield_dense.json')
