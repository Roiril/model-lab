"""角の床側の部品 3 つ: 板 A（脚 2 本 + 5 本目）、板 B（脚 2 本）、添え板。

    ./run.sh models/pipe-foot-corner/model.py

板の形は lib/pair_base.build()（pipe-foot-pair と同じ）。
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from mathutils import Matrix
from blender_utils import clear_scene, EXPORTS_DIR
import foot_core as fc
import pair_base
from params import PAIR as P, FIFTH_OFF, TIE_L, TIE_RING_ID, TIE_RING_R, TIE_T, TIE_SLOT, TIE_CHAMFER

SEG = P.SEG


def build_tie():
    """添え板。2 つの輪（内径 TIE_RING_ID）を幅 2*TIE_RING_R の帯でつないだ長丸の板。
    片側の穴は長手に ±TIE_SLOT の長穴。穴の口は上側に TIE_CHAMFER の面取り（かぶせる時のリード）。

    穴と面取りは 1 つの回転体（下は r、上端で r+ch）で切る。長穴は中心を ±TIE_SLOT にずらした
    回転体 2 つと、そのあいだを埋める台形の押し出しで作る。
    """
    c0, c1 = (0.0, 0.0), (TIE_L, 0.0)
    body = fc.prism("pipe_foot_corner_tie", fc.hull_poly([c0, c1], TIE_RING_R, SEG), 0.0, TIE_T)
    r, ch = TIE_RING_ID / 2, TIE_CHAMFER
    prof = [(-1.0, r), (TIE_T - ch, r), (TIE_T + 0.5, r + ch + 0.5)]
    fc.boolean(body, fc.revolve("hole0", prof, fc.translate(*c0), SEG), "DIFFERENCE")
    for dx in (-TIE_SLOT, TIE_SLOT):
        fc.boolean(body, fc.revolve("hole1", prof, fc.translate(c1[0] + dx, 0.0), SEG), "DIFFERENCE")
    # 長穴の中央部: 断面 (y, z) の台形を x 方向へ押し出す。lib の prism は (x, y) を z へ
    # 押し出すので、行列で回して置く
    poly = [(-r, -1.0), (r, -1.0), (r, TIE_T - ch), (r + ch + 0.5, TIE_T + 0.5),
            (-(r + ch + 0.5), TIE_T + 0.5), (-r, TIE_T - ch)]
    m = (fc.translate(c1[0], 0.0) @ Matrix.Rotation(math.radians(90), 4, "Z")
         @ Matrix.Rotation(math.radians(90), 4, "X"))
    fc.boolean(body, fc.prism("hole1m", poly, -TIE_SLOT, TIE_SLOT, m), "DIFFERENCE")
    fc.clean(body, dist=2e-5)
    fc.activate(body)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.shade_flat()
    return body


clear_scene()
pair_base.export(pair_base.build(P, "pipe_foot_corner_a", FIFTH_OFF), EXPORTS_DIR, "pipe_foot_corner_a.stl")

clear_scene()
pair_base.export(pair_base.build(P, "pipe_foot_corner_b", None), EXPORTS_DIR, "pipe_foot_corner_b.stl")

clear_scene()
pair_base.export(build_tie(), EXPORTS_DIR, "pipe_foot_corner_tie.stl")
