"""C4外環格子の除去式印刷支持を実形状で検証する。"""

import hashlib
import json
import os
import sys

import bmesh
import bpy


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(ROOT, "models", "mystery-box-sg92r-c4")
sys.path.insert(0, MODEL_DIR)
sys.path.insert(0, os.path.join(ROOT, "lib"))

import model
import params as P
from printmech.geometry import box, volume
from solid_volume import closed_boundary_volume


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def common_volume(first, second, solver="MANIFOLD"):
    probe = model.duplicate(first, "support_probe_a")
    cutter = model.duplicate(second, "support_probe_b")
    try:
        for ob in (probe, cutter):
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            invalid = any(not edge.is_manifold for edge in bm.edges)
            bm.free()
            if invalid:
                raise ValueError("support common-volume input is not a closed solid")
        modifier = probe.modifiers.new("intersection", "BOOLEAN")
        modifier.operation = "INTERSECT"
        modifier.solver = solver
        modifier.object = cutter
        bpy.context.view_layer.objects.active = probe
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm = bmesh.new()
        bm.from_mesh(probe.data)
        try:
            measured = closed_boundary_volume(bm)
        finally:
            bm.free()
        measured_bbox = model.bbox(probe) if probe.data.vertices else None
        return round(measured, 9), measured_bbox
    finally:
        for ob in (probe, cutter):
            bpy.data.objects.remove(ob, do_unlink=True)


def component_min_z(path):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=path)
    ob = next(item for item in bpy.data.objects if item not in before)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    unseen = set(bm.verts)
    minima = []
    while unseen:
        start = unseen.pop()
        stack = [start]
        component = [start]
        while stack:
            vertex = stack.pop()
            for edge in vertex.link_edges:
                neighbor = edge.other_vert(vertex)
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
                    component.append(neighbor)
        minima.append(min(vertex.co.z for vertex in component))
    bm.free()
    bpy.data.objects.remove(ob, do_unlink=True)
    return sorted(round(value, 6) for value in minima)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    model.clear_scene()
    carrier = model.build_carrier(2)
    model.place_on_bed(carrier, model.PRINT_TRANSFORMS["carrier_outer"])
    support = model.build_carrier_outer_print_support()

    positive_a = box(50, 52, 50, 52, 0, 2, "positive_a")
    positive_b = box(51, 53, 51, 53, 1, 3, "positive_b")
    negative_a = box(60, 62, 60, 62, 0, 2, "negative_a")
    negative_b = box(60, 62, 60, 62, 2.2, 4.2, "negative_b")
    thin_a = box(70, 71, 70, 71, 0, 1, "thin_a")
    thin_b = box(70.99, 71.99, 70, 71, 0, 1, "thin_b")
    calibration = {
        "positive_common_volume_mm3": common_volume(positive_a, positive_b)[0],
        "negative_common_volume_mm3": common_volume(negative_a, negative_b)[0],
        "thin_expected_mm3": 0.01,
        "thin_common_volume_mm3": common_volume(thin_a, thin_b)[0],
    }
    calibration["pass"] = (abs(calibration["positive_common_volume_mm3"] - 1.0) < .00001
        and calibration["negative_common_volume_mm3"] <= .00001
        and abs(calibration["thin_common_volume_mm3"] - .01) < .00001)
    for ob in (positive_a, positive_b, negative_a, negative_b, thin_a, thin_b):
        if ob.name in bpy.data.objects:
            bpy.data.objects.remove(ob, do_unlink=True)

    measured, measured_bbox = common_volume(carrier, support)
    exact_measured, _ = common_volume(carrier, support, "EXACT")
    print_stl = os.path.join(MODEL_DIR, "build", "print_carrier_outer.stl")
    tool_path = os.path.abspath(__file__)
    report = {
        "model": P.MODEL_ID,
        "part": "carrier_outer",
        "method": "closed inputs and closed-boundary volume; MANIFOLD primary, EXACT comparison; actual binary STL components",
        "primary_solver": "MANIFOLD",
        "calibration": calibration,
        "support_bbox_mm": model.bbox(support),
        "support_volume_mm3": round(volume(support), 6),
        "support_bed_footprint_mm2": round(
            2 * model.mm(P.CARRIER_OUTER_PRINT_SUPPORT_BASE_X_HALF)
            * (model.mm(P.CARRIER_OUTER_PRINT_SUPPORT_BASE_Y[1])
               - model.mm(P.CARRIER_OUTER_PRINT_SUPPORT_BASE_Y[0])), 6),
        "support_product_common_volume_mm3": measured,
        "support_product_exact_common_volume_mm3": exact_measured,
        "support_product_common_bbox_mm": measured_bbox,
        "designed_product_first_extrusion_z_mm": model.mm(
            P.CARRIER_OUTER_PRINT_SUPPORT_PRODUCT_Z),
        "designed_support_top_z_mm": (
            model.mm(P.CARRIER_OUTER_PRINT_SUPPORT_PRODUCT_Z)
            - model.mm(P.CARRIER_OUTER_PRINT_SUPPORT_LAYER_H)
            - model.mm(P.CARRIER_OUTER_PRINT_SUPPORT_GAP)),
        "designed_material_face_gap_mm": model.mm(P.CARRIER_OUTER_PRINT_SUPPORT_GAP),
        "print_stl_component_min_z_mm": component_min_z(print_stl),
        "expected_print_components": 2,
        "source_sha256": {
            "tools/lattice_carrier_outer_support.py": sha256(tool_path),
            "lib/solid_volume.py": sha256(os.path.join(ROOT, "lib", "solid_volume.py")),
            "models/mystery-box-sg92r-c4/model.py": sha256(
                os.path.join(MODEL_DIR, "model.py")),
            "models/mystery-box-sg92r-c4/params.py": sha256(
                os.path.join(MODEL_DIR, "params.py")),
            "models/mystery-box-sg92r-c4/build/carrier_outer.stl": sha256(
                os.path.join(MODEL_DIR, "build", "carrier_outer.stl")),
            "models/mystery-box-sg92r-c4/build/print_carrier_outer.stl": sha256(print_stl),
        },
    }
    report["pass"] = (
        calibration["pass"]
        and measured <= 0.001
        and abs(exact_measured - measured) <= .00001
        and report["print_stl_component_min_z_mm"] == [0.0, 0.0]
    )
    output = os.path.join(MODEL_DIR, "build", "carrier_outer_print_support.json")
    model.write_json(output, report)
    print(json.dumps({"output": output, **report}, ensure_ascii=False))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
