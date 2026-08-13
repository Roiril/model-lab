"""入隅マウントの見取り図を焼く。壁 2 枚・実機・カメラの視線を添えて 4 方向から。

    ./run.sh models/pixel7a-corner45/render.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
from mathutils import Vector
from blender_utils import clear_scene
from params import *

MM = 1000.0   # STL は mm で書き出してある
OUT = os.path.join(os.path.dirname(__file__), "../../exports")
STL = os.path.join(OUT, "pixel7a-corner45.stl")

A = math.radians(TILT_DEG)
CA, SA = math.cos(A), math.sin(A)
R2 = math.sqrt(2.0)
U_ORG = (U_BACK + SHELL_TOTAL * SA) * MM
ROT = (A, 0.0, -math.pi / 4)

clear_scene()


def world(u, v, z):
    return ((u + v) / R2, (u - v) / R2, z)


def sp(s, h, t=0.0):
    return world(U_ORG + s * CA + h * SA, t, s * SA - h * CA)


def color(obj, rgba):
    obj.color = rgba
    return obj


def add_box(name, size, loc, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return o


# --- 本体 ---
bpy.ops.wm.stl_import(filepath=STL)
for o in bpy.context.selected_objects:
    color(o, (0.62, 0.70, 0.80, 1.0))

# --- 壁 2 枚（貼付面と重ならないよう 0.3mm 逃がす） ---
color(add_box("wall_a", (330, 0.6, 230), (140, -0.3, 55)), (0.93, 0.91, 0.87, 1))
color(add_box("wall_b", (0.6, 330, 230), (-0.3, 140, 55)), (0.86, 0.84, 0.80, 1))

# --- 実機（Pixel 7a） ---
color(add_box("pixel7a",
              (PHONE_L * MM, PHONE_W * MM, PHONE_T * MM),
              sp(STOPPER * MM + PHONE_W * MM / 2,
                 -(FRONT_SKIN + CLR_T / 2 + PHONE_T / 2) * MM), ROT),
      (0.15, 0.16, 0.18, 1))

# --- カメラの視線（背面の法線。斜め下 40°） ---
gaze = Vector((SA / R2, SA / R2, -CA))
eye = Vector(sp(0.020 * MM, 0.0,
                (SLOT_L / 2 - CAM_EDGE_RIM - CAM_WIN_L / 2) * MM))
bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=150, vertices=16,
                                    location=eye + gaze * 75)
ray = bpy.context.object
ray.rotation_mode = "QUATERNION"
ray.rotation_quaternion = gaze.to_track_quat("Z", "Y")
color(ray, (0.95, 0.45, 0.10, 1))

# --- レンダ設定 ---
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.color_type = "OBJECT"
sc.display.shading.show_cavity = True
sc.display.render_aa = "16"
sc.render.film_transparent = False
sc.world.color = (1, 1, 1)
sc.render.resolution_x, sc.render.resolution_y = 1100, 850

bpy.ops.object.camera_add()
cam = bpy.context.object
sc.camera = cam

TARGET = Vector((62, 62, 34))
VIEWS = [
    ("room",  Vector((430, 430, 210)), 0),   # 部屋の側から角を見る
    ("top",   Vector((95, 95, 620)), 0),     # 真上
    ("wall",  Vector((520, 60, 150)), 0),    # 壁 A に沿って
    ("under", Vector((330, 330, -90)), 0),   # 下から見上げる（カメラ窓の側）
]
for name, pos, _ in VIEWS:
    cam.location = pos
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (pos - TARGET).to_track_quat("Z", "Y")
    cam.data.lens = 50
    sc.render.filepath = os.path.join(OUT, "_c45_%s.png" % name)
    bpy.ops.render.render(write_still=True)
    print("rendered", sc.render.filepath)
