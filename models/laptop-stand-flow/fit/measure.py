"""書き出した1脚のSTLを、参考画像のカメラから描いて、左の脚の輪郭と比べる。
  blender --background --python measure.py -- <stl> <out_prefix>
結果は out_prefix_mask.npz（モデルの輪郭）と標準出力の数字。
"""
import json, os, sys
import numpy as np
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import view_warp as VW

W, H = 1536, 1024
stl, prefix = sys.argv[sys.argv.index("--") + 1:][:2]
cam = json.load(open(os.path.join(HERE, "camera_left.json")))["params"]
cam = dict(az=cam[0], el=cam[1], roll=cam[2], dist=float(np.exp(cam[3])), f=float(np.exp(cam[4])), cx=cam[5], cy=cam[6])
offset = json.load(open(os.path.join(HERE, "unit_offset.json")))["x"]
tgt = np.load(os.path.join(HERE, "left_target.npz"))
target, care = tgt["target"], tgt["care"]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=stl)
ob = bpy.context.object
ob.location = (offset, 0, 0)          # 書き出し時に X を中心へ寄せた分を戻す
scene = bpy.context.scene
cd = bpy.data.cameras.new("c")
cd.sensor_fit, cd.sensor_width = "HORIZONTAL", 36.0
cd.lens = cam["f"] * 36.0 / W
cd.shift_x = -(cam["cx"] - W / 2) / W
cd.shift_y = (cam["cy"] - H / 2) / W
cd.clip_start, cd.clip_end = 10.0, 20000.0
co = bpy.data.objects.new("c", cd)
scene.collection.objects.link(co)
pos, fwd, right, up = VW.basis(cam)
rot = Matrix(((right[0], up[0], -fwd[0]), (right[1], up[1], -fwd[1]), (right[2], up[2], -fwd[2])))
co.matrix_world = Matrix.Translation(Vector(pos)) @ rot.to_4x4()
scene.camera = co
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = W, H, 100
scene.render.image_settings.file_format, scene.render.image_settings.color_mode = "PNG", "RGB"
scene.view_settings.view_transform = "Standard"
scene.display.render_aa = "OFF"
scene.display.shading.light, scene.display.shading.color_type = "FLAT", "SINGLE"
scene.display.shading.single_color = (1, 1, 1)
scene.world = bpy.data.worlds.new("w")
scene.world.color = (0, 0, 0)
scene.render.filepath = prefix + "_sil.png"
bpy.ops.render.render(write_still=True)
img = bpy.data.images.load(prefix + "_sil.png")
px = np.empty(W * H * 4, np.float32)
img.pixels.foreach_get(px)
mask = px.reshape(H, W, 4)[::-1, :, 0] > 0.5
np.savez(prefix + "_mask.npz", mask=mask)
xor = ((mask ^ target) & care).sum()
area = (target & care).sum()
inter = (mask & target & care).sum()
union = ((mask | target) & care).sum()
print(f"MEASURE xor/area = {xor / area * 100:.2f} %   IoU = {inter / union * 100:.2f} %   (target area {area} px)")
