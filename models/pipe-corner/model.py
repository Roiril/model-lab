"""角の内側エルボ（R25、差し込み 30）と外側エルボ（R185、差し込み 28.5）。

    ./run.sh models/pipe-corner/model.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, EXPORTS_DIR
import corner
from rail_coupling import export_print_part
from params import R_INNER, R_OUTER, STRAIGHT_INNER, STRAIGHT_OUTER

clear_scene()
os.makedirs(EXPORTS_DIR, exist_ok=True)

for R, straight, name in ((R_INNER, STRAIGHT_INNER, "pipe_corner_in_28"),
                          (R_OUTER, STRAIGHT_OUTER, "pipe_corner_out_28")):
    for ob in list(bpy.context.scene.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    body = corner.build_corner(R, straight, name)
    stl = os.path.join(EXPORTS_DIR, name + ".stl")
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True,
                          global_scale=1000.0, ascii_format=False)
    print("Exported:", stl, "bbox mm:", [round(v * 1000, 2) for v in body.dimensions])
    filename = 'pipe-corner-inner-refined.3mf' if R == R_INNER else 'pipe-corner-outer-refined.3mf'
    export_print_part(body, EXPORTS_DIR, filename)
