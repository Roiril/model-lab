# -*- coding: utf-8 -*-
"""全部入りGLBのキービジュアル。クリーム背景・柔らかい影・斜め俯瞰のヒーローショット。"""
import bpy, os, math, mathutils
HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "deep-sea"))

bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, "deep-sea-adventure.glb"))

# バウンディング
mn = mathutils.Vector((1e9,1e9,1e9)); mx = -mn
for o in bpy.data.objects:
    if o.type=="MESH":
        for c in o.bound_box:
            w = o.matrix_world @ mathutils.Vector(c)
            mn = mathutils.Vector((min(mn[i],w[i]) for i in range(3)))
            mx = mathutils.Vector((max(mx[i],w[i]) for i in range(3)))
center = (mn+mx)/2; center.z = 0
W = (mx-mn).x; H = (mx-mn).y; R = max(W, H)

# 地面（クリーム、影を受ける）
bpy.ops.mesh.primitive_plane_add(size=R*6, location=(center.x, center.y, -0.0009))
ground = bpy.context.active_object
gm = bpy.data.materials.new("ground"); gm.use_nodes=True
gb = gm.node_tree.nodes.get("Principled BSDF")
gb.inputs["Base Color"].default_value = (0.945, 0.935, 0.915, 1)  # クリーム
gb.inputs["Roughness"].default_value = 0.95
ground.data.materials.append(gm)

# カメラ（斜め俯瞰: 仰角~56°, 方位わずかに振る）。全体が収まる距離を計算。
cam_data = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_data)
bpy.context.collection.objects.link(cam)
cam_data.lens = 52
elev = math.radians(56); azim = math.radians(-12)
fov = 2*math.atan(0.5*cam_data.sensor_width/cam_data.lens)
fit = max(W, H*math.sin(elev))
dist = (fit*0.5)/math.tan(fov*0.5)*1.22
cam.location = (
    center.x + dist*math.cos(elev)*math.sin(azim),
    center.y - dist*math.cos(elev)*math.cos(azim),
    center.z + dist*math.sin(elev),
)
# 注視点を少し下げて、手前の駒・サイコロを画面内に収める
look = mathutils.Vector((center.x, center.y - H*0.12, center.z))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.camera = cam

# ライティング: エリアライト(キー, 柔らかい影) + フィル + 環境（露出控えめ）
key = bpy.data.lights.new("key","AREA"); key.energy=30; key.size=R*1.3
ko = bpy.data.objects.new("key",key); bpy.context.collection.objects.link(ko)
ko.location = (center.x - R*0.3, center.y - R*0.4, R*1.4)
ko.rotation_euler = (math.radians(26), math.radians(-12), 0)
fill = bpy.data.lights.new("fill","AREA"); fill.energy=8; fill.size=R*2.2
fo = bpy.data.objects.new("fill",fill); bpy.context.collection.objects.link(fo)
fo.location = (center.x + R*0.6, center.y + R*0.3, R*1.1)

world = bpy.data.worlds.new("w"); bpy.context.scene.world = world
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(0.95,0.94,0.92,1)
world.node_tree.nodes["Background"].inputs[1].default_value=0.45

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
try: sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Base Contrast"
except Exception: pass
try: sc.eevee.taa_render_samples = 128
except Exception: pass
try: sc.eevee.use_shadows = True
except Exception: pass
try: sc.eevee.use_gtao = True
except Exception: pass
sc.render.resolution_x = 2000
sc.render.resolution_y = 1450
sc.render.film_transparent = False
sc.render.filepath = os.path.join(OUT, "deep-sea-keyvisual.png")
bpy.ops.render.render(write_still=True)
print("HERO:", sc.render.filepath)
