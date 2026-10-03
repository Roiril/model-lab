"""Render the real generated mesh, plus a separate non-exported tablet mockup."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "exports" / "tablet-stand-45"
sys.path.insert(0, str(HERE))
import params


def rgb(hex_value):
    values = [int(hex_value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
                 for v in values) + (1,)


def material(name, color, roughness=0.7):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = rgb(color)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = mat.diffuse_color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def box(name, dimensions, center, mat, bevel=0.002):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Rounded edges", "BEVEL")
        mod.width = bevel
        mod.segments = 8
        bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = False
    return obj


def camera(location, target, span, aspect=1.4):
    data = bpy.data.cameras.new("Product view")
    obj = bpy.data.objects.new("Product view", data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    data.type = "ORTHO"
    data.ortho_scale = span
    data.clip_start = 0.001
    data.clip_end = 100
    bpy.context.scene.camera = obj
    bpy.context.view_layer.update()
    visible = [mesh for mesh in bpy.context.scene.objects
               if mesh.type == "MESH" and not mesh.hide_render and mesh.name != "Studio floor"]
    inverse = obj.matrix_world.inverted()
    corners = [inverse @ (mesh.matrix_world @ Vector(corner))
               for mesh in visible for corner in mesh.bound_box]
    if corners:
        xmin, xmax = min(p.x for p in corners), max(p.x for p in corners)
        ymin, ymax = min(p.y for p in corners), max(p.y for p in corners)
        data.ortho_scale = max(span, (xmax - xmin) * 1.16, (ymax - ymin) * aspect * 1.16)
        adjustment = obj.rotation_euler.to_matrix() @ Vector(((xmin + xmax) / 2, (ymin + ymax) / 2, 0))
        obj.location += adjustment
    return obj


def render(path, width=1400, height=1000):
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / "exports" / "tablet-stand-45.blend"))
    stand = next(obj for obj in bpy.context.scene.objects if obj.type == "MESH")
    stand.name = "Tablet stand"
    stand.data.materials.clear()
    # The report tokens supply neutral background and muted material colors.
    stand.data.materials.append(material("Matte sage", "526c61", 0.78))
    dark = material("Soft dark tablet", "2b2723", 0.5)
    screen = material("Unlit screen", "191512", 0.3)
    paper = material("Background", "f5efe2", 0.95)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world = bpy.data.worlds.new("Studio background")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = rgb("f5efe2")
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.0015))
    ground = bpy.context.object
    ground.name = "Studio floor"
    ground.data.materials.append(paper)
    for name, position, energy, size in [
        ("Key", (-0.25, -0.25, 0.55), 14, 0.45),
        ("Fill", (0.45, -0.05, 0.30), 7, 0.45),
        ("Rim", (-0.12, 0.40, 0.38), 11, 0.35),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        lamp = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(lamp)
        lamp.location = position
        lamp.rotation_euler = (Vector((0, 0.10, 0.06)) - lamp.location).to_track_quat("-Z", "Y").to_euler()
    angle = math.radians(params.ANGLE_DEG)
    u = Vector((0, math.cos(angle), math.sin(angle)))
    n = Vector((0, -math.sin(angle), math.cos(angle)))
    origin = Vector((0, params.SEAT_Y, params.SEAT_Z))
    width, height, thickness = 0.3264, 0.2086, 0.014
    pose = Matrix(((1, 0, 0), (0, u.y, n.y), (0, u.z, n.z)))
    center = origin + u * (height / 2 + 0.001) + n * (thickness / 2 + 0.001)
    tablet = box("14.6 inch landscape reference", (width, height, thickness), center, dark, 0.003)
    tablet.rotation_euler = pose.to_euler()
    glass = box("Screen reference", (width - 0.017, height - 0.017, 0.0005),
                center + n * (thickness / 2 + 0.0001), screen, 0.00024)
    glass.rotation_euler = pose.to_euler()
    tablet.hide_render = True
    glass.hide_render = True
    # A little above the front-right exposes the lip, deck and side opening together.
    camera((0.48, -0.30, 0.31), (0, 0.112, 0.067), 0.39)
    render(OUT / "stand.png")
    tablet.hide_render = False
    glass.hide_render = False
    camera((0.50, -0.36, 0.36), (0, 0.11, 0.083), 0.45)
    render(OUT / "in-use.png")
    camera((0.5, 0.12, 0.095), (0, 0.12, 0.095), 0.36)
    render(OUT / "side.png")
    tablet.hide_render = True
    glass.hide_render = True
    ground.hide_render = True
    camera((0.40, -0.18, -0.25), (0, 0.10, 0.05), 0.39)
    render(OUT / "underside.png")
    ground.hide_render = False
    stand.hide_render = True
    bpy.ops.wm.stl_import(filepath=str(OUT / "print.stl"))
    printing = bpy.context.object
    printing.name = "Side-down print orientation"
    printing.scale = (0.001, 0.001, 0.001)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    printing.data.materials.append(stand.data.materials[0])
    bounds = [printing.matrix_world @ Vector(corner) for corner in printing.bound_box]
    lo = Vector(tuple(min(point[i] for point in bounds) for i in range(3)))
    hi = Vector(tuple(max(point[i] for point in bounds) for i in range(3)))
    target = (lo + hi) / 2
    camera(target + Vector((0.45, -0.40, 0.32)), target, 0.39)
    render(OUT / "print.png")
    print("PREVIEW_FILES: stand.png in-use.png side.png underside.png print.png")
    print(f"TABLET_REFERENCE_MM: {width * 1000:.1f} x {height * 1000:.1f} x {thickness * 1000:.1f}")


if __name__ == "__main__":
    main()
