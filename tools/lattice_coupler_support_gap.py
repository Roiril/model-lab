"""Measure the C4 removable support/peg vertical gap from the actual sliced G-code."""

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.stdout.reconfigure(encoding="utf-8")

from lattice_delivery import inspect_layout  # noqa: E402
from lattice_span_locator import read_width_layers  # noqa: E402
from plate_3mf import bbox, read_stl  # noqa: E402


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def component_bounds(vertices, faces):
    parent = list(range(len(vertices)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left, right):
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left

    for face in faces:
        union(face[0], face[1])
        union(face[1], face[2])
    groups = {}
    for index, vertex in enumerate(vertices):
        groups.setdefault(find(index), []).append(vertex)
    return [bbox(points) for points in groups.values()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--material", default="PLA", choices=("PLA", "PETG"))
    args = parser.parse_args()
    model = "mystery-box-sg92r-c4"
    folder = ROOT / "models" / model
    span_path = folder / "build" / f"print_spans_{args.material}.json"
    span = json.loads(span_path.read_text(encoding="utf-8"))
    object_name = f"{model}-print-horn_coupler"
    object_id = next(row["objectId"] for row in span["objects"] if row["name"] == object_name)
    plate_path = ROOT / "prints" / model / f"{model}-{args.material}.gcode.3mf"
    placement = next(row for row in inspect_layout(plate_path)["objects"]
                     if row["name"] == object_name)
    stl_path = ROOT / "prints" / model / f"{object_name}.stl"
    stl_vertices, stl_faces = read_stl(stl_path)
    stl_min, _ = bbox(stl_vertices)
    components = component_bounds(stl_vertices, stl_faces)
    support_component = next(
        bounds for bounds in components
        if abs(bounds[0][2]) <= 1e-4 and abs(bounds[1][2] - 7.8) <= 1e-3
        and bounds[1][0] - bounds[0][0] < 10.0
        and bounds[1][1] - bounds[0][1] < 3.0)
    offset = span["objectAssignment"]["detail"]["global_offset_mm"]
    def plate_xy(local_x, local_y):
        return (local_x - stl_min[0] + placement["min"][0] - offset[0],
                local_y - stl_min[1] + placement["min"][1] - offset[1])

    support_center_y = (support_component[0][1] + support_component[1][1]) / 2
    corner0 = plate_xy(support_component[0][0], support_center_y - 0.3)
    corner1 = plate_xy(support_component[1][0], support_center_y + 0.3)
    x0, x1 = sorted((corner0[0], corner1[0]))
    y0, y1 = sorted((corner0[1], corner1[1]))
    selected = {}
    object_nearby = {}
    center_x, center_y = (x0 + x1) / 2, (y0 + y1) / 2
    for layer in read_width_layers(plate_path):
        if layer["z"] is None:
            continue
        for segment in layer["segs"]:
            if segment[5] != object_id:
                continue
            if 7.4 <= float(layer["z"]) <= 8.6:
                nearby = object_nearby.setdefault(round(float(layer["z"]), 4), {
                    "x": [], "y": [], "features": set(), "nearest": []})
                nearby["x"].extend((segment[0], segment[2]))
                nearby["y"].extend((segment[1], segment[3]))
                nearby["features"].add(segment[4])
                nearby["nearest"].append((
                    min((segment[0] - center_x) ** 2 + (segment[1] - center_y) ** 2,
                        (segment[2] - center_x) ** 2 + (segment[3] - center_y) ** 2) ** 0.5,
                    segment[0], segment[1], segment[2], segment[3], segment[4]))
            margin = segment[7] / 2
            if (max(segment[0], segment[2]) + margin < x0
                    or min(segment[0], segment[2]) - margin > x1
                    or max(segment[1], segment[3]) + margin < y0
                    or min(segment[1], segment[3]) - margin > y1):
                continue
            key = round(float(layer["z"]), 4)
            row = selected.setdefault(key, {"zMm": key, "segments": 0,
                                            "features": set(), "lineWidthsMm": set(),
                                            "layerHeightsMm": set()})
            row["segments"] += 1
            row["features"].add(segment[4])
            row["lineWidthsMm"].add(round(segment[7], 5))
            row["layerHeightsMm"].add(round(segment[8], 5))
    rows = []
    for row in selected.values():
        row["features"] = sorted(row["features"])
        row["lineWidthsMm"] = sorted(row["lineWidthsMm"])
        row["layerHeightsMm"] = sorted(row["layerHeightsMm"])
        rows.append(row)
    rows.sort(key=lambda row: row["zMm"])
    if not any(row["zMm"] < 8.2 for row in rows) or not any(row["zMm"] >= 8.2 for row in rows):
        diagnostic = {
            "inspectionBounds": [[x0, x1], [y0, y1]],
            "selectedLayers": rows,
            "objectLayers": {
                str(z): {"boundsXYmm": [[min(row["x"]), max(row["x"])],
                                         [min(row["y"]), max(row["y"])]],
                         "features": sorted(row["features"]),
                         "nearestSegments": sorted(row["nearest"])[:5]}
                for z, row in object_nearby.items()
            },
        }
        raise RuntimeError(json.dumps(diagnostic, ensure_ascii=False))
    support = max((row for row in rows if row["zMm"] < 8.2),
                  key=lambda row: row["zMm"])
    peg = min((row for row in rows if row["zMm"] >= 8.2),
              key=lambda row: row["zMm"])
    peg_height = min(peg["layerHeightsMm"])
    result = {
        "model": model,
        "material": args.material,
        "sourceGcode": {"file": plate_path.relative_to(ROOT).as_posix(),
                        "sha256": sha256(plate_path)},
        "sourcePrintStl": {"file": stl_path.relative_to(ROOT).as_posix(),
                           "sha256": sha256(stl_path)},
        "inspectionPlateBoundsXYmm": [[round(x0, 4), round(x1, 4)],
                                      [round(y0, 4), round(y1, 4)]],
        "supportComponentBoundsMm": support_component,
        "supportLastExtrusion": support,
        "pegFirstExtrusion": peg,
        "supportMaterialTopMm": support["zMm"],
        "pegMaterialBottomMm": round(peg["zMm"] - peg_height, 4),
        "materialGapMm": round(peg["zMm"] - peg_height - support["zMm"], 4),
        "nearbyLayers": [row for row in rows if 7.4 <= row["zMm"] <= 8.6],
        "removalPhysicallyVerified": False
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
