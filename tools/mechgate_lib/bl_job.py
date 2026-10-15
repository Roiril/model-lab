"""ゲートの Blender 側。tools/mechgate.py が job.json を作って呼ぶ（直接は呼ばない）。

blender --background --python-exit-code 1 --python tools/mechgate_lib/bl_job.py -- <job.json>

測るもの（すべて lib/printmech/solid_meter.py の MANIFOLD 共通体積。先に校正する）:
- selfIntersection : 刷る STL の自己交差
- motion           : motion.json の全姿勢（2.5° 刻み以下）・全部品の組の共通体積
- assembly         : assembly.json の各工程の経路。当たってよいのは spec の許可だけで、上限はハーネスの定数
- drive            : 駆動の界面。従動側を動きの前後へ押したとき、遊びの中で駆動側に当たるか
- retention        : 抜け止め。外れる向きに動かしたとき、上限までに止まるか
"""
from __future__ import annotations

import itertools
import json
import math
import sys
import time
import traceback
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
sys.path.insert(0, str(ROOT / "lib" / "printmech"))
sys.path.insert(0, str(ROOT / "tools"))

import solid_meter as SM  # noqa: E402
import contract as C  # noqa: E402
from mechgate_lib import limits as L  # noqa: E402

FLOOR = L.VOLUME_FLOOR_MM3


def log(*args):
    print("[mechgate]", *args, flush=True)


def load_solids(paths):
    return {pid: SM.Solid.load(pid, path) for pid, path in paths.items()}


def pair_key(a, b):
    return tuple(sorted((a, b)))


def allowance_index(allowances, kinds):
    index = {}
    for item in allowances:
        if item["type"] not in kinds:
            continue
        for a, b in item["pairs"]:
            index.setdefault(pair_key(a, b), []).append(item)
    return index


class PoseCache:
    def __init__(self, solids, matrices):
        self.solids, self.matrices = solids, matrices
        self.verts, self.bvh = {}, {}

    def v(self, pid):
        if pid not in self.verts:
            self.verts[pid] = self.solids[pid].posed(self.matrices[pid])
        return self.verts[pid]

    def b(self, pid):
        if pid not in self.bvh:
            self.bvh[pid] = SM.Meter.bvh_of(self.v(pid), self.solids[pid].faces)
        return self.bvh[pid]

    def bounds(self, pid):
        return self.solids[pid].posed_bounds(self.matrices[pid])


def aabb_apart(ba, bb):
    return bool(np.any(ba[1] < bb[0]) or np.any(bb[1] < ba[0]))


def measure(meter, cache, a, b):
    sa, sb = cache.solids[a], cache.solids[b]
    return meter.common_posed(sa, cache.v(a), cache.b(a), sb, cache.v(b), cache.b(b))[0]


# --- 姿勢の密度 ------------------------------------------------------------------------------
def corners(solid):
    lo, hi = solid.lo, solid.hi
    return np.array([[x, y, z, 1.0] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])


def displacement(m0, m1, cs):
    """部品の外接箱の角が 2 姿勢の間で動く距離の最大（mm）"""
    return float(np.linalg.norm(((m1 - m0) @ cs.T)[:3], axis=0).max())


def interpolate(m0, m1, fraction):
    s = C.screw(m1 @ np.linalg.inv(m0))
    amount = s["angle_deg"] if s["angle_deg"] > 0 else s["slide_mm"]
    return C.screw_motion(s)(fraction * amount) @ m0


def densify(frames, solids, key):
    """frames: [{key: 値, "matrices": {...}}]。隣どうしの間でどの点も SWEEP_MAX_DISPLACEMENT_MM を超えて
    動かないよう、剛体補間の姿勢を足す。戻りは (新しい列, 足した数)"""
    cs = {}
    out, added = [frames[0]], 0
    for f0, f1 in zip(frames, frames[1:]):
        worst = 0.0
        for p, m1 in f1["matrices"].items():
            m0 = f0["matrices"].get(p)
            if m0 is None or p not in solids:
                continue
            if p not in cs:
                cs[p] = corners(solids[p])
            worst = max(worst, displacement(m0, m1, cs[p]))
        n = int(np.ceil(worst / L.SWEEP_MAX_DISPLACEMENT_MM - 1e-9))
        for i in range(1, n):
            t = i / n
            mats = {p: (interpolate(f0["matrices"][p], m1, t) if p in f0["matrices"] else m1)
                    for p, m1 in f1["matrices"].items()}
            out.append({key: f0[key] + (f1[key] - f0[key]) * t, "matrices": mats, "interpolated": True})
            added += 1
        out.append(f1)
    return out, added


