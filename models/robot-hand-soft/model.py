"""ロボットハンド本体。部品ごとの Blender オブジェクトを親子階層で組む。

単独で実行すると exports/robot-hand-soft.stl と .blend を書く。
他のスクリプトからは build_hand() を呼ぶ。
部品は重なった閉じた殻（凸の小部品）の集まりで、印刷用に結合していない。
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils import geometry as mgeo

import params as P

M = P.MM


# ---- 小部品（局所座標は mm。最後に m へ直す） --------------------------------

def _finish(bm):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    verts = [tuple(v.co) for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    faces = [tuple(idx[v] for v in f.verts) for f in bm.faces]
    bm.free()
    return verts, faces


def rbox(x0, x1, y0, y1, z0, z1, r, seg=3):
    """角を丸めた直方体。"""
    bm = bmesh.new()
    cs = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    v = [bm.verts.new(c) for c in cs]
    for q in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([v[i] for i in q])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if r > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, segments=seg, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    return _finish(bm)


def xcyl(x0, x1, y, z, r, edge=0.0, seg=40):
    """X 軸方向の円柱。"""
    bm = bmesh.new()
    rows = []
    prof = [(x0, r - edge), (x0 + edge, r), (x1 - edge, r), (x1, r - edge)] if edge > 0 else [(x0, r), (x1, r)]
    for xx, rr in prof:
        rows.append([bm.verts.new((xx, y + rr * math.cos(2 * math.pi * i / seg), z + rr * math.sin(2 * math.pi * i / seg)))
                     for i in range(seg)])
    for a, b in zip(rows, rows[1:]):
        for i in range(seg):
            bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[-1])
    return _finish(bm)


def _section(w, d, r, n=12):
    """角丸長方形の断面（反時計回り）。"""
    pts = []
    hw, hd = w / 2, d / 2
    r = min(r, hw - 1e-3, hd - 1e-3)
    for cx, cy, a0 in ((hw - r, hd - r, 0), (-hw + r, hd - r, 90), (-hw + r, -hd + r, 180), (hw - r, -hd + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def fingertip(w, d, z0, z1, base_r=2.2, nose=None):
    """丸い指先。z0 が根元、z1 が頂点。胴は角丸長方形で、先は全体を縮めて丸める。"""
    nose = nose if nose is not None else w * 0.62
    bm = bmesh.new()
    rows = []
    zb = z1 - nose
    body_r = min(w, d) * 0.42
    base_r = max(base_r, body_r * 0.72)
    stations = [(z0, 0.93, base_r), (z0 + 0.7, 1.0, base_r)]
    for t in np.linspace(z0 + 1.6, zb, 5):
        k = min((t - z0) / max(min(zb - z0, 3.5), 1e-6), 1.0)
        stations.append((t, 1.0, base_r + (body_r - base_r) * k))
    for i in range(1, 15):
        a = math.pi / 2 * i / 15
        stations.append((zb + nose * math.sin(a), math.cos(a), body_r))
    for z, s, r in stations:
        sec = _section(max(w * s, 0.3), max(d * s, 0.3), min(r, d * 0.45) * s)
        rows.append([bm.verts.new((x, y, z)) for x, y in sec])
    n = len(rows[0])
    for a, b in zip(rows, rows[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(rows[0])
    top = bm.verts.new((0, 0, z1))
    for i in range(n):
        bm.faces.new((rows[-1][i], rows[-1][(i + 1) % n], top))
    return _finish(bm)


def rounded_plate(hx, y0, y1, z0, z1, r0, r1, e, n=10):
    """Y 方向に厚みのある板。z0 側の角を r0、z1 側の角を r1 で丸める。面の縁は e で丸める。"""
    def poly(i):
        hw, a, b = hx - i, z0 + i, z1 - i
        ra, rb = max(r0 - i, 0.05), max(r1 - i, 0.05)
        pts = []
        for cx, cz, r, a0 in ((hw - rb, b - rb, rb, 0), (-hw + rb, b - rb, rb, 90), (-hw + ra, a + ra, ra, 180), (hw - ra, a + ra, ra, 270)):
            for k in range(n + 1):
                t = math.radians(a0 + 90 * k / n)
                pts.append((cx + r * math.cos(t), cz + r * math.sin(t)))
        return pts
    prof = []
    for k in range(5):
        t = math.pi / 2 * (1 - k / 4)
        prof.append((y0 + e * (1 - math.sin(t)), e * (1 - math.cos(t))))
    for k in range(5):
        t = math.pi / 2 * k / 4
        prof.append((y1 - e * (1 - math.sin(t)), e * (1 - math.cos(t))))
    bm = bmesh.new()
    rows = [[bm.verts.new((x, y, z)) for x, z in poly(i)] for y, i in prof]
    m = len(rows[0])
    for a, b in zip(rows, rows[1:]):
        for i in range(m):
            bm.faces.new((a[i], a[(i + 1) % m], b[(i + 1) % m], b[i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[-1])
    return _finish(bm)


def cradle_lip(zh):
    """棒を受ける部分と背面の壁。近位の節が持つ。棒の裏を塞ぎ、手のひら側へ曲げても当たらない。"""
    h = P.NARROW_HALF + 0.1          # 板の中まで通して、棒の両脇のすき間も塞ぐ
    ax = P.AXIS_Y
    rc = P.CRADLE_R
    yb = P.LIP_BACK_Y - ax
    zb = P.LIP_BOTTOM
    zt = P.LIP_TOP
    a1 = math.pi - math.acos(min(zt / rc, 1.0))   # 0 が近位の方向（-Z）、増えると背面（+Y）を通って遠位へ
    angs = np.linspace(0, a1, 15)
    A = [(rc * math.sin(t), -rc * math.cos(t)) for t in angs]
    B = []
    for t in angs:
        sy, sz = math.sin(t), -math.cos(t)     # 光線の向き（y, z）
        rr = yb / max(sy, 1e-6)
        if sz < 0:
            rr = min(rr, zb / -sz)
        elif sz > 0:
            rr = min(rr, zt / sz)
        B.append((rr * sy, rr * sz))
    # 外枠の角を通るように、背面の 2 つの角の方向を足す
    corners = [(math.atan2(yb, zb), (yb, -zb)), (math.pi - math.atan2(yb, zt), (yb, zt))]
    pairs = list(zip(angs, A, B))
    for ca, cp in corners:
        if 0 < ca < a1:
            pairs.append((ca, (rc * math.sin(ca), -rc * math.cos(ca)), cp))
    pairs.sort(key=lambda q: q[0])
    A = [q[1] for q in pairs]
    B = [q[2] for q in pairs]
    bm = bmesh.new()
    rows = []
    for x in (-h, h):
        rows.append(([bm.verts.new((x, ax + y, zh + z)) for y, z in A], [bm.verts.new((x, ax + y, zh + z)) for y, z in B]))
    (a0, b0), (a1v, b1v) = rows
    n = len(A)
    for i in range(n - 1):
        bm.faces.new((a0[i], a0[i + 1], b0[i + 1], b0[i]))
        bm.faces.new((a1v[i], b1v[i], b1v[i + 1], a1v[i + 1]))
        bm.faces.new((a0[i], a1v[i], a1v[i + 1], a0[i + 1]))
        bm.faces.new((b0[i], b0[i + 1], b1v[i + 1], b1v[i]))
    bm.faces.new((a0[0], b0[0], b1v[0], a1v[0]))
    bm.faces.new((a0[-1], a1v[-1], b1v[-1], b0[-1]))
    return _finish(bm)


def stadium_plate(x0, x1, ax, z0, z1, R, e=0.5, n=20, dome=0):
    """X 方向に厚みのある長円の板。y=ax を中心に、z0〜z1 の範囲。1 つの閉じた殻にする（重なった面を作らない）。"""
    def poly(r):
        zc0, zc1 = z0 + R, z1 - R
        pts = []
        for i in range(n + 1):
            t = math.pi * i / n
            pts.append((ax + r * math.cos(t), zc1 + r * math.sin(t)))
        for i in range(n + 1):
            t = math.pi + math.pi * i / n
            pts.append((ax + r * math.cos(t), zc0 + r * math.sin(t)))
        return pts
    inner_lo = [(x0, R - e), (x0 + e * 0.29, R - e * 0.29), (x0 + e, R)]
    inner_hi = [(x1 - e, R), (x1 - e * 0.29, R - e * 0.29), (x1, R - e)]
    h = min(P.CAP_DOME_H, x1 - x0 - 2 * e)
    rt = P.CAP_DOME_R
    dome_rows = [(h * math.sin(math.pi / 2 * k / 10), R - (R - rt) * (1 - math.cos(math.pi / 2 * k / 10))) for k in range(11)]
    if dome > 0:
        prof = inner_lo + [(x1 - h + a, r) for a, r in dome_rows]
    elif dome < 0:
        prof = [(x0 + h - a, r) for a, r in reversed(dome_rows)] + inner_hi
    else:
        prof = inner_lo + inner_hi
    bm = bmesh.new()
    rows = [[bm.verts.new((x, y, z)) for y, z in poly(r)] for x, r in prof]
    m = len(rows[0])
    for a, b in zip(rows, rows[1:]):
        for i in range(m):
            bm.faces.new((a[i], a[(i + 1) % m], b[(i + 1) % m], b[i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[-1])
    return _finish(bm)


def side_plates(zh, tail=None, outer=None, lip=True):
    """z=zh の軸を挟む左右の長円の板。近位の節が持つ。"""
    tail = P.PLATE_TAIL if tail is None else tail
    outer = P.DISC_OUTER_X if outer is None else outer
    R = P.DISC_R
    out = []
    for sx in (-1, 1):
        x0, x1 = sorted((sx * P.NARROW_HALF, sx * outer))
        out.append(stadium_plate(x0, x1, P.AXIS_Y, zh - tail - R, zh + R, R, dome=sx))
    if lip:
        out.append(cradle_lip(zh))
        out.append(xcyl(-P.DRUM_HALF, P.DRUM_HALF, P.DRUM_Y, zh, P.DRUM_R, edge=0.25, seg=48))
    return out


def round_polygon(pts, r=1.2, n=6):
    """閉じた折れ線の角を半径 r 相当で丸める。長い辺はそのまま残る。"""
    pts = [np.array(p, float) for p in pts]
    out = []
    m = len(pts)
    for i in range(m):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % m]
        l1, l2 = np.linalg.norm(p1 - p0), np.linalg.norm(p2 - p1)
        t = min(r, 0.45 * l1, 0.45 * l2)
        a, b = p1 + (p0 - p1) / l1 * t, p1 + (p2 - p1) / l2 * t
        for k in range(n + 1):
            u = k / n
            out.append((1 - u) ** 2 * a + 2 * u * (1 - u) * p1 + u * u * b)
    return np.array(out)


def profile_plate(right, y0, y1, e0, e1, flat=0.94):
    """Y 方向に厚みのある板。right=[(半幅, z), ...] を z の順に。左右対称。縁は y0 側 e0、y1 側 e1 で丸める。

    平らな面の内側にもう 1 周（輪郭を中心へ flat 倍に縮めた輪）を置いて、なめらかな陰影が面の中へ広がらないようにする。
    """
    c = round_polygon([(x, z) for x, z in right] + [(-x, z) for x, z in reversed(right)])
    t = np.roll(c, -1, 0) - np.roll(c, 1, 0)
    t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-9)
    nrm = np.stack([-t[:, 1], t[:, 0]], 1)     # 反時計回りの輪郭の内向き
    prof = []
    if e0 > 0:
        for k in range(4):
            a = math.pi / 2 * (1 - k / 3)
            prof.append((y0 + e0 * (1 - math.sin(a)), e0 * (1 - math.cos(a))))
    else:
        prof.append((y0, 0.0))
    for k in range(5):
        a = math.pi / 2 * k / 4
        prof.append((y1 - e1 * (1 - math.sin(a)), e1 * (1 - math.cos(a))))
    zc = (c[:, 1].min() + c[:, 1].max()) / 2
    bm = bmesh.new()
    rows = [[bm.verts.new((p[0], y, p[1])) for p in c + nrm * i] for y, i in prof]
    m = len(c)

    def shrink(row, y):
        return [bm.verts.new((v.co.x * flat, y, zc + (v.co.z - zc) * flat)) for v in row]

    if e0 > 0:
        rows.insert(0, shrink(rows[0], y0))
    rows.append(shrink(rows[-1], y1))
    for a, b in zip(rows, rows[1:]):
        for i in range(m):
            bm.faces.new((a[i], a[(i + 1) % m], b[(i + 1) % m], b[i]))
    # 平らな蓋。平面の中の三角分割なので、凹んだ輪郭でも膜は張らない
    for row in (rows[0], rows[-1]):
        cap = bm.faces.new(row)
        bmesh.ops.triangulate(bm, faces=[cap], quad_method="BEAUTY", ngon_method="BEAUTY")
    return _finish(bm)


def rear_cover(right):
    """節の甲側の板。胴より背面へわずかに出て、輪郭は胴と同じ。手のひら側からは見えない。"""
    return profile_plate(right, P.COVER_Y0, P.SEG_DEPTH / 2 + 0.06, 0.0, P.SEG_EDGE_R)


def seg_outline(w, L):
    """節の輪郭の胴の部分。幅広の部分から左右の軸のふたの間へ斜めに細くなる。"""
    hw = w / 2
    n = P.NARROW_HALF
    return [(P.BAR_HALF, 5.0), (hw, 5.8), (hw, L - 9.4), (n, L - 6.6)]


def seg_cover(w, L):
    z0 = P.COVER_Z0
    d = 0.02
    return rear_cover([(7.2, z0), (P.BAR_HALF + d, z0 + 0.4)]
                      + [(x + d, z) for x, z in seg_outline(w, L)]
                      + [(P.NARROW_HALF + d, L - 3.9), (7.2, L - P.COVER_END)])


def tip_cover(w, d):
    """指先の甲側を胴の手前まで伸ばす。断面は指先の根元と同じ丸い角。"""
    body_r = min(w, d) * 0.42
    base_r = max(2.2, body_r * 0.72)
    z0 = P.COVER_Z0
    stations = [(z0, 0.76), (z0 + 0.25, 0.88), (z0 + 0.7, 0.95), (P.WIDE_START + 0.8, 0.995)]
    y0 = P.COVER_Y0
    bm = bmesh.new()
    rows = []
    for z, s in stations:
        sec = _section(w * s, d * s, min(base_r, d * 0.45) * s)
        half = sec[:len(sec) // 2]        # 背面側の 2 つの角
        ring = half + [(half[-1][0], y0), (half[0][0], y0)]
        rows.append([bm.verts.new((x, y, z)) for x, y in ring])
    m = len(rows[0])
    for a, b in zip(rows, rows[1:]):
        for i in range(m):
            bm.faces.new((a[i], a[(i + 1) % m], b[(i + 1) % m], b[i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[-1])
    return _finish(bm)


def hinge_bar(neck=False):
    """軸の近くの横棒と、節へつなぐ舌。遠位側の節が持つ。棒の下は暗い溝として見える。neck=True で板の間を通る首も付ける。"""
    h = P.BAR_HALF
    ax = P.AXIS_Y
    hd = P.SEG_DEPTH / 2 - 0.02
    out = [rbox(-h, h, ax - P.BAR_FRONT, ax + P.TONGUE_HALF, P.BAR_Z0, P.BAR_Z1, P.BAR_ROUND, seg=4),
           rbox(-h, h, ax - P.TONGUE_HALF, ax + P.TONGUE_HALF, P.BAR_Z0 + 0.5, P.DIST_START + 0.8, 0.3, seg=2)]
    if neck:
        out.append(rbox(-h, h, -hd, P.NECK_BACK_Y, P.DIST_START, P.WIDE_START + 1.0, P.SEG_EDGE_R, seg=3))
    return out


def seg_body(w, L):
    """節の胴。1 枚の平らな板で、近位は細い首、中央が幅広、遠位は左右の板の間へ細くなる。"""
    hd = P.SEG_DEPTH / 2
    e = P.SEG_EDGE_R
    body = profile_plate([(P.BAR_HALF, P.DIST_START)] + seg_outline(w, L) + [(P.NARROW_HALF, L - P.PROX_END)], -hd, hd, e, e)
    return [body, seg_cover(w, L)]


def finger_parts(name, tip, hinges, width, tip_width, root_extra):
    """1 本の指の節。戻り値は [(部品名, 親, 親の中の z, 小部品のリスト)]。局所原点は近位の関節。"""
    h1, h2, h3 = hinges
    out = []
    out.append((f"{name}_root", None, 0.0,
                [profile_plate([(width / 2, -root_extra), (width / 2, -9.4), (P.NARROW_HALF, -6.6), (P.NARROW_HALF, -P.PROX_END)],
                               -P.SEG_DEPTH / 2, P.SEG_DEPTH / 2, P.SEG_EDGE_R, P.SEG_EDGE_R),
                 rear_cover([(width / 2 + 0.02, -root_extra), (width / 2 + 0.02, -9.4), (P.NARROW_HALF + 0.02, -6.6),
                             (P.NARROW_HALF + 0.02, -3.9), (7.2, -P.COVER_END)])] + side_plates(0.0)))
    L1 = h3 - h2
    out.append((f"{name}_seg1", f"{name}_root", 0.0,
                seg_body(width, L1) + hinge_bar() + side_plates(L1)))
    L2 = h2 - h1
    out.append((f"{name}_seg2", f"{name}_seg1", L1,
                seg_body(width, L2) + hinge_bar() + side_plates(L2)))
    out.append((f"{name}_tip", f"{name}_seg2", L2,
                [fingertip(tip_width, P.SEG_DEPTH + 0.5, P.WIDE_START, h1), tip_cover(tip_width, P.SEG_DEPTH + 0.5)] + hinge_bar(neck=True)))
    return out


# ---- 手のひら -------------------------------------------------------------

def _palm_polygon():
    """外形の点列 (X, Z)[mm]。px の指定を Catmull-Rom で滑らかにして等間隔に取り直す。"""
    pts = []
    for p in P.PALM_OUTLINE_PX:
        pts.append(p)
    pts = np.array([P.px(*p) for p in pts], float)
    n = len(pts)
    dense = []
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        for t in np.linspace(0, 1, 12, endpoint=False):
            t2, t3 = t * t, t * t * t
            dense.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    dense = np.array(dense)
    seg = np.linalg.norm(np.roll(dense, -1, 0) - dense, axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    step = 0.9
    ts = np.arange(0, s[-1], step)
    closed = np.vstack([dense, dense[0]])
    out = np.stack([np.interp(ts, s, closed[:, 0]), np.interp(ts, s, closed[:, 1])], 1)
    # 手で読んだ点の小さな凹凸を消す
    for _ in range(4):
        out = (np.roll(out, 1, 0) + 2 * out + np.roll(out, -1, 0)) / 4
    return out


def palm_mesh():
    """外形から距離で厚みを決めて閉じた手のひらを作る。縁は丸く、甲側はふくらむ。"""
    poly = _palm_polygon()
    seg_a = poly
    seg_b = np.roll(poly, -1, 0)

    def dist_at(q):
        """外形までの距離（外側は負）。"""
        d = np.full(len(q), 1e9)
        ab = seg_b - seg_a
        l2 = (ab ** 2).sum(1)
        inside = np.zeros(len(q), bool)
        for i0 in range(0, len(q), 4000):
            qq = q[i0:i0 + 4000]
            ap = qq[:, None, :] - seg_a[None]
            t = np.clip((ap * ab[None]).sum(2) / l2[None], 0, 1)
            near = ap - t[..., None] * ab[None]
            d[i0:i0 + 4000] = np.sqrt((near ** 2).sum(2)).min(1)
            crossing = (seg_a[None, :, 1] > qq[:, None, 1]) != (seg_b[None, :, 1] > qq[:, None, 1])
            with np.errstate(divide="ignore", invalid="ignore"):
                xs = seg_a[:, 0] + (qq[:, None, 1] - seg_a[:, 1]) * (seg_b[:, 0] - seg_a[:, 0]) / (seg_b[:, 1] - seg_a[:, 1])
            inside[i0:i0 + 4000] = ((crossing & (qq[:, None, 0] < xs)).sum(1) % 2) == 1
        return np.where(inside, d, -d)

    # 内向きの法線で等距離の点を作り、距離が合わない点（自己交差した角）を捨てる
    R, p = P.PALM_EDGE_R, P.PALM_EDGE_P
    tang = np.roll(poly, -1, 0) - np.roll(poly, 1, 0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True)
    nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
    if dist_at(poly[:1] + nrm[:1] * 0.5)[0] < 0:
        nrm = -nrm
    pts = []
    for a in np.linspace(0.12, 1.0, 12):
        o = R * (1 - math.cos(a * math.pi / 2))
        q = poly + nrm * o
        q = q[np.abs(dist_at(q) - o) < 0.08]
        pts.append(q)
    x0, z0 = poly.min(0) - 2
    x1, z1 = poly.max(0) + 2
    gx, gz = np.meshgrid(np.arange(x0, x1, 1.6), np.arange(z0, z1, 1.6))
    grid = np.stack([gx.ravel(), gz.ravel()], 1)
    grid = grid[dist_at(grid) > R + 1.2]
    pts.append(grid)
    inner = np.vstack(pts)

    nb = len(poly)
    verts2 = [Vector(q) for q in poly] + [Vector(q) for q in inner]
    edges = [(i, (i + 1) % nb) for i in range(nb)]
    out = mgeo.delaunay_2d_cdt(verts2, edges, [], 1, 1e-4)
    vs, tris = out[0], out[2]
    q = np.array([tuple(v) for v in vs])
    d = np.maximum(dist_at(q), 0)

    # 厚みは細かい格子の高さ場で作り、一様にぼかして距離場の折れ目を消す。メッシュの点はそこから読む。
    hf = P.PALM_FIELD_STEP
    fx = np.arange(x0, x1 + hf, hf)
    fz = np.arange(z0, z1 + hf, hf)
    mx, mz = np.meshgrid(fx, fz)
    D = dist_at(np.stack([mx.ravel(), mz.ravel()], 1)).reshape(mx.shape)
    Dp = np.maximum(D, 0)
    t = np.clip(Dp / R, 0, 1)
    edge = (P.PALM_DEPTH / 2) * (1 - (1 - t) ** p) ** (1 / p)
    # ふくらみは外形の距離に依らない楕円の放物面にする。距離で作ると中心線に沿って折れ目が出る。
    px0, pz0 = poly.min(0)
    px1, pz1 = poly.max(0)
    cx, cz, ax_, az_ = (px0 + px1) / 2, (pz0 + pz1) / 2, (px1 - px0) / 2, (pz1 - pz0) / 2
    dome_shape = np.maximum(1 - ((mx - cx) / ax_) ** 2 - ((mz - cz) / az_) ** 2, 0)

    def blur(field):
        rad = int(3 * P.PALM_BLUR / hf)
        g = np.exp(-0.5 * (np.arange(-rad, rad + 1) * hf / P.PALM_BLUR) ** 2)
        g /= g.sum()
        out = np.apply_along_axis(lambda m: np.convolve(m, g, mode="same"), 0, field)
        return np.apply_along_axis(lambda m: np.convolve(m, g, mode="same"), 1, out)

    keep = np.clip((Dp - R * 0.12) / (R * 0.35), 0, 1)  # 縁のごく近くは元の丸みのまま
    # ふくらみを縁へ向けて 0 に落とす。折れ目を出さないよう広くぼかす
    rim = np.clip(Dp / P.PALM_DOME_RIM, 0, 1)
    for _ in range(3):
        rim = blur(rim)

    def make(dome):
        h = edge + dome * dome_shape * rim
        return h * (1 - keep) + blur(h) * keep

    def read(field, pts):
        u = (pts[:, 0] - x0) / hf
        v = (pts[:, 1] - z0) / hf
        i = np.clip(np.floor(u).astype(int), 0, field.shape[1] - 2)
        j = np.clip(np.floor(v).astype(int), 0, field.shape[0] - 2)
        a = np.clip(u - i, 0, 1)
        b = np.clip(v - j, 0, 1)
        return (field[j, i] * (1 - a) * (1 - b) + field[j, i + 1] * a * (1 - b)
                + field[j + 1, i] * (1 - a) * b + field[j + 1, i + 1] * a * b)

    poly_keys = {tuple(np.round(a, 3)) for a in poly}
    onb = np.array([tuple(np.round(a, 3)) in poly_keys for a in q])
    yf = read(make(P.PALM_DOME_FRONT), q)
    yb = read(make(P.PALM_DOME_REAR), q)
    yf[onb] = 0
    yb[onb] = 0
    # 前後の面。外周の点は共有して閉じる。
    n = len(q)
    index_back = np.full(n, -1)
    verts = [(q[i, 0], -yf[i], q[i, 1]) for i in range(n)]
    for i in range(n):
        if onb[i]:
            index_back[i] = i
        else:
            index_back[i] = len(verts)
            verts.append((q[i, 0], yb[i], q[i, 1]))
    faces = []
    for t in tris:
        a, b, c = t
        ab = q[b] - q[a]
        ac = q[c] - q[a]
        s = ab[0] * ac[1] - ab[1] * ac[0]
        if s > 0:
            faces.append((a, b, c))
            faces.append((index_back[a], index_back[c], index_back[b]))
        else:
            faces.append((a, c, b))
            faces.append((index_back[a], index_back[b], index_back[c]))
    return verts, faces


def pivot_mm():
    return np.array(P.px(*P.THUMB_PIVOT_PX))


def ray_to_palm(c, a, poly, r_max, overlap):
    """開口の中心から角度 a の線が手のひらの外形に最初に当たる距離 + overlap。当たらなければ 0。"""
    d = np.array([math.cos(a), math.sin(a)])
    p0 = poly
    e = np.roll(poly, -1, 0) - p0
    den = d[0] * e[:, 1] - d[1] * e[:, 0]
    ok = np.abs(den) > 1e-9
    w = p0 - c
    t = np.where(ok, (w[:, 0] * e[:, 1] - w[:, 1] * e[:, 0]) / np.where(ok, den, 1), -1)
    u = np.where(ok, (w[:, 0] * d[1] - w[:, 1] * d[0]) / np.where(ok, den, 1), -1)
    hit = t[(t > 0) & (u >= 0) & (u <= 1) & (t < r_max)]
    return float(hit.min()) + overlap if len(hit) else 0.0


def shade_ring():
    """開口の奥を暗くする輪（手のひらに固定）。外周は外形の内側へ少し入るだけにして、壁の前へ出さない。"""
    L = P.NOTCH_SHADE
    c = pivot_mm()
    phi = math.radians(P.THUMB["splay"])
    # 親指が出ていく方向の角度（X→Z の角度）から gap だけ離して、反対側を回る
    out = math.atan2(math.cos(phi), math.sin(phi))
    amin = math.asin(L["perp"] / L["r1"])
    poly = _palm_polygon()
    # 外形に届く角度だけを使う。届かない向きは開口の口で、そこには何も置かない
    angs = [a for a in np.linspace(out + amin, out + 2 * math.pi - amin, 200)
            if ray_to_palm(c, a, poly, L["r1"], L["overlap"]) > 0]
    bm = bmesh.new()
    corners = []
    for y in (L["y0"], L["y1"]):
        inner, outer = [], []
        for a in angs:
            off = abs(math.sin(a - out))
            # 親指の線から perp より離れる。そこまでは半径を広げる
            # 開口の出口側は親指の線からの距離だけで切る。奥側は根元の丸い端を避けて半径で切る
            r0 = L["r0"] if math.cos(a - out) < -0.45 else L["perp"] / max(off, 1e-6)
            r1 = ray_to_palm(c, a, poly, L["r1"], L["overlap"])
            r0 = min(r0, r1 - 0.01)
            inner.append(bm.verts.new((c[0] + r0 * math.cos(a), y, c[1] + r0 * math.sin(a))))
            outer.append(bm.verts.new((c[0] + r1 * math.cos(a), y, c[1] + r1 * math.sin(a))))
        corners.append((inner, outer))
    (i0, o0), (i1, o1) = corners
    n = len(angs)
    for k in range(n - 1):
        bm.faces.new((i0[k], i0[k + 1], o0[k + 1], o0[k]))
        bm.faces.new((i1[k], o1[k], o1[k + 1], i1[k + 1]))
        bm.faces.new((i0[k], i1[k], i1[k + 1], i0[k + 1]))
        bm.faces.new((o0[k], o0[k + 1], o1[k + 1], o1[k]))
    bm.faces.new((i0[0], o0[0], o1[0], i1[0]))
    bm.faces.new((i0[-1], i1[-1], o1[-1], o0[-1]))
    return _finish(bm)


def shade_disc(z_max):
    """親指の根元の裏の円板。親指と一緒に回る。開口の奥の暗がりとして見える。指先側は z_max で切る。"""
    r = P.THUMB_SHADE_R
    y0, y1 = P.THUMB_SHADE_Y
    seg = 72
    pts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        pts.append((r * math.cos(a), min(r * math.sin(a), z_max)))
    bm = bmesh.new()
    rows = [[bm.verts.new((x, y, z)) for x, z in pts] for y in (y0, y1)]
    for i in range(seg):
        bm.faces.new((rows[0][i], rows[0][(i + 1) % seg], rows[1][(i + 1) % seg], rows[1][i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    return _finish(bm)


# ---- 台座 -----------------------------------------------------------------

def revolve(profile, seg=96, cap_top=True):
    """(z, r) の断面を Z 軸回りに回す。"""
    bm = bmesh.new()
    rows = []
    for z, r in profile:
        rows.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    for a, b in zip(rows, rows[1:]):
        for i in range(seg):
            bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[-1])
    return _finish(bm)


def base_parts():
    e = P.BASE_EDGE
    disc = revolve([(0.0, P.BASE_R - 0.5), (0.5, P.BASE_R), (P.BASE_H - e, P.BASE_R), (P.BASE_H - e * 0.3, P.BASE_R - e * 0.3), (P.BASE_H, P.BASE_R - e), (P.BASE_H + 0.0, 56.0)])
    prof = [(P.BASE_H - 0.4, P.STEM_PROFILE[0][1])] + list(P.STEM_PROFILE)
    z, r = P.STEM_PROFILE[-1]
    prof += [(z + P.STEM_TOP_ROUND * 0.0, r - P.STEM_TOP_ROUND)]
    stem = revolve(prof)
    # 耳とピン。軸の高さに中心。下は軸足の中へ。
    zw = P.WRIST_Z
    parts = [disc, stem]
    for sx in (-1, 1):
        a, b = sorted((sx * P.WRIST_LUG_X[0], sx * P.WRIST_LUG_X[1]))
        parts.append(xcyl(a, b, 0, zw, P.WRIST_LUG_R, edge=0.5))
        parts.append(rbox(a, b, -P.WRIST_LUG_R, P.WRIST_LUG_R, P.STEM_TOP_Z - 2.5, zw, 0.5, seg=2))
        c, d = sorted((sx * P.WRIST_LUG_X[1], sx * P.WRIST_PIN_X))
        parts.append(xcyl(c - 0.1 if sx > 0 else c, d if sx > 0 else d + 0.1, 0, zw, P.WRIST_PIN_R, edge=0.4))
    return parts


# ---- 組み立て -------------------------------------------------------------

def _mesh_object(name, subs, collection, mat=None, scale=M, sharp=0.95):
    verts, faces = [], []
    for v, f in subs:
        n = len(verts)
        verts += [(a * scale, b * scale, c * scale) for a, b, c in v]
        faces += [tuple(i + n for i in q) for q in f]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    me.shade_smooth()
    if hasattr(me, "set_sharp_from_angle"):
        me.set_sharp_from_angle(angle=sharp)
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    return ob


def hand_material():
    mat = bpy.data.materials.get("hand_matte") or bpy.data.materials.new("hand_matte")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*P.HAND_COLOR, 1)
    bsdf.inputs["Roughness"].default_value = P.HAND_ROUGHNESS
    bsdf.inputs["Specular IOR Level"].default_value = P.HAND_SPECULAR
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1800.0
    noise.inputs["Detail"].default_value = 4.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.8
    bump.inputs["Distance"].default_value = 0.0002
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return mat


def shade_material():
    """開口の奥の暗がり。ほとんど光を返さない。"""
    mat = bpy.data.materials.get("hand_shade") or bpy.data.materials.new("hand_shade")
    mat.use_nodes = True
    b = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (0, 0, 0, 1)
    b.inputs["Roughness"].default_value = 1.0
    b.inputs["Specular IOR Level"].default_value = 0.0
    b.inputs["Emission Color"].default_value = (*P.SHADE_EMIT, 1)
    b.inputs["Emission Strength"].default_value = 1.0
    return mat


def base_side_material():
    """台座の側面の帯。上面より暗い。"""
    mat = bpy.data.materials.get("base_side") or bpy.data.materials.new("base_side")
    mat.use_nodes = True
    b = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*P.BASE_SIDE_COLOR, 1)
    b.inputs["Roughness"].default_value = P.HAND_ROUGHNESS
    b.inputs["Specular IOR Level"].default_value = P.BASE_SIDE_SPECULAR
    return mat


def on_axis(subs):
    """回る節の小部品を、関節の軸（y=AXIS_Y）が局所原点になる座標へ移す。"""
    return [([(a, b - P.AXIS_Y, c) for a, b, c in v], f) for v, f in subs]


def build_hand(collection=None):
    """手を組む。戻り値は {部品名: オブジェクト}, {部品名: [小部品(m)]}, {関節名: (オブジェクト, 軸, 基準の Euler)}。"""
    col = collection or bpy.context.scene.collection
    mat = hand_material()
    objs, subs_all, joints = {}, {}, {}

    dark = shade_material()

    def add(name, subs, parent, loc, rot=(0.0, 0.0, 0.0), material=None):
        ob = _mesh_object(name, subs, col, material or mat)
        if parent is not None:
            ob.parent = objs[parent]
        ob.location = Vector(loc) * M
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = rot
        objs[name] = ob
        subs_all[name] = [([(a * M, b * M, c * M) for a, b, c in v], f) for v, f in subs]
        return ob

    # 台座（固定）
    add("base", base_parts(), None, (0, 0, 0))
    e = P.BASE_EDGE
    add("base_rim", [revolve([(0.0, P.BASE_R - 0.48), (0.5, P.BASE_R + 0.02), (P.BASE_H - e, P.BASE_R + 0.02), (P.BASE_H - e + 0.02, P.BASE_R - 0.3)])],
        "base", (0, 0, 0), material=base_side_material())
    # 手のひら（原点は手首の軸）
    zw = P.WRIST_Z
    pv, pf = palm_mesh()
    palm = [([(x, y, z - zw) for x, y, z in pv], pf)]
    h = P.WRIST_BLOCK_HALF
    palm.append(xcyl(-h, h, 0, 0, P.WRIST_BLOCK_R, edge=0.5))
    palm.append(rbox(-h, h, -P.WRIST_BLOCK_R, P.WRIST_BLOCK_R, 0, 10.0, 0.5, seg=2))
    add("palm", palm, "base" if False else None, (0, 0, zw))
    objs["palm"].parent = objs["base"]
    rv, rf = shade_ring()
    add("palm_shade", [(rv, rf)], "palm", (0, 0, -zw), material=dark)
    joints["wrist"] = (objs["palm"], 0, (0.0, 0.0, 0.0))

    # 指 4 本
    for name in P.FINGER_ORDER:
        f = P.FINGERS[name]
        phi = math.radians(f["splay"])
        d = np.array([math.sin(phi), math.cos(phi)])  # 指先方向 (X,Z)
        tip = np.array(f["tip"])
        h1, h2, h3 = f["hinges"]
        j3 = tip - d * h3
        root_extra = (f["length"] - h3) + P.ROOT_BELOW_PALM
        for part, parent, z, subs in finger_parts(name, tip, f["hinges"], f["width"], f["tip_width"], root_extra):
            if parent is None:
                add(part, subs, "palm", (j3[0], 0.0, j3[1] - zw), (0.0, phi, 0.0))
            else:
                if part.endswith("seg1"):
                    add(part, on_axis(subs), parent, (0, P.AXIS_Y, 0))
                else:
                    add(part, on_axis(subs), parent, (0, 0, z))
        joints[f"{name}_j3"] = (objs[f"{name}_seg1"], 0, (0.0, 0.0, 0.0))
        joints[f"{name}_j2"] = (objs[f"{name}_seg2"], 0, (0.0, 0.0, 0.0))
        joints[f"{name}_j1"] = (objs[f"{name}_tip"], 0, (0.0, 0.0, 0.0))

    # 親指
    t = P.THUMB
    phi = math.radians(t["splay"])
    d = np.array([math.sin(phi), math.cos(phi)])
    tip = np.array(t["tip"])
    h1, h2, h3 = t["hinges"]
    # 回転の中心は開口の中。関節 j3 は指の線の上にあるので、根元の節はわずかに偏心する。
    piv = pivot_mm()
    rel = (tip - d * h3) - piv
    Lp = float(rel @ d)
    dx = float(rel @ np.array([math.cos(phi), -math.sin(phi)]))
    w = t["width"]
    hd = P.SEG_DEPTH / 2

    def shifted(subs):
        return [([(a + dx, b, c) for a, b, c in v], f) for v, f in subs]

    # 根元: 平らな板が開口の奥まで入り、両脇の細長い板が関節まで伸びる
    root = shifted([rounded_plate(P.NARROW_HALF, -hd, hd, t["root_end"], Lp - P.PROX_END, t["root_end_r"], P.SEG_EDGE_R, P.SEG_EDGE_R),
                    rounded_plate(P.NARROW_HALF + 0.02, P.COVER_Y0, hd + 0.06, t["root_end"] - 0.02, Lp - P.COVER_END, t["root_end_r"], P.SEG_EDGE_R, P.SEG_EDGE_R)]
                   + side_plates(Lp, tail=Lp + t["rail_tail"], outer=t["rail_outer"]))
    add("thumb_root", root, "palm", (piv[0], 0.0, piv[1] - zw), (math.radians(t["rest_tilt"]), phi, 0.0))
    add("thumb_shade", [shade_disc(P.THUMB_SHADE_ZMAX)], "thumb_root", (0, 0, 0), material=dark)
    L1 = h3 - h2
    L2 = h2 - h1
    add("thumb_seg1", on_axis(seg_body(w, L1) + hinge_bar() + side_plates(L1)), "thumb_root", (dx, P.AXIS_Y, Lp))
    add("thumb_seg2", on_axis(seg_body(w, L2) + hinge_bar() + side_plates(L2)), "thumb_seg1", (0, 0, L1))
    add("thumb_tip", on_axis([fingertip(t["tip_width"], P.SEG_DEPTH + 0.5, P.WIDE_START, h1), tip_cover(t["tip_width"], P.SEG_DEPTH + 0.5)] + hinge_bar(neck=True)), "thumb_seg2", (0, 0, L2))
    joints["thumb_cmc"] = (objs["thumb_root"], 1, (math.radians(t["rest_tilt"]), phi, 0.0))
    joints["thumb_j3"] = (objs["thumb_seg1"], 0, (0.0, 0.0, 0.0))
    joints["thumb_j2"] = (objs["thumb_seg2"], 0, (0.0, 0.0, 0.0))
    joints["thumb_j1"] = (objs["thumb_tip"], 0, (0.0, 0.0, 0.0))
    return objs, subs_all, joints


def dump_world_triangles(objs, path):
    """現在の姿勢の全三角形を世界座標で npz に書く（カメラ合わせ用）。"""
    bpy.context.view_layer.update()
    rec = {}
    for name, ob in objs.items():
        me = ob.data
        me.calc_loop_triangles()
        mw = np.array(ob.matrix_world)
        v = np.array([tuple(x.co) for x in me.vertices])
        v = (mw[:3, :3] @ v.T).T + mw[:3, 3]
        rec[name] = v[np.array([t.vertices for t in me.loop_triangles])]
    np.savez_compressed(path, **rec)


if __name__ == "__main__":
    from blender_utils import clear_scene, export_stl
    clear_scene()
    objs, _, _ = build_hand()
    bpy.context.view_layer.update()
    xs = [Vector(c) for ob in objs.values() for c in (ob.matrix_world @ Vector(b) for b in ob.bound_box)]
    lo = [min(v[i] for v in xs) * 1000 for i in range(3)]
    hi = [max(v[i] for v in xs) * 1000 for i in range(3)]
    print("外形 mm: W=%.1f D=%.1f H=%.1f" % (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]))
    print("部品数:", len(objs), "面数:", sum(len(o.data.polygons) for o in objs.values()))
    if "--dump" in sys.argv:
        dump_world_triangles(objs, sys.argv[sys.argv.index("--dump") + 1])
    export_stl("robot-hand-soft")
