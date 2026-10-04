"""exports のSTLを、参考画像に近い撮り方で描く（./run.sh models/laptop-stand-flow/render_preview.py）。"""
import math
import os
import sys

import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
OUT = os.path.join(ROOT, "exports", "laptop-stand-flow")
os.makedirs(OUT, exist_ok=True)


def srgb(hex_value):
    v = [int(hex_value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v) + (1,)


def material(color, rough):
    mat = bpy.data.materials.new("m")
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = srgb(color)
    bsdf.inputs["Roughness"].default_value = rough
    return mat


def setup(stl, both):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=stl)
    obj = bpy.context.object
    obj.scale = (0.001, 0.001, 0.001)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.data.materials.append(material("e4dccb", 0.85))
    setup_world()
    return obj


def setup_world():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.view_settings.view_transform = "AgX"
    scene.world = bpy.data.worlds.new("w")
    scene.world.use_nodes = True
    bg = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = srgb("b9b4ab")
    bg.inputs["Strength"].default_value = 0.5
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0.12, 0))
    floor = bpy.context.object
    floor.data.materials.append(material("a8a39a", 0.95))
    for name, pos, energy, size in (("key", (0.2, 0.9, 0.7), 40, 0.8), ("fill", (0.9, -0.2, 0.4), 12, 0.9),
                                    ("top", (-0.3, 0.1, 1.0), 14, 1.0)):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.size = size
        lamp = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(lamp)
        lamp.location = pos
        lamp.rotation_euler = (Vector((0, 0.12, 0.06)) - lamp.location).to_track_quat("-Z", "Y").to_euler()


def shoot(name, target, azimuth_deg, elevation_deg, distance, lens=60, width=1500, height=1000):
    scene = bpy.context.scene
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    pos = Vector(target) + Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))) * distance
    data = bpy.data.cameras.new("c")
    data.lens = lens
    cam = bpy.data.objects.new("c", data)
    bpy.context.collection.objects.link(cam)
    cam.location = pos
    cam.rotation_euler = (Vector(target) - pos).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("wrote", scene.render.filepath)


def pair_scene():
    """左右2脚と、印刷しない参考用のノートPC（14インチ相当）を描く。"""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=os.path.join(ROOT, "exports", "laptop-stand-flow.stl"))
    stand = bpy.context.object
    stand.scale = (0.001, 0.001, 0.001)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for poly in stand.data.polygons:
        poly.use_smooth = True
    stand.data.materials.append(material("e4dccb", 0.85))
    return stand


def add_laptop():
    top = 0.1395
    width, depth, thick = 0.312, 0.221, 0.016
    y0 = 0.246 - depth - 0.004
    objs = []
    dark = material("26262a", 0.4)
    bpy.ops.mesh.primitive_cube_add(location=(0, y0 + depth / 2, top + thick / 2))
    base = bpy.context.object
    base.dimensions = (width, depth, thick)
    objs.append(base)
    import math
    bpy.ops.mesh.primitive_cube_add(location=(0, y0 + 0.003, top + thick + 0.1))
    lid = bpy.context.object
    lid.dimensions = (width, 0.006, 0.2)
    lid.location = (0, y0 + 0.003 - 0.0, top + thick + 0.09)
    lid.rotation_euler = (math.radians(-12), 0, 0)
    objs.append(lid)
    for o in objs:
        o.data.materials.append(dark)
    return objs


def main():
    which = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "all"
    if which == "pair":
        pair_scene()
        setup_world()
        shoot("pair", (0, 0.123, 0.07), 38, 16, 0.95, lens=50, width=1500, height=1000)
        add_laptop()
        shoot("in-use", (0, 0.123, 0.09), 18, 9, 1.25, lens=50, width=1500, height=1000)
        return
    setup(os.path.join(ROOT, "exports", "laptop-stand-flow-unit.stl"), False)
    center = (0.0, 0.123, 0.068)
    if which in ("all", "side"):
        shoot("side", center, 0, 6, 0.95, lens=85)
    if which in ("all", "iso"):
        shoot("iso", center, 47, 17, 0.5, lens=50, width=1400, height=1000)
    if which in ("all", "back"):
        shoot("front", (0, 0.123, 0.07), 90, 15, 0.9)
        shoot("top", (0, 0.123, 0.0), 0, 89, 1.3, lens=85)


main()