def thin(frames, solids, max_deg):
    """動作の姿勢を間引く。角度の差が max_deg 以下で、どの点も 1mm 以内しか動かない範囲は 1 つにまとめる。
    残した姿勢の間がまだ粗ければ densify で補間する"""
    cs = {p: corners(solids[p]) for p in frames[0]["matrices"] if p in solids}

    def far(a, b):
        if b["deg"] - a["deg"] > max_deg + 1e-9:
            return True
        return any(displacement(a["matrices"][p], b["matrices"][p], cs[p]) > L.SWEEP_MAX_DISPLACEMENT_MM
                   for p in cs)

    kept = [frames[0]]
    for i in range(1, len(frames)):
        if far(kept[-1], frames[i]) and frames[i - 1] is not kept[-1]:
            kept.append(frames[i - 1])
    if frames[-1] is not kept[-1]:
        kept.append(frames[-1])
    return densify(kept, solids, "deg")


# --- 動作の当たり ----------------------------------------------------------------------------
def motion_sweep(meter, solids, frames, allowances):
    parts = sorted(set(frames[0]["matrices"]) & set(solids))
    static_fit = allowance_index(allowances, {"static_fit"})
    reference = allowance_index(allowances, {"reference_internal"})
    constant, varying = [], []
    for a, b in itertools.combinations(parts, 2):
        rel0 = np.linalg.inv(frames[0]["matrices"][a]) @ frames[0]["matrices"][b]
        same = all(np.abs(np.linalg.inv(f["matrices"][a]) @ f["matrices"][b] - rel0).max() <= 1e-6
                   for f in frames[1:])
        (constant if same else varying).append((a, b))
    violations, allowed_rows = [], {}
    worst = {}

    def judge(a, b, volume, deg):
        key = pair_key(a, b)
        worst[key] = max(worst.get(key, 0.0), volume)
        if volume <= FLOOR:
            return
        for item in reference.get(key, []):
            if volume <= min(item["max_mm3"], L.REFERENCE_INTERNAL_MAX_MM3):
                allowed_rows.setdefault(key, {"type": "reference_internal", "maxMm3": 0.0})
                allowed_rows[key]["maxMm3"] = max(allowed_rows[key]["maxMm3"], volume)
                return
        if (a, b) in constant_set:
            for item in static_fit.get(key, []):
                if volume <= min(item["max_mm3"], L.STATIC_FIT_MAX_MM3):
                    allowed_rows.setdefault(key, {"type": "static_fit", "maxMm3": 0.0})
                    allowed_rows[key]["maxMm3"] = max(allowed_rows[key]["maxMm3"], volume)
                    return
        violations.append({"parts": list(key), "servoDeg": deg, "commonMm3": round(volume, 6)})

    constant_set = set(constant)
    first = PoseCache(solids, frames[0]["matrices"])
    for a, b in constant:
        if aabb_apart(first.bounds(a), first.bounds(b)):
            continue
        judge(a, b, measure(meter, first, a, b), frames[0]["deg"])
    log(f"motion: constant pairs {len(constant)} done; varying {len(varying)} x {len(frames)} frames")
    for frame in frames:
        cache = PoseCache(solids, frame["matrices"])
        for a, b in varying:
            if aabb_apart(cache.bounds(a), cache.bounds(b)):
                continue
            judge(a, b, measure(meter, cache, a, b), frame["deg"])
    by_pair = {}
    for row in violations:
        key = tuple(row["parts"])
        entry = by_pair.setdefault(key, {"parts": row["parts"], "frames": 0, "maxCommonMm3": 0.0,
                                         "servoDegRange": [row["servoDeg"], row["servoDeg"]]})
        entry["frames"] += 1
        entry["maxCommonMm3"] = max(entry["maxCommonMm3"], row["commonMm3"])
        entry["servoDegRange"][1] = row["servoDeg"]
    return {
        "pass": not violations,
        "parts": len(parts), "pairs": len(constant) + len(varying),
        "constantPairs": len(constant), "varyingPairs": len(varying),
        "frames": len(frames), "servoDegs": [frames[0]["deg"], frames[-1]["deg"]],
        "violations": sorted(by_pair.values(), key=lambda r: -r["maxCommonMm3"]),
        "allowedContacts": [{"parts": list(k), **v} for k, v in sorted(allowed_rows.items())],
    }


