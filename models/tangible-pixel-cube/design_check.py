"""設計検算。寸法・カム・こじれ・トルク・歯車・位相・印刷を表で出し、build/design_check.json に保存する。
実行: py -3.11 models/tangible-pixel-cube/design_check.py
単位は mm・度・N・Nm（表示用）。入力は params.py と patterns.py だけ。合格条件は各行に書く。
"""
import json
import math
import os
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P
import cams as C
import kinematics as K
import patterns as PT

MM = 1000.0
ITEMS = []


def add(sec, name, value, limit, kind, unit="mm", note=""):
    """kind: 'min' = value >= limit で合格、'max' = value <= limit で合格。余裕 = 合格側に何 unit 残るか"""
    if kind == "min":
        ok = value >= limit - 1e-6
        margin = value - limit
    else:
        ok = value <= limit + 1e-6
        margin = limit - value
    ITEMS.append({"section": sec, "name": name, "value": round(float(value), 4), "limit": round(float(limit), 4),
                  "kind": kind, "unit": unit, "margin": round(float(margin), 4), "pass": bool(ok), "note": note})


def add_info(sec, name, text):
    ITEMS.append({"section": sec, "name": name, "value": text, "limit": None, "kind": "info", "unit": "",
                  "margin": None, "pass": True, "note": ""})


def add_bool(sec, name, ok, note=""):
    ITEMS.append({"section": sec, "name": name, "value": bool(ok), "limit": True, "kind": "bool", "unit": "",
                  "margin": None, "pass": bool(ok), "note": note})


def mm(v):
    return v * MM


# ---------------------------------------------------------------------------------------------
# 入力: 既定の表からカムを作る
# ---------------------------------------------------------------------------------------------
cams = C.build_all(PT.TABLES)
RB = mm(P.CAM_RB)
ZC = mm(P.CAM_AXIS_Z)
ZS = mm(P.SERVO_AXIS_Z)
T_CAM = mm(P.CAM_T)
DRIFT = mm(P.AXIAL_DRIFT)
GAP = mm(P.GEAR_GAP)
GAPS = 0.5                                  # 動かない部品との隙間の下限（足は X に動かない）
RMAX_ACT = round(max(c["rmax_mm"] for row in cams for c in row), 3)      # 実際に作られたカムの最大半径（多角形は円に外接するので 0.0001mm 大きい。3 桁に丸める）
RMIN_ACT = round(min(c["rmin_mm"] for row in cams for c in row), 3)

# ---------------------------------------------------------------------------------------------
# A. X 方向の配置
# ---------------------------------------------------------------------------------------------
SEC = "A X方向"
shift = mm(P.ROW_SHIFT)
foot_ext = mm(P.SLOT_X) / 2             # 足の X 方向の最大の張り出し（十字溝の中で片側 0.2 動く位置）

add(SEC, "隣の行のカムどうし（回転円が重なるので X で離す）", 2 * shift - T_CAM - 2 * DRIFT, GAP, "min",
    note=f"行のずれ ±{shift} -> 中心 {2 * shift}、カム厚 {T_CAM}、軸の遊び 片側 {DRIFT} x 2")
add(SEC, "足（溝の中で動く）と隣の行のカム", 2 * shift - foot_ext - T_CAM / 2 - DRIFT, GAP, "min",
    note="足は Z が -3 のとき隣の軸のカムの回転円の高さにある")

col_x = [mm(K.col_x(i)) for i in range(P.N)]
foot_edges = []
cam_edges = []
for j in range(P.N):
    for i in range(P.N):
        x = col_x[i] + (shift if j % 2 == 0 else -shift)
        foot_edges.append((x - foot_ext, x + foot_ext))
        cam_edges.append((x - T_CAM / 2 - DRIFT, x + T_CAM / 2 + DRIFT))
gear_lo = mm(P.GEAR_X0) - DRIFT             # 歯車（軸と一体）は軸ごと ±0.2 動く
gear_hi = mm(P.GEAR_X1) + DRIFT
foot_far = max(hi for lo, hi in foot_edges)
cam_far = max(hi for lo, hi in cam_edges)
add(SEC, "最も +X の足と歯車の -X 面（遊び込み。足は X に動かない）", gear_lo - foot_far, GAPS, "min",
    note="歯車の歯先 Zc+9.5 は足の下面（-3 で Zc+5.3）より高いので Z も重なる")
add(SEC, "最も +X のカム面（遊び込み）と歯車の -X 面（遊び込み）", gear_lo - cam_far, GAP, "min", note=f"カム面 {cam_far:.2f}、歯車 {gear_lo:.2f}")
add(SEC, "歯車（遊び込み）と +X パッドの内面", mm(P.PAD_X0) - gear_hi, GAP, "min", note="パッドは Z >= Zc-5。歯車は Zc±9.5 なので Z も重なる")
add(SEC, "受けの +X 面と +X 端壁の内面", mm(P.PAD_X1) - mm(P.RECV_X1), GAP, "min", note="支えのピンが壁の止まり穴へ入る")
add(SEC, "止まり穴の底から壁の外面までの肉（外装壁）", mm(P.PAD_X1) + mm(P.WALL_END) - mm(P.RECV_WALL_HOLE_BOTTOM), 2.0, "min")
add(SEC, "支えのピンと穴の隙間（片側）", (mm(P.RECV_WALL_HOLE_D) - mm(P.RECV_PIN_D)) / 2, 0.2, "min", note="支えだけ。位置ずれ 0.5mm まで許す")
add(SEC, "ピンの先と穴の底", mm(P.RECV_WALL_HOLE_BOTTOM) - mm(P.RECV_PIN_X1), 0.5, "min")
add(SEC, "軸の端（遊び込み）と端壁の内面", mm(P.PAD_X1) - (mm(P.JOURNAL_END) + DRIFT), 0.2, "min")
add(SEC, "軸の肩とパッドの内面（片側の軸方向の遊び）", mm(P.PAD_X0) - mm(P.SHAFT_HALF_L), DRIFT, "min", note="これが AXIAL_DRIFT そのもの")
add(SEC, "パッドの厚み（壁の上の出っ張り。壁本体は 3mm）", mm(P.PAD_T), 1.2, "min", note="停動でも軸受けの力は 15N 未満。壁本体 3mm が支える")
add(SEC, "U 溝の下の肉（溝の底からパッドの下端まで）", mm(P.PAD_BOT) - mm(P.U_SLOT_W) / 2, 1.2, "min")
add(SEC, "端壁の厚み（力を受ける壁）", mm(P.WALL_END), 3.0, "min")
add(SEC, "歯車の噛み合う幅（歯幅 - 遊び 0.2 x 2）", mm(P.GEAR_T) - 2 * DRIFT, 2.0, "min", note="隣の軸の歯車どうしは両方動く")
bore_R = mm(P.SHAFT_BORE_AF) / math.sqrt(3)
add(SEC, "カム最小半径と六角穴の外接円（穴の周りの肉）", RMIN_ACT - bore_R, 1.2, "min", note=f"穴の外接 R{bore_R:.3f}")
add(SEC, "スリーブ半径と六角穴の外接円（肉）", mm(P.SLEEVE_R) - bore_R, 1.2, "min")
add(SEC, "歯車の歯底半径と六角穴の外接円（歯車は軸と別部品）", mm(P.CHAIN_GEAR_ROOT_R) - bore_R, 1.2, "min")
add(SEC, "C クリップの溝の底の半径（軸の強さ）", mm(P.CLIP_GROOVE_R), 2.5, "min", note="六角の面までの距離 3.25 に対し、溝の底 R2.9")
add(SEC, "軸の鍔（六角 AF9.5）の外接円と隣の軸の鍔・歯車の歯先との隙間", mm(P.PITCH) - mm(P.COLLAR_AF) / math.sqrt(3) - mm(P.COLLAR_AF) / math.sqrt(3), GAP, "min", note="鍔は X 43.0..43.6、歯車の歯は 40.6..43.0。鍔どうしは同じ X")
add(SEC, "鍔の +X 面（遊び込み）と +X パッドの内面", mm(P.PAD_X0) - (mm(P.SHAFT_HALF_L) + DRIFT), 0.0, "min", note="軸の肩の遊び 0.2 そのもの")

# ---------------------------------------------------------------------------------------------
# B. Y 方向
# ---------------------------------------------------------------------------------------------
SEC = "B Y方向"
P_ = mm(P.PITCH)
add(SEC, "カムの回転円（実際の最大）と隣の軸のスリーブ", P_ - RMAX_ACT - mm(P.SLEEVE_R), GAP, "min",
    note=f"カム Rmax {RMAX_ACT:.3f}、スリーブ R{mm(P.SLEEVE_R)}、軸の間 {P_}")
inner_y = mm(P.INNER_Y) / 2
add(SEC, "外側の軸のカム回転円と ±Y 側壁の内面", inner_y - (2 * P_ + RMAX_ACT), GAP, "min",
    note=f"側壁 {mm(P.WALL_Y)}、内面 {inner_y}")
