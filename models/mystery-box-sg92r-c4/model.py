"""SG92R一台で19枚の六角面を3段階に持ち上げる住人の箱 C4。

形はmmで組み立てる。build/*.stl はそのままmmで保存する。
exports/ はmへ戻してから blender_utils.export_stl() で保存する。
"""

from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../.."))
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.path.insert(0, HERE)

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

from blender_utils import EXPORTS_DIR, clear_scene, export_stl  # noqa: E402
from printmech.geometry import (  # noqa: E402
    boolean, box, circle, clean, cut, cyl_x, hull, nonmanifold, prism,
    rrect, transform, union, volume,
)
import motion  # noqa: E402
import params as P  # noqa: E402

MM = 1000.0
BUILD = os.path.join(HERE, "build")
HALF = P.CUBE * MM / 2.0
INNER = HALF - P.WALL * MM
TOP_Z0 = (P.CUBE - P.TOP_T) * MM
WEB_Z0 = P.WEB_Z0 * MM
WEB_Z1 = WEB_Z0 + P.WEB_T * MM


def mm(value):
    return value * MM


def hex_poly(cx, cy, flat, n=6):
    radius = flat / math.sqrt(3.0)
    return [(cx + radius * math.cos(math.radians(30 + 360 * i / n)),
             cy + radius * math.sin(math.radians(30 + 360 * i / n))) for i in range(n)]


def lattice_centers():
    out = {0: [], 1: [], 2: []}
    pitch = mm(P.HEX_PITCH)
    for q in range(-2, 3):
        for r in range(-2, 3):
            ring = max(abs(q), abs(r), abs(-q - r))
            if ring <= 2:
                out[ring].append((pitch * (q + r / 2.0), pitch * math.sqrt(3.0) * r / 2.0))
    for ring in out:
        out[ring].sort(key=lambda p: math.atan2(p[1], p[0]))
    return out


CENTERS = lattice_centers()


def duplicate(ob, name):
    copy = ob.copy()
    copy.data = ob.data.copy()
    copy.name = name
    bpy.context.collection.objects.link(copy)
    return copy


def bbox(ob):
    pts = [ob.matrix_world @ Vector(corner) for corner in ob.bound_box]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    return [[round(x, 3) for x in lo], [round(x, 3) for x in hi]]


def capsule_xy(a, b, radius, z0, z1, name):
    poly = hull(circle(a, radius, 24) + circle(b, radius, 24))
    return prism(poly, "z", z0, z1, name)


def cut_collection(target, cutters, name):
    """重なるカッターを一度のEXACT差分へ渡し、中間面を残さない。"""
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    for cutter in cutters:
        collection.objects.link(cutter)
    modifier = target.modifiers.new(name, "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.operand_type = "COLLECTION"
    modifier.collection = collection
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    for cutter in cutters:
        bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.data.collections.remove(collection)
    clean(target)
    return target


def rect_yz_between(a, b, width):
    dy, dz = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dy, dz)
    ny, nz = -dz / length * width / 2, dy / length * width / 2
    return [(a[0] + ny, a[1] + nz), (b[0] + ny, b[1] + nz),
            (b[0] - ny, b[1] - nz), (a[0] - ny, a[1] - nz)]


def save_stl(objects, path):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True, global_scale=1.0)


def triangulate_for_export(ob):
    if ob.name.startswith("servo_"):
        # 正本STLは三角形で水密。通常部品用の距離結合で近接頂点を潰さない。
        return
    bpy.context.view_layer.objects.active = ob
    modifier = ob.modifiers.new("export_triangulate", "TRIANGULATE")
    modifier.quad_method = "BEAUTY"
    modifier.ngon_method = "BEAUTY"
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    # 円筒と角柱を結合した保持具だけは、0.1µm量子化で潰れるスリバーを除く。
    clean(ob, dist=1e-3 if ob.name == "bearing_keeper" else 1e-4)


def validate_reference_mesh(ob):
    """正本STLの変換後に重複面と零面積面がないことを確認する。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    bm.faces.ensure_lookup_table()
    seen = set()
    duplicate_faces = 0
    zero_area_faces = 0
    for face in bm.faces:
        key = tuple(sorted(vertex.index for vertex in face.verts))
        zero_area_faces += len(set(key)) < 3
        duplicate_faces += key in seen
        seen.add(key)
    bm.free()
    if duplicate_faces or zero_area_faces:
        raise RuntimeError(
            f"{ob.name}: canonical reference has duplicate_faces={duplicate_faces}, "
            f"zero_area_faces={zero_area_faces} after transform")


def cleanup_wire_reference(ob):
    """配線端面の同一直線上にある中間頂点を溶解し、外形を保ったまま零面積面を除く。"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    target_points = (
        Vector((14.5, 0.5935106873512268, 5.3733062744140625)),
        Vector((14.5, 0.585004448890686, 5.364799976348877)),
        Vector((14.5, 0.4624224901199341, 5.242218017578125)),
    )

    def matches_target(face):
        return len(face.verts) == 3 and all(
            any((vertex.co - point).length <= 1e-5 for vertex in face.verts)
            for point in target_points)

    target_faces = [face for face in bm.faces if matches_target(face)]
    if len(target_faces) != 1:
        bm.free()
        raise RuntimeError(
            f"{ob.name}: expected one canonical zero-area triangle, found {len(target_faces)}")

    middle = None
    vertices = list(target_faces[0].verts)
    for candidate in vertices:
        endpoints = [vertex for vertex in vertices if vertex is not candidate]
        segment = endpoints[1].co - endpoints[0].co
        if segment.length_squared == 0:
            continue
        t = (candidate.co - endpoints[0].co).dot(segment) / segment.length_squared
        closest = endpoints[0].co + t * segment
        if 1e-6 < t < 1.0 - 1e-6 and (candidate.co - closest).length <= 1e-6:
            middle = candidate
            break
    if middle is None:
        bm.free()
        raise RuntimeError(f"{ob.name}: zero-area triangle has no collinear middle vertex")

    bmesh.ops.dissolve_verts(
        bm, verts=[middle], use_face_split=False, use_boundary_tear=False)
    bm.normal_update()
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def write_json(path, data):
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(temp, path)


def build_guide_sleeve(cx, cy, name):
    lug = mm(P.GUIDE_LUG)
    gap = mm(P.GUIDE_CLEARANCE)
    wall = mm(P.GUIDE_WALL)
    inner = lug + 2 * gap
    outer = inner + 2 * wall
    z0, z1 = mm(P.GUIDE_Z0), mm(P.GUIDE_Z1) + 0.25
    walls = {
        "l": box(cx - outer / 2, cx - inner / 2, cy - outer / 2, cy + outer / 2, z0, z1, name + "_l"),
        "r": box(cx + inner / 2, cx + outer / 2, cy - outer / 2, cy + outer / 2, z0, z1, name + "_r"),
        "b": box(cx - inner / 2, cx + inner / 2, cy - outer / 2, cy - inner / 2, z0, z1, name + "_b"),
        "f": box(cx - inner / 2, cx + inner / 2, cy + inner / 2, cy + outer / 2, z0, z1, name + "_f"),
    }
    # 連結腕が上下する内向き面だけ開ける。対向する2個のC案内で残る3方向を拘束する。
    if abs(cx) < 1.0 and abs(cy) < 10.0:
        omit = "r"
    else:
        omit = ("l" if cx > 0 else "r") if abs(cx) > abs(cy) else ("b" if cy > 0 else "f")
    keep = [ob for key, ob in walls.items() if key != omit]
    sleeve = keep.pop(0)
    sleeve.name = name
    union(sleeve, *keep)
    return sleeve


GUIDES = {
    0: [(mm(P.CENTER_GUIDE_X), -5.4), (mm(P.CENTER_GUIDE_X), 5.4)],
    1: [(-6.6, 12.0), (6.6, 12.0)],
    2: [(0.0, -30.5), (0.0, 30.5)],
}


def build_guide_frame():
    z0 = mm(P.GUIDE_Z0)
    z1 = z0 + mm(P.GUIDE_FRAME_T)
    rail = mm(P.GUIDE_FRAME_RAIL)
    edge = 35.35
    frame = box(-edge, edge, -edge, -edge + rail, z0, z1, "guide_frame")
    union(frame,
          box(-edge, edge, edge - rail, edge, z0, z1, "frame_front"),
          box(-edge, -edge + rail, -edge, edge, z0, z1, "frame_left"),
          box(edge - rail, edge, -edge, edge, z0, z1, "frame_right"))
    # 天板爪の通路で外周枠を切るため、その内側を2mmの迂回梁で連続させる。
    for y in (-12.0, 12.0):
        union(frame,
              box(-32.0, -30.0, y - 4.3, y + 4.3, z0, z1, "frame_tab_bypass_l"),
              box(30.0, 32.0, y - 4.3, y + 4.3, z0, z1, "frame_tab_bypass_r"))
    # 中心案内の腕は従動柱のY=±4mm包絡より外を通して左枠へつなぐ。
    for gy in (-8.5, 8.5):
        union(frame, box(-edge + rail - 0.2, -4.3, gy - rail / 2, gy + rail / 2,
                         z0, z1, "center_guide_arm"))
    # 内環案内は前枠へ、外環案内は前後枠へ最短でつなぐ。
    for gx in (-6.6, 6.6):
        union(frame, box(gx - rail / 2, gx + rail / 2, 16.85, edge - rail + 0.2,
                         z0, z1, "inner_guide_arm"))
    # 外環案内の外側壁は前後の外周枠へ直接0.85mm重なる。
    for group in range(3):
        for index, (gx, gy) in enumerate(GUIDES[group]):
            union(frame, build_guide_sleeve(gx, gy, f"guide_{group}_{index}"))
    # 天板の4本の保持爪が外周枠を通る位置だけ、片側0.3mmを加えて抜く。
    for side in (-1, 1):
        for y in (-12.0, 12.0):
            x0, x1 = ((32.0, 35.6) if side > 0 else (-35.6, -32.0))
            cut(frame, box(x0, x1, y - 4.3, y + 4.3, z0 - 0.2, z1 + 0.2,
                           "face_tab_clearance"))
            # 切欠き境界の三角形状の細片を、通路外側の1.2mm角で受ける。
            rx0, rx1 = ((30.0, 32.6) if side > 0 else (-32.6, -30.0))
            union(frame,
                  box(rx0, rx1, y - 5.5, y - 4.3, z0, z1, "face_tab_edge_support"),
                  box(rx0, rx1, y + 4.3, y + 5.5, z0, z1, "face_tab_edge_support"))
    frame.name = "guide_frame"
    return frame


