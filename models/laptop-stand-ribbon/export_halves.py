"""完成STLを幅中央で左右に分け、使用姿勢と原寸の印刷姿勢を出力する。"""
import hashlib
import json
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(HERE))

import bpy
import bmesh
import numpy as np
from mathutils import Vector

from blender_utils import clear_scene, export_stl
from export_onepiece import duplicate, export_single
from params import MODEL_NAME
from verify import calibrate, inspect_triangles, read_binary_stl


SOURCE = ROOT / "exports" / f"{MODEL_NAME}.stl"
OUT = ROOT / "exports" / MODEL_NAME / "halves"
SEAM_OVERLAP_M = 0.000001  # Booleanの退化を避ける片側1umの重ね幅。
SEAM_SNAP_M = SEAM_OVERLAP_M + 1e-9
CUT_TOLERANCE_MM = 0.0001
RATIO_TOLERANCE = 1e-4
ROUNDING_FACE_AREA_M2 = 1e-15
DOWNWARD_MICRO_FACE_AREA_M2 = 1e-10


def import_source():
    before = set(bpy.context.scene.objects)
    bpy.ops.wm.stl_import(filepath=str(SOURCE))
    imported = list(set(bpy.context.scene.objects) - before)
    if len(imported) != 1:
        raise ValueError(f"STLの読み込み結果が1オブジェクトではありません: {len(imported)}")
    obj = imported[0]
    obj.name = "Source millimetre STL"
    obj.scale = (0.001,) * 3
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def apply_intersection(obj, low_x, high_x, name):
    centre_x = (low_x + high_x) / 2
    dimensions = (high_x - low_x, 1.0, 1.0)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(centre_x, 0.14, 0.08))
    cutter = bpy.context.object
    cutter.name = name
    cutter.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new("Centre split", "BOOLEAN")
    modifier.operation = "INTERSECT"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def finish_half(obj, side):
    for vertex in obj.data.vertices:
        if abs(vertex.co.x) <= SEAM_SNAP_M:
            vertex.co.x = 0.0
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-9)
    bmesh.ops.triangulate(
        bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="EAR_CLIP"
    )
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if not bm.verts or any(not edge.is_manifold for edge in bm.edges):
        raise ValueError(f"{side}半分が閉じていません")
    if bm.calc_volume(signed=True) <= 0:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    obj.name = f"Usage {side} half"


def split_source(source):
    source_low = min(vertex.co.x for vertex in source.data.vertices)
    source_high = max(vertex.co.x for vertex in source.data.vertices)
    halves = {}
    for side, low_x, high_x in (
        ("left", source_low - 0.01, SEAM_OVERLAP_M),
        ("right", -SEAM_OVERLAP_M, source_high + 0.01),
    ):
        piece = duplicate(source, f"{side} half")
        apply_intersection(piece, low_x, high_x, f"{side} half volume")
        finish_half(piece, side)
        halves[side] = piece
    bpy.data.objects.remove(source, do_unlink=True)
    return halves


def convex_hull(points):
    points = sorted(set(map(tuple, np.asarray(points, dtype=float))))
    if len(points) <= 1:
        return np.asarray(points, dtype=float)

    def cross(origin, first, second):
        return ((first[0] - origin[0]) * (second[1] - origin[1])
                - (first[1] - origin[1]) * (second[0] - origin[0]))

    lower = []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return np.asarray(lower[:-1] + upper[:-1], dtype=float)