add(SEC, "外側の軸の歯車の歯先と ±Y 側壁の内面", inner_y - (2 * P_ + mm(P.CHAIN_GEAR_TIP_R)), GAP, "min")
add(SEC, "歯車の噛み合い: 歯先と相手の歯底の隙間（標準 0.25）", P_ - mm(P.CHAIN_GEAR_TIP_R) - mm(P.CHAIN_GEAR_ROOT_R), 0.2, "min",
    note="中心距離 17 = PD 17")
add(SEC, "外側の画素の足（Y ±10）と側壁の内面", inner_y - (2 * P_ + mm(P.FOOT_Y) / 2), GAP, "min")
add(SEC, "外側の画素のつばと側壁の内面", inner_y - (2 * P_ + mm(P.FLANGE_W) / 2), GAP, "min")
add(SEC, "外側の画素のつばと端壁の内面（X）", mm(P.INNER_X) / 2 - (2 * P_ + mm(P.FLANGE_W) / 2), GAP, "min")
add(SEC, "受けの長腕の先の回転円と側壁の内面", inner_y - mm(P.RECV_BAR_R), GAP, "min")
add(SEC, "受けの長腕の回転円（R20.6）と軸 1・3 の歯車の歯先円（同じ X の面）", math.hypot(P_, mm(P.SERVO_CD)) - mm(P.RECV_BAR_R) - mm(P.CHAIN_GEAR_TIP_R), GAP, "min",
    note="軸 1/3 の歯車は Y ±17、Zc。受けは Y 0、Zs。中心距離 32.3")
# サーボ本体と耳（native X -> +Y）
body_y0 = mm(P.SG.BODY_CENTER_X) - mm(P.SG.FLANGE_L) / 2
add(SEC, "サーボの耳の -Y 端と -Y 側壁の内面", body_y0 + inner_y, GAP, "min", note=f"耳 {body_y0:.1f}..{mm(P.SG.BODY_CENTER_X) + mm(P.SG.FLANGE_L) / 2:.1f}")
# 案内板の穴の桟
web_x = 2 * shift - mm(P.SLOT_X)
web_y = (P_ - mm(P.HOLE_W) / 2) - mm(P.SLOT_Y) / 2
add(SEC, "案内板: 隣の行の十字溝どうしの桟（X）", web_x, 1.2, "min")
add(SEC, "案内板: 十字溝の端と隣の行の角穴の桟（Y）", web_y, 1.2, "min")
add(SEC, "案内板: 同じ行の角穴どうしの桟", P_ - mm(P.HOLE_W), 1.2, "min")
add(SEC, "ベゼル: 窓と窓の桟", mm(P.BEZEL_BAR), 1.2, "min")

# ---------------------------------------------------------------------------------------------
# C. Z 方向の積み
# ---------------------------------------------------------------------------------------------
SEC = "C Z方向"
add(SEC, "受けの長腕の先（最下）と底の上面", ZS - mm(P.RECV_BAR_R) - mm(P.FLOOR), GAP, "min", note=f"Zs {ZS:.2f}")
add(SEC, "サーボ本体の上面（Zs+6）とカムの回転円の下端", (ZC - RMAX_ACT) - (ZS + mm(P.SG.BODY_W) / 2), GAP, "min")
add(SEC, "受けの長腕の先（最上）と +X パッドの下端（受け X 40.5..43.7 とパッド X 43.6.. が 0.1 重なる）", (ZC - mm(P.PAD_BOT)) - (ZS + mm(P.RECV_BAR_R)), GAP, "min")
add(SEC, "端の歯車の下端（歯先）と半円歯車（噛み合い）の中心距離のずれ", abs(ZC - ZS - mm(P.SERVO_CD)), 0.001, "max",
    note="Zc - Zs = (38+17)/2 = 27.5")
add(SEC, "カムの回転円の上端（実際）と案内板の下面", mm(P.PLATE_Z0) - (ZC + RMAX_ACT), GAP, "min")
add(SEC, "歯車の歯先の上端（Zc+9.5）と案内板の下面", mm(P.PLATE_Z0) - (ZC + mm(P.CHAIN_GEAR_TIP_R)), GAP, "min")
add(SEC, "案内板の上面と、-3 のときのつばの下面", (mm(P.FLANGE_BOT_FLUSH) + mm(P.H_MIN)) - mm(P.PLATE_Z1), GAP, "min")
add(SEC, "+3 のときのつばの上面とベゼルの下面（先にカムが止める）", mm(P.BEZEL_Z0) - (mm(P.FLANGE_TOP_FLUSH) + mm(P.H_MAX)), GAP, "min")
add(SEC, "足の下面（面一）とカム最大半径の和: 足の下面 = Zc + Rb", mm(P.CAM_TOP_FLUSH) - (ZC + RB), 0.001, "max")
add(SEC, "外形の最大（画素 +3）", mm(P.BEZEL_Z1) + mm(P.H_MAX), 100.0, "max", note="外見の一辺 10cm 以下")
add(SEC, "頭と窓の隙間（片側）", (mm(P.WINDOW) - mm(P.HEAD)) / 2, 0.2, "min")
add(SEC, "-3 のときの頭の上面とベゼルの下面（窓の深さ 3 = 凹みどおり）", mm(P.FLANGE_TOP_FLUSH) + mm(P.HEAD_H) + mm(P.H_MIN), mm(P.BEZEL_Z0), "min",
    note="頭の上面が窓の底（ベゼルの下面）まで下がり、深さ 3mm の穴に見える")
add(SEC, "案内板の厚み（案内の長さ）", mm(P.PLATE_T), 10.0, "min")
add(SEC, "足が +3 で十字溝へ入る高さ（足の上端と案内板の上面）", mm(P.PLATE_Z1) - (ZC + RB + mm(P.H_MAX) + mm(P.FOOT_H)), 0.0, "min")
add(SEC, "ベゼルの厚み（凹み 3mm の窓の深さを覆う）", mm(P.BEZEL_T), 3.0, "min")
add(SEC, "床の厚み", mm(P.FLOOR), 3.0, "min")
add(SEC, "Y 側壁（外装）", mm(P.WALL_Y), 2.0, "min")

# ---------------------------------------------------------------------------------------------
# A2. 軸ごとの X の並び（カム・歯車・スリーブ・パッド）。bpy 担当が使う
# ---------------------------------------------------------------------------------------------
SEC = "A2 軸の並び"
LAYOUT = {}
ok_nov = True
min_gap_axis = 1e9
clip_pos = {}
for j in range(P.N):
    cx = sorted((mm(K.cam_x(i, j)) - T_CAM / 2, mm(K.cam_x(i, j)) + T_CAM / 2, i) for i in range(P.N))
    members = []
    hubs = []
    for n, (x0, x1, i) in enumerate(cx):
        members.append(("cam", f"cam_{i}_{j}", x0, x1))
        nxt = cx[n + 1][0] if n + 1 < len(cx) else mm(P.GEAR_X0)
        hubs.append((f"cam_{i}_{j}", x1, nxt))              # ハブ = カム板の +X 面から次の部材の -X 面まで（R5.2 の円筒）
    members.append(("gear", f"gear_{j}", mm(P.GEAR_X0), mm(P.GEAR_X1)))
    members.append(("collar", f"shaft_{j}_collar", mm(P.COLLAR_X0), mm(P.SHAFT_HALF_L)))
    clip_x1 = cx[0][0]
    clip_pos[j] = (clip_x1 - mm(P.CLIP_T), clip_x1)
    LAYOUT[j] = {"y_mm": mm(K.axis_y(j)), "z_mm": ZC,
                 "members": [(k, n, round(a, 3), round(b, 3)) for k, n, a, b in members],
                 "hubs": [(n, round(a, 3), round(b, 3)) for n, a, b in hubs],
                 "clip_x": [round(clip_pos[j][0], 3), round(clip_pos[j][1], 3)],
                 "bare_hex_x": [-mm(P.SHAFT_HALF_L), round(clip_pos[j][0], 3)],
                 "shaft_hex_x": [-mm(P.SHAFT_HALF_L), mm(P.SHAFT_HALF_L)],
                 "journal_x": [-mm(P.JOURNAL_END), mm(P.JOURNAL_END)]}
    ms = sorted(members, key=lambda m: m[2])
    for a, b in zip(ms, ms[1:]):
        g = b[2] - a[3]
        min_gap_axis = min(min_gap_axis, g)
        if g < -1e-6:
            ok_nov = False
add_bool(SEC, "同じ軸の部材（カム・歯車・鍔）が X で重ならない", ok_nov, note=f"最小のすき間 {min_gap_axis:.2f}mm（ここはカムのハブが埋める）")
hub_max = max(b - a for L in LAYOUT.values() for n, a, b in L["hubs"])
add(SEC, "カムのハブの最長（刷るとき板の上に立てる円筒 Ø10.4）の高さ / 径", hub_max / (2 * mm(P.SLEEVE_R)), 5.0, "max", unit="倍", note=f"最長 {hub_max:.1f}mm。ハブは +X 側だけ。-X 側にはハブも別のスリーブも無い")
add(SEC, "束が連続（クリップ -> カム -> ハブ -> ... -> 歯車）で、ハブの最短が 0 以上", min(b - a for L in LAYOUT.values() for n, a, b in L["hubs"]), 0.0, "min", note="最短は偶数行の最後のカムと歯車の間の 1.3mm")
add_info(SEC, "軸 2（偶数行）の並び（X mm）", " ".join(f"{n}[{a:.1f},{b:.1f}]" for k, n, a, b in LAYOUT[2]["members"]) + f" クリップ{LAYOUT[2]['clip_x']}")
add_info(SEC, "軸 0（偶数行）の並び（X mm）", " ".join(f"{n}[{a:.1f},{b:.1f}]" for k, n, a, b in LAYOUT[0]["members"]) + f" クリップ{LAYOUT[0]['clip_x']}")
add_info(SEC, "軸 1（奇数行）の並び（X mm）", " ".join(f"{n}[{a:.1f},{b:.1f}]" for k, n, a, b in LAYOUT[1]["members"]) + f" クリップ{LAYOUT[1]['clip_x']}")
add_info(SEC, "組立の通し順（各軸）", "gear_j を -X 端から通して +X の鍔に当てる -> cam を +X 側から順に（cam_4, cam_3, ... cam_0）-X 端から通す -> shaft_clip_j を溝に嵌める")

