"""角の床側を 1 枚にまとめた板（H2D 向け、294.7 角）。

    ./run.sh models/pipe-foot-corner-one/model.py
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from mathutils import Matrix
from blender_utils import clear_scene, EXPORTS_DIR
import foot_core as fc
import pair_base
import params as P
from params import *

Z_BUILD_BOT = -BASE_ROUND
HT = SPINE_T / 2


# ---------------------------------------------------------------- profiles

def arm_top(s):
    """脚列の背骨の上端。s は列の軸座標（脚は -CORNER_OFF と -CORNER_OFF-SPAN、中点 -MC）。"""
    t = (s + MC) / (SPAN / 2)
    return SPINE_MID_Z + (SPINE_TOP_Z - SPINE_MID_Z) * t * t


def branch_top(s, side):
    """枝の上端。J（脚の中点、軸座標 0 の節点）の面 -HT の高さから、F（軸座標 -MC）で
    SPINE_TOP_Z へ上がる。付け根の高さは列の背骨の -MC ± HT での高さに合わせる。"""
    z0 = arm_top(-MC + side * HT)
    t = min(1.0, max(0.0, (-HT - s) / (MC - HT)))
    return z0 + (SPINE_TOP_Z - z0) * t * t


def tie_top(s, side):
    """A1 → B1 の対角の壁。両端 SPINE_TOP_Z、中央 SPINE_MID_Z の二次曲線。"""
    t = (s - TIE_L / 2) / (TIE_L / 2)
    return SPINE_MID_Z + (SPINE_TOP_Z - SPINE_MID_Z) * t * t


def spine_net():
    """背骨の網。A の列（x 軸上）と B の列（y 軸上）はそれぞれ脚の中点 J で枝を出し、
    枝は中央レールの真下を通って 5 本目 F で出会う。"""
    nodes = {"J1": (-MC, 0.0), "J2": (0.0, -MC), "F": F}
    arm = lambda s, side: arm_top(s)
    n = SPINE_SEG // 2
    walls = [
        dict(axis="x", c=0.0, a=("free", A2[0]), b=("node", "J1"), top=arm, seg=n),
        dict(axis="x", c=0.0, a=("node", "J1"), b=("free", A1[0]), top=arm, seg=n),
        dict(axis="y", c=0.0, a=("free", B2[1]), b=("node", "J2"), top=arm, seg=n),
        dict(axis="y", c=0.0, a=("node", "J2"), b=("free", B1[1]), top=arm, seg=n),
        dict(axis="y", c=F[0], a=("node", "F"), b=("node", "J1"), top=branch_top, seg=BRANCH_SEG),
        dict(axis="x", c=F[1], a=("node", "F"), b=("node", "J2"), top=branch_top, seg=BRANCH_SEG),
    ]
    return fc.wall_net("spine", nodes, walls, SPINE_T, PLATE_T - SPINE_LAP)


def tie_wall():
    """A1 → B1 の対角の壁。ローカル x で作って -45° 回し、A1 に置く。"""
    ob = fc.wall_net("tie", {}, [
        dict(axis="x", c=0.0, a=("free", 0.0), b=("free", TIE_L), top=tie_top, seg=SPINE_SEG),
    ], SPINE_T, PLATE_T - SPINE_LAP)
    ob.matrix_world = fc.translate(*A1) @ Matrix.Rotation(math.radians(-45), 4, "Z")
    return ob


# ---------------------------------------------------------------- build

def build():
    # ソケットの軸と、そのひれの向き。脚 4 本は内側（板に余地がある側）へ 1 枚、5 本目は外側へ 2 枚
    sockets = [(A1, (-90.0,)), (A2, (-90.0,)), (B1, (180.0,)), (B2, (180.0,)),
               (F, (180.0, -90.0))]
    circles = [(A1[0], A1[1], EDGE_R), (A2[0], A2[1], EDGE_R),
               (B1[0], B1[1], EDGE_R), (B2[0], B2[1], EDGE_R), (F[0], F[1], PLATE_R)]
    body = fc.prism("pipe_foot_corner_one", fc.hull_circles(circles, 2 * SEG), Z_BUILD_BOT, PLATE_T)

    # ソケット 5 本（台座なし。根元の壁を厚くした筒）
    prof = fc.socket_profile_root(P, Z_BUILD_BOT)
    for k, (c, _) in enumerate(sockets):
        fc.boolean(body, fc.revolve("socket%d" % k, prof, fc.translate(*c), SEG), "UNION")

    fc.boolean(body, spine_net(), "UNION")
    fc.boolean(body, tie_wall(), "UNION")

    for k, (c, angs) in enumerate(sockets):
        for j, ang in enumerate(angs):
            fc.boolean(body, fc.fin("fin%d%d" % (k, j), P, c[0], c[1], ang), "UNION")

    fc.clean(body)
    fc.bevel(body, FILLET_R * MM, FILLET_SEG, FILLET_ANGLE)
    fc.boolean(body, fc.box_mm("cut_base", -400, 400, -400, 400, -100, 0), "DIFFERENCE")

    pair_base.bore_sockets(P, body, [c for c, _ in sockets])
    return pair_base.finish(P, body)


clear_scene()
pair_base.export(build(), EXPORTS_DIR, "pipe_foot_corner_one.stl")
