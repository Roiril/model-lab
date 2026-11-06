"""スマホ板ロボットの歩き方を MuJoCo で比べる（py -3.10。mujoco は 3.10 側にだけ入っている）。

形（中央板と脚の長さの差 clearance）ごとに、腰 2 軸の波形を乱択＋局所探索で探し、
「転ばずに進めた距離」を比べる。結果は build/gait_search.json。

サーボの式は mycobot-lab/.claude/memory/so101_servo_physics.md の STS3215 12V の値:
  τ = 2.94 N·m × clip(誤差 / 22°, ±1) − 0.58 N·m·s/rad × 角速度
実機の測定ではないので、数字は形どうしを比べるために使う。絶対値を信じない。
"""
import argparse
import json
import math
import os
from multiprocessing import Pool
from pathlib import Path

import mujoco
import numpy as np

HERE = Path(__file__).parent
STALL_NM = 2.94
DUTY_FULL_DEG = 22.0
BACK_EMF = 0.58
ARMATURE = 0.028
FALL_DEG = 40.0
DT = 0.002

# 形の既定（mm・g）。build の params.py と別に持つのは、ここが探索の出発点だから。結論は params.py へ写す
GEOM = dict(
    hip_mm=234.9,        # 腰の軸から脚の足裏まで
    body_w=90.2, body_d=34.0,
    leg_w=26.0, leg_gap=0.6,
    foot_d=60.0,         # 足裏の前後の長さ
    foot_r=3000.0,        # 足裏の円弧の半径
    body_print_g=210.0, servos_g=110.0, board_g=25.0, battery_g=45.0, phone_g=194.0,
    leg_g=73.0,
)


def arc_spheres(chord, radius, n=7):
    half = chord / 2
    sag_max = radius - math.sqrt(max(radius ** 2 - half ** 2, 0.0))
    out = []
    for i in range(n):
        y = -half + chord * i / (n - 1)
        z = (radius - math.sqrt(max(radius ** 2 - y ** 2, 0.0)))  # 足裏の中央が最も低い
        out.append((y, z, sag_max))
    return out


def foot_geoms(x0, x1, chord, radius, bottom_z, friction):
    """足裏を、両端の列に小球を並べた円弧で表す（平面との接触が安定する）"""
    xml = []
    for x in (x0, x1):
        for y, z, _ in arc_spheres(chord, radius):
            xml.append(f'<geom type="sphere" size="0.003" pos="{x/1000:.4f} {y/1000:.4f} {(bottom_z + z + 3)/1000:.4f}" '
                       f'friction="{friction} 0.005 0.0001" contype="1" conaffinity="1" mass="0"/>')
    return "\n".join(xml)


