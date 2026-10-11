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
        "camshaft", "left_spacer", "cam_0", "cam_1", "cam_2", "cam_3", "cam_4", "cam_gear", "drive_gear",
        "cap_left", "cap_right", "servo_clip", "drive_bearing_clip",
        "ref_servo", "ref_horn", "ref_wire",
    )
    plan = AssemblyPlan(P.MODEL_ID, parts)
    plan.seed("shell")
    servo_pivot = (P.SERVO_AXIS_Y * 1000.0, P.SERVO_AXIS_Z * 1000.0)
    cam_pivot = (P.CAM_AXIS_Y * 1000.0, P.CAM_AXIS_Z * 1000.0)
    servo_90 = rotate_x_about(-75.0, *servo_pivot)
    cam_90 = rotate_x_about(75.0, *cam_pivot)

    plan.add(
        "servo-outside", "箱の外でSG92Rを90度へ合わせる",
        "箱の外でSG92Rを電源につなぎ、中央の90度へ合わせてから電源を切る。配線は曲げられる状態にしておく。",
        "正本STLのSG92R本体と配線を箱の上方へ置き、ホーンを付ける空間を残す。",
        ("ref_servo", "ref_wire"),
        translated_group({"ref_servo": IDENTITY, "ref_wire": IDENTITY},
                         (0, 0, 90), (0, 0, 65)),
    )
    plan.add(
        "horn-on-servo", "付属ホーンを90度で差す",
        "正本形状の付属ホーンを90度の出力軸へ+X側から差す。スプライン歯は参照STLに無いため回転止めは実物で確かめる。",
        "付属ホーンが箱外のSG92R出力軸へ同軸で着座する。",
        ("ref_horn",), translated_group({"ref_horn": servo_90},
                                         (12, 0, 65), (0, 0, 65)),
    )
    plan.add(
        "drive-gear-on-horn", "駆動歯車をホーンへ差す",
        "駆動歯車の非対称受けを付属ホーンへ+X側から差し、2mmの盲底へ着座させる。",
        "ホーンの丸端、中心ハブ、非対称腕が片側0.2mmの受けへ入り、歯車と一体で動く。",
        ("drive_gear",), translated_group({"drive_gear": servo_90},
                                           (12, 0, 65), (0, 0, 65)),
    )
    plan.add(
        "servo-unit-in", "SG92R一式をU字座へ下ろす",
        "SG92R、付属ホーン、駆動歯車の相対位置を保ち、配線と一緒に上から下ろす。直径6mmジャーナルをU字座へ置く。",
        "SG92R本体と配線は着座レールへ入り、駆動歯車のジャーナルは半径0.25mm隙間のU字座へ着座する。",
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
    plan.add(
        "drive-bearing-clip", "ジャーナル上クリップを付ける",
        "別刷りの上クリップをU字座へまっすぐ下ろし、左右の爪を凹みへ掛ける。",
        "ジャーナル上面に0.25mmの隙間を残し、駆動歯車の浮上を止める。",
        ("drive_bearing_clip",),
        translated_group({"drive_bearing_clip": IDENTITY}, (0, 0, 18), (0, 0, 0)),
        (Allowance(
            ("drive_bearing_clip", "shell"), "snap", zone="drive_clip_hooks",
            deflection_mm=(P.DRIVE_CLIP_HOOK - P.DRIVE_CLIP_GAP) * 1000.0,
            strain_percent=(1.5 * P.DRIVE_CLIP_T
                            * (P.DRIVE_CLIP_HOOK - P.DRIVE_CLIP_GAP)
                            / ((P.SERVO_AXIS_Z + P.DRIVE_JOURNAL_D / 2
                                + P.DRIVE_CLIP_GAP)
                               - (P.SERVO_AXIS_Z
                                  - (P.DRIVE_JOURNAL_D / 2
                                     + P.DRIVE_BEARING_RADIAL_CLEARANCE
                                     + P.DRIVE_BEARING_WALL)
                                  + 0.00235 + P.DRIVE_CLIP_T)) ** 2 * 100.0),
            allow_at_final=True,
            bounds_mm=((7.75, -6.5, 19.45), (10.75, 6.5, 20.95))),),
    )
    cam_group = tuple(["left_spacer"] + [f"cam_{index}" for index in range(P.GRID_N)] + ["cam_gear"])
    plan.add(
        "cams-at-90", "スペーサーとカム一式を90度位相で置く",
        "左スペーサー、5個の偏心カム、従動歯車を90度位相のまま上から置く。15度の形へ先に戻さない。",
        "軸方向保持ハブが隣接面へ0.2mmを残し、カム一式が90度位相の終点へ着座する。",
        cam_group, translated_group({name: cam_90 for name in cam_group}, (0, 0, 35), (0, 0, 0)),
    )
    plan.add(
        "camshaft-at-90", "六角カム軸を右から通す",
        "六角カム軸を右側から軸受け、従動歯車、5個のカム、左スペーサーへ順に通す。",
        "六角軸が90度位相の全カムとスペーサーを通り、周囲の既設部品と干渉しない。",
        ("camshaft",), translated_group({"camshaft": cam_90}, (82, 0, 0), (0, 0, 0)),
    )
    cap_insert = rotate_x_about(90.0, *cam_pivot)
    cap_tip_r = (P.CAP_BODY_R - P.CAP_DETENT_INTERFERENCE
                 + P.CAP_DETENT_ARM_T / 2) * 1000.0
    cap_tip_y = cap_tip_r * 2 ** -0.5
    cap_tip_z = P.CAM_AXIS_Z * 1000.0 + cap_tip_y
    cap_strain = (1.5 * P.CAP_DETENT_ARM_T * P.CAP_DETENT_INTERFERENCE
                  / P.CAP_DETENT_ARM_L ** 2 * 100.0)
    cap_body_inner_x = (P.SHAFT_MAIN_X + P.AXIAL_PLAY / 2) * 1000.0
    right_detent_bounds = ((cap_body_inner_x + 0.3, cap_tip_y - 1.5, cap_tip_z - 1.5),
                            (40.0, cap_tip_y + 1.5, cap_tip_z + 1.5))
    left_detent_bounds = ((-40.0, cap_tip_y - 1.5, cap_tip_z - 1.5),
                          (-cap_body_inner_x - 0.3, cap_tip_y + 1.5, cap_tip_z + 1.5))
    plan.add(
        "right-cap-insert", "右キャップをキー溝へ入れる",
        "右キャップの爪を上下のキー溝へ合わせ、+X側から奥まで差し込む。",
        "右キャップの爪がキー溝を通る。主軸肩の公称隙間は片側0.15mm。カム積層は内向きカラーで別に保持する。",
        ("cap_right",), translated_group({"cap_right": cap_insert}, (8, 0, 0), (0, 0, 0)),
        (Allowance(("cap_right", "shell"), "snap", zone="right_cap_detent",
                   deflection_mm=P.CAP_DETENT_INTERFERENCE * 1000.0,
                   strain_percent=cap_strain, allow_at_final=True,
                   bounds_mm=right_detent_bounds),),
    )
    plan.add(
        "right-cap-lock", "右キャップを90度回して留める",
        "右キャップを90度回し、左右の爪を外装内へ掛けて板ばねを凹みへ戻す。",
        "右キャップの爪が外装へ当たり、印刷したdetentが保持位置へ入る。",
        ("cap_right",), rotation_group({"cap_right": lambda angle: rotate_x_about(
            angle, *cam_pivot)}, 90.0, 0.0),
        (Allowance(("cap_right", "shell"), "snap", zone="right_cap_detent",
                   deflection_mm=P.CAP_DETENT_INTERFERENCE * 1000.0,
                   strain_percent=cap_strain, allow_at_final=True,
                   bounds_mm=right_detent_bounds),),
    )
    plan.add(
        "left-cap-insert", "左キャップをキー溝へ入れる",
        "左キャップの爪を上下のキー溝へ合わせ、-X側から奥まで差し込む。",
        "左キャップの爪がキー溝を通る。主軸肩の公称隙間は片側0.15mm。カム積層は内向きカラーで別に保持する。",
        ("cap_left",), translated_group({"cap_left": cap_insert}, (-8, 0, 0), (0, 0, 0)),
        (Allowance(("cap_left", "shell"), "snap", zone="left_cap_detent",
                   deflection_mm=P.CAP_DETENT_INTERFERENCE * 1000.0,
                   strain_percent=cap_strain, allow_at_final=True,
                   bounds_mm=left_detent_bounds),),
    )
    plan.add(
        "left-cap-lock", "左キャップを90度回して留める",
        "左キャップを90度回し、左右の爪を外装内へ掛けて板ばねを凹みへ戻す。",
        "左キャップの爪が外装へ当たり、印刷したdetentが保持位置へ入る。",
        ("cap_left",), rotation_group({"cap_left": lambda angle: rotate_x_about(
            angle, *cam_pivot)}, 90.0, 0.0),
        (Allowance(("cap_left", "shell"), "snap", zone="left_cap_detent",
                   deflection_mm=P.CAP_DETENT_INTERFERENCE * 1000.0,
                   strain_percent=cap_strain, allow_at_final=True,
                   bounds_mm=left_detent_bounds),),
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
