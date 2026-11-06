"""ゲートの結果から Studio の物理検証・組み立てタブの入力を作る。

    ./run.sh models/phone-slab-walker/model.py
    py -3.11 tools/mechgate.py check phone-slab-walker
    py -3.11 models/phone-slab-walker/lattice_export.py     # assembly.json の校正欄を埋める
    py -3.11 tools/mechgate.py check phone-slab-walker      # 埋めたあとの形で測り直す
    py -3.11 models/phone-slab-walker/lattice_export.py     # 表示データを書き出す

物理検証は「脚を床から浮かせて 1 軸で振る」計算。歩行そのものは sim_gait.py が別に見る。
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "lib")]
sys.stdout.reconfigure(encoding="utf-8")

import lattice_simulation as physics  # noqa: E402
import lattice_web  # noqa: E402
from mechgate_lib import limits  # noqa: E402
from mechgate_lib.gate import freshness  # noqa: E402

MODEL = "phone-slab-walker"
BUILD = HERE / "build"
GEOMETRY_CHECKS = ("instrument.calibration", "parts.topology", "motion.interference", "motion.torque",
                   "interface.coverage", "interface.drive", "interface.retention", "assembly.path")
DURATION_S = 2.0
# STS3215 の値。sim_gait.py と同じ出どころ（FEETECH C047 データシートと mycobot-lab の同定）
NO_LOAD_RAD_S = 45 * 2 * math.pi / 60
CONTROL_BAND_RAD = math.radians(22.0)
ARMATURE_KGM2 = 0.028
FRICTION_NM = 0.052
REACH_TOLERANCE_DEG = 3.0   # サーボは比例制御なので、脚の重さのぶん手前で釣り合う


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, document):
    """同じ中身なら書かない。ゲートの入力の時刻とハッシュを無駄に動かさない"""
    text = json.dumps(document, ensure_ascii=False, indent=1, allow_nan=False) + "\n"
    if Path(path).exists() and Path(path).read_text(encoding="utf-8") == text:
        return False
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(path)
    return True


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gate_checks():
    report = read(BUILD / "gate_report.json")
    return {row["id"]: row for row in report.get("checks", [])}


def rigid_properties(matrices, q, mass):
    """一般化慣性と重力トルク。行列は mm の剛体変換、微分は rad"""
    rotation = matrices[:, :3, :3]
    centers = np.einsum("nij,j->ni", rotation, mass["comM"]) + matrices[:, :3, 3] / 1000
    velocity = np.gradient(centers, q, axis=0, edge_order=2)
    acceleration = np.gradient(velocity, q, axis=0, edge_order=2)
    rdot = np.gradient(rotation, q, axis=0, edge_order=2)
    skew = np.einsum("nij,nkj->nik", rdot, rotation)
    omega = np.column_stack(((skew[:, 2, 1] - skew[:, 1, 2]) / 2,
                             (skew[:, 0, 2] - skew[:, 2, 0]) / 2,
                             (skew[:, 1, 0] - skew[:, 0, 1]) / 2))
    xx, yy, zz, xy, xz, yz = mass["inertiaComKgm2"]
    tensor = np.array([[xx, xy, xz], [xy, yy, yz], [xz, yz, zz]])
    world = np.einsum("nij,jk,nlk->nil", rotation, tensor, rotation)
    inertia = mass["massKg"] * np.einsum("ni,ni->n", velocity, velocity)
    inertia += np.einsum("ni,nij,nj->n", omega, world, omega)
    return dict(inertia=inertia, gravity=mass["massKg"] * limits.GRAVITY * velocity[:, 2],
                z=centers[:, 2], dz=velocity[:, 2], ddz=acceleration[:, 2])


def build_tables():
    manifest = read(BUILD / "manifest.json")
    motion = read(BUILD / "motion.json")
    frames = motion["frames"]
    angles = np.array([frame["servo_deg"] for frame in frames], dtype=float)
    q = np.radians(angles)
    groups, values = [], []
    hashes = {}
    for name in ("manifest.json", "motion.json"):
        hashes[f"models/{MODEL}/build/{name}"] = digest(BUILD / name)
    for part in manifest["parts"]:
        pid = part["id"]
        matrices = np.array([np.array(frame["transforms"][pid]).reshape(4, 4, order="F") for frame in frames])
        if np.allclose(matrices, matrices[0], atol=1e-9, rtol=0):
            continue
        source = HERE / part["assembly"]
        triangles = physics.read_stl(source)
        mass = physics.signed_tetra_properties(triangles, limits.PRINT_DENSITY_G_CM3 * 1000)
        if mass["signedVolumeMm3"] <= 0 or any(physics.edge_diagnostics(triangles)):
            raise ValueError(f"{pid}: 閉じた STL でないと質量を出せない")
        hashes[f"models/{MODEL}/{part['assembly']}"] = digest(source)
        groups.append(dict(id=pid, label=part.get("label", pid), massKg=mass["massKg"]))
        values.append(rigid_properties(matrices, q, mass))
    inertia = sum(v["inertia"] for v in values)
    gravity = sum(v["gravity"] for v in values)
    dinertia = np.gradient(inertia, q, edge_order=2)
    ledger = read(ROOT / "lib" / "printmech" / "parts_ledger.json")
    stall = ledger["parts"][read(HERE / "spec.json")["motion"]["servo"]]["stall_torque_nm"]
    rows = [dict(servoDeg=float(angle), inertiaRestKgm2=0.0, inertiaGroupsKgm2=float(inertia[n]),
                 dMGroupsDqKgm2PerRad=float(dinertia[n]), gravityRestNm=0.0, gravityGroupsNm=float(gravity[n]),
                 contactFrictionGroupsNm=0.0,
                 liftsMm=[float(v["z"][n] * 1000) for v in values],
                 dLiftDqMPerRad=[float(v["dz"][n]) for v in values],
                 d2LiftDq2MPerRad2=[float(v["ddz"][n]) for v in values]) for n, angle in enumerate(angles)]
    tables = dict(model=MODEL, limitsDeg=angles[[0, -1]].tolist(), duration_s=DURATION_S, groups=groups, rows=rows,
                  contactModel="gravity_one_sided", contactBoundariesDeg=[],
                  const=dict(stallTorqueNm=2 * stall, noLoadSpeedRadS=NO_LOAD_RAD_S,
                             controlBandRad=CONTROL_BAND_RAD, motorInertiaKgm2=ARMATURE_KGM2,
                             servoFrictionNm=FRICTION_NM, gravityMS2=limits.GRAVITY,
                             dtS=physics.DT, recordS=physics.RECORD, settleS=physics.SETTLE,
                             contactToleranceN=1e-8))
    return tables, hashes


def calculate(tables):
    """2 秒の quintic で振ったときの必要トルク。左右の脚を足した負荷を、サーボ 2 個で受ける"""
    sim = physics.TableSim(tables)
    low, high = tables["limitsDeg"]
    peaks, runs = [], []
    for start, target in ((low, high), (high, low)):
        peak = 0.0
        for u in np.linspace(0, 1, 2001):
            angle = start + (target - start) * (10 * u**3 - 15 * u**4 + 6 * u**5)
            speed = math.radians(target - start) * (30 * u**2 - 60 * u**3 + 30 * u**4) / DURATION_S
            accel = math.radians(target - start) * (60 * u - 180 * u**2 + 120 * u**3) / DURATION_S**2
            state = sim.at(angle)
            torque = state["inertiaGroupsKgm2"] * accel + 0.5 * state["dMGroupsDqKgm2PerRad"] * speed**2 + state["gravityGroupsNm"]
            peak = max(peak, abs(torque))
        result = sim.run(from_deg=start, to_deg=target)
        runs.append(dict(fromDeg=start, toDeg=target, final=result["final"], trace=result["trace"],
                         peakMotorTorqueNm=result["peakTorqueNm"],
                         reached=abs(result["final"]["servoDeg"] - target) < REACH_TOLERANCE_DEG,
                         contactAssessment="not_applicable_to_direct_drive"))
        peaks.append(peak)
    peak = float(max(peaks))
    stall = tables["const"]["stallTorqueNm"]
    limit = stall * limits.TORQUE_MAX_FRACTION
    return dict(pass_=peak <= limit and all(run["reached"] for run in runs), peakIdealTorqueNm=peak, limitNm=limit,
                stallFraction=peak / stall, movingMassKg=sum(g["massKg"] for g in tables["groups"]),
                limitsDeg=[low, high], runs=runs)


def main():
    status, changed = freshness(MODEL)
    checks = gate_checks()
    measured = status in ("pass", "fail")
    geometry = status == "pass" and all(checks.get(key, {}).get("pass") is True for key in GEOMETRY_CHECKS)

    # 組み立ての欄は、ゲートが測った結果だけを写す
    assembly = read(BUILD / "assembly.json")
    assembly["pass"] = checks.get("assembly.path", {}).get("pass") is True
    assembly["calibration"] = {"pass": checks.get("instrument.calibration", {}).get("pass") is True,
                               "by": "tools/mechgate.py instrument.calibration"}
    measured_steps = {row["id"]: row for row in (checks.get("assembly.path", {}).get("detail") or {}).get("steps", [])}
    for step in assembly["steps"]:
        row = measured_steps.get(step["id"], {})
        step["report"] = {"samples": row.get("checkedPoses", 0), "pass": row.get("pass") is True,
                          "source": f"models/{MODEL}/build/gate_report.json#assembly.path"}
    if write(BUILD / "assembly.json", assembly):
        print("assembly.json を更新した。ゲートを流し直してから、もう一度実行する")
        return 1

    tables, hashes = build_tables()
    outcome = calculate(tables)
    write(BUILD / "sim_tables.json", tables)
    passed = outcome.pop("pass_")
    spec = read(HERE / "spec.json")
    drive_rows = (checks.get("interface.drive", {}).get("detail") or {}).get("all") or []
    measured_by_id = {row.get("id"): row for row in drive_rows if isinstance(row, dict)}
    interfaces = []
    for item in spec["interfaces"]:
        if item["type"] != "drive":
            continue
        row = measured_by_id.get(item["id"], {})
        ok = checks.get("interface.drive", {}).get("pass") is True and row.get("pass") is True
        interfaces.append(dict(id=item["id"], label=f"{item['driver']} → {item['driven']}",
                               status="pass" if ok else "fail",
                               detail="tools/mechgate.py interface.drive が測った", measurement=row))
    write(BUILD / "drive_report.json", dict(
        model=MODEL, overall=dict(geometryPass=geometry), interfaces=interfaces,
        calibration=[dict(id="instrument.calibration", label="ゲートの計器の校正",
                          **{"pass": checks.get("instrument.calibration", {}).get("pass") is True},
                          detail="tools/mechgate.py")],
        hardwareUnknown=[row["what"] for row in spec["unknowns"]], sourceHashes=hashes))
    write(BUILD / "simulate_report.json", dict(
        model=MODEL, method="脚を床から浮かせて 1 軸で振る運動方程式。歩行は sim_gait.py が別に見る",
        overall={"pass": passed, "calculationPass": passed, "status": "conditional" if passed else "fail"},
        driveGeometry=dict(geometryPass=geometry, sourceHashesFresh=measured and not changed),
        assumptions=["質量は中実の PLA。実物は充填 15% で軽い",
                     "左右の脚とホーンとねじの合計を、サーボ 2 個の停動の合計と比べる",
                     "摩擦は共通の見積もり。床からの力は入っていない"],
        sourceHashes=hashes, **outcome))
    write(BUILD / "boolean_evidence.json", {})
    write(BUILD / "ui.json", dict(
        label="スマホ板ロボット", displayName="スマホ板ロボット", navLabel="スマホ板ロボット",
        physics=dict(title="脚の振り", playback="motion-frames", term="脚", chartSeries=["leg_right", "leg_left"],
                     openLabel="前へ振る", closeLabel="後ろへ振る",
                     chartLabel="足先の高さ", chartAxis="高さ [mm]",
                     simLimits="脚を床から浮かせて ±45° 振る計算です。歩くときの床からの力は入っていません。歩きは sim_gait.py で別に見ています。",
                     massNote="中実の PLA として数えた上限側の値です。左右の合計をサーボ 2 個の停動の合計と比べています。"),
        assembly=dict(servoSetup="脚をまっすぐ持ち、Z 命令でまっすぐの位置を覚えさせてからねじを締めます。"),
        print=dict(downloadBase="prints"),
        legendGroups=[dict(label="脚", prefix="leg_", color="#70797f"),
                      dict(label="ホーンのねじ", prefix="bolts_", color="#b0b5b8"),
                      dict(label="サーボ", prefix="servo_", color="#1c1c1c")]))
    result = lattice_web.export(MODEL)
    print(json.dumps(dict(geometry=geometry, calculation=passed, peakNm=round(outcome["peakIdealTorqueNm"], 3),
                          stallFraction=round(outcome["stallFraction"], 3), export=result), ensure_ascii=False)[:400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
