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

# SG92R 付属クロスホーン（白石実測）。横35×たて17の非対称クロス。
HORN_TYPE = 0       # 形状: 0=十字(cross) / 1=1腕(single) / 2=円盤(round)
ARM_SPAN_X = 35.0   # 長腕の全長（端〜端）横
ARM_SPAN_Y = 17.0   # 短腕の全長（端〜端）たて
ARM_W = 4.0         # 腕の幅
HUB_DIA = 7.0       # 中央ハブ径 ⌀
THICKNESS = 2.0     # 腕板の厚み（＝頭側の受け溝の深さ）
STACK_H = 5.6       # ギアカバー上面〜ホーン頂部（小円柱+ホーン）
ROUND_DIA = 20.0    # 円盤径 ⌀（round タイプのとき）
SCREW_DIA = 2.4     # センタービス径 ⌀（自タッピング）

# --- ブラウザUIからのパラメータ上書き ---
try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