# ---------------------------------------------------------------------------------------------
# C2. サーボ・配線・鍵
# ---------------------------------------------------------------------------------------------
SEC = "C2 サーボ・配線・鍵"
add(SEC, "サーボ本体の下面（Zs-6）の台の高さ（底から。台で支える）", ZS - mm(P.SG.BODY_W) / 2 - mm(P.FLOOR), 0.0, "min", note="台は底から立つ柵（取付耳を 1.6mm の柵で挟む）")
add(SEC, "サーボ本体の X の範囲（底面〜ギアカバー上面）", mm(P.SERVO_BODY_X0) + mm(P.SG.GEAR_COVER_BOTTOM_Z + P.SG.GEAR_COVER_H), mm(P.RECV_HUB_X0), "max",
    note=f"本体 X {mm(P.SERVO_BODY_X0):.1f}..{mm(P.SERVO_BODY_X0) + 27:.1f}、受けの -X 面（ハブの口）{mm(P.RECV_HUB_X0):.1f}")
add(SEC, "ホーンの腕の下面と受けの -X 面（ポケットの深さ 1.6 に腕 1.5）", mm(P.RECV_POCKET) - mm(P.SG.HORN_ARM_T), 0.05, "min")
horn_arm_x0 = mm(P.SERVO_BODY_X0) + mm(P.SG.HORN_ARM_BOTTOM_Z)
add(SEC, "ホーンの腕の下面の X と受けの -X 面の差（ポケットの口。腕の下 0.1）", horn_arm_x0 - mm(P.RECV_HUB_X0), -0.1, "min", note="腕の下面は受けの面より 0.1 内側（受けの面の上）。= +0.1 のとき腕が受けの面から出ない")
add(SEC, "配線の窓（+Y 壁、幅）", mm(P.WIRE_WIN_W), mm(P.CONNECTOR_W) + 2.0, "min", note=f"コネクタ {mm(P.CONNECTOR_W):g} + 片側 1.0")
add(SEC, "配線の窓（垂直な辺の高さ）", mm(P.WIRE_WIN_H), mm(P.CONNECTOR_T) + 2.0, "min", note=f"コネクタ {mm(P.CONNECTOR_T):g} + 片側 1.0")
add(SEC, "配線の窓の下端と底の上面", ZS - mm(P.WIRE_WIN_H) / 2 - mm(P.FLOOR), 1.2, "min", note=f"窓 X={mm(P.SERVO_BODY_X0) + mm(P.SG.WIRE_EXIT_Z):.1f}±4、Z={ZS:.1f}±{mm(P.WIRE_WIN_H) / 2:g}（上は 45° の尖り屋根）、+Y 壁 Y=46..48。コネクタは窓から外へ")
add(SEC, "サーボの配線の出口の Y（本体の +Y 端）と +Y 壁の内面", inner_y - (mm(P.SG.BODY_CENTER_X) + mm(P.SG.BODY_L) / 2), 10.0, "min", note="配線は +Y 端から壁の窓まで曲げて通す")

# 鍵の代わりの、六角の 1 つの角の非対称な切り落とし（キラル）と、位相合わせ治具 phase_comb
SEC = "C3 切り落とし・潰しリブ・治具"
Ac = mm(P.SHAFT_AF)
ap_s = Ac / 2                              # 軸の六角の面までの距離（3.25）
ap_b = mm(P.SHAFT_BORE_AF) / 2             # 穴の六角の面までの距離（3.45）
Rc_s = Ac / math.sqrt(3)
cut_d, cut_db = mm(P.HEX_CUT_D), mm(P.HEX_CUT_BORE_D)
cut_n = np.array([math.cos(math.radians(P.HEX_KEY_NORMAL_DEG)), math.sin(math.radians(P.HEX_KEY_NORMAL_DEG))])


def hex_vertices(af):
    r = af / math.sqrt(3)
    return np.array([[r * math.cos(math.radians(60 * k)), r * math.sin(math.radians(60 * k))] for k in range(6)])


def clip_halfplane(poly, n, d):
    out = []
    for a_, b_ in zip(poly, np.roll(poly, -1, axis=0)):
        da, db = a_ @ n - d, b_ @ n - d
        if da <= 0:
            out.append(a_)
        if da * db < 0:
            t = da / (da - db)
            out.append(a_ + (b_ - a_) * t)
    return np.array(out)


shaft_poly = clip_halfplane(hex_vertices(Ac), cut_n, cut_d)          # 軸の断面（六角 + 1 つの角を切り落とし）
bore_cons = [(np.array([math.cos(math.radians(90 + 60 * k)), math.sin(math.radians(90 + 60 * k))]), ap_b) for k in range(6)] + [(cut_n, cut_db)]


def penetration(poly):
    """poly の頂点が穴の拘束（六角 + 出っ張り面）に食い込む深さの最大（mm。負 = 全部入る）"""
    return max(float(v @ n_ - d_) for v in poly for n_, d_ in bore_cons)


def cut_only_penetration(poly):
    return max(float(v @ cut_n - cut_db) for v in poly)


worst_all, worst_cut, ident = 1e9, 1e9, None
for r_ in range(6):
    for m_ in (False, True):
        S_ = shaft_poly.copy()
        if m_:
            ca = math.radians(P.HEX_CUT_CORNER_DEG)
            Rm = np.array([[math.cos(2 * ca), math.sin(2 * ca)], [math.sin(2 * ca), -math.cos(2 * ca)]])   # 切り落とす角の二等分線に対する鏡像
            S_ = S_ @ Rm.T
        a_ = math.radians(60 * r_)
        S_ = S_ @ np.array([[math.cos(a_), -math.sin(a_)], [math.sin(a_), math.cos(a_)]]).T
        if r_ == 0 and not m_:
            ident = penetration(S_)
            continue
        worst_all = min(worst_all, penetration(S_))
        worst_cut = min(worst_cut, cut_only_penetration(S_))
add(SEC, "切り落とし: 正しい向きの軸が穴に入る（食い込み = 隙間の符号を反転）", -ident, 0.2, "min", note="軸の全頂点が穴の六角と出っ張り面から 0.2mm 以上内側")
add(SEC, "切り落とし: 鏡像・60° おきの回しの軸（11 通り）が穴に食い込む深さの最小", worst_all, 0.3, "min",
    note=f"切り落とし面の法線 {P.HEX_KEY_NORMAL_DEG:.0f}°、角 {P.HEX_CUT_CORNER_DEG:.0f}° から {P.HEX_CUT_TILT_DEG:.0f}° 傾け、深さ {mm(P.HEX_CUT_DEPTH)}。通らない")
add(SEC, "切り落とし: 同じ 11 通りが櫛の切り欠き（上半分）の出っ張りに食い込む深さの最小", worst_cut, 0.3, "min", note="櫛は出っ張り面だけで向きを読む。向き違いの軸を入れると櫛が浮いて耳が座らない")
add(SEC, "切り落とし: 軸の切り落とし面までの距離（軸の最小の太さ）", cut_d, 2.5, "min", note="六角の面までの距離 3.25、角まで 3.75。切り落とし面 2.74。肉は削るだけで穴の外側は変わらない")
v120 = hex_vertices(Ac)[2]
add(SEC, "切り落とし: 隣の角（120°）に切り落とし面がかからない余裕", cut_d - float(v120 @ cut_n), 0.1, "min", note="かかると切り落としが 2 つの角に広がる")
V60, V0 = hex_vertices(Ac)[1], hex_vertices(Ac)[0]
t_end = (V60 @ cut_n - cut_d) / (cut_n @ (V60 - V0))
cut_len_on_flat = t_end * float(np.linalg.norm(V60 - V0))
add(SEC, "切り落とし: 面（法線 30°）に食い込む長さと、その面の中央の潰しリブ（幅 0.6）の間", Ac / math.sqrt(3) / 2 - mm(P.HEX_RIB_W) / 2 - cut_len_on_flat, 0.2, "min",
    note=f"切り落としが面に掛かる長さ {cut_len_on_flat:.2f}mm。面の長さの半分 1.88")
add(SEC, "カム番号の刻み深さと残る厚み", T_CAM - mm(P.CAM_LABEL_DEPTH), 3.0, "min")

