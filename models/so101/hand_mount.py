"""グリッパの先を、ロボットハンドと「配線の箱」に付け替える。

形の出どころは table-duo-vr の Robot Hand（VR Hands Starter Pack、購入アセット）。
このリポジトリは公開なので、FBX は hand_src/（git 管理外）に置き、作った STL も
build/ と exports/（どちらも git 管理外）にしか書かない。FBX が無ければ元のグリッパのまま作る。

座標はすべて gripper_link 座標（m）。z が負の向きが先端、+x が可動あごの側（掌を向ける側）。

  くちばし（固定あごの先）を z < CUT_Z で切り落とし、可動あごは外す
  → 本体の下に中空の箱を一体で付ける（8Servos Unit と指のサーボ線を入れる）
  → 箱の底を取付板でふさぎ、板にハンドの手首の円盤を載せる（板とハンドは一体で刷る）
     板の四隅は M2 のタッピングねじで箱のボスへ留める。中央の穴は指の線をハンドから箱へ通す
  → 手の甲側（−x）の壁の上に、Grove と 5V の線を腕の方へ出す切り欠き
"""
from __future__ import annotations

from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
FBX = HERE / "hand_src" / "RobotHand.fbx"
MM = 0.001

# 箱の外形は元のグリッパ本体の幅にそろえる（gripper_link 座標、mm。STL を断面で測った値）
BOX_X = (-35.2, 30.0)
BOX_Y = (-28.0, 24.0)
CUT_Z = -40.0            # これより先のくちばしを切る。本体の受け（servo-6 の下面 −35.8）より 4 mm 先
BOX_TOP = -38.0          # 箱は本体へ 2 mm 食い込ませて一体にする
WALL = 2.0
TOP_WALL = 2.4
PLATE_T = 3.0
BOSS_D, BOSS_H = 6.0, 10.0
PILOT_D, PILOT_DEPTH = 1.8, 8.0     # M2 タッピング
CLEAR_D = 2.4                       # 取付板の M2 通し穴
CABLE_HOLE = (18.0, 10.0)           # 指の線を通す穴（x 方向, y 方向）
CABLE_RISE = 20.0                   # 手首の円盤の中へ通す深さ
SLOT = (16.0, 8.0)                  # 甲側の壁の切り欠き（y 方向の幅, z 方向の高さ）
VOXEL = 0.35                        # ハンドを 1 個の閉じた形にするときの格子（mm）


def _box(name, x, y, z):
    """mm の範囲で直方体を作る。"""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(((x[1] - x[0]) * MM, (y[1] - y[0]) * MM, (z[1] - z[0]) * MM)), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector((sum(x) / 2 * MM, sum(y) / 2 * MM, sum(z) / 2 * MM)), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def _cyl(name, cx, cy, z, d, segments=32):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=d / 2 * MM, radius2=d / 2 * MM,
                          depth=(z[1] - z[0]) * MM)
    bmesh.ops.translate(bm, vec=Vector((cx * MM, cy * MM, sum(z) / 2 * MM)), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def _boolean(target, tool, op):
    mod = target.modifiers.new(f"{op}-{tool.name}", "BOOLEAN")
    mod.operation, mod.object, mod.solver = op, tool, "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool, do_unlink=True)


def _bake(ob, matrix):
    ob.data.transform(matrix)
    ob.matrix_world = Matrix.Identity(4)


def _boss_centers():
    # ボスは内壁へ 1 mm 食い込ませる（壁に接するだけだと、接線で面が重なって開いた辺が残る）
    inset = WALL + BOSS_D / 2 - 1.0
    xi = (BOX_X[0] + inset, BOX_X[1] - inset)
    yi = (BOX_Y[0] + inset, BOX_Y[1] - inset)
    return [(x, y) for x in xi for y in yi]


def _wiring_box(bottom):
    """中空の箱（底は開いている）。ボスと甲側の切り欠きつき。"""
    box = _box("wiring-box", BOX_X, BOX_Y, (bottom, BOX_TOP))
    cavity = _box("cavity", (BOX_X[0] + WALL, BOX_X[1] - WALL), (BOX_Y[0] + WALL, BOX_Y[1] - WALL),
                  (bottom - 1.0, BOX_TOP - TOP_WALL))
    # ボスは空洞から削り残す。足し算で付けると、ボスの底が箱の底と同じ面に重なって開いた辺が出る
    for i, (x, y) in enumerate(_boss_centers()):
        _boolean(cavity, _cyl(f"boss{i}", x, y, (bottom - 2.0, bottom + BOSS_H), BOSS_D), "DIFFERENCE")
    _boolean(box, cavity, "DIFFERENCE")
    for i, (x, y) in enumerate(_boss_centers()):
        _boolean(box, _cyl(f"pilot{i}", x, y, (bottom - 1.0, bottom + PILOT_DEPTH), PILOT_D, 16), "DIFFERENCE")
    cy = sum(BOX_Y) / 2
    top_in = BOX_TOP - TOP_WALL
    _boolean(box, _box("slot", (BOX_X[0] - 1.0, BOX_X[0] + WALL + 1.0), (cy - SLOT[0] / 2, cy + SLOT[0] / 2),
                       (top_in - SLOT[1], top_in)), "DIFFERENCE")
    return box


def _load_hand(side, scale_m):
    """FBX の手（side="Right"|"Left"）を、骨の初期姿勢のまま 1 個のメッシュにする（FBX 座標 × scale）。"""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(FBX))
    imported = [o for o in bpy.data.objects if o not in before]
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    for o in imported:
        if o.type != "MESH" or not o.name.startswith(side + "."):
            continue
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        me.transform(o.matrix_world)
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    for o in imported:
        bpy.data.objects.remove(o, do_unlink=True)
    bmesh.ops.scale(bm, vec=Vector((scale_m, scale_m, scale_m)), verts=bm.verts)
    me = bpy.data.meshes.new("hand")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("hand", me)
    bpy.context.collection.objects.link(ob)
    return ob


