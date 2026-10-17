"""タンジブル画素キューブの駆動接続と保持を実 STL から検証する（ホーン・鍵・歯車の噛み合い・軸・サーボ・案内板・ベゼル・画素・配線）。

実行: "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python-exit-code 1 --python models/tangible-pixel-cube/drive.py
出力: build/drive_report.json（viewer/lattice/CONTRACT.md の形。overall.geometryPass, interfaces[{id,label,status,detail}], calibration[], hardwareUnknown[]）

計器は verify.py のもの（MANIFOLD の共通体積、床 0.001mm3、初接触の二分探索）をそのまま使う。
界面ごとに「保持相手との初接触までの移動量」を ±X / ±Y / ±Z（回転は ±角）で測り、保持相手を外した負例で接触が消えることも測る。
初接触は「共通体積が床を超えた最初の位置」なので、面接触の侵入深さ = 床 / 接触面積（面 1mm2 で 0.001mm）だけ手前の値より先で検出される。
"""
from __future__ import annotations

import itertools
import json
import math
import sys
import time
from pathlib import Path

import bmesh
import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import verify as V  # noqa: E402
import params as P  # noqa: E402
import kinematics as K  # noqa: E402
import patterns as PT  # noqa: E402

FLOOR = V.VOLUME_FLOOR_MM3
I4 = np.eye(4)
ZS = P.SERVO_AXIS_Z * 1000.0       # サーボ出力軸の高さ（24.2）
ZC = P.CAM_AXIS_Z * 1000.0         # カム軸の高さ（51.7）
G = P.G_RATIO
DIRS = {"+X": (1, 0, 0), "-X": (-1, 0, 0), "+Y": (0, 1, 0), "-Y": (0, -1, 0), "+Z": (0, 0, 1), "-Z": (0, 0, -1)}
MARGIN_LIMIT_DEG = 1.0             # 位相の余裕の合格条件（design_check と同じ。2026-10-13 に 2° から変更）
FAR = 400.0                        # 保持相手を退避させる距離（mm）


def log(text):
    print(text, flush=True)


# =============================================================================================
# 共通の道具
# =============================================================================================
class Ctx:
    """計器と場面。部品は組立姿勢（サーボ 90 度、画素は面一）の STL"""

    def __init__(self):
        self.meter = V.Meter()
        self.scene = V.Scene()
        self.pose = self.scene.poses(90.0)
        self.rib_theory = {}
        self.specs = {}

    def solid(self, name):
        return self.scene.solids[name]

    def at(self, *names):
        """組立姿勢の固定側 {名前: (Solid, 4x4)}"""
        return {name: (self.scene.solids[name], self.pose[name]) for name in names}

    def away(self, names, direction):
        """names を direction へ FAR だけ退避させた固定側（保持相手を外した負例）"""
        d = np.asarray(direction, dtype=float)
        return {name: (self.scene.solids[name], V.translation_np(*(d * FAR)) @ self.pose[name]) for name in names}


def measure_group(meter, members, delta, fixed, allowed=None):
    """members = [(名前, Solid, 基準姿勢)] を共通の変換 delta で動かし、固定側との共通体積を測る。
    戻り: (最大体積, [(動く側, 固定側)], 成分の外接箱)"""
    worst, pairs, comps = 0.0, [], []
    for name, solid, base in members:
        volume, names, components = V.measure_set(meter, solid, delta @ base, fixed, allowed)
        for other in names:
            pairs.append((name, other))
        comps.extend(components)
        worst = max(worst, volume)
    return worst, pairs, comps


def first_contact_group(meter, members, delta_fn, fixed, maximum, coarse, allowed=None, refine=14):
    """V.first_contact の複数部品版（剛体として動く群）"""
    volume0, pairs0, comps0 = measure_group(meter, members, delta_fn(0.0), fixed, allowed)
    if pairs0:
        return {"nominalEvent": True, "travel": 0.0, "volume": volume0, "pairs": pairs0, "components": comps0}
    previous, t = 0.0, coarse
    while t <= maximum + 1e-9:
        volume, pairs, comps = measure_group(meter, members, delta_fn(t), fixed, allowed)
        if pairs:
            low, high = previous, t
            for _ in range(refine):
                middle = (low + high) / 2.0
                if measure_group(meter, members, delta_fn(middle), fixed, allowed)[1]:
                    high = middle
                else:
                    low = middle
            volume, pairs, comps = measure_group(meter, members, delta_fn(high), fixed, allowed)
            return {"nominalEvent": False, "travel": round(high, 6), "volume": volume, "pairs": pairs, "components": comps}
        previous, t = t, t + coarse
    return {"nominalEvent": False, "travel": None, "volume": 0.0, "pairs": [], "components": []}


def bounds_of(components):
    if not components:
        return None
    lower = [min(c[0][a] for c in components) for a in range(3)]
    upper = [max(c[1][a] for c in components) for a in range(3)]
    return [[round(v, 3) for v in lower], [round(v, 3) for v in upper]]


def six_directions(ctx, members, fixed, expected, retainers, maximum=3.0, coarse=0.05, allowed=None,
                   tolerance=0.05, locations=None, only=None):
    """動かす群を ±X/±Y/±Z へ動かし、保持相手との初接触を測る。
    expected[方向] = 期待する移動量（None なら maximum まで接触しない）。
    retainers[方向] = その方向の保持相手の名前の一覧。負例はその相手だけを退避させて、接触が消えること。
    locations[方向] = 接触成分が収まるべき領域の一覧（任意）"""
    rows = []
    for name, vector in DIRS.items():
        if only is not None and name not in only:
            continue
        base_fixed = fixed
        result = first_contact_group(ctx.meter, members, lambda t, v=vector: V.translation_np(*(np.asarray(v) * t)),
                                     base_fixed, maximum, coarse, allowed)
        want = expected.get(name)
        travel = result["travel"]
        if want is None:
            matches = travel is None
        elif want == "contact":
            matches = travel is not None
        else:
            matches = travel is not None and abs(travel - want) <= tolerance
        located = True
        region = (locations or {}).get(name)
        if region is not None and result["components"]:
            located = V.components_inside(result["components"], region, tolerance=0.05)
        # 期待した接触が探索範囲 maximum の中に無いとき: 範囲を広げて探し、止まらないのが「保持の相手が無い」からか「探索範囲が足りない」からかを区別する
        extended = None
        if travel is None and want is not None:
            ext_max = max(5.0, maximum * 3.0)
            wide = first_contact_group(ctx.meter, members, lambda t, v=vector: V.translation_np(*(np.asarray(v) * t)),
                                       fixed, ext_max, 0.1, allowed)
            extended = {"searchedToMm": ext_max, "travelMm": wide["travel"],
                        "contactedPairs": sorted({f"{a}|{b}" for a, b in wide["pairs"]}),
                        "contactComponentsBoundsMm": bounds_of(wide["components"]),
                        "reason": ("探索範囲 %.2fmm の外で %s に %.3fmm で当たる（探索範囲が足りないのではなく、期待した止まりが無く、その先の別の面で止まる）"
                                   % (maximum, "/".join(sorted({b for _a, b in wide["pairs"]})), wide["travel"])
                                   if wide["travel"] is not None else
                                   "%.1fmm 先まで保持の相手が無い（固定側のどの部品にも当たらない）" % ext_max)}
        # 負例: この方向の保持相手だけを退避させる
        removal = None
        removed_names = retainers.get(name, [])
        if want is not None and removed_names and travel is not None:
            reduced = {key: value for key, value in fixed.items()}
            for other in removed_names:
                solid, matrix = reduced[other]
                reduced[other] = (solid, V.translation_np(*(np.asarray(vector) * FAR)) @ matrix)
            neg = first_contact_group(ctx.meter, members, lambda t, v=vector: V.translation_np(*(np.asarray(v) * t)),
                                      reduced, maximum, coarse, allowed)
            # 相手を外すと、その接触が消える（None）か、さらに先の別の部品に当たる（0.1mm 以上遠い）こと
            removal = {"removed": removed_names, "travelMm": neg["travel"],
                       "pass": bool(neg["travel"] is None or round(neg["travel"], 2) >= round(travel + 0.1, 2))}
        rows.append({"direction": name, "label": name, "contact": {"contactTravelMm": travel},
                     "expectedMm": None if want == "contact" else want, "travelMm": travel,
                     "contactedPairs": sorted({f"{a}|{b}" for a, b in result["pairs"]}),
                     "contactComponentsBoundsMm": bounds_of(result["components"]),
                     "matchesExpected": bool(matches), "locatedAtExpectedRegion": bool(located),
                     "retainerRemovedNegative": removal, "noContactWithinSearch": travel is None, "extendedSearch": extended,
                     "pass": bool(matches and located and (removal is None or removal["pass"]))})
    return rows


def interface(identifier, label, rows_or_pass, detail, **extra):
    """drive_report.interfaces の 1 件。status は pass / fail / unknown"""
    passed = rows_or_pass if isinstance(rows_or_pass, bool) else all(row["pass"] for row in rows_or_pass)
    entry = {"id": identifier, "label": label, "status": "pass" if passed else "fail", "detail": detail}
    entry.update(extra)
    return entry


# =============================================================================================
# 校正（drive.py 固有の道具）
# =============================================================================================
def clip_area_beyond(poly, y_wall):
    """多角形のうち y > y_wall の面積（Sutherland-Hodgman）"""
    out = []
    n = len(poly)
    for k in range(n):
        a, b = poly[k], poly[(k + 1) % n]
        a_in, b_in = a[1] > y_wall, b[1] > y_wall
        if a_in:
            out.append(a)
        if a_in != b_in:
            t = (y_wall - a[1]) / (b[1] - a[1])
            out.append((a[0] + t * (b[0] - a[0]), y_wall))
    if len(out) < 3:
        return 0.0
    return abs(sum(out[i][0] * out[(i + 1) % len(out)][1] - out[(i + 1) % len(out)][0] * out[i][1] for i in range(len(out)))) / 2.0


def slot_bar_volume(alpha_deg, half_length=5.0, half_width=1.0, wall=1.5, thickness=2.0):
    """長さ 2*half_length・幅 2*half_width の棒を Z まわりに alpha 回したとき、y = +wall の壁を越える体積（片方の壁の分）"""
    a = math.radians(alpha_deg)
    c, s = math.cos(a), math.sin(a)
    corners = [(x * c - y * s, x * s + y * c) for x, y in ((-half_length, -half_width), (half_length, -half_width),
                                                          (half_length, half_width), (-half_length, half_width))]
    return clip_area_beyond(corners, wall) * thickness


def prepare_a(solid, matrix):
    """固定側 A の世界座標・外接箱・BVH（B の姿勢を変えながら何度も測るとき、A を作り直さない）"""
    vertices = solid.posed(matrix)
    return {"verts": vertices, "lo": vertices.min(axis=0), "hi": vertices.max(axis=0),
            "bvh": V.Meter.bvh_of(vertices, solid.faces)}


def common_with_a(meter, solid_a, a_entry, solid_b, matrix_b):
    """prepare_a で用意した A と、姿勢 matrix_b の B の共通体積（Meter.common と同じ判定）"""
    vb = solid_b.posed(matrix_b)
    lo_b, hi_b = vb.min(axis=0), vb.max(axis=0)
    if np.any(a_entry["hi"] < lo_b) or np.any(hi_b < a_entry["lo"]):
        return 0.0
    bvh_b = V.Meter.bvh_of(vb, solid_b.faces)
    verdict = meter.zero_by_topology(a_entry["verts"], solid_a.faces, a_entry["bvh"], a_entry["lo"], a_entry["hi"],
                                     vb, solid_b.faces, bvh_b, lo_b, hi_b)
    if verdict:
        return 0.0
    return meter.boolean_common(solid_a, a_entry["verts"], solid_b, vb)[0]


def mesh_window(meter, solid_a, matrix_a, solid_b, matrix_b_fn, scan=4.0, coarse=0.1, limit=30.0, refine=14):
    """B を自分の軸まわりに delta（度）回し、A と共通体積が床以下になる delta の区間（自由な窓）を測る。
    delta = 0 が干渉していれば、±scan の範囲で自由な点を探し、その点を含む区間を返す。
    戻り: {free, low, high, centerFound}。自由な点が無ければ free = False（噛み合えない）"""
    a_entry = prepare_a(solid_a, matrix_a)

    def clear(delta):
        return common_with_a(meter, solid_a, a_entry, solid_b, matrix_b_fn(delta)) <= FLOOR

    center = None
    if clear(0.0):
        center = 0.0
    else:
        k = 1
        while k * coarse <= scan + 1e-9 and center is None:
            for sign in (1, -1):
                if clear(sign * k * coarse):
                    center = sign * k * coarse
                    break
            k += 1
    if center is None:
        return {"free": False, "low": None, "high": None, "centerFound": None}

    def boundary(sign):
        previous, step = center, coarse
        while abs(center + sign * step) <= limit:
            if not clear(center + sign * step):
                low, high = previous, center + sign * step
                for _ in range(refine):
                    middle = (low + high) / 2.0
                    if clear(middle):
                        low = middle
                    else:
                        high = middle
                return low
            previous = center + sign * step
            step += coarse
        return center + sign * limit
    return {"free": True, "low": boundary(-1), "high": boundary(1), "centerFound": center}


