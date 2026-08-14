# 差し込み側が実績のある exports/pixel7a-stand.stl と同じ形か、光線で突き合わせる。
#
#   ./run.sh models/pipe-phone-clamp/compare_stand.py
#
# 両方を「斜面座標 (s, h, x)」へ揃えて同じ格子を撃つ。s は斜面を上る向き、h は外向き
# 法線（h=0 が外皮の外表面）、x はスマホの長辺方向。スタンドは 75°、こちらは 45° で
# 世界での姿勢は違うが、この座標で見れば同じ形でなければならない。
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from mathutils import Vector, Matrix

from blender_utils import clear_scene
import params as P
import mount as M

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_STL = os.path.join(BASE, "exports", "pixel7a-stand.stl")

clear_scene()
coll = bpy.context.scene.collection

# --- 基準: 実機で入ることを確認済みの STL ---------------------------------
ref = {}
exec(open(os.path.join(BASE, "models", "pixel7a-stand", "params.py"), encoding="utf-8").read(), ref)
bpy.ops.wm.stl_import(filepath=REF_STL)
stand = bpy.context.selected_objects[0]
stand.scale = (0.001, 0.001, 0.001)          # STL は 1000 倍で書かれている
bpy.context.view_layer.update()

A = math.radians(ref["TILT_DEG"])
UY, UZ = math.cos(A), math.sin(A)
NY, NZ = -math.sin(A), math.cos(A)
BASE_Y = -ref["STAND_D"] / 2
BASE_Z = ref["FRONT_H"]


def sp_ref(s, h, x):
    return Vector((x, BASE_Y + s * UY + h * NY, BASE_Z + s * UZ + h * NZ))


# --- こちらのポケット（C 座標で組む。s = z + S_MID, h = x - X_FRONT） ------
cradle = M.build_cradle(coll, Matrix.Identity(4))


def sp_new(s, h, x):
    return Vector((P.X_FRONT + h, x, s - P.S_MID))


def probe(ob, sp, s, x):
    """外側から h を減らす向きに撃ち、最初に当たった h を返す（当たらなければ None）。"""
    o = sp(s, 0.030, x)
    d = (sp(s, -1.0, x) - sp(s, 0.0, x)).normalized()
    ok, loc, nor, idx = ob.ray_cast(ob.matrix_world.inverted() @ o, d)
    if not ok:
        return None
    w = ob.matrix_world @ loc
    return (w - sp(s, 0.0, x)).dot(d) * -1000.0     # mm、外表面を 0 として内向きが負


def cls(h):
    if h is None:
        return " "
    if h > -0.5:
        return "#"          # 外皮がある
    if h > -6.0:
        return "+"          # 少し窪んでいる（テーパー）
    if h > -13.0:
        return "="          # 外皮が抜けている（カメラ窓）
    return "-"              # 表裏とも抜けている（指がかり）


NS, NX = 24, 68
rows_r, rows_n, diff = [], [], 0
for i in range(NS):
    s = ref["SLOPE_LEN"] * (NS - 0.5 - i) / NS
    r, n = "", ""
    for j in range(NX):
        x = -0.085 + 0.170 * j / (NX - 1)
        cr_ = cls(probe(stand, sp_ref, s, x))
        cn_ = cls(probe(cradle, sp_new, s, x))
        r += cr_
        n += cn_
        if cr_ != cn_:
            diff += 1
    rows_r.append((s, r))
    rows_n.append((s, n))

print("\n■ 基準 exports/pixel7a-stand.stl        ■ こちら M_cradle")
print("   # 外皮 / + テーパー / = カメラ窓 / - 表裏抜け（指がかり）/ 空白 材料なし")
for (s, r), (_, n) in zip(rows_r, rows_n):
    print(f" s={s*1000:5.1f} |{r}|  |{n}|")
print(f"\n食い違った升目: {diff} / {NS * NX}")

def skin(ob, sp, s, x):
    """外皮の厚み（外表面から内面まで）を撃って測る。テーパーが効いていれば入口で薄くなる。"""
    d = (sp(s, -1.0, x) - sp(s, 0.0, x)).normalized()
    o = ob.matrix_world.inverted() @ sp(s, 0.030, x)
    hs = []
    for _ in range(4):
        ok, loc, nor, idx = ob.ray_cast(o, d)
        if not ok:
            break
        w = ob.matrix_world @ loc
        hs.append((w - sp(s, 0.0, x)).dot(d) * -1000.0)
        o = loc + d * 2e-5
    return hs[1] - hs[0] if len(hs) >= 2 else None


print("\n■ 外皮の厚み（x=-30mm。指がかりとカメラ窓を外した所。入口で薄くなるはず）")
for s in (0.050, 0.060, 0.066, 0.070, 0.074, 0.0778):
    a = skin(stand, sp_ref, s, -0.030)
    b = skin(cradle, sp_new, s, -0.030)
    fa = f"{-a:5.2f}" if a is not None else "   -- "
    fb = f"{-b:5.2f}" if b is not None else "   -- "
    print(f"  s={s*1000:5.1f}mm  基準 {fa}mm / こちら {fb}mm")

print("\n■ 寸法の突き合わせ（左が基準 params、右がこちら）")
for k in ("SLOT_L", "SLOT_W", "SLOT_T", "FRONT_SKIN", "BACK_PLATE", "SIDE_WALL", "STOPPER",
          "SLOPE_LEN", "CAM_EDGE_RIM", "CAM_WIN_L", "TAPER_S0", "TAPER_LEN", "TAPER_D",
          "GRIP_W", "GRIP_S0", "USB_W", "USB_S", "CLR_L", "CLR_W", "CLR_T"):
    a, b = ref[k], getattr(P, k)
    mark = "  " if abs(a - b) < 1e-9 else "<-- 違う"
    print(f"  {k:13s} {a*1000:8.2f} / {b*1000:8.2f} mm {mark}")
