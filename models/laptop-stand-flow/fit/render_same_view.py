"""参考画像と同じカメラから、1脚を陰影つきで描く（参考画像と同じ 1536 x 1024、地面は z=0）。
  blender --background --python render_same_view.py -- <stl> <out.png>
"""
import json, os, sys
import numpy as np
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import view_warp as VW

W, H = 1536, 1024
stl, out = sys.argv[sys.argv.index("--") + 1:][:2]
cam = json.load(open(os.path.join(HERE, "camera_left.json")))["params"]
cam = dict(az=cam[0], el=cam[1], roll=cam[2], dist=float(np.exp(cam[3])), f=float(np.exp(cam[4])), cx=cam[5], cy=cam[6])
offset = json.load(open(os.path.join(HERE, "unit_offset.json")))["x"]


def srgb(h):
    v = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v) + (1,)


def material(color, rough):
    m = bpy.data.materials.new("m")
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = srgb(color)
    b.inputs["Roughness"].default_value = rough
    return m


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=stl)
ob = bpy.context.object
ob.location = (offset, 0, 0)
ob.scale = (0.001, 0.001, 0.001)
ob.location = (offset * 0.001, 0, 0)
for p in ob.data.polygons:
    p.use_smooth = True
ob.data.materials.append(material("e0d6c4", 0.85))
scene = bpy.context.scene
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0.123, 0))
bpy.context.object.data.materials.append(material("b6b1a9", 0.95))
cd = bpy.data.cameras.new("c")
cd.sensor_fit, cd.sensor_width = "HORIZONTAL", 36.0
cd.lens = cam["f"] * 36.0 / W
cd.shift_x = -(cam["cx"] - W / 2) / W
cd.shift_y = (cam["cy"] - H / 2) / W
cd.clip_start, cd.clip_end = 0.01, 20.0
co = bpy.data.objects.new("c", cd)
scene.collection.objects.link(co)
pos, fwd, right, up = VW.basis(cam)
rot = Matrix(((right[0], up[0], -fwd[0]), (right[1], up[1], -fwd[1]), (right[2], up[2], -fwd[2])))
co.matrix_world = Matrix.Translation(Vector(pos) * 0.001) @ rot.to_4x4()
scene.camera = co
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = W, H, 100
scene.view_settings.view_transform = "AgX"
scene.world = bpy.data.worlds.new("w")
scene.world.use_nodes = True
bg = next(n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = srgb("b6b1a9")
bg.inputs["Strength"].default_value = 1.0
for name, p, energy, size in (("key", (-0.7, 0.5, 0.8), 55, 0.9), ("fill", (0.7, 0.4, 0.4), 18, 0.9),
                              ("top", (0.0, 0.1, 1.1), 20, 1.0)):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy, ld.size = energy, size
    lo = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(lo)
    lo.location = p
    lo.rotation_euler = (Vector((offset * 0.001, 0.123, 0.06)) - lo.location).to_track_quat("-Z", "Y").to_euler()
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("wrote", out)
