"""SO-101 の部品への手直し。Studio の依頼はここに書き足す。

`apply(parts)` は組み立てる前に呼ばれる。`parts` は部品 id → Blender オブジェクト。
メッシュは部品自身の座標（URDF の visual 座標を当てる前、単位 m）なので、
寸法は部品の元の STL と同じ軸で考えればよい。

例（上腕に直径 5mm の穴を足す）:

    import bpy
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0025, depth=0.03, location=(0.0, 0.01, 0.0))
    cutter = bpy.context.active_object
    mod = parts["upper-arm"].modifiers.new("hole", "BOOLEAN")
    mod.operation, mod.object = "DIFFERENCE", cutter
    bpy.context.view_layer.objects.active = parts["upper-arm"]
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return ["上腕に直径 5mm の穴"]

手直しが無い間は何もしない。元の形のまま書き出される。
"""


def apply(parts):
    return []          # 手直しの一覧（manifest に記録する）。今は無し
