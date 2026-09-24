"""角の床側の部品を 1 枚の板にまとめた版（Bambu Lab H2D 向け）の寸法定義。

    pipe_foot_corner_one … M 字 A の脚 2 本 + M 字 B の脚 2 本 + 5 本目を 1 枚で受ける板

配置は pipe-foot-corner（板 2 枚 + 添え板）と同じ。違いは板が 1 枚につながっていることと、
外側の縁を詰めていること。板が 1 枚だと角の脚 2 本の位置が板で決まるので、添え板は要らない。

造形板: H2D は 1 ノズルで 325 x 320、2 ノズルで 300 x 320（同じフィラメントを両方に入れた
ときだけ 350 x 320）。どのモードでも刷れるよう 300 x 300 に収める。
    全幅 = CORNER_OFF + SPAN + 2 * EDGE_R - JOINT_SHIFT = 261.5
外側の縁は軸から EDGE_R = 28。X1C 向けに 2 枚へ切る分割版（pipe-foot-corner-split）で
それぞれの片が 252 に入る上限は 32（片の幅 = 197.35 + 1.707 * EDGE_R）。
そこにあるソケット 4 本は pipe-foot の台座（半径 34 の段・半径 26 の円錐）を付けず、
根元の壁を厚くした筒にする。5 本目は板の内側の角にあるので、まわりの板は半径 PLATE_R = 42 のまま。

上から見た配置（すべて mm。角の節点が原点、A の脚は x 軸上の負側、B の脚は y 軸上の負側）:
    A の脚 A1 (-CORNER_OFF, -JOINT_SHIFT), A2 (-CORNER_OFF-160, -JOINT_SHIFT)
    B の脚 B1 (-JOINT_SHIFT, -CORNER_OFF), B2 (-JOINT_SHIFT, -CORNER_OFF-160)
    5 本目 F (-FIFTH_OFF, -FIFTH_OFF) = 2 つの中央レールの延長線の交点
    板の輪郭は「A1, A2, B1, B2 に半径 EDGE_R、F に半径 PLATE_R の円」の凸包。
    F は A2-B2 の対角線より外にあるので、輪郭は五角形（A2 → F → B2 → B1 → A1）。
    角の節点 (0,0) は板の外（A1-B1 のあいだの縁は対角線 x + y = -35.1）

背骨:
    A の列は A2 → J1 → A1、B の列は B2 → J2 → B1（J は中央レールの真下の節点、脚の中点）。
    J1 → F、J2 → F の枝は中央レールの真下を通る。A1 と B1 は対角の壁で直接つなぐ
    （板 2 枚版の添え板の役目。長さ 105.6）。角の節点まで背骨を伸ばすと板の外へ出る。

板厚は pipe-foot-pair の 5 でなく 8（2026-09-20 ユーザー指示「もっと折れにくく」。
分割版の凸凹がこの厚みで切られる）。

印刷はこの向きのまま。底面が丸ごと着き、上へ行くほど細るだけなので無支持。
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


PAIR = _load("pipe_foot_pair_params", "pipe-foot-pair")
CORNER = _load("pipe_corner_params", "pipe-corner")

MM = PAIR.MM

# --- パイプとソケット（pipe-foot-pair と同じ）---
PIPE_OD = PAIR.PIPE_OD           # 28.0
BORE_D = PAIR.BORE_D             # 28.6
BOSS_R = PAIR.BOSS_R             # 18.3 ソケット外径 36.6
SEAT_Z = PAIR.SEAT_Z             # 30.0 パイプの下端の高さ
BOSS_TOP = PAIR.BOSS_TOP         # 85.0 全高
MOUTH_TAPER = PAIR.MOUTH_TAPER   # 0.0 外側の絞りなし
TIP_R = PAIR.TIP_R               # 18.3
FUNNEL_L = PAIR.FUNNEL_L         # 6.0 口の漏斗
FUNNEL_DR = PAIR.FUNNEL_DR       # 2.5

# --- 配置（正本は pipe-corner。ここでは読むだけ）---
SPAN = PAIR.SPAN                 # 160.0
CORNER_OFF = CORNER.CORNER_OFF   # 74.7 角の脚の軸 → 相手の脚列の軸線
JOINT_SHIFT = CORNER.JOINT_SHIFT # 29.2 M 字を回さず角の内側へ平行移動する量
FIFTH_OFF = CORNER_OFF + SPAN / 2    # 154.7 5 本目の軸 → 各脚列の軸線
A1, A2 = (-CORNER_OFF, -JOINT_SHIFT), (-CORNER_OFF - SPAN, -JOINT_SHIFT)
B1, B2 = (-JOINT_SHIFT, -CORNER_OFF), (-JOINT_SHIFT, -CORNER_OFF - SPAN)
F = (-FIFTH_OFF, -FIFTH_OFF)
MC = CORNER_OFF + SPAN / 2       # 154.7 各列の脚の中点（= 中央レールの位置）

# --- 床に着く板 ---
PLATE_T = 8.0                    # 板厚（pipe-foot-pair は 5。角は継ぎ目の凸凹を持つので厚く）
PLATE_R = PAIR.PLATE_R           # 42.0 5 本目まわりの半径
EDGE_R = 28.0                    # 脚 4 本まわりの半径（外側の縁）
BED = 300.0                      # H2D の 2 ノズル時の X。ここに入れば全モードで刷れる
EXTENT = CORNER_OFF + SPAN + 2 * EDGE_R - JOINT_SHIFT  # 261.5 全幅 = 奥行き
assert EXTENT <= BED, f"造形板に入らない: {EXTENT}"

# --- ソケットの根元（脚 4 本。縁まで 28 しか無いので台座を付けず、根元の壁を厚くする）---
FILLET_R = PAIR.FILLET_R         # 2.5 接合部と板の縁の R
ROOT_WALL = 5.2                  # 根元の壁厚（BORE_D/2 から）。筒の断面係数 3018 → 4460 mm3
ROOT_R = BORE_D / 2 + ROOT_WALL  # 19.5
ROOT_TOP_Z = SEAT_Z              # 30.0 ここまで厚いまま
ROOT_TAPER = 15.0                # ここから 15mm かけて BOSS_R へ細る
assert ROOT_R + FILLET_R <= EDGE_R - FILLET_R - 0.5, "ソケットの根元の R と板の縁の R が食い合う"

# --- 背骨と枝 ---
RIB_TOP_Z = 60.0                 # 背骨・ひれ・対角の壁がソケットに付く高さ（筒の 7 割を抱える）
SPINE_T = PAIR.SPINE_T           # 8.0
SPINE_TOP_Z = RIB_TOP_Z
SPINE_MID_Z = PAIR.SPINE_MID_Z   # 14.0 脚 2 本の中央での高さ
SPINE_LAP = PAIR.SPINE_LAP       # 1.0 板へ食い込ませる量
SPINE_SEG = PAIR.SPINE_SEG       # 48
BRANCH_SEG = PAIR.BRANCH_SEG     # 24
TIE_L = (CORNER_OFF - JOINT_SHIFT) * math.sqrt(2.0)   # 64.35 A1 → B1 の対角の壁の長さ
TIE_MID_Z = 24.0                 # 対角の壁の中央の高さ。分割版はここに節（凸凹）を付けるので 14 より高く
# 対角の壁の外側の面から板の縁までの距離
TIE_EDGE_CLEAR = EDGE_R - SPINE_T / 2
assert TIE_EDGE_CLEAR >= 2 * FILLET_R + 6.0, "対角の壁が板の縁に寄りすぎ"

# --- 横のひれ（脚 4 本は内側だけ、5 本目は外側 2 枚）---
FIN_T = PAIR.FIN_T               # 6.0
FIN_OUT_R = PAIR.FIN_OUT_R       # 36.0
FIN_OUT_H = PAIR.FIN_OUT_H       # 5.0
FIN_TOP_Z = RIB_TOP_Z
assert FIN_OUT_R + 2 * FILLET_R <= PLATE_R, "5 本目のひれが板の縁の R に掛かる"

# --- 仕上げ ---
FILLET_ANGLE = PAIR.FILLET_ANGLE
FILLET_SEG = PAIR.FILLET_SEG
BASE_ROUND = PAIR.BASE_ROUND     # 1.5

# --- メッシュ品質 ---
SEG = PAIR.SEG                   # 96
CONE_SEG = PAIR.CONE_SEG         # 24
