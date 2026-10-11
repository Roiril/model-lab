"""住人の箱 C4-2。四つの独立した面カムで19枚の六角面を選択的に沈める。"""



from __future__ import annotations



import json

import math

import os

import sys



HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.abspath(os.path.join(HERE, "../.."))

sys.path.insert(0, os.path.join(ROOT, "lib"))

sys.path.insert(0, HERE)



import bmesh  # noqa: E402

import bpy  # noqa: E402

from mathutils import Matrix, Vector  # noqa: E402



from blender_utils import EXPORTS_DIR, clear_scene, export_stl  # noqa: E402

from printmech.geometry import (  # noqa: E402

    boolean, box, circle, clean, cut, hull, nonmanifold, prism, transform,

    union, volume,

)

import motion  # noqa: E402

import params as P  # noqa: E402



MM = 1000.0

BUILD = os.path.join(HERE, "build")

HALF = P.CUBE * MM / 2.0

INNER = HALF - P.WALL * MM

WALL = P.WALL * MM

FRAME_T = P.FRAME_T * MM

TOP_Z0 = P.CUBE * MM - FRAME_T

CAP_Z0 = TOP_Z0

CAP_Z1 = P.CUBE * MM

WEB_Z0 = P.CARRIER_WEB_Z0 * MM

WEB_Z1 = WEB_Z0 + FRAME_T

GUIDE_Z0 = P.GUIDE_Z0 * MM

GUIDE_Z1 = P.GUIDE_Z1 * MM

GUIDE_LUG = P.GUIDE_LUG * MM

GUIDE_WALL = P.GUIDE_WALL * MM

SERVO_REFS = {"servo_body", "servo_horn", "servo_wire"}





def mm(value):

    return value * MM





def write_json(path, data):

    temporary = path + ".tmp"

    with open(temporary, "w", encoding="utf-8", newline="\n") as handle:

        json.dump(data, handle, ensure_ascii=False, indent=2)

        handle.write("\n")

    os.replace(temporary, path)





def save_stl(objects, path):

    bpy.ops.object.select_all(action="DESELECT")

    for ob in objects:

        ob.select_set(True)

    bpy.context.view_layer.objects.active = objects[0]

    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True, global_scale=1.0)





def duplicate(ob, name):

    copied = ob.copy()

    copied.data = ob.data.copy()

    copied.name = name

    bpy.context.collection.objects.link(copied)

    return copied


def cut_collection(target, cutters, name):
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
    clean(target, dist=1e-5)
    return target





def bbox(ob):

    points = [ob.matrix_world @ Vector(corner) for corner in ob.bound_box]

    return [[round(min(p[i] for p in points), 4) for i in range(3)],

            [round(max(p[i] for p in points), 4) for i in range(3)]]


