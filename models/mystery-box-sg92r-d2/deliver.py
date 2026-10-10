"""検証済みの STL と 3mf を prints/<model>/ に集める。"""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
EXPORTS = ROOT / "exports"
DEST = ROOT / "prints" / HERE.name
PARTS = ("box", "lid", "roof", "crank", "link", "pin", "clip", "speaker_clip")
COUPONS = ("joint_b_test", "speaker_test")
OUTPUTS = ("PLA", "PETG", "crank-test-PLA", "joints-test-PLA", "speaker-test-PLA", "plate")
NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
IDENTITY = (1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)


def transform(points, attribute):
    matrix = tuple(map(float, attribute.split())) if attribute else IDENTITY
    return [(x * matrix[0] + y * matrix[3] + z * matrix[6] + matrix[9],
             x * matrix[1] + y * matrix[4] + z * matrix[7] + matrix[10],
             x * matrix[2] + y * matrix[5] + z * matrix[8] + matrix[11]) for x, y, z in points]


def placed_bounds(path):
    with zipfile.ZipFile(path) as archive:
        documents = {name: ET.fromstring(archive.read(name)) for name in archive.namelist()
                     if name.endswith(".model")}

        def vertices(document, object_id):
            obj = next(item for item in documents[document].iter(NS + "object") if item.get("id") == object_id)
            mesh = obj.find(NS + "mesh")
            if mesh is not None:
                return [tuple(float(vertex.get(axis)) for axis in ("x", "y", "z"))
                        for vertex in mesh.find(NS + "vertices")]
            result = []
            for component in obj.find(NS + "components"):
                child = next((value.lstrip("/") for key, value in component.attrib.items()
                              if key.split("}")[-1] == "path"), document)
                result.extend(transform(vertices(child, component.get("objectid")), component.get("transform")))
            return result

        main = documents["3D/3dmodel.model"]
        rows = []
        for item in main.find(NS + "build"):
            points = transform(vertices("3D/3dmodel.model", item.get("objectid")), item.get("transform"))
            lower = [min(point[axis] for point in points) for axis in range(3)]
            upper = [max(point[axis] for point in points) for axis in range(3)]
            rows.append({
                "id": item.get("objectid"),
                "min": lower,
                "max": upper,
                "off_bed": lower[0] < 0 or lower[1] < 0 or upper[0] > 256 or upper[1] > 256
                or lower[2] < -0.001 or upper[2] > 250,
                "excluded": any(point[0] < 18 and point[1] < 28 for point in points),
            })
        overlaps = []
        for index, first in enumerate(rows):
            for second in rows[index + 1:]:
                if all(min(first["max"][axis], second["max"][axis])
                       - max(first["min"][axis], second["min"][axis]) > 0.001 for axis in (0, 1)):
                    overlaps.append([first["id"], second["id"]])
        return {"objects": rows, "bbox_overlaps": overlaps,
                "ok": not overlaps and not any(row["off_bed"] or row["excluded"] for row in rows)}


def read_report(name):
    return json.loads((BUILD / name).read_text(encoding="utf-8"))


def copy_file(source, destination, files):
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    files.append(destination)


def main():
    model = read_report("model_report.json")
    sliced = read_report("slice_report.json")
    plates = read_report("plate_report.json")
    if not sliced["calibration"]["ok"] or any("error" in value for value in sliced["parts"].values()):
        raise RuntimeError("slice_check did not pass")
    model_parts = model.get("parts", {})
    if model_parts and not set(PARTS).issubset(model_parts):
        raise RuntimeError(f"model_report lacks print parts: {sorted(set(PARTS) - set(model_parts))}")
    support_required = bool(sliced["support_recommendation"]["required"])
    for material in ("PLA", "PETG"):
        support_used = str(plates[material]["support_used"]).lower() == "true"
        if support_used != support_required:
            raise RuntimeError(f"{material}: support_used={support_used}, required={support_required}")
    if any(str(plates[key]["support_used"]).lower() != "false"
           for key in ("crank_test", "joints_test", "speaker_test")):
        raise RuntimeError("a test plate unexpectedly uses support")

    DEST.mkdir(parents=True, exist_ok=True)
    files = []
    for part in PARTS:
        copy_file(BUILD / f"print_{part}.stl", DEST / f"{part}.stl", files)
        copy_file(BUILD / f"{part}.stl", DEST / "assembly" / f"{part}.stl", files)
    for coupon in COUPONS:
        copy_file(BUILD / f"print_{coupon}.stl", DEST / f"{coupon}.stl", files)

    placements = {}
    for key in OUTPUTS:
        suffix = ".3mf" if key == "plate" else ".gcode.3mf"
        source = EXPORTS / f"{HERE.name}-{key}{suffix}"
        destination = DEST / source.name
        copy_file(source, destination, files)
        placements[key] = placed_bounds(destination)
        if not placements[key]["ok"]:
            raise RuntimeError(f"invalid placement in {key}: {placements[key]}")
    if len(placements["PLA"]["objects"]) != len(PARTS) or len(placements["PETG"]["objects"]) != len(PARTS):
        raise RuntimeError("full plate does not contain eight parts")

    manifest = {
        "model": HERE.name,
        "parts": len(PARTS),
        "support": {
            "required": support_required,
            "allowed_surface": sliced["support_recommendation"]["allowed_surface"],
            "PLA_used": plates["PLA"]["support_used"],
            "PETG_used": plates["PETG"]["support_used"],
        },
        "slicing": {material: {"prediction_s": plates[material]["prediction_s"],
                               "weight_g": plates[material]["weight_g"],
                               "filament": plates[material]["filament"],
                               "support_region": plates[material]["support_region"]}
                    for material in ("PLA", "PETG")},
        "accepted_short_unsupported": plates["settings"]["accepted_short_unsupported"],
        "floating_meter_limit": plates["settings"]["floating_meter_limit"],
        "placements": placements,
        "files": [{"name": str(path.relative_to(DEST)).replace("\\", "/"),
                   "bytes": path.stat().st_size,
                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files],
    }
    temporary = DEST / "manifest.tmp"
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    temporary.replace(DEST / "manifest.json")
    (BUILD / "delivery_report.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1),
                                                encoding="utf-8", newline="\n")
    print(json.dumps({"parts": len(PARTS), "files": len(files), "support": manifest["support"],
                      "placements": {key: value["ok"] for key, value in placements.items()}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
