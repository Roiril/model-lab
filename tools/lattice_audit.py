"""完成時の形状・運動表・配送ファイルを独立に照合する。"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
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
    review_path = build / "print_path_review.json"
    if review_path.exists():
        path_review = read("print_path_review.json")
        warnings = {row["object"].removeprefix(f"{model}-print-")
            for plate in delivery["plates"].values() for material in plate["materials"].values()
            for row in material.get("visible_unsupported", [])}
        reviewed = {row["id"] for row in path_review["objects"] if row["decision"] == "accepted"}
        source_parts = {p["id"]: p for p in manifest["parts"]}
        checks["print_review_matches_final_files"] = (
            digest(build / "delivery_report.json") == path_review["basis"]["delivery_report_sha256"] and
            all(digest(folder / source_parts[row["id"]]["print"]) == row["source_stl_sha256"]
                for row in path_review["objects"]))
        checks["print_warnings_reviewed"] = warnings == reviewed and path_review["status"] == "accepted_with_fit_test"
        checks["web_print_review_matches"] = web.get("print_path_review") == path_review
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
    raise SystemExit(0 if audit(parser.parse_args().model) else 1)
