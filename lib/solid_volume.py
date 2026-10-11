"""Boolean 共通境界の体積。単位は入力と同じ（検証では mm）。"""
from __future__ import annotations

import math
import numpy as np

PLANAR_RMS_TOL_MM = 0.00001


def triangle_twice_area(points):
    """STLの実座標を倍精度で読む。極小の正面積と零面積を分ける。"""
    a, b, c = np.asarray(points, dtype=float)
    return float(np.linalg.norm(np.cross(b - a, c - a)))


def triangle_area_calibration():
    normal = triangle_twice_area(((0, 0, 0), (1, 0, 0), (0, 1, 0)))
    zero = triangle_twice_area(((0, 0, 0), (1, 0, 0), (2, 0, 0)))
    small = triangle_twice_area(((0, 0, 0), (.001, 0, 0), (0, 1e-8, 0)))
    return {'pass': normal == 1 and zero == 0 and small > 0,
            'normalTwiceAreaMm2': normal, 'zeroTwiceAreaMm2': zero,
            'smallPositiveTwiceAreaMm2': small, 'smallExpectedTwiceAreaMm2': 1e-11}


def closed_boundary_volume(bm):
    """閉境界を積分する。開いた平面接触だけを零体積として扱う。

    開いた非平面境界は有効な立体ではないので計算を中止する。
    外周と空洞内周の符号を保持する。原点から離れた平面に
    calc_volume を直接呼ぶと擬似体積が出るため、それを使わない。
    """
    remaining = set(bm.verts)
    signed_parts = []
    while remaining:
        seed = remaining.pop()
        vertices, pending = [seed], [seed]
        while pending:
            vertex = pending.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in remaining:
                    remaining.remove(other)
                    vertices.append(other)
                    pending.append(other)
        faces = {face for vertex in vertices for face in vertex.link_faces}
        if not faces:
            continue
        points = np.asarray([tuple(vertex.co) for vertex in vertices], dtype=float)
        center = points.mean(axis=0)
        edges = {edge for face in faces for edge in face.edges}
        if any(not edge.is_manifold for edge in edges):
            singular = np.linalg.svd(points - center, compute_uv=False)
            smallest_rms = singular[-1] / math.sqrt(len(points)) if len(singular) == 3 else 0.0
            if smallest_rms <= PLANAR_RMS_TOL_MM:
                continue
            raise ValueError(f'Open nonplanar Boolean boundary: {len(vertices)} vertices; minimum RMS width {smallest_rms:.9f} mm')
        signed6 = []
        for face in faces:
            polygon = [np.asarray(tuple(vertex.co), dtype=float) - center for vertex in face.verts]
            for index in range(1, len(polygon) - 1):
                signed6.append(float(np.dot(polygon[0], np.cross(polygon[index], polygon[index + 1]))))
        signed_parts.append(math.fsum(signed6) / 6)
    return abs(math.fsum(signed_parts))
