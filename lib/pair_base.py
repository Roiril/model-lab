"""脚 2 本（芯間 SPAN）と、任意で中心線上の 3 本目を受けるベースの形づくり。

pipe-foot-pair/model.py（直線の壁の端）と pipe-foot-corner/model.py（角。A は 5 本目つき、
B は脚 2 本だけ）が同じ関数で出す。寸法は params モジュール P から、3 本目の位置だけ
引数で受ける。形づくりの部品（回転体・押し出し・boolean・板の網）は foot_core。
"""
import os

import bpy
import foot_core as fc


def spine_top(P, x):
    """主材の上端。中央で傾きが 0 になる二次曲線。

    smoothstep にすると中央が平らな帯になり、板を立てただけに見える。
    曲げを受けるのは根元だけなので、中央は低くてよい。
    """
    t = abs(x) / (P.SPAN / 2)
    return P.SPINE_MID_Z + (P.SPINE_TOP_Z - P.SPINE_MID_Z) * t * t


def branch_top_for(P, third_off):
    """枝の上端。主材の側面から出る所の高さを起点に、同じ二次曲線で上がる。"""
    y0 = P.SPINE_T / 2
    z0 = spine_top(P, y0)

    def top(y, side):
        t = (y - y0) / (third_off - y0)
        return z0 + (P.SPINE_TOP_Z - z0) * t * t
    return top


def spine(P, third_off):
    """背骨。X 方向の主材と、3 本目があればそこへ伸びる枝を 1 つのメッシュで作る（T 字）。

    枝を別体にして boolean で足すと、主材の上面（中央で 14mm）と枝の上面が
    ほぼ同じ高さで交わり、0.1mm 以下の段や薄片が出て bevel が荒れる。
    中央に SPINE_T 角の芯を置き、主材の左右と枝をその芯の面につなぐ（wall_net）。
    両端はソケットの軸まで伸ばし、肉の中で終わらせる。
    """
    sx = P.SPAN / 2
    n = P.SPINE_SEG // 2
    main = lambda s, side: spine_top(P, s)
    zb = P.PLATE_T - P.SPINE_LAP
    if third_off is None:
        return fc.wall_net("spine", {}, [
            dict(axis="x", c=0.0, a=("free", -sx), b=("free", sx), top=main, seg=P.SPINE_SEG),
        ], P.SPINE_T, zb)
    return fc.wall_net("spine", {"J": (0.0, 0.0)}, [
        dict(axis="x", c=0.0, a=("free", -sx), b=("node", "J"), top=main, seg=n),
        dict(axis="x", c=0.0, a=("node", "J"), b=("free", sx), top=main, seg=n),
        dict(axis="y", c=0.0, a=("node", "J"), b=("free", third_off),
             top=branch_top_for(P, third_off), seg=P.BRANCH_SEG),
    ], P.SPINE_T, zb)


def bore_sockets(P, body, centers):
    """パイプの穴（座面まで）と、口の漏斗（脚を上から落とすときのリード）を開ける。"""
    r = P.BORE_D / 2
    funnel = [(P.BOSS_TOP - P.FUNNEL_L, r),
              (P.BOSS_TOP + 1.0, r + P.FUNNEL_DR * (P.FUNNEL_L + 1.0) / P.FUNNEL_L)]
    for k, c in enumerate(centers):
        fc.boolean(body, fc.cyl("bore%d" % k, r, P.SEAT_Z, P.BOSS_TOP + 10,
                                c[0], c[1], P.SEG), "DIFFERENCE")
        fc.boolean(body, fc.revolve("funnel%d" % k, funnel, fc.translate(*c), P.SEG), "DIFFERENCE")
    return body


def finish(P, body):
    """スリバーを潰し、変換を焼いて書き出せる状態にする（穴あけの後に呼ぶ）。"""
    # 穴あけが残す極小のスリバーを潰す。0.02mm は最小の造形物（口元の肉厚 1.0mm）の
    # 1/50 なので意図した形には触らない。
    # ⚠ 0.1mm まで粗くすると bevel の刻みまで潰れて、非多様体が 3 から 15 に増える
    fc.clean(body, dist=2e-5)
    fc.activate(body)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_flat()
    return body


def build(P, name, third_off):
    """P: pipe-foot-pair の params。third_off: 3 本目の軸の、脚の軸線からの距離（+Y 側）。
    None なら脚 2 本だけ。"""
    # 角丸を作るために下へ伸ばしておき、最後に z=0 で切る。
    # こうすると底面は平らなまま、その上だけが丸まる。
    z_bot = -P.BASE_ROUND
    sx = P.SPAN / 2
    # ソケットの軸と、そのひれの向き。ひれは背骨と直交する側に出す
    sockets = [((-sx, 0.0), (90.0, -90.0)),
               ((sx, 0.0), (90.0, -90.0))]
    if third_off is not None:
        sockets.append(((0.0, third_off), (0.0, 180.0)))

    # 床に着く板（ソケットを包む凸包。反時計回りに並べる）
    body = fc.prism(name, fc.hull_poly([c for c, _ in sockets], P.PLATE_R, P.SEG),
                    z_bot, P.PLATE_T)

    # ソケット
    prof = fc.socket_profile(P, z_bot)
    for k, (c, _) in enumerate(sockets):
        fc.boolean(body, fc.revolve("socket%d" % k, prof, fc.translate(*c), P.SEG), "UNION")

    # 背骨（主材 + 枝）
    fc.boolean(body, spine(P, third_off), "UNION")

    # 横のひれ（ソケットごとに 2 枚）
    for k, (c, angs) in enumerate(sockets):
        for j, ang in enumerate(angs):
            fc.boolean(body, fc.fin("fin%d%d" % (k, j), P, c[0], c[1], ang), "UNION")

    # 接合部に R
    fc.clean(body)
    fc.bevel(body, P.FILLET_R * fc.MM, P.FILLET_SEG, P.FILLET_ANGLE)

    # 底を平らに切る（角丸を残したまま接地面を確保）
    fc.boolean(body, fc.box_mm("cut_base", -300, 300, -300, 300, -100, 0), "DIFFERENCE")

    bore_sockets(P, body, [c for c, _ in sockets])
    return finish(P, body)


def export(body, exports_dir, filename):
    os.makedirs(exports_dir, exist_ok=True)
    stl = os.path.join(exports_dir, filename)
    fc.activate(body)
    bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True,
                          global_scale=1000.0, ascii_format=False)
    print("Exported:", stl)
    print("bbox mm:", [round(v * 1000, 2) for v in body.dimensions])
    return stl
