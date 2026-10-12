"""motion.json の検査。実行: py -3.11 models/tangible-pixel-cube/test_motion.py

build/motion.json を読み、params.py / kinematics.py / cams.py / patterns.py から独立に作り直した値と照合する。
(1) 通る側: 現在の motion.json が全項目を通る
(2) 止める側（計器の校正）: わざと壊した複製（拡大・Z のずれ・軸の向き・増速比・古い入力の SHA）を、同じ検査が全部落とす
通る側と止める側の両方が期待どおりでなければ、全体が落ちる。
"""
import copy
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import params as P  # noqa: E402
import kinematics as K  # noqa: E402
import cams as C  # noqa: E402
import patterns as PT  # noqa: E402
import motion as M  # noqa: E402

MM = 1000.0
N = P.N
RB_MM = P.CAM_RB * MM
TOL_MAT = 1e-9
TOL_Z_MM = 1e-9
TOL_STOP_MM = 0.05
TOL_INTERP_MM = 0.06    # 接点が頂点から頂点へ移るところで高さの傾きが跳ぶ（折れ線）。1 度刻みの線形補間は最大 0.045mm ずれる
TOL_SIM_MM = 1e-6


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


def angle_of(m):
    return math.degrees(math.atan2(m[6], m[5]))


def apply(m, p):
    x, y, z = p
    return (m[0] * x + m[4] * y + m[8] * z + m[12],
            m[1] * x + m[5] * y + m[9] * z + m[13],
            m[2] * x + m[6] * y + m[10] * z + m[14])


def true_height_mm(cam, phi_deg):
    """カムの輪郭から直接求めた h*（mm、面一 = 0）。kinematics を通さない独立の計算"""
    v = np.asarray(cam["vertices"], dtype=float)
    r = math.radians(phi_deg)
    return float((v[:, 0] * math.sin(r) + v[:, 1] * math.cos(r)).max()) - RB_MM


def expected_ids():
    """params.py の部品表（PART_IDS + EXTRA_PART_IDS）から phase_comb を除いた集合。motion.py の part_ids を通さずに数える"""
    ids = set(getattr(P, "PART_IDS", [])) | set(getattr(P, "EXTRA_PART_IDS", []))
    ids.discard("phase_comb")
    return ids


# --- 検査（doc を受けて (ok, 詳細) を返す。壊した複製にも同じものを掛ける）------------------------------
def check_frames(doc, cams):
    th = [f["servo_deg"] for f in doc["frames"]]
    step = th[1] - th[0] if len(th) > 1 else 0.0
    ascending = all(b > a for a, b in zip(th, th[1:]))
    uniform = all(abs((b - a) - step) < 1e-9 for a, b in zip(th, th[1:]))
    covers = th[0] <= P.SERVO_MIN_DEG + 1e-9 and th[-1] >= P.SERVO_MAX_DEG - 1e-9
    return ascending and uniform and covers, f"{len(th)} 枚、{th[0]}..{th[-1]} 度、刻み {step}"


def check_ids(doc, cams):
    want = expected_ids()
    bad = []
    for f in doc["frames"]:
        got = set(f["transforms"])
        if got != want:
            bad.append((f["servo_deg"], sorted(got ^ want)[:5]))
            break
    return not bad and "phase_comb" not in doc["frames"][0]["transforms"] and len(want) >= 66, f"{len(want)} 部品、phase_comb は無し"


def check_finite_rigid(doc, cams):
    worst_orth = 0.0
    worst_det = 0.0
    for f in doc["frames"]:
        for pid, m in f["transforms"].items():
            if len(m) != 16 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in m):
                return False, f"{pid} @ {f['servo_deg']}: 16 要素の有限な数ではない"
            if (m[3], m[7], m[11], m[15]) != (0.0, 0.0, 0.0, 1.0):
                return False, f"{pid} @ {f['servo_deg']}: 最下行が (0,0,0,1) ではない"
            r = np.array([[m[0], m[4], m[8]], [m[1], m[5], m[9]], [m[2], m[6], m[10]]])
            worst_orth = max(worst_orth, float(np.abs(r.T @ r - np.eye(3)).max()))
            worst_det = max(worst_det, abs(float(np.linalg.det(r)) - 1.0))
    return worst_orth < TOL_MAT and worst_det < TOL_MAT, f"直交のずれ最大 {worst_orth:.2e}、行列式のずれ最大 {worst_det:.2e}"


