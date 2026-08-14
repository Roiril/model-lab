"""Common utilities for Blender scripting via bpy."""
import bpy
import os


EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def export_stl(filename: str, only=None):
    """only にオブジェクトのリストを渡すと、それだけを書き出す（部品ごとの分割用）。"""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    base = filename[:-4] if filename.endswith(".stl") else filename
    stl_path = os.path.join(EXPORTS_DIR, base + ".stl")
    blend_path = os.path.join(EXPORTS_DIR, base + ".blend")
    if only is not None:
        bpy.ops.object.select_all(action="DESELECT")
        for o in only:
            o.select_set(True)
        bpy.context.view_layer.objects.active = only[0]
    # モデルは m 単位（1mm = 0.001）で組んでいる。STL に単位は無くスライサーは mm と読むので
    # 1000 倍して書き出す。これが無いと 160mm のモデルが 0.16mm の粒として読み込まれる。
    bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=only is not None,
                          global_scale=1000.0)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path, copy=True)
    print(f"Exported: {stl_path}")
    print(f"Saved:    {blend_path}")
    return stl_path
