"""カムの生成器（bpy 非依存）。表（5x5 の高さ [mm]、K 枚）→ 画素ごとの板カムの輪郭。単位は mm と度。

考え方（平面足の従動子 = 圧力角 0、カムは凸）:
- カムの高さは支持関数 h(phi)。足の下面 Z = Zc + h(phi)。カムの枠で、上向き = n(phi) = (sin phi, cos phi)
- 表 k を出すサーボ角 → 軸角 phi_k。その前後 ±w（停止区間）で h = CAM_RB + 高さ k（= 同心円の弧）
- 停止区間では半平面 x . n(phi) <= t(phi)（t は目標の半径）。停止区間の間は、両隣の高い方の半径を上限にする
  （高い方を超えて飛び出さない。同じ高さなら真円になる）
- 輪郭 = 半平面の交わり（凸多角形）。双対で書くと、点 n(phi)/t(phi) の凸包の双対なので O(N log N)
- 実現した高さ h* = 交わりの支持関数。停止区間で h* = t なら表どおり。他の表の弧が食い込めば h* < t
  → その表は足りない（隣の表との角度差が足りない等）として CamError で拒否する。真の可否は輪郭の幾何で決める
  （required_angle は保守的な目安。半径の上限の上を横にすべる頂点で目安より狭くても成り立つことがあるが、
  そのとき接点の横ずれが大きくなるので、横ずれの上限でも拒否する）
- 接点の横ずれ e(phi) = dh*/dphi（足の中心から接点までの横の距離）。足の半幅 - 1mm 以下であること
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import params as P
import kinematics as K

DWELL_TOL_MM = 0.01            # 停止区間での高さ誤差の許容（mm）
LATERAL_MAX_MM = P.FOOT_Y * 1000.0 / 2 - 1.0   # 接点の横ずれの上限（足の半幅 - 1mm = 9mm）


class CamError(Exception):
    """この表の組ではカムが作れない（隣の表との角度差が足りない等）"""


def required_angle(r_lo, r_hi, w_deg=None):
    """低い方の弧 r_lo の停止区間に、高い方の弧 r_hi の端が食い込まない最小の中心間の角度（度）。
    2w + acos(r_lo / r_hi)。r_hi <= r_lo なら 2w（弧が隣り合うだけでよい）"""
    w = P.DWELL_HALF_DEG if w_deg is None else w_deg
    if r_hi <= r_lo:
        return 2 * w
    return 2 * w + math.degrees(math.acos(r_lo / r_hi))


def _hull(points):
    pts = sorted(set(points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo = []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    up = []
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def _window_list(centers, radii, w):
    """(中心角, 半径) を中心角の昇順に並べる。停止区間が重なれば CamError"""
    order = sorted(range(len(centers)), key=lambda k: centers[k] % 360.0)
    cs = [centers[k] % 360.0 for k in order]
    rs = [radii[k] for k in order]
    n = len(cs)
    if n > 1:
        for m in range(n):
            gap = (cs[(m + 1) % n] - cs[m]) % 360.0
            if n > 1 and gap < 2 * w - 1e-9:
                raise CamError(f"停止区間が重なる: 中心 {cs[m]:.1f} と {cs[(m + 1) % n]:.1f} 度（間 {gap:.1f} 度 < 2w = {2 * w:.1f}）")
    return cs, rs


def _upper_bound(cs, rs, w, step):
    """全周の角度格子 phi に対する t(phi)。停止区間 = 弧の半径。間 = 両隣の高い方"""
    N = int(round(360.0 / step))
    phis = np.arange(N) * step
    t = np.empty(N)
    n = len(cs)
    for a in range(N):
        phi = phis[a]
        inside = None
        for m in range(n):
            if abs(K.wrap180(phi - cs[m])) <= w + 1e-9:
                inside = m
                break
        if inside is not None:
            t[a] = rs[inside]
        else:
            # 反時計回りにすぐ前の窓 m の次の隙間にいる
            prev = max((m for m in range(n) if cs[m] <= phi), default=n - 1, key=lambda m: cs[m])
            nxt = (prev + 1) % n
            t[a] = max(rs[prev], rs[nxt])
    return phis, t


def _contour(phis, t):
    pts = []
    for phi, tt in zip(phis, t):
        r = math.radians(phi)
        pts.append((math.sin(r) / tt, math.cos(r) / tt))
    H = _hull(pts)
    V = []
    for k in range(len(H)):
        a = H[k]
        b = H[(k + 1) % len(H)]
        det = a[0] * b[1] - a[1] * b[0]
        V.append(((b[1] - a[1]) / det, (a[0] - b[0]) / det))
    return np.array(V)


def support(V, phis_deg):
    """輪郭 V（頂点 (u,v) mm の配列）の支持関数と接点の横ずれ（どちらも mm）"""
    r = np.radians(np.atleast_1d(phis_deg))
    n = np.stack([np.sin(r), np.cos(r)], axis=1)
    d = V @ n.T
    idx = d.argmax(axis=0)
    h = d.max(axis=0)
    lat = (V[idx] * np.stack([np.cos(r), -np.sin(r)], axis=1)).sum(axis=1)
    return h, lat


def build_cam(heights_mm, j, i=0, thetas=None, theta_flat=None, w=None, step=None, check=True,
              lateral_limit_mm=None):
    """1 画素のカム。heights_mm = 各表での高さ [mm]（長さ K）。j = 軸（回転方向と角度を決める）。
    返り値: 輪郭と検査値の辞書。足りない表なら CamError。"""
    w = P.DWELL_HALF_DEG if w is None else w
    step = P.CAM_STEP_DEG if step is None else step
    th = P.TABLE_THETA if thetas is None else thetas
    lateral_limit_mm = LATERAL_MAX_MM if lateral_limit_mm is None else lateral_limit_mm
    if len(heights_mm) != len(th):
        raise CamError(f"表の数 {len(heights_mm)} と角度の数 {len(th)} が違う")
    rb = P.CAM_RB * 1000.0
    radii = [rb + h for h in heights_mm]
    for h in heights_mm:
        if h < P.H_MIN * 1000.0 - 1e-9 or h > P.H_MAX * 1000.0 + 1e-9:
            raise CamError(f"画素 ({i},{j}): 高さ {h} mm が範囲 -3..+3 の外")
    centers = [K.axis_angle(t, j, theta_flat) for t in th]
    cs, rs = _window_list(centers, radii, w)

    # 角度差の目安（保守的な下限。真の可否は下の輪郭の幾何で決まる。拒否時の説明に使う）
    need_info = []
    n = len(cs)
    for a in range(n):
        for b in range(a + 1, n):
            d = abs(K.wrap180(cs[a] - cs[b]))
            lo, hi = (rs[a], rs[b]) if rs[a] <= rs[b] else (rs[b], rs[a])
            if hi > lo:
                need_info.append((d, required_angle(lo, hi, w), lo - rb, hi - rb))

    phis, t = _upper_bound(cs, rs, w, step)
    V = _contour(phis, t)

    # 停止区間での h* と t
    fine = np.arange(0, 360, 0.25)
    h_fine, lat_fine = support(V, fine)
    err = 0.0
    errs = []
    for k, (c, r) in enumerate(zip(cs, rs)):
        m = np.abs(((fine - c + 180) % 360) - 180) <= w
        e = float(np.max(r - h_fine[m]))
        errs.append(max(e, 0.0))
        err = max(err, e)
    if check and err > DWELL_TOL_MM:
        worst = min(need_info, key=lambda x: x[0] - x[1]) if need_info else None
        hint = (f"。最も厳しい組: 角度差 {worst[0]:.1f} 度、高さ {worst[2]:+.1f} と {worst[3]:+.1f} mm"
                f"（目安の必要角 {worst[1]:.1f} 度）") if worst else ""
        raise CamError(f"画素 ({i},{j}): 停止区間で高さが {err:.3f} mm 足りない（他の表の弧が食い込む。隣の表との角度差が足りない）" + hint)

    # 接点の横ずれ。サーボの使える範囲の軸角だけ見る
    half = K.table_theta_to_phi_range(theta_flat) + 0.0
    reach = np.abs(((fine + 180) % 360) - 180) <= half
    lateral_max = float(np.abs(lat_fine[reach]).max())
    if check and lateral_max > lateral_limit_mm:
        raise CamError(f"画素 ({i},{j}): 接点の横ずれ {lateral_max:.2f} mm > 足が覆える {lateral_limit_mm:.1f} mm（表の高さの差が急すぎる）")

    # 凸性（頂点の外積が全部 >= 0）と半径
    e1 = np.roll(V, -1, axis=0) - V
    e2 = np.roll(e1, -1, axis=0)
    cr = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
    convex = bool(cr.min() >= -1e-9)
    rad = np.hypot(V[:, 0], V[:, 1])
    # 最小半径 = 輪郭上の原点からの最短距離 = 全辺（頂点間の線分）への距離
    rmin = float(_min_radius(V))
    return {
        "i": i, "j": j,
        "heights_mm": list(map(float, heights_mm)),
        "phi_centers_deg": [float(c) for c in centers],
        "dwell_half_deg": float(w),
        "vertices": V.round(5).tolist(),
        "dwell_err_mm": errs,
        "dwell_err_max_mm": float(max(errs)),
        "lateral_max_mm": lateral_max,
        "rmin_mm": rmin,
        "rmax_mm": float(rad.max()),
        "convex": convex,
        "n_vertices": int(len(V)),
        "need_info": [[round(a, 2), round(b, 2), c, d] for a, b, c, d in need_info],
    }


def _min_radius(V):
    """原点から輪郭（閉じた多角形）までの最短距離"""
    a = V
    b = np.roll(V, -1, axis=0)
    ab = b - a
    t = -(a * ab).sum(axis=1) / np.maximum((ab * ab).sum(axis=1), 1e-30)
    t = np.clip(t, 0.0, 1.0)
    pt = a + ab * t[:, None]
    return np.hypot(pt[:, 0], pt[:, 1]).min()


def target_curve(heights_mm, j, thetas=None, w=None, theta_flat=None):
    """目標の高さ h_i(phi)（mm）。停止区間は一定、その間は余弦の滑らかな遷移（表示と比較用）。
    返すのは phi（度）の関数"""
    w = P.DWELL_HALF_DEG if w is None else w
    th = P.TABLE_THETA if thetas is None else thetas
    centers = [K.axis_angle(t, j, theta_flat) % 360.0 for t in th]
    order = sorted(range(len(th)), key=lambda k: centers[k])
    cs = [centers[k] for k in order]
    hs = [heights_mm[k] for k in order]
    n = len(cs)

    def f(phi):
        phi = phi % 360.0
        for m in range(n):
            if abs(K.wrap180(phi - cs[m])) <= w:
                return hs[m]
        prev = max((m for m in range(n) if cs[m] <= phi), default=n - 1, key=lambda m: cs[m])
        nxt = (prev + 1) % n
        a0 = cs[prev] + w
        a1 = cs[nxt] - w + (360.0 if nxt <= prev else 0.0)
        pp = phi + (360.0 if phi < a0 - 1e-9 else 0.0)
        s = (pp - a0) / max(a1 - a0, 1e-9)
        s = min(max(s, 0.0), 1.0)
        return hs[prev] + (hs[nxt] - hs[prev]) * (1 - math.cos(math.pi * s)) / 2

    return f


def build_all(tables, thetas=None, theta_flat=None, w=None, step=None):
    """tables[k][j][i] = 表 k の画素 (列 i, 行 j) の高さ [mm]。cams[j][i] の 5x5 を返す。
    足りない表が 1 枚でもあれば CamError（どの画素かが文面に入る）"""
    Kn = len(tables)
    check_tables(tables)
    cams = [[None] * P.N for _ in range(P.N)]
    for j in range(P.N):
        for i in range(P.N):
            hs = [tables[k][j][i] for k in range(Kn)]
            cams[j][i] = build_cam(hs, j, i, thetas=thetas, theta_flat=theta_flat, w=w, step=step)
    return cams


def cone_pair_limits_mm():
    """隣の行のカムの、最大高さの和の上限 (同じ列の組 A, 斜めの組 B)。mm。
    隙間 = 17 - (R_a - t) - R_b = 17 - 2 x 8.2 + t - (h_a + h_b)。設計位置で >= CONE_CLEAR_NOMINAL、軸方向の遊び（相対 2 x AXIAL_DRIFT）を最悪に入れて >= CONE_CLEAR_SLACK"""
    pitch = P.PITCH * 1000.0
    rb = P.CAM_RB * 1000.0
    diff = (P.ROW_SHIFT_POS - P.ROW_SHIFT_NEG) * 1000.0
    t_a = diff - P.CAM_T * 1000.0
    t_b = pitch - diff - P.CAM_T * 1000.0
    base = pitch - 2 * rb
    slack = 2 * P.AXIAL_DRIFT * 1000.0
    out = []
    for t in (t_a, t_b):
        out.append(min(base + t - P.CONE_CLEAR_NOMINAL * 1000.0, base + t - slack - P.CONE_CLEAR_SLACK * 1000.0))
    return out[0], out[1], t_a, t_b


def first_cam_neg_row_height_max_mm():
    """奇数行（-X へ 5.1 ずれる行）の cam 0 の高さの上限 (mm)。円錐がパッドの面（-PAD_X0）で、じょうご（半径 U 溝の半幅 + U_FUNNEL）に収まる条件。
    軸が -X へ AXIAL_DRIFT 動いた最悪で、円錐の半径 = R - (x0 - AXIAL_DRIFT + PAD_X0)"""
    x0 = K.cam_x_range(0, 1)[0] * 1000.0
    t_pad = (x0 - P.AXIAL_DRIFT * 1000.0) + P.PAD_X0 * 1000.0
    f_pad = (P.U_SLOT_MX_W / 2 + P.U_FUNNEL) * 1000.0
    r_max = f_pad - P.FUNNEL_CLEAR * 1000.0 + t_pad
    return r_max - P.CAM_RB * 1000.0


def check_tables(tables):
    """表の組の、隣の行のカムの制約。足りなければ CamError。
    (1) 隣り合う行のカムの、全表での最大高さの和 <= cone_pair_limits_mm()
    (2) 奇数行の cam 0 の最大高さ <= first_cam_neg_row_height_max_mm()"""
    lim_a, lim_b, _, _ = cone_pair_limits_mm()
    hmax = [[max(tables[k][j][i] for k in range(len(tables))) for i in range(P.N)] for j in range(P.N)]
    for j in range(P.N - 1):
        pos_j, neg_j = (j, j + 1) if j % 2 == 0 else (j + 1, j)
        for i in range(P.N):
            s = hmax[pos_j][i] + hmax[neg_j][i]                       # 同じ列: pos の円錐が neg の板へ（t = 4.25）
            if s > lim_a + 1e-9:
                raise CamError(f"隣の行のカム ({i},{pos_j}) と ({i},{neg_j}) の最大高さの和 {s:.2f} mm > 上限 {lim_a:.2f} mm（同じ列。円錐が食い込む）")
            if i >= 1:
                s = hmax[neg_j][i] + hmax[pos_j][i - 1]               # 斜め: neg の円錐が 1 つ -X の列の pos の板へ（t = 4.75）
                if s > lim_b + 1e-9:
                    raise CamError(f"隣の行のカム ({i},{neg_j}) と ({i - 1},{pos_j}) の最大高さの和 {s:.2f} mm > 上限 {lim_b:.2f} mm（斜め。円錐が食い込む）")
    lim0 = first_cam_neg_row_height_max_mm()
    for j in range(1, P.N, 2):
        if hmax[j][0] > lim0 + 1e-9:
            raise CamError(f"奇数行の最初のカム (0,{j}) の最大高さ {hmax[j][0]:.2f} mm > 上限 {lim0:.2f} mm（-X のパッドのじょうごに円錐が収まらない）")


def write_json(cams, path, tables=None, names=None):
    """カムの輪郭を JSON に書く（bpy 担当が読む）。単位 mm。頂点は輪郭を反時計回り（u=+Y, v=+Z の枠）"""
    out = {
        "units": "mm",
        "frame": "cam frame: u=+Y, v=+Z at phi=0; phi rotates about +X (Y->Z)",
        "cam_rb_mm": P.CAM_RB * 1000.0,
        "dwell_half_deg": P.DWELL_HALF_DEG,
        "table_theta_deg": list(P.TABLE_THETA),
        "axis_dir": list(P.AXIS_DIR),
        "g_ratio": P.G_RATIO,
        "tables": tables,
        "names": names,
        "cams": [[cams[j][i] for i in range(P.N)] for j in range(P.N)],
        "cam_x_mm": [[K.cam_x(i, j) * 1000.0 for i in range(P.N)] for j in range(P.N)],
        "cam_thickness_mm": P.CAM_T * 1000.0,
        "camshaft_body_d_mm": P.CAMSHAFT_BODY_D * 1000.0,
        "skirt_deg": P.CAM_SKIRT_DEG,
        "row_shift_mm": {"even": P.ROW_SHIFT_POS * 1000.0, "odd": P.ROW_SHIFT_NEG * 1000.0},
    }
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False)
    os.replace(tmp, path)


if __name__ == "__main__":
    import patterns as PT
    cams_ = build_all(PT.TABLES)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "cams.json")
    write_json(cams_, out, tables=PT.TABLES, names=PT.NAMES)
    print("wrote", out, "cams:", sum(len(r) for r in cams_))
    print("lateral max", max(c["lateral_max_mm"] for r in cams_ for c in r), "rmax", max(c["rmax_mm"] for r in cams_ for c in r))