def check_rotation_parts(doc, cams):
    worst_angle = 0.0
    worst_fix = 0.0
    for f in doc["frames"]:
        th = f["servo_deg"]
        t = f["transforms"]
        for pid, m in t.items():
            j = M.axis_of_part(pid)
            if pid in M.SERVO_PARTS:
                y0, z0, want = 0.0, P.SERVO_AXIS_Z * MM, K.servo_delta(th)
            elif j is not None:
                y0, z0, want = K.axis_y(j) * MM, P.CAM_AXIS_Z * MM, K.axis_angle(th, j)
            else:
                continue
            worst_angle = max(worst_angle, abs(wrap(angle_of(m) - want)))
            p = (0.0, y0, z0)
            q = apply(m, p)
            worst_fix = max(worst_fix, max(abs(q[0] - p[0]), abs(q[1] - p[1]), abs(q[2] - p[2])))
    return worst_angle < 1e-9 and worst_fix < 1e-9, f"角度のずれ最大 {worst_angle:.2e} 度、軸上の点のずれ最大 {worst_fix:.2e} mm"


def check_static_identity(doc, cams):
    ident = M.identity()
    for f in doc["frames"]:
        for pid in M.STATIC_PARTS:
            if f["transforms"][pid] != ident:
                return False, f"{pid} @ {f['servo_deg']} が単位行列でない"
    return True, ", ".join(M.STATIC_PARTS)


def check_pixel_z(doc, cams):
    worst = 0.0
    where = None
    ident_ok = True
    for f in doc["frames"]:
        th = f["servo_deg"]
        for j in range(N):
            phi = K.axis_angle(th, j)
            for i in range(N):
                m = f["transforms"][f"pixel_{i}_{j}"]
                if any(abs(m[k] - e) > 1e-12 for k, e in enumerate(M.identity()) if k != 14):
                    ident_ok = False
                err = abs(m[14] - true_height_mm(cams[j][i], phi))
                if err > worst:
                    worst, where = err, (th, i, j)
    return ident_ok and worst < TOL_Z_MM, f"Z の独立再計算との差の最大 {worst:.2e} mm {where}、Z 以外は単位行列 {ident_ok}"


def check_stop_heights(doc, cams):
    by_th = {round(f["servo_deg"], 6): f for f in doc["frames"]}
    worst = 0.0
    for k in range(P.K):
        f = by_th.get(round(P.TABLE_THETA[k], 6))
        if f is None:
            return False, f"表 {k} のサーボ角 {P.TABLE_THETA[k]} の frame が無い"
        for j in range(N):
            for i in range(N):
                worst = max(worst, abs(f["transforms"][f"pixel_{i}_{j}"][14] - PT.TABLES[k][j][i]))
    return worst <= TOL_STOP_MM, f"表の停止角（{', '.join(str(t) for t in P.TABLE_THETA)}）で画素の高さと表の差の最大 {worst:.2e} mm"


def check_axis_alternation(doc, cams):
    bad = []
    for f in doc["frames"]:
        d = K.servo_delta(f["servo_deg"])
        if abs(d) < 1e-9:
            continue
        ang = [wrap(angle_of(f["transforms"][f"shaft_{j}"])) for j in range(N)]
        if abs(d) * P.G_RATIO < 179.0:        # 折り返す前の範囲だけ符号を見る
            for j in range(N - 1):
                if ang[j] * ang[j + 1] >= 0:
                    bad.append((f["servo_deg"], j))
            for j in range(N):
                if abs(ang[j] - P.AXIS_DIR[j] * P.G_RATIO * d) > 1e-9:
                    bad.append((f["servo_deg"], f"j{j} 角度"))
        if bad:
            break
    return not bad, f"隣り合う軸の回転が互いに逆（軸 0..4 の向き {list(P.AXIS_DIR)}）{bad[:3] if bad else ''}"


