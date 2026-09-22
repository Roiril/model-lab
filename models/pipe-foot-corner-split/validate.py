"""分割板の STL を読み直し、干渉・ソケット・節の肉厚を測る。"""

import sys
import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


P = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(P))
import params as D


def clear():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def volume(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    answer = abs(bm.calc_volume()) * 1e9
    bm.free()
    return answer


def intersection(a, b):
    copy = a.copy()
    copy.data = a.data.copy()
    bpy.context.collection.objects.link(copy)
    bpy.context.view_layer.objects.active = copy
    mod = copy.modifiers.new('check', 'BOOLEAN')
    mod.operation = 'INTERSECT'
    mod.object = b
    mod.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    result = volume(copy)
    bpy.data.objects.remove(copy, do_unlink=True)
    return result


clear()
bpy.ops.mesh.primitive_cube_add(size=.01, location=(0, 0, 0))
a = bpy.context.object
bpy.ops.mesh.primitive_cube_add(size=.01, location=(.005, 0, 0))
b = bpy.context.object
assert abs(intersection(a, b) - 500) < 1e-2
b.location.x = .02
bpy.context.view_layer.update()
assert intersection(a, b) < 1e-8

clear()
parts = {}
for letter in ('a', 'b'):
    bpy.ops.wm.stl_import(filepath=str(ROOT / 'exports' / f'pipe_foot_corner_split_{letter}.stl'))
    ob = bpy.context.object
    ob.scale = (.001,) * 3
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    parts[letter] = ob

results = {'calibration': 'overlapping cubes 500mm3; separated cubes 0mm3',
           'insertion_overlap_mm3': {}}
for dz in (0, .2, 1, 4, 8, 16, 30, 44, 86):
    parts['b'].location.z = dz * .001
    bpy.context.view_layer.update()
    overlap = intersection(parts['a'], parts['b'])
    results['insertion_overlap_mm3'][str(dz)] = overlap
    assert overlap < 1e-4, (dz, overlap)
parts['b'].location.z = 0
bpy.context.view_layer.update()


def ray_hits(ob, origin, direction):
    origin = Vector(origin) * .001
    direction = Vector(direction).normalized()
    result = []
    for _ in range(16):
        yes, point, normal, index = ob.ray_cast(origin, direction, distance=1)
        if not yes:
            break
        result.append(tuple(x * 1000 for x in point))
        origin = point + direction * 1e-7
    return result


results['sockets'] = []
for name, center, owner in [('A1', D.ONE.A1, 'a'), ('A2', D.ONE.A2, 'a'),
                            ('F', D.ONE.F, 'a'), ('B1', D.ONE.B1, 'b'), ('B2', D.ONE.B2, 'b')]:
    ob = parts[owner]
    cx, cy = center
    seat = ray_hits(ob, (cx, cy, 90), (0, 0, -1))[0][2]
    radii = []
    walls = []
    for angle in range(0, 360, 15):
        dx, dy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        pts = ray_hits(ob, (cx, cy, 65), (dx, dy, 0))
        assert len(pts) >= 2, (name, angle, pts)
        r = math.dist((cx, cy), pts[0][:2])
        r2 = math.dist((cx, cy), pts[1][:2])
        radii.append(r)
        walls.append(r2 - r)
    result = dict(name=name, center_mm=center, seat_mm=seat,
                  bore_diameter_range_mm=[2 * min(radii), 2 * max(radii)],
                  wall_at_z65_mm=[min(walls), max(walls)])
    assert abs(seat - 30) < .02 and min(radii) > 14.28 and max(radii) < 14.32, result
    assert min(walls) > 3.98, result
    results['sockets'].append(result)

results['female_head_side_walls'] = []
for seg, pos, owner, kind in D.TABS:
    if kind != 'knuckle':
        continue
    p = (pos, pos) if seg == 's1' else (D.SEAM_X, pos)
    d = (2**-.5, -2**-.5) if seg == 's1' else (1, 0)
    t = (-d[1], d[0])
    hc = (p[0] + 15 * d[0], p[1] + 15 * d[1])
    measured = []
    for angle in range(-90, 91, 5):
        theta = math.radians(angle)
        direction = (d[0] * math.cos(theta) + t[0] * math.sin(theta),
                     d[1] * math.cos(theta) + t[1] * math.sin(theta), 0)
        hits = ray_hits(parts['b'], (*hc, 15), direction)
        assert len(hits) >= 2, (seg, angle, hits)
        measured.append(math.dist(hits[0], hits[1]))
    results['female_head_side_walls'].append(
        dict(seam=seg, z_mm=15, min_mm=min(measured), max_mm=max(measured)))
    assert min(measured) > 4.97, (seg, min(measured))

(ROOT / 'exports' / 'pipe-foot-corner-refined-validation.json').write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(results, ensure_ascii=False, indent=2))
