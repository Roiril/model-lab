# -*- coding: utf-8 -*-
"""論文の先頭に置く 1 枚。卓の横から、uHand を中央寄りに大きく入れ、同じ駒を指す人の横顔と右手を右に収める。

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
_DEFAULTS = {"--chip": "13", "--hand-dir": "-0.10,-0.60,-0.80", "--palm": "0.0,-0.35,-1.0", "--hand-scale": "1.9",
             "--pose": "index=0,middle=0.7,ring=0.8,little=0.9,thumb=0.3",
             "--head-turn": "0", "--seat": "0.58"}
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
arm_r = S.arm_r
TOP = S.top
hand_body = Vector(S.arm_h.matrix_world @ S.arm_h.pose.bones["index_prox"].head)


def bpos(name, tail=False):
    bpy.context.view_layer.update()
    b = arm_r.pose.bones["mixamorig:" + name]
    return Vector(arm_r.matrix_world @ (b.tail if tail else b.head))


def spin(name, axis, ang):
    """骨を、世界の軸 axis のまわりに ang ラジアン回す。"""
    bpy.context.view_layer.update()
    p = arm_r.pose.bones["mixamorig:" + name]
    cur = p.matrix.copy()
    ax = (arm_r.matrix_world.to_quaternion().inverted() @ Vector(axis)).normalized()
    m = (Matrix.Rotation(ang, 3, ax) @ cur.to_3x3()).to_4x4()
    m.translation = cur.translation
    p.matrix = m


def signed(a, b, axis):
    a = (a - axis * a.dot(axis)).normalized()
    b = (b - axis * b.dot(axis)).normalized()
    return math.atan2(axis.dot(a.cross(b)), a.dot(b))


def reach(side, wrist, elbow_min=0.06):
    """肩から手首までを 2 本の骨で届かせる。肘は下げたいが、天板より elbow_min 以上は高く保つ
    （前腕が卓の縁に埋まらないように、足りなければ肘を外へ開く）。"""
    s = bpos(side + "Arm")
    l1 = (bpos(side + "ForeArm") - s).length
    l2 = (bpos(side + "Hand") - bpos(side + "ForeArm")).length
    v = Vector(wrist) - s
    dist = min(v.length, (l1 + l2) * 0.995)
    vh = v.normalized()
    a = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(l1 * l1 - a * a, 0))
    out = Vector((-1 if side == "Left" else 1, 0, 0))
    for deg in range(0, 121, 5):
        t = math.radians(deg)
        pp = Vector((0, -0.25, -1)) * math.cos(t) + out * math.sin(t)
        pp = (pp - vh * pp.dot(vh)).normalized()
        elbow = s + vh * a + pp * h
        if elbow.z >= TOP + elbow_min:
            break
    S.aim(side + "Arm", elbow - s)
    S.aim(side + "ForeArm", s + vh * dist - elbow)
    return deg, elbow.z - TOP


def palm_normal(side):
    w = bpos(side + "Hand")
    n = (bpos(side + "HandIndex1") - w).cross(bpos(side + "HandPinky1") - w).normalized()
    return n if side == "Right" else -n


def orient_hand(side, d, n):
    """手の指の向きを d、手のひらの向きを n にする。ねじりは前腕と手首で分ける。"""
    d = Vector(d).normalized()
    n = Vector(n)
    S.aim(side + "Hand", d)
    fa = (bpos(side + "Hand") - bpos(side + "ForeArm")).normalized()
    spin(side + "ForeArm", fa, signed(palm_normal(side), n, fa) * 0.6)
    S.aim(side + "Hand", d)
    spin(side + "Hand", d, signed(palm_normal(side), n, d))
    return (n - d * n.dot(d)).normalized()


def curl(side, finger, degs, d, n):
    for k, a in enumerate(degs, 1):
        r = math.radians(a)
        S.aim(f"{side}Hand{finger}{k}", d * math.cos(r) + n * math.sin(r))


def low_point(side):
    """卓の天板の上にある前腕と手の頂点のうち、いちばん低い高さ（天板からの差）。"""
    bpy.context.view_layer.update()
    dg_ = bpy.context.evaluated_depsgraph_get()
    lo = 1e9
    for o in S.remy_new:
        if o.type != "MESH":
            continue
        idx = {g.index for g in o.vertex_groups if g.name.startswith("mixamorig:" + side)
               and ("Hand" in g.name or "ForeArm" in g.name)}
        if not idx:
            continue
        ev = o.evaluated_get(dg_)
        mw = ev.matrix_world
        for v_src, v in zip(o.data.vertices, ev.data.vertices):
            if sum(g.weight for g in v_src.groups if g.group in idx) < 0.5:
                continue
            w = mw @ v.co
            if abs(w.x - S.cx) < S.hx and abs(w.y - S.cy) < S.hy:
                lo = min(lo, w.z - TOP)
    return lo


# 体を卓へ少し乗り出させる
for nm, d in (("Spine", (0, 0.24, 1)), ("Spine1", (0, 0.36, 1)), ("Spine2", (-0.04, 0.44, 1)), ("Neck", (-0.03, 0.42, 1))):
    S.aim(nm, d)

# 右手（奥）: uHand が指している駒を、人の側から人差し指で指す
chip_c = goal.copy()
tip_goal = chip_c + Vector((0.030, -0.050, 0.020))
d_r = Vector((-0.30, 0.90, -0.30)).normalized()
wrist_r = tip_goal - d_r * 0.17
for _ in range(4):
    el_r = reach("Right", wrist_r)
    n_r = orient_hand("Right", d_r, (-0.45, 0.0, -1.0))
    curl("Right", "Index", (4, 12, 20), d_r, n_r)
    curl("Right", "Middle", (62, 150, 205), d_r, n_r)
    curl("Right", "Ring", (68, 156, 210), d_r, n_r)
    curl("Right", "Pinky", (72, 160, 212), d_r, n_r)
    med = (bpos("RightHandIndex1") - bpos("RightHandPinky1")).normalized()  # 親指の側
    for k, (cd, cm, cn) in enumerate(((0.55, 0.80, 0.10), (0.80, 0.50, 0.25), (0.90, 0.25, 0.40)), 1):
        S.aim(f"RightHandThumb{k}", d_r * cd + med * cm + n_r * cn)
    wrist_r = wrist_r + (tip_goal - bpos("RightHandIndex3", tail=True))
tip_r = bpos("RightHandIndex3", tail=True)
print(f"[remy] 右の人差し指の先と狙いの差 {(tip_r - tip_goal).length * 1000:.1f} mm / uHand の指先まで "
      f"{(tip_r - goal).length * 1000:.0f} mm / 右腕の最下点 {low_point('Right') * 1000:+.1f} mm / 肘の開き {el_r[0]} 度")

# 左手（カメラ側）: 卓に出さず、腿の上に下ろす
S.aim("LeftArm", (-0.10, 0.10, -1.0))
S.aim("LeftForeArm", (0.10, 0.80, -0.60))
d_l = Vector((0.20, 0.95, -0.25)).normalized()
n_l = orient_hand("Left", d_l, (0.0, 0.0, -1.0))
for f, degs in (("Index", (10, 28, 40)), ("Middle", (12, 32, 44)), ("Ring", (14, 36, 48)), ("Pinky", (16, 40, 52))):
    curl("Left", f, degs, d_l, n_l)
wl = bpos("LeftHand")
print(f"[remy] 左手首 ({wl.x:.3f}, {wl.y:.3f}, {wl.z:.3f}) / 天板より上に出た左腕の最下点 {low_point('Left') * 1000:+.1f} mm（1e12 なら卓の上に無い）")

# 顔を uHand へ向ける。頭の骨の上向きを決めてから、目の向きを手へ回す
eye = (bpos("LeftEye") + bpos("RightEye")) / 2
gz = (hand_body + Vector((0, 0, float(arg("--gaze-up", "-0.06")))) - eye).normalized()
up = (Vector((0, 0, 1)) - gz * gz.z).normalized()
S.aim("Head", up)
eye = (bpos("LeftEye") + bpos("RightEye")) / 2
face = eye - bpos("Head")
spin("Head", up, signed(face, gz, up))
eye = (bpos("LeftEye") + bpos("RightEye")) / 2
face = (eye - bpos("Head"))
face = (face - up * face.dot(up)).normalized()
print(f"[remy] 顔の向きと手への向きの内積 {face.dot((gz - up * gz.dot(up)).normalized()):.3f}")
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


cam_loc = vec("--cam", "-0.88,0.0,1.10")
look = vec("--look", "0.0,0.0,0.995")
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
cam_d.lens = float(arg("--lens", "28.5"))
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
