"""刷りやすさ・仕上がりの精査（Blender の Python で走らせる）。

    "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python models/servo-lid-cube/print_review.py

組んだ姿勢の STL（build/<部品>.stl）と、部品ごとの「刷るときの上向き」で調べる。
  1. 接地: ベッドに付く面積、重心が接地の外接矩形の中にあるか、高さと接地の幅の比
  2. 宙に浮く面: 45° より寝た下向き面の塊と、その外側のすぐ下に肉があるか
  3. 肉厚: 面の内側へ打った光線が反対の面に当たるまでの距離
  4. 段差: 水平から 25° より寝た上向きの斜面
出力: build/print_review.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lib"))
sys.stdout.reconfigure(encoding="utf-8")

from meshkit import Mesh  # noqa: E402
from printmech.printability import (  # noqa: E402
    calibrate, calibration_plate as plate, calibration_wedge as wedge,
    faces, review as _review,
)

BUILD = os.path.join(HERE, "build")
LAYER = 0.2
UP = {"box": (0, 0, 1), "lid": (0, 0, -1), "crank": (1, 0, 0),
      "link": (1, 0, 0), "clip": (-1, 0, 0), "pin": (0, 0, 1)}


def exterior(center):
    """組んだ姿勢で立方体の外から見える面か。"""
    return abs(center.x) > 37.2 or abs(center.y) > 37.2 or center.z < 2.8 or center.z > 77.2


def review(mesh, up, ext_check=False):
    """既存モデルの呼び出し方を保ち、共有検査へ外面判定を渡す。"""
    return _review(mesh, up, exterior_test=exterior if ext_check else None, layer=LAYER)


def main():
    out = {"calibration": calibrate()}
    print("calibration", json.dumps(out["calibration"], ensure_ascii=False))
    out["parts"] = {}
    for name, up in UP.items():
        mesh = Mesh.load(os.path.join(BUILD, f"{name}.stl"), name)
        result = review(mesh, up, ext_check=name in ("box", "lid"))
        out["parts"][name] = result
        print(f"\n== {name}  bed {result['bed']}")
        print("   thin(<1.2):", result["thin_under_1_2mm"][:8])
        print("   terrace exterior mm2:", result["terrace_exterior_mm2"],
              result["terrace_under_25deg"][:6])
        print("   overhang:", [(cluster["area_mm2"], cluster["supported"], cluster["h"], cluster["at"])
                              for cluster in result["overhang_clusters"][:8]])
    with open(os.path.join(BUILD, "print_review.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
