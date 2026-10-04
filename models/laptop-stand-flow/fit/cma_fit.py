"""CMA-ES で、カメラ・半幅 H・中心ずれ xc・側面輪郭の歪み・レール板を、左の脚の輪郭にあわせる。

歪みは側面（Y-Z）平面の滑らかな変位場で、x 方向には一様に効く。
そのため立体は「輪郭を厚み付けした形」のままで、他の角度から見ても崩れない。
"""
import json, os, sys, time
from pathlib import Path
import numpy as np
from multiprocessing import Pool

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import fwd
import ref_mask
import shape_field as P
import ref_trace as T

STEP = 3
ROI = (30, 190, 760, 900)
SEEDS = np.array(P.SEEDS, float)
NS = len(SEEDS)
OUT0 = np.array([P.to_mm(p) for p in T.OUTER], float)
NODE_IDX = list(range(0, len(T.OUTER), 3))
NODES = OUT0[NODE_IDX]
NN = len(NODES)
SIGMA_W = 16.0
H_MIN, XC_MAX = 9.0, 18.0
TUNNEL = None   # (H0, k): 穴の縁では半幅を H0 に絞り、穴から離れるほど k の傾きで広げる

# x の並び: cam(7) H(NS) xc(NS) disp(2*NN) plank(3)
I_H, I_XC = 7, 7 + NS
I_D = I_XC + NS
I_PL = I_D + 2 * NN
I_TN = I_PL + 3
NX = I_TN + 2

SCALE = np.concatenate([[4, 3, 2, 0.08, 0.1, 30, 30], np.full(NS, 4.0), np.full(NS, 4.0), np.full(2 * NN, 3.0), [3, 3, 1, 3, 0.3]])
W_H, W_XC, W_D = 0.01, 0.01, 0.01   # 6mm / 6mm / 5mm の二乗平均ずれで、それぞれ 1% 分

_c = {}