def calibration_rows(ctx):
    """drive.py 固有の計器の校正。verify.py の校正（共通体積・初接触・姿勢）に加えて、群の初接触・窓・六方向の表を測る"""
    meter = ctx.meter
    rows = []
    base = V.meter_calibration(meter)
    rows.append({"id": "verify-instrument", "label": "共通体積・初接触・姿勢・高さの計器（verify.py の校正）",
                 "pass": bool(base["pass"]), "detail": {key: row.get("pass") for key, row in base.items() if isinstance(row, dict)}})
    # 群の初接触: 2 つの立方体を一緒に +X へ動かし、先頭の立方体が壁に当たる位置
    cube_a = V.cube_solid("cal_group_a", (0, 0, 0), 1.0)
    cube_b = V.cube_solid("cal_group_b", (0, 5.0, 0), 1.0)
    wall = V.box_solid("cal_group_wall", (2.0, -5.0, -5.0), (3.0, 10.0, 5.0))
    members = [("a", cube_a, I4), ("b", cube_b, V.translation_np(0.0, 0.0, 0.0))]
    found = first_contact_group(meter, members, lambda t: V.translation_np(t, 0, 0), {"wall": (wall, I4)}, maximum=3.0, coarse=0.05)
    expected = 1.5 + FLOOR / 1.0
    rows.append({"id": "group-first-contact", "label": "剛体群の初接触（2 立方体、壁まで 1.5mm）",
                 "pass": bool(found["travel"] is not None and abs(found["travel"] - expected) <= 0.0001),
                 "detail": {"measured": found["travel"], "expected": expected,
                            "pairs": sorted({f"{a}|{b}" for a, b in found["pairs"]})}})
    # 窓: 溝の中の棒。対称な窓は初接触の探索（解析値と照合済み）の ±、ずらした棒は区間がずれ、delta = 0 が干渉していても窓を見つける
    slot = [V.box_solid("cal_slot_p", (-20.0, 1.5, -2.0), (20.0, 6.0, 2.0)),
            V.box_solid("cal_slot_m", (-20.0, -6.0, -2.0), (20.0, -1.5, 2.0))]
    bar = V.box_solid("cal_bar", (-5.0, -1.0, -1.0), (5.0, 1.0, 1.0))
    # 壁が 2 枚あるので、窓の端の解析値は片方の壁との接触角（体積が床を超える角）
    low_a, high_a = 0.0, 20.0
    for _ in range(60):
        middle = (low_a + high_a) / 2.0
        if slot_bar_volume(middle) > FLOOR:
            high_a = middle
        else:
            low_a = middle
    expected_edge = low_a

    def both_walls(delta, offset):
        # 2 枚の壁を 1 つの固定側として扱うため、壁ごとに測って大きい方を返す補助
        volumes = [meter.common(bar, V.rot_z_np(delta + offset), wall_solid, I4)[0] for wall_solid in slot]
        return max(volumes)

    def window_for(offset):
        def clear(delta):
            return both_walls(delta, offset) <= FLOOR
        if clear(0.0):
            center = 0.0
        else:
            center = None
            k = 1
            while k * 0.1 <= 4.0 + 1e-9 and center is None:
                for sign in (1, -1):
                    if clear(sign * k * 0.1):
                        center = sign * k * 0.1
                        break
                k += 1
        if center is None:
            return None

        def edge(sign):
            previous, step = center, 0.1
            while abs(center + sign * step) <= 30.0:
                if not clear(center + sign * step):
                    low, high = previous, center + sign * step
                    for _ in range(14):
                        middle = (low + high) / 2.0
                        if clear(middle):
                            low = middle
                        else:
                            high = middle
                    return low
                previous = center + sign * step
                step += 0.1
            return None
        return edge(-1), edge(1)
    centered = window_for(0.0)
    shifted = window_for(8.0)           # 棒を 8 度ずらしてある。delta = 0 は壁に当たっている
    ok_centered = bool(centered and abs(centered[0] + expected_edge) <= 0.01 and abs(centered[1] - expected_edge) <= 0.01)
    ok_shifted = bool(shifted and abs(shifted[0] - (-expected_edge - 8.0)) <= 0.01 and abs(shifted[1] - (expected_edge - 8.0)) <= 0.01)
    rows.append({"id": "mesh-window", "label": "噛み合いの窓（溝の中の棒を回す。窓の端の解析値と照合）",
                 "pass": ok_centered and ok_shifted,
                 "detail": {"expectedEdgeDeg": expected_edge, "centered": centered, "shiftedBy8deg": shifted,
                            "note": "ずらした棒では delta = 0 が壁に当たっており、探索が窓を見つけること"}})
    # 窓の関数そのもの（mesh_window）が 1 枚の壁で同じ端を返すこと
    wall_one = V.box_solid("cal_slot_one", (-20.0, 1.5, -2.0), (20.0, 6.0, 2.0))
    one_window = mesh_window(meter, wall_one, I4, bar, lambda d: V.rot_z_np(d), scan=4.0, coarse=0.1)
    # 棒は両端が壁に近づくので、1 枚の壁でも窓は ±expected_edge
    rows.append({"id": "mesh-window-function", "label": "mesh_window 関数（1 枚の壁。窓の両端が解析値）",
                 "pass": bool(one_window["free"] and one_window["high"] is not None and one_window["low"] is not None
                              and abs(one_window["high"] - expected_edge) <= 0.01
                              and abs(one_window["low"] + expected_edge) <= 0.01),
                 "detail": {"measured": one_window, "expectedEdgeDeg": expected_edge}})
    # 六方向の表: 1 つの立方体の囲み（隙間 0.1..0.35 を測り分ける）
    box_parts = {
        "xp": V.box_solid("cal_xp", (0.6, -3, -3), (3, 3, 3)), "xm": V.box_solid("cal_xm", (-3, -3, -3), (-0.55, 3, 3)),
        "yp": V.box_solid("cal_yp", (-3, 0.7, -3), (3, 3, 3)), "ym": V.box_solid("cal_ym", (-3, -3, -3), (3, -0.65, 3)),
        "zp": V.box_solid("cal_zp", (-3, -3, 0.8), (3, 3, 3)), "zm": V.box_solid("cal_zm", (-3, -3, -3), (3, 3, -0.75)),
    }
    probe = V.cube_solid("cal_probe", (0, 0, 0), 1.0)
    ctx_like = type("C", (), {"meter": meter})()
    fixed = {name: (solid, I4) for name, solid in box_parts.items()}
    retainers = {"+X": ["xp"], "-X": ["xm"], "+Y": ["yp"], "-Y": ["ym"], "+Z": ["zp"], "-Z": ["zm"]}
    expected_gaps = {"+X": 0.1, "-X": 0.05, "+Y": 0.2, "-Y": 0.15, "+Z": 0.3, "-Z": 0.25}
    table = six_directions(ctx_like, [("probe", probe, I4)], fixed,
                           {name: value + FLOOR / 1.0 for name, value in expected_gaps.items()},
                           retainers, maximum=1.0, coarse=0.025, tolerance=0.0005)
    rows.append({"id": "six-directions", "label": "六方向の初接触の表（囲みの隙間 0.05〜0.30mm を各方向で測り分け、相手を外すと消える）",
                 "pass": all(row["pass"] for row in table),
                 "detail": {row["direction"]: {"expected": expected_gaps[row["direction"]], "measured": row["travelMm"],
                                              "negative": row["retainerRemovedNegative"]} for row in table}})
    rows.append(phase_propagation_calibration())
    rows.append(boolean_difference_calibration())
    rows.append(design_check_calibration())
    rows.append({"id": "floor-bias", "label": "初接触の定義（共通体積が床 0.001mm3 を超えた最初の位置）",
                 "pass": True,
                 "detail": "面接触は侵入深さ = 床 / 接触面積 だけ先で検出される（1mm2 で 0.001mm）。線・角の接触は侵入が浅いうち体積が小さいので、"
                           "角度に直した偏りが大きい。歯の側面（幅 2mm の線接触）の偏りは歯車の節で別に見積もる"})
    return rows


# =============================================================================================
# 1. ホーンと受け
# =============================================================================================
def mirror_y(solid, y0, name):
    """Y = y0 の面で鏡像にした立体（面の向きを反転して閉じた立体のまま）"""
    tris = solid.tris.copy()
    tris[:, :, 1] = 2.0 * y0 - tris[:, :, 1]
    return V.Solid(name, tris[:, [0, 2, 1], :])


def horn_interface(ctx):
    """付属ホーン（sg92r_horn）と受け（horn_coupler）。受けを動かして初接触を測る。ホーンのスプライン嵌合は正本に無いので別に未確認とする"""
    meter = ctx.meter
    horn, coupler = ctx.solid("sg92r_horn"), ctx.solid("horn_coupler")
    nominal = meter.common(horn, ctx.pose["sg92r_horn"], coupler, ctx.pose["horn_coupler"])[0]
    members = [("horn_coupler", coupler, ctx.pose["horn_coupler"])]
    fixed = ctx.at("sg92r_horn")
    clearance = P.HORN_CLR * 1000.0
    rows = six_directions(
        ctx, members, fixed,
        {"-X": 0.0, "+X": None, "+Y": clearance, "-Y": clearance, "+Z": clearance, "-Z": clearance},
        {name: ["sg92r_horn"] for name in ("-X", "+Y", "-Y", "+Z", "-Z")}, maximum=1.0, coarse=0.025, tolerance=0.05)
    # 回転の遊び: 受けをサーボ軸まわりに正逆へ回す。角度はサーボ軸の角度（そのまま軸の位相誤差になる）
    plus = V.first_contact(meter, coupler, V.angular_step_x(ctx.pose["horn_coupler"], +1, 0.0, ZS), fixed, maximum=20.0, coarse=0.1)
    minus = V.first_contact(meter, coupler, V.angular_step_x(ctx.pose["horn_coupler"], -1, 0.0, ZS), fixed, maximum=20.0, coarse=0.1)
    removed = ctx.away(["sg92r_horn"], (0, 0, 1))
    plus_removed = V.first_contact(meter, coupler, V.angular_step_x(ctx.pose["horn_coupler"], +1, 0.0, ZS), removed, maximum=20.0, coarse=0.5)
    angles = [plus["travel"], minus["travel"]]
    play_ok = all(value is not None and 0.1 <= value <= 1.0 for value in angles) and plus_removed["travel"] is None
    half_play = max(value for value in angles if value is not None) if all(v is not None for v in angles) else None
    # 逆向き（180 度）・中心ずらし・裏返しを形で通さないこと。付属ホーンを動かして受けとの共通体積を測る
    rot180 = V.rot_x_np(180.0, 0.0, ZS)
    reversed_scan = {}
    for dz in np.arange(-3.0, 3.01, 0.5):
        reversed_scan[f"{dz:+.1f}"] = meter.common(horn, V.translation_np(0.0, 0.0, float(dz)) @ rot180 @ ctx.pose["sg92r_horn"],
                                                   coupler, ctx.pose["horn_coupler"])[0]
    x_mid = P.RECV_HUB_X0 * 1000.0 + 0.1 + P.SG.HORN_ARM_T * 1000.0 / 2.0
    flip = V.translation_np(x_mid, 0.0, 0.0) @ V.rot_z_np(180.0) @ V.translation_np(-x_mid, 0.0, 0.0)
    flipped = meter.common(horn, flip @ ctx.pose["sg92r_horn"], coupler, ctx.pose["horn_coupler"])[0]
    shifted = {}
    for label, (dy, dz) in {"+Y": (0.3, 0.0), "-Y": (-0.3, 0.0), "+Z": (0.0, 0.3), "-Z": (0.0, -0.3)}.items():
        shifted[label] = meter.common(horn, V.translation_np(0.0, dy, dz) @ ctx.pose["sg92r_horn"], coupler, ctx.pose["horn_coupler"])[0]
    reject_ok = (min(reversed_scan.values()) > 1.0 and flipped > 1.0 and all(value > FLOOR for value in shifted.values()))
    passed = bool(nominal <= FLOOR and all(row["pass"] for row in rows) and play_ok and reject_ok)
    return interface(
        "horn-coupler", "付属ホーンと受け（回転の伝達・向き・中心）", passed,
        (f"受けとホーンの共通体積 {nominal:.6f}mm3。径方向の初接触は設計の隙間 {clearance:.2f}mm、-X は腕の上面とポケットの天井が接する。"
         f"回転の遊び +{angles[0]}° / -{angles[1]}°（サーボ軸）。180° 逆向きの最小共通体積 {min(reversed_scan.values()):.2f}mm3、"
         f"裏返し {flipped:.2f}mm3、中心を 0.3mm ずらすと各方向で干渉。スプライン嵌合は正本に歯が無く未確認。"),
        directions=rows, angularPlay={"plusDeg": plus, "minusDeg": minus, "halfPlayDeg": half_play,
                                      "limitPerSideDeg": 1.0, "retainerRemovedPlusTravelDeg": plus_removed["travel"], "pass": bool(play_ok),
                                      "note": "初接触は共通体積が床を超えた角（面接触の偏りは 0.02° 以下）。この遊びがそのままサーボ軸の位相誤差に入り、カム軸では g 倍"},
        nominalCommonVolumeMm3=nominal,
        wrongOrientation={"rotate180AboutAxisScanMm3": reversed_scan, "rotate180MinMm3": min(reversed_scan.values()),
                          "flippedOverMm3": flipped, "centreShifted0.3mmMm3": shifted, "pass": bool(reject_ok)},
        spline={"status": "unknown", "note": "SG92R 出力軸のスプライン（歯）は正本に無い。ホーンと受けの嵌合だけを測った"})


# =============================================================================================
# 2. 受けのピンと +X 壁の溝
# =============================================================================================
def pin_interface(ctx):
    meter = ctx.meter
    coupler = ctx.solid("horn_coupler")
    members = [("horn_coupler", coupler, ctx.pose["horn_coupler"])]
    fixed = ctx.at("housing")
    region = [[44.9, -3.5, ZS - 3.5], [46.1, 3.5, ZS + 3.7]]
    radial = (P.RECV_WALL_HOLE_D - P.RECV_PIN_D) * 500.0
    axial = (P.RECV_WALL_HOLE_BOTTOM - P.RECV_PIN_X1) * 1000.0
    rows = six_directions(
        ctx, members, fixed,
        {"+X": axial, "-X": None, "+Y": radial, "-Y": radial, "-Z": radial, "+Z": None},
        {name: ["housing"] for name in ("+X", "+Y", "-Y", "-Z")}, maximum=3.0, coarse=0.05, tolerance=0.06,
        locations={name: [region] for name in ("+X", "+Y", "-Y", "-Z")})
    return interface(
        "coupler-pin-wall", "受けのピンと +X 端壁の止まり穴", rows,
        (f"ピン（径 {P.RECV_PIN_D * 1000:.0f}）と穴・降ろし溝の隙間は径方向 {radial:.2f}mm、ピンの先と穴の底は軸方向 {axial:.1f}mm。"
         "-X はピンが穴から出る向き、+Z は降ろし溝を上へ抜ける向きで接触しない（組立の向き）。"),
        directions=rows, expectedRadialMm=radial, expectedAxialMm=axial,
        note="受けを動かし、外装（housing）だけを保持相手とした。接触成分がピンと穴の位置（X 44.9..46.1）に収まること")


