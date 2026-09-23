"""手すり接続用の上半周ビードと、上から被せる半割り袖。単位 mm。"""
import math


CLEAR = .35
BEAD_HEIGHT = 1.5
BEAD_WIDTH = 8.0
BEAD_TRANSITION = 1.5
BEAD_FLAT = 5.0
BEAD_OVERLAP = .8
BEAD_EDGE_SINK = .1
BEAD_END_FADE_DEG = 15.0

CAP_LENGTH = 24.0
CAP_OUTER_R = 22.65
CAP_INNER_R = 18.65
CAP_POCKET_R = CAP_INNER_R + BEAD_HEIGHT
CAP_END_DROP = 1.0
CAP_END_TAPER = 1.0
CAP_EDGE = .35

_MM = .001
_SEG = 48


def export_print_part(ob, exports_dir, filename):
    """既存の検証済み3MF出力を使用。印刷設定は埋め込まない。"""
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / 'models/pipe-foot-corner-split/export_3mf.py'
    spec = importlib.util.spec_from_file_location('handrail_export_3mf', path)
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    exporter.REVISION = 'handrail-20260923'
    return exporter.export_part(ob, exports_dir, filename)


def _finish(name, bm, col):
    import bpy
    import bmesh

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def build_upper_bead(name, station_frames, col, hub_r):
    """上半周だけのビードを作る。

    station_frames は ``[(高さ係数, (原点, 横, 上)), ...]``。ビードの根は
    元の外周へ0.8mm食い込ませる。左右15度は高さを線形に落とす。
    """
    import bmesh

    bm = bmesh.new()
    angles = [math.pi * i / _SEG for i in range(_SEG + 1)]
    rings = []
    for axial, (origin, side, up) in station_frames:
        inner = []
        outer = []
        for angle in angles:
            end_distance = min(angle, math.pi - angle)
            circumferential = min(1.0, end_distance / math.radians(BEAD_END_FADE_DEG))
            fade = axial * circumferential
            # 高さ0の端は面一致を避けて筒内へ沈める。外径と内径は削らない。
            outer_r = hub_r - BEAD_EDGE_SINK + (BEAD_HEIGHT + BEAD_EDGE_SINK) * fade
            inner_r = hub_r - BEAD_OVERLAP
            direction = side * math.cos(angle) + up * math.sin(angle)
            inner.append(bm.verts.new(origin + direction * (inner_r * _MM)))
            outer.append(bm.verts.new(origin + direction * (outer_r * _MM)))
        rings.append((inner, outer))

    for (inner0, outer0), (inner1, outer1) in zip(rings, rings[1:]):
        for i in range(_SEG):
            j = i + 1
            bm.faces.new((outer0[i], outer1[i], outer1[j], outer0[j]))
            bm.faces.new((inner0[j], inner1[j], inner1[i], inner0[i]))
        bm.faces.new((inner0[0], inner1[0], outer1[0], outer0[0]))
        bm.faces.new((outer0[-1], outer1[-1], inner1[-1], inner0[-1]))

    first_inner, first_outer = rings[0]
    last_inner, last_outer = rings[-1]
    for i in range(_SEG):
        bm.faces.new((first_inner[i + 1], first_outer[i + 1], first_outer[i], first_inner[i]))
        bm.faces.new((last_inner[i], last_outer[i], last_outer[i + 1], last_inner[i + 1]))
    return _finish(name, bm, col)


def bead_stations(frame_at, center):
    """幅8mm（1.5mm遷移＋5mm平頂＋1.5mm遷移）の断面列。"""
    half = BEAD_WIDTH / 2
    flat = BEAD_FLAT / 2
    return [(height, frame_at(center + offset))
            for offset, height in ((-half, 0.0), (-flat, 1.0),
                                   (flat, 1.0), (half, 0.0))]


def add_upper_bead(body, name, frame_at, center, col, boolean, hub_r):
    bead = build_upper_bead(name, bead_stations(frame_at, center), col, hub_r)
    return boolean(body, bead, 'UNION', solver='EXACT')


def _pocket_depth(x):
    """中心±6mmのビードを軸方向へ片側0.35mm広げたポケット。"""
    flat = BEAD_FLAT / 2 + CLEAR
    edge = BEAD_WIDTH / 2 + CLEAR
    depth = 0.0
    for center in (-6.0, 6.0):
        d = abs(x - center)
        if d <= flat:
            depth = max(depth, BEAD_HEIGHT)
        elif d < edge:
            depth = max(depth, BEAD_HEIGHT * (edge - d) / (edge - flat))
    return depth


def build_rail_coupler(name='pipe_rail_coupler', col=None):
    """軸をXに置いた、上180度の共通半割り袖を作る。"""
    import bpy
    import bmesh
    from mathutils import Vector

    if col is None:
        col = bpy.data.collections.get('rail_coupler')
        if col is None:
            col = bpy.data.collections.new('rail_coupler')
            bpy.context.scene.collection.children.link(col)
    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    pocket_edge = BEAD_WIDTH / 2 + CLEAR
    pocket_flat = BEAD_FLAT / 2 + CLEAR
    xs = {-CAP_LENGTH / 2, -CAP_LENGTH / 2 + CAP_END_TAPER,
          CAP_LENGTH / 2 - CAP_END_TAPER, CAP_LENGTH / 2}
    for center in (-6.0, 6.0):
        xs.update((center - pocket_edge, center - pocket_flat,
                   center + pocket_flat, center + pocket_edge))
    xs = sorted(xs)

    bm = bmesh.new()
    angles = [math.pi * i / _SEG for i in range(_SEG + 1)]
    rings = []
    for x in xs:
        edge_d = min(x + CAP_LENGTH / 2, CAP_LENGTH / 2 - x)
        edge_factor = min(1.0, max(0.0, edge_d / CAP_END_TAPER))
        outer_r = CAP_OUTER_R - CAP_END_DROP * (1.0 - edge_factor)
        inner_r = CAP_INNER_R + _pocket_depth(x)
        inner = [bm.verts.new(Vector((x, inner_r * math.cos(a), inner_r * math.sin(a))) * _MM)
                 for a in angles]
        outer = [bm.verts.new(Vector((x, outer_r * math.cos(a), outer_r * math.sin(a))) * _MM)
                 for a in angles]
        rings.append((inner, outer))

    for (inner0, outer0), (inner1, outer1) in zip(rings, rings[1:]):
        for i in range(_SEG):
            j = i + 1
            bm.faces.new((outer0[i], outer1[i], outer1[j], outer0[j]))
            bm.faces.new((inner0[j], inner1[j], inner1[i], inner0[i]))
        bm.faces.new((inner0[0], inner1[0], outer1[0], outer0[0]))
        bm.faces.new((outer0[-1], outer1[-1], inner1[-1], inner0[-1]))
    first_inner, first_outer = rings[0]
    last_inner, last_outer = rings[-1]
    for i in range(_SEG):
        bm.faces.new((first_inner[i + 1], first_outer[i + 1], first_outer[i], first_inner[i]))
        bm.faces.new((last_inner[i], last_outer[i], last_outer[i + 1], last_inner[i + 1]))

    ob = _finish(name, bm, col)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bevel = ob.modifiers.new('soft_touch_edges', 'BEVEL')
    bevel.width = CAP_EDGE * _MM
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(30)
    bevel.use_clamp_overlap = True
    bpy.ops.object.modifier_apply(modifier=bevel.name)

    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-8)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-9)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    assert all(edge.is_manifold for edge in bm.edges), 'coupler mesh must be closed'
    bm.to_mesh(ob.data)
    bm.free()
    bpy.ops.object.shade_flat()
    return ob
