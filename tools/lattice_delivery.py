"""manifest から印刷 STL、配置済み 3MF、スライス済み 3MF をまとめる。

    py -3.11 tools/lattice_delivery.py <model-id> [--material PLA|PETG|both]

入力は models/<model-id>/build/manifest.json。印刷物は prints/<model-id>/、
検査結果は models/<model-id>/build/delivery_report.json に書く。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
import uuid
import zipfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
PRINTS = ROOT / "prints"
EXPORTS = ROOT / "exports"
BAMBU_STUDIO = Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe")
BED = (256.0, 256.0, 250.0)
EXCLUDE = (18.0, 28.0)
MACHINE = "Bambu Lab X1 Carbon 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL X1C"
FILAMENTS = {
    "PLA": "Bambu PLA Basic @BBL X1C",
    "PETG": "Bambu PETG Basic @BBL X1C",
}
OVERRIDES = {
    "curr_bed_type": "Textured PEI Plate",
    "layer_height": "0.2",
    "wall_loops": "3",
    "exclude_object": "1",
    "enable_support": "0",
}
IDENTITY = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0)
SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
BBOX_ENDPOINT_TOLERANCE = 0.8  # ノズル半幅、経路量子化、外周線中心の差を含む上限 [mm]

sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))

import plate_3mf  # noqa: E402
from bambu_profiles import resolve, write_flat  # noqa: E402
from printmech.gcode import parse_gcode  # noqa: E402
from printmech.stl import write_binary_stl  # noqa: E402
from printmech.three_mf import inspect_sliced_3mf  # noqa: E402
from studio_plate import export_studio_plate  # noqa: E402


def _tag(element):
    return element.tag.rsplit("}", 1)[-1]


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path, base=ROOT):
    path = Path(path)
    try:
        name = path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        name = str(path.resolve())
    return {"file": name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def _atomic_copy(source, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    try:
        shutil.copyfile(source, temporary)
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return destination


def _atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with open(temporary, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _model_path(model_dir, value, field):
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty path")
    path = (model_dir / value).resolve()
    try:
        path.relative_to(model_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"{field} escapes the model directory: {value!r}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"{field} does not exist: {path}")
    return path


def load_manifest(model_id):
    if not SAFE_ID.fullmatch(model_id) or model_id in {".", ".."}:
        raise ValueError(f"unsafe model id: {model_id!r}")
    model_dir = MODELS / model_id
    manifest_path = model_dir / "build" / "manifest.json"
    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)
    source_parts = manifest.get("parts")
    if not isinstance(source_parts, list) or not source_parts:
        raise ValueError(f"manifest parts must be a non-empty list: {manifest_path}")
    parts = []
    seen = set()
    for index, raw in enumerate(source_parts):
        if not isinstance(raw, dict):
            raise ValueError(f"parts[{index}] must be an object")
        part_id = raw.get("id")
        if not isinstance(part_id, str) or not SAFE_ID.fullmatch(part_id):
            raise ValueError(f"parts[{index}].id is unsafe: {part_id!r}")
        if part_id in seen:
            raise ValueError(f"duplicate part id: {part_id}")
        seen.add(part_id)
        label = raw.get("label")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"part {part_id}: label must be a non-empty string")
        assembly = _model_path(model_dir, raw.get("assembly"), f"part {part_id} assembly")
        print_value = raw.get("print")
        print_path = None if print_value is None else _model_path(
            model_dir, print_value, f"part {part_id} print"
        )
        fit_test = raw.get("fit_test", False)
        if not isinstance(fit_test, bool):
            raise ValueError(f"part {part_id}: fit_test must be boolean")
        fit_only = raw.get("fit_only", False)
        if not isinstance(fit_only, bool):
            raise ValueError(f"part {part_id}: fit_only must be boolean")
        if fit_test and print_path is None:
            raise ValueError(f"part {part_id}: a reference part cannot be a fit test")
        if fit_only and not fit_test:
            raise ValueError(f"part {part_id}: fit_only requires fit_test=true")
        if fit_only and print_path is None:
            raise ValueError(f"part {part_id}: fit_only requires a print STL")
        parts.append({
            "id": part_id,
            "label": label,
            "assembly": assembly,
            "print": print_path,
            "fit_test": fit_test,
            "fit_only": fit_only,
        })
    if not any(part["print"] for part in parts):
        raise ValueError("manifest has no printable parts")
    return model_dir, manifest_path, parts


def _transform(points, value):
    matrix = IDENTITY if not value else tuple(float(field) for field in value.split())
    if len(matrix) != 12 or not all(math.isfinite(field) for field in matrix):
        raise ValueError(f"invalid 3MF transform: {value!r}")
    return [
        (
            x * matrix[0] + y * matrix[3] + z * matrix[6] + matrix[9],
            x * matrix[1] + y * matrix[4] + z * matrix[7] + matrix[10],
            x * matrix[2] + y * matrix[5] + z * matrix[8] + matrix[11],
        )
        for x, y, z in points
    ]


def inspect_layout(path, expected_names=None):
    """3MF の XML から配置後の境界、重なり、除外域を調べる。"""
    with zipfile.ZipFile(path) as archive:
        documents = {
            name.lstrip("/"): ET.fromstring(archive.read(name))
            for name in archive.namelist()
            if name.lower().endswith(".model")
        }
        try:
            main = documents["3D/3dmodel.model"]
        except KeyError as exc:
            raise ValueError(f"3mf has no 3D/3dmodel.model: {path}") from exc
        if main.attrib.get("unit", "millimeter") != "millimeter":
            raise ValueError(f"3mf unit is not millimeter: {path}")
        labels = {}
        try:
            config = ET.fromstring(archive.read("Metadata/model_settings.config"))
        except KeyError:
            config = None
        if config is not None:
            for obj in config.iter():
                if _tag(obj) != "object" or "id" not in obj.attrib:
                    continue
                for child in obj:
                    if (_tag(child) == "metadata" and child.attrib.get("key") == "name"
                            and child.attrib.get("value")):
                        labels[obj.attrib["id"]] = child.attrib["value"]
                        break

        def object_points(document_name, object_id, stack=()):
            key = (document_name, object_id)
            if key in stack:
                raise ValueError(f"3mf component cycle at {document_name}#{object_id}")
            document = documents.get(document_name)
            if document is None:
                raise ValueError(f"3mf references missing model: {document_name}")
            obj = next((node for node in document.iter()
                        if _tag(node) == "object" and node.attrib.get("id") == object_id), None)
            if obj is None:
                raise ValueError(f"3mf references missing object: {document_name}#{object_id}")
            mesh = next((node for node in obj if _tag(node) == "mesh"), None)
            if mesh is not None:
                vertices = next((node for node in mesh if _tag(node) == "vertices"), None)
                if vertices is None:
                    raise ValueError(f"3mf object has no vertices: {document_name}#{object_id}")
                points = [tuple(float(vertex.attrib[axis]) for axis in ("x", "y", "z"))
                          for vertex in vertices if _tag(vertex) == "vertex"]
                if not points:
                    raise ValueError(f"3mf object is empty: {document_name}#{object_id}")
                return points
            components = next((node for node in obj if _tag(node) == "components"), None)
            if components is None:
                raise ValueError(f"3mf object has neither mesh nor components: {document_name}#{object_id}")
            points = []
            for component in components:
                if _tag(component) != "component":
                    continue
                child_document = next(
                    (value.lstrip("/") for name, value in component.attrib.items()
                     if name.rsplit("}", 1)[-1] == "path"),
                    document_name,
                )
                child = object_points(child_document, component.attrib["objectid"], stack + (key,))
                points.extend(_transform(child, component.attrib.get("transform")))
            return points

        build = next((node for node in main if _tag(node) == "build"), None)
        if build is None:
            raise ValueError(f"3mf has no build: {path}")
        rows = []
        for item in build:
            if _tag(item) != "item":
                continue
            object_id = item.attrib["objectid"]
            points = _transform(
                object_points("3D/3dmodel.model", object_id), item.attrib.get("transform")
            )
            lower = [min(point[axis] for point in points) for axis in range(3)]
            upper = [max(point[axis] for point in points) for axis in range(3)]
            rows.append({
                "id": object_id,
                "name": labels.get(object_id, object_id),
                "min": [round(value, 4) for value in lower],
                "max": [round(value, 4) for value in upper],
                "off_bed": (
                    lower[0] < -0.001 or lower[1] < -0.001 or lower[2] < -0.001
                    or upper[0] > BED[0] + 0.001 or upper[1] > BED[1] + 0.001
                    or upper[2] > BED[2] + 0.001
                ),
                "excluded": any(point[0] < EXCLUDE[0] and point[1] < EXCLUDE[1]
                                for point in points),
            })
    overlaps = []
    for index, left in enumerate(rows):
        for right in rows[index + 1:]:
            overlap_x = min(left["max"][0], right["max"][0]) - max(left["min"][0], right["min"][0])
            overlap_y = min(left["max"][1], right["max"][1]) - max(left["min"][1], right["min"][1])
            if overlap_x > 0.001 and overlap_y > 0.001:
                overlaps.append({
                    "objects": [left["name"], right["name"]],
                    "overlap_mm": [round(overlap_x, 4), round(overlap_y, 4)],
                })
    actual = {row["name"].removesuffix(".stl") for row in rows}
    expected = set(expected_names or actual)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    issues = []
    if overlaps:
        issues.append("bbox_overlap")
    if any(row["off_bed"] for row in rows):
        issues.append("off_bed")
    if any(row["excluded"] for row in rows):
        issues.append("excluded_area")
    if missing or extra:
        issues.append("object_set_mismatch")
    return {
        "ok": not issues,
        "objects": rows,
        "bbox_overlaps": overlaps,
        "missing": missing,
        "extra": extra,
        "issues": issues,
    }


def create_layout(destination, stls):
    """plate_3mf.py で 6mm 間隔に配置し、その XML を独立に再検査する。"""
    for path in stls:
        vertices, faces = plate_3mf.read_stl(str(path))
        if not vertices or not faces:
            raise ValueError(f"empty STL: {path}")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = f"_delivery-{destination.stem}-{os.getpid()}-{uuid.uuid4().hex}"
    temporary = EXPORTS / f"{temporary_name}.3mf"
    command = [
        sys.executable, str(ROOT / "tools" / "plate_3mf.py"), temporary_name,
        *(str(path) for path in stls), "--bed=x1c",
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if result.returncode != 0 or not temporary.is_file():
            raise RuntimeError(
                f"plate_3mf failed (exit {result.returncode}): "
                f"{(result.stdout or '')[-1000:]}{(result.stderr or '')[-1000:]}"
            )
        expected = [Path(path).stem for path in stls]
        placement = inspect_layout(temporary, expected)
        if not placement["ok"]:
            raise RuntimeError(f"invalid plate layout {destination}: {placement['issues']}")
        _atomic_copy(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return placement


def write_settings(work_dir, material):
    material_dir = Path(work_dir) / material
    machine = resolve("machine", MACHINE)
    process = resolve("process", PROCESS)
    process.update(OVERRIDES)
    filament = resolve("filament", FILAMENTS[material])
    paths = {
        "machine": Path(write_flat(str(material_dir / "machine.json"), machine)),
        "process": Path(write_flat(str(material_dir / "process.json"), process)),
        "filament": Path(write_flat(str(material_dir / "filament.json"), filament)),
    }
    return paths


def slice_plate(layout, destination, material, settings, work_dir, logs_dir, tag):
    logs_dir = Path(logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{tag}.log"
    if not BAMBU_STUDIO.is_file():
        log_path.write_text(
            f"Bambu Studio CLI does not exist: {BAMBU_STUDIO}\n",
            encoding="utf-8", newline="\n",
        )
        raise FileNotFoundError(f"Bambu Studio CLI does not exist: {BAMBU_STUDIO}")
    out_dir = Path(work_dir) / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    out_name = "sliced.3mf"
    output = out_dir / out_name
    if output.exists():
        output.unlink()
    command = [
        str(BAMBU_STUDIO), "--slice", "0", "--debug", "2", "--arrange", "0",
        "--load-settings", f"{settings['machine']};{settings['process']}",
        "--load-filaments", str(settings["filament"]),
        "--outputdir", str(out_dir), "--export-3mf", out_name, str(layout),
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
    except OSError as exc:
        log_path.write_text(
            "command: " + subprocess.list2cmdline(command) + f"\n\n{exc}\n",
            encoding="utf-8", newline="\n",
        )
        raise RuntimeError(f"slice could not start for {tag}; log: {log_path}") from exc
    log_path.write_text(
        "command: " + subprocess.list2cmdline(command) + "\n\n"
        + (result.stdout or "") + "\n" + (result.stderr or ""),
        encoding="utf-8", newline="\n",
    )
    if result.returncode != 0 or not output.is_file():
        raise RuntimeError(
            f"slice failed for {tag} (exit {result.returncode}); log: {log_path}"
        )
    _atomic_copy(output, destination)
    try:
        inspection = inspect_sliced_3mf(str(destination))
    except Exception as exc:
        raise RuntimeError(f"sliced 3mf inspection failed for {tag}; log: {log_path}") from exc
    if str(inspection["support_used"]).lower() != "false":
        raise RuntimeError(f"support was generated for {tag}; log: {log_path}")
    return inspection, log_path


def _slice_info_names(path):
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("Metadata/slice_info.config"))
    names = {}
    for element in root.iter():
        object_id = element.attrib.get("identify_id")
        name = element.attrib.get("name")
        if object_id is not None and name:
            names[object_id] = name.removesuffix(".stl")
    return names


def _outer_wall_bboxes(path):
    """G-code の物体IDごとに Outer wall 押出経路の XY bbox を返す。"""
    with zipfile.ZipFile(path) as archive:
        gcode_names = [name for name in archive.namelist() if name.endswith(".gcode")]
        if len(gcode_names) != 1:
            raise ValueError(f"expected one G-code in sliced 3mf, found {gcode_names}")
        gcode = archive.read(gcode_names[0])
    with tempfile.TemporaryDirectory(prefix="lattice_delivery_") as temporary_dir:
        temporary = Path(temporary_dir) / "plate.gcode"
        temporary.write_bytes(gcode)
        layers, _ = parse_gcode(str(temporary))
    points = {}
    for layer in layers:
        for x0, y0, x1, y1, feature, object_id, _z in layer["segs"]:
            if feature != "Outer wall":
                continue
            points.setdefault(str(object_id), []).extend(((x0, y0), (x1, y1)))
    return {
        object_id: [min(x for x, _ in values), min(y for _, y in values),
                    max(x for x, _ in values), max(y for _, y in values)]
        for object_id, values in points.items()
    }


def _bbox_object_assignment(
        path, object_ids, expected_names, tolerance=BBOX_ENDPOINT_TOLERANCE):
    """配置bboxと外周経路bboxを端点誤差 tolerance mm 以内で一意に対応させる。"""
    layout = inspect_layout(path)
    layout_bboxes = {
        row["name"].removesuffix(".stl"): [
            row["min"][0], row["min"][1], row["max"][0], row["max"][1]
        ]
        for row in layout["objects"]
        if row["name"].removesuffix(".stl") in expected_names
    }
    outer_bboxes = _outer_wall_bboxes(path)
    available_outer = [outer_bboxes[object_id] for object_id in object_ids
                       if object_id in outer_bboxes]
    if layout_bboxes and len(available_outer) == len(object_ids):
        layout_union = [
            min(bbox[0] for bbox in layout_bboxes.values()),
            min(bbox[1] for bbox in layout_bboxes.values()),
            max(bbox[2] for bbox in layout_bboxes.values()),
            max(bbox[3] for bbox in layout_bboxes.values()),
        ]
        outer_union = [
            min(bbox[0] for bbox in available_outer),
            min(bbox[1] for bbox in available_outer),
            max(bbox[2] for bbox in available_outer),
            max(bbox[3] for bbox in available_outer),
        ]
        offset = [
            (layout_union[0] + layout_union[2] - outer_union[0] - outer_union[2]) / 2,
            (layout_union[1] + layout_union[3] - outer_union[1] - outer_union[3]) / 2,
        ]
    else:
        offset = [0.0, 0.0]
    candidates = {}
    errors = {}
    for object_id in object_ids:
        outer = outer_bboxes.get(object_id)
        if outer is None:
            candidates[object_id] = []
            errors[object_id] = {}
            continue
        outer = [outer[0] + offset[0], outer[1] + offset[1],
                 outer[2] + offset[0], outer[3] + offset[1]]
        errors[object_id] = {
            name: round(max(abs(left - right) for left, right in zip(outer, bbox)), 4)
            for name, bbox in layout_bboxes.items()
        }
        candidates[object_id] = [
            name for name, error in errors[object_id].items() if error <= tolerance
        ]
    selected = {
        object_id: names[0] for object_id, names in candidates.items() if len(names) == 1
    }
    if (len(selected) != len(object_ids)
            or len(set(selected.values())) != len(selected)):
        return {}, {"candidates": candidates, "endpoint_errors_mm": errors}
    return selected, {
        "tolerance_mm": tolerance,
        "global_offset_mm": [round(value, 4) for value in offset],
        "matches": {
            object_id: {
                "name": name,
                "candidate_count": len(candidates[object_id]),
                "max_endpoint_error_mm": errors[object_id][name],
            }
            for object_id, name in selected.items()
        },
    }


def normalize_object_results(path, inspection, expected_names):
    label_by_id = _slice_info_names(path)
    expected = list(expected_names)
    output = {}
    pending = []
    for raw_name, value in inspection["objects"].items():
        name = str(raw_name).removesuffix(".stl")
        name = label_by_id.get(name, name)
        match = next((label for label in expected
                      if name == label or name.endswith("/" + label)), None)
        if match is None:
            pending.append((name, value))
        else:
            output[match] = value
    remaining = [name for name in expected if name not in output]
    bbox_check = None
    ids_are_matchable = all(name.isdigit() for name, _ in pending) or (
        len(pending) == 1 and pending[0][0] == "None"
    )
    if pending and len(pending) == len(remaining) and ids_are_matchable:
        matched, bbox_check = _bbox_object_assignment(
            path, [name for name, _ in pending], remaining
        )
        if matched:
            for name, value in pending:
                output[matched[name]] = value
            pending = []
            remaining = []
    assignment = {
        "missing": remaining,
        "unassigned": [name for name, _ in pending],
        "bbox_check": bbox_check,
    }
    if remaining or pending:
        raise RuntimeError(f"could not assign sliced objects uniquely: {assignment}")
    return output, assignment


def unsupported_findings(objects):
    findings = []
    for name, result in objects.items():
        length = float(result.get("floating", {}).get("external_unsupported_mm", 0.0) or 0.0)
        if length > 0.01:
            findings.append({
                "object": name,
                "external_unsupported_mm": round(length, 2),
                "worst_layers": result.get("overhang_walls", []),
            })
    return findings


def _external_unsupported_mm(objects, name, missing):
    value = objects.get(name, {}).get("floating", {}).get("external_unsupported_mm")
    return float(missing if value is None else value)


def _gamma_triangles():
    polygon = [(0, 0), (10, 0), (10, 10), (20, 10), (20, 12), (0, 12)]
    caps = [(0, 1, 2), (0, 2, 5), (2, 3, 4), (2, 4, 5)]
    front = [(x, 0.0, z) for x, z in polygon]
    back = [(x, 10.0, z) for x, z in polygon]
    triangles = [(front[c], front[b], front[a]) for a, b, c in caps]
    triangles += [(back[a], back[b], back[c]) for a, b, c in caps]
    for index in range(len(polygon)):
        following = (index + 1) % len(polygon)
        triangles.extend([
            (front[index], front[following], back[following]),
            (front[index], back[following], back[index]),
        ])
    return triangles


def _slope_triangles():
    vertices = [
        (0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0),
        (20, 0, 20), (30, 0, 20), (30, 10, 20), (20, 10, 20),
    ]
    faces = [
        (0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
        (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
        (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7),
    ]
    return [(vertices[a], vertices[b], vertices[c]) for a, b, c in faces]


def calibrate(materials, settings_by_material, work_dir, logs_dir):
    calibration_dir = Path(work_dir) / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    gamma = calibration_dir / "calibration-gamma.stl"
    slope = calibration_dir / "calibration-slope-45.stl"
    write_binary_stl(str(gamma), _gamma_triangles())
    write_binary_stl(str(slope), _slope_triangles())
    layout = calibration_dir / "calibration-layout.3mf"
    placement = create_layout(layout, [gamma, slope])
    report = {"ok": True, "placement": placement, "materials": {}}
    expected = [gamma.stem, slope.stem]
    for material in materials:
        sliced = calibration_dir / f"calibration-{material}.gcode.3mf"
        inspection, log = slice_plate(
            layout, sliced, material, settings_by_material[material], work_dir, logs_dir,
            f"calibration-{material}",
        )
        objects, assignment = normalize_object_results(sliced, inspection, expected)
        gamma_mm = _external_unsupported_mm(objects, gamma.stem, 0.0)
        slope_mm = _external_unsupported_mm(objects, slope.stem, 99.0)
        ok = gamma_mm > 20.0 and slope_mm < 1.0 and not assignment["missing"]
        report["materials"][material] = {
            "ok": ok,
            "gamma_external_unsupported_mm": round(gamma_mm, 2),
            "slope_45_external_unsupported_mm": round(slope_mm, 2),
            "objects": objects,
            "assignment": assignment,
            "slice": file_record(sliced),
            "log": file_record(log),
        }
        report["ok"] = report["ok"] and ok
    if not report["ok"]:
        raise RuntimeError(f"G-code unsupported-perimeter calibration failed: {report['materials']}")
    return report


def _plate_result(kind, material, layout, sliced, placement, inspection, expected):
    sliced_placement = inspect_layout(sliced, expected)
    if not sliced_placement["ok"]:
        raise RuntimeError(f"Bambu Studio changed {kind} placement: {sliced_placement['issues']}")
    objects, assignment = normalize_object_results(sliced, inspection, expected)
    findings = unsupported_findings(objects)
    return {
        "material": material,
        "file": file_record(sliced),
        "prediction_s": inspection["prediction_s"],
        "weight_g": float(inspection["weight_g"]),
        "filament": inspection["filament"],
        "support_used": inspection["support_used"],
        "objects": objects,
        "object_assignment": assignment,
        "visible_unsupported": findings,
        "status": "review_required" if (
            findings or assignment["missing"] or assignment["unassigned"]
        ) else "ok",
        "placement": sliced_placement,
        "source_layout_sha256": sha256_file(layout),
        "layout_preserved": placement["ok"] and sliced_placement["ok"],
    }


def register_studio_plate(model_id, layout, delivered_stls):
    """Studio の鮮度検査に必要な source STL を exports に置いて登録する。"""
    source_files = []
    for delivered in delivered_stls:
        delivered = Path(delivered)
        if not delivered.name.startswith(model_id + "-") or delivered.suffix != ".stl":
            raise ValueError(f"unsafe Studio source STL name: {delivered.name!r}")
        destination = EXPORTS / delivered.name
        if destination.resolve().parent != EXPORTS.resolve():
            raise ValueError(f"Studio source STL escapes exports: {destination}")
        if not destination.exists() or sha256_file(destination) != sha256_file(delivered):
            _atomic_copy(delivered, destination)
        source_files.append(file_record(destination))
    manifest = export_studio_plate(model_id, str(layout), bed=BED[:2])
    manifest_path = ROOT / "viewer" / "studio" / "plates" / f"{model_id}.json"
    return {
        "id": manifest["id"],
        "parts": len(manifest["parts"]),
        "manifest": file_record(manifest_path),
        "source_files": source_files,
    }


def run(model_id, material_option):
    materials = ["PLA", "PETG"] if material_option == "both" else [material_option]
    model_dir, manifest_path, parts = load_manifest(model_id)
    output_dir = PRINTS / model_id
    build_dir = model_dir / "build"
    work_dir = build_dir / "delivery"
    logs_dir = work_dir / "logs"
    output_dir.mkdir(parents=True, exist_ok=True)
    printable = [part for part in parts if part["print"] is not None]
    full_parts = [part for part in printable if not part["fit_only"]]
    fit_parts = [part for part in printable if part["fit_test"]]
    if not full_parts:
        raise ValueError("manifest has no printable parts for the full plate")
    part_report = []
    by_stem = {}
    artifacts = []
    for part in parts:
        result = {
            "id": part["id"],
            "label": part["label"],
            "fit_test": part["fit_test"],
            "fit_only": part["fit_only"],
            "assembly": file_record(part["assembly"]),
            "status": "reference" if part["print"] is None else "printable",
            "slices": {},
        }
        if part["print"] is not None:
            destination = output_dir / f"{model_id}-print-{part['id']}.stl"
            _atomic_copy(part["print"], destination)
            result["source_print"] = file_record(part["print"])
            result["delivered_print"] = file_record(destination)
            by_stem[destination.stem] = result
            artifacts.append(file_record(destination))
        part_report.append(result)

    settings_by_material = {
        material: write_settings(work_dir / "settings", material) for material in materials
    }
    calibration = calibrate(materials, settings_by_material, work_dir, logs_dir)

    full_stls = [output_dir / f"{model_id}-print-{part['id']}.stl" for part in full_parts]
    full_layout = output_dir / f"{model_id}-layout.3mf"
    full_placement = create_layout(full_layout, full_stls)
    exportable_3mfs = [full_layout]
    artifacts.append(file_record(full_layout))
    plates = {
        "full": {
            "layout": file_record(full_layout),
            "placement": full_placement,
            "materials": {},
        }
    }
    expected_full = [path.stem for path in full_stls]
    for material in materials:
        destination = output_dir / f"{model_id}-{material}.gcode.3mf"
        inspection, log = slice_plate(
            full_layout, destination, material, settings_by_material[material],
            work_dir, logs_dir, f"full-{material}",
        )
        result = _plate_result(
            "full", material, full_layout, destination, full_placement, inspection, expected_full
        )
        result["log"] = file_record(log)
        plates["full"]["materials"][material] = result
        exportable_3mfs.append(destination)
        artifacts.append(file_record(destination))
        for stem, object_result in result["objects"].items():
            if stem in by_stem:
                by_stem[stem]["slices"][material] = object_result

    if fit_parts:
        fit_stls = [output_dir / f"{model_id}-print-{part['id']}.stl" for part in fit_parts]
        fit_layout = output_dir / f"{model_id}-fit-test-layout.3mf"
        fit_placement = create_layout(fit_layout, fit_stls)
        exportable_3mfs.append(fit_layout)
        artifacts.append(file_record(fit_layout))
        plates["fit_test"] = {
            "parts": [part["id"] for part in fit_parts],
            "layout": file_record(fit_layout),
            "placement": fit_placement,
            "materials": {},
        }
        expected_fit = [path.stem for path in fit_stls]
        for material in materials:
            destination = output_dir / f"{model_id}-fit-test-{material}.gcode.3mf"
            inspection, log = slice_plate(
                fit_layout, destination, material, settings_by_material[material],
                work_dir, logs_dir, f"fit-test-{material}",
            )
            result = _plate_result(
                "fit_test", material, fit_layout, destination, fit_placement,
                inspection, expected_fit,
            )
            result["log"] = file_record(log)
            plates["fit_test"]["materials"][material] = result
            exportable_3mfs.append(destination)
            artifacts.append(file_record(destination))
            for stem, object_result in result["objects"].items():
                if stem in by_stem:
                    by_stem[stem].setdefault("fit_test_slices", {})[material] = object_result

    for source in exportable_3mfs:
        if not source.name.startswith(model_id + "-") or source.suffix != ".3mf":
            raise ValueError(f"unsafe exported delivery artifact: {source.name!r}")
        destination = EXPORTS / source.name
        if destination.resolve().parent != EXPORTS.resolve():
            raise ValueError(f"delivery artifact escapes exports: {destination}")
        _atomic_copy(source, destination)
        artifacts.append(file_record(destination))

    studio = register_studio_plate(model_id, full_layout, full_stls)
    visible_unsupported = [
        {"plate": plate_name, "material": material, **finding}
        for plate_name, plate in plates.items()
        for material, result in plate["materials"].items()
        for finding in result["visible_unsupported"]
    ]
    for part in part_report:
        if part["status"] == "reference":
            part["delivery_status"] = "not_applicable"
            continue
        verification_key = "fit_test_slices" if part["fit_only"] else "slices"
        verification = part.get(verification_key, {})
        part["verification_source"] = verification_key
        if set(verification) != set(materials):
            part["delivery_status"] = "unverified"
        elif any(
            float(result.get("floating", {}).get("external_unsupported_mm", 0.0) or 0.0) > 0.01
            for result in verification.values()
        ):
            part["delivery_status"] = "review_required"
        else:
            part["delivery_status"] = "ok"
    review_required = bool(visible_unsupported) or any(
        result["status"] != "ok"
        for plate in plates.values()
        for result in plate["materials"].values()
    )
    report = {
        "version": 1,
        "model": model_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "manifest": file_record(manifest_path),
        "materials": materials,
        "settings": {
            "machine": MACHINE,
            "process": PROCESS,
            "filament": {material: FILAMENTS[material] for material in materials},
            "overrides": OVERRIDES,
            "resolved_files": {
                material: {kind: file_record(path) for kind, path in settings.items()}
                for material, settings in settings_by_material.items()
            },
        },
        "calibration": calibration,
        "parts": part_report,
        "plates": plates,
        "visible_unsupported": visible_unsupported,
        "status": "review_required" if review_required else "ok",
        "studio": studio,
        "artifacts": artifacts,
    }
    report_path = build_dir / "delivery_report.json"
    _atomic_json(report_path, report)
    return report_path, report


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="manifest から印刷 STL とスライス済み 3MF を作り、配置と G-code を検査する。"
    )
    parser.add_argument("model_id", metavar="model-id")
    parser.add_argument(
        "--material", choices=("PLA", "PETG", "both"), default="both",
        help="作る材料。既定は both。",
    )
    return parser.parse_args(argv)


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args(argv)
    report_path, report = run(args.model_id, args.material)
    print(f"[delivery] report: {report_path}")
    for plate_name, plate in report["plates"].items():
        for material, result in plate["materials"].items():
            print(
                f"[delivery] {plate_name}/{material}: {result['prediction_s'] / 60:.1f} min / "
                f"{result['weight_g']:.2f} g / support={result['support_used']} / "
                f"unsupported={len(result['visible_unsupported'])}"
            )
            for finding in result["visible_unsupported"]:
                print(
                    f"[delivery] WARNING {finding['object']}: visible unsupported "
                    f"{finding['external_unsupported_mm']:.2f} mm; "
                    f"layers={finding['worst_layers']}"
                )
    print(f"[delivery] status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
