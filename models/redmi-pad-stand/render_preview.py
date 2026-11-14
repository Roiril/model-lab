"""書き出した STL をそのまま描く。本体（タブレット）は描画用の箱で、書き出しには入らない。

使い方:
  blender --background --python models/redmi-pad-stand/render_preview.py -- <出力フォルダ>
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import params as P
import stand_profile as prof

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else Path("G:/マイドライブ/shubie/renders/2026-11-14_redmi-pad-stand")
MM = 0.001


def rgb(hex_value):
    values = [int(hex_value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values) + (1,)


def material(name, color, roughness=0.7):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = rgb(color)
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = mat.diffuse_color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def rounded_box(name, dims, mat, bevel):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = obj.modifiers.new("round", "BEVEL")
    mod.width = bevel
    mod.segments = 6
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.append(mat)
    return obj


def tablet(dark, screen):
    """背面下端を受け口の奥の隅 S0 に合わせて置く。"""
    s0, u2, n2 = prof.frame()
    u = Vector((0, u2[0], u2[1]))
    n = Vector((0, n2[0], n2[1]))
    w, h = P.TABLET_W_MM, P.TABLET_H_MM  # 横置き専用
    t = P.TABLET_T_MM
    origin = Vector((0, s0[0], s0[1]))
    center = (origin + u * (h / 2) + n * (t / 2)) * MM
    pose = Matrix(((1, 0, 0), (0, u.y, n.y), (0, u.z, n.z))).to_euler()
    body = rounded_box("Tablet", (w * MM, h * MM, t * MM), dark, 0.0025)
    body.location = center
    body.rotation_euler = pose
    bezel = 2 * P.TABLET_BEZEL_MM
    glass = rounded_box("Screen", ((w - bezel) * MM, (h - bezel) * MM, 0.0004), screen, 0.0001)
    glass.location = center + n * (t / 2 + 0.05) * MM
    glass.rotation_euler = pose
    return [body, glass]


def camera(direction, span_pad=1.12, aspect=1.4, lens=None):
    data = bpy.data.cameras.new("View")
    obj = bpy.data.objects.new("View", data)
    bpy.context.collection.objects.link(obj)
    bpy.context.scene.camera = obj
    visible = [m for m in bpy.context.scene.objects
               if m.type == "MESH" and not m.hide_render and m.name != "Floor"]
    pts = [m.matrix_world @ Vector(c) for m in visible for c in m.bound_box]
    target = sum(pts, Vector()) / len(pts)
    obj.location = target + Vector(direction).normalized() * 1.5
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()
    data.type = "ORTHO"
    data.clip_start = 0.01
    data.clip_end = 10
    bpy.context.view_layer.update()
    inv = obj.matrix_world.inverted()
    local = [inv @ p for p in pts]
    xmin, xmax = min(p.x for p in local), max(p.x for p in local)
    ymin, ymax = min(p.y for p in local), max(p.y for p in local)
    data.ortho_scale = max(xmax - xmin, (ymax - ymin) * aspect) * span_pad
    obj.location += obj.rotation_euler.to_matrix() @ Vector(((xmin + xmax) / 2, (ymin + ymax) / 2, 0))
    return obj


def render(name, width=1400, height=1000):
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.filepath = str(OUT / name)
    bpy.ops.render.render(write_still=True)
    print("RENDERED", OUT / name)


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = rgb("f3efe7")
    bg.inputs["Strength"].default_value = 0.55
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.0002))
    floor = bpy.context.object
    floor.name = "Floor"
    floor.data.materials.append(material("Floor", "ece6da", 0.9))
    for name, pos, energy, size in [("Key", (-0.45, -0.5, 0.7), 28, 0.6),
                                    ("Fill", (0.6, -0.2, 0.35), 10, 0.6),
                                    ("Rim", (-0.2, 0.6, 0.5), 18, 0.4)]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.size = size
        lamp = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(lamp)
        lamp.location = pos
        lamp.rotation_euler = (Vector((0, 0.09, 0.04)) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    return floor


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    floor = setup()
    bpy.ops.wm.stl_import(filepath=str(ROOT / "exports" / f"{P.MODEL_NAME}.stl"))
    stand = bpy.context.object
    stand.scale = (MM, MM, MM)
    bpy.ops.object.transform_apply(scale=True)
    stand.data.materials.append(material("Stand", "8fa89a", 0.62))
    dark = material("Tablet", "2a2d31", 0.4)
    screen = material("Screen", "101216", 0.15)

    camera((0.9, -1.0, 0.75))
    render("stand.png")
    camera((-0.75, 1.0, 0.8))
    render("rear.png")
    camera((0.25, -1.0, 0.55))
    render("front.png")
    camera((1, 0, 0), span_pad=1.15)
    render("side.png")

    tablet(dark, screen)
    camera((-0.8, -1.0, 0.7))
    render("in-use.png")
    camera((1, 0, 0), span_pad=1.1)
    render("in-use-side.png")


main()
