"""タンジブル画素キューブの物理検証（1 自由度の運動方程式。Blender 不要）。

    py -3.11 models/tangible-pixel-cube/simulate.py

一般化座標はサーボ角 q。25 画素は重力でカムに載る（片側接触）。画素の上下 z_p(q) は cams.py の実カムの支持関数 h*
（motion.py と同じ値）。回転部（軸・カム・歯車・受け・ホーン）の慣性は増速比 g の 2 乗でサーボ軸へ換算する。
摩擦は足と板カムの滑り・案内（こじれ係数 κ）・軸受け・歯車効率をサーボ軸のトルクへ換算する（クーロン、符号は速度の逆）。
サーボは C1 と同じトルク上限つき位置制御（tools/lattice_simulation.py の TableSim。viewer/lattice/sim.mjs と同じ式）。
質量と慣性は build/<id>.stl があれば閉じた STL の符号付き四面体積分、無ければ params.py と cams.py からの見積もり。
出力: build/sim_tables.json, build/simulate_report.json, build/sim_js_reference.json（Python の軌跡。test_sim_js.mjs が読む）
"""
import argparse
import concurrent.futures
import copy
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))
sys.stdout.reconfigure(encoding="utf-8")

import params as P  # noqa: E402
import kinematics as K  # noqa: E402
import cams as C  # noqa: E402
import patterns as PT  # noqa: E402
import motion as M  # noqa: E402
import lattice_simulation as common  # noqa: E402

MODEL = "tangible-pixel-cube"
BUILD = HERE / "build"
MM = 1000.0
GRAV = common.G
N = P.N
NP = N * N                                  # 画素の数。群の添字は j * N + i
RB_MM = P.CAM_RB * MM

# --- 仮定（report にそのまま書く）----------------------------------------------------
PLA_DENSITY = 1240.0                        # kg/m3（PLA 1.24 g/cm3）
FILL_FACTOR = 0.85                          # 実効密度 = PLA の 85%。壁 2 周 + 上下 5 層 + 充填 15% で、薄肉の小部品は外殻が主
EFFECTIVE_DENSITY = PLA_DENSITY * FILL_FACTOR
PP_DENSITY = common.PP_DENSITY              # 付属ホーン（PP）
HORN_VOLUME_MM3 = 369.6                     # C1 の verify.py が付属ホーン STL から出した体積
TABLE_STEP_DEG = 0.25                       # 表の刻み（サーボ角）。sim の線形補間誤差と d2 の平滑化幅を決める
DURATION_S = M.DURATION_S                   # 片道の所要時間（3 秒）
SERVO_STALL = P.SERVO_STALL_NM
TORQUE_LIMIT = SERVO_STALL * P.TORQUE_FRAC  # 停動の 1/3
HEIGHT_TOL_MM = 0.05                        # 表の停止角での高さの許容
GEAR_ALPHA = math.radians(20.0)
JOURNAL_R = P.JOURNAL_D / 2.0               # +X の軸受け（Ø5）の半径（m）
JOURNAL_MX_R = P.JOURNAL_MX_D / 2.0         # -X の軸受け（Ø10）の半径（m）
BEARING_PX_X = (P.SHAFT_HALF_L + P.JOURNAL_END) / 2.0     # +X の軸受けの荷重の中心 X（m）。-X は対称
BEARING_SPAN = 2.0 * BEARING_PX_X
STOP_RUN_SOURCES = (P.SERVO_MIN_DEG, P.SERVO_MAX_DEG)      # 表へ入る出発角（両側から止める）

ROTATING_IDS = [pid for pid in M.part_ids() if M.classify(pid)[0] in ("axis", "servo")]     # 軸まわり・サーボ軸まわりに回る部品
PIXEL_IDS = [f"pixel_{i}_{j}" for j in range(N) for i in range(N)]      # 群の順（j 外側）


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rounded(value):
    return float(f"{value:.12g}")


def atomic_json(path, payload, indent=2):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    if indent is None:
        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    else:
        text = json.dumps(payload, ensure_ascii=False, indent=indent) + "\n"
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def source_hashes(extra=()):
    paths = [HERE / name for name in ("params.py", "kinematics.py", "cams.py", "patterns.py", "motion.py", "simulate.py",
                                      "test_sim_js.mjs")]
    paths += [ROOT / "tools/lattice_simulation.py", ROOT / "viewer/lattice/sim.mjs", ROOT / "models/sg92r-photo/params.py"]
    paths += list(extra)
    return {Path(p).resolve().relative_to(ROOT).as_posix(): digest(p) for p in paths if Path(p).is_file()}


# =============================================================================================
# 質量と慣性
# =============================================================================================
def polygon_props(V):
    """輪郭（頂点 (u, v) mm）の面積 mm2、重心 (mm, mm)、原点まわりの極二次モーメント mm4"""
    x, y = V[:, 0], V[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    c = x * y1 - x1 * y
    a = c.sum() / 2.0
    cx = ((x + x1) * c).sum() / (6.0 * a)
    cy = ((y + y1) * c).sum() / (6.0 * a)
    j = (((y * y + y * y1 + y1 * y1) * c).sum() + ((x * x + x * x1 + x1 * x1) * c).sum()) / 12.0
    return abs(a), float(cx), float(cy), abs(j)


def hex_bore(af_mm):
    """六角の面積 mm2 と原点まわりの極二次モーメント mm4（外接円半径 a = AF / sqrt3、J = 5/12 A a2）"""
    area = math.sqrt(3.0) / 2.0 * af_mm ** 2
    a2 = af_mm ** 2 / 3.0
    return area, 5.0 / 12.0 * area * a2


def estimate_row(mass_kg, com_m, i_axis, axis_yz):
    """見積もりの質量特性。i_axis = 回転軸まわりの慣性、axis_yz = 軸の (y0, z0)（m）。Ixx は重心まわりへ直す"""
    dy, dz = com_m[1] - axis_yz[0], com_m[2] - axis_yz[1]
    return {"massKg": mass_kg, "comM": list(com_m),
            "inertiaComKgm2": [i_axis - mass_kg * (dy * dy + dz * dz), 0.0, 0.0, 0.0, 0.0, 0.0],
            "source": "estimate"}


def estimated_properties(pid, cams):
    """build/<id>.stl が無い部品の質量特性。回転部は params.py と cams.py の形から、画素は PIXEL_MASS_G から"""
    rho = EFFECTIVE_DENSITY
    zc, zs = P.CAM_AXIS_Z, P.SERVO_AXIS_Z
    if pid.startswith("pixel_"):
        return {"massKg": P.PIXEL_MASS_G / 1000.0 * FILL_FACTOR, "comM": [0.0, 0.0, 0.0],
                "inertiaComKgm2": [0.0] * 6, "source": "estimate"}
    if pid.startswith("camshaft_"):
        # 胴 Ø10（-X の軸受け端 -JOURNAL_END から gear_j のハブ面 GEAR_HUB_X0 まで）+ 板カム 5 枚（胴の外へ出る分）+ +X の Ø5 の軸受け。STL が無いときの見積もり
        j = int(pid.split("_")[1])
        rb = P.CAMSHAFT_BODY_D * MM / 2.0
        body_len = (P.GEAR_HUB_X0 + P.JOURNAL_END) * MM
        vol_mm3 = math.pi * rb ** 2 * body_len
        i_pol = math.pi * rb ** 4 / 2.0 * body_len                          # mm5（極二次モーメント x 長さ）
        mx = my = 0.0
        t = P.CAM_T * MM
        for i in range(N):
            area, cu, cv, jp = polygon_props(np.asarray(cams[j][i]["vertices"], dtype=float))
            extra = max(area - math.pi * rb ** 2, 0.0)
            j_extra = max(jp - math.pi * rb ** 4 / 2.0, 0.0)
            vol_mm3 += extra * t
            i_pol += j_extra * t
            my += area * t * cu * (1.0 if extra > 0 else 0.0)      # 円の外の材料の一次モーメント = 輪郭全体の重心 x 面積（円は原点中心で寄与 0）
            mx += area * t * cv * (1.0 if extra > 0 else 0.0)
        m = rho * vol_mm3 * 1e-9
        com = (0.0, K.axis_y(j) + (my / vol_mm3) / MM, zc + (mx / vol_mm3) / MM)
        return estimate_row(m, ((P.GEAR_HUB_X0 - P.JOURNAL_END) / 2.0, com[1], com[2]), rho * i_pol * 1e-15, (K.axis_y(j), zc))
    if pid.startswith("gear_"):
        j = int(pid.split("_")[1])
        rp = P.CHAIN_GEAR_PD * MM / 2.0
        b_area, b_j = hex_bore(P.SHAFT_BORE_AF * MM)
        t = P.GEAR_T * MM
        vol = (math.pi * rp ** 2 - b_area) * t * 1e-9
        i_axis = rho * (math.pi * rp ** 4 / 2.0 - b_j) * t * 1e-15
        return estimate_row(rho * vol, ((P.GEAR_X0 + P.GEAR_X1) / 2.0, K.axis_y(j), zc), i_axis, (K.axis_y(j), zc))
    if pid == "horn_coupler":
        # 半円の歯車つきの受け: 半径 = 歯車のピッチ円、中心角 2 x 92 度、厚み = 受けの X 幅。歯の向きは +Z 側（サーボ 90 度）と仮定
        r = P.SERVO_GEAR_PD * MM / 2.0
        theta = 2.0 * math.radians(P.RECV_ARC_HALF_DEG)
        t = (P.RECV_X1 - P.RECV_X0) * MM
        vol = 0.5 * r * r * theta * t * 1e-9
        m = rho * vol
        half = theta / 2.0
        d = 2.0 * r * math.sin(half) / (3.0 * half) / MM
        i_axis = 0.5 * m * (r / MM) ** 2
        return estimate_row(m, ((P.RECV_X0 + P.RECV_X1) / 2.0, 0.0, zs + d), i_axis, (0.0, zs))
    if pid == "sg92r_horn":
        import importlib.util
        spec = importlib.util.spec_from_file_location("sg92r_photo_params_sim", ROOT / "models/sg92r-photo/params.py")
        sg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sg)
        m = PP_DENSITY * HORN_VOLUME_MM3 * 1e-9
        length = sg.HORN_RIGHT_X - sg.HORN_LEFT_X
        return estimate_row(m, (P.RECV_X0, 0.0, zs), m * length ** 2 / 12.0, (0.0, zs))
    raise KeyError(pid)


