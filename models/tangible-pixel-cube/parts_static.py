"""静止部品の形（bpy）。housing / bezel / guide_plate / sg92r / sg92r_horn。

build_static() -> dict[id, Object]   組立姿勢、単位 m、オブジェクト名 = id
PRINT_POSE                          各 id の刷る向き（回転オイラー XYZ 度・理由・サポートの場所）
VISIBLE_FACE                        見える面の判定（id -> f(重心 mm, 法線) -> bool、組立姿勢の座標）

寸法はすべて params.py / kinematics.py から読む。ここに書くのは、params に無い細部（面取り・爪・柵・隙間）だけで、
理由をコメントに書く。内部の作図は mm（Blender の単位を mm として組む）。出口で 0.001 倍して m にする。

座標: X = カム軸の方向、Y = 前後（+Y が背面、配線の窓）、Z = 上。原点は箱の底面の中心。
サーボの原寸 STL（native）から世界への写像: 世界 X = SERVO_BODY_X0 + native z、世界 Y = native x、世界 Z = Zs + native y
（巡回置換で右手系のまま。出力軸 +X、サーボ 90 度のホーンの姿勢）。
"""
import math
import os
import struct
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P  # noqa: E402
import kinematics as K  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
EXPORTS = os.path.join(REPO, "exports")


def mm(v):
    """params の m を mm へ（丸めて 63.50000000000001 のような値を作らない）"""
    return round(v * 1000.0, 6)


# --- params から読む寸法（mm）-------------------------------------------------------------------
HALF = mm(P.CUBE) / 2                      # 外形の半分（48）
IX = HALF - mm(P.WALL_END)                 # 内寸 X の半分（45）
IY = HALF - mm(P.WALL_Y)                   # 内寸 Y の半分（46）
FLOOR = mm(P.FLOOR)                        # 底（3）
Z_SEAM = mm(P.BEZEL_Z0)                    # 外装の上端 = ベゼルの下面（93）
Z_TOP = mm(P.BEZEL_Z1)                     # ベゼルの上面（96）
ZC = mm(P.CAM_AXIS_Z)                      # カム軸の高さ（51.7）
ZS = mm(P.SERVO_AXIS_Z)                    # サーボ出力軸の高さ（24.2）
XS0 = mm(P.SERVO_BODY_X0)                  # サーボ本体の底面の X（native z 0。10.2）
PITCH = mm(P.PITCH)                        # 17
AXIS_Y = [mm(K.axis_y(j)) for j in range(P.N)]
CAM_X = [[mm(K.cam_x(i, j)) for i in range(P.N)] for j in range(P.N)]   # [j][i]

# --- 外観 -------------------------------------------------------------------------------------
# 外の稜はすべて 1.0mm の 45 度面取り。ベッドに接する稜（外装の底、ベゼルの上面）も同じ。
# 外装の上端とベゼルの下面の継ぎ目だけは面取りせず、平らな 1 本の水平線にする
CHAMFER = 1.0
FIT = 0.2                                  # 嵌め合いの片側の隙間（回さない・滑らせない面。CLAUDE.md 0.2〜0.4 の下限）

# --- 軸受け（両端の壁に付ける帯）--------------------------------------------------------------
PAD_X0 = mm(P.PAD_X0)                      # 帯の内面（43.8）
PAD_X1 = mm(P.PAD_X1)                      # 帯の外面 = 端壁の内面（45）
PAD_TOP = ZC + mm(P.PAD_TOP_ABOVE)         # 帯の上面（55.15。位相合わせ治具の耳が座る）
PAD_BOT = ZC - mm(P.PAD_BOT)               # 帯の下端（46.7）
PAD_UNDER = PAD_X1 - PAD_X0                # 帯の下の 45 度の面取りの高さ（1.2。張り出しが 45 度を超えない）
U_W = mm(P.U_SLOT_W)                       # U 溝の幅（6.8）
U_MOUTH = 0.6                              # U 溝の入口の面取り（0.6、45 度。軸が落ちやすい）
U_DEEP = 0.0                               # U 溝そのものは壁へ掘り込まない（溝の底は壁の内面 45 と同じ面）
U_RECESS_D = 1.0                           # 栓の外側の肉（厚み 1.85 を確保する分）が入る縦の溝の、壁の内面からの深さ。壁は 2.0mm 残る（栓の外面 45.75 に 0.25 の隙間）
U_RECESS_TOP_Z = ZC + 6.3                  # 栓の外側の部分の上端の目安（58.0。栓は 57.8 まで、上は 45 度で丸める）
FN = 48                                    # 円の分割数（外接円で作り、隙間を割らない）

# --- 案内板を受ける壁の出っ張り（±Y の壁）--------------------------------------------------------
PLATE_Z0 = mm(P.PLATE_Z0)                  # 板の下面（63.5）
PLATE_Z1 = mm(P.PLATE_Z1)                  # 板の上面（83.4）
LEDGE_W = 1.6                              # 壁から出る幅（1.6）。足は Y 44.0 までなので、溝の端 44.4 より外に置く（足との隙間 0.4 以上）
LEDGE_OUT = IY - LEDGE_W                   # 出っ張りの内端の Y（44.4）

# --- 画素の十字穴 --------------------------------------------------------------------------------
HOLE_W = mm(P.HOLE_W)                      # 茎の角穴（9.4）
SLOT_X = mm(P.SLOT_X)                      # 足の溝の X 幅（5.0）
SLOT_Y = mm(P.SLOT_Y)                      # 足の溝の Y 長（20.8）
HOLE_MOUTH = 0.4                           # ベッド側（板の上面 = 画素が上から入る側）の穴の縁の面取り。最初の層の膨らみで 0.2mm の隙間が潰れず、25 個の画素を同時に入れやすい。桟は面で 0.8 残る

# --- 板の落下止め（軸受けの上へ入る栓。軸ごと・両端）-------------------------------------------------------
# 軸の丸の上端（軸が溝の底に載ったとき Zc-0.05+2.5）の 0.15（Zc+2.5 から HOLD_GAP = 0.1、溝の底の隙間 0.05 を足した値）上に栓の下端を置く
# （params.HOLD_PLUG_BOT = 54.3）。中央軸は半円歯車の噛み合いの分離力（約 1N）で上へ押されるので、浮きは 0.15 に抑える。
# 栓は U 溝（幅 5.2）の壁の間へ入る（幅 4.6）。厚みは 1.2 以上にする: 下の部分は軸の鍔（遊び込みの +X 面 43.8、回して R5.49 = Z 57.19）の外側
# X 43.9 から、板の端 44.8 を越えて 45.4 まで（厚み 1.5）。板の端から外へ出る 0.6 は、壁の窪み（U_RECESS_D）に入れる。
# 上の部分（Z 57.8 から上。鍔の上端から 0.6）は歯車の歯先（X 42.6）の外側 42.9 から 44.8 まで（厚み 1.9）
PLUG_BOT = mm(P.HOLD_PLUG_BOT)             # 54.3
PLUG_W = 4.6                               # 栓の Y 幅（溝 5.2、板の左右の遊び ±0.2 を許す）
PLUG_X_LO = 43.9                           # 下の部分の内面
PLUG_X_OUT = 45.75                         # 下の部分の外面（板の端 44.8 から 0.95 出る）。内面 43.9 から厚み 1.85
PLUG_STEP_Z = ZC + 6.1                     # これより上（57.8）は内面を PLUG_X_UP まで太らせる
PLUG_X_UP = 42.9                           # 上の部分の内面（厚み 1.9 以上）。栓の高さ 9.2（54.3 から板の下面 63.5）÷ 最小の厚み 1.85 = 4.97（5 以下）
U_UP = mm(P.U_SLOT_UP)                     # U 溝の丸い底の中心の持ち上げ（0.05）。溝の底は Zc-2.55。軸の丸（R2.5）が載って中心が Zc - 0.05