# =============================================================================================
# 3. 鍵（カム・歯車が鏡像・60° 回しで軸へ入らない）
# =============================================================================================
def key_interface(ctx):
    """数珠つなぎの継ぎ目ごとに、雄のスタブ（雄の部品を軸まわりに回す・鏡像にする）が雌穴へ入らないことを測る。
    正しい向きの共通体積は設計した潰しリブの量（場所は verify の joint-crush-ribs と同じ）。雄の部品は +X 向きのスタブしか穴へ入らないので、裏返しは測らない"""
    meter = ctx.meter
    rows = []
    for j in range(P.N):
        y0 = K.axis_y(j) * 1000.0
        for female, male in V.joint_seams(j):
            spec = ctx.specs[tuple(sorted((female, male)))]
            f_solid, m_solid = ctx.solid(female), ctx.solid(male)
            nominal = meter.common(m_solid, ctx.pose[male], f_solid, ctx.pose[female])[0]
            wrong = {}
            for k in range(1, 6):
                wrong[f"rotate{60 * k}"] = meter.common(m_solid, V.rot_x_np(60.0 * k, y0, ZC) @ ctx.pose[male], f_solid, ctx.pose[female])[0]
            mirrored = mirror_y(m_solid, y0, male + "_mirror")
            wrong["mirror"] = meter.common(mirrored, ctx.pose[male], f_solid, ctx.pose[female])[0]
            accepted = spec["minMm3"] <= nominal <= spec["maxMm3"]
            margin = min(wrong.values()) - nominal
            rejected = margin > 0.5
            rows.append({"axis": j, "female": female, "male": male, "correctOrientationCommonMm3": nominal,
                         "designedRibMm3": [spec["minMm3"], spec["maxMm3"]], "correctAccepted": bool(accepted),
                         "wrongOrientationCommonMm3": wrong, "wrongMinimumExcessOverCorrectMm3": margin,
                         "wrongRejected": bool(rejected), "pass": bool(accepted and rejected)})
    worst = min(row["wrongMinimumExcessOverCorrectMm3"] for row in rows)
    return interface(
        "hex-key", "継ぎ目の鍵（雄スタブの鏡像・60° おきの回しは雌穴へ入らない）", rows,
        (f"数珠つなぎの継ぎ目 {len(rows)} 個（5 軸 x 6）で、正しい向きの共通体積は設計した潰しリブの量の範囲に入る。"
         f"60°〜300° の回し・鏡像の 6 通りは正しい向きより最小で {worst:.2f}mm3 多く干渉する（スタブの切り落とし面の向きが穴の出っ張りに当たる）。"),
        parts=rows,
        note="共通体積は雄のスタブが雌穴へ入る長さの全部を含む。雄の部品の板どうしは面で接するだけなので、回しても板は干渉しない")


# =============================================================================================
# 4. 歯車の噛み合い（受けの半円歯車 38T - 中央軸 17T - 隣の軸の 17T ...）
# =============================================================================================
# U 溝の中で軸の丸が取りうる位置（軸の中心の、設計位置 Zc からのずれ [Y, Z] mm）。params から導く:
#  - 溝の底に載る: 溝の丸い底の中心は軸の中心より U_SLOT_UP 上、半径 U_SLOT_W/2。軸の丸（半径 JOURNAL_D/2）が底に載ったとき中心は Zc - U_FLOOR_CLR
#  - 上の栓まで浮く: 栓の下端と丸の上端の隙間 HOLD_GAP。中心は Zc + HOLD_GAP
#  - 溝の壁まで寄る: Y は ±(U_SLOT_W - JOURNAL_D)/2。壁が垂直になる高さは U_SLOT_UP 以上
SLOT_WALL_Y = (P.U_SLOT_W - P.JOURNAL_D) * 500.0              # 0.2
SLOT_ARC_UP = P.U_SLOT_UP * 1000.0                              # 0.15
SETTLED_Z = -(P.U_SLOT_W * 500.0 - SLOT_ARC_UP - P.JOURNAL_D * 500.0)   # -0.05
FLOAT_Z = (P.HOLD_GAP - P.U_FLOOR_CLR + P.CAP_LIFT) * 1000.0                # 軸を上へ押すと、押さえ棒の指に当たるまで（図面の位置から HOLD_GAP - U_FLOOR_CLR = 0.12）。押さえ棒は外装に座るので案内板は経由しない
POSITIONS = {
    "settled": (0.0, SETTLED_Z),
    "floated": (0.0, FLOAT_Z),
    "wall-left": (-SLOT_WALL_Y, SLOT_ARC_UP),
    "wall-right": (SLOT_WALL_Y, SLOT_ARC_UP),
    "wall-left-floated": (-SLOT_WALL_Y, FLOAT_Z),
    "wall-right-floated": (SLOT_WALL_Y, FLOAT_Z),
}
# 受けの位置の遊び: 受けはホーンの隙間 HORN_CLR の中で動く（サーボ軸は動かない）
COUPLER_PLAY = P.HORN_CLR * 1000.0
COUPLER_POSITIONS = {f"{sy}{sz}": (sy * COUPLER_PLAY, sz * COUPLER_PLAY) for sy in (-1, 0, 1) for sz in (-1, 0, 1)}
PHASE_THETAS = [90.0 + 1.6 * k for k in range(6)]       # 歯の 1 ピッチ（軸で 21.2°）を 3.6° おきに 6 点


def chain_link_specs():
    """噛み合いの 5 つの組。A = 駆動側、B = 従動側。Ma(θ) = A の姿勢、Mb(θ, v, δ) = B の姿勢（v = 位置のずれ、δ = 自分の軸まわりの余分な回転）"""
    specs = []

    def gear_matrix(j, theta, v=(0.0, 0.0), delta=0.0):
        return (V.translation_np(0.0, v[0], v[1])
                @ V.rot_x_np(K.axis_angle(theta, j) + delta, K.axis_y(j) * 1000.0, ZC))

    def sector_matrix(theta):
        return V.rot_x_np(K.servo_delta(theta), 0.0, ZS)
    specs.append({"id": "sector-2", "a": "horn_coupler", "b": "gear_2", "axisOfB": 2,
                  "ma": sector_matrix, "mb": lambda th, v, d: gear_matrix(2, th, v, d), "aPositions": COUPLER_POSITIONS})
    for a, b in ((2, 1), (1, 0), (2, 3), (3, 4)):
        specs.append({"id": f"{a}-{b}", "a": f"gear_{a}", "b": f"gear_{b}", "axisOfB": b,
                      "ma": (lambda th, a=a: gear_matrix(a, th)), "mb": (lambda th, v, d, b=b: gear_matrix(b, th, v, d)),
                      "aPositions": POSITIONS})
    return specs


def unique_vectors(positions_a, positions_b):
    """B の位置 - A の位置 の一意な集合 {(vy, vz): [(a 名, b 名), ...]}"""
    out = {}
    for name_a, (ay, az) in positions_a.items():
        for name_b, (by, bz) in positions_b.items():
            out.setdefault((round(by - ay, 4), round(bz - az, 4)), []).append((name_a, name_b))
    return out


def gear_mesh_interface(ctx):
    meter = ctx.meter
    specs = chain_link_specs()
    pitch_r = P.CHAIN_GEAR_PD * 500.0
    dense = [90.0 + 0.25 * k for k in range(-320, 321)]         # 10..170 度を 0.25 度刻み
    all_thetas = [float(t) for t in V.SERVO_DEGS]
    link_results = {}
    started = time.time()
    for spec in specs:
        solid_a, solid_b = ctx.solid(spec["a"]), ctx.solid(spec["b"])
        # (a) 設計位置（全部の軸が図面の位置）で、全サーボ角（0.25 度刻み）に食い込みが無いこと
        dense_max, dense_over = 0.0, 0
        for theta in dense:
            volume = meter.common(solid_a, spec["ma"](theta), solid_b, spec["mb"](theta, (0.0, 0.0), 0.0))[0]
            dense_max = max(dense_max, volume)
            dense_over += volume > FLOOR
        # (b) 位置のずれの組み合わせ x 6 位相: 窓（噛み合ったまま自由に回れる範囲）
        vectors = unique_vectors(spec["aPositions"], POSITIONS)
        a_cache = {theta: prepare_a(solid_a, spec["ma"](theta)) for theta in all_thetas}
        entries = []
        for (vy, vz), origins in sorted(vectors.items()):
            overlap_poses = 0
            for theta in all_thetas:
                volume = common_with_a(meter, solid_a, a_cache[theta], solid_b, spec["mb"](theta, (vy, vz), 0.0))
                overlap_poses += volume > FLOOR
            windows = []
            for theta in PHASE_THETAS:
                ma = spec["ma"](theta)
                windows.append(mesh_window(meter, solid_a, ma, solid_b, lambda d, th=theta, v=(vy, vz): spec["mb"](th, v, d),
                                           scan=4.0, coarse=0.1))
            free_all = all(w["free"] for w in windows)
            entries.append({
                "vectorYZ": [vy, vz], "originCombinations": len(origins), "examples": [list(o) for o in origins[:2]],
                "centreDistanceChangeMm": round(math.hypot(spec_center(spec)[0] + vy, spec_center(spec)[1] + vz)
                                                - math.hypot(*spec_center(spec)), 4),
                "poseCount": len(all_thetas), "posesOverlappingAtIdealPhase": overlap_poses,
                "feasible": bool(free_all),
                "windows": [{"servoDeg": th, **w} for th, w in zip(PHASE_THETAS, windows)],
                "windowLowDeg": min(w["low"] for w in windows) if free_all else None,
                "windowHighDeg": max(w["high"] for w in windows) if free_all else None})
        link_results[spec["id"]] = {"parts": [spec["a"], spec["b"]], "denseIdealMaxMm3": dense_max,
                                    "denseIdealPosesOver": dense_over, "densePoses": len(dense), "vectors": entries}
        log(f"  噛み合い {spec['id']} 完了 {time.time() - started:.0f}s ベクトル {len(entries)}")
    return link_results


def spec_center(spec):
    """A から B への中心距離のベクトル [Y, Z] mm（位置のずれの前）"""
    if spec["a"] == "horn_coupler":
        return (0.0, P.SERVO_CD * 1000.0)
    ya, yb = K.axis_y(int(spec["a"].split("_")[1])) * 1000.0, K.axis_y(int(spec["b"].split("_")[1])) * 1000.0
    return (yb - ya, 0.0)


def window_of(link, vector):
    key = (round(vector[0], 4), round(vector[1], 4))
    index = link.get("_index")
    if index is None:
        index = {tuple(entry["vectorYZ"]): entry for entry in link["vectors"]}
        link["_index"] = index
    return index[key]


def propagate(link_results, selection):
    """位置の選択（軸 j -> 位置名、受け -> 位置名）から、軸ごとの位相の誤差の区間（度）を求める。
    受けが理想の角度のとき、軸 2 の誤差は S-2 の窓。以後 eps_B = [lo - eps_A_hi, hi - eps_A_lo]（A の誤差は B の理想の角度を逆向きにずらす）。
    どれかの組が噛み合えない（窓が無い）なら None"""
    def pos(name):
        return POSITIONS[selection[name]]
    coupler = COUPLER_POSITIONS[selection["coupler"]]
    entry = window_of(link_results["sector-2"], (pos("axis2")[0] - coupler[0], pos("axis2")[1] - coupler[1]))
    if not entry["feasible"]:
        return None
    eps = {2: (entry["windowLowDeg"], entry["windowHighDeg"])}
    for a, b in ((2, 1), (1, 0), (2, 3), (3, 4)):
        link = link_results[f"{a}-{b}"]
        e = window_of(link, (pos(f"axis{b}")[0] - pos(f"axis{a}")[0], pos(f"axis{b}")[1] - pos(f"axis{a}")[1]))
        if not e["feasible"]:
            return None
        lo_a, hi_a = eps[a]
        eps[b] = (e["windowLowDeg"] - hi_a, e["windowHighDeg"] - lo_a)
    return eps


def design_terms():
    """design_check の位相誤差の項（軸の角度、度）。バックラッシュ以外は design_check と同じ式（params だけから）"""
    servo = P.SERVO_ERR_DEG * G
    vernier_step = 360.0 / (20 * 38 / math.gcd(20, 38))
    vernier = vernier_step / 2.0 * G
    joint_each, joints = P.JOINT_ERR_DEG, 1            # 継ぎ目 1 つの遊び x 継ぎ目の数（camshaft_j と gear_j の 1 か所だけ）
    joint_total = joint_each * joints
    lash_one = math.degrees(P.GEAR_LASH * 1000.0 / (P.CHAIN_GEAR_PD * 500.0))
    meshes = [3, 2, 1, 2, 3]
    chain_meshes = [2, 1, 0, 1, 2]
    # design_check の (a) 隣り合う軸の高さの差 = 床 + 栓 + 案内板の遊び。1 噛合あたり degrees(δ / R)
    delta_a = (P.U_FLOOR_CLR + P.HOLD_GAP + P.CAP_LIFT) * 1000.0       # design_check と同じ: 溝の底 + 押さえ棒の隙間 + 押さえ棒の浮き（案内板の遊びは入らない）
    ph_a = math.degrees(delta_a / (P.CHAIN_GEAR_PD * 500.0))
    # (b)+(c) 中央軸と受けの Y のずれ = U 溝の Y 隙間 + ホーンとの隙間
    ph_sector = math.degrees((P.U_SLOT_Y_CLR + P.HORN_CLR) * 1000.0 / (P.CHAIN_GEAR_PD * 500.0))
    linear = [servo + vernier + joint_total + lash_one * meshes[j] + ph_sector + ph_a * chain_meshes[j] for j in range(P.N)]
    return {"servo": servo, "vernier": vernier, "jointEach": joint_each, "joints": joints, "jointTotal": joint_total, "lashOneMesh": lash_one,
            "meshes": meshes, "phA": ph_a, "phSector": ph_sector,
            "designTotals": [servo + vernier + joint_total + lash_one * m for m in meshes],
            "designLinearTotals": linear}


