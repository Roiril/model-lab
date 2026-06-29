# -*- coding: utf-8 -*-
"""
海底探検 (Deep Sea Adventure) コンポーネントのテクスチャ生成。
クリーンなベクター調テクスチャを PIL で描画し、各ピースの 2D アウトラインを
outlines.json に書き出す。Blender 側 (build_glb.py) がこの JSON を読んで
UV 付きの薄板メッシュを作り、テクスチャを貼って GLB を出力する。

座標系: 正規化座標 (nx, ny) は [-0.5, 0.5]、+y は上。
  - テクスチャ:  pixel = ((n+0.5) * SIZE),  pixel_y は (0.5 - ny)*SIZE で上下反転
  - メッシュ頂点: (nx*size_mm, ny*size_mm)
  - UV:          u = nx+0.5,  v = 0.5 - ny   (glTF 左上原点に一致)
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "deep-sea"))
TEX = os.path.join(OUT, "tex")
os.makedirs(TEX, exist_ok=True)

SIZE = 1024          # 最終テクスチャ解像度
SS = 3               # スーパーサンプリング倍率（アンチエイリアス用）
FDIR = os.path.join(HERE, "fonts")
F_SERIF = os.path.join(FDIR, "PlayfairDisplay.ttf")   # 宝物の数字（ディドネ調）
F_SANS  = os.path.join(FDIR, "Jost.ttf")              # ボードのラベル

def serif(px, weight=700):
    f = ImageFont.truetype(F_SERIF, int(px))
    try: f.set_variation_by_axes([weight])
    except Exception: pass
    return f

def sans(px, weight=500):
    f = ImageFont.truetype(F_SANS, int(px))
    try: f.set_variation_by_axes([weight])
    except Exception: pass
    return f

# ---------------------------------------------------------------- 幾何ヘルパ
def reg_poly(n, R, rot_deg):
    rot = math.radians(rot_deg)
    return [(R*math.cos(rot+2*math.pi*i/n), R*math.sin(rot+2*math.pi*i/n))
            for i in range(n)]

def _unit(v):
    l = math.hypot(v[0], v[1])
    return (v[0]/l, v[1]/l) if l else (0.0, 0.0)

def round_corners(verts, r, seg=14):
    """多角形 verts の各頂点を半径 r でフィレットして点列を返す。"""
    n = len(verts)
    out = []
    for i in range(n):
        P  = verts[i]
        A  = verts[(i-1) % n]
        B  = verts[(i+1) % n]
        u1 = _unit((A[0]-P[0], A[1]-P[1]))
        u2 = _unit((B[0]-P[0], B[1]-P[1]))
        # 角度
        dot = max(-1.0, min(1.0, u1[0]*u2[0] + u1[1]*u2[1]))
        phi = math.acos(dot)
        if phi < 1e-4 or abs(phi-math.pi) < 1e-4:
            out.append(P); continue
        # フィレット接線長（隣接辺長の半分でクランプ）
        eA = math.hypot(A[0]-P[0], A[1]-P[1])
        eB = math.hypot(B[0]-P[0], B[1]-P[1])
        t = min(r/math.tan(phi/2), eA*0.5, eB*0.5)
        rr = t*math.tan(phi/2)
        T1 = (P[0]+u1[0]*t, P[1]+u1[1]*t)
        T2 = (P[0]+u2[0]*t, P[1]+u2[1]*t)
        bis = _unit((u1[0]+u2[0], u1[1]+u2[1]))
        C = (P[0]+bis[0]*(rr/math.sin(phi/2)), P[1]+bis[1]*(rr/math.sin(phi/2)))
        a1 = math.atan2(T1[1]-C[1], T1[0]-C[0])
        a2 = math.atan2(T2[1]-C[1], T2[0]-C[0])
        # 最短方向でスイープ
        da = a2 - a1
        while da <= -math.pi: da += 2*math.pi
        while da >   math.pi: da -= 2*math.pi
        for k in range(seg+1):
            a = a1 + da*k/seg
            out.append((C[0]+rr*math.cos(a), C[1]+rr*math.sin(a)))
    return out

def circle_pts(R, n=96):
    return [(R*math.cos(2*math.pi*i/n), R*math.sin(2*math.pi*i/n)) for i in range(n)]

def normalize_fit(pts, target=0.9):
    """点列を [-target/2, target/2] に収まるよう中心化・等方スケール。"""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    cx = (min(xs)+max(xs))/2; cy = (min(ys)+max(ys))/2
    span = max(max(xs)-min(xs), max(ys)-min(ys))
    s = target/span
    return [((p[0]-cx)*s, (p[1]-cy)*s) for p in pts]

# ---------------------------------------------------------------- 描画ヘルパ
def n2px(n):  # 正規化 x -> ピクセル
    return (n+0.5)*SIZE*SS
def n2py(n):  # 正規化 y -> ピクセル（上下反転）
    return (0.5-n)*SIZE*SS

def new_canvas():
    img = Image.new("RGBA", (SIZE*SS, SIZE*SS), (0,0,0,0))
    return img, ImageDraw.Draw(img)

def fill_shape(d, outline, color):
    poly = [(n2px(x), n2py(y)) for x,y in outline]
    d.polygon(poly, fill=color)

def draw_number(d, text, color, font, frac=0.42, dx=0.0, dy=0.0, underline=False):
    bb = d.textbbox((0,0), text, font=font)
    w = bb[2]-bb[0]; h = bb[3]-bb[1]
    cx = SIZE*SS/2 + dx*SIZE*SS
    cy = SIZE*SS/2 + dy*SIZE*SS
    ox = cx - w/2 - bb[0]; oy = cy - h/2 - bb[1]
    d.text((ox, oy), text, fill=color, font=font)
    if underline:   # 6/9 の判別用アンダーライン（実物に倣う）
        uy = oy + bb[3] + int(0.03*SIZE*SS)
        lw = max(2, int(0.018*SIZE*SS))
        d.line([(cx - w*0.42, uy), (cx + w*0.42, uy)], fill=color, width=lw)

def draw_dots(d, count, color, R=0.16, dot_r=0.055):
    """中央配置のドット（サイコロ目風）。count=0..4。"""
    R *= SIZE*SS; dot_r *= SIZE*SS
    cx = cy = SIZE*SS/2
    offs = {
        0: [],
        1: [(0,0)],
        2: [(-R*0.5,0),(R*0.5,0)],
        3: [(-R*0.55,R*0.5),(R*0.55,R*0.5),(0,-R*0.55)],
        4: [(-R*0.5,-R*0.5),(R*0.5,-R*0.5),(-R*0.5,R*0.5),(R*0.5,R*0.5)],
    }[count]
    for ox,oy in offs:
        d.ellipse([cx+ox-dot_r, cy+oy-dot_r, cx+ox+dot_r, cy+oy+dot_r], fill=color)

def save(img, name):
    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    img.save(os.path.join(TEX, name+".png"))

# ---------------------------------------------------------------- 配色
COL = {
    "tri_body":   (236,238,240,255),   # 三角(レベル1) 白
    "tri_num":    (176,138,74,255),     # タン
    "sq_body":    (201,160,100,255),    # 四角(レベル2) タン
    "sq_num":     (250,250,248,255),    # 白
    "pen_body":   (205,211,221,255),    # 五角(レベル3) 淡ラベンダー
    "pen_num":    (92,100,112,255),      # グレー
    "hex_body":   (178,162,92,255),      # 六角(レベル4) ゴールド
    "hex_num":    (250,250,246,255),     # 白
    "mint":       (134,213,205,255),     # 裏トークン ミント
    "mint2":      (120,205,200,255),
    "blue_back":  (62,155,184,255),      # 裏トークン 六角(濃青)
    "back_dot":   (250,253,252,255),
    "red":        (192,57,43,255),       # 空気マーカー
    "board_blue": (45,124,164,255),
    "board_line": (242,247,249,255),
    "meeple_purple": (94,61,107,255),
    "meeple_red":    (190,58,47,255),
    "wood":       (217,188,140,255),
    "pip":        (40,38,36,255),
    "side_light": (228,230,233,255),     # 側面/裏（明）
    "side_tan":   (188,150,94,255),
}

manifest = {}

def add(name, outline, size_mm, thick_mm, textured, color, ptype, side_color=None):
    manifest[name] = {
        "outline": [[round(x,5), round(y,5)] for x,y in outline],
        "size_mm": size_mm, "thick_mm": thick_mm,
        "textured": textured, "color": list(color),
        "side_color": list(side_color) if side_color else list(color),
        "type": ptype,
        "tex": (name+".png") if textured else None,
    }

# ---------------------------------------------------------------- 宝物チップ
def make_treasure(name, sides, rot, value, body, num, side, size_mm,
                  frac, weight, dy=0.0):
    base = reg_poly(sides, 0.5, rot)
    outline = normalize_fit(round_corners(base, 0.12), 0.92)
    img, d = new_canvas()
    fill_shape(d, outline, body)
    font = serif(SIZE*SS*frac, weight)
    draw_number(d, str(value), num, font, dy=dy, underline=(value in (6,9)))
    save(img, name)
    add(name, outline, size_mm, 2.4, True, body, "treasure", side)

# レベル1: 三角 0-3（白地・タン数字、頂点が上なので数字をやや下げる）
for v in range(0,4):
    make_treasure(f"tri_{v}", 3, 90, v, COL["tri_body"], COL["tri_num"],
                  COL["side_light"], 33, 0.34, 620, dy=0.07)
# レベル2: 四角 4-7（タン地・白数字）
for v in range(4,8):
    make_treasure(f"sq_{v}", 4, 45, v, COL["sq_body"], COL["sq_num"],
                  COL["side_tan"], 30, 0.42, 600)
# レベル3: 五角 8-11（淡ラベンダー地・グレー数字）
for v in range(8,12):
    make_treasure(f"pen_{v}", 5, 90, v, COL["pen_body"], COL["pen_num"],
                  COL["side_light"], 33, 0.40, 620, dy=0.03)
# レベル4: 六角 12-15（ゴールド地・白数字）
for v in range(12,16):
    make_treasure(f"hex_{v}", 6, 0, v, COL["hex_body"], COL["hex_num"],
                  COL["side_tan"], 33, 0.44, 700)

# ---------------------------------------------------------------- 裏トークン（レベル指標）
def make_back(name, sides, rot, dots, body, size_mm, cross=False):
    if sides == 0:
        outline = normalize_fit(circle_pts(0.5), 0.92)
    else:
        base = reg_poly(sides, 0.5, rot)
        outline = normalize_fit(round_corners(base, 0.12), 0.92)
    img, d = new_canvas()
    fill_shape(d, outline, body)
    if cross:
        lw = int(0.045*SIZE*SS)
        c = SIZE*SS/2; r = 0.34*SIZE*SS
        d.line([(c-r,c),(c+r,c)], fill=COL["back_dot"], width=lw)
        d.line([(c,c-r),(c,c+r)], fill=COL["back_dot"], width=lw)
    else:
        draw_dots(d, dots, COL["back_dot"])
    save(img, name)
    add(name, outline, size_mm, 2.4, True, body, "back")

make_back("back_circle",  0, 0,  0, COL["mint"],      30, cross=True)
make_back("back_tri",     3, 90, 1, COL["mint"],      30)
make_back("back_square",  4, 45, 2, COL["mint2"],     28)
make_back("back_pentagon",5, 90, 3, COL["mint2"],     30)
make_back("back_hexagon", 6, 0,  4, COL["blue_back"], 30)

# ---------------------------------------------------------------- 空気マーカー（赤丸）
outline = normalize_fit(circle_pts(0.5), 0.92)
img, d = new_canvas()
fill_shape(d, outline, COL["red"])
save(img, "air_marker")
add("air_marker", outline, 18, 6.0, True, COL["red"], "air")

# ---------------------------------------------------------------- 潜水艦ボード
def chaikin(pts, iters=2):
    for _ in range(iters):
        new = []; n = len(pts)
        for i in range(n):
            p = pts[i]; q = pts[(i+1) % n]
            new.append((0.75*p[0]+0.25*q[0], 0.75*p[1]+0.25*q[1]))
            new.append((0.25*p[0]+0.75*q[0], 0.25*p[1]+0.75*q[1]))
        pts = new
    return pts

def make_submarine():
    # 実物写真(PXL_20260629)から cv2 で抽出した輪郭とドット配置を使用
    data = json.load(open(os.path.join(OUT, "_board_data.json"), encoding="utf-8"))
    outline = chaikin([tuple(p) for p in data["outline"]], 2)

    img, d = new_canvas()
    fill_shape(d, outline, COL["board_blue"])
    line = COL["board_line"]
    lw = max(2, int(0.0055*SIZE*SS))
    def P(nx,ny): return (n2px(nx), n2py(ny))
    # 縁取り（淡い白）
    d.line([P(x,y) for x,y in outline]+[P(*outline[0])], fill=(255,255,255,60), width=lw)

    # 抽出した行ジオメトリ（正規化座標, y上）。25→1 の蛇行 + ダイブ点。
    rows = [  # (ny, xL, xR, count, dir)  dir=+1:左→右, -1:右→左
        ( 0.047, -0.437,  0.410, 11, +1),   # 上段 25 ... 15
        (-0.040, -0.384,  0.372, 10, -1),   # 中段（折返し）
        (-0.124, -0.250,  0.217,  7, +1),   # 下段 ... 1
    ]
    dive = (-0.017, -0.205)

    def row_pts(ny, xl, xr, cnt, dr):
        xs = [xl + (xr-xl)*i/(cnt-1) for i in range(cnt)]
        if dr < 0: xs = xs[::-1]
        return [(x, ny) for x in xs]

    path = []                 # 蛇行順の全ドット
    rowdots = []
    for ny,xl,xr,cnt,dr in rows:
        rp = row_pts(ny,xl,xr,cnt,dr); rowdots.append(rp); path += rp

    # 接続線（蛇行 + 端の折返し弧 + ダイブへの弧）
    d.line([P(x,y) for x,y in path], fill=line, width=lw)
    d.line([P(*path[-1]), P(dive[0]+0.07, dive[1]+0.01), P(*dive)], fill=line, width=lw)

    # ドット
    dr = 0.0135*SIZE*SS
    for x,y in path:
        px,py = P(x,y)
        d.ellipse([px-dr,py-dr,px+dr,py+dr], fill=line)
    # ダイブポイント（◎）
    px,py = P(*dive)
    d.ellipse([px-dr*1.6,py-dr*1.6,px+dr*1.6,py+dr*1.6], outline=line, width=lw)
    d.ellipse([px-dr*0.55,py-dr*0.55,px+dr*0.55,py+dr*0.55], fill=line)

    # 数字ラベル（実物の表示位置に合わせる）
    fnt = sans(0.030*SIZE*SS, 500)
    def label(pt, t, off=0.050):
        px,py = P(pt[0], pt[1]+off)
        bb = d.textbbox((0,0),t,font=fnt)
        d.text((px-(bb[2]-bb[0])/2-bb[0], py-(bb[3]-bb[1])/2-bb[1]), t, fill=line, font=fnt)
    r0,r1,r2 = rowdots
    label(r0[0], "25"); label(r0[5], "20"); label(r0[10], "15")   # 上段
    label(min(r1, key=lambda p:p[0]), "10")                        # 中段 左
    for i,t in enumerate(["5","4","3","2","1"]):                   # 下段 左→右
        label(r2[i], t, off=-0.052)
    save(img, "submarine_board")
    add("submarine_board", outline, 175, 3.0, True, COL["board_blue"], "board")

make_submarine()

# ---------------------------------------------------------------- ミープル（潜水士）
def meeple_outline():
    # 右半分の輪郭（上→下）、頭は円弧
    head_c = (0.0, 0.34); head_r = 0.15
    pts = []
    # 頭頂から右回りに円弧（90°→ -20°くらいまで）
    a0, a1 = 100, -18
    seg = 16
    for i in range(seg+1):
        a = math.radians(a0 + (a1-a0)*i/seg)
        pts.append((head_c[0]+head_r*math.cos(a), head_c[1]+head_r*math.sin(a)))
    # 首〜肩〜腕〜胴〜脚（右半分）
    body = [
        (0.085, 0.16),   # 首右
        (0.30, 0.115),   # 肩〜腕付け根
        (0.345, 0.02),   # 腕先
        (0.165, -0.045), # 脇下
        (0.185, -0.30),  # 腰右
        (0.165, -0.50),  # 右足 外
        (0.045, -0.50),  # 右足 内
        (0.02, -0.20),   # 股
        (0.0, -0.20),
    ]
    pts += body
    # 左半分（ミラー、下→上の逆順）
    left = [(-x, y) for x,y in reversed(pts[:-1])]
    full = pts + left
    return normalize_fit(round_corners(full, 0.02, seg=4), 0.92)

mo = meeple_outline()
add("meeple_purple", mo, 24, 8.0, False, COL["meeple_purple"], "meeple")
add("meeple_red",    mo, 24, 8.0, False, COL["meeple_red"],    "meeple")

# ---------------------------------------------------------------- サイコロ目テクスチャ
def die_face(n):
    img = Image.new("RGBA", (SIZE*SS, SIZE*SS), COL["wood"])
    d = ImageDraw.Draw(img)
    g = SIZE*SS
    r = 0.085*g
    # 3x3 グリッド位置
    a,b,c = 0.26, 0.5, 0.74
    grid = {
        1:[(b,b)],
        2:[(a,a),(c,c)],
        3:[(a,a),(b,b),(c,c)],
        4:[(a,a),(c,a),(a,c),(c,c)],
        5:[(a,a),(c,a),(b,b),(a,c),(c,c)],
        6:[(a,a),(c,a),(a,b),(c,b),(a,c),(c,c)],
    }[n]
    for px,py in grid:
        x,y = px*g, py*g
        d.ellipse([x-r,y-r,x+r,y+r], fill=COL["pip"])
    img = img.resize((SIZE,SIZE), Image.LANCZOS)
    img.save(os.path.join(TEX, f"die_{n}.png"))

for n in range(1,7):
    die_face(n)
manifest["die"] = {"type":"die", "size_mm":16, "color":list(COL["wood"])}

# ---------------------------------------------------------------- 書き出し
with open(os.path.join(OUT, "outlines.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)

print("textures:", len(os.listdir(TEX)), "files")
print("pieces:", len(manifest))
print("OUT:", OUT)
