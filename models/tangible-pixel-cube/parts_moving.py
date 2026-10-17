"""タンジブル画素キューブの動く部品の形（bpy）。静止部品と統合は別担当。寸法は params.py だけから読む。

build_moving() が全部品を組立姿勢（サーボ THETA_FLAT = 90 度、全軸 phi = 0、画素は面一）で作って返す。
オブジェクト名 = 部品 id、単位 m。PRINT_POSE は各部品を刷る向きにする回転（オイラー XYZ 度）と理由。

座標: X = 軸方向、(u, v) = (Y, Z)。軸まわりの極角 psi は +Y から +Z へ測る（kinematics と同じ）。内部は mm で組み、最後に 1/1000 する。
部品: camshaft_j（胴 Ø10 + 板カム 5 枚の一体）, gear_j, pixel_i_j, horn_coupler, phase_comb（i = 列 = X、j = 行 = Y）。

統合側への申し送り:
- 全部品はワールド座標（原点 = 箱の底面の中心）で、オブジェクトの変換は焼き込み済み（原点 0、回転 0、倍率 1）
- horn_coupler の姿勢: 付属ホーンの長腕（18mm）が -Z、右腕（16mm）が +Z、短腕が Y。sg92r_horn も同じ姿勢（サーボ 90 度）で置く。
  ホーンの腕の下面の X = 受けの -X 面（RECV_HUB_X0 = 40.0）+ 0.1 = 40.1、腕の上面 = ポケットの天井 = 41.6（接する）。ハブは 37.1 から。
  受けの -X 面は歯の面（40.6）より 0.6 -X へ出る（受け全体が平らに刷れるように）
- phase_comb は組立の途中で外す治具で、最終形には残らない
- 軸は camshaft_j（-X の Ø10 軸受け + 胴 + カム 5 枚 + +X の六角の雄スタブ）と gear_j（雌穴 + ハブ + 歯車 + ボス + +X の Ø5 軸受け）の 2 部品。
  刷る向きは PRINT_POSE。camshaft_j は -X 端を下にして立てて刷り、刷るときだけの円盤 Ø30（リブ 4 本で端面とつなぐ）を付ける。
  円盤つきの形は build_moving() のあとに build_print_variants()（{id: Object}、組立姿勢の座標、m）で受け取る。print_<id>.stl はこれを PRINT_POSE で回して書く
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../.."))
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.path.insert(0, HERE)

import bmesh  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix  # noqa: E402

from printmech.geometry import circle, hull, link_obj, loft_rings, prism  # noqa: E402
from printmech.geometry import cut as _cut, union as _union  # noqa: E402
import kinematics as K  # noqa: E402
import params as P  # noqa: E402

MM = 1000.0


def mm(v):
    return v * MM


ZC = mm(P.CAM_AXIS_Z)                       # カム軸の高さ（51.7）
ZS = mm(P.SERVO_AXIS_Z)                     # サーボ出力軸の高さ（24.2）
CAM_T = mm(P.CAM_T)
GEAR_X0 = mm(P.GEAR_X0)
GEAR_X1 = mm(P.GEAR_X1)
LASH = mm(P.GEAR_LASH)                      # 1 噛合のバックラッシュ（0.1）。2 枚で半分ずつ（歯厚を 0.05 ずつ細らせる）

# --- この部品側で足した定数（params に無い。理由を各行に）---------------------------------------
DP_TOL = 0.002                              # カム輪郭の頂点を間引く許容（0.002mm。元の頂点の部分集合なので、輪郭の内側に 0.002 以内。566 点 -> 数十点）
SKIRT_FLOOR = 4.5                           # 円錐の輪の床の半径（胴 R5 の内側 0.5。円錐は胴の面で終わり、床の折れ目は胴の中に隠れる。-X の端の面取り 0.4 の内側にも収まる）
SKIRT_BIAS = 0.01                           # 円錐を板の下面（t = 0）の輪より外へ 0.01 だけ太らせる（t > 0 の輪の半径 = R - t + 0.01）。輪の頂点が胴の面（R5）にちょうど乗ると boolean が 1e-3mm の三角形を出すため。傾きは 45 度より少し立つ（0.24 / 0.25）
SKIRT_STEP = 0.25                           # 円錐の輪の深さの刻み（0.25 < 胴との差 0.5 なので、折れ目の手前の輪は必ず胴の内側）
SKIRT_STOP_MARGIN = 0.1                     # すその頂の半径をさらに 0.1 抑える（円錐が胴の面に着く X を SKIRT_X_MIN より 0.1 +X 側にする。輪の頂点が胴の面にちょうど乗って細い三角形が出るのを避ける）
SKIRT_X_MIN = -mm(P.PAD_X0) + 0.6              # すその -X 側の端の限界（-43.4 = パッドの内面 -44.0 + 0.6。-X の押さえ棒の爪・治具との隙間）。奇数行の cam 0 だけが届く
D_FLAT_X1 = -mm(P.PAD_X0)                   # D 面の +X の端（-44.0）。そこから 45 度の斜面で上がる（円錐のすそは斜面の 0.1 下を平行に走るので、削らない）
RIB_NORMALS = (30, 150, 270)                # 潰しリブを付ける穴の面の法線（度）。切り落とす角（60 度）の側の面（90 度）を避けた 1 面おき
KEY_N = (math.cos(math.radians(P.HEX_KEY_NORMAL_DEG)), math.sin(math.radians(P.HEX_KEY_NORMAL_DEG)))   # 切り落とし面の法線
FIRST_LAYER = mm(P.FIRST_LAYER_CHAMFER)     # 第 1 層の膨らみ対策の面取り（0.3、45 度）
CAM_BORE_PAD = 1.0                          # 穴のカッターの突き出し
COUPLER_WALL = 2.45                         # 受けの肉（長腕の先 18 + 0.15 + 2.45 = 20.6 = RECV_BAR_R）
COUPLER_CAP_R = 17.5                        # 受けの +X 側の蓋（半円）の半径。右腕のポケットの先 16.15 から 1.35 の肉。歯底 17.75 より内
MOUTH_RELIEF = FIRST_LAYER                  # ポケットの口の 45 度の面取り（刷るときベッド側の第 1 層の膨らみを逃がす）
COMB_HANDLE_Y = 7.0                         # 治具の持ち手の Y 半幅
COMB_HANDLE_TOP = mm(P.PLATE_Z0) - 0.6      # 持ち手の上端（案内板の下面 63.5 から 0.6）
JOURNAL_MX_END = 45.6                        # -X の軸受けの端（-45.6）。溝の底（-46.0）から 0.4 離す: -X へ動く軸は、この端が溝の底に当たって止まる（-X には肩が無い。胴も軸受けも Ø10）。+X へは歯車のボスの肩（43.6）が +X のパッドの内面（44.0）に当たって 0.4 で止まる。軸受けが溝（パッドの内面 -44.0 から）にかかる長さ 1.6
COMB_X0 = -44.7                             # 櫛の -X 面（-44.7）。壁の内面（-45.0）から 0.3 内側。壁（-X の押さえ棒の溝は軸ごとの幅だけ）に入らない
COMB_T = 1.6                                # 櫛の厚み（1.6。肉厚の下限 1.2 以上）。+X 面 -43.1
COMB_Y_HALF = 39.0                          # 櫛の Y の半長（39.0。外装の Y 止めの面 39.3 から 0.3）
COMB_EAR_X0, COMB_EAR_X1 = -44.7, -43.4      # 耳の X（厚み 1.3）。-X パッドの上面（X -45.0..-44.0。内縁に面取り 0.5 なので平らなのは -44.5 まで）に座る。座の幅は 0.2、壁の内面から 0.3
COMB_TOOTH_X0, COMB_TOOTH_X1 = -45.3, -44.0     # 歯の X（厚み 1.3）。歯は U 溝の中（壁の溝の幅の中）に入るので、板より -X へ伸ばせる。D 面（X -45.0..-44.0）の上に収まる
COMB_PLATE_GAP = 0.3                        # 櫛の板の下面と -X パッドの上面の隙間（0.3mm。外装との間）
COMB_EAR_H = 3.5                            # 耳の高さ（パッドの上面から。板の上端 4.0 より低くして、耳の上面が板の上端と面一にならないように）
LABEL_H = mm(P.CAM_LABEL_H)                 # 番号の字の高さ（3.0）。1 字の幅 LABEL_DW
LABEL_DW = 1.8                              # 1 字の幅（1.8mm）
LABEL_STROKE = 0.5                          # 番号の線の太さ
LABEL_MARGIN = 0.3                          # 番号と板の縁・胴の余裕
VENT = 3.0                                  # 画素の茎の通気穴（内部の空洞を外へ開けて連結成分を 1 にする。3mm 角、刷るとき橋 3mm）

INFO = {}                                   # run_moving.py が report.json に入れる計算値


# --- 2D の道具 -----------------------------------------------------------------------------
def hex_poly(af):
    """二面幅 af の正六角形（角が ±Y、平らな面が上下）。ccw"""
    r = af / math.sqrt(3.0)
    return [(r * math.cos(math.radians(60 * k)), r * math.sin(math.radians(60 * k))) for k in range(6)]


def clip_half(poly, n, d):
    """多角形を n・p <= d の側だけ残す（Sutherland-Hodgman）"""
    out = []
    m = len(poly)
    for k in range(m):
        a, b = poly[k], poly[(k + 1) % m]
        da = n[0] * a[0] + n[1] * a[1] - d
        db = n[0] * b[0] + n[1] * b[1] - d
        ina, inb = da <= 1e-12, db <= 1e-12
        if ina:
            out.append(a)
        if ina != inb:
            t = da / (da - db)
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out


def shaft_poly():
    """軸の断面: 六角 AF6.5 の 60 度の角を、法線 74 度・中心から 2.74mm の面で切り落とした形（キラル）。ccw、(u, v)"""
    return clip_half(hex_poly(mm(P.SHAFT_AF)), KEY_N, mm(P.HEX_CUT_D))


def bore_poly(ribs=False):
    """カム・歯車の穴の輪郭: 六角 AF6.9 の 60 度の角を、法線 74 度・中心から HEX_CUT_BORE_D（2.94）の面で切り落とした形
    （穴の角が内側へ出っ張る。軸の形を 0.2 外へずらした形）。ribs なら 1 面おきの 3 面（法線 30, 150, 270 度）の中央に潰しリブ（幅 0.6、
    高さ 0.38）の出っ張りを足す。ccw、(u, v)"""
    ap = mm(P.SHAFT_BORE_AF) / 2
    r = ap * 2 / math.sqrt(3.0)
    corners = [(r * math.cos(math.radians(60 * k)), r * math.sin(math.radians(60 * k))) for k in range(6)]
    pts = []
    for k in range(6):
        pts.append(corners[k])
        th = (30 + 60 * k) % 360
        if not ribs or th not in RIB_NORMALS:
            continue
        n = (math.cos(math.radians(th)), math.sin(math.radians(th)))
        t = (-n[1], n[0])                                   # ccw の接線
        w, h = mm(P.HEX_RIB_W) / 2, mm(P.HEX_RIB_H)
        c = (ap * n[0], ap * n[1])
        p0 = (c[0] - t[0] * w, c[1] - t[1] * w)
        p3 = (c[0] + t[0] * w, c[1] + t[1] * w)
        pts += [p0, (p0[0] - n[0] * h, p0[1] - n[1] * h), (p3[0] - n[0] * h, p3[1] - n[1] * h), p3]
    return clip_half(pts, KEY_N, mm(P.HEX_CUT_BORE_D))


def bore_chamfer(x0, c=None):
    """穴のベッド側（-X 面 x0）の縁の 45 度の面取り（c、既定は第 1 層の 0.3）を切るカッター"""
    c = FIRST_LAYER if c is None else c
    plain = bore_poly(False)
    return loft_x([(x0 - 0.5, offset_convex(plain, c + 0.5)), (x0 + c, plain)], "bore_chamfer")


def offset_convex(poly, d):
    """凸多角形（ccw）を d だけ太らせる（角は mitre）"""
    n = len(poly)
    out = []
    for k in range(n):
        p0, p1, p2 = poly[k - 1], poly[k], poly[(k + 1) % n]
        e1 = (p1[0] - p0[0], p1[1] - p0[1])
        e2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*e1), math.hypot(*e2)
        n1 = (e1[1] / l1, -e1[0] / l1)
        n2 = (e2[1] / l2, -e2[0] / l2)
        den = 1.0 + n1[0] * n2[0] + n1[1] * n2[1]
        out.append((p1[0] + d * (n1[0] + n2[0]) / den, p1[1] + d * (n1[1] + n2[1]) / den))
    return out


def translate_poly(poly, du, dv):
    return [(u + du, v + dv) for u, v in poly]


# --- 3D の道具（mm）-------------------------------------------------------------------------------
def loft_x(rings, name, tri=False):
    """X 方向に積む loft。rings = [(x, [(u, v)...])...]（同じ点数）。頂点は (x, u, v)。
    tri = True なら側面の四角形を、輪の間の「半径方向の辺」を必ず含む 2 枚の三角形（a_i a_j b_j と a_i b_j b_i）にする。
    ねじれた四角形を boolean に渡すと、切られた断片が任意の対角線で三角形化されて傾きが変わる（円錐が 45 度より寝る）ため"""
    bm = bmesh.new()
    vs = [[bm.verts.new(((x[k] if hasattr(x, '__len__') else x), p[0], p[1])) for k, p in enumerate(ring)] for x, ring in rings]   # x は輪ごとの値か、頂点ごとの列
    bm.faces.new(vs[0][::-1])
    bm.faces.new(vs[-1])
    for a, b in zip(vs[:-1], vs[1:]):
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            if tri:
                bm.faces.new((a[i], a[j], b[j]))
                bm.faces.new((a[i], b[j], b[i]))
            else:
                bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link_obj(bm, name)


def annulus_x(r_in, r_out, x0, x1, n, name):
    """軸方向の円環（輪の溝を切るカッター）"""
    bm = bmesh.new()
    rings = {}
    for tag, r in (("i", r_in), ("o", r_out)):
        for xi, x in (("0", x0), ("1", x1)):
            rings[tag + xi] = [bm.verts.new((x, r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n)))
                               for k in range(n)]
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((rings["o0"][k], rings["o0"][j], rings["o1"][j], rings["o1"][k]))
        bm.faces.new((rings["i0"][j], rings["i0"][k], rings["i1"][k], rings["i1"][j]))
        bm.faces.new((rings["i0"][k], rings["i0"][j], rings["o0"][j], rings["o0"][k]))
        bm.faces.new((rings["o1"][k], rings["o1"][j], rings["i1"][j], rings["i1"][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return link_obj(bm, name)


def box3(x0, x1, y0, y1, z0, z1, name="box"):
    return prism([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "z", z0, z1, name)


def cut_collection(target, cutters, name):
    """重なった複数のカッターを 1 回の boolean で切る（EXACT、コレクション指定）"""
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    for cutter in cutters:
        collection.objects.link(cutter)
    modifier = target.modifiers.new(name, "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.operand_type = "COLLECTION"
    modifier.collection = collection
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    for cutter in cutters:
        bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.data.collections.remove(collection)
    tidy(target.data)
    return target


def cut(target, *others):
    """boolean の差。毎回 tidy する（残った零面積の面・一直線上の頂点を除く）"""
    _cut(target, *others)
    tidy(target.data)
    return target


def union(target, *others):
    _union(target, *others)
    tidy(target.data)
    return target


def drop(ob):
    """作業用のオブジェクトを、メッシュごと捨てる"""
    me = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    if me.users == 0:
        bpy.data.meshes.remove(me)


def tidy(me):
    """零面積の面・長さ 0 の辺を除き、法線を外向きにそろえる（mm のメッシュ）"""
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-4)       # 1e-4mm 未満の辺を残さない（寸法への影響は 2e-4mm 以下）
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=2e-4)
    # 同一平面の面を 1 枚にし、一直線上の頂点を消す（boolean が辺の途中に残す頂点が、三角形化で零面積の三角形になるため）
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.002), use_dissolve_boundaries=False, verts=bm.verts, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()


def triangulate(me):
    """最後に自分で三角形化する（STL の書き出しに任せると、一直線上の頂点を持つ多角形から零面積の三角形が出る）"""
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(me)
    bm.free()


def inst(src, name, off=(0.0, 0.0, 0.0)):
    """src（mm）のコピーを off（mm）だけずらして、m 単位のオブジェクトにする"""
    me = src.data.copy()
    me.name = name
    tidy(me)
    triangulate(me)
    me.transform(Matrix.Scale(1.0 / MM, 4) @ Matrix.Translation(off))
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


# --- 歯車（インボリュート、m1、圧力角 20 度）------------------------------------------------------
def _inv(a):
    return math.tan(a) - a


def gear_spec(z, root_r, tip_r, lash):
    """歯車の仕様。lash = 歯厚を細らせる量（ピッチ円上、mm）"""
    m = mm(P.GEAR_M)
    rp = z * m / 2
    alpha = math.radians(20.0)
    rb = rp * math.cos(alpha)
    th0 = (math.pi * m / 2 - lash) / (2 * rp) + _inv(alpha)    # 歯の中心から、基礎円上の歯の端までの半角
    return {"z": z, "rp": rp, "rb": rb, "ra": tip_r, "rr": root_r, "th0": th0}


def _polar(r, a):
    return (r * math.cos(a), r * math.sin(a))


def _half(g, rho):
    return g["th0"] - _inv(math.acos(min(1.0, g["rb"] / rho)))


def tooth_points(g, psi, n_flank=10):
    """歯 1 枚（中心 psi [rad]）の輪郭。歯底の低い側から高い側へ ccw。基礎円より下は半径方向の直線"""
    rb, ra, rr = g["rb"], g["ra"], g["rr"]
    pts = [_polar(rr, psi - g["th0"])]
    rho = [rb + (ra - rb) * i / n_flank for i in range(n_flank + 1)]
    for r in rho:
        pts.append(_polar(r, psi - _half(g, r)))
    ht = _half(g, ra)
    for s in (-1.0 / 3.0, 1.0 / 3.0):
        pts.append(_polar(ra, psi + s * ht))
    for r in reversed(rho):
        pts.append(_polar(r, psi + _half(g, r)))
    pts.append(_polar(rr, psi + g["th0"]))
    return pts


def _arc_inner(r, a0, a1, n):
    return [_polar(r, a0 + (a1 - a0) * i / (n + 1)) for i in range(1, n + 1)]


def gear_outline(g, phase_deg):
    """全周の歯車の輪郭（ccw）。歯の中心は phase + k * 360/z 度"""
    z = g["z"]
    pitch = 2 * math.pi / z
    pts = []
    for k in range(z):
        psi = math.radians(phase_deg) + k * pitch
        pts += tooth_points(g, psi)
        pts += _arc_inner(g["rr"], psi + g["th0"], psi + pitch - g["th0"], 4)
    return pts


def sector_teeth(g, phase_deg, a_lo_deg, a_hi_deg):
    """範囲 [a_lo, a_hi] に全体が入る歯の中心の極角 [rad] の並び"""
    pitch_deg = 360.0 / g["z"]
    th_deg = math.degrees(g["th0"])
    out = []
    for k in range(-g["z"], 2 * g["z"]):
        c = phase_deg + k * pitch_deg
        if c - th_deg >= a_lo_deg - 1e-9 and c + th_deg <= a_hi_deg + 1e-9:
            out.append(math.radians(c))
    return out


def sector_outline(g, phase_deg, a_lo_deg, a_hi_deg):
    """半円歯車（扇）の輪郭（ccw）。原点 → 歯底の弧 → 歯 → 歯底の弧 → 原点。範囲の端まで歯底で閉じる"""
    a_lo, a_hi = math.radians(a_lo_deg), math.radians(a_hi_deg)
    pts = [(0.0, 0.0), _polar(g["rr"], a_lo)]
    cur = a_lo
    for psi in sector_teeth(g, phase_deg, a_lo_deg, a_hi_deg):
        lo = psi - g["th0"]
        pts += _arc_inner(g["rr"], cur, lo, 3)
        pts += tooth_points(g, psi)
        cur = psi + g["th0"]
    pts += _arc_inner(g["rr"], cur, a_hi, 3)
    pts.append(_polar(g["rr"], a_hi))
    return pts


def chain_gear_spec():
    return gear_spec(P.CHAIN_Z, mm(P.CHAIN_GEAR_ROOT_R), mm(P.CHAIN_GEAR_TIP_R), LASH / 2)


def servo_gear_spec():
    return gear_spec(P.SERVO_Z, mm(P.SERVO_GEAR_ROOT_R), mm(P.SERVO_GEAR_TIP_R), LASH / 2)


# --- 軸の並び -----------------------------------------------------------------------------------------------
def cam_x(i, j):
    return mm(K.cam_x(i, j))


def axis_y(j):
    return mm(K.axis_y(j))


# --- 輪郭の道具（numpy）--------------------------------------------------------------------------------------
def simplify_closed(V, tol):
    """閉じた多角形の頂点を間引く（Douglas-Peucker。元の頂点の部分集合なので、元の輪郭の内側に tol 以内で収まる）"""
    V = np.asarray(V, dtype=float)
    n = len(V)
    a = 0
    b = int(np.argmax(np.hypot(V[:, 0] - V[0, 0], V[:, 1] - V[0, 1])))
    keep = {a, b}
    stack = [(a, b), (b, a + n)]
    while stack:
        i0, i1 = stack.pop()
        if i1 - i0 < 2:
            continue
        idx = np.arange(i0 + 1, i1) % n
        p0, p1 = V[i0 % n], V[i1 % n]
        d = p1 - p0
        ln = math.hypot(d[0], d[1])
        dist = np.abs(d[0] * (V[idx, 1] - p0[1]) - d[1] * (V[idx, 0] - p0[0])) / max(ln, 1e-12)
        k = int(np.argmax(dist))
        if dist[k] > tol:
            m = i0 + 1 + k
            keep.add(m % n)
            stack += [(i0, m), (m, i1)]
    return V[sorted(keep)]


_CAMS = None


def load_cams():
    global _CAMS
    if _CAMS is None:
        with open(os.path.join(HERE, "build", "cams.json"), encoding="utf-8") as f:
            _CAMS = json.load(f)
    return _CAMS


def cam_contour(i, j):
    """カム (i, j) の輪郭（cams.json の凸多角形。頂点を DP_TOL 以内で間引いた ccw の配列 (u, v) mm）。
    板・円錐・番号・隣の行の検査が全部これを使う"""
    return simplify_closed(load_cams()["cams"][j][i]["vertices"], DP_TOL)


def skirt_levels(rmax):
    """円錐の輪の深さ t の列（0 から、胴の床の半径 SKIRT_FLOOR に全部の頂点が届くまで SKIRT_STEP おき）"""
    n = int(math.ceil((rmax - SKIRT_FLOOR) / SKIRT_STEP - 1e-6))
    return [SKIRT_STEP * k for k in range(n + 1)]


def cam_solid(i, j):
    """カム (i, j) の板 + -X 側の 45 度の円錐（すそ）を 1 つの立体にする。輪（X ごとの断面）の頂点は輪郭の頂点そのもの:
    板の下面（t = 0）の輪 = 輪郭、深さ t の輪 = 各頂点を半径 max(SKIRT_FLOOR, R - t + SKIRT_BIAS) へ原点向きに縮めた点。
    半径は t に対して傾き 1（45 度）の直線で、輪の間を結ぶ面は水平から 45 度以上に立つ（下向きの張り出しは 45 度以内）。
    床（SKIRT_FLOOR）は胴（R5）の内側なので、円錐は胴の面で終わる（床の折れ目は胴の中に隠れる）。
    すその -X 側の端は SKIRT_X_MIN（-43.4）で止める: 円錐の頂の半径を R から min(R, 5 + (板の下面の X - SKIRT_X_MIN)) に抑える（45 度の線が
    胴の面に SKIRT_X_MIN で着く）。抑えた分（R - 抑えた半径）は、板の下の外周の稜を 45 度で面取りして（高さ = 抑えた分）、頂の輪とつなぐ"""
    V = cam_contour(i, j)
    R = np.hypot(V[:, 0], V[:, 1])
    body_r = mm(P.CAMSHAFT_BODY_D) / 2
    x0 = cam_x(i, j) - CAM_T / 2
    x1 = x0 + CAM_T
    Rs = np.minimum(R, body_r + (x0 - SKIRT_X_MIN) - SKIRT_STOP_MARGIN)
    cut_skirt = bool((Rs < R - 1e-9).any())
    rings = []
    for t in reversed(skirt_levels(float(Rs.max()))):
        r = np.maximum(SKIRT_FLOOR, Rs - t + (SKIRT_BIAS if t > 0 else 0.0))
        r = np.minimum(r, Rs)
        rings.append((x0 - t, (V * (r / R)[:, None]).tolist()))
    if cut_skirt:
        # 板の下の外周の稜を、抑えた分 R - Rs だけ 45 度で面取りする（円錐の頂 Rs の輪から、輪郭の頂点の (x0 + R - Rs) まで）。水平な縁を作らない
        rings.append((x0 + (R - Rs), V.tolist()))
    rings.append((x1, V.tolist()))
    INFO.setdefault("cam_skirt_end_x_mm", {})[f"{i}_{j}"] = round(x0 - (float(Rs.max()) - body_r), 3)
    if cut_skirt:
        INFO.setdefault("skirt_chamfer_height_max_mm", {})[f"{i}_{j}"] = round(float((R - Rs).max()), 3)
        INFO.setdefault("rim_width_left_mm", {})[f"{i}_{j}"] = round(float(CAM_T - (R - Rs).max()), 3)
    ob = loft_x(rings, f"camsolid_{i}_{j}", tri=True)
    if cut_skirt:                                          # 縁の幅 0 の所の重なった頂点を 1 つにする（退化した三角形を残さない）
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(ob.data)
        bm.free()
    return ob


# --- カム軸 camshaft_j（胴 Ø10 + 板カム 5 枚の一体）----------------------------------------------------------------
def union_all(target, others, name):
    """重なる複数の立体を 1 回の boolean（EXACT、コレクション指定）で足す"""
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    for o in others:
        collection.objects.link(o)
    modifier = target.modifiers.new(name, "BOOLEAN")
    modifier.operation = "UNION"
    modifier.solver = "EXACT"
    modifier.operand_type = "COLLECTION"
    modifier.collection = collection
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    for o in others:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(collection)
    tidy(target.data)
    return target


def label_boxes(text, contour):
    """番号の箱（text = 数字の列。1 字 LABEL_DW x LABEL_H、字の間 0.6）を、輪郭の内側（余裕 LABEL_MARGIN）・胴の外（R5 + 余裕）に収まる
    位置で探す。上（psi = 90 度）に近く、内側から。返り値: 中心 (u, v) か None"""
    V = np.asarray(contour, dtype=float)
    a, b = V, np.roll(V, -1, axis=0)
    e = b - a
    nrm = np.stack([e[:, 1], -e[:, 0]], axis=1)
    nrm /= np.hypot(nrm[:, 0], nrm[:, 1])[:, None]
    w = len(text) * LABEL_DW + (len(text) - 1) * 0.6
    gx, gy = np.meshgrid(np.linspace(-w / 2, w / 2, 7), np.linspace(-LABEL_H / 2, LABEL_H / 2, 5))
    box_pts = np.stack([gx.ravel(), gy.ravel()], axis=1)
    hub = mm(P.CAMSHAFT_BODY_D) / 2 + LABEL_MARGIN
    angles = sorted(np.arange(0.0, 360.0, 3.0), key=lambda t: abs(((t - 90.0 + 180.0) % 360.0) - 180.0))
    for r in np.arange(6.0, 11.5, 0.1):
        for ang in angles:
            c = np.array([r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))])
            pts = box_pts + c
            if np.hypot(pts[:, 0], pts[:, 1]).min() < hub:
                continue
            dist = -((pts[:, None, :] - a[None, :, :]) * nrm[None, :, :]).sum(axis=2)
            if dist.min() >= LABEL_MARGIN:
                return float(c[0]), float(c[1])
    return None


def label_cutters(text, center, x_face):
    """text（数字の列）の 7 セグメントの字を、中心 center の箱に +X 面（x_face）から CAM_LABEL_DEPTH 彫るカッター"""
    cu, cv = center
    s = LABEL_STROKE
    dw, dh = LABEL_DW, LABEL_H
    w = len(text) * dw + (len(text) - 1) * 0.6
    segs = {"a": (0, 1, "h"), "d": (0, 0, "h"), "g": (0, 0.5, "h"), "f": (0, 1, "vu"), "b": (1, 1, "vu"),
            "e": (0, 0, "vl"), "c": (1, 0, "vl")}
    digit = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc"}
    cutters = []
    for pos, ch in enumerate(text):
        x0 = cu - w / 2 + pos * (dw + 0.6)
        y0 = cv - dh / 2
        for sg in digit[int(ch)]:
            sx, sy, kind = segs[sg]
            if kind == "h":
                yy = {1: y0 + dh - s, 0: y0, 0.5: y0 + dh / 2 - s / 2}[sy]
                rect = [(x0, yy), (x0 + dw, yy), (x0 + dw, yy + s), (x0, yy + s)]
            else:
                xx = x0 + (dw - s if sx == 1 else 0.0)
                ya, yb = (y0 + dh / 2, y0 + dh) if kind == "vu" else (y0, y0 + dh / 2)
                rect = [(xx, ya), (xx + s, ya), (xx + s, yb), (xx, yb)]
            cutters.append(prism(rect, "x", x_face - mm(P.CAM_LABEL_DEPTH), x_face + 0.5, f"label_{pos}{sg}"))
    return cutters


def d_flat_cutter():
    """-X の Ø10 軸受けの D 面（位相合わせ治具が掛かる平らな面）を切るカッター。平らな面は φ0 で真上（v = 軸受けの上端 5.0 - 0.6 = 4.4）。
    面は X = -45.0 から D_FLAT_X1 まで。+X の端は 45 度の斜面（刷るときの下向き面を 45 度にする。面の端が水平な下向きの壁にならない）"""
    top = mm(P.CAMSHAFT_BODY_D) / 2
    v0 = top - mm(P.COMB_GRIP_FLAT_DEPTH)
    xe = D_FLAT_X1
    poly = [(-JOURNAL_MX_END - 1.0, v0), (xe, v0), (xe + (top + 1.0 - v0), top + 1.0), (-JOURNAL_MX_END - 1.0, top + 1.0)]
    return prism(poly, "y", -top - 1.0, top + 1.0, "d_flat")


def build_camshaft(j, with_label=True):
    """camshaft_j（軸の中心を原点にした局所。X は組立の位置）: 胴 Ø10（-X の端 -45.0 から +X の端 40.4）+ 各カムの板と円錐（5 枚）
    + +X 端の六角の雄スタブ（AF5.5、40.4..42.4）+ -X の軸受けの D 面 + 番号（最も +X のカムの +X 面）。
    -X の端面（X -45.0）の外縁に 0.4 の 45 度の面取り。刷るときは -X 端を下にして立てる"""
    body_r = mm(P.CAMSHAFT_BODY_D) / 2
    x_end = GEAR_X0                                   # 胴の +X の端 = gear_j の -X 面（歯車に突き当たる肩）
    xj = JOURNAL_MX_END
    ch = mm(P.SHOULDER_CHAMFER)
    n = 96
    body = loft_x([(-xj, circle((0, 0), body_r - ch, n)), (-xj + ch, circle((0, 0), body_r, n)), (x_end, circle((0, 0), body_r, n))],
                  f"camshaft_{j}")
    cams = [cam_solid(i, j) for i in range(P.N)]
    union_all(body, cams, f"cams_{j}")
    union(body, prism(shaft_poly(), "x", x_end - 0.4, mm(P.GEAR_HUB_X0) + mm(P.JOINT_ENGAGE_GEAR), "stub"))
    cut(body, d_flat_cutter())
    if with_label:
        for i in (4, 3, 2, 1, 0):
            c = label_boxes(str(j), cam_contour(i, j))
            if c is not None:
                x_face = cam_x(i, j) + CAM_T / 2
                cut_collection(body, label_cutters(str(j), c, x_face), f"label_{j}")
                INFO.setdefault("camshaft_label", {})[str(j)] = {"cam": i, "uv_mm": [round(c[0], 2), round(c[1], 2)]}
                break
        else:
            raise RuntimeError(f"camshaft_{j}: 番号の箱が入るカムが無い")
    return body


def build_print_foot():
    """刷るときだけの円盤（camshaft_j の -X の端面の下。軸の中心を原点にした局所、X は組立の位置の延長）: 円盤 Ø30 x 1.2（ベッドに
    つく縁に 0.3 の面取り）+ 端面から 1.0 下に離して、4 本のリブ（90 度おき、半径 1.5..4.6、厚み 0.8、端面側 0.3 で 0.4 まで絞る首）。
    リブは端面の中へ 0.3 食い込ませて 1 つの立体にする（端面の面取りの内側 R4.6 に収まる）"""
    xe = -JOURNAL_MX_END                             # 軸受けの端面
    gap, td = mm(P.PRINT_FOOT_GAP), mm(P.PRINT_FOOT_T)
    r_d = mm(P.PRINT_FOOT_D) / 2
    xt = xe - gap                                    # 円盤の上面
    fc = FIRST_LAYER
    disk = loft_x([(xt - td, circle((0, 0), r_d - fc, 96)), (xt - td + fc, circle((0, 0), r_d, 96)), (xt, circle((0, 0), r_d, 96))],
                  "print_foot_disk")
    w = mm(P.PRINT_FOOT_RIB_W) / 2
    wn = mm(P.PRINT_FOOT_NECK) / 2
    neck_h = mm(P.PRINT_FOOT_RESIDUE_MAX)
    r0, r1 = mm(P.PRINT_FOOT_RIB_R0), mm(P.PRINT_FOOT_RIB_R1)
    prof = [(xt - 0.3, -w), (xe - neck_h, -w), (xe, -wn), (xe + 0.3, -wn), (xe + 0.3, wn), (xe, wn), (xe - neck_h, w), (xt - 0.3, w)]
    ribs = []
    for k in range(P.PRINT_FOOT_RIBS):
        rib = prism(prof, "y", r0, r1, f"print_foot_rib{k}")           # (x, 厚み z) の輪郭を y = 半径方向 r0..r1 へ押し出す → 軸まわりに回す
        rib.data.transform(Matrix.Rotation(math.radians(360.0 * k / P.PRINT_FOOT_RIBS), 4, "X"))
        ribs.append(rib)
    union_all(disk, ribs, "print_foot")
    return disk


def gear_hole():
    """gear_j の雌穴の寸法（mm）: 口の X（歯車の -X 面）、底の X（camshaft_j のスタブの先）、深さ、リブの始まりの X と長さ。
    -X のハブをやめたので、穴は歯車の板の -X 面（平らな面）から開く。リブは口の面取りの奥から始まる"""
    x_mouth = GEAR_X0
    x_bot = mm(P.GEAR_HUB_X0) + mm(P.JOINT_ENGAGE_GEAR)                # 42.4
    lc = mm(P.JOINT_LEAD_CHAMFER)
    xr0 = max(x_bot - mm(P.JOINT_RIB_LEN), x_mouth + lc)
    return {"x_mouth": x_mouth, "x_bot": x_bot, "depth": x_bot - x_mouth, "rib_x0": xr0, "rib_len": x_bot - xr0, "lead_chamfer": lc}


def build_gear():
    """gear_j（軸の中心を原点にした局所）: 歯車（X 40.4..43.2、-X 面が平ら）+ +X の丸いボス Ø9.5 x 0.4（外縁に 0.2 の面取り、43.2..43.6 = 肩）
    + +X の Ø5 軸受け（43.6..45.4）。-X 面から六角の雌穴（深さ 2.0、切り落とし六角 AF5.9、口に 0.5 の面取り）。camshaft_j の胴（Ø10）が
    X 40.4 まで届いて、その面で歯車の -X 面に突き当たる（肩）。潰しリブは口の面取りの奥から穴の底まで（1.5mm）、手前の端は 45 度の傾き。
    刷るときは -X 面（穴の口）を下にして平置き: 板の -X 面が全部ベッドに着く（ハブ無し）"""
    g = chain_gear_spec()
    h_ = gear_hole()
    x0, x1 = GEAR_X0, GEAR_X1
    ts = x1 + mm(P.GEAR_BOSS_T)                                       # 肩（43.6）
    gb = mm(P.GEAR_BOSS_D) / 2
    bc = mm(P.GEAR_BOSS_CHAMFER)
    ob = prism(gear_outline(g, P.CHAIN_TOOTH_PHASE_DEG), "x", x0, x1, "gear")
    union(ob, loft_x([(x1 - 0.2, circle((0, 0), gb, 96)), (ts - bc, circle((0, 0), gb, 96)), (ts, circle((0, 0), gb - bc, 96))], "boss"))
    union(ob, prism(circle((0, 0), mm(P.JOURNAL_D) / 2, 64), "x", ts - 0.2, mm(P.JOURNAL_END), "journal_p"))
    cut(ob, prism(bore_poly(False), "x", x0 - CAM_BORE_PAD, h_["x_bot"], "gear_bore"))
    cut(ob, bore_chamfer(x0, h_["lead_chamfer"]))
    ap = mm(P.SHAFT_BORE_AF) / 2
    h, w = mm(P.HEX_RIB_H), mm(P.HEX_RIB_W) / 2
    xr0, x_bot = h_["rib_x0"], h_["x_bot"]
    prof = [(xr0, ap + 0.3), (xr0, ap), (xr0 + h, ap - h), (x_bot + 0.3, ap - h), (x_bot + 0.3, ap + 0.3)]
    for q, th in enumerate(RIB_NORMALS):
        rib = prism(prof, "y", -w, w, f"gear_rib{q}")                  # (x, z = 法線方向の距離) を y = 接線方向へ ±w 押し出す。法線 +z = 90 度
        rib.data.transform(Matrix.Rotation(math.radians(th - 90.0), 4, "X"))
        union(ob, rib)
    INFO["gear_hole"] = {k: round(v, 3) for k, v in h_.items()}
    return ob, g


# --- 画素 pixel_i_j --------------------------------------------------------------------------------------
def _sq(w, dx=0.0):
    return [(dx - w / 2, -w / 2), (dx + w / 2, -w / 2), (dx + w / 2, w / 2), (dx - w / 2, w / 2)]


def build_pixel(parity):
    """画素 1 個（頭の中心を X = Y = 0 にした局所、Z は組立の位置、面一）。parity = 行 j の偶奇。
    頭（上縁に 0.3 の面取り）+ つば（頭の下側に 45 度の面取り）+ 角筒の茎（X に stem_shift ずれる）+ 足（YZ の板、45 度で広がる。
    X は自分のカムの真上 = row_shift。茎から偏る）。
    刷るときは頭の上面を下にして立てる。茎の空洞は +Y の壁の通気穴で外へ開ける。偶奇は茎の -Y 面の溝の本数（偶数行 1、奇数行 2）"""
    dx = mm(K.stem_shift(parity))                      # 茎（と空洞・通気穴・偶奇の溝）の中心の X（列の中心から。偶数行 +0.80、奇数行 -2.75）
    dxf = mm(K.row_shift(parity))                      # 足（YZ の板）の中心の X = 自分のカムの X（偶数行 +3.15、奇数行 -5.10）。茎から ±2.35 偏る
    z_top = mm(P.BEZEL_Z1)                            # 頭の上面（96）
    z_ft = mm(P.FLANGE_TOP_FLUSH)                     # つばの上面 = 頭の下面
    z_fb = mm(P.FLANGE_BOT_FLUSH)                     # つばの下面
    fw, hw = mm(P.FLANGE_W), mm(P.HEAD)
    cham = (fw - hw) / 2                              # 0.7。45 度の面取りの高さ = 幅
    fc = FIRST_LAYER                                  # 頭の上縁（刷るときベッド側）の 45 度の面取り 0.3
    top = loft_rings([(z_fb, _sq(fw)), (z_ft - cham, _sq(fw)), (z_ft, _sq(hw)), (z_top - fc, _sq(hw)), (z_top, _sq(hw - 2 * fc))],
                     "pixel")
    tw, wall = mm(P.TOWER_W), mm(P.TOWER_WALL)
    foot_y, foot_x, flat = mm(P.FOOT_Y), mm(P.FOOT_X), mm(P.FOOT_FLAT)
    z_foot = mm(P.CAM_TOP_FLUSH)                      # 足の下面（59.9）
    z_fl = z_foot + flat                              # 足の平らな板の上面
    z_tb = z_foot + mm(P.FOOT_H)                      # 茎の下端 = 足の面取りの上端（67.0）
    union(top, prism(_sq(tw, dx), "z", z_tb, z_fb + 0.6, "tower"))
    fin = [(-foot_y / 2, z_foot), (foot_y / 2, z_foot), (foot_y / 2, z_fl), (tw / 2, z_tb), (tw / 2, z_tb + 0.6),
           (-tw / 2, z_tb + 0.6), (-tw / 2, z_tb), (-foot_y / 2, z_fl)]
    union(top, prism(fin, "x", dxf - foot_x / 2, dxf + foot_x / 2, "foot"))
    # 空洞（刷るとき天井の橋 5.8mm）と通気穴（+Y の壁、3mm 角）
    inner = tw - 2 * wall
    z_cav0 = z_tb + wall
    # 空洞と通気穴は 1 回で切る: 空洞だけを先に切ると内側の殻の法線が recalc で裏返り、次の boolean で空洞が埋まる
    cut_collection(top, [prism(_sq(inner, dx), "z", z_cav0, z_fb + 1.0, "cavity"),
                         box3(dx - VENT / 2, dx + VENT / 2, tw / 2 - wall - 0.3, tw / 2 + 0.3, z_cav0 + 0.4, z_cav0 + 0.4 + VENT, "vent")],
                   "cavity_vent")
    # 偶奇の溝（-Y の面、深さ 0.4、幅 1.0、茎の途中の 12mm。残る肉 1.2）
    n_groove = 1 if parity % 2 == 0 else 2
    centers = [dx] if n_groove == 1 else [dx - 1.5, dx + 1.5]
    for q, xg in enumerate(centers):
        cut(top, box3(xg - 0.5, xg + 0.5, -tw / 2 - 0.3, -tw / 2 + 0.4, z_cav0 + 6.0, z_cav0 + 18.0, f"mark{q}"))
    top.name = "pixel"
    return top


# --- 受け horn_coupler -------------------------------------------------------------------------------------
def horn_polys(c, n=24):
    """ホーン（ホーン座標 hx = 長腕の向き、hy）の腕と短腕とハブを c だけ太らせた凸多角形 4 つ。C4-2 と同じ構成"""
    sg = P.SG
    tip = mm(sg.HORN_TIP_W) / 2 + c
    root = mm(sg.HORN_ROOT_W) / 2 + c
    hub = mm(sg.HORN_HUB_DIA) / 2 + c
    left = mm(sg.HORN_LEFT_X) - c
    right = mm(sg.HORN_RIGHT_X) + c
    root_x = mm(sg.HORN_HUB_DIA) / 2
    left_arm = hull(circle((left + tip, 0), tip, n) + [(-root_x, -root), (-root_x, root), (0, -root), (0, root)])
    right_arm = hull(circle((right - tip, 0), tip, n) + [(root_x, -root), (root_x, root), (0, -root), (0, root)])
    sh = mm(sg.HORN_SPAN_Y) / 2 + c
    sr = mm(sg.HORN_SHORT_W) / 2 + c
    short = hull(circle((0, sh - sr), sr, n) + circle((0, -sh + sr), sr, n))
    return {"long": left_arm, "right": right_arm, "short": short, "hub": [tuple(p) for p in circle((0, 0), hub, 48)]}


def horn_to_uv(poly):
    """ホーン座標 (hx, hy) → 受けの (u, v)。長腕（-hx、18mm）が下（-Z）、右腕（+hx、16mm）が上（+Z）。回転 +90 度"""
    return [(-hy, hx) for hx, hy in poly]


def build_horn_coupler():
    """受け（軸 = サーボ出力軸を原点にした局所）。扇の半円歯車（38T）+ 長腕と短腕のふくらみ + ハブの台 + +X 側の蓋 + 支えのピン。
    ホーンのポケット（-X 面から 1.6mm、口は 45 度で 0.3 面取り）は付属ホーンの非対称（長腕 18 / 右腕 16）の形をそのまま使い、
    逆向きの装着と、中心を左右差ぶんずらした装着を、形で通さない"""
    x0 = mm(P.RECV_HUB_X0)                                # 受け全体の -X 面 = ポケットの口（40.0）
    x_pocket = x0 + mm(P.RECV_POCKET)
    x_top = mm(P.RECV_X1)
    x_gear = mm(P.RECV_X0) + mm(P.RECV_GEAR_T)            # 歯の +X 面（42.4）。歯の面は中央の軸の歯車（40.0..42.4）と同じ
    x_lo, x_hi = x0 - 1.0, x_top + 1.0                    # 部品ごとに両端を余分に押し出して合わせ、最後に 1 回の切断で面を作る
    g = servo_gear_spec()                                 # （面一の別々の面を重ねると、重なった面が残って自己交差になる）
    arc = P.RECV_ARC_HALF_DEG
    outline = sector_outline(g, P.SECTOR_TOOTH_PHASE_DEG, 90.0 - arc, 90.0 + arc)
    x_plate = x_hi if x_gear >= x_top - 1e-6 else x_gear      # 歯の板の +X 面が受けの +X 面と同じ高さなら、蓋・ふくらみと一緒に x_hi まで伸ばして 1 回で切る（面一の別々の面を作らない）
    body = prism(outline, "x", x_lo, x_plate, "horn_coupler")
    # ふくらみ（ポケットを囲む肉 COUPLER_WALL）。右腕側は扇の歯底の内側に収まるのでふくらみを付けない
    lobes = horn_polys(mm(P.HORN_CLR) + COUPLER_WALL)
    for key in ("long", "short", "hub"):
        union(body, prism(horn_to_uv(lobes[key]), "x", x_lo, x_hi, f"lobe_{key}"))
    cap_pts = [(0.0, 0.0)] + [_polar(COUPLER_CAP_R, math.radians(90.0 - arc + 2 * arc * q / 60)) for q in range(61)]
    union(body, prism(cap_pts, "x", x_gear - 0.4, x_hi, "cap"))
    cut(body, box3(x_lo - 1.0, x0, -60.0, 60.0, -60.0, 60.0, "trim_lo"), box3(x_top, x_hi + 1.0, -60.0, 60.0, -60.0, 60.0, "trim_hi"))
    union(body, prism(circle((0, 0), mm(P.RECV_PIN_D) / 2, 48), "x", x_top - 0.1, mm(P.RECV_PIN_X1), "pin"))
    # ポケット（口は 45 度で 0.3 面取り）
    base = horn_polys(mm(P.HORN_CLR))
    for key in ("long", "right", "short", "hub"):
        poly = base[key]
        rings = [(x0 - MOUTH_RELIEF, offset_convex(poly, 2 * MOUTH_RELIEF)), (x0 + MOUTH_RELIEF, offset_convex(poly, 0.0)),
                 (x_pocket, poly)]
        rings = [(x, horn_to_uv(p)) for x, p in rings]
        cut(body, loft_x(rings, f"pocket_{key}"))
    return body


def horn_solid():
    """付属ホーンの立体（検査用。部品ではない）。受けと同じ局所で、正しい向きの位置に置く。腕の輪郭は models/sg92r-photo/model.py の
    add_long_arm と同じ点列（先端の円弧 + 根元 ±3.5 への直線）、短腕はカプセル、ハブは径 7。腕の下面は受けの -X 面 + 0.1、上面 = ポケットの天井"""
    sg = P.SG
    x_arm0 = mm(P.RECV_HUB_X0) + 0.1
    x_top = x_arm0 + mm(sg.HORN_ARM_T)
    r = mm(sg.HORN_TIP_W) / 2
    lc, rc = mm(sg.HORN_LEFT_X) + r, mm(sg.HORN_RIGHT_X) - r
    rx, rh = mm(sg.HORN_HUB_DIA) / 2, mm(sg.HORN_ROOT_W) / 2
    pts = []
    for i in range(9):
        a = math.pi + i * math.pi / 16
        pts.append((lc + r * math.cos(a), r * math.sin(a)))
    pts += [(-rx, -rh), (rx, -rh), (rc, -r)]
    for i in range(1, 17):
        a = -math.pi / 2 + i * math.pi / 16
        pts.append((rc + r * math.cos(a), r * math.sin(a)))
    pts += [(rx, rh), (-rx, rh), (lc, r)]
    for i in range(1, 8):
        a = math.pi / 2 + i * math.pi / 16
        pts.append((lc + r * math.cos(a), r * math.sin(a)))
    ob = prism(horn_to_uv(pts), "x", x_arm0, x_top, "horn_ref")
    polys = horn_polys(0.0)
    union(ob, prism(horn_to_uv(polys["short"]), "x", x_arm0, x_top, "horn_short"))
    union(ob, prism(horn_to_uv(polys["hub"]), "x", x_arm0 - 3.0, x_top, "horn_hub"))
    return ob


# --- 位相合わせ治具 phase_comb -------------------------------------------------------------------------------
def build_phase_comb():
    """位相合わせ治具（全体の座標。Y は軸の位置、Z は組立の位置）。YZ の薄い板（X COMB_X0..COMB_X1）。板は -X パッドの上面より COMB_PLATE_GAP 上
    （外装に触れない）に置き、5 本の camshaft_j の -X の Ø10 軸受け（上端がパッドの上面より低い）の上に、軸ごとに歯（幅 3.0）を下へ出す。
    歯の下端は軸受けの上端の下 0.4（D 面 4.4 の 0.2 上 = 4.6）で、U 溝の中へ入る。φ0 のときだけ歯が D 面の上に落ち、耳が -X のパッドの上面に座る。
    向きがずれると D 面でない円周が歯に当たって櫛が浮く。持ち手の出っ張りと、軸の間の 4 つの耳（パッドの上面に座る）つき"""
    x0, x1 = COMB_X0, COMB_X0 + COMB_T                   # 板の X（-44.7..-43.1、厚み 1.6）。params の COMB_X0（-45.2）・COMB_T（1.0）は使わない（壁の中に入る・薄い）
    yh = COMB_Y_HALF
    pad_top = ZC + mm(P.PAD_TOP_ABOVE_MX)
    z0, z1 = pad_top + COMB_PLATE_GAP, mm(P.COMB_Z1)
    plate = [(-yh, z0), (yh, z0), (yh, z1), (COMB_HANDLE_Y, z1), (COMB_HANDLE_Y, COMB_HANDLE_TOP), (-COMB_HANDLE_Y, COMB_HANDLE_TOP),
             (-COMB_HANDLE_Y, z1), (-yh, z1)]
    ob = prism(plate, "x", x0, x1, "phase_comb")
    ew = mm(P.COMB_EAR_W)
    for ye in P.COMB_EAR_Y:
        y = mm(ye)
        union(ob, prism([(y - ew / 2, pad_top), (y + ew / 2, pad_top), (y + ew / 2, pad_top + COMB_EAR_H), (y - ew / 2, pad_top + COMB_EAR_H)],
                        "x", COMB_EAR_X0, COMB_EAR_X1, "ear"))
    tw = mm(P.COMB_TOOTH_W) / 2
    v_b = mm(P.CAMSHAFT_BODY_D) / 2 - mm(P.COMB_GRIP_FLAT_DEPTH) + mm(P.COMB_NOTCH_CLR)       # 歯の下端（軸の中心から 4.6）
    for j in range(P.N):
        y = axis_y(j)
        union(ob, prism([(y - tw, ZC + v_b), (y + tw, ZC + v_b), (y + tw, z0 + 0.5), (y - tw, z0 + 0.5)], "x", COMB_TOOTH_X0, COMB_TOOTH_X1, f"tooth_{j}"))
    INFO["comb"] = {"plate_bottom_z_mm": round(z0, 3), "pad_top_z_mm": round(pad_top, 3), "tooth_tip_z_mm": round(ZC + v_b, 3),
                    "d_flat_z_mm": round(ZC + mm(P.CAMSHAFT_BODY_D) / 2 - mm(P.COMB_GRIP_FLAT_DEPTH), 3), "bearing_top_z_mm": round(ZC + mm(P.CAMSHAFT_BODY_D) / 2, 3)}
    return ob


# --- 全部品 ---------------------------------------------------------------------------------------------------
def part_ids():
    ids = [f"camshaft_{j}" for j in range(P.N)] + [f"gear_{j}" for j in range(P.N)]
    ids += [f"pixel_{i}_{j}" for j in range(P.N) for i in range(P.N)] + ["horn_coupler", "phase_comb"]
    return ids


PRINT_VARIANT_IDS = [f"camshaft_{j}" for j in range(P.N)]       # 刷る STL が組立姿勢の STL と形が違う部品（刷るときだけの円盤がつく）
_PRINT_VARIANTS = {}


def build_print_variants():
    """刷る STL にだけ含める形（組立姿勢の座標、m）。build_moving() のあとに呼ぶ。camshaft_j + 刷るときだけの円盤（連結 1）"""
    return dict(_PRINT_VARIANTS)


def build_moving():
    """全部品を組立姿勢（サーボ 90 度、phase_comb は装着位置）で作って返す。単位 m。オブジェクト名 = id"""
    out = {}
    for name in part_ids() + [f"print_{n}" for n in PRINT_VARIANT_IDS]:
        old = bpy.data.objects.get(name)
        if old is not None:
            drop(old)
    INFO.clear()
    _PRINT_VARIANTS.clear()

    # camshaft_j（5 本とも輪郭が違う）と刷るときだけの円盤
    foot = build_print_foot()
    for j in range(P.N):
        y = axis_y(j)
        cs = build_camshaft(j)
        out[f"camshaft_{j}"] = inst(cs, f"camshaft_{j}", (0.0, y, ZC))
        pv = cs
        f = foot.copy()
        f.data = foot.data.copy()
        bpy.context.collection.objects.link(f)
        union(pv, f)
        _PRINT_VARIANTS[f"camshaft_{j}"] = inst(pv, f"print_camshaft_{j}", (0.0, y, ZC))
        drop(pv)
    drop(foot)

    # 歯車 gear_j
    gear_t, g = build_gear()
    for j in range(P.N):
        out[f"gear_{j}"] = inst(gear_t, f"gear_{j}", (0.0, axis_y(j), ZC))
    drop(gear_t)

    # 画素（偶奇で 2 種。頭の中心の X・Y へずらす）
    pix = {par: build_pixel(par) for par in (0, 1)}
    for j in range(P.N):
        for i in range(P.N):
            out[f"pixel_{i}_{j}"] = inst(pix[j % 2], f"pixel_{i}_{j}", (mm(K.col_x(i)), axis_y(j), 0.0))
    for ob in pix.values():
        drop(ob)

    # 受け
    rc = build_horn_coupler()
    out["horn_coupler"] = inst(rc, "horn_coupler", (0.0, 0.0, ZS))
    drop(rc)

    # 位相合わせ治具
    pc = build_phase_comb()
    out["phase_comb"] = inst(pc, "phase_comb")
    drop(pc)
    return out


# --- 刷る向き -------------------------------------------------------------------------------------------------------
# euler_deg = Blender のオイラー XYZ（度）。統合側は回転後に最下点を z = 0、XY を原点へ寄せて書き出す
_X_UP = (0.0, -90.0, 0.0)                     # +X 面が上になる（-X 面が下）
PRINT_POSE = {}
for _j in range(P.N):
    PRINT_POSE[f"camshaft_{_j}"] = {
        "euler_deg": _X_UP,
        "print_variant": True,
        "reason": "-X 端を下にして立てる（高さ 89.6mm = 軸 87.4 + 円盤 1.2 + 隙間 1.0。円盤 Ø30 で 高さ/接地 = 3.0 倍）。各カムの -X 側（下側）は 45 度の円錐で、"
                  "胴まで絞る。-X の軸受け Ø10 の端面は外縁に 0.4 の 45 度の面取り。D 面は +X の端が 45 度の斜面。+X の六角のスタブ（AF5.5、2.8）が一番上。"
                  "刷るときだけの円盤 Ø30 x 1.2 を、4 本のリブ（厚み 0.8、端面側は 0.4 の首）で端面とつなぐ。折り取ると端面に 0.3 以下の出っ張りが残る"
                  "（壁の溝の中の見えない面）",
        "support": "なし。下向きの面は、円盤とリブでつないだ端面（円盤の上 1.0、リブの間は橋 ≈ 3.4mm、壁の溝の中の見えない面）だけ。"
                   "軸 1・3（奇数行）の cam 0 は、すそを X -43.4 で止めた分、板の下の外周の稜を 45 度で面取り（高さ 0.5〜1.5。外周の残りの幅 2.5 以上）",
        "exceptions": []}
    PRINT_POSE[f"gear_{_j}"] = {
        "euler_deg": _X_UP,
        "reason": "歯の輪郭を XY 面にして平置き。-X 面（歯車の板の面。雌穴の口に 0.5 の面取り）が全部ベッド。ボス Ø9.5（0.4）と +X の Ø5 軸受け（1.8）が上へ立つ。"
                  "歯の側面・穴の切り落とし六角とリブは鉛直。リブの手前の端は 45 度の傾き",
        "support": "なし。下向きの水平面は穴の底（橋 5.9mm、内側）だけ"}
for _j in range(P.N):
    for _i in range(P.N):
        PRINT_POSE[f"pixel_{_i}_{_j}"] = {
            "euler_deg": (180.0, 0.0, 0.0),
            "reason": "頭の上面（見える面）を下にして立てる（上縁に 0.3 の面取り）。つばは頭の下側が 45 度の面取り。茎は 9mm 角、"
                      "頭とつばの上に 27mm（3 倍）。足の平らな面（カムに乗る面）が最上面",
            "support": "なし。見える面（頭の上面、つばの 45 度面取り、茎と足の外面）に水平な下向き面は無い。足の 45 度の広がりは 45 度ちょうどで"
                       "張り出しに数えない。下向きの水平面は茎の中だけ: 空洞の天井（橋 5.8mm、33.6mm2）、通気穴の上辺（3mm、4.8mm2）、"
                       "偶奇の溝の上端（0.4mm2）"}
PRINT_POSE["horn_coupler"] = {
    "euler_deg": _X_UP,
    "reason": "-X 面（ポケットの口）を下にして平置き。歯の板（2.8〜3.2）が下、ポケットは下面の凹み（橋は最大幅 7.3mm）、"
              "口は 45 度で 0.3 面取りしてある。上へ向かって細るだけで、支えのピンは上に 2.1mm 立つ",
    "support": "なし。ポケットの天井（橋 7.3mm 以下、見えない）だけが水平な下向き面"}
PRINT_POSE["phase_comb"] = {
    "euler_deg": (0.0, 90.0, 0.0),
    "reason": "+X 面を下にして平置き（厚み 1.0）。耳は -X 側へ出ているので上へ立つ。切り欠きの歯は板の面内で、張り出しは無い",
    "support": "なし"}
