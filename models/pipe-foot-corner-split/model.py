"""角の床側の板を、パズルの凸凹つきで 2 枚に切る（X1C 向け）。

    ./run.sh models/pipe-foot-corner-split/model.py
    → exports/pipe_foot_corner_split_a.stl / _b.stl

板は lib/corner_plate.build_plate()（pipe-foot-corner-one と同じ形）に「節」（継ぎ目が壁を
横切る所の太い塊）を足して作り、継ぎ目の片側の領域（角柱）との共通部分を取って 2 枚にする。
凸凹はすべて z 方向の押し出しなので、B を A の上から落として組む。
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from mathutils import Matrix
from blender_utils import clear_scene, EXPORTS_DIR
import foot_core as fc
import pair_base
import corner_plate
from params import (ONE, SEAM_S0, SEAM_X, SEAM_TIE_XY, GAP, TAB_CLEAR, PLATE_TAB, KNUCKLE_TAB,
                    KNUCKLE_W, KNUCKLE_L, KNUCKLE_L_TAB, KNUCKLE_UP, KNUCKLE_CHAMFER, TABS)

FAR = 400.0          # 領域の角柱を板より十分大きく取る
Z_TOP = 300.0
S2 = math.sqrt(2.0)


def seam_frame(seg, pos):
    """継ぎ目上の点 p と、A → B の向き d（継ぎ目の法線）、継ぎ目に沿う向き t。"""
    if seg == "s1":
        p = (pos, pos)
        d = (1.0 / S2, -1.0 / S2)
    else:
        p = (SEAM_X, pos)
        d = (1.0, 0.0)
    return p, d, (-d[1], d[0])


def wall_height_at(seg):
    """継ぎ目が壁を横切る所の、壁の上端の高さ。"""
    if seg == "s1":
        return corner_plate.tie_top(ONE)(ONE.TIE_L / 2, 1)
    return corner_plate.branch_top(ONE)(SEAM_X, 1)


def knuckle_blocks():
    """節: 継ぎ目が壁を横切る所で、壁を幅 KNUCKLE_W の塊に太らせる。凹の側へ KNUCKLE_L、
    凸の側（持ち主の側）へ KNUCKLE_L_TAB。上面は壁の上端より KNUCKLE_UP 高く（面を重ねない）、
    端の上の角は 45° で落として、そこから壁が出て行く形にする。
    側面の輪郭 (s, z) を壁と直交する向きへ押し出す。s は A → B の向き。"""
    out = []
    for seg, pos, owner, kind in TABS:
        if kind != "knuckle":
            continue
        p, d, t = seam_frame(seg, pos)
        h = wall_height_at(seg) + KNUCKLE_UP
        c = KNUCKLE_CHAMFER
        la, lb = (KNUCKLE_L_TAB, KNUCKLE_L) if owner == "A" else (KNUCKLE_L, KNUCKLE_L_TAB)
        prof = [(-la, -1.0), (lb, -1.0), (lb, h - c), (lb - c, h), (-la + c, h), (-la, h - c)]
        m = (fc.translate(*p) @ Matrix.Rotation(math.atan2(d[1], d[0]), 4, "Z")
             @ Matrix.Rotation(math.radians(90), 4, "X"))
        out.append(fc.prism("knuckle_" + seg, prof, -KNUCKLE_W / 2, KNUCKLE_W / 2, m))
    return out


def tab_solids(owner, shrink, tag):
    """owner の側から相手の側へ出る凸（首 + 頭）。shrink だけ痩せさせる。
    板の凸凹は板の厚みまで、節の凸凹は節の上面の上まで。"""
    out = []
    for i, (seg, pos, o, kind) in enumerate(TABS):
        if o != owner:
            continue
        p, d, t = seam_frame(seg, pos)
        if owner == "B":
            d = (-d[0], -d[1])
        dim = KNUCKLE_TAB if kind == "knuckle" else PLATE_TAB
        z_top = (wall_height_at(seg) + KNUCKLE_UP if kind == "knuckle" else ONE.PLATE_T) + 1.0
        w = dim["neck_w"] / 2 - shrink
        a0, a1 = -1.0, dim["neck_l"]                # 首: 継ぎ目の 1 手前から頭の中心まで
        quad = [(p[0] + d[0] * a0 + t[0] * w, p[1] + d[1] * a0 + t[1] * w),
                (p[0] + d[0] * a1 + t[0] * w, p[1] + d[1] * a1 + t[1] * w),
                (p[0] + d[0] * a1 - t[0] * w, p[1] + d[1] * a1 - t[1] * w),
                (p[0] + d[0] * a0 - t[0] * w, p[1] + d[1] * a0 - t[1] * w)]
        out.append(fc.prism("%s_neck%d" % (tag, i), quad, -1.0, z_top))
        out.append(fc.cyl("%s_head%d" % (tag, i), dim["head_r"] - shrink, -1.0, z_top,
                          p[0] + d[0] * dim["neck_l"], p[1] + d[1] * dim["neck_l"], 64))
    return out


def side_poly(side, e):
    """継ぎ目から e だけ side（"A" / "B"）の側へ寄せた境界で、その側を覆う大きな多角形。
    継ぎ目 1 は x - y = 0 の線（A 側は x - y < 0）、継ぎ目 2 は x = SEAM_X の線（A 側は x < SEAM_X）。"""
    s = -1.0 if side == "A" else 1.0
    x2 = SEAM_X + s * e
    k = (x2, x2 - s * e * S2)                   # 2 本の線の交点
    top_t = 60.0                                # S0 の先（板の外）まで継ぎ目 1 を延ばす
    p_top = (SEAM_S0[0] + top_t + s * e / S2, SEAM_S0[1] + top_t - s * e / S2)
    if side == "A":
        return [p_top, (p_top[0], FAR), (-FAR, FAR), (-FAR, -FAR), (x2, -FAR), k]
    return [p_top, k, (x2, -FAR), (FAR, -FAR), (FAR, FAR), (p_top[0], FAR)]


def region(side):
    """side の片が占める領域。継ぎ目から GAP/2 寄せた境界 + 自分の凸（TAB_CLEAR 痩せ）
    - 相手の凹（図面の寸法）。A 側は折れ点で凹むので prism_concave で作る。"""
    reg = fc.prism_concave("region_" + side, side_poly(side, GAP / 2), -1.0, Z_TOP)
    for ob in tab_solids(side, TAB_CLEAR, "own"):
        fc.boolean(reg, ob, "UNION")
    other = "B" if side == "A" else "A"
    for ob in tab_solids(other, 0.0, "cut"):
        fc.boolean(reg, ob, "DIFFERENCE")
    return reg


def copy_of(ob, name):
    cp = ob.copy()
    cp.data = ob.data.copy()
    cp.name = name
    bpy.context.scene.collection.objects.link(cp)
    return cp


clear_scene()
plate = corner_plate.build_plate(ONE, "plate", extras=knuckle_blocks())
piece_b = copy_of(plate, "pipe_foot_corner_split_b")
piece_a = plate
piece_a.name = "pipe_foot_corner_split_a"

fc.boolean(piece_a, region("A"), "INTERSECT")
fc.boolean(piece_b, region("B"), "INTERSECT")
for ob in (piece_a, piece_b):
    pair_base.finish(ONE, ob)

pair_base.export(piece_a, EXPORTS_DIR, "pipe_foot_corner_split_a.stl")
pair_base.export(piece_b, EXPORTS_DIR, "pipe_foot_corner_split_b.stl")
