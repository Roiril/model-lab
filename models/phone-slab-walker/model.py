"""スマホ板ロボットの形を作り、build/ の契約（部品表・動作・組立）を書き出す。

    ./run.sh models/phone-slab-walker/model.py
    py -3.11 tools/mechgate.py check phone-slab-walker
"""
import importlib
import math
import os
import struct
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [HERE, os.path.join(ROOT, "lib")]
sys.stdout.reconfigure(encoding="utf-8")

import params as P  # noqa: E402
importlib.reload(P)
from printmech import contract as C  # noqa: E402
from printmech.geometry import box, circle, clean, cut, hull3d, intersect, loft_rings, nonmanifold, nonmanifold_where, prism, transform, union  # noqa: E402

BUILD = os.path.join(HERE, "build")
EXPORTS = os.path.join(ROOT, "exports")
TRIALS = os.path.join(ROOT, "prints", "phone-slab-walker", "trial")
os.makedirs(BUILD, exist_ok=True)
os.makedirs(TRIALS, exist_ok=True)

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)


def tris_mm(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    out = np.array([[tuple(v.co) for v in f.verts] for f in bm.faces], dtype=float)
    bm.free()
    return out


def write_stl(path, tris):
    data = bytearray(b"phone-slab-walker".ljust(80) + struct.pack("<I", len(tris)))
    for t in tris:
        n = np.cross(t[1] - t[0], t[2] - t[0])
        length = np.linalg.norm(n)
        n = n / length if length > 0 else n
        data += struct.pack("<12fH", *n, *t.reshape(-1), 0)
    with open(path, "wb") as fh:
        fh.write(bytes(data))


def to_bed(tris, orient):
    """刷る向きへ。原点へ寄せて z=0 に置く"""
    x, y, z = tris[..., 0], tris[..., 1], tris[..., 2]
    if orient == "rear_down":
        out = np.stack([x, -z, y], axis=-1)
    elif orient == "front_down":
        out = np.stack([x, z, -y], axis=-1)
    elif orient == "outer_down_right":
        out = np.stack([z, y, -x], axis=-1)
    elif orient == "outer_down_left":
        out = np.stack([-z, y, x], axis=-1)
    elif orient == "asis":
        out = tris.copy()
    else:
        raise ValueError(orient)
    lo = out.reshape(-1, 3).min(axis=0)
    return out - lo


# --- 共通の形 ----------------------------------------------------------------------------
def dovetail(x_sign, y0, z0, z1, grow=0.0, name="tongue"):
    """舌の断面（XY）を z 方向に伸ばす。grow>0 で溝の大きさにする"""
    xc = x_sign * P.TONGUE_X
    base, tip = P.TONGUE_BASE + grow, P.TONGUE_TIP + grow
    h = P.TONGUE_H + grow
    return prism([(xc - base, y0 - 0.5), (xc + base, y0 - 0.5), (xc + base, y0), (xc + tip, y0 + h), (xc - tip, y0 + h), (xc - base, y0)],
                 "z", z0, z1, name)


# --- 中央板の背中側（トレイ）-------------------------------------------------------------------
def make_tray():
    w = P.HALF_W
    lower = box(-w, w, P.Y_REAR, P.Y_SLOT_BACK, P.Z_SPLIT, P.Z_SLOT1 + 0.01, "tray")
    upper = box(-w, w, P.Y_REAR, P.Y_POCKET, P.Z_SLOT1, P.Z_TOP, "upper")
    tray = union(lower, upper)
    # マイコンと電池の部屋
    cav_w = P.CAV_W
    cut(tray, box(-cav_w, cav_w, P.Y_CAV_BACK, P.Y_DIV_BACK + 0.01, P.Z_SPLIT - 1, P.Z_SLOT1, "cav"))
    # 仕切りの座（棚より上は少し広い）
    shelf = cav_w + P.SHELF_W
    cut(tray, box(-shelf, shelf, P.Y_DIV_BACK, P.Y_SLOT_BACK + 1, P.Z_SPLIT - 1, P.Z_SLOT1, "seat"))
    # サーボの穴（前から落とし込む）
    for s in (-1, 1):
        x0, x1 = sorted((s * P.SERVO_X_REAR, s * P.SERVO_X_TOP))
        cut(tray, box(x0, x1, -P.Y_POCKET, P.Y_POCKET + 1, P.Z_STOP1, P.Z_POCKET_TOP, "pocket"))
        # ホーンの通り道（上が開いた U 字）
        xw0, xw1 = sorted((s * (P.SERVO_X_TOP - 0.3), s * (w + 1)))
        cut(tray, prism(circle((0.0, P.HIP_Z), P.HOLE_R, 64), "x", xw0, xw1, "hole"),
            box(xw0, xw1, 0, P.Y_POCKET + 1, P.HIP_Z - P.HOLE_R, P.HIP_Z + P.HOLE_R, "u"))
    # コネクタの部屋（尻の間）と、線を下へ通す口
    cut(tray, box(-P.SERVO_X_REAR - 0.1, P.SERVO_X_REAR + 0.1, -P.Y_POCKET, P.Y_POCKET + 1, P.Z_STOP1 + 6, P.Z_POCKET_TOP - 7, "gap"))
    # 刷る向きで天井にならないよう、前まで抜く。スマホは両側の壁で止まる
    cut(tray, box(-P.CABLE_HALF, P.CABLE_HALF, -P.Y_POCKET, P.Y_POCKET + 1, P.Z_SLOT1 - 1, P.Z_STOP1 + 0.5, "cable"))
    # 尻の間の柱は床から立てる。前半分を線の通り道にする
    cut(tray, box(-P.CABLE_HALF, P.CABLE_HALF, P.PILLAR_Y1, P.Y_POCKET + 1, P.Z_STOP1, P.Z_STOP1 + 7, "cableFront"))
    # 仕切りの下の止め
    union(tray, box(-shelf - 0.5, -cav_w - 0.02, P.Y_DIV_BACK - 0.5, P.Y_SLOT_BACK - 0.02, P.Z_SLOT0 - 3, P.Z_SLOT0, "stopL"),
          box(cav_w + 0.02, shelf + 0.5, P.Y_DIV_BACK - 0.5, P.Y_SLOT_BACK - 0.02, P.Z_SLOT0 - 3, P.Z_SLOT0, "stopR"))
    # 舌
    for s in (-1, 1):
        union(tray, dovetail(s, P.Y_SLOT_BACK, P.Z_SPLIT + 0.5, P.Z_SLOT1 - 0.3, name="tongueLow"))
    # 頭の庇: 前枠の上端の爪を受けて、前へ開かないようにする
    union(tray, box(-w, w, P.Y_POCKET - 0.5, P.Y_FRONT, P.Z_TOP - P.HOOD_H, P.Z_TOP, "hood"))
    for s in (-1, 1):
        x0, x1 = sorted((s * P.TAB_X[0], s * P.TAB_X[1]))
        plate_top = P.Z_TOP - P.HOOD_H - 0.2
        y_a = P.TAB_Y[1] + P.TAB_FIT * math.sqrt(2)
        z_b = plate_top + P.TAB_RISE + P.TAB_FIT
        cut(tray, prism([(P.TAB_Y[0] - P.TAB_FIT, plate_top - 0.5), (y_a, plate_top - 0.5), (y_a, plate_top),
                         (y_a - (z_b - plate_top), z_b), (P.TAB_Y[0] - P.TAB_FIT, z_b)],
                        "x", x0 - P.TAB_FIT, x1 + P.TAB_FIT, "tabPocket"))
    # 爪の窓
    z0, z1 = P.Z_SPLIT + P.SNAP_WINDOW_Z[0], P.Z_SPLIT + P.SNAP_WINDOW_Z[1]
    ya, yb = P.SNAP_Y[0] - 0.3, P.SNAP_Y[1] + 0.3
    window = [(ya, z0), (yb, z0), (yb + (z1 - z0) / 2, (z0 + z1) / 2), (yb, z1), (ya, z1)]
    cut(tray, prism(window, "x", -w - 1, -cav_w + 0.01, "winL"),
        prism(window, "x", cav_w - 0.01, w + 1, "winR"))
    # マイコンの台と軸
    for u, v in P.BOARD_HOLES:
        z = P.BOARD_Z0 + u
        x = v - P.BOARD_W / 2
        union(tray, prism(circle((x, z), 3.0, 32), "y", P.Y_CAV_BACK - 0.1, P.Y_CAV_BACK + P.BOARD_STANDOFF, "pad"),
              prism(circle((x, z), P.BOARD_PEG_R, 24), "y", P.Y_CAV_BACK, P.Y_CAV_BACK + P.BOARD_STANDOFF + P.BOARD_PEG_H, "peg"))
    # 電池の部屋の仕切り（線を通す口を残す）
    fence_z = P.BOARD_Z0 + P.BOARD_L + 4
    union(tray, box(-cav_w - 0.1, -12, P.Y_CAV_BACK - 0.1, P.Y_CAV_BACK + 6, fence_z, fence_z + 3, "fL"),
          box(12, cav_w + 0.1, P.Y_CAV_BACK - 0.1, P.Y_CAV_BACK + 6, fence_z, fence_z + 3, "fR"))
    # 電源線の口（背中の下）
    cut(tray, box(-7, 7, P.Y_REAR - 1, P.Y_CAV_BACK + 1, P.Z_SPLIT + 4, P.Z_SPLIT + 12, "power"))
    tray.name = "tray"
    return tray


# --- 前枠 ---------------------------------------------------------------------------------
def make_frame():
    w = P.HALF_W
    low = box(-w, w, P.Y_SLOT_BACK, P.Y_FRONT, P.Z_SPLIT, P.Z_SLOT1, "frame")
    plate_top = P.Z_TOP - P.HOOD_H - 0.2
    up = box(-w, w, P.Y_POCKET, P.Y_FRONT, P.Z_SLOT1 - 0.01, plate_top, "frameUp")
    frame = union(low, up)
    half_slot = P.SLOT_W / 2
    # スマホの通り道（下から差す。上は壁で止まる）
    cut(frame, box(-half_slot, half_slot, P.Y_SLOT_BACK - 1, P.Y_SLOT_FRONT, P.Z_SPLIT - 1, P.Z_SLOT1, "slot"))
    # 画面の窓。ベゼルの幅だけ縁で押さえる
    win = P.PHONE_W / 2 - 3.0
    cut(frame, box(-win, win, P.Y_SLOT_FRONT - 0.5, P.Y_FRONT + 1, P.Z_SLOT0 + 5, P.Z_SLOT1 - 4, "window"))
    # 電源・音量ボタンを押し続けない逃げ（上 90mm の両側）
    for s in (-1, 1):
        ya, yb = P.Y_SLOT_BACK + 2.8, P.Y_SLOT_FRONT - 2.8
        xa, xb = half_slot - 0.1, half_slot + 1.5
        outline = [(xa, ya), (xb, ya + (xb - xa)), (xb, yb), (xa, yb)] if s > 0 else [(-xa, ya), (-xa, yb), (-xb, yb), (-xb, ya + (xb - xa))]
        cut(frame, prism(outline, "z", P.Z_SLOT1 - 90, P.Z_SLOT1 - 5, "button"))
        # 溝
        cut(frame, dovetail(s, P.Y_SLOT_BACK, P.Z_SPLIT - 1, P.Z_SLOT1 + 1, grow=P.TONGUE_FIT, name="grooveLow"))
        # 上端の爪。前の面を根元から先まで 45° にして、刷るとき浮かせない
        x0, x1 = sorted((s * P.TAB_X[0], s * P.TAB_X[1]))
        y0, y1 = P.TAB_Y
        z1 = plate_top + P.TAB_RISE
        union(frame, prism([(y0, plate_top - 0.5), (y1, plate_top - 0.5), (y1, plate_top), (y1 - P.TAB_RISE, z1), (y0, z1)],
                           "x", x0, x1, "tab"))
    frame.name = "frame"
    return frame


def make_divider():
    w = P.CAV_W + P.SHELF_W - 0.3
    d = box(-w, w, P.Y_DIV_BACK, P.Y_SLOT_BACK - 0.02, P.Z_SLOT0 + 0.2, P.Z_SLOT1 - 0.2, "divider")
    return d


# --- 足のふた -----------------------------------------------------------------------------
def make_cap():
    w = P.HALF_W
    zb, zs = P.Z_BOTTOM, P.Z_SPLIT
    h = P.FOOT_D / 2
    ch = P.SOLE_CHAMFER
    # 足: 下が広く、45° で本体の幅へ戻る
    pts = []
    for x in (-w, w):
        pts += [(x, -h + ch, zb), (x, h - ch, zb), (x, -h, zb + ch), (x, h, zb + ch),
                (x, P.Y_REAR, zb + ch + (h + P.Y_REAR)), (x, P.Y_FRONT, zb + ch + (h - P.Y_FRONT))]
    foot = hull3d(pts, "foot")
    wall = box(-w, w, P.Y_REAR, P.Y_FRONT, zb + 2, zs, "capWall")
    cap = union(foot, wall)
    cut(cap, box(-w + 2.5, w - 2.5, P.Y_REAR + 2.5, P.Y_FRONT - 2.5, zb + P.CAP_FLOOR, zs + 1, "chamber"))
    # 爪: 床から立ち上がるしなる腕
    cav_w = P.CAV_W
    z_root = zb + P.CAP_FLOOR - 0.1
    top = zs + P.SNAP_WINDOW_Z[0] + 2.5
    for s in (-1, 1):
        a0, a1 = sorted((s * (cav_w - 0.2 - P.SNAP_T), s * (cav_w - 0.2)))
        union(cap, box(a0, a1, P.SNAP_Y[0], P.SNAP_Y[1], z_root, top, "arm"))
        # 爪の出っ張り
        xi = s * (cav_w - 0.2 - 0.05)
        xo = s * (cav_w + P.SNAP_DELTA - 0.2)
        # 上側は差し込むときの斜面。下側は刷れるよう 45° にして、窓の下の縁に掛ける
        z_edge = zs + P.SNAP_WINDOW_Z[0] + 0.05          # 窓の内壁の位置での爪の下面
        wall_to_tip = abs(xo) - cav_w
        z_tip = z_edge + wall_to_tip
        z_in = z_edge - abs(abs(xi) - cav_w)
        z_flat = z_tip + 0.5
        z_top = z_flat + P.SNAP_DELTA + 0.15
        bump = [(xi, z_in), (xo, z_tip), (xo, z_flat), (xi, z_top)] if s > 0 else [(xi, z_in), (xi, z_top), (xo, z_flat), (xo, z_tip)]
        union(cap, prism(bump, "y", P.SNAP_Y[0], P.SNAP_Y[1], "bump"))
    # スマホを受ける柱。USB プラグに重さをかけない
    for s in (-1, 1):
        x0, x1 = sorted((s * P.PHONE_POST_X[0], s * P.PHONE_POST_X[1]))
        union(cap, box(x0, x1, P.Y_SLOT_BACK + 0.6, P.Y_SLOT_FRONT - 0.6, zb + P.CAP_FLOOR - 0.5, P.Z_SLOT0 - 0.1, "post"))
    cap.name = "cap"
    return cap


# --- 脚 -----------------------------------------------------------------------------------
def leg_outline():
    y0, y1 = -P.FOOT_D / 2, P.FOOT_D / 2
    ch, flare_y = P.SOLE_CHAMFER, P.Y_FRONT
    top = P.LEG_TOP
    r = 8.0
    pts = [(y0 + ch, 0.0), (y1 - ch, 0.0), (y1, ch), (flare_y, ch + (y1 - flare_y))]
    for k in range(9):
        a = math.radians(90 * k / 8)
        pts.append((flare_y - r + r * math.cos(a), top - r + r * math.sin(a)))
    for k in range(9):
        a = math.radians(90 + 90 * k / 8)
        pts.append((-flare_y + r + r * math.cos(a), top - r + r * math.sin(a)))
    pts += [(-flare_y, ch + (y1 - flare_y)), (y0, ch)]
    return pts


def along_x(c, stations, name, n=32):
    """x 軸に沿った回転体。c=(y,z)、stations=[(x, 半径), ...]"""
    rings = [(x, [(-q[1], q[0]) for q in circle(c, r, n)]) for x, r in stations]
    ob = loft_rings(rings, name)
    transform(ob, Matrix.Rotation(math.pi / 2, 4, "Y"))
    clean(ob)
    return ob


def make_leg_right():
    leg = prism(leg_outline(), "x", P.LEG_X0, P.LEG_X1, "leg_right")
    union(leg, prism(circle((0.0, P.HIP_Z), P.BOSS_R, 64), "x", P.LEG_SEAT_X, P.LEG_X0 + 0.5, "boss"))
    cut(leg, prism(circle((0.0, P.HIP_Z), P.SPLINE_R + 0.7, 32), "x", P.LEG_SEAT_X - 1, P.TIP_X + 0.6, "spline"))
    o = P.HORN_HOLE_OFFSET
    seat = P.LEG_SEAT_X + P.BOLT_SEAT_T
    # 穴の奥は 45° の円錐で絞る。外を下に刷っても天井にならず、ねじの頭が円錐に座って芯が出る
    head_clear = P.BOLT_HEAD_R + 0.1
    x_cone = seat + 0.3 - (head_clear - P.BOLT_HOLE_R)
    x_full = x_cone + (P.BOLT_WELL_R - P.BOLT_HOLE_R)
    for dy, dz in ((o, o), (o, -o), (-o, o), (-o, -o)):
        c = (dy, P.HIP_Z + dz)
        # 穴と円錐と広い穴を、1 本の回転体として抜く
        stations = [(P.LEG_SEAT_X - 1.3, P.BOLT_HOLE_R), (x_cone, P.BOLT_HOLE_R),
                    (x_full, P.BOLT_WELL_R), (P.LEG_X1 + 1, P.BOLT_WELL_R)]
        cut(leg, along_x(c, stations, "boltHole"))
    return leg


def mirrored(ob, name):
    new = ob.copy()
    new.data = ob.data.copy()
    bpy.context.collection.objects.link(new)
    new.name = name
    transform(new, Matrix.Scale(-1, 4, (1, 0, 0)))
    clean(new)
    return new


# --- 既製部品の形（当たりと組立の確かめ用に単純化した立体）------------------------------------------
def make_servo(sign, name):
    """尻を中央へ、出力軸を外へ。長辺は Z（出力軸が上寄り）。ホーンは別部品"""
    ax = P.SERVO_X_REAR
    def wx(zs):
        return ax + (zs - P.SERVO_ZS_REAR)
    def wz(xs):
        return P.HIP_Z + (xs - P.SERVO_SHAFT_XS)
    d = P.SERVO_D / 2
    body = box(wx(P.SERVO_ZS_CAP), wx(P.SERVO_ZS_TOP), -d, d, wz(-P.SERVO_L / 2), wz(P.SERVO_L / 2), name)
    union(body, box(wx(P.SERVO_ZS_REAR), wx(P.SERVO_ZS_CAP) + 0.1, -d, d, wz(P.SERVO_CAP_XS[0]), wz(P.SERVO_CAP_XS[1]), "rear"))
    # 右は +Y 側、左は -Y 側のコネクタを使う（中央で互い違いにして隙間を分け合う）
    y0, y1 = P.CONNECTOR_YS
    zc = wz(P.CONNECTOR_XS)
    union(body, box(wx(P.SERVO_ZS_REAR) - P.CONNECTOR_LEN, wx(P.SERVO_ZS_REAR) + 0.1, y0, y1, zc - 3, zc + 3, "connector"))
    if sign < 0:
        transform(body, Matrix.Rotation(math.pi, 4, "Z"))
        clean(body)
    return body


def make_horn_pair():
    pair = None
    o = P.HORN_HOLE_OFFSET
    for s in (-1, 1):
        x0, x1 = sorted((s * (P.HORN_X0 + 0.02), s * P.HORN_X1))
        disc = prism(circle((0.0, P.HIP_Z), P.HORN_R, 64), "x", x0, x1, "disc")
        xa, xb = sorted((s * P.HORN_X1, s * P.TIP_X))
        tip = prism(circle((0.0, P.HIP_Z), P.SPLINE_R, 32), "x", xa - (0.1 if s > 0 else 0), xb + (0.1 if s < 0 else 0), "tip")
        disc = union(disc, tip)
        for dy, dz in ((o, o), (o, -o), (-o, o), (-o, -o)):
            cut(disc, prism(circle((dy, P.HIP_Z + dz), P.HORN_HOLE_R + 0.05, 24), "x", x0 - 1, x1 + 1, "h"))
        if pair is None:
            pair = disc
        else:
            # 離れた 2 つの円盤を 1 つのメッシュに（ゲート用の 1 アクチュエータ）
            bm = bmesh.new()
            bm.from_mesh(pair.data)
            bm.from_mesh(disc.data)
            bm.to_mesh(pair.data)
            bm.free()
            bpy.data.objects.remove(disc, do_unlink=True)
    pair.name = "horn_pair"
    return pair


def make_bolts(name):
    """右脚の 4 本。ゲートが抜け止めと駆動を測る"""
    o = P.HORN_HOLE_OFFSET
    head0 = P.LEG_SEAT_X + P.BOLT_SEAT_T + 0.3
    out = None
    for dy, dz in ((o, o), (o, -o), (-o, o), (-o, -o)):
        c = (dy, P.HIP_Z + dz)
        b = prism(circle(c, P.BOLT_SHANK_R, 24), "x", P.HORN_X0 + 0.5, head0 + 0.1, "shank")
        b = union(b, prism(circle(c, P.BOLT_HEAD_R, 24), "x", head0, head0 + P.BOLT_HEAD_H, "head"))
        if out is None:
            out = b
        else:
            bm = bmesh.new()
            bm.from_mesh(out.data)
            bm.from_mesh(b.data)
            bm.to_mesh(out.data)
            bm.free()
            bpy.data.objects.remove(b, do_unlink=True)
    out.name = name
    return out


def make_phone():
    h = P.PHONE_W / 2
    gap = (P.SLOT_T - P.PHONE_T) / 2
    return box(-h, h, P.Y_SLOT_BACK + gap, P.Y_SLOT_FRONT - gap, P.Z_SLOT0 + 0.3, P.Z_SLOT0 + 0.3 + P.PHONE_L, "phone")


def make_board():
    x0, x1 = -P.BOARD_W / 2, P.BOARD_W / 2
    y0 = P.Y_CAV_BACK + P.BOARD_STANDOFF
    board = box(x0, x1, y0 + 0.02, y0 + P.BOARD_T, P.BOARD_Z0, P.BOARD_Z0 + P.BOARD_L, "board")
    for u, v in P.BOARD_HOLES:
        cut(board, prism(circle((v - P.BOARD_W / 2, P.BOARD_Z0 + u), 1.6, 24), "y", y0 - 1, y0 + P.BOARD_T + 1, "h"))
    return board


# --- 組み立て ------------------------------------------------------------------------------
tray = make_tray()
frame = make_frame()
divider = make_divider()
cap = make_cap()
leg_r = make_leg_right()
leg_l = mirrored(leg_r, "leg_left")
servo_r = make_servo(1, "servo_right")
servo_l = make_servo(-1, "servo_left")
horn = make_horn_pair()
bolts_r = make_bolts("bolts_right")
bolts_l = mirrored(bolts_r, "bolts_left")
phone = make_phone()
board = make_board()

PRINTED = [
    ("tray", tray, "rear_down", "背中側のトレイ（サーボ・マイコン・電池）", "#5f6b73"),
    ("frame", frame, "front_down", "前枠（スマホを押さえる）", "#3f474d"),
    ("divider", divider, "rear_down", "仕切り板（スマホとマイコンの間）", "#8a959c"),
    ("cap", cap, "asis", "足のふた（中央板の足）", "#2f353a"),
    ("leg_right", leg_r, "outer_down_right", "右脚", "#70797f"),
    ("leg_left", leg_l, "outer_down_left", "左脚", "#70797f"),
]
STOCK = [
    ("servo_right", servo_r, "右サーボ STS3215", "#1c1c1c"),
    ("servo_left", servo_l, "左サーボ STS3215", "#1c1c1c"),
    ("horn_pair", horn, "左右のホーン（別のサーボだが同じ角度で掃く）", "#c9ced2"),
    ("bolts_right", bolts_r, "右脚のホーンねじ 4 本（サーボ付属）", "#b0b5b8"),
    ("bolts_left", bolts_l, "左脚のホーンねじ 4 本（サーボ付属）", "#b0b5b8"),
    ("phone", phone, "Pixel 7a", "#0b0b0d"),
    ("board", board, "Arduino Leonardo R3", "#1b6f8a"),
]

parts = []
for pid, ob, orient, label, color in PRINTED:
    clean(ob)
    assert nonmanifold(ob) == 0, (pid, nonmanifold(ob), nonmanifold_where(ob, 12))
    tr = tris_mm(ob)
    write_stl(os.path.join(BUILD, f"{pid}.stl"), tr)
    write_stl(os.path.join(BUILD, f"print_{pid}.stl"), to_bed(tr, orient))
    parts.append(dict(id=pid, assembly=f"build/{pid}.stl", print=f"build/print_{pid}.stl", label=label, color=color))
for pid, ob, label, color in STOCK:
    clean(ob)
    assert nonmanifold(ob) == 0, (pid, nonmanifold(ob), nonmanifold_where(ob, 12))
    write_stl(os.path.join(BUILD, f"{pid}.stl"), tris_mm(ob))
    parts.append(dict(id=pid, assembly=f"build/{pid}.stl", label=label, color=color))

C.write_manifest(BUILD, parts, meta=dict(title="スマホ板ロボット", units="mm", hipZ=P.HIP_Z, halfWidth=P.HALF_W,
                                       dimensions_mm=[round(2 * P.LEG_X1, 1), P.FOOT_D, round(P.Z_TOP, 1)]))

# --- 動作: 脚とホーンとねじが腰の軸まわりに回る ---------------------------------------------------
MOVING = ["leg_right", "leg_left", "horn_pair", "bolts_right", "bolts_left"]
STATIC = ["tray", "frame", "divider", "cap", "servo_right", "servo_left", "phone", "board"]
frames = []
n = int(round(2 * P.SWING_DEG / P.SWING_STEP))
for i in range(n + 1):
    deg = -P.SWING_DEG + i * P.SWING_STEP
    rot = C.rotation((1, 0, 0), deg, pivot=(0.0, 0.0, P.HIP_Z))
    tf = {p: rot for p in MOVING}
    tf.update({p: np.eye(4) for p in STATIC})
    frames.append((deg, tf))
C.write_motion(BUILD, frames, note="左右の脚は別サーボ。脚どうしは触れないので同じ角度で掃いて、脚と中央板の当たりを見る")

# --- 組立: 前から落とし込み、前枠とスマホは下から、脚は横から ------------------------------------------
plan = C.AssemblyPlan()
plan.place("tray", "トレイを置く", ["tray"], "背中を下にして置く")
plan.move("servos", "サーボを前から落とし込む", ["servo_right", "servo_left", "horn_pair"],
          C.straight_path(["servo_right", "servo_left", "horn_pair"], C.translation(0, 35, 0)), 36,
          "ホーンを付けたまま。線は尻の間から下へ。実機は 1 個ずつ入れる")
plan.move("board", "マイコンを 4 本の軸へ", ["board"], C.straight_path(["board"], C.translation(0, 30, 0)), 31, "USB を下へ向ける")
plan.move("divider", "仕切り板を棚へ", ["divider"], C.straight_path(["divider"], C.translation(0, 20, 0)), 21, "")
plan.move("frame", "前枠を下から滑らせる", ["frame"], C.straight_path(["frame"], C.translation(0, 0, -182)), 183,
          "両側の舌が溝に入る。上の壁で止まる")
plan.move("phone", "スマホを下から差す", ["phone"], C.straight_path(["phone"], C.translation(0, 0, -165)), 166, "USB ケーブルを挿してから")
plan.move("cap", "足のふたをはめる", ["cap"], C.straight_path(["cap"], C.translation(0, 0, -25)), 26, "爪が窓に入るまで押す")
plan.move("leg_right", "右脚をホーンへ", ["leg_right"], C.straight_path(["leg_right"], C.translation(12, 0, 0)), 13, "脚をまっすぐ、サーボは Z 命令の位置で")
plan.move("leg_left", "左脚をホーンへ", ["leg_left"], C.straight_path(["leg_left"], C.translation(-12, 0, 0)), 13, "")
plan.move("bolts_right", "右脚のねじ 4 本", ["bolts_right"], C.straight_path(["bolts_right"], C.translation(30, 0, 0)), 31, "穴の奥からホーンへねじ込む")
plan.move("bolts_left", "左脚のねじ 4 本", ["bolts_left"], C.straight_path(["bolts_left"], C.translation(-30, 0, 0)), 31, "")
plan.write(BUILD, calibration="tools/mechgate.py が測る", passed=True)

# --- 確かめ用の小さな部品 --------------------------------------------------------------------------
def coupon(source, band, orient, name):
    ob = source.copy()
    ob.data = source.data.copy()
    bpy.context.collection.objects.link(ob)
    intersect(ob, box(*band, "band"))
    clean(ob)
    write_stl(os.path.join(TRIALS, name), to_bed(tris_mm(ob), orient))


# サーボの穴と U 字（右半分）。STS3215 が入るか、ホーンが通るかを見る
coupon(tray, (0.0, P.HALF_W + 2, P.Y_REAR - 1, P.Y_POCKET + 3, P.Z_SLOT1 - 1, P.Z_TOP + 1), "rear_down", "servo_pocket.stl")
# ホーンとねじ。脚の座面だけ切り出す
coupon(leg_r, (P.LEG_SEAT_X - 1, P.LEG_X1 + 1, -14, 14, P.HIP_Z - 14, P.HIP_Z + 13.4), "outer_down_right", "horn_seat.stl")
# スマホの通り道。厚みと幅を、下から 25mm の帯で見る
coupon(frame, (-P.HALF_W - 1, P.HALF_W + 1, P.Y_SLOT_BACK - 1, P.Y_FRONT + 1, P.Z_SLOT0 - 1, P.Z_SLOT0 + 24), "front_down", "phone_slot.stl")

# Studio の全体 STL
everything = [tris_mm(ob) for _, ob, *_ in PRINTED] + [tris_mm(ob) for _, ob, *_ in STOCK]
write_stl(os.path.join(EXPORTS, "phone-slab-walker.stl"), np.concatenate(everything))

print(f"腰 z={P.HIP_Z:.1f} 全高 {P.Z_TOP:.1f} 中央板の幅 {2 * P.HALF_W:.1f} 全幅 {2 * P.LEG_X1:.1f} 足 {P.FOOT_D}")
print("done")
