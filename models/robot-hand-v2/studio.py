"""参考画像と同じ構図（白い壁・つや消しの黒）を組む。手は前腕の先にあり、前腕は画面の下の外へ出る。机は置かない。

単独で実行すると 3 視点の静止画を描く:
  blender --background --python models/robot-hand-v2/studio.py -- [--res 1254] [--samples 128] [--views front,rear,oblique] [--out DIR]
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bpy
import numpy as np
from mathutils import Matrix, Vector

import model as HM
import params as P

CAM_JSON = os.path.join(HERE, "cameras.json")
RENDER_DIR = r"G:\マイドライブ\shubie\renders\robot-hand-v2"
# 机の奥の縁が写る行（参考画像から測った値）。視点ごとに机と壁をカメラへ向けて置く。
TABLE_EDGE_ROW = {"front": 965, "oblique": 935, "rear": 967, "target": 1500, "side": 1500, "wrist": 1500}
# 壁の色は視点ごとに参考画像から読んだ sRGB。自発光にして、下へ向かって暗くならないようにする
WALL_SRGB = {"front": (225, 220, 216), "oblique": (222, 216, 213), "rear": (224, 218, 214), "video": (225, 220, 216),
             "target": (222, 216, 213), "side": (226, 226, 226), "wrist": (226, 226, 226)}
# 手を照らす面光源の強さ。視点ごとに手のひらの色が参考画像と合うように決めた
LIGHT_ENERGY = {"front": 5.5, "oblique": 6.0, "rear": 3.2, "video": 5.0, "target": 4.0, "side": 5.0, "wrist": 4.0}
# 周囲の明るさ。手のひらの色はほぼこれで決まる
WORLD_BY_VIEW = {"front": 0.60, "oblique": 0.75, "rear": 0.88, "video": 0.7, "target": 0.85, "side": 0.8, "wrist": 0.85}
WOOD_LIGHT = (0.37, 0.165, 0.075)
WOOD_DARK = (0.235, 0.092, 0.036)
WORLD_STRENGTH = 0.9


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def camera_axes(c):
    a, p, r = math.radians(c["az"]), math.radians(c["pitch"]), math.radians(c["roll"])
    F = Vector((-math.sin(a) * math.cos(p), math.cos(a) * math.cos(p), -math.sin(p)))
    Rt0 = F.cross(Vector((0, 0, 1))).normalized()
    Up0 = Rt0.cross(F)
    Rt = Rt0 * math.cos(r) + Up0 * math.sin(r)
    Up = -Rt0 * math.sin(r) + Up0 * math.cos(r)
    return F, Rt, Up, Rt0


def camera_pos(c):
    F, Rt, Up, Rt0 = camera_axes(c)
    T = Rt0 * (c["tx"] * P.MM) + Vector((0, 0, c["tz"] * P.MM))
    return T - F * (c["dist"] * P.MM)


def apply_camera(cam, c):
    F, Rt, Up, _ = camera_axes(c)
    m = Matrix((Rt, Up, -F)).transposed().to_4x4()
    m.translation = camera_pos(c)
    cam.matrix_world = m
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.sensor_width = 36.0
    cam.data.lens = c["f"] * 36.0 / 1254.0
    cam.data.clip_start = 0.01
    cam.data.clip_end = 20.0


def table_depth_for_row(c, row):
    """机の奥の縁がその行に写る、カメラからの水平距離 [m]。"""
    F, Rt, Up, _ = camera_axes(c)
    C = camera_pos(c)
    a = math.radians(c["az"])
    fwd = Vector((-math.sin(a), math.cos(a), 0))
    lo, hi = 0.1, 15.0
    for _ in range(60):
        mid = (lo + hi) / 2
        q = (Vector((C.x, C.y, 0)) + fwd * mid) - C
        v = 627 - c["f"] * q.dot(Up) / q.dot(F)
        if v > row:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _plane(name, size_x, size_y, col):
    me = bpy.data.meshes.new(name)
    hx, hy = size_x / 2, size_y / 2
    me.from_pydata([(-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def wood_material():
    mat = bpy.data.materials.new("wood")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Roughness"].default_value = 0.55
    b.inputs["Specular IOR Level"].default_value = 0.25
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    # 木目は机の X 方向に長い
    mp.inputs["Scale"].default_value = (5.0, 230.0, 1.0)
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = 1.0
    n1.inputs["Detail"].default_value = 8.0
    n1.inputs["Distortion"].default_value = 0.6
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.33
    ramp.color_ramp.elements[0].color = (*WOOD_DARK, 1)
    ramp.color_ramp.elements[1].position = 0.68
    ramp.color_ramp.elements[1].color = (*WOOD_LIGHT, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs[0], n1.inputs["Vector"])
    nt.links.new(n1.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs[0], b.inputs["Base Color"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return mat


def wall_material():
    mat = bpy.data.materials.new("wall")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = 1.0
    nt.links.new(e.outputs[0], out.inputs[0])
    return mat


def set_wall_color(st, view):
    nt = st["wall"].data.materials[0].node_tree
    e = next(n for n in nt.nodes if n.type == "EMISSION")
    e.inputs["Color"].default_value = (*[srgb_to_linear(c) for c in WALL_SRGB[view]], 1)


def setup_scene(res=1254, samples=128):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.use_adaptive_sampling = True
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for kind in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = kind
                prefs.get_devices()
                gpus = [d for d in prefs.devices if d.type == kind]
                if gpus:
                    for d in prefs.devices:
                        d.use = d.type == kind
                    sc.cycles.device = "GPU"
                    print("GPU:", kind, [d.name for d in gpus])
                    break
            except Exception as e:
                print("GPU 不可:", kind, e)
    except Exception as e:
        print("GPU 設定失敗:", e)
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (1, 1, 1, 1)
    bg.inputs[1].default_value = WORLD_STRENGTH
    col = sc.collection
    # 机・壁（視点ごとに置き直す）
    table = _plane("table", 6.0, 6.0, col)
    table.data.materials.append(wood_material())
    # 机の色が手へ映って赤くならないように、拡散光には机を見せない
    table.visible_diffuse = False
    table.visible_glossy = False
    # 手は前腕で支えるので机に置かない。机は描かず、壁だけを背景にする
    table.hide_render = True
    wall = _plane("wall", 12.0, 12.0, col)
    wall.data.materials.append(wall_material())
    # 上の大きな面光源で輪郭に薄い明るさを乗せる
    ld = bpy.data.lights.new("soft", "AREA")
    ld.shape = "RECTANGLE"
    ld.size = 1.2
    ld.size_y = 1.2
    ld.energy = 5.0
    ld.color = (1.0, 0.99, 0.97)
    lo = bpy.data.objects.new("soft", ld)
    col.objects.link(lo)
    cd = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cd)
    col.objects.link(cam)
    sc.camera = cam
    return dict(table=table, wall=wall, light=lo, cam=cam)


def place_view(st, cams, view, row=None, light_key=None):
    c = cams[view]
    apply_camera(st["cam"], c)
    set_wall_color(st, light_key or view)
    st["light"].data.energy = LIGHT_ENERGY[light_key or view]
    bg = next(n for n in bpy.context.scene.world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[1].default_value = WORLD_BY_VIEW[light_key or view]
    a = math.radians(c["az"])
    C = camera_pos(c)
    fwd = Vector((-math.sin(a), math.cos(a), 0))
    rgt = Vector((math.cos(a), math.sin(a), 0))
    d = table_depth_for_row(c, row if row is not None else TABLE_EDGE_ROW[view])
    edge = Vector((C.x, C.y, 0)) + fwd * d
    # 机: 奥の縁が edge に来る
    st["table"].rotation_euler = (0, 0, a)
    st["table"].location = edge - fwd * 3.0
    st["wall"].rotation_euler = (math.pi / 2, 0, a)
    st["wall"].location = edge + Vector((0, 0, 2.0))
    # 光はカメラの上（少し手前左）から手へ向ける
    lp = C * 0.55 + Vector((0, 0, 0.75)) - rgt * 0.25
    st["light"].location = lp
    st["light"].rotation_euler = (Vector((0, 0, 0.13)) - lp).to_track_quat("-Z", "Y").to_euler()


def load_cameras():
    with open(CAM_JSON, encoding="utf-8") as f:
        return json.load(f)


def render_still(path, media_png=True):
    sc = bpy.context.scene
    sc.render.image_settings.media_type = "IMAGE"
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def _arg(name, default):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(name) + 1] if name in a else default


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    res = int(_arg("--res", 1254))
    samples = int(_arg("--samples", 128))
    outdir = _arg("--out", RENDER_DIR)
    views = _arg("--views", "front,oblique,rear").split(",")
    os.makedirs(outdir, exist_ok=True)
    st = setup_scene(res, samples)
    HM.build_hand()
    cams = load_cameras()
    for v in views:
        place_view(st, cams, v)
        render_still(os.path.join(outdir, f"model-{v}.png"))
        print("描画:", v, flush=True)
