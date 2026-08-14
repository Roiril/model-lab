"""入隅パイプホルダーの見取り図。パイプ 2 本・仮の継手・実機・視線を添えて 4 方向から。

    ./run.sh models/pipe-corner45/render.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
from mathutils import Matrix, Vector
from blender_utils import clear_scene
from params import *

MM = 1000.0
OUT = os.path.join(os.path.dirname(__file__), "../../exports")
DL, PSI = math.radians(CAM_DEPRESSION), math.radians(YAW_DEG)
CD, SDl, CP, SP = math.cos(DL), math.sin(DL), math.cos(PSI), math.sin(PSI)
HV = Vector((CD * CP, CD * SP, -SDl))
SV = Vector((SDl * CP, SDl * SP, CD))
LV = Vector((-SP, CP, 0.0))
POCKET_ROT = Matrix(((-LV.x, SV.x, -HV.x), (-LV.y, SV.y, -HV.y),
                     (-LV.z, SV.z, -HV.z))).to_euler()
C_PH = HV * (H_PH * MM) + SV * (S_PH * MM) + LV * (L_PH * MM)
S_C = (STOPPER + PHONE_W / 2) * MM
H_C = -(FRONT_SKIN + CLR_T / 2 + PHONE_T / 2) * MM

clear_scene()


def sp(s, h, t=0.0):
    return C_PH + SV * (s - S_C) + HV * (h - H_C) - LV * t


def color(o, c):
    o.color = c
    return o


bpy.ops.wm.stl_import(filepath=os.path.join(OUT, "pipe-corner45-asm.stl"))
for o in bpy.context.selected_objects:
    color(o, (0.62, 0.70, 0.80, 1))

# --- パイプ 2 本 ---
bpy.ops.mesh.primitive_cylinder_add(radius=PIPE_OD * MM / 2, depth=460, vertices=64,
                                    location=(0, 230, 0), rotation=(math.pi / 2, 0, 0))
color(bpy.context.object, (0.80, 0.80, 0.82, 1))
bpy.ops.mesh.primitive_cylinder_add(radius=PIPE_OD * MM / 2, depth=460, vertices=64,
                                    location=(0, 0, -230))
color(bpy.context.object, (0.80, 0.80, 0.82, 1))
# --- 仮の継手 ---
for loc, rot, dep in (((0, JOINT_RAIL * MM / 2, 0), (math.pi / 2, 0, 0), JOINT_RAIL * MM),
                      ((0, 0, -JOINT_POST * MM / 2), (0, 0, 0), JOINT_POST * MM)):
    bpy.ops.mesh.primitive_cylinder_add(radius=JOINT_R * MM, depth=dep, vertices=48,
                                        location=loc, rotation=rot)
    color(bpy.context.object, (0.90, 0.55, 0.25, 1))

# --- 実機 ---
bpy.ops.mesh.primitive_cube_add(size=1.0, rotation=POCKET_ROT, location=C_PH)
ph = bpy.context.object
ph.scale = (PHONE_L * MM, PHONE_W * MM, PHONE_T * MM)
bpy.ops.object.transform_apply(scale=True)
color(ph, (0.15, 0.16, 0.18, 1))

# --- カメラの視線 ---
gaze = Vector(HV)
eye = sp(0.020 * MM, 0.0, (SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2) * MM)
bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=170, vertices=16,
                                    location=eye + gaze * 85)
ray = bpy.context.object
ray.rotation_mode = "QUATERNION"
ray.rotation_quaternion = gaze.to_track_quat("Z", "Y")
color(ray, (0.95, 0.45, 0.10, 1))

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.color_type = "OBJECT"
sc.display.shading.show_cavity = True
sc.display.render_aa = "16"
sc.world.color = (1, 1, 1)
sc.render.resolution_x, sc.render.resolution_y = 1100, 850

bpy.ops.object.camera_add()
cam = bpy.context.object
sc.camera = cam
TARGET = Vector((60, 75, -30))
VIEWS = [("side", Vector((-380, 430, 60)), 50),
         ("iso", Vector((470, 400, 240)), 50),
         ("front", Vector((380, 400, -330)), 50),
         ("clamp", Vector((280, -230, 90)), 60)]
for name, pos, lens in VIEWS:
    cam.location = pos
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (pos - TARGET).to_track_quat("Z", "Y")
    cam.data.lens = lens
    sc.render.filepath = os.path.join(OUT, "_pc45_%s.png" % name)
    bpy.ops.render.render(write_still=True)
    print("rendered", sc.render.filepath)
