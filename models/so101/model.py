"""SO-101（5 自由度のアーム）を URDF どおりに組み立てて、部品ごとに書き出す。Headless Blender.

入力:  source/so101_new_calib.urdf + source/assets/*.stl（TheRobotStudio、Apache-2.0。読むだけ）
       params.py（関節角）/ edits.py（部品への手直し）
出力:  build/<id>.stl        組み立てた姿勢の部品（mm）
       build/print/<id>.stl  印刷する部品だけ、部品自身の座標（mm）
       build/manifest.json / build/ui.json   部品台帳の元（tools/studio_parts.py so101 で Studio に載る）
       exports/so101.stl     全部をまとめた 1 個

関節角の向きと 0 点は mycobot-lab のシミュレータと同じ（同じ URDF から作っている）。
"""
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(HERE))

import bpy
from mathutils import Euler, Matrix, Vector

import params as P
import edits
import hand_mount
from blender_utils import clear_scene, export_stl

SOURCE = HERE / "source"
URDF = SOURCE / "so101_new_calib.urdf"
BUILD = HERE / "build"
PRINT_DIR = BUILD / "print"
MM = 1000.0

JOINT_DEG = {
    "shoulder_pan": P.SHOULDER_PAN, "shoulder_lift": P.SHOULDER_LIFT, "elbow_flex": P.ELBOW_FLEX,
    "wrist_flex": P.WRIST_FLEX, "wrist_roll": P.WRIST_ROLL, "gripper": P.GRIPPER,
}

PRINTED = "#d6d0c2"     # 印刷部品（シミュレータの腕と同じ骨色）
SERVO = "#2a2a2e"
# (リンク, メッシュ, そのリンク内で何個目か) -> (部品 id, 日本語名, 印刷するか)
PARTS = {
    ("base_link", "base_so101_v2", 0): ("base-body", "土台", True),
    ("base_link", "base_motor_holder_so101_v1", 0): ("base-motor-holder", "土台のモータ受け", True),
    ("base_link", "waveshare_mounting_plate_so101_v2", 0): ("base-board-plate", "基板の取付板", True),
    ("base_link", "sts3215_03a_v1", 0): ("servo-1", "サーボ #1 肩の旋回", False),
    ("shoulder_link", "motor_holder_so101_base_v1", 0): ("shoulder-motor-holder", "肩のモータ受け", True),
    ("shoulder_link", "rotation_pitch_so101_v1", 0): ("shoulder-rotation", "肩の回転台", True),
    ("shoulder_link", "sts3215_03a_v1", 0): ("servo-2", "サーボ #2 肩の上下", False),
    ("upper_arm_link", "upper_arm_so101_v1", 0): ("upper-arm", "上腕", True),
    ("upper_arm_link", "sts3215_03a_v1", 0): ("servo-3", "サーボ #3 肘", False),
    ("lower_arm_link", "under_arm_so101_v1", 0): ("lower-arm", "前腕", True),
    ("lower_arm_link", "motor_holder_so101_wrist_v1", 0): ("lower-wrist-holder", "手首のモータ受け", True),
    ("lower_arm_link", "sts3215_03a_v1", 0): ("servo-4", "サーボ #4 手首の曲げ", False),
    ("wrist_link", "wrist_roll_pitch_so101_v2", 0): ("wrist-body", "手首", True),
    ("wrist_link", "sts3215_03a_no_horn_v1", 0): ("servo-5", "サーボ #5 手首の回転", False),
    ("gripper_link", "wrist_roll_follower_so101_v1", 0): ("gripper-fixed-jaw", "グリッパの固定あご", True),
    ("gripper_link", "sts3215_03a_v1", 0): ("servo-6", "サーボ #6 グリッパ", False),
    ("moving_jaw_so101_v1_link", "moving_jaw_so101_v1", 0): ("gripper-moving-jaw", "グリッパの可動あご", True),
}
GROUPS = [
    {"label": "土台", "prefix": "base", "color": "#b8b2a4"},
    {"label": "肩", "prefix": "shoulder", "color": "#c7c1b3"},
    {"label": "上腕", "prefix": "upper", "color": "#d6d0c2"},
    {"label": "前腕", "prefix": "lower", "color": "#ccc6b8"},
    {"label": "手首", "prefix": "wrist", "color": "#ddd7c9"},
    {"label": "グリッパ", "prefix": "gripper", "color": "#e4dfd2"},
    {"label": "ロボットハンド", "prefix": "hand", "color": "#9aa0a6"},
    {"label": "サーボ", "prefix": "servo", "color": SERVO},
]


