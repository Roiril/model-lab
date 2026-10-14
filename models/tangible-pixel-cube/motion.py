"""サーボ角 -> 全部品の姿勢（motion.json）。bpy 非依存。

    py -3.11 models/tangible-pixel-cube/motion.py [--step 1.0]

寸法と運動学は params.py / kinematics.py / cams.py / patterns.py を読む（値を書き写さない）。
- 軸 j（行 j）の gear_j / cam_i_j（5 枚）/ shaft_j（-X 端の部品）は数珠つなぎで 1 つの剛体。Y=axis_y(j), Z=Zc を通る X 軸まわりに axis_angle 度回る
- horn_coupler と sg92r_horn はサーボ軸（Y=0, Z=Zs）の X 軸まわりに servo_delta 度回る
- pixel_i_j は Z だけ動く。高さは cams.py のカムの支持関数 h*（接点の高さ。表どおりの高さを作る実カム）
- housing / bezel / guide_plate / sg92r は動かない（単位行列）。phase_comb（組立治具）は運動表に入れない
行列は 4x4 の列優先（要素 12,13,14 が並進 X,Y,Z、mm）。回転は右ねじ（+Y から +Z へ）が正。
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import params as P  # noqa: E402
import kinematics as K  # noqa: E402
import cams as C  # noqa: E402
import patterns as PT  # noqa: E402

BUILD = os.path.join(HERE, "build")
MM = 1000.0
STEP_DEG = 1.0                      # motion.json のサーボ角の刻み（度）
DURATION_S = 3.0                    # 記録用。片道の目安時間（simulate.py と同じ）

STATIC_PARTS = ("housing", "bezel", "guide_plate", "sg92r", "servo_clip_0", "servo_clip_1")
SERVO_PARTS = ("sg92r_horn", "horn_coupler")          # サーボ軸まわり
PHASE_JIG = "phase_comb"                               # 運動表には入れない


def part_ids():
    """運動表に載る部品 id。params.PART_IDS（親が決めた正本）に EXTRA_PART_IDS（C クリップ）を足し、phase_comb を除く"""
    base = list(getattr(P, "PART_IDS", None) or (
        ["housing", "bezel", "guide_plate", "sg92r", "sg92r_horn", "horn_coupler"]
        + [f"shaft_{j}" for j in range(P.N)] + [f"gear_{j}" for j in range(P.N)]
        + [f"cam_{i}_{j}" for j in range(P.N) for i in range(P.N)]
        + [f"pixel_{i}_{j}" for j in range(P.N) for i in range(P.N)]))
    base += list(getattr(P, "EXTRA_PART_IDS", []))
    out = []
    for pid in base:
        if pid != PHASE_JIG and pid not in out:
            out.append(pid)
    return out


def classify(pid):
    """部品 id の動き方。("static",) / ("servo",) / ("axis", j) / ("pixel", i, j)。知らない id は ValueError（黙って固定にしない）"""
    if pid in STATIC_PARTS:
        return ("static",)
    if pid in SERVO_PARTS:
        return ("servo",)
    parts = pid.split("_")
    if parts[0] in ("shaft", "gear") and len(parts) == 2 and parts[1].isdigit():
        return ("axis", int(parts[1]))
    if parts[0] == "cam" and len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
        return ("axis", int(parts[2]))
    if parts[0] == "pixel" and len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
        return ("pixel", int(parts[1]), int(parts[2]))
    raise ValueError(f"動き方が分からない部品 id: {pid}（motion.py の classify に足す）")


def identity():
    return [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]


def rot_x_matrix(angle_deg, y0_m, z0_m):
    """点 (*, y0, z0) を通る X 軸まわりに angle_deg 回す剛体。p' = R (p - p0) + p0。並進は mm"""
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    y0, z0 = y0_m * MM, z0_m * MM
    ty = y0 - (c * y0 - s * z0)
    tz = z0 - (s * y0 + c * z0)
    return [1.0, 0.0, 0.0, 0.0,
            0.0, c, s, 0.0,
            0.0, -s, c, 0.0,
            0.0, ty, tz, 1.0]


def trans_z_matrix(dz_mm):
    m = identity()
    m[14] = dz_mm
    return m


def build_cams():
    """patterns.py の表からカムを作る（motion.json と同じ入力で simulate.py も呼ぶ）"""
    return C.build_all(PT.TABLES)


def axis_of_part(pid):
    """軸まわりに回る部品（shaft_j / gear_j / cam_i_j）の j。それ以外は None"""
    kind = classify(pid)
    return kind[1] if kind[0] == "axis" else None


def pixel_heights_mm(cams, theta_deg):
    """5x5 の画素の高さ h*（mm、面一 = 0）。[j][i]"""
    return [[K.pixel_height(cams[j][i], K.axis_angle(theta_deg, j)) * MM for i in range(P.N)] for j in range(P.N)]


def transforms(theta_deg, cams):
    """サーボ角 theta の全部品の行列"""
    servo = rot_x_matrix(K.servo_delta(theta_deg), 0.0, P.SERVO_AXIS_Z)
    axis = [rot_x_matrix(K.axis_angle(theta_deg, j), K.axis_y(j), P.CAM_AXIS_Z) for j in range(P.N)]
    hh = pixel_heights_mm(cams, theta_deg)
    out = {}
    for pid in part_ids():
        kind = classify(pid)
        if kind[0] == "static":
            out[pid] = identity()
        elif kind[0] == "servo":
            out[pid] = servo[:]
        elif kind[0] == "axis":
            out[pid] = axis[kind[1]][:]
        else:
            out[pid] = trans_z_matrix(hh[kind[2]][kind[1]])
    return out


def servo_angles(step_deg=STEP_DEG):
    n = int(round((P.SERVO_MAX_DEG - P.SERVO_MIN_DEG) / step_deg))
    return [round(P.SERVO_MIN_DEG + k * step_deg, 10) for k in range(n + 1)]


def digest(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def motion_document(step_deg=STEP_DEG, cams=None):
    cams = build_cams() if cams is None else cams
    frames = [{"servo_deg": th, "transforms": transforms(th, cams)} for th in servo_angles(step_deg)]
    patterns = [{"id": PT.NAMES[k], "label": PT.LABELS_JA[k], "servo_deg": P.TABLE_THETA[k]} for k in range(P.K)]
    return {
        "home_servo_deg": P.THETA_FLAT,
        "duration_s": DURATION_S,
        "easing": "quintic_smoothstep",
        "patterns": patterns,
        "stepDeg": step_deg,
        "gRatio": P.G_RATIO,
        "axisDir": list(P.AXIS_DIR),
        "pixelZ": "Z 並進 = cams.py のカムの支持関数 h*（mm、面一 = 0）。frames の間は線形補間",
        "excludedParts": [PHASE_JIG],
        "sourceSha256": {f"models/tangible-pixel-cube/{name}": digest(os.path.join(HERE, name))
                         for name in ("params.py", "kinematics.py", "cams.py", "patterns.py", "motion.py")},
        "frames": frames,
    }


def write_motion(step_deg=STEP_DEG):
    os.makedirs(BUILD, exist_ok=True)
    target = os.path.join(BUILD, "motion.json")
    tmp = target + ".tmp"
    doc = motion_document(step_deg)
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, target)
    return target, len(doc["frames"]), len(part_ids())


if __name__ == "__main__":
    step = STEP_DEG
    if "--step" in sys.argv:
        step = float(sys.argv[sys.argv.index("--step") + 1])
    path, n_frames, n_parts = write_motion(step)
    print("wrote", path, "frames:", n_frames, "parts:", n_parts, "size:", os.path.getsize(path), "bytes")