# --- 組立の経路 ------------------------------------------------------------------------------
def remaining_relative_travel(step_matrices, a, b, radius):
    """各フレームから工程の終わりまで、a に対する b の相対移動の道のり（mm）"""
    rel = [np.linalg.inv(m[a]) @ m[b] for m in step_matrices]
    seg = [C.relative_change(rel[i], rel[i + 1], radius) for i in range(len(rel) - 1)]
    remaining = [0.0] * len(rel)
    for i in range(len(rel) - 2, -1, -1):
        remaining[i] = remaining[i + 1] + seg[i]
    return remaining


def assembly_path(meter, solids, steps, allowances, jigs):
    path_allow = allowance_index(allowances, {"press_fit", "snap"})
    static_fit = allowance_index(allowances, {"static_fit"})
    reference = allowance_index(allowances, {"reference_internal"})
    boundary_errors, violations, step_rows = [], [], []
    interpolated = 0
    used = {}
    previous_end = None
    for step in steps:
        raw = [{"progress": f["progress"], "matrices": {p: C.from_column_major(v) for p, v in f["transforms"].items()}}
               for f in step["frames"]]
        dense, added = densify(raw, solids, "progress")
        interpolated += added
        mats = [f["matrices"] for f in dense]
        progress = [f["progress"] for f in dense]
        moving = set(step["moving"])
        missing = [p for m in mats for p in m if p not in solids]
        if missing:
            raise ValueError(f"工程 {step['id']} に STL の無い部品: {sorted(set(missing))[:5]}")
        if previous_end is not None:
            for p in set(previous_end) & set(mats[0]):
                if np.abs(previous_end[p] - mats[0][p]).max() > 1e-5:
                    boundary_errors.append({"step": step["id"], "part": p})
        final_rel = {}
        remaining_cache = {}
        relative_cache = {}
        step_violations = 0
        for k, matrices in enumerate(mats):
            cache = PoseCache(solids, matrices)
            for a, b in itertools.combinations(sorted(matrices), 2):
                if a not in moving and b not in moving:
                    continue
                if aabb_apart(cache.bounds(a), cache.bounds(b)):
                    continue
                key = pair_key(a, b)
                rel = np.linalg.inv(matrices[key[0]]) @ matrices[key[1]]
                rkey = (key, tuple(np.round(rel, 6).reshape(-1)))
                volume = relative_cache.get(rkey)
                if volume is None:
                    volume = measure(meter, cache, key[0], key[1])
                    relative_cache[rkey] = volume
                if volume <= FLOOR:
                    continue
                verdict = None
                for item in reference.get(key, []):
                    if volume <= min(item["max_mm3"], L.REFERENCE_INTERNAL_MAX_MM3):
                        verdict = ("reference_internal", None)
                if verdict is None:
                    if key not in final_rel:
                        final_rel[key] = np.linalg.inv(mats[-1][key[0]]) @ mats[-1][key[1]]
                    seated = np.abs(rel - final_rel[key]).max() <= 1e-5
                    for item in static_fit.get(key, []):
                        if seated and volume <= min(item["max_mm3"], L.STATIC_FIT_MAX_MM3):
                            verdict = ("static_fit", None)
                if verdict is None:
                    for item in path_allow.get(key, []):
                        if item.get("step") not in (None, step["id"]):
                            continue
                        if key not in remaining_cache:
                            radius = min(solids[key[0]].radius, solids[key[1]].radius)
                            remaining_cache[key] = remaining_relative_travel(mats, key[0], key[1], radius)
                        remaining = remaining_cache[key][k]
                        if item["type"] == "press_fit":
                            limit = min(item["insertion_mm"], L.PRESS_FIT_MAX_INSERTION_MM)
                            if remaining <= limit + 0.05:
                                verdict = ("press_fit", remaining)
                        else:
                            limit = min(item["engage_mm"], L.SNAP_MAX_ENGAGE_MM)
                            strain_ok = item["strain_percent"] <= L.SNAP_MAX_STRAIN_PERCENT
                            final = k == len(mats) - 1
                            if strain_ok and not final and remaining <= limit + 0.05:
                                verdict = ("snap", remaining)
                        if verdict:
                            break
                if verdict:
                    row = used.setdefault((key, verdict[0]), {"parts": list(key), "type": verdict[0],
                                                              "maxCommonMm3": 0.0, "maxRemainingTravelMm": 0.0,
                                                              "samples": 0, "steps": set()})
                    row["samples"] += 1
                    row["steps"].add(step["id"])
                    row["maxCommonMm3"] = max(row["maxCommonMm3"], volume)
                    if verdict[1] is not None:
                        row["maxRemainingTravelMm"] = max(row["maxRemainingTravelMm"], verdict[1])
                    continue
                step_violations += 1
                remaining = None
                if key in remaining_cache:
                    remaining = round(remaining_cache[key][k], 3)
                violations.append({"step": step["id"], "progress": round(progress[k], 6),
                                   "parts": list(key), "commonMm3": round(volume, 6),
                                   "remainingRelativeTravelMm": remaining,
                                   "declared": [i["type"] for i in path_allow.get(key, []) + static_fit.get(key, [])]})
        step_rows.append({"id": step["id"], "frames": len(raw), "checkedPoses": len(mats), "moving": len(moving),
                          "violations": step_violations, "pass": step_violations == 0})
        previous_end = mats[-1]
    final = previous_end or {}
    not_identity = [p for p, m in final.items() if p not in jigs and np.abs(m - np.eye(4)).max() > 1e-5]
    not_identity += sorted(p for p in solids if p not in final and p not in jigs)   # どの工程にも出てこない部品
    for row in used.values():
        row["steps"] = sorted(row["steps"])
        row["maxCommonMm3"] = round(row["maxCommonMm3"], 6)
        row["maxRemainingTravelMm"] = round(row["maxRemainingTravelMm"], 3)
    grouped = {}
    for v in violations:
        k = (v["step"], tuple(v["parts"]))
        g = grouped.setdefault(k, {**v, "frames": 0})
        g["frames"] += 1
        g["commonMm3"] = max(g["commonMm3"], v["commonMm3"])
    return {
        "pass": not violations and not boundary_errors and not not_identity,
        "steps": step_rows,
        "violations": list(grouped.values()),
        "interpolatedPoses": interpolated,
        "boundaryErrors": boundary_errors[:20],
        "finalNotAssembled": not_identity,
        "finalParts": sorted(final),
        "allowedContacts": sorted(used.values(), key=lambda r: r["parts"]),
    }