def load_mass_properties(cams):
    """部品ごとの質量特性。STL があって閉じていれば符号付き四面体積分、無ければ見積もり。(辞書, STL を使った id, 却下した STL, 使ったファイル)"""
    props, stl_used, rejected, files = {}, [], {}, []
    for pid in PIXEL_IDS + ROTATING_IDS:
        path = BUILD / f"{pid}.stl"
        density = PP_DENSITY if pid == "sg92r_horn" else EFFECTIVE_DENSITY
        row = None
        if path.is_file():
            try:
                triangles = common.read_stl(path)
                boundary, nonmanifold = common.edge_diagnostics(triangles)
                if boundary or nonmanifold:
                    rejected[pid] = f"閉じていない STL（開いた辺 {boundary}、非多様体辺 {nonmanifold}）"
                else:
                    row = common.signed_tetra_properties(triangles, density)
                    row.update({"source": "stl", "densityKgM3": density, "triangles": len(triangles), "sha256": digest(path)})
                    stl_used.append(pid)
                    files.append(path)
            except ValueError as error:
                rejected[pid] = str(error)
        if row is None:
            row = estimated_properties(pid, cams)
            row["densityKgM3"] = density
        props[pid] = row
    return props, stl_used, rejected, files


def axis_inertia(row, y0, z0):
    cx, cy, cz = row["comM"]
    return row["inertiaComKgm2"][0] + row["massKg"] * ((cy - y0) ** 2 + (cz - z0) ** 2)


# =============================================================================================
# 幾何（サーボ角の配列 -> 各画素の接点の高さ・横ずれ）
# =============================================================================================
def geometry(cams, q_deg):
    """q_deg（度の配列）の各 q で、25 画素（j * N + i）のカムの支持関数 h（mm）と接点の横ずれ e（mm）"""
    q = np.asarray(q_deg, dtype=float)
    h = np.empty((len(q), NP))
    e = np.empty((len(q), NP))
    for j in range(N):
        phi = K.axis_angle(q, j)
        for i in range(N):
            hh, ee = C.support(np.asarray(cams[j][i]["vertices"], dtype=float), phi)
            h[:, j * N + i] = hh
            e[:, j * N + i] = ee
    return h, e


# --- こじれ係数（design_check.py の guide_geometry / kappa と同じ式。同期は手で保つ。cross-check で照合する）---------
def guide_geometry(h):
    """h = 接点の高さ（軸からの支持関数、mm）。(z1, L_B, L_A): 足の下面から案内板の下端までの距離、窓と板を使った長さ、板だけの長さ"""
    zc = P.CAM_AXIS_Z * MM
    z0, z1p = P.PLATE_Z0 * MM, P.PLATE_Z1 * MM
    ft = P.FLANGE_TOP_FLUSH * MM
    bz0, bz1 = P.BEZEL_Z0 * MM, P.BEZEL_Z1 * MM
    zf = zc + h
    zlow = np.maximum(z0, zf)
    z1 = zlow - zf
    hh = h - RB_MM
    lo = np.maximum(bz0, ft + hh)
    hi = np.minimum(bz1, bz1 + hh)
    zw = (lo + np.maximum(lo, hi)) / 2
    return z1, zw - zlow, z1p - zlow


def kappa(mu_c, mu_g, e, z1, length, b):
    s = (mu_c + 2 * (np.abs(e) + np.maximum(z1, 0.0) * mu_c) / length) / (1 - 2 * mu_g * b / length)
    return mu_g * s


GUIDE_B = P.TOWER_W * MM / 2.0              # 案内の接触の横位置（茎の半幅、mm）


def kappa_grid(cams, mu_c, mu_g):
    """design_check.py と同じ 0.25 度の軸角格子で、全画素・サーボの全範囲の κ の最大（板だけ A、窓つき B）。位置も返す"""
    half = K.table_theta_to_phi_range()
    phi_all = np.arange(-180, 180, 0.25)
    phi = np.arange(-half, half + 1e-9, 0.25)
    sel = np.round((((phi + 180) % 360) - 180 + 180) / 0.25).astype(int) % len(phi_all)
    out = {"A": (0.0, None), "B": (0.0, None)}
    for j in range(N):
        for i in range(N):
            h_all, lat_all = C.support(np.asarray(cams[j][i]["vertices"], dtype=float), phi_all)
            hh, ee = h_all[sel], lat_all[sel]
            z1, lb, la = guide_geometry(hh)
            for key, length in (("B", lb), ("A", la)):
                kv = kappa(mu_c, mu_g, ee, z1, length, GUIDE_B)
                if float(kv.max()) > out[key][0]:
                    out[key] = (float(kv.max()), {"i": i, "j": j, "phiDeg": float(phi[kv.argmax()]),
                                                  "heightMm": float(hh[kv.argmax()] - RB_MM), "lateralMm": float(ee[kv.argmax()])})
    return out


