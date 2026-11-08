# -*- coding: utf-8 -*-
"""ROBOTIS HX5-D20（右手）の組み立て済み STL 21 個を 1 個にまとめ、exports/robotis-hx5-d20.stl に書く。

  ./run.sh models/robotis-hx5-d20/model.py（bpy を使わないので py -3.11 でも動く）

入力は params.py の SRC_DIR（Drive の design-study に置いた組み立て結果。元データと組み立て手順は README.md）。
単位は元の STL のまま（m）。
"""
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import SRC_DIR, PART_COUNT  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "exports" / "robotis-hx5-d20.stl"


def read_binary_stl(path):
    b = path.read_bytes()
    n = struct.unpack("<I", b[80:84])[0]
    if len(b) != 84 + 50 * n:
        raise ValueError(f"バイナリ STL ではありません: {path}")
    return n, b[84:]


def main():
    src = Path(SRC_DIR)
    files = sorted(src.glob("*.stl"))
    if len(files) != PART_COUNT:
        raise SystemExit(f"STL が {PART_COUNT} 個ではありません（{len(files)} 個）: {src}")
    total, body = 0, []
    for f in files:
        n, tri = read_binary_stl(f)
        total += n
        body.append(tri)
    header = b"robotis-hx5-d20 right hand, merged".ljust(80, b" ")
    tmp = OUT.with_suffix(".stl.tmp")
    with open(tmp, "wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", total))
        for tri in body:
            fh.write(tri)
    os.replace(tmp, OUT)
    print(f"{len(files)} 部品、{total} 三角形 → {OUT}")


if __name__ == "__main__":
    main()
