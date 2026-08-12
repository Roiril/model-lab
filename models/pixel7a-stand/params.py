# Pixel 7a 固定スタンド（レンズだけ露出）— 寸法・定数（単位: m）
import math

# --- Pixel 7a 実寸（Google 公式スペック） ---
PHONE_L    = 0.1520   # 152.0mm 長辺
PHONE_W    = 0.0729   # 72.9mm 短辺
PHONE_T    = 0.0090   # 9.0mm 厚み（カメラバー部を除く）
PHONE_BUMP = 0.0011   # カメラバーの出っ張り 1.1mm（窓から外へ逃がす）

# --- クリアランス（片側） ---
# 初版（長辺 0.5 / 厚み 0.4 + リブ）は実機で入らなかったので広げた。
# FDM の内寸は 0.2〜0.3mm 縮むため、リブ込みの実効値で 0.5mm 以上を残す。
CLR_L = 0.0007   # 長辺方向 0.7mm（側壁リブ込みの実効 0.45mm）
CLR_W = 0.0007   # 短辺方向 0.7mm
CLR_T = 0.0008   # 厚み方向 0.8mm（保持リブ込みの実効 0.6mm）

# --- スロット内寸 ---
SLOT_L = PHONE_L + 2 * CLR_L   # 153.0mm 長辺方向（X）
SLOT_W = PHONE_W + 2 * CLR_W   #  73.7mm 短辺方向（斜面に沿う）
SLOT_T = PHONE_T + CLR_T       #   9.4mm 厚み方向（斜面の法線）

# --- 肉厚 ---
FRONT_SKIN = 0.0025   # 2.5mm 斜面の外皮（この裏にスマホ背面が接する）
BACK_PLATE = 0.0030   # 3.0mm スロット裏板（画面側）
SIDE_WALL  = 0.0035   # 3.5mm 側壁
WALL_Y     = 0.0030   # 3.0mm 前壁・背面壁
BOTTOM_T   = 0.0025   # 2.5mm 底板（接地面を全面にして first layer を安定させる）
STOPPER    = 0.0035   # 3.5mm スロット下端の受け（ここでスマホが止まる）

# --- 姿勢・外形 ---
TILT_DEG   = 75.0
FRONT_H    = 0.0080   # 8.0mm 前壁の立ち上がり
TOP_FLAT   = 0.0300   # 30.0mm 天面（差し込み口が開く。75°は背が高いので奥行きで転倒を抑える）
SLOPE_LEN  = STOPPER + SLOT_W + 0.0008   # 78.0mm 斜面の長さ
SLOT_ENTRY = 0.0600   # 差し込み口を抜くためのカッター延長

STAND_W = SLOT_L + 2 * SIDE_WALL                         # 160.4mm
RUN     = SLOPE_LEN * math.cos(math.radians(TILT_DEG))   #  20.3mm 斜面の水平投影
RISE    = SLOPE_LEN * math.sin(math.radians(TILT_DEG))   #  75.9mm 斜面の立ち上がり
STAND_D = RUN + TOP_FLAT                                 #  50.3mm
STAND_H = FRONT_H + RISE                                 #  83.9mm

# --- カメラ窓（外皮を貫通。カメラバーはここから外へ出る） ---
CAM_EDGE_RIM = 0.0040   # 4.0mm スマホ上端側に残す外皮リム
CAM_WIN_L    = 0.0340   # 34.0mm 窓の長さ（端末上端から 4〜38mm を覆う）
WIN_S_MIN    = 0.0030
WIN_S_MAX    = SLOPE_LEN + 0.0040   # 天面との間の楔まで抜く（窓の上に橋を架けない）
WIN_S_LEN    = WIN_S_MAX - WIN_S_MIN
WIN_S_CENTER = (WIN_S_MIN + WIN_S_MAX) / 2

# --- 差し込み口のテーパー（外皮側だけ広げて導入する） ---
TAPER_S0  = 0.0660   # ここから上を広げ始める（指がかりと保持リブの端に重ねない）
TAPER_LEN = 0.0140
TAPER_D   = 0.0012   # 入口で 1.2mm 外へ逃がす（入口の厚み 10.6mm・外皮は 1.3mm 残る）

# --- 指がかり（スマホの上端を表裏から摘まむ切り欠き） ---
GRIP_W  = 0.0460   # 46.0mm 幅（中央）
GRIP_S0 = 0.0630   # ここから斜面の上端まで外皮と裏板を落とす

# --- 保持リブ（カタカタ止め） ---
RIB_EMBED   = 0.0005    # 0.5mm 母材へ埋める量（coplanar 回避）
RIB_H       = 0.0002    # 0.2mm 裏板から突き出す量（緩ければここを上げる）
RIB_S       = 0.0600    # s=60mm に 1 本。スマホ上部を外皮側へ押して 3 点で支える
RIB_BW      = 0.0040    # 4.0mm 幅（斜面方向）
RIB_SIDE_GAP = 0.0030   # リブの端面を側壁から離す（coplanar を避ける）
SIDE_RIB_H  = 0.00025   # 0.25mm 側壁から突き出す量（長辺方向のガタ止め）
SIDE_RIB_S0 = 0.0060
SIDE_RIB_S1 = 0.0740

# --- USB-C / スピーカーの逃げ（スマホ下端側の側壁を切り欠く） ---
USB_W = 0.0200   # 20.0mm
USB_S = STOPPER + SLOT_W / 2
