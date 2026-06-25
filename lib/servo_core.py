"""1サーボ（SG90）パン機構の共通コア。

round-bot / square-bot などのキャラクターが共有する「サーボを最初から仕込む」ための
ジオメトリ・ユーティリティ群。設計思想は CLAUDE.md の議論どおり:

  - SG90 を縦置き、軸を上向き。フランジ（羽根）をデッキ上面に載せ、本体は胴の中に
    吊り下げ、軸だけ上に突き出す（実機のパネル取付と同じで最も堅い）。
  - SG90 は軸が本体長手中心からずれているので、軸が胴の中心 (x=0,y=0) に来るよう
    本体を内部でオフセットして配置する。
  - 頭のスカートがデッキ上の円リップ（スラストリング）に乗り、横荷重を軸から逃がす。
  - 頭裏にクロス溝＋センター穴を彫り、クロス/シングルどちらのホーンも掴める。
  - 配線は背面 (-X) のチャネルから逃がす。

座標系: z=0 を胴の底面とする。軸（回転中心）は (x, y) = (0, 0)。
単位: メートル（1mm = 0.001）。Blender 内部単位に一致。

SG90 の各キャラ model.py からは概ね次のように使う:

    from servo_core import (
        add_cyl, add_box, boolean,
        cut_servo_mount, add_thrust_ring, cut_horn_coupling,
        SG90, servo_clearance_default,
    )
"""
import bpy
import math  # noqa: F401  (呼び出し側で使う場合あり)


# ============================================================
# サーボ実寸プロファイル（公称値。製造ばらつきはクリアランス側で吸収する）
#
# マウントは「羽根をデッキ上面に載せ、本体は胴の中に吊り下げ、軸だけ上に突き出す」。
# 派生値:
#   NUB_ABOVE_DECK   = 羽根より上（デッキ上面より上）に飛び出すケース部分の高さ
#   SHAFT_ABOVE_DECK = デッキ上面〜軸先端（頭の軸逃げ・ホーン結合の基準）
# ============================================================
class SG90:
    BODY_L = 0.0228   # 本体長手（軸オフセット方向 = X）
    BODY_W = 0.0122   # 本体幅（Y）
    BODY_H = 0.0225   # 本体高さ（底〜ケース上面。軸の突起は含まない）
    SHAFT_OFFSET = 0.0057  # 軸が本体長手中心からずれる量
    FLANGE_L = 0.0322  # 羽根を含む全長
    FLANGE_W = 0.0122  # 羽根の幅（本体と同じ）
    FLANGE_T = 0.0025  # 羽根の厚み
    FLANGE_FROM_BOTTOM = 0.0159  # 本体底〜羽根下面
    SCREW_SPACING = 0.0280  # 取付ネジ穴ピッチ（長手方向）
    SCREW_R = 0.0011  # ネジ下穴半径（M2 セルフタップ想定）
    SHAFT_R = 0.0030  # 軸＋スプライン外径の逃げ半径
    TAB_HOLE_R = 0.0010  # 取付タブの穴 ⌀2
    # ケース上の2円柱（下=ギアカバー座 / 上=出力軸スプライン）
    BOSS_DIA = 0.0116
    BOSS_H = 0.0018
    SHAFT_DIA = 0.0048
    SHAFT_H = 0.0027
    SHAFT_ABOVE_CASE = BOSS_H + SHAFT_H  # ケース上面〜軸先端
    NUB_ABOVE_DECK = BODY_H - FLANGE_FROM_BOTTOM
    SHAFT_ABOVE_DECK = NUB_ABOVE_DECK + SHAFT_ABOVE_CASE


class SG92R:
    # 白石の実測値（2026-06-24・sg92r UIで採寸）。公式表より個体差で小さめ。
    BODY_L = 0.0220            # 本体長
    BODY_W = 0.0123            # 本体幅
    BODY_H = 0.0223            # 本体高（ケース上面まで・軸除く）
    SHAFT_OFFSET = 0.0050      # 軸の中心ずれ
    FLANGE_L = 0.0322          # 羽根全長（タブ先端-先端）
    FLANGE_W = 0.0123
    FLANGE_T = 0.0022          # 羽根の厚み
    FLANGE_FROM_BOTTOM = 0.0160
    SCREW_SPACING = 0.02884    # ネジ穴ピッチ中心間
    SCREW_R = 0.0009           # マウント側の M2 セルフタップ下穴（screws=True 時）
    TAB_HOLE_R = 0.0015        # サーボ側タブ穴 ⌀3
    SHAFT_R = 0.0030
    # ケース上の2円柱（下=ギアカバー座 / 上=出力軸スプライン）
    BOSS_DIA = 0.0123          # 大円柱（ギアカバー座）径 ⌀
    BOSS_H = 0.0046            # 大円柱の高さ（ケース上面から）
    SHAFT_DIA = 0.0046         # 小円柱（出力軸スプライン）径 ⌀
    SHAFT_H = 0.0036           # 小円柱の高さ（大円柱上〜軸先端）≈ホーン込み5.6−板厚
    SHAFT_ABOVE_CASE = BOSS_H + SHAFT_H
    NUB_ABOVE_DECK = BODY_H - FLANGE_FROM_BOTTOM
    SHAFT_ABOVE_DECK = NUB_ABOVE_DECK + SHAFT_ABOVE_CASE


