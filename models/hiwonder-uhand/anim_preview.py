"""uHand の動きを絵にして確かめる。

blender --background --python models/hiwonder-uhand/anim_preview.py -- --clip open_close [--view front] [--out DIR]
    <out>/<clip>_<view>_sheet.png   8 コマを左上から右下へ時間順に並べた 1 枚
    <out>/<clip>_<view>.mp4         動画（ffmpeg があるとき。--no-video で省く）
blender --background --python models/hiwonder-uhand/anim_preview.py -- --pose fist [--view front]
blender --background --python models/hiwonder-uhand/anim_preview.py -- --dofs "index=1,thumb=0.5" [--view back]
    <out>/pose_<名前>_<view>.png     姿勢 1 枚
--clip all で全部のクリップ（dof_ を除く）の 1 枚絵だけを作る。
view は front（手のひら側の斜め前）/ back（甲の側）/ side（親指側の真横）/ palm（手のひらの正面）。
出力先の既定は exports/uhand-anim-preview/。
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy
import numpy as np
from mathutils import Vector

import anim_build as AB
import anim_lib
import kin

# 名前: (方位[deg]: -Y から -X 側へ, 仰角[deg], 注視点 [mm], 距離 [mm])
VIEWS = {
    "front": (25.0, 10.0, (16, -8, 90), 370),
    "palm": (0.0, 4.0, (20, -8, 90), 370),
    "back": (200.0, 12.0, (12, 10, 90), 370),
    "side": (-90.0, 4.0, (0, -10, 90), 370),
}
SIZE = 480
SHEET = (4, 2)


def arg(name, default=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(name) + 1] if name in a else default


def flag(name):
    return "--" in sys.argv and name in sys.argv[sys.argv.index("--") + 1:]


def setup(view):
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    sc.render.resolution_x = sc.render.resolution_y = SIZE
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs[0].default_value = (0.82, 0.83, 0.85, 1)
    sc.world = w
    for name, loc, en, size in (("key", (-0.35, -0.5, 0.45), 30.0, 0.3), ("fill", (0.45, -0.35, 0.2), 14.0, 0.4),
                                ("rim", (0.1, 0.5, 0.4), 22.0, 0.3)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy, ld.size = en, size
        lo = bpy.data.objects.new(name, ld)
        lo.location = loc
        lo.rotation_euler = (Vector((0, 0, 0.09)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(lo)
    az, pitch, look, dist = VIEWS[view]
    cd = bpy.data.cameras.new("cam")
    cd.lens = 70
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    a, p = math.radians(az), math.radians(pitch)
    t = Vector(look) * 0.001
    cam.location = t + Vector((-math.sin(a) * math.cos(p), -math.cos(a) * math.cos(p), math.sin(p))) * dist * 0.001
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def pixels(path):
    im = bpy.data.images.load(path)
    w, h = im.size
    px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(im)
    return px


def save_sheet(paths, out):
    cols, rows = SHEET
    tiles = [pixels(p) for p in paths]
    h, w = tiles[0].shape[:2]
    sheet = np.ones((rows * h, cols * w, 4), dtype=np.float32)
    for n, t in enumerate(tiles[:cols * rows]):
        r, c = divmod(n, cols)
        sheet[(rows - 1 - r) * h:(rows - r) * h, c * w:(c + 1) * w] = t     # Blender の画素は下の行から
    im = bpy.data.images.new("sheet", cols * w, rows * h, alpha=True)
    im.pixels.foreach_set(sheet.ravel())
    im.filepath_raw, im.file_format = out, "PNG"
    im.save()
    bpy.data.images.remove(im)


def do_clip(arm, rest, clip, view, out, video):
    fr = anim_lib.frames(clip)
    tmp = os.path.join(out, f"_{clip['name']}_{view}")
    os.makedirs(tmp, exist_ok=True)
    n_tiles = SHEET[0] * SHEET[1]
    picks = sorted({round(k * (len(fr) - 1) / (n_tiles - 1)) for k in range(n_tiles)})
    todo = range(len(fr)) if video else picks
    for n in todo:
        AB.apply_pose(arm, rest, fr[n])
        render(os.path.join(tmp, f"{n:04d}.png"))
    sheet = os.path.join(out, f"{clip['name']}_{view}_sheet.png")
    save_sheet([os.path.join(tmp, f"{n:04d}.png") for n in picks], sheet)
    print("[preview]", sheet)
    if video:
        mp4 = os.path.join(out, f"{clip['name']}_{view}.mp4")
        try:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(anim_lib.FPS), "-i",
                            os.path.join(tmp, "%04d.png"), "-pix_fmt", "yuv420p", "-movflags", "faststart", mp4], check=True)
            print("[preview]", mp4)
        except (OSError, subprocess.CalledProcessError) as e:
            print("[preview] 動画は作れなかった:", e)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)


def main():
    view = arg("--view", "front")
    if view not in VIEWS:
        raise SystemExit(f"view は {', '.join(VIEWS)} のどれか")
    out = arg("--out", os.path.join(AB.EXPORTS, "uhand-anim-preview"))
    os.makedirs(out, exist_ok=True)
    arm, rest = AB.rig()
    setup(view)
    if arg("--pose") or arg("--dofs"):
        if arg("--pose"):
            name = arg("--pose")
            dofs = anim_lib.load_poses()[name]
        else:
            dofs = {k: float(v) for k, v in (kv.split("=") for kv in arg("--dofs").split(","))}
            name = "_".join(f"{k}{v:g}" for k, v in dofs.items())
        bad = [k for k in dofs if k not in kin.DOFS]
        if bad:
            raise SystemExit(f"量 {bad} は無い（{', '.join(kin.DOFS)}）")
        AB.apply_pose(arm, rest, dofs)
        path = os.path.join(out, f"pose_{name}_{view}.png")
        render(path)
        print("[preview]", path)
        return
    clips, errors = anim_lib.load_all()
    if errors:
        raise SystemExit("\n".join(errors))
    want = arg("--clip")
    if want == "all":
        for c in clips:
            if not c["name"].startswith("dof_"):
                do_clip(arm, rest, c, view, out, False)
        return
    clip = next((c for c in clips if c["name"] == want), None)
    if clip is None:
        raise SystemExit(f"クリップ {want!r} は無い: {', '.join(c['name'] for c in clips)}")
    do_clip(arm, rest, clip, view, out, not flag("--no-video"))


main()
