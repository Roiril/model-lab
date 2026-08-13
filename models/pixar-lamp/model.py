"""Pixar ランプ（Luxo Jr.）— 傘（ヘッド）以外のアーム＆ベース。

ドーム状ベース＋基部/肘/頭部の3ピボット、各区間に平行2本ロッドと
中心線コイルスプリング。古典的な立ち姿のポーズ。
各パーツは別オブジェクトのまま（重なってよい）出力し全体形を確認する。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
from mathutils import Vector
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()


# ============================================================
# helpers
# ============================================================

def apply_transform(obj, location=False, rotation=False, scale=False):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def add_cylinder(r, h, location=(0, 0, 0), rotation=(0, 0, 0), verts=48, name="cyl"):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=h, location=location, rotation=rotation, vertices=verts
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def p3(p2d, y=0.0):
    """XZ の2点を 3D ベクトルへ（X前方, Z上）。"""
    return Vector((p2d[0], y, p2d[1]))


def segment_cylinder(a, b, r, name="seg", verts=32):
    """3D点 a→b を結ぶ円柱ロッド。"""
    a = Vector(a); b = Vector(b)
    d = b - a
    length = d.length
    mid = (a + b) / 2
    cu = add_cylinder(r, length, location=mid, verts=verts, name=name)
    cu.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    apply_transform(cu, rotation=True)
    return cu


def helix_spring(a, b, coil_r, wire_r, turns, res_u, name="spring"):
    """a→b 方向に巻くコイルスプリング（ローカル+Zに生成して整列）。"""
    a = Vector(a); b = Vector(b)
    d = b - a
    length = d.length
    n = int(turns * res_u)
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = wire_r
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(n)  # n+1 点
    for i in range(n + 1):
        t = i / n
        ang = 2.0 * math.pi * turns * t
        x = coil_r * math.cos(ang)
        y = coil_r * math.sin(ang)
        z = length * t
        sp.points[i].co = (x, y, z, 1.0)
    obj = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    # ローカル+Z を d 方向へ向け、a に配置
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    obj.location = a
    apply_transform(obj, location=True, rotation=True)
    return obj


def spring_between(a, b, margin):
    """区間 a→b の中心線に沿い、両端を margin だけ内側に縮めたスプリングを置く。"""
    a = Vector(a); b = Vector(b)
    u = (b - a).normalized()
    a2 = a + u * margin
    b2 = b - u * margin
    return helix_spring(a2, b2, SPRING_COIL_R, SPRING_WIRE_R,
                        SPRING_TURNS, SPRING_RES_U)


# ============================================================
# 1. ベース（截頭円錐＋上縁ベベル）
# ============================================================
bpy.ops.mesh.primitive_cone_add(
    radius1=BASE_R_BOTTOM, radius2=BASE_R_TOP, depth=BASE_H,
    location=(0, 0, BASE_H / 2), vertices=BASE_VERTS,
)
base = bpy.context.active_object
base.name = "base"
bev = base.modifiers.new("bevel", "BEVEL")
bev.width = BASE_BEVEL_W
bev.segments = BASE_BEVEL_SEG
bev.limit_method = "ANGLE"
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier="bevel")


# ============================================================
# 2. 関節ナックル（横向き円柱）
# ============================================================
def knuckle(p2d, name):
    return add_cylinder(
        KNUCKLE_R, KNUCKLE_L,
        location=p3(p2d), rotation=(math.pi / 2, 0, 0),  # Z→Y 横向き
        name=name,
    )

knuckle(P_BASE, "joint_base")
knuckle(P_ELBOW, "joint_elbow")
knuckle(P_HEAD, "joint_head")


# ============================================================
# 3. アーム・ロッド（各区間 平行2本）
# ============================================================
half = ROD_SPACING / 2
for seg_name, a2d, b2d in [("lower", P_BASE, P_ELBOW),
                           ("upper", P_ELBOW, P_HEAD)]:
    for side in (+1, -1):
        a = p3(a2d, side * half)
        b = p3(b2d, side * half)
        segment_cylinder(a, b, ROD_R, name=f"rod_{seg_name}_{'L' if side>0 else 'R'}")


# ============================================================
# 4. スプリング（各区間の中心線に沿う）
# ============================================================
spring_between(p3(P_BASE), p3(P_ELBOW), SPRING_MARGIN)
spring_between(p3(P_ELBOW), p3(P_HEAD), SPRING_MARGIN)


# ============================================================
# 5. 頭部スタブ（傘の代わりの短い首）
# ============================================================
head = p3(P_HEAD)
# 上アーム方向の延長線上へ前方に突き出す
u = (p3(P_HEAD) - p3(P_ELBOW)).normalized()
stub_mid = head + u * (STUB_L / 2)
stub = add_cylinder(STUB_R, STUB_L, location=stub_mid, name="head_stub")
stub.rotation_euler = u.to_track_quat("Z", "Y").to_euler()
apply_transform(stub, rotation=True)


export_stl("pixar-lamp")
