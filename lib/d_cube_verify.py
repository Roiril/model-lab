"""Dの生STLを読む。校正したEXACT交差で全開閉を2.5度以下刻みで測る。"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json
import hashlib
import math
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(MODEL_HERE)
ROOT = HERE.parents[1]
BUILD = HERE / 'build'
sys.path.insert(0, str(ROOT / 'lib'))
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding='utf-8')
import params as P
import linkage as K
from printmech.mesh import Mesh, clearance
from printmech.geometry import volume

PARTS = ('box', 'lid', 'roof', 'crank', 'link', 'pin', 'clip', 'speaker_clip')
REFS = ('ref_body', 'ref_horn', 'ref_wire', 'ref_speaker')
TOL = 0.0001  # STL境界の丸め残差。実干渉を許容する設計値ではない。
COMPONENTS = {}


def topology(raw):
    n = struct.unpack_from('<I', raw, 80)[0]
    assert len(raw) == 84 + 50 * n
    edges, directed, faces = Counter(), Counter(), Counter()
    degenerate = 0
    for i in range(n):
        xyz = struct.unpack_from('<12f', raw, 84 + i * 50)[3:]
        p = [tuple(xyz[j:j + 3]) for j in (0, 3, 6)]
        degenerate += len(set(p)) < 3
        faces[tuple(sorted(p))] += 1
        for a, b in zip(p, p[1:] + p[:1]):
            edges[tuple(sorted((a, b)))] += 1
            directed[(a, b)] += 1
    out = dict(triangles=n, nonmanifold_edges=sum(v != 2 for v in edges.values()),
               winding_mismatches=sum(directed[b, a] != v for (a, b), v in directed.items()),
               duplicate_faces=sum(v - 1 for v in faces.values()), degenerate_faces=degenerate)
    out['ok'] = not any(out[k] for k in out if k != 'triangles')
    return out


def fixture_bytes(faces):
    raw = bytearray(b'D cube calibration'.ljust(80, bytes(1)))
    raw += struct.pack('<I', len(faces))
    for face in faces:
        raw += struct.pack('<12fH', 0, 0, 0, *[x for point in face for x in point], 0)
    return raw


def cube_mesh(lo, hi, name):
    verts = [Vector((x, y, z)) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    faces = [(0, 2, 3), (0, 3, 1), (4, 5, 7), (4, 7, 6), (0, 1, 5), (0, 5, 4),
             (2, 6, 7), (2, 7, 3), (0, 4, 6), (0, 6, 2), (1, 3, 7), (1, 7, 5)]
    return Mesh(verts, faces, name)


def intersection(a, b):
    alo, ahi = a.bounds()
    blo, bhi = b.bounds()
    if any(ahi[i] <= blo[i] or bhi[i] <= alo[i] for i in range(3)):
        return 0.0
    for mesh in (a, b):
        if not hasattr(mesh, '_cached_bvh'):
            mesh._cached_bvh = mesh.bvh()
        key = id(mesh.t)
        if key not in COMPONENTS:
            neighbors = [set() for _ in mesh.v]
            for face in mesh.t:
                for i in face:
                    neighbors[i].update(face)
            left = set(range(len(mesh.v)))
            representatives = []
            while left:
                point = left.pop()
                representatives.append(point)
                pending = [point]
                while pending:
                    at = pending.pop()
                    found = neighbors[at] & left
                    left.difference_update(found)
                    pending.extend(found)
            COMPONENTS[key] = (mesh.t, representatives)
    if not a._cached_bvh.overlap(b._cached_bvh):
        if not any(other.contains(mesh.v[i], other._cached_bvh)
                   for mesh, other in ((a, b), (b, a)) for i in COMPONENTS[id(mesh.t)][1]):
            return 0.0
    objects = []
    for mesh in (a, b):
        data = bpy.data.meshes.new('check')
        data.from_pydata(mesh.v, [], mesh.t)
        data.update()
        ob = bpy.data.objects.new('check', data)
        bpy.context.collection.objects.link(ob)
        objects.append(ob)
    left, right = objects
    bpy.context.view_layer.objects.active = left
    mod = left.modifiers.new('intersection', 'BOOLEAN')
    mod.operation = 'INTERSECT'
    mod.solver = 'EXACT'
    mod.object = right
    bpy.ops.object.modifier_apply(modifier=mod.name)
    result = abs(volume(left))
    for ob in objects:
        mesh = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.meshes.remove(mesh)
    return result


def rot(deg, yz):
    return Matrix.Translation((0, *yz)) @ Matrix.Rotation(math.radians(deg), 4, 'X') @ Matrix.Translation((0, -yz[0], -yz[1]))


def pose(parts, theta):
    alpha = K.sweep(theta, max(2, math.ceil(theta * 2)))[-1][1]
    a0, b0 = K.pin_a(K.ALPHA0), K.pin_b(0)
    a1, b1 = K.pin_a(alpha), K.pin_b(theta)
    delta = K.link_angle(theta, alpha) - K.link_angle(0, K.ALPHA0)
    lm = Matrix.Translation((0, a1[0] - a0[0], a1[1] - a0[1])) @ rot(delta, a0)
    out = dict(parts)
    for name, mat in (('lid', rot(theta, K.H)), ('crank', rot(alpha - K.ALPHA0, K.O)),
                      ('ref_horn', rot(alpha - K.ALPHA0, K.O)), ('link', lm)):
        out[name] = parts[name].moved(mat)
    return out


def external_faces(parts):
    """1mm格子で6面を外から検査。継ぎ目は記録して別扱いする。"""
    side = P.CUBE * 1000
    half = side / 2
    split = side - P.LID_T * 1000
    tops = []
    for name in ('lid', 'roof'):
        ys = [v.y for v in parts[name].v if abs(v.z - side) < 0.01]
        tops.append(min(ys) if name == 'lid' else max(ys))
    seam_min, seam_max = min(tops), max(tops)
    trees = [parts[name].bvh() for name in ('box', 'lid', 'roof')]
    failures, checked, seams, failed = [], 0, 0, 0
    for axis in range(3):
        others = [i for i in range(3) if i != axis]
        for sign in (-1, 1):
            for i in range(int(side)):
                for j in range(int(side)):
                    p = Vector((0, 0, 0))
                    p[axis] = (0 if sign < 0 else side) if axis == 2 else sign * half
                    for k, index in enumerate(others):
                        p[index] = ((i, j)[k] + 0.5) - (0 if index == 2 else half)
                    side_seam = False
                    if axis == 0 and split <= p.z <= side:
                        dz = p.z - P.HINGE_Z * 1000
                        ends = [P.HINGE_Y * 1000 + math.sqrt(max(0, (radius * 1000) ** 2 - dz ** 2))
                                for radius in (P.ROOF_SEAM_R, P.LID_SEAM_R)]
                        side_seam = min(ends) - .01 <= p.y <= max(ends) + .01
                    if (axis == 2 and sign > 0 and seam_min - 0.01 <= p.y <= seam_max + 0.01) or side_seam:
                        seams += 1
                        continue
                    start = p.copy()
                    start[axis] += sign * 2
                    direction = Vector((0, 0, 0))
                    direction[axis] = -sign
                    distances = [hit[3] for tree in trees if (hit := tree.ray_cast(start, direction, 5))[0] is not None]
                    checked += 1
                    if not distances or abs(min(distances) - 2) > 0.015:
                        failed += 1
                        if len(failures) < 100:
                            failures.append([axis, sign, *p, min(distances) if distances else None])
    vertices = [v for name in PARTS for v in parts[name].v]
    lo = [min(v[i] for v in vertices) for i in range(3)]
    hi = [max(v[i] for v in vertices) for i in range(3)]
    sizes = [round(hi[i] - lo[i], 4) for i in range(3)]
    return dict(ok=not failures and all(abs(s - side) < .02 for s in sizes),
                bbox_mm=[lo, hi], size_mm=sizes, checked=checked, passed=checked - failed,
                seam_samples=seams, top_seam_y_mm=[seam_min, seam_max], failures=failures,
                note='1mm格子の面確認。継ぎ目は除外。STLの多様体検査を併用。')


def motion(parts):
    moving = {'lid', 'crank', 'link', 'ref_horn'}
    names = list(PARTS + REFS)
    pairs = [(a, b) for a, b in combinations(names, 2)
             if (a in moving or b in moving) and {a, b} != {'ref_body', 'ref_horn'}]
    count = math.ceil(P.LID_OPEN_DEG / 2.5)
    worst, failures, measured = {}, [], 0
    hardware_mating = dict(
        pair=['ref_body', 'ref_horn'], status='excluded_manufactured_mating',
        reason='既製サーボ軸と付属ホーンの嵌合は設計対象外。参照STLのEXACT交差は順序で異なる値になった。印刷部品との交差にはこの除外を適用しない。',
        sha256={name: hashlib.sha256((BUILD / (name + '.stl')).read_bytes()).hexdigest()
                for name in ('ref_body', 'ref_horn')},
        diagnostic_mm3=[intersection(parts['ref_body'], parts['ref_horn']),
                        intersection(parts['ref_horn'], parts['ref_body'])])
    gap = {'lid-roof': float('inf'), 'link-lid': float('inf'), 'link-crank': float('inf')}
    for t in range(count + 1):
        theta = P.LID_OPEN_DEG * t / count
        posed = pose(parts, theta)
        for a, b in pairs:
            val = intersection(posed[a], posed[b])
            measured += 1
            label = a + '-' + b
            if label not in worst or val > worst[label]['volume_mm3']:
                worst[label] = dict(theta=theta, volume_mm3=val)
            if val > TOL:
                row = dict(pair=label, theta=theta, volume_mm3=val)
                failures.append(row)
        for label in gap:
            a, b = label.split('-')
            gap[label] = min(gap[label], clearance(posed[a], posed[b]))
        print(f'{P.MODEL_ID} motion {theta:.1f}: failures={len(failures)} {failures[-2:]}', flush=True)
    return dict(ok=not failures, samples=count + 1, step_deg=P.LID_OPEN_DEG / count,
                intersection_tests=measured, tolerance_mm3=TOL, worst=worst,
                min_clearance_mm=gap, failures=failures, hardware_mating=hardware_mating,
                hardware_mating_note='SG92Rの正本は歯形を再現していない。既製品同士の嵌合の成功は判定しない。')


def assembly(parts):
    from d_cube_assembly import run
    return run(parts, P, K, intersection, pose)


def finish(report):
    report['ok'] = all(row['ok'] for row in report['topology'].values()) and report['exterior']['ok'] and report['motion']['ok'] and report['assembly']['ok']
    (BUILD / 'verify_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key not in ('mass', 'motion')}, ensure_ascii=False))
    assert report['ok'], 'D cube verification failed; see verify_report.json'


def main():
    parts = {name: Mesh.load(str(BUILD / (name + '.stl')), name) for name in PARTS + REFS}
    fingerprints = {name: hashlib.sha256((BUILD / (name + '.stl')).read_bytes()).hexdigest() for name in PARTS + REFS}
    if '--assembly-only' in sys.argv:
        report = json.loads((BUILD / 'verify_report.json').read_text(encoding='utf-8'))
        assert report['input_sha256'] == fingerprints, 'STLs changed; a complete verification is required'
        report['assembly'] = assembly(parts)
        finish(report)
        return
    a, b, c, d = (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)
    tetra = [(a, c, b), (a, b, d), (a, d, c), (b, c, d)]
    closed, opened = topology(fixture_bytes(tetra)), topology(fixture_bytes(tetra[:-1]))
    unit = cube_mesh((0, 0, 0), (2, 2, 2), 'unit')
    overlap = intersection(unit, cube_mesh((1, 1, 1), (3, 3, 3), 'overlap'))
    separated = intersection(unit, cube_mesh((4, 4, 4), (6, 6, 6), 'separated'))
    contained = intersection(unit, cube_mesh((.5, .5, .5), (1.5, 1.5, 1.5), 'contained'))
    calibration = dict(closed=closed, open=opened, overlap_mm3=overlap, separated_mm3=separated,
                       contained_mm3=contained,
                       ok=closed['ok'] and opened['nonmanifold_edges'] == 3 and abs(overlap - 1) < 1e-5 and separated == 0 and abs(contained - 1) < 1e-5)
    assert calibration['ok'], calibration
    topo = {name: topology((BUILD / ('print_' + name + '.stl')).read_bytes()) for name in PARTS}
    masses = {}
    for name in PARTS + REFS:
        props = parts[name].mass_props()
        masses[name] = dict(volume_mm3=props['volume'], mass_g=props['volume'] * P.PLA_DENSITY * 1e-6,
                            com_mm=list(props['com']), ixx_com_mm5=props['ixx_com'])
    half, height = P.CUBE * 500, P.CUBE * 1000
    closed_cube = cube_mesh((-half, -half, 0), (half, half, height), 'closed_cube')
    broken_cube = Mesh(closed_cube.v, [face for i, face in enumerate(closed_cube.t) if i not in (6, 7)], 'missing_front')
    face_pass = external_faces({**parts, 'box': closed_cube})
    face_fail = external_faces({**parts, 'box': broken_cube})
    calibration['exterior'] = dict(closed_ok=face_pass['ok'], missing_face_ok=face_fail['ok'],
                                   missing_face_detected=face_fail['checked']-face_fail['passed'])
    calibration['ok'] &= face_pass['ok'] and not face_fail['ok']
    assert calibration['ok'], calibration
    report = dict(calibration=calibration, topology=topo, mass=masses, exterior=external_faces(parts),
                  input_sha256=fingerprints)
    (BUILD / 'verify_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    report['motion'] = motion(parts)
    report['assembly'] = assembly(parts)
    finish(report)


if __name__ == '__main__':
    main()