def scan_positions(link_results, position_names, coupler_names, fixed_axis2=None):
    """軸 0..4 の位置（position_names の組み合わせ）と受けの位置から、噛み合える組すべての軸ごとの位相誤差の最大（度）を求める。
    fixed_axis2 を与えると軸 2 の位置をそれに固定する"""
    worst = {j: {"eps": 0.0, "selection": None, "interval": None} for j in range(P.N)}
    feasible, infeasible = 0, 0
    middle = [fixed_axis2] if fixed_axis2 else position_names
    for coupler in coupler_names:
        for p2 in middle:
            for p1, p3 in itertools.product(position_names, repeat=2):
                for p0, p4 in itertools.product(position_names, repeat=2):
                    selection = {"coupler": coupler, "axis0": p0, "axis1": p1, "axis2": p2, "axis3": p3, "axis4": p4}
                    eps = propagate(link_results, selection)
                    if eps is None:
                        infeasible += 1
                        continue
                    feasible += 1
                    for j in range(P.N):
                        magnitude = max(abs(eps[j][0]), abs(eps[j][1]))
                        if magnitude > worst[j]["eps"]:
                            worst[j] = {"eps": magnitude, "selection": selection, "interval": list(eps[j])}
    return worst, feasible, infeasible


def phase_budget(link_results, horn_half_play_deg):
    """位相誤差の合計 = サーボ + ホーン合わせ + カム嵌め + 歯車嵌め（design_check と同じ式）+ 受けとホーンの遊び x g + 歯車列の測定値。
    歯車列の項は design_check の「バックラッシュ x 噛合数」を、実 STL で測った窓の伝播に置き換える。
    判定は最大の遊び（噛み合える位置の組み合わせすべて）。重力で溝の底に沈む前提の場合を併記する"""
    terms = design_terms()
    base = terms["servo"] + terms["vernier"] + terms["jointTotal"] + horn_half_play_deg * G
    names = list(POSITIONS)
    coupler_all = list(COUPLER_POSITIONS)

    def pack(worst):
        rows = []
        for j in range(P.N):
            total = base + worst[j]["eps"]
            rows.append({"axis": j, "chainWorstDeg": worst[j]["eps"], "totalDeg": total,
                         "marginDeg": P.DWELL_HALF_DEG - total, "worstSelection": worst[j]["selection"],
                         "worstInterval": worst[j]["interval"]})
        return rows
    definitions = (
        ("gravitySettled", "全軸が溝の底（重力）、受けは中央",
         dict(position_names=["settled"], coupler_names=["00"])),
        ("gravitySettledCouplerPlay", "全軸が溝の底、受けはホーンの隙間 0.15mm の中で動く",
         dict(position_names=["settled"], coupler_names=coupler_all)),
        ("centreAxisFloated", "中央の軸だけが栓まで浮く（分離力）、他は溝の底、受けは中央",
         dict(position_names=["settled"], coupler_names=["00"], fixed_axis2="floated")),
        ("verticalFloatOnly", "各軸が溝の底か栓まで浮くかのどちらか（左右は重力で中央）、受けはホーンの隙間の中",
         dict(position_names=["settled", "floated"], coupler_names=coupler_all)),
        ("maximumPlay", "溝の中の 6 位置（底・浮く・左右の壁寄り）の全組み合わせ、受けはホーンの隙間の中（重力を仮定しない）",
         dict(position_names=names, coupler_names=coupler_all)),
    )
    scenarios = {}
    for key, label, kwargs in definitions:
        worst, feasible, infeasible = scan_positions(link_results, **kwargs)
        rows = pack(worst)
        scenarios[key] = {"label": label, "feasiblePositionTuples": feasible, "infeasiblePositionTuples": infeasible,
                          "perAxis": rows, "minimumMarginDeg": min(row["marginDeg"] for row in rows)}
    verdict = scenarios["maximumPlay"]
    return {"terms": terms, "hornHalfPlayDeg": horn_half_play_deg, "baseDeg": base, "dwellHalfDeg": P.DWELL_HALF_DEG,
            "designTotalsDeg": terms["designTotals"], "designLinearTotalsDeg": terms["designLinearTotals"],
            "differenceFromDesignLinearDeg": [row["totalDeg"] - terms["designLinearTotals"][row["axis"]] for row in verdict["perAxis"]],
            "scenarios": scenarios, "verdictScenario": "maximumPlay",
            "perAxis": verdict["perAxis"], "feasiblePositionTuples": verdict["feasiblePositionTuples"],
            "infeasiblePositionTuples": verdict["infeasiblePositionTuples"],
            "minimumMarginDeg": verdict["minimumMarginDeg"],
            "minimumMarginGravitySettledDeg": scenarios["gravitySettled"]["minimumMarginDeg"],
            "jointNote": "継ぎ目の遊び = JOINT_ERR_DEG x 1（camshaft_j と gear_j の 1 か所だけ。カムは胴と一体なのでカムごとの継ぎ目は無い）"}


# =============================================================================================
# 5. 軸の保持
# =============================================================================================
def axis_members(ctx, j):
    names = [f"camshaft_{j}", f"gear_{j}"]
    return [(name, ctx.solid(name), ctx.pose[name]) for name in names]


# 継ぎ目（camshaft_j のスタブと gear_j の雌穴）の合格基準。歯車は平歯車なので継ぎ目を引き離す軸方向の力はほぼ 0。継ぎ目が開くのは、
# 軸方向の遊び（合計 0.8）が全部そこに集まる最悪の場合だけ。そのときの残りの差し込みが JOINT_MIN_REMAINING_MM 以上、かつ停動トルクでの
# 六角の面圧（3 面が当たるとして、残りの差し込み長さで計算）が PLA の許容（降伏 35MPa の 1/3）以下。
JOINT_MIN_REMAINING_MM = 1.0
PLA_YIELD_MPA = 35.0
PLA_ALLOWABLE_MPA = PLA_YIELD_MPA / 3.0
JOINT_FACES = 3
# 軸にかかる停動トルク: 増速（サーボの歯 38 -> 軸の歯 17）なのでトルクは 1/g に下がる。依頼の「0.245Nm x 増速比」は 5 倍の過大見積りなので、
# 判定は 1/g（物理）で行い、依頼どおりの x g も参考値として併記する（どちらでも負例は fail になる）。
JOINT_TORQUE_BASIS = "divide_by_g"


def joint_pressure(remaining_mm):
    """継ぎ目の六角の面圧（MPa）。3 面が当たり、各面の力は軸の中心から AF/2 の腕で受けるとして F = T / (3 x AF/2)、面積 = 面の長さ（AF/sqrt3）x 残りの差し込み長さ。
    戻り: {pressureMpa（判定: T = 停動 / g）, pressureAtTimesGMpa（参考: T = 停動 x g）, ...}"""
    af = P.STUB_AF * 1000.0
    face_len = af / math.sqrt(3.0)
    arm = af / 2.0
    t_axis = P.SERVO_STALL_NM * 1000.0 / G                    # N mm
    t_times_g = P.SERVO_STALL_NM * 1000.0 * G
    if remaining_mm is None or remaining_mm <= 0:
        return {"pressureMpa": None, "pressureAtTimesGMpa": None, "axisTorqueNmm": t_axis, "axisTorqueTimesGNmm": t_times_g}
    area = face_len * remaining_mm
    return {"pressureMpa": t_axis / (JOINT_FACES * arm) / area, "pressureAtTimesGMpa": t_times_g / (JOINT_FACES * arm) / area,
            "axisTorqueNmm": t_axis, "axisTorqueTimesGNmm": t_times_g, "faceLengthMm": face_len, "armMm": arm}


def joint_verdict(remaining_mm):
    """残りの差し込み長さ remaining_mm の継ぎ目が基準を満たすか（0.001mm に丸めて比べる）"""
    load = joint_pressure(remaining_mm)
    ok = bool(remaining_mm is not None and round(remaining_mm, 3) >= JOINT_MIN_REMAINING_MM
              and load["pressureMpa"] is not None and load["pressureMpa"] <= PLA_ALLOWABLE_MPA)
    return {"pass": ok, **load}


def shaft_chain_engagement(ctx, j):
    """数珠つなぎの軸 j の軸方向。両端のパッドの間（肩から肩 87.2、パッド間 87.6）で、継ぎ目が開ける量の合計（余り）と、
    その余りが 1 つの継ぎ目に全部集まったときの差し込み長さの残り（基準: 1.0mm 以上かつ停動での六角の面圧が許容以下）を測る。
    余り = 歯車の部品を +X へ動かして +X のパッドに当たるまで + -X の端の部品を -X へ動かして -X のパッドに当たるまで（外装だけが相手）"""
    meter = ctx.meter
    housing = ctx.at("housing")
    gear, end = f"gear_{j}", f"camshaft_{j}"
    t_g = V.first_contact(meter, ctx.solid(gear), V.linear_step(ctx.pose[gear], (1, 0, 0)), housing, maximum=3.0, coarse=0.025)["travel"]
    t_s = V.first_contact(meter, ctx.solid(end), V.linear_step(ctx.pose[end], (-1, 0, 0)), housing, maximum=3.0, coarse=0.025)["travel"]
    slack = None if t_g is None or t_s is None else t_g + t_s

    design_pad_gap = 2 * P.PAD_X0 * 1000.0                      # 設計のパッドの内面の間
    design_slack = 2 * P.AXIAL_DRIFT * 1000.0                    # 設計の余り（片側 AXIAL_DRIFT x 2）
    seams = []
    for female, male in V.joint_seams(j):
        f_solid, m_solid = ctx.solid(female), ctx.solid(male)
        depth = float(m_solid.verts[:, 0].max() - f_solid.verts[:, 0].min())     # 雄の +X 端（スタブの先）- 雌の -X 面 = 差し込み長さ
        remaining = None if slack is None else depth - slack
        nominal = meter.common(m_solid, ctx.pose[male], f_solid, ctx.pose[female])[0]
        opened, opened_components, _ = meter.common(m_solid, V.translation_np(-(slack or 0.0), 0, 0) @ ctx.pose[male], f_solid, ctx.pose[female])
        pulled = meter.common(m_solid, V.translation_np(-(depth + 0.5), 0, 0) @ ctx.pose[male], f_solid, ctx.pose[female])[0]
        # 最悪の位置（遊びが全部集まった位置）で潰しリブがまだ当たっている長さ（成分の X の幅の平均。保持力の目安。実機未確認）
        widths = [hi[0] - lo[0] for lo, hi in opened_components]
        rib_length = float(sum(widths) / len(widths)) if widths else 0.0
        verdict = joint_verdict(remaining)
        negative = joint_verdict(0.3)                       # 負例: 残りの差し込みを 0.3mm にした形は不合格になること
        seams.append({"female": female, "male": male, "insertionMm": depth, "remainingAtFullSlackMm": remaining,
                      "ribOverlapSeatedMm3": nominal, "ribOverlapAtFullSlackMm3": opened, "ribOverlapPulledOutMm3": pulled,
                      "ribEngagedLengthAtFullSlackMm": rib_length, "ribComponentsAtFullSlack": len(widths),
                      "load": verdict, "negativeRemaining0.3mmRejected": not negative["pass"],
                      "pass": bool(verdict["pass"] and opened > FLOOR and pulled <= FLOOR and not negative["pass"])})
    return {"gearToPadMm": t_g, "endToPadMm": t_s, "slackMm": slack, "designSlackMm": design_slack, "designPadGapMm": design_pad_gap,
            "endContactParts": "camshaft の -X 端 -> 外装（パッドか溝の底かは contactBounds）", "seams": seams,
            "pass": bool(slack is not None and all(row["pass"] for row in seams))}


