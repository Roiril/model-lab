"""STL の閉じ方・実寸・組み立て時の干渉を検査する。Blender --background で実行。"""
import sys
import json
import struct
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import numpy as np
import bpy
import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'exports'
sys.path.insert(0, str(ROOT / 'lib'))
sys.path.insert(0, str(Path(__file__).parent))
import params as C
import rail_coupling as K
J = C.J


def read_stl(path):
    data = path.read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    assert len(data) == 84 + count * 50
    dtype = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('attr', '<u2')])
    raw = np.frombuffer(data, dtype=dtype, offset=84, count=count)['v'].astype(float)
    vertices, inverse = np.unique(raw.reshape(-1, 3), axis=0, return_inverse=True)
    return vertices, inverse.reshape(-1, 3)


def metrics(v, f):
    edges = defaultdict(list)
    parent = list(range(len(v)))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for face in f:
        for a, b in zip(face, np.roll(face, -1)):
            edges[tuple(sorted((int(a), int(b))))].append(1 if a < b else -1)
            parent[root(a)] = root(b)
    p = v[f]
    area2 = np.linalg.norm(np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), axis=1)
    return dict(bbox_mm=np.ptp(v, axis=0).tolist(),
                volume_mm3=float(np.einsum('ij,ij->i', p[:, 0], np.cross(p[:, 1], p[:, 2])).sum() / 6),
                components=len({root(i) for i in range(len(v))}),
                bad_edges=sum(len(x) != 2 or sum(x) != 0 for x in edges.values()),
                degenerate_triangles=int((area2 < 1e-9).sum()),
                duplicate_triangles=len(f) - len({tuple(sorted(x)) for x in f}))


def projected_pole_gap(v, f, center, radius):
    """鉛直ポールに対する保守的な水平隙間。全三角形の辺までの距離を測る。"""
    p = v[f][:, :, :2]
    a = p.reshape(-1, 2)
    b = np.roll(p, -1, axis=1).reshape(-1, 2)
    d = b - a
    denom = (d * d).sum(axis=1)
    t = np.clip(((np.array(center) - a) * d).sum(axis=1) / np.maximum(denom, 1e-20), 0, 1)
    return float(np.linalg.norm(a + d*t[:, None] - center, axis=1).min() - radius)


