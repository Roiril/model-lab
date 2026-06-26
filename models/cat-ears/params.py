# CATEGORY: かわいいロボット
# cat-ears — round-bot 用 猫耳カチューシャ（バンドのみ）（mm）
#
# round-bot のドームにかぶせるアーチ状バンド。耳は別途 Blender で手作り。
# 印刷はバンドの面を寝かせて（Y面を造形プレートに）置くと平らに刷れる。

HEAD_R = 28.0    # round-bot のドーム半径（合わせる）
FIT_CLR = 0.4    # ドームとのすき間（かぶせる遊び）
BAND_W = 6.0     # バンドの幅
BAND_T = 2.5     # バンドの厚み

# --- ブラウザUIからのパラメータ上書き ---
try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
