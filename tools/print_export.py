"""印刷用: 各モデルをビルドし、構成パーツを1つずつ別STLで書き出す。

実行: blender --background --python tools/print_export.py
出力: <model-lab>/prints/<model>__<part>.stl
"""
import bpy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "prints")
os.makedirs(OUT, exist_ok=True)

# 既存の .stl を掃除（最新セットだけにする）
for f in os.listdir(OUT):
    if f.endswith(".stl"):
        os.remove(os.path.join(OUT, f))

MODELS = ["round-bot", "square-bot", "servo-test", "sg92r"]


def run_model(model):
    mp = os.path.join(ROOT, "models", model, "model.py")
    # 前モデルの params キャッシュを捨てる（同名モジュールの取り違え防止）
    sys.modules.pop("params", None)
    g = {"__file__": mp, "__name__": "__main__"}
    with open(mp, encoding="utf-8") as fh:
        code = fh.read()
    exec(compile(code, mp, "exec"), g)  # clear_scene + build + 結合STL出力


def export_parts(model):
    n = 0
    for o in list(bpy.data.objects):
        if o.type != "MESH":
            continue
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        path = os.path.join(OUT, f"{model}__{o.name}.stl")
        bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
        d = o.dimensions
        print(f"[part] {os.path.basename(path)}  {d.x*1000:.1f} x {d.y*1000:.1f} x {d.z*1000:.1f} mm")
        n += 1
    print(f"[model] {model}: {n} parts")


for m in MODELS:
    run_model(m)
    export_parts(m)

print("PRINT_DIR:", OUT)
