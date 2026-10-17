"""camshaft_j（胴 Ø10 + 板カム 5 枚の一体）の隣の行どうしの隙間。bpy 非依存。単位 mm・度。

各カムの -X 側（下側）は 45° の円錐（すそ）で胴まで絞る: 半径 = max(胴の半径, カムの輪郭の半径(θ) - 板の下面からの距離 t)。
隣り合う行の camshaft（Y が 17 離れ、角度は互いに逆向き = 歯車 1:1）を、サーボ 10..170° の全範囲・全 X で動かし、2 つの断面の最短距離を測る。
軸方向の遊び（片側 AXIAL_DRIFT、合計 2 x AXIAL_DRIFT）は、隣の行の相対の X のずれ（-0.8, 0, +0.8）として入れる。
負の値 = 食い込み（深さ）。
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P
import kinematics as K

NT = 720
TH = np.arange(NT) * 360.0 / NT
TR = np.radians(TH)
MM = 1000.0
BODY_R = P.CAMSHAFT_BODY_D * MM / 2
CAM_T = P.CAM_T * MM
PITCH = P.PITCH * MM


def raycast(V):
    """多角形（原点を含む星形）の、TH での半径"""
    V = np.asarray(V, float)
    a = V
    b = np.roll(V, -1, axis=0)
    e = b - a
    d = np.stack([np.cos(TR), np.sin(TR)], 1)
    den = d[:, 0:1] * e[None, :, 1] - d[:, 1:2] * e[None, :, 0]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (a[None, :, 0] * e[None, :, 1] - a[None, :, 1] * e[None, :, 0]) / den
        s = (a[None, :, 0] * d[:, 1:2] - a[None, :, 1] * d[:, 0:1]) / den
    ok = (np.abs(den) > 1e-12) & (s >= -1e-9) & (s <= 1 + 1e-9) & (t > 0)
    t = np.where(ok, t, -1.0)
    return t.max(axis=1)


class Shaft:
    """camshaft_j の半径関数 rho[X, θ]（軸の枠、φ=0）。X は camshaft の -JOURNAL_END..+スタブの先"""

    def __init__(self, j, cams_row, dx=0.25, x_shift=0.0, skirt=True):
        self.j = j
        xlo, xhi = (v * MM for v in K.camshaft_x_range())
        self.X = np.arange(xlo, xhi + 1e-9, dx)
        n = len(self.X)
        rho = np.full((n, NT), BODY_R)
        self.cams = []
        for i in range(P.N):
            x0, x1 = (v * MM + x_shift for v in K.cam_x_range(i, j))
            R = raycast(cams_row[i]["vertices"])
            self.cams.append((i, x0, x1, float(R.max())))
        # 板と円錐は shift 前の X で作る（shift は呼び出し側が、相手との相対位置として与える）
        for i, x0, x1, _ in self.cams:
            R = raycast(cams_row[i]["vertices"])
            m = (self.X >= x0 - 1e-9) & (self.X <= x1 + 1e-9)
            rho[m] = np.maximum(rho[m], R[None, :])
            if skirt:
                t = x0 - self.X
                ms = (t > 0) & (t <= R.max() - BODY_R + 1e-9)
                if ms.any():
                    rho[ms] = np.maximum(rho[ms], np.maximum(R[None, :] - t[ms][:, None], BODY_R))
        self.rho = rho
        self.rmax = rho.max(axis=1)


def _shift_idx(phi_deg):
    return int(round(phi_deg * NT / 360.0))


def _rolled(rho_row, phis):
    sh = np.array([_shift_idx(p) for p in phis])
    idx = (np.arange(NT)[None, :] - sh[:, None]) % NT
    return rho_row[idx]


def pair_clearance(A, B, phis, clearance_floor=0.6, coarse=6):
    """A（Y=0）と B（Y=PITCH）の最短距離（mm）の、全 X・全 φ での最小。B の角度は -φ（歯車 1:1 の逆回り）。
    A と B の X は共通の座標（B の X のずれは Shaft の x_shift で既に入っている）。
    返り値 (最小隙間, X, φ)。clearance_floor + 0.75 より遠い X は粗い境界で省く"""
    X = A.X
    # B は x_shift だけずれているので、B の rho を A の X 格子へ補間
    cand = np.where(A.rmax + B.rmax_on(X) + clearance_floor > PITCH)[0]
    cosw = np.cos(TR)
    sinw = np.sin(TR)
    win = np.where(np.abs(((TH + 180) % 360) - 180) <= 66)[0]
    winB = np.where(np.abs((TH % 360) - 180) <= 66)[0]
    wc = win[::coarse]
    wbc = winB[::coarse]
    best = (1e9, None, None)
    for xi in cand:
        RA = _rolled(A.rho[xi], phis)
        RB = _rolled(B.rho_on(X[xi]), [-p for p in phis])
        ax = RA[:, wc] * cosw[wc]
        ay = RA[:, wc] * sinw[wc]
        bx = PITCH + RB[:, wbc] * cosw[wbc]
        by = RB[:, wbc] * sinw[wbc]
        dd = np.hypot(ax[:, :, None] - bx[:, None, :], ay[:, :, None] - by[:, None, :]).min(axis=(1, 2))
        todo = np.where(dd < clearance_floor + 0.75)[0]
        worst = 1e9
        wphi = None
        for k in todo:
            ra, rb = RA[k], RB[k]
            ax_ = ra[win] * cosw[win]
            ay_ = ra[win] * sinw[win]
            bx_ = PITCH + rb[winB] * cosw[winB]
            by_ = rb[winB] * sinw[winB]
            v = np.hypot(ax_[:, None] - bx_[None, :], ay_[:, None] - by_[None, :]).min()
            pa = np.hypot(ax_ - PITCH, ay_)
            ang = np.degrees(np.arctan2(ay_, ax_ - PITCH)) % 360
            ia = (np.round(ang * NT / 360).astype(int)) % NT
            inB = pa < rb[ia] - 1e-9
            pb = np.hypot(bx_, by_)
            ang2 = np.degrees(np.arctan2(by_, bx_)) % 360
            ib = (np.round(ang2 * NT / 360).astype(int)) % NT
            inA = pb < ra[ib] - 1e-9
            if inB.any() or inA.any():
                depth = 0.0
                if inB.any():
                    depth = max(depth, float((rb[ia] - pa)[inB].max()))
                if inA.any():
                    depth = max(depth, float((ra[ib] - pb)[inA].max()))
                v = -depth
            if v < worst:
                worst, wphi = v, phis[k]
        if worst == 1e9:
            worst = float(dd.min()) - 0.5       # 粗い境界からの下限（> clearance_floor）
            wphi = phis[int(dd.argmin())]
        if worst < best[0]:
            best = (worst, float(X[xi]), wphi)
    return best


class _Rel:
    """B を A の X 格子で読むための、x_shift 付きの薄い包み"""

    def __init__(self, shaft, dx_shift):
        self.s = shaft
        self.d = dx_shift

    def rho_on(self, x):
        k = int(round((x - self.d - self.s.X[0]) / (self.s.X[1] - self.s.X[0])))
        if 0 <= k < len(self.s.X):
            return self.s.rho[k]
        return np.full(NT, BODY_R)

    def rmax_on(self, X):
        k = np.round((X - self.d - self.s.X[0]) / (self.s.X[1] - self.s.X[0])).astype(int)
        ok = (k >= 0) & (k < len(self.s.X))
        out = np.full(len(X), BODY_R)
        out[ok] = self.s.rmax[k[ok]]
        return out


def adjacent_rows_clearance(cams, rel_shifts=(0.0,), phis=None, rows=None):
    """隣の行の組 (j, j+1) ごとの最小隙間。rel_shifts = B の A に対する X のずれ（mm）の候補。
    返り値 {j: (隙間, X, φ, ずれ)}（ずれの候補のうち最悪）"""
    if phis is None:
        half = K.table_theta_to_phi_range()
        phis = [float(p) for p in np.arange(-round(half), round(half) + 1e-9, 2.0)]
    out = {}
    for j in (range(P.N - 1) if rows is None else rows):
        A = Shaft(j, cams[j])
        res = (1e9, None, None, None)
        for d in rel_shifts:
            B = _Rel(Shaft(j + 1, cams[j + 1]), d)
            r = pair_clearance(A, B, phis)
            if r[0] < res[0]:
                res = (r[0], r[1], r[2], d)
        out[j] = res
    return out
