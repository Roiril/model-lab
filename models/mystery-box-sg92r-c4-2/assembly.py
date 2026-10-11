"""C4-2 の累積組立工程を表示フレームとMANIFOLD検査へ同時に書き出す。"""
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))

import motion  # noqa: E402
import params as P  # noqa: E402
import evidence as E  # noqa: E402
import verify  # noqa: E402
from lattice_assembly import (  # noqa: E402
    Allowance, AssemblyPlan, IDENTITY, join_paths, rotation_group, run, translated_group,
)


TRANSLATION_STEP_MM = 0.99
ROTATION_STEP_DEG = 1.0
ROTATION_SAMPLE_STEP_DEG = 0.999


def translated(base, start, end):
    return translated_group(base, start, end, maximum_step=TRANSLATION_STEP_MM)


def pose(part, degree):
    values = motion.transforms(degree)
    return E.transform_matrix(values[part]) if part in values else IDENTITY.copy()


def reference_allowances():
    rows = []
    allowance = verify.CANONICAL_ALLOWANCES.get(("servo_body", "servo_horn"))
    if allowance is not None:
        bounds = allowance["componentBoundsMm"][0]
        rows.append(Allowance(("servo_body", "servo_horn"), "reference_internal",
                              maximum_common_volume_mm3=allowance["maximumCommonVolumeMm3"],
                              bounds_mm=bounds))
    return tuple(rows)


def add_vertical(plan, labels, part, title, distance, allowances=()):
    start = (0, 0, distance)
    plan.add(part, title, f"{labels[part]}を開放側から所定位置へ入れる。",
             "0.99mm以下の累積フレームで全既設部品とのMANIFOLD共通体積を測定する。",
             (part,), translated({part: IDENTITY}, start, (0, 0, 0)), allowances)


def snap_allowance(part):
    key = tuple(sorted((part, "housing")))
    definition = verify.CANONICAL_ALLOWANCES[key]
    strain = (1.5 * definition["tabThicknessMm"] * definition["maximumDeflectionMm"]
              / definition["freeLengthMm"] ** 2 * 100.0)
    return Allowance((part, "housing"), "snap", zone=part,
                     deflection_mm=definition["maximumDeflectionMm"],
                     strain_percent=strain, allow_at_final=True)


def snap_evidence(plan, meshes):
    rows = []
    for step in plan.steps:
        allowances = [item for item in step["_allowances"] if item.kind == "snap"]
        for allowance in allowances:
            key = tuple(sorted(allowance.parts))
            contacts = []
            rejected = []
            for sample_index, matrices in enumerate(step["_matrices"]):
                if not set(key) <= set(matrices):
                    continue
                intersection_vertices = []

                def record_intersection_vertex(point):
                    intersection_vertices.append(tuple(float(value) for value in point))
                    return True

                geometry = E.exact_common_geometry(
                    meshes[key[0]], matrices[key[0]], meshes[key[1]], matrices[key[1]],
                    vertex_predicate=record_intersection_vertex)
                geometry["intersection_vertices_mm"] = intersection_vertices
                if geometry["common_volume_mm3"] <= 0.001:
                    continue
                accepted = verify.allowed_intersection(key, geometry)
                item = {"sample": sample_index,
                        "progress": step["frames"][sample_index]["progress"],
                        "commonVolumeMm3": geometry["common_volume_mm3"],
                        "intersectionBoundsMm": geometry["intersection_bounds_mm"],
                        "maximumIntrusionMm": geometry.get("maximum_snap_intrusion_mm"),
                        "intrusionMethod": geometry.get("snap_intrusion_method"),
                        "strainPercent": geometry.get("snap_strain_percent"),
                        "pass": accepted}
                contacts.append(item)
                if not accepted:
                    rejected.append(item)
            maximum_intrusion = max((item["maximumIntrusionMm"] for item in contacts
                                     if item["maximumIntrusionMm"] is not None), default=None)
            maximum_strain = max((item["strainPercent"] for item in contacts
                                  if item["strainPercent"] is not None), default=None)
            rows.append({"step": step["id"], "parts": list(key),
                         "contactSamples": len(contacts),
                         "maximumActualIntrusionMm": maximum_intrusion,
                         "maximumActualStrainPercent": maximum_strain,
                         "declaredDeflectionMm": allowance.deflection_mm,
                         "rejectedContacts": rejected,
                         "pass": bool(contacts) and not rejected})
    return {"interfaces": rows, "pass": bool(rows) and all(row["pass"] for row in rows)}


