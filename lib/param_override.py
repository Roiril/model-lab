"""ブラウザUIからのパラメータ上書き機構（汎用）。

各モデルの params.py 末尾で:

    try:
        from param_override import apply_overrides
        apply_overrides(globals())
    except Exception:
        pass

を呼ぶと、環境変数 MODEL_PARAMS_JSON が指す JSON で定数を上書きできる。
JSON 例: {"BASE_R_BOTTOM": 0.04, "P_ELBOW": [0.03, 0.11]}
タプル定数はリストで渡す（indexing 互換）。
"""
import os
import json


def apply_overrides(g):
    path = os.environ.get("MODEL_PARAMS_JSON")
    if not path or not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return
    for k, v in data.items():
        if k in g:
            g[k] = v
