"""直線の壁の端で、M 字ジョイントの脚 2 本と中央レールを受ける 3 本目の柱を床で受けるベース。

    ./run.sh models/pipe-foot-pair/model.py

形は lib/pair_base.build()。角用（pipe-foot-corner）も同じ関数で出す。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

from blender_utils import clear_scene, EXPORTS_DIR
import pair_base
import params

clear_scene()
body = pair_base.build(params, "pipe_foot_pair", params.THIRD_OFF)
pair_base.export(body, EXPORTS_DIR, "pipe_foot_pair.stl")
