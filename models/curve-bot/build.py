"""curve-bot を SVG に展開 → exports/laser/curve-bot.svg。

パーツ: 帯(band, ヒンジ＋タブ＋顔) と 丸フタ(cap) x2。
実行: python models/curve-bot/build.py
"""
import sys, os, math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../laser-bot"))  # face_extract
sys.path.insert(0, os.path.dirname(__file__))  # 自分の params を最優先

import laser_core as lc
import face_extract as fe
from params import (D_OUT, T, H, N_TAB, TAB_W, HINGE_COL, HINGE_SEG, HINGE_LIG,
                    HINGE_VMARGIN, END_MARGIN, FACE, FACE_W, FACE_WINDOW_HALF, GAP)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "exports", "laser")
os.makedirs(OUT_DIR, exist_ok=True)

R_C = (D_OUT - T) / 2.0          # 帯中心線の半径
C = 2 * math.pi * R_C            # 円周＝帯の幅
CAP_R = R_C + T / 2.0 + 0.5      # フタ半径（0.5mm リム）
R_RING = R_C                     # スロット中心半径


def band_outline():
    """帯の外周（上下端に N_TAB のタブ）。閉ループ点列。"""
    tw, th = TAB_W, T
    us = [(i + 0.5) * C / N_TAB for i in range(N_TAB)]
    pts = [(0.0, 0.0)]
    # 上端 v=0 左→右, タブは上(v<0)へ
    for u in us:
        pts += [(u - tw / 2, 0.0), (u - tw / 2, -th), (u + tw / 2, -th), (u + tw / 2, 0.0)]
    pts += [(C, 0.0), (C, H)]
    # 下端 v=H 右→左, タブは下(v>H)へ
    for u in reversed(us):
        pts += [(u + tw / 2, H), (u + tw / 2, H + th), (u - tw / 2, H + th), (u - tw / 2, H)]
    pts += [(0.0, H)]
    return pts


def face_on_band():
    """顔（fills, lines）を帯の中央 u=C/2, v=H/2 に配置して返す。"""
    fills, lines = fe.extract_face(*FACE)
    allpts = np.vstack(lines) if lines else np.vstack([lp for f in fills for lp in f])
    cw = allpts[:, 0].max() - allpts[:, 0].min()
    ch = allpts[:, 1].max() - allpts[:, 1].min()
    scale = min(FACE_W / cw, (H - 16) / ch)
    cx, cy = C / 2.0, H / 2.0

    def place(lp):
        return [(cx + x * scale, cy + y * scale) for x, y in lp]

    fills_p = [[place(lp) for lp in f] for f in fills]
    lines_p = [place(lp) for lp in lines]
    return fills_p, lines_p


WF = 2 * FACE_WINDOW_HALF   # 前面フラット幅（＝顔窓）


def _solve_D(circ, wf):
    """前面フラット wf + 背面アーチ の D 断面。2R sin(θ/2)=wf, R(2π-θ)=circ-wf を解く。"""
    def f(th):
        return 2 * (circ - wf) / (2 * math.pi - th) * math.sin(th / 2) - wf
    lo, hi = 1e-4, 2 * math.pi - 1e-4
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    th = (lo + hi) / 2
    return (circ - wf) / (2 * math.pi - th), th   # R, θ


