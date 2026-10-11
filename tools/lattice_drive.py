"""実 STL の断面と接触から C3/C4 の駆動接続を検査する。

Blender --background --python tools/lattice_drive.py -- <model>。
動作の行列を与えるだけでは伝達を証明しない。相対回転の接触と
軸方向の保持を独立に測る。SG92R 正本にないスプラインは unknown。
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TOL_MM = 0.002  # 断面の接触距離。STL float32 と三角化の校正後の固定値。


def read_stl(path):
    raw = Path(path).read_bytes()
    count = struct.unpack_from('<I', raw, 80)[0]
    if len(raw) != 84 + count * 50:
        raise ValueError(f'Invalid binary STL: {path}')
    dtype = np.dtype([('normal', '<f4', 3), ('vertex', '<f4', (3, 3)), ('attr', '<u2')])
    return np.frombuffer(raw, dtype=dtype, offset=84, count=count)['vertex'].astype(float)


def slice_x(triangles, x):
    """面に重ならない X 断面。穴も含めた全境界を返す。"""
    rows = []
    for tri in triangles:
        if not (tri[:, 0].min() < x < tri[:, 0].max()):
            continue
        points = []
        for a, b in zip(tri, np.roll(tri, -1, axis=0)):
            if (a[0] <= x < b[0]) or (b[0] <= x < a[0]):
                point = (a + (b - a) * ((x - a[0]) / (b[0] - a[0])))[1:]
                if not any(np.linalg.norm(point - other) < 1e-7 for other in points):
                    points.append(point)
        if len(points) == 2 and np.linalg.norm(points[1] - points[0]) > 1e-7:
            rows.append(points)
    return np.asarray(rows, dtype=float).reshape((-1, 2, 2))


def rotate(segments, deg, center):
    a = math.radians(deg)
    matrix = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    return (segments - center) @ matrix.T + center


def cross2(a, b):
    return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]


def inside(points, segments):
    if not len(segments):
        return np.zeros(len(points), dtype=bool)
    a, b = segments[:, 0], segments[:, 1]
    p = np.asarray(points)[:, None, :]
    denominator = b[:, 1] - a[:, 1]
    safe = np.where(abs(denominator) > 1e-12, denominator, 1e-12)
    hit_x = a[:, 0] + (p[..., 1] - a[:, 1]) * (b[:, 0] - a[:, 0]) / safe
    crossings = ((a[:, 1] > p[..., 1]) != (b[:, 1] > p[..., 1])) & (hit_x > p[..., 0])
    return np.count_nonzero(crossings, axis=1) % 2 == 1


def intersects(a, b, containment=True):
    if not len(a) or not len(b):
        return False
    aa, ar = a[:, None, 0], (a[:, 1] - a[:, 0])[:, None]
    bb, br = b[None, :, 0], (b[:, 1] - b[:, 0])[None, :]
    denominator = cross2(ar, br)
    safe = np.where(abs(denominator) > 1e-10, denominator, 1.0)
    t, u = cross2(bb - aa, br) / safe, cross2(bb - aa, ar) / safe
    crossing = ((abs(denominator) > 1e-10) & (t > 1e-7) & (t < 1 - 1e-7)
                & (u > 1e-7) & (u < 1 - 1e-7))
    if np.any(crossing):
        return True
    if containment:
        return bool(np.any(inside(a.mean(axis=1), b)) or np.any(inside(b.mean(axis=1), a)))
    return False


def distance(a, b):
    if not len(a) or not len(b):
        return float('inf')
    if intersects(a, b, containment=False):
        return 0.0

    def one(points, edges):
        p = points[:, None, :]
        start, vector = edges[None, :, 0], (edges[:, 1] - edges[:, 0])[None]
        length2 = np.sum(vector * vector, axis=-1)
        t = np.clip(np.sum((p - start) * vector, axis=-1) / np.maximum(length2, 1e-20), 0, 1)
        return float(np.sqrt(np.min(np.sum((p - start - t[..., None] * vector) ** 2, axis=-1))))
    return min(one(a.reshape(-1, 2), b), one(b.reshape(-1, 2), a))


def contact_angle(male, female, center, sign, limit=15.0, containment=True, filter_box=None):
    def collision(deg):
        moving = rotate(male, sign * deg, center)
        fixed = female
        if filter_box is not None:
            lo, hi = np.array(filter_box[0]), np.array(filter_box[1])
            moving = moving[np.all(moving.max(axis=1) >= lo, axis=1) & np.all(moving.min(axis=1) <= hi, axis=1)]
            fixed = fixed[np.all(fixed.max(axis=1) >= lo, axis=1) & np.all(fixed.min(axis=1) <= hi, axis=1)]
        return intersects(moving, fixed, containment=containment)
    if collision(0):
        return None
    previous = 0.0
    for candidate in np.arange(0.5, limit + 0.5, 0.5):
        if collision(float(candidate)):
            lo, hi = previous, float(candidate)
            for _ in range(18):
                middle = (lo + hi) / 2
                if collision(middle):
                    hi = middle
                else:
                    lo = middle
            return (lo + hi) / 2
        previous = float(candidate)
    return None


def interface_rotation(male, female, x, center, label, identifier, max_angle=15):
    a, b = slice_x(male, x), slice_x(female, x)
    angles = [contact_angle(a, b, center, sign, max_angle) for sign in (-1, 1)]
    zero = intersects(a, b)
    gap = distance(a, b)
    valid = not zero and len(a) > 0 and len(b) > 0 and all(value is not None for value in angles)
    return {'id': identifier, 'label': label, 'status': 'pass' if valid else 'fail',
            'sliceXmm': round(x, 5), 'boundarySegments': [len(a), len(b)],
            'nominalInterference': zero, 'nearestGapMm': round(gap, 6) if math.isfinite(gap) else None,
            'contactAnglesDeg': [round(value, 6) if value is not None else None for value in angles],
            'totalAngularPlayDeg': round(sum(angles), 6) if valid else None,
            'method': 'STL plane intersection; rotate male independently until actual boundary contact'}


def polygon_edges(points):
    p = np.array(points, dtype=float)
    return np.stack((p, np.roll(p, -1, axis=0)), axis=1)


def calibration():
    square = polygon_edges([(-1, -1), (1, -1), (1, 1), (-1, 1)])
    larger = polygon_edges([(-1.2, -1.2), (1.2, -1.2), (1.2, 1.2), (-1.2, 1.2)])
    # 雌形状は外周と内周を持つ。大きな外周で material の偶奇を正しく作る。
    outside = polygon_edges([(-3, -3), (3, -3), (3, 3), (-3, 3)])
    socket = np.concatenate((larger, outside))
    circle = polygon_edges([(1.5 * math.cos(i * 2 * math.pi / 180),
                             1.5 * math.sin(i * 2 * math.pi / 180)) for i in range(180)])
    round_socket = np.concatenate((circle, outside))
    angle = contact_angle(square, socket, (0, 0), 1, 30)
    expected = math.degrees(math.asin(1.2 / math.sqrt(2))) - 45
    rows = [
        {'id': 'known-gap', 'label': '既知の断面隙間', 'pass': abs(distance(square, larger) - .2) < 1e-7,
         'detail': f'測定 {distance(square, larger):.6f} mm。期待 0.200000 mm。'},
        {'id': 'key-contact', 'label': '回転止めの正例', 'pass': angle is not None and abs(angle - expected) < 1e-4,
         'detail': f'測定 {angle} deg。解析 {expected:.6f} deg。'},
        {'id': 'round-hole', 'label': '真円穴の負例', 'pass': contact_angle(square, round_socket, (0, 0), 1, 180) is None,
         'detail': '同じ計器で180度回しても接触しない。回転伝達不成立。'},
        {'id': 'missing-shape', 'label': '欠落形状の負例', 'pass': contact_angle(np.empty((0, 2, 2)), socket, (0, 0), 1) is None,
         'detail': '雄形状を削除すると接触不成立。'},
    ]
    return rows


def gear_report(meshes, P):
    x = P.GEAR_X * 1000
    a, b = slice_x(meshes['drive_gear'], x), slice_x(meshes['cam_gear'], x)
    center1, center2 = np.array([0, P.SERVO_AXIS_Z * 1000]), np.array([0, P.CAM_AXIS_Z * 1000])
    module, rp = P.GEAR_MODULE * 1000, P.GEAR_MODULE * P.GEAR_TEETH * 500
    ra, rb, rf = rp + module, rp * math.cos(math.radians(P.GEAR_PRESSURE_DEG)), rp - 1.25 * module
    actual_r = []
    for edges, center in ((a, center1), (b, center2)):
        radii = np.linalg.norm(edges.reshape(-1, 2) - center, axis=1) if len(edges) else np.array([])
        actual_r.append(float(max(radii)) if len(radii) else 0.0)
    def tooth_width(triangles, center, phase):
        if not len(triangles):
            return None
        points = triangles.reshape(-1, 3)
        radial = points[:, 1:] - center
        keep = abs(np.linalg.norm(radial, axis=1) - ra) <= .001
        points, radial = points[keep], radial[keep]
        groups = np.mod(np.rint((np.degrees(np.arctan2(radial[:, 1], radial[:, 0])) - phase)
                                 / (360 / P.GEAR_TEETH)).astype(int), P.GEAR_TEETH)
        if any(not np.any(groups == i) for i in range(P.GEAR_TEETH)):
            return None
        # 中心ハブと長腕の張出しを歯幅へ数えない。30歯すべてがある区間を要求する。
        return [max(float(points[groups == i, 0].min()) for i in range(P.GEAR_TEETH)),
                min(float(points[groups == i, 0].max()) for i in range(P.GEAR_TEETH))]
    widths = [tooth_width(meshes['drive_gear'], center1, 90), tooth_width(meshes['cam_gear'], center2, 276)]
    width = max(0, min(w[1] for w in widths) - max(w[0] for w in widths)) if all(w is not None for w in widths) else 0.0
    box = ((-10, center2[1] - ra - .1), (10, center1[1] + ra + .1))
    samples = []
    delta_end = P.SERVO_END_DEG - P.SERVO_HOME_DEG
    for delta in np.linspace(0, delta_end, int(math.ceil(delta_end / 2.5)) + 1):
        driver, follower = rotate(a, -delta, center1), rotate(b, delta, center2)
        contact = [contact_angle(follower, driver, center2, sign, 3.0,
                                containment=False, filter_box=box) for sign in (-1, 1)]
        samples.append({'servoDeg': round(P.SERVO_HOME_DEG + delta, 5),
                        'contactAnglesDeg': [round(v, 6) if v is not None else None for v in contact]})
    distance_centers = float(np.linalg.norm(center2 - center1))
    alpha_work = math.acos(2 * rb / distance_centers)
    ratio = (2 * math.sqrt(ra * ra - rb * rb) - distance_centers * math.sin(alpha_work)) / (
        math.pi * module * math.cos(math.radians(P.GEAR_PRESSURE_DEG)))
    def counts(edges, center):
        if not len(edges):
            return 0
        # 歯先の弧にある境界を角度帯へまとめる。歯数は STL の実歯先から数える。
        points = edges.reshape(-1, 2) - center
        points = points[np.linalg.norm(points, axis=1) > ra - .01]
        if not len(points):
            return 0
        angles = np.sort(np.mod(np.arctan2(points[:, 1], points[:, 0]), 2 * math.pi))
        gaps = np.diff(np.append(angles, angles[0] + 2 * math.pi))
        return int(np.count_nonzero(gaps > math.radians(3)))
    teeth = [counts(a, center1), counts(b, center2)]
    valid = (len(a) > 0 and len(b) > 0 and min(actual_r) >= ra - .01 and teeth == [P.GEAR_TEETH] * 2
             and width >= P.GEAR_THICK * 1000 - .01 and ratio > 1.2
             and all(all(v is not None and v <= 1.5 for v in row['contactAnglesDeg']) for row in samples))
    return {'id': 'gear-mesh', 'label': '駆動歯車と従動歯車', 'status': 'pass' if valid else 'fail',
            'actualTeeth': teeth, 'actualTipRadiusMm': [round(v, 5) for v in actual_r],
            'faceWidthOverlapMm': round(width, 5), 'toothRangesXmm': widths, 'centerDistanceMm': distance_centers,
            'workingPressureAngleDeg': round(math.degrees(alpha_work), 5),
            'contactRatio': round(ratio, 5), 'samples': samples,
            'maximumTotalAngularPlayDeg': round(max(sum(r['contactAnglesDeg']) for r in samples), 6)
             if all(all(v is not None for v in r['contactAnglesDeg']) for r in samples) else None,
            'source': 'https://khkgears.net/gear-knowledge/gear-technical-reference/calculation-gear-dimensions/',
            'method': 'actual STL tooth boundary; follower independent contact in both load directions; working pitch geometry'}


def transform_triangles(triangles, angle=0.0, center=(0, 0), offset=(0, 0, 0)):
    result = triangles.copy()
    result[:, :, 1:] = rotate(result[:, :, 1:], angle, np.array(center))
    return result + np.array(offset)


def relative_pose_key(angle_a, pivot_a, offset_a, angle_b, pivot_b):
    """相対配置を倍精度で作る。共通回転で単精度の移動誤差を増やさない。"""
    def placed(angle, pivot, shift):
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        rotation = np.array(((1., 0., 0.), (0., c, -s), (0., s, c)))
        center = np.array((0., *pivot))
        result = np.eye(4)
        result[:3, :3] = rotation
        result[:3, 3] = center - rotation @ center + np.asarray(shift)
        return result
    relative = np.linalg.solve(placed(angle_a, pivot_a, offset_a), placed(angle_b, pivot_b, (0, 0, 0)))
    return tuple(np.round(relative.reshape(-1), 6))


def follower_report(meshes, P, is_c3, dz_fault=0.0):
    low, high = ((P.SERVO_HOME_DEG, P.SERVO_END_DEG) if is_c3 else (P.SERVO_MIN_DEG, P.SERVO_MAX_DEG))
    axis_z = (P.CAM_AXIS_Z * 1000)
    names = [(f'cam_{i}', f'carrier_{i}') for i in range(P.GRID_N)] if is_c3 else list(zip(
        ('cam_center', 'cam_inner', 'cam_outer'), ('carrier_center', 'carrier_inner', 'carrier_outer')))
    rows = []
    for servo in np.linspace(low, high, int(math.ceil((high - low) / 2.5)) + 1):
        delta = servo - low
        for i, (cam, carrier) in enumerate(names):
            x = (i - 2) * P.PITCH * 1000 if is_c3 else P.CAM_X[i] * 1000
            cam_edges = rotate(slice_x(meshes[cam], x), delta, np.array([0, axis_z]))
            cam_points = cam_edges.reshape(-1, 2)
            top = cam_points[np.argmax(cam_points[:, 1])]
            if is_c3:
                theta = math.radians(P.CAM_HOME_DEG + delta - P.CAM_PHASE_DEG[i])
                lift = max(0, (P.CAM_R + P.CAM_E * math.cos(theta) + P.CAM_AXIS_Z - P.FOLLOWER_STOP_Z) * 1000)
                active = lift > 1e-6
            else:
                theta = math.radians(P.CAM_THETA_MIN_DEG + delta)
                lift = P.CAM_E[i] * (math.sin(theta) - math.sin(math.radians(P.CAM_THETA_MIN_DEG))) * 1000
                active = True
            carrier_edges = slice_x(meshes[carrier], x) + np.array([0, lift + dz_fault])
            # 接点の鉛直線と従動部の実境界を交差させる。舌と柱の下面は接点と異なる。
            levels = []
            for a, b in carrier_edges:
                if min(a[0], b[0]) - 1e-5 <= top[0] <= max(a[0], b[0]) + 1e-5:
                    if abs(b[0] - a[0]) > 1e-8:
                        level = a[1] + (top[0] - a[0]) * (b[1] - a[1]) / (b[0] - a[0])
                        if level > axis_z + (6 if is_c3 else 0):
                            levels.append(level)
            bottom = min(levels) if levels else None
            gap = bottom - top[1] if bottom is not None else None
            good = gap is not None and (not active or -TOL_MM <= gap <= .012)
            rows.append({'servoDeg': round(float(servo), 5), 'group': i,
                         'contactYmm': round(float(top[0]), 6), 'camTopZmm': round(float(top[1]), 6),
                         'followerBottomZmm': round(float(bottom), 6) if bottom is not None else None,
                         'gapMm': round(float(gap), 6) if gap is not None else None,
                         'active': active, 'pass': good})
    active = [row for row in rows if row['active']]
    return {'id': 'cam-followers', 'label': 'カムと格子の従動面',
            'status': 'pass' if active and all(row['pass'] for row in rows) else 'fail',
            'gapLimitMm': .012, 'penetrationLimitMm': TOL_MM,
            'polygonChordErrorBoundMm': round((P.CAM_R * 1000) * (1 - math.cos(math.pi / (72 if is_c3 else 96))), 6),
            'maximumActiveGapMm': max((row['gapMm'] for row in active if row['gapMm'] is not None), default=None),
            'samples': rows, 'method': 'actual STL cam maximum and follower vertical intersection at each pose'}


def unique_surface_area(triangles):
    """重複面を除いた STL 表面積。頂点が残る面欠落も検出する。"""
    vertices = triangles
    order = np.lexsort((vertices[:, :, 2], vertices[:, :, 1], vertices[:, :, 0]), axis=1)
    faces = np.unique(np.take_along_axis(vertices, order[:, :, None], axis=1).reshape(-1, 9), axis=0).reshape(-1, 3, 3)
    return float(np.linalg.norm(np.cross(faces[:, 1] - faces[:, 0], faces[:, 2] - faces[:, 0]), axis=1).sum() / 2)


def surface_distance(first, second):
    """全頂点・全重心から相手の面への距離。細い面も float64 で測る。"""
    def directed(points, target):
        triangles = np.asarray(target, dtype=np.float64)
        a, b, c = triangles[:, 0], triangles[:, 1], triangles[:, 2]
        normals = np.cross(b - a, c - a)
        normal_sq = np.einsum('ij,ij->i', normals, normals)
        valid = normal_sq > 0
        a, b, c, normals, normal_sq = (value[valid] for value in (a, b, c, normals, normal_sq))
        if not len(a):
            raise ValueError('surface distance target has no positive-area triangles')
        maximum_sq = 0.
        # BVH の単精度最近傍は極細面で同一表面にも偽の距離を返す。
        # 各面の射影と三辺を直接比較し、近い候補を落とさない。
        for start in range(0, len(points), 32):
            points_chunk = np.asarray(points[start:start + 32], dtype=np.float64)
            offset = points_chunk[:, None, :] - a[None, :, :]
            dot = np.einsum('pti,ti->pt', offset, normals)
            projected = points_chunk[:, None, :] - (dot / normal_sq)[..., None] * normals
            inside = np.ones(dot.shape, dtype=bool)
            edge_sq = np.full(dot.shape, np.inf)
            for begin, end in ((a, b), (b, c), (c, a)):
                edge = end - begin
                side = np.einsum('pti,ti->pt', np.cross(edge, projected - begin), normals)
                inside &= side >= -1e-12 * normal_sq
                length_sq = np.einsum('ti,ti->t', edge, edge)
                fraction = np.clip(np.einsum('pti,ti->pt', points_chunk[:, None, :] - begin, edge) / length_sq, 0, 1)
                residual = points_chunk[:, None, :] - begin - fraction[..., None] * edge
                edge_sq = np.minimum(edge_sq, np.einsum('pti,pti->pt', residual, residual))
            distance_sq = np.minimum(edge_sq, np.where(inside, dot * dot / normal_sq, np.inf))
            maximum_sq = max(maximum_sq, float(np.min(distance_sq, axis=1).max()))
        return math.sqrt(maximum_sq)
    samples = lambda triangles: np.unique(np.concatenate((triangles.reshape(-1, 3), triangles.mean(axis=1))), axis=0)
    return max(directed(samples(first), second), directed(samples(second), first))


def canonical_surface_calibration():
    source = cube_triangles()
    face = source[0]
    midpoint = (face[0] + face[1]) / 2
    divided = np.concatenate((np.array([[face[0], midpoint, face[2]], [midpoint, face[1], face[2]]]), source[1:]))
    identical = surface_distance(source, divided)
    missing = surface_distance(source, source[1:])
    shifted = surface_distance(source, source + np.array([.5, 0, 0]))
    area_error = abs(unique_surface_area(source) - unique_surface_area(divided))
    skinny = np.array([[[40., 17., 63.], [41., 17., 63.], [40.1, 17.0000001, 63.]]])
    skinny_same = surface_distance(skinny, skinny.copy())
    skinny_shift = surface_distance(skinny, skinny + np.array([0, 0, .02]))
    return {'id': 'canonical-surface', 'label': '再三角化と面欠落を区別する計器',
        'pass': identical <= .00001 and area_error <= .00001 and missing > .1 and shifted > .49
                and skinny_same <= 1e-10 and skinny_shift > .01999,
        'detail': {'sameSurfaceRetriangulatedDistanceMm': identical, 'sameSurfaceAreaDifferenceMm2': area_error,
                   'missingFaceDistanceMm': missing, 'shiftedSurfaceDistanceMm': shifted,
                   'skinnyIdenticalDistanceMm': skinny_same, 'skinnyShiftedDistanceMm': skinny_shift}}


def canonical_report(meshes, P, is_c3):
    rows = []
    for suffix, name in (('body', 'ref_servo' if is_c3 else 'servo_body'),
                         ('horn', 'ref_horn' if is_c3 else 'servo_horn'),
                         ('wire', 'ref_wire' if is_c3 else 'servo_wire')):
        source = read_stl(ROOT / 'exports' / f'sg92r-photo-{suffix}.stl')
        expected = source[:, :, [2, 0, 1]].copy()
        expected += np.array([-(P.SG.SHAFT_BOTTOM_Z + P.SG.SHAFT_H) * 1000 if is_c3 else P.SERVO_X0 * 1000,
                              0 if is_c3 else P.SERVO_Y_OFFSET * 1000,
                              P.SERVO_AXIS_Z * 1000 if is_c3 else P.SERVO_Z * 1000])
        if suffix == 'horn' and not is_c3:
            expected = transform_triangles(expected, P.HORN_HOME_DEG, (0, P.CAM_AXIS_Z * 1000))
        a = np.unique(np.round(expected.reshape(-1, 3), 3), axis=0)
        b = np.unique(np.round(meshes[name].reshape(-1, 3), 3), axis=0)
        # 全頂点を両方向に比較し、同じ頂点を使う面の欠落は表面積でも調べる。
        def hausdorff(first, second):
            maxima = []
            for chunk in np.array_split(first, max(1, int(math.ceil(len(first) / 128)))):
                maxima.append(float(np.sqrt(np.max(np.min(np.sum((chunk[:, None] - second[None]) ** 2, axis=-1), axis=1)))))
            return max(maxima)
        error = max(hausdorff(a, b), hausdorff(b, a))
        surface_error = surface_distance(expected, meshes[name])
        expected_area = unique_surface_area(expected)
        actual_area = unique_surface_area(meshes[name])
        area_error = abs(expected_area - actual_area)
        rows.append({'part': name, 'maximumVertexDifferenceMm': round(error, 6),
                     'maximumSurfaceDifferenceMm': surface_error,
                     'expectedSurfaceAreaMm2': round(expected_area, 6), 'actualSurfaceAreaMm2': round(actual_area, 6),
                     'surfaceAreaDifferenceMm2': round(area_error, 6),
                     'pass': surface_error <= .003 and area_error <= .003})
    return {'id': 'canonical-reference', 'label': '正本サーボとホーンと配線の実形状',
            'status': 'pass' if all(row['pass'] for row in rows) else 'fail', 'parts': rows,
            'method': 'raw STL vertices and all triangle centroids to opposing triangle surface in both directions; total unique surface area. Vertex-set distance is informational for retriangulation.'}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('model', choices=['mystery-box-sg92r-c3', 'mystery-box-sg92r-c4'])
    parsed = parser.parse_args(args)
    folder = ROOT / 'models' / parsed.model
    manifest = json.loads((folder / 'build/manifest.json').read_text(encoding='utf-8'))
    sources = [folder / part['assembly'] for part in manifest['parts'] if not part.get('fit_only')]
    sources += [folder / 'params.py', folder / 'model.py', folder / 'motion.py',
                folder / 'build/manifest.json', Path(__file__), ROOT / 'models/sg92r-photo/params.py',
                ROOT / 'lib/solid_volume.py', ROOT / 'tools/lattice_boolean_evidence.py',
                folder / 'build/boolean_evidence.json']
    sources += [ROOT / 'exports' / f'sg92r-photo-{suffix}.stl' for suffix in ('body', 'horn', 'wire')]
    if parsed.model.endswith('c3'):
        sources.append(ROOT / 'tools/fixtures/lattice-drive/c3-missing-teeth.stl')
    def source_hashes():
        return {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
    hashes = source_hashes()
    evidence = json.loads((folder / 'build/boolean_evidence.json').read_text(encoding='utf-8'))
    evidence_rows = evidence['assemblyStls'] + evidence['printStls'] + evidence['deliveredPrintStls']
    expected_assembly = {(folder / part['assembly']).relative_to(ROOT).as_posix() for part in manifest['parts']}
    if expected_assembly != {row['path'] for row in evidence['assemblyStls']}:
        raise ValueError('Boolean evidence does not cover current assembly parts')
    evidence_fresh = all(row.get('exists') and row.get('geometryValidClosedSolid') and
        hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
        for row in evidence_rows)
    algorithm_fresh = all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == sha
        for path, sha in evidence.get('algorithmSha256', {}).items())
    if not evidence_rows or not evidence_fresh or not algorithm_fresh or not evidence.get('algorithmSha256') or not all(
            row['pass'] for row in evidence['calibration']):
        raise ValueError('Boolean input geometry evidence is missing, invalid or stale')
    spec = importlib.util.spec_from_file_location('drive_params', folder / 'params.py')
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    meshes = {part['id']: read_stl(folder / part['assembly']) for part in manifest['parts'] if not part.get('fit_only')}
    cal = calibration()
    cal.append(canonical_surface_calibration())
    cal.append({'id': 'solid-input-geometry', 'label': '閉じた入力と自己交差の検査', 'pass': True,
                'detail': evidence['summary']})
    if parsed.model.endswith('c3'):
        probe = evidence['shaftCapProbe']
        lower = probe['independentSection']['volumeLowerBoundMm3']
        measured = probe['solvers']
        probe_pass = lower > 0 and all(row['nonmanifoldEdges'] == 0 and row['error'] is None and
            row['closedBoundaryVolumeMm3'] >= lower for row in measured.values()) and abs(
            measured['EXACT']['closedBoundaryVolumeMm3'] - measured['MANIFOLD']['closedBoundaryVolumeMm3']) < .0001
        cal.append({'id': 'shaft-cap-positive-volume', 'label': '保持面の解析下限と二つの体積計器',
                    'pass': probe_pass, 'detail': probe})
    print(json.dumps({'drivePhase': 'rotational-interfaces', 'model': parsed.model}), flush=True)
    interfaces = []
    is_c3 = parsed.model.endswith('c3')
    horn = 'ref_horn' if is_c3 else 'servo_horn'
    receiver = 'drive_gear' if is_c3 else 'horn_coupler'
    center = (0, (P.SERVO_AXIS_Z if is_c3 else P.CAM_AXIS_Z) * 1000)
    horn_x = .75 if is_c3 else (P.SERVO_X0 + P.SG.HORN_ARM_BOTTOM_Z + P.SG.HORN_ARM_T / 2) * 1000
    interfaces.append(interface_rotation(meshes[horn], meshes[receiver], horn_x, center,
                                          '付属ホーンと受け', 'horn-receiver'))
    if is_c3:
        interfaces.append(gear_report(meshes, P))
        keyed = ['cam_gear', 'left_spacer'] + [f'cam_{i}' for i in range(P.GRID_N)]
        for name in keyed:
            x = ((meshes[name][:, :, 0].min() + meshes[name][:, :, 0].max()) / 2 if name == 'left_spacer'
                 else P.GEAR_X * 1000 if name == 'cam_gear' else (int(name[-1]) - 2) * P.PITCH * 1000)
            interfaces.append(interface_rotation(meshes['camshaft'], meshes[name], x,
                                                 (0, P.CAM_AXIS_Z * 1000), '六角軸と' + next(
                                                     part['label'] for part in manifest['parts'] if part['id'] == name), 'shaft-' + name))
    else:
        interfaces.append(interface_rotation(meshes['horn_coupler'], meshes['camshaft'],
                                             (P.COUPLER_X1 + P.SHAFT_JOINT_L / 2) * 1000,
                                             center, 'ホーン受けと主軸', 'coupler-shaft'))
        for index, name in enumerate(('cam_center', 'cam_inner', 'cam_outer')):
            interfaces.append(interface_rotation(meshes['camshaft'], meshes[name], P.CAM_X[index] * 1000,
                                                 center, '主軸と' + ('中央カム', '内環カム', '外環カム')[index], 'shaft-' + name))
    interfaces.append({'id': 'servo-spline', 'label': 'SG92R 出力軸と付属ホーン', 'status': 'unknown',
                       'basis': '正本の真円軸とソケットは配置確認用。スプライン歯と実物嵌合を未計測。真円接触からトルク伝達を証明できない。'})
    report = {'version': 1, 'model': parsed.model, 'sourceHashes': hashes, 'calibration': cal,
              'interfaces': interfaces, 'overall': {'geometryPass': False, 'physicalStatus': 'fail',
                 'basis': '回転接触以外の保持と従動接触の検査を実行するまで未成立。'},
              'hardwareUnknown': ['SG92R のスプライン嵌合と軸高さ', '印刷収縮と接触摩擦', '保持具の着脱と荷重試験']}
    # 追加の保持・従動面検査は下に定義する。単独の回転表示は合格根拠にしない。
    extra_checks(report, meshes, P, folder, is_c3)
    source_end = source_hashes()
    report['sourceIntegrity'] = {'pass': hashes == source_end, 'endHashes': source_end}
    geometry_pass = (all(row['status'] == 'pass' for row in report['interfaces'] if row['id'] != 'servo-spline')
                     and all(row['pass'] for row in cal) and hashes == source_end)
    report['overall'] = {'geometryPass': geometry_pass, 'physicalStatus': 'conditional' if geometry_pass else 'fail',
                         'basis': '実 STL の接触と保持を検査。スプライン嵌合と材料は実機未確認。'}
    temporary = folder / 'build/drive_report.json.tmp'
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2,
                                    default=lambda value: value.item() if isinstance(value, np.generic) else str(value)) + '\n',
                         encoding='utf-8', newline='\n')
    os.replace(temporary, folder / 'build/drive_report.json')
    print(json.dumps({'model': parsed.model, 'geometryPass': geometry_pass,
                      'interfaces': [{k: row[k] for k in ('id', 'status')} for row in interfaces]}, ensure_ascii=False))
    if not geometry_pass:
        raise SystemExit(1)


def extra_checks(report, meshes, P, folder, is_c3):
    report['interfaces'].append(canonical_report(meshes, P, is_c3))
    report['interfaces'].append(follower_report(meshes, P, is_c3))
    negative = follower_report(meshes, P, is_c3, dz_fault=.5)
    report['calibration'].append({'id': 'follower-gap', 'label': '従動面を離す負例',
        'pass': negative['status'] == 'fail', 'detail': f"0.5mm離した最大隙間 {negative['maximumActiveGapMm']} mm。接触不成立。"})
    retention_checks(report, meshes, P, is_c3)
    report['interfaces'].append(servo_seat_report(report, meshes, P, is_c3))
    offset_meshes = dict(meshes)
    horn_name = 'ref_horn' if is_c3 else 'servo_horn'
    offset_meshes[horn_name] = meshes[horn_name] + np.array([0, .5, 0])
    offset_seat = servo_seat_report(report, offset_meshes, P, is_c3)
    report['calibration'].append({'id': 'horn-axis-offset', 'label': 'ホーンの軸をずらす負例',
        'pass': offset_seat['status'] == 'fail',
        'detail': f"実ホーンをYへ0.5mm移動。測定中心ずれ {offset_seat['axisOffsetMm']}mm。接続判定 {offset_seat['status']}。"})
    if not is_c3:
        seat = report['interfaces'][-1]
        projection = np.unique(np.round(np.concatenate((meshes['servo_horn'].reshape(-1, 3)[:, 1:],
            meshes['servo_horn'].mean(axis=1)[:, 1:])), 5), axis=0)
        measured = blind_floor_measure(meshes['horn_coupler'], projection,
            seat.get('blindStartXmm'), P.JOINT_COUPLER_GROOVE_X0 * 1000)
        report['interfaces'].append({'id': 'coupler-structure', 'label': 'ホーン受けの連続した盲底',
            'status': 'pass' if measured['pass'] else 'fail', **measured,
            'method': '実STLのX断面3面と全ホーン投影点へのX直線。中実の連続厚を測定。下限1.2mm。'})
        coupon = cube_triangles()
        witnesses = np.array([[.25, .25], [.5, .5], [.75, .75]])
        positive = blind_floor_measure(coupon * np.array([1.25, 1, 1]), witnesses, 0, 1.25)
        negative = blind_floor_measure(coupon * np.array([.15, 1, 1]), witnesses, 0, 1.25)
        report['calibration'].append({'id': 'blind-floor-thickness', 'label': '薄い盲底を落とす負例',
            'pass': positive['pass'] and not negative['pass'],
            'detail': '実厚1.25mmの中実試験片は合格。実厚0.15mmの試験片は不合格。'})
    if is_c3:
        gear = next(row for row in report['interfaces'] if row['id'] == 'gear-mesh')
        retention = next(row for row in report['interfaces'] if row['id'] == 'retention')
        stack = retention.get('axialStack')
        play = [row['maximumTravelMm'] for row in retention.get('cases', [])
                if row['id'] in ('drive-plus', 'drive-minus')]
        minimum_overlap = (gear['faceWidthOverlapMm'] - stack['totalFreeTravelMm'] - max(play)
                           if stack and stack.get('totalFreeTravelMm') is not None and len(play) == 2 and
                              all(value is not None for value in play) else None)
        gear['minimumRetainedFaceOverlapMm'] = round(minimum_overlap, 6) if minimum_overlap is not None else None
        if minimum_overlap is None or minimum_overlap < 2.0:
            gear['status'] = 'fail'
        # すべて実 STL の変形を入力する。同じ判定が壊れた駆動列を落とすことを要求する。
        faults = [('gear-missing', '修正前の歯が欠落したSTL',
                   read_stl(ROOT / 'tools/fixtures/lattice-drive/c3-missing-teeth.stl'), None),
                  ('gear-separated', '歯幅を離す負例', meshes['drive_gear'] + np.array([6, 0, 0]), None),
                  ('gear-center-offset', '歯車中心を離す負例', None, meshes['cam_gear'] + np.array([0, 0, 10])),
                  ('gear-half-tooth', '歯半分の位相ずれ負例', None,
                   transform_triangles(meshes['cam_gear'], 180 / P.GEAR_TEETH, (0, P.CAM_AXIS_Z * 1000)))]
        for identifier, label, driver, follower in faults:
            altered = dict(meshes)
            if driver is not None:
                # 空の入力の歯幅検査も同じ経路で扱う。
                altered['drive_gear'] = driver
            if follower is not None:
                altered['cam_gear'] = follower
            measured = gear_report(altered, P)
            report['calibration'].append({'id': identifier, 'label': label, 'pass': measured['status'] == 'fail',
                'detail': f"歯数 {measured['actualTeeth']}。歯幅重なり {measured['faceWidthOverlapMm']}mm。接続判定 {measured['status']}。"})


def retention_checks(report, meshes, P, is_c3):
    try:
        import bpy
        from mathutils import Matrix
    except ImportError:
        report['interfaces'].append({'id': 'retention', 'label': '軸と受けの抜け止め', 'status': 'fail',
                                     'basis': 'Blender の EXACT 引抜き検査を未実行。'})
        return
    evaluator = ExactSolids(meshes)
    positive = evaluator.volume_arrays(cube_triangles(), cube_triangles() + np.array([.5, 0, 0]))
    negative = evaluator.volume_arrays(cube_triangles(), cube_triangles() + np.array([2, 0, 0]))
    contact = evaluator.volume_arrays(cube_triangles() + np.array([14, 15, 17]),
                                      cube_triangles() + np.array([15, 15, 17]))
    tilted = transform_triangles(cube_triangles(), 23, offset=(14, 15, 17))
    tilted_other = transform_triangles(cube_triangles() + np.array([0, 1, 0]), 23, offset=(14, 15, 17))
    tilted_contact = evaluator.volume_arrays(tilted, tilted_other)
    thin = evaluator.volume_arrays(cube_triangles(), cube_triangles() + np.array([.99, 0, 0]))
    report['calibration'].append({'id': 'pullout-volume', 'label': '引抜き接触の体積計器',
        'pass': abs(positive - .5) <= .001 and negative <= 1e-7 and contact <= 1e-7
                and tilted_contact <= 1e-7 and abs(thin - .01) <= .00001,
        'detail': f'1mm立方体。重複={positive:.6f}mm3。離隔={negative:.6f}mm3。移動面接触={contact:.6f}mm3。傾斜面接触={tilted_contact:.6f}mm3。薄い重複={thin:.6f}mm3（期待0.01）。'})
    cube_meter = ExactSolids({'a': cube_triangles(), 'b': cube_triangles()})
    solver_comparison = []
    for shift, expected in ((.5, .5), (2., 0.), (1., 0.), (.99, .01)):
        exact = cube_meter.volume_data(cube_meter.data['a'], cube_meter.data['b'], offset=(shift, 0, 0), solver='EXACT')
        manifold = cube_meter.volume_data(cube_meter.data['a'], cube_meter.data['b'], offset=(shift, 0, 0), solver='MANIFOLD')
        solver_comparison.append({'offsetXmm': shift, 'expectedMm3': expected,
                                  'exactMm3': exact, 'manifoldMm3': manifold})
    report['calibration'].append({'id': 'manifold-volume', 'label': '閉じた入力の独立体積計器',
        'pass': all(abs(row['exactMm3'] - row['manifoldMm3']) < .00001 and
                    abs(row['manifoldMm3'] - row['expectedMm3']) < .00001 for row in solver_comparison),
        'detail': json.dumps(solver_comparison)})
    open_input_refused = False
    try:
        ExactSolids({'open': cube_triangles()[:-1]})
    except ValueError as error:
        open_input_refused = str(error).startswith('Boolean input is not closed:')
    report['calibration'].append({'id': 'manifold-open-input', 'label': '開いた入力を拒否する負例',
        'pass': open_input_refused, 'detail': '1mm立方体の1三角形を削除した入力は、再計測前に拒否。'})
    import bpy
    for data in cube_meter.data.values():
        bpy.data.meshes.remove(data)
    cases = []
    if is_c3:
        clip = 'drive_keeper'
        if clip not in meshes:
            clip = next((name for name in meshes if 'drive' in name and ('clip' in name or 'keeper' in name)), '')
        cases = [
            ('drive-plus', '駆動歯車の前向き抜け止め', ['drive_gear'], ['shell'], (1, 0, 0), 1.0),
            ('drive-minus', '駆動歯車の後向き抜け止め', ['drive_gear'], ['shell'], (-1, 0, 0), 1.0),
            ('drive-lift', '駆動歯車の浮上防止', ['drive_gear'], [clip] if clip else [], (0, 0, 1), 1.0),
            ('drive-clip-pull', '上クリップとU字座の爪', [clip] if clip else [], ['shell'], (0, 0, 1), 1.0),
            ('horn-rear', 'ホーンとサーボの後向き着座', ['ref_horn'], ['ref_servo'], (-1, 0, 0), 1.0),
            ('horn-seat', 'ホーン腕の着座面', ['drive_gear'], ['ref_horn'], (-1, 0, 0), 1.0),
            ('shaft-plus', 'カム軸の右抜け止め', ['camshaft'], ['cap_right'], (1, 0, 0), 1.0),
            ('shaft-minus', 'カム軸の左抜け止め', ['camshaft'], ['cap_left'], (-1, 0, 0), 1.0),
            ('cap-right', '右保持具と外装', ['cap_right'], ['shell'], (1, 0, 0), 2.0),
            ('cap-left', '左保持具と外装', ['cap_left'], ['shell'], (-1, 0, 0), 2.0),
        ]
        rotating_stack = ['left_spacer', 'cam_0', 'cam_1', 'cam_gear', 'cam_2', 'cam_3', 'cam_4']
        for name in rotating_stack:
            display_name = ('左スペーサー' if name == 'left_spacer' else '従動歯車' if name == 'cam_gear'
                            else f'列{int(name[-1]) + 1}のカム')
            for suffix, direction in (('plus', (1, 0, 0)), ('minus', (-1, 0, 0))):
                cases.append((name + '-' + suffix, display_name + ('の右向き保持' if suffix == 'plus' else 'の左向き保持'), [name],
                    [other for other in rotating_stack if other != name] + ['shell', 'cap_left', 'cap_right'], direction, 2.0))
    else:
        joint = next((name for name in meshes if 'joint' in name and ('clip' in name or 'keeper' in name or 'lock' in name)), None)
        cases = [
            ('shaft-plus', '主軸と右保持具', ['camshaft'], ['bearing_keeper'], (1, 0, 0), 1.0),
            ('shaft-minus', '主軸と連結保持具', ['camshaft'], [joint] if joint else [], (-1, 0, 0), 1.0),
            ('keeper-pull', '右保持具と外装', ['bearing_keeper'], ['housing'], (1, 0, 0), 2.0),
            ('coupler-plus', '受けと主軸の前向き保持', ['horn_coupler'], ['camshaft'] + ([joint] if joint else []), (1, 0, 0), 1.0),
            ('coupler-minus', '受けと主軸の後向き保持', ['horn_coupler'], ['camshaft'] + ([joint] if joint else []), (-1, 0, 0), 1.0),
            ('horn-seat', 'ホーン腕の着座面', ['horn_coupler'], ['servo_horn'], (-1, 0, 0), 1.0),
            ('horn-rear', 'ホーンとサーボの後向き着座', ['servo_horn'], ['servo_body'], (-1, 0, 0), 1.0),
            ('joint-up', '連結保持具の上向き保持', [joint] if joint else [],
             ['horn_coupler', 'camshaft', 'housing'], (0, 0, 1), 1.0),
            ('joint-down', '連結保持具と底板', [joint] if joint else [],
             ['bottom'], (0, 0, -1), 1.0),
        ]
    removed_case = ('meter-keeper-removed', '保持相手を削除した校正',
                    ['drive_gear'] if is_c3 else ['camshaft'], [],
                    (0, 0, 1) if is_c3 else (1, 0, 0), 1.0)
    cases.append(removed_case)
    results = []
    low, high = ((P.SERVO_HOME_DEG, P.SERVO_END_DEG) if is_c3 else (P.SERVO_MIN_DEG, P.SERVO_MAX_DEG))
    angles = np.linspace(low, high, int(math.ceil((high - low) / 2.5)) + 1)

    def pose(name, angle):
        delta = angle - low
        if is_c3:
            if name in ('drive_gear', 'ref_horn'):
                return -delta, (0, P.SERVO_AXIS_Z * 1000)
            if name in ('camshaft', 'left_spacer') or name.startswith('cam_'):
                return delta, (0, P.CAM_AXIS_Z * 1000)
        elif name in ('camshaft', 'horn_coupler', 'servo_horn') or name.startswith('cam_'):
            return delta, (0, P.CAM_AXIS_Z * 1000)
        return 0, (0, 0)

    for identifier, label, moving, fixed, direction, limit in cases:
        evaluator.current_case = identifier
        print(json.dumps({'drivePhase': 'retention', 'case': identifier}), flush=True)
        if identifier == 'horn-rear':
            rows = []
            for angle in angles:
                rotation, pivot = pose(moving[0], angle)
                horn = transform_triangles(meshes[moving[0]], rotation, pivot)
                body = meshes[fixed[0]]
                measured = rear_surface_measure(horn, body)
                stop = measured['minimumGapMm']
                before = rear_surface_measure(horn + np.array([-(stop - .01), 0, 0]), body) if stop is not None else {}
                after = rear_surface_measure(horn + np.array([-(stop + .01), 0, 0]), body) if stop is not None else {}
                valid = (measured['complete'] and stop is not None and -.003 <= stop <= .55 and
                    before.get('minimumGapMm', -math.inf) >= .01 - .003 and
                    after.get('minimumGapMm', math.inf) <= -.01 + .003)
                rows.append({'servoDeg': round(float(angle), 5), 'firstStopMm': stop,
                    'supportSamples': measured['samples'], 'minimumSignedGapMm': stop,
                    'maximumSignedGapMm': measured['maximumGapMm'],
                    'beforeContactGapMm': before.get('minimumGapMm'),
                    'afterContactGapMm': after.get('minimumGapMm'), 'pass': valid})
            good = all(row['pass'] for row in rows)
            results.append({'id': identifier, 'label': label, 'moving': moving, 'fixed': fixed,
                'direction': list(direction), 'pass': good, 'samples': rows,
                'maximumTravelMm': max((row['firstStopMm'] for row in rows if row['firstStopMm'] is not None), default=None),
                'method': 'rear-surface-first-contact',
                'scope': '実STL後端面の全三角形重心からX直線で支持面まで測定。後端初接触だけ。軸ソケットの体積干渉やスプライン嵌合は未確認。'})
            cube = cube_triangles()
            controls = [rear_surface_measure(cube + np.array([shift, 0, 0]), cube) for shift in (1, 1.01, .99)]
            missing = rear_surface_measure(cube + np.array([1, 2, 0]), cube)
            report['calibration'].append({'id': 'rear-surface-contact', 'label': '後端面の接触と離隔と侵入',
                'pass': all(row['complete'] for row in controls) and
                    all(abs(row['minimumGapMm'] - expected) < .00001 for row, expected in zip(controls, (0, .01, -.01))) and
                    not missing['complete'],
                'detail': '実三角形への直線で接触0mm、離隔0.01mm、侵入-0.01mm。支持面を横へ離した負例は測定不可。'})
            print(json.dumps({'drivePhase': 'retention-result', 'case': identifier, 'pass': good,
                              'maximumTravelMm': results[-1]['maximumTravelMm']}), flush=True)
            continue
        expected_cover_stop = None
        expected_stop_part = ('cap_left' if identifier == 'left_spacer-minus' else
                              'cap_right' if identifier == 'cam_4-plus' else None)
        rows = []
        pose_cache = {}
        for angle in angles:
            if not fixed or any(name not in meshes for name in moving + fixed):
                rows.append({'servoDeg': float(angle), 'firstStopMm': None})
                continue
            cache_key = tuple((name, pose(name, angle)) for name in moving + fixed)
            if cache_key in pose_cache:
                rows.append({**pose_cache[cache_key], 'servoDeg': round(float(angle), 5)})
                continue
            baseline = evaluator.pairs(moving, fixed, (0, 0, 0), lambda name: pose(name, angle))
            volume_delta = .001
            hit = None
            stop_volume = None
            previous = 0.0
            for travel in np.arange(.25, limit + .125, .25):
                offset = np.array(direction) * travel
                volume = evaluator.pairs(moving, fixed, offset, lambda name: pose(name, angle))
                if volume > baseline + volume_delta:
                    lo, hi = previous, float(travel)
                    for _ in range(8):
                        middle = (lo + hi) / 2
                        vm = evaluator.pairs(moving, fixed, np.array(direction) * middle, lambda name: pose(name, angle))
                        if vm > baseline + volume_delta:
                            hi = middle
                        else:
                            lo = middle
                    hit, stop_volume = (lo + hi) / 2, volume
                    break
                previous = float(travel)
            stop_pair_volume = (evaluator.pairs(moving, [expected_stop_part],
                np.array(direction) * (hit + .01), lambda name: pose(name, angle))
                if expected_stop_part and hit is not None else None)
            rows.append({'servoDeg': round(float(angle), 5), 'firstStopMm': round(hit, 6) if hit is not None else None,
                         'baselineCommonVolumeMm3': round(baseline, 6),
                         'stopVolumeIncrementMm3': volume_delta,
                         'stopProbeCommonVolumeMm3': round(stop_volume, 6) if stop_volume is not None else None,
                         'expectedStopPart': expected_stop_part,
                         'expectedStopPartProbeVolumeMm3': stop_pair_volume})
            pose_cache[cache_key] = rows[-1]
        permitted = 1.65 if identifier.startswith(('cam_', 'left_spacer')) else (
            1.0 if identifier.startswith(('cap-', 'keeper-')) else .55)
        valid = all(row['firstStopMm'] is not None and row['firstStopMm'] <= permitted
                    and row.get('baselineCommonVolumeMm3', math.inf) <= (.030 if identifier == 'horn-rear' else .001)
                    and (expected_stop_part is None or row.get('expectedStopPartProbeVolumeMm3', 0) > .001)
                    and (expected_cover_stop is None or expected_cover_stop - .003 <= row['firstStopMm'] <= expected_cover_stop + .020)
                    for row in rows)
        measured_case = {'id': identifier, 'label': label, 'moving': moving, 'fixed': fixed,
                        'direction': list(direction), 'pass': valid, 'samples': rows,
                        'expectedCoverStopMm': expected_cover_stop,
                        'maximumTravelMm': max((row['firstStopMm'] for row in rows if row['firstStopMm'] is not None), default=None)}
        if identifier == 'meter-keeper-removed':
            report['calibration'].append({'id': 'keeper-removed', 'label': '保持相手を削除する負例',
                'pass': not valid and all(row['firstStopMm'] is None for row in rows),
                'detail': '同じ保持検査から保持相手を削除すると最初の止まりは無し。当該界面だけの校正。他部品との干渉や機構全体からの自由抜けは検証していない。'})
        else:
            results.append(measured_case)
        print(json.dumps({'drivePhase': 'retention-result', 'case': identifier,
                          'pass': valid, 'maximumTravelMm': measured_case['maximumTravelMm']}), flush=True)
    stack = None
    if is_c3:
        order = sorted(rotating_stack, key=lambda name: meshes[name][:, :, 0].min())
        limits = [(float(meshes[name][:, :, 0].min()), float(meshes[name][:, :, 0].max())) for name in order]
        # 端ハブは外装穴を通る。実際のスラストカラーの面を測る。
        witness = (P.CAM_AXIS_Y * 1000, P.CAM_AXIS_Z * 1000 + P.CAM_SPACER_D * 400)
        left_faces = ray_x_surfaces(meshes['cap_left'], witness)
        right_faces = ray_x_surfaces(meshes['cap_right'], witness)
        left_stop = max(left_faces) if left_faces else None
        right_stop = min(right_faces) if right_faces else None
        gaps = ([limits[0][0] - left_stop] + [b[0] - a[1] for a, b in zip(limits, limits[1:])] +
                [right_stop - limits[-1][1]]) if left_stop is not None and right_stop is not None else []
        cap_cases = {row['id']: row for row in results if row['id'] in ('cap-left', 'cap-right')}
        cap_travel = [cap_cases.get(key, {}).get('maximumTravelMm') for key in ('cap-left', 'cap-right')]
        total = sum(gaps) + sum(cap_travel) if gaps and all(v is not None for v in cap_travel) else None
        pad_margin = (P.CARRIER_BEAM_W - P.CAM_T) * 500
        part_travel = {name: {'leftMm': sum(gaps[:index + 1]) + cap_travel[0],
                             'rightMm': sum(gaps[index + 1:]) + cap_travel[1]}
                       for index, name in enumerate(order)} if total is not None else {}
        follower_travel = [max(part_travel[name].values()) for name in order
                           if name.startswith('cam_') and name != 'cam_gear'] if part_travel else []
        follower_bounds = {}
        for name in order:
            if not name.startswith('cam_') or name == 'cam_gear' or not part_travel:
                continue
            carrier = 'carrier_' + name.rsplit('_', 1)[1]
            beam_faces = ray_x_surfaces(meshes[carrier], (0, (P.CARRIER_BEAM_Z0 + P.CARRIER_BEAM_Z1) * 500))
            points = meshes[name].reshape(-1, 3)
            radial = np.linalg.norm(points[:, 1:] - np.array([P.CAM_AXIS_Y, P.CAM_AXIS_Z]) * 1000, axis=1)
            disk = points[radial > P.CAM_SPACER_D * 500 + .01]
            left_margin = float(disk[:, 0].min()) - min(beam_faces)
            right_margin = max(beam_faces) - float(disk[:, 0].max())
            remaining = min(left_margin - part_travel[name]['leftMm'],
                            right_margin - part_travel[name]['rightMm'])
            follower_bounds[name] = {'carrier': carrier, 'beamFacesXmm': [min(beam_faces), max(beam_faces)],
                'diskFacesXmm': [float(disk[:, 0].min()), float(disk[:, 0].max())],
                'leftMarginMm': left_margin, 'rightMarginMm': right_margin,
                'leftTravelMm': part_travel[name]['leftMm'], 'rightTravelMm': part_travel[name]['rightMm'],
                'minimumRemainingSupportMm': remaining, 'pass': remaining >= .1}
        stack = {'parts': order, 'clearancesMm': [round(value, 6) for value in gaps],
                 'stopFacesXmm': [left_stop, right_stop],
                 'nominalFreeTravelMm': round(sum(gaps), 6) if gaps else None,
                 'capSeatTravelMm': cap_travel, 'partTravelBoundsMm': part_travel,
                 'totalFreeTravelMm': round(total, 6) if total is not None else None,
                 'followerWidthMarginMm': round(pad_margin, 6),
                 'maximumFollowerTravelMm': max(follower_travel) if follower_travel else None,
                 'followerSupportBounds': follower_bounds,
                 'pass': bool(gaps) and min(gaps) >= -.002 and bool(follower_travel) and
                         bool(follower_bounds) and all(row['pass'] for row in follower_bounds.values())}
    report['interfaces'].append({'id': 'retention', 'label': '軸と受けの抜け止め',
        'status': 'pass' if results and all(row['pass'] for row in results) and (stack is None or stack['pass']) else 'fail',
        'cases': results, 'axialStack': stack,
        'primarySolver': 'MANIFOLD',
        'solverFallbacks': evaluator.solver_fallbacks,
        'method': '全姿勢2.5度以下。ホーン後端は実面へX直線を通した初接触。他の保持界面は水密な実STLから校正済みMANIFOLDで閉境界体積を計測。EXACTの空結果は合格根拠にしない。0.25mm区間・約0.001mm精度。'})


def ray_x_surfaces(triangles, yz):
    """実三角形へX方向の直線を通し、境界のXを返す。"""
    a, b, c = triangles[:, 0], triangles[:, 1], triangles[:, 2]
    ab, ac, aq = b[:, 1:] - a[:, 1:], c[:, 1:] - a[:, 1:], np.asarray(yz) - a[:, 1:]
    cross = lambda u, v: u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]
    det = cross(ab, ac)
    usable = abs(det) > 1e-10
    u, v = np.zeros(len(a)), np.zeros(len(a))
    u[usable] = cross(aq, ac)[usable] / det[usable]
    v[usable] = cross(ab, aq)[usable] / det[usable]
    hits = usable & (u >= -1e-8) & (v >= -1e-8) & (u + v <= 1 + 1e-8)
    values = a[hits, 0] + u[hits] * (b[hits, 0] - a[hits, 0]) + v[hits] * (c[hits, 0] - a[hits, 0])
    return sorted(set(np.round(values, 5).tolist()))


def rear_surface_measure(horn, body):
    """実後端面の重心を支持面へ投影する。X負方向の初接触だけを測る。"""
    rear_x = float(horn[:, :, 0].min())
    flat = (np.ptp(horn[:, :, 0], axis=1) < .003) & (abs(horn[:, 0, 0] - rear_x) < .003)
    witnesses = horn[flat].mean(axis=1)
    gaps = []
    for point in witnesses:
        boundaries = ray_x_surfaces(body, point[1:])
        if not boundaries:
            continue
        gaps.append(float(point[0] - max(boundaries)))
    complete = len(witnesses) > 0 and len(gaps) == len(witnesses)
    return {'complete': complete, 'samples': len(witnesses), 'supportedSamples': len(gaps),
            'minimumGapMm': round(min(gaps), 6) if gaps else None,
            'maximumGapMm': round(max(gaps), 6) if gaps else None}


def blind_floor_measure(triangles, projection, left, right):
    """指定域を埋める連続した中実材を、実境界の厚さで検査する。"""
    if left is None or right is None or right <= left or not len(projection):
        return {'pass': False, 'minimumAxialThicknessMm': None,
                'projectionSamples': len(projection), 'sections': [], 'floorRangeXmm': [left, right]}
    planes = [left + .01, (left + right) / 2, right - .01]
    sections = []
    for x in planes:
        filled = inside(projection, slice_x(triangles, x))
        sections.append({'xMm': round(x, 6), 'coveredSamples': int(filled.sum()),
                         'totalSamples': len(projection), 'pass': bool(filled.all())})
    midpoint = (left + right) / 2
    thicknesses = []
    for yz in projection:
        hits = ray_x_surfaces(triangles, yz)
        containing = [(a, b) for a, b in zip(hits[::2], hits[1::2]) if a < midpoint < b]
        thicknesses.append(max((b - a for a, b in containing), default=0.0))
    minimum = min(thicknesses)
    return {'pass': all(row['pass'] for row in sections) and minimum >= 1.2 - TOL_MM,
            'minimumAxialThicknessMm': round(minimum, 6), 'projectionSamples': len(projection),
            'sections': sections, 'floorRangeXmm': [round(left, 6), round(right, 6)]}


def servo_seat_report(report, meshes, P, is_c3):
    body, horn = (('ref_servo', 'ref_horn') if is_c3 else ('servo_body', 'servo_horn'))
    center = np.array([0, (P.SERVO_AXIS_Z if is_c3 else P.SERVO_Z) * 1000])
    radius = P.SG.SHAFT_DIA * 500
    def matching_range(name, window):
        points = meshes[name].reshape(-1, 3)
        radii = np.linalg.norm(points[:, 1:] - center, axis=1)
        near = points[(abs(radii - radius) < .01) & (points[:, 0] >= window[0] - .003)
                      & (points[:, 0] <= window[1] + .003)]
        return [float(near[:, 0].min()), float(near[:, 0].max())] if len(near) else None
    origin = -(P.SG.SHAFT_BOTTOM_Z + P.SG.SHAFT_H) * 1000 if is_c3 else P.SERVO_X0 * 1000
    shaft_range = matching_range(body, [(P.SG.SHAFT_BOTTOM_Z * 1000 + origin),
                                       ((P.SG.SHAFT_BOTTOM_Z + P.SG.SHAFT_H) * 1000 + origin)])
    socket_range = matching_range(horn, [P.SG.HORN_HUB_BOTTOM_Z * 1000 + origin,
                                        P.SG.HORN_SOCKET_TOP_Z * 1000 + origin])
    engagement = max(0, min(shaft_range[1], socket_range[1]) - max(shaft_range[0], socket_range[0])) if shaft_range and socket_range else 0
    mid_x = (max(shaft_range[0], socket_range[0]) + min(shaft_range[1], socket_range[1])) / 2 if engagement else 0
    a, b = slice_x(meshes[body], mid_x), slice_x(meshes[horn], mid_x)
    def ring_center(edges):
        points = edges.reshape(-1, 2)
        points = points[abs(np.linalg.norm(points - center, axis=1) - radius) < .02]
        return (points.max(axis=0) + points.min(axis=0)) / 2 if len(points) else np.array([math.inf] * 2)
    offset = float(np.linalg.norm(ring_center(a) - ring_center(b)))
    retention = next((row for row in report['interfaces'] if row['id'] == 'retention'), {})
    cases = {row['id']: row for row in retention.get('cases', [])}
    identifiers = ['drive-plus'] if is_c3 else ['shaft-plus', 'coupler-plus']
    retained = all(identifier in cases and cases[identifier].get('maximumTravelMm') is not None for identifier in identifiers)
    float_mm = sum(cases[identifier]['maximumTravelMm'] for identifier in identifiers) if retained else None
    pocket_gap = cases.get('horn-seat', {}).get('maximumTravelMm')
    rear_play = cases.get('horn-rear', {}).get('maximumTravelMm')
    minimum = (max(0, engagement - float_mm - pocket_gap)
               if float_mm is not None and pocket_gap is not None else None)
    arm_range = [(P.SG.HORN_ARM_BOTTOM_Z * 1000 + origin),
                 ((P.SG.HORN_ARM_BOTTOM_Z + P.SG.HORN_ARM_T) * 1000 + origin)]
    triangles = meshes[horn]
    flat = (np.ptp(triangles[:, :, 0], axis=1) < .003) & (abs(triangles[:, 0, 0] - arm_range[1]) < .003)
    centroids = triangles[flat].mean(axis=1)
    tip = (centroids[np.argmax(np.linalg.norm(centroids[:, 1:] - center, axis=1)), 1:]
           if len(centroids) else None)
    receiver = 'drive_gear' if is_c3 else 'horn_coupler'
    boundaries = ray_x_surfaces(meshes[receiver], tip) if tip is not None else []
    blind = next((x for x in boundaries if x >= arm_range[1] - .003), None)
    mouth = float(meshes[receiver][:, :, 0].min())
    # 最悪はホーンが後向きへ、受けが前向きへ動いた相対位置。
    arm_retained = (max(0, min(arm_range[1] - rear_play, blind)
                        - max(arm_range[0] - rear_play, mouth + float_mm))
                    if blind is not None and float_mm is not None and rear_play is not None else None)
    good = (engagement >= 2.5 - .003 and offset <= .003 and minimum is not None and minimum >= 2.0
            and arm_retained is not None and arm_retained >= 1.2 - .003)
    return {'id': 'servo-seat', 'label': '出力軸とホーンの公称位置と差込', 'status': 'pass' if good else 'fail',
            'shaftRangeXmm': shaft_range, 'socketRangeXmm': socket_range,
            'nominalEngagementMm': round(engagement, 6), 'axisOffsetMm': round(offset, 6) if math.isfinite(offset) else None,
            'minimumRetainedEngagementMm': round(minimum, 6) if minimum is not None else None,
            'hornArmRangeXmm': arm_range, 'receiverMouthXmm': round(mouth, 6),
            'blindStartXmm': blind, 'minimumArmEngagementMm': round(arm_retained, 6) if arm_retained is not None else None,
            'frontSeatTravelMm': pocket_gap, 'rearSeatTravelMm': rear_play,
            'basis': '実 STL の軸とソケットを測定。軸高さは正本でも仮値。スプライン歯と実物の固さは別途未確認。'}


def cube_triangles():
    vertices = np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                         (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], dtype=float)
    faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
             (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return vertices[np.array(faces)]


class ExactSolids:
    def __init__(self, meshes):
        import bpy
        import bmesh
        self.meshes = meshes
        self.data = {}
        self.volume_cache = {}
        self.solver_fallbacks = []
        self.current_case = None
        for name, triangles in meshes.items():
            vertices, index = np.unique(triangles.reshape(-1, 3), axis=0, return_inverse=True)
            mesh = bpy.data.meshes.new('drive_check_' + name)
            mesh.from_pydata(vertices.tolist(), [], index.reshape(-1, 3).tolist())
            mesh.update()
            bm = bmesh.new()
            bm.from_mesh(mesh)
            try:
                if any(not edge.is_manifold for edge in bm.edges):
                    raise ValueError(f'Boolean input is not closed: {name}')
            finally:
                bm.free()
            self.data[name] = mesh

    def pairs(self, moving, fixed, offset, pose):
        total = 0.0
        for left in moving:
            for right in fixed:
                angle_a, pivot_a = pose(left)
                angle_b, pivot_b = pose(right)
                # 共通の剛体移動で共通体積は変わらない。相対配置ごとにEXACTを一度測る。
                key = (left, right, relative_pose_key(angle_a, pivot_a, offset, angle_b, pivot_b))
                if key in self.volume_cache:
                    total += self.volume_cache[key]
                    continue
                a = transform_triangles(self.meshes[left], angle_a, pivot_a, offset)
                b = transform_triangles(self.meshes[right], angle_b, pivot_b)
                if np.any(a.max(axis=(0, 1)) < b.min(axis=(0, 1))) or np.any(b.max(axis=(0, 1)) < a.min(axis=(0, 1))):
                    continue
                measured = self.volume_data(self.data[left], self.data[right], angle_a, pivot_a, offset, angle_b, pivot_b)
                self.volume_cache[key] = measured
                total += measured
        return total

    def volume_arrays(self, a, b):
        temporary = ExactSolids({'a': a, 'b': b})
        result = temporary.volume_data(temporary.data['a'], temporary.data['b'])
        import bpy
        for data in temporary.data.values():
            bpy.data.meshes.remove(data)
        return result

    def volume_data(self, data_a, data_b, angle_a=0, pivot_a=(0, 0), offset=(0, 0, 0), angle_b=0, pivot_b=(0, 0), *, solver='MANIFOLD'):
        import bpy
        from mathutils import Matrix
        def matrix(angle, pivot, shift):
            return (Matrix.Translation(tuple(shift)) @ Matrix.Translation((0, *pivot))
                    @ Matrix.Rotation(math.radians(angle), 4, 'X') @ Matrix.Translation((0, -pivot[0], -pivot[1])))
        right = bpy.data.objects.new('drive_cutter', data_b)
        bpy.context.collection.objects.link(right)
        right.matrix_world = matrix(angle_b, pivot_b, (0, 0, 0))
        import bmesh
        sys.path.insert(0, str(ROOT / 'lib'))
        from solid_volume import closed_boundary_volume

        def calculate(method):
            left = bpy.data.objects.new('drive_intersection', data_a.copy())
            bpy.context.collection.objects.link(left)
            left.matrix_world = matrix(angle_a, pivot_a, offset)
            bpy.context.view_layer.objects.active = left
            modifier = left.modifiers.new('drive_actual_contact', 'BOOLEAN')
            modifier.operation = 'INTERSECT'
            modifier.solver = method
            modifier.object = right
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
                bm = bmesh.new()
                bm.from_mesh(left.data)
                try:
                    return closed_boundary_volume(bm)
                finally:
                    bm.free()
            finally:
                data = left.data
                bpy.data.objects.remove(left, do_unlink=True)
                bpy.data.meshes.remove(data)

        try:
            return calculate(solver)
        finally:
            bpy.data.objects.remove(right, do_unlink=True)


if __name__ == '__main__':
    main()
