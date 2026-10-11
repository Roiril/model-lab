"""実STLの三角形と有限接点の重なりから鉛直接触高さを求める。"""
from functools import lru_cache
from pathlib import Path
import hashlib
import math
import struct

import numpy as np

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"


def read_stl(path):
    raw = path.read_bytes()
    count = struct.unpack_from('<I', raw, 80)[0]
    if len(raw) != 84 + 50 * count:
        raise ValueError(f'invalid STL: {path}')
    dtype = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])
    return np.frombuffer(raw, dtype=dtype, count=count, offset=84)['vertices'].astype(np.float64)


def cross(a, b):
    return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]


def barycentric(points, triangles):
    a = triangles[:, 0, :2]
    u = triangles[:, 1, :2] - a
    v = triangles[:, 2, :2] - a
    denominator = cross(u, v)
    safe = np.where(np.abs(denominator) > 1e-14, denominator, np.nan)
    relative = points[:, None, :] - a[None, :, :]
    b = cross(relative, v[None, :, :]) / safe[None, :]
    c = cross(u[None, :, :], relative) / safe[None, :]
    weights = np.stack((1 - b - c, b, c), axis=-1)
    inside = np.isfinite(weights).all(axis=-1) & (weights >= -1e-10).all(axis=-1)
    return weights, inside


def boundary_edges(triangles):
    counts = {}
    for triangle in triangles:
        for i in range(3):
            a = tuple(triangle[i, :2])
            b = tuple(triangle[(i + 1) % 3, :2])
            key = tuple(sorted((a, b)))
            counts[key] = counts.get(key, 0) + 1
    return np.array([edge for edge, count in counts.items() if count == 1], dtype=np.float64)


def minimum_radius(triangles):
    values = []
    for i in range(3):
        start = triangles[:, i, :2]
        delta = triangles[:, (i + 1) % 3, :2] - start
        squared = (delta * delta).sum(axis=1)
        fraction = np.clip(-(start * delta).sum(axis=1)
                           / np.maximum(squared, 1e-30), 0, 1)
        values.append(np.linalg.norm(start + fraction[:, None] * delta, axis=1))
    radii = np.minimum.reduce(values)
    _, origin_inside = barycentric(np.array([[0., 0.]]), triangles)
    radii[origin_inside[0]] = 0
    return radii


def maximum_height(cam_triangles, foot_triangles, foot_edges=None, cam_bounds=None):
    """重なる各三角形の頂点と辺交点が線形高さの極値を含む。"""
    foot_points = foot_triangles[:, :, :2].reshape(-1, 2)
    lo, hi = foot_points.min(axis=0), foot_points.max(axis=0)
    cam_lo, cam_hi = cam_bounds if cam_bounds is not None else (
        cam_triangles[:, :, :2].min(axis=1), cam_triangles[:, :, :2].max(axis=1))
    relevant = (cam_hi >= lo - 1e-9).all(axis=1)
    relevant &= (cam_lo <= hi + 1e-9).all(axis=1)
    cam = cam_triangles[relevant]
    if not len(cam):
        raise ValueError('foot has no cam below it')
    peaks = []
    weights, inside = barycentric(foot_points, cam)
    heights = (weights * cam[None, :, :, 2]).sum(axis=-1)
    if inside.any():
        peaks.append(float(heights[inside].max()))
    cam_points = cam.reshape(-1, 3)
    _, inside_foot = barycentric(cam_points[:, :2], foot_triangles)
    belongs = inside_foot.any(axis=1)
    if belongs.any():
        peaks.append(float(cam_points[belongs, 2].max()))
    edges = boundary_edges(foot_triangles) if foot_edges is None else foot_edges
    cam_edges = np.concatenate((cam[:, [0, 1]], cam[:, [1, 2]], cam[:, [2, 0]]))
    a = cam_edges[:, 0, :2]
    u = cam_edges[:, 1, :2] - a
    b = edges[:, 0, :]
    v = edges[:, 1, :] - b
    denominator = cross(u[:, None, :], v[None, :, :])
    safe = np.where(np.abs(denominator) > 1e-14, denominator, np.nan)
    relative = b[None, :, :] - a[:, None, :]
    along_cam = cross(relative, v[None, :, :]) / safe
    along_foot = cross(relative, u[:, None, :]) / safe
    intersections = (np.isfinite(along_cam) & (along_cam >= -1e-10)
                     & (along_cam <= 1 + 1e-10) & (along_foot >= -1e-10)
                     & (along_foot <= 1 + 1e-10))
    edge_heights = (cam_edges[:, 0, 2, None]
                    + along_cam * (cam_edges[:, 1, 2] - cam_edges[:, 0, 2])[:, None])
    if intersections.any():
        peaks.append(float(edge_heights[intersections].max()))
    if not peaks:
        raise ValueError('cam and foot do not overlap in XY')
    return max(peaks)


