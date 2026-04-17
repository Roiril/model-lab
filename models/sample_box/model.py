"""Sample: simple box for 3D printing."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

import bpy
from blender_utils import clear_scene, export_stl

# params (mm → m)
WIDTH  = 0.050  # 50mm
DEPTH  = 0.030  # 30mm
HEIGHT = 0.020  # 20mm

clear_scene()

bpy.ops.mesh.primitive_cube_add(size=1)
box = bpy.context.active_object
box.scale = (WIDTH / 2, DEPTH / 2, HEIGHT / 2)
bpy.ops.object.transform_apply(scale=True)

export_stl("sample_box")