# 潰しリブ
sig_c = 15.0                               # リブの先の押し潰し応力（MPa）。仮定（PLA の降伏 50〜60 の約 1/4）。要実測
crush = mm(P.HEX_RIB_CRUSH)
add(SEC, "潰しリブ: 潰し代（0.15〜0.20）", crush, 0.15, "min", note="リブの高さ 0.38 = 穴の隙間 0.2 + 潰し代 0.18")
add(SEC, "潰しリブ: 潰し代の上限", crush, 0.20, "max")
add(SEC, "潰しリブ: 穴の面の隙間（リブの無い面）", mm(P.SHAFT_BORE_CLR), 0.2, "min", note="1 面おき（法線 30°, 150°, 270°）の 3 面にだけリブ。残り 3 面は隙間 0.2 のまま")
N_rib_cam = sig_c * mm(P.HEX_RIB_W) * mm(P.HEX_RIB_L_CAM)       # N
N_rib_gear = sig_c * mm(P.HEX_RIB_W) * mm(P.HEX_RIB_L_GEAR)
F_cam = 3 * 0.35 * N_rib_cam
F_gear = 3 * 0.35 * N_rib_gear
add(SEC, "潰しリブ: カムの押し込み力の見積り（リブ 3 本 x 面圧 15MPa x 幅 0.6 x 長さ 4 x μ0.35）", F_cam, 40.0, "max", unit="N",
    note="手で押せる範囲。面圧 15MPa は仮定。実測で潰し代を 0.15〜0.20 の中で調整")
add(SEC, "潰しリブ: 歯車の押し込み力の見積り（長さ 2.4）", F_gear, 40.0, "max", unit="N")
cap_gear = 3 * 0.35 * N_rib_gear * ap_s            # N mm（歯車の滑り始めるトルク）
cap_cam = 3 * 0.35 * N_rib_cam * ap_s

# 位相合わせ治具 phase_comb
comb_x0, comb_x1 = mm(P.COMB_X0), mm(P.COMB_X1)
clip_min = min(v[0] for v in clip_pos.values())
add(SEC, "治具: 櫛の -X 面と -X パッドの内面", comb_x0 - (-mm(P.PAD_X0)), GAP, "min", note=f"櫛 X {comb_x0:.1f}..{comb_x1:.1f}、パッド内面 {-mm(P.PAD_X0):.1f}")
add(SEC, "治具: 櫛が軸の裸の六角の上にある（遊び -0.2 込み。-X の肩の内側）", comb_x0 - (-mm(P.SHAFT_HALF_L) + DRIFT), 0.0, "min")
add(SEC, "治具: 櫛の +X 面と最も -X のクリップの溝の間", clip_min - comb_x1, GAP, "min", note="奇数行のクリップは -40.8..-39.3。クリップは櫛を抜いてから嵌める")
add(SEC, "治具: 切り欠きの角の隙間（水平、片側）", mm(P.SHAFT_BORE_AF) / math.sqrt(3) - mm(P.SHAFT_AF) / math.sqrt(3), 0.2, "min", note="切り欠きは六角（AF6.9、平らな面が上）の上半分 + 角から下へ垂直 2mm")
add(SEC, "治具: 切り欠きの天井と軸の上の面の隙間", ap_b - ap_s, 0.2, "min")
add(SEC, "治具: 向きが違う軸のとき櫛が浮く量（軸の角が出っ張りに食い込む深さの最小）", worst_cut, 0.3, "min", note="正しい向きでは耳がパッドに座る。浮けば向き違い")
add(SEC, "治具: 切り欠きの間の板の幅", mm(P.PITCH) - 2 * mm(P.SHAFT_BORE_AF) / math.sqrt(3), 1.2, "min")
add(SEC, "治具: 切り欠きの上の板の高さ", mm(P.COMB_BAR_ABOVE), 1.2, "min")
add(SEC, "治具: 櫛の厚み", mm(P.COMB_T), 1.2, "min")
add(SEC, "治具: 櫛の Y 端と側壁の内面", inner_y - mm(P.COMB_Y_HALF), GAP, "min")
ear_gap = min(abs(abs(y) - mm(K.axis_y(j)) * 0 - 0) for y in [0] ) if False else 0
slot_w = mm(P.U_SLOT_W)
ear_edges = [(mm(y) - mm(P.COMB_EAR_W) / 2, mm(y) + mm(P.COMB_EAR_W) / 2) for y in P.COMB_EAR_Y]
slot_edges = [(mm(K.axis_y(j)) - slot_w / 2, mm(K.axis_y(j)) + slot_w / 2) for j in range(P.N)]
ear_web = min(min(abs(a1 - b0), abs(b1 - a0)) for a0, a1 in ear_edges for b0, b1 in slot_edges if not (a1 < b0 - 20 or a0 > b1 + 20))
add(SEC, "治具: 耳（Y 幅 6、軸の間に 4 つ）と U 溝の端の間", ear_web, 1.2, "min", note="耳は -X パッドの上面（軸の中心 +3.45）に座る")
add(SEC, "治具: 耳とパッドの X の重なり", (-mm(P.PAD_X0)) - mm(P.COMB_EAR_X0), 0.5, "min", note=f"耳 X {mm(P.COMB_EAR_X0):.1f}..{comb_x1:.1f}、パッド -45..-43.8")
add_info(SEC, "治具の使い方", "5 本の軸（カム・歯車付き、クリップ無し）の -X の裸の六角に上から被せる -> 耳がパッドに座るまで下ろす -> 5 本が切り落とし面の向き（φ0）で U 溝に収まる -> 受けと歯車が噛んだことを確かめて上へ抜く -> shaft_clip_j を嵌める。最終形には残さない")
add_info(SEC, "歯の位相（φ=0、サーボ 90 度）", f"全軸の 17T: +Y の向きに歯の中心（{P.CHAIN_TOOTH_PHASE_DEG}°、21.176° ごと。奇数歯なので -Y は谷）。歯車の枠では切り落とし面の法線から歯の中心まで {P.GEAR_TOOTH_FROM_KEY_DEG:.3f}°（法線 {P.HEX_KEY_NORMAL_DEG:.0f}°）。受けの 38T: 歯の中心が {P.SECTOR_TOOTH_PHASE_DEG:.3f}°（+Y から +Z へ、9.474° ごと）")

# 歯の噛み合いの位相を数値で確かめる（治具の姿勢 = φ0、サーボ 90 度、および各表の角度）
def tooth_arc_positions(zt, phase_deg, rot_deg, r_pitch, contact_deg, span_deg=40.0):
    """歯の中心の、接点からの円弧上の位置（mm、接点から +角度の向きが正）"""
    pitch = 360.0 / zt
    out = []
    for k in range(zt):
        a = (phase_deg + rot_deg + pitch * k - contact_deg + 180.0) % 360.0 - 180.0
        if abs(a) <= span_deg:
            out.append(math.radians(a) * r_pitch)
    return out


def mesh_error(posA, posB):
    """A の歯の中心が、B の隣り合う歯の中心の真ん中にあるか。誤差の最大（mm）。B の円弧は向きが逆なので符号を反転して渡す"""
    p = math.pi * mm(P.GEAR_M)
    worst = 0.0
    for a in posA:
        if abs(a) > 1.8 * p:
            continue
        d = min(abs(((a - b) % p) - p / 2) for b in posB)
        worst = max(worst, d)
    return worst


mesh_worst = 0.0
mesh_at = None
rA = mm(P.CHAIN_GEAR_PD) / 2
rS = mm(P.SERVO_GEAR_PD) / 2
sec_err = 0.0
for th_t in list(P.TABLE_THETA) + [P.THETA_FLAT, 10.0, 170.0]:
    rots = [K.axis_angle(th_t, j) for j in range(P.N)]
    for j in range(P.N - 1):
        pa = tooth_arc_positions(P.CHAIN_Z, P.CHAIN_TOOTH_PHASE_DEG, rots[j], rA, 0.0)
        pb = [-v for v in tooth_arc_positions(P.CHAIN_Z, P.CHAIN_TOOTH_PHASE_DEG, rots[j + 1], rA, 180.0)]
        e = mesh_error(pa, pb)
        if e > mesh_worst:
            mesh_worst, mesh_at = e, (th_t, j)
    dS = K.servo_delta(th_t)
    ps = tooth_arc_positions(P.SERVO_Z, P.SECTOR_TOOTH_PHASE_DEG, dS, rS, 90.0)
    pg = [-v for v in tooth_arc_positions(P.END_Z, P.END_TOOTH_PHASE_DEG, rots[2], rA, 270.0)]
    sec_err = max(sec_err, mesh_error(ps, pg))
add(SEC, "歯車の位相: 隣の軸どうしの歯の中心が相手の谷の中心に合う（φ0 と各表の角度）", mesh_worst, 0.05, "max", unit="mm",
    note=f"歯の中心と谷の中心のずれの最大。最悪 サーボ{mesh_at[0]:.0f}° 軸{mesh_at[1]}-{mesh_at[1] + 1}。バックラッシュ 0.1 の半分以下")
add(SEC, "歯車の位相: 受けの半円歯車と中央の軸の歯車（サーボ 90 度ほか）", sec_err, 0.05, "max", unit="mm", note="同上。受けの歯の位相 7.105°")
add(SEC, "受けの半円歯車の歯の範囲の余裕（±92° - サーボの ±80°）", P.RECV_ARC_HALF_DEG - 80.0, 10.0, "min", unit="度", note="噛み合い点の前後 10° の歯が要る")

