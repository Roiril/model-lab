`arc60/` は遮蔽修正前の同心円弧案を固定した比較用ソースです。`geometry.py` が形状、`params.py` が寸法、`gears.py` が歯形、`kinematics.py` が運動を定義します。取付レシピだけは現行の共通規格を使います。`compare_shields.py` から専用の名前空間で読み込み、合成用の現行モジュールには混ぜません。
