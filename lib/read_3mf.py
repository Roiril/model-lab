"""3mf を読んで、設計の参考になる数値を取り出す。

Blender を経由せず標準ライブラリだけで動く。

    py -3.11 lib/read_3mf.py "C:/Users/kouga/Downloads/SG90実寸.3mf"

出すもの:
  - 部品ごとの外形寸法（mm）・三角形数・メッシュ健全性
  - 円筒フィーチャ（穴・ボス・軸）の径と深さ
  - 造形プレート上の姿勢（どの面を下にして印刷しているか）
  - スライス設定（層厚・壁数・充填・サポート）
"""

import sys
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from statistics import mean, pstdev

NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"

# 円と認めるしきい値
MIN_RING_VERTS = 8      # 1 リングを構成する最小頂点数
RING_ROUNDNESS = 0.02   # 半径のばらつき / 平均半径
MIN_DIAMETER = 0.8      # mm。これ未満は無視
CENTER_TOL = 1          # 中心座標を丸める桁（0.1mm）
DIAM_TOL = 2            # 径を丸める桁（0.01mm）


# --------------------------------------------------------------------------
# 読み取り
# --------------------------------------------------------------------------

def _part_names(z):
    """Bambu / Orca の model_settings.config から部品名とメッシュ健全性を拾う。"""
    info = {}
    try:
        raw = z.read("Metadata/model_settings.config").decode("utf-8", "replace")
    except KeyError:
        return info
    for m in re.finditer(r'<object\s+id="(\d+)"[^>]*>(.*?)</object>', raw, re.S):
        oid, body = m.group(1), m.group(2)
        name = re.search(r'key="name"\s+value="([^"]*)"', body)
        stat = re.search(r'<mesh_stat ([^/]*)/>', body)
        info[oid] = {
            "name": name.group(1) if name else "",
            "stat": dict(re.findall(r'(\w+)="([^"]*)"', stat.group(1))) if stat else {},
        }
    return info


def _build_transforms(z):
    """build/item の 4x3 行列を objectid ごとに返す。造形時の姿勢そのもの。"""
    out = {}
    try:
        root = ET.fromstring(z.read("3D/3dmodel.model"))
    except KeyError:
        return out
    build = root.find(NS + "build")
    if build is None:
        return out
    for item in build.findall(NS + "item"):
        t = item.get("transform")
        if t:
            out[item.get("objectid")] = [float(v) for v in t.split()]
    return out


def _meshes(z):
    """(object id, 頂点リスト, 三角形リスト) を順に返す。"""
    for entry in z.namelist():
        if not entry.endswith(".model"):
            continue
        root = ET.fromstring(z.read(entry))
        for obj in root.iter(NS + "object"):
            mesh = obj.find(NS + "mesh")
            if mesh is None:
                continue
            vs = mesh.find(NS + "vertices")
            ts = mesh.find(NS + "triangles")
            if vs is None or len(vs) == 0:
                continue
            verts = [(float(v.get("x")), float(v.get("y")), float(v.get("z"))) for v in vs]
            tris = ([(int(t.get("v1")), int(t.get("v2")), int(t.get("v3"))) for t in ts]
                    if ts is not None else [])
            yield obj.get("id"), verts, tris


def _slice_settings(z):
    keys = ["layer_height", "wall_loops", "sparse_infill_density", "sparse_infill_pattern",
            "support_type", "enable_support", "nozzle_diameter", "filament_type", "brim_type"]
    try:
        raw = z.read("Metadata/project_settings.config").decode("utf-8", "replace")
    except KeyError:
        return {}
    out = {}
    for k in keys:
        m = re.search(r'"' + k + r'":\s*(\[[^\]]*\]|"[^"]*")', raw)
        if m:
            out[k] = " ".join(m.group(1).replace('"', "").split())
    return out


# --------------------------------------------------------------------------
# 幾何
# --------------------------------------------------------------------------

