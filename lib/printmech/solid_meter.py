"""2 立体の共通体積と、動かしたときの初接触。Blender の Python で動く（mm 単位）。

models/tangible-pixel-cube/verify.py の Solid / Meter / first_contact を、モデルに依存しない形で切り出したもの。
tangible 側は監査が算法の SHA を記録しているので、元のファイルは書き換えずに残してある。

- 主計器は Blender Boolean の MANIFOLD による共通体積。境界は lib/solid_volume.py で倍精度に積分する
- 表面が交わらず入れ子でもない組は共通体積 0 と数学的に決まるので Boolean を省く。省略と Boolean の一致は校正で測る
- 体積の床 VOLUME_FLOOR_MM3 はハーネスの定数。モデル側で広げない
"""
from __future__ import annotations

import math
import struct
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from solid_volume import closed_boundary_volume  # noqa: E402

VOLUME_FLOOR_MM3 = 0.001


def read_stl(path):
    """binary STL を (n, 3, 3) の倍精度配列で返す。値は float32 のまま丸めない"""
    raw = Path(path).read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + 50 * count:
        raise ValueError(f"binary STL のバイト数が合わない: {path}")
    dtype = np.dtype([("normal", "<f4", 3), ("vertex", "<f4", (3, 3)), ("attr", "<u2")])
    return np.frombuffer(raw, dtype=dtype, offset=84, count=count)["vertex"].astype(float)


