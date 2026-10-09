"""閉じた箱、開いた箱、全部品を同じ寸法で目視確認する。"""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'lib'))
import params as P
import linkage as K
from printmech.geometry import transform, rot_x_about

PARTS = ['box', 'lid', 'crank', 'link', 'pin', 'clip', 'speaker_clip', 'ref_body', 'ref_horn', 'ref_wire', 'ref_speaker']
COLORS = [(0.63, 0.60, 0.56, 1), (0.25, 0.65, 0.87, 1), (0.89, 0.61, 0.12, 1),
          (0.08, 0.61, 0.42, 1), (0.18, 0.18, 0.18, 1), (0.78, 0.47, 0.65, 1),
          (0.82, 0.31, 0.12, 1), (0.06, 0.32, 0.60, 1), (0.18, 0.18, 0.18, 1),
          (0.84, 0.30, 0.05, 1), (0.81, 0.75, 0.20, 1)]


def load(name, printed=False):
    path = HERE / 'build' / (('print_' if printed else '') + name + '.stl')
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    ob = (set(bpy.data.objects) - before).pop()
    ob.color = COLORS[PARTS.index(name)]
    return ob


def render(label, theta=0, bed=False):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    obs = []
    names = PARTS[:7] if bed else PARTS
    for i, name in enumerate(names):
        ob = load(name, printed=bed)
        if bed:
            ob.location = ((i % 3) * 82 - 82, (i // 3) * 82, 0)
        elif theta:
            a = K.sweep(theta)[-1][1]
            if name == 'lid':
                transform(ob, rot_x_about(theta, *K.H))
            elif name in ('crank', 'ref_horn'):
                transform(ob, rot_x_about(a - K.ALPHA0, *K.O))
            elif name == 'link':
                from mathutils import Matrix
                pa0, pb0 = K.pin_a(K.ALPHA0), K.pin_b(0)
                pa1, pb1 = K.pin_a(a), K.pin_b(theta)
                da = K.link_angle(theta, a) - K.link_angle(0, K.ALPHA0)
                transform(ob, Matrix.Translation((0, pa1[0] - pa0[0], pa1[1] - pa0[1])) @ rot_x_about(da, *pa0))
        obs.append(ob)
    bpy.context.view_layer.update()
    points = [ob.matrix_world @ v.co for ob in obs for v in ob.data.vertices]
    lo = Vector(tuple(min(v[j] for v in points) for j in range(3)))
    hi = Vector(tuple(max(v[j] for v in points) for j in range(3)))
    center = (lo + hi) / 2
    bpy.ops.object.camera_add(location=center + Vector((1.4, 1.7, 1.4)).normalized() * 280)
    cam = bpy.context.object
    cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.type = 'ORTHO'
    basis = cam.rotation_euler.to_matrix().transposed()
    projected = [basis @ (p - center) for p in points]
    width = max(p.x for p in projected) - min(p.x for p in projected)
    height = max(p.y for p in projected) - min(p.y for p in projected)
    offset = Vector(((max(p.x for p in projected) + min(p.x for p in projected)) / 2,
                     (max(p.y for p in projected) + min(p.y for p in projected)) / 2, 0))
    cam.location += basis.transposed() @ offset
    cam.data.ortho_scale = max(width, height * 1000 / 860) * 1.18
    cam.data.clip_end = 1000
    scene = bpy.context.scene
    scene.camera = cam
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'OBJECT'
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.background_type = 'WORLD'
    scene.world.color = (0.93, 0.93, 0.93)
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 860
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(HERE / 'build' / (label + '.png'))
    bpy.ops.render.render(write_still=True)
    print(label, 'bbox', list(lo), list(hi))


render('closed')
render('open', P.LID_OPEN_DEG)
render('parts', bed=True)
