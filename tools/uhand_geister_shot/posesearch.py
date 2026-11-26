# -*- coding: utf-8 -*-
"""手の姿勢と傾きを格子で探し、駒を親指の先と人差し指の先でつまむ場面を決める。カメラは見ない。

"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python tools/uhand_geister_shot/posesearch.py --
    --out scene.json [--quick]

目標（参照の記述から）:
  - 親指の先は駒の下のほう（接点の高さ 2〜15mm）、人差し指の先は駒の頭の横（25〜45mm）に接する
  - ほかの部品は駒に食い込まない
  - 手は床から浮く。最も低いのは親指の先（中指などの先が床に着かない）
  - 傾きは小さいほどよい（手のひらを下に向けた自然な姿勢）
"""
import itertools
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np

import scene as SC


def arg(name, default=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(name) + 1] if name in a else default


def flag(name):
    return "--" in sys.argv and name in sys.argv[sys.argv.index("--") + 1:]


VIS_GATE = 20.0
# 斜め上からの向き（駒からカメラへ）。方位は -Y から +X 側へ（camsearch.py と同じ）
DIRS = []
for _el in (45, 50, 55, 60):
    for _az in range(0, 360, 15):
        _e, _a = math.radians(_el), math.radians(_az)
        DIRS.append((_el, _az, (math.sin(_a) * math.cos(_e), -math.cos(_a) * math.cos(_e), math.sin(_e))))


def band(x, lo, hi):
    return 0.0 if lo <= x <= hi else min(abs(x - lo), abs(x - hi))


def evaluate(S, index, step, thumb, pitch, roll, little=None, tprox=None, ttip=None):
    d = SC.fingers(index, step, little)
    d["thumb"] = thumb
    if tprox is not None:       # 親指の基節と末節の角度 [deg] を別々に（scene.py の _thumb_pose）
        d["thumb_prox_deg"], d["thumb_tip_deg"] = tprox, ttip
    S.set_hand(d, pitch, roll)
    c, cl, v = S.place_ghost()
    if not cl:
        return None
    t, i = cl["uh_thumb_tip"], cl["uh_index_tip"]
    others = min((val[0] for k, val in cl.items() if k not in ("uh_thumb_tip", "uh_index_tip")), default=1.0)
    tips_low = min(S.verts[f"uh_{f}_tip"][:, 2].min() for f in ("middle", "ring", "little"))
    score = (abs(t[0]) + abs(i[0])) * 1000 * 4                    # 接していること [mm]
    score += max(0.0, -others) * 1000 * 50                         # 食い込み
    score += band(t[1] * 1000, 2, 15) * 2 + band(i[1] * 1000, 25, 45) * 2
    score += max(0.0, 6 - tips_low * 1000) * 2                     # ほかの指の先は 6mm 以上浮く
    score += abs(pitch) * 0.05 + abs(roll) * 0.08
    vis, vdir = 0.0, None
    # 参照の見え方: 手の甲が見え（甲の法線とカメラの向きの内積 0.5 以上）、親指の側がカメラに近い
    R = SC.hand_rot(pitch, roll)
    back, thumb_side = R @ np.array([0, 1.0, 0]), R @ np.array([1.0, 0, 0])
    dirs = [x for x in DIRS if np.dot(x[2], back) >= 0.5 and np.dot(x[2], thumb_side) >= 0.0]
    if score < VIS_GATE and dirs:     # 接触が成り立つ候補だけ、駒が見える向きを探す（重い）
        vals = S.visibility([d for _, _, d in dirs])
        k = int(np.argmax(vals))
        vis, vdir = vals[k], dirs[k][:2]
        score += max(0.0, 0.9 - vis) * 200          # 硬い条件: 9 割以上見える向きがある
    else:
        score += 200
    return dict(score=score, visible=vis, view_el_az=vdir, index=index, step=step, thumb=thumb, pitch=pitch, roll=roll, c=[float(c[0]), float(c[1])],
                thumb_gap_mm=t[0] * 1000, thumb_z_mm=t[1] * 1000, index_gap_mm=i[0] * 1000, index_z_mm=i[1] * 1000,
                others_min_mm=others * 1000, other_tips_low_mm=tips_low * 1000, lowest=S.lowest, dofs=d)


def main():
    S = SC.Scene()
    if flag("--quick"):
        t0 = time.time()
        for g in ((0.85, 0.07, 1.0, 0, 20), (0.7, 0.05, 0.5, 20, 0)):
            t0 = time.time()
            r = evaluate(S, *g)
            print(f"[pose] {g}: {time.time() - t0:.2f} 秒 score={r['score']:.1f} 見え={r['visible']:.2f} 向き={r['view_el_az']} "
                  f"親指 {r['thumb_gap_mm']:.1f}mm@{r['thumb_z_mm']:.0f} 人差し指 {r['index_gap_mm']:.1f}mm@{r['index_z_mm']:.0f}")
        return
    axes = {"index": (0.5, 0.6, 0.7, 0.8, 0.9, 1.0), "step": (0.05,), "thumb": (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
            "pitch": (-10, 0, 10, 20, 30, 40), "roll": (-30, -20, -10, 0, 10, 20, 30), "little": (None,),
            "tprox": (None,), "ttip": (None,)}
    # little を固定すると step は使われず、人差し指から小指までを直線でつなぐ（負は甲の側へ反る）
    if arg("--fix"):      # 例: --fix index=0.7,step=0.15,thumb=1,pitch=-10,roll=20 / --fix index=0.7,little=-0.08,...
        for kv in arg("--fix").split(","):
            k, v = kv.split("=")
            axes[k] = tuple(float(x) for x in v.split("|"))     # a|b|c で複数の値を並べて探す
    grid = list(itertools.product(*axes.values()))
    res = []
    t0 = time.time()
    for n, g in enumerate(grid):
        r = evaluate(S, *g)
        if r:
            res.append(r)
        if n % 100 == 0:
            best = min(res, key=lambda x: x["score"]) if res else None
            print(f"[pose] {n}/{len(grid)} {time.time() - t0:.0f}s 最良 {best and round(best['score'], 2)}", flush=True)
    res.sort(key=lambda x: x["score"])
    for r in res[:8]:
        print("[pose] " + ", ".join(f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}" for k, v in r.items() if k != "dofs"))
    out = arg("--out")
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"best": res[0], "top": res[:20]}, f, ensure_ascii=False, indent=1)
    os.replace(tmp, out)
    print("[pose]", out)


main()
