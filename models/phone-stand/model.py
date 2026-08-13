"""アーム式スマホスタンド（固定ポーズの装飾モデル）。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
import bmesh
from mathutils import Vector, Matrix
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()


# ============================================================
# helpers
# ============================================================

def add_cylinder(r, h, location=(0, 0, 0), rotation=(0, 0, 0), verts=32, name="cyl"):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=h, location=location, rotation=rotation, vertices=verts
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def add_box(w, d, h, location=(0, 0, 0), name="box"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.scale = (w / 2, d / 2, h / 2)
    bpy.ops.object.transform_apply(scale=True)
    obj.name = name
    return obj


def add_rod_between(p1, p2, r, name="rod"):
    """2点間を結ぶ円柱。"""
    p1 = Vector(p1); p2 = Vector(p2)
    vec = p2 - p1
    length = vec.length
    mid = (p1 + p2) / 2
    # デフォルト Z 軸方向の円柱を vec 方向へ向ける
    z = Vector((0, 0, 1))
    if vec.length > 1e-9:
        rot_quat = z.rotation_difference(vec)
    else:
        rot_quat = z.to_track_quat('Z', 'Y')
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=length, location=mid, vertices=24)
    obj = bpy.context.active_object
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = rot_quat
    obj.name = name
    return obj


def add_spring(p1, p2, coil_r, wire_r, turns, name="spring"):
    """2点間に伸びるコイルバネを bmesh で生成。"""
    p1 = Vector(p1); p2 = Vector(p2)
    axis = p2 - p1
    length = axis.length
    if length < 1e-6:
        return None

    # 軸方向の正規直交基底
    z_axis = axis.normalized()
    helper = Vector((0, 0, 1)) if abs(z_axis.z) < 0.9 else Vector((1, 0, 0))
    x_axis = (helper - z_axis * helper.dot(z_axis)).normalized()
    y_axis = z_axis.cross(x_axis)

    # コイルの中心線
    segments_per_turn = 16
    total_segs = turns * segments_per_turn
    centers = []
    for i in range(total_segs + 1):
        t = i / total_segs
        ang = t * turns * 2 * math.pi
        offset = x_axis * math.cos(ang) * coil_r + y_axis * math.sin(ang) * coil_r
        centers.append(p1 + z_axis * (t * length) + offset)

    # 円形断面を sweep
    ring_segs = 8
    bm = bmesh.new()
    rings = []
    for i, c in enumerate(centers):
        # 中心線の接線
        if i == 0:
            tangent = (centers[1] - centers[0]).normalized()
        elif i == len(centers) - 1:
            tangent = (centers[-1] - centers[-2]).normalized()
        else:
            tangent = (centers[i + 1] - centers[i - 1]).normalized()
        # 接線に直交する基底
        helper2 = Vector((0, 0, 1)) if abs(tangent.z) < 0.9 else Vector((1, 0, 0))
        u = (helper2 - tangent * helper2.dot(tangent)).normalized()
        v = tangent.cross(u)
        ring = []
        for j in range(ring_segs):
            a = j / ring_segs * 2 * math.pi
            p = c + u * math.cos(a) * wire_r + v * math.sin(a) * wire_r
            ring.append(bm.verts.new(p))
        rings.append(ring)

    # ring 間を四角面で連結
    for i in range(len(rings) - 1):
        r0 = rings[i]; r1 = rings[i + 1]
        for j in range(ring_segs):
            j2 = (j + 1) % ring_segs
            bm.faces.new([r0[j], r0[j2], r1[j2], r1[j]])
    # 端面（キャップ）
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ============================================================
# 1. 机クランプ（C字）
# ============================================================
# C字を bmesh で押し出して作る
def make_clamp():
    bm = bmesh.new()
    # 側面プロファイル（XZ平面）。机は z=0、机上面にスタンドが乗る
    # 上アーム、背、下アームの C 字
    bw = CLAMP_W
    bt = CLAMP_T
    bd = CLAMP_DEPTH
    op = CLAMP_OPENING
    # 外枠を反時計回りで定義（Y方向に押し出す）
    # 下アーム下面 z = -(op + bt)、上アーム上面 z = bt（机が z=0 〜 -op の間に挟まれるイメージ）
    z_top = bt
    z_bot = -(op + bt)
    x_back = -bw / 2
    x_front = bw / 2
    pts = [
        (x_back, 0, z_bot),
        (x_front, 0, z_bot),
        (x_front, 0, z_bot + bt),
        (x_back + bt, 0, z_bot + bt),
        (x_back + bt, 0, z_top - bt),
        (x_front, 0, z_top - bt),
        (x_front, 0, z_top),
        (x_back, 0, z_top),
    ]
    verts = [bm.verts.new(p) for p in pts]
    face = bm.faces.new(verts)
    # Y方向に押し出し
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    new_verts = [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, bd, 0), verts=new_verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new("clamp")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("clamp", mesh)
    bpy.context.collection.objects.link(obj)
    # クランプを y 中央へ
    obj.location = (0, -bd / 2, 0)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True)
    return obj


clamp = make_clamp()

# 締め付けネジ（下アームの下から伸びる）
screw_z = -(CLAMP_OPENING + CLAMP_T) - CLAMP_SCREW_L / 2 + 0.005
screw = add_cylinder(
    CLAMP_SCREW_R, CLAMP_SCREW_L,
    location=(0, 0, screw_z),
    name="screw",
)
# ネジのノブ
knob = add_cylinder(
    CLAMP_SCREW_R * 2.2, 0.010,
    location=(0, 0, screw_z - CLAMP_SCREW_L / 2 - 0.005),
    name="knob",
)


# ============================================================
# 2. 垂直支柱
# ============================================================
post_base_z = CLAMP_T  # クランプ上面
post = add_cylinder(
    POST_R, POST_H,
    location=(0, 0, post_base_z + POST_H / 2),
    name="post",
)
post_top = Vector((0, 0, post_base_z + POST_H))


# ============================================================
# 3. 3関節アーム（XZ 平面内でジグザグ）
# ============================================================
def add_joint(center, name):
    """関節（厚み JOINT_T、Y軸を回転軸とする円盤）。"""
    return add_cylinder(
        JOINT_R, JOINT_T,
        location=center,
        rotation=(math.pi / 2, 0, 0),  # Z軸→Y軸
        name=name,
    )


def arm_segment(start, angle, length, idx):
    """start から XZ 平面内で angle（Y軸まわり、X+ から +Z へ）方向に length のアーム。"""
    direction = Vector((math.cos(angle), 0, math.sin(angle)))
    end = start + direction * length

    # 関節（始点）
    add_joint(start, f"joint_{idx}_a")
    # アーム本体（2本の棒で表現してバネを挟む雰囲気）
    side_offset = SPRING_R + ARM_R + 0.001
    perp = Vector((-math.sin(angle), 0, math.cos(angle))) * side_offset
    add_rod_between(start + perp, end + perp, ARM_R, name=f"arm_{idx}_top")
    add_rod_between(start - perp, end - perp, ARM_R, name=f"arm_{idx}_bot")

    # バネ（中央、両端を少し縮めた区間）
    margin = (1 - SPRING_LEN_RATIO) / 2
    sp_start = start + direction * (length * margin)
    sp_end = start + direction * (length * (1 - margin))
    add_spring(sp_start, sp_end, SPRING_R, SPRING_WIRE_R, SPRING_TURNS, name=f"spring_{idx}")

    return end


# 累積角度でジグザグに配置
p = post_top
a = ARM1_ANGLE
p = arm_segment(p, a, ARM_LEN, 1)

a = a + ARM2_ANGLE  # 折れ
p = arm_segment(p, a, ARM_LEN, 2)

a = a + ARM3_ANGLE
p = arm_segment(p, a, ARM_LEN * 0.7, 3)  # 最終アームは少し短く

# 末端の関節（ホルダー接続部）
add_joint(p, "joint_end")
holder_anchor = p


# ============================================================
# 4. スマホホルダー
# ============================================================
# ホルダーの中心は anchor から少し前方
# anchor から HOLDER_TILT の傾きで 5cm 先にプレート中心
holder_dir = Vector((math.cos(HOLDER_TILT), 0, math.sin(HOLDER_TILT)))
holder_center = holder_anchor + holder_dir * 0.040

# プレート（裏板）
plate = add_box(
    HOLDER_W, HOLDER_PLATE_T, HOLDER_W * 0.7,  # 横幅広め、縦は少し短め
    location=holder_center,
    name="holder_plate",
)
# プレートを傾ける（Y軸まわり）
plate.rotation_euler = (0, -HOLDER_TILT, 0)
bpy.context.view_layer.objects.active = plate
bpy.ops.object.transform_apply(rotation=True)

# 4つの爪（プレートの四隅から前方へ）
plate_half_w = HOLDER_W / 2
plate_half_h = HOLDER_W * 0.7 / 2
forward = Vector((-math.sin(HOLDER_TILT), 0, math.cos(HOLDER_TILT)))  # プレート法線（前向き）
right = Vector((0, 1, 0))  # プレート横方向（Y軸）

# 横方向を実際にはプレートのローカル「横」にしたい → プレートは XZ 平面に立っていて Y が薄み
# 上の add_box では w=HOLDER_W が X、d=HOLDER_PLATE_T が Y、h が Z。
# 傾けたあとは X が「水平横」ではなく傾いた方向になる。
# 簡単のため、爪は holder_center から ±X 方向（傾き考慮）と ±Z（傾き考慮）でオフセット。
local_x = Vector((math.cos(HOLDER_TILT), 0, math.sin(HOLDER_TILT)))  # 傾いた X
local_z = Vector((-math.sin(HOLDER_TILT), 0, math.cos(HOLDER_TILT)))  # 法線（前向き）= forward
local_y = Vector((0, 1, 0))

# 爪は左右の中央上下、または四隅
grip_offset_z = plate_half_h - 0.005
grip_offset_x = plate_half_w - 0.008
for sx in (-1, 1):
    for sz in (-1, 1):
        base = holder_center + local_x * (sx * grip_offset_x) + Vector((0, 0, sz * grip_offset_z * math.cos(HOLDER_TILT)))
        # プレートから前方に少し出した位置
        base = base + forward * (HOLDER_PLATE_T / 2 + GRIP_W / 2)
        bpy.ops.mesh.primitive_cube_add(size=1, location=base)
        grip = bpy.context.active_object
        grip.scale = (GRIP_W / 2, GRIP_W / 2, GRIP_H / 2)
        bpy.ops.object.transform_apply(scale=True)
        grip.name = f"grip_{sx}_{sz}"


# ============================================================
# 5. スマホ本体（ホルダーに装着）
# ============================================================
# 初期軸: X=厚み(T), Y=幅(W), Z=縦(H) — X を forward に揃える前提
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
phone = bpy.context.active_object
phone.name = "phone"
phone.scale = (PHONE_T / 2, PHONE_W / 2, PHONE_H / 2)
bpy.ops.object.transform_apply(scale=True)

# 角丸
bevel = phone.modifiers.new("bevel", "BEVEL")
bevel.width = PHONE_CORNER_R
bevel.segments = 6
bevel.limit_method = "ANGLE"
bpy.ops.object.modifier_apply(modifier="bevel")

# X軸（厚み方向）を forward に揃える Y軸まわり回転
# Y回転 θ で X(1,0,0) → (cosθ, 0, -sinθ)。forward = (cos a, 0, sin a) なら θ = -a
fwd_angle = math.atan2(forward.z, forward.x)
phone.rotation_euler = (0, -fwd_angle, 0)
bpy.ops.object.transform_apply(rotation=True)

# プレート前面に配置
phone.location = holder_center + forward * (HOLDER_PLATE_T / 2 + PHONE_T / 2)

export_stl("phone-stand")