def translation(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def rotation(axis, angle_deg, pivot=(0.0, 0.0, 0.0)):
    """pivot を通る axis まわりに angle_deg 回す 4x4"""
    u = np.asarray(axis, dtype=float)
    u = u / np.linalg.norm(u)
    a = math.radians(angle_deg)
    k = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    r = np.eye(3) + math.sin(a) * k + (1 - math.cos(a)) * (k @ k)
    m = np.eye(4)
    m[:3, :3] = r
    p = np.asarray(pivot, dtype=float)
    m[:3, 3] = p - r @ p
    return m


class Solid:
    """閉じた三角形メッシュ（mm）。頂点は float32 の値そのままで共有化する"""

    def __init__(self, name, tris):
        self.name = name
        tris = np.asarray(tris, dtype=float)
        self.tris = tris
        flat = tris.reshape(-1, 3)
        self.verts, inverse = np.unique(flat, axis=0, return_inverse=True)
        self.faces = inverse.reshape(-1, 3)
        self.lo = self.verts.min(axis=0)
        self.hi = self.verts.max(axis=0)
        self.radius = float(np.linalg.norm(self.hi - self.lo) / 2.0)

    @staticmethod
    def load(name, path):
        return Solid(name, read_stl(path))

    def posed(self, matrix):
        return self.verts @ matrix[:3, :3].T + matrix[:3, 3]

    def posed_bounds(self, matrix):
        corners = np.array([[x, y, z] for x in (self.lo[0], self.hi[0])
                            for y in (self.lo[1], self.hi[1]) for z in (self.lo[2], self.hi[2])])
        world = corners @ matrix[:3, :3].T + matrix[:3, 3]
        return world.min(axis=0), world.max(axis=0)


def box_solid(name, lower, upper):
    x0, y0, z0 = lower
    x1, y1, z1 = upper
    verts = np.array([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                      (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], dtype=float)
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
             (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return Solid(name, verts[np.array(faces)])


def cube_solid(name, center, size):
    h = size / 2.0
    return box_solid(name, [c - h for c in center], [c + h for c in center])


def _component_bounds(bm):
    remaining = set(bm.verts)
    rows = []
    while remaining:
        seed = remaining.pop()
        stack, component = [seed], [seed]
        while stack:
            vertex = stack.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in remaining:
                    remaining.remove(other)
                    stack.append(other)
                    component.append(other)
        rows.append([[min(v.co[a] for v in component) for a in range(3)],
                     [max(v.co[a] for v in component) for a in range(3)]])
    return rows


class Meter:
    """2 立体の共通体積。Blender のオブジェクトは立体ごとに持ち回し、頂点だけを姿勢ごとに書き換える"""

    def __init__(self):
        self.objects = {}
        self.stats = {"boolean": 0, "skipped": 0}

    def _object_for(self, solid, role):
        key = (solid.name, role)
        entry = self.objects.get(key)
        if entry is None or entry["solid"] is not solid:
            if entry is not None:
                self._drop(entry)
            mesh = bpy.data.meshes.new(f"meter_{role}_{solid.name}")
            mesh.from_pydata(solid.verts.tolist(), [], solid.faces.tolist())
            mesh.update()
            ob = bpy.data.objects.new(f"meter_{role}_{solid.name}", mesh)
            bpy.context.collection.objects.link(ob)
            entry = {"ob": ob, "mesh": mesh, "modifier": None, "solid": solid}
            self.objects[key] = entry
        return entry

    @staticmethod
    def _drop(entry):
        bpy.data.objects.remove(entry["ob"], do_unlink=True)
        bpy.data.meshes.remove(entry["mesh"])

    def _set_pose(self, solid, role, world_vertices):
        entry = self._object_for(solid, role)
        arr = np.asarray(world_vertices, dtype=np.float32)
        entry["mesh"].vertices.foreach_set("co", arr.ravel())
        entry["mesh"].update()
        return entry

    @staticmethod
    def bvh_of(world_vertices, faces):
        return BVHTree.FromPolygons(world_vertices.tolist(), faces.tolist(), epsilon=0.0)

    @staticmethod
    def inside(bvh, point):
        """3 方向の光線の偶奇の多数決で、点が閉じたメッシュの内側か"""
        directions = (Vector((0.2113, 0.3547, 0.9108)).normalized(),
                      Vector((0.7311, 0.2217, 0.6455)).normalized(),
                      Vector((-0.4173, 0.8061, 0.4227)).normalized())
        votes = 0
        for direction in directions:
            count, origin = 0, Vector(point)
            for _ in range(200):
                hit = bvh.ray_cast(origin, direction)
                if hit[0] is None:
                    break
                count += 1
                origin = hit[0] + direction * 1e-4
            votes += count % 2
        return votes >= 2

    def boolean_common(self, solid_a, world_a, solid_b, world_b):
        entry_a = self._set_pose(solid_a, "a", world_a)
        entry_b = self._set_pose(solid_b, "b", world_b)
        ob_a = entry_a["ob"]
        modifier = entry_a["modifier"]
        if modifier is None:
            modifier = ob_a.modifiers.new("common", "BOOLEAN")
            modifier.operation = "INTERSECT"
            modifier.solver = "MANIFOLD"
            entry_a["modifier"] = modifier
        modifier.object = entry_b["ob"]
        bpy.context.view_layer.update()
        evaluated = ob_a.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            bm = bmesh.new()
            bm.from_mesh(mesh)
            try:
                volume = closed_boundary_volume(bm)
                components = _component_bounds(bm)
            finally:
                bm.free()
        finally:
            evaluated.to_mesh_clear()
            modifier.object = None
        self.stats["boolean"] += 1
        return volume, components

    def common(self, solid_a, matrix_a, solid_b, matrix_b, full=False):
        """姿勢つきの共通体積 (mm3, 交差成分の外接箱の列)。full=True なら省略せず Boolean で測る"""
        va, vb = solid_a.posed(matrix_a), solid_b.posed(matrix_b)
        if full:
            return self.boolean_common(solid_a, va, solid_b, vb)
        return self.common_posed(solid_a, va, None, solid_b, vb, None)

    def common_posed(self, solid_a, va, bvh_a, solid_b, vb, bvh_b):
        """世界座標の頂点（と、あれば BVH）を渡す版。姿勢ごとに BVH を使い回すときに使う"""
        lo_a, hi_a = va.min(axis=0), va.max(axis=0)
        lo_b, hi_b = vb.min(axis=0), vb.max(axis=0)
        if np.any(hi_a < lo_b) or np.any(hi_b < lo_a):
            self.stats["skipped"] += 1
            return 0.0, []
        bvh_a = bvh_a or self.bvh_of(va, solid_a.faces)
        bvh_b = bvh_b or self.bvh_of(vb, solid_b.faces)
        if not bvh_a.overlap(bvh_b):
            a_in_b = np.all(lo_a >= lo_b) and np.all(hi_a <= hi_b)
            b_in_a = np.all(lo_b >= lo_a) and np.all(hi_b <= hi_a)
            nested = ((a_in_b and self.inside(bvh_b, va[0]))
                      or (b_in_a and self.inside(bvh_a, vb[0])))
            if not nested:
                self.stats["skipped"] += 1
                return 0.0, []
        return self.boolean_common(solid_a, va, solid_b, vb)

    def dispose(self):
        for entry in self.objects.values():
            self._drop(entry)
        self.objects.clear()


def self_intersections(solid, limit=20):
    """隣り合わない三角形どうしの交差（頂点を共有する組は除く）。戻りは (組の数, 先頭 limit 組)"""
    bvh = BVHTree.FromPolygons(solid.verts.tolist(), solid.faces.tolist(), epsilon=0.0)
    pairs = bvh.overlap(bvh)
    faces = solid.faces
    bad = []
    for i, j in pairs:
        if i >= j:
            continue
        if set(faces[i]) & set(faces[j]):
            continue
        bad.append((int(i), int(j)))
    return len(bad), bad[:limit]


def first_contact(meter, moving, pose_at, fixed, maximum, coarse, refine=14):
    """pose_at(t) -> 4x4。t を 0 から maximum まで進め、fixed（{名前: (Solid, 4x4)}）のどれかと
    共通体積が床を超える最初の t を二分探索で返す。接触しなければ travel は None"""

    def touching(t):
        hits = []
        for name, (solid, matrix) in fixed.items():
            volume, _ = meter.common(moving, pose_at(t), solid, matrix)
            if volume > VOLUME_FLOOR_MM3:
                hits.append(name)
        return hits

    hits = touching(0.0)
    if hits:
        return {"travel": 0.0, "nominalContact": True, "parts": hits}
    previous, t = 0.0, coarse
    while t <= maximum + 1e-9:
        hits = touching(t)
        if hits:
            low, high = previous, t
            for _ in range(refine):
                middle = (low + high) / 2.0
                if touching(middle):
                    high = middle
                else:
                    low = middle
            return {"travel": round(high, 6), "nominalContact": False, "parts": touching(high)}
        previous, t = t, t + coarse
    return {"travel": None, "nominalContact": False, "parts": []}


def calibrate(meter):
    """答えの分かっている形で計器を校正する。1 行でも外れたら、その回の判定は使わない"""
    identity = np.eye(4)
    cube = cube_solid("cal_cube", (0, 0, 0), 1.0)
    big = cube_solid("cal_big", (0, 0, 0), 4.0)
    wide = cube_solid("cal_wide", (0, 0, 0), 20.0)
    rows = {}

    def volume(a, ma, b, mb, full=False):
        return meter.common(a, ma, b, mb, full=full)[0]

    cases = {
        "overlapHalf": (volume(cube, identity, cube, translation(0.5)), 0.5, 1e-4),
        "thinOverlap0.002": (volume(cube, identity, cube, translation(0.998)), 0.002, 1e-4),
        "separated": (volume(cube, identity, cube, translation(2.0)), 0.0, 1e-9),
        "faceContact": (volume(cube, identity, cube, translation(1.0)), 0.0, 1e-7),
        "edgeContact": (volume(cube, identity, cube, translation(1.0, 1.0)), 0.0, 1e-7),
        "nestedInside": (volume(cube, identity, big, identity), 1.0, 1e-6),
        "nestedInsideReversed": (volume(big, identity, cube, identity), 1.0, 1e-6),
    }
    pose = translation(30.0, -20.0, 52.0) @ rotation((1, 0, 0), 37.0)
    cases["tiltedFaceContactAtScale"] = (volume(wide, pose, wide, pose @ translation(0.0, 20.0, 0.0)),
                                         0.0, VOLUME_FLOOR_MM3 / 10.0)
    cases["tiltedThinOverlapAtScale"] = (volume(wide, pose, wide, pose @ translation(0.0, 19.99, 0.0)),
                                         4.0, 0.01)
    for key, (measured, expected, tolerance) in cases.items():
        rows[key] = {"measured": measured, "expected": expected,
                     "pass": abs(measured - expected) <= tolerance}
    agreement = []
    for label, mb, other in (("separated", translation(2.0), cube), ("overlap", translation(0.3), cube),
                             ("nested", identity, big)):
        fast = volume(cube, identity, other, mb)
        full = volume(cube, identity, other, mb, full=True)
        agreement.append({"case": label, "fast": fast, "full": full, "pass": abs(fast - full) < 1e-9})
    rows["skipAgreesWithBoolean"] = {"cases": agreement, "pass": all(r["pass"] for r in agreement)}
    wall = box_solid("cal_wall", (1.0, -5.0, -5.0), (3.0, 5.0, 5.0))
    linear = first_contact(meter, cube, lambda t: translation(t), {"wall": (wall, identity)},
                           maximum=2.0, coarse=0.05)
    expected_linear = 0.5 + VOLUME_FLOOR_MM3
    rows["firstContactLinear"] = {"measured": linear["travel"], "expected": expected_linear,
                                  "pass": linear["travel"] is not None
                                  and abs(linear["travel"] - expected_linear) <= 1e-4}
    far = first_contact(meter, cube, lambda t: translation(t), {"wall": (wall, translation(5.0))},
                        maximum=2.0, coarse=0.05)
    rows["firstContactNone"] = {"measured": far["travel"], "expected": None, "pass": far["travel"] is None}
    square = box_solid("cal_square", (-1.0, -1.0, -1.0), (1.0, 1.0, 1.0))
    wall2 = box_solid("cal_wall2", (1.2, -5.0, -5.0), (3.0, 5.0, 5.0))

    def corner_volume(a_deg):
        a = math.radians(a_deg)
        d = max(0.0, math.cos(a) + math.sin(a) - 1.2)
        return 2.0 * d * d / math.sin(2.0 * a)

    low, high = 13.0, 20.0
    for _ in range(60):
        middle = (low + high) / 2.0
        if corner_volume(middle) > VOLUME_FLOOR_MM3:
            high = middle
        else:
            low = middle
    angular = first_contact(meter, square, lambda t: rotation((0, 0, 1), t),
                            {"wall": (wall2, identity)}, maximum=30.0, coarse=0.5)
    rows["firstContactAngular"] = {"measured": angular["travel"], "expected": high,
                                   "pass": angular["travel"] is not None
                                   and abs(angular["travel"] - high) <= 0.01}
    rows["pass"] = all(row["pass"] for row in rows.values())
    return rows
