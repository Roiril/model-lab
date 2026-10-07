# 住人の箱 — SG92R v6

70 × 70 × 70 mm、軽量蓋0〜65°、13印刷部品。実機未検証。

日本語の全説明：[README_日本語.txt](README_日本語.txt)。画像付き：[assembly_guide.html](assembly_guide.html)。

`stl/` は印刷部品、`coupons/` は事前試験、`plates/` は形状3MFです。参照サーボは印刷しません。組立全体のSTLを一括印刷しないでください。

編集は `params.py` と `model.py`、または `editable_cube_v6.blend`。Blender 5.1.1 / Python API。寸法はm、局所ヘルパーはmm。

生成例：`blender --background --python-exit-code 1 --python model.py`

検査：`verify_motion.py` / `check_assembly.py`、`make_coupons.py` → `make_plates.py` → `audit_all.py`。スライス確認はローカルのBambu Studioプロファイルが必要です。配布にG-codeは含めません。