def main():
    calibration = E.calibration()
    if not calibration["pass"]:
        raise SystemExit("calibration failed before prototype STL inspection")
    manifest = json.loads((HERE / "build" / "manifest.json").read_text(encoding="utf-8"))
    parts = tuple(part["id"] for part in manifest["parts"] if not part.get("fit_only"))
    labels = {part["id"]: part["label"] for part in manifest["parts"]}
    required = {"housing", "guide_frame", "cam_disk", "servo_body", "servo_horn",
                "horn_coupler", "drive_key", *(f"carrier_{name}" for name in P.GROUPS)}
    missing = sorted(required - set(parts))
    if missing:
        raise SystemExit(f"assembly required parts missing: {missing}")
    plan = AssemblyPlan(P.MODEL_ID, parts)
    plan.seed("housing")
    references = reference_allowances()

    # 付属ホーンと受けを先に低い保持壁の外側から入れる。SG92R本体は底板を
    # 付ける前に直線で入れ、出力軸を下から付属ホーンへ差す。
    assembly_degree = P.ASSEMBLY_SERVO_DEG
    horn_group = {name: pose(name, assembly_degree)
                  for name in ("servo_horn", "horn_coupler")}
    plan.add("stage-horn-coupler", "付属ホーンとホーン受けを先に入れる",
             "箱外で付属ホーンとホーン受けを組み、底側の+X寄りから所定高さへ上げて中央へ移す。",
             "上側の固定止めを通さず、低い保持壁より上の最終高さで横移動する。",
             tuple(horn_group), join_paths(
                 translated(horn_group, (30, 0, -45), (30, 0, 0)),
                 translated(horn_group, (30, 0, 0), (0, 0, 0))))
    body_group = {"servo_body": IDENTITY.copy()}
    if "servo_wire" in parts:
        body_group["servo_wire"] = IDENTITY.copy()
    plan.add("servo-body", "SG92R本体を底側から入れる",
             "配線の自由端を+X出口へ先に通し、本体と正本の短い配線部を底側から直線で入れる。",
             "正本配線の未収録部分は曲げずに通せる経路を外装開口の断面で別に確認する。",
             tuple(body_group), translated(body_group, (0, 0, -40), (0, 0, 0)), references)

    # 17mmのキー頭は円盤の10.2mm角穴を通らない。円盤を先に置き、キーを最後に差す。
    drive_order = ("servo_horn", "horn_coupler", "cam_disk", "drive_key")
    heights = {"drive_key": 32, "cam_disk": 48}
    for part in ("cam_disk", "drive_key"):
        matrix = pose(part, assembly_degree)
        label = labels[part]
        plan.add(f"{part}-at-assembly-angle", f"{label}を組立角で入れる",
                 f"{label}を上側から{assembly_degree:.0f}度位相の所定位置へ入れる。",
                 "正本本体とホーンの既知範囲以外は共通体積0.001mm3以下を要求する。",
                 (part,), translated({part: matrix}, (0, 0, heights[part]), (0, 0, 0)), references)

    if "cam_keeper" in parts:
        keeper_strain = (1.5 * P.KEEPER_TAB_T * P.KEEPER_TAB_DEFLECTION
                         / P.KEEPER_TAB_FREE_L ** 2 * 100.0)
        plan.add("cam-keeper-snap", "円盤止め輪を上から押し込む",
                 "4本の爪を支持環へ通し、指定範囲だけをしならせて下面へ掛ける。",
                 "爪の実座標範囲だけを弾性接触として扱い、ひずみ2%以下を要求する。",
                 ("cam_keeper",), translated({"cam_keeper": IDENTITY}, (0, 0, 24), (0, 0, 0)),
                 (Allowance(("cam_keeper", "housing"), "snap", zone="cam_keeper",
                            deflection_mm=P.KEEPER_TAB_DEFLECTION * 1000.0,
                            strain_percent=keeper_strain,
                            allow_at_final=True),))

    rotating = drive_order
    plan.add("return-home", "駆動一式をホーム角へ戻す",
             f"組立角{assembly_degree:.0f}度からホーム角{P.HOME_SERVO_DEG:.0f}度へ一式で戻す。",
             "1度以下の同一フレームで正回転を検査する。逆分解は同じフレームを逆順に検査する。",
             rotating,
             rotation_group({part: (lambda degree, name=part: pose(name, degree))
                             for part in rotating}, assembly_degree, P.HOME_SERVO_DEG,
                            maximum_step=ROTATION_SAMPLE_STEP_DEG), references)

    # manifestに追加された保持具は、格子群より先に開放側から入れる。
    reserved = {"housing", "guide_frame", "faceplate", "bottom", "servo_wire", "servo_body",
                *drive_order, "cam_keeper", *(f"carrier_{name}" for name in P.GROUPS)}
    for part in parts:
        if part not in reserved:
            add_vertical(plan, labels, part, f"{labels[part]}を下側から入れる", -32)

    plan.add("stage-guide", "案内枠を箱上へ仮置きする",
             "案内枠を箱外の組立高さへ下ろす。",
             "外装と既設駆動部品を通り抜けない。", ("guide_frame",),
             translated({"guide_frame": IDENTITY}, (0, 0, 120), (0, 0, 90)))
    for group in P.GROUPS:
        part = f"carrier_{group}"
        path = translated({part: IDENTITY}, (0, 0, 115), (0, 0, 90))
        if group == "upper_left":
            path = join_paths(
                translated({part: IDENTITY}, (0.025, 0, 115), (0.025, 0, 108)),
                translated({part: IDENTITY}, (0.025, 0, 108), (0, 0, 108)),
                translated({part: IDENTITY}, (0, 0, 108), (0, 0, 90)))
        plan.add(f"stage-{part}", f"{labels[part]}を案内枠へ入れる",
                 "箱外の案内枠へ上側から入れる。",
                 "案内枠と先に入れたキャリアを含む全既設部品へ照合する。", (part,),
                 path)
    group_parts = ("guide_frame", *(f"carrier_{name}" for name in P.GROUPS))
    plan.add("lower-guide-group", "案内枠と4群を箱へ下ろす",
             "箱外で組んだ相対位置を保ち、格子一式を所定位置へ下ろす。",
             "全5部品の累積フレームを既設部品へ照合する。", group_parts,
             translated({part: IDENTITY for part in group_parts}, (0, 0, 90), (0, 0, 0)))

    if "faceplate" in parts:
        add_vertical(plan, labels, "faceplate", "天板を上側から付ける", 24,
                     (snap_allowance("faceplate"),))
    if "bottom" in parts:
        add_vertical(plan, labels, "bottom", "底板を下側から付ける", -24,
                     (snap_allowance("bottom"),))

    raw = E.exact_volume_calibration()
    assembly_calibration = {
        "positiveCommonVolumeMm3": raw["positive_common_volume_mm3"],
        "negativeCommonVolumeMm3": raw["negative_common_volume_mm3"],
        "pass": calibration["pass"] and raw["pass"],
        "prototypeInspectedAfterCalibration": True,
    }
    run(plan, verify, HERE / "build", E.load, assembly_calibration)
    report_path = HERE / "build" / "assembly_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["frameContract"] = {"maximumTranslationStepMm": TRANSLATION_STEP_MM,
                               "maximumRotationStepDeg": ROTATION_STEP_DEG,
                               "pass": (report["frameValidation"]["maxTranslationStepMm"] <= TRANSLATION_STEP_MM + 1e-6
                                        and report["frameValidation"]["maxRotationStepDeg"] <= ROTATION_STEP_DEG + 1e-6)}
    report["sourceHashes"] = E.source_hashes(
        path for path in (
            HERE / "assembly.py", HERE / "evidence.py", HERE / "verify.py",
            HERE / "params.py", HERE / "motion.py", HERE / "contact_envelope.py",
            HERE / "model.py",
            HERE / "build" / "manifest.json", ROOT / "tools" / "lattice_assembly.py",
            ROOT / "models" / "mystery-box-sg92r-c4" / "verify.py",
        ) if path.exists())
    meshes = {name: E.load(name) for name in parts}
    report["snapEvidence"] = snap_evidence(plan, meshes)
    report["pass"] = (report["pass"] and report["frameContract"]["pass"]
                      and report["snapEvidence"]["pass"])
    E.write_json(report_path, report)
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
