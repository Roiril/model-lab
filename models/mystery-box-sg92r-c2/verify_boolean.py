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
from printmech.stl import write_binary_stl


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
         for n in ('box', 'lid', 'crank', 'link', 'ref_horn', 'roof')}
moving, alpha = V.pose(parts, V.K.THETA_OPEN / 2)
link = V.bent_link(moving['link'], V.K.pin_a(alpha), V.K.pin_b(V.K.THETA_OPEN / 2), 3.4)
for i in range(11):
    frame = V.bent_link(moving['link'], V.K.pin_a(alpha), V.K.pin_b(V.K.THETA_OPEN / 2), 3.4 * (1 - i / 10))
    write_binary_stl(str(HERE / 'build' / f'link_bend_{i}.stl'), [(frame.v[a], frame.v[b], frame.v[c]) for a, b, c in frame.t])
out = {'closed_lid_box_mm3': intersection(parts['lid'], parts['box']),
       'bent_link_crank_mm3': intersection(link, moving['crank']),
       'calibration_hit_mm3': intersection(parts['link'].moved(V.Matrix.Translation((1, 0, 0))), parts['lid']),
       'calibration_clear_mm3': intersection(parts['link'].moved(V.Matrix.Translation((50, 0, 0))), parts['lid'])}
out['roof_box_mm3']=intersection(parts['roof'],parts['box'])
out['lid_roof_motion_mm3']={}
for theta in (0,16.25,32.5,48.75,65):
    lid=parts['lid'].moved(V.rot_x(theta,*V.K.H))
    out['lid_roof_motion_mm3'][str(theta)]=intersection(lid,parts['roof'])
out['volume_tolerance_mm3'] = 0.0001  # STLを0.0001mmで丸めた接触境界の残差を許容する。
out['ok'] = out['calibration_hit_mm3'] > 0.1 and out['calibration_clear_mm3'] < 1e-5 and out['closed_lid_box_mm3'] < out['volume_tolerance_mm3'] and out['bent_link_crank_mm3'] < out['volume_tolerance_mm3']
out['ok'] = out['ok'] and out['roof_box_mm3'] < out['volume_tolerance_mm3'] and all(value < out['volume_tolerance_mm3'] for value in out['lid_roof_motion_mm3'].values())
(HERE / 'build' / 'boolean_report.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(json.dumps(out))
assert out['ok'], out
