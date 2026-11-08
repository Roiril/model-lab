"""手首と前腕。WRIST.md の部品表どおりに作る。局所座標は mm で、原点は円柱の軸の中心。"""
import math

import bmesh
import numpy as np

import params as P


def _finish(bm):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    verts = [tuple(v.co) for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    faces = [tuple(idx[v] for v in f.verts) for f in bm.faces]
    bm.free()
    return verts, faces


def _swap(sub, order):
    """座標の軸を入れ替える。鏡映になる入れ替えでは面の向きを戻す。"""
    v, f = sub
    v = [tuple(p[i] for i in order) for p in v]
    if np.linalg.det(np.eye(3)[list(order)]) < 0:
        f = [tuple(reversed(q)) for q in f]
    return v, f


def lathe(rows_rz, top_fn=None, seg=96, cap_lo=True, cap_hi=True):
    """回転体。rows_rz=[(r, z, use_top)]。use_top が真の点は z に top_fn(x, y) を足す（縁を斜めに切る）。
    最初と最後の行は中心へ扇で閉じる。"""
    bm = bmesh.new()
    rings = []
    for r, z, use_top in rows_rz:
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            x, y = r * math.cos(a), r * math.sin(a)
            zz = z + (top_fn(x, y) if (use_top and top_fn) else 0.0)
            ring.append(bm.verts.new((x, y, zz)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
    for ring, on in ((rings[0], cap_lo), (rings[-1], cap_hi)):
        if not on:
            continue
        zc = sum(v.co.z for v in ring) / seg
        c = bm.verts.new((0, 0, zc))
        for i in range(seg):
            bm.faces.new((ring[i], ring[(i + 1) % seg], c))
    return _finish(bm)


def axis_cyl(axis, c0, c1, r, edge=0.0, seg=48, center=(0.0, 0.0)):
    """axis（0=X, 1=Y, 2=Z）の向きの円柱。c0..c1 は軸方向の範囲、center は残り 2 軸の中心。"""
    prof = [(c0, r - edge), (c0 + edge, r), (c1 - edge, r), (c1, r - edge)] if edge > 0 else [(c0, r), (c1, r)]
    o = [i for i in range(3) if i != axis]
    bm = bmesh.new()
    rows = []
    for t, rr in prof:
        row = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            p = [0.0, 0.0, 0.0]
            p[axis] = t
            p[o[0]] = center[0] + rr * math.cos(a)
            p[o[1]] = center[1] + rr * math.sin(a)
            row.append(bm.verts.new(p))
        rows.append(row)
    for a, b in zip(rows, rows[1:]):
        for i in range(seg):
            bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[-1])
    return _finish(bm)


def rim_height(x, y):
    """縁の高さの傾きの分（軸 +FOREARM_RIM からの差）[mm]。小指側（+X）が高い。"""
    return math.tan(math.radians(P.FOREARM_TILT)) * x


def forearm_parts():
    R = P.FOREARM_R
    Ri = R - P.FOREARM_WALL
    ch = P.FOREARM_CHAMFER
    top = P.FOREARM_RIM
    zs = top - P.FOREARM_SEAM
    zf = top - P.FOREARM_FLOOR
    zb = -P.FOREARM_LEN
    rows = [(R - 1.5, zb, False), (R, zb + 1.5, False),
            (R, zs - 1.0, False), (R - 0.7, zs - 0.35, False), (R - 0.7, zs + 0.35, False), (R, zs + 1.0, False),
            (R, top - ch * 1.6, True), (R - ch * 0.3, top - ch * 0.45, True), (R - ch, top, True),
            (Ri + ch * 0.6, top, True), (Ri, top - ch * 0.6, True),
            (Ri, zf + 1.0, False), (Ri - 1.0, zf, False)]
    tube = lathe(rows, rim_height)
    out = [tube]
    # 偏りの軸の台座（手のひら側と甲側の内壁）
    y0 = Ri - P.BOSS_DEPTH
    for s in (-1, 1):
        a, b = sorted((s * y0, s * (Ri + 1.5)))
        out.append(axis_cyl(1, a, b, P.BOSS_R, edge=0.5, seg=40, center=(0.0, -P.PIN_DROP)))
    return out


def lip_parts():
    """口の内側の輪。縁と同じ傾き。外周は壁へ少し入る。"""
    Ri = P.FOREARM_R - P.FOREARM_WALL
    r0 = Ri - P.LIP_W
    top = P.FOREARM_RIM - P.LIP_DROP
    bot = top - P.LIP_H
    rows = [(Ri + 0.3, bot, True), (r0, bot, True), (r0, top - 0.5, True), (r0 + 0.5, top, True), (Ri + 0.3, top, True)]
    bm_sub = lathe(rows, rim_height, cap_lo=False, cap_hi=False)
    # 開いた輪を閉じる: 最初と最後の行をつなぐ面を足す
    v, f = bm_sub
    seg = 96
    first = list(range(0, seg))
    last = list(range(len(rows) * seg - seg, len(rows) * seg))
    f = list(f) + [(first[i], last[i], last[(i + 1) % seg], first[(i + 1) % seg]) for i in range(seg)]
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in v]
    for q in f:
        bm.faces.new([vs[i] for i in q])
    return [_finish(bm)]


def rbox(x0, x1, y0, y1, z0, z1, r, seg=3):
    """角を丸めた直方体。"""
    bm = bmesh.new()
    cs = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    v = [bm.verts.new(c) for c in cs]
    for q in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([v[i] for i in q])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, segments=seg, profile=0.5, affect="EDGES", clamp_overlap=True)
    return _finish(bm)