# =============================================================================================
# 表（sim_tables.json）
# =============================================================================================
def build_tables(cams, props, mu_c, mu_g, hashes):
    masses = np.array([props[pid]["massKg"] for pid in PIXEL_IDS])
    weights = masses * GRAV
    rows_n = int(round((P.SERVO_MAX_DEG - P.SERVO_MIN_DEG) / TABLE_STEP_DEG)) + 1
    q_ext = P.SERVO_MIN_DEG + (np.arange(rows_n + 4) - 2) * TABLE_STEP_DEG       # 添字 m = k + 2（k = 行番号）
    q_rows = q_ext[2:-2]
    d = math.radians(TABLE_STEP_DEG)
    h_ext, _ = geometry(cams, q_ext)
    z_ext = (h_ext - RB_MM) / MM                                                  # 画素の高さ（m、面一 = 0）
    dz_ext = (z_ext[2:] - z_ext[:-2]) / (2.0 * d)                                 # k = -1 .. rows_n（長さ rows_n + 2）
    lifts = z_ext[2:-2]
    dz = dz_ext[1:-1]
    d2z = (z_ext[3:-1] - 2.0 * z_ext[2:-2] + z_ext[1:-3]) / (d * d)
    i_group_ext = (masses[None, :] * dz_ext ** 2).sum(axis=1)                      # k = -1 .. rows_n
    i_group = i_group_ext[1:-1]
    dm = (i_group_ext[2:] - i_group_ext[:-2]) / (2.0 * d)
    gravity_groups = (weights[None, :] * dz).sum(axis=1)

    # 回転部の慣性（サーボ軸へ換算）と重力トルク
    g = P.G_RATIO
    i_axes = np.zeros(N)
    w_rot = np.zeros(N)                    # 軸 j まわりの回転部の重さ（N）
    r_rot = np.zeros(N)                    # 同、2 つの軸受けへの分担で重みを付けた軸受けの半径（m）
    for j in range(N):
        for name in [p for p in ROTATING_IDS if M.axis_of_part(p) == j]:
            i_axes[j] += axis_inertia(props[name], K.axis_y(j), P.CAM_AXIS_Z)
            w_rot[j] += props[name]["massKg"] * GRAV
            share = float(np.clip((BEARING_PX_X - props[name]["comM"][0]) / BEARING_SPAN, 0.0, 1.0))
            r_rot[j] += props[name]["massKg"] * GRAV * ((1.0 - share) * JOURNAL_R + share * JOURNAL_MX_R)
        r_rot[j] = r_rot[j] / w_rot[j] if w_rot[j] > 0 else JOURNAL_R
    i_servo_parts = sum(axis_inertia(props[name], 0.0, P.SERVO_AXIS_Z) for name in ("horn_coupler", "sg92r_horn"))
    inertia_rest = i_servo_parts + g * g * float(i_axes.sum())
    gravity_rest = np.zeros(rows_n)
    for j in range(N):
        phi = np.radians(K.axis_angle(q_rows, j))
        for name in [p for p in ROTATING_IDS if M.axis_of_part(p) == j]:
            row = props[name]
            dy, dzc = row["comM"][1] - K.axis_y(j), row["comM"][2] - P.CAM_AXIS_Z
            gravity_rest += row["massKg"] * GRAV * (dy * np.cos(phi) - dzc * np.sin(phi)) * P.AXIS_DIR[j] * g
    delta = np.radians(q_rows - P.THETA_FLAT)
    for name in ("horn_coupler", "sg92r_horn"):
        row = props[name]
        dy, dzc = row["comM"][1], row["comM"][2] - P.SERVO_AXIS_Z
        gravity_rest += row["massKg"] * GRAV * (dy * np.cos(delta) - dzc * np.sin(delta))

    # 摩擦（サーボ軸のトルク。画素の重さに比例する分は contactFrictionGroupsNm、回転部の重さの分は servoFrictionNm へ）
    h_rows = h_ext[2:-2]
    _, e_rows = geometry(cams, q_rows)
    z1, _lb, la = guide_geometry(h_rows)
    kap = kappa(mu_c, mu_g, e_rows, z1, la, GUIDE_B)                  # 板だけの案内（保守的）
    kap_used = np.minimum(kap, 0.99)
    normal = weights[None, :] / (1.0 - kap_used)                      # 上へ動くときの接触力（案内の摩擦で増える）
    shape = (rows_n, N, N)                                            # [行番号, 軸 j, 画素 i]
    n3 = normal.reshape(shape)
    e3 = (e_rows / MM).reshape(shape)
    h3 = (h_rows / MM).reshape(shape)
    k3 = kap.reshape(shape)
    t_cons = np.abs((n3 * e3).sum(axis=2))                            # 軸まわりの保持トルク（符号つき和の大きさ）
    t_cam = (mu_c * n3 * h3).sum(axis=2)
    t_guide = (k3 * n3 * np.abs(e3)).sum(axis=2)
    t0 = t_cons + t_cam + t_guide
    fn = 1.0 / (P.CHAIN_GEAR_PD / 2.0 * math.cos(GEAR_ALPHA))         # 歯面力 = トルク / (ピッチ半径 cos α)
    m01, m12, m34 = t0[:, 0], t0[:, 0] + t0[:, 1], t0[:, 4]
    m23 = t0[:, 3] + t0[:, 4]
    msv = t0.sum(axis=1)
    f_gear = fn * np.stack([m01, m01 + m12, m12 + m23 + msv, m23 + m34, m34], axis=1)
    # 軸受けの荷重を 2 つの軸受け（+X Ø5、-X Ø10）に、軸の両端の単純支持でてこの比に分ける。-X の分担 = (X_px - x) / スパン
    def mx_share(x):
        return np.clip((BEARING_PX_X - x) / BEARING_SPAN, 0.0, 1.0)

    share_pix = mx_share(np.array([[K.cam_x(i, jj) for i in range(N)] for jj in range(N)]))     # [j, i]
    share_gear = float(mx_share((P.GEAR_X0 + P.GEAR_X1) / 2.0))
    r_pix = (1.0 - share_pix) * JOURNAL_R + share_pix * JOURNAL_MX_R                          # [j, i] 荷重で重みを付けた半径
    r_gear = (1.0 - share_gear) * JOURNAL_R + share_gear * JOURNAL_MX_R
    bear_pix = P.BEARING_MU * ((n3 * r_pix[None, :, :]).sum(axis=2) + f_gear * r_gear)
    meshes = np.array([1 + abs(j - 2) for j in range(N)])
    eta_inv = P.GEAR_EFF ** (-meshes.astype(float))
    contact_friction = g * (((t_cons + t_cam + t_guide + bear_pix) * eta_inv[None, :]) - t_cons).sum(axis=1)
    shaft_friction = g * float((P.BEARING_MU * r_rot * w_rot * eta_inv).sum())
    servo_friction = common.SERVO_FRICTION + shaft_friction

    rows = []
    for k in range(rows_n):
        rows.append({
            "servoDeg": rounded(q_rows[k]),
            "inertiaRestKgm2": rounded(inertia_rest),
            "inertiaGroupsKgm2": rounded(i_group[k]),
            "dMGroupsDqKgm2PerRad": rounded(dm[k]),
            "gravityRestNm": rounded(gravity_rest[k]),
            "gravityGroupsNm": rounded(gravity_groups[k]),
            "contactFrictionGroupsNm": rounded(contact_friction[k]),
            "liftsMm": [rounded(v * MM) for v in lifts[k]],
            "dLiftDqMPerRad": [rounded(v) for v in dz[k]],
            "d2LiftDq2MPerRad2": [rounded(v) for v in d2z[k]],
        })
    labels = [f"画素 {i + 1} 列 {j + 1} 行" for j in range(N) for i in range(N)]
    groups = [{"id": pid, "label": label, "massKg": rounded(props[pid]["massKg"]), "mass_g": rounded(props[pid]["massKg"] * 1000.0)}
              for pid, label in zip(PIXEL_IDS, labels)]
    tables = {
        "version": 1, "model": MODEL,
        "limitsDeg": [P.SERVO_MIN_DEG, P.SERVO_MAX_DEG],
        "duration_s": DURATION_S, "groups": groups,
        "contactModel": "gravity_one_sided", "contactBoundariesDeg": [],
        "columns": list(rows[0]), "rows": rows,
        "const": {
            "stallTorqueNm": SERVO_STALL, "noLoadSpeedRadS": common.NO_LOAD_SPEED, "controlBandRad": common.CONTROL_BAND,
            "motorInertiaKgm2": common.MOTOR_INERTIA, "servoFrictionNm": rounded(servo_friction),
            "servoEquivalentFrictionNm": common.SERVO_FRICTION, "rotatingBearingFrictionNm": rounded(shaft_friction),
            "camFrictionMu": mu_c, "guideFrictionMu": mu_g, "bearingFrictionMu": P.BEARING_MU, "bearingRadiusPxM": JOURNAL_R, "bearingRadiusMxM": JOURNAL_MX_R,
            "bearingMxShareOfGearForce": share_gear, "gearEfficiencyPerMesh": P.GEAR_EFF,
            "gRatio": g, "kappaModel": "plate_only",
            "gravityMS2": GRAV, "dtS": common.DT, "recordS": common.RECORD, "settleS": common.SETTLE, "contactToleranceN": 1.0e-8,
            "assumptions": {
                "mass": f"STL があれば閉じた STL の符号付き四面体積分、無ければ見積もり。実効密度 PLA {PLA_DENSITY:.0f} x {FILL_FACTOR} = {EFFECTIVE_DENSITY:.0f} kg/m3。付属ホーンは PP {PP_DENSITY:.0f}。",
                "inertia": "軸・カム・歯車の慣性は各軸まわり、g^2 でサーボ軸へ換算。受けとホーンはサーボ軸まわり。画素は m (dz/dq)^2。",
                "friction": "足と板カムの滑り mu_c N h、案内 kappa N |dz/dq|（板だけの案内 A、保守的）、軸受け mu_b (sum N + 歯面力 + 回転部の重さ) R_j、"
                            "歯車 1 噛合 0.9 を Σ(トルク x (1/eta^噛合数 - 1)) としてサーボ軸へ換算。N は上へ動くときの値 W/(1-kappa)（両方向に同じ大きさを使う保守側）。",
                "contact": "画素は重力でカムに追従する片側接触。接触力が負なら浮き上がり（不成立）。案内の摩擦を入れても接触力の符号は m(g + zdd) の符号と同じ。",
                "servo": "トルク上限つき位置制御（C1 と同じ）。停動 0.245 N m、無負荷 60 度 / 0.1 s、制御帯 4 度。",
                "polygonCam": "カムは 0.5 度刻みの凸多角形。d2z は 0.25 度（サーボ）の差分で頂点の切り替わりを平滑化している。",
            },
        },
        "massProperties": {pid: {**{k: v for k, v in props[pid].items() if k != "inertiaComKgm2"},
                                 "ixxComKgm2": props[pid]["inertiaComKgm2"][0]} for pid in PIXEL_IDS + ROTATING_IDS},
        "sourceHashes": hashes,
    }
    diag = {
        "kappaMaxUsed": float(kap.max()), "kappaClipped": bool((kap >= 0.99).any()),
        "inertiaRestKgm2": inertia_rest, "inertiaServoPartsKgm2": i_servo_parts, "inertiaAxesKgm2": [float(v) for v in i_axes],
        "rotatingWeightN": [float(v) for v in w_rot], "shaftFrictionNm": shaft_friction,
        "maxGravityGroupsNm": float(np.abs(gravity_groups).max()), "maxGravityRestNm": float(np.abs(gravity_rest).max()),
        "maxContactFrictionNm": float(contact_friction.max()), "maxInertiaGroupsKgm2": float(i_group.max()),
        "maxDLiftDqMPerRad": float(np.abs(dz).max()), "minD2LiftMPerRad2": float(d2z.min()),
        "maxNormalForceN": float(normal.max()), "maxAxisTorqueNm": [float(v) for v in t0.max(axis=0)],
        "arrays": {"q": q_rows, "n3": n3, "e3": e3, "h3": h3, "k3": k3, "eta_inv": eta_inv, "t_cons": t_cons, "t_cam": t_cam,
                   "t_guide": t_guide, "bear_pix": bear_pix, "gravity_groups": gravity_groups, "gravity_rest": gravity_rest,
                   "contact_friction": contact_friction, "servo_friction": servo_friction, "mu_c": mu_c},
    }
    return tables, diag


