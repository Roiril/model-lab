"""グリッパの先を、サーボ 6 で前後に振れるロボットハンドに付け替える。

形の出どころは table-duo-vr の Robot Hand（VR Hands Starter Pack、購入アセット）。
このリポジトリは公開なので、FBX は hand_src/（git 管理外）に置き、作った STL も
build/ と exports/（どちらも git 管理外）にしか書かない。FBX が無ければ元のグリッパのまま作る。

形の組み立ては gripper_link 座標（mm、可動あごの角度 0 のとき）で行う。
z が負の向きが先端、+x が掌を向ける側、サーボ 6 の軸は y 方向。

  固定あご: くちばしを z < CUT_Z で切り落とす（サーボ 6 の受けだけ残す）
  可動あご: 軸受けの根元だけ残し、その先に中空の箱を一体で付ける（8Servos Unit と指の線を入れる）
            → 箱の底を取付板でふさぎ、板にハンドの手首の円盤を載せる（板とハンドは一体で刷る）
            板の四隅は M2 のタッピングねじで箱のボスへ留める。中央の穴は指の線をハンドから箱へ通す
            → 甲側（−x）の壁の上の切り欠きから Grove と 5V を出し、軸をまたいで腕へ沿わせる
  箱ごと回すので、回る継ぎ目をまたぐ線は Grove 4 本 + 5V 2 本だけ（指の 15 本は箱の中で終わる）

  ハンドは可動あごの角度 STRAIGHT_DEG で真っすぐ（−z）を向く。軸から箱の上面までを AXIS_GAP 離すと、
  可動域 −10〜+100° の全部で本体とサーボ 6 に当たらない（sweep_check で確かめる）。
"""
from __future__ import annotations

import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
FBX = HERE / "hand_src" / "RobotHand.fbx"
MM = 0.001

CUT_Z = -40.0            # 固定あごはここより先を切る。サーボ 6 の下面（−35.8）より 4 mm 先
AXIS_GAP = 30.0          # サーボ 6 の軸から箱の上面まで（真っすぐのとき）
BOX_HALF_X = 32.6        # 箱の外形: x は軸を中心に ±32.6、y は元のグリッパの幅
BOX_Y = (-28.0, 24.0)
STUB_OVERLAP = 4.5       # 可動あごの根元を箱の上面へ食い込ませる量（傾けて付けるので、浅い側でも 2 mm 以上かかる）
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
SWEEP = (-10.0, 100.0, 2.0)         # 当たりを調べる可動あごの角度（度）: 始め, 終わり, 刻み


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


def _boss_centers(bx, by):
    # ボスは内壁へ 1 mm 食い込ませる（壁に接するだけだと、接線で面が重なって開いた辺が残る）
    inset = WALL + BOSS_D / 2 - 1.0
    return [(x, y) for x in (bx[0] + inset, bx[1] - inset) for y in (by[0] + inset, by[1] - inset)]


def _wiring_box(bx, by, top, bottom):
    """中空の箱（底は開いている）。ボスと甲側の切り欠きつき。"""
    box = _box("wiring-box", bx, by, (bottom, top))
    cavity = _box("cavity", (bx[0] + WALL, bx[1] - WALL), (by[0] + WALL, by[1] - WALL),
                  (bottom - 1.0, top - TOP_WALL))
    # ボスは空洞から削り残す。足し算で付けると、ボスの底が箱の底と同じ面に重なって開いた辺が出る
    for i, (x, y) in enumerate(_boss_centers(bx, by)):
        _boolean(cavity, _cyl(f"boss{i}", x, y, (bottom - 2.0, bottom + BOSS_H), BOSS_D), "DIFFERENCE")
    _boolean(box, cavity, "DIFFERENCE")
    for i, (x, y) in enumerate(_boss_centers(bx, by)):
        _boolean(box, _cyl(f"pilot{i}", x, y, (bottom - 1.0, bottom + PILOT_DEPTH), PILOT_D, 16), "DIFFERENCE")
    cy, top_in = sum(by) / 2, top - TOP_WALL
    # 切り欠きの上面は天井より 1 mm 上へ。天井と同じ平面にすると、傾けて付けたときに面が食い違って開いた辺が出る
    _boolean(box, _box("slot", (bx[0] - 1.0, bx[0] + WALL + 1.0), (cy - SLOT[0] / 2, cy + SLOT[0] / 2),
                       (top_in - SLOT[1], top_in + 1.0)), "DIFFERENCE")
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


