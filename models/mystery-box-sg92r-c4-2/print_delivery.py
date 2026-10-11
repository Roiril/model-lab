"""C4-2 を複数プレートへ分け、PLA/PETG の実 G-code 3MF を生成する。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
import uuid
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEMP_ROOT = Path(r"D:\Projects\model-lab-c4-2-temp")
TEMP_ROOT.mkdir(parents=True, exist_ok=True)
os.environ["TEMP"] = str(TEMP_ROOT)
os.environ["TMP"] = str(TEMP_ROOT)
sys.path.insert(0, str(ROOT / "tools"))

import lattice_delivery as delivery  # noqa: E402

MODEL = "mystery-box-sg92r-c4-2"
PRIMARY_IDS = ("housing", "bottom")
PRINT_OVERRIDES = {
    **delivery.OVERRIDES,
    "bottom_shell_thickness": str(delivery.BED[2]),
    "brim_object_gap": "0.1",
    "brim_type": "outer_and_inner",
    "brim_width": "5",
    "top_shell_thickness": str(delivery.BED[2]),
}
DELIVERY_TEMP_EXPORTS = TEMP_ROOT / "delivery-layout-temp"
DELIVERY_TEMP_EXPORTS.mkdir(parents=True, exist_ok=True)
delivery.EXPORTS = DELIVERY_TEMP_EXPORTS


def temporary_layout(destination: Path, stls: list[Path]) -> dict:
    parts = []
    for path in stls:
        vertices, faces = delivery.plate_3mf.read_stl(str(path))
        if not vertices or not faces:
            raise ValueError(f"empty STL: {path}")
        parts.append((Path(path).stem, vertices, faces))
    plate = delivery.plate_3mf
    placed, total = plate.arrange(parts, plate.BED_X - 2 * plate.MARGIN)
    placed = plate.center_on_bed(placed, total)
    temporary = DELIVERY_TEMP_EXPORTS / (
        f".{Path(destination).stem}.{os.getpid()}.{uuid.uuid4().hex}.3mf")
    try:
        plate.write_3mf(str(temporary), placed)
        placement = delivery.inspect_layout(temporary, [part[0] for part in parts])
        if not placement["ok"]:
            raise RuntimeError(f"invalid calibration layout: {placement['issues']}")
        delivery._atomic_copy(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return placement


delivery.create_layout = temporary_layout


def write_settings(work_dir: Path, material: str) -> dict[str, Path]:
    material_dir = Path(work_dir) / material
    machine = delivery.resolve("machine", delivery.MACHINE)
    process = delivery.resolve("process", delivery.PROCESS)
    process.update(PRINT_OVERRIDES)
    filament = delivery.resolve("filament", delivery.FILAMENTS[material])
    return {
        "machine": Path(delivery.write_flat(str(material_dir / "machine.json"), machine)),
        "process": Path(delivery.write_flat(str(material_dir / "process.json"), process)),
        "filament": Path(delivery.write_flat(str(material_dir / "filament.json"), filament)),
    }


def file_record(path: Path) -> dict:
    path = Path(path)
    try:
        name = path.relative_to(ROOT).as_posix()
    except ValueError:
        name = str(path)
    return {"file": name, "bytes": path.stat().st_size,
            "sha256": delivery.sha256_file(path)}


def solid_fill_evidence(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        settings = json.loads(archive.read("Metadata/project_settings.config"))
        gcode_names = [name for name in archive.namelist() if name.endswith(".gcode")]
        if len(gcode_names) != 1:
            raise ValueError(f"expected one G-code in {path}, found {gcode_names}")
        gcode = archive.read(gcode_names[0])
    features = {}
    for raw_name in re.findall(rb"^;\s*(?:FEATURE|TYPE):\s*([^\r\n]+)",
                               gcode, re.MULTILINE):
        name = raw_name.decode("utf-8", "replace").strip()
        features[name] = features.get(name, 0) + 1
    actual = {
        key: settings.get(key)
        for key in ("bottom_shell_layers", "bottom_shell_thickness",
                    "top_shell_layers", "top_shell_thickness",
                    "sparse_infill_density", "sparse_infill_pattern")
    }
    pass_evidence = (
        float(actual["bottom_shell_thickness"]) >= delivery.BED[2]
        and float(actual["top_shell_thickness"]) >= delivery.BED[2]
        and features.get("Sparse infill", 0) == 0
        and features.get("Internal solid infill", 0) > 0
    )
    return {
        "source": file_record(path),
        "strategy": "top_bottom_shell_thickness_covers_build_height",
        "actualSettings": actual,
        "featurePathCounts": features,
        "sparseInfillPathCount": features.get("Sparse infill", 0),
        "internalSolidInfillPathCount": features.get("Internal solid infill", 0),
        "pass": pass_evidence,
    }


def model_path(model_dir: Path, value: object, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty path")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"{field} escapes the model directory: {value!r}")
    path = model_dir / relative
    if not path.is_file():
        raise FileNotFoundError(f"{field} does not exist: {path}")
    return path


def load_manifest() -> tuple[Path, Path, list[dict]]:
    model_dir = ROOT / "models" / MODEL
    manifest_path = model_dir / "build" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_parts = manifest.get("parts")
    if not isinstance(source_parts, list) or not source_parts:
        raise ValueError("manifest parts must be a non-empty list")
    parts = []
    seen = set()
    for index, raw in enumerate(source_parts):
        if not isinstance(raw, dict):
            raise ValueError(f"parts[{index}] must be an object")
        part_id = raw.get("id")
        if not isinstance(part_id, str) or not delivery.SAFE_ID.fullmatch(part_id):
            raise ValueError(f"parts[{index}].id is unsafe: {part_id!r}")
        if part_id in seen:
            raise ValueError(f"duplicate part id: {part_id}")
        seen.add(part_id)
        label = raw.get("label")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"part {part_id}: label must be a non-empty string")
        assembly = model_path(model_dir, raw.get("assembly"), f"part {part_id} assembly")
        print_value = raw.get("print")
        print_path = None if print_value is None else model_path(
            model_dir, print_value, f"part {part_id} print")
        fit_test = raw.get("fit_test", False)
        fit_only = raw.get("fit_only", False)
        if not isinstance(fit_test, bool) or not isinstance(fit_only, bool):
            raise ValueError(f"part {part_id}: fit_test and fit_only must be boolean")
        if fit_test and print_path is None:
            raise ValueError(f"part {part_id}: a reference part cannot be a fit test")
        if fit_only and (not fit_test or print_path is None):
            raise ValueError(f"part {part_id}: fit_only requires a printable fit test")
        parts.append({"id": part_id, "label": label, "assembly": assembly,
                      "print": print_path, "fit_test": fit_test, "fit_only": fit_only})
    if not any(part["print"] for part in parts):
        raise ValueError("manifest has no printable parts")
    return model_dir, manifest_path, parts


def footprint_area(path: Path) -> float:
    vertices, _faces = delivery.plate_3mf.read_stl(str(path))
    xs = [point[0] for point in vertices]
    ys = [point[1] for point in vertices]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def split_balanced(parts: list[dict]) -> tuple[list[dict], list[dict]]:
    bins: list[list[dict]] = [[], []]
    areas = [0.0, 0.0]
    for part in sorted(parts, key=lambda row: footprint_area(row["delivered"]), reverse=True):
        index = 0 if areas[0] <= areas[1] else 1
        bins[index].append(part)
        areas[index] += footprint_area(part["delivered"])
    if not all(bins):
        raise RuntimeError("full_2 を2枚へ分けられません")
    return bins[0], bins[1]


def layout_name(output_dir: Path, plate_id: str) -> Path:
    suffix = {"full": "layout", "full_2": "layout-2", "full_3": "layout-3",
              "fit_test": "fit-test-layout"}[plate_id]
    return output_dir / f"{MODEL}-{suffix}.3mf"


def gcode_name(output_dir: Path, plate_id: str, material: str) -> Path:
    suffix = {"full": material, "full_2": f"full-2-{material}",
              "full_3": f"full-3-{material}",
              "fit_test": f"fit-test-{material}"}[plate_id]
    return output_dir / f"{MODEL}-{suffix}.gcode.3mf"


def make_layout(output_dir: Path, plate_id: str, parts: list[dict]) -> tuple[Path, dict]:
    path = layout_name(output_dir, plate_id)
    source_parts = []
    for part in parts:
        vertices, faces = delivery.plate_3mf.read_stl(str(part["delivered"]))
        if not vertices or not faces:
            raise ValueError(f"empty STL: {part['delivered']}")
        source_parts.append((part["delivered"].stem, vertices, faces))
    plate = delivery.plate_3mf
    placed, total = plate.arrange(source_parts, plate.BED_X - 2 * plate.MARGIN)
    placed = plate.center_on_bed(placed, total)

    def intruders(rows):
        return [index for index, (_name, vertices, _faces, dx, dy) in enumerate(rows)
                if any(x + dx < plate.EXCLUDE[0] and y + dy < plate.EXCLUDE[1]
                       for x, y, _z in vertices)]

    for placed_index in intruders(placed):
        target_name = placed[placed_index][0]
        index = next(i for i, row in enumerate(source_parts) if row[0] == target_name)
        name, original, faces = source_parts[index]
        for degree in (90, 180, 270):
            cosine, sine = math.cos(math.radians(degree)), math.sin(math.radians(degree))
            rotated = [(x * cosine - y * sine, x * sine + y * cosine, z)
                       for x, y, z in original]
            trial = source_parts[:index] + [(name, rotated, faces)] + source_parts[index + 1:]
            candidate, candidate_total = plate.arrange(trial, plate.BED_X - 2 * plate.MARGIN)
            candidate = plate.center_on_bed(candidate, candidate_total)
            candidate_intruders = {candidate[i][0] for i in intruders(candidate)}
            if target_name not in candidate_intruders:
                source_parts, placed, total = trial, candidate, candidate_total
                break
    temporary = TEMP_ROOT / f"layout-{plate_id}-{os.getpid()}-{uuid.uuid4().hex}.3mf"
    try:
        plate.write_3mf(str(temporary), placed)
        expected = [part["delivered"].stem for part in parts]
        placement = delivery.inspect_layout(temporary, expected)
        if not placement["ok"]:
            raise RuntimeError(f"invalid plate layout {plate_id}: {placement['issues']}")
        delivery._atomic_copy(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return path, placement


def create_full_layouts(output_dir: Path, full_parts: list[dict]) -> list[tuple[str, list[dict], Path, dict]]:
    primary = [part for part in full_parts if part["id"] in PRIMARY_IDS]
    remainder = [part for part in full_parts if part["id"] not in PRIMARY_IDS]
    if {part["id"] for part in primary} != set(PRIMARY_IDS):
        raise ValueError("full plate requires housing and bottom")
    layouts = [("full", primary, *make_layout(output_dir, "full", primary))]
    try:
        layouts.append(("full_2", remainder, *make_layout(output_dir, "full_2", remainder)))
    except RuntimeError:
        left, right = split_balanced(remainder)
        layouts.append(("full_2", left, *make_layout(output_dir, "full_2", left)))
        layouts.append(("full_3", right, *make_layout(output_dir, "full_3", right)))
    return layouts


def run(material_option: str = "both", layout_only: bool = False) -> tuple[Path, dict]:
    materials = ["PLA", "PETG"] if material_option == "both" else [material_option]
    model_dir, manifest_path, parts = load_manifest()
    output_dir = delivery.PRINTS / MODEL
    build_dir = model_dir / "build"
    work_dir = TEMP_ROOT / "delivery"
    logs_dir = work_dir / "logs"
    output_dir.mkdir(parents=True, exist_ok=True)

    part_report = []
    printable = []
    by_stem = {}
    artifacts = []
    for part in parts:
        row = {"id": part["id"], "label": part["label"],
               "fit_test": part["fit_test"], "fit_only": part["fit_only"],
               "assembly": file_record(part["assembly"]),
               "status": "reference" if part["print"] is None else "printable", "slices": {}}
        if part["print"] is not None:
            delivered = output_dir / f"{MODEL}-print-{part['id']}.stl"
            delivery._atomic_copy(part["print"], delivered)
            row["source_print"] = file_record(part["print"])
            row["delivered_print"] = file_record(delivered)
            part_with_delivery = {**part, "delivered": delivered}
            printable.append(part_with_delivery)
            by_stem[delivered.stem] = row
            artifacts.append(file_record(delivered))
        part_report.append(row)

    full_parts = [part for part in printable if not part["fit_only"]]
    fit_parts = [part for part in printable if part["fit_test"]]
    if not fit_parts:
        raise ValueError("manifest has no printable fit-test parts")
    settings_by_material = ({
        material: write_settings(build_dir / "print_settings", material)
        for material in materials
    } if not layout_only else {})
    calibration = (delivery.calibrate(materials, settings_by_material, work_dir, logs_dir)
                   if not layout_only else {
                       "status": "not_run", "pass": None,
                       "reason": "layout_only_user_slices",
                   })
    layouts = create_full_layouts(output_dir, full_parts)
    fit_layout, fit_placement = make_layout(output_dir, "fit_test", fit_parts)
    layouts.append(("fit_test", fit_parts, fit_layout, fit_placement))

    plates = {}
    for plate_id, plate_parts, layout, placement in layouts:
        plate = {"parts": [part["id"] for part in plate_parts],
                 "layout": file_record(layout), "placement": placement, "materials": {}}
        plates[plate_id] = plate
        artifacts.append(file_record(layout))
        expected = [part["delivered"].stem for part in plate_parts]
        for material in (() if layout_only else materials):
            destination = gcode_name(output_dir, plate_id, material)
            inspection, _log = delivery.slice_plate(
                layout, destination, material, settings_by_material[material],
                work_dir, logs_dir, f"{plate_id}-{material}")
            result = delivery._plate_result(
                plate_id, material, layout, destination, placement, inspection, expected)
            result["file"] = file_record(destination)
            result["solid_fill_evidence"] = solid_fill_evidence(destination)
            if not result["solid_fill_evidence"]["pass"]:
                raise RuntimeError(
                    f"solid fill settings were not applied to {plate_id}/{material}"
                )
            plate["materials"][material] = result
            artifacts.append(file_record(destination))
            slice_key = "fit_test_slices" if plate_id == "fit_test" else "slices"
            for stem, object_result in result["objects"].items():
                by_stem[stem].setdefault(slice_key, {})[material] = object_result

    visible_unsupported = [
        {"plate": plate_id, "material": material, **finding}
        for plate_id, plate in plates.items()
        for material, result in plate["materials"].items()
        for finding in result["visible_unsupported"]
    ]
    for row in part_report:
        if row["status"] == "reference":
            row["delivery_status"] = "not_applicable"
            continue
        if layout_only:
            row["delivery_status"] = "user_slices"
            row["verification_source"] = "user_slices"
            continue
        verification_key = "fit_test_slices" if row["fit_only"] else "slices"
        verification = row.get(verification_key, {})
        row["verification_source"] = verification_key
        if set(verification) != set(materials):
            row["delivery_status"] = "unverified"
        elif any(float(result.get("floating", {}).get("external_unsupported_mm", 0.0) or 0.0) > 0.01
                 for result in verification.values()):
            row["delivery_status"] = "review_required"
        else:
            row["delivery_status"] = "ok"
    review_required = not layout_only and (bool(visible_unsupported) or any(
        result["status"] != "ok" for plate in plates.values()
        for result in plate["materials"].values()))
    report = {
        "version": 1, "model": MODEL, "created_at": datetime.now(timezone.utc).isoformat(),
        "manifest": file_record(manifest_path), "materials": materials,
        "settings": {"machine": delivery.MACHINE, "process": delivery.PROCESS,
                     "filament": {material: delivery.FILAMENTS[material] for material in materials},
                     "overrides": PRINT_OVERRIDES,
                     "solid_fill": {
                         "strategy": "top_bottom_shell_thickness_covers_build_height",
                         "build_height_mm": delivery.BED[2],
                         "bottom_shell_thickness_mm": delivery.BED[2],
                         "top_shell_thickness_mm": delivery.BED[2],
                         "actual_values_recorded_per_plate": not layout_only,
                     },
                     "resolved_files": {material: {kind: file_record(path)
                                                    for kind, path in settings.items()}
                                        for material, settings in settings_by_material.items()}},
        "calibration": calibration, "parts": part_report, "plates": plates,
        "visible_unsupported": visible_unsupported,
        "deliveryMode": "layout_only" if layout_only else "sliced",
        "slicing": {"status": "user_slices" if layout_only else "generated",
                    "performed": not layout_only,
                    "requestedMaterials": materials},
        "status": "layout_only" if layout_only else (
            "review_required" if review_required else "ok"),
        "studio": {"status": "served_from_prints",
                   "reason": ("編集可能な配置3MFと部品STLを /prints/ から配布する。"
                              if layout_only else
                              "複数の実印刷プレートを /prints/ から配布する。")},
        "sourceAlgorithms": {
            "models/mystery-box-sg92r-c4-2/print_delivery.py":
                delivery.sha256_file(Path(__file__)),
            "tools/lattice_delivery.py":
                delivery.sha256_file(ROOT / "tools/lattice_delivery.py"),
            "tools/plate_3mf.py": delivery.sha256_file(ROOT / "tools/plate_3mf.py"),
        },
        "artifacts": artifacts,
    }
    report_path = build_dir / "delivery_report.json"
    delivery._atomic_json(report_path, report)
    return report_path, report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--material", choices=("PLA", "PETG", "both"), default="both")
    parser.add_argument("--layout-only", action="store_true", default=True,
                        help="部品STLと編集可能な配置3MFだけを生成し、スライスしない（既定）")
    args = parser.parse_args(argv)
    report_path, report = run(args.material, layout_only=args.layout_only)
    print(f"[delivery] report: {report_path}")
    for plate_id, plate in report["plates"].items():
        for material, result in plate["materials"].items():
            print(f"[delivery] {plate_id}/{material}: {result['prediction_s'] / 60:.1f} min / "
                  f"{result['weight_g']:.2f} g / support={result['support_used']} / "
                  f"unsupported={len(result['visible_unsupported'])}")
    print(f"[delivery] status: {report['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
