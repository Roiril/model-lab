"""カメラから見た輪郭を目標にあわせる、画面平面方向の滑らかな歪み。numpy のみ。

頂点を画面へ写し、格子上の変位 (dx, dy) ピクセルを引いて、同じ奥行きのまま
画面と平行に動かす。model.py も同じ関数で再生して、同じ形を作り直す。
"""
import numpy as np


def basis(cam):
    az, el, roll = np.radians(cam["az"]), np.radians(cam["el"]), np.radians(cam["roll"])
    target = np.array([0.0, 123.0, 70.0])
    pos = target + cam["dist"] * np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    fwd = target - pos
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    c, s = np.cos(roll), np.sin(roll)
    right, up = c * right + s * up, -s * right + c * up
    return pos, fwd, right, up


def project(verts, cam):
    pos, fwd, right, up = basis(cam)
    rel = verts - pos
    depth = rel @ fwd
    u = cam["f"] * (rel @ right) / depth + cam["cx"]
    v = -cam["f"] * (rel @ up) / depth + cam["cy"]
    return u, v, depth


def sample(grid, spacing, u, v):
    """grid[gy, gx, 2] を、画素座標 (u, v) で双一次補間する。格子点は spacing 画素おき。"""
    gx = np.clip(u / spacing, 0, grid.shape[1] - 1.001)
    gy = np.clip(v / spacing, 0, grid.shape[0] - 1.001)
    x0, y0 = np.floor(gx).astype(int), np.floor(gy).astype(int)
    fx, fy = (gx - x0)[:, None], (gy - y0)[:, None]
    return ((1 - fx) * (1 - fy) * grid[y0, x0] + fx * (1 - fy) * grid[y0, x0 + 1]
            + (1 - fx) * fy * grid[y0 + 1, x0] + fx * fy * grid[y0 + 1, x0 + 1])


def apply(verts, cam, grid, spacing, alpha=1.0):
    pos, fwd, right, up = basis(cam)
    u, v, depth = project(verts, cam)
    d = sample(grid, spacing, u, v) * alpha
    shift = (right[None, :] * d[:, 0:1] - up[None, :] * d[:, 1:2]) * (depth / cam["f"])[:, None]
    return verts + shift