def build_xml(clearance_mm, geom, phone_g=None, friction_body=0.5, friction_leg=0.5):
    g = dict(geom)
    if phone_g is not None:
        g["phone_g"] = phone_g
    L = g["hip_mm"]
    Lb = L - clearance_mm
    # 中央板: 腰の軸を原点に下へ伸びる。質量は箇所ごとに置く
    servo_z, phone_z = -20.0, -(38 + 76)
    board_z, batt_z = -(38 + 60), -(38 + 130)
    body_masses = [
        (g["body_print_g"], -Lb / 2, (g["body_w"] / 2, g["body_d"] / 2, Lb / 2)),
        (g["servos_g"], servo_z, (39, 12, 22)),
        (g["phone_g"], phone_z, (36, 5, 76)),
        (g["board_g"], board_z, (26, 8, 34)),
        (g["battery_g"], batt_z, (15, 10, 28)),
    ]
    geoms = []
    for mass, z, half in body_masses:
        geoms.append(f'<geom type="box" size="{half[0]/1000:.4f} {half[1]/1000:.4f} {half[2]/1000:.4f}" '
                     f'pos="0 0 {z/1000:.4f}" mass="{mass/1000:.4f}" contype="0" conaffinity="0"/>')
    body_foot = foot_geoms(-g["body_w"] / 2 + 6, g["body_w"] / 2 - 6, g["foot_d"], g["foot_r"], -Lb, friction_body)
    leg_x = g["body_w"] / 2 + g["leg_gap"] + g["leg_w"] / 2
    legs = []
    for side, sign in (("L", -1), ("R", 1)):
        x = sign * leg_x
        legs.append(f'''
    <body name="leg{side}" pos="0 0 0">
      <joint name="hip{side}" type="hinge" axis="1 0 0" armature="{ARMATURE}" damping="0.0" frictionloss="0.052"/>
      <geom type="box" size="{g['leg_w']/2000:.4f} {g['body_d']/2000:.4f} {L/2000:.4f}" pos="{x/1000:.4f} 0 {-L/2000:.4f}"
            mass="{g['leg_g']/1000:.4f}" contype="0" conaffinity="0"/>
      {foot_geoms(x - g['leg_w']/2 + 2, x + g['leg_w']/2 - 2, g['foot_d'], g['foot_r'], -L, friction_leg)}
    </body>''')
    return f'''<mujoco>
  <size memory="2M"/>
  <option timestep="{DT}" gravity="0 0 -9.81" integrator="implicitfast" cone="elliptic"/>
  <worldbody>
    <geom name="floor" type="plane" size="5 5 0.1" friction="0.1 0.005 0.0001" contype="1" conaffinity="1"/>
    <body name="body" pos="0 0 {L/1000 + 0.002:.4f}">
      <freejoint/>
      {"".join(geoms)}
      {body_foot}
      {"".join(legs)}
    </body>
  </worldbody>
  <actuator>
    <motor name="mL" joint="hipL" gear="1" ctrlrange="-3 3"/>
    <motor name="mR" joint="hipR" gear="1" ctrlrange="-3 3"/>
  </actuator>
</mujoco>'''


def wave(params, t):
    """1 周期を 4 点の角度でつなぐ（滑らかに補間）。戻り値は左右の角度 [deg]"""
    period = params["period"]
    knots = params["knots"]            # 4 点の角度
    times = np.cumsum([0.0] + list(params["durs"]))
    times = times / times[-1]

    def at(phase):
        phase = phase % 1.0
        i = int(np.searchsorted(times, phase, side="right") - 1)
        i = min(i, len(knots) - 1)
        a, b = knots[i], knots[(i + 1) % len(knots)]
        u = (phase - times[i]) / max(times[i + 1] - times[i], 1e-6)
        u = u * u * (3 - 2 * u)
        return a + (b - a) * u

    ph = t / period
    return at(ph), at(ph + params["phase"])


KEYS = 24


def firmware_keys(params):
    """1 周期を等間隔に切り、1° 単位に丸める。ファームが持つ表そのもの"""
    period = params["period"]
    ms = int(round(period * 1000 / KEYS))
    return [(*[int(round(v)) for v in wave(params, (i + 1) * period / KEYS)], ms) for i in range(KEYS)]


def keyed_wave(keys, sign=1.0, skew_s=0.0):
    """ファームと同じ動き。1 キーごとに次の角度へ等速で向かう。skew_s は右の遅れ"""
    total = sum(k[2] for k in keys) / 1000.0
    n = len(keys)

    def at(t, column):
        phase = (t % total) / total * n
        i = int(phase) % n
        u = phase - int(phase)
        return sign * (keys[i - 1][column] + (keys[i][column] - keys[i - 1][column]) * u)

    return lambda t: (at(t, 0), at(t - skew_s, 1))


