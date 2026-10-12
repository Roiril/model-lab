"""力を受ける部位の応力判定。print_review.py が使う（許した例外 params.PRINT_EXCEPTIONS の選び方は print_review.py の exception_fns）。

肉厚 3.0mm 未満でも、運転時の力と応力が PLA の降伏の 1/3 以下、停動（サーボが止まるまで押した最悪）でも 1/1.5 以下なら
「応力で許可」として分ける。1.0mm 未満の薄い所（潰しリブなど）は応力では許可しない。
"""
import importlib.util
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))

SIGMA_Y = 35.0           # PLA の降伏応力 MPa（Bambu PLA Basic の XY 公称 約 35。層に直交は約 20 なので、層に沿う荷重だけを判定する）
TAU_Y = 0.577 * SIGMA_Y  # せん断の降伏（von Mises）
LEWIS_Y = {17: 0.302, 38: 0.384}   # Lewis の歯形係数（圧力角 20 度）
FACTOR_OP = 3.0          # 運転時は降伏の 1/3 以下
FACTOR_STALL = 1.5       # 停動でも降伏の 1/1.5 以下
MIN_JUDGED_MM = 1.0      # これ未満の薄さは応力で許可しない

HEX_WALL_MIN = 1.22      # カムの六角穴の角と最小半径 CAM_RMIN の間の肉（params: CAM_RMIN 5.2 - 六角穴の外接半径 3.98）
HORN_ARM_MM = 18.0       # SG92R ホーンの長腕
COUPLER_WALL_MM = 1.6    # 受けのポケットの壁
COUPLER_WALL_W = 7.3     # 同 橋の最大幅


