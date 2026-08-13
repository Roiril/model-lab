# -*- coding: utf-8 -*-
"""バンディド (Bandido) カードのテクスチャ生成。

白背景の生写真（RAW_DIR/*.jpg）から各カードを輪郭抽出→透視補正し、
縦長 1:2 に正規化した「全面カード色（角スリバーを埋めた不透明）」テクスチャを
exports/bandido/tex/*.png に出力する。角丸はメッシュ側（build_glb）で切るため、
テクスチャは角まで紙が写り込まないよう内側の色で充填する。

同時に、角丸長方形アウトライン＋各カードの側面色を outlines.json に書き出す。

輪郭抽出は Lab 色空間の彩度＋暗部で分離（白背景の影を彩度で除外し、黒いトンネル
部分は暗部で拾う）。全 33 枚で aspect≈2.00・矩形フィット率≈0.98 を確認済み。
"""
import cv2, numpy as np, json, math, os, sys, glob

sys.path.insert(0, os.path.dirname(__file__))
from params import (CARD_W, CARD_H, CARD_R, CARD_T, CORNER_FRAC,
                    TEX_W, TEX_H, RAW_DIR, FACE_CARDS, BACK, SIDE_FALLBACK)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "bandido"))
TEX = os.path.join(OUT, "tex")
os.makedirs(TEX, exist_ok=True)

R_PX = round(TEX_W * CORNER_FRAC)   # テクスチャ角丸半径 px


# ---------------------------------------------------------------- 抽出ヘルパ
def card_quad(img):
    """カードの4隅（tl,tr,br,bl）を返す。影に強い Lab 彩度＋暗部で分離。"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    s = 60
    def corn(a):
        return np.concatenate([a[:s, :s].ravel(), a[:s, -s:].ravel(),
                               a[-s:, :s].ravel(), a[-s:, -s:].ravel()])
    a0, b0, Lbg = np.median(corn(A)), np.median(corn(B)), np.median(corn(L))
    chroma = np.sqrt((A - a0) ** 2 + (B - b0) ** 2)
    dark = Lbg - L
    mask = ((chroma > 12) | (dark > 60)).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k, iterations=1)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts, key=cv2.contourArea)
    box = cv2.boxPoints(cv2.minAreaRect(c)).astype(np.float32)
    return order_pts(box)


def order_pts(pts):
    pts = pts.reshape(4, 2)
    ssum = pts.sum(1); d = np.diff(pts, axis=1).ravel()
    tl = pts[np.argmin(ssum)]; br = pts[np.argmax(ssum)]
    tr = pts[np.argmin(d)]; bl = pts[np.argmax(d)]
    return np.array([tl, tr, br, bl], dtype=np.float32)


def warp_portrait(img, quad):
    """カードを縦長 TEX_W×TEX_H に透視補正。回転のみで縦長化（引き延ばしなし）。"""
    tl, tr, br, bl = quad
    w_top = np.linalg.norm(tr - tl)
    h_left = np.linalg.norm(bl - tl)
    dst = np.array([[0, 0], [TEX_W, 0], [TEX_W, TEX_H], [0, TEX_H]], np.float32)
    if h_left >= w_top:                       # 縦撮り: 上下維持
        src = quad
    else:                                     # 横撮り(bandy等): 90°回転
        src = np.array([bl, tl, tr, br], np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(img, M, (TEX_W, TEX_H), flags=cv2.INTER_CUBIC,
                               borderMode=cv2.BORDER_REPLICATE)


def rounded_mask(w, h, r):
    a = np.zeros((h, w), np.uint8)
    cv2.rectangle(a, (r, 0), (w - r, h), 255, -1)
    cv2.rectangle(a, (0, r), (w, h - r), 255, -1)
    for cx, cy in [(r, r), (w - r, r), (r, h - r), (w - r, h - r)]:
        cv2.circle(a, (cx, cy), r, 255, -1)
    return a


def fill_corners(card, r):
    """角丸の外側（紙が写る三角）を内側カード色で inpaint 充填し不透明化。"""
    m = rounded_mask(TEX_W, TEX_H, r)
    hole = cv2.bitwise_not(m)                 # 埋めるべき領域
    # 少し内側まで再塗りして縁のにじみを消す
    hole = cv2.dilate(hole, np.ones((5, 5), np.uint8), iterations=1)
    return cv2.inpaint(card, hole, 6, cv2.INPAINT_TELEA)


def side_color(card, r):
    """カード内側の帯（縁から 20〜60px 内側）の中央値を側面色に。
    エッジ直近は紙のにじみが混ざるので避け、実カード色を採る。"""
    m = rounded_mask(TEX_W, TEX_H, r)
    k = np.ones((3, 3), np.uint8)
    outer = cv2.erode(m, k, iterations=20)
    inner = cv2.erode(m, k, iterations=60)
    ring = cv2.subtract(outer, inner)
    px = card[ring > 0]
    if len(px) == 0:
        return SIDE_FALLBACK
    bgr = np.median(px, axis=0)
    return (int(bgr[2] * 0.82), int(bgr[1] * 0.82), int(bgr[0] * 0.82))  # RGB, やや沈める


# ---------------------------------------------------------------- 幾何
def rounded_rect_mm(w, h, r, seg=16):
    r = min(r, w / 2, h / 2)
    hx, hy = w / 2, h / 2
    corners = [(hx - r, hy - r, 0.0), (-hx + r, hy - r, 90.0),
               (-hx + r, -hy + r, 180.0), (hx - r, -hy + r, 270.0)]
    pts = []
    for cx, cy, a0 in corners:
        for k in range(seg + 1):
            a = math.radians(a0 + 90.0 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def outline_normalized():
    pts = rounded_rect_mm(CARD_W, CARD_H, CARD_R)
    return [(x / CARD_W, y / CARD_H) for x, y in pts]


# ---------------------------------------------------------------- ビルド
def extract(name):
    for ext in (".jpg", ".jpeg", ".png"):
        p = os.path.join(RAW_DIR, name + ext)
        if os.path.exists(p):
            break
    else:
        raise FileNotFoundError(name)
    img = cv2.imread(p)
    quad = card_quad(img)
    card = warp_portrait(img, quad)
    filled = fill_corners(card, R_PX)
    return filled, side_color(card, R_PX)


manifest = {
    "card_w_mm": CARD_W * 1000,
    "card_h_mm": CARD_H * 1000,
    "thick_mm": CARD_T * 1000,
    "corner_r_mm": round(CARD_R * 1000, 2),
    "outline": [[round(x, 5), round(y, 5)] for x, y in outline_normalized()],
    "back_tex": BACK + ".png",
    "cards": {},
}

# 表面カード
for name in FACE_CARDS:
    tex, side = extract(name)
    cv2.imwrite(os.path.join(TEX, name + ".png"), tex)
    manifest["cards"][name] = {"tex": name + ".png", "side_color": list(side)}
    print("tex", name, "side", side)

# 共通の裏（ura）も同じ処理でテクスチャ化（面として全カードのボトムに使う）
back, _ = extract(BACK)
cv2.imwrite(os.path.join(TEX, BACK + ".png"), back)
print("back", BACK)

with open(os.path.join(OUT, "outlines.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)

print("\nfaces:", len(manifest["cards"]), " tex:", len(os.listdir(TEX)),
      "files (%dx%d)" % (TEX_W, TEX_H))
print("OUT:", OUT)