def rollout(clearance_mm, params, geom=GEOM, seconds=10.0, phone_g=None, friction=0.5, turn=0.0, record=False, yaw_kp=0.0,
            wave_fn=None, zero_err=(0.0, 0.0)):
    model = mujoco.MjModel.from_xml_string(build_xml(clearance_mm, geom, phone_g, friction, friction))
    data = mujoco.MjData(model)
    body = model.body("body").id
    ql, qr = model.joint("hipL").qposadr[0], model.joint("hipR").qposadr[0]
    dl, dr = model.joint("hipL").dofadr[0], model.joint("hipR").dofadr[0]
    # 落ち着くまで 0.5 秒
    tmax = int(seconds / DT)
    settle = int(0.5 / DT)
    fall = None
    yaw0 = None
    rec = []
    start = None
    peak_tau = 0.0
    tilt_max = 0.0
    work = 0.0
    for k in range(tmax + settle):
        t = (k - settle) * DT
        if k < settle:
            tl, tr = 0.0, 0.0
        else:
            ramp = min(t / 0.5, 1.0)
            tl, tr = wave_fn(t) if wave_fn else wave(params, t)
            steer = turn
            if yaw_kp and yaw0 is not None:
                # スマホのジャイロで向きを見て、脚の中心を左右へずらす想定（±8° まで）
                yaw_now = math.degrees(math.atan2(data.xmat[body][3], data.xmat[body][0]) - yaw0)
                yaw_now = (yaw_now + 180) % 360 - 180
                steer += float(np.clip(-yaw_kp * yaw_now, -8.0, 8.0))
            tl, tr = ramp * (tl + steer), ramp * (tr - steer)
        # zero_err: 組むときに脚のゼロがずれた分（指令は同じで、実際の脚がずれる）
        el = tl + zero_err[0] - math.degrees(data.qpos[ql])
        er = tr + zero_err[1] - math.degrees(data.qpos[qr])
        ul = STALL_NM * np.clip(el / DUTY_FULL_DEG, -1, 1) - BACK_EMF * data.qvel[dl]
        ur = STALL_NM * np.clip(er / DUTY_FULL_DEG, -1, 1) - BACK_EMF * data.qvel[dr]
        data.ctrl[0], data.ctrl[1] = ul, ur
        peak_tau = max(peak_tau, abs(ul), abs(ur))
        work += (abs(ul * data.qvel[dl]) + abs(ur * data.qvel[dr])) * DT
        mujoco.mj_step(model, data)
        if k == settle:
            start = data.xpos[body].copy()
            yaw0 = math.atan2(data.xmat[body][3], data.xmat[body][0])
        up = data.xmat[body].reshape(3, 3)[2, 2]
        tilt = math.degrees(math.acos(min(1.0, max(-1.0, up))))
        tilt_max = max(tilt_max, tilt)
        if tilt > FALL_DEG and fall is None:
            fall = t
            break
        if record and k % 10 == 0:
            rec.append([round(t, 3), *[round(float(v), 4) for v in data.xpos[body]], round(tilt, 2),
                        round(math.degrees(data.qpos[ql]), 2), round(math.degrees(data.qpos[qr]), 2)])
    delta = data.xpos[body] - start if start is not None else np.zeros(3)
    yaw = math.degrees(math.atan2(data.xmat[body][3], data.xmat[body][0]) - yaw0) if start is not None else 0.0
    yaw = (yaw + 180) % 360 - 180
    out = dict(forward_mm=float(delta[1] * 1000), lateral_mm=float(delta[0] * 1000), yaw_deg=yaw, fell_at=fall,
               peak_tau=float(peak_tau), tilt_max=float(tilt_max), work_j=float(work))
    if record:
        out["trace"] = rec
    return out


def score(result):
    base = abs(result["forward_mm"]) - 0.5 * abs(result["lateral_mm"])
    if result["fell_at"] is not None:
        base = min(base, 0) - 500 + 20 * result["fell_at"]
    return base


def random_params(rng):
    a = rng.uniform(3, 30)
    bias = rng.uniform(-10, 10)
    return dict(period=float(rng.uniform(0.5, 3.0)),
                knots=[float(bias + a * s) for s in (1, rng.uniform(-1, 1), -1, rng.uniform(-1, 1))],
                durs=[float(v) for v in rng.uniform(0.1, 1.0, 4)],
                phase=float(rng.choice([0.0, 0.5])))


def mutate(p, rng, scale):
    q = json.loads(json.dumps(p))
    q["period"] = float(np.clip(q["period"] * math.exp(rng.normal(0, 0.15 * scale)), 0.4, 4.0))
    q["knots"] = [float(np.clip(v + rng.normal(0, 4 * scale), -45, 45)) for v in q["knots"]]
    q["durs"] = [float(np.clip(v * math.exp(rng.normal(0, 0.25 * scale)), 0.05, 2.0)) for v in q["durs"]]
    if rng.random() < 0.05:
        q["phase"] = 0.5 - q["phase"]
    return q


