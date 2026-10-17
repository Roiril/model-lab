"""cams.py の校正。答えの分かる入力で生成器を確かめる。実行: py -3.11 models/tangible-pixel-cube/test_cams.py

(a) 全部 0 の表 -> 真円。h* が一定（誤差 0.01mm 以内）
(b) 1 画素だけ +3 の表を 2 枚 -> 停止区間で h* = 目標 +-0.01mm 以内（通す側）。他の画素は面一のまま
(c) 隣の表との角度差が明らかに足りない表 -> CamError（止める側）。高さの範囲外・停止区間の重なりも止める
(d) 既定の表（patterns.py）が作れて、kinematics が表のサーボ角で全画素の表どおりの高さを返す
通る側と止める側の両方が期待どおりでなければ、全体が落ちる。
"""
import math
import random
import os
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))
import params as P
import cams as C
import kinematics as K
import patterns as PT

TOL = 0.01
DW_TOL_FOR_TEST = 0.01
fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" : " + detail if detail else ""))
    if not ok:
        fails.append(name)


RB = P.CAM_RB * 1000.0

# --- (a) 全部 0 -> 真円 -----------------------------------------------------------
cam = C.build_cam([0.0] * P.K, j=2, i=2)
V = np.array(cam["vertices"])
ph = np.arange(0, 360, 0.25)
h, lat = C.support(V, ph)
rad = np.hypot(V[:, 0], V[:, 1])
check("a1 h* が一定", np.abs(h - RB).max() <= TOL, f"max|h*-{RB}| = {np.abs(h - RB).max():.5f} mm")
check("a2 半径が一定（真円）", rad.max() - rad.min() <= 2 * TOL, f"rmin {rad.min():.4f} rmax {rad.max():.4f} mm")
check("a3 接点の横ずれ 0 に近い", np.abs(lat).max() <= 0.1, f"max|e| = {np.abs(lat).max():.4f} mm")

# --- (b) 1 画素だけ +3 の表を 2 枚 --------------------------------------------------
hs_b = [0.0, 3.0, 0.0, 3.0, 0.0]
for j in (0, 1, 2, 3, 4):
    cam = C.build_cam(hs_b, j=j, i=0)
    V = np.array(cam["vertices"])
    worst = 0.0
    for k, th in enumerate(P.TABLE_THETA):
        c = K.axis_angle(th, j)
        for d in np.linspace(-P.DWELL_HALF_DEG, P.DWELL_HALF_DEG, 43):
            hh, _ = C.support(V, c + d)
            worst = max(worst, abs(float(hh[0]) - (RB + hs_b[k])))
    check(f"b 軸 {j}: +3 を 2 枚、停止区間の誤差", worst <= TOL, f"max |h* - 目標| = {worst:.5f} mm, 凸 {cam['convex']}, Rmax {cam['rmax_mm']:.3f}")
# 別の画素（面一のまま）も面一のまま
cam0 = C.build_cam([0.0] * P.K, j=2, i=4)
check("b2 隣の画素は真円のまま", cam0["rmax_mm"] - cam0["rmin_mm"] <= 2 * TOL, f"rmin {cam0['rmin_mm']:.4f} rmax {cam0['rmax_mm']:.4f}")

# --- (c) 足りない表 / 範囲外 / 重なり -> 止める -----------------------------------------
def must_fail(name, f):
    try:
        f()
    except C.CamError as e:
        check(name, True, f"CamError: {e}")
    else:
        check(name, False, "例外が出なかった（作れてしまった）")


must_fail("c1 -3 と +3 が隣の表（軸で 76 度では足りない）", lambda: C.build_cam([0.0, -3.0, 3.0, 0.0, 0.0], 1, 0))
must_fail("c2 表の間隔が狭い（サーボ 8 度 = 軸 18 度 < 2w）", lambda: C.build_cam([0.0] * 5, 1, 0, thetas=(80.0, 88.0, 96.0, 104.0, 112.0)))
must_fail("c3 高さが範囲外（+3.5）", lambda: C.build_cam([0.0, 3.5, 0.0, 0.0, 0.0], 1, 0))
must_fail("c4 端の表どうし（56 度で隣り合う）が -3 と +3", lambda: C.build_cam([-3.0, 0.0, 0.0, 0.0, 3.0], 1, 0))

