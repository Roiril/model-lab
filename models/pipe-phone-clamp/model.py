# Φ28 パイプ用 Pixel 7a ホルダー — 印刷用の STL を部品ごとに書き出す（ヘッドレス）
#
#   ./run.sh models/pipe-phone-clamp/model.py
#
# 据え付けた姿勢のまま組み、部品ごとに「その向きで印刷する」向きへ倒してから焼く。
# どの向きにするかは下向き面の面積を測って選んだ（UPS の値がその向き）。
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from mathutils import Vector

from blender_utils import clear_scene, export_stl
import params as P
import mount as M

clear_scene()
coll = bpy.context.scene.collection

fC, fK, arm_len = M.frames(P.PHONE_CENTER, P.PLATE_EULER_DEG, P.RAIL_POINT, P.RAIL_DIR)
fR, fQ = M.corner_frames()

parts = [M.build_corner(coll, fR, fQ, fC),
         M.build_corner_strap(coll, fR, fQ),
         M.build_cradle(coll, fC)]

# 造形板へ向ける向き（この向きの「上」を +Z にして寝かせる）。
# 角の 2 部品は共通の分割面を伏せる。2 本ぶんの樋が上を向き、天井は切妻なので支持材が要らない。
UPS = {"M_corner": Vector((1, 0, 0)),
       "M_corner_strap": Vector((-1, 0, 0)),
       "M_cradle": fC.to_3x3() @ Vector((0, 0, 1))}   # 差し込み口を上に立てる

print("\n=== 部品（この向きのまま STL にしてある） ===")
for ob in parts:
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = UPS[ob.name].to_track_quat("Z", "Y").inverted()
    bpy.context.view_layer.update()
    # ローカル bbox の角を回した AABB は実際より大きく出る。頂点から直に測る
    cs = [ob.matrix_world @ v.co for v in ob.data.vertices]
    lo = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
    hi = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
    ob.location = ob.location + Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))
    bpy.context.view_layer.update()
    s = M.stats(ob)
    print(f"{ob.name:14s} 造形板 {hi.x - lo.x:.3f} x {hi.y - lo.y:.3f} m / 高さ {(hi.z - lo.z) * 1000:5.1f}mm"
          f"  体積 {s['vol_cm3']:6.1f}cm3  非多様体 {s['nonmani']}  殻 {s['shells']}")
    export_stl(f"pipe-phone-clamp_{ob.name[2:]}", only=[ob])

print("\nねじ: M4×16 を 6 本、M4 ナットを 6 個")
print("  角のジョイント 4 本（レール 2・柱 2）/ ポケット 2 本")

# ビューワー用に 6 部品を並べた 1 枚
y = 0.0
for ob in parts:
    # ローカル bbox の角を回した AABB は実際より大きく出る。頂点から直に測る
    cs = [ob.matrix_world @ v.co for v in ob.data.vertices]
    lo = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
    hi = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
    ob.location = ob.location + Vector((0.0, y - lo.y, 0.0))
    bpy.context.view_layer.update()
    y += (hi.y - lo.y) + 0.010
export_stl("pipe-phone-clamp")
print(f"並べた全幅 {y * 1000:.0f}mm（ビューワー用。造形板には 1 個ずつ載せる）")
