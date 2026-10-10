"""蓋の開閉の物理検証（1 自由度の運動方程式。Blender 不要）。

    py -3.11 models/mystery-box-sg92r-d1/simulate.py

一般化座標はサーボ角 α。蓋・リンク・クランク・ホーンの質量と慣性は verify.py が STL から出した値
（中実 PLA。実物は充填率ぶん軽いので、ここでの必要トルクは上限側）を使う。
サーボは「トルク上限つき位置制御」で表す: τ = τ_stall · clamp((α_cmd − α)/帯, ±1) − (τ_stall/ω0)·α̇
（逆起電力の分だけ速いほど出せるトルクが減る。ω0 は無負荷速度 60°/0.1s）。
蓋が縁に当たるところは硬いばね＋減衰。蝶番と各ピンの摩擦はクーロン摩擦で入れる。
計器の校正として、(1) 負荷なしで公称速度が出るか、(2) トルクを静的必要量の半分にすると開かないか、を先に流す。
"""
import json
import math
import os
import sys

HERE = str(MODEL_HERE)
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import linkage as K  # noqa: E402
import params as P  # noqa: E402

G = 9.80665
RHO = P.PLA_DENSITY
REP = json.load(open(os.path.join(HERE, "build", "verify_report.json"), encoding="utf-8"))
MASS = REP["mass"]


def kg(part):
    return MASS[part]["volume_mm3"] * 1e-9 * RHO


def ixx_com(part):
    return MASS[part]["ixx_com_mm5"] * 1e-15 * RHO


# --- 質量特性（m, kg·m²）---------------------------------------------------
H = (K.H[0] / 1000, K.H[1] / 1000)
O = (K.O[0] / 1000, K.O[1] / 1000)
LID_M = kg("lid")
LID_COM0 = (MASS["lid"]["com_mm"][1] / 1000, MASS["lid"]["com_mm"][2] / 1000)
LID_I_H = ixx_com("lid") + LID_M * ((LID_COM0[0] - H[0]) ** 2 + (LID_COM0[1] - H[1]) ** 2)
LINK_M = kg("link")
LINK_COM0 = (MASS["link"]["com_mm"][1] / 1000, MASS["link"]["com_mm"][2] / 1000)
LINK_I = ixx_com("link")
CRANK_M = kg("crank")
CRANK_COM0 = (MASS["crank"]["com_mm"][1] / 1000, MASS["crank"]["com_mm"][2] / 1000)
CRANK_I_O = ixx_com("crank") + CRANK_M * ((CRANK_COM0[0] - O[0]) ** 2 + (CRANK_COM0[1] - O[1]) ** 2)
HORN_I_O = 0.9 * 1e3 * 369.6e-9 * (0.012 ** 2) / 3          # PP ホーン ≈0.33g、半径 12mm の棒で近似
ROTOR_I = 5.0e-6                                             # モーター回転子の出力軸換算（推定・小さめ）

STALL = P.SERVO_STALL_TORQUE
OMEGA0 = math.radians(60) / P.SERVO_SPEED
BAND = math.radians(4.0)
MU = 0.3                                                     # PLA どうしの摩擦係数（乾燥、多め）
PIN_R = P.PIN_R
HINGE_R = P.HINGE_PIN_D / 2
SERVO_FRIC = 0.004                                           # ギアの摩擦（N·m、無通電で回すときの感触から推定）


