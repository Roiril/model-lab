"""角の床側の板（pipe-foot-corner-one と同じ形）を、X1C で刷れるよう 2 枚に切る版の寸法定義。

    pipe_foot_corner_split_a … A の脚 2 本 + 5 本目の側（240 x 222）
    pipe_foot_corner_split_b … B の脚 2 本の側（90 x 240）

2 枚は継ぎ目の板（厚み 5）に付けたパズルの凸凹で位置を合わせる。床に置いて噛み合わせるだけで
角の脚の間隔が決まるので、添え板（pipe-foot-corner の tie）は要らない。

継ぎ目（世界座標。角の節点が原点、A の脚は x 軸上の負側、B の脚は y 軸上の負側）:
    1. 角の縁（対角線 x + y = -39.3）の中点 S0 = (-19.67, -19.67) から (-1, -1) の向きへ
       （x = y の線）、A1-B1 の対角の壁をその真ん中で直角に横切って K = (SEAM_X, SEAM_X) まで
    2. K から真っ直ぐ下（-y）へ板の縁まで。x = SEAM_X = -115
    継ぎ目 2 を -45 に置くと、5 本目と B2 のあいだで垂れている縁（x = -45 で y = -244）が
    A に付いて A が 269 になる。-115 なら縁は y = -216 で、A は 241 に収まる。
    横切る壁は対角の壁（真ん中、高さ 14）と、J2 → F の枝（x = -115、高さ 39）の 2 枚だけ。
    どちらも継ぎ目で切り、両側に GAP/2 ずつ空ける（板の噛み合いだけで位置が決まるように）。

凸凹（ジグソー）:
    継ぎ目 1 に 2 つ、継ぎ目 2 に 2 つ。首の幅 TAB_NECK_W、継ぎ目から頭の中心まで TAB_NECK_L、
    頭の半径 TAB_HEAD_R（首より太いので引き抜きに掛かる）。B・A・B・A の順に持ち主を変える。
    凸は持ち主の板から TAB_CLEAR だけ痩せさせ、相手の板の凹は図面の寸法のまま（片側 0.2 の遊び）。
    首と頭は板の厚みだけ（z 0〜5）。壁とひれから離した位置に置く。

片の大きさ（外側の縁 EDGE_R = 25 のとき）:
    A: x -259.7 〜 -19.67（240.0）、y -215.8 〜 +25（240.8）
    B: x -135 〜 +25（160。B の凸の頭が -135 まで出る）、y -259.7 〜 -19.67（240.0）
    どちらも X1C の 252 に入る（縁まで 5.6〜6）。
"""
import importlib.util
import math
import os


def _load(name, model):
    path = os.path.join(os.path.dirname(__file__), os.pardir, model, "params.py")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ONE = _load("pipe_foot_corner_one_params", "pipe-foot-corner-one")   # 板そのものの寸法はこちら
PAIR = ONE.PAIR
CORNER = ONE.CORNER

MM = ONE.MM
PLATE_T = ONE.PLATE_T            # 5.0
EDGE_R = ONE.EDGE_R              # 25.0
CORNER_OFF = ONE.CORNER_OFF      # 74.7
SPAN = ONE.SPAN                  # 160.0
FIN_OUT_R = ONE.FIN_OUT_R        # 36.0
FILLET_R = ONE.FILLET_R          # 2.5
SPINE_T = ONE.SPINE_T            # 8.0

# --- 継ぎ目 ---
CHAMFER_C = CORNER_OFF - EDGE_R * math.sqrt(2.0)   # 39.3 角の縁の対角線 x + y = -CHAMFER_C
SEAM_S0 = (-CHAMFER_C / 2, -CHAMFER_C / 2)         # (-19.67, -19.67) 継ぎ目が角の縁に出る点
SEAM_X = -115.0                                    # 継ぎ目 2（縦）の x。折れ点 K = (SEAM_X, SEAM_X)
SEAM_K = (SEAM_X, SEAM_X)
GAP = 0.3                                          # 継ぎ目の板どうし・壁の切り口の隙間（合計。両側へ半分ずつ）
TAB_CLEAR = 0.2                                    # 凸を痩せさせる量（片側）。凹は図面の寸法のまま

