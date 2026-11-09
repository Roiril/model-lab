"""寸法図（正面・側面の正射影）と同じ向き・縮尺でモデルを描く。

blender --background --python models/hiwonder-uhand/ortho.py -- --out DIR [--mmpx 0.16]
  dwg_front.png: 手のひら側（-Y）から。+X（親指側）が右
  dwg_side.png : 親指側（+X）から。手のひら（-Y）が左
画素は mmpx [mm/px]。各画像の左上は (x or y, z) = (MIN, ZTOP) [mm] に固定し、ortho_cmp.py が図に重ねる。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))
sys.path.insert(0, HERE)
os.environ["UHAND_NO_EXPORT"] = "1"

import bpy
from mathutils import Vector

import model as HM

# 描く範囲 [mm]（モデル座標。縮尺を変えても枠は同じ）
FRAME = dict(h0=-110.0, h1=170.0, z0=-40.0, z1=200.0)


def main():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = a[a.index("--out") + 1] if "--out" in a else os.path.join(HERE, "_renders")
    mmpx = float(a[a.index("--mmpx") + 1]) if "--mmpx" in a else 0.16
    os.makedirs(out, exist_ok=True)
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "FLAT"
    sh.color_type = "SINGLE"
    sh.single_color = (1, 1, 1)
    sh.show_object_outline = True
    sh.object_outline_color = (0, 0, 0)
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = "RGBA"
    sh.show_cavity = True
    sh.cavity_type = "SCREEN"
    sh.curvature_ridge_factor = 0.0
    sh.curvature_valley_factor = 2.0
    sc.view_settings.view_transform = "Standard"
    HM.build()
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cd.clip_end = 10.0
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    f = FRAME
    w, h = f["h1"] - f["h0"], f["z1"] - f["z0"]
    sc.render.resolution_x, sc.render.resolution_y = round(w / mmpx), round(h / mmpx)
    cd.sensor_fit = "HORIZONTAL"
    cd.ortho_scale = w * 0.001
    hc, zc = (f["h0"] + f["h1"]) / 2 * 0.001, (f["z0"] + f["z1"]) / 2 * 0.001
    for name, loc, look in (("dwg_front", (hc, -1.0, zc), (hc, 0, zc)),
                            ("dwg_side", (1.0, hc, zc), (0, hc, zc))):
        cam.location = loc
        cam.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, name + ".png")
        bpy.ops.render.render(write_still=True)
        print("[ortho]", sc.render.filepath, mmpx)


main()