# 独立の実装（Sutherland-Hodgman で半平面を順に切る）と h* が一致するか
def clip_support(cs_t, step, phis_eval):
    poly = [(-1e3, -1e3), (1e3, -1e3), (1e3, 1e3), (-1e3, 1e3)]
    for phi, tt in cs_t:
        r = math.radians(phi)
        nx, ny = math.sin(r), math.cos(r)
        out = []
        for a, b in zip(poly, poly[1:] + poly[:1]):
            da = a[0] * nx + a[1] * ny - tt
            db = b[0] * nx + b[1] * ny - tt
            if da <= 0:
                out.append(a)
            if (da < 0) != (db < 0) and da != db:
                s = da / (da - db)
                out.append((a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s))
        poly = out
    P_ = np.array(poly)
    r = np.radians(phis_eval)
    return (P_ @ np.stack([np.sin(r), np.cos(r)])).max(axis=0)


random.seed(7)
worst_diff = 0.0
for _ in range(20):
    hs = [random.choice([-1.0, 0.0, 1.0, 2.0]) for _ in range(5)]
    cam = C.build_cam(hs, 1, 0, check=False)
    centers = [K.axis_angle(th, 1) for th in P.TABLE_THETA]
    cs, rs = C._window_list(centers, [RB + h for h in hs], P.DWELL_HALF_DEG)
    phis, tt = C._upper_bound(cs, rs, P.DWELL_HALF_DEG, P.CAM_STEP_DEG)
    ev = np.arange(0, 360, 1.0)
    ref = clip_support(list(zip(phis, tt)), P.CAM_STEP_DEG, ev)
    mine, _ = C.support(np.array(cam["vertices"]), ev)
    worst_diff = max(worst_diff, float(np.abs(ref - mine).max()))
check("c5 独立の半平面クリップと h* が一致（20 組）", worst_diff <= 1e-3, f"最大差 {worst_diff:.2e} mm")
geo = C.build_cam([0.0, -3.0, 3.0, 0.0, 0.0], 1, 0, check=False)
check("c6 足りない表は事前検査なしでも停止区間か横ずれに表れる",
      geo["dwell_err_max_mm"] > DW_TOL_FOR_TEST or geo["lateral_max_mm"] > C.LATERAL_MAX_MM,
      f"dwell 誤差 {geo['dwell_err_max_mm']:.3f} mm, 横ずれ {geo['lateral_max_mm']:.2f} mm")

# --- (d) 既定の表 ----------------------------------------------------------------
try:
    cams = C.build_all(PT.TABLES)
    check("d1 既定の表の全 25 カムが作れる", True)
except C.CamError as e:
    cams = None
    check("d1 既定の表の全 25 カムが作れる", False, str(e))
if cams is not None:
    worst = 0.0
    for k, th in enumerate(P.TABLE_THETA):
        hh = K.pixel_heights(cams, th)
        for j in range(P.N):
            for i in range(P.N):
                worst = max(worst, abs(hh[j][i] * 1000.0 - PT.TABLES[k][j][i]))
    check("d2 表のサーボ角で全画素が表どおり", worst <= TOL, f"max 誤差 = {worst:.5f} mm")
    flat_h = K.pixel_heights(cams, P.THETA_FLAT)
    check("d3 サーボ 90 度で全画素が面一", max(abs(v) for row in flat_h for v in row) * 1000.0 <= TOL)
    ok_conv = all(c["convex"] for row in cams for c in row)
    check("d4 全カムが凸", ok_conv)
    lat = max(c["lateral_max_mm"] for row in cams for c in row)
    check("d5 接点の横ずれ <= 足の半幅 - 1mm", lat <= C.LATERAL_MAX_MM, f"最大 {lat:.2f} mm（上限 {C.LATERAL_MAX_MM:.1f}）")

