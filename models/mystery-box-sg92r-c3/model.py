"""住人の箱C3を生成する。組立STLはmm、exportsは共通export_stlを使う。"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
import bmesh
from mathutils import Matrix

from blender_utils import EXPORTS_DIR, clear_scene, export_stl
from printmech.geometry import box, circle, cut, cyl_x, hull, prism, union
import motion
import params as P


HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"


def regular_polygon(n, radius, angle=0.0, center=(0.0, 0.0)):
    return [(center[0] + radius * math.cos(angle + 2 * math.pi * i / n),
             center[1] + radius * math.sin(angle + 2 * math.pi * i / n)) for i in range(n)]


def resample_polygon(poly, count):
    lengths = []
    total = 0.0
    for index in range(len(poly)):
        a, b = poly[index], poly[(index + 1) % len(poly)]
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        lengths.append(length)
        total += length
    result = []
    edge = 0
    walked = 0.0
    for sample in range(count):
        target = total * sample / count
        while walked + lengths[edge] < target:
            walked += lengths[edge]
            edge += 1
        a, b = poly[edge], poly[(edge + 1) % len(poly)]
        t = (target - walked) / lengths[edge]
        result.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return result


def loft_x(rings, name):
    """同点数の(x, [(y,z)])輪をつなぎ、段付き軸を1メッシュで作る。"""
    bm = bmesh.new()
    rows = [[bm.verts.new((x, y, z)) for y, z in ring] for x, ring in rings]
    bm.faces.new(rows[0][::-1])
    bm.faces.new(rows[-1])
    for left, right in zip(rows[:-1], rows[1:]):
        for index in range(len(left)):
            following = (index + 1) % len(left)
            bm.faces.new((left[index], right[index], right[following], left[following]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    return ob


def prepare_mesh(ob):
    """STL三角化前に共線点と微小面を落とす。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-7)
    bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
    tiny = [face for face in bm.faces if face.calc_area() < 1e-14]
    if tiny:
        bmesh.ops.dissolve_faces(bm, faces=tiny, use_verts=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def clean_closed_mesh(ob):
    """座標を保ったまま重複面、零面積面、微小な開境界を除く。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-9)
    bm.verts.index_update()
    seen = set()
    discard = []
    for face in bm.faces:
        key = tuple(sorted(vertex.index for vertex in face.verts))
        if face.calc_area() < 1e-16 or key in seen:
            discard.append(face)
        else:
            seen.add(key)
    if discard:
        bmesh.ops.delete(bm, geom=discard, context="FACES_ONLY")
    boundary = [edge for edge in bm.edges if not edge.is_manifold]
    if boundary:
        bmesh.ops.holes_fill(bm, edges=boundary)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def union_precise(target, *others):
    """0.1mmの接続部を潰さずEXACT unionする。"""
    for other in others:
        modifier = target.modifiers.new("union_precise", "BOOLEAN")
        modifier.operation = "UNION"
        modifier.solver = "EXACT"
        modifier.object = other
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(other, do_unlink=True)
        bm = bmesh.new()
        bm.from_mesh(target.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-7)
        bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.verts.index_update()
        seen = {}
        repeated = set()
        for face in bm.faces:
            key = tuple(sorted(vertex.index for vertex in face.verts))
            if key in seen:
                prior = seen[key]
                repeated.add(face)
                if prior.normal.dot(face.normal) < 0:
                    repeated.add(prior)
            else:
                seen[key] = face
        if repeated:
            bmesh.ops.delete(bm, geom=list(repeated), context="FACES_ONLY")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(target.data)
        bm.free()
        target.data.update()
    return target


def union_closed(target, other):
    """閉じた歯車とホーン受けをMANIFOLD solverで一体化する。"""
    modifier = target.modifiers.new("union_closed", "BOOLEAN")
    modifier.operation = "UNION"
    modifier.solver = "MANIFOLD"
    modifier.object = other
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(other, do_unlink=True)
    prepare_mesh(target)
    return target


def gear_polygon(cy, cz, rotation_deg=0.0):
    z = P.GEAR_TEETH
    module = P.GEAR_MODULE
    rp = module * z / 2
    rb = rp * math.cos(math.radians(P.GEAR_PRESSURE_DEG))
    ra = rp + module
    rf = rp - 1.25 * module
    alpha = math.radians(P.GEAR_PRESSURE_DEG)
    inv_pitch = math.tan(alpha) - alpha
    half = math.pi / (2 * z) - P.GEAR_BACKLASH / (2 * rp)
    pitch = 2 * math.pi / z
    points = []
    for tooth in range(z):
        center = math.radians(rotation_deg) + tooth * pitch
        base_half = half + inv_pitch
        local = [(rf, -pitch / 2), (rf, -base_half)]
        for k in range(7):
            r = rb + (ra - rb) * k / 6
            a = math.acos(rb / r)
            local.append((r, -(half - ((math.tan(a) - a) - inv_pitch))))
        for k in reversed(range(7)):
            r = rb + (ra - rb) * k / 6
            a = math.acos(rb / r)
            local.append((r, half - ((math.tan(a) - a) - inv_pitch)))
        # 谷の中央点は次の歯の先頭だけに置く。重複頂点は耳切りを壊す。
        local.append((rf, base_half))
        points.extend([(cy + r * math.cos(center + a), cz + r * math.sin(center + a))
                       for r, a in local])
    return points


def hex_bore(name):
    radius = (P.SHAFT_BORE_AF / 2) / math.cos(math.pi / 6)
    return prism(regular_polygon(6, radius, math.pi / 6, (P.CAM_AXIS_Y, P.CAM_AXIS_Z)),
                 "x", -0.05, 0.05, name)


def make_gear(name, axis_z, x0, x1, rotation):
    return prism(gear_polygon(0.0, axis_z, rotation), "x", x0, x1, name)


def horn_shapes(clearance=0.0, hub_radius=None):
    """正本ホーンの丸端、非対称腕、中心ハブをY-Z断面へ写す。"""
    tip = P.SG.HORN_TIP_W / 2 + clearance
    root = P.SG.HORN_ROOT_W / 2 + clearance
    hub = hub_radius if hub_radius is not None else P.SG.HORN_HUB_DIA / 2 + clearance
    left = P.SG.HORN_LEFT_X - clearance
    right = P.SG.HORN_RIGHT_X + clearance
    root_y = P.SG.HORN_HUB_DIA / 2
    left_arm = hull(circle((left + tip, 0), tip, 24) +
                    circle((-root_y, 0), root, 32))
    right_arm = hull(circle((root_y, 0), root, 32) +
                     circle((right - tip, 0), tip, 24))
    root_bridge = hull(circle((-root_y, 0), root, 32) +
                       circle((root_y, 0), root, 32))
    short_r = P.SG.HORN_SHORT_W / 2 + clearance
    short_half = P.SG.HORN_SPAN_Y / 2 + clearance
    short_arm = hull(circle((0, -short_half + short_r), short_r, 24) +
                     circle((0, short_half - short_r), short_r, 24))
    return [left_arm, right_arm, root_bridge, short_arm, circle((0, 0), hub, 48)]


def cross2(a, b):
    return a[0] * b[1] - a[1] * b[0]


def ray_exit(poly, direction):
    distance = 0.0
    for index, start in enumerate(poly):
        end = poly[(index + 1) % len(poly)]
        edge = (end[0] - start[0], end[1] - start[1])
        denominator = cross2(direction, edge)
        if abs(denominator) < 1e-12:
            continue
        ray_distance = cross2(start, edge) / denominator
        edge_fraction = cross2(start, direction) / denominator
        if ray_distance >= 0 and -1e-9 <= edge_fraction <= 1 + 1e-9:
            distance = max(distance, ray_distance)
    return distance


def horn_profile(clearance=0.0, hub_radius=None, count=256):
    """重なる丸端断面の外周を、原点からの放射包絡で1本の輪郭にする。"""
    shapes = horn_shapes(clearance, hub_radius)
    points = []
    for index in range(count):
        angle = 2 * math.pi * index / count
        direction = (math.cos(angle), math.sin(angle))
        radius = max(ray_exit(shape, direction) for shape in shapes)
        points.append((P.SERVO_AXIS_Y + radius * direction[0],
                       P.SERVO_AXIS_Z + radius * direction[1]))
    return points


def horn_solid(name, x0, x1, clearance=0.0, hub_radius=None):
    return prism(horn_profile(clearance, hub_radius), "x", x0, x1, name)


def make_horn_receiver(name):
    outer = horn_profile(P.HORN_CLEARANCE + P.HORN_RECEIVER_WALL,
                         P.HORN_BOSS_D / 2)
    inner = horn_profile(P.HORN_CLEARANCE)
    x0 = P.HORN_RECEIVER_OPEN_X
    x1 = P.HORN_BLIND_X0
    x2 = x1 + P.HORN_BLIND_T
    bm = bmesh.new()
    boss = [(P.SERVO_AXIS_Y + P.HORN_BOSS_D / 2 * math.cos(2 * math.pi * index / len(outer)),
             P.SERVO_AXIS_Z + P.HORN_BOSS_D / 2 * math.sin(2 * math.pi * index / len(outer)))
            for index in range(len(outer))]
    outer_rows = [[bm.verts.new((x, y, z)) for y, z in profile]
                  for x, profile in ((x0, outer), (x1, outer), (x2, boss))]
    inner_rows = [[bm.verts.new((x, y, z)) for y, z in inner] for x in (x0, x1)]
    count = len(outer)
    for index in range(count):
        following = (index + 1) % count
        bm.faces.new((outer_rows[0][index], outer_rows[0][following],
                      inner_rows[0][following], inner_rows[0][index]))
        bm.faces.new((outer_rows[0][index], outer_rows[1][index],
                      outer_rows[1][following], outer_rows[0][following]))
        bm.faces.new((outer_rows[1][index], outer_rows[2][index],
                      outer_rows[2][following], outer_rows[1][following]))
        bm.faces.new((inner_rows[0][index], inner_rows[0][following],
                      inner_rows[1][following], inner_rows[1][index]))
    blind_center = bm.verts.new((x1, P.SERVO_AXIS_Y, P.SERVO_AXIS_Z))
    end_center = bm.verts.new((x2, P.SERVO_AXIS_Y, P.SERVO_AXIS_Z))
    for index in range(count):
        following = (index + 1) % count
        bm.faces.new((inner_rows[1][index], inner_rows[1][following], blind_center))
        bm.faces.new((outer_rows[2][following], outer_rows[2][index], end_center))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    return ob


def rect_yz_between(a, b, width):
    dy, dz = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dy, dz)
    ny, nz = -dz / length * width / 2, dy / length * width / 2
    return [(a[0] + ny, a[1] + nz), (b[0] + ny, b[1] + nz),
            (b[0] - ny, b[1] - nz), (a[0] - ny, a[1] - nz)]


def cut_cap_mount(wall, side):
    """内側爪をキー溝から入れて90度回す軸端キャップの穴と板ばねを作る。"""
    half = P.CUBE_W / 2
    inner = half - P.WALL
    if side < 0:
        outer_x = -half - 0.001
        through_x = -inner + 0.0005
        body_inner_x = -P.SHAFT_MAIN_X - P.AXIAL_PLAY / 2
        wall_x0, wall_x1 = -half, -inner
        detent_x0, detent_x1 = wall_x0, body_inner_x - 0.0003
    else:
        outer_x = half + 0.001
        through_x = inner - 0.0005
        body_inner_x = P.SHAFT_MAIN_X + P.AXIAL_PLAY / 2
        wall_x0, wall_x1 = inner, half
        detent_x0, detent_x1 = body_inner_x + 0.0003, wall_x1
    bore_r = max(P.CAP_BODY_R + P.CAP_BODY_CLEARANCE,
                 P.CAP_STEM_R + P.CAP_STEM_W / 2 + P.CAP_BAYONET_CLEARANCE)
    cut(wall, cyl_x((0, P.CAM_AXIS_Z), bore_r,
                    min(outer_x, through_x), max(outer_x, through_x), 72,
                    "cap_body_bore"))
    key_half = P.CAP_LUG_W / 2 + P.CAP_BAYONET_CLEARANCE
    for sign in (-1, 1):
        cut(wall, box(min(outer_x, through_x), max(outer_x, through_x),
                      -key_half, key_half,
                      P.CAM_AXIS_Z + sign * P.CAP_LUG_R - key_half,
                      P.CAM_AXIS_Z + sign * P.CAP_LUG_R + key_half,
                      "cap_keyway"))

    angle = math.radians(P.CAP_DETENT_ANGLE_DEG)
    radial = (math.cos(angle), math.sin(angle))
    tangent = (-radial[1], radial[0])
    tip_r = P.CAP_BODY_R - P.CAP_DETENT_INTERFERENCE + P.CAP_DETENT_ARM_T / 2
    tip = (radial[0] * tip_r, P.CAM_AXIS_Z + radial[1] * tip_r)
    free_anchor = (tip[0] - tangent[0] * P.CAP_DETENT_ARM_L,
                   tip[1] - tangent[1] * P.CAP_DETENT_ARM_L)
    beam_anchor = (free_anchor[0] - tangent[0] * 0.0005,
                   free_anchor[1] - tangent[1] * 0.0005)
    pocket_tip = (tip[0] + tangent[0] * 0.0004,
                  tip[1] + tangent[1] * 0.0004)
    cut(wall, prism(rect_yz_between(free_anchor, pocket_tip,
                                    P.CAP_DETENT_ARM_T + 0.0006),
                    "x", detent_x0 - 0.0002, detent_x1 + 0.0002,
                    "cap_detent_clearance"))
    union_precise(wall, prism(rect_yz_between(beam_anchor, tip, P.CAP_DETENT_ARM_T),
                              "x", detent_x0, detent_x1, "cap_detent_spring"))


def make_drive_bearing_support():
    journal_r = P.DRIVE_JOURNAL_D / 2
    bore_r = journal_r + P.DRIVE_BEARING_RADIAL_CLEARANCE
    outer_r = bore_r + P.DRIVE_BEARING_WALL
    x0 = P.DRIVE_JOURNAL_X0 + (P.DRIVE_JOURNAL_SPAN - P.DRIVE_BEARING_W) / 2
    x1 = x0 + P.DRIVE_BEARING_W
    top = P.SERVO_AXIS_Z + bore_r
    support = box(x0, x1, -outer_r, outer_r,
                  P.SERVO_AXIS_Z - outer_r, top, "drive_bearing_support")
    cut(support, cyl_x((0, P.SERVO_AXIS_Z), bore_r,
                       x0 - 0.0005, x1 + 0.0005, 64, "drive_bearing_bore"))
    cut(support, box(x0 - 0.0005, x1 + 0.0005,
                     -bore_r - 0.0002, bore_r + 0.0002,
                     P.SERVO_AXIS_Z, top + 0.0005, "drive_bearing_opening"))
    notch_z0 = P.SERVO_AXIS_Z - outer_r + 0.0022
    notch_z1 = notch_z0 + 0.0015
    cut(support,
        box(x0 - 0.0002, x1 + 0.0002, -outer_r - 0.0002,
            -outer_r + P.DRIVE_CLIP_HOOK + 0.0002, notch_z0, notch_z1,
            "drive_clip_notch_left"),
        box(x0 - 0.0002, x1 + 0.0002, outer_r - P.DRIVE_CLIP_HOOK - 0.0002,
            outer_r + 0.0002, notch_z0, notch_z1,
            "drive_clip_notch_right"))
    union_precise(
        support,
        box(x0, x1, -P.DRIVE_BEARING_WALL / 2, P.DRIVE_BEARING_WALL / 2,
            P.FLOOR - 0.0001, P.SERVO_AXIS_Z - outer_r + 0.0002,
            "drive_bearing_center_rib"))
    for sign in (-1, 1):
        inner_y = sign * (outer_r - 0.0002)
        outer_y = sign * (outer_r + 0.005)
        rib = prism([(inner_y, P.SERVO_AXIS_Z - outer_r + 0.0002),
                     (outer_y, P.FLOOR - 0.0001),
                     (inner_y, P.FLOOR - 0.0001)],
                    "x", x0, x1, f"drive_bearing_rib_{sign}")
        union_precise(support, rib)
    return support


def make_shell():
    inner = P.CUBE_W / 2 - P.WALL
    ledge_z0 = P.CUBE_H - 0.0045
    ledge_z1 = P.CUBE_H - P.TILE_T - 0.00005
    overlap = 0.0001
    # 底と四枚の壁を個別に作る。軸受けは単純な側壁へ抜いてから一体化する。
    shell = box(-P.CUBE_W / 2, P.CUBE_W / 2, -P.CUBE_D / 2, P.CUBE_D / 2,
                0, P.FLOOR + overlap, "shell")
    front = box(-P.CUBE_W / 2, P.CUBE_W / 2,
                -P.CUBE_D / 2, -inner + overlap, P.FLOOR, P.CUBE_H, "front_wall")
    back = box(-P.CUBE_W / 2, P.CUBE_W / 2,
               inner - overlap, P.CUBE_D / 2, P.FLOOR, P.CUBE_H, "back_wall")
    left = box(-P.CUBE_W / 2, -inner + overlap, -inner, inner,
               P.FLOOR, P.CUBE_H, "left_wall")
    right = box(inner - overlap, P.CUBE_W / 2, -inner, inner,
                P.FLOOR, P.CUBE_H, "right_wall")
    cut_cap_mount(left, -1)
    cut_cap_mount(right, 1)
    # 正本配線stubの+Y方向に合わせた背面コネクタ出口。
    wire_x = -0.0255
    cut(back, box(wire_x - P.WIRE_EXIT_W / 2, wire_x + P.WIRE_EXIT_W / 2,
                  inner - 0.001, P.CUBE_D / 2 + 0.001,
                  P.SERVO_AXIS_Z - P.WIRE_EXIT_H / 2,
                  P.SERVO_AXIS_Z + P.WIRE_EXIT_H / 2, "wire_exit"))
    union_precise(shell, front, back, left, right)
    # 別刷り案内板のスカートを受ける2.2mm棚。下面は45度の斜面で壁へつなぐ。
    ledge_inner = inner - 0.0022
    ledge = box(-inner, inner, -inner, inner, ledge_z0 - overlap, ledge_z1, "frame_ledge")
    cut(ledge, box(-ledge_inner, ledge_inner, -ledge_inner, ledge_inner,
                   ledge_z0 - 0.001, ledge_z1 + 0.001, "frame_ledge_opening"))
    union_precise(shell, ledge)
    slope_bottom = ledge_z0 - 0.0022
    union_precise(
        shell,
        prism([(-inner, slope_bottom), (-inner, ledge_z0 + overlap),
               (-ledge_inner, ledge_z0 + overlap)], "x", -inner, inner, "ledge_slope_front"),
        prism([(ledge_inner, ledge_z0 + overlap), (inner, ledge_z0 + overlap),
               (inner, slope_bottom)], "x", -inner, inner, "ledge_slope_back"),
        prism([(-inner, slope_bottom), (-inner, ledge_z0 + overlap),
               (-ledge_inner, ledge_z0 + overlap)], "y", -ledge_inner, ledge_inner,
              "ledge_slope_left"),
        prism([(ledge_inner, ledge_z0 + overlap), (inner, ledge_z0 + overlap),
               (inner, slope_bottom)], "y", -ledge_inner, ledge_inner,
              "ledge_slope_right"))
    # φ12.6mmの端ハブと左スペーサーを90度位相のまま下ろす挿入溝。
    insert_half_y = P.CAM_SPACER_D / 2 + P.CAM_INSERT_CLEARANCE
    first_cam_left = -2 * P.PITCH - P.CAM_T / 2
    left_spacer_x0 = -P.CUBE_W / 2 + P.WALL + P.CAM_SPACER_GAP
    left_spacer_x1 = first_cam_left - P.CAM_SPACER_GAP
    last_cam_right = 2 * P.PITCH + P.CAM_T / 2
    right_hub_x0 = last_cam_right - 0.0002
    right_hub_x1 = P.CUBE_W / 2 - P.WALL - P.CAM_SPACER_GAP
    for x0, x1, name in (
            (left_spacer_x0, left_spacer_x1, "left_spacer_insert_slot"),
            (right_hub_x0, right_hub_x1, "right_hub_insert_slot")):
        cut(shell, box(x0 - P.CAM_INSERT_CLEARANCE, x1 + P.CAM_INSERT_CLEARANCE,
                       -insert_half_y, insert_half_y,
                       slope_bottom - 0.0002, P.CUBE_H + 0.0005, name))
    # 前後ガイド兼、キャリアの低位置ストップ。
    for sign in (-1, 1):
        y = sign * P.GUIDE_Y
        bar = box(-P.CUBE_W / 2 + P.WALL - overlap, P.CUBE_W / 2 - P.WALL + overlap,
                  y - P.GUIDE_BAR_D / 2, y + P.GUIDE_BAR_D / 2,
                  P.FOLLOWER_STOP_Z - P.GUIDE_BAR_H, P.FOLLOWER_STOP_Z,
                  f"guide_bar_{sign}")
        for i in range(P.GRID_N):
            x = (i - 2) * P.PITCH
            slot = box(x - P.GUIDE_TONGUE_W / 2 - P.GUIDE_CLEARANCE,
                       x + P.GUIDE_TONGUE_W / 2 + P.GUIDE_CLEARANCE,
                       y - P.GUIDE_BAR_D / 2 - 0.0005,
                       y + P.GUIDE_BAR_D / 2 + 0.0005,
                       P.FOLLOWER_STOP_Z - P.GUIDE_BAR_H - 0.0005,
                       P.FOLLOWER_STOP_Z + 0.0005, f"guide_slot_{sign}_{i}")
            cut(bar, slot)
        outer_rib_x = (inner + (P.GRID_N // 2) * P.PITCH) / 2
        rib_positions = [(gap - 1.5) * P.PITCH for gap in range(P.GRID_N - 1)]
        rib_positions.extend((-outer_rib_x, outer_rib_x))
        for rib_index, x in enumerate(rib_positions):
            rib = box(x - P.GUIDE_RIB_W / 2, x + P.GUIDE_RIB_W / 2,
                       y - P.GUIDE_BAR_D / 2, y + P.GUIDE_BAR_D / 2,
                       P.FLOOR - overlap,
                      P.FOLLOWER_STOP_Z - P.GUIDE_BAR_H + overlap,
                       f"guide_rib_{sign}_{rib_index}")
            union_precise(bar, rib)
        union_precise(shell, bar)
    # サーボの着座レール。正本外形に片側0.35mmを足す。
    sx0 = -(P.SG.SHAFT_BOTTOM_Z + P.SG.SHAFT_H)
    sx1 = sx0 + P.SG.BODY_H
    sy0 = P.SG.BODY_CENTER_X - P.SG.BODY_L / 2
    sy1 = P.SG.BODY_CENTER_X + P.SG.BODY_L / 2
    for x0, x1 in ((sx0 - 0.002, sx0 - P.SERVO_CLEARANCE),
                   (sx1 + P.SERVO_CLEARANCE, sx1 + 0.002)):
        rail = box(x0, x1, sy0 - 0.001, sy1 + 0.001,
                   P.FLOOR - overlap, P.SERVO_AXIS_Z - P.SG.BODY_W / 2,
                   "servo_rail")
        union_precise(shell, rail)
    for y0, y1 in ((sy0 - 0.002, sy0 - P.SERVO_CLEARANCE),
                   (sy1 + P.SERVO_CLEARANCE, sy1 + 0.002)):
        end = box(sx0 - 0.002, sx1 + 0.002, y0, y1, P.FLOOR - overlap,
                  P.SERVO_AXIS_Z - P.SG.BODY_W / 2, "servo_end")
        union_precise(shell, end)
    union_precise(shell, make_drive_bearing_support())
    return shell


def make_carrier(index):
    x = (index - 2) * P.PITCH
    beam_x_w = P.CARRIER_BEAM_X_WIDTHS[index]
    carrier = box(x - beam_x_w / 2, x + beam_x_w / 2,
                  -0.0325, 0.0325, P.CARRIER_BEAM_Z0, P.CARRIER_BEAM_Z1,
                  f"carrier_{index}")
    for sign in (-1, 1):
        y = sign * P.GUIDE_Y
        tongue = box(x - P.GUIDE_TONGUE_W / 2 + 0.0002,
                     x + P.GUIDE_TONGUE_W / 2 - 0.0002,
                     y - P.GUIDE_TONGUE_D / 2, y + P.GUIDE_TONGUE_D / 2,
                     P.FOLLOWER_STOP_Z - 0.008, P.CARRIER_BEAM_Z1, "tongue")
        outer_post_y = sign * (2 * P.PITCH + P.CARRIER_BEAM_W / 2 - 0.0002)
        inner_tongue_y = y - sign * P.GUIDE_TONGUE_D / 2
        gusset_h = abs(inner_tongue_y - outer_post_y)
        gusset = prism([(outer_post_y, P.CARRIER_BEAM_Z1 + gusset_h),
                        (outer_post_y, P.CARRIER_BEAM_Z1),
                        (inner_tongue_y, P.CARRIER_BEAM_Z1)],
                       "x", x - P.GUIDE_TONGUE_W / 2 + 0.0002,
                       x + P.GUIDE_TONGUE_W / 2 - 0.0002,
                       f"tongue_gusset_{sign}")
        union(carrier, tongue, gusset)
    for row in range(P.GRID_N):
        y = (row - 2) * P.PITCH
        post = box(x - beam_x_w / 2 + 0.0002, x + beam_x_w / 2 - 0.0002,
                   y - P.CARRIER_BEAM_W / 2 + 0.0002, y + P.CARRIER_BEAM_W / 2 - 0.0002,
                   P.CARRIER_BEAM_Z1 - 0.0003, P.TILE_Z0 + 0.0003, "post")
        tile = box(x - P.TILE / 2, x + P.TILE / 2, y - P.TILE / 2, y + P.TILE / 2,
                   P.TILE_Z0, P.CARRIER_TOP_Z, "tile")
        union(carrier, post, tile)
    return carrier


def make_top_frame():
    """見える天面を下にして平面印刷し、上から着脱する案内板。"""
    outer = P.CUBE_W / 2 - P.WALL - 0.0003
    opening = (P.PITCH * (P.GRID_N - 1) + P.TILE) / 2 + 0.0004
    frame = box(-outer, outer, -outer, outer, P.CUBE_H - P.TILE_T, P.CUBE_H, "top_frame")
    cut(frame, box(-opening, opening, -opening, opening,
                   P.CUBE_H - P.TILE_T - 0.0005, P.CUBE_H + 0.0005, "frame_opening"))
    skirt_outer = outer - 0.0022
    skirt_inner = skirt_outer - 0.0015
    skirt = box(-skirt_outer, skirt_outer, -skirt_outer, skirt_outer,
                P.CUBE_H - 0.0055, P.CUBE_H - P.TILE_T + 0.0003, "frame_skirt")
    cut(skirt, box(-skirt_inner, skirt_inner, -skirt_inner, skirt_inner,
                   P.CUBE_H - 0.006, P.CUBE_H - P.TILE_T + 0.0008, "skirt_opening"))
    union(frame, skirt)
    return frame


def make_cam(index):
    phi = math.radians(P.CAM_HOME_DEG - P.CAM_PHASE_DEG[index])
    cy = P.CAM_AXIS_Y - P.CAM_E * math.sin(phi)
    cz = P.CAM_AXIS_Z + P.CAM_E * math.cos(phi)
    x = (index - 2) * P.PITCH
    envelope = hull(circle((cy, cz), P.CAM_R, 72) +
                    circle((P.CAM_AXIS_Y, P.CAM_AXIS_Z), 0.006, 72))
    x0, x1 = x - P.CAM_T / 2, x + P.CAM_T / 2
    cam = prism(envelope, "x", x0, x1, f"cam_{index}")
    if index < 2:
        next_left = (index - 1) * P.PITCH - P.CAM_T / 2
    elif index == 2:
        next_left = P.DRIVE_GEAR_X0
    elif index < P.GRID_N - 1:
        next_left = (index - 1) * P.PITCH - P.CAM_T / 2
    else:
        next_left = P.CUBE_W / 2 - P.WALL
    hub_x1 = next_left - P.CAM_SPACER_GAP
    union_precise(cam, cyl_x((P.CAM_AXIS_Y, P.CAM_AXIS_Z), P.CAM_SPACER_D / 2,
                             x1 - 0.0002, hub_x1, 72, f"cam_{index}_spacer_hub"))
    cut(cam, hex_bore("cam_bore"))
    return cam


def make_left_spacer():
    x0 = -P.CUBE_W / 2 + P.WALL + P.CAM_SPACER_GAP
    first_cam_left = -2 * P.PITCH - P.CAM_T / 2
    spacer = cyl_x((P.CAM_AXIS_Y, P.CAM_AXIS_Z), P.CAM_SPACER_D / 2,
                   x0, first_cam_left - P.CAM_SPACER_GAP, 72, "left_spacer")
    cut(spacer, hex_bore("left_spacer_bore"))
    return spacer


def make_camshaft():
    hex_r = (P.SHAFT_AF / 2) / math.cos(math.pi / 6)
    center = (P.CAM_AXIS_Y, P.CAM_AXIS_Z)
    tip = circle(center, P.SHAFT_TIP_D / 2, 48)
    keyed = resample_polygon(regular_polygon(6, hex_r, math.pi / 6, center), 48)
    eps = 0.00005
    return loft_x([
        (-P.SHAFT_TIP_X, tip), (-P.SHAFT_MAIN_X - eps, tip),
        (-P.SHAFT_MAIN_X, keyed), (P.SHAFT_MAIN_X, keyed),
        (P.SHAFT_MAIN_X + eps, tip), (P.SHAFT_TIP_X, tip),
    ], "camshaft")


def make_cam_gear():
    gear = prism(gear_polygon(0.0, P.CAM_AXIS_Z, 276.0), "x",
                 P.DRIVE_GEAR_X0, P.DRIVE_GEAR_X1, "cam_gear")
    next_cam_left = P.PITCH - P.CAM_T / 2
    union_precise(gear, cyl_x((P.CAM_AXIS_Y, P.CAM_AXIS_Z), P.CAM_SPACER_D / 2,
                              P.DRIVE_GEAR_X1 - 0.0002,
                              next_cam_left - P.CAM_SPACER_GAP, 72,
                              "cam_gear_spacer_hub"))
    cut(gear, hex_bore("gear_bore"))
    return gear


def make_drive_gear():
    gear_profile = gear_polygon(0.0, P.SERVO_AXIS_Z, 90.0)
    def scaled_profile(radius):
        result = []
        for y, z in gear_profile:
            dy, dz = y - P.SERVO_AXIS_Y, z - P.SERVO_AXIS_Z
            scale = radius / math.hypot(dy, dz)
            result.append((P.SERVO_AXIS_Y + dy * scale,
                           P.SERVO_AXIS_Z + dz * scale))
        return result

    root_profile = scaled_profile(P.DRIVE_SUPPORT_ROOT_R)
    journal_profile = scaled_profile(P.DRIVE_JOURNAL_D / 2)
    shoulder_profile = scaled_profile(P.DRIVE_SHOULDER_D / 2)
    gear = loft_x([
        (P.DRIVE_GEAR_X0, gear_profile),
        (P.DRIVE_GEAR_X1, gear_profile),
        (P.DRIVE_SUPPORT_ROOT_X, root_profile),
        (P.DRIVE_JOURNAL_X0, journal_profile),
        (P.DRIVE_JOURNAL_X1, journal_profile),
        (P.DRIVE_JOURNAL_X1, shoulder_profile),
        (P.DRIVE_SHOULDER_X1, shoulder_profile),
    ], "drive_gear")
    receiver = make_horn_receiver("horn_receiver")
    cut(gear, cyl_x((0, P.SERVO_AXIS_Z), P.HORN_BOSS_D / 2 - 0.0005,
                    P.DRIVE_GEAR_X0 - 0.0002,
                    P.HORN_BLIND_X0 + P.HORN_BLIND_T,
                    96, "receiver_boss_recess"))
    union_precise(gear, receiver)
    return gear


def make_cap(name, side):
    def cap_difference(target, cutter):
        modifier = target.modifiers.new("cap_difference", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "EXACT"
        modifier.object = cutter
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
        prepare_mesh(target)

    half = P.CUBE_W / 2
    if side < 0:
        inner_x = -P.SHAFT_MAIN_X - P.AXIAL_PLAY / 2
        x0, x1 = -half + P.CAP_FACE_INSET, inner_x
        lug_x0 = -half + P.WALL + P.CAP_BAYONET_CLEARANCE
        lug_x1 = lug_x0 + P.CAP_LUG_T
        stem_x0, stem_x1 = lug_x1 - 0.0002, inner_x + 0.0002
    else:
        inner_x = P.SHAFT_MAIN_X + P.AXIAL_PLAY / 2
        x0, x1 = inner_x, half - P.CAP_FACE_INSET
        lug_x1 = half - P.WALL - P.CAP_BAYONET_CLEARANCE
        lug_x0 = lug_x1 - P.CAP_LUG_T
        stem_x0, stem_x1 = inner_x + 0.0002, lug_x0 + 0.0002
    cap = cyl_x((0, P.CAM_AXIS_Z), P.CAP_BODY_R, x0, x1, 72, name)
    cap_difference(cap, cyl_x((0, P.CAM_AXIS_Z), P.CAP_BORE_D / 2,
                              min(x0, x1) - 0.0005, max(x0, x1) + 0.0005,
                              48, "cap_bore"))
    for sign in (-1, 1):
        union_precise(
            cap,
            box(min(lug_x0, lug_x1), max(lug_x0, lug_x1),
                sign * P.CAP_LUG_R - P.CAP_LUG_W / 2,
                sign * P.CAP_LUG_R + P.CAP_LUG_W / 2,
                P.CAM_AXIS_Z - P.CAP_LUG_W / 2,
                P.CAM_AXIS_Z + P.CAP_LUG_W / 2,
                "cap_bayonet_lug"),
            box(min(stem_x0, stem_x1), max(stem_x0, stem_x1),
                sign * P.CAP_STEM_R - P.CAP_STEM_W / 2,
                sign * P.CAP_STEM_R + P.CAP_STEM_W / 2,
                P.CAM_AXIS_Z - P.CAP_STEM_W / 2,
                P.CAM_AXIS_Z + P.CAP_STEM_W / 2,
                "cap_bayonet_stem"),
            box(min(lug_x0, lug_x1), max(lug_x0, lug_x1),
                min(sign * P.CAP_STEM_R, sign * P.CAP_LUG_R),
                max(sign * P.CAP_STEM_R, sign * P.CAP_LUG_R),
                P.CAM_AXIS_Z - P.CAP_STEM_W / 2,
                P.CAM_AXIS_Z + P.CAP_STEM_W / 2,
                "cap_bayonet_inner_bridge"))
    angle = math.radians(P.CAP_DETENT_ANGLE_DEG)
    radial = (math.cos(angle), math.sin(angle))
    tangent = (-radial[1], radial[0])
    inner_r = P.CAP_BODY_R - P.CAP_DETENT_NOTCH_DEPTH
    outer_r = P.CAP_BODY_R + 0.0002
    half_w = P.CAP_DETENT_NOTCH_W / 2
    notch = [
        (radial[0] * inner_r + tangent[0] * half_w,
         P.CAM_AXIS_Z + radial[1] * inner_r + tangent[1] * half_w),
        (radial[0] * outer_r + tangent[0] * half_w,
         P.CAM_AXIS_Z + radial[1] * outer_r + tangent[1] * half_w),
        (radial[0] * outer_r - tangent[0] * half_w,
         P.CAM_AXIS_Z + radial[1] * outer_r - tangent[1] * half_w),
        (radial[0] * inner_r - tangent[0] * half_w,
         P.CAM_AXIS_Z + radial[1] * inner_r - tangent[1] * half_w),
    ]
    cap_difference(cap, prism(notch, "x", min(x0, x1) - 0.0002,
                              max(x0, x1) + 0.0002, "cap_detent_notch"))
    collar_inner = side * P.CAP_THRUST_COLLAR_INNER_X
    collar_outer = inner_x + side * P.CAP_THRUST_COLLAR_OVERLAP
    collar = cyl_x((0, P.CAM_AXIS_Z), P.CAP_THRUST_COLLAR_D / 2,
                   min(collar_inner, collar_outer), max(collar_inner, collar_outer),
                   72, "cap_thrust_collar")
    cap_difference(collar, cyl_x(
        (0, P.CAM_AXIS_Z), P.CAP_THRUST_COLLAR_BORE_D / 2,
        min(collar_inner, collar_outer) - 0.0002,
        max(collar_inner, collar_outer) + 0.0002, 72,
        "cap_thrust_collar_bore"))
    union_precise(cap, collar)
    return cap


def make_drive_bearing_clip():
    journal_r = P.DRIVE_JOURNAL_D / 2
    bore_r = journal_r + P.DRIVE_BEARING_RADIAL_CLEARANCE
    support_r = bore_r + P.DRIVE_BEARING_WALL
    x0 = P.DRIVE_JOURNAL_X0 + (P.DRIVE_JOURNAL_SPAN - P.DRIVE_BEARING_W) / 2
    x1 = x0 + P.DRIVE_BEARING_W
    bridge_z0 = P.SERVO_AXIS_Z + journal_r + P.DRIVE_CLIP_GAP
    bridge_z1 = bridge_z0 + P.DRIVE_BEARING_WALL
    inner_y = support_r + P.DRIVE_CLIP_GAP
    outer_y = inner_y + P.DRIVE_CLIP_T
    hook_z0 = P.SERVO_AXIS_Z - support_r + 0.00235
    clip = box(x0, x1, -outer_y, outer_y, bridge_z0, bridge_z1,
               "drive_bearing_clip")
    union(clip,
          box(x0, x1, -outer_y, -inner_y, hook_z0, bridge_z1,
              "drive_clip_leg_left"),
          box(x0, x1, inner_y, outer_y, hook_z0, bridge_z1,
              "drive_clip_leg_right"),
          box(x0, x1, -inner_y, -support_r + P.DRIVE_CLIP_HOOK,
              hook_z0, hook_z0 + P.DRIVE_CLIP_T, "drive_clip_hook_left"),
          box(x0, x1, support_r - P.DRIVE_CLIP_HOOK, inner_y,
              hook_z0, hook_z0 + P.DRIVE_CLIP_T, "drive_clip_hook_right"))
    return clip


def make_servo_clip():
    sx0 = -(P.SG.SHAFT_BOTTOM_Z + P.SG.SHAFT_H) - 0.002
    sx1 = sx0 + P.SG.BODY_H + 0.004
    # 配線根元はX=-26..-18mm、取付フランジはX=-14.5..-12.5mm。
    # 腕を本体後端の4mm区間へ寄せ、両方から0.5mm以上離す。
    center_x = sx0 + 0.003
    x0, x1 = center_x - 0.003, center_x + 0.003
    sy0 = P.SG.BODY_CENTER_X - P.SG.BODY_L / 2
    sy1 = P.SG.BODY_CENTER_X + P.SG.BODY_L / 2
    z0 = P.SERVO_AXIS_Z - P.SG.BODY_W / 2
    z1 = P.SERVO_AXIS_Z + P.SG.BODY_W / 2
    clip = box(x0, x1, sy0 - P.CLIP_T, sy0 + P.CLIP_INTERFERENCE,
               z0, z1 + P.CLIP_T, "servo_clip")
    union(clip,
          box(x0, x1, sy1 - P.CLIP_INTERFERENCE, sy1 + P.CLIP_T,
              z0, z1 + P.CLIP_T, "clip_leg"),
          box(x0, x1, sy0 - P.CLIP_T, sy1 + P.CLIP_T,
              z1, z1 + P.CLIP_T, "clip_bridge"))
    return clip


SERVO_REFERENCE_MATRIX = Matrix((
    (0, 0, 0.001, -P.SG.HORN_ARM_BOTTOM_Z),
    (0.001, 0, 0, P.SERVO_AXIS_Y),
    (0, 0.001, 0, P.SERVO_AXIS_Z),
    (0, 0, 0, 1),
))


def import_servo_ref(part, name):
    path = Path(EXPORTS_DIR) / f"sg92r-photo-{part}.stl"
    if not path.is_file():
        raise FileNotFoundError(f"SG92R正本STLがありません: {path}")
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    ob = next(item for item in bpy.data.objects if item not in before)
    ob.data.transform(SERVO_REFERENCE_MATRIX)
    ob.data.update()
    ob.name = name
    return ob


def make_fit_horn():
    receiver = make_horn_receiver("fit_horn")
    outer = horn_profile(P.HORN_CLEARANCE + P.HORN_RECEIVER_WALL,
                         P.HORN_BOSS_D / 2)
    backing = prism(outer, "x", P.HORN_BLIND_X0,
                    P.HORN_BLIND_X0 + P.HORN_BLIND_T, "fit_horn_backing")
    union_precise(receiver, backing)
    return receiver


def make_fit_bearing():
    coupon = box(-0.006, 0.006, -0.016, -0.004, 0, 0.008, "fit_bearing")
    bore = cyl_x((-0.010, 0.004), P.BEARING_D / 2, -0.0065, 0.0065, 48, "fit_bore")
    cut(coupon, bore)
    peg_r = (P.JOURNAL_AF / 2) / math.cos(math.pi / 6)
    peg = prism(regular_polygon(6, peg_r, math.pi / 6, (0.008, 0.004)),
                "x", -0.006, 0.006, "fit_peg")
    # 同一STL内で離した閉じた試片。接触や重なりはない。
    bpy.context.view_layer.objects.active = coupon
    coupon.select_set(True)
    peg.select_set(True)
    bpy.ops.object.join()
    coupon.name = "fit_bearing"
    return coupon


def add_cap_print_supports(cap, name):
    """印刷時だけ、左右の爪を前層から支える除去式フィンを足す。"""
    half = P.CUBE_W / 2
    body_h = half - P.CAP_FACE_INSET - (P.SHAFT_MAIN_X + P.AXIAL_PLAY / 2)
    lug_z0 = P.WALL + P.CAP_BAYONET_CLEARANCE - P.CAP_FACE_INSET
    root_z = body_h - P.CAP_PRINT_SUPPORT_ROOT_OVERLAP
    contact_z = lug_z0 + P.CAP_PRINT_SUPPORT_LUG_OVERLAP
    axis_x = -P.CAM_AXIS_Z if name == "cap_left" else P.CAM_AXIS_Z
    x0 = axis_x - P.CAP_PRINT_SUPPORT_FIN_T / 2
    x1 = axis_x + P.CAP_PRINT_SUPPORT_FIN_T / 2
    for sign in (-1, 1):
        fin = prism([
            (sign * (P.CAP_BODY_R - P.CAP_PRINT_SUPPORT_ROOT_OVERLAP), root_z),
            (sign * P.CAP_BODY_R, root_z),
            (sign * (P.CAP_LUG_R + P.CAP_PRINT_SUPPORT_CONTACT_W / 2), contact_z),
            (sign * (P.CAP_LUG_R - P.CAP_PRINT_SUPPORT_CONTACT_W / 2), contact_z),
        ], "x", x0, x1, f"cap_print_support_{sign:+d}")
        union_precise(cap, fin)


def export_one(ob, name, print_matrix=None):
    BUILD.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.wm.stl_export(filepath=str(BUILD / f"{name}.stl"), export_selected_objects=True,
                          global_scale=1000.0)
    if print_matrix is None:
        print_matrix = Matrix.Identity(4)
    duplicate = ob.copy()
    duplicate.data = ob.data.copy()
    bpy.context.collection.objects.link(duplicate)
    duplicate.data.transform(print_matrix)
    minimum_z = min(vertex.co.z for vertex in duplicate.data.vertices)
    duplicate.data.transform(Matrix.Translation((0, 0, -minimum_z)))
    if name in {"cap_left", "cap_right"}:
        add_cap_print_supports(duplicate, name)
    bpy.ops.object.select_all(action="DESELECT")
    duplicate.select_set(True)
    bpy.context.view_layer.objects.active = duplicate
    bpy.ops.wm.stl_export(filepath=str(BUILD / f"print_{name}.stl"), export_selected_objects=True,
                          global_scale=1000.0)
    bpy.data.objects.remove(duplicate, do_unlink=True)


def write_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def main():
    clear_scene()
    parts = {}
    parts["shell"] = make_shell()
    parts["top_frame"] = make_top_frame()
    for i in range(P.GRID_N):
        parts[f"carrier_{i}"] = make_carrier(i)
    parts["camshaft"] = make_camshaft()
    parts["left_spacer"] = make_left_spacer()
    for i in range(P.GRID_N):
        parts[f"cam_{i}"] = make_cam(i)
    parts["cam_gear"] = make_cam_gear()
    parts["drive_gear"] = make_drive_gear()
    parts["cap_right"] = make_cap("cap_right", 1)
    parts["cap_left"] = parts["cap_right"].copy()
    parts["cap_left"].data = parts["cap_right"].data.copy()
    bpy.context.collection.objects.link(parts["cap_left"])
    parts["cap_left"].data.transform(Matrix.Diagonal((-1.0, 1.0, 1.0, 1.0)))
    parts["cap_left"].name = "cap_left"
    parts["servo_clip"] = make_servo_clip()
    parts["drive_bearing_clip"] = make_drive_bearing_clip()
    parts["fit_horn"] = make_fit_horn()
    parts["fit_bearing"] = make_fit_bearing()
    parts["ref_servo"] = import_servo_ref("body", "ref_servo")
    parts["ref_horn"] = import_servo_ref("horn", "ref_horn")
    parts["ref_wire"] = import_servo_ref("wire", "ref_wire")

    for name, ob in parts.items():
        if name == "ref_horn":
            clean_closed_mesh(ob)
        else:
            prepare_mesh(ob)
            if name == "shell":
                clean_closed_mesh(ob)

    labels = {
        "shell": "箱本体", "top_frame": "天面案内板", "camshaft": "六角カム軸", "left_spacer": "左軸方向スペーサー", "cam_gear": "従動歯車",
        "drive_gear": "ホーン受け付き駆動歯車", "cap_left": "左軸端キャップ",
        "cap_right": "右軸端キャップ", "servo_clip": "サーボ押さえ",
        "drive_bearing_clip": "駆動歯車ジャーナル上クリップ",
        "fit_horn": "ホーン受け試片", "fit_bearing": "軸受け試片",
        "ref_servo": "SG92R本体", "ref_horn": "SG92R付属ホーン", "ref_wire": "SG92R配線",
    }
    for i in range(P.GRID_N):
        labels[f"carrier_{i}"] = f"格子列 {i + 1}"
        labels[f"cam_{i}"] = f"偏心カム {i + 1}"

    printable = {name for name in parts if not name.startswith("ref_")}
    flip_carrier = Matrix.Translation((0, 0, P.CARRIER_TOP_Z)) @ Matrix.Rotation(math.pi, 4, "Y")
    flat_x = Matrix.Rotation(math.pi / 2, 4, "Y")
    flat_x_mirrored = Matrix.Rotation(-math.pi / 2, 4, "Y")
    flat_hex = Matrix.Rotation(math.pi / 6, 4, "X")
    for name, ob in parts.items():
        if name in printable:
            if name.startswith("carrier_"):
                matrix = flip_carrier
            elif name == "top_frame":
                matrix = Matrix.Translation((0, 0, P.CUBE_H)) @ Matrix.Rotation(math.pi, 4, "Y")
            elif name == "cap_left":
                matrix = flat_x_mirrored
            elif name.startswith("cam_"):
                matrix = flat_x_mirrored
            elif name == "drive_gear":
                matrix = flat_x
            elif name == "camshaft":
                matrix = flat_hex
            elif name in {"left_spacer", "cap_right",
                          "fit_horn", "fit_bearing"}:
                matrix = flat_x
            elif name in {"servo_clip", "drive_bearing_clip"}:
                matrix = Matrix.Rotation(math.pi / 2, 4, "Y")
            else:
                matrix = Matrix.Identity(4)
            export_one(ob, name, matrix)
        else:
            bpy.ops.object.select_all(action="DESELECT")
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
            bpy.ops.wm.stl_export(filepath=str(BUILD / f"{name}.stl"), export_selected_objects=True,
                                  global_scale=1000.0)

    rows = []
    for index, (name, ob) in enumerate(parts.items()):
        is_ref = name.startswith("ref_")
        if name == "shell":
            explode = [0, 0, -65]
        elif name == "top_frame":
            explode = [0, 0, 55]
        elif name.startswith("carrier_"):
            column = int(name.rsplit("_", 1)[1])
            explode = [(column - 2) * 7, 0, 30]
        elif name == "camshaft":
            explode = [60, 0, 0]
        elif name == "left_spacer":
            explode = [-35, 0, 0]
        elif name.startswith("cam_") and name != "cam_gear":
            column = int(name.rsplit("_", 1)[1])
            explode = [(column - 2) * 6, 0, 0]
        elif name in {"cam_gear", "drive_gear"}:
            explode = [0, -30, 0]
        elif name == "cap_left":
            explode = [-50, 0, 0]
        elif name == "cap_right":
            explode = [50, 0, 0]
        elif name in {"servo_clip", "drive_bearing_clip"}:
            explode = [0, 0, -20]
        elif is_ref:
            explode = [0, 0, -30]
        else:
            explode = [0, 20, 0]
        rows.append({
            "id": name,
            "label": labels[name],
            "assembly": f"build/{name}.stl",
            "print": None if is_ref else f"build/print_{name}.stl",
            "fit_test": name in {"fit_horn", "fit_bearing"},
            "fit_only": name in {"fit_horn", "fit_bearing"},
            "expected_print_components": 2 if name == "fit_bearing" else 1,
            "color": "#607d8b" if is_ref else ("#c79a54" if name.startswith("carrier_") else "#d8d3c9"),
            "explode": explode,
        })
    manifest = {
        "meta": {
            "title": "住人の箱 C3・直交格子",
            "description": "5本の格子列が中央から外側へ順に持ち上がるSG92R駆動の80mm箱。",
            "dimensions_mm": [80.0, 80.0, 80.0],
            "max_dimensions_mm": [80.0, 80.0, 83.0],
            "assembly_steps": [
                "箱の外でSG92Rを90°へ合わせ、正本形状の付属ホーンを出力軸へ差す。",
                "駆動歯車の丸端付き非対称受けを付属ホーンへ差し、盲底へ着座させる。",
                "サーボ、ホーン、駆動歯車を一緒に上からU字座へ下ろす。",
                "サーボ押さえと駆動歯車ジャーナル上クリップを上から付ける。",
                "左スペーサー、5個のカム、従動歯車を90°位相で置き、右側から六角軸を通す。",
                "軸端キャップを両側から入れて90°回し、爪と板ばねで保持する。両端カラーと端ハブの公称隙間は各0.15mm。内部の隙間も含む総遊びは検証表で確認する。",
                "5本の列キャリアを上から前後ガイドへ落とし、低位置ストップへ着座させる。",
                "天面案内板を格子列の周囲へ下ろし、内側の4辺の棚へ着座させる。",
                "15°へ低速移動して全列が面一になることを確認し、90°へ低速で戻して待機する。",
                "シリアルgで15〜165°を片道2秒のquintic補間で往復させる。",
            ],
            "decisions": [
                "ホーン全角度包絡と3mm床を両立するため外形を80mm角にした。",
                "サーボ軸Z=23.5mm、カム軸Z=53.7mm、中心距離30.2mmとした。",
                "ホーン受けは片側0.2mm、+X面0.2mm、盲底2mmとし、直径12mmボスから30歯歯車まで一体化した。",
                "駆動歯車の+X側を直径6mmの3.30mmジャーナルとし、有効幅3mmのU字座と別刷り上クリップで支えた。",
                "左右キャップは外から差して90°回し、印刷した板ばねのdetentで保持する。",
                "各カムと従動歯車の右側を直径12.6mmのハブで埋め、隣接面との隙間を0.2mmにした。左端は同寸法の別刷りスペーサーで埋めた。",
                "カム軸の軸受け区間も対辺5mmの六角とし、平面印刷と0.21mmの頂点隙間を両立した。",
                "天面案内板は見える面を平面印刷する別部品とし、筐体側の棚を45度斜面で支えた。",
            ],
            "limitations": [
                "天面を上にした卓上姿勢専用。復帰は重力に依存する。",
                "SG92Rの参照表示は正本STLを使う。ホーン長さ配分と穴位置は写真由来の推定値なので試片を先に刷る。",
                "正本ホーンはスプライン歯を再現していない。ホーン受けの回転止めと公称2.5mm以上の差込は実物未確認。",
                "PLAとPETGの実摩擦、歯面の収縮、キャップの保持力は実物確認が必要。",
                "停電時はサーボ減速機を重力で逆駆動できず、停止角度付近に残る場合がある。復電後は15°へ低速復帰する。",
            ],
        },
        "parts": rows,
    }
    write_json(BUILD / "manifest.json", manifest)
    write_json(BUILD / "motion.json", {
        "duration_s": P.MOTION_DURATION_S,
        "home_servo_deg": P.SERVO_HOME_DEG,
        "end_servo_deg": P.SERVO_END_DEG,
        "interpolation": "quintic-command / 1deg sampled transforms",
        "frames": motion.frames(),
    })

    # Studio標準の単体表示用。試片は除き、組立状態だけを共通export_stlで出す。
    visible = [ob for name, ob in parts.items() if not name.startswith("fit_")]
    export_stl(P.MODEL_ID, only=visible)
    print(f"[c3] parts={len(parts)} build={BUILD}")


if __name__ == "__main__":
    main()
