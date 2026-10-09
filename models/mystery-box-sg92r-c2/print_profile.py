"""このモデルを刷る設定。Bambu Studio 同梱の標準プロファイルを平らにして、ここで決めた値だけ上書きする。

ユーザーの既存プロジェクト（whistle.3mf ほか）は X1C 0.4 / Textured PEI Plate / 0.20mm Standard /
第 1 層の補正 0.15 / 壁 2 周 / 充填 15%。これを土台に、次だけ変える:
  - 継ぎ目は後ろ（箱は後ろ面が奥を向くように置くので、継ぎ目が蝶番側の面に集まる）
  - 壁 3 周（蝶番の節・ピン・クランクの肉を増やす。外観は変わらない）
  - 物体ごとに印刷を止められるようにする（失敗した小物だけ外して続けられる）
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../lib"))

from bambu_profiles import resolve, write_flat  # noqa: E402

MACHINE = "Bambu Lab X1 Carbon 0.4 nozzle"
PROCESS = "0.20mm Standard @BBL X1C"
FILAMENT = {"PLA": "Bambu PLA Basic @BBL X1C", "PETG": "Bambu PETG Basic @BBL X1C"}
OVERRIDES = {
    "curr_bed_type": "Textured PEI Plate",
    "seam_position": "back",
    "wall_loops": "3",
    "exclude_object": "1",
    "enable_support": "0",
}
OUT = os.path.join(HERE, "build", "print")


def settings(material):
    """平らにした (machine, process, filament) の JSON を build/print/ に書き、パスを返す。"""
    m = resolve("machine", MACHINE)
    p = resolve("process", PROCESS)
    p.update(OVERRIDES)
    f = resolve("filament", FILAMENT[material])
    return (write_flat(os.path.join(OUT, "machine.json"), m),
            write_flat(os.path.join(OUT, "process.json"), p),
            write_flat(os.path.join(OUT, f"filament_{material}.json"), f))
