"""npz のメッシュ（mm）を側面・斜めから描く。
  blender --background --python preview_npz.py -- <mesh.npz> <out_prefix>
"""
import math, os, sys
import numpy as np
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
mesh_path, prefix = args[0], args[1]
d = np.load(mesh_path)
verts, quads = d["verts"].astype(np.float64), d["quads"]


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
me = bpy.data.meshes.new("m")
me.from_pydata((verts / 1000.0).tolist(), [], quads.tolist())
me.update()
for p in me.polygons:
    p.use_smooth = True
ob = bpy.data.objects.new("m", me)
bpy.context.scene.collection.objects.link(ob)
ob.data.materials.append(material("e4dccb", 0.85))
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.view_settings.view_transform = "AgX"
sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True
bg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = srgb("b9b4ab")
bg.inputs["Strength"].default_value = 0.5
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0.12, 0))
bpy.context.object.data.materials.append(material("a8a39a", 0.95))
for name, pos, energy, size in (("key", (0.2, 0.9, 0.7), 40, 0.8), ("fill", (0.9, -0.2, 0.4), 12, 0.9),
                                ("top", (-0.3, 0.1, 1.0), 14, 1.0)):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy, ld.size = energy, size
    lo = bpy.data.objects.new(name, ld)
    bpy.context.collection.objects.link(lo)
    lo.location = pos
    lo.rotation_euler = (Vector((0, 0.12, 0.06)) - lo.location).to_track_quat("-Z", "Y").to_euler()


def shoot(name, az, el, dist, lens=50):
    target = Vector((0, 0.123, 0.07))
    a, e = math.radians(az), math.radians(el)
    pos = target + Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))) * dist
    cd = bpy.data.cameras.new("c")
    cd.lens = lens
    co = bpy.data.objects.new("c", cd)
    bpy.context.collection.objects.link(co)
    co.location = pos
    co.rotation_euler = (target - pos).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = 1400, 1000
    sc.render.filepath = f"{prefix}_{name}.png"
    bpy.ops.render.render(write_still=True)


shoot("side", 0, 6, 0.95, 85)
shoot("iso", 47, 17, 0.5)
shoot("top", 0, 89, 1.3, 85)
