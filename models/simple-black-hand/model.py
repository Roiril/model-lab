"""ロボットハンド本体。部品ごとの Blender オブジェクトを親子階層で組む。

単独で実行すると exports/simple-black-hand.stl を書く。手首と前腕は無い（手だけ）。
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


def xcyl(x0, x1, y, z, r, seg=96):
    """X 軸方向の円柱（えぐり・くぼみの刃物）。"""
    bm = bmesh.new()
    rows = [[bm.verts.new((x, y + r * math.cos(2 * math.pi * i / seg), z + r * math.sin(2 * math.pi * i / seg)))
             for i in range(seg)] for x in (x0, x1)]
    for i in range(seg):
        bm.faces.new((rows[0][i], rows[0][(i + 1) % seg], rows[1][(i + 1) % seg], rows[1][i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[1])
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


def loft(stations, apex=None):
    """角丸長方形の断面をつないだ殻。stations=[(z, 幅, 手のひら側の Y, 甲側の Y, 縮める割合), ...]。
    断面は凸なので両端は平らな蓋で閉じる。apex=(x, y, z) を渡すと遠位の端を 1 点へ閉じる。"""
    bm = bmesh.new()
    rows = []
    for z, w, f, b, s in stations:
        d, yc = b - f, (b + f) / 2
        sec = _section(max(w * s, 0.3), max(d * s, 0.3), min(P.SHELL_EDGE_R, d * 0.45) * s)
        rows.append([bm.verts.new((x, y + yc, z)) for x, y in sec])
    n = len(rows[0])
    for a, b in zip(rows, rows[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(rows[0])
    if apex is None:
        bm.faces.new(rows[-1])
    else:
        top = bm.verts.new(apex)
        for i in range(n):
            bm.faces.new((rows[-1][i], rows[-1][(i + 1) % n], top))
    return _finish(bm)


def straight(z0, z1, w0, w1, f0, f1, b0, b1, n=6):
    """z0 から z1 まで幅と厚みが直線で変わる節の胴。"""
    out = []
    for t in np.linspace(0, 1, n):
        out.append((z0 + (z1 - z0) * t, w0 + (w1 - w0) * t, f0 + (f1 - f0) * t, b0 + (b1 - b0) * t, 1.0))
    return loft(out)


def knuckle(w, z, front, back, seg=96):
    """関節の軸（y=AXIS_Y, z）を中心にした丸い拳骨。半径は甲側の面まで。手のひら側の面で平らに切る。
    断面 (y, z) は円と直線で囲まれた凸の形で、X 方向へ押し出す。左右の縁は節の角と同じ丸みで落とす。"""
    ay = P.AXIS_Y
    R = back - ay
    e = min(P.SHELL_EDGE_R, w * 0.2)
    t_end = math.acos(max(min((front - ay) / R, 1.0), -1.0))   # 手のひら側の面と円の交点（0 が甲側 +Y、π/2 が遠位 +Z）
    prof = [(ay + R * math.cos(t), z + R * math.sin(t)) for t in np.linspace(0, t_end, seg // 2)]
    # 近位へ胴の中まで OVERLAP 伸ばして、胴と継ぎ目なく重ねる。胴の面と同じ平面にならないよう、わずかに内へ寄せる
    ov, s = 3.0, 0.03
    prof = [(back - s, z - ov)] + prof + [(front + s, z - ov)]
    clean = []
    for p in prof:
        if not clean or math.dist(p, clean[-1]) > 1e-6:
            clean.append(p)
    prof = np.array(clean)
    c = prof.mean(0)
    # 辺ごとの内向きの法線
    ed = np.roll(prof, -1, 0) - prof
    ed /= np.maximum(np.linalg.norm(ed, axis=1, keepdims=True), 1e-9)
    en = np.stack([-ed[:, 1], ed[:, 0]], 1)
    mid = (prof + np.roll(prof, -1, 0)) / 2
    if ((c - mid) * en).sum(1).mean() < 0:
        en = -en

    def inset(k):
        """凸の輪郭を k だけ内へ寄せる。頂点は前後の辺を寄せた線の交点。"""
        n1, n2 = np.roll(en, 1, 0), en
        return prof + k * (n1 + n2) / (1 + (n1 * n2).sum(1, keepdims=True))

    hw = w / 2
    rows_x = []
    for k in range(5):
        a = math.pi / 2 * (1 - k / 4)
        rows_x.append((-hw + e * (1 - math.sin(a)), e * (1 - math.cos(a))))
    for k in range(5):
        a = math.pi / 2 * k / 4
        rows_x.append((hw - e * (1 - math.sin(a)), e * (1 - math.cos(a))))
    bm = bmesh.new()
    rows = [[bm.verts.new((x, y, zz)) for y, zz in inset(k)] for x, k in rows_x]
    m = len(prof)
    for a, b in zip(rows, rows[1:]):
        for i in range(m):
            bm.faces.new((a[i], a[(i + 1) % m], b[(i + 1) % m], b[i]))
    bm.faces.new(rows[0])
    bm.faces.new(rows[-1])
    return _finish(bm)


def cup(w, back_prev):
    """近位の端のえぐり。手前の節の拳骨（半径 back_prev - AXIS_Y）と同心で、継ぎ目の幅だけ大きい。"""
    R = back_prev - P.AXIS_Y + P.KNUCKLE_GAP
    return xcyl(-w / 2 - 2, w / 2 + 2, P.AXIS_Y, 0.0, R)


def pin_recess(w, z):
    """拳骨の左右の面の、軸のふたの浅いくぼみ。"""
    h = w / 2
    return [xcyl(h - P.PIN_DEPTH, h + 1, P.AXIS_Y, z, P.PIN_R, seg=48),
            xcyl(-h - 1, -h + P.PIN_DEPTH, P.AXIS_Y, z, P.PIN_R, seg=48)]


def rounded_plate(hx, y0, y1, z0, z1, r0, r1, e, n=10):
    """Y 方向に厚みのある板。z0 側の角を r0、z1 側の角を r1 で丸める。面の縁は e で丸める。
    角の丸みは板の長さと幅に収まるよう縮める（はみ出すと輪郭が自己交差し、ブーリアンで板ごと消える）。"""
    lim_z = (z1 - z0 - 0.2) / (r0 + r1) if r0 + r1 > z1 - z0 - 0.2 else 1.0
    r0, r1 = min(r0 * lim_z, hx - 0.1), min(r1 * lim_z, hx - 0.1)

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


# ---- 形の足し引き（Blender の EXACT ブーリアン） --------------------------------

def _temp_object(subs, name):
    verts, faces = [], []
    for v, f in subs:
        n = len(verts)
        verts += list(v)
        faces += [tuple(i + n for i in q) for q in f]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def combine(base, ops):
    """base（小部品のリスト）に ops=[("UNION" | "DIFFERENCE", 小部品のリスト), ...] を順に当てて 1 つの殻にする。"""
    ob = _temp_object(base, "_csg")
    tools = []
    for i, (op, subs) in enumerate(ops):
        t = _temp_object(subs, f"_csg_tool{i}")
        t.hide_render = True
        mod = ob.modifiers.new(f"op{i}", "BOOLEAN")
        mod.operation = op
        mod.object = t
        mod.solver = "EXACT"
        tools.append(t)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    verts = [tuple(v.co) for v in me.vertices]
    faces = [tuple(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    for o in [ob] + tools:
        m = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.meshes.remove(m)
    if not faces:
        raise RuntimeError("ブーリアンの結果が空")
    return [(verts, faces)]


# ---- 節 -------------------------------------------------------------------

def segment(L, w0, w1, back_prev, back, front0=P.SEG_FRONT, front1=P.SEG_FRONT):
    """回る節。局所原点は近位の関節の軸の高さの z=0。遠位の端 z=L に拳骨を持ち、近位は手前の拳骨に沿ってえぐる。"""
    body = straight(0.0, L, w0, w1, front0, front1, back_prev, back)
    return combine([body], [("UNION", [knuckle(w1, L, front1, back)]),
                            ("DIFFERENCE", [cup(max(w0, w1), back_prev)]),
                            ("DIFFERENCE", pin_recess(w1, L))])


def root_segment(width, root_extra, back):
    """指の根元の節（手のひらに固定）。遠位の端 z=0 に関節 j3 の拳骨を持つ。"""
    body = straight(-root_extra, 0.0, width, width, P.SEG_FRONT, P.SEG_FRONT, back, back, n=2)
    return combine([body], [("UNION", [knuckle(width, 0.0, P.SEG_FRONT, back)]),
                            ("DIFFERENCE", pin_recess(width, 0.0))])


def tip_segment(w0, w, length, back_prev, back):
    """指先。近位は手前の拳骨に沿ってえぐり、厚みを指先の値まで細くしてから丸く閉じる。"""
    f0, f1 = P.SEG_FRONT, P.TIP_FRONT
    nose = w * P.TIP_NOSE
    zb = length - nose
    zt = min(zb, length * 0.45)       # ここまでで指先の厚みになる
    st = []
    for t in np.linspace(0, 1, 6):
        st.append((zt * t, w0 + (w - w0) * t, f0 + (f1 - f0) * t, back_prev + (back - back_prev) * t, 1.0))
    st.append((zb, w, f1, back, 1.0))
    for i in range(1, 15):
        a = math.pi / 2 * i / 15
        st.append((zb + nose * math.sin(a), w, f1, back, math.cos(a)))
    body = loft(st, apex=(0.0, (f1 + back) / 2, length))
    return combine([body], [("DIFFERENCE", [cup(max(w0, w), back_prev)])])


def finger_parts(name, hinges, width, tip_width, root_extra):
    """1 本の指の節。戻り値は [(部品名, 親, 親の中の z, 小部品のリスト)]。局所原点は近位の関節。"""
    h1, h2, h3 = hinges
    B = P.SEG_BACK
    L1, L2 = h3 - h2, h2 - h1
    return [
        (f"{name}_root", None, 0.0, root_segment(width, root_extra, B["root"])),
        (f"{name}_seg1", f"{name}_root", 0.0, segment(L1, width, width, B["root"], B["seg1"])),
        (f"{name}_seg2", f"{name}_seg1", L1, segment(L2, width, width, B["seg1"], B["seg2"])),
        (f"{name}_tip", f"{name}_seg2", L2, tip_segment(width, tip_width, h1, B["seg2"], B["tip"])),
    ]


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
    # 甲側は手首の側へ寄せる。参考の横からの写真では、手の甲は指の付け根から手首へ向けて高くなる
    dome_rear = np.maximum(1 - ((mx - cx) / ax_) ** 2 - ((mz - cz - P.PALM_DOME_REAR_DZ) / az_) ** 2, 0)

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

    th = P.THENAR
    thenar = th["h"] * np.exp(-0.5 * ((mx - th["x"]) ** 2 + (mz - th["z"]) ** 2) / th["sigma"] ** 2)

    def make(dome, extra=0.0, shape=dome_shape):
        h = edge + (dome * shape + extra) * rim
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
    yf = read(make(P.PALM_DOME_FRONT, thenar), q)
    yb = read(make(P.PALM_DOME_REAR, shape=dome_rear), q)
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

    # 手のひら（階層の根）。手首と前腕はこの種には無い
    zw = 0.0
    pv, pf = palm_mesh()
    add("palm", [(pv, pf)], None, (0, 0, 0))
    rv, rf = shade_ring()
    add("palm_shade", [(rv, rf)], "palm", (0, 0, 0), material=dark)

    # 指 4 本
    for name in P.FINGER_ORDER:
        f = P.FINGERS[name]
        phi = math.radians(f["splay"])
        d = np.array([math.sin(phi), math.cos(phi)])  # 指先方向 (X,Z)
        tip = np.array(f["tip"])
        h1, h2, h3 = f["hinges"]
        j3 = tip - d * h3
        root_extra = (f["length"] - h3) + P.ROOT_BELOW_PALM
        for part, parent, z, subs in finger_parts(name, f["hinges"], f["width"], f["tip_width"], root_extra):
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

    def shifted(subs):
        return [([(a + dx, b, c) for a, b, c in v], f) for v, f in subs]

    # 根元: 角の丸い板が開口の奥から関節 j3 の拳骨まで続く。手のひら側は関節の手前まで厚くふくらむ
    B = P.SEG_BACK
    rb = B["root"]
    pe = P.THUMB_PAD_EDGE
    root_body = rounded_plate(w / 2, P.SEG_FRONT, rb, t["root_end"], Lp, t["root_end_r"], 1.0, P.SHELL_EDGE_R)  # 遠位の角は拳骨の重なりの中に隠れる
    pad = rounded_plate(w / 2 - 1.5, P.THUMB_ROOT_FRONT, P.SEG_FRONT + pe, t["root_end"], Lp - P.THUMB_PAD_STOP,
                        t["root_end_r"], pe + 1.0, pe)
    root = shifted(combine([root_body], [("UNION", [pad]),
                                         ("UNION", [knuckle(w, Lp, P.SEG_FRONT, rb)]),
                                         ("DIFFERENCE", pin_recess(w, Lp))]))
    add("thumb_root", root, "palm", (piv[0], 0.0, piv[1] - zw), (math.radians(t["rest_tilt"]), phi, 0.0))
    add("thumb_shade", [shade_disc(P.THUMB_SHADE_ZMAX)], "thumb_root", (0, 0, 0), material=dark)
    L1 = h3 - h2
    L2 = h2 - h1
    add("thumb_seg1", on_axis(segment(L1, w, w, rb, B["seg1"])), "thumb_root", (dx, P.AXIS_Y, Lp))
    add("thumb_seg2", on_axis(segment(L2, w, w, B["seg1"], B["seg2"])), "thumb_seg1", (0, 0, L1))
    add("thumb_tip", on_axis(tip_segment(w, t["tip_width"], h1, B["seg2"], B["tip"])), "thumb_seg2", (0, 0, L2))
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
    export_stl("simple-black-hand")
