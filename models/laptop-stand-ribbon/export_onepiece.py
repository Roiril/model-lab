"""肩をつないだモデルから、横置きの一体印刷候補を生成する。"""
import json
import hashlib
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
from mathutils import Matrix
from blender_utils import clear_scene, export_stl
from params import MODEL_NAME
from verify import read_binary_stl, inspect_triangles, inspect_overhangs, calibrate

OUT = ROOT / "exports" / MODEL_NAME / "onepiece"


def mesh_triangles(obj):
    obj.data.calc_loop_triangles()
    return np.array([[obj.data.vertices[i].co[:] for i in face.vertices]
                     for face in obj.data.loop_triangles], dtype=float)


def duplicate(obj, name):
    copied = obj.copy()
    copied.data = obj.data.copy()
    copied.name = name
    bpy.context.collection.objects.link(copied)
    return copied


def export_single(name, obj):
    detached = [(other, tuple(other.users_collection))
                for other in bpy.context.scene.objects if other != obj]
    try:
        for other, collections in detached:
            for collection in collections:
                collection.objects.unlink(other)
        return export_stl(name, only=[obj])
    finally:
        for other, collections in detached:
            for collection in collections:
                collection.objects.link(other)


def flatten_one_side():
    clear_scene()
    source_path = ROOT / "exports" / (MODEL_NAME + ".stl")
    read_binary_stl(source_path)  # 入力を先に独立して確認する。
    bpy.ops.wm.stl_import(filepath=str(source_path))
    obj = bpy.context.object
    obj.scale = (.001,) * 3
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # 元の左右半分を幅2倍へ変形する。片側が平面になり、反対側は曲面を保つ。
    cut_x = -.000001  # 0.001mmだけ中心より外へ置き、既存頂点との一致を避ける。
    bpy.ops.mesh.primitive_cube_add(size=1, location=(.5 + cut_x, .14, .08))
    cutter = bpy.context.object
    cutter.dimensions = (1, 1, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new("Centre plane", "BOOLEAN")
    modifier.operation = "INTERSECT"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    for vertex in obj.data.vertices:
        vertex.co.x = 2 * (vertex.co.x - cut_x)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if not bm.verts or any(not edge.is_manifold for edge in bm.edges):
        raise ValueError("One-sided mesh is not closed")
    bm.to_mesh(obj.data)
    bm.free()
    obj.name = "One curved side and one flat side"
    return obj


def print_rotation(obj):
    # 使用姿勢のxを印刷高さzへ移す。整数の行列で底面の誤差を避ける。
    rotation = Matrix(((0, 1, 0), (0, 0, 1), (1, 0, 0)))
    for vertex in obj.data.vertices:
        vertex.co = rotation @ vertex.co
    triangles = mesh_triangles(obj)
    xy = np.unique(triangles[:, :, :2].reshape(-1, 2), axis=0)
    best = None
    for angle in np.linspace(0, math.pi / 2, 901):
        matrix = np.array([[math.cos(angle), -math.sin(angle)],
                           [math.sin(angle), math.cos(angle)]])
        sizes = np.ptp(xy @ matrix, axis=0)
        if best is None or sizes.max() < best[0]:
            best = (float(sizes.max()), angle)
    rotation_z = Matrix.Rotation(-best[1], 3, "Z")
    for vertex in obj.data.vertices:
        vertex.co = rotation_z @ vertex.co
    vertices = [vertex.co for vertex in obj.data.vertices]
    centre_x = (min(v.x for v in vertices) + max(v.x for v in vertices)) / 2
    centre_y = (min(v.y for v in vertices) + max(v.y for v in vertices)) / 2
    bottom = min(v.z for v in vertices)
    for vertex in obj.data.vertices:
        vertex.co.x -= centre_x
        vertex.co.y -= centre_y
        vertex.co.z -= bottom
    obj.data.update()
    return best


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    calibration = calibrate()
    source_path = ROOT / "exports" / (MODEL_NAME + ".stl")
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    original = flatten_one_side()
    usage_dimensions = np.ptp(mesh_triangles(original), axis=(0, 1)) * 1000
    usage_path = export_single(MODEL_NAME + "/onepiece/usage-full", original)
    usage_mesh = inspect_triangles(read_binary_stl(Path(usage_path)))
    source_mesh = inspect_triangles(read_binary_stl(ROOT / "exports" / (MODEL_NAME + ".stl")))
    candidate = duplicate(original, "Print full size")
    bed_size, angle = print_rotation(candidate)
    scale_256 = min(1.0, .246 / bed_size)  # 各側5mmブリムの範囲を残す。
    records = {}
    for name, scale in (("print-full", 1.0), ("print-256", scale_256)):
        piece = duplicate(candidate, name)
        for vertex in piece.data.vertices:
            vertex.co *= scale
        piece.data.update()
        destination = export_single(MODEL_NAME + "/onepiece/" + name, piece)
        triangles = read_binary_stl(Path(destination))
        checked = inspect_triangles(triangles, require_overhangs=True)
        dimensions = np.ptp(triangles, axis=(0, 1))
        if name == "print-256" and dimensions[:2].max() + 10 > 256.001:
            raise ValueError("The 256 mm version does not fit its bed")
        records[name] = {
            "scale": scale,
            "usage_dimensions_mm": (usage_dimensions * scale).tolist(),
            "print_dimensions_mm": dimensions.tolist(),
            "required_square_bed_with_5mm_brim_mm": float(dimensions[:2].max() + 10),
            "mesh": checked,
            "overhangs": inspect_overhangs(triangles),
        }
    report = {
        "source_stl_sha256": source_hash,
        "calibration": calibration,
        "construction": "One piece, flat left side, curved right side; rail is offset to flat side",
        "bed_rotation_deg": math.degrees(angle),
        "load_tested": False,
        "slicer_and_physical_print_tested": False,
        "usage_mesh": usage_mesh,
        "onepiece_to_source_volume_ratio": usage_mesh["signed_volume_cm3"] / source_mesh["signed_volume_cm3"],
        "variants": records,
    }
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != source_hash:
        raise ValueError("Source STL changed while creating print versions")
    temporary = OUT / "verification.json.tmp"
    temporary.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    temporary.replace(OUT / "verification.json")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
