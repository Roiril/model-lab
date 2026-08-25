"""servo-arm の 3 部品を造形プレートに並べる。

形は一切いじらない。servo-arm が出した印刷用 STL を読み込み、底をプレートに落とし、
brim のぶんを空けて横に並べるだけ。並べたものを 1 つの STL として出す。

判定は Bambu Studio の設定に合わせてある（exports/whistle.3mf の実測値）:
  X1 Carbon / 0.4mm ノズル / 0.2mm 層 / PLA Basic / サポート OFF /
  support_threshold_angle = 30° / auto brim / 手前左 18 x 28mm は除外域

サポートを切って刷るので、「下向きで水平から 30° 以内の面」は
  (a) プレート接地  (b) 両端が肉に載る橋渡し
のどちらかでなければならない。ビルドのたびに、その内訳を印字する。

使い方:
  1. ./run.sh models/servo-arm/model.py     ← 先にこちら（STL を作る）
  2. ./run.sh models/servo-arm-plate/model.py
  3. exports/servo-arm-plate.stl を Bambu Studio へ。3 部品が入った 1 オブジェクトに
     なるので、そのまま刷るか「オブジェクトに分割」して個別設定を付ける
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import math
import time
import bpy
import bmesh
from mathutils import Vector

import blender_utils
from blender_utils import clear_scene, export_stl
from params import *

MM = 0.001
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "servo-arm")
THRESH = 30.0          # サポートが要るかの境目（水平からの角度）
FIRST_LAYER = 0.25     # これ以下はプレート接地とみなす [mm]


def _activate(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    return o


def load_part(name):
    """印刷用 STL を読み、m 単位へ直して、底を z=0 に落とす。"""
    path = os.path.join(blender_utils.EXPORTS_DIR, name + ".stl")
    if not os.path.exists(path):
        raise SystemExit(f"[plate] {name}.stl が無い。先に servo-arm をビルドすること")
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=path)
    o = (set(bpy.data.objects) - before).pop()
    o.name = name
    _activate(o)
    o.scale = (MM, MM, MM)                      # STL は mm。プロジェクトは m
    bpy.ops.object.transform_apply(scale=True)
    zmin = min((o.matrix_world @ v.co).z for v in o.data.vertices)
    o.location = (0, 0, -zmin)                  # 底をプレートへ
    bpy.ops.object.transform_apply(location=True)
    return o


def printability(o):
    """接地 / 橋渡し / 空中 の面積 [mm2] と、橋渡しの最大差し渡し [mm]。

    真下に肉があるかをレイで見る。穴の天井は真下が空なので、そのときは
    その層の高さで水平 8 方向へ飛ばし、近くの壁に届けば橋渡しと判定する。
    """
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.normal_update()
    lim = math.cos(math.radians(THRESH))
    contact = 0.0
    flagged = []
    for f in bm.faces:
        n = f.normal
        if n.z >= 0 or abs(n.z) < lim:
            continue
        c = f.calc_center_median()
        if c.z * 1000 <= FIRST_LAYER:
            contact += f.calc_area()
        else:
            flagged.append(f)

    fset = {f.index for f in flagged}
    seen, comps = set(), []
    for f in flagged:
        if f.index in seen:
            continue
        stack, grp = [f], []
        seen.add(f.index)
        while stack:
            cur = stack.pop(); grp.append(cur)
            for e in cur.edges:
                for h in e.link_faces:
                    if h.index in fset and h.index not in seen:
                        seen.add(h.index); stack.append(h)
        comps.append(grp)

    bridge = air = 0.0
    span = 0.0
    inv = o.matrix_world.inverted()
    for grp in comps:
        area = sum(f.calc_area() for f in grp)
        pts = [v.co for f in grp for v in f.verts]
        cen = sum(pts, Vector()) / len(pts)
        xs = [p.x for p in pts]; ys = [p.y for p in pts]
        w = max(max(xs) - min(xs), max(ys) - min(ys))
        # ⚠ 「真下に肉があるか」では判定できない。10mm 上に浮いた板でも真下には
        #    土台があるので通ってしまう（校正用の浮いた板を実際に見逃した）。
        #    横へレイを飛ばす手も使えない。浮いた板でもレイは自分の側壁に当たる。
        #    刷れるかどうかを決めるのは「その層で、輪郭のすぐ外に肉があるか」。
        #    あれば端が載る（橋渡し・張り出し）。無ければ空中で始まる。
        zt = min(p.z for p in pts) + 0.00015
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        off = 0.0006
        probes = []
        for t in [i / 4.0 for i in range(5)]:
            probes += [Vector((x0 + (x1 - x0) * t, y0 - off, zt)),
                       Vector((x0 + (x1 - x0) * t, y1 + off, zt)),
                       Vector((x0 - off, y0 + (y1 - y0) * t, zt)),
                       Vector((x1 + off, y0 + (y1 - y0) * t, zt))]
        anchored = 0
        for p3 in probes:
            res, loc, nrm, _ = o.closest_point_on_mesh(inv @ p3)
            if res and (inv @ p3 - loc).dot(nrm) < 0:      # 面の内側 = 肉の中
                anchored += 1
        if anchored == 0:
            air += area
            print(f"[plate] ⚠ {o.name}: 空中で始まる面 {area * 1e6:.1f}mm2 "
                  f"@ z={cen.z * 1000:.1f}mm 差し渡し {w * 1000:.1f}mm "
                  f"（部品の中で x={cen.x * 1000:.1f} y={cen.y * 1000:.1f}）")
            continue
        bridge += area
        span = max(span, w)
    bm.free()
    return contact * 1e6, bridge * 1e6, air * 1e6, span * 1000


# ============================================================
# 元の STL が古くないか
# ============================================================
def check_fresh(names):
    src_t = max(os.path.getmtime(os.path.join(SRC, f)) for f in ("model.py", "params.py"))
    for n in names:
        p = os.path.join(blender_utils.EXPORTS_DIR, n + ".stl")
        if os.path.exists(p) and os.path.getmtime(p) < src_t:
            print(f"[plate] ⚠ {n}.stl が servo-arm のソースより古い "
                  f"（STL {time.strftime('%m-%d %H:%M', time.localtime(os.path.getmtime(p)))} < "
                  f"ソース {time.strftime('%m-%d %H:%M', time.localtime(src_t))}）。"
                  f"先に ./run.sh models/servo-arm/model.py を回すこと")


clear_scene()
check_fresh(ORDER)
parts = [load_part(n) for n in ORDER]
AIR_TOTAL = [0.0]     # 3 部品ぶんの「空中で始まる面」の合計 [mm2]

# ============================================================
# 並べる（brim + すきま を空けて横に、Y は中央そろえ）
# ============================================================
PITCH_GAP = (2 * BRIM + GAP) * MM
widths = [p.dimensions.x for p in parts]
depths = [p.dimensions.y for p in parts]
total_w = sum(widths) + PITCH_GAP * (len(parts) - 1)
x = (BED_W * MM - total_w) / 2 if PLACE_ALL else (BED_W * MM - widths[0]) / 2

print(f"[plate] プレート {BED_W:.0f} x {BED_D:.0f}mm / 除外域 手前左 "
      f"{EXCLUDE_W:.0f} x {EXCLUDE_D:.0f}mm / brim {BRIM:.0f}mm")
ok = True
for p, w, d in zip(parts, widths, depths):
    bb = [p.matrix_world @ Vector(c) for c in p.bound_box]
    x0 = min(v.x for v in bb); y0 = min(v.y for v in bb)
    p.location = (p.location.x + (x - x0), p.location.y + ((BED_D * MM - d) / 2 - y0), p.location.z)
    _activate(p)
    bpy.ops.object.transform_apply(location=True)

    bb = [p.matrix_world @ Vector(c) for c in p.bound_box]
    X0, X1 = min(v.x for v in bb) * 1000, max(v.x for v in bb) * 1000
    Y0, Y1 = min(v.y for v in bb) * 1000, max(v.y for v in bb) * 1000
    b = BRIM
    inside = (X0 - b >= MARGIN and X1 + b <= BED_W - MARGIN
              and Y0 - b >= MARGIN and Y1 + b <= BED_D - MARGIN)
    clear_ex = not (X0 - b < EXCLUDE_W and Y0 - b < EXCLUDE_D)
    ok = ok and inside and clear_ex
    con, bri, air, span = printability(p)
    AIR_TOTAL[0] += air
    print(f"[part] {p.name:<17} {w * 1000:5.1f} x {d * 1000:5.1f} x "
          f"{p.dimensions.z * 1000:5.1f}mm  置き場所 x {X0:5.1f}〜{X1:5.1f} / y {Y0:5.1f}〜{Y1:5.1f}"
          + ("" if inside and clear_ex else "  ⚠ プレートからはみ出す"))
    print(f"       接地 {con:6.0f}mm2 / 橋渡し {bri:5.0f}mm2（最大差し渡し {span:4.1f}mm）"
          f" / 空中 {air:.1f}mm2")
    x += w + PITCH_GAP
    if not PLACE_ALL:
        break

print(f"[plate] 3 部品の占める幅 {total_w * 1000:.1f}mm / "
      + ("全部プレートに収まる" if ok else "⚠ 収まらない。GAP か並べ方を見直すこと"))
if AIR_TOTAL[0] < 1.0:
    print(f"[plate] 空中で始まる面は合計 {AIR_TOTAL[0]:.1f}mm2。サポート無しで刷れる")
else:
    print(f"[plate] ⚠ 空中で始まる面が合計 {AIR_TOTAL[0]:.1f}mm2 ある。"
          f"サポートを入れるか、その場所を設計で直すこと")

export_stl("servo-arm-plate")
