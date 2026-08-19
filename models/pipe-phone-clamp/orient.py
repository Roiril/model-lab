# 印刷の向きを総当たりで評価する。スパゲッティの原因を数字で特定するための道具。
#
#   ./run.sh models/pipe-phone-clamp/orient.py
#
# 見るのは 3 つ。
#   接地  … 造形板に着く面積。ここが小さいと部品全体がサポートの上で揺れる
#   要サポート … 45°より寝た下向き面（ボアの中は切妻で処理できるので除く）
#   高さ  … 造形の高さ
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from mathutils import Vector

from blender_utils import clear_scene
import params as P
import mount as M

clear_scene()
coll = bpy.context.scene.collection
fC, fK, arm = M.frames(P.PHONE_CENTER, P.PLATE_EULER_DEG, P.RAIL_POINT, P.RAIL_DIR)
fR, fQ = M.corner_frames(fC)
ob = M.build_one(coll, fR, fQ, fC)

MX = (fC.to_3x3() @ Vector((1, 0, 0))).normalized()
MY = (fC.to_3x3() @ Vector((0, 1, 0))).normalized()
MZ = (fC.to_3x3() @ Vector((0, 0, 1))).normalized()

tris = [((ob.matrix_world.to_3x3() @ f.normal).normalized(), f.area, ob.matrix_world @ f.center)
        for f in ob.data.polygons]
ws = [ob.matrix_world @ v.co for v in ob.data.vertices]


def in_bore(c, rad=0.024):
    for f in (fR, fQ):
        o = f.translation
        d = (f.to_3x3() @ Vector((0, 0, 1))).normalized()
        w = c - o
        if (w - d * w.dot(d)).length < rad:
            return True
    return False


def report(up):
    up = Vector(up).normalized()
    lo = min(w.dot(up) for w in ws)
    hi = max(w.dot(up) for w in ws)
    base = sum(a for n, a, c in tris if n.dot(up) < -0.98 and c.dot(up) < lo + 0.0005)
    bad = sum(a for n, a, c in tris
              if n.dot(up) < -0.72 and c.dot(up) > lo + 0.0005 and not in_bore(c))
    return (hi - lo) * 1000, base * 1e6, bad * 1e6, lo


# --- いまの向き（Mz を上）で、ポケットの底がどこにあるか ---
h, base, bad, lo = report(MZ)
print("■ いまの向き（ポケットを立てる = Mz を上）")
print(f"   高さ {h:.1f}mm / 接地 {base:.0f}mm2 / 要サポート {bad:.0f}mm2")
corners = []
for sy in (-1, 1):
    for sx in (-1, 1):
        p = fC @ Vector((P.X_BACK if sx < 0 else P.X_FRONT, sy * P.SHELL_Y / 2, P.Z_BOT))
        corners.append(p.dot(MZ) - lo)
print(f"   ポケットの底の四隅は造形板から {min(corners)*1000:.1f} 〜 {max(corners)*1000:.1f}mm 浮いている")
print("   → ここが「下の角」。宙に浮いた細い壁がサポートの上に載っている")

# --- スロットの壁を垂直に保つ向き（up ⊥ Mx）を総当たり ---
print("\n■ スロットの壁が垂直になる向き（up ⊥ Mx）を 5° 刻みで走査")
print("   角度  高さmm   接地mm2  要サポートmm2   （接地が大きいほど失敗しにくい）")
rows = []
for deg in range(0, 360, 5):
    t = math.radians(deg)
    up = MZ * math.cos(t) + MY * math.sin(t)
    h, base, bad, _ = report(up)
    rows.append((base, bad, h, deg, up))
for base, bad, h, deg, up in sorted(rows, key=lambda r: -r[0])[:8]:
    print(f"   {deg:4d}°  {h:6.1f}  {base:8.0f}  {bad:9.0f}")

# --- 制約を外して全面走査（面の法線を候補にする） ---
print("\n■ 面の法線を全部試す（接地の大きい順。スロットの向きは問わない）")
cand = []
for n, a, c in tris:
    for i, (m, s) in enumerate(cand):
        if m.dot(n) > 0.999:
            cand[i] = (m, s + a)
            break
    else:
        cand.append((n, a))
rows = []
for n, a in cand:
    up = (-n).normalized()
    h, base, bad, _ = report(up)
    # スロットの中に要サポート面があるか（スマホの入る空間の中の下向き面）
    Ci = fC.inverted()
    ins = 0.0
    for nn, aa, cc in tris:
        if nn.dot(up) >= -0.72:
            continue
        p = Ci @ cc
        if abs(p.x) < 0.006 and abs(p.y) < 0.078 and -0.040 < p.z < 0.038:
            ins += aa
    rows.append((base, bad, ins * 1e6, h, up))
for base, bad, ins, h, up in sorted(rows, key=lambda r: -r[0])[:6]:
    print(f"   上向き({up.x:+.2f},{up.y:+.2f},{up.z:+.2f}) 接地{base:8.0f} 要サポート{bad:8.0f}"
          f"（うちスロット内{ins:6.0f}） 高さ{h:6.1f}mm")
