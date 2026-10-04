"""Binary STLを直接読み、印刷用メッシュの閉じ方と外形を検査する。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

import json
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


def inspect_triangles(triangles, check_design=False):
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
    return {
        "closed_tetrahedron_accepted": tetrahedron["passed"],
        "closed_tetrahedron_volume_mm3": tetrahedron["signed_volume_cm3"] * 1000.0,
        "rejected": rejected,
    }


def main():
    calibration = calibrate()
    mesh = inspect_triangles(read_binary_stl(STL_PATH), check_design=True)
    report = {
        "source": str(STL_PATH.relative_to(ROOT)).replace("\\", "/"),
        "calibration": calibration,
        "mesh": mesh,
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