def d_outline(circ, wf, seg=240):
    """D 断面の外周点列（座標中心 O=原点, 前面＝+y）。始点＝背面シーム(下)。"""
    R, th = _solve_D(circ, wf)
    half = th / 2

    def apts(p0, p1, n):
        return [(R * math.cos(p0 + (p1 - p0) * i / n),
                 R * math.sin(p0 + (p1 - p0) * i / n)) for i in range(n + 1)]

    seg1 = apts(-math.pi / 2, math.pi / 2 - half, seg // 2)   # 背面下→右→前右端B
    B = seg1[-1]
    A = (R * math.cos(math.pi / 2 + half), R * math.sin(math.pi / 2 + half))
    flat = [(B[0] + (A[0] - B[0]) * i / 24, B[1] + (A[1] - B[1]) * i / 24)
            for i in range(25)]                               # 前面フラット B→A
    seg2 = apts(math.pi / 2 + half, 3 * math.pi / 2, seg // 2)  # 前左端A→左→背面下
    return seg1[:-1] + flat[:-1] + seg2, R, th


def _cum(outline):
    cum = [0.0]
    for i in range(1, len(outline)):
        dx = outline[i][0] - outline[i - 1][0]
        dy = outline[i][1] - outline[i - 1][1]
        cum.append(cum[-1] + math.hypot(dx, dy))
    return cum


CAP_RIM = 2.0   # フタが帯の外面より張り出す量。スロット外縁との橋
                # = CAP_RIM + T/2 - (T+KERF)/2 ≈ 1.95mm を確保（0.8だと0.75mmで割れる）


def _point_tangent(outline, cum, s):
    """中心線 outline 上の弧長 s の点と単位接線を返す。"""
    total = cum[-1]
    s = s % total
    j = 1
    while j < len(cum) and cum[j] < s:
        j += 1
    j = min(j, len(outline) - 1)
    seglen = cum[j] - cum[j - 1] or 1e-9
    f = (s - cum[j - 1]) / seglen
    p0, p1 = outline[j - 1], outline[j]
    px = p0[0] + (p1[0] - p0[0]) * f
    py = p0[1] + (p1[1] - p0[1]) * f
    tl = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1e-9
    return (px, py), ((p1[0] - p0[0]) / tl, (p1[1] - p0[1]) / tl)


def _outward(p, t):
    """接線 t に直交する外向き法線（原点=断面中心から遠ざかる側）。"""
    nx, ny = t[1], -t[0]
    if nx * p[0] + ny * p[1] < 0:    # 内向きなら反転
        nx, ny = -nx, -ny
    return nx, ny


def cap_outline(outline):
    """中心線を T/2+CAP_RIM だけ外側へオフセットしたフタ外周を返す。"""
    off = T / 2 + CAP_RIM
    n = len(outline)
    out = []
    for i in range(n):
        p_prev = outline[i - 1]
        p = outline[i]
        p_next = outline[(i + 1) % n]
        tx = p_next[0] - p_prev[0]
        ty = p_next[1] - p_prev[1]
        tl = math.hypot(tx, ty) or 1e-9
        nx, ny = _outward(p, (tx / tl, ty / tl))
        out.append((p[0] + nx * off, p[1] + ny * off))
    return out


def cap_slots(outline, cum, u_list, tab_w, t):
    """帯中心線上（＝壁の中心）に、輪郭接線向きでスロット矩形を置く。"""
    slots = []
    sw, sh = (tab_w + lc.KERF) / 2, (t + lc.KERF) / 2
    for u in u_list:
        p, tan = _point_tangent(outline, cum, u)
        nx, ny = _outward(p, tan)
        corners = [(-sw, -sh), (sw, -sh), (sw, sh), (-sw, sh)]
        loop = [(p[0] + a * tan[0] + b * nx, p[1] + a * tan[1] + b * ny)
                for a, b in corners]
        slots.append(loop)
    return slots


def compose():
    cut_loops, cut_lines, eng_loops, eng_lines = [], [], [], []

    # --- 帯（左上）---
    bx, by = 0.0, 0.0
    cut_loops.append((band_outline(), bx, by))
    hinge = lc.living_hinge(END_MARGIN, C - END_MARGIN, 0.0, H,
                            col_space=HINGE_COL, seg_len=HINGE_SEG,
                            ligament=HINGE_LIG, margin=HINGE_VMARGIN,
                            exclude=(C / 2 - FACE_WINDOW_HALF, C / 2 + FACE_WINDOW_HALF))
    for s in hinge:
        cut_lines.append((s, bx, by))
    fills, lines = face_on_band()
    for f in fills:
        eng_loops.append((f, bx, by))
    if lines:
        eng_lines.append((lines, bx, by))

    # --- D字フタ x2（帯の下に横並び）---
    # 中心線(=帯の壁センター)の弧長を帯の u と一致させ、同位置にスロット。
    # フタ外周は中心線を T/2+CAP_RIM 外側へオフセット（壁全厚を受けて少し張り出す）。
    u_list = [(i + 0.5) * C / N_TAB for i in range(N_TAB)]
    centerline, R, th = d_outline(C, WF)
    cum = _cum(centerline)
    rim = cap_outline(centerline)
    dmaxx = max(p[0] for p in rim) - min(p[0] for p in rim)
    dmaxy = max(p[1] for p in rim) - min(p[1] for p in rim)
    cap_y = H + T + GAP + dmaxy / 2
    for k in range(2):
        ccx = dmaxx / 2 + k * (dmaxx + GAP)
        cut_loops.append((rim, ccx, cap_y))
        for slot in cap_slots(centerline, cum, u_list, TAB_W, T):
            cut_loops.append((slot, ccx, cap_y))

    return cut_loops, cut_lines, eng_loops, eng_lines


def main():
    cut_loops, cut_lines, eng_loops, eng_lines = compose()
    svg = os.path.join(OUT_DIR, "curve-bot.svg")
    sheet = lc.write_svg(svg, cut_loops, eng_loops, eng_lines, cut_lines=cut_lines)
    print(f"curve-bot  D={D_OUT} H={H}  t={T}mm  (MDF/合板推奨)")
    print(f"  circumference C = {C:.1f}mm  帯 {C:.0f} x {H}")
    print(f"  tabs/slots = {N_TAB}  cap R = {CAP_R:.1f}")
    print(f"  hinge slits = {len(cut_lines)}")
    print(f"  sheet {sheet[0]:.1f} x {sheet[1]:.1f} mm  (bed {lc.BED_W} x {lc.BED_H})")
    fit = "OK" if sheet[0] <= lc.BED_W and sheet[1] <= lc.BED_H else "OVER BED!"
    print(f"  fit {fit}")
    print(f"  wrote {svg}")


if __name__ == "__main__":
    main()
