# CATEGORY: かわいいロボット
# round-bot — まるっぽい1サーボ・キャラ（パン）寸法・定数（単位: m）
#
# 機構は lib/servo_core.py に集約（SG90 縦置き・軸上向き・パン）。
# ここは「外皮（まるっぽい胴＋ドーム頭＋点目）」と調整スライダーだけ。
# 数値はすべてメートル。コメント `# ラベル` がブラウザUIのスライダー名になる。

import math  # noqa: F401  （model 側で使う）

# --- 全体サイズ ---
BODY_R = 0.024    # 胴の半径
BODY_H = 0.044    # 胴の高さ
HEAD_R = 0.024    # 頭（ドーム）の半径
WALL = 0.002      # 胴の肉厚
DECK_T = 0.003    # デッキ厚（サーボを受ける天板）

# --- 目（前面 +Y のくぼみ）---
EYE_R = 0.0032    # 目の大きさ（半径）
EYE_DX = 0.009    # 目の左右間隔（中心から）
EYE_H = 0.013     # 目の高さ（接合面から）

# --- サーボ結合まわり（高さはサーボ実寸から自動計算。ここは微調整用）---
SERVO_SCREWS = 0      # サーボ固定ねじ穴を開ける（1=開ける / 0=無ねじ・頭で挟む）
SERVO_CLR = 0.0004    # サーボはめ込みクリアランス
COUPLING_GAP = 0.002  # ホーン結合のすき間（サーボ突起の上にどれだけ空けるか）

# --- ブラウザUIからのパラメータ上書き（server.js が JSON を渡す）---
try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