def build_housing():
    wall = mm(P.WALL)
    top = box(-HALF, -INNER, -HALF, HALF, 0, TOP_Z0, "housing")
    union(top,
          box(INNER, HALF, -HALF, HALF, 0, TOP_Z0, "wall_r"),
          box(-INNER, INNER, -HALF, -INNER, 0, TOP_Z0, "wall_b"),
          box(-INNER, INNER, INNER, HALF, 0, TOP_Z0, "wall_f"))

    # SG92R tray. Source body maps to X[-36,-14], Y[-16.5,6.5], Z[34,46].
    sx0 = mm(P.SERVO_X0)
    sx1 = sx0 + mm(P.SG.BODY_H)
    sy0 = mm(P.SG.BODY_CENTER_X - P.SG.BODY_L / 2 + P.SERVO_Y_OFFSET)
    sy1 = mm(P.SG.BODY_CENTER_X + P.SG.BODY_L / 2 + P.SERVO_Y_OFFSET)
    sz0 = mm(P.SERVO_Z - P.SG.BODY_W / 2)
    tray_t = mm(P.SERVO_TRAY_T)
    clr = mm(P.SERVO_CLR)
    # 底を塞がず、サーボを下から通す。取付耳が通るX[-19.5,-16.5]は側柵も切る。
    for xa, xb in ((-INNER - 0.2, -19.5), (-16.5, sx1 + 0.8)):
        union(top,
              box(xa, xb, sy0 - clr - tray_t, sy0 - clr, sz0 - 0.5, sz0 + 8.0, "servo_rail_b"),
              box(xa, xb, sy1 + clr, sy1 + clr + tray_t, sz0 - 0.5, sz0 + 8.0, "servo_rail_f"))
        # 長い空中橋を作らず、壁と縦リブの直上にある四隅の短いタブだけで上面を止める。
        tab_w = 3.0
        for tx0, tx1 in ((xa, min(xa + tab_w, xb)), (max(xb - tab_w, xa), xb)):
            union(top,
                  box(tx0, tx1, sy0 - clr, sy0 + 2.8, sz0 + mm(P.SG.BODY_W) + clr,
                      sz0 + mm(P.SG.BODY_W) + clr + tray_t, "servo_stop_b"),
                  box(tx0, tx1, sy1 - 2.8, sy1 + clr, sz0 + mm(P.SG.BODY_W) + clr,
                      sz0 + mm(P.SG.BODY_W) + clr + tray_t, "servo_stop_f"))

    # レール自由端を外壁から立ち上げた縦リブへつなぐ。底から刷っても空中に始まらない。
    support_xs = ((-21.9, -19.5), (sx1 - 1.6, sx1 + 0.8))
    support_top = sz0 + mm(P.SG.BODY_W) + clr + tray_t
    for xa, xb in support_xs:
        union(top,
              box(xa, xb, -INNER - 0.2, sy0 - clr, 0, support_top, "servo_rib_b"),
              box(xa, xb, sy1 + clr, INNER + 0.2, 0, support_top, "servo_rib_f"))
    # 左壁から最初の縦リブまでの橋を6.5mm以下へ分ける。サーボ包絡の外だけを通す。
    mid_x0, mid_x1 = -33.4, -31.0
    union(top,
          box(mid_x0, mid_x1, sy0 - clr - tray_t, sy0 - clr, 0, sz0 + 8.0, "servo_post_b"),
          box(-INNER - 0.2, mid_x1, sy0 - clr - tray_t, sy0 - clr, 0, tray_t, "servo_foot_b"),
          box(mid_x0, mid_x1, sy1 + clr, sy1 + clr + tray_t, 0, sz0 + 8.0, "servo_post_f"),
          box(-INNER - 0.2, mid_x1, sy1 + clr, sy1 + clr + tray_t, 0, tray_t, "servo_foot_f"))

    # 配線は正本の+X側（この組立では+Y）へ出す。
    cut(top, box(sx0 + 2.0, sx0 + 2.0 + mm(P.WIRE_EXIT_W), sy1, HALF + 0.5,
                 mm(P.SERVO_Z - P.WIRE_EXIT_H / 2), mm(P.SERVO_Z + P.WIRE_EXIT_H / 2), "wire_exit"))

    # 右端の軸受け。主軸は+X側から通し、外面と面一の回転式keeperで閉じる。
    bx = mm(P.BEARING_X[0])
    bt = mm(P.BEARING_T)
    ro = mm(P.BEARING_OUT_R)
    ri = mm(P.CAM_SHAFT_R + P.BEARING_CLEARANCE)
    support = box(bx - bt / 2, INNER + 0.2, -ro, ro,
                  mm(P.CAM_AXIS_Z) - ro, mm(P.CAM_AXIS_Z) + ro, "bearing_support")
    union(top, support)
    # 軸受け下面の壁側3.8mmを45度面で受け、片持ちの水平開始を作らない。
    bearing_z0 = mm(P.CAM_AXIS_Z) - ro
    gusset = mm(P.BEARING_PRINT_GUSSET)
    gusset_x1 = INNER + 0.2
    gusset_poly = [(gusset_x1 - gusset, bearing_z0),
                    (gusset_x1, bearing_z0 - gusset),
                    (gusset_x1, bearing_z0)]
    union(top,
          prism(gusset_poly, "y", ro - 2.8, ro + 0.2, "bearing_print_gusset_f"),
          prism(gusset_poly, "y", -ro - 0.2, -ro + 2.8, "bearing_print_gusset_b"))
    cut(top, cyl_x((0, mm(P.CAM_AXIS_Z)), ri, bx - bt, HALF + 0.5, 64, "bearing_bore"))
    # keeper本体の穴、保持爪の全回転包絡、挿入時だけ使う左右のキー溝。
    cut(top,
        cyl_x((0, mm(P.CAM_AXIS_Z)), 5.8, bx + bt / 2 - 0.1, HALF + 0.5, 64, "keeper_body_bore"))
    cut(top, cyl_x((0, mm(P.CAM_AXIS_Z)), ro + 0.25,
                   34.0, 35.9, 96, "keeper_turn_sweep"))
    for sign in (-1, 1):
        cut(top, box(bx + bt / 2 - 0.1, HALF + 0.5,
                     sign * 5.2 - 1.75, sign * 5.2 + 1.75,
                     mm(P.CAM_AXIS_Z) - 1.75, mm(P.CAM_AXIS_Z) + 1.75,
                     "keeper_keyway"))

    # 45度位置の板ばねが保持具外周を0.15mm押し、90度位置の凹みへ戻る。
    detent_angle = math.radians(P.KEEPER_DETENT_ANGLE_DEG)
    radial = (math.cos(detent_angle), math.sin(detent_angle))
    tangent = (-radial[1], radial[0])
    arm_t = mm(P.KEEPER_DETENT_ARM_T)
    arm_l = mm(P.KEEPER_DETENT_ARM_L)
    tip_r = 5.5 - mm(P.KEEPER_DETENT_INTERFERENCE) + arm_t / 2
    tip = (radial[0] * tip_r, mm(P.CAM_AXIS_Z) + radial[1] * tip_r)
    free_anchor = (tip[0] - tangent[0] * arm_l, tip[1] - tangent[1] * arm_l)
    beam_anchor = (free_anchor[0] - tangent[0] * 0.5,
                   free_anchor[1] - tangent[1] * 0.5)
    pocket_tip = (tip[0] + tangent[0] * 0.4, tip[1] + tangent[1] * 0.4)
    cut(top, prism(rect_yz_between(free_anchor, pocket_tip, arm_t + 0.6), "x",
                   INNER - 0.2, HALF + 0.2, "keeper_detent_clearance"))
    union(top, prism(rect_yz_between(beam_anchor, tip, arm_t), "x",
                     INNER, HALF, "keeper_detent_spring"))

    # 底板の4本の爪が掛かる凹み。
    hook_z0 = mm(P.BOTTOM_T + P.BOTTOM_TAB_L) - 2.2
    hook_z1 = hook_z0 + 2.4
    for y in (-12.0, 12.0):
        cut(top, box(-HALF - 0.2, -INNER + 1.0, y - 4.2, y + 4.2, hook_z0, hook_z1, "bottom_notch_l"))
        cut(top, box(INNER - 1.0, HALF + 0.2, y - 4.2, y + 4.2, hook_z0, hook_z1, "bottom_notch_r"))
    # 天板の4本の爪が掛かる凹み。
    for y in (-12.0, 12.0):
        cut(top, box(-HALF - 0.2, -INNER + 1.0, y - 4.2, y + 4.2, 59.0, 63.3, "face_notch_l"))
        cut(top, box(INNER - 1.0, HALF + 0.2, y - 4.2, y + 4.2, 59.0, 63.3, "face_notch_r"))
    # 独立案内枠を四隅で受ける。枠下面と面一で、組立後は格子の案内柱が抜け止めになる。
    for x in (-33.0, 33.0):
        for y in (-33.0, 33.0):
            xa, xb = ((-INNER - 0.2, x + 2.0) if x < 0 else
                      (x - 2.0, INNER + 0.2))
            union(top, box(xa, xb, y - 2.0, y + 2.0,
                           57.5, mm(P.GUIDE_Z0), "guide_frame_seat"))
            wedge = ([(-INNER - 0.2, 52.7), (x + 2.0, 57.7), (-INNER - 0.2, 57.7)]
                     if x < 0 else
                     [(INNER + 0.2, 52.7), (INNER + 0.2, 57.7), (x - 2.0, 57.7)])
            union(top, prism(wedge, "y", y - 2.0, y + 2.0, "guide_frame_seat_gusset"))
    # サーボ保持具が底から通る区間。保持台は前後に残し、クリップ自身で本体下面を受ける。
    cut(top, box(-30.3, -23.2, -22.2, 12.2, -0.5, 37.9, "servo_clip_passage"))
    top.name = "housing"
    return top


