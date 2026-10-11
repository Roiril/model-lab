"""C4-2 のホーン、キー、カム外周、保持を実STLから検証する。"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import motion  # noqa: E402
import params as P  # noqa: E402
import evidence as E  # noqa: E402
import verify  # noqa: E402


VOLUME_LIMIT_MM3 = 0.001
MAX_ONE_SIDED_CONTACT_DEG = 5.0


def rectangular_probe(lower, upper, name):
    """指定直方体をMANIFOLD負例・正例へ使う。"""
    x0, y0, z0 = lower
    x1, y1, z1 = upper
    vertices = [E.Vector(point) for point in (
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    triangles = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
                 (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
                 (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return E.Mesh(vertices, triangles, name)


def angular_interface(meshes, male_name, female_name, identifier, label, wrong_angle):
    if male_name not in meshes or female_name not in meshes:
        return {"id": identifier, "label": label, "status": "fail",
                "missing": sorted({male_name, female_name} - set(meshes))}
    male, female = meshes[male_name], meshes[female_name]
    negative = E.first_angular_contact(male, female, sign=-1)
    positive = E.first_angular_contact(male, female, sign=1)
    wrong = E.common_at_rotation(male, female, wrong_angle)
    angles = [negative["contactAngleDeg"], positive["contactAngleDeg"]]
    total = sum(angles) if all(value is not None for value in angles) else None
    passed = (negative["pass"] and positive["pass"] and total is not None
              and max(angles) <= MAX_ONE_SIDED_CONTACT_DEG
              and wrong["common_volume_mm3"] > VOLUME_LIMIT_MM3)
    return {
        "id": identifier, "label": label, "status": "pass" if passed else "fail",
        "parts": [male_name, female_name], "negativeDirection": negative,
        "positiveDirection": positive, "totalAngularPlayDeg": round(total, 6) if total is not None else None,
        "contactAnglesDeg": [negative["contactAngleDeg"], positive["contactAngleDeg"]],
        "maximumOneSidedContactAngleDeg": MAX_ONE_SIDED_CONTACT_DEG,
        "wrongOrientationDeg": wrong_angle,
        "wrongOrientationCommonVolumeMm3": wrong["common_volume_mm3"],
        "wrongOrientationRejected": wrong["common_volume_mm3"] > VOLUME_LIMIT_MM3,
        "method": "雄STLだけを正逆へ回し、MANIFOLD共通体積が0.001mm3を超える最初の角度を二分探索。",
    }


def axial_retention(meshes):
    interfaces = (
        ("coupler-housing-stop", "ホーン受けと外装上昇止め",
         "horn_coupler", "housing", 1, 0.3, -30.0),
        ("coupler-blind-floor", "角キーとホーン受け盲底",
         "horn_coupler", "drive_key", 1, 0.2, 30.0),
        ("key-head-disk", "キー頭と円盤上面", "cam_disk", "drive_key", 1, 0.2, 30.0),
        ("key-head-guide-stop", "キー頭と案内枠上止め",
         "drive_key", "guide_frame", 1, 0.3, 30.0),
        ("disk-keeper", "円盤と止め輪", "cam_keeper", "cam_disk", -1, 0.3, -30.0),
    )
    missing = sorted({part for _id, _label, moving, stop, _sign, _gap, _remove in interfaces
                      for part in (moving, stop)} - set(meshes))
    if missing:
        return {"id": "axial-retention", "label": "駆動積層の両方向保持", "status": "fail",
                "missing": missing}
    identity = E.Matrix.Identity(4)
    rows = []
    for identifier, label, moving, stop, sign, nominal_gap, remove_shift in interfaces:
        contact = E.first_linear_contact(meshes[moving], meshes[stop], axis=2, sign=sign,
                                         maximum_mm=2.0, coarse_step=0.05)
        travel = contact.get("contactTravelMm")
        moved = identity if travel is None else E.Matrix.Translation((0, 0, sign * travel))
        target = E.exact_common_geometry(meshes[moving], moved, meshes[stop], identity)
        # 同じ接触姿勢のまま停止部品だけを30mm退避し、別形状の偶発接触ではないことを確認する。
        removed_stop = E.exact_common_geometry(
            meshes[moving], moved, meshes[stop], E.Matrix.Translation((0, 0, remove_shift)))
        passed = (contact["pass"]
                  and contact["nominalCommonVolumeMm3"] <= VOLUME_LIMIT_MM3
                  and travel is not None and abs(travel - nominal_gap) <= 0.03
                  and target["common_volume_mm3"] > VOLUME_LIMIT_MM3
                  and removed_stop["common_volume_mm3"] <= VOLUME_LIMIT_MM3)
        rows.append({
            "id": identifier, "label": label, "movingPart": moving, "stopPart": stop,
            "direction": "+Z" if sign > 0 else "-Z", "contact": contact,
            "requiredNominalGapMm": nominal_gap, "gapToleranceMm": 0.03,
            "targetContact": target,
            "stopRemovedNegativeExample": {
                "stopTranslationMm": [0.0, 0.0, remove_shift],
                **removed_stop,
                "pass": removed_stop["common_volume_mm3"] <= VOLUME_LIMIT_MM3,
            },
            "pass": passed,
        })
    passed = bool(rows) and all(row["pass"] for row in rows)
    return {"id": "axial-retention", "label": "駆動積層の両方向保持",
            "status": "pass" if passed else "fail", "interfaces": rows,
            "method": ("ホーン受け、角キー、円盤、止め輪を界面ごとに相対移動する。"
                       "初接触をMANIFOLD共通体積で求め、同じ姿勢で対象停止部品だけを"
                       "30mm退避した負例が0.001mm3以下になることを測る。")}


def outer_support(meshes):
    if not {"cam_disk", "housing", "cam_keeper"} <= set(meshes):
        return {"id": "cam-outer-support", "label": "カム円盤の外周支持", "status": "fail",
                "missing": sorted({"cam_disk", "housing", "cam_keeper"} - set(meshes))}
    identity = E.Matrix.Identity(4)
    nominal_lower = E.exact_common_geometry(meshes["cam_disk"], identity, meshes["housing"], identity)
    nominal_upper = E.exact_common_geometry(meshes["cam_disk"], identity, meshes["cam_keeper"], identity)
    lower = E.exact_common_geometry(meshes["cam_disk"], E.Matrix.Translation((0, 0, -0.1)),
                                    meshes["housing"], identity)
    upper = E.exact_common_geometry(meshes["cam_disk"], E.Matrix.Translation((0, 0, 0.5)),
                                    meshes["cam_keeper"], identity)
    passed = (nominal_lower["common_volume_mm3"] <= VOLUME_LIMIT_MM3
              and nominal_upper["common_volume_mm3"] <= VOLUME_LIMIT_MM3
              and lower["common_volume_mm3"] > VOLUME_LIMIT_MM3
              and upper["common_volume_mm3"] > VOLUME_LIMIT_MM3)
    return {"id": "cam-outer-support", "label": "カム円盤の外周支持",
            "status": "pass" if passed else "fail", "nominalLower": nominal_lower,
            "nominalUpper": nominal_upper, "downward0_1Mm": lower, "upward0_5Mm": upper,
            "method": "円盤フランジ実STLを下へ0.1mm動かしてhousing支持環、上へ0.5mm動かしてkeeperへ接触することをMANIFOLDで測定。"}


def servo_body_retention(meshes, manifest):
    if not {"servo_body", "housing", "bottom"} <= set(meshes):
        return {"id": "servo-body-retention", "label": "SG92R本体の六方向保持",
                "status": "fail",
                "missing": sorted({"servo_body", "housing", "bottom"} - set(meshes))}
    definitions = manifest.get("meta", {}).get("retention_interfaces", {})
    directions = (
        ("x-minus", 0, -1, "housing"), ("x-plus", 0, 1, "housing"),
        ("y-minus", 1, -1, "housing"), ("y-plus", 1, 1, "housing"),
        ("z-minus", 2, -1, "bottom"), ("z-plus", 2, 1, "housing"),
    )
    rows = []
    for identifier, axis, sign, default_receiver in directions:
        definition = definitions.get("servo_body_" + identifier.replace("-", "_"), {})
        receiver = definition.get("receiver", default_receiver)
        allowed = definition.get("contact_bbox_mm")
        expected = float(definition.get("nominal_gap_mm", P.SERVO_CLR * 1000.0))
        contact = E.first_linear_contact(meshes["servo_body"], meshes[receiver],
                                         axis=axis, sign=sign, maximum_mm=1.0,
                                         coarse_step=0.025)
        travel = contact.get("contactTravelMm")
        offset_values = [0.0, 0.0, 0.0]
        if travel is not None:
            offset_values[axis] = sign * travel
        geometry = E.exact_common_geometry(
            meshes["servo_body"], E.Matrix.Translation(offset_values),
            meshes[receiver], E.Matrix.Identity(4))
        components = geometry["intersection_component_bounds_mm"]
        localized = (allowed is not None and bool(components)
                     and all(E.bounds_within(component, allowed, tolerance=0.01)
                             for component in components))
        passed = (contact["pass"]
                  and contact["nominalCommonVolumeMm3"] <= VOLUME_LIMIT_MM3
                  and travel is not None and abs(travel - expected) <= 0.03
                  and geometry["common_volume_mm3"] > VOLUME_LIMIT_MM3
                  and localized)
        rows.append({"direction": identifier, "axis": axis, "sign": sign,
                     "receiver": receiver, "expectedGapMm": expected,
                     "gapToleranceMm": 0.03, "contact": contact,
                     "contactGeometry": geometry, "allowedContactBoundsMm": allowed,
                     "localizedToCorrespondingWall": localized, "pass": passed})
    bottom_snap_regions = verify.CANONICAL_ALLOWANCES[("bottom", "housing")]["componentBoundsMm"]
    bottom_contact = E.first_linear_contact(
        meshes["bottom"], meshes["housing"], axis=2, sign=-1,
        maximum_mm=1.0, coarse_step=0.025)
    bottom_travel = bottom_contact.get("contactTravelMm")
    bottom_snap = ({"common_volume_mm3": 0.0, "intersection_component_bounds_mm": []}
                   if bottom_travel is None else E.exact_common_geometry(
                       meshes["bottom"], E.Matrix.Translation((0.0, 0.0, -bottom_travel)),
                       meshes["housing"], E.Matrix.Identity(4)))
    bottom_snap_localized = (
        bool(bottom_snap["intersection_component_bounds_mm"])
        and all(any(E.bounds_within(component, region, tolerance=0.01)
                    for region in bottom_snap_regions)
                for component in bottom_snap["intersection_component_bounds_mm"]))
    bottom_removed = E.exact_common_geometry(
        meshes["bottom"], (E.Matrix.Identity(4) if bottom_travel is None else
                           E.Matrix.Translation((0.0, 0.0, -bottom_travel))),
        meshes["housing"], E.Matrix.Translation((0.0, 0.0, 200.0)))
    retention_chain = {
        "parts": ["servo_body", "bottom", "housing"],
        "bottomToHousingContact": bottom_contact,
        "bottomSnapContactGeometry": bottom_snap,
        "localizedToBottomHookStops": bottom_snap_localized,
        "bodyToBottomNominalGapMm": 0.35,
        "bottomToHousingNominalGapMm": 0.2,
        "totalDownwardPlayMm": (None if bottom_travel is None else
                                 round(0.35 + bottom_travel, 6)),
        "housingRemovedNegativeExample": {
            **bottom_removed, "housingTranslationMm": [0.0, 0.0, 200.0],
            "pass": bottom_removed["common_volume_mm3"] <= VOLUME_LIMIT_MM3,
        },
        "pass": (bottom_contact["pass"]
                 and bottom_contact["nominalCommonVolumeMm3"] <= VOLUME_LIMIT_MM3
                 and bottom_travel is not None and abs(bottom_travel - 0.2) <= 0.03
                 and bottom_snap["common_volume_mm3"] > VOLUME_LIMIT_MM3
                 and bottom_snap_localized
                 and bottom_removed["common_volume_mm3"] <= VOLUME_LIMIT_MM3),
    }
    wire_probe = rectangular_probe((49.01, -3.99, 6.51), (55.1, 3.99, 11.49),
                                   "wire_exit_clear_probe")
    blocked_probe = rectangular_probe((52.7, 4.05, 6.6), (54.9, 4.35, 11.4),
                                      "wire_exit_blocked_probe")
    wire_clear = E.exact_common_geometry(
        wire_probe, E.Matrix.Identity(4), meshes["housing"], E.Matrix.Identity(4))
    wire_blocked = E.exact_common_geometry(
        blocked_probe, E.Matrix.Identity(4), meshes["housing"], E.Matrix.Identity(4))
    wire_exit = {
        "clearProbeBoundsMm": [[49.01, -3.99, 6.51], [55.1, 3.99, 11.49]],
        "measuredClearWidthMm": 7.98,
        "measuredClearHeightMm": 4.98,
        "clearProbe": wire_clear,
        "blockedCalibrationProbeBoundsMm": [[52.7, 4.05, 6.6], [54.9, 4.35, 11.4]],
        "blockedCalibrationProbe": wire_blocked,
        "pass": (wire_clear["common_volume_mm3"] <= VOLUME_LIMIT_MM3
                 and wire_blocked["common_volume_mm3"] > VOLUME_LIMIT_MM3),
    }
    passed = (len(rows) == 6 and all(row["pass"] for row in rows)
              and retention_chain["pass"] and wire_exit["pass"])
    return {"id": "servo-body-retention", "label": "SG92R本体の六方向保持",
            "status": "pass" if passed else "fail", "directions": rows,
            "retentionChain": retention_chain,
            "wireExitClearance": wire_exit,
            "method": ("SG92R本体だけをX/Y/Zの正負へ動かす。各0.35mm公称隙間の初接触を"
                       "MANIFOLD体積で求め、manifestの対応壁範囲に実交差成分が収まることを測る。"
                       "X方向の受けを持つ底板から爪を経て外装へ伝わる保持連鎖も局所接触で測る。"
                       "本体から底板まで0.35mmと底板から外装まで0.2mmを分けて記録する。"),
            "physicalForceStatus": "底板爪を介したSG92R保持力は実機未確認。"}


def guide_frame_retention(meshes, manifest):
    if not {"guide_frame", "housing", "faceplate"} <= set(meshes):
        return {"id": "guide-frame-retention", "label": "案内枠の六方向保持",
                "status": "fail",
                "missing": sorted({"guide_frame", "housing", "faceplate"} - set(meshes))}
    definitions = manifest.get("meta", {}).get("retention_interfaces", {})
    directions = (
        ("x-minus", 0, -1, "housing"), ("x-plus", 0, 1, "housing"),
        ("y-minus", 1, -1, "housing"), ("y-plus", 1, 1, "housing"),
        ("z-minus", 2, -1, "housing"), ("z-plus", 2, 1, "faceplate"),
    )
    rows = []
    for identifier, axis, sign, receiver in directions:
        definition = definitions.get("guide_frame_" + identifier.replace("-", "_"), {})
        allowed = definition.get("contact_bbox_mm")
        allowed_regions = [allowed] if allowed is not None else []
        if identifier == "z-minus":
            allowed_regions = [
                [[x0, y0, 75.8], [x1, y1, 76.2]]
                for x0, x1 in ((-52.8, -47.0), (47.0, 52.8))
                for y0, y1 in ((-52.8, -47.0), (47.0, 52.8))]
        elif identifier == "z-plus":
            allowed_regions = [
                [[x0, y0, 79.0], [x1, y1, 79.7]]
                for x0, x1 in ((-50.0, -47.0), (47.0, 50.0))
                for y0, y1 in ((-50.0, -47.0), (47.0, 50.0))]
        expected = definition.get("nominal_gap_mm")
        contact = E.first_linear_contact(meshes["guide_frame"], meshes[receiver],
                                         axis=axis, sign=sign, maximum_mm=1.0,
                                         coarse_step=0.025)
        travel = contact.get("contactTravelMm")
        target_travel = (0.1 if identifier == "z-minus" else travel)
        offset = [0.0, 0.0, 0.0]
        if target_travel is not None:
            offset[axis] = sign * target_travel
        geometry = E.exact_common_geometry(
            meshes["guide_frame"], E.Matrix.Translation(offset),
            meshes[receiver], E.Matrix.Identity(4))
        receiver_offset = [0.0, 0.0, 0.0]
        receiver_offset[axis] = sign * 200.0
        removed = E.exact_common_geometry(
            meshes["guide_frame"], E.Matrix.Translation(offset),
            meshes[receiver], E.Matrix.Translation(receiver_offset))
        localized = (bool(allowed_regions) and bool(geometry["intersection_component_bounds_mm"])
                     and all(any(E.bounds_within(component, region, tolerance=0.01)
                                 for region in allowed_regions)
                             for component in geometry["intersection_component_bounds_mm"]))
        passed = (expected is not None and contact["pass"]
                  and contact["nominalCommonVolumeMm3"] <= VOLUME_LIMIT_MM3
                  and travel is not None and abs(travel - float(expected)) <= 0.03
                  and geometry["common_volume_mm3"] > VOLUME_LIMIT_MM3
                  and localized and removed["common_volume_mm3"] <= VOLUME_LIMIT_MM3)
        rows.append({"direction": identifier, "axis": axis, "sign": sign,
                     "receiver": receiver, "expectedGapMm": expected,
                     "gapToleranceMm": 0.03, "contact": contact,
                     "proofTranslationMm": target_travel,
                     "contactGeometry": geometry, "allowedContactBoundsMm": allowed_regions,
                     "localizedToCorrespondingMountFace": localized,
                     "receiverRemovedNegativeExample": {
                         "receiverTranslationMm": receiver_offset, **removed,
                         "pass": removed["common_volume_mm3"] <= VOLUME_LIMIT_MM3},
                     "pass": passed})

    faceplate_contact = E.first_linear_contact(
        meshes["faceplate"], meshes["housing"], axis=2, sign=1,
        maximum_mm=2.0, coarse_step=0.025)
    faceplate_travel = faceplate_contact.get("contactTravelMm")
    faceplate_geometry = ({"common_volume_mm3": 0.0,
                           "intersection_component_bounds_mm": []}
                          if faceplate_travel is None else E.exact_common_geometry(
                              meshes["faceplate"],
                              E.Matrix.Translation((0.0, 0.0, faceplate_travel)),
                              meshes["housing"], E.Matrix.Identity(4)))
    snap_regions = verify.CANONICAL_ALLOWANCES[("faceplate", "housing")]["componentBoundsMm"]
    snap_localized = (bool(faceplate_geometry["intersection_component_bounds_mm"])
                      and all(any(E.bounds_within(component, region, tolerance=0.01)
                                  for region in snap_regions)
                              for component in faceplate_geometry["intersection_component_bounds_mm"]))
    upward_snap_geometry = E.exact_common_geometry(
        meshes["faceplate"], E.Matrix.Translation((0.0, 0.0, 0.1)),
        meshes["housing"], E.Matrix.Identity(4))
    upward_snap_localized = (
        bool(upward_snap_geometry["intersection_component_bounds_mm"])
        and all(any(E.bounds_within(component, region, tolerance=0.01)
                    for region in snap_regions)
                for component in upward_snap_geometry["intersection_component_bounds_mm"]))
    faceplate_removed = E.exact_common_geometry(
        meshes["faceplate"], E.Matrix.Translation((0.0, 0.0, 0.1)),
        meshes["housing"], E.Matrix.Translation((0.0, 0.0, 200.0)))
    upper_chain = {
        "parts": ["guide_frame", "faceplate", "housing"],
        "faceplateSnapContact": faceplate_contact,
        "faceplateSnapContactGeometry": faceplate_geometry,
        "snapContactBoundsMm": snap_regions,
        "localizedToFaceplateSnaps": snap_localized,
        "upwardRetentionProof": {
            "faceplateTranslationMm": [0.0, 0.0, 0.1],
            "contactGeometry": upward_snap_geometry,
            "localizedToFaceplateSnaps": upward_snap_localized,
            "pass": (upward_snap_geometry["common_volume_mm3"] > VOLUME_LIMIT_MM3
                     and upward_snap_localized),
        },
        "housingRemovedNegativeExample": {**faceplate_removed,
                                            "housingTranslationMm": [0.0, 0.0, 200.0],
                                            "pass": faceplate_removed["common_volume_mm3"]
                                                    <= VOLUME_LIMIT_MM3},
    }
    upper_chain["pass"] = (faceplate_contact["pass"]
                            and faceplate_contact["nominalCommonVolumeMm3"] <= VOLUME_LIMIT_MM3
                            and faceplate_travel is not None and faceplate_travel <= 0.03
                            and snap_localized and faceplate_geometry["common_volume_mm3"] > VOLUME_LIMIT_MM3
                            and upward_snap_localized
                            and upward_snap_geometry["common_volume_mm3"] > VOLUME_LIMIT_MM3
                            and faceplate_removed["common_volume_mm3"] <= VOLUME_LIMIT_MM3)
    passed = len(rows) == 6 and all(row["pass"] for row in rows) and upper_chain["pass"]
    return {"id": "guide-frame-retention", "label": "案内枠の六方向保持",
            "status": "pass" if passed else "fail", "directions": rows,
            "upperRetentionChain": upper_chain,
            "method": ("案内枠をXY正負とZ正負へ動かし、隅の受け面と天板柱への初接触を"
                       "局所成分で測る。天板を上へ動かし、爪から外装までの上抜け連鎖も"
                       "実接触と外装退避負例で測る。"),
            "physicalForceStatus": "天板爪による上抜け保持力は実機未確認。"}


def square_boundary(segments, point, half, tolerance=0.02):
    """案内中心まわりの正方形境界だけを取り出し、接続梁の面を除外する。"""
    if not len(segments):
        return segments
    local = segments - np.asarray(point, dtype=float)[None, None, :]
    endpoint_radius = np.max(np.abs(local), axis=2)
    midpoint_radius = np.max(np.abs(local.mean(axis=1)), axis=1)
    mask = ((np.max(endpoint_radius, axis=1) <= half + tolerance)
            & (midpoint_radius >= half - tolerance)
            & (midpoint_radius <= half + tolerance))
    return segments[mask]


def cam_radial_retention(meshes):
    required = {"cam_disk", "guide_frame", *(f"carrier_{group}" for group in P.GROUPS)}
    if not required <= set(meshes):
        return {"id": "cam-radial-retention", "label": "カム円盤の径方向保持",
                "status": "fail", "missing": sorted(required - set(meshes))}
    identity = E.Matrix.Identity(4)
    boss_r = P.CAM_RADIAL_BEARING_R * 1000.0
    bearing_z0 = P.CAM_RADIAL_BEARING_Z0 * 1000.0
    bearing_z1 = P.CAM_RADIAL_BEARING_Z1 * 1000.0
    contact_rows = []
    for name, axis, sign in (("x-minus", 0, -1), ("x-plus", 0, 1),
                             ("y-minus", 1, -1), ("y-plus", 1, 1)):
        contact = E.first_linear_contact(meshes["cam_disk"], meshes["guide_frame"],
                                         axis=axis, sign=sign, maximum_mm=1.0,
                                         coarse_step=0.025)
        travel = contact.get("contactTravelMm")
        offset = [0.0, 0.0, 0.0]
        if travel is not None:
            offset[axis] = sign * travel
        geometry = E.exact_common_geometry(
            meshes["cam_disk"], E.Matrix.Translation(offset),
            meshes["guide_frame"], identity)
        side_bounds = [[-12.1, -12.1, bearing_z0 - 0.1],
                       [12.1, 12.1, bearing_z1 + 0.1]]
        side_bounds[0][axis] = sign * boss_r - (0.25 if sign < 0 else 0.05)
        side_bounds[1][axis] = sign * boss_r + (0.05 if sign < 0 else 0.25)
        removed = E.exact_common_geometry(
            meshes["cam_disk"], E.Matrix.Translation(offset),
            meshes["guide_frame"], E.Matrix.Translation((0.0, 0.0, 30.0)))
        localized = (bool(geometry["intersection_component_bounds_mm"])
                     and all(E.bounds_within(component, side_bounds, tolerance=0.01)
                             for component in geometry["intersection_component_bounds_mm"]))
        passed = (contact["pass"]
                  and contact["nominalCommonVolumeMm3"] <= VOLUME_LIMIT_MM3
                  and travel is not None and abs(travel - 0.2) <= 0.03
                  and geometry["common_volume_mm3"] > VOLUME_LIMIT_MM3
                  and localized and removed["common_volume_mm3"] <= VOLUME_LIMIT_MM3)
        contact_rows.append({"direction": name, "axis": axis, "sign": sign,
                             "expectedGapMm": 0.2, "gapToleranceMm": 0.03,
                             "contact": contact, "contactGeometry": geometry,
                             "allowedContactBoundsMm": side_bounds,
                             "localizedToCorrespondingBearingSide": localized,
                             "receiverRemovedNegativeExample": {
                                 "guideFrameTranslationMm": [0.0, 0.0, 30.0],
                                 **removed, "pass": removed["common_volume_mm3"] <= VOLUME_LIMIT_MM3},
                             "pass": passed})

    cam_points = E.read_stl("cam_disk").reshape(-1, 3)
    guide_section = E.slice_z(E.read_stl("guide_frame"), 85.0)
    post_half = P.GUIDE_LUG * 1000.0 / 2.0
    bore_half = post_half + P.GUIDE_CLR * 1000.0
    base_top = (P.CAM_BASE_Z + P.CAM_BASE_T) * 1000.0
    track_rows = []
    for index, group in enumerate(P.GROUPS):
        radius = P.CAM_RADII[index] * 1000.0
        angle = math.radians(P.FOLLOWER_ANGLES_DEG[index])
        radial = np.asarray((math.cos(angle), math.sin(angle)))
        tangent = np.asarray((-math.sin(angle), math.cos(angle)))
        cam_radius = np.linalg.norm(cam_points[:, :2], axis=1)
        cam_track_points = cam_points[
            (np.abs(cam_radius - radius) <= P.CAM_TRACK_W * 500.0 + 0.05)
            & (cam_points[:, 2] >= base_top - 0.01)]
        actual_track_width = (None if not len(cam_track_points) else
                              float(np.ptp(cam_radius[(np.abs(cam_radius - radius)
                                                      <= P.CAM_TRACK_W * 500.0 + 0.05)
                                                     & (cam_points[:, 2] >= base_top - 0.01)])))
        carrier_triangles = E.read_stl(f"carrier_{group}")
        carrier_points = carrier_triangles.reshape(-1, 3)
        radial_coordinate = carrier_points[:, :2] @ radial
        tangent_coordinate = carrier_points[:, :2] @ tangent
        foot_mask = ((np.abs(radial_coordinate - radius) <= 2.0)
                     & (np.abs(tangent_coordinate) <= P.FOLLOWER_ARC_L * 500.0 + 0.05)
                     & (carrier_points[:, 2] >= P.FOLLOWER_HOME_Z * 1000.0 - 0.05)
                     & (carrier_points[:, 2] <= ((P.FOLLOWER_HOME_Z + P.FOLLOWER_T)
                                                 * 1000.0 + 0.05)))
        foot_radial = radial_coordinate[foot_mask]
        foot_tangent = tangent_coordinate[foot_mask]
        foot_radius_norm = np.linalg.norm(carrier_points[foot_mask, :2], axis=1)
        actual_foot_width = None if not len(foot_radial) else float(np.ptp(foot_radial))
        actual_foot_arc = None if not len(foot_tangent) else float(np.ptp(foot_tangent))
        actual_foot_radius_norm_width = (None if not len(foot_radius_norm)
                                         else float(np.ptp(foot_radius_norm)))
        expected_foot_projection = (
            radius + P.FOLLOWER_RADIAL_W * 500.0
            - (radius - P.FOLLOWER_RADIAL_W * 500.0)
            * math.cos((P.FOLLOWER_ARC_L * 500.0) / radius))
        guide_clearances = []
        for guide_radius in (P.GUIDE_INNER_R * 1000.0, radius):
            point = radial * guide_radius
            carrier_section = E.slice_z(carrier_triangles, 85.0)
            post = square_boundary(carrier_section, point, post_half)
            bore = square_boundary(guide_section, point, bore_half)
            clearance = E.segment_distance(post, bore)
            if clearance is not None:
                guide_clearances.append(clearance)
        actual_guide_clearance = max(guide_clearances, default=None)
        contact_travels = [row["contact"].get("contactTravelMm") for row in contact_rows]
        eccentricity = (max(contact_travels)
                        if all(value is not None for value in contact_travels) else None)
        projection = (None if actual_guide_clearance is None else float(
                      actual_guide_clearance * (abs(radial[0]) + abs(radial[1]))))
        rotation_projection = None
        if actual_guide_clearance is not None and actual_foot_arc is not None:
            guide_separation = radius - P.GUIDE_INNER_R * 1000.0
            tangent_play = (2.0 * actual_guide_clearance
                            * (abs(tangent[0]) + abs(tangent[1])))
            radial_play = (2.0 * actual_guide_clearance
                           * (abs(radial[0]) + abs(radial[1])))
            maximum_rotation = math.atan2(tangent_play, guide_separation - radial_play)
            rotation_projection = float(actual_foot_arc / 2.0 * math.sin(maximum_rotation))
        margin = None
        if None not in (actual_track_width, actual_foot_width, eccentricity,
                        projection, rotation_projection):
            margin = float((actual_track_width - actual_foot_width) / 2.0
                           - eccentricity - projection - rotation_projection)
        passed = (len(guide_clearances) == 2
                  and actual_track_width is not None and actual_track_width >= 3.58
                  and actual_foot_width is not None
                  and abs(actual_foot_width - expected_foot_projection) <= 0.002
                  and actual_foot_radius_norm_width is not None
                  and abs(actual_foot_radius_norm_width
                          - P.FOLLOWER_RADIAL_W * 1000.0) <= 0.002
                  and margin is not None and margin > 0.0)
        track_rows.append({"group": group, "trackRadiusMm": radius,
                           "actualTrackWidthMm": actual_track_width,
                           "actualFootRadialWidthMm": actual_foot_width,
                           "expectedFootRadialProjectionMm": expected_foot_projection,
                           "actualFootRadiusNormWidthMm": actual_foot_radius_norm_width,
                           "actualFootTangentialLengthMm": actual_foot_arc,
                           "actualGuideClearancesMm": guide_clearances,
                           "camBearingEccentricityMm": eccentricity,
                           "worstGuideRadialProjectionMm": projection,
                           "worstFootRotationProjectionMm": rotation_projection,
                           "remainingRadialMarginMm": margin, "pass": passed})
    passed = (all(row["pass"] for row in contact_rows)
              and len(track_rows) == len(P.GROUPS) and all(row["pass"] for row in track_rows))
    return {"id": "cam-radial-retention", "label": "カム円盤の径方向保持",
            "status": "pass" if passed else "fail", "directions": contact_rows,
            "trackContainment": track_rows,
            "method": ("円盤bossをXY正負へ動かして案内枠軸受との0.2mm初接触を測る。"
                       "実STLのトラック幅、足輪郭、2案内の断面隙間から、偏心と案内移動と"
                       "足回転を同方向へ合算した径方向残量を求める。"),
            "physicalToleranceStatus": "公称STLの数値証拠。全面の製造公差組合せは未検証。"}


def carrier_retention(meshes):
    guide = meshes.get("guide_frame")
    if guide is None:
        return {"id": "carrier-retention", "label": "4群キャリアの案内保持", "status": "fail",
                "missing": ["guide_frame"]}
    guide_triangles = E.read_stl("guide_frame")
    post_half = P.GUIDE_LUG * 1000.0 / 2.0
    bore_half = post_half + P.GUIDE_CLR * 1000.0

    rows = []
    for index, group in enumerate(P.GROUPS):
        name = f"carrier_{group}"
        if name not in meshes:
            rows.append({"group": group, "pass": False, "missing": True})
            continue
        carrier_triangles = E.read_stl(name)
        angle = math.radians(P.FOLLOWER_ANGLES_DEG[index])
        points = ((P.GUIDE_INNER_R * 1000.0 * math.cos(angle),
                   P.GUIDE_INNER_R * 1000.0 * math.sin(angle)),
                  (P.CAM_RADII[index] * 1000.0 * math.cos(angle),
                   P.CAM_RADII[index] * 1000.0 * math.sin(angle)))
        guide_points = guide_triangles.reshape(-1, 3)
        carrier_points = carrier_triangles.reshape(-1, 3)
        samples = []
        for state_id, _label, degree in P.PATTERNS:
            matrix = E.transform_matrix(motion.transforms(degree)[name])
            lift = matrix.translation.z
            point_rows = []
            for point in points:
                carrier_local = carrier_points[
                    (abs(carrier_points[:, 0] - point[0]) <= 1.7)
                    & (abs(carrier_points[:, 1] - point[1]) <= 1.7)]
                guide_local = guide_points[
                    (abs(guide_points[:, 0] - point[0]) <= 4.0)
                    & (abs(guide_points[:, 1] - point[1]) <= 4.0)]
                if not len(carrier_local) or not len(guide_local):
                    point_rows.append({"xyMm": list(point), "pass": False, "missingSection": True})
                    continue
                carrier_range = [float(carrier_local[:, 2].min() + lift),
                                 float(carrier_local[:, 2].max() + lift)]
                guide_range = [float(guide_local[:, 2].min()), float(guide_local[:, 2].max())]
                engagement = max(0.0, min(carrier_range[1], guide_range[1])
                                 - max(carrier_range[0], guide_range[0]))
                overlap_z0 = max(carrier_range[0], guide_range[0])
                overlap_z1 = min(carrier_range[1], guide_range[1])
                section_rows = []
                if engagement >= P.GUIDE_MIN_ENGAGEMENT * 1000.0:
                    margin = min(0.05, engagement / 20.0)
                    for section_z in np.linspace(overlap_z0 + margin, overlap_z1 - margin, 9):
                        carrier_section = E.slice_z(carrier_triangles, section_z - lift)
                        guide_section = E.slice_z(guide_triangles, section_z)
                        near_carrier = square_boundary(carrier_section, point, post_half)
                        near_guide = square_boundary(guide_section, point, bore_half)
                        clearance = E.segment_distance(near_carrier, near_guide)
                        section_rows.append({
                            "zMm": round(float(section_z), 6),
                            "carrierSegments": len(near_carrier),
                            "sleeveSegments": len(near_guide),
                            "minimumClearanceMm": (None if clearance is None else round(clearance, 6)),
                            "pass": (len(near_carrier) > 0 and len(near_guide) > 0
                                     and clearance is not None
                                     and abs(clearance - P.GUIDE_CLR * 1000.0) <= 0.01),
                        })
                clearance = min((row["minimumClearanceMm"] for row in section_rows
                                 if row["minimumClearanceMm"] is not None), default=None)
                passed_point = (engagement >= P.GUIDE_MIN_ENGAGEMENT * 1000.0
                                and len(section_rows) == 9
                                and all(row["pass"] for row in section_rows))
                point_rows.append({"xyMm": [round(value, 6) for value in point],
                                   "carrierZRangeMm": [round(value, 6) for value in carrier_range],
                                   "sleeveZRangeMm": [round(value, 6) for value in guide_range],
                                   "continuousEngagementMm": round(engagement, 6),
                                   "minimumSectionClearanceMm": None if clearance is None else round(clearance, 6),
                                   "continuousSectionSamples": section_rows,
                                   "pass": passed_point})
            nominal = E.exact_common_volume(meshes[name], matrix, guide, E.Matrix.Identity(4))
            samples.append({"state": state_id, "servoDeg": degree, "guides": point_rows,
                            "nominalCommonVolumeMm3": nominal,
                            "pass": nominal <= VOLUME_LIMIT_MM3 and all(row["pass"] for row in point_rows)})
        flat_matrix = E.transform_matrix(motion.transforms(P.HOME_SERVO_DEG)[name])
        angle = math.radians(P.FOLLOWER_ANGLES_DEG[index])
        radial = np.asarray((math.cos(angle), math.sin(angle)))
        tangent = np.asarray((-math.sin(angle), math.cos(angle)))
        directions = (("radial-plus", radial), ("radial-minus", -radial),
                      ("tangent-plus", tangent), ("tangent-minus", -tangent))
        negative_cases = []
        sleeve_half = ((P.GUIDE_LUG + 2 * P.GUIDE_CLR + 2 * P.GUIDE_WALL)
                       * 1000.0 / 2.0)
        for point_index, point in enumerate(points):
            target_bounds = ((point[0] - sleeve_half, point[1] - sleeve_half,
                              P.GUIDE_Z0 * 1000.0),
                             (point[0] + sleeve_half, point[1] + sleeve_half,
                              P.GUIDE_Z1 * 1000.0))
            for direction_name, direction in directions:
                expected_contact = (P.GUIDE_CLR * 1000.0
                                    / max(abs(float(direction[0])), abs(float(direction[1]))))

                def common(distance):
                    delta = E.Matrix.Translation((distance * float(direction[0]),
                                                  distance * float(direction[1]), 0.0))
                    return E.exact_common_volume(meshes[name], delta @ flat_matrix,
                                                 guide, E.Matrix.Identity(4))

                low, high = 0.0, min(0.6, expected_contact + 0.1)
                while high < 0.6 and common(high) <= VOLUME_LIMIT_MM3:
                    low, high = high, min(0.6, high + 0.05)
                first_contact = None
                if common(high) > VOLUME_LIMIT_MM3:
                    for _ in range(12):
                        middle = (low + high) / 2.0
                        if common(middle) > VOLUME_LIMIT_MM3:
                            high = middle
                        else:
                            low = middle
                    first_contact = high
                contact_geometry = ({"common_volume_mm3": 0.0,
                                     "intersection_component_bounds_mm": []}
                                    if first_contact is None else E.exact_common_geometry(
                                        meshes[name], E.Matrix.Translation(
                                            (first_contact * float(direction[0]),
                                             first_contact * float(direction[1]), 0.0)) @ flat_matrix,
                                        guide, E.Matrix.Identity(4)))
                first_matching = [component for component in
                                  contact_geometry["intersection_component_bounds_mm"]
                                  if E.bounds_within(component, target_bounds, tolerance=0.01)]
                offset = E.Matrix.Translation((0.5 * float(direction[0]),
                                               0.5 * float(direction[1]), 0.0))
                geometry = E.exact_common_geometry(meshes[name], offset @ flat_matrix,
                                                   guide, E.Matrix.Identity(4))
                matching = [component for component in
                            geometry["intersection_component_bounds_mm"]
                            if E.bounds_within(component, target_bounds, tolerance=0.01)]
                negative_cases.append({"guideIndex": point_index,
                                       "guideCenterMm": [round(value, 6) for value in point],
                                       "direction": direction_name,
                                       "expectedFirstContactMm": expected_contact,
                                       "firstContactMm": first_contact,
                                       "firstContactCommonVolumeMm3":
                                           contact_geometry["common_volume_mm3"],
                                       "firstContactMatchingSleeveComponentBoundsMm": first_matching,
                                       "offsetMm": [round(0.5 * float(direction[0]), 6),
                                                    round(0.5 * float(direction[1]), 6), 0.0],
                                       "commonVolumeMm3": geometry["common_volume_mm3"],
                                       "intersectionComponentBoundsMm":
                                           geometry["intersection_component_bounds_mm"],
                                       "matchingSleeveComponentBoundsMm": matching,
                                       "targetSleeveBoundsMm": target_bounds,
                                       "pass": (first_contact is not None
                                                and abs(first_contact - expected_contact) <= 0.03
                                                and bool(first_matching)
                                                and geometry["common_volume_mm3"] > VOLUME_LIMIT_MM3
                                                and bool(matching))})
        negative = {"cases": negative_cases,
                    "pass": all(case["pass"] for case in negative_cases)}
        rows.append({"group": group, "states": samples,
                     "xyShiftNegativeExample": negative,
                     "pass": all(sample["pass"] for sample in samples) and negative["pass"]})
    passed = rows and all(row["pass"] for row in rows)
    return {"id": "carrier-retention", "label": "4群キャリアの案内保持",
            "status": "pass" if passed else "fail", "minimumEngagementMm": P.GUIDE_MIN_ENGAGEMENT * 1000.0,
            "groups": rows,
            "method": ("各角柱と対応する孔内壁を同一XYの9水平断面で測り、5状態の連続Z係合長を算出。"
                       "各群の局所径方向と接線方向の正負へ0.5mmずらした実メッシュ共通体積を負例とする。")}


def main():
    calibration = E.calibration()
    if not calibration["pass"]:
        raise SystemExit("calibration failed before prototype STL inspection")
    manifest_path = E.BUILD / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    names = tuple(part["id"] for part in manifest["parts"] if not part.get("fit_only"))
    stl_paths = [E.BUILD / f"{name}.stl" for name in names]
    start = E.source_hashes(stl_paths)
    meshes = {name: E.load(name) for name in names}
    interfaces = [
        angular_interface(meshes, "servo_horn", "horn_coupler", "horn-key",
                          "付属ホーンとホーン受けの正逆伝達", 180.0),
        angular_interface(meshes, "drive_key", "cam_disk", "disk-key",
                          "角キーとカム円盤の正逆伝達", 45.0),
        angular_interface(meshes, "drive_key", "horn_coupler", "coupler-key",
                          "ホーン受けと駆動キーの正逆伝達", 45.0),
        axial_retention(meshes), outer_support(meshes), cam_radial_retention(meshes),
        servo_body_retention(meshes, manifest), guide_frame_retention(meshes, manifest),
        carrier_retention(meshes),
    ]
    end = E.source_hashes(stl_paths)
    source_integrity = {"startHashes": start, "endHashes": end, "pass": start == end}
    sources = [HERE / name for name in
               ("params.py", "motion.py", "contact_envelope.py", "model.py",
                "drive.py", "verify.py", "evidence.py")]
    sources.extend((manifest_path, ROOT / "models/sg92r-photo/params.py",
                    ROOT / "models/mystery-box-sg92r-c4/verify.py"))
    source_hashes = E.source_hashes(path for path in sources if path.exists()) | end
    geometry_pass = all(item["status"] == "pass" for item in interfaces) and source_integrity["pass"]
    report = {
        "version": 1, "model": P.MODEL_ID, "calibration": calibration,
        "interfaces": interfaces,
        "overall": {"geometryPass": geometry_pass, "physicalStatus": "conditional" if geometry_pass else "fail",
                    "basis": "実STLのMANIFOLD接触、保持範囲、外周連続性。実機合格ではない。"},
        "hardwareUnknown": ["SG92Rスプラインの実物嵌合", "印刷収縮と摩擦",
                            "保持具の着脱力と繰返し寿命", "天板爪による案内枠の上抜け保持力",
                            "底板爪を介したSG92R保持力"],
        "sourceHashes": source_hashes, "sourceIntegrity": source_integrity,
    }
    E.write_json(E.BUILD / "drive_report.json", report)
    print(json.dumps({"geometryPass": geometry_pass,
                      "interfaces": {item["id"]: item["status"] for item in interfaces},
                      "physicalStatus": report["overall"]["physicalStatus"]}, ensure_ascii=False))
    if not geometry_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
