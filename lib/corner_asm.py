"""角一式を組んだ状態の確認用 STL を作る（印刷には使わない）。

部品の STL（M 字・エルボ・板）を exports から読んで角の配置に置き、パイプを円柱で足す。
板の置き方だけ呼ぶ側（pipe-foot-corner / pipe-foot-corner-one の asm.py）が渡す。
世界座標: 角の節点が原点、A の脚が x 軸上の負側、B の脚が y 軸上の負側、床が z=0。
脚は ASM_LEG_L に縮めてある（実物は約 900）。
"""
import os
import math

import bpy
from mathutils import Matrix, Vector
import foot_core as fc

ASM_LEG_L = 300.0                         # 脚パイプの長さ（確認用に短く）
ASM_RAIL_EXT = 120.0                      # レールを M 字の絞る面から壁側へ出す長さ
ASM_FIFTH_ABOVE = 60.0                    # 5 本目を中央レールの軸より上へ出す量
T_SOCKET_OD = 37.0                        # 5 本目の側面ソケット（市販継手）の外径（仮）


def load_stl(exports_dir, name, filename):
    path = os.path.join(exports_dir, filename)
    assert os.path.exists(path), f"先に部品を出しておく: {path}"
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.stl_import(filepath=path, global_scale=0.001)
    ob = bpy.context.selected_objects[0]
    ob.name = name
    return ob


def place(ob, rot_z_deg, tx, ty, tz):
    ob.matrix_world = (Matrix.Translation(Vector((tx, ty, tz)) * fc.MM)
                       @ Matrix.Rotation(math.radians(rot_z_deg), 4, "Z") @ ob.matrix_world)
    fc.activate(ob)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return ob


def pipe(name, p0, p1, r):
    """p0 → p1（mm）の円柱。"""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    ob = fc.revolve(name, [(0.0, r), (d.length, r)], None, 48)
    ob.matrix_world = Matrix.Translation(a * fc.MM) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()
    fc.activate(ob)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return ob


def build_asm(P, C, exports_dir, name, boards):
    """P: pipe-foot-pair の params、C: pipe-corner の params。
    boards: [(stl ファイル名, Z 回転 deg, tx, ty, tz)] 床側の部品の置き方。"""
    J = P.J
    h_center = P.SEAT_Z + ASM_LEG_L - J.LEG_TOP_Z     # 中央レールの軸の高さ
    h_side = h_center + J.SIDE_Z                       # 左右レールの軸の高さ
    co = C.CORNER_OFF
    shift = C.JOINT_SHIFT
    mc = co + P.SPAN / 2                               # M 字の中心（脚 2 本の中点）の、軸線からの距離
    arc_c = -(co - C.R_INNER)                          # 同心の中心 (arc_c, arc_c)
    f = (-mc, -mc)                                     # 5 本目
    a_legs = [(-co, -shift), (-co - P.SPAN, -shift)]
    b_legs = [(-shift, -co), (-shift, -co - P.SPAN)]
    r_pipe = P.PIPE_OD / 2
    parts = []

    for k, (fn, rot, tx, ty, tz) in enumerate(boards):
        parts.append(place(load_stl(exports_dir, "board%d" % k, fn), rot, tx, ty, tz))

    # M 字 2 つ（設計の向きの STL: レール = X、脚の並び = Y、上 = Z。脚の軸は X = LEG_X）
    # A: レールは世界 y。平らな面（-X）を角（-y）へ。ローカル +X → 世界 +y は Rz(+90)。
    #    脚の中心が世界 y = -shift に来るよう平行移動する。
    parts.append(place(load_stl(exports_dir, "joint_a", "pipe_joint_28.stl"), 90, -mc, -J.LEG_X - shift, h_center))
    # B: レールは世界 x。平らな面を角（-x）へ。ローカル +X → 世界 +x（回さない）
    parts.append(place(load_stl(exports_dir, "joint_b", "pipe_joint_28.stl"), 0, -J.LEG_X - shift, -mc, h_center))

    # エルボ 2 つ（ローカル: 円弧の中心が原点、口は -x と -y を向く。世界では +x / +y を向く）
    for nm, fn in (("elbow_in", "pipe_corner_in_28.stl"), ("elbow_out", "pipe_corner_out_28.stl")):
        parts.append(place(load_stl(exports_dir, nm, fn), 180, arc_c, arc_c, h_side))

    # パイプ
    for i, (x, y) in enumerate(a_legs + b_legs):
        parts.append(pipe("leg%d" % i, (x, y, P.SEAT_Z), (x, y, P.SEAT_Z + ASM_LEG_L), r_pipe))
    parts.append(pipe("fifth", (f[0], f[1], P.SEAT_Z), (f[0], f[1], h_center + ASM_FIFTH_ABOVE), r_pipe))
    # 5 本目の側面ソケット（+y = A の面へ、+x = B の面へ）
    parts.append(pipe("tsock_a", (f[0], f[1] + r_pipe, h_center),
                      (f[0], f[1] + r_pipe + P.SIDE_JOINT_L, h_center), T_SOCKET_OD / 2))
    parts.append(pipe("tsock_b", (f[0] + r_pipe, f[1], h_center),
                      (f[0] + r_pipe + P.SIDE_JOINT_L, f[1], h_center), T_SOCKET_OD / 2))
    # レール。壁側の端は絞る面（-LEG_X + X_TOP）から ASM_RAIL_EXT
    wall = -J.LEG_X + J.X_TOP + ASM_RAIL_EXT - shift
    for k, x in enumerate((a_legs[0][0], a_legs[1][0])):          # A の左右レール → エルボの接点まで
        parts.append(pipe("rail_a%d" % k, (x, wall, h_side), (x, arc_c, h_side), r_pipe))
    parts.append(pipe("rail_a_c", (-mc, wall, h_center),
                      (-mc, f[1] + r_pipe + P.SIDE_JOINT_L - 25, h_center), r_pipe))
    for k, y in enumerate((b_legs[0][1], b_legs[1][1])):
        parts.append(pipe("rail_b%d" % k, (wall, y, h_side), (arc_c, y, h_side), r_pipe))
    parts.append(pipe("rail_b_c", (wall, -mc, h_center),
                      (f[0] + r_pipe + P.SIDE_JOINT_L - 25, -mc, h_center), r_pipe))

    # 1 つにまとめて書き出す（boolean はしない。重なったままの別々の殻）
    bpy.ops.object.select_all(action="DESELECT")
    for ob in parts:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    asm = bpy.context.active_object
    asm.name = name

    os.makedirs(exports_dir, exist_ok=True)
    stl = os.path.join(exports_dir, name + ".stl")
    bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True, global_scale=1000.0, ascii_format=False)
    print("Exported:", stl)
    print("bbox mm:", [round(v * 1000, 2) for v in asm.dimensions])
    print(f"[asm] 中央レールの軸 z={h_center:.1f} / 左右レール z={h_side:.1f} / 5 本目 {f} / 同心の中心 ({arc_c}, {arc_c})")
    return asm