def build_faceplate():
    face = box(-HALF, HALF, -HALF, HALF, TOP_Z0, mm(P.CUBE), "faceplate")
    for center in sum(CENTERS.values(), []):
        cut(face, prism(hex_poly(*center, mm(P.HEX_OPEN_FLAT)), "z",
                        TOP_Z0 - 0.6, mm(P.CUBE) + 0.6, "hex_open"))
    # 側壁内へ下ろす4本の着脱爪。外形の継ぎ目はz=74mmの一本だけになる。
    tab_t, tab_l, hook = 1.8, 14.0, 0.7
    x_inner = INNER - mm(P.BOTTOM_GAP)
    for side in (-1, 1):
        x = side * (x_inner - tab_t / 2)
        for y in (-12.0, 12.0):
            union(face, box(x - tab_t / 2, x + tab_t / 2, y - 4.0, y + 4.0,
                            TOP_Z0 - tab_l, TOP_Z0 + 0.2, "face_tab"))
            xo = x + side * hook / 2
            union(face, box(xo - (tab_t + hook) / 2, xo + (tab_t + hook) / 2,
                            y - 4.0, y + 4.0, TOP_Z0 - tab_l + 1.0,
                            TOP_Z0 - tab_l + 3.0, "face_hook"))
    face.name = "faceplate"
    return face


def build_carrier(group):
    centers = CENTERS[group]
    stem_r = mm(P.STEM_D) / 2
    web_r = mm(P.WEB_W) / 2
    cap_z1 = mm(P.HEX_HOME_TOP)
    cap_z0 = cap_z1 - mm(P.HEX_CAP_T)
    if group == 0:
        carrier = prism(circle(centers[0], 4.4, 48), "z", WEB_Z0, WEB_Z1, "carrier_center")
    else:
        carrier = capsule_xy(centers[0], centers[1], web_r, WEB_Z0, WEB_Z1, f"carrier_{group}")
        ring_edges = list(zip(centers, centers[1:] + centers[:1]))
        for a, b in ring_edges[1:]:
            union(carrier, capsule_xy(a, b, web_r, WEB_Z0, WEB_Z1, "ring_web"))
    for i, center in enumerate(centers):
        face = prism(hex_poly(*center, mm(P.HEX_CAP_FLAT)), "z", cap_z0, cap_z1, f"face_{i}")
        union(carrier, face)
        # 3本の柱を環の裏へ置き、中央の六角穴を下まで見通せるようにする。
        for k in range(3):
            angle = math.radians(30 + 120 * k)
            stem_center = (center[0] + 4.2 * math.cos(angle), center[1] + 4.2 * math.sin(angle))
            stem = prism(circle(stem_center, stem_r, 28), "z",
                         WEB_Z0 - 0.2, cap_z0 + 0.2, f"stem_{i}_{k}")
            boolean(stem, prism(hex_poly(*center, mm(P.STEM_OUTER_FLAT)), "z",
                                WEB_Z0 - 0.4, cap_z0 + 0.4,
                                f"stem_clip_{i}_{k}"), "INTERSECT")
            union(carrier, stem)
    if group == 0:
        helper = tuple(mm(value) for value in P.CENTER_CAP_PRINT_SUPPORT)
        union(carrier, prism(circle(helper, mm(P.CENTER_CAP_PRINT_SUPPORT_D) / 2, 24), "z",
                              WEB_Z0 - 0.2, cap_z0 + 0.2,
                              "center_cap_print_support"))

    # 対向2点の長い角柱案内。片側のパッド荷重でも傾きにくい。
    anchor = centers[0]
    for i, (gx, gy) in enumerate(GUIDES[group]):
        nearest = min(centers, key=lambda p: (p[0] - gx) ** 2 + (p[1] - gy) ** 2)
        if group == 0:
            elbow = (3.0, gy)
            union(carrier,
                  capsule_xy(nearest, elbow, web_r, WEB_Z0, WEB_Z1, f"guide_arm_{i}_a"),
                  capsule_xy(elbow, (gx, gy), web_r, WEB_Z0, WEB_Z1, f"guide_arm_{i}_b"))
        else:
            union(carrier, capsule_xy(nearest, (gx, gy), web_r, WEB_Z0, WEB_Z1, f"guide_arm_{i}"))
        union(carrier, box(gx - mm(P.GUIDE_LUG) / 2, gx + mm(P.GUIDE_LUG) / 2,
                           gy - mm(P.GUIDE_LUG) / 2, gy + mm(P.GUIDE_LUG) / 2,
                           mm(P.GUIDE_LUG_Z0), WEB_Z1, f"guide_lug_{i}"))

    # 偏心カムに直接載る水平パッドと、カム円板の両側を通る2本の柱。
    cx = mm(P.CAM_X[group])
    low = mm(P.CAM_AXIS_Z + P.CAM_R + P.CAM_E[group] * math.sin(math.radians(P.CAM_THETA_MIN_DEG)))
    pad_top = low + mm(P.FOLLOWER_PAD_T)
    pad_x0, pad_x1 = ((cx - 2.0, mm(P.CENTER_FOLLOWER_PAD_X1)) if group == 0 else
                      (cx - mm(P.FOLLOWER_PAD_X) / 2, cx + mm(P.FOLLOWER_PAD_X) / 2))
    union(carrier, box(pad_x0, pad_x1,
                       -mm(P.FOLLOWER_PAD_Y) / 2, mm(P.FOLLOWER_PAD_Y) / 2,
                       low, pad_top, "follower_pad"))
    if group == 0:
        # 中央だけY方向へ二分し、右端を内環webから0.3mm離す。
        px = cx + mm(P.CENTER_FOLLOWER_POST_OFFSET_X)
        for py in (-2.5, 2.5):
            union(carrier, box(px - mm(P.FOLLOWER_POST_T) / 2, px + mm(P.FOLLOWER_POST_T) / 2,
                               py - mm(P.FOLLOWER_POST_T) / 2, py + mm(P.FOLLOWER_POST_T) / 2,
                               pad_top - 0.2, WEB_Z0 + 0.2, "follower_post"))
    else:
        for px in (cx - mm(P.FOLLOWER_POST_OFFSET_X), cx + mm(P.FOLLOWER_POST_OFFSET_X)):
            union(carrier, box(px - mm(P.FOLLOWER_POST_T) / 2, px + mm(P.FOLLOWER_POST_T) / 2,
                               -mm(P.FOLLOWER_PAD_Y) / 2, mm(P.FOLLOWER_PAD_Y) / 2,
                               pad_top - 0.2, WEB_Z0 + 0.2, "follower_post"))

    # すべての支柱と案内を結合した後に穴を開け直し、連結板の下部だけを残す。
    hole_cutters = [
        prism(hex_poly(*center, mm(P.HEX_HOLE_FLAT)), "z",
              mm(P.HOLE_CLEAR_Z0), mm(P.HOLE_CLEAR_Z1),
              f"final_hole_clear_{i}")
        for i, center in enumerate(centers)
    ]
    cut_collection(carrier, hole_cutters, f"carrier_{group}_hole_clears")
    carrier.name = ("carrier_center", "carrier_inner", "carrier_outer")[group]
    return carrier


def rotated_poly(poly, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(c * y - s * z, s * y + c * z) for y, z in poly]


def horn_shapes(clearance):
    sg = P.SG
    tip = mm(sg.HORN_TIP_W) / 2 + clearance
    root = mm(sg.HORN_ROOT_W) / 2 + clearance
    hub = mm(sg.HORN_HUB_DIA) / 2 + clearance
    left = mm(sg.HORN_LEFT_X) - clearance
    right = mm(sg.HORN_RIGHT_X) + clearance
    root_x = mm(sg.HORN_HUB_DIA) / 2
    left_arm = hull(circle((left + tip, 0), tip, 24) +
                    [(-root_x, -root), (-root_x, root), (0, -root), (0, root)])
    right_arm = hull(circle((right - tip, 0), tip, 24) +
                     [(root_x, -root), (root_x, root), (0, -root), (0, root)])
    sl = mm(sg.HORN_SPAN_Y) / 2 + clearance
    sw = mm(sg.HORN_SHORT_W) / 2 + clearance
    short = hull(circle((0, sl - sw), sw, 24) + circle((0, -sl + sw), sw, 24))
    return [left_arm, right_arm, short, circle((0, 0), hub, 48)]


