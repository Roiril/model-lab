"""完成時の形状・運動表・配送ファイルを独立に照合する。"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import struct
import sys
import tempfile

from lattice_web import read_mesh

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes_match(records):
    if not records:
        return False
    for relative, expected in records.items():
        path = (ROOT / relative).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError:
            return False
        if not path.is_file() or digest(path) != expected:
            return False
    return True


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def topology(path):
    mesh = read_mesh(path)
    indices = mesh["triangles"]
    faces = [tuple(indices[i:i + 3]) for i in range(0, len(indices), 3)]
    edges = Counter(tuple(sorted(edge)) for a, b, c in faces for edge in ((a, b), (b, c), (c, a)))
    duplicate = len(faces) - len({tuple(sorted(f)) for f in faces})
    bad_edges = sum(count != 2 for count in edges.values())
    collapsed = sum(len(set(f)) != 3 for f in faces)
    parents = list(range(len(mesh["vertices"]) // 3))
    def root(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index
    for a, b, c in faces:
        parents[root(b)] = root(a)
        parents[root(c)] = root(a)
    components = len({root(i) for i in range(len(parents))})
    component_min_z = {}
    for index in range(len(parents)):
        group = root(index)
        z = mesh["vertices"][index * 3 + 2]
        component_min_z[group] = min(z, component_min_z.get(group, z))
    z_min = min(mesh["vertices"][2::3])
    return {"triangles": len(faces), "bad_edges": bad_edges, "duplicate_faces": duplicate,
            "collapsed_faces": collapsed, "components": components, "min_z_mm": z_min,
            "component_min_z_mm": sorted(component_min_z.values()),
            "ok": not (bad_edges or duplicate or collapsed)}


def calibrate_topology():
    points = ((0., 0., 0.), (1., 0., 0.), (0., 1., 0.), (0., 0., 1.))
    faces = ((0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3))
    temporary_root = ROOT / ".codex-tmp"
    temporary_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lattice-audit-", dir=temporary_root) as temporary:
        results = []
        samples = ((points, faces), (points, faces[:-1]),
                   (points + tuple((x + 3, y, z) for x, y, z in points),
                    faces + tuple(tuple(i + 4 for i in f) for f in faces)))
        for sample_points, subset in samples:
            path = Path(temporary) / f"{len(subset)}.stl"
            raw = bytearray(80) + struct.pack("<I", len(subset))
            for face in subset:
                raw.extend(struct.pack("<12fH", 0., 0., 0., *(v for i in face for v in sample_points[i]), 0))
            path.write_bytes(raw)
            results.append(topology(path))
    return {"ok": results[0]["ok"] and not results[1]["ok"] and
                   results[0]["components"] == 1 and results[2]["components"] == 2,
            "closed_bad_edges": results[0]["bad_edges"], "opened_bad_edges": results[1]["bad_edges"],
            "joined_components": results[0]["components"], "separate_components": results[2]["components"]}


def audit(model):
    folder = ROOT / "models" / model
    build = folder / "build"
    read = lambda name: json.loads((build / name).read_text(encoding="utf-8"))
    manifest, motion, delivery, verify = (read(name) for name in (
        "manifest.json", "motion.json", "delivery_report.json", "verify_report.json"))
    checks = {}
    checks["audit_completed"] = True
    calibration = calibrate_topology()
    checks["independent_topology_calibration"] = calibration["ok"]
    parts = {p["id"]: p for p in manifest["parts"] if not p.get("fit_only")}
    checks["manifest_matches_delivery"] = digest(build / "manifest.json") == delivery["manifest"]["sha256"]
    checks["current_sources_match_delivery"] = all(
        digest(ROOT / p["source_print"]["file"]) == p["source_print"]["sha256"]
        for p in delivery["parts"] if "source_print" in p)
    checks["delivered_files_match_hashes"] = all(
        digest(ROOT / record["file"]) == record["sha256"] for record in delivery["artifacts"])
    checks["source_and_delivered_stl_match"] = all(
        p["source_print"]["sha256"] == p["delivered_print"]["sha256"]
        for p in delivery["parts"] if "source_print" in p)
    geometry = {p["id"]: topology(folder / p["print"]) for p in manifest["parts"] if p.get("print")}
    checks["print_stl_topology"] = all(row["ok"] for row in geometry.values())
    solid_evidence = read("boolean_evidence.json")
    solid_rows = (solid_evidence.get("assemblyStls", []) + solid_evidence.get("printStls", []) +
                  solid_evidence.get("deliveredPrintStls", []))
    checks["boolean_geometry_calibrated"] = bool(solid_evidence.get("calibration")) and all(
        row.get("pass") is True for row in solid_evidence["calibration"])
    checks["boolean_geometry_algorithm_fresh"] = source_hashes_match(solid_evidence.get("algorithmSha256"))
    checks["boolean_geometry_all_solids_valid"] = bool(solid_rows) and all(
        row.get("exists") and row.get("geometryValidClosedSolid") for row in solid_rows)
    checks["boolean_geometry_sources_fresh"] = bool(solid_rows) and source_hashes_match({
        row["path"]: row["sha256"] for row in solid_rows if row.get("exists")})
    checks["boolean_geometry_assembly_complete"] = {
        (folder / part["assembly"]).relative_to(ROOT).as_posix() for part in manifest["parts"]
    } == {row.get("path") for row in solid_evidence.get("assemblyStls", [])}
    checks["boolean_geometry_print_complete"] = {
        (folder / part["print"]).relative_to(ROOT).as_posix() for part in manifest["parts"] if part.get("print")
    } == {row.get("path") for row in solid_evidence.get("printStls", [])}
    if model.endswith("c4"):
        hole_evidence = read("hole_clearance.json")
        checks["hex_holes_geometry_clear"] = (hole_evidence.get("pass") is True and
            hole_evidence.get("calibration", {}).get("pass") is True and len(hole_evidence.get("holes", [])) == 19 and
            all(row.get("pass") is True and finite_number(row.get("common_volume_mm3")) and
                row["common_volume_mm3"] <= .001 for row in hole_evidence["holes"]))
        checks["hex_holes_evidence_fresh"] = source_hashes_match(hole_evidence.get("source_sha256"))
    checks["print_parts_connected"] = all(
        geometry[p["id"]]["components"] == p.get("expected_print_components", 1)
        for p in manifest["parts"] if p.get("print"))
    checks["print_parts_on_bed"] = all(abs(z) < .001
        for row in geometry.values() for z in row["component_min_z_mm"])
    frames = motion["frames"]
    checks["frame_angles_increase"] = all(a["servo_deg"] < b["servo_deg"] for a, b in zip(frames, frames[1:]))
    checks["motion_parts_exist"] = all(set(frame["transforms"]) <= parts.keys() for frame in frames)
    checks["motion_matrices_finite"] = all(len(m) == 16 and all(math.isfinite(v) for v in m)
        for frame in frames for m in frame["transforms"].values())
    combined = read_mesh(ROOT / "exports" / f"{model}.stl")["vertices"]
    bounds = [[min(combined[k::3]), max(combined[k::3])] for k in range(3)]
    size = [round(b - a, 4) for a, b in bounds]
    checks["closed_export_dimensions"] = all(abs(a - b) < .01 for a, b in zip(size, manifest["meta"]["dimensions_mm"]))
    web = json.loads((ROOT / "viewer/lattice/assets" / f"{model}.json").read_text(encoding="utf-8"))
    checks["web_parts_match"] = set(parts) == {p["id"] for p in web["parts"]}
    checks["web_meshes_match_assembly"] = all(
        part["mesh"] == read_mesh(folder / parts[part["id"]]["assembly"]) for part in web["parts"])
    checks["web_motion_matches"] = web["motion"] == motion
    checks["web_reports_match"] = web["verify"] == verify and web["delivery"] == delivery
    checks["web_solid_evidence_matches"] = web.get("boolean_evidence") == solid_evidence
    if model.endswith("c4"):
        checks["web_hex_hole_evidence_matches"] = web.get("hole_clearance") == hole_evidence
    assembly, assembly_report, sim_tables, sim_report, drive_report = (read(name) for name in (
        "assembly.json", "assembly_report.json", "sim_tables.json", "simulate_report.json",
        "drive_report.json"))
    checks["web_workflows_match_reports"] = (web.get("assembly") == assembly and
        web.get("simTables") == sim_tables and web.get("sim") == sim_report and
        web.get("drive") == drive_report)
    interfaces = {row.get("id"): row for row in drive_report.get("interfaces", [])}
    required_interfaces = {"horn-receiver", "servo-seat", "canonical-reference",
                           "cam-followers", "retention"}
    if model.endswith("c3"):
        required_interfaces |= {"gear-mesh", "shaft-cam_gear", "shaft-left_spacer",
                                *(f"shaft-cam_{index}" for index in range(5))}
    else:
        required_interfaces |= {"coupler-shaft", "coupler-structure", "shaft-cam_center",
                                "shaft-cam_inner", "shaft-cam_outer"}
    checks["drive_required_interfaces_present"] = required_interfaces <= interfaces.keys()
    checks["drive_required_interfaces_pass"] = all(
        interfaces.get(interface, {}).get("status") == "pass" for interface in required_interfaces)
    checks["drive_interface_statuses_valid"] = all(
        row.get("status") in {"pass", "unknown"} for row in drive_report.get("interfaces", []))
    checks["drive_spline_remains_unknown"] = (
        interfaces.get("servo-spline", {}).get("status") == "unknown" and
        any("スプライン" in str(item) for item in drive_report.get("hardwareUnknown", [])))
    checks["drive_source_hashes_match"] = source_hashes_match(drive_report.get("sourceHashes"))
    checks["drive_calibration_passes"] = bool(drive_report.get("calibration")) and all(
        row.get("pass") is True for row in drive_report.get("calibration", []))
    checks["drive_calibration_schema"] = all(
        set(row) >= {"id", "label", "pass", "detail"} and bool(row.get("id")) and bool(row.get("label"))
        for row in drive_report.get("calibration", []))
    calibration_ids = {row.get("id") for row in drive_report.get("calibration", [])}
    required_calibration = {"known-gap", "key-contact", "round-hole", "missing-shape",
                            "follower-gap", "pullout-volume", "keeper-removed", "rear-surface-contact", "horn-axis-offset",
                            "manifold-volume", "manifold-open-input", "solid-input-geometry", "canonical-surface"}
    if model.endswith("c3"):
        required_calibration |= {"gear-missing", "gear-separated", "gear-center-offset", "gear-half-tooth",
                                 "shaft-cap-positive-volume"}
    else:
        required_calibration.add("blind-floor-thickness")
    checks["drive_negative_calibrations_present"] = required_calibration <= calibration_ids
    horn = interfaces.get("horn-receiver", {})
    servo_seat = interfaces.get("servo-seat", {})
    canonical = interfaces.get("canonical-reference", {})
    followers = interfaces.get("cam-followers", {})
    retention = interfaces.get("retention", {})
    checks["drive_primary_volume_solver"] = retention.get("primarySolver") == "MANIFOLD"
    checks["drive_horn_measurements_present"] = (
        finite_number(horn.get("nearestGapMm")) and finite_number(horn.get("totalAngularPlayDeg")) and
        len(horn.get("contactAnglesDeg", [])) == 2 and all(finite_number(value) for value in horn["contactAnglesDeg"]))
    checks["drive_servo_seat_measurements_present"] = (
        all(len(servo_seat.get(key, [])) == 2 and all(finite_number(value) for value in servo_seat[key])
            for key in ("shaftRangeXmm", "socketRangeXmm")) and
        all(finite_number(servo_seat.get(key)) for key in (
            "nominalEngagementMm", "axisOffsetMm", "minimumRetainedEngagementMm",
            "receiverMouthXmm", "blindStartXmm", "minimumArmEngagementMm")))
    checks["drive_canonical_measurements_present"] = bool(canonical.get("parts")) and all(
        finite_number(row.get("maximumVertexDifferenceMm")) and
        finite_number(row.get("maximumSurfaceDifferenceMm")) and row["maximumSurfaceDifferenceMm"] <= .003 and
        finite_number(row.get("expectedSurfaceAreaMm2")) and finite_number(row.get("actualSurfaceAreaMm2")) and
        finite_number(row.get("surfaceAreaDifferenceMm2")) and row.get("pass") is True
        for row in canonical.get("parts", []))
    if model.endswith("c4"):
        floor = interfaces.get("coupler-structure", {})
        checks["drive_coupler_structure_measurements_present"] = (
            finite_number(floor.get("minimumAxialThicknessMm")) and
            floor["minimumAxialThicknessMm"] >= 1.2 - .002 and floor.get("projectionSamples", 0) > 0 and
            len(floor.get("sections", [])) == 3 and all(row.get("pass") is True and
                row.get("coveredSamples") == row.get("totalSamples") for row in floor["sections"]))
    follower_fields = {"servoDeg", "group", "contactYmm", "camTopZmm",
                       "followerBottomZmm", "gapMm", "active", "pass"}
    checks["drive_follower_measurements_present"] = bool(followers.get("samples")) and all(
        follower_fields <= row.keys() and finite_number(row.get("servoDeg")) and
        finite_number(row.get("contactYmm")) and finite_number(row.get("camTopZmm")) and
        (not row.get("active") or (finite_number(row.get("followerBottomZmm")) and
                                   finite_number(row.get("gapMm"))))
        for row in followers.get("samples", []))
    retention_fields = {"servoDeg", "firstStopMm", "baselineCommonVolumeMm3",
                        "stopProbeCommonVolumeMm3"}
    retention_cases = {case.get("id"): case for case in retention.get("cases", [])}
    if model.endswith("c3"):
        required_retention_cases = {
            "drive-plus", "drive-minus", "drive-lift", "drive-clip-pull",
            "shaft-plus", "shaft-minus", "cap-right", "cap-left", "horn-rear", "horn-seat",
            *(f"{name}-{direction}" for name in
              ("cam_0", "cam_1", "cam_2", "cam_3", "cam_4", "cam_gear", "left_spacer")
              for direction in ("plus", "minus")),
        }
    else:
        required_retention_cases = {"shaft-plus", "shaft-minus", "keeper-pull", "coupler-plus", "horn-rear",
                                    "coupler-minus", "horn-seat", "joint-up", "joint-down"}
    checks["drive_required_retention_cases_present"] = required_retention_cases <= retention_cases.keys()
    checks["drive_required_retention_cases_pass"] = all(
        retention_cases.get(identifier, {}).get("pass") is True
        for identifier in required_retention_cases)
    if model.endswith("c3"):
        stack = retention.get("axialStack", {})
        gaps, cap_travel = stack.get("clearancesMm", []), stack.get("capSeatTravelMm", [])
        checks["drive_stack_includes_cap_travel"] = (len(gaps) == 8 and len(cap_travel) == 2 and
            all(finite_number(value) for value in gaps + cap_travel) and
            finite_number(stack.get("totalFreeTravelMm")) and abs(
                stack["totalFreeTravelMm"] - sum(gaps) - sum(cap_travel)) < .00002)
        follower_bounds = stack.get("followerSupportBounds", {})
        checks["drive_stack_follower_travel_bounded"] = (set(follower_bounds) == {f"cam_{i}" for i in range(5)} and
            all(row.get("pass") is True and finite_number(row.get("minimumRemainingSupportMm")) and
                row["minimumRemainingSupportMm"] >= .1 and abs(row["minimumRemainingSupportMm"] - min(
                    row["leftMarginMm"] - row["leftTravelMm"], row["rightMarginMm"] - row["rightTravelMm"])) < .00002
                for row in follower_bounds.values()))
        checks["drive_end_parts_stop_at_caps"] = all(
            retention_cases.get(identifier, {}).get("samples") and all(
                row.get("expectedStopPart") == expected and
                finite_number(row.get("expectedStopPartProbeVolumeMm3")) and
                row["expectedStopPartProbeVolumeMm3"] > .001
                for row in retention_cases[identifier]["samples"])
            for identifier, expected in (("left_spacer-minus", "cap_left"), ("cam_4-plus", "cap_right")))
    checks["drive_retention_measurements_present"] = bool(retention.get("cases")) and all(
        finite_number(case.get("maximumTravelMm")) and bool(case.get("samples")) and
        all(finite_number(row.get("servoDeg")) and finite_number(row.get("firstStopMm")) and
            ((case.get("id") == "horn-rear" and case.get("method") == "rear-surface-first-contact" and
              row.get("supportSamples", 0) > 0 and row.get("pass") is True and
              finite_number(row.get("minimumSignedGapMm")) and finite_number(row.get("maximumSignedGapMm")) and
              finite_number(row.get("beforeContactGapMm")) and finite_number(row.get("afterContactGapMm"))) or
             (retention_fields <= row.keys() and finite_number(row.get("baselineCommonVolumeMm3")) and
              finite_number(row.get("stopProbeCommonVolumeMm3")))) for row in case.get("samples", []))
        for case in retention.get("cases", []))
    checks["drive_solver_fallbacks_are_closed_measurements"] = all(
        row.get("inputMeshesClosed") is True and row.get("failedSolver") == "EXACT" and
        row.get("measuredSolver") == "MANIFOLD" and bool(row.get("case")) and
        len(row.get("parts", [])) == 2 and len(row.get("offsetMm", [])) == 3 and
        all(finite_number(value) for value in row["offsetMm"]) and
        finite_number(row.get("closedBoundaryVolumeMm3")) and row["closedBoundaryVolumeMm3"] >= 0
        for row in retention.get("solverFallbacks", []))
    if model.endswith("c3"):
        gear = interfaces.get("gear-mesh", {})
        checks["drive_gear_measurements_present"] = (
            len(gear.get("actualTeeth", [])) == 2 and all(finite_number(value) for value in gear["actualTeeth"]) and
            len(gear.get("actualTipRadiusMm", [])) == 2 and all(finite_number(value) for value in gear["actualTipRadiusMm"]) and
            all(finite_number(gear.get(key)) for key in ("faceWidthOverlapMm", "centerDistanceMm", "contactRatio")) and
            bool(gear.get("samples")) and all(
                finite_number(row.get("servoDeg")) and len(row.get("contactAnglesDeg", [])) == 2 and
                all(finite_number(value) for value in row["contactAnglesDeg"])
                for row in gear.get("samples", [])))
    checks["drive_geometry_is_conditional"] = (
        drive_report.get("overall", {}).get("geometryPass") is True and
        drive_report.get("overall", {}).get("physicalStatus") == "conditional" and
        bool(drive_report.get("hardwareUnknown")) and
        drive_report.get("overall", {}).get("physicalStatus") != "pass")
    checks["assembly_display_paths_pass"] = assembly["pass"] and assembly_report["pass"]
    checks["assembly_path_calibration"] = assembly["calibration"]["pass"]
    checks["assembly_sources_match"] = (set(assembly["source_sha256"]) == set(parts) and all(
        digest(folder / parts[key]["assembly"]) == value
        for key, value in assembly["source_sha256"].items()))
    checks["assembly_algorithms_match"] = (
        assembly.get("algorithm_sha256") == assembly_report.get("algorithm_sha256") and
        source_hashes_match(assembly.get("algorithm_sha256")) and
        assembly_report.get("algorithmIntegrity") is True)
    checks["assembly_final_and_reverse_pass"] = (assembly_report["finalState"]["pass"] and
        assembly_report["reverseDisassembly"]["pass"])
    continuity = coverage = rigidity = True
    previous = None
    for step in assembly["steps"]:
        step_frames = step["frames"]
        presence = set(step["installed"]) | set(step["moving"])
        coverage &= all(set(frame["transforms"]) == presence for frame in step_frames)
        coverage &= (step_frames[0]["progress"] == 0 and step_frames[-1]["progress"] == 1 and
            all(a["progress"] < b["progress"] for a, b in zip(step_frames, step_frames[1:])))
        pairs = {tuple(sorted(pair)) for pair in itertools.combinations(presence, 2)
                 if set(pair) & set(step["moving"])}
        recorded_pairs = {tuple(sorted(row["parts"])) for row in step["report"]["pairs"]}
        coverage &= pairs == recorded_pairs and all(
            row["samples"] == len(step_frames) and
            row["aabbZeroSamples"] + row["exactSamples"] == row["samples"]
            for row in step["report"]["pairs"])
        if previous:
            current = step_frames[0]["transforms"]
            continuity &= set(previous) <= set(current) and all(
                max(abs(a - b) for a, b in zip(previous[key], current[key])) < 1e-6
                for key in previous)
        for frame in step_frames:
            for matrix in frame["transforms"].values():
                rigidity &= len(matrix) == 16 and all(math.isfinite(v) for v in matrix)
                for c in range(3):
                    for d in range(3):
                        rigidity &= abs(sum(matrix[4*c+k] * matrix[4*d+k] for k in range(3))
                                        - (1 if c == d else 0)) < 2e-6
        previous = step_frames[-1]["transforms"]
    identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    checks["assembly_all_frames_covered"] = bool(coverage)
    checks["assembly_between_steps_continuous"] = bool(continuity)
    checks["assembly_transforms_rigid"] = bool(rigidity)
    checks["assembly_ends_in_actual_geometry"] = (set(previous) == set(parts) and all(
        max(abs(a-b) for a, b in zip(matrix, identity)) < 1e-6 for matrix in previous.values()))
    simulation_overall = sim_report.get("overall", {})
    checks["simulation_is_conditional_calculation"] = (
        simulation_overall.get("pass") is False and
        simulation_overall.get("status") == "conditional" and
        simulation_overall.get("calculationPass") is True and
        simulation_overall.get("geometryPass") is True and
        sim_report.get("driveGeometry", {}).get("geometryPass") is True and
        sim_report.get("driveGeometry", {}).get("sourceHashesFresh") is True and
        all(row.get("pass") is True for row in sim_report.get("calibration", [])))
    checks["simulation_sources_match"] = sim_tables["sourceHashes"] == sim_report["sourceHashes"] and all(
        digest(folder / key) == value
        for key, value in sim_tables["sourceHashes"].items())
    checks["simulation_algorithms_match"] = sim_tables.get("algorithmHashes") == sim_report.get("algorithmHashes") and bool(
        sim_tables.get("algorithmHashes")) and all(digest(ROOT / path) == expected
        for path, expected in sim_tables.get("algorithmHashes", {}).items())
    from lattice_simulation import clearance_envelope, load_modules
    envelope = sim_report.get("clearanceEnvelope", {})
    params, definition_motion = load_modules(folder)
    try:
        expected_envelope = clearance_envelope(model, params, definition_motion, drive_report)
        expected_envelope["source"] = {
            "path": "build/drive_report.json", "sha256": digest(build / "drive_report.json")}
        checks["clearance_envelope_contact_sources_valid"] = True
    except ValueError:
        # A rejected drive measurement must invalidate the saved integration
        # result. Retaining an earlier green report after this failure is unsafe.
        expected_envelope = None
        checks["clearance_envelope_contact_sources_valid"] = False
    checks["clearance_envelope_matches_measured_contacts"] = envelope == expected_envelope
    checks["clearance_envelope_covers_all_nominal_angles"] = bool(envelope.get("groups")) and all(
        len(group.get("samples", [])) >= 2 and
        group["samples"][0]["servoDeg"] == sim_tables["limitsDeg"][0] and
        group["samples"][-1]["servoDeg"] == sim_tables["limitsDeg"][1] and
        all(0 < b["servoDeg"] - a["servoDeg"] <= 2.5 + 1e-9
            for a, b in zip(group["samples"], group["samples"][1:])) and
        all(len(row.get("heightRangeMm", [])) == 2 and
            all(finite_number(value) for value in row["heightRangeMm"]) and
            row["heightRangeMm"][0] - 1e-9 <= row["nominalHeightMm"] <= row["heightRangeMm"][1] + 1e-9
            for row in group["samples"])
        for group in envelope.get("groups", []))
    convergence = sim_report.get("integrationConvergence", {}).get("reportedUpperBound", {})
    # 表示精度より小さい差を要求する。実測結果に合わせて閾値を広げない。
    limits = {"finalServoDeg": .01, "maxTraceServoDeg": .01, "maxTraceTorqueNm": .0001,
              "maxTraceLiftMm": .001, "peakTorqueNm": .0001, "maxContactSpeedMmS": .01}
    checks["simulation_time_step_converges"] = all(
        key in convergence and 0 <= convergence[key] <= limit for key, limit in limits.items())
    checks["simulation_traces_in_verified_range"] = all(
        sim_tables["limitsDeg"][0] - 1e-9 <= row["servoDeg"] <= sim_tables["limitsDeg"][1] + 1e-9 and
        len(row["liftsMm"]) == len(sim_tables["groups"]) and
        all(math.isfinite(value) for value in row["liftsMm"])
        for scenario in sim_report["scenarios"].values() for row in scenario["trace"])
    review_path = build / "print_path_review.json"
    evidence_path = build / "print_geometry_evidence.json"
    if evidence_path.exists():
        print_evidence = read("print_geometry_evidence.json")
        printable_ids = {part["id"] for part in manifest["parts"] if part.get("print")}
        evidence_parts = print_evidence.get("parts", {})
        checks["print_geometry_meter_calibrated"] = print_evidence.get("calibrationPass") is True
        checks["print_geometry_matches_final_files"] = (
            print_evidence.get("manifestSha256") == digest(build / "manifest.json") and
            set(evidence_parts) == printable_ids and
            all(source_hashes_match({row["source"]["file"]: row["source"]["sha256"]})
                for row in evidence_parts.values()))
    else:
        checks["print_geometry_meter_calibrated"] = False
        checks["print_geometry_matches_final_files"] = False
    if review_path.exists():
        path_review = read("print_path_review.json")
        warnings = {row["object"].removeprefix(f"{model}-print-")
            for plate in delivery["plates"].values() for material in plate["materials"].values()
            for row in material.get("visible_unsupported", [])}
        reviewed = {row["id"] for row in path_review["objects"] if row["decision"] == "accepted"}
        source_parts = {p["id"]: p for p in manifest["parts"]}
        checks["print_review_matches_final_files"] = (
            digest(build / "delivery_report.json") == path_review["basis"]["delivery_report_sha256"] and
            digest(build / "manifest.json") == path_review["basis"]["manifest_sha256"] and
            digest(evidence_path) == path_review["basis"]["print_geometry_evidence_sha256"] and
            all(digest(ROOT / "prints" / model / f"{model}-{'fit-test-' if plate == 'fit_test' else ''}{material}.gcode.3mf")
                == path_review["basis"]["gcode_sha256"][f"{plate}_{material}"]
                for plate in ("full", "fit_test") for material in ("PLA", "PETG")) and
            all(digest(folder / source_parts[row["id"]]["print"]) == row["source_stl_sha256"]
                for row in path_review["objects"] + path_review.get("orientation_checks", [])))
        checks["print_warnings_reviewed"] = warnings == reviewed and path_review["status"] == "accepted_with_fit_test"
        checks["print_review_preserves_hardware_unknown"] = path_review.get("physical_print_verified") is False
        checks["print_review_actual_spans_bounded"] = all(
            finite_number(row.get("max_actual_span_mm")) and row["max_actual_span_mm"] <= 10.0
            for row in path_review["objects"])
        span_names = [f"print_spans_{suffix}{material}.json"
            for suffix in ("", "fit_") for material in ("PLA", "PETG")]
        span_reports = [read(name) for name in span_names if (build / name).exists()]
        checks["continuous_print_spans_measured"] = all(
            row.get("calibration", {}).get("pass") is True and
            row.get("objectAssignment", {}).get("complete") is True and
            digest(Path(row["source"]["file"])) == row["source"]["sha256"]
            for row in span_reports) and len(span_reports) == len(span_names)
        closed_loop_file = build / "closed_loop_support_evidence.json"
        closed_loop = read("closed_loop_support_evidence.json") if closed_loop_file.is_file() else {}
        loop_plates = closed_loop.get("plates", {})
        checks["closed_print_paths_calibrated"] = closed_loop.get("calibration", {}).get("pass") is True
        checks["closed_print_paths_algorithms_fresh"] = (
            source_hashes_match(closed_loop.get("sourceAlgorithmSha256")) and
            closed_loop.get("sourceAlgorithmIntegrity", {}).get("pass") is True)
        checks["closed_print_paths_sources_fresh"] = (
            set(loop_plates) == {"PLA", "PETG", "fit-test-PLA", "fit-test-PETG"} and
            all(source_hashes_match({row[key]["file"]: row[key]["sha256"]})
                for row in loop_plates.values() for key in ("sourceGcode", "sourceSpanReport")))
        checks["closed_print_paths_supported"] = (
            closed_loop.get("overall", {}).get("pass") is True and
            all(row.get("decision") == "accepted" and bool(row.get("basis"))
                for plate in loop_plates.values() for row in plate.get("closedUnsupportedPaths", [])))
        checks["closed_print_paths_review_fresh"] = (
            closed_loop_file.is_file() and path_review.get("basis", {}).get("closed_loop_support_evidence_sha256") ==
                digest(closed_loop_file))
        checks["web_closed_print_paths_match"] = web.get("closed_loop_support_evidence") == closed_loop
        checks["web_print_review_matches"] = web.get("print_path_review") == path_review
        path_evidence_file = build / "print_path_evidence.json"
        checks["web_print_path_evidence_matches"] = (path_evidence_file.is_file() and
            web.get("print_path_evidence") == read("print_path_evidence.json"))
        if model.endswith("c4"):
            support_geometry = read("print_support_geometry.json")
            measured_supports = support_geometry.get("supports", [])
            checks["all_print_support_geometry_passes"] = (
                support_geometry.get("pass") is True and
                support_geometry.get("calibration", {}).get("pass") is True and
                support_geometry.get("primarySolver") == "MANIFOLD" and
                {row.get("partId") for row in measured_supports} ==
                    {"housing", "horn_coupler", "carrier_center", "carrier_outer"} and
                all(row.get("pass") is True and row.get("removalPhysicallyVerified") is False
                    for row in measured_supports))
            checks["all_print_support_geometry_sources_fresh"] = (
                source_hashes_match(support_geometry.get("sourceSha256")) and
                support_geometry.get("sourceIntegrity", {}).get("pass") is True)
            checks["all_print_support_geometry_review_fresh"] = (
                path_review.get("basis", {}).get("print_support_geometry_sha256") ==
                    digest(build / "print_support_geometry.json") and
                all(row.get("externalSupportEvidence", {}).get("geometryEvidenceSha256") ==
                        digest(build / "print_support_geometry.json")
                    for plate in loop_plates.values() for row in plate.get("closedUnsupportedPaths", [])
                    if row.get("externalSupportEvidence")))
            checks["web_all_print_support_geometry_matches"] = (
                web.get("print_support_geometry") == support_geometry)
            support = read("carrier_outer_print_support.json")
            path_evidence = read("print_path_evidence.json")
            carrier_support = path_evidence.get("carrier_outer_support_gap", {})
            checks["removable_carrier_support_geometry"] = (support.get("pass") is True and
                support.get("primary_solver") == "MANIFOLD" and support.get("calibration", {}).get("pass") is True and
                support.get("print_stl_component_min_z_mm") == [0., 0.] and
                support.get("support_product_common_volume_mm3", math.inf) <= .001 and
                abs(support.get("support_product_exact_common_volume_mm3", math.inf) -
                    support.get("support_product_common_volume_mm3", -math.inf)) <= .00001)
            checks["removable_carrier_support_sources_fresh"] = source_hashes_match(support.get("source_sha256"))
            checks["removable_carrier_support_review_fresh"] = (
                carrier_support.get("source_support_evidence_sha256") == digest(build / "carrier_outer_print_support.json") and
                path_review.get("carrier_support_check", {}).get("source_support_evidence_sha256") ==
                    digest(build / "carrier_outer_print_support.json"))
            for key, part_id in (("coupler_support_gap", "horn_coupler"), ("carrier_outer_support_gap", "carrier_outer")):
                record = path_evidence.get(key, {})
                checks[f"{key}_gcode_and_unknown_preserved"] = (record.get("removal_physically_verified") is False and
                    record.get("source_stl_sha256") == digest(folder / source_parts[part_id]["print"]) and
                    set(record.get("materials", {})) == {"PLA", "PETG"} and
                    all(values.get("source_gcode_sha256") == digest(ROOT / "prints" / model / f"{model}-{material}.gcode.3mf") and
                        finite_number(values.get("material_gap_mm")) and abs(values["material_gap_mm"] - .2) < .00001
                        for material, values in record["materials"].items()))
    else:
        checks["print_warnings_reviewed"] = delivery["status"] == "ok"
    top_z = bounds[2][1]
    web_parts = {p["id"]: p for p in web["parts"]}
    for frame in frames:
        for part_id, matrix in frame["transforms"].items():
            vertices = web_parts[part_id]["mesh"]["vertices"]
            top_z = max(top_z, max(matrix[2] * vertices[i] + matrix[6] * vertices[i + 1]
                + matrix[10] * vertices[i + 2] + matrix[14] for i in range(0, len(vertices), 3)))
    peak_height = round(top_z - bounds[2][0], 4)
    checks["maximum_height_matches_geometry"] = abs(peak_height - manifest["meta"]["max_dimensions_mm"][2]) < .01
    render_path = build / "render_report.json"
    if render_path.exists():
        renders = read("render_report.json")
        checks["renders_match_final_geometry"] = all(digest(folder / path) == expected
            for path, expected in renders["assembly_sha256"].items()) and digest(build / "motion.json") == renders["motion_sha256"]
        checks["rendered_images_match_hashes"] = all(digest(build / row["file"]) == row["sha256"] for row in renders["images"])
    else:
        checks["renders_match_final_geometry"] = False
    if model.endswith("c3"):
        detail_path = build / "drive_detail_report.json"
        detail = read("drive_detail_report.json") if detail_path.is_file() else {}
        detail_sources = detail.get("sourceAssemblyStlSha256", {})
        source_parts = {p["id"]: p for p in manifest["parts"]}
        checks["drive_detail_matches_final_geometry"] = bool(detail_sources) and all(
            key in source_parts and digest(folder / source_parts[key]["assembly"]) == expected
            for key, expected in detail_sources.items())
        checks["drive_detail_image_and_script_current"] = (
            detail.get("image", {}).get("file") == "drive-detail.png" and
            digest(build / "drive-detail.png") == detail.get("image", {}).get("sha256") and
            detail.get("renderScript", {}).get("file") == "render_drive_detail.py" and
            digest(folder / "render_drive_detail.py") == detail.get("renderScript", {}).get("sha256"))
        checks["drive_detail_clips_only_shell"] = (
            detail.get("section", {}).get("part") == "shell" and
            detail.get("section", {}).get("internalPartsOpaque") is True)
    checks["mechanism_report_passes"] = verify.get("ok", verify.get("pass")) is True
    integrity = verify.get("source_stl_integrity", {})
    recorded = integrity.get("end", {})
    recorded = recorded.get("per_file_sha256", recorded)
    source_parts = {p["id"]: p for p in manifest["parts"]}
    checks["verification_matches_final_geometry"] = (
        integrity.get("pass") is True and set(parts) <= set(recorded) and
        all(key in source_parts and digest(folder / source_parts[key]["assembly"]) == value
            for key, value in recorded.items()))
    exact_scene = verify.get("exact_scene", {})
    checks["all_pairs_exact_verification_passes"] = exact_scene.get("ok", exact_scene.get("pass")) is True
    static_result = verify.get("static_geometry", {})
    checks["static_geometry_passes"] = static_result.get("ok", static_result.get("pass")) is True
    checks["plates_and_calibration_pass"] = delivery["calibration"]["ok"] and all(
        result["placement"]["ok"] and result["layout_preserved"]
        for plate in delivery["plates"].values() for result in plate["materials"].values())
    result = {"ok": all(checks.values()), "checks": checks, "calibration": calibration, "closed_dimensions_mm": size,
              "animation_frames": len(frames), "max_height_mm": peak_height, "print_parts": geometry,
              "print_path_review_status": delivery["status"]}
    path = build / "integration_report.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    os.replace(temp, path)
    print(json.dumps({"model": model, "ok": result["ok"], "checks": checks,
                      "dimensions_mm": size, "print_parts": len(geometry)}, ensure_ascii=False))
    return result["ok"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=("mystery-box-sg92r-c3", "mystery-box-sg92r-c4"))
    selected_model = parser.parse_args().model
    try:
        passed = audit(selected_model)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = {"ok": False, "checks": {"audit_completed": False},
                  "input_error": {"type": type(error).__name__, "reason": str(error)}}
        report_path = ROOT / "models" / selected_model / "build/integration_report.json"
        temporary = report_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        os.replace(temporary, report_path)
        print(json.dumps({"model": selected_model, **result}, ensure_ascii=False))
        passed = False
    raise SystemExit(0 if passed else 1)
