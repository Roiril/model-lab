"""face_extract — 顔シート画像から各表情の黒領域を輪郭抽出してベクトル化。

face-sheet.png（2行x7列の表情シート）から指定セルの黒い部分（目・口）を
高解像で輪郭抽出し、ハイライト(白)は穴として保持。彫刻用の閉ループ群を返す。

座標系: 画像と同じ y 下向き（SVG 系に一致）。返り値は「コンテンツ重心を原点・
最大辺を 1.0 に正規化」した閉ループ群。build 側で目標サイズに拡大配置する。
"""
import os
import cv2
import numpy as np

_DIR = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(_DIR, "face-sheet.png")

# グリッド（解析で確定）
BG_BGR = np.array([73, 207, 237])      # 黄背景
X0, X1 = 28, 786                       # コンテンツ横範囲
NCOL = 7
ROW_BANDS = [(48, 120), (138, 205)]    # 上段 / 下段 の y 帯
UPSCALE = 8                            # 輪郭平滑用アップスケール
BLACK_TH = 95                          # これ未満を黒(彫る)とみなす
NONYELLOW_TH = 60                      # 黄背景からこの距離超で「描画(白or黒)」
APPROX_EPS = 1.1                       # approxPolyDP（アップスケール後px）


def _chaikin(poly, iters=2):
    """Chaikin 角丸め平滑（閉ループ）。"""
    p = np.asarray(poly, float)
    for _ in range(iters):
        n = len(p)
        out = np.empty((n * 2, 2))
        for i in range(n):
            a = p[i]
            b = p[(i + 1) % n]
            out[2 * i] = a * 0.75 + b * 0.25
            out[2 * i + 1] = a * 0.25 + b * 0.75
        p = out
    return p


def _smooth(c):
    ap = cv2.approxPolyDP(c, APPROX_EPS, True).reshape(-1, 2).astype(float)
    return _chaikin(ap, 2) if len(ap) >= 3 else None


def _cell_masks(row, col):
    img = cv2.imread(SHEET)
    if img is None:
        raise FileNotFoundError(SHEET)
    cw = (X1 - X0) / NCOL
    y0, y1 = ROW_BANDS[row]
    cx0 = int(round(X0 + (col - 1) * cw))
    cx1 = int(round(X0 + col * cw))
    cell = img[y0:y1, cx0:cx1]
    big = cv2.resize(cell, None, fx=UPSCALE, fy=UPSCALE, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
    black = (gray < BLACK_TH).astype(np.uint8) * 255
    dist = np.linalg.norm(big.astype(int) - BG_BGR[None, None, :], axis=2)
    nonyellow = (dist > NONYELLOW_TH).astype(np.uint8) * 255
    white = (big[:, :, 0] > 150).astype(np.uint8) * 255  # 白目(B高)。黄(B低)・黒を除外
    k = np.ones((3, 3), np.uint8)
    for m in (black, nonyellow, white):
        cv2.morphologyEx(m, cv2.MORPH_OPEN, k, dst=m)
        cv2.morphologyEx(m, cv2.MORPH_CLOSE, k, dst=m)
    return black, nonyellow, white


def extract_face(row, col, min_area_frac=0.0012):
    """row(0=上,1=下), col(1始まり) の顔を抽出。

    戻り: (fills, lines)  いずれも非黄色領域の bbox で共通正規化（原点中心・最大辺1）。
      fills = [[outer, hole, ...], ...]  黒シェイプ（彫りベタ, evenodd）
      lines = [loop, ...]                非黄色領域の外周＝白目と黄色の境目（黒線で描く）
    """
    black, nonyellow, white = _cell_masks(row, col)
    H, W = black.shape
    area_all = H * W
    amin = area_all * min_area_frac

    # --- 黒ベタ（穴つき） ---
    cnts, hier = cv2.findContours(black, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    fills = []
    if cnts:
        hier = hier[0]
        for i, c in enumerate(cnts):
            if hier[i][3] != -1 or cv2.contourArea(c) < amin:
                continue
            loops = [c]
            ch = hier[i][2]
            while ch != -1:
                if cv2.contourArea(cnts[ch]) >= amin * 0.5:
                    loops.append(cnts[ch])
                ch = hier[ch][0]
            sm = [s for s in (_smooth(l) for l in loops) if s is not None]
            if sm:
                fills.append(sm)

    # --- 白目↔黄色の境目 → 黒線（白画素を含む眼ブロックの外周のみ。口は除外）---
    ncnts, _ = cv2.findContours(nonyellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    white_bin = white > 0
    lines = []
    ny_pts = []
    for c in ncnts:
        if cv2.contourArea(c) < amin:
            continue
        ny_pts.append(c.reshape(-1, 2).astype(float))
        blob = np.zeros((H, W), np.uint8)
        cv2.drawContours(blob, [c], -1, 1, -1)
        wfrac = (white_bin & (blob > 0)).sum() / max(int(blob.sum()), 1)
        if wfrac < 0.06:      # 白目を含まない（＝口など）はスキップ
            continue
        sm = _smooth(c)
        if sm is not None:
            lines.append(sm)

    # --- 共通正規化（全眼ブロック=非黄色領域の bbox で。白フィルタに依らず安定）---
    npts = np.vstack(ny_pts) if ny_pts else np.vstack([lp for f in fills for lp in f])
    mn, mx = npts.min(axis=0), npts.max(axis=0)
    ctr = (mn + mx) / 2
    span = (mx - mn).max()
    fills_n = [[(lp - ctr) / span for lp in f] for f in fills]
    lines_n = [(lp - ctr) / span for lp in lines]
    return fills_n, lines_n
