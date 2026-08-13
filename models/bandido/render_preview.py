# -*- coding: utf-8 -*-
"""俯瞰GLBと単体カードを読み込み、テクスチャ付きでレンダして確認画像を出す。
  _preview.png  … 全32枚の俯瞰
  _hero.png     … 単体カードを傾けて（角丸・厚み確認）
"""
import bpy, os, math, mathutils, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "bandido"))


def reset():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
    for m in list(bpy.data.materials): bpy.data.materials.remove(m)
    for im in list(bpy.data.images):
        try: bpy.data.images.remove(im)
        except Exception: pass


def bounds():
    mn = mathutils.Vector((1e9, 1e9, 1e9)); mx = -mn
    for o in bpy.data.objects:
        if o.type == "MESH":
            for c in o.bound_box:
                w = o.matrix_world @ mathutils.Vector(c)
                mn = mathutils.Vector((min(mn[i], w[i]) for i in range(3)))
                mx = mathutils.Vector((max(mx[i], w[i]) for i in range(3)))
    return mn, mx


def setup_world_light():
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.0
    so = bpy.data.objects.new("sun", sun); bpy.context.collection.objects.link(so)
    so.rotation_euler = (math.radians(38), math.radians(10), math.radians(22))
    world = bpy.data.worlds.new("w"); bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.55, 0.56, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.95


def render(path, resx, resy):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.film_transparent = False
    sc.render.resolution_x = resx; sc.render.resolution_y = resy
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("rendered:", path)


def cam_at(center, loc, lens=50):
    cd = bpy.data.cameras.new("cam"); cd.lens = lens
    cam = bpy.data.objects.new("cam", cd); bpy.context.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (center - mathutils.Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


# --- 俯瞰 ---------------------------------------------------------------
reset()
bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, "bandido.glb"))
mn, mx = bounds(); center = (mn + mx) / 2; span = (mx - mn)
setup_world_light()
d = max(span.x, span.y) * 1.85
cam_at(center, (center.x, center.y - d * 0.10, center.z + d * 1.05), lens=40)
render(os.path.join(OUT, "_preview.png"), 1500, 1200)

# --- 単体ヒーロー（bandy を傾けて角丸・厚みを見る）----------------------
reset()
bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, "glb", "bandy.glb"))
mn, mx = bounds(); center = (mn + mx) / 2; span = (mx - mn)
setup_world_light()
d = span.y * 1.5
cam_at(center, (center.x + d * 0.35, center.y - d * 0.7, center.z + d * 0.7), lens=60)
render(os.path.join(OUT, "_hero.png"), 900, 1100)

print("DONE preview")