def horn_world_poly(poly, clearance_deg=P.HORN_HOME_DEG):
    return [(y, z + mm(P.CAM_AXIS_Z)) for y, z in rotated_poly(poly, clearance_deg)]


def hex_yz(flat, cy=0.0, cz=0.0):
    radius = flat / math.sqrt(3.0)
    return [(cy + radius * math.cos(math.radians(60 * i)),
             cz + radius * math.sin(math.radians(60 * i))) for i in range(6)]


def build_camshaft():
    # 主軸は横向き印刷する。8mm盲穴より右の中実部だけをヨーク用に細くする。
    shaft = prism(hex_yz(mm(P.CAM_SHAFT_FLAT), 0, mm(P.CAM_AXIS_Z)), "x",
                  mm(P.COUPLER_X1),
                  mm(P.CAM_SHAFT_X1), "camshaft")
    cut(shaft, prism(hex_yz(mm(P.SHAFT_JOINT_SOCKET_FLAT), 0, mm(P.CAM_AXIS_Z)), "x",
                     mm(P.COUPLER_X1) - 0.5,
                     mm(P.COUPLER_X1 + P.SHAFT_JOINT_L) + 0.2, "shaft_joint_socket"))
    groove_cutter = box(mm(P.JOINT_SHAFT_GROOVE_X0), mm(P.JOINT_SHAFT_GROOVE_X1),
                        -6.0, 6.0, mm(P.CAM_AXIS_Z) - 6.0, mm(P.CAM_AXIS_Z) + 6.0,
                        "joint_keeper_groove_cutter")
    cut(groove_cutter, cyl_x((0, mm(P.CAM_AXIS_Z)), mm(P.JOINT_SHAFT_GROOVE_D) / 2,
                             mm(P.JOINT_SHAFT_GROOVE_X0) - 0.2,
                             mm(P.JOINT_SHAFT_GROOVE_X1) + 0.2, 64,
                             "joint_keeper_groove_core"))
    cut(shaft, groove_cutter)
    shaft.name = "camshaft"
    return shaft


def build_horn_coupler():
    # 受け本体を面で置く。保持溝の両側へ1.2mmの円形肩を残す。
    wall = 2.4
    outer = horn_shapes(mm(P.HORN_CLEARANCE) + wall)
    socket_x1 = mm(P.JOINT_COUPLER_GROOVE_X0)
    coupler = prism(horn_world_poly(outer[0]), "x", mm(P.COUPLER_X0),
                    socket_x1, "horn_coupler")
    for poly in outer[1:]:
        union(coupler, prism(horn_world_poly(poly), "x", mm(P.COUPLER_X0),
                             socket_x1, "coupler_lobe"))
    union(coupler, cyl_x((0, mm(P.CAM_AXIS_Z)), mm(P.JOINT_COUPLER_SHOULDER_R),
                         mm(P.JOINT_COUPLER_SHOULDER_X0),
                         mm(P.JOINT_COUPLER_SHOULDER_X1), 64,
                         "coupler_keeper_shoulders"))
    union(coupler, prism(hex_yz(mm(P.SHAFT_JOINT_FLAT), 0, mm(P.CAM_AXIS_Z)), "x",
                         mm(P.COUPLER_X1) - 0.2,
                         mm(P.COUPLER_X1 + P.SHAFT_JOINT_L), "shaft_joint_peg"))

    cutters = []
    for poly in horn_shapes(mm(P.HORN_CLEARANCE)):
        cutters.append(prism(horn_world_poly(poly), "x", mm(P.COUPLER_X0) - 0.5,
                             mm(P.HORN_POCKET_X1), "horn_pocket"))
    mouth = horn_shapes(mm(P.HORN_CLEARANCE + P.HORN_MOUTH_EXTRA))
    for poly in mouth:
        cutters.append(prism(horn_world_poly(poly), "x", mm(P.COUPLER_X0) - 0.6,
                             mm(P.COUPLER_X0) + 0.3, "horn_mouth"))
    groove = box(mm(P.JOINT_COUPLER_GROOVE_X0), mm(P.JOINT_COUPLER_GROOVE_X1),
                 -40.0, 40.0, 0.0, 80.0,
                 "coupler_keeper_groove")
    cut(groove, cyl_x((0, mm(P.CAM_AXIS_Z)), mm(P.JOINT_COUPLER_GROOVE_R),
                      mm(P.JOINT_COUPLER_GROOVE_X0) - 0.2,
                      mm(P.JOINT_COUPLER_GROOVE_X1) + 0.2, 64,
                      "coupler_keeper_groove_core"))
    cutters.append(groove)
    # 外周短腕の先端だけを削り、横軸印刷で使う2mm以上の壁と接地平面を両立する。
    outer_bottom = min(point[1] for poly in outer for point in poly)
    flat_cut = [(-100.0, -100.0), (100.0, -100.0),
                (100.0, outer_bottom + mm(P.COUPLER_PRINT_FLAT)),
                (-100.0, outer_bottom + mm(P.COUPLER_PRINT_FLAT))]
    cutters.append(prism(horn_world_poly(flat_cut), "x", mm(P.COUPLER_X0) - 0.5,
                         mm(P.COUPLER_X1) + 0.5, "coupler_print_flat"))
    cut_collection(coupler, cutters, "horn_coupler_voids")
    coupler.name = "horn_coupler"
    return coupler


def build_joint_keeper():
    """底から入れ、ホーン受けの肩と主軸の中実溝を捕える静止二股ヨーク。"""
    zc = mm(P.CAM_AXIS_Z)

    def fork(x0, x1, slot_r, outer_r, name):
        part = cyl_x((0, zc), outer_r, x0, x1, 64, name)
        cut(part,
            cyl_x((0, zc), slot_r, x0 - 0.2, x1 + 0.2, 64, name + "_round_slot"),
            box(x0 - 0.2, x1 + 0.2, -slot_r, slot_r,
                zc, zc + outer_r + 0.2, name + "_open_top"))
        return part

    left = fork(mm(P.JOINT_KEEPER_LEFT_X0), mm(P.JOINT_KEEPER_LEFT_X1),
                mm(P.JOINT_COUPLER_GROOVE_R) + 0.3,
                mm(P.JOINT_COUPLER_GROOVE_R) + 3.3, "joint_keeper_left_fork")
    right = fork(mm(P.JOINT_KEEPER_RIGHT_X0), mm(P.JOINT_KEEPER_RIGHT_X1),
                 mm(P.JOINT_KEEPER_RIGHT_SLOT_R),
                 mm(P.JOINT_KEEPER_RIGHT_SLOT_R) + 3.0, "joint_keeper_right_fork")
    panel = box(mm(P.JOINT_KEEPER_LEFT_X0), mm(P.JOINT_KEEPER_RIGHT_X1),
                -3.0, 3.0, mm(P.JOINT_KEEPER_PANEL_Z0), mm(P.JOINT_KEEPER_PANEL_Z1),
                "joint_keeper_bottom_stop")
    union(panel,
          box(mm(P.JOINT_KEEPER_LEFT_X0), mm(P.JOINT_KEEPER_LEFT_X1),
              -3.0, 3.0, mm(P.JOINT_KEEPER_PANEL_Z1) - 0.2,
              zc - mm(P.JOINT_KEEPER_LEFT_SLOT_R) + 0.2, "joint_keeper_left_riser"),
          box(mm(P.JOINT_KEEPER_RIGHT_X0), mm(P.JOINT_KEEPER_RIGHT_X1),
              -3.0, 3.0, mm(P.JOINT_KEEPER_PANEL_Z1) - 0.2,
              zc - mm(P.JOINT_KEEPER_RIGHT_SLOT_R) + 0.2, "joint_keeper_right_riser"),
          left, right)
    panel.name = "joint_keeper"
    return panel


def build_cam(group):
    theta = math.radians(P.CAM_THETA_MIN_DEG)
    cx = mm(P.CAM_X[group])
    ecc = mm(P.CAM_E[group])
    cy = ecc * math.cos(theta)
    cz = mm(P.CAM_AXIS_Z) + ecc * math.sin(theta)
    x0 = cx - mm(P.CAM_T) / 2
    x1 = x0 + mm(P.CENTER_CAM_T if group == 0 else P.CAM_T)
    cam = cyl_x((cy, cz), mm(P.CAM_R), x0, x1, 96, f"cam_{group}")
    bore_x0 = x0 - 0.5
    # 中央と内環のハブ間に静止ヨークの右フォークを通す。
    if group == 0:
        next_x = mm(P.JOINT_KEEPER_RIGHT_X0) - 0.2
    elif group < 2:
        next_x = mm(P.CAM_X[group + 1]) - mm(P.CAM_T) / 2 - 0.3
    else:
        next_x = mm(P.BEARING_X[0] - P.BEARING_T / 2) - 0.3
    if next_x > x1 + 0.2:
        union(cam, cyl_x((0, mm(P.CAM_AXIS_Z)), mm(P.CAM_HUB_R), x1 - 0.2, next_x, 64, "cam_hub"))
    if group == 1:
        # 円板の左面を最下層にして全面接地させる。0.6mmの軸方向隙間は維持する。
        left_hub_x0 = x0
        union(cam, cyl_x((0, mm(P.CAM_AXIS_Z)), mm(P.CAM_HUB_R),
                         left_hub_x0, x0 + 0.2, 64, "cam_left_hub"))
        bore_x0 = left_hub_x0 - 0.5
    cut(cam, prism(hex_yz(mm(P.CAM_BORE_FLAT), 0, mm(P.CAM_AXIS_Z)), "x",
                   bore_x0, next_x + 0.5, "cam_hex_bore"))
    if group == 0:
        cut(cam, cyl_x((0, mm(P.CAM_AXIS_Z)), mm(P.CENTER_CAM_RELIEF_R),
                       x0, mm(P.CENTER_CAM_RELIEF_X1), 64,
                       "coupler_shoulder_relief"))
    cam.name = ("cam_center", "cam_inner", "cam_outer")[group]
    return cam


