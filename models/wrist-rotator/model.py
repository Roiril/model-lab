"""ロボットハンド用 手首回転機構（2自由度ジンバル）— 骨格。

座標系: Z=上, Y=前, X=幅。中立姿勢（ピッチ0 = ハンド前方水平）で配置。
構成:
  yoke      … 固定部: ベース平板 + 左右2ポスト（ピッチ用 608 座, X軸）
  carriage  … 可動部: 底板 + ロール用2壁 + 側板 + ピッチスタブ軸（ヨークに対しX軸で傾く）
  rotor     … ロール軸: シャフト + フランジ + 駆動IF（キャリッジに対しY軸で回る）
  placeholder … 608 ×4（ロール2 + ピッチ2, 視覚確認用・印刷対象外）
組立式（608実物使用）。骨格では一括STLで形を確認。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()


def _add_cyl(r, length, center, name, axis, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=length, location=(0, 0, 0), vertices=verts)
    o = bpy.context.active_object
    if axis == "Y":
        o.rotation_euler = (math.pi / 2, 0, 0)
    elif axis == "X":
        o.rotation_euler = (0, math.pi / 2, 0)
    if axis in ("X", "Y"):
        bpy.ops.object.transform_apply(rotation=True)
    o.location = center
    bpy.ops.object.transform_apply(location=True)
    o.name = name
    return o


def add_cyl_y(r, length, center, name, verts=64):
    return _add_cyl(r, length, center, name, "Y", verts)


def add_cyl_x(r, length, center, name, verts=64):
    return _add_cyl(r, length, center, name, "X", verts)


def add_cyl_z(r, length, center, name, verts=64):
    return _add_cyl(r, length, center, name, "Z", verts)


def add_box(w, d, h, location, name):
    bpy.ops.mesh.primitive_cube_add(size=2, location=location)
    o = bpy.context.active_object
    o.scale = (w / 2, d / 2, h / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.name = name
    return o


def boolean(target, cutter, op="DIFFERENCE"):
    m = target.modifiers.new("bool", "BOOLEAN")
    m.operation = op
    m.object = cutter
    m.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier="bool")
    bpy.data.objects.remove(cutter, do_unlink=True)


# ============================================================
# yoke（固定部）= ベース平板 + 左右2ポスト
# ============================================================
yoke = add_box(BASE_X, BASE_Y, BASE_T, location=(0, BASE_Y / 2, BASE_T / 2), name="yoke")

post_h = POST_TOP - BASE_T
post_zc = BASE_T + post_h / 2
post_xc = (POST_INNER_X + POST_OUTER_X) / 2
for sx in (-1, +1):
    p = add_box(POST_T, POST_YW, post_h, location=(sx * post_xc, PITCH_Y, post_zc), name="post")
    boolean(yoke, p, op="UNION")

# ピッチ用 608 座（外面から座ぐり）+ リップ貫通穴（X軸）
for sx in (-1, +1):
    pocket_len = BRG_W + 0.0005
    outer_face = sx * POST_OUTER_X
    pocket_cx = outer_face - sx * (pocket_len / 2) + sx * 0.0005
    pk = add_cyl_x(POCKET_R, pocket_len, (pocket_cx, PITCH_Y, PITCH_Z), "p_pocket")
    boolean(yoke, pk)
    bore = add_cyl_x(LIP_BORE_R, POST_T + 0.002, (sx * post_xc, PITCH_Y, PITCH_Z), "p_bore")
    boolean(yoke, bore)

# 卓上固定穴（四隅, Z貫通 M4 ばか穴）
for sx in (-1, +1):
    for cy in (MOUNT_INSET, BASE_Y - MOUNT_INSET):
        hx = sx * (BASE_X / 2 - MOUNT_INSET)
        mh = add_cyl_z(MOUNT_HOLE_R, BASE_T + 0.002, (hx, cy, BASE_T / 2), "mount_hole")
        boolean(yoke, mh)

# ============================================================
# carriage（可動部）= 底板 + ロール2壁 + 側板 + ピッチスタブ
# ============================================================
cplate_yc = (CPLATE_Y0 + CPLATE_Y1) / 2
cplate_yw = CPLATE_Y1 - CPLATE_Y0
carriage = add_box(2 * CARRIAGE_HALF, cplate_yw, CARRIAGE_PLATE_T,
                   location=(0, cplate_yc, CARRIAGE_PLATE_Z0 + CARRIAGE_PLATE_T / 2),
                   name="carriage")

# ロール用2壁（底板の上に立てる）
wall_h = WALL_TOP - CARRIAGE_PLATE_TOP
wall_zc = CARRIAGE_PLATE_TOP + wall_h / 2
for wy in (WALL_BACK_Y, WALL_FRONT_Y):
    w = add_box(WALL_X, WALL_T, wall_h, location=(0, wy, wall_zc), name="r_wall")
    boolean(carriage, w, op="UNION")

# ロール用 608 座 + リップ貫通穴（Y軸, 各壁の外面から）
for wy, outward in ((WALL_BACK_Y, -1), (WALL_FRONT_Y, +1)):
    pocket_len = BRG_W + 0.0005
    outer_face = wy + outward * (WALL_T / 2)
    pocket_cy = outer_face - outward * (pocket_len / 2) + outward * 0.0005
    pk = add_cyl_y(POCKET_R, pocket_len, (0, pocket_cy, AXIS_Z), "r_pocket")
    boolean(carriage, pk)
    bore = add_cyl_y(LIP_BORE_R, WALL_T + 0.002, (0, wy, AXIS_Z), "r_bore")
    boolean(carriage, bore)

# 側板（左右）+ 内側座ボス + ピッチピン圧入穴（中心軸には達しない）
side_xc = CARRIAGE_HALF - SIDE_PLATE_T / 2
side_h = SIDE_PLATE_TOP - CARRIAGE_PLATE_TOP
side_zc = CARRIAGE_PLATE_TOP + side_h / 2
for sx in (-1, +1):
    sp = add_box(SIDE_PLATE_T, SIDE_PLATE_YW, side_h,
                 location=(sx * side_xc, PITCH_Y, side_zc), name="side_plate")
    boolean(carriage, sp, op="UNION")
    # 内側座ボス（側板内面 ±0.017 → ±STUB_PIN_IN へ）
    boss_cx = sx * (STUB_PIN_IN + HUB_BOSS_LEN / 2)
    boss = add_cyl_x(HUB_BOSS_R, HUB_BOSS_LEN, (boss_cx, PITCH_Y, PITCH_Z), "hub_boss")
    boolean(carriage, boss, op="UNION")
    # ピン圧入穴: 側板外面 ±CARRIAGE_HALF → ボス内端 ±STUB_PIN_IN
    bore_len = CARRIAGE_HALF - STUB_PIN_IN
    bore_cx = sx * (STUB_PIN_IN + bore_len / 2)
    bore = add_cyl_x(STUB_PIN_R, bore_len + 0.001, (bore_cx, PITCH_Y, PITCH_Z), "pin_bore")
    boolean(carriage, bore)

# ============================================================
# rotor（ロール軸）= シャフト + フランジ + 駆動IF + ストッパーペグ
# ============================================================
rotor = add_cyl_y(SHAFT_R, SHAFT_LEN,
                  (0, (SHAFT_REAR_Y + SHAFT_FRONT_Y) / 2, AXIS_Z), "rotor")

# 駆動IF: 後端のDカット（+Z側を平面に削る）
flat_z = AXIS_Z + (SHAFT_R - DCUT_FLAT)
dcut = add_box(SHAFT_R * 4, DCUT_LEN + 0.001, SHAFT_R * 2,
               location=(0, SHAFT_REAR_Y + DCUT_LEN / 2, flat_z + SHAFT_R), name="dcut")
boolean(rotor, dcut)

# フランジ
flange = add_cyl_y(FLANGE_R, FLANGE_T,
                   (0, (FLANGE_BACK_Y + FLANGE_FRONT_Y) / 2, AXIS_Z), "flange")
boolean(rotor, flange, op="UNION")

# ストッパーペグ
peg_y = FLANGE_BACK_Y - STOP_PEG_LEN / 2
peg = add_cyl_y(STOP_PEG_R, STOP_PEG_LEN, (0, peg_y, AXIS_Z + STOP_PCD_R), "peg")
boolean(rotor, peg, op="UNION")

# フランジ ボルト穴（仮の汎用パターン）
for i in range(FLANGE_N_HOLE):
    a = 2 * math.pi * i / FLANGE_N_HOLE + math.pi / 4
    hx = FLANGE_PCD_R * math.cos(a)
    hz = AXIS_Z + FLANGE_PCD_R * math.sin(a)
    hole = add_cyl_y(FLANGE_HOLE_R, FLANGE_T + 0.002,
                     (hx, (FLANGE_BACK_Y + FLANGE_FRONT_Y) / 2, hz), "fhole")
    boolean(rotor, hole)

# ============================================================
# ピッチピン（別パーツ ×2）= 外から 608 経由でキャリッジへ差し込む
# 構成: 軸部(608内輪→キャリッジ圧入) + 外端ヘッド(抜け止め+駆動結合面)
# ============================================================
PIN_HEAD_R = 0.006
PIN_HEAD_T = 0.002
for sx in (-1, +1):
    pin_cx = sx * (STUB_PIN_IN + STUB_PIN_LEN / 2)
    pin = add_cyl_x(STUB_PIN_R, STUB_PIN_LEN, (pin_cx, PITCH_Y, PITCH_Z), "pitch_pin")
    head_cx = sx * (STUB_PIN_OUT + PIN_HEAD_T / 2)
    head = add_cyl_x(PIN_HEAD_R, PIN_HEAD_T, (head_cx, PITCH_Y, PITCH_Z), "pin_head")
    boolean(pin, head, op="UNION")
    # 駆動結合用フラット（ヘッド外側面を平らに削る = 後でサーボホーン等を当てる）
    fcut = add_box(PIN_HEAD_R * 3, PIN_HEAD_R * 3, PIN_HEAD_R,
                   location=(head_cx, PITCH_Y, PITCH_Z + PIN_HEAD_R + (STUB_PIN_R - DCUT_FLAT)),
                   name="pin_flat")
    boolean(pin, fcut)

# ============================================================
# 608 placeholder（視覚確認用・印刷対象外）
# ============================================================
# ロール用（Y軸）×2
for wy in (WALL_BACK_Y, WALL_FRONT_Y):
    ring = add_cyl_y(BRG_OD / 2, BRG_W, (0, wy, AXIS_Z), "r_brg")
    rbore = add_cyl_y(BRG_ID / 2, BRG_W + 0.002, (0, wy, AXIS_Z), "r_brg_bore")
    boolean(ring, rbore)
# ピッチ用（X軸）×2
for sx in (-1, +1):
    cx = sx * (POST_OUTER_X - BRG_W / 2)
    ring = add_cyl_x(BRG_OD / 2, BRG_W, (cx, PITCH_Y, PITCH_Z), "p_brg")
    rbore = add_cyl_x(BRG_ID / 2, BRG_W + 0.002, (cx, PITCH_Y, PITCH_Z), "p_brg_bore")
    boolean(ring, rbore)

export_stl("wrist-rotator")