def component_count(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    remaining = set(bm.verts)
    count = 0
    while remaining:
        count += 1
        stack = [remaining.pop()]
        while stack:
            vertex = stack.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in remaining:
                    remaining.remove(other)
                    stack.append(other)
    bm.free()
    return count





def hex_poly(cx, cy, flat):

    radius = flat / math.sqrt(3.0)

    return [(cx + radius * math.cos(math.radians(30 + 60 * i)),

             cy + radius * math.sin(math.radians(30 + 60 * i))) for i in range(6)]





def axial_xy(q, r):

    pitch = mm(P.HEX_PITCH)

    return (pitch * (q + r / 2.0), pitch * math.sqrt(3.0) * r / 2.0)





ALL_AXIAL = [(q, r) for r in range(-2, 3) for q in range(-2, 3)

             if max(abs(q), abs(r), abs(-q - r)) <= 2]

GROUP_AXIAL = {group: list(P.CELL_QR[group]) for group in P.GROUPS}

MOVING_AXIAL = {cell for cells in GROUP_AXIAL.values() for cell in cells}

FIXED_AXIAL = list(P.CELL_QR["fixed"])





def capsule_xy(a, b, radius, z0, z1, name):

    return prism(hull(circle(a, radius, 20) + circle(b, radius, 20)), "z", z0, z1, name)


def strip_xy(a, b, width, z0, z1, name):
    direction = Vector((b[0] - a[0], b[1] - a[1])).normalized()
    normal = Vector((-direction.y, direction.x)) * (width / 2)
    start = Vector(a) - direction * 0.3
    end = Vector(b) + direction * 0.3
    poly = [(start.x + normal.x, start.y + normal.y),
            (end.x + normal.x, end.y + normal.y),
            (end.x - normal.x, end.y - normal.y),
            (start.x - normal.x, start.y - normal.y)]
    return prism(poly, "z", z0, z1, name)





def ring_hex(center, name, z0=CAP_Z0, z1=CAP_Z1):

    ring = prism(hex_poly(*center, mm(P.HEX_CAP_FLAT)), "z", z0, z1, name)

    cut(ring, prism(hex_poly(*center, mm(P.HEX_HOLE_FLAT)), "z", z0 - 0.4, z1 + 0.4,

                    name + "_hole"))

    return ring





def annulus(name, r0, r1, z0, z1, segments=160):

    result = prism(circle((0, 0), r1, segments), "z", z0, z1, name)

    cut(result, prism(circle((0, 0), r0, segments), "z", z0 - 0.3, z1 + 0.3,

                      name + "_bore"))

    return result


def chamfered_annulus(name, r0, r1, z0, z1, chamfer, segments=160):
    """下面内周だけを45度で広げた閉じた円環。"""
    rings = ((r1, z0), (r1, z1), (r0, z1),
             (r0, z0 + chamfer), (r0 + chamfer, z0))
    vertices = []
    for radius, z in rings:
        vertices.extend((radius * math.cos(2 * math.pi * index / segments),
                         radius * math.sin(2 * math.pi * index / segments), z)
                        for index in range(segments))
    faces = []
    for ring_index in range(len(rings)):
        next_ring = (ring_index + 1) % len(rings)
        for index in range(segments):
            next_index = (index + 1) % segments
            faces.append((ring_index * segments + index,
                          ring_index * segments + next_index,
                          next_ring * segments + next_index,
                          next_ring * segments + index))
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    result = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(result)
    clean(result, dist=1e-5)
    return result


def annular_sector(radius, radial_width, arc_length, samples=8):
    half_angle = arc_length / (2.0 * radius)
    inner = radius - radial_width / 2.0
    outer = radius + radial_width / 2.0
    points = []
    for index in range(samples + 1):
        angle = -half_angle + 2.0 * half_angle * index / samples
        points.append((outer * math.cos(angle), outer * math.sin(angle)))
    for index in range(samples, -1, -1):
        angle = -half_angle + 2.0 * half_angle * index / samples
        points.append((inner * math.cos(angle), inner * math.sin(angle)))
    return points





def build_cam_disk():

    """0.25度刻みの面カム。上下面と側面は全て三角形で閉じる。"""

    angular_steps = 1440

    track_half_width = mm(P.CAM_TRACK_W) / 2
    first_track_edge = mm(P.CAM_RADII[0]) - track_half_width
    radial_nodes = [0.0, 8.0, mm(P.CAM_RADIAL_BEARING_R),
                    mm(P.CAM_RADIAL_BEARING_OUTER_R),
                    first_track_edge - 0.4]
    for center_radius in P.CAM_RADII:
        radial_nodes.extend((mm(center_radius) - track_half_width,
                             mm(center_radius) + track_half_width))
    radial_nodes.extend((47.0, mm(P.CAM_OUTER_R)))

    base_z = mm(P.CAM_BASE_Z)



    def top_at(radius, angle):

        if radius <= 8.0:

            return base_z + mm(P.CAM_BASE_T)

        tracks = []

        for group, center_radius in enumerate(P.CAM_RADII):

            tracks.append((mm(center_radius),

                           base_z + mm(motion.cam_height_m(group, angle))))

        if radius < tracks[0][0] - mm(P.CAM_TRACK_W) / 2:

            return base_z + mm(P.CAM_BASE_T)

        for index, (center_radius, height) in enumerate(tracks):

            edge = mm(P.CAM_TRACK_W) / 2

            if center_radius - edge <= radius <= center_radius + edge:

                return height

            if index + 1 < len(tracks):

                next_radius, next_height = tracks[index + 1]

                lo, hi = center_radius + edge, next_radius - edge

                if lo < radius < hi:

                    t = (radius - lo) / (hi - lo)

                    return height * (1.0 - t) + next_height * t

        outer_edge = tracks[-1][0] + mm(P.CAM_TRACK_W) / 2

        if radius > outer_edge:

            t = min(1.0, (radius - outer_edge) / max(0.001, 47.0 - outer_edge))

            return tracks[-1][1] * (1.0 - t) + (base_z + mm(P.CAM_BASE_T)) * t

        return base_z + mm(P.CAM_BASE_T)



    bm = bmesh.new()

    bottom_center = bm.verts.new((0, 0, base_z))

    top_center = bm.verts.new((0, 0, top_at(0, 0)))

    bottom_rings = []

    top_rings = []

    for radius in radial_nodes[1:]:

        br, tr = [], []

        for step in range(angular_steps):

            angle = 360.0 * step / angular_steps

            x = radius * math.cos(math.radians(angle))

            y = radius * math.sin(math.radians(angle))

            br.append(bm.verts.new((x, y, base_z)))

            tr.append(bm.verts.new((x, y, top_at(radius, angle))))

        bottom_rings.append(br)

        top_rings.append(tr)

    first_b, first_t = bottom_rings[0], top_rings[0]

    for i in range(angular_steps):

        j = (i + 1) % angular_steps

        bm.faces.new((bottom_center, first_b[j], first_b[i]))

        bm.faces.new((top_center, first_t[i], first_t[j]))

    for ring_index in range(len(bottom_rings) - 1):

        b0, b1 = bottom_rings[ring_index], bottom_rings[ring_index + 1]

        t0, t1 = top_rings[ring_index], top_rings[ring_index + 1]

        for i in range(angular_steps):

            j = (i + 1) % angular_steps

            bm.faces.new((b0[i], b1[j], b1[i]))

            bm.faces.new((b0[i], b0[j], b1[j]))

            bm.faces.new((t0[i], t1[i], t1[j]))

            bm.faces.new((t0[i], t1[j], t0[j]))

    last_b, last_t = bottom_rings[-1], top_rings[-1]

    for i in range(angular_steps):

        j = (i + 1) % angular_steps

        bm.faces.new((last_b[i], last_b[j], last_t[j]))

        bm.faces.new((last_b[i], last_t[j], last_t[i]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new("cam_disk_mesh")

    bm.to_mesh(mesh)

    bm.free()

    disk = bpy.data.objects.new("cam_disk", mesh)

    bpy.context.collection.objects.link(disk)

    # bossを中実で結合してから角穴を一度だけ切り、共面の内部殻を残さない。

    boss = prism(circle((0, 0), mm(P.CAM_RADIAL_BEARING_R), 96), "z",
                 base_z, 50.3, "cam_center_boss")

    union(disk, boss)

    cut(disk, box(-mm(P.KEY_SOCKET_FLAT) / 2, mm(P.KEY_SOCKET_FLAT) / 2,

                  -mm(P.KEY_SOCKET_FLAT) / 2, mm(P.KEY_SOCKET_FLAT) / 2,

                  base_z - 0.4, 51.8, "cam_key_socket"))

    disk.name = "cam_disk"

    return disk





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

    short_half = mm(sg.HORN_SPAN_Y) / 2 + clearance

    short_r = mm(sg.HORN_SHORT_W) / 2 + clearance

    short = hull(circle((0, short_half - short_r), short_r, 24) +

                 circle((0, -short_half + short_r), short_r, 24))

    return [left_arm, right_arm, short, circle((0, 0), hub, 48)]





def build_horn_coupler():

    wall = 2.4

    outer = horn_shapes(mm(P.HORN_CLR) + wall)

    coupler = prism(outer[0], "z", mm(P.COUPLER_Z0), mm(P.COUPLER_Z1), "horn_coupler")

    for shape in outer[1:]:

        union(coupler, prism(shape, "z", mm(P.COUPLER_Z0), mm(P.COUPLER_Z1), "horn_coupler_lobe"))

    union(coupler, prism(circle((0, 0), mm(P.COUPLER_KEY_BOSS_R), 96), "z",

                         mm(P.COUPLER_Z0), mm(P.COUPLER_Z1), "coupler_key_boss"))

    for shape in horn_shapes(mm(P.HORN_CLR)):

        cut(coupler, prism(shape, "z", mm(P.COUPLER_Z0) - 0.4,

                           mm(P.HORN_POCKET_Z1), "horn_pocket"))

    cut(coupler, box(-mm(P.KEY_SOCKET_FLAT) / 2, mm(P.KEY_SOCKET_FLAT) / 2,

                     -mm(P.KEY_SOCKET_FLAT) / 2, mm(P.KEY_SOCKET_FLAT) / 2,

                     mm(P.KEY_SOCKET_Z0), mm(P.COUPLER_Z1) + 0.3, "coupler_key_socket"))

    coupler.name = "horn_coupler"

    return coupler





def build_drive_key():

    key = box(-mm(P.KEY_FLAT) / 2, mm(P.KEY_FLAT) / 2,

              -mm(P.KEY_FLAT) / 2, mm(P.KEY_FLAT) / 2,

              mm(P.DRIVE_KEY_Z0), mm(P.DRIVE_KEY_Z1), "drive_key")

    # 上端の外周を0.6mm削り、盲穴へ入る実体の誘導面にする。

    cut(key,

        prism([(4.4, 50.3), (5.4, 50.3), (5.4, 49.3)], "y", -5.8, 5.8, "key_chamfer_xp"),

        prism([(-4.4, 50.3), (-5.4, 49.3), (-5.4, 50.3)], "y", -5.8, 5.8, "key_chamfer_xn"))

    union(key, prism(circle((0, 0), mm(P.KEY_HEAD_D) / 2, 96), "z",

                     mm(P.KEY_HEAD_Z0), mm(P.KEY_HEAD_Z1), "drive_key_head"))

    key.name = "drive_key"

    return key





def build_cam_keeper():

    keeper = annulus("cam_keeper", mm(P.KEEPER_INNER_R), mm(P.KEEPER_OUTER_R), 47.6, 50.8, 160)

    # 四つの長い爪を外周に置く。0.5mm撓ませて支持環下面へ掛ける。

    for angle in P.KEEPER_ANGLES_DEG:

        tab_inner = mm(P.KEEPER_TAB_INNER)
        tab_outer = tab_inner + mm(P.KEEPER_TAB_T)
        tab = box(tab_inner, tab_outer, -3.2, 3.2,
                  mm(P.KEEPER_HOOK_Z0), 48.0, "keeper_tab")
        hook = box(mm(P.KEEPER_HOOK_INNER), tab_outer, -3.2, 3.2,
                   mm(P.KEEPER_HOOK_Z0), mm(P.KEEPER_HOOK_Z1), "keeper_hook")
        cut(hook, prism([(mm(P.KEEPER_HOOK_INNER) - 0.3, mm(P.KEEPER_HOOK_Z0) - 0.3),
                         (tab_inner, mm(P.KEEPER_HOOK_Z0) - 0.3),
                         (mm(P.KEEPER_HOOK_INNER) - 0.3, mm(P.KEEPER_HOOK_Z0) + 0.7)],
                        "y", -3.5, 3.5, "keeper_hook_lead"))

        transform(tab, Matrix.Rotation(math.radians(angle), 4, "Z"))

        transform(hook, Matrix.Rotation(math.radians(angle), 4, "Z"))

        union(keeper, tab, hook)

    keeper.name = "cam_keeper"

    return keeper





def build_housing():

    z0, z1 = FRAME_T, TOP_Z0

    housing = box(-HALF, -INNER, -HALF, HALF, z0, z1, "housing")

    union(housing,

          box(INNER, HALF, -HALF, HALF, z0, z1, "wall_right"),

          box(-INNER, INNER, -HALF, -INNER, z0, z1, "wall_back"),

          box(-INNER, INNER, INNER, HALF, z0, z1, "wall_front"))

    # 案内枠は四隅の棚で受ける。棚下面の45度リブを外壁へ連続させる。
    ledge_inner = mm(P.GUIDE_LEDGE_INNER)
    ledge_outer = mm(P.GUIDE_LEDGE_OUTER)
    ledge_z0 = mm(P.GUIDE_LEDGE_Z0)
    ledge_z1 = mm(P.GUIDE_LEDGE_Z1)
    gusset_z0 = ledge_z0 - (ledge_outer - ledge_inner)
    for angle in (0, 90, 180, 270):
        ledge = box(ledge_inner, ledge_outer, ledge_inner, ledge_outer,
                    ledge_z0, ledge_z1, "guide_corner_ledge")
        gusset_x = prism([(ledge_inner, ledge_z0),
                          (ledge_outer, gusset_z0),
                          (ledge_outer, ledge_z0)],
                         "y", ledge_inner, ledge_outer, "guide_ledge_gusset_x")
        gusset_y = prism([(ledge_inner, ledge_z0),
                          (ledge_outer, gusset_z0),
                          (ledge_outer, ledge_z0)],
                         "x", ledge_inner, ledge_outer, "guide_ledge_gusset_y")
        union(ledge, gusset_x, gusset_y)
        transform(ledge, Matrix.Rotation(math.radians(angle), 4, "Z"))
        union(housing, ledge)

    # 対角二隅のL字面が案内枠をXY各方向へ0.2mm隙間で止める。
    stop_inner = mm(P.GUIDE_XY_STOP_INNER)
    stop_z0 = mm(P.GUIDE_XY_STOP_Z0)
    stop_z1 = mm(P.GUIDE_XY_STOP_Z1)
    stop_chamfer = mm(P.GUIDE_XY_STOP_CHAMFER)
    chamfer_z0 = stop_z1 - 0.8
    for angle in (0, 180):
        corner_stop = box(stop_inner, ledge_outer, ledge_inner, ledge_outer,
                          stop_z0, chamfer_z0, "guide_xy_stop_x")
        union(corner_stop,
              box(ledge_inner, ledge_outer, stop_inner, ledge_outer,
                  stop_z0, chamfer_z0, "guide_xy_stop_y"),
              prism([(stop_inner, chamfer_z0),
                     (stop_inner + stop_chamfer, stop_z1),
                     (ledge_outer, stop_z1), (ledge_outer, chamfer_z0)],
                    "y", ledge_inner, ledge_outer, "guide_xy_chamfer_x"),
              prism([(stop_inner, chamfer_z0),
                     (stop_inner + stop_chamfer, stop_z1),
                     (ledge_outer, stop_z1), (ledge_outer, chamfer_z0)],
                    "x", ledge_inner, ledge_outer, "guide_xy_chamfer_y"))
        transform(corner_stop, Matrix.Rotation(math.radians(angle), 4, "Z"))
        union(housing, corner_stop)

    # 円盤下面を受ける外周スラスト環。四方の柱で底から連続させる。

    support = annulus("cam_thrust_support", 46.9, 50.5, 40.9, 44.1, 160)

    union(housing, support)

    for angle in (0, 90, 180, 270):

        post = box(49.4, INNER + 0.2, -3.2, 3.2, z0, 44.1, "thrust_post")

        if angle in P.BOTTOM_LATCH_ANGLES_DEG:
            relief_top = mm(P.BOTTOM_TAB_Z1) + 0.2
            cut(post, prism([(51.0, 3.0), (INNER + 0.5, 3.0),
                             (INNER + 0.5, relief_top + INNER + 0.5 - 51.0),
                             (51.0, relief_top)],
                            "y", -4.2, 4.2, "bottom_tab_post_relief"))

        transform(post, Matrix.Rotation(math.radians(angle), 4, "Z"))

        union(housing, post)

    # ホーン受けの上昇を0.3mmで止める静止板。回転する角キーは円孔へ通す。

    stop = box(-21.0, 20.0, -11.0, 11.0, 40.8, 43.8, "coupler_stop")

    cut(stop, prism(circle((0, 0), 7.6, 96), "z", 40.5, 44.1, "coupler_stop_key_sweep"))

    union(housing, stop,

          box(19.8, 47.2, -1.6, 1.6, 40.8, 43.8, "coupler_stop_spoke_r"),

          box(-47.2, -20.8, -1.6, 1.6, 40.8, 43.8, "coupler_stop_spoke_l"))

    # SG92R本体の左右を0.35mm隙間で案内し、取付耳上面で上昇を止める。

    body_x0 = mm(P.SG.BODY_CENTER_X - P.SG.BODY_L / 2) - mm(P.SERVO_CLR)

    body_x1 = mm(P.SG.BODY_CENTER_X + P.SG.BODY_L / 2) + mm(P.SERVO_CLR)

    body_y = mm(P.SG.BODY_W) / 2 + mm(P.SERVO_CLR)

    for side in (-1, 1):

        ya, yb = ((-body_y - 2.4, -body_y) if side < 0 else (body_y, body_y + 2.4))

        rail = box(body_x0 - 0.2, body_x1 + 0.2, ya, yb, 3.2, 22.55, "servo_rail")

        floor_y0, floor_y1 = ((-INNER, yb) if side < 0 else (ya, INNER))

        floor = box(body_x0 - 0.2, body_x1 + 0.2, floor_y0, floor_y1,

                    3.2, 6.4, "servo_rail_floor")

        relief_y0, relief_y1 = ((-INNER - 0.5, -51.0) if side < 0 else (51.0, INNER + 0.5))
        cut(floor, box(-4.2, 4.2, relief_y0, relief_y1,
                       3.0, mm(P.BOTTOM_TAB_Z1) + 0.2, "bottom_tab_floor_relief"))

        union(housing, rail, floor)

    union(housing,

          box(-21.5, body_x0, -8.8, 8.8, 22.35, 25.55, "servo_flange_stop_l"),

          box(body_x1, 11.5, -8.8, 8.8, 22.35, 25.55, "servo_flange_stop_r"))

    # +Xへ出る配線用の外壁開口。

    cut(housing, box(49.0, HALF + 0.3, -4.0, 4.0, 6.5, 11.5, "wire_exit"))

    # 底板と天板の着脱爪用ポケット。

    for angle in P.BOTTOM_LATCH_ANGLES_DEG:

        pocket = box(INNER - 1.0, HALF + 0.3, -5.0, 5.0,
                     mm(P.BOTTOM_POCKET_Z0), mm(P.BOTTOM_POCKET_Z1), "bottom_latch_pocket")

        transform(pocket, Matrix.Rotation(math.radians(angle), 4, "Z"))

        cut(housing, pocket)

    for angle in (0, 180):

        face_pocket = box(INNER - 1.0, HALF + 0.3, -5.0, 5.0,
                          mm(P.FACE_POCKET_Z0), mm(P.FACE_POCKET_Z1), "face_latch_pocket")

        transform(face_pocket, Matrix.Rotation(math.radians(angle), 4, "Z"))

        cut(housing, face_pocket)

    housing.name = "housing"

    return housing





def build_bottom():

    bottom = box(-HALF, HALF, -HALF, HALF, 0, FRAME_T, "bottom")

    # 本体下面を0.35mmの隙間で支え、底板を外すとサーボを下へ抜ける。

    union(bottom, box(-16.5, 6.5, -6.0, 6.0, FRAME_T, 3.65, "servo_bottom_stop"))

    # 取付耳を下から通した後で、底板に一体化したX両端止めを閉じる。
    # Y幅は本体の12mm内へ収め、外装側の案内レールへ重ねない。
    body_x0 = mm(P.SG.BODY_CENTER_X - P.SG.BODY_L / 2) - mm(P.SERVO_CLR)
    body_x1 = mm(P.SG.BODY_CENTER_X + P.SG.BODY_L / 2) + mm(P.SERVO_CLR)
    body_y = mm(P.SG.BODY_W) / 2
    stop_t = mm(P.SERVO_X_STOP_T)
    stop_z1 = mm(P.SERVO_X_STOP_Z1)
    union(bottom,
          box(body_x0 - stop_t, body_x0, -body_y, body_y,
              FRAME_T - 0.2, stop_z1, "servo_x_stop_left"),
          box(body_x1, body_x1 + stop_t, -body_y, body_y,
              FRAME_T - 0.2, stop_z1, "servo_x_stop_right"))

    for angle in P.BOTTOM_LATCH_ANGLES_DEG:

        tab_outer = INNER - mm(P.EXTERIOR_TAB_CLR)
        tab_inner = tab_outer - mm(P.EXTERIOR_TAB_T)
        hook_outer = INNER + mm(P.EXTERIOR_HOOK_DEFLECTION)
        tab = box(tab_inner, tab_outer, -4.0, 4.0, FRAME_T - 0.2,
                  mm(P.BOTTOM_TAB_Z1), "bottom_tab")
        hook = box(tab_inner, hook_outer, -3.6, 3.6,
                   mm(P.BOTTOM_HOOK_Z0), mm(P.BOTTOM_HOOK_Z1), "bottom_hook")
        cut(hook, prism([(tab_outer, mm(P.BOTTOM_HOOK_Z1)),
                         (hook_outer + 0.3, mm(P.BOTTOM_HOOK_Z1)),
                         (hook_outer + 0.3, mm(P.BOTTOM_HOOK_Z1) - 1.0)],
                        "y", -4.0, 4.0, "bottom_hook_lead"))

        transform(tab, Matrix.Rotation(math.radians(angle), 4, "Z"))

        transform(hook, Matrix.Rotation(math.radians(angle), 4, "Z"))

        union(bottom, tab, hook)

    bottom.name = "bottom"

    return bottom





def build_faceplate():
    face = box(-HALF, HALF, -HALF, HALF, TOP_Z0, CAP_Z1, "faceplate")
    openings = []
    for cell in MOVING_AXIAL:
        center = axial_xy(*cell)
        openings.append(prism(hex_poly(*center, mm(P.HEX_OPEN_FLAT)), "z",
                              TOP_Z0 - 0.4, CAP_Z1 + 0.4, "face_open"))
    cut_collection(face, openings, "faceplate_openings")

    # 固定6枚は単一天板へ穴だけを開け、0.6mmの輪郭溝で可動面と外観をそろえる。
    for cell in FIXED_AXIAL:
        center = axial_xy(*cell)
        cut(face, prism(hex_poly(*center, mm(P.HEX_HOLE_FLAT)), "z",
                        TOP_Z0 - 0.4, CAP_Z1 + 0.4, "fixed_hole"))
        groove = prism(hex_poly(*center, mm(P.HEX_CAP_FLAT)), "z",
                       CAP_Z1 - 0.6, CAP_Z1 + 0.3, "fixed_outline_groove")
        cut(groove, prism(hex_poly(*center, mm(P.HEX_CAP_FLAT) - 0.8), "z",
                          CAP_Z1 - 0.8, CAP_Z1 + 0.5, "fixed_outline_inside"))
        cut(face, groove)

    # 四隅の柱が案内枠上面を0.3mm隙間で押さえ、天板の爪へ荷重を渡す。
    post_inner = mm(P.GUIDE_TOP_POST_INNER)
    post_outer = mm(P.GUIDE_TOP_POST_OUTER)
    post_z0 = mm(P.GUIDE_TOP_POST_Z0)
    for angle in (0, 90, 180, 270):
        post = box(post_inner, post_outer, post_inner, post_outer,
                   post_z0, TOP_Z0 + 0.2, "guide_top_post")
        transform(post, Matrix.Rotation(math.radians(angle), 4, "Z"))
        union(face, post)

    for angle in (0, 180):
        tab_outer = INNER - mm(P.EXTERIOR_TAB_CLR)
        tab_inner = tab_outer - mm(P.EXTERIOR_TAB_T)
        hook_outer = INNER + mm(P.EXTERIOR_HOOK_DEFLECTION)
        tab = box(tab_inner, tab_outer, -4.0, 4.0, 93.0, TOP_Z0 + 0.2, "face_tab")
        hook = box(tab_inner, hook_outer, -3.6, 3.6, 96.5, 98.5, "face_hook")
        cut(hook, prism([(tab_outer, 96.5), (hook_outer + 0.3, 96.5),
                         (hook_outer + 0.3, 97.5)],
                        "y", -4.0, 4.0, "face_hook_lead"))
        transform(tab, Matrix.Rotation(math.radians(angle), 4, "Z"))
        transform(hook, Matrix.Rotation(math.radians(angle), 4, "Z"))
        union(face, tab, hook)
    face.name = "faceplate"
    return face





def guide_points(group_index):

    angle = math.radians(P.FOLLOWER_ANGLES_DEG[group_index])

    return [(mm(P.GUIDE_INNER_R) * math.cos(angle), mm(P.GUIDE_INNER_R) * math.sin(angle)),

            (mm(P.CAM_RADII[group_index]) * math.cos(angle),

             mm(P.CAM_RADII[group_index]) * math.sin(angle))]





def build_carrier(group_index):

    group = P.GROUPS[group_index]

    cells = GROUP_AXIAL[group]

    centers = [axial_xy(*cell) for cell in cells]

    group_web_z0 = WEB_Z0 if group == "center" else mm(P.MOVING_WEB_Z0)

    group_web_z1 = group_web_z0 + FRAME_T

    carrier = ring_hex(centers[0], "carrier_" + group)

    for center in centers[1:]:

        union(carrier, ring_hex(center, "moving_hex"))

    # 同じ六角環を隠し梁高さにも置き、柱3本の荷重を群の梁へ渡す。

    for center in centers:

        union(carrier, ring_hex(center, "carrier_lower_ring", group_web_z0, group_web_z1))

    # 各六角環の下面を3本の柱で3.2mm荷重梁へつなぐ。

    for center in centers:

        for angle in (30, 150, 270):

            a = math.radians(angle)

            p = (center[0] + 6.25 * math.cos(a), center[1] + 6.25 * math.sin(a))

            union(carrier, prism(circle(p, 0.8, 24), "z",

                                 group_web_z0, CAP_Z0 + 0.2, "cap_post"))

    # 群内の六角を3.2mmの隠し梁で連結する。

    connected = [centers[0]]

    remaining = centers[1:]

    while remaining:

        point = min(remaining, key=lambda p: min((Vector(p) - Vector(q)).length for q in connected))

        near = min(connected, key=lambda q: (Vector(point) - Vector(q)).length)

        direction = (Vector(point) - Vector(near)).normalized()

        web_start = Vector(near) + direction * 5.8

        web_end = Vector(point) - direction * 5.8

        union(carrier, strip_xy(web_start, web_end, FRAME_T + 0.2,

                                group_web_z0, group_web_z1, "group_web"))

        connected.append(point)

        remaining.remove(point)

    # 中央群だけ梁を下へ分離し、他群が4mm下降しても0.3mmを残す。

    arm_z0 = mm(P.CENTER_ARM_Z0) if group == "center" else group_web_z0

    arm_z1 = arm_z0 + FRAME_T

    gp = guide_points(group_index)

    nearest = min(centers, key=lambda p: (Vector(p) - Vector(gp[0])).length)

    arm_direction = (Vector(gp[0]) - Vector(nearest)).normalized()

    arm_start = Vector(nearest) + arm_direction * 5.8

    union(carrier,

          strip_xy(arm_start, gp[0], FRAME_T + 0.2, arm_z0, arm_z1, "carrier_arm_inner"))

    if group == "lower_pair":

        # 固定下セルの貫通穴を避け、右側のセル間を通って外側案内へ戻す。

        route = [gp[0], (8.5, -24.0), (8.5, -35.0), gp[1]]

        for start, end in zip(route, route[1:]):

            union(carrier, capsule_xy(start, end, FRAME_T / 2,

                                      arm_z0, arm_z1, "carrier_arm_outer"))

    else:

        union(carrier, capsule_xy(gp[0], gp[1], FRAME_T / 2,

                                  arm_z0, arm_z1, "carrier_arm_outer"))

    for point_index, point in enumerate(gp):

        lug_z0 = (mm(P.FOLLOWER_HOME_Z + P.FOLLOWER_T) - 0.2

                  if point_index == 1 else GUIDE_Z0 - 4.0)

        union(carrier, box(point[0] - GUIDE_LUG / 2, point[0] + GUIDE_LUG / 2,

                           point[1] - GUIDE_LUG / 2, point[1] + GUIDE_LUG / 2,

                           lug_z0, arm_z1 - 0.2, "guide_lug"))

    # 扇形の接点。径方向2.0mm。周方向2.4mm。厚さ4.8mm。
    # 斜めの位置にある角形案内棒はトラック幅より広い。
    # 4mm下降時も棒の下端が谷外の平面へ触れない高さにする。

    foot = prism(annular_sector(mm(P.CAM_RADII[group_index]),

                                mm(P.FOLLOWER_RADIAL_W), mm(P.FOLLOWER_ARC_L)),

                 "z", mm(P.FOLLOWER_HOME_Z), mm(P.FOLLOWER_HOME_Z + P.FOLLOWER_T),

                 "follower_flatfoot")

    transform(foot, Matrix.Rotation(math.radians(P.FOLLOWER_ANGLES_DEG[group_index]), 4, "Z"))

    union(carrier, foot)

    # 隠し梁がセル開口へ残らないよう、全荷重部を一体化した後に穴だけを再切削する。

    for center in centers:

        cut(carrier, prism(hex_poly(*center, mm(P.HEX_HOLE_FLAT) + 0.05), "z",

                           CAP_Z1 - 10.0, CAP_Z1 + 0.4, "carrier_final_hex_hole"))

    carrier.name = "carrier_" + group

    return carrier





def build_guide_frame():

    edge = 50.2

    rail = FRAME_T

    frame = box(-edge, edge, -edge, -edge + rail, 76.0, 79.2, "guide_frame")

    union(frame,

          box(-edge, edge, edge - rail, edge, 76.0, 79.2, "guide_frame_front"),

          box(-edge, -edge + rail, -edge, edge, 76.0, 79.2, "guide_frame_left"),

          box(edge - rail, edge, -edge, edge, 76.0, 79.2, "guide_frame_right"))

    stop_z0, stop_z1 = mm(P.KEY_TOP_STOP_Z0), mm(P.KEY_TOP_STOP_Z1)
    bearing = chamfered_annulus(
        "cam_radial_bearing", mm(P.CAM_RADIAL_BEARING_INNER_R),
        mm(P.CAM_RADIAL_BEARING_OUTER_R), mm(P.CAM_RADIAL_BEARING_Z0),
        mm(P.CAM_RADIAL_BEARING_Z1), mm(P.CAM_RADIAL_BEARING_CHAMFER), 128)
    key_support = prism(circle((0, 0), mm(P.KEY_TOP_STOP_R), 128), "z",
                        stop_z0, stop_z1, "drive_key_top_stop")
    union(key_support,
          prism(circle((0, 0), mm(P.CAM_RADIAL_BEARING_OUTER_R), 128), "z",
                stop_z1 - 0.2, 79.4, "guide_center_column"),
          box(-48.8, -8.8, -1.6, 1.6, stop_z0, stop_z1, "drive_key_stop_arm"),
          box(-49.6, -47.6, -3.2, 3.2, stop_z0, 78.8, "drive_key_stop_post"))
    union(key_support, bearing)
    union(frame, key_support)

    for group_index in range(4):

        points = guide_points(group_index)

        for point_index, point in enumerate(points):

            outer = GUIDE_LUG + 2 * (mm(P.GUIDE_CLR) + GUIDE_WALL)

            inner = GUIDE_LUG + 2 * mm(P.GUIDE_CLR)

            sleeve = box(point[0] - outer / 2, point[0] + outer / 2,

                         point[1] - outer / 2, point[1] + outer / 2,

                         GUIDE_Z0, GUIDE_Z1, "guide_sleeve")

            cut(sleeve, box(point[0] - inner / 2, point[0] + inner / 2,

                            point[1] - inner / 2, point[1] + inner / 2,

                            GUIDE_Z0 - 0.3, GUIDE_Z1 + 0.3, "guide_bore"))

            direction = Vector(point).normalized()

            normal = Vector((-direction.y, direction.x)) * (rail / 2)

            if point_index == 0:

                spoke_start = Vector(point) - direction * (outer / 2 - 0.2)

                boundary = (direction.x * 8.8, direction.y * 8.8)

            else:

                scale = (edge + 0.4) / max(abs(direction.x), abs(direction.y))

                boundary = (direction.x * scale, direction.y * scale)

                spoke_start = Vector(point) + direction * (outer / 2 - 0.2)

            spoke_poly = [(spoke_start.x + normal.x, spoke_start.y + normal.y),

                          (boundary[0] + normal.x, boundary[1] + normal.y),

                          (boundary[0] - normal.x, boundary[1] - normal.y),

                          (spoke_start.x - normal.x, spoke_start.y - normal.y)]

            union(sleeve, prism(spoke_poly, "z", 75.8, 79.4, "guide_spoke"))
            union(frame, sleeve)

    frame.name = "guide_frame"

    return frame





def cleanup_wire(ob):

    bm = bmesh.new()

    bm.from_mesh(ob.data)

    zero_faces = [face for face in bm.faces if face.calc_area() <= 1e-12]

    middle_vertices = []

    for face in zero_faces:

        vertices = list(face.verts)

        middle = None

        for candidate in vertices:

            endpoints = [vertex for vertex in vertices if vertex is not candidate]

            segment = endpoints[1].co - endpoints[0].co

            if segment.length_squared <= 1e-16:

                continue

            t = (candidate.co - endpoints[0].co).dot(segment) / segment.length_squared

            closest = endpoints[0].co + t * segment

            if 0.0 < t < 1.0 and (candidate.co - closest).length <= 1e-5:

                middle = candidate

                break

        if middle is not None:

            middle_vertices.append(middle)

    if middle_vertices:

        bmesh.ops.dissolve_verts(bm, verts=list(set(middle_vertices)), use_face_split=False,

                                 use_boundary_tear=False)

    bm.normal_update()

    bm.to_mesh(ob.data)

    bm.free()

    ob.data.update()





def import_servo_ref(part):

    path = os.path.join(EXPORTS_DIR, f"sg92r-photo-{part}.stl")

    before = set(bpy.data.objects)

    bpy.ops.wm.stl_import(filepath=path)

    ob = next(item for item in bpy.data.objects if item not in before)

    ob.name = "servo_" + part

    transform(ob, Matrix.Translation((0, 0, mm(P.SERVO_Z0))))

    return ob





def build_print_test():
    # 実ホーン受け、角キー、案内、接点、止め爪の縮小試片。
    coupon = build_horn_coupler()
    transform(coupon, Matrix.Diagonal((1.0, -1.0, -1.0, 1.0)))
    place_on_bed(coupon, Matrix.Identity(4))
    coupon.name = "print_test_horn_coupler"

    key = build_drive_key()
    place_on_bed(key, Matrix.Diagonal((1.0, -1.0, -1.0, 1.0)))
    transform(key, Matrix.Translation((0, 25.0, 0)))
    transform(key, Matrix.Translation((28.0, 0, 0)))
    key.name = "print_test_drive_key"

    inner = GUIDE_LUG + 2 * mm(P.GUIDE_CLR)
    outer = inner + 2 * GUIDE_WALL
    guide = box(39.0 - outer / 2, 39.0 + outer / 2, -outer / 2, outer / 2,
                0, 12.0, "print_test_guide")
    cut(guide, box(39.0 - inner / 2, 39.0 + inner / 2, -inner / 2, inner / 2,
                   -0.3, 12.3, "print_test_guide_bore"))
    guide_foot = box(34.0, 44.0, -5.0, 5.0, 0, 0.4,
                     "print_test_guide_foot")
    cut(guide_foot, box(39.0 - inner / 2, 39.0 + inner / 2,
                        -inner / 2, inner / 2, -0.3, 0.7,
                        "print_test_guide_foot_bore"))
    union(guide, guide_foot)
    lug = box(49.0 - GUIDE_LUG / 2, 49.0 + GUIDE_LUG / 2,
              -GUIDE_LUG / 2, GUIDE_LUG / 2, 0, 12.0, "print_test_lug")
    union(lug, box(46.5, 51.5, -4.0, 4.0, 0, 1.2, "print_test_lug_handle"))

    track = box(58.0, 72.0, -5.0, 5.0, 0, 3.2, "print_test_track")
    foot = prism(annular_sector(mm(P.CAM_RADII[0]), mm(P.FOLLOWER_RADIAL_W),
                                mm(P.FOLLOWER_ARC_L)), "z", 0, mm(P.FOLLOWER_T),
                 "print_test_foot")
    transform(foot, Matrix.Translation((41.0, 0, 0)))

    keeper_free_end = 82.0 + mm(P.KEEPER_TAB_FREE_L)
    keeper_tab = box(82.0, keeper_free_end, -3.2, 3.2,
                     0, mm(P.KEEPER_TAB_T), "print_test_keeper_tab")
    union(keeper_tab, box(80.8, 84.0, -4.0, 4.0, 0, 3.2, "print_test_keeper_root"),
          box(keeper_free_end - 0.2,
              keeper_free_end + mm(P.KEEPER_TAB_INNER - P.KEEPER_HOOK_INNER),
              -3.2, 3.2, 0, mm(P.KEEPER_TAB_T), "print_test_keeper_hook"))
    ledge = box(96.0, 101.0, -5.0, 5.0, 0, 4.4, "print_test_keeper_ledge")
    cut(ledge, box(95.7, 99.3, -3.6, 3.6, 1.2, 4.7, "print_test_keeper_slot"))
    radial_bearing = chamfered_annulus(
        "print_test_radial_bearing", mm(P.CAM_RADIAL_BEARING_INNER_R),
        mm(P.CAM_RADIAL_BEARING_OUTER_R), 0,
        mm(P.CAM_RADIAL_BEARING_Z1 - P.CAM_RADIAL_BEARING_Z0),
        mm(P.CAM_RADIAL_BEARING_CHAMFER), 128)
    transform(radial_bearing, Matrix.Translation((116.0, 0, 0)))
    return [coupon, key, guide, lug, track, foot, keeper_tab, ledge, radial_bearing]





PRINT_TRANSFORMS = {

    "housing": Matrix.Identity(4),

    "faceplate": Matrix.Diagonal((1.0, -1.0, -1.0, 1.0)),

    "guide_frame": Matrix.Identity(4),

    "bottom": Matrix.Identity(4),

    "carrier_center": Matrix.Diagonal((1.0, -1.0, -1.0, 1.0)),

    "carrier_upper_left": Matrix.Diagonal((1.0, -1.0, -1.0, 1.0)),

    "carrier_upper_right": Matrix.Diagonal((1.0, -1.0, -1.0, 1.0)),

    "carrier_lower_pair": Matrix.Diagonal((1.0, -1.0, -1.0, 1.0)),

    "cam_disk": Matrix.Identity(4),

    "horn_coupler": Matrix.Diagonal((1.0, -1.0, -1.0, 1.0)),

    "drive_key": Matrix.Diagonal((1.0, -1.0, -1.0, 1.0)),

    "cam_keeper": Matrix.Diagonal((1.0, -1.0, -1.0, 1.0)),

}





def place_on_bed(ob, matrix):

    transform(ob, matrix)

    minimum = min(vertex.co.z for vertex in ob.data.vertices)

    transform(ob, Matrix.Translation((0, 0, -minimum)))





def split_print_support(ob, name):
    mesh = bmesh.new()
    mesh.from_mesh(ob.data)
    try:
        remaining = set(mesh.verts)
        components = []
        while remaining:
            seed = remaining.pop()
            vertices = [seed]
            pending = [seed]
            while pending:
                vertex = pending.pop()
                for edge in vertex.link_edges:
                    other = edge.other_vert(vertex)
                    if other in remaining:
                        remaining.remove(other)
                        vertices.append(other)
                        pending.append(other)
            faces = {face for vertex in vertices for face in vertex.link_faces}
            index = {vertex: position for position, vertex in enumerate(vertices)}
            data = bpy.data.meshes.new(name + "_mesh")
            data.from_pydata([tuple(vertex.co) for vertex in vertices], [],
                             [[index[vertex] for vertex in face.verts] for face in faces])
            data.update()
            component = bpy.data.objects.new(f"{name}_{len(components) + 1}", data)
            bpy.context.collection.objects.link(component)
            clean(component, dist=1e-5)
            components.append(component)
    finally:
        mesh.free()
        bpy.data.objects.remove(ob, do_unlink=True)
    return components


def sanitize_print_support(ob):
    mesh = bmesh.new()
    mesh.from_mesh(ob.data)
    bmesh.ops.remove_doubles(mesh, verts=mesh.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(mesh, edges=mesh.edges, dist=1e-5)
    mesh.verts.ensure_lookup_table()
    seen = {}
    remove = []
    for face in mesh.faces:
        key = tuple(sorted(vertex.index for vertex in face.verts))
        if face.calc_area() <= 1e-10 or key in seen:
            remove.append(face)
        else:
            seen[key] = face
    if remove:
        bmesh.ops.delete(mesh, geom=remove, context="FACES")
    bmesh.ops.recalc_face_normals(mesh, faces=mesh.faces)
    mesh.to_mesh(ob.data)
    mesh.free()
    ob.data.update()
    return ob


def build_carrier_web_supports(group_index):
    group = P.GROUPS[group_index]
    centers = [axial_xy(*cell) for cell in GROUP_AXIAL[group]]
    outer = None
    for center in centers:
        collar = prism(hex_poly(*center, 16.1), "z", 0, 2.7,
                       f"carrier_{group}_web_outer_print_support")
        cut(collar, prism(hex_poly(*center, 13.7), "z", -0.3, 3.0,
                          f"carrier_{group}_web_outer_support_bore"))
        if outer is None:
            outer = collar
        else:
            union(outer, collar)

    connected = [centers[0]]
    remaining = centers[1:]
    while remaining:
        point = min(remaining, key=lambda value: min(
            (Vector(value) - Vector(other)).length for other in connected))
        near = min(connected, key=lambda value: (Vector(point) - Vector(value)).length)
        direction = (Vector(point) - Vector(near)).normalized()
        web_start = Vector(near) + direction * 5.8
        web_end = Vector(point) - direction * 5.8
        union(outer, strip_xy(web_start, web_end, FRAME_T + 0.2, 0, 2.7,
                              f"carrier_{group}_web_bridge_print_support"))
        connected.append(point)
        remaining.remove(point)

    gp = guide_points(group_index)
    nearest = min(centers, key=lambda point: (Vector(point) - Vector(gp[0])).length)
    direction = (Vector(gp[0]) - Vector(nearest)).normalized()
    arm_start = Vector(nearest) + direction * 5.8
    union(outer, strip_xy(arm_start, gp[0], FRAME_T + 0.2, 0, 2.7,
                          f"carrier_{group}_arm_inner_print_support"))
    if group == "lower_pair":
        route = [gp[0], (8.5, -24.0), (8.5, -35.0), gp[1]]
        for start, end in zip(route, route[1:]):
            union(outer, capsule_xy(start, end, FRAME_T / 2, 0, 2.7,
                                    f"carrier_{group}_arm_outer_print_support"))
    else:
        union(outer, capsule_xy(gp[0], gp[1], FRAME_T / 2, 0, 2.7,
                                f"carrier_{group}_arm_outer_print_support"))

    for center in centers:
        cut(outer, prism(hex_poly(*center, 13.7), "z", -0.3, 3.0,
                         f"carrier_{group}_cap_clearance"))
    outer.name = f"carrier_{group}_web_outer_print_support"
    supports = split_print_support(outer, outer.name)
    for support in supports:
        transform(support, Matrix.Diagonal((1.0, -1.0, 1.0, 1.0)))
    return supports


def build_print_supports(name):

    supports = []

    if name == "carrier_center":

        supports.append(box(7.0, 33.8, -1.2, 1.2, 0, 10.5,

                            "carrier_center_arm_print_support"))

        inner_support = prism(hex_poly(0, 0, 8.9), "z", 0, 3.4,
                              "carrier_center_web_inner_print_support")
        union(inner_support, prism(hex_poly(0, 0, 9.7), "z", 3.4, 8.3,
                                   "carrier_center_web_inner_support_cap"))
        for angle in (30, 150, 270):
            radians = math.radians(angle)
            post_center = (6.25 * math.cos(radians), -6.25 * math.sin(radians))
            cut(inner_support, prism(circle(post_center, 1.05, 24), "z", 3.1, 8.8,
                                     "carrier_center_web_post_clearance"))
        supports.append(inner_support)
        outer_support = prism(hex_poly(0, 0, 16.1), "z", 0, 3.4,
                              "carrier_center_web_outer_print_support")
        cut(outer_support, prism(hex_poly(0, 0, 13.7), "z", -0.3, 8.8,
                                 "carrier_center_web_outer_support_bore"))
        outer_cap = prism(hex_poly(0, 0, 16.1), "z", 3.4, 8.3,
                          "carrier_center_web_outer_support_cap")
        cut(outer_cap, prism(hex_poly(0, 0, 12.9), "z", 3.1, 8.8,
                             "carrier_center_web_outer_support_cap_bore"))
        union(outer_support, outer_cap)
        cut(outer_support, box(6.8, 34.0, -1.4, 1.4, -0.3, 8.8,
                               "carrier_center_arm_support_clearance"))
        supports.append(outer_support)

    elif name.startswith("carrier_"):

        supports.extend(build_carrier_web_supports(
            P.GROUPS.index(name.removeprefix("carrier_"))))

    elif name == "guide_frame":
        print_z0 = mm(P.CAM_RADIAL_BEARING_Z0)
        sleeve_base_top = GUIDE_Z0 - print_z0 - 0.5
        sleeve_top = GUIDE_Z0 - print_z0 - 0.3
        spoke_top = 75.8 - print_z0 - 0.5
        frame_top = 76.0 - print_z0 - 0.5
        key_arm_top = mm(P.KEY_TOP_STOP_Z0) - print_z0 - 0.5

        guide_support = box(-49.8, -1.9, -49.8, -48.6, 0, frame_top,

                            "guide_frame_print_support")

        union(guide_support,
              box(1.9, 49.8, -49.8, -48.6, 0, frame_top,
                  "guide_support_back_right"),

              box(-1.9, 1.9, -49.8, -48.6, 0, spoke_top,
                  "guide_support_back_spoke"),

              box(-49.8, 49.8, 48.6, 49.8, 0, frame_top, "guide_support_front"),

              box(-49.8, -48.6, -49.8, 49.8, 0, frame_top, "guide_support_left"),

              box(48.6, 49.8, -49.8, 49.8, 0, frame_top, "guide_support_right"),

              box(-49.0, -12.6, -0.6, 0.6, 0, key_arm_top,
                  "guide_key_arm_print_support"))
        cut(guide_support,
            box(-50.1, -48.3, -3.6, 3.6, key_arm_top, frame_top + 0.3,
                "guide_post_support_relief"))

        sleeve_outer = GUIDE_LUG + 2 * (mm(P.GUIDE_CLR) + GUIDE_WALL)

        sleeve_supports = []

        for group_index in range(4):

            for point_index, point in enumerate(guide_points(group_index)):

                direction = Vector(point).normalized()

                if point_index == 1:
                    scale = 49.2 / max(abs(direction.x), abs(direction.y))
                    boundary = (direction.x * scale, direction.y * scale)
                    relief_scale = 51.0 / max(abs(direction.x), abs(direction.y))
                    relief_boundary = (direction.x * relief_scale,
                                       direction.y * relief_scale)
                    sleeve_ray = sleeve_outer / 2 / max(abs(direction.x), abs(direction.y))
                    support_start = Vector(point) + direction * (sleeve_ray + 1.2)
                    spoke_support = strip_xy(
                        support_start, boundary, 1.2, 0, spoke_top,
                        "guide_spoke_print_support")
                    cut(guide_support,
                        strip_xy(support_start, relief_boundary, 3.8, spoke_top,
                                 frame_top + 0.3, "guide_spoke_support_relief"))
                    union(guide_support, spoke_support)

                local_sleeve_base_top = sleeve_base_top
                local_sleeve_top = sleeve_top
                if group_index == 3 and point_index == 1:
                    local_sleeve_base_top -= 0.2
                    local_sleeve_top -= 0.2
                sleeve_support = box(
                    point[0] - sleeve_outer / 2, point[0] + sleeve_outer / 2,
                    point[1] - sleeve_outer / 2, point[1] + sleeve_outer / 2,
                    0, local_sleeve_base_top, "guide_sleeve_print_support")
                sleeve_cap = box(
                    point[0] - sleeve_outer / 2, point[0] + sleeve_outer / 2,
                    point[1] - sleeve_outer / 2, point[1] + sleeve_outer / 2,
                    local_sleeve_base_top, local_sleeve_top, "guide_sleeve_support_cap")
                cap_inner = (GUIDE_LUG + 2 * mm(P.GUIDE_CLR)) / 2 - 0.2
                cut(sleeve_cap,
                    box(point[0] - cap_inner, point[0] + cap_inner,
                        point[1] - cap_inner, point[1] + cap_inner,
                        local_sleeve_base_top - 0.3, local_sleeve_top + 0.3,
                        "guide_sleeve_support_cap_bore"))
                union(sleeve_support, sleeve_cap)
                sleeve_supports.append(sleeve_support)

        center_support = prism(circle((0, 0), 9.6, 96), "z", 0, key_arm_top - 0.2,
                               "guide_center_stop_print_support")
        supports.extend([guide_support, *sleeve_supports, center_support])

    elif name == "housing":

        sg = P.SG

        body_x0 = mm(sg.BODY_CENTER_X - sg.BODY_L / 2) - mm(P.SERVO_CLR)

        body_x1 = mm(sg.BODY_CENTER_X + sg.BODY_L / 2) + mm(P.SERVO_CLR)

        left_center = (-21.5 + body_x0) / 2

        right_center = (body_x1 + 11.5) / 2

        for center, suffix in ((left_center, "left"), (right_center, "right")):

            supports.append(box(center - 2.5, center + 2.5, -4.4, 4.4,

                                0, 18.55, f"housing_flange_{suffix}_print_support"))

        coupler_support = box(-6.0, 6.0, -5.5, 5.5, 0, 34.0,
                              "housing_coupler_stop_print_support")
        union(coupler_support,
              prism([(-6.0, 34.0), (6.0, 34.0), (9.0, 37.3), (-9.0, 37.3)],
                    "y", -5.5, 5.5, "coupler_support_cap_x"),
              prism([(-5.5, 34.0), (5.5, 34.0), (9.0, 37.3), (-9.0, 37.3)],
                    "x", -9.0, 9.0, "coupler_support_cap_y"),
              box(-46.8, -21.8, -1.2, 1.2, 0, 37.3,
                  "coupler_support_spoke_left"),
              box(12.0, 46.8, -1.2, 1.2, 0, 37.3,
                  "coupler_support_spoke_right"),
              box(-46.8, -21.8, 9.6, 11.0, 0, 37.3,
                  "coupler_support_edge_left_front"),
              box(-46.8, -21.8, -11.0, -9.6, 0, 37.3,
                  "coupler_support_edge_left_back"),
              box(12.0, 46.8, 9.6, 11.0, 0, 37.3,
                  "coupler_support_edge_right_front"),
              box(12.0, 46.8, -11.0, -9.6, 0, 37.3,
                  "coupler_support_edge_right_back"),
              box(-46.8, -45.6, -11.0, 11.0, 0, 37.3,
                  "coupler_support_left_tie"),
              box(45.6, 46.8, -11.0, 11.0, 0, 37.3,
                  "coupler_support_right_tie"))
        front_ramp = prism(
            [(5.3, 25.8), (6.5, 25.8), (10.8, 30.1),
             (10.8, 37.3), (8.8, 37.3), (8.8, 30.8), (5.3, 27.3)],
            "x", -6.0, 6.0, "coupler_support_front_ramp")
        back_ramp = prism(
            [(-5.3, 25.8), (-5.3, 27.3), (-8.8, 30.8),
             (-8.8, 37.3), (-10.8, 37.3), (-10.8, 30.1), (-6.5, 25.8)],
            "x", -6.0, 6.0, "coupler_support_back_ramp")
        union(coupler_support, front_ramp, back_ramp,
              prism([(-6.2, 31.3), (-5.0, 31.3), (-5.0, 37.3), (-12.0, 37.3)],
                    "y", 8.8, 10.8, "coupler_support_front_left_reach"),
              prism([(-6.2, 31.3), (-5.0, 31.3), (-5.0, 37.3), (-12.0, 37.3)],
                    "y", -10.8, -8.8, "coupler_support_back_left_reach"),
              box(-46.8, 46.8, 9.6, 11.0, 36.9, 37.3,
                  "coupler_support_front_roof"),
              box(-46.8, 46.8, -11.0, -9.6, 36.9, 37.3,
                  "coupler_support_back_roof"))
        supports.append(coupler_support)

    for support in supports:
        triangulate_export(support)
        sanitize_print_support(support)
    return supports




def triangulate_export(ob):

    bpy.context.view_layer.objects.active = ob

    modifier = ob.modifiers.new("export_triangulate", "TRIANGULATE")

    modifier.quad_method = "BEAUTY"

    modifier.ngon_method = "BEAUTY"

    bpy.ops.object.modifier_apply(modifier=modifier.name)

    clean(ob, dist=1e-5)





def refresh_manifest_metadata(manifest):
    meta = manifest['meta']
    meta['decisions'][1] = (f"扇形の平面接点は径方向幅{mm(P.FOLLOWER_RADIAL_W):g}mm。"
                            f"周方向長さ{mm(P.FOLLOWER_ARC_L):g}mm。厚さ{mm(P.FOLLOWER_T):g}mm。")
    meta['assembly_steps'] = [
        '箱の外で付属ホーンをホーン受けへ入れる。底側の+X寄りから所定高さへ上げて中央へ移す。',
        '配線の自由端を+X側の出口へ通す。',
        '箱の外でホーン未装着のSG92Rを起動する。90度で静止させる。',
        'SG92R本体を下側から案内へ入れる。出力軸を先に入れた付属ホーンへ差す。',
        '円盤を外周の支持環へ載せる。円盤の角穴を受けの盲穴へ合わせる。',
        '円盤の上から角キーを入れる。円盤止め輪を押し込む。',
        '駆動一式を15度へ戻す。',
        '箱の上で案内枠へ四群の格子を通す。組んだ一式を箱へ下ろす。',
        '天板を付ける。底板を閉じる。',
    ]
    meta['follower_dimensions_mm'] = {
        'radial_width': mm(P.FOLLOWER_RADIAL_W), 'arc_length': mm(P.FOLLOWER_ARC_L),
        'thickness': mm(P.FOLLOWER_T),
        'lug_bottom_at_full_dent': mm(P.FOLLOWER_HOME_Z + P.FOLLOWER_T - P.DENT_DEPTH) - 0.2,
        'cam_outside_valley_top': mm(P.FOLLOWER_HOME_Z),
    }
    return manifest


def main():

    clear_scene()

    os.makedirs(BUILD, exist_ok=True)

    parts = {

        "housing": build_housing(),

        "faceplate": build_faceplate(),

        "guide_frame": build_guide_frame(),

        "bottom": build_bottom(),

        "carrier_center": build_carrier(0),

        "carrier_upper_left": build_carrier(1),

        "carrier_upper_right": build_carrier(2),

        "carrier_lower_pair": build_carrier(3),

        "cam_disk": build_cam_disk(),

        "horn_coupler": build_horn_coupler(),

        "drive_key": build_drive_key(),

        "cam_keeper": build_cam_keeper(),

        "servo_body": import_servo_ref("body"),

        "servo_horn": import_servo_ref("horn"),

        "servo_wire": import_servo_ref("wire"),

    }

    tests = build_print_test()

    for name, ob in parts.items():

        if nonmanifold(ob) or component_count(ob) != 1:

            raise RuntimeError(

                f"{name}: non-manifold={nonmanifold(ob)}, connected_components={component_count(ob)}")

    for test in tests:

        if nonmanifold(test) or component_count(test) != 1:

            raise RuntimeError(

                f"{test.name}: non-manifold={nonmanifold(test)}, connected_components={component_count(test)}")



    for name, ob in parts.items():

        save_stl([ob], os.path.join(BUILD, name + ".stl"))

    save_stl(tests, os.path.join(BUILD, "print_test.stl"))

    print_support_metadata = {}

    print_component_counts = {}

    for name, matrix in PRINT_TRANSFORMS.items():

        if name == "cam_keeper":
            before = set(bpy.data.objects)
            bpy.ops.wm.stl_import(filepath=os.path.join(BUILD, name + ".stl"))
            printable = next(item for item in bpy.data.objects if item not in before)
            printable.name = "print_" + name
        else:
            printable = duplicate(parts[name], "print_" + name)

        if name == "faceplate" or name.startswith("carrier_"):

            # 大きな下面を組立座標で先に三角化し、180度反転後の再分割を避ける。

            triangulate_export(printable)

        place_on_bed(printable, matrix)

        supports = build_print_supports(name)

        for support in supports:

            if nonmanifold(support) or component_count(support) != 1:

                raise RuntimeError(
                    f"{support.name}: invalid print support; "
                    f"non-manifold={nonmanifold(support)}, "
                    f"connected_components={component_count(support)}")

        if nonmanifold(printable) or component_count(printable) != 1:

            raise RuntimeError(

                f"print_{name}: non-manifold={nonmanifold(printable)}, "

                f"connected_components={component_count(printable)}")

        save_stl([printable, *supports], os.path.join(BUILD, "print_" + name + ".stl"))

        print_component_counts[name] = 1 + len(supports)

        if supports:

            guide_print_z0 = mm(P.CAM_RADIAL_BEARING_Z0)
            print_support_metadata[name] = []
            for support in supports:
                support_top = round(max(vertex.co.z for vertex in support.data.vertices), 4)
                if support.name.startswith("carrier_center_arm"):
                    product_first, support_gcode, product_gcode = 10.7, 10.4, 10.8
                elif support.name.startswith("carrier_center_web"):
                    product_first, support_gcode, product_gcode = 8.8, 8.4, 8.8
                elif support.name.startswith("carrier_"):
                    product_first, support_gcode, product_gcode = 3.2, 2.8, 3.2
                elif support.name.startswith("guide_sleeve"):
                    product_first = round(GUIDE_Z0 - guide_print_z0, 4)
                    support_gcode = round(math.ceil((support_top - 1.0e-6) / 0.2) * 0.2, 4)
                    product_gcode = 24.2 if support.name.endswith(".007") else 24.4
                elif support.name.startswith("guide_center_stop"):
                    product_first = round(mm(P.KEY_TOP_STOP_Z0) - guide_print_z0, 4)
                    support_gcode, product_gcode = 3.6, 4.0
                elif name == "guide_frame":
                    product_first = round(76.0 - guide_print_z0, 4)
                    support_gcode, product_gcode = 27.8, 28.2
                elif support.name.startswith("housing_coupler_stop"):
                    product_first, support_gcode, product_gcode = 37.6, 37.2, 37.6
                else:
                    product_first, support_gcode, product_gcode = 19.15, 18.6, 19.0
                print_support_metadata[name].append({
                    "id": support.name,
                    "attachment": "separate_breakaway_clearance",
                    "bbox_mm": bbox(support),
                    "support_top_z_mm": support_top,
                    "product_first_z_mm": product_first,
                    "geometric_clearance_mm": round(product_first - support_top, 4),
                    "expected_last_support_gcode_z_mm": support_gcode,
                    "expected_first_product_gcode_z_mm": product_gcode,
                    "layer_height_mm": 0.2,
                    "material_face_gap_mm": 0.2,
                    "bed_origin_expected": True,
                    "removal": "印刷後に隙間へ薄いへらを入れ、外装内側から折って外す",
                    "physical_removal_verified": False,
                })

            if name == "guide_frame":

                print_support_metadata[name][0]["support_regions"] = [

                    {"region": "key_stop_arm",
                     "support_top_z_mm": round(mm(P.KEY_TOP_STOP_Z0) - guide_print_z0 - 0.5, 4),
                     "product_first_z_mm": round(mm(P.KEY_TOP_STOP_Z0) - guide_print_z0, 4),
                     "geometric_clearance_mm": 0.5,
                     "expected_last_support_gcode_z_mm": 3.8,
                     "expected_first_product_gcode_z_mm": 4.2,
                     "material_face_gap_mm": 0.2},

                    {"region": "four_outer_spokes",
                     "support_top_z_mm": round(75.8 - guide_print_z0 - 0.5, 4),
                     "product_first_z_mm": round(75.8 - guide_print_z0, 4),
                     "geometric_clearance_mm": 0.5,
                     "expected_last_support_gcode_z_mm": 27.6,
                     "expected_first_product_gcode_z_mm": 28.0,
                     "material_face_gap_mm": 0.2},

                    {"region": "outer_frame",
                     "support_top_z_mm": round(76.0 - guide_print_z0 - 0.5, 4),
                     "product_first_z_mm": round(76.0 - guide_print_z0, 4),
                     "geometric_clearance_mm": 0.5,
                     "expected_last_support_gcode_z_mm": 27.8,
                     "expected_first_product_gcode_z_mm": 28.2,
                     "material_face_gap_mm": 0.2},

                ]



    labels = {

        "housing": "外装", "faceplate": "六角格子の天板", "guide_frame": "格子の案内枠",

        "bottom": "底板", "carrier_center": "中央", "carrier_upper_left": "左上",

        "carrier_upper_right": "右上", "carrier_lower_pair": "下側", "cam_disk": "四群円盤カム",

        "horn_coupler": "ホーン受け", "drive_key": "角形駆動キー", "cam_keeper": "円盤止め輪",

        "servo_body": "SG92R本体", "servo_horn": "付属クロスホーン", "servo_wire": "SG92R配線",

    }

    colors = {name: ("#335d91" if name == "servo_body" else "#f5f5f2" if name == "servo_horn"

                     else "#756d65" if name == "servo_wire" else "#34383a" if name in

                     ("cam_disk", "horn_coupler", "drive_key", "cam_keeper") else "#ecece8")

              for name in parts}

    explodes = {

        "housing": [0, 0, 0], "faceplate": [0, 0, 30], "guide_frame": [0, 0, 18],

        "bottom": [0, 0, -24], "carrier_center": [0, 0, 42],

        "carrier_upper_left": [-18, 0, 34], "carrier_upper_right": [18, 0, 34],

        "carrier_lower_pair": [0, -18, 28], "cam_disk": [0, 0, -18],

        "horn_coupler": [0, -22, -18], "drive_key": [0, 22, -18],

        "cam_keeper": [0, 0, 12], "servo_body": [-25, 0, -25],

        "servo_horn": [0, -30, -22], "servo_wire": [25, 0, -25],

    }

    manifest_parts = []

    for name in parts:

        manifest_parts.append({

            "id": name,

            "label": labels[name],

            "assembly": f"build/{name}.stl",

            "print": None if name in SERVO_REFS else f"build/print_{name}.stl",

            "fit_test": False,

            "color": colors[name],

            "explode": explodes[name],

            "expected_assembly_components": 1,

            "expected_print_components": print_component_counts.get(name, 1),

        })

        if name in print_support_metadata:

            manifest_parts[-1]["print_supports"] = print_support_metadata[name]

    manifest_parts.append({"id": "print_test", "label": "ホーン受け・角キー・径受け試片",

                           "assembly": "build/print_test.stl", "print": "build/print_test.stl",

                           "fit_test": True, "fit_only": True, "expected_assembly_components": 9,

                           "expected_print_components": 9, "color": "#d9d1bf", "explode": [0, -60, 0]})

    manifest = {

        "meta": {

            "dimensions_mm": [110, 110, 110],

            "max_dimensions_mm": [110, 110, 110],

            "exterior_parts": ["housing", "bottom", "faceplate"],

            "description": "4本の独立した面カムで19枚の穴あき六角面から4群を選んで沈める住人の箱C4-2。",

            "assembly_steps": [

                "底板を外し、SG92Rを底から案内へ入れて配線を+X壁の出口へ通す。",

                "サーボを90度で静止させ、付属ホーンへ非対称ホーン受けを下向きに差す。",

                "円盤カムの角穴を駆動キーへ合わせ、外周をスラスト支持環へ載せる。",

                "円盤カムの角穴から角形駆動キーを入れ、ホーン受けの上側盲穴へ差す。",

                "円盤止め輪を上から押し、4本の爪を支持環の下面へ掛ける。",

                "4群の格子を案内枠へ通し、扇形平面従動子を各トラックへ載せる。",

                "案内枠と六角格子の天板を上から入れ、2本の爪を外装へ掛ける。",

                "底板を押し込み、2本の爪を外装へ掛ける。",

            ],

            "decisions": [

                "中央、左上、右上、下側の4群へ半径33/37/41/45mmの独立トラックを割り当てた。",

                "扇形平面従動子は径方向2.0mm、周方向3mm、厚さ3.2mmとした。",

                "円盤外周を静止環で受け、SG92R出力軸へ円盤の軸荷重を渡さない。",

                "円盤中央bossを片側0.2mm隙間の円環で受け、径方向の移動を止めた。",

                "円盤止め輪は自由長7mm、厚さ1.2mmの4爪で着脱する原型とした。",

                "各群は2本の角柱を19mm長の静止案内へ通し、両端で8mm以上の係合を残した。",

                "案内枠は外装四隅の45度リブ付き棚へ載せ、対角L字面と天板四隅柱で六方向を保持する。",

            ],

            "limitations": [

                "重力で面カムへ追従するため天面上向き専用。",

                "ホーン嵌合、円盤止め輪の保持力、印刷収縮は実物未検証。",

                "全150度の運動と組立の合否は別の実STL検査記録で確認する。",

            ],

            "retention_interfaces": {

                "servo_body_x_minus": {

                    "contact_bbox_mm": [[-17.05, -6.2, 3.8], [-16.65, 6.2, 25.75]],

                    "nominal_gap_mm": 0.35, "receiver": "bottom"},

                "servo_body_x_plus": {

                    "contact_bbox_mm": [[6.65, -6.2, 3.8], [7.05, 6.2, 25.75]],

                    "nominal_gap_mm": 0.35, "receiver": "bottom"},

                "servo_body_y_minus": {

                    "contact_bbox_mm": [[-17.25, -6.55, 3.8], [7.25, -6.15, 22.75]],

                    "nominal_gap_mm": 0.35, "receiver": "housing"},

                "servo_body_y_plus": {

                    "contact_bbox_mm": [[-17.25, 6.15, 3.8], [7.25, 6.55, 22.75]],

                    "nominal_gap_mm": 0.35, "receiver": "housing"},

                "servo_body_z_minus": {

                    "contact_bbox_mm": [[-16.5, -6.0, 3.45], [6.5, 6.0, 3.85]],

                    "nominal_gap_mm": 0.35, "receiver": "bottom"},

                "servo_body_z_plus": {

                    "contact_bbox_mm": [[-21.5, -8.8, 22.15], [11.5, 8.8, 22.55]],

                    "nominal_gap_mm": 0.35, "receiver": "housing"},

                "guide_frame_x_minus": {
                    "contact_bbox_mm": [[-50.6, -52.8, 75.7], [-50.2, -47.0, 80.2]],
                    "nominal_gap_mm": 0.2, "receiver": "housing"},

                "guide_frame_x_plus": {
                    "contact_bbox_mm": [[50.2, 47.0, 75.7], [50.6, 52.8, 80.2]],
                    "nominal_gap_mm": 0.2, "receiver": "housing"},

                "guide_frame_y_minus": {
                    "contact_bbox_mm": [[-52.8, -50.6, 75.7], [-47.0, -50.2, 80.2]],
                    "nominal_gap_mm": 0.2, "receiver": "housing"},

                "guide_frame_y_plus": {
                    "contact_bbox_mm": [[47.0, 50.2, 75.7], [52.8, 50.6, 80.2]],
                    "nominal_gap_mm": 0.2, "receiver": "housing"},

                "guide_frame_z_minus": {
                    "contact_bbox_mm": [[-52.8, -52.8, 75.8], [52.8, 52.8, 76.2]],
                    "nominal_gap_mm": 0.0, "receiver": "housing"},

                "guide_frame_z_plus": {
                    "contact_bbox_mm": [[-50.0, -50.0, 79.0], [50.0, 50.0, 79.7]],
                    "nominal_gap_mm": 0.3, "receiver": "faceplate"},

                "horn_coupler_drive_key": {"bbox_mm": [[-5.0, -5.0, 37.55], [5.0, 5.0, 40.5]],

                                             "insertion": "+Z"},

                "drive_key_cam_disk": {"bbox_mm": [[-5.0, -5.0, 44.1], [5.0, 5.0, 50.3]],

                                        "insertion": "+Z"},

                "drive_key_head_stop": {"bbox_mm": [[-8.5, -8.5, 50.5], [8.5, 8.5, 52.0]],

                                          "axial_play_mm": 0.3,

                                          "release": "guide_frameを上へ外す"},

                "cam_flange_support": {"bbox_mm": [[-49.0, -49.0, 44.1], [49.0, 49.0, 47.6]],

                                        "insertion": "+Z"},

                "cam_radial_bearing": {
                    "bbox_mm": [[-12.0, -12.0, 47.8], [12.0, 12.0, 52.7]],
                    "boss_radius_mm": 10.0, "bearing_inner_radius_mm": 10.2,
                    "radial_clearance_mm": 0.2, "insertion": "+Z"},

                "cam_keeper_snap": {
                    "local_bbox_mm": [[mm(P.KEEPER_HOOK_INNER), -3.2, mm(P.KEEPER_HOOK_Z0)],
                                      [mm(P.KEEPER_TAB_INNER + P.KEEPER_TAB_T), 3.2, 48.0]],
                    "deflection_mm": mm(P.KEEPER_TAB_DEFLECTION),
                    "free_length_mm": mm(P.KEEPER_TAB_FREE_L),
                    "strain_percent": round(150 * P.KEEPER_TAB_T * P.KEEPER_TAB_DEFLECTION
                                            / P.KEEPER_TAB_FREE_L ** 2, 6),
                    "angles_deg": list(P.KEEPER_ANGLES_DEG), "count": 4},

                "faceplate_snap": {
                    "local_bbox_mm": [[INNER - mm(P.EXTERIOR_TAB_CLR + P.EXTERIOR_TAB_T), -4.0, 93.0],
                                      [INNER + mm(P.EXTERIOR_HOOK_DEFLECTION), 4.0, TOP_Z0 + 0.2]],
                    "deflection_mm": mm(P.EXTERIOR_HOOK_DEFLECTION),
                    "free_length_mm": round(TOP_Z0 - 98.5, 6),
                    "strain_percent": round(150 * mm(P.EXTERIOR_TAB_T) * mm(P.EXTERIOR_HOOK_DEFLECTION)
                                            / (TOP_Z0 - 98.5) ** 2, 6),
                    "angles_deg": [0, 180], "count": 2},

                "bottom_snap": {
                    "local_bbox_mm": [[INNER - mm(P.EXTERIOR_TAB_CLR + P.EXTERIOR_TAB_T), -4.0, FRAME_T - 0.2],
                                      [INNER + mm(P.EXTERIOR_HOOK_DEFLECTION), 4.0, mm(P.BOTTOM_TAB_Z1)]],
                    "deflection_mm": mm(P.EXTERIOR_HOOK_DEFLECTION),
                    "free_length_mm": round(mm(P.BOTTOM_HOOK_Z0) - FRAME_T, 6),
                    "strain_percent": round(150 * mm(P.EXTERIOR_TAB_T) * mm(P.EXTERIOR_HOOK_DEFLECTION)
                                            / (mm(P.BOTTOM_HOOK_Z0) - FRAME_T) ** 2, 6),
                    "angles_deg": [90, 270], "count": 2},

            },

        },

        "parts": manifest_parts,

    }

    write_json(os.path.join(BUILD, "manifest.json"), refresh_manifest_metadata(manifest))

    motion.write_motion()

    write_json(os.path.join(BUILD, "model_report.json"), {

        "parts": {name: {"bbox_mm": bbox(ob), "volume_mm3": round(volume(ob), 3),

                          "nonmanifold_edges": nonmanifold(ob),

                          "connected_components": component_count(ob)}

                  for name, ob in parts.items() if name not in SERVO_REFS},

        "group_cells_axial": GROUP_AXIAL,

        "fixed_cells_axial": FIXED_AXIAL,

        "print_supports": print_support_metadata,

        "expected_print_components": print_component_counts,

        "cam_mesh": {"angular_step_deg": 0.25, "track_width_mm": mm(P.CAM_TRACK_W),

                     "track_radii_mm": [mm(value) for value in P.CAM_RADII],
                     "radial_bearing_mm": {
                         "boss_radius": mm(P.CAM_RADIAL_BEARING_R),
                         "inner_radius": mm(P.CAM_RADIAL_BEARING_INNER_R),
                         "outer_radius": mm(P.CAM_RADIAL_BEARING_OUTER_R),
                         "z": [mm(P.CAM_RADIAL_BEARING_Z0),
                               mm(P.CAM_RADIAL_BEARING_Z1)]}},

    })



    export_objects = list(parts.values())

    for ob in export_objects:

        transform(ob, Matrix.Scale(0.001, 4))

    export_stl(P.MODEL_ID, only=export_objects)





if __name__ == "__main__":

    if '--metadata-only' in sys.argv:
        with open(os.path.join(BUILD, 'manifest.json'), encoding='utf-8') as stream:
            metadata = json.load(stream)
        write_json(os.path.join(BUILD, 'manifest.json'), refresh_manifest_metadata(metadata))
        print('manifest metadata refreshed; STL unchanged')
    else:
        main()
