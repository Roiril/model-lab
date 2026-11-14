"""側面の輪郭（Y-Z, mm）を計算する。Blender に依存しない（verify.py からも使う）。"""
from __future__ import annotations

import math

import params as P


def frame():
    """支えの面の向き u（上り）と、画面側の法線 n、本体の背面下端 S0。"""
    a = math.radians(P.ANGLE_DEG)
    u = (math.cos(a), math.sin(a))
    n = (-math.sin(a), math.cos(a))
    lip_reach = (P.GROOVE_MM + P.LIP_T_MM) * n[0] + P.LIP_H_MM * u[0]
    s0 = (P.LIP_FRONT_Y_MM - lip_reach, P.SEAT_Z_MM)
    return s0, u, n


def _add(p, v, k=1.0):
    return (p[0] + v[0] * k, p[1] + v[1] * k)


def skeleton():
    """丸める前の多角形（反時計回り）と各頂点の丸め半径。"""
    s0, u, n = frame()
    f = _add(s0, n, P.GROOVE_MM)
    lip_in = _add(f, u, P.LIP_H_MM)
    lip_out = _add(lip_in, n, P.LIP_T_MM)
    top = _add(s0, u, P.SUPPORT_MM)
    b = math.radians(P.BACK_DEG)
    down = (math.cos(b), -math.sin(b))
    knee = _add(top, down, (top[1] - P.TAIL_H_MM) / math.sin(b))
    pts = [
        ((0.0, 0.0), 0.0),
        ((P.DEPTH_MM, 0.0), 0.0),
        ((P.DEPTH_MM, P.TAIL_H_MM), P.R_TAIL_MM),
        (knee, P.R_KNEE_MM),
        (top, P.R_TOP_MM),
        (s0, P.R_GROOVE_BACK_MM),
        (f, P.R_GROOVE_FRONT_MM),
        (lip_in, P.R_LIP_IN_MM),
        (lip_out, P.R_LIP_OUT_MM),
        ((0.0, P.FRONT_STEP_MM), P.R_FRONT_MM),
    ]
    return [p for p, _ in pts], [r for _, r in pts]


def _norm(v):
    length = math.hypot(*v)
    return (v[0] / length, v[1] / length), length


def rounded(points, radii):
    """各頂点を接線円弧で丸めた点列。接線の長さが辺に収まらなければ例外。"""
    out = []
    count = len(points)
    used = [0.0] * count  # 辺 i（点 i → i+1）の両端で消費した長さ
    arcs = []
    for i in range(count):
        cur = points[i]
        prev = points[i - 1]
        nxt = points[(i + 1) % count]
        a, la = _norm((prev[0] - cur[0], prev[1] - cur[1]))
        c, lc = _norm((nxt[0] - cur[0], nxt[1] - cur[1]))
        r = radii[i]
        corner = math.acos(max(-1.0, min(1.0, a[0] * c[0] + a[1] * c[1])))
        if r <= 0:
            arcs.append([cur])
            continue
        t = r / math.tan(corner / 2.0)
        used[i - 1] += t
        used[i] += t
        start = _add(cur, a, t)
        end = _add(cur, c, t)
        bis, _ = _norm((a[0] + c[0], a[1] + c[1]))
        center = _add(cur, bis, r / math.sin(corner / 2.0))
        a0 = math.atan2(start[1] - center[1], start[0] - center[0])
        a1 = math.atan2(end[1] - center[1], end[0] - center[0])
        turn = (cur[0] - prev[0]) * (nxt[1] - cur[1]) - (cur[1] - prev[1]) * (nxt[0] - cur[0])
        if turn > 0:
            while a1 <= a0:
                a1 += 2 * math.pi
        else:
            while a1 >= a0:
                a1 -= 2 * math.pi
        sweep = abs(a1 - a0)
        steps = max(2, math.ceil(math.degrees(sweep) / P.ARC_STEP_DEG),
                    math.ceil(sweep * r / P.ARC_MAX_CHORD_MM))
        arcs.append([(center[0] + r * math.cos(a0 + (a1 - a0) * k / steps),
                      center[1] + r * math.sin(a0 + (a1 - a0) * k / steps)) for k in range(steps + 1)])
    for i in range(count):
        _, length = _norm((points[(i + 1) % count][0] - points[i][0],
                           points[(i + 1) % count][1] - points[i][1]))
        if used[i] > length + 1e-9:
            raise ValueError(f"fillets overlap on edge {i}: need {used[i]:.2f} of {length:.2f} mm")
    for arc in arcs:
        for p in arc:
            if not out or math.dist(p, out[-1]) > 1e-6:
                out.append(p)
    if math.dist(out[0], out[-1]) <= 1e-6:
        out.pop()
    return out


def outline():
    pts, radii = skeleton()
    return rounded(pts, radii)


def signed_area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


def offset(poly, d):
    """内側へ d 平行移動した輪郭。机に接する辺（z=0 の辺）は動かさない。

    隣り合う 2 辺のずらした直線の交点を新しい頂点にする（尖った角も正確）。
    """
    count = len(poly)
    assert signed_area(poly) > 0, "outline must be counter-clockwise"
    lines = []
    for i in range(count):
        p, q = poly[i], poly[(i + 1) % count]
        t, _ = _norm((q[0] - p[0], q[1] - p[1]))
        inward = (-t[1], t[0])  # 反時計回りなら左が内側
        dist = 0.0 if (abs(p[1]) < 1e-9 and abs(q[1]) < 1e-9) else d
        lines.append((inward, inward[0] * p[0] + inward[1] * p[1] + dist))
    out = []
    for i in range(count):
        (n1, c1), (n2, c2) = lines[i - 1], lines[i]
        det = n1[0] * n2[1] - n1[1] * n2[0]
        if abs(det) < 1e-9:
            p = poly[i]
            out.append((p[0] + n2[0] * (c2 - (n2[0] * p[0] + n2[1] * p[1])),
                        p[1] + n2[1] * (c2 - (n2[0] * p[0] + n2[1] * p[1]))))
        else:
            out.append(((c1 * n2[1] - c2 * n1[1]) / det, (n1[0] * c2 - n2[0] * c1) / det))
    return out


def side_rings():
    """左右の縁の丸めに使う (x, 内側へのずらし量) の列。左端から右端へ。"""
    half = P.WIDTH_MM / 2.0
    r = P.R_SIDE_MM
    left = []
    for k in range(P.SIDE_STEPS, -1, -1):
        phi = math.pi / 2 * k / P.SIDE_STEPS
        left.append((-(half - r + r * math.sin(phi)), r * (1 - math.cos(phi))))
    right = [(-x, d) for x, d in reversed(left)]
    return left + right


if __name__ == "__main__":
    s0, u, n = frame()
    poly = outline()
    print("S0", s0, "points", len(poly), "area", round(signed_area(poly), 1))
    print("height", round(max(p[1] for p in poly), 2), "depth", round(max(p[0] for p in poly), 2))
    for d in (0.0, P.R_SIDE_MM):
        o = offset(poly, d)
        print("offset", d, "area", round(signed_area(o), 1))
