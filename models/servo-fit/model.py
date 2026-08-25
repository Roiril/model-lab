"""servo-fit — サーボがはまるかだけ確かめる試し刷り。

servo-arm の関節から「サーボを留める板（デッキ）」だけを取り出し、クリアランス違いを
横に並べた 1 部品。板の厚み・穴・羽根座・ネジ下穴は servo-arm とまったく同じ手順
（servo_core.cut_servo_mount）で彫るので、ここで合った値がそのまま本番で使える。

⚠ 印刷の向きは servo-arm と同じ「板が立った状態」。このモデルはその向きのまま
  出力されるので、スライサーで回さずにそのまま並べること。寝かせて刷ると
  穴の天井の橋渡しと 1 層目のつぶれ方が変わり、試した意味が無くなる。

使い方:
  1. サーボをノギスで測って params.py の SERVO_* を書き換える
  2. 刷って、番号の小さい板（きつい方）から順にサーボを差してみる
     （線は先に穴へ通す。尻尾側の縁に線を逃がす溝があるので、そこへ寝かせる）
  3. 「羽根が座面にぴたりと着き、本体がガタつかない」板の番号を採用し、
     その SERVO_CLR を models/servo-arm/params.py へ書き写す
  4. ねじも試すなら M2 のタッピングを下から入れる（効き代 4.3mm）

番号は手前の縁の点の数。点 1 個 = SERVO_CLR - CLR_STEP（いちばんきつい）。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import types
import bpy
import bmesh
from mathutils import Matrix

import blender_utils
import servo_core
from blender_utils import clear_scene, export_stl
from servo_core import add_cyl, add_box, boolean, cut_servo_mount, add_servo_dummy
from params import *

MM = 0.001

# ============================================================
# サーボのプロファイル（params の mm 値 → m の名前空間）
# servo_core.SERVO を差し替えるので、穴あけも同じ実寸で動く
# ============================================================
SERVO = types.SimpleNamespace(
    BODY_L=SERVO_BODY_L * MM,
    BODY_W=SERVO_BODY_W * MM,
    BODY_H=SERVO_BODY_H * MM,
    SHAFT_OFFSET=SERVO_SHAFT_OFFSET * MM,
    FLANGE_L=SERVO_FLANGE_L * MM,
    FLANGE_W=SERVO_FLANGE_W * MM,
    FLANGE_T=SERVO_FLANGE_T * MM,
    FLANGE_FROM_BOTTOM=SERVO_FLANGE_FROM_BOTTOM * MM,
    SCREW_SPACING=SERVO_SCREW_SPACING * MM,
    SCREW_R=SERVO_SCREW_PILOT * MM / 2,
    TAB_HOLE_R=SERVO_TAB_HOLE * MM / 2,
    SHAFT_R=SERVO_SHAFT_DIA * MM / 2,
    BOSS_DIA=SERVO_BOSS_DIA * MM,
    BOSS_H=SERVO_BOSS_H * MM,
    SHAFT_DIA=SERVO_SHAFT_DIA * MM,
    SHAFT_H=SERVO_SHAFT_H * MM,
)
SERVO.SHAFT_ABOVE_CASE = SERVO.BOSS_H + SERVO.SHAFT_H
SERVO.NUB_ABOVE_DECK = SERVO.BODY_H - SERVO.FLANGE_FROM_BOTTOM
SERVO.SHAFT_ABOVE_DECK = SERVO.NUB_ABOVE_DECK + SERVO.SHAFT_ABOVE_CASE
servo_core.SERVO = SERVO


# ============================================================
# 道具（servo-arm と同じ流儀）
# ============================================================
def _activate(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    return o


def clean(ob, dist=1e-5):
    """boolean が残す重複頂点・ゼロ長エッジを掃除する（非多様体のまま次の
    boolean に入れると EXACT が黙って壊れた結果を返す）。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return ob


def union(a, b):
    boolean(a, b, op="UNION")
    return clean(a)


def place(o, mat):
    o.matrix_world = mat @ o.matrix_world
    _activate(o)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o


def servo_mat(ang, oy=0.0, oz=0.0):
    """servo_core のフレーム（Z=出力軸・上面 z=0）→ この模型の座標系。

    出力軸は +X を向き、サーボの尻尾は YZ 平面の角度 ang を向く。
    ang=-90° で尻尾が真下＝servo-arm の肩と同じ姿勢になる。
    """
    return (Matrix.Translation((0.0, oy, oz))
            @ Matrix.Rotation(ang - math.pi / 2, 4, "X")
            @ Matrix.Rotation(math.pi / 2, 4, "Y"))


