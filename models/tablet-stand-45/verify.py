"""Read the exported binary STL directly. Units in this script are millimetres.

Run: py -3.11 models/tablet-stand-45/verify.py --stand-mass 1.0
The static calculation is an assumption-based estimate, not a strength test.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "exports" / "tablet-stand-45"
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


def inspect_mesh(triangles):
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
    if components != 1:
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


def frame(params):
    angle = math.radians(params.ANGLE_DEG)
    u = np.array([0.0, math.cos(angle), math.sin(angle)])
    n = np.array([0.0, -math.sin(angle), math.cos(angle)])
    origin = np.array([0.0, params.SEAT_Y * 1000, params.SEAT_Z * 1000])
    return origin, u, n


def geometric_checks(triangles, printing, params):
    origin, u, n = frame(params)
    # The case spans 16mm, with 1mm backing and bottom cushioning.
    tested = 0
    for lift in np.linspace(0.0, 50.0, 101):
        for along in (1.0, 4.0, 10.0, 40.0, 90.0, 160.0, 226.0):
            for thickness in (1.0, 9.0, 17.0):
                for x in (-80.0, 0.0, 80.0):
                    point = origin + u * along + n * thickness + np.array([x, 0.0, lift])
                    if contains(triangles, point):
                        raise ValueError(f"Tablet lift intersects stand: {point.tolist()}")
                    tested += 1
    # Check material and void using the same occupancy instrument.
    assert contains(triangles, (0, 100, 5))
    assert not contains(triangles, (0, 110, 40))
    deck = []
    for along in np.linspace(45, 140, 16):
        hits = ray_hits(triangles, origin + u * along + n * 0.01, -n)
        if len(hits) < 2:
            raise ValueError("Deck ray did not cross both faces")
        deck.append(float(hits[1] - hits[0]))
    base = []
    for y in np.linspace(65, 195, 16):
        hits = ray_hits(triangles, (0, y, -0.01), (0, 0, 1))
        if len(hits) < 2:
            raise ValueError("Base ray did not cross both faces")
        base.append(float(hits[1] - hits[0]))
    if min(deck) < params.DECK_THICKNESS * 1000 - 0.01:
        raise ValueError("Deck is thinner than its design dimension")
    if min(base) < params.BASE_THICKNESS * 1000 - 0.01:
        raise ValueError("Base is thinner than its design dimension")
    cross = np.cross(printing[:, 1] - printing[:, 0], printing[:, 2] - printing[:, 0])
    lengths = np.linalg.norm(cross, axis=1)
    normals = cross / lengths[:, None]
    bed = printing[:, :, 2].max(axis=1) < 0.001
    # Bevel mitres on tessellated arcs can exceed exactly 45 degrees very slightly.
    # Report their actual maximum. A 0.5 degree tolerance is explicit, not hidden.
    limit = math.sin(math.radians(45.5))
    steep = (normals[:, 2] < -limit) & ~bed
    if np.any(steep):
        raise ValueError(f"Print has steep unsupported faces: {int(steep.sum())}")
    if abs(float(printing[:, :, 2].min())) > 0.001:
        raise ValueError("Print is not on Z=0")
    return {"vertical_lift_samples_clear": tested, "vertical_lift_mm": 50,
            "sampled_case_thickness_mm": 16, "back_and_floor_pad_mm": 1,
            "minimum_sampled_deck_mm": min(deck), "minimum_sampled_base_mm": min(base),
            "steep_downward_faces_above_bed": int(steep.sum()),
            "overhang_threshold_deg": 45.5,
            "maximum_downward_overhang_deg": float(np.degrees(np.arcsin(
                np.clip(-normals[~bed, 2], 0, 1))).max()),
            "bed_contact_area_cm2": float(lengths[bed].sum() / 200),
            "lift_note": "Sampled geometric clearance; not a physical extraction test"}


def static_estimate(info, params, stand_mass):
    origin, u, n = frame(params)
    # Continuous strips extend to x=+-108, front y=10..24, rear y=222..236.
    # This polygon uses 2mm inset from their outer edges.
    half_width = params.WIDTH * 500 - 6
    front = 12.0
    rear = params.DEPTH * 1000 - 6
    stand_y = info["uniform_density_centroid_mm"][1]
    stand_y_conservative = stand_y + 10.0
    g = 9.80665
    touch_n = 10.0
    safety = 1.5
    rows = []
    for width, height, mass, thickness in [(281.6, 215.5, 0.579, 5.1),
                                            (326.4, 208.6, 0.718, 5.4),
                                            (340.0, 225.0, 0.600, 16.0),
                                            (340.0, 225.0, 1.000, 16.0)]:
        center = origin + u * (height / 2 + 1) + n * (1 + thickness / 2)
        top = origin + u * (height + 1) + n * (1 + thickness)
        top[2] += 1.5  # Adhesive feet lift the assembly above the tabletop.
        rear_lever_per_n = max(0.0, math.sin(math.radians(params.ANGLE_DEG)) * top[2]
                              + math.cos(math.radians(params.ANGLE_DEG)) * (top[1] - rear)) / 1000
        rear_moment = g * (stand_mass * (rear - stand_y_conservative)
                           + mass * (rear - center[1])) / 1000
        side_lever_per_n = math.cos(math.radians(params.ANGLE_DEG)) * max(0.0, width / 2 - half_width) / 1000
        side_moment = (stand_mass + mass) * g * half_width / 1000
        rear_force = rear_moment / rear_lever_per_n
        side_force = side_moment / side_lever_per_n if side_lever_per_n else float("inf")
        minimum_mass = max(0.0, (safety * touch_n * rear_lever_per_n * 1000 / g
                                - mass * (rear - center[1])) / (rear - stand_y_conservative))
        mu_required = safety * touch_n * math.sin(math.radians(params.ANGLE_DEG)) / (
            (stand_mass + mass) * g + touch_n * math.cos(math.radians(params.ANGLE_DEG)))
        rows.append({"tablet_width_height_mm": [width, height], "tablet_mass_kg": mass,
                     "case_thickness_mm": thickness, "rear_tip_threshold_normal_press_n": rear_force,
                     "side_tip_threshold_normal_press_n": side_force,
                     "rear_safety_factor_at_10n": rear_force / touch_n,
                     "side_safety_factor_at_10n": side_force / touch_n,
                     "stand_mass_for_rear_factor_1_5_kg": minimum_mass,
                     "friction_coefficient_for_slide_factor_1_5": mu_required,
                     "unloaded_center_from_front_mm": (
                         stand_mass * stand_y + mass * center[1]) / (stand_mass + mass) - front})
    minimum = max(row["stand_mass_for_rear_factor_1_5_kg"] for row in rows)
    return {"assumed_stand_mass_kg": stand_mass, "screen_normal_press_n": touch_n,
            "contact_polygon_mm": [[-half_width, front], [half_width, front],
                                   [half_width, rear], [-half_width, rear]],
            "stand_centroid_uncertainty_rearward_mm": 10,
            "required_stand_mass_kg": minimum, "cases": rows,
            "limitations": "Rigid-body static estimate only. Actual mass, friction, strength and fatigue need physical verification."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stand-mass", type=float, default=1.0, help="Finished printed stand mass, kg")
    args = parser.parse_args()
    if args.stand_mass <= 0:
        parser.error("stand mass must be positive")
    import params
    calibration = calibrate()
    stand = load_stl(ROOT / "exports" / "tablet-stand-45.stl")
    printing = load_stl(OUT / "print.stl")
    stand_info = inspect_mesh(stand)
    print_info = inspect_mesh(printing)
    if abs(stand_info["volume_cm3"] - print_info["volume_cm3"]) > 0.01:
        raise ValueError("Print orientation changed volume")
    if not np.allclose(sorted(stand_info["dimensions_mm"]), sorted(print_info["dimensions_mm"]), atol=0.01):
        raise ValueError("Print orientation changed dimensions")
    report = {"calibration": calibration, "stand": stand_info, "print": print_info,
              "geometry": geometric_checks(stand, printing, params),
              "static_estimate": static_estimate(stand_info, params, args.stand_mass)}
    OUT.mkdir(parents=True, exist_ok=True)
    report_path = OUT / "verification.json"
    temporary = report_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    temporary.replace(report_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
