"""laser_core — レーザーカッター箱組み（フィンガージョイント）の一元モジュール。

3Dの servo_core.py に相当する「単一真実源」。素材・カーフ・嵌合の実物 config と、
フィンガージョイント箱を SVG(mm) に展開するヘルパーをここに集約する。

出力規約（make_vector.py / Trotec Ruby に準拠）:
  - カットライン = 赤ヘアライン  stroke="#FF0000" stroke-width="0.01" fill="none"
  - 彫刻        = 黒ベタ        fill="#000000"（Ruby 側でパワー/スピード再指定）
  - 単位は mm。SVG は width/height を mm 指定 + viewBox 同値。

機種: Trotec Speedy 300 / 30W / 加工エリア 726 x 432 mm。
"""

# ============================================================
#  実物 config（単一真実源）— 実機キャリブレーションでここを詰める
# ============================================================

# 素材（3mm アクリル）
MAT_T = 3.0          # 板厚 mm（フィンガーのタブ深さ＝この値）

# レーザーのカーフ（ビーム幅で溶ける分）。最初のテストカットで実測して詰める。
#   0 で出すと「設計寸ぴったり」のカット中心線。アクリルは概ね 0.1〜0.2mm。
#   KERF を上げるとタブが太く（＝きつめ）なる方向に補正する。
KERF = 0.1           # mm（テスト省略の一発本番用に実機現実値 0.1 を採用。実測後に再調整可）

# 加工エリア（Trotec Speedy 300）
BED_W = 726.0
BED_H = 432.0

# フィンガー幅の目安（この値に近い本数を自動で奇数化して使う）
FINGER_TARGET = 11.0  # mm


def finger_count(length, target=FINGER_TARGET):
    """エッジ長から奇数のフィンガー本数を決める（最小3、必ず奇数）。

    奇数にすることで male エッジは finger…finger（両端タブ＝角が埋まる）、
    female エッジは gap…gap（両端ノッチ＝角が欠ける）で相補になる。
    """
    n = max(3, round(length / target))
    if n % 2 == 0:
        n += 1
    return n


# ============================================================
#  幾何ヘルパー
# ============================================================

def _add(p, q):
    return (p[0] + q[0], p[1] + q[1])


def _mul(v, s):
    return (v[0] * s, v[1] * s)


def edge_internal(start, du, normal, length, n, male, t=MAT_T, kerf=KERF):
    """1 エッジの「内部ジグザグ点列」を返す（両端の角頂点は含まない）。

    角は rect_panel 側で male/female の凹み状態から矩形コーナー頂点として算出する。
    ここでは内部境界(u = seg..length-seg)の縦段差のみを生成する。

    start  : エッジ始点 (x,y) mm（＝CCW 上の手前の角の公称位置）
    du     : エッジ進行方向の単位ベクトル
    normal : パネル内側を向く単位ベクトル（gap はこちらに t だけ凹む）
    n      : フィンガー本数（奇数）
    male   : True=偶数番が finger（タブ）/ False=偶数番が gap（ノッチ）

    kerf 補正: 内部境界を動かしてタブ(finger)を kerf/2 ずつ広げ、gap を狭める。
    """
    seg = length / n
    is_finger = [((i % 2 == 0) == male) for i in range(n)]
    bounds = [i * seg for i in range(n + 1)]
    for i in range(1, n):
        if is_finger[i - 1] and not is_finger[i]:
            bounds[i] += kerf / 2.0
        elif (not is_finger[i - 1]) and is_finger[i]:
            bounds[i] -= kerf / 2.0

    def depth(i):
        return 0.0 if is_finger[i] else t

    pts = []
    for b in range(1, n):  # 内部境界のみ
        u = bounds[b]
        d_prev, d_next = depth(b - 1), depth(b)
        base = _add(start, _mul(du, u))
        pts.append(_add(base, _mul(normal, d_prev)))  # 段差の手前
        pts.append(_add(base, _mul(normal, d_next)))  # 段差の後
    return pts


