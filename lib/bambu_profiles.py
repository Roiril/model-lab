"""Bambu Studio 同梱の標準プロファイルを、継承（inherits）をたどって 1 つの設定に平らにする。

Bambu Studio の CLI は --load-settings で渡した JSON の inherits をたどらない。
そのまま渡すと親で決まっている値（第 1 層のはみ出し補正 0.15 など）が抜け、
CLI の内蔵既定値（0 や Cool Plate）で切られる（2026-10-10 に実測）。
ここで親から順に重ねた完全な設定を作り、それを CLI に渡す。

    from bambu_profiles import resolve, write_flat
    proc = resolve("process", "0.20mm Standard @BBL X1C")
"""
import glob
import json
import os

PROFILE_ROOT = r"C:\Program Files\Bambu Studio\resources\profiles\BBL"
_INDEX = {}


def _index(kind):
    if kind not in _INDEX:
        idx = {}
        for path in glob.glob(os.path.join(PROFILE_ROOT, kind, "**", "*.json"), recursive=True):
            try:
                d = json.load(open(path, encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(d, dict) and "name" in d:
                idx[d["name"]] = d
        _INDEX[kind] = idx
    return _INDEX[kind]


def resolve(kind, name):
    """kind = machine / process / filament。親から順に重ねた dict を返す。"""
    idx = _index(kind)
    chain = []
    cur = name
    while cur:
        if cur not in idx:
            raise KeyError(f"{kind} プロファイル {cur!r} が見つからない")
        d = idx[cur]
        chain.append(d)
        cur = d.get("inherits", "")
    flat = {}
    for d in reversed(chain):
        flat.update(d)
    flat["inherits"] = ""
    flat["name"] = name
    flat["from"] = "system"
    return flat


def write_flat(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    return path


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    p = resolve("process", "0.20mm Standard @BBL X1C")
    m = resolve("machine", "Bambu Lab X1 Carbon 0.4 nozzle")
    f = resolve("filament", "Bambu PLA Basic @BBL X1C")
    for k in ("elefant_foot_compensation", "wall_loops", "seam_position", "sparse_infill_density", "brim_type",
              "top_shell_layers", "bottom_shell_layers", "outer_wall_line_width", "xy_hole_compensation"):
        print("process", k, p.get(k))
    for k in ("printable_area", "bed_exclude_area", "default_bed_type", "nozzle_diameter"):
        print("machine", k, m.get(k))
    for k in ("nozzle_temperature", "textured_plate_temp", "cool_plate_temp", "filament_density"):
        print("filament", k, f.get(k))