def origin(el):
    """URDF の <origin xyz rpy> -> 4x4。rpy は固定軸 X→Y→Z（= Blender の Euler 'XYZ'）。"""
    if el is None:
        return Matrix.Identity(4)
    xyz = [float(v) for v in (el.get("xyz") or "0 0 0").split()]
    rpy = [float(v) for v in (el.get("rpy") or "0 0 0").split()]
    return Matrix.Translation(Vector(xyz)) @ Euler(rpy, "XYZ").to_matrix().to_4x4()


def link_frames(root):
    """各リンクのワールド座標。関節は全部 z 軸まわりの回転（この URDF の約束）。"""
    frames = {"base_link": Matrix.Identity(4)}
    joints = [j for j in root.findall("joint")]
    pending = list(joints)
    while pending:
        progressed = False
        for j in list(pending):
            parent, child = j.find("parent").get("link"), j.find("child").get("link")
            if parent not in frames:
                continue
            q = 0.0
            if j.get("type") == "revolute":
                axis = [float(v) for v in j.find("axis").get("xyz").split()]
                if axis != [0.0, 0.0, 1.0]:
                    raise ValueError(f"{j.get('name')} の軸が z ではありません: {axis}")
                q = math.radians(JOINT_DEG[j.get("name")])
            frames[child] = frames[parent] @ origin(j.find("origin")) @ Matrix.Rotation(q, 4, "Z")
            pending.remove(j)
            progressed = True
        if not progressed:
            raise ValueError("URDF の関節がつながっていません")
    return frames


def import_stl(path):
    bpy.ops.wm.stl_import(filepath=str(path))
    ob = bpy.context.selected_objects[0]
    ob.matrix_world = Matrix.Identity(4)
    return ob


def export_one(ob, path, matrix):
    path.parent.mkdir(parents=True, exist_ok=True)
    keep = ob.matrix_world.copy()
    ob.matrix_world = matrix
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True, global_scale=MM)
    ob.matrix_world = keep


def main():
    clear_scene()
    root = ET.parse(URDF).getroot()
    frames = link_frames(root)

    objects, placed, seen = {}, {}, {}
    for link in root.findall("link"):
        lname = link.get("name")
        for vis in link.findall("visual"):
            mesh = vis.find("geometry/mesh")
            if mesh is None:
                continue
            stem = Path(mesh.get("filename")).stem
            n = seen.get((lname, stem), 0)
            seen[(lname, stem)] = n + 1
            key = (lname, stem, n)
            if key not in PARTS:
                raise KeyError(f"部品表に無い形があります: {key}")
            pid, label, printed = PARTS[key]
            ob = import_stl(SOURCE / "assets" / f"{stem}.stl")
            ob.name = pid
            objects[pid] = ob
            placed[pid] = frames[lname] @ origin(vis.find("origin"))
    missing = set(p[0] for p in PARTS.values()) - set(objects)
    if missing:
        raise KeyError(f"URDF に見つからない部品: {sorted(missing)}")

    changes = edits.apply(objects) or []
    registry = [{"id": pid, "label": label, "printed": printed, "ob": objects[pid], "placed": placed[pid]}
                for (pid, label, printed) in PARTS.values()]
    changes += hand_mount.apply(registry, frames, P)

    for stale in list(BUILD.glob("*.stl")) + list(PRINT_DIR.glob("*.stl")):
        stale.unlink()                     # 外した部品の STL を残さない
    parts = []
    for p in registry:
        pid, ob = p["id"], p["ob"]
        export_one(ob, BUILD / f"{pid}.stl", p["placed"])
        entry = {"id": pid, "label": p["label"], "assembly": f"build/{pid}.stl",
                 "color": PRINTED if p["printed"] else SERVO}
        if p["printed"]:
            export_one(ob, PRINT_DIR / f"{pid}.stl", Matrix.Identity(4))
            entry["print"] = f"build/print/{pid}.stl"
        else:
            entry["stock"] = True
        parts.append(entry)

    for p in registry:
        p["ob"].matrix_world = p["placed"]
    bpy.ops.object.select_all(action="SELECT")
    export_stl("so101")

    BUILD.mkdir(exist_ok=True)
    (BUILD / "manifest.json").write_text(json.dumps({
        "meta": {"description": "SO-101（5 自由度アーム）。URDF どおりに組み立てた姿勢",
                 "joints_deg": JOINT_DEG, "edits": changes,
                 "source": "source/so101_new_calib.urdf (TheRobotStudio/SO-ARM100, Apache-2.0)"},
        "parts": parts,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (BUILD / "ui.json").write_text(json.dumps({"legendGroups": GROUPS}, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
    print(f"SO-101: {len(parts)} parts, joints {JOINT_DEG}, edits {changes}")


main()