def bbox(verts):
    xs, ys, zs = zip(*verts)
    return (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


def _wall_faces(verts, tris, axis):
    """axis に平行な壁（法線が axis と直交する面）を集める。

    円筒面はこの条件を満たし、しかも法線が軸をまっすぐ指す。
    平らな面や斜面もここに混じるが、次段で落ちる。

    返すのは (重心, 法線, 軸方向の範囲, 投影した 3 頂点)。
    半径は重心ではなく頂点で測る。多角形近似の重心は円より内側に入るため。
    """
    a, b = [i for i in (0, 1, 2) if i != axis]
    out = []
    for i0, i1, i2 in tris:
        p0, p1, p2 = verts[i0], verts[i1], verts[i2]
        ux, uy, uz = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        vx, vy, vz = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
        n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
        ln = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5
        if ln < 1e-12 or abs(n[axis] / ln) > 0.03:
            continue
        pts = ((p0[a], p0[b]), (p1[a], p1[b]), (p2[a], p2[b]))
        out.append({
            "c": (sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3),
            "n": (n[a] / ln, n[b] / ln),
            "lo": min(p0[axis], p1[axis], p2[axis]),
            "hi": max(p0[axis], p1[axis], p2[axis]),
            "pts": pts,
        })
    return out


def _axis_peaks(faces, sample=220, grid=4):
    """壁面の法線を延ばした直線どうしの交点。円筒なら中心に集まる。

    格子で数えたあと、峰の中身を平均して中心を格子より細かく決め直す。
    """
    step = max(1, len(faces) // sample)
    fs = faces[::step]
    bins = defaultdict(list)
    for i in range(len(fs)):
        (cx1, cy1), (nx1, ny1) = fs[i]["c"], fs[i]["n"]
        for j in range(i + 1, len(fs)):
            (cx2, cy2), (nx2, ny2) = fs[j]["c"], fs[j]["n"]
            det = ny1 * nx2 - nx1 * ny2
            if abs(det) < 0.3:           # 法線がほぼ平行なら交点は当てにならない
                continue
            t = ((cy2 - cy1) * nx2 - (cx2 - cx1) * ny2) / det
            x, y = cx1 + t * nx1, cy1 + t * ny1
            bins[(round(x * grid), round(y * grid))].append((x, y))
    if not bins:
        return []
    peak = max(len(v) for v in bins.values())
    out = []
    for key, pts in bins.items():
        if len(pts) < max(8, peak * 0.03):
            continue
        out.append((mean(p[0] for p in pts), mean(p[1] for p in pts), len(pts)))
    return sorted(out, key=lambda t: -t[2])[:40]


def _angular_span(members, ox, oy):
    """面の法線が中心のまわりにどれだけ扇形に広がっているか（度）。

    円筒なら法線が全周に散る。平らな壁は法線が全部同じ向きなので 0 に近い。
    遠方に立った偽の中心はこれで落ちる。
    """
    import math
    angs = sorted(math.atan2(m[1]["c"][1] - oy, m[1]["c"][0] - ox) for m in members)
    if len(angs) < 2:
        return 0.0
    gaps = [angs[i + 1] - angs[i] for i in range(len(angs) - 1)]
    gaps.append(angs[0] + 2 * math.pi - angs[-1])
    return math.degrees(2 * math.pi - max(gaps))


def cylinders(verts, tris, min_support=5, max_radius=None):
    """円筒フィーチャ（穴・ボス・軸）を返す。

    平面を輪切りにする方法は、穴のふちと、それを囲む平らな面の外周が
    三角形分割を通じてつながっているせいで混ざる。ここでは面の法線を使う。
    円筒の壁の法線は必ず軸を通るので、法線を延ばした直線の交点が軸に集まる。
    """
    if max_radius is None:
        max_radius = max(bbox(verts)) / 2
    out = []
    for axis in (0, 1, 2):
        faces = _wall_faces(verts, tris, axis)
        if len(faces) < min_support:
            continue
        for ox, oy, _ in _axis_peaks(faces):
            # 法線が中心をまっすぐ指す面だけを、半径ごとの箱に入れる
            buckets = defaultdict(list)
            for f in faces:
                cx, cy = f["c"]
                dr = ((cx - ox) ** 2 + (cy - oy) ** 2) ** 0.5
                if dr < MIN_DIAMETER / 2:
                    continue
                if abs(((ox - cx) * f["n"][0] + (oy - cy) * f["n"][1]) / dr) < 0.97:
                    continue
                rs = [((p[0] - ox) ** 2 + (p[1] - oy) ** 2) ** 0.5 for p in f["pts"]]
                r = mean(rs)
                if pstdev(rs) > 0.02:    # 3 頂点が同じ円に乗らない = 平らな面
                    continue
                buckets[round(r / 0.05)].append((r, f))
            if not buckets:
                continue
            # いちばん面数の多い半径を採る
            key = max(buckets, key=lambda k: len(buckets[k]))
            members = buckets[key]
            if len(members) < min_support:
                continue
            r = mean(m[0] for m in members)
            if r * 2 < MIN_DIAMETER or r > max_radius:
                continue
            span = _angular_span(members, ox, oy)
            if span < 60:                # 平らな壁は法線が扇形に広がらない
                continue
            lo = min(m[1]["lo"] for m in members)
            hi = max(m[1]["hi"] for m in members)
            if hi - lo < 0.2:
                continue
            inward = mean(
                ((ox - m[1]["c"][0]) * m[1]["n"][0] + (oy - m[1]["c"][1]) * m[1]["n"][1])
                for m in members)
            out.append({
                "axis": "XYZ"[axis], "d": r * 2, "depth": hi - lo,
                "center": (ox, oy), "from": lo, "to": hi,
                "kind": "穴" if inward > 0 else "外周",
                "faces": len(members), "span": span,
            })

    # 同じフィーチャが複数の峰から重複して出る。近いものを 1 つに畳む
    out.sort(key=lambda c: -c["faces"])
    kept = []
    for c in out:
        dup = False
        for k in kept:
            if (k["axis"] == c["axis"]
                    and abs(k["d"] - c["d"]) < 0.6
                    and abs(k["center"][0] - c["center"][0]) < 0.6
                    and abs(k["center"][1] - c["center"][1]) < 0.6):
                dup = True
                break
        if not dup:
            kept.append(c)
    return sorted(kept, key=lambda c: -c["d"])


def plate_orientation(matrix):
    """build の 4x3 行列から、造形時にどの軸が上を向いているかを返す。"""
    if not matrix or len(matrix) < 9:
        return None
    # 行優先 3x3。ローカル各軸がワールドでどこを向くか。
    cols = [(matrix[0], matrix[3], matrix[6]),
            (matrix[1], matrix[4], matrix[7]),
            (matrix[2], matrix[5], matrix[8])]
    up = max(range(3), key=lambda i: abs(cols[i][2]))
    sign = "+" if cols[up][2] > 0 else "-"
    return f"ローカル {sign}{'XYZ'[up]} が上"


# --------------------------------------------------------------------------
# 報告
# --------------------------------------------------------------------------

def report(path, max_cyl=12):
    lines = []
    with zipfile.ZipFile(path) as z:
        info = _part_names(z)
        tf = _build_transforms(z)
        parts = []
        for oid, verts, tris in _meshes(z):
            w, d, h = bbox(verts)
            parts.append({
                "id": oid, "name": info.get(oid, {}).get("name", ""),
                "stat": info.get(oid, {}).get("stat", {}),
                "size": (w, d, h), "tris": len(tris),
                "cyl": cylinders(verts, tris),
                "orient": plate_orientation(tf.get(oid)),
            })
        settings = _slice_settings(z)

    parts.sort(key=lambda p: -(p["size"][0] * p["size"][1] * p["size"][2]))
    lines.append(f"{path}")
    lines.append(f"部品 {len(parts)} 点 / 三角形 {sum(p['tris'] for p in parts):,}")
    if settings:
        lines.append("スライス設定: " + "  ".join(f"{k}={v}" for k, v in settings.items()))
    lines.append("")
    for p in parts:
        w, d, h = p["size"]
        head = f"[{p['id']}] {p['name'] or '(無名)'}"
        lines.append(head)
        lines.append(f"    外形 {w:.2f} x {d:.2f} x {h:.2f} mm   三角形 {p['tris']:,}")
        st = p["stat"]
        if st:
            bad = {k: v for k, v in st.items()
                   if k != "face_count" and v not in ("0", "")}
            lines.append("    メッシュ " + ("健全" if not bad else f"要注意 {bad}"))
        if p["orient"]:
            lines.append(f"    造形姿勢 {p['orient']}")
        for c in p["cyl"][:max_cyl]:
            lines.append(f"    ⌀{c['d']:6.2f} mm  深さ {c['depth']:5.2f} mm  {c['kind']}  "
                         f"軸={c['axis']}  中心=({c['center'][0]:.2f}, {c['center'][1]:.2f})")
        if len(p["cyl"]) > max_cyl:
            lines.append(f"    ... 他 {len(p['cyl']) - max_cyl} 個の円筒")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for f in sys.argv[1:]:
        print(report(f))
