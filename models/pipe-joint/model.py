import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from mathutils import Matrix, Vector
from blender_utils import clear_scene, EXPORTS_DIR
import joint

clear_scene()
body = joint.build_all(ref=False)


def export(ob, name):
    path = os.path.join(EXPORTS_DIR, name + ".stl")
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True, global_scale=1000.0)
    print("Exported:", path)
    print("  bbox mm:", [round(v * 1000, 2) for v in ob.dimensions])
    return path


os.makedirs(EXPORTS_DIR, exist_ok=True)
export(body, "pipe_joint_28")

# --- スライサーへ渡す向き ------------------------------------------------
# 設計は +X を上にして刷る前提。分割面（平らな -X 端）を造形板へ伏せると、
# レールの穴も脚の穴も「上を向いた樋」になるので支持材が要らない。
# そのままだと寝ているので、+X が +Z を向くよう倒し、底を z=0 に載せる。
pr = body.copy()
pr.data = body.data.copy()
pr.name = "pipe_joint_28_print"
bpy.context.scene.collection.objects.link(pr)
pr.matrix_world = Matrix.Rotation(math.radians(-90), 4, "Y")
bpy.context.view_layer.update()
zs = [(pr.matrix_world @ Vector(c)).z for c in pr.bound_box]
pr.matrix_world = Matrix.Translation((0, 0, -min(zs))) @ pr.matrix_world
export(pr, "pipe_joint_28_print")