def rect_panel(A, B, edges, t=MAT_T, kerf=KERF, n_over=None):
    """A(幅,u) x B(高,v) のパネル外周をフィンガー付き閉ループ点列で返す。

    edges = dict(bottom=male?, right=?, top=?, left=?) の bool（True=male）。
    n_over= dict(edge -> 本数) で本数を上書き可（n=1 + male=True で直線エッジ）。
    角(0,0)->(A,0)->(A,B)->(0,B) を CCW で回る。female エッジは両端が gap(凹)。
    角頂点は隣接2エッジの凹み状態から矩形ノッチとして算出（斜め欠けを防ぐ）。
    """
    n_over = n_over or {}
    nA = n_over.get("bottom", finger_count(A))
    nB = n_over.get("right", finger_count(B))
    # エッジ定義（CCW）: (始点, du, 内側normal, 長さ, n, male)
    E = {
        "bottom": ((0, 0), (1, 0), (0, 1), A, n_over.get("bottom", nA), edges["bottom"]),
        "right":  ((A, 0), (0, 1), (-1, 0), B, n_over.get("right", nB), edges["right"]),
        "top":    ((A, B), (-1, 0), (0, -1), A, n_over.get("top", nA), edges["top"]),
        "left":   ((0, B), (0, -1), (1, 0), B, n_over.get("left", nB), edges["left"]),
    }
    seq = ["bottom", "right", "top", "left"]
    # 公称角（CCW 上で seq[i] の始点 = 角 i）
    corners_nom = {"bottom": (0, 0), "right": (A, 0), "top": (A, B), "left": (0, B)}

    def corner_vertex(prev_name, next_name):
        """prev エッジの終端 = next エッジの始端 = この角。
        female なら各エッジの内側 normal 方向に t 凹む（矩形ノッチの内角）。"""
        cn = corners_nom[next_name]
        v = list(cn)
        if not E[prev_name][5]:  # prev female → prev の normal 方向に凹む
            pn = E[prev_name][2]
            v[0] += pn[0] * t; v[1] += pn[1] * t
        if not E[next_name][5]:  # next female → next の normal 方向に凹む
            nn = E[next_name][2]
            v[0] += nn[0] * t; v[1] += nn[1] * t
        return (v[0], v[1])

    loop = []
    for i, name in enumerate(seq):
        prev_name = seq[(i - 1) % 4]
        loop.append(corner_vertex(prev_name, name))           # 角頂点
        start, du, nrm, length, n, male = E[name]
        loop += edge_internal(start, du, nrm, length, n, male, t, kerf)  # 内部ジグザグ
    loop.append(loop[0])  # 閉じる
    return loop


# ============================================================
#  6面フィンガー箱
# ============================================================
#
#  male/female 割り当て（各共有エッジが必ず male+female の相補になる）:
#    Top / Bottom (W x D)        : 全エッジ male
#    Front / Back (W x H)        : 上下エッジ female, 左右エッジ male
#    Left / Right (D x H)        : 全エッジ female
#
#  検証:
#    - W エッジ(front上⇔top前)     : front上=female, top=male            ✓
#    - H エッジ(front左⇔left前)     : front左=male,  left=female          ✓
#    - D エッジ(top左⇔left上)       : top=male,      left上=female        ✓
#  → 12 エッジすべて male/female 一意。

