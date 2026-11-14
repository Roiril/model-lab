"""書き出した STL と輪郭から、置ける・外せる・倒れない・刷れるを数値で確かめる。

使い方:
  py -3.11 models/redmi-pad-stand/verify.py --stand-mass 0.62 [--out <json>]
--stand-mass は刷った（またはスライスした）スタンドの質量 kg。転倒の計算に使う。
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")
import params as P
import stand_profile as prof

G = 9.81
TABLET_CORNER_R = 1.0  # 本体の角の丸みの最小の仮定（受け口の奥の隅の丸み 1mm と同じ）


# ---------- メッシュ ----------
def read_stl(path):
    data = Path(path).read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    if 84 + count * 50 != len(data):
        raise ValueError("ASCII STL is not supported")
    rec = np.frombuffer(data, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]),
                        count=count, offset=84)
    return rec["v"].astype(np.float64)


def mesh_report(tris):
    flat = tris.reshape(-1, 3)
    uniq, inverse = np.unique(np.round(flat, 5), axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    parent = list(range(len(uniq)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b, c in faces:
        for x, y in ((a, b), (b, c)):
            ra, rb = find(x), find(y)
            if ra != rb:
                parent[ra] = rb
    comps = len({find(i) for i in range(len(uniq))})
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    cross = np.cross(b - a, c - a)
    area = np.linalg.norm(cross, axis=1) / 2
    vol6 = np.einsum("ij,ij->i", a, np.cross(b, c))
    volume = vol6.sum() / 6
    centroid = ((a + b + c) * vol6[:, None]).sum(axis=0) / (24 * volume)
    normals = cross / np.maximum(np.linalg.norm(cross, axis=1), 1e-12)[:, None]
    return dict(
        triangles=len(tris), non_manifold_edges=int((counts != 2).sum()), components=comps,
        zero_area=int((area < 1e-6).sum()), volume_cm3=volume / 1000, centroid_mm=centroid.tolist(),
        min_mm=flat.min(axis=0).tolist(), max_mm=flat.max(axis=0).tolist(),
        _normals=normals, _area=area, _zmin=np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2]),
    )


def overhang_area(tris, rep, limit_deg=45.0):
    """机の面より上で、下向きに limit_deg を超えて張り出す面積（mm²）。"""
    nz = rep["_normals"][:, 2]
    above_bed = rep["_zmin"] > 0.05
    bad = above_bed & (nz < -math.cos(math.radians(limit_deg)))
    return float(rep["_area"][bad].sum())


def footprint_area(tris, rep):
    nz = rep["_normals"][:, 2]
    flat_bottom = (rep["_zmin"] < 0.01) & (nz < -0.999)
    return float(rep["_area"][flat_bottom].sum())


# ---------- 2D（側面） ----------
def inside(pt, poly):
    x, y = pt
    hit = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def seg_dist(p, a, b):
    ab = (b[0] - a[0], b[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1]) / max(ab[0] ** 2 + ab[1] ** 2, 1e-12)))
    return math.dist(p, (a[0] + ab[0] * t, a[1] + ab[1] * t))


def poly_dist(p, poly):
    return min(seg_dist(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def tablet_section(height, thickness, lift=0.0, r=TABLET_CORNER_R, steps=12):
    """本体の断面（Y-Z）。背面を支えの面に、底を受け口の床に合わせ、u 方向へ lift 持ち上げる。"""
    s0, u, n = prof.frame()
    local = []
    corners = [(r, r, math.pi), (r, height - r, math.pi / 2), (thickness - r, height - r, 0.0),
               (thickness - r, r, -math.pi / 2)]
    # local (a, b): a = n 方向（背面 0 → 画面 t）, b = u 方向（底 0 → 上 h）
    for ca, cb, start in corners:
        for k in range(steps + 1):
            ang = start + (math.pi / 2) * k / steps
            local.append((ca + r * math.cos(ang), cb + r * math.sin(ang)))
    pts = [(s0[0] + a * n[0] + (b + lift) * u[0], s0[1] + a * n[1] + (b + lift) * u[1]) for a, b in local]
    return pts


def interference(stand_poly, section, tol=0.05):
    """本体の断面が輪郭の中へ tol 以上入り込んでいる量（mm）。0 なら当たらない。"""
    worst = 0.0
    dense = []
    for i in range(len(section)):
        a, b = section[i], section[(i + 1) % len(section)]
        k = max(1, int(math.dist(a, b) / 0.5))
        dense += [(a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k) for j in range(k)]
    for p in dense:
        if inside(p, stand_poly):
            worst = max(worst, poly_dist(p, stand_poly))
    for p in stand_poly:
        if inside(p, section):
            worst = max(worst, poly_dist(p, section))
    return worst if worst > tol else 0.0


def lip_cover(stand_poly, thickness, eye_drop_deg=0.0):
    """画面の下端から、返しが隠す長さ（画面に沿って mm）。

    eye_drop_deg: 画面の法線から下へ傾けた視線（座った目がやや低いとき）。
    """
    s0, u, n = prof.frame()
    # 視線の向き（目→画面）: -n を下へ eye_drop_deg 回す。目が下にあるほど返しが高く映る
    a = math.radians(eye_drop_deg)
    # 目が法線より下にあると、視線は画面に沿って上向き（+u）の成分を持つ
    view = (-n[0] * math.cos(a) + u[0] * math.sin(a), -n[1] * math.cos(a) + u[1] * math.sin(a))
    cover = 0.0
    for p in stand_poly:
        a_n = (p[0] - s0[0]) * n[0] + (p[1] - s0[1]) * n[1]
        if a_n <= thickness:
            continue
        b_u = (p[0] - s0[0]) * u[0] + (p[1] - s0[1]) * u[1]
        # 点から視線を逆にたどって画面の面 (a_n = thickness) に当たる位置
        vn = view[0] * n[0] + view[1] * n[1]
        vu = view[0] * u[0] + view[1] * u[1]
        k = (thickness - a_n) / vn
        cover = max(cover, b_u + k * vu)
    return cover


# ---------- 転倒 ----------
def tipping(stand_mass, stand_cg_y, height, push_at, rear_y):
    """画面に垂直に押したとき、後ろの接地端のまわりで浮き始める力（N）。

    push_at: 画面に沿って底から測った押す位置（mm）。
    """
    s0, u, n = prof.frame()
    t = P.TABLET_T_MM
    px = s0[0] + t * n[0] + push_at * u[0]
    pz = s0[1] + t * n[1] + push_at * u[1]
    tab_cg_y = s0[0] + t / 2 * n[0] + height / 2 * u[0]
    restore = (stand_mass * (rear_y - stand_cg_y) + P.TABLET_MASS_KG * (rear_y - tab_cg_y)) * G  # N·mm
    # 押す力の向き -n = (後ろ, 下)。後ろ向き成分が倒し、下向き成分（接地端より前なら）が戻す
    fy, fz = -n[0], -n[1]
    overturn_per_n = fy * pz + fz * (rear_y - px)
    return restore / overturn_per_n


def calibrate(tris, rep):
    """計器の校正: 上下を反転したスタンドは大きく張り出し、元の形と同じ式で数えて検出できること。"""
    flipped = tris.copy()
    flipped[:, :, 2] = rep["max_mm"][2] - flipped[:, :, 2]
    flipped = flipped[:, ::-1, :]  # 反転で面の向きが裏返るのを戻す
    frep = mesh_report(flipped)
    flipped_overhang = overhang_area(flipped, frep)
    s0, u, n = prof.frame()
    poly = prof.outline()
    sunk = interference(poly, tablet_section(P.TABLET_H_MM, P.TABLET_T_MM, lift=-2.0))
    return dict(flipped_overhang_mm2=flipped_overhang, sunk_2mm_interference_mm=sunk,
                ok=flipped_overhang > 1000 and sunk > 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stand-mass", type=float, required=True, help="kg")
    ap.add_argument("--stl", default=str(ROOT / "exports" / f"{P.MODEL_NAME}.stl"))
    ap.add_argument("--out")
    args = ap.parse_args()

    tris = read_stl(args.stl)
    rep = mesh_report(tris)
    cal = calibrate(tris, rep)
    poly = prof.outline()
    s0, u, n = prof.frame()
    t = P.TABLET_T_MM

    h = P.TABLET_H_MM  # 横置き専用
    fit = dict(seated_interference_mm=interference(poly, tablet_section(h, t)),
               lift_out_interference_mm=max(interference(poly, tablet_section(h, t, lift=s))
                                            for s in np.arange(0, 40.1, 0.5)))
    # 入るケースの厚さ: 受け口の幅（支えの面から返しまで）から 0.5mm の余裕を引く
    case_max = P.GROOVE_MM - 0.5
    case_fit = interference(poly, tablet_section(P.TABLET_H_MM, case_max))

    rear_y = rep["max_mm"][1]
    cg_y = rep["centroid_mm"][1]
    tip = dict(top_edge_N=tipping(args.stand_mass, cg_y, h, h, rear_y),
               screen_center_N=tipping(args.stand_mass, cg_y, h, h / 2, rear_y))
    # 滑り: 上端を押したとき、後ろ向きの力 = 摩擦 になる摩擦係数（倒れる直前の力で）
    f = tip["top_edge_N"]
    total_w = (args.stand_mass + P.TABLET_MASS_KG) * G
    mu_needed = (-n[0] * f) / (total_w + (-n[1]) * f)

    support_top = max(((p[0] - s0[0]) * u[0] + (p[1] - s0[1]) * u[1]) for p in poly
                      if abs((p[0] - s0[0]) * n[0] + (p[1] - s0[1]) * n[1]) < 0.05)

    report = dict(
        mesh={k: v for k, v in rep.items() if not k.startswith("_")},
        footprint_cm2=footprint_area(tris, rep) / 100,
        overhang_over_45deg_mm2=overhang_area(tris, rep),
        calibration=cal,
        fit=fit,
        case_thickness_max_mm=case_max, case_fit_interference_mm=case_fit,
        lip_cover_mm=dict(normal=lip_cover(poly, t), eye_15deg_low=lip_cover(poly, t, 15.0), eye_15deg_high=lip_cover(poly, t, -15.0),
                          bezel=P.TABLET_BEZEL_MM),
        support_contact_mm=support_top,
        support_share=support_top / P.TABLET_H_MM,
        stand_mass_kg=args.stand_mass,
        tipping_N=tip,
        friction_needed_to_tip_before_slide=mu_needed,
    )
    ok = (rep["non_manifold_edges"] == 0 and rep["components"] == 1 and rep["zero_area"] == 0
          and cal["ok"] and report["overhang_over_45deg_mm2"] < 1.0
          and fit["seated_interference_mm"] == 0 and fit["lift_out_interference_mm"] == 0
          and case_fit == 0
          and report["lip_cover_mm"]["normal"] < P.TABLET_BEZEL_MM
          and rep["max_mm"][0] - rep["min_mm"][0] <= 230 and rep["max_mm"][1] - rep["min_mm"][1] <= 230)
    report["ok"] = bool(ok)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        out = Path(args.out)
        tmp = out.with_suffix(out.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8", newline="\n")
        json.loads(tmp.read_text(encoding="utf-8"))
        tmp.replace(out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
