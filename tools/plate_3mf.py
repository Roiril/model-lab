"""exports の STL を造形プレートに並べて 3mf にまとめる。

    py -3.11 tools/plate_3mf.py <出力名> <stl> [<stl> ...]
    py -3.11 tools/plate_3mf.py hug-arm-pla exports/hug-arm-upper-l.stl ...

Blender を使わない（STL を直に読んで 3mf を直に書く）。
書き出す STL は既に刷る向き（底面が z=0）になっている前提。

プリンタは exports の既存 3mf から読んだ Bambu Lab X1 Carbon の値に合わせる:
造形範囲 256 x 256 x 250mm / 手前左 18 x 28mm は除外域。
"""

import os
import re
import struct
import sys
import zipfile
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS = os.path.join(ROOT, "exports")

BED_X, BED_Y, BED_Z = 256.0, 256.0, 250.0
EXCLUDE = (18.0, 28.0)        # 手前左の除外域
MARGIN = 10.0                 # プレートの縁からの余白
GAP = 6.0                     # 部品どうしの間隔
WELD = 1e-4                   # 頂点をまとめる距離 [mm]

NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"


# ------------------------------------------------------------
# STL 読み取り
# ------------------------------------------------------------

def read_stl(path):
    """バイナリ / ASCII どちらの STL でも (頂点, 三角形) を返す。"""
    raw = open(path, "rb").read()
    tris = []
    if len(raw) > 84:
        n = struct.unpack("<I", raw[80:84])[0]
        if len(raw) == 84 + 50 * n:                     # バイナリ
            for i in range(n):
                o = 84 + 50 * i + 12                    # 法線 12 バイトを飛ばす
                tris.append(tuple(struct.unpack("<9f", raw[o:o + 36])))
    if not tris:                                        # ASCII
        txt = raw.decode("ascii", "replace")
        pts = [tuple(float(x) for x in m)
               for m in re.findall(r"vertex\s+(\S+)\s+(\S+)\s+(\S+)", txt)]
        tris = [tuple(pts[i] + pts[i + 1] + pts[i + 2]) for i in range(0, len(pts), 3)]

    index, verts, faces = {}, [], []
    for t in tris:
        f = []
        for k in range(3):
            p = (round(t[k * 3] / WELD), round(t[k * 3 + 1] / WELD), round(t[k * 3 + 2] / WELD))
            if p not in index:
                index[p] = len(verts)
                verts.append((p[0] * WELD, p[1] * WELD, p[2] * WELD))
            f.append(index[p])
        if f[0] != f[1] and f[1] != f[2] and f[0] != f[2]:
            faces.append(tuple(f))
    return verts, faces


def bbox(verts):
    xs, ys, zs = zip(*verts)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


# ------------------------------------------------------------
# 並べる（棚づめ）
# ------------------------------------------------------------

def arrange(parts, max_w):
    """[(名前, 頂点, 面)] を棚に並べ、[(…, dx, dy)] を返す。

    背の高い（Y に長い）ものから順に棚へ置き、幅が尽きたら次の棚へ移る。
    """
    sized = []
    for name, v, f in parts:
        lo, hi = bbox(v)
        sized.append([name, v, f, hi[0] - lo[0], hi[1] - lo[1], lo])
    sized.sort(key=lambda p: -p[4])

    placed, x, y, shelf_h = [], 0.0, 0.0, 0.0
    for name, v, f, w, h, lo in sized:
        if x > 0 and x + w > max_w:
            x, y, shelf_h = 0.0, y + shelf_h + GAP, 0.0
        placed.append((name, v, f, x - lo[0], y - lo[1]))
        x += w + GAP
        shelf_h = max(shelf_h, h)
    total = (max(p[3] + bbox(p[1])[1][0] for p in placed),
             y + shelf_h)
    return placed, total


def center_on_bed(placed, total):
    """並べた塊をプレートの中心へ寄せる。除外域に掛かるなら奥へ逃がす。"""
    ox = (BED_X - total[0]) / 2
    oy = (BED_Y - total[1]) / 2
    ox = max(ox, MARGIN)
    oy = max(oy, MARGIN)
    if ox < EXCLUDE[0] + 2 and oy < EXCLUDE[1] + 2:
        oy = EXCLUDE[1] + 2
    return [(n, v, f, dx + ox, dy + oy) for n, v, f, dx, dy in placed]


# ------------------------------------------------------------
# 3mf 書き出し
# ------------------------------------------------------------

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="config" ContentType="application/xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""


