"""タンジブル画素キューブの動く部品の形（bpy）。静止部品と統合は別担当。寸法は params.py だけから読む。

build_moving() が全部品を組立姿勢（サーボ THETA_FLAT = 90 度、全軸 phi = 0、画素は面一）で作って返す。
オブジェクト名 = 部品 id、単位 m。PRINT_POSE は各部品を刷る向きにする回転（オイラー XYZ 度）と理由。

座標: X = 軸方向、(u, v) = (Y, Z)。軸まわりの極角 psi は +Y から +Z へ測る（kinematics と同じ）。内部は mm で組み、最後に 1/1000 する。
部品: shaft_j, gear_j, cam_i_j, pixel_i_j, horn_coupler, phase_comb（i = 列 = X、j = 行 = Y）。

統合側への申し送り:
- 全部品はワールド座標（原点 = 箱の底面の中心）で、オブジェクトの変換は焼き込み済み（原点 0、回転 0、倍率 1）
- horn_coupler の姿勢: 付属ホーンの長腕（18mm）が -Z、右腕（16mm）が +Z、短腕が Y。sg92r_horn も同じ姿勢（サーボ 90 度）で置く。
  ホーンの腕の下面の X = 受けの -X 面（RECV_HUB_X0 = 40.0）+ 0.1 = 40.1、腕の上面 = ポケットの天井 = 41.6（接する）。ハブは 37.1 から。
  受けの -X 面は歯の面（40.6）より 0.6 -X へ出る（受け全体が平らに刷れるように）
- phase_comb は組立の途中で外す治具で、最終形には残らない
- 軸は数珠つなぎ: gear_j（+X、ボス + Ø5 軸受け + 雌穴）← cam_4..0（雄スタブ + 雌穴）← shaft_j（-X の端、雄スタブ + Ø5 軸受け）。刷る向きは PRINT_POSE
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
STUB_OVERLAP = 0.4                          # カムの雄スタブを板の中へ重ねる量（板の +X 面と面一にしない。穴の底より +X）
RIB_NORMALS = (30, 150, 270)                # 潰しリブを付ける穴の面の法線（度）。切り落とす角（60 度）の側の面（90 度）を避けた 1 面おき
KEY_N = (math.cos(math.radians(P.HEX_KEY_NORMAL_DEG)), math.sin(math.radians(P.HEX_KEY_NORMAL_DEG)))   # 切り落とし面の法線
FIRST_LAYER = mm(P.FIRST_LAYER_CHAMFER)     # 第 1 層の膨らみ対策の面取り（0.3、45 度）
CAM_BORE_PAD = 1.0                          # 穴のカッターの突き出し
COUPLER_WALL = 2.45                         # 受けの肉（長腕の先 18 + 0.15 + 2.45 = 20.6 = RECV_BAR_R）
COUPLER_CAP_R = 17.5                        # 受けの +X 側の蓋（半円）の半径。右腕のポケットの先 16.15 から 1.35 の肉。歯底 17.75 より内
MOUTH_RELIEF = FIRST_LAYER                  # ポケットの口の 45 度の面取り（刷るときベッド側の第 1 層の膨らみを逃がす）
COMB_HANDLE_Y = 7.0                         # 治具の持ち手の Y 半幅
COMB_HANDLE_TOP = mm(P.PLATE_Z0) - 0.6      # 持ち手の上端（案内板の下面 63.5 から 0.6）
COMB_EAR_H = 3.5                            # 耳の高さ（パッドの上面から。板の上端 4.0 より低くして、耳の上面が板の上端と面一にならないように）
LABEL_W, LABEL_H = 4.6, 3.0                 # カムの番号の箱。+X 面でスタブ（外接円 R3.2）の外に全 25 枚が入る（CAM_LABEL_H 3.0）
LABEL_STROKE = 0.5                          # 番号の線の太さ
LABEL_MARGIN = 0.3                          # 番号と板の縁・スタブの余裕
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


def bore_chamfer(x0):
    """穴のベッド側（-X 面 x0）の縁の 45 度の面取り（0.3）を切るカッター"""
    plain = bore_poly(False)
    return loft_x([(x0 - 0.5, offset_convex(plain, FIRST_LAYER + 0.5)), (x0 + FIRST_LAYER, plain)], "bore_chamfer")


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
def loft_x(rings, name):
    """X 方向に積む loft。rings = [(x, [(u, v)...])...]（同じ点数）。頂点は (x, u, v)"""
    bm = bmesh.new()
    vs = [[bm.verts.new((x, p[0], p[1])) for p in ring] for x, ring in rings]
    bm.faces.new(vs[0][::-1])
    bm.faces.new(vs[-1])
    for a, b in zip(vs[:-1], vs[1:]):
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
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


# --- 軸の並び（design_check の LAYOUT と同じ）-----------------------------------------------------------
def cam_x(i, j):
    return mm(K.cam_x(i, j))


def axis_y(j):
    return mm(K.axis_y(j))


def row_cams(j):
    """行 j のカムを X の小さい順に: [(i, x0, x1)]"""
    return sorted(((i, cam_x(i, j) - CAM_T / 2, cam_x(i, j) + CAM_T / 2) for i in range(P.N)), key=lambda t: t[1])


def stub_end(i, j):
    """カム (i, j) の雄スタブの +X 端 = 次の部品（隣のカム・歯車の部品）の -X 面 + 雌穴の深さ（スタブの先は穴の底に着く）"""
    if i + 1 < P.N:
        return cam_x(i + 1, j) - CAM_T / 2 + mm(P.JOINT_ENGAGE_CAM)
    return GEAR_X0 + mm(P.JOINT_ENGAGE_GEAR)


# --- 数珠つなぎの -X の端の部品 shaft_j ---------------------------------------------------------------------------
def build_shaft(j):
    """-X の端の部品 shaft_j（軸の中心を原点にした局所）。切り落とし六角のスタブ AF5.5 を -X 端（肩 -43.6）から最も -X のカムの雌穴の底まで、
    -X の丸い軸受け Ø5（-44.6..-43.6）。スタブのカムの手前の部分は裸で、位相合わせ治具が掛かる。刷るときは組立の向きのまま寝かせ、
    六角の下の面（法線 270 度）がベッド"""
    half_l = mm(P.SHAFT_HALF_L)
    je = mm(P.JOURNAL_END)
    x_end = row_cams(j)[0][1] + mm(P.JOINT_ENGAGE_CAM)
    sh = prism(shaft_poly(), "x", -half_l, x_end, f"shaft_{j}")
    union(sh, prism(circle((0, 0), mm(P.JOURNAL_D) / 2, 48), "x", -je, -half_l, "journal_n"))
    INFO.setdefault("shaft_len_mm", {})[str(j)] = round(x_end + half_l, 3)
    return sh


# --- 歯車 gear_j -----------------------------------------------------------------------------------------
def build_gear():
    """+X の端の部品 gear_j（軸の中心を原点にした局所）。歯車（X 40.0..42.4）+ 丸いボス Ø9.5（42.4..43.6、パッドの内面に当たる肩）+ +X の
    丸い軸受け Ø5（43.6..44.6）+ -X 面から開く雌の六角穴（深さ 2.4 = 歯幅。切り落とし六角 + 潰しリブ、口に 0.3 の面取り）。
    刷るときは歯の輪郭を XY 面にして -X 面（穴の口）がベッド、ボスと軸受けが上"""
    g = chain_gear_spec()
    x0, x1 = GEAR_X0, GEAR_X1
    plate = prism(gear_outline(g, P.CHAIN_TOOTH_PHASE_DEG), "x", x0, x1, "gear")
    cut(plate, prism(bore_poly(True), "x", x0 - CAM_BORE_PAD, x1 + CAM_BORE_PAD, "gear_bore"))
    cut(plate, bore_chamfer(x0))
    # 穴は歯車の板だけを貫き、ボスの面が底になる（ボスは板の +X 面に接して付ける。穴を先に開けてから接合）
    xb = x1 + mm(P.GEAR_BOSS_T)
    union(plate, prism(circle((0, 0), mm(P.GEAR_BOSS_D) / 2, 64), "x", x1, xb, "boss"))
    union(plate, prism(circle((0, 0), mm(P.JOURNAL_D) / 2, 48), "x", xb, mm(P.JOURNAL_END), "journal_p"))
    return plate, g


_CAMS = None


def load_cams():
    global _CAMS
    if _CAMS is None:
        with open(os.path.join(HERE, "build", "cams.json"), encoding="utf-8") as f:
            _CAMS = json.load(f)
    return _CAMS


def label_cutters(i, j, contour, x_face):
    """番号 "ij"（i = 列、j = 行）の 7 セグメントの字を +X 面（x_face）に 0.4mm 彫るカッターと、置いた位置。
    ハブの外・板の縁の内に入る箱 LABEL_W x LABEL_H を、上（psi = 90 度）に近く内側から探す"""
    import numpy as np
    V = np.asarray(contour, dtype=float)[::3]          # 凸なので、頂点を間引いた多角形は元の内側（探索を保守側に倒す）
    a, b = V, np.roll(V, -1, axis=0)
    e = b - a
    nrm = np.stack([e[:, 1], -e[:, 0]], axis=1)
    nrm /= np.hypot(nrm[:, 0], nrm[:, 1])[:, None]
    gx, gy = np.meshgrid(np.linspace(-LABEL_W / 2, LABEL_W / 2, 5), np.linspace(-LABEL_H / 2, LABEL_H / 2, 4))
    box_pts = np.stack([gx.ravel(), gy.ravel()], axis=1)
    hub = mm(P.SHAFT_AF) / math.sqrt(3.0) + LABEL_MARGIN       # スタブの外接円の外
    angles = sorted(np.arange(0.0, 360.0, 3.0), key=lambda t: abs(((t - 90.0 + 180.0) % 360.0) - 180.0))
    found = None
    for r in np.arange(6.0, 10.5, 0.15):
        for ang in angles:
            c = np.array([r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))])
            pts = box_pts + c
            if np.hypot(pts[:, 0], pts[:, 1]).min() < hub:
                continue
            dist = -((pts[:, None, :] - a[None, :, :]) * nrm[None, :, :]).sum(axis=2)
            if dist.min() >= LABEL_MARGIN:
                found = (float(c[0]), float(c[1]))
                break
        if found:
            break
    if found is None:
        raise RuntimeError(f"cam_{i}_{j}: 番号の箱 {LABEL_W}x{LABEL_H} が +X 面に入らない")
    cu, cv = found
    s = LABEL_STROKE
    dw, dh = (LABEL_W - 0.6) / 2, LABEL_H                         # 1 字の幅と高さ（字の間 0.6）
    segs = {"a": (0, 1, "h"), "d": (0, 0, "h"), "g": (0, 0.5, "h"), "f": (0, 1, "vu"), "b": (1, 1, "vu"),
            "e": (0, 0, "vl"), "c": (1, 0, "vl")}
    digit = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc"}
    cutters = []
    for pos, ch in enumerate(f"{i}{j}"):
        x0 = cu - LABEL_W / 2 + pos * (dw + 0.6)
        y0 = cv - LABEL_H / 2
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
    return cutters, (cu, cv)


def build_cam(i, j):
    """カム (i, j)（軸の中心を原点にした局所。X は組立の位置）。板 + 雄スタブ（+X、次の部品の雌穴の底まで）+ 雌穴（-X 面、深さ 2.8、
    切り落とし六角 + 潰しリブ、口に 0.3 の面取り）+ 番号"""
    c = load_cams()["cams"][j][i]
    xc = cam_x(i, j)
    x0, x1 = xc - CAM_T / 2, xc + CAM_T / 2
    ob = prism([tuple(p) for p in c["vertices"]], "x", x0, x1, f"cam_{i}_{j}")
    # 雌穴: -X 面から深さ JOINT_ENGAGE_CAM（2.8）の止まり穴。底に肉 1.2
    cut(ob, prism(bore_poly(True), "x", x0 - CAM_BORE_PAD, x0 + mm(P.JOINT_ENGAGE_CAM), "bore"))
    cut(ob, bore_chamfer(x0))
    # 雄スタブ: +X 面から次の部品の雌穴の底まで（切り落とし六角 AF5.5）。板の中へ 0.4 重ねる
    xs = stub_end(i, j)
    union(ob, prism(shaft_poly(), "x", x1 - STUB_OVERLAP, xs, "stub"))
    cutters, pos = label_cutters(i, j, c["vertices"], x1)
    cut_collection(ob, cutters, f"label_{i}{j}")
    INFO.setdefault("cam_label_pos_mm", {})[f"{i}_{j}"] = [round(pos[0], 2), round(pos[1], 2)]
    INFO.setdefault("cam_stub_len_mm", {})[f"{i}_{j}"] = round(xs - x1, 3)
    return ob


# --- 画素 pixel_i_j --------------------------------------------------------------------------------------
def _sq(w, dx=0.0):
    return [(dx - w / 2, -w / 2), (dx + w / 2, -w / 2), (dx + w / 2, w / 2), (dx - w / 2, w / 2)]


def build_pixel(parity):
    """画素 1 個（頭の中心を X = Y = 0 にした局所、Z は組立の位置、面一）。parity = 行 j の偶奇。
    頭（上縁に 0.3 の面取り）+ つば（頭の下側に 45 度の面取り）+ 角筒の茎（X に ±ROW_SHIFT ずれる）+ 足（YZ の板、45 度で広がる）。
    刷るときは頭の上面を下にして立てる。茎の空洞は +Y の壁の通気穴で外へ開ける。偶奇は茎の -Y 面の溝の本数（偶数行 1、奇数行 2）"""
    dx = mm(K.row_shift(parity))                       # 偶数行 +ROW_SHIFT、奇数行 -ROW_SHIFT
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
    union(top, prism(fin, "x", dx - foot_x / 2, dx + foot_x / 2, "foot"))
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
    body = prism(outline, "x", x_lo, x_gear, "horn_coupler")
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
    """位相合わせ治具（全体の座標。Y は軸の位置、Z は組立の位置）。YZ の薄い板に、軸 5 本の -X 端の裸の六角に上から被さる切り欠き
    （穴と同じ切り落とし六角 AF6.9 の上半分 + 角から下へ垂直 2mm）、軸の間の 4 つの耳（-X パッドの上面に座る）、持ち手の出っ張り"""
    x0, x1 = mm(P.COMB_X0), mm(P.COMB_X1)
    yh = mm(P.COMB_Y_HALF)
    z0, z1 = mm(P.COMB_Z0), mm(P.COMB_Z1)
    plate = [(-yh, z0), (yh, z0), (yh, z1), (COMB_HANDLE_Y, z1), (COMB_HANDLE_Y, COMB_HANDLE_TOP), (-COMB_HANDLE_Y, COMB_HANDLE_TOP),
             (-COMB_HANDLE_Y, z1), (-yh, z1)]
    ob = prism(plate, "x", x0, x1, "phase_comb")
    pad_top = ZC + mm(P.PAD_TOP_ABOVE)
    for ye in P.COMB_EAR_Y:
        y = mm(ye)
        union(ob, prism([(y - mm(P.COMB_EAR_W) / 2, pad_top), (y + mm(P.COMB_EAR_W) / 2, pad_top),
                         (y + mm(P.COMB_EAR_W) / 2, pad_top + COMB_EAR_H), (y - mm(P.COMB_EAR_W) / 2, pad_top + COMB_EAR_H)],
                        "x", mm(P.COMB_EAR_X0), x0 + 0.2, "ear"))
    ap = mm(P.SHAFT_BORE_AF) / 2                    # 切り欠きの天井（軸の中心から 3.45）
    rr = ap * 2 / math.sqrt(3.0)
    drop_v = -mm(P.COMB_NOTCH_DROP) - 1.0
    # 切り欠き = 穴と同じ輪郭の上半分（六角 AF6.9 の 60 度の角を、出っ張り面 HEX_CUT_BORE_D で切り落とした形）+ 角から下へ垂直。
    # 板が出っ張る側が穴と同じなので、軸の形が一致する向きでだけ櫛が下まで入る
    notch = clip_half([(rr, drop_v), (rr, 0.0), (rr / 2, ap), (-rr / 2, ap), (-rr, 0.0), (-rr, drop_v)], KEY_N, mm(P.HEX_CUT_BORE_D))
    for j in range(P.N):
        cut(ob, prism(translate_poly(notch, axis_y(j), ZC), "x", mm(P.COMB_EAR_X0) - 0.5, x1 + 0.5, f"notch_{j}"))
    return ob


# --- 全部品 ---------------------------------------------------------------------------------------------------
def part_ids():
    ids = [f"shaft_{j}" for j in range(P.N)] + [f"gear_{j}" for j in range(P.N)]
    ids += [f"cam_{i}_{j}" for j in range(P.N) for i in range(P.N)]
    ids += [f"pixel_{i}_{j}" for j in range(P.N) for i in range(P.N)] + ["horn_coupler", "phase_comb"]
    return ids


def build_moving():
    """全部品を組立姿勢（サーボ 90 度、phase_comb は装着位置）で作って返す。単位 m。オブジェクト名 = id"""
    out = {}
    for name in part_ids():
        old = bpy.data.objects.get(name)
        if old is not None:
            drop(old)
    INFO.clear()

    # 端の部品 shaft_j（行の偶奇で長さが違う）と歯車の部品 gear_j
    shafts = {par: build_shaft(par) for par in (0, 1)}       # 偶数行の代表 = 0、奇数行の代表 = 1
    gear_t, g = build_gear()
    for j in range(P.N):
        y = axis_y(j)
        out[f"shaft_{j}"] = inst(shafts[j % 2], f"shaft_{j}", (0.0, y, ZC))
        out[f"gear_{j}"] = inst(gear_t, f"gear_{j}", (0.0, y, ZC))
    for ob in (*shafts.values(), gear_t):
        drop(ob)

    # カム（25 枚それぞれ別の輪郭）
    for j in range(P.N):
        for i in range(P.N):
            cam = build_cam(i, j)
            out[f"cam_{i}_{j}"] = inst(cam, f"cam_{i}_{j}", (0.0, axis_y(j), ZC))
            drop(cam)

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
    PRINT_POSE[f"shaft_{_j}"] = {
        "euler_deg": (0.0, 0.0, 0.0),
        "reason": "組立の向きのまま寝かせて刷る（長さ 7.5〜13.4mm の六角スタブ + -X の Ø5 軸受け 1mm）。六角の下の面（法線 270 度）がベッド。"
                  "切り落とし面は上向き、他の面は 30 度の斜面。Ø5 の軸受けは六角の端面から 1mm の片持ちで、ベッドから 0.25 浮く",
        "support": "なし"}
    PRINT_POSE[f"gear_{_j}"] = {
        "euler_deg": _X_UP,
        "reason": "歯の輪郭を XY 面にして平置き。-X 面（雌穴の口、0.3 面取り）がベッド。丸いボス Ø9.5（1.2）と +X の Ø5 軸受け（1.0）が上へ立つ。"
                  "歯の側面・穴の切り落とし六角とリブは鉛直",
        "support": "なし。雌穴の底（ボスの面、橋 5.9mm）だけが水平な下向き面で、内側"}
for _j in range(P.N):
    for _i in range(P.N):
        PRINT_POSE[f"cam_{_i}_{_j}"] = {
            "euler_deg": (0.0, -90.0, -90.0),
            "reason": "板（厚み 4）を平置きにして雄スタブ（+X、六角 AF5.5）を上へ立てる（高さ 3.5〜15.8、太さの 2.9 倍以下）。-X 面がベッド"
                      "（雌穴の口に 0.3 の面取り）。番号は上になる +X 面。Z まわり -90 度で番号が正立（右 = +Y、上 = +Z）",
            "support": "なし。輪郭は鉛直な壁、雌穴の切り落とし六角とリブも鉛直。雌穴の底（橋 5.9mm、内側）だけが水平な下向き面"}
        PRINT_POSE[f"pixel_{_i}_{_j}"] = {
            "euler_deg": (180.0, 0.0, 0.0),
            "reason": "頭の上面（見える面）を下にして立てる（上縁に 0.3 の面取り）。つばは頭の下側が 45 度の面取り。茎は 9mm 角、"
                      "頭とつばの上に 27mm（3 倍）。足の平らな面（カムに乗る面）が最上面",
            "support": "なし。見える面（頭の上面、つばの 45 度面取り、茎と足の外面）に水平な下向き面は無い。足の 45 度の広がりは 45 度ちょうどで"
                       "張り出しに数えない。下向きの水平面は茎の中だけ: 空洞の天井（橋 5.8mm、33.6mm2）、通気穴の上辺（3mm、4.8mm2）、"
                       "偶奇の溝の上端（0.4mm2）"}
PRINT_POSE["horn_coupler"] = {
    "euler_deg": _X_UP,
    "reason": "-X 面（ポケットの口）を下にして平置き。歯の板（2.4）が下、ポケットは下面の凹み（橋は最大幅 7.3mm）、"
              "口は 45 度で 0.3 面取りしてある。上へ向かって細るだけで、支えのピンは上に 2.1mm 立つ",
    "support": "なし。ポケットの天井（橋 7.3mm 以下、見えない）だけが水平な下向き面"}
PRINT_POSE["phase_comb"] = {
    "euler_deg": (0.0, 90.0, 0.0),
    "reason": "+X 面を下にして平置き（厚み 1.5）。耳は -X 側へ出ているので上へ 1.4mm 立つ",
    "support": "なし"}