# ---------------------------------------------------------------------------------------------
# D. カム
# ---------------------------------------------------------------------------------------------
SEC = "D カム"
lat_max = max(c["lateral_max_mm"] for row in cams for c in row)
foot_half_y = mm(P.FOOT_Y) / 2
add(SEC, "接点の横ずれの最大（全 25 カム、使う角度すべて）", lat_max, foot_half_y - 1.0, "max",
    note=f"足の Y 幅 {mm(P.FOOT_Y)} の半分 - 1mm = {foot_half_y - 1.0}")
add(SEC, "カムの最小半径（全 25）", RMIN_ACT, mm(P.CAM_RMIN) - 1e-3, "min", note="-3 の弧 = 5.3")
add(SEC, "カムの最大半径（全 25）", RMAX_ACT, mm(P.CAM_RMAX) + 1e-3, "max", note="+3 の弧 = 11.3。壁・隣のスリーブから決めた上限")
add_bool(SEC, "全 25 カムが凸（輪郭の外積が全部 >= 0。最小曲率半径 > 0）", all(c["convex"] for row in cams for c in row))
add(SEC, "停止区間での高さ誤差の最大（全 25、全 5 表）", max(c["dwell_err_max_mm"] for row in cams for c in row), 0.01, "max")
# 表どうしの必要角度。目安 = 2w + acos(r_lo/r_hi)（保守的）。真の可否は幾何（上の誤差 0 と横ずれ）
th = list(P.TABLE_THETA)
pairs = []
for k in range(len(th)):
    k2 = (k + 1) % len(th)
    avail = abs(K.wrap180(K.axis_angle(th[k], 2) - K.axis_angle(th[k2], 2)))
    need = 0.0
    for j in range(P.N):
        for i in range(P.N):
            lo, hi = sorted([PT.TABLES[k][j][i], PT.TABLES[k2][j][i]])
            need = max(need, C.required_angle(RB + lo, RB + hi))
    pairs.append((k, k2, avail, need))
for k, k2, avail, need in pairs:
    add_info(SEC, f"表 {k}({PT.NAMES[k]}) と表 {k2}({PT.NAMES[k2]}): 軸の角度差 / 目安の必要角（保守的な下限 = 2w + acos(r低/r高)）",
             f"{avail:.1f} 度 / {need:.1f} 度（真の可否は幾何で決まり、下の誤差 0.002mm で確認済み）")
add_bool(SEC, "全 25 カム x 5 表で停止区間が表どおり（幾何）。足りない表は cams.py が CamError で拒否する",
         max(c["dwell_err_max_mm"] for row in cams for c in row) <= 0.01)
add(SEC, "表の間隔（サーボ角）", min(th[k + 1] - th[k] for k in range(len(th) - 1)), 2 * P.DWELL_HALF_DEG / P.G_RATIO, "min", unit="度",
    note="軸で 2w 以上（停止区間が重ならない）")
add(SEC, "端の表（0 と 4）が一周で隣り合う角度", 360 - abs(K.axis_angle(th[-1], 2) - K.axis_angle(th[0], 2)), 2 * P.DWELL_HALF_DEG, "min", unit="度")

# ---------------------------------------------------------------------------------------------
# E. こじれ（自己ロック）係数 κ
# ---------------------------------------------------------------------------------------------
SEC = "E こじれ"
W_N = P.PIXEL_MASS_G / 1000.0 * 9.81      # 画素の重さ（N）
Z0, Z1 = mm(P.PLATE_Z0), mm(P.PLATE_Z1)
FT = mm(P.FLANGE_TOP_FLUSH)
BZ0, BZ1 = mm(P.BEZEL_Z0), mm(P.BEZEL_Z1)
b_c = mm(P.TOWER_W) / 2                   # 案内の接触の横位置（茎の半幅）
half = K.table_theta_to_phi_range()
PHI = np.arange(-half, half + 1e-9, 0.25)
PHI_ALL = np.arange(-180, 180, 0.25)


def cam_curves(cam):
    V = np.array(cam["vertices"])
    h, lat = C.support(V, PHI_ALL)
    return h, lat


CURVE = [[cam_curves(cams[j][i]) for i in range(P.N)] for j in range(P.N)]


def idx_of(phi):
    return np.round((((np.asarray(phi) + 180) % 360) - 180 + 180) / 0.25).astype(int) % len(PHI_ALL)


def kappa(mu_c, mu_g, e, z1, L, b):
    S = (mu_c + 2 * (np.abs(e) + np.maximum(z1, 0.0) * mu_c) / L) / (1 - 2 * mu_g * b / L)
    return mu_g * S


def guide_geometry(h):
    """h = 接点の高さ（軸からの支持関数、mm）。(z1, L_B, L_A): 足の下面から案内板の下端までの距離、
    窓と板を使った長さ、板だけの長さ"""
    zf = ZC + h
    zlow = np.maximum(Z0, zf)             # 下の案内の接触: 板の下端、足が板の中へ入っていれば足の下面
    z1 = zlow - zf
    H = h - RB
    lo = np.maximum(BZ0, FT + H)
    hi = np.minimum(BZ1, BZ1 + H)
    zw = (lo + np.maximum(lo, hi)) / 2
    return z1, zw - zlow, Z1 - zlow


worst = {}
for tag, (mc, mg) in {"0.35": (P.MU_CAM, P.MU_GUIDE), "0.45": (P.MU_CAM_HI, P.MU_GUIDE_HI)}.items():
    kB_max = kA_max = 0.0
    locB = locA = None
    for j in range(P.N):
        for i in range(P.N):
            h, lat = CURVE[j][i]
            sel = idx_of(PHI)
            hh, ee = h[sel], lat[sel]
            z1, LB, LA = guide_geometry(hh)
            kB = kappa(mc, mg, ee, z1, LB, b_c)
            kA = kappa(mc, mg, ee, z1, LA, b_c)
            if kB.max() > kB_max:
                kB_max, locB = float(kB.max()), (i, j, float(PHI[kB.argmax()]), float(hh[kB.argmax()] - RB), float(ee[kB.argmax()]))
            if kA.max() > kA_max:
                kA_max, locA = float(kA.max()), (i, j, float(PHI[kA.argmax()]), float(hh[kA.argmax()] - RB), float(ee[kA.argmax()]))
    worst[tag] = (kB_max, locB, kA_max, locA)
kB35, locB35, kA35, locA35 = worst["0.35"]
kB45, locB45, kA45, locA45 = worst["0.45"]
add(SEC, "κ 最大 μc=μg=0.35（頭の窓 + 板の案内の剛体）", kB35, P.KAPPA_LIMIT_LO, "max", unit="",
    note=f"画素({locB35[0]},{locB35[1]}) φ={locB35[2]:.1f}° 高さ{locB35[3]:+.2f} 横ずれ{locB35[4]:.2f}")
add(SEC, "κ 最大 μc=μg=0.45（同）", kB45, 0.999, "max", unit="", note="1 未満なら詰まらない。1 以上は自己ロック")
add(SEC, "κ 最大 μ=0.35、板だけの案内（窓を使わない保守的な見方）", kA35, 0.999, "max", unit="",
    note=f"画素({locA35[0]},{locA35[1]}) φ={locA35[2]:.1f}° 高さ{locA35[3]:+.2f} 横ずれ{locA35[4]:.2f}")
add(SEC, "κ 最大 μ=0.45、板だけの案内", kA45, 0.999, "max", unit="")
add(SEC, "案内の隙間による傾き（板の厚みで、片側 0.2mm）", math.degrees(math.atan2(2 * 0.2, mm(P.PLATE_T))), 3.0, "max", unit="度",
    note="頭の上面の横ぶれ ≈ 傾き x 頭までの距離（約 30mm）= 0.5mm 以下")

# ---------------------------------------------------------------------------------------------
# F. トルク（サーボ軸へ換算）
# ---------------------------------------------------------------------------------------------
SEC = "F トルク"
ETA = P.GEAR_EFF
SHAFT_W_N = 0.15                          # 軸 + カム + 歯車の重さ（約 15g）
R_J = mm(P.JOURNAL_D) / 2
THETAS = np.arange(P.SERVO_MIN_DEG, P.SERVO_MAX_DEG + 1e-9, 0.5)


def torque_sweep(mc, mg):
    tmax = 0.0
    t2max = 0.0
    th_at = None
    inf = False
    for th_s in THETAS:
        tau = []
        for j in range(P.N):
            phi = K.axis_angle(th_s, j)
            sel = int(idx_of(phi))
            s = 0.0
            sumN = 0.0
            for i in range(P.N):
                h, lat = CURVE[j][i]
                hh = np.array([h[sel]])
                ee = np.array([lat[sel]])
                z1, LB, LA = guide_geometry(hh)
                k = float(kappa(mc, mg, ee, z1, LB, b_c)[0])
                if k >= 1.0:
                    inf = True
                    k = 0.99
                N = W_N / (1 - k)
                s += N * (abs(float(ee[0])) + mc * float(hh[0]))      # N mm
                sumN += N
            s += P.BEARING_MU * (sumN + SHAFT_W_N) * R_J
            tau.append(s / 1000.0)                                    # N m
        # 軸 2 から見た合計: 軸 1,3 は 1 噛合、軸 0,4 は 2 噛合
        t2 = tau[2] + (tau[1] + tau[0] / ETA) / ETA + (tau[3] + tau[4] / ETA) / ETA
        t2max = max(t2max, t2)
        # 増速なので軸はサーボの g 倍で回る。仕事の釣り合い τs·ωs = τ2·ωc / η から τs = τ2·g / η
        t_servo = t2 * P.G_RATIO / ETA
        if t_servo > tmax:
            tmax, th_at = t_servo, float(th_s)
    return tmax, th_at, inf, t2max


