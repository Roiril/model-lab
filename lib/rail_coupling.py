"""手すりの位置決め。単位 mm。抜け止めはテープに任せる。"""

DEPTH = 6.0
CLEAR = .25
INNER_R = 15.75             # 受けの内端15.5と内径半径14.3の間に1.2残す
OUTER_R = 18.05
HALF_H = 2.0
ROUND = .5
INNER_L = 5.3
OUTER_L = 5.5


def export_print_part(ob, exports_dir, filename):
    """既存の検証済み3MF出力を使用。印刷設定は埋め込まない。"""
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / 'models/pipe-foot-corner-split/export_3mf.py'
    spec = importlib.util.spec_from_file_location('handrail_export_3mf', path)
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    exporter.REVISION = 'handrail-20260922'
    return exporter.export_part(ob, exports_dir, filename)


def cut_receivers(body, col, boolean, x_face, side_y, side_z):
    """外側へ開いた短い受け。4箇所とも同寸法。M字の内径は削らない。"""
    import bpy
    from mathutils import Vector

    inner = INNER_R - CLEAR
    outer = 20.0
    for sy in (-side_y, side_y):
        for sign in (-1, 1):
            bpy.ops.mesh.primitive_cube_add(size=1)
            ob = bpy.context.object
            ob.name = 'rail_location_socket'
            ob.location = Vector((x_face + (DEPTH - 1) / 2,
                                  sy + sign * (inner + outer) / 2, side_z)) * .001
            ob.dimensions = Vector((DEPTH + 1, outer - inner, 2 * (HALF_H + CLEAR))) * .001
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            # 受け内隅は舌より大きな角丸。片側0.25の隙間を全周で保つ。
            mod = ob.modifiers.new('rounded_receiver', 'BEVEL')
            mod.width = (ROUND + CLEAR) * .001
            mod.segments = 4
            bpy.ops.object.modifier_apply(modifier=mod.name)
            boolean(body, ob, 'DIFFERENCE', solver='EXACT')
    return body
