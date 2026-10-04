"""Blender 内で、歪みを少しずつ重ねて輪郭を参考画像に寄せる。
  blender --background --python warp_fit.py -- <overlay.png>
"""
import json, os, sys, time
import numpy as np
import bpy
from mathutils import Matrix, Vector, kdtree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import view_warp as VW

W, H = 1536, 1024
SPACING = 12
SIGMA1, SIGMA2 = float(os.environ.get('SIGMA1', '14')), 45.0
ALPHA = float(os.environ.get('ALPHA', '0.6'))
NIT = int(os.environ.get("NIT", "14"))
out_png = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else os.path.join(HERE, "warp_overlay.png")

cam = json.load(open(os.path.join(HERE, "camera_left.json")))["params"]
cam = dict(az=cam[0], el=cam[1], roll=cam[2], dist=float(np.exp(cam[3])), f=float(np.exp(cam[4])), cx=cam[5], cy=cam[6])
mesh = np.load(os.path.join(HERE, "unit_mesh.npz"))
verts, quads = mesh["verts"].astype(np.float64), mesh["quads"]
tgt = np.load(os.path.join(HERE, "left_target.npz"))
target, care = tgt["target"], tgt["care"]
warpcare = tgt["warpcare"]


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    me = bpy.data.meshes.new("m")
    me.from_pydata(verts.tolist(), [], quads.tolist())
    me.update()
    ob = bpy.data.objects.new("m", me)
    scene.collection.objects.link(ob)
    cd = bpy.data.cameras.new("c")
    cd.sensor_fit = "HORIZONTAL"
    cd.sensor_width = 36.0
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
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "Standard"
    scene.display.render_aa = "OFF"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (1, 1, 1)
    scene.world = bpy.data.worlds.new("w")
    scene.world.color = (0, 0, 0)
    return me


def render_mask(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path)
    px = np.empty(W * H * 4, np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    px = px.reshape(H, W, 4)[::-1, :, 0]
    return px > 0.5


def boundary(mask):
    p = np.pad(mask, 1)
    inner = p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return mask & ~inner


def nearest_vectors(src, dst, maxd=70.0):
    """src(y, x) の各点から dst の最近点へのベクトル (dx, dy)。"""
    tree = kdtree.KDTree(len(dst))
    for i, (y, x) in enumerate(dst):
        tree.insert((float(x), float(y), 0.0), i)
    tree.balance()
    out = np.zeros((len(src), 2))
    keep = np.zeros(len(src), bool)
    for i, (y, x) in enumerate(src):
        co, _, d = tree.find((float(x), float(y), 0.0))
        if d < maxd:
            out[i] = (co[0] - x, co[1] - y)
            keep[i] = True
    return out, keep


def make_grid(mask, tg):
    bm = boundary(mask) & warpcare
    bt = boundary(tg) & warpcare
    pm = np.argwhere(bm)[::2]
    pt = np.argwhere(bt)[::2]
    v1, k1 = nearest_vectors(pm, pt)             # モデル輪郭 → 目標輪郭
    v2, k2 = nearest_vectors(pt, pm)             # 目標輪郭 → モデル輪郭（足りない所を引き寄せる）
    # 2 つ目は、目標点 q の最近モデル点 p = q + v2 を始点とし、p を q へ動かす（変位 = -v2）
    p2 = np.stack([pt[k2][:, 1] + v2[k2][:, 0], pt[k2][:, 0] + v2[k2][:, 1]], axis=1)
    pos = np.concatenate([pm[k1][:, ::-1], p2]).astype(float)
    vec = np.concatenate([v1[k1], -v2[k2]]).astype(float)
    gx = np.arange(0, W + SPACING, SPACING)
    gy = np.arange(0, H + SPACING, SPACING)
    gxx, gyy = np.meshgrid(gx, gy)
    res = []
    for sigma in (SIGMA1, SIGMA2):
        num = np.zeros(gxx.shape + (2,))
        den = np.zeros(gxx.shape)
        r = int(3 * sigma // SPACING) + 1
        for (px, py), (vx, vy) in zip(pos, vec):
            cx, cy = int(px // SPACING), int(py // SPACING)
            x0, x1 = max(cx - r, 0), cx + r + 1
            y0, y1 = max(cy - r, 0), cy + r + 1
            sx, sy = gxx[y0:y1, x0:x1], gyy[y0:y1, x0:x1]
            if sx.size == 0:
                continue
            w = np.exp(-((sx - px) ** 2 + (sy - py) ** 2) / (2 * sigma ** 2))
            num[y0:y1, x0:x1, 0] += w * vx
            num[y0:y1, x0:x1, 1] += w * vy
            den[y0:y1, x0:x1] += w
        res.append((num, den))
    (n1, d1), (n2, d2) = res
    w1 = np.clip(d1 / 3.0, 0, 1)[..., None]
    g1 = n1 / np.maximum(d1, 1e-9)[..., None]
    g2 = n2 / np.maximum(d2, 1e-9)[..., None]
    return w1 * g1 + (1 - w1) * g2


def error(mask):
    return ((mask ^ target) & care).sum() / (target & care).sum()


def main():
    global verts
    me = setup()
    grids = []
    t0 = time.time()
    m = render_mask(os.path.join(HERE, "_sil.png"))
    print("iter 0 xor", round(error(m), 4), flush=True)
    for it in range(NIT):
        G = make_grid(m, target)
        grids.append(G * ALPHA)
        verts = VW.apply(verts, cam, G, SPACING, ALPHA)
        verts[:, 2] = np.maximum(verts[:, 2], 0.0)   # 接地面より下へは沈ませない
        me.vertices.foreach_set("co", verts.astype(np.float32).ravel())
        me.update()
        m = render_mask(os.path.join(HERE, "_sil.png"))
        print("iter", it + 1, "xor", round(error(m), 4), "t", round(time.time() - t0), flush=True)
    np.savez_compressed(os.path.join(HERE, "view_warp.npz"), grids=np.array(grids).astype(np.float16), spacing=SPACING, cam=json.dumps(cam))
    np.savez(os.path.join(HERE, "unit_mesh_warped.npz"), verts=verts.astype(np.float32), quads=quads)
    out = np.zeros((H, W, 3), np.uint8)
    out[target & care] = (255, 0, 0)
    out[m] = out[m] + np.array((0, 0, 255), np.uint8)
    img = bpy.data.images.new("ov", W, H, alpha=False)
    rgba = np.ones((H, W, 4), np.float32)
    rgba[..., :3] = out[::-1] / 255.0
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = out_png
    img.file_format = "PNG"
    img.save()


main()