def check_speed_ratio(doc, cams):
    frames = doc["frames"]
    worst = 0.0
    worst_servo = 0.0
    for a, b in zip(frames, frames[1:]):
        dth = b["servo_deg"] - a["servo_deg"]
        d2 = wrap(angle_of(b["transforms"]["shaft_2"]) - angle_of(a["transforms"]["shaft_2"]))
        worst = max(worst, abs(d2 / dth - P.AXIS_DIR[2] * P.G_RATIO))
        ds = wrap(angle_of(b["transforms"]["horn_coupler"]) - angle_of(a["transforms"]["horn_coupler"]))
        worst_servo = max(worst_servo, abs(ds / dth - 1.0))
    return worst < 1e-9 and worst_servo < 1e-9, f"中央の軸 / サーボ = -{P.G_RATIO:.6f}（{P.SERVO_Z}/{P.END_Z}）、ずれ最大 {worst:.2e}、受けのずれ最大 {worst_servo:.2e}"


def check_interpolation(doc, cams):
    frames = doc["frames"]
    worst = 0.0
    for a, b in zip(frames, frames[1:]):
        mid = (a["servo_deg"] + b["servo_deg"]) / 2.0
        for j in range(N):
            phi = K.axis_angle(mid, j)
            for i in range(N):
                lin = (a["transforms"][f"pixel_{i}_{j}"][14] + b["transforms"][f"pixel_{i}_{j}"][14]) / 2.0
                worst = max(worst, abs(lin - true_height_mm(cams[j][i], phi)))
    return worst < TOL_INTERP_MM, f"frames の間の線形補間と実カムの差の最大 {worst:.2e} mm（許容 {TOL_INTERP_MM}）"


def check_sim_tables(doc, cams):
    path = os.path.join(HERE, "build", "sim_tables.json")
    if not os.path.isfile(path):
        return True, "build/sim_tables.json が無いので省略"
    tables = json.load(open(path, encoding="utf-8"))
    rows = {round(r["servoDeg"], 6): r for r in tables["rows"]}
    worst = 0.0
    n = 0
    for f in doc["frames"]:
        row = rows.get(round(f["servo_deg"], 6))
        if row is None:
            continue
        n += 1
        for j in range(N):
            for i in range(N):
                worst = max(worst, abs(row["liftsMm"][j * N + i] - f["transforms"][f"pixel_{i}_{j}"][14]))
    return n > 0 and worst < TOL_SIM_MM, f"物理表の liftsMm と motion の Z の差の最大 {worst:.2e} mm（{n} 角度）"


def check_meta(doc, cams):
    ok = doc.get("home_servo_deg") == P.THETA_FLAT
    pats = doc.get("patterns", [])
    ok = ok and [p["servo_deg"] for p in pats] == list(P.TABLE_THETA) and [p["id"] for p in pats] == list(PT.NAMES)
    return ok, f"home_servo_deg {doc.get('home_servo_deg')}、patterns {[p['id'] for p in pats]}"


def check_fresh(doc, cams):
    stale = []
    for rel, digest in doc.get("sourceSha256", {}).items():
        name = os.path.basename(rel)
        if M.digest(os.path.join(HERE, name)) != digest:
            stale.append(name)
    return bool(doc.get("sourceSha256")) and not stale, f"入力の SHA-256 が現在のファイルと一致（古い: {stale or 'なし'}）"


CHECKS = [
    ("角度が昇順・等間隔で SERVO_MIN..MAX を覆う", check_frames),
    ("部品 id が params.py の部品表（phase_comb を除く）と一致", check_ids),
    ("全行列が 16 要素・有限・最下行 (0,0,0,1)・直交・行列式 1", check_finite_rigid),
    ("軸・カム・歯車・受け・ホーンの回転角が kinematics と一致し軸上の点が動かない", check_rotation_parts),
    ("housing / bezel / guide_plate / sg92r は単位行列", check_static_identity),
    ("画素の Z 並進が実カムの h* と一致（Z 以外は単位行列）", check_pixel_z),
    ("表のサーボ角で画素の高さが patterns.py の表どおり（±0.05mm）", check_stop_heights),
    ("軸の回転方向が交互で、角度 = 向き x g x サーボ変位", check_axis_alternation),
    ("中央軸の角速度がサーボの g 倍、受けはサーボと同じ", check_speed_ratio),
    ("frames の間の画素の線形補間が実カムから 0.06mm 以内（隙間 0.2mm より十分小さい）", check_interpolation),
    ("物理表（sim_tables.json）の liftsMm と motion の Z が一致", check_sim_tables),
    ("home_servo_deg と patterns が params / patterns.py と一致", check_meta),
    ("motion.json が現在の入力ファイル（SHA-256）から作られている", check_fresh),
]

