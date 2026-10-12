"""タンジブル画素キューブの干渉検証（実 STL、全サーボ角、MANIFOLD 共通体積）。

実行: "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python-exit-code 1 --python models/tangible-pixel-cube/verify.py
出力: build/verify_report.json, build/boolean_evidence.json
drive.py はこのファイルの計器（Solid / Meter / 校正）を読む。

計器の構成:
- 主計器は Blender Boolean の MANIFOLD による共通体積（mm3）。入力 STL は先に全辺の 2 面共有・向き・自己交差を検査する
- 表面が交わらない組（BVH の三角形交差が 0 で、入れ子でもない）は共通体積 0 と数学的に決まるので Boolean を省く。
  この省略が Boolean と一致することを校正（立方体の正負例）と、実部品の抜き取りの全組比較（verify_report.prefilterAgreement）で測る
- 体積の床（これ以下は 0 とみなす）は 0.001mm3。校正で固定し、後で広げない
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import os
import struct
import sys
import time
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(HERE))

import params as P  # noqa: E402
import kinematics as K  # noqa: E402
import patterns as PT  # noqa: E402
from solid_volume import closed_boundary_volume  # noqa: E402

VOLUME_FLOOR_MM3 = 0.001          # 共通体積の床。これを超えれば接触・干渉とみなす（校正で固定）
WIN_MOUTH_IN_MM = 0.4             # ベゼルの窓の下縁（画素が入る側）の 45 度の面取り（parts_static.WIN_MOUTH_IN）
SERVO_DEGS = [10.0 + k for k in range(161)]   # 10..170 度、1 度刻み（motion.json と同じ）
JIG_PARTS = ("phase_comb",)       # 組立の途中だけに居る治具。最終姿勢の干渉には入れない


# =============================================================================================
# 入出力
# =============================================================================================
def read_stl_path(path):
    """binary STL を (n, 3, 3) の倍精度配列で返す。値は float32 そのまま（丸めない）"""
    raw = Path(path).read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + 50 * count:
        raise ValueError(f"binary STL のバイト数が合わない: {path}")
    dtype = np.dtype([("normal", "<f4", 3), ("vertex", "<f4", (3, 3)), ("attr", "<u2")])
    return np.frombuffer(raw, dtype=dtype, offset=84, count=count)["vertex"].astype(float)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes(paths):
    rows = {}
    for path in paths:
        path = Path(path)
        try:
            name = path.relative_to(ROOT).as_posix()
        except ValueError:
            name = path.as_posix()
        rows[name] = sha256(path)
    return rows


def write_json(path, document):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, ensure_ascii=False, indent=1, default=_json_default)
        handle.write("\n")
    os.replace(temporary, path)


def _json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"JSON にできない型: {type(value).__name__}")


def matrix_np(values):
    """列優先の 16 要素 -> 4x4 numpy（mm）"""
    return np.array(values, dtype=float).reshape(4, 4).T


def translation_np(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def rot_x_np(angle_deg, y0=0.0, z0=0.0):
    """点 (*, y0, z0) を通る X 軸まわりに angle_deg 回す（+Y から +Z へが正）。motion.json と独立に params から作る"""
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    m[1, 1], m[1, 2], m[2, 1], m[2, 2] = c, -s, s, c
    m[1, 3] = y0 - (c * y0 - s * z0)
    m[2, 3] = z0 - (s * y0 + c * z0)
    return m


def rot_z_np(angle_deg, x0=0.0, y0=0.0):
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    m[0, 0], m[0, 1], m[1, 0], m[1, 1] = c, -s, s, c
    m[0, 3] = x0 - (c * x0 - s * y0)
    m[1, 3] = y0 - (s * x0 + c * y0)
    return m


# =============================================================================================
# 立体
# =============================================================================================
class Solid:
    """閉じた三角形メッシュ（mm）。頂点は float32 値そのままで共有化する"""

    def __init__(self, name, tris):
        self.name = name
        tris = np.asarray(tris, dtype=float)
        self.tris = tris
        flat = tris.reshape(-1, 3)
        self.verts, inverse = np.unique(flat, axis=0, return_inverse=True)
        self.faces = inverse.reshape(-1, 3)
        self.lo = self.verts.min(axis=0)
        self.hi = self.verts.max(axis=0)

    @staticmethod
    def load(name):
        return Solid(name, read_stl_path(BUILD / f"{name}.stl"))

    def posed(self, matrix):
        return self.verts @ matrix[:3, :3].T + matrix[:3, 3]

    def posed_bounds(self, matrix):
        if np.allclose(matrix, np.eye(4)):
            return self.lo, self.hi
        corners = np.array([[x, y, z] for x in (self.lo[0], self.hi[0])
                            for y in (self.lo[1], self.hi[1]) for z in (self.lo[2], self.hi[2])])
        world = corners @ matrix[:3, :3].T + matrix[:3, 3]
        return world.min(axis=0), world.max(axis=0)

    def posed_tris(self, matrix):
        return self.tris @ matrix[:3, :3].T + matrix[:3, 3]


def cube_solid(name, center, size):
    cx, cy, cz = center
    h = size / 2.0
    corners = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
               (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
    verts = np.array([(cx + x * h, cy + y * h, cz + z * h) for x, y, z in corners], dtype=float)
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
             (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return Solid(name, verts[np.array(faces)])


def box_solid(name, lower, upper):
    x0, y0, z0 = lower
    x1, y1, z1 = upper
    verts = np.array([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                      (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], dtype=float)
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
             (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return Solid(name, verts[np.array(faces)])


# =============================================================================================
# 計器: 共通体積
# =============================================================================================
class Meter:
    """2 立体の共通体積。表面が交わらない組は Boolean を省き、それ以外を MANIFOLD で測る。

    Blender のオブジェクトは立体ごとに 1 つ持ち回し、頂点座標だけを姿勢ごとに書き換える（毎回作り直さない）。
    """

    def __init__(self):
        self.objects = {}
        self.stats = {"boolean": 0, "bvh_zero": 0, "nested_zero": 0}

    # -- Blender 側の持ち回しオブジェクト ---------------------------------------------------
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

    # -- 表面が交わるか --------------------------------------------------------------------
    @staticmethod
    def bvh_of(world_vertices, faces):
        return BVHTree.FromPolygons(world_vertices.tolist(), faces.tolist(), epsilon=0.0)

    @staticmethod
    def _inside(bvh, point):
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

    def zero_by_topology(self, va, fa, bvh_a, lo_a, hi_a, vb, fb, bvh_b, lo_b, hi_b):
        """True なら共通体積は数学的に 0（外接箱が離れている / 表面が交わらず入れ子でもない）。
        None なら Boolean で測る"""
        if np.any(hi_a < lo_b) or np.any(hi_b < lo_a):
            return True
        if bvh_a.overlap(bvh_b):
            return None
        # 表面が交わらない: 離れているか、一方が他方の中にある。入れ子は外接箱の包含が前提
        a_in_b = np.all(lo_a >= lo_b) and np.all(hi_a <= hi_b)
        b_in_a = np.all(lo_b >= lo_a) and np.all(hi_b <= hi_a)
        if a_in_b and self._inside(bvh_b, va[0]):
            return None
        if b_in_a and self._inside(bvh_a, vb[0]):
            return None
        return True

    # -- Boolean ---------------------------------------------------------------------------
    def boolean_common(self, solid_a, world_a, solid_b, world_b):
        """MANIFOLD の INTERSECT。戻りは体積（mm3）と交差成分の外接箱（世界座標）"""
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

    def common(self, solid_a, matrix_a, solid_b, matrix_b, bvh_a=None, bvh_b=None):
        """姿勢つきの共通体積。(体積, 成分の外接箱の列, 方式)。方式は "bvh" か "boolean" """
        va, vb = solid_a.posed(matrix_a), solid_b.posed(matrix_b)
        lo_a, hi_a = va.min(axis=0), va.max(axis=0)
        lo_b, hi_b = vb.min(axis=0), vb.max(axis=0)
        if np.any(hi_a < lo_b) or np.any(hi_b < lo_a):
            self.stats["bvh_zero"] += 1
            return 0.0, [], "aabb"
        bvh_a = bvh_a or self.bvh_of(va, solid_a.faces)
        bvh_b = bvh_b or self.bvh_of(vb, solid_b.faces)
        verdict = self.zero_by_topology(va, solid_a.faces, bvh_a, lo_a, hi_a,
                                        vb, solid_b.faces, bvh_b, lo_b, hi_b)
        if verdict:
            self.stats["bvh_zero"] += 1
            return 0.0, [], "bvh"
        volume, components = self.boolean_common(solid_a, va, solid_b, vb)
        return volume, components, "boolean"

    def common_full(self, solid_a, matrix_a, solid_b, matrix_b):
        """省略せずに Boolean だけで測る（校正・省略の検証用）"""
        va, vb = solid_a.posed(matrix_a), solid_b.posed(matrix_b)
        volume, components = self.boolean_common(solid_a, va, solid_b, vb)
        return volume, components

    def dispose(self):
        for entry in self.objects.values():
            self._drop(entry)
        self.objects.clear()


def _component_bounds(bm):
    """Boolean 結果の連結成分ごとの外接箱 [[x0,y0,z0],[x1,y1,z1]]"""
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


# =============================================================================================
# 接触の初検出（相対移動）
# =============================================================================================
def components_inside(components, regions, tolerance=0.02):
    """全成分の外接箱が、いずれかの許可領域（[[x0,y0,z0],[x1,y1,z1]]）に収まるか"""
    if not components:
        return False
    for lower, upper in components:
        if not any(all(region[0][a] - tolerance <= lower[a] and upper[a] <= region[1][a] + tolerance
                       for a in range(3)) for region in regions):
            return False
    return True


def contact_event(volume, components, allowed=None):
    """接触の発生。volume が床を超え、許可領域が与えられたときはその外にも成分があること"""
    if volume <= VOLUME_FLOOR_MM3:
        return False
    if allowed:
        return not components_inside(components, allowed)
    return True


def measure_set(meter, moving, moving_matrix, fixed, allowed=None):
    """動かす立体と、固定側の立体群（{名前: (Solid, 4x4)}）との共通体積。戻りは (最大体積, 接した名前の一覧, 成分)。
    allowed があれば、許可領域に収まらない成分を持つ組だけを数える"""
    worst, names, comps = 0.0, [], []
    for name, (solid, matrix) in fixed.items():
        volume, components, _ = meter.common(moving, moving_matrix, solid, matrix)
        if contact_event(volume, components, allowed):
            names.append(name)
            comps.extend(components)
            worst = max(worst, volume)
    return worst, names, comps


def first_contact(meter, moving, step_matrix, fixed, maximum, coarse, allowed=None, refine=14):
    """step_matrix(t) -> 4x4（動かす立体の姿勢）。t を 0 から maximum まで進め、最初に接触する t を二分探索で返す。
    戻り: {nominalEvent, travel, volume, parts, components}。接触しなければ travel は None"""
    volume0, names0, comps0 = measure_set(meter, moving, step_matrix(0.0), fixed, allowed)
    if names0:
        return {"nominalEvent": True, "travel": 0.0, "volume": volume0, "parts": names0, "components": comps0}
    previous, t = 0.0, coarse
    while t <= maximum + 1e-9:
        volume, names, comps = measure_set(meter, moving, step_matrix(t), fixed, allowed)
        if names:
            low, high = previous, t
            for _ in range(refine):
                middle = (low + high) / 2.0
                if measure_set(meter, moving, step_matrix(middle), fixed, allowed)[1]:
                    high = middle
                else:
                    low = middle
            volume, names, comps = measure_set(meter, moving, step_matrix(high), fixed, allowed)
            return {"nominalEvent": False, "travel": round(high, 6), "volume": volume,
                    "parts": names, "components": comps}
        previous, t = t, t + coarse
    return {"nominalEvent": False, "travel": None, "volume": 0.0, "parts": [], "components": []}


def linear_step(base, direction):
    """base（4x4）の立体を direction（単位ベクトル）へ t 動かす姿勢"""
    d = np.asarray(direction, dtype=float)
    return lambda t: translation_np(*(d * t)) @ base


def angular_step_x(base, sign, y0, z0):
    """X 軸（Y=y0, Z=z0 を通る）まわりに sign*t 度回す"""
    return lambda t: rot_x_np(sign * t, y0, z0) @ base


# =============================================================================================
# 上向きの面の高さ（カムの上に足が載る高さを測る）
# =============================================================================================
def top_heights(tris, xs, ys):
    """tris（(T,3,3) 倍精度、世界座標）の上向きの三角形だけから、各点（xs[k], ys[k]）の真上から見た最高点の Z。
    どの面の下にも入らない点は -inf"""
    tris = np.asarray(tris, dtype=float)
    normal_z = ((tris[:, 1, 0] - tris[:, 0, 0]) * (tris[:, 2, 1] - tris[:, 0, 1])
                - (tris[:, 1, 1] - tris[:, 0, 1]) * (tris[:, 2, 0] - tris[:, 0, 0]))
    t = tris[normal_z > 1e-12]
    out = np.full(len(xs), -np.inf)
    if not len(t):
        return out
    a, b, c = t[:, 0], t[:, 1], t[:, 2]
    denominator = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    px, py = np.asarray(xs, dtype=float)[None, :], np.asarray(ys, dtype=float)[None, :]
    u = ((b[:, 1] - c[:, 1])[:, None] * (px - c[:, 0][:, None])
         + (c[:, 0] - b[:, 0])[:, None] * (py - c[:, 1][:, None])) / denominator[:, None]
    v = ((c[:, 1] - a[:, 1])[:, None] * (px - c[:, 0][:, None])
         + (a[:, 0] - c[:, 0])[:, None] * (py - c[:, 1][:, None])) / denominator[:, None]
    w = 1.0 - u - v
    inside = (u >= -1e-9) & (v >= -1e-9) & (w >= -1e-9)
    z = u * a[:, 2][:, None] + v * b[:, 2][:, None] + w * c[:, 2][:, None]
    return np.where(inside, z, -np.inf).max(axis=0)


def top_max_in_rect(tris, rect):
    """矩形 rect = (x0, x1, y0, y1) の真上から見た最高点の Z（厳密）。区分線形の面の最大値は、
    (1) 矩形の中にある上向き三角形の頂点、(2) 三角形の辺と矩形の辺の交点、(3) 矩形の角の真上の面、のどれかにある。
    矩形の中に上向きの面が無ければ -inf"""
    x0, x1, y0, y1 = rect
    tris = np.asarray(tris, dtype=float)
    normal_z = ((tris[:, 1, 0] - tris[:, 0, 0]) * (tris[:, 2, 1] - tris[:, 0, 1])
                - (tris[:, 1, 1] - tris[:, 0, 1]) * (tris[:, 2, 0] - tris[:, 0, 0]))
    up = tris[normal_z > 1e-12]
    if not len(up):
        return -math.inf
    best = -math.inf
    vertices = up.reshape(-1, 3)
    inside = ((vertices[:, 0] >= x0) & (vertices[:, 0] <= x1) & (vertices[:, 1] >= y0) & (vertices[:, 1] <= y1))
    if inside.any():
        best = max(best, float(vertices[inside, 2].max()))
    starts = up.reshape(-1, 3)
    ends = np.roll(up, -1, axis=1).reshape(-1, 3)
    for axis, value, other_lo, other_hi in ((0, x0, y0, y1), (0, x1, y0, y1), (1, y0, x0, x1), (1, y1, x0, x1)):
        da, db = starts[:, axis] - value, ends[:, axis] - value
        crossing = (da * db <= 0) & (da != db)
        if not crossing.any():
            continue
        s = da[crossing] / (da[crossing] - db[crossing])
        points = starts[crossing] + s[:, None] * (ends[crossing] - starts[crossing])
        other = 1 - axis
        ok = (points[:, other] >= other_lo) & (points[:, other] <= other_hi)
        if ok.any():
            best = max(best, float(points[ok, 2].max()))
    corners = top_heights(up, [x0, x0, x1, x1], [y0, y1, y0, y1])
    if np.isfinite(corners).any():
        best = max(best, float(corners.max()))
    return best


def top_height_calibration():
    """答えの分かる形で top_heights を確かめる。平らな板、傾けた板、穴の外"""
    cube = cube_solid("topcal", (0, 0, 0), 2.0)
    flat = float(top_heights(cube.tris, [0.0], [0.0])[0])
    outside = float(top_heights(cube.tris, [5.0], [0.0])[0])
    # X 軸まわりに 30 度傾けた立方体。中心の真上の高さ = 1 / cos 30 度（上面は 30 度傾く）
    tilted = cube.posed_tris(rot_x_np(30.0))
    centre = float(top_heights(tilted, [0.0], [0.0])[0])
    expected_centre = 1.0 / math.cos(math.radians(30.0))
    # 傾けた立方体の最高の稜線の真上
    c30, s30 = math.cos(math.radians(30.0)), math.sin(math.radians(30.0))
    ridge = float(top_heights(tilted, [0.0], [c30 - s30])[0])
    expected_ridge = s30 + c30
    rect_ridge = top_max_in_rect(tilted, (-3.0, 3.0, -3.0, 3.0))                 # 傾けた立方体の稜線は矩形の中
    rect_clipped = top_max_in_rect(tilted, (-3.0, 3.0, -3.0, c30 - s30 - 0.5))   # 稜線の手前で矩形を切ると、切り口（辺との交点）が最高点
    rect_empty = top_max_in_rect(cube.tris, (5.0, 6.0, 5.0, 6.0))
    # 切り口の高さ: 上面は Z = (Y - ...) の平面。矩形の辺 Y = yc での上面の高さを、矩形の中の 2 点の補間で独立に求める
    yc = c30 - s30 - 0.5
    clipped_expected = float(top_heights(tilted, [0.0], [yc])[0])
    result = {"flatTopMm": flat, "outsideIsMinusInf": bool(outside == -np.inf),
              "rectRidgeMm": rect_ridge, "rectClippedMm": rect_clipped, "rectClippedExpectedMm": clipped_expected,
              "rectEmptyIsMinusInf": bool(rect_empty == -math.inf),
              "tiltedCentreMm": centre, "tiltedCentreExpectedMm": expected_centre,
              "tiltedRidgeMm": ridge, "tiltedRidgeExpectedMm": expected_ridge}
    result["pass"] = bool(abs(flat - 1.0) < 1e-9 and result["outsideIsMinusInf"]
                          and abs(centre - expected_centre) < 1e-9 and abs(ridge - expected_ridge) < 1e-6
                          and abs(rect_ridge - expected_ridge) < 1e-6 and abs(rect_clipped - clipped_expected) < 1e-6
                          and result["rectEmptyIsMinusInf"])
    return result


# =============================================================================================
# 校正
# =============================================================================================
def meter_calibration(meter):
    """原型 STL を読む前に、正負の立体で計器（共通体積・省略・初接触・姿勢）を校正する。
    床 VOLUME_FLOOR_MM3 を決める根拠もここで測る"""
    identity = np.eye(4)
    cube = cube_solid("cal_cube", (0, 0, 0), 1.0)
    rows = {}

    def volume_of(a, ma, b, mb):
        return meter.common(a, ma, b, mb)[0]

    rows["overlapHalf"] = {"measured": volume_of(cube, identity, cube, translation_np(0.5)), "expected": 0.5, "tolerance": 1e-4}
    rows["thinOverlap0.01"] = {"measured": volume_of(cube, identity, cube, translation_np(0.99)), "expected": 0.01, "tolerance": 1e-4}
    rows["thinOverlap0.002"] = {"measured": volume_of(cube, identity, cube, translation_np(0.998)), "expected": 0.002, "tolerance": 1e-4}
    rows["separated"] = {"measured": volume_of(cube, identity, cube, translation_np(2.0)), "expected": 0.0, "tolerance": 1e-9}
    rows["faceContact"] = {"measured": volume_of(cube, identity, cube, translation_np(1.0)), "expected": 0.0, "tolerance": 1e-7}
    rows["edgeContact"] = {"measured": volume_of(cube, identity, cube, translation_np(1.0, 1.0)), "expected": 0.0, "tolerance": 1e-7}
    big = cube_solid("cal_big", (0, 0, 0), 4.0)
    rows["nestedInside"] = {"measured": volume_of(cube, identity, big, identity), "expected": 1.0, "tolerance": 1e-6}
    rows["nestedInsideReversed"] = {"measured": volume_of(big, identity, cube, identity), "expected": 1.0, "tolerance": 1e-6}
    # 実寸の座標と傾きでの面接触の数値ノイズ。床の 1/10 を超えたら計器の方が壊れている
    wide = cube_solid("cal_wide", (0, 0, 0), 20.0)
    pose = translation_np(30.0, -20.0, 52.0) @ rot_x_np(37.0, 0.0, 0.0)
    slide = pose @ translation_np(0.0, 20.0, 0.0)
    rows["tiltedFaceContactAtScale"] = {"measured": volume_of(wide, pose, wide, slide), "expected": 0.0,
                                        "tolerance": VOLUME_FLOOR_MM3 / 10.0}
    rows["tiltedThinOverlapAtScale"] = {"measured": volume_of(wide, pose, wide, pose @ translation_np(0.0, 19.99, 0.0)),
                                        "expected": 0.01 * 400.0, "tolerance": 0.01}
    # 省略が Boolean と一致するか（離れ・食い込み・入れ子）
    agreement = []
    for label, mb, other in (("separated", translation_np(2.0), cube), ("overlap", translation_np(0.3), cube),
                             ("nested", identity, big)):
        fast = meter.common(cube, identity, other, mb)[0]
        full = meter.common_full(cube, identity, other, mb)[0]
        agreement.append({"case": label, "fast": fast, "full": full, "pass": abs(fast - full) < 1e-9})
    rows["prefilterAgreement"] = {"cases": agreement, "pass": all(row["pass"] for row in agreement)}
    for row in rows.values():
        if "tolerance" in row:
            row["pass"] = abs(row["measured"] - row["expected"]) <= row["tolerance"]
    # 床の根拠: 厚み 0.002mm の重なり（体積 0.002mm3）は床を超えて検出され、実寸の傾いた面接触の数値ノイズは床の 1/10 以下
    rows["floorSeparatesNoiseFromOverlap"] = {
        "floorMm3": VOLUME_FLOOR_MM3,
        "pass": bool(rows["thinOverlap0.002"]["measured"] > VOLUME_FLOOR_MM3
                     and rows["tiltedFaceContactAtScale"]["measured"] <= VOLUME_FLOOR_MM3 / 10.0),
        "note": "実寸 20mm 立方体の傾けた面接触が床の 1/10 以下、厚み 0.002mm（体積 0.002mm3）の重なりが床を超える"}
    # 初接触の探索（直線）: 1mm 立方体を +X へ。隙間 0.5mm の相手の面
    wall = box_solid("cal_wall", (1.0, -5.0, -5.0), (3.0, 5.0, 5.0))
    linear = first_contact(meter, cube, linear_step(identity, (1, 0, 0)), {"wall": (wall, identity)},
                           maximum=2.0, coarse=0.05)
    # 初接触は「共通体積が床を超えた最初の位置」。面接触なら、侵入深さ = 床 / 接触面積 だけ手前の値より先で検出される
    expected_linear = 0.5 + VOLUME_FLOOR_MM3 / 1.0
    rows["firstContactLinear"] = {"measured": linear["travel"], "expected": expected_linear, "tolerance": 0.0001,
                                  "note": "隙間 0.5mm + 床 / 面積（1mm2）",
                                  "pass": bool(linear["travel"] is not None
                                               and abs(linear["travel"] - expected_linear) <= 0.0001)}
    # 初接触の探索（回転）: 2x2 の正方形を Z まわりに回し、X=1.2 の壁に角が当たる角度
    square = box_solid("cal_square", (-1.0, -1.0, -1.0), (1.0, 1.0, 1.0))
    wall2 = box_solid("cal_wall2", (1.2, -5.0, -5.0), (3.0, 5.0, 5.0))
    # 角の接触: 壁を越えた分 d = cos a + sin a - 1.2 の三角形（面積 d^2 / sin 2a）x 厚み 2 が床になる a を解析的に求める
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
    expected_angle = high
    nominal_angle = math.degrees(math.asin(1.2 / math.sqrt(2.0))) - 45.0
    angular = first_contact(meter, square, lambda t: rot_z_np(t), {"wall": (wall2, identity)}, maximum=30.0, coarse=0.5)
    rows["firstContactAngular"] = {"measured": angular["travel"], "expected": expected_angle, "tolerance": 0.01,
                                   "contactWithoutFloorDeg": nominal_angle,
                                   "note": "角の接触は侵入が浅いうちは体積が小さく、床を超える角が幾何の接触角より 1 度ほど先になる。その解析値と比べる",
                                   "pass": bool(angular["travel"] is not None
                                                and abs(angular["travel"] - expected_angle) <= 0.01)}
    # 許可領域の外の成分だけを数える初接触: 設計どおりのリブでは止まらず、その先の面で止まる
    rib = box_solid("cal_rib", (0.8, -0.3, -0.3), (1.0, 0.3, 0.3))
    face = box_solid("cal_face", (1.5, -5.0, -5.0), (3.0, 5.0, 5.0))
    region = [[0.5, -0.31, -0.31], [1.01, 0.31, 0.31]]
    both = {"rib": (rib, identity), "face": (face, identity)}
    plain = first_contact(meter, cube, linear_step(identity, (1, 0, 0)), both, maximum=2.0, coarse=0.02)
    masked = first_contact(meter, cube, linear_step(identity, (1, 0, 0)), both, maximum=2.0, coarse=0.02,
                           allowed=[region])
    plain_expected = 0.3 + VOLUME_FLOOR_MM3 / 0.36       # リブの先端 0.6 x 0.6
    masked_expected = 1.0 + VOLUME_FLOOR_MM3 / 1.0       # 面は 1mm2 の立方体の面
    rows["firstContactIgnoresDesignedRib"] = {
        "plainTravel": plain["travel"], "plainExpected": plain_expected,
        "maskedTravel": masked["travel"], "maskedExpected": masked_expected,
        "pass": bool(plain["travel"] is not None and abs(plain["travel"] - plain_expected) <= 0.0002
                     and masked["travel"] is not None and abs(masked["travel"] - masked_expected) <= 0.0002)}
    # 姿勢の作り方: サーボ軸（Y=0, Z=Zs）まわりに +90 度。軸の 18 下の点は +Y の 18 へ
    zs = P.SERVO_AXIS_Z * 1000.0
    rotated = (rot_x_np(90.0, 0.0, zs) @ np.array([1.0, 0.0, zs - 18.0, 1.0]))[:3]
    rows["rotationConvention"] = {"measured": rotated.tolist(), "expected": [1.0, 18.0, zs],
                                  "pass": bool(np.allclose(rotated, [1.0, 18.0, zs], atol=1e-9))}
    rows["topHeight"] = top_height_calibration()
    rows["pass"] = all(row["pass"] for row in rows.values())
    return rows


# =============================================================================================
# 場面（全部品の STL と、サーボ角ごとの姿勢）
# =============================================================================================
def group_of(name):
    """部品 id の動き方。独立に params の id 規則から決める（motion.py を読まない）"""
    if name in ("housing", "bezel", "guide_plate", "sg92r") or name.startswith("servo_clip_"):
        return ("static",)
    if name in ("horn_coupler", "sg92r_horn"):
        return ("servo",)
    parts = name.split("_")
    if parts[0] in ("shaft", "gear") and len(parts) == 2:
        return ("axis", int(parts[1]))
    if parts[:2] == ["shaft", "clip"]:
        return ("axis", int(parts[2]))
    if parts[0] == "cam":
        return ("axis", int(parts[2]))
    if parts[0] == "pixel":
        return ("pixel", int(parts[1]), int(parts[2]))
    raise ValueError(f"動き方の分からない部品: {name}")


class Scene:
    """manifest の全部品（治具を除く）と motion.json の姿勢"""

    def __init__(self):
        self.manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
        self.motion = json.loads((BUILD / "motion.json").read_text(encoding="utf-8"))
        self.names = [part["id"] for part in self.manifest["parts"] if part["id"] not in JIG_PARTS]
        self.solids = {name: Solid.load(name) for name in self.names}
        self.frames = {float(frame["servo_deg"]): frame["transforms"] for frame in self.motion["frames"]}
        self.groups = {name: group_of(name) for name in self.names}
        self._pose_cache = {}

    def matrix(self, name, theta):
        values = self.frames[float(theta)].get(name)
        if not values:
            return np.eye(4)
        return matrix_np(values)

    def poses(self, theta):
        cached = self._pose_cache.get(theta)
        if cached is None:
            cached = {name: self.matrix(name, theta) for name in self.names}
            self._pose_cache[theta] = cached
        return cached

    def pixel_dz(self, name, theta):
        return float(self.matrix(name, theta)[2, 3])


def independent_matrix(name, theta, group, dz=0.0):
    """params と kinematics から作る姿勢（motion.json を読まない）"""
    zs = P.SERVO_AXIS_Z * 1000.0
    zc = P.CAM_AXIS_Z * 1000.0
    if group[0] == "servo":
        return rot_x_np(K.servo_delta(theta), 0.0, zs)
    if group[0] == "axis":
        j = group[1]
        return rot_x_np(K.axis_angle(theta, j), K.axis_y(j) * 1000.0, zc)
    if group[0] == "pixel":
        return translation_np(0.0, 0.0, dz)
    return np.eye(4)


def motion_consistency(scene):
    """motion.json の行列が params / kinematics から独立に作った姿勢と一致するか（回転・並進は全部品、画素は X/Y が動かないこと）"""
    worst_rotation, worst_translation, rows = 0.0, 0.0, 0
    pixel_xy = 0.0
    for theta in SERVO_DEGS:
        for name in scene.names:
            group = scene.groups[name]
            actual = scene.matrix(name, theta)
            dz = actual[2, 3] if group[0] == "pixel" else 0.0
            expected = independent_matrix(name, theta, group, dz)
            worst_rotation = max(worst_rotation, float(np.abs(actual[:3, :3] - expected[:3, :3]).max()))
            worst_translation = max(worst_translation, float(np.abs(actual[:3, 3] - expected[:3, 3]).max()))
            if group[0] == "pixel":
                pixel_xy = max(pixel_xy, float(np.abs(actual[:2, 3]).max()))
            rows += 1
    return {"matricesCompared": rows, "maxRotationElementDiff": worst_rotation, "maxTranslationDiffMm": worst_translation,
            "pixelMaxXYTranslationMm": pixel_xy, "frames": len(SERVO_DEGS),
            "pass": bool(worst_rotation < 1e-5 and worst_translation < 1e-4 and pixel_xy < 1e-9
                         and sorted(scene.frames) == SERVO_DEGS)}


# =============================================================================================
# 設計した潰しリブ（これだけ重なってよい。場所と量を限定する）
# =============================================================================================
def _box_around(points, margin):
    """点列の外接箱（[[x0,y0,z0],[x1,y1,z1]]）を margin だけ広げる"""
    pts = np.asarray(points, dtype=float)
    return [(pts.min(axis=0) - margin).tolist(), (pts.max(axis=0) + margin).tolist()]


def hex_rib_regions(axis_j, x0, x1):
    """軸 j の六角穴の潰しリブが軸の六角の面へ食い込む領域（φ=0 の組立姿勢。軸に直交する面は (Y,Z)、X は x0..x1）。
    リブ = 穴の面（apothem a_b）から内へ HEX_RIB_H、幅 HEX_RIB_W。軸の面（apothem a_s）より内側の部分だけが重なる"""
    a_s = P.SHAFT_AF * 1000.0 / 2.0
    a_b = P.SHAFT_BORE_AF * 1000.0 / 2.0
    h = P.HEX_RIB_H * 1000.0
    w = P.HEX_RIB_W * 1000.0 / 2.0
    y0, z0 = K.axis_y(axis_j) * 1000.0, P.CAM_AXIS_Z * 1000.0
    regions = []
    # 潰しリブは穴の六角の 1 面おき（面の法線 30, 150, 270 度）。キーの切り落とし面（法線 HEX_KEY_NORMAL_DEG）とは別の面
    for th_deg in (30, 150, 270)[:P.HEX_RIB_FACES]:
        th = math.radians(th_deg)
        n = np.array([math.cos(th), math.sin(th)])
        t = np.array([-n[1], n[0]])
        corners = []
        for radial in (a_b - h, a_s):
            for tangential in (-w, w):
                p = radial * n + tangential * t
                corners.append((x0, y0 + p[0], z0 + p[1]))
                corners.append((x1, y0 + p[0], z0 + p[1]))
        regions.append(_box_around(corners, 0.0))
    return regions


def designed_overlaps(scene):
    """{(a, b): 仕様}。a < b の順。仕様 = {kind, regions, components, minMm3, maxMm3, theoryMm3}"""
    specs = {}
    crush = P.HEX_RIB_CRUSH * 1000.0
    width = P.HEX_RIB_W * 1000.0
    chamfer = P.FIRST_LAYER_CHAMFER * 1000.0      # 穴のベッド側の縁の面取り 0.3mm 分、リブの長さが短くなる
    for j in range(P.N):
        shaft = f"shaft_{j}"
        for i in range(P.N):
            cam = f"cam_{i}_{j}"
            cx = K.cam_x(i, j) * 1000.0
            theory = P.HEX_RIB_FACES * width * crush * (P.CAM_T * 1000.0 - chamfer)
            specs[tuple(sorted((shaft, cam)))] = {
                "kind": "hex-crush-ribs", "regions": hex_rib_regions(j, cx - P.CAM_T * 500.0, cx + P.CAM_T * 500.0),
                "components": P.HEX_RIB_FACES, "theoryMm3": theory,
                "minMm3": theory * 0.98, "maxMm3": theory * 1.02,
                "basis": "潰しリブ 3 本 x 幅 0.6 x 潰し代 0.18 x（カム厚 4.0 - 穴の面取り 0.3）"}
        gear = f"gear_{j}"
        theory = P.HEX_RIB_FACES * width * crush * (P.HEX_RIB_L_GEAR * 1000.0 - chamfer)
        specs[tuple(sorted((shaft, gear)))] = {
            "kind": "hex-crush-ribs",
            "regions": hex_rib_regions(j, P.GEAR_X0 * 1000.0, P.GEAR_X1 * 1000.0),
            "components": P.HEX_RIB_FACES, "theoryMm3": theory,
            "minMm3": theory * 0.98, "maxMm3": theory * 1.02,
            "basis": "潰しリブ 3 本 x 幅 0.6 x 潰し代 0.18 x（歯幅 2.4 - 穴の面取り 0.3）"}
    # SG92R の取付耳と柵の潰しリブ（片側 2 本 x 柵 2 枚 x 耳 2 つ = 8 本）。耳と柵の隙間 0.2、リブの高さ 0.3 で潰し代 0.1
    SG = P.SG
    ear_x0 = P.SERVO_BODY_X0 * 1000.0 + SG.FLANGE_BOTTOM_Z * 1000.0
    ear_x1 = ear_x0 + SG.FLANGE_T * 1000.0
    ear_z0 = P.SERVO_AXIS_Z * 1000.0 - SG.BODY_W * 1000.0 / 2.0
    fence_top = ear_z0 + 8.0
    clr = P.SERVO_CLR * 1000.0
    body_y0 = (SG.BODY_CENTER_X - SG.BODY_L / 2) * 1000.0
    body_y1 = (SG.BODY_CENTER_X + SG.BODY_L / 2) * 1000.0
    ear_y0 = (SG.BODY_CENTER_X - SG.FLANGE_L / 2) * 1000.0
    ear_y1 = (SG.BODY_CENTER_X + SG.FLANGE_L / 2) * 1000.0
    rib_y = [ear_y0 - clr + 0.9, body_y0 - clr - 1.5, body_y1 + clr + 1.5, ear_y1 + clr - 0.9]
    rib_w = 0.6                      # parts_static.EAR_RIB_W
    crush_depth = 0.1                # 柵のリブ高さ 0.3（EAR_RIB_H）- 耳と柵の隙間 0.2（EAR_GAP）
    rib_top = fence_top - 1.6 + crush_depth   # リブの上端は柵の上 1.6 下から 45 度で耳側へ下がる。耳の面（リブの根元から 0.2）での高さ
    regions = []
    for y in rib_y:
        regions.append([[ear_x0, y - rib_w / 2, ear_z0], [ear_x0 + crush_depth, y + rib_w / 2, rib_top]])
        regions.append([[ear_x1 - crush_depth, y - rib_w / 2, ear_z0], [ear_x1, y + rib_w / 2, rib_top]])
    max_volume = len(regions) * rib_w * crush_depth * (rib_top - ear_z0)
    specs[("housing", "sg92r")] = {
        "kind": "ear-crush-ribs", "regions": regions, "components": len(regions), "theoryMm3": max_volume,
        "minMm3": len(regions) * 0.2, "maxMm3": max_volume * 1.02,
        "basis": "柵の潰しリブ 8 本 x 幅 0.6 x 潰し代 0.1 x 長さ（耳の下端 18.2 からリブの上端 24.7 まで 6.5 以下）。上限は全部が 6.5 のとき"}
    return specs


def canonical_servo_allowance():
    """正本 SG92R の本体と付属ホーンは内部で微小に重なる。出力軸まわりの円筒の中だけ、体積 0.03mm3 まで許す"""
    zs = P.SERVO_AXIS_Z * 1000.0
    x0 = P.SERVO_BODY_X0 * 1000.0 + P.SG.HORN_HUB_BOTTOM_Z * 1000.0
    x1 = P.SERVO_BODY_X0 * 1000.0 + (P.SG.SHAFT_BOTTOM_Z + P.SG.SHAFT_H) * 1000.0
    radius = 2.313
    return {"kind": "canonical-servo-output-shaft", "regions": [[[x0 - 0.01, -radius, zs - radius], [x1 + 0.01, radius, zs + radius]]],
            "maxMm3": 0.05,
            "basis": ("出力軸（径 4.6）とホーンの穴の正本どうしの重なり。軸と穴の円は 64 角形で、相対的に回ると頂点が相手の辺へ入る"
                      "（体積の上限は頂点の入り込み 64 個 x 弦 0.226 x 矢高 0.011 / 2 x 長さ 3.0 = 0.24mm3、測定は 0.03）。スプライン歯は正本に無い")}


# =============================================================================================
# 全組・全サーボ角の干渉
# =============================================================================================
class PoseCache:
    """1 つのサーボ角での、各部品の世界座標の頂点・外接箱・BVH"""

    def __init__(self, scene, theta, static_cache):
        self.scene, self.theta, self.static_cache = scene, theta, static_cache
        self.entries = {}

    def entry(self, name):
        found = self.entries.get(name)
        if found is None:
            matrix = self.scene.matrix(name, self.theta)
            solid = self.scene.solids[name]
            if np.allclose(matrix, np.eye(4)):
                found = self.static_cache.get(name)
                if found is None:
                    verts = solid.verts
                    found = {"matrix": matrix, "verts": verts, "lo": verts.min(axis=0), "hi": verts.max(axis=0), "bvh": None}
                    self.static_cache[name] = found
            else:
                verts = solid.posed(matrix)
                found = {"matrix": matrix, "verts": verts, "lo": verts.min(axis=0), "hi": verts.max(axis=0), "bvh": None}
            self.entries[name] = found
        return found

    def bvh(self, name):
        entry = self.entry(name)
        if entry["bvh"] is None:
            entry["bvh"] = Meter.bvh_of(entry["verts"], self.scene.solids[name].faces)
        return entry["bvh"]


def measure_pair(meter, scene, cache, a, b, full=False):
    """2 部品の共通体積。(体積, 成分, 方式)"""
    ea, eb = cache.entry(a), cache.entry(b)
    solid_a, solid_b = scene.solids[a], scene.solids[b]
    if full:
        volume, components = meter.boolean_common(solid_a, ea["verts"], solid_b, eb["verts"])
        return volume, components, "boolean"
    if np.any(ea["hi"] < eb["lo"]) or np.any(eb["hi"] < ea["lo"]):
        meter.stats["bvh_zero"] += 1
        return 0.0, [], "aabb"
    verdict = meter.zero_by_topology(ea["verts"], solid_a.faces, cache.bvh(a), ea["lo"], ea["hi"],
                                     eb["verts"], solid_b.faces, cache.bvh(b), eb["lo"], eb["hi"])
    if verdict:
        meter.stats["bvh_zero"] += 1
        return 0.0, [], "bvh"
    volume, components = meter.boolean_common(solid_a, ea["verts"], solid_b, eb["verts"])
    return volume, components, "boolean"


def relative_constant(scene, a, b):
    """相対姿勢が全サーボ角で変わらない組（同じ軸の部品どうし・静止部品どうし・サーボ側どうし）"""
    ga, gb = scene.groups[a], scene.groups[b]
    return ga == gb and ga[0] in ("static", "servo", "axis")


def interference_sweep(meter, scene, thetas, log=print):
    names = scene.names
    count = len(names)
    reference_theta = 90.0
    rows = {}
    for a, b in itertools.combinations(names, 2):
        key = (a, b) if a < b else (b, a)
        rows[key] = {"parts": list(key), "constantRelativePose": relative_constant(scene, a, b),
                     "poses": 0, "aabbZero": 0, "topologyZero": 0, "boolean": 0,
                     "maximumCommonVolumeMm3": 0.0, "maximumAtServoDeg": None, "maximumComponentsMm": [],
                     "posesOverFloor": 0}
    static_cache = {}
    cached_results = {}
    started = time.time()
    for index, theta in enumerate(thetas):
        cache = PoseCache(scene, theta, static_cache)
        lows = np.array([cache.entry(name)["lo"] for name in names])
        highs = np.array([cache.entry(name)["hi"] for name in names])
        overlap = (np.all(highs[:, None, :] >= lows[None, :, :], axis=2)
                   & np.all(highs[None, :, :] >= lows[:, None, :], axis=2))
        for ia, ib in itertools.combinations(range(count), 2):
            a, b = names[ia], names[ib]
            key = (a, b) if a < b else (b, a)
            row = rows[key]
            if row["constantRelativePose"] and theta != reference_theta:
                continue
            row["poses"] += 1
            if not overlap[ia, ib]:
                row["aabbZero"] += 1
                continue
            pose_key = (a, b, tuple(np.round(cache.entry(a)["matrix"].ravel(), 7)),
                        tuple(np.round(cache.entry(b)["matrix"].ravel(), 7)))
            found = cached_results.get(pose_key)
            if found is None:
                found = measure_pair(meter, scene, cache, a, b)
                cached_results[pose_key] = found
            volume, components, method = found
            if method in ("bvh", "aabb"):
                row["topologyZero"] += 1
                continue
            row["boolean"] += 1
            if volume > VOLUME_FLOOR_MM3:
                row["posesOverFloor"] += 1
            if volume > row["maximumCommonVolumeMm3"]:
                row["maximumCommonVolumeMm3"] = volume
                row["maximumAtServoDeg"] = theta
                row["maximumComponentsMm"] = components
        if index % 20 == 0:
            log(f"  干渉 θ={theta:.0f}° ({index + 1}/{len(thetas)}) {time.time() - started:.0f}s "
                f"boolean={meter.stats['boolean']}")
    return rows


def classify_interference(rows, specs, canonical):
    """重なりのある組を、設計した重なりと、それ以外（違反）に分ける"""
    designed, violations = [], []
    for key, row in sorted(rows.items()):
        volume = row["maximumCommonVolumeMm3"]
        spec = specs.get(key)
        if spec is None and set(key) == {"sg92r", "sg92r_horn"}:
            spec = canonical
        if volume <= VOLUME_FLOOR_MM3 and spec is None:
            continue
        if spec is None:
            violations.append({**row, "reason": "設計した重なりの表に無い組が床を超えた"})
            continue
        components = row["maximumComponentsMm"]
        located = components_inside(components, spec["regions"], tolerance=0.02) if volume > VOLUME_FLOOR_MM3 else True
        count_ok = (spec.get("components") is None or len(components) == spec["components"])
        amount_ok = volume <= spec["maxMm3"] and volume >= spec.get("minMm3", 0.0)
        result = {**row, "kind": spec["kind"], "basis": spec["basis"], "theoryMm3": spec.get("theoryMm3"),
                  "allowedMinMm3": spec.get("minMm3", 0.0), "allowedMaxMm3": spec["maxMm3"],
                  "locatedInDesignedRegion": located, "componentCountMatches": count_ok,
                  "componentCount": len(components), "amountWithinLimits": amount_ok,
                  "pass": bool(located and count_ok and amount_ok)}
        designed.append(result)
        if not result["pass"]:
            violations.append({**row, "reason": f"設計した重なり（{spec['kind']}）の場所・個数・量が合わない",
                               "locatedInDesignedRegion": located, "componentCountMatches": count_ok,
                               "amountWithinLimits": amount_ok, "allowedMinMm3": spec.get("minMm3", 0.0),
                               "allowedMaxMm3": spec["maxMm3"]})
    return designed, violations


def prefilter_agreement(meter, scene, thetas, log=print):
    """省略（外接箱・BVH・入れ子判定）を使った結果が、省略せずに Boolean だけで測った結果と全組で一致するか"""
    static_cache = {}
    names = scene.names
    mismatches, compared, boolean_full = [], 0, 0
    for theta in thetas:
        cache = PoseCache(scene, theta, static_cache)
        for a, b in itertools.combinations(names, 2):
            if scene.groups[a] == scene.groups[b] and scene.groups[a][0] in ("static", "servo", "axis") and theta != 90.0:
                continue
            ea, eb = cache.entry(a), cache.entry(b)
            if np.any(ea["hi"] < eb["lo"]) or np.any(eb["hi"] < ea["lo"]):
                continue
            fast = measure_pair(meter, scene, cache, a, b)
            full = measure_pair(meter, scene, cache, a, b, full=True)
            compared += 1
            boolean_full += 1
            if abs(fast[0] - full[0]) > 1e-7:
                mismatches.append({"parts": [a, b], "servoDeg": theta, "fastMm3": fast[0], "fullMm3": full[0],
                                   "fastMethod": fast[2]})
        log(f"  省略の一致 θ={theta:.0f}° 比較 {compared} 件")
    return {"servoDegs": list(thetas), "comparedPairPoses": compared, "mismatches": mismatches,
            "pass": not mismatches}


# =============================================================================================
# カムと画素の足
# =============================================================================================
def foot_footprint(solid):
    """画素の足の下面（最下点の水平な下向き面）の Z と XY の範囲"""
    tris = solid.tris
    normal_z = ((tris[:, 1, 0] - tris[:, 0, 0]) * (tris[:, 2, 1] - tris[:, 0, 1])
                - (tris[:, 1, 1] - tris[:, 0, 1]) * (tris[:, 2, 0] - tris[:, 0, 0]))
    z_min = float(tris[:, :, 2].min())
    selected = (normal_z < 0) & (tris[:, :, 2].max(axis=1) < z_min + 1e-3)
    points = tris[selected].reshape(-1, 3)
    area = float(np.abs(normal_z[selected]).sum() / 2.0)
    x0, x1 = float(points[:, 0].min()), float(points[:, 0].max())
    y0, y1 = float(points[:, 1].min()), float(points[:, 1].max())
    return {"zMm": z_min, "x": [x0, x1], "y": [y0, y1], "areaMm2": area, "rectangleAreaMm2": (x1 - x0) * (y1 - y0)}


def shaft_vertical_play():
    """カム軸が U 溝の中で上下する遊びが、画素の高さへそのまま足される量（軸と一緒にカムが動くので画素は剛体の並進分だけずれる）。
    溝の底に載ったとき（重力）は -U_FLOOR_CLR、上の栓まで浮いたときは +HOLD_GAP、さらに軸が案内板を押し上げると +PLATE_PLAY_Z。
    表の高さの許容 ±0.1 との比較（図面の位置の軸の中心 = 0）"""
    settled = -(P.U_SLOT_W * 500.0 - P.U_SLOT_UP * 1000.0 - P.JOURNAL_D * 500.0)
    plug = P.HOLD_GAP * 1000.0
    pushed = plug + P.PLATE_PLAY_Z * 1000.0
    tol = 0.1
    return {"settledShiftMm": settled, "floatedToPlugShiftMm": plug, "floatedPushingPlateShiftMm": pushed, "tableToleranceMm": tol,
            "settledWithinTolerance": bool(abs(settled) <= tol + 1e-9), "plugWithinTolerance": bool(abs(plug) <= tol + 1e-9),
            "pushingPlateWithinTolerance": bool(abs(pushed) <= tol + 1e-9),
            "note": (f"軸が溝の底に載っていれば画素は表より {abs(settled):.2f} 低い、栓まで浮くと {plug:.2f} 高い（どちらも許容 ±{tol} の内）。"
                     f"軸が案内板を押し上げる分まで入れると {pushed:.2f} 高く、許容を超える。"
                     "浮くのは歯車の分離力が画素と軸の重さを超えるときで、実機で確かめる。+Z 側の停止の余裕 0.6（斜面で 1.2）は十分"),
            "limit": "公称 STL の幾何。実際の軸の位置は摩擦と荷重で決まるので実機未確認"}


def cam_foot_check(scene, log=print):
    """各画素・各サーボ角で、足の全領域（X 幅・Y 幅）の下にあるカム群の最高の高さを実 STL から求め、足の下面との差を測る。
    - gap = 足の下面（motion.json の高さ） - 実 STL のカム群の最高点。食い込み（gap < 0）は 0.01mm 以下、浮き（gap > 0）は 0.05mm 以下
    - 最高点を持つ部品が自分のカムであること（隣のカム・軸・歯車・クリップではない）
    - 表の停止角で表どおりの高さ（±0.1mm）"""
    flush_z = P.CAM_TOP_FLUSH * 1000.0
    rows = []
    worst_penetration, worst_float = 0.0, 0.0
    not_own = []
    table_rows = []
    dwell_worst = 0.0
    started = time.time()
    # 各画素の足の範囲と、足の下に入りうる部品の三角形（X が重なるものだけ）
    for j in range(P.N):
        candidates = [name for name in scene.names if scene.groups[name][0] == "axis" and abs(scene.groups[name][1] - j) <= 1]
        for i in range(P.N):
            pixel = f"pixel_{i}_{j}"
            cam = f"cam_{i}_{j}"
            foot = foot_footprint(scene.solids[pixel])
            rect = (foot["x"][0], foot["x"][1], foot["y"][0], foot["y"][1])
            subsets = {}
            for name in candidates:
                tris = scene.solids[name].tris
                overlap = (tris[:, :, 0].max(axis=1) >= foot["x"][0]) & (tris[:, :, 0].min(axis=1) <= foot["x"][1])
                if overlap.any():
                    subsets[name] = tris[overlap]
            min_gap, max_gap, min_at, max_at = np.inf, -np.inf, None, None
            own_not_top = 0
            supporters = {}
            heights = {}
            for theta in SERVO_DEGS:
                best, best_name, own_height = -np.inf, None, -np.inf
                for name, tris in subsets.items():
                    matrix = scene.matrix(name, theta)
                    height = top_max_in_rect(tris @ matrix[:3, :3].T + matrix[:3, 3], rect)
                    if name == cam:
                        own_height = height
                    if height > best:
                        best, best_name = height, name
                dz = scene.pixel_dz(pixel, theta)
                gap = (foot["zMm"] + dz) - best
                heights[theta] = best - flush_z
                if gap < min_gap:
                    min_gap, min_at = gap, theta
                if gap > max_gap:
                    max_gap, max_at = gap, theta
                supporters[best_name] = supporters.get(best_name, 0) + 1
                if best_name != cam and best - own_height > 0.005:
                    own_not_top += 1
                    not_own.append({"pixel": pixel, "servoDeg": theta, "supporter": best_name,
                                    "supporterHeightMm": best, "ownCamHeightMm": own_height})
            worst_penetration = max(worst_penetration, -min_gap if min_gap < 0 else 0.0)
            worst_float = max(worst_float, max_gap if max_gap > 0 else 0.0)
            # 表の停止角で表どおりの高さか
            table_errors = []
            for k, theta_k in enumerate(P.TABLE_THETA):
                expected = PT.TABLES[k][j][i]
                measured = heights[float(theta_k)]
                table_errors.append({"table": k, "servoDeg": theta_k, "expectedMm": expected,
                                     "measuredMm": round(measured, 5), "errorMm": round(measured - expected, 5)})
                # 停止区間内（軸角で ±DWELL_HALF）の最大誤差
                phi_k = K.axis_angle(theta_k, j)
                for theta in SERVO_DEGS:
                    if abs(K.axis_angle(theta, j) - phi_k) <= P.DWELL_HALF_DEG:
                        dwell_worst = max(dwell_worst, abs(heights[theta] - expected))
            table_rows.extend({"pixel": pixel, **row} for row in table_errors)
            rows.append({"pixel": pixel, "foot": foot,
                         "minimumGapMm": round(float(min_gap), 6), "minimumGapAtServoDeg": min_at,
                         "maximumGapMm": round(float(max_gap), 6), "maximumGapAtServoDeg": max_at,
                         "supportingPartsByPoseCount": supporters, "posesNotOnOwnCam": own_not_top,
                         "tableErrorMaxMm": max(abs(row["errorMm"]) for row in table_errors)})
        log(f"  足と接触 行 {j} 完了 {time.time() - started:.0f}s")
    table_worst = max(abs(row["errorMm"]) for row in table_rows)
    footprint_ok = all(abs(row["foot"]["areaMm2"] - row["foot"]["rectangleAreaMm2"]) < 1e-3 for row in rows)
    passed = bool(worst_penetration <= 0.01 and worst_float <= 0.05 and not not_own and table_worst <= 0.1 and footprint_ok)
    return {
        "pixels": len(rows), "servoDegs": len(SERVO_DEGS), "sampling": "足の下面の矩形（X 4.6 x Y 20）の真上から見た最高点。上向きの三角形の頂点・矩形の辺との交点・矩形の角の 3 種類の候補から厳密に求める（格子の刻みによる取りこぼし無し）",
        "flushFootBottomZMm": flush_z,
        "footBottomZMm": sorted({round(row["foot"]["zMm"], 4) for row in rows}),
        "footprintsAreRectangles": footprint_ok,
        "worstPenetrationMm": round(worst_penetration, 6), "penetrationLimitMm": 0.01,
        "worstFloatMm": round(worst_float, 6), "floatLimitMm": 0.05,
        "posesNotOnOwnCam": len(not_own), "notOnOwnCamExamples": not_own[:20],
        "tableHeightWorstErrorMm": round(table_worst, 6), "tableHeightLimitMm": 0.1,
        "dwellWorstErrorMm": round(dwell_worst, 6),
        "shaftVerticalPlay": shaft_vertical_play(),
        "tableHeights": table_rows, "perPixel": rows, "pass": passed}


def pixel_limits(meter, scene):
    """画素の上下の限界。つばとベゼル（+3 での隙間）、つばと案内板（-3 での隙間）、上へ引いたときの初接触"""
    bezel = scene.solids["bezel"]
    plate = scene.solids["guide_plate"]
    identity = np.eye(4)
    up_gap, down_gap = [], []
    # つばの上面の外周は 45 度の面取り（外縁 FLANGE_W/2 から頭の面 HEAD/2 まで、高さ (FLANGE_W - HEAD)/2）、
    # ベゼルの窓の下縁も 45 度の面取り。2 つの斜面は平行に向き合い、鉛直の隙間は
    #   (BEZEL_Z0 + 面取り + WINDOW/2) - (つばの上面 - 面取りの高さ + FLANGE_W/2) - H_MAX
    flange_chamfer = (P.FLANGE_W - P.HEAD) * 500.0
    slope_stop_gap = ((P.BEZEL_Z0 * 1000.0 + WIN_MOUTH_IN_MM + P.WINDOW * 500.0)
                      - (P.FLANGE_TOP_FLUSH * 1000.0 - flange_chamfer + P.FLANGE_W * 500.0) - P.H_MAX * 1000.0)
    rows = []
    for j in range(P.N):
        for i in range(P.N):
            name = f"pixel_{i}_{j}"
            solid = scene.solids[name]
            at_max = first_contact(meter, solid, linear_step(translation_np(0, 0, P.H_MAX * 1000.0), (0, 0, 1)),
                                   {"bezel": (bezel, identity)}, maximum=2.0, coarse=0.05)
            from_flush = first_contact(meter, solid, linear_step(identity, (0, 0, 1)),
                                       {"bezel": (bezel, identity)}, maximum=5.0, coarse=0.1)
            removed = first_contact(meter, solid, linear_step(translation_np(0, 0, P.H_MAX * 1000.0), (0, 0, 1)),
                                    {"bezel": (bezel, translation_np(0, 0, 200.0))}, maximum=2.0, coarse=0.1)
            at_min = first_contact(meter, solid, linear_step(translation_np(0, 0, P.H_MIN * 1000.0), (0, 0, -1)),
                                   {"guide_plate": (plate, identity)}, maximum=2.0, coarse=0.05)
            expected_up = P.FLANGE_STOP_GAP * 1000.0
            expected_flush = expected_up + P.H_MAX * 1000.0
            expected_down = (P.FLANGE_BOT_FLUSH + P.H_MIN - P.PLATE_Z1) * 1000.0
            # つばの上面は 0.7 の 45 度の面取り、ベゼルの窓の下縁は 0.4 の 45 度の面取りで、2 つの斜面が平行に向き合う。
            # 最初の接触は平らな面どうしの設計値（0.6）より広い。設計値より狭くないこと（隙間の下限 0.6）と、
            # 広がりが斜面の幾何（1.2）に一致することを見る
            up_ok = (at_max["travel"] is not None and at_max["travel"] >= expected_up - 0.03
                     and abs(at_max["travel"] - slope_stop_gap) <= 0.03)
            flush_ok = (from_flush["travel"] is not None and from_flush["travel"] >= expected_flush - 0.03
                        and abs(from_flush["travel"] - (slope_stop_gap + P.H_MAX * 1000.0)) <= 0.03)
            down_ok = at_min["travel"] is not None and abs(at_min["travel"] - expected_down) <= 0.03
            rows.append({"pixel": name, "upFromPlus3Mm": at_max["travel"], "upFromFlushMm": from_flush["travel"],
                         "downFromMinus3Mm": at_min["travel"], "designUpFromPlus3Mm": expected_up, "slopeGeometryUpFromPlus3Mm": slope_stop_gap,
                         "designUpFromFlushMm": expected_flush, "expectedDownFromMinus3Mm": expected_down,
                         "bezelRemovedNegativeTravelMm": removed["travel"],
                         "pass": bool(up_ok and flush_ok and down_ok and removed["travel"] is None)})
            up_gap.append(at_max["travel"])
            down_gap.append(at_min["travel"])
    return {"pixels": rows, "upGapMm": [min(up_gap), max(up_gap)], "downGapMm": [min(down_gap), max(down_gap)],
            "designUpGapMm": P.FLANGE_STOP_GAP * 1000.0, "slopeGeometryUpGapMm": slope_stop_gap,
            "note": ("+3 での上向きの最初の接触は、平らな面どうしの設計値 0.6 ではなく、つばの上面の 45 度の面取りとベゼルの窓の下縁の 45 度の面取りが"
                     f"平行に向き合う位置（{slope_stop_gap:.1f}mm）。設計値より広く、画素が +3 を超えて浮く余裕が大きい（隙間が詰まる側ではない）"),
            "tableHeightRangeMm": [min(min(min(row) for row in table) for table in PT.TABLES),
                                   max(max(max(row) for row in table) for table in PT.TABLES)],
            "method": ("画素 1 つだけを +Z（+3 の姿勢）と -Z（-3 の姿勢）へ動かし、ベゼル・案内板との共通体積が床を超える最初の移動量を二分探索。"
                       "ベゼルを 200mm 退避した負例で接触が消えること。"),
            "pass": all(row["pass"] for row in rows)}


def part_calibration(meter, scene):
    """実部品での校正（原型 STL を読んだ直後、測定の前）。
    - 画素を案内板の角穴の隙間（片側 0.2）の内（0.1mm）と外（0.3mm）へ動かす: 内は 0、外は床を超える体積
    - 設計した重なり以外が床を超えた組、設計した重なりの場所外・量外を、classify_interference が違反にする"""
    identity = np.eye(4)
    pixel, plate = scene.solids["pixel_2_2"], scene.solids["guide_plate"]
    inside = meter.common(pixel, translation_np(0.1), plate, identity)[0]
    outside = meter.common(pixel, translation_np(0.3), plate, identity)[0]
    # 外へ 0.3mm: 角穴 9.4 に茎 9.0。重なりは 0.1mm x 茎の側面（9 x 板の厚み内の茎の長さ）> 0
    row = {"parts": ["a", "b"], "constantRelativePose": False, "poses": 1, "aabbZero": 0, "topologyZero": 0, "boolean": 1,
           "maximumCommonVolumeMm3": 0.01, "maximumAtServoDeg": 90.0, "maximumComponentsMm": [[[0, 0, 0], [1, 1, 1]]], "posesOverFloor": 1}
    rows = {("a", "b"): dict(row), ("c", "d"): dict(row, parts=["c", "d"])}
    spec = {("c", "d"): {"kind": "calibration", "regions": [[[0, 0, 0], [1, 1, 1]]], "components": 1, "theoryMm3": 0.01,
                         "minMm3": 0.009, "maxMm3": 0.011, "basis": "校正"}}
    designed, violations = classify_interference(rows, spec, {"regions": [], "maxMm3": 0.0, "kind": "x", "basis": "x"})
    outside_region = {("c", "d"): dict(rows[("c", "d")], maximumComponentsMm=[[[5, 5, 5], [6, 6, 6]]], parts=["c", "d"])}
    _, violations_region = classify_interference(outside_region, spec, {"regions": [], "maxMm3": 0.0, "kind": "x", "basis": "x"})
    too_much = {("c", "d"): dict(rows[("c", "d")], maximumCommonVolumeMm3=0.5, parts=["c", "d"])}
    _, violations_amount = classify_interference(too_much, spec, {"regions": [], "maxMm3": 0.0, "kind": "x", "basis": "x"})
    result = {"pixelInsideClearance0.1mmMm3": inside, "pixelPastClearance0.3mmMm3": outside,
              "undesignedOverlapFlagged": [v["parts"] for v in violations] == [["a", "b"]],
              "designedOverlapAccepted": [d["parts"] for d in designed] == [["c", "d"]],
              "designedOverlapOutsideRegionFlagged": len(violations_region) == 1,
              "designedOverlapOverLimitFlagged": len(violations_amount) == 1}
    result["pass"] = bool(inside <= VOLUME_FLOOR_MM3 and outside > 10 * VOLUME_FLOOR_MM3 and result["undesignedOverlapFlagged"]
                          and result["designedOverlapAccepted"] and result["designedOverlapOutsideRegionFlagged"]
                          and result["designedOverlapOverLimitFlagged"])
    return result


# =============================================================================================
# 入力 STL の検査（全辺の 2 面共有・向き・自己交差）
# =============================================================================================
def run_boolean_evidence():
    """tools/lattice_boolean_evidence.py の検査器をこのモデルへ適用し、build/boolean_evidence.json を書く"""
    tool_path = ROOT / "tools" / "lattice_boolean_evidence.py"
    spec = importlib.util.spec_from_file_location("lattice_boolean_evidence_tpc", tool_path)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    calibration = tool.calibration()
    if not all(row["pass"] for row in calibration):
        raise SystemExit("boolean evidence calibration failed before STL inspection")
    tool.MODELS["tpc"] = HERE
    output, summary = tool.model_report("tpc")
    report = json.loads(Path(output).read_text(encoding="utf-8"))
    report["wrapperSha256"] = {Path(__file__).relative_to(ROOT).as_posix(): sha256(__file__)}
    report["selfIntersectionLimit"] = ("共有頂点を持つ三角形は隣接面として自己交差検査から除く。"
                                       "共有頂点の内部で起きる折り返しは対象外")
    classification = classify_input_integrity(tool, report)
    report["classification"] = classification
    write_json(Path(output), report)
    return report, summary, classification


def classify_input_integrity(tool, report):
    """既存の検査器の結果を、閉じていない・向きの誤り（MANIFOLD の入力として不可）、実体のある自己交差、接するだけの交差、零面積に分ける。
    自己交差は検査器が保存する例（先頭 20 件）ではなく、該当する STL を再検査して全件の交差の長さ・重なり面積で分類する。
    実体がある = 交差線の長さが 0.001mm を超えるか、同一平面の重なりが 1e-6mm2 を超える。
    正本（stock）の SG92R は印刷部品ではないので別に数える"""
    manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
    stock = {part["id"] for part in manifest["parts"] if part.get("stock")}
    hard, real_ours, real_stock, touching, zero_area = [], [], [], [], []
    for group in ("assemblyStls", "printStls"):
        for row in report[group]:
            name = row["id"]
            label = f"{'組立' if group == 'assemblyStls' else '印刷'}:{name}"
            if (row["edgesNotUsedTwice"] or row["sharedEdgesWithSameDirection"] or not row["outwardOriented"]
                    or row["duplicateTriangles"]):
                hard.append({"part": label, "edgesNotUsedTwice": row["edgesNotUsedTwice"],
                             "sharedEdgesWithSameDirection": row["sharedEdgesWithSameDirection"],
                             "outwardOriented": row["outwardOriented"], "duplicateTriangles": row["duplicateTriangles"]})
            if row["zeroAreaTriangles"]:
                zero_area.append({"part": label, "zeroAreaTriangles": row["zeroAreaTriangles"]})
            if not row["properNonadjacentIntersections"]:
                continue
            triangles = tool.read_stl(ROOT / row["path"])
            found = tool.self_intersections(*tool.indexed_mesh(triangles))
            lengths = [item.get("intersectionLengthMm", 0.0) for item in found]
            areas = [item.get("overlapAreaMm2", 0.0) for item in found]
            real = [item for item in found if item.get("intersectionLengthMm", 0.0) > 1e-3
                    or item.get("overlapAreaMm2", 0.0) > 1e-6]
            entry = {"part": label, "pairs": len(found), "realPairs": len(real),
                     "maximumLengthMm": max(lengths, default=0.0), "maximumCoplanarOverlapMm2": max(areas, default=0.0),
                     "examplePointsMm": [[round(c, 4) for c in point] for item in real[:2] for point in item.get("pointsMm", [])[:1]]}
            if real:
                (real_stock if name in stock else real_ours).append(entry)
            else:
                touching.append(entry)
    return {
        "hardFailures": hard, "realSelfIntersectionsInOurParts": real_ours, "realSelfIntersectionsInStockReference": real_stock,
        "touchingOnlyIntersections": touching, "zeroAreaTriangleParts": zero_area,
        "rule": ("全辺が 2 面で共有され向きが外向きであること（MANIFOLD の入力条件）と、実体のある自己交差が無いこと。"
                 "零面積の三角形は体積に寄与しないので数えるが、不合格にはしない"),
        "pass": bool(not hard and not real_ours)}


# =============================================================================================
# 本体
# =============================================================================================
def main():
    started = time.time()
    meter = Meter()
    log = lambda text: print(text, flush=True)
    log("校正")
    calibration = meter_calibration(meter)
    if not calibration["pass"]:
        failed = [key for key, row in calibration.items() if isinstance(row, dict) and not row.get("pass", True)]
        write_json(BUILD / "verify_report.json", {"version": 1, "model": "tangible-pixel-cube",
                                                   "calibration": calibration, "overall": {"pass": False, "failures": ["計器の校正に失敗: " + ", ".join(failed)]}})
        raise SystemExit("calibration failed before prototype STL inspection: " + ", ".join(failed))
    log("入力 STL の検査")
    evidence, evidence_summary, classification = run_boolean_evidence()
    input_pass = bool(evidence_summary["calibrationPass"] and not evidence_summary["missingFiles"]
                      and classification["pass"])
    scene = Scene()
    calibration["realPartDetection"] = part_calibration(meter, scene)
    if not calibration["realPartDetection"]["pass"]:
        failed = ["realPartDetection"]
        write_json(BUILD / "verify_report.json", {"version": 1, "model": "tangible-pixel-cube",
                                                   "calibration": calibration, "overall": {"pass": False, "failures": ["実部品での校正に失敗"]}})
        raise SystemExit("part calibration failed: " + ", ".join(failed))
    stl_paths = [BUILD / f"{name}.stl" for name in scene.names]
    start_hashes = source_hashes(stl_paths)
    log("姿勢の整合")
    consistency = motion_consistency(scene)
    log("全組・全サーボ角の干渉")
    rows = interference_sweep(meter, scene, SERVO_DEGS, log)
    specs = designed_overlaps(scene)
    canonical = canonical_servo_allowance()
    designed, violations = classify_interference(rows, specs, canonical)
    present_specs = {tuple(row["parts"]) for row in designed}
    missing_designed = [list(key) for key in sorted(specs) if key not in present_specs]
    for key in missing_designed:
        violations.append({"parts": key, "reason": "設計した潰しリブの重なりが無い（リブが効かない）"})
    designed_keys = {tuple(row["parts"]) for row in designed}
    below_floor = [{"parts": row["parts"], "maximumCommonVolumeMm3": row["maximumCommonVolumeMm3"],
                    "atServoDeg": row["maximumAtServoDeg"], "posesOverFloor": row["posesOverFloor"],
                    "componentsMm": row["maximumComponentsMm"][:3]}
                   for key, row in sorted(rows.items(), key=lambda item: -item[1]["maximumCommonVolumeMm3"])
                   if 0.0 < row["maximumCommonVolumeMm3"] <= VOLUME_FLOOR_MM3 and key not in designed_keys]
    non_designed_max = max((row["maximumCommonVolumeMm3"] for key, row in rows.items() if key not in designed_keys), default=0.0)
    log("省略と Boolean の一致")
    agreement = prefilter_agreement(meter, scene, [10.0, 30.0, 50.0, 70.0, 90.0, 110.0, 130.0, 150.0, 170.0], log)
    pair_poses = sum(row["poses"] for row in rows.values())
    interference = {
        "servoDegs": [SERVO_DEGS[0], SERVO_DEGS[-1]], "stepDeg": 1.0, "poseCount": len(SERVO_DEGS),
        "parts": len(scene.names), "excludedJigs": list(JIG_PARTS),
        "uniquePairs": len(rows), "expectedUniquePairs": len(scene.names) * (len(scene.names) - 1) // 2,
        "pairPoseEvaluations": pair_poses,
        "aabbZeroEvaluations": sum(row["aabbZero"] for row in rows.values()),
        "topologyZeroEvaluations": sum(row["topologyZero"] for row in rows.values()),
        "booleanEvaluations": sum(row["boolean"] for row in rows.values()),
        "pairsWithConstantRelativePose": sum(1 for row in rows.values() if row["constantRelativePose"]),
        "volumeFloorMm3": VOLUME_FLOOR_MM3,
        "designedOverlaps": designed,
        "belowFloorContacts": below_floor,
        "maximumNonDesignedCommonVolumeMm3": non_designed_max,
        "violations": violations,
        "prefilterAgreement": agreement,
        "method": ("全部品（治具を除く）の全組を、サーボ 10〜170 度の 1 度刻み（161 姿勢）で測る。同じ軸・同じ静止群の部品どうしは相対姿勢が"
                   "変わらないので 1 姿勢。外接箱が離れた組は共通体積 0。重なる組は BVH で表面の交差を調べ、交差も入れ子も無ければ 0、"
                   "それ以外は Blender Boolean MANIFOLD で共通体積を測る。許すのは設計した潰しリブ（場所・個数・量を限定）と、"
                   "正本 SG92R 本体とホーンの重なりだけ。"),
        "pass": bool(not violations and agreement["pass"])}
    log("カムと画素の足")
    camfoot = cam_foot_check(scene, log)
    log("画素の上下の限界")
    limits = pixel_limits(meter, scene)
    end_hashes = source_hashes(stl_paths)
    integrity = {"startHashes": len(start_hashes), "endHashes": len(end_hashes), "pass": start_hashes == end_hashes}
    sources = [HERE / name for name in ("params.py", "kinematics.py", "patterns.py", "verify.py")]
    sources.extend((BUILD / "manifest.json", BUILD / "motion.json", ROOT / "lib/solid_volume.py",
                    ROOT / "tools/lattice_boolean_evidence.py", ROOT / "models/sg92r-photo/params.py"))
    failures = []
    if not input_pass:
        failures.append("入力 STL の検査が不合格（実体のある自己交差: "
                        + ", ".join(entry["part"] for entry in classification["realSelfIntersectionsInOurParts"]) + "）")
    if not consistency["pass"]:
        failures.append("motion.json の姿勢が params から作った姿勢と一致しない")
    if not interference["pass"]:
        failures.append("干渉: 設計した重なり以外の共通体積、または省略の不一致がある")
    if not camfoot["pass"]:
        failures.append("カムと足: 食い込み・浮き・載っている部品・表の高さのいずれかが範囲外")
    if not limits["pass"]:
        failures.append("画素の上下の限界の隙間が設計値と合わない")
    if not integrity["pass"]:
        failures.append("検証中に STL が変わった")
    report = {
        "version": 1, "model": "tangible-pixel-cube",
        "calibration": calibration,
        "inputIntegrity": {"booleanEvidence": "build/boolean_evidence.json", "summary": evidence_summary,
                           "classification": classification, "pass": input_pass},
        "motionConsistency": consistency,
        "interference": interference, "camFoot": camfoot, "pixelLimits": limits,
        "sourceIntegrity": integrity,
        "overall": {"pass": not failures, "failures": failures,
                    "elapsedSeconds": round(time.time() - started, 1),
                    "booleanCalls": meter.stats["boolean"]},
        "computedByGeometry": [
            "全部品の組 x サーボ 10〜170 度の共通体積（設計した潰しリブ以外は床 0.001mm3 以下）",
            "画素の足の下面と、実カム STL の最高点の差（食い込み・浮き）と、載っている部品の特定",
            "停止角での画素の高さが表どおりか",
            "画素の上限・下限の隙間（ベゼル・案内板）"],
        "hardwareUnknown": [
            "潰しリブの実際の潰れ代と回転ガタ（印刷公差・クリープ）",
            "PLA/PETG の摩擦係数と足がカムを滑るときの実際の力",
            "SG92R の出力スプラインとホーンの嵌合（正本に歯が無い）",
            "印刷収縮による隙間の増減"],
        "sourceHashes": source_hashes(p for p in sources if p.exists()) | end_hashes,
    }
    write_json(BUILD / "verify_report.json", report)
    log(json.dumps({"pass": not failures, "failures": failures, "elapsed": round(time.time() - started, 1)}, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
