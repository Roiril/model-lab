"""facet-bot を SVG に展開 → exports/laser/facet-bot.svg。

パーツ: 平らなファセット(前面1＋背面M枚) と D字ポリゴンのフタ2枚。
各ファセットは上下端タブでフタのスロットへ差し込み。曲げゼロ＝アクリル可。
実行: python models/facet-bot/build.py
"""
import sys, os, math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../laser-bot"))  # face_extract
sys.path.insert(0, os.path.dirname(__file__))

import laser_core as lc
import face_extract as fe
from params import (D_OUT, T, H, WF, M_ARC, TAB_W, TAB_PER_22MM,
                    FACE, FACE_W, RIM, GAP)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "exports", "laser")
os.makedirs(OUT_DIR, exist_ok=True)

RC = (D_OUT - T) / 2.0      # ファセット中心線が乗る円の半径


def section_vertices():
    """断面ポリゴンの頂点列（中心 O=原点, 前面＝+y）。
    前面フラット弦(WF)＋背面アーチ M_ARC 分割。頂点は半径 RC の円上。"""
    theta = 2 * math.asin(WF / (2 * RC))         # 前面フラットが張る角
    a_B = math.pi / 2 - theta / 2                 # 前面右端 B
    a_A = math.pi / 2 + theta / 2                 # 前面左端 A
    arc_end = a_A - 2 * math.pi                    # B から時計回りに A まで
    verts = []
    for i in range(M_ARC + 1):
        ang = a_B + (arc_end - a_B) * i / M_ARC
        verts.append((RC * math.cos(ang), RC * math.sin(ang)))
    # verts[0]=B ... verts[M_ARC]=A。facet辺 = arc(M_ARC本) + 前面(A->B)
    return verts


def facets(verts):
    """各ファセット辺 (p0, p1, width, ntab, is_front) のリスト。"""
    out = []
    n = len(verts)
    for i in range(n - 1):        # アーチ辺
        p0, p1 = verts[i], verts[i + 1]
        w = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        out.append((p0, p1, w, max(1, round(w / TAB_PER_22MM)), False))
    # 前面フラット A(verts[-1]) -> B(verts[0])
    p0, p1 = verts[-1], verts[0]
    w = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    out.append((p0, p1, w, max(1, round(w / TAB_PER_22MM)), True))
    return out


def tab_fracs(ntab):
    return [(j + 0.5) / ntab for j in range(ntab)]


def facet_panel(w, ntab):
    """幅 w x 高さ H の平パネル外周（上下端に ntab タブ）。ローカル原点左上。"""
    tw, th = TAB_W, T
    xs = [f * w for f in tab_fracs(ntab)]
    pts = [(0.0, 0.0)]
    for x in xs:
        pts += [(x - tw / 2, 0.0), (x - tw / 2, -th), (x + tw / 2, -th), (x + tw / 2, 0.0)]
    pts += [(w, 0.0), (w, H)]
    for x in reversed(xs):
        pts += [(x + tw / 2, H), (x + tw / 2, H + th), (x - tw / 2, H + th), (x - tw / 2, H)]
    pts += [(0.0, H)]
    return pts


def _line_int(a0, a1, b0, b1):
    x1, y1 = a0; x2, y2 = a1; x3, y3 = b0; x4, y4 = b1
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(d) < 1e-9:
        return b0
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def offset_polygon(verts, d):
    """凸ポリゴンを外側へ d オフセット（各辺を外向き平行移動→隣辺と交点）。"""
    n = len(verts)
    cx = sum(p[0] for p in verts) / n
    cy = sum(p[1] for p in verts) / n
    lines = []
    for i in range(n):
        p0, p1 = verts[i], verts[(i + 1) % n]
        ex, ey = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(ex, ey) or 1e-9
        nx, ny = ey / L, -ex / L
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        if (mx - cx) * nx + (my - cy) * ny < 0:
            nx, ny = -nx, -ny
        lines.append(((p0[0] + nx * d, p0[1] + ny * d), (p1[0] + nx * d, p1[1] + ny * d)))
    out = []
    for i in range(n):
        out.append(_line_int(lines[i - 1][0], lines[i - 1][1], lines[i][0], lines[i][1]))
    return out


