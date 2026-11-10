"""uHand の動きの計算（bpy を使わない。Blender からも検査からも同じ物を呼ぶ）。

動かせる量は 6 個で、実物のサーボ 6 個に対応する。
  little / ring / middle / index : 0（寸法図の姿勢）〜 1（握る）
  thumb                          : 0（寸法図の姿勢）〜 1（手のひらへ倒す）
  wrist                          : -1 〜 1（手首の回転。0 が正面）

指は 1 個の量から 3 つの関節と銀の板 2 枚の姿勢が決まる（実物と同じ 4 節リンク）。
  付け根の角度 = 量 x FINGER_MCP_MAX
  S 字の板（手のひらの板の受け H と中節の尾 G をつなぐ）の長さが変わらない条件から、次の関節の角度
  銀の連結板（基節の A と末節の D をつなぐ）の長さが変わらない条件から、指先の関節の角度

pose(dofs) は部品ごとの 4x4 行列（mm、何もしないとき単位行列）を返す。部品の名前は BONES の名前。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P

FINGERS = ("little", "ring", "middle", "index")
# 量: (最小, 最大, 何もしないときの値)
DOFS = {
    "little": (0.0, 1.0, 0.0), "ring": (0.0, 1.0, 0.0), "middle": (0.0, 1.0, 0.0), "index": (0.0, 1.0, 0.0),
    "thumb": (0.0, 1.0, 0.0), "wrist": (-1.0, 1.0, 0.0),
}
FINGER_MCP_MAX = 60.0     # 付け根の最大の曲げ [deg]。このとき次の関節は約 76 度、指先は約 60 度
THUMB_PROX_MAX = 46.0     # 親指の基節が手のひら側へ倒れる角度 [deg]
THUMB_TIP_MAX = 38.0      # 親指の末節の曲げ [deg]
WRIST_MAX = 90.0


# ---- 小さな行列の道具（4x4、行優先のリスト） ------------------------------
def ident():
    return [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]


def mul(*ms):
    out = ms[0]
    for m in ms[1:]:
        out = [[sum(out[i][k] * m[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
    return out


def trans(v):
    m = ident()
    for i in range(3):
        m[i][3] = v[i]
    return m


def apply(m, p):
    return tuple(m[i][0] * p[0] + m[i][1] * p[1] + m[i][2] * p[2] + m[i][3] for i in range(3))


def inv_rigid(m):
    """回転と平行移動だけの行列の逆。"""
    r = [[m[j][i] for j in range(3)] for i in range(3)]
    t = [-sum(r[i][k] * m[k][3] for k in range(3)) for i in range(3)]
    return [r[0] + [t[0]], r[1] + [t[1]], r[2] + [t[2]], [0.0, 0.0, 0.0, 1.0]]


def rot_axis(axis, ang, point=(0.0, 0.0, 0.0)):
    """点 point を通る軸 axis まわりの回転（ロドリゲス）。"""
    n = math.sqrt(sum(a * a for a in axis))
    x, y, z = (a / n for a in axis)
    c, s = math.cos(ang), math.sin(ang)
    C = 1 - c
    r = [[c + x * x * C, x * y * C - z * s, x * z * C + y * s, 0.0],
         [y * x * C + z * s, c + y * y * C, y * z * C - x * s, 0.0],
         [z * x * C - y * s, z * y * C + x * s, c + z * z * C, 0.0],
         [0.0, 0.0, 0.0, 1.0]]
    return mul(trans(point), r, trans([-v for v in point]))


def vsub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def vadd(a, b):
    return tuple(x + y for x, y in zip(a, b))


def vlen(a):
    return math.sqrt(sum(x * x for x in a))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def aim(pivot_rest, pivot_new, d0, d1, stretch=1.0):
    """pivot_rest にある棒（向き d0）を、pivot_new から向き d1 へ向け直す。stretch で棒の向きに伸び縮みさせる。"""
    l0, l1 = vlen(d0), vlen(d1)
    u0, u1 = tuple(x / l0 for x in d0), tuple(x / l1 for x in d1)
    ax = cross(u0, u1)
    s = vlen(ax)
    r = ident() if s < 1e-9 else rot_axis(ax, math.atan2(s, dot(u0, u1)))
    sc = ident()
    if abs(stretch - 1.0) > 1e-9:
        for i in range(3):
            for j in range(3):
                sc[i][j] += (stretch - 1.0) * u0[i] * u0[j]
    return mul(trans(pivot_new), r, sc, trans([-v for v in pivot_rest]))


# ---- 指（面内の 2D で解く。座標は (y, z)） -------------------------------
def _r2(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def _solve(v, g, L, prev):
    """|v - R(a) g| = L になる角度 a。2 つの解のうち prev に近いほう。解が無ければ None。"""
    nv, ng = math.hypot(*v), math.hypot(*g)
    K = (nv * nv + ng * ng - L * L) / (2 * nv * ng)
    if abs(K) > 1.0:
        return None
    base = math.atan2(v[1], v[0]) - math.atan2(g[1], g[0])
    cands = [base + math.acos(K), base - math.acos(K)]
    cands = [((c - prev + math.pi) % (2 * math.pi)) - math.pi + prev for c in cands]
    return min(cands, key=lambda c: abs(c - prev))


def finger_points(i):
    """指 i の、寸法図の姿勢での面内の点。"""
    dz = P.FINGER_DZ[i]
    sh = lambda p: (p[0], p[1] + dz)
    return dict(mcp=sh(P.F_MCP), pip=sh(P.F_PIP), dip=sh(P.F_DIP), g=sh(P.F_G), a=sh(P.F_A), d=sh(P.F_D),
                rb=sh(P.F_ROD_BOTTOM), rt=sh(P.F_ROD_TOP),
                h=(P.HOOK_PIVOT[0], P.STEP_Z[i] + P.HOOK_PIVOT[1]))


def finger_solve(i, u, steps=24):
    """指 i を量 u まで曲げたときの面内の姿勢。0 から少しずつ進めて、解の枝を取り違えないようにする。
    返す角度は rad。mid と tip は寸法図の姿勢からの絶対の回転。"""
    q = finger_points(i)
    Ls = math.hypot(q["g"][0] - q["h"][0], q["g"][1] - q["h"][1])
    Ld = math.hypot(q["d"][0] - q["a"][0], q["d"][1] - q["a"][1])
    alpha = beta = 0.0
    n = max(1, int(math.ceil(abs(u) * steps)))
    for k in range(1, n + 1):
        t1 = math.radians(FINGER_MCP_MAX) * u * k / n
        pip = vadd2(q["mcp"], _r2(vsub2(q["pip"], q["mcp"]), t1))
        a2 = _solve(vsub2(q["h"], pip), vsub2(q["g"], q["pip"]), Ls, alpha)
        if a2 is None:
            raise ValueError(f"finger {FINGERS[i]}: S 字の板が届かない (u={u * k / n:.3f})")
        alpha = a2
        dip = vadd2(pip, _r2(vsub2(q["dip"], q["pip"]), alpha))
        ap = vadd2(q["mcp"], _r2(vsub2(q["a"], q["mcp"]), t1))
        b2 = _solve(vsub2(ap, dip), vsub2(q["d"], q["dip"]), Ld, beta)
        if b2 is None:
            raise ValueError(f"finger {FINGERS[i]}: 銀の連結板が届かない (u={u * k / n:.3f})")
        beta = b2
    t1 = math.radians(FINGER_MCP_MAX) * u
    pip = vadd2(q["mcp"], _r2(vsub2(q["pip"], q["mcp"]), t1))
    dip = vadd2(pip, _r2(vsub2(q["dip"], q["pip"]), alpha))
    g = vadd2(pip, _r2(vsub2(q["g"], q["pip"]), alpha))
    ap = vadd2(q["mcp"], _r2(vsub2(q["a"], q["mcp"]), t1))
    dp = vadd2(dip, _r2(vsub2(q["d"], q["dip"]), beta))
    rt = vadd2(q["mcp"], _r2(vsub2(q["rt"], q["mcp"]), t1))
    ang = lambda a, b: math.atan2(b[1] - a[1], b[0] - a[0])
    return dict(prox=t1, mid=alpha, tip=beta, pip=pip, dip=dip, g=g, a=ap, d=dp, rt=rt,
                slink=ang(q["h"], g) - ang(q["h"], q["g"]),
                link=ang(ap, dp) - ang(q["a"], q["d"]),
                rod=ang(q["rb"], rt) - ang(q["rb"], q["rt"]),
                rod_stretch=math.hypot(rt[0] - q["rb"][0], rt[1] - q["rb"][1])
                / math.hypot(q["rt"][0] - q["rb"][0], q["rt"][1] - q["rb"][1]))


def vadd2(a, b):
    return (a[0] + b[0], a[1] + b[1])


def vsub2(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _plane(ang, rest, new, x=0.0):
    """面内 (y, z) の剛体の動き（rest の点を new へ運び、ang だけ回す）を 3D の行列にする。"""
    return mul(trans((0.0, new[0], new[1])), rot_axis((1, 0, 0), ang), trans((0.0, -rest[0], -rest[1])))


def finger_fan(i):
    """指 i を付け根の軸まわりに扇に開く行列（model.py と同じ）。"""
    q = finger_points(i)
    c = (P.FINGER_X[i], q["mcp"][0], q["mcp"][1])
    return rot_axis((0, 1, 0), math.radians(P.FINGER_FAN[i]), c)


def finger_pose(i, u):
    nm = FINGERS[i]
    q = finger_points(i)
    s = finger_solve(i, u)
    F = finger_fan(i)
    Fi = inv_rigid(F)
    out = {
        f"{nm}_prox": mul(F, _plane(s["prox"], q["mcp"], q["mcp"]), Fi),
        f"{nm}_mid": mul(F, _plane(s["mid"], q["pip"], s["pip"]), Fi),
        f"{nm}_tip": mul(F, _plane(s["tip"], q["dip"], s["dip"]), Fi),
        f"{nm}_link": mul(F, _plane(s["link"], q["a"], s["a"]), Fi),
        f"{nm}_slink": _plane(s["slink"], q["h"], q["h"]),      # 手のひらの板に付くので扇に開かない
    }
    # 引き棒: 下端は動かず、上端が基節に付いて行く。棒の向きに伸び縮みさせる
    d0 = (0.0, q["rt"][0] - q["rb"][0], q["rt"][1] - q["rb"][1])
    d1 = (0.0, s["rt"][0] - q["rb"][0], s["rt"][1] - q["rb"][1])
    rb = (0.0, q["rb"][0], q["rb"][1])
    out[f"{nm}_rod"] = mul(F, aim(rb, rb, d0, d1, s["rod_stretch"]), Fi)
    return out


# ---- 親指 ---------------------------------------------------------------
def thumb_frame():
    t = math.radians(P.THUMB_TILT)
    e1 = (math.cos(t), 0.0, -math.sin(t))
    e2 = (0.0, -1.0, 0.0)
    return e1, e2, cross(e1, e2), P.THUMB_ORIGIN


def thumb_pt(a, b, h=0.0):
    e1, e2, n, o = thumb_frame()
    return tuple(o[k] + e1[k] * a + e2[k] * b + n[k] * h for k in range(3))


def thumb_points():
    d = math.radians(P.THUMB_DIR)
    du = (math.cos(d), math.sin(d))
    pv = (P.THUMB_PIVOT_A, 0.0)
    jt = (pv[0] + du[0] * P.THUMB_PROX_LEN, pv[1] + du[1] * P.THUMB_PROX_LEN)
    st = (pv[0] + du[0] * P.THUMB_STRUT, pv[1] + du[1] * P.THUMB_STRUT)
    hx, hz = P.HORN_TIP
    sx, sz = P.THUMB_SERVO_SHAFT
    return dict(pivot=thumb_pt(pv[0], pv[1], 5.0), joint=thumb_pt(jt[0], jt[1], 5.0),
                strut=thumb_pt(st[0], st[1], P.THUMB_LAYERS["lower"][1] + 9.5),
                horn_tip=(hx, P.HORN_Y - 2.8, hz), shaft=(sx, P.HORN_Y, sz),
                crank_f=tuple(P.THUMB_CRANK_F), crank_t=tuple(P.THUMB_CRANK_T))


def thumb_pose(u):
    """親指。基節が付け根の軸まわりに手のひら側へ倒れ、末節が関節で曲がる。
    ホーンは、押し棒の長さが変わらない角度まで回る。銀のクランクは固定側から親指を追う（伸び縮みで合わせる）。"""
    e1, e2, n, o = thumb_frame()
    q = thumb_points()
    Wp = rot_axis(n, math.radians(THUMB_PROX_MAX) * u, q["pivot"])
    Wt = mul(Wp, rot_axis(n, math.radians(THUMB_TIP_MAX) * u, q["joint"]))
    strut = apply(Wp, q["strut"])
    L = vlen(vsub(q["strut"], q["horn_tip"]))

    def err(g):
        tip = apply(rot_axis((0, 1, 0), g, q["shaft"]), q["horn_tip"])
        return vlen(vsub(strut, tip)) - L

    # 0 から外へ向けて符号の変わる所を探し、二分法で詰める
    gamma, found = 0.0, abs(err(0.0)) < 1e-9
    if not found:
        step = math.radians(1.0)
        for k in range(1, 121):
            for sgn in (1, -1):
                g0, g1 = sgn * (k - 1) * step, sgn * k * step
                if err(g0) * err(g1) <= 0:
                    for _ in range(40):
                        gm = (g0 + g1) / 2
                        if err(g0) * err(gm) <= 0:
                            g1 = gm
                        else:
                            g0 = gm
                    gamma, found = (g0 + g1) / 2, True
                    break
            if found:
                break
    if not found:
        raise ValueError(f"thumb: 押し棒が届かない (u={u:.3f})")
    Wh = rot_axis((0, 1, 0), gamma, q["shaft"])
    tip = apply(Wh, q["horn_tip"])
    Wrod = aim(q["horn_tip"], tip, vsub(q["strut"], q["horn_tip"]), vsub(strut, tip))
    ct = apply(Wp, q["crank_t"])
    d0, d1 = vsub(q["crank_t"], q["crank_f"]), vsub(ct, q["crank_f"])
    Wc = aim(q["crank_f"], q["crank_f"], d0, d1, vlen(d1) / vlen(d0))
    return {"thumb_prox": Wp, "thumb_tip": Wt, "thumb_horn": Wh, "thumb_pushrod": Wrod, "thumb_crank": Wc}, \
        dict(horn=gamma, crank_stretch=vlen(d1) / vlen(d0))


# ---- 骨の一覧 -----------------------------------------------------------
def bones():
    """骨: 名前 → (親, 頭の点, 尾の点) [mm]。頭は回転の中心。伸び縮みする棒は頭から尾が棒の向き。"""
    f = P.WRIST_FLANGE
    c = (f["x"], f["y"], P.WRIST_H_Z[0])
    up = lambda p, d=10.0: (p[0], p[1], p[2] + d)
    out = {"base": (None, (c[0], c[1], 0.0), (c[0], c[1], 4.0)), "hand": ("base", c, up(c))}
    for i, nm in enumerate(FINGERS):
        q = finger_points(i)
        F = finger_fan(i)
        w = lambda p2, layer=P.LAYER_CORE: apply(F, (P.FINGER_X[i] + layer, p2[0], p2[1]))
        out[f"{nm}_prox"] = ("hand", w(q["mcp"]), w(q["pip"]))
        out[f"{nm}_mid"] = (f"{nm}_prox", w(q["pip"], P.LAYER_MID), w(q["dip"], P.LAYER_MID))
        out[f"{nm}_tip"] = (f"{nm}_mid", w(q["dip"]), w((P.F_TIP_C[0], P.F_TIP_C[1] + P.FINGER_DZ[i])))
        out[f"{nm}_link"] = (f"{nm}_prox", w(q["a"], P.LAYER_LINK), w(q["d"], P.LAYER_LINK))
        xs = P.FINGER_X[i] + P.LAYER_S
        out[f"{nm}_slink"] = ("hand", (xs, q["h"][0], q["h"][1]), (xs, q["g"][0], q["g"][1]))
        out[f"{nm}_rod"] = ("hand", w(q["rb"]), w(q["rt"]))
    q = thumb_points()
    out["thumb_prox"] = ("hand", q["pivot"], q["joint"])
    e1, e2, n, o = thumb_frame()
    d = math.radians(P.THUMB_TIP_DIR)
    tip = tuple(q["joint"][k] + (e1[k] * math.cos(d) + e2[k] * math.sin(d)) * P.THUMB_TIP_LEN for k in range(3))
    out["thumb_tip"] = ("thumb_prox", q["joint"], tip)
    out["thumb_horn"] = ("hand", q["shaft"], (P.HORN_TIP[0], P.HORN_Y, P.HORN_TIP[1]))
    out["thumb_pushrod"] = ("thumb_horn", q["horn_tip"], q["strut"])
    out["thumb_crank"] = ("hand", q["crank_f"], q["crank_t"])
    return out


def clamp_dofs(dofs):
    out = {}
    for k, (lo, hi, rest) in DOFS.items():
        out[k] = min(hi, max(lo, float(dofs.get(k, rest))))
    return out


def pose(dofs):
    """量の辞書から、骨ごとの行列（mm、世界座標。何もしないとき単位行列）を返す。"""
    d = clamp_dofs(dofs)
    out = {"base": ident(), "hand": ident()}
    for i, nm in enumerate(FINGERS):
        out.update(finger_pose(i, d[nm]))
    th, _ = thumb_pose(d["thumb"])
    out.update(th)
    f = P.WRIST_FLANGE
    Ww = rot_axis((0, 0, 1), math.radians(WRIST_MAX) * d["wrist"], (f["x"], f["y"], 0.0))
    return {k: (m if k == "base" else mul(Ww, m)) for k, m in out.items()}