# --- 案内板を外装へ直接留める舌（板の X 端。軸の間の窓に 4 本）------------------------------------------------------
# 板の下面は外装の出っ張り（Z 63.5）に載り、板の上面から PLATE_PLAY_Z = 0.05 上（Z 83.45 = params.PLATE_LIP_BOT）に、端壁の窪みの天井がある。
# 板の端の舌（X 43.6..44.8 の厚み 1.2、Y 長 9.8、高さ 4）は、両側を切り込んで根元だけ板につなぎ、面内（XY）でしなる = 刷るとき層に沿う。
# 舌の先の爪が端壁の窪みに入り、爪の上面（水平から 15 度）が窪みの天井の 0.05 下に来る。上下の遊びは 0.05（板が X に ±0.2 動くと 0.05 ± 0.054）
TONGUE_T = 1.2                             # 舌の厚み
TONGUE_L = 9.8                             # 舌の長さ（Y）。根元は -Y 側
TONGUE_H = 4.0                             # 舌の高さ（Z）。板の上面から下へ
TONGUE_SLIT = 0.6                          # 舌の側面と下面の切り込みの幅
TONGUE_YC = (-8.0, 8.0)                    # 窓の中心 Y（軸 0 と ±17 の栓の縦溝（Y ±2.6）の間）。+Y 側の舌は先が +Y、-Y 側は先が -Y（爪の窪みと縦溝の間の壁を 1.2 以上に取る）
HOOK_H = 0.4                               # 爪の出っ張り（板の端から 0.4）。壁の内面に対する食い込み 0.4 - 0.2 = 0.2、板が壁へ 0.2 寄ると 0.4
HOOK_Y0, HOOK_Y1 = 2.4, 4.8                # 爪の Y の範囲（窓の中心から舌の先の向きへ 2.4..4.8。長さ 2.4）
HOOK_TOP_SLOPE = math.tan(math.radians(15.0))   # 爪の上面の傾き（外へ下がる 15 度）。持ち上げると壁の天井が爪を内へ押す = 工具なしで引き抜ける
HOOK_TIP_H = 1.2                           # 爪の先の垂直な面の高さ（1.2）。爪の肉を 1.2 以上にする（先を刃先にしない）
POCKET_PLATE_DEPTH = 0.5                   # 端壁の窪みの深さ（0.5。壁は 2.5mm 残る）
POCKET_PLATE_PAD = 0.3                     # 窪みの Y の余裕（爪の両側 0.3）。窪みの端と栓の縦溝の間に壁 1.3 が残る
# 舌のひずみ: 根元（先と逆の端）から爪の中心まで a = 4.9 + 3.6 = 8.5、たわみ δ = 0.4 + 板の寄り 0.2 = 0.6（最悪）→ ε = 3tδ/(2a²) = 3x1.2x0.6/(2x8.5²) = 1.5%（PLA 2% 以下）。
# 通常は δ = 0.4 で 1.0%。曲げ剛性 k = 3EI/a³ = 3x3000x(4x1.2³/12)/8.5³ = 8.4N/mm → 落とし込み 1 本 3.4N（4 本で 14N）。
# 引き抜き: 壁の窪みの天井が爪を内へ押す力 = kδ/tan15 = 8.4x0.2/0.268 = 6.3N/本（4 本で 25N）。軸の押し上げ（約 1N）の 25 倍

# --- ベゼルの爪（ベゼルの縁が、壁の内側の窪みに嵌まる）--------------------------------------------------
LIP_T = 2.0                                # 縁の厚み（2.0）。立てて刷る高さ 9.6 を太さの 5 倍以内（4.8 倍）にする。画素のつば（片側 42.2）まで 0.6 以上空く
LIP_BOT = PLATE_Z1 + 0.2                   # 縁の下端（83.6）。板の上面に 0.2 の隙間を空けて載せ、板が 0.2 以上浮かない
BARB_H = 0.35                              # 爪の出っ張り（0.35）。壁の内面に対する食い込み = 0.35 - 0.2 = 0.15mm。爪は ±X の縁（端壁 3mm、窪みの深さ 0.6 で壁が 2.4 残る。±Y 壁の窪みでは 1.3 になるため移した）。
#   着脱はベゼルの縁ではなく端壁がたわむ（縁は 2.0 の厚みで曲がらない）。壁を板の上面（83.4）から上端（93）までの片持ち梁 L=9.6mm と見ると
#   ε=3tδ/(2L^2)=3x3x0.15/(2x92)=0.7%（最悪の見積り。実際は ±Y 壁と底が壁を支えるので 1 桁小さい）。PLA の 2% 以下。押し込む力 ≈ 3EI/L^3 x δ x 幅 = 3x3000x(14x27/12)/884 x 0.15 = 17N/本（6 本で約 100N の最悪。実際は支えられた壁で 1 桁小さい）
BARB_FLAT = 1.2                            # 爪の平らな頂の高さ（1.2）。両側は 45 度の斜面
BARB_Z = 88.0                              # 爪の中心の高さ。ピクセルのつばの上面（+3 のとき 92.4）とベゼルの下面 93 の間には入らず、ベゼルの縁にある
BARB_L = 14.0                              # 爪の長さ（14、Y 方向）
BARB_Y = (-26.0, 0.0, 26.0)                # 爪の Y。±X の縁それぞれ 3 つ
POCKET_DEPTH = 0.6                         # 壁の窪みの深さ（0.6）。端壁は 2.4mm 残る
POCKET_L = 16.0                            # 窪みの長さ（16。爪 14 に片側 1.0 の余裕）
FINGER_W = 10.0                            # 指の掛かりの幅（Y 方向、10）
FINGER_Y = (-8.5, 8.5)                     # 同 Y の位置（各端壁に 2 つ）。栓の縦溝（軸 0・±17 の Y ±2.6）とピンの溝（Y ±2.5）から離す: 残る壁は全域で 2.0
FINGER_H = 1.6                             # 同 高さ
FINGER_D = 1.0                             # 同 深さ。端壁（3mm）に 2.0mm 残る（他の溝と重ならないので全域で 2.0）

