"""SG92R 1 サーボで天面が開く 70mm 立方体。単位: m（コメントに mm を併記）。

座標: X = 左右（蝶番の軸方向）、Y = 前(+)/後(-)、Z = 上。立方体は x,y ∈ [-35, 35]mm、z ∈ [0, 70]mm。
前側の天面はY=-13mm・Z=65mmの蝶番で開く。サーボは左の壁ぎわに寝かせ、出力軸は +X を向く。
サーボの寸法は models/sg92r-photo/ の候補プロファイルから読む。ここには書き写さない。
"""
# CATEGORY: ケースと展示

import importlib.util as _ilu
import os as _os

_base_spec = _ilu.spec_from_file_location(
    "sg92r_photo_params",
    _os.path.join(_os.path.dirname(__file__), "..", "sg92r-photo", "params.py"),
)
_base_sg = _ilu.module_from_spec(_base_spec)
_base_spec.loader.exec_module(_base_sg)
_profiles_spec = _ilu.spec_from_file_location(
    "sg92r_photo_profiles",
    _os.path.join(_os.path.dirname(__file__), "..", "sg92r-photo", "profiles.py"),
)
_profiles = _ilu.module_from_spec(_profiles_spec)
_profiles_spec.loader.exec_module(_profiles)

# ユーザーの寸法図を採ったC2試作候補。実物SG92Rとの一致はservo_fit_testで未確認。
SG = _profiles.load_profile("c2-drawing-trial", _base_sg)
SERVO_DIMENSION_PROFILE = _profiles.profile_record(SG)

# --- 外形 -------------------------------------------------------------
CUBE = 0.070
WALL = 0.003            # 側壁の厚み（3mm）
FLOOR = 0.003           # 底の厚み（3mm）
LID_T = 0.003           # 蓋板の厚み（3mm）
EDGE_R = 0.005          # 外形の稜の丸み（5mm）

# --- 蝶番（分割天面の間）----------------------------------------------
HINGE_Y = -0.013               # 分割天面の蝶番軸Y（-13mm）
HINGE_Z = CUBE - EDGE_R         # 蝶番軸Z（65mm）
BOX_KNUCKLE_X = 0.017
KNUCKLE_GAP = 0.0004            # 節どうしの隙間（0.4mm）
HINGE_PIN_D = 0.005             # 蝶番ピン径（5mm）
HINGE_HOLE_LID_D = 0.0054       # 蓋の節の穴（5.4mm、回る）
HINGE_HOLE_BOX_D = 0.0052       # 左の節の貫通穴（5.2mm、割った先端が締まる）
HINGE_HOLE_THRU_D = 0.0056      # 右の節の通し穴（5.6mm、先端が素通りする）
HINGE_PIN_FLAT = 0.0005         # 寝かせて刷るための平面の削り量（0.5mm）
HINGE_LEFT_END_X = -0.035       # 左端の外形位置（-35mm）
HINGE_PIN_END_GAP = 0.00005     # ピン端と外形の隙間（0.05mm）
HINGE_SPLIT_L = 0.008           # ピン先の割りの長さ（8mm）
HINGE_SPLIT_W = 0.0010          # 割りの幅（1mm）
HINGE_TIP_D = 0.0053            # 割った先端の径（5.3mm、止まり穴 5.2 に締まる）
HINGE_TIP_L = 0.0070            # 太い先端の長さ（7mm）
HINGE_SWEEP_R = 0.0058          # 蓋の節が回る範囲として箱から削る半径（5.8mm）
TEARDROP_CAP = 0.0005           # 横穴の天井を平らに切るまでの余分（0.5mm）
BACK_LIP = 0.0010               # 蓋の節の下で、後ろの壁の上端を平らに残す幅（1mm）

# --- 蓋 ---------------------------------------------------------------
LID_SKIRT_T = 0.0016            # 蓋の裏の縁（スカート）の厚み（1.6mm）
LID_SKIRT_H = 0.003             # スカートの深さ（3mm）
LID_SKIRT_CLR = 0.0004          # スカートと壁の内面の隙間（0.4mm）
LID_SKIRT_BACK_Y = -0.007
LID_EDGE_V = 0.0010             # 箱の節の横で、蓋の天面の縁を垂直に立てる高さ（1mm）
LID_OPEN_DEG = 65.0

# --- サーボの置き方 ----------------------------------------------------
SERVO_X0 = -0.0315
SHAFT_Y = 0.0090                # 出力軸 O の Y（9mm）。配線を蝶番支持から離す
SHAFT_Z = 0.0306
SERVO_PSI_DEG = 180.0           # 本体の長手（軸側の端=配線側）が向く角度。180° = 後ろ(-Y)

