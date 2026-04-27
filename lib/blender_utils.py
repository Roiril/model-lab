"""Common utilities for Blender scripting via bpy."""
import bpy
import os


EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def export_stl(filename: str):
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    base = filename[:-4] if filename.endswith(".stl") else filename
    stl_path = os.path.join(EXPORTS_DIR, base + ".stl")
    blend_path = os.path.join(EXPORTS_DIR, base + ".blend")
    bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=False)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path, copy=True)
    print(f"Exported: {stl_path}")
    print(f"Saved:    {blend_path}")
    return stl_path