def torque_breakdown(diag, limit, at_deg=None):
    """必要トルク（静的）が最大になるサーボ角で、何が効いているか。サーボ軸換算の mNm。上位の画素と、限界を超える角度の範囲も返す"""
    a = diag["arrays"]
    g = P.G_RATIO
    req = np.abs(a["gravity_groups"]) + np.abs(a["gravity_rest"]) + a["contact_friction"] + a["servo_friction"]
    k = int(req.argmax()) if at_deg is None else int(np.abs(a["q"] - at_deg).argmin())
    eta = a["eta_inv"]
    cam_ax = g * (a["t_cam"][k] * eta)                # 軸 j の足とカムの滑り
    guide_ax = g * (a["t_guide"][k] * eta)
    bear_ax = g * (a["bear_pix"][k] * eta)
    loss_ax = g * (a["t_cons"][k] * (eta - 1.0))      # 保持トルクにかかる歯車の損失
    pixels = []
    for j in range(N):
        for i in range(N):
            n, e, h, kap = a["n3"][k, j, i], a["e3"][k, j, i], a["h3"][k, j, i], a["k3"][k, j, i]
            cam = g * eta[j] * a["mu_c"] * n * h
            guide = g * eta[j] * kap * n * abs(e)
            loss = g * (eta[j] - 1.0) * abs(n * e)
            pixels.append({"i": i, "j": j, "camSlidingMNm": cam * 1e3, "guideMNm": guide * 1e3, "gearLossMNm": loss * 1e3,
                           "totalMNm": (cam + guide + loss) * 1e3, "kappa": float(kap), "normalN": float(n),
                           "heightMm": float(h * MM - RB_MM), "lateralMm": float(e * MM)})
    pixels.sort(key=lambda r: -r["totalMNm"])
    over = np.where(req > limit)[0]
    ranges = []
    if len(over):
        start = prev = over[0]
        for idx in over[1:]:
            if idx != prev + 1:
                ranges.append([float(a["q"][start]), float(a["q"][prev])])
                start = idx
            prev = idx
        ranges.append([float(a["q"][start]), float(a["q"][prev])])
    return {
        "worstServoDeg": float(a["q"][k]), "requiredMNm": float(req[k] * 1e3), "limitMNm": limit * 1e3, "overByMNm": float((req[k] - limit) * 1e3),
        "components": {"gravityGroupsMNm": float(abs(a["gravity_groups"][k]) * 1e3), "gravityRestMNm": float(abs(a["gravity_rest"][k]) * 1e3),
                       "camSlidingMNm": float(cam_ax.sum() * 1e3), "guideFrictionMNm": float(guide_ax.sum() * 1e3),
                       "bearingMNm": float(bear_ax.sum() * 1e3), "gearLossOnHoldMNm": float(loss_ax.sum() * 1e3),
                       "servoFixedFrictionMNm": float(a["servo_friction"] * 1e3)},
        "perAxisMNm": [float((cam_ax[j] + guide_ax[j] + bear_ax[j] + loss_ax[j]) * 1e3) for j in range(N)],
        "topPixels": [{kk: (rounded(vv) if isinstance(vv, float) else vv) for kk, vv in r.items()} for r in pixels[:8]],
        "anglesOverLimitDeg": ranges,
        "note": "画素ごとの値は足とカムの滑り・案内の摩擦・保持トルクにかかる歯車損失（軸受けは軸ごと）。重力の分は 'gravityGroupsMNm'。",
    }


# =============================================================================================
# シミュレーション（TableSim。並列に回す）
# =============================================================================================
_SIM = None


def _init_worker(tables):
    global _SIM
    _SIM = common.TableSim(tables)


def _run_job(job):
    name, args = job
    result = _SIM.run(**args)
    return name, args, result


def run_jobs(tables, jobs, workers=None):
    """jobs = [(name, kwargs)]。同じ表で並列に走らせて {name: (args, result)} を返す"""
    out = {}
    workers = min(len(jobs), workers or min(12, os.cpu_count() or 1))
    if workers <= 1:
        _init_worker(tables)
        for job in jobs:
            name, args, result = _run_job(job)
            out[name] = (args, result)
        return out
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(tables,)) as pool:
        for name, args, result in pool.map(_run_job, jobs):
            out[name] = (args, result)
    return out


NOLIFT_GRID_S = [round(0.05 * (3.0 / 0.05) ** (k / 15.0), 4) for k in range(16)]     # 0.05 .. 3.0 秒（等比）
NOLIFT_RESOLUTION_S = 0.005


def _nolift_ok(frm, to, duration):
    res = _SIM.run(from_deg=frm, to_deg=to, kind="ease", duration=duration)
    return (res["contactFeasible"] and abs(res["final"]["servoDeg"] - to) <= 1.0), res


def _min_nolift_job(job):
    """表 k0 -> k1 の quintic 移動で、画素が浮かず目標の 1 度以内に着く最短の所要時間（秒）。格子で全域を調べ、境目を二分探索"""
    k0, k1 = job
    frm, to = P.TABLE_THETA[k0], P.TABLE_THETA[k1]
    flags = [_nolift_ok(frm, to, d)[0] for d in NOLIFT_GRID_S]
    i = len(NOLIFT_GRID_S)
    while i > 0 and flags[i - 1]:
        i -= 1                                     # flags[i:] がすべて True になる最小の i（それより長い時間は全部浮かない）
    out = {"from": k0, "to": k1, "fromDeg": frm, "toDeg": to, "gridS": NOLIFT_GRID_S, "gridFeasible": flags,
           "monotonicAbove": True, "resolutionS": NOLIFT_RESOLUTION_S}
    if i == len(NOLIFT_GRID_S):
        out.update({"minS": None, "reason": f"{NOLIFT_GRID_S[-1]} 秒でも浮く、または届かない"})
        return job, out
    if i == 0:
        hi, lo = NOLIFT_GRID_S[0], 0.0
        out["boundBelowS"] = NOLIFT_GRID_S[0]       # 最短の格子点でも浮かない。これより短い時間は調べていない
    else:
        lo, hi = NOLIFT_GRID_S[i - 1], NOLIFT_GRID_S[i]
        while hi - lo > NOLIFT_RESOLUTION_S:
            mid = (lo + hi) / 2.0
            if _nolift_ok(frm, to, mid)[0]:
                hi = mid
            else:
                lo = mid
    ok, res = _nolift_ok(frm, to, hi)
    out.update({"minS": rounded(hi), "infeasibleBelowS": rounded(lo) if i else None, "minNormalForceN": res["minNormalForceN"],
                "finalErrorDeg": rounded(abs(res["final"]["servoDeg"] - to)), "feasibleAtMin": bool(ok)})
    return job, out


