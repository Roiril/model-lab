"""Binary STLを直接読み、印刷用メッシュの閉じ方と外形を検査する。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

import json
import math
import struct
from pathlib import Path

import numpy as np

import params


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STL_PATH = ROOT / "exports" / f"{params.MODEL_NAME}.stl"
REPORT_PATH = ROOT / "exports" / params.MODEL_NAME / "verification.json"
WELD_MM = 0.0001
BOTTOM_TOLERANCE_MM = 0.001
DIMENSION_TOLERANCE_MM = 2.0
AREA_EPSILON_MM2 = 1e-12
VOLUME_EPSILON_MM3 = 1e-9


def inspect_overhangs(triangles):
    """印刷姿勢のZから測る。接地面以外の下向き面を全数検査する。"""
    triangles = np.asarray(triangles, dtype=np.float64)
    cross = np.cross(triangles[:, 1] - triangles[:, 0],
                     triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(cross, axis=1)
    bottom = np.all(np.abs(triangles[:, :, 2]) <= BOTTOM_TOLERANCE_MM, axis=1)
    down = (~bottom) & (cross[:, 2] < 0) & (lengths > 0)
    angles = np.degrees(np.arctan2(-cross[:, 2], np.linalg.norm(cross[:, :2], axis=1)))
    over = down & (angles > 45.0 + 1e-5)
    return {
        "angle_reference": "vertical build direction; horizontal underside is 90 degrees",
        "max_downward_overhang_deg": float(angles[down].max()) if down.any() else 0.0,
        "over_45deg_triangles": int(over.sum()),
        "over_45deg_area_mm2": float((lengths[over] / 2).sum()),
        "downward_area_mm2": float((lengths[down] / 2).sum()),
        "excluded_bed_triangles": int(bottom.sum()),
        "passed": not bool(over.any()),
    }


def read_binary_stl(path):
    if not path.is_file():
        raise FileNotFoundError(f"STLがありません: {path}")
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError("STLヘッダーが途中で切れています")
    triangle_count = struct.unpack_from("<I", data, 80)[0]
    expected_size = 84 + triangle_count * 50
    if triangle_count == 0 or len(data) != expected_size:
        raise ValueError(
            f"STLの三角形数またはバイト数が不正です: triangles={triangle_count}, "
            f"bytes={len(data)}, expected={expected_size}"
        )
    dtype = np.dtype([
        ("normal", "<f4", (3,)),
        ("vertices", "<f4", (3, 3)),
        ("attribute", "<u2"),
    ])
    rows = np.frombuffer(data, dtype=dtype, count=triangle_count, offset=84)
    return rows["vertices"].astype(np.float64)


def _component_count(vertex_count, edges):
    parents = np.arange(vertex_count)

    def find(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    for first, second in edges:
        first_root = find(int(first))
        second_root = find(int(second))
        if first_root != second_root:
            parents[second_root] = first_root
    return len({find(index) for index in range(vertex_count)})


def inspect_triangles(triangles, check_design=False, require_overhangs=False):
    triangles = np.asarray(triangles, dtype=np.float64)
    if triangles.shape == (0,):
        triangles = triangles.reshape(0, 3, 3)
    if triangles.ndim != 3 or triangles.shape[1:] != (3, 3):
        raise ValueError(f"三角形配列の形が不正です: {triangles.shape}")
    if len(triangles) == 0:
        raise ValueError("メッシュが空です")
    if not np.isfinite(triangles).all():
        raise ValueError("座標に非有限値があります")

    quantized = np.rint(triangles.reshape(-1, 3) / WELD_MM).astype(np.int64)
    welded_vertices, vertex_ids = np.unique(quantized, axis=0, return_inverse=True)
    faces = vertex_ids.reshape(-1, 3)
    collapsed_count = int(np.count_nonzero(
        (faces[:, 0] == faces[:, 1])
        | (faces[:, 1] == faces[:, 2])
        | (faces[:, 2] == faces[:, 0])
    ))

    cross = np.cross(triangles[:, 1] - triangles[:, 0],
                     triangles[:, 2] - triangles[:, 0])
    double_area = np.linalg.norm(cross, axis=1)
    degenerate_count = int(np.count_nonzero(double_area <= 2 * AREA_EPSILON_MM2))

    directed_edges = np.concatenate((
        faces[:, [0, 1]],
        faces[:, [1, 2]],
        faces[:, [2, 0]],
    ))
    undirected_edges, edge_inverse, edge_counts = np.unique(
        np.sort(directed_edges, axis=1),
        axis=0,
        return_inverse=True,
        return_counts=True,
    )
    nonmanifold_count = int(np.count_nonzero(edge_counts != 2))
    directions = np.where(directed_edges[:, 0] < directed_edges[:, 1], 1, -1)
    direction_balance = np.bincount(
        edge_inverse, weights=directions, minlength=len(undirected_edges)
    )
    inconsistent_winding_count = int(np.count_nonzero(direction_balance != 0))
    components = _component_count(len(welded_vertices), undirected_edges)

    signed_tetrahedra = np.einsum(
        "ij,ij->i",
        triangles[:, 0],
        np.cross(triangles[:, 1], triangles[:, 2]),
    ) / 6.0
    volume_mm3 = float(signed_tetrahedra.sum())
    low = triangles.min(axis=(0, 1))
    high = triangles.max(axis=(0, 1))
    dimensions = high - low
    bottom_faces = np.all(
        np.abs(triangles[:, :, 2]) <= BOTTOM_TOLERANCE_MM,
        axis=1,
    )
    bottom_area_mm2 = float((double_area[bottom_faces] / 2.0).sum())

    failures = []
    if collapsed_count or degenerate_count:
        failures.append("面積ゼロの三角形があります")
    if nonmanifold_count:
        failures.append("出現回数が2でない無向辺があります")
    if inconsistent_winding_count:
        failures.append("共有辺の向きが反対ではありません")
    if components != 1:
        failures.append(f"連結成分が1ではありません: {components}")
    if volume_mm3 <= VOLUME_EPSILON_MM3:
        failures.append(f"符号付き体積が正ではありません: {volume_mm3}")
    if abs(float(low[2])) > BOTTOM_TOLERANCE_MM:
        failures.append(f"底のZ座標が0ではありません: {low[2]} mm")
    if bottom_area_mm2 <= AREA_EPSILON_MM2:
        failures.append("平坦な底面がありません")

    expected_dimensions = np.array([
        params.FOOT_WIDTH,
        params.LENGTH,
        params.HEIGHT,
    ]) * 1000.0
    dimension_error = dimensions - expected_dimensions
    if check_design and np.any(np.abs(dimension_error) > DIMENSION_TOLERANCE_MM):
        failures.append(
            "外形寸法が設計値から2 mmを超えて外れています: "
            f"actual={dimensions.tolist()}, expected={expected_dimensions.tolist()}"
        )

    overhangs = inspect_overhangs(triangles)
    if require_overhangs and not overhangs["passed"]:
        failures.append(f"45度を超える下向き面があります: {overhangs}")

    report = {
        "passed": not failures,
        "triangles": int(len(triangles)),
        "welded_vertices": int(len(welded_vertices)),
        "edges": int(len(undirected_edges)),
        "weld_tolerance_mm": WELD_MM,
        "nonmanifold_edges": nonmanifold_count,
        "inconsistent_winding_edges": inconsistent_winding_count,
        "degenerate_triangles": degenerate_count,
        "collapsed_after_weld_triangles": collapsed_count,
        "components": components,
        "signed_volume_cm3": volume_mm3 / 1000.0,
        "bounds_mm": [low.tolist(), high.tolist()],
        "dimensions_mm": dimensions.tolist(),
        "expected_dimensions_mm": expected_dimensions.tolist(),
        "dimension_error_mm": dimension_error.tolist(),
        "dimension_tolerance_mm": DIMENSION_TOLERANCE_MM,
        "bottom_z_mm": float(low[2]),
        "bottom_tolerance_mm": BOTTOM_TOLERANCE_MM,
        "flat_bottom_triangles": int(np.count_nonzero(bottom_faces)),
        "flat_bottom_area_mm2": bottom_area_mm2,
        "failures": failures,
        "overhangs": overhangs,
    }
    if failures:
        raise ValueError("; ".join(failures))
    return report


def calibrate():
    vertices = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ])
    faces = np.array([
        [0, 2, 1],
        [0, 1, 3],
        [1, 2, 3],
        [2, 0, 3],
    ])
    tetrahedron = inspect_triangles(vertices[faces])
    rejected = []
    for name, sample in (
        ("empty", np.empty((0, 3, 3))),
        ("single_open_triangle", vertices[[faces[0]]]),
    ):
        try:
            inspect_triangles(sample)
        except ValueError:
            rejected.append(name)
    if rejected != ["empty", "single_open_triangle"]:
        raise RuntimeError(f"検査器の校正に失敗しました: rejected={rejected}")
    angle_checks = {}
    for angle in (42.0, 45.0, 46.0, 89.0):
        slope = 1 / math.tan(math.radians(angle))
        sample = np.array([[[0., 0., 1.], [1., 0., 1. + slope], [0., -1., 1.]]])
        measured = inspect_overhangs(sample)
        expected = angle <= 45.0
        if measured["passed"] != expected or not math.isclose(
                measured["max_downward_overhang_deg"], angle, abs_tol=1e-8):
            raise RuntimeError(f"角度検査器の校正に失敗しました: {angle}, {measured}")
        angle_checks[str(angle)] = measured
    upward = np.array([[[0., 0., 1.], [1., 0., 1.], [0., 1., 1.]]])
    bed = upward[:, ::-1].copy()
    bed[:, :, 2] = 0.
    if not inspect_overhangs(upward)["passed"] or not inspect_overhangs(bed)["passed"]:
        raise RuntimeError("上向き面または接地面の角度検査に失敗しました")
    wedge_vertices = np.array([
        [0., 0., 0.], [.2, 0., 0.], [.2, 1., 0.], [0., 1., 0.],
        [0., 0., 1.], [1.5, 0., 1.], [1.5, 1., 1.], [0., 1., 1.],
    ])
    wedge_faces = np.array([
        [0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7],
    ])
    inspect_triangles(wedge_vertices[wedge_faces])
    try:
        inspect_triangles(wedge_vertices[wedge_faces], require_overhangs=True)
    except ValueError as error:
        if "45度" not in str(error):
            raise RuntimeError("閉じた張り出し形状の校正で別の検査が失敗しました") from error
    else:
        raise RuntimeError("45度超の閉じたメッシュを印刷用検査が通しました")
    inspect_triangles(vertices[faces], require_overhangs=True)
    return {
        "closed_tetrahedron_accepted": tetrahedron["passed"],
        "closed_tetrahedron_volume_mm3": tetrahedron["signed_volume_cm3"] * 1000.0,
        "rejected": rejected,
        "overhang_angles": angle_checks,
        "upward_and_bed_faces_accepted": True,
        "strict_print_accepts_tetrahedron_rejects_overhanging_wedge": True,
    }


def main():
    calibration = calibrate()
    triangles = read_binary_stl(STL_PATH)
    mesh = inspect_triangles(triangles, check_design=True)
    xy = np.unique(triangles[:, :, :2].reshape(-1, 2), axis=0)
    best = None
    for angle in np.linspace(0, math.pi / 2, 901):
        rotation = np.array([[math.cos(angle), -math.sin(angle)],
                             [math.sin(angle), math.cos(angle)]])
        size = np.ptp(xy @ rotation, axis=0)
        if best is None or float(size.max()) < best[0]:
            best = (float(size.max()), angle, size)
    bed = {
        "rotation_about_z_deg": math.degrees(best[1]),
        "rotated_xy_dimensions_mm": best[2].tolist(),
        "minimum_square_bed_mm": best[0],
        "square_bed_with_5mm_brim_mm": best[0] + 10,
        "fits_256mm_square_without_brim": best[0] <= 256,
        "fits_256mm_square_with_5mm_brim": best[0] + 10 <= 256,
    }
    report = {
        "source": str(STL_PATH.relative_to(ROOT)).replace("\\", "/"),
        "calibration": calibration,
        "mesh": mesh,
        "upright_bed_fit": bed,
        "print_ready_upright": mesh["overhangs"]["passed"],
        "validation_scope": "mesh closure and dimensions; printing angles assessed separately",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = REPORT_PATH.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(REPORT_PATH)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