def build_bearing_keeper():
    bx = mm(P.BEARING_X[0])
    bt = mm(P.KEEPER_T)
    keeper_x1 = HALF - 0.3
    keeper_x0 = keeper_x1 - bt
    zc = mm(P.CAM_AXIS_Z)
    keeper = cyl_x((0, zc), 5.5, keeper_x0, keeper_x1, 64, "bearing_keeper")
    # 左右キー溝から入れた後に90度回し、上下の回転空間へ置く1.2mm厚の爪。
    for sign in (-1, 1):
        union(keeper, box(keeper_x0 - 1.2, keeper_x0 + 0.2,
                          -1.5, 1.5, zc + sign * 5.2 - 1.5,
                          zc + sign * 5.2 + 1.5, "keeper_bayonet_lug"))
    # 板ばねが90度位置で戻る凹み。回転中は外周がばねを0.15mmだけ押す。
    angle = math.radians(P.KEEPER_DETENT_ANGLE_DEG)
    radial = (math.cos(angle), math.sin(angle))
    tangent = (-radial[1], radial[0])
    inner_r = 5.5 - mm(P.KEEPER_DETENT_NOTCH_DEPTH)
    outer_r = 5.7
    half_w = mm(P.KEEPER_DETENT_NOTCH_W) / 2
    notch = [
        (radial[0] * inner_r + tangent[0] * half_w,
         zc + radial[1] * inner_r + tangent[1] * half_w),
        (radial[0] * outer_r + tangent[0] * half_w,
         zc + radial[1] * outer_r + tangent[1] * half_w),
        (radial[0] * outer_r - tangent[0] * half_w,
         zc + radial[1] * outer_r - tangent[1] * half_w),
        (radial[0] * inner_r - tangent[0] * half_w,
         zc + radial[1] * inner_r - tangent[1] * half_w),
    ]
    cut(keeper, prism(notch, "x", keeper_x0 - 0.2, keeper_x1 + 0.2,
                       "keeper_detent_notch"))
    keeper.name = "bearing_keeper"
    return keeper


def build_servo_clip():
    sx0 = mm(P.SERVO_X0)
    x0, x1 = sx0 + 5.0, sx0 + 11.5
    sy0 = mm(P.SG.BODY_CENTER_X - P.SG.BODY_L / 2 + P.SERVO_Y_OFFSET)
    sy1 = mm(P.SG.BODY_CENTER_X + P.SG.BODY_L / 2 + P.SERVO_Y_OFFSET)
    z0 = mm(P.SERVO_Z - P.SG.BODY_W / 2)
    z1 = mm(P.SERVO_Z + P.SG.BODY_W / 2)
    gap = mm(P.SERVO_CLR)
    t = mm(P.SERVO_CLIP_T)
    leg_b0, leg_b1 = sy0 - gap - 2 * t, sy0 - gap - t
    leg_f0, leg_f1 = sy1 + gap + t, sy1 + gap + 2 * t
    bridge_z0, bridge_z1 = z0 - gap - t, z0 - gap
    clip = box(x0, x1, leg_b0, leg_b1, bridge_z0, z0 + 4.5, "servo_clip")
    union(clip,
          box(x0, x1, leg_f0, leg_f1, bridge_z0, z0 + 4.0, "clip_front"),
          box(x0, x1, leg_b1, leg_f0, bridge_z0, bridge_z1, "clip_bridge"))
    hook = mm(P.SERVO_CLIP_HOOK)
    union(clip,
          box(x0, x1, leg_b1, leg_b1 + hook, z0 + 1.5, z0 + 3.5, "clip_hook_b"),
          box(x0, x1, leg_f0 - hook, leg_f0, z0 + 1.5, z0 + 3.5, "clip_hook_f"))
    clip.name = "servo_clip"
    return clip


def build_bottom():
    gap = mm(P.BOTTOM_GAP)
    panel = box(-INNER + gap, INNER - gap, -INNER + gap, INNER - gap,
                0.0, mm(P.BOTTOM_T), "bottom")
    t = mm(P.BOTTOM_TAB_T)
    z0, z1 = mm(P.BOTTOM_T) - 0.2, mm(P.BOTTOM_T + P.BOTTOM_TAB_L)
    hook = mm(P.BOTTOM_TAB_HOOK)
    for side in (-1, 1):
        x = side * (INNER - gap - t / 2)
        for y in (-12.0, 12.0):
            union(panel, box(x - t / 2, x + t / 2, y - 4.0, y + 4.0, z0, z1, "bottom_tab"))
            xo = x + side * hook / 2
            union(panel, box(xo - (t + hook) / 2, xo + (t + hook) / 2, y - 4.0, y + 4.0,
                             z1 - 2.0, z1, "bottom_hook"))
    # 外装と一体で床から立つサーボ保持リブだけを避ける。各切欠きは片側0.3mm余裕。
    sx1 = mm(P.SERVO_X0 + P.SG.BODY_H)
    sy0 = mm(P.SG.BODY_CENTER_X - P.SG.BODY_L / 2 + P.SERVO_Y_OFFSET)
    sy1 = mm(P.SG.BODY_CENTER_X + P.SG.BODY_L / 2 + P.SERVO_Y_OFFSET)
    clr = mm(P.SERVO_CLR)
    tray_t = mm(P.SERVO_TRAY_T)
    for xa, xb in ((-21.9, -19.5), (sx1 - 1.6, sx1 + 0.8)):
        cut(panel,
            box(xa - 0.3, xb + 0.3, -INNER - 0.3, sy0 - clr + 0.3,
                -0.3, mm(P.BOTTOM_T) + 0.3, "bottom_rib_clearance"),
            box(xa - 0.3, xb + 0.3, sy1 + clr - 0.3, INNER + 0.3,
                -0.3, mm(P.BOTTOM_T) + 0.3, "bottom_rib_clearance"))
    cut(panel,
        box(-33.7, -30.7, sy0 - clr - tray_t - 0.3, sy0 - clr + 0.3,
            -0.3, mm(P.BOTTOM_T) + 0.3, "bottom_post_clearance"),
        box(-INNER - 0.3, -30.7, sy0 - clr - tray_t - 0.3, sy0 - clr + 0.3,
            -0.3, mm(P.BOTTOM_T) + 0.3, "bottom_foot_clearance"),
        box(-33.7, -30.7, sy1 + clr - 0.3, sy1 + clr + tray_t + 0.3,
            -0.3, mm(P.BOTTOM_T) + 0.3, "bottom_post_clearance"),
        box(-INNER - 0.3, -30.7, sy1 + clr - 0.3, sy1 + clr + tray_t + 0.3,
            -0.3, mm(P.BOTTOM_T) + 0.3, "bottom_foot_clearance"))
    panel.name = "bottom"
    return panel


SERVO_MATRIX = Matrix(((0, 0, 1, mm(P.SERVO_X0)),
                       (1, 0, 0, mm(P.SERVO_Y_OFFSET)),
                       (0, 1, 0, mm(P.SERVO_Z)),
                       (0, 0, 0, 1)))


def import_servo_ref(part):
    path = os.path.join(EXPORTS_DIR, f"sg92r-photo-{part}.stl")
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=path)
    ob = next(o for o in bpy.data.objects if o not in before)
    ob.name = f"servo_{part}"
    if part == "wire":
        cleanup_wire_reference(ob)
    transform(ob, SERVO_MATRIX)
    if part == "horn":
        a = math.radians(P.HORN_HOME_DEG)
        transform(ob, Matrix.Translation((0, 0, mm(P.CAM_AXIS_Z))) @ Matrix.Rotation(a, 4, "X") @
                  Matrix.Translation((0, 0, -mm(P.CAM_AXIS_Z))))
    validate_reference_mesh(ob)
    return ob