def shaft_retention(ctx):
    """カム軸 j（歯車・カム 5 枚・端の部品を 1 つの剛体として）を ±X/±Y/±Z へ動かし、外装と案内板との初接触を測る。
    動かす前の姿勢は図面の位置（軸の中心 = Zc、サーボ 90 度）。軸方向は継ぎ目ごとの差し込み長さの残りも測る"""
    drift = P.AXIAL_DRIFT * 1000.0
    # 図面の位置では軸の中心が丸い溝の底の中心より arc_up 下にあるので、左右の初接触は壁の隙間ではなく円弧の隙間。+X（Ø5、溝 5.4）と -X（Ø10、溝 10.6）の小さい方が先に当たる
    side_px = math.sqrt((P.U_SLOT_W * 500.0 - P.JOURNAL_D * 500.0) ** 2 - (P.U_SLOT_UP * 1000.0) ** 2)
    side_mx = math.sqrt((P.U_SLOT_MX_W * 500.0 - P.JOURNAL_MX_D * 500.0) ** 2 - (P.U_SLOT_UP_MX * 1000.0) ** 2)
    side = min(side_px, side_mx)
    up = (P.HOLD_GAP - P.U_FLOOR_CLR) * 1000.0         # 図面の位置（軸の中心 = Zc）から押さえ棒の指まで（指は溝の底に載った状態から HOLD_GAP 上）
    down = P.U_FLOOR_CLR * 1000.0
    results = []
    for j in range(P.N):
        y0 = K.axis_y(j) * 1000.0
        ends = [[[43.5, y0 - 6.5, ZC - 6.0], [46.1, y0 + 6.5, ZC + 6.0]],
                [[-46.1, y0 - 6.5, ZC - 6.0], [-43.5, y0 + 6.5, ZC + 6.0]]]
        rows = six_directions(
            ctx, axis_members(ctx, j), ctx.at("housing", "bearing_cap_px", "bearing_cap_mx", "guide_plate"),
            {"+X": drift, "-X": drift, "+Y": side, "-Y": side, "+Z": up, "-Z": down},
            {"+X": ["housing"], "-X": ["housing"], "+Y": ["housing"], "-Y": ["housing"],
             "+Z": ["bearing_cap_px", "bearing_cap_mx"], "-Z": ["housing"]},
            maximum=1.0, coarse=0.025, tolerance=0.03,
            locations={"+X": [ends[0]], "-X": [ends[1]], "+Y": ends, "-Y": ends, "+Z": ends, "-Z": ends})
        chain = shaft_chain_engagement(ctx, j)
        results.append({"axis": j, "directions": rows, "chainAxial": chain,
                        "pass": all(row["pass"] for row in rows) and chain["pass"]})
    worst = {name: [row["travelMm"] for result in results for row in result["directions"] if row["direction"] == name]
             for name in DIRS}

    def span(values):
        found = [v for v in values if v is not None]
        if not found:
            return "接触なし"
        text = f"{min(found):.3f}〜{max(found):.3f}" if len(found) == len(values) else f"{min(found):.3f}〜{max(found):.3f}（{len(values) - len(found)} 本は接触なし）"
        return text
    missing = sorted({(row["direction"], row["extendedSearch"]["reason"]) for result in results for row in result["directions"] if row.get("extendedSearch")})
    missing_text = "".join(f" {d}: {r}。" for d, r in missing)
    remaining = [seam["remainingAtFullSlackMm"] for result in results for seam in result["chainAxial"]["seams"] if seam["remainingAtFullSlackMm"] is not None] or [0.0]
    slacks = [result["chainAxial"]["slackMm"] for result in results if result["chainAxial"]["slackMm"] is not None] or [0.0]
    play = {"upMm": up, "downMm": down, "totalVerticalPlayMm": up + down}
    return interface(
        "shaft-retention", "カム軸の保持（両端のパッド・継ぎ目の差し込み・U 溝の左右・栓と溝の底）", all(result["pass"] for result in results),
        ("5 本の軸を、歯車・カム 5 枚・端の部品の剛体として動かした初接触（mm）: " +
         "、".join(f"{name} {span(values)}" for name, values in worst.items()) + "。" + missing_text +
         f"。図面の位置からの設計値は軸方向 {drift:.2f}（肩とパッド）・左右 {side:.3f}（溝の丸い底の円弧。+X {side_px:.3f}、-X {side_mx:.3f} の小さい方）・上 {up:.2f}（押さえ棒の指）・下 {down:.2f}（溝の底）。"
         f"上下の遊びの合計 {up + down:.2f}mm。"
         f"軸方向は両端のパッドで挟まれ、継ぎ目が開ける量の合計は {min(slacks):.3f}〜{max(slacks):.3f}mm。それが 1 つの継ぎ目に集まっても"
         f"差し込み長さは {min(remaining):.2f}mm 残る（基準 {JOINT_MIN_REMAINING_MM:.1f} 以上、かつ停動での六角の面圧が許容 {PLA_ALLOWABLE_MPA:.1f}MPa 以下）。"
         f"その位置の面圧 {max([sm['load']['pressureMpa'] for r_ in results for sm in r_['chainAxial']['seams'] if sm['load']['pressureMpa'] is not None] or [float('nan')]):.1f}MPa（軸の停動トルク = 0.245Nm / g、"
         f"依頼どおり x g にすると {max([sm['load']['pressureAtTimesGMpa'] for r_ in results for sm in r_['chainAxial']['seams'] if sm['load']['pressureAtTimesGMpa'] is not None] or [float('nan')]):.1f}MPa）。"
         f"潰しリブが最悪の位置でまだ当たっている長さ {min(sm['ribEngagedLengthAtFullSlackMm'] for r_ in results for sm in r_['chainAxial']['seams']):.2f}mm"
         f"（座りは {max(sm['insertionMm'] for r_ in results for sm in r_['chainAxial']['seams']):.1f}mm の穴の最後の部分。保持力の目安、実機未確認）。"
         f"負例（残り 0.3mm）は全継ぎ目で不合格になる。"),
        axes=results, directions=results[2]["directions"], verticalPlay=play,
        note=("保持相手は外装と押さえ棒（案内板も固定側に置いたが、先に当たるのは外装と押さえ棒）。回転部品どうしや画素は数えない。負例: 方向ごとの保持相手だけを退避させると接触が消える（さらに先の別の部品に当たるなら 0.1mm 以上遠い）。"
              "継ぎ目は雌穴の潰しリブの重なりが開き量の最大でも残ること、引き抜くと消えることで確かめた。潰しリブの引き抜き力は実物未確認"))


# =============================================================================================
# 5b. 軸の上向きの遊びの鎖（軸 -> 栓 -> 案内板 -> 案内板の爪 -> 外装）
# =============================================================================================
def solid_volume(solid):
    t = solid.tris
    return float(np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6.0)


def boolean_difference(solid, boxes, name):
    """solid から直方体 boxes（[[x0,y0,z0],[x1,y1,z1]]）を引いた閉じた立体（MANIFOLD）。三角形に直して返す"""
    mesh = bpy.data.meshes.new(name + "_base")
    mesh.from_pydata(solid.verts.tolist(), [], solid.faces.tolist())
    mesh.update()
    ob = bpy.data.objects.new(name + "_base", mesh)
    bpy.context.collection.objects.link(ob)
    cutters = []
    try:
        for index, (lo, hi) in enumerate(boxes):
            box = V.box_solid(f"{name}_cut{index}", lo, hi)
            cmesh = bpy.data.meshes.new(f"{name}_cut{index}")
            cmesh.from_pydata(box.verts.tolist(), [], box.faces.tolist())
            cmesh.update()
            cob = bpy.data.objects.new(f"{name}_cut{index}", cmesh)
            bpy.context.collection.objects.link(cob)
            cutters.append(cob)
            modifier = ob.modifiers.new(f"cut{index}", "BOOLEAN")
            modifier.operation = "DIFFERENCE"
            modifier.solver = "MANIFOLD"
            modifier.object = cob
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        try:
            bmesh.ops.triangulate(bm, faces=bm.faces)
            closed = all(edge.is_manifold for edge in bm.edges)
            tris = np.array([[tuple(v.co) for v in face.verts] for face in bm.faces], dtype=float)
        finally:
            bm.free()
    finally:
        for cob in cutters:
            data = cob.data
            bpy.data.objects.remove(cob, do_unlink=True)
            bpy.data.meshes.remove(data)
        data = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.meshes.remove(data)
    if not closed:
        raise ValueError(f"{name}: Boolean の結果が閉じていない")
    return V.Solid(name, tris)


def first_contact_multi(meter, members, fixed, maximum, coarse, allowed=None, refine=14):
    """members = [(名前, Solid, 基準姿勢, onset)]。t が onset を超えた分だけ +Z へ動く（軸が案内板を押し上げる経路）。
    戻り: 最初に固定側へ当たる t"""
    def hit(t):
        pairs, comps, worst = [], [], 0.0
        for name, solid, base, onset in members:
            volume, names, components = V.measure_set(meter, solid, V.translation_np(0, 0, max(0.0, t - onset)) @ base, fixed, allowed)
            for other in names:
                pairs.append((name, other))
            comps.extend(components)
            worst = max(worst, volume)
        return pairs, comps, worst
    pairs, comps, worst = hit(0.0)
    if pairs:
        return {"travel": 0.0, "pairs": pairs, "components": comps, "volume": worst}
    previous, t = 0.0, coarse
    while t <= maximum + 1e-9:
        pairs, comps, worst = hit(t)
        if pairs:
            low, high = previous, t
            for _ in range(refine):
                middle = (low + high) / 2.0
                if hit(middle)[0]:
                    high = middle
                else:
                    low = middle
            pairs, comps, worst = hit(high)
            return {"travel": round(high, 6), "pairs": pairs, "components": comps, "volume": worst}
        previous, t = t, t + coarse
    return {"travel": None, "pairs": [], "components": [], "volume": 0.0}


def tip_radius(solid, y0, z0, x_range, polar_deg=None, polar_half=40.0):
    """歯先円の半径（STL の頂点の最大半径）。polar_deg を与えると、その極角（+Y から +Z）±polar_half の頂点だけ"""
    pts = solid.verts
    m = (pts[:, 0] >= x_range[0] - 1e-6) & (pts[:, 0] <= x_range[1] + 1e-6)
    dy, dz = pts[m, 1] - y0, pts[m, 2] - z0
    if polar_deg is not None:
        ang = np.degrees(np.arctan2(dz, dy))
        diff = (ang - polar_deg + 180.0) % 360.0 - 180.0
        keep = np.abs(diff) <= polar_half
        dy, dz = dy[keep], dz[keep]
    return float(np.hypot(dy, dz).max())


CAP_LIFT_MAX_MM = P.CAP_LIFT * 1000.0   # 押さえ棒の上向きの浮きの設計値（0.05mm）。合格は設計値 + 0.01 以下


def cap_rib_regions(ctx):
    """押さえ棒の Y 端の潰しリブが外装の Y 止めのブロックと擦れる領域。座りの姿勢で棒と外装が重なる成分（設計したリブの重なり）の外接箱を、
    X ±0.02・Y ±0.03 に絞り、Z だけ ±1.0 に広げる（棒を上へ動かすとリブが面を擦って滑る）。棒の爪とブロックの下向きの段の接触はこの外にあるので数える"""
    cached = getattr(ctx, "_cap_regions", None)
    if cached is not None:
        return cached or None
    regions = []
    for name in ("bearing_cap_px", "bearing_cap_mx"):
        volume, components, _ = ctx.meter.common(ctx.solid(name), ctx.pose[name], ctx.solid("housing"), ctx.pose["housing"])
        for lo, hi in components:
            regions.append([[lo[0] - 0.02, lo[1] - 0.03, lo[2] - 1.0], [hi[0] + 0.02, hi[1] + 0.03, hi[2] + 1.0]])
    ctx._cap_regions = regions
    return regions or None


def cap_without_claws(ctx, name):
    """負例用の押さえ棒: Y の両端 1.5mm の板（潰しリブと上向きの爪を含む）を切り取った形（Boolean MANIFOLD）"""
    solid = ctx.solid(name)
    lo, hi = solid.lo, solid.hi
    boxes = [[[float(lo[0]) - 1, float(hi[1]) - 1.5, float(lo[2]) - 1], [float(hi[0]) + 1, float(hi[1]) + 1, float(hi[2]) + 1]],
             [[float(lo[0]) - 1, float(lo[1]) - 1, float(lo[2]) - 1], [float(hi[0]) + 1, float(lo[1]) + 1.5, float(hi[2]) + 1]]]
    return boolean_difference(solid, boxes, name + "_noclaw")