# 使用するサーボ（手元に SG92R が複数あるため既定を SG92R に）
SERVO = SG92R

_PROFILES = {"SG90": SG90, "SG92R": SG92R}


def use_servo(name):
    """アクティブなサーボプロファイルを切り替える（"SG90" / "SG92R"）。"""
    global SERVO
    SERVO = _PROFILES[name]
    return SERVO


# 推奨デフォルトのはめ込みクリアランス（per side）
servo_clearance_default = 0.0004  # 0.4mm


# ============================================================
# サーボホーン仕様（実測前のプレースホルダ。入手後ここを更新すれば全モデル追従）
# ============================================================
class HORN:
    # SG92R 付属クロスホーン（白石実測）。横35×たて17の非対称クロス。
    TYPE = "cross"        # "cross"（十字）/ "single"（1腕）/ "round"（円盤）
    ARM_SPAN_X = 0.0350   # 長腕の全長（端〜端）横35mm
    ARM_SPAN_Y = 0.0170   # 短腕の全長（端〜端）たて17mm
    ARM_W_X = 0.0068      # 長腕の幅 6.8mm
    ARM_W_Y = 0.0036      # 短腕の幅 3.6mm
    HUB_DIA = 0.0070      # 中央ハブ径
    THICKNESS = 0.0020    # 腕板の厚み（＝受け溝の深さ）
    STACK_H = 0.0056      # ギアカバー上面〜ホーン頂部（小円柱+ホーン）＝5.6mm
    ROUND_DIA = 0.0200    # round タイプの円盤径
    # ねじ止めしない運用（はめ込み保持）。screw=True にすると下記でビス穴＋ザグリを彫る
    SCREW_DIA = 0.0024    # センタービス径（screw=True 時）
    COUNTERBORE_DIA = 0.0050  # 天面ザグリ径（screw=True 時）
    SEAT_LEDGE = 0.0015   # ねじ頭座面の肉厚（screw=True 時）


# ============================================================
# 低レベル・プリミティブ（既存モデルと同じ流儀）
# ============================================================
def add_cyl(r, h, z_center, name, verts=96, location=None):
    loc = location if location is not None else (0, 0, z_center)
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    return o


