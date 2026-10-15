"""交換規格の決定論的検査。mechgate の形状検査の代わりにはしない。"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch

import numpy as np

from compose import (C, HERE, MODEL, ROOT, SLOTS, changed_dependencies, checked_transforms, common_params,
                     dependency_hashes, dependency_status, face_package, load_configuration,
                     key_slide_step, key_turn_step, motion_range, qualify, read, rigid, sample_angles,
                     retention_poses, selected_face_sources, world_transform)
from certify import retention_result_passed


def rejected(function):
    try:
        function()
    except (ValueError, KeyError, TypeError, FileNotFoundError):
        return True
    return False


def verify_motion_ranges(check, interface, config, common):
    pixels = read(HERE / "faces" / "three_pixels" / "module.json")
    motion = pixels["motion"]
    angles = sample_angles(motion)
    check("range.explicit_endpoints", motion_range(motion) == (60, 120))
    check("range.explicit_61_poses", np.array_equal(angles, np.arange(60, 121)))
    check("range.physical_home_unchanged", motion["closed_servo_deg"] == 90 and 90 in angles)
    poses = retention_poses(object(), motion, interface, common)
    check("range.retention_mid_and_open", {p["id"]: p["servo_deg"] for p in poses} == {"mid": 90, "open": 120})
    narrower = {key: value for key, value in motion.items() if key != "range_servo_deg"}
    check("range.default_uses_closed_open", motion_range(narrower) == (90, 120)
          and len(sample_angles(narrower)) == 31)
    fallback_poses = retention_poses(object(), narrower, interface, common)
    check("range.default_retention_mid", {p["id"]: p["servo_deg"] for p in fallback_poses}
          == {"mid": 105, "open": 120})
    link_motion = read(HERE / "faces" / "link_lid" / "module.json")["motion"]
    link_angles = sample_angles(link_motion)
    check("range.link_lid_legacy_70_poses", "range_servo_deg" not in link_motion and len(link_angles) == 70
          and np.allclose((link_angles[0], link_angles[-1]),
                          sorted((link_motion["closed_servo_deg"], link_motion["open_servo_deg"]))))
    explicit_config = copy.deepcopy(config)
    explicit_config["slots"]["top"] = {"module": "three_pixels", "rotation_deg": 0, "calibration_deg": 0}
    _, _, explicit_faces = load_configuration(explicit_config, interface)
    check("range.configuration_accepts_explicit", motion_range(explicit_faces["top"]["meta"]["motion"]) == (60, 120))
    kinematics = face_package("three_pixels", "top")["kinematics"]
    low = checked_transforms(kinematics, float(angles[0]), interface, common, pixels["parts"])
    home = checked_transforms(kinematics, motion["closed_servo_deg"], interface, common, pixels["parts"])
    check("range.low_endpoint_preserves_pixel_1", np.isclose(low["pixel_1"][2, 3], -3)
          and all(np.allclose(matrix, np.eye(4)) for matrix in home.values()))
    invalid_bounds = {
        "null": None, "scalar": 60, "string": "60,120", "mapping": {"low": 60, "high": 120},
        "empty": [], "short": [60], "long": [60, 90, 120], "tuple": (60, 120),
        "bool_low": [False, 120], "bool_high": [60, True], "numeric_string": ["60", 120],
        "nan": [float("nan"), 120], "infinity": [60, float("inf")],
        "reversed": [120, 60], "equal": [90, 90], "negative": [-1, 120], "over_180": [60, 181],
        "missing_closed": [91, 120], "missing_open": [60, 119]}
    for name, bounds in invalid_bounds.items():
        invalid = {**motion, "range_servo_deg": bounds}
        check(f"range.reject.{name}", rejected(lambda: motion_range(invalid))
              and rejected(lambda: sample_angles(invalid))
              and rejected(lambda: retention_poses(object(), invalid, interface, common)))
    assembly_outside = {**motion, "closed_servo_deg": 100, "assembly_servo_deg": 90, "range_servo_deg": [95, 120]}
    check("range.reject.missing_assembly", rejected(lambda: motion_range(assembly_outside)))
    for key in ("closed_servo_deg", "open_servo_deg", "assembly_servo_deg"):
        check(f"range.reject.bool_{key}", rejected(lambda: motion_range({**motion, key: True})))
    check("range.calibration_boundary_accepted", motion_range(motion, -60) == (60, 120)
          and motion_range(motion, 60) == (60, 120))
    for calibration in (-60.1, 60.1, True, float("nan")):
        check(f"range.reject.calibration_{calibration}", rejected(lambda: motion_range(motion, calibration)))
    invalid_config = copy.deepcopy(explicit_config)
    invalid_config["slots"]["top"]["calibration_deg"] = -61
    check("range.configuration_rejects_calibration", rejected(lambda: load_configuration(invalid_config, interface)))
    invalid_metadata = copy.deepcopy(pixels)
    invalid_metadata["motion"]["range_servo_deg"] = [90, 90]
    def invalid_read(path):
        return invalid_metadata if Path(path) == HERE / "faces" / "three_pixels" / "module.json" else read(path)
    with patch("compose.read", side_effect=invalid_read):
        check("range.configuration_rejects_invalid", rejected(lambda: load_configuration(explicit_config, interface)))


def verify(require_outputs=True):
    rows = []

    def check(name, condition, detail=""):
        rows.append({"id": name, "pass": bool(condition), "detail": detail})

    interface, config, faces = load_configuration()
    common = common_params()
    verify_motion_ranges(check, interface, config, common)
    key_definition = interface["mount"]["keys"]
    check("mount.release_geometry_declared", "release_rotation_deg" in key_definition
          and "release_pivot_uv_mm" in key_definition)
    for slot, face in faces.items():
        S = face["S"]
        check(f"{slot}.right_handed", np.isclose(np.linalg.det(S[:3, :3]), 1))
        local = C.rotation((1, 0, 0), 17, (0, -12, 3)) @ C.translation(0.3, 0.2, 0.1)
        point = np.array([1.3, 4.2, 7.9, 1])
        check(f"{slot}.conjugation", np.allclose(world_transform(S, local) @ (S @ point), S @ local @ point))
        if "release_rotation_deg" in key_definition and "release_pivot_uv_mm" in key_definition:
            for index, key in enumerate(("key_l", "key_r")):
                plan = C.AssemblyPlan()
                part_id = qualify(slot, key)
                plan.place("initial", "initial", [part_id])
                key_turn_step(plan, slot, key, index, face, interface, True, "release")
                key_slide_step(plan, slot, key, index, face, interface, 0, 50, "out")
                key_slide_step(plan, slot, key, index, face, interface, 50, 0, "in")
                key_turn_step(plan, slot, key, index, face, interface, False, "lock")
                continuous = all(np.allclose(a["frames"][-1]["transforms"][part_id],
                                             b["frames"][0]["transforms"][part_id], atol=1e-8)
                                 for a, b in zip(plan.steps[:-1], plan.steps[1:]))
                check(f"{slot}.{key}.exchange_continuity", continuous)
                check(f"{slot}.{key}.exchange_final_identity", np.allclose(plan.state[part_id], np.eye(4)))
        modules = face_package(face["config"]["module"], slot)
        motion = face["meta"].get("motion")
        angles = sample_angles(motion) if motion else [0, 90, 180]
        all_transforms = [checked_transforms(modules["kinematics"], angle, interface, common,
                                           face["meta"]["parts"]) for angle in angles]
        check(f"{slot}.complete_ids", all(set(row) == set(face["meta"]["parts"]) for row in all_transforms))
        if motion:
            poses = retention_poses(modules["kinematics"], motion, interface, common)
            check(f"{slot}.retention_pose_ids", {pose["id"] for pose in poses} == {"mid", "open"})
            for pose in poses:
                posed = checked_transforms(modules["kinematics"], pose["servo_deg"], interface, common,
                                           face["meta"]["parts"])
                check(f"{slot}.retention.{pose['id']}.complete_ids", set(posed) == set(face["meta"]["parts"]))
            check(f"{slot}.monotonic_servo", np.all(np.diff(angles) > 0) and np.max(np.diff(angles)) <= 1 + 1e-8)
            low, high = motion_range(motion, face["config"].get("calibration_deg", 0))
            check(f"{slot}.endpoints", np.isclose(angles[0], low) and np.isclose(angles[-1], high))
            closed = checked_transforms(modules["kinematics"], motion["closed_servo_deg"], interface, common,
                                        face["meta"]["parts"])
            check(f"{slot}.closed_identity", all(np.allclose(m, np.eye(4), atol=1e-7) for m in closed.values()))
            check(f"{slot}.nonzero_motion", any(not np.allclose(row[p], np.eye(4), atol=1e-6)
                  for row in all_transforms for p in row))
            # Finite differences catch branch jumps, not only valid endpoint matrices.
            increments = [C.rotation_angle_deg(b[p] @ np.linalg.inv(a[p]))
                          for a, b in zip(all_transforms[:-1], all_transforms[1:]) for p in a]
            check(f"{slot}.continuous_kinematics", max(increments, default=0) <= 5,
                  f"largest part rotation per sample={max(increments, default=0):.6f}deg")
        else:
            check(f"{slot}.blank_static", all(np.allclose(m, np.eye(4)) for row in all_transforms for m in row.values()))
        declared = set(face["meta"]["parts"])
        for item in face["meta"].get("interfaces", []):
            references = ([item[k] for k in ("part", "driver", "driven") if k in item]
                          + item.get("parts", []) + item.get("against", []))
            check(f"{slot}.interface.{item['id']}", bool(references) and set(references) <= declared)
        for index, allowance in enumerate(face["meta"].get("allowances", [])):
            references = {part for pair in allowance.get("pairs", []) for part in pair}
            check(f"{slot}.allowance.{index}.references", bool(references) and references <= declared)
    invalid = copy.deepcopy(config)
    invalid["slots"]["front"]["module"] = "../blank"
    check("reject.path_traversal", rejected(lambda: load_configuration(invalid, interface)))
    invalid = copy.deepcopy(config)
    invalid["slots"]["front"]["rotation_deg"] = 180
    check("reject.rotation", rejected(lambda: load_configuration(invalid, interface)))
    invalid = copy.deepcopy(config)
    del invalid["slots"]["back"]
    check("reject.missing_slot", rejected(lambda: load_configuration(invalid, interface)))
    invalid = copy.deepcopy(config)
    invalid["slots"]["front"]["module"] = "not_a_module"
    check("reject.unknown_module", rejected(lambda: load_configuration(invalid, interface)))
    invalid = copy.deepcopy(config)
    invalid["slots"]["bottom"]["module"] = "link_lid"
    check("reject.unsupported_bottom_slot", rejected(lambda: load_configuration(invalid, interface)))
    invalid = copy.deepcopy(config)
    invalid["interface"] = "resident-face-v0"
    check("reject.interface_version", rejected(lambda: load_configuration(invalid, interface)))
    reflected = np.diag([1, 1, -1, 1])
    check("reject.reflection", rejected(lambda: rigid(reflected)))
    check("reject.nonlocal_id", rejected(lambda: qualify("front", "right/lid")))
    hashes = dependency_hashes()
    selected_modules = {row["module"] for row in config["slots"].values()}
    selected_sources = selected_face_sources(config)
    check("dependencies.include_selected_faces", bool(selected_sources) and
          all(p.relative_to(ROOT).as_posix() in hashes for p in selected_sources))
    unselected_prefixes = [(directory.relative_to(ROOT).as_posix() + "/")
                           for directory in (HERE / "faces").iterdir()
                           if directory.is_dir() and directory.name not in selected_modules]
    check("dependencies.exclude_unselected_faces", all(not any(path.startswith(prefix)
          for prefix in unselected_prefixes) for path in hashes))
    face_prefix = (HERE / "faces").relative_to(ROOT).as_posix() + "/"
    check("dependencies.exclude_face_generated_outputs", all(
        not {"build", "__pycache__", "_local"}.intersection(Path(path).parts[:-1])
        for path in hashes if path.startswith(face_prefix)))
    pruned = []
    def generated_walk(directory):
        children = ["build", "__pycache__", "_local"]
        yield str(directory), children, ["module.json", "params.py", "README.md"]
        pruned.append(not children)
    with patch("compose.os.walk", side_effect=generated_walk):
        generated_sources = selected_face_sources(config)
    check("dependencies.prune_generated_directories", bool(pruned) and all(pruned)
          and all(path.name in {"module.json", "params.py"} for path in generated_sources))
    slots_path = (HERE / "slots.json").relative_to(ROOT).as_posix()
    check("dependencies.include_slots", slots_path in hashes)
    changed_slots = copy.deepcopy(config)
    for slot in changed_slots["slots"].values():
        slot["module"] = "blank"
    if selected_modules == {"blank"}:
        changed_slots["slots"]["front"]["module"] = "link_lid"
    original_slots_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    changed_slots_hash = hashlib.sha256(json.dumps(changed_slots, sort_keys=True).encode()).hexdigest()
    check("dependencies.detect_slots_change", changed_dependencies(
          {slots_path: original_slots_hash}, {slots_path: changed_slots_hash}) == [slots_path])
    check("dependencies.selection_follows_slots", selected_face_sources(changed_slots) != selected_sources)
    check("dependencies.include_reference", all(f"models/sg92r-photo/{p}" in hashes for p in ("params.py", "model.py")))
    check("dependencies.detect_changed_hash", changed_dependencies({"face": "old"}, {"face": "new"}) == ["face"])
    check("dependencies.detect_added_source", changed_dependencies({}, {"face": "new"}) == ["face"])
    check("dependencies.detect_deleted_source", changed_dependencies({"face": "old"}, {}) == ["face"])
    check("dependencies.accept_identical", changed_dependencies(hashes, hashes) == [])
    valid_retention = {"ok": True, "calibration": {"pass": True},
                       "retention": [{"id": "a", "pass": True}, {"id": "b", "pass": True}]}
    check("retention.accept_complete_calibrated", retention_result_passed(valid_retention, ["a", "b"]))
    invalid_retention = copy.deepcopy(valid_retention)
    invalid_retention["calibration"]["pass"] = False
    check("retention.reject_bad_calibration", not retention_result_passed(invalid_retention, ["a", "b"]))
    invalid_retention = copy.deepcopy(valid_retention)
    invalid_retention["retention"].pop()
    check("retention.reject_missing_result", not retention_result_passed(invalid_retention, ["a", "b"]))
    invalid_retention = copy.deepcopy(valid_retention)
    invalid_retention["retention"][0]["pass"] = False
    check("retention.reject_failed_interface", not retention_result_passed(invalid_retention, ["a", "b"]))
    check("retention.reject_empty", not retention_result_passed({"ok": True, "calibration": {"pass": True}}, []))
    if require_outputs:
        fresh, changed = dependency_status()
        check("dependencies.fresh", fresh, changed)
        cases = read(HERE / "build" / "cases.json")
        check("cases.every_active_slot", set(cases["models"]) ==
              {f"{MODEL}/checks/{s}" for s, f in faces.items() if f["meta"].get("motion")})
        retention_index = read(HERE / "build" / "retention_cases.json")
        expected_retention_cases = {f"{slot}/{pose}" for slot, face in faces.items()
                                    if face["meta"].get("motion") for pose in ("mid", "open")}
        check("retention.every_active_pose", {case["id"] for case in retention_index["cases"]} == expected_retention_cases)
        root_manifest = read(HERE / "build" / "manifest.json")
        root_ids = {part["id"] for part in root_manifest["parts"]}
        from verify_envelopes import read_triangles, transform_triangles
        root_meshes = {part["id"]: read_triangles(HERE / part["assembly"]) for part in root_manifest["parts"]}
        for case in retention_index["cases"]:
            job = read(HERE / case["job"])
            target = read(HERE / "checks" / case["slot"] / "build" / "motion.json")["frames"]
            static = sorted(part for part in root_ids if all(
                            frame["transforms"][part] == target[0]["transforms"][part] for frame in target))
            check(f"retention.{case['id']}.all_parts", set(job["parts"]) == root_ids and
                  all(Path(path).is_file() for path in job["parts"].values()))
            check(f"retention.{case['id']}.static_classification", job["static_parts"] == static)
            check(f"retention.{case['id']}.scope", "motion" not in job and "assembly" not in job
                  and not job["print_parts"] and all(i["type"] == "retention" for i in job["interfaces"]))
            check(f"retention.{case['id']}.complete_interfaces", [item["id"] for item in job["interfaces"]] == case["retention_ids"])
            pose_file = (HERE / case["job"]).with_name("pose.json")
            pose_data = read(pose_file)
            baselines = pose_data["baseline_transforms"]
            check(f"retention.{case['id']}.identity_baseline", set(baselines) == root_ids and all(
                np.allclose(C.from_column_major(matrix), np.eye(4)) for matrix in baselines.values()))
            mismatched = []
            for part, path in job["parts"].items():
                expected_mesh = transform_triangles(root_meshes[part],
                    C.from_column_major(pose_data["baked_transforms"][part]))
                actual_mesh = read_triangles(Path(path))
                # Both files are float32 STL; this tolerance only covers their numeric round trip.
                if actual_mesh.shape != expected_mesh.shape or not np.allclose(actual_mesh, expected_mesh, atol=1e-4, rtol=0):
                    mismatched.append(part)
            check(f"retention.{case['id']}.actual_baked_meshes", not mismatched, mismatched)
        expected = {qualify(s, p) for s, f in faces.items() for p in f["meta"]["parts"]}
        for name in [MODEL] + cases["models"]:
            directory = ROOT / "models" / name
            manifest = read(directory / "build" / "manifest.json")
            ids = [row["id"] for row in manifest["parts"]]
            check(f"{name}.unique_ids", len(set(ids)) == len(ids))
            check(f"{name}.prefixes", expected <= set(ids) and all(i.split("/")[0] in set(SLOTS) | {"frame"} for i in ids))
            spec = read(directory / "spec.json")
            for item in spec["interfaces"]:
                references = ([item[k] for k in ("part", "driver", "driven") if k in item]
                              + item.get("parts", []) + item.get("against", []))
                check(f"{name}.interface.{item['id']}", set(references) <= set(ids))
            saved_motion = read(directory / "build" / "motion.json")
            source_motion = faces[saved_motion["slot"]]["meta"]["motion"]
            expected_angles = sample_angles(source_motion)
            saved_angles = [frame["servo_deg"] for frame in saved_motion["frames"]]
            check(f"{name}.saved_range", len(saved_angles) == len(expected_angles)
                  and np.allclose(saved_angles, expected_angles))
            check(f"{name}.physical_home", np.isclose(saved_motion["home_servo_deg"], source_motion["closed_servo_deg"]))
            for frame in saved_motion["frames"]:
                check(f"{name}.frame.{frame['servo_deg']:.5f}", set(frame["transforms"]) == set(ids))
            assembly = read(directory / "build" / "assembly.json")
            previous = {}
            boundary_errors = []
            for step in assembly["steps"]:
                first = step["frames"][0]["transforms"]
                for part in set(first) & set(previous):
                    if not np.allclose(first[part], previous[part], atol=1e-6):
                        boundary_errors.append(f"{step['id']}:{part}")
                previous = step["frames"][-1]["transforms"]
            check(f"{name}.assembly_continuity", not boundary_errors, boundary_errors)
            check(f"{name}.assembly_final", set(previous) == set(ids) and
                  all(np.allclose(C.from_column_major(m), np.eye(4), atol=1e-6) for m in previous.values()))
    return {"pass": all(row["pass"] for row in rows), "checks": rows,
            "scope": "規格・識別子・運動学・入力鮮度。物理検査と実物適合はmechgateと試し刷りで確認。"}


def main():
    try:
        report = verify("--sources-only" not in sys.argv)
    except (ValueError, KeyError, TypeError, FileNotFoundError) as error:
        print(f"FAIL contract: {error}")
        return 1
    for row in report["checks"]:
        if not row["pass"]:
            print(f"FAIL {row['id']}: {row['detail']}")
    if "--sources-only" not in sys.argv:
        C.write_json(HERE / "build" / "contract_report.json", report)
    print(f"contract: {sum(r['pass'] for r in report['checks'])}/{len(report['checks'])} passed")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
