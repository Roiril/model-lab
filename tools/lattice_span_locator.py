"""Map one measured G-code unsupported interval back to its print STL coordinates."""

import argparse
import json
import math
from pathlib import Path
import re
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.stdout.reconfigure(encoding="utf-8")

from lattice_delivery import inspect_layout  # noqa: E402
from lattice_print_spans import (  # noqa: E402
    CELL,
    _run_result,
    _sample_chain,
    _unsupported_runs,
    coverage,
)
from plate_3mf import bbox, read_stl  # noqa: E402


def point_segment_distance(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    squared = dx * dx + dy * dy
    if squared == 0:
        return math.dist(point, start)
    t = max(0.0, min(1.0, ((point[0] - start[0]) * dx
                            + (point[1] - start[1]) * dy) / squared))
    closest = (start[0] + t * dx, start[1] + t * dy)
    return math.dist(point, closest)


def read_width_layers(path):
    with zipfile.ZipFile(path) as archive:
        name = next(name for name in archive.namelist() if name.endswith(".gcode"))
        lines = archive.read(name).decode("utf-8", "replace").splitlines()
    layers = []
    current = None
    x = y = z = 0.0
    feature = ""
    obj = None
    width = None
    layer_height = None
    for line in lines:
        if line.startswith(";"):
            if line.startswith("; CHANGE_LAYER"):
                current = {"z": None, "segs": []}
                layers.append(current)
            elif line.startswith("; Z_HEIGHT:") and current is not None:
                current["z"] = float(line.split(":", 1)[1])
            elif line.startswith("; FEATURE:"):
                feature = line.split(":", 1)[1].strip()
            elif line.startswith("; LINE_WIDTH:"):
                width = float(line.split(":", 1)[1])
            elif line.startswith("; LAYER_HEIGHT:"):
                layer_height = float(line.split(":", 1)[1])
            elif line.startswith("; start printing object, unique label id:"):
                obj = int(line.rsplit(":", 1)[1])
            elif line.startswith("; stop printing object"):
                obj = None
            continue
        if not (line.startswith("G0 ") or line.startswith("G1 ")
                or line.startswith("G2 ") or line.startswith("G3 ")):
            continue
        values = dict(re.findall(r"([XYZEIJ])(-?[\d.]+)", line.split(";")[0]))
        nx, ny = float(values.get("X", x)), float(values.get("Y", y))
        if "Z" in values:
            z = float(values["Z"])
        extrusion = float(values.get("E", 0.0))
        if (current is not None and extrusion > 0 and width is not None and layer_height is not None
                and (nx != x or ny != y or "I" in values or "J" in values)):
            if (line.startswith("G2") or line.startswith("G3")) and ("I" in values or "J" in values):
                center_x = x + float(values.get("I", 0.0))
                center_y = y + float(values.get("J", 0.0))
                radius = math.hypot(x - center_x, y - center_y)
                a0, a1 = math.atan2(y - center_y, x - center_x), math.atan2(ny - center_y, nx - center_x)
                sweep = ((a1 - a0) % (2 * math.pi) or 2 * math.pi) if line.startswith("G3") else -((a0 - a1) % (2 * math.pi) or 2 * math.pi)
                count = max(2, int(abs(sweep) * radius / 0.2))
                px, py = x, y
                for index in range(1, count + 1):
                    angle = a0 + sweep * index / count
                    qx, qy = ((center_x + radius * math.cos(angle), center_y + radius * math.sin(angle))
                              if index < count else (nx, ny))
                    current["segs"].append((px, py, qx, qy, feature, obj, z, width, layer_height))
                    px, py = qx, qy
            elif line.startswith("G1"):
                current["segs"].append((x, y, nx, ny, feature, obj, z, width, layer_height))
        x, y = nx, ny
    return layers


def width_chains(segments):
    chains = []
    current = None
    for segment in segments:
        start, end, feature, width = segment[:2], segment[2:4], segment[4], segment[7]
        if math.dist(start, end) <= 1e-6:
            continue
        if (current is not None and current["feature"] == feature
                and math.dist(current["points"][-1], start) <= 1e-6):
            current["points"].append(end)
            current["widths"].append(width)
        else:
            current = {"feature": feature, "points": [start, end], "widths": [width]}
            chains.append(current)
    return chains


def same_layer_anchors(plate_path, object_id, z_mm, interval):
    layers = read_width_layers(plate_path)
    by_z = {}
    for layer in layers:
        segments = [segment for segment in layer["segs"] if segment[5] == object_id]
        if segments:
            by_z[round(float(layer["z"]), 4)] = segments
    ordered_z = sorted(by_z)
    layer_index = ordered_z.index(z_mm)
    previous_cells = coverage(by_z[ordered_z[layer_index - 1]], CELL)
    chains = width_chains(by_z[z_mm])
    target_index = interval["pathIndex"]
    target_width = max(chains[target_index]["widths"])
    target_points = [interval["startXYmm"], interval["endXYmm"]]
    results = []
    for path_index, chain in enumerate(chains[:target_index]):
        units = _sample_chain(chain["points"], previous_cells)
        if not units:
            continue
        unsupported = [
            _run_result(units, run, math.dist(chain["points"][0], chain["points"][-1]) <= 1e-6)
            for run in _unsupported_runs(
                units, math.dist(chain["points"][0], chain["points"][-1]) <= 1e-6)
        ]
        distances = [
            min(point_segment_distance(point, start, end)
                for start, end in zip(chain["points"][:-1], chain["points"][1:]))
            for point in target_points
        ]
        if min(distances) <= 1.0:
            prior_width = max(chain["widths"])
            overlap_limit = (target_width + prior_width) / 2
            results.append({
                "pathIndex": path_index,
                "feature": chain["feature"],
                "distanceFromTargetEndpointsMm": [round(value, 4) for value in distances],
                "targetLineWidthMm": round(target_width, 5),
                "earlierLineWidthMm": round(prior_width, 5),
                "centerlineOverlapLimitMm": round(overlap_limit, 5),
                "centerlineOverlapsAtTargetEndpoints": [
                    value <= overlap_limit for value in distances],
                "overlapMarginAtTargetEndpointsMm": [
                    round(overlap_limit - value, 4) for value in distances],
                "previousLayerSupportedFraction": round(
                    sum(unit["supported"] for unit in units) / len(units), 4),
                "unsupportedRuns": sorted(unsupported,
                    key=lambda row: row["lengthMm"], reverse=True)[:3],
            })
    return sorted(results,
                  key=lambda row: min(row["distanceFromTargetEndpointsMm"]))[:8]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model")
    parser.add_argument("object")
    parser.add_argument("support", choices=("one_end", "none"))
    parser.add_argument("feature")
    parser.add_argument("category")
    parser.add_argument("--material", default="PLA", choices=("PLA", "PETG"))
    args = parser.parse_args()

    folder = ROOT / "models" / args.model
    report_path = folder / "build" / f"print_spans_{args.material}.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    wanted_name = f"{args.model}-print-{args.object}"
    obj = next(row for row in report["objects"] if row["name"] == wanted_name)
    candidates = []
    for layer in obj["layers"]:
        for interval in layer["intervals"]:
            if (interval["support"], interval["feature"], interval["category"]) == (
                    args.support, args.feature, args.category):
                candidates.append((interval["lengthMm"], layer["zMm"], interval))
    length, z_mm, interval = max(candidates, key=lambda row: row[0])

    plate_path = ROOT / "prints" / args.model / f"{args.model}-{args.material}.gcode.3mf"
    layout = inspect_layout(plate_path)
    placement = next(row for row in layout["objects"] if row["name"] == wanted_name)
    stl_path = ROOT / "prints" / args.model / f"{wanted_name}.stl"
    stl_min, _ = bbox(read_stl(stl_path)[0])
    offset = report["objectAssignment"]["detail"]["global_offset_mm"]
    def local(point):
        return [
            round(point[0] + offset[0] - placement["min"][0] + stl_min[0], 4),
            round(point[1] + offset[1] - placement["min"][1] + stl_min[1], 4),
            z_mm,
        ]

    endpoints = [local(interval["startXYmm"]), local(interval["endXYmm"])]
    chord = math.dist(endpoints[0], endpoints[1])
    result = {
        "model": args.model,
        "object": args.object,
        "support": args.support,
        "feature": args.feature,
        "category": args.category,
        "targetPathIndex": interval["pathIndex"],
        "pathLengthMm": length,
        "endpointDistanceMm": round(chord, 4),
        "plateEndpointsMm": [interval["startXYmm"], interval["endXYmm"]],
        "printStlEndpointsMm": endpoints,
        "sameLayerEarlierPathsWithin1mm": same_layer_anchors(
            plate_path, obj["objectId"], z_mm, interval),
    }
    if args.model == "mystery-box-sg92r-c4" and args.object.startswith("carrier_"):
        manifest = json.loads((folder / "build" / "manifest.json").read_text(encoding="utf-8"))
        part = next(row for row in manifest["parts"] if row["id"] == args.object)
        _, assembly_max = bbox(read_stl(folder / part["assembly"])[0])
        result["assemblyEndpointsMm"] = [
            [point[0], round(-point[1], 4), round(assembly_max[2] - point[2], 4)]
            for point in endpoints
        ]
    elif args.object == "housing":
        result["assemblyEndpointsMm"] = endpoints
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
