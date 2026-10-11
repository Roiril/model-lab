"""Blender --background --python-exit-code 1 --python tools/test_solid_volume.py."""
import sys
from pathlib import Path
import importlib.util
import json
import bmesh

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))
from solid_volume import closed_boundary_volume

for model in ('mystery-box-sg92r-c3', 'mystery-box-sg92r-c4'):
    folder = ROOT / 'models' / model
    for key in ('params', 'motion'):
        sys.modules.pop(key, None)
    sys.path.insert(0, str(folder))
    spec = importlib.util.spec_from_file_location('volume_fixture_verify', folder / 'verify.py')
    verify = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verify)
    result = verify.collision_calibration() if model.endswith('c3') else verify.exact_volume_calibration()
    print(model, json.dumps(result), flush=True)
    assert result.get('ok', result.get('pass'))

bm = bmesh.new()
bmesh.ops.create_cube(bm, size=2)
inner = bmesh.ops.create_cube(bm, size=1)['verts']
for face in {face for vertex in inner for face in vertex.link_faces}:
    face.normal_flip()
assert abs(closed_boundary_volume(bm) - 7) < 1e-8
print('hollow_boundary_volume', closed_boundary_volume(bm), flush=True)
bm.free()

from solid_volume import triangle_area_calibration
area = triangle_area_calibration()
assert area['pass']
assert abs(area['smallPositiveTwiceAreaMm2'] - area['smallExpectedTwiceAreaMm2']) < 1e-20
print('triangle_area_calibration', json.dumps(area), flush=True)

bm = bmesh.new()
a, b, c, d = [bm.verts.new(p) for p in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))]
bm.faces.new((a, b, c))
bm.faces.new((a, d, b))
try:
    closed_boundary_volume(bm)
except ValueError:
    print('open_nonplanar_refused', True, flush=True)
else:
    raise AssertionError('Open nonplanar boundary passed')
bm.free()