# --- 駆動と抜け止め ----------------------------------------------------------------------------
def drive_check(meter, solids, motion_frames, item):
    driver, driven = item["driver"], item["driven"]
    sides = item.get("sides", "both")
    moves = []
    for f0, f1 in zip(motion_frames, motion_frames[1:]):
        d = f1["matrices"][driven] @ np.linalg.inv(f0["matrices"][driven])
        s = C.screw(d)
        if s["angle_deg"] < 1e-6 and abs(s["slide_mm"]) < 1e-6:
            continue
        moves.append((f0, s))
    if not moves:
        return {"id": item["id"], "pass": False, "reason": "従動側が motion の中で一度も動かない", "samples": 0}
    picks = [moves[round(i * (len(moves) - 1) / max(1, L.DRIVE_SAMPLES - 1))]
             for i in range(min(L.DRIVE_SAMPLES, len(moves)))]
    rows = []
    for f0, s in picks:
        rotational = s["angle_deg"] > 1e-6
        cap = L.DRIVE_MAX_PLAY_DEG if rotational else L.DRIVE_MAX_PLAY_MM
        limit = min(item.get("max_play_deg" if rotational else "max_play_mm", cap), cap)
        fixed = {driver: (solids[driver], f0["matrices"][driver])}
        base = f0["matrices"][driven]
        result = {}
        for label, sign in (("back", -1.0), ("ahead", 1.0)):
            step = C.screw_motion(s, sign)
            probe = SM.first_contact(meter, solids[driven], lambda t, step=step: step(t) @ base, fixed,
                                     maximum=limit * 1.5, coarse=limit / 10.0)
            result[label] = probe["travel"]
        within = {k: v is not None and v <= limit for k, v in result.items()}
        ok = (within["back"] and within["ahead"]) if sides == "both" else (within["back"] or within["ahead"])
        rows.append({"servoDeg": f0["deg"], "unit": "deg" if rotational else "mm", "limit": limit,
                     "back": result["back"], "ahead": result["ahead"], "pass": ok})
    return {"id": item["id"], "driver": driver, "driven": driven, "sides": sides,
            "samples": len(rows), "pass": all(r["pass"] for r in rows),
            "worst": [r for r in rows if not r["pass"]][:5] or rows[:2]}


