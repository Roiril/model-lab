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


def extract_face(row, col, min_area_frac=0.0012):
    """row(0=上,1=下), col(1始まり) の顔の黒領域を抽出。

    戻り: paths = [ [outer_loop, hole_loop, ...], ... ]  正規化座標(原点中心・最大辺1)。
    """
    img = cv2.imread(SHEET)
    if img is None:
        raise FileNotFoundError(SHEET)
    cw = (X1 - X0) / NCOL
    y0, y1 = ROW_BANDS[row]
    cx0 = int(round(X0 + (col - 1) * cw))
    cx1 = int(round(X0 + col * cw))
    cell = img[y0:y1, cx0:cx1]

    # アップスケールして滑らかに
    big = cv2.resize(cell, None, fx=UPSCALE, fy=UPSCALE, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
    black = (gray < BLACK_TH).astype(np.uint8) * 255
    # 微小ノイズ除去
    k = np.ones((3, 3), np.uint8)
    black = cv2.morphologyEx(black, cv2.MORPH_OPEN, k)
    black = cv2.morphologyEx(black, cv2.MORPH_CLOSE, k)

    cnts, hier = cv2.findContours(black, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return []
    H, W = black.shape
    area_all = H * W
    hier = hier[0]

    # 外輪郭(level0, parent==-1) ごとに、その子(穴)を集める
    paths = []
    for i, c in enumerate(cnts):
        if hier[i][3] != -1:
            continue  # 穴は親側で処理
        if cv2.contourArea(c) < area_all * min_area_frac:
            continue
        loops = [c]
        ch = hier[i][2]  # first child
        while ch != -1:
            if cv2.contourArea(cnts[ch]) >= area_all * min_area_frac * 0.5:
                loops.append(cnts[ch])
            ch = hier[ch][0]  # next sibling
        paths.append(loops)

    if not paths:
        return []

    # 平滑＋簡約 → float 点列
    proc = []
    for loops in paths:
        pls = []
        for c in loops:
            ap = cv2.approxPolyDP(c, APPROX_EPS, True).reshape(-1, 2).astype(float)
            if len(ap) >= 3:
                pls.append(_chaikin(ap, 2))
        if pls:
            proc.append(pls)

    # 正規化（全 path の bbox 重心を原点、最大辺=1）
    allpts = np.vstack([lp for pls in proc for lp in pls])
    mn = allpts.min(axis=0)
    mx = allpts.max(axis=0)
    ctr = (mn + mx) / 2
    span = (mx - mn).max()
    norm = [[(lp - ctr) / span for lp in pls] for pls in proc]
    return norm  # list of [np.array(N,2) ...]


def content_aspect(row, col):
    """抽出コンテンツの横/縦 比（配置の縦横調整用）。"""
    norm = extract_face(row, col)
    allpts = np.vstack([lp for pls in norm for lp in pls])
    w = allpts[:, 0].max() - allpts[:, 0].min()
    h = allpts[:, 1].max() - allpts[:, 1].min()
    return w, h
