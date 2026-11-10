"""写真と同じ角度で描く。

blender --background --python models/hiwonder-uhand/render_views.py -- --out DIR [--views main,side]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)
os.environ["UHAND_NO_EXPORT"] = "1"

import bpy
from mathutils import Vector

import model as HM

MM = HM.P.MM
# 名前: (方位[deg]: -Y から -X 側へ、仰角[deg]、注視点 (x, y, z)[mm]、距離[mm]、焦点距離、解像度、ロール[deg])
VIEWS = {
    # 商品写真 10（手のひら側、小指側の斜め前から）
    "p10": (27.0, 8.0, (20, 0, 88), 400, 70, (757, 705), 0.0),
    # 商品写真 11（同じ向きで少し上から）
    "p11": (30.0, 14.0, (18, 0, 90), 400, 70, (676, 676), 0.0),
    # 実物写真 14（手のひら側をほぼ正面から）
    "p14": (4.0, 4.0, (22, 0, 88), 430, 70, (746, 866), 0.0),
    # 甲の写真 04（後ろから、親指側へ少し回る）
    "p04": (196.0, -2.0, (14, 20, 50), 400, 85, (1010, 681), -6.0),
    # 甲の写真 06（斜め後ろ上、小指側から。指が左上へ伸びる）
    "p06": (150.0, 32.0, (-5, 10, 90), 400, 70, (666, 666), -32.0),
    # 商品写真 13 の左下（甲を上から）
    "p13": (215.0, 50.0, (0, 20, 45), 220, 70, (690, 512), -60.0),
    # 確認用
    "side": (-90.0, 5.0, (0, 0, 88), 380, 70, (700, 900), 0.0),
    "under": (160.0, -12.0, (5, 10, 25), 330, 60, (900, 700), 0.0),
}


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = os.path.join(HERE, "_renders")
    if "--out" in a:
        out = a[a.index("--out") + 1]
    if "--views" in a:
        keep = a[a.index("--views") + 1].split(",")
        for k in list(VIEWS):
            if k not in keep:
                del VIEWS[k]
    return out


def setup_scene():
    sc = bpy.context.scene
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for eng in ("CYCLES",):
        try:
            sc.render.engine = eng
        except TypeError:
            pass
    sc.cycles.samples = 96
    sc.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception as e:
        print("[render] GPU unavailable:", e)
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    # カメラには白、映り込みには暗い灰色を見せる（商品写真のスタジオ）
    nt = w.node_tree
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    out = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
    bg.inputs[0].default_value = (0.035, 0.035, 0.038, 1)
    bg.inputs[1].default_value = 1.0
    white = nt.nodes.new("ShaderNodeBackground")
    white.inputs[0].default_value = (1, 1, 1, 1)
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(bg.outputs[0], mix.inputs[1])
    nt.links.new(white.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    for name, loc, en, size in (("key", (-0.45, -0.6, 0.55), 18.0, 0.12), ("fill", (0.5, -0.5, 0.25), 8.0, 0.25),
                                ("top", (0.0, 0.1, 0.8), 12.0, 0.15), ("rim", (0.2, 0.6, 0.4), 10.0, 0.12)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = en
        ld.size = size
        lo = bpy.data.objects.new(name, ld)
        lo.location = loc
        d = Vector((0, 0, 0.09)) - Vector(loc)
        lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(lo)
    cd = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def place(cam, az, pitch, look, dist, lens, roll=0.0):
    a, p = math.radians(az), math.radians(pitch)
    t = Vector(look) * MM
    d = Vector((-math.sin(a) * math.cos(p), -math.cos(a) * math.cos(p), math.sin(p)))
    cam.location = t + d * dist * MM
    q = (t - cam.location).to_track_quat("-Z", "Y")
    from mathutils import Quaternion
    cam.rotation_euler = (q @ Quaternion((0, 0, 1), math.radians(roll))).to_euler()
    cam.data.lens = lens


def main():
    out = args()
    os.makedirs(out, exist_ok=True)
    cam = setup_scene()
    sc = bpy.context.scene
    HM.build()
    for name, (az, pitch, look, dist, lens, res, roll) in VIEWS.items():
        sc.render.resolution_x, sc.render.resolution_y = res
        place(cam, az, pitch, look, dist, lens, roll)
        sc.render.filepath = os.path.join(out, f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("[render]", sc.render.filepath)


main()