def robust(clearance, params):
    """スマホの重さと摩擦を振っても転ばないか。最悪の値を返す"""
    rows = []
    for phone in (170.0, 194.0, 240.0):
        for fr in (0.35, 0.5, 0.8):
            rows.append(rollout(clearance, params, phone_g=phone, friction=fr, seconds=10.0))
    ok = [r for r in rows if r["fell_at"] is None]
    return dict(survived=len(ok), of=len(rows),
                min_forward=min((abs(r["forward_mm"]) for r in rows), default=0.0),
                mean_forward=float(np.mean([abs(r["forward_mm"]) for r in rows])), rows=rows)


def straight_score(clearance, params):
    """組立誤差 ±1.5mm、スマホの重さ、摩擦を振り、ジャイロで向きを直しながら 12 秒まっすぐ歩けるか"""
    total, signed = [], []
    for dc, phone, fr in ((-1.5, 170.0, 0.8), (0.0, 194.0, 0.5), (1.5, 240.0, 0.35), (1.5, 170.0, 0.5), (-1.5, 240.0, 0.5)):
        r = rollout(clearance + dc, params, seconds=12.0, phone_g=phone, friction=fr, yaw_kp=0.3)
        if r["fell_at"] is not None:
            total.append(-1000.0 + 10 * r["fell_at"])
        else:
            total.append(-0.3 * abs(r["lateral_mm"]) - 3.0 * abs(r["yaw_deg"]) - 30 * max(r["tilt_max"] - 15.0, 0.0))
        signed.append(r["forward_mm"])
    same = min(signed) if np.mean(signed) > 0 else -max(signed)
    return float(np.mean(total) + 2 * max(same, 0.0))


def turn_score(clearance, params):
    """その場で回る。向きの変化が大きく、位置が動かず、転ばないものを選ぶ"""
    total, signed = [], []
    for dc, phone, fr in ((-1.5, 170.0, 0.8), (0.0, 194.0, 0.5), (1.5, 240.0, 0.35)):
        r = rollout(clearance + dc, params, seconds=8.0, phone_g=phone, friction=fr)
        if r["fell_at"] is not None:
            total.append(-1000.0 + 10 * r["fell_at"])
        else:
            total.append(-0.2 * math.hypot(r["forward_mm"], r["lateral_mm"]) - 30 * max(r["tilt_max"] - 15.0, 0.0))
        signed.append(r["yaw_deg"])
    same = min(signed) if np.mean(signed) > 0 else -max(signed)
    return float(np.mean(total) + 3 * max(same, 0.0))


