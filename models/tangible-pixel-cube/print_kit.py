"""印刷性の検査に使う道具（numpy だけ。Blender は要らない）。単位は mm。

print_review.py（検査）と print_deliver.py（刷るファイル）が使う。
STL は三角形の並びを保ったまま読む（組立姿勢と刷る向きの三角形を、番号で対応させるため）。

  Solid         三角形の並び（T）と、頂点を溶接した V / F。面の法線・面積・体積・重心・位相
  rigid_fit     組立姿勢 -> 刷る向きの剛体変換（回転 R と平行移動 t）を三角形の対応から求める
  overhang_*    45 度より寝た下向きの面の塊と、橋の長さ
  thickness_field 面を細かく割った点から内側へ打つ光線の肉厚（向かいの面が反対を向く場合だけ数える）
  slice_layers  0.2mm の層ごとの断面（輪 -> 島）。島ごとの太さと積み上がる高さ
  first_layer_*  ベッドに接する縁の面取り（第 1 層の膨らみ）
  校正用の形    loft / extrude_poly で閉じた 1 つのメッシュを作る
"""
import math
import struct

import numpy as np

WELD = 1e-4
LAYER = 0.2
OVERHANG_DEG = 44.8            # 水平から 45 度より寝ている下向きの面（45 度ちょうどは数えない）
COS_OVERHANG = math.cos(math.radians(OVERHANG_DEG))


