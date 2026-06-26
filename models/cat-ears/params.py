# CATEGORY: かわいいロボット
# cat-ears — round-bot 用 猫耳カチューシャ（mm）
#
# round-bot のドームにかぶせるアーチ状バンド＋三角の猫耳。
# 印刷はバンドの面を寝かせて（Y面を造形プレートに）置くと平らに刷れる。

HEAD_R = 28.0    # round-bot のドーム半径（合わせる）
FIT_CLR = 0.4    # ドームとのすき間（かぶせる遊び）
BAND_W = 6.0     # バンドの幅（耳が並ぶ方向と直交）
BAND_T = 2.5     # バンドの厚み

EAR_DX = 11.0    # 耳の左右間隔（中心から）
EAR_W = 14.0     # 耳の根元の幅
EAR_H = 15.0     # 耳の高さ
EAR_T = 3.0      # 耳の厚み

# --- ブラウザUIからのパラメータ上書き ---
try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
