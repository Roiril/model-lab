# -*- coding: utf-8 -*-
"""俯瞰GLBを真上から正射投影でレンダ → _top.png（実物写真との比較用）。"""
import bpy, os, math, mathutils
HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "deep-sea"))

bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, "deep-sea-adventure.glb"))

mn = mathutils.Vector((1e9,1e9,1e9)); mx = -mn
for o in bpy.data.objects:
    if o.type=="MESH":
        for c in o.bound_box:
            w = o.matrix_world @ mathutils.Vector(c)
            mn = mathutils.Vector((min(mn[i],w[i]) for i in range(3)))
            mx = mathutils.Vector((max(mx[i],w[i]) for i in range(3)))
center = (mn+mx)/2
W = (mx-mn).x; H = (mx-mn).y

cam_data = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_data)
bpy.context.collection.objects.link(cam)
cam_data.type = "ORTHO"
cam_data.ortho_scale = max(W, H) * 1.12
tilt = math.radians(18)                  # 真上に近い斜め
dist = 1.0
cam.location = (center.x, center.y - math.sin(tilt)*dist, center.z + math.cos(tilt)*dist)
cam.rotation_euler = (tilt, 0, 0)
bpy.context.scene.camera = cam

# 平板ライティング（影なし）: 環境光のみで真上テクスチャを素直に見る
world = bpy.data.worlds.new("w"); bpy.context.scene.world = world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(0.93,0.92,0.90,1)
world.node_tree.nodes["Background"].inputs[1].default_value=1.4

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
aspect = W/H
sc.render.resolution_x = 1600
sc.render.resolution_y = int(1600/aspect)
sc.render.filepath = os.path.join(OUT, "_top.png")
bpy.ops.render.render(write_still=True)
print("rendered top:", sc.render.resolution_x, "x", sc.render.resolution_y)
