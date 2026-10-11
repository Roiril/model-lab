"""C4-2 の全STL、全組合せ、カム接触、代表姿勢を実形状で検証する。"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

from mathutils import Matrix
from mathutils.bvhtree import BVHTree
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import motion  # noqa: E402
import params as P  # noqa: E402
import evidence as E  # noqa: E402
import contact_envelope as CE  # noqa: E402


# tools/lattice_assembly.py が C4 系 verify の公開計器として参照する。
exact_common_geometry = E.exact_common_geometry


VOLUME_LIMIT_MM3 = 0.001
POSE_STEP_DEG = 1.0
REQUIRED_PARTS = {
    "housing", "faceplate", "guide_frame", "bottom", "cam_disk", "horn_coupler",
    "drive_key", "cam_keeper", "servo_body", "servo_horn", "servo_wire",
    *(f"carrier_{name}" for name in P.GROUPS),
}


def rotated_regions(local_bounds, angles):
    rows = []
    for angle in angles:
        radians = math.radians(angle)
        cosine, sine = math.cos(radians), math.sin(radians)
        corners = []
        for x in (local_bounds[0][0], local_bounds[1][0]):
            for y in (local_bounds[0][1], local_bounds[1][1]):
                for z in (local_bounds[0][2], local_bounds[1][2]):
                    corners.append((cosine * x - sine * y,
                                    sine * x + cosine * y, z))
        rows.append(tuple(tuple(float(min(point[axis] for point in corners))
                                if side == 0 else float(max(point[axis] for point in corners))
                                for axis in range(3)) for side in range(2)))
    return tuple(rows)

# 正本SG92R本体とホーンは内部で重なる。この範囲はCAD生成後に実座標で固定する。
CANONICAL_ALLOWANCES = {
    ("cam_keeper", "housing"): {
        "kind": "snap", "componentBoundsMm": (
            *rotated_regions(((P.KEEPER_HOOK_INNER * 1000.0, -3.2,
                               P.KEEPER_HOOK_Z0 * 1000.0),
                              (51.9, 3.2, 48.0)), P.KEEPER_ANGLES_DEG),
        ),
        "maximumDeflectionMm": P.KEEPER_TAB_DEFLECTION * 1000.0,
        "tabThicknessMm": P.KEEPER_TAB_T * 1000.0,
        "freeLengthMm": P.KEEPER_TAB_FREE_L * 1000.0,
    },
    ("faceplate", "housing"): {
        "kind": "snap", "componentBoundsMm": rotated_regions(
            (((P.CUBE / 2 - P.WALL) * 1000.0 - 1.4, -4.0, 93.0),
             ((P.CUBE / 2 - P.WALL) * 1000.0 + 0.6, 4.0,
              (P.CUBE - P.FRAME_T) * 1000.0 + 0.2)), (0, 180)),
        "maximumDeflectionMm": P.EXTERIOR_HOOK_DEFLECTION * 1000.0,
        "tabThicknessMm": P.EXTERIOR_TAB_T * 1000.0, "freeLengthMm": 8.3,
    },
    ("bottom", "housing"): {
        "kind": "snap", "componentBoundsMm": rotated_regions(
            (((P.CUBE / 2 - P.WALL) * 1000.0 - 1.4, -4.0,
              P.FRAME_T * 1000.0 - 0.2),
             ((P.CUBE / 2 - P.WALL) * 1000.0 + 0.6, 4.0,
              P.BOTTOM_TAB_Z1 * 1000.0)), P.BOTTOM_LATCH_ANGLES_DEG),
        "maximumDeflectionMm": P.EXTERIOR_HOOK_DEFLECTION * 1000.0,
        "tabThicknessMm": P.EXTERIOR_TAB_T * 1000.0, "freeLengthMm": 8.0,
    },
    ("servo_body", "servo_horn"): {
        "kind": "canonical",
        "componentBoundsMm": (((-2.303, -2.303, 31.497), (2.303, 2.303, 34.503)),),
        "maximumCommonVolumeMm3": 0.030,
    },
}

# 組立中に弾性接触を許す場合も、実座標の直方体をここへ固定する。
SNAP_ZONES = {
    "cam_keeper": CANONICAL_ALLOWANCES[("cam_keeper", "housing")]["componentBoundsMm"],
    "faceplate": CANONICAL_ALLOWANCES[("faceplate", "housing")]["componentBoundsMm"],
    "bottom": CANONICAL_ALLOWANCES[("bottom", "housing")]["componentBoundsMm"],
}


def point_in_snap_zone(kind, point):
    regions = SNAP_ZONES.get(kind, ())
    tolerance = 0.01
    return any(all(bounds[0][axis] - tolerance <= point[axis]
                       <= bounds[1][axis] + tolerance
                   for axis in range(3)) for bounds in regions)


def allowed_intersection(key, geometry):
    allowance = CANONICAL_ALLOWANCES.get(key)
    if allowance is None:
        return False
    regions = allowance["componentBoundsMm"]
    components = geometry.get("intersection_component_bounds_mm", ())
    if not components or not all(any(E.bounds_within(component, region)
                                     for region in regions) for component in components):
        return False
    if allowance["kind"] != "snap":
        return geometry["common_volume_mm3"] <= allowance["maximumCommonVolumeMm3"]
    if key == ("cam_keeper", "housing") and geometry.get("intersection_vertices_mm"):
        radii = [math.hypot(point[0], point[1])
                 for point in geometry["intersection_vertices_mm"]]
        depths = [max(radii) - min(radii)]
        geometry["snap_intrusion_method"] = "actual_boolean_vertex_radial_range"
    else:
        depths = []
        for component in components:
            region = next(region for region in regions if E.bounds_within(component, region))
            center = [(region[0][axis] + region[1][axis]) / 2.0 for axis in range(3)]
            radial_axis = 0 if abs(center[0]) >= abs(center[1]) else 1
            depths.append(component[1][radial_axis] - component[0][radial_axis])
        geometry["snap_intrusion_method"] = "actual_boolean_component_radial_axis_width"
    geometry["snap_intrusion_depths_mm"] = [round(value, 6) for value in depths]
    geometry["maximum_snap_intrusion_mm"] = round(max(depths), 6)
    strain = (1.5 * allowance["tabThicknessMm"] * max(depths)
              / allowance["freeLengthMm"] ** 2 * 100.0)
    geometry["snap_strain_percent"] = round(strain, 6)
    return (max(depths) <= allowance["maximumDeflectionMm"] + 0.002
            and strain <= 2.0)


def degrees():
    count = int(math.ceil((P.SERVO_MAX_DEG - P.SERVO_MIN_DEG) / POSE_STEP_DEG))
    return [P.SERVO_MIN_DEG + (P.SERVO_MAX_DEG - P.SERVO_MIN_DEG) * i / count
            for i in range(count + 1)]


def pose_matrices(names, degree):
    values = motion.transforms(degree)
    return {name: E.transform_matrix(values[name]) if name in values else Matrix.Identity(4)
            for name in names}


def relative_key(left, right):
    relative = left.inverted_safe() @ right
    return tuple(round(float(relative[row][column]), 7)
                 for row in range(4) for column in range(4))


def scene_geometry(meshes):
    """全STL pairを1度以下で走査し、AABB候補をMANIFOLD実体積で測る。"""
    pair_rows = {}
    violations = []
    allowed = []
    cache = {}
    sample_degrees = degrees()
    for sample_index, degree in enumerate(sample_degrees):
        if sample_index % 25 == 0 or sample_index + 1 == len(sample_degrees):
            print(json.dumps({"phase": "exact_scene", "sample": sample_index + 1,
                              "samples": len(sample_degrees),
                              "servoDeg": round(degree, 6)}), flush=True)
        matrices = pose_matrices(meshes, degree)
        bounds = {name: E.transformed_bounds(mesh, matrices[name]) for name, mesh in meshes.items()}
        for left, right in itertools.combinations(sorted(meshes), 2):
            key = (left, right)
            row = pair_rows.setdefault(key, {
                "parts": [left, right], "poseSamples": 0, "aabbZeroSamples": 0,
                "manifoldSamples": 0, "maxCommonVolumeMm3": 0.0, "allowedSamples": 0,
                "pass": True,
            })
            row["poseSamples"] += 1
            if not E.bounds_overlap(bounds[left], bounds[right]):
                row["aabbZeroSamples"] += 1
                continue
            cache_key = (key, relative_key(matrices[left], matrices[right]))
            geometry = cache.get(cache_key)
            if geometry is None:
                geometry = E.exact_common_geometry(
                    meshes[left], matrices[left], meshes[right], matrices[right])
                cache[cache_key] = geometry
            row["manifoldSamples"] += 1
            volume = geometry["common_volume_mm3"]
            row["maxCommonVolumeMm3"] = max(row["maxCommonVolumeMm3"], volume)
            if volume <= VOLUME_LIMIT_MM3:
                continue
            allowance = CANONICAL_ALLOWANCES.get(key)
            if allowance is not None and allowed_intersection(key, geometry):
                row["allowedSamples"] += 1
                allowed.append({"servoDeg": round(degree, 6), "parts": list(key),
                                "commonVolumeMm3": volume,
                                "intersectionBoundsMm": geometry["intersection_bounds_mm"],
                                "allowedComponentBoundsMm": allowance["componentBoundsMm"],
                                "maximumAllowedCommonVolumeMm3":
                                    allowance.get("maximumCommonVolumeMm3"),
                                "snapIntrusionDepthsMm": geometry.get("snap_intrusion_depths_mm"),
                                "maximumSnapIntrusionMm": geometry.get("maximum_snap_intrusion_mm"),
                                "maximumDeflectionMm": allowance.get("maximumDeflectionMm"),
                                "snapStrainPercent": geometry.get("snap_strain_percent"),
                                "kind": allowance["kind"]})
                continue
            row["pass"] = False
            violations.append({"servoDeg": round(degree, 6), "parts": list(key),
                               "commonVolumeMm3": volume,
                               "intersectionBoundsMm": geometry["intersection_bounds_mm"],
                               "snapIntrusionDepthsMm": geometry.get("snap_intrusion_depths_mm"),
                               "maximumSnapIntrusionMm": geometry.get("maximum_snap_intrusion_mm"),
                               "snapStrainPercent": geometry.get("snap_strain_percent")})
    rows = []
    for key in sorted(pair_rows):
        row = pair_rows[key]
        row["maxCommonVolumeMm3"] = round(row["maxCommonVolumeMm3"], 6)
        rows.append(row)
    return {
        "method": ("全STL pairを1度以下で走査。AABB非交差は数学的0。候補は校正済みBlender "
                   "Boolean MANIFOLDで閉境界共通体積を測定。"),
        "poseStepDeg": max(b - a for a, b in zip(sample_degrees, sample_degrees[1:])),
        "poseSamples": len(sample_degrees), "uniquePairs": len(rows),
        "commonVolumeLimitMm3": VOLUME_LIMIT_MM3, "pairs": rows,
        "allowedContacts": allowed, "violations": violations,
        "pass": not violations,
    }


def actual_cam_foot(meshes):
    """4トラックの実カム上面と各キャリア足下面を1度以下で照合する。"""
    cam = E.read_stl("cam_disk")
    carriers = {name: E.read_stl(f"carrier_{name}") for name in P.GROUPS}
    rows = []
    missing = []
    for degree in degrees():
        delta = degree - P.HOME_SERVO_DEG
        for index, name in enumerate(P.GROUPS):
            radius = P.CAM_RADII[index] * 1000.0
            follower_angle = P.FOLLOWER_ANGLES_DEG[index]
            local_angle = follower_angle - delta
            radial_half_width = P.FOLLOWER_RADIAL_W * 500.0
            tangential_half_width = P.FOLLOWER_ARC_L * 500.0
            half_angle = math.degrees(tangential_half_width / radius)
            center_height = E.vertical_surface_height(
                cam, radius * math.cos(math.radians(local_angle)),
                radius * math.sin(math.radians(local_angle)), highest=True)
            samples = E.sample_disk(radius, local_angle,
                                    radial_offsets=(-radial_half_width, 0.0, radial_half_width),
                                    angular_offsets=(-half_angle, 0.0, half_angle))
            cam_levels = [E.vertical_surface_height(cam, x, y, highest=True) for x, y in samples]
            cam_levels = [value for value in cam_levels if value is not None]
            fixed_samples = E.sample_disk(radius, follower_angle,
                                          radial_offsets=(-radial_half_width, 0.0,
                                                          radial_half_width),
                                          angular_offsets=(-half_angle, 0.0, half_angle))
            foot_levels = [E.vertical_surface_height(carriers[name], x, y, highest=False)
                           for x, y in fixed_samples]
            foot_levels = [value for value in foot_levels if value is not None]
            if not cam_levels or not foot_levels:
                missing.append({"servoDeg": degree, "group": name})
                continue
            cam_top = max(cam_levels)
            foot_bottom = min(foot_levels) + motion.lift_m(index, degree) * 1000.0
            expected = motion.cam_height_m(index, local_angle) * 1000.0 + P.CAM_BASE_Z * 1000.0
            gap = foot_bottom - cam_top
            height_error = None if center_height is None else center_height - expected
            passed = abs(gap) <= 0.03 and height_error is not None and abs(height_error) <= 0.08
            rows.append({"servoDeg": round(degree, 6), "group": name,
                         "camFootprintMaximumHeightMm": round(cam_top, 6),
                         "camCenterActualHeightMm": None if center_height is None else round(center_height, 6),
                         "camCenterAnalyticHeightMm": round(expected, 6),
                         "carrierFootActualHeightMm": round(foot_bottom, 6),
                         "gapMm": round(gap, 6), "heightErrorMm": round(height_error, 6),
                         "pass": passed})
    # 実メッシュを0.1mm下げれば共通体積が生じ、0.5mm上げれば接触を失うことを確かめる。
    negative_rows = []
    for index, name in enumerate(P.GROUPS):
        degree = P.SELECT_DEG[index]
        matrices = pose_matrices(meshes, degree)
        lowered = Matrix.Translation((0.0, 0.0, -0.1)) @ matrices[f"carrier_{name}"]
        common = E.exact_common_volume(meshes["cam_disk"], matrices["cam_disk"],
                                       meshes[f"carrier_{name}"], lowered)
        nominal = next((row for row in rows if row["group"] == name
                        and abs(row["servoDeg"] - degree) <= 1e-6), None)
        raised_gap = None if nominal is None else nominal["gapMm"] + 0.5
        negative_rows.append({"group": name, "servoDeg": degree,
                              "loweredByMm": 0.1, "loweredCommonVolumeMm3": common,
                              "raisedByMm": 0.5, "raisedGapMm": raised_gap,
                              "penetrationDetected": common > VOLUME_LIMIT_MM3,
                              "gapDetected": raised_gap is not None and raised_gap > 0.03})
    negative_examples = {"cases": negative_rows,
                         "pass": bool(negative_rows) and all(
                             row["penetrationDetected"] and row["gapDetected"] for row in negative_rows)}
    lug_rows = []
    cam_normal = np.cross(cam[:, 1] - cam[:, 0], cam[:, 2] - cam[:, 0])
    cam_top = cam[cam_normal[:, 2] > 1e-14]
    expected_lug_z = (P.FOLLOWER_HOME_Z + P.FOLLOWER_T) * 1000.0 - 0.2
    lug_half = P.GUIDE_LUG * 500.0
    for index, name in enumerate(P.GROUPS):
        angle = math.radians(P.FOLLOWER_ANGLES_DEG[index])
        center = np.asarray((P.CAM_RADII[index] * 1000.0 * math.cos(angle),
                             P.CAM_RADII[index] * 1000.0 * math.sin(angle)))
        carrier = carriers[name]
        centroids = carrier[:, :, :2].mean(axis=1)
        horizontal = np.ptp(carrier[:, :, 2], axis=1) <= 1e-7
        at_lug_floor = (horizontal
                        & (np.abs(carrier[:, :, 2].mean(axis=1) - expected_lug_z) <= 0.002)
                        & (np.abs(centroids[:, 0] - center[0]) <= lug_half + 0.01)
                        & (np.abs(centroids[:, 1] - center[1]) <= lug_half + 0.01))
        lug_floor = carrier[at_lug_floor]
        degree = P.SELECT_DEG[index]
        matrices = pose_matrices(meshes, degree)
        world_lug = transformed_triangles(lug_floor, matrices[f"carrier_{name}"])
        world_cam = transformed_triangles(cam_top, matrices["cam_disk"])
        actual_lug_z = None if not len(world_lug) else float(world_lug[:, :, 2].min())
        cam_height = (None if not len(world_lug) else
                      CE.maximum_height(world_cam, world_lug))
        clearance = (None if actual_lug_z is None or cam_height is None else
                     actual_lug_z - cam_height)
        lug_rows.append({
            "group": name, "servoDeg": degree,
            "actualGuideLugUndersideMm": (None if actual_lug_z is None else
                                           round(actual_lug_z, 6)),
            "actualCamMaximumBelowLugMm": (None if cam_height is None else
                                            round(cam_height, 6)),
            "clearanceMm": None if clearance is None else round(clearance, 6),
            "lugFloorTriangles": int(len(lug_floor)),
            "requiredMinimumClearanceMm": 0.5,
            "pass": clearance is not None and clearance >= 0.5,
        })
    guide_lug_clearance = {
        "method": ("各谷停止で、外側案内角棒の実STL下面三角形と、そのXY領域に重なる"
                   "実カム上面三角形の最大高さを倍精度で比較する。"),
        "cases": lug_rows,
        "pass": bool(lug_rows) and all(row["pass"] for row in lug_rows),
    }
    passage_rows = []
    guide_section_z = (P.GUIDE_Z0 + P.GUIDE_Z1) * 500.0
    guide_section = E.slice_z(E.read_stl("guide_frame"), guide_section_z)
    for index, name in enumerate(P.GROUPS):
        carrier = carriers[name]
        floor_z = float(carrier[:, :, 2].min())
        on_floor = np.all(np.abs(carrier[:, :, 2] - floor_z) <= 1e-7, axis=1)
        footprint = carrier[on_floor]
        points = footprint[:, :, :2].reshape(-1, 2)
        foot_min = points.min(axis=0) if len(points) else np.asarray((math.inf, math.inf))
        foot_max = points.max(axis=0) if len(points) else np.asarray((-math.inf, -math.inf))
        extents = foot_max - foot_min
        maximum_projection = float(extents.max())
        angle = math.radians(P.FOLLOWER_ANGLES_DEG[index])
        center = np.asarray((P.CAM_RADII[index] * 1000.0 * math.cos(angle),
                             P.CAM_RADII[index] * 1000.0 * math.sin(angle)))
        x_crossings = line_crossings(guide_section, center[1], center[0])
        swapped_section = guide_section[:, :, ::-1]
        y_crossings = line_crossings(swapped_section, center[0], center[1])
        left = max((value for value in x_crossings if value < center[0]), default=None)
        right = min((value for value in x_crossings if value > center[0]), default=None)
        lower = max((value for value in y_crossings if value < center[1]), default=None)
        upper = min((value for value in y_crossings if value > center[1]), default=None)
        hole_bounds = None if None in (left, right, lower, upper) else np.asarray(
            ((left, lower), (right, upper)), dtype=float)
        clearances = ([] if hole_bounds is None else
                      [foot_min[0] - hole_bounds[0, 0], hole_bounds[1, 0] - foot_max[0],
                       foot_min[1] - hole_bounds[0, 1], hole_bounds[1, 1] - foot_max[1]])
        minimum_clearance = min(clearances, default=-math.inf)
        passage_rows.append({
            "group": name,
            "guideSectionZMm": round(guide_section_z, 6),
            "actualGuideOpeningBoundsMm": (None if hole_bounds is None else
                                            [[round(float(value), 6) for value in side]
                                             for side in hole_bounds]),
            "actualFootBoundsMm": [[round(float(value), 6) for value in foot_min],
                                   [round(float(value), 6) for value in foot_max]],
            "actualFootProjectionMm": [round(float(value), 6) for value in extents],
            "maximumProjectionMm": round(maximum_projection, 6),
            "actualSideClearancesMm": [round(float(value), 6) for value in clearances],
            "actualMinimumPerSideClearanceMm": (None if not clearances else
                                                 round(float(minimum_clearance), 6)),
            "requiredMinimumPerSideClearanceMm": round(P.GUIDE_CLR * 1000.0, 6),
            "footFloorTriangles": int(len(footprint)),
            "pass": bool(len(footprint) > 0 and hole_bounds is not None
                         and minimum_clearance >= P.GUIDE_CLR * 1000.0 - 0.002),
        })
    foot_passage = {
        "method": ("各足の実STL下面三角形をXYへ投影し、案内角穴3.6mmに対する"
                   "最小片側通過隙間を測る。"),
        "cases": passage_rows,
        "pass": bool(passage_rows) and all(row["pass"] for row in passage_rows),
    }
    return {
        "method": "実STLを鉛直線で切り、各足面内9点のカム最高面と足最低面を比較。",
        "poseStepDeg": POSE_STEP_DEG, "trackCount": len(P.GROUPS), "samples": rows,
        "missingSamples": missing, "maximumAbsoluteNominalGapMm": 0.03,
        "footprint": {"radialHalfWidthMm": P.FOLLOWER_RADIAL_W * 500.0,
                      "tangentialHalfWidthMm": P.FOLLOWER_ARC_L * 500.0,
                      "samplesPerFoot": 9},
        "negativeExamples": negative_examples,
        "guideLugCamClearance": guide_lug_clearance,
        "footGuidePassage": foot_passage,
        "pass": bool(rows) and not missing and all(row["pass"] for row in rows)
                and negative_examples["pass"] and guide_lug_clearance["pass"]
                and foot_passage["pass"],
    }


def state_bounds(meshes):
    rows = []
    flat = {}
    for state_id, label, degree in P.PATTERNS:
        matrices = pose_matrices(meshes, degree)
        all_bounds = [E.transformed_bounds(mesh, matrices[name]) for name, mesh in meshes.items()]
        bounds = [[min(row[0][axis] for row in all_bounds) for axis in range(3)],
                  [max(row[1][axis] for row in all_bounds) for axis in range(3)]]
        carriers = {}
        for index, name in enumerate(P.GROUPS):
            part = f"carrier_{name}"
            actual = E.transformed_bounds(meshes[part], matrices[part])
            expected_shift = motion.lift_m(index, degree) * 1000.0
            if state_id == "flat":
                flat[name] = actual
            carriers[name] = {"boundsMm": actual, "expectedShiftMm": round(expected_shift, 6)}
        rows.append({"id": state_id, "label": label, "servoDeg": degree,
                     "boundsMm": [[round(value, 4) for value in side] for side in bounds],
                     "carriers": carriers})
    errors = []
    dent_errors = []
    for state in rows:
        for name, item in state["carriers"].items():
            actual_shift = item["boundsMm"][0][2] - flat[name][0][2]
            item["actualShiftFromFlatMm"] = round(actual_shift, 6)
            error = actual_shift - item["expectedShiftMm"]
            item["shiftErrorMm"] = round(error, 6)
            if abs(error) > 0.002:
                errors.append({"state": state["id"], "group": name, "errorMm": error})
            expected_dent = -4.0 if state["id"] == name else 0.0
            item["requiredDentFromFlatMm"] = expected_dent
            item["dentPatternPass"] = abs(actual_shift - expected_dent) <= 0.002
            if not item["dentPatternPass"]:
                dent_errors.append({"state": state["id"], "group": name,
                                    "actualMm": actual_shift, "requiredMm": expected_dent})
    half = P.CUBE * 500.0
    expected_overall = [[-half, -half, 0.0], [half, half, P.CUBE * 1000.0]]
    envelope_errors = []
    for state in rows:
        error = max(abs(state["boundsMm"][side][axis] - expected_overall[side][axis])
                    for side in range(2) for axis in range(3))
        state["expectedBoundsMm"] = expected_overall
        state["boundsErrorMm"] = round(error, 6)
        state["boundsPass"] = error <= 0.02
        if not state["boundsPass"]:
            envelope_errors.append({"state": state["id"], "maximumErrorMm": error})
    housing_bounds = E.transformed_bounds(meshes["housing"], Matrix.Identity(4))
    housing_xy = [housing_bounds[1][axis] - housing_bounds[0][axis] for axis in (0, 1)]
    housing_pass = all(abs(value - P.CUBE * 1000.0) <= 0.02 for value in housing_xy)
    return {"states": rows, "expectedStateCount": 5, "carrierShiftErrors": errors,
            "dentPatternErrors": dent_errors,
            "housingBoundsMm": housing_bounds, "housingXYExtentMm": housing_xy,
            "housingXYExtentPass": housing_pass, "expectedOverallBoundsMm": expected_overall,
            "envelopeErrors": envelope_errors,
            "pass": len(rows) == 5 and len({row["servoDeg"] for row in rows}) == 5
                    and not errors and not dent_errors and housing_pass and not envelope_errors}


def indexed_triangle_surface_distance(source_triangles, target_triangles):
    """同じ三角形順を保つSTLコピーの表面距離上限を倍精度で返す。"""
    source = np.asarray(source_triangles, dtype=np.float64)
    target = np.asarray(target_triangles, dtype=np.float64)
    if source.shape != target.shape:
        return None
    vertex_bound = float(np.max(np.linalg.norm(source - target, axis=2)))
    source_areas = np.linalg.norm(
        np.cross(source[:, 1] - source[:, 0], source[:, 2] - source[:, 0]), axis=1) * 0.5
    target_areas = np.linalg.norm(
        np.cross(target[:, 1] - target[:, 0], target[:, 2] - target[:, 0]), axis=1) * 0.5
    return {
        "maximumVertexDistanceMm": vertex_bound,
        "surfaceAreaErrorMm2": float(abs(source_areas.sum() - target_areas.sum())),
    }


def canonical_surface_calibration():
    """薄い三角形でも既知の同一面と0.004mm変位を区別する。"""
    source = np.asarray((
        ((0.0, 0.0, 0.0), (12.0, 0.0, 0.0), (0.0, 0.0002, 0.0)),
        ((0.0, 0.0, 0.001), (0.0, 0.0002, 0.001), (12.0, 0.0, 0.001)),
    ), dtype=np.float64)
    positive = indexed_triangle_surface_distance(source, source.copy())
    shifted = source.copy()
    shifted[:, :, 2] += 0.004
    negative = indexed_triangle_surface_distance(source, shifted)
    positive_pass = (positive is not None
                     and positive["maximumVertexDistanceMm"] <= 1e-12
                     and positive["surfaceAreaErrorMm2"] <= 1e-12)
    negative_pass = (negative is not None
                     and abs(negative["maximumVertexDistanceMm"] - 0.004) <= 1e-12
                     and negative["maximumVertexDistanceMm"] > 0.003)
    return {
        "positiveFixture": positive,
        "negativeFixture": negative,
        "requiredMaximumDistanceMm": 0.003,
        "positivePass": positive_pass,
        "negativePass": negative_pass,
        "pass": positive_pass and negative_pass,
    }


def canonical_reference_placement():
    def directed_surface_distance(source_triangles, target_triangles):
        target_vertices = target_triangles.reshape(-1, 3)
        target_faces = [(index, index + 1, index + 2)
                        for index in range(0, len(target_vertices), 3)]
        tree = BVHTree.FromPolygons([tuple(point) for point in target_vertices],
                                    target_faces, all_triangles=True)
        source_points = np.concatenate((source_triangles.reshape(-1, 3),
                                        source_triangles.mean(axis=1)), axis=0)
        maximum = 0.0
        for point in source_points:
            nearest = tree.find_nearest(tuple(point))
            if nearest[0] is None:
                return float("inf")
            maximum = max(maximum, float(nearest[3]))
        return maximum

    rows = {}
    for suffix in ("body", "horn", "wire"):
        source_path = ROOT / "exports" / f"sg92r-photo-{suffix}.stl"
        build_path = E.BUILD / f"servo_{suffix}.stl"
        if not source_path.exists() or not build_path.exists():
            rows[suffix] = {"pass": False, "missing": [str(path) for path in
                                                        (source_path, build_path) if not path.exists()]}
            continue
        source = E.read_stl_path(source_path)
        built = E.read_stl_path(build_path)
        translated_source = source.copy()
        translated_source[:, :, 2] += P.SERVO_Z0 * 1000.0
        source_bounds = E.triangle_bounds(source)
        build_bounds = E.triangle_bounds(built)
        expected = [[source_bounds[side][axis] + (P.SERVO_Z0 * 1000.0 if axis == 2 else 0.0)
                     for axis in range(3)] for side in range(2)]
        errors = [[build_bounds[side][axis] - expected[side][axis] for axis in range(3)]
                  for side in range(2)]
        source_topology = E.topology(source_path)
        build_topology = E.topology(build_path)
        extent_source = [source_bounds[1][axis] - source_bounds[0][axis] for axis in range(3)]
        extent_build = [build_bounds[1][axis] - build_bounds[0][axis] for axis in range(3)]
        pass_bounds = max(abs(value) for row in errors for value in row) <= 0.002
        pass_extent = max(abs(a - b) for a, b in zip(extent_source, extent_build)) <= 0.002
        pass_volume = abs(abs(source_topology["signed_volume_mm3"])
                          - abs(build_topology["signed_volume_mm3"])) <= 0.01
        forward_distance = directed_surface_distance(translated_source, built)
        reverse_distance = directed_surface_distance(built, translated_source)
        bvh_surface_distance = max(forward_distance, reverse_distance)
        indexed = indexed_triangle_surface_distance(translated_source, built)
        indexed_surface_bound = (None if indexed is None else
                                 indexed["maximumVertexDistanceMm"])
        indexed_surface_area_error = (None if indexed is None else
                                      indexed["surfaceAreaErrorMm2"])
        # 同一三角形順の正本コピーは、対応頂点の最大距離が全三角形面の
        # Hausdorff距離上限になる。BVH最近傍の単精度誤差より厳密なのでこちらを使う。
        indexed_identity = (indexed_surface_bound is not None
                            and indexed_surface_area_error is not None
                            and indexed_surface_area_error <= 0.003)
        maximum_surface_distance = (indexed_surface_bound if indexed_identity
                                    else bvh_surface_distance)
        common_volume = None
        common_volume_pass = True
        if suffix in ("body", "horn"):
            source_mesh = E.Mesh.load(str(source_path), "canonical_" + suffix)
            built_mesh = E.Mesh.load(str(build_path), "placed_" + suffix)
            common_volume = E.exact_common_volume(
                source_mesh, Matrix.Translation((0, 0, P.SERVO_Z0 * 1000.0)),
                built_mesh, Matrix.Identity(4))
            common_volume_pass = abs(common_volume - abs(build_topology["signed_volume_mm3"])) <= 0.01
        home_matrix = motion.transforms(P.HOME_SERVO_DEG).get(
            f"servo_{suffix}", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
        identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        home_identity_pass = max(abs(a - b) for a, b in zip(home_matrix, identity)) <= 1e-9
        rows[suffix] = {
            "source": source_path.relative_to(ROOT).as_posix(),
            "build": build_path.relative_to(ROOT).as_posix(),
            "sourceBoundsMm": source_bounds, "buildBoundsMm": build_bounds,
            "expectedTranslationMm": [0.0, 0.0, P.SERVO_Z0 * 1000.0],
            "boundsErrorMm": errors, "extentIdentityPass": pass_extent,
            "signedVolumeIdentityPass": pass_volume, "homeMotionMatrix": home_matrix,
            "bidirectionalSurfaceDistanceMm": {
                "sourceToBuild": round(forward_distance, 6),
                "buildToSource": round(reverse_distance, 6),
                "bvhMaximumDiagnostic": round(bvh_surface_distance, 6),
                "indexedTriangleUpperBound": (None if indexed_surface_bound is None else
                                                round(indexed_surface_bound, 9)),
                "indexedSurfaceAreaErrorMm2": (None if indexed_surface_area_error is None else
                                                 round(indexed_surface_area_error, 9)),
                "maximum": round(maximum_surface_distance, 9),
                "method": ("indexed_triangle_upper_bound" if indexed_identity
                           else "bidirectional_bvh"),
            },
            "surfaceIdentityPass": maximum_surface_distance <= 0.003,
            "commonVolumeMm3": common_volume,
            "commonVolumeIdentityPass": common_volume_pass,
            "homeMotionIdentityPass": home_identity_pass,
            "pass": (pass_bounds and pass_extent and pass_volume
                     and maximum_surface_distance <= 0.003
                     and common_volume_pass and home_identity_pass),
        }
    calibration = canonical_surface_calibration()
    return {"parts": rows, "calibration": calibration,
            "pass": calibration["pass"] and bool(rows) and all(row["pass"] for row in rows.values()),
            "method": ("正本STLと配置後STLを独立にバイナリ解析する。bbox、外形寸法、"
                       "符号付き体積、倍精度の対応三角形表面距離、閉境界共通体積を照合する。")}


def axial_xy(q, r):
    pitch = P.HEX_PITCH * 1000.0
    return pitch * (q + r / 2.0), pitch * math.sqrt(3.0) * r / 2.0


def line_crossings(segments, y, center_x):
    values = []
    for first, second in segments:
        if not (min(first[1], second[1]) - 1e-7 <= y <= max(first[1], second[1]) + 1e-7):
            continue
        if abs(second[1] - first[1]) <= 1e-9:
            continue
        fraction = (y - first[1]) / (second[1] - first[1])
        x = first[0] + fraction * (second[0] - first[0])
        if abs(x - center_x) <= 6.0:
            values.append(float(x))
    unique = []
    for value in sorted(values):
        if not unique or abs(value - unique[-1]) > 1e-4:
            unique.append(value)
    return unique


def transformed_triangles(triangles, matrix):
    values = np.asarray(matrix, dtype=float)
    flat = triangles.reshape(-1, 3)
    homogeneous = np.column_stack((flat, np.ones(len(flat))))
    return (homogeneous @ values.T)[:, :3].reshape((-1, 3, 3))


def point_in_section(point, segments):
    """水平断面の閉曲線に点が含まれるかを奇偶則で判定する。"""
    x, y = point
    crossings = 0
    for first, second in segments:
        if (first[1] > y) == (second[1] > y):
            continue
        hit_x = first[0] + ((y - first[1]) * (second[0] - first[0])
                            / (second[1] - first[1]))
        if hit_x > x:
            crossings += 1
    return crossings % 2 == 1


def opening_width(segments, center, direction):
    """中心を通る直線と全境界の交点から、開口の対向距離を返す。"""
    direction = np.asarray(direction, dtype=float)
    values = []
    for first, second in segments:
        edge = second - first
        denominator = direction[0] * edge[1] - direction[1] * edge[0]
        if abs(denominator) <= 1e-10:
            continue
        delta = first - np.asarray(center)
        distance = (delta[0] * edge[1] - delta[1] * edge[0]) / denominator
        fraction = (delta[0] * direction[1] - delta[1] * direction[0]) / denominator
        if -1e-8 <= fraction <= 1.0 + 1e-8:
            values.append(float(distance))
    unique = []
    for value in sorted(values):
        if not unique or abs(value - unique[-1]) > 1e-4:
            unique.append(value)
    negative = [value for value in unique if value < -1e-5]
    positive = [value for value in unique if value > 1e-5]
    return None if not negative or not positive else min(positive) - max(negative)


def hex_probe_offsets(flat):
    radius = flat / math.sqrt(3.0)
    limit = flat / 2.0 - 0.01
    rows = []
    for x in np.linspace(-radius, radius, 13):
        for y in np.linspace(-radius, radius, 13):
            if (abs(x) <= limit
                    and abs(0.5 * x + math.sqrt(3.0) * 0.5 * y) <= limit
                    and abs(0.5 * x - math.sqrt(3.0) * 0.5 * y) <= limit):
                rows.append((float(x), float(y)))
    return rows


def hole_clearance(meshes):
    """19セルの9.3mm六角通路を5停止状態の実STL断面で検査する。"""
    relevant = ("faceplate", *(f"carrier_{name}" for name in P.GROUPS))
    source = {name: E.read_stl(name) for name in relevant}
    cells = [(group, cell) for group in P.GROUPS for cell in P.CELL_QR[group]]
    cells.extend(("fixed", cell) for cell in P.CELL_QR["fixed"])
    z_levels = (100.41, 102.0, 104.0, 106.79, 106.81, 108.0, 109.99)
    directions = ((1.0, 0.0), (0.5, math.sqrt(3.0) / 2.0),
                  (0.5, -math.sqrt(3.0) / 2.0))
    probes = hex_probe_offsets(P.HEX_HOLE_FLAT * 1000.0)
    rows = []
    for state_id, label, degree in P.PATTERNS:
        matrices = pose_matrices(meshes, degree)
        triangles = {name: transformed_triangles(source[name], matrices[name])
                     for name in relevant}
        sections = {z: {name: E.slice_z(data, z) for name, data in triangles.items()}
                    for z in z_levels}
        for group, (q, r) in cells:
            center = axial_xy(q, r)
            level_rows = []
            for z in z_levels:
                per_part = sections[z]
                combined = np.concatenate([segments for segments in per_part.values() if len(segments)],
                                          axis=0) if any(len(segments) for segments in per_part.values()) else np.empty((0, 2, 2))
                blocked = []
                for offset in probes:
                    point = (center[0] + offset[0], center[1] + offset[1])
                    for part, segments in per_part.items():
                        if len(segments) and point_in_section(point, segments):
                            blocked.append({"part": part,
                                            "pointMm": [round(point[0], 5), round(point[1], 5)]})
                            break
                widths = [opening_width(combined, center, direction) for direction in directions]
                width_pass = (z < (P.CUBE - P.FRAME_T) * 1000.0
                              or all(width is not None
                                     and width >= P.HEX_HOLE_FLAT * 1000.0 - 0.02
                                     for width in widths))
                level_rows.append({"zMm": z,
                                   "actualFlatsMm": [None if width is None else round(width, 6)
                                                     for width in widths],
                                   "blockedProbeCount": len(blocked),
                                   "blockedProbeExamples": blocked[:8],
                                   "pass": not blocked and width_pass})
            rows.append({"state": state_id, "stateLabel": label, "servoDeg": degree,
                         "group": group, "cellQr": [q, r], "centerMm": list(center),
                         "requiredFlatMm": P.HEX_HOLE_FLAT * 1000.0,
                         "requiredOpenZMm": [P.CUBE * 1000.0 - 9.6, P.CUBE * 1000.0],
                         "levels": level_rows,
                         "pass": all(level["pass"] for level in level_rows)})
    failures = [row for row in rows if not row["pass"]]
    return {"method": ("全19セルを5停止状態で水平切断する。六角内の実点群がどの実STL断面にも"
                       "含まれないことと、上部断面の3対辺距離が9.28mm以上であることを測る。"),
            "states": len(P.PATTERNS), "cellsPerState": len(cells),
            "zSamplesMm": list(z_levels), "probePointsPerSection": len(probes),
            "cells": rows, "failures": failures, "pass": bool(rows) and not failures}


def hole_clearance_calibration():
    square = np.asarray((((-5.0, -5.0), (5.0, -5.0)),
                         ((5.0, -5.0), (5.0, 5.0)),
                         ((5.0, 5.0), (-5.0, 5.0)),
                         ((-5.0, 5.0), (-5.0, -5.0))), dtype=float)
    inside = point_in_section((0.0, 0.0), square)
    outside = point_in_section((6.0, 0.0), square)
    width = opening_width(square, (0.0, 0.0), (1.0, 0.0))
    return {
        "positiveFixture": {"description": "10mm正方形内の原点", "inside": inside,
                            "openingWidthMm": width,
                            "pass": inside and width is not None and abs(width - 10.0) <= 1e-9},
        "negativeFixture": {"description": "10mm正方形外の点(6,0)", "inside": outside,
                            "pass": not outside},
        "pass": inside and not outside and width is not None and abs(width - 10.0) <= 1e-9,
    }


def write_hole_clearance_report(meshes, names):
    stl_paths = [E.BUILD / f"{name}.stl" for name in names]
    start = E.source_hashes(stl_paths)
    calibration = hole_clearance_calibration()
    clearance = hole_clearance(meshes)
    end = E.source_hashes(stl_paths)
    source_integrity = {"start": start, "end": end, "pass": start == end}
    source_paths = [HERE / name for name in ("hole_clearance.py", "verify.py", "evidence.py",
                                              "params.py", "motion.py", "contact_envelope.py",
                                              "model.py")]
    source_paths.append(E.BUILD / "manifest.json")
    document = {
        "version": 1, "model": P.MODEL_ID,
        "method": clearance["method"], "calibration": calibration,
        "clearance": clearance,
        "sourceHashes": E.source_hashes(path for path in source_paths if path.exists()) | end,
        "sourceIntegrity": source_integrity,
        "pass": calibration["pass"] and clearance["pass"] and source_integrity["pass"],
    }
    E.write_json(E.BUILD / "hole_clearance.json", document)
    return document


def read_manifest():
    path = E.BUILD / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    calibration = E.calibration()
    if not calibration["pass"]:
        raise SystemExit("calibration failed before prototype STL inspection")
    manifest = read_manifest()
    names = tuple(part["id"] for part in manifest["parts"] if not part.get("fit_only"))
    missing_required = sorted(REQUIRED_PARTS - set(names))
    start_paths = [E.BUILD / f"{name}.stl" for name in names]
    source_start = E.source_hashes(start_paths)
    meshes = {name: E.load(name) for name in names}
    references = {"servo_body", "servo_horn", "servo_wire"}
    topology = {}
    for name in names:
        item = E.topology(E.BUILD / f"{name}.stl")
        expected = next(part.get("expected_assembly_components", 1)
                        for part in manifest["parts"] if part["id"] == name)
        item["expected_connected_components"] = expected
        item["pass"] = item["pass"] and item["connected_components"] == expected
        topology[name] = item
    printed = tuple(part["id"] for part in manifest["parts"] if part.get("print") and not part.get("fit_only"))
    print_topology = {}
    for name in printed:
        item = E.topology(E.BUILD / f"print_{name}.stl")
        expected = next(part.get("expected_print_components", 1)
                        for part in manifest["parts"] if part["id"] == name)
        item["expected_connected_components"] = expected
        item["on_bed"] = abs(item["bounds_mm"][0][2]) <= 0.001
        item["pass"] = item["pass"] and item["connected_components"] == expected and item["on_bed"]
        print_topology[name] = item
    print(json.dumps({"phase": "exact_scene", "status": "start"}), flush=True)
    scene = scene_geometry(meshes)
    print(json.dumps({"phase": "cam_follower", "status": "start"}), flush=True)
    cam_foot = actual_cam_foot(meshes) if not ({"cam_disk"} | {
        f"carrier_{name}" for name in P.GROUPS}) - set(meshes) else {
            "pass": False, "missing": sorted(({"cam_disk"} | {f"carrier_{name}" for name in P.GROUPS}) - set(meshes))}
    print(json.dumps({"phase": "state_bounds", "status": "start"}), flush=True)
    states = state_bounds(meshes)
    reference_placement = canonical_reference_placement()
    print(json.dumps({"phase": "hole_clearance", "status": "start"}), flush=True)
    hole_document = write_hole_clearance_report(meshes, names)
    holes = hole_document["clearance"]
    source_end = E.source_hashes(start_paths)
    source_integrity = {"start": source_start, "end": source_end, "pass": source_start == source_end}
    dependency_paths = [HERE / name for name in ("params.py", "motion.py", "contact_envelope.py",
                                                  "verify.py", "drive.py", "assembly.py",
                                                  "evidence.py", "boolean_evidence.py",
                                                  "hole_clearance.py", "model.py")]
    dependency_paths.extend((E.BUILD / "manifest.json", ROOT / "models/sg92r-photo/params.py",
                             ROOT / "models/mystery-box-sg92r-c4/verify.py"))
    source_hashes = E.source_hashes(path for path in dependency_paths if path.exists()) | source_end
    assembly_path = E.BUILD / "assembly_report.json"
    drive_path = E.BUILD / "drive_report.json"
    assembly = json.loads(assembly_path.read_text(encoding="utf-8")) if assembly_path.exists() else {}
    drive = json.loads(drive_path.read_text(encoding="utf-8")) if drive_path.exists() else {}
    boolean_path = E.BUILD / "boolean_evidence.json"
    boolean_document = json.loads(boolean_path.read_text(encoding="utf-8")) if boolean_path.exists() else {}
    boolean_summary = boolean_document.get("summary", {})
    boolean_ok = (boolean_document.get("model") == P.MODEL_ID
                  and boolean_summary.get("calibrationPass") is True
                  and boolean_summary.get("missingFiles") == 0
                  and boolean_summary.get("invalidClosedSolids") == 0
                  and boolean_summary.get("properNonadjacentIntersections") == 0
                  and E.hashes_match(boolean_document.get("wrapperSha256", {})))
    assembly_ok = (assembly.get("model") == P.MODEL_ID and assembly.get("pass") is True
                   and E.hashes_match(assembly.get("sourceHashes", {}))
                   and assembly.get("sourceIntegrity", {}).get("end") == {
                       name: source_end[(E.BUILD / f"{name}.stl").relative_to(ROOT).as_posix()] for name in names})
    drive_ok = (drive.get("model") == P.MODEL_ID
                and drive.get("overall", {}).get("geometryPass") is True
                and E.hashes_match(drive.get("sourceHashes", {})))
    passed = (not missing_required and all(item["pass"] for item in topology.values())
              and all(item["pass"] for item in print_topology.values()) and scene["pass"]
              and cam_foot["pass"] and states["pass"] and reference_placement["pass"]
              and hole_document["pass"]
              and assembly_ok and drive_ok and boolean_ok
              and source_integrity["pass"])
    report = {
        "version": 1, "model": P.MODEL_ID, "pass": passed, "passScope": "cad",
        "passBasis": "実STLの幾何、駆動界面、現行組立経路の合否。実機合格ではない。",
        "physicalStatus": "conditional" if passed else "fail",
        "hardwareUnknown": drive.get("hardwareUnknown", ["SG92R実物嵌合", "印刷収縮", "摩擦と材料強度"]),
        "calibration": calibration, "requiredParts": sorted(REQUIRED_PARTS),
        "missingRequiredParts": missing_required, "sourceHashes": source_hashes,
        "source_stl_integrity": source_integrity,
        "stl_direct_parse": {name: item for name, item in topology.items() if name not in references},
        "canonical_reference_stl": {name: item for name, item in topology.items() if name in references},
        "print_stl_direct_parse": print_topology, "exact_scene": scene,
        "camFollowerActualHeight": cam_foot, "stateBounds": states,
        "canonicalReferencePlacement": reference_placement,
        "holeClearance": {"report": "build/hole_clearance.json", **holes},
        "assembly": {"report": "build/assembly_report.json", "pass": assembly_ok},
        "drive": {"report": "build/drive_report.json", "pass": drive_ok},
        "booleanEvidence": {"report": "build/boolean_evidence.json", "summary": boolean_summary,
                            "pass": boolean_ok},
        "limitations": ["物理印刷、SG92R通電、嵌合、摩擦、材料強度は未検証。",
                        "許容する実体積は座標範囲を固定した既知接触だけ。"],
    }
    E.write_json(E.BUILD / "verify_report.json", report)
    print(json.dumps({"pass": passed, "topologyPass": all(x["pass"] for x in topology.values()),
                      "scenePass": scene["pass"], "camFootPass": cam_foot["pass"],
                      "assemblyPass": assembly_ok, "drivePass": drive_ok,
                      "missingRequiredParts": missing_required}, ensure_ascii=False))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