def add_box(w, d, h, location, name):
    bpy.ops.mesh.primitive_cube_add(size=2, location=location)
    o = bpy.context.active_object
    o.scale = (w / 2, d / 2, h / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.name = name
    return o


def add_sphere(r, location, name, segs=64, rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=location,
                                         segments=segs, ring_count=rings)
    o = bpy.context.active_object
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


def join_objects(objs, name):
    """複数オブジェクトを1つに結合（表示・スライス用。boolean ではなく join）。"""
    objs = [o for o in objs if o is not None]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


def round_box_xy(w, d, h, r, z_center, name, verts=24):
    """XY 平面の四隅を半径 r で丸めた角丸ボックス（Z は平ら）。

    minkowski 的に「四隅の円柱 + 十字の箱」を UNION して作る。
    """
    if r <= 0:
        return add_box(w, d, h, (0, 0, z_center), name)
    r = min(r, w / 2 - 1e-5, d / 2 - 1e-5)
    cx, cy = w / 2 - r, d / 2 - r
    # 十字の2枚で中央を埋める
    base = add_box(w, d - 2 * r, h, (0, 0, z_center), name)
    cross = add_box(w - 2 * r, d, h, (0, 0, z_center), name + "_cross")
    boolean(base, cross, op="UNION")
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = add_cyl(r, h, z_center, name + "_c", location=(sx * cx, sy * cy, z_center))
            boolean(base, c, op="UNION")
    return base


# ============================================================
# サーボ・マウント（胴側に彫る）
# ============================================================
def _servo_center_x():
    """軸が原点に来るよう本体中心の X を返す。本体バルクは -X（背面）側。"""
    return -SERVO.SHAFT_OFFSET


def cut_servo_mount(body, deck_top_z, deck_t, clr=servo_clearance_default, screws=True,
                    wire_notch_w=0.006):
    """胴 `body` にサーボ取付フィーチャを彫る。

    - デッキ貫通穴: 本体断面 (L×W) + クリアランス。本体＋上部突起がここを通る。
    - フランジ座: デッキ上面の浅いポケット (FLANGE_L×FLANGE_W)。羽根が面で受かる。
    - ネジ下穴: 28mm ピッチ × 2、デッキを貫通（下から M2 セルフタップ）。
    - 配線チャネル: 背面 (-X) からデッキ穴へ抜ける溝。

    deck_top_z: デッキ上面の z（通常は胴の全高 BODY_H）
    deck_t:     デッキ厚
    """
    cx = _servo_center_x()
    deck_bottom = deck_top_z - deck_t

    # --- デッキ貫通穴（本体が通る）。上下に突き出して面一回避 ---
    hole = add_box(SERVO.BODY_L + 2 * clr, SERVO.BODY_W + 2 * clr, deck_t + 0.004,
                   (cx, 0, deck_top_z - deck_t / 2), "servo_hole")
    boolean(body, hole)

    # --- フランジ座（デッキ上面のポケット）---
    pocket = add_box(SERVO.FLANGE_L + 2 * clr, SERVO.FLANGE_W + 2 * clr, SERVO.FLANGE_T + 0.0005,
                     (cx, 0, deck_top_z - SERVO.FLANGE_T / 2 + 0.00025), "flange_pocket")
    boolean(body, pocket)

    # --- 羽受けの配線逃げ（サーボ長手の +X 端）---
    # サーボの配線は長手方向の +X 端から出る。3芯リボンが羽根脇を通れるよう、
    # 本体穴の +X 端〜デッキを小さく抜いて中空へ落とす。底の配線スロットへ繋がる。
    if wire_notch_w > 0:
        notch = add_box(0.008, wire_notch_w, deck_t + 0.004,
                        (cx + SERVO.BODY_L / 2, 0, deck_top_z - deck_t / 2), "wire_notch")
        boolean(body, notch)

    # --- ネジ下穴（フランジ両端ピッチ）。screws=False なら省略（頭で挟むので無ねじ可）---
    if screws:
        for sx in (-1, 1):
            sh = add_cyl(SERVO.SCREW_R, deck_t + 0.004, 0,
                         "servo_screw", verts=24,
                         location=(cx + sx * SERVO.SCREW_SPACING / 2, 0, deck_top_z - deck_t / 2))
            boolean(body, sh)

    # 配線は外壁を切らず、中空胴の内側を通す。出口は cut_wire_exit で背面下端に開ける。
    return deck_bottom


def cut_wire_exit(body, back_x, wall, width=0.006, height=0.007):
    """サーボ長手 +X 側の壁の下端に、配線を逃がす下開放スロットを彫る。

    サーボの線は長手 +X 端から出て中空胴の内部を通り、このスロットから下端へ出る。
    back_x: 壁の外側 x。正負どちらでも対応（copysign で内側へオフセット）。
    width=スロット幅(Y), height=底からの高さ(Z)。
    底（z=0）より下に突き出して切るので、下端が開いた切り欠きになる（印刷向き◎）。
    """
    cx_wall = back_x - math.copysign(wall / 2, back_x)
    cutter = add_box(wall + 0.004, width, height + 0.002,
                     (cx_wall, 0, height / 2 - 0.001), "wire_exit")
    boolean(body, cutter)


def cut_servo_head_clearance(part, plane_z, deck_top_z, coupling_z, clr=servo_clearance_default):
    """回る側（頭 / キャップ）の裏に、サーボのデッキ上突起ぶんの逃げを彫る。

    頭は軸まわりに回るので、逃げは「回転しても当たらない丸穴」にする必要がある。
    - 下段: 上部ケース（羽根より上の角型ケース）を、最遠角までの半径で丸く逃がす
    - 上段: ギアカバー座（丸）を coupling_z まで丸く逃がす
    ホーン結合（cut_horn_coupling）は呼び出し側で別途彫る。
    """
    s = SERVO
    case_top = deck_top_z + s.NUB_ABOVE_DECK
    # 角型ケースの最遠角（軸=原点 からの距離）。回転で当たらないようこの半径で丸逃げ
    nub_r = math.hypot(s.BODY_L / 2 + s.SHAFT_OFFSET, s.BODY_W / 2) + clr
    h1 = (case_top - plane_z) + 0.004
    c1 = add_cyl(nub_r, h1, (plane_z + case_top) / 2, "nub_clear")
    boolean(part, c1)
    # ギアカバー座の丸逃げ（plane..coupling）
    boss_r = s.BOSS_DIA / 2 + clr
    h2 = (coupling_z - plane_z) + 0.004
    c2 = add_cyl(boss_r, h2, plane_z - 0.002 + h2 / 2, "boss_clear")
    boolean(part, c2)
    return nub_r


def add_thrust_ring(body, deck_top_z, ring_outer_r, ring_t=0.0015, ring_wall=0.002):
    """デッキ上面にスラストリング（円リップ）を UNION する。

    頭のスカート下面がこのリング上面に乗り、横荷重を軸から逃がす。
    ring_outer_r: リング外半径（頭スカートの内径がこれ + クリアランスに合う想定）
    """
    outer = add_cyl(ring_outer_r, ring_t, deck_top_z + ring_t / 2, "thrust_ring")
    inner = add_cyl(ring_outer_r - ring_wall, ring_t + 0.002, deck_top_z + ring_t / 2, "thrust_bore")
    boolean(outer, inner)
    boolean(body, outer, op="UNION")
    return deck_top_z + ring_t  # リング上面 z


# ============================================================
# ホーン結合（頭側に彫る）
# ============================================================
def cut_horn_coupling(head, coupling_z, clr=servo_clearance_default, horn=None, screw=False,
                      floor_z=None):
    """頭 `head` の裏側にホーン受けを彫る。寸法は HORN 仕様から取る。

    horn: ホーン仕様オブジェクト（属性参照）。None なら共通の HORN。
    floor_z: クロス溝を彫り下げる床の z（=頭の底面 PLANE）。指定すると溝が床まで縦に
             貫通し、ホーン腕を下から差し込めるようになる（None なら結合面付近のみ）。
    coupling_z: 受けの基準 z（ホーン下面が当たる高さ）。腕は coupling_z で着座する。
    """
    h = horn if horn is not None else HORN
    t = (getattr(h, "TYPE", "cross") or "cross").lower()
    thick = h.THICKNESS
    depth = thick + 0.0015          # 着座部の余裕
    slot_top = coupling_z + depth
    # 溝は床（floor_z＝頭の底）から着座上端まで縦に通す。腕が下から滑り上がって入る。
    # 床は底面より少し下へ出して coplanar を避け、確実に底へ開口させる。
    floor = (floor_z - 0.002) if floor_z is not None else (coupling_z - 0.0005)
    hh = slot_top - floor
    zc = (floor + slot_top) / 2

    # 中央ハブ受け（床まで通す）
    hub = add_cyl(h.HUB_DIA / 2 + clr, hh, zc, "horn_hub")
    boolean(head, hub)

    if t in ("cross", "single"):
        # 長腕（X）: 長さ ARM_SPAN_X × 幅 ARM_W_X
        s = add_box(h.ARM_SPAN_X + 2 * clr, h.ARM_W_X + 2 * clr, hh, (0, 0, zc), "horn_slot_x")
        boolean(head, s)
        if t == "cross":  # 短腕（Y）: 長さ ARM_SPAN_Y × 幅 ARM_W_Y
            s = add_box(h.ARM_W_Y + 2 * clr, h.ARM_SPAN_Y + 2 * clr, hh, (0, 0, zc), "horn_slot_y")
            boolean(head, s)
    elif t == "round":
        disc = add_cyl(h.ROUND_DIA / 2 + clr, hh, zc, "horn_disc")
        boolean(head, disc)

    # --- センタービス（screw=True のときのみ）。ザグリ＋シャンク逃げで短ねじ化 ---
    if screw:
        cbore_dia = getattr(h, "COUNTERBORE_DIA", 0.005)
        seat_ledge = getattr(h, "SEAT_LEDGE", 0.0015)
        seat_z = coupling_z + thick + seat_ledge
        shank = add_cyl(h.SCREW_DIA / 2, (seat_z - coupling_z) + 0.004,
                        (coupling_z + seat_z) / 2 - 0.002, "horn_shank", verts=24)
        boolean(head, shank)
        cbore = add_cyl(cbore_dia / 2, 0.20, seat_z + 0.10, "horn_cbore", verts=32)
        boolean(head, cbore)


def add_horn_dummy(prof=None, name="horn", base_z=0.0):
    """サーボホーンの実体ダミー（正の形状）。horn モデルの可視化・確認用。"""
    h = prof if prof is not None else HORN
    t = (getattr(h, "TYPE", "cross") or "cross").lower()
    thick = h.THICKNESS
    parts = [add_cyl(h.HUB_DIA / 2, thick, base_z + thick / 2, name + "_hub", verts=48)]
    if t in ("cross", "single"):
        parts.append(add_box(h.ARM_SPAN_X, h.ARM_W_X, thick, (0, 0, base_z + thick / 2), name + "_armx"))
        if t == "cross":
            parts.append(add_box(h.ARM_W_Y, h.ARM_SPAN_Y, thick, (0, 0, base_z + thick / 2), name + "_army"))
    elif t == "round":
        parts.append(add_cyl(h.ROUND_DIA / 2, thick, base_z + thick / 2, name + "_disc", verts=64))
    # 穴あけ前に UNION で多様体化（join のままだと EXACT boolean が空になる）
    horn = parts[0]
    horn.name = name
    for p in parts[1:]:
        boolean(horn, p, op="UNION")
    hole = add_cyl(h.SCREW_DIA / 2, thick + 0.004, base_z + thick / 2, name + "_hole", verts=24)
    boolean(horn, hole)
    return horn


# ============================================================
# サーボ実体ダミー（シミュレーション / フィット確認用）
# ============================================================
def add_servo_dummy(flange_top_z=None, name="servo", clr=0.0, prof=None):
    """サーボの実体ダミーを1オブジェクトで生成する。

    prof: サーボ寸法を持つオブジェクト（属性で参照）。None なら SERVO（共通プロファイル）。
          sg92r モデルは自分の params から作った namespace を渡して、UI実測値で即描く。
    座標はマウントと同じ: 軸（出力軸）が原点 (x=y=0)、本体バルクは -X、配線は -X。
    flange_top_z で羽根上面の z を指定（マウントのデッキ上面に合わせて重ねられる）。
    None のときは本体底が z=0 に来る（単体表示用）。
    clr>0 で各辺を膨らませる（socket フィット確認用の“きつめダミー”）。
    """
    s = prof if prof is not None else SERVO
    # 寸法ばらつき（class は *_R 属性、UI namespace は *_DIA 属性）を吸収
    tab_hole_r = getattr(s, "TAB_HOLE_R", None)
    if tab_hole_r is None:
        tab_hole_r = getattr(s, "TAB_HOLE_DIA", 0.003) / 2
    boss_r = getattr(s, "BOSS_DIA", 0.0116) / 2
    shaft_r = getattr(s, "SHAFT_DIA", 0.0048) / 2
    boss_h = getattr(s, "BOSS_H", 0.0018)
    shaft_h = getattr(s, "SHAFT_H", getattr(s, "SHAFT_ABOVE_CASE", 0.0050) - boss_h)

    cx = -s.SHAFT_OFFSET
    if flange_top_z is None:
        flange_top_z = s.FLANGE_FROM_BOTTOM
    body_bottom = flange_top_z - s.FLANGE_FROM_BOTTOM
    body_top = body_bottom + s.BODY_H
    e = 2 * clr  # 直径方向の膨らみ

    parts = []

    # 本体
    parts.append(add_box(s.BODY_L + e, s.BODY_W + e, s.BODY_H,
                         (cx, 0, body_bottom + s.BODY_H / 2), name + "_body"))

    # 羽根（両耳）。ネジ穴を彫ってから後で join
    flange_z = flange_top_z - s.FLANGE_T / 2
    flange = add_box(s.FLANGE_L + e, s.FLANGE_W + e, s.FLANGE_T, (cx, 0, flange_z), name + "_flange")
    for sx in (-1, 1):
        hole = add_cyl(tab_hole_r, s.FLANGE_T + 0.002, flange_z, "fhole", verts=20,
                       location=(cx + sx * s.SCREW_SPACING / 2, 0, flange_z))
        boolean(flange, hole)
    parts.append(flange)

    # 大円柱（ギアカバー座）: ケース上面に乗る
    parts.append(add_cyl(boss_r, boss_h, body_top + boss_h / 2, name + "_boss", verts=48))

    # 小円柱（出力軸スプライン）: 大円柱の上に乗る
    parts.append(add_cyl(shaft_r, shaft_h, body_top + boss_h + shaft_h / 2,
                         name + "_shaft", verts=24))

    # 配線スタブ（背面 -X）
    parts.append(add_box(0.008, 0.004, 0.004,
                         (cx - s.BODY_L / 2 - 0.004 + 0.001, 0, body_bottom + 0.004),
                         name + "_wire"))

    return join_objects(parts, name)
