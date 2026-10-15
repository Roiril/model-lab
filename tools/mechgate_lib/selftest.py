"""ゲートの自己検査。小さな合成機構を作り、正常な版が合格し、過去の失敗を注入した版が狙った検査で落ちることを確かめる。

py -3.11 tools/mechgate.py selftest

注入する故障（どれも model-lab で実際に起きた型）:
- 駆動の界面が離れている        … C3 で歯車が Boolean 後に消え、共通体積 0 だけで駆動成立とみなした
- 圧入の当たりが長い行程に続く   … C4-3 の板カムが 87mm の軸を潰しリブ全長で擦り、実物で通らなかった
- 宣言が上限を超える            … 許可を広げてゲートを通すことを防ぐ
- 動作中に部品が食い込む
- 動く部品が駆動の界面につながっていない
- 抜け止めの相手が遠い          … tangible の落下止めが歯丈 2.25mm に対し 4.85mm 上にあった
- 刷る部品が 2 つに分かれて浮く  … C2 の蓋の腕が天面につながっていなかった
- 閉じていない STL
- 既製部品の仮値を扱っていない   … C4-3 の配線の窓をコネクタ寸法の仮定で作り、実物で通らなかった
"""
from __future__ import annotations

import json
import os
import shutil
import struct
import time
from pathlib import Path

import numpy as np

from . import gate as G

ROOT = G.ROOT
NAME = "_mechgate_selftest"


