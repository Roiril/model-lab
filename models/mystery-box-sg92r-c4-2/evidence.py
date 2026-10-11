"""C4-2 の検証スクリプトで共有する実形状測定。"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import sys

import numpy as np
from mathutils import Matrix, Vector


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
LIB = ROOT / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))


def _load_c4_verify():
    """既存 C4 の校正済みメッシュ計器を別名で読む。"""
    path = HERE.parent / "mystery-box-sg92r-c4" / "verify.py"
    spec = importlib.util.spec_from_file_location("c4_verify_helpers", path)
    module = importlib.util.module_from_spec(spec)
    search_path = list(sys.path)
    try:
        spec.loader.exec_module(module)
    finally:
        # 旧C4 verifyは自身のディレクトリをsys.path先頭へ追加する。
        # C4-2のverify/paramsを後続importが確実に選ぶよう元へ戻す。
        sys.path[:] = search_path
    return module


C4 = _load_c4_verify()
Mesh = C4.Mesh
topology = C4.topology
topology_calibration = C4.topology_calibration
cube_mesh = C4.cube_mesh
exact_common_geometry = C4.exact_common_geometry
exact_common_volume = C4.exact_common_volume
exact_volume_calibration = C4.exact_volume_calibration


def load(name):
    return Mesh.load(str(BUILD / f"{name}.stl"), name)


def read_stl_path(path):
    path = Path(path)
    raw = path.read_bytes()
    if len(raw) < 84:
        raise ValueError(f"STL header is missing: {path}")
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + 50 * count:
        raise ValueError(f"STL byte count mismatch: {path}")
    dtype = np.dtype([("normal", "<f4", 3), ("vertex", "<f4", (3, 3)), ("attr", "<u2")])
    return np.frombuffer(raw, dtype=dtype, offset=84, count=count)["vertex"].astype(float)


def read_stl(name):
    return read_stl_path(BUILD / f"{name}.stl")


def triangle_bounds(triangles):
    points = triangles.reshape(-1, 3)
    return [[round(float(points[:, axis].min()), 6) for axis in range(3)],
            [round(float(points[:, axis].max()), 6) for axis in range(3)]]


def slice_z(triangles, z):
    """面と一致しない水平断面の線分を返す。"""
    rows = []
    for triangle in triangles:
        if not (triangle[:, 2].min() < z < triangle[:, 2].max()):
            continue
        points = []
        for first, second in zip(triangle, np.roll(triangle, -1, axis=0)):
            if ((first[2] <= z < second[2]) or (second[2] <= z < first[2])):
                point = first[:2] + (second[:2] - first[:2]) * (
                    (z - first[2]) / (second[2] - first[2]))
                if not any(np.linalg.norm(point - other) <= 1e-7 for other in points):
                    points.append(point)
        if len(points) == 2 and np.linalg.norm(points[1] - points[0]) > 1e-7:
            rows.append(points)
    return np.asarray(rows, dtype=float).reshape((-1, 2, 2))


def segment_distance(first, second):
    """2組の線分群の最小距離。"""
    if not len(first) or not len(second):
        return None

    def directed(points, edges):
        point = points[:, None, :]
        start = edges[None, :, 0]
        vector = (edges[:, 1] - edges[:, 0])[None]
        length2 = np.sum(vector * vector, axis=-1)
        fraction = np.clip(np.sum((point - start) * vector, axis=-1)
                           / np.maximum(length2, 1e-20), 0, 1)
        residual = point - start - fraction[..., None] * vector
        return float(np.sqrt(np.min(np.sum(residual * residual, axis=-1))))

    return min(directed(first.reshape(-1, 2), second),
               directed(second.reshape(-1, 2), first))


def transform_matrix(values):
    return Matrix([values[index:index + 4] for index in range(0, 16, 4)]).transposed()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes(paths):
    rows = {}
    for path in paths:
        path = Path(path)
        try:
            name = path.relative_to(ROOT).as_posix()
        except ValueError:
            name = path.as_posix()
        rows[name] = sha256(path)
    return rows


def stl_hashes(names):
    return source_hashes(BUILD / f"{name}.stl" for name in names)


def hashes_match(rows):
    if not rows:
        return False
    for name, digest in rows.items():
        path = Path(name)
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file() or sha256(path) != digest:
            return False
    return True


def write_json(path, document):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, path)


def calibration():
    """原型 STL を読む前に、正例と負例で計器を校正する。"""
    topology_result = topology_calibration()
    volume_result = exact_volume_calibration()
    cube = cube_mesh((0, 0, 0), 4.0, "contact_fixture")
    identity = Matrix.Identity(4)
    positive = exact_common_geometry(cube, identity, cube, Matrix.Translation((3.0, 0, 0)))
    negative = exact_common_geometry(cube, identity, cube, Matrix.Translation((5.0, 0, 0)))
    contacts = {
        "positiveCommonVolumeMm3": positive["common_volume_mm3"],
        "negativeCommonVolumeMm3": negative["common_volume_mm3"],
        "positivePass": abs(positive["common_volume_mm3"] - 16.0) <= 0.001,
        "negativePass": negative["common_volume_mm3"] <= 1e-7,
    }
    contacts["pass"] = contacts["positivePass"] and contacts["negativePass"]
    return {"topology": topology_result, "exactVolume": volume_result, "meshContact": contacts,
            "pass": topology_result["pass"] and volume_result["pass"] and contacts["pass"]}


def transformed_bounds(mesh, matrix):
    points = [matrix @ point for point in mesh.v]
    return [[round(min(point[axis] for point in points), 6) for axis in range(3)],
            [round(max(point[axis] for point in points), 6) for axis in range(3)]]


def bounds_overlap(left, right):
    return all(left[1][axis] > right[0][axis] and right[1][axis] > left[0][axis]
               for axis in range(3))


def bounds_within(actual, allowed, tolerance=0.002):
    return actual is not None and all(
        allowed[0][axis] - tolerance <= actual[0][axis]
        and actual[1][axis] <= allowed[1][axis] + tolerance for axis in range(3))


def vertical_surface_height(triangles, x, y, highest=True):
    """STL表面と鉛直線の交点を倍精度で返す。"""
    triangles = np.asarray(triangles, dtype=float)
    a, b, c = triangles[:, 0], triangles[:, 1], triangles[:, 2]
    denominator = ((b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0])
                   + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1]))
    valid = np.abs(denominator) > 1e-9
    safe_denominator = np.where(valid, denominator, 1.0)
    u = ((b[:, 1] - c[:, 1]) * (x - c[:, 0])
         + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / safe_denominator
    v = ((c[:, 1] - a[:, 1]) * (x - c[:, 0])
         + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / safe_denominator
    w = 1.0 - u - v
    inside = valid & (u >= -1e-7) & (v >= -1e-7) & (w >= -1e-7)
    if not np.any(inside):
        return None
    levels = u * a[:, 2] + v * b[:, 2] + w * c[:, 2]
    return float(np.max(levels[inside]) if highest else np.min(levels[inside]))


def rotate_xy(point, degrees):
    angle = math.radians(degrees)
    c, s = math.cos(angle), math.sin(angle)
    x, y = point
    return c * x - s * y, s * x + c * y


def sample_disk(radius, angle_degrees, radial_offsets=(-0.8, 0.0, 0.8), angular_offsets=(-1.0, 0.0, 1.0)):
    rows = []
    for radial in radial_offsets:
        for angle in angular_offsets:
            theta = math.radians(angle_degrees + angle)
            rows.append(((radius + radial) * math.cos(theta), (radius + radial) * math.sin(theta)))
    return rows


def rotate_about_z(degrees, x=0.0, y=0.0):
    return (Matrix.Translation((x, y, 0.0))
            @ Matrix.Rotation(math.radians(degrees), 4, "Z")
            @ Matrix.Translation((-x, -y, 0.0)))


def first_angular_contact(male, female, pivot=(0.0, 0.0), sign=1,
                          maximum_degrees=20.0, coarse_step=0.25):
    """雄形状だけを回し、MANIFOLD共通体積が閾値を超える最初の角度を返す。"""
    identity = Matrix.Identity(4)

    def volume(angle):
        return exact_common_volume(male, rotate_about_z(sign * angle, *pivot), female, identity)

    nominal = volume(0.0)
    if nominal > 0.001:
        return {"nominalCommonVolumeMm3": nominal, "contactAngleDeg": 0.0,
                "contactCommonVolumeMm3": nominal, "pass": False}
    previous = 0.0
    angle = coarse_step
    while angle <= maximum_degrees + 1e-9:
        current = volume(angle)
        if current > 0.001:
            low, high = previous, angle
            for _ in range(12):
                middle = (low + high) / 2.0
                if volume(middle) > 0.001:
                    high = middle
                else:
                    low = middle
            contact_volume = volume(high)
            return {"nominalCommonVolumeMm3": nominal,
                    "contactAngleDeg": round(high, 6),
                    "contactCommonVolumeMm3": round(contact_volume, 6), "pass": True}
        previous, angle = angle, angle + coarse_step
    return {"nominalCommonVolumeMm3": nominal, "contactAngleDeg": None,
            "contactCommonVolumeMm3": None, "pass": False}


def common_at_rotation(male, female, degrees, pivot=(0.0, 0.0)):
    return exact_common_geometry(male, rotate_about_z(degrees, *pivot),
                                 female, Matrix.Identity(4))


def first_linear_contact(male, female, axis=2, sign=1, maximum_mm=12.0, coarse_step=0.25):
    """雄形状だけを直線移動し、最初のMANIFOLD共通体積を返す。"""
    identity = Matrix.Identity(4)

    def volume(distance):
        offset = [0.0, 0.0, 0.0]
        offset[axis] = sign * distance
        return exact_common_volume(male, Matrix.Translation(offset), female, identity)

    nominal = volume(0.0)
    if nominal > 0.001:
        return {"nominalCommonVolumeMm3": nominal, "contactTravelMm": 0.0,
                "contactCommonVolumeMm3": nominal, "pass": False}
    previous = 0.0
    distance = coarse_step
    while distance <= maximum_mm + 1e-9:
        current = volume(distance)
        if current > 0.001:
            low, high = previous, distance
            for _ in range(12):
                middle = (low + high) / 2.0
                if volume(middle) > 0.001:
                    high = middle
                else:
                    low = middle
            return {"nominalCommonVolumeMm3": nominal, "contactTravelMm": round(high, 6),
                    "contactCommonVolumeMm3": round(volume(high), 6), "pass": True}
        previous, distance = distance, distance + coarse_step
    return {"nominalCommonVolumeMm3": nominal, "contactTravelMm": None,
            "contactCommonVolumeMm3": None, "pass": False}


def common_at_translation(male, female, offset):
    return exact_common_geometry(male, Matrix.Translation(tuple(offset)),
                                 female, Matrix.Identity(4))