def orient_for_print(obj, side):
    for vertex in obj.data.vertices:
        x, y, z = vertex.co
        vertex.co = (y, z, x) if side == "right" else (y, -z, -x)
    obj.data.update()

    hull = convex_hull([(vertex.co.x, vertex.co.y) for vertex in obj.data.vertices])
    best = None
    for angle in np.linspace(0, math.pi / 2, 901):
        cosine, sine = math.cos(angle), math.sin(angle)
        rotation = np.array(((cosine, -sine), (sine, cosine)))
        sizes = np.ptp(hull @ rotation.T, axis=0)
        score = (float(sizes.max()), float(np.prod(sizes)), angle)
        if best is None or score < best[0]:
            best = (score, angle)
    angle = best[1]
    cosine, sine = math.cos(angle), math.sin(angle)
    for vertex in obj.data.vertices:
        x, y = vertex.co.x, vertex.co.y
        vertex.co.x = cosine * x - sine * y
        vertex.co.y = sine * x + cosine * y

    low = [min(vertex.co[axis] for vertex in obj.data.vertices) for axis in range(3)]
    high = [max(vertex.co[axis] for vertex in obj.data.vertices) for axis in range(3)]
    offset = Vector((-(low[0] + high[0]) / 2, -(low[1] + high[1]) / 2, -low[2]))
    for vertex in obj.data.vertices:
        vertex.co += offset
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.dissolve_limit(
        bm,
        angle_limit=1e-7,
        use_dissolve_boundaries=True,
        verts=list(bm.verts),
        edges=list(bm.edges),
    )
    bmesh.ops.dissolve_degenerate(bm, dist=1e-10, edges=list(bm.edges))
    bmesh.ops.triangulate(
        bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="EAR_CLIP"
    )
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    for _ in range(12):
        bad_faces = []
        for face in bm.faces:
            exported = np.asarray(
                [[coordinate * 1000 for coordinate in vertex.co]
                 for vertex in face.verts],
                dtype=np.float32,
            ).astype(np.float64)
            cross = np.cross(exported[1] - exported[0], exported[2] - exported[0])
            area_mm2 = np.linalg.norm(cross) / 2
            on_bed = bool(np.all(np.abs(exported[:, 2]) <= 0.001))
            horizontal = np.linalg.norm(cross[:2])
            downward_angle = (
                math.degrees(math.atan2(-cross[2], horizontal))
                if cross[2] < 0 else 0.0
            )
            if (area_mm2 <= ROUNDING_FACE_AREA_M2 * 1e6
                    or (not on_bed and downward_angle > 45.00001
                        and area_mm2 <= DOWNWARD_MICRO_FACE_AREA_M2 * 1e6)):
                bad_faces.append(face)
        if not bad_faces:
            break
        dissolve = set()
        for face in bad_faces:
            vertices = list(face.verts)
            middle = min(
                vertices,
                key=lambda vertex: (
                    (vertices[(vertices.index(vertex) + 1) % 3].co - vertex.co).normalized()
                    .dot((vertices[(vertices.index(vertex) + 2) % 3].co - vertex.co).normalized())
                ),
            )
            dissolve.add(middle)
        bmesh.ops.dissolve_verts(
            bm,
            verts=list(dissolve),
            use_face_split=False,
            use_boundary_tear=False,
        )
        bmesh.ops.triangulate(
            bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="EAR_CLIP"
        )
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if any(not edge.is_manifold for edge in bm.edges):
        raise ValueError(f"{side}印刷姿勢のメッシュが閉じていません")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return math.degrees(angle)


def cut_area_mm2(triangles):
    triangles = np.asarray(triangles, dtype=np.float64)
    on_plane = np.all(np.abs(triangles[:, :, 0]) <= CUT_TOLERANCE_MM, axis=1)
    selected = triangles[on_plane]
    cross = np.cross(selected[:, 1] - selected[:, 0], selected[:, 2] - selected[:, 0])
    return float(np.linalg.norm(cross, axis=1).sum() / 2), int(on_plane.sum())


def object_bounds(objects):
    points = [obj.matrix_world @ vertex.co for obj in objects for vertex in obj.data.vertices]
    low = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
    high = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
    return low, high


def render(objects, destination, camera_direction):
    # 複製部品の配置をmatrix_worldへ反映してから画角を決める。
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.055, 0.055, 0.055)
    objects[0].color = (0.16, 0.52, 0.86, 1)
    objects[1].color = (0.92, 0.43, 0.12, 1)

    low, high = object_bounds(objects)
    target = (low + high) / 2
    camera_data = bpy.data.cameras.new(destination.stem + " camera")
    camera_data.type = "ORTHO"
    camera = bpy.data.objects.new(destination.stem + " camera", camera_data)
    bpy.context.collection.objects.link(camera)
    direction = Vector(camera_direction).normalized()
    camera.location = target + direction
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    right = camera.rotation_euler.to_matrix() @ Vector((1, 0, 0))
    up = camera.rotation_euler.to_matrix() @ Vector((0, 1, 0))
    points = [obj.matrix_world @ vertex.co for obj in objects for vertex in obj.data.vertices]
    projected_x = [point.dot(right) for point in points]
    projected_y = [point.dot(up) for point in points]
    target += right * ((max(projected_x) + min(projected_x)) / 2 - target.dot(right))
    target += up * ((max(projected_y) + min(projected_y)) / 2 - target.dot(up))
    camera.location = target + direction
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    x_span = max(projected_x) - min(projected_x)
    y_span = max(projected_y) - min(projected_y)
    camera_data.ortho_scale = max(x_span, y_span * 1.5) * 1.15
    scene.camera = camera
    scene.render.filepath = str(destination)
    hidden = [(obj, obj.hide_render) for obj in scene.objects
              if obj.type == "MESH" and obj not in objects]
    for obj, _ in hidden:
        obj.hide_render = True
    try:
        bpy.ops.render.render(write_still=True)
    finally:
        for obj, was_hidden in hidden:
            obj.hide_render = was_hidden
    bpy.data.objects.remove(camera, do_unlink=True)