def mesh(name, v, f):
    me = bpy.data.meshes.new(name)
    me.from_pydata((v * .001).tolist(), [], f.tolist())
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def volume(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    result = abs(bm.calc_volume()) * 1e9
    bm.free()
    return result


def intersection(a, b):
    ob = a.copy()
    ob.data = a.data.copy()
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active = ob
    mod = ob.modifiers.new('interference', 'BOOLEAN')
    mod.operation = 'INTERSECT'
    mod.solver = 'EXACT'
    mod.object = b
    bpy.ops.object.modifier_apply(modifier=mod.name)
    result = volume(ob)
    bpy.data.objects.remove(ob, do_unlink=True)
    return result


def hit(ob, origin, direction):
    yes, p, normal, index = ob.ray_cast(Vector(origin) * .001, Vector(direction), distance=2)
    assert yes, (ob.name, origin, direction)
    return np.array(p) * 1000


def penetration(a, b, tolerance_mm=.001):
    """最近傍法線で候補を絞り、3方向の交差回数で内外を判定する。"""
    b.data.calc_loop_triangles()
    bv = [b.matrix_world @ v.co for v in b.data.vertices]
    bounds = [(min(v[i] for v in bv), max(v[i] for v in bv)) for i in range(3)]
    tree = BVHTree.FromPolygons(bv, [list(t.vertices) for t in b.data.loop_triangles], all_triangles=True)
    a.data.calc_loop_triangles()
    av = [a.matrix_world @ v.co for v in a.data.vertices]
    probes = av + [sum((av[i] for i in t.vertices), Vector()) / 3 for t in a.data.loop_triangles]
    count, deepest, examples = 0, 0.0, []
    directions = [Vector(v).normalized() for v in ((.913, .377, .157), (-.271, .851, .449), (.417, -.287, .863))]
    for p in probes:
        if any(p[i] < lo - 1e-8 or p[i] > hi + 1e-8 for i, (lo, hi) in enumerate(bounds)):
            continue
        q, normal, index, distance = tree.find_nearest(p)
        signed = (p - q).dot(normal) * 1000
        if signed < -tolerance_mm:
            votes = 0
            for d in directions:
                start, hits = p.copy(), 0
                for _ in range(80):
                    location, n, idx, dist = tree.ray_cast(start, d)
                    if location is None:
                        break
                    hits += 1
                    start = location + d * 1e-8
                votes += hits % 2
            if votes >= 2:
                count += 1
                deepest = max(deepest, -signed)
                if len(examples) < 3:
                    examples.append([round(x * 1000, 6) for x in p])
    return {'samples': len(probes), 'inside_samples': count, 'max_depth_mm': deepest, 'examples': examples}


def main():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    tv = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], float)
    tf = np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]])
    assert metrics(tv, tf)['bad_edges'] == 0
    assert metrics(tv, tf[:-1])['bad_edges'] == 3
    bpy.ops.mesh.primitive_cube_add(size=.01)
    a = bpy.context.object
    bpy.ops.mesh.primitive_cube_add(size=.01, location=(.005, 0, 0))
    b = bpy.context.object
    assert abs(intersection(a, b) - 500) < .01
    b.location.x = .02
    bpy.context.view_layer.update()
    assert intersection(a, b) < 1e-6
    b.location.x = .005
    bpy.context.view_layer.update()
    assert penetration(a, b)['inside_samples'] > 0
    b.location.x = .02
    bpy.context.view_layer.update()
    assert penetration(a, b)['inside_samples'] == 0
    for ob in (a, b):
        bpy.data.objects.remove(ob, do_unlink=True)

    results = {'calibration': 'closed/open tetrahedra; intersecting/separate cubes', 'meshes': {}}
    obs = {}
    for name in ('pipe_joint_28', 'pipe_corner_in_28', 'pipe_corner_out_28'):
        v, f = read_stl(OUT / (name + '.stl'))
        m = metrics(v, f)
        results['meshes'][name] = m
        assert m['components'] == 1 and m['volume_mm3'] > 0, (name, m)
        assert not any(m[k] for k in ('bad_edges', 'degenerate_triangles', 'duplicate_triangles')), (name, m)
        obs[name] = mesh(name, v, f)
        if name == 'pipe_corner_out_28':
            # 中央ポールは世界(-154.7,-154.7)、カーブの座標では(105,105)。
            pole = C.R_INNER + J.SIDE_Y
            gap = projected_pole_gap(v, f, (pole, pole), J.PIPE_OD / 2)
            assert gap >= 22.0, gap
            assert abs(v[:, 2].min() + C.Z_BASE) < .0001
            tri = v[f]
            on_bed = np.max(np.abs(tri[:, :, 2] + C.Z_BASE), axis=1) < .0001
            area = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1)
            flat_width = (hit(obs[name], (-15, C.R_OUTER, -C.Z_BASE+.0001), (0, 1, 0))[1]
                          - hit(obs[name], (-15, C.R_OUTER, -C.Z_BASE+.0001), (0, -1, 0))[1])
            assert 19.8 < flat_width < 20.1, flat_width
            results['outer_clearance_and_bed'] = {'pole_horizontal_gap_mm': gap,
                  'flat_width_mm': float(flat_width), 'flat_contact_area_mm2': float(area[on_bed].sum()/2),
                  'bottom_slope_deg': C.OUTER_BOTTOM_SLOPE, 'bulge_mm': C.OUTER_BULGE}

    joint = obs['pipe_joint_28']
    measurements = []
    for y, z in ((0, 0), (80, 62.3), (-80, 62.3)):
        lo = hit(joint, (0, y, z), (0, -1, 0))[1]
        hi = hit(joint, (0, y, z), (0, 1, 0))[1]
        assert abs(hi - lo - 28.6) < .002
        measurements.append({'rail_y': y, 'diameter_mm': hi - lo})
    for y in (-80, 80):
        seat = hit(joint, (-7.3, y, 0), (0, 0, 1))[2]
        low = hit(joint, (-7.3, y, 32), (0, -1, 0))[1]
        high = hit(joint, (-7.3, y, 32), (0, 1, 0))[1]
        assert abs(seat - 39) < .002 and abs(high - low - 28.9) < .002
        measurements.append({'leg_y': y, 'seat_z': seat, 'diameter_mm': high - low})
    results['joint_measurements'] = measurements
    results['corner_measurements'] = []
    for name, radius, straight in (('pipe_corner_in_28', C.R_INNER, C.STRAIGHT_INNER),
                                    ('pipe_corner_out_28', C.R_OUTER, C.STRAIGHT_OUTER)):
        ob = obs[name]
        for along in (3, 15, 25):
            x = -straight + along
            lo = hit(ob, (x, radius, 0), (0, -1, 0))[1]
            hi = hit(ob, (x, radius, 0), (0, 1, 0))[1]
            assert abs(hi - lo - 28.6) < .03, (name, along, lo, hi)
            results['corner_measurements'].append({'name': name, 'distance_from_mouth': along,
                                                   'diameter_mm': hi - lo})
    results['fixed_dimensions'] = {'joint_length': J.BODY_T, 'leg_x': J.LEG_X,
                                  'side_y': J.SIDE_Y, 'side_z': J.SIDE_Z,
                                  'corner_off': C.CORNER_OFF, 'inner_radius': C.R_INNER,
                                  'outer_endpoint_offset': C.R_OUTER, 'outer_reveal': C.REVEAL}
    assert np.allclose([J.BODY_T, J.LEG_X, J.SIDE_Y, J.SIDE_Z, C.CORNER_OFF], [54, -7.3, 80, 62.3, 74.7])

    # 組み立て位置を実際の頂点へ適用して、両方のM字との干渉を測る。
    ma = joint.copy()
    ma.data = joint.data.copy()
    bpy.context.collection.objects.link(ma)
    mc = C.CORNER_OFF + J.SIDE_Y
    joint.matrix_world = Matrix.Translation(Vector((-J.LEG_X, -mc, 0)) * .001)
    ma.matrix_world = Matrix(((0, -1, 0, -mc * .001), (1, 0, 0, -J.LEG_X * .001), (0, 0, 1, 0), (0, 0, 0, 1)))
    arc = -(C.CORNER_OFF - C.R_INNER)
    results['assembly_penetration'] = {}
    for name in ('pipe_corner_in_28', 'pipe_corner_out_28'):
        ob = obs[name]
        ob.matrix_world = Matrix(((-1, 0, 0, arc * .001), (0, -1, 0, arc * .001), (0, 0, 1, J.SIDE_Z * .001), (0, 0, 0, 1)))
        bpy.context.view_layer.update()
        checks = [penetration(ob, x) for x in (joint, ma)] + [penetration(x, ob) for x in (joint, ma)]
        results['assembly_penetration'][name] = checks
        assert all(c['inside_samples'] == 0 for c in checks), (name, checks)
    # 実部品も故意に2mm食い込ませ、検査が止められることを確認。
    ob = obs['pipe_corner_in_28']
    ob.location.x += .002
    bpy.context.view_layer.update()
    assert penetration(ob, joint)['inside_samples'] > 0
    ob.location.x -= .002
    results['contact_test_note'] = 'Surface samples, tolerance 0.001mm; displaced real part fails. Coplanar Boolean intersection is unreliable.'
    results['key_clearance_mm_per_side'] = K.CLEAR
    results['key_engagement_mm'] = {'inner': K.INNER_L, 'outer': K.OUTER_L - C.REVEAL}
    results['receiver_inner_wall_mm'] = K.INNER_R - K.CLEAR - J.BORE_D / 2
    results['print_files'] = {}
    assert (OUT / 'pipe-corner-outer-roomy.3mf').read_bytes() == (OUT / 'pipe-corner-outer-refined.3mf').read_bytes()
    ns = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
    for filename, stl in (('pipe-joint-refined.3mf', 'pipe_joint_28_print'),
                          ('pipe-corner-inner-refined.3mf', 'pipe_corner_in_28'),
                          ('pipe-corner-outer-refined.3mf', 'pipe_corner_out_28')):
        with zipfile.ZipFile(OUT / filename) as zf:
            root = ET.fromstring(zf.read('3D/3dmodel.model'))
        assert root.get('unit') == 'millimeter'
        data = root.find(ns+'resources/'+ns+'object/'+ns+'mesh')
        vertices = np.array([[float(e.get(k)) for k in ('x', 'y', 'z')] for e in data.find(ns+'vertices')])
        faces = np.array([[int(e.get(k)) for k in ('v1', 'v2', 'v3')] for e in data.find(ns+'triangles')])
        actual, actual_faces = read_stl(OUT / (stl + '.stl'))
        tree = KDTree(len(actual))
        for i, v in enumerate(actual):
            tree.insert(v, i)
        tree.balance()
        error = max(tree.find(v)[2] for v in vertices)
        assert error < .0001 and len(faces) == len(actual_faces), (filename, error)
        m = metrics(vertices, faces)
        assert m['bad_edges'] == 0 and m['degenerate_triangles'] == 0, (filename, m)
        transform = np.array([float(x) for x in root.find(ns+'build/'+ns+'item').get('transform').split()]).reshape(4, 3)
        placed = vertices @ transform[:3] + transform[3]
        assert abs(placed[:, 2].min()) < .0001
        assert placed[:, :2].min() >= 0 and placed[:, :2].max() <= 256
        results['print_files'][filename] = {'stl_max_vertex_difference_mm': error, 'bbox_mm': m['bbox_mm']}
    encoded = json.dumps(results, ensure_ascii=False, indent=2, default=lambda x: x.item())
    (OUT / 'pipe-handrail-validation.json').write_text(encoded, encoding='utf-8')
    print(encoded)


if __name__ == '__main__':
    main()
