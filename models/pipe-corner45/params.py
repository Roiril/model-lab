# 28mm パイプの入隅（縦柱＋水平レール）に付ける Pixel 7a ホルダー — 単位: m
#
# 向きは Blender に置かれた板（Cube.005、回転 0/45/45）から取った。
# 板の厚み方向＝カメラの視線は (0.5, 0.5, -0.707)。水平から 45° 下で、平面でも 45° 振れる。
# つまり壁の入隅版（pixel7a-corner45）と同じ「振り 45°＋俯角 45°」。
#
# 座標系（原点＝2 本の軸の交点。以下すべて原点から測る）:
#   x … 外向き   y … 水平レールに沿って奥   z … 上（縦柱は z<0 側へ伸びる）
#   h … カメラの視線 (cosδcosψ, cosδsinψ, -sinδ)
#   s … スロットを上る向き (sinδcosψ, sinδsinψ, cosδ)。差し込み口は上
#   L … スマホの長辺 (-sinψ, cosψ, 0)
import math

# --- パイプ（イレクター相当。models/pipe-* と同じ値） ---
PIPE_OD    = 0.0280
PIPE_CLEAR = 0.0003
BORE_D     = PIPE_OD + 2 * PIPE_CLEAR      # 28.6mm
POST_EXTRA = 0.0004   # 縦柱のボアだけ広げる（2 本を同時に掴むので直角の誤差を逃がす）

# --- 継手（未計測。測ったらこの 4 つだけ直す） -------------------------------
JOINT_R    = 0.0300   # 30.0mm 継手の外半径
JOINT_RAIL = 0.0450   # 45.0mm 角からレールに沿って張り出す長さ
JOINT_POST = 0.0450   # 45.0mm 角から縦柱に沿って張り出す長さ
JOINT_GAP  = 0.0040   # 4.0mm  継手との隙間

# --- 姿勢（板の回転から確定） ---
CAM_DEPRESSION = 45.0   # δ 俯角
YAW_DEG        = 45.0   # ψ 平面での振り（+x から +y へ）

# --- スマホ中心の位置（原点から h / s / L 方向に測る） ---
# 板の中心はこの座標で (170.1, 65.0, 13.6)。ただし板は 200x100x20mm で実機
# (152x72.9x9) より大きい置き代わりなので、H だけ詰めて腕を短くしてある。
# レール軸からの距離はビルド時に印字する。押し出したいときは H_PH を増やす。
H_PH = 0.1050   # 105.0mm 視線方向（大きくすると前へ出る＝腕が長くなる）
S_PH = 0.0650   # 65.0mm  スロープ方向（大きくすると上へ）
L_PH = 0.0140   # 14.0mm  長辺方向（レールの奥側へずらす量）

# --- 割りリング（レール用・柱用で同じ寸法。帯は 1 種類で兼用） ---
RING_W    = 0.0240
RING_WALL = 0.0040
RING_R    = BORE_D / 2 + RING_WALL     # 18.3mm
CLAMP_GAP = 0.0013                     # 割りの片側の隙間（0 だと締まらない）
STRAP_ARC = 0.0035                     # 帯の肉厚（本体より薄くして先に馴染ませる）

# --- 耳とねじ（M4） ---
EAR_T   = 0.0090
EAR_R   = 0.0250
EAR_W   = 0.0150
SCREW_D = 0.0043
NUT_AF  = 0.0074
NUT_T   = 0.0035
NUT_SLOT_W = 0.0074

# --- 腕（リングとポケットを渡す板） ---
WEB_T    = 0.0100   # 10.0mm 厚み
WEB_BITE = 0.0020   # 2.0mm ポケットへ食い込ませる量（裏板 3mm を超えるとスロットに穴が開く）
WEB_Y    = 0.0400   # 40.0mm レール腕の軸方向の幅
WEB_Z    = 0.0400   # 40.0mm 柱腕の軸方向の幅

TETHER_D = 0.0045   # テザー穴

# =========================================================================
# ここから下は据置版・壁掛け版と同じ実績寸法。触らない。
# =========================================================================
PHONE_L    = 0.1520
PHONE_W    = 0.0729
PHONE_T    = 0.0090
PHONE_BUMP = 0.0011

CLR_L = 0.0007
CLR_W = 0.0007
CLR_T = 0.0008

SLOT_L = PHONE_L + 2 * CLR_L   # 153.4mm
SLOT_W = PHONE_W + 2 * CLR_W   #  74.3mm
SLOT_T = PHONE_T + CLR_T       #   9.8mm

FRONT_SKIN = 0.0025
BACK_PLATE = 0.0030
SIDE_WALL  = 0.0035
STOPPER    = 0.0035

SHELL_TOTAL = FRONT_SKIN + SLOT_T + BACK_PLATE   # 15.3mm
SLOPE_LEN   = STOPPER + SLOT_W + 0.0008          # 78.6mm
SLOT_ENTRY  = 0.0600
MOUNT_W     = SLOT_L + 2 * SIDE_WALL             # 160.4mm

CAM_EDGE_RIM = 0.0040
CAM_WIN_L    = 0.0340
WIN_S_MIN    = 0.0030
WIN_S_MAX    = SLOPE_LEN + 0.0040
WIN_S_LEN    = WIN_S_MAX - WIN_S_MIN
WIN_S_CENTER = (WIN_S_MIN + WIN_S_MAX) / 2

TAPER_S0  = 0.0665
TAPER_LEN = 0.0140
TAPER_D   = 0.0012
TAPER_CUT = 0.0040

GRIP_W  = 0.0460
GRIP_S0 = 0.0635

USB_W = 0.0200
USB_T = 0.0170
USB_INTO = 0.0015
USB_S = STOPPER + SLOT_W / 2

LATCH_H = 0.0008
LATCH_L = 0.0120
LATCH_X = 0.0300
LATCH_S = 0.0040