# --- サーボの受け -------------------------------------------------------------------------------
BODY_Y0 = mm(P.SG.BODY_CENTER_X - P.SG.BODY_L / 2)          # 本体の -Y 面（-16.5）
BODY_Y1 = mm(P.SG.BODY_CENTER_X + P.SG.BODY_L / 2)          # 本体の +Y 面（6.5）
EAR_Y0 = mm(P.SG.BODY_CENTER_X - P.SG.FLANGE_L / 2)         # 取付耳の -Y 端（-21）
EAR_Y1 = mm(P.SG.BODY_CENTER_X + P.SG.FLANGE_L / 2)         # 同 +Y 端（11）
EAR_X0 = XS0 + mm(P.SG.FLANGE_BOTTOM_Z)                     # 耳の -X 面（26.2）
EAR_X1 = EAR_X0 + mm(P.SG.FLANGE_T)                         # 耳の +X 面（28.2）
EAR_Z0 = ZS - mm(P.SG.BODY_W) / 2                           # 耳と本体の下面（18.2）
EAR_FENCE_T = 3.0                                           # 柵の厚み（3.0。params の 1.6 から太らせた: 立ての比 5.8 を 3 以下に）。耳から受ける力は、運転トルク 9mNm / 耳の間 32mm = 0.3N、停動 245mNm でも 7.7N。柵 3 x 8 の断面の曲げ応力は 7.7N x 4mm / (3 x 8² / 6) = 1.0MPa
SERVO_CLR = mm(P.SERVO_CLR)                                 # 本体と柵の隙間（片側 0.35）
EAR_GAP = 0.2                                               # 耳と柵の片側の隙間（0.2）。潰しリブがその上に 0.3 出て、耳を 0.1 ずつ挟む
EAR_RIB_H = 0.3                                             # 潰しリブの高さ（0.3）。差し引き 0.1 の潰し代。縦リブなので層に沿う
EAR_RIB_W = 0.6                                             # 同 幅
FENCE_TOP = EAR_Z0 + 8.0                                    # 柵の上端（26.2。耳の幅 12 の下 8mm を挟む）
BACK_T = 3.0                                                # 柵をつなぐ奥の壁の厚み（3）。クリップの爪の窪みの Y の端の肉を 1.2 以上に取る
RIB_UNDER_GAP = 0.2                                         # 本体の下の受けの面と本体の隙間（0.2）。耳の受けの面だけ高さを出す
RIB_UNDER_X = ((XS0 + 1.4, XS0 + 4.6), (XS0 + 18.9, XS0 + 22.1))   # 本体の下の 2 本の受け（-X 端と +X 端）。厚み 3.2 x 高さ 15（Z 3..18.0）= 4.7 倍（5 以下）。Y には 22mm の壁なので揺れない

# --- 配線の窓（+Y 壁）----------------------------------------------------------------------------
WIN_W = mm(P.WIRE_WIN_W)                   # 8
WIN_H = mm(P.WIRE_WIN_H)                   # 4.5
WIN_X = XS0 + mm(P.SG.WIRE_EXIT_Z)         # 窓の中心 X（15.2。配線の出口の真向かい）
WIN_SIDE_H = 3.0                           # 窓の垂直な辺の高さ（3.0）。その上は 45 度の尖り屋根（頂点まで 4.0）。橋も支えも無い。コネクタ（2.5 の厚みを縦にして通す）は垂直な辺の範囲に収まる

# --- SG92R ホーンの向き ---------------------------------------------------------------------------------
# 原寸 STL（写真の姿勢）はホーンの長腕が native -x（世界 -Y）を向く。サーボ 90 度（THETA_FLAT）の組立では、長腕を下（-Z）に向ける
# （params の RECV_BAR_R 20.6 = 長腕 18 + 肉 2.6 が底から 0.6 浮く高さ Zs を決めている。parts_moving.horn_to_uv も長腕 = -Z）。
# 本体の向きは変えず、ホーンだけ出力軸まわりに +90 度。ホーンの 20 山（18 度刻み）の 5 山ぶんなので付け直せる向き
HORN_ROT_DEG = 90.0

# --- SG92R の押さえクリップ（servo_clip_0 = -Y の耳、servo_clip_1 = +Y の耳）-----------------------------------------
# 耳を挟む柵と底の受けの上から被せる U 字のクリップ。上の板が耳の上端（Z 30.2）の 0.2 上に掛かって耳の浮きを 0.2 に止め、両脚の内側の爪が
# 受けの側面の窪みに嵌まる。工具なしで上から押し込み、上へ引いて外す。脚は XZ 面でしなる（刷るときクリップを Y 面で寝かせるので層に沿う）
CLIP_W = 4.0                               # クリップの Y 幅（受けの Y 長 7.5 の中央。窪みは CLIP_W + 0.6 で、両端の肉 1.45）
CLIP_LEG_T = 1.6                           # 脚の厚み
CLIP_BAR_T = 2.0                           # 上の板の厚み
CLIP_CLR = 0.2                             # 受けの側面・耳の上端との隙間
CLIP_BARB_H = 0.5                          # 爪の出っ張り（脚の内面から。受けの側面に対し 0.3 食い込む）
CLIP_BARB_FLAT = 0.8                       # 爪の平らな頂の高さ（両側 45 度）
CLIP_BARB_Z = 16.3                         # 爪の中心の高さ（受けの上面 18.2 より下）
CLIP_GROOVE_SLACK = 0.3                    # 窪みの Y の余裕（爪の両側）。窪みの Y の端は閉じている = クリップは Y へ滑らない
CLIP_GROOVE_D = 0.7                        # 受けの側面の窪みの深さ（天井は 45 度で張り出さない。爪の頂から 0.2 の遊び = 上へ 0.2 浮いたところで引っ掛かる）
# 脚のしなり: 板の下面（30.4）から爪（16.3）まで L = 14.1、たわみ δ = 0.3 → ひずみ ε = 3tδ/(2L²) = 3x1.6x0.3/(2x14.1²) = 0.36%（PLA 2% 以下）、
# 1 本を押し広げる力 = 3EI/L³ x δ = 3x3000x1.91/14.1³ x 0.3 = 1.8N

# --- 内側の補強（壁が揺れない。PLA / PETG で薄い壁は揺れる）----------------------------------------------
GUSSET_T = 3.0                             # 三角リブの厚み
GUSSET_H = 40.0                            # 三角リブの高さ（底から 40mm。カムの下端 40.5 以下）
GUSSET_Y_DEPTH = 8.0                       # ±Y 壁のリブの出（底で 8、上へ向かって 0）
GUSSET_Y_X = (-40.0, -26.0, -12.0, 28.0, 40.0)   # X の位置。配線の窓（X 11.2..19.2）と、窓を抜けるコネクタの通り道を避ける
GUSSET_X_DEPTH = 6.0                       # ±X 壁のリブの出
GUSSET_X_Y = (-40.0, -28.0, 28.0, 40.0)    # Y の位置。受けの回転円（Y ±20.6）の外

# --- ベゼル ------------------------------------------------------------------------------------
WIN = mm(P.WINDOW)                         # 窓（15.4）
WIN_MOUTH = 0.3                            # 窓の上縁の面取り（0.3）。見える桟は 1.6 - 0.6 = 1.0 の平らが残る
WIN_MOUTH_IN = 0.4                         # 窓の下側（画素の頭が下から入る側。ベゼルの下面）の面取り（0.4）。25 個の頭を同時に通す。桟の下面は 0.8 の平らが残る
BEZEL_Z0 = Z_SEAM
BEZEL_Z1 = Z_TOP

# --- 見える面の判定用の閾値（組立姿勢）-----------------------------------------------------------------
VISIBLE_OUTER = 46.75                      # 外装の見える面 = 外側 1.25mm の層（窪みの底 46.7 の内側は見えない）


# =============================================================================================
# 作図の道具
# =============================================================================================
def _link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _from_pydata(name, verts, faces):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in verts]
    for f in faces:
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return _link(bpy.data.objects.new(name, mesh))