def hub_parts():
    """横向きの円柱（曲げの軸）と両端の輪、偏りの軸。"""
    h, r = P.HUB_HALF, P.HUB_R
    out = [axis_cyl(0, -h - 0.2, h + 0.2, r, edge=0.6, seg=64)]
    for s in (-1, 1):
        a, b = sorted((s * h, s * (h + P.HUB_RING_W)))
        out.append(axis_cyl(0, a, b, P.HUB_RING_R, edge=0.7, seg=64))
        # 胴の帯（少し太い細い輪）
        a, b = sorted((s * 7.0, s * 9.0))
        out.append(axis_cyl(0, a, b, r + 0.5, edge=0.3, seg=64))
    # 円柱の下の台。偏りの軸（Y）が通る
    sx, sy = P.SADDLE
    zp = -P.PIN_DROP
    out.append(rbox(-sx, sx, -sy, sy, zp - 4.5, -r * 0.5, 1.5))
    out.append(axis_cyl(1, -sy - 1.2, sy + 1.2, 6.0, edge=0.8, seg=48, center=(0.0, zp)))
    Ri = P.FOREARM_R - P.FOREARM_WALL
    y1 = Ri - P.BOSS_DEPTH - P.PIN_GAP
    for s in (-1, 1):
        a, b = sorted((0.0, s * y1))
        out.append(axis_cyl(1, a, b, P.PIN_R, edge=0.4, seg=40, center=(0.0, zp)))
    return out


def yoke_parts(rounded_plate, profile_plate):
    """左右の板と上の平たい板、板の外の軸のふた。"""
    D = P.YOKE_DISC_R
    hy = P.YOKE_TOP_HALF_Y
    ztop = P.CARRIER_Z[0] + 2.5
    right = [(D * math.cos(math.radians(a)), D * math.sin(math.radians(a))) for a in np.linspace(-84, 0, 10)]
    right += [(D, 2.5), (hy, 10.0), (hy, ztop)]
    x0 = P.HUB_HALF + P.HUB_RING_W + P.YOKE_GAP
    x1 = x0 + P.YOKE_T
    out = []
    for s in (-1, 1):
        a, b = sorted((s * x0, s * x1))
        plate = profile_plate(right, a, b, 0.7, 0.7)          # 厚みは Y。X と入れ替える
        out.append(_swap(plate, (1, 0, 2)))
        c0, c1 = sorted((s * (x1 - 0.2), s * (x1 + P.YOKE_CAP_H)))
        out.append(axis_cyl(0, c0, c1, P.YOKE_CAP_R, edge=0.5, seg=48))
        c0, c1 = sorted((s * (x1 + P.YOKE_CAP_H - 0.2), s * (x1 + P.YOKE_CAP_H + 0.9)))
        out.append(axis_cyl(0, c0, c1, 2.6, edge=0.35, seg=32))
    cx, cy = P.CARRIER_HALF
    z0, z1 = P.CARRIER_Z
    carrier = rounded_plate(cx, z0, z1, -cy, cy, P.CARRIER_R * 3, P.CARRIER_R * 3, 1.6)   # 厚みは Y。Z と入れ替える
    out.append(_swap(carrier, (0, 2, 1)))
    return out
