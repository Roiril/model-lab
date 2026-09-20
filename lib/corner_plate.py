"""角の床側を 1 枚にまとめた板の形づくり（pipe-foot-corner-one / pipe-foot-corner-split で共有）。

寸法は params モジュール P（pipe-foot-corner-one の params）から取る。
世界座標: 角の節点が原点、A の脚が x 軸上の負側、B の脚が y 軸上の負側、床が z=0。
"""
import math

from mathutils import Matrix
import foot_core as fc
import pair_base


def arm_top(P, s):
    """脚列の背骨の上端。s は列の軸座標（脚は -CORNER_OFF と -CORNER_OFF-SPAN、中点 -MC）。"""
    t = (s + P.MC) / (P.SPAN / 2)
    return P.SPINE_MID_Z + (P.SPINE_TOP_Z - P.SPINE_MID_Z) * t * t


def branch_top(P):
    """枝の上端。J（脚の中点、軸座標 0 の節点）の面 -HT の高さから、F（軸座標 -MC）で
    SPINE_TOP_Z へ上がる。付け根の高さは列の背骨の -MC ± HT での高さに合わせる。"""
    ht = P.SPINE_T / 2

    def top(s, side):
        z0 = arm_top(P, -P.MC + side * ht)
        t = min(1.0, max(0.0, (-ht - s) / (P.MC - ht)))
        return z0 + (P.SPINE_TOP_Z - z0) * t * t
    return top


def tie_top(P):
    """A1 → B1 の対角の壁。両端 SPINE_TOP_Z、中央 TIE_MID_Z の二次曲線。"""
    def top(s, side):
        t = (s - P.TIE_L / 2) / (P.TIE_L / 2)
        return P.TIE_MID_Z + (P.SPINE_TOP_Z - P.TIE_MID_Z) * t * t
    return top


def spine_net(P):
    """背骨の網。A の列（x 軸上）と B の列（y 軸上）はそれぞれ脚の中点 J で枝を出し、
    枝は中央レールの真下を通って 5 本目 F で出会う。"""
    nodes = {"J1": (-P.MC, 0.0), "J2": (0.0, -P.MC), "F": P.F}
    arm = lambda s, side: arm_top(P, s)
    br = branch_top(P)
    n = P.SPINE_SEG // 2
    walls = [
        dict(axis="x", c=0.0, a=("free", P.A2[0]), b=("node", "J1"), top=arm, seg=n),
        dict(axis="x", c=0.0, a=("node", "J1"), b=("free", P.A1[0]), top=arm, seg=n),
        dict(axis="y", c=0.0, a=("free", P.B2[1]), b=("node", "J2"), top=arm, seg=n),
        dict(axis="y", c=0.0, a=("node", "J2"), b=("free", P.B1[1]), top=arm, seg=n),
        dict(axis="y", c=P.F[0], a=("node", "F"), b=("node", "J1"), top=br, seg=P.BRANCH_SEG),
        dict(axis="x", c=P.F[1], a=("node", "F"), b=("node", "J2"), top=br, seg=P.BRANCH_SEG),
    ]
    return fc.wall_net("spine", nodes, walls, P.SPINE_T, P.PLATE_T - P.SPINE_LAP)


def tie_wall(P):
    """A1 → B1 の対角の壁。ローカル x で作って -45° 回し、A1 に置く。"""
    ob = fc.wall_net("tie", {}, [
        dict(axis="x", c=0.0, a=("free", 0.0), b=("free", P.TIE_L), top=tie_top(P), seg=P.SPINE_SEG),
    ], P.SPINE_T, P.PLATE_T - P.SPINE_LAP)
    ob.matrix_world = fc.translate(*P.A1) @ Matrix.Rotation(math.radians(-45), 4, "Z")
    return ob


def sockets(P):
    """ソケットの軸と、そのひれの向き。脚 4 本は内側（板に余地がある側）へ 1 枚、5 本目は外側へ 2 枚。"""
    return [(P.A1, (-90.0,)), (P.A2, (-90.0,)), (P.B1, (180.0,)), (P.B2, (180.0,)),
            (P.F, (180.0, -90.0))]


def build_plate(P, name, extras=()):
    """板 + ソケット 5 本 + 背骨 + 対角の壁 + ひれ、穴あけまで済ませて返す。
    extras: bevel の前に union する追加の立体（分割版の節など）。"""
    z_bot = -P.BASE_ROUND
    socks = sockets(P)
    circles = [(P.A1[0], P.A1[1], P.EDGE_R), (P.A2[0], P.A2[1], P.EDGE_R),
               (P.B1[0], P.B1[1], P.EDGE_R), (P.B2[0], P.B2[1], P.EDGE_R),
               (P.F[0], P.F[1], P.PLATE_R)]
    body = fc.prism(name, fc.hull_circles(circles, 2 * P.SEG), z_bot, P.PLATE_T)

    # ソケット 5 本（台座なし。根元の壁を厚くした筒）
    prof = fc.socket_profile_root(P, z_bot)
    for k, (c, _) in enumerate(socks):
        fc.boolean(body, fc.revolve("socket%d" % k, prof, fc.translate(*c), P.SEG), "UNION")

    fc.boolean(body, spine_net(P), "UNION")
    fc.boolean(body, tie_wall(P), "UNION")
    for ob in extras:
        fc.boolean(body, ob, "UNION")

    for k, (c, angs) in enumerate(socks):
        for j, ang in enumerate(angs):
            fc.boolean(body, fc.fin("fin%d%d" % (k, j), P, c[0], c[1], ang), "UNION")

    fc.clean(body)
    fc.bevel(body, P.FILLET_R * fc.MM, P.FILLET_SEG, P.FILLET_ANGLE)
    fc.boolean(body, fc.box_mm("cut_base", -400, 400, -400, 400, -100, 0), "DIFFERENCE")

    pair_base.bore_sockets(P, body, [c for c, _ in socks])
    return pair_base.finish(P, body)
