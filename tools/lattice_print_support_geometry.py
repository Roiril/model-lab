"""C4の印刷専用支持と最終binary STLの接続を検査する。"""

import hashlib
import json
import os
from pathlib import Path
import sys

import bmesh
import bpy


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from lattice_carrier_outer_support import common_volume, component_min_z  # noqa: E402
import lattice_carrier_outer_support as carrier_meter  # noqa: E402
from solid_volume import closed_boundary_volume  # noqa: E402


model = carrier_meter.model
P = carrier_meter.P
BUILD = ROOT / "models" / P.MODEL_ID / "build"
PRODUCT_BUILDERS = {
    "housing": model.build_housing,
    "horn_coupler": model.build_horn_coupler,
    "carrier_center": lambda: model.build_carrier(0),
    "carrier_outer": lambda: model.build_carrier(2),
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hashes(paths):
    return {Path(path).relative_to(ROOT).as_posix(): digest(path) for path in paths}


def solid_volume(ob):
    mesh = bmesh.new()
    mesh.from_mesh(ob.data)
    try:
        if any(not edge.is_manifold for edge in mesh.edges):
            raise ValueError(f"support volume input is not closed: {ob.name}")
        return closed_boundary_volume(mesh)
    finally:
        mesh.free()


def imported_stl(path):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    added = set(bpy.data.objects) - before
    if len(added) != 1:
        raise ValueError(f"unexpected STL object count: {path}")
    return added.pop()


def positive_contact_bounds(first, second):
    """Exclude disconnected planar contact faces from the material overlap box."""
    probe = model.duplicate(first, "positive_contact_probe")
    cutter = model.duplicate(second, "positive_contact_cutter")
    try:
        modifier = probe.modifiers.new("actual_material_contact", "BOOLEAN")
        modifier.operation = "INTERSECT"
        modifier.solver = "MANIFOLD"
        modifier.object = cutter
        bpy.context.view_layer.objects.active = probe
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        mesh = bmesh.new()
        mesh.from_mesh(probe.data)
        positive_points = []
        remaining = set(mesh.verts)
        try:
            while remaining:
                seed = remaining.pop()
                vertices, pending = [seed], [seed]
                while pending:
                    vertex = pending.pop()
                    for edge in vertex.link_edges:
                        other = edge.other_vert(vertex)
                        if other in remaining:
                            remaining.remove(other)
                            vertices.append(other)
                            pending.append(other)
                faces = {face for vertex in vertices for face in vertex.link_faces}
                if not faces:
                    continue
                component = bmesh.new()
                mapping = {vertex: component.verts.new(vertex.co) for vertex in vertices}
                for face in faces:
                    component.faces.new([mapping[vertex] for vertex in face.verts])
                try:
                    if closed_boundary_volume(component) > 1e-12:
                        positive_points.extend(tuple(vertex.co) for vertex in vertices)
                finally:
                    component.free()
        finally:
            mesh.free()
        return ([[min(point[axis] for point in positive_points) for axis in range(3)],
                 [max(point[axis] for point in positive_points) for axis in range(3)]]
                if positive_points else None)
    finally:
        for ob in (probe, cutter):
            bpy.data.objects.remove(ob, do_unlink=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    report_source = BUILD / "model_report.json"
    metadata = json.loads(report_source.read_text(encoding="utf-8"))["print_supports"]
    if not isinstance(metadata, list):
        raise ValueError("print_supports must enumerate each support height")
    dependency_paths = [Path(__file__), ROOT / "tools/lattice_carrier_outer_support.py",
        ROOT / "lib/solid_volume.py", ROOT / "lib/printmech/geometry.py",
        ROOT / "models" / P.MODEL_ID / "model.py",
        ROOT / "models" / P.MODEL_ID / "params.py", report_source]
    part_ids = {row["part_id"] for row in metadata}
    dependency_paths.extend(BUILD / f"print_{part}.stl" for part in part_ids)
    dependency_paths.extend(BUILD / f"{part}.stl" for part in part_ids)
    start_hashes = hashes(dependency_paths)
    model.clear_scene()

    box = carrier_meter.box
    first = box(50, 51, 50, 51, 0, 1, "meter_positive_a")
    second = box(50.5, 51.5, 50, 51, 0, 1, "meter_positive_b")
    absent = box(52, 53, 50, 51, 0, 1, "meter_negative")
    touching = box(51, 52, 50, 51, 0, 1, "meter_touching")
    thin = box(50.99, 51.99, 50, 51, 0, 1, "meter_thin")
    calibration = {
        "overlapExpectedMm3": .5, "overlapMeasuredMm3": common_volume(first, second)[0],
        "absentMeasuredMm3": common_volume(first, absent)[0],
        "touchingMeasuredMm3": common_volume(first, touching)[0],
        "thinExpectedMm3": .01, "thinMeasuredMm3": common_volume(first, thin)[0],
        "containmentExpectedMm3": 1., "containmentMeasuredMm3": common_volume(first, first)[0],
        "positiveContactBoundsMm": positive_contact_bounds(first, second),
        "touchingPositiveContactBoundsMm": positive_contact_bounds(first, touching),
    }
    calibration["pass"] = (abs(calibration["overlapMeasuredMm3"] - .5) <= .00001
        and calibration["absentMeasuredMm3"] <= .00001
        and calibration["touchingMeasuredMm3"] <= .00001
        and abs(calibration["thinMeasuredMm3"] - .01) <= .00001
        and abs(calibration["containmentMeasuredMm3"] - 1.) <= .00001
        and calibration["positiveContactBoundsMm"] == [[50.5, 50., 0.], [51., 51., 1.]]
        and calibration["touchingPositiveContactBoundsMm"] is None)

    rows = []
    for part_id in sorted(part_ids):
        support_rows = [row for row in metadata if row["part_id"] == part_id]
        builders = {row["support_builder"] for row in support_rows}
        if len(builders) != 1:
            raise ValueError(f"one part must use one complete support builder: {part_id}")
        product = PRODUCT_BUILDERS[part_id]()
        model.place_on_bed(product, model.PRINT_TRANSFORMS[part_id])
        support = getattr(model, builders.pop())()
        printed = imported_stl(BUILD / f"print_{part_id}.stl")
        expected_volume = solid_volume(support)
        contained_volume, _ = common_volume(printed, support)
        common, raw_contact_bbox = common_volume(product, support)
        contact_bbox = positive_contact_bounds(product, support)
        exact_common, _ = common_volume(product, support, "EXACT")
        actual_min_z = component_min_z(str(BUILD / f"print_{part_id}.stl"))
        expected_components = {row["expected_print_components"] for row in support_rows}
        attached = any(row.get("attachment") == "breakaway_contact" for row in support_rows)
        allowed_bounds = next((row.get("allowed_contact_bbox_mm") for row in support_rows
            if row.get("allowed_contact_bbox_mm")), None)
        allowed_regions = next((row.get("allowed_contact_regions_mm") for row in support_rows
            if row.get("allowed_contact_regions_mm")), [])
        regional_contact = []
        regions_valid = bool(allowed_regions)
        support_bounds = model.bbox(support)
        for bounds in allowed_regions:
            regions_valid = regions_valid and all(
                support_bounds[0][axis] - .00001 <= bounds[0][axis] < bounds[1][axis] <=
                    support_bounds[1][axis] + .00001 for axis in range(3))
            region = box(bounds[0][0], bounds[1][0], bounds[0][1], bounds[1][1],
                bounds[0][2], bounds[1][2], "declared_contact_region")
            regional_contact.append({"boundsMm": bounds, "commonVolumeMm3": common_volume(product, region)[0]})
            bpy.data.objects.remove(region, do_unlink=True)
        for first_index, first_bounds in enumerate(allowed_regions):
            for second_bounds in allowed_regions[first_index + 1:]:
                regions_valid = regions_valid and any(
                    first_bounds[1][axis] <= second_bounds[0][axis] or
                    second_bounds[1][axis] <= first_bounds[0][axis] for axis in range(3))
        regional_total = sum(item["commonVolumeMm3"] for item in regional_contact)
        # The only attached support is rectangular. Each declared box is within
        # that actual support, so the regional product intersections partition
        # its material contacts without admitting material outside the support.
        if attached and part_id != "housing":
            raise ValueError("attached nonrectangular support needs its own region-clipping meter")
        contact_in_bounds = (common <= .001 if not attached else
            regions_valid and abs(regional_total - common) <= .00001)
        row = {
            "partId": part_id, "supportIds": [item["support_id"] for item in support_rows],
            "attachment": "breakaway_contact" if attached else "separate",
            "supportBoundsMm": model.bbox(support),
            "supportVolumeMm3": expected_volume,
            "supportPresentInPrintVolumeMm3": contained_volume,
            "missingSupportVolumeMm3": max(0., expected_volume - contained_volume),
            "supportPresenceVolumeDifferenceMm3": contained_volume - expected_volume,
            "supportProductCommonVolumeMm3": common,
            "supportProductExactCommonVolumeMm3": exact_common,
            "supportProductCommonBoundsMm": contact_bbox,
            "supportProductRawBoundaryBoundsMm": raw_contact_bbox,
            "allowedContactBoundsMm": allowed_bounds,
            "allowedContactRegionsMm": allowed_regions,
            "regionalContactMeasurements": regional_contact,
            "regionalContactSumMm3": regional_total,
            "omittingUpperRegionLeavesContactMm3": (
                common - regional_contact[0]["commonVolumeMm3"] if len(regional_contact) > 1 else None),
            "contactWithinDeclaredBounds": contact_in_bounds,
            "printComponentMinimumZMm": actual_min_z,
            "expectedPrintComponents": next(iter(expected_components)) if len(expected_components) == 1 else None,
            "heights": support_rows,
            "removalPhysicallyVerified": False,
        }
        if part_id == "housing" and common > .001:
            support_bounds = model.bbox(support)
            z0, z1 = support_bounds[0][2], support_bounds[1][2]
            contact_bins = []
            # Locate material rather than treating zero-thickness appendages
            # in a Boolean boundary as a solid contact bounding box.
            bin_count = 19
            for index in range(bin_count):
                low = z0 + (z1 - z0) * index / bin_count
                high = z0 + (z1 - z0) * (index + 1) / bin_count
                region = box(support_bounds[0][0], support_bounds[1][0],
                    support_bounds[0][1], support_bounds[1][1], low, high,
                    "housing_contact_region")
                region_volume = common_volume(product, region)[0]
                contact_bins.append({"zRangeMm": [low, high], "commonVolumeMm3": region_volume})
                bpy.data.objects.remove(region, do_unlink=True)
            row["contactHeightBins"] = contact_bins
            row["contactHeightBinsSumMm3"] = sum(item["commonVolumeMm3"] for item in contact_bins)
        row["pass"] = (abs(row["supportPresenceVolumeDifferenceMm3"]) <= .001
            and abs(exact_common - common) <= .00001 and contact_in_bounds
            and row["expectedPrintComponents"] == len(actual_min_z)
            and all(abs(z) <= .001 for z in actual_min_z)
            and (not attached or (len(regional_contact) == 2 and
                all(item["commonVolumeMm3"] > .001 for item in regional_contact) and
                row["omittingUpperRegionLeavesContactMm3"] > .001 and
                abs(row["contactHeightBinsSumMm3"] - common) <= .00001)))
        rows.append(row)
        for ob in (product, support, printed):
            bpy.data.objects.remove(ob, do_unlink=True)

    end_hashes = hashes(dependency_paths)
    result = {"model": P.MODEL_ID, "primarySolver": "MANIFOLD", "comparisonSolver": "EXACT",
        "calibration": calibration, "sourceSha256": start_hashes,
        "sourceIntegrity": {"start": start_hashes, "end": end_hashes, "pass": start_hashes == end_hashes},
        "supports": rows,
        "limitations": ["Removal force and surface damage are not verified on printed hardware.",
            "Containment tests support material, not whole-product shape equivalence.",
            "G-code projection is a separate closed-loop support test."],
        "pass": calibration["pass"] and start_hashes == end_hashes and bool(rows)
            and all(row["pass"] for row in rows)}
    target = BUILD / "print_support_geometry.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, target)
    print(json.dumps({"pass": result["pass"], "calibration": calibration,
        "supports": [{key: row[key] for key in ("partId", "pass", "missingSupportVolumeMm3",
            "supportProductCommonVolumeMm3", "contactWithinDeclaredBounds", "printComponentMinimumZMm")}
            for row in rows]}, ensure_ascii=False))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