def box(lo, hi):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = np.array([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                  (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], dtype=float)
    f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
         (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return v[np.array(f)]


def write_stl(path, tris):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        fh.write(b"mechgate selftest".ljust(80, b" "))
        fh.write(struct.pack("<I", len(tris)))
        for t in tris:
            fh.write(struct.pack("<3f", 0, 0, 0))
            fh.write(struct.pack("<9f", *np.asarray(t, dtype=np.float32).reshape(-1)))
            fh.write(b"\0\0")


def to_bed(tris):
    out = tris.copy()
    out[:, :, 2] -= out[:, :, 2].min()
    return out


def translation(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def col(m):
    return [float(v) for v in m.T.reshape(-1)]


def base_design():
    parts = {
        "base": box((-20, -15, 0), (40, 15, 5)),
        "wall": box((-20, 5.5, 5), (10, 8, 12)),
        "rib": box((31.9, 6, 5.5), (36, 12, 7.0)),
        "pin": box((30, 8, 5.5), (32, 10, 15.5)),
        "pusher": box((-15, -5, 5.3), (-5, 5, 10.3)),
        "slider": box((-4.8, -5, 5.3), (4.8, 5, 10.3)),
    }
    lying = {"pin"}
    spec = {
        "model": NAME,
        "requirements": [
            {"id": "R1", "text": "押し棒がスライダーを押して動かす", "checks": ["motion.interference", "interface.drive"]},
            {"id": "R2", "text": "工具なしで組める", "checks": ["assembly.path", "manual:手で押し込めるか"]},
            {"id": "R3", "text": "サポート無しで刷れる", "checks": ["parts.topology", "print.grounding"]},
        ],
        "envelope_mm": [70, 40, 20],
        "uses": [],
        "motion": {"actuator": "pusher", "servo": "sg92r"},
        "allowances": [
            {"type": "press_fit", "pairs": [["pin", "rib"]], "insertion_mm": 2.0, "basis": "リブ 0.1mm x 最後の 1.5mm"},
            {"type": "static_fit", "pairs": [["pin", "rib"]], "max_mm3": 0.5, "basis": "0.1 x 2 x 1.5 = 0.3mm3"},
        ],
        "interfaces": [
            {"id": "push", "type": "drive", "driver": "pusher", "driven": "slider", "sides": "one_sided"},
            {"id": "slider-y", "type": "retention", "part": "slider", "direction": [0, 1, 0], "max_free_mm": 1.0},
        ],
        "unknowns": [],
        "waivers": [{"check": "print.slice", "reason": "selftest は刷らない"}],
    }

    def motion(deg):
        s = translation(0.1 * deg)
        return {"pusher": s, "slider": s}

    steps = [
        ("place", ["base", "wall", "rib"], lambda t: {p: np.eye(4) for p in ("base", "wall", "rib")}, 2),
        ("slider", ["slider"], lambda t: {"slider": translation(0, 0, 6 * (1 - t))}, 7),
        ("pusher", ["pusher"], lambda t: {"pusher": translation(0, 0, 6 * (1 - t))}, 7),
        ("pin", ["pin"], lambda t: {"pin": translation(0, 0, 10 * (1 - t))}, 21),
    ]
    return {"parts": parts, "lying": lying, "spec": spec, "motion": motion, "steps": steps, "extra_motion": {}}


def materialize(design):
    folder = ROOT / "models" / NAME
    if folder.exists():
        shutil.rmtree(folder)
    build = folder / "build"
    manifest = []
    for pid, tris in design["parts"].items():
        write_stl(build / f"{pid}.stl", tris)
        printed = tris
        if pid in design["lying"]:
            printed = tris[:, :, [2, 1, 0]][:, ::-1]   # X と Z を入れ替え（向きを保つため頂点順を逆に）
        write_stl(build / f"print_{pid}.stl", to_bed(design.get("print_override", {}).get(pid, printed)))
        manifest.append({"id": pid, "assembly": f"build/{pid}.stl", "print": f"build/print_{pid}.stl"})
    G.C.write_json(build / "manifest.json", {"meta": {}, "parts": manifest})
    frames = []
    for deg in range(0, 31):
        tf = {p: np.eye(4) for p in design["parts"]}
        tf.update(design["motion"](deg))
        for pid, fn in design["extra_motion"].items():
            tf[pid] = fn(deg)
        frames.append({"servo_deg": float(deg), "transforms": {p: col(m) for p, m in tf.items()}})
    G.C.write_json(build / "motion.json", {"frames": frames})
    state, steps = {}, []
    for sid, moving, path, n in design["steps"]:
        rows = []
        for i in range(n):
            t = i / (n - 1)
            tf = dict(state)
            tf.update(path(t))
            rows.append({"progress": t, "transforms": {p: col(m) for p, m in tf.items()}})
        state.update(path(1.0))
        steps.append({"id": sid, "title": sid, "moving": moving, "frames": rows})
    G.C.write_json(build / "assembly.json", {"steps": steps, "calibration": {"pass": True}, "pass": True})
    G.C.write_json(folder / "spec.json", design["spec"])


def fault_cases():
    cases = []

    def case(name, expect, mutate, blender=True):
        cases.append({"name": name, "expect": expect, "mutate": mutate, "blender": blender})

    def drive_gap(d):
        d["parts"]["slider"] = box((-2.0, -5, 5.3), (7.6, 5, 10.3))
    case("駆動の界面が 3mm 離れている（歯車の欠落）", "interface.drive", drive_gap)

    def long_rib(d):
        d["parts"]["rib"] = box((31.9, 6, 5.5), (36, 12, 13.5))
    case("圧入の当たりが最後の 2mm を超えて 8mm 続く", "assembly.path", long_rib)

    def over_cap(d):
        d["spec"]["allowances"][0]["insertion_mm"] = 87.0
    case("圧入の差し込み長さを上限を超えて宣言する", "spec.valid", over_cap, blender=False)

    def sink(d):
        d["parts"]["slider"] = box((-4.8, -5, 4.5), (4.8, 5, 9.5))
    case("動作中にスライダーが台に 0.5mm 食い込む", "motion.interference", sink)

    def orphan(d):
        d["parts"]["flag"] = box((-12, -14, 5.3), (-8, -10, 8))
        d["extra_motion"]["flag"] = lambda deg: (translation(-10, -12) @ np.array(
            [[np.cos(np.radians(deg)), -np.sin(np.radians(deg)), 0, 0], [np.sin(np.radians(deg)), np.cos(np.radians(deg)), 0, 0],
             [0, 0, 1, 0], [0, 0, 0, 1]]) @ translation(10, 12))
        d["steps"].append(("flag", ["flag"], lambda t: {"flag": translation(0, 0, 6 * (1 - t))}, 7))
    case("回る部品が駆動の界面につながっていない", "interface.coverage", orphan, blender=False)

    def far_wall(d):
        d["parts"]["wall"] = box((-20, 9, 5), (10, 11, 12))
    case("抜け止めの壁が 4mm 離れている", "interface.retention", far_wall)

    def floating(d):
        d["print_override"] = {"base": np.concatenate([box((-20, -15, 0), (40, 15, 5)), box((50, 0, 3), (55, 5, 8))])}
    case("刷る部品が 2 つに分かれ、片方が浮いている", "parts.components", floating, blender=False)

    def open_mesh(d):
        d["parts"]["wall"] = d["parts"]["wall"][:-1]
    case("STL が 1 面欠けて閉じていない", "parts.topology", open_mesh, blender=False)

    def tunnel(d):
        # ピンを 20mm 上から 2 フレームだけで下ろす。途中に 0.6mm の板があり、フレームの上では当たらない
        d["parts"]["fence"] = box((29, 7, 20), (33, 11, 20.6))
        steps = []
        for s in d["steps"]:
            if s[0] == "place":
                s = ("place", ["base", "wall", "rib", "fence"],
                     lambda t: {p: np.eye(4) for p in ("base", "wall", "rib", "fence")}, 2)
            if s[0] == "pin":
                s = ("pin", ["pin"], lambda t: {"pin": translation(0, 0, 20 * (1 - t))}, 2)
            steps.append(s)
        d["steps"] = steps
    case("組立の刻みが 10mm で、0.6mm の板をすり抜ける", "assembly.path", tunnel)

    def unknown(d):
        d["spec"]["uses"] = ["sg92r"]
    case("SG92R を使うのに仮値の扱いを書いていない", "unknowns.resolved", unknown, blender=False)
    return cases


def run_case(design, blender):
    materialize(design)
    gate = G.Gate(NAME, skip_blender=not blender)
    doc = gate.run()
    failing = {c["id"] for c in doc["checks"] if c["required"] and not c["pass"] and not c["waived"]}
    failing.discard("harness.calibrated")
    if not blender:
        failing -= {"instrument.calibration", "parts.self_intersection", "motion.interference",
                    "interface.drive", "interface.retention", "assembly.path"}
    return failing, doc


def main():
    os.environ["MECHGATE_SELFTEST"] = "1"
    started = time.time()
    results = []
    try:
        failing, doc = run_case(base_design(), blender=True)
        results.append({"case": "正常な版", "expect": "合格", "failing": sorted(failing), "pass": not failing})
        print(("OK " if not failing else "NG ") + f"正常な版: 落ちた検査 {sorted(failing) or 'なし'}", flush=True)
        if failing:
            print(json.dumps([c for c in doc["checks"] if c["id"] in failing], ensure_ascii=False, indent=1)[:4000])
        for item in fault_cases():
            design = base_design()
            item["mutate"](design)
            failing, doc = run_case(design, item["blender"])
            ok = item["expect"] in failing
            results.append({"case": item["name"], "expect": item["expect"], "failing": sorted(failing), "pass": ok})
            print(("OK " if ok else "NG ") + f"{item['name']}: 狙い {item['expect']} / 落ちた検査 {sorted(failing)}", flush=True)
    finally:
        shutil.rmtree(ROOT / "models" / NAME, ignore_errors=True)
    passed = all(r["pass"] for r in results)
    stamp = {"harness_sha": G.harness_sha(), "pass": passed, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
             "seconds": round(time.time() - started, 1), "results": results}
    G.C.write_json(G.STAMP, stamp)
    print(f"selftest {'合格' if passed else '不合格'}（{stamp['seconds']} 秒）。記録: {G.STAMP.relative_to(ROOT).as_posix()}")
    return 0 if passed else 1