def upward_chain(ctx):
    """軸を上へ押したとき、軸 -> 押さえ棒 -> 外装 の順に各界面の初接触を測り、外装に当たるまでの合計を求める。案内板は経由しない。
    - 軸 -> 押さえ棒の指: 図面の位置から HOLD_GAP - U_FLOOR_CLR
    - 押さえ棒 -> 外装: 棒だけを上へ動かして最初に当たる部品が外装であること（案内板が先に当たったら不合格）
    - 合計: 軸と棒を一緒に上へ動かし（棒は軸が指に当たった後から）、外装に当たるまで。案内板を足しても同じ値のこと（案内板を経由しない）
    - 負例: 押さえ棒を外した軸は、外装・案内板に 1mm 上がるまで当たらない。外装を外すと棒は当たらない
    最後に、その持ち上がりでの歯先の重なりの残り（受け - 中央軸、軸どうし）を実 STL の歯先半径から求める"""
    meter = ctx.meter
    caps = ("bearing_cap_px", "bearing_cap_mx")
    # 界面 2: 押さえ棒 -> 外装（棒だけを上へ。外装と案内板を固定側に置き、最初に当たる部品を見る）
    cap_rows = []
    for name in caps:
        alone = V.first_contact(meter, ctx.solid(name), V.linear_step(ctx.pose[name], (0, 0, 1)), ctx.at("housing", "guide_plate"), maximum=1.0, coarse=0.01,
                                allowed=cap_rib_regions(ctx))
        gone = V.first_contact(meter, ctx.solid(name), V.linear_step(ctx.pose[name], (0, 0, 1)), ctx.away(["housing", "guide_plate"], (0, 0, 1)), maximum=1.0, coarse=0.05)
        partners = sorted(set(alone.get("parts", [])))
        # 負例: 爪（と Y 端のリブ）を切り取った棒は、同じ姿勢から上へ動かすと浮きが増える（案内板まで届く）
        noclaw = V.first_contact(meter, cap_without_claws(ctx, name), V.linear_step(ctx.pose[name], (0, 0, 1)), ctx.at("housing", "guide_plate"),
                                 maximum=1.0, coarse=0.01, allowed=cap_rib_regions(ctx))
        increase = None if alone["travel"] is None else (1.0 if noclaw["travel"] is None else noclaw["travel"] - alone["travel"])
        cap_rows.append({"cap": name, "upTravelMm": alone["travel"], "firstContactParts": partners,
                         "contactBoundsMm": bounds_of(alone["components"]), "wallsRemovedTravelMm": gone["travel"],
                         "liftLimitMm": CAP_LIFT_MAX_MM + 0.01, "clawRemovedUpTravelMm": noclaw["travel"],
                         "clawRemovedFirstContactParts": sorted(set(noclaw.get("parts", []))), "clawRemovedLiftIncreaseMm": increase,
                         "pass": bool(alone["travel"] is not None and partners == ["housing"] and gone["travel"] is None
                                      and alone["travel"] <= CAP_LIFT_MAX_MM + 0.01 and increase is not None and increase >= 0.1)})
    t2 = {row["cap"]: row["upTravelMm"] for row in cap_rows}
    rows = []
    expected_t1 = (P.HOLD_GAP - P.U_FLOOR_CLR) * 1000.0
    settled_to_nominal = P.U_FLOOR_CLR * 1000.0
    for j in range(P.N):
        members = axis_members(ctx, j)
        r1 = first_contact_group(meter, members, lambda t: V.translation_np(0, 0, t), ctx.at(*caps), maximum=1.0, coarse=0.01)
        t1 = r1["travel"]
        onset = t1 if t1 is not None else 0.0
        cap_members = [(n, ctx.solid(n), ctx.pose[n], onset) for n in caps]
        multi = [(n, s_, b, 0.0) for n, s_, b in members] + cap_members
        total = first_contact_multi(meter, multi, ctx.at("housing"), maximum=1.0, coarse=0.01, allowed=cap_rib_regions(ctx))
        with_plate = first_contact_multi(meter, multi, ctx.at("housing", "guide_plate"), maximum=1.0, coarse=0.01, allowed=cap_rib_regions(ctx))
        no_caps = first_contact_multi(meter, [(n, s_, b, 0.0) for n, s_, b in members], ctx.at("housing", "guide_plate"), maximum=1.0, coarse=0.05)
        housing_gone = first_contact_multi(meter, multi, ctx.away(["housing"], (0, 0, 1)), maximum=1.0, coarse=0.05, allowed=cap_rib_regions(ctx))
        t_total = total["travel"]
        # 押さえ棒の上の止まりが外装ではなく案内板のとき（形が「案内板を経由しない」になっていない）: 案内板も一緒に押し上げる経路を測る
        # （軸 -> 棒 -> 案内板 -> 案内板の爪 -> 外装）。数値は報告し、判定は「経由しない」を満たさないので不合格のまま
        via_plate = None
        cap_plate = [row_["upTravelMm"] for row_ in cap_rows if row_["firstContactParts"] == ["guide_plate"]]
        if t_total is None and cap_plate and t1 is not None:
            plate_member = [("guide_plate", ctx.solid("guide_plate"), ctx.pose["guide_plate"], t1 + min(cap_plate))]
            via_plate = first_contact_multi(meter, multi + plate_member, ctx.at("housing"), maximum=1.5, coarse=0.01, allowed=cap_rib_regions(ctx))["travel"]
        expected_total = None if None in t2.values() or t1 is None else t1 + min(t2.values())
        ok = bool(t1 is not None and abs(t1 - expected_t1) <= 0.03 and t_total is not None and expected_total is not None
                  and abs(t_total - expected_total) <= 0.02
                  and with_plate["travel"] is not None and abs(with_plate["travel"] - t_total) <= 0.005
                  and (no_caps["travel"] is None or no_caps["travel"] >= t_total + 0.1) and housing_gone["travel"] is None)
        rows.append({"axis": j, "shaftToCapMm": t1, "capToHousingMm": t2, "totalFromDrawingPositionMm": t_total,
                     "totalFromSettledMm": None if t_total is None else t_total + settled_to_nominal,
                     "viaGuidePlateTotalMm": via_plate,
                     "firstContactPairsTotal": sorted({f"{a}|{b}" for a, b in total["pairs"]}),
                     "contactBoundsMm": bounds_of(total["components"]),
                     "withGuidePlateAddedTotalMm": with_plate["travel"],
                     "capsRemovedTotalMm": no_caps["travel"], "housingRemovedTotalMm": housing_gone["travel"], "pass": ok})
    # 浮きでの歯先の重なりの残り
    sector = ctx.solid("horn_coupler")
    r_sector = tip_radius(sector, 0.0, ZS, (P.RECV_X0 * 1000.0, P.RECV_X0 * 1000.0 + P.RECV_GEAR_T * 1000.0), polar_deg=90.0)
    r_gear = [tip_radius(ctx.solid(f"gear_{j}"), K.axis_y(j) * 1000.0, ZC, (P.GEAR_X0 * 1000.0, P.GEAR_X1 * 1000.0)) for j in range(P.N)]
    lift = max(((row["totalFromDrawingPositionMm"] if row["totalFromDrawingPositionMm"] is not None else row["viaGuidePlateTotalMm"]) or 0.0) for row in rows)       # 図面の位置から外装に当たるまでの最大の持ち上がり
    coupler_down = P.HORN_CLR * 1000.0
    y_play = 2 * P.U_SLOT_Y_CLR * 1000.0
    cd_sector = math.hypot(P.U_SLOT_Y_CLR * 1000.0 + P.HORN_CLR * 1000.0, P.SERVO_CD * 1000.0 + lift + coupler_down)
    remaining_sector = r_sector + r_gear[2] - cd_sector
    remaining_chain = []
    for a, b in ((2, 1), (1, 0), (2, 3), (3, 4)):
        cd = math.hypot(17.0 + y_play, lift + P.U_FLOOR_CLR * 1000.0)
        remaining_chain.append({"pair": f"{a}-{b}", "remainingMm": r_gear[a] + r_gear[b] - cd})
    remaining = min([remaining_sector] + [item["remainingMm"] for item in remaining_chain])
    tooth_ok = remaining >= 0.6
    passed = bool(all(row["pass"] for row in cap_rows) and all(row["pass"] for row in rows) and tooth_ok)
    totals = [row["totalFromDrawingPositionMm"] for row in rows if row["totalFromDrawingPositionMm"] is not None]
    via_totals = [row["viaGuidePlateTotalMm"] for row in rows if row["viaGuidePlateTotalMm"] is not None]
    t1s = [row["shaftToCapMm"] for row in rows if row["shaftToCapMm"] is not None]
    no_caps_text = "、".join(str(row["capsRemovedTotalMm"]) if row["capsRemovedTotalMm"] is not None else "接触なし" for row in rows[:1])
    cap_text = "、".join(
        "{} が {}mm で {}".format(row["cap"], row["upTravelMm"] if row["upTravelMm"] is not None else "当たらない",
                                  "/".join(row["firstContactParts"]) or "接触なし") for row in cap_rows)
    claw_text = "、".join(
        "{} は爪を切り取ると {}mm（浮きが {} 増える）".format(row["cap"], row["clawRemovedUpTravelMm"] if row["clawRemovedUpTravelMm"] is not None else "当たらない",
                                                        "%.3f" % row["clawRemovedLiftIncreaseMm"] if row["clawRemovedLiftIncreaseMm"] is not None else "-") for row in cap_rows)
    head = (f"軸を上へ押すと、押さえ棒の指に当たるまで {min(t1s):.3f}〜{max(t1s):.3f}mm（設計 {expected_t1:.2f}）。" if t1s
            else "軸が押さえ棒に当たらない。")
    total_text = (f"軸が棒を押し上げて外装に当たるまでの合計 {min(totals):.3f}〜{max(totals):.3f}mm（図面の位置から。溝の底からは +{settled_to_nominal:.2f}）。"
                  if totals else
                  ("棒の上の止まりは外装ではなく案内板（案内板を経由しない形になっていない）。案内板も押し上げて外装の爪に当たるまでの合計 "
                   f"{min(via_totals):.3f}〜{max(via_totals):.3f}mm（図面の位置から。溝の底からは +{settled_to_nominal:.2f}）。" if via_totals else "合計は測れなかった。"))
    detail = (head + "押さえ棒は " + cap_text + f"（浮きの上限 {CAP_LIFT_MAX_MM:.2f}）。" + claw_text + "。" + total_text + f"押さえ棒を外すと {no_caps_text}、外装を外すと接触なし。"
              f"その持ち上がり {lift:.2f}mm での歯先の重なりの残り: 受け-中央軸 {remaining_sector:.2f}mm、軸どうし {min(i['remainingMm'] for i in remaining_chain):.2f}mm"
              f"（基準 0.6 以上、歯先半径 受け {r_sector:.2f}・歯車 {min(r_gear):.2f}〜{max(r_gear):.2f}）。")
    return interface(
        "axis-upward-chain", "軸の上向きの遊びの鎖（軸 -> 押さえ棒 -> 外装。案内板は経由しない）", passed, detail,
        axes=rows, caps=cap_rows,
        toothOverlap={"sectorTipRadiusMm": r_sector, "gearTipRadiiMm": r_gear, "liftMm": lift, "couplerDownMm": coupler_down,
                      "remainingSectorMm": remaining_sector, "remainingChain": remaining_chain, "limitMm": 0.6, "pass": bool(tooth_ok)},
        note=("案内板を固定側に足しても合計が変わらないこと（案内板を経由しない）を確かめた。歯先の重なりの残りは、歯先半径の和 - 中心距離"
              "（浮き・受けの沈み・U 溝の Y の遊びを同時に最大に取る）。押さえ棒の圧入の保持力は実物未確認"))


# =============================================================================================
# 6. サーボ本体の保持（柵・奥の壁・受け台・クリップ）
# =============================================================================================
def servo_retention(ctx):
    clip_up = 0.2          # クリップの上の板と耳の上端の隙間（parts_static.CLIP_CLR）
    fence_gap = 0.25       # 耳と柵の片側の隙間（parts_static.EAR_GAP。C1 と同じ。潰しリブは無い）
    wall_gap = P.SERVO_CLR * 1000.0
    members = [("sg92r", ctx.solid("sg92r"), ctx.pose["sg92r"])]
    fixed = ctx.at("housing", "servo_clip_0", "servo_clip_1")
    rows = six_directions(
        ctx, members, fixed,
        {"+X": fence_gap, "-X": fence_gap, "+Y": wall_gap, "-Y": wall_gap, "+Z": clip_up, "-Z": 0.0},
        {"+X": ["housing"], "-X": ["housing"], "+Y": ["housing"], "-Y": ["housing"],
         "+Z": ["servo_clip_0", "servo_clip_1"], "-Z": ["housing"]},
        maximum=1.0, coarse=0.025, allowed=None, tolerance=0.05,
        locations={"+Z": [[[21.9, -23.2, 30.0], [31.3, 13.2, 32.6]]]})
    travels = {row["direction"]: row["travelMm"] for row in rows}
    return interface(
        "servo-body-retention", "SG92R 本体の六方向保持（柵・奥の壁・受け台・クリップ）", rows,
        ("本体を ±X/±Y/±Z へ動かした初接触（mm）: " + "、".join(f"{k} {v}" for k, v in travels.items()) +
         f"。設計値は ±X {fence_gap}（耳と柵。リブ無し）・±Y {wall_gap}（奥の壁）・+Z {clip_up}（クリップ）・-Z 0（受け台に座る）。"
         "回転部（受け・ホーン）の衝突は保持に数えない。クリップ自身の保持は servo-clip-retention。"),
        directions=rows,
        note=("保持相手は外装とクリップ。耳の溝は C1 と同じ片側 0.25 で、重なりは無い。"
              "負例: 方向ごとの保持相手を外すと接触が消える（±Y は外装を外してもクリップが 0.8mm 先で受ける）"))


def servo_clip_retention(ctx):
    """押さえクリップ（印刷の U 字）自身が、外装とサーボの耳に対して六方向に止まるか。止まらない方向は不合格として報告する"""
    names = ("servo_clip_0", "servo_clip_1")
    clip_rows = {}
    for name in names:
        outward = "-Y" if name == "servo_clip_0" else "+Y"
        directions = six_directions(
            ctx, [(name, ctx.solid(name), ctx.pose[name])], ctx.at("housing", "sg92r"),
            {key: "contact" for key in DIRS}, {key: ["housing", "sg92r"] for key in DIRS},
            maximum=3.0, coarse=0.05, tolerance=0.05)
        clip_rows[name] = {"outwardDirection": outward, "directions": directions,
                           "pass": all(row["pass"] for row in directions)}
    unblocked = [f"{name} {entry['outwardDirection']}" for name, entry in clip_rows.items()
                 if any(not row["pass"] for row in entry["directions"])]
    travels = {name: {row["direction"]: row["travelMm"] for row in entry["directions"]} for name, entry in clip_rows.items()}
    detail = ("クリップを ±X/±Y/±Z へ動かした初接触（mm）: " +
              "。".join(f"{name} " + "、".join(f"{k} {v if v is not None else '止まらない'}" for k, v in values.items())
                       for name, values in travels.items()) + "。")
    if unblocked:
        detail += (f"止まらない方向: {', '.join(unblocked)}（爪の溝が奥の壁まで通っており、クリップが外向きへ滑って抜ける。"
                   "抜けるとクリップが耳を押さえる +Z の保持が失われる）。")
    return interface("servo-clip-retention", "SG92R の押さえクリップ自身の保持（爪・脚・奥の壁）",
                     all(entry["pass"] for entry in clip_rows.values()), detail,
                     clips=clip_rows,
                     note="保持相手は外装とサーボ本体（耳）。爪の着脱力は実物未確認。外向きに止まりが無いことは、クリップの Y 位置の遊びが耳を覆う範囲（耳の端から内側へ）を超えると保持が消える設計上の指摘")


# =============================================================================================
# 7. 案内板・ベゼル・画素（つば）の保持
# =============================================================================================
def guide_plate_retention(ctx):
    members = [("guide_plate", ctx.solid("guide_plate"), ctx.pose["guide_plate"])]
    fixed = ctx.at("housing", "bezel")
    side = P.PLATE_SIDE_PLAY * 1000.0
    play = P.PLATE_PLAY_Z * 1000.0
    rows = six_directions(
        ctx, members, fixed,
        {"+X": side, "-X": side, "+Y": side, "-Y": side, "-Z": 0.0, "+Z": play},
        {"+X": ["housing"], "-X": ["housing"], "+Y": ["housing"], "-Y": ["housing"], "-Z": ["housing"], "+Z": ["housing"]},
        maximum=1.0, coarse=0.025, tolerance=0.06)
    travels = {row["direction"]: row["travelMm"] for row in rows}
    return interface(
        "guide-plate-retention", "案内板の六方向保持（外装の壁・出っ張り・ベゼルの縁）", rows,
        ("案内板を動かした初接触（mm）: " + "、".join(f"{k} {v}" for k, v in travels.items()) +
         f"。設計値は ±X/±Y {side:.2f}（壁）・-Z 0（出っ張りに座る）・+Z {play:.2f}（舌の爪と端壁の窪みの天井。ベゼルを経由しない）。"),
        directions=rows, note="保持相手は外装（ベゼルも固定側に置いたが、先に当たるのは外装）。負例: 外装を外すと接触が消える（さらに先のベゼルがあれば 0.1mm 以上遠くなる）")


