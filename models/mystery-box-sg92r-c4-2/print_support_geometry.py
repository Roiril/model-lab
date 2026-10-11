"""C4-2 の印刷専用支持を実STLと閉境界Booleanで照合する。"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


HERE = Path(os.path.abspath(os.path.dirname(__file__)))
ROOT = Path(os.path.abspath(os.path.join(HERE, "../..")))
BUILD = HERE / "build"
LIB = ROOT / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from solid_volume import closed_boundary_volume  # noqa: E402


def load_module(alias: str, path: Path, imports: dict[str, object] | None = None):
    """同名の別モデルを sys.path から拾わず、指定ファイルを別名で読む。"""
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    previous = {}
    for name, dependency in (imports or {}).items():
        previous[name] = sys.modules.get(name)
        sys.modules[name] = dependency
    sys.modules[alias] = module
    try:
        spec.loader.exec_module(module)
    finally:
        for name, dependency in previous.items():
            if dependency is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = dependency
    return module


P = load_module("c42_support_params", HERE / "params.py")
MOTION = load_module("c42_support_motion", HERE / "motion.py", {"params": P})
MODEL = load_module("c42_support_model", HERE / "model.py",
                    {"params": P, "motion": MOTION})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_hashes(paths) -> dict[str, str]:
    rows = {}
    for path in paths:
        path = Path(path)
        key = path.relative_to(ROOT).as_posix()
        rows[key] = sha256(path)
    return rows


def record(path: Path) -> dict[str, str]:
    return {"file": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def object_volume(ob) -> float:
    mesh = bmesh.new()
    mesh.from_mesh(ob.data)
    try:
        if any(not edge.is_manifold for edge in mesh.edges):
            raise ValueError(f"closed volume input is open: {ob.name}")
        return closed_boundary_volume(mesh)
    finally:
        mesh.free()


def component_count(ob) -> int:
    mesh = bmesh.new()
    mesh.from_mesh(ob.data)
    try:
        remaining = set(mesh.verts)
        count = 0
        while remaining:
            count += 1
            pending = [remaining.pop()]
            while pending:
                vertex = pending.pop()
                for edge in vertex.link_edges:
                    other = edge.other_vert(vertex)
                    if other in remaining:
                        remaining.remove(other)
                        pending.append(other)
        return count
    finally:
        mesh.free()


def imported_stl(path: Path, name: str):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    added = set(bpy.data.objects) - before
    if len(added) != 1:
        raise ValueError(f"unexpected STL object count: {path}")
    result = added.pop()
    result.name = name
    return result


def split_loose_objects(source):
    """import済みSTLを辺接続ごとの閉立体へ分ける。"""
    mesh = bmesh.new()
    mesh.from_mesh(source.data)
    try:
        remaining = set(mesh.verts)
        rows = []
        while remaining:
            seed = remaining.pop()
            vertices = [seed]
            pending = [seed]
            while pending:
                vertex = pending.pop()
                for edge in vertex.link_edges:
                    other = edge.other_vert(vertex)
                    if other in remaining:
                        remaining.remove(other)
                        vertices.append(other)
                        pending.append(other)
            faces = {face for vertex in vertices for face in vertex.link_faces}
            index = {vertex: position for position, vertex in enumerate(vertices)}
            data = bpy.data.meshes.new("actual_print_component_mesh")
            data.from_pydata([tuple(vertex.co) for vertex in vertices], [],
                             [[index[vertex] for vertex in face.verts] for face in faces])
            data.update()
            ob = bpy.data.objects.new("actual_print_component", data)
            bpy.context.collection.objects.link(ob)
            rows.append(ob)
        return rows
    finally:
        mesh.free()


def boolean_common(first, second, solver="MANIFOLD") -> dict:
    probe = MODEL.duplicate(first, "support_common_probe")
    cutter = MODEL.duplicate(second, "support_common_cutter")
    try:
        for ob in (probe, cutter):
            mesh = bmesh.new()
            mesh.from_mesh(ob.data)
            try:
                if any(not edge.is_manifold for edge in mesh.edges):
                    raise ValueError(f"Boolean input is not closed: {ob.name}")
            finally:
                mesh.free()
        modifier = probe.modifiers.new("support_intersection", "BOOLEAN")
        modifier.operation = "INTERSECT"
        modifier.solver = solver
        modifier.object = cutter
        bpy.context.view_layer.objects.active = probe
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        mesh = bmesh.new()
        mesh.from_mesh(probe.data)
        try:
            volume = closed_boundary_volume(mesh)
            components = []
            remaining = set(mesh.verts)
            while remaining:
                seed = remaining.pop()
                vertices = [seed]
                pending = [seed]
                while pending:
                    vertex = pending.pop()
                    for edge in vertex.link_edges:
                        other = edge.other_vert(vertex)
                        if other in remaining:
                            remaining.remove(other)
                            vertices.append(other)
                            pending.append(other)
                if vertices:
                    faces = {face for vertex in vertices for face in vertex.link_faces}
                    component = bmesh.new()
                    mapping = {vertex: component.verts.new(vertex.co) for vertex in vertices}
                    for face in faces:
                        component.faces.new([mapping[vertex] for vertex in face.verts])
                    try:
                        component_volume = closed_boundary_volume(component)
                    finally:
                        component.free()
                    components.append({"bboxMm": [
                        [round(min(v.co[axis] for v in vertices), 6) for axis in range(3)],
                        [round(max(v.co[axis] for v in vertices), 6) for axis in range(3)],
                    ], "volumeMm3": round(component_volume, 9)})
        finally:
            mesh.free()
        return {"volumeMm3": round(volume, 9), "componentBoundsMm": components}
    finally:
        for ob in (probe, cutter):
            if ob.name in bpy.data.objects:
                bpy.data.objects.remove(ob, do_unlink=True)


def intersect_object(first, second, name):
    result = MODEL.duplicate(first, name)
    cutter = MODEL.duplicate(second, name + "_cutter")
    modifier = result.modifiers.new(name + "_intersection", "BOOLEAN")
    modifier.operation = "INTERSECT"
    modifier.solver = "MANIFOLD"
    modifier.object = cutter
    bpy.context.view_layer.objects.active = result
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    finally:
        bpy.data.objects.remove(cutter, do_unlink=True)
    return result


def region_band_contact(product, shifted_support, low, high):
    bounds = MODEL.bbox(shifted_support)
    band = MODEL.box(bounds[0][0] - .1, bounds[1][0] + .1,
                     bounds[0][1] - .1, bounds[1][1] + .1,
                     low, high, "declared_contact_band")
    clipped = intersect_object(shifted_support, band, "support_in_declared_band")
    try:
        measured = boolean_common(product, clipped)
    finally:
        bpy.data.objects.remove(clipped, do_unlink=True)
        bpy.data.objects.remove(band, do_unlink=True)
    components = measured["componentBoundsMm"]
    if components:
        actual_min = min(row["bboxMm"][0][2] for row in components)
        actual_max = max(row["bboxMm"][1][2] for row in components)
    else:
        actual_min = actual_max = None
    thickness = high - low
    return {"declaredBandMm": [round(low, 6), round(high, 6)],
            "actualMinZMm": actual_min, "actualMaxZMm": actual_max,
            "volumeMm3": measured["volumeMm3"],
            "horizontalAreaMm2": round(measured["volumeMm3"] / thickness, 9)
                if thickness > 0 else None,
            "components": components}


def independent_first_z(product, support, support_top):
    """支持天面のXY点から上向きrayを打ち、製品下面を独立に測る。"""
    support_mesh = bmesh.new()
    support_mesh.from_mesh(support.data)
    product_mesh = bmesh.new()
    product_mesh.from_mesh(product.data)
    try:
        support_mesh.normal_update()
        samples = []
        for face in support_mesh.faces:
            if (face.normal.z < .9
                    or any(abs(vertex.co.z - support_top) > .002 for vertex in face.verts)):
                continue
            center = face.calc_center_median()
            samples.append(center.copy())
            for edge in face.edges:
                midpoint = (edge.verts[0].co + edge.verts[1].co) * .5
                samples.append(center * .2 + midpoint * .8)
        tree = BVHTree.FromBMesh(product_mesh)
        levels = []
        sample_rows = []
        for point in samples:
            hit = tree.ray_cast(Vector((point.x, point.y, support_top + .0001)),
                                Vector((0, 0, 1)), 200.0)
            level = None if hit[0] is None else round(float(hit[0].z), 6)
            sample_rows.append({"xyMm": [round(point.x, 6), round(point.y, 6)],
                                "firstProductZMm": level})
            if level is not None:
                levels.append(level)
        return {"supportTopZMm": round(support_top, 6),
                "sampleCount": len(samples), "hitCount": len(levels),
                "actualProductFirstZMm": min(levels) if levels else None,
                "actualGapMm": round(min(levels) - support_top, 6) if levels else None,
                "samples": sample_rows}
    finally:
        support_mesh.free()
        product_mesh.free()


def remove_receivers(product, bounds):
    result = MODEL.duplicate(product, "receiver_removed_product")
    for index, component in enumerate(bounds):
        row = component["bboxMm"]
        cutter = MODEL.box(row[0][0] - .02, row[1][0] + .02,
                           row[0][1] - .02, row[1][1] + .02,
                           row[0][2] - .02, row[1][2] + .02,
                           f"receiver_removal_{index}")
        MODEL.cut(result, cutter)
    return result


def binary_stl_components(path: Path) -> dict:
    """binary STLそのものの辺接続を数え、manifest値を参照せず成分を返す。"""
    raw = path.read_bytes()
    if len(raw) < 84:
        raise ValueError(f"STL header is missing: {path}")
    triangle_count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + 50 * triangle_count:
        raise ValueError(f"binary STL byte count mismatch: {path}")
    parent = {}
    bounds = {}
    edge_counts = {}

    def root(value):
        parent.setdefault(value, value)
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def join(first, second):
        a, b = root(first), root(second)
        if a != b:
            parent[b] = a

    for index in range(triangle_count):
        values = struct.unpack_from("<9f", raw, 96 + index * 50)
        vertices = [tuple(values[offset:offset + 3]) for offset in (0, 3, 6)]
        for first, second in ((vertices[0], vertices[1]), (vertices[1], vertices[2]),
                              (vertices[2], vertices[0])):
            edge = tuple(sorted((first, second)))
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
            join(first, second)
    for vertex in parent:
        key = root(vertex)
        if key not in bounds:
            bounds[key] = [[*vertex], [*vertex]]
        else:
            for axis in range(3):
                bounds[key][0][axis] = min(bounds[key][0][axis], vertex[axis])
                bounds[key][1][axis] = max(bounds[key][1][axis], vertex[axis])
    components = [{"bboxMm": [[round(value, 6) for value in row[0]],
                                [round(value, 6) for value in row[1]]],
                   "bedMinZMm": round(row[0][2], 6)} for row in bounds.values()]
    components.sort(key=lambda row: tuple(row["bboxMm"][0] + row["bboxMm"][1]))
    return {"triangleCount": triangle_count,
            "badEdgeCount": sum(count != 2 for count in edge_counts.values()),
            "componentCount": len(components), "components": components}


def bounds_close(first, second, tolerance=.002) -> bool:
    return all(abs(first[side][axis] - second[side][axis]) <= tolerance
               for side in range(2) for axis in range(3))


def matched_component(components, expected):
    matches = [row for row in components if bounds_close(row["bboxMm"], expected)]
    return matches[0] if len(matches) == 1 else None


def matched_object(objects, expected):
    matches = [ob for ob in objects if bounds_close(MODEL.bbox(ob), expected)]
    return matches[0] if len(matches) == 1 else None


def calibration() -> dict:
    MODEL.clear_scene()
    first = MODEL.box(50, 51, 50, 51, 0, 1, "fixture_first")
    overlap = MODEL.box(50.5, 51.5, 50, 51, 0, 1, "fixture_overlap")
    absent = MODEL.box(52, 53, 50, 51, 0, 1, "fixture_absent")
    touching = MODEL.box(51, 52, 50, 51, 0, 1, "fixture_touching")
    thin = MODEL.box(50.99, 51.99, 50, 51, 0, 1, "fixture_thin")
    contained = MODEL.box(50.2, 50.8, 50.2, 50.8, .2, .8, "fixture_contained")
    gap_support = MODEL.box(60, 61, 60, 61, 0, 1, "fixture_gap_support")
    shifted_gap_support = MODEL.duplicate(gap_support, "fixture_shifted_gap_support")
    MODEL.transform(shifted_gap_support, Matrix.Translation((0, 0, .3)))
    gap_product_point_two = MODEL.box(60, 61, 60, 61, 1.2, 2.2,
                                      "fixture_gap_product_point_two")
    gap_product_point_two_five = MODEL.box(60, 61, 60, 61, 1.25, 2.25,
                                           "fixture_gap_product_point_two_five")
    declared_gap = [{"region": "declared_point_two", "support_top_z_mm": 1.0,
                     "product_first_z_mm": 1.2, "material_face_gap_mm": .2}]
    point_two_region = region_evidence(gap_product_point_two, gap_support,
                                       shifted_gap_support, declared_gap)[0]
    point_two_five_region = region_evidence(gap_product_point_two_five, gap_support,
                                            shifted_gap_support, declared_gap)[0]
    rows = {
        "overlapExpectedMm3": .5,
        "overlapManifoldMm3": boolean_common(first, overlap)["volumeMm3"],
        "overlapExactMm3": boolean_common(first, overlap, "EXACT")["volumeMm3"],
        "absentMm3": boolean_common(first, absent)["volumeMm3"],
        "touchingMm3": boolean_common(first, touching)["volumeMm3"],
        "thinExpectedMm3": .01,
        "thinMm3": boolean_common(first, thin)["volumeMm3"],
        "containmentExpectedMm3": .216,
        "containmentMm3": boolean_common(first, contained)["volumeMm3"],
        "declaredPointTwoActualPointTwo": point_two_region,
        "declaredPointTwoActualPointTwoFive": point_two_five_region,
    }
    rows["pass"] = (abs(rows["overlapManifoldMm3"] - .5) <= .00001
                    and abs(rows["overlapExactMm3"] - .5) <= .00001
                    and rows["absentMm3"] <= .00001
                    and rows["touchingMm3"] <= .00001
                    and abs(rows["thinMm3"] - .01) <= .00001
                    and abs(rows["containmentMm3"] - .216) <= .00001
                    and point_two_region["pass"]
                    and not point_two_five_region["pass"])
    MODEL.clear_scene()
    return rows


def product_for_print(part_id: str, assembly_path: Path):
    product = imported_stl(assembly_path, f"expected_product_{part_id}")
    MODEL.place_on_bed(product, MODEL.PRINT_TRANSFORMS[part_id])
    return product


def region_evidence(product, support, shifted_support, regions, positive_shift=.3):
    rows = []
    for region in regions:
        low = float(region["product_first_z_mm"])
        high = float(region["support_top_z_mm"]) + positive_shift
        band = region_band_contact(product, shifted_support, low, high)
        first = independent_first_z(product, support,
                                    float(region["support_top_z_mm"]))
        declared_clearance = float(
            region.get("geometric_clearance_mm")
            or (float(region["product_first_z_mm"])
                - float(region["support_top_z_mm"])))
        band_pass = (band["actualMinZMm"] is not None
                     and abs(band["actualMinZMm"] - low) <= .002
                     and abs(band["actualMaxZMm"] - high) <= .002
                     and band["horizontalAreaMm2"] is not None
                     and band["horizontalAreaMm2"] > .001)
        first_pass = (first["actualProductFirstZMm"] is not None
                      and abs(first["actualProductFirstZMm"] - low) <= .002
                      and abs(first["actualGapMm"] - declared_clearance) <= .002)
        rows.append({**region, "positiveShiftBandContact": band,
                     "independentFirstZ": first,
                     "declaredGeometricClearanceMm": declared_clearance,
                     "bandPass": band_pass, "independentFirstZPass": first_pass,
                     "pass": band_pass and first_pass})
    return rows


def inspect_part(part: dict) -> dict:
    part_id = part["id"]
    MODEL.clear_scene()
    assembly_path = HERE / part["assembly"]
    print_path = HERE / part["print"]
    product = product_for_print(part_id, assembly_path)
    supports = MODEL.build_print_supports(part_id)
    declarations = part["print_supports"]
    if len(supports) != len(declarations):
        raise ValueError(f"support count mismatch: {part_id}")
    printed = imported_stl(print_path, f"actual_print_{part_id}")
    binary = binary_stl_components(print_path)
    actual_objects = split_loose_objects(printed)
    unmatched_objects = set(actual_objects)
    product_volume = object_volume(product)
    print_volume = object_volume(printed)
    support_rows = []
    actual_support_total = 0.0
    expected_support_total = 0.0
    support_symmetric_total = 0.0

    for support, declaration in zip(supports, declarations):
        support_id = declaration["id"]
        generated_name_matches = support.name == support_id
        expected_bbox = MODEL.bbox(support)
        declared_bbox = declaration["bbox_mm"]
        valid_solid = MODEL.nonmanifold(support) == 0 and component_count(support) == 1
        support_volume = object_volume(support) if valid_solid else 0.0
        actual_support = matched_object(unmatched_objects, expected_bbox)
        actual_support_volume = object_volume(actual_support) if actual_support else 0.0
        contained_manifold = (boolean_common(actual_support, support)
                              if actual_support else {"volumeMm3": 0.0,
                                                      "componentBoundsMm": []})
        nominal_manifold = boolean_common(product, support)
        nominal_exact = boolean_common(product, support, "EXACT")
        actual_component = matched_component(binary["components"], expected_bbox)
        if actual_support is not None:
            unmatched_objects.remove(actual_support)
        regions = declaration.get("support_regions") or [{
            "region": support_id,
            "support_top_z_mm": declaration["support_top_z_mm"],
            "product_first_z_mm": declaration["product_first_z_mm"],
            "geometric_clearance_mm": declaration.get("geometric_clearance_mm"),
            "expected_last_support_gcode_z_mm": declaration.get(
                "expected_last_support_gcode_z_mm"),
            "expected_first_product_gcode_z_mm": declaration.get(
                "expected_first_product_gcode_z_mm"),
            "material_face_gap_mm": declaration["material_face_gap_mm"],
        }]
        positive_shift = max(float(
            region.get("geometric_clearance_mm")
            or (float(region["product_first_z_mm"])
                - float(region["support_top_z_mm"])))
            for region in regions) + .1
        shifted = MODEL.duplicate(support, f"{support_id}_positive_shift")
        MODEL.transform(shifted, Matrix.Translation((0, 0, positive_shift)))
        positive = boolean_common(product, shifted)
        receiver_removed = remove_receivers(product, positive["componentBoundsMm"])
        negative = boolean_common(receiver_removed, shifted)
        bpy.data.objects.remove(receiver_removed, do_unlink=True)
        regional = region_evidence(product, support, shifted, regions, positive_shift)
        bpy.data.objects.remove(shifted, do_unlink=True)
        bbox_matches = bounds_close(expected_bbox, declared_bbox)
        containment_difference = (support_volume + actual_support_volume
                                  - 2 * contained_manifold["volumeMm3"])
        accepted = (generated_name_matches and valid_solid and bbox_matches
                    and actual_component is not None
                    and actual_support is not None
                    and (not declaration.get("bed_origin_expected", True)
                         or abs(actual_component["bedMinZMm"]) <= .001)
                    and abs(containment_difference) <= .001
                    and nominal_manifold["volumeMm3"] <= .001
                    and nominal_exact["volumeMm3"] <= .001
                    and abs(nominal_manifold["volumeMm3"]
                            - nominal_exact["volumeMm3"]) <= .00001
                    and positive["volumeMm3"] > .001
                    and negative["volumeMm3"] <= .001
                    and all(row["pass"] for row in regional))
        support_rows.append({
            "id": support_id, "decision": "accepted" if accepted else "rejected",
            "attachment": declaration["attachment"],
            "declaredBboxMm": declared_bbox, "generatedBboxMm": expected_bbox,
            "actualComponent": actual_component,
            "generatedNameMatches": generated_name_matches,
            "closedSolid": valid_solid, "supportVolumeMm3": round(support_volume, 9),
            "actualSupportComponentVolumeMm3": round(actual_support_volume, 9),
            "actualPrintContainmentManifoldMm3": contained_manifold["volumeMm3"],
            "missingSupportVolumeMm3": round(max(0.0, support_volume
                                                  - contained_manifold["volumeMm3"]), 9),
            "unexpectedActualSupportVolumeMm3": round(max(0.0,
                actual_support_volume - contained_manifold["volumeMm3"]), 9),
            "supportContainmentAbsoluteDifferenceMm3": round(
                abs(containment_difference), 9),
            "supportSymmetricDifferenceMm3": round(abs(containment_difference), 9),
            "nominalProductCommonManifoldMm3": nominal_manifold["volumeMm3"],
            "nominalProductCommonExactMm3": nominal_exact["volumeMm3"],
            "positiveShiftMm": round(positive_shift, 6),
            "positiveShiftCommonMm3": positive["volumeMm3"],
            "positiveShiftContactComponents": positive["componentBoundsMm"],
            "receiverRemovedCommonMm3": negative["volumeMm3"],
            "regionalContactEvidence": regional,
            "supportTopZMm": declaration["support_top_z_mm"],
            "productFirstZMm": declaration["product_first_z_mm"],
            "geometricClearanceMm": declaration.get("geometric_clearance_mm"),
            "expectedLastSupportGcodeZMm": declaration.get(
                "expected_last_support_gcode_z_mm"),
            "expectedFirstProductGcodeZMm": declaration.get(
                "expected_first_product_gcode_z_mm"),
            "materialFaceGapMm": declaration["material_face_gap_mm"],
            "bedOriginExpected": declaration.get("bed_origin_expected", True),
        })
        actual_support_total += actual_support_volume
        expected_support_total += support_volume
        support_symmetric_total += abs(containment_difference)

    actual_product = next(iter(unmatched_objects)) if len(unmatched_objects) == 1 else None
    actual_product_volume = object_volume(actual_product) if actual_product else 0.0
    actual_product_manifold = (boolean_common(actual_product, product)
                               if actual_product else {"volumeMm3": 0.0,
                                                       "componentBoundsMm": []})
    product_common = actual_product_manifold["volumeMm3"]
    product_symmetric = abs(product_volume + actual_product_volume - 2 * product_common)
    total_volume_difference = abs(print_volume - product_volume - expected_support_total)
    symmetric_difference = product_symmetric + support_symmetric_total
    expected_count = int(part["expected_print_components"])
    accepted = (binary["badEdgeCount"] == 0
                and binary["componentCount"] == expected_count
                and actual_product is not None
                and product_symmetric <= .001
                and symmetric_difference <= .001
                and total_volume_difference <= .001
                and all(row["decision"] == "accepted" for row in support_rows))
    return {
        "sourceAssemblyStl": record(assembly_path), "sourcePrintStl": record(print_path),
        "expectedComponentCount": expected_count,
        "actualComponentCount": binary["componentCount"],
        "actualBinaryTopology": binary,
        "productVolumeMm3": round(product_volume, 9),
        "actualProductComponentVolumeMm3": round(actual_product_volume, 9),
        "actualPrintVolumeMm3": round(print_volume, 9),
        "actualProductContainmentManifoldMm3": actual_product_manifold["volumeMm3"],
        "expectedProductAndSupportsVolumeMm3": round(product_volume + expected_support_total, 9),
        "actualProductSymmetricDifferenceMm3": round(product_symmetric, 9),
        "allSupportsSymmetricDifferenceMm3": round(support_symmetric_total, 9),
        "actualPrintVolumeResidualMm3": round(total_volume_difference, 9),
        "productSymmetricDifferenceMm3": round(symmetric_difference, 9),
        "supports": support_rows,
        "decision": "accepted" if accepted else "rejected",
    }


def dependency_paths(manifest: dict) -> list[Path]:
    paths = [Path(__file__), HERE / "model.py", HERE / "params.py", HERE / "motion.py",
             BUILD / "manifest.json", LIB / "solid_volume.py",
             LIB / "blender_utils.py", LIB / "printmech" / "geometry.py",
             ROOT / "models" / "sg92r-photo" / "params.py"]
    for part in manifest["parts"]:
        for key in ("assembly", "print"):
            value = part.get(key)
            if value:
                path = HERE / value
                if path not in paths:
                    paths.append(path)
    return paths


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    manifest_path = BUILD / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    measured = [part for part in manifest["parts"] if part.get("print_supports")]
    paths = dependency_paths(manifest)
    start = source_hashes(paths)
    fixture = calibration()
    parts = {part["id"]: inspect_part(part) for part in measured}
    end = source_hashes(paths)
    source_integrity = {"start": start, "end": end, "pass": start == end}
    overall = {"pass": (fixture["pass"] and source_integrity["pass"] and bool(parts)
                           and all(part["decision"] == "accepted"
                                   for part in parts.values()))}
    report = {"model": P.MODEL_ID, "manifest": record(manifest_path),
              "sourceAlgorithmIntegrity": source_integrity,
              "calibration": fixture, "parts": parts, "overall": overall}
    target = BUILD / "print_support_geometry.json"
    temporary = target.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, target)
    print(json.dumps({"output": str(target), "overall": overall,
                      "parts": {name: {"decision": row["decision"],
                                       "symmetricDifferenceMm3": row["productSymmetricDifferenceMm3"],
                                       "components": [row["actualComponentCount"],
                                                      row["expectedComponentCount"]]}
                                for name, row in parts.items()}}, ensure_ascii=False))
    if not overall["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