# 継ぎ目 1（x = y）と A1 のひれの先 (-CORNER_OFF, -FIN_OUT_R) の距離
_fin_tip_gap = (CORNER_OFF - FIN_OUT_R) / math.sqrt(2.0) - ONE.FIN_T / 2 - FILLET_R
assert _fin_tip_gap >= 4.0, "継ぎ目 1 が A1・B1 のひれの先に掛かる"
# 縦の継ぎ目 2 と 5 本目のソケットの根元（F は継ぎ目より左にある）
assert SEAM_X - ONE.F[0] >= ONE.ROOT_R + FILLET_R + 4.0, "継ぎ目 2 が 5 本目のソケットに掛かる"

# F と B2 を結ぶ縁（半径の違う円の共通外接線）。継ぎ目 2 がこの縁に出る点が A の片の一番下
_c1, _r1 = ONE.F, ONE.PLATE_R
_c2, _r2 = ONE.B2, EDGE_R
_dx, _dy = _c2[0] - _c1[0], _c2[1] - _c1[1]
_dl = math.hypot(_dx, _dy)
_ex, _ey = _dx / _dl, _dy / _dl
_al = (_r1 - _r2) / _dl
_be = math.sqrt(1.0 - _al * _al)
_nx, _ny = _al * _ex + _be * _ey, _al * _ey - _be * _ex          # 外向きの法線（-x, -y 側）
_h = _nx * _c1[0] + _ny * _c1[1] + _r1
SEAM_BOTTOM_Y = (_h - _nx * SEAM_X) / _ny                        # -215.8 継ぎ目 2 が縁に出る y

# --- 凸凹 ---
TAB_NECK_W = 10.0                # 首の幅
TAB_NECK_L = 12.0                # 継ぎ目から頭の中心まで
TAB_HEAD_R = 8.0                 # 頭の半径（首の半分 5 より 3 太い → 引き抜きに掛かる）
TAB_Z_TOP = PLATE_T + 1.0        # 凸凹を切る高さ（板の上面より上には何も無い所に置く）
# (継ぎ目, 位置, 持ち主)。継ぎ目 1 は x（= y）、継ぎ目 2 は y。壁とひれから離す:
#   対角の壁は継ぎ目 1 の x = -37.35 / J2→F の枝は y -158.7〜-150.7 / B2 のひれ y -237.7〜-231.7
TABS = [("s1", -70.0, "B"), ("s1", -95.0, "A"), ("s2", -128.0, "B"), ("s2", -185.0, "A")]
_TAB_KEEP = TAB_HEAD_R + 4.0 + FILLET_R + 2.5     # 頭の中心から壁の面まで最低これだけ
for _seg, _p, _o in TABS:
    if _seg == "s1":
        assert abs(_p - (-CORNER_OFF / 2)) * math.sqrt(2.0) >= _TAB_KEEP, f"継ぎ目 1 の凸凹 {_p} が対角の壁に掛かる"
        assert abs(_p - SEAM_X) * math.sqrt(2.0) >= TAB_HEAD_R + 6.0, f"継ぎ目 1 の凸凹 {_p} が折れ点に近すぎる"
    else:
        for _wall_y in (-ONE.FIFTH_OFF, ONE.B2[1]):
            assert abs(_p - _wall_y) >= _TAB_KEEP, f"継ぎ目 2 の凸凹 {_p} が壁・ひれに掛かる"
        assert _p - TAB_HEAD_R - 6.0 >= SEAM_BOTTOM_Y, f"継ぎ目 2 の凸凹 {_p} が板の縁に近すぎる"

# --- 片の大きさ ---
BED = 252.0                                        # X1C の使える幅
A_EXTENT_X = (CORNER_OFF + SPAN + EDGE_R) - (-SEAM_S0[0])   # 240.0 A2 の外側の縁 → S0
A_EXTENT_Y = EDGE_R - SEAM_BOTTOM_Y                         # 240.8 A の縁（y = +25）→ 継ぎ目 2 の下端
B_EXTENT_X = EDGE_R - (SEAM_X - TAB_NECK_L - TAB_HEAD_R)    # 160  B の縁（x = +25）→ B の凸の頭
B_EXTENT_Y = (CORNER_OFF + SPAN + EDGE_R) - (-SEAM_S0[1])   # 240.0
assert max(A_EXTENT_X, A_EXTENT_Y, B_EXTENT_X, B_EXTENT_Y) <= BED, "片が X1C に入らない"
