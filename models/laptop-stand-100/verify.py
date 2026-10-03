"""Read the exported binary STL directly. Units in this script are millimetres.

Run: py -3.11 models/laptop-stand-100/verify.py
Static calculations use explicit assumed stiffness, not measured load capacity.
"""
from __future__ import annotations

import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "exports" / "laptop-stand-100"
WELD_MM = 0.0001


def load_stl(path):
    data = Path(path).read_bytes()
    if len(data) < 84:
        raise ValueError("STL header is incomplete")
    count = struct.unpack_from("<I", data, 80)[0]
    if count == 0 or len(data) != 84 + count * 50:
        raise ValueError("STL is empty or its triangle count is inconsistent")
    dtype = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)),
                      ("attribute", "<u2")])
    records = np.frombuffer(data, dtype=dtype, count=count, offset=84)
    return records["vertices"].astype(np.float64)


def inspect_mesh(triangles, expected_components=1):
    if len(triangles) == 0 or not np.isfinite(triangles).all():
        raise ValueError("Mesh is empty or contains nonfinite coordinates")
    vertices, ids = np.unique(np.rint(triangles.reshape(-1, 3) / WELD_MM).astype(np.int64),
                              axis=0, return_inverse=True)
    ids = ids.reshape(-1, 3)
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    area2 = np.linalg.norm(cross, axis=1)
    if np.any(area2 < 1e-9):
        raise ValueError("Degenerate triangles")
    faces = np.sort(ids, axis=1)
    if len(np.unique(faces, axis=0)) != len(faces):
        raise ValueError("Duplicate triangles")
    directed = np.concatenate((ids[:, [0, 1]], ids[:, [1, 2]], ids[:, [2, 0]]))
    edges, inverse, counts = np.unique(np.sort(directed, axis=1), axis=0,
                                       return_inverse=True, return_counts=True)
    if not np.all(counts == 2):
        raise ValueError(f"Nonmanifold edges: {int(np.sum(counts != 2))}")
    direction = np.where(directed[:, 0] < directed[:, 1], 1, -1)
    balance = np.bincount(inverse, weights=direction, minlength=len(edges))
    if np.any(balance != 0):
        raise ValueError("Inconsistent face winding")
    parents = np.arange(len(vertices))

    def find(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    for a, b in edges:
        parents[find(a)] = find(b)
    components = len({find(i) for i in range(len(vertices))})
    if components != expected_components:
        raise ValueError(f"Disconnected solids: {components}")
    tetra = np.einsum("ij,ij->i", triangles[:, 0],
                       np.cross(triangles[:, 1], triangles[:, 2])) / 6.0
    volume = float(tetra.sum())
    if volume <= 1e-6:
        raise ValueError("Nonpositive volume")
    centroid = (tetra[:, None] * triangles.sum(axis=1) / 4.0).sum(axis=0) / volume
    low = triangles.min(axis=(0, 1))
    high = triangles.max(axis=(0, 1))
    return {"triangles": len(triangles), "vertices": len(vertices),
            "components": components, "nonmanifold_edges": 0,
            "degenerate_triangles": 0, "dimensions_mm": (high - low).tolist(),
            "bounds_mm": [low.tolist(), high.tolist()], "volume_cm3": volume / 1000.0,
            "uniform_density_centroid_mm": centroid.tolist(),
            "surface_area_cm2": float(area2.sum() / 200.0)}


def ray_hits(triangles, point, direction):
    """Moller-Trumbore intersection, with coincident edge hits merged."""
    point = np.asarray(point, dtype=float)
    direction = np.asarray(direction, dtype=float)
    e1 = triangles[:, 1] - triangles[:, 0]
    e2 = triangles[:, 2] - triangles[:, 0]
    h = np.cross(np.broadcast_to(direction, e2.shape), e2)
    det = np.einsum("ij,ij->i", e1, h)
    usable = np.abs(det) > 1e-10
    inv = np.zeros_like(det)
    inv[usable] = 1.0 / det[usable]
    delta = point - triangles[:, 0]
    u = np.einsum("ij,ij->i", delta, h) * inv
    q = np.cross(delta, e1)
    v = q @ direction * inv
    t = np.einsum("ij,ij->i", e2, q) * inv
    good = usable & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9) & (t > 1e-5)
    hits = np.sort(t[good])
    if len(hits) > 1:
        hits = hits[np.r_[True, np.diff(hits) > 0.0001]]
    return hits


def contains(triangles, point):
    # Irrational components avoid frequent face diagonals at symmetric coordinates.
    return len(ray_hits(triangles, point, (1, 0.0000137, 0.0000173))) % 2 == 1


