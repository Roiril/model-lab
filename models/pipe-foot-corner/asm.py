"""角一式を組んだ状態の確認用 STL（印刷には使わない）。

    ./run.sh models/pipe-foot-corner/asm.py  →  exports/pipe_foot_corner_asm.stl

部品の STL（M 字・エルボ・板）を読んで params の配置に置き、パイプを円柱で足す。
脚は ASM_LEG_L に縮めてある（実物は約 900）。世界座標は params の docstring と同じ:
角の節点が原点、A の脚が x 軸上の負側、B の脚が y 軸上の負側、床が z=0。
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
import bmesh
from mathutils import Matrix, Vector
from blender_utils import clear_scene, EXPORTS_DIR
import foot_core as fc
from params import PAIR as P, CORNER as C, CORNER_OFF, FIFTH_OFF, TIE_L, TIE_Z, TIE_T

J = P.J                                   # pipe-joint の params
MM = P.MM
ASM_LEG_L = 300.0                         # 脚パイプの長さ（確認用に短く）
ASM_RAIL_EXT = 120.0                      # レールを M 字の絞る面から壁側へ出す長さ
ASM_FIFTH_ABOVE = 60.0                    # 5 本目を中央レールの軸より上へ出す量
T_SOCKET_OD = 37.0                        # 5 本目の側面ソケット（市販継手）の外径（仮）

H_CENTER = P.SEAT_Z + ASM_LEG_L - J.LEG_TOP_Z    # 中央レールの軸の高さ
H_SIDE = H_CENTER + J.SIDE_Z                      # 左右レールの軸の高さ
MC = CORNER_OFF + P.SPAN / 2                      # M 字の中心（脚 2 本の中点）の、軸線からの距離
ARC_C = -(CORNER_OFF - C.R_INNER)                 # 同心の中心 (ARC_C, ARC_C)
F = (-FIFTH_OFF, -FIFTH_OFF)                      # 5 本目
A_LEGS = [(-CORNER_OFF, 0.0), (-CORNER_OFF - P.SPAN, 0.0)]
B_LEGS = [(0.0, -CORNER_OFF), (0.0, -CORNER_OFF - P.SPAN)]


def load_stl(name, filename):
    path = os.path.join(EXPORTS_DIR, filename)
    assert os.path.exists(path), f"先に部品を出しておく: {path}"
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.stl_import(filepath=path, global_scale=0.001)
    ob = bpy.context.selected_objects[0]
    ob.name = name
    return ob


def place(ob, rot_z_deg, tx, ty, tz):
    ob.matrix_world = (Matrix.Translation(Vector((tx, ty, tz)) * MM)
                       @ Matrix.Rotation(math.radians(rot_z_deg), 4, "Z") @ ob.matrix_world)
    fc.activate(ob)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return ob


def pipe(name, p0, p1, r=P.PIPE_OD / 2):
    """p0 → p1（mm）の円柱。"""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    ob = fc.revolve(name, [(0.0, r), (d.length, r)], None, 48)
    ob.matrix_world = Matrix.Translation(a * MM) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    fc.activate(ob)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return ob


clear_scene()
parts = []

# --- 板 2 枚と添え板 ---
# 板 A: ローカルは脚が x=±80、3 本目が (0, +FIFTH_OFF)。180° 回して中心を (-MC, 0) へ
parts.append(place(load_stl("base_a", "pipe_foot_corner_a.stl"), 180, -MC, 0, 0))
# 板 B: ローカルは脚が x=±80。90° 回して中心を (0, -MC) へ
parts.append(place(load_stl("base_b", "pipe_foot_corner_b.stl"), 90, 0, -MC, 0))
# 添え板: ローカルは穴が (0,0) と (TIE_L, 0)。A1 から B1 へ -45°。ひれの上 z=TIE_Z に乗る
parts.append(place(load_stl("tie", "pipe_foot_corner_tie.stl"), -45, A_LEGS[0][0], A_LEGS[0][1], TIE_Z))

# --- M 字 2 つ（設計の向きの STL: レール = X、脚の並び = Y、上 = Z。脚の軸は X = LEG_X）---
# A: レールは世界 y。平らな面（-X）を角（-y）へ。ローカル +X → 世界 +y は Rz(+90)。
#    脚の軸（ローカル X = LEG_X）が世界 y = 0 に来るよう y に -LEG_X を足す
parts.append(place(load_stl("joint_a", "pipe_joint_28.stl"), 90, -MC, -J.LEG_X, H_CENTER))
# B: レールは世界 x。平らな面を角（-x）へ。ローカル +X → 世界 +x（回さない）
parts.append(place(load_stl("joint_b", "pipe_joint_28.stl"), 0, -J.LEG_X, -MC, H_CENTER))

# --- エルボ 2 つ（ローカル: 円弧の中心が原点、口は -x と -y を向く。世界では +x / +y を向く）---
for name, fn in (("elbow_in", "pipe_corner_in_28.stl"), ("elbow_out", "pipe_corner_out_28.stl")):
    parts.append(place(load_stl(name, fn), 180, ARC_C, ARC_C, H_SIDE))

# --- パイプ ---
for i, (x, y) in enumerate(A_LEGS + B_LEGS):
    parts.append(pipe("leg%d" % i, (x, y, P.SEAT_Z), (x, y, P.SEAT_Z + ASM_LEG_L)))
parts.append(pipe("fifth", (F[0], F[1], P.SEAT_Z), (F[0], F[1], H_CENTER + ASM_FIFTH_ABOVE)))
# 5 本目の側面ソケット（+y = A の面へ、+x = B の面へ）
r_pipe = P.PIPE_OD / 2
parts.append(pipe("tsock_a", (F[0], F[1] + r_pipe, H_CENTER), (F[0], F[1] + r_pipe + P.SIDE_JOINT_L, H_CENTER), T_SOCKET_OD / 2))
parts.append(pipe("tsock_b", (F[0] + r_pipe, F[1], H_CENTER), (F[0] + r_pipe + P.SIDE_JOINT_L, F[1], H_CENTER), T_SOCKET_OD / 2))
# レール。A の 3 本は x = 脚の軸 / 中心、壁側の端は絞る面（y = -LEG_X + X_TOP）から ASM_RAIL_EXT
y_wall = -J.LEG_X + J.X_TOP + ASM_RAIL_EXT
x_wall = -J.LEG_X + J.X_TOP + ASM_RAIL_EXT
for k, x in enumerate((A_LEGS[0][0], A_LEGS[1][0])):          # A の左右レール → エルボの接点まで
    parts.append(pipe("rail_a%d" % k, (x, y_wall, H_SIDE), (x, ARC_C, H_SIDE)))
parts.append(pipe("rail_a_c", (-MC, y_wall, H_CENTER), (-MC, F[1] + r_pipe + P.SIDE_JOINT_L - 25, H_CENTER)))
for k, y in enumerate((B_LEGS[0][1], B_LEGS[1][1])):
    parts.append(pipe("rail_b%d" % k, (x_wall, y, H_SIDE), (ARC_C, y, H_SIDE)))
parts.append(pipe("rail_b_c", (x_wall, -MC, H_CENTER), (F[0] + r_pipe + P.SIDE_JOINT_L - 25, -MC, H_CENTER)))

# --- 1 つにまとめて書き出す（boolean はしない。重なったままの別々の殻）---
bpy.ops.object.select_all(action="DESELECT")
for ob in parts:
    ob.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
asm = bpy.context.active_object
asm.name = "pipe_foot_corner_asm"

os.makedirs(EXPORTS_DIR, exist_ok=True)
stl = os.path.join(EXPORTS_DIR, "pipe_foot_corner_asm.stl")
bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True, global_scale=1000.0, ascii_format=False)
print("Exported:", stl)
print("bbox mm:", [round(v * 1000, 2) for v in asm.dimensions])
print(f"[asm] 中央レールの軸 z={H_CENTER:.1f} / 左右レール z={H_SIDE:.1f} / 5 本目 {F} / 同心の中心 ({ARC_C}, {ARC_C})")
