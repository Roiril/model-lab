"""手のアニメーション。関節の値を時刻で決めて鍵を打ち、GLB と MP4 を書く。

blender --background --python models/robot-hand-v2/animate.py -- --glb <path> --mp4 <path> [--res 960] [--samples 48]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

import bpy

import model as HM
import params as P
import studio as ST

# 関節の値 [deg] を返す。名前は "index_j3" "thumb_cmc" "wrist" など。
ALL_FINGERS = P.FINGER_ORDER


def zero_pose():
    pose = {"wrist": 0.0, "wrist_dev": 0.0, "thumb_cmc": 0.0}
    for n in ALL_FINGERS + ("thumb",):
        for j in ("j3", "j2", "j1"):
            pose[f"{n}_{j}"] = 0.0
    return pose


def with_finger(pose, name):
    q = dict(pose)
    for j, v in P.FIST_FINGER[name].items():
        q[f"{name}_{j}"] = v
    return q


def with_thumb(pose, spec):
    q = dict(pose)
    for j in ("cmc", "j3", "j2", "j1"):
        q[f"thumb_{j}"] = spec.get(j, 0.0)
    return q


def timeline():
    """(時刻[s], 姿勢) の列。最後は最初と同じ姿勢でループする。"""
    open_ = zero_pose()
    k = [(0.0, open_), (0.4, open_)]
    p = open_
    t = 0.4
    # 1 本ずつ曲げる（少し重ねて次へ）
    for name in ALL_FINGERS:
        q = with_finger(p, name)
        k.append((t + 0.55, q))
        p = q
        t += 0.55
    # 握る: 親指を閉じる
    q = with_thumb(p, P.FIST_THUMB)
    k.append((t + 0.65, q))
    t += 0.65
    k.append((t + 0.4, q))   # 握ったまま
    t += 0.4
    # 開く
    k.append((t + 0.9, open_))
    t += 0.9
    k.append((t + 0.2, open_))
    t += 0.2
    # 親指を動かす: 横へ振って戻す → 曲げて戻す
    k.append((t + 0.45, with_thumb(open_, P.THUMB_SWING_DOWN)))
    t += 0.45
    k.append((t + 0.6, with_thumb(open_, P.THUMB_SWING_UP)))
    t += 0.6
    k.append((t + 0.35, open_))
    t += 0.35
    k.append((t + 0.65, with_thumb(open_, P.THUMB_CURL)))
    t += 0.65
    k.append((t + 0.55, open_))
    t += 0.55
    # 手首を動かす: 枠の左右の柱の軸で曲げる → 前腕の口の中の回転部の軸で振る
    for dt, q in ((0.5, dict(open_, wrist=P.WRIST_FORWARD)), (0.7, dict(open_, wrist=P.WRIST_BACK)),
                  (0.5, dict(open_, wrist_dev=P.WRIST_DEV)), (0.55, dict(open_, wrist_dev=-P.WRIST_DEV)),
                  (0.4, open_)):
        k.append((t + dt, q))
        t += dt
    k.append((P.LOOP_SECONDS, open_))
    assert t <= P.LOOP_SECONDS + 1e-6, t
    check_limits(k)
    return k


def _limit(name):
    if name == "wrist":
        return P.WRIST_LIMITS
    if name == "wrist_dev":
        return P.WRIST_DEV_LIMITS
    f, j = name.split("_")
    return P.THUMB_JOINT_LIMITS[j] if f == "thumb" else P.FINGER_JOINT_LIMITS[j]


def check_limits(k):
    for _, pose in k:
        for j, v in pose.items():
            lo, hi = _limit(j)
            assert lo - 1e-6 <= v <= hi + 1e-6, f"{j}={v} が範囲 {lo}..{hi} の外"


def apply_keys(joints):
    """鍵を打つ。曲線は両端で速度 0 になる BEZIER（既定の AUTO_CLAMPED）。"""
    for t, pose in timeline():
        frame = 1 + round(t * P.FPS)
        for name, v in pose.items():
            ob, axis, base = joints[name]
            e = list(base)
            e[axis] = base[axis] + math.radians(v)
            ob.rotation_euler[axis] = e[axis]
            ob.keyframe_insert("rotation_euler", index=axis, frame=frame)
    sc = bpy.context.scene
    sc.render.fps = P.FPS
    sc.frame_start = 1
    # 最後の鍵（ループの継ぎ目）と最初のコマは同じ姿勢なので、動画は 1 コマ手前で切る
    sc.frame_end = round(P.LOOP_SECONDS * P.FPS)
    return sc.frame_start, sc.frame_end


def merge_animations(path):
    """関節ごとに分かれたクリップを 1 本にまとめる。分かれたままだと、再生側が 1 本選ぶと 1 関節しか動かない。"""
    import json
    import struct
    with open(path, "rb") as f:
        magic, ver, _ = struct.unpack("<4sII", f.read(12))
        n, kind = struct.unpack("<I4s", f.read(8))
        assert magic == b"glTF" and kind == b"JSON"
        g = json.loads(f.read(n).decode("utf-8"))
        rest = f.read()
    channels, samplers = [], []
    for a in g.get("animations", []):
        off = len(samplers)
        samplers += a["samplers"]
        for c in a["channels"]:
            c = dict(c)
            c["sampler"] += off
            channels.append(c)
    g["animations"] = [{"name": "hand_loop", "channels": channels, "samplers": samplers}]
    body = json.dumps(g, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    body += b" " * ((4 - len(body) % 4) % 4)
    total = 12 + 8 + len(body) + len(rest)
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", ver, total))
        f.write(struct.pack("<I4s", len(body), b"JSON"))
        f.write(body)
        f.write(rest)
    os.replace(tmp, path)


def export_glb(path, objs):
    sc = bpy.context.scene
    keep = sc.frame_end
    sc.frame_end = keep + 1  # GLB は継ぎ目のコマまで持つ
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs.values():
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs["forearm"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True,
                              export_animations=True, export_animation_mode="SCENE", export_frame_range=True,
                              export_force_sampling=True, export_apply=False,
                              export_yup=True, export_materials="EXPORT")
    sc.frame_end = keep
    merge_animations(path)


def render_mp4(path, res, samples, view="front"):
    sc = bpy.context.scene
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.cycles.samples = samples
    sc.render.image_settings.media_type = "VIDEO"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.ffmpeg.ffmpeg_preset = "GOOD"
    sc.render.ffmpeg.gopsize = 15
    base = os.path.splitext(path)[0] + "_"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sc.render.filepath = base
    bpy.ops.render.render(animation=True)
    made = f"{base}{sc.frame_start:04d}-{sc.frame_end:04d}.mp4"
    if os.path.exists(path):
        os.remove(path)
    os.rename(made, path)


def fit_video_camera(objs, fs, fe, az):
    """全コマの手が画面に収まる範囲で、いちばん大きく映る焦点距離と注視点を求める。"""
    from mathutils import Vector
    sc = bpy.context.scene
    pts = []
    for fr in range(fs, fe + 1, 3):
        sc.frame_set(fr)
        bpy.context.view_layer.update()
        for name, ob in objs.items():
            if name == "forearm":
                continue          # 前腕は画面の下から外へ出す
            mw = ob.matrix_world
            pts += [mw @ Vector(c) for c in ob.bound_box]
    c = {"az": az, "pitch": P.VIDEO_PITCH, "roll": 0.0, "tx": 0.0, "tz": 120.0, "dist": P.VIDEO_DIST, "f": 1500.0}
    for _ in range(6):
        F, Rt, Up, Rt0 = ST.camera_axes(c)
        C = ST.camera_pos(c)
        xs = [(p - C).dot(Rt) / (p - C).dot(F) for p in pts]
        ys = [(p - C).dot(Up) / (p - C).dot(F) for p in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        c["tx"] += cx * c["dist"]
        c["tz"] += cy * c["dist"]
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    c["f"] = ST.P.MM * 0 + 1254.0 * (1 - 2 * P.VIDEO_MARGIN) / span
    return c


def place_video(st, c):
    """壁を手の後ろへ置く。"""
    from mathutils import Vector
    F, Rt, Up, _ = ST.camera_axes(c)
    C = ST.camera_pos(c)
    a = math.radians(c["az"])
    fwd = Vector((-math.sin(a), math.cos(a), 0))
    q = fwd * 0.16 - C
    row = 627 - c["f"] * q.dot(Up) / q.dot(F)
    ST.place_view(st, {"front": c}, "front", row=row, light_key="video")


if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    res = int(ST._arg("--res", 960))
    samples = int(ST._arg("--samples", 48))
    glb = ST._arg("--glb", None)
    mp4 = ST._arg("--mp4", None)
    view = ST._arg("--view", "front")
    st = ST.setup_scene(res, samples)
    objs, _, joints = HM.build_hand()
    fs, fe = apply_keys(joints)
    print("コマ", fs, fe, "秒", (fe - fs + 1) / P.FPS)
    az = float(ST._arg("--az", P.VIDEO_AZ))
    cam_view = fit_video_camera(objs, fs, fe, az)
    print("動画のカメラ", {k: round(v, 1) for k, v in cam_view.items()})
    place_video(st, cam_view)
    stills = ST._arg("--stills", None)
    if stills:
        for fr in stills.split(","):
            bpy.context.scene.frame_set(int(fr))
            ST.render_still(os.path.join(ST._arg("--stills-dir", ST.RENDER_DIR), f"pose-{int(fr):04d}.png"))
    if glb:
        export_glb(glb, objs)
        print("GLB:", glb, os.path.getsize(glb))
    if mp4:
        render_mp4(mp4, res, samples, view)
        print("MP4:", mp4, os.path.getsize(mp4))
