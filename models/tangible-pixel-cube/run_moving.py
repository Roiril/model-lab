"""動く部品の単独確認。シーンを消して parts_moving.build_moving() を呼び、部品ごとに STL と検査値を書く。
実行: "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python-exit-code 1 --python models/tangible-pixel-cube/run_moving.py
出力: build/moving_check/<id>.stl（組立姿勢、mm）、print_<id>.stl（刷る向き、最下点 z = 0、XY は外接の中心が原点）、report.json
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../.."))
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.path.insert(0, HERE)

import bmesh  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Euler, Matrix, Vector  # noqa: E402

from blender_utils import clear_scene  # noqa: E402
from printmech.geometry import boolean, nonmanifold, volume  # noqa: E402
import kinematics as K  # noqa: E402
import params as P  # noqa: E402
import parts_moving as PM  # noqa: E402

OUT = os.path.join(HERE, "build", "moving_check")
OVERHANG_TOL_DEG = 0.25                            # 45 度ちょうどの面（面取り・円錐）が、float32 の丸めで 45 度をわずかに割って見える分の許容（度）
OVERHANG_COS = math.cos(math.radians(45.0 - OVERHANG_TOL_DEG))   # これより寝た下向き面（水平から 44.75 度未満）を張り出しに数える


def write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def export_stl(ob, path):
    """ob だけを mm で書く（ob は m 単位、移動・回転は焼き込み済み）"""
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True, global_scale=1000.0)


def stl_zero_area(path):
    """書き出した STL（バイナリ）の零面積（ZERO_AREA_MM2 未満）または辺が SHORT_EDGE_MM 未満の三角形の数"""
    import struct
    with open(path, "rb") as f:
        b = f.read()
    n = struct.unpack("<I", b[80:84])[0]
    a = np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))["v"].astype(float)
    area = 0.5 * np.linalg.norm(np.cross(a[:, 1] - a[:, 0], a[:, 2] - a[:, 0]), axis=1)
    short = np.zeros(len(a), dtype=bool)
    for k in range(3):
        short |= np.linalg.norm(a[:, (k + 1) % 3] - a[:, k], axis=1) < SHORT_EDGE_MM
    return int(((area < ZERO_AREA_MM2) | short).sum())


# --- 検査 --------------------------------------------------------------------------------------------
def components(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    unseen = set(bm.verts)
    n = 0
    while unseen:
        n += 1
        stack = [unseen.pop()]
        while stack:
            v = stack.pop()
            for e in v.link_edges:
                o = e.other_vert(v)
                if o in unseen:
                    unseen.remove(o)
                    stack.append(o)
    bm.free()
    return n


def bbox_mm(me, mat=None):
    co = np.array([(mat @ v.co) if mat is not None else v.co for v in me.vertices], dtype=float) * 1000.0
    return co.min(axis=0), co.max(axis=0)


def rotated_print_mesh(ob, euler_deg):
    """ob のメッシュを euler で回し、最下点 z = 0、XY は外接の中心が原点になるように動かしたコピー（m）を返す"""
    rot = Euler([math.radians(a) for a in euler_deg], "XYZ").to_matrix().to_4x4()
    me = ob.data.copy()
    me.transform(rot)
    lo, hi = bbox_mm(me)
    me.transform(Matrix.Translation(Vector((-(lo[0] + hi[0]) / 2e3, -(lo[1] + hi[1]) / 2e3, -lo[2] / 1e3))))
    me.update()
    return me


def overhang(me, bridged=None):
    """刷る向きのメッシュ（m）の、水平から 45 度より寝た下向き面の面積（mm2）。ベッドに接する面は除く。
    bridged = (z_mm, r_mm, cx_mm, cy_mm): 円盤とリブで支えた端面（水平な下向き面で、高さ z、中心から半径 r 以内）は別に数える。
    返り値: (面積（bridged を除く）, 場所の一覧) か、bridged を渡したときは (面積, 場所の一覧, bridged の面積)。
    場所 = 高さごと（水平面）または傾き面の塊 {z_mm, area_mm2, bbox_mm}"""
    zmin = min(v.co.z for v in me.vertices)
    total = 0.0
    bridged_area = 0.0
    groups = {}
    for p in me.polygons:
        nz = p.normal.z
        if nz >= -OVERHANG_COS:
            continue
        zs = [me.vertices[i].co.z for i in p.vertices]
        if nz < -0.999 and max(zs) - zmin < 1e-6:
            continue                                    # ベッドに接する面
        a = p.area * 1e6
        c = p.center * 1000.0
        if bridged is not None and nz < -0.999 and abs(c.z - bridged[0]) < 0.02 and math.hypot(c.x - bridged[2], c.y - bridged[3]) <= bridged[1]:
            bridged_area += a
            continue
        total += a
        key = ("flat", round(c.z, 1)) if nz < -0.999 else ("slope", round(math.degrees(math.acos(min(1.0, -nz))), 0))   # 傾き = 法線と真下の角 = 水平からの角
        g = groups.setdefault(key, {"area": 0.0, "lo": [1e9] * 3, "hi": [-1e9] * 3})
        g["area"] += a
        for i in p.vertices:
            co = me.vertices[i].co * 1000.0
            for k in range(3):
                g["lo"][k] = min(g["lo"][k], co[k])
                g["hi"][k] = max(g["hi"][k], co[k])
    out = []
    for (kind, val), g in sorted(groups.items(), key=lambda kv: -kv[1]["area"]):
        out.append({"kind": kind, "z_mm" if kind == "flat" else "angle_from_horizontal_deg": val,
                    "area_mm2": round(g["area"], 3),
                    "bbox_mm": [[round(x, 2) for x in g["lo"]], [round(x, 2) for x in g["hi"]]]})
    if bridged is not None:
        return total, out, bridged_area
    return total, out


# --- メッシュの欠陥: 自己交差（共有頂点のない三角形どうしの交差）と零面積の三角形 ------------------------------------------
ZERO_AREA_MM2 = 1e-6                                 # これ未満の三角形は零面積
SHORT_EDGE_MM = 1e-4                                 # これ未満の辺を持つ三角形（頂点が潰れている）も零面積と同じ欠陥として数える
TOL = 1e-6                                           # 辺が三角形の内部を貫く判定の余裕（重心座標・線分の割合）
COPLANAR_MM = 1e-5                                   # 同一平面とみなす距離（mm）


def _seg_tri(p, q, a, b, c):
    """線分 pq（行ごと）が三角形 abc の内部（余裕 TOL）を貫くか。すべて (K, 3) の配列"""
    e1, e2, d = b - a, c - a, q - p
    h = np.cross(d, e2)
    det = (e1 * h).sum(axis=1)
    ok = np.abs(det) >= 1e-14
    f = 1.0 / np.where(ok, det, 1.0)
    s_ = p - a
    u = f * (s_ * h).sum(axis=1)
    qv = np.cross(s_, e1)
    v = f * (d * qv).sum(axis=1)
    t = f * (e2 * qv).sum(axis=1)
    return ok & (u >= TOL) & (u <= 1 - TOL) & (v >= TOL) & (u + v <= 1 - TOL) & (t > TOL) & (t < 1 - TOL)


def _clip_area(tri_a, tri_b, n):
    """同一平面の 2 つの三角形の重なる面積（n は法線。投影して Sutherland-Hodgman）"""
    ax = int(np.argmax(np.abs(n)))
    keep = [i for i in range(3) if i != ax]
    A = [tuple(v[keep]) for v in tri_a]
    B = [tuple(v[keep]) for v in tri_b]

    def area(poly):
        return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    if area(A) < 0:
        A = A[::-1]
    poly = B
    for i in range(3):
        a, b = A[i], A[(i + 1) % 3]
        out = []
        for k in range(len(poly)):
            p, q = poly[k], poly[(k + 1) % len(poly)]
            sp = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
            sq = (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
            if sp >= 0:
                out.append(p)
            if (sp >= 0) != (sq >= 0):
                t = sp / (sp - sq)
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        poly = out
        if not poly:
            return 0.0
    return abs(area(poly))


def mesh_defects(me, scale=1.0):
    """メッシュ（scale 倍して mm にする）の (自己交差の組の数, 零面積の三角形の数)。三角形化したうえで、頂点を共有しない三角形どうしが
    交差する組（辺が相手の内部を貫く、または同一平面で重なる）を数える"""
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.transform(bm, matrix=Matrix.Scale(scale, 4), verts=bm.verts)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    co = np.array([v.co[:] for v in bm.verts], dtype=float)
    tris = np.array([[v.index for v in f.verts] for f in bm.faces], dtype=int)
    bm.free()
    # 箱の重なりで候補を絞る（BVH の overlap は同一平面の重なりを返さないので自前）。X の下端で並べて、X が重なる範囲だけ見る（掃引）
    lo = np.minimum(np.minimum(co[tris[:, 0]], co[tris[:, 1]]), co[tris[:, 2]]) - COPLANAR_MM
    hi = np.maximum(np.maximum(co[tris[:, 0]], co[tris[:, 1]]), co[tris[:, 2]]) + COPLANAR_MM
    srt = np.argsort(lo[:, 0], kind="stable")
    lo_s, hi_s = lo[srt], hi[srt]
    ends = np.searchsorted(lo_s[:, 0], hi_s[:, 0], side="right")
    pl = []
    for a in range(len(srt) - 1):
        e = ends[a]
        if e <= a + 1:
            continue
        m = (lo_s[a + 1:e, 1:] <= hi_s[a, 1:]).all(axis=1) & (hi_s[a + 1:e, 1:] >= lo_s[a, 1:]).all(axis=1)
        idx = np.nonzero(m)[0] + a + 1
        if len(idx):
            pl.append(np.stack([np.full(len(idx), srt[a]), srt[idx]], axis=1))
    pairs = np.concatenate(pl) if pl else np.zeros((0, 2), dtype=int)
    A, B, C = co[tris[:, 0]], co[tris[:, 1]], co[tris[:, 2]]
    nrm = np.cross(B - A, C - A)
    area = 0.5 * np.linalg.norm(nrm, axis=1)
    short = ((np.linalg.norm(B - A, axis=1) < SHORT_EDGE_MM) | (np.linalg.norm(C - B, axis=1) < SHORT_EDGE_MM)
             | (np.linalg.norm(A - C, axis=1) < SHORT_EDGE_MM))
    zero = int(((area < ZERO_AREA_MM2) | short).sum())
    nrm_u = nrm / np.maximum(np.linalg.norm(nrm, axis=1), 1e-30)[:, None]
    if len(pairs) == 0:
        return 0, zero
    I, J = pairs[:, 0], pairs[:, 1]
    sh = np.zeros(len(pairs), dtype=bool)
    for a in range(3):
        for b in range(3):
            sh |= tris[I, a] == tris[J, b]
    I, J = I[~sh], J[~sh]
    live = (area[I] >= ZERO_AREA_MM2) & (area[J] >= ZERO_AREA_MM2)
    I, J = I[live], J[live]
    eps = COPLANAR_MM

    def dist(src, dst):
        return np.stack([((co[tris[dst, k]] - A[src]) * nrm_u[src]).sum(axis=1) for k in range(3)], axis=1)
    dj, di = dist(I, J), dist(J, I)                                  # J の頂点から I の平面まで、I の頂点から J の平面まで
    apart = ((dj > eps).all(axis=1) | (dj < -eps).all(axis=1) | (di > eps).all(axis=1) | (di < -eps).all(axis=1))
    coplanar = (np.abs(dj) <= eps).all(axis=1) & (np.abs(di) <= eps).all(axis=1)
    count = 0
    keep = ~apart
    # 同一平面の組: 平面へ投影して、分離軸（両方の辺の法線 6 本）が無ければ重なる（余裕 1e-5mm 未満の接触は重なりとしない）
    ci, cj = I[keep & coplanar], J[keep & coplanar]
    if len(ci):
        ax = np.argmax(np.abs(nrm_u[ci]), axis=1)
        drop = ax[:, None] == np.arange(3)[None, :]
        sel = np.where(drop, False, True)                                     # (K, 3) 残す 2 軸
        order = np.argsort(~sel, axis=1, kind="stable")[:, :2]                # 残す 2 軸の番号
        pi = np.stack([co[tris[ci, k]] for k in range(3)], axis=1)            # (K, 3, 3)
        pj = np.stack([co[tris[cj, k]] for k in range(3)], axis=1)
        pi = np.take_along_axis(pi, order[:, None, :].repeat(3, axis=1), axis=2)
        pj = np.take_along_axis(pj, order[:, None, :].repeat(3, axis=1), axis=2)
        overlap = np.ones(len(ci), dtype=bool)
        for poly in (pi, pj):
            for k in range(3):
                e = poly[:, (k + 1) % 3] - poly[:, k]
                n2 = np.stack([e[:, 1], -e[:, 0]], axis=1)
                n2 /= np.maximum(np.linalg.norm(n2, axis=1), 1e-30)[:, None]
                ri = (pi * n2[:, None, :]).sum(axis=2)
                rj = (pj * n2[:, None, :]).sum(axis=2)
                gap = np.maximum(rj.min(axis=1) - ri.max(axis=1), ri.min(axis=1) - rj.max(axis=1))
                overlap &= gap < -1e-5
        count += int(overlap.sum())
    ni, nj = I[keep & ~coplanar], J[keep & ~coplanar]
    if len(ni):
        ti = [co[tris[ni, k]] for k in range(3)]
        tj = [co[tris[nj, k]] for k in range(3)]
        hit = np.zeros(len(ni), dtype=bool)
        for k in range(3):
            hit |= _seg_tri(ti[k], ti[(k + 1) % 3], *tj)
            hit |= _seg_tri(tj[k], tj[(k + 1) % 3], *ti)
        count += int(hit.sum())
    return count, zero


# --- 校正: 答えの分かる形で overhang() を確かめる -----------------------------------------------------------
def _profile_solid(profile, length, name):
    """(y, z) の輪郭を X に length 押し出した閉じた立体（m）"""
    from printmech.geometry import prism
    ob = prism(profile, "x", 0.0, length, name)
    ob.data.transform(Matrix.Scale(0.001, 4))
    ob.data.update()
    return ob


def calibrate_overhang():
    """45 度ちょうどの面取り = 0、水平の張り出し = 面積が出る、40・44 度（寝ている）= 出る、44.9・50 度（立っている）= 0"""
    length = 20.0
    cases = {}
    t40, t50 = math.tan(math.radians(40.0)), math.tan(math.radians(50.0))
    t44, t449 = math.tan(math.radians(44.0)), math.tan(math.radians(44.9))
    shapes = {
        "chamfer_45": ([(0, 0), (10, 0), (10, 5), (15, 10), (15, 12), (-5, 12), (-5, 10), (0, 5)], 0.0),
        "ledge_horizontal": ([(0, 0), (10, 0), (10, 10), (15, 10), (15, 12), (-5, 12), (-5, 10), (0, 10)], 2 * 5.0 * length),
        "slope_40": ([(0, 0), (10, 0), (10, 5), (15, 5 + 5 * t40), (15, 14), (-5, 14), (-5, 5 + 5 * t40), (0, 5)],
                     2 * (5.0 / math.cos(math.radians(40.0))) * length),
        "slope_50": ([(0, 0), (10, 0), (10, 5), (15, 5 + 5 * t50), (15, 14), (-5, 14), (-5, 5 + 5 * t50), (0, 5)], 0.0),
        "slope_44": ([(0, 0), (10, 0), (10, 5), (15, 5 + 5 * t44), (15, 14), (-5, 14), (-5, 5 + 5 * t44), (0, 5)],
                     2 * (5.0 / math.cos(math.radians(44.0))) * length),                       # 許容 0.25 度の外（44 度）は数える
        "slope_44.9": ([(0, 0), (10, 0), (10, 5), (15, 5 + 5 * t449), (15, 14), (-5, 14), (-5, 5 + 5 * t449), (0, 5)], 0.0),   # 許容の内（丸めの分）は数えない
    }
    for name, (prof, expect) in shapes.items():
        ob = _profile_solid(prof, length, "cal_" + name)
        me = ob.data
        area, _ = overhang(me)
        cases[name] = {"expected_mm2": round(expect, 3), "measured_mm2": round(area, 3), "ok": abs(area - expect) < 0.01}
        PM.drop(ob)
    return cases


# --- ホーンの逆向きを形で通さないことの確認 -------------------------------------------------------------------
def _intersect_volume(coupler, horn, mat):
    """受け（mm）と、mat で動かした付属ホーン（mm）の共通体積（mm3）"""
    a = coupler.copy()
    a.data = coupler.data.copy()
    bpy.context.collection.objects.link(a)
    b = horn.copy()
    b.data = horn.data.copy()
    b.data.transform(mat)
    b.data.update()
    bpy.context.collection.objects.link(b)
    boolean(a, b, "INTERSECT")
    v = volume(a) if len(a.data.polygons) else 0.0
    PM.drop(a)
    return v


def check_horn_rejection():
    coupler = PM.build_horn_coupler()
    horn = PM.horn_solid()
    x_mid = P.RECV_HUB_X0 * 1000.0 + 0.1 + P.SG.HORN_ARM_T * 1000.0 / 2          # 腕の厚みの中央
    res = {}
    res["correct"] = _intersect_volume(coupler, horn, Matrix.Identity(4))
    res["correct_shift_u0.1_v0.1"] = _intersect_volume(coupler, horn, Matrix.Translation((0, 0.1, 0.1)))
    res["correct_shift_u-0.1_v-0.1"] = _intersect_volume(coupler, horn, Matrix.Translation((0, -0.1, -0.1)))
    rot180 = Matrix.Rotation(math.pi, 4, "X")                                      # 軸まわりに 180 度（長腕 18 と右腕 16 が入れ替わる）
    res["rot180"] = _intersect_volume(coupler, horn, rot180)
    scan = {}
    for dv in np.arange(-3.0, 3.01, 0.5):
        scan[f"{dv:+.1f}"] = _intersect_volume(coupler, horn, Matrix.Translation((0, 0, float(dv))) @ rot180)
    res["rot180_shift_scan_v_mm"] = scan
    res["rot180_min_over_scan"] = min(scan.values())
    res["rot180_shift_+2.0"] = scan["+2.0"]
    res["rot180_shift_-2.0"] = scan["-2.0"]
    # 裏返し（長腕の軸 = Z まわりに 180 度、X を腕の中央で折り返す）。ハブがポケットの天井の上へ入る
    flip = Matrix.Translation((x_mid, 0, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation((-x_mid, 0, 0))
    res["flipped_over"] = _intersect_volume(coupler, horn, flip)
    PM.drop(coupler)
    PM.drop(horn)
    res = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in res.items()}
    res["rot180_shift_scan_v_mm"] = {k: round(v, 4) for k, v in scan.items()}
    res["rot180_min_over_scan"] = round(res["rot180_min_over_scan"], 4)
    res["pass"] = bool(res["correct"] < 0.01 and res["correct_shift_u0.1_v0.1"] < 0.01 and res["correct_shift_u-0.1_v-0.1"] < 0.01
                       and res["rot180_min_over_scan"] > 1.0 and res["flipped_over"] > 1.0)
    return res


# --- 歯の噛み合い（2D の輪郭で、全状態の食い込みと最小隙間）--------------------------------------------------------
def _sample(poly, n):
    pts = np.asarray(poly, dtype=float)
    nxt = np.roll(pts, -1, axis=0)
    seg = np.hypot(*(nxt - pts).T)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    t = np.linspace(0.0, cum[-1], n, endpoint=False)
    idx = np.searchsorted(cum, t, side="right") - 1
    f = (t - cum[idx]) / seg[idx]
    return pts[idx] + (nxt[idx] - pts[idx]) * f[:, None]


def _inside(pts, poly):
    """点群が多角形の内側か（偶奇則）"""
    poly = np.asarray(poly, dtype=float)
    x, y = pts[:, 0][:, None], pts[:, 1][:, None]
    x0, y0 = poly[:, 0][None, :], poly[:, 1][None, :]
    x1, y1 = np.roll(poly[:, 0], -1)[None, :], np.roll(poly[:, 1], -1)[None, :]
    cond = (y0 > y) != (y1 > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        xi = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
    return (cond & (x < xi)).sum(axis=1) % 2 == 1


def _rot(poly, deg, du=0.0, dv=0.0):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(c * u - s * v + du, s * u + c * v + dv) for u, v in poly]


def check_gear_mesh():
    """隣の軸の 17T どうし（中心距離 17）と、受けの 38T と中央の軸の 17T（中心距離 27.5）の噛み合い。
    各サーボ角（表の角度、平ら、使用範囲の端）で、輪郭を回して食い込む点の数と最小の隙間（mm）を数える"""
    g17, g38 = PM.chain_gear_spec(), PM.servo_gear_spec()
    o17 = PM.gear_outline(g17, P.CHAIN_TOOTH_PHASE_DEG)
    arc = P.RECV_ARC_HALF_DEG
    o38 = PM.sector_outline(g38, P.SECTOR_TOOTH_PHASE_DEG, 90.0 - arc, 90.0 + arc)
    angles = list(P.TABLE_THETA) + [P.THETA_FLAT, P.SERVO_MIN_DEG, P.SERVO_MAX_DEG, 40.0, 73.0, 107.0, 141.0]
    cd = PM.mm(P.PITCH)
    worst_pen, worst_gap, rows = 0, 1e9, []
    engaged = 0.0                                   # 状態ごとの最小隙間の最大（どの状態でも噛んでいる = 0.2 より小さい）
    for th in angles:
        for j in range(P.N - 1):
            a = _rot(o17, K.axis_angle(th, j))
            b = _rot(o17, K.axis_angle(th, j + 1), du=cd)
            sa, sb = _sample(a, 2400), _sample(b, 2400)
            pen = int(_inside(sa, b).sum() + _inside(sb, a).sum())
            gap = float(np.sqrt(((sa[:, None, :] - sb[None, :, :]) ** 2).sum(axis=2)).min())
            worst_pen = max(worst_pen, pen)
            worst_gap = min(worst_gap, gap)
            engaged = max(engaged, gap)
            rows.append({"servo_deg": th, "pair": f"{j}-{j + 1}", "penetrating_points": pen, "min_gap_mm": round(gap, 4)})
        d = K.servo_delta(th)
        a = _rot(o38, d)
        b = _rot(o17, K.axis_angle(th, 2), dv=PM.mm(P.SERVO_CD))
        sa, sb = _sample(a, 3000), _sample(b, 2400)
        pen = int(_inside(sa, b).sum() + _inside(sb, a).sum())
        gap = float(np.sqrt(((sa[:, None, :] - sb[None, :, :]) ** 2).sum(axis=2)).min())
        worst_pen = max(worst_pen, pen)
        worst_gap = min(worst_gap, gap)
        engaged = max(engaged, gap)
        rows.append({"servo_deg": th, "pair": "sector-2", "penetrating_points": pen, "min_gap_mm": round(gap, 4)})
    return {"worst_penetrating_points": worst_pen, "worst_min_gap_mm": round(worst_gap, 4), "max_state_min_gap_mm": round(engaged, 4), "backlash_per_mesh_mm": PM.mm(P.GEAR_LASH),
            "tooth_tip_width_17T_mm": round(2 * g17["ra"] * (g17["th0"] - (math.tan(math.acos(g17["rb"] / g17["ra"])) - math.acos(g17["rb"] / g17["ra"]))), 3),
            "teeth_on_sector": len(PM.sector_teeth(g38, P.SECTOR_TOOTH_PHASE_DEG, 90.0 - arc, 90.0 + arc)),
            "states": rows, "pass": bool(worst_pen == 0 and worst_gap > 0.0 and engaged < 0.2)}


# --- 嵌め合い（組立姿勢の実形状で、鍵・リブ・D 面・治具が意図どおりに効くか）---------------------------------------------
def _copy_obj(ob, mat=None):
    """ob（m）のコピーを mm にして、mat（mm の座標で書いた変換）で動かす。boolean は m の小さな座標では薄い食い込みの体積がぶれるので mm で行う"""
    c = ob.copy()
    c.data = ob.data.copy()
    c.data.transform(Matrix.Scale(1000.0, 4))
    if mat is not None:
        c.data.transform(mat)
        if mat.determinant() < 0:
            c.data.flip_normals()                        # 鏡像は面の向きが裏返る
    c.data.update()
    bpy.context.collection.objects.link(c)
    return c


def inter_mm3(a, b, mat_b=None):
    """a と、mat_b（mm）で動かした b（どちらも m のオブジェクト）の共通体積（mm3）"""
    ca, cb = _copy_obj(a), _copy_obj(b, mat_b)
    boolean(ca, cb, "INTERSECT")
    v = volume(ca) if len(ca.data.polygons) else 0.0
    PM.drop(ca)
    return v


def about_axis(j, deg, mirror=False):
    """軸 j（Y = axis_y(j)、Z = ZC、mm）まわりに deg 度回す（mirror なら先に Y を軸の面で折り返す）"""
    y, z = PM.axis_y(j), PM.ZC
    m = Matrix.Translation((0, y, z)) @ Matrix.Rotation(math.radians(deg), 4, "X")
    if mirror:
        m = m @ Matrix.Diagonal((1.0, -1.0, 1.0, 1.0))
    return m @ Matrix.Translation((0, -y, -z))


def crop_x(ob, x0, x1, name):
    """ob（m）の X が x0..x1（mm）の部分だけを切り出した新しいオブジェクト（m）。実形状のスタブ・軸受けを、本体の重い boolean なしで繰り返し使うため"""
    c = _copy_obj(ob)
    box = PM.box3(x0, x1, -200.0, 200.0, -50.0, 300.0, "crop_box")
    boolean(c, box, "INTERSECT")
    c.data.transform(Matrix.Scale(0.001, 4))
    c.data.update()
    c.name = name
    return c


def joint_scan(owner, holder, depth, j, deg=0.0, mirror=False):
    """継ぎ目の差し込み: owner（camshaft の雄スタブの切り出し）を、holder（gear_j の雌穴）へ深さ s まで差したときの共通体積 V(s)（mm3）。
    depth = 全部差した深さ（組立の姿勢）。owner を X 方向に (depth - s) だけ引き戻して測る（deg / mirror なら軸まわりの向きも変える）。
    返り値: 全部差したときの V、V が出始める深さ s0（これより浅いと隙間で入る）、擦る長さ = depth - s0"""
    base = about_axis(j, deg, mirror)

    def V(sd):
        return inter_mm3(holder, owner, Matrix.Translation((-(depth - sd), 0, 0)) @ base)
    v_full = V(depth)
    if V(0.0) > 1e-4:
        s0 = 0.0
    else:
        lo_, hi_ = 0.0, depth
        for _ in range(9):
            mid = (lo_ + hi_) / 2
            if V(mid) > 1e-4:
                hi_ = mid
            else:
                lo_ = mid
        s0 = hi_
    return v_full, s0, depth - s0


def check_fits(parts):
    """実形状どうしの共通体積（mm3、mm の座標で計算）。
    (1) 継ぎ目（camshaft_j の雄スタブ ⇔ gear_j の雌穴）の差し込み: 押し始めは隙間で入り（V = 0）、リブが擦るのは穴の最後の部分だけ。
        意図した食い込みはリブだけ（3 本 x 幅 0.6 x 潰し代 x 長さ。リブの手前の端の 45 度の傾きを含む）。
    (2) 鍵: 鏡像・60 度おきの向きは、スタブの角が穴の出っ張りに当たって口のすぐ奥で止まる。
    (3) 治具: -X の軸受けの D 面に歯が落ちる。φ0 で当たらず、ずれた向き（1 歯ずれ 21.18 度ほか）では櫛が浮く。
    (4) 継ぎ目以外で当たらない（受けと歯車、画素とカム軸）"""
    out = {}
    ok = True
    w, crush, h = PM.mm(P.HEX_RIB_W), PM.mm(P.HEX_RIB_CRUSH), PM.mm(P.HEX_RIB_H)
    gh = PM.gear_hole()
    depth = gh["depth"]                              # 穴の深さ（2.0）
    rib_len = gh["rib_len"]                           # リブの長さ（口の面取りの奥から底まで）
    clr = PM.mm(P.SHAFT_BORE_CLR)
    ramp = h                                             # 45 度の傾き（高さ h を長さ h で上がる）
    expect_v = 3 * w * (crush * (rib_len - ramp) + crush * crush / 2)       # 隙間 clr を超えた分（ramp のうち clr を超える所は 45 度の三角）
    stubs = {}
    for j in range(P.N):
        stubs[j] = crop_x(parts[f"camshaft_{j}"], PM.GEAR_X0 - 1.0, gh["x_bot"] + 0.5, f"stub_{j}")
    rows = {}
    for j in range(P.N):
        v_full, s0, rub = joint_scan(stubs[j], parts[f"gear_{j}"], depth, j)
        rows[f"camshaft_{j}->gear_{j}"] = {"insert_depth_mm": round(depth, 3), "rib_start_depth_mm": round(s0, 3), "rib_rub_length_mm": round(rub, 3),
                                           "volume_full_mm3": round(v_full, 4), "volume_expected_mm3": round(expect_v, 4)}
        # リブが擦るのは最後の rib_len 以内（手前 depth - rib_len = 0.8mm は隙間で入る）。擦り始めは傾きが隙間を超えた所
        ok &= abs(v_full - expect_v) < 0.02 and rub <= rib_len + 0.05 and s0 >= depth - rib_len + clr - 0.05 and rib_len <= PM.mm(P.JOINT_RIB_LEN) + 1e-6
    out["joints"] = rows
    out["rub_length_max_mm"] = max(r["rib_rub_length_mm"] for r in rows.values())
    out["free_insert_mm"] = min(r["rib_start_depth_mm"] for r in rows.values())
    wrong = {}
    for j in (2, 1):
        res = {}
        for k in range(1, 6):
            v_full, s0, _ = joint_scan(stubs[j], parts[f"gear_{j}"], depth, j, deg=60.0 * k)
            res[f"rot{60 * k}"] = {"volume_full_mm3": round(v_full, 3), "blocked_at_depth_mm": round(s0, 3)}
        v_full, s0, _ = joint_scan(stubs[j], parts[f"gear_{j}"], depth, j, mirror=True)
        res["mirror"] = {"volume_full_mm3": round(v_full, 3), "blocked_at_depth_mm": round(s0, 3)}
        wrong[f"camshaft_{j}->gear_{j}"] = res
        ok &= all(r["volume_full_mm3"] > 1.0 and r["blocked_at_depth_mm"] <= 0.6 for r in res.values())
    out["wrong_orientation"] = wrong
    out["wrong_min_volume_mm3"] = min(r["volume_full_mm3"] for res in wrong.values() for r in res.values())
    out["wrong_max_blocked_depth_mm"] = max(r["blocked_at_depth_mm"] for res in wrong.values() for r in res.values())
    for pc in stubs.values():
        PM.drop(pc)

    # 治具と D 面: 軸受けの切り出し（X -45.6..-43.0）と櫛。櫛の浮き = 当たりが消えるまで上げた量
    xs0, xs1 = -PM.JOURNAL_MX_END - 0.2, -PM.mm(P.PAD_X0) + 1.0
    bearings = {j: crop_x(parts[f"camshaft_{j}"], xs0, xs1, f"bearing_{j}") for j in range(P.N)}
    comb = parts["phase_comb"]

    def lift_needed(piece, mat):
        lo_, hi_ = 0.0, 8.0
        if inter_mm3(comb, piece, mat) <= 1e-4:
            return 0.0
        for _ in range(9):
            mid = (lo_ + hi_) / 2
            if inter_mm3(comb, piece, Matrix.Translation((0, 0, -mid)) @ mat) > 1e-4:
                lo_ = mid
            else:
                hi_ = mid
        return hi_
    out["comb_in_bearings_mm3"] = {f"camshaft_{j}": round(inter_mm3(comb, bearings[j]), 4) for j in range(P.N)}
    pitch_deg = 360.0 / P.CHAIN_Z
    tests = {"correct": 0.0, "+5": 5.0, "-5": -5.0, "+1tooth": pitch_deg, "-1tooth": -pitch_deg, "+2teeth": 2 * pitch_deg, "-2teeth": -2 * pitch_deg,
             "+60": 60.0, "+120": 120.0, "+180": 180.0, "-120": -120.0, "-60": -60.0}
    lift = {}
    for name, deg in tests.items():
        lift[name] = round(max(lift_needed(bearings[j], about_axis(j, deg)) for j in (0, 1, 2)), 3)
    out["comb_lift_mm"] = lift                           # D 面は左右対称（鏡像は同じ形）なので、向きの自由度は回転だけ
    wrong_keys = [k for k in lift if k not in ("correct", "+5", "-5")]
    lift_ok = lift["correct"] == 0.0 and min(lift[k] for k in wrong_keys) >= 0.1
    for pc in bearings.values():
        PM.drop(pc)

    # 継ぎ目以外で当たらない
    out["coupler_in_gear_2"] = round(inter_mm3(parts["horn_coupler"], parts["gear_2"]), 4)
    out["coupler_in_camshaft_2"] = round(inter_mm3(parts["horn_coupler"], parts["camshaft_2"]), 4)
    out["pixel_2_2_in_camshafts"] = round(max(inter_mm3(parts["pixel_2_2"], parts[f"camshaft_{j}"]) for j in range(P.N)), 4)
    out["gear_in_camshaft_same_row"] = round(max(inter_mm3(parts[f"gear_{j}"], parts[f"camshaft_{j}"]) for j in (0, 2)), 4)
    ok &= (all(v < 0.001 for v in out["comb_in_bearings_mm3"].values()) and out["coupler_in_gear_2"] < 0.001 and out["coupler_in_camshaft_2"] < 0.001
           and out["pixel_2_2_in_camshafts"] < 0.001 and lift_ok)
    out["comb_lift_pass"] = bool(lift_ok)
    out["pass"] = bool(ok)
    return out


def check_alignment(parts):
    """画素の足の中心 X = カムの板の中心 X、茎の中心 = stem_x、頭の中心 = 列の X（25 個）。カム軸の刷る向き（-X が下）"""
    foot_err = head_err = stem_err = 0.0
    z_foot_top = PM.mm(P.CAM_TOP_FLUSH) + PM.mm(P.FOOT_FLAT) + 0.01
    z_tb = PM.mm(P.CAM_TOP_FLUSH) + PM.mm(P.FOOT_H)               # 茎の下端の面（角の頂点がある）
    for j in range(P.N):
        for i in range(P.N):
            pix = parts[f"pixel_{i}_{j}"].data
            fx = [v.co.x * 1000.0 for v in pix.vertices if v.co.z * 1000.0 < z_foot_top]
            hx = [v.co.x * 1000.0 for v in pix.vertices if v.co.z * 1000.0 > PM.mm(P.FLANGE_TOP_FLUSH) + 0.01]
            tx = [v.co.x * 1000.0 for v in pix.vertices if abs(v.co.z * 1000.0 - z_tb) < 0.01]
            foot_err = max(foot_err, abs((min(fx) + max(fx)) / 2 - PM.mm(K.cam_x(i, j))))
            head_err = max(head_err, abs((min(hx) + max(hx)) / 2 - PM.mm(K.col_x(i))))
            stem_err = max(stem_err, abs((min(tx) + max(tx)) / 2 - PM.mm(K.stem_x(i, j))))
            # 茎の断面（高さ 78 の平面で切る。頂点だけで測ると、特徴（通気穴・溝）の頂点だけが拾われて細く見える）の X の範囲 = 中心 stem_x、幅 TOWER_W
            bm = bmesh.new()
            bm.from_mesh(pix)
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.078), plane_no=(0, 0, 1), clear_inner=True, clear_outer=True)
            sx = [v.co.x * 1000.0 for v in bm.verts]
            bm.free()
            stem_err = max(stem_err, abs((min(sx) + max(sx)) / 2 - PM.mm(K.stem_x(i, j))), abs((max(sx) - min(sx)) - PM.mm(P.TOWER_W)))
    rot = Euler([math.radians(a) for a in PM.PRINT_POSE["camshaft_2"]["euler_deg"]], "XYZ").to_matrix()
    up = rot @ Vector((1, 0, 0))                          # 組立の +X が刷るときどちらを向くか
    ok = (foot_err < 1e-3 and head_err < 1e-3 and stem_err < 1e-3 and up.z > 0.999)
    return {"foot_vs_cam_x_error_mm": round(foot_err, 5), "stem_vs_stem_x_error_mm": round(stem_err, 5), "head_vs_column_x_error_mm": round(head_err, 5),
            "camshaft_print_dir_of_assembly_+X": [round(c, 3) for c in up], "pass": bool(ok)}


def min_wall_thickness(me, skip_below=1e-3):
    """メッシュ（m）の最小肉厚（mm）: 各面の中心から材料の中へ光線を飛ばし、向かい側の面までの距離の最小。小さい面（面積 1e-3mm2 未満）は除く"""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    tree = BVHTree.FromBMesh(bm)
    best = (1e9, None)
    for f in bm.faces:
        if f.calc_area() * 1e6 < skip_below:
            continue
        c, n = f.calc_center_median(), f.normal
        loc, nrm, _, dist = tree.ray_cast(c - n * 1e-7, -n)
        if loc is not None and nrm.dot(n) < -0.5 and dist * 1000.0 < best[0]:       # 向かい側は反対向きの面（その外向きの法線が光線と同じ向き = -n）
            best = (dist * 1000.0, tuple(round(v * 1000.0, 2) for v in c))
    bm.free()
    return best


def _tri_arrays(ob):
    """ob（m）の頂点（mm）と三角形の配列（n-gon は三角形化したコピーで）"""
    me = ob.data.copy()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    co = np.array([v.co[:] for v in me.vertices], dtype=float) * 1000.0
    tr = np.array([[v for v in p.vertices] for p in me.polygons], dtype=int)
    bpy.data.meshes.remove(me)
    return co, tr


def check_static_clearances(parts):
    """静止部品（parts_static の実形状）との隙間。
    (1) 位相合わせ治具（組立姿勢）と外装 housing の共通体積と最短距離。
    (2) 奇数行の camshaft のすそ（胴 R5.02 より外の頂点）と -X の押さえ棒 bearing_cap_mx の最短距離。サーボ -180..170 度の全周と、軸方向の遊び ±AXIAL_DRIFT"""
    import parts_static as S
    from mathutils.bvhtree import BVHTree
    out = {}
    housing = S.build_housing()
    cap = S.build_bearing_cap(-1)
    comb = parts["phase_comb"]
    out["comb_housing_volume_mm3"] = round(inter_mm3(comb, housing), 4)
    hco, htr = _tri_arrays(housing)
    th = BVHTree.FromPolygons([tuple(v) for v in hco], [tuple(t) for t in htr])
    cco, _ = _tri_arrays(comb)
    seat = PM.ZC + PM.mm(P.PAD_TOP_ABOVE_MX)
    dmin = min(th.find_nearest(Vector(v))[3] for v in cco if abs(v[2] - seat) > 0.05)        # 耳がパッドの上面に座る面（設計した接触）は除く
    out["comb_housing_min_distance_mm"] = round(dmin, 3)               # 耳の座を除く
    kco, ktr = _tri_arrays(cap)
    tc = BVHTree.FromPolygons([tuple(v) for v in kco], [tuple(t) for t in ktr])
    drift = PM.mm(P.AXIAL_DRIFT)
    rows = {}
    worst_all = 1e9
    for j in (1, 3):
        sco, _ = _tri_arrays(parts[f"camshaft_{j}"])
        y, z = PM.axis_y(j), PM.ZC
        rad = np.hypot(sco[:, 1] - y, sco[:, 2] - z)
        skirt = np.nonzero((rad > PM.mm(P.CAMSHAFT_BODY_D) / 2 + 0.02) & (sco[:, 0] < -41.0))[0]
        best = (1e9, None)
        for dx in (-drift, 0.0, drift):
            for phi in range(-180, 180, 10):
                c, s_ = math.cos(math.radians(phi)), math.sin(math.radians(phi))
                yy, zz = sco[skirt, 1] - y, sco[skirt, 2] - z
                pts = np.stack([sco[skirt, 0] + dx, y + c * yy - s_ * zz, z + s_ * yy + c * zz], axis=1)
                for q in pts[(pts[:, 2] > z + 3.0)]:
                    d = tc.find_nearest(Vector(q))[3]
                    if d < best[0]:
                        best = (d, (dx, phi))
        rows[f"camshaft_{j}"] = {"skirt_to_cap_min_mm": round(best[0], 3), "at_axial_shift_and_phi": best[1],
                                 "skirt_most_minus_x_mm": round(float(sco[skirt][:, 0].min()), 3)}
        worst_all = min(worst_all, best[0])
    out["skirt_vs_bearing_cap_mx"] = rows
    # 軸方向の止まり: camshaft_j + gear_j（一体）を ±X へ動かしたときの、外装 housing との初接触の動き（mm）。共通体積が出始める所を二分法で探す
    hm = _copy_obj(housing)
    stops = {}
    for j in (1, 2):
        pair = [parts[f"camshaft_{j}"], parts[f"gear_{j}"]]

        def penetrates(d):
            tot = 0.0
            for ob in pair:
                c = _copy_obj(ob, Matrix.Translation((d, 0, 0)))
                ca = hm.copy()
                ca.data = hm.data.copy()
                bpy.context.collection.objects.link(ca)
                boolean(ca, c, "INTERSECT")
                tot += volume(ca) if len(ca.data.polygons) else 0.0
                PM.drop(ca)
            return tot > 1e-4
        res = {}
        for name, sign in (("minus_x", -1.0), ("plus_x", +1.0)):
            lo_, hi_ = 0.0, 1.2
            if penetrates(0.0):
                res[name] = 0.0
                continue
            if not penetrates(sign * hi_):
                res[name] = None
                continue
            for _ in range(8):
                mid = (lo_ + hi_) / 2
                if penetrates(sign * mid):
                    hi_ = mid
                else:
                    lo_ = mid
            res[name] = round(hi_, 3)
        stops[f"row_{j}"] = res
    PM.drop(hm)
    out["axial_first_contact_mm"] = stops
    contacts = [v for r in stops.values() for v in r.values()]
    contact_ok = all(v is not None and abs(v - PM.mm(P.AXIAL_DRIFT)) <= 0.05 for v in contacts)
    out["skirt_to_cap_min_mm"] = round(worst_all, 3)
    # 軸方向の止まり: -X の軸受けの端と溝の底の隙間（遊びを入れる前）。+X の肩とパッドの内面の隙間 AXIAL_DRIFT が先に決まること
    out["axial_stop"] = {"bearing_end_to_groove_bottom_mm": round(PM.mm(P.PAD_X1) + PM.mm(P.U_DIG) - PM.JOURNAL_MX_END, 3),
                         "bearing_overlap_with_slot_mm": round(PM.JOURNAL_MX_END - PM.mm(P.PAD_X0), 3),
                         "shoulder_to_pad_mm": round(PM.mm(P.PAD_X0) - PM.mm(P.SHAFT_HALF_L), 3), "design_drift_mm": PM.mm(P.AXIAL_DRIFT)}
    out["pass"] = bool(out["comb_housing_volume_mm3"] < 1e-4 and out["comb_housing_min_distance_mm"] >= 0.3 - 1e-6 and worst_all >= 0.3
                       and out["axial_stop"]["bearing_overlap_with_slot_mm"] >= 1.0 - 1e-6 and contact_ok)
    for ob in (housing, cap):
        PM.drop(ob)
    return out


def check_coupler_walls(parts):
    """受けのポケットの壁と天井の厚み（mm）。ポケットの壁の面から外へ光線を飛ばし、向かい合う面（反対向き）に当たるまでの距離"""
    from mathutils.bvhtree import BVHTree
    rc = PM.build_horn_coupler()
    bm = bmesh.new()
    bm.from_mesh(rc.data)
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    tree = BVHTree.FromBMesh(bm)
    pocket = [PM.horn_to_uv(offset) for offset in (PM.offset_convex(p, 0.03) for p in PM.horn_polys(PM.mm(P.HORN_CLR)).values())]
    x0, x1 = PM.mm(P.RECV_HUB_X0), PM.mm(P.RECV_HUB_X0) + PM.mm(P.RECV_POCKET)
    walls, ceil = [], []
    for f in bm.faces:
        c, n = f.calc_center_median(), f.normal
        if abs(n.x) < 0.2 and x0 + 0.4 < c.x < x1 - 0.05 and any(_inside(np.array([[c.y, c.z]]), poly)[0] for poly in pocket):
            origin = c - n * 1e-3                               # 材料の中へ
            loc, nrm, _, dist = tree.ray_cast(origin, -n)
            if loc is not None and nrm.dot(-n) > 0.7:           # 出口の面は光線と同じ向き（材料の外を向く）
                walls.append((dist, (round(c.y, 2), round(c.z, 2))))
        elif n.x < -0.9 and abs(c.x - x1) < 1e-3:
            loc, nrm, _, dist = tree.ray_cast(c + Vector((1e-3, 0, 0)), Vector((1, 0, 0)))
            if loc is not None:
                ceil.append((dist, (round(c.y, 2), round(c.z, 2))))
    bm.free()
    # 受けの本体（支えのピン以外）の +X 端と、+X のパッドの帯の内面（PAD_X0）の隙間。上から降りるとき帯を擦らない
    body_x1 = max(v.co.x for v in rc.data.vertices if math.hypot(v.co.y, v.co.z) > PM.mm(P.RECV_PIN_D) / 2 + 0.05)
    band_gap = PM.mm(P.PAD_X0) - body_x1
    # 受けの掃く範囲（サーボ軸まわりの半径 20.6）に回転円が掛かるカムの板（+X 面）と、受けの -X 面との X の隙間。軸方向の遊び片側 AXIAL_DRIFT を引いた値も出す
    x_min = min(v.co.x for v in rc.data.vertices)
    zs, zc = PM.ZS, PM.ZC
    cam_gap, cam_at = 1e9, None
    for j in range(P.N):
        for i in range(P.N):
            plate_x1 = PM.cam_x(i, j) + PM.CAM_T / 2
            rmax = float(np.hypot(*PM.cam_contour(i, j).T).max())
            if math.hypot(PM.axis_y(j), zc - zs) - PM.mm(P.RECV_BAR_R) - rmax < 0:       # 回転円どうしが重なりうる
                gap = x_min - plate_x1
                if gap < cam_gap:
                    cam_gap, cam_at = gap, f"camshaft_{j} cam {i}"
    PM.drop(rc)
    wmin = min(walls)
    cmin = min(ceil)
    return {"wall_min_mm": round(wmin[0] + 1e-3, 3), "wall_min_at_yz": wmin[1], "wall_samples": len(walls),
            "ceiling_min_mm": round(cmin[0], 3), "ceiling_min_at_yz": cmin[1], "ceiling_samples": len(ceil),
            "body_x1_mm": round(body_x1, 3), "gap_to_pad_band_mm": round(band_gap, 3),
            "body_x0_mm": round(x_min, 3), "min_x_gap_to_swept_cam_plate_mm": round(cam_gap, 3), "that_cam": cam_at,
            "min_x_gap_with_axial_play_mm": round(cam_gap - PM.mm(P.AXIAL_DRIFT), 3),
            "pass": bool(wmin[0] + 1e-3 >= 1.2 and cmin[0] >= 1.2 and band_gap >= 0.5)}


def check_cone_clearance(parts):
    """隣の行の camshaft どうし（Y が 17 離れる）の実形状の最短距離（mm）。サーボ 10..170 度と表の角度で、2 本を逆回りに（歯車 1:1）回し、
    B の X のずれを設計位置 0 と軸方向の遊び ±2 x AXIAL_DRIFT（片側 0.4 の 2 本分 = 0.8）で測る。
    頂点から相手の面までの距離（最も近い面の法線で内外を判定。食い込みは負）の、両方向の最小"""
    from mathutils.bvhtree import BVHTree
    thetas = sorted(set([float(t) for t in range(10, 171, 10)] + [float(t) for t in P.TABLE_THETA]))
    slack = 2 * PM.mm(P.AXIAL_DRIFT)
    shifts = (0.0, -slack, slack)
    res = {}
    mesh = {}
    for j in range(P.N):
        me = parts[f"camshaft_{j}"].data
        co = np.array([v.co[:] for v in me.vertices], dtype=float) * 1000.0
        tr = np.array([[v for v in p.vertices] for p in me.polygons if len(p.vertices) == 3], dtype=int)
        quads = [p for p in me.polygons if len(p.vertices) != 3]
        if quads:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            tr = np.array([[v.index for v in f.verts] for f in bm.faces], dtype=int)
            bm.free()
        mesh[j] = (co, tr)

    def placed(j, phi, dx):
        co, tr = mesh[j]
        y, z = PM.axis_y(j), PM.ZC
        c, s_ = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        yy, zz = co[:, 1] - y, co[:, 2] - z
        out = np.stack([co[:, 0] + dx, y + c * yy - s_ * zz, z + s_ * yy + c * zz], axis=1)
        return out

    def inside_parity(tree, q):
        """q が tree の閉じた面の内側か（2 本の光線の交点の数の偶奇。2 本とも奇数なら内側）。面の法線の向きに頼らない（辺の上では法線の判定が不定）"""
        votes = 0
        for dv in (Vector((1.0, 0.1234, 0.0567)), Vector((0.0432, 1.0, 0.3141)), Vector((0.2718, 0.0871, 1.0))):
            d = dv.normalized()
            o = q.copy()
            n = 0
            while True:
                loc, nrm, idx, dist = tree.ray_cast(o, d)
                if loc is None:
                    break
                n += 1
                o = loc + d * 1e-4
            votes += n % 2
        return votes >= 2

    def signed_min(src, tree, axis_other, others_r):
        d = np.hypot(src[:, 1] - axis_other[0], src[:, 2] - axis_other[1])
        sel = np.nonzero(d < others_r)[0]
        best = 1e9
        for k in sel:
            q = Vector(src[k])
            loc, nrm, _, dist = tree.find_nearest(q)
            if loc is None or dist >= best and dist >= 1.5:
                continue
            if dist < 1.5 and inside_parity(tree, q):
                dist = -dist
            best = min(best, dist)
        return best
    worst_all = {"nominal": (1e9, None), "slack": (1e9, None)}
    per_pair = {}
    for j in range(P.N - 1):
        pn, ps = (1e9, None), (1e9, None)
        for th in thetas:
            pa, pb = K.axis_angle(th, j), K.axis_angle(th, j + 1)
            for dx in shifts:
                A = placed(j, pa, 0.0)
                B = placed(j + 1, pb, dx)
                ta = BVHTree.FromPolygons([tuple(v) for v in A], [tuple(t) for t in mesh[j][1]], epsilon=0.0)
                tb = BVHTree.FromPolygons([tuple(v) for v in B], [tuple(t) for t in mesh[j + 1][1]], epsilon=0.0)
                reach = 13.0
                d = min(signed_min(A, tb, (PM.axis_y(j + 1), PM.ZC), reach), signed_min(B, ta, (PM.axis_y(j), PM.ZC), reach))
                if dx == 0.0:
                    if d < pn[0]:
                        pn = (d, (th, dx))
                else:
                    if d < ps[0]:
                        ps = (d, (th, dx))
        per_pair[f"{j}-{j + 1}"] = {"nominal_min_mm": round(pn[0], 3), "nominal_at_servo_deg": pn[1][0],
                                    "with_axial_play_min_mm": round(min(pn[0], ps[0]), 3), "slack_at": [ps[1][0], ps[1][1]]}
        for key, v in (("nominal", pn), ("slack", ps)):
            if v[0] < worst_all[key][0]:
                worst_all[key] = (v[0], f"pair {j}-{j + 1}")
    res["pairs"] = per_pair
    res["nominal_min_mm"] = round(worst_all["nominal"][0], 3)
    res["with_axial_play_min_mm"] = round(min(worst_all["nominal"][0], worst_all["slack"][0]), 3)
    res["design_limits_mm"] = {"nominal": PM.mm(P.CONE_CLEAR_NOMINAL), "with_axial_play": PM.mm(P.CONE_CLEAR_SLACK)}
    res["servo_angles_tested"] = thetas
    res["pass"] = bool(res["nominal_min_mm"] >= PM.mm(P.CONE_CLEAR_NOMINAL) - 0.1 and res["with_axial_play_min_mm"] >= PM.mm(P.CONE_CLEAR_SLACK) + 0.0)
    return res


def check_camshaft_print(print_parts, parts):
    """camshaft_j を -X 端を下にして立てて刷る形（刷るときだけの円盤つき）の確認: 高さ / 接地、連結成分、サポートの要らなさ（端面以外の下向き面 0）"""
    out = {}
    rows = {}
    ok = True
    td = PM.mm(P.PRINT_FOOT_T)
    gap = PM.mm(P.PRINT_FOOT_GAP)
    for j in range(P.N):
        pid = f"camshaft_{j}"
        pme = rotated_print_mesh(print_parts[pid], PM.PRINT_POSE[pid]["euler_deg"])
        zs = np.array([v.co.z for v in pme.vertices]) * 1000.0
        xy = np.array([(v.co.x, v.co.y) for v in pme.vertices]) * 1000.0
        bottom = xy[zs < 0.35]
        foot_w = float(min(np.ptp(bottom[:, 0]), np.ptp(bottom[:, 1])))
        height = float(zs.max() - zs.min())
        area, where, bridged = overhang(pme, bridged=(td + gap, PM.mm(P.CAMSHAFT_BODY_D) / 2 + 0.05, 0.0, 0.0))
        bare = rotated_print_mesh(parts[pid], PM.PRINT_POSE[pid]["euler_deg"])
        height_bare = float(max(v.co.z for v in bare.vertices) - min(v.co.z for v in bare.vertices)) * 1000.0
        width_bare = float(min(np.ptp([v.co.x for v in bare.vertices]), np.ptp([v.co.y for v in bare.vertices]))) * 1000.0
        # すその -X の端を SKIRT_X_MIN で止めた cam の、板の下面の水平な縁（下向き）。印刷の高さ z = 板の下面の X - 円盤の下面の X
        z_foot_bottom = -PM.JOURNAL_MX_END - gap - td
        ledge_z = [PM.cam_x(i, j) - PM.CAM_T / 2 - z_foot_bottom for i in range(P.N)
                   if f"{i}_{j}" in PM.INFO.get("skirt_chamfer_height_max_mm", {})] if pid == f"camshaft_{j}" else []
        ledge = sum(w["area_mm2"] for w in where if w["kind"] == "flat" and any(abs(w["z_mm"] - z) < 0.06 for z in ledge_z))
        other = area - ledge
        co_a = np.array([v.co[:] for v in parts[pid].data.vertices], dtype=float) * 1000.0
        rad = np.hypot(co_a[:, 1] - PM.axis_y(j), co_a[:, 2] - PM.ZC)
        skirt_min_x = float(co_a[rad > PM.mm(P.CAMSHAFT_BODY_D) / 2 + 0.005][:, 0].min())      # 胴（R5）より外にある材料の最も -X の位置
        rows[pid] = {"height_mm": round(height, 3), "skirt_most_minus_x_mm": round(skirt_min_x, 3),
                     "skirt_ledge_area_mm2": round(ledge, 3), "skirt_chamfer_height_max_mm": PM.INFO.get("skirt_chamfer_height_max_mm", {}), "rim_width_left_mm": PM.INFO.get("rim_width_left_mm", {}),
                     "downward_area_other_than_ledge_mm2": round(other, 4), "footprint_mm": round(foot_w, 3), "height_over_footprint": round(height / foot_w, 3),
                     "bare_height_mm": round(height_bare, 3), "bare_min_width_mm": round(width_bare, 3), "bare_ratio": round(height_bare / width_bare, 3),
                     "components": components(pme), "downward_area_excluding_foot_end_face_mm2": round(area, 4),
                     "downward_where": where, "foot_end_face_area_mm2": round(bridged, 3)}
        ok &= (height / foot_w <= 5.0 and rows[pid]["components"] == 1 and area < 1e-3 and skirt_min_x >= PM.SKIRT_X_MIN - 0.02
               and all(v >= 2.5 - 1e-6 for v in PM.INFO.get("rim_width_left_mm", {}).values()))
        bpy.data.meshes.remove(pme)
        bpy.data.meshes.remove(bare)
    out["camshafts"] = rows
    out["foot"] = {"disk_d_mm": PM.mm(P.PRINT_FOOT_D), "disk_t_mm": td, "gap_mm": gap, "ribs": P.PRINT_FOOT_RIBS, "rib_w_mm": PM.mm(P.PRINT_FOOT_RIB_W),
                   "neck_w_mm": PM.mm(P.PRINT_FOOT_NECK), "residue_after_break_mm": PM.mm(P.PRINT_FOOT_RESIDUE_MAX)}
    out["pass"] = bool(ok)
    return out


# --- 本体 --------------------------------------------------------------------------------------------------------
def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):                       # 前の構成の STL（廃止した部品）を残さない
        if f.endswith(".stl"):
            os.remove(os.path.join(OUT, f))
    clear_scene()
    report = {"units": "mm / mm2 / cm3", "calibration": {}, "parts": {}}

    # 校正（先に計器を確かめる）
    report["calibration"]["overhang_area"] = calibrate_overhang()
    cal_ok = all(c["ok"] for c in report["calibration"]["overhang_area"].values())
    print("calibration overhang:", {k: (v["expected_mm2"], v["measured_mm2"]) for k, v in report["calibration"]["overhang_area"].items()})
    if not cal_ok:
        write_json(os.path.join(OUT, "report.json"), report)
        raise RuntimeError("overhang() の校正が合わない。部品の数字を信じない")

    parts = PM.build_moving()
    variants = PM.build_print_variants()
    print(f"built {len(parts)} parts (+ {len(variants)} print variants) in {time.time() - t0:.1f}s")
    ids = PM.part_ids()
    assert sorted(parts) == sorted(ids), "build_moving() の返りが part_ids() と違う"
    assert sorted(ids) == sorted(i for i in P.PART_IDS if i in ids), "part_ids() に params.PART_IDS に無い id がある"
    assert all(i in ids for i in P.PART_IDS if not i.startswith(("housing", "bezel", "guide_plate", "sg92r", "bearing_cap"))), \
        "params.PART_IDS の動く部品が build_moving() に無い"
    bad, defects = [], []
    si_total = za_total = 0
    for pid in ids:
        ob = parts[pid]
        me = ob.data
        lo, hi = bbox_mm(me)
        export_stl(ob, os.path.join(OUT, f"{pid}.stl"))
        za_file = stl_zero_area(os.path.join(OUT, f"{pid}.stl"))
        pose = PM.PRINT_POSE[pid]
        pob_src = variants.get(pid, ob)                  # 刷る形が違う部品（円盤つきの camshaft_j）はそちら
        pme = rotated_print_mesh(pob_src, pose["euler_deg"])
        pob = bpy.data.objects.new(f"print_{pid}", pme)
        bpy.context.collection.objects.link(pob)
        export_stl(pob, os.path.join(OUT, f"print_{pid}.stl"))
        za_file += stl_zero_area(os.path.join(OUT, f"print_{pid}.stl"))
        if pid in variants:
            area, where, bridged = overhang(pme, bridged=(PM.mm(P.PRINT_FOOT_T) + PM.mm(P.PRINT_FOOT_GAP), PM.mm(P.CAMSHAFT_BODY_D) / 2 + 0.05, 0.0, 0.0))
        else:
            area, where = overhang(pme)
            bridged = None
        plo, phi = bbox_mm(pme)
        nm = nonmanifold(ob)
        cc = components(me)
        cc_print = components(pme)
        nm_print = nonmanifold(pob_src)
        si_a, za_a = mesh_defects(me, 1000.0)
        si_p, za_p = mesh_defects(pme, 1000.0)
        entry = {
            "bbox_assembly_mm": [round(float(x), 3) for x in (hi - lo)],
            "bbox_assembly_min_mm": [round(float(x), 3) for x in lo], "bbox_assembly_max_mm": [round(float(x), 3) for x in hi],
            "volume_cm3": round(volume(ob) * 1e6, 4),
            "nonmanifold_edges": nm, "components": cc, "print_nonmanifold_edges": nm_print, "print_components": cc_print,
            "self_intersections": {"assembly": si_a, "print": si_p}, "zero_area_triangles": {"assembly": za_a, "print": za_p, "stl_files": za_file},
            "faces": len(me.polygons),
            "print": {"euler_deg": list(pose["euler_deg"]), "bbox_mm": [round(float(x), 3) for x in (phi - plo)],
                      "overhang_area_mm2": round(area, 3), "overhang_where": where,
                      "foot_end_face_area_mm2": None if bridged is None else round(bridged, 3),
                      "reason": pose["reason"], "support": pose["support"]},
        }
        report["parts"][pid] = entry
        if nm or cc != 1 or nm_print or cc_print != 1:
            bad.append((pid, nm, cc, nm_print, cc_print))
        if si_a or si_p or za_a or za_p or za_file:
            defects.append((pid, si_a, si_p, za_a, za_p, za_file))
        si_total += si_a + si_p
        za_total += za_a + za_p + za_file
        bpy.data.objects.remove(pob, do_unlink=True)
        bpy.data.meshes.remove(pme)

    report["alignment"] = check_alignment(parts)
    report["camshaft_print"] = check_camshaft_print(variants, parts)
    report["fits"] = check_fits(parts)
    report["cone_clearance"] = check_cone_clearance(parts)
    report["horn_rejection"] = check_horn_rejection()
    report["coupler_walls"] = check_coupler_walls(parts)
    report["gear_mesh"] = check_gear_mesh()
    report["camshaft_label"] = PM.INFO.get("camshaft_label")
    report["comb_layout"] = PM.INFO.get("comb")
    report["static_clearances"] = check_static_clearances(parts)
    mt = min_wall_thickness(parts["phase_comb"].data)
    report["comb_min_wall_mm"] = {"thickness_mm": round(mt[0], 3), "at_xyz_mm": mt[1], "pass": bool(mt[0] >= 1.2 - 1e-6)}
    report["cam_skirt_end_x_mm"] = PM.INFO.get("cam_skirt_end_x_mm")
    report["summary"] = {
        "parts": len(ids), "all_manifold_single_component": not bad, "bad": bad,
        "self_intersections_total": si_total, "zero_area_triangles_total": za_total, "defect_parts": defects,
        "defects_pass": bool(si_total == 0 and za_total == 0),
        "overhang_calibration_ok": cal_ok, "camshaft_print_pass": report["camshaft_print"]["pass"], "comb_min_wall_mm": report["comb_min_wall_mm"]["thickness_mm"], "static_pass": report["static_clearances"]["pass"], "comb_housing_mm3": report["static_clearances"]["comb_housing_volume_mm3"], "skirt_cap_min_mm": report["static_clearances"]["skirt_to_cap_min_mm"], "cone_pass": report["cone_clearance"]["pass"], "horn_rejection_pass": report["horn_rejection"]["pass"], "fits_pass": report["fits"]["pass"], "coupler_walls_pass": report["coupler_walls"]["pass"], "alignment_pass": report["alignment"]["pass"],
        "gear_mesh_pass": report["gear_mesh"]["pass"], "seconds": round(time.time() - t0, 1),
    }
    write_json(os.path.join(OUT, "report.json"), report)
    print("summary:", json.dumps(report["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