def retention_check(meter, solids, item, assembled, static_parts):
    """item["parts"]（または part）を一緒に動かす。相手は against か、それ以外の組んだ全部品"""
    group = item.get("parts") or [item["part"]]
    direction = np.asarray(item["direction"], dtype=float)
    direction /= np.linalg.norm(direction)
    # 相手の既定は「動作中に動かない部品」。重力で載っているだけの部品（画素など）を止め役に数えない
    others = item.get("against") or [p for p in static_parts if p in assembled and p not in group]
    fixed = {p: (solids[p], assembled[p]) for p in others if p in solids}
    limit = min(item["max_free_mm"], L.RETENTION_MAX_FREE_MM)
    if item.get("engage_depth_mm") is not None:
        limit = min(limit, item["engage_depth_mm"])
    best = None
    for part in group:
        base = assembled[part]
        probe = SM.first_contact(meter, solids[part], lambda t, base=base: C.translation(*(direction * t)) @ base,
                                 fixed, maximum=max(limit * 2.0, 1.0), coarse=min(0.25, limit / 4.0))
        if probe["travel"] is not None and (best is None or probe["travel"] < best["travel"]):
            best = {**probe, "movingPart": part}
    travel = best["travel"] if best else None
    return {"id": item["id"], "parts": group, "direction": direction.round(4).tolist(), "limitMm": limit,
            "travelMm": travel, "stoppedBy": best["parts"] if best else [],
            "stoppedPart": best["movingPart"] if best else None, "pass": travel is not None and travel <= limit}


# --- 本体 -----------------------------------------------------------------------------------
def main():
    job_path = Path(sys.argv[sys.argv.index("--") + 1])
    job = json.loads(job_path.read_text(encoding="utf-8"))
    out = {"startedAt": time.strftime("%Y-%m-%dT%H:%M:%S")}
    meter = SM.Meter()
    try:
        out["calibration"] = SM.calibrate(meter)
        log("calibration", out["calibration"]["pass"])
        if not out["calibration"]["pass"]:
            raise RuntimeError("計器の校正が外れた。判定を出さない")
        solids = load_solids(job["parts"])
        prints = load_solids(job.get("print_parts", {}))
        rows = {}
        for pid, solid in prints.items():
            count, sample = SM.self_intersections(solid)
            rows[pid] = {"pairs": count, "sample": sample}
        out["selfIntersection"] = {"pass": all(r["pairs"] == 0 for r in rows.values()),
                                   "failing": {k: v for k, v in rows.items() if v["pairs"]}, "checked": len(rows)}
        log("self intersection", out["selfIntersection"]["pass"])
        motion = job.get("motion")
        if motion:
            full = [{"deg": f["deg"], "matrices": {p: C.from_column_major(v) for p, v in f["transforms"].items()
                                                   if p in solids}} for f in motion["all_frames"]]
            frames, added = thin(full, solids, L.MOTION_MAX_STEP_DEG)
            out["motion"] = motion_sweep(meter, solids, frames, job["allowances"])
            out["motion"]["interpolatedPoses"] = added
            log("motion", out["motion"]["pass"], len(frames), "poses")
            out["drive"] = [drive_check(meter, solids, full, item) for item in job["interfaces"]
                            if item["type"] == "drive"]
            log("drive", all(r["pass"] for r in out["drive"]))
        if job.get("assembly"):
            out["assembly"] = assembly_path(meter, solids, job["assembly"]["steps"], job["allowances"],
                                            set(job.get("jigs", [])))
            log("assembly", out["assembly"]["pass"])
        assembled = {p: np.eye(4) for p in solids if p not in set(job.get("jigs", []))}
        static_parts = job.get("static_parts") or list(assembled)
        out["retention"] = [retention_check(meter, solids, item, assembled, static_parts) for item in job["interfaces"]
                            if item["type"] == "retention"]
        out["meterStats"] = meter.stats
        out["ok"] = True
    except Exception as error:  # 計器の失敗は判定の失敗として記録する
        out["ok"] = False
        out["error"] = f"{type(error).__name__}: {error}"
        out["traceback"] = traceback.format_exc()
        log("ERROR", out["error"])
    finally:
        meter.dispose()
    C.write_json(job["out"], out)


main()