def build_print_tests():
    # ホーン受けは本体と同じポケット深さ。サーボ保持は台とクリップ脚の実寸断面。
    outer = horn_shapes(mm(P.HORN_CLEARANCE) + 2.4)
    horn = prism(outer[0], "z", 0, 4.8, "horn_fit_test")
    for poly in outer[1:]:
        union(horn, prism(poly, "z", 0, 4.8, "horn_fit_lobe"))
    horn_pocket_depth = mm(P.SG.HORN_ARM_T + P.HORN_POCKET_EXTRA)
    for poly in horn_shapes(mm(P.HORN_CLEARANCE)):
        cut(horn, prism(poly, "z", 4.8 - horn_pocket_depth, 5.3, "horn_fit_pocket"))
    # 主軸継手と同じ3.6mm差込は独立した台へ立て、ホーン穴の上で空中開始させない。
    peg_center = (21.2, 0.0)
    peg = box(19.1, 23.3, -2.2, 2.2, 0.0, 1.2, "shaft_joint_fit_peg_base")
    union(peg, prism(hex_poly(*peg_center, mm(P.SHAFT_JOINT_FLAT)), "z",
                     1.0, 1.0 + mm(P.SHAFT_JOINT_L), "shaft_joint_fit_peg"))
    rail = box(24, 38, -14, 10, 0, 2.4, "servo_fit_rail")
    union(rail, box(24, 38, -14, -11.15, 2.2, 10.5, "servo_fit_side"),
          box(24, 38, 6.85, 9.7, 2.2, 10.5, "servo_fit_side2"))
    socket = prism(hex_poly(46, 0, mm(P.CAM_SHAFT_FLAT)), "z", 0, mm(P.SHAFT_JOINT_L),
                   "shaft_joint_fit_socket")
    cut(socket, prism(hex_poly(46, 0, mm(P.SHAFT_JOINT_SOCKET_FLAT)), "z",
                      -0.4, mm(P.SHAFT_JOINT_L) + 0.4, "shaft_joint_fit_bore"))
    # ヨーク右フォークとφ5.4mm中実軸溝を平置き試片で確かめる。
    fork = box(58.0, 72.0, -8.0, 8.0, 0.0, 1.2, "joint_keeper_fit_fork")
    cut(fork,
        prism(circle((65.0, 0.0), mm(P.JOINT_KEEPER_RIGHT_SLOT_R), 64),
              "z", -0.2, 1.4, "joint_keeper_fit_round_slot"),
        box(65.0 - mm(P.JOINT_KEEPER_RIGHT_SLOT_R),
            65.0 + mm(P.JOINT_KEEPER_RIGHT_SLOT_R), 0.0, 8.2,
            -0.2, 1.4, "joint_keeper_fit_opening"))
    groove = prism(hex_poly(82.0, 0.0, mm(P.CAM_SHAFT_FLAT)),
                   "z", 0.0, 6.0, "joint_keeper_fit_groove")
    groove_cutter = box(76.0, 88.0, -6.0, 6.0, 2.3, 3.7,
                        "joint_keeper_fit_groove_cutter")
    cut(groove_cutter,
        prism(circle((82.0, 0.0), mm(P.JOINT_SHAFT_GROOVE_D) / 2, 64),
              "z", 2.1, 3.9, "joint_keeper_fit_groove_core"))
    cut(groove, groove_cutter)
    # ホーン受け側の円形溝と左フォークも実寸で組み合わせる。
    left_fork = box(93.0, 107.0, -8.0, 8.0, 0.0, 1.2, "coupler_keeper_fit_fork")
    left_slot_r = mm(P.JOINT_COUPLER_GROOVE_R) + 0.3
    cut(left_fork,
        prism(circle((100.0, 0.0), left_slot_r, 64),
              "z", -0.2, 1.4, "coupler_keeper_fit_round_slot"),
        box(100.0 - left_slot_r, 100.0 + left_slot_r, 0.0, 8.2,
            -0.2, 1.4, "coupler_keeper_fit_opening"))
    neck = prism(circle((117.0, 0.0), 5.5, 64), "z", 0.0, 6.0,
                 "coupler_keeper_fit_neck")
    neck_cutter = box(111.0, 123.0, -6.0, 6.0, 2.3, 3.7,
                      "coupler_keeper_fit_neck_cutter")
    cut(neck_cutter,
        prism(circle((117.0, 0.0), mm(P.JOINT_COUPLER_GROOVE_R), 64),
              "z", 2.1, 3.9, "coupler_keeper_fit_neck_core"))
    cut(neck, neck_cutter)
    # 円形溝は横向きにし、溝から離れた両端の平らな足で接地させる。
    transform(neck, Matrix.Translation((117.0, 0.0, 5.5)) @
              Matrix.Rotation(math.radians(90), 4, "Y") @
              Matrix.Translation((-117.0, 0.0, -3.0)))
    union(neck,
          box(114.0, 115.0, -1.2, 1.2, 0.0, 0.8, "neck_print_foot_l"),
          box(119.0, 120.0, -1.2, 1.2, 0.0, 0.8, "neck_print_foot_r"))
    # 8試片を同じSTLにする。差込、穴、保持部、左右フォークと各溝を別々に確認する。
    horn.name = "print_test"
    return [horn, peg, rail, socket, fork, groove, left_fork, neck]


PRINT_TRANSFORMS = {
    "housing": Matrix.Identity(4),
    "faceplate": Matrix.Rotation(math.radians(180), 4, "X"),
    "guide_frame": Matrix.Identity(4),
    "bottom": Matrix.Identity(4),
    "carrier_center": Matrix.Rotation(math.radians(180), 4, "X"),
    "carrier_inner": Matrix.Rotation(math.radians(180), 4, "X"),
    "carrier_outer": Matrix.Rotation(math.radians(180), 4, "X"),
    "camshaft": Matrix.Identity(4),
    "horn_coupler": Matrix.Rotation(math.radians(-P.HORN_HOME_DEG), 4, "X"),
    "joint_keeper": Matrix.Identity(4),
    "cam_center": Matrix.Rotation(math.radians(-90), 4, "Y"),
    "cam_inner": Matrix.Rotation(math.radians(-90), 4, "Y"),
    "cam_outer": Matrix.Rotation(math.radians(-90), 4, "Y"),
    "bearing_keeper": Matrix.Rotation(math.radians(90), 4, "Y"),
    "servo_clip": Matrix.Rotation(math.radians(90), 4, "Y"),
}


def place_on_bed(ob, matrix):
    transform(ob, matrix)
    lo = min((ob.matrix_world @ vertex.co).z for vertex in ob.data.vertices)
    transform(ob, Matrix.Translation((0, 0, -lo)))
    placed_lo = min((ob.matrix_world @ vertex.co).z for vertex in ob.data.vertices)
    if abs(placed_lo) > 1e-5:
        raise RuntimeError(f"{ob.name}: print STL bed normalization failed: z={placed_lo:.6f}mm")


def build_coupler_print_support():
    """横向き六角差込の下面だけを支える、ベッドから折り取る印刷用支持。"""
    thickness = mm(P.COUPLER_PRINT_SUPPORT_T)
    gap = mm(P.COUPLER_PRINT_SUPPORT_GAP)
    peg_layer_z = 8.2
    support_top = peg_layer_z - mm(P.COUPLER_PRINT_LAYER_H) - gap
    y0 = -39.2 - thickness / 2
    y1 = -39.2 + thickness / 2
    base = box(1.8, 9.0, y0 - 0.7, y1 + 0.7, 0.0, 0.4,
               "coupler_support_base")
    union(base, box(1.8, 9.0, y0, y1, 0.0, support_top,
                    "coupler_support_wall"))
    second_product_z = mm(P.COUPLER_SECOND_PRINT_SUPPORT_PRODUCT_Z)
    second_top = second_product_z - mm(P.COUPLER_PRINT_LAYER_H) - gap
    union(base,
          box(0.0, 2.0, -40.5, -38.3, 0.0, 0.4,
              "coupler_second_support_base"),
          box(0.1, 1.1, -40.45, -38.35, 0.2, second_top,
              "coupler_second_support_wall"))
    base.name = "coupler_print_support"
    return base


def build_carrier_outer_print_support():
    """外環裏面の閉曲線だけを受ける、ベッドから折り取る印刷用支持。"""
    product_z = mm(P.CARRIER_OUTER_PRINT_SUPPORT_PRODUCT_Z)
    layer_h = mm(P.CARRIER_OUTER_PRINT_SUPPORT_LAYER_H)
    gap = mm(P.CARRIER_OUTER_PRINT_SUPPORT_GAP)
    support_top = product_z - layer_h - gap
    x_half = mm(P.CARRIER_OUTER_PRINT_SUPPORT_X_HALF)
    y0, y1 = (mm(value) for value in P.CARRIER_OUTER_PRINT_SUPPORT_Y)
    base_x_half = mm(P.CARRIER_OUTER_PRINT_SUPPORT_BASE_X_HALF)
    base_y0, base_y1 = (mm(value) for value in P.CARRIER_OUTER_PRINT_SUPPORT_BASE_Y)
    base_t = mm(P.CARRIER_OUTER_PRINT_SUPPORT_BASE_T)
    ramp_z0 = mm(P.CARRIER_OUTER_PRINT_SUPPORT_RAMP_Z0)
    ramp_z1 = ramp_z0 + (y1 - base_y1)
    base = box(-base_x_half, base_x_half, base_y0, base_y1, 0.0, base_t,
               "carrier_outer_support_base")
    tower_profile = [
        (y0, base_t - 0.2), (base_y1, base_t - 0.2),
        (base_y1, ramp_z0), (y1, ramp_z1),
        (y1, support_top), (y0, support_top),
    ]
    union(base, prism(tower_profile, "x", -x_half, x_half,
                      "carrier_outer_support_tower"))
    base.name = "carrier_outer_print_support"
    return base


