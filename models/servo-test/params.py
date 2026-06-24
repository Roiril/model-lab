# CATEGORY: かわいいロボット
# servo-test — 機構検証用の最小テスト治具（単位: m）
#
# 平板マウント（プレート）+ 回るキャップ の2パーツだけ。外皮なし。
# サーボ実寸は lib/servo_core.py の SERVO（既定 SG92R）を参照。
# 目的: socket フィット / フランジ着座 / ネジ穴 / スラストリング上の回転 / ホーン結合 の確認。

import math  # noqa: F401

# --- マウント平板（サーボ本体はこの下にぶら下がる）---
PLATE_W = 0.040     # 平板の幅（X）
PLATE_D = 0.026     # 平板の奥行き（Y）
PLATE_T = 0.006     # 平板の厚み（フランジ座 + ネジ受け）
PLATE_FILLET = 0.004  # 平板の角丸

# --- スラストリング（キャップが乗って回る）---
RING_OUTER = 0.012   # リング外半径
RING_T = 0.0015      # リング高さ
RING_WALL = 0.002    # リング肉厚

# --- 回るキャップ（カップ形。ホーンに結合）---
CAP_R = 0.013        # キャップ外半径
CAP_WALL = 0.002     # キャップ肉厚（スカート）
CAP_TOP_T = 0.006    # キャップ天面の厚み（ホーン溝3.5mmの上に余肉を残す）

# --- 回転が見えるポインタ ---
POINTER_L = 0.011    # ポインタ長さ
POINTER_W = 0.003    # ポインタ幅
POINTER_H = 0.002    # ポインタ高さ

# --- 表示 ---
SHOW_SERVO = 0        # サーボ実体ダミーを重ねる（1で表示・シミュレーション用）

# --- サーボ結合まわり（微調整用）---
SERVO_SCREWS = 0      # サーボ固定ねじ穴を開ける（1=開ける / 0=無ねじ・頭で挟む）
SERVO_CLR = 0.0004    # サーボはめ込みクリアランス
COUPLING_GAP = 0.002  # ホーン結合のすき間（サーボ突起の上）
CLEAR_R = 0.0080      # キャップ内部・軸逃げ半径

# --- ブラウザUIからのパラメータ上書き ---
try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
