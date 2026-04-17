"""Common utilities for Blender scripting via bpy."""
import bpy
import os


EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def export_stl(filename: str):
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    path = os.path.join(EXPORTS_DIR, filename if filename.endswith(".stl") else filename + ".stl")
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=False)
    print(f"Exported: {path}")
    return path
