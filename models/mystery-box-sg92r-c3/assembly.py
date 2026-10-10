"""C3の組立工程を同一フレームで表示・EXACT検査する。"""
from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))

import params as P  # noqa: E402
import verify  # noqa: E402
from lattice_assembly import (  # noqa: E402
    Allowance, AssemblyPlan, IDENTITY, rotate_x_about,
    rotation_group, run, translated_group,
)


def main():
    parts = (
        "shell", "top_frame", "carrier_0", "carrier_1", "carrier_2", "carrier_3", "carrier_4",
        "camshaft", "cam_0", "cam_1", "cam_2", "cam_3", "cam_4", "cam_gear", "drive_gear",
        "cap_left", "cap_right", "servo_clip", "ref_servo", "ref_horn", "ref_wire",
    )
    plan = AssemblyPlan(P.MODEL_ID, parts)
    plan.seed("shell")
    servo_pivot = (P.SERVO_AXIS_Y * 1000.0, P.SERVO_AXIS_Z * 1000.0)
    cam_pivot = (P.CAM_AXIS_Y * 1000.0, P.CAM_AXIS_Z * 1000.0)
    servo_90 = rotate_x_about(-75.0, *servo_pivot)
    cam_90 = rotate_x_about(75.0, *cam_pivot)

    plan.add(
        "servo-at-90", "SG92R一式を90度で入れる",
        "SG92Rを電源で中央の90度へ合わせる。電源を切ってから付属ホーンと駆動歯車の三角印を合わせ、配線と一緒に上から下ろす。実物でのホーン装着と通電は未検証。",
        "SG92R本体、配線、付属ホーン、駆動歯車が同じ経路で外装内へ入る。",
        ("ref_servo", "ref_wire", "ref_horn", "drive_gear"),
        translated_group({"ref_servo": IDENTITY, "ref_wire": IDENTITY,
                          "ref_horn": servo_90, "drive_gear": servo_90},
                         (0, 0, 65), (0, 0, 0)),
    )
    press_strain = 1.5 * P.CLIP_T * P.CLIP_INTERFERENCE / (P.SG.BODY_W ** 2) * 100.0
    plan.add(
        "servo-clip", "サーボ押さえを入れる",
        "サーボ押さえを上からまっすぐ下ろし、指定した片側0.1mmの圧入部だけをしならせる。",
        "圧入は既存検査の位置判定内に限り、PLAひずみ2%以下である。",
        ("servo_clip",), translated_group({"servo_clip": IDENTITY}, (0, 0, 20), (0, 0, 0)),
        (Allowance(("servo_clip", "ref_servo"), "press_fit",
                   deflection_mm=P.CLIP_INTERFERENCE * 1000.0,
                   strain_percent=press_strain),),
    )
    cam_group = tuple([f"cam_{index}" for index in range(P.GRID_N)] + ["cam_gear"])
    plan.add(
        "cams-at-90", "カム一式を90度位相で置く",
        "5個の偏心カムと従動歯車を90度位相のまま上から置く。15度の形へ先に戻さない。",
        "カム一式が駆動歯車と外装を通り抜けず、90度位相の終点へ着座する。",
        cam_group, translated_group({name: cam_90 for name in cam_group}, (0, 0, 35), (0, 0, 0)),
    )
    plan.add(
        "camshaft-at-90", "六角カム軸を右から通す",
        "六角カム軸を右側から軸受け、従動歯車、5個のカムへ順に通す。",
        "六角軸が90度位相の全カムを通り、周囲の既設部品と干渉しない。",
        ("camshaft",), translated_group({"camshaft": cam_90}, (82, 0, 0), (0, 0, 0)),
    )
    plan.add(
        "right-cap", "右キャップを押し込む",
        "右キャップを+X側から軸端へ押し込む。",
        "右キャップが外装と六角軸へ干渉せず終点へ入る。",
        ("cap_right",), translated_group({"cap_right": IDENTITY}, (8, 0, 0), (0, 0, 0)),
    )
    plan.add(
        "left-cap", "左キャップを押し込む",
        "左キャップを-X側から軸端へ押し込む。",
        "左キャップが外装と六角軸へ干渉せず終点へ入る。",
        ("cap_left",), translated_group({"cap_left": IDENTITY}, (-8, 0, 0), (0, 0, 0)),
    )
    rotating = ("ref_horn", "drive_gear", "camshaft", *cam_group)
    functions = {
        "ref_horn": lambda servo: rotate_x_about(-(servo - P.SERVO_HOME_DEG), *servo_pivot),
        "drive_gear": lambda servo: rotate_x_about(-(servo - P.SERVO_HOME_DEG), *servo_pivot),
        "camshaft": lambda servo: rotate_x_about(servo - P.SERVO_HOME_DEG, *cam_pivot),
        **{name: (lambda servo, _name=name: rotate_x_about(
            servo - P.SERVO_HOME_DEG, *cam_pivot)) for name in cam_group},
    }
    plan.add(
        "return-to-15", "カムと歯車を15度へ戻す",
        "左右キャップを付けた後、SG92R出力側とカム軸側を90度からデモ開始角15度まで一緒に低速で戻す。格子列はこの後に入れる。",
        "90度で組んだ実形状を1度刻みで15度まで戻し、既設部品との干渉がない。",
        rotating, rotation_group(functions, 90.0, P.SERVO_HOME_DEG),
    )
    for index in range(P.GRID_N):
        carrier = f"carrier_{index}"
        plan.add(
            f"carrier-{index + 1}", f"格子列{index + 1}を入れる",
            f"格子列{index + 1}を上から外装ガイドへ下ろし、15度位置のカムへ載せる。",
            "既設の全格子列、外装、対応カムに対して同じ下降経路を検査する。",
            (carrier,), translated_group({carrier: IDENTITY}, (0, 0, 12), (0, 0, 0)),
        )
    plan.add(
        "top-frame", "天面案内板を置く",
        "天面案内板を上から5本の格子列の周囲へ下ろし、外装の棚へ置く。",
        "案内板が既設の全格子列と外装へ干渉せず終点へ入る。",
        ("top_frame",), translated_group({"top_frame": IDENTITY}, (0, 0, 12), (0, 0, 0)),
    )
    calibration = verify.collision_calibration()
    calibration = {"positiveCommonVolumeMm3": calibration["positive_common_volume_mm3"],
                   "negativeCommonVolumeMm3": calibration["negative_common_volume_mm3"],
                   "pass": calibration["ok"]}
    run(plan, verify, HERE / "build", lambda name: verify.load_stl(HERE / "build" / f"{name}.stl"), calibration)


if __name__ == "__main__":
    main()
