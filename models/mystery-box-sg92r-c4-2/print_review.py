"""C4-2 の全プレートを実 G-code で測り、印刷経路の判定を発行する。"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
MODEL = "mystery-box-sg92r-c4-2"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")
TEMP_ROOT = Path(r"D:\Projects\model-lab-c4-2-temp")
TEMP_ROOT.mkdir(parents=True, exist_ok=True)
os.environ["TEMP"] = str(TEMP_ROOT)
os.environ["TMP"] = str(TEMP_ROOT)
sys.path.insert(0, str(ROOT / "tools"))

import lattice_closed_loop_support as closed  # noqa: E402
import lattice_delivery as delivery_tool  # noqa: E402
import lattice_print_spans as spans  # noqa: E402
import lattice_span_locator as locator  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict:
    return {"file": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": sha256(path)}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def span_name(plate_id: str, material: str) -> Path:
    return BUILD / f"print_spans_{plate_id}_{material}.json"


def geometry_worker(output: Path) -> None:
    import lattice_print_geometry_review as geometry
    from mathutils import Matrix, Vector

    spec = importlib.util.spec_from_file_location("c42_print_params", HERE / "params.py")
    params = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(params)
    report = geometry.inspect(MODEL)
    rotations = {
        "current": Matrix.Identity(4),
        "x_plus_90": Matrix.Rotation(math.pi / 2, 4, "X"),
        "x_minus_90": Matrix.Rotation(-math.pi / 2, 4, "X"),
        "y_plus_90": Matrix.Rotation(math.pi / 2, 4, "Y"),
        "y_minus_90": Matrix.Rotation(-math.pi / 2, 4, "Y"),
        "x_180": Matrix.Rotation(math.pi, 4, "X"),
    }
    adoption_reasons = {
        "housing": "底面を接地し、110mm外装を全高で積層する。",
        "bottom": "外から見える底面をベッドへ向ける。",
        "faceplate": "外から見える六角格子面をベッドへ向ける。",
        "guide_frame": "四辺の案内枠を同一平面で接地する。",
        "carrier_center": "外から見える六角面をベッドへ向ける。",
        "carrier_upper_left": "外から見える六角面をベッドへ向ける。",
        "carrier_upper_right": "外から見える六角面をベッドへ向ける。",
        "carrier_lower_pair": "外から見える六角面をベッドへ向ける。",
        "cam_disk": "円盤の全面を水平に接地し、4本のカム溝を上向きに積層する。",
        "horn_coupler": "ホーン受け外面を接地し、嵌合面を上向きにする。",
        "drive_key": "角形キーの広い端面を接地する。",
        "cam_keeper": "止め輪の平面を接地し、爪を面内で積層する。",
        "print_test": "試片の嵌合基準面を同じベッド面へそろえる。",
    }
    orientations = {}
    actual_bed_support = {}

    def convex_hull(points):
        points = sorted(set(points))
        if len(points) <= 1:
            return points
        def cross(origin, a, b):
            return ((a[0] - origin[0]) * (b[1] - origin[1])
                    - (a[1] - origin[1]) * (b[0] - origin[0]))
        lower = []
        for point in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
                lower.pop()
            lower.append(point)
        upper = []
        for point in reversed(points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
                upper.pop()
            upper.append(point)
        return lower[:-1] + upper[:-1]

    def bed_support(mesh):
        low = min(vertex.z for vertex in mesh.v)
        contact_area = 0.0
        points = []
        for triangle in mesh.t:
            vertices = [mesh.v[index] for index in triangle]
            normal = (vertices[1] - vertices[0]).cross(vertices[2] - vertices[0])
            area = normal.length / 2.0
            if area <= 1.0e-12:
                continue
            center_z = sum(vertex.z for vertex in vertices) / 3.0
            if abs(normal.normalized().z) > 0.999 and center_z - low < 0.05:
                contact_area += area
                points.extend((round(vertex.x, 5), round(vertex.y, 5)) for vertex in vertices)
        hull = convex_hull(points)
        props = mesh.mass_props()
        com = props["com"]
        if len(hull) >= 3:
            signed = [((hull[(index + 1) % len(hull)][0] - hull[index][0])
                       * (com[1] - hull[index][1])
                       - (hull[(index + 1) % len(hull)][1] - hull[index][1])
                       * (com[0] - hull[index][0])) for index in range(len(hull))]
            com_supported = all(value >= -1.0e-5 for value in signed)
            widths = []
            for index, start in enumerate(hull):
                end = hull[(index + 1) % len(hull)]
                dx, dy = end[0] - start[0], end[1] - start[1]
                length = math.hypot(dx, dy)
                if length <= 1.0e-9:
                    continue
                normal = (-dy / length, dx / length)
                projections = [point[0] * normal[0] + point[1] * normal[1]
                               for point in hull]
                widths.append(max(projections) - min(projections))
            minimum_width = min(widths, default=0.0)
        else:
            com_supported = False
            minimum_width = 0.0
        height = max(vertex.z for vertex in mesh.v) - low
        return {"contactAreaMm2": round(contact_area, 4),
                "supportHullXYmm": [[round(value, 4) for value in point] for point in hull],
                "centerOfMassXYmm": [round(com[0], 4), round(com[1], 4)],
                "centerOfMassOverSupportHull": com_supported,
                "minimumSupportWidthMm": round(minimum_width, 4),
                "heightMm": round(height, 4),
                "heightToMinimumSupportWidth": (
                    round(height / minimum_width, 4) if minimum_width > 1.0e-6 else None)}

    for part in report["parts"]:
        path = HERE / next(row["print"] for row in
                           json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))["parts"]
                           if row["id"] == part)
        actual_bed_support[part] = bed_support(geometry.Mesh.load(path, part))
        candidates = geometry.orientation_candidates(path, rotations)
        valid = {name: row for name, row in candidates.items()
                 if row["bed"]["contact_mm2"] > 0 and row["bed"]["com_over_footprint"]}
        def risk(row):
            return sum(cluster["area_mm2"] * (1.0 - float(cluster["supported"] or 0.0))
                       for cluster in row["largestOverhangClusters"])
        recommended = min(valid, key=lambda name: (risk(valid[name]),
                                                     -valid[name]["bed"]["contact_mm2"])) \
            if valid else None
        for name, row in candidates.items():
            row["unsupportedOverhangRiskMm2"] = round(risk(row), 4)
            if name == "current":
                row["decision"] = "adopted"
                row["reason"] = adoption_reasons.get(part, "実G-codeで支持経路を確認する現行姿勢。")
            else:
                row["decision"] = "numerically_preferred" if name == recommended else "not_adopted"
                row["reason"] = ("接地と重心支持を満たし、下向き面の指標が最小。見える面と実G-codeを含めて採否を決める。"
                                 if name == recommended else "採用方向より接地または下向き面の条件が劣る。")
        orientations[part] = {"adopted": "current", "numericPreference": recommended,
                              "adoptionBasis": adoption_reasons.get(part),
                              "candidates": candidates}
    report["orientationCandidates"] = orientations
    report["actualBedSupport"] = actual_bed_support

    def ray_thickness(mesh, origin, direction):
        bvh = mesh.bvh()
        cursor = Vector(origin)
        direction = Vector(direction).normalized()
        distances = []
        traveled = 0.0
        for _ in range(4):
            hit = bvh.ray_cast(cursor, direction, 40.0)
            if hit[0] is None:
                break
            traveled += hit[3]
            distances.append(traveled)
            cursor = hit[0] + direction * 1.0e-4
            traveled += 1.0e-4
        return round(distances[1] - distances[0], 4) if len(distances) >= 2 else None

    manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
    print_by_id = {row["id"]: HERE / row["print"] for row in manifest["parts"] if row.get("print")}
    hex_rows = []
    pitch = params.HEX_PITCH * 1000.0
    for group, cells in params.CELL_QR.items():
        if group == "fixed":
            continue
        part_id = "carrier_" + group
        mesh = geometry.Mesh.load(print_by_id[part_id], part_id)
        q, r = cells[0]
        center = (pitch * (q + r / 2.0), -pitch * math.sqrt(3.0) * r / 2.0)
        thickness = ray_thickness(mesh, (center[0], center[1], 1.6), (0, 1, 0))
        hex_rows.append({"partId": part_id, "witnessMm": [center[0], center[1], 1.6],
                         "measuredWallMm": thickness,
                         "pass": thickness is not None and thickness >= 1.95})
    guide_mesh = geometry.Mesh.load(print_by_id["guide_frame"], "guide_frame")
    _guide_lower, guide_upper = guide_mesh.bounds()
    guide_rows = []
    guide_outer = (params.GUIDE_LUG + 2 * (params.GUIDE_CLR + params.GUIDE_WALL)) * 1000.0
    guide_z = guide_upper[2] - (params.GUIDE_Z1 - params.GUIDE_Z0) * 500.0
    for index, angle_deg in enumerate(params.FOLLOWER_ANGLES_DEG):
        angle = math.radians(angle_deg)
        for radius in (params.GUIDE_INNER_R * 1000.0, params.CAM_RADII[index] * 1000.0):
            center = (radius * math.cos(angle), radius * math.sin(angle))
            candidates = [
                ray_thickness(guide_mesh,
                              (center[0] - guide_outer / 2.0 - 1.0, center[1], guide_z),
                              (1, 0, 0)),
                ray_thickness(guide_mesh,
                              (center[0], center[1] - guide_outer / 2.0 - 1.0, guide_z),
                              (0, 1, 0)),
            ]
            measured = [value for value in candidates if value is not None]
            value = min(measured, default=None)
            guide_rows.append({"group": params.GROUPS[index], "radiusMm": radius,
                               "witnessMm": [*center, guide_z],
                               "axisMeasurementsMm": candidates,
                               "measuredWallMm": value,
                               "pass": value is not None and value >= 1.55})
    drive_mesh = geometry.Mesh.load(print_by_id["drive_key"], "drive_key")
    drive_lower, drive_upper = drive_mesh.bounds()
    drive_center = [(drive_lower[axis] + drive_upper[axis]) / 2.0
                    for axis in range(3)]
    drive_z = drive_lower[2] + 0.55 * (drive_upper[2] - drive_lower[2])
    drive_rows = [
        {"axis": "x", "measuredMm": ray_thickness(
            drive_mesh, (drive_lower[0] - 1.0, drive_center[1], drive_z), (1, 0, 0))},
        {"axis": "y", "measuredMm": ray_thickness(
            drive_mesh, (drive_center[0], drive_lower[1] - 1.0, drive_z), (0, 1, 0))},
    ]
    for row in drive_rows:
        row["minimumRequiredMm"] = 9.8
        row["pass"] = row["measuredMm"] is not None and row["measuredMm"] >= 9.8
    keeper_mesh = geometry.Mesh.load(print_by_id["cam_keeper"], "cam_keeper")
    keeper_lower, keeper_upper = keeper_mesh.bounds()
    keeper_z = keeper_lower[2] + 4.0
    keeper_rows = []
    for label, origin, direction in (
            ("positive_x", (keeper_upper[0] + 1.0, 0, keeper_z), (-1, 0, 0)),
            ("negative_x", (keeper_lower[0] - 1.0, 0, keeper_z), (1, 0, 0)),
            ("positive_y", (0, keeper_upper[1] + 1.0, keeper_z), (0, -1, 0)),
            ("negative_y", (0, keeper_lower[1] - 1.0, keeper_z), (0, 1, 0))):
        value = ray_thickness(keeper_mesh, origin, direction)
        keeper_rows.append({"tab": label, "witnessMm": list(origin),
                            "measuredRadialThicknessMm": value,
                            "minimumRequiredMm": 1.19,
                            "pass": value is not None and value >= 1.19})
    report["featureThickness"] = {
        "exposedHexWalls": {"minimumRequiredMm": 1.95, "measurements": hex_rows,
                            "pass": all(row["pass"] for row in hex_rows)},
        "guideSleeveWalls": {"minimumRequiredMm": 1.55, "measurements": guide_rows,
                             "pass": all(row["pass"] for row in guide_rows)},
        "driveKeyLoadShaft": {"minimumRequiredMm": 9.8, "measurements": drive_rows,
                              "pass": all(row["pass"] for row in drive_rows)},
        "keeperLoadTabs": {"minimumRequiredMm": 1.19, "measurements": keeper_rows,
                           "pass": all(row["pass"] for row in keeper_rows)},
        "calibrationBasis": {
            "commonGeometryCalibrationPass": report["calibrationPass"],
            "method": "荷重部の中央断面を実三角形BVHの対向面間隔で測る。面取り先端は証人点に使わない。",
        },
    }
    write_json(output, report)


def load_inputs() -> tuple[dict, dict, Path, Path]:
    manifest_path = BUILD / "manifest.json"
    delivery_path = BUILD / "delivery_report.json"
    if not manifest_path.is_file() or not delivery_path.is_file():
        missing = [path.relative_to(ROOT).as_posix()
                   for path in (manifest_path, delivery_path) if not path.is_file()]
        raise FileNotFoundError("missing final print inputs: " + ", ".join(missing))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    delivery = json.loads(delivery_path.read_text(encoding="utf-8"))
    if delivery.get("model") != MODEL:
        raise ValueError("delivery report model mismatch")
    if delivery.get("manifest", {}).get("sha256") != sha256(manifest_path):
        raise ValueError("delivery report manifest SHA is stale")
    required_plates = {"full", "full_2", "fit_test"}
    if not required_plates.issubset(delivery.get("plates", {})):
        raise ValueError("delivery report does not contain full/full_2/fit_test plates")
    if set(delivery.get("materials", [])) != {"PLA", "PETG"}:
        raise ValueError("final print review requires PLA and PETG")
    for part in delivery.get("parts", []):
        records = [part.get("assembly")]
        if part.get("source_print"):
            records.extend((part["source_print"], part.get("delivered_print")))
        for source in records:
            if not source:
                continue
            path = ROOT / source["file"]
            if not path.is_file() or sha256(path) != source["sha256"]:
                raise ValueError(f"delivery source SHA is stale: {part.get('id')} {source['file']}")
    for plate_id, plate in delivery["plates"].items():
        if set(plate.get("materials", {})) != {"PLA", "PETG"}:
            raise ValueError(f"plate lacks PLA/PETG slices: {plate_id}")
    return manifest, delivery, manifest_path, delivery_path


def load_support_geometry(manifest: dict, manifest_path: Path) -> tuple[Path, dict]:
    required_parts = {part["id"]: part for part in manifest["parts"]
                      if part.get("print_supports")}
    path = BUILD / "print_support_geometry.json"
    if not path.is_file():
        raise FileNotFoundError("print supports require build/print_support_geometry.json")
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("model") != MODEL:
        raise ValueError("print support geometry model mismatch")
    if report.get("manifest", {}).get("sha256") != sha256(manifest_path):
        raise ValueError("print support geometry manifest SHA is stale")
    if not report.get("sourceAlgorithmIntegrity", {}).get("pass"):
        raise ValueError("print support geometry source algorithm changed during measurement")
    if not report.get("calibration", {}).get("pass"):
        raise ValueError("print support geometry calibration failed")
    measured_parts = report.get("parts", {})
    for part_id, part in required_parts.items():
        measured = measured_parts.get(part_id)
        if not isinstance(measured, dict):
            raise ValueError(f"print support geometry lacks part: {part_id}")
        source_path = HERE / part["print"]
        if measured.get("sourcePrintStl", {}).get("sha256") != sha256(source_path):
            raise ValueError(f"print support geometry source STL is stale: {part_id}")
        expected_count = int(part.get("expected_print_components", 1))
        if (measured.get("expectedComponentCount") != expected_count
                or measured.get("actualComponentCount") != expected_count):
            raise ValueError(f"print support component mismatch: {part_id}")
        expected_supports = {row["id"] for row in part["print_supports"]}
        supports = measured.get("supports", [])
        if {row.get("id") for row in supports} != expected_supports:
            raise ValueError(f"print support evidence set mismatch: {part_id}")
        if measured.get("decision") != "accepted" or any(
                row.get("decision") != "accepted" for row in supports):
            raise ValueError(f"print support geometry rejected: {part_id}")
    if not report.get("overall", {}).get("pass"):
        raise ValueError("print support geometry overall failed")
    return path, report


def generate_spans(delivery: dict) -> tuple[dict, dict]:
    reports = {}
    sources = {}
    for plate_id, plate in delivery["plates"].items():
        for material, result in plate["materials"].items():
            key = f"{plate_id}_{material}"
            gcode = ROOT / result["file"]["file"]
            layout = ROOT / plate["layout"]["file"]
            if sha256(gcode) != result["file"]["sha256"]:
                raise ValueError(f"delivery G-code SHA is stale: {key}")
            if sha256(layout) != plate["layout"]["sha256"]:
                raise ValueError(f"delivery layout SHA is stale: {plate_id}")
            report = spans.inspect(gcode)
            path = span_name(plate_id, material)
            write_json(path, report)
            reports[key] = report
            sources[key] = {"gcode": record(gcode), "layout": record(layout),
                            "span": record(path), "plateId": plate_id, "material": material}
    return reports, sources


def straight_span_evidence(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    maximum = {}
    long_rows = []
    for obj in report["objects"]:
        for layer in obj["layers"]:
            for interval in layer["intervals"]:
                length = float(interval["lengthMm"])
                chord = math.dist(interval["startXYmm"], interval["endXYmm"])
                straightness = chord / length if length else 0.0
                if straightness < 0.98:
                    continue
                row = {"object": obj["name"], "zMm": layer["zMm"],
                       "feature": interval["feature"], "category": interval["category"],
                       "support": interval["support"], "pathLengthMm": length,
                       "endpointDistanceMm": round(chord, 4),
                       "straightness": round(straightness, 4),
                       "startXYmm": interval["startXYmm"], "endXYmm": interval["endXYmm"],
                       "boundsXYmm": interval["boundsXYmm"]}
                if obj["name"] not in maximum or length > maximum[obj["name"]]["pathLengthMm"]:
                    maximum[obj["name"]] = row
                if length >= 10.0:
                    long_rows.append(row)
    return {"file": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": sha256(path), "sourceGcodeSha256": report["source"]["sha256"],
            "calibrationPass": report["calibration"]["pass"],
            "objectAssignmentComplete": report["objectAssignment"]["complete"],
            "method": "Straight intervals have endpoint distance at least 98% of path length.",
            "maximumStraightIntervalByObject": maximum,
            "straightIntervalsAtLeast10mm": sorted(
                long_rows, key=lambda row: row["pathLengthMm"], reverse=True)}


def geometry_evidence(manifest: dict, manifest_path: Path, span_sources: dict) -> tuple[Path, dict]:
    print_paths = [HERE / part["print"] for part in manifest["parts"] if part.get("print")]
    inputs = [manifest_path, *print_paths, *(ROOT / row["span"]["file"] for row in span_sources.values())]
    start = {path: sha256(path) for path in inputs}
    if not BLENDER.is_file():
        raise FileNotFoundError(f"Blender not found: {BLENDER}")
    temporary = BUILD / f".print_geometry_evidence.{os.getpid()}.json"
    log_path = BUILD / "print_geometry_review.log"
    command = [str(BLENDER), "--background", "--python", str(Path(__file__)), "--",
               "--geometry-worker", "--output", str(temporary)]
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        log_path.write_text("command: " + subprocess.list2cmdline(command) + "\n\n"
                            + (result.stdout or "") + "\n" + (result.stderr or ""),
                            encoding="utf-8", newline="\n")
        if result.returncode != 0 or not temporary.is_file():
            raise RuntimeError(f"print geometry review failed; log: {log_path}")
        evidence = json.loads(temporary.read_text(encoding="utf-8"))
    finally:
        if temporary.exists():
            temporary.unlink()
    evidence["straightSpanEvidence"] = {
        key: straight_span_evidence(ROOT / source["span"]["file"])
        for key, source in span_sources.items()
    }
    end = {path: sha256(path) for path in inputs}
    evidence["sourceIntegrity"] = {
        "start": {path.relative_to(ROOT).as_posix(): value for path, value in start.items()},
        "end": {path.relative_to(ROOT).as_posix(): value for path, value in end.items()},
        "pass": start == end,
    }
    path = BUILD / "print_geometry_evidence.json"
    write_json(path, evidence)
    return path, evidence


def c42_external_support_calibration() -> dict:
    points = [(math.cos(index * math.pi / 8), math.sin(index * math.pi / 8))
              for index in range(16)]
    points.append(points[0])
    target = {"feature": "Outer wall", "points": points, "widths": [0.4] * 16}
    supported = [(a, b, 0.4) for a, b in zip(points[:-1], points[1:])]
    separated = [((a[0] + 4.0, a[1]), (b[0] + 4.0, b[1]), 0.4)
                 for a, b in zip(points[:-1], points[1:])]
    positive = closed.external_path_coverage(target, supported)
    negative = closed.external_path_coverage(target, separated)
    return {
        "coveredLoop": positive,
        "separatedLoop": negative,
        "pass": (positive["pathCoverageFraction"] == 1.0
                 and all(positive["startAndEndCovered"])
                 and negative["pathCoverageFraction"] == 0.0
                 and not any(negative["startAndEndCovered"])),
    }


def apply_c42_external_support(findings: list[dict], source: dict,
                               span_report: dict, manifest: dict,
                               support_geometry_path: Path,
                               support_geometry: dict) -> None:
    gcode_path = ROOT / source["gcode"]["file"]
    layout = delivery_tool.inspect_layout(gcode_path)
    offset = span_report["objectAssignment"]["detail"]["global_offset_mm"]
    object_records = {row["objectId"]: row for row in span_report["objects"]}
    manifest_parts = {row["id"]: row for row in manifest["parts"]}
    geometry_parts = support_geometry.get("parts", {})
    layers_by_object = {}
    for layer in locator.read_width_layers(gcode_path):
        if layer["z"] is None:
            continue
        z_mm = round(float(layer["z"]), 4)
        for object_id in {segment[5] for segment in layer["segs"]}:
            segments = [segment for segment in layer["segs"]
                        if segment[5] == object_id]
            layers_by_object.setdefault(object_id, {})[z_mm] = segments

    geometry_valid = (
        support_geometry.get("overall", {}).get("pass") is True
        and support_geometry.get("calibration", {}).get("pass") is True
        and support_geometry.get("sourceAlgorithmIntegrity", {}).get("pass") is True
    )
    for finding in findings:
        if finding["decision"] == "accepted":
            continue
        object_id = finding["objectId"]
        object_record = object_records[object_id]
        part_id = object_record["name"].rsplit("-print-", 1)[1]
        definitions = manifest_parts[part_id].get("print_supports", [])
        geometry_by_id = {
            row["id"]: row
            for row in geometry_parts.get(part_id, {}).get("supports", [])
        }
        if not definitions or not geometry_by_id:
            continue
        target_segments = layers_by_object.get(object_id, {}).get(
            round(float(finding["zMm"]), 4), [])
        chains = locator.width_chains(target_segments)
        if finding["pathIndex"] >= len(chains):
            continue
        target = chains[finding["pathIndex"]]
        placement = next(row for row in layout["objects"]
                         if row["name"] == object_record["name"])
        stl_path = ROOT / "prints" / MODEL / f"{object_record['name']}.stl"
        stl_min, _ = closed.bbox(closed.read_stl(stl_path)[0])
        best = None
        best_rank = None
        external_pass = False
        for definition in definitions:
            geometry_row = geometry_by_id.get(definition["id"])
            support_min = definition["bbox_mm"][0]
            support_max = definition["bbox_mm"][1]

            def plate_xy(point):
                return [point[axis] - stl_min[axis] + placement["min"][axis]
                        - offset[axis] for axis in range(2)]

            plate_min = plate_xy(support_min)
            plate_max = plate_xy(support_max)
            regions = definition.get("support_regions") or [definition]
            for region in regions:
                support_z = round(float(region.get(
                    "expected_last_support_gcode_z_mm",
                    region["support_top_z_mm"])), 4)
                support_layer = layers_by_object.get(object_id, {}).get(support_z, [])
                support_segments = []
                support_heights = set()
                for segment in support_layer:
                    midpoint = ((segment[0] + segment[2]) / 2,
                                (segment[1] + segment[3]) / 2)
                    if (plate_min[0] <= midpoint[0] <= plate_max[0]
                            and plate_min[1] <= midpoint[1] <= plate_max[1]):
                        support_segments.append(
                            ((segment[0], segment[1]), (segment[2], segment[3]), segment[7]))
                        support_heights.add(round(float(segment[8]), 5))
                coverage = closed.external_path_coverage(target, support_segments)
                product_heights = sorted({round(float(segment[8]), 5)
                                          for segment in target_segments})
                actual_gap = None
                if product_heights and support_layer:
                    actual_gap = round(float(finding["zMm"])
                                       - max(product_heights) - support_z, 5)
                declared_gap = float(region["material_face_gap_mm"])
                gap_matches = (actual_gap is not None
                               and actual_gap >= 0.0
                               and abs(actual_gap - declared_gap) <= 0.01)
                geometry_pass = bool(
                    geometry_valid and geometry_row
                    and geometry_row.get("decision") == "accepted")
                candidate_pass = (geometry_pass
                                  and coverage["pathCoverageFraction"] == 1.0
                                  and all(coverage["startAndEndCovered"])
                                  and gap_matches)
                evidence = {
                    "supportId": definition["id"],
                    "supportRegion": region.get("region"),
                    "geometryEvidenceFile": support_geometry_path.relative_to(ROOT).as_posix(),
                    "geometryEvidenceSha256": sha256(support_geometry_path),
                    "geometryPass": geometry_pass,
                    "supportGeometryTopZMm": region["support_top_z_mm"],
                    "supportTopGcodeZMm": support_z,
                    "supportTopLayerHeightsMm": sorted(support_heights),
                    "productLayerHeightsMm": product_heights,
                    "declaredMaterialFaceGapMm": declared_gap,
                    "actualMaterialFaceGapMm": actual_gap,
                    "gapMatchesDefinition": gap_matches,
                    **coverage,
                }
                candidate_rank = (candidate_pass, gap_matches,
                                  evidence["pathCoverageFraction"],
                                  -abs(actual_gap - declared_gap)
                                  if actual_gap is not None else -math.inf)
                if best is None or candidate_rank > best_rank:
                    best = evidence
                    best_rank = candidate_rank
                external_pass = external_pass or candidate_pass
        if best is not None:
            finding["externalSupportEvidence"] = best
        if external_pass:
            finding["decision"] = "accepted"
            finding["basis"] = "removable_support_below_first_product_path"
            finding["decisionEvidence"] = {
                "connectedFraction": 1.0,
                "maximumUnconnectedLengthMm": 0.0,
            }


def closed_loop_evidence(span_reports: dict, sources: dict) -> tuple[Path, dict]:
    algorithm_paths = [Path(__file__), ROOT / "tools/lattice_closed_loop_support.py",
                       ROOT / "tools/lattice_print_spans.py", ROOT / "tools/lattice_span_locator.py",
                       ROOT / "tools/lattice_delivery.py", ROOT / "tools/plate_3mf.py",
                       ROOT / "lib/printmech/gcode.py"]
    start = {path.relative_to(ROOT).as_posix(): sha256(path) for path in algorithm_paths}
    manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
    support_geometry_path = BUILD / "print_support_geometry.json"
    support_geometry = json.loads(support_geometry_path.read_text(encoding="utf-8"))
    plates = {}
    for key, source in sources.items():
        findings = closed.inspect_plate(ROOT / source["gcode"]["file"], span_reports[key],
                                        ROOT / source["layout"]["file"])
        apply_c42_external_support(
            findings, source, span_reports[key], manifest,
            support_geometry_path, support_geometry)
        plates[key] = {
            "sourceGcode": source["gcode"], "sourceLayout": source["layout"],
            "sourceSpanReport": source["span"],
            "summary": {"closedUnsupportedPathCount": len(findings),
                        "failedFindingCount": sum(row["decision"] != "accepted" for row in findings)},
            "closedUnsupportedPaths": findings,
        }
    end = {path.relative_to(ROOT).as_posix(): sha256(path) for path in algorithm_paths}
    calibration = closed.calibration()
    calibration["c42ExternalSupportSchema"] = c42_external_support_calibration()
    calibration["pass"] = (
        calibration["pass"] and calibration["c42ExternalSupportSchema"]["pass"]
    )
    all_findings = [row for plate in plates.values() for row in plate["closedUnsupportedPaths"]]
    evidence = {
        "model": MODEL,
        "sourceManifest": record(BUILD / "manifest.json"),
        "sourcePrintSupportGeometry": record(support_geometry_path),
        "sourceAlgorithmSha256": end,
        "sourceAlgorithmIntegrity": {"start": start, "end": end, "pass": start == end},
        "calibration": calibration,
        "overall": {"findingCount": len(all_findings),
                    "failedFindingCount": sum(row["decision"] != "accepted" for row in all_findings),
                    "pass": calibration["pass"] and start == end
                            and all(row["decision"] == "accepted" for row in all_findings)},
        "plates": plates,
    }
    path = BUILD / "closed_loop_support_evidence.json"
    write_json(path, evidence)
    return path, evidence


def interval_key(plate_key: str, object_name: str, z_mm: float,
                 interval: dict) -> str:
    return "|".join((plate_key, object_name, f"{float(z_mm):.4f}",
                     str(interval["pathIndex"]), interval["support"],
                     f"{float(interval['startXYmm'][0]):.4f}",
                     f"{float(interval['startXYmm'][1]):.4f}",
                     f"{float(interval['endXYmm'][0]):.4f}",
                     f"{float(interval['endXYmm'][1]):.4f}"))


def actual_span(interval: dict) -> float:
    bounds = interval["boundsXYmm"]
    return math.hypot(bounds[0][1] - bounds[0][0],
                      bounds[1][1] - bounds[1][0])


def convex_hull_2d(points):
    points = sorted(set(points))
    if len(points) <= 1:
        return points

    def cross(origin, a, b):
        return ((a[0] - origin[0]) * (b[1] - origin[1])
                - (a[1] - origin[1]) * (b[0] - origin[0]))

    lower = []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def support_polygon_metrics(segments, center_of_mass, height_mm):
    points = []
    cells = set()
    cell_size = 0.2
    for segment in segments:
        start = (segment[0], segment[1])
        end = (segment[2], segment[3])
        width = float(segment[7])
        length = math.dist(start, end)
        if length <= 1.0e-9 or width <= 0:
            continue
        along = ((end[0] - start[0]) / length, (end[1] - start[1]) / length)
        normal = (-along[1], along[0])
        for point in (start, end):
            for longitudinal in (-width / 2.0, width / 2.0):
                for lateral in (-width / 2.0, width / 2.0):
                    points.append((point[0] + along[0] * longitudinal + normal[0] * lateral,
                                   point[1] + along[1] * longitudinal + normal[1] * lateral))
        for cell_x in range(math.floor((min(start[0], end[0]) - width / 2) / cell_size),
                            math.floor((max(start[0], end[0]) + width / 2) / cell_size) + 1):
            for cell_y in range(math.floor((min(start[1], end[1]) - width / 2) / cell_size),
                                math.floor((max(start[1], end[1]) + width / 2) / cell_size) + 1):
                sample = ((cell_x + 0.5) * cell_size, (cell_y + 0.5) * cell_size)
                if locator.point_segment_distance(sample, start, end) <= width / 2.0:
                    cells.add((cell_x, cell_y))
    hull = convex_hull_2d(points)

    def cell_component_metrics(component):
        corners = []
        for cell_x, cell_y in component:
            x0, y0 = cell_x * cell_size, cell_y * cell_size
            corners.extend(((x0, y0), (x0 + cell_size, y0),
                            (x0 + cell_size, y0 + cell_size), (x0, y0 + cell_size)))
        component_hull = convex_hull_2d(corners)
        component_widths = []
        for index, start in enumerate(component_hull):
            end = component_hull[(index + 1) % len(component_hull)]
            dx, dy = end[0] - start[0], end[1] - start[1]
            length = math.hypot(dx, dy)
            if length <= 1.0e-9:
                continue
            normal = (-dy / length, dx / length)
            projections = [point[0] * normal[0] + point[1] * normal[1]
                           for point in component_hull]
            component_widths.append(max(projections) - min(projections))
        return {"cellCount": len(component),
                "areaEstimateMm2": round(len(component) * cell_size * cell_size, 4),
                "centerXYmm": [round(sum((x + 0.5) * cell_size for x, _y in component)
                                          / len(component), 4),
                               round(sum((y + 0.5) * cell_size for _x, y in component)
                                          / len(component), 4)],
                "supportHullXYmm": [[round(value, 4) for value in point]
                                     for point in component_hull],
                "minimumSupportWidthMm": round(min(component_widths, default=0.0), 4)}

    remaining = set(cells)
    connected_components = []
    while remaining:
        seed = remaining.pop()
        component = {seed}
        pending = [seed]
        while pending:
            cell_x, cell_y = pending.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    neighbor = (cell_x + dx, cell_y + dy)
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        component.add(neighbor)
                        pending.append(neighbor)
        connected_components.append(cell_component_metrics(component))
    connected_components.sort(key=lambda row: row["areaEstimateMm2"], reverse=True)
    signed = []
    widths = []
    if len(hull) >= 3:
        for index, start in enumerate(hull):
            end = hull[(index + 1) % len(hull)]
            signed.append((end[0] - start[0]) * (center_of_mass[1] - start[1])
                          - (end[1] - start[1]) * (center_of_mass[0] - start[0]))
            dx, dy = end[0] - start[0], end[1] - start[1]
            length = math.hypot(dx, dy)
            if length > 1.0e-9:
                normal = (-dy / length, dx / length)
                projections = [point[0] * normal[0] + point[1] * normal[1]
                               for point in hull]
                widths.append(max(projections) - min(projections))
    minimum_width = min(widths, default=0.0)
    ratio = height_mm / minimum_width if minimum_width > 1.0e-6 else None
    return {
        "depositedAreaEstimateMm2": round(len(cells) * cell_size * cell_size, 4),
        "supportHullXYmm": [[round(value, 4) for value in point] for point in hull],
        "centerOfMassXYmm": [round(value, 4) for value in center_of_mass],
        "centerOfMassOverSupportHull": len(hull) >= 3 and all(value >= -1.0e-6
                                                               for value in signed),
        "minimumSupportWidthMm": round(minimum_width, 4),
        "heightMm": round(height_mm, 4),
        "heightToMinimumSupportWidth": round(ratio, 4) if ratio is not None else None,
        "connectedComponents": connected_components,
    }


def first_layer_calibration() -> dict:
    def segment(start, end, width=0.4):
        return (*start, *end, "calibration", 1, 0.2, width, 0.2)

    square = [segment((0.0, 0.0), (10.0, 0.0)),
              segment((10.0, 0.0), (10.0, 10.0)),
              segment((10.0, 10.0), (0.0, 10.0)),
              segment((0.0, 10.0), (0.0, 0.0))]
    inside = support_polygon_metrics(square, (5.0, 5.0), 20.0)
    outside = support_polygon_metrics(square, (15.0, 5.0), 20.0)
    narrow = support_polygon_metrics(
        [segment((0.0, 0.0), (2.0, 0.0)), segment((2.0, 0.0), (2.0, 2.0)),
         segment((2.0, 2.0), (0.0, 2.0)), segment((0.0, 2.0), (0.0, 0.0))],
        (1.0, 1.0), 20.0)
    disconnected = support_polygon_metrics(
        [segment((0.0, 0.0), (2.0, 0.0)), segment((2.0, 0.0), (2.0, 2.0)),
         segment((2.0, 2.0), (0.0, 2.0)), segment((0.0, 2.0), (0.0, 0.0)),
         segment((20.0, 0.0), (22.0, 0.0)), segment((22.0, 0.0), (22.0, 2.0)),
         segment((22.0, 2.0), (20.0, 2.0)), segment((20.0, 2.0), (20.0, 0.0))],
        (11.0, 1.0), 20.0)
    support_last_01 = (0.0, 0.0, 1.0, 0.0, "calibration", 1, 1.0, 0.4, 0.1)
    product_first_02 = (0.0, 0.0, 1.0, 0.0, "calibration", 1, 1.4, 0.4, 0.2)
    touching_product_02 = (0.0, 0.0, 1.0, 0.0, "calibration", 1, 1.2, 0.4, 0.2)
    cases = [
        {"name": "wide_support_contains_com", "expected": True,
         "actual": inside["centerOfMassOverSupportHull"]
                   and inside["heightToMinimumSupportWidth"] <= 5.0},
        {"name": "com_outside_support", "expected": False,
         "actual": outside["centerOfMassOverSupportHull"]},
        {"name": "tall_narrow_support", "expected": False,
         "actual": narrow["heightToMinimumSupportWidth"] <= 5.0},
        {"name": "disconnected_slender_towers_do_not_share_global_hull", "expected": False,
         "actual": all(20.0 / row["minimumSupportWidthMm"] <= 5.0
                       for row in disconnected["connectedComponents"])},
        {"name": "unequal_layer_heights_preserve_material_face_gap", "expected": True,
         "actual": material_face_gap_decision(
             support_last_01, product_first_02, 0.2)["pass"]},
        {"name": "unequal_layer_heights_reject_zero_material_face_gap", "expected": False,
         "actual": material_face_gap_decision(
             support_last_01, touching_product_02, 0.2)["pass"]},
        {"name": "material_face_gap_rejects_missing_support_path", "expected": False,
         "actual": material_face_gap_decision(None, product_first_02, 0.2)["pass"]},
    ]
    return {"cases": cases,
            "pass": all(row["actual"] == row["expected"] for row in cases)}


def material_face_gap_mm(support_last: tuple, product_first: tuple) -> float:
    """Return the open Z distance between deposited material faces."""
    return float(product_first[6]) - float(product_first[8]) - float(support_last[6])


def material_face_gap_decision(support_last: tuple | None,
                               product_first: tuple | None,
                               declared_gap_mm: float) -> dict:
    actual_gap = None
    if support_last is not None and product_first is not None:
        actual_gap = material_face_gap_mm(support_last, product_first)
    passed = (actual_gap is not None and actual_gap >= 0.0
              and abs(actual_gap - declared_gap_mm) <= 0.05)
    return {"actualGapMm": actual_gap, "pass": passed}


def first_layer_evidence(span_reports: dict, sources: dict,
                         geometry_path: Path, geometry_report: dict) -> tuple[Path, dict]:
    algorithm_paths = [Path(__file__), ROOT / "tools/lattice_span_locator.py",
                       ROOT / "tools/lattice_print_spans.py",
                       ROOT / "tools/lattice_delivery.py", ROOT / "tools/plate_3mf.py"]
    start_hashes = {path.relative_to(ROOT).as_posix(): sha256(path)
                    for path in algorithm_paths}
    manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
    manifest_parts = {row["id"]: row for row in manifest["parts"]}
    plates = {}
    all_rows = []
    for plate_key, source in sources.items():
        layout = delivery_tool.inspect_layout(ROOT / source["layout"]["file"])
        offset = span_reports[plate_key]["objectAssignment"]["detail"]["global_offset_mm"]
        parsed = locator.read_width_layers(ROOT / source["gcode"]["file"])
        segments_by_object = {}
        for layer in parsed:
            for segment in layer["segs"]:
                segments_by_object.setdefault(segment[5], []).append(segment)
        rows = []
        for obj in span_reports[plate_key]["objects"]:
            segments = segments_by_object.get(obj["objectId"], [])
            first_z = min((round(float(segment[6]), 4) for segment in segments), default=None)
            first_segments = [segment for segment in segments
                              if round(float(segment[6]), 4) == first_z]
            placement = next(row for row in layout["objects"] if row["name"] == obj["name"])
            stl_path = ROOT / "prints" / MODEL / f"{obj['name']}.stl"
            vertices, _faces = delivery_tool.plate_3mf.read_stl(str(stl_path))
            stl_min = [min(point[axis] for point in vertices) for axis in range(3)]
            part_id = obj["name"].rsplit("-print-", 1)[-1]
            local_com = geometry_report["actualBedSupport"][part_id]["centerOfMassXYmm"]
            plate_com = [local_com[axis] - offset[axis] + placement["min"][axis]
                         - stl_min[axis] for axis in range(2)]
            height = geometry_report["actualBedSupport"][part_id]["heightMm"]
            metrics = support_polygon_metrics(first_segments, plate_com, height)
            component_rows = metrics.pop("connectedComponents")
            declared_supports = manifest_parts[part_id].get("print_supports", [])
            support_assignments = []
            support_footprints = []
            for support in declared_supports:
                bbox = support["bbox_mm"]
                local_center = [(bbox[0][axis] + bbox[1][axis]) / 2.0 for axis in range(2)]
                plate_center = [local_center[axis] - offset[axis] + placement["min"][axis]
                                - stl_min[axis] for axis in range(2)]
                candidates = [(math.dist(plate_center, component["centerXYmm"]), index)
                              for index, component in enumerate(component_rows)]
                distance, component_index = min(candidates, default=(math.inf, None))
                matched = component_index is not None and distance <= 2.0
                support_assignments.append({"supportId": support["id"],
                                            "componentIndex": component_index if matched else None,
                                            "centerDistanceMm": round(distance, 4)
                                            if math.isfinite(distance) else None,
                                            "matched": matched})
                expanded = 6.0
                support_segments = []
                for segment in first_segments:
                    midpoint = ((segment[0] + segment[2]) / 2.0,
                                (segment[1] + segment[3]) / 2.0)
                    in_expanded = all(
                        bbox[0][axis] - offset[axis] + placement["min"][axis]
                        - stl_min[axis] - expanded <= midpoint[axis] <=
                        bbox[1][axis] - offset[axis] + placement["min"][axis]
                        - stl_min[axis] + expanded for axis in range(2))
                    in_support = all(
                        bbox[0][axis] - offset[axis] + placement["min"][axis]
                        - stl_min[axis] - 0.6 <= midpoint[axis] <=
                        bbox[1][axis] - offset[axis] + placement["min"][axis]
                        - stl_min[axis] + 0.6 for axis in range(2))
                    if in_support or (segment[4] == "Brim" and in_expanded):
                        support_segments.append(segment)
                footprint = support_polygon_metrics(
                    support_segments, plate_center, float(support["support_top_z_mm"]))
                split_z = (float(support["support_top_z_mm"])
                           + float(support["product_first_z_mm"])) / 2.0
                spatial_segments = []
                for segment in segments:
                    midpoint = ((segment[0] + segment[2]) / 2.0,
                                (segment[1] + segment[3]) / 2.0)
                    if all(bbox[0][axis] - offset[axis] + placement["min"][axis]
                           - stl_min[axis] - 0.6 <= midpoint[axis] <=
                           bbox[1][axis] - offset[axis] + placement["min"][axis]
                           - stl_min[axis] + 0.6 for axis in range(2)):
                        spatial_segments.append(segment)
                below = [segment for segment in spatial_segments if segment[6] < split_z]
                above = [segment for segment in spatial_segments if segment[6] > split_z]
                support_last = max(below, key=lambda segment: segment[6], default=None)
                product_first = min(above, key=lambda segment: segment[6], default=None)
                declared_gap = float(support["material_face_gap_mm"])
                gap_result = material_face_gap_decision(
                    support_last, product_first, declared_gap)
                material_gap = gap_result["actualGapMm"]
                region_rows = []
                if support.get("support_regions"):
                    for region in support["support_regions"]:
                        support_z = round(float(
                            region["expected_last_support_gcode_z_mm"]), 4)
                        product_z = round(float(
                            region["expected_first_product_gcode_z_mm"]), 4)
                        region_support = max(
                            (segment for segment in spatial_segments
                             if round(float(segment[6]), 4) == support_z),
                            key=lambda segment: segment[6], default=None)
                        region_product = min(
                            (segment for segment in spatial_segments
                             if round(float(segment[6]), 4) == product_z),
                            key=lambda segment: segment[6], default=None)
                        region_gap = material_face_gap_decision(
                            region_support, region_product,
                            float(region["material_face_gap_mm"]))
                        region_rows.append({
                            "id": region["region"],
                            "declaredMaterialFaceGapMm": region["material_face_gap_mm"],
                            "actualSupportLastExtrusionZMm": region_support[6]
                            if region_support is not None else None,
                            "actualProductFirstExtrusionZMm": region_product[6]
                            if region_product is not None else None,
                            "actualMaterialFaceGapMm": round(
                                region_gap["actualGapMm"], 4)
                            if region_gap["actualGapMm"] is not None else None,
                            "decision": "accepted" if region_gap["pass"] else "rejected",
                        })
                    material_gap = min(
                        (row["actualMaterialFaceGapMm"] for row in region_rows
                         if row["actualMaterialFaceGapMm"] is not None), default=None)
                    gap_result = {"actualGapMm": material_gap,
                                  "pass": all(row["decision"] == "accepted"
                                              for row in region_rows)}
                footprint_pass = (footprint["depositedAreaEstimateMm2"] > 0
                                  and footprint["centerOfMassOverSupportHull"]
                                  and footprint["heightToMinimumSupportWidth"] is not None
                                  and footprint["heightToMinimumSupportWidth"] <= 5.0
                                  and gap_result["pass"])
                footprint_row = {
                    "supportId": support["id"], "declaredBboxMm": bbox,
                    "declaredMaterialFaceGapMm": support["material_face_gap_mm"],
                    "actualSupportLastExtrusionZMm": None if region_rows else (
                        support_last[6] if support_last is not None else None),
                    "actualProductFirstExtrusionZMm": None if region_rows else (
                        product_first[6] if product_first is not None else None),
                    "actualMaterialFaceGapMm": round(material_gap, 4)
                    if material_gap is not None else None,
                    "footprint": footprint,
                    "decision": "accepted" if footprint_pass else "rejected",
                }
                if region_rows:
                    footprint_row["regions"] = region_rows
                support_footprints.append(footprint_row)
            product_contact_height = min((row["product_first_z_mm"]
                                          for row in declared_supports), default=height)
            for index, component in enumerate(component_rows):
                support_match = next((row for row in support_assignments
                                      if row["componentIndex"] == index), None)
                if support_match:
                    support = next(row for row in declared_supports
                                   if row["id"] == support_match["supportId"])
                    required_height = float(support["support_top_z_mm"])
                    role = "removable_print_support"
                else:
                    required_height = float(product_contact_height)
                    role = "product_until_support_contact" if declared_supports else "product"
                width = component["minimumSupportWidthMm"]
                ratio = required_height / width if width > 1.0e-6 else None
                component.update({
                    "componentIndex": index, "role": role,
                    "requiredStableHeightMm": round(required_height, 4),
                    "heightToComponentSupportWidth": round(ratio, 4)
                    if ratio is not None else None,
                    "stableToRequiredHeight": ratio is not None and ratio <= 5.0,
                })
            component_stability_pass = (bool(component_rows)
                                        and all(row["stableToRequiredHeight"]
                                                for row in component_rows)
                                        and all(row["decision"] == "accepted"
                                                for row in support_footprints))
            reasons = []
            if not first_segments:
                reasons.append("first_layer_extrusion_missing")
            if metrics["depositedAreaEstimateMm2"] <= 0:
                reasons.append("first_layer_contact_area_missing")
            if not metrics["centerOfMassOverSupportHull"] and len(component_rows) == 1:
                reasons.append("center_of_mass_outside_actual_first_layer_support")
            if metrics["heightToMinimumSupportWidth"] is None:
                reasons.append("actual_first_layer_support_width_not_measurable")
            elif metrics["heightToMinimumSupportWidth"] > 5.0:
                reasons.append("height_exceeds_five_times_actual_first_layer_support_width")
            if not component_stability_pass:
                reasons.append("one_or_more_first_layer_components_are_too_slender_before_connection")
            if declared_supports and not metrics["centerOfMassOverSupportHull"]:
                reasons.append("center_of_mass_outside_combined_support_after_contact")
            row = {"objectId": obj["objectId"], "objectName": obj["name"],
                   "partId": part_id, "firstLayerZMm": first_z,
                   "sourceStlSha256": geometry_report["parts"][part_id]["source"]["sha256"],
                   "features": sorted(set(segment[4] for segment in first_segments)),
                   "segmentCount": len(first_segments), **metrics,
                   "componentStability": {"components": component_rows,
                                          "declaredSupportAssignments": support_assignments,
                                          "supportFootprints": support_footprints,
                                          "pass": component_stability_pass,
                                          "combinedHullAppliesAfterSupportContact": bool(
                                              declared_supports)},
                   "decision": "accepted" if not reasons else "rejected",
                   "reasons": reasons}
            rows.append(row)
            all_rows.append(row)
        plates[plate_key] = {"sourceGcode": source["gcode"],
                             "sourceLayout": source["layout"], "objects": rows}
    calibration = first_layer_calibration()
    end_hashes = {path.relative_to(ROOT).as_posix(): sha256(path)
                  for path in algorithm_paths}
    evidence = {"model": MODEL, "sourceGeometryEvidence": record(geometry_path),
                "sourceManifest": record(BUILD / "manifest.json"),
                "sourceAlgorithmSha256": end_hashes,
                "sourceAlgorithmIntegrity": {"start": start_hashes, "end": end_hashes,
                                             "pass": start_hashes == end_hashes},
                "calibration": calibration, "plates": plates,
                "overall": {"objectMaterialCount": len(all_rows),
                            "failedObjectMaterialCount": sum(
                                row["decision"] != "accepted" for row in all_rows),
                            "pass": calibration["pass"] and start_hashes == end_hashes and all(
                                row["decision"] == "accepted" for row in all_rows)}}
    path = BUILD / "first_layer_contact_evidence.json"
    write_json(path, evidence)
    return path, evidence


def connection_to_established(point, target_width, support_grid):
    candidates = []
    radius = max(1, math.ceil(target_width / 2.0))
    center = (math.floor(point[0]), math.floor(point[1]))
    segments = {}
    for cell_x in range(center[0] - radius, center[0] + radius + 1):
        for cell_y in range(center[1] - radius, center[1] + radius + 1):
            for segment in support_grid.get((cell_x, cell_y), []):
                segments[segment[:6]] = segment
    for path_index, feature, start_x, start_y, end_x, end_y, earlier_width in segments.values():
        distance = locator.point_segment_distance(
            point, (start_x, start_y), (end_x, end_y))
        overlap = (target_width + earlier_width) / 2.0
        candidates.append({
            "pathIndex": path_index,
            "feature": feature,
            "distanceMm": round(distance, 5),
            "targetLineWidthMm": round(target_width, 5),
            "earlierLineWidthMm": round(earlier_width, 5),
            "centerlineOverlapLimitMm": round(overlap, 5),
            "overlaps": distance <= overlap + 1.0e-6,
            "earlierPathEstablished": True,
        })
    return min(candidates, key=lambda row: row["distanceMm"], default=None)


def add_established_chain(support_grid, path_index, chain):
    for segment_index, (start, end) in enumerate(
            zip(chain["points"][:-1], chain["points"][1:])):
        width = chain["widths"][segment_index]
        padding = width / 2.0
        segment = (path_index, chain["feature"], start[0], start[1],
                   end[0], end[1], width)
        for cell_x in range(math.floor(min(start[0], end[0]) - padding),
                            math.floor(max(start[0], end[0]) + padding) + 1):
            for cell_y in range(math.floor(min(start[1], end[1]) - padding),
                                math.floor(max(start[1], end[1]) + padding) + 1):
                support_grid.setdefault((cell_x, cell_y), []).append(segment)


def continuous_previous_support_decision(coverage: dict,
                                         previous_layer_established: bool,
                                         previous_layer_z_contiguous: bool) -> bool:
    return (previous_layer_established
            and previous_layer_z_contiguous
            and coverage["pathCoverageFraction"] == 1.0
            and all(coverage["startAndEndCovered"]))


def chain_layer_heights(segments: list[tuple]) -> list[float]:
    heights = []
    previous_feature = None
    previous_end = None
    for segment in segments:
        start, end, feature = segment[:2], segment[2:4], segment[4]
        if math.dist(start, end) <= 1.0e-6:
            continue
        if (heights and previous_feature == feature
                and math.dist(previous_end, start) <= 1.0e-6):
            heights[-1] = max(heights[-1], float(segment[8]))
        else:
            heights.append(float(segment[8]))
        previous_feature = feature
        previous_end = end
    return heights


def open_interval_decision(actual_span_mm: float,
                           endpoint_established: list[bool]) -> bool:
    return actual_span_mm <= 10.0 and all(endpoint_established)


def support_calibration() -> dict:
    def decide_case(span, start_direct, end_direct, start_prior, end_prior,
                    closed_path=False, closed_accepted=False):
        endpoints = [start_direct or start_prior, end_direct or end_prior]
        if closed_path:
            return closed_accepted
        return open_interval_decision(span, endpoints)

    established_grid = {}
    add_established_chain(established_grid, 0, {
        "feature": "calibration_supported_prior",
        "points": [(0.0, 0.0), (10.0, 0.0)], "widths": [0.4]})
    connected = connection_to_established((5.0, 0.35), 0.4, established_grid)
    separated = connection_to_established((5.0, 0.41), 0.4, established_grid)
    floating = connection_to_established((5.0, 0.0), 0.4, {})
    target_path = {"feature": "calibration_target",
                   "points": [(0.0, 0.0), (10.0, 0.0)], "widths": [0.4]}
    direct_supported = closed.external_path_coverage(
        target_path, [((0.0, 0.0), (10.0, 0.0), 0.4)])
    direct_separated = closed.external_path_coverage(
        target_path, [((0.0, 0.41), (10.0, 0.41), 0.4)])
    cases = [
        {"name": "supported_bridge", "expected": True,
         "actual": decide_case(9.9, True, True, False, False)},
        {"name": "one_end_to_established_prior", "expected": True,
         "actual": decide_case(2.1, True, False, False,
                               connected is not None and connected["overlaps"])},
        {"name": "one_end_to_floating_prior", "expected": False,
         "actual": decide_case(2.1, True, False, False,
                               floating is not None and floating["overlaps"])},
        {"name": "centerlines_outside_combined_half_width", "expected": False,
         "actual": decide_case(2.1, True, False, False,
                               separated is not None and separated["overlaps"])},
        {"name": "open_interval_with_unanchored_start", "expected": False,
         "actual": decide_case(0.08, False, True, False, False)},
        {"name": "bridge_over_limit", "expected": False,
         "actual": decide_case(10.01, True, True, False, False)},
        {"name": "closed_loop_without_closed_proof", "expected": False,
         "actual": decide_case(0.06, False, False, False, False, True, False)},
        {"name": "closed_loop_with_closed_proof", "expected": True,
         "actual": decide_case(4.0, False, False, False, False, True, True)},
        {"name": "whole_path_supported_by_established_previous_layer", "expected": True,
         "actual": continuous_previous_support_decision(direct_supported, True, True)},
        {"name": "whole_path_outside_previous_layer_width", "expected": False,
         "actual": continuous_previous_support_decision(direct_separated, True, True)},
        {"name": "whole_path_over_floating_previous_layer", "expected": False,
         "actual": continuous_previous_support_decision(direct_supported, False, True)},
        {"name": "whole_path_over_established_layer_ten_mm_below", "expected": False,
         "actual": continuous_previous_support_decision(direct_supported, True, False)},
    ]
    return {"cases": cases,
            "pass": all(row["actual"] == row["expected"] for row in cases)}


def continuous_path_evidence(span_reports: dict, sources: dict,
                             closed_evidence_path: Path,
                             closed_evidence: dict) -> tuple[Path, dict]:
    algorithm_paths = [Path(__file__), ROOT / "tools/lattice_print_spans.py",
                       ROOT / "tools/lattice_span_locator.py",
                       ROOT / "tools/lattice_closed_loop_support.py",
                       ROOT / "tools/lattice_delivery.py", ROOT / "tools/plate_3mf.py",
                       ROOT / "lib/printmech/gcode.py"]
    start_hashes = {path.relative_to(ROOT).as_posix(): sha256(path)
                    for path in algorithm_paths}
    closed_decisions = {
        (plate_key, row["objectName"], round(float(row["zMm"]), 4), row["pathIndex"]): row
        for plate_key, plate in closed_evidence["plates"].items()
        for row in plate["closedUnsupportedPaths"]
    }
    manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
    support_geometry_path = BUILD / "print_support_geometry.json"
    support_geometry = json.loads(support_geometry_path.read_text(encoding="utf-8"))
    plates = {}
    all_findings = []
    for plate_key, source in sources.items():
        layer_segments = {}
        for layer in locator.read_width_layers(ROOT / source["gcode"]["file"]):
            if layer["z"] is None:
                continue
            for segment in layer["segs"]:
                layer_segments.setdefault((segment[5], round(float(layer["z"]), 4)), []).append(segment)
        layer_zs = {}
        for object_id, z_mm in layer_segments:
            layer_zs.setdefault(object_id, []).append(z_mm)
        for values in layer_zs.values():
            values.sort()
        findings = []
        for obj in span_reports[plate_key]["objects"]:
            unsupported_layer_zs = {
                round(float(layer["zMm"]), 4) for layer in obj["layers"]
                if layer["intervals"]
            }
            for measured_layer in obj["layers"]:
                z_key = round(float(measured_layer["zMm"]), 4)
                segments = layer_segments.get((obj["objectId"], z_key), [])
                chains = locator.width_chains(segments)
                chain_heights = chain_layer_heights(segments)
                if len(chain_heights) != len(chains):
                    raise RuntimeError(
                        f"chain height mapping mismatch for {obj['name']} at Z={z_key}: "
                        f"{len(chain_heights)} != {len(chains)}")
                intervals_by_path = {}
                for interval in measured_layer["intervals"]:
                    intervals_by_path.setdefault(interval["pathIndex"], []).append(interval)
                established = {}
                support_grid = {}
                for path_index, chain in enumerate(chains):
                    path_findings = []
                    is_closed_path = (
                        math.dist(chain["points"][0], chain["points"][-1]) <= 1.0e-6
                    )
                    previous_levels = [value for value in layer_zs.get(obj["objectId"], [])
                                       if value < z_key - 1.0e-6]
                    previous_z = max(previous_levels, default=None)
                    previous_segments = (layer_segments.get((obj["objectId"], previous_z), [])
                                         if previous_z is not None else [])
                    previous_paths = [
                        ((segment[0], segment[1]), (segment[2], segment[3]), segment[7])
                        for segment in previous_segments
                    ]
                    previous_coverage = closed.external_path_coverage(chain, previous_paths)
                    previous_layer_established = (
                        previous_z is not None and previous_z not in unsupported_layer_zs
                    )
                    expected_previous_z = round(z_key - chain_heights[path_index], 4)
                    previous_layer_z_contiguous = (
                        previous_z is not None
                        and abs(previous_z - expected_previous_z) <= 0.01
                    )
                    continuous_previous_support = continuous_previous_support_decision(
                        previous_coverage, previous_layer_established,
                        previous_layer_z_contiguous)
                    for interval in intervals_by_path.get(path_index, []):
                        target_width = max(chain["widths"])
                        prior = [
                            connection_to_established(interval["startXYmm"], target_width,
                                                      support_grid),
                            connection_to_established(interval["endXYmm"], target_width,
                                                      support_grid),
                        ]
                        prior_overlap = [row is not None and row["overlaps"] for row in prior]
                        direct = [bool(interval["supportedBefore"]),
                                  bool(interval["supportedAfter"])]
                        endpoint_established = [direct[index] or prior_overlap[index]
                                                for index in range(2)]
                        span = actual_span(interval)
                        closed_row = closed_decisions.get(
                            (plate_key, obj["name"], z_key, path_index))
                        if is_closed_path:
                            accepted = (closed_row is not None
                                        and closed_row["decision"] == "accepted")
                            basis = ("閉環は専用計器で全周の直下支持または成立済み先行線への接続を確認。"
                                     if accepted else
                                     "閉環の短い端点距離を根拠にせず、専用計器の支持証明が成立していない。")
                        elif continuous_previous_support:
                            accepted = True
                            basis = ("経路全体が成立済み直下層の実押出へ、両線幅の半分和以内で連続する。")
                        else:
                            accepted = open_interval_decision(span, endpoint_established)
                            basis = ("区間両端が直下支持または成立済み先行経路へ実線幅内で接続する。"
                                     if accepted else
                                     "区間両端の支持または成立済み先行経路への実線幅内接続が不足する。")
                        finding = {
                            "key": interval_key(plate_key, obj["name"], z_key, interval),
                            "objectId": obj["objectId"], "objectName": obj["name"],
                            "zMm": z_key, "pathIndex": path_index,
                            "feature": interval["feature"], "category": interval["category"],
                            "support": interval["support"],
                            "pathLengthMm": interval["lengthMm"],
                            "actualSpanMm": round(span, 4),
                            "lineWidthMm": round(target_width, 5),
                            "startXYmm": interval["startXYmm"],
                            "endXYmm": interval["endXYmm"],
                            "directPreviousLayerSupport": direct,
                            "priorEstablishedPathConnections": prior,
                            "endpointEstablished": endpoint_established,
                            "closedPath": is_closed_path,
                            "closedLoopEvidenceDecision": (
                                closed_row["decision"] if closed_row else None),
                            "continuousPreviousLayerEvidence": {
                                "previousLayerZMm": previous_z,
                                "previousLayerEstablished": previous_layer_established,
                                "currentLayerHeightMm": round(chain_heights[path_index], 4),
                                "expectedPreviousLayerZMm": expected_previous_z,
                                "previousLayerZContiguous": previous_layer_z_contiguous,
                                **previous_coverage,
                            },
                            "decision": "accepted" if accepted else "rejected",
                            "basis": basis,
                        }
                        findings.append(finding)
                        path_findings.append(finding)
                    established[path_index] = all(
                        row["decision"] == "accepted" for row in path_findings)
                    if established[path_index]:
                        add_established_chain(support_grid, path_index, chain)
                for path_index in sorted(set(intervals_by_path) - set(range(len(chains)))):
                    for interval in intervals_by_path[path_index]:
                        finding = {
                            "key": interval_key(plate_key, obj["name"], z_key, interval),
                            "objectId": obj["objectId"], "objectName": obj["name"],
                            "zMm": z_key, "pathIndex": path_index,
                            "feature": interval["feature"], "category": interval["category"],
                            "support": interval["support"],
                            "pathLengthMm": interval["lengthMm"],
                            "actualSpanMm": round(actual_span(interval), 4),
                            "decision": "rejected",
                            "basis": "span計器のpathIndexを実G-code幅付き経路へ対応付けられない。",
                        }
                        findings.append(finding)

        apply_c42_external_support(
            findings, source, span_reports[plate_key], manifest,
            support_geometry_path, support_geometry)
        all_findings.extend(findings)
        plates[plate_key] = {
            "sourceGcode": source["gcode"], "sourceLayout": source["layout"],
            "sourceSpanReport": source["span"],
            "summary": {"findingCount": len(findings),
                        "failedFindingCount": sum(row["decision"] != "accepted"
                                                  for row in findings)},
            "unsupportedIntervals": findings,
        }
    end_hashes = {path.relative_to(ROOT).as_posix(): sha256(path)
                  for path in algorithm_paths}
    calibration = support_calibration()
    evidence = {
        "model": MODEL, "sourceClosedLoopEvidence": record(closed_evidence_path),
        "sourceAlgorithmSha256": end_hashes,
        "sourceAlgorithmIntegrity": {"start": start_hashes, "end": end_hashes,
                                     "pass": start_hashes == end_hashes},
        "calibration": calibration,
        "overall": {"findingCount": len(all_findings),
                    "failedFindingCount": sum(row["decision"] != "accepted"
                                              for row in all_findings),
                    "pass": calibration["pass"] and start_hashes == end_hashes
                            and all(row["decision"] == "accepted" for row in all_findings)},
        "plates": plates,
    }
    path = BUILD / "continuous_path_support_evidence.json"
    write_json(path, evidence)
    return path, evidence


def decide(span_reports: dict, sources: dict,
           continuous_evidence: dict) -> tuple[list[dict], list[dict]]:
    support_findings = {
        row["key"]: row
        for plate in continuous_evidence["plates"].values()
        for row in plate["unsupportedIntervals"]
    }
    objects = {}
    rejected = []
    for key, report in span_reports.items():
        layout = delivery_tool.inspect_layout(ROOT / sources[key]["layout"]["file"])
        offset = report["objectAssignment"]["detail"]["global_offset_mm"]
        for obj in report["objects"]:
            name = obj["name"]
            placement = next(item for item in layout["objects"] if item["name"] == name)
            stl_path = ROOT / "prints" / MODEL / f"{name}.stl"
            vertices, _faces = delivery_tool.plate_3mf.read_stl(str(stl_path))
            stl_min = [min(point[axis] for point in vertices) for axis in range(3)]

            def local(point):
                return [round(point[axis] + offset[axis] - placement["min"][axis]
                              + stl_min[axis], 4) for axis in range(2)]

            row = objects.setdefault(name, {"id": name.rsplit("-print-", 1)[-1],
                                             "plates": [], "max_actual_span_mm": 0.0,
                                             "warnings": []})
            row["plates"].append(key)
            for layer in obj["layers"]:
                for interval in layer["intervals"]:
                    length = float(interval["lengthMm"])
                    bounds = interval["boundsXYmm"]
                    measured_span = actual_span(interval)
                    row["max_actual_span_mm"] = max(row["max_actual_span_mm"], measured_span)
                    finding = support_findings.get(
                        interval_key(key, name, layer["zMm"], interval))
                    reason = None if finding and finding["decision"] == "accepted" \
                        else "continuous_path_support_not_established"
                    if reason:
                        warning = {"plate": key, "object": name, "zMm": layer["zMm"],
                                   "pathIndex": interval["pathIndex"], "feature": interval["feature"],
                                   "category": interval["category"], "support": interval["support"],
                                   "pathLengthMm": length,
                                   "actualSpanMm": round(measured_span, 4),
                                   "startXYmm": interval["startXYmm"],
                                   "endXYmm": interval["endXYmm"],
                                   "boundsXYmm": bounds, "reason": reason,
                                   "supportEvidence": finding}
                        warning["printStlEndpointsMm"] = [
                            [*local(interval["startXYmm"]), layer["zMm"]],
                            [*local(interval["endXYmm"]), layer["zMm"]],
                        ]
                        warning["printStlBoundsXYMm"] = [
                            [round(bounds[axis][edge] + offset[axis] - placement["min"][axis]
                                   + stl_min[axis], 4) for edge in range(2)]
                            for axis in range(2)
                        ]
                        row["warnings"].append(warning)
                        rejected.append(warning)
    rows = []
    for row in objects.values():
        row["max_actual_span_mm"] = round(row["max_actual_span_mm"], 4)
        row["decision"] = "accepted" if not row["warnings"] else "rejected"
        rows.append(row)
    return sorted(rows, key=lambda row: row["id"]), rejected


def decide_geometry(report: dict, first_layer_report: dict) -> tuple[list[dict], bool]:
    first_layer_by_part = {}
    for plate_key, plate in first_layer_report["plates"].items():
        for row in plate["objects"]:
            first_layer_by_part.setdefault(row["partId"], []).append(
                {"plate": plate_key, **row})
    rows = []
    for part_id, measured in report["parts"].items():
        actual = report["actualBedSupport"][part_id]
        orientation = report["orientationCandidates"][part_id]
        reasons = []
        if actual["contactAreaMm2"] <= 0:
            reasons.append("bed_contact_missing")
        if not actual["centerOfMassOverSupportHull"]:
            reasons.append("center_of_mass_outside_bed_support_hull")
        if actual["heightToMinimumSupportWidth"] is None:
            reasons.append("bed_support_width_not_measurable")
        elif actual["heightToMinimumSupportWidth"] > 5.0:
            reasons.append("height_exceeds_five_times_minimum_support_width")
        unacceptable_thin = [row for row in measured["thinUnder1_2mm"]
                             if float(row["min_mm"]) < 1.19]
        if unacceptable_thin:
            reasons.append("detected_thickness_below_1_2mm_requires_geometry_fix_or_witness")
        first_layer_checks = first_layer_by_part.get(part_id, [])
        if not first_layer_checks:
            reasons.append("actual_first_layer_evidence_missing")
        elif any(row["decision"] != "accepted" for row in first_layer_checks):
            reasons.append("actual_first_layer_support_rejected")
        rows.append({"id": part_id, "source_stl_sha256": measured["source"]["sha256"],
                     "bedContactMm2": actual["contactAreaMm2"],
                     "centerOfMassOverFootprint": actual["centerOfMassOverSupportHull"],
                     "heightToMinimumFootprint": actual["heightToMinimumSupportWidth"],
                     "actualBedSupport": actual,
                     "thinClusterCount": measured["thinClusterCount"],
                     "unacceptableThinClusters": unacceptable_thin,
                     "actualFirstLayerChecks": first_layer_checks,
                     "selectedOrientation": orientation["adopted"],
                     "numericOrientationPreference": orientation["numericPreference"],
                     "orientationAdoptionBasis": orientation["adoptionBasis"],
                     "decision": "accepted" if not reasons else "rejected",
                     "reasons": reasons,
                     "physicalStabilityVerified": False})
    feature = report.get("featureThickness", {})
    feature_pass = all(bool(feature.get(name, {}).get("pass")) for name in (
        "exposedHexWalls", "guideSleeveWalls", "driveKeyLoadShaft", "keeperLoadTabs"))
    return rows, feature_pass and all(row["decision"] == "accepted" for row in rows)


def run() -> tuple[Path, dict]:
    manifest, delivery, manifest_path, delivery_path = load_inputs()
    support_geometry_path, support_geometry_report = load_support_geometry(
        manifest, manifest_path)
    span_reports, sources = generate_spans(delivery)
    geometry_path, geometry_report = geometry_evidence(manifest, manifest_path, sources)
    first_layer_path, first_layer_report = first_layer_evidence(
        span_reports, sources, geometry_path, geometry_report)
    closed_path, closed_report = closed_loop_evidence(span_reports, sources)
    continuous_path, continuous_report = continuous_path_evidence(
        span_reports, sources, closed_path, closed_report)
    objects, rejected = decide(span_reports, sources, continuous_report)
    geometry_checks, geometry_pass = decide_geometry(geometry_report, first_layer_report)
    calibrations_pass = (geometry_report["calibrationPass"]
                         and geometry_report["sourceIntegrity"]["pass"]
                         and first_layer_report["calibration"]["pass"]
                         and first_layer_report["sourceAlgorithmIntegrity"]["pass"]
                         and support_geometry_report["calibration"]["pass"]
                         and support_geometry_report["sourceAlgorithmIntegrity"]["pass"]
                         and closed_report["calibration"]["pass"]
                         and closed_report["sourceAlgorithmIntegrity"]["pass"]
                         and continuous_report["calibration"]["pass"]
                         and continuous_report["sourceAlgorithmIntegrity"]["pass"]
                         and all(report["calibration"]["pass"]
                                 and report["objectAssignment"]["complete"]
                                 for report in span_reports.values()))
    support_settings_pass = all(
        str(result.get("support_used")).lower() == "false"
        for plate in delivery["plates"].values()
        for result in plate["materials"].values())
    accepted = (calibrations_pass and geometry_pass
                and support_settings_pass and closed_report["overall"]["pass"]
                and continuous_report["overall"]["pass"]
                and first_layer_report["overall"]["pass"]
                and support_geometry_report["overall"]["pass"] and not rejected)
    evidence = {
        "version": 1, "model": MODEL, "calibrationPass": calibrations_pass,
        "sourceAlgorithms": {
            path.relative_to(ROOT).as_posix(): sha256(path) for path in (
                Path(__file__), ROOT / "tools/lattice_print_spans.py",
                ROOT / "tools/lattice_span_locator.py",
                ROOT / "tools/lattice_closed_loop_support.py",
                ROOT / "tools/lattice_print_geometry_review.py",
                ROOT / "tools/lattice_delivery.py")
        },
        "sources": {"manifest": record(manifest_path), "delivery": record(delivery_path),
                    "geometry": record(geometry_path), "closedLoops": record(closed_path),
                    "continuousPaths": record(continuous_path),
                    "firstLayerContact": record(first_layer_path),
                    "printSupportGeometry": record(support_geometry_path),
                    "plates": sources},
        "geometryChecks": geometry_checks,
        "featureThickness": geometry_report.get("featureThickness"),
        "objects": objects, "rejectedPaths": rejected,
        "summary": {"plateMaterialCount": len(sources), "objectCount": len(objects),
                    "rejectedPathCount": len(rejected), "geometryPass": geometry_pass,
                    "closedLoopPass": closed_report["overall"]["pass"],
                    "continuousPathPass": continuous_report["overall"]["pass"],
                    "firstLayerContactPass": first_layer_report["overall"]["pass"],
                    "printSupportGeometryPass": support_geometry_report["overall"]["pass"],
                    "supportDisabledOnAllSlices": support_settings_pass},
    }
    evidence_path = BUILD / "print_path_evidence.json"
    write_json(evidence_path, evidence)
    review = {
        "version": 1, "model": MODEL,
        "status": "accepted_with_fit_test" if accepted else "review_required",
        "delivery_status": delivery.get("status"), "physical_print_verified": False,
        "basis": {"manifest_sha256": sha256(manifest_path),
                  "delivery_report_sha256": sha256(delivery_path),
                  "print_geometry_evidence_sha256": sha256(geometry_path),
                  "closed_loop_support_evidence_sha256": sha256(closed_path),
                  "continuous_path_support_evidence_sha256": sha256(continuous_path),
                  "first_layer_contact_evidence_sha256": sha256(first_layer_path),
                  "print_support_geometry_sha256": sha256(support_geometry_path),
                  "print_path_evidence_sha256": sha256(evidence_path),
                  "print_review_source_sha256": sha256(Path(__file__)),
                  "gcode_sha256": {key: source["gcode"]["sha256"] for key, source in sources.items()},
                  "layout_sha256": {key: source["layout"]["sha256"] for key, source in sources.items()},
                  "span_sha256": {key: source["span"]["sha256"] for key, source in sources.items()}},
        "calibration_pass": calibrations_pass,
        "support_check": {"decision": "accepted" if support_settings_pass else "rejected",
                          "support_used_values": {
                              f"{plate_id}_{material}": result.get("support_used")
                              for plate_id, plate in delivery["plates"].items()
                              for material, result in plate["materials"].items()}},
        "geometry_check": {"decision": "accepted" if geometry_pass else "rejected",
                           "parts": geometry_checks,
                           "featureThickness": geometry_report.get("featureThickness")},
        "closed_loop_check": {"decision": "accepted" if closed_report["overall"]["pass"] else "rejected",
                              "unresolved": [row for plate in closed_report["plates"].values()
                                             for row in plate["closedUnsupportedPaths"]
                                             if row["decision"] != "accepted"]},
        "continuous_path_check": {
            "decision": "accepted" if continuous_report["overall"]["pass"] else "rejected",
            "unresolved": [row for plate in continuous_report["plates"].values()
                           for row in plate["unsupportedIntervals"]
                           if row["decision"] != "accepted"]},
        "first_layer_contact_check": {
            "decision": "accepted" if first_layer_report["overall"]["pass"] else "rejected",
            "calibration_pass": first_layer_report["calibration"]["pass"],
            "unresolved": [row for plate in first_layer_report["plates"].values()
                           for row in plate["objects"] if row["decision"] != "accepted"]},
        "print_support_geometry_check": {
            "decision": "accepted" if support_geometry_report["overall"]["pass"] else "rejected",
            "parts": support_geometry_report["parts"]},
        "objects": objects,
        "fit_test": {"present": "fit_test" in delivery["plates"],
                     "decision": "slice_pass" if accepted else "review_required"},
        "limitations": ["ホーン嵌合、材料収縮、除去式支持の外しやすさは実機未確認。",
                        "高さ/最小接地幅が5を超える部品は印刷中の安定性を実機未確認として不合格にする。"],
    }
    review_path = BUILD / "print_path_review.json"
    write_json(review_path, review)
    return review_path, review


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--output", type=Path, help=argparse.SUPPRESS)
    if argv is None and "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
    args = parser.parse_args(argv)
    if args.geometry_worker:
        if args.output is None:
            parser.error("--geometry-worker requires --output")
        geometry_worker(args.output)
        return 0
    path, review = run()
    print(f"[print-review] report: {path}")
    print(f"[print-review] status={review['status']} objects={len(review['objects'])} "
          f"rejected={sum(len(row['warnings']) for row in review['objects'])}")
    return 0 if review["status"] == "accepted_with_fit_test" else 2


if __name__ == "__main__":
    raise SystemExit(main())
