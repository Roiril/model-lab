# CATEGORY: かわいいロボット
# sg92r — SG92R 実寸入力UI（ノギスで測って上書き → 最終確定の元にする）
#
# ★この params は「mm 単位」で書く（UIでもmmで入力）。m への変換は model.py が行う。
#
# 使い方:
#   1) viewer で sg92r を開く（各寸法が mm のスライダー/数値で出る）
#   2) 実物をノギスで測って、数値を上書き → 「STL 生成」でダミーが即更新
#   3) 形が実物と合ったら確定 → その値を共通プロファイル servo_core.SG92R に焼き込む
#      （→ マウント・治具・キャラ全部が追従する）
#
# 既定値の出どころ:
#   公式寸法図 A–F（TowerPro）の値を採用済み。
#   ★ = 公式図に数値が無く 9g 標準値で仮置き → 要実測。
# 穴・軸は直径(⌀)で入力（測りやすいので）。

# --- 本体（白石の実測値 2026-06-24）---
BODY_L = 22.0            # 本体長（軸オフセット方向 = X）
BODY_W = 12.3            # 本体幅（Y）
BODY_H = 22.3            # 本体高（底〜ケース上面・軸除く）
FLANGE_L = 32.2          # 羽根全長（タブ先端〜先端 = X）
SCREW_SPACING = 28.84    # ネジ穴ピッチ中心間（X）
FLANGE_FROM_BOTTOM = 16.0  # 本体底〜羽根下面

FLANGE_W = 12.3          # 羽根の幅（Y）
FLANGE_T = 2.2           # 羽根の厚み
SHAFT_OFFSET = 5.0       # 軸の中心ずれ（本体長手中心〜軸中心）
TAB_HOLE_DIA = 3.0       # 取付タブ穴 ⌀

# ケース上の2円柱（下=ギアカバー座 / 上=出力軸スプライン）。それぞれ径と高さ
BOSS_DIA = 12.3          # 大円柱（ギアカバー座）の径 ⌀
BOSS_H = 4.6             # 大円柱の高さ（ケース上面から）
SHAFT_DIA = 4.6          # 小円柱（出力軸スプライン）の径 ⌀
SHAFT_H = 3.2            # 小円柱の高さ（大円柱の上〜軸先端）

# --- 表示用 ---
DUMMY_CLR = 0.0          # ダミーの膨らみ mm（socket確認用・通常0）

# --- ブラウザUIからのパラメータ上書き ---
try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