def prism(poly, axis, a0, a1, name="p"):
    """凸多角形（poly = 2 次元の点列）を axis に押し出す。axis 'x': poly = (y, z)、'y': (x, z)、'z': (x, y)"""
    n = len(poly)

    def p3(u, v, a):
        if axis == "x":
            return (a, u, v)
        if axis == "y":
            return (u, a, v)
        return (u, v, a)

    verts = [p3(u, v, a0) for u, v in poly] + [p3(u, v, a1) for u, v in poly]
    faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j, n + i])
    return _from_pydata(name, verts, faces)


def box(x0, x1, y0, y1, z0, z1, name="b"):
    return prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "z", z0, z1, name)


def frustum_z(cx, cy, w0, d0, w1, d1, z0, z1, name="f"):
    """下 z0 の矩形（w0 x d0）から上 z1 の矩形（w1 x d1）へ広がる（または狭まる）四角錐台"""
    r0 = [(cx - w0 / 2, cy - d0 / 2), (cx + w0 / 2, cy - d0 / 2), (cx + w0 / 2, cy + d0 / 2), (cx - w0 / 2, cy + d0 / 2)]
    r1 = [(cx - w1 / 2, cy - d1 / 2), (cx + w1 / 2, cy - d1 / 2), (cx + w1 / 2, cy + d1 / 2), (cx - w1 / 2, cy + d1 / 2)]
    verts = [(x, y, z0) for x, y in r0] + [(x, y, z1) for x, y in r1]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7]]
    for i in range(4):
        j = (i + 1) % 4
        faces.append([i, j, 4 + j, 4 + i])
    return _from_pydata(name, verts, faces)


def circle_pts(cy, cz, r, n=FN):
    """外接円（多角形の頂点が半径 r / cos(pi/n) の円上にある。辺の中点で半径 r を割らない）"""
    R = r / math.cos(math.pi / n)
    return [(cy + R * math.cos(2 * math.pi * k / n), cz + R * math.sin(2 * math.pi * k / n)) for k in range(n)]


def cyl_x(cy, cz, r, x0, x1, name="c"):
    return prism(circle_pts(cy, cz, r), "x", x0, x1, name)


def mirror_poly(poly):
    return [(-u, v) for u, v in poly][::-1]


def _boolean(target, tools, op, name):
    """tools をまとめて 1 回の EXACT で適用する（コレクション方式）。重なる道具どうしは自己交差として解く"""
    if not tools:
        return target
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    for t in tools:
        for c in list(t.users_collection):
            c.objects.unlink(t)
        coll.objects.link(t)
    mod = target.modifiers.new(name, "BOOLEAN")
    mod.operation = op
    mod.solver = "EXACT"
    mod.operand_type = "COLLECTION"
    mod.collection = coll
    mod.use_self = True
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for t in tools:
        bpy.data.objects.remove(t, do_unlink=True)
    bpy.data.collections.remove(coll)
    _clean(target)
    return target


def union(target, tools, name="union"):
    return _boolean(target, tools, "UNION", name)


def cut(target, tools, name="cut"):
    return _boolean(target, tools, "DIFFERENCE", name)


def _clean(ob, dist=1e-4):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def bevel(ob, pick, width):
    """pick(v0, v1) が True の辺を width の 45 度の面取りにする"""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    edges = [e for e in bm.edges if pick(e.verts[0].co, e.verts[1].co)]
    bmesh.ops.bevel(bm, geom=edges, offset=width, offset_type="OFFSET", segments=1, profile=0.5, affect="EDGES")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def _isclose(a, b, t=1e-6):
    return abs(a - b) < t


def finish(ob, name):
    """mm の作図を m へ。名前を id にする"""
    ob.name = name
    ob.data.name = name
    ob.data.transform(Matrix.Scale(0.001, 4))
    ob.data.update()
    return ob


# =============================================================================================
# housing
# =============================================================================================
def _tongue_y(yc):
    """舌の Y の配置。(向き d, 根元 Y, 先 Y, 爪の Y 範囲)。先は窓の中心から d 向きへ TONGUE_L / 2、根元は反対側"""
    d = 1.0 if yc > 0 else -1.0
    y_root, y_free = yc - d * TONGUE_L / 2, yc + d * TONGUE_L / 2
    hy0, hy1 = sorted((yc + d * HOOK_Y0, yc + d * HOOK_Y1))
    return d, y_root, y_free, hy0, hy1


def _servo_block_y(side):
    """耳の受け（底の台 + 柵 + 奥の壁）の Y の範囲"""
    if side < 0:
        return EAR_Y0 - SERVO_CLR - BACK_T, BODY_Y0 - SERVO_CLR
    return BODY_Y1 + SERVO_CLR, EAR_Y1 + SERVO_CLR + BACK_T


BLOCK_X0 = EAR_X0 - EAR_GAP - EAR_FENCE_T          # 受けの X（24.4..30.0）
BLOCK_X1 = EAR_X1 + EAR_GAP + EAR_FENCE_T
EAR_TOP = EAR_Z0 + mm(P.SG.BODY_W)                 # 耳の上端（30.2）


def _clip_barb_polys():
    """爪の断面（X-Z）。-X 側の脚と +X 側の脚。脚の内面から出る台形（両側 45 度）。脚へ 0.3 食い込ませて結合"""
    h, f = CLIP_BARB_H, CLIP_BARB_FLAT / 2
    xa = BLOCK_X0 - CLIP_CLR                         # -X 側の脚の内面
    a = [(xa - 0.3, CLIP_BARB_Z - f - h - 0.3), (xa + h, CLIP_BARB_Z - f), (xa + h, CLIP_BARB_Z + f), (xa - 0.3, CLIP_BARB_Z + f + h + 0.3)]
    xc = (BLOCK_X0 + BLOCK_X1) / 2
    b = [(2 * xc - x, z) for x, z in a][::-1]
    return a, b


def _clip_grooves():
    """受けの側面の窪みの断面（X-Z）。-X 側と +X 側。爪の頂の上下に 0.2 の遊び、深さ CLIP_GROOVE_D、両側 45 度"""
    h, f = CLIP_BARB_H, CLIP_BARB_FLAT / 2
    xa = BLOCK_X0 - CLIP_CLR
    tip = xa + h
    gx = BLOCK_X0 + CLIP_GROOVE_D
    half_tip = f + 0.2
    half_out = half_tip + (tip - (xa - 0.3))
    half_bot = half_tip - (gx - tip)
    a = [(xa - 0.3, CLIP_BARB_Z - half_out), (gx, CLIP_BARB_Z - half_bot), (gx, CLIP_BARB_Z + half_bot), (xa - 0.3, CLIP_BARB_Z + half_out)]
    xc = (BLOCK_X0 + BLOCK_X1) / 2
    b = [(2 * xc - x, z) for x, z in a][::-1]
    return a, b


