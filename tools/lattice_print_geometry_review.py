"""Inspect the actual print-orientation STL files with the calibrated mesh checks.

Run with Blender because ``printmech`` uses ``mathutils``::

    blender.exe --background --python tools/lattice_print_geometry_review.py -- \
        mystery-box-sg92r-c4 --output models/.../build/print_geometry_evidence.json
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))
sys.stdout.reconfigure(encoding="utf-8")

from printmech.mesh import Mesh  # noqa: E402
from printmech.printability import calibrate, review  # noqa: E402
import lattice_drive as drive  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_params(folder):
    spec = importlib.util.spec_from_file_location("print_geometry_params", folder / "params.py")
    params = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(params)
    return params


def c4_drive_features(folder):
    """Measure the blind floor, shoulder, and peg from the current triangle files."""
    params = load_params(folder)
    build = folder / "build"
    coupler_path = build / "horn_coupler.stl"
    horn_path = build / "servo_horn.stl"
    coupler = drive.read_stl(coupler_path)
    horn = drive.read_stl(horn_path)
    projection = drive.np.unique(drive.np.round(drive.np.concatenate((
        horn.reshape(-1, 3)[:, 1:], horn.mean(axis=1)[:, 1:])), 5), axis=0)
    blind = drive.blind_floor_measure(
        coupler, projection, params.HORN_POCKET_X1 * 1000,
        params.JOINT_COUPLER_GROOVE_X0 * 1000)

    def material_interval(yz, midpoint):
        boundaries = drive.ray_x_surfaces(coupler, yz)
        intervals = [[a, b] for a, b in zip(boundaries[::2], boundaries[1::2])]
        containing = next((row for row in intervals if row[0] < midpoint < row[1]), None)
        return {"witnessYZmm": list(yz), "boundariesXmm": boundaries,
                "containingIntervalXmm": containing}

    axis_z = params.CAM_AXIS_Z * 1000
    shoulder_mid = (params.JOINT_COUPLER_SHOULDER_X0
                    + params.JOINT_COUPLER_SHOULDER_X1) * 500
    shoulder = material_interval((params.JOINT_COUPLER_SHOULDER_R * 1000 - 0.5, axis_z),
                                 shoulder_mid)
    peg_mid = (params.COUPLER_X1 + params.SHAFT_JOINT_L / 2) * 1000
    peg = material_interval((0.0, axis_z), peg_mid)
    if peg["containingIntervalXmm"]:
        peg["projectionBeyondShoulderMm"] = round(
            peg["containingIntervalXmm"][1] - params.JOINT_COUPLER_SHOULDER_X1 * 1000, 6)
    return {
        "sources": {coupler_path.relative_to(ROOT).as_posix(): sha256(coupler_path),
                    horn_path.relative_to(ROOT).as_posix(): sha256(horn_path)},
        "blindFloor": blind,
        "shoulder": shoulder,
        "peg": peg,
        "calibration": {
            "positive1_25mm": drive.blind_floor_measure(
                drive.cube_triangles() * drive.np.array([1.25, 1, 1]),
                drive.np.array([[.25, .25], [.5, .5], [.75, .75]]), 0, 1.25),
            "negative0_15mm": drive.blind_floor_measure(
                drive.cube_triangles() * drive.np.array([.15, 1, 1]),
                drive.np.array([[.25, .25], [.5, .5], [.75, .75]]), 0, .15),
        },
    }


def orientation_candidates(path, rotations):
    source = Mesh.load(path)
    candidates = {}
    for name, matrix in rotations.items():
        moved = source.moved(matrix, name)
        low = min(vertex.z for vertex in moved.v)
        moved = moved.moved(Matrix.Translation(Vector((0, 0, -low))), name)
        result = review(moved, (0, 0, 1), layer=0.2)
        bounds = moved.bounds()
        candidates[name] = {
            "boundsMm": [[round(value, 4) for value in row] for row in bounds],
            "bed": result["bed"],
            "minimumDetectedThicknessMm": min(
                (row["min_mm"] for row in result["thin_under_1_2mm"]),
                default=None,
            ),
            "thinClusterCount": len(result["thin_under_1_2mm"]),
            "largestOverhangClusters": result["overhang_clusters"][:3],
        }
    return candidates


def straight_span_evidence(path):
    report = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    maximum_by_object = {}
    unsupported_group_maxima = {}
    for obj in report["objects"]:
        for layer in obj["layers"]:
            for interval in layer["intervals"]:
                length = interval["lengthMm"]
                start, end = interval["startXYmm"], interval["endXYmm"]
                chord = math.hypot(end[0] - start[0], end[1] - start[1])
                straightness = chord / length if length else 0.0
                if interval["support"] in {"one_end", "none"}:
                    row = {
                        "object": obj["name"], "zMm": layer["zMm"],
                        "feature": interval["feature"], "category": interval["category"],
                        "support": interval["support"], "pathLengthMm": length,
                        "endpointDistanceMm": round(chord, 4),
                        "straightness": round(straightness, 4),
                        "startXYmm": start, "endXYmm": end,
                        "boundsXYmm": interval["boundsXYmm"],
                    }
                    key = (obj["name"], interval["support"],
                           interval["feature"], interval["category"])
                    previous = unsupported_group_maxima.get(key)
                    if previous is None or length > previous["pathLengthMm"]:
                        unsupported_group_maxima[key] = row
                if straightness >= 0.98:
                    row = {
                        "object": obj["name"], "zMm": layer["zMm"],
                        "feature": interval["feature"], "category": interval["category"],
                        "support": interval["support"], "pathLengthMm": length,
                        "endpointDistanceMm": round(chord, 4),
                        "straightness": round(straightness, 4),
                        "startXYmm": start, "endXYmm": end,
                        "boundsXYmm": interval["boundsXYmm"],
                    }
                    previous = maximum_by_object.get(obj["name"])
                    if previous is None or row["pathLengthMm"] > previous["pathLengthMm"]:
                        maximum_by_object[obj["name"]] = row
                    if length >= 10.0:
                        rows.append(row)
    longest = {}
    for row in rows:
        key = (row["object"], row["zMm"], row["feature"],
               row["category"], row["support"])
        if key not in longest or row["pathLengthMm"] > longest[key]["pathLengthMm"]:
            longest[key] = row
    rows = sorted(longest.values(), key=lambda row: row["pathLengthMm"], reverse=True)
    return {
        "file": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
        "sha256": sha256(path), "sourceGcodeSha256": report["source"]["sha256"],
        "calibrationPass": report["calibration"]["pass"],
        "objectAssignmentComplete": report["objectAssignment"]["complete"],
        "method": "Intervals at least 10 mm whose endpoint distance is at least 98% of path length. Closed rings and accumulated curves are excluded.",
        "maximumStraightIntervalByObject": maximum_by_object,
        "oneEndOrNoneMaximumByGroup": sorted(
            unsupported_group_maxima.values(),
            key=lambda row: (row["object"], row["support"],
                             row["feature"], row["category"]),
        ),
        "straightIntervalsAtLeast10mm": rows,
    }


def inspect(model_id):
    folder = ROOT / "models" / model_id
    build = folder / "build"
    manifest_path = build / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    inputs = [manifest_path]
    inputs.extend(folder / part["print"] for part in manifest["parts"] if part.get("print"))
    span_files = {
        "fullPLA": build / "print_spans_PLA.json",
        "fullPETG": build / "print_spans_PETG.json",
        "fitPLA": build / "print_spans_fit_PLA.json",
        "fitPETG": build / "print_spans_fit_PETG.json",
    }
    inputs.extend(path for path in span_files.values() if path.exists())
    if model_id == "mystery-box-sg92r-c3":
        inputs.extend(build / name for name in (
            "camshaft.stl", "cam_0.stl", "cam_gear.stl", "drive_gear.stl",
        ))
    if model_id == "mystery-box-sg92r-c4":
        inputs.extend((build / "horn_coupler.stl", build / "servo_horn.stl"))
    start_hashes = {path: sha256(path) for path in inputs}
    parts = {}
    for part in manifest["parts"]:
        relative = part.get("print")
        if not relative:
            continue
        path = folder / relative
        mesh = Mesh.load(path, part["id"])
        result = review(mesh, (0, 0, 1), layer=0.2)
        parts[part["id"]] = {
            "source": {
                "file": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            },
            "boundsMm": [[round(value, 4) for value in row] for row in mesh.bounds()],
            "bed": result["bed"],
            "thinClusterCount": len(result["thin_under_1_2mm"]),
            "thinUnder1_2mm": result["thin_under_1_2mm"][:4],
            "overhangClusterCount": len(result["overhang_clusters"]),
            "largestOverhangClusters": result["overhang_clusters"][:3],
        }
    calibration = calibrate()
    result = {
        "version": 1,
        "model": model_id,
        "method": {
            "input": "build/print_*.stl and the fit-test STL in their final print orientation",
            "bed": "Down-facing triangles within 0.05 mm of minimum Z",
            "thin": "Triangle-centroid inward ray to an oppositely facing triangle; clusters below 1.2 mm",
            "overhang": "Down-facing triangles steeper than 44.8 degrees, grouped spatially",
            "limits": "Triangle checks locate risk regions. G-code continuity decides actual unsupported span length.",
        },
        "calibration": calibration,
        "calibrationPass": bool(calibration.get("ok")),
        "manifestSha256": sha256(manifest_path),
        "parts": parts,
    }
    if model_id == "mystery-box-sg92r-c3":
        quarter = math.pi / 2
        sixth = math.pi / 6
        result["orientationCandidates"] = {
            "camshaft": orientation_candidates(build / "camshaft.stl", {
                "current": Matrix.Identity(4),
                "hex_face_x_plus_30": Matrix.Rotation(sixth, 4, "X"),
            }),
            "cam_0": orientation_candidates(build / "cam_0.stl", {
                "current_y_plus_90": Matrix.Rotation(quarter, 4, "Y"),
                "main_face_y_minus_90": Matrix.Rotation(-quarter, 4, "Y"),
            }),
            "cam_gear": orientation_candidates(build / "cam_gear.stl", {
                "current_y_plus_90": Matrix.Rotation(quarter, 4, "Y"),
                "gear_face_y_minus_90": Matrix.Rotation(-quarter, 4, "Y"),
            }),
            "drive_gear": orientation_candidates(build / "drive_gear.stl", {
                "current_y_plus_90": Matrix.Rotation(quarter, 4, "Y"),
                "receiver_mouth_y_minus_90": Matrix.Rotation(-quarter, 4, "Y"),
                "axis_horizontal": Matrix.Identity(4),
                "axis_horizontal_x_plus_6": Matrix.Rotation(math.pi / 30, 4, "X"),
                "axis_horizontal_x_plus_12": Matrix.Rotation(math.pi / 15, 4, "X"),
            }),
        }
    if model_id == "mystery-box-sg92r-c4":
        result["driveFeatures"] = c4_drive_features(folder)
        quarter = 1.5707963267948966
        result["orientationCandidates"] = {
            "horn_coupler": orientation_candidates(build / "horn_coupler.stl", {
                "axis_vertical_blind_down": Matrix.Rotation(-quarter, 4, "Y"),
                "axis_vertical_mouth_up": Matrix.Rotation(quarter, 4, "Y"),
                "axis_horizontal_identity": Matrix.Identity(4),
                "axis_horizontal_x_plus_80": Matrix.Rotation(1.3962634015954636, 4, "X"),
            }),
            "joint_keeper": orientation_candidates(build / "joint_keeper.stl", {
                "current_x_plus_90": Matrix.Rotation(quarter, 4, "X"),
                "assembly_identity": Matrix.Identity(4),
                "y_plus_90": Matrix.Rotation(quarter, 4, "Y"),
                "y_minus_90": Matrix.Rotation(-quarter, 4, "Y"),
            }),
        }
    if any(path.exists() for path in span_files.values()):
        result["straightSpanEvidence"] = {
            name: straight_span_evidence(path)
            for name, path in span_files.items() if path.exists()
        }
    changed = [path for path, digest in start_hashes.items()
               if not path.exists() or sha256(path) != digest]
    if changed:
        names = ", ".join(path.relative_to(ROOT).as_posix() for path in changed)
        raise RuntimeError(f"inspection inputs changed during measurement: {names}")
    return result


def write_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv=None):
    args = arguments(sys.argv[sys.argv.index("--") + 1:] if argv is None and "--" in sys.argv else argv)
    report = inspect(args.model)
    write_json(args.output, report)
    if not report["calibrationPass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
