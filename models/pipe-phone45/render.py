"""パイプ端ホルダーの見取り図。パイプ・仮の継手・実機・カメラの視線を添えて 4 方向から。

    ./run.sh models/pipe-phone45/render.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
from mathutils import Vector
from blender_utils import clear_scene
from params import *

MM = 1000.0
OUT = os.path.join(os.path.dirname(__file__), "../../exports")
A = math.radians(TILT_DEG)
UY, UZ = math.cos(A), math.sin(A)
NY, NZ = math.sin(A), -math.cos(A)
S0 = SLOPE_LEN / 2
ORG_Y = ((D_BACK + SHELL_TOTAL) * NY - S0 * UY) * MM
ORG_Z = (-(D_BACK + SHELL_TOTAL) * math.cos(A) - S0 * UZ) * MM
X_MID = (JOINT_LEN + JOINT_GAP + RING_W / 2 + RING_DX / 2) * MM

clear_scene()


def sp(s, h, x=0.0):
    return (x, ORG_Y + s * UY + h * NY, ORG_Z + s * UZ + h * NZ)


def color(o, c):
    o.color = c
    return o


def add_box(name, size, loc, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    o = bpy.context.object
    o.name, o.scale = name, size
    bpy.ops.object.transform_apply(scale=True)
    return o


# 印刷用の STL は立てた向きなので、確認には組んだ状態（-asm）を読む。
bpy.ops.wm.stl_import(filepath=os.path.join(OUT, "pipe-phone45-asm.stl"))
for o in bpy.context.selected_objects:
    color(o, (0.62, 0.70, 0.80, 1))

# --- パイプ（x=0 が端。負の側は継手の向こう） ---
bpy.ops.mesh.primitive_cylinder_add(radius=PIPE_OD * MM / 2, depth=520, vertices=64,
                                    location=(230, 0, 0), rotation=(0, math.pi / 2, 0))
color(bpy.context.object, (0.80, 0.80, 0.82, 1))
# --- 仮の継手（実測したら params の JOINT_* を直す） ---
bpy.ops.mesh.primitive_cylinder_add(radius=JOINT_R * MM, depth=JOINT_LEN * MM,
                                    vertices=48, location=(JOINT_LEN * MM / 2, 0, 0),
                                    rotation=(0, math.pi / 2, 0))
color(bpy.context.object, (0.90, 0.55, 0.25, 1))

# --- 実機 ---
color(add_box("pixel7a", (PHONE_L * MM, PHONE_W * MM, PHONE_T * MM),
              sp(STOPPER * MM + PHONE_W * MM / 2,
                 -(FRONT_SKIN + CLR_T / 2 + PHONE_T / 2) * MM, X_MID),
              (A, 0, 0)), (0.15, 0.16, 0.18, 1))

# --- カメラの視線 ---
gaze = Vector((0.0, NY, NZ))
eye = Vector(sp(0.020 * MM, 0.0, X_MID + (SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2) * MM))
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
TARGET = Vector((X_MID, 20, -20))
VIEWS = [("axis", Vector((X_MID - 620, 60, 40)), 60),
         ("iso", Vector((X_MID - 330, 330, 240)), 50),
         ("front", Vector((X_MID + 60, 420, -260)), 50),
         ("clamp", Vector((60, 210, 150)), 60)]
for name, pos, lens in VIEWS:
    tgt = Vector((65, 10, 0)) if name == "clamp" else TARGET
    cam.location = pos
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (pos - tgt).to_track_quat("Z", "Y")
    cam.data.lens = lens
    sc.render.filepath = os.path.join(OUT, "_p45_%s.png" % name)
    bpy.ops.render.render(write_still=True)
    print("rendered", sc.render.filepath)