def run_pool(tables, func, jobs):
    workers = min(len(jobs), min(12, os.cpu_count() or 1))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(tables,)) as pool:
        return list(pool.map(func, jobs))


def min_no_lift_moves(tables):
    """隣り合う表（0-1, 1-2, 2-3, 3-4 の両方向）ごとの、浮かない最短の移動時間。firmware.py が読む `motion.minNoLiftMoveS`"""
    jobs = [(a, a + 1) for a in range(P.K - 1)] + [(a + 1, a) for a in range(P.K - 1)]
    rows = [out for _, out in run_pool(tables, _min_nolift_job, jobs)]
    values = [r["minS"] for r in rows]
    return {"criterion": "quintic の ease 移動で、全 25 画素の接触力 m(g + zdd) が全時刻で >= 0 かつ最終角が目標の 1 度以内（mu 0.35、質量倍率 1）",
            "profile": "quintic（3 t^2 ではなく 10 u^3 - 15 u^4 + 6 u^5）", "massScale": 1.0, "mu": P.MU_CAM,
            "byTransition": {f"{r['from']}to{r['to']}": r["minS"] for r in rows},
            "max": None if any(v is None for v in values) else max(values),
            "transitions": rows}


def summarize(args, result, tables):
    """軌跡を捨てて要約にする。画素の最大速度（mm/s）と、目標の ±1 度に入ってとどまる時刻"""
    trace = result["trace"]
    target = args["to_deg"]
    lifts = np.array([r["liftsMm"] for r in trace])
    times = np.array([r["t"] for r in trace])
    speed = np.abs(np.diff(lifts, axis=0)) / np.maximum(np.diff(times), 1e-12)[:, None]
    servo = np.array([r["servoDeg"] for r in trace])
    outside = np.where(np.abs(servo - target) > 1.0)[0]
    settle = None if len(outside) and outside[-1] == len(trace) - 1 else (float(times[outside[-1] + 1]) if len(outside) else 0.0)
    return {
        "fromDeg": args["from_deg"], "toDeg": target, "kind": args.get("kind", "ease"),
        "stallScale": args.get("stall_scale", 1.0), "massScale": args.get("mass_scale", 1.0),
        "durationS": args.get("duration", tables["duration_s"]),
        "finalServoDeg": result["final"]["servoDeg"], "finalErrorDeg": rounded(abs(result["final"]["servoDeg"] - target)),
        "reached": abs(result["final"]["servoDeg"] - target) <= 1.0,
        "settleTimeS": settle,
        "peakTorqueNm": result["peakTorqueNm"], "maxContactSpeedMmS": result["maxContactSpeedMmS"],
        "maxPixelSpeedMmS": rounded(float(speed.max())) if speed.size else 0.0,
        "contactFeasible": result["contactFeasible"], "minNormalForceN": result["minNormalForceN"],
        "possibleLiftOffGroups": result["possibleLiftOffGroups"], "finalLiftsMm": result["final"]["liftsMm"],
    }


def table_pairs():
    """5 つの表の全順序対（20 通り）"""
    return [(a, b) for a in range(P.K) for b in range(P.K) if a != b]


def make_jobs(tables, required, with_extra=True):
    lo, hi = P.SERVO_MIN_DEG, P.SERVO_MAX_DEG
    th = P.TABLE_THETA
    jobs = [("standard", dict(from_deg=lo, to_deg=hi, kind="ease")),
            ("reverse", dict(from_deg=hi, to_deg=lo, kind="ease"))]
    for src in STOP_RUN_SOURCES:
        for k in range(P.K):
            jobs.append((f"stop_{int(src)}_to_{k}", dict(from_deg=src, to_deg=th[k], kind="ease")))
    if with_extra:
        jobs += [("heavy", dict(from_deg=lo, to_deg=hi, kind="ease", mass_scale=4.0)),
                 ("fullSpeed", dict(from_deg=lo, to_deg=hi, kind="step")),
                 ("fullSpeedReverse", dict(from_deg=hi, to_deg=lo, kind="step")),
                 ("zeroTorque", dict(from_deg=lo, to_deg=hi, kind="ease", stall_scale=0.0)),
                 ("halfRequired", dict(from_deg=lo, to_deg=hi, kind="ease", stall_scale=min(1.0, 0.5 * required / SERVO_STALL))),
                 ("shortfall50", dict(from_deg=lo, to_deg=hi, kind="ease", stall_scale=1.0 / 50.0))]
        for a, b in table_pairs():
            jobs.append((f"pair_{a}_to_{b}", dict(from_deg=th[a], to_deg=th[b], kind="ease")))
        for a in range(P.K - 1):
            jobs.append((f"pairstep_{a}_to_{a + 1}", dict(from_deg=th[a], to_deg=th[a + 1], kind="step")))
            jobs.append((f"pairstep_{a + 1}_to_{a}", dict(from_deg=th[a + 1], to_deg=th[a], kind="step")))
    return jobs


def stop_height_errors(results, tables):
    """表の停止角へ向かった全走行で、最終姿勢の各画素の高さと表の差（mm）。(最大, 最悪の組)"""
    sim = common.TableSim(tables)
    worst, where = 0.0, None
    for src in STOP_RUN_SOURCES:
        for k in range(P.K):
            args, res = results[f"stop_{int(src)}_to_{k}"]
            lifts = sim.at(res["final"]["servoDeg"])["liftsMm"]
            for j in range(N):
                for i in range(N):
                    err = abs(lifts[j * N + i] - PT.TABLES[k][j][i])
                    if err > worst:
                        worst, where = err, {"from": src, "table": k, "i": i, "j": j, "servoDeg": res["final"]["servoDeg"],
                                              "heightMm": lifts[j * N + i], "tableMm": PT.TABLES[k][j][i]}
    return worst, where


def nominal_stop_errors(cams):
    """表の停止角ちょうどで、実カムの高さ h* と表の差の最大（mm）"""
    worst = 0.0
    for k in range(P.K):
        hh = M.pixel_heights_mm(cams, P.TABLE_THETA[k])
        for j in range(N):
            for i in range(N):
                worst = max(worst, abs(hh[j][i] - PT.TABLES[k][j][i]))
    return worst


def compare_dt(tables, standard):
    fine = copy.deepcopy(tables)
    fine["const"]["dtS"] /= 2.0
    result = common.TableSim(fine).run(from_deg=P.SERVO_MIN_DEG, to_deg=P.SERVO_MAX_DEG, kind="ease")
    if len(standard["trace"]) != len(result["trace"]):
        raise RuntimeError("dt と dt/2 の軌跡の長さが違う")
    diff = {
        "finalServoDeg": abs(standard["final"]["servoDeg"] - result["final"]["servoDeg"]),
        "maxTraceServoDeg": max(abs(a["servoDeg"] - b["servoDeg"]) for a, b in zip(standard["trace"], result["trace"])),
        "maxTraceTorqueNm": max(abs(a["torqueNm"] - b["torqueNm"]) for a, b in zip(standard["trace"], result["trace"])),
        "maxTraceLiftMm": max(abs(x - y) for a, b in zip(standard["trace"], result["trace"]) for x, y in zip(a["liftsMm"], b["liftsMm"])),
        "peakTorqueNm": abs(standard["peakTorqueNm"] - result["peakTorqueNm"]),
    }
    return {"dtS": tables["const"]["dtS"], "halfDtS": fine["const"]["dtS"],
            "observedAbsoluteDifference": {k: rounded(v) for k, v in diff.items()},
            "reportedUpperBound": {k: rounded(2.0 * v) for k, v in diff.items()},
            "basis": "同じ記録時刻で dt と dt/2 を比べる。差の 2 倍を保守上限とする。"}


DT_TOL = {"finalServoDeg": 0.05, "maxTraceServoDeg": 0.05, "maxTraceTorqueNm": 2.0e-3, "maxTraceLiftMm": 0.02, "peakTorqueNm": 2.0e-3}