T35, th35, inf35, T2_35 = torque_sweep(P.MU_CAM, P.MU_GUIDE)
T45, th45, inf45, T2_45 = torque_sweep(P.MU_CAM_HI, P.MU_GUIDE_HI)
lim = P.SERVO_STALL_NM * P.TORQUE_FRAC
add(SEC, "サーボ軸の最大トルク μ=0.35（全画素・全サーボ角、横ずれと摩擦の符号は最悪にそろえる）", T35 * 1000, lim * 1000, "max", unit="mNm",
    note=f"サーボ {th35:.1f}° で最大。停動 {P.SERVO_STALL_NM * 1000:.0f}mNm の 1/3 = {lim * 1000:.1f}。画素 {P.PIXEL_MASS_G}g、歯車効率 {ETA}/噛合")
add(SEC, "サーボ軸の最大トルク μ=0.45", T45 * 1000, lim * 1000, "max", unit="mNm", note=f"サーボ {th45:.1f}°")
add(SEC, "最大トルクの停動に対する割合 μ=0.35", T35 / P.SERVO_STALL_NM * 100, P.TORQUE_FRAC * 100, "max", unit="%")

# ---------------------------------------------------------------------------------------------
# G. 歯車
# ---------------------------------------------------------------------------------------------
SEC = "G 歯車"
m_ = mm(P.GEAR_M)
alpha = math.radians(20)


def contact_ratio(z1, z2, a):
    r1, r2 = z1 * m_ / 2, z2 * m_ / 2
    ra1, ra2 = r1 + m_, r2 + m_
    rb1, rb2 = r1 * math.cos(alpha), r2 * math.cos(alpha)
    L = math.sqrt(ra1 ** 2 - rb1 ** 2) + math.sqrt(ra2 ** 2 - rb2 ** 2) - a * math.sin(alpha)
    return L / (math.pi * m_ * math.cos(alpha))


add(SEC, "モジュール m（mm）", m_, 1.0, "min", unit="mm", note="m1、圧力角 20°、歯先 +1.0m、歯底 -1.25m")
add(SEC, "隣の軸の歯車 17T-17T の中心距離とピッチの差", abs(m_ * P.CHAIN_Z - mm(P.PITCH)), 0.001, "max", note="PD17 = 軸の間 17。中心距離は固定なので歯を細らせてバックラッシュを取る")
add(SEC, "サーボ側 38T-17T の中心距離とサーボ軸 - カム軸の差", abs(m_ * (P.SERVO_Z + P.END_Z) / 2 - mm(P.SERVO_CD)), 0.001, "max")
add(SEC, "歯数 17T（理論最小 17.1 = 2/sin²20°）", P.CHAIN_Z, 16, "min", unit="枚", note="歯元のわずかな削れ（0.02mm 未満）。転位なしで許容")
add(SEC, "噛み合い率 17T-17T", contact_ratio(17, 17, mm(P.PITCH)), 1.2, "min", unit="")
add(SEC, "噛み合い率 38T-17T", contact_ratio(P.SERVO_Z, P.END_Z, mm(P.SERVO_CD)), 1.2, "min", unit="")
add(SEC, "歯幅", mm(P.GEAR_T), 2.0, "min")
add(SEC, "歯先円直径 17T", 2 * mm(P.CHAIN_GEAR_TIP_R), 19.0, "min", note="PD17 + 2 = 19")
add(SEC, "歯元円直径 17T", 2 * mm(P.CHAIN_GEAR_ROOT_R), 14.5, "min", note="PD17 - 2.5 = 14.5")
add(SEC, "歯先円直径 38T（受けの半円歯車）", 2 * mm(P.SERVO_GEAR_TIP_R), 40.0, "min", note="PD38 + 2 = 40。受けの長腕 R20.6 は歯の範囲の外に出る")
add(SEC, "バックラッシュ（1 噛合）", mm(P.GEAR_LASH), 0.1, "min")
F_stall = P.SERVO_STALL_NM * MM / (mm(P.SERVO_GEAR_PD) / 2)       # N（停動で受け側の歯面力）
y17 = 0.30
sig_end = F_stall / ((mm(P.GEAR_T) - 2 * DRIFT) * m_ * y17)          # 軸の遊びで噛み合う幅が減った値
sig_chain = sig_end
add(SEC, "歯面力 停動 = 0.245Nm / 19mm", F_stall, 20.0, "max", unit="N")
add(SEC, "歯の曲げ応力（17T、噛み合う幅 2.0、Lewis Y=0.30、停動で全負荷が通る）", sig_end, 25.0, "max", unit="MPa", note="PLA の許容 25MPa 程度（降伏の半分以下）。実使用の負荷は停動の 1/10")

# ---------------------------------------------------------------------------------------------
# H. 位相と停止区間
# ---------------------------------------------------------------------------------------------
SEC = "H 位相"
a_b = mm(P.SHAFT_BORE_AF) / 2
Rc = mm(P.SHAFT_AF) / math.sqrt(3)
hex_slack = 30.0 - math.degrees(math.acos(a_b / Rc))      # 潰しリブが効かないときの上限（参考）
servo_deg = P.SERVO_ERR_DEG * P.G_RATIO
# 受けの向きの残り。ホーンは 18° 刻みでしか付かず、受けの歯は ±92° にしか無いので、付け方は設計の向きに近い 1 通りに限られる（最大 ±9° ずれる）。
# そのずれは全軸に同じだけ乗るので、組立後に位相補正（デモの + / - で 0.25° 刻み、表の高さで幅を測って中央へ）で消す。
# 補正後の残りを ±0.474°（サーボ角）と見込む: 刻みの半分 0.125° + 幅の端を測る誤差 0.35°。値は以前の 20x38 の組合せの式と同じ数にしてある
vern_step = 360.0 / (20 * 38 / math.gcd(20, 38))        # 2 x 0.474°（補正後の残りの幅）
vern_deg = vern_step / 2 * P.G_RATIO
lash_one = math.degrees(mm(P.GEAR_LASH) / (mm(P.CHAIN_GEAR_PD) / 2))
meshes = [3, 2, 1, 2, 3]                                  # 軸 j がサーボから何噛合（受け-中央の歯車 1 + 隣の軸）
chain_meshes = [2, 1, 0, 1, 2]                            # そのうち隣の軸どうしの噛合の数
fit_cam = P.FIT_ERR_DEG                                   # カム - 軸（潰しリブ）
fit_gear = P.FIT_ERR_DEG                                  # 歯車 - 軸（潰しリブ）
R_g = mm(P.CHAIN_GEAR_PD) / 2                             # 17T の歯車のピッチ半径（8.5）
# (a) 隣り合う軸の高さの差 δ（床の隙間 + 栓の隙間 + 案内板の遊び）。噛み合う接線の方向は Z なので、δ / R がそのまま位相のずれ
delta_a = mm(P.U_FLOOR_CLR) + mm(P.HOLD_GAP) + mm(P.PLATE_PLAY_Z)
ph_a = math.degrees(delta_a / R_g)                        # 1 噛合あたり（= 2δ/CD。CD = 2 x 8.5）
# (b) 中央軸が受けの半円歯車に対して Y へずれる量（38T-17T の噛み合いの接線は Y）= U 溝の Y の隙間 片側
ph_b_mm = mm(P.U_SLOT_Y_CLR)
# (c) 受けの径方向の遊び = ホーンとの隙間（片側 HORN_CLR）。Y 成分が接線
ph_c_mm = mm(P.HORN_CLR)
ph_sector = math.degrees((ph_b_mm + ph_c_mm) / R_g)       # 軸 2 の位相のずれ（(b) + (c)）
tot = [servo_deg + vern_deg + fit_cam + fit_gear + lash_one * meshes[j] + ph_sector + ph_a * chain_meshes[j] for j in range(P.N)]
tau_ax_nmm = T2_45 * 1000.0                                # 軸 2 の歯車が運ぶ最大トルク（N mm、μ0.45）
k_t = 1150.0 * mm(P.HEX_RIB_W) * mm(P.HEX_RIB_L_GEAR) / (mm(P.HEX_RIB_H) - crush)    # リブのせん断剛性（N/mm）。G=1150MPa
twist = tau_ax_nmm / (3 * k_t * ap_s ** 2)                # rad
add(SEC, "潰しリブ: 歯車が滑り始めるトルク / 運転の最大トルク（軸 2、μ0.45）", cap_gear / tau_ax_nmm, 3.0, "min", unit="倍",
    note=f"滑り始め {cap_gear:.0f}N mm、運転 {tau_ax_nmm:.1f}N mm。停動（0.245Nm x g）では滑って歯車を守る")
