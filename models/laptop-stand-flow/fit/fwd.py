"""輪郭あわせ用の高速な順方向モデル。numpy のみ。

モデル（shape_field.py と同じ式）の片側厚み h(y, z) を 1mm 格子で作り、
x = 一定の平面で切った断面を画像へ写して、その和集合を輪郭とする。
"""
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import ref_trace as T
import shape_field as P

G = 1.0                      # 格子 mm
Y0, Y1, Z0, Z1 = -2.0, 252.0, -1.0, 146.0
SEAT_Z = (T.GROUND_Y - T.PLANK_BOTTOM_Y) * P.S + 0.75
PLANK_TOP = (T.GROUND_Y - T.PLANK_TOP_Y) * P.S
PLANK_Y = ((T.PLANK_X[0] - T.ORIGIN_X) * P.S, (T.PLANK_X[1] - T.ORIGIN_X) * P.S)


class Field:
    def __init__(self, cache=HERE / "dist_cache.npz"):
        self.y = np.arange(Y0, Y1 + G, G)
        self.z = np.arange(Z0, Z1 + G, G)
        yy, zz = np.meshgrid(self.y, self.z, indexing="ij")
        self.yy, self.zz = yy, zz
        if cache.exists():
            z = np.load(cache)
            self.d, self.thick = z["d"], z["thick"]
            self.dh = z["dh"] if "dh" in z.files else self._hole_distance()
            if "dh" not in z.files:
                np.savez(cache, d=self.d, thick=self.thick, dh=self.dh)
        else:
            outer, hole = P.silhouette_polygons()
            inside = P.inside_mask(yy, zz, [outer, hole])
            dist = P.boundary_distance(yy, zz, [outer, hole])
            d = np.where(inside, dist, -dist)
            self.thick = P.local_thickness(np.maximum(d, 0.0), 9.0, G)
            self.d = P.blur(d, 1.6, G)
            self.dh = self._hole_distance()
            np.savez(cache, d=self.d, thick=self.thick, dh=self.dh)

    def _hole_distance(self):
        outer, hole = P.silhouette_polygons()
        return P.boundary_distance(self.yy, self.zz, [hole], step=0.3).astype(np.float64)

    def set_polygons(self, outer_ctrl, hole_ctrl):
        """制御点（mm）から d と thick を作り直す。"""
        outer = P.catmull_closed(outer_ctrl)
        hole = P.catmull_closed(hole_ctrl)
        inside = P.inside_mask(self.yy, self.zz, [outer, hole])
        dist = P.boundary_distance(self.yy, self.zz, [outer, hole], step=0.5)
        d = np.where(inside, dist, -dist)
        self.thick = P.local_thickness(np.maximum(d, 0.0), 9.0, G)
        self.d = P.blur(d, 1.6, G)

    def thickness(self, seeds, power=2.0, sigma=17.0, xc=None):
        """seeds: [(x_px, y_px, R, H)]。片側の厚み h(y, z)と、中心のXオフセット場。"""
        sy = np.array([P.to_mm((s[0], s[1]))[0] for s in seeds])
        sz = np.array([P.to_mm((s[0], s[1]))[1] for s in seeds])
        sr = np.array([s[2] for s in seeds], float)
        sh = np.array([s[3] for s in seeds], float)
        d2 = (self.yy[None] - sy[:, None, None]) ** 2 + (self.zz[None] - sz[:, None, None]) ** 2
        logw = -d2 / (2.0 * sigma ** 2)
        logw -= logw.max(axis=0)
        w = np.exp(logw)
        den = w.sum(axis=0)
        r_seed = (w * sr[:, None, None]).sum(axis=0) / den
        h_max = (w * sh[:, None, None]).sum(axis=0) / den
        if xc is None:
            xc_field = np.zeros_like(h_max)
        else:
            xc_field = (w * np.asarray(xc, float)[:, None, None]).sum(axis=0) / den
        r = P.blur(np.minimum(r_seed, np.maximum(self.thick, 1.0)), 2.5, G)
        u = np.maximum(0.0, 1.0 - self.d / r)
        # |x/H|^p + u^p <= 1  ->  |x| <= H (1 - u^p)^(1/p)
        h = h_max * np.maximum(0.0, 1.0 - u ** power) ** (1.0 / power)
        h = np.where(self.d > -0.0, h, 0.0)
        h = np.where((self.zz >= 0) & (self.zz <= SEAT_Z), h, 0.0)
        return h, xc_field


def camera_rays(p, shape, step):
    """p: dict(az, el, roll, dist, f, cx, cy)。shape=(h, w) は画像全体、step は間引き。"""
    az, el, roll = np.radians(p["az"]), np.radians(p["el"]), np.radians(p["roll"])
    target = np.array([0.0, 123.0, 70.0])
    pos = target + p["dist"] * np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    fwd = (target - pos)
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    c, s = np.cos(roll), np.sin(roll)
    right, up = c * right + s * up, -s * right + c * up
    h, w = shape
    v, u = np.mgrid[0:h:step, 0:w:step]
    u = u.astype(float) + step / 2
    v = v.astype(float) + step / 2
    dirs = (fwd[None, None] * p["f"] + right[None, None] * (u - p["cx"])[..., None]
            - up[None, None] * (v - p["cy"])[..., None])
    return pos, dirs


def silhouette(field_h, p, shape, step, roi, spacing, dy_mid=0.0, plank_half=12.0, slice_step=1.5, xc_field=None, plank_dy=(0.0, 0.0), single=False):
    """roi=(x0,y0,x1,y1)（画像座標）内の輪郭マスク。左の脚(x=+s/2)と中の脚(x=-s/2, y+dy_mid)。"""
    pos, dirs = camera_rays(p, shape, step)
    x0, y0, x1, y1 = [int(v // step) for v in roi]
    dirs = dirs[y0:y1, x0:x1]
    mask = np.zeros(dirs.shape[:2], bool)
    dx, dy, dz = dirs[..., 0], dirs[..., 1], dirs[..., 2]
    gy, gz = len(Field_y), len(Field_z)
    hmax = float(field_h.max())
    xcm = 0.0 if xc_field is None else float(np.abs(xc_field).max())
    units = ((spacing / 2.0, 0.0),) if single else ((spacing / 2.0, 0.0), (-spacing / 2.0, dy_mid))
    for ux, uy in units:
        c = -hmax - xcm
        while c <= hmax + xcm:
            X = ux + c
            t = (X - pos[0]) / dx
            ok = t > 0
            y = pos[1] + t * dy - uy
            z = pos[2] + t * dz
            iy = np.rint((y - Y0) / G).astype(int)
            iz = np.rint((z - Z0) / G).astype(int)
            ok &= (iy >= 0) & (iy < gy) & (iz >= 0) & (iz < gz)
            iy = np.clip(iy, 0, gy - 1)
            iz = np.clip(iz, 0, gz - 1)
            off = 0.0 if xc_field is None else xc_field[iy, iz]
            mask |= ok & (field_h[iy, iz] >= np.abs(c - off))
            if abs(c) <= plank_half:
                mask |= ok & (y >= PLANK_Y[0] + plank_dy[0]) & (y <= PLANK_Y[1] + plank_dy[1]) & (z >= PLANK_TOP - 7.5) & (z <= PLANK_TOP)
            c += slice_step
    return mask


Field_y = np.arange(Y0, Y1 + G, G)
Field_z = np.arange(Z0, Z1 + G, G)
