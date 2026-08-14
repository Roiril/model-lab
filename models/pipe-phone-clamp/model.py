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
post_xy = (P.RAIL_POINT[0], P.POST_Y)
fQ, hole_c, boss_c = M.brace_frames(post_xy, fC)

parts = [M.build_saddle(coll, fK, fC, arm_len),
         M.build_strap(coll, fK),
         M.build_cradle(coll, fC, brace=True),
         M.build_post_saddle(coll, fQ, fC, hole_c),
         M.build_strap(coll, fQ, name="M_post_strap"),
         M.build_strut(coll, fC, hole_c, boss_c)]

# 造形板へ向ける向き（この向きの「上」を +Z にして寝かせる）
MX = fC.to_3x3() @ Vector((1, 0, 0))
MZ = fC.to_3x3() @ Vector((0, 0, 1))
UPS = {"M_saddle": fK.to_3x3() @ Vector((1, 0, 0)),   # 分割面を造形板へ
       "M_strap": fK.to_3x3() @ Vector((0, 0, 1)),    # リングを寝かせる
       "M_cradle": MZ,                                # 差し込み口を上に立てる
       "M_post_saddle": -MX,                          # 棒の座面を造形板へ
       "M_post_strap": Vector((0, 0, 1)),
       "M_strut": MX}                                 # 平置き（支持材ゼロ）

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

print(f"\n腕の長さ（レール軸→合わせ面）{arm_len * 1000:.1f}mm / 片持ち {(arm_len - P.RING_R) * 1000:.1f}mm")
print(f"つっかえ棒の穴どうし {((boss_c - hole_c).length) * 1000:.1f}mm")
print("ねじ: M4×16 を 8 本、M4 ナットを 8 個")

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