def _bvh(ob, matrix):
    verts = [matrix @ v.co for v in ob.data.vertices]
    return BVHTree.FromPolygons(verts, [tuple(p.vertices) for p in ob.data.polygons])


def sweep_check(fixed, moving, joint_rot):
    """可動あごを SWEEP の角度で回し、動く部品と止まった部品の面が交わる角度を返す。
    fixed / moving: [(object, gripper_link 座標への行列)]。joint_rot(deg) は可動あご 0° からの回転行列。"""
    fixed_trees = [_bvh(ob, m) for ob, m in fixed]
    hits = []
    a, b, step = SWEEP
    n = int(round((b - a) / step))
    for i in range(n + 1):
        deg = a + i * step
        R = joint_rot(deg)
        for ob, m in moving:
            t = _bvh(ob, R @ m)
            if any(t.overlap(f) for f in fixed_trees):
                hits.append(deg)
                break
    return hits


def apply(parts, frames, P):
    """parts: [{id,label,printed,ob,placed}]。手直しの一覧（日本語 1 行ずつ）を返す。"""
    if not P.HAND:
        return []
    if not FBX.exists():
        print(f"[hand] {FBX} が無いので元のグリッパのまま作ります（購入アセットは git に無い）")
        return ["ハンドの FBX が無いので元のグリッパのまま"]
    by_id = {p["id"]: p for p in parts}
    grip = frames["gripper_link"]
    jaw_frame = frames["moving_jaw_so101_v1_link"]
    to_grip = grip.inverted()
    # 可動あご 0° のときの、可動あご座標 → gripper_link 座標
    T0 = to_grip @ jaw_frame @ Matrix.Rotation(-math.radians(P.GRIPPER), 4, "Z")
    to_jaw0 = T0.inverted()

    def joint_rot(deg):              # gripper_link 座標での、可動あご 0° からの回転
        return T0 @ Matrix.Rotation(math.radians(deg), 4, "Z") @ to_jaw0

    pivot = T0.translation / MM      # サーボ 6 の軸上の点（mm）
    px, pz = pivot.x, pivot.z

    # 1. 固定あご: くちばしを切る
    body = by_id["gripper-fixed-jaw"]
    _bake(body["ob"], to_grip @ body["placed"])
    body["placed"] = grip
    _boolean(body["ob"], _box("cut", (-80, 80), (-80, 80), (-200, CUT_Z)), "DIFFERENCE")
    body["label"] = "グリッパ本体（くちばしを切ったもの）"

    # 2. 可動あご: 根元を残して、真っすぐの姿勢で作った箱を付ける
    jaw = by_id["gripper-moving-jaw"]
    _bake(jaw["ob"], to_grip @ jaw["placed"] @ Matrix.Rotation(-math.radians(P.GRIPPER), 4, "Z"))
    top = pz - AXIS_GAP
    bottom = top - P.BOX_HEIGHT * 1000.0
    bx = (px - BOX_HALF_X, px + BOX_HALF_X)
    straight_to_0 = joint_rot(-P.STRAIGHT_DEG)        # 真っすぐ（角度 STRAIGHT_DEG）の形を 0° の形へ
    box = _wiring_box(bx, BOX_Y, top, bottom)
    _bake(box, straight_to_0)
    # 当たり判定は足した箱で行う（可動あごの根元はサーボ 6 のホーンと元から接していて、常に交わる）
    box_check = box.copy()
    box_check.data = box.data.copy()
    bpy.context.collection.objects.link(box_check)
    _boolean(jaw["ob"], _box("stub-cut", (-200, 200), (-80, 80), (-300, pz - AXIS_GAP - STUB_OVERLAP)), "DIFFERENCE")
    _boolean(jaw["ob"], box, "UNION")
    jaw["label"] = "手首の振り台（可動あご + 配線の箱）"

    # 3. ハンド + 取付板（一体）。真っすぐの姿勢で、手首の中心を箱の中心に、指を −z、掌を +x へ
    cx, cy = px, sum(BOX_Y) / 2
    plate_top, plate_bot = bottom, bottom - PLATE_T
    hand = _load_hand(P.HAND_SIDE, P.HAND_SCALE)
    # FBX: 指 +Z、掌 +Y、親指 ±X  →  gripper_link: 指 −z、掌 +x、FBX の X は +y
    R = Matrix(((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))
    _bake(hand, Matrix.Translation(Vector((cx * MM, cy * MM, plate_bot * MM))) @ R)
    plate = _box("plate", bx, BOX_Y, (plate_bot, plate_top))
    bm = bmesh.new()
    bm.from_mesh(hand.data)
    bm.from_mesh(plate.data)
    bm.to_mesh(hand.data)
    bm.free()
    bpy.data.objects.remove(plate, do_unlink=True)
    _voxel_remesh(hand, VOXEL)
    for i, (x, y) in enumerate(_boss_centers(bx, BOX_Y)):
        _boolean(hand, _cyl(f"clear{i}", x, y, (plate_bot - 1.0, plate_top + 1.0), CLEAR_D, 16), "DIFFERENCE")
    _boolean(hand, _box("cable", (cx - CABLE_HOLE[0] / 2, cx + CABLE_HOLE[0] / 2),
                        (cy - CABLE_HOLE[1] / 2, cy + CABLE_HOLE[1] / 2),
                        (plate_bot - CABLE_RISE, plate_top + 1.0)), "DIFFERENCE")
    _bake(hand, straight_to_0)
    islands, open_edges = _islands(hand)

    # 4. 可動域の全部で、動く側（振り台・ハンド）が止まった側（本体・サーボ 6）に当たらないか
    servo6 = by_id["servo-6"]
    fixed = [(body["ob"], Matrix.Identity(4)), (servo6["ob"], to_grip @ servo6["placed"])]
    moving = [(box_check, Matrix.Identity(4)), (hand, Matrix.Identity(4))]
    hits = sweep_check(fixed, moving, joint_rot)
    bpy.data.objects.remove(box_check, do_unlink=True)

    # 書き出しは可動あご座標（関節角 GRIPPER で回る）
    for ob in (jaw["ob"], hand):
        _bake(ob, to_jaw0)
    jaw["placed"] = jaw_frame
    parts.append({"id": "hand", "label": f"ロボットハンド（取付板つき・{'右' if P.HAND_SIDE == 'Right' else '左'}手）",
                  "printed": True, "ob": hand, "placed": jaw_frame})
    sweep = f"{SWEEP[0]:.0f}〜{SWEEP[1]:.0f}°" + ("で当たりなし" if not hits else f"で当たる角度 {hits}")
    print(f"[hand] islands={islands} open_edges={open_edges} sweep {sweep}")
    return [
        "固定あごのくちばしを切った",
        f"可動あごの先に配線の箱（{2 * BOX_HALF_X:.0f}×{BOX_Y[1] - BOX_Y[0]:.0f}×{P.BOX_HEIGHT * 1000:.0f} mm）を一体化。"
        f"サーボ 6 の軸から {AXIS_GAP:.0f} mm、角度 {P.STRAIGHT_DEG:.0f}° で真っすぐ",
        f"Robot Hand（{P.HAND_SIDE}）を 1 単位 {P.HAND_SCALE * 1000:.0f} mm で取付板と一体化。島 {islands} 個・開いた辺 {open_edges} 本",
        f"可動域 {sweep}",
    ]
