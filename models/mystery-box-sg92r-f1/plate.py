"""Place the manifest's print meshes on four X1C plates and slice without support."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL = HERE.name
OUT = ROOT / "prints" / MODEL
BUILD = HERE / "build"
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "tools"))
from bambu_profiles import resolve, write_flat
import plate_3mf as P
from printmech.three_mf import inspect_sliced_3mf
from printmech.gcode import parse_gcode
from mechgate_lib import limits as L

NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
EXE = Path("C:/Program Files/Bambu Studio/bambu-studio.exe")
PLATES = {
    "01-frame": ("frame/", "back/", "left/"),
    "02-front": ("front/", "bottom/"),
    "03-top": ("top/",),
    "04-right": ("right/",),
}
IDENTITY = (1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    read(temporary)
    os.replace(temporary, path)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def part_mesh(name, path, flip_x=False):
    verts, faces = P.read_stl(path)
    if not verts or not faces:
        raise ValueError(f"{name}: empty print STL: {path}")
    if flip_x:
        verts = [(x, -y, -z) for x, y, z in verts]
    z0 = P.bbox(verts)[0][2]
    verts = [(x, y, z - z0) for x, y, z in verts]
    return name.replace("/", "__"), verts, faces


def production_groups():
    manifest = read(BUILD / "manifest.json")
    slots = read(HERE / "slots.json")["slots"]
    if slots["right"]["module"] != "sector_flag":
        raise ValueError("right/sector_flag must be composed before production plates")
    groups = {name: [] for name in PLATES}
    sources = {}
    for part in manifest["parts"]:
        if "print" not in part:
            continue
        pid = part["id"]
        group = next((name for name, prefixes in PLATES.items() if pid.startswith(prefixes)), None)
        if pid in ("frame/wiring", "frame/tray"):
            group = "02-front"
        if pid.startswith("frame/carrier_"):
            group = {"front": "02-front", "right": "03-top", "back": "03-top",
                     "left": "02-front"}[pid.removeprefix("frame/carrier_")]
        if group is None or pid in sources:
            raise ValueError(f"unassigned or duplicate print part: {pid}")
        path = (HERE / part["print"]).resolve()
        sources[pid] = {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}
        groups[group].append(part_mesh(pid, path))
    if any(not parts for parts in groups.values()):
        raise ValueError("each of the four production plates must contain print parts")
    return groups, sources


def trial_files():
    # These are cut-downs of production geometry. Lower cam and servo seat use
    # the same X half-turn as their manifest print meshes.
    return [
        ("frame_corner", "trial/frame_corner.stl", False),
        ("mount_panel", "trial/back/mount_panel.stl", False),
        ("mount_key", "trial/back/mount_key_l.stl", True),
        ("servo_seat", "trial/top/servo_fit.stl", True),
        ("servo_cap", "trial/top/servo_cap_fit.stl", False),
        ("horn_fit", "trial/top/horn_fit.stl", False),
        ("connector_nest", "trial/top/connector_nest.stl", False),
        ("cam_lower", "trial/top/lower_cam_fit.stl", True),
        ("cam_upper", "trial/top/upper_cam_fit.stl", False),
        ("pixel", "trial/top/pixel_fit.stl", False),
        ("guide", "trial/top/guide_fit.stl", False),
        ("cam_key", "top/cam_key_1.stl", False),
    ]


def trial_parts():
    return [part_mesh("trial/" + name, OUT / path, flip) for name, path, flip in trial_files()]


def check_boxes(boxes):
    for row in boxes:
        lo, hi = row["min_mm"], row["max_mm"]
        if any(lo[i] < -0.001 or hi[i] > size + 0.001 for i, size in enumerate((256, 256, 250))):
            raise ValueError(f"outside X1C bed: {row}")
        if lo[0] < 18 and lo[1] < 28:
            raise ValueError(f"intersects 18 x 28 mm exclusion: {row}")
        if abs(lo[2]) > 0.002:
            raise ValueError(f"not on print bed: {row}")
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if all(min(a["max_mm"][j], b["max_mm"][j]) - max(a["min_mm"][j], b["min_mm"][j]) > 0.001
                   for j in (0, 1)):
                raise ValueError(f"overlapping XY boxes: {a['name']} / {b['name']}")


def arrange(parts):
    # The reserved left strip clears the exclusion. In-plane quarter-turns keep
    # the manifest's contact face and layer direction while fitting narrow posts.
    free = [(20., 6., 236., 250.)]
    sized = []
    for name, vertices, faces in parts:
        lo, hi = P.bbox(vertices)
        sized.append((name, vertices, faces, hi[0] - lo[0], hi[1] - lo[1]))
    sized.sort(key=lambda p: (-p[3] * p[4], -max(p[3:]), p[0]))
    placed, boxes = [], []
    for name, vertices, faces, width, height in sized:
        candidates = []
        for index, (x, y, w, h) in enumerate(free):
            for turn, pw, ph in ((False, width, height), (True, height, width)):
                rw, rh = pw + P.GAP, ph + P.GAP
                if rw <= w + 1e-6 and rh <= h + 1e-6:
                    candidates.append((min(w - rw, h - rh), max(w - rw, h - rh), y, x,
                                       index, turn, rw, rh))
        if not candidates:
            raise ValueError(f"four-plate allocation does not fit: {name} {width:.3f} x {height:.3f} mm")
        _short, _long, y, x, _index, turn, rw, rh = min(candidates)
        if turn:
            vertices = [(-vy, vx, vz) for vx, vy, vz in vertices]
        lo, hi = P.bbox(vertices)
        dx, dy = x - lo[0], y - lo[1]
        placed.append((name, vertices, faces, dx, dy))
        boxes.append({"name": name, "min_mm": [x, y, lo[2]],
                      "max_mm": [x + hi[0] - lo[0], y + hi[1] - lo[1], hi[2]],
                      "in_plane_rotation_deg": 90 if turn else 0})
        remaining = []
        for fx, fy, fw, fh in free:
            if x >= fx + fw or x + rw <= fx or y >= fy + fh or y + rh <= fy:
                remaining.append((fx, fy, fw, fh))
                continue
            if x > fx:
                remaining.append((fx, fy, x - fx, fh))
            if x + rw < fx + fw:
                remaining.append((x + rw, fy, fx + fw - x - rw, fh))
            if y > fy:
                remaining.append((fx, fy, fw, y - fy))
            if y + rh < fy + fh:
                remaining.append((fx, y + rh, fw, fy + fh - y - rh))
        free = [a for i, a in enumerate(remaining) if not any(
            i != j and a[0] >= b[0] and a[1] >= b[1]
            and a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3]
            and (a != b or i > j) for j, b in enumerate(remaining))]
    check_boxes(boxes)
    return placed, boxes


def transform(point, values):
    x, y, z = point
    return tuple(x * values[i] + y * values[3 + i] + z * values[6 + i] + values[9 + i]
                 for i in range(3))


def archive_boxes(path):
    """Read final component meshes and build transforms, including Bambu submodels."""
    with zipfile.ZipFile(path) as archive:
        config = ET.fromstring(archive.read("Metadata/model_settings.config"))
        names = {obj.get("id"): next((m.get("value") for m in obj.findall("metadata")
                                      if m.get("key") == "name"), obj.get("id"))
                 for obj in config.findall("object")}
        cache = {}

        def document(member):
            if member not in cache:
                tree = ET.fromstring(archive.read(member))
                cache[member] = (tree, {o.get("id"): o for o in tree.findall("m:resources/m:object", NS)})
            return cache[member]

        def vertices(member, object_id, ancestry=()):
            key = (member, object_id)
            if key in ancestry:
                raise ValueError(f"cyclic 3mf components: {key}")
            obj = document(member)[1][object_id]
            result = [tuple(float(v.get(k)) for k in ("x", "y", "z"))
                      for v in obj.findall("m:mesh/m:vertices/m:vertex", NS)]
            for child in obj.findall("m:components/m:component", NS):
                target = next((v.lstrip("/") for k, v in child.attrib.items() if k.endswith("}path")), member)
                matrix = tuple(float(v) for v in child.get("transform", " ".join(map(str, IDENTITY))).split())
                result.extend(transform(v, matrix) for v in vertices(target, child.get("objectid"), ancestry + (key,)))
            return result

        rows = []
        for item in document("3D/3dmodel.model")[0].findall("m:build/m:item", NS):
            oid = item.get("objectid")
            matrix = tuple(float(v) for v in item.get("transform", " ".join(map(str, IDENTITY))).split())
            points = [transform(v, matrix) for v in vertices("3D/3dmodel.model", oid)]
            lo, hi = P.bbox(points)
            rows.append({"name": names[oid], "min_mm": list(lo), "max_mm": list(hi)})
    check_boxes(rows)
    return rows


def profile_data():
    machine = resolve("machine", "Bambu Lab X1 Carbon 0.4 nozzle")
    process = resolve("process", "0.20mm Standard @BBL X1C")
    process.update({"curr_bed_type": "Textured PEI Plate", "wall_loops": "2",
                    "sparse_infill_density": "15%", "seam_position": "back",
                    "enable_support": "0", "exclude_object": "1", "brim_type": "no_brim",
                    "elefant_foot_compensation": "0.15"})
    filament = resolve("filament", "Bambu PLA Basic @BBL X1C")
    return [("machine", machine), ("process", process), ("filament_PLA", filament)]


def profiles(data):
    return [write_flat(str(OUT / "profiles" / (kind + ".json")), values) for kind, values in data]


def fingerprint(sources, data, trial_only):
    return {"plate_code": sha(Path(__file__)), "production_sources": sources,
            "manifest": None if trial_only else sha(BUILD / "manifest.json"),
            "trial_sources": {path: sha(OUT / path) for _name, path, _flip in trial_files()},
            "profiles": hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest(),
            "trial_only": trial_only}


def cached_summary(inputs):
    path = BUILD / "plate-summary.json"
    if not path.is_file():
        return None
    try:
        summary = read(path)
        if (summary.get("fingerprint") != inputs or not summary.get("output_sha256")
                or not isinstance(summary.get("slice_pass"), bool) or not summary.get("plates")):
            return None
        for relative, expected in summary["output_sha256"].items():
            if sha(ROOT / relative) != expected:
                return None
        return summary
    except (OSError, ValueError, TypeError, KeyError):
        return None


def slice_plate(name, parts, settings, log_directory):
    placed, expected = arrange(parts)
    basename = f"{MODEL}-{name}-PLA"
    layout = OUT / f"{basename}-layout.3mf"
    temporary = layout.with_name(layout.name + ".tmp")
    P.write_3mf(temporary, placed)
    os.replace(temporary, layout)
    print(f"{name}: {len(parts)} print parts; layout bounds checked", flush=True)
    work = BUILD / f"slice-{name}"
    work.mkdir(parents=True, exist_ok=True)
    destination = OUT / f"{basename}.gcode.3mf"
    output = work / destination.name
    if output.exists():
        output.unlink()
    mp, pp, fp = settings
    command = [str(EXE), "--slice", "0", "--debug", "2", "--arrange", "0",
               "--load-settings", f"{mp};{pp}", "--load-filaments", fp,
               "--outputdir", str(work), "--export-3mf", destination.name, str(layout)]
    log_path = log_directory / f"{name}.log"
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=False)
    if result.returncode or not output.is_file():
        raise RuntimeError(f"{name}: Bambu CLI exit {result.returncode}; missing output={not output.exists()}; {log_path}")
    actual = archive_boxes(output)
    expected_by_name = {r["name"]: r for r in expected}
    if set(expected_by_name) != {r["name"] for r in actual}:
        raise ValueError(f"{name}: sliced object names differ from manifest")
    for row in actual:
        source = expected_by_name[row["name"]]
        if any(abs(a - b) > 0.005 for key in ("min_mm", "max_mm") for a, b in zip(row[key], source[key])):
            raise ValueError(f"{name}: Bambu changed placement: {row}; expected {source}")
    info = inspect_sliced_3mf(str(output))
    info.update({"plate": name, "parts": [p[0] for p in parts], "layout_boxes": actual,
                 "command": command, "returncode": result.returncode, "log": str(log_path),
                 "sha256": sha(output), "file": destination.relative_to(ROOT).as_posix(),
                 "layout_file": layout.relative_to(ROOT).as_posix()})
    info["named_objects"] = identify_slice_objects(output, info, read(mp))
    temporary = destination.with_name(destination.name + ".tmp")
    shutil.copyfile(output, temporary)
    os.replace(temporary, destination)
    write(BUILD / f"plate-{name}.json", info)
    bad = {key: row["floating"]["external_unsupported_mm"] for key, row in info["objects"].items()
           if row["floating"]["external_unsupported_mm"] > L.SLICE_MAX_EXTERNAL_UNSUPPORTED_MM}
    info["slice_failing"] = bad
    info["slice_pass"] = not bad and info["support_used"] in ("false", "0")
    write(BUILD / f"plate-{name}.json", info)
    print(f"{name}: {info['prediction_s']} s / {info['weight_g']} g / support={info['support_used']} / external unsupported={bad}", flush=True)
    return info


def identify_slice_objects(path, report, machine):
    """Map meter object IDs by actual extrusion bounds, never XML/index order.

    Measurements come from the shared slice meter unchanged. This only attaches
    the manifest part name after checking a unique geometric correspondence.
    """
    offset = [float(v) for v in machine["extruder_offset"][0].split("x")]
    with zipfile.ZipFile(path) as archive:
        members = [n for n in archive.namelist() if n.endswith(".gcode")]
        if len(members) != 1:
            raise ValueError(f"expected one sliced plate: {members}")
        payload = archive.read(members[0])
    with tempfile.TemporaryDirectory(dir=BUILD) as directory:
        gcode = Path(directory) / "plate.gcode"
        gcode.write_bytes(payload)
        layers, _stats = parse_gcode(str(gcode))
    bounds = {}
    for layer in layers:
        for x0, y0, x1, y1, _feature, oid, _z in layer["segs"]:
            x0, x1 = x0 + offset[0], x1 + offset[0]
            y0, y1 = y0 + offset[1], y1 + offset[1]
            box = bounds.setdefault(str(oid), [float("inf"), float("inf"),
                                                 -float("inf"), -float("inf")])
            box[:] = [min(box[0], x0, x1), min(box[1], y0, y1),
                      max(box[2], x0, x1), max(box[3], y0, y1)]
    rows, matched = [], set()
    for oid, obj in report["objects"].items():
        box = bounds[oid]
        candidates = [b for b in report["layout_boxes"]
                      if all(box[i] >= b["min_mm"][i] - 1 for i in (0, 1))
                      and all(box[i + 2] <= b["max_mm"][i] + 1 for i in (0, 1))]
        if len(candidates) != 1 or candidates[0]["name"] in matched:
            raise ValueError(f"{report['plate']}: ambiguous extrusion object {oid}: {box}")
        name = candidates[0]["name"]
        matched.add(name)
        rows.append({"part": name.replace("__", "/"), "gcode_object_id": oid,
                     "external_unsupported_mm": obj["floating"]["external_unsupported_mm"],
                     "print_xy_mm": box, "overhang_walls": obj["overhang_walls"]})
    if matched != set(report["parts"]):
        raise ValueError(f"{report['plate']}: printed object coverage differs from layout")
    return rows


def publish_case_plates(reports):
    # Gate slice.files resolves paths from the repository root, including cases.
    write(BUILD / "plate-case-files.json", {slot: [r["file"] for r in reports]
          for slot in ("root", "front", "top", "right")})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout-only", action="store_true")
    parser.add_argument("--trial-only", action="store_true")
    parser.add_argument("--if-stale", action="store_true", help="reuse only when all input and output hashes match")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    groups, sources = production_groups() if not args.trial_only else ({}, {})
    data = profile_data()
    inputs = fingerprint(sources, data, args.trial_only)
    if args.if_stale and not args.layout_only:
        previous = cached_summary(inputs)
        if previous is not None:
            print("Slice inputs and output SHA256 match; reusing existing plate-summary.json", flush=True)
            return 0 if previous.get("slice_pass") is True else 1
    groups["05-fit-trial"] = trial_parts()
    if args.layout_only:
        rows = {name: arrange(parts)[1] for name, parts in groups.items()}
        write(BUILD / "plate-layout-check.json", {"sources": sources, "plates": rows})
        print(json.dumps({k: len(v) for k, v in rows.items()}, indent=1))
        return 0
    log_directory = Path("G:/マイドライブ/shubie/reports") / f"{MODEL}-v2-slices"
    log_directory.mkdir(parents=True, exist_ok=True)
    temp_directory = BUILD / "slice-temp"
    temp_directory.mkdir(parents=True, exist_ok=True)
    os.environ["TEMP"] = os.environ["TMP"] = str(temp_directory)
    tempfile.tempdir = str(temp_directory)
    settings = profiles(data)
    reports = [slice_plate(name, parts, settings, log_directory) for name, parts in groups.items()]
    write(BUILD / "plate-diagnostics.json", {"plates": [
        {"plate": r["plate"], "file": r["file"], "parts": r["named_objects"]} for r in reports]})
    if not args.trial_only:
        publish_case_plates(reports)
    outputs = [ROOT / r[key] for r in reports for key in ("file", "layout_file")]
    outputs += [Path(path) for path in settings]
    outputs += [BUILD / f"plate-{r['plate']}.json" for r in reports]
    if not args.trial_only:
        outputs.append(BUILD / "plate-case-files.json")
    outputs.append(BUILD / "plate-diagnostics.json")
    current_sources = {} if args.trial_only else production_groups()[1]
    if fingerprint(current_sources, profile_data(), args.trial_only) != inputs:
        raise RuntimeError("slice inputs changed during execution; regenerate before certification")
    write(BUILD / "plate-summary.json", {"sources": sources, "settings": settings, "plates": reports,
          "logs": str(log_directory), "support_required": False,
          "slice_pass": all(r["slice_pass"] for r in reports), "fingerprint": inputs,
          "output_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in outputs}})
    if not args.trial_only:
        from print_results import generate
        generate()
    return 0 if all(r["slice_pass"] for r in reports) else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
