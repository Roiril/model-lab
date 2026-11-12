# -*- coding: utf-8 -*-
"""実験環境の全景。物の無い暗い部屋に、卓とゲームと手と人だけがある。少し離れた高い所から見下ろす。光は図1と同じ組み立て。

人と手の姿勢・駒の配置は図1（models/deep-sea-adventure/render_teaser.py）と同じ瞬間。卓と椅子と床と光とカメラをここで作る。

blender --background --python tools/tableduo_figs/fig_env.py -- [--out PATH] [--size 2400x1350] [--samples N]
    [--cam x,y,z] [--look x,y,z] [--lens mm] [--key k] [--rim k] [--wash k] [--exposure ev]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "models", "deep-sea-adventure")))

import bpy
from mathutils import Vector

import render_teaser as T  # 卓・駒・人・手を組み、姿勢を付ける（描画はしない）
import tdf_common as C

S = T.S
arg, flag, vec = C.arg, C.flag, C.vec
sc = bpy.context.scene

# ---------------------------------------------------------------- 卓と椅子を作り直す
for root in (S.table, S.chair0, S.chair1):
    for o in [root, *root.children_recursive]:
        o.hide_render = True
wood = C.wood_mat(light=(0.27, 0.19, 0.13), dark=(0.175, 0.118, 0.078), rough=0.46, coat=0.10)
frame_m = C.flat_mat("td_frame", (0.035, 0.036, 0.040), 0.45)
C.build_table(wood, leg_mat=frame_m, cx=S.cx, cy=S.cy, hx=S.hx, hy=S.hy, top=S.top)
hips = Vector(S.arm_r.matrix_world @ S.arm_r.pose.bones["mixamorig:Hips"].head)
SEAT = hips.z - float(arg("--seat-drop", "0.105"))
C.build_chair(frame_m, (hips.x, hips.y - 0.03), seat=SEAT)
print(f"[env] hips z {hips.z:.3f} / seat {SEAT:.3f}")
for part in ("LeftToeBase", "RightToeBase", "LeftFoot", "RightFoot"):
    p = S.arm_r.matrix_world @ S.arm_r.pose.bones["mixamorig:" + part].head
    print(f"[env] {part} z {p.z:.3f}")

# ---------------------------------------------------------------- 部屋（図1と同じ。暗い床と、青い明かりの当たる壁）
ROOM = float(arg("--room", "10"))
floor_m = C.flat_mat("floor", (0.030, 0.036, 0.045), float(arg("--floor-rough", "0.35")))
wall_m = C.flat_mat("wall", (0.070, 0.095, 0.120), 0.95)
C.rbox("floor", (0, 0, -0.01), (ROOM, ROOM, 0.02), floor_m, bevel=0)
for name, loc, size in (("wall_n", (0, ROOM / 2, 2), (ROOM, 0.02, 4)), ("wall_s", (0, -ROOM / 2, 2), (ROOM, 0.02, 4)),
                        ("wall_e", (ROOM / 2, 0, 2), (0.02, ROOM, 4)), ("wall_w", (-ROOM / 2, 0, 2), (0.02, ROOM, 4))):
    C.rbox(name, loc, size, wall_m, bevel=0)
C.world((0.30, 0.42, 0.60), float(arg("--ambient", "0.06")))

# ---------------------------------------------------------------- 光（図1と同じ組み立て。1 灯で照らし出さない）
K = float(arg("--light", "1.0"))
hand_c = Vector(S.arm_h.matrix_world @ S.arm_h.pose.bones["index_prox"].head)
head_c = Vector(S.arm_r.matrix_world @ S.arm_r.pose.bones["mixamorig:Head"].head) + Vector((0, 0.03, 0.08))
tc = (S.cx, S.cy, S.top)
hc, fc = tuple(hand_c), tuple(head_c)
WARM, COOL = (1.0, 0.90, 0.78), (0.62, 0.82, 1.0)
RIM = float(arg("--rim", "1.0"))
HAND_OBJS = [o for o in bpy.data.objects if o.name.startswith("uh_") and o.type == "MESH"]
REMY_OBJS = [o for o in S.remy_new if o.type == "MESH"]

# 主光: 卓の向こう側（手の席の側）の左上から、やわらかい面で。人の顔と手の正面に当たり、卓から離れるほど暗くなる
C.light("key", "AREA", (-0.9, 1.5, 2.3), 150 * K * float(arg("--key", "1.0")), 1.2, target=tc, color=WARM, spread=110)
# 人の顔だけを少し起こす
C.only(C.light("face", "AREA", (-1.3, 0.5, 1.7), 14 * K, 0.8, target=fc, color=WARM, spread=70), REMY_OBJS, "ll_face")
# 手の輪郭: カメラの反対側の上から、細長い青い光
C.only(C.light("rim_hand", "AREA", (1.2, 0.7, 1.6), 110 * K * RIM, 1.3, target=hc, color=COOL, size_y=0.16, spread=60),
       HAND_OBJS, "ll_rim_hand")
# 人の髪と肩と背の輪郭
C.only(C.light("rim_head", "AREA", (1.3, -1.5, 2.2), 70 * K * RIM, 0.9, target=fc, color=COOL, spread=60),
       REMY_OBJS, "ll_rim_head")
# 手の甲の板に映り込ませる大きな面
C.only(C.light("card", "AREA", (-1.6, 1.0, 2.1), 30 * K, 1.6, target=hc, color=(0.92, 0.96, 1.0), spread=90),
       HAND_OBJS, "ll_card")
# 奥の壁の青い明かり（カメラから見て人と手の後ろになる 2 面）
WASH = float(arg("--wash", "0.38"))
if WASH > 0:
    h = ROOM / 2
    for i, (p0, p1) in enumerate((((h - 1.6, -0.6, 0.15), (h, -0.6, 1.5)), ((0.6, -h + 1.6, 0.15), (0.6, -h, 1.5)))):
        C.light(f"wash{i}", "SPOT", p0, 1500 * WASH, 0.3, target=p1, color=(0.30, 0.58, 0.85), spot=125)

# ---------------------------------------------------------------- カメラ（少し離れた高い所から）
cam_loc = vec("--cam", "-3.3,1.5,2.45")
look = vec("--look", "0.0,-0.18,0.55")
C.camera(cam_loc, look, float(arg("--lens", "41")), fstop=float(arg("--fstop", "0")), focus=tc)
print(f"[env] cam->table {(Vector(tc) - cam_loc).length:.2f} m")

for o in bpy.data.objects:  # 大きい物の一覧（画に入るはずのない物が残っていないかを見る）
    if o.type == "MESH" and not o.hide_render and max(o.dimensions) > 0.9:
        print(f"[env] big {o.name} dim {tuple(round(v, 2) for v in o.dimensions)} at {tuple(round(v, 2) for v in o.matrix_world.translation)}")
C.setup_render("env", arg("--size", "2400x1350"), samples=int(arg("--samples", "256")),
               engine=arg("--engine", "cycles"), exposure=float(arg("--exposure", "0")),
               look=arg("--agx-look", "AgX - Base Contrast"), bounces=8)
C.render("env", arg("--out", os.path.join(C.ML, "exports", "table-duo-figs", "env.png")))
