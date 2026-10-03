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


def projected_cover_counts(triangles, points):
    """Count interior coverage in YZ without merging coincident surfaces."""
    yz = triangles[:, :, 1:]
    a = yz[:, 0]
    v0, v1 = yz[:, 1] - a, yz[:, 2] - a
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


def exterior_overlap_checks(body, params):
    checked = 0
    for side in (-1, 1):
        plane_x = side * params.UPPER_WIDTH * 500
        selected = body[np.max(np.abs(body[:, :, 0] - plane_x), axis=1) < .01]
        if not len(selected):
            raise ValueError("No upper planar exterior faces were found")
        # Include the centroid of each nondegenerate projected face and an
        # independent regular grid across the two opening crowns.
        centers = selected.mean(axis=1)[:, 1:]
        grid = np.array([(y, z) for y in np.linspace(20.123, 224.123, 31)
                         for z in np.linspace(70.157, 90.157, 41)])
        points = np.concatenate((centers, grid))
        counts = projected_cover_counts(selected, points)
        if np.any(counts > 1):
            raise ValueError(f"Coplanar exterior overlap on side {side}: {int(np.sum(counts > 1))}")
        checked += len(points)
    return {"planar_side_projection_samples": checked, "overlapping_exterior_samples": 0}


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
    plane = np.array([[[15, 0, 0], [15, 4, 0], [15, 0, 4]]], dtype=float)
    assert projected_cover_counts(plane, [(1, 1)]).tolist() == [1]
    assert projected_cover_counts(np.concatenate((plane, plane)), [(1, 1)]).tolist() == [2]
    return {"closed_cube_accepted": True, "open_inverted_empty_rejected": 3,
            "inside_and_outside_ray_checks": True,
            "single_and_overlapping_plane_checks": True}


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
    steep = (normals[:, 2] < -math.sin(math.radians(45.5))) & ~bed
    accepted = np.zeros(len(body), dtype=bool)
    crowns = []
    for center in params.HOLE_CENTERS:
        y = center * 1000
        region = ((np.abs(body[:, :, 1] - y).max(axis=1) <= 7.0) &
                  (body[:, :, 2].min(axis=1) >= params.HOLE_PEAK * 1000 - 8))
        accepted |= region
        crown = body[steep & region]
        if len(crown):
            low = crown.min(axis=(0, 1))
            high = crown.max(axis=(0, 1))
            span = float(high[1] - low[1])
            if span > 14.0:
                raise ValueError("Rounded crown bridge exceeds 14 mm")
            crowns.append({"center_y_mm": y, "downward_triangles": len(crown),
                           "projected_bridge_span_y_mm": span,
                           "z_bounds_mm": [float(low[2]), float(high[2])]})
    unsupported = steep & ~accepted
    if unsupported.any():
        bounds = body[unsupported].min(axis=(0, 1)), body[unsupported].max(axis=(0, 1))
        raise ValueError(f"Steep faces outside the two short crowns: {int(unsupported.sum())}, {bounds}")
    if abs(float(printing[:, :, 2].min())) > .001 or not bed.any():
        raise ValueError("Body does not start on the print bed")
    brim = np.ptp(printing, axis=(0, 1))[:2] + 8
    if brim.max() > 256:
        raise ValueError("Part and 4 mm brim exceed the assumed 256 mm bed")
    return {"steep_faces_outside_short_crowns": int(unsupported.sum()),
            "short_rounded_crowns": crowns,
            "maximum_downward_overhang_deg": float(np.degrees(np.arcsin(np.clip(-normals[~bed, 2], 0, 1))).max()),
            "bed_contact_area_cm2": float(lengths[bed].sum() / 200),
            "print_xy_with_4mm_brim_mm": brim.tolist(),
            "note": "Two short rounded crowns require bridge tuning. This geometry check does not replace slicing or a trial print."}


