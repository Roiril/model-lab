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
            "components": components, "closed": True, "nonmanifold_edges": 0,
            "duplicate_triangles": 0, "inconsistent_winding_edges": 0,
            "euler_characteristic": len(vertices) - len(edges) + len(triangles),
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


def projected_cover_counts(triangles, points, axes=(0, 1)):
    """Count projected triangle interiors without merging coincident surfaces."""
    projected = triangles[:, :, axes]
    a = projected[:, 0]
    v0, v1 = projected[:, 1] - a, projected[:, 2] - a
    det = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    valid = np.abs(det) > 1e-6
    result = []
    for point in points:
        v2 = point - a
        u = np.divide(v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1], det,
                      out=np.zeros(len(det)), where=valid)
        v = np.divide(v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1], det,
                      out=np.zeros(len(det)), where=valid)
        result.append(int(np.sum(valid & (u > 1e-7) & (v > 1e-7) & (u + v < 1 - 1e-7))))
    return np.asarray(result)


def cap_overlap_checks(body, params):
    result = {}
    for label, height in (("bottom", 0.0), ("top", params.BODY_HEIGHT * 1000)):
        selected = body[np.max(np.abs(body[:, :, 2] - height), axis=1) < .01]
        if not len(selected):
            raise ValueError(f"No {label} planar cap faces were found")
        step = max(1, len(selected) // 512)
        points = selected[::step].mean(axis=1)[:, :2]
        counts = projected_cover_counts(selected, points, axes=(0, 1))
        if np.any(counts != 1):
            raise ValueError(f"Coplanar {label} cap overlap: {np.unique(counts, return_counts=True)}")
        result[label] = {"cap_triangles": len(selected), "projection_samples": len(points),
                         "overlapping_samples": 0}
    return result


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
    plane = np.array([[[0, 0, 15], [4, 0, 15], [0, 4, 15]]], dtype=float)
    assert projected_cover_counts(plane, [(1, 1)], axes=(0, 1)).tolist() == [1]
    assert projected_cover_counts(np.concatenate((plane, plane)), [(1, 1)], axes=(0, 1)).tolist() == [2]
    return {"closed_cube_accepted": True, "open_inverted_empty_rejected": 3,
            "inside_and_outside_ray_checks": True,
            "single_and_overlapping_xy_plane_checks": True}


def unrotate_body(triangles, params):
    restored = np.empty_like(triangles)
    restored[:, :, 0] = (triangles[:, :, 0] + triangles[:, :, 1]) / math.sqrt(2)
    restored[:, :, 1] = (triangles[:, :, 1] - triangles[:, :, 0]) / math.sqrt(2) + params.FRAME_DEPTH * 500
    restored[:, :, 2] = triangles[:, :, 2]
    return restored


def print_checks(printing, body, params):
    cross = np.cross(body[:, 1] - body[:, 0], body[:, 2] - body[:, 0])
    lengths = np.linalg.norm(cross, axis=1)
    normals = cross / lengths[:, None]
    bed = body[:, :, 2].max(axis=1) < .001
    underside = (normals[:, 2] < -math.sin(math.radians(45.0))) & ~bed
    if abs(float(printing[:, :, 2].min())) > .001 or not bed.any():
        raise ValueError("Body does not start on the print bed")
    brim = np.ptp(printing, axis=(0, 1))[:2] + 8
    if brim.max() > 248.4:
        raise ValueError("Part and 4 mm brim exceed the 248.4 mm print target")
    return {"downward_support_candidate_triangles": int(underside.sum()),
            "downward_support_candidate_area_cm2": float(lengths[underside].sum() / 200),
            "needs_support": True,
            "maximum_downward_overhang_deg": float(np.degrees(np.arcsin(np.clip(-normals[~bed, 2], 0, 1))).max()),
            "bed_contact_area_cm2": float(lengths[bed].sum() / 200),
            "print_xy_with_4mm_brim_mm": brim.tolist(),
            "note": "The S underside and rear support need slicer support. Counts and areas describe the STL only; slicing and a trial print remain required."}


def geometry_checks(body, assembly, params):
    height = params.BODY_HEIGHT * 1000
    info = inspect_mesh(body)
    expected = np.array([params.FOOT_WIDTH, params.FOOT_DEPTH, params.BODY_HEIGHT]) * 1000
    if not np.allclose(info['dimensions_mm'], expected, atol=.015):
        raise ValueError(f"Body dimensions differ: {info['dimensions_mm']}")
    expected_bounds = np.array([[-params.FOOT_WIDTH * 500, params.FOOT_FRONT_Y * 1000, 0],
                                [params.FOOT_WIDTH * 500,
                                 (params.FOOT_FRONT_Y + params.FOOT_DEPTH) * 1000, height]])
    if not np.allclose(info['bounds_mm'], expected_bounds, atol=.015):
        raise ValueError(f"Body bounds differ: {info['bounds_mm']}")
    if info['euler_characteristic'] != 0:
        raise ValueError("Body must have one closed side opening")

    def curve_point(points, amount):
        p = np.asarray(points, dtype=float) * 1000
        return ((1-amount)**3*p[0] + 3*(1-amount)**2*amount*p[1]
                + 3*(1-amount)*amount**2*p[2] + amount**3*p[3])

    centerline = {}
    for label, points, radius, side_radius in (
            ("main_s", params.S_CURVE_POINTS, params.S_X_RADIUS, params.S_SIDE_RADIUS),
            ("rear_support", params.REAR_CURVE_POINTS, params.REAR_X_RADIUS, params.REAR_SIDE_RADIUS)):
        thicknesses = []
        side_thicknesses = []
        samples = []
        for amount in np.linspace(.08, .92, 9):
            y, z = curve_point(points, amount)
            point = (0, float(y), float(z))
            if not contains(body, point):
                raise ValueError(f"{label} centerline leaves the solid at t={amount}")
            plus = ray_hits(body, point, (1, 0, 0))
            minus = ray_hits(body, point, (-1, 0, 0))
            if not len(plus) or not len(minus):
                raise ValueError(f"{label} core thickness ray missed the surface")
            thicknesses.append(float(plus[0] + minus[0]))
            import mechanics
            tangent = mechanics.bezier_tangent(points, amount)
            normal = np.array([0, -tangent[1], tangent[0]])
            side_plus = ray_hits(body, point, normal)
            side_minus = ray_hits(body, point, -normal)
            if not len(side_plus) or not len(side_minus):
                raise ValueError(f"{label} side thickness ray missed the surface")
            side_thicknesses.append(float(side_plus[0] + side_minus[0]))
            samples.append([float(amount), float(y), float(z)])
        assumed_core = 2 * (radius * 1000 - .8)
        if min(thicknesses) < assumed_core - .1:
            raise ValueError(f"{label} is thinner than the mechanics core assumption")
        assumed_side_core = 2 * (side_radius * 1000 - .8)
        if min(side_thicknesses) < assumed_side_core - .1:
            raise ValueError(f"{label} is thinner in YZ than the mechanics core assumption")
        centerline[label] = {"solid_samples": len(samples), "samples_t_y_z_mm": samples,
                             "actual_core_thickness_x_mm": thicknesses,
                             "minimum_actual_core_thickness_x_mm": min(thicknesses),
                             "mechanics_assumed_core_thickness_x_mm": assumed_core,
                             "actual_core_thickness_normal_yz_mm": side_thicknesses,
                             "minimum_actual_core_thickness_normal_yz_mm": min(side_thicknesses),
                             "mechanics_assumed_core_thickness_normal_yz_mm": assumed_side_core}

    main_mid = curve_point(params.S_CURVE_POINTS, .5)
    rear_mid = curve_point(params.REAR_CURVE_POINTS, .5)
    closed_opening = (main_mid + rear_mid) / 2
    front_concavity = np.array([
        params.REAR_CURVE_POINTS[0][0] * 1000 - 16,
        (params.BODY_HEIGHT - params.TOP_BEAM - params.S_SIDE_RADIUS) * 1000])
    if contains(body, (0, *closed_opening)):
        raise ValueError("Closed side opening is filled")
    if contains(body, (0, *front_concavity)):
        raise ValueError("Front-open concavity is filled")

    # The frame calculation uses a conservative 80 x 10 mm bottom core.
    base_core_points = 0
    bottom_widths = []
    bottom_heights = []
    for y in np.linspace(22, 223, 11):
        for x in (-39.9, 0, 39.9):
            for z in (.05, params.BOTTOM_BEAM * 500,
                      params.BOTTOM_BEAM * 1000 - .05):
                if not contains(body, (x, y, z)):
                    raise ValueError("Assumed bottom beam core contains a void")
                base_core_points += 1
        x_hits = ray_hits(body, (0, y, params.BOTTOM_BEAM * 500), (1, 0, 0))
        x_back = ray_hits(body, (0, y, params.BOTTOM_BEAM * 500), (-1, 0, 0))
        z_hits = ray_hits(body, (0, y, .001), (0, 0, 1))
        if not len(x_hits) or not len(x_back) or not len(z_hits):
            raise ValueError("Bottom core thickness ray missed the surface")
        bottom_widths.append(float(x_hits[0] + x_back[0]))
        bottom_heights.append(float(z_hits[0] + .001))
    if min(bottom_widths) < 80 or min(bottom_heights) < params.BOTTOM_BEAM * 1000:
        raise ValueError("Actual bottom core is smaller than 80 x 10 mm")

    assembly_info = inspect_mesh(assembly, expected_components=2)
    expected = [(2 * params.RAIL_CENTER + params.FOOT_WIDTH) * 1000,
                params.FOOT_DEPTH * 1000, height]
    if not np.allclose(assembly_info['dimensions_mm'], expected, atol=.015):
        raise ValueError("Assembly dimensions differ from parameters")
    assembly_bounds = np.array([[-(params.RAIL_CENTER + params.FOOT_WIDTH/2)*1000,
                                  params.FOOT_FRONT_Y*1000, params.PAD_THICKNESS*1000],
                                 [(params.RAIL_CENTER + params.FOOT_WIDTH/2)*1000,
                                  (params.FOOT_FRONT_Y + params.FOOT_DEPTH)*1000,
                                  (params.PAD_THICKNESS + params.BODY_HEIGHT)*1000]])
    if not np.allclose(assembly_info['bounds_mm'], assembly_bounds, atol=.015):
        raise ValueError("Assembly bounds differ from the two padded support positions")
    lower_points = upper_points = 0
    upper_bottom = (params.PAD_THICKNESS + params.BODY_HEIGHT) * 1000
    for x in (-params.RAIL_CENTER * 1000, params.RAIL_CENTER * 1000):
        for start in (params.BASE_PAD_FRONT_Y * 1000, params.BASE_PAD_REAR_Y * 1000):
            for dx in (-params.BASE_PAD_WIDTH * 500, 0, params.BASE_PAD_WIDTH * 500):
                for dy in (0, params.BASE_PAD_LENGTH * 500, params.BASE_PAD_LENGTH * 1000):
                    hits = ray_hits(assembly, (x + dx, start + dy, 0), (0, 0, 1))
                    if not len(hits) or abs(float(hits[0]) - params.PAD_THICKNESS * 1000) > .01:
                        raise ValueError("Bottom pad is not beneath flat body material")
                    lower_points += 1
        for start in (params.PAD_FRONT_Y * 1000, params.PAD_REAR_Y * 1000):
            for dx in (-params.PAD_WIDTH * 500, 0, params.PAD_WIDTH * 500):
                for dy in (0, params.PAD_LENGTH * 500, params.PAD_LENGTH * 1000):
                    hits = ray_hits(assembly, (x + dx, start + dy, upper_bottom + .1), (0, 0, -1))
                    if not len(hits) or abs(float(hits[0]) - .1) > .01:
                        raise ValueError("Top pad is not on flat body material")
                    upper_points += 1
    if lower_points != 36 or upper_points != 36:
        raise ValueError("Expected 36 ray samples on each pad level")
    return {"centerline_core_checks": centerline,
            "closed_side_opening_sample_y_z_mm": closed_opening.tolist(),
            "front_open_concavity_sample_y_z_mm": front_concavity.tolist(),
            "bottom_beam_solid_core_points": base_core_points,
            "bottom_core_actual_width_x_mm": bottom_widths,
            "bottom_core_actual_height_z_mm": bottom_heights,
            "bottom_core_assumption_mm": [80, params.BOTTOM_BEAM * 1000],
            "flat_bottom_pad_points": lower_points, "flat_top_pad_points": upper_points,
            "height_with_two_1mm_pads_mm": height + 2 * params.PAD_THICKNESS * 1000,
            "one_piece_per_support": True, "closed_side_openings_per_support": 1,
            "front_open_concavities_per_support": 1}


def load_estimate(params, stand_mass):
    import mechanics

    g = 9.80665
    frame = mechanics.sculpture_frame(params)
    if len(frame["cases"]) != 9:
        raise ValueError("The beam-frame calculation must cover nine load cases")
    if frame["calibration"] != {"known_cantilever_deflection_mm": 2.0,
                                 "known_cantilever_stress_mpa": 3.0,
                                 "passed": True}:
        raise ValueError("The beam-frame calibration result changed")
    if frame["maximum_section_stress_mpa"] > 5.0:
        raise ValueError("Assumed beam-frame stress exceeds 5 MPa")
    # Support coordinates use the actual four pad locations, with a 1mm inset.
    half = params.RAIL_CENTER * 1000 + params.BASE_PAD_WIDTH * 500 - 1
    front = params.BASE_PAD_FRONT_Y * 1000 + 1
    rear = (params.BASE_PAD_REAR_Y + params.BASE_PAD_LENGTH) * 1000 - 1
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
    horizontal = []
    force_height = (params.BODY_HEIGHT + 2 * params.PAD_THICKNESS + params.LAPTOP_BASE_THICKNESS) * 1000
    for mass in (3.0, 4.0):
        for dx in (-30, 30):
            for dy in (-60, 60):
                weight = (mass + stand_mass) * g
                cx = mass * g * dx / weight
                cy = center_y + mass * g * dy / weight
                for fx, fy in ((10, 0), (-10, 0), (0, 10), (0, -10)):
                    rx = cx + fx * force_height / weight
                    ry = cy + fy * force_height / weight
                    margin = min(half - abs(rx), ry - front, rear - ry)
                    if margin <= 0:
                        raise ValueError("Horizontal body-level push tips the assumed coupled system")
                    horizontal.append(margin)
    individual = []
    local_half = params.BASE_PAD_WIDTH * 500 - 1
    rail_spacing = params.RAIL_CENTER * 2000
    # There is no joint. Keep a 1 mm allowance for imperfect placement.
    placement_allowance = 1.0
    for mass in (3.0, 4.0):
        for dx in (-30, 30):
            for side in (-1, 1):
                laptop_reaction = mass * g * (.5 + side * dx / rail_spacing)
                total_reaction = laptop_reaction + stand_mass * g / 2
                cop_shift = 5 * force_height / total_reaction
                margin = local_half - cop_shift - placement_allowance
                if margin <= 0:
                    raise ValueError("Lighter individual support tips under assumed 5 N push")
                individual.append({"laptop_mass_kg": mass, "com_side_offset_mm": dx,
                                   "support_side": side, "normal_force_n": total_reaction,
                                   "horizontal_force_n": 5, "cop_shift_mm": cop_shift,
                                   "margin_mm": margin})
    new_area = 2 * half * (rear - front)
    return {"design_laptop_mass_kg": params.LOAD_MASS_KG,
            "beam_frame": frame,
            "contact_polygon_mm": [[-half, front], [half, front], [half, rear], [-half, rear]],
            "assumed_laptop_com_offsets_mm": {"side": 30, "front_rear": 60},
            "vertical_keyboard_press_n": 20, "static_cases_checked": len(stability),
            "minimum_vertical_resultant_margin_mm": min(stability),
            "support_polygon_area_mm2": new_area,
            "individual_contact_half_width_mm": local_half,
            "horizontal_body_push_n": 10, "horizontal_force_height_mm": force_height,
            "horizontal_static_cases_checked": len(horizontal),
            "minimum_horizontal_resultant_margin_mm": min(horizontal),
            "individual_lighter_support_cases": individual,
            "individual_placement_allowance_mm": placement_allowance,
            "minimum_individual_horizontal_margin_mm": min(case['margin_mm'] for case in individual),
            "limitations": "The 1000 MPa modulus and 5 MPa stress threshold are assumptions in a linear two-dimensional beam-frame calculation. It is not FEA or a physical load rating. Whole-system stability assumes a rigid laptop contacts both non-slipping supports. Screen-level pushing, unequal horizontal force, impacts, printed strength, heat, creep and friction remain unverified and require physical tests."}


def main():
    import params
    calibration = calibrate()
    printing = load_stl(OUT / "body.stl")
    assembly = load_stl(ROOT / "exports/laptop-stand-100.stl")
    canonical = unrotate_body(printing, params)
    body_info = inspect_mesh(canonical)
    print_info = inspect_mesh(printing)
    assembly_info = inspect_mesh(assembly, expected_components=2)
    if abs(assembly_info["volume_cm3"] - 2 * body_info["volume_cm3"]) > .02:
        raise ValueError("Assembly volume differs from two identical monolithic bodies")
    density = 1.27
    mass = assembly_info["volume_cm3"] * density / 1000
    report = {"calibration": calibration, "body": body_info, "print": print_info,
              "print_checks": print_checks(printing, canonical, params),
              "cap_surface_checks": cap_overlap_checks(canonical, params),
              "assembly": assembly_info, "geometry": geometry_checks(canonical, assembly, params),
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
