"""見た目の確認用の静止画。手の甲側・斜め・横・寄りを描く。

blender --background --python models/simple-black-hand/render_views.py -- [--out DIR] [--pose fist]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bpy
from mathutils import Vector

import model as HM
import params as P

OUT = r"G:\マイドライブ\shubie\renders\simple-black-hand"
# 名前: (方位[deg]、見下ろす角度[deg]、注視点 (X,Z)[mm]、距離[mm])
VIEWS = {
    "front": (0.0, 8.0, (0, 140), 620),
    "rear": (180.0, 8.0, (0, 140), 620),
    "oblique": (145.0, 22.0, (0, 150), 600),
    "side": (90.0, 4.0, (0, 140), 620),
    "close": (150.0, 20.0, (5, 200), 260),
    "close_front": (25.0, 15.0, (5, 200), 260),
    "thumb_base": (-20.0, 10.0, (-45, 95), 240),
}


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = OUT
    pose = None
    if "--out" in a:
        out = a[a.index("--out") + 1]
    if "--views" in a:
        keep = a[a.index("--views") + 1].split(",")
        for k in list(VIEWS):
            if k not in keep:
                del VIEWS[k]
    if "--pose" in a:
        pose = a[a.index("--pose") + 1]
    return out, pose


def setup_scene():
    sc = bpy.context.scene
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    try:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1000
    sc.render.resolution_y = 1000
    sc.render.film_transparent = False
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.78, 0.79, 0.81, 1)
    bg.inputs[1].default_value = 0.7
    for name, loc, en, size in (("key", (0.4, -0.5, 0.6), 60.0, 0.4), ("fill", (-0.5, -0.3, 0.3), 25.0, 0.6),
                                ("rim", (0.0, 0.6, 0.5), 45.0, 0.4)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = en
        ld.size = size
        lo = bpy.data.objects.new(name, ld)
        lo.location = loc
        d = Vector((0, 0, 0.14)) - Vector(loc)
        lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(lo)
    cd = bpy.data.cameras.new("cam")
    cd.lens = 85
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def place(cam, az, pitch, look, dist):
    a, p = math.radians(az), math.radians(pitch)
    t = Vector((look[0] * P.MM, 0, look[1] * P.MM))
    d = Vector((math.sin(a) * math.cos(p), -math.cos(a) * math.cos(p), math.sin(p)))
    cam.location = t + d * dist * P.MM
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()


def apply_pose(joints, pose):
    if pose != "fist":
        return
    for name, ang in P.FIST_FINGER.items():
        for j, v in ang.items():
            ob, ax, base = joints[f"{name}_{j}"]
            r = list(base)
            r[ax] += math.radians(v)
            ob.rotation_euler = r
    for j, v in P.FIST_THUMB.items():
        ob, ax, base = joints[f"thumb_{j}"]
        r = list(base)
        r[ax] += math.radians(v)
        ob.rotation_euler = r


def main():
    out, pose = args()
    os.makedirs(out, exist_ok=True)
    cam = setup_scene()
    objs, _, joints = HM.build_hand()
    apply_pose(joints, pose)
    bpy.context.view_layer.update()
    tag = f"_{pose}" if pose else ""
    for name, (az, pitch, look, dist) in VIEWS.items():
        place(cam, az, pitch, look, dist)
        bpy.context.scene.render.filepath = os.path.join(out, f"{name}{tag}.png")
        bpy.ops.render.render(write_still=True)
        print("[render]", bpy.context.scene.render.filepath)


main()
