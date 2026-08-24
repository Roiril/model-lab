"""servo-arm — 肩・肘に 1 個ずつサーボを置いた片腕（2 自由度）。

構成（印刷パーツ 3 個）:
  base   … 土台。肩サーボを縦板（デッキ）に留め、反対側にピボットピンを立てる
  upper  … 上腕。肩側はホーン受け＋ピン受けの二枚頬でサーボを挟み、肘側は駆動側になる
  fore   … 前腕。肘側は同じ二枚頬。先端は手先フランジ（ハンドや 3 個目の関節用）

関節は肩・肘とも同一のモジュール。駆動側（サーボを持つ方）と従動側（ホーンで回される方）が
噛み合う形で、寸法はすべて params.py のサーボ実寸から出す。別のサーボへ替えるときは
params.py の SERVO_* / HORN_* だけ直せば、関節幅・逃げ・結合面の高さが全部追従する。

組み立ての順（この順でないと入らない）:
  1. サーボをデッキの羽根座へ +X 側から差し込み、M2 タッピング 2 本で留める
  2. ホーンを従動側の頬板の溝へ落とし、長穴から M2 タッピング 2 本で留める
  3. リンクを軸方向へ差し込む。ピンが反対側の頬板の穴へ、ホーンがスプラインへ同時に入る
     （サーボは中立位置にしてから。腕の向きはスプラインの歯 1 個ぶん＝約 14° 刻みで決まる）
  4. 頬板の天面のザグリからセンタービスを締めて、頬板ごとホーンを軸へ固定する

座標: X = 関節軸（左右）／ Y = 腕の伸びる向き／ Z = 上。
各リンクは「自分のローカル系（関節が原点・梁が +Y・軸が X）」で組んでから、
プレビュー用に姿勢角へ回す。印刷用 STL はローカル系のまま（＝底が平らな向き）で書き出す。
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
from servo_core import (
    add_cyl, add_box, boolean,
    cut_servo_mount, cut_horn_coupling, add_servo_dummy, add_horn_dummy,
)
from params import *

MM = 0.001

# ============================================================
# サーボ / ホーンのプロファイル（params の mm 値 → m の名前空間）
# servo_core.SERVO を差し替えるので、servo_core 側の関数もこの実寸で動く
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

HORN = types.SimpleNamespace(
    TYPE="cross",
    ARM_SPAN_X=HORN_SPAN_LONG * MM,
    ARM_SPAN_Y=HORN_SPAN_SHORT * MM,
    ARM_W_X=HORN_ARM_W_LONG * MM,
    ARM_W_Y=HORN_ARM_W_SHORT * MM,
    HUB_DIA=HORN_HUB_DIA * MM,
    THICKNESS=HORN_T * MM,
    ROUND_DIA=HORN_SPAN_LONG * MM,
    SCREW_DIA=HORN_SCREW_DIA * MM,
    COUNTERBORE_DIA=HORN_CBORE_DIA * MM,
    SEAT_LEDGE=HORN_CBORE_LEDGE * MM,
)
servo_core.HORN = HORN

# ============================================================
# 派生寸法（すべて m）。サーボが変わっても成立するよう下限で自動補正する
# ============================================================
CLR = SERVO_CLR * MM

# --- 軸方向（X）の積み上げ。X=0 をデッキ上面に取る -------------------------
X_DECK_TOP = 0.0
X_DECK_BOT = -DECK_T * MM
X_BODY_BOT = -SERVO.FLANGE_FROM_BOTTOM                 # サーボ本体の底
X_CHEEK_A1 = X_BODY_BOT - GAP_SERVO * MM               # 従動 頬板（ピン側）の内面
X_CHEEK_A0 = X_CHEEK_A1 - CHEEK_A_T * MM
X_PIVOT1 = X_CHEEK_A0 - GAP_ROT * MM                   # 駆動 ピボット腕の内面
X_PIVOT0 = X_PIVOT1 - PIVOT_T * MM
X_COUPLING = SERVO.NUB_ABOVE_DECK + SERVO.BOSS_H + SERVO.SHAFT_H   # ホーン下面
X_CHEEK_B1 = X_COUPLING + CHEEK_B_T * MM               # 従動 頬板（ホーン側）の外面
JOINT_WIDTH = X_CHEEK_B1 - X_PIVOT0

# --- 断面（Z）。梁・背板・頬板・デッキの高さを揃えて底を平らにする ----------
BEAM_HH = max(BEAM_H * MM, HORN.ARM_SPAN_Y + 0.005) / 2   # 梁の半分の高さ = 頬板の半幅
WEB_HH = BEAM_HH

# --- 半径方向。回転して当たらない最小値へ引き上げる ------------------------
# デッキ上に出るサーボ角ケースの最遠角（従動側はこの外を回る）
NUB_R = math.hypot(SERVO.BODY_L / 2 + SERVO.SHAFT_OFFSET, SERVO.BODY_W / 2)
DECK_FRONT = max(DECK_FRONT_R * MM, SERVO.FLANGE_L / 2 - SERVO.SHAFT_OFFSET + 0.0025)
# デッキ・支柱・ピボット腕の半幅。梁より狭いと印刷時に底面から浮いてサポートが要るので
# 梁の高さに揃える（サーボ穴のまわりの肉も増える）
DECK_HW = max(DECK_W * MM / 2, (SERVO.BODY_W + 2 * CLR + 0.006) / 2, BEAM_HH)
DECK_CORNER = math.hypot(DECK_FRONT, DECK_HW)                        # 前側の角の半径

R_WEB_IN = max(R_WEB * MM, NUB_R + 0.0015, DECK_CORNER + 0.002)      # 背板の内半径
R_JOINT = max(R_HUB * MM, R_WEB_IN + WEB_T * MM,
              HORN.ARM_SPAN_X / 2 + 0.0025)                          # 従動 頬板の最大半径
R_SPINE_IN = max(SPINE_IN * MM, R_JOINT + 0.002)                     # 駆動 支柱の内半径
R_BACK = max(DECK_BACK * MM, SERVO.FLANGE_L / 2 + SERVO.SHAFT_OFFSET + 0.003,
             R_SPINE_IN + 0.004)                                     # デッキ・支柱の後ろ端
R_PIVOT_DISK = PIN_DIA * MM / 2 + 0.004

BEAM_X0 = X_CHEEK_A0 + 0.0004      # 梁の X 範囲（両リンク共通）。頬板・デッキの
BEAM_X1 = X_DECK_TOP - 0.0004      # 外面と面一にすると boolean が壊れるので 0.4mm 逃がす
BEAM_XC = (BEAM_X0 + BEAM_X1) / 2

PIN_R = PIN_DIA * MM / 2
PIN_LEN = X_CHEEK_A1 - X_PIVOT1
LINK_M = LINK * MM
BEAM_FAR = R_SPINE_IN - 0.0005      # 駆動関節側での梁の先端半径（支柱に食い込ませる）


# ============================================================
# プリミティブ
# ============================================================
def _activate(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    return o


def place(o, mat):
    """行列で置き直して適用する。"""
    o.matrix_world = mat @ o.matrix_world
    _activate(o)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o


def servo_mat(ang, oy=0.0, oz=0.0):
    """servo_core のフレーム（Z=出力軸・上面 z=0）→ リンクのローカル系。

    出力軸は +X を向き、サーボの尻尾（羽根の長い方）は YZ 平面の角度 ang を向く。
    """
    return (Matrix.Translation((0.0, oy, oz))
            @ Matrix.Rotation(ang - math.pi / 2, 4, "X")
            @ Matrix.Rotation(math.pi / 2, 4, "Y"))


def box_range(x0, x1, y0, y1, z0, z1, name):
    return add_box(x1 - x0, y1 - y0, z1 - z0,
                   ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), name)


def cyl_x(r, x0, x1, y, z, name, verts=96):
    """X 軸に沿った円柱。"""
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=abs(x1 - x0), vertices=verts,
                                        location=(0, 0, 0), rotation=(0, math.pi / 2, 0))
    o = bpy.context.active_object
    o.location = ((x0 + x1) / 2, y, z)
    _activate(o)
    bpy.ops.object.transform_apply(location=True, rotation=True)
    o.name = name
    return o


def cyl_y(r, y0, y1, x, z, name, verts=32):
    """Y 軸に沿った円柱。"""
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=abs(y1 - y0), vertices=verts,
                                        location=(0, 0, 0), rotation=(math.pi / 2, 0, 0))
    o = bpy.context.active_object
    o.location = (x, (y0 + y1) / 2, z)
    _activate(o)
    bpy.ops.object.transform_apply(location=True, rotation=True)
    o.name = name
    return o


def cone_x(r0, r1, x0, x1, y, z, name, verts=64):
    """X 軸に沿った円錐台（-X 端が r0、+X 端が r1）。"""
    bpy.ops.mesh.primitive_cone_add(radius1=r0, radius2=r1, depth=abs(x1 - x0), vertices=verts,
                                    location=(0, 0, 0), rotation=(0, math.pi / 2, 0))
    o = bpy.context.active_object
    o.location = ((x0 + x1) / 2, y, z)
    _activate(o)
    bpy.ops.object.transform_apply(location=True, rotation=True)
    o.name = name
    return o


def radial_box(x0, x1, r0, r1, hw, ang, oy, oz, name):
    """関節中心 (oy,oz) から角度 ang の向きへ r0..r1、接線方向 ±hw の箱。"""
    o = box_range(x0, x1, r0, r1, -hw, hw, name)
    return place(o, Matrix.Translation((0.0, oy, oz)) @ Matrix.Rotation(ang, 4, "X"))


def clean(ob, dist=1e-5):
    """boolean が残す重複頂点・ゼロ長エッジを掃除する。

    これを挟まないと non-manifold のまま次の boolean に入り、EXACT が
    まるごと誤った結果（穴がふさがる等）を返すことがある。
    """
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


def cut(a, b):
    boolean(a, b)
    return clean(a)


def prism_x(name, poly, x0, x1):
    """(y, z) の閉じた多角形を X 方向へ押し出す。boolean を使わないので確実に多様体。"""
    bm = bmesh.new()
    lo = [bm.verts.new((x0, y, z)) for y, z in poly]
    hi = [bm.verts.new((x1, y, z)) for y, z in poly]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def prism_z(name, poly, z0, z1):
    """(x, y) の閉じた多角形を Z 方向へ押し出す。"""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in poly]
    hi = [bm.verts.new((x, y, z1)) for x, y in poly]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.faces.new(list(reversed(lo)))
    bm.faces.new(hi)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def stadium_poly(half_len, half_w, seg=24):
    """長円の輪郭（第1座標に長い）。

    箱＋円柱の UNION だと円柱が箱の面に接して（接線）degenerate なエッジが残るので、
    輪郭を直接ポリゴンで作って押し出す。
    """
    r = min(half_w, half_len)
    c = half_len - r
    pts = []
    for i in range(seg + 1):
        a = -math.pi / 2 + math.pi * i / seg
        pts.append((c + r * math.cos(a), r * math.sin(a)))
    for i in range(seg + 1):
        a = math.pi / 2 + math.pi * i / seg
        pts.append((-c + r * math.cos(a), r * math.sin(a)))
    return pts


def stadium_x(x0, x1, half_len, half_w, oy, oz, name, seg=24):
    """X 軸方向に押し出した長円（Y に長く、Z に ±half_w）。頬板の外形。"""
    poly = [(oy + a, oz + b) for a, b in stadium_poly(half_len, half_w, seg)]
    return prism_x(name, poly, x0, x1)


# ============================================================
# 駆動側（サーボを持つ方）: デッキ + ピボット腕 + 支柱
# ============================================================
def build_driver(ang, oy, oz, tag):
    """関節 (oy,oz) の駆動側パーツを作って返す（呼び出し側で本体へ UNION）。

    ang: サーボの尻尾と支柱が向く方向（リンク YZ 平面の角度）。ここが可動域の死角になる。
    """
    # --- デッキ（サーボフレームで作る。上面 z=0・尻尾は -X）---
    deck = box_range(-R_BACK, DECK_FRONT, -DECK_HW, DECK_HW, -DECK_T * MM, 0.0, tag + "_deck")
    cut_servo_mount(deck, deck_top_z=0.0, deck_t=DECK_T * MM, clr=CLR,
                    screws=True, wire_notch_w=0.0)
    place(deck, servo_mat(ang, oy, oz))

    # --- ピボット腕（ピンが生える板）---
    arm = cyl_x(R_PIVOT_DISK, X_PIVOT0, X_PIVOT1, oy, oz, tag + "_pivot")
    tail = radial_box(X_PIVOT0, X_PIVOT1, 0.0, R_BACK, DECK_HW, ang, oy, oz, tag + "_pivot_tail")
    union(arm, tail)
    union(deck, arm)

    # --- 支柱（ピボット腕とデッキをつなぐ。従動側の回転半径の外を通す）---
    spine = radial_box(X_PIVOT0 + 0.0004, X_DECK_TOP - 0.0004, R_SPINE_IN, R_BACK,
                       DECK_HW, ang, oy, oz, tag + "_spine")
    union(deck, spine)

    # --- ピボットピン（従動頬板の穴に入る）---
    # 先端を細らせる。差し込みの誘いになり、横向きに刷ったときの下側の垂れも吸収する
    pin = cone_x(PIN_R, PIN_R - PIN_TAPER * MM, X_PIVOT1, X_CHEEK_A1, oy, oz,
                 tag + "_pin", verts=64)
    union(deck, pin)
    return deck


# ============================================================
# 従動側（ホーンで回される方）: 二枚の頬板 + 背板
# ============================================================
def build_driven(tag):
    """リンクのローカル原点にある従動側パーツを作って返す（梁は呼び出し側）。"""
    # --- ピン側の頬板 ---
    cheek_a = stadium_x(X_CHEEK_A0, X_CHEEK_A1, R_JOINT, BEAM_HH, 0.0, 0.0, tag + "_cheek_a")
    bore = cyl_x(PIN_R + PIN_CLR * MM, X_CHEEK_A0 - 0.002, X_CHEEK_A1 + 0.002, 0.0, 0.0,
                 tag + "_bore", verts=64)
    cut(cheek_a, bore)

    # --- ホーン側の頬板（サーボフレームで彫ってから寝かせる）---
    cheek_b = stadium_x(X_COUPLING, X_CHEEK_B1, R_JOINT, BEAM_HH, 0.0, 0.0, tag + "_cheek_b")
    # servo_core の受け溝は「長腕 = servo X・軸 = servo Z」の前提で彫る。
    # 頬板をいったんサーボフレームへ戻して彫り、リンク系へ戻す。
    # servo_mat(pi) では servo X → リンク Y なので、長腕は腕の伸びる向きに寝る。
    place(cheek_b, servo_mat(math.pi).inverted())
    cut_horn_coupling(cheek_b, coupling_z=X_COUPLING, clr=CLR, horn=HORN, screw=True)
    # 腕ビスは長穴。実物のホーンは穴ピッチが個体で違うので、
    # HORN_ARM_SCREW_R ± HORN_ARM_SLOT/2 のどの穴でも通るようにする
    for i in range(int(HORN_ARM_SCREW_N)):
        sx = 1 if i % 2 == 0 else -1
        poly = [(sx * HORN_ARM_SCREW_R * MM + pa, pb) for pa, pb in
                stadium_poly(HORN_ARM_SLOT * MM / 2, HORN_ARM_SCREW_DIA * MM / 2, seg=12)]
        slot = prism_z(tag + "_hs", poly, X_COUPLING - 0.002, X_CHEEK_B1 + 0.002)
        cut(cheek_b, slot)
    place(cheek_b, servo_mat(math.pi))                 # → リンク系へ戻す
    union(cheek_a, cheek_b)

    # --- 背板（二枚の頬板をつなぐ。梁へ荷重を渡す）---
    web = box_range(X_CHEEK_A0, X_CHEEK_B1, R_WEB_IN, R_JOINT, -WEB_HH, WEB_HH, tag + "_web")
    union(cheek_a, web)
    return cheek_a


def lighten(part, y0, y1, tag):
    """梁に肉抜きの丸穴を開ける。軽くなるぶん肩のトルクが浮く。

    穴は横向き（X 貫通）なので、印刷時の天井はアーチになりサポートが要らない。
    結束バンドを通して配線をまとめる穴も兼ねる。
    """
    if not BEAM_HOLE:
        return
    wall = BEAM_WALL * MM
    r = BEAM_HH - wall
    lo, hi = y0 + wall, y1 - wall
    avail = hi - lo
    if r <= 0.002 or avail <= 2 * r:
        return
    n = int((avail + wall) // (2 * r + wall))
    step = avail / n
    for i in range(n):
        h = cyl_x(r, BEAM_X0 - 0.002, BEAM_X1 + 0.002, lo + step * (i + 0.5), 0.0,
                  tag + "_lighten", verts=48)
        cut(part, h)


# ============================================================
# パーツ 1: 土台（肩の駆動側）
# ============================================================
SH_Z = SHOULDER_Z * MM


def build_base():
    bx0, bx1 = X_PIVOT0, X_CHEEK_B1
    cx = (bx0 + bx1) / 2
    plate = box_range(cx - BASE_W * MM / 2, cx + BASE_W * MM / 2,
                      BASE_FRONT * MM - BASE_D * MM, BASE_FRONT * MM,
                      0.0, BASE_T * MM, "base")
    # 卓上固定穴（四隅）
    ins = BASE_HOLE_INSET * MM
    for sx in (-1, 1):
        for hy in (BASE_FRONT * MM - ins, BASE_HOLE_REAR_Y * MM):
            hx = cx + sx * (BASE_W * MM / 2 - ins)
            h = add_cyl(BASE_HOLE_DIA * MM / 2, BASE_T * MM + 0.004, BASE_T * MM / 2,
                        "base_hole", verts=32, location=(hx, hy, BASE_T * MM / 2))
            cut(plate, h)

    # おもり入れ（後ろの箱）。腕を前へ伸ばすと前へ倒れるので、卓上固定しないなら
    # ここに重りを入れて釣り合わせる。前壁は支柱に食い込ませて一体にする
    if BALLAST_H > 0:
        bhw, bd = BALLAST_W * MM / 2, BALLAST_D * MM
        bh, bwall = BALLAST_H * MM, BALLAST_WALL * MM
        iy0 = BASE_FRONT * MM - BASE_D * MM + bwall + 0.001
        iy1 = iy0 + bd
        box = box_range(cx - bhw - bwall, cx + bhw + bwall, iy0 - bwall, iy1 + bwall,
                        BASE_T * MM / 2, BASE_T * MM + bh, "ballast")
        union(plate, box)
        cav = box_range(cx - bhw, cx + bhw, iy0, iy1,
                        BASE_T * MM, BASE_T * MM + bh + 0.002, "ballast_cav")
        cut(plate, cav)

    # 支柱（土台から肩まで）。上端は肩の回転半径で削り取る
    col = box_range(X_PIVOT0 + 0.0004, X_DECK_TOP - 0.0004,
                    -COLUMN_W * MM / 2, COLUMN_W * MM / 2,
                    BASE_T * MM / 2, SH_Z, "column")
    clear = cyl_x(R_JOINT + 0.0015, X_PIVOT0 - 0.002, X_CHEEK_B1 + 0.002, 0.0, SH_Z,
                  "col_clear", verts=96)
    cut(col, clear)
    union(plate, col)

    # 肩の駆動側（サーボの尻尾と支柱は真下 = 可動域の死角を下へ逃がす）
    drv = build_driver(-math.pi / 2, 0.0, SH_Z, "sh")
    union(plate, drv)
    plate.name = "base"
    return plate


# ============================================================
# パーツ 2: 上腕（肩=従動 / 肘=駆動）
# ============================================================
def build_upper():
    part = build_driven("up")
    beam = box_range(BEAM_X0, BEAM_X1, R_WEB_IN, LINK_M - BEAM_FAR, -BEAM_HH, BEAM_HH,
                     "up_beam")
    union(part, beam)
    lighten(part, R_WEB_IN, LINK_M - R_BACK, "up")   # 肘の支柱より手前まで
    drv = build_driver(math.pi, LINK_M, 0.0, "el")   # 肘の死角は肩側（腕をたたむ向き）
    union(part, drv)
    part.name = "upper"
    return part


# ============================================================
# パーツ 3: 前腕（肘=従動 / 先端=手先フランジ）
# ============================================================
def build_fore():
    part = build_driven("fo")
    beam = box_range(BEAM_X0, BEAM_X1, R_WEB_IN, LINK_M - TIP_T * MM, -BEAM_HH, BEAM_HH,
                     "fo_beam")
    union(part, beam)
    lighten(part, R_WEB_IN, LINK_M - TIP_T * MM, "fo")

    tip = box_range(BEAM_XC - TIP_W * MM / 2, BEAM_XC + TIP_W * MM / 2,
                    LINK_M - TIP_T * MM, LINK_M, -TIP_H * MM / 2, TIP_H * MM / 2, "fo_tip")
    for sx in (-1, 1):
        for sz in (-1, 1):
            hole = cyl_y(TIP_HOLE_DIA * MM / 2, LINK_M - TIP_T * MM - 0.002, LINK_M + 0.002,
                         BEAM_XC + sx * TIP_HOLE_PX * MM / 2, sz * TIP_HOLE_PZ * MM / 2,
                         "tip_hole")
            cut(tip, hole)
    union(part, tip)
    part.name = "fore"
    return part


# ============================================================
# 組み立て
# ============================================================
clear_scene()

base = build_base()
upper = build_upper()
fore = build_fore()

# --- 印刷用 STL（ローカル系のまま = 底が平らな向き）---
for obj, fname in ((base, "servo-arm-base"), (upper, "servo-arm-upper"), (fore, "servo-arm-fore")):
    _activate(obj)
    path = os.path.join(blender_utils.EXPORTS_DIR, fname + ".stl")
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True, global_scale=1000.0)
    d = obj.dimensions
    print(f"[part] {fname}: {d.x * 1000:.1f} x {d.y * 1000:.1f} x {d.z * 1000:.1f} mm")

# --- プレビュー姿勢へ回す ---
a_sh = math.radians(POSE_SHOULDER)
a_el = a_sh + math.radians(POSE_ELBOW)
M_UP = Matrix.Translation((0.0, 0.0, SH_Z)) @ Matrix.Rotation(a_sh, 4, "X")
elbow_w = M_UP @ Matrix.Translation((0.0, LINK_M, 0.0))
M_FO = Matrix.Translation(elbow_w.to_translation()) @ Matrix.Rotation(a_el, 4, "X")

place(upper, M_UP)
place(fore, M_FO)

# --- サーボ / ホーンのダミー（確認用。印刷パーツではない）---
if SHOW_SERVO:
    sv_sh = add_servo_dummy(flange_top_z=0.0, name="servo_sh", prof=SERVO)
    place(sv_sh, servo_mat(-math.pi / 2, 0.0, SH_Z))
    hn_sh = add_horn_dummy(prof=HORN, name="horn_sh", base_z=X_COUPLING)
    place(hn_sh, M_UP @ servo_mat(math.pi))

    sv_el = add_servo_dummy(flange_top_z=0.0, name="servo_el", prof=SERVO)
    place(sv_el, M_UP @ servo_mat(math.pi, LINK_M, 0.0))
    hn_el = add_horn_dummy(prof=HORN, name="horn_el", base_z=X_COUPLING)
    place(hn_el, M_FO @ servo_mat(math.pi))

print(f"[joint] 幅 {JOINT_WIDTH * 1000:.1f}mm / 頬板半径 {R_JOINT * 1000:.1f}mm "
      f"/ 背板内半径 {R_WEB_IN * 1000:.1f}mm / 支柱内半径 {R_SPINE_IN * 1000:.1f}mm")
print(f"[joint] ホーン結合面 デッキ上 {X_COUPLING * 1000:.1f}mm / "
      f"サーボ上部の回転逃げ半径 {NUB_R * 1000:.1f}mm")
print(f"[link]  関節間 {LINK:.0f}mm / 梁 {(BEAM_X1 - BEAM_X0) * 1000:.1f} x "
      f"{BEAM_HH * 2000:.1f}mm")

export_stl("servo-arm")
