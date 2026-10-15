"""刷れる機構のゲート。完了かどうかはこのコマンドの終了コードで決める（モデルの自己申告ではなく）。

  py -3.11 tools/mechgate.py new <名前>          spec.json の雛形を作る（依頼の要件をここに写す）
  py -3.11 tools/mechgate.py check <名前>        全検査を流して build/gate_report.json と gate_summary.md を書く。不合格なら exit 1
  py -3.11 tools/mechgate.py check <名前> --no-blender   Blender を使わない検査だけ（数秒。途中の確認用。合格にはならない）
  py -3.11 tools/mechgate.py fresh <名前>        gate_report が今のファイルと一致して合格か（速い。hook 用）
  py -3.11 tools/mechgate.py status              spec.json を持つ全モデルの状態
  py -3.11 tools/mechgate.py selftest            ハーネスの自己検査（計器・閾値を変えたら必ず流す）

手順と spec.json の書き方: .agents/skills/mechanism-gate/SKILL.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from mechgate_lib import gate as G  # noqa: E402

TEMPLATE = {
    "model": "<名前>",
    "request": "依頼文の原文をここに貼る（要件番号つき）",
    "requirements": [
        {"id": "R1", "text": "〈依頼の要件 1 を 1 行で〉", "checks": ["motion.interference", "interface.drive"]},
        {"id": "R2", "text": "〈要件 2〉", "checks": ["assembly.path", "manual:〈実物でしか確かめられないこと〉"]},
        {"id": "C3", "text": "共通条件 §3 見える面をサポート無しできれいに刷る", "checks": ["print.slice", "print.grounding", "print.slender"]},
        {"id": "C4", "text": "共通条件 §4 印刷部品と既製部品だけで、工具なしで組める", "checks": ["assembly.path", "interface.retention"]},
    ],
    "envelope_mm": [100, 100, 100],
    "uses": ["sg92r"],
    "parts": {"components": {}, "jigs": [], "slender_ok": {}},
    "motion": {"actuator": "sg92r_horn", "servo": "sg92r", "exclude": []},
    "allowances": [],
    "interfaces": [],
    "unknowns": [],
    "waivers": [],
}


def cmd_new(name):
    folder = ROOT / "models" / name
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "spec.json"
    if path.exists():
        print(f"既にある: {path.relative_to(ROOT).as_posix()}（上書きしない）")
        return 1
    doc = json.loads(json.dumps(TEMPLATE).replace("<名前>", name))
    G.C.write_json(path, doc)
    print(f"作った: {path.relative_to(ROOT).as_posix()}")
    print("次: 依頼の要件を requirements に写し、検査 id を割り当てる。書き方は .agents/skills/mechanism-gate/SKILL.md")
    return 0


def cmd_check(name, no_blender):
    doc = G.Gate(name, skip_blender=no_blender).run()
    width = max(len(c["id"]) for c in doc["checks"])
    for c in doc["checks"]:
        mark = "外" if c["waived"] else ("○" if c["pass"] else "×")
        req = "" if c["required"] else "（任意）"
        print(f"{mark} {c['id'].ljust(width)}  {c['summary']}{req}")
    print()
    if no_blender:
        print("--no-blender: Blender の検査は流していない。合格にはならない")
    verdict = "合格" if doc["pass"] else "不合格: " + ", ".join(doc["blocking"])
    print(f"判定 {verdict}")
    print(f"詳細 models/{name}/build/gate_report.json / gate_summary.md")
    return 0 if doc["pass"] and not no_blender else 1


def cmd_fresh(name):
    state, rows = G.freshness(name)
    labels = {"pass": "合格・最新", "fail": "不合格", "stale": "古い（検査の後にファイルが変わった）", "missing": "未実行"}
    print(f"{name}: {labels[state]}" + (f" {rows[:8]}" if rows else ""))
    return 0 if state == "pass" else 1


def cmd_status():
    code = 0
    for spec in sorted((ROOT / "models").glob("*/spec.json")):
        code |= cmd_fresh(spec.parent.name)
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("new").add_argument("model")
    check = sub.add_parser("check")
    check.add_argument("model")
    check.add_argument("--no-blender", action="store_true")
    sub.add_parser("fresh").add_argument("model")
    sub.add_parser("status")
    sub.add_parser("selftest")
    args = parser.parse_args()
    if args.cmd == "new":
        return cmd_new(args.model)
    if args.cmd == "check":
        return cmd_check(args.model, args.no_blender)
    if args.cmd == "fresh":
        return cmd_fresh(args.model)
    if args.cmd == "status":
        return cmd_status()
    from mechgate_lib import selftest
    return selftest.main()


if __name__ == "__main__":
    raise SystemExit(main())