# --- (e) 隣の行のカムの円錐の制約（表の組）---------------------------------------------------------
def tables_with(edits):
    t = [[[0.0] * P.N for _ in range(P.N)] for _ in range(P.K)]
    for (k, j, i), v in edits.items():
        t[k][j][i] = v
    return t


lim_a, lim_b, _, _ = C.cone_pair_limits_mm()
# 通す側: 同じ列の隣の行の和が上限ちょうど / 斜めの和が上限ちょうど
C.check_tables(tables_with({(3, 2, 2): 3.0, (3, 1, 2): lim_a - 3.0}))
check("e1 同じ列の隣の行の和が上限ちょうどは通る", True, f"上限 {lim_a:.2f}")
C.check_tables(tables_with({(3, 1, 2): 3.0, (3, 2, 1): lim_b - 3.0}))
check("e2 斜めの隣の行の和が上限ちょうどは通る", True, f"上限 {lim_b:.2f}")
# 止める側
must_fail("e3 同じ列の隣の行の和が上限 + 0.1", lambda: C.check_tables(tables_with({(3, 2, 2): 3.0, (3, 1, 2): lim_a - 3.0 + 0.1})))
must_fail("e4 斜めの隣の行の和が上限 + 0.1", lambda: C.check_tables(tables_with({(3, 1, 2): 3.0, (3, 2, 1): lim_b - 3.0 + 0.1})))
lim0 = C.first_cam_neg_row_height_max_mm()
C.check_tables(tables_with({(3, 1, 0): lim0}))
check("e5 奇数行の cam 0 が上限ちょうどは通る", True, f"上限 {lim0:.2f}")
must_fail("e6 奇数行の cam 0 が上限 + 0.1（-X のじょうごに収まらない）", lambda: C.check_tables(tables_with({(3, 1, 0): lim0 + 0.1})))
C.check_tables(tables_with({(3, 0, 0): 3.0, (3, 2, 0): 3.0}))
check("e7 偶数行の cam 0 は +3 でも通る（円錐は -X のパッドから遠い）", True)
# 実際の輪郭で測った隙間（cone_check）: 上限ちょうどの表が当たらない
import cone_check as CC
cams_edge = C.build_all(tables_with({(3, 2, 2): 3.0, (3, 1, 2): lim_a - 3.0}), w=P.DWELL_HALF_DEG)
r_nom = CC.adjacent_rows_clearance(cams_edge, rel_shifts=(0.0,), rows=[1])
r_slk = CC.adjacent_rows_clearance(cams_edge, rel_shifts=(-2 * P.AXIAL_DRIFT * 1000, 0.0, 2 * P.AXIAL_DRIFT * 1000), rows=[1])
vn, vs = r_nom[1][0], r_slk[1][0]
check("e8 上限ちょうどの表: 実輪郭の隙間は遊びを入れて >= 0（当たらない）", vs >= 0.0, f"設計位置 {'>= 0.6' if vn > 1e8 else round(float(vn), 3)} mm、遊び込み {round(float(vs), 3)} mm")
# 上限を 1.0 超えた表: 実輪郭でも遊び込みで当たる（制約が意味を持つこと = 通す側だけでなく止める側の確認）
cams_bad = C.build_all(tables_with({(3, 2, 2): 3.0}), w=P.DWELL_HALF_DEG)
cams_bad[1][2] = C.build_cam([0.0, 0.0, 0.0, lim_a - 3.0 + 1.0, 0.0], 1, 2, check=False)
r_bad = CC.adjacent_rows_clearance(cams_bad, rel_shifts=(-2 * P.AXIAL_DRIFT * 1000, 0.0, 2 * P.AXIAL_DRIFT * 1000), rows=[1])
check("e9 上限 + 1.0 の表を cams.py を迂回して作ると、実輪郭で食い込む（計器が当たりを検出できる）", r_bad[1][0] < 0.0, f"遊び込み {round(float(r_bad[1][0]), 3)} mm")

print()
if fails:
    print("FAILED:", ", ".join(fails))
    sys.exit(1)
print("ALL PASS")
