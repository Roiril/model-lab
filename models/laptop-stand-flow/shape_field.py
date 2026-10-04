"""側面輪郭（trace.py）から、断面の厚み場 h(y, z) を作る。numpy のみ。

側面の輪郭の内側に入った深さ d から、片側の厚み h = H * f(d / R) を決める。
  H: 脚の最大の半幅（X方向）  R: 丸みの半径  f: 楕円（に近い曲線）
立体は |x| <= h(y, z) の領域。H と R は位置ごとに SEEDS から滑らかに補間する。
単位はこのファイルの中では mm。
"""
import json
from pathlib import Path

import numpy as np

import ref_trace as T

# ピクセル (x, y) → 足先を原点とした mm (y, z)
S = 0.75


def to_mm(point):
    return ((point[0] - T.ORIGIN_X) * S, (T.GROUND_Y - point[1]) * S)


def catmull_closed(points, per_segment=10):
    pts = np.array(points, float)
    m = len(pts)
    out = []
    for i in range(m):
        p0, p1, p2, p3 = pts[(i - 1) % m], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        for t in np.linspace(0.0, 1.0, per_segment, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


def densify(poly, step):
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        k = max(1, int(np.ceil(np.hypot(*(b - a)) / step)))
        for j in range(k):
            out.append(a + (b - a) * (j / k))
    return np.array(out)


def silhouette_polygons():
    """mm 単位の (外形, 穴)。"""
    outer = catmull_closed([to_mm(p) for p in T.OUTER])
    hole = catmull_closed([to_mm(p) for p in T.HOLE])
    return outer, hole


def inside_mask(py, pz, polys):
    """偶奇則。py, pz は同形の配列。"""
    inside = np.zeros(py.shape, bool)
    for poly in polys:
        n = len(poly)
        for i in range(n):
            y1, z1 = poly[i]
            y2, z2 = poly[(i + 1) % n]
            if z1 == z2:
                continue
            cond = ((z1 > pz) != (z2 > pz))
            xin = (y2 - y1) * (pz - z1) / (z2 - z1) + y1
            inside ^= cond & (py < xin)
    return inside


def boundary_distance(py, pz, polys, step=0.2):
    """各点から輪郭までの最短距離（mm）。"""
    samples = np.concatenate([densify(p, step) for p in polys]).astype(np.float32)
    try:
        from mathutils import kdtree
        tree = kdtree.KDTree(len(samples))
        for i, (a, b) in enumerate(samples):
            tree.insert((float(a), float(b), 0.0), i)
        tree.balance()
        flat_y, flat_z = py.ravel(), pz.ravel()
        out = np.empty(flat_y.shape, np.float32)
        for i in range(len(flat_y)):
            out[i] = tree.find((float(flat_y[i]), float(flat_z[i]), 0.0))[2]
        return out.reshape(py.shape)
    except ImportError:
        flat_y = py.ravel().astype(np.float32)
        flat_z = pz.ravel().astype(np.float32)
        out = np.empty(flat_y.shape, np.float32)
        for lo in range(0, len(flat_y), 1500):
            dy = flat_y[lo:lo + 1500, None] - samples[None, :, 0]
            dz = flat_z[lo:lo + 1500, None] - samples[None, :, 1]
            out[lo:lo + 1500] = np.sqrt((dy * dy + dz * dz).min(axis=1))
        return out.reshape(py.shape)


# 位置ごとの半幅 H と丸み R。(x_px, y_px, R_mm, H_mm)
# R は、その場所の輪郭の厚みの半分以上にすると断面が丸くなり、小さいと平らな面が残る。
SEEDS = [
    # 柱と肩
    (1205, 395, 18, 24),
    (1213, 425, 16, 21),
    (1232, 455, 15, 19),
    (1240, 485, 15, 19),
    (1235, 510, 14, 26),
    # 足の後ろ（足先へ向けて細く）
    (1160, 552, 3, 8),
    (1185, 541, 6, 16),
    (1215, 546, 9, 32),
    # 足の中ほど
    (1270, 548, 9, 38),
    (1310, 550, 9, 42),
    (1360, 545, 12, 44),
    (1420, 545, 12, 42),
    (1458, 552, 7, 32),
    # 斜めのリボン
    (1245, 435, 9, 19),
    (1280, 455, 7, 19),
    (1330, 480, 6.5, 20),
    (1380, 498, 8, 24),
    (1420, 515, 10, 30),
    (1445, 530, 10, 33),
]


def seed_fields(py, pz, sigma=17.0):
    """SEEDS の R と H を、ガウス重みで滑らかに補間する。"""
    sy = np.array([to_mm((s[0], s[1]))[0] for s in SEEDS])
    sz = np.array([to_mm((s[0], s[1]))[1] for s in SEEDS])
    sr = np.array([s[2] for s in SEEDS], float)
    sh = np.array([s[3] for s in SEEDS], float)
    d2 = np.stack([((py - y) ** 2 + (pz - z) ** 2) for y, z in zip(sy, sz)])
    logw = -d2 / (2.0 * sigma ** 2)
    logw -= logw.max(axis=0)
    w = np.exp(logw)
    den = w.sum(axis=0)
    return (w * sr[:, None, None]).sum(axis=0) / den, (w * sh[:, None, None]).sum(axis=0) / den


def blur(a, radius_mm, pitch, passes=3):
    """箱型ぼかしの繰り返し（ほぼガウス）。"""
    k = max(1, int(round(radius_mm / pitch)))
    kernel = np.ones(2 * k + 1) / (2 * k + 1)
    out = a.astype(np.float64)
    for _ in range(passes):
        for axis in (0, 1):
            pad = [(0, 0), (0, 0)]
            pad[axis] = (k, k)
            padded = np.pad(out, pad, mode="edge")
            acc = np.zeros_like(out)
            for i in range(2 * k + 1):
                sl = [slice(None), slice(None)]
                sl[axis] = slice(i, i + out.shape[axis])
                acc += kernel[i] * padded[tuple(sl)]
            out = acc
    return out


def local_thickness(d, window_mm, pitch):
    """輪郭の厚みの半分の見積り。窓の中での d の最大値。"""
    k = int(round(window_mm / pitch))
    pad = np.pad(d, k, mode="constant", constant_values=0)
    out = d.copy()
    for dy in range(-k, k + 1):
        for dz in range(-k, k + 1):
            if dy * dy + dz * dz > k * k:
                continue
            out = np.maximum(out, pad[k + dy:k + dy + d.shape[0], k + dz:k + dz + d.shape[1]])
    return out


FIT_PATH = Path(__file__).with_name("fit_state.json")
SIGMA_W = 16.0


def load_fit():
    """fit/export_fit.py が書く fit_state.json（参考画像の輪郭にあわせた結果）。無ければ None。"""
    if not FIT_PATH.exists():
        return None
    raw = json.load(open(FIT_PATH, encoding="utf-8"))
    return {k: np.array(v, float) if isinstance(v, list) else v for k, v in raw.items()}


def warp_nodes():
    out = np.array([to_mm(p) for p in T.OUTER], float)
    return out[list(range(0, len(T.OUTER), 3))]


def bilerp(a, y0, z0, pitch, py, pz):
    gy = np.clip((py - y0) / pitch, 0, a.shape[0] - 1.001)
    gz = np.clip((pz - z0) / pitch, 0, a.shape[1] - 1.001)
    iy, iz = np.floor(gy).astype(int), np.floor(gz).astype(int)
    fy, fz = gy - iy, gz - iz
    return ((1 - fy) * (1 - fz) * a[iy, iz] + fy * (1 - fz) * a[iy + 1, iz]
            + (1 - fy) * fz * a[iy, iz + 1] + fy * fz * a[iy + 1, iz + 1])


def section_params(py, pz, pitch, window_mm=9.0, blur_mm=1.6, fit=None):
    """格子 (y, z) 上の、符号付き距離 d（内側が正）・丸み R・半幅 H・中心ずれ xc。

    fit があれば、側面の滑らかな変位場 W で位置を引き戻して（p' = p - W）、
    輪郭の距離場・厚み・シードの補間をその位置で読む。"""
    outer, hole = silhouette_polygons()
    inside = inside_mask(py, pz, [outer, hole])
    dist = boundary_distance(py, pz, [outer, hole])
    d = np.where(inside, dist, -dist).astype(np.float32)
    # R が厚みの半分を超えると中心線に尾根（折れ目）ができるので、厚みで頭打ちにする
    thick = local_thickness(np.maximum(d, 0.0), window_mm, pitch)
    d = blur(d, blur_mm, pitch)
    qy, qz = py, pz
    h_seed = np.array([s[3] for s in SEEDS], float)
    xc_seed = np.zeros(len(SEEDS))
    if fit is not None:
        nodes = warp_nodes()
        disp = fit["disp"].reshape(-1, 2)
        d2 = (py[None] - nodes[:, 0, None, None]) ** 2 + (pz[None] - nodes[:, 1, None, None]) ** 2
        w = np.exp(-d2 / (2 * SIGMA_W ** 2)) + 1e-12
        w /= w.sum(axis=0)
        qy = py - (w * disp[:, 0, None, None]).sum(axis=0)
        qz = pz - (w * disp[:, 1, None, None]).sum(axis=0)
        d = bilerp(d, py[0, 0], pz[0, 0], pitch, qy, qz)
        thick = bilerp(thick, py[0, 0], pz[0, 0], pitch, qy, qz)
        h_seed = fit["h"]
        xc_seed = fit["xc"]
    sy = np.array([to_mm((s[0], s[1]))[0] for s in SEEDS])
    sz = np.array([to_mm((s[0], s[1]))[1] for s in SEEDS])
    g2 = (qy[None] - sy[:, None, None]) ** 2 + (qz[None] - sz[:, None, None]) ** 2
    lw = -g2 / (2.0 * 17.0 ** 2)
    lw -= lw.max(axis=0)
    ww = np.exp(lw)
    den = ww.sum(axis=0)
    r_seed = (ww * np.array([s[2] for s in SEEDS], float)[:, None, None]).sum(axis=0) / den
    h_max = (ww * h_seed[:, None, None]).sum(axis=0) / den
    xc = (ww * xc_seed[:, None, None]).sum(axis=0) / den
    r = blur(np.minimum(r_seed, np.maximum(thick, 1.0)), 2.5, pitch)
    return d.astype(np.float32), r.astype(np.float32), h_max.astype(np.float32), xc.astype(np.float32)
