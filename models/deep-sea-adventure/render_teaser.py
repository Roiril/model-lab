# -*- coding: utf-8 -*-
"""論文の先頭に置く 1 枚。卓の横から、人の横顔と uHand が海底探検の駒をはさんで向かい合うところを撮る。

場面（卓・駒・Remy・uHand）は render_vr_scene.py が組む。ここは手の向き・人の視線・部屋・光・カメラだけを決める。

blender --background --python models/deep-sea-adventure/render_teaser.py -- [--out PATH] [--size 2400x1350]
    [--engine cycles|eevee] [--samples N]
    [--cam x,y,z] [--look x,y,z] [--lens mm] [--fstop f]
    [--chip N] [--hand-dir x,y,z] [--palm x,y,z] [--hand-scale s]   （render_vr_scene.py と共通）
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# 手の置き方の既定をこの構図用に差し替える（引数で上書きできる）
_DEFAULTS = {"--chip": "13", "--hand-dir": "-0.25,-0.42,-0.87", "--palm": "0.0,-0.35,-1.0", "--hand-scale": "1.6",
             "--pose": "index=0,middle=0.75,ring=0.85,little=0.95,thumb=0.3",
             "--head-turn": "0"}
if "--" not in sys.argv:
    sys.argv.append("--")
for k, v in _DEFAULTS.items():
    if k not in sys.argv:
        sys.argv += [k, v]

import bpy
from mathutils import Matrix, Vector

import render_vr_scene as S

arg, flag = S.arg, S.flag
sc = bpy.context.scene


def vec(name, default):
    return Vector(tuple(float(v) for v in arg(name, default).split(",")))


goal = S.goal.copy()  # 人差し指の先（駒の上）
print("[teaser] fingertip", tuple(round(v, 3) for v in goal))

# ---------------------------------------------------------------- 人の視線を手へ
S.aim("Neck", vec("--neck", "0.0,0.34,1"))
S.aim("Head", vec("--head", "0.10,0.62,1"))
S.twist("Head", float(arg("--head-yaw", "0")))
bpy.context.view_layer.update()

# ---------------------------------------------------------------- uHand の黒を少し起こす
# 実物の写真では黒いアクリルと樹脂は濃い灰に写る。真っ黒のままだと形が潰れて手に見えない
LIFT = float(arg("--lift", "1.0"))
for name, rgb, rough in (("uh_acrylic", (0.016, 0.017, 0.020), 0.16), ("uh_servo", (0.020, 0.021, 0.024), 0.42),
                         ("uh_alu", (0.030, 0.031, 0.035), 0.55), ("uh_dark", (0.008, 0.008, 0.009), 0.45),
                         ("uh_bushing", (0.02, 0.02, 0.022), 0.25)):
    m = bpy.data.materials.get(name)
    if m is None:
        continue
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*[c * LIFT for c in rgb], 1)
    b.inputs["Roughness"].default_value = rough
for name in ("uh_steel", "uh_link"):
    m = bpy.data.materials.get(name)
    if m is not None:
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Metallic"].default_value = 0.9
        b.inputs["Base Color"].default_value = (0.72, 0.73, 0.76, 1)
        b.inputs["Roughness"].default_value = 0.28

# ---------------------------------------------------------------- 部屋
ROOM = 6.0
floor_m = S.flat_mat("floor", (0.050, 0.060, 0.072), 0.55)
wall_m = S.flat_mat("wall", (0.070, 0.095, 0.120), 0.95)
S.box("floor", (0, 0, -0.01), (ROOM, ROOM, 0.02), floor_m)
S.box("wall_n", (0, ROOM / 2, 1.5), (ROOM, 0.02, 3), wall_m)
S.box("wall_e", (ROOM / 2, 0, 1.5), (0.02, ROOM, 3), wall_m)
S.box("wall_w", (-ROOM / 2, 0, 1.5), (0.02, ROOM, 3), wall_m)
S.box("wall_s", (0, -ROOM / 2, 1.5), (ROOM, 0.02, 3), wall_m)

world = bpy.data.worlds.new("w")
sc.world = world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (0.35, 0.45, 0.60, 1)
bg.inputs[1].default_value = float(arg("--ambient", "0.10"))


def light(name, kind, loc, energy, size=1.0, target=(0, 0, 0.75), color=(1, 1, 1), size_y=None, spot=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == "AREA":
        ld.size = size
        if size_y:
            ld.shape = "RECTANGLE"
            ld.size_y = size_y
    if kind == "SPOT":
        ld.spot_size = math.radians(spot or 40)
        ld.spot_blend = 1.0
        ld.shadow_soft_size = size
    lo = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return lo


cam_loc = vec("--cam", "-0.97,-0.16,1.08")
look = vec("--look", "-0.02,-0.20,0.96")
K = float(arg("--light", "1.0"))
g = tuple(goal)
hand_c = Vector(S.arm_h.matrix_world @ S.arm_h.pose.bones["index_prox"].head)  # 手の胴のあたり

head_c = Vector(S.arm_r.matrix_world @ S.arm_r.pose.bones["mixamorig:Head"].head) + Vector((0, 0.03, 0.08))
RIM = float(arg("--rim", "1.0"))
# 卓の真上から落とす主光。卓と駒を明るい面にする
light("key", "AREA", (-0.15, -0.05, 2.15), 60 * K, 1.1, target=(0, -0.05, 0.75), color=(1.0, 0.96, 0.90))
# 人の顔に当てる光（卓の向こう、カメラ寄りの上から）
light("face", "AREA", (-0.65, 0.60, 1.65), 42 * K, 0.8, target=tuple(head_c), color=(1.0, 0.93, 0.85))
# 手の輪郭を拾う細長い光。カメラの反対側の上から
light("rim_hand", "AREA", (0.85, 0.50, 1.50), 110 * K * RIM, 1.4, target=tuple(hand_c), color=(0.72, 0.87, 1.0), size_y=0.22)
# 人の髪と肩の輪郭
light("rim_head", "AREA", (0.90, -1.15, 1.95), 75 * K * RIM, 0.9, target=tuple(head_c), color=(0.72, 0.87, 1.0))
# 手のカメラ側の板とねじを起こす光
light("hand_fill", "AREA", (-0.95, 0.30, 1.18), 20 * K, 0.45, target=tuple(hand_c), color=(1.0, 0.96, 0.92))
# 奥の壁に落とす青い明かり。黒い手の後ろを明るくして形を抜く
WASH = float(arg("--wash", "0.45"))
if WASH > 0:
    wx = float(arg("--wash-y", "0.75"))
    light("wash", "SPOT", (1.2, wx, 0.15), 1500 * WASH, 0.3, target=(3.0, wx, 1.05), color=(0.35, 0.62, 0.85), spot=120)

# ---------------------------------------------------------------- カメラ
cam_d = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
cam_d.lens = float(arg("--lens", "32"))
cam.location = cam_loc
cam.rotation_euler = (look - cam_loc).to_track_quat("-Z", "Y").to_euler()
fstop = float(arg("--fstop", "4.0"))
if fstop > 0:
    cam_d.dof.use_dof = True
    cam_d.dof.focus_distance = (hand_c - cam_loc).length
    cam_d.dof.aperture_fstop = fstop
print(f"[teaser] cam->hand {(hand_c - cam_loc).length:.3f} m / cam->head "
      f"{((S.arm_r.matrix_world @ S.arm_r.pose.bones['mixamorig:Head'].head) - cam_loc).length:.3f} m")

# ---------------------------------------------------------------- 描画
engine = arg("--engine", "cycles")
samples = int(arg("--samples", "128"))
if engine == "cycles":
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    dev = "CPU"
    for kind in ("OPTIX", "CUDA", "HIP", "ONEAPI"):
        try:
            prefs.compute_device_type = kind
            prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == kind]
            if gpus:
                for d in prefs.devices:
                    d.use = d.type == kind
                dev = "GPU"
                print("[teaser] cycles device", kind, [d.name for d in gpus])
                break
        except Exception:
            pass
    sc.cycles.device = dev
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
else:
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    sc.eevee.taa_render_samples = samples
    for attr in ("use_shadows", "use_gtao", "use_raytracing"):
        try:
            setattr(sc.eevee, attr, True)
        except Exception:
            pass
try:
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = arg("--agx-look", "AgX - Base Contrast")
except TypeError as e:
    print("[teaser] view", e)
sc.view_settings.exposure = float(arg("--exposure", "0"))
w, h = (int(v) for v in arg("--size", "2400x1350").split("x"))
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.render.film_transparent = False
out = arg("--out", os.path.join(S.ML, "exports", "deep-sea", "vr-scene.png"))
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("[teaser] wrote", out)