def build_housing():
    # 外形: 96 x 96 x 93。縦の 4 辺と底の 4 辺を面取り。上端（継ぎ目）は面取りしない
    base = box(-HALF, HALF, -HALF, HALF, 0.0, Z_SEAM, "housing")

    def outer_edge(a, b):
        vertical = _isclose(a.x, b.x) and _isclose(a.y, b.y)
        bottom = _isclose(a.z, 0.0) and _isclose(b.z, 0.0)
        return vertical or bottom

    bevel(base, outer_edge, CHAMFER)
    cut(base, [box(-IX, IX, -IY, IY, FLOOR, Z_SEAM + 1.0, "cavity")], "cavity")

    adds = []

    # --- 軸受けの帯（±X の壁の内側。5 本の軸の U 溝を切る）---------------------------------------------
    # 帯の断面（X-Z）: 内面 43.8、上面 Zc+3.45、下は壁へ向かって 45 度（張り出しが 45 度を超えない）。壁へ 0.5 食い込ませて結合
    pad = [(PAD_X0, PAD_BOT), (PAD_X0, PAD_TOP), (PAD_X1 + 0.5, PAD_TOP), (PAD_X1 + 0.5, PAD_BOT - PAD_UNDER - 0.5)]
    adds.append(prism(pad, "y", -IY - 0.5, IY + 0.5, "pad_p"))
    adds.append(prism(mirror_poly(pad), "y", -IY - 0.5, IY + 0.5, "pad_m"))

    # --- 案内板を受ける出っ張り（±Y の壁）。上面が板の下面。下は 45 度 -----------------------------------------
    ledge = [(LEDGE_OUT, PLATE_Z0), (IY + 0.5, PLATE_Z0), (IY + 0.5, PLATE_Z0 - LEDGE_W - (IY + 0.5 - LEDGE_OUT)), (LEDGE_OUT, PLATE_Z0 - LEDGE_W)]
    adds.append(prism(ledge, "x", -IX - 0.5, IX + 0.5, "ledge_p"))
    adds.append(prism(mirror_poly(ledge), "x", -IX - 0.5, IX + 0.5, "ledge_m"))

    # --- 壁の補強の三角リブ（底から立ち上がる。斜面は上向きで張り出さない）---------------------------------
    k = GUSSET_Y_DEPTH / (GUSSET_H - FLOOR)
    ytri = [(IY - GUSSET_Y_DEPTH - k * 0.5, FLOOR - 0.5), (IY + 0.5, FLOOR - 0.5), (IY + 0.5, GUSSET_H + 0.5 / k)]
    for x in GUSSET_Y_X:
        adds.append(prism(ytri, "x", x - GUSSET_T / 2, x + GUSSET_T / 2, "gus_yp"))
        adds.append(prism(mirror_poly(ytri), "x", x - GUSSET_T / 2, x + GUSSET_T / 2, "gus_ym"))
    k = GUSSET_X_DEPTH / (GUSSET_H - FLOOR)
    xtri = [(IX - GUSSET_X_DEPTH - k * 0.5, FLOOR - 0.5), (IX + 0.5, FLOOR - 0.5), (IX + 0.5, GUSSET_H + 0.5 / k)]
    for y in GUSSET_X_Y:
        adds.append(prism(xtri, "y", y - GUSSET_T / 2, y + GUSSET_T / 2, "gus_xp"))
        adds.append(prism(mirror_poly(xtri), "y", y - GUSSET_T / 2, y + GUSSET_T / 2, "gus_xm"))

    # --- SG92R の受け台 ---------------------------------------------------------------------------------
    # 取付耳（X 26.2..28.2、Y の両端 4.5mm ずつ）を、柵 2 枚で挟んで落とし込む。柵の内面に縦の潰しリブ（片側 0.1 の潰し代）で
    # 耳を保持し、前後は奥の壁（0.35 の隙間）で止める。本体の下面は耳の受けと同じ高さの 2 本の受けで水平に支える
    fx0a, fx0b = EAR_X0 - EAR_GAP - EAR_FENCE_T, EAR_X0 - EAR_GAP     # 柵 A（-X 側）の X
    fx1a, fx1b = EAR_X1 + EAR_GAP, EAR_X1 + EAR_GAP + EAR_FENCE_T     # 柵 B（+X 側）の X
    # 柵の断面（X-Z）。内面の上の角は 45 度の面取り 0.8（耳が入りやすい）
    fa = [(fx0a, EAR_Z0 - 0.7), (fx0b, EAR_Z0 - 0.7), (fx0b, FENCE_TOP - 0.8), (fx0b - 0.8, FENCE_TOP), (fx0a, FENCE_TOP)]
    fb = [(fx1b, EAR_Z0 - 0.7), (fx1a, EAR_Z0 - 0.7), (fx1a, FENCE_TOP - 0.8), (fx1a + 0.8, FENCE_TOP), (fx1b, FENCE_TOP)]
    # 潰しリブの断面（X-Z）。先端の上は 45 度で、耳の下端から入りやすい
    ra = [(fx0b - 0.4, EAR_Z0 - 0.2), (fx0b + EAR_RIB_H, EAR_Z0 - 0.2), (fx0b + EAR_RIB_H, FENCE_TOP - 1.6),
          (fx0b - 0.4, FENCE_TOP - 1.6 + EAR_RIB_H + 0.4)]
    rb = [(fx1a + 0.4, EAR_Z0 - 0.2), (fx1a - EAR_RIB_H, EAR_Z0 - 0.2), (fx1a - EAR_RIB_H, FENCE_TOP - 1.6),
          (fx1a + 0.4, FENCE_TOP - 1.6 + EAR_RIB_H + 0.4)]
    for side in (-1, +1):
        if side < 0:
            y_in = BODY_Y0 - SERVO_CLR          # 柵の本体側の端（-16.85）
            y_end = EAR_Y0 - SERVO_CLR          # 耳の先の隙間の面（-21.35）= 奥の壁の内面
            yb0, yb1 = y_end - BACK_T, y_in
            fy0, fy1 = y_end - BACK_T, y_in
            rib_y = (y_end + 0.9, y_in - 1.5)
        else:
            y_in = BODY_Y1 + SERVO_CLR
            y_end = EAR_Y1 + SERVO_CLR
            yb0, yb1 = y_in, y_end + BACK_T
            fy0, fy1 = y_in, y_end + BACK_T
            rib_y = (y_in + 1.5, y_end - 0.9)
        # 底の受け（耳の下面と同じ高さ。X 24.4..30.0）。耳はこの面に座る
        adds.append(box(fx0a, fx1b, yb0, yb1, FLOOR - 0.5, EAR_Z0, "ear_block"))
        adds.append(prism(fa, "y", fy0, fy1, "fence_a"))
        adds.append(prism(fb, "y", fy0, fy1, "fence_b"))
        # 奥の壁（柵をつなぐ）
        ya, yb = (y_end - BACK_T, y_end) if side < 0 else (y_end, y_end + BACK_T)
        adds.append(box(fx0a, fx1b, ya, yb, FLOOR - 0.5, FENCE_TOP, "back_wall"))
        # 奥の壁の外側の三角リブ（床から 22mm まで、Y へ 6mm 出る）。立ての比を下げる
        gk = 6.0 / (22.2 - FLOOR)
        if side < 0:
            tri = [(yb0 - 6.0 - gk * 0.5, FLOOR - 0.5), (yb0 + 0.5, FLOOR - 0.5), (yb0 + 0.5, 22.2 + 0.5 / gk)]
        else:
            tri = [(yb1 + 6.0 + gk * 0.5, FLOOR - 0.5), (yb1 - 0.5, FLOOR - 0.5), (yb1 - 0.5, 22.2 + 0.5 / gk)]
        xmid = (fx0a + fx1b) / 2
        adds.append(prism(tri, "x", xmid - 1.5, xmid + 1.5, "back_gusset"))
        for ry in rib_y:
            adds.append(prism(ra, "y", ry - EAR_RIB_W / 2, ry + EAR_RIB_W / 2, "rib_a"))
            adds.append(prism(rb, "y", ry - EAR_RIB_W / 2, ry + EAR_RIB_W / 2, "rib_b"))
    # 本体の下の 2 本の受け（Y は本体の面の内側）。本体の下面との隙間 0.2
    for xa, xb in RIB_UNDER_X:
        adds.append(box(xa, xb, BODY_Y0 + 0.5, BODY_Y1 - 0.5, FLOOR - 0.5, EAR_Z0 - RIB_UNDER_GAP, "under_rib"))

    union(base, adds, "adds")

    cuts = []

    # --- 軸の U 溝（5 本 x 2 端）。上が開く。入口は 45 度の面取り -------------------------------------------
    for j in range(P.N):
        yj = AXIS_Y[j]
        for sign in (-1, +1):
            xa, xb = (PAD_X0 - 0.5, PAD_X1 + U_DEEP) if sign > 0 else (-PAD_X1 - U_DEEP, -PAD_X0 + 0.5)
            cuts.append(box(xa, xb, yj - U_W / 2, yj + U_W / 2, ZC + U_UP, PAD_TOP + 0.5, "u_box"))
            cuts.append(cyl_x(yj, ZC + U_UP, U_W / 2, xa, xb, "u_round"))     # 底は Zc - 3.25。軸の丸（R3.2）が載って中心が Zc - 0.05
            top = PAD_TOP
            mouth = [(yj - U_W / 2, top - U_MOUTH), (yj + U_W / 2, top - U_MOUTH),
                     (yj + U_W / 2 + U_MOUTH + 0.5, top + 0.5), (yj - U_W / 2 - U_MOUTH - 0.5, top + 0.5)]
            cuts.append(prism(mouth, "x", xa, xb, "u_mouth"))
            # 栓の外側の肉（板の端 44.8 から 45.4）の縦の溝。壁の内面から 0.7、溝の中心から外装の上端まで通す（案内板を上から降ろすとき栓の外側が壁を通る）。天井が無い
            ra_, rb_ = (IX - 0.1, IX + U_RECESS_D) if sign > 0 else (-IX - U_RECESS_D, -IX + 0.1)
            z_r = ZC + U_UP
            cuts.append(box(ra_, rb_, yj - U_W / 2, yj + U_W / 2, z_r, Z_SEAM + 1.0, "u_recess"))

    # --- 押さえクリップの爪が嵌まる窪み（受けの両側面。天井は 45 度）----------------------------------------------
    for side in (-1, +1):
        yb0, yb1 = _servo_block_y(side)
        yc = (yb0 + yb1) / 2
        gy = CLIP_W / 2 + CLIP_GROOVE_SLACK                   # 窪みの Y の半分。端は閉じる
        for poly in _clip_grooves():
            cuts.append(prism(poly, "y", yc - gy, yc + gy, "clip_groove"))

    # --- ベゼルの爪が掛かる窪み（±X の端壁の内面）。天井は 45 度 -----------------------------------------------
    flat = BARB_FLAT / 2
    half_base = flat + POCKET_DEPTH                      # 壁の内面での窪みの高さの半分（45 度の斜面）
    for sgn in (-1, +1):
        pk = [(IX - 0.5, BARB_Z - half_base - 0.5), (IX + POCKET_DEPTH, BARB_Z - flat),
              (IX + POCKET_DEPTH, BARB_Z + flat), (IX - 0.5, BARB_Z + half_base + 0.5)]
        if sgn < 0:
            pk = mirror_poly(pk)
        for y in BARB_Y:
            cuts.append(prism(pk, "y", y - POCKET_L / 2, y + POCKET_L / 2, "pocket"))

    # --- 案内板の舌の爪が入る窪み（±X の端壁の内面）。天井は水平から 15 度（爪の上面と平行、0.05 上）-------------------
    ceil0 = mm(P.PLATE_LIP_BOT)                                # 窪みの天井の、壁の内面（板の端）での高さ（83.45）
    for sgn in (-1, +1):
        x_a, x_b = IX - 0.5, IX + POCKET_PLATE_DEPTH
        pk = [(x_a, ceil0 - (x_a - (IX - FIT)) * HOOK_TOP_SLOPE), (x_b, ceil0 - (x_b - (IX - FIT)) * HOOK_TOP_SLOPE),
              (x_b, ceil0 - 2.1), (x_a, ceil0 - 2.1 - (x_b - x_a))]
        if sgn < 0:
            pk = mirror_poly(pk)
        for yc in TONGUE_YC:
            _, _, _, hy0, hy1 = _tongue_y(yc)
            cuts.append(prism(pk, "y", hy0 - POCKET_PLATE_PAD, hy1 + POCKET_PLATE_PAD, "pocket_plate"))

    # --- 配線の窓（+Y 壁）。上は 45 度の尖り屋根（橋も支えも無い）---------------------------------------------------
    zw0 = ZS - WIN_H / 2
    xw0, xw1 = WIN_X - WIN_W / 2, WIN_X + WIN_W / 2
    zs_top = zw0 + WIN_SIDE_H
    win = [(xw0, zw0), (xw1, zw0), (xw1, zs_top), (WIN_X, zs_top + WIN_W / 2), (xw0, zs_top)]      # 垂直な辺 + 45 度の尖り屋根
    cuts.append(prism(win, "y", IY - 0.5, HALF + 0.5, "wire_window"))

    # --- 端壁の指の掛かり（ベゼルの下面の縁に爪を掛けて持ち上げる）---------------------------------------------
    for sgn in (-1, +1):
        xa, xb = (HALF - FINGER_D, HALF + 0.5) if sgn > 0 else (-HALF - 0.5, -HALF + FINGER_D)
        for fy in FINGER_Y:
            cuts.append(box(xa, xb, fy - FINGER_W / 2, fy + FINGER_W / 2, Z_SEAM - FINGER_H, Z_SEAM + 0.5, "finger"))

    # --- 受けのピンの止まり穴（+X 端壁の内面。涙形で、天井が 45 度）---------------------------------------------
    r = mm(P.RECV_WALL_HOLE_D) / 2
    xb = mm(P.RECV_WALL_HOLE_BOTTOM)
    cuts.append(cyl_x(0.0, ZS, r, IX - 0.5, xb, "pin_hole"))
    s = r / math.sqrt(2)
    tear = [(-s, ZS + s), (s, ZS + s), (0.0, ZS + r * math.sqrt(2))]
    cuts.append(prism(tear, "x", IX - 0.5, xb, "pin_tear"))
    # ピンの降ろし溝: ピンの先は壁の内面より 0.3 出る（45.3 > 45）。サーボ一式は -X へ 1.8 寄せて降ろし、最終位置の 15mm 上で +X へ戻す
    # 経路なので、溝は穴の高さからその上のピンの半径まで（Z 41.7）だけでよい。パッドの帯（下端 45.0）とは 1.2mm 以上空ける: 上は 45 度で細め、
    # 平らな頂 1.0 は Z 43.7（帯の下端から 1.3）。深さはピンの先から 0.3 深い 45.6
    z_g = ZS + 15.0 + mm(P.RECV_PIN_D) / 2 + 0.5
    groove = [(-r, ZS), (r, ZS), (r, z_g), (0.5, z_g + r - 0.5), (-0.5, z_g + r - 0.5), (-r, z_g)]
    cuts.append(prism(groove, "x", IX - 0.5, mm(P.RECV_PIN_X1) + 0.3, "pin_groove"))

    cut(base, cuts, "features")
    return finish(base, "housing")


