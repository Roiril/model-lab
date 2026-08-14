# Φ28 パイプ用 Pixel 7a ホルダー — 印刷用の STL を部品ごとに書き出す（ヘッドレス）
#
#   ./run.sh models/pipe-phone-clamp/model.py
#
# 据え付けた姿勢のまま焼くのではなく、部品ごとに「その向きで印刷する」座標系で組む。
# K（クランプ）は z がパイプ軸、C（ポケット）は z がスロットを上る向き。どちらも
# その z を上にして置くと、支持材の要る面が 1 つも無い。
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from mathutils import Matrix, Vector

from blender_utils import clear_scene, export_stl
import params as P
import mount as M

clear_scene()
coll = bpy.context.scene.collection

C, K, arm_len = M.frames(P.PHONE_CENTER, P.PLATE_EULER_DEG, P.RAIL_POINT, P.RAIL_DIR)
I = Matrix.Identity(4)

saddle = M.build_saddle(coll, I, K.inverted() @ C, arm_len)   # 腕とパッドだけ C 座標
strap = M.build_strap(coll, I)
cradle = M.build_cradle(coll, I)

# saddle だけは組んだ座標のまま置くと、腕の先のパッドがリングより下へ出る。
# 下向き面の面積を 4 通り測って比べたところ、分割面（パイプを抱く合わせ面）を
# 造形板へ伏せる向きが最も少なかった（629mm2。リングを寝かせると 2305mm2）。
# この向きだと耳のナット座が真上を向くので、ナットを落とし込むだけで入る。
saddle.rotation_euler = (0.0, -1.5707963, 0.0)
bpy.context.view_layer.update()

print("\n=== 部品（この向きのまま STL にしてある） ===")
for ob in (saddle, strap, cradle):
    s = M.stats(ob)
    print(f"{ob.name:10s} 造形板 {s['dim_mm'][0]:6.1f} x {s['dim_mm'][1]:6.1f} mm / 高さ {s['dim_mm'][2]:5.1f} mm"
          f"  体積 {s['vol_cm3']:6.1f}cm3  非多様体 {s['nonmani']}  殻 {s['shells']}")
print(f"\n腕の長さ（パイプ軸→合わせ面）{arm_len*1000:.1f}mm / 片持ち {(arm_len-P.RING_R)*1000:.1f}mm")
print("ねじ: M4×16 を 4 本、M4 ナットを 4 個")

export_stl("pipe-phone-clamp_saddle", only=[saddle])
export_stl("pipe-phone-clamp_strap", only=[strap])
export_stl("pipe-phone-clamp_cradle", only=[cradle])

# ビューワー用に 3 部品を並べた 1 枚。造形板へ載せる向き・並びのまま
y = 0.0
for ob in (cradle, saddle, strap):
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    lo = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
    hi = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
    ob.location = ob.location + Vector((-(lo.x + hi.x) / 2, y - lo.y, -lo.z))
    bpy.context.view_layer.update()
    y += (hi.y - lo.y) + 0.010
export_stl("pipe-phone-clamp")
print(f"\n造形板の占有: 幅 {y*1000:.0f}mm 方向に 3 部品を 10mm 空けて並べた")