def bezel_retention(ctx):
    members = [("bezel", ctx.solid("bezel"), ctx.pose["bezel"])]
    fixed = ctx.at("housing", "guide_plate")
    rows = six_directions(
        ctx, members, fixed,
        {"-Z": 0.0, "+Z": "contact", "+X": "contact", "-X": "contact", "+Y": "contact", "-Y": "contact"},
        {key: ["housing", "guide_plate"] for key in ("-Z", "+Z", "+X", "-X", "+Y", "-Y")},
        maximum=2.0, coarse=0.025, tolerance=0.05)
    travels = {row["direction"]: row["travelMm"] for row in rows}
    upward = next(row for row in rows if row["direction"] == "+Z")
    return interface(
        "bezel-retention", "ベゼルの六方向保持（外装の継ぎ目・縁の爪と窪み）", rows,
        ("ベゼルを動かした初接触（mm）: " + "、".join(f"{k} {v}" for k, v in travels.items()) +
         "。-Z は外装の上端に座る（0）。+Z は縁の爪が窪みの天井に掛かる位置。爪の着脱力と壁のたわみは実物未確認。"),
        directions=rows, upwardContactBoundsMm=upward["contactComponentsBoundsMm"],
        note="保持相手は外装と案内板")


def pixel_retention(ctx):
    """画素 25 個の保持。左右は案内板の角穴・十字溝とベゼルの窓、上はつばとベゼルの窓の縁、下は自分のカム"""
    rows = []
    clearance = (P.HOLE_W - P.TOWER_W) * 500.0
    window = (P.WINDOW - P.HEAD) * 500.0
    flange_chamfer = (P.FLANGE_W - P.HEAD) * 500.0
    up_gap = ((P.BEZEL_Z0 * 1000.0 + V.WIN_MOUTH_IN_MM + P.WINDOW * 500.0)
              - (P.FLANGE_TOP_FLUSH * 1000.0 - flange_chamfer + P.FLANGE_W * 500.0))     # 面一の画素の上への初接触
    for j in range(P.N):
        for i in range(P.N):
            name = f"pixel_{i}_{j}"
            members = [(name, ctx.solid(name), ctx.pose[name])]
            lateral = six_directions(
                ctx, members, ctx.at("guide_plate", "bezel"),
                {"+X": clearance, "-X": clearance, "+Y": clearance, "-Y": clearance},
                {key: ["guide_plate", "bezel"] for key in ("+X", "-X", "+Y", "-Y")},
                maximum=0.6, coarse=0.025, tolerance=0.05, only=("+X", "-X", "+Y", "-Y"))
            up = six_directions(ctx, members, ctx.at("bezel"), {"+Z": up_gap}, {"+Z": ["bezel"]},
                                maximum=6.0, coarse=0.1, tolerance=0.05, only=("+Z",))
            down = six_directions(ctx, members, ctx.at(f"camshaft_{j}"), {"-Z": 0.0}, {"-Z": [f"camshaft_{j}"]},
                                  maximum=1.0, coarse=0.05, tolerance=0.05, only=("-Z",))
            directions = lateral + up + down
            rows.append({"pixel": name, "directions": directions, "pass": all(row["pass"] for row in directions)})
    firsts = [row["travelMm"] for entry in rows for row in entry["directions"] if row["direction"] in ("+X", "-X", "+Y", "-Y")]
    return interface(
        "pixel-guides", "画素の保持（案内板の角穴・十字溝、ベゼルの窓、つばとベゼル、足とカム）", all(entry["pass"] for entry in rows),
        (f"25 個の画素を面一の姿勢で動かした初接触: ±X/±Y は {min(firsts):.3f}〜{max(firsts):.3f}mm（設計値 {clearance:.2f}mm、茎と角穴の隙間。頭と窓の隙間 {window:.2f}mm より先に止まる）、"
         f"+Z はつばの面取りとベゼルの窓の面取りが当たる {up_gap:.1f}mm（+3 の姿勢からは {up_gap - P.H_MAX * 1000.0:.1f}mm。平らな面どうしの設計値より広い）、-Z は自分のカムに座る 0mm。"),
        pixels=rows, note="保持相手は案内板・ベゼル・自分のカム。+3 / -3 の隙間は verify_report の pixelLimits")


# =============================================================================================
# 8. 配線の出口（3 ピンコネクタが組立経路で窓を通る）
# =============================================================================================
def wire_exit(ctx):
    meter = ctx.meter
    window_x = P.SERVO_BODY_X0 * 1000.0 + P.SG.WIRE_EXIT_Z * 1000.0
    window_width = P.WIRE_WIN_W * 1000.0
    window_height = P.WIRE_WIN_H * 1000.0
    straight = window_height                           # 窓の垂直な辺の高さ（parts_static.WIN_SIDE_H = WIRE_WIN_H）。その上は 45 度の尖り屋根
    cw, ct, cl = P.CONNECTOR_W * 1000.0, P.CONNECTOR_T * 1000.0, P.CONNECTOR_L * 1000.0
    z_low = ZS - window_height / 2.0
    centre_z = z_low + straight / 2.0
    wire_end_y = 14.5                                  # 正本 SG92R の配線の先
    fixed = ctx.at("housing", "sg92r", "servo_clip_0", "servo_clip_1")
    y_starts = np.arange(wire_end_y, 56.0, 0.25)

    def path_clear(width, thickness, length=None, stop_at_first=True):
        length = cl if length is None else length
        solid = V.box_solid("connector_probe", (window_x - width / 2, 0.0, centre_z - thickness / 2),
                            (window_x + width / 2, length, centre_z + thickness / 2))
        blocked = []
        for y in y_starts:
            volume, names, comps = V.measure_set(meter, solid, V.translation_np(0.0, float(y), 0.0), fixed)
            if names:
                blocked.append({"yStartMm": float(y), "parts": names, "volumeMm3": volume,
                                "componentsMm": bounds_of(comps)})
                if stop_at_first:
                    break
        return blocked
    connector = path_clear(cw, ct)
    wide = path_clear(window_width + 0.4, ct)
    thick = path_clear(cw, straight + 0.3)

    def largest(measure, lower, upper):
        low, high = lower, upper
        for _ in range(12):
            middle = (low + high) / 2.0
            if path_clear(*measure(middle)):
                high = middle
            else:
                low = middle
        return low
    max_width = largest(lambda w: (w, ct), cw, window_width + 1.0)
    max_thickness = largest(lambda t: (cw, t), ct, straight + 1.0)
    passed = bool(not connector and wide and thick and max_width >= cw + 0.1 and max_thickness >= ct + 0.1)
    return interface(
        "wire-exit", f"配線の出口（3 ピンコネクタの箱 {cw:g} x {ct:g}mm が窓を通る）", passed,
        (f"コネクタ近似の箱（幅 {cw:g}・厚み {ct:g}・長さ {cl:g}）を配線の先（Y {wire_end_y}）から外へ 0.25mm 刻みで通すと、外装・サーボ・クリップに当たらない。"
         f"通る最大の幅は {max_width:.2f}mm（窓 {window_width:.1f}）、最大の厚みは {max_thickness:.2f}mm（垂直な辺 {straight:.1f}）。"
         f"幅 {window_width + 0.4:.1f} と厚み {straight + 0.3:.1f} の負例は窓に当たる。"),
        connectorPathBlocked=connector, widerNegative=wide[:1], thickerNegative=thick[:1],
        maximumPassingWidthMm=max_width, maximumPassingThicknessMm=max_thickness,
        probe={"widthMm": cw, "thicknessMm": ct, "lengthMm": cl, "centreXMm": window_x, "centreZMm": centre_z},
        note=f"コネクタの寸法 {cw:g}x{ct:g}x{cl:g} は params.CONNECTOR_*（JR / Futaba 形 3 ピンの大きめの近似。実物未計測）。配線の曲げ・被覆の剛性は未確認")


# =============================================================================================
# 本体
# =============================================================================================
def main():
    started = time.time()
    ctx = Ctx()
    specs = V.designed_overlaps(ctx.scene)
    ctx.specs = specs
    log("校正")
    calibration = calibration_rows(ctx)
    if not all(row["pass"] for row in calibration):
        failed = [row["id"] for row in calibration if not row["pass"]]
        report = {"version": 1, "model": "tangible-pixel-cube", "calibration": calibration, "interfaces": [],
                  "overall": {"geometryPass": False, "physicalStatus": "fail", "basis": "計器の校正に失敗: " + ", ".join(failed)}}
        V.write_json(V.BUILD / "drive_report.json", report)
        raise SystemExit("calibration failed before prototype STL inspection: " + ", ".join(failed))
    stl_paths = [V.BUILD / f"{name}.stl" for name in ctx.scene.names]
    start_hashes = V.source_hashes(stl_paths)
    interfaces = []
    log("ホーンと受け")
    horn = horn_interface(ctx)
    interfaces.append(horn)
    log("受けのピン")
    interfaces.append(pin_interface(ctx))
    log("鍵")
    interfaces.append(key_interface(ctx))
    log("歯車の噛み合い")
    links = gear_mesh_interface(ctx)
    half_play = horn["angularPlay"]["halfPlayDeg"] or 0.0
    budget = phase_budget(links, half_play)
    gear_slot = len(interfaces)
    log("軸の保持")
    interfaces.append(shaft_retention(ctx))
    log("軸の上向きの遊びの鎖")
    chain = upward_chain(ctx)
    interfaces.append(chain)
    log("停止時の高さの誤差")
    shift_up = max((row["totalFromDrawingPositionMm"] if row["totalFromDrawingPositionMm"] is not None else (row["viaGuidePlateTotalMm"] or 0.0))
                   for row in chain["axes"])
    shift_down = P.U_FLOOR_CLR * 1000.0
    stop = stop_height_error(ctx, budget, shift_up, shift_down)
    stop_doubled = stop_height_error(ctx, budget, shift_up, shift_down, factor=2.0)
    interfaces.insert(gear_slot, gear_interface_entry(links, budget, stop, stop_doubled))
    log("サーボの保持")
    interfaces.append(servo_retention(ctx))
    interfaces.append(servo_clip_retention(ctx))
    log("案内板・ベゼル・画素")
    interfaces.append(guide_plate_retention(ctx))
    interfaces.append(bezel_retention(ctx))
    interfaces.append(pixel_retention(ctx))
    log("配線の出口")
    interfaces.append(wire_exit(ctx))
    interfaces.append({"id": "horn-spline", "label": "SG92R 出力スプラインと付属ホーンの嵌合", "status": "unknown",
                       "detail": "正本の SG92R にスプライン（歯）が無いので、嵌合の形と回転の伝達は実物でしか確かめられない。ホーンと受けの嵌合は horn-coupler で測った。"})
    end_hashes = V.source_hashes(stl_paths)
    integrity = {"pass": start_hashes == end_hashes, "files": len(start_hashes)}
    geometry_pass = all(item["status"] in ("pass", "unknown") for item in interfaces) and integrity["pass"]
    failed = [item["id"] for item in interfaces if item["status"] == "fail"]
    report = {
        "version": 1, "model": "tangible-pixel-cube",
        "calibration": calibration,
        "interfaces": interfaces,
        "overall": {"geometryPass": geometry_pass, "physicalStatus": "conditional" if geometry_pass else "fail",
                    "basis": "実 STL の MANIFOLD 共通体積（床 0.001mm3）による初接触と保持。実機合格ではない。",
                    "failedInterfaces": failed, "elapsedSeconds": round(time.time() - started, 1),
                    "booleanCalls": ctx.meter.stats["boolean"]},
        "phaseBudget": budget,
        "computedByGeometry": [
            "ホーンと受けの嵌合（径方向・軸方向・回転の遊び・逆向きと中心ずらしの拒否）",
            "受けのピンと壁の止まり穴", "カム・歯車の鍵（鏡像・60° おきの回し・裏返し）",
            "歯車の噛み合い（設計位置の全サーボ角、U 溝の中の位置のずれの組み合わせ、バックラッシュと位相の窓）",
            "軸・サーボ本体・案内板・ベゼル・画素の保持（初接触と、保持相手を外した負例）", "配線の出口"],
        "hardwareUnknown": [
            "SG92R スプラインとホーンの実際の嵌合と回転伝達", "印刷収縮・面粗さによる隙間の増減と摩擦",
            "潰しリブの実際の潰れ代と回転ガタ（位相誤差の見積りは仮定）", "クリップ・ベゼルの爪の着脱力と繰り返し寿命",
            "歯車の実際のバックラッシュ（印刷の歯形誤差）", "配線の曲げ・コネクタの実寸"],
        "sourceIntegrity": integrity,
        "sourceHashes": V.source_hashes([HERE / name for name in ("params.py", "kinematics.py", "drive.py", "verify.py")]
                                       + [V.BUILD / "manifest.json", V.BUILD / "motion.json",
                                          ROOT / "models/sg92r-photo/params.py"]) | end_hashes,
    }
    V.write_json(V.BUILD / "drive_report.json", report)
    log(json.dumps({"geometryPass": geometry_pass, "interfaces": {item["id"]: item["status"] for item in interfaces},
                    "minimumPhaseMarginDeg": budget["minimumMarginDeg"], "stopHeightErrorMm": stop["maximumErrorMm"], "elapsed": round(time.time() - started, 1)},
                   ensure_ascii=False))
    if not geometry_pass:
        raise SystemExit(1)