add(SEC, "潰しリブ: カムが滑り始めるトルク / 運転の最大トルク（軸 2 全体を 1 枚で受けた場合）", cap_cam / tau_ax_nmm, 3.0, "min", unit="倍")
add(SEC, "潰しリブ: 運転の最大トルクでのたわみ（リブのせん断）", math.degrees(twist), 0.2, "max", unit="度", note="せん断剛性 G=1150MPa から。FIT_ERR 1.0 度の内訳: たわみ 0.0x + 潰し代・リブ位置・穴寸法の公差 0.5 + クリープ 0.5")
add(SEC, "潰しリブ嵌めの回転ガタ + たわみの見積り（FIT_ERR）", P.FIT_ERR_DEG, math.degrees(twist) + 0.9, "min", unit="度",
    note="目安 ±1° 以内。根拠: 3 本が潰れて軸を挟み、運転トルクの 3 倍以上の摩擦で滑らない。ガタは潰し代・リブ位置・穴寸法の公差 0.5° とクリープ 0.4° で 0.9° 以内と置く（仮定。要実測）")
add_info(SEC, "参考: 潰しリブが全部効かなかった場合の六角ガタ", f"±{hex_slack:.2f}° x（カムと歯車で 2 箇所）。これだと合計 {servo_deg + vern_deg + 2 * hex_slack + lash_one * 3:.1f}° で停止区間を超える。リブは必須")
add(SEC, "サーボの位置誤差 ±1° x g", servo_deg, 2.5, "max", unit="度")
add(SEC, "受けの向きの残り（位相補正の後）±0.474° x g", vern_deg, 1.2, "max", unit="度",
    note=f"ホーンの付け方は設計に近い 1 通りで最大 ±9° ずれる。全軸に同じだけ乗るので位相補正（0.25° 刻み）で消す。残り ±{vern_step / 2:.3f}°（サーボ角）を軸で {P.G_RATIO:.3f} 倍")
add(SEC, "歯車のバックラッシュ（軸 0/4、3 噛合 x 0.674°）", lash_one * 3, 2.1, "max", unit="度")
add(SEC, "(a) 隣り合う軸の高さの差 δ = 床 0.05 + 栓 0.1 + 案内板 0.05（mm）", delta_a * 1.0, 0.25, "max", unit="mm", note=f"1 噛合あたり {ph_a:.2f}°（= 2δ/CD）。外側の軸は 2 噛合ぶん足す")
add(SEC, "(b)+(c) 中央軸と受けの Y のずれ = U 溝の Y 隙間 0.1 + ホーンとの隙間 0.15（mm）", ph_b_mm + ph_c_mm, 0.3, "max", unit="mm", note=f"軸 2 の位相のずれ {ph_sector:.2f}°（接線のずれ / 歯車 17T のピッチ半径 8.5）")
add_info(SEC, "位相誤差の内訳（最悪の軸 0/4、絶対値の線形和）",
         f"サーボ {servo_deg:.2f} + ホーン合わせ {vern_deg:.2f} + カム嵌め {fit_cam:.2f} + 歯車嵌め {fit_gear:.2f} + バックラッシュ {lash_one * 3:.2f} + (b)(c) {ph_sector:.2f} + (a) {ph_a:.2f} x 2 = {max(tot):.2f}°")
add(SEC, "位相誤差の合計（最悪の軸 0/4、絶対値の線形和）", max(tot), P.DWELL_HALF_DEG, "max", unit="度",
    note=f"停止区間の半幅 {P.DWELL_HALF_DEG} 度が覆う。二乗和の平方根は {math.sqrt(servo_deg ** 2 + vern_deg ** 2 + fit_cam ** 2 + fit_gear ** 2 + (lash_one * 3) ** 2 + ph_sector ** 2 + (2 * ph_a) ** 2):.1f} 度")
add(SEC, "停止区間の半幅と位相誤差の合計の差（余裕）", P.DWELL_HALF_DEG - max(tot), 1.0, "min", unit="度", note="合格条件: 最悪の線形和で 1.0 度以上")
add(SEC, "サーボ 1 度あたりのカム軸の角度 g（下限 2.0）", P.G_RATIO, 2.0, "min", unit="")
add(SEC, "サーボ 1 度あたりのカム軸の角度 g（上限 2.3）", P.G_RATIO, 2.3, "max", unit="")
add_info(SEC, "向きの決め方", "六角の 1 つの角の非対称な切り落とし（キラル）。向きだけを決め、駆動は潰しリブの摩擦。溝・突起が無いので鍵の遊びは無い")
add(SEC, "サーボ使用範囲での軸の角度の幅（±g x 80）", 2 * K.table_theta_to_phi_range(), 360.0, "max", unit="度")
add(SEC, "最も外の表のサーボ角と使用範囲の端の余裕（較正の残り込み）", min(th[0] - P.SERVO_MIN_DEG, P.SERVO_MAX_DEG - th[-1]) - P.CALIB_DEG, 5.0, "min", unit="度",
    note="表 0 = 22°、表 4 = 158°")

# ---------------------------------------------------------------------------------------------
# I. 印刷（刷る向きでの形）
# ---------------------------------------------------------------------------------------------
SEC = "I 印刷"
tower_h = mm(P.FLANGE_BOT_FLUSH) - (ZC + RB + mm(P.FOOT_H))
add(SEC, "画素: 立てた茎（角筒 9x9）の高さ / 最小太さ", tower_h / mm(P.TOWER_W), 5.0, "max", unit="倍", note=f"茎の高さ {tower_h:.1f}、太さ {mm(P.TOWER_W)}。頭を下にして刷る")
add(SEC, "画素: 茎の角筒の肉", mm(P.TOWER_WALL), 1.2, "min")
add(SEC, "画素: 足の面取りの角度（刷る向きで上端が広がる）", math.degrees(math.atan2(mm(P.FOOT_CHAMFER), mm(P.FOOT_CHAMFER))), 45.0, "max", unit="度",
    note=f"9 から {mm(P.FOOT_Y)} へ片側 {mm(P.FOOT_CHAMFER)} を 45°で広げる")
add(SEC, "画素: 角筒の中の空洞の天井（橋）", mm(P.TOWER_W) - 2 * mm(P.TOWER_WALL), 10.0, "max", note="足の側で閉じるときの橋の幅")
add(SEC, "画素: つばの張り出し（頭から片側）", (mm(P.FLANGE_W) - mm(P.HEAD)) / 2, 1.0, "max", note="45° の面取りで逃がす（bpy 側）")
add(SEC, "画素: 足の X 幅（カム厚 + 片側 0.15）", mm(P.FOOT_X), T_CAM + 0.3, "min")
add(SEC, "画素: 足の板の厚み", mm(P.FOOT_FLAT), 1.2, "min")
add(SEC, "カム: 厚み（平置き）", T_CAM, 3.0, "min")
add(SEC, "案内板: 十字溝の桟の最小", min(web_x, web_y), 1.2, "min")
add(SEC, "軸: 寝かせて刷る長さ", 2 * mm(P.SHAFT_HALF_L), 100.0, "max", note="六角面を下に。両端の丸は径が二面幅より小さい。歯車は別部品なので軸に円盤は付かない")
add(SEC, "軸: 鍔（六角 AF9.5、寝かせて刷る）の張り出し角（鉛直から）", 30.0, 45.0, "max", unit="度", note="六角の面が上向き斜め 60° 傾き = 鉛直から 30°")
add(SEC, "歯車 gear_j: 平置き（軸を縦、歯の輪郭が XY 面）で歯の張り出し", 0.0, 0.0, "max", unit="度", note="歯の側面は鉛直。穴は六角 + 鍵の突起 + リブ（鉛直）")
add(SEC, "horn_coupler: ポケットの橋（-X 面を下にして刷る）の最大幅", max(mm(P.SG.HORN_ROOT_W) + 2 * mm(P.HORN_CLR), mm(P.SG.HORN_HUB_DIA) + 2 * mm(P.HORN_CLR)), 10.0, "max", note="ホーンの長腕の付け根 7.3 とハブ 7.3")
add(SEC, "phase_comb: 平置き（YZ 面を下）、切り欠きは上から抜ける形で橋は無い", mm(P.COMB_T), 1.2, "min")

# ---------------------------------------------------------------------------------------------
# I2. 軸の上向きの保持・歯の噛み合いの余裕・受けの降りる経路（印刷の節 I の後ろに足した）
# ---------------------------------------------------------------------------------------------
SEC = "I2 保持と経路"


