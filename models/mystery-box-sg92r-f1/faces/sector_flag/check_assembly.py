"""Check cumulative assembly poses against the actual local STLs."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import importlib.util
_spec=importlib.util.spec_from_file_location('sector_local_check',Path(__file__).with_name('check_local.py'))
C=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)
import json
import math
import numpy as np
from sector_flag_local import assembly
from sector_flag_local.evidence import require_meshes

evidence=require_meshes(C.HERE)
meter=C.Meter()
assert C.calibrate(meter)['pass']
manifest=json.loads((C.HERE/'module.json').read_text(encoding='utf-8'))
interface=json.loads((C.MODEL/'interface.json').read_text(encoding='utf-8'))
solids={p:C.Solid.load(p,C.HERE/'_local'/(p+'.stl')) for p in manifest['parts']}
poses={}
hits={}
samples=0
max_move=0.
max_turn=0.
for step in assembly.steps(interface,None):
    previous=None
    for i,frame in enumerate(step['frames']):
        if previous:
            for p,mat in frame.items():
                delta=mat@np.linalg.inv(previous[p])
                max_move=max(max_move,float(np.linalg.norm(mat[:3,3]-previous[p][:3,3])))
                max_turn=max(max_turn,math.degrees(math.acos(np.clip((np.trace(delta[:3,:3])-1)/2,-1,1))))
        poses.update(frame)
        previous=frame
        done=set()
        for a in frame:
            for b in poses:
                pair=tuple(sorted((a,b)))
                if a==b or pair in done: continue
                done.add(pair)
                v,bounds=meter.common(solids[a],poses[a],solids[b],poses[b])
                samples+=1
                if set(pair)=={'servo','horn'} and v<=.05: continue
                if v>C.VOLUME_FLOOR_MM3:
                    remaining=max(float(np.linalg.norm(frame[p][:3,3]-step['frames'][-1][p][:3,3])) for p in frame)
                    allowance=next((row for row in manifest['allowances'] if row['type']=='snap' and
                                    any(set(pp)==set(pair) for pp in row['pairs']) and
                                    remaining<=row['engage_mm'] and i<len(step['frames'])-1),None)
                    if allowance: continue
                    key=step['id']+'/'+a+'/'+b
                    if v>hits.get(key,{}).get('volume_mm3',0):
                        hits[key]={'frame':i,'volume_mm3':v,'remaining_mm':remaining,'bounds':bounds}
    print('ASSEMBLY',step['id'],'unresolved',len(hits),flush=True)
result={'pair_evaluations':samples,'max_translation_step_mm':max_move,'max_rotation_step_deg':max_turn,
        'hits':hits,'final_identity':all(np.allclose(m,np.eye(4),atol=1e-7) for m in poses.values()),
        'final_parts':sorted(poses),'mesh_source_sha256':evidence['source_sha256'],
        'assembly_source_sha256':C.hashlib.sha256((C.HERE/'assembly.py').read_bytes()).hexdigest(),
        'pass':not hits and max_move<=1.000001 and max_turn<=5.000001 and all(np.allclose(m,np.eye(4),atol=1e-7) for m in poses.values()) and set(poses)==set(manifest['parts'])}
C.write_json(C.HERE/'_local/assembly.json',result)
print('RESULT',json.dumps(result),flush=True)
meter.dispose()
if not result['pass']: raise RuntimeError('Unresolved assembly path')
