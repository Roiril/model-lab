"""接触として分類した面をBoolean EXACTでも確認する。"""
from pathlib import Path
import json
import sys
import bpy
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'lib'))
import verify as V
from printmech.geometry import volume


def object_from(mesh):
    data = bpy.data.meshes.new(mesh.name)
    data.from_pydata(mesh.v, [], mesh.t)
    data.update()
    obj = bpy.data.objects.new(mesh.name, data)
    bpy.context.collection.objects.link(obj)
    return obj


def intersection(a, b):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    left, right = object_from(a), object_from(b)
    bpy.context.view_layer.objects.active = left
    mod = left.modifiers.new('intersection', 'BOOLEAN')
    mod.operation = 'INTERSECT'
    mod.solver = 'EXACT'
    mod.object = right
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return abs(volume(left))


parts = {n: V.Mesh.load(str(HERE / 'build' / (n + '.stl')), n)
         for n in ('box', 'lid', 'crank', 'link', 'ref_horn')}
setup_theta = V.P.ASSEMBLY_LID_BACK_DEG
setup, setup_alpha = V.pose(parts, setup_theta)
pb = V.K.pin_b(setup_theta)
link_deg = V.K.link_angle(setup_theta, setup_alpha)
key_deg = setup_theta + V.P.B_KEY_DEG - 180.0
link_at_key = setup['link'].moved(V.rot_x(key_deg - link_deg, pb[0], pb[1]))
pulls = [i * 0.5 for i in range(16)]
b_clear = {}
for theta in (0.0, V.K.THETA_OPEN / 2, V.K.THETA_OPEN):
    moving, _ = V.pose(parts, theta)
    b_clear[str(theta)] = intersection(moving['link'], moving['lid'])
moving_mid, _ = V.pose(parts, V.K.THETA_OPEN / 2)
b_pull_hit = {str(pull): intersection(
    moving_mid['link'].moved(V.Matrix.Translation((-pull, 0, 0))), moving_mid['lid']) for pull in pulls}
b_key_clear = {str(pull): intersection(
    link_at_key.moved(V.Matrix.Translation((-pull, 0, 0))), setup['lid']) for pull in pulls}
out = {'closed_lid_box_mm3': intersection(parts['lid'], parts['box']),
       'Bclear_operating_mm3': b_clear,
       'Bpullhit_mm3': b_pull_hit,
       'Bkeyclear_mm3': b_key_clear,
       'calibration_hit_mm3': intersection(parts['link'].moved(V.Matrix.Translation((1, 0, 0))), parts['lid']),
       'calibration_clear_mm3': intersection(parts['link'].moved(V.Matrix.Translation((50, 0, 0))), parts['lid'])}
out['volume_tolerance_mm3'] = 0.0001  # STLを0.0001mmで丸めた接触境界の残差を許容する。
out['ok'] = (out['calibration_hit_mm3'] > 0.1
             and out['calibration_clear_mm3'] < 1e-5
             and out['closed_lid_box_mm3'] < out['volume_tolerance_mm3']
             and all(value < out['volume_tolerance_mm3'] for value in b_clear.values())
             and max(b_pull_hit.values()) > 0.01
             and all(value < out['volume_tolerance_mm3'] for value in b_key_clear.values()))
(HERE / 'build' / 'boolean_report.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(json.dumps(out))
assert out['ok'], out
