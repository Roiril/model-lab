"""C3 のサーボから従動歯車までの実接続を拡大描画する。"""
from pathlib import Path
import hashlib
import json
import os
import sys

import bpy
from mathutils import Vector


sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
OUTPUT = BUILD / "drive-detail.png"
REPORT = BUILD / "drive_detail_report.json"
CUT_X = -16.0
FONT = Path("C:/Windows/Fonts/BIZ-UDGothicB.ttc")

PARTS = {
    "shell": ("shell.stl", (0.45, 0.50, 0.56, 1.0)),
    "ref_servo": ("ref_servo.stl", (0.08, 0.20, 0.30, 1.0)),
    "ref_horn": ("ref_horn.stl", (0.96, 0.68, 0.18, 1.0)),
    "drive_gear": ("drive_gear.stl", (0.88, 0.23, 0.12, 1.0)),
    "cam_gear": ("cam_gear.stl", (0.08, 0.58, 0.58, 1.0)),
    "camshaft": ("camshaft.stl", (0.15, 0.40, 0.43, 1.0)),
    "servo_clip": ("servo_clip.stl", (0.53, 0.58, 0.62, 1.0)),
    "drive_bearing_clip": ("drive_bearing_clip.stl", (0.62, 0.66, 0.69, 1.0)),
}


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def load_stl(name, filename, color):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(BUILD / filename))
    obj = (set(bpy.data.objects) - before).pop()
    obj.name = name
    obj.color = color
    return obj


def section_shell(shell):
    bpy.ops.mesh.primitive_cube_add(location=(-58.0, 0.0, 40.0))
    cutter = bpy.context.object
    cutter.name = "shell_section_cutter"
    cutter.dimensions = (84.0, 100.0, 100.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = shell.modifiers.new("section_world_pos_x", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.context.view_layer.objects.active = shell
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def add_camera():
    target = Vector((-1.0, -0.5, 37.0))
    direction = Vector((-1.0, -0.58, 0.34)).normalized()
    bpy.ops.object.camera_add(location=target + direction * 220.0)
    camera = bpy.context.object
    camera.name = "drive_detail_camera"
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 78.0
    camera.data.clip_start = 0.1
    camera.data.clip_end = 500.0
    return camera


def add_label(camera, text, location, color):
    bpy.ops.object.text_add()
    label = bpy.context.object
    label.data.body = text
    if FONT.exists():
        label.data.font = bpy.data.fonts.load(str(FONT), check_existing=True)
    label.data.align_x = "LEFT"
    label.data.align_y = "CENTER"
    label.data.size = 2.25
    label.data.extrude = 0.0
    label.color = color
    label.parent = camera
    label.location = location
    label.rotation_euler = (0.0, 0.0, 0.0)
    return label


def add_legend(camera):
    entries = [
        ("SG92R", PARTS["ref_servo"][1]),
        ("付属ホーン", PARTS["ref_horn"][1]),
        ("30歯 駆動ギア", PARTS["drive_gear"][1]),
        ("30歯 従動ギア", PARTS["cam_gear"][1]),
    ]
    for index, (text, color) in enumerate(entries):
        y = 24.5 - index * 4.2
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        swatch = bpy.context.object
        swatch.name = f"legend_swatch_{index}"
        swatch.dimensions = (2.7, 2.7, 0.12)
        swatch.color = color
        swatch.parent = camera
        swatch.location = (-35.0, y, -12.0)
        swatch.rotation_euler = (0.0, 0.0, 0.0)
        add_label(camera, text, (-32.5, y, -12.0), color)


def configure_render(camera):
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    scene.display.shading.curvature_ridge_factor = 1.6
    scene.display.shading.curvature_valley_factor = 1.2
    scene.display.shading.show_specular_highlight = True
    scene.display.shading.background_type = "WORLD"
    scene.world.color = (0.025, 0.031, 0.040)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(OUTPUT)


clear_scene()
source_hashes = {
    name: hashlib.sha256((BUILD / filename).read_bytes()).hexdigest()
    for name, (filename, _color) in PARTS.items()
}
objects = {}
for name, (filename, color) in PARTS.items():
    objects[name] = load_stl(name, filename, color)
section_shell(objects["shell"])

camera = add_camera()
add_legend(camera)
configure_render(camera)
bpy.ops.render.render(write_still=True)

end_hashes = {
    name: hashlib.sha256((BUILD / filename).read_bytes()).hexdigest()
    for name, (filename, _color) in PARTS.items()
}
if end_hashes != source_hashes:
    raise RuntimeError("assembly STL changed during drive-detail rendering")

manifest = json.loads((BUILD / "manifest.json").read_text(encoding="utf-8"))
assembly_parts = {
    part["id"] for part in manifest["parts"]
    if part.get("assembly") and not part.get("fit_only")
}
report = {
    "version": 1,
    "image": {
        "file": OUTPUT.name,
        "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        "width": 1600,
        "height": 1200,
    },
    "renderScript": {
        "file": Path(__file__).name,
        "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    },
    "section": {
        "part": "shell",
        "removedSide": "world -X",
        "cutXmm": CUT_X,
        "internalPartsOpaque": True,
    },
    "sourceAssemblyStlSha256": source_hashes,
    "omittedParts": sorted(assembly_parts - set(PARTS)),
}
temporary = REPORT.with_name(f".{REPORT.name}.{os.getpid()}.tmp")
try:
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, REPORT)
finally:
    if temporary.exists():
        temporary.unlink()

print(f"output={OUTPUT}")
print(f"report={REPORT}")
print(f"cut_x_mm={CUT_X:.3f}")
for name, (filename, _color) in PARTS.items():
    print(f"{name} sha256={source_hashes[name]}")
