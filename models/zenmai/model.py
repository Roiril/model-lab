"""ゼンマイ（平面渦巻きトーションばね）回転機構。

中心アーバー — 渦巻きばね — 外周バレル を一体プリント。バレルを固定して
中心の角穴をひねるとばねが巻かれ、離すと逆回転で戻る。サポート不要。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
import bmesh
from mathutils import Vector
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()


def add_cyl(r, h, z_center, name, verts=96):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h,
                                         location=(0, 0, z_center), vertices=verts)
    o = bpy.context.active_object
    o.name = name
    return o


def add_box(w, d, h, location, name):
    bpy.ops.mesh.primitive_cube_add(size=2, location=location)
    o = bpy.context.active_object
    o.scale = (w / 2, d / 2, h / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.name = name
    return o


def boolean(target, cutter, op="DIFFERENCE"):
    m = target.modifiers.new("bool", "BOOLEAN")
    m.operation = op
    m.object = cutter
    m.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier="bool")
    bpy.data.objects.remove(cutter, do_unlink=True)


def make_spiral_ribbon():
    """アルキメデス渦巻きの中心線を肉厚 SPRING_T・高さ HEIGHT のソリッドリボンにする。"""
    n = SPIRAL_SEGS
    theta_max = TURNS * 2 * math.pi
    dr_dtheta = (RING_CL_R - HUB_CL_R) / theta_max

    centers, normals = [], []
    for k in range(n + 1):
        t = k / n
        theta = t * theta_max
        r = HUB_CL_R + (RING_CL_R - HUB_CL_R) * t
        c = Vector((r * math.cos(theta), r * math.sin(theta), 0.0))
        # 接線 dC/dθ
        tang = Vector((dr_dtheta * math.cos(theta) - r * math.sin(theta),
                       dr_dtheta * math.sin(theta) + r * math.cos(theta), 0.0))
        tang.normalize()
        nrm = Vector((-tang.y, tang.x, 0.0))  # 面内法線（90°回転）
        centers.append(c)
        normals.append(nrm)

    bm = bmesh.new()
    ht = SPRING_T / 2
    # 各断面で 4 頂点: L下, L上, R下, R上
    rings = []
    for c, nrm in zip(centers, normals):
        L = c + nrm * ht
        R = c - nrm * ht
        lb = bm.verts.new((L.x, L.y, 0.0))
        lt = bm.verts.new((L.x, L.y, HEIGHT))
        rb = bm.verts.new((R.x, R.y, 0.0))
        rt = bm.verts.new((R.x, R.y, HEIGHT))
        rings.append((lb, lt, rb, rt))

    for k in range(n):
        lb0, lt0, rb0, rt0 = rings[k]
        lb1, lt1, rb1, rt1 = rings[k + 1]
        bm.faces.new([lt0, rt0, rt1, lt1])   # top
        bm.faces.new([lb0, lb1, rb1, rb0])   # bottom
        bm.faces.new([lb0, lt0, lt1, lb1])   # L wall
        bm.faces.new([rb0, rb1, rt1, rt0])   # R wall
    # 端キャップ
    lb0, lt0, rb0, rt0 = rings[0]
    bm.faces.new([lb0, rb0, rt0, lt0])
    lb1, lt1, rb1, rt1 = rings[-1]
    bm.faces.new([lb1, lt1, rt1, rb1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("spring")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("spring", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ============================================================
# 1. 渦巻きばね（ベース骨格）
# ============================================================
spring = make_spiral_ribbon()

# ============================================================
# 2. 中心アーバー（巻き軸）を融合
# ============================================================
hub = add_cyl(HUB_R, HEIGHT, HEIGHT / 2, "hub")
boolean(spring, hub, op="UNION")

# ============================================================
# 3. 外周バレル（固定リング）を融合
# ============================================================
ring_outer = add_cyl(RING_OR, HEIGHT, HEIGHT / 2, "ring_outer")
ring_inner = add_cyl(RING_IR, HEIGHT + 0.002, HEIGHT / 2, "ring_inner")
boolean(ring_outer, ring_inner, op="DIFFERENCE")
boolean(spring, ring_outer, op="UNION")

# ============================================================
# 4. 巻きキー角穴（アーバー中心を貫通）
# ============================================================
key = add_box(KEY_SIZE, KEY_SIZE, HEIGHT + 0.002, (0, 0, HEIGHT / 2), "key")
boolean(spring, key, op="DIFFERENCE")

# ============================================================
# 5. バレル固定穴（±X 2か所）
# ============================================================
for sx in (-1, 1):
    mh = add_cyl(MOUNT_HOLE_R, HEIGHT + 0.002, HEIGHT / 2, f"mhole_{sx}")
    mh.location = (sx * MOUNT_HOLE_PCD, 0, HEIGHT / 2)
    boolean(spring, mh, op="DIFFERENCE")

spring.name = "zenmai"
export_stl("zenmai")
