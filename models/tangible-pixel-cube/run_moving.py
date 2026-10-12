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
OVERHANG_COS = math.cos(math.radians(45.0))        # 45 度ちょうどの面は数えない（1e-4 の余裕）


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


def overhang(me):
    """刷る向きのメッシュ（m）の、水平から 45 度より寝た下向き面の面積（mm2）。ベッドに接する面は除く。
    返り値: (面積, 場所の一覧)。場所 = 高さごと（水平面）または傾き面の塊 {z_mm, area_mm2, bbox_mm}"""
    zmin = min(v.co.z for v in me.vertices)
    total = 0.0
    groups = {}
    for p in me.polygons:
        nz = p.normal.z
        if nz >= -OVERHANG_COS - 1e-4:
            continue
        zs = [me.vertices[i].co.z for i in p.vertices]
        if nz < -0.999 and max(zs) - zmin < 1e-6:
            continue                                    # ベッドに接する面
        a = p.area * 1e6
        total += a
        c = p.center * 1000.0
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
    # 箱の重なりで候補を絞る（BVH の overlap は同一平面の重なりを返さないので自前）
    lo = np.minimum(np.minimum(co[tris[:, 0]], co[tris[:, 1]]), co[tris[:, 2]]) - COPLANAR_MM
    hi = np.maximum(np.maximum(co[tris[:, 0]], co[tris[:, 1]]), co[tris[:, 2]]) + COPLANAR_MM
    pl = []
    for i in range(len(tris) - 1):
        m = (lo[i + 1:] <= hi[i]).all(axis=1) & (hi[i + 1:] >= lo[i]).all(axis=1)
        idx = np.nonzero(m)[0]
        if len(idx):
            pl.append(np.stack([np.full(len(idx), i), idx + i + 1], axis=1))
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
    """45 度ちょうどの面取り = 0、水平の張り出し = 面積が出る、40 度（寝ている）= 出る、50 度（立っている）= 0"""
    length = 20.0
    cases = {}
    t40, t50 = math.tan(math.radians(40.0)), math.tan(math.radians(50.0))
    shapes = {
        "chamfer_45": ([(0, 0), (10, 0), (10, 5), (15, 10), (15, 12), (-5, 12), (-5, 10), (0, 5)], 0.0),
        "ledge_horizontal": ([(0, 0), (10, 0), (10, 10), (15, 10), (15, 12), (-5, 12), (-5, 10), (0, 10)], 2 * 5.0 * length),
        "slope_40": ([(0, 0), (10, 0), (10, 5), (15, 5 + 5 * t40), (15, 14), (-5, 14), (-5, 5 + 5 * t40), (0, 5)],
                     2 * (5.0 / math.cos(math.radians(40.0))) * length),
        "slope_50": ([(0, 0), (10, 0), (10, 5), (15, 5 + 5 * t50), (15, 14), (-5, 14), (-5, 5 + 5 * t50), (0, 5)], 0.0),
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


# --- 嵌め合い（組立姿勢の実形状で、鍵・リブ・溝・治具が意図どおりに効くか）-----------------------------------------------
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


def check_fits(parts):
    """実形状どうしの共通体積（mm3、mm の座標で計算）。意図した食い込みは潰しリブだけ（3 本 x 0.18 x 0.6 x 長さ）、他は 0。
    間違った向き（60 度おき・鏡像）は、軸・治具に当たって食い込む"""
    # リブはベッド側の面取りカッター（0.3）の中を通るので、ベッド側の 0.3mm は削れて無い
    rib_cam = 3 * PM.mm(P.HEX_RIB_CRUSH) * PM.mm(P.HEX_RIB_W) * (PM.CAM_T - PM.FIRST_LAYER)
    rib_gear = 3 * PM.mm(P.HEX_RIB_CRUSH) * PM.mm(P.HEX_RIB_W) * (PM.mm(P.GEAR_T) - PM.FIRST_LAYER)
    out = {"rib_crush_expected_cam_mm3": round(rib_cam, 4), "rib_crush_expected_gear_mm3": round(rib_gear, 4)}
    out["cam_in_shaft"] = {f"cam_{i}_{j}": round(inter_mm3(parts[f"cam_{i}_{j}"], parts[f"shaft_{j}"]), 4)
                           for i, j in ((0, 0), (2, 2), (4, 4), (3, 1), (1, 3), (0, 1))}
    out["gear_in_shaft"] = {f"gear_{j}": round(inter_mm3(parts[f"gear_{j}"], parts[f"shaft_{j}"]), 4) for j in range(P.N)}
    out["clip_in_shaft"] = {f"shaft_clip_{j}": round(inter_mm3(parts[f"shaft_clip_{j}"], parts[f"shaft_{j}"]), 4) for j in range(P.N)}
    out["comb_in_shaft"] = {f"shaft_{j}": round(inter_mm3(parts["phase_comb"], parts[f"shaft_{j}"]), 4) for j in range(P.N)}
    out["coupler_in_gear_2"] = round(inter_mm3(parts["horn_coupler"], parts["gear_2"]), 4)
    out["pixel_2_2_in_cams"] = round(max(inter_mm3(parts["pixel_2_2"], parts[f"cam_{i}_{j}"]) for j in range(P.N) for i in range(P.N)), 4)
    wrong = {}
    for name, part, jj in (("cam_2_2", "cam_2_2", 2), ("gear_2", "gear_2", 2)):
        vols = {f"rot{60 * k}": inter_mm3(parts[part], parts[f"shaft_{jj}"], about_axis(jj, 60.0 * k)) for k in range(1, 6)}
        vols["mirror"] = inter_mm3(parts[part], parts[f"shaft_{jj}"], about_axis(jj, 0.0, mirror=True))
        wrong[f"{name}_on_shaft"] = {k: round(v, 3) for k, v in vols.items()}
    vols = {f"rot{60 * k}": inter_mm3(parts["phase_comb"], parts["shaft_2"], about_axis(2, 60.0 * k)) for k in range(1, 6)}
    vols["mirror"] = inter_mm3(parts["phase_comb"], parts["shaft_2"], about_axis(2, 0.0, mirror=True))
    wrong["comb_on_shaft"] = {k: round(v, 3) for k, v in vols.items()}
    out["wrong_orientation_mm3"] = wrong
    out["wrong_min_mm3"] = round(min(v for d in wrong.values() for v in d.values()), 3)
    # 治具: 間違った向きの軸は、軸の角が切り欠きの出っ張りに当たる。当たりが消えるまで櫛を上げた量（mm）= 浮き。正しい向きは 0
    def lift_needed(mat):
        lo_, hi_ = 0.0, 8.0
        if inter_mm3(parts["phase_comb"], parts["shaft_2"], mat) <= 1e-4:
            return 0.0
        for _ in range(9):
            mid = (lo_ + hi_) / 2
            if inter_mm3(parts["phase_comb"], parts["shaft_2"], Matrix.Translation((0, 0, -mid)) @ mat) > 1e-4:
                lo_ = mid
            else:
                hi_ = mid
        return hi_
    lift = {"correct": lift_needed(Matrix.Identity(4))}
    for k in range(1, 6):
        lift[f"rot{60 * k}"] = lift_needed(about_axis(2, 60.0 * k))
    lift["mirror"] = lift_needed(about_axis(2, 0.0, mirror=True))
    lift = {k: round(v, 3) for k, v in lift.items()}
    out["comb_lift_mm"] = lift
    lift_ok = lift["correct"] == 0.0 and min(v for k, v in lift.items() if k != "correct") >= 0.1
    ok = (all(abs(v - rib_cam) < 0.02 for v in out["cam_in_shaft"].values())
          and all(abs(v - rib_gear) < 0.02 for v in out["gear_in_shaft"].values())
          and all(v < 0.001 for v in out["clip_in_shaft"].values()) and all(v < 0.001 for v in out["comb_in_shaft"].values())
          and out["coupler_in_gear_2"] < 0.001 and out["pixel_2_2_in_cams"] < 0.001 and out["wrong_min_mm3"] > 0.5 and lift_ok)
    out["pass"] = bool(ok)
    return out


def check_alignment(parts):
    """画素の足の中心 X = カム板の中心 X、画素の頭の中心 X = 列の X、カム番号の向き（刷る向きで上 = 組立の +Z）の確認"""
    foot_err = head_err = 0.0
    z_foot_top = PM.mm(P.CAM_TOP_FLUSH) + PM.mm(P.FOOT_FLAT) + 0.01
    for j in range(P.N):
        for i in range(P.N):
            cam = parts[f"cam_{i}_{j}"].data
            plate_c = min(v.co.x for v in cam.vertices) * 1000.0 + PM.CAM_T / 2
            pix = parts[f"pixel_{i}_{j}"].data
            fx = [v.co.x * 1000.0 for v in pix.vertices if v.co.z * 1000.0 < z_foot_top]
            hx = [v.co.x * 1000.0 for v in pix.vertices if v.co.z * 1000.0 > PM.mm(P.FLANGE_TOP_FLUSH) + 0.01]
            foot_err = max(foot_err, abs((min(fx) + max(fx)) / 2 - plate_c))
            head_err = max(head_err, abs((min(hx) + max(hx)) / 2 - PM.mm(K.col_x(i))))
    rot = Euler([math.radians(a) for a in PM.PRINT_POSE["cam_2_2"]["euler_deg"]], "XYZ").to_matrix()
    up, right, plate_up = rot @ Vector((0, 0, 1)), rot @ Vector((0, 1, 0)), rot @ Vector((1, 0, 0))
    ok = (foot_err < 1e-3 and head_err < 1e-3 and plate_up.z > 0.999 and up.y > 0.999 and right.x > 0.999)
    return {"foot_vs_cam_x_error_mm": round(foot_err, 5), "head_vs_column_x_error_mm": round(head_err, 5),
            "cam_print_dir_of_assembly_+Z": [round(c, 3) for c in up], "cam_print_dir_of_assembly_+Y": [round(c, 3) for c in right],
            "cam_print_dir_of_assembly_+X": [round(c, 3) for c in plate_up], "pass": bool(ok)}


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
    # 受けの掃く範囲（サーボ軸まわりの半径 20.6）に、カム（回転円の半径 = 輪郭の最大）・ハブ・歯車・鍔（外接円）が掛かる部品と、受けの -X 面との X の隙間。
    # 軸の遊び 0.2 が受けへ寄る向きに効いた値も出す
    x_min = min(v.co.x for v in rc.data.vertices)
    zs, zc = PM.ZS, PM.ZC
    cam_gap, cam_at = 1e9, None
    for j in range(P.N):
        for i in range(P.N):
            cam = parts[f"cam_{i}_{j}"].data
            xs = [v.co.x * 1000.0 for v in cam.vertices]
            plate_x1 = min(xs) + PM.CAM_T
            rmax = max(math.hypot(v.co.y * 1000.0 - PM.axis_y(j), v.co.z * 1000.0 - zc) for v in cam.vertices)
            if math.hypot(PM.axis_y(j), zc - zs) - PM.mm(P.RECV_BAR_R) - rmax < 0:       # 回転円どうしが重なりうる
                gap = x_min - plate_x1
                if gap < cam_gap:
                    cam_gap, cam_at = gap, f"cam_{i}_{j}"
    PM.drop(rc)
    wmin = min(walls)
    cmin = min(ceil)
    return {"wall_min_mm": round(wmin[0] + 1e-3, 3), "wall_min_at_yz": wmin[1], "wall_samples": len(walls),
            "ceiling_min_mm": round(cmin[0], 3), "ceiling_min_at_yz": cmin[1], "ceiling_samples": len(ceil),
            "body_x1_mm": round(body_x1, 3), "gap_to_pad_band_mm": round(band_gap, 3),
            "body_x0_mm": round(x_min, 3), "min_x_gap_to_swept_cam_plate_mm": round(cam_gap, 3), "that_cam": cam_at,
            "min_x_gap_with_axial_play_mm": round(cam_gap - PM.mm(P.AXIAL_DRIFT), 3),
            "pass": bool(wmin[0] + 1e-3 >= 1.2 and cmin[0] >= 1.2 and band_gap >= 0.5)}


# --- 本体 --------------------------------------------------------------------------------------------------------
def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
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
    print(f"built {len(parts)} parts in {time.time() - t0:.1f}s")
    ids = PM.part_ids()
    assert sorted(parts) == sorted(ids), "build_moving() の返りが part_ids() と違う"
    bad, defects = [], []
    si_total = za_total = 0
    for pid in ids:
        ob = parts[pid]
        me = ob.data
        lo, hi = bbox_mm(me)
        export_stl(ob, os.path.join(OUT, f"{pid}.stl"))
        za_file = stl_zero_area(os.path.join(OUT, f"{pid}.stl"))
        pose = PM.PRINT_POSE[pid]
        pme = rotated_print_mesh(ob, pose["euler_deg"])
        pob = bpy.data.objects.new(f"print_{pid}", pme)
        bpy.context.collection.objects.link(pob)
        export_stl(pob, os.path.join(OUT, f"print_{pid}.stl"))
        za_file += stl_zero_area(os.path.join(OUT, f"print_{pid}.stl"))
        area, where = overhang(pme)
        plo, phi = bbox_mm(pme)
        nm = nonmanifold(ob)
        cc = components(me)
        si_a, za_a = mesh_defects(me, 1000.0)
        si_p, za_p = mesh_defects(pme, 1000.0)
        entry = {
            "bbox_assembly_mm": [round(float(x), 3) for x in (hi - lo)],
            "bbox_assembly_min_mm": [round(float(x), 3) for x in lo], "bbox_assembly_max_mm": [round(float(x), 3) for x in hi],
            "volume_cm3": round(volume(ob) * 1e6, 4),
            "nonmanifold_edges": nm, "components": cc,
            "self_intersections": {"assembly": si_a, "print": si_p}, "zero_area_triangles": {"assembly": za_a, "print": za_p, "stl_files": za_file},
            "faces": len(me.polygons),
            "print": {"euler_deg": list(pose["euler_deg"]), "bbox_mm": [round(float(x), 3) for x in (phi - plo)],
                      "overhang_area_mm2": round(area, 3), "overhang_where": where,
                      "reason": pose["reason"], "support": pose["support"]},
        }
        report["parts"][pid] = entry
        if nm or cc != 1:
            bad.append((pid, nm, cc))
        if si_a or si_p or za_a or za_p or za_file:
            defects.append((pid, si_a, si_p, za_a, za_p, za_file))
        si_total += si_a + si_p
        za_total += za_a + za_p + za_file
        bpy.data.objects.remove(pob, do_unlink=True)
        bpy.data.meshes.remove(pme)

    report["alignment"] = check_alignment(parts)
    report["fits"] = check_fits(parts)
    report["horn_rejection"] = check_horn_rejection()
    report["coupler_walls"] = check_coupler_walls(parts)
    report["gear_mesh"] = check_gear_mesh()
    report["clip"] = PM.INFO.get("clip")
    report["cam_label_pos_mm"] = PM.INFO.get("cam_label_pos_mm")
    report["cam_hub_len_mm"] = PM.INFO.get("cam_hub_len_mm")
    report["summary"] = {
        "parts": len(ids), "all_manifold_single_component": not bad, "bad": bad,
        "self_intersections_total": si_total, "zero_area_triangles_total": za_total, "defect_parts": defects,
        "defects_pass": bool(si_total == 0 and za_total == 0),
        "overhang_calibration_ok": cal_ok, "horn_rejection_pass": report["horn_rejection"]["pass"], "fits_pass": report["fits"]["pass"], "coupler_walls_pass": report["coupler_walls"]["pass"], "alignment_pass": report["alignment"]["pass"],
        "gear_mesh_pass": report["gear_mesh"]["pass"], "seconds": round(time.time() - t0, 1),
    }
    write_json(os.path.join(OUT, "report.json"), report)
    print("summary:", json.dumps(report["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
