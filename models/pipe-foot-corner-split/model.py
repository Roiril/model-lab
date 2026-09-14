"""角の床側の板を、パズルの凸凹つきで 2 枚に切る（X1C 向け）。

    ./run.sh models/pipe-foot-corner-split/model.py
    → exports/pipe_foot_corner_split_a.stl / _b.stl

板は lib/corner_plate.build_plate()（pipe-foot-corner-one と同じ形）で作り、
継ぎ目の片側の領域（角柱）との共通部分を取って 2 枚にする。
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, EXPORTS_DIR
import foot_core as fc
import pair_base
import corner_plate
from params import (ONE, SEAM_S0, SEAM_X, GAP, TAB_CLEAR, TAB_NECK_W, TAB_NECK_L, TAB_HEAD_R, TAB_Z_TOP, TABS)

FAR = 400.0          # 領域の角柱を板より十分大きく取る
Z_TOP = 300.0
S2 = math.sqrt(2.0)


def side_poly(side, e):
    """継ぎ目から e だけ side（"A" / "B"）の側へ寄せた境界で、その側を覆う大きな多角形。
    継ぎ目 1 は x - y = 0 の線（A 側は x - y < 0）、継ぎ目 2 は x = SEAM_X の線（A 側は x < SEAM_X）。"""
    s = -1.0 if side == "A" else 1.0            # A へ寄せる = 継ぎ目 2 なら -x、継ぎ目 1 なら (+, -)... 符号で扱う
    # 継ぎ目 1 を e だけ寄せた線: x - y = s * e * √2。継ぎ目 2: x = SEAM_X + s * e
    x2 = SEAM_X + s * e
    k = (x2, x2 - s * e * S2)                   # 2 本の線の交点
    top_t = 60.0                                # S0 の先（板の外）まで継ぎ目 1 を延ばす
    p_top = (SEAM_S0[0] + top_t + s * e / S2, SEAM_S0[1] + top_t - s * e / S2)
    if side == "A":
        return [p_top, (p_top[0], FAR), (-FAR, FAR), (-FAR, -FAR), (x2, -FAR), k]
    return [p_top, k, (x2, -FAR), (FAR, -FAR), (FAR, FAR), (p_top[0], FAR)]


def tab_solids(owner, shrink, tag):
    """owner の側から相手の側へ出る凸（首の箱 + 頭の円柱）。shrink だけ痩せさせる。

    継ぎ目 1（x = y、S0 → K）では凸の向きは (1, -1)/√2（B 側）か (-1, 1)/√2（A 側）。
    継ぎ目 2（x = SEAM_X、下向き）では (1, 0) か (-1, 0)。
    """
    out = []
    for i, (seg, pos, o) in enumerate(TABS):
        if o != owner:
            continue
        if seg == "s1":
            p = (pos, pos)
            d = (1.0 / S2, -1.0 / S2)               # A → B の向き
        else:
            p = (SEAM_X, pos)
            d = (1.0, 0.0)
        if owner == "B":
            d = (-d[0], -d[1])
        t = (-d[1], d[0])                           # 継ぎ目に沿う向き
        w = TAB_NECK_W / 2 - shrink
        a0, a1 = -1.0, TAB_NECK_L                   # 首: 継ぎ目の 1 手前から頭の中心まで
        quad = [(p[0] + d[0] * a0 + t[0] * w, p[1] + d[1] * a0 + t[1] * w),
                (p[0] + d[0] * a1 + t[0] * w, p[1] + d[1] * a1 + t[1] * w),
                (p[0] + d[0] * a1 - t[0] * w, p[1] + d[1] * a1 - t[1] * w),
                (p[0] + d[0] * a0 - t[0] * w, p[1] + d[1] * a0 - t[1] * w)]
        out.append(fc.prism("%s_neck%d" % (tag, i), quad, -1.0, TAB_Z_TOP))
        out.append(fc.cyl("%s_head%d" % (tag, i), TAB_HEAD_R - shrink, -1.0, TAB_Z_TOP,
                          p[0] + d[0] * TAB_NECK_L, p[1] + d[1] * TAB_NECK_L, 64))
    return out


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
plate = corner_plate.build_plate(ONE, "plate")
piece_b = copy_of(plate, "pipe_foot_corner_split_b")
piece_a = plate
piece_a.name = "pipe_foot_corner_split_a"

fc.boolean(piece_a, region("A"), "INTERSECT")
fc.boolean(piece_b, region("B"), "INTERSECT")
for ob in (piece_a, piece_b):
    pair_base.finish(ONE, ob)

pair_base.export(piece_a, EXPORTS_DIR, "pipe_foot_corner_split_a.stl")
pair_base.export(piece_b, EXPORTS_DIR, "pipe_foot_corner_split_b.stl")