def geometry_checks(body, assembly, params):
    height = params.BODY_HEIGHT * 1000
    depth = params.FRAME_DEPTH * 1000
    info = inspect_mesh(body)
    expected = np.array([params.FOOT_WIDTH, params.FOOT_DEPTH, params.BODY_HEIGHT]) * 1000
    if not np.allclose(info['dimensions_mm'], expected, atol=.015):
        raise ValueError(f"Body dimensions differ: {info['dimensions_mm']}")
    if info['euler_characteristic'] != -2:
        raise ValueError("Body must be one connected solid with exactly two through openings")
    assert contains(body, (0, depth / 2, height / 2))
    assert contains(body, (0, depth / 2, height - 4))
    for center in params.HOLE_CENTERS:
        assert not contains(body, (0, center * 1000, 45))
    top, bottom, width, pier = [], [], [], []
    for center in params.HOLE_CENTERS:
        for y in np.linspace(center * 1000 - 20, center * 1000 + 20, 9):
            for x in (-12, 0, 12):
                hits = ray_hits(body, (x, y, height + .01), (0, 0, -1))
                if len(hits) < 2:
                    raise ValueError("Missing upper beam surfaces")
                top.append(float(hits[1] - hits[0]))
            for x in (-40, 0, 40):
                hits = ray_hits(body, (x, y, -.01), (0, 0, 1))
                if len(hits) < 2:
                    raise ValueError("Missing lower beam surfaces")
                bottom.append(float(hits[1] - hits[0]))
    for y in (40, 65, 90, 122.5, 155, 181, 205):
        hits = ray_hits(body, (-100, y, height - 4), (1, 0, 0))
        if len(hits) < 2:
            raise ValueError("Missing upper section width")
        width.append(float(hits[1] - hits[0]))
    for z in np.linspace(25, 65, 9):
        plus = ray_hits(body, (0, depth / 2, z), (0, 1, 0))
        minus = ray_hits(body, (0, depth / 2, z), (0, -1, 0))
        if not len(plus) or not len(minus):
            raise ValueError("Missing central pier")
        pier.append(float(plus[0] + minus[0]))
    minima = {"top_beam": min(top), "bottom_beam": min(bottom),
              "upper_width": min(width), "central_pier_center_section": min(pier)}
    limits = {"top_beam": params.TOP_BEAM * 1000, "bottom_beam": params.BOTTOM_BEAM * 1000,
              "upper_width": params.FRAME_WIDTH * 1000, "central_pier_center_section": 23}
    if any(minima[name] < limit - .03 for name, limit in limits.items()):
        raise ValueError(f"A sampled load section is too thin: {minima}")
    # The bottom beam calculation uses an 80 mm-wide, 12 mm-high central
    # rectangular core. Confirm actual solid material at its limiting faces.
    base_core_points = 0
    for y in np.linspace(22, 223, 11):
        for x in (-39.9, 0, 39.9):
            for z in (.05, 6, params.BOTTOM_BEAM * 1000 - .05):
                if not contains(body, (x, y, z)):
                    raise ValueError("Assumed bottom beam core contains a void")
                base_core_points += 1
    assembly_info = inspect_mesh(assembly, expected_components=2)
    expected = [(2 * params.RAIL_CENTER + params.FOOT_WIDTH) * 1000,
                params.FOOT_DEPTH * 1000, height]
    if not np.allclose(assembly_info['dimensions_mm'], expected, atol=.015):
        raise ValueError("Assembly dimensions differ from parameters")
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
    return {"minimum_sampled_sections_mm": minima, "bottom_beam_solid_core_points": base_core_points,
            "flat_bottom_pad_points": lower_points, "flat_top_pad_points": upper_points,
            "height_with_two_1mm_pads_mm": height + 2 * params.PAD_THICKNESS * 1000,
            "one_piece_per_support": True, "through_openings_per_support": 2}


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
    # A central pier also transfers load into the bottom beam. The rectangular
    # 80 x 12 mm core is checked for actual solid material by geometry_checks.
    base_span = (params.BASE_PAD_REAR_Y - params.BASE_PAD_FRONT_Y) * 1000
    base_width = 80.0
    base_thickness = params.BOTTOM_BEAM * 1000
    base_force = params.LOAD_MASS_KG * g + 20
    base_inertia = base_width * base_thickness ** 3 / 12
    base_section = base_width * base_thickness ** 2 / 6
    base_stress = base_force * base_span / (4 * base_section)
    base_deflection = base_force * base_span ** 3 / (48 * modulus * base_inertia)
    if base_stress > allowable or base_deflection > 1.5:
        raise ValueError("Assumed bottom beam check failed")
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
    return {"design_laptop_mass_kg": params.LOAD_MASS_KG, "beam_span_mm": span,
            "assumed_modulus_mpa": modulus, "assumed_stress_threshold_mpa": allowable,
            "bottom_beam_case": {"span_mm": base_span, "width_mm": base_width,
                                 "thickness_mm": base_thickness, "load_n": base_force,
                                 "bending_stress_mpa": base_stress,
                                 "midspan_deflection_mm": base_deflection},
            "beam_cases": cases, "contact_polygon_mm": [[-half, front], [half, front], [half, rear], [-half, rear]],
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
            "limitations": "Assumed solid-beam statics only. Whole-system polygon assumes a rigid laptop contacts both non-slipping supports. Horizontal cases are at keyboard height, split 5 N per support, separately from vertical pressing. Screen-level pushing, unequal horizontal force, impacts, printed strength, heat, creep and friction need physical tests."}


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
              "exterior_surface_checks": exterior_overlap_checks(canonical, params),
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
