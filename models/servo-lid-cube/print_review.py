"""刷りやすさ・仕上がりの精査（Blender の Python で走らせる）。

    "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python models/servo-lid-cube/print_review.py

組んだ姿勢の STL（build/<部品>.stl）と、部品ごとの「刷るときの上向き」で調べる。
  1. 接地: ベッドに付く面積、重心が接地の外接矩形の中にあるか、高さと接地の幅の比
  2. 宙に浮く面: 45° より寝た下向き面の塊と、その外側のすぐ下に肉があるか（verify.py と同じ判定）
  3. 肉厚: 面の内側へ打った光線が反対の面に当たるまでの距離。0.8mm 未満は外壁 2 本が並ばない
  4. 段差: 水平から 25° より寝た上向きの斜面（層の段が帯になって見える）。外から見える面かどうかも分ける
計器はそれぞれ、答えの分かっている形（0.6mm と 2mm の板、10° と 45° の斜面）で先に確かめる。
出力: build/print_review.json
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

from mathutils import Vector  # noqa: E402

from meshkit import Mesh, inside  # noqa: E402

BUILD = os.path.join(HERE, "build")
LAYER = 0.2
UP = {"box": (0, 0, 1), "lid": (0, 0, -1), "crank": (1, 0, 0), "link": (1, 0, 0), "clip": (-1, 0, 0), "pin": (0, 0, 1)}


def faces(m):
    for i, (a, b, c) in enumerate(m.t):
        p, q, r = m.v[a], m.v[b], m.v[c]
        n = (q - p).cross(r - p)
        area = n.length / 2
        if area < 1e-9:
            continue
        yield i, (p + q + r) / 3, n.normalized(), area


def exterior(c):
    """組んだ姿勢で立方体の外から見える面か（内側の空洞 74 角より外、または天面・底面の近く）。"""
    return abs(c.x) > 37.2 or abs(c.y) > 37.2 or c.z < 2.8 or c.z > 77.2


def review(m, up, ext_check=False):
    up = Vector(up)
    bvh = m.bvh()
    hs = [v.dot(up) for v in m.v]
    h0, h1 = min(hs), max(hs)
    res = {}
    # 1. 接地
    contact_area = 0.0
    pts = []
    for i, c, n, a in faces(m):
        if n.dot(up) < -0.999 and c.dot(up) - h0 < 0.05:
            contact_area += a
            pts.append(c)
    mp = m.mass_props()
    com = Vector(mp["com"])
    # 接地点を上向きに直交する 2 軸で見る
    e1 = up.orthogonal().normalized()
    e2 = up.cross(e1).normalized()
    if pts:
        u = [p.dot(e1) for p in pts]
        v = [p.dot(e2) for p in pts]
        cu, cv = com.dot(e1), com.dot(e2)
        inside_fp = min(u) <= cu <= max(u) and min(v) <= cv <= max(v)
        fp = (max(u) - min(u), max(v) - min(v))
    else:
        inside_fp, fp = False, (0, 0)
    res["bed"] = dict(contact_mm2=round(contact_area, 1), footprint_mm=[round(x, 1) for x in fp],
                      height_mm=round(h1 - h0, 1), com_over_footprint=inside_fp,
                      height_to_min_footprint=round((h1 - h0) / max(0.1, min(fp)), 2) if pts else None)
    # 2〜4
    thin, terr, hang = [], [], []
    for i, c, n, a in faces(m):
        h = c.dot(up) - h0
        d = n.dot(up)
        # 3. 肉厚（内側へ）
        # 向かいの面が反対を向いているときだけ数える（ゆるい角の縁で隣の面に当たるのは薄さではない）。
        # 60° より鋭い楔は数える＝刃物の縁
        hit = bvh.ray_cast(c - n * 1e-3, -n, 50.0)
        t = hit[3] + 1e-3 if hit[0] is not None else None
        if t is not None and t < 1.2 and hit[1].dot(n) < -0.6:
            thin.append((t, a, c))
        # 4. 段差（上向きの浅い斜面）
        if 0.906 < d < 0.9994 and h > LAYER:
            slope = math.degrees(math.acos(min(1.0, d)))
            terr.append((slope, a, c, exterior(c) if ext_check else False))
        # 2. 下向き（45° より寝た面）
        # 45° ちょうどの面（面取り・涙形・支え）は刷れるので数えない
        if d < -math.cos(math.radians(44.8)) and h > LAYER * 1.25:
            hang.append((i, a, c))
    def cluster(items, key_pos, radius=2.0):
        """近い面をまとめる（格子で粗く）。"""
        cells = {}
        for it in items:
            p = key_pos(it)
            k = (round(p.x / radius), round(p.y / radius), round(p.z / radius))
            cells.setdefault(k, []).append(it)
        # 隣り合う格子をつなぐ
        keys = list(cells)
        parent = {k: k for k in keys}
        def f(k):
            while parent[k] != k:
                parent[k] = parent[parent[k]]
                k = parent[k]
            return k
        for k in keys:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        nb = (k[0] + dx, k[1] + dy, k[2] + dz)
                        if nb in parent:
                            parent[f(nb)] = f(k)
        groups = {}
        for k in keys:
            groups.setdefault(f(k), []).extend(cells[k])
        return list(groups.values())
    rows = []
    for g in cluster(thin, lambda it: it[2]):
        area = sum(it[1] for it in g)
        if area < 0.5:
            continue
        ps = [it[2] for it in g]
        rows.append(dict(min_mm=round(min(it[0] for it in g), 2), area_mm2=round(area, 1),
                         at=[[round(min(p[k] for p in ps), 1) for k in range(3)], [round(max(p[k] for p in ps), 1) for k in range(3)]]))
    rows.sort(key=lambda r: r["min_mm"])
    res["thin_under_1_2mm"] = rows
    rows = []
    for g in cluster(terr, lambda it: it[2], 4.0):
        area = sum(it[1] for it in g)
        if area < 1.0:
            continue
        ps = [it[2] for it in g]
        ext = sum(it[1] for it in g if it[3])
        rows.append(dict(min_slope_deg=round(min(it[0] for it in g), 1), area_mm2=round(area, 1), exterior_mm2=round(ext, 1),
                         at=[[round(min(p[k] for p in ps), 1) for k in range(3)], [round(max(p[k] for p in ps), 1) for k in range(3)]]))
    rows.sort(key=lambda r: -r["exterior_mm2"] - r["area_mm2"] * 0.01)
    res["terrace_under_25deg"] = rows
    res["terrace_exterior_mm2"] = round(sum(r["exterior_mm2"] for r in rows), 1)
    # 下向き面の支え（塊ごとに、外周のすぐ外・半層下が肉か）
    rows = []
    for g in cluster(hang, lambda it: it[2], 1.5):
        area = sum(it[1] for it in g)
        ps = [it[2] for it in g]
        cen = sum(ps, Vector()) / len(ps)
        sup = tot = 0
        for p in ps:
            dvec = p - cen
            dvec -= up * dvec.dot(up)
            if dvec.length < 0.3:
                continue
            probe = p + dvec.normalized() * 0.6 - up * (LAYER * 0.5)
            tot += 1
            sup += inside(bvh, probe)
        rows.append(dict(area_mm2=round(area, 2), supported=round(sup / tot, 2) if tot else None,
                         h=[round(min(p.dot(up) for p in ps) - h0, 2), round(max(p.dot(up) for p in ps) - h0, 2)],
                         at=[[round(min(p[k] for p in ps), 1) for k in range(3)], [round(max(p[k] for p in ps), 1) for k in range(3)]]))
    rows.sort(key=lambda r: -r["area_mm2"])
    res["overhang_clusters"] = rows
    return res


def plate(t, w=20.0, d=20.0, h=10.0):
    v = [Vector((x, y, z)) for z in (0, h) for y in (0, d) for x in (0, t)]
    f = [(0, 2, 3), (0, 3, 1), (4, 5, 7), (4, 7, 6), (0, 1, 5), (0, 5, 4), (2, 6, 7), (2, 7, 3), (0, 4, 6), (0, 6, 2), (1, 3, 7), (1, 7, 5)]
    return Mesh(v, f, f"plate_{t}")


def wedge(deg, length=20.0, width=10.0, base=2.0):
    """上面が水平から deg 傾いた楔（底は z=0）。"""
    hgt = length * math.tan(math.radians(deg))
    pts = [(0, 0), (length, 0), (length, base + hgt), (0, base)]
    v = [Vector((x, 0, z)) for x, z in pts] + [Vector((x, width, z)) for x, z in pts]
    f = [(0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6), (0, 4, 5), (0, 5, 1), (1, 5, 6), (1, 6, 2), (2, 6, 7), (2, 7, 3), (3, 7, 4), (3, 4, 0)]
    return Mesh(v, f, f"wedge_{deg}")


def calibrate():
    r = {}
    r["plate_0.6_thin"] = review(plate(0.6), (0, 0, 1))["thin_under_1_2mm"][:1]
    r["plate_2.0_thin"] = review(plate(2.0), (0, 0, 1))["thin_under_1_2mm"][:1]
    r["wedge_10_terrace"] = review(wedge(10), (0, 0, 1))["terrace_under_25deg"][:1]
    r["wedge_45_terrace"] = review(wedge(45), (0, 0, 1))["terrace_under_25deg"][:1]
    # 刃物の縁（20° の楔）は薄いと出る。ゆるい縁（70° の楔）は出ない
    r["knife_20_thin"] = review(wedge(20, length=6.0, base=0.0), (0, 0, 1))["thin_under_1_2mm"][:1]
    r["blunt_70_thin"] = review(wedge(70, length=6.0, base=0.0), (0, 0, 1))["thin_under_1_2mm"][:1]
    ok = (bool(r["plate_0.6_thin"]) and abs(r["plate_0.6_thin"][0]["min_mm"] - 0.6) < 0.05 and not r["plate_2.0_thin"]
          and bool(r["wedge_10_terrace"]) and not r["wedge_45_terrace"]
          and bool(r["knife_20_thin"]) and not r["blunt_70_thin"])
    r["ok"] = ok
    return r


def main():
    out = {"calibration": calibrate()}
    print("calibration", json.dumps(out["calibration"], ensure_ascii=False))
    out["parts"] = {}
    for name, up in UP.items():
        m = Mesh.load(os.path.join(BUILD, f"{name}.stl"), name)
        r = review(m, up, ext_check=name in ("box", "lid"))
        out["parts"][name] = r
        print(f"\n== {name}  bed {r['bed']}")
        print("   thin(<1.2):", r["thin_under_1_2mm"][:8])
        print("   terrace exterior mm2:", r["terrace_exterior_mm2"], r["terrace_under_25deg"][:6])
        print("   overhang:", [(c["area_mm2"], c["supported"], c["h"], c["at"]) for c in r["overhang_clusters"][:8]])
    with open(os.path.join(BUILD, "print_review.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)


main()