def load_params():
    spec = importlib.util.spec_from_file_location("tpc_params", os.path.join(HERE, "params.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def judgement(P, design):
    """項目名 -> 応力の表。運転 = 設計の必要トルク（μ=0.45 の側）、停動 = SG92R の停動トルク。寸法は params から読む。"""
    stall = P.SERVO_STALL_NM * 1000.0                                 # N·mm（サーボ軸）
    t_op = float(design["summary"]["key"]["torque_045_mNm"])         # N·mm（サーボ軸）
    g = P.G_RATIO
    b = P.GEAR_T * 1000.0
    r_sector = P.SERVO_GEAR_PD / 2 * 1000.0                          # 半円歯車のピッチ半径 19mm
    items = {}

    def add(name, basis, op, st, yield_mpa, note):
        ok = op <= yield_mpa / FACTOR_OP and st <= yield_mpa / FACTOR_STALL
        items[name] = {"basis": basis, "operating_mpa": round(op, 2), "stall_mpa": round(st, 2),
                       "yield_mpa": round(yield_mpa, 1), "operating_fraction_of_yield": f"1/{yield_mpa / op:.0f}",
                       "stall_fraction_of_yield": f"1/{yield_mpa / st:.1f}", "pass": bool(ok), "note": note}

    names = {}
    for z, key, label in ((P.CHAIN_Z, "gear", "歯車 17 歯の歯（軸 5 本の連動）"), (P.SERVO_Z, "horn_coupler", "受けの半円歯車 38 歯の歯")):
        y = LEWIS_Y[z]
        fo, fs = t_op / r_sector, stall / r_sector
        add(label, f"Lewis σ = Ft/(b m Y)。b={b:.1f}mm、m=1、Y={y}。接線力 Ft = サーボ軸のトルク / {r_sector:.0f}mm: "
                   f"運転 {fo:.1f}N、停動 {fs:.1f}N", fo / (b * y), fs / (b * y), SIGMA_Y, "歯は層に沿って曲がる向き（平置き）")
        names[key] = label
    t_shaft_op, t_shaft_st = t_op / g, stall / g                      # 軸のトルク（増速 g 倍なので 1/g）
    arm = P.SHAFT_AF * 1000.0 / 2
    f_op, f_st = t_shaft_op / arm, t_shaft_st / arm
    cam_l = P.CAM_T * 1000
    label = "カムの六角穴まわりの環（最小の肉 1.22）"
    add(label, f"軸のトルク = サーボ/{g:.2f}（運転 {t_shaft_op:.0f}、停動 {t_shaft_st:.0f} N·mm）を 1 枚のカムが全部受ける最悪。"
               f"六角の面（腕 {arm:.2f}mm）に {f_op:.1f}N / {f_st:.1f}N、せん断面 = 肉 {HEX_WALL_MIN} x カム厚 {cam_l:.0f}",
        f_op / (HEX_WALL_MIN * cam_l), f_st / (HEX_WALL_MIN * cam_l), TAU_Y, "せん断。実際は 5 枚で分担")
    names["cam"] = label
    area = math.pi * (P.SLEEVE_R * 1000) ** 2 - 0.866 * (P.SHAFT_BORE_AF * 1000) ** 2
    add("カムのハブ筒（軸方向）", f"軸方向の押し付けを 10N と仮定。断面 {area:.0f}mm2", 10.0 / area, 10.0 / area, SIGMA_Y,
        "ハブは次の部材との間隔を保つだけ（トルクは板が受ける）")
    d = 2 * P.CLIP_GROOVE_R * 1000
    tau = 16 * t_shaft_st / (math.pi * d ** 3)
    label = "軸の C クリップ溝の首（Ø%.1f）と鍔" % d
    add(label, f"軸のトルク（停動 {t_shaft_st:.0f} N·mm）のねじり τ = 16T/(πd³)。鍔は軸方向 10N、厚み 1.2 x 円周 {math.pi * 6.5:.0f}mm のせん断は {10 / (1.2 * math.pi * 6.5):.2f}MPa",
        tau * t_shaft_op / t_shaft_st, tau, TAU_Y, "ねじり")
    names["shaft"] = label
    f_h_st, f_h_op = stall / HORN_ARM_MM, t_op / HORN_ARM_MM
    lever = COUPLER_WALL_MM
    label = "受けのホーンのポケットの壁（厚み 1.6）"
    add(label, f"ホーンの長腕の先 {HORN_ARM_MM:.0f}mm で受ける力: 運転 {f_h_op:.1f}N、停動 {f_h_st:.1f}N。壁の根元の曲げ（腕 {lever}mm、幅 {COUPLER_WALL_W}mm）",
        6 * f_h_op * lever / (COUPLER_WALL_W * COUPLER_WALL_MM ** 2), 6 * f_h_st * lever / (COUPLER_WALL_W * COUPLER_WALL_MM ** 2),
        SIGMA_Y, "ホーンは壁を押す")
    names["housing_bearing"] = "軸受けの壁（U 溝の裏、2.3mm）"
    ft_st, ft_op = stall / r_sector, t_op / r_sector
    tan_phi = math.tan(math.radians(20.0))
    weight = 0.5                                                        # 軸 + カム 5 枚 + 画素の重さ（N。上限の見積り）
    f_st, f_op = ft_st * tan_phi + weight, ft_op * tan_phi + weight    # 歯車の分離力（Ft tan 20°）+ 重さ
    dj, lj = 5.0, 1.0                                                   # 軸の丸の径と、U 溝にかかる長さ（params.JOURNAL_D、PAD 1.0）
    add(names["housing_bearing"], f"軸の丸 Ø{dj} が U 溝に掛かる長さ {lj}mm への面圧。径方向の力 = 歯の分離力 Ft tan20° + 重さ 0.5N: 運転 {f_op:.1f}N、停動 {f_st:.1f}N。"
        f"裏の壁（2.3mm）の押し抜きせん断は {f_st / (math.pi * dj * 2.3):.2f}MPa", f_op / (dj * lj), f_st / (dj * lj), SIGMA_Y, "面圧")
    names["housing_fence"] = "サーボ取付耳の柵（厚み 3.0）"
    lever, wf, tf, hf = 16.0, 6.5, 3.0, 8.0
    ff_st, ff_op = stall / lever, t_op / lever
    add(names["housing_fence"], f"サーボのトルクの反力が耳（軸から {lever:.0f}mm）に掛かる力: 運転 {ff_op:.1f}N、停動 {ff_st:.1f}N。柵（幅 {wf}mm、厚み {tf}mm、高さ {hf}mm の片持ち）の根元の曲げ",
        6 * ff_op * hf / (wf * tf ** 2), 6 * ff_st * hf / (wf * tf ** 2), SIGMA_Y, "片持ちの曲げ。耳は 2 枚の柵で挟むので実際は半分ずつ")
    return items, names


def worst_pass(items, labels):
    """複数の項目のうち 1 つでも通らなければ通らない。"""
    return all(items[l]["pass"] for l in labels)
