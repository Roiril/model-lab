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

from blender_utils import clear_scene, export_stl
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
    ob = prism(gear_polygon(0.0, axis_z, rotation), "x", x0, x1, name)
    hub = cyl_x((0.0, axis_z), 0.006, x0, x1, 72, name + "_hub")
    union(ob, hub)
    return ob


def horn_profile(clearance=0.0, wall=0.0):
    left = P.SG.HORN_LEFT_X - clearance - wall
    right = P.SG.HORN_RIGHT_X + clearance + wall
    tip = P.SG.HORN_TIP_W / 2 + clearance + wall
    root = P.SG.HORN_ROOT_W / 2 + clearance + wall
    root_x = 0.0045
    return [(left, -tip), (-root_x, -root), (root_x, -root), (right, -tip),
            (right, tip), (root_x, root), (-root_x, root), (left, tip)]


def horn_solid(name, x0, x1, clearance=0.0, wall=0.0):
    long_arm = prism([(P.SERVO_AXIS_Y + y, P.SERVO_AXIS_Z + z)
                      for y, z in horn_profile(clearance, wall)], "x", x0, x1, name)
    short_half = P.SG.HORN_SPAN_Y / 2 + clearance + wall
    short_w = P.SG.HORN_SHORT_W / 2 + clearance + wall
    short_arm = box(x0, x1, P.SERVO_AXIS_Y - short_w, P.SERVO_AXIS_Y + short_w,
                    P.SERVO_AXIS_Z - short_half, P.SERVO_AXIS_Z + short_half, name + "_short")
    union(long_arm, short_arm)
    return long_arm