def _stl_vertices(path):
    # build/ の STL が params.py より古いときは使わない（params から導く）
    if os.path.exists(path) and os.path.getmtime(path) < os.path.getmtime(os.path.join(HERE, 'params.py')):
        return None
    """バイナリ STL の頂点（mm）。無ければ None"""
    if not os.path.exists(path):
        return None
    d = open(path, "rb").read()
    n = int(np.frombuffer(d[80:84], dtype="<u4")[0])
    a = np.frombuffer(d[84:84 + 50 * n], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    return a["v"].astype(float).reshape(-1, 3)


journal_top_rest = ZC - mm(P.U_FLOOR_CLR) + mm(P.JOURNAL_D) / 2          # 軸が溝の底に載ったときの丸の上端（Zc - 0.05 + 3.2）
plate_v = _stl_vertices(os.path.join(HERE, "build", "guide_plate.stl"))
gaps = []
src = "build/guide_plate.stl の実形状"
for j in range(P.N):
    yj = mm(K.axis_y(j))
    if plate_v is None:
        bots = [mm(P.HOLD_PLUG_BOT)]
        src = "params（build/guide_plate.stl が無い）"
    else:
        sel = (np.abs(plate_v[:, 0]) > 43.0) & (np.abs(plate_v[:, 1] - yj) < 3.2) & (plate_v[:, 2] < mm(P.PLATE_Z0) - 0.1)
        bots = [plate_v[sel & (np.sign(plate_v[:, 0]) == sg), 2].min() for sg in (-1, 1)] if sel.any() else [float("nan")]
    gaps.append(min(bots) - journal_top_rest)
gaps = np.round(np.array(gaps), 3)                # STL は float32（1e-5 の誤差）。1 マイクロメートル単位に丸める
add(SEC, "各軸の上向きの隙間の最小（案内板の栓の下端 - 軸の丸の上端。溝の底に載った状態）", float(np.nanmin(gaps)), mm(P.HOLD_GAP_MIN), "min",
    note=f"{src}。栓は軸ごとに両端（U 溝の上）にある")
add(SEC, "各軸の上向きの隙間の最大", float(np.nanmax(gaps)), mm(P.HOLD_GAP_MAX), "max",
    note="中央軸は半円歯車の噛み合いの分離力（運転トルク 18.8N mm / PD17 の接線力 2.2N x tan20 度 = 約 0.8N）で上へ押される。下向きの重さは約 0.34N")
add_info(SEC, "軸ごとの上向きの隙間（mm）", " ".join(f"軸{j}={g:.3f}" for j, g in enumerate(gaps)))
add(SEC, "中央軸の歯車の噛み合いが外れるまでの余裕（歯先の重なり - 最大の上向きの隙間）", mm(P.GEAR_ADD) - float(np.nanmax(gaps)), 0.6, "min",
    note=f"歯先の重なり = 歯先高さ {mm(P.GEAR_ADD):.2f}。受けの半円歯車との噛み合い（歯丈 2.25）が浮きで外れて歯が飛ぶのを防ぐ")
# 軸の浮きの鎖: 軸 -> 栓 -> 案内板 -> その留め（外装の縁）-> 外装
f_floor, f_plug, f_plate = mm(P.U_FLOOR_CLR), mm(P.HOLD_GAP), mm(P.PLATE_PLAY_Z)
chain_total = f_floor + f_plug + f_plate
add(SEC, "軸の浮きの鎖の合計（溝の底 0.05 + 栓 0.10 + 案内板の遊び 0.05。軸 -> 栓 -> 案内板 -> 外装の縁 -> 外装）", chain_total, 0.2, "max", unit="mm",
    note="案内板は外装へ直接留める（ベゼル経由にしない）。板の遊び 0.1 以下: 0.05")
add(SEC, "案内板の上下の遊び（外装の出っ張りの上面から縁の下端まで - 板の厚み）", f_plate, mm(P.PLATE_PLAY_Z_MAX), "max", unit="mm")
cd_sector = f_plug + f_plate + mm(P.HORN_CLR)                 # 中央軸が最大に浮き、受けが ホーンの隙間の分だけ下がったときの中心距離の増え（設計位置から）
cd_chain = math.sqrt((mm(P.PITCH) + 2 * mm(P.U_SLOT_Y_CLR)) ** 2 + chain_total ** 2) - mm(P.PITCH)   # 隣の軸が両側の壁へ寄り、高さも最大にずれたとき
add(SEC, "歯先の重なりの残り: 受け-中央軸（浮き + 案内板の遊び + 受けのホーンの遊び）", mm(P.GEAR_ADD) - cd_sector, 0.6, "min", unit="mm", note=f"中心距離の増え {cd_sector:.2f}")
add(SEC, "歯先の重なりの残り: 隣の軸どうし（Y に壁まで離れ、高さもずれる）", mm(P.GEAR_ADD) - cd_chain, 0.6, "min", unit="mm", note=f"中心距離の増え {cd_chain:.3f}")
rise = f_plug + f_plate - (-f_floor)                           # 溝の底に載った状態から栓・板まで上がる最大
mid = (f_plug + f_plate + (-f_floor)) / 2
add(SEC, "軸が浮いた分の画素の高さの変化（設計値を可動域の中央に置いたときの片側）", rise / 2, 0.1, "max", unit="mm", note=f"軸の中心は Zc-{f_floor:.2f}（溝の底）から Zc+{f_plug + f_plate:.2f} まで。全幅 {rise:.2f}。許容 ±0.1")
add(SEC, "軸の丸と U 溝の底の隙間（軸が載って中心が Zc からずれる量）", mm(P.U_FLOOR_CLR), 0.1, "max",
    note="歯車の中心距離は全軸いっしょにこれだけ縮む。0 だと軸が溝の底に擦る")
lift_worst = float(np.nanmax(gaps)) + mm(P.U_FLOOR_CLR)
add(SEC, "最大に浮いた軸の丸の下端と、U 溝の細い部分の上端（入口の面取り 0.6 の下）の差", (mm(P.PAD_TOP_ABOVE) - 0.6) - (-mm(P.JOURNAL_D) / 2 + lift_worst), 2.0, "min",
    note="壁が軸の Y 方向の動きを止める高さが、浮いても残る")
add(SEC, "受けが降りる経路: +X のパッドの帯の内面と受けの +X 面の X の隙間", mm(P.PAD_X0) - mm(P.RECV_X1), 0.5, "min",
    note="受けはホーンごとサーボと上から降りる。パッドの帯（Z 46.7..55.15）を通る。ピンは U 溝（Y ±3.4）を通る")

# ---------------------------------------------------------------------------------------------
# J. 部品の id
# ---------------------------------------------------------------------------------------------
SEC = "J 部品 id"
ids = P.PART_IDS
add_bool(SEC, "PART_IDS に重複が無い", len(ids) == len(set(ids)))
need = ["housing", "bezel", "guide_plate", "horn_coupler", "phase_comb", "sg92r", "sg92r_horn"]
need += [f"shaft_{j}" for j in range(5)] + [f"gear_{j}" for j in range(5)]
need += [f"cam_{i}_{j}" for i in range(5) for j in range(5)] + [f"pixel_{i}_{j}" for i in range(5) for j in range(5)]
add_bool(SEC, "親が決めた id がすべて入っている", all(n in ids for n in need), note=f"{len(ids)} 個。追加: {', '.join(P.EXTRA_PART_IDS)}")
add_bool(SEC, "LAYOUT の部材がすべて PART_IDS にある", all(n in ids for L in LAYOUT.values() for k, n, a, b in L["members"] if k in ("cam", "gear")))

# ---------------------------------------------------------------------------------------------
# 出力
# ---------------------------------------------------------------------------------------------
def fmt(v):
    if isinstance(v, bool):
        return str(v)
    return f"{v:.3f}" if isinstance(v, float) else str(v)


cur = None
n_fail = 0
for it in ITEMS:
    if it["section"] != cur:
        cur = it["section"]
        print(f"\n== {cur} ==")
    mark = "PASS" if it["pass"] else "FAIL"
    if not it["pass"]:
        n_fail += 1
    if it["kind"] == "info":
        print(f"INFO {it['name']}: {it['value']}")
    elif it["kind"] == "bool":
        print(f"{mark} {it['name']}" + (f"  [{it['note']}]" if it["note"] else ""))
    else:
        rel = ">=" if it["kind"] == "min" else "<="
        print(f"{mark} {it['name']}: {fmt(it['value'])} {it['unit']} (要 {rel} {fmt(it['limit'])}, 余裕 {it['margin']:+.3f})"
              + (f"  [{it['note']}]" if it["note"] else ""))

summary = {
    "n_items": len(ITEMS), "n_fail": n_fail,
    "key": {
        "cube_mm": mm(P.CUBE), "zc_mm": ZC, "zs_mm": ZS, "g": P.G_RATIO, "rb_mm": RB, "rmax_actual_mm": RMAX_ACT,
        "lateral_max_mm": lat_max, "kappa_B_035": kB35, "kappa_B_045": kB45, "kappa_A_035": kA35, "kappa_A_045": kA45,
        "torque_035_mNm": T35 * 1000, "torque_045_mNm": T45 * 1000, "phase_sum_deg": max(tot),
        "dwell_half_deg": P.DWELL_HALF_DEG, "hex_slack_if_ribs_fail_deg": hex_slack, "phase_margin_deg": P.DWELL_HALF_DEG - max(tot),
    },
}
os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
out = os.path.join(HERE, "build", "design_check.json")
tmp = out + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump({"summary": summary, "items": ITEMS, "layout_x": LAYOUT}, f, ensure_ascii=False, indent=1)
os.replace(tmp, out)
print(f"\n{len(ITEMS)} 項目、不合格 {n_fail}。保存: {out}")
sys.exit(1 if n_fail else 0)