# =============================================================================================
# STL
# =============================================================================================
def read_stl(path):
    """バイナリ STL を (n, 3, 3) の float64 で読む。三角形の並びは保つ。"""
    with open(path, "rb") as fh:
        raw = fh.read()
    n = struct.unpack("<I", raw[80:84])[0]
    if len(raw) < 84 + 50 * n:
        raise ValueError(f"truncated STL: {path}")
    a = np.frombuffer(raw[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return a["v"].reshape(-1, 3, 3).astype(np.float64)


def write_stl(path, T):
    T = np.asarray(T, dtype=np.float64).reshape(-1, 3, 3)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    ln = np.linalg.norm(n, axis=1)
    n = n / np.where(ln > 0, ln, 1.0)[:, None]
    rec = np.zeros(len(T), dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    rec["n"] = n
    rec["v"] = T.reshape(-1, 9)
    with open(path, "wb") as fh:
        fh.write(b"\0" * 80 + struct.pack("<I", len(T)))
        fh.write(rec.tobytes())


# =============================================================================================
# Solid
# =============================================================================================
class Solid:
    """三角形の並び T（(n,3,3)）と、頂点を 1e-4mm で溶接した V（(m,3)）/ F（(n,3)）。"""

    def __init__(self, T, name=""):
        self.name = name
        self.T = np.asarray(T, dtype=np.float64).reshape(-1, 3, 3)
        key = np.round(self.T.reshape(-1, 3) / WELD).astype(np.int64)
        uniq, inv = np.unique(key, axis=0, return_inverse=True)
        self.V = uniq.astype(np.float64) * WELD
        self.F = inv.reshape(-1, 3)
        cr = np.cross(self.T[:, 1] - self.T[:, 0], self.T[:, 2] - self.T[:, 0])
        ln = np.linalg.norm(cr, axis=1)
        self.area = ln / 2.0
        self.n = cr / np.where(ln > 1e-12, ln, 1.0)[:, None]
        self.c = self.T.mean(axis=1)
        self.lo = self.T.reshape(-1, 3).min(axis=0)
        self.hi = self.T.reshape(-1, 3).max(axis=0)

    def volume(self):
        return float(np.einsum("ij,ij->i", self.T[:, 0], np.cross(self.T[:, 1], self.T[:, 2])).sum() / 6.0)

    def com(self):
        v6 = np.einsum("ij,ij->i", self.T[:, 0], np.cross(self.T[:, 1], self.T[:, 2]))
        cen = (self.T[:, 0] + self.T[:, 1] + self.T[:, 2]) / 4.0
        return (cen * v6[:, None]).sum(axis=0) / v6.sum()

    def topology(self):
        """辺ごとの面数と向き。open = 面が 1 枚だけの辺、over = 3 枚以上、flipped = 同じ向きの辺が重なる、components = 辺でつながる塊の数。

        頂点を溶接（1e-4mm）して 2 点が潰れた三角形（collapsed）は、固体に効かないので数えずに辺の検査から外す
        （外しても隣の面どうしの辺は対になる）。個数は collapsed_faces に残す。
        """
        F_all = self.F
        valid = (F_all[:, 0] != F_all[:, 1]) & (F_all[:, 1] != F_all[:, 2]) & (F_all[:, 0] != F_all[:, 2])
        F = F_all[valid]
        a = F.reshape(-1)
        b = F[:, [1, 2, 0]].reshape(-1)
        nv = len(self.V)
        und = np.minimum(a, b) * nv + np.maximum(a, b)
        _, inv, cnt = np.unique(und, return_inverse=True, return_counts=True)
        d = a * nv + b
        ud, dc = np.unique(d, return_counts=True)
        n = len(F)
        parent = list(range(n))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        face_of_edge = np.repeat(np.arange(n), 3)
        order = np.argsort(und, kind="stable")
        su = und[order]
        sf = face_of_edge[order]
        same = np.nonzero(su[1:] == su[:-1])[0]
        for i in same:
            ra, rb = find(int(sf[i])), find(int(sf[i + 1]))
            if ra != rb:
                parent[ra] = rb
        roots = np.array([find(i) for i in range(n)])
        lab = np.unique(roots, return_inverse=True)[1] if n else np.zeros(0, dtype=int)
        self.labels = np.full(len(F_all), -1, dtype=int)
        self.labels[valid] = lab
        comps = int(lab.max()) + 1 if n else 0
        return {"open_edges": int((cnt == 1).sum()), "over_edges": int((cnt > 2).sum()),
                "flipped_edges": int((dc > 1).sum()), "components": comps,
                "degenerate_faces": int((self.area < 1e-9).sum()), "collapsed_faces": int((~valid).sum())}

    def component_rows(self):
        """連結成分ごとの体積・最下点・ベッドに接する面積。topology() の後で呼ぶ。"""
        rows = []
        for k in range(int(self.labels.max()) + 1):
            m = self.labels == k
            T = self.T[m]
            vol = float(np.einsum("ij,ij->i", T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6.0)
            zmax = T[:, :, 2].max(axis=1)
            bed = float(self.area[m][(self.n[m, 2] < -0.999) & (zmax <= 0.05)].sum())
            rows.append({"faces": int(m.sum()), "volume_cm3": round(vol / 1000.0, 4),
                         "z_min_mm": round(float(T[:, :, 2].min()), 3), "bed_contact_mm2": round(bed, 2),
                         "grounded": bed > 1.0})
        return rows


# =============================================================================================
# 剛体変換（組立姿勢 -> 刷る向き）
# =============================================================================================
def rigid_fit(A, P):
    """対応する三角形 A, P（(n,3,3)）から P = R A + t を求める。返り値: R, t, 頂点の最大残差, 面の法線の最小内積, 面積比の範囲。"""
    a = A.reshape(-1, 3)
    p = P.reshape(-1, 3)
    ac, pc = a.mean(axis=0), p.mean(axis=0)
    H = (a - ac).T @ (p - pc)
    U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))             # -1 なら最良の対応が鏡像（回転だけでは重ならない）
    R = Vt.T @ np.diag([1.0, 1.0, d]) @ U.T
    t = pc - R @ ac
    resid = float(np.abs(a @ R.T + t - p).max())
    sa, sp = Solid(A), Solid(P)
    ok = (sa.area > 1e-2) & (sp.area > 1e-2)          # 面積のほぼ 0 の細長い三角形は、法線と面積が丸めで揺れるので比べない
    dots = np.einsum("ij,ij->i", sa.n[ok] @ R.T, sp.n[ok])
    ratio = sp.area[ok] / sa.area[ok]
    return R, t, resid, float(dots.min()), (float(ratio.min()), float(ratio.max())), float(d)


# =============================================================================================
# 面の塊（clusters）
# =============================================================================================
def face_clusters(S, mask):
    """mask の面を、頂点を共有するもの同士でまとめる。面番号の配列のリストを返す。"""
    idx = np.nonzero(mask)[0]
    if len(idx) == 0:
        return []
    parent = {int(i): int(i) for i in idx}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    owner = {}
    for i in idx:
        for v in S.F[i]:
            v = int(v)
            if v in owner:
                ra, rb = find(owner[v]), find(int(i))
                if ra != rb:
                    parent[ra] = rb
            else:
                owner[v] = int(i)
    groups = {}
    for i in idx:
        groups.setdefault(find(int(i)), []).append(int(i))
    return [np.array(g) for g in groups.values()]


def rasterize_xy(T, res):
    """三角形（(k,3,3)）の XY 投影を res mm の格子に塗る。返り値: 真偽の配列 (ny, nx) と原点 (x0, y0)。"""
    xy = T[:, :, :2]
    lo = xy.reshape(-1, 2).min(axis=0) - res
    hi = xy.reshape(-1, 2).max(axis=0) + res
    nx = int(math.ceil((hi[0] - lo[0]) / res)) + 1
    ny = int(math.ceil((hi[1] - lo[1]) / res)) + 1
    img = np.zeros((ny, nx), dtype=bool)
    for tri in xy:
        x0, y0 = tri.min(axis=0)
        x1, y1 = tri.max(axis=0)
        i0 = max(int(math.floor((x0 - lo[0]) / res)), 0)
        i1 = min(int(math.ceil((x1 - lo[0]) / res)), nx - 1)
        j0 = max(int(math.floor((y0 - lo[1]) / res)), 0)
        j1 = min(int(math.ceil((y1 - lo[1]) / res)), ny - 1)
        gx, gy = np.meshgrid(lo[0] + (np.arange(i0, i1 + 1) + 0.5) * res,
                             lo[1] + (np.arange(j0, j1 + 1) + 0.5) * res)
        p0, p1, p2 = tri
        den = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
        if abs(den) < 1e-12:
            continue
        w0 = ((p1[1] - p2[1]) * (gx - p2[0]) + (p2[0] - p1[0]) * (gy - p2[1])) / den
        w1 = ((p2[1] - p0[1]) * (gx - p2[0]) + (p0[0] - p2[0]) * (gy - p2[1])) / den
        w2 = 1.0 - w0 - w1
        eps = -1e-9
        img[j0:j1 + 1, i0:i1 + 1] |= (w0 >= eps) & (w1 >= eps) & (w2 >= eps)
    return img, lo


def inscribed_diameter(img, res, max_boundary=1500):
    """塗った領域の内接円の直径（= 橋の幅）と、領域の最長の長さ。格子の外は領域外とみなす。"""
    pad = np.pad(img, 1)
    inner = pad[1:-1, 1:-1]
    boundary = inner & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    by, bx = np.nonzero(boundary)
    iy, ix = np.nonzero(inner)
    if len(by) == 0:
        return 0.0, 0.0
    if len(by) > max_boundary:
        pick = np.linspace(0, len(by) - 1, max_boundary).astype(int)
        by, bx = by[pick], bx[pick]
    best = 0.0
    chunk = max(1, 4_000_000 // len(by))
    for s in range(0, len(iy), chunk):
        dy = iy[s:s + chunk, None] - by[None, :]
        dx = ix[s:s + chunk, None] - bx[None, :]
        d = np.sqrt((dy * dy + dx * dx).min(axis=1))
        best = max(best, float(d.max()))
    # 最長の長さ: 領域の点の対角（凸包でなく外接の対角で近似せず、境界点の最遠距離）
    pts = np.stack([bx, by], axis=1).astype(float)
    far = 0.0
    if len(pts) > 1:
        sub = pts if len(pts) <= 800 else pts[np.linspace(0, len(pts) - 1, 800).astype(int)]
        dd = np.sqrt(((sub[:, None, :] - sub[None, :, :]) ** 2).sum(axis=2))
        far = float(dd.max())
    return (best * 2.0 + 1.0) * res, (far + 1.0) * res


def overhang_clusters(S, visible, layer=LAYER):
    """刷る向き（z が上）で、水平から 45 度より寝た下向きの面の塊。ベッドに接する面は数えない。

    visible は面ごとの真偽（組立姿勢で外から見える面）。返り値は塊ごとの dict のリスト（面積の大きい順）。
    """
    zmax = S.T[:, :, 2].max(axis=1)
    zmin = S.T[:, :, 2].min(axis=1)
    down = (S.n[:, 2] < -COS_OVERHANG) & (S.area >= 0.01)         # 面積のほぼ 0 の細長い三角形は法線が不安定なので数えない
    on_bed = (zmax <= 0.01) | ((zmin <= 0.01) & (zmax <= layer + 1e-6))
    mask = down & ~on_bed
    rows = []
    for g in face_clusters(S, mask):
        T = S.T[g]
        area = float(S.area[g].sum())
        vis_area = float(S.area[g][visible[g]].sum())
        res = 0.05
        while True:
            span = (T[:, :, :2].reshape(-1, 2).max(axis=0) - T[:, :, :2].reshape(-1, 2).min(axis=0))
            if (span[0] / res) * (span[1] / res) <= 45000:
                break
            res *= 1.5
        img, _ = rasterize_xy(T, res)
        bridge, length = inscribed_diameter(img, res)
        angle = np.degrees(np.arccos(np.clip(-S.n[g, 2], 0.0, 1.0)))
        rows.append({
            "faces": int(len(g)), "area_mm2": round(area, 3), "visible_area_mm2": round(vis_area, 3),
            "incline_from_horizontal_deg": [round(float(angle.min()), 1), round(float(angle.max()), 1)],
            "z_mm": [round(float(T[:, :, 2].min()), 2), round(float(T[:, :, 2].max()), 2)],
            "bbox_mm": [[round(float(v), 2) for v in T.reshape(-1, 3).min(axis=0)],
                        [round(float(v), 2) for v in T.reshape(-1, 3).max(axis=0)]],
            "bridge_width_mm": round(bridge, 2), "bridge_length_mm": round(length, 2),
            "raster_res_mm": round(res, 3),
        })
    rows.sort(key=lambda r: -r["area_mm2"])
    return rows


def terrace_faces(S, visible):
    """見える面の、水平から 25 度以内の上向きの浅い斜面（0.2mm の層が段になる）。水平な面（2 度以内）と最下層は除く。"""
    zmax = S.T[:, :, 2].max(axis=1)
    up = (S.n[:, 2] > math.cos(math.radians(25.0))) & (S.n[:, 2] < math.cos(math.radians(2.0))) & (S.area >= 0.01)
    mask = up & visible & (zmax > LAYER)
    rows = []
    for g in face_clusters(S, mask):
        T = S.T[g]
        angle = np.degrees(np.arccos(np.clip(S.n[g, 2], 0.0, 1.0)))
        rows.append({"area_mm2": round(float(S.area[g].sum()), 2),
                     "incline_deg": [round(float(angle.min()), 1), round(float(angle.max()), 1)],
                     "z_mm": [round(float(T[:, :, 2].min()), 2), round(float(T[:, :, 2].max()), 2)],
                     "bbox_mm": [[round(float(v), 1) for v in T.reshape(-1, 3).min(axis=0)],
                                 [round(float(v), 1) for v in T.reshape(-1, 3).max(axis=0)]]})
    rows.sort(key=lambda r: -r["area_mm2"])
    return rows


# =============================================================================================
# 肉厚（光線）
# =============================================================================================
def sample_faces(S, min_face=0.2, big=3.0, spacing=1.0, budget=60000):
    """肉厚を測る点。面積 min_face（mm2）未満の細長い三角形は測らない（重心が縁に寄り、法線も不安定で偽の値が出る）。

    面積 big 以下の面は重心 1 点。それより大きい面は、細かい三角形に割った重心を並べる（大きな壁の面の裏の薄い所を見逃さない）。
    返り値: 点 pts、その面の法線 nrm、面番号 fidx、その点が代表する面積 w。
    """
    idx = np.nonzero(S.area >= min_face)[0]
    small = idx[S.area[idx] <= big]
    large = idx[S.area[idx] > big]
    pts, nrm, fidx, w = [S.c[small]], [S.n[small]], [small], [S.area[small]]
    if len(large):
        sp = max(spacing, math.sqrt(float(S.area[large].sum()) / budget))
        for i in large:
            k = max(1, int(math.ceil(math.sqrt(float(S.area[i])) / sp)))
            a, b, c = S.T[i]
            # 一辺 k 分割の格子の小三角形の重心（上向き k(k+1)/2 個と下向き k(k-1)/2 個。面積はどれも area / k^2）
            uu, vv = [], []
            for p in range(k):
                for q in range(k - p):
                    uu.append((p + 1.0 / 3.0) / k)
                    vv.append((q + 1.0 / 3.0) / k)
                    if p + q < k - 1:
                        uu.append((p + 2.0 / 3.0) / k)
                        vv.append((q + 2.0 / 3.0) / k)
            uu, vv = np.array(uu), np.array(vv)
            pt = a + np.outer(uu, b - a) + np.outer(vv, c - a)
            pts.append(pt)
            nrm.append(np.repeat(S.n[i][None, :], len(pt), axis=0))
            fidx.append(np.full(len(pt), i))
            w.append(np.full(len(pt), S.area[i] / (k * k)))
    return {"pts": np.vstack(pts), "nrm": np.vstack(nrm), "fidx": np.concatenate(fidx), "w": np.concatenate(w)}


def ray_points(S, pts, nrm, cap=60.0, chunk=96):
    """点 pts から内側（-nrm）へ打つ光線の肉厚。返り値: thickness（当たらなければ nan）, opposite（向かいの面が反対を向く）。"""
    n = len(pts)
    thick = np.full(n, np.nan)
    opp = np.zeros(n, dtype=bool)
    v0 = S.T[:, 0]
    e1 = S.T[:, 1] - v0
    e2 = S.T[:, 2] - v0
    for s in range(0, n, chunk):
        idx = np.arange(s, min(n, s + chunk))
        orig = pts[idx] - nrm[idx] * 1e-3
        d = -nrm[idx]
        pvec = np.cross(d[:, None, :], e2[None, :, :])               # (c, m, 3)
        det = np.einsum("mk,cmk->cm", e1, pvec)
        ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
        tvec = orig[:, None, :] - v0[None, :, :]
        u = np.einsum("cmk,cmk->cm", tvec, pvec) * inv
        qvec = np.cross(tvec, e1[None, :, :])
        v = np.einsum("ck,cmk->cm", d, qvec) * inv
        t = np.einsum("mk,cmk->cm", e2, qvec) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-7) & (t < cap)
        tt = np.where(hit, t, np.inf)
        j = tt.argmin(axis=1)
        tmin = tt[np.arange(len(idx)), j]
        found = np.isfinite(tmin)
        thick[idx[found]] = tmin[found] + 1e-3
        dots = np.einsum("ck,ck->c", S.n[j], nrm[idx])
        opp[idx[found]] = dots[found] < -0.6
    return thick, opp


def thickness_field(S, **kw):
    """全面の肉厚の標本。返り値の dict: pts, nrm, fidx, w, th（肉厚）, opp（向かいの面が反対を向く）, valid（opp かつ有限）。"""
    f = sample_faces(S, **kw)
    th, opp = ray_points(S, f["pts"], f["nrm"])
    f["th"], f["opp"] = th, opp
    f["valid"] = opp & np.isfinite(th)
    return f


def cluster_points(pts, w, values, radius=2.0):
    """点を近い順にまとめ、代表面積（w の和）・位置の範囲・値の最小を返す。min_mm 昇順。"""
    if len(pts) == 0:
        return []
    cells = {}
    for i, c in enumerate(pts):
        cells.setdefault((round(c[0] / radius), round(c[1] / radius), round(c[2] / radius)), []).append(i)
    keys = list(cells)
    parent = {k: k for k in keys}

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k
    for k in keys:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    nb = (k[0] + dx, k[1] + dy, k[2] + dz)
                    if nb in parent:
                        ra, rb = find(nb), find(k)
                        if ra != rb:
                            parent[ra] = rb
    groups = {}
    for k in keys:
        groups.setdefault(find(k), []).extend(cells[k])
    rows = []
    for g in groups.values():
        g = np.array(g)
        rows.append({"samples": int(len(g)), "area_mm2": round(float(w[g].sum()), 2),
                     "at_mm": [[round(float(v), 1) for v in pts[g].min(axis=0)],
                               [round(float(v), 1) for v in pts[g].max(axis=0)]],
                     "min_mm": round(float(values[g].min()), 2)})
    rows.sort(key=lambda r: (r["min_mm"], -r["area_mm2"]))
    return rows


# =============================================================================================
# 断面（層）
# =============================================================================================
def slice_loops(S, z):
    """水平面 z での断面の輪（(k,2) の配列のリスト）と、輪にならなかった断面の欠陥数。"""
    zz = S.V[:, 2]
    side = zz[S.F] > z
    cnt = side.sum(axis=1)
    idx = np.nonzero((cnt == 1) | (cnt == 2))[0]
    if len(idx) == 0:
        return [], 0
    F = S.F[idx]
    sd = side[idx]
    nxt = F[:, [1, 2, 0]]
    cross = sd != sd[:, [1, 2, 0]]
    order = np.argsort(~cross, axis=1, kind="stable")[:, :2]
    ea = np.take_along_axis(F, order, axis=1)
    eb = np.take_along_axis(nxt, order, axis=1)
    lo = np.minimum(ea, eb)
    hi = np.maximum(ea, eb)
    nv = len(S.V)
    key = lo * nv + hi
    ukey, inv = np.unique(key.reshape(-1), return_inverse=True)
    ulo = ukey // nv
    uhi = ukey % nv
    zl, zh = zz[ulo], zz[uhi]
    t = (z - zl) / (zh - zl)
    pts = S.V[ulo, :2] + (S.V[uhi, :2] - S.V[ulo, :2]) * t[:, None]
    seg = inv.reshape(-1, 2)
    adj = {}
    for a, b in seg.tolist():
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    loops, seen, bad = [], set(), 0
    for start in adj:
        if start in seen:
            continue
        loop, prev, cur = [start], None, start
        seen.add(start)
        closed = False
        for _ in range(len(adj) + 2):
            nb = adj[cur]
            if len(nb) != 2:
                break
            nx = nb[0] if nb[0] != prev else nb[1]
            if prev is None:
                nx = nb[0]
            if nx == start:
                closed = True
                break
            if nx in seen:
                break
            loop.append(nx)
            seen.add(nx)
            prev, cur = cur, nx
        if closed and len(loop) >= 3:
            loops.append(pts[loop])
        else:
            bad += 1
    return loops, bad


def shoelace(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def pip(poly, pts):
    """多角形 poly（(k,2)）の内側にある点 pts（(m,2)）の真偽。"""
    x, y = pts[:, 0][:, None], pts[:, 1][:, None]
    x0, y0 = poly[:, 0][None, :], poly[:, 1][None, :]
    x1, y1 = np.roll(poly[:, 0], -1)[None, :], np.roll(poly[:, 1], -1)[None, :]
    cond = (y0 > y) != (y1 > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        xin = (x1 - x0) * (y - y0) / (y1 - y0) + x0
    return (cond & (x < xin)).sum(axis=1) % 2 == 1


def hull(points):
    pts = sorted({(round(float(p[0]), 5), round(float(p[1]), 5)) for p in points})
    if len(pts) <= 2:
        return np.array(pts)

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower = []
    for p in pts:
        while len(lower) >= 2 and cr(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cr(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.array(lower[:-1] + upper[:-1])


def min_caliper(poly):
    """凸包の最小の幅（mm）。"""
    h = hull(poly)
    if len(h) < 3:
        return 0.0
    best = float("inf")
    for i in range(len(h)):
        a, b = h[i], h[(i + 1) % len(h)]
        e = b - a
        ln = float(np.hypot(*e))
        if ln < 1e-9:
            continue
        nrm = np.array([-e[1], e[0]]) / ln
        w = float(np.ptp((h - a) @ nrm))
        best = min(best, w)
    return best


def resample(poly, step=0.5, cap=300):
    k = len(poly)
    closed = np.vstack([poly, poly[:1]])
    seg = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    total = seg.sum()
    m = int(min(cap, max(8, total / step)))
    s = np.linspace(0.0, total, m, endpoint=False)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    x = np.interp(s, cum, closed[:, 0])
    y = np.interp(s, cum, closed[:, 1])
    return np.stack([x, y], axis=1)


def layer_islands(loops):
    """輪を島（外周 + 穴）にまとめる。返り値: 島のリスト。"""
    n = len(loops)
    if n == 0:
        return []
    areas = [shoelace(p) for p in loops]
    absa = [abs(a) for a in areas]
    parent = [-1] * n
    depth = [0] * n
    for i in range(n):
        containers = []
        probe = loops[i][:1]
        for j in range(n):
            if j == i or absa[j] <= absa[i]:
                continue
            if pip(loops[j], probe)[0]:
                containers.append(j)
        depth[i] = len(containers)
        if containers:
            parent[i] = min(containers, key=lambda j: absa[j])
    islands = []
    for i in range(n):
        if depth[i] % 2 == 0:
            holes = [j for j in range(n) if parent[j] == i and depth[j] % 2 == 1]
            outer = loops[i]
            area = absa[i] - sum(absa[j] for j in holes)
            lo, hi = outer.min(axis=0), outer.max(axis=0)
            islands.append({"outer": outer, "holes": [loops[j] for j in holes], "area": area,
                            "caliper": min_caliper(outer), "centroid": (lo + hi) / 2.0, "lo": lo, "hi": hi})
    return islands


def in_island(isl, pts):
    inside = pip(isl["outer"], pts)
    for h in isl["holes"]:
        inside &= ~pip(h, pts)
    return inside


def overlap(a, b):
    """島 a, b の断面が重なるか（輪の上の点を相手の中に入れて調べる）。"""
    if np.any(a["hi"] < b["lo"]) or np.any(b["hi"] < a["lo"]):
        return False
    for x, y in ((a, b), (b, a)):
        pts = np.vstack([resample(x["outer"])] + [resample(h) for h in x["holes"]])
        if in_island(y, pts).any():
            return True
    return False


def slice_layers(S, layer=LAYER, ratio_limit=5.0):
    """全層を切り、島ごとの太さ（凸包の最小幅）と積み上がる高さを追う。

    h は、その島が「広い土台から立ち上がって」からの高さ。親の島（1 層下で重なるもの）の面積の半分未満になったら
    立ち上がり直し（柱が土台から生える）として h を 0 に戻す。親が無い島（ベッドの第 1 層以外）は空中から始まる島として数える。
    """
    nl = int(math.ceil((S.hi[2] - 1e-6) / layer))
    prev = []
    flagged, floating, bad_layers = [], [], 0
    peak = {"ratio": 0.0}
    chains = []
    first_layer_area = 0.0
    for k in range(nl):
        z = (k + 0.5) * layer + 1.3e-4
        loops, bad = slice_loops(S, z)
        bad_layers += 1 if bad else 0
        cur = layer_islands(loops)
        for isl in cur:
            parents = [p for p in prev if overlap(isl, p)]
            isl["floating"] = (k > 0 and not parents)
            if not parents:
                isl.update(h=layer, base=isl["caliper"], amax=isl["area"], wmax=isl["caliper"], z0=k * layer,
                           hl=layer, wref=isl["caliper"])
            else:
                main = max(parents, key=lambda p: p["area"])
                if isl["area"] < 0.5 * main["area"]:
                    isl.update(h=layer, base=main["caliper"], amax=isl["area"], wmax=isl["caliper"], z0=k * layer,
                               hl=layer, wref=isl["caliper"])
                else:
                    isl.update(h=main["h"] + layer, base=main["base"], amax=max(main["amax"], isl["area"]),
                               wmax=max(main["wmax"], isl["caliper"]), z0=main["z0"])
                    # 局所の高さ: 太さが 1.5 分の 1 未満に細った所から数え直す（細い先が太い土台の上に載る形）
                    if isl["caliper"] * 1.5 < main["wref"]:
                        isl.update(hl=layer, wref=isl["caliper"])
                    else:
                        isl.update(hl=main["hl"] + layer, wref=max(main["wref"], isl["caliper"]))
            if isl["floating"]:
                floating.append({"z_mm": round(k * layer, 2), "area_mm2": round(isl["area"], 2),
                                 "at_mm": [round(float(v), 1) for v in isl["centroid"]]})
            w = max(isl["caliper"], 1e-6)
            r = isl["h"] / w
            if r > peak["ratio"] and isl["h"] > 2.0:
                peak = {"ratio": round(r, 2), "z_mm": round((k + 1) * layer, 2), "height_mm": round(isl["h"], 2),
                        "width_mm": round(w, 2), "at_mm": [round(float(v), 1) for v in isl["centroid"]]}
            if r > ratio_limit and isl["area"] >= 0.6 * isl["amax"] and isl["h"] > layer * 2:
                flagged.append({"z_mm": round((k + 1) * layer, 2), "height_mm": round(isl["h"], 2),
                                "width_mm": round(w, 2), "ratio": round(r, 2),
                                "local_height_mm": round(isl["hl"], 2), "local_ratio": round(isl["hl"] / w, 2),
                                "column_width_mm": round(isl["wmax"], 2),
                                "at_mm": [round(float(v), 1) for v in isl["centroid"]],
                                "span_mm": [[round(float(v), 1) for v in isl["lo"]],
                                            [round(float(v), 1) for v in isl["hi"]]]})
        if k == 0:
            first_layer_area = sum(i["area"] for i in cur)
        prev = cur
    # 同じ柱の連続した層をまとめる（近い重心で z が連続するものを 1 本にして、最悪の層と範囲を残す）
    parent = list(range(len(flagged)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i in range(len(flagged)):
        for j in range(i + 1, len(flagged)):
            a_, b_ = flagged[i], flagged[j]
            if abs(a_["z_mm"] - b_["z_mm"]) <= 2 * layer + 1e-6 and                     math.hypot(a_["at_mm"][0] - b_["at_mm"][0], a_["at_mm"][1] - b_["at_mm"][1]) < 3.0:
                parent[find(i)] = find(j)
    groups = {}
    for i, f in enumerate(flagged):
        groups.setdefault(find(i), []).append(f)
    grouped = []
    for rows in groups.values():
        worst = dict(max(rows, key=lambda r: r["ratio"]))
        worst["z_from_mm"] = min(r["z_mm"] for r in rows)
        worst["z_to_mm"] = max(r["z_mm"] for r in rows)
        grouped.append(worst)
    grouped.sort(key=lambda r: (-r["ratio"], r["z_from_mm"]))
    return {"layers": nl, "peak": peak, "slender": grouped,
            "floating_islands": floating, "bad_layers": bad_layers, "first_layer_area_mm2": round(first_layer_area, 1)}


# =============================================================================================
# ベッドに接する縁の面取り（第 1 層の膨らみ）
# =============================================================================================
def first_layer_chamfer(S, z_low=0.1):
    """第 1 層（z=0.1）の輪が、上の鉛直な壁の位置より内側へ（外周）／外側へ（穴）どれだけ引っ込んでいるか（面取り幅 mm）。

    基準の輪 z_ref = 1.7（低い部品は天の 0.1 下）。o(z) = 基準の輪から測った z の輪の動き（面積差 / 周長。外周は小さいほど正、
    穴は大きいほど正）。傾いた壁は o が z に比例するので、z_ref-0.4 での値から z=0.1 へ直線で延ばした値を引く:
        chamfer_mm = o(0.1) - o(z_ref - 0.4) * (z_ref - 0.1) / 0.4
    鉛直な壁の根元の 0.3mm の 45 度面取りは 0.2、1.0mm の面取りは 0.9。60 度の斜面は 0（面取りと誤認しない）。
    """
    eps = 1.3e-4
    top = float(S.hi[2]) - 0.1

    def total(z):
        return sum(i["area"] for i in layer_islands(slice_loops(S, z + eps)[0]))
    z_ref = min(1.7, top)
    for cand in (1.7, 1.3, 0.9):                       # 壁が鉛直な（面積が変わらない）一番高い基準を選ぶ
        if cand > top:
            continue
        a1, a0 = total(cand), total(cand - 0.4)
        if a1 > 0 and abs(a1 - a0) / a1 < 0.02:
            z_ref = cand
            break
    z_mid = z_ref - 0.4
    lv = [layer_islands(slice_loops(S, z + eps)[0]) for z in (z_low, z_mid, z_ref)]

    def entries(islands):
        out = []
        for isl in islands:
            out.append(("outer", isl["outer"]))
            for h in isl["holes"]:
                out.append(("hole", h))
        return out
    ent = [entries(i) for i in lv]

    def center(loop):
        return (loop.min(axis=0) + loop.max(axis=0)) / 2.0

    def match(kind, loop, pool, a_ref):
        c = center(loop)
        best, bd = None, 1e9
        for k2, l2 in pool:
            if k2 != kind:
                continue
            dist = float(np.linalg.norm(center(l2) - c))
            a2 = abs(shoelace(l2))
            if dist < bd and 0.5 < a2 / max(a_ref, 1e-9) < 2.0:
                best, bd = l2, dist
        return best if (best is not None and bd <= 1.5) else None

    def offset(kind, loop_z, loop_ref, per_ref):
        a_z, a_ref = abs(shoelace(loop_z)), abs(shoelace(loop_ref))
        return ((a_ref - a_z) if kind == "outer" else (a_z - a_ref)) / per_ref

    rows = []
    for kind, ref in ent[2]:
        a_ref = abs(shoelace(ref))
        per = float(np.linalg.norm(np.diff(np.vstack([ref, ref[:1]]), axis=0), axis=1).sum())
        c = center(ref)
        ext = ref.max(axis=0) - ref.min(axis=0)
        row = {"kind": kind, "centroid_mm": [round(float(v), 1) for v in c],
               "size_mm": [round(float(ext[0]), 2), round(float(ext[1]), 2)], "chamfer_mm": None}
        lo, mid = match(kind, ref, ent[0], a_ref), match(kind, ref, ent[1], a_ref)
        if lo is not None and mid is not None:
            o_low = offset(kind, lo, ref, per)
            o_mid = offset(kind, mid, ref, per)
            row["chamfer_mm"] = round(float(o_low - o_mid * (z_ref - z_low) / (z_ref - z_mid)), 3)
        rows.append(row)
    return rows


# =============================================================================================
# 質量の見込み
# =============================================================================================
def estimate_mass(S, density=1.26, wall_loops=2, line_outer=0.42, line_inner=0.45, top_layers=5, bottom_layers=3,
                  layer=LAYER, infill=0.15):
    """スライスせずに PLA の質量を見込む（Bambu Studio「0.20mm Standard @BBL X1C」の既定: 壁 2 周、上 5 層、下 3 層、充填 15%）。

    殻の体積 V_s = min(V, sum_i A_i t_i)。面 i の殻の厚み t_i = t_side |n_xy| + t_cap |n_z|
    （t_side = 壁の線幅の和 0.42 + 0.45 = 0.87、t_cap = 上向きなら 5 x 0.2 = 1.0、下向きなら 3 x 0.2 = 0.6）。
    質量 m = density (V_s + infill (V - V_s)) / 1000 [g]（density は Bambu PLA Basic の 1.26 g/cm3、V は mm3）。
    薄い部品は殻が重なって数えすぎるので V で頭打ちにしている（上側の見込み）。solid_g は全部中実の上限。
    """
    nz = S.n[:, 2]
    nxy = np.sqrt(np.clip(1.0 - nz * nz, 0.0, 1.0))
    t_side = line_outer + (wall_loops - 1) * line_inner
    t = t_side * nxy + np.where(nz > 0, top_layers * layer, bottom_layers * layer) * np.abs(nz)
    vol = S.volume()
    v_shell = min(vol, float((S.area * t).sum()))
    v_in = max(0.0, vol - v_shell)
    return {"volume_cm3": round(vol / 1000.0, 3), "shell_cm3": round(v_shell / 1000.0, 3),
            "mass_g": round(density * (v_shell + infill * v_in) / 1000.0, 2),
            "solid_g": round(density * vol / 1000.0, 2)}


# =============================================================================================
# ベッドの接地
# =============================================================================================
def bed_contact(S):
    zmax = S.T[:, :, 2].max(axis=1)
    mask = (S.n[:, 2] < -0.999) & (zmax <= 0.05) & (S.area > 1e-9)
    area = float(S.area[mask].sum())
    pts = S.T[mask].reshape(-1, 3)[:, :2]
    height = float(S.hi[2])
    com = S.com()
    if len(pts) < 3:
        return {"contact_mm2": round(area, 1), "footprint_caliper_mm": 0.0, "height_mm": round(height, 1),
                "height_over_caliper": None, "com_over_footprint": False}
    h = hull(pts)
    cal = min_caliper(h)
    inside = bool(pip(h, np.array([[com[0], com[1]]]))[0]) if len(h) >= 3 else False
    return {"contact_mm2": round(area, 1), "footprint_caliper_mm": round(cal, 2), "height_mm": round(height, 1),
            "height_over_caliper": round(height / cal, 2) if cal > 1e-6 else None,
            "com_over_footprint": inside,
            "com_xy_mm": [round(float(com[0]), 1), round(float(com[1]), 1)],
            "footprint_bbox_mm": [round(float(np.ptp(pts[:, 0])), 1), round(float(np.ptp(pts[:, 1])), 1)]}


# =============================================================================================
# 校正用の形（閉じた 1 つのメッシュ）
# =============================================================================================
def _ear_clip(poly):
    """単純多角形（反時計回り）を三角形の添字へ。"""
    idx = list(range(len(poly)))
    out = []

    def cr(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if cr(a, b, c) <= 1e-12:
                continue
            ear = True
            for j in idx:
                if j in (i0, i1, i2):
                    continue
                p = poly[j]
                if cr(a, b, p) >= -1e-12 and cr(b, c, p) >= -1e-12 and cr(c, a, p) >= -1e-12:
                    ear = False
                    break
            if ear:
                out.append((i0, i1, i2))
                idx.pop(k)
                break
    out.append((idx[0], idx[1], idx[2]))
    return out


def extrude_poly(poly_yz, x0, x1):
    """YZ 平面の単純多角形を X 方向に押し出した閉じたメッシュ（(n,3,3)）。多角形は何回りでもよい。"""
    poly = [tuple(p) for p in poly_yz]
    area = 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))
    if area < 0:
        poly = poly[::-1]
    tris = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        p00, p01 = (x0, a[0], a[1]), (x0, b[0], b[1])
        p10, p11 = (x1, a[0], a[1]), (x1, b[0], b[1])
        tris.append((p00, p11, p10))
        tris.append((p00, p01, p11))
    for i0, i1, i2 in _ear_clip(poly):
        a, b, c = poly[i0], poly[i1], poly[i2]
        tris.append(((x1, a[0], a[1]), (x1, b[0], b[1]), (x1, c[0], c[1])))
        tris.append(((x0, a[0], a[1]), (x0, c[0], c[1]), (x0, b[0], b[1])))
    return np.array(tris, dtype=float)


def loft(rings):
    """(z, (x0, x1, y0, y1)) の並びを下から積んだ閉じたメッシュ。z が違う隣は側面、同じ z で矩形が違う隣は段（入れ子の矩形）。"""
    def corners(r, z):
        x0, x1, y0, y1 = r
        return [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    tris = []

    def quad(a, b, c, d):
        tris.append((a, b, c))
        tris.append((a, c, d))
    z0, r0 = rings[0]
    c = corners(r0, z0)
    quad(c[0], c[3], c[2], c[1])                                  # 底（下向き）
    for (za, ra), (zb, rb) in zip(rings[:-1], rings[1:]):
        ca, cb = corners(ra, za), corners(rb, zb)
        if abs(zb - za) > 1e-12:
            for i in range(4):
                j = (i + 1) % 4
                quad(ca[i], ca[j], cb[j], cb[i])
        else:
            area_a = (ra[1] - ra[0]) * (ra[3] - ra[2])
            area_b = (rb[1] - rb[0]) * (rb[3] - rb[2])
            big, small = (ca, cb) if area_a > area_b else (cb, ca)
            for i in range(4):
                j = (i + 1) % 4
                if area_a > area_b:        # 上が小さい: 肩（上向き）
                    quad(big[i], big[j], small[j], small[i])
                else:                      # 上が大きい: 張り出しの下面（下向き）
                    quad(small[i], small[j], big[j], big[i])
    zt, rt = rings[-1]
    c = corners(rt, zt)
    quad(c[0], c[1], c[2], c[3])                                  # 天（上向き）
    return np.array(tris, dtype=float)


def box_solid(x0, x1, y0, y1, z0, z1):
    return loft([(z0, (x0, x1, y0, y1)), (z1, (x0, x1, y0, y1))])
