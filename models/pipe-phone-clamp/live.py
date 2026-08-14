# 起動中の Blender（MCP 経由）へ、既存のブースを壊さずにホルダーを据え付ける。
#
#   exec(open(r"...\models\pipe-phone-clamp\live.py", encoding="utf-8").read())
#
# 触るのは phone_mount コレクションの中だけ。ユーザーが手で置いた物は消さない。
import sys
import os
import importlib

BASE = r"C:\Users\kouga\Projects\Web\model-lab"
MODEL_DIR = os.path.join(BASE, "models", "pipe-phone-clamp")
for p in (MODEL_DIR, os.path.join(BASE, "lib")):
    if p not in sys.path:
        sys.path.insert(0, p)
for m in ("params", "mount"):
    if m in sys.modules:
        del sys.modules[m]

import bpy
import bmesh
from mathutils import Vector

import params as P
import mount as M

COLL = "phone_mount"


def _volume(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    v = bm.calc_volume(signed=True)
    bm.free()
    return v


def _wbb(ob):
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return (Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs))),
            Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs))))


def _overlap(a, b, pad=0.002):
    a0, a1 = _wbb(a)
    b0, b1 = _wbb(b)
    return all(a0[i] - pad <= b1[i] and b0[i] - pad <= a1[i] for i in range(3))


def _intersect_cm3(a, b, coll):
    tmp = a.copy()
    tmp.data = a.data.copy()
    coll.objects.link(tmp)
    mod = tmp.modifiers.new("i", "BOOLEAN")
    mod.operation = "INTERSECT"
    mod.solver = "EXACT"
    mod.object = b
    M._bake(tmp)
    v = _volume(tmp) * 1e6
    me = tmp.data
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.meshes.remove(me)
    return v


# --- 据え付ける姿勢を実物から読む ------------------------------------------
plate = bpy.data.objects.get("Cube.005")
if plate is not None:
    center = tuple(plate.matrix_world.translation)
    euler = tuple(a * 57.2957795 for a in plate.rotation_euler)
    src = "Cube.005（ユーザーが置いた板）"
else:
    center, euler, src = P.PHONE_CENTER, P.PLATE_EULER_DEG, "params.py の控え"

rail = bpy.data.objects.get("P_rail_B")
if rail is not None:
    r0, r1 = _wbb(rail)
    ext = [r1[i] - r0[i] for i in range(3)]
    ax = ext.index(max(ext))                      # いちばん長い辺がパイプ軸
    pipe_dir = tuple(1.0 if i == ax else 0.0 for i in range(3))
    ctr = (r0 + r1) / 2
    pipe_pt = tuple(ctr)
    rail_src = f"P_rail_B（軸 {'xyz'[ax]}、半径 {min(ext) * 500:.1f}mm）"
else:
    pipe_pt, pipe_dir, rail_src = P.RAIL_POINT, P.RAIL_DIR, "params.py の控え"

print(f"[pose] {src}: center_mm={tuple(round(v * 1000, 1) for v in center)} euler_deg={tuple(round(v, 1) for v in euler)}")
print(f"[pipe] {rail_src}: pt_mm={tuple(round(v * 1000, 1) for v in pipe_pt)} dir={pipe_dir}")

post = bpy.data.objects.get("P_post_3_hi")
if post is not None:
    q0, q1 = _wbb(post)
    post_xy = ((q0.x + q1.x) / 2, (q0.y + q1.y) / 2)
else:
    post_xy = (0.480, -0.955)

fC, fK, arm_len = M.frames(center, euler, pipe_pt, pipe_dir)
print(f"[frame] 腕の長さ（パイプ軸→合わせ面）= {arm_len * 1000:.1f}mm / "
      f"リング外まで {(arm_len - P.RING_R) * 1000:.1f}mm が片持ち")

fQ, hole_c, boss_c = M.brace_frames(post_xy, fC)
hw = fC @ hole_c
print(f"[brace] 柱のリングの高さ z={hw.z*1000:.1f}mm（レールの {(pipe_pt[2]-hw.z)*1000:.0f}mm 下）"
      f" / 柱の軸から水平 {P.POST_HOLE_R*1000:.0f}mm")
print(f"        棒の穴どうしの距離 {((boss_c - hole_c).length)*1000:.1f}mm（1 枚の平板）")

# --- 自分の作った物だけ消して作り直す --------------------------------------
coll = bpy.data.collections.get(COLL)
if coll is None:
    coll = bpy.data.collections.new(COLL)
    bpy.context.scene.collection.children.link(coll)
for ob in list(coll.objects):
    me = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    if getattr(me, "users", 1) == 0:
        bpy.data.meshes.remove(me)

parts = [M.build_saddle(coll, fK, fC, arm_len),
         M.build_strap(coll, fK),
         M.build_cradle(coll, fC, brace=True),
         M.build_post_saddle(coll, fQ, fC, hole_c),
         M.build_strap(coll, fQ, name="M_post_strap"),
         M.build_strut(coll, fC, hole_c, boss_c)]

# 実機と同じ寸法の箱を、スロットの底へ着くまで差し込んだ位置に置く。見た目の確認と
# 「本当に入るのか」の検算を兼ねる（部品ではないので STL には出さない）
phone = M._box("REF_phone", fC, (0, 0, -P.SLOT_W / 2 + P.PHONE_W / 2 + P.CLR_W),
               (P.PHONE_T, P.PHONE_L, P.PHONE_W), coll)

