"""28mm パイプ用 90 度コーナー（手すり）の寸法定義。角で 2 つの M 字ジョイントの
内側レールどうし・外側レールどうしをつなぐ。

すべて mm。ローカル座標:
    内側円弧の中心が原点。曲がりは点 (0,R) から点 (R,0) へ回る
    両端に STRAIGHT の直線部。差し込み口はそれぞれ -X 側と -Y 側を向く
    Z=0 がパイプの芯の高さ

断面と印刷:
    内側は円から45度接線と平底へつなぐ。下面の角はR0.8。
    外側は55度の斜面と約20mm幅の平底。底の縁は45度で立ち上げる。
    本体は寝かせて刷る。先端の差し込み筒にも同じ高さの平底を設ける。
    握り部の上面は円弧を保つ。穴の天井は両側45度と約11.85mmの橋渡し。

角での置き方（2026-09-13 に決め直し。上面図は pipe-foot-corner の docstring）:
    2 つの M 字は平らな面を角へ向け、レールは平らな面を抜けて角へ出る。
    内側エルボ（R_INNER）の口は両方の M 字の平らな面に突き当たる。これが角の寸法の基準で、
    角の脚の軸から相手の軸線までの距離 CORNER_OFF = JOINT_END + R_INNER + STRAIGHT_INNER。
    外側はR_OUTER = R_INNER + 160の両端を保ち、中央を外へ18mm膨らませる。
    口は突き当てず REVEAL の目地を残す。
    内側を位置決めの突き当てにする。外側は見える隙間を0.8mmに抑え、同時突き当てを避ける。
    この余裕で吸収できる実物の印刷誤差は未検証。
    接続位置は維持する。端の肩を厚くし、外径35.6の差し込み筒を一体で延長する。

抜け止め:
    カーブの筒をM字の円形受けへ差し込む。追加部品は使わず、抜けをテープで止める。
    外側の筒は0.8mm長くし、目地を含めて内側と同じ7.3mmが受けに入る。

曲げの内側は半径 R_INNER - HUB_R。R=20 だと 1.7 で指を挟む溝になるので 25（6.7）にした。
"""
import importlib.util
import os


def _load(name, model):
    path = os.path.join(os.path.dirname(__file__), os.pardir, model, "params.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


J = _load("pipe_joint_params", "pipe-joint")

MM = 0.001

# --- パイプ ---
PIPE_OD = 28.0
CLEAR = 0.30
BORE_D = PIPE_OD + 2 * CLEAR       # 28.6

# --- 断面（U ターンと共通）---
WALL = 4.0
HUB_R = BORE_D / 2 + WALL          # 18.3 握り部の側面半径（幅36.6 = M字のスリーブと同径）
assert abs(HUB_R * 2 - J.HUB_D) < 1e-9, "M 字のスリーブと径が違う。突き当てで段が出る"

BOT_WALL = 3.0
Z_BASE = BORE_D / 2 + BOT_WALL     # 17.3 芯から底面までの深さ
EDGE_R = 0.8                     # 握りの底の稜線を丸める最小半径
OUTER_BOTTOM_SLOPE = 55.0        # 外側カーブ下面の斜面。水平から55度
OUTER_BED_INSET = 0.3            # 平底の縁を内側へ0.3mm寄せ、45度で立ち上げる

BORE_ROOF_TOP = BORE_D / 2           # 14.3。円柱の外形とパイプ通路を保つ
BORE_ROOF_HALF = BORE_D / 2 * 2**0.5 - BORE_ROOF_TOP  # 約5.92。側面は45度
BORE_MOUTH_L = 12.0                # 差し込み口で屋根を円へ戻す長さ

# --- 芯線 ---
SPAN = 2 * J.SIDE_Y                # 160.0 内側レールと外側レールの間隔
R_INNER = 25.0                     # 内側レール。曲げの内側の半径 = 25 - 18.3 = 6.7
R_OUTER = R_INNER + SPAN           # 185.0 外側の両端位置。中央は円弧より膨らませる
OUTER_BULGE = 18.0                # 外側の中央を円弧より18mm外へ出す
OUTER_HANDLE = 0.30               # 5次曲線の端側制御点 / R_OUTER
STRAIGHT_INNER = 30.0              # 内側の直線部 = 差し込み深さ。口は M 字の面に突き当たる
REVEAL = 0.8                       # 外側の口と M 字の面のあいだに残す目地
STRAIGHT_OUTER = STRAIGHT_INNER - REVEAL   # 29.2

JOINT_END = J.LEG_X - J.X_BOT      # 19.7 M 字の本体が脚の軸から平らな面まで出る量
CORNER_OFF = JOINT_END + R_INNER + STRAIGHT_INNER   # 74.7 角の脚の軸 → 相手の軸線
ARC_CENTER_OFF = CORNER_OFF - R_INNER               # 49.7 同心の中心（角の節点から両軸へ）

assert STRAIGHT_OUTER >= 1.0 * PIPE_OD, "外側の差し込みがパイプ径より浅い"

# --- メッシュ品質 ---
STR_SEG = 28                       # 直線部の分割数
PROF_SEG = 48                      # 断面の上半円の分割数
ARC_SEG_MIN = 48                   # 90 度あたりの最小分割数
