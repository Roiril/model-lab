# CATEGORY: かわいいロボット
# rabbit-ears — square-bot 用 うさ耳カチューシャ（バンドのみ）（mm）
#
# square-bot の角頭にかぶせるコの字バンド。耳は別途 Blender で手作り。
# 印刷はバンドの面を寝かせて（Y面を造形プレートに）置くと平らに刷れる。

HEAD_W = 44.0    # square-bot の頭の幅（合わせる）
FIT_CLR = 0.4    # 頭とのすき間
BAND_W = 6.0     # バンドの幅
BAND_T = 2.5     # バンドの厚み
DROP = 10.0      # 側面に垂れる脚の長さ

# --- ブラウザUIからのパラメータ上書き ---
try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
