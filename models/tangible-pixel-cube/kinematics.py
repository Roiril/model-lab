"""サーボ角 → 各軸の角 → 各画素の高さ。部品ごとの剛体変換。bpy 非依存。単位は m と度。

軸角 phi は +X まわりの右ねじ（+Y から +Z へ回る向き）を正とする。phi = 0（サーボ THETA_FLAT）で全画素が面一。
カムの枠（u, v）は phi = 0 で u = +Y、v = +Z。上向きの単位ベクトルは枠の上で n(phi) = (sin phi, cos phi) と書ける。
カムの高さ（支持関数）は h(phi) = max over contour of p . n(phi)。足の下面 Z = Zc(軸) + h(phi) になる。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import params as P


# --- 位置の基本 -------------------------------------------------------------
def col_x(i):
    """列 i（0..4）の頭の中心 X"""
    return P.PITCH * (i - 2)


def axis_y(j):
    """軸 j（行 j）の Y。この上に行 j の画素が並ぶ"""
    return P.PITCH * (j - 2)


def row_shift(j):
    """行 j の互い違いの量（偶数行 +、奇数行 -）"""
    return P.ROW_SHIFT if j % 2 == 0 else -P.ROW_SHIFT


def cam_x(i, j):
    """画素 (列 i, 行 j) のカムとつば下の茎の中心 X"""
    return col_x(i) + row_shift(j)


# --- 角度 ------------------------------------------------------------------------
def servo_delta(theta_deg, theta_flat=None):
    """サーボ出力軸の回転量（度）。THETA_FLAT を 0 にした値"""
    return theta_deg - (P.THETA_FLAT if theta_flat is None else theta_flat)


def axis_angle(theta_deg, j, theta_flat=None):
    """サーボ角 theta から軸 j の角 phi（度）。増速比 G_RATIO と回転方向 AXIS_DIR を掛ける"""
    return P.AXIS_DIR[j] * P.G_RATIO * servo_delta(theta_deg, theta_flat)


def wrap180(a):
    return (a + 180.0) % 360.0 - 180.0


def table_phis(j, thetas=None, theta_flat=None):
    """軸 j の各表の中心角（度、-180..180 に畳む）"""
    th = P.TABLE_THETA if thetas is None else thetas
    return [wrap180(axis_angle(t, j, theta_flat)) for t in th]


def table_theta_to_phi_range(theta_flat=None):
    """サーボの使用範囲 SERVO_MIN..SERVO_MAX が作る軸角の範囲の半幅（度）"""
    d = max(abs(servo_delta(P.SERVO_MIN_DEG, theta_flat)), abs(servo_delta(P.SERVO_MAX_DEG, theta_flat)))
    return d * P.G_RATIO


# --- 高さ ------------------------------------------------------------------------
def pixel_height(cam, phi_deg):
    """カム（cams.build_cam の返す辞書）が軸角 phi のとき、画素の高さ（m、面一 = 0）"""
    import numpy as np
    V = np.asarray(cam["vertices"], dtype=float)          # mm
    r = math.radians(phi_deg)
    h = float((V @ np.array([math.sin(r), math.cos(r)])).max())
    return (h - P.CAM_RB * 1000.0) / 1000.0


def pixel_heights(cams, theta_deg, theta_flat=None):
    """cams[j][i] から 5x5 の高さ（m）。h[j][i]"""
    return [[pixel_height(cams[j][i], axis_angle(theta_deg, j, theta_flat)) for i in range(P.N)] for j in range(P.N)]


# --- 部品ごとの剛体変換 --------------------------------------------------------------
# 戻り値の kind: "rot_x" = 点 (y0, z0) を通る X 軸まわりに angle_deg 回す。"trans_z" = z に dz 動く。
def part_transforms(theta_deg, cams=None, theta_flat=None):
    """部品 id（params.PART_IDS）-> 変換の辞書。motion.json を作る担当向け。
    - horn_coupler と sg92r_horn: サーボ軸（Y=0, Z=Zs）まわりに servo_delta 度。sg92r（本体）は動かない
    - shaft_j（-X の端の部品）, gear_j（+X の歯車の部品）, cam_i_j（j=行）: カム軸 j（Y=axis_y(j), Z=Zc）まわりに axis_angle 度。数珠つなぎで 1 つの剛体として回る
    - pixel_i_j: z に高さ dz（m）。cams が None なら省く
    歯車の噛み合いの位相は params の CHAIN/SECTOR の歯の位相で決まる（kinematics は角だけを返す）。
    """
    out = {}
    rec = {"kind": "rot_x", "y0": 0.0, "z0": P.SERVO_AXIS_Z, "angle_deg": servo_delta(theta_deg, theta_flat)}
    out["horn_coupler"] = dict(rec)
    out["sg92r_horn"] = dict(rec)
    for j in range(P.N):
        ax = {"kind": "rot_x", "y0": axis_y(j), "z0": P.CAM_AXIS_Z, "angle_deg": axis_angle(theta_deg, j, theta_flat)}
        out[f"shaft_{j}"] = dict(ax)
        out[f"gear_{j}"] = dict(ax)
        for i in range(P.N):
            out[f"cam_{i}_{j}"] = dict(ax)
    if cams is not None:
        hh = pixel_heights(cams, theta_deg, theta_flat)
        for j in range(P.N):
            for i in range(P.N):
                out[f"pixel_{i}_{j}"] = {"kind": "trans_z", "dz": hh[j][i]}
    return out


def servo_theta_for_table(k, theta_flat=None):
    """表 k を表示するサーボ角（度）。較正で THETA_FLAT がずれたら表全体を同じだけずらす"""
    off = 0.0 if theta_flat is None else theta_flat - P.THETA_FLAT
    return P.TABLE_THETA[k] + off


# --- 数珠つなぎのカム軸（params の STUB_AF / JOINT_ENGAGE_*）---------------------------------------
def cam_x_range(i, j):
    """カム板の X の範囲（m）"""
    x = cam_x(i, j)
    return (x - P.CAM_T / 2, x + P.CAM_T / 2)


def next_face_x(i, j):
    """カム i の次の部品（+X 側）の -X 面の X（m）。カム 4 の次は歯車の部品、それ以外は同じ行の次のカム"""
    return P.GEAR_X0 if i == P.N - 1 else cam_x_range(i + 1, j)[0]


def stub_length(i, j):
    """カム i の雄スタブの長さ（m）: カム板の +X 面から、次の部品の穴の底まで = 面どうしの間 + 穴の深さ"""
    depth = P.JOINT_ENGAGE_GEAR if i == P.N - 1 else P.JOINT_ENGAGE_CAM
    return next_face_x(i, j) - cam_x_range(i, j)[1] + depth


def end_part_hex_x(j):
    """端の部品 shaft_j の六角部の X の範囲（m）: -X の肩（-SHAFT_HALF_L）から、最も -X のカムの穴の底まで。治具はこの -X 寄りに掛かる"""
    x0 = cam_x_range(0, j)[0]
    return (-P.SHAFT_HALF_L, x0 + P.JOINT_ENGAGE_CAM)
