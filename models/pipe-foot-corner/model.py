"""M 字ジョイント 2 つが直角に出会う角のベース（脚 4 本 + 5 本目）。

    ./run.sh models/pipe-foot-corner/model.py

形づくりの部品は lib/foot_core.py（pipe-foot-pair と共有）。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, EXPORTS_DIR
import foot_core as fc
import params as P
from params import *

# 角丸を作るために下へ伸ばしておき、最後に z=0 で切る
Z_BUILD_BOT = -BASE_ROUND
HT = SPINE_T / 2


# ---------------------------------------------------------------- profiles

def arm_top(s):
    """脚列の背骨の上端。s は軸座標（角の節点が 0、脚は -CORNER_OFF と -CORNER_OFF-SPAN）。

    脚 2 本のあいだ: pipe-foot-pair と同じ、中央で最も低い二次曲線。
    角に近い脚から角まで: 同じ曲率で角が最も低くなる二次曲線。
    どちらも脚の軸で SPINE_TOP_Z になり、継ぎ目はソケットの肉の中。
    """
    if s <= -CORNER_OFF:
        t = (s + CORNER_OFF + SPAN / 2) / (SPAN / 2)
        return SPINE_MID_Z + (SPINE_TOP_Z - SPINE_MID_Z) * t * t
    return CORNER_Z + SPINE_CURV * s * s


def branch_top(s_face, s_tip, root_of_side):
    """枝の上端。付け根の面（s_face）の高さから、先端の軸（s_tip）で SPINE_TOP_Z へ上がる。

    付け根の面の 2 隅は、背骨の傾きのぶん高さが違う。側ごとに自分の隅の高さから
    同じ二次曲線で上がり、先端で揃う。
    """
    def top(s, side):
        z0 = root_of_side(side)
        t = min(1.0, max(0.0, (s - s_face) / (s_tip - s_face)))
        return z0 + (SPINE_TOP_Z - z0) * t * t
    return top


def spine_net():
    """背骨の網。X 列と Y 列の背骨が角で出会い、5 本目へは各列から枝が 1 本ずつ出る。

    節点は 4 つ。角 C、X 列の枝の付け根 J1、Y 列の枝の付け根 J2、5 本目の軸 F。
    F を節点にするのは、2 本の枝がソケットの中で重ならず 1 つの殻になるようにするため。
    """
    fo = FIFTH_OFF
    nodes = {"C": (0.0, 0.0), "J1": (-fo, 0.0), "J2": (0.0, -fo), "F": (-fo, -fo)}
    arm = lambda s, side: arm_top(s)
    n_arm = SPINE_SEG // 2
    # 枝: F から J1（+Y へ）と J2（+X へ）。付け根の面は節点の芯の -y / -x 面（軸座標 -HT）で、
    # その 2 隅の高さは列の背骨の軸座標 -fo ± HT での高さ。2 本は対称なので同じ関数
    br = branch_top(-HT, -fo, lambda side: arm_top(-fo + side * HT))
    walls = [
        dict(axis="x", c=0.0, a=("free", A2[0]), b=("node", "J1"), top=arm, seg=n_arm),
        dict(axis="x", c=0.0, a=("node", "J1"), b=("node", "C"), top=arm, seg=n_arm),
        dict(axis="y", c=0.0, a=("free", B2[1]), b=("node", "J2"), top=arm, seg=n_arm),
        dict(axis="y", c=0.0, a=("node", "J2"), b=("node", "C"), top=arm, seg=n_arm),
        dict(axis="y", c=-fo, a=("node", "F"), b=("node", "J1"), top=br, seg=BRANCH_SEG),
        dict(axis="x", c=-fo, a=("node", "F"), b=("node", "J2"), top=br, seg=BRANCH_SEG),
    ]
    return fc.wall_net("spine", nodes, walls, SPINE_T, PLATE_T - SPINE_LAP)


# ---------------------------------------------------------------- build

def plate_outline():
    """床に着く板の輪郭。反時計回り。どの継ぎ目も接線がつながる。

    遠い端（-227, 0）から: 内側へ広がる弧（END_R）→ 斜辺 → もう一方の遠い端の弧 →
    遠い端の外側の半円（OUTER_R）→ 外側の直線 → 角の 1/4 円（OUTER_R）→ 外側の直線 →
    遠い端の外側の半円。遠い端の点で半径 OUTER_R と END_R の円が内接する
    （END_R の中心は軸から END_R - OUTER_R だけ角の側）。
    """
    ro, re = OUTER_R, END_R
    ca = (A2[0] + (re - ro), 0.0)            # X 列の遠い端、内側の弧の中心
    cb = (0.0, B2[1] + (re - ro))            # Y 列の遠い端
    n = SEG // 4
    return fc.chain(
        fc.arc(ca, re, 180, 225, n // 2),    # 遠い端 → 斜辺の接点
        fc.arc(cb, re, 225, 270, n // 2),    # 斜辺（直線）→ もう一方の遠い端
        fc.arc(B2, ro, 270, 360, n),         # 遠い端の外側の半円
        fc.arc((0.0, 0.0), ro, 0, 90, n),    # 外側の直線（x = OUTER_R）→ 角の 1/4 円
        fc.arc(A2, ro, 90, 180, n),          # 外側の直線（y = OUTER_R）→ 遠い端の外側の半円
    )


def build():
    # ソケットの軸と、そのひれの向き。ひれは背骨と直交し、板に余地がある内側へ出す
    sockets = [(A1, (-90.0,)), (A2, (-90.0,)), (B1, (180.0,)), (B2, (180.0,)),
               (FIFTH, (180.0, -90.0))]

    body = fc.prism("pipe_foot_corner", plate_outline(), Z_BUILD_BOT, PLATE_T)

    # ソケット 5 本（台座なし。板から FOOT_R の丸みで筒が立つ）
    prof = fc.socket_profile_plain(P, Z_BUILD_BOT, FOOT_R)
    for k, (c, _) in enumerate(sockets):
        fc.boolean(body, fc.revolve("socket%d" % k, prof, fc.translate(*c), SEG), "UNION")

    # 背骨の網
    fc.boolean(body, spine_net(), "UNION")

    # 横のひれ 6 枚
    for k, (c, angs) in enumerate(sockets):
        for j, ang in enumerate(angs):
            fc.boolean(body, fc.fin("fin%d%d" % (k, j), P, c[0], c[1], ang), "UNION")

    # 接合部に R
    fc.clean(body)
    fc.bevel(body, FILLET_R * MM, FILLET_SEG, FILLET_ANGLE)

    # 底を平らに切る
    fc.boolean(body, fc.box_mm("cut_base", -400, 400, -400, 400, -100, 0), "DIFFERENCE")

    # パイプの穴（座面まで）
    for k, (c, _) in enumerate(sockets):
        fc.boolean(body, fc.cyl("bore%d" % k, BORE_D / 2, SEAT_Z, BOSS_TOP + 10, c[0], c[1], SEG),
                   "DIFFERENCE")

    # 穴あけが残す極小のスリバーを潰す（pipe-foot-pair と同じ 0.02mm）
    fc.clean(body, dist=2e-5)

    fc.activate(body)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_flat()
    return body


clear_scene()
body = build()

os.makedirs(EXPORTS_DIR, exist_ok=True)
stl = os.path.join(EXPORTS_DIR, "pipe_foot_corner.stl")
fc.activate(body)
bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True,
                      global_scale=1000.0, ascii_format=False)
print("Exported:", stl)
print("bbox mm:", [round(v * 1000, 2) for v in body.dimensions])