# --- 4 節リンク --------------------------------------------------------
CRANK_A = 0.0246                # 軸 O からピン A まで（24.6mm）
CRANK_ALPHA_CLOSED_DEG = 222.6  # 閉じたときのクランク角（YZ 面、+Y から +Z へ）
B_REL_Y = 0.0147                # 閉じた蓋でのピン B の位置（蝶番軸からの Y、14.7mm）
B_REL_Z = -0.0123               # 同 Z（-12.3mm）

# 層（X 方向の重なり）。リンクとクランクと蓋の耳は別の層を動く
AX_GAP = 0.0003                 # 層どうしの隙間（0.3mm）
CRANK_TOP_T = 0.0025            # ホーンの上に載るクランクの肉（2.5mm）
LINK_T = 0.003                  # リンクの厚み（3mm）。端の丸を除いた長さでも曲げひずみ2%以下
FIN_T = 0.003                   # 蓋の耳の厚み（3mm）

# --- クランク（ホーンを包む）--------------------------------------------
HORN_CLR = 0.00015              # ホーンの外形との隙間（片側 0.15mm）
HORN_POCKET_EXTRA = 0.0001      # ホーンの腕厚に足すポケットの深さ（0.1mm）
CRANK_ARM_HW = 0.0050           # 長腕を包む幅の半分（5mm）
CRANK_PIN_BOSS_R = 0.0038       # ピンA側は半径3.8mmへ細め、組立中に曲がるリンクを逃がす
CRANK_LINK_RELIEF = 0.00035     # 曲げたリンクの実形状が通る上面の逃げ（0.35mm）
CRANK_SHORT_HW = 0.0036         # 短腕を包む幅の半分（3.6mm）
CRANK_SHORT_L = 0.0101          # 短腕を包む長さ（中心から 10.1mm）
CRANK_HUB_R = 0.0060            # 中心の丸（6mm）
STUB_R = 0.0030                 # 受けに入る軸（半径 3mm）
PIN_R = 0.0025                  # ピン A / B の半径（直径 5mm）
PIN_HOLE_R = 0.00270            # ピン穴の半径（直径5.4mm、片側0.2mm）
TAB_W = 0.0020                  # バヨネットの爪の幅（2mm）
TAB_R = 0.0041                  # 爪の先端までの半径（4.1mm）
TAB_T = 0.0040                  # 爪の軸方向の厚み（4mm、先端の肉1.7mm）
KEYWAY_W = 0.0024               # リンクの鍵溝の幅（2.4mm）
KEYWAY_R = 0.0044               # 鍵溝の深さ（中心から 4.4mm）
BAYONET_KEY_DEG = 75.0          # 爪が抜ける リンク−クランク の相対角（動作範囲の反対側）
B_TAB_W = 0.0020                # ピンBの爪の幅（2mm）
B_TAB_R = 0.0041                # ピンBの爪の先端までの半径（4.1mm）
B_TAB_T = 0.0040                # ピンBの爪の軸方向の厚み（4mm）
B_KEYWAY_W = 0.0024             # 蓋の耳に設ける鍵溝の幅（2.4mm）
B_KEYWAY_R = 0.0044             # 蓋の耳に設ける鍵溝の深さ（中心から4.4mm）
B_KEY_DEG = -55.0               # 蓋ローカル+Y基準。動作域から50°以上離し、リンクを板の前側へ通す

# --- リンク -------------------------------------------------------------
LINK_HW = 0.0040                # リンクの幅の半分（4mm）
LINK_A_BOSS_R = 0.0060          # A 端の丸（6mm、鍵溝の外に 1.6mm）
LINK_B_BOSS_R = 0.0050          # B 端の丸（5mm）
LINK_PIN_CHAMFER = 0.0005       # ピン B 先端の面取り（0.5mm）

# --- 蓋の耳 -------------------------------------------------------------
FIN_B_BOSS_R = 0.0060           # ピンBまわりの丸（6mm、鍵溝の外に1.6mm）
FIN_ROOT_Y = HINGE_Y + 0.023    # C1と同じ蝶番から23mm先（Y=10mm）。腕を天面までつなぐ
FIN_BACK_Y = -0.0316

# --- 受け（クランクの軸を下から受け、+X への抜けを止める）-----------------
U_IN_R = 0.0033                 # U 溝の半径（3.3mm）
U_OUT_R = 0.0065                # U の外半径（6.5mm）
U_PRONG_H = 0.0035              # U の爪が軸より上に出る高さ（3.5mm）
U_COL_X1 = 0.019
U_COL_HW = 0.0065               # 柱の幅の半分（6.5mm）

