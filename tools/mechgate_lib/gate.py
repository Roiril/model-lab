"""ゲート本体。spec.json と build/ の契約ファイルから全検査を流し、build/gate_report.json を書く。

モデルの自前の verify.py の結果は読まない。同じ STL と姿勢から、ハーネスの計器で測り直す。
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "lib" / "printmech"))

import contract as C  # noqa: E402

from . import limits as L  # noqa: E402
from . import meshcheck as M  # noqa: E402

BLENDER = os.environ.get("BLENDER_EXE", r"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe")
HARNESS_FILES = [
    "tools/mechgate.py",
    "tools/mechgate_lib/__init__.py",
    "tools/mechgate_lib/limits.py",
    "tools/mechgate_lib/meshcheck.py",
    "tools/mechgate_lib/gate.py",
    "tools/mechgate_lib/bl_job.py",
    "tools/mechgate_lib/selftest.py",
    "lib/printmech/solid_meter.py",
    "lib/printmech/contract.py",
    "lib/solid_volume.py",
]
STAMP = ROOT / "tools" / "mechgate_lib" / "selftest_stamp.json"
LEDGER = ROOT / "lib" / "printmech" / "parts_ledger.json"
TRUSTED_SOURCES = {"measured", "datasheet", "printed_ok"}

# 検査の一覧。id は spec.json の requirements[].checks に書く名前
CHECKS = {
    "harness.calibrated": "ハーネスの計器が selftest を通った版のままか",
    "spec.valid": "spec.json が揃っていて、許可・界面の宣言がハーネスの上限の中か",
    "contract.files": "manifest / motion / assembly と全 STL がそろっているか",
    "instrument.calibration": "共通体積と初接触の計器が正負の形で期待どおりに出たか",
    "parts.topology": "全 STL が閉じて向きのそろった多様体か（面積 0 の三角形も無し）",
    "parts.components": "刷る STL の連結成分の数が宣言どおりか（既定 1）",
    "parts.self_intersection": "刷る STL に自己交差が無いか",
    "print.grounding": "刷る向きでベッドに十分な面積で接し、浮いた成分が無いか",
    "print.slender": "立てて刷る部品の高さが接地の短辺の 5 倍以内か",
    "assembly.envelope": "組んだ外形が spec の上限に収まるか",
    "motion.resolution": "motion.json の刻みが 2.5° 以下か",
    "motion.interference": "動く全範囲で、許可の無い部品の組の共通体積が 0 か",
    "motion.torque": "重力だけで見積もった必要トルクが停動トルクの 1/3 以下か",
    "interface.coverage": "動く部品の塊がすべて、駆動の界面でアクチュエータにつながっているか",
    "interface.drive": "駆動の界面ごとに、従動側を押すと遊びの中で駆動側に当たるか",
    "interface.retention": "抜け止めごとに、外れる向きへ動かすと上限までに止まるか",
    "assembly.path": "組立の各工程で、許可の範囲の外の当たりが無く、最後に全部品が組まれるか",
    "unknowns.resolved": "既製部品の仮値・未確認の寸法がすべて扱いを決められているか（試し刷りの部品など）",
    "print.slice": "スライス済みのプレートで、サポート無し・外に見える支えの無い押し出しが上限以下か",
}
NON_WAIVABLE = {"harness.calibrated", "spec.valid", "contract.files", "instrument.calibration",
                "parts.topology", "motion.interference", "interface.coverage", "interface.drive",
                "assembly.path", "unknowns.resolved"}
ALLOWANCE_TYPES = {"press_fit", "snap", "static_fit", "reference_internal"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def harness_sha():
    h = hashlib.sha256()
    for rel in HARNESS_FILES:
        h.update(rel.encode())
        h.update(sha256(ROOT / rel).encode())
    return h.hexdigest()


class Gate:
    def __init__(self, model, skip_blender=False):
        self.model = model
        self.dir = ROOT / "models" / model
        self.build = self.dir / "build"
        self.rows = {}
        self.skip_blender = skip_blender
        self.inputs = {}

    # --- 記録 ------------------------------------------------------------------------------
    def put(self, check, passed, summary, detail=None):
        self.rows[check] = {"id": check, "title": CHECKS[check], "pass": bool(passed),
                            "summary": summary, "detail": detail}

    def track(self, path):
        path = Path(path)
        if path.exists():
            self.inputs[path.relative_to(ROOT).as_posix()] = sha256(path)

    # --- 読み込み --------------------------------------------------------------------------
    def load(self):
        spec_path = self.dir / "spec.json"
        if not spec_path.exists():
            raise SystemExit(f"spec.json が無い: {spec_path}\n  py -3.11 tools/mechgate.py new {self.model} で雛形を作る")
        self.spec = C.read_json(spec_path)
        self.track(spec_path)
        self.manifest = C.read_json(self.build / "manifest.json") if (self.build / "manifest.json").exists() else None
        self.motion = C.read_json(self.build / "motion.json") if (self.build / "motion.json").exists() else None
        self.assembly = C.read_json(self.build / "assembly.json") if (self.build / "assembly.json").exists() else None
        for name in ("manifest.json", "motion.json", "assembly.json"):
            self.track(self.build / name)
        for source in sorted(self.dir.glob("*.py")):
            self.track(source)

    def part_paths(self):
        parts = [p for p in self.manifest["parts"] if not p.get("fit_only")]
        assembly = {p["id"]: self.dir / p["assembly"] for p in parts}
        prints = {p["id"]: self.dir / p["print"] for p in parts if p.get("print")}
        return assembly, prints

    # --- 検査 ------------------------------------------------------------------------------
    def check_harness(self):
        current = harness_sha()
        stamp = C.read_json(STAMP) if STAMP.exists() else {}
        ok = stamp.get("harness_sha") == current and stamp.get("pass") is True
        self.harness = {"sha": current, "stamp": stamp.get("harness_sha"), "stampedAt": stamp.get("at")}
        self.put("harness.calibrated", ok,
                 "selftest を通った版" if ok else
                 "ハーネスが selftest 後に変わった。py -3.11 tools/mechgate.py selftest を流す", self.harness)

    def check_spec(self):
        spec, errors = self.spec, []
        ids = {p["id"] for p in self.manifest["parts"]} if self.manifest else set()
        reqs = spec.get("requirements") or []
        if not reqs:
            errors.append("requirements が空。依頼の要件を 1 行ずつ書き、検査 id を割り当てる")
        for r in reqs:
            if not r.get("id") or not r.get("text"):
                errors.append(f"要件に id か text が無い: {r}")
            if not r.get("checks"):
                errors.append(f"{r.get('id')}: checks が空。数で確かめる検査 id か manual:<実物での確かめ方> を書く")
            for c in r.get("checks", []):
                if c not in CHECKS and not c.startswith("manual:"):
                    errors.append(f"{r.get('id')}: 知らない検査 id {c}")
        for a in spec.get("allowances", []):
            t = a.get("type")
            if t not in ALLOWANCE_TYPES:
                errors.append(f"許可の type が不明: {t}")
                continue
            if not a.get("basis"):
                errors.append(f"許可 {t} {a.get('pairs')} に basis（なぜ当たってよいか・量の根拠）が無い")
            for pair in a.get("pairs", []):
                if len(pair) != 2 or any(p not in ids for p in pair):
                    errors.append(f"許可 {t} の部品が manifest に無い: {pair}")
            if t == "press_fit" and not (0 < a.get("insertion_mm", 0) <= L.PRESS_FIT_MAX_INSERTION_MM):
                errors.append(f"press_fit {a.get('pairs')}: insertion_mm は 0〜{L.PRESS_FIT_MAX_INSERTION_MM}mm（差し込みの最後だけ）")
            if t == "snap":
                if not (0 < a.get("engage_mm", 0) <= L.SNAP_MAX_ENGAGE_MM):
                    errors.append(f"snap {a.get('pairs')}: engage_mm は 0〜{L.SNAP_MAX_ENGAGE_MM}mm")
                if not (0 < a.get("strain_percent", 99) <= L.SNAP_MAX_STRAIN_PERCENT):
                    errors.append(f"snap {a.get('pairs')}: strain_percent は {L.SNAP_MAX_STRAIN_PERCENT}% 以下（計算を basis に書く）")
            if t == "static_fit" and not (0 < a.get("max_mm3", 0) <= L.STATIC_FIT_MAX_MM3):
                errors.append(f"static_fit {a.get('pairs')}: max_mm3 は 0〜{L.STATIC_FIT_MAX_MM3}")
            if t == "reference_internal" and not (0 < a.get("max_mm3", 0) <= L.REFERENCE_INTERNAL_MAX_MM3):
                errors.append(f"reference_internal {a.get('pairs')}: max_mm3 は 0〜{L.REFERENCE_INTERNAL_MAX_MM3}")
        for i in spec.get("interfaces", []):
            if i.get("type") == "drive":
                if i.get("driver") not in ids or i.get("driven") not in ids:
                    errors.append(f"界面 {i.get('id')}: driver / driven が manifest に無い")
                if i.get("sides", "both") not in ("both", "one_sided"):
                    errors.append(f"界面 {i.get('id')}: sides は both か one_sided")
            elif i.get("type") == "retention":
                group = i.get("parts") or [i.get("part")]
                if any(p not in ids for p in group) or len(i.get("direction", [])) != 3 or "max_free_mm" not in i:
                    errors.append(f"抜け止め {i.get('id')}: part（または parts）・direction[3]・max_free_mm が要る")
            else:
                errors.append(f"界面の type が不明: {i.get('type')}（drive / retention）")
            if not i.get("id"):
                errors.append(f"界面に id が無い: {i}")
        for w in spec.get("waivers", []):
            if w.get("check") in NON_WAIVABLE:
                errors.append(f"{w.get('check')} は外せない検査")
            if not w.get("reason"):
                errors.append(f"waiver {w.get('check')} に reason が無い")
        self.put("spec.valid", not errors, "宣言はハーネスの上限の中" if not errors else f"{len(errors)} 件の問題", errors)

    def check_contract(self):
        problems = []
        if self.manifest is None:
            problems.append("build/manifest.json が無い")
        else:
            assembly, prints = self.part_paths()
            for pid, path in list(assembly.items()) + list(prints.items()):
                if not path.exists():
                    problems.append(f"{pid}: STL が無い {path.relative_to(ROOT).as_posix()}")
                else:
                    self.track(path)
        moving = bool(self.spec.get("motion"))
        if moving and self.motion is None:
            problems.append("spec に motion があるのに build/motion.json が無い")
        if self.assembly is None and not self.spec.get("single_part"):
            problems.append("build/assembly.json が無い（1 部品だけなら spec に single_part: true）")
        self.put("contract.files", not problems, "そろっている" if not problems else f"{len(problems)} 件欠け", problems)
        return not problems

    def check_meshes(self):
        assembly, prints = self.part_paths()
        expect = self.spec.get("parts", {}).get("components", {})
        slender_ok = self.spec.get("parts", {}).get("slender_ok", {})
        topo_bad, comp_bad, ground_bad, slender_bad = {}, {}, {}, {}
        self.mass = {}
        self.bounds = {}
        reference_notes = {}
        for pid, path in assembly.items():
            tris = M.read_stl(path)
            self.bounds[pid] = M.bounds(tris)
            t = M.topology(tris)
            if pid not in prints and not t["pass"] and t["edgesNotSharedByTwo"] == 0                     and t["edgesWithSameDirectionTwice"] == 0 and t["signedVolumeMm3"] > 0:
                reference_notes[pid] = t     # 既製部品の正本: 閉じて向きがそろっていれば計器は使える
            elif not t["pass"]:
                topo_bad[f"{pid} (assembly)"] = t
            if pid in prints:
                self.mass[pid] = M.mass_properties(tris)
        for pid, path in prints.items():
            tris = M.read_stl(path)
            t = M.topology(tris)
            if not t["pass"]:
                topo_bad[f"{pid} (print)"] = t
            n = len(M.components(tris))
            if n != int(expect.get(pid, 1)):
                comp_bad[pid] = {"components": n, "expected": int(expect.get(pid, 1))}
            g = M.grounding(tris)
            if g["contactAreaMm2"] < L.MIN_BED_CONTACT_MM2 or g["floatingComponents"]:
                ground_bad[pid] = g
            ratio = g["heightOverShortSide"]
            if (ratio is None or ratio > L.SLENDER_MAX) and pid not in slender_ok:
                slender_bad[pid] = g
        self.put("parts.topology", not topo_bad,
                 f"{len(assembly) + len(prints)} 個の STL を検査" + ("" if not topo_bad else f"、{len(topo_bad)} 個が不合格")
                 + (f"（既製部品の正本 {len(reference_notes)} 個に面積 0 の三角形。閉じているので計器には使える）" if reference_notes else ""),
                 {"failing": topo_bad, "referenceNotes": reference_notes})
        self.put("parts.components", not comp_bad, f"刷る部品 {len(prints)} 点", comp_bad)
        self.put("print.grounding", not ground_bad,
                 f"接地 {L.MIN_BED_CONTACT_MM2}mm² 以上・浮いた成分なし" + ("" if not ground_bad else f"、{len(ground_bad)} 点が不合格"),
                 ground_bad)
        self.put("print.slender", not slender_bad,
                 f"高さ / 接地の短辺 ≤ {L.SLENDER_MAX}" + ("" if not slender_bad else f"、{len(slender_bad)} 点が超過")
                 + (f"（理由つきの例外 {len(slender_ok)} 点）" if slender_ok else ""),
                 {"failing": slender_bad, "declaredExceptions": slender_ok})
        env = self.spec.get("envelope_mm")
        if env:
            lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
            for pid in prints:
                a, b = M.bounds(M.read_stl(assembly[pid]))
                lo, hi = np.minimum(lo, a), np.maximum(hi, b)
            size = (hi - lo).round(3).tolist()
            ok = all(s <= e + 1e-6 for s, e in zip(size, env))
            self.put("assembly.envelope", ok, f"組んだ外形 {size[0]} x {size[1]} x {size[2]}mm（上限 {env}）",
                     {"size": size, "limit": env})

    def motion_frames(self):
        frames = sorted(self.motion["frames"], key=lambda f: f["servo_deg"])
        exclude = {e["part"] for e in self.spec.get("motion", {}).get("exclude", [])}
        rows = [{"deg": f["servo_deg"], "transforms": {p: v for p, v in f["transforms"].items() if p not in exclude}}
                for f in frames]
        gaps = [b["deg"] - a["deg"] for a, b in zip(rows, rows[1:])]
        coarse = max(gaps) if gaps else 0.0
        self.put("motion.resolution", coarse <= L.MOTION_MAX_STEP_DEG + 1e-9,
                 f"motion.json の最大の刻み {coarse:.3f}°（{len(rows)} 姿勢）", {"maxGapDeg": coarse})
        return rows

    def rigid_groups(self, rows):
        parts = sorted(rows[0]["transforms"])
        mats = [{p: C.from_column_major(f["transforms"][p]) for p in parts} for f in rows]
        parent = {p: p for p in parts}

        def find(p):
            while parent[p] != p:
                parent[p] = parent[parent[p]]
                p = parent[p]
            return p

        def near(p, q, margin=0.2):
            # 同じ動きをする離れた部品（隣の画素など）を 1 つの塊にしない。組んだ姿勢の外接箱が触れる組だけつなぐ
            if p not in self.bounds or q not in self.bounds:
                return False
            boxes = []
            for pid in (p, q):
                lo, hi = self.bounds[pid]
                corners = np.array([[x, y, z, 1.0] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
                world = (mats[0][pid] @ corners.T).T[:, :3]
                boxes.append((world.min(axis=0), world.max(axis=0)))
            (la, ha), (lb, hb) = boxes
            return bool(np.all(la <= hb + margin) and np.all(lb <= ha + margin))

        for p in parts:
            for q in parts:
                if q <= p or find(p) == find(q) or not near(p, q):
                    continue
                rel0 = np.linalg.inv(mats[0][p]) @ mats[0][q]
                if all(np.abs(np.linalg.inv(m[p]) @ m[q] - rel0).max() <= 1e-6 for m in mats[1:]):
                    parent[find(q)] = find(p)
        groups = defaultdict(list)
        for p in parts:
            groups[find(p)].append(p)
        moving = {}
        for root, members in groups.items():
            p = members[0]
            if any(np.abs(m[p] - mats[0][p]).max() > 1e-6 for m in mats[1:]):
                moving[root] = members
        return groups, moving, find

    def check_torque(self, rows):
        servo = self.spec.get("motion", {}).get("servo", "sg92r")
        ledger = C.read_json(LEDGER)["parts"].get(servo, {})
        stall = self.spec.get("motion", {}).get("stall_torque_nm") or ledger.get("stall_torque_nm")
        degs = np.array([f["deg"] for f in rows])
        energy = np.zeros(len(rows))
        for pid, (volume, centroid) in self.mass.items():
            if pid not in rows[0]["transforms"]:
                continue
            mass_kg = volume * 1e-3 * L.PRINT_DENSITY_G_CM3 / 1000.0
            c = np.append(centroid, 1.0)
            z = np.array([(C.from_column_major(f["transforms"][pid]) @ c)[2] for f in rows])
            energy += mass_kg * L.GRAVITY * z / 1000.0
        theta = np.radians(degs)
        torque = np.gradient(energy, theta) if len(rows) > 2 else np.zeros(len(rows))
        peak = float(np.abs(torque).max()) if len(torque) else 0.0
        ok = stall is not None and peak <= stall * L.TORQUE_MAX_FRACTION
        at = float(degs[int(np.abs(torque).argmax())]) if len(torque) else None
        self.put("motion.torque", ok,
                 f"重力の必要トルク最大 {peak * 1000:.1f} mN·m（{at}°）/ 停動 {stall} N·m = {peak / stall * 100 if stall else float('nan'):.1f}%"
                 "（摩擦・圧入・ばねは含まない下限の見積もり）",
                 {"peakNm": peak, "atServoDeg": at, "stallNm": stall, "limitFraction": L.TORQUE_MAX_FRACTION,
                  "massesG": {k: round(v[0] * 1e-3 * L.PRINT_DENSITY_G_CM3, 2) for k, v in self.mass.items()}})

    def check_coverage(self, rows):
        groups, moving, find = self.rigid_groups(rows)
        actuator = self.spec.get("motion", {}).get("actuator")
        if actuator not in rows[0]["transforms"]:
            self.put("interface.coverage", False, f"spec.motion.actuator（{actuator}）が motion.json に無い", None)
            return
        start = find(actuator)
        edges = defaultdict(set)
        for i in self.spec.get("interfaces", []):
            if i.get("type") == "drive" and i["driver"] in rows[0]["transforms"] and i["driven"] in rows[0]["transforms"]:
                edges[find(i["driver"])].add(find(i["driven"]))
        reached, stack = {start}, [start]
        while stack:
            g = stack.pop()
            for h in edges[g]:
                if h not in reached:
                    reached.add(h)
                    stack.append(h)
        missing = {root: sorted(members)[:6] for root, members in moving.items() if root not in reached}
        self.put("interface.coverage", not missing,
                 f"動く塊 {len(moving)} 個のうち {len(moving) - len(missing)} 個がアクチュエータから駆動の界面でつながる",
                 {"unreachableGroups": list(missing.values()),
                  "hint": "動く塊ごとに spec.interfaces に type: drive（driver → driven）を書く。界面はゲートが形で確かめる"})

    def check_unknowns(self):
        ledger = C.read_json(LEDGER)["parts"]
        declared = {u["id"]: u for u in self.spec.get("unknowns", [])}
        ids = {p["id"]: p for p in self.manifest["parts"]} if self.manifest else {}
        problems, rows = [], []
        required = []
        for part in self.spec.get("uses", []):
            if part not in ledger:
                problems.append(f"uses の {part} が lib/printmech/parts_ledger.json に無い（台帳に足す）")
                continue
            required += [item for item in ledger[part]["items"] if item["source"] not in TRUSTED_SOURCES]
        for item in required:
            if item["id"] not in declared:
                problems.append(f"{item['id']}（{item['what']}・{item['source']}）の扱いが spec.unknowns に無い")
        for uid, u in declared.items():
            kind = next((k for k in ("trial_part", "not_applicable", "accepted_risk") if u.get(k)), None)
            if kind is None:
                problems.append(f"{uid}: trial_part / not_applicable / accepted_risk のどれかを書く")
            elif kind == "trial_part":
                trial = u["trial_part"]
                in_manifest = trial in ids and ids[trial].get("print")
                if not in_manifest and not (ROOT / trial).is_file():
                    problems.append(f"{uid}: 試し刷りの部品 {trial} が無い（manifest の刷る部品 id か、リポジトリ内の STL のパス）")
                elif not in_manifest:
                    self.track(ROOT / trial)
            rows.append({"id": uid, "kind": kind, "value": u.get(kind), "what": u.get("what")})
        self.put("unknowns.resolved", not problems,
                 f"未確認 {len(rows)} 件の扱いが決まっている" if not problems else f"{len(problems)} 件未解決",
                 {"problems": problems, "resolutions": rows})

    def check_slice(self):
        sys.path.insert(0, str(ROOT / "lib"))
        from printmech.three_mf import inspect_sliced_3mf
        files = self.spec.get("slice", {}).get("files")
        if files is None:
            files = []
            for path in sorted((ROOT / "prints" / self.model).glob("*.3mf")):
                with zipfile.ZipFile(path) as z:
                    if any(n.endswith(".gcode") for n in z.namelist()):
                        files.append(path.relative_to(ROOT).as_posix())
        if not files:
            self.put("print.slice", False, f"prints/{self.model}/ にスライス済みの 3mf が無い", None)
            return
        supports_ok = self.spec.get("slice", {}).get("supports", {})
        bad, rows = {}, {}
        for rel in files:
            self.track(ROOT / rel)
            info = inspect_sliced_3mf(str(ROOT / rel))
            for name, obj in info["objects"].items():
                ext = obj["floating"]["external_unsupported_mm"]
                rows[f"{rel}:{name}"] = ext
                if ext > L.SLICE_MAX_EXTERNAL_UNSUPPORTED_MM and name not in supports_ok:
                    bad[f"{rel}:{name}"] = ext
            if info["support_used"] not in ("false", "0") and not supports_ok:
                bad[rel] = "support_used"
        self.put("print.slice", not bad,
                 f"{len(files)} 枚・{len(rows)} 物体。外の支えなし押し出し ≤ {L.SLICE_MAX_EXTERNAL_UNSUPPORTED_MM}mm"
                 + ("" if not bad else f"、{len(bad)} 件超過"),
                 {"failing": bad, "declaredSupports": supports_ok})

    def run_blender(self, all_rows):
        assembly, prints = self.part_paths()
        job = {
            "parts": {k: str(v) for k, v in assembly.items()},
            "print_parts": {k: str(v) for k, v in prints.items()},
            "allowances": self.spec.get("allowances", []),
            "interfaces": self.spec.get("interfaces", []),
            "jigs": self.spec.get("parts", {}).get("jigs", []),
            "out": str(self.build / "gate_blender.json"),
        }
        if self.motion is not None and self.spec.get("motion"):
            job["motion"] = {"all_frames": all_rows}
            job["static_parts"] = sorted(p for p in all_rows[0]["transforms"]
                                         if all(f["transforms"][p] == all_rows[0]["transforms"][p] for f in all_rows))
        if self.assembly is not None:
            job["assembly"] = {"steps": self.assembly["steps"]}
        job_path = self.build / "gate_job.json"
        C.write_json(job_path, job)
        out_path = Path(job["out"])
        if out_path.exists():
            out_path.unlink()
        log_path = self.build / "gate_blender.log"
        started = time.time()
        with log_path.open("w", encoding="utf-8") as log:
            proc = subprocess.run([BLENDER, "--background", "--factory-startup", "--python-exit-code", "1",
                                   "--python", str(ROOT / "tools" / "mechgate_lib" / "bl_job.py"), "--", str(job_path)],
                                  stdout=log, stderr=subprocess.STDOUT, timeout=4 * 3600)
        self.blender_seconds = round(time.time() - started, 1)
        if not out_path.exists():
            return {"ok": False, "error": f"Blender が結果を書かなかった（exit {proc.returncode}、{log_path.name} を見る）"}
        return C.read_json(out_path)

    def apply_blender(self, result):
        if not result.get("ok"):
            msg = result.get("error", "不明")
            for check in ("instrument.calibration", "parts.self_intersection", "motion.interference",
                          "interface.drive", "interface.retention", "assembly.path"):
                self.put(check, False, f"計器が判定を出せなかった: {msg}", result.get("traceback"))
            return
        cal = result["calibration"]
        self.put("instrument.calibration", cal["pass"],
                 "正負の形がすべて期待どおり" if cal["pass"] else "校正が外れた", cal)
        si = result["selfIntersection"]
        self.put("parts.self_intersection", si["pass"], f"刷る STL {si['checked']} 点", si["failing"])
        if "motion" in result:
            mo = result["motion"]
            self.put("motion.interference", mo["pass"],
                     f"{mo['parts']} 部品・{mo['pairs']} 組 x {mo['frames']} 姿勢（{mo['servoDegs'][0]}〜{mo['servoDegs'][1]}°、"
                     f"どの点も姿勢の間で {L.SWEEP_MAX_DISPLACEMENT_MM}mm 以内。補間 {mo.get('interpolatedPoses', 0)}）"
                     + ("" if mo["pass"] else f"、許可外の当たり {len(mo['violations'])} 組"),
                     {"violations": mo["violations"][:30], "allowedContacts": mo["allowedContacts"]})
            drive = result.get("drive", [])
            failing = [d for d in drive if not d["pass"]]
            self.put("interface.drive", bool(drive) and not failing,
                     f"界面 {len(drive)} 個" + ("" if not failing else f"、{len(failing)} 個が遊びの中で当たらない")
                     if drive else "駆動の界面が spec に無い", {"failing": failing, "all": drive})
        ret = result.get("retention", [])
        failing = [r for r in ret if not r["pass"]]
        if ret or "interface.retention" in self.required():
            self.put("interface.retention", bool(ret) and not failing,
                     f"抜け止め {len(ret)} 個" + ("" if not failing else f"、{len(failing)} 個が止まらない"),
                     {"failing": failing, "all": ret})
        if "assembly" in result:
            asm = result["assembly"]
            self.put("assembly.path", asm["pass"],
                     f"{len(asm['steps'])} 工程（補間で足した姿勢 {asm['interpolatedPoses']}）" + ("" if asm["pass"] else
                                                   f"、許可外の当たり {len(asm['violations'])} 件・工程の継ぎ目のずれ {len(asm['boundaryErrors'])}・"
                                                   f"組まれていない部品 {len(asm['finalNotAssembled'])}"),
                     {k: asm[k] for k in ("violations", "boundaryErrors", "interpolatedPoses",
                                          "finalNotAssembled", "allowedContacts", "steps")})

    def required(self):
        spec = self.spec
        req = {"harness.calibrated", "spec.valid", "contract.files", "parts.topology", "parts.components",
               "parts.self_intersection", "print.grounding", "print.slender", "unknowns.resolved", "print.slice",
               "instrument.calibration"}
        if spec.get("envelope_mm"):
            req.add("assembly.envelope")
        if spec.get("motion"):
            req |= {"motion.resolution", "motion.interference", "motion.torque", "interface.coverage", "interface.drive"}
        if not spec.get("single_part"):
            req.add("assembly.path")
        if any(i.get("type") == "retention" for i in spec.get("interfaces", [])):
            req.add("interface.retention")
        for r in spec.get("requirements", []):
            req |= {c for c in r.get("checks", []) if c in CHECKS}
        return req

    # --- 実行 ------------------------------------------------------------------------------
    def run(self):
        self.load()
        self.check_harness()
        self.check_spec()
        if self.manifest is not None and self.check_contract():
            self.check_meshes()
            all_rows = None
            if self.motion is not None and self.spec.get("motion"):
                all_rows = self.motion_frames()
                self.check_torque(all_rows)
                self.check_coverage(all_rows)
            self.check_unknowns()
            self.check_slice()
            if not self.skip_blender:
                self.apply_blender(self.run_blender(all_rows))
        else:
            self.check_contract() if self.manifest is None else None
        return self.report()

    def report(self):
        required = self.required()
        waived = {w["check"]: w["reason"] for w in self.spec.get("waivers", []) if w.get("check") not in NON_WAIVABLE}
        checks = []
        for cid in CHECKS:
            row = self.rows.get(cid)
            if row is None:
                if cid in required:
                    row = {"id": cid, "title": CHECKS[cid], "pass": False,
                           "summary": "未実行（前の段で止まったか --no-blender）", "detail": None}
                else:
                    continue
            row = dict(row)
            row["required"] = cid in required
            row["waived"] = waived.get(cid)
            checks.append(row)
        blocking = [c["id"] for c in checks if c["required"] and not c["pass"] and not c["waived"]]
        reqs = []
        by_id = {c["id"]: c for c in checks}
        for r in self.spec.get("requirements", []):
            auto = [c for c in r.get("checks", []) if c in CHECKS]
            manual = [c[len("manual:"):] for c in r.get("checks", []) if c.startswith("manual:")]
            ok = all(by_id.get(c, {}).get("pass") or by_id.get(c, {}).get("waived") for c in auto)
            reqs.append({"id": r["id"], "text": r["text"], "checks": auto, "manual": manual,
                         "pass": ok if auto else None})
        self.track_harness()
        doc = {
            "model": self.model,
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "pass": not blocking,
            "blocking": blocking,
            "harness": getattr(self, "harness", None),
            "blenderSeconds": getattr(self, "blender_seconds", None),
            "declared": {
                "waivers": waived,
                "allowances": self.spec.get("allowances", []),
                "unknowns": self.spec.get("unknowns", []),
                "slenderExceptions": self.spec.get("parts", {}).get("slender_ok", {}),
                "motionExcluded": self.spec.get("motion", {}).get("exclude", []),
            },
            "requirements": reqs,
            "checks": checks,
            "inputs": self.inputs,
        }
        C.write_json(self.build / "gate_report.json", doc)
        (self.build / "gate_summary.md").write_text(summary_markdown(doc), encoding="utf-8", newline="\n")
        return doc

    def track_harness(self):
        for rel in HARNESS_FILES:
            self.track(ROOT / rel)


def summary_markdown(doc):
    lines = [f"# ゲート: {doc['model']}", "",
             f"- 判定: **{'合格' if doc['pass'] else '不合格'}**（{doc['generatedAt']}）",
             f"- 止めている検査: {', '.join(doc['blocking']) or 'なし'}", ""]
    lines += ["## 要件", "", "| 要件 | 内容 | 検査 | 結果 | 実物で確かめること |", "|---|---|---|---|---|"]
    for r in doc["requirements"]:
        res = "—" if r["pass"] is None else ("○" if r["pass"] else "×")
        lines.append(f"| {r['id']} | {r['text']} | {', '.join(r['checks'])} | {res} | {'; '.join(r['manual'])} |")
    lines += ["", "## 検査", "", "| 検査 | 結果 | 内容 |", "|---|---|---|"]
    for c in doc["checks"]:
        res = "外した: " + c["waived"] if c["waived"] else ("○" if c["pass"] else "×")
        lines.append(f"| {c['id']} | {res} | {c['summary']} |")
    d = doc["declared"]
    lines += ["", "## モデル側が宣言したもの（合格の理由ではない。読む人が確かめる）", ""]
    for w, reason in d["waivers"].items():
        lines.append(f"- 外した検査 {w}: {reason}")
    for a in d["allowances"]:
        extra = {k: v for k, v in a.items() if k not in ("type", "pairs", "basis")}
        lines.append(f"- 許可 {a['type']} {len(a.get('pairs', []))} 組 {extra}: {a.get('basis', '')}")
    for u in d["unknowns"]:
        kind = next((k for k in ("trial_part", "not_applicable", "accepted_risk") if u.get(k)), "?")
        lines.append(f"- 未確認 {u['id']}: {kind} = {u.get(kind)}")
    for p, reason in d["slenderExceptions"].items():
        lines.append(f"- 細長の例外 {p}: {reason}")
    for e in d["motionExcluded"]:
        lines.append(f"- 動作の検査から除いた部品 {e.get('part')}: {e.get('reason')}")
    return "\n".join(lines) + "\n"


def freshness(model):
    """gate_report.json の入力 SHA が今のファイルと一致するか。Blender は使わない（hook 用に速い）"""
    path = ROOT / "models" / model / "build" / "gate_report.json"
    if not path.exists():
        return "missing", []
    doc = C.read_json(path)
    changed = []
    for rel, digest in doc.get("inputs", {}).items():
        p = ROOT / rel
        if not p.exists() or sha256(p) != digest:
            changed.append(rel)
    spec = ROOT / "models" / model / "spec.json"
    rel = spec.relative_to(ROOT).as_posix()
    if rel not in doc.get("inputs", {}):
        changed.append(rel)
    if changed:
        return "stale", changed
    return ("pass" if doc.get("pass") else "fail"), doc.get("blocking", [])
