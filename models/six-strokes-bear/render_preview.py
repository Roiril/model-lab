# -*- coding: utf-8 -*-
"""俯瞰セットと協力プレイ例をレンダし、目視確認用 PNG を出力する。"""
from __future__ import annotations

import math
import os

import bpy
import mathutils


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "six-strokes-bear"))
GLB = os.path.join(OUT, "glb")


def reset() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for blocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.images,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(blocks):
            blocks.remove(block)


def mesh_bounds() -> tuple[mathutils.Vector, mathutils.Vector]:
    minimum = mathutils.Vector((1e9, 1e9, 1e9))
    maximum = mathutils.Vector((-1e9, -1e9, -1e9))
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            world = obj.matrix_world @ mathutils.Vector(corner)
            minimum = mathutils.Vector(tuple(min(minimum[i], world[i]) for i in range(3)))
            maximum = mathutils.Vector(tuple(max(maximum[i], world[i]) for i in range(3)))
    return minimum, maximum


def add_ground(center: mathutils.Vector, span: mathutils.Vector) -> None:
    size = max(span.x, span.y) * 4
    bpy.ops.mesh.primitive_plane_add(size=size, location=(center.x, center.y, -0.0012))
    ground = bpy.context.active_object
    ground.name = "ground"
    material = bpy.data.materials.new("ground_mat")
    material.diffuse_color = (0.94, 0.91, 0.84, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.94, 0.91, 0.84, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.96
    ground.data.materials.append(material)


def add_lighting(center: mathutils.Vector, span: mathutils.Vector) -> None:
    radius = max(span.x, span.y)
    key_data = bpy.data.lights.new("key", "AREA")
    key_data.energy = 7
    key_data.shape = "DISK"
    key_data.size = radius * 1.25
    key = bpy.data.objects.new("key", key_data)
    bpy.context.collection.objects.link(key)
    key.location = (center.x - radius * 0.45, center.y - radius * 0.55, radius * 1.35)

    fill_data = bpy.data.lights.new("fill", "AREA")
    fill_data.energy = 2
    fill_data.size = radius * 1.8
    fill = bpy.data.objects.new("fill", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = (center.x + radius * 0.55, center.y + radius * 0.35, radius * 1.0)

    world = bpy.data.worlds.new("paper_world")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (0.955, 0.93, 0.875, 1.0)
    background.inputs[1].default_value = 0.28


def add_camera(
    center: mathutils.Vector,
    span: mathutils.Vector,
    elevation_deg: float = 58,
    azimuth_deg: float = -10,
    margin: float = 1.20,
) -> None:
    data = bpy.data.cameras.new("camera")
    camera = bpy.data.objects.new("camera", data)
    bpy.context.collection.objects.link(camera)
    data.lens = 52
    elevation = math.radians(elevation_deg)
    azimuth = math.radians(azimuth_deg)
    fov = 2 * math.atan(0.5 * data.sensor_width / data.lens)
    fit = max(span.x, span.y * math.sin(elevation))
    distance = (fit * 0.5) / math.tan(fov * 0.5) * margin
    camera.location = (
        center.x + distance * math.cos(elevation) * math.sin(azimuth),
        center.y - distance * math.cos(elevation) * math.cos(azimuth),
        center.z + distance * math.sin(elevation),
    )
    look = mathutils.Vector((center.x, center.y, center.z * 0.25))
    camera.rotation_euler = (look - camera.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera


def configure_render(path: str, width: int, height: int) -> None:
    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    scene.view_settings.exposure = -0.35
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("rendered:", path)


def import_group(path: str) -> list[bpy.types.Object]:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [obj for obj in bpy.data.objects if obj not in before]


def place_group(objects: list[bpy.types.Object], x: float, y: float, z: float = 0.0, rot_z: float = 0.0) -> None:
    c, s = math.cos(rot_z), math.sin(rot_z)
    for obj in objects:
        ox, oy, oz = obj.location
        obj.location = (x + c * ox - s * oy, y + s * ox + c * oy, z + oz)
        obj.rotation_euler.z += rot_z


# ---------------------------------------------------------------- 俯瞰
reset()
bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, "six-strokes-bear.glb"))
minimum, maximum = mesh_bounds()
center = (minimum + maximum) / 2
span = maximum - minimum
add_ground(center, span)
add_lighting(center, span)
add_camera(center, span, elevation_deg=61, azimuth_deg=-8, margin=1.38)
configure_render(os.path.join(OUT, "_preview.png"), 1800, 1250)


# -------------------------------------------------------------- 協力ヒーロー
reset()
place_group(import_group(os.path.join(GLB, "sheet_sleepy_demo.glb")), -0.105, 0.015, rot_z=-0.025)
place_group(import_group(os.path.join(GLB, "role_circle.glb")), 0.035, 0.060, rot_z=-0.05)
place_group(import_group(os.path.join(GLB, "role_segment.glb")), 0.115, 0.060, rot_z=0.05)
place_group(import_group(os.path.join(GLB, "achievement_card.glb")), 0.075, -0.070)
for component, x, y in [
    ("stroke_circle", 0.010, -0.125),
    ("stroke_circle", 0.052, -0.125),
    ("stroke_oval", 0.103, -0.125),
    ("stroke_straight", 0.010, -0.170),
    ("stroke_straight", 0.062, -0.170),
    ("stroke_bend", 0.116, -0.170),
    ("achievement_token", 0.015, -0.215),
    ("achievement_token", 0.057, -0.215),
    ("achievement_token", 0.099, -0.215),
]:
    place_group(import_group(os.path.join(GLB, component + ".glb")), x, y)
minimum, maximum = mesh_bounds()
center = (minimum + maximum) / 2
span = maximum - minimum
add_ground(center, span)
add_lighting(center, span)
add_camera(center, span, elevation_deg=57, azimuth_deg=-12, margin=1.40)
configure_render(os.path.join(OUT, "_hero.png"), 1600, 1250)

print("DONE previews")
