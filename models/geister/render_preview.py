# -*- coding: utf-8 -*-
"""geister.glb を読み込み、テクスチャ付きでレンダして _preview.png を出す（目視確認用）。"""
import bpy, os, math, mathutils
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "geister"))

bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
for m in list(bpy.data.materials): bpy.data.materials.remove(m)

bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, "geister.glb"))

mn = mathutils.Vector((1e9, 1e9, 1e9)); mx = -mn
for o in bpy.data.objects:
    if o.type == "MESH":
        for c in o.bound_box:
            w = o.matrix_world @ mathutils.Vector(c)
            mn = mathutils.Vector((min(mn[i], w[i]) for i in range(3)))
            mx = mathutils.Vector((max(mx[i], w[i]) for i in range(3)))
center = (mn + mx) / 2
span_x = (mx - mn).x

cam_data = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_data)
bpy.context.collection.objects.link(cam)
d = span_x * 1.15
cam.location = (center.x, center.y - d * 0.55, center.z + d * 0.95)
dirv = center - cam.location
cam.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()
cam_data.lens = 50
bpy.context.scene.camera = cam

sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.0
so = bpy.data.objects.new("sun", sun); bpy.context.collection.objects.link(so)
so.rotation_euler = (math.radians(35), math.radians(8), math.radians(25))
world = bpy.data.worlds.new("w"); bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.56, 0.58, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.9

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.film_transparent = False
sc.render.resolution_x = 1400; sc.render.resolution_y = 1100
sc.render.filepath = os.path.join(OUT, "_preview.png")
bpy.ops.render.render(write_still=True)
print("rendered:", sc.render.filepath)