# =============================================================================================
# guide_plate
# =============================================================================================
def build_guide_plate():
    px, py = IX - FIT, IY - FIT                         # 板の X, Y の半分（44.8, 45.8）
    plate = box(-px, px, -py, py, PLATE_Z0, PLATE_Z1, "guide_plate")
    # 落下止め: 軸受けの U 溝の上へ入る栓（軸ごと、両端）
    adds = []
    for j in range(P.N):
        yj = AXIS_Y[j]
        for sign in (-1, +1):
            def bx(x0, x1, z0, z1, nm):
                xa, xb = sorted((sign * x0, sign * x1))
                return box(xa, xb, yj - PLUG_W / 2, yj + PLUG_W / 2, z0, z1, nm)
            adds.append(bx(PLUG_X_LO, px, PLUG_BOT, PLATE_Z0 + 0.5, "plug"))                       # 下から板まで（厚み 0.9 + 外の部分）
            adds.append(bx(px - 0.3, PLUG_X_OUT, PLUG_BOT, PLATE_Z0 + 0.1, "plug_out"))              # 板の端の外へ出る部分（壁の縦溝に入る。板の下面まで通す）
    # 舌の爪（板の端から出る。上面は外へ下がる 15 度、先は垂直に HOOK_TIP_H、下は 45 度の斜面）
    for sign in (-1, +1):
        for yc in TONGUE_YC:
            ht = PLATE_Z1
            tip_top = ht - HOOK_H * HOOK_TOP_SLOPE
            hp = [(px - 0.3, ht - 0.05), (px, ht), (px + HOOK_H, tip_top), (px + HOOK_H, tip_top - HOOK_TIP_H),
                  (px - 0.3, tip_top - HOOK_TIP_H - HOOK_H - 0.3)]
            hp = [(sign * u, v) for u, v in hp]
            if sign < 0:
                hp = hp[::-1]
            d, _, _, hy0, hy1 = _tongue_y(yc)
            adds.append(prism(hp, "y", hy0, hy1, "hook"))
    union(plate, adds, "plugs")
    # 舌の切り込み: 側面（X 43.0..43.6）と先の端（Y）と下面を切って、根元（-Y 側）だけ板につなぐ
    tcut = []
    zt0 = PLATE_Z1 - TONGUE_H
    for sign in (-1, +1):
        for yc in TONGUE_YC:
            d, y_root, y_free, _, _ = _tongue_y(yc)
            xi = px - TONGUE_T - TONGUE_SLIT               # 側面の切り込みの内面（43.0）
            y_end = y_free + d * TONGUE_SLIT               # 先の端の切り込みの外側
            def tb(x0, x1, y0, y1, z0, z1, nm):
                a_, b_ = sorted((sign * x0, sign * x1))
                return box(a_, b_, y0, y1, z0, z1, nm)
            ya, yb = sorted((y_root, y_end))
            ea, eb = sorted((y_free, y_end))
            tcut.append(tb(xi, px - TONGUE_T, ya, yb, zt0 - TONGUE_SLIT, PLATE_Z1 + 0.5, "slit_side"))
            tcut.append(tb(xi, px + 1.0, ea, eb, zt0 - TONGUE_SLIT, PLATE_Z1 + 0.5, "slit_end"))
            tcut.append(tb(xi, px + 1.0, ya, yb, zt0 - TONGUE_SLIT, zt0, "slit_under"))
    cut(plate, tcut, "tongues")
    cuts = []
    for j in range(P.N):
        for i in range(P.N):
            cx, cy = CAM_X[j][i], AXIS_Y[j]
            cuts.append(box(cx - HOLE_W / 2, cx + HOLE_W / 2, cy - HOLE_W / 2, cy + HOLE_W / 2, PLATE_Z0 - 0.5, PLATE_Z1 + 0.5, "hole"))
            cuts.append(box(cx - SLOT_X / 2, cx + SLOT_X / 2, cy - SLOT_Y / 2, cy + SLOT_Y / 2, PLATE_Z0 - 0.5, PLATE_Z1 + 0.5, "slot"))
            # ベッド側（板の上面）の縁の面取り。茎（9）と足（4.6 x 20）が通る穴を、最初の層の膨らみから守る
            m = HOLE_MOUTH
            cuts.append(frustum_z(cx, cy, HOLE_W, HOLE_W, HOLE_W + 2 * (m + 0.5), HOLE_W + 2 * (m + 0.5), PLATE_Z1 - m, PLATE_Z1 + 0.5, "hole_m"))
            cuts.append(frustum_z(cx, cy, SLOT_X, SLOT_Y, SLOT_X + 2 * (m + 0.5), SLOT_Y + 2 * (m + 0.5), PLATE_Z1 - m, PLATE_Z1 + 0.5, "slot_m"))
    cut(plate, cuts, "holes")
    return finish(plate, "guide_plate")


