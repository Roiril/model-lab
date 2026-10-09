"""SG92R 1 サーボで天面が開く 80mm 立方体。

部品（すべて印刷）: 箱 / 蓋 / クランク / リンク / 蝶番ピン / サーボ押さえクリップ。
買う部品は SG92R と付属の十字ホーンだけ。ねじ・結束バンド・接着剤は使わない。

形は mm で組み、最後に 0.001 倍して m に戻す（params はメートル）。
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

from blender_utils import EXPORTS_DIR, clear_scene, export_stl  # noqa: E402
import linkage as K  # noqa: E402
import params as P  # noqa: E402

NAME = "servo-lid-cube"
BUILD = os.path.join(HERE, "build")
MM = 1000.0
SG = P.SG


def mm(v):
    return v * MM


L = mm(P.CUBE)
HALF = L / 2
R = mm(P.EDGE_R)
WALL = mm(P.WALL)
FLOOR = mm(P.FLOOR)
SPLIT = L - mm(P.LID_T)                 # 77: 箱と蓋の境
IN = HALF - WALL                        # 37: 内面
HY, HZ = K.H
OY, OZ = K.O
BKX = mm(P.BOX_KNUCKLE_X)               # 20
LKX = BKX - mm(P.KNUCKLE_GAP)           # 19.6
GAP = mm(P.AX_GAP)

# X 方向の層（mm）
SX0 = mm(P.SERVO_X0)                                        # サーボ底面 -36.5
HORN_TOP = SX0 + mm(SG.HORN_TOP_Z)                          # -4.5
CRANK_X0 = SX0 + mm(SG.HORN_ARM_BOTTOM_Z) - mm(P.HORN_POCKET_EXTRA)  # -6.1
CRANK_X1 = HORN_TOP + mm(P.CRANK_TOP_T)                     # -2.0
LINK_X0 = CRANK_X1 + GAP                                    # -1.7
LINK_X1 = LINK_X0 + mm(P.LINK_T)                            # 2.3
FIN_X0 = LINK_X1 + GAP                                      # 2.6
FIN_X1 = FIN_X0 + mm(P.FIN_T)                               # 5.6

C45 = R * (2 - math.sqrt(2))            # 2.929: 刷る面の 45° 面取りの幅
T45 = R * (1 - 1 / math.sqrt(2))        # 1.464: 45° 面が丸に接する高さ


# ---------------------------------------------------------------------------
# 2D の道具
# ---------------------------------------------------------------------------

def circle(c, r, n=64, a0=0.0, a1=360.0, closed=True):
    m = n if closed else n + 1
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(m)]


def hull(points):
    pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


def ccw(poly):
    return poly if area(poly) > 0 else poly[::-1]


def triangulate(poly):
    """耳切り。凹んだ輪郭を n-gon で閉じると膜が張るので、蓋は必ず三角形で作る。"""
    poly = ccw(poly)
    idx = list(range(len(poly)))
    tris = []

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def inside(p, a, b, c):
        return cross(a, b, p) >= -1e-12 and cross(b, c, p) >= -1e-12 and cross(c, a, p) >= -1e-12
    guard = 0
    while len(idx) > 3 and guard < 100000:
        guard += 1
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if cross(a, b, c) <= 1e-12:
                continue
            if any(inside(poly[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            raise RuntimeError("triangulation failed")
    tris.append(tuple(idx))
    return poly, tris


def teardrop(c, r, up=1.0, n=48):
    """横穴の輪郭。刷るときの上側（up=+1 なら +2 軸目）に 45° の尖りを付け、余分 CAP で平らに切る。"""
    cap = mm(P.TEARDROP_CAP)
    pts = []
    for i in range(n + 1):
        a = math.radians(45 + 270 * i / n)          # 45°..315° を時計回りでなく反時計回りに
        pts.append((r * math.cos(a + math.pi / 2), r * math.sin(a + math.pi / 2)))
    # pts は上(90°)の左右 45° を除いた円弧。尖りの代わりに高さ r+cap の平らな天井
    top = r + cap
    half = (r * math.sqrt(2) - top)                  # 45° 線と天井の交点の半幅
    poly = pts + [(half, top), (-half, top)]
    poly = [(x, y * up) for x, y in poly]
    return [(c[0] + x, c[1] + y) for x, y in ccw(poly)]


# ---------------------------------------------------------------------------
# 3D の道具
# ---------------------------------------------------------------------------

def link_obj(bm, name):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def prism(poly, axis, a0, a1, name="prism"):
    """2D 輪郭を軸方向に押し出す。axis='x': (y,z) / 'y': (x,z) / 'z': (x,y)。"""
    poly, tris = triangulate(poly)

    def P3(p, t):
        if axis == "x":
            return (t, p[0], p[1])
        if axis == "y":
            return (p[0], t, p[1])
        return (p[0], p[1], t)
    bm = bmesh.new()
    lo = [bm.verts.new(P3(p, a0)) for p in poly]
    hi = [bm.verts.new(P3(p, a1)) for p in poly]
    for a, b, c in tris:
        bm.faces.new((lo[c], lo[b], lo[a]))
        bm.faces.new((hi[a], hi[b], hi[c]))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link_obj(bm, name)


def box(x0, x1, y0, y1, z0, z1, name="box"):
    return prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "z", z0, z1, name)


def cyl_x(c, r, x0, x1, n=64, name="cyl"):
    return prism(circle(c, r, n), "x", x0, x1, name)


def hull3d(points, name="hull"):
    bm = bmesh.new()
    for p in points:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link_obj(bm, name)


def loft_rings(rings, name):
    """同じ点数の輪（z, [(x,y)...]）を下から順に繋いだ立体。"""
    bm = bmesh.new()
    vs = [[bm.verts.new((p[0], p[1], z)) for p in ring] for z, ring in rings]
    bm.faces.new(vs[0][::-1])
    bm.faces.new(vs[-1])
    for a, b in zip(vs[:-1], vs[1:]):
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link_obj(bm, name)


def clean(ob, dist=1e-4):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=dist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def boolean(target, other, op):
    mod = target.modifiers.new("b", "BOOLEAN")
    mod.operation = op
    mod.solver = "EXACT"
    mod.object = other
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(other, do_unlink=True)
    clean(target)
    return target


def union(t, *others):
    for o in others:
        boolean(t, o, "UNION")
    return t


def cut(t, *others):
    for o in others:
        boolean(t, o, "DIFFERENCE")
    return t


def intersect(t, o):
    return boolean(t, o, "INTERSECT")


def nonmanifold(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    n = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    return n


def nonmanifold_where(ob, k=4):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    out = [[round(c, 2) for c in (e.verts[0].co + e.verts[1].co) / 2] for e in bm.edges if not e.is_manifold][:k]
    bm.free()
    return out


def volume(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    v = bm.calc_volume(signed=False)
    bm.free()
    return v


def transform(ob, mat):
    ob.data.transform(mat)
    ob.data.update()


def rot_x_about(deg, cy, cz):
    """X 軸（y=cy, z=cz を通る）まわりの回転。+deg で +Y が +Z へ回る。"""
    return (Matrix.Translation((0, cy, cz)) @ Matrix.Rotation(math.radians(deg), 4, "X")
            @ Matrix.Translation((0, -cy, -cz)))


# ---------------------------------------------------------------------------
# 外形（刷る面だけ 45° に逃がした丸み 5mm の立方体）
# ---------------------------------------------------------------------------

def rrect(half, rho, n=10):
    pts = []
    for cx, cy, a in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        for k in range(n + 1):
            t = math.radians(a + 90 * k / n)
            pts.append((cx * (half - rho) + rho * math.cos(t), cy * (half - rho) + rho * math.sin(t)))
    return pts


def round_profile(phi_from, phi_to, z_center, steps):
    """φ は角の丸の中心から見た角度（0=真下、90=真横、180=真上）。(z, 引っ込み d) を返す。"""
    out = []
    for i in range(steps + 1):
        f = math.radians(phi_from + (phi_to - phi_from) * i / steps)
        out.append((z_center - R * math.cos(f), R - R * math.sin(f)))
    return out


def outer_solid(bed_side, name):
    """bed_side='bottom'（箱）: 底の稜を 45°。'top'（蓋）: 天面の稜を 45°。"""
    prof = []
    if bed_side == "bottom":
        prof.append((0.0, C45))
        prof += round_profile(45, 90, R, 8)
        prof += round_profile(90, 177, L - R, 14)
    else:
        prof.append((55.0, 0.0))
        prof += round_profile(90, 135, L - R, 8)
        prof.append((L, C45))
    rings = []
    for z, d in prof:
        if rings and abs(rings[-1][0] - z) < 1e-6:
            continue
        rings.append((z, rrect(HALF - d, R - d)))
    return loft_rings(rings, name)


# ---------------------------------------------------------------------------
# 箱
# ---------------------------------------------------------------------------

def knuckle_bite_poly():
    """z>77 の帯から蝶番の円（5.05）をくり抜いた輪郭（箱の節の上を残す切り取り）。"""
    rr = R + 0.05
    dz = SPLIT - HZ
    dy = math.sqrt(rr * rr - dz * dz)
    a_l = math.degrees(math.atan2(dz, -dy))      # 左の交点（後ろ側）
    a_r = math.degrees(math.atan2(dz, dy))       # 右の交点（前側）
    arc = circle((HY, HZ), rr, 40, a_l, a_r, closed=False)   # 後ろ→上→前（時計回り）
    return [(-HALF - 5, SPLIT), *arc, (HALF + 5, SPLIT), (HALF + 5, L + 10), (-HALF - 5, L + 10)]


def knuckle_inner_poly():
    """箱の節が箱の内側へ張り出す部分＋下の 45° の支え。"""
    rr = R + 0.05
    tan_pt = (HY + rr * math.cos(math.radians(-45)), HZ + rr * math.sin(math.radians(-45)))
    z_at_wall = tan_pt[1] - (tan_pt[0] - (-IN - 0.2))
    a_top = math.degrees(math.asin((SPLIT + 0.5 - HZ) / rr))
    arc = circle((HY, HZ), rr, 24, -45, a_top, closed=False)
    return [(-IN - 0.2, z_at_wall), *arc, (-IN - 0.2, SPLIT + 0.5)]


def build_box():
    b = outer_solid("bottom", "box")
    # 上の帯を落とす（中央は全部、両端は節の円だけ残す）
    cut(b, box(-BKX, BKX, -HALF - 5, HALF + 5, SPLIT, L + 10, "top_mid"))
    for x0, x1 in ((-HALF - 5, -BKX), (BKX, HALF + 5)):
        cut(b, prism(knuckle_bite_poly(), "x", x0, x1, "top_end"))
    # 内側は z=77.5 まで（それより上の節の円は残す）
    cut(b, box(-IN, IN, -IN, IN, FLOOR, SPLIT + 0.5, "cavity"))
    # 節の内側の張り出しと支え
    for x0, x1 in ((-IN - 0.2, -BKX), (BKX, IN + 0.2)):
        union(b, prism(knuckle_inner_poly(), "x", x0, x1, "knuckle_in"))
    # 蓋の節が回る範囲を逃がす（45° の余分込み）
    cut(b, cyl_x((HY, HZ), mm(P.HINGE_SWEEP_R), -BKX, BKX, 96, "sweep"))

    # --- サーボの台 ---
    sz0 = OZ - mm(SG.BODY_W) / 2           # 本体の下側面 34.6
    sz1 = OZ + mm(SG.BODY_W) / 2           # 上側面 46.6
    clr = mm(P.SERVO_CLR)
    ped_top = sz0 - clr
    ped_x1 = mm(P.PED_X1)
    ped_y0, ped_y1 = mm(P.PED_Y0), mm(P.PED_Y1)
    union(b, box(-IN - 0.2, ped_x1, ped_y0, ped_y1, FLOOR - 0.2, ped_top, "pedestal"))
    # 本体の両端（配線側 y=-3.5、反対側 y=19.5）を止める壁
    near_end = OY - (mm(SG.BODY_CENTER_X) + mm(SG.BODY_L) / 2)          # X_s=+6.5 → y=3-6.5
    far_end = OY - (mm(SG.BODY_CENTER_X) - mm(SG.BODY_L) / 2)           # X_s=-16.5 → y=19.5
    ewt = mm(P.END_WALL_T)
    ew_top = sz1 + mm(P.END_WALL_ABOVE)
    ew_x1 = mm(P.END_WALL_X1)
    wall_n = box(-IN - 0.2, ew_x1, near_end - clr - ewt, near_end - clr, ped_top - 0.2, ew_top, "end_n")
    cut(wall_n, box(mm(P.WIRE_SLOT_X0), mm(P.WIRE_SLOT_X1), near_end - clr - ewt - 1, near_end - clr + 1,
                    OZ - 3.0, ew_top + 1, "wire_slot"))
    union(b, wall_n)
    union(b, box(-IN - 0.2, ew_x1, far_end + clr, far_end + clr + ewt, ped_top - 0.2, ew_top, "end_f"))
    # 取付耳を X で挟む柵
    ear_x0 = SX0 + mm(SG.FLANGE_BOTTOM_Z)
    ear_x1 = ear_x0 + mm(SG.FLANGE_T)
    ft = mm(P.EAR_FENCE_T)
    f_top = ped_top + mm(P.EAR_FENCE_TOP)
    fl_lo = OY - (mm(SG.BODY_CENTER_X) + mm(SG.FLANGE_L) / 2)   # 耳の後端 -8
    fl_hi = OY - (mm(SG.BODY_CENTER_X) - mm(SG.FLANGE_L) / 2)   # 耳の前端 24
    for ya, yb in ((fl_lo + 0.3, near_end - 0.5), (far_end + 0.5, fl_hi - 0.3)):
        union(b, box(ear_x0 - 0.25 - ft, ear_x0 - 0.25, ya, yb, ped_top - 0.2, f_top, "fence_a"))
        union(b, box(ear_x1 + 0.25, ear_x1 + 0.25 + ft, ya, yb, ped_top - 0.2, f_top, "fence_b"))
    # クリップの爪が掛かる溝（台の両端面）
    nz0 = mm(P.HOOK_Z) - 0.5
    nz1 = mm(P.HOOK_Z) + mm(P.HOOK_H) + 0.1
    hd = mm(P.HOOK_D)
    cx0, cx1 = mm(P.CLIP_X0) - 0.3, mm(P.CLIP_X1) + 0.3
    cut(b, box(cx0, cx1, ped_y0 - 1, ped_y0 + hd, nz0, nz1, "notch_n"))
    cut(b, box(cx0, cx1, ped_y1 - hd, ped_y1 + 1, nz0, nz1, "notch_f"))

    # --- クランク軸の受け（U 溝。+X への抜けと下・横の力を受ける）---
    u_hw = mm(P.U_COL_HW)
    u_top = OZ + mm(P.U_PRONG_H)
    blk = prism([(FIN_X0, FLOOR - 0.2), (mm(P.U_COL_X1), FLOOR - 0.2), (mm(P.U_COL_X1), u_top),
                 (LINK_X0, u_top), (LINK_X0, OZ - mm(P.U_OUT_R) - 0.2),
                 (FIN_X0, OZ - mm(P.U_OUT_R) - 0.2 - (FIN_X0 - LINK_X0))],
                "y", OY - u_hw, OY + u_hw, "u_block")
    slot = prism([(OY - mm(P.U_IN_R), OZ), (OY + mm(P.U_IN_R), OZ), (OY + mm(P.U_IN_R), u_top + 1),
                  (OY - mm(P.U_IN_R), u_top + 1)], "x", LINK_X0 - 1, FIN_X1, "u_slot")
    union(slot, cyl_x((OY, OZ), mm(P.U_IN_R), LINK_X0 - 1, FIN_X1, 64, "u_round"))
    cut(blk, slot)
    union(b, blk)

    # --- 蝶番の穴 ---
    hr_thru = mm(P.HINGE_HOLE_THRU_D) / 2
    hr_box = mm(P.HINGE_HOLE_BOX_D) / 2
    # 右の節: 奥は涙形、角の球面に出る最後の 3mm は丸穴（外から見える口を丸く）
    cut(b, prism(teardrop((HY, HZ), hr_thru, up=1), "x", BKX - 0.5, HALF - 3.0, "hole_r"))
    cut(b, cyl_x((HY, HZ), hr_thru, HALF - 3.2, HALF + 1, 64, "hole_r_out"))
    cut(b, prism(teardrop((HY, HZ), hr_box, up=1), "x", mm(P.HINGE_BLIND_END_X), -BKX + 0.5, "hole_l"))

    # --- 配線の出口（後ろの壁の下端）---
    cut(b, box(mm(P.WIRE_EXIT_X0), mm(P.WIRE_EXIT_X1), -HALF - 1, -IN + 0.1, -1, mm(P.WIRE_EXIT_H), "wire_exit"))
    b.name = "box"
    return b


# ---------------------------------------------------------------------------
# 蓋
# ---------------------------------------------------------------------------

def fin_poly():
    b0 = K.B0
    pts = circle(b0, mm(P.FIN_B_BOSS_R), 48) + circle((HY, HZ), R - 0.5, 48)
    pts += [(mm(P.FIN_ROOT_Y), SPLIT + 0.2), (mm(P.FIN_ROOT_Y), SPLIT - 0.4)]
    poly = hull(pts)
    # 後ろの壁の内面より前だけ（節の円の中は蓋の節と重なるので問題ない）
    back = mm(P.FIN_BACK_Y)
    clipped = []
    n = len(poly)
    for i in range(n):
        a, c = poly[i], poly[(i + 1) % n]
        ina, inc = a[0] >= back, c[0] >= back
        if ina:
            clipped.append(a)
        if ina != inc:
            t = (back - a[0]) / (c[0] - a[0])
            clipped.append((back, a[1] + t * (c[1] - a[1])))
    return clipped


def build_lid():
    lid = outer_solid("top", "lid")
    cut(lid, box(-HALF - 5, HALF + 5, -HALF - 5, HALF + 5, 50, SPLIT, "below"))
    # 蓋の節（中央）
    union(lid, cyl_x((HY, HZ), R - 0.02, -LKX, LKX, 96, "lid_knuckle"))
    # 箱の節の位置では蓋を逃がす
    for x0, x1 in ((-HALF - 1, -LKX), (LKX, HALF + 1)):
        cut(lid, cyl_x((HY, HZ), R + mm(P.KNUCKLE_GAP) + 0.05, x0, x1, 96, "bk_clear"))
    # 裏の縁（前と左右。後ろは蝶番があるので開けておく）
    so = IN - mm(P.LID_SKIRT_CLR)
    si = so - mm(P.LID_SKIRT_T)
    yb = mm(P.LID_SKIRT_BACK_Y)
    rc = 3.0
    ri = rc - (so - si)
    outer = ([(-so, yb)] + circle((-so + rc, so - rc), rc, 8, 180, 90, closed=False)
             + circle((so - rc, so - rc), rc, 8, 90, 0, closed=False) + [(so, yb)])
    inner = ([(si, yb)] + circle((si - ri, si - ri), ri, 8, 0, 90, closed=False)
             + circle((-si + ri, si - ri), ri, 8, 90, 180, closed=False) + [(-si, yb)])
    skirt_poly = outer + inner
    union(lid, prism(skirt_poly, "z", SPLIT - mm(P.LID_SKIRT_H), SPLIT + 0.2, "skirt"))
    # 耳（ピン B を受ける板）
    union(lid, prism(fin_poly(), "x", FIN_X0, FIN_X1, "fin"))
    # 穴（刷るときは裏返すので、尖りは組んだ姿勢の -Z 側）
    cut(lid, prism(teardrop((HY, HZ), mm(P.HINGE_HOLE_LID_D) / 2, up=-1), "x", -BKX, BKX, "lid_hole"))
    cut(lid, prism(teardrop(K.B0, mm(P.PIN_HOLE_R), up=-1), "x", FIN_X0 - 0.5, FIN_X1 + 0.5, "b_hole"))
    lid.name = "lid"
    return lid


# ---------------------------------------------------------------------------
# クランク（付属ホーンを包む）
# ---------------------------------------------------------------------------

def crank_frame(alpha):
    a = math.radians(alpha)
    u = (math.cos(a), math.sin(a))
    v = (-math.sin(a), math.cos(a))

    def f(pu, pv):
        return (OY + pu * u[0] + pv * v[0], OZ + pu * u[1] + pv * v[1])
    return f


def capsule(f, p0, p1, r, n=32):
    pts = circle(p0, r, n) + circle(p1, r, n)
    return [f(*p) for p in hull(pts)]


def horn_outline(clr):
    """ホーンの平面形（ホーン座標: hx = 長腕、hy = 短腕）を clr だけ太らせた部品群。"""
    tip = mm(SG.HORN_TIP_W) / 2 + clr
    root = mm(SG.HORN_ROOT_W) / 2 + clr
    hub = mm(SG.HORN_HUB_DIA) / 2 + clr
    left = mm(SG.HORN_LEFT_X) - clr
    right = mm(SG.HORN_RIGHT_X) + clr
    long_arm = hull(circle((left + tip, 0), tip, 24) + circle((right - tip, 0), tip, 24)
                    + [(-hub, -root), (-hub, root), (hub, -root), (hub, root)])
    # 根元が太く先が細い。左右それぞれ根元→先の台形で近似
    # 実物の腕は、ハブの径（±3.5）までは根元の幅のまま。そこから先へ細くなる
    root_x = mm(SG.HORN_HUB_DIA) / 2
    left_arm = hull(circle((left + tip, 0), tip, 24) + [(-root_x, -root), (-root_x, root), (0, -root), (0, root)])
    right_arm = hull(circle((right - tip, 0), tip, 24) + [(root_x, -root), (root_x, root), (0, -root), (0, root)])
    sl = mm(SG.HORN_SPAN_Y) / 2 + clr
    sw = mm(SG.HORN_SHORT_W) / 2 + clr
    short_arm = hull(circle((0, sl - sw), sw, 24) + circle((0, -sl + sw), sw, 24))
    hub_c = circle((0, 0), hub, 48)
    return [left_arm, right_arm, short_arm, hub_c], long_arm


def build_crank(alpha):
    f = crank_frame(alpha)
    a = K.A_LEN
    parts = [capsule(f, (mm(SG.HORN_LEFT_X) - 1.6, 0), (a, 0), mm(P.CRANK_ARM_HW)),
             capsule(f, (0, -mm(P.CRANK_SHORT_L)), (0, mm(P.CRANK_SHORT_L)), mm(P.CRANK_SHORT_HW)),
             [f(*p) for p in circle((0, 0), mm(P.CRANK_HUB_R), 48)]]
    cr = prism(parts[0], "x", CRANK_X0, CRANK_X1, "crank")
    for i, poly in enumerate(parts[1:]):
        union(cr, prism(poly, "x", CRANK_X0, CRANK_X1, f"crank_{i}"))
    # ホーンのポケット（-X 面から腕厚＋0.1）。口元は 0.2 広げて最初の層の膨らみを逃がす
    shapes, _ = horn_outline(mm(P.HORN_CLR))
    for i, poly in enumerate(shapes):
        cut(cr, prism([f(*p) for p in poly], "x", CRANK_X0 - 1, HORN_TOP, f"pocket_{i}"))
    shapes2, _ = horn_outline(mm(P.HORN_CLR) + 0.2)
    for i, poly in enumerate(shapes2):
        cut(cr, prism([f(*p) for p in poly], "x", CRANK_X0 - 1, CRANK_X0 + 0.3, f"mouth_{i}"))
    # 受けに入る軸
    union(cr, cyl_x((OY, OZ), mm(P.STUB_R), CRANK_X1 - 0.1, FIN_X1 - GAP, 48, "stub"))
    # ピン A（+X 向き）と、先端のバヨネットの爪
    pa = f(a, 0)
    pin_top = LINK_X1 + GAP + mm(P.TAB_T)
    union(cr, cyl_x(pa, mm(P.PIN_R), CRANK_X1 - 0.1, pin_top, 48, "pin_a"))
    phi = math.radians(P.BAYONET_KEY_DEG + 180.0 + alpha)   # 爪の向き（世界の YZ 角）
    t = (math.cos(phi), math.sin(phi))
    w = (-t[1], t[0])
    hw = mm(P.TAB_W) / 2
    r_in, r_out = mm(P.PIN_R) - 0.1, mm(P.TAB_R)
    x_lo = LINK_X1 + GAP
    x_mid = x_lo + (r_out - r_in)
    pts = []
    for rr, xx in ((r_in, x_lo), (r_out, x_mid), (r_out, pin_top), (r_in, pin_top)):
        for s in (-hw, hw):
            pts.append((xx, pa[0] + rr * t[0] + s * w[0], pa[1] + rr * t[1] + s * w[1]))
    union(cr, hull3d(pts, "tab"))
    cr.name = "crank"
    return cr


# ---------------------------------------------------------------------------
# リンク
# ---------------------------------------------------------------------------

def build_link(alpha, theta):
    pa = K.pin_a(alpha)
    pb = K.pin_b(theta)
    body = hull(circle(pa, mm(P.LINK_HW), 32) + circle(pb, mm(P.LINK_HW), 32))
    lk = prism(body, "x", LINK_X0, LINK_X1, "link")
    union(lk, cyl_x(pa, mm(P.LINK_A_BOSS_R), LINK_X0, LINK_X1, 64, "boss_a"))
    union(lk, cyl_x(pb, mm(P.LINK_B_BOSS_R), LINK_X0, LINK_X1, 64, "boss_b"))
    # A の穴と鍵溝（B と反対向き）
    cut(lk, cyl_x(pa, mm(P.PIN_HOLE_R), LINK_X0 - 1, LINK_X1 + 1, 48, "hole_a"))
    d = (pa[0] - pb[0], pa[1] - pb[1])
    n = math.hypot(*d)
    d = (d[0] / n, d[1] / n)
    w = (-d[1], d[0])
    kw = mm(P.KEYWAY_W) / 2
    kr = mm(P.KEYWAY_R)
    key = [(pa[0] + s * w[0] + rr * d[0], pa[1] + s * w[1] + rr * d[1])
           for rr, s in ((0, -kw), (kr, -kw), (kr, kw), (0, kw))]
    cut(lk, prism(key, "x", LINK_X0 - 1, LINK_X1 + 1, "keyway"))
    # ピン B（+X 向き、蓋の耳の穴に入る。先端を面取り）
    tip = FIN_X1
    ch = []
    for k in range(48):
        ang = 2 * math.pi * k / 48
        for rr, xx in ((mm(P.PIN_R), LINK_X1 - 0.3), (mm(P.PIN_R), tip - mm(P.LINK_PIN_CHAMFER)),
                       (mm(P.PIN_R) - mm(P.LINK_PIN_CHAMFER), tip)):
            ch.append((xx, pb[0] + rr * math.cos(ang), pb[1] + rr * math.sin(ang)))
    union(lk, hull3d(ch, "pin_b"))
    lk.name = "link"
    return lk


# ---------------------------------------------------------------------------
# 蝶番ピン（刷る姿勢で作る: 軸 X、平面が z=0）
# ---------------------------------------------------------------------------

def sphere(c, r, segs=96, rings=48, name="sphere"):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(c))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link_obj(bm, name)


def build_pin():
    """頭は付けない。右端は角の球面（中心は角の丸の中心）と同じ球面にして面一に納める。"""
    r = mm(P.HINGE_PIN_D) / 2
    flat = mm(P.HINGE_PIN_FLAT)
    x_tip = mm(P.HINGE_BLIND_END_X) + mm(P.HINGE_PIN_END_GAP)
    tip_r = mm(P.HINGE_TIP_D) / 2
    tip_l = mm(P.HINGE_TIP_L)
    pin = cyl_x((0, 0), r, x_tip + tip_l - 0.2, HALF + 1, 64, "pin")
    dome = box(HALF - R, HALF + 5, -10, 10, -10, 10, "dome_cut")
    cut(dome, sphere((HALF - R, 0, 0), R - 0.05, name="corner_sphere"))
    cut(pin, dome)
    union(pin, cyl_x((0, 0), tip_r, x_tip + 0.6, x_tip + tip_l, 64, "tip"))
    ch = []
    for k in range(64):
        ang = 2 * math.pi * k / 64
        for rr, xx in ((tip_r, x_tip + 0.61), (tip_r - 0.5, x_tip)):
            ch.append((xx, rr * math.cos(ang), rr * math.sin(ang)))
    union(pin, hull3d(ch, "tip_ch"))
    # 割り（刷る面に垂直 → 2 本の脚は刷る面内でたわむ）
    cut(pin, box(x_tip - 1, x_tip + mm(P.HINGE_SPLIT_L), -mm(P.HINGE_SPLIT_W) / 2, mm(P.HINGE_SPLIT_W) / 2,
                 -10, 10, "split"))
    # 寝かせて刷るための平面
    cut(pin, box(x_tip - 1, HALF + 1, -10, 10, -10, -r + flat, "flat"))
    pin.name = "pin"
    return pin


# ---------------------------------------------------------------------------
# サーボ押さえクリップ（コの字、上から押し込んで台の溝に爪を掛ける）
# ---------------------------------------------------------------------------

def clip_poly():
    sz1 = OZ + mm(SG.BODY_W) / 2
    y0, y1 = mm(P.PED_Y0), mm(P.PED_Y1)
    g = mm(P.CLIP_SIDE_GAP)
    lt = mm(P.CLIP_LEG_T)
    bz0 = sz1 + mm(P.CLIP_TOP_GAP)
    bz1 = bz0 + mm(P.CLIP_BRIDGE_T)
    hz0 = mm(P.HOOK_Z)
    hz1 = hz0 + mm(P.HOOK_H)
    hd = mm(P.HOOK_D) - 0.3
    ln_o, ln_i = y0 - g - lt, y0 - g          # 後ろの脚
    lf_i, lf_o = y1 + g, y1 + g + lt          # 前の脚
    return [
        (ln_o, hz0), (ln_i, hz0), (ln_i + hd, hz0 + hd), (ln_i + hd, hz1), (ln_i, hz1),
        (ln_i, bz0), (lf_i, bz0),
        (lf_i, hz1), (lf_i - hd, hz1), (lf_i - hd, hz0 + hd), (lf_i, hz0), (lf_o, hz0),
        (lf_o, bz1), (ln_o, bz1),
    ]


def build_clip():
    c = prism(clip_poly(), "x", mm(P.CLIP_X0), mm(P.CLIP_X1), "clip")
    c.name = "clip"
    return c


# ---------------------------------------------------------------------------
# 参考のサーボ（正本 sg92r-photo の STL をそのまま置く）
# ---------------------------------------------------------------------------

SERVO_MAT = Matrix(((0, 0, 1, SX0), (-1, 0, 0, OY), (0, -1, 0, OZ), (0, 0, 0, 1)))


def import_ref(name):
    path = os.path.join(EXPORTS_DIR, f"sg92r-photo-{name}.stl")
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=path)
    ob = [o for o in bpy.data.objects if o not in before][0]
    ob.name = f"ref_{name}"
    transform(ob, SERVO_MAT)
    return ob


def place_horn(ob, alpha):
    transform(ob, rot_x_about(alpha - 180.0, OY, OZ))


# ---------------------------------------------------------------------------
# 組み立て姿勢と刷る姿勢
# ---------------------------------------------------------------------------

def pose_matrices(theta):
    """閉じた姿勢で作った部品を、蓋角 θ の姿勢へ動かす行列。"""
    a0 = K.ALPHA0
    s = K.sweep(theta, 48) if theta > 0 else [(0.0, a0)]
    alpha = s[-1][1]
    lid_m = rot_x_about(theta, HY, HZ)
    crank_m = rot_x_about(alpha - a0, OY, OZ)
    pa0, pb0 = K.pin_a(a0), K.pin_b(0.0)
    pa1, pb1 = K.pin_a(alpha), K.pin_b(theta)
    d_ang = math.degrees(math.atan2(pb1[1] - pa1[1], pb1[0] - pa1[0]) - math.atan2(pb0[1] - pa0[1], pb0[0] - pa0[0]))
    link_m = Matrix.Translation((0, pa1[0] - pa0[0], pa1[1] - pa0[1])) @ rot_x_about(d_ang, pa0[0], pa0[1])
    return dict(lid=lid_m, crank=crank_m, link=link_m, alpha=alpha)


ROT_Y_UP = Matrix.Rotation(math.radians(-90), 4, "Y")   # +X → +Z（クランク・リンクを寝かせる）
FLIP_X = Matrix.Rotation(math.radians(180), 4, "X")     # 蓋を裏返す


def copy_obj(ob, name):
    c = ob.copy()
    c.data = ob.data.copy()
    c.name = name
    bpy.context.collection.objects.link(c)
    return c


def to_print(ob, mat):
    transform(ob, mat)
    xs = [v.co for v in ob.data.vertices]
    lo = Vector((min(p.x for p in xs), min(p.y for p in xs), min(p.z for p in xs)))
    hi = Vector((max(p.x for p in xs), max(p.y for p in xs), max(p.z for p in xs)))
    transform(ob, Matrix.Translation((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z)))


def bbox(ob):
    xs = [v.co for v in ob.data.vertices]
    return [round(min(p[i] for p in xs), 3) for i in range(3)], [round(max(p[i] for p in xs), 3) for i in range(3)]


def scale_to_m(objs):
    s = Matrix.Scale(1 / MM, 4)
    for o in objs:
        transform(o, s)


def save_stl(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True, global_scale=1.0)


def main():
    clear_scene()
    os.makedirs(BUILD, exist_ok=True)
    a0 = K.ALPHA0
    parts = {
        "box": build_box(),
        "lid": build_lid(),
        "crank": build_crank(a0),
        "link": build_link(a0, 0.0),
        "clip": build_clip(),
    }
    pin_print = build_pin()
    pin = copy_obj(pin_print, "pin_asm")
    transform(pin, Matrix.Translation((0, HY, HZ)))
    parts["pin"] = pin
    refs = {k: import_ref(k) for k in ("body", "horn", "wire")}
    place_horn(refs["horn"], a0)

    report = {"units": "mm", "parts": {}}
    for k, ob in list(parts.items()) + [("pin_print", pin_print)]:
        report["parts"][k] = dict(nonmanifold=nonmanifold(ob), nm_at=nonmanifold_where(ob),
                                  volume_mm3=round(volume(ob), 1), bbox=bbox(ob))
    report["linkage"] = dict(H=K.H, O=K.O, a=K.A_LEN, l=K.L_LINK, B0=K.B0, alpha0=a0,
                             layers=dict(crank=[CRANK_X0, CRANK_X1], link=[LINK_X0, LINK_X1],
                                         fin=[FIN_X0, FIN_X1]))

    # 開いた姿勢
    pm = pose_matrices(K.THETA_OPEN)
    opened = {}
    for k in ("lid", "crank", "link"):
        opened[k] = copy_obj(parts[k], f"{k}_open")
        transform(opened[k], pm[k])
    horn_open = copy_obj(refs["horn"], "horn_open")
    place_horn(horn_open, pm["alpha"] - a0 + 180.0)

    # build/ に組んだ姿勢の部品（検証用、mm）
    for k, ob in list(parts.items()) + [(f"ref_{k}", o) for k, o in refs.items()]:
        save_stl([ob], os.path.join(BUILD, f"{k}.stl"))

    # 刷る姿勢
    printed = {}
    for k, mat in (("box", Matrix.Identity(4)), ("lid", FLIP_X), ("crank", ROT_Y_UP),
                   ("link", ROT_Y_UP), ("clip", Matrix.Rotation(math.radians(90), 4, "Y"))):
        printed[k] = copy_obj(parts[k], f"{k}_print")
        to_print(printed[k], mat)
    printed["pin"] = pin_print
    to_print(pin_print, Matrix.Identity(4))
    for k, ob in printed.items():
        report["parts"][k]["print_bbox"] = bbox(ob)
        save_stl([ob], os.path.join(BUILD, f"print_{k}.stl"))

    asm = list(parts.values()) + list(refs.values())
    open_objs = [parts["box"], parts["pin"], parts["clip"], refs["body"], refs["wire"],
                 opened["lid"], opened["crank"], opened["link"], horn_open]
    all_objs = set(asm) | set(open_objs) | set(printed.values())
    scale_to_m(all_objs)
    export_stl(f"{NAME}-asm", only=asm)
    export_stl(f"{NAME}-open", only=open_objs)
    for k, ob in printed.items():
        export_stl(f"{NAME}-{k}", only=[ob])
    with open(os.path.join(BUILD, "model_report.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False))


main()
