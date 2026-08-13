# ロボットハンド用 手首回転機構（2自由度ジンバル）— 寸法・定数（単位: m）
#
# 座標系: Z=上（卓上）, Y=前, X=幅（左右）
# 自由度:
#   ロール  = Y軸まわり（前腕 旋前/旋後）          … 内側
#   ピッチ  = X軸まわり（屈曲/伸展, 水平→上 0..+90°）… 外側ヨーク
# 軸は1点 (0, PITCH_Y, AXIS_Z) で交差（ロール軸高さ = ピッチ軸高さ）。
# 駆動は両軸とも 608 直結・歯車なし（能動保持）。駆動IFは後付けモジュール。
#
# 「骨格（option A）」段階。中立姿勢（ピッチ0=ハンド前方水平）でモデル化。
# 仮値: フランジ穴/片持ち長/卓上固定/各軸ストッパー角度 → 確定後に詰める。

import math  # noqa: F401

# --- 608 ベアリング（深溝玉軸受 8x22x7）両軸共通 ---
BRG_OD = 0.022
BRG_ID = 0.008
BRG_W  = 0.007

# --- クリアランス ---
POCKET_CLEAR = 0.0001   # ベアリング座
SHAFT_CLEAR  = 0.0005   # リップ貫通穴のシャフト逃げ

# 座ぐり/リップ（両軸共通）
POCKET_R   = BRG_OD / 2 + POCKET_CLEAR
LIP_BORE_R = BRG_ID / 2 + SHAFT_CLEAR

# ============================================================
# 軸の交差点（ロール軸 = ピッチ軸 の高さ）
# ============================================================
AXIS_Z = 0.050        # 軸中心高さ（ピッチ+90°時に後端が卓上へ干渉しない高さ）

# ============================================================
# ロール機構（内側・Y軸）= キャリッジに載る
# ============================================================
SHAFT_R = BRG_ID / 2          # 4mm（608内輪に圧入想定）

# 前後2壁（ロール用 608 座、2点支持）
WALL_T = 0.010
WALL_X = 0.036
WALL_BACK_Y  = 0.020
SUPPORT_SPAN = 0.040
WALL_FRONT_Y = WALL_BACK_Y + SUPPORT_SPAN
WALL_TOP = AXIS_Z + POCKET_R + 0.007

# 片持ち / 後端
CANTILEVER = 0.030
REAR_OH    = 0.012

# ハンド取付フランジ（前端）※穴は仮の汎用パターン
FLANGE_R = 0.020
FLANGE_T = 0.004
FLANGE_PCD_R  = 0.012
FLANGE_HOLE_R = 0.0017
FLANGE_N_HOLE = 4

# 駆動IF（ロール後端・Dカット）
DCUT_FLAT = 0.0015
DCUT_LEN  = REAR_OH

# ロール派生 Y 座標
SHAFT_REAR_Y    = WALL_BACK_Y - WALL_T / 2 - REAR_OH
WALL_FRONT_FACE = WALL_FRONT_Y + WALL_T / 2
FLANGE_BACK_Y   = WALL_FRONT_FACE + CANTILEVER
FLANGE_FRONT_Y  = FLANGE_BACK_Y + FLANGE_T
SHAFT_FRONT_Y   = FLANGE_FRONT_Y
SHAFT_LEN       = SHAFT_FRONT_Y - SHAFT_REAR_Y

# ロール用ストッパーペグ（壁側当たりは角度確定後）
STOP_PEG_R   = 0.0025
STOP_PEG_LEN = 0.006
STOP_PCD_R   = 0.014

# ============================================================
# ピッチ機構（外側・X軸）= ヨーク + キャリッジ
# ============================================================
PITCH_Z = AXIS_Z                                   # ピッチ軸高さ = ロール軸高さ（交差）
PITCH_Y = (WALL_BACK_Y + WALL_FRONT_Y) / 2         # 0.040（2壁の中点に通す）

# キャリッジ（ロール機構を載せて傾く可動部）
CARRIAGE_HALF   = 0.022      # 側板外面 X（±22mm）
CARRIAGE_PLATE_Z0 = 0.012    # 底板 下面
CARRIAGE_PLATE_T  = 0.005
CARRIAGE_PLATE_TOP = CARRIAGE_PLATE_Z0 + CARRIAGE_PLATE_T   # 0.017（ロール壁の下端）
CPLATE_Y0 = 0.012
CPLATE_Y1 = 0.068
SIDE_PLATE_T  = 0.005        # 側板厚（X方向）
SIDE_PLATE_YW = 0.028        # 側板 Y幅
SIDE_PLATE_TOP = PITCH_Z + 0.008

PITCH_GAP = 0.0015           # キャリッジ側面 ↔ ポスト内面 の隙間
POST_T   = 0.010             # ポスト厚（X）
POST_INNER_X = CARRIAGE_HALF + PITCH_GAP          # 0.0235
POST_OUTER_X = POST_INNER_X + POST_T              # 0.0335

# ピッチ軸 = 別パーツの差し込みピン（外から 608 経由でキャリッジ側板へ圧入）
# → 固定された2ポスト間にキャリッジを置いてから左右からピンを挿せる（組立可能化）
STUB_PIN_R   = BRG_ID / 2                          # 4mm（608内輪に圧入）
HUB_BOSS_R   = 0.0065                              # 側板内側の座ボス半径（ピン把持を増す）
HUB_BOSS_LEN = 0.006                               # ボス長
STUB_PIN_IN  = CARRIAGE_HALF - SIDE_PLATE_T - HUB_BOSS_LEN   # ピン内端 X = 0.011（中心軸に達しない）
STUB_PIN_OUT = POST_OUTER_X                        # ピン外端 X（ポスト外面まで）
STUB_PIN_LEN = STUB_PIN_OUT - STUB_PIN_IN          # ピン長

# ヨーク（固定部）= ベース平板 + 左右2ポスト
BASE_T  = 0.005
BASE_X  = 0.090
BASE_Y  = 0.105
POST_TOP = PITCH_Z + POCKET_R + 0.007              # 0.068
POST_YW  = 0.028                                   # ポスト Y幅（PITCH_Y中心）

# 卓上固定（クランプ/ねじ）穴 = M4 ばか穴 ×4（四隅）→ 前方片持ちの転倒対策
MOUNT_HOLE_R = 0.0021
MOUNT_INSET  = 0.010

# ピッチ用ストッパー（0→+90°）※駆動方式確定後に当たり面を作り込む
