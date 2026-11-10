"""uHand に骨を入れ、anim/ のクリップを焼いて FBX と GLB に書き出す。

"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python models/hiwonder-uhand/anim_build.py
  exports/hiwonder-uhand-rigged.fbx    Unity 用（骨 + クリップ。メートル、Y が上）
  exports/hiwonder-uhand-rigged.glb    ブラウザで見る用（viewer/uhand-anim.html）
  exports/hiwonder-uhand-rigged.json   目録（骨・量と骨の対応・クリップの一覧）。Unity の設定スクリプトが読む
ほかのスクリプトからは rig() と apply_pose() を使う（anim_preview.py）。

作り:
  部品は動く塊ごとに 1 つのメッシュにまとめ、骨に直接ぶら下げる（スキンは使わない。機械なので変形しない）。
  骨の親子と回転の中心は kin.bones()、姿勢は kin.pose()。ここでは形と骨を結びつけて焼くだけ。
  どの部品がどの骨に付くかは下の RULES。model.py に部品を足したら、名前がどれかに当たるようにする（当たらないと止まる）。
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)
os.environ["UHAND_NO_EXPORT"] = "1"

import bpy
from mathutils import Matrix

import anim_lib
import kin
import model as HM

EXPORTS = os.path.normpath(os.path.join(HERE, "../../exports"))
NAME = "hiwonder-uhand-rigged"
ARM = "uhand"

# 部品の名前（正規表現）→ 骨。上から順に当てる。{f} は指の名前
RULES = [
    (r"wrist_(flange|hub)$", "base"),
    (r"(palm_|hook_|sp_|servo\d|servo_plate$|thumb_servo|back_plate$|bp_|wall_|lip_|post\d|wrist_|thumb_crank_post$)", "hand"),
    (r"{f}_(rod_end|rod_nut|base)", "hand"),
    (r"{f}_rod$", "{f}_rod"),
    (r"{f}_slink", "{f}_slink"),
    (r"{f}_link", "{f}_link"),
    (r"{f}_(prox|pip_|mcp_)", "{f}_prox"),
    (r"{f}_(mid|washer|jscrew)", "{f}_mid"),
    (r"{f}_(tip|dip_pin)", "{f}_tip"),
    (r"(horn_|rod_end0)", "thumb_horn"),
    (r"push_rod$", "thumb_pushrod"),
    (r"thumb_distal$", "thumb_tip"),
    (r"thumb_crank_tab$", "thumb_prox"),
    (r"thumb_crank", "thumb_crank"),
    (r"(thumb_(upper|lower|root|pivot|strut|w\d|s\d|n\d)|rod_end1)", "thumb_prox"),
]
# 量 → その量で動く骨（Unity で層ごとのマスクに使う）
DOF_BONES = {nm: [f"{nm}_{p}" for p in ("prox", "mid", "tip", "link", "slink", "rod")] for nm in kin.FINGERS}
DOF_BONES["thumb"] = ["thumb_prox", "thumb_tip", "thumb_horn", "thumb_pushrod", "thumb_crank"]
DOF_BONES["wrist"] = ["hand"]


def bone_of(name):
    for pat, bone in RULES:
        for f in (kin.FINGERS if "{f}" in pat else ("",)):
            if re.match(pat.replace("{f}", f), name):
                return bone.replace("{f}", f)
    raise ValueError(f"部品 {name!r} がどの骨に付くか決まっていない（anim_build.py の RULES に足す）")


def to_m(m):
    """kin の行列（mm）を Blender の行列（m）にする。"""
    M = Matrix(m)
    for i in range(3):
        M[i][3] *= 0.001
    return M


def rig():
    """シーンを空にしてモデルを作り、骨に結びつける。(骨のオブジェクト, 休みの行列の辞書) を返す。"""
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for act in list(bpy.data.actions):
        bpy.data.actions.remove(act)
    coll = HM.build()
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    groups = {}
    for ob in list(coll.objects):
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        me.transform(ob.matrix_world)
        mo = bpy.data.objects.new("_" + ob.name, me)
        groups.setdefault(bone_of(ob.name), []).append(mo)
    for ob in list(coll.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    spec = kin.bones()
    missing = [b for b in spec if b not in groups]
    if missing:
        raise ValueError(f"部品が 1 つも付かない骨がある: {missing}")

    sc = bpy.context.scene.collection
    meshes = {}
    for bone, obs in groups.items():
        for o in obs:
            sc.objects.link(o)
        bpy.ops.object.select_all(action="DESELECT")
        for o in obs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = obs[0]
        if len(obs) > 1:
            bpy.ops.object.join()
        ob = bpy.context.view_layer.objects.active
        ob.name = ob.data.name = f"uh_{bone}"
        for p in ob.data.polygons:
            p.use_smooth = True
        ob.data.set_sharp_from_angle(angle=math.radians(40))
        meshes[bone] = ob

    ad = bpy.data.armatures.new(ARM)
    arm = bpy.data.objects.new(ARM, ad)
    sc.objects.link(arm)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (parent, head, tail) in spec.items():
        eb = ad.edit_bones.new(name)
        eb.head = [v * 0.001 for v in head]
        eb.tail = [v * 0.001 for v in tail]
    for name, (parent, head, tail) in spec.items():
        if parent:
            ad.edit_bones[name].parent = ad.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    for bone, ob in meshes.items():
        ob.parent = arm
        ob.parent_type = "BONE"
        ob.parent_bone = bone
    bpy.context.view_layer.update()
    for ob in meshes.values():
        ob.matrix_world = Matrix.Identity(4)
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    rest = {b.name: b.matrix_local.copy() for b in ad.bones}
    return arm, rest


def apply_pose(arm, rest, dofs):
    """量の辞書の姿勢を骨に入れる。骨ごとの行列は 親の動きを打ち消してから自分の動きを掛ける。"""
    W = {k: to_m(m) for k, m in kin.pose(dofs).items()}
    for pb in arm.pose.bones:
        R = rest[pb.name]
        Wp = W[pb.parent.name].inverted() if pb.parent else Matrix.Identity(4)
        pb.matrix_basis = R.inverted() @ Wp @ W[pb.name] @ R


def bake(arm, rest, clip):
    act = bpy.data.actions.new(clip["name"])
    act.use_fake_user = True
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act
    # dof_ のクリップは、その量で動く骨だけにキーを打つ（Unity で層を重ねたとき他の量を上書きしない）
    only = DOF_BONES.get(clip["name"][4:]) if clip["name"].startswith("dof_") else None
    prev = {}
    for n, dofs in enumerate(anim_lib.frames(clip)):
        apply_pose(arm, rest, dofs)
        for pb in arm.pose.bones:
            if only is not None and pb.name not in only:
                continue
            q = pb.rotation_quaternion.copy()
            if pb.name in prev and prev[pb.name].dot(q) < 0:     # 符号をそろえて、補間で逆回りしないようにする
                q.negate()
                pb.rotation_quaternion = q
            prev[pb.name] = q
            for path in ("location", "rotation_quaternion", "scale"):
                pb.keyframe_insert(path, frame=n)
    return act


def dof_list():
    """量の一覧（Unity の JsonUtility は辞書を読めないので配列でも持つ）。"""
    return [dict(name=k, min=lo, max=hi, rest=r, bones=DOF_BONES[k], clip=f"dof_{k}") for k, (lo, hi, r) in kin.DOFS.items()]


def probes(clips):
    """読み込んだ先で動きが合っているかを確かめる目印。骨 2 本の頭どうしの距離 [m]（座標系の向きに依らない）。
    Unity の設定スクリプトが、クリップを引いた結果と量を入れた結果をこの値と比べる。"""
    spec = kin.bones()

    def dist(dofs, a, b):
        W = kin.pose(dofs)
        pa, pb = kin.apply(W[a], spec[a][1]), kin.apply(W[b], spec[b][1])
        return kin.vlen(kin.vsub(pa, pb)) * 0.001

    order = list(kin.DOFS)
    out = []
    pairs = [("index_tip", "hand"), ("middle_tip", "hand"), ("ring_tip", "hand"), ("little_tip", "hand"),
             ("thumb_tip", "hand"), ("index_tip", "thumb_tip"), ("index_link", "index_mid"), ("thumb_pushrod", "thumb_prox")]
    by = {c["name"]: c for c in clips}
    for name, t in (("open_close", 0.0), ("open_close", 1.1), ("count_up", 2.0), ("thumbs_up", 1.8)):
        if name in by:
            d = anim_lib.sample(by[name], t)
            out += [dict(kind="clip", clip=name, time=t, values=[d[k] for k in order], a=a, b=b, dist=dist(d, a, b)) for a, b in pairs]
    for d in (dict(index=1.0), dict(little=0.5, thumb=1.0), dict(middle=1.0, wrist=0.6)):
        full = kin.clamp_dofs(d)
        out += [dict(kind="dofs", clip="", time=0.0, values=[full[k] for k in order], a=a, b=b, dist=dist(full, a, b)) for a, b in pairs]
    return out


def reset(arm):
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)


def main():
    clips, errors = anim_lib.load_all()
    if errors:
        raise SystemExit("クリップの定義に誤りがある。anim_check.py を通すこと:\n" + "\n".join(errors))
    arm, rest = rig()
    sc = bpy.context.scene
    sc.render.fps = anim_lib.FPS
    for clip in clips:
        bake(arm, rest, clip)
    arm.animation_data.action = None
    reset(arm)
    sc.frame_start, sc.frame_end = 0, max(anim_lib.frame_count(c) for c in clips)

    bpy.ops.object.select_all(action="DESELECT")
    for ob in sc.collection.objects:
        ob.select_set(True)
    os.makedirs(EXPORTS, exist_ok=True)
    fbx = os.path.join(EXPORTS, NAME + ".fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
        apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y", mesh_smooth_type="FACE",
        bake_anim=True, bake_anim_use_all_bones=False, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=True,
        bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0)
    glb = os.path.join(EXPORTS, NAME + ".glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_animations=True,
                              export_animation_mode="ACTIONS", export_force_sampling=True, export_yup=True)
    manifest = dict(
        fps=anim_lib.FPS, armature=ARM, dof_list=dof_list(), probes=probes(clips),
        dofs={k: dict(min=lo, max=hi, rest=r, bones=DOF_BONES[k], clip=f"dof_{k}") for k, (lo, hi, r) in kin.DOFS.items()},
        bones={k: dict(parent=p) for k, (p, _, _) in kin.bones().items()},
        clips=[dict(name=c["name"], frames=anim_lib.frame_count(c) + 1, seconds=c["keys"][-1]["t"], loop=c["loop"],
                    description=c["description"]) for c in clips])
    tmp = os.path.join(EXPORTS, NAME + ".json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(EXPORTS, NAME + ".json"))
    tris = sum(len(p.vertices) - 2 for ob in sc.collection.objects if ob.type == "MESH" for p in ob.data.polygons)
    print(f"[anim_build] 骨 {len(arm.pose.bones)} 本 / メッシュ {len(arm.children)} 個 / 三角形 {tris} / クリップ {len(clips)} 本")
    print("[anim_build]", fbx)


if __name__ == "__main__":
    main()