def ctx():
    if not _c:
        F = fwd.Field()
        comp, care = ref_mask.left_unit()
        h_, w_ = comp.shape
        x0, y0, x1, y1 = [v // STEP for v in ROI]
        sub = lambda a: a[STEP // 2:h_:STEP, STEP // 2:w_:STEP][y0:y1, x0:x1]
        _c.update(F=F, target=sub(comp), care=sub(care), shape=(h_, w_))
    return _c


def bilerp(a, py, pz):
    gy = np.clip((py - fwd.Y0) / fwd.G, 0, a.shape[0] - 1.001)
    gz = np.clip((pz - fwd.Z0) / fwd.G, 0, a.shape[1] - 1.001)
    y0, z0 = np.floor(gy).astype(int), np.floor(gz).astype(int)
    fy, fz = gy - y0, gz - z0
    return ((1 - fy) * (1 - fz) * a[y0, z0] + fy * (1 - fz) * a[y0 + 1, z0]
            + (1 - fy) * fz * a[y0, z0 + 1] + fy * fz * a[y0 + 1, z0 + 1])


def warped_fields(F, h_seed, xc_seed, disp, tunnel=None, power=2.0, sigma=17.0):
    yy, zz = F.yy, F.zz
    d2 = (yy[None] - NODES[:, 0, None, None]) ** 2 + (zz[None] - NODES[:, 1, None, None]) ** 2
    w = np.exp(-d2 / (2 * SIGMA_W ** 2)) + 1e-12
    w /= w.sum(axis=0)
    wy = (w * disp[:, 0, None, None]).sum(axis=0)
    wz = (w * disp[:, 1, None, None]).sum(axis=0)
    py, pz = yy - wy, zz - wz
    d = bilerp(F.d, py, pz)
    thick = bilerp(F.thick, py, pz)
    dh = bilerp(F.dh, py, pz)
    sy = np.array([P.to_mm((s[0], s[1]))[0] for s in SEEDS])
    sz = np.array([P.to_mm((s[0], s[1]))[1] for s in SEEDS])
    g2 = (py[None] - sy[:, None, None]) ** 2 + (pz[None] - sz[:, None, None]) ** 2
    lw = -g2 / (2.0 * sigma ** 2)
    lw -= lw.max(axis=0)
    ww = np.exp(lw)
    den = ww.sum(axis=0)
    r_seed = (ww * SEEDS[:, 2, None, None]).sum(axis=0) / den
    h_max = (ww * h_seed[:, None, None]).sum(axis=0) / den
    if tunnel is not None:
        h_max = np.minimum(h_max, tunnel[0] + tunnel[1] * dh)
    xc = (ww * xc_seed[:, None, None]).sum(axis=0) / den
    from shape_field import blur
    r = blur(np.minimum(r_seed, np.maximum(thick, 1.0)), 2.5, fwd.G)
    u = np.maximum(0.0, 1.0 - d / r)
    h = h_max * np.maximum(0.0, 1.0 - u ** power) ** (1.0 / power)
    h = np.where(d > 0.0, h, 0.0)
    h = np.where((zz >= 0) & (zz <= fwd.SEAT_Z), h, 0.0)
    return h, xc


def unpack(x):
    cam = dict(az=x[0], el=x[1], roll=x[2], dist=np.exp(x[3]), f=np.exp(x[4]), cx=x[5], cy=x[6])
    hs = np.maximum(x[I_H:I_H + NS], H_MIN)       # 幅が負・極端に細くなるのを避ける（印刷の強度も）
    xcs = np.clip(x[I_XC:I_XC + NS], -XC_MAX, XC_MAX)
    return cam, hs, xcs, x[I_D:I_D + 2 * NN].reshape(NN, 2), x[I_PL:I_PL + 3]


def evaluate(x, detail=False):
    c = ctx()
    cam, hs, xcs, disp, pl = unpack(x)
    h, xc = warped_fields(c["F"], hs, xcs, disp, tunnel=(max(x[I_TN], 4.0), max(x[I_TN + 1], 0.0)))
    m = fwd.silhouette(h, cam, c["shape"], STEP, ROI, 0.0, 0.0, plank_half=12.0 + pl[2], xc_field=xc,
                       plank_dy=(pl[0], pl[1]), single=True)
    xor = (m ^ c["target"]) & c["care"]
    e = xor.sum() / (c["target"] & c["care"]).sum()
    reg = (W_H * np.mean(((hs - SEEDS[:, 3]) / 6.0) ** 2) + W_XC * np.mean((xcs / 6.0) ** 2)
           + W_D * np.mean((disp / 5.0) ** 2))
    if detail:
        return e, reg, m
    return e + reg


def init():
    ctx()


X0 = None


def main():
    global X0
    out_png = sys.argv[1]
    cam = json.load(open(HERE / "camera_left.json"))["params"]
    X0 = np.zeros(NX)
    X0[:7] = cam
    X0[I_H:I_H + NS] = SEEDS[:, 3]
    X0[I_TN:I_TN + 2] = [14.0, 1.0]
    sf = HERE / "cma_state.json"
    if sf.exists():
        X0 = np.array(json.load(open(sf))["x"], float)
    n = NX
    lam = int(os.environ.get("POP", "52"))
    mu = lam // 2
    wts = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1))
    wts /= wts.sum()
    mueff = 1.0 / (wts ** 2).sum()
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n)
    cs = (mueff + 2) / (n + mueff + 5)
    c1 = 2 / ((n + 1.3) ** 2 + mueff)
    cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff))
    damps = 1 + 2 * max(0, np.sqrt((mueff - 1) / (n + 1)) - 1) + cs
    chiN = np.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n))
    mean = np.zeros(n)
    sigma = float(os.environ.get("SIGMA0", "0.5"))
    C = np.eye(n)
    pc, ps = np.zeros(n), np.zeros(n)
    rng = np.random.default_rng(int(os.environ.get("SEED", "0")))
    pool = Pool(int(os.environ.get("NPROC", "26")), initializer=init)
    best = (np.inf, None)
    t0 = time.time()
    maxgen = int(os.environ.get("GENS", "3000"))
    eigen_t = 0
    B, D = np.eye(n), np.ones(n)
    for gen in range(maxgen):
        if gen - eigen_t >= 1 / (c1 + cmu) / n / 10:
            eigen_t = gen
            C = np.triu(C) + np.triu(C, 1).T
            D2, B = np.linalg.eigh(C)
            D = np.sqrt(np.maximum(D2, 1e-20))
        Z = rng.standard_normal((lam, n))
        Y = (Z * D) @ B.T
        Xs = mean + sigma * Y
        vals = np.array(pool.map(evaluate, list(X0 + Xs * SCALE), chunksize=2))
        order = np.argsort(vals)
        if vals[order[0]] < best[0]:
            best = (vals[order[0]], X0 + Xs[order[0]] * SCALE)
        sel = order[:mu]
        old = mean.copy()
        mean = wts @ Xs[sel]
        yw = (mean - old) / sigma
        invsqrtC = B @ np.diag(1 / D) @ B.T
        ps = (1 - cs) * ps + np.sqrt(cs * (2 - cs) * mueff) * (invsqrtC @ yw)
        hsig = np.linalg.norm(ps) / np.sqrt(1 - (1 - cs) ** (2 * (gen + 1))) / chiN < 1.4 + 2 / (n + 1)
        pc = (1 - cc) * pc + hsig * np.sqrt(cc * (2 - cc) * mueff) * yw
        artmp = (Xs[sel] - old) / sigma
        C = ((1 - c1 - cmu) * C + c1 * (np.outer(pc, pc) + (1 - hsig) * cc * (2 - cc) * C)
             + cmu * (artmp.T * wts) @ artmp)
        sigma *= np.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1))
        if gen % 20 == 0:
            e, reg, _ = evaluate(best[1], detail=True)
            print(f"gen {gen} best {best[0]:.4f} (xor {e:.4f} reg {reg:.4f}) sigma {sigma:.3f} t {time.time() - t0:.0f}",
                  flush=True)
            json.dump({"x": list(map(float, best[1])), "loss": float(best[0])}, open(sf, "w"))
    pool.close()
    json.dump({"x": list(map(float, best[1])), "loss": float(best[0])}, open(sf, "w"))
    e, reg, m = evaluate(best[1], detail=True)
    print("final xor", e, "reg", reg)
    from PIL import Image
    c = ctx()
    out = np.zeros(m.shape + (3,), np.uint8)
    out[c["target"]] = (255, 0, 0)
    out[m] = out[m] + np.array((0, 0, 255), np.uint8)
    Image.fromarray(out).resize((out.shape[1] * 2, out.shape[0] * 2), Image.NEAREST).save(out_png)


if __name__ == "__main__":
    main()