def box_panels(W, D, H, t=MAT_T, kerf=KERF):
    """外形 W(x) x D(y) x H(z) の箱の 6 パネル外周を返す。

    戻り値: dict(name -> (loop点列, (パネル幅A, パネル高B)))
    """
    P = {}
    # bottom / top: A=W, B=D, 全 male
    male_all = dict(bottom=True, right=True, top=True, left=True)
    P["bottom"] = (rect_panel(W, D, male_all, t, kerf), (W, D))
    P["top"] = (rect_panel(W, D, male_all, t, kerf), (W, D))
    # front / back: A=W, B=H, 上下(bottom/top)=female, 左右(right/left)=male
    fb = dict(bottom=False, right=True, top=False, left=True)
    P["front"] = (rect_panel(W, H, fb, t, kerf), (W, H))
    P["back"] = (rect_panel(W, H, fb, t, kerf), (W, H))
    # left / right: A=D, B=H, 全 female
    female_all = dict(bottom=False, right=False, top=False, left=False)
    P["left"] = (rect_panel(D, H, female_all, t, kerf), (D, H))
    P["right"] = (rect_panel(D, H, female_all, t, kerf), (D, H))
    return P


# ============================================================
#  SVG 出力（カット＝赤ヘアライン / 彫刻＝黒ベタ）
# ============================================================

def loop_to_path(loop, dx=0.0, dy=0.0):
    d = "M " + " L ".join(f"{x+dx:.3f},{y+dy:.3f}" for x, y in loop) + " Z"
    return d


def _engrave_subpaths(item):
    """engrave エントリを (subpaths, dx, dy) に正規化。

    item は (loop, dx, dy)          … 単一ループ
        or (subpaths, dx, dy)       … 複合（subpaths=ループのリスト, evenodd で穴/島）
    単一ループ判定: 先頭要素が (x,y) のタプルなら単一ループ。
    """
    first, dx, dy = item
    if first and isinstance(first[0], (int, float)):
        return [first], dx, dy          # 単一ループ
    return first, dx, dy                # ループのリスト


def write_svg(path, cut_loops, engrave_loops=None, margin=5.0):
    """cut_loops: [(loop, dx, dy)]  engrave_loops: [(loop|subpaths, dx, dy)] mm。

    cut    = 赤ヘアライン（外周・スロット）
    engrave= 黒ベタ（顔）。複合パスは fill-rule:evenodd で穴/島を表現。
    """
    engrave_loops = engrave_loops or []
    eng_norm = [_engrave_subpaths(it) for it in engrave_loops]
    all_pts = [(x + dx, y + dy) for loop, dx, dy in cut_loops for (x, y) in loop]
    all_pts += [(x + dx, y + dy) for sub, dx, dy in eng_norm for lp in sub for (x, y) in lp]
    maxx = max(x for x, _ in all_pts)
    maxy = max(y for _, y in all_pts)
    minx = min(x for x, _ in all_pts)
    miny = min(y for _, y in all_pts)
    W = (maxx - minx) + 2 * margin
    H = (maxy - miny) + 2 * margin
    ox, oy = margin - minx, margin - miny

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'width="{W:.2f}mm" height="{H:.2f}mm" '
           f'viewBox="0 0 {W:.2f} {H:.2f}">']
    # 彫刻（先に黒ベタ。複合パスは evenodd）
    for sub, dx, dy in eng_norm:
        d = " ".join(loop_to_path(lp, dx + ox, dy + oy) for lp in sub)
        out.append(f'<path d="{d}" fill="#000000" fill-rule="evenodd" stroke="none"/>')
    # カット（赤ヘアライン）
    for loop, dx, dy in cut_loops:
        out.append(f'<path d="{loop_to_path(loop, dx+ox, dy+oy)}" '
                   f'fill="none" stroke="#FF0000" stroke-width="0.01"/>')
    out.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(out))
    return (W, H)


# ============================================================
#  かわいい顔の彫刻パーツ（多角形近似ループを返す）
# ============================================================

def circle(cx, cy, r, seg=48):
    import math
    return [(cx + r * math.cos(2 * math.pi * i / seg),
             cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


def arc(cx, cy, r, a0, a1, seg=24):
    import math
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / seg),
             cy + r * math.sin(a0 + (a1 - a0) * i / seg)) for i in range(seg + 1)]