# =============================================================================================
# bezel
# =============================================================================================
def build_bezel():
    base = box(-HALF, HALF, -HALF, HALF, BEZEL_Z0, BEZEL_Z1, "bezel")

    def outer_edge(a, b):
        vertical = _isclose(a.x, b.x) and _isclose(a.y, b.y)
        top = _isclose(a.z, BEZEL_Z1) and _isclose(b.z, BEZEL_Z1)
        return vertical or top

    bevel(base, outer_edge, CHAMFER)

    adds = []
    # 縁: 板の上へ載り、壁の内側へ入る。ベゼルの位置決めと板の押さえ
    lx, ly = IX - FIT, IY - FIT
    ring = box(-lx, lx, -ly, ly, LIP_BOT, BEZEL_Z0 + 0.5, "lip_out")
    adds.append(ring)
    # 爪: ±X の縁の外側。両側 45 度の台形（端壁の窪みに嵌まる。±Y の壁は窪みで 1.3mm まで薄くなるので使わない）
    flat = BARB_FLAT / 2
    hb = flat + BARB_H
    for sgn in (-1, +1):
        bp = [(lx - 0.5, BARB_Z - hb - 0.5), (lx + BARB_H, BARB_Z - flat), (lx + BARB_H, BARB_Z + flat), (lx - 0.5, BARB_Z + hb + 0.5)]
        if sgn < 0:
            bp = mirror_poly(bp)
        for y in BARB_Y:
            adds.append(prism(bp, "y", y - BARB_L / 2, y + BARB_L / 2, "barb"))
    union(base, adds, "lip")
    # 縁の内側をくり抜く（厚み 1.6）。窓と同時に切る
    cuts = [box(-(lx - LIP_T), lx - LIP_T, -(ly - LIP_T), ly - LIP_T, LIP_BOT - 1.0, BEZEL_Z0, "lip_in")]
    for j in range(P.N):
        for i in range(P.N):
            cx, cy = mm(K.col_x(i)), AXIS_Y[j]
            cuts.append(box(cx - WIN / 2, cx + WIN / 2, cy - WIN / 2, cy + WIN / 2, BEZEL_Z0 - 0.5, BEZEL_Z1 + 0.5, "window"))
            m = WIN_MOUTH
            cuts.append(frustum_z(cx, cy, WIN, WIN, WIN + 2 * (m + 0.5), WIN + 2 * (m + 0.5), BEZEL_Z1 - m, BEZEL_Z1 + 0.5, "window_m"))
            mi = WIN_MOUTH_IN
            cuts.append(frustum_z(cx, cy, WIN + 2 * (mi + 0.5), WIN + 2 * (mi + 0.5), WIN, WIN, BEZEL_Z0 - 0.5, BEZEL_Z0 + mi, "window_in"))
    cut(base, cuts, "windows")
    return finish(base, "bezel")