def no_load_calibration(tables):
    """無負荷（画素質量 0、回転部の慣性・摩擦・重力もなし）で 60 度を公称 0.1 秒で動くか。回転部を残した場合も参考に出す"""
    t = copy.deepcopy(tables)
    t["const"]["servoFrictionNm"] = 0.0
    t["const"]["recordS"] = 0.001
    t["const"]["settleS"] = 0.1
    for row in t["rows"]:
        row["inertiaRestKgm2"] = row["inertiaGroupsKgm2"] = row["dMGroupsDqKgm2PerRad"] = 0.0
        row["gravityRestNm"] = row["gravityGroupsNm"] = row["contactFrictionGroupsNm"] = 0.0
        row["dLiftDqMPerRad"] = [0.0] * NP
        row["d2LiftDq2MPerRad2"] = [0.0] * NP

    def reach(tab):
        res = common.TableSim(tab).run(from_deg=P.SERVO_MIN_DEG, to_deg=P.SERVO_MIN_DEG + 60.0, kind="step", duration=0.2)
        return next((r["t"] for r in res["trace"] if r["servoDeg"] >= P.SERVO_MIN_DEG + 59.0), None)

    t_pure = reach(t)
    t2 = copy.deepcopy(t)
    for row, src in zip(t2["rows"], tables["rows"]):
        row["inertiaRestKgm2"] = src["inertiaRestKgm2"]
    t_rot = reach(t2)
    ok = t_pure is not None and abs(t_pure - 0.1) <= 0.02
    return {"id": "no-load-speed", "label": "無負荷の公称速度（画素質量 0）", "pass": bool(ok),
            "detail": {"nominalS": 0.1, "toleranceS": 0.02, "timeTo59DegS": t_pure, "withRotatingPartsS": t_rot,
                       "basis": "慣性・摩擦・重力をすべて 0 にし、60 度のステップ指令が公称 60 度 / 0.1 秒の速さで動くか"}}


def liftoff_detector_calibration(tables, standard_summary):
    """浮き上がり検出器の校正。加速度が重力を超える合成表（d2 = -100 m/rad2）で検出し、実際の表の標準走行では出さない"""
    t = copy.deepcopy(tables)
    for row in t["rows"]:
        row["d2LiftDq2MPerRad2"] = [-100.0] * NP
    res = common.TableSim(t).run(from_deg=P.SERVO_MIN_DEG, to_deg=P.SERVO_MAX_DEG, kind="ease")
    detected = (not res["contactFeasible"]) and (res["minNormalForceN"] is not None and res["minNormalForceN"] < 0)
    clean = standard_summary["contactFeasible"]
    return {"id": "liftoff-detector", "label": "浮き上がり検出器（出る側と出ない側）", "pass": bool(detected and clean),
            "detail": {"syntheticD2MPerRad2": -100.0, "syntheticDetected": detected, "syntheticMinNormalN": res["minNormalForceN"],
                       "realStandardContactFeasible": clean}}


def power_shortfall_calibration(summaries):
    std = summaries["standard"]
    s50, half, zero = summaries["shortfall50"], summaries["halfRequired"], summaries["zeroTorque"]
    ok = std["reached"] and not s50["reached"] and not half["reached"] and not zero["reached"]
    return {"id": "power-shortfall", "label": "力不足の負例（停動 1/50・必要量の半分・0）は届かない、通常は届く", "pass": bool(ok),
            "detail": {"standard": {"finalServoDeg": std["finalServoDeg"], "reached": std["reached"]},
                       "stall1over50": {"finalServoDeg": s50["finalServoDeg"], "reached": s50["reached"], "stallScale": s50["stallScale"]},
                       "halfRequired": {"finalServoDeg": half["finalServoDeg"], "reached": half["reached"], "stallScale": rounded(half["stallScale"])},
                       "zeroTorque": {"finalServoDeg": zero["finalServoDeg"], "reached": zero["reached"]},
                       "targetDeg": P.SERVO_MAX_DEG}}


def parity_with_js(tables, runs):
    """Python の軌跡を書き、test_sim_js.mjs（node）が viewer/lattice/sim.mjs の createSim で同じ表を流して全時刻を照合する"""
    reference = {"model": MODEL, "tablesSha256": digest(BUILD / "sim_tables.json"), "runs": []}
    for name, (args, result) in runs.items():
        reference["runs"].append({
            "name": name,
            "args": {"from": args["from_deg"], "to": args["to_deg"], "kind": args.get("kind", "ease"),
                     "stallScale": args.get("stall_scale", 1.0), "massScale": args.get("mass_scale", 1.0),
                     "duration": args.get("duration", tables["duration_s"])},
            "trace": result["trace"], "final": result["final"], "peakTorqueNm": result["peakTorqueNm"],
            "maxContactSpeedMmS": result["maxContactSpeedMmS"], "minNormalForceN": result["minNormalForceN"],
            "contactFeasible": result["contactFeasible"], "possibleLiftOffGroups": result["possibleLiftOffGroups"]})
    atomic_json(BUILD / "sim_js_reference.json", reference, indent=None)
    parity_path = BUILD / "sim_js_parity.json"
    if parity_path.exists():
        parity_path.unlink()
    proc = subprocess.run(["node", str(HERE / "test_sim_js.mjs")], capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))
    parity = json.loads(parity_path.read_text(encoding="utf-8")) if parity_path.is_file() else None
    ok = proc.returncode == 0 and parity is not None and parity.get("pass") is True
    return {"id": "python-js-parity", "label": "Python と JS（sim.mjs の createSim）で全時刻が一致", "pass": bool(ok),
            "detail": {"nodeExitCode": proc.returncode, "parity": parity,
                       "nodeStderrTail": proc.stderr.strip().splitlines()[-5:] if proc.returncode else []}}


# =============================================================================================
# 駆動形状（drive_report.json）
# =============================================================================================
def drive_state():
    path = BUILD / "drive_report.json"
    pending = {"geometryPass": False, "sourceHashesFresh": False, "pending": True,
               "reason": "build/drive_report.json が未生成。駆動形状の検査（別担当）が出るまで保留。", "staleSources": [],
               "driveReportSha256": None}
    if not path.is_file():
        return pending
    report = json.loads(path.read_text(encoding="utf-8"))
    stale = []
    recorded = report.get("sourceHashes", {})
    for relative, expected in recorded.items():
        lexical = Path(relative)
        if lexical.is_absolute() or ".." in lexical.parts:
            stale.append(relative)
            continue
        src = ROOT / lexical
        if not src.is_file() or digest(src) != expected:
            stale.append(relative)
    geometry_ok = report.get("overall", {}).get("geometryPass") is True
    fresh = bool(recorded) and not stale
    interfaces = report.get("interfaces", [])
    acceptable = bool(interfaces) and all(row.get("status") in {"pass", "unknown"} for row in interfaces)
    ok = report.get("model") == MODEL and geometry_ok and fresh and acceptable
    return {"geometryPass": ok, "sourceHashesFresh": fresh, "pending": False,
            "reason": "接続形状は確認済み。" if ok else "drive_report の geometryPass または source SHA が未成立。",
            "staleSources": stale, "driveReportSha256": digest(path)}


# =============================================================================================
# 本体
# =============================================================================================
def design_check_cross(kap35, kap45):
    path = BUILD / "design_check.json"
    if not path.is_file():
        return {"available": False}
    key = json.loads(path.read_text(encoding="utf-8"))["summary"]["key"]
    pairs = {"kappa_A_035": kap35["A"][0], "kappa_A_045": kap45["A"][0], "kappa_B_035": kap35["B"][0], "kappa_B_045": kap45["B"][0]}
    diff = {name: abs(key[name] - value) for name, value in pairs.items() if name in key}
    return {"available": True, "designCheckSha256": digest(path), "mine": pairs, "designCheck": {n: key.get(n) for n in pairs},
            "maxAbsDifference": max(diff.values()) if diff else None,
            "agrees": bool(diff) and max(diff.values()) < 1.0e-6,
            "torqueNote": {"designCheckTorque035mNm": key.get("torque_035_mNm"), "designCheckTorque045mNm": key.get("torque_045_mNm")}}


def scenario_set(tables, required, with_extra=True):
    jobs = make_jobs(tables, required, with_extra)
    raw = run_jobs(tables, jobs)
    return raw, {name: summarize(args, res, tables) for name, (args, res) in raw.items()}