def box_range(x0, x1, y0, y1, z0, z1, name):
    return add_box(x1 - x0, y1 - y0, z1 - z0,
                   ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), name)


# ============================================================
# 派生寸法（すべて m）
# ============================================================
N = max(1, int(N_VARIANTS))
CLRS = [(SERVO_CLR + (i - (N - 1) / 2) * CLR_STEP) * MM for i in range(N)]
CLR_MAX = max(CLRS)

# 板の外形。サーボが収まる最小値へ自動補正する
DECK_HW = max(DECK_W * MM, SERVO.BODY_W + 2 * CLR_MAX + 0.006) / 2
R_BACK = max(DECK_BACK * MM, SERVO.FLANGE_L / 2 + SERVO.SHAFT_OFFSET + 0.003)
DECK_FRONT = max(DECK_FRONT_R * MM, SERVO.FLANGE_L / 2 - SERVO.SHAFT_OFFSET + 0.0025)

FOOT_T_M = FOOT_T * MM
SHAFT_Z = R_BACK + FOOT_T_M * 0.4        # 板の下端が足の中に少し埋まる高さ
PITCH = 2 * DECK_HW + GAP * MM
YS = [(i - (N - 1) / 2) * PITCH for i in range(N)]

clear_scene()

# ============================================================
# 足（全部の板を載せる 1 枚）
# ============================================================
part = box_range(-FOOT_BACK * MM, FOOT_FRONT * MM,
                 YS[0] - DECK_HW - 0.002, YS[-1] + DECK_HW + 0.002,
                 0.0, FOOT_T_M, "servo_fit")

# ============================================================
# 板（クリアランス違い）+ 番号の点
# ============================================================
for i, (y, clr) in enumerate(zip(YS, CLRS)):
    # サーボフレームで彫ってから立てる（servo-arm のデッキと同一手順）
    wall = box_range(-R_BACK, DECK_FRONT, -DECK_HW, DECK_HW, -DECK_T * MM, 0.0, f"deck{i}")
    cut_servo_mount(wall, deck_top_z=0.0, deck_t=DECK_T * MM, clr=clr,
                    screws=True, wire_notch_w=WIRE_NOTCH_W * MM,
                    wire_notch_d=WIRE_NOTCH_D * MM)
    place(wall, servo_mat(-math.pi / 2, y, SHAFT_Z))
    union(part, wall)

    # 番号（点の数 = i+1。点 1 個がいちばんきつい）
    n_pip = i + 1
    for k in range(n_pip):
        py = y + (k - (n_pip - 1) / 2) * PIP_PITCH * MM
        pip = add_cyl(PIP_DIA * MM / 2, PIP_H * MM * 2, 0.0, "pip", verts=24,
                      location=(FOOT_FRONT * MM - PIP_DIA * MM, py, FOOT_T_M))
        union(part, pip)

# ============================================================
# 印刷用 STL（この向きのまま。回さない）
# ============================================================
_activate(part)
path = os.path.join(blender_utils.EXPORTS_DIR, "servo-fit-print.stl")
bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True, global_scale=1000.0)
d = part.dimensions
print(f"[part] servo-fit-print: {d.x * 1000:.1f} x {d.y * 1000:.1f} x {d.z * 1000:.1f} mm")
for i, clr in enumerate(CLRS):
    print(f"[variant] 点 {i + 1} 個 = クリアランス片側 {clr * 1000:.2f}mm "
          f"（本体穴 {(SERVO.BODY_L + 2 * clr) * 1000:.1f} x "
          f"{(SERVO.BODY_W + 2 * clr) * 1000:.1f}mm）")
print(f"[deck]  板厚 {DECK_T:.1f}mm / 羽根座の深さ {SERVO.FLANGE_T * 1000 + 0.5:.1f}mm / "
      f"ネジの効き代 {(DECK_T * MM - SERVO.FLANGE_T - 0.0005) * 1000:.1f}mm")

# ============================================================
# サーボ実体ダミー（プレビュー用。印刷 STL には入らない）
# ============================================================
if SHOW_SERVO:
    for y in YS:
        d = add_servo_dummy(flange_top_z=0.0, name="servo", prof=SERVO)
        place(d, servo_mat(-math.pi / 2, y, SHAFT_Z))

export_stl("servo-fit")