def calibration():
    foot = np.array([[[0, 0, 0], [1, 0, 0], [1, 1, 0]],
                     [[0, 0, 0], [1, 1, 0], [0, 1, 0]]], dtype=float)
    cam = foot.copy()
    cam[:, :, 2] = cam[:, :, 0] + cam[:, :, 1]
    edge_case = maximum_height(cam, foot)
    inner = np.array([[[.2, .2, 0], [.8, .2, 0], [.2, .8, 0]]])
    inner_case = maximum_height(cam, inner)
    crossing_cam = np.array([[[-2, -1, 0], [2, -1, 0], [0, 1, 2]]], dtype=float)
    crossing_foot = np.array([[[-2, .5, 0], [2, .5, 0], [0, -1.5, 0]]], dtype=float)
    crossing_case = maximum_height(crossing_cam, crossing_foot)
    displaced = foot.copy()
    displaced[:, :, 0] += 10
    try:
        maximum_height(cam, displaced)
        absent = False
    except ValueError:
        absent = True
    cases = {'shared_edges_expected_2': abs(edge_case - 2) < 1e-10,
             'edge_intersection_expected_1': abs(inner_case - 1) < 1e-10,
             'only_edge_intersections_expected_1_5': abs(crossing_case - 1.5) < 1e-10,
             'displaced_foot_rejected': absent,
             'long_chord_minimum_radius_expected_1': abs(minimum_radius(np.array(
                 [[[-100, 1, 0], [100, 1, 0], [100, 2, 0]]], dtype=float))[0] - 1) < 1e-10}
    cases = {name: bool(value) for name, value in cases.items()}
    return {'cases': cases, 'pass': all(cases.values())}


@lru_cache(maxsize=1)
def geometry():
    import params as P
    proof = calibration()
    if not proof['pass']:
        raise ValueError(f'contact envelope calibration failed: {proof}')
    cam = read_stl(BUILD / 'cam_disk.stl')
    normal = np.cross(cam[:, 1] - cam[:, 0], cam[:, 2] - cam[:, 0])
    cam = cam[normal[:, 2] > 1e-14]
    cam_radial = np.linalg.norm(cam[:, :, :2], axis=2)
    cam_minimum_radius = minimum_radius(cam)
    groups = []
    for name in P.GROUPS:
        carrier = read_stl(BUILD / f'carrier_{name}.stl')
        floor = float(carrier[:, :, 2].min())
        foot = carrier[(np.abs(carrier[:, :, 2] - floor) < 1e-7).all(axis=1)]
        if not len(foot):
            raise ValueError(f'{name}: horizontal finite foot missing')
        foot_radial = np.linalg.norm(foot[:, :, :2], axis=2)
        radial_match = ((cam_radial.max(axis=1) >= minimum_radius(foot).min() - 1e-9)
                        & (cam_minimum_radius <= foot_radial.max() + 1e-9))
        local_cam = cam[radial_match]
        bounds = (local_cam[:, :, :2].min(axis=1), local_cam[:, :, :2].max(axis=1))
        groups.append((foot, boundary_edges(foot), floor, local_cam, bounds))
    return cam, groups


@lru_cache(maxsize=200000)
def lift_mm(group, degree):
    import params as P
    cam, groups = geometry()
    foot, edges, floor, local_cam, bounds = groups[group]
    angle = math.radians(-(degree - P.HOME_SERVO_DEG))
    c, s = math.cos(angle), math.sin(angle)
    rotation = np.array([[c, -s], [s, c]])
    rotated = foot.copy()
    rotated[:, :, :2] = foot[:, :, :2] @ rotation.T
    rotated_edges = edges @ rotation.T
    return maximum_height(local_cam, rotated, rotated_edges, bounds) - floor


def source_hashes():
    import params as P
    paths = [Path(__file__), HERE / 'params.py', HERE / 'motion.py', BUILD / 'cam_disk.stl',
             *[BUILD / f'carrier_{name}.stl' for name in P.GROUPS]]
    return {path.relative_to(HERE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}
