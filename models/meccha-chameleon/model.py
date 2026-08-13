"""meccha-chameleon — 『めっちゃカメレオン』の隠れ側プレイヤーアバター素体（リグ方式）。

本物のゲームキャラと同じ設計思想に切り替えた版:
  1) ニュートラル(ゆるいAポーズ)の素体メッシュを「メタボール→メッシュ化」で1体だけ作る
  2) 骨格に合わせたアーマチュア(ボーン)を入れ、自動ウェイトでスキニング
  3) ボーンを回して各ポーズに変形させ、変形後メッシュを別STLとして書き出す

これにより、どのポーズでも体積・解剖が一定（手足が近づいても癒着・膨張しない）、
関節も自然に曲がる。メタボールはあくまで「素体の滑らかな造形」にのみ使用する。

- 関節角は左半身を基準に与え、右半身は鏡像 S=diag(-1,1,1) で自動生成
- 非対称ポーズは pose に関節名キー(shoulder_L 等)を直接書いて左右独立に指定
- 寝そべりは書き出し時に全身をX軸まわりで倒す(tilt)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import bpy
from mathutils import Vector, Matrix, Euler
from blender_utils import clear_scene, EXPORTS_DIR
from params import *

S = SCALE
FACTOR = 1.0 / math.sqrt(1.0 - math.sqrt(MB_THRESH / MB_STIFF))  # 物理半径→要素半径
BS = BUILD_SCALE  # メタボール多角形化の拡大率（解像度クランプ回避）

# ============================================================
# 骨格定義（中立姿勢・ワールド軸そろえ。Z上 / +Y前 / +X=キャラの左）
# ============================================================
SKELETON = [
    ("pelvis",     None,         (0, 0, 0)),
    ("chest",      "pelvis",     (0, 0, L_SPINE)),
    ("neck",       "chest",      (0, 0, L_NECK)),
    ("head",       "neck",       (0, 0, L_HEADUP)),
    ("shoulder_L", "chest",      (SH_W, 0, SH_UP)),
    ("shoulder_R", "chest",      (-SH_W, 0, SH_UP)),
    ("elbow_L",    "shoulder_L", (0, 0, -L_UARM)),
    ("elbow_R",    "shoulder_R", (0, 0, -L_UARM)),
    ("wrist_L",    "elbow_L",    (0, 0, -L_LARM)),
    ("wrist_R",    "elbow_R",    (0, 0, -L_LARM)),
    ("hip_L",      "pelvis",     (HIP_W, 0, -HIP_DN)),
    ("hip_R",      "pelvis",     (-HIP_W, 0, -HIP_DN)),
    ("knee_L",     "hip_L",      (0, 0, -L_ULEG)),
    ("knee_R",     "hip_R",      (0, 0, -L_ULEG)),
    ("ankle_L",    "knee_L",     (0, 0, -L_LLEG)),
    ("ankle_R",    "knee_R",     (0, 0, -L_LLEG)),
]
PARENT = {j: p for j, p, _ in SKELETON}
OFFSET = {j: Vector(o) * S for j, _, o in SKELETON}
ORDER = [j for j, _, _ in SKELETON]
MIRROR = Matrix.Diagonal((-1, 1, 1)).to_3x3()

STRAIGHT_DEG = 16  # これ未満の関節角は1本のカプセルで通す


def emat(deg):
    rx, ry, rz = (math.radians(d) for d in deg)
    return Euler((rx, ry, rz), "XYZ").to_matrix()


def joint_rotations(pose):
    g = {k: emat(pose.get(k, (0, 0, 0)))
         for k in ("chest", "neck", "head", "shoulder", "elbow", "hip", "knee", "ankle")}
    rot = {j: Matrix.Identity(3) for j in ORDER}
    rot["chest"], rot["neck"], rot["head"] = g["chest"], g["neck"], g["head"]
    for key, jl, jr in (("shoulder", "shoulder_L", "shoulder_R"),
                        ("elbow", "elbow_L", "elbow_R"),
                        ("hip", "hip_L", "hip_R"),
                        ("knee", "knee_L", "knee_R"),
                        ("ankle", "ankle_L", "ankle_R")):
        rot[jl] = g[key]
        rot[jr] = MIRROR @ g[key] @ MIRROR
    for j in ORDER:                       # 非対称オーバーライド
        if j in pose:
            rot[j] = emat(pose[j])
    return rot


def fk(pose):
    """各関節のワールド座標と累積回転を返す。"""
    rot = joint_rotations(pose)
    wpos, wrot = {}, {}
    for j in ORDER:
        p = PARENT[j]
        Rp, Pp = (Matrix.Identity(3), Vector((0, 0, 0))) if p is None else (wrot[p], wpos[p])
        wpos[j] = Pp + Rp @ OFFSET[j]
        wrot[j] = Rp @ rot[j]
    return wpos, wrot


# ============================================================
# メタボール素体（ニュートラル姿勢を1体だけ造形）
# ============================================================
BALLS = [("head", R_HEAD)]  # 玉は頭のみ（関節はカプセル融合に任せる）


def add_ball(mball, co, r):
    e = mball.elements.new(); e.type = "BALL"
    e.co = co * BS; e.radius = r * FACTOR * BS; e.stiffness = MB_STIFF


def add_capsule(mball, a, b, r):
    d = b - a
    if d.length < 1e-6:
        return
    e = mball.elements.new(); e.type = "CAPSULE"
    e.co = (a + b) * 0.5 * BS; e.radius = r * FACTOR * BS
    e.size_x = d.length * 0.5 * BS; e.stiffness = MB_STIFF
    e.rotation = tuple(Vector((1, 0, 0)).rotation_difference(d.normalized()))


def add_chain(mball, a, b, c, r):
    d1, d2 = (b - a), (c - b)
    if d1.length < 1e-6 or d2.length < 1e-6:
        add_capsule(mball, a, c, r); return
    if math.degrees(d1.angle(d2)) < STRAIGHT_DEG:
        add_capsule(mball, a, c, r)
    else:
        add_capsule(mball, a, b, r); add_capsule(mball, b, c, r)
        add_ball(mball, b, r * 0.8)


def add_ellipsoid(mball, co, sx, sy, sz):
    e = mball.elements.new(); e.type = "ELLIPSOID"
    e.co = co * BS; e.stiffness = MB_STIFF
    e.size_x = sx * FACTOR * BS
    e.size_y = sy * FACTOR * BS
    e.size_z = sz * FACTOR * BS
    e.radius = min(sx, sy, sz) * FACTOR * BS


def add_head(mball, head):
    # 大きい丸い頭（ボールが最も安定して大きく出る）
    add_ball(mball, head, R_HEAD * S)


def add_hand(mball, wrist):
    # 平たいミトン: 前後(Y)に薄く、腕方向(Z)にやや長い丸パドル
    add_ellipsoid(mball, wrist, R_HAND * S * 1.55, R_HAND * S * 0.85, R_HAND * S * 1.85)


def add_foot(mball, ankle):
    e = mball.elements.new(); e.type = "ELLIPSOID"
    e.co = (ankle + Vector((0, FOOT_FWD * S * 0.5, -R_FOOT * S * 0.3))) * BS
    e.stiffness = MB_STIFF
    e.size_x = R_FOOT * S * FACTOR * BS
    e.size_y = (R_FOOT * S + FOOT_FWD * S) * FACTOR * BS
    e.size_z = R_FOOT * S * FOOT_FLAT * FACTOR * BS
    e.radius = R_FOOT * S * FACTOR * BS


def build_body_mesh(pose, name="body"):
    wp, _ = fk(pose)
    mball = bpy.data.metaballs.new(name)
    mball.resolution = MB_RES; mball.render_resolution = MB_RES; mball.threshold = MB_THRESH
    add_capsule(mball, wp["pelvis"], wp["chest"], R_TORSO * S)
    add_capsule(mball, wp["chest"], wp["neck"], R_NECK * S)
    add_capsule(mball, wp["neck"], wp["head"], R_NECK * S)
    add_capsule(mball, wp["chest"], wp["shoulder_L"], R_ARM * S)
    add_capsule(mball, wp["chest"], wp["shoulder_R"], R_ARM * S)
    add_chain(mball, wp["shoulder_L"], wp["elbow_L"], wp["wrist_L"], R_ARM * S)
    add_chain(mball, wp["shoulder_R"], wp["elbow_R"], wp["wrist_R"], R_ARM * S)
    add_capsule(mball, wp["pelvis"], wp["hip_L"], R_LEG * S)
    add_capsule(mball, wp["pelvis"], wp["hip_R"], R_LEG * S)
    add_chain(mball, wp["hip_L"], wp["knee_L"], wp["ankle_L"], R_LEG * S)
    add_chain(mball, wp["hip_R"], wp["knee_R"], wp["ankle_R"], R_LEG * S)
    add_head(mball, wp["head"])
    add_hand(mball, wp["wrist_L"]); add_hand(mball, wp["wrist_R"])
    add_foot(mball, wp["ankle_L"]); add_foot(mball, wp["ankle_R"])

    obj = bpy.data.objects.new(name, mball)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj; obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.active_object
    obj.scale = (1.0 / BS, 1.0 / BS, 1.0 / BS)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # ボクセル・リメッシュで「薄い接合シートのゴミ」を除去し、
    # 多様体・均一トポロジー化（スキニングと印刷の両方に有利）
    obj.select_set(True); bpy.context.view_layer.objects.active = obj
    rm = obj.modifiers.new("remesh", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = REMESH_VOXEL
    rm.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier="remesh")
    return obj


# ============================================================
# アーマチュア（ボーン）— レスト姿勢に合わせて構築
# ============================================================
# (bone, parent_bone, head_joint, tail_joint)
RIG = [
    ("spine",  None,    "pelvis", "chest"),
    ("neck",   "spine", "chest",  "neck"),
    ("head",   "neck",  "neck",   "head"),
    ("clav_L", "spine", "chest",  "shoulder_L"),
    ("uarm_L", "clav_L","shoulder_L", "elbow_L"),
    ("farm_L", "uarm_L","elbow_L",    "wrist_L"),
    ("clav_R", "spine", "chest",  "shoulder_R"),
    ("uarm_R", "clav_R","shoulder_R", "elbow_R"),
    ("farm_R", "uarm_R","elbow_R",    "wrist_R"),
    ("pelv_L", "spine", "pelvis", "hip_L"),
    ("uleg_L", "pelv_L","hip_L",  "knee_L"),
    ("lleg_L", "uleg_L","knee_L", "ankle_L"),
    ("pelv_R", "spine", "pelvis", "hip_R"),
    ("uleg_R", "pelv_R","hip_R",  "knee_R"),
    ("lleg_R", "uleg_R","knee_R", "ankle_R"),
]
RIG_HEAD = {name: hj for name, _, hj, _ in RIG}


def build_armature(P_rest):
    arm = bpy.data.armatures.new("rig")
    arm_obj = bpy.data.objects.new("rig", arm)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    ebs = {}
    for name, parent, hj, tj in RIG:
        b = arm.edit_bones.new(name)
        b.head = P_rest[hj]; b.tail = P_rest[tj]
        if parent:
            b.parent = ebs[parent]; b.use_connect = False
        ebs[name] = b
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm_obj


def skin(body, arm_obj):
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True); arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    try:
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    except RuntimeError:
        # フォールバック: エンベロープ
        for b in arm_obj.data.bones:
            b.envelope_distance = 0.02
        bpy.ops.object.select_all(action="DESELECT")
        body.select_set(True); arm_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type="ARMATURE_ENVELOPE")


def apply_pose(arm_obj, pose, P_rest, W_rest):
    wpos, wrot = fk(pose)
    bpy.context.view_layer.objects.active = arm_obj
    for name, parent, hj, tj in RIG:          # 親→子の順
        pb = arm_obj.pose.bones[name]
        A = hj
        Md = (Matrix.Translation(wpos[A]) @ wrot[A].to_4x4()
              @ W_rest[A].to_4x4().inverted() @ Matrix.Translation(-P_rest[A]))
        pb.matrix = Md @ pb.bone.matrix_local
        bpy.context.view_layer.update()


# ============================================================
# 書き出しユーティリティ
# ============================================================
def lowest_z(o):
    return min((o.matrix_world @ v.co).z for v in o.data.vertices)


def ground(o):
    # 接地。location を実頂点へ焼き込む（焼かないと後続の make_base が
    # 旧 matrix_world を読んで台座を足元から大きくずれた位置に作ってしまう）
    o.select_set(True); bpy.context.view_layer.objects.active = o
    o.location.z += -lowest_z(o)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)


def apply_tilt(o, deg):
    o.select_set(True); bpy.context.view_layer.objects.active = o
    o.rotation_euler = (math.radians(deg), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)


def make_base(o):
    mz = lowest_z(o)
    band = mz + 0.006 * S
    pts = [(o.matrix_world @ v.co) for v in o.data.vertices
           if (o.matrix_world @ v.co).z < band]
    cx = sum(p.x for p in pts) / len(pts); cy = sum(p.y for p in pts) / len(pts)
    r = max(((p.x - cx) ** 2 + (p.y - cy) ** 2) ** 0.5 for p in pts)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r + BASE_MARGIN * S, depth=BASE_T * S, vertices=64,
        location=(cx, cy, mz + BASE_OVERLAP * S - BASE_T * S * 0.5))
    base = bpy.context.active_object; base.name = "base"
    return base


def deformed_copy(body, name):
    deps = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(body.evaluated_get(deps))
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    return o


def export_only(objs, filename):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    path = os.path.join(EXPORTS_DIR, filename + ".stl")
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    print(f"Exported: {path}")


# ============================================================
# ポーズ定義（実物プリント写真の構成に合わせる）
# 角度はまっすぐ立ち(全0)基準。レスト姿勢との差分はリグが吸収する。
# ============================================================
POSE_REST = dict(shoulder=(0, -25, 0), hip=(0, -10, 0))  # スキニング用ゆるいAポーズ

POSES = {
    "stand":       dict(shoulder=(0, -11, 0)),
    "wave":        dict(shoulder_L=(5, -145, 0), shoulder_R=(0, 6, 0)),
    "handsonhead": dict(shoulder=(0, -115, 0), elbow=(0, -125, 0)),
    "star":        dict(shoulder=(0, -138, 0), hip=(0, -22, 0)),
    "bend":        dict(chest=(-55, 0, 0), shoulder=(0, -8, 0)),
    "lie":         dict(tilt=-90, shoulder=(0, -165, 0)),
    "curl":        dict(chest=(-40, 0, 0), head=(-25, 0, 0),
                        shoulder=(100, -8, 0), elbow=(70, 0, 0),
                        hip=(118, 0, 0), knee=(-120, 0, 0)),
}
UPRIGHT = {"stand", "wave", "handsonhead", "star", "bend"}


# ============================================================
# メイン
# ============================================================
clear_scene()

# 1) レスト素体メッシュ＋アーマチュア＋スキニング
body = build_body_mesh(POSE_REST, "body")
P_rest, W_rest = fk(POSE_REST)
arm_obj = build_armature(P_rest)
skin(body, arm_obj)

# 2) 各ポーズへ変形して個別STL
for name, pose in POSES.items():
    apply_pose(arm_obj, pose, P_rest, W_rest)
    o = deformed_copy(body, f"mc_{name}")
    tilt = pose.get("tilt", 0)
    if tilt:
        apply_tilt(o, tilt)
    ground(o)
    objs = [o]
    if BASE_ON == 1 and name in UPRIGHT:
        objs.append(make_base(o))
    bb = o.bound_box
    dims = o.dimensions
    print(f"[meccha-chameleon] {name:11s} W={dims.x*1000:5.1f} D={dims.y*1000:5.1f} "
          f"H={dims.z*1000:5.1f} mm  tris={len(o.data.polygons)}")
    export_only(objs, f"meccha-chameleon-{name}")
    for x in objs:
        bpy.data.objects.remove(x, do_unlink=True)

# 3) 全ポーズ一覧（台座なし・横並び）
gap = 0.075 * S
order = ["stand", "wave", "handsonhead", "star", "bend", "lie", "curl"]
line_objs = []
for i, name in enumerate(order):
    apply_pose(arm_obj, POSES[name], P_rest, W_rest)
    o = deformed_copy(body, f"line_{name}")
    tilt = POSES[name].get("tilt", 0)
    if tilt:
        apply_tilt(o, tilt)
    ground(o)
    o.location.x += (i - (len(order) - 1) / 2) * gap
    line_objs.append(o)
export_only(line_objs, "meccha-chameleon")

print("[meccha-chameleon] done")
