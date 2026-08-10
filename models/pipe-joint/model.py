import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, EXPORTS_DIR
import joint

clear_scene()
body = joint.build_all(ref=False)

os.makedirs(EXPORTS_DIR, exist_ok=True)
stl = os.path.join(EXPORTS_DIR, "pipe_joint_28.stl")
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True, global_scale=1000.0)
print("Exported:", stl)
print("bbox mm:", [round(v * 1000, 2) for v in body.dimensions])
