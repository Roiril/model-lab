"""Render the real generated meshes, plus a non-exported laptop reference."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "exports" / "laptop-stand-100"
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
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'exports/laptop-stand-100.blend'))
    parts = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if {obj.name for obj in parts} != {'left_body', 'right_body'}:
        raise ValueError('Assembly scene must contain two monolithic support bodies')
    sage = material('Matte warm ivory body', 'bcae94', .65)
    dark = material('Graphite laptop', '2b2723', .55)
    glass_mat = material('Unlit glass', '191512', .32)
    pad_mat = material('Soft protective pads', '59534d', .9)
    keyboard_mat = material('Keyboard reference', '383532', .8)
    paper = material('Studio background', 'f5efe2', .95)
    for obj in parts:
        obj.data.materials.clear()
        obj.data.materials.append(sage)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.world = bpy.data.worlds.new('Studio world')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = rgb('f5efe2')
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .7
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = 'Studio floor'
    ground.data.materials.append(paper)
    for name, position, energy, size in [
        ('Key', (-.4, -.4, .8), 35, .65),
        ('Fill', (.65, -.2, .6), 20, .65),
        ('Rim', (-.2, .55, .75), 30, .6),
    ]:
        data = bpy.data.lights.new(name, 'AREA')
        data.energy = energy
        data.shape = 'DISK'
        data.size = size
        lamp = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(lamp)
        lamp.location = position
        lamp.rotation_euler = (Vector((0, .12, .10)) - lamp.location).to_track_quat('-Z', 'Y').to_euler()
    pads = []
    laptop_z = params.BODY_HEIGHT + 2 * params.PAD_THICKNESS
    for x in (-params.RAIL_CENTER, params.RAIL_CENTER):
        for start in (params.PAD_FRONT_Y, params.PAD_REAR_Y):
            pads.append(box('Non-print upper protective pad',
                            (params.PAD_WIDTH, params.PAD_LENGTH, params.PAD_THICKNESS),
                            (x, start + params.PAD_LENGTH / 2, laptop_z - params.PAD_THICKNESS / 2),
                            pad_mat, .0003))
        for start in (params.BASE_PAD_FRONT_Y, params.BASE_PAD_REAR_Y):
            pads.append(box('Non-print wide anti-slip pad',
                            (params.BASE_PAD_WIDTH, params.BASE_PAD_LENGTH, params.PAD_THICKNESS),
                            (x, start + params.BASE_PAD_LENGTH / 2, params.PAD_THICKNESS / 2),
                            pad_mat, .0003))
    yc = params.FRAME_DEPTH / 2
    laptop = []
    thickness = params.LAPTOP_BASE_THICKNESS
    width, depth = params.LAPTOP_WIDTH, params.LAPTOP_DEPTH
    laptop.append(box('400 x 330mm laptop base reference', (width, depth, thickness),
                      (0, yc, laptop_z + thickness / 2), dark, .0035))
    top_z = laptop_z + thickness
    laptop.append(box('Keyboard area reference', (width - .045, .135, .0008),
                      (0, yc + .041, top_z + .0004), keyboard_mat, .00035))
    laptop.append(box('Trackpad reference', (.12, .073, .0008),
                      (0, yc - .103, top_z + .0004), keyboard_mat, .00035))
    # A generic open lid is illustrative. Its mass and COM are not measured.
    angle = math.radians(15)
    upward = Vector((0, math.sin(angle), math.cos(angle)))
    normal = Vector((0, -math.cos(angle), math.sin(angle)))
    hinge = Vector((0, yc + depth / 2 - .004, top_z))
    display_height = .25
    display_thickness = .008
    pose = Matrix(((1, 0, 0), (0, upward.y, normal.y), (0, upward.z, normal.z)))
    display_center = hinge + upward * (display_height / 2)
    lid = box('Laptop lid reference', (width, display_height, display_thickness), display_center, dark, .003)
    lid.rotation_euler = pose.to_euler()
    laptop.append(lid)
    glass = box('Screen reference', (width - .024, display_height - .024, .0005),
                display_center + normal * (display_thickness / 2 + .0001), glass_mat, .00024)
    glass.rotation_euler = pose.to_euler()
    laptop.append(glass)
    for obj in laptop:
        obj.hide_render = True
    for obj in pads:
        obj.hide_render = True
    camera((.58, -.38, .34), (0, yc, .05), .50)
    render(OUT / 'stand.png')
    for obj in pads:
        obj.hide_render = False
    for obj in laptop:
        obj.hide_render = False
    camera((.72, -.55, .55), (0, yc, .18), .66)
    render(OUT / 'in-use.png')
    camera((.8, yc, .19), (0, yc, .19), .58)
    render(OUT / 'side.png')
    for obj in laptop:
        obj.hide_render = True
    ground.hide_render = True
    camera((.5, -.25, -.34), (0, yc, .045), .5)
    render(OUT / 'underside.png')
    ground.hide_render = False
    for obj in pads:
        obj.hide_render = True
    camera((.58, yc, .18), (0, yc, .05), .50)
    render(OUT / 'sculpture-side.png')
    for obj in parts:
        if obj.name == 'left_body':
            obj.hide_render = True
    camera((.46, -.20, .19), (params.RAIL_CENTER, yc, .05), .33)
    render(OUT / 'flow-detail.png')
    for obj in parts + pads:
        obj.hide_render = True
    bpy.ops.wm.stl_import(filepath=str(OUT / 'body.stl'))
    printing = bpy.context.object
    printing.name = 'One seamless body upright print orientation'
    printing.scale = (.001, .001, .001)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    printing.data.materials.append(sage)
    camera((.40, -.38, .37), (0, 0, .049), .37)
    render(OUT / 'print.png')
    print('PREVIEW_FILES: stand.png in-use.png side.png underside.png sculpture-side.png flow-detail.png print.png')
    print(f'LAPTOP_REFERENCE_MM: {width * 1000:.1f} x {depth * 1000:.1f}')
    print(f'SUPPORT_HEIGHT_WITH_PADS_MM: {laptop_z * 1000:.1f}')


if __name__ == '__main__':
    main()
