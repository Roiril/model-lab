"""参考画像のS字ノートPCスタンドを、側面輪郭の厚み付けで立体にする。

1. profile.py で側面輪郭から片側の厚み h(y, z) を作る
2. 3D格子上の符号付き場 |x| - h を、レール板と合わせて作る
3. 表面を surface nets で取り出し、Taubin 平滑化して Blender のメッシュにする
4. 左右2脚を並べて exports/laptop-stand-flow.stl に、1脚だけを -unit.stl に書き出す
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import bpy

from blender_utils import clear_scene, export_stl
from params import *
import shape_field as P
import ref_trace as T


def mm(value):
    return value * 1000.0


def build_grid():
    g = mm(GRID)
    y = np.arange(-2.0, 250.0 + 2 * g, g)
    z = np.arange(-1.0, 146.0 + 2 * g, g)
    half = 52.0
    x = np.arange(-half, half + g, g)
    return x.astype(np.float32), y.astype(np.float32), z.astype(np.float32)


def rounded_box(px, py, pz, y0, y1, z0, z1, half_x, edge, plan_r):
    """平面の角Rと稜線Rを持つ箱の符号付き距離。座標は mm。"""
    cy, hy = (y0 + y1) / 2.0, (y1 - y0) / 2.0
    cz, hz = (z0 + z1) / 2.0, (z1 - z0) / 2.0
    qx = np.abs(px) - (half_x - plan_r)
    qy = np.abs(py - cy) - (hy - plan_r)
    plan = np.hypot(np.maximum(qx, 0.0), np.maximum(qy, 0.0)) + np.minimum(np.maximum(qx, qy), 0.0) - plan_r
    az = np.abs(pz - cz) - hz
    a, b = plan + edge, az + edge
    return np.hypot(np.maximum(a, 0.0), np.maximum(b, 0.0)) + np.minimum(np.maximum(a, b), 0.0) - edge


def smooth_min(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def build_field(x, y, z):
    yy, zz = np.meshgrid(y, z, indexing="ij")
    d, r, h = P.section_params(yy.astype(np.float64), zz.astype(np.float64), mm(GRID))
    # 断面: |x/H|^p + (1 - d/R)^p = 1。d は輪郭からの深さ（内側が正）。
    u = np.maximum(0.0, 1.0 - d / r)
    p = SECTION_POWER
    body = (np.abs(x)[:, None, None] / h[None, :, :]) ** p + (u ** p)[None, :, :] - 1.0
    body *= 10.0
    # 本体は座の高さで水平に切る。足の底は z=0 で切る。
    seat_z = (T.GROUND_Y - T.PLANK_BOTTOM_Y) * P.S + 0.75
    body = np.maximum(body, z[None, None, :] - seat_z)
    body = np.maximum(body, -z[None, None, :])

    px, py, pz = np.meshgrid(x, y, z, indexing="ij")
    plank_top = (T.GROUND_Y - T.PLANK_TOP_Y) * P.S
    plank_bottom = plank_top - mm(PLANK_THICKNESS)
    plank_y0 = (T.PLANK_X[0] - T.ORIGIN_X) * P.S
    plank_y1 = (T.PLANK_X[1] - T.ORIGIN_X) * P.S
    plank = rounded_box(px, py, pz, plank_y0, plank_y1, plank_bottom, plank_top,
                        mm(PLANK_HALF_WIDTH), mm(PLANK_EDGE_RADIUS), mm(PLANK_END_RADIUS))
    lip = rounded_box(px, py, pz, plank_y1 - mm(LIP_LENGTH), plank_y1,
                      plank_bottom - mm(LIP_DROP), plank_bottom + 3.0,
                      mm(PLANK_HALF_WIDTH), 3.0, mm(PLANK_END_RADIUS))
    top = smooth_min(plank, lip, 3.0)
    return np.minimum(body, top)


def surface_nets(field, origin, pitch):
    """符号付き場から四角形メッシュを取り出す。field[i,j,k] は格子点の値。"""
    shape = np.array(field.shape) - 1
    inside = field < 0
    edges = []
    for axis in range(3):
        lo = [slice(None)] * 3
        hi = [slice(None)] * 3
        lo[axis] = slice(0, -1)
        hi[axis] = slice(1, None)
        a, b = field[tuple(lo)], field[tuple(hi)]
        cross = inside[tuple(lo)] != inside[tuple(hi)]
        idx = np.argwhere(cross)
        t = a[cross] / (a[cross] - b[cross])
        pos = idx.astype(np.float32)
        pos[:, axis] += t
        edges.append((idx, pos, a[cross] < 0))
    # 交点を、その辺を共有するセルへ集める
    flats, poss = [], []
    for axis, (idx, pos, _) in enumerate(edges):
        b0, b1 = (axis + 1) % 3, (axis + 2) % 3
        for d0 in (0, 1):
            for d1 in (0, 1):
                cell = idx.copy()
                cell[:, b0] -= d0
                cell[:, b1] -= d1
                ok = np.all((cell >= 0) & (cell < shape), axis=1)
                flats.append(np.ravel_multi_index(cell[ok].T, shape))
                poss.append(pos[ok])
    flats = np.concatenate(flats)
    poss = np.concatenate(poss)
    cells, inverse = np.unique(flats, return_inverse=True)
    count = np.bincount(inverse).astype(np.float64)
    verts = np.stack([np.bincount(inverse, weights=poss[:, c]) for c in range(3)], axis=1) / count[:, None]
    verts = (verts * pitch + np.array(origin, np.float64)).astype(np.float32)
    quads = []
    for axis, (idx, _, from_inside) in enumerate(edges):
        b0, b1 = (axis + 1) % 3, (axis + 2) % 3
        corners = []
        for d0, d1 in ((1, 1), (0, 1), (0, 0), (1, 0)):
            cell = idx.copy()
            cell[:, b0] -= d0
            cell[:, b1] -= d1
            corners.append(cell)
        ok = np.ones(len(idx), bool)
        for cell in corners:
            ok &= np.all((cell >= 0) & (cell < shape), axis=1)
        ids = np.stack([np.searchsorted(cells, np.ravel_multi_index(c[ok].T, shape)) for c in corners], axis=1)
        flip = ~from_inside[ok]
        ids[flip] = ids[flip][:, ::-1]
        quads.append(ids)
    return verts, np.concatenate(quads)


def taubin(verts, quads, iterations, lam=0.5, mu=-0.53):
    edges = np.concatenate([quads[:, [0, 1]], quads[:, [1, 2]], quads[:, [2, 3]], quads[:, [3, 0]]])
    edges = np.unique(np.sort(edges, axis=1), axis=0)
    a = np.concatenate([edges[:, 0], edges[:, 1]])
    b = np.concatenate([edges[:, 1], edges[:, 0]])
    count = np.bincount(a, minlength=len(verts)).astype(np.float32)
    v = verts.copy()
    for step in range(iterations * 2):
        acc = np.zeros_like(v)
        np.add.at(acc, a, v[b])
        mean = acc / np.maximum(count, 1)[:, None]
        v += (lam if step % 2 == 0 else mu) * (mean - v)
    return v


def mesh_object(name, verts_mm, quads):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata((verts_mm / 1000.0).tolist(), [], quads.tolist())
    mesh.validate(verbose=True)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = True
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def main():
    clear_scene()
    x, y, z = build_grid()
    field = build_field(x, y, z).astype(np.float32)
    verts, quads = surface_nets(field, (x[0], y[0], z[0]), mm(GRID))
    print(f"raw mesh: {len(verts)} verts, {len(quads)} quads")
    verts = taubin(verts, quads, SMOOTH_ITERATIONS)
    verts[:, 2] = np.maximum(verts[:, 2], 0.0)  # 平滑化で底が沈んだ分を接地面へ戻す
    verts *= SIZE_FACTOR
    unit_a = mesh_object("leg_left", verts + np.array([-mm(PAIR_SPACING) / 2, 0, 0], np.float32), quads)
    unit_b = mesh_object("leg_right", verts + np.array([mm(PAIR_SPACING) / 2, 0, 0], np.float32), quads)
    bpy.context.view_layer.update()
    low = verts.min(axis=0)
    high = verts.max(axis=0)
    print(f"unit size mm: X {high[0]-low[0]:.1f}  Y {high[1]-low[1]:.1f}  Z {high[2]-low[2]:.1f}")
    export_stl(MODEL_NAME)
    leg = mesh_object("leg", verts, quads)
    export_stl(MODEL_NAME + "-unit", only=[leg])


main()
