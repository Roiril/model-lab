"""刷れるかの精査（印刷する全部品を、刷る向きで）。numpy だけで動く（Blender 不要）。

    py -3.11 models/tangible-pixel-cube/print_review.py

入力: build/manifest.json、build/<id>.stl（組立姿勢）、build/print_<id>.stl（刷る向き）。
出力: build/print_review.json

見る項目（依頼者の要件 ① きれいに刷れる ④ 実際に刷るとき薄いと揺れる）:
  0. 校正: 答えの分かる形を先に流す。外れたら本番の数字を出さずに落ちる
  1. 対応: 組立姿勢と刷る向きの三角形が同じ並びで、剛体変換（回転 + 平行移動、鏡像なし）だけで重なるか
  2. 張り出し: 水平から 45 度より寝た下向きの面（ベッド接地面と 45 度ちょうどを除く）の塊。
     組立姿勢で外から見える面に 1 つでもあれば不合格。見えない面は場所・面積・橋の長さ（10mm 以内）
  3. 立てて刷る細い形: 0.2mm の層ごとの断面の島の太さ（凸包の最小幅）と、土台から立ち上がった高さ。高さ <= 太さ x 5
  4. 肉厚: 面の内側へ打つ光線（向かいの面が反対を向くときだけ数える）。どこでも 1.2 以上、外装の見える面 2.0 以上、力を受ける部品 3.0 以上
  5. ベッド: 接地面積・重心が接地の凸包の中か・高さ / 接地の幅
  6. ベッドに接する縁で嵌め合う箇所の 0.3mm 面取り（第 1 層の膨らみ）
  7. 連結成分と非多様体

見える面の定義（組立姿勢の座標。外から見えるもの）:
  housing  外装 5 面（底 + ±X + ±Y）と外周の面取り、配線の窓・指の掛かりの壁 = 外側 1.25mm の層（|x|,|y| >= 46.75、または底）
  bezel    継ぎ目（Z=93）より上の面 = 上面・外周・面取り・窓の壁（凹んだ画素の上に見える）
  pixel    頭（つばの上: Z > 89.5）の上面と側面（凹凸で見える）
  ほか     見えない
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import print_kit as K  # noqa: E402
import print_loads as L  # noqa: E402

BUILD = os.path.join(HERE, "build")
ROOT = os.path.dirname(os.path.dirname(HERE))
MODEL = "tangible-pixel-cube"

# 合格の閾値
BRIDGE_MAX = 10.0        # 見えない面の橋の長さ（mm）
SLENDER_MAX = 5.0        # 高さ / 太さ
WALL_MIN = 1.2           # どこでも
WALL_EXTERIOR = 2.0      # 外装の見える面
WALL_LOAD = 3.0          # 力を受ける部品
CUT_NEAR = 1.3           # 切り出しの切り口からこの距離以内の標本を「切り口の縁」として別に数える（mm）
THIN_AREA_MIN = 0.5      # 肉厚の塊として数える面積（mm2）
WALL_TOL = 0.01          # 肉厚の判定の許容（メッシュの丸め・標本の位置。1.2 ちょうどを 1.2 未満に誤判定しない）
THIN_FACE_MIN = 0.2      # 肉厚を測る面の最小面積（mm2）。細長い三角形の重心が縁に寄る誤検出を避ける
CHAMFER_MIN = 0.15       # 第 1 層（z=0.1）の食い込み幅（0.3mm の 45 度面取りで約 0.2、0.25mm で 0.15）
HOLE_MATING_MAX = 40.0   # この大きさ以下の穴は何かが嵌まる穴として数える（mm）

# 組立姿勢の座標で、外から見える面
VISIBLE_OUTER = 46.75
Z_SEAM = 93.0
HEAD_BASE = 89.5


def vis_housing(c, n):
    return (np.abs(c[:, 0]) >= VISIBLE_OUTER) | (np.abs(c[:, 1]) >= VISIBLE_OUTER) | (c[:, 2] <= 0.05)


def vis_bezel(c, n):
    return c[:, 2] >= Z_SEAM + 1e-3


def vis_pixel(c, n):
    return c[:, 2] > HEAD_BASE


def vis_none(c, n):
    return np.zeros(len(c), dtype=bool)


VISIBLE = {"housing": vis_housing, "bezel": vis_bezel}

# 部品の役割（肉厚の基準を選ぶ）。load = 力・トルクを伝える。flex = しなって使う（薄くてよい）。
ROLE = {"housing": "exterior", "bezel": "exterior", "guide_plate": "guide", "shaft": "load", "gear": "load",
        "cam": "load", "pixel": "guide", "horn_coupler": "load", "shaft_clip": "flex", "servo_clip": "flex",
        "phase_comb": "jig"}


# 力を受ける部位（組立姿勢の座標）。外装は大半が外装の壁だが、次は荷重が掛かる
LOAD_REGIONS = {
    "housing": {
        "サーボ取付耳の受け（-Y 側の柵と奥の壁）": lambda a: (a[:, 0] > 23.5) & (a[:, 0] < 30.5) & (a[:, 1] > -23.5) & (a[:, 1] < -16.5) & (a[:, 2] < 28),
        "サーボ取付耳の受け（+Y 側の柵と奥の壁）": lambda a: (a[:, 0] > 23.5) & (a[:, 0] < 30.5) & (a[:, 1] > 6.5) & (a[:, 1] < 13.5) & (a[:, 2] < 28),
        "軸受け（±X 端壁と帯の U 溝まわり）": lambda a: (np.abs(a[:, 0]) > 43.7) & (np.abs(a[:, 1]) < 45.5) & (a[:, 2] > 44.0) & (a[:, 2] < 58.0),
    },
}


def family(pid):
    for key in ("shaft_clip", "servo_clip", "guide_plate", "horn_coupler", "phase_comb"):
        if pid.startswith(key) or pid == key:
            return key
    return pid.split("_")[0]


# =============================================================================================
# 1 部品の検査
# =============================================================================================
P_PARAMS = L.load_params()
EXC_ENABLED = tuple(getattr(P_PARAMS, "PRINT_EXCEPTIONS", ()))     # params.PRINT_EXCEPTIONS: 許可した例外


def exception_fns(fam, enabled, P):
    """許可した例外ごとの標本の選び方 fn(print 座標の点, 組立座標の点, 肉厚, 見える) -> 真偽。該当する部品の族だけ返す。"""
    fns = {}
    if fam == "bezel" and "bezel_bar_1.6" in enabled:
        # 窓と窓の桟。見える面の肉厚 1.55〜2.0（桟 1.6mm）。1.2 未満はここでは許さない
        fns["bezel_bar_1.6"] = lambda pts, a, th, vis: vis & (th >= 1.55) & (th < WALL_EXTERIOR - 5e-3)
    if fam == "cam" and "cam_label_engraving" in enabled:
        # +X 面（刷るとき上）の彫り: 深さ CAM_LABEL_DEPTH の帯
        top, depth = P.CAM_T * 1000.0, P.CAM_LABEL_DEPTH * 1000.0
        fns["cam_label_engraving"] = lambda pts, a, th, vis: (pts[:, 2] >= top - depth - 0.15) & (pts[:, 2] <= top + 0.05)
    if fam == "housing" and "finger_catch_1.4" in enabled:
        # 端壁の外側の指の掛かり（幅 FINGER_W 12、ベゼルの継ぎ目 Z=93 の下 1.6）の面。1.2 未満はここでは許さない
        fns["finger_catch_1.4"] = lambda pts, a, th, vis: (vis & (np.abs(a[:, 0]) >= 46.5) & (a[:, 2] >= 90.5)
                                                           & (np.abs(a[:, 1]) <= 6.5) & (th >= WALL_MIN))
    if fam in ("cam", "gear", "housing") and "crush_rib_0.6" in enabled:
        # 潰しリブ（幅 0.6）。肉厚 0.55〜0.65 の標本だけ（1.2 未満の規則に限る）
        fns["crush_rib_0.6"] = lambda pts, a, th, vis: (th >= 0.55) & (th <= 0.65)
    if fam in ("gear", "horn_coupler") and "gear_tooth_tip_1.1" in enabled:
        # m1 の歯。歯の肉厚 1.0〜1.2 の標本だけ（1.2 未満の規則に限る）
        fns["gear_tooth_tip_1.1"] = lambda pts, a, th, vis: (th >= 1.0) & (th < WALL_MIN - WALL_TOL)
    return fns


ONLY_UNDER_1_2 = ("crush_rib_0.6", "gear_tooth_tip_1.1")


def to_asm_points(points, R, t):
    return (np.asarray(points) - t) @ R           # R^T (p - t)


def bbox_asm(lo, hi, R, t):
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    a = to_asm_points(corners, R, t)
    return [[round(float(v), 1) for v in a.min(axis=0)], [round(float(v), 1) for v in a.max(axis=0)]]


def analyze(S, visible, role, R=None, t=None, with_slices=True, regions=None, exceptions=None, cut_fn=None):
    """刷る向きの Solid S（z が上）と、面ごとの見える真偽から、全項目を測る。"""
    if R is None:
        R, t = np.eye(3), np.zeros(3)
    out = {"topology": S.topology(), "volume_cm3": round(S.volume() / 1000.0, 3),
           "size_mm": [round(float(v), 2) for v in (S.hi - S.lo)]}
    out["components"] = S.component_rows()
    out["mass_pla"] = K.estimate_mass(S)
    # --- 張り出し
    oh = K.overhang_clusters(S, visible)
    for row in oh:
        row["bbox_asm_mm"] = bbox_asm(row["bbox_mm"][0], row["bbox_mm"][1], R, t)
    out["overhang"] = {
        "clusters": oh,
        "total_area_mm2": round(sum(r["area_mm2"] for r in oh), 3),
        "visible_area_mm2": round(sum(r["visible_area_mm2"] for r in oh), 3),
        "max_bridge_mm": round(max([r["bridge_width_mm"] for r in oh if r["visible_area_mm2"] == 0] + [0.0]), 2),
        "fail_visible": [r for r in oh if r["visible_area_mm2"] > 0],
        "fail_bridge": [r for r in oh if r["visible_area_mm2"] == 0 and r["bridge_width_mm"] > BRIDGE_MAX],
    }
    # --- 見える面の浅い上向き斜面（層の段）。参考値
    out["terrace_visible"] = K.terrace_faces(S, visible)
    # --- 肉厚（面を細かく割った点から内側へ光線）
    fld = K.thickness_field(S, min_face=THIN_FACE_MIN)
    th, valid, pts, w = fld["th"], fld["valid"], fld["pts"], fld["w"]
    vis_s = visible[fld["fidx"]]

    def rows_for(mask):
        rows = K.cluster_points(pts[mask], w[mask], th[mask])
        rows = [r for r in rows if r["area_mm2"] >= THIN_AREA_MIN]
        for r in rows:
            r["at_asm_mm"] = bbox_asm(r["at_mm"][0], r["at_mm"][1], R, t)
        return rows
    a_pts = to_asm_points(pts, R, t)
    exc_masks = {k: fn(pts, a_pts, th, vis_s) & valid for k, fn in (exceptions or {}).items()}
    any_exc = np.zeros(len(pts), dtype=bool)
    for m in exc_masks.values():
        any_exc |= m
    allowed = {}
    # 試し刷りの切り口（INTERSECT の面の近く）。本体に無い形なので別に数える
    cut_mask = cut_fn(pts, a_pts) if cut_fn is not None else np.zeros(len(pts), dtype=bool)
    cut_edge = {}

    def split(rule, mask):
        """mask の標本を、切り口の近く・例外として許した所・それ以外に分ける。返り値は残りの塊。"""
        if (mask & cut_mask).any():
            cut_edge[rule] = rows_for(mask & cut_mask)
        mask = mask & ~cut_mask
        use = {k: m for k, m in exc_masks.items() if rule == "under_1_2" or k not in ONLY_UNDER_1_2}
        skip = np.zeros(len(pts), dtype=bool)
        for k, m in use.items():
            skip |= m
            if (mask & m).any():
                allowed.setdefault(rule, {})[k] = rows_for(mask & m)
        return rows_for(mask & ~skip)
    out["wall"] = {"min_mm": round(float(th[valid].min()), 3) if valid.any() else None,
                   "samples": int(len(pts)), "under_1_2": split("under_1_2", valid & (th < WALL_MIN - WALL_TOL))}
    if role == "exterior":
        out["wall"]["exterior_under_2_0"] = split("exterior_under_2_0", valid & vis_s & (th < WALL_EXTERIOR - 5e-3))
        out["wall"]["exterior_min_mm"] = round(float(th[valid & vis_s].min()), 3) if (valid & vis_s).any() else None
        out["wall"]["exterior_min_excluding_exceptions_mm"] = (
            round(float(th[valid & vis_s & ~any_exc].min()), 3) if (valid & vis_s & ~any_exc).any() else None)
    load_band = valid & (th >= L.MIN_JUDGED_MM) & (th < WALL_LOAD - 5e-3)       # 1.0 未満の薄さは 1.2 の規則で別に出る
    if role == "load":
        out["wall"]["load_under_3_0"] = split("load_under_3_0", load_band)
    if regions:
        out["wall"]["load_regions"] = {}
        for name, fn in regions.items():
            m = fn(a_pts)
            sel = valid & m
            out["wall"]["load_regions"][name] = {
                "samples": int(m.sum()), "min_mm": round(float(th[sel].min()), 3) if sel.any() else None,
                "under_3_0": split("load_region", load_band & m)}
    out["wall"]["allowed"] = allowed
    out["wall"]["cut_edge"] = cut_edge
    # --- ベッド
    out["bed"] = K.bed_contact(S)
    # --- 層ごとの島（細い形）と第 1 層の面取り
    if with_slices:
        sl = K.slice_layers(S, ratio_limit=SLENDER_MAX)
        for row in sl["slender"]:
            row["span_asm_mm"] = bbox_asm([row["span_mm"][0][0], row["span_mm"][0][1], row["z_mm"]],
                                          [row["span_mm"][1][0], row["span_mm"][1][1], row["z_mm"]], R, t)
        out["slices"] = sl
        out["first_layer"] = K.first_layer_chamfer(S)
    return out


# =============================================================================================
# 校正（答えの分かる形）
# =============================================================================================
def revolve(profile_rz, n=96):
    """(r, z) の閉じた多角形を Z 軸まわりに回した閉じたメッシュ。多角形の回り向きは問わない。"""
    poly = [tuple(p) for p in profile_rz]
    area = 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))
    if area < 0:
        poly = poly[::-1]
    tris = []
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        for i in range(len(poly)):
            (r0, z0), (r1, z1) = poly[i], poly[(i + 1) % len(poly)]
            p00 = (r0 * math.cos(a0), r0 * math.sin(a0), z0)
            p01 = (r0 * math.cos(a1), r0 * math.sin(a1), z0)
            p10 = (r1 * math.cos(a0), r1 * math.sin(a0), z1)
            p11 = (r1 * math.cos(a1), r1 * math.sin(a1), z1)
            if abs(r0) < 1e-12 and abs(r1) < 1e-12:
                continue
            tris.append((p00, p10, p11))
            tris.append((p00, p11, p01))
    return np.array(tris, dtype=float)


def _fix_orientation(T):
    """体積が負なら向きを反転する（校正用の形を作る道具の向き違いを吸収）。"""
    S = K.Solid(T)
    if S.volume() < 0:
        T = T[:, ::-1, :]
    return T


def calibrate():
    cases = []

    def add(name, expect, got, ok):
        cases.append({"name": name, "expect": expect, "got": got, "pass": bool(ok)})

    allfalse = lambda T: np.zeros(len(T), dtype=bool)
    allvis = lambda T: np.ones(len(T), dtype=bool)

    def oh(T, visible=None):
        S = K.Solid(T)
        vis = allfalse(T) if visible is None else visible(T)
        return K.overhang_clusters(S, vis)

    # --- 張り出し
    tplate = K.extrude_poly([(-2.5, 0), (2.5, 0), (2.5, 20), (10, 20), (10, 22), (-10, 22), (-10, 20), (-2.5, 20)], 0, 20)
    r = oh(tplate)
    add("T 字の板の下面: 水平の張り出し 300mm2（片側 7.5 x 20 が 2 つ）", 300.0,
        round(sum(x["area_mm2"] for x in r), 2), abs(sum(x["area_mm2"] for x in r) - 300.0) < 0.5 and len(r) == 2)
    add("  その橋の幅 7.5mm", 7.5, r[0]["bridge_width_mm"] if r else None, bool(r) and abs(r[0]["bridge_width_mm"] - 7.5) < 0.3)
    r = oh(tplate, allvis)
    add("  見える面に指定すると見える面積が 300", 300.0, round(sum(x["visible_area_mm2"] for x in r), 2),
        abs(sum(x["visible_area_mm2"] for x in r) - 300.0) < 0.5)

    def wedge(deg):
        a = math.radians(deg)
        ln = 20.0
        return K.extrude_poly([(0, 0), (5, 0), (5 + ln * math.cos(a), ln * math.sin(a)),
                               (5 + ln * math.cos(a), 30), (0, 30)], 0, 10)
    for deg, expect_hit in ((45, False), (40, True), (50, False), (30, True)):
        r = oh(wedge(deg))
        got = round(sum(x["area_mm2"] for x in r), 2)
        add(f"水平から {deg} 度の下向き斜面: {'張り出しあり' if expect_hit else '0'}", "あり" if expect_hit else 0.0,
            got, (got > 1.0) if expect_hit else got == 0.0)

    def arch(span):
        return K.extrude_poly([(0, 0), (5, 0), (5, 10), (5 + span, 10), (5 + span, 0), (10 + span, 0),
                               (10 + span, 13), (0, 13)], 0, 20)
    for span in (8.0, 14.0):
        r = oh(arch(span))
        got = r[0]["bridge_width_mm"] if r else None
        add(f"橋の長さ {span}mm（脚の間の天井）", span, got, got is not None and abs(got - span) < 0.3)
    # 橋の判定（10mm 超が引っかかる）は analyze 経由
    S14 = K.Solid(arch(14.0))
    a14 = analyze(S14, allfalse(S14.T), "guide", with_slices=False)
    S8 = K.Solid(arch(8.0))
    a8 = analyze(S8, allfalse(S8.T), "guide", with_slices=False)
    add("橋 14mm は不合格に出る", "出る", len(a14["overhang"]["fail_bridge"]), len(a14["overhang"]["fail_bridge"]) == 1)
    add("橋 8mm は不合格に出ない", "出ない", len(a8["overhang"]["fail_bridge"]), len(a8["overhang"]["fail_bridge"]) == 0)

    # --- 細い柱（層ごとの島）
    def column(h):
        return K.loft([(0, (-10, 10, -10, 10)), (2, (-10, 10, -10, 10)), (2, (-2, 2, -2, 2)), (2 + h, (-2, 2, -2, 2))])
    for h, expect in ((30.0, True), (16.0, False)):
        S = K.Solid(column(h))
        a = analyze(S, allfalse(S.T), "guide")
        n = len(a["slices"]["slender"])
        add(f"4mm 角の柱 高さ {h}（比 {h / 4:.1f}）: {'引っかかる' if expect else '引っかからない'}",
            expect, n > 0, (n > 0) == expect)
        if expect and a["slices"]["slender"]:
            f = a["slices"]["slender"][0]
            add("  柱の太さ 4、高さ 30 を測る", [4.0, 30.0], [f["width_mm"], f["height_mm"]],
                abs(f["width_mm"] - 4.0) < 0.1 and abs(f["height_mm"] - 30.0) < 0.3)

    # --- 肉厚
    for t, expect_hit in ((1.0, True), (2.0, False), (0.6, True)):
        S = K.Solid(K.box_solid(0, t, 0, 20, 0, 20))
        a = analyze(S, allfalse(S.T), "guide", with_slices=False)
        got = a["wall"]["min_mm"]
        hit = bool(a["wall"]["under_1_2"])
        add(f"厚み {t}mm の板: {'引っかかる' if expect_hit else '引っかからない'}", t, got,
            hit == expect_hit and abs((got or 0) - t) < 0.05)
    for t, expect_hit in ((1.8, True), (2.4, False)):
        S = K.Solid(K.box_solid(0, t, 0, 20, 0, 20))
        a = analyze(S, allvis(S.T), "exterior", with_slices=False)
        hit = bool(a["wall"]["exterior_under_2_0"])
        add(f"外装の見える面の厚み {t}mm: {'引っかかる' if expect_hit else '引っかからない'}", t,
            a["wall"]["exterior_min_mm"], hit == expect_hit)
    S = K.Solid(K.box_solid(0, 2.4, 0, 20, 0, 20))
    a = analyze(S, allfalse(S.T), "exterior", with_slices=False)
    add("外装でも見えない面は 2.0 の基準を当てない", "出ない", len(a["wall"]["exterior_under_2_0"]),
        not a["wall"]["exterior_under_2_0"])
    S = K.Solid(K.box_solid(0, 2.4, 0, 20, 0, 20))
    a = analyze(S, allfalse(S.T), "load", with_slices=False)
    add("力を受ける部品の厚み 2.4mm は 3.0 未満に出る", "出る", len(a["wall"]["load_under_3_0"]),
        bool(a["wall"]["load_under_3_0"]))
    # 大きな壁の面の裏の溝: 重心 1 点の光線では見つからない薄い所（外装の壁の裏の窪み）
    for left, expect_hit in ((1.5, True), (2.4, False)):
        S = K.Solid(K.extrude_poly([(0, 0), (4, 0), (4, 2), (left, 2), (left, 8), (4, 8), (4, 40), (0, 40)], 0, 40))
        vis = S.n[:, 1] < -0.9
        a = analyze(S, vis, "exterior", with_slices=False)
        hit = bool(a["wall"]["exterior_under_2_0"])
        add(f"壁（4mm）の裏の溝で残りが {left}mm（溝は面の重心の外）: {'引っかかる' if expect_hit else '引っかからない'}",
            left, a["wall"]["exterior_min_mm"], hit == expect_hit and abs(a["wall"]["exterior_min_mm"] - min(left, 4.0)) < 0.05)
    # 楔（鋭い縁）: 20 度の楔は薄い、70 度の楔は薄くない（向かいの面が反対を向く条件）
    for deg, expect_hit in ((20, True), (70, False)):
        half = 6.0 * math.tan(math.radians(deg / 2.0))             # 先端の角が deg の二等辺の楔（長さ 6、奥の面は垂直）
        S = K.Solid(K.extrude_poly([(0, 0), (6, -half), (6, half)], 0, 10))
        a = analyze(S, allfalse(S.T), "guide", with_slices=False)
        add(f"先端の角 {deg} 度の楔の肉厚: {'薄い' if expect_hit else '薄くない'}", expect_hit, bool(a["wall"]["under_1_2"]),
            bool(a["wall"]["under_1_2"]) == expect_hit)

    # --- 第 1 層の面取り
    def block(ch):
        rings = [(0, (-10 + ch, 10 - ch, -10 + ch, 10 - ch)), (ch, (-10, 10, -10, 10)), (10, (-10, 10, -10, 10))] if ch \
            else [(0, (-10, 10, -10, 10)), (10, (-10, 10, -10, 10))]
        return K.loft(rings)
    for ch in (0.0, 0.3, 1.0):
        S = K.Solid(block(ch))
        rows = K.first_layer_chamfer(S)
        d = rows[0]["chamfer_mm"] if rows else None
        want = {0.0: 0.0, 0.3: 0.2, 1.0: 0.9}[ch]
        add(f"ベッド側の外周の面取り {ch}mm: {'検出' if ch else '検出しない'}（z=0.1 の食い込み {want}）", want, d,
            d is not None and abs(d - want) < 0.05)
    # 穴の面取り（ワッシャー。穴の口の 0.3mm 面取り）と、鉛直でない壁（60 度の斜面）を面取りと誤認しない
    washer = revolve([(3.45, 0), (9, 0), (9, 3), (3.45, 3)])
    washer_ch = revolve([(3.75, 0), (9, 0), (9, 3), (3.45, 3), (3.45, 0.3)])
    cone = revolve([(0, 0), (8, 0), (8 - 10 / math.tan(math.radians(60)), 10), (0, 10)])
    for name, T, kind, want in (("穴の面取りなし", washer, "hole", 0.0), ("穴に 0.3mm の面取り", washer_ch, "hole", 0.2),
                                ("60 度の斜面の外周（面取りと誤認しない）", cone, "outer", 0.0)):
        rows = [r_ for r_ in K.first_layer_chamfer(K.Solid(_fix_orientation(T))) if r_["kind"] == kind]
        d = rows[0]["chamfer_mm"] if rows else None
        add(f"{name}: z=0.1 の食い込み {want}", want, d, d is not None and abs(d - want) < 0.05)

    # --- 接地
    S = K.Solid(K.box_solid(-1, 1, -1, 1, 0, 30))
    b = K.bed_contact(S)
    add("接地 2x2mm、高さ 30 の柱は高さ / 幅 = 15", 15.0, b["height_over_caliper"], abs(b["height_over_caliper"] - 15.0) < 0.1)
    S = K.Solid(K.box_solid(-10, 10, -10, 10, 0, 10))
    b = K.bed_contact(S)
    add("接地 20x20 の箱は接地面積 400、重心が接地の内", [400.0, True], [b["contact_mm2"], b["com_over_footprint"]],
        abs(b["contact_mm2"] - 400.0) < 0.5 and b["com_over_footprint"])
    # 重心が接地の外: L 字（細い脚で立ち、重い頭が横へ出る）
    Lm = K.extrude_poly([(0, 0), (4, 0), (4, 20), (30, 20), (30, 30), (0, 30)], 0, 20)
    b = K.bed_contact(K.Solid(Lm))
    add("重心が接地の外にある形（脚 4mm に頭 30mm が載る）", False, b["com_over_footprint"], not b["com_over_footprint"])

    # --- 位相: 開いた形・対応・鏡像
    cube = K.box_solid(0, 10, 0, 10, 0, 10)
    opened = cube[1:]
    t_open = K.Solid(opened).topology()
    add("面を 1 枚抜いた形は開いた辺が出る", ">0", t_open["open_edges"], t_open["open_edges"] > 0)
    t_ok = K.Solid(cube).topology()
    add("立方体は開いた辺 0・連結 1", [0, 1], [t_ok["open_edges"], t_ok["components"]],
        t_ok["open_edges"] == 0 and t_ok["components"] == 1)
    rng = np.random.default_rng(1)
    ang = math.radians(33)
    Rz = np.array([[math.cos(ang), -math.sin(ang), 0], [math.sin(ang), math.cos(ang), 0], [0, 0, 1]])
    A = K.extrude_poly([(0, 0), (6, 0), (6, 3), (3, 3), (3, 8), (0, 8)], 0, 5)
    P = A @ Rz.T + np.array([1.0, 2.0, 3.0])
    _, _, res, dmin, _, det = K.rigid_fit(A, P)
    add("回して動かしただけの対応は残差 0", "< 1e-6", res, res < 1e-6 and dmin > 0.9999 and det > 0)
    perm = rng.permutation(len(A))
    _, _, res, dmin, _, det = K.rigid_fit(A, P[perm])
    add("三角形の並びを入れ替えると残差が出る", "> 0.1", round(res, 3), res > 0.1)
    Pm = A * np.array([1.0, -1.0, 1.0])
    _, _, res, dmin, _, det = K.rigid_fit(A, Pm)
    add("鏡像は det < 0 / 残差が出る", "det<0", round(det, 3), det < 0 or res > 0.1)

    ok = all(c["pass"] for c in cases)
    return {"ok": ok, "cases": cases}


# =============================================================================================
# 本体
# =============================================================================================
def mating_failures(part_family, first_layer):
    """ベッドに接する縁で、面取りが無い嵌め合いの縁。"""
    rows = []
    for r in first_layer:
        if r["chamfer_mm"] is None:
            continue
        mating = False
        if r["kind"] == "hole" and r["size_mm"] and max(r["size_mm"]) <= HOLE_MATING_MAX:
            mating = True
        if r["kind"] == "outer" and part_family == "pixel":
            mating = True                         # 頭（15mm）がベゼルの窓（15.4mm）へ入る
        if mating and r["chamfer_mm"] < CHAMFER_MIN:
            rows.append(r)
    return rows


def main():
    t0 = time.time()
    manifest = json.load(open(os.path.join(BUILD, "manifest.json"), encoding="utf-8"))
    print("== 校正 ==")
    cal = calibrate()
    for c in cal["cases"]:
        print(("  ok " if c["pass"] else "  NG ") + c["name"], "| 期待", c["expect"], "| 実測", c["got"])
    if not cal["ok"]:
        out = {"model": MODEL, "calibration": cal, "error": "校正に失敗したので本番の数字は出さない"}
        with open(os.path.join(BUILD, "print_review.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        raise SystemExit("校正に失敗")
    print(f"校正 {len(cal['cases'])} 件すべて期待どおり ({time.time() - t0:.1f}s)")

    parts, corr, cache = {}, {}, {}
    print_ids = [p["id"] for p in manifest["parts"] if p.get("print")]
    for pid in print_ids:
        A = K.read_stl(os.path.join(BUILD, f"{pid}.stl"))
        P = K.read_stl(os.path.join(BUILD, f"print_{pid}.stl"))
        same_n = len(A) == len(P)
        if not same_n:
            corr[pid] = {"same_triangle_count": False, "pass": False}
            continue
        R, t, resid, dmin, ratio, det = K.rigid_fit(A, P)
        corr[pid] = {"same_triangle_count": True, "triangles": int(len(A)), "max_vertex_residual_mm": round(resid, 6),
                     "min_normal_dot": round(dmin, 6), "area_ratio": [round(ratio[0], 5), round(ratio[1], 5)],
                     "det": round(det, 6),
                     "pass": bool(resid < 1e-3 and dmin > 0.9999 and det > 0 and 0.999 < ratio[0] and ratio[1] < 1.001)}
        SA = K.Solid(A, pid)
        fam = family(pid)
        vis = VISIBLE.get(fam, vis_pixel if fam == "pixel" else vis_none)(SA.c, SA.n)
        S = K.Solid(P, pid)
        key = hashlib.sha1(np.round(P, 3).tobytes() + vis.tobytes() + ROLE[fam].encode()).hexdigest()
        if key in cache:
            res = cache[key][1]
            same_as = cache[key][0]
        else:
            if S.lo[2] < -1e-3 or S.lo[2] > 1e-3:
                raise SystemExit(f"{pid}: 刷る向きの最下点が z=0 でない ({S.lo[2]})")
            res = analyze(S, vis, ROLE[fam], R, t, regions=LOAD_REGIONS.get(fam), exceptions=exception_fns(fam, EXC_ENABLED, P_PARAMS))
            res["visible_area_mm2"] = round(float(SA.area[vis].sum()), 2)
            res["visible_faces"] = int(vis.sum())
            cache[key] = (pid, res)
            same_as = None
            print(f"  {pid:14s} {time.time() - t0:6.1f}s  張り出し {res['overhang']['total_area_mm2']:8.2f}mm2"
                  f"（見える {res['overhang']['visible_area_mm2']}） 最小肉厚 {res['wall']['min_mm']}")
        entry = dict(res)
        entry["family"] = fam
        entry["role"] = ROLE[fam]
        entry["same_analysis_as"] = same_as
        entry["first_layer_mating_without_chamfer"] = mating_failures(fam, res["first_layer"])
        entry["asm_x_max_mm"] = round(float(SA.hi[0]), 3)
        parts[pid] = entry

    # --- 不合格の一覧
    fails, notes = [], []
    allowed, judged_ok = [], []
    P_ = P_PARAMS
    EXC = EXC_ENABLED
    design = json.load(open(os.path.join(BUILD, "design_check.json"), encoding="utf-8"))
    judged, judge_names = L.judgement(P_, design)
    # 肉厚 3.0mm 未満の部品ごとの応力判定の割り当て（部品に当たる項目が全部通ったときだけ許可）
    judge_for = {"gear": [judge_names["gear"]], "horn_coupler": [judge_names["horn_coupler"], "受けのホーンのポケットの壁（厚み 1.6）"],
                 "cam": [judge_names["cam"], "カムのハブ筒（軸方向）"], "shaft": [judge_names["shaft"]]}
    REGION_JUDGE = {"軸受け（±X 端壁と帯の U 溝まわり）": judge_names["housing_bearing"],
                    "サーボ取付耳の受け（-Y 側の柵と奥の壁）": judge_names["housing_fence"],
                    "サーボ取付耳の受け（+Y 側の柵と奥の壁）": judge_names["housing_fence"]}
    RULE_NAMES = {"under_1_2": "肉厚 1.2mm 未満", "exterior_under_2_0": "外装の見える面の肉厚 2.0mm 未満",
                  "load_under_3_0": "力を受ける部品の肉厚 3.0mm 未満", "load_region": "力を受ける部位の肉厚 3.0mm 未満（外装の中）"}
    def check_part(pid, p, fails, allowed, judged_ok):
        for r in p["overhang"]["fail_visible"]:
            fails.append({"rule": "見える面の張り出し", "part": pid, "value": r})
        for r in p["overhang"]["fail_bridge"]:
            fails.append({"rule": "見えない面の橋が 10mm 超", "part": pid, "value": r})
        for r in p["slices"]["slender"]:
            fails.append({"rule": "立てて刷る細い形（高さ > 太さ x 5）", "part": pid, "value": r})
        fam_ = p["family"]
        for rule_key, by_exc in p["wall"].get("allowed", {}).items():
            for ex, rows in by_exc.items():
                for r in rows:
                    allowed.append({"exception": ex, "rule": RULE_NAMES[rule_key], "part": pid, "value": r})

        def route(kind, rows, rule, region=None):
            for r in rows:
                val = dict(r, region=region) if region else r
                if (kind == "load" and fam_ in judge_for and L.worst_pass(judged, judge_for[fam_])):
                    judged_ok.append({"rule": rule, "part": pid, "value": val, "judgement": judge_for[fam_]})
                else:
                    fails.append({"rule": rule, "part": pid, "value": val})
        route("thin", p["wall"]["under_1_2"], RULE_NAMES["under_1_2"])
        route("exterior", p["wall"].get("exterior_under_2_0", []), RULE_NAMES["exterior_under_2_0"])
        route("load", p["wall"].get("load_under_3_0", []), RULE_NAMES["load_under_3_0"])
        for name, reg in p["wall"].get("load_regions", {}).items():
            for r in reg["under_3_0"]:
                val = dict(r, region=name)
                item = REGION_JUDGE.get(name)
                if item and judged[item]["pass"]:
                    judged_ok.append({"rule": RULE_NAMES["load_region"], "part": pid, "value": val, "judgement": [item]})
                else:
                    fails.append({"rule": RULE_NAMES["load_region"], "part": pid, "value": val})
        b = p["bed"]
        if not b["com_over_footprint"] or (b["height_over_caliper"] or 0) > SLENDER_MAX:
            fails.append({"rule": "接地・倒れ", "part": pid, "value": b})
        for r in p["first_layer_mating_without_chamfer"]:
            fails.append({"rule": "ベッドに接する縁の嵌め合いに 0.3mm 面取りが無い", "part": pid, "value": r})
        if p["slices"]["floating_islands"]:
            fails.append({"rule": "空中から始まる島", "part": pid, "value": p["slices"]["floating_islands"][:5]})
        t = p["topology"]
        if t["open_edges"] or t["over_edges"] or t["flipped_edges"] or t["components"] != 1:
            fails.append({"rule": "非多様体・連結成分が 1 でない", "part": pid, "value": t})
        for c in p["components"]:
            if not c["grounded"]:
                fails.append({"rule": "ベッドに接地していない成分", "part": pid, "value": c})
    for pid, p in parts.items():
        check_part(pid, p, fails, allowed, judged_ok)
    for pid, c in corr.items():
        if not c["pass"]:
            fails.append({"rule": "組立姿勢と刷る向きの三角形の対応が崩れている", "part": pid, "value": c})

    # --- 試し刷りの小片（print_trials.py が prints/tangible-pixel-cube/trial/ へ書いたもの。trial_pieces.json が目録）
    trials, trial_fails, trial_allowed, trial_judged = {}, [], [], []
    tpath = os.path.join(ROOT, "prints", "tangible-pixel-cube", "trial", "trial_pieces.json")
    if os.path.exists(tpath):
        spec = json.load(open(tpath, encoding="utf-8"))
        for name, t in spec.items():
            fam_t = family(t["src"])
            T = K.read_stl(os.path.join(ROOT, t["file"]))
            S = K.Solid(T)
            R = np.array(t["to_piece"]["R"])
            tt = np.array(t["to_piece"]["t"])
            ta = (T.reshape(-1, 3) - tt) @ R                         # 組立姿勢へ戻した三角形
            SA = K.Solid(ta.reshape(-1, 3, 3))
            cut_planes = []
            if t["box_asm_mm"] is not None:
                src_lo, src_hi = K.read_stl(os.path.join(BUILD, f"{t['src']}.stl")).reshape(-1, 3).min(0),                     K.read_stl(os.path.join(BUILD, f"{t['src']}.stl")).reshape(-1, 3).max(0)
                bx = t["box_asm_mm"]
                for ax in range(3):
                    for side, val in ((0, bx[2 * ax]), (1, bx[2 * ax + 1])):
                        if src_lo[ax] + 0.05 < val < src_hi[ax] - 0.05:        # 部品の外にある面は切っていない
                            cut_planes.append((ax, val))
            vis = VISIBLE.get(fam_t, vis_pixel if fam_t == "pixel" else vis_none)(SA.c, SA.n)
            for ax, val in cut_planes:                                  # 切り口の面そのものは見える面にしない
                on_plane = np.all(np.abs(ta.reshape(-1, 3, 3)[:, :, ax] - val) < 2e-3, axis=1)
                vis &= ~on_plane

            def cut_fn(pts, a, planes=tuple(cut_planes)):
                near = np.zeros(len(pts), dtype=bool)
                for ax, val in planes:
                    near |= np.abs(a[:, ax] - val) < CUT_NEAR
                return near
            res = analyze(S, vis, ROLE[fam_t], R, tt, regions=LOAD_REGIONS.get(fam_t),
                          exceptions=exception_fns(fam_t, EXC_ENABLED, P_PARAMS), cut_fn=cut_fn if cut_planes else None)
            res["src"], res["plate"], res["checks"], res["file"] = t["src"], t["plate"], t["checks"], t["file"]
            res["family"], res["cut_planes_asm"] = fam_t, cut_planes
            res["first_layer_mating_without_chamfer"] = mating_failures(fam_t, res["first_layer"])
            # ベッドに接する面が切り口なら、その縁は本体に無い形（嵌め合う縁ではない）。別に数える
            bottom = (S.n[:, 2] < -0.999) & (S.T[:, :, 2].max(axis=1) <= 0.05) & (S.area > 1e-9)
            if bottom.any() and cut_planes:
                ta3 = ta.reshape(-1, 3, 3)[bottom]
                if all(any(np.all(np.abs(tri[:, ax] - val) < 2e-3) for ax, val in cut_planes) for tri in ta3):
                    res["first_layer_cut_edge"] = res["first_layer_mating_without_chamfer"]
                    res["first_layer_mating_without_chamfer"] = []
            trials[name] = res
            check_part(name, res, trial_fails, trial_allowed, trial_judged)
            ce = res["wall"]["cut_edge"]
            print(f"  [試し刷り] {name:30s} {res['size_mm']} 切り口の面 {len(cut_planes)} 切り口の薄い所 {sum(len(v) for v in ce.values())}"
                  f"（最小 {min([r['min_mm'] for v in ce.values() for r in v] + [9])}）")

    summary = {"n_parts_reviewed": len(parts), "n_unique_analyses": len(cache), "n_fail_entries": len(fails),
               "n_trial_pieces": len(trials), "n_trial_fail_entries": len(trial_fails),
               "n_trial_allowed_exception_entries": len(trial_allowed), "n_trial_load_judged_ok_entries": len(trial_judged),
               "n_trial_cut_edge_entries": sum(len(v) for t in trials.values() for v in t["wall"]["cut_edge"].values()),
               "n_allowed_exception_entries": len(allowed), "n_load_judged_ok_entries": len(judged_ok), "fail_by_rule": {}}
    for f in fails:
        d = summary["fail_by_rule"].setdefault(f["rule"], [])
        if f["part"] not in d:
            d.append(f["part"])
    out = {
        "model": MODEL, "generated_by": "models/tangible-pixel-cube/print_review.py",
        "thresholds": {"overhang_deg_from_horizontal": K.OVERHANG_DEG, "bridge_max_mm": BRIDGE_MAX,
                       "slender_height_over_width": SLENDER_MAX, "wall_min_mm": WALL_MIN, "wall_exterior_mm": WALL_EXTERIOR,
                       "wall_load_mm": WALL_LOAD, "thin_area_min_mm2": THIN_AREA_MIN, "first_layer_chamfer_min_mm": CHAMFER_MIN,
                       "layer_mm": K.LAYER},
        "visible_definition": __doc__.split("見える面の定義")[1].split('"""')[0].strip(),
        "calibration": cal, "correspondence": corr, "summary": summary, "fails": fails, "parts": parts,
        "trial_pieces": trials, "trial_fails": trial_fails, "trial_allowed_exceptions": trial_allowed,
        "trial_load_judged_ok": trial_judged,
        "allowed_exceptions": allowed, "print_exceptions_enabled": list(EXC),
        "load_judgement": judged, "load_judged_ok": judged_ok,
    }
    path = os.path.join(BUILD, "print_review.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    print(f"== 完了 {time.time() - t0:.1f}s: {len(parts)} 部品、独立な解析 {len(cache)}、不合格の項目 {len(fails)} -> {path}")
    for rule, ids in summary["fail_by_rule"].items():
        print(f"  {rule}: {len(ids)} 部品 {ids[:6]}{' ...' if len(ids) > 6 else ''}")


if __name__ == "__main__":
    main()