# --- サーボの台 -----------------------------------------------------------
SERVO_CLR = 0.00035             # 上から挿入する横方向だけの隙間（片側0.35mm）
SERVO_FAR_END_GAP = 0.00035     # 軸から遠い本体端の逃げ（0.35mm）
SERVO_DATUM_AXIS_TOL = 0.00010  # 寸法図と実物の差で許す軸位置誤差（0.10mm、試片で要確認）
PED_X1 = -0.0105
PED_Y0 = -0.0047                # 台の後端（-4.7mm）
PED_Y1 = 0.0290                 # 台の前端（29mm）。クリップの外側を内壁から離す
EAR_FENCE_T = 0.0016            # 取付耳を挟む柵の厚み（1.6mm）
EAR_FENCE_TOP = 0.0060          # 柵が台の上に出る高さ（6mm）
END_WALL_T = 0.0020             # 本体の両端を止める壁（2mm）
END_WALL_X1 = -0.0160
END_WALL_ABOVE = -0.0015        # 端の壁の上端（本体の上面より 1.5mm 下。クリップの梁を通す）
WIRE_SLOT_X0 = -0.0295
WIRE_SLOT_X1 = -0.0235
WIRE_SLOT_BOTTOM = 0.0020       # 切り欠きの底（軸の高さより 2mm 下）

# --- サーボ押さえ（コの字のクリップ）-----------------------------------------
CLIP_X0 = -0.0230
CLIP_X1 = -0.0165
CLIP_BRIDGE_T = 0.0030          # 上の梁の厚み（3mm）
CLIP_LEG_T = 0.0025             # 脚の厚み（2.5mm）
CLIP_TOP_GAP = 0.0002           # 梁と本体上面の隙間（0.2mm）
CLIP_SIDE_GAP = 0.0003          # 脚と台の端面の隙間（0.3mm）
HOOK_D = 0.0015                 # 爪のかかり（1.5mm）
HOOK_H = 0.0020                 # 爪の高さ（2mm）
HOOK_Z = 0.0180
NOTCH_H = 0.0030                # 台の受け溝の高さ（3mm）
SERVO_SPRING_T = 0.0012         # 長手押さえの厚み（1.2mm）
SERVO_SPRING_INTENT = 0.00012   # 遠い端への公称押込み（0.12mm）
SERVO_SPRING_TIP_ABOVE_SEAT = 0.0020  # 押さえ先端の下端（座面から2mm）
SERVO_SPRING_TIP_H = 0.0012     # 先端の案内斜面の高さ（1.2mm）

# --- 配線の出口（後ろの壁の下端）------------------------------------------
WIRE_EXIT_X0 = -0.0300
WIRE_EXIT_X1 = -0.0220
WIRE_EXIT_H = 0.0040            # 高さ 4mm

# --- 物理量 --------------------------------------------------------------
PLA_DENSITY = 1240.0            # kg/m3（中実で見積もる。実物はこれより軽い）
SERVO_STALL_TORQUE = 0.245      # N·m（2.5 kgf·cm @4.8V、SG92R 公称）
SERVO_SPEED = 0.10              # s/60°（@4.8V、SG92R 公称）

try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass

# エキサイターは B3 の包絡寸法。製品型番と接触面は未確定。
EXCITER_D = 0.025  # 25mm
EXCITER_H = 0.010  # 10mm
EXCITER_CENTER_Y = 0.016  # 16mm
EXCITER_CENTER_Z = 0.020  # 20mm
EXCITER_CLR = 0.0003  # 片側0.3mm
EXCITER_PRELOAD = 0.0001  # 0.1mm。実物の接触面に合わせる仮値
EXCITER_CLIP_T = 0.003  # 3mm
OPEN_TIME_S = 1.2  # 1.2秒
ASSEMBLY_LID_BACK_DEG = 75.0   # B→Aの順に接合した一式を、蓋75°で箱へ下ろす
MODEL_ID = "mystery-box-sg92r-c2"

# 固定天面は別部品として裏返しで刷る。内へ伸びた解除つまみを左右から押して外す。
ROOF_GAP = 0.0004  # 0.4mm
ROOF_FRONT_Y = -0.0188  # -18.8mm。回転逃げの切り口にも2mmの肉を残す
ROOF_LEG_T = 0.002  # 2mm
ROOF_LEG_X = 0.030  # 脚の外面 X=±30mm
ROOF_LEG_Y0 = -0.024  # -24mm
ROOF_LEG_Y1 = -0.020  # -20mm。脚の根元を天面へ全面でつなぐ
ROOF_LEG_BOTTOM = 0.043  # 43mm
ROOF_HOOK = 0.0028  # 脚外面30mmから32.8mmまで。内壁へ0.8mm掛かる
ROOF_HOOK_H = 0.0048  # 4.8mm。爪先を2mm厚にし、45°の案内斜面を残す
ROOF_PRESS_DELTA = 0.00112  # 1.12mm。爪全体を内壁から0.3mm以上逃がす
ROOF_RELEASE_X = 0.018  # 解除つまみの内面 X=±18mm
ROOF_RELEASE_T = 0.002  # つまみの厚み2mm
ROOF_RELEASE_BOTTOM = 0.039  # つまみの下端39mm
ROOF_RELEASE_FOOT_Z = 0.041  # 解除腕の下面41mm
ROOF_RELEASE_TOP_Z = 0.051  # 45°の支えの上端51mm。曲がる脚の自由長16mm