# =============================================================================================
# sg92r / sg92r_horn（正本の STL を組立姿勢へ）
# =============================================================================================
def _read_stl(path):
    with open(path, "rb") as f:
        d = f.read()
    n = struct.unpack("<I", d[80:84])[0]
    a = np.frombuffer(d[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return a["v"].reshape(-1, 3).astype(np.float64)


def native_to_world(v):
    """native（x, y, z）[mm] -> 世界。X = XS0 + z、Y = x、Z = Zs + y"""
    return np.stack([XS0 + v[:, 2], v[:, 0], ZS + v[:, 1]], axis=1)


def _servo_object(name, parts, rot_deg=0.0):
    """rot_deg: 出力軸（Y=0, Z=Zs の X 軸）まわりに回す角（度、+Y から +Z へ）。本体と配線は 0、ホーンだけ HORN_ROT_DEG"""
    verts_all, faces_all = [], []
    base = 0
    for part in parts:
        path = os.path.join(EXPORTS, f"sg92r-photo-{part}.stl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} がありません。先に models/sg92r-photo/model.py をヘッドレスで実行してください")
        v = native_to_world(_read_stl(path))
        if rot_deg:
            a = math.radians(rot_deg)
            y, z = v[:, 1].copy(), v[:, 2] - ZS
            v[:, 1] = y * math.cos(a) - z * math.sin(a)
            v[:, 2] = ZS + y * math.sin(a) + z * math.cos(a)
        key = np.round(v, 4)
        u, inv = np.unique(key, axis=0, return_inverse=True)
        f = inv.reshape(-1, 3) + base
        verts_all.append(u)
        faces_all.append(f)
        base += len(u)
    verts = np.concatenate(verts_all)
    faces = np.concatenate(faces_all)
    ok = ~((faces[:, 0] == faces[:, 1]) | (faces[:, 1] == faces[:, 2]) | (faces[:, 0] == faces[:, 2]))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts.tolist(), [], faces[ok].tolist())
    mesh.update()
    return _link(bpy.data.objects.new(name, mesh))


def build_sg92r():
    return finish(_servo_object("sg92r", ["body", "wire"]), "sg92r")


def build_sg92r_horn():
    return finish(_servo_object("sg92r_horn", ["horn"], HORN_ROT_DEG), "sg92r_horn")


# =============================================================================================
# servo_clip
# =============================================================================================
def build_servo_clip(side):
    name = "servo_clip_0" if side < 0 else "servo_clip_1"
    yb0, yb1 = _servo_block_y(side)
    yc = (yb0 + yb1) / 2
    y0, y1 = yc - CLIP_W / 2, yc + CLIP_W / 2
    xa, xb = BLOCK_X0 - CLIP_CLR, BLOCK_X1 + CLIP_CLR            # 脚の内面
    z_bar0 = EAR_TOP + CLIP_CLR
    z_bar1 = z_bar0 + CLIP_BAR_T
    z_bot = CLIP_BARB_Z - (CLIP_BARB_FLAT / 2 + CLIP_BARB_H + 0.3)   # 爪の根元（脚へ 0.3 食い込む分まで）の下。ここを爪の根元より上にすると脚の下に 0.3 のとげが出る
    ob = box(xa - CLIP_LEG_T, xb + CLIP_LEG_T, y0, y1, z_bar0, z_bar1, name)
    parts = [box(xa - CLIP_LEG_T, xa, y0, y1, z_bot, z_bar0 + 0.5, "leg_a"),
             box(xb, xb + CLIP_LEG_T, y0, y1, z_bot, z_bar0 + 0.5, "leg_b")]
    for poly in _clip_barb_polys():
        parts.append(prism(poly, "y", y0, y1, "barb"))
    union(ob, parts, "clip")
    return finish(ob, name)


# =============================================================================================
# 公開
# =============================================================================================
def build_static():
    """静止部品を作って {id: Object} を返す（組立姿勢、m）。シーンは消さない"""
    return {
        "housing": build_housing(),
        "bezel": build_bezel(),
        "guide_plate": build_guide_plate(),
        "sg92r": build_sg92r(),
        "sg92r_horn": build_sg92r_horn(),
        "servo_clip_0": build_servo_clip(-1),
        "servo_clip_1": build_servo_clip(+1),
    }


# 刷る向き。rot_deg は回転オイラー XYZ（度）。回したあと、最下点を z=0、XY の外接の中心を原点に置く
PRINT_POSE = {
    "housing": {
        "rot_deg": [0, 0, 0],
        "reason": "底（Z=0）をベッドに置く。外装の 5 面（底・±X・±Y）は接地か垂直。内側の張り出し（軸受けの帯・案内板の受け・窪み・天井）は"
                  "すべて 45 度の斜面か、見えない面の短い橋（配線の窓の天井 5mm）",
        "support": "なし",
    },
    "bezel": {
        "rot_deg": [180, 0, 0],
        "reason": "見える上面（Z=96）をベッドに置く。縁・爪は上へ立つ。上面の稜の 45 度の面取りが接地面を 1mm 縮めて、最初の層の膨らみを逃がす",
        "support": "なし",
    },
    "guide_plate": {
        "rot_deg": [180, 0, 0],
        "reason": "板の上面（画素側）をベッドに置く。落下止めは上へ立つ。穴の縁の面取り 0.3 がベッド側に来て、最初の層の膨らみから穴の隙間を守る",
        "support": "なし",
    },
    "servo_clip_0": {
        "rot_deg": [90, 0, 0],
        "reason": "Y 面を下にして寝かせる。U 字の断面（XZ 面）が層の面内に入るので、脚のしなり（X 方向）が層に沿う。爪は両側 45 度",
        "support": "なし",
    },
    "servo_clip_1": {
        "rot_deg": [90, 0, 0],
        "reason": "servo_clip_0 と同じ（Y 面を下にして寝かせる）",
        "support": "なし",
    },
    "sg92r": None,
    "sg92r_horn": None,
}


def _housing_visible(c, n):
    """外装の見える面: 外側 1.25mm の層（外周の面と面取り、配線の窓・指の掛かりの面）と底"""
    return abs(c[0]) >= VISIBLE_OUTER or abs(c[1]) >= VISIBLE_OUTER or c[2] <= 0.05


def _bezel_visible(c, n):
    """ベゼル: 継ぎ目（Z=93）より上の面 = 上面・外周・面取り・窓の壁（凹んだ画素の上に見える）。縁と爪と下面は見えない"""
    return c[2] >= Z_SEAM + 1e-3


VISIBLE_FACE = {
    "housing": _housing_visible,
    "bezel": _bezel_visible,
    "guide_plate": lambda c, n: False,
    "servo_clip_0": lambda c, n: False,
    "servo_clip_1": lambda c, n: False,
}
