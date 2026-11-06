"""探索した歩き方を firmware/slab_walker/gait.h へ書き出し、ファームと同じ折れ線で確かめ直す。

    py -3.10 models/phone-slab-walker/sim_gait.py --firmware --n 300 --seeds 10 --workers 10
    py -3.10 models/phone-slab-walker/export_gait.py

出力: firmware/slab_walker/gait.h、build/gait_report.json
シミュレーションは比べるためのもの。実機の距離を保証しない。
"""
import json
import sys
from pathlib import Path

import sim_gait as S

HERE = Path(__file__).parent
BUILD = HERE / "build"
HEADER = HERE / "firmware" / "slab_walker" / "gait.h"
LIMIT_DEG = 45
TURN_TRIM_DEG = 6
TRIM_MAX_DEG = 8


def write_header(keys, seed):
    lines = [
        "// 歩き方の波形。export_gait.py が build/gait_firmware.json から書き出す（手で直さない）。",
        f"// 出どころ: 探索の種 {seed}",
        "#pragma once",
        "#include <avr/pgmspace.h>",
        "",
        "struct GaitKey {",
        "  int8_t left;    // deg（前が正）",
        "  int8_t right;   // deg",
        "  uint16_t ms;    // この姿勢まで何 ms かけるか",
        "};",
        "",
        "const GaitKey GAIT_WALK[] PROGMEM = {",
    ]
    lines += [f"  {{{left}, {right}, {ms}}}," for left, right, ms in keys]
    lines += ["};", f"const uint8_t GAIT_WALK_LEN = {len(keys)};", f"const int8_t TURN_TRIM_DEG = {TURN_TRIM_DEG};", ""]
    HEADER.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def summarize(result):
    return dict(forward_mm=round(result["forward_mm"]), lateral_mm=round(result["lateral_mm"]),
                yaw_deg=round(result["yaw_deg"]), fell_at=result["fell_at"],
                peak_nm=round(result["peak_tau"], 2), tilt_max=round(result["tilt_max"], 1))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    best = json.loads((BUILD / "gait_firmware.json").read_text(encoding="utf-8"))[0]
    keys = S.firmware_keys(best["params"])
    base = S.run_condition(keys, S.CONDITIONS[0])
    if base["forward_mm"] < 0:
        # 探索は向きを問わない。後ろへ進む波形なら符号を反転して前へ進ませる
        keys = [(-left, -right, ms) for left, right, ms in keys]
    assert max(abs(v) for k in keys for v in k[:2]) + TRIM_MAX_DEG <= LIMIT_DEG, "可動域を超える"

    rows = {c["name"]: summarize(S.run_condition(keys, c)) for c in S.CONDITIONS}
    reference = S.CONDITIONS[0]
    rows["ジャイロつきで 40 秒"] = summarize(S.run_condition(keys, reference, seconds=40.0))
    rows["後ろへ（符号反転）"] = summarize(S.run_condition(keys, reference, sign=-1.0))
    still = S.rollout(3.0, dict(period=1.0, knots=[0, 0, 0, 0], durs=[1, 1, 1, 1], phase=0.0), seconds=5.0)
    rows["校正: 指令なしなら進まず転ばない"] = summarize(still)
    for name, row in rows.items():
        print(name, row)

    survived = [rows[c["name"]] for c in S.CONDITIONS]
    assert all(row["fell_at"] is None for row in survived), "転ぶ条件がある"
    straight = [rows[c["name"]] for c in S.CONDITIONS if "turn" not in c]
    assert all(row["forward_mm"] > 0 for row in straight), "前へ進まない条件がある"
    assert rows["後ろへ（符号反転）"]["forward_mm"] < 0, "後ろへ進まない"
    assert abs(still["forward_mm"]) < 1 and still["fell_at"] is None, "校正に失敗"

    write_header(keys, best["seed"])
    period = sum(k[2] for k in keys) / 1000.0
    report = dict(seed=best["seed"], params=best["params"], periodS=round(period, 3), keys=len(keys), rows=rows,
                  worstForwardMmPerS=round(min(r["forward_mm"] for r in straight) / 12.0, 1),
                  note="MuJoCo の比較。実機で歩かせて確かめるまで距離は保証しない")
    (BUILD / "gait_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("gait.h", len(keys), "keys", round(period, 3), "s")


if __name__ == "__main__":
    main()
