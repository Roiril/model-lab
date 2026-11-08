"""手首を寄りで撮り、参考画像と並べる。

blender --background --python models/robot-hand-soft/wrist_closeup.py -- --out <png> [--res 960] [--samples 64]

参考画像（wrist-ref-x8.png）と同じく、親指の側から少し指先の側へ回り、手の甲を上にして撮る。
参考は手が左なので、描画は左右を反転して並べる（side_compare.py と同じ扱い）。
Blender で <png 名>-model.png に描画を書き、py -3.11 wrist_closeup.py --compose <png> で <png> に並べる。
参考画像が無ければ落ちる。
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)

REF = r"G:\マイドライブ\shubie\design-study\2026-11-07-robot-hand\ref\wrist-ref-x8.png"
TARGET = (0.0, 0.0, 0.024)     # 手首の中ほど [m]
VIEW_DIR = (-1.0, 0.55, 1.25)  # 手首からカメラへ向かう向き。親指の側、甲の側、指先の側
ORTHO = 0.120                          # 画面の幅 [m]
POSE = {"wrist": 22.0, "wrist_dev": 6.0}   # 手を手のひらの側へ曲げ、前腕の口と枠が甲の側から見えるようにする


def main():
    import bpy
    from mathutils import Matrix, Vector

    import model as HM
    import side_view as SV
    import studio as ST
    TGT = Vector(TARGET)
    out = ST._arg("--out", None)
    res = int(ST._arg("--res", 960))
    samples = int(ST._arg("--samples", 64))
    if not os.path.exists(REF):
        sys.exit(f"参考画像が無い: {REF}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    st = ST.setup_scene(res, samples)
    sc = bpy.context.scene
    sc.render.resolution_x = res
    sc.render.resolution_y = round(res * 800 / 752)
    st["table"].hide_render = True
    st["wall"].hide_render = True
    bg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[1].default_value = 0.85
    objs, _, joints = HM.build_hand()
    pose = SV.pointing_pose()
    pose.update(POSE)
    for name, v in pose.items():
        ob, axis, base = joints[name]
        ob.rotation_euler[axis] = base[axis] + math.radians(v)
    bpy.context.view_layer.update()
    cam = st["cam"]
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ORTHO
    cam.data.sensor_fit = "HORIZONTAL"
    d = Vector(VIEW_DIR).normalized()
    fwd = -d
    up = (Vector((0, 1, 0)) - fwd * fwd.dot(Vector((0, 1, 0)))).normalized()
    m = Matrix((fwd.cross(up), up, -fwd)).transposed().to_4x4()
    m.translation = TGT + d * 1.0
    cam.matrix_world = m
    st["light"].location = TGT + Vector((-0.5, 0.6, 0.4))
    st["light"].rotation_euler = (TGT - st["light"].location).to_track_quat("-Z", "Y").to_euler()
    st["light"].data.energy = 6.0
    model_png = out.replace(".png", "-model.png")
    ST.render_still(model_png)
    print("寄り:", model_png)


def compose(model_png, out):
    """参考（左）と、左右を反転したモデル（右）を同じ大きさで並べる。部品の名前を画像の上に書く。"""
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    ref = Image.open(REF).convert("RGB")
    mod = ImageOps.mirror(Image.open(model_png).convert("RGB")).resize(ref.size, Image.LANCZOS)
    pad, head = 16, 56
    W = ref.width * 2 + pad * 3
    H = ref.height + head + pad
    img = Image.new("RGB", (W, H), (250, 250, 250))
    img.paste(ref, (pad, head))
    img.paste(mod, (pad * 2 + ref.width, head))
    font = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 24)
    d = ImageDraw.Draw(img)
    d.text((pad, 12), "参考（8 倍）", fill=(20, 20, 20), font=font)
    d.text((pad * 2 + ref.width, 12), "モデル（左右反転）", fill=(20, 20, 20), font=font)
    img.save(out)


if __name__ == "__main__":
    if "--compose" in sys.argv:      # py -3.11 wrist_closeup.py --compose <png>（Blender の Python には PIL が無い）
        out = sys.argv[sys.argv.index("--compose") + 1]
        compose(out.replace(".png", "-model.png"), out)
        print("並べた:", out)
    else:
        main()
