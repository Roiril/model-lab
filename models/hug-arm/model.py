"""hug-arm — 抱きつくロボットの片腕（肩・肘の 2 自由度）。

印刷パーツ 4 個:
  bracket … 肩ブラケット。体の前板に平らに当てて 4 本で留める。サーボは板を貫く
  upper   … 上腕。肩側は従動（軸受けに差す）、肘側は駆動（サーボを持つ）
  fore    … 前腕。肘側は従動。内側へ曲げてあり、抱いた相手に面で当たる
  pad     … 前腕の縁にかぶせる TPU の袖。硬いまま抱かせない

関節の作り（servo-arm から変えたところ）:
  サーボのギアカバー座のまわりに軸受けリングを立て、従動側はその外周へ片持ちで
  差す。挟まないので軸方向にまっすぐ入る。servo-arm は二枚の頬板で挟んでおり、
  横入れのための逃げ 5.5mm が関節幅にそのまま乗って 50.1mm になっていた。

  X の並び（各関節のローカル。x=0 = サーボのケース上面）:
    -22.3  サーボ底
     -4.1  羽根の上面 ＝ デッキ板の内面（羽根はここに面で当たり、外から 2 本で留める）
      0.4  デッキ板の外面 ＝ 軸受けリングの根元
      0.8  従動側 平板の内面
      4.6  ギアカバー座の上面 ＝ 軸受けリングの先端
      6.6  ホーンの上面
      8.2  軸の先端
     10.3  従動側 平板の外面（長穴 2 本とセンタービスの通し穴をここから開ける）

組み立ての順:
  1. サーボをデッキ板の内面（-X 側）へ当て、M2 タッピング 2 本で外から留める
  2. ホーンを従動側の溝へ落とし、平板の長穴から M2 タッピング 2 本で留める
  3. サーボを中立にして、従動側を軸方向にまっすぐ差す（挟まないので横入れは不要）
  4. 平板の中央の穴からセンタービスを締めて、ホーンを軸へ固定する

座標: X = 関節軸 / Y = 腕の伸びる向き / Z = 面内の上（+ が閉じる向き）。
印刷用 STL は各パーツのローカル系のまま（＝平板が寝た向き）で書き出す。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import types
import bpy
import bmesh
from mathutils import Matrix, Vector

import blender_utils
from blender_utils import clear_scene
from servo_core import add_servo_dummy, add_horn_dummy
from mesh_ops import (
    activate, place, clean, union, cut, non_manifold, boolean,
    box_range, cyl_x, prism_x, chain_plate, arc_centers, hull2_poly,
)
from params import *

MM = 0.001
EPS = 0.0005
HORN_CBORE = 6.0        # センタービスの頭とドライバーが通る穴 ⌀
TPU_DENSITY = 1.21      # g/cm3

# ============================================================
# サーボ / ホーンのプロファイル（params の mm 値 → m の名前空間）
# ============================================================
SERVO = types.SimpleNamespace(
    BODY_L=SERVO_BODY_L * MM, BODY_W=SERVO_BODY_W * MM, BODY_H=SERVO_BODY_H * MM,
    SHAFT_OFFSET=SERVO_SHAFT_OFFSET * MM,
    FLANGE_L=SERVO_FLANGE_L * MM, FLANGE_W=SERVO_FLANGE_W * MM,
    FLANGE_T=SERVO_FLANGE_T * MM, FLANGE_FROM_BOTTOM=SERVO_FLANGE_FROM_BOTTOM * MM,
    SCREW_SPACING=SERVO_SCREW_SPACING * MM, SCREW_R=SERVO_SCREW_PILOT * MM / 2,
    TAB_HOLE_R=0.0015, SHAFT_R=SERVO_SHAFT_DIA * MM / 2,
    BOSS_DIA=SERVO_BOSS_DIA * MM, BOSS_H=SERVO_BOSS_H * MM,
    SHAFT_DIA=SERVO_SHAFT_DIA * MM, SHAFT_H=SERVO_SHAFT_H * MM,
)
SERVO.SHAFT_ABOVE_CASE = SERVO.BOSS_H + SERVO.SHAFT_H
SERVO.NUB_ABOVE_DECK = SERVO.BODY_H - SERVO.FLANGE_FROM_BOTTOM
SERVO.SHAFT_ABOVE_DECK = SERVO.NUB_ABOVE_DECK + SERVO.SHAFT_ABOVE_CASE

HORN = types.SimpleNamespace(
    TYPE="cross", T=HORN_T * MM, THICKNESS=HORN_T * MM, HUB_DIA=HORN_HUB_DIA * MM,
    ARM_SPAN_X=HORN_SPAN_LONG * MM, ARM_W_X=HORN_ARM_W_LONG * MM,
    ARM_SPAN_Y=HORN_SPAN_SHORT * MM, ARM_W_Y=HORN_ARM_W_SHORT * MM,
    SCREW_DIA=HORN_SCREW_DIA * MM,
)

# ============================================================
# 関節の X の並び（すべて「サーボのケース上面 = 0」からの距離）
# ============================================================
NUB = SERVO.BODY_H - SERVO.FLANGE_FROM_BOTTOM - SERVO.FLANGE_T   # 羽根上面〜ケース上面

# デッキがギアカバー座より厚いと、座が板に埋まって軸受けが成立しない。ここで頭打ち
JOURNAL_H_MIN = 0.0025
DECK = min(DECK_T * MM, NUB + SERVO.BOSS_H - JOURNAL_H_MIN)
X_DECK0 = -NUB
X_DECK1 = X_DECK0 + DECK
X_BOSS1 = SERVO.BOSS_H
X_HORN0, X_HORN1 = X_BOSS1, X_BOSS1 + HORN.T
X_SHAFT1 = SERVO.BOSS_H + SERVO.SHAFT_H
# servo_core の flange_top_z は羽根がデッキへ載る面（＝羽根の下面）。
# 上面だと思って渡すとダミーが羽根の厚みぶん浮く（2026-09-03 に実測で判明）
X_SEAT = X_DECK0 - SERVO.FLANGE_T

GAP_FACE = 0.0004                              # 回る面どうしの軸方向すきま
X_WEB0 = X_DECK1 + GAP_FACE
X_BORE1 = X_HORN1 + HORN_CLR * MM              # 軸受け穴の底
PLATE = max(PLATE_T * MM, X_BORE1 - X_WEB0 + LEDGE_T * MM)
X_WEB1 = X_WEB0 + PLATE

# ホーンは軸受け穴を通って奥へ落ちる。通るのは腕の先端ではなく「角」なので、
# 半span と半幅の合成で見る。ここを腕の長さだけで見ると角が引っかかる
R_HORN_SWEEP = math.hypot(HORN_SPAN_LONG * MM / 2, HORN_ARM_W_LONG * MM / 2)
R_BORE = max(JOURNAL_D * MM / 2 + JOURNAL_CLR * MM, R_HORN_SWEEP + HORN_CLR * MM)
R_JOURNAL = R_BORE - JOURNAL_CLR * MM
R_JOURNAL_IN = SERVO.BOSS_DIA / 2 + BOSS_CLR * MM
R_HUB = R_BORE + HUB_WALL * MM
R_BEAM = BEAM_W * MM / 2
R_SLOT = R_BEAM - SLOT_RAIL * MM

L1_M, L2_M = L1 * MM, L2 * MM
SERVO_CY = -SERVO.SHAFT_OFFSET                 # 本体の中心（Y）。尻尾は -Y へ向く
SERVO_SCREW_Y = (SERVO_CY + SERVO.SCREW_SPACING / 2, SERVO_CY - SERVO.SCREW_SPACING / 2)
SERVO_BODY_Y = (SERVO_CY - SERVO.BODY_L / 2, SERVO_CY + SERVO.BODY_L / 2)
# 羽根は本体より Y に長い（32.2 対 22.0）。逃げは羽根で決まる
SERVO_FLANGE_Y = (SERVO_CY - SERVO.FLANGE_L / 2, SERVO_CY + SERVO.FLANGE_L / 2)

# 駆動側は肩も肘も同じ形: 厚み PLATE の板、表面から DECK 内側に羽根の座、
# 座より裏はすべて逃げ。表面から軸受けリングが立つ
X_BRK0 = X_DECK1 - PLATE          # ブラケットの裏面
X_ELBOW_DECK1 = X_WEB1
X_ELBOW_DECK0 = X_WEB1 - DECK
X_ELBOW_CASE = X_ELBOW_DECK0 + NUB             # 肘サーボのケース上面（上腕ローカル）


# ============================================================
# 関節のフィーチャ
# ============================================================
def servo_mat(ang, oy=0.0, ox=0.0):
    """servo_core のフレーム（Z=出力軸）→ リンクのローカル系（X=出力軸）。

    ang はサーボ本体の尻尾が YZ 平面で向く角度。ang=π で -Y（腕の付け根側）。
    """
    return (Matrix.Translation((ox, oy, 0.0))
            @ Matrix.Rotation(ang - math.pi / 2, 4, "X")
            @ Matrix.Rotation(math.pi / 2, 4, "Y"))


def cut_deck(part, x_back, x_seat, x_out, oy=0.0):
    """駆動側: サーボの貫通穴・羽根の座ぐり・羽根を留めるタッピング下穴を彫る。

    羽根を板の外に出さず、板の裏側へ掘り込んだ座に落とす。こうすると
      - ブラケットの裏面が平らになり、体の板へそのまま当てられる
      - 板の表裏に出っ張りが無くなり、平らに寝かせて刷れる
    座の天井は羽根の縁の 5.1mm ぶんだけで、橋渡しで出る。

      x_back … 板の裏面（ここから羽根が入る）
      x_seat … 羽根の座（羽根の上面が当たる面）
      x_out  … 板の表面（軸受けリングが立つ側）
    """
    clr = SERVO_CLR * MM
    # 本体は板を貫く
    part = cut(part, box_range(x_back - EPS, x_out + EPS,
                               oy + SERVO_BODY_Y[0] - clr, oy + SERVO_BODY_Y[1] + clr,
                               -SERVO.BODY_W / 2 - clr, SERVO.BODY_W / 2 + clr,
                               "servo_hole"))
    # 羽根の座ぐり（裏面から x_seat まで）
    part = cut(part, box_range(x_back - EPS, x_seat,
                               oy + SERVO_FLANGE_Y[0] - clr, oy + SERVO_FLANGE_Y[1] + clr,
                               -SERVO.FLANGE_W / 2 - clr, SERVO.FLANGE_W / 2 + clr,
                               "flange_pocket"))
    for sy in SERVO_SCREW_Y:
        part = cut(part, cyl_x(SERVO.SCREW_R, x_seat - EPS, x_out + EPS, oy + sy, 0.0,
                               "pilot", verts=32))
    return part


def add_journal(part, x0, x1, oy=0.0):
    """駆動側: ギアカバー座のまわりに軸受けリングを立てる。従動側はここに乗る。

    根元を板の中へ 0.3mm 沈める。板の外面と面一で UNION すると同一平面になり、
    non-manifold のもとになる（見た目は変わらない）。
    """
    ring = cyl_x(R_JOURNAL, x0 - 0.0003, x1, oy, 0.0, "journal")
    ring = cut(ring, cyl_x(R_JOURNAL_IN, x0 - 0.001, x1 + EPS, oy, 0.0, "journal_in", verts=64))
    return union(part, ring)


def cut_driven(part, oy=0.0):
    """従動側: 軸受け穴・ホーンの溝・長穴・センタービスの通し穴を彫る。

    穴は 1 つだけ。軸受けリングが乗る面と、ホーンが座る面を同じ円筒で兼ねる。
    ホーンはこの穴を通って奥へ落ちるので、十字の溝は要らない。
    """
    # 穴は 1 つ。軸受けリングもホーンもここに収まる。十字の溝は彫らない
    part = cut(part, cyl_x(R_BORE, X_WEB0 - EPS, X_BORE1, oy, 0.0, "bore"))

    # 長穴は「箱 + 端の円柱」で作らない。円柱が箱の側面に接してゼロ長エッジが残り、
    # 次の boolean が壊れた結果を返す（上腕で non-manifold 3 本 → 干渉検算が全滅した）
    r = HORN_ARM_SCREW_DIA * MM / 2
    slot = HORN_ARM_SLOT * MM / 2
    for s in (1, -1):
        zc = s * HORN_ARM_SCREW_R * MM
        poly = hull2_poly((oy, zc - slot), r, (oy, zc + slot), r, 24)
        part = cut(part, prism_x("slot", poly, X_BORE1 - EPS, X_WEB1 + EPS))

    part = cut(part, cyl_x(HORN_CBORE * MM / 2, X_BORE1 - EPS, X_WEB1 + EPS, oy, 0.0,
                           "cbore", verts=48))
    return part


# ============================================================
# 節点列（桁の骨組み）
# ============================================================
def path_len(nodes):
    return sum(math.hypot(b[0][0] - a[0][0], b[0][1] - a[0][1])
               for a, b in zip(nodes, nodes[1:]))


def along(nodes, t):
    """節点列の道のりを 0..1 で辿って (中心, 半径) を返す。"""
    segs = [math.hypot(b[0][0] - a[0][0], b[0][1] - a[0][1])
            for a, b in zip(nodes, nodes[1:])]
    total = sum(segs)
    if total < 1e-9:
        return nodes[0]
    want = t * total
    acc = 0.0
    for (ca, ra), (cb, rb), s in zip(nodes, nodes[1:], segs):
        if acc + s >= want - 1e-12:
            u = (want - acc) / s if s > 1e-9 else 0.0
            return ((ca[0] + (cb[0] - ca[0]) * u, ca[1] + (cb[1] - ca[1]) * u),
                    ra + (rb - ra) * u)
        acc += s
    return nodes[-1]


def slot_cut(part, nodes, x0, x1, tag, t_end=2.0):
    """桁の真ん中を 1 本だけ抜く。

    丸穴を等間隔に並べるのは理由が無い。面内で曲げを受ける桁では中央の肉は
    効かないので、真ん中を通しで抜いて両脇に桁を残すのが素直。配線と結束
    バンドの通り道も兼ねる。参考モデルの腕も、抜くときは大きな開口 1 つで
    抜いている（丸穴の行列は 1 つも無い）。
    """
    if not SLOT:
        return part
    # 溝の先端は節点より R_SLOT ぶん外へ伸びる。両端ともそのぶん内側に節点を置く
    # （引き算にすると溝がハブの中まで食い込んで、軸受け穴とつながる）
    total = path_len(nodes)
    t0 = (nodes[0][1] + SLOT_MARGIN * MM + R_SLOT) / total
    t1 = min(t_end, 1.0 - (nodes[-1][1] + SLOT_MARGIN * MM + R_SLOT) / total)
    if (t1 - t0) * total < SLOT_MIN * MM:
        print(f"[slot] {tag}: 取れる長さが {(t1 - t0) * total * 1000:.0f}mm しかないので抜かない")
        return part
    pts = [along(nodes, t0 + (t1 - t0) * i / 5)[0] for i in range(6)]
    cutter = chain_plate(f"{tag}_slot", [(c, R_SLOT) for c in pts], x0 - EPS, x1 + EPS)
    print(f"[slot] {tag}: 幅 {R_SLOT * 2000:.1f}mm / 両脇の桁 {SLOT_RAIL:.1f}mm x2 / "
          f"長さ {(t1 - t0) * total * 1000:.0f}mm")
    return cut(part, cutter)


# ============================================================
# 肩ブラケット
# ============================================================
def round_rect_poly(y0, y1, z0, z1, r, seg=10):
    pts = []
    for cy, cz, a0 in ((y1 - r, z1 - r, 0.0), (y0 + r, z1 - r, math.pi / 2),
                       (y0 + r, z0 + r, math.pi), (y1 - r, z0 + r, 3 * math.pi / 2)):
        for i in range(seg + 1):
            a = a0 + math.pi / 2 * i / seg
            pts.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def build_bracket():
    m = BRK_MARGIN * MM
    hr = BRK_HOLE_DIA * MM / 2
    inset = hr + 0.0035
    y0 = SERVO_SCREW_Y[1] - m - 2 * inset
    y1 = max(SERVO_SCREW_Y[0] + m + 2 * inset, R_HUB + 0.002)
    hz = max(SERVO.BODY_W / 2 + m, R_HUB + 0.002, BRK_HOLE_PITCH * MM / 2 + hr + 0.003)

    part = prism_x("bracket", round_rect_poly(y0, y1, -hz, hz, 0.005), X_BRK0, X_DECK1)
    part = cut_deck(part, X_BRK0, X_DECK0, X_DECK1)
    part = add_journal(part, X_DECK1, X_BOSS1)
    for sy in (y0 + inset, y1 - inset):
        for sz in (-BRK_HOLE_PITCH * MM / 2, BRK_HOLE_PITCH * MM / 2):
            part = cut(part, cyl_x(hr, X_BRK0 - EPS, X_DECK1 + EPS, sy, sz,
                                   "brk_hole", verts=32))
    print(f"[bracket] 板 {(y1 - y0) * 1000:.1f} x {hz * 2000:.1f} x "
          f"{(X_DECK1 - X_BRK0) * 1000:.1f}mm / "
          f"取付穴 ⌀{BRK_HOLE_DIA:.1f} 4 本（ピッチ "
          f"{(y1 - y0 - 2 * inset) * 1000:.1f} x {BRK_HOLE_PITCH:.1f}mm）")
    return part


# ============================================================
# 上腕（肩＝従動 / 肘＝駆動）
# ============================================================
def upper_nodes():
    """ハブ → 一定幅の桁 → ハブ。桁の幅は全長で変えない。"""
    t = BEAM_TAPER
    return [((0.0, 0.0), R_HUB),
            ((L1_M * t, 0.0), R_BEAM),
            ((L1_M * (1 - t), 0.0), R_BEAM),
            ((L1_M, 0.0), R_HUB)]


def build_upper():
    """厚みは全長で一様。肘のサーボは板の裏へ掘った座で受ける。

    段（肩側だけ厚い板）にすると、どちらを上にして刷っても大きな宙吊り面か
    下向きの出っ張りが出る。一様な板＋裏の座ぐりなら、裏面がそのまま平らな
    接地面になり、上に出るのは軸受けリングだけになる。
    """
    nodes = upper_nodes()
    part = chain_plate("upper", nodes, X_WEB0, X_WEB1)
    # 溝は肘のサーボ穴の手前で止める。溝の先端は節点より R_SLOT ぶん伸びるので
    # そのぶん手前に節点を置く（引かないとサーボ穴とつながって切り欠きになる）
    t_end = (L1_M + SERVO_BODY_Y[0] - 0.003 - R_SLOT) / path_len(nodes)
    part = slot_cut(part, nodes, X_WEB0, X_WEB1, "upper", t_end)
    part = cut_driven(part)                                            # 肩側（従動）
    part = cut_deck(part, X_WEB0, X_ELBOW_DECK0, X_WEB1, oy=L1_M)      # 肘側（駆動）
    part = add_journal(part, X_WEB1, X_ELBOW_CASE + SERVO.BOSS_H, oy=L1_M)
    print(f"[upper] ハブ ⌀{R_HUB * 2000:.1f} / 桁 幅 {BEAM_W:.1f}mm 一定 / "
          f"平板 {PLATE * 1000:.1f}mm 一定（肘の座は裏から "
          f"{(X_ELBOW_DECK0 - X_WEB0) * 1000:.1f}mm）")
    return part


# ============================================================
# 前腕（肘＝従動。内側へ曲げる）
# ============================================================
def fore_nodes():
    th = math.radians(FORE_CURL)
    n = max(3, FORE_NODES)
    if abs(th) < 1e-6:
        cs = [(L2_M * i / (n - 1), 0.0) for i in range(n)]
    else:
        r_path = L2_M / th
        cs = arc_centers((0.0, r_path), r_path, -math.pi / 2, -math.pi / 2 + th, n)
    # 根元のハブから桁幅へ絞り、あとは先端まで一定
    radii = [R_HUB if i == 0 else R_BEAM for i in range(n)]
    return list(zip(cs, radii))


def build_fore():
    nodes = fore_nodes()
    part = chain_plate("fore", nodes, X_WEB0, X_WEB1)
    part = slot_cut(part, nodes, X_WEB0, X_WEB1, "fore")
    part = cut_driven(part)
    tip = nodes[-1][0]
    print(f"[fore] 曲がり {FORE_CURL:.0f}° / 桁 幅 {BEAM_W:.1f}mm 一定 / "
          f"先端は肘軸から ({tip[0] * 1000:.0f}, {tip[1] * 1000:.0f})mm")
    return part


def build_pad():
    """前腕の縁にかぶせる TPU の袖。先端から差し込む。"""
    nodes = fore_nodes()
    seg = nodes[max(1, int(len(nodes) * PAD_FROM)):]
    t, g, c = PAD_T * MM, PAD_GRIP * MM, PAD_CLR * MM
    part = chain_plate("pad", [(cc, rr + t) for cc, rr in seg], X_WEB0 - t, X_WEB1 + t)
    part = cut(part, chain_plate("pad_h", [(cc, rr + c) for cc, rr in seg],
                                 X_WEB0 - c, X_WEB1 + c))
    part = cut(part, chain_plate("pad_d", [(cc, max(rr - g, 0.001)) for cc, rr in seg],
                                 X_WEB0 - t - 0.002, X_WEB1 + t + 0.002))
    (ty, tz), tr = seg[-1]
    part = cut(part, cyl_x(tr + t + 0.002, X_WEB0 - t - 0.002, X_WEB1 + t + 0.002,
                           ty, tz, "pad_open", verts=64))     # 先端を開けて差し込めるように
    print(f"[pad] TPU / 肉厚 {PAD_T:.1f}mm / 掴み代 片側 {PAD_GRIP:.1f}mm / "
          f"前腕の {PAD_FROM * 100:.0f}% から先")
    return part


# ============================================================
# 組み立て
# ============================================================
clear_scene()

bracket = build_bracket()
upper = build_upper()
fore = build_fore()
pad = build_pad() if PAD else None

# (部品, 名前, 刷るとき裏返すか)
PARTS = [(bracket, "hug-arm-bracket", False), (upper, "hug-arm-upper", False),
         (fore, "hug-arm-fore", True)]
if pad is not None:
    PARTS.append((pad, "hug-arm-pad", False))


def mirror_x(ob, name):
    """X で鏡像にした複製を返す。左右の腕は鏡像で、同じ部品は使えない。"""
    dup = ob.copy()
    dup.data = ob.data.copy()
    dup.name = name
    bpy.context.scene.collection.objects.link(dup)
    dup.scale = (-1.0, 1.0, 1.0)
    activate(dup)
    bpy.ops.object.transform_apply(scale=True)
    return clean(dup)


def write_stl(ob, fname, flip=False):
    """刷る向きに倒してから書き出す。

    平板は面を寝かせる。既定は「板の裏面を接地、軸受けリングを上」。
    flip=True は逆向き（前腕は軸受け穴を上に開けたいので裏返す。そうしないと
    ⌀21.7 の天井を橋渡しすることになる）。
    """
    dup = ob.copy()
    dup.data = ob.data.copy()
    bpy.context.scene.collection.objects.link(dup)
    place(dup, Matrix.Rotation(math.pi / 2 if flip else -math.pi / 2, 4, "Y"))
    lo = min((dup.matrix_world @ Vector(c)).z for c in dup.bound_box)
    place(dup, Matrix.Translation((0.0, 0.0, -lo)))
    activate(dup)
    bpy.ops.wm.stl_export(
        filepath=os.path.join(blender_utils.EXPORTS_DIR, fname + ".stl"),
        export_selected_objects=True, global_scale=1000.0)
    d = dup.dimensions
    bpy.data.objects.remove(dup, do_unlink=True)
    print(f"[part] {fname}: 接地 {d.x * 1000:.0f} x {d.y * 1000:.0f}mm / 高さ "
          f"{d.z * 1000:.1f}mm / non-manifold {non_manifold(ob)}"
          f"{' / 裏返して刷る' if flip else ''}")


# 抱きつくには左右 2 本要る。部品は鏡像なので両方書き出す（-l = 左腕 / -r = 右腕）
for ob, fname, flip in PARTS:
    write_stl(ob, fname + "-l", flip)
    dup = mirror_x(ob, ob.name + "_r")
    write_stl(dup, fname + "-r", flip)
    bpy.data.objects.remove(dup, do_unlink=True)   # 書き出したら消す（プレビューに残さない）


# ============================================================
# トルク収支（メッシュから質量と体積重心を出す）
# 最悪姿勢 = 肩・肘とも 0°、腕を真横へ伸ばしきった状態
# ============================================================
def vol_com(o):
    """体積 [mm3] と体積重心。頂点の平均ではない（肉抜き側へ寄って過小評価する）。"""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.transform(o.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    vol = 0.0
    acc = Vector((0.0, 0.0, 0.0))
    for f in bm.faces:
        a, b, c = [x.co for x in f.verts]
        tet = a.dot(b.cross(c)) / 6.0
        vol += tet
        acc += tet * (a + b + c) / 4.0
    bm.free()
    return abs(vol) * 1e9, (acc / vol if abs(vol) > 1e-12 else Vector())


def print_torque():
    v_up, c_up = vol_com(upper)
    v_fo, c_fo = vol_com(fore)
    m_up = v_up * PLA_DENSITY / 1000.0
    m_fo = v_fo * PLA_DENSITY / 1000.0
    m_pad = vol_com(pad)[0] * TPU_DENSITY / 1000.0 if pad is not None else 0.0
    y_up, y_fo = abs(c_up.y) * 1000.0, abs(c_fo.y) * 1000.0
    m_joint = SERVO_MASS_G + HORN_MASS_G
    reach = abs(fore_nodes()[-1][0][0]) * 1000.0

    sh_self = m_up * y_up + (m_fo + m_pad) * (L1 + y_fo) + m_joint * L1
    el_self = (m_fo + m_pad) * y_fo
    budget = SERVO_STALL_KGCM * SERVO_DUTY * 10000.0     # g·mm

    print(f"[mass]  上腕 {m_up:.1f}g（肩軸から {y_up:.0f}mm）/ 前腕 {m_fo:.1f}g"
          f"（肘軸から {y_fo:.0f}mm）/ パッド {m_pad:.1f}g")
    for tag, self_t, arm_mm in (("肩", sh_self, L1 + reach), ("肘", el_self, reach)):
        pay = max(0.0, (budget - self_t) / arm_mm)
        print(f"[torque] {tag} 自重 {self_t / 10000:.2f} / 連続枠 {budget / 10000:.2f} kgf·cm "
              f"（{self_t / budget * 100:.0f}%）→ 先端に載せられるのは {pay:.0f}g まで")
    print(f"[range] 電気 180°: 肩 {SHOULDER_WINDOW[0]:+.0f}〜{SHOULDER_WINDOW[1]:+.0f}° / "
          f"肘 {ELBOW_WINDOW[0]:+.0f}〜{ELBOW_WINDOW[1]:+.0f}°"
          f"（スプライン {SERVO_SPLINE_TEETH} 山 = ホーンは "
          f"{360 / SERVO_SPLINE_TEETH:.0f}° 刻み）")


print_torque()


# ============================================================
# 干渉の検算（サーボの実体と印刷パーツの共通体積）
# 「入るはず」を図面で信じない。剛体だけのダミーを作って重なりを測る。
# 計器が死んでいないことを、必ず当たる入力（サーボを 1mm ずらす）で先に確かめる
# ============================================================
def solid_volume(o):
    return vol_com(o)[0]


def wbox(o):
    """ワールド系の外接箱を mm で返す（どこが当たっているかを見るため）。"""
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = [min(c[i] for c in cs) * 1000 for i in range(3)]
    hi = [max(c[i] for c in cs) * 1000 for i in range(3)]
    return (f"x {lo[0]:7.1f}..{hi[0]:7.1f}  y {lo[1]:7.1f}..{hi[1]:7.1f}  "
            f"z {lo[2]:6.1f}..{hi[2]:6.1f}")


def overlap_mm3(part, mat, dy=0.0):
    """サーボの実体と部品の共通体積 [mm3] と、その位置（どこが当たっているか）。"""
    # 羽根の面とデッキの面はぴったり合わさる。完全な同一平面のまま EXACT に渡すと
    # boolean が失敗して「部品まるごとが共通部分」という答えを返す。0.05mm 引いて逃がす
    dummy = add_servo_dummy(flange_top_z=X_SEAT, name="chk", prof=SERVO)
    place(dummy, Matrix.Translation((-0.00005, dy, 0.0)) @ mat)
    probe = part.copy()
    probe.data = part.data.copy()
    bpy.context.scene.collection.objects.link(probe)
    boolean(probe, dummy, op="INTERSECT")
    v = solid_volume(probe)
    box = wbox(probe) if v > 0.01 else "なし"
    bpy.data.objects.remove(probe, do_unlink=True)
    return v, box


def overlap_horn(part, mat, grow=0.0):
    """ホーンの実体と従動側の共通体積 [mm3]。穴に本当に入るかを測る。

    校正は「ホーンを一回り大きくする」。長さ方向へずらしても穴の中で動くだけで
    当たらないので、ずらしでは計器の生死が分からない（1 度これで騙された）。
    """
    horn = add_horn_dummy(prof=HORN, name="hchk", base_z=X_BOSS1)
    if grow:
        horn.scale = (1.0 + grow, 1.0 + grow, 1.0)
        activate(horn)
        bpy.ops.object.transform_apply(scale=True)
    place(horn, mat)
    probe = part.copy()
    probe.data = part.data.copy()
    bpy.context.scene.collection.objects.link(probe)
    boolean(probe, horn, op="INTERSECT")
    v = solid_volume(probe)
    box = wbox(probe) if v > 0.01 else "なし"
    bpy.data.objects.remove(probe, do_unlink=True)
    return v, box


def check_horn():
    """ホーンが溝に収まるか。長腕・短腕・ハブすべてを含む実体で測る。

    校正は「ホーンを 1.5mm 横へずらす」。溝の余裕は片側 0.2mm なので必ず当たる。
    """
    for tag, part, mat in (("肩", upper, servo_mat(math.pi / 2)),
                           ("肘", fore, servo_mat(math.pi / 2))):
        good, box = overlap_horn(part, mat)
        bad, _ = overlap_horn(part, mat, grow=0.10)
        ok = "OK" if good < 1.0 else "⚠ 入らない"
        cal = "計器 生きている" if bad > good + 5.0 else "⚠ 計器が死んでいる"
        print(f"[horn] {tag}（ホーン ↔ 従動側）: 共通体積 {good:.2f}mm3 ({box}) → {ok} "
              f"（1 割大きくすると {bad:.1f}mm3 ＝ {cal}）")


def check_fit():
    cases = (("肩サーボ ↔ ブラケット", bracket, servo_mat(math.pi)),
             ("肘サーボ ↔ 上腕", upper, servo_mat(math.pi, oy=L1_M, ox=X_ELBOW_CASE)))
    for tag, part, mat in cases:
        good, box = overlap_mm3(part, mat)
        bad, _ = overlap_mm3(part, mat, dy=0.0015)    # 必ず当たる入力（計器の校正）
        ok = "OK" if good < 1.0 else "干渉"
        cal = "計器 生きている" if bad > good + 5.0 else "⚠ 計器が死んでいる"
        print(f"[fit] {tag}: 共通体積 {good:.2f}mm3 ({box}) → {ok} "
              f"（1.5mm ずらすと {bad:.1f}mm3 ＝ {cal}）")


check_fit()
check_horn()
print(f"[joint] 平板 {PLATE * 1000:.1f}mm / ハブ ⌀{R_HUB * 2000:.1f} / "
      f"軸受け ⌀{R_JOURNAL * 2000:.1f} × 高さ {(X_BOSS1 - X_DECK1) * 1000:.1f}mm"
      f"（ホーンの角 ⌀{R_HORN_SWEEP * 2000:.1f} が通る径まで自動で広げた）/ "
      f"デッキ {DECK * 1000:.1f}mm")
print(f"[joint] 印刷パーツの幅 肩+上腕 {(X_WEB1 - X_DECK0) * 1000:.1f}mm / "
      f"前腕まで {(X_ELBOW_CASE + X_WEB1 - X_DECK0) * 1000:.1f}mm "
      f"/ サーボの出っ張り込み {(X_ELBOW_CASE + X_WEB1 + SERVO.BODY_H - NUB) * 1000:.1f}mm")


# ============================================================
# プレビュー姿勢
# ============================================================
a_sh = math.radians(POSE_SHOULDER)
M_UP = Matrix.Rotation(a_sh, 4, "X")
M_FO = (M_UP @ Matrix.Translation((X_ELBOW_CASE, L1_M, 0.0))
        @ Matrix.Rotation(math.radians(POSE_ELBOW), 4, "X"))

place(upper, M_UP)
place(fore, M_FO)
if pad is not None:
    place(pad, M_FO)

arm = [bracket, upper, fore] + ([pad] if pad is not None else [])
if SHOW_SERVO:
    arm += [
        place(add_servo_dummy(flange_top_z=X_SEAT, name="servo_sh", prof=SERVO),
              servo_mat(math.pi)),
        place(add_horn_dummy(prof=HORN, name="horn_sh", base_z=X_BOSS1),
              M_UP @ servo_mat(math.pi / 2)),
        place(add_servo_dummy(flange_top_z=X_SEAT, name="servo_el", prof=SERVO),
              M_UP @ servo_mat(math.pi, oy=L1_M, ox=X_ELBOW_CASE)),
        place(add_horn_dummy(prof=HORN, name="horn_el", base_z=X_BOSS1),
              M_FO @ servo_mat(math.pi / 2)),
    ]

# 体へ据える。関節軸は前を向き、腕は正面で開閉する（左右が向かい合って閉じる）
# ローカル X（関節軸）→ 前 / ローカル Y（腕）→ 外 / ローカル Z → 上
M_MOUNT = (Matrix.Translation((-SHOULDER_SPAN * MM / 2, 0.0, 0.0))
           @ Matrix.Rotation(-math.radians(MOUNT_TILT), 4, "X")
           @ Matrix.Rotation(math.pi / 2, 4, "Z"))
for ob in arm:
    place(ob, M_MOUNT)

pair = []
if SHOW_PAIR:
    for ob in list(arm):
        dup = mirror_x(ob, ob.name + "_pair")
        place(dup, Matrix.Translation((0.0, HUG_OFFSET_Y * MM, 0.0)))
        pair.append(dup)


def check_pair():
    """閉じた姿勢で左右の腕がぶつかっていないか、共通体積で確かめる。"""
    if not pair:
        return
    movers = [o for o in arm if o is not bracket]
    others = [o for o in pair if not o.name.startswith("bracket")]
    total = 0.0
    for a in movers:
        for b in others:
            probe = a.copy()
            probe.data = a.data.copy()
            bpy.context.scene.collection.objects.link(probe)
            cutter = b.copy()
            cutter.data = b.data.copy()
            bpy.context.scene.collection.objects.link(cutter)
            boolean(probe, cutter, op="INTERSECT")
            total += solid_volume(probe)
            bpy.data.objects.remove(probe, do_unlink=True)
    verdict = "OK" if total < 1.0 else "⚠ 左右がぶつかる"
    print(f"[pair] 肩 {POSE_SHOULDER:.0f}° / 肘 {POSE_ELBOW:.0f}° で "
          f"左右の共通体積 {total:.1f}mm3 → {verdict}"
          f"（前後のずらし {HUG_OFFSET_Y:.0f}mm）")


check_pair()
print(f"[hug] 肩の間隔 {SHOULDER_SPAN:.0f}mm / 肩軸を前へ {MOUNT_TILT:.0f}° 傾ける / "
      f"左右 2 本（部品は鏡像なので -l と -r を別に刷る）/ "
      f"右腕は {HUG_OFFSET_Y:.0f}mm 前へ")

blender_utils.export_stl("hug-arm")
