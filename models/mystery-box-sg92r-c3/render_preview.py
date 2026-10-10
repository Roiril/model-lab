"""closed / raised / parts の確認画像を同じ投影で作る。"""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
MANIFEST = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
MOTION = json.loads((BUILD / "motion.json").read_text(encoding="utf-8"))


def matrix_from_column(values):
    return Matrix([[values[column * 4 + row] for column in range(4)] for row in range(4)])


def load_stl(path, color):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    ob = (set(bpy.data.objects) - before).pop()
    ob.color = color
    return ob


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def set_camera(objects, filename, parts=False):
    points = [ob.matrix_world @ vertex.co for ob in objects for vertex in ob.data.vertices]
    lo = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
    hi = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
    center = (lo + hi) / 2
    direction = Vector((1.35, -1.55, 1.15)) if not parts else Vector((1.2, -1.4, 1.55))
    bpy.ops.object.camera_add(location=center + direction.normalized() * 300)
    camera = bpy.context.object
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    basis = camera.rotation_euler.to_matrix().transposed()
    projected = [basis @ (point - center) for point in points]
    width = max(point.x for point in projected) - min(point.x for point in projected)
    height = max(point.y for point in projected) - min(point.y for point in projected)
    camera.data.ortho_scale = max(width, height * 1200 / 900) * 1.16
    camera.data.clip_end = 1000
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.background_type = "WORLD"
    scene.world.color = (0.035, 0.042, 0.050)
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(BUILD / filename)
    bpy.ops.render.render(write_still=True)
    print(filename, "bbox", list(lo), list(hi))


def render_assembly(filename, frame):
    clear()
    colors = {
        "shell": (0.68, 0.65, 0.59, 1), "carrier": (0.82, 0.61, 0.25, 1),
        "cam": (0.25, 0.58, 0.65, 1), "drive": (0.78, 0.37, 0.22, 1),
        "ref": (0.12, 0.28, 0.38, 1), "other": (0.48, 0.52, 0.55, 1),
    }
    objects = []
    for part in MANIFEST["parts"]:
        if part.get("fit_only"):
            continue
        name = part["id"]
        group = "carrier" if name.startswith("carrier_") else (
            "cam" if name.startswith("cam") else (
                "drive" if name == "drive_gear" else (
                    "ref" if name.startswith("ref_") else ("shell" if name == "shell" else "other"))))
        ob = load_stl(HERE / part["assembly"], colors[group])
        ob.name = name
        if name in frame.get("transforms", {}):
            ob.matrix_world = matrix_from_column(frame["transforms"][name])
        objects.append(ob)
    set_camera(objects, filename)


def render_parts():
    clear()
    objects = []
    printable = [part for part in MANIFEST["parts"] if part["print"] and not part.get("fit_only")]
    for index, part in enumerate(printable):
        ob = load_stl(HERE / part["print"], (0.66, 0.62, 0.54, 1))
        ob.location.x += (index % 5) * 48
        ob.location.y += (index // 5) * 48
        objects.append(ob)
    set_camera(objects, "parts.png", parts=True)


render_assembly("closed.png", MOTION["frames"][0])
render_assembly("raised.png", MOTION["frames"][-1])
render_parts()