def search_final(args):
    mode, clearance, seed, n = args
    rng = np.random.default_rng(seed)
    best, best_score = None, -1e9
    fn = straight_score if mode == "walk" else turn_score
    phase = 0.5 if mode == "walk" else None
    for i in range(n):
        p = random_params(rng) if (best is None or i < n // 3) else mutate(best, rng, 1.0 - 0.7 * (i / n))
        if phase is not None:
            p["phase"] = phase
        else:
            p["phase"] = float(rng.uniform(0.0, 1.0)) if i < n // 3 else float((p["phase"] + rng.normal(0, 0.05)) % 1.0)
        s = fn(clearance, p)
        if s > best_score:
            best, best_score = p, s
    return dict(mode=mode, clearance=clearance, seed=seed, score=best_score, params=best)


def robust_score(clearance, params):
    """スマホの重さと摩擦の端で 12 秒。評価時間の直後に倒れる波形を選ばないよう、傾きも罰する"""
    total = []
    signed = []
    for phone, fr in ((170.0, 0.8), (194.0, 0.5), (240.0, 0.35)):
        r = rollout(clearance, params, seconds=12.0, phone_g=phone, friction=fr)
        if r["fell_at"] is not None:
            total.append(-1000.0 + 10 * r["fell_at"])
        else:
            total.append(-0.5 * abs(r["lateral_mm"]) - 30 * max(r["tilt_max"] - 15.0, 0.0))
        signed.append(r["forward_mm"])
    # 3 条件で同じ向きに進んだ分だけ数える
    same = min(signed) if np.mean(signed) > 0 else -max(signed)
    return float(np.mean(total) + max(same, 0.0))


# 隙間・重さ・摩擦・組み付けのずれ・左右の遅れ。すべて平らな足とジャイロ補正つきで見る
CONDITIONS = [
    dict(name="基準", clearance=3.0, phone_g=194.0, friction=0.5),
    dict(name="隙間 1.5mm", clearance=1.5, phone_g=194.0, friction=0.5),
    dict(name="隙間 4.5mm", clearance=4.5, phone_g=194.0, friction=0.5),
    dict(name="軽くて滑る", clearance=3.0, phone_g=174.0, friction=0.35),
    dict(name="重くて滑らない", clearance=3.0, phone_g=230.0, friction=0.8),
    dict(name="脚のゼロ 左+3 右-3", clearance=3.0, phone_g=194.0, friction=0.5, zero_err=(3.0, -3.0)),
    dict(name="脚のゼロ 左-3 右+3", clearance=3.0, phone_g=194.0, friction=0.5, zero_err=(-3.0, 3.0)),
    dict(name="右が 40ms 遅れる", clearance=3.0, phone_g=194.0, friction=0.5, skew_s=0.04),
    # ジャイロが使えなくても、曲げても転ばないこと
    dict(name="ジャイロなし", clearance=3.0, phone_g=194.0, friction=0.5, yaw_kp=0.0),
    dict(name="左へ曲げる（+6°）", clearance=3.0, phone_g=194.0, friction=0.5, yaw_kp=0.0, turn=6.0),
    dict(name="右へ曲げる（-6°）", clearance=3.0, phone_g=194.0, friction=0.5, yaw_kp=0.0, turn=-6.0),
]


def run_condition(keys, cond, seconds=12.0, sign=1.0):
    return rollout(cond["clearance"], None, seconds=seconds, phone_g=cond["phone_g"], friction=cond["friction"],
                   wave_fn=keyed_wave(keys, sign, cond.get("skew_s", 0.0)), zero_err=cond.get("zero_err", (0.0, 0.0)),
                   yaw_kp=cond.get("yaw_kp", 1.0), turn=cond.get("turn", 0.0))


def firmware_score(params):
    """ファームの表で全条件を流す。転ばない条件の数を最優先し、次に一番進まない条件の距離を見る"""
    keys = firmware_keys(params)
    base = run_condition(keys, CONDITIONS[0])
    if base["fell_at"] is not None:
        return -2000.0 + base["fell_at"]
    sign = 1.0 if base["forward_mm"] >= 0 else -1.0
    survived, worst, tilt = 1, sign * base["forward_mm"], base["tilt_max"]
    for cond in CONDITIONS[1:]:
        r = run_condition(keys, cond)
        if r["fell_at"] is None:
            survived += 1
            # 曲げている条件は距離を問わない（転ばないことだけ見る）
            if "turn" not in cond:
                worst = min(worst, sign * r["forward_mm"])
            tilt = max(tilt, r["tilt_max"])
    return float(1000.0 * survived + min(worst, 900.0) - 20.0 * max(tilt - 15.0, 0.0))


def search_firmware(args):
    seed, n = args
    rng = np.random.default_rng(seed)
    best, best_score = None, -1e9
    for i in range(n):
        p = random_params(rng) if (best is None or i < n // 3) else mutate(best, rng, 1.0 - 0.7 * (i / n))
        p["phase"] = 0.5
        p["knots"] = [float(np.clip(v, -36.0, 36.0)) for v in p["knots"]]
        s = firmware_score(p)
        if s > best_score:
            best, best_score = p, s
    return dict(seed=seed, score=best_score, params=best)


def search(args):
    clearance, phase_fixed, seed, n = args
    rng = np.random.default_rng(seed)
    best, best_score = None, -1e9
    for i in range(n):
        if best is None or i < n // 3:
            p = random_params(rng)
        else:
            p = mutate(best, rng, 1.0 - 0.7 * (i / n))
        if phase_fixed is not None:
            p["phase"] = phase_fixed
        s = robust_score(clearance, p)
        if s > best_score:
            best, best_score = p, s
    return dict(clearance=clearance, phase=phase_fixed, seed=seed, score=best_score, params=best)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--final", action="store_true", help="平らな足で、歩きと旋回の波形を決める")
    ap.add_argument("--firmware", action="store_true", help="ファームの表の形で、ばらつきに強い歩き方を探す")
    args = ap.parse_args()
    if args.firmware:
        with Pool(args.workers) as pool:
            res = pool.map(search_firmware, [(seed * 41 + 7, args.n) for seed in range(args.seeds)], chunksize=1)
        res.sort(key=lambda r: -r["score"])
        for r in res:
            print(round(r["score"]), r["seed"], {a: (round(b, 2) if isinstance(b, float) else [round(x, 1) for x in b]) for a, b in r["params"].items()})
        (HERE / "build").mkdir(exist_ok=True)
        (HERE / "build" / "gait_firmware.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        return
    if args.final:
        jobs = [("walk", 3.0, seed * 37 + 11, args.n) for seed in range(args.seeds)]
        with Pool(args.workers) as pool:
            res = pool.map(search_final, jobs, chunksize=1)
        best = {}
        for r in res:
            key = f"{r['mode']}_{r['clearance']}"
            if key not in best or r["score"] > best[key]["score"]:
                best[key] = r
        for k, r in sorted(best.items()):
            print(k, round(r["score"]), {a: (round(b, 2) if isinstance(b, float) else [round(x, 1) for x in b]) for a, b in r["params"].items()})
        (HERE / "build").mkdir(exist_ok=True)
        (HERE / "build" / "gait_final.json").write_text(json.dumps(best, ensure_ascii=False, indent=1), encoding="utf-8")
        return
    # 校正: 無指令なら進まず転ばない。立てない形（中央板より脚が短い形を片足で）で転ぶことも見る
    still = dict(period=1.0, knots=[0, 0, 0, 0], durs=[1, 1, 1, 1], phase=0.0)
    cal_stand = rollout(0.0, still, seconds=5.0)
    cal_kick = rollout(0.0, dict(period=0.6, knots=[45, -45, 45, -45], durs=[1, 1, 1, 1], phase=0.0), seconds=5.0)
    print("校正 無指令:", {k: round(cal_stand[k], 2) if cal_stand[k] is not None else None for k in ("forward_mm", "tilt_max", "fell_at")})
    print("校正 大振幅:", {k: round(cal_kick[k], 2) if cal_kick[k] is not None else None for k in ("forward_mm", "tilt_max", "fell_at")})
    jobs = []
    # clearance: 中央板が脚より何 mm 短いか。200 は依頼の「左右の足だけ」に近い形（中央は地面に届かない）
    for clearance in (0.0, 4.0, 8.0, 15.0, 200.0):
        for phase in (0.0, 0.5):
            for seed in range(args.seeds):
                jobs.append((clearance, phase, seed + int(clearance) * 100, args.n))
    with Pool(args.workers) as pool:
        results = pool.map(search, jobs, chunksize=1)
    table = {}
    for r in results:
        key = (r["clearance"], r["phase"])
        if key not in table or r["score"] > table[key]["score"]:
            table[key] = r
    rows = []
    for key in sorted(table):
        r = table[key]
        rob = robust(key[0], r["params"])
        one = rollout(key[0], r["params"], seconds=10.0)
        rows.append(dict(clearance=key[0], phase=key[1], score=r["score"], params=r["params"], nominal=one,
                         survived=rob["survived"], of=rob["of"], min_forward=rob["min_forward"], mean_forward=rob["mean_forward"]))
        print(f"差 {key[0]:5.0f}mm 位相 {key[1]:.1f}: 10 秒 {one['forward_mm']:7.0f}mm 横 {one['lateral_mm']:6.0f} 旋回 {one['yaw_deg']:6.1f}° "
              f"転倒 {one['fell_at']} 傾き {one['tilt_max']:4.1f}° 振り {rob['survived']}/{rob['of']} 最低 {rob['min_forward']:.0f}mm 周期 {r['params']['period']:.2f}s")
    out = HERE / "build" / "gait_search.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(calibration=dict(still=cal_stand, kick=cal_kick), rows=rows), ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