def make_shell():
    inner = P.CUBE_W / 2 - P.WALL
    ledge_z0, ledge_z1 = P.CUBE_H - 0.0045, P.CUBE_H - P.TILE_T
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
    bearing_ring = circle((0, P.CAM_AXIS_Z), P.BEARING_D / 2, 48)
    cap_ring = circle((0, P.CAM_AXIS_Z), 0.0043, 48)
    cut(left, loft_x([
        (-P.CUBE_W / 2 - 0.001, cap_ring), (-P.SHAFT_MAIN_X, cap_ring),
        (-P.SHAFT_MAIN_X + 0.00005, bearing_ring), (-inner + 0.001, bearing_ring),
    ], "bearing_cut_l"))
    cut(right, loft_x([
        (inner - 0.001, bearing_ring), (P.SHAFT_MAIN_X - 0.00005, bearing_ring),
        (P.SHAFT_MAIN_X, cap_ring), (P.CUBE_W / 2 + 0.001, cap_ring),
    ], "bearing_cut_r"))
    # SG92Rの3ピンコネクタが通る前面出口。
    cut(front, box(-0.020, -0.020 + P.WIRE_EXIT_W,
                   -P.CUBE_D / 2 - 0.001, -inner + 0.001,
                   P.FLOOR, P.FLOOR + P.WIRE_EXIT_H, "wire_exit"))
    union(shell, front, back, left, right)
    # 別刷り案内板のスカートを受ける2.2mm棚。下面は45度の斜面で壁へつなぐ。
    ledge_inner = inner - 0.0022
    ledge = box(-inner, inner, -inner, inner, ledge_z0 - overlap, ledge_z1, "frame_ledge")
    cut(ledge, box(-ledge_inner, ledge_inner, -ledge_inner, ledge_inner,
                   ledge_z0 - 0.001, ledge_z1 + 0.001, "frame_ledge_opening"))
    union(shell, ledge)
    slope_bottom = ledge_z0 - 0.0022
    union(shell,
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
        for gap in range(P.GRID_N - 1):
            x = (gap - 1.5) * P.PITCH
            rib = box(x - P.GUIDE_RIB_W / 2, x + P.GUIDE_RIB_W / 2,
                      y - P.GUIDE_BAR_D / 2, y + P.GUIDE_BAR_D / 2,
                      P.FLOOR - overlap,
                      P.FOLLOWER_STOP_Z - P.GUIDE_BAR_H + overlap,
                      f"guide_rib_{sign}_{gap}")
            union(bar, rib)
        union(shell, bar)
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
        union(shell, rail)
    for y0, y1 in ((sy0 - 0.002, sy0 - P.SERVO_CLEARANCE),
                   (sy1 + P.SERVO_CLEARANCE, sy1 + 0.002)):
        end = box(sx0 - 0.002, sx1 + 0.002, y0, y1, P.FLOOR - overlap,
                  P.SERVO_AXIS_Z - P.SG.BODY_W / 2, "servo_end")
        union(shell, end)
    return shell


def make_carrier(index):
    x = (index - 2) * P.PITCH
    carrier = box(x - P.CARRIER_BEAM_W / 2, x + P.CARRIER_BEAM_W / 2,
                  -0.0325, 0.0325, P.CARRIER_BEAM_Z0, P.CARRIER_BEAM_Z1,
                  f"carrier_{index}")
    for sign in (-1, 1):
        y = sign * P.GUIDE_Y
        tongue = box(x - P.GUIDE_TONGUE_W / 2 + 0.0002,
                     x + P.GUIDE_TONGUE_W / 2 - 0.0002,
                     y - P.GUIDE_TONGUE_D / 2, y + P.GUIDE_TONGUE_D / 2,
                     P.FOLLOWER_STOP_Z - 0.008, P.CARRIER_BEAM_Z1, "tongue")
        union(carrier, tongue)
    for row in range(P.GRID_N):
        y = (row - 2) * P.PITCH
        post = box(x - P.CARRIER_BEAM_W / 2 + 0.0002, x + P.CARRIER_BEAM_W / 2 - 0.0002,
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
    cut(cam, hex_bore("cam_bore"))
    return cam


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
    cut(gear, hex_bore("gear_bore"))
    return gear


def make_drive_gear():
    gear = make_gear("drive_gear", P.SERVO_AXIS_Z, P.DRIVE_GEAR_X0, P.DRIVE_GEAR_X1, 90.0)
    bridge = cyl_x((0, P.SERVO_AXIS_Z), 0.006, P.HORN_RECEIVER_X1 - 0.0003,
                   P.DRIVE_GEAR_X0 + 0.0003, 64, "drive_bridge")
    union(gear, bridge)
    outer = horn_solid("horn_receiver_outer", P.HORN_RECEIVER_X0, P.HORN_RECEIVER_X1,
                       P.HORN_CLEARANCE, P.HORN_RECEIVER_WALL)
    inner = horn_solid("horn_receiver_inner", P.HORN_RECEIVER_X0 - 0.0005,
                       P.HORN_RECEIVER_X1 + 0.0005, P.HORN_CLEARANCE, 0.0)
    cut(outer, inner)
    union(gear, outer)
    # 90°位相合わせ用の非対称キー。長腕左端側だけに三角印を置く。
    mark = prism([(P.SERVO_AXIS_Y + P.SG.HORN_LEFT_X - 0.001, P.SERVO_AXIS_Z - 0.0015),
                  (P.SERVO_AXIS_Y + P.SG.HORN_LEFT_X - 0.001, P.SERVO_AXIS_Z + 0.0015),
                  (P.SERVO_AXIS_Y + P.SG.HORN_LEFT_X - 0.003, P.SERVO_AXIS_Z)],
                 "x", P.HORN_RECEIVER_X0, P.HORN_RECEIVER_X1, "phase_mark")
    union(gear, mark)
    return gear


def make_cap(name, side):
    if side < 0:
        x0, x1 = -P.CUBE_W / 2, -P.SHAFT_MAIN_X - P.AXIAL_PLAY / 2
    else:
        x0, x1 = P.SHAFT_MAIN_X + P.AXIAL_PLAY / 2, P.CUBE_W / 2
    cap = cyl_x((0, P.CAM_AXIS_Z), 0.0042, x0, x1, 48, name)
    cut(cap, cyl_x((0, P.CAM_AXIS_Z), P.CAP_BORE_D / 2,
                   min(x0, x1) - 0.0005, max(x0, x1) + 0.0005, 48, "cap_bore"))
    return cap


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


def make_ref_servo():
    x0 = -(P.SG.SHAFT_BOTTOM_Z + P.SG.SHAFT_H)
    body = box(x0, x0 + P.SG.BODY_H,
               P.SG.BODY_CENTER_X - P.SG.BODY_L / 2,
               P.SG.BODY_CENTER_X + P.SG.BODY_L / 2,
               P.SERVO_AXIS_Z - P.SG.BODY_W / 2, P.SERVO_AXIS_Z + P.SG.BODY_W / 2,
               "ref_servo")
    flange_x0 = P.SG.FLANGE_BOTTOM_Z - (P.SG.SHAFT_BOTTOM_Z + P.SG.SHAFT_H)
    flange = box(flange_x0, flange_x0 + P.SG.FLANGE_T,
                  P.SG.BODY_CENTER_X - P.SG.FLANGE_L / 2,
                  P.SG.BODY_CENTER_X + P.SG.FLANGE_L / 2,
                  P.SERVO_AXIS_Z - P.SG.FLANGE_W / 2, P.SERVO_AXIS_Z + P.SG.FLANGE_W / 2,
                  "ref_flange")
    union(body, flange)
    return body


def make_ref_horn():
    return horn_solid("ref_horn", 0.0, P.SG.HORN_ARM_T)


def make_ref_wire():
    return box(-0.026, -0.018, P.SG.BODY_CENTER_X + P.SG.BODY_L / 2,
               P.SG.BODY_CENTER_X + P.SG.BODY_L / 2 + P.SG.WIRE_LENGTH,
               P.SERVO_AXIS_Z - P.SG.WIRE_W / 2, P.SERVO_AXIS_Z + P.SG.WIRE_W / 2,
               "ref_wire")


def make_fit_horn():
    outer = horn_solid("fit_horn", 0, 0.003, P.HORN_CLEARANCE, P.HORN_RECEIVER_WALL)
    inner = horn_solid("fit_horn_inner", -0.0005, 0.0035, P.HORN_CLEARANCE, 0)
    cut(outer, inner)
    return outer


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
    for i in range(P.GRID_N):
        parts[f"cam_{i}"] = make_cam(i)
    parts["cam_gear"] = make_cam_gear()
    parts["drive_gear"] = make_drive_gear()
    parts["cap_left"] = make_cap("cap_left", -1)
    parts["cap_right"] = make_cap("cap_right", 1)
    parts["servo_clip"] = make_servo_clip()
    parts["fit_horn"] = make_fit_horn()
    parts["fit_bearing"] = make_fit_bearing()
    parts["ref_servo"] = make_ref_servo()
    parts["ref_horn"] = make_ref_horn()
    parts["ref_wire"] = make_ref_wire()

    for ob in parts.values():
        prepare_mesh(ob)

    labels = {
        "shell": "箱本体", "top_frame": "天面案内板", "camshaft": "六角カム軸", "cam_gear": "従動歯車",
        "drive_gear": "ホーン受け付き駆動歯車", "cap_left": "左軸端キャップ",
        "cap_right": "右軸端キャップ", "servo_clip": "サーボ押さえ",
        "fit_horn": "ホーン受け試片", "fit_bearing": "軸受け試片",
        "ref_servo": "SG92R本体", "ref_horn": "SG92R付属ホーン", "ref_wire": "SG92R配線",
    }
    for i in range(P.GRID_N):
        labels[f"carrier_{i}"] = f"格子列 {i + 1}"
        labels[f"cam_{i}"] = f"偏心カム {i + 1}"

    printable = {name for name in parts if not name.startswith("ref_")}
    flip_carrier = Matrix.Translation((0, 0, P.CARRIER_TOP_Z)) @ Matrix.Rotation(math.pi, 4, "Y")
    flat_x = Matrix.Rotation(math.pi / 2, 4, "Y")
    for name, ob in parts.items():
        if name in printable:
            if name.startswith("carrier_"):
                matrix = flip_carrier
            elif name == "top_frame":
                matrix = Matrix.Translation((0, 0, P.CUBE_H)) @ Matrix.Rotation(math.pi, 4, "Y")
            elif name.startswith("cam_") or name in {"drive_gear", "cap_left", "cap_right",
                          "fit_horn", "fit_bearing"}:
                matrix = flat_x
            elif name == "servo_clip":
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
        elif name.startswith("cam_") and name != "cam_gear":
            column = int(name.rsplit("_", 1)[1])
            explode = [(column - 2) * 6, 0, 0]
        elif name in {"cam_gear", "drive_gear"}:
            explode = [0, -30, 0]
        elif name == "cap_left":
            explode = [-50, 0, 0]
        elif name == "cap_right":
            explode = [50, 0, 0]
        elif name == "servo_clip":
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
                "SG92Rを上から着座レールへ入れ、配線を前面の8×4mm出口へ通す。",
                "サーボを90°へ動かし、付属ホーンの長腕左側と駆動歯車の三角印を合わせて押し込む。",
                "サーボ押さえを上から差し込み、左右の脚を着座レールの外側へ掛ける。",
                "5個のカムと従動歯車を位相順に箱内へ置き、右側から六角軸を通す。",
                "軸端キャップを両側から押し込み、0.3mmの軸方向遊びを確認する。",
                "5本の列キャリアを上から前後ガイドへ落とし、低位置ストップへ着座させる。",
                "天面案内板を格子列の周囲へ下ろし、内側の4辺の棚へ着座させる。",
                "15°へ低速移動して全列が面一になることを確認し、90°へ低速で戻して待機する。",
                "シリアルgで15〜165°を片道2秒のquintic補間で往復させる。",
            ],
            "decisions": [
                "ホーン全角度包絡と3mm床を両立するため外形を80mm角にした。",
                "サーボ軸Z=23.5mm、カム軸Z=53.7mm、中心距離30.2mmとした。",
                "ホーン受けは歯面よりX負側へ分離し、六角軸と非対称三角印で位相を固定した。",
                "カム軸の軸受け区間も対辺5mmの六角とし、平面印刷と0.21mmの頂点隙間を両立した。",
                "天面案内板は見える面を平面印刷する別部品とし、筐体側の棚を45度斜面で支えた。",
            ],
            "limitations": [
                "天面を上にした卓上姿勢専用。復帰は重力に依存する。",
                "SG92Rホーンの長さ配分と穴位置には写真由来の推定値があるため試片を先に刷る。",
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
