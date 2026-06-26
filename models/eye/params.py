# CATEGORY: かわいいロボット
# eye — 頭の球くぼみに接着する目玉ボール（mm）。
#
# 頭は今のまま（球のくぼみ）。このボールをくぼみに後から接着剤で貼る。
# くぼみ径に合わせる: round-bot = ⌀6.4 / square-bot = ⌀6.8。
# 生成 → 印刷（黒など別色で）→ くぼみに接着。印刷は底の平面を造形プレートに置く。

EYE_DIA = 6.4    # 目玉の径（くぼみ径に合わせる。round=6.4 / square=6.8）
FLAT_H = 0.6     # 印刷用に底を平らにする高さ（接着面・くぼみ奥に入る側）

# --- ブラウザUIからのパラメータ上書き ---
try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
