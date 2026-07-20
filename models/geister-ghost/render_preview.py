# -*- coding: utf-8 -*-
"""geister-ghost.glb を読み込み、正面・側面・裏の3アングルをレンダして _preview.png を出す。"""
import bpy, os, math, mathutils
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "geister-ghost"))
TARGET = os.environ.get("GHOST_GLB", "ghost_blue.glb")

bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, TARGET))

mn = mathutils.Vector((1e9, 1e9, 1e9)); mx = -mn
for o in bpy.data.objects:
    if o.type == "MESH":
        for c in o.bound_box:
            w = o.matrix_world @ mathutils.Vector(c)
            mn = mathutils.Vector((min(mn[i], w[i]) for i in range(3)))
            mx = mathutils.Vector((max(mx[i], w[i]) for i in range(3)))
center = (mn + mx) / 2
span = max((mx - mn).x, (mx - mn).z)

cam_data = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_data)
bpy.context.collection.objects.link(cam); bpy.context.scene.camera = cam
cam_data.lens = 65

sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.2
so = bpy.data.objects.new("sun", sun); bpy.context.collection.objects.link(so)
so.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
world = bpy.data.worlds.new("w"); bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.32, 0.33, 0.35, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = 520; sc.render.resolution_y = 900

# 3アングル: 正面=目(+Y)側 / 側面(+X) / 裏=マーカー(-Y)側
angles = {"front": (0, 1), "side": (1, 0), "back": (0, -1)}
d = span * 2.6
tmp = []
for nm, (dx, dy) in angles.items():
    cam.location = (center.x + dx * d, center.y + dy * d, center.z + span * 0.12)
    dirv = center - cam.location
    cam.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()
    p = os.path.join(OUT, f"_v_{nm}.png")
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    tmp.append(p)

# 横連結
try:
    from PIL import Image
    ims = [Image.open(p) for p in tmp]
    W = sum(i.width for i in ims); H = max(i.height for i in ims)
    canvas = Image.new("RGB", (W, H), (50, 51, 54))
    x = 0
    for im in ims:
        canvas.paste(im, (x, 0)); x += im.width
    canvas.save(os.path.join(OUT, "_preview.png"))
    print("combined -> _preview.png")
except Exception as e:
    print("PIL merge skipped:", e)
print("rendered", TARGET)