def rot(v, deg, c):
    a = math.radians(deg)
    x, y = v[0] - c[0], v[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


# --- α → θ の表（運動学）。リンクが届く範囲で 0〜110° -----------------------
TABLE = []
prev = K.ALPHA0
th = -2.0
while th <= 110.0:
    a = K.crank_angle(th, prev)
    if a is None:
        break
    prev = K.unwrap(a, prev)
    TABLE.append((prev, th))
    th += 0.05
TABLE.sort()


def theta_of(alpha):
    lo, hi = 0, len(TABLE) - 1
    if alpha <= TABLE[0][0]:
        return TABLE[0][1]
    if alpha >= TABLE[-1][0]:
        return TABLE[-1][1]
    while hi - lo > 1:
        m = (lo + hi) // 2
        if TABLE[m][0] <= alpha:
            lo = m
        else:
            hi = m
    a0, t0 = TABLE[lo]
    a1, t1 = TABLE[hi]
    return t0 + (t1 - t0) * (alpha - a0) / (a1 - a0)


def config(alpha):
    """α（度）での各剛体の重心位置と角度（m, 度）。"""
    theta = theta_of(alpha)
    lid_com = rot(LID_COM0, theta, H)
    crank_com = rot(CRANK_COM0, alpha - K.ALPHA0, O)
    pa0, pb0 = K.pin_a(K.ALPHA0), K.pin_b(0.0)
    pa1, pb1 = K.pin_a(alpha), K.pin_b(theta)
    ang0 = math.degrees(math.atan2(pb0[1] - pa0[1], pb0[0] - pa0[0]))
    ang1 = math.degrees(math.atan2(pb1[1] - pa1[1], pb1[0] - pa1[0]))
    lc = rot((LINK_COM0[0] * 1000, LINK_COM0[1] * 1000), ang1 - ang0, pa0)
    link_com = ((lc[0] + pa1[0] - pa0[0]) / 1000, (lc[1] + pa1[1] - pa0[1]) / 1000)
    return theta, lid_com, crank_com, link_com, ang1


def energy_terms(alpha, h=0.02):
    """M(α)（kg·m²）と G(α)=dV/dα（N·m）と dθ/dα。数値微分。"""
    c0 = config(alpha - h)
    c1 = config(alpha + h)
    da = math.radians(2 * h)
    dth = math.radians(c1[0] - c0[0]) / da
    v_link = ((c1[3][0] - c0[3][0]) / da, (c1[3][1] - c0[3][1]) / da)
    w_link = math.radians(c1[4] - c0[4]) / da
    m = (ROTOR_I + CRANK_I_O + HORN_I_O + LID_I_H * dth ** 2
         + LINK_M * (v_link[0] ** 2 + v_link[1] ** 2) + LINK_I * w_link ** 2)
    v1 = G * (LID_M * c1[1][1] + CRANK_M * c1[2][1] + LINK_M * c1[3][1])
    v0 = G * (LID_M * c0[1][1] + CRANK_M * c0[2][1] + LINK_M * c0[3][1])
    return m, (v1 - v0) / da, dth


def link_force(alpha, tau_servo):
    """クランクのトルクから、リンクの軸力（N）。"""
    theta = theta_of(alpha)
    pa, pb = K.pin_a(alpha), K.pin_b(theta)
    d = ((pb[0] - pa[0]) / 1000, (pb[1] - pa[1]) / 1000)
    n = math.hypot(*d)
    u = (d[0] / n, d[1] / n)
    r = ((pa[0] - K.O[0]) / 1000, (pa[1] - K.O[1]) / 1000)
    arm = abs(r[0] * u[1] - r[1] * u[0])
    return abs(tau_servo) / arm if arm > 1e-6 else float("inf")


def static_requirement(n=200):
    """静的に蓋を保持するのに要るサーボ・トルク（重力だけ）。動作範囲の全角度で。"""
    a_open = K.crank_angle(K.THETA_OPEN, K.ALPHA0 - 60)
    a_open = K.unwrap(a_open, K.ALPHA0 - 70)
    rows = []
    for i in range(n + 1):
        a = K.ALPHA0 + (a_open - K.ALPHA0) * i / n
        m, g, dth = energy_terms(a)
        rows.append((theta_of(a), a, g, dth))
    return rows, a_open


def simulate(cmd, t_end, stall=STALL, gravity=True, load=True, friction=True, dt=2e-5, alpha_start=None):
    """cmd(t) → 目標角（度）。結果: 時刻ごとの θ・α・トルク。"""
    alpha = math.radians(alpha_start if alpha_start is not None else K.ALPHA0)
    w = 0.0
    t = 0.0
    out = []
    peak = dict(tau=0.0, link_N=0.0, impact_w=0.0)
    k_rim, c_rim = 400.0, 0.4    # 縁: N·m/rad、N·m·s/rad（蓋角で）
    step = 0
    while t < t_end:
        ad = math.degrees(alpha)
        if load:
            m, gterm, dth = energy_terms(ad)
            if not gravity:
                gterm = 0.0
        else:
            m, gterm, dth = ROTOR_I, 0.0, 0.0
        err = math.radians(cmd(t)) - alpha
        u = max(-1.0, min(1.0, err / BAND))
        tau = stall * u - stall / OMEGA0 * w
        tau = max(-stall, min(stall, tau))
        # 摩擦: サーボのギア＋蝶番とピン（リンク軸力 × 半径 × μ）
        fr = 0.0
        if friction:
            fl = link_force(ad, gterm) if load else 0.0
            fr = SERVO_FRIC + MU * fl * PIN_R * 2 * 0.5 + MU * abs(gterm) * 0.0
        # 縁（θ<0）
        rim = 0.0
        theta = theta_of(ad)
        if load and theta < 0:
            th_r = math.radians(theta)
            rim = -(k_rim * th_r + c_rim * w * dth) * dth   # 蓋角の反力をクランク軸へ
            if w * dth < 0:
                peak["impact_w"] = max(peak["impact_w"], abs(w * dth))
        net = tau - gterm + rim
        if friction and abs(w) > 1e-4:
            net -= math.copysign(fr, w)
        elif friction and abs(net) <= fr:
            net = 0.0
            w = 0.0
        acc = net / m
        w += acc * dt
        alpha += w * dt
        t += dt
        peak["tau"] = max(peak["tau"], abs(tau))
        if load:
            peak["link_N"] = max(peak["link_N"], link_force(ad, tau))
        if step % 250 == 0:
            out.append((round(t, 4), round(theta_of(math.degrees(alpha)), 3), round(math.degrees(alpha), 3),
                        round(tau, 5)))
        step += 1
    return out, peak


def lid_terms(alpha, h=0.02):
    """蓋だけの M と G（質量を変える試験用に分けて出す）。"""
    c0 = config(alpha - h)
    c1 = config(alpha + h)
    da = math.radians(2 * h)
    dth = math.radians(c1[0] - c0[0]) / da
    return LID_I_H * dth ** 2, G * LID_M * (c1[1][1] - c0[1][1]) / da


def export_tables(a_closed, a_open, step=0.1):
    """Studio の物理検証画面（viewer/lid-cube）が同じ式をブラウザで解くための表。

    α は TABLE の範囲（θ = -2〜110°）。M・G は蓋とそれ以外に分ける（蓋の質量の倍率を掛けるため）。"""
    lo, hi = TABLE[0][0] + 0.2, TABLE[-1][0] - 0.2
    rows = []
    n = int((hi - lo) / step)
    for i in range(n + 1):
        a = lo + i * step
        m, g, dth = energy_terms(a)
        ml, gl = lid_terms(a)
        theta = theta_of(a)
        pa, pb = K.pin_a(a), K.pin_b(theta)
        d = ((pb[0] - pa[0]) / 1000, (pb[1] - pa[1]) / 1000)
        nn = math.hypot(*d)
        r = ((pa[0] - K.O[0]) / 1000, (pa[1] - K.O[1]) / 1000)
        arm = abs(r[0] * d[1] / nn - r[1] * d[0] / nn)
        rows.append([round(a, 3), round(theta, 4), m - ml, ml, g - gl, gl, round(dth, 5), arm])
    out = dict(columns=["alpha_deg", "theta_deg", "M_rest", "M_lid", "G_rest", "G_lid", "dtheta_dalpha", "arm_m"],
               rows=rows, alpha_closed=a_closed, alpha_open=a_open,
               const=dict(stall=STALL, omega0=OMEGA0, band=BAND, mu=MU, pin_r=PIN_R, servo_fric=SERVO_FRIC,
                          k_rim=400.0, c_rim=0.4, dt=2e-5))
    with open(os.path.join(HERE, "build", "sim_tables.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, separators=(",", ":"))


def first_time(rows, pred):
    for r in rows:
        if pred(r):
            return r[0]
    return None


def main():
    res = {'input_sha256': REP['input_sha256']}
    rows, a_open = static_requirement()
    a_closed = K.ALPHA0
    req = max(abs(r[2]) for r in rows)
    at = max(rows, key=lambda r: abs(r[2]))
    res["kinematics"] = dict(alpha_closed=round(a_closed, 2), alpha_open=round(a_open, 2),
                             crank_travel=round(a_open - a_closed, 2), lid_travel=K.THETA_OPEN)
    res["mass"] = dict(lid_g=round(LID_M * 1000, 2), lid_I_hinge_kgm2=LID_I_H, link_g=round(LINK_M * 1000, 2),
                       crank_g=round(CRANK_M * 1000, 2), crank_I_O=CRANK_I_O)
    if "roof" in MASS:
        res["mass"]["roof_g"] = round(kg("roof") * 1000, 2)
    res["static"] = dict(max_torque_Nm=round(req, 5), at_theta=round(at[0], 1),
                         ratio_to_stall=round(req / STALL, 4),
                         curve=[(round(r[0], 1), round(r[2] * 1000, 2)) for r in rows[::10]])

    # 計器の校正 1: 負荷なし・重力なしで 70° 回す時間 ≈ 公称 0.1s/60°
    span = a_open - a_closed
    out, pk = simulate(lambda t: a_closed + span, 0.4, load=False, gravity=False, friction=False)
    t70 = first_time(out, lambda r: abs(r[2] - (a_closed + span)) < 1.0)
    res["calib_noload_speed"] = dict(t_to_within_1deg=t70, nominal=round(abs(span) / 60 * P.SERVO_SPEED, 3))
    # 計器の校正 2: トルクを静的必要量の半分にすると開かない
    out, pk = simulate(lambda t: a_open, 1.5, stall=req * 0.5)
    res["calib_half_torque_fails"] = dict(final_theta=out[-1][1], opened=out[-1][1] > K.THETA_OPEN - 5)

    # 本番 1: 全速の開閉（目標を一気に切り替える）
    def step_cmd(t):
        return a_open if t < 1.0 else a_closed
    out, pk = simulate(step_cmd, 2.0)
    res["full_speed"] = dict(
        t_open_90pct=first_time(out, lambda r: r[1] > 0.9 * K.THETA_OPEN),
        theta_at_1s=[r[1] for r in out if r[0] >= 0.999][0],
        t_closed=first_time([r for r in out if r[0] > 1.0], lambda r: r[1] < 0.5),
        peak_torque_Nm=round(pk["tau"], 4), peak_link_N=round(pk["link_N"], 2),
        lid_impact_rad_s=round(pk["impact_w"], 2),
        trace=[r for r in out[::2]])
    duration = P.OPEN_TIME_S
    res['motion_time_s'] = duration
    # 本番 2: 指定時間かけて目標を動かす
    def ramp(t):
        if t < duration:
            return a_closed + (a_open - a_closed) * t / duration
        if t < 1.5:
            return a_open
        if t < 1.5 + duration:
            return a_open + (a_closed - a_open) * (t - 1.5) / duration
        return a_closed
    out, pk = simulate(ramp, 3.0)
    res["ramped"] = dict(theta_at_1_5s=[r[1] for r in out if r[0] >= 1.499][0], final_theta=out[-1][1],
                         peak_torque_Nm=round(pk["tau"], 4), lid_impact_rad_s=round(pk["impact_w"], 2),
                         trace=[r for r in out[::2]])
    # 本番 3: OPEN_TIME_Sで始めと終わりをゆっくり動かす。
    def ease(t):
        def s(x):
            x = max(0.0, min(1.0, x))
            return x * x * (3 - 2 * x)
        if t < 1.5:
            return a_closed + (a_open - a_closed) * s(t / duration)
        return a_open + (a_closed - a_open) * s((t - 1.5) / duration)
    out, pk = simulate(ease, 3.0)
    res["eased"] = dict(theta_at_1_5s=[r[1] for r in out if r[0] >= 1.499][0], final_theta=out[-1][1],
                        peak_torque_Nm=round(pk["tau"], 4), lid_impact_rad_s=round(pk["impact_w"], 2),
                        trace=[r for r in out[::2]])
    # 開いた位置での重力トルク。
    m95, g95, _ = energy_terms(a_open)
    _, _, dth95 = energy_terms(a_open)
    res["open_hold"] = dict(gravity_torque_about_hinge_Nm=round(g95 / dth95, 5),
                            note="蝶番まわりの重力トルク dV/dθ。正なら閉じる向き、負なら後ろへ倒れる向き")
    # 余裕: 電圧が下がってトルクが 30% しか出ない場合（摩擦は多めのまま）
    out, pk = simulate(lambda t: a_open, 1.5, stall=STALL * 0.3)
    res["weak_30pct"] = dict(final_theta=out[-1][1], opened=out[-1][1] > K.THETA_OPEN - 1)
    # 閉じた位置での保持（電源 OFF でも蓋の重さでギアが回らないか）: 重力トルク vs ギア摩擦
    m, g0, _ = energy_terms(a_closed + 0.5)
    res["closed_hold_unpowered"] = dict(gravity_torque_at_servo_Nm=round(abs(g0), 5), servo_friction_Nm=SERVO_FRIC)
    calibration_ok = (t70 is not None and abs(t70 - abs(span) / 60 * P.SERVO_SPEED)
                      <= .2 * abs(span) / 60 * P.SERVO_SPEED
                      and not res['calib_half_torque_fails']['opened'])
    res['calibration_ok'] = calibration_ok
    res['ok'] = (calibration_ok and res['weak_30pct']['opened']
                 and abs(res['eased']['theta_at_1_5s'] - K.THETA_OPEN) < 1
                 and abs(res['eased']['final_theta']) < .5)
    with open(os.path.join(HERE, "build", "simulate_report.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    export_tables(a_closed, a_open)
    assert res['ok'], 'Physical simulation or its calibration failed'
    show = {k: v for k, v in res.items() if k not in ()}
    for k, v in show.items():
        if isinstance(v, dict):
            v = {kk: vv for kk, vv in v.items() if kk not in ("trace", "curve")}
        print(k, v)


main()