def generate():
    cams = M.build_cams()
    props, stl_used, rejected, stl_files = load_mass_properties(cams)
    hashes = source_hashes(stl_files + [BUILD / "motion.json"] if (BUILD / "motion.json").is_file() else stl_files)
    mu_c, mu_g = P.MU_CAM, P.MU_GUIDE
    tables, diag = build_tables(cams, props, mu_c, mu_g, hashes)
    atomic_json(BUILD / "sim_tables.json", tables, indent=None)
    rows = tables["rows"]
    static_req = max(abs(r["gravityGroupsNm"]) + abs(r["gravityRestNm"]) + r["contactFrictionGroupsNm"] + tables["const"]["servoFrictionNm"] for r in rows)
    kap35, kap45 = kappa_grid(cams, mu_c, mu_g), kappa_grid(cams, P.MU_CAM_HI, P.MU_GUIDE_HI)

    raw, summ = scenario_set(tables, static_req)
    slow = [n for n in summ if n in ("standard", "reverse") or n.startswith("pair_") or n.startswith("stop_")]
    peak_slow = max(summ[n]["peakTorqueNm"] for n in slow)
    min_normal_slow = min(summ[n]["minNormalForceN"] for n in slow)
    contact_slow = all(summ[n]["contactFeasible"] for n in slow)
    stop_err, stop_where = stop_height_errors(raw, tables)
    nominal_err = nominal_stop_errors(cams)
    step_names = [n for n in summ if n.startswith("pairstep_")] + ["fullSpeed", "fullSpeedReverse"]
    fast = {n: summ[n] for n in step_names}
    pair_names = [n for n in summ if n.startswith("pair_")]

    # --- 感度: 摩擦 0.45（標準・逆・全停止角）-------------------------------------------------
    tables45, diag45 = build_tables(cams, props, P.MU_CAM_HI, P.MU_GUIDE_HI, hashes)
    breakdown45 = torque_breakdown(diag45, TORQUE_LIMIT)
    static45 = max(abs(r["gravityGroupsNm"]) + abs(r["gravityRestNm"]) + r["contactFrictionGroupsNm"] + tables45["const"]["servoFrictionNm"]
                   for r in tables45["rows"])
    raw45, summ45 = scenario_set(tables45, static45, with_extra=False)
    peak45 = max(s["peakTorqueNm"] for s in summ45.values())
    peak_run = max(raw45, key=lambda n: raw45[n][1]["peakTorqueNm"])
    peak_row = max(raw45[peak_run][1]["trace"], key=lambda r: abs(r["torqueNm"]))
    peak_info = {"run": peak_run, "peakTorqueNm": rounded(peak45), "atServoDeg": peak_row["servoDeg"], "atTimeS": peak_row["t"],
                 "staticRequiredAtThatAngleNm": rounded(float(np.abs(diag45["arrays"]["gravity_groups"][int(np.abs(diag45["arrays"]["q"] - peak_row["servoDeg"]).argmin())])
                                                              + np.abs(diag45["arrays"]["gravity_rest"][int(np.abs(diag45["arrays"]["q"] - peak_row["servoDeg"]).argmin())])
                                                              + diag45["arrays"]["contact_friction"][int(np.abs(diag45["arrays"]["q"] - peak_row["servoDeg"]).argmin())]
                                                              + diag45["arrays"]["servo_friction"])),
                 "breakdownAtPeakAngle": torque_breakdown(diag45, TORQUE_LIMIT, at_deg=peak_row["servoDeg"]),
                 "note": "走行中の最大トルクは静的な必要量に、サーボの位置制御の偏差（目標との差 x 制御帯）と加減速の分が乗る。"}
    stop45, _ = stop_height_errors(raw45, tables45)
    sens = {"mu": P.MU_CAM_HI, "staticRequiredNm": rounded(static45), "peakSlowTorqueNm": rounded(peak45),
            "torqueWithinOneThirdStall": max(static45, peak45) <= TORQUE_LIMIT,
            "contactFeasible": all(s["contactFeasible"] for s in summ45.values()),
            "minNormalForceN": min(s["minNormalForceN"] for s in summ45.values()),
            "stopHeightErrorMaxMm": rounded(stop45), "stopWithinTolerance": stop45 <= HEIGHT_TOL_MM,
            "kappaPlateOnlyMax": rounded(kap45["A"][0]), "kappaWindowMax": rounded(kap45["B"][0]),
            "kappaUsedInTablesMax": rounded(diag45["kappaMaxUsed"]), "maxContactFrictionNm": rounded(diag45["maxContactFrictionNm"]),
            "torqueBreakdown": breakdown45, "peakTorque": peak_info,
            "staticWithinOneThirdStall": static45 <= TORQUE_LIMIT, "peakWithinOneThirdStall": peak45 <= TORQUE_LIMIT}

    # --- 校正 -------------------------------------------------------------------------------
    min_no_lift = min_no_lift_moves(tables)
    dt = compare_dt(tables, raw["standard"][1])
    dt_ok = all(dt["observedAbsoluteDifference"][k] <= tol for k, tol in DT_TOL.items())
    calibration = [
        no_load_calibration(tables),
        power_shortfall_calibration(summ),
        {"id": "dt-halving", "label": "時間刻みを半分にしても結果が一致", "pass": bool(dt_ok),
         "detail": {**dt, "tolerance": DT_TOL}},
    ]
    parity_names = ("standard", "reverse", "fullSpeed", "heavy", "halfRequired", "pair_1_to_3", "pairstep_2_to_3", "stop_10_to_1")
    calibration.append(parity_with_js(tables, {n: raw[n] for n in parity_names}))
    calibration.append(liftoff_detector_calibration(tables, summ["standard"]))
    mass_cal = common.mass_calibration()
    calibration.append({"id": "signed-mass", "label": "符号付き四面体積分（既知の直方体）", "pass": bool(mass_cal["ok"]), "detail": mass_cal})
    cross = design_check_cross(kap35, kap45)

    # --- 判定 --------------------------------------------------------------------------------
    check_a = max(static_req, peak_slow) <= TORQUE_LIMIT
    check_b = contact_slow and min_normal_slow >= 0.0
    check_c = kap45["A"][0] < 1.0 and kap45["B"][0] < 1.0 and not diag45["kappaClipped"]
    check_d = stop_err <= HEIGHT_TOL_MM and nominal_err <= HEIGHT_TOL_MM
    cal_ok = all(row["pass"] for row in calibration)
    calculation = bool(check_a and check_b and check_c and check_d and cal_ok)
    drive = drive_state()

    std = summ["standard"]
    report = {
        "version": 1, "model": MODEL,
        "method": "SG92R torque-speed limited one-DOF Lagrange simulation（C1 と同じサーボ模型、TableSim / sim.mjs）",
        "equation": "M(q) qdd + 0.5 dM/dq qdot^2 + G(q) = servoTorque - servoFriction - sign(qdot) contactFriction",
        "limitsDeg": tables["limitsDeg"], "tableStepDeg": TABLE_STEP_DEG, "durationS": DURATION_S,
        "massIntegration": {
            "method": "build/<id>.stl があれば閉じた STL の符号付き四面体積分、無ければ params.py と cams.py の形からの見積もり",
            "densityKgM3": {"effective": EFFECTIVE_DENSITY, "pla": PLA_DENSITY, "fillFactor": FILL_FACTOR, "pp": PP_DENSITY},
            "densityBasis": "PLA 1.24 g/cm3 x 0.85。壁 2 周 + 上下 5 層 + 充填 15% のスライスで、肉厚 1.6〜4mm の小部品は外殻が主になり中実の 6〜10 割",
            "stlUsed": stl_used, "estimatedParts": [pid for pid in PIXEL_IDS + ROTATING_IDS if pid not in stl_used], "stlRejected": rejected, "stlCount": len(stl_used), "partCount": len(PIXEL_IDS) + len(ROTATING_IDS),
            "source": "stl" if len(stl_used) == len(PIXEL_IDS) + len(ROTATING_IDS) else ("estimate" if not stl_used else "mixed"),
            "pixelMassG": {"min": rounded(min(props[p]["massKg"] for p in PIXEL_IDS) * 1000.0),
                           "max": rounded(max(props[p]["massKg"] for p in PIXEL_IDS) * 1000.0)},
            "axisSetMassG": [rounded(sum(props[p]["massKg"] for p in ROTATING_IDS if M.axis_of_part(p) == j) * 1000.0) for j in range(N)],
            "servoSideMassG": rounded(sum(props[p]["massKg"] for p in ("horn_coupler", "sg92r_horn")) * 1000.0),
            "totals": {"pixelsG": rounded(sum(props[p]["massKg"] for p in PIXEL_IDS) * 1000.0),
                       "rotatingG": rounded(sum(props[p]["massKg"] for p in ROTATING_IDS) * 1000.0),
                       "movingTotalG": rounded(sum(props[p]["massKg"] for p in PIXEL_IDS + ROTATING_IDS) * 1000.0)},
            "inertia": {"restServoAxisKgm2": diag["inertiaRestKgm2"], "servoSideKgm2": diag["inertiaServoPartsKgm2"],
                        "axesOwnAxisKgm2": diag["inertiaAxesKgm2"], "gRatioSquared": P.G_RATIO ** 2,
                        "maxPixelsKgm2": diag["maxInertiaGroupsKgm2"], "motorKgm2": common.MOTOR_INERTIA},
            "calibration": mass_cal,
        },
        "calibration": calibration, "dynamicCalibration": common.dynamic_calibration(),
        "driveGeometry": drive,
        "overall": {"pass": False, "calculationPass": calculation, "status": "conditional" if calculation else "fail",
                    "geometryPass": drive["geometryPass"], "pending": drive["pending"],
                    "basis": (("計算内成立。駆動形状の検査（drive_report.json）は適合。" if drive["geometryPass"] else
                               "計算内成立。駆動形状の検査（drive_report.json）が揃うまで接続は未確認。")
                              + "スプライン嵌合・摩擦係数・材料は実機未確認。"
                              if calculation else "条件付き 1 自由度計算の成立条件を満たさない。"),
                    "calculationBasis": "必要トルク <= 停動の 1/3、全時刻で接触力 >= 0、全画素・全角度で kappa < 1（mu 0.45）、表の停止角で高さが表どおり（±0.05mm）、校正が全部通る",
                    "checks": {"a_torque": check_a, "b_contact": check_b, "c_kappa": check_c, "d_stopHeights": check_d, "calibration": cal_ok}},
        "checks": {
            "a_torque": {"pass": check_a, "limitNm": rounded(TORQUE_LIMIT), "staticRequiredNm": rounded(static_req),
                         "peakSlowTorqueNm": rounded(peak_slow), "maxNm": rounded(max(static_req, peak_slow)),
                         "marginNm": rounded(TORQUE_LIMIT - max(static_req, peak_slow)), "fractionOfStall": rounded(max(static_req, peak_slow) / SERVO_STALL),
                         "slowRuns": len(slow)},
            "b_contact": {"pass": check_b, "minNormalForceN": min_normal_slow, "slowRunsAllFeasible": contact_slow,
                          "pixelWeightN": rounded(min(props[p]["massKg"] for p in PIXEL_IDS) * GRAV),
                          "minNormalForceWithGuideFrictionN": rounded(min_normal_slow / (1.0 + kap35["A"][0])),
                          "note": "案内の摩擦を入れても接触力は m(g+zdd)/(1±kappa) で符号は m(g+zdd) と同じ。下限は 1/(1+kappa) 倍した値"},
            "c_kappa": {"pass": check_c, "mu": P.MU_CAM_HI, "plateOnlyMax": rounded(kap45["A"][0]), "windowMax": rounded(kap45["B"][0]),
                        "worstPlateOnly": kap45["A"][1], "tablesClipped": diag45["kappaClipped"],
                        "mu035": {"plateOnlyMax": rounded(kap35["A"][0]), "windowMax": rounded(kap35["B"][0])}},
            "d_stopHeights": {"pass": check_d, "toleranceMm": HEIGHT_TOL_MM, "simFinalErrorMaxMm": rounded(stop_err),
                              "worstSimFinal": stop_where, "nominalAtStopAngleErrorMaxMm": rounded(nominal_err),
                              "runs": len(STOP_RUN_SOURCES) * P.K},
        },
        "static": {"maxGravityGroupsNm": rounded(diag["maxGravityGroupsNm"]), "maxGravityRestNm": rounded(diag["maxGravityRestNm"]),
                   "maxContactFrictionNm": rounded(diag["maxContactFrictionNm"]), "servoFrictionNm": tables["const"]["servoFrictionNm"],
                   "maximumRequiredTorqueNm": rounded(static_req), "fractionOfStall": rounded(static_req / SERVO_STALL),
                   "withinOneThirdStall": static_req <= TORQUE_LIMIT, "peakLowSpeedTorqueNm": rounded(peak_slow),
                   "peakWithinOneThirdStall": peak_slow <= TORQUE_LIMIT, "maxNormalForceN": rounded(diag["maxNormalForceN"]),
                   "maxAxisTorqueNm": [rounded(v) for v in diag["maxAxisTorqueNm"]]},
        "motion": {"minNoLiftMoveS": min_no_lift, "standardMove": {k: std[k] for k in ("fromDeg", "toDeg", "durationS", "settleTimeS", "peakTorqueNm", "maxPixelSpeedMmS", "finalErrorDeg")},
                   "tablePairs": {"count": len(pair_names), "durationS": DURATION_S,
                                  "peakTorqueNmMax": rounded(max(summ[n]["peakTorqueNm"] for n in pair_names)),
                                  "maxPixelSpeedMmS": rounded(max(summ[n]["maxPixelSpeedMmS"] for n in pair_names)),
                                  "allReached": all(summ[n]["reached"] for n in pair_names),
                                  "allContactFeasible": all(summ[n]["contactFeasible"] for n in pair_names)},
                   "fastestTableToTable": {n: {k: s[k] for k in ("settleTimeS", "maxPixelSpeedMmS", "peakTorqueNm", "contactFeasible",
                                                                    "minNormalForceN", "possibleLiftOffGroups", "reached", "finalErrorDeg")}
                                          for n, s in fast.items()},
                   "fastestSummary": {"settleTimeSMax": (None if any(s["settleTimeS"] is None for s in fast.values())
                                                         else rounded(max(s["settleTimeS"] for s in fast.values()))),
                                      "maxPixelSpeedMmS": rounded(max(s["maxPixelSpeedMmS"] for s in fast.values())),
                                      "liftOffRuns": [n for n, s in fast.items() if not s["contactFeasible"]]}},
        "kappa": {"tablesModel": "plate_only", "mu035": {"A": kap35["A"], "B": kap35["B"]}, "mu045": {"A": kap45["A"], "B": kap45["B"]},
                  "designCheckCrossCheck": cross},
        "sensitivity": sens,
        "integrationConvergence": dt,
        "scenarios": summ,
        "stopRuns": {n: summ[n] for n in summ if n.startswith("stop_")},
        "assumptions": tables["const"]["assumptions"], "sourceHashes": hashes,
        "algorithmHashes": {"models/tangible-pixel-cube/simulate.py": digest(HERE / "simulate.py"),
                            "tools/lattice_simulation.py": digest(ROOT / "tools/lattice_simulation.py"),
                            "viewer/lattice/sim.mjs": digest(ROOT / "viewer/lattice/sim.mjs")},
        "findings": [
            "2026-10-12 に design_check.py の F トルクが t2 / (g * eta) で g^2 小さく出ていたのを見つけた。t2 * g / eta に直した（増速で軸が g 倍速く回るため）。"
            "この計算は仕事の保存（dz/dq = e g）で g を掛けている。",
        ],
        "limitations": [
            "摩擦係数 0.35 / 0.45（足とカム・案内）は未実測の仮値。軸受け 0.35・歯車 1 噛合 0.9 も仮値。",
            f"STL が無い部品は params と cams の形からの見積もり（{len(stl_used)}/{len(PIXEL_IDS) + len(ROTATING_IDS)} 部品が STL）。",
            "付属ホーンのスプライン嵌合と材料特性は実機未確認。歯車の位相・バックラッシュは駆動形状の検査（別担当）が決める。",
            "カムは 0.5 度刻みの凸多角形。多角形の頂点で接点が飛ぶ衝撃は d2 を 0.25 度で平滑化しており、実メッシュの動的衝突は別検査。",
            "最速（ステップ指令）の走行は加速度が大きく、画素が浮く場合がある。これは判定に入れていない（通常の動かし方は 3 秒の quintic）。",
        ],
    }
    atomic_json(BUILD / "simulate_report.json", report)
    return {"model": MODEL, "calculationPass": calculation,
            "a_maxTorqueNm": rounded(max(static_req, peak_slow)), "a_limitNm": rounded(TORQUE_LIMIT),
            "b_minNormalN": min_normal_slow, "c_kappa045": rounded(kap45["A"][0]), "d_stopErrMm": rounded(stop_err),
            "calibration": {row["id"]: row["pass"] for row in calibration}, "mass": report["massIntegration"]["source"]}


def main():
    argparse.ArgumentParser().parse_args()
    result = generate()
    print(json.dumps(result, ensure_ascii=False))
    if not result["calculationPass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