def write_3mf(path, placed, extruder=1):
    out = [f'<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<model xmlns="{NS}" unit="millimeter" xml:lang="en-US">\n'
           f' <metadata name="Application">model-lab plate_3mf</metadata>\n'
           f' <metadata name="CreationDate">{date.today().isoformat()}</metadata>\n'
           f' <resources>\n']
    for i, (name, verts, faces, dx, dy) in enumerate(placed, start=1):
        out.append(f'  <object id="{i}" type="model">\n   <mesh>\n    <vertices>\n')
        out += [f'     <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>\n' for x, y, z in verts]
        out.append('    </vertices>\n    <triangles>\n')
        out += [f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>\n' for a, b, c in faces]
        out.append('    </triangles>\n   </mesh>\n  </object>\n')
    out.append(' </resources>\n <build>\n')
    for i, (name, verts, faces, dx, dy) in enumerate(placed, start=1):
        out.append(f'  <item objectid="{i}" printable="1" '
                   f'transform="1 0 0 0 1 0 0 0 1 {dx:.4f} {dy:.4f} 0"/>\n')
    out.append(' </build>\n</model>\n')

    cfg = ['<?xml version="1.0" encoding="UTF-8"?>\n<config>\n']
    for i, (name, verts, faces, dx, dy) in enumerate(placed, start=1):
        cfg.append(f'  <object id="{i}">\n'
                   f'    <metadata key="name" value="{name}"/>\n'
                   f'    <metadata key="extruder" value="{extruder}"/>\n'
                   f'    <part id="{i}" subtype="normal_part">\n'
                   f'      <metadata key="name" value="{name}"/>\n'
                   f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
                   f'    </part>\n  </object>\n')
    cfg.append('</config>\n')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("3D/3dmodel.model", "".join(out))
        z.writestr("Metadata/model_settings.config", "".join(cfg))


# ------------------------------------------------------------

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    out_name = sys.argv[1]
    extruder = 1
    files = []
    for a in sys.argv[2:]:
        if a.startswith("--extruder="):
            extruder = int(a.split("=")[1])
        else:
            files.append(a)

    parts = []
    for f in files:
        v, t = read_stl(f)
        parts.append((os.path.splitext(os.path.basename(f))[0], v, t))
        lo, hi = bbox(v)
        print(f"[plate] {parts[-1][0]}: {hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f} x "
              f"{hi[2]-lo[2]:.1f}mm / 三角形 {len(t):,}")

    placed, total = arrange(parts, BED_X - 2 * MARGIN)
    placed = center_on_bed(placed, total)

    # 重なっていないことを枠の突き合わせで確かめる（棚づめの結果を信用しない）
    boxes = []
    for name, v, _, dx, dy in placed:
        lo, hi = bbox(v)
        boxes.append((name, lo[0] + dx, lo[1] + dy, hi[0] + dx, hi[1] + dy))
    worst = 0.0
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            ov = (min(a[3], b[3]) - max(a[1], b[1]), min(a[4], b[4]) - max(a[2], b[2]))
            if ov[0] > 0 and ov[1] > 0:
                print(f"[plate] ⚠ {a[0]} と {b[0]} が {ov[0]:.1f} x {ov[1]:.1f}mm 重なっている")
                worst = max(worst, min(ov))
    off_bed = [b[0] for b in boxes
               if b[1] < 0 or b[2] < 0 or b[3] > BED_X or b[4] > BED_Y
               or (b[1] < EXCLUDE[0] and b[2] < EXCLUDE[1])]
    print(f"[plate] 重なり {'なし' if worst == 0 else f'{worst:.1f}mm'} / "
          f"はみ出し・除外域 {'なし' if not off_bed else off_bed}")

    hi_z = max(bbox(v)[1][2] for _, v, _, _, _ in placed)
    fits = total[0] <= BED_X - 2 * MARGIN and total[1] <= BED_Y - 2 * MARGIN and hi_z <= BED_Z
    print(f"[plate] 占める広さ {total[0]:.0f} x {total[1]:.0f}mm / 最大高さ {hi_z:.1f}mm "
          f"→ {'入る' if fits else '⚠ プレートに入らない'}（256 x 256 x 250）")

    path = os.path.join(EXPORTS, out_name + ".3mf")
    write_3mf(path, placed, extruder)
    print(f"[plate] {path} ({os.path.getsize(path):,} バイト / {len(placed)} 部品 / "
          f"フィラメント {extruder})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