def build_carrier_center_print_support():
    """中央従動柱を受ける、ベッドから45度で寄せる除去式支持。"""
    product_z = mm(P.CARRIER_CENTER_PRINT_SUPPORT_PRODUCT_Z)
    support_top = (product_z - mm(P.CARRIER_CENTER_PRINT_SUPPORT_LAYER_H)
                   - mm(P.CARRIER_CENTER_PRINT_SUPPORT_GAP))
    base = box(6.2, 7.5, 1.7, 3.3, 0.0, 0.4, "carrier_center_support_base")
    profile = [(6.2, 0.2), (7.2, 0.2), (7.2, 2.4), (5.9, 3.7),
               (5.9, support_top), (4.7, support_top), (4.7, 3.9), (6.2, 2.4)]
    union(base, prism(profile, "y", 1.9, 3.1, "carrier_center_support_tower"))
    base.name = "carrier_center_print_support"
    return base


def build_housing_detent_print_support():
    """横穴の内面から板ばね先端を受け、横穴から折り取る印刷用支持。"""
    product_z = mm(P.HOUSING_DETENT_PRINT_SUPPORT_PRODUCT_Z)
    support_top = (product_z - mm(P.HOUSING_DETENT_PRINT_SUPPORT_LAYER_H)
                   - mm(P.HOUSING_DETENT_PRINT_SUPPORT_GAP))
    support = box(36.05, 37.85, 3.5, 4.0, 35.3, support_top,
                  "housing_detent_print_support")
    support.name = "housing_detent_print_support"
    return support


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    return mat


