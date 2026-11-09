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

MM = 0.001
# 名前: (方位[deg]: -Y から -X 側へ、仰角[deg]、注視点 (x, y, z)[mm]、距離[mm]、焦点距離、解像度)
VIEWS = {
    # 商品写真（正面寄り、小指側から）
    "main": (24.0, 10.0, (8, -10, 150), 700, 70, (760, 1000)),
    # 指の横顔（親指側から、指先側）
    "side": (55.0, 18.0, (20, -30, 212), 400, 70, (1035, 765), 0.0),
    # 手のひら側のサーボを寄りで（写真の左上）
    "servo": (22.0, 18.0, (5, -20, 100), 330, 70, (1035, 765)),
    # 正面寄りの写真（2 枚目に届いた写真。手のひら側を正面から）
    "front": (4.0, 6.0, (8, -10, 150), 700, 70, (746, 866)),
    # 手の甲のアルミ板（写真の左下）
    "back": (200.0, 45.0, (0, 10, 72), 330, 70, (1035, 765), 70.0),
}


CURLED = {"side"}   # 指を曲げた姿勢で描く図
FIT = "--fit" in sys.argv   # points/<view>_cam.json があれば写真から逆算したカメラで描く


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
        d = Vector((0, 0, 0.13)) - Vector(loc)
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


def place_fit(cam, view):
    """camfit.py が写真から逆算したカメラを置く。写真と同じ画角になる。"""
    import json
    from mathutils import Matrix
    d = json.load(open(os.path.join(HERE, "points", f"{view}_cam.json"), encoding="utf-8"))
    r, dn, fw = (Vector(d[k]) for k in ("right", "down", "fwd"))
    m = Matrix((r, -dn, -fw)).transposed()          # 列 = カメラの x, y, z（Blender は -Z を見る）
    cam.matrix_world = Matrix.Translation(Vector(d["pos"]) * MM) @ m.to_4x4()
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.sensor_width = 36.0
    cam.data.lens = d["f_px"] * 36.0 / d["size"][0]
    return tuple(d["size"])


def main():
    out = args()
    os.makedirs(out, exist_ok=True)
    cam = setup_scene()
    sc = bpy.context.scene
    for name, (az, pitch, look, dist, lens, res, *rest) in VIEWS.items():
        pose = HM.P.CURL_POSE if name in CURLED else None
        if HM.COLL is None or HM.POSE != pose:
            if HM.COLL is not None:
                for ob in list(HM.COLL.objects):
                    bpy.data.objects.remove(ob, do_unlink=True)
                bpy.data.collections.remove(HM.COLL)
            HM.POSE = pose
            HM.build()
        sc.render.resolution_x, sc.render.resolution_y = res
        place(cam, az, pitch, look, dist, lens, rest[0] if rest else 0.0)
        if FIT and os.path.exists(os.path.join(HERE, "points", f"{name}_cam.json")):
            sc.render.resolution_x, sc.render.resolution_y = place_fit(cam, name)
        sc.render.filepath = os.path.join(out, f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("[render]", sc.render.filepath)


main()
