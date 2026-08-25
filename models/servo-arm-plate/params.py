# CATEGORY: ロボットアーム
# servo-arm-plate — servo-arm の 3 部品を造形プレートに並べたもの（単位: mm）
#
# 形は作らない。servo-arm が出した印刷用 STL をそのまま読み込み、向きを確かめて
# 並べ直すだけ。だから寸法は servo-arm/params.py が正で、ここには「並べ方」しか無い。
#
# 使う前に servo-arm をビルドしておくこと（./run.sh models/servo-arm/model.py）。
# STL が古いとビルド時に警告が出る。
#
# 向きは 6 通りの面接地を実測して決めた（scratchpad/orient.py）。3 部品とも
# servo-arm が出したままの向きが最良で、回すと接地面積が 1/5 以下に落ちて
# 垂れる面が 10 倍以上に増える。だからここでは回さない。

# ============================================================
# プリンタ（exports/whistle.3mf の設定から実測）
# Bambu Lab X1 Carbon / 0.4mm ノズル / 0.2mm 層 / PLA Basic / サポート OFF
# ============================================================
BED_W = 256.0         # 造形プレート 幅
BED_D = 256.0         # 同 奥行き
EXCLUDE_W = 18.0      # 手前左の除外域 幅（オートカットの落とし口）
EXCLUDE_D = 28.0      # 同 奥行き
BRIM = 5.0            # auto brim の想定幅（部品の外へ出る量）
GAP = 4.0             # brim どうしの間に残すすきま
MARGIN = 8.0          # プレート縁から brim までの余白

# 並べる順（左から）。指の入るすきまを確保したいときは GAP を上げる
ORDER = ("servo-arm-base", "servo-arm-upper", "servo-arm-fore")

# 1 枚に載せず 1 部品ずつ刷るなら 0 にする（並びの確認だけしたいとき）
PLACE_ALL = 1

# --- ブラウザUIからのパラメータ上書き ---
try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