def calibrate():
    v = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                  [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]], dtype=float)
    f = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
                  [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
                  [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    cube = v[f]
    info = inspect_mesh(cube)
    assert abs(info["volume_cm3"] - 0.001) < 1e-12
    assert contains(cube, (0.5, 0.5, 0.5))
    assert not contains(cube, (2.5, 0.5, 0.5))
    rejected = 0
    for broken in (cube[1:], cube[:, ::-1], np.empty((0, 3, 3))):
        try:
            inspect_mesh(broken)
        except ValueError:
            rejected += 1
    assert rejected == 3
    return {"closed_cube_accepted": True, "open_inverted_empty_rejected": 3,
            "inside_and_outside_ray_checks": True}


def unrotate_print(triangles, params):
    restored = np.empty_like(triangles)
    restored[:, :, 0] = triangles[:, :, 2] - params.FRAME_WIDTH * 500
    restored[:, :, 1] = (triangles[:, :, 0] + triangles[:, :, 1]) / math.sqrt(2) + params.FRAME_DEPTH * 500
    restored[:, :, 2] = (triangles[:, :, 1] - triangles[:, :, 0]) / math.sqrt(2) + params.BODY_HEIGHT * 500
    return restored


def geometry_checks(frame, printing, assembly, params):
    width = params.FRAME_WIDTH * 1000
    depth = params.FRAME_DEPTH * 1000
    height = params.BODY_HEIGHT * 1000
    expected = [width, depth, height]
    actual = inspect_mesh(frame)["dimensions_mm"]
    if not np.allclose(actual, expected, atol=0.01):
        raise ValueError(f"Frame dimensions differ: {actual}")
    assert contains(frame, (0, depth / 2, height - 4))
    assert not contains(frame, (0, depth / 2, height / 2))
    measured = {"top": [], "bottom": [], "front_column": [], "rear_column": [], "width": []}
    for y in np.linspace(30, depth - 30, 20):
        for label, point, direction in [
            ("top", (0, y, height + 0.01), (0, 0, -1)),
            ("bottom", (0, y, -0.01), (0, 0, 1)),
        ]:
            hits = ray_hits(frame, point, direction)
            if len(hits) < 2:
                raise ValueError(f"Missing {label} surfaces")
            measured[label].append(float(hits[1] - hits[0]))
    for z in np.linspace(25, 65, 12):
        for label, point, direction in [
            ("front_column", (0, -0.01, z), (0, 1, 0)),
            ("rear_column", (0, depth + 0.01, z), (0, -1, 0)),
        ]:
            hits = ray_hits(frame, point, direction)
            if len(hits) < 2:
                raise ValueError(f"Missing {label} surfaces")
            measured[label].append(float(hits[1] - hits[0]))
    for y in (40, 100, 170, 205):
        hits = ray_hits(frame, (-width / 2 - 0.01, y, height - 5), (1, 0, 0))
        measured["width"].append(float(hits[1] - hits[0]))
    limits = {"top": params.TOP_BEAM * 1000, "bottom": params.BOTTOM_BEAM * 1000,
              "front_column": params.END_COLUMN * 1000, "rear_column": params.END_COLUMN * 1000,
              "width": width}
    minimum = {name: min(values) for name, values in measured.items()}
    if any(minimum[name] < limit - 0.01 for name, limit in limits.items()):
        raise ValueError(f"A section is thinner than designed: {minimum}")
    cross = np.cross(printing[:, 1] - printing[:, 0], printing[:, 2] - printing[:, 0])
    lengths = np.linalg.norm(cross, axis=1)
    normals = cross / lengths[:, None]
    bed = printing[:, :, 2].max(axis=1) < 0.001
    steep = (normals[:, 2] < -math.sin(math.radians(45.5))) & ~bed
    if steep.any():
        raise ValueError(f"Steep faces in print orientation: {int(steep.sum())}")
    if abs(float(printing[:, :, 2].min())) > 0.001:
        raise ValueError("Print is not on the bed")
    pad_points = 0
    for x in (-params.RAIL_CENTER * 1000, params.RAIL_CENTER * 1000):
        for start in (params.PAD_FRONT_Y * 1000, params.PAD_REAR_Y * 1000):
            for dx in (-params.PAD_WIDTH * 500, 0, params.PAD_WIDTH * 500):
                for dy in (0, params.PAD_LENGTH * 500, params.PAD_LENGTH * 1000):
                    hits = ray_hits(assembly, (x + dx, start + dy, 0), (0, 0, 1))
                    if len(hits) < 2 or abs(float(hits[0]) - params.PAD_THICKNESS * 1000) > 0.01:
                        raise ValueError("Pad is not beneath flat stand material")
                    pad_points += 1
    return {"minimum_sampled_sections_mm": minimum, "flat_bottom_pad_points": pad_points,
            "height_with_two_1mm_pads_mm": height + 2 * params.PAD_THICKNESS * 1000,
            "steep_downward_faces_above_bed": int(steep.sum()),
            "maximum_downward_overhang_deg": float(np.degrees(np.arcsin(np.clip(-normals[~bed, 2], 0, 1))).max()),
            "bed_contact_area_cm2": float(lengths[bed].sum() / 200),
            "print_xy_with_4mm_brim_mm": (np.ptp(printing, axis=(0, 1))[:2] + 8).tolist()}


def load_estimate(params, stand_mass):
    g = 9.80665
    span = (params.FRAME_DEPTH - 2 * params.END_COLUMN) * 1000
    width = params.FRAME_WIDTH * 1000
    thickness = params.TOP_BEAM * 1000
    modulus = 1000.0  # MPa, deliberately an assumption rather than a material claim.
    allowable = 5.0  # MPa, assumed design check threshold, not a tested rating.
    inertia = width * thickness ** 3 / 12
    section = width * thickness ** 2 / 6
    cases = []
    for name, force in [("4kg_total_75_percent_on_one_frame", params.LOAD_MASS_KG * g * .75),
                        ("3kg_concentrated_on_one_frame", 3 * g),
                        ("3kg_on_one_frame_plus_20n_keyboard_press", 3 * g + 20),
                        ("4kg_concentrated_on_one_frame", 4 * g),
                        ("4kg_on_one_frame_plus_20n_keyboard_press", 4 * g + 20)]:
        stress = force * span / (4 * section)
        deflection = force * span ** 3 / (48 * modulus * inertia)
        if stress > allowable or deflection > 1.5:
            raise ValueError(f"Assumed beam check failed: {name}")
        cases.append({"case": name, "load_n": force, "bending_stress_mpa": stress,
                      "midspan_deflection_mm": deflection,
                      "allowable_to_stress_ratio": allowable / stress})
    # Support coordinates use the actual four pad locations, with a 1mm inset.
    half = params.RAIL_CENTER * 1000 + params.PAD_WIDTH * 500 - 1
    front = params.PAD_FRONT_Y * 1000 + 1
    rear = (params.PAD_REAR_Y + params.PAD_LENGTH) * 1000 - 1
    center_y = params.FRAME_DEPTH * 500
    stability = []
    for mass in (3.0, 4.0):
        for dx in (-30, 30):
            for dy in (-60, 60):
                for px in (-params.LAPTOP_WIDTH * 500, params.LAPTOP_WIDTH * 500):
                    for py in (center_y - params.LAPTOP_DEPTH * 500, center_y + params.LAPTOP_DEPTH * 500):
                        load = 20
                        total = (mass + stand_mass) * g + load
                        rx = (mass * g * dx + load * px) / total
                        ry = (mass * g * (center_y + dy) + stand_mass * g * center_y + load * py) / total
                        margin = min(half - abs(rx), ry - front, rear - ry)
                        if margin <= 0:
                            raise ValueError("Resultant vertical load leaves support polygon")
                        stability.append(margin)
    return {"design_laptop_mass_kg": params.LOAD_MASS_KG, "beam_span_mm": span,
            "assumed_modulus_mpa": modulus, "assumed_stress_threshold_mpa": allowable,
            "beam_cases": cases, "contact_polygon_mm": [[-half, front], [half, front], [half, rear], [-half, rear]],
            "assumed_laptop_com_offsets_mm": {"side": 30, "front_rear": 60},
            "vertical_keyboard_press_n": 20, "static_cases_checked": len(stability),
            "minimum_vertical_resultant_margin_mm": min(stability),
            "limitations": "Assumed solid-beam static calculation only. Printed strength, heat, creep, friction and laptop contact require physical tests."}


def main():
    import params
    calibration = calibrate()
    printing = load_stl(OUT / "frame.stl")
    assembly = load_stl(ROOT / "exports/laptop-stand-100.stl")
    canonical = unrotate_print(printing, params)
    frame_info = inspect_mesh(canonical)
    print_info = inspect_mesh(printing)
    assembly_info = inspect_mesh(assembly, expected_components=2)
    if abs(assembly_info["volume_cm3"] - 2 * frame_info["volume_cm3"]) > .01:
        raise ValueError("Assembly volume differs from two identical frames")
    density = 1.27
    mass = assembly_info["volume_cm3"] * density / 1000
    report = {"calibration": calibration, "frame": frame_info, "print": print_info,
              "assembly": assembly_info, "geometry": geometry_checks(canonical, printing, assembly, params),
              "material": {"assumed_petg_density_g_cm3": density, "solid_pair_mass_g": mass * 1000,
                           "note": "Volume conversion only; excludes brim and startup waste."},
              "load_estimate": load_estimate(params, mass)}
    path = OUT / "verification.json"
    temporary = path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8', newline='\n')
    temporary.replace(path)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