def _voxel_remesh(ob, size_mm):
    ob.data.remesh_voxel_size = size_mm * MM
    ob.data.use_remesh_fix_poles = True
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.ops.object.voxel_remesh()


def _islands(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    seen, count = set(), 0
    for v in bm.verts:
        if v.index in seen:
            continue
        count += 1
        stack = [v]
        while stack:
            a = stack.pop()
            if a.index in seen:
                continue
            seen.add(a.index)
            stack.extend(e.other_vert(a) for e in a.link_edges)
    bad = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    return count, bad


def apply(parts, frames, P):
    """parts: [{id,label,printed,ob,placed}]。手直しの一覧（日本語 1 行ずつ）を返す。"""
    if not P.HAND:
        return []
    if not FBX.exists():
        print(f"[hand] {FBX} が無いので元のグリッパのまま作ります（購入アセットは git に無い）")
        return ["ハンドの FBX が無いので元のグリッパのまま"]
    by_id = {p["id"]: p for p in parts}
    grip = frames["gripper_link"]
    to_link = grip.inverted()

    # 1. 本体: くちばしを切り、箱を一体で付ける
    body = by_id["gripper-fixed-jaw"]
    _bake(body["ob"], to_link @ body["placed"])
    body["placed"] = grip
    _boolean(body["ob"], _box("cut", (-80, 80), (-80, 80), (-200, CUT_Z)), "DIFFERENCE")
    bottom = BOX_TOP - P.BOX_HEIGHT * 1000.0
    _boolean(body["ob"], _wiring_box(bottom), "UNION")
    body["label"] = "グリッパ本体（配線の箱つき）"

    # 2. 可動あごは外す（指はハンドのサーボが動かす）
    parts[:] = [p for p in parts if p["id"] != "gripper-moving-jaw"]
    bpy.data.objects.remove(by_id["gripper-moving-jaw"]["ob"], do_unlink=True)

    # 3. ハンド + 取付板（一体）。手首の中心を箱の中心に、指を −z、掌を +x（元の可動あごの側）へ
    cx, cy = sum(BOX_X) / 2, sum(BOX_Y) / 2
    plate_top, plate_bot = bottom, bottom - PLATE_T
    hand = _load_hand(P.HAND_SIDE, P.HAND_SCALE)
    # FBX: 指 +Z、掌 +Y、親指 ±X  →  link: 指 −z、掌 +x、FBX の X は +y
    R = Matrix(((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))
    _bake(hand, Matrix.Translation(Vector((cx * MM, cy * MM, plate_bot * MM))) @ R)
    plate = _box("plate", BOX_X, BOX_Y, (plate_bot, plate_top))
    bm = bmesh.new()
    bm.from_mesh(hand.data)
    bm.from_mesh(plate.data)
    bm.to_mesh(hand.data)
    bm.free()
    bpy.data.objects.remove(plate, do_unlink=True)
    _voxel_remesh(hand, VOXEL)
    for i, (x, y) in enumerate(_boss_centers()):
        _boolean(hand, _cyl(f"clear{i}", x, y, (plate_bot - 1.0, plate_top + 1.0), CLEAR_D, 16), "DIFFERENCE")
    _boolean(hand, _box("cable", (cx - CABLE_HOLE[0] / 2, cx + CABLE_HOLE[0] / 2),
                        (cy - CABLE_HOLE[1] / 2, cy + CABLE_HOLE[1] / 2),
                        (plate_bot - CABLE_RISE, plate_top + 1.0)), "DIFFERENCE")
    islands, open_edges = _islands(hand)
    parts.append({"id": "hand", "label": f"ロボットハンド（取付板つき・{'右' if P.HAND_SIDE == 'Right' else '左'}手）",
                  "printed": True, "ob": hand, "placed": grip})
    print(f"[hand] islands={islands} open_edges={open_edges}")
    return [
        f"くちばしを切り、配線の箱（{BOX_X[1] - BOX_X[0]:.0f}×{BOX_Y[1] - BOX_Y[0]:.0f}×{P.BOX_HEIGHT * 1000:.0f} mm）を本体に一体化",
        "可動あごを外した",
        f"Robot Hand（{P.HAND_SIDE}）を 1 単位 {P.HAND_SCALE * 1000:.0f} mm で取付板と一体化。島 {islands} 個・開いた辺 {open_edges} 本",
    ]
