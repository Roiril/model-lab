"""Check the actual pin section and reserved wiring voids in the finished solids."""
import sys
sys.dont_write_bytecode=True
import importlib.util
import json
from pathlib import Path
import numpy as np

_spec=importlib.util.spec_from_file_location('sector_local_check',Path(__file__).with_name('check_local.py'))
C=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)
from sector_flag_local.evidence import require_meshes

evidence=require_meshes(C.HERE)
manifest=json.loads((C.HERE/'module.json').read_text(encoding='utf-8'))
interface=json.loads((C.MODEL/'interface.json').read_text(encoding='utf-8'))
solids={p:C.Solid.load(p,C.HERE/'_local'/(p+'.stl')) for p in manifest['parts']}
meter=C.Meter()
assert C.calibrate(meter)['pass']
section=[]
for tri in solids['hinge_pin'].tris:
    for a,b in zip(tri,np.roll(tri,-1,axis=0)):
        if abs(a[0]-b[0])<1e-8: continue
        t=(-15.5-a[0])/(b[0]-a[0])
        if 0<=t<=1: section.append((a+(b-a)*t)[1:])
dimensions=np.ptp(section,axis=0)
keeper=solids['bearing_bridge'].verts
radial=np.linalg.norm(keeper[:,1:]-C.K.H,axis=1)
neck_surface=keeper[np.abs(radial-1.6)<1e-3]
if not len(neck_surface): raise RuntimeError('Left pin-retaining bore is missing')
left_support=float(np.ptp(neck_surface[:,0]))
voids={
    'connector_bay':C.box_solid('bay',(-23,15,3.25),(-9,23,21.25)),
    # Provisional 4 x 1.6 mm bundle with 0.25 mm radial allowance.
    'wire_exit':C.box_solid('wire',(-20.55,13.45,12.65),(-18.45,15.0,17.15)),
}
hits={}
for name,void in voids.items():
    for pid,s in solids.items():
        volume,_=meter.common(void,np.eye(4),s,np.eye(4))
        if volume>C.VOLUME_FLOOR_MM3: hits[name+'/'+pid]=volume
    bad=C.envelope(void,np.eye(4),interface,.25,0)
    if bad: hits[name+'/envelope']=bad
minimum_d=min(float(s.verts[:,2].min()) for s in solids.values())
result={'pin_neck_section_vd_mm':dimensions.tolist(),
        'left_bearing_support_mm':left_support,
        'pin_neck_minimum_mm':float(min(dimensions)),
        'closed_minimum_d_mm':minimum_d,'wiring_void_hits':hits,
        'connector_bay_uvd_mm':[14,8,18],
        'wire_bundle_is_provisional':True,'service_loop_verified':False,
        'mesh_source_sha256':evidence['source_sha256'],
        'pass':bool(min(dimensions)>=3 and left_support>=3-1e-5 and minimum_d>=-1e-5 and not hits)}
C.write_json(C.HERE/'_local/features.json',result)
print('FEATURES',json.dumps({k:v for k,v in result.items() if k!='mesh_source_sha256'}),flush=True)
meter.dispose()
if not result['pass']: raise RuntimeError('Pin, flush face, or wiring space failed')
