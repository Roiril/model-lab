"""STL 単体の検査（numpy のみ。Blender 不要）。単位は mm。

- 位相: 全辺がちょうど 2 面に共有され、向きがそろい（有向辺が 1 回ずつ）、面積 0 の三角形が無い
- 連結成分の数
- 体積・重心（四面体分解）
- 刷る向きの STL の接地: 最下面の面積、各連結成分がベッドに触れるか、高さ / 接地の短辺
"""
from __future__ import annotations

import struct
from pathlib import Path

import numpy as np

from . import limits as L


def read_stl(path):
    raw = Path(path).read_bytes()
    if len(raw) < 84:
        raise ValueError(f"STL が短すぎる: {path}")
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + 50 * count:
        raise ValueError(f"binary STL のバイト数が合わない（ASCII STL は未対応）: {path}")
    dtype = np.dtype([("normal", "<f4", 3), ("vertex", "<f4", (3, 3)), ("attr", "<u2")])
    return np.frombuffer(raw, dtype=dtype, offset=84, count=count)["vertex"].astype(float)


def index_mesh(tris):
    flat = tris.reshape(-1, 3)
    verts, inverse = np.unique(flat, axis=0, return_inverse=True)
    return verts, inverse.reshape(-1, 3)


def topology(tris):
    """閉じた向きのそろった 2 多様体か。戻りは数値の dict"""
    if len(tris) == 0:
        return {"pass": False, "triangles": 0, "reason": "三角形が 0 個"}
    verts, faces = index_mesh(tris)
    twice_area = np.linalg.norm(np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]), axis=1)
    degenerate = int(np.count_nonzero(twice_area <= 1e-12))
    directed = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    undirected = np.sort(directed, axis=1)
    _, counts = np.unique(undirected, axis=0, return_counts=True)
    not_two = int(np.count_nonzero(counts != 2))
    _, directed_counts = np.unique(directed, axis=0, return_counts=True)
    repeated_directed = int(np.count_nonzero(directed_counts > 1))
    volume = signed_volume(tris)
    row = {
        "triangles": int(len(tris)),
        "vertices": int(len(verts)),
        "edgesNotSharedByTwo": not_two,
        "edgesWithSameDirectionTwice": repeated_directed,
        "degenerateTriangles": degenerate,
        "signedVolumeMm3": round(volume, 4),
    }
    row["pass"] = not_two == 0 and repeated_directed == 0 and degenerate == 0 and volume > 0
    return row


def components(tris):
    """頂点を共有する三角形のつながりで数えた連結成分。戻りは成分ごとの三角形番号の配列"""
    _, faces = index_mesh(tris)
    parent = np.arange(faces.max() + 1)

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    for a, b, c in faces:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[find(rc)] = ra
    roots = np.array([find(f[0]) for f in faces])
    return [np.nonzero(roots == r)[0] for r in np.unique(roots)]


def signed_volume(tris):
    return float(np.einsum("ij,ij->i", tris[:, 0], np.cross(tris[:, 1], tris[:, 2])).sum() / 6.0)


def mass_properties(tris):
    """体積（mm3）と重心（mm）。閉じたメッシュ前提"""
    six = np.einsum("ij,ij->i", tris[:, 0], np.cross(tris[:, 1], tris[:, 2]))
    volume = six.sum() / 6.0
    if abs(volume) < 1e-12:
        return 0.0, tris.reshape(-1, 3).mean(axis=0)
    centroid = (six[:, None] * tris.sum(axis=1)).sum(axis=0) / (4.0 * six.sum())
    return float(volume), centroid


def grounding(tris):
    """刷る向きの STL（Z が上）の接地。ベッドは最下点の高さ"""
    z0 = float(tris[:, :, 2].min())
    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    lengths[lengths == 0] = 1.0
    nz = normals[:, 2] / lengths
    on_bed = np.all(np.abs(tris[:, :, 2] - z0) <= L.GROUND_TOL_MM, axis=1) & (nz < -0.999)
    contact_area = float((lengths[on_bed] / 2.0).sum())
    floating = []
    for index, comp in enumerate(components(tris)):
        bottom = float(tris[comp][:, :, 2].min())
        if bottom - z0 > L.GROUND_TOL_MM:
            floating.append({"component": index, "bottomAboveBedMm": round(bottom - z0, 4)})
    height = float(tris[:, :, 2].max() - z0)
    if on_bed.any():
        pts = tris[on_bed].reshape(-1, 3)[:, :2]
        short_side = float(min(np.ptp(pts[:, 0]), np.ptp(pts[:, 1])))
    else:
        short_side = 0.0
    slender = height / short_side if short_side > 0 else float("inf")
    return {
        "bedZ": round(z0, 4),
        "contactAreaMm2": round(contact_area, 3),
        "floatingComponents": floating,
        "heightMm": round(height, 3),
        "contactShortSideMm": round(short_side, 3),
        "heightOverShortSide": round(slender, 3) if slender != float("inf") else None,
    }


def bounds(tris):
    return tris.reshape(-1, 3).min(axis=0), tris.reshape(-1, 3).max(axis=0)