# --- 見た目（パイプは青。部品は黒くして区別する） ---------------------------
GRAY = (0.62, 0.60, 0.56, 1.0)   # 灰色。黒くするとソリッド表示で面の陰影が読めなくなる
mat = bpy.data.materials.get("M_mount")
if mat is None:
    mat = bpy.data.materials.new("M_mount")
    mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.use_nodes else None
if bsdf:
    bsdf.inputs["Base Color"].default_value = GRAY
    bsdf.inputs["Roughness"].default_value = 0.55
mat.diffuse_color = GRAY
for ob in parts:
    ob.data.materials.clear()
    ob.data.materials.append(mat)

pmat = bpy.data.materials.get("M_phone") or bpy.data.materials.new("M_phone")
pmat.diffuse_color = (0.02, 0.02, 0.025, 1.0)
phone.data.materials.clear()
phone.data.materials.append(pmat)

print(f"\n[検算] Pixel 7a 実寸の箱 ∩ ポケット = {_intersect_cm3(phone, parts[2], coll):.4f} cm3"
      f"（0 でなければ入らない）")

# --- 検査 -------------------------------------------------------------------
print("\n[部品]")
for ob in parts:
    s = M.stats(ob)
    print(f"  {s['name']:10s} 体積 {s['vol_cm3']:6.1f}cm3  非多様体エッジ {s['nonmani']}"
          f"  浮き頂点 {s['loose']}  殻 {s['shells']}（1 以外なら内部に壁）")

skip = {"Cube", "Cube.001", "Cube.002", "Cube.003", "Cube.004", "Cylinder",
        "Cylinder.001", "Cylinder.002", "Cylinder.003", "Cylinder.004",
        "Plane", "Plane.001", "Cube.005", "Cube.006", "Cube.007"}   # 005/006/007 は下書き
print("\n[ブースとの干渉（交差体積。0 以外は当たっている）]")
hit = 0
for ob in parts:
    for other in bpy.data.objects:
        if other.type != "MESH" or other.name in skip or other.name in coll.objects:
            continue
        if not _overlap(ob, other):
            continue
        v = _intersect_cm3(ob, other, coll)
        if v > 1e-4:
            hit += 1
            print(f"  !! {ob.name} x {other.name}: {v:.3f} cm3")
        else:
            print(f"  ok {ob.name} x {other.name}: 0")
if hit == 0:
    print("  当たりなし")

# --- パイプとの隙間（ボアは片側 0.3mm のはず） ------------------------------
def _min_r(ob, p0, d):
    d = Vector(d).normalized()
    return min((((ob.matrix_world @ v.co) - Vector(p0))
                - d * (((ob.matrix_world @ v.co) - Vector(p0)).dot(d))).length
               for v in ob.data.vertices)


print("\n[パイプまでの最短距離（外周は 14.00mm。抱く部品は 14.28mm が正解）]")
axes = (("レール", pipe_pt, pipe_dir), ("柱", (post_xy[0], post_xy[1], 0.0), (0, 0, 1)))
for ob in parts:
    s = "  ".join(f"{nm} {_min_r(ob, p, d) * 1000:6.2f}mm" for nm, p, d in axes)
    print(f"  {ob.name:14s} {s}")

# 継手（ユーザー実測: 角から横 80mm・縦 50mm）を避けられているか
corner_y = post_xy[1]
z_free = pipe_pt[2] - P.JOINT_ALONG_POST          # 柱側で自由になる高さ
y_free = corner_y + P.JOINT_ALONG_RAIL            # レール側で自由になる位置
print(f"\n[継手の回避] 柱は z<{z_free*1000:.1f}mm、レールは y>{y_free*1000:.1f}mm が自由")
for ob in parts:
    ws = [ob.matrix_world @ v.co for v in ob.data.vertices]
    near_post = [w for w in ws if ((w.x - post_xy[0]) ** 2 + (w.y - corner_y) ** 2) ** 0.5 < 0.045]
    if near_post:
        print(f"  {ob.name:14s} 柱まわり半径45mm 内の最高点 z={max(w.z for w in near_post)*1000:7.1f}mm"
              f"（{(z_free - max(w.z for w in near_post))*1000:+.1f}mm の余裕）")
    near_rail = [w for w in ws if abs(w.x - pipe_pt[0]) < 0.045 and abs(w.z - pipe_pt[2]) < 0.045]
    if near_rail:
        print(f"  {ob.name:14s} レールまわり半径45mm 内の最も角寄り y={min(w.y for w in near_rail)*1000:7.1f}mm"
              f"（{(min(w.y for w in near_rail) - y_free)*1000:+.1f}mm の余裕）")

# --- 旧版と下書きの板は目障りなので隠す（消してはいない。Alt+H で戻る） -----
for n in ("Cube.005", "Cube.006"):
    ob = bpy.data.objects.get(n)
    if ob:
        ob.hide_set(True)
print("\n[表示] Cube.005（下書きの板）と Cube.006（前スレッドの版）を隠した。Alt+H で戻る")
print("done")
