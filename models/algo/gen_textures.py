# -*- coding: utf-8 -*-
"""アルゴ (algo) カードのテクスチャ生成。

角丸長方形の面を PIL で描画し（地色＋中央に数字、6 は algo ロゴ付き）、
各カードの 2D アウトライン（角丸長方形）を outlines.json に書き出す。
Blender 側 (build_glb.py) がこの JSON を読んで UV 付き薄板メッシュを作り、
テクスチャを貼って GLB を出力する。

座標系: 正規化座標 (nx, ny) は各軸 [-0.5, 0.5]、+y は上。
  - x はカード幅 W、y はカード高さ H でスケール（カードの縦横比を保持）
  - テクスチャ: pixel_x = (nx+0.5)*Wpx,  pixel_y = (0.5-ny)*Hpx（上下反転）
  - メッシュ頂点: (nx*W, ny*H)
  - UV:          u = nx+0.5,  v = 0.5+ny
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from params import (CARD_W, CARD_H, CARD_R, CARD_T, VALUES,
                    WHITE_BODY, WHITE_NUM, BLACK_BODY, BLACK_NUM,
                    WHITE_SIDE, BLACK_SIDE)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "algo"))
TEX = os.path.join(OUT, "tex")
os.makedirs(TEX, exist_ok=True)

# テクスチャ解像度: カードの縦横比に合わせる（高さ基準）。
H_PX = 1200
W_PX = round(H_PX * CARD_W / CARD_H)   # 幅は縦横比で決定
SS = 3                                  # スーパーサンプリング倍率
FONT = os.path.join(HERE, "fonts", "Jost.ttf")  # 幾何学サンセリフ（Futura 系）


def font_at(px, weight=500):
    f = ImageFont.truetype(FONT, int(px))
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


# ---------------------------------------------------------------- 幾何ヘルパ
def rounded_rect_mm(w, h, r, seg=16):
    """幅 w・高さ h・角丸半径 r の角丸長方形を、実寸(mm系, m単位)で
    原点中心・CCW の点列にして返す。"""
    r = min(r, w / 2, h / 2)
    hx, hy = w / 2, h / 2
    # 4 隅の円弧中心（右上・左上・左下・右下）と各弧の開始角
    corners = [
        (hx - r, hy - r, 0.0),        # 右上: 0°→90°
        (-hx + r, hy - r, 90.0),      # 左上: 90°→180°
        (-hx + r, -hy + r, 180.0),    # 左下: 180°→270°
        (hx - r, -hy + r, 270.0),     # 右下: 270°→360°
    ]
    pts = []
    for cx, cy, a0 in corners:
        for k in range(seg + 1):
            a = math.radians(a0 + 90.0 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def outline_normalized():
    """カード角丸長方形を各軸 [-0.5,0.5] に正規化した点列（x は W, y は H で割る）。"""
    pts = rounded_rect_mm(CARD_W, CARD_H, CARD_R)
    return [(x / CARD_W, y / CARD_H) for x, y in pts]


# ---------------------------------------------------------------- 描画ヘルパ
def n2px(nx):
    return (nx + 0.5) * W_PX * SS


def n2py(ny):
    return (0.5 - ny) * H_PX * SS


def new_canvas():
    img = Image.new("RGBA", (W_PX * SS, H_PX * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def fill_card(d, outline, color):
    poly = [(n2px(x), n2py(y)) for x, y in outline]
    d.polygon(poly, fill=color)


def draw_center_text(d, text, color, font, dy=0.0):
    """テキストをキャンバス中央（+dy オフセット, 正規化 y）に配置。"""
    bb = d.textbbox((0, 0), text, font=font)
    w = bb[2] - bb[0]
    h = bb[3] - bb[1]
    cx = W_PX * SS / 2
    cy = H_PX * SS / 2 - dy * H_PX * SS
    ox = cx - w / 2 - bb[0]
    oy = cy - h / 2 - bb[1]
    d.text((ox, oy), text, fill=color, font=font)


def draw_algo_logo(d, color, cy_norm=-0.30):
    """カード下部に小さな "a.lgo" ワードマーク（実物 6 の装飾に倣う簡略版）。"""
    f = font_at(H_PX * SS * 0.075, 600)
    draw_center_text(d, "a.lgo", color, f, dy=cy_norm)


def save(img, name):
    img = img.resize((W_PX, H_PX), Image.LANCZOS)
    img.save(os.path.join(TEX, name + ".png"))


# ---------------------------------------------------------------- マニフェスト
manifest = {
    "card_w_mm": CARD_W * 1000,
    "card_h_mm": CARD_H * 1000,
    "thick_mm": CARD_T * 1000,
    "outline": [[round(x, 5), round(y, 5)] for x, y in outline_normalized()],
    "cards": {},
}


def add_card(name, body, num, side):
    manifest["cards"][name] = {
        "tex": name + ".png",
        "side_color": list(side),
        "body_color": list(body),
    }


def make_card(name, value, body, num, side, with_logo=False):
    outline = outline_normalized()
    img, d = new_canvas()
    fill_card(d, outline, body)
    # 数字（2桁は少し小さめにして横はみ出しを防ぐ）
    frac = 0.46 if value < 10 else 0.40
    f = font_at(H_PX * SS * frac, 500)
    # ロゴを載せる 6 は数字を少し上へ寄せる
    dy = 0.06 if with_logo else 0.0
    draw_center_text(d, str(value), num, f, dy=dy)
    if with_logo:
        draw_algo_logo(d, num, cy_norm=-0.30)
    save(img, name)
    add_card(name, body, num, side)


# 白カード 0〜11 / 黒カード 0〜11（6 のみ algo ロゴ）
for v in VALUES:
    make_card(f"white_{v}", v, WHITE_BODY, WHITE_NUM, WHITE_SIDE, with_logo=(v == 6))
for v in VALUES:
    make_card(f"black_{v}", v, BLACK_BODY, BLACK_NUM, BLACK_SIDE, with_logo=(v == 6))

# ---------------------------------------------------------------- 書き出し
with open(os.path.join(OUT, "outlines.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)

print("textures:", len(os.listdir(TEX)), "files  (%dx%d px)" % (W_PX, H_PX))
print("cards:", len(manifest["cards"]))
print("OUT:", OUT)
