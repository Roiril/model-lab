# Pixel 7a 固定スタンド（レンズだけ露出）— 寸法・定数（単位: m）
import math

# --- Pixel 7a 実寸（Google 公式スペック） ---
PHONE_L    = 0.1520   # 152.0mm 長辺
PHONE_W    = 0.0729   # 72.9mm 短辺
PHONE_T    = 0.0090   # 9.0mm 厚み（カメラバー部を除く）
PHONE_BUMP = 0.0011   # カメラバーの出っ張り 1.1mm（窓から外へ逃がす）

# --- クリアランス（片側） ---
CLR_L = 0.0005   # 長辺方向 0.5mm
CLR_W = 0.0004   # 短辺方向 0.4mm（ずれない側の詰め）
CLR_T = 0.0006   # 厚み方向 0.6mm

# --- スロット内寸 ---
SLOT_L = PHONE_L + 2 * CLR_L   # 153.0mm 長辺方向（X）
SLOT_W = PHONE_W + 2 * CLR_W   #  73.7mm 短辺方向（斜面に沿う）
SLOT_T = PHONE_T + CLR_T       #   9.6mm 厚み方向（斜面の法線）

# --- 肉厚 ---
FRONT_SKIN = 0.0025   # 2.5mm 斜面の外皮（この裏にスマホ背面が接する）
BACK_PLATE = 0.0030   # 3.0mm スロット裏板（画面側）
SIDE_WALL  = 0.0035   # 3.5mm 側壁
WALL_Y     = 0.0030   # 3.0mm 前壁・背面壁
STOPPER    = 0.0035   # 3.5mm スロット下端の受け（ここでスマホが止まる）
RIB_W      = 0.0080   # 8.0mm 底面中央に残すリブ

# --- 姿勢・外形 ---
TILT_DEG   = 45.0
FRONT_H    = 0.0080   # 8.0mm 前壁の立ち上がり
TOP_FLAT   = 0.0160   # 16.0mm 天面（ここにスロットの差し込み口が開く）
SLOPE_LEN  = STOPPER + SLOT_W + 0.0008   # 78.0mm 斜面の長さ
SLOT_ENTRY = 0.0600   # 差し込み口を抜くためのカッター延長

STAND_W = SLOT_L + 2 * SIDE_WALL                         # 160.0mm
RUN     = SLOPE_LEN * math.cos(math.radians(TILT_DEG))   #  55.2mm 斜面の水平投影
STAND_D = RUN + TOP_FLAT                                 #  71.2mm
STAND_H = FRONT_H + RUN                                  #  63.2mm

# --- カメラ窓（外皮を貫通。カメラバーはここから外へ出る） ---
CAM_EDGE_RIM = 0.0040   # 4.0mm スマホ上端側に残す外皮リム
CAM_WIN_L    = 0.0340   # 34.0mm 窓の長さ（端末上端から 4〜38mm を覆う）
WIN_S_MIN    = 0.0030
WIN_S_MAX    = SLOPE_LEN   # 斜面の上端まで開く（差し込み口と繋がり、カメラバーが引っかからない）
WIN_S_LEN    = WIN_S_MAX - WIN_S_MIN
WIN_S_CENTER = (WIN_S_MIN + WIN_S_MAX) / 2

# --- 指穴（裏板を貫通。ここを押してスマホを抜く） ---
FINGER_R     = 0.0130   # φ26mm
FINGER_X     = 0.0350   # 中心から ±35mm
FINGER_S     = STOPPER + SLOT_W / 2
FINGER_DEPTH = 0.0140

# --- USB-C / スピーカーの逃げ（スマホ下端側の側壁を切り欠く） ---
USB_W = 0.0200   # 20.0mm
USB_S = STOPPER + SLOT_W / 2