def render_parts(print_halves):
    copies = [duplicate(print_halves[side], f"Render print {side}")
              for side in ("left", "right")]
    gap = 0.025
    copies[0].location.x = -(copies[0].dimensions.x + gap) / 2
    copies[1].location.x = (copies[1].dimensions.x + gap) / 2
    render(copies, OUT / "parts.png", (0.55, -0.75, 0.5))
    for obj in copies:
        bpy.data.objects.remove(obj, do_unlink=True)


def render_assembly(usage_halves):
    copies = [duplicate(usage_halves[side], f"Render usage {side}")
              for side in ("left", "right")]
    copies[0].location.x = -0.012
    copies[1].location.x = 0.012
    render(copies, OUT / "assembly-split.png", (0.65, -0.75, 0.42))
    for obj in copies:
        bpy.data.objects.remove(obj, do_unlink=True)


def main():
    clear_scene()
    OUT.mkdir(parents=True, exist_ok=True)
    calibration = calibrate()
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    source_triangles = read_binary_stl(SOURCE)
    source_mesh = inspect_triangles(source_triangles)

    usage_halves = split_source(import_source())
    usage_records = {}
    usage_triangles = {}
    for side, obj in usage_halves.items():
        path = Path(export_single(f"{MODEL_NAME}/halves/usage-{side}", obj))
        triangles = read_binary_stl(path)
        mesh = inspect_triangles(triangles)
        low, high = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        if side == "left" and (abs(high[0]) > CUT_TOLERANCE_MM or low[0] >= -41.0):
            raise ValueError(f"左半分のx範囲が不正です: {low[0]}, {high[0]} mm")
        if side == "right" and (abs(low[0]) > CUT_TOLERANCE_MM or high[0] <= 41.0):
            raise ValueError(f"右半分のx範囲が不正です: {low[0]}, {high[0]} mm")
        if not 41.0 <= high[0] - low[0] <= 44.0:
            raise ValueError(f"{side}半分の幅が約42.5 mmではありません: {high[0]-low[0]}")
        area, cut_triangles = cut_area_mm2(triangles)
        usage_triangles[side] = triangles
        usage_records[side] = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "mesh": mesh,
            "x_range_mm": [float(low[0]), float(high[0])],
            "cut_face_area_mm2": area,
            "cut_face_triangles": cut_triangles,
        }

    volume_sum = sum(record["mesh"]["signed_volume_cm3"]
                     for record in usage_records.values())
    volume_ratio = volume_sum / source_mesh["signed_volume_cm3"]
    if abs(volume_ratio - 1.0) > RATIO_TOLERANCE:
        raise ValueError(f"左右体積和と元体積の比が不正です: {volume_ratio}")
    left_area = usage_records["left"]["cut_face_area_mm2"]
    right_area = usage_records["right"]["cut_face_area_mm2"]
    area_relative_difference = abs(left_area - right_area) / max(left_area, right_area)
    if area_relative_difference > RATIO_TOLERANCE:
        raise ValueError(f"左右切断面積の差が大きすぎます: {area_relative_difference}")

    print_halves = {}
    print_records = {}
    for side, usage in usage_halves.items():
        obj = duplicate(usage, f"Print {side} half")
        angle = orient_for_print(obj, side)
        path = Path(export_single(f"{MODEL_NAME}/halves/print-{side}", obj))
        triangles = read_binary_stl(path)
        mesh = inspect_triangles(triangles, require_overhangs=True)
        dimensions = np.ptp(triangles, axis=(0, 1))
        print_halves[side] = obj
        print_records[side] = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "integer_transform": "(y,-z,-x)" if side == "left" else "(y,z,x)",
            "bed_rotation_deg": angle,
            "dimensions_mm": dimensions.tolist(),
            "minimum_square_bed_mm": float(dimensions[:2].max()),
            "required_square_bed_with_5mm_brim_mm": float(dimensions[:2].max() + 10),
            "mesh": mesh,
            "over_45deg_triangles": mesh["overhangs"]["over_45deg_triangles"],
        }

    render_parts(print_halves)
    render_assembly(usage_halves)
    report = {
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_stl_sha256": source_hash,
        "calibration": calibration,
        "construction": "Full-size left and right halves split at usage x=0",
        "seam_overlap_before_snap_um_per_side": SEAM_OVERLAP_M * 1e6,
        "source_mesh": source_mesh,
        "usage": usage_records,
        "volume_sum_to_source_ratio": volume_ratio,
        "cut_face_area_relative_difference": area_relative_difference,
        "print": print_records,
        "renders": ["parts.png", "assembly-split.png"],
        "scaled": False,
    }
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != source_hash:
        raise ValueError("Source STL changed while creating halves")
    temporary = OUT / "verification.json.tmp"
    temporary.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(OUT / "verification.json")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
