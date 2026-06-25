# CATEGORY: かわいいロボット
# horn — サーボホーン実測入力UI（mm）。入手後に測って上書き→確定の元にする。
#
# 使い方:
#   1) viewer で horn を開く（mm のスライダー/数値）
#   2) 実物ホーンを測って上書き → ライブプレビューが即更新
#   3) 形が合ったら確定 → その値を共通 servo_core.HORN に焼き込む
#      （→ round/square/servo-test のホーン受けが全部追従）
#
# まだ実物が無いので既定は仮置き（9g サーボ標準的なクロスホーン想定）。
# 穴・径は直径(⌀)で入力。

HORN_TYPE = 0       # 形状: 0=十字(cross) / 1=1腕(single) / 2=円盤(round)
ARM_SPAN = 19.0     # 腕の全長（端〜端・最長方向）
ARM_W = 4.2         # 腕の幅
HUB_DIA = 8.0       # 中央ハブ径 ⌀
THICKNESS = 3.5     # ホーン厚み（＝頭側の受け溝の深さ）
ROUND_DIA = 20.0    # 円盤径 ⌀（round タイプのとき）
SCREW_DIA = 2.6     # センタービス径 ⌀（頭天面の貫通穴）

# --- ブラウザUIからのパラメータ上書き ---
try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