def phase_propagation_calibration():
    """位相誤差の区間の伝播（propagate）を、答えの分かる窓で確かめる。
    対称な窓 [-b, +b] なら軸 2/1/0 の誤差は ±b/±2b/±3b、片側の窓 [0.5, 1.0] なら軸 2 = [0.5, 1.0]、軸 1 = [-0.5, 0.5]、軸 0 = [0, 1.5]"""
    def fake(lo, hi):
        links = {}
        for link_id, positions in (("sector-2", COUPLER_POSITIONS), ("2-1", POSITIONS), ("1-0", POSITIONS), ("2-3", POSITIONS), ("3-4", POSITIONS)):
            vectors = unique_vectors(positions, POSITIONS)
            links[link_id] = {"parts": [link_id], "vectors": [
                {"vectorYZ": list(vector), "feasible": True, "windowLowDeg": lo, "windowHighDeg": hi} for vector in vectors]}
        return links
    selection = {"coupler": "00", "axis0": "settled", "axis1": "settled", "axis2": "settled", "axis3": "settled", "axis4": "settled"}
    b = 0.4
    symmetric = propagate(fake(-b, b), selection)
    one_sided = propagate(fake(0.5, 1.0), selection)
    expected_sym = {2: (-b, b), 1: (-2 * b, 2 * b), 0: (-3 * b, 3 * b), 3: (-2 * b, 2 * b), 4: (-3 * b, 3 * b)}
    expected_one = {2: (0.5, 1.0), 1: (-0.5, 0.5), 0: (0.0, 1.5), 3: (-0.5, 0.5), 4: (0.0, 1.5)}
    ok_sym = all(abs(symmetric[j][0] - expected_sym[j][0]) < 1e-9 and abs(symmetric[j][1] - expected_sym[j][1]) < 1e-9 for j in expected_sym)
    ok_one = all(abs(one_sided[j][0] - expected_one[j][0]) < 1e-9 and abs(one_sided[j][1] - expected_one[j][1]) < 1e-9 for j in expected_one)
    return {"id": "phase-propagation", "label": "位相誤差の区間の伝播（既知の窓で軸 2/1/0 の誤差を照合）",
            "pass": bool(ok_sym and ok_one),
            "detail": {"symmetricWindow": {str(j): list(v) for j, v in symmetric.items()}, "oneSidedWindow": {str(j): list(v) for j, v in one_sided.items()}}}


def boolean_difference_calibration():
    """直方体を引いた立体の体積が解析値に一致し、結果が閉じていること"""
    cube = V.cube_solid("cal_diff_cube", (0, 0, 0), 4.0)
    cut = [[[1.0, -1.0, -3.0], [3.0, 1.0, 3.0]]]            # 立方体の +X 側の 1..2 x 2 x 4 を取る
    result = boolean_difference(cube, cut, "cal_diff_result")
    expected = 64.0 - 1.0 * 2.0 * 4.0
    measured = solid_volume(result)
    return {"id": "boolean-difference", "label": "Boolean の差（爪を切り取る負例の作り方）の体積と閉鎖",
            "pass": bool(abs(measured - expected) < 1e-6), "detail": {"measuredMm3": measured, "expectedMm3": expected}}


def design_check_calibration():
    """このファイルで再現した design_check の線形和（位相誤差）が、design_check.json の値と一致すること"""
    summary = json.loads((V.BUILD / "design_check.json").read_text(encoding="utf-8"))["summary"]["key"]
    mine = max(design_terms()["designLinearTotals"])
    theirs = summary["phase_sum_deg"]
    return {"id": "design-check-sum", "label": "design_check の位相誤差の線形和の再現（最悪の軸）",
            "pass": bool(abs(mine - theirs) < 0.01), "detail": {"reproducedDeg": mine, "designCheckDeg": theirs}}


HEIGHT_LIMIT_MM = 0.25            # 停止時の高さの誤差の合格条件。既定の表の最小の刻み 0.5mm の半分（隣の段と見分けがつく）


def stop_height_error(ctx, budget, shift_up, shift_down, factor=1.0, scenario="maximumPlay"):
    """各画素・各表の停止角で、位相誤差 ±(factor x Δ_j)（軸 j ごと、度）の範囲に実カム STL を回したときの、足の全幅での最大の高さと表との差。
    shift_up / shift_down は軸の上下の遊びによる高さのずれ（mm、図面の位置から）。誤差の最大 = max(|差の最小| + down, |差の最大| + up)
    戻り: {perPixel[...], maximumErrorMm, phaseOnlyMaximumMm, ...}"""
    total_by_axis = {row["axis"]: row["totalDeg"] for row in budget["scenarios"][scenario]["perAxis"]}
    flush_z = P.CAM_TOP_FLUSH * 1000.0
    rows, worst = [], {"errorMm": 0.0}
    phase_only = 0.0
    for j in range(P.N):
        y0 = K.axis_y(j) * 1000.0
        for i in range(P.N):
            # カムは胴と一体（継ぎ目は camshaft_j と gear_j の 1 か所だけ）なので、位相誤差は軸ごとの予算をそのまま使う
            dj = factor * total_by_axis[j]
            offsets = np.unique(np.concatenate([np.arange(-dj, dj, 0.25), [dj], [-dj], [0.0]]))
            cam = ctx.solid(f"camshaft_{j}")
            foot = V.foot_footprint(ctx.solid(f"pixel_{i}_{j}"))
            rect = (foot["x"][0], foot["x"][1], foot["y"][0], foot["y"][1])
            overlap = (cam.tris[:, :, 0].max(axis=1) >= rect[0]) & (cam.tris[:, :, 0].min(axis=1) <= rect[1])
            sub = cam.tris[overlap]                       # 足と X が重なる三角形だけ（軸まわりの回転は X を変えない）
            for k, theta in enumerate(P.TABLE_THETA):
                phi = K.axis_angle(theta, j)
                expected = PT.TABLES[k][j][i]
                diffs = []
                for off in offsets:
                    matrix = V.rot_x_np(phi + float(off), y0, ZC)
                    tris = sub @ matrix[:3, :3].T + matrix[:3, 3]
                    diffs.append(V.top_max_in_rect(tris, rect) - flush_z - expected)
                lo, hi = min(diffs), max(diffs)
                total = max(abs(lo - shift_down), abs(hi + shift_up))
                phase = max(abs(lo), abs(hi))
                phase_only = max(phase_only, phase)
                row = {"pixel": f"pixel_{i}_{j}", "table": k, "servoDeg": theta, "expectedMm": expected,
                       "phaseDeltaDeg": dj, "heightErrorRangeMm": [lo, hi], "phaseOnlyMm": phase, "totalMm": total}
                rows.append(row)
                if total > worst["errorMm"]:
                    worst = {"errorMm": total, **row}
    return {"factor": factor, "scenario": scenario, "phaseDeltaDegByAxis": total_by_axis, "shiftUpMm": shift_up, "shiftDownMm": shift_down,
            "maximumErrorMm": worst["errorMm"], "worst": worst, "phaseOnlyMaximumMm": phase_only, "limitMm": HEIGHT_LIMIT_MM,
            "pass": bool(worst["errorMm"] <= HEIGHT_LIMIT_MM), "rows": rows}


def gear_interface_entry(links, budget, stop=None, stop_doubled=None):
    """歯車の噛み合いの判定。設計位置で食い込みなし、ずれ 0 の位置で噛み合える、停止時の高さの誤差の最大が 0.25mm 以下。
    停止区間の余裕（重力ありと最悪）は参考値"""
    problems = []
    nominal = {}
    for link_id, link in links.items():
        nominal[link_id] = {"idealPhaseOverlapPoses": link["denseIdealPosesOver"], "poses": link["densePoses"],
                            "maxCommonVolumeMm3": link["denseIdealMaxMm3"]}
        if link["denseIdealPosesOver"] or link["denseIdealMaxMm3"] > FLOOR:
            problems.append(f"{link_id}: 設計位置で {link['denseIdealPosesOver']}/{link['densePoses']} 姿勢が干渉")
        zero = window_of(link, (0.0, 0.0)) if (0.0, 0.0) in {tuple(e["vectorYZ"]) for e in link["vectors"]} else None
        if zero is not None and not zero["feasible"]:
            problems.append(f"{link_id}: ずれ 0 の位置でも噛み合えない")
    margin = budget["minimumMarginDeg"]
    if stop is None or not stop["pass"]:
        problems.append("停止時の高さの誤差の最大が " + ("未計算" if stop is None else f"{stop['maximumErrorMm']:.3f}mm で {HEIGHT_LIMIT_MM}mm を超える"))
    infeasible = [(link_id, entry["vectorYZ"]) for link_id, link in links.items() for entry in link["vectors"] if not entry["feasible"]]
    compact = {}
    for link_id, link in links.items():
        compact[link_id] = {
            "parts": link["parts"], "idealPhaseDense": nominal[link_id],
            "vectors": [{k: entry[k] for k in ("vectorYZ", "centreDistanceChangeMm", "poseCount", "posesOverlappingAtIdealPhase",
                                                "feasible", "windowLowDeg", "windowHighDeg", "originCombinations")}
                        for entry in link["vectors"]]}
    pitch_r = P.CHAIN_GEAR_PD * 500.0
    widths = [(entry["windowHighDeg"] - entry["windowLowDeg"], link_id, entry["vectorYZ"])
              for link_id, link in links.items() for entry in link["vectors"] if entry["feasible"]]
    widest = max(widths)
    chain_zero = [window_of(links[link_id], (0.0, 0.0)) for link_id in ("2-1", "1-0", "2-3", "3-4")]
    nominal_width = max(e["windowHighDeg"] - e["windowLowDeg"] for e in chain_zero)
    scenarios = budget["scenarios"]
    detail = (f"設計位置で全サーボ角（0.25° 刻み 641 姿勢）に歯の食い込みは無く、ずれ 0 の位置の遊びの窓は {nominal_width:.2f}°"
              f"（歯面で {math.radians(nominal_width) * pitch_r:.2f}mm、設計の想定 0.10mm）。"
              f"U 溝の中の位置のずれの組み合わせでは、噛み合えない組が {len(infeasible)}/{sum(len(l['vectors']) for l in links.values())} 件"
              f"（中心距離が縮む向きで歯が食い込む。歯が軸を押し戻すので到達しない）、最も広い窓 {widest[0]:.2f}°（{widest[1]}、ずれ {widest[2]}）。"
              f"位相誤差の合計の最悪（軸 0/4）と停止区間の半幅 {P.DWELL_HALF_DEG}° との余裕: "
              + "、".join(f"{scenarios[key]['label'].split('、')[0]} {scenarios[key]['minimumMarginDeg']:.2f}°"
                         for key in ("gravitySettled", "gravitySettledCouplerPlay", "centreAxisFloated", "verticalFloatOnly", "maximumPlay"))
              + f"。最大の遊びで {margin:.2f}°（参考値。以前の基準は {MARGIN_LIMIT_DEG:g}° 以上）。"
              f"判定の指標は停止時の高さの誤差の最大: {stop['maximumErrorMm']:.3f}mm（基準 {HEIGHT_LIMIT_MM}mm 以下。位相誤差だけでは {stop['phaseOnlyMaximumMm']:.3f}mm、"
              f"軸の上下の遊び -{stop['shiftDownMm']:.3f}〜+{stop['shiftUpMm']:.3f}mm を足した値）。位相誤差を 2 倍にすると "
              f"{stop_doubled['maximumErrorMm']:.3f}mm（{'不合格になる' if not stop_doubled['pass'] else '合格のまま'}）。"
              f"design_check の線形和との差（軸 0/4）: 測定の合計 {budget['perAxis'][0]['totalDeg']:.2f}° - 線形和 {budget['designLinearTotalsDeg'][0]:.2f}° = {budget['differenceFromDesignLinearDeg'][0]:+.2f}°。")
    entry = {"id": "gear-mesh", "label": "歯車の噛み合い（受けの半円歯車・中央の軸・隣の軸）と停止時の高さの誤差",
             "status": "pass" if not problems else "fail", "detail": detail, "problems": problems,
             "links": compact, "phaseBudget": budget,
             "stopHeight": {k: v for k, v in stop.items() if k != "rows"} if stop else None,
             "stopHeightDoubledPhase": {k: v for k, v in stop_doubled.items() if k != "rows"} if stop_doubled else None,
             "stopHeightRows": stop["rows"] if stop else None, "infeasibleVectors": [{"link": a, "vectorYZ": b} for a, b in infeasible],
             "assumptions": ["軸の中心の位置は U 溝の中の 6 位置（溝の底・栓まで浮く・左右の壁寄り）。壁寄りは溝の壁が垂直になる高さ（Zc+0.15）以上",
                             "受けの位置は、ホーンの隙間 0.15mm の中で Y/Z に動く（9 点）",
                             "判定は maximumPlay（重力で溝の底に戻る効果を仮定しない）。gravitySettled は重力で全軸が溝の底に沈み、受けが中央にあるときだけの値",
                             "中心距離が縮む向きの組（歯が食い込む）は歯そのものが軸を押し戻すので到達しないものとして除く。除いた後の最悪を取る",
                             "隣の軸の高さが 0.25mm 違うと、歯車の噛み合い位置が 0.25/8.5 rad = 1.7° ずれる（遊びではなく位相のずれ）。歯の接線力は軸を上下に押すので、負荷中に起こりうる",
                             "窓の区間は 6 つの歯の位相（軸で 3.6° おき）の和集合。区間の伝播は eps_B = [lo - eps_A_hi, hi - eps_A_lo]",
                             "初接触は共通体積が床 0.001mm3 を超えた角。歯の側面の線接触では侵入深さ約 0.003mm、軸の角度で 0.02° 以下"]}
    return entry


if __name__ == "__main__":
    main()
