"""内側R25と、中央ポールを避けて外へ膨らませた外側カーブ。

    ./run.sh models/pipe-corner/model.py
"""
import sys, os, math
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from mathutils import Matrix, Vector
from blender_utils import clear_scene, EXPORTS_DIR
import corner
from rail_coupling import build_rail_coupler, export_print_part
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
    if R == R_OUTER:
        shutil.copyfile(os.path.join(EXPORTS_DIR, filename),
                        os.path.join(EXPORTS_DIR, 'pipe-corner-outer-roomy.3mf'))

for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
coupler = build_rail_coupler()
bpy.ops.object.select_all(action="DESELECT")
coupler.select_set(True)
bpy.context.view_layer.objects.active = coupler
bpy.ops.wm.stl_export(filepath=os.path.join(EXPORTS_DIR, 'pipe_rail_coupler.stl'),
                      export_selected_objects=True, global_scale=1000.0, ascii_format=False)

printed = coupler.copy()
printed.data = coupler.data.copy()
printed.name = 'pipe_rail_coupler_print'
bpy.context.scene.collection.objects.link(printed)
printed.matrix_world = Matrix.Rotation(math.radians(-90), 4, 'Y')
bpy.context.view_layer.update()
zs = [(printed.matrix_world @ Vector(corner_point)).z for corner_point in printed.bound_box]
printed.matrix_world = Matrix.Translation((0, 0, -min(zs))) @ printed.matrix_world
bpy.ops.object.select_all(action="DESELECT")
printed.select_set(True)
bpy.context.view_layer.objects.active = printed
bpy.ops.wm.stl_export(filepath=os.path.join(EXPORTS_DIR, 'pipe_rail_coupler_print.stl'),
                      export_selected_objects=True, global_scale=1000.0, ascii_format=False)
export_print_part(printed, EXPORTS_DIR, 'pipe-rail-coupler.3mf')
print('Exported rail coupler bbox mm:', [round(v * 1000, 2) for v in coupler.dimensions])