def render_scene(objects, path, raised=False, exploded=False):
    scene = bpy.context.scene
    for ob in bpy.context.scene.objects:
        ob.hide_render = ob not in objects
    if raised:
        tf = motion.transforms(P.SERVO_MAX_DEG)
        for ob in objects:
            key = ob.name.split("_preview")[0]
            if key in tf:
                ob.matrix_world = Matrix([tf[key][i:i + 4] for i in range(0, 16, 4)]).transposed() @ ob.matrix_world
    if exploded:
        for i, ob in enumerate(objects):
            ob.location += Vector(((i % 4 - 1.5) * 16, (i // 4 - 1) * 14, (i % 3) * 5))
    bpy.context.view_layer.update()
    points = [ob.matrix_world @ Vector(corner) for ob in objects for corner in ob.bound_box]
    lo = Vector(tuple(min(point[i] for point in points) for i in range(3)))
    hi = Vector(tuple(max(point[i] for point in points) for i in range(3)))
    target = (lo + hi) / 2
    bpy.ops.object.camera_add(location=target + Vector((122, -142, 72)))
    camera = bpy.context.object
    camera.rotation_euler = ((target - camera.location).to_track_quat("-Z", "Y")).to_euler()
    bpy.context.view_layer.update()
    camera.data.type = "ORTHO"
    right = camera.matrix_world.to_3x3() @ Vector((1, 0, 0))
    up = camera.matrix_world.to_3x3() @ Vector((0, 1, 0))
    projected_x = [point.dot(right) for point in points]
    projected_y = [point.dot(up) for point in points]
    projected_center = (right * ((min(projected_x) + max(projected_x)) / 2 - target.dot(right)) +
                        up * ((min(projected_y) + max(projected_y)) / 2 - target.dot(up)))
    camera.location += projected_center
    target += projected_center
    camera.rotation_euler = ((target - camera.location).to_track_quat("-Z", "Y")).to_euler()
    camera.data.ortho_scale = 1.25 * max(max(projected_x) - min(projected_x),
                                        max(projected_y) - min(projected_y))
    scene.camera = camera
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 800
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)


def main():
    clear_scene()
    os.makedirs(BUILD, exist_ok=True)
    parts = {
        "housing": build_housing(),
        "faceplate": build_faceplate(),
        "guide_frame": build_guide_frame(),
        "bottom": build_bottom(),
        "carrier_center": build_carrier(0),
        "carrier_inner": build_carrier(1),
        "carrier_outer": build_carrier(2),
        "camshaft": build_camshaft(),
        "horn_coupler": build_horn_coupler(),
        "joint_keeper": build_joint_keeper(),
        "cam_center": build_cam(0),
        "cam_inner": build_cam(1),
        "cam_outer": build_cam(2),
        "bearing_keeper": build_bearing_keeper(),
        "servo_clip": build_servo_clip(),
        "servo_body": import_servo_ref("body"),
        "servo_horn": import_servo_ref("horn"),
        "servo_wire": import_servo_ref("wire"),
    }
    tests = build_print_tests()

    servo_refs = {"servo_body", "servo_horn", "servo_wire"}
    for ob in [*parts.values(), *tests]:
        triangulate_for_export(ob)
    for name, ob in parts.items():
        if name in servo_refs:
            continue
        if nonmanifold(ob):
            raise RuntimeError(f"{name}: non-manifold={nonmanifold(ob)}")
    for ob in tests:
        if nonmanifold(ob):
            raise RuntimeError(f"{ob.name}: non-manifold={nonmanifold(ob)}")

    # 組立姿勢STL（mm）
    for name, ob in parts.items():
        save_stl([ob], os.path.join(BUILD, f"{name}.stl"))
    save_stl(tests, os.path.join(BUILD, "print_test.stl"))

    printed = {}
    print_supports = []
    for name in ("housing", "faceplate", "guide_frame", "bottom", "carrier_center", "carrier_inner", "carrier_outer",
                 "camshaft", "horn_coupler", "joint_keeper", "cam_center", "cam_inner", "cam_outer",
                 "bearing_keeper", "servo_clip"):
        ob = duplicate(parts[name], f"print_{name}")
        place_on_bed(ob, PRINT_TRANSFORMS[name])
        printed[name] = ob
        print_objects = [ob]
        if name == "horn_coupler":
            support = build_coupler_print_support()
            if nonmanifold(support):
                raise RuntimeError(f"coupler_print_support: non-manifold={nonmanifold(support)}")
            print_objects.append(support)
            support_common = {
                "part_id": name, "support_builder": "build_coupler_print_support",
                "nonmanifold_edges": nonmanifold(support), "expected_print_components": 2,
                "attachment_mode": "separate_bed_tower", "bed_contact_required": True,
                "removal_route": "ベッド側の共通台を折り、+X差込先端側から引き抜く",
            }
            print_supports.extend([
                {**support_common, "support_id": "horn_coupler_peg_support",
                 "component_bbox_mm": [[1.8, -40.1, 0.0], [9.0, -38.3, 7.8]],
                 "support_top_z_mm": 7.8, "product_first_z_mm": 8.2,
                 "material_face_gap_mm": 0.2},
                {**support_common, "support_id": "horn_coupler_loop_support",
                 "component_bbox_mm": [[0.0, -40.5, 0.0], [2.0, -38.3, 5.2]],
                 "support_top_z_mm": 5.2, "product_first_z_mm": 5.6,
                 "material_face_gap_mm": 0.2},
            ])
        elif name == "housing":
            support = build_housing_detent_print_support()
            print_supports.append({
                "support_id": "housing_detent_support", "part_id": name,
                "support_builder": "build_housing_detent_print_support",
                "component_bbox_mm": bbox(support), "support_top_z_mm": 44.4,
                "product_first_z_mm": 44.8, "material_face_gap_mm": 0.2,
                "nonmanifold_edges": nonmanifold(support), "expected_print_components": 1,
                "attachment": "breakaway_contact", "attachment_mode": "breakaway_contact",
                "bed_contact_required": False,
                "allowed_contact_regions_mm": [
                    [[36.05, 3.5, 35.3], [37.85, 4.0, 36.3]],
                    [[36.05, 3.5, 43.4], [37.85, 4.0, 44.4]],
                ],
                "removal_route": "+X側の右軸受け開口からつまみ、Y方向へ倒して同じ開口から抜く"})
            union(ob, support)
            if nonmanifold(ob):
                raise RuntimeError(f"print_housing: non-manifold={nonmanifold(ob)}")
        elif name == "carrier_center":
            support = build_carrier_center_print_support()
            if nonmanifold(support):
                raise RuntimeError(
                    f"carrier_center_print_support: non-manifold={nonmanifold(support)}")
            print_objects.append(support)
            print_supports.append({
                "support_id": "carrier_center_support", "part_id": name,
                "support_builder": "build_carrier_center_print_support",
                "component_bbox_mm": bbox(support), "support_top_z_mm": 11.0,
                "product_first_z_mm": 11.4, "material_face_gap_mm": 0.2,
                "nonmanifold_edges": nonmanifold(support), "expected_print_components": 2,
                "attachment_mode": "separate_bed_tower", "bed_contact_required": True,
                "removal_route": "ベッド側の台を折り、格子裏面から離す"})
        elif name == "carrier_outer":
            support = build_carrier_outer_print_support()
            if nonmanifold(support):
                raise RuntimeError(
                    f"carrier_outer_print_support: non-manifold={nonmanifold(support)}")
            print_objects.append(support)
            print_supports.append({
                "support_id": "carrier_outer_support", "part_id": name,
                "support_builder": "build_carrier_outer_print_support",
                "component_bbox_mm": bbox(support), "support_top_z_mm": 8.2,
                "product_first_z_mm": 8.6, "material_face_gap_mm": 0.2,
                "nonmanifold_edges": nonmanifold(support), "expected_print_components": 2,
                "attachment_mode": "separate_bed_tower", "bed_contact_required": True,
                "removal_route": "ベッド側の台を折り、格子裏面から離す"})
        save_stl(print_objects, os.path.join(BUILD, f"print_{name}.stl"))

    face_mat = material("face", (0.87, 0.88, 0.86))
    mech_mat = material("mechanism", (0.19, 0.21, 0.22))
    ref_mat = material("servo", (0.18, 0.32, 0.55))
    for name, ob in parts.items():
        ob.data.materials.append(ref_mat if name.startswith("servo_") else
                                 face_mat if name in ("housing", "faceplate", "bottom", "carrier_center", "carrier_inner", "carrier_outer")
                                 else mech_mat)

    closed_preview = [duplicate(ob, f"{name}_preview") for name, ob in parts.items()]
    render_scene(closed_preview, os.path.join(BUILD, "closed.png"))
    for ob in closed_preview:
        bpy.data.objects.remove(ob, do_unlink=True)
    raised_preview = [duplicate(ob, f"{name}_preview") for name, ob in parts.items()]
    render_scene(raised_preview, os.path.join(BUILD, "raised.png"), raised=True)
    for ob in raised_preview:
        bpy.data.objects.remove(ob, do_unlink=True)
    part_preview = [duplicate(ob, f"{name}_preview") for name, ob in parts.items() if name not in servo_refs]
    render_scene(part_preview, os.path.join(BUILD, "parts.png"), exploded=True)
    for ob in part_preview:
        bpy.data.objects.remove(ob, do_unlink=True)

    raised_height_mm = max(
        bbox(parts[name])[1][2] + mm(motion.lift_m(group, P.SERVO_MAX_DEG))
        for group, name in enumerate(("carrier_center", "carrier_inner", "carrier_outer"))
    )

    manifest_parts = []
    labels = {
        "housing": "外装", "faceplate": "六角格子の天板", "guide_frame": "格子の案内枠",
        "bottom": "底板", "carrier_center": "中心の格子",
        "carrier_inner": "内側の格子", "carrier_outer": "外側の格子", "camshaft": "六角カム軸",
        "horn_coupler": "ホーン受け", "joint_keeper": "軸継手保持ヨーク",
        "cam_center": "中心用偏心カム", "cam_inner": "内環用偏心カム", "cam_outer": "外環用偏心カム",
        "bearing_keeper": "右軸受け保持具", "servo_clip": "サーボ保持具",
        "servo_body": "SG92R本体", "servo_horn": "付属クロスホーン", "servo_wire": "SG92R配線",
    }
    colors = {
        "housing": "#e5e6e2", "faceplate": "#eeeeeb", "guide_frame": "#4a4e50",
        "bottom": "#d7d9d5", "carrier_center": "#fafafa",
        "carrier_inner": "#f1f1ef", "carrier_outer": "#e7e8e5", "camshaft": "#34383a",
        "horn_coupler": "#34383a", "joint_keeper": "#4a4e50",
        "cam_center": "#34383a", "cam_inner": "#3d4244", "cam_outer": "#474c4e",
        "bearing_keeper": "#4a4e50", "servo_clip": "#4a4e50", "servo_body": "#335d91",
        "servo_horn": "#f5f5f2", "servo_wire": "#756d65",
    }
    explodes = {
        "housing": [0, 0, 0], "faceplate": [0, 0, 20], "guide_frame": [0, 0, 12],
        "bottom": [0, 0, -18],
        "carrier_center": [0, 0, 34], "carrier_inner": [0, 0, 26], "carrier_outer": [0, 0, 18],
        "camshaft": [10, 0, -10], "horn_coupler": [-12, 0, -10], "joint_keeper": [0, 12, -18],
        "cam_center": [0, -14, -10], "cam_inner": [0, -20, -10],
        "cam_outer": [0, -26, -10], "bearing_keeper": [16, 0, -12], "servo_clip": [-18, 0, -12],
        "servo_body": [-18, 0, -18], "servo_horn": [-12, 0, -10], "servo_wire": [-18, 8, -18],
    }
    for name in parts:
        manifest_part = {
            "id": name,
            "label": labels[name],
            "assembly": f"build/{name}.stl",
            "print": None if name in servo_refs else f"build/print_{name}.stl",
            "fit_test": False,
            "color": colors[name],
            "explode": explodes[name],
        }
        if name in ("horn_coupler", "carrier_center", "carrier_outer"):
            manifest_part["expected_print_components"] = 2
        manifest_parts.append(manifest_part)
    manifest_parts.append({"id": "print_test", "label": "ホーン受け・軸継手・ヨーク・サーボ保持試片",
                           "assembly": "build/print_test.stl", "print": "build/print_test.stl",
                           "fit_test": True, "fit_only": True, "expected_print_components": 8,
                           "color": "#d9d1bf", "explode": [0, -55, 0]})
    manifest = {
        "meta": {
            "dimensions_mm": [76, 76, 76],
            "max_dimensions_mm": [76, 76, round(raised_height_mm, 3)],
            "exterior_parts": ["housing", "bottom", "faceplate"],
            "description": "19枚の六角面を3個の偏心円カムで6/4/2mm弱持ち上げる住人の箱C4。",
            "assembly_steps": [
                "外装、中央格子、外環格子、ホーン受けの印刷用支持をベッド側から折り取り、支持面に残りがないことを確かめる。",
                "SG92Rを底から保持台へ入れ、正本+X側の配線を箱+Y側の出口へ通す。",
                "サーボ保持具を底から押し込み、左右の爪を保持台へ掛ける。",
                "3枚のカムを底から各位置へ入れ、六角穴を同じ向きへ揃える。",
                "サーボを90度で静止させ、カムの偏心中心を+Yへ向ける。",
                "非対称ホーン受けの左右を合わせて付属ホーンへ差し、対辺3.6mmの六角差込を+Xへ向ける。",
                "対辺6.3mmのカム軸を右側から3枚のカムへ通し、左端の穴を六角差込へ8mm入れる。",
                "軸継手保持ヨークを底から上げ、左フォークをホーン受け盲底の円形溝へ、右フォークを主軸の中実溝へ入れる。",
                "右軸受け保持具を+X外側のキー溝へ入れ、外面と面一の位置で90度回し、板ばねが凹みへ戻る位置で保持する。",
                "内側と外側の格子を案内枠へ上から通す。中心の格子は+X側からC形開口へ水平に差す。",
                "3組の格子を通した案内枠を一体で上から外装の四隅の受けへ載せ、従動パッドを各カムへ載せる。",
                "六角格子の天板を上から外装へ下ろす。",
                "天板の4本の爪を内側へ軽く押し、外装の凹みへ掛ける。",
                "底板の4本の爪を内側へ軽く押しながら差し込み、凹みへ掛ける。",
            ],
            "decisions": [
                "閉位置は六角面を天面と面一にし、最大時の段差を5.909/3.939/1.970mmとした。",
                "左端はSG92R出力軸、右端は着脱式受けで支える両持ち構造とした。主軸6.3mm、穴3.9mm、差込3.6mm、長さ8mmで、穴外に1.2mm残す。",
                "静止二股ヨークがホーン受け盲底の円形溝と盲穴より右の中実軸溝を捕え、底板がヨークの下方脱落を止める。",
                "カム半径は10mm。最大偏心3mmと穴頂点半径3.839mmを差し引く保守最薄部を3.161mmとした。",
                "各格子は独立した3mm厚案内枠の対向2点で案内し、片側荷重のこじれを抑える。",
                "右保持具は自由長8mm、厚さ1.2mmの板ばねと幅2.6mm、深さ0.3mmの凹みで90度位置を保つ。回転中の押し量0.15mm、曲げひずみ0.422%。",
                "外装、中央格子、外環格子、ホーン受けの印刷STLに、対象面から0.2mm離した除去式支持を同梱する。",
            ],
            "limitations": [
                "重力復帰のため天面を上にした姿勢専用。",
                "無通電SG92Rは逆駆動できるとは限らず、停止角度付近に残り得る。復電後に低速で10度へ戻す。",
                "ホーン寸法、配線出口、摩擦、PLA/PETGの収縮は実物未検証。",
                "右保持具の板ばね保持力と繰り返し耐久は実物未検証。",
                "4部品5か所の除去式支持は、実印刷後の癒着と除去性が未確認。",
            ],
        },
        "parts": manifest_parts,
        "print_supports": print_supports,
    }
    write_json(os.path.join(BUILD, "manifest.json"), manifest)
    motion.write_motion()

    report = {"parts": {name: {"bbox_mm": bbox(ob), "volume_mm3": round(volume(ob), 2),
                                "nonmanifold_edges": nonmanifold(ob)}
                        for name, ob in parts.items() if name not in servo_refs},
              "closed_bbox_mm": [[-38.0, -38.0, 0.0], [38.0, 38.0, 76.0]],
              "print_supports": print_supports,
              "raised_height_mm": round(raised_height_mm, 3),
              "raised_height_source": "実メッシュ上端へservo=170度の運動量を加算"}
    write_json(os.path.join(BUILD, "model_report.json"), report)

    # exportsは既存の規約どおりmへ戻してexport_stl()から出す。
    export_objects = list(parts.values())
    for ob in export_objects:
        transform(ob, Matrix.Scale(0.001, 4))
    export_stl(P.MODEL_ID, only=export_objects)
    for name in ("housing", "faceplate", "guide_frame", "bottom", "carrier_center", "carrier_inner", "carrier_outer",
                 "camshaft", "horn_coupler", "joint_keeper", "cam_center", "cam_inner", "cam_outer",
                 "bearing_keeper", "servo_clip"):
        ob = duplicate(parts[name], f"export_{name}")
        # 元は既にm。個別の印刷姿勢はbuild/を正本とする。
        export_stl(f"{P.MODEL_ID}-{name}", only=[ob])


if __name__ == "__main__":
    main()
