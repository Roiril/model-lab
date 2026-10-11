"""Measure the C4 carrier_outer removable support gap from actual sliced G-code."""

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
    evidence_path = folder / "build" / "carrier_outer_print_support.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    span_path = folder / "build" / f"print_spans_{args.material}.json"
    span = json.loads(span_path.read_text(encoding="utf-8"))
    object_name = f"{model}-print-carrier_outer"
    object_id = next(row["objectId"] for row in span["objects"] if row["name"] == object_name)
    plate_path = ROOT / "prints" / model / f"{model}-{args.material}.gcode.3mf"
    placement = next(row for row in inspect_layout(plate_path)["objects"]
                     if row["name"] == object_name)
    stl_path = ROOT / "prints" / model / f"{object_name}.stl"
    stl_vertices, stl_faces = read_stl(stl_path)
    stl_min, _ = bbox(stl_vertices)
    expected_bounds = evidence["support_bbox_mm"]
    support_component = next(
        bounds for bounds in component_bounds(stl_vertices, stl_faces)
        if all(abs(bounds[side][axis] - expected_bounds[side][axis]) <= 1e-3
               for side in range(2) for axis in range(3)))
    offset = span["objectAssignment"]["detail"]["global_offset_mm"]

    def plate_xy(local_x, local_y):
        return (local_x - stl_min[0] + placement["min"][0] - offset[0],
                local_y - stl_min[1] + placement["min"][1] - offset[1])

    corner0 = plate_xy(support_component[0][0], support_component[0][1])
    corner1 = plate_xy(support_component[1][0], support_component[1][1])
    x0, x1 = sorted((corner0[0], corner1[0]))
    y0, y1 = sorted((corner0[1], corner1[1]))
    selected = {}
    for layer in read_width_layers(plate_path):
        rows = []
        for segment in layer["segs"]:
            sx, sy, ex, ey, feature, obj, z, width, height = segment
            mx, my = (sx + ex) / 2, (sy + ey) / 2
            if obj == object_id and x0 <= mx <= x1 and y0 <= my <= y1:
                rows.append((feature, z, width, height))
        if rows:
            selected[round(float(layer["z"]), 4)] = rows

    support_top = round(evidence["designed_support_top_z_mm"], 4)
    product_first = round(evidence["designed_product_first_extrusion_z_mm"], 4)
    support_rows = selected[support_top]
    product_rows = selected[product_first]
    support_height = max(row[3] for row in support_rows)
    product_height = max(row[3] for row in product_rows)
    support_material_top = support_top
    product_material_bottom = round(product_first - product_height, 4)
    result = {
        "model": model,
        "material": args.material,
        "sourceGcode": {
            "file": str(plate_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(plate_path),
        },
        "sourcePrintStl": {
            "file": str(stl_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(stl_path),
        },
        "sourceSupportEvidence": {
            "file": str(evidence_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(evidence_path),
        },
        "supportComponentBoundsMm": support_component,
        "supportLastExtrusion": {
            "zMm": support_top,
            "segments": len(support_rows),
            "features": sorted({row[0] for row in support_rows}),
            "lineWidthsMm": sorted({round(row[2], 5) for row in support_rows}),
            "layerHeightsMm": sorted({round(row[3], 5) for row in support_rows}),
        },
        "productFirstExtrusion": {
            "zMm": product_first,
            "segments": len(product_rows),
            "features": sorted({row[0] for row in product_rows}),
            "lineWidthsMm": sorted({round(row[2], 5) for row in product_rows}),
            "layerHeightsMm": sorted({round(row[3], 5) for row in product_rows}),
        },
        "supportMaterialTopMm": support_material_top,
        "productMaterialBottomMm": product_material_bottom,
        "materialGapMm": round(product_material_bottom - support_material_top, 4),
        "extrusionAtGapLayer": round(product_first - product_height, 4) in selected,
        "removalPhysicallyVerified": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
