"""D 系ミステリーボックスの Bambu Studio 印刷設定。"""
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
HIDDEN_SUPPORT_OVERRIDES = {
    "enable_support": "1",
    "support_type": "tree(auto)",
    "support_on_build_plate_only": "1",
    "support_threshold_angle": "30",
    "support_top_z_distance": "0.2",
}
OUT = os.path.join(HERE, "build", "print")


def settings(material, support=False):
    """継承を解いた machine/process/filament の JSON を書き、パスを返す。"""
    if material not in FILAMENT:
        raise ValueError(f"unsupported material: {material}")
    machine = resolve("machine", MACHINE)
    process = resolve("process", PROCESS)
    process.update(OVERRIDES)
    if support:
        process.update(HIDDEN_SUPPORT_OVERRIDES)
    filament = resolve("filament", FILAMENT[material])
    suffix = "hidden_support" if support else "no_support"
    return (
        write_flat(os.path.join(OUT, "machine.json"), machine),
        write_flat(os.path.join(OUT, f"process_{suffix}.json"), process),
        write_flat(os.path.join(OUT, f"filament_{material}.json"), filament),
    )