fails = []


def report(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" : " + detail if detail else ""))
    if not ok:
        fails.append(name)


def corrupt(doc, kind):
    d = copy.deepcopy(doc)
    mid = len(d["frames"]) // 2 + 3
    t = d["frames"][mid]["transforms"]
    if kind == "scale":                 # 拡大（剛体でなくなる）
        t["shaft_1"][0] *= 1.01
    elif kind == "pixel_z":             # 画素の Z が実カムからずれる
        t["pixel_2_3"][14] += 0.2
    elif kind == "direction":           # 軸 1 の回転が逆（隣と同じ向きになる）
        a = -math.radians(K.axis_angle(d["frames"][mid]["servo_deg"], 1))
        c, s = math.cos(a), math.sin(a)
        y0, z0 = K.axis_y(1) * MM, P.CAM_AXIS_Z * MM
        t["shaft_1"][5], t["shaft_1"][6], t["shaft_1"][9], t["shaft_1"][10] = c, s, -s, c
        t["shaft_1"][13], t["shaft_1"][14] = y0 - (c * y0 - s * z0), z0 - (s * y0 + c * z0)
    elif kind == "ratio":               # 中央軸の増速比が違う（g の代わりに 2.0）
        for f in d["frames"]:
            a = math.radians(P.AXIS_DIR[2] * 2.0 * K.servo_delta(f["servo_deg"]))
            c, s = math.cos(a), math.sin(a)
            y0, z0 = K.axis_y(2) * MM, P.CAM_AXIS_Z * MM
            m = f["transforms"]["shaft_2"]
            m[5], m[6], m[9], m[10] = c, s, -s, c
            m[13], m[14] = y0 - (c * y0 - s * z0), z0 - (s * y0 + c * z0)
    elif kind == "stale":               # 古い入力から作られた motion.json
        key = next(iter(d["sourceSha256"]))
        d["sourceSha256"][key] = "0" * 64
    elif kind == "missing_part":
        del d["frames"][mid]["transforms"]["cam_0_0"]
    return d


NEGATIVE = [
    ("scale", "check_finite_rigid", "拡大した行列"),
    ("pixel_z", "check_pixel_z", "画素の Z を 0.2mm ずらす"),
    ("direction", "check_axis_alternation", "軸 1 の回転を逆にする"),
    ("ratio", "check_speed_ratio", "増速比を 2.0 にする"),
    ("stale", "check_fresh", "入力の SHA が古い"),
    ("missing_part", "check_ids", "部品が 1 つ欠ける"),
]


def main():
    path = os.path.join(HERE, "build", "motion.json")
    if not os.path.isfile(path):
        print("FAIL build/motion.json が無い。先に py -3.11 models/tangible-pixel-cube/motion.py")
        sys.exit(1)
    doc = json.load(open(path, encoding="utf-8"))
    cams = M.build_cams()
    funcs = {fn.__name__: fn for _, fn in CHECKS}
    for name, fn in CHECKS:
        ok, detail = fn(doc, cams)
        report(name, ok, detail)
    n_pos = len(CHECKS)
    for kind, fn_name, label in NEGATIVE:
        bad = corrupt(doc, kind)
        ok, detail = funcs[fn_name](bad, cams)
        report(f"負例: {label} -> {fn_name} が落とす", not ok, detail)
    total = n_pos + len(NEGATIVE)
    if fails:
        print(f"FAILED {len(fails)}/{total}: " + "; ".join(fails))
        sys.exit(1)
    print(f"ALL PASS {total}/{total}（通る側 {n_pos}、止める側 {len(NEGATIVE)}）")


if __name__ == "__main__":
    main()
