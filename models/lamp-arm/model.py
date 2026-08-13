"""卓上ランプ型ロボットアーム・スタンド（v1: 形のシルエット確定フェーズ）。

ベース（平たいD字トレー：丸リム＋中央窪み）＋ スワンネック支柱（根元フレア）
＋ ヘッド（プレースホルダ）。分割面・圧入ペグは v2 で追加する。
各パーツは別オブジェクトのまま（重なってよい）エクスポートし全体形を確認する。
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

def boolean_difference(target, cutter):
    mod = target.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier="cut")
    bpy.data.objects.remove(cutter, do_unlink=True)


def add_box(w, d, h, location=(0, 0, 0), name="box"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.scale = (w / 2, d / 2, h / 2)
    bpy.ops.object.transform_apply(scale=True)
    obj.name = name
    return obj


def add_cylinder(r, h, location=(0, 0, 0), rotation=(0, 0, 0), verts=48, name="cyl"):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=h, location=location, rotation=rotation, vertices=verts
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def filled_solid(name, pts2d, half_thick):
    """上面視の閉輪郭(pts2d)を 2D filled curve にし、±half_thick で押し出して
    上下キャップ付きのソリッドにする。z は [-half_thick, +half_thick]。"""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"      # 上下キャップを生成（manifold ソリッド化）
    cu.extrude = half_thick
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts2d) - 1)
    for bp, (x, y) in zip(sp.bezier_points, pts2d):
        bp.co = (x, y, 0.0)
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    sp.use_cyclic_u = True

    obj = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    return obj


def tapered_tube(name, pts, bevel_res):
    """(x, z, radius) の制御点列から半径テーパ付きの滑らかな丸チューブを作る。"""
    r_max = max(r for (_xz, r) in pts)
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r_max
    cu.bevel_resolution = bevel_res
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, ((x, z), r) in zip(sp.bezier_points, pts):
        bp.co = (x, 0.0, z)
        bp.radius = r / r_max
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    return obj


def apply_transform(obj, location=False, rotation=False, scale=False):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


# ============================================================
# 1. ベース（平たいD字トレー：外周リム＋中央窪み）
# ============================================================
# スラブ本体：z[-H/2,+H/2] → +H/2 持ち上げて底を z=0 に
base = filled_solid("base", BASE_OUTLINE, BASE_H / 2)
base.location.z = BASE_H / 2
apply_transform(base, location=True)

# 外周エッジを丸めてピロー状の土手に
bev = base.modifiers.new("bevel", "BEVEL")
bev.width = BASE_BEVEL_W
bev.segments = BASE_BEVEL_SEG
bev.limit_method = "ANGLE"
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier="bevel")

# 中央の窪み：輪郭を重心まわりに縮小したカッターで上面を掘る
cx = RIM_CENTER_X
rim_inner = [(cx + (x - cx) * RIM_SCALE, y * RIM_SCALE) for (x, y) in BASE_OUTLINE]
recess = filled_solid("recess", rim_inner, 0.040)   # z[-0.04,+0.04]
recess.location.z = RIM_FLOOR + 0.040               # 下端を RIM_FLOOR に合わせる
apply_transform(recess, location=True)
boolean_difference(base, recess)


# ============================================================
# 2. 支柱（スワンネック・根元フレア・扁平断面）
# ============================================================
column = tapered_tube("column", COL_PTS, COL_BEVEL_RES)
column.scale = (1.0, COL_FLATTEN_Y, 1.0)            # 左右を縮めて扁平ブレード状に
apply_transform(column, scale=True)


# ============================================================
# 3. ヘッド（手首ナックル＋マウントプレート：プレースホルダ）
# ============================================================
tip_x, tip_z = COL_PTS[-1][0]
tip = Vector((tip_x, 0.0, tip_z))

knuckle = add_cylinder(
    HEAD_KNUCKLE_R, HEAD_KNUCKLE_L,
    location=tip,
    rotation=(math.pi / 2, 0, 0),   # Z軸→Y軸
    name="head_knuckle",
)

plate_center = tip + Vector((HEAD_FWD, 0.0, HEAD_UP))
plate = add_box(HEAD_PLATE_L, HEAD_PLATE_W, HEAD_PLATE_T,
                location=plate_center, name="head_plate")
plate.rotation_euler = (0, -math.radians(HEAD_TILT_DEG), 0)
apply_transform(plate, rotation=True)

# ナックル↔プレートをつなぐ短いネック
neck_mid = (tip + plate_center) / 2
neck = add_box(HEAD_FWD * 0.7, HEAD_PLATE_W * 0.4, HEAD_UP * 0.7,
               location=neck_mid, name="head_neck")


export_stl("lamp-arm")
