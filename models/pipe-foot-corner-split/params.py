"""角の床側の板（pipe-foot-corner-one と同じ形）を、X1C で刷れるよう 2 枚に切る版の寸法定義。

    pipe_foot_corner_split_a … A の脚 2 本 + 5 本目の側（245 x 245）
    pipe_foot_corner_split_b … B の脚 2 本の側（169 x 245）

2 枚は継ぎ目のパズルの凸凹で位置を合わせる。B を A の上から落として噛み合わせるだけで
角の脚の間隔が決まるので、添え板（pipe-foot-corner の tie）は要らない。

継ぎ目（世界座標。角の節点が原点、A の脚は x 軸上の負側、B の脚は y 軸上の負側）:
    1. 角の縁（対角線 x + y = -39.3）の中点 S0 = (-19.67, -19.67) から (-1, -1) の向きへ
       （x = y の線）、A1-B1 の対角の壁をその真ん中で直角に横切って K = (SEAM_X, SEAM_X) まで
    2. K から真っ直ぐ下（-y）へ板の縁まで。x = SEAM_X = -115
    継ぎ目 2 を -45 に置くと、5 本目と B2 のあいだで垂れている縁（x = -45 で y = -244）が
    A に付いて A が 269 になる。-115 なら縁は y = -216 で、A は 241 に収まる。
    横切る壁は対角の壁（真ん中、高さ 24）と、J2 → F の枝（x = -115、高さ 39）の 2 枚。
    そこには「節」（KNUCKLE）を付け、壁の高さまで貫く凸凹で壁どうしをつなぐ。
    板の部分は板の厚み（8）の凸凹。板どうし・壁の切り口は GAP/2 ずつ空ける。

凸凹（ジグソー）:
    継ぎ目 1 に節 1 + 板 1、継ぎ目 2 に節 1 + 板 1。節は A、板は B が持つ
    （それぞれの片が凸 2 つと凹 2 つを持つ）。
    凸は持ち主から TAB_CLEAR だけ痩せさせ、相手の凹は図面の寸法のまま（片側 0.2 の遊び）。

片の大きさ（外側の縁 EDGE_R = 28、板厚 8）:
    A: x -262.7 〜 -17.55（245.1）、y -216.9 〜 +28（244.9）
    B: x -139.5 〜 +28（167.5。B の板の凸の頭が -139.5 まで出る）、y -262.7 〜 -17.55（245.1）
    どちらも X1C の 252 に入る（縁まで 3.5）。
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
SEAM_TIE_XY = -CORNER_OFF / 2                      # -37.35 継ぎ目 1 が対角の壁を横切る点（x = y）
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
# 2 種類。どちらも z 方向の押し出しなので、B を A の上から落として組む。
#   plate   … 板の厚み（8）だけの凸凹。壁の無い所に置く
#   knuckle … 継ぎ目が壁を横切る所の「節」。壁を継ぎ目の両側で幅 KNUCKLE_W の塊に太らせ、
#             その塊を壁の高さまで貫く凸凹で噛み合わせる。壁が継ぎ目をまたいでつながる
#             （2026-09-20 ユーザー指示「もっと折れにくく」。それまでは壁を切りっ放しにしていた）
TAB_CLEAR = 0.2                  # 凸を痩せさせる量（片側）。凹は図面の寸法のまま
PLATE_TAB = dict(neck_w=14.0, neck_l=14.0, head_r=10.5)   # 首の幅 / 継ぎ目から頭の中心 / 頭の半径
KNUCKLE_TAB = dict(neck_w=14.0, neck_l=15.0, head_r=11.0)
KNUCKLE_W = 32.0                 # 節の幅（壁と直交する向き）。凹の頭 22 の両側に 5 残る
KNUCKLE_L = 31.0                 # 節が継ぎ目から凹の側へ伸びる長さ。凹の頭の先（15 + 11）に 5 残る
KNUCKLE_L_TAB = 14.0             # 凸の側（持ち主の側）は短い。凸の根元に肉があればよい
#   ⚠ 枝の節は 5 本目のソケット（根元 r 19.5、x = -135.2 まで）に近い。凹を A 側（-x）に
#   置くと頭が根元に食い込み、穴の壁に穴が開く（実測）。凸凹の向きは A → B（+x）にする
KNUCKLE_UP = 5.0                 # 節の上面を壁の上端よりこれだけ高くする（面を重ねない）
KNUCKLE_CHAMFER = 10.0           # 節の端の上の角を 45° で落とす（壁がそこから出る）
for _t in (PLATE_TAB, KNUCKLE_TAB):
    assert _t["head_r"] > _t["neck_w"] / 2 + 2.0, "頭が首より太くないと引き抜きに掛からない"
assert KNUCKLE_W >= 2 * KNUCKLE_TAB["head_r"] + 10.0, "節の幅が凹の頭に対して薄い"
assert KNUCKLE_L >= KNUCKLE_TAB["neck_l"] + KNUCKLE_TAB["head_r"] + 5.0, "節の長さが凹の頭に対して短い"
assert KNUCKLE_L_TAB >= KNUCKLE_TAB["neck_w"], "凸の根元の肉が短い"

# (継ぎ目, 位置, 持ち主, 種類)。継ぎ目 1 は x（= y）、継ぎ目 2 は y。
#   対角の壁は継ぎ目 1 と (-37.35, -37.35) で交わる（A1-B1 の中点）
#   J2→F の枝（y = -154.7）は継ぎ目 2 と (-115, -154.7) で交わる
TABS = [("s1", -CORNER_OFF / 2, "A", "knuckle"),
        ("s1", -82.0, "B", "plate"),
        ("s2", -ONE.FIFTH_OFF, "A", "knuckle"),
        ("s2", -195.0, "B", "plate")]
# 枝の節の A 側（短い方）が 5 本目のソケットの根元に掛からないこと
assert SEAM_X - KNUCKLE_L_TAB >= ONE.F[0] + ONE.ROOT_R + FILLET_R + 3.0, "枝の節が 5 本目のソケットの根元に掛かる"
# 継ぎ目 2 の板の凸（B → A）の頭が 5 本目のソケット・ひれから離れていること
_pt = [t for t in TABS if t[0] == "s2" and t[3] == "plate"][0]
_hx, _hy = SEAM_X - PLATE_TAB["neck_l"], _pt[1]
assert math.hypot(_hx - ONE.F[0], _hy - ONE.F[1]) - PLATE_TAB["head_r"] >= ONE.ROOT_R + FILLET_R + 4.0, "板の凸の頭が 5 本目の根元に掛かる"
assert math.hypot(_hx - ONE.F[0], _hy - (ONE.F[1] - ONE.FIN_OUT_R)) - PLATE_TAB["head_r"] >= ONE.FIN_T / 2 + FILLET_R + 4.0, "板の凸の頭が 5 本目のひれに掛かる"
_KEEP = PLATE_TAB["head_r"] + 4.0 + FILLET_R + 2.5     # 板の凸凹の頭の中心から壁・節まで
# 節は継ぎ目に沿って ±KNUCKLE_W/2 を占める（KNUCKLE_L は壁に沿う向き）
for _seg, _p, _o, _kind in TABS:
    if _kind != "plate":
        continue
    if _seg == "s1":
        assert abs(_p - SEAM_TIE_XY) * math.sqrt(2.0) >= KNUCKLE_W / 2 + _KEEP, f"継ぎ目 1 の凸凹 {_p} が節に掛かる"
        assert abs(_p - SEAM_X) * math.sqrt(2.0) >= PLATE_TAB["head_r"] + 6.0, f"継ぎ目 1 の凸凹 {_p} が折れ点に近すぎる"
    else:
        assert abs(_p - (-ONE.FIFTH_OFF)) >= KNUCKLE_W / 2 + _KEEP, f"継ぎ目 2 の凸凹 {_p} が節に掛かる"
        assert abs(_p - ONE.B2[1]) >= _KEEP, f"継ぎ目 2 の凸凹 {_p} が B2 のひれに掛かる"
        assert _p - PLATE_TAB["head_r"] - 6.0 >= SEAM_BOTTOM_Y, f"継ぎ目 2 の凸凹 {_p} が板の縁に近すぎる"

assert (SEAM_S0[0] - SEAM_TIE_XY) * math.sqrt(2.0) >= KNUCKLE_W / 2 + FILLET_R + 3.0, "対角の壁の節が角の縁からはみ出す"
assert (SEAM_X - (-ONE.FIFTH_OFF)) >= KNUCKLE_W / 2 + 6.0, "枝の節が折れ点 K に掛かる"

# --- 片の大きさ ---
BED = 252.0                                        # X1C の使える幅
A_EXTENT_X = (CORNER_OFF + SPAN + EDGE_R) - (-SEAM_S0[0])   # 240.0 A2 の外側の縁 → S0
A_EXTENT_Y = EDGE_R - SEAM_BOTTOM_Y                         # 240.8 A の縁（y = +25）→ 継ぎ目 2 の下端
B_EXTENT_X = EDGE_R - (SEAM_X - PLATE_TAB["neck_l"] - PLATE_TAB["head_r"])   # 167.5 B の縁 → B の板の凸の頭
B_EXTENT_Y = (CORNER_OFF + SPAN + EDGE_R) - (-SEAM_S0[1])   # 240.0
assert max(A_EXTENT_X, A_EXTENT_Y, B_EXTENT_X, B_EXTENT_Y) <= BED, "片が X1C に入らない"
