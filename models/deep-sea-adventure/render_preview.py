# -*- coding: utf-8 -*-
"""俯瞰GLBを読み込み、テクスチャ付きでレンダして _preview.png を出す（目視確認用）。"""
import bpy, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "deep-sea"))

bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
for m in list(bpy.data.materials): bpy.data.materials.remove(m)

bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, "deep-sea-adventure.glb"))

# 全体バウンディング
import mathutils
mn = mathutils.Vector((1e9,1e9,1e9)); mx = -mn
for o in bpy.data.objects:
    if o.type=="MESH":
        for c in o.bound_box:
            w = o.matrix_world @ mathutils.Vector(c)
            mn = mathutils.Vector((min(mn[i],w[i]) for i in range(3)))
            mx = mathutils.Vector((max(mx[i],w[i]) for i in range(3)))
center = (mn+mx)/2
span = max((mx-mn).x, (mx-mn).y)

# カメラ（やや俯瞰、縦長レイアウト全体を入れる）
cam_data = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_data)
bpy.context.collection.objects.link(cam)
d = span*1.5
cam.location = (center.x + d*0.04, center.y - d*0.45, center.z + d*1.05)
dir = center - cam.location
cam.rotation_euler = dir.to_track_quat('-Z','Y').to_euler()
cam_data.lens = 50
bpy.context.scene.camera = cam

# ライト
sun = bpy.data.lights.new("sun","SUN"); sun.energy=4.0
so = bpy.data.objects.new("sun",sun); bpy.context.collection.objects.link(so)
so.rotation_euler = (math.radians(40), math.radians(10), math.radians(30))
# 背景クリーム
world = bpy.data.worlds.new("w"); bpy.context.scene.world = world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(0.90,0.88,0.84,1)
world.node_tree.nodes["Background"].inputs[1].default_value=0.9

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.film_transparent = False
sc.render.resolution_x = 1100; sc.render.resolution_y = 1400
sc.render.filepath = os.path.join(OUT, "_preview.png")
bpy.ops.render.render(write_still=True)
print("rendered:", sc.render.filepath)
