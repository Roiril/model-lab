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
        k = min((z - z0) / P.BODY_CHAMFER, 1.0)   # 手のひら側を節と同じように斜めに落とす
        dd = d * (0.6 + 0.4 * k)
        off = d * 0.2 * (1 - k)
        sec = _section(max(w * s, 0.3), max(dd * s, 0.3), min(r, dd * 0.45) * s)
        rows.append([bm.verts.new((x, y + off, z)) for x, y in sec])
    n = len(rows[0])
    for a, b in zip(rows, rows[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(rows[0])
    top = bm.verts.new((0, 0, z1))
    for i in range(n):
        bm.faces.new((rows[-1][i], rows[-1][(i + 1) % n], top))
    return _finish(bm)


def rear_web(zh):
    """棒の背面を塞ぐ薄い壁。近位の節が持つ。手のひら側へ曲げても棒と舌に当たらない。"""
    h = P.BAR_HALF
    r0 = P.BAR_R + 0.35
    yb = P.WEB_REAR_Y
    zb = P.HINGE_CLEAR + 0.6
    bm = bmesh.new()
    angs = np.radians(np.linspace(0, 78, 9))  # 0 が近位の方向（-Z）、増えると背面（+Y）
    A = [(r0 * math.sin(t), zh - r0 * math.cos(t)) for t in angs]
    B = []
    for t in angs:
        # 同じ光線が外枠（y=yb または z=zh-zb）に当たる点
        sy, sz = math.sin(t), math.cos(t)
        rr = min(yb / max(sy, 1e-6), zb / max(sz, 1e-6))
        B.append((rr * sy, zh - rr * sz))
    rows = []
    for x in (-h, h):
        rows.append(([bm.verts.new((x, y, z)) for y, z in A], [bm.verts.new((x, y, z)) for y, z in B]))
    (a0, b0), (a1, b1) = rows
    n = len(A)
    for i in range(n - 1):
        bm.faces.new((a0[i], a0[i + 1], b0[i + 1], b0[i]))
        bm.faces.new((a1[i], b1[i], b1[i + 1], a1[i + 1]))
        bm.faces.new((a0[i], a1[i], a1[i + 1], a0[i + 1]))
        bm.faces.new((b0[i], b0[i + 1], b1[i + 1], b1[i]))
    bm.faces.new((a0[0], b0[0], b1[0], a1[0]))
    bm.faces.new((a0[-1], a1[-1], b1[-1], b0[-1]))
    return _finish(bm)


def thumb_cheek(r, y_half, x_edge, z_low, sign):
    """つばの左右の張り出し。関節の円板より外側で、開口の中だけを塞ぐ。"""
    n = 14
    a0 = math.asin(min(max(z_low / r, -1), 1))
    xe = abs(x_edge)
    if xe >= r:
        return None
    a1 = math.acos(xe / r)
    pts = [(xe, z_low)] + [(r * math.cos(a0 + (a1 - a0) * i / n), r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    bm = bmesh.new()
    rows = []
    for y in (-y_half, y_half):
        rows.append([bm.verts.new((sign * x, y, z)) for x, z in pts])
    m = len(pts)
    for i in range(m):
        bm.faces.new((rows[0][i], rows[0][(i + 1) % m], rows[1][(i + 1) % m], rows[1][i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[1])
    return _finish(bm)


def thumb_boss(r, y_half, z_max, seg=64):
    """親指の根元の丸い部分。Y 軸の円盤で、遠位側を z_max で切る。"""
    pts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        x, z = r * math.sin(a), r * math.cos(a)
        pts.append((x, min(z, z_max)))
    bm = bmesh.new()
    rows = []
    e = 0.6
    for y, k in ((-y_half, (r - e) / r), (-y_half + e, 1.0), (y_half - e, 1.0), (y_half, (r - e) / r)):
        rows.append([bm.verts.new((x * k, y, z * k)) for x, z in pts])
    for a, b in zip(rows, rows[1:]):
        for i in range(seg):
            bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[-1])
    return _finish(bm)


def side_plates(zh):
    """z=zh の軸を挟む左右の長円の板。近位の節が持つ。軸の背面を塞ぐ壁も付ける。"""
    out = []
    for sx in (-1, 1):
        x0, x1 = sorted((sx * P.DISC_INNER_X, sx * P.DISC_OUTER_X))
        out.append(xcyl(x0, x1, 0, zh, P.DISC_R, edge=0.5))
        out.append(xcyl(x0, x1, 0, zh - P.PLATE_TAIL, P.DISC_R, edge=0.5))
        out.append(rbox(x0, x1, -P.DISC_R, P.DISC_R, zh - P.PLATE_TAIL, zh, 0.5, seg=2))
    out.append(rear_web(zh))
    return out


def hinge_bar():
    """z=0 の軸にある棒と、節へつなぐ舌と細い首。遠位側の節が持つ。"""
    h = P.BAR_HALF
    c = P.HINGE_CLEAR
    return [xcyl(-h, h, 0, 0, P.BAR_R, edge=0.3),
            rbox(-h, h, -P.TONGUE_DEPTH / 2, P.TONGUE_DEPTH / 2, 0, c + 1.0, 0.4, seg=2),
            profile_body(2 * h, c, P.BODY_START + 2.0, chamfer_far=False)]


def profile_body(w, z0, z1, chamfer_far=True, chamfer_near=True):
    """節の胴。手のひら側（-Y）の両端を斜めに落とした断面を X へ伸ばす。縁は丸い。"""
    hd = P.SEG_DEPTH / 2
    r = P.SEG_EDGE_R
    c = min(P.BODY_CHAMFER, (z1 - z0) * 0.45)
    # (y, z) の輪郭（凸）。-Y 側の両端は斜め、+Y 側は丸い角
    pts = []
    if chamfer_near:
        pts += [(-hd, z0 + c), (-hd * 0.2, z0)]
    else:
        pts += [(-hd, z0)]
    for i in range(7):
        a = math.pi / 2 * (1 - i / 6)
        pts.append((hd - r + r * math.cos(a), z0 + r - r * math.sin(a)))
    for i in range(7):
        a = math.pi / 2 * i / 6
        pts.append((hd - r + r * math.cos(a), z1 - r + r * math.sin(a)))
    if chamfer_far:
        pts += [(-hd * 0.2, z1), (-hd, z1 - c)]
    else:
        pts += [(-hd, z1)]
    pts = np.array(pts)
    ctr = pts.mean(0)
    e = r
    rows = []
    bm = bmesh.new()
    for x, k in ((-w / 2, 1.0), (-w / 2 + e * 0.29, 0.29), (-w / 2 + e, 0.0), (w / 2 - e, 0.0), (w / 2 - e * 0.29, 0.29), (w / 2, 1.0)):
        q = ctr + (pts - ctr) * np.array([1 - 2 * k * e / P.SEG_DEPTH, 1 - 2 * k * e / max(z1 - z0, 1e-3)])
        rows.append([bm.verts.new((x, a, b)) for a, b in q])
    n = len(pts)
    for a, b in zip(rows, rows[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[-1])
    return _finish(bm)


def seg_body(w, z0, z1):
    return profile_body(w, z0, z1)


def finger_parts(name, tip, hinges, width, tip_width, root_extra):
    """1 本の指の節。戻り値は [(部品名, 親, 親の中の z, 小部品のリスト)]。局所原点は近位の関節。"""
    h1, h2, h3 = hinges
    c = P.HINGE_CLEAR
    b0 = P.BODY_START
    out = []
    out.append((f"{name}_root", None, 0.0,
                [profile_body(width - 2.5, -root_extra, -c, chamfer_near=False)] + side_plates(0.0)))
    L1 = h3 - h2
    out.append((f"{name}_seg1", f"{name}_root", 0.0,
                [seg_body(width, b0, L1 - c)] + hinge_bar() + side_plates(L1)))
    L2 = h2 - h1
    out.append((f"{name}_seg2", f"{name}_seg1", L1,
                [seg_body(width, b0, L2 - c)] + hinge_bar() + side_plates(L2)))
    out.append((f"{name}_tip", f"{name}_seg2", L2,
                [fingertip(tip_width, P.SEG_DEPTH + 0.5, b0, h1)] + hinge_bar()))
    return out


# ---- 手のひら -------------------------------------------------------------

def _palm_polygon():
    """外形の点列 (X, Z)[mm]。px の指定を Catmull-Rom で滑らかにして等間隔に取り直す。"""
    pts = []
    for p in P.PALM_OUTLINE_PX:
        if p == "NOTCH":
            cu, cv = P.NOTCH_CENTER_PX
            a0, a1 = P.NOTCH_ARC_START_DEG, P.NOTCH_ARC_END_DEG
            for t in np.linspace(a0, a1, 14):
                a = math.radians(t)
                pts.append((cu + P.NOTCH_R_PX * math.cos(a), cv + P.NOTCH_R_PX * math.sin(a)))
        else:
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
    dome_shape = 1 - np.exp(-np.maximum(Dp - R, 0) / 14.0)
    mound = np.zeros(mx.shape)
    for name in P.FINGER_ORDER:
        f = P.FINGERS[name]
        phi = math.radians(f["splay"])
        c = np.array(f["tip"]) - np.array([math.sin(phi), math.cos(phi)]) * (f["length"] + P.MOUND_INSET)
        mound += P.MOUND_H * np.exp(-((mx - c[0]) ** 2 + (mz - c[1]) ** 2) / (2 * P.MOUND_SIGMA ** 2))
    mound *= t

    def blur(field):
        rad = int(3 * P.PALM_BLUR / hf)
        g = np.exp(-0.5 * (np.arange(-rad, rad + 1) * hf / P.PALM_BLUR) ** 2)
        g /= g.sum()
        out = np.apply_along_axis(lambda m: np.convolve(m, g, mode="same"), 0, field)
        return np.apply_along_axis(lambda m: np.convolve(m, g, mode="same"), 1, out)

    keep = np.clip((Dp - R * 0.12) / (R * 0.35), 0, 1)  # 縁のごく近くは元の丸みのまま

    def make(dome, extra):
        h = edge + dome * dome_shape + extra
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
    yf = read(make(P.PALM_DOME_FRONT, 0.0), q)
    yb = read(make(P.PALM_DOME_REAR, mound), q)
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


def notch_ledge():
    """開口の奥の段（手のひらに固定）。親指のつばの背面に重なって、すき間から向こうが見えないようにする。"""
    L = P.NOTCH_LEDGE
    cx, cz = P.px(*P.NOTCH_CENTER_PX)
    angs = np.radians(np.linspace(L["deg0"], L["deg1"], 40))
    bm = bmesh.new()
    corners = []
    for y in (L["y0"], L["y1"]):
        inner = [bm.verts.new((cx + L["r0"] * math.cos(a), y, cz - L["r0"] * math.sin(a))) for a in angs]
        outer = [bm.verts.new((cx + L["r1"] * math.cos(a), y, cz - L["r1"] * math.sin(a))) for a in angs]
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


def build_hand(collection=None):
    """手を組む。戻り値は {部品名: オブジェクト}, {部品名: [小部品(m)]}, {関節名: (オブジェクト, 軸, 基準の Euler)}。"""
    col = collection or bpy.context.scene.collection
    mat = hand_material()
    objs, subs_all, joints = {}, {}, {}

    def add(name, subs, parent, loc, rot=(0.0, 0.0, 0.0)):
        ob = _mesh_object(name, subs, col, mat)
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
    # 手のひら（原点は手首の軸）
    zw = P.WRIST_Z
    pv, pf = palm_mesh()
    palm = [([(x, y, z - zw) for x, y, z in pv], pf)]
    lv, lf = notch_ledge()
    palm.append(([(x, y, z - zw) for x, y, z in lv], lf))
    h = P.WRIST_BLOCK_HALF
    palm.append(xcyl(-h, h, 0, 0, P.WRIST_BLOCK_R, edge=0.5))
    palm.append(rbox(-h, h, -P.WRIST_BLOCK_R, P.WRIST_BLOCK_R, 0, 10.0, 0.5, seg=2))
    add("palm", palm, "base" if False else None, (0, 0, zw))
    objs["palm"].parent = objs["base"]
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
                    add(part, subs, parent, (0, 0, 0))
                else:
                    add(part, subs, parent, (0, 0, z))
        joints[f"{name}_j3"] = (objs[f"{name}_seg1"], 0, (0.0, 0.0, 0.0))
        joints[f"{name}_j2"] = (objs[f"{name}_seg2"], 0, (0.0, 0.0, 0.0))
        joints[f"{name}_j1"] = (objs[f"{name}_tip"], 0, (0.0, 0.0, 0.0))

    # 親指
    t = P.THUMB
    phi = math.radians(t["splay"])
    d = np.array([math.sin(phi), math.cos(phi)])
    tip = np.array(t["tip"])
    h1, h2, h3 = t["hinges"]
    # 回転の中心は開口の中心。関節 j3 は指の線の上にあるので、根元の節は少し偏心する。
    piv = np.array(P.px(*P.NOTCH_CENTER_PX))
    rel = (tip - d * h3) - piv
    Lp = float(rel @ d)
    dx = float(rel @ np.array([math.cos(phi), -math.sin(phi)]))
    w = t["width"]
    r_end = t["root_end_r"]
    zcut = Lp - P.BAR_R - 0.3

    def shifted(subs):
        return [([(a + dx, b, c) for a, b, c in v], f) for v, f in subs]

    root = shifted([profile_body(w - 1.0, -2.0, Lp - P.HINGE_CLEAR, chamfer_near=False)] + side_plates(Lp))
    root += [thumb_boss(r_end, t["boss_half"], zcut), thumb_boss(t["flange_r"], t["flange_half"], zcut)]
    for sg in (-1, 1):
        ch = thumb_cheek(t["flange_r"], t["flange_half"], P.DISC_OUTER_X + 0.3 + sg * dx * 1.0, zcut - 0.5, sg)
        if ch is not None:
            root.append(ch)
    add("thumb_root", root, "palm", (piv[0], 0.0, piv[1] - zw), (math.radians(t["rest_tilt"]), phi, 0.0))
    L1 = h3 - h2
    L2 = h2 - h1
    b0 = P.BODY_START
    c = P.HINGE_CLEAR
    add("thumb_seg1", [seg_body(w, b0, L1 - c)] + hinge_bar() + side_plates(L1), "thumb_root", (dx, 0, Lp))
    add("thumb_seg2", [seg_body(w, b0, L2 - c)] + hinge_bar() + side_plates(L2), "thumb_seg1", (0, 0, L1))
    add("thumb_tip", [fingertip(t["tip_width"], P.SEG_DEPTH + 0.5, b0, h1)] + hinge_bar(), "thumb_seg2", (0, 0, L2))
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