def edge_slots(p0, p1, ntab):
    """ファセット辺(p0->p1)上に ntab スロット矩形（フタ穴）を返す。"""
    ex, ey = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(ex, ey) or 1e-9
    tx, ty = ex / L, ey / L
    nx, ny = ty, -tx                       # 法線（向きは後で外向きに）
    # 外向き（原点から遠ざかる側）に統一
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    if mx * nx + my * ny < 0:
        nx, ny = -nx, -ny
    sw, sh = (TAB_W + lc.KERF) / 2, (T + lc.KERF) / 2
    loops = []
    for f in tab_fracs(ntab):
        px, py = p0[0] + ex * f, p0[1] + ey * f
        corners = [(-sw, -sh), (sw, -sh), (sw, sh), (-sw, sh)]
        loops.append([(px + a * tx + b * nx, py + a * ty + b * ny) for a, b in corners])
    return loops


def face_on_panel(w):
    """前面パネル(w x H)中央に顔（fills, lines）を配置。"""
    fills, lines = fe.extract_face(*FACE)
    allpts = np.vstack(lines) if lines else np.vstack([lp for f in fills for lp in f])
    cw = allpts[:, 0].max() - allpts[:, 0].min()
    ch = allpts[:, 1].max() - allpts[:, 1].min()
    scale = min(FACE_W / cw, (H - 16) / ch)
    cx, cy = w / 2.0, H / 2.0

    def place(lp):
        return [(cx + x * scale, cy + y * scale) for x, y in lp]

    return [[place(lp) for lp in f] for f in fills], [place(lp) for lp in lines]


def compose():
    cut_loops, eng_loops, eng_lines = [], [], []
    verts = section_vertices()
    fac = facets(verts)

    # --- ファセットパネルを1列に並べる ---
    x_cursor = 0.0
    row_y = 0.0
    for idx, (p0, p1, w, ntab, is_front) in enumerate(fac):
        cut_loops.append((facet_panel(w, ntab), x_cursor, row_y + T))
        if is_front:
            fills, lines = face_on_panel(w)
            for f in fills:
                eng_loops.append((f, x_cursor, row_y + T))
            if lines:
                eng_lines.append((lines, x_cursor, row_y + T))
        x_cursor += w + GAP

    # --- D字ポリゴンのフタ x2（パネル群の下に GAP を空けて配置）---
    rim = offset_polygon(verts, T / 2 + RIM)
    dminx = min(p[0] for p in rim); dmaxx = max(p[0] for p in rim)
    dminy = min(p[1] for p in rim); dmaxy = max(p[1] for p in rim)
    panel_ymax = row_y + T + H + T           # パネル下端（タブ含む）
    cap_y = panel_ymax + GAP - dminy         # フタ上端 = panel_ymax + GAP
    for k in range(2):
        ccx = -dminx + k * ((dmaxx - dminx) + GAP)
        cut_loops.append((rim, ccx, cap_y))
        for (p0, p1, w, ntab, is_front) in fac:
            for slot in edge_slots(p0, p1, ntab):
                cut_loops.append((slot, ccx, cap_y))

    return cut_loops, eng_loops, eng_lines, fac, rim


def main():
    cut_loops, eng_loops, eng_lines, fac, rim = compose()
    svg = os.path.join(OUT_DIR, "facet-bot.svg")
    sheet = lc.write_svg(svg, cut_loops, eng_loops, eng_lines)
    nfac = len(fac)
    ntabs = sum(f[3] for f in fac)
    print(f"facet-bot  D={D_OUT} H={H}  t={T}mm  (アクリル可・曲げゼロ)")
    print(f"  ファセット {nfac}枚（前面1＋背面{M_ARC}）  総タブ/スロット {ntabs}")
    print(f"  前面フラット幅 {WF}  各背面ファセット幅 ~{fac[0][2]:.1f}mm")
    print(f"  部品数 = {nfac} + フタ2 = {nfac + 2}")
    print(f"  sheet {sheet[0]:.1f} x {sheet[1]:.1f} mm  (bed {lc.BED_W} x {lc.BED_H})")
    fit = "OK" if sheet[0] <= lc.BED_W and sheet[1] <= lc.BED_H else "OVER BED!"
    print(f"  fit {fit}")
    print(f"  wrote {svg}")


if __name__ == "__main__":
    main()
