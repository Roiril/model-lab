"""4 節リンクの運動学（Blender 不要。単位 mm・度）。

蓋は蝶番軸 H のまわりに θ 回る（+θ で前が上がる）。クランクは出力軸 O のまわりに α。
ピン A（クランク）とピン B（蓋の耳）をリンク（長さ l）がつなぐ。
model.py / verify.py / simulate.py が同じ式を使う。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import params as P  # noqa: E402

MM = 1000.0
H = (P.HINGE_Y * MM, P.HINGE_Z * MM)
O = (P.SHAFT_Y * MM, P.SHAFT_Z * MM)
A_LEN = P.CRANK_A * MM
B_REL = (P.B_REL_Y * MM, P.B_REL_Z * MM)
ALPHA0 = P.CRANK_ALPHA_CLOSED_DEG
THETA_OPEN = P.LID_OPEN_DEG


def rot(v, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def norm(v):
    return math.hypot(v[0], v[1])


def pin_a(alpha):
    r = math.radians(alpha)
    return (O[0] + A_LEN * math.cos(r), O[1] + A_LEN * math.sin(r))


def pin_b(theta):
    return add(H, rot(B_REL, theta))


B0 = pin_b(0.0)
L_LINK = norm(sub(B0, pin_a(ALPHA0)))


def crank_angle(theta, prev=ALPHA0):
    """蓋角 θ に対するクランク角 α（prev に近い枝）。届かなければ None。"""
    b = pin_b(theta)
    d = norm(sub(b, O))
    if d > A_LEN + L_LINK or d < abs(L_LINK - A_LEN):
        return None
    base = math.degrees(math.atan2(b[1] - O[1], b[0] - O[0]))
    x = math.degrees(math.acos(max(-1.0, min(1.0, (A_LEN ** 2 + d * d - L_LINK ** 2) / (2 * A_LEN * d)))))
    cands = (base + x, base - x)
    return min(cands, key=lambda c: abs((c - prev + 180.0) % 360.0 - 180.0))


def unwrap(alpha, prev):
    return prev + ((alpha - prev + 180.0) % 360.0 - 180.0)


def sweep(theta_max=THETA_OPEN, n=96, theta_min=0.0):
    """θ を theta_min..theta_max で刻み、(θ, α) の列を返す（α は連続に繋ぐ）。"""
    out = []
    prev = ALPHA0
    if theta_min != 0.0:
        for k in range(1, 41):
            t = theta_min * k / 40
            a = crank_angle(t, prev)
            prev = unwrap(a, prev)
    for i in range(n + 1):
        t = theta_min + (theta_max - theta_min) * i / n
        a = crank_angle(t, prev)
        if a is None:
            return None
        prev = unwrap(a, prev)
        out.append((t, prev))
    return out


def link_angle(theta, alpha):
    a, b = pin_a(alpha), pin_b(theta)
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def relative_link_crank(theta, alpha):
    """リンク方向 − クランク方向（符号付き、-180..180）。バヨネットの鍵溝の向きに使う。"""
    return (link_angle(theta, alpha) - alpha + 180.0) % 360.0 - 180.0


def pressure_angle(theta, alpha):
    """B の速度方向とリンクのなす角（0 が理想）。"""
    a, b = pin_a(alpha), pin_b(theta)
    link = sub(b, a)
    v = rot(sub(b, H), 90.0)
    c = abs(link[0] * v[0] + link[1] * v[1]) / (norm(link) * norm(v))
    return math.degrees(math.acos(min(1.0, c)))


def ratio(theta, h=0.05):
    """dθ/dα（数値微分）。サーボ側トルク = 蓋側トルク × dθ/dα。"""
    a1 = crank_angle(theta - h, crank_angle(theta))
    a2 = crank_angle(theta + h, crank_angle(theta))
    return (2 * h) / (unwrap(a2, a1) - a1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"H={H} O={O} a={A_LEN:.2f} B0={tuple(round(v, 2) for v in B0)} l={L_LINK:.3f}")
    s = sweep()
    print(f"alpha: {s[0][1]:.1f} -> {s[-1][1]:.1f} (Δ {s[-1][1]-s[0][1]:.1f}°)")
    rel = [relative_link_crank(t, a) for t, a in s]
    pr = [pressure_angle(t, a) for t, a in s]
    print(f"link-crank relative: {min(rel):.1f} .. {max(rel):.1f}")
    print(f"pressure angle max {max(pr):.1f}° (transmission min {90-max(pr):.1f}°)")
    for t, a in s[::12]:
        print(f"θ={t:5.1f} α={a:6.1f} A={tuple(round(v,1) for v in pin_a(a))} "
              f"B={tuple(round(v,1) for v in pin_b(t))} dθ/dα={ratio(t) if t>0.1 else float('nan'):.2f}")
