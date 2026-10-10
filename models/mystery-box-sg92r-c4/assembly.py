"""C4の組立工程を同一フレームで表示・EXACT検査する。"""
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
    Allowance, AssemblyPlan, IDENTITY, join_paths, rotate_x_about,
    rotation_group, run, translated_group,
)


def mechanism_pose(servo_degrees):
    return rotate_x_about(servo_degrees - P.SERVO_MIN_DEG, 0.0, P.CAM_AXIS_Z * 1000.0)


def main():
    parts = (
        "housing", "faceplate", "guide_frame", "bottom", "carrier_center", "carrier_inner",
        "carrier_outer", "camshaft", "horn_coupler", "cam_center", "cam_inner", "cam_outer",
        "bearing_keeper", "servo_clip", "servo_body", "servo_horn", "servo_wire",
    )
    plan = AssemblyPlan(P.MODEL_ID, parts)
    plan.seed("housing")
    pose_90 = mechanism_pose(90.0)
    reference_allowances = (Allowance(
        ("servo_body", "servo_horn"), "reference_internal",
        maximum_common_volume_mm3=0.030,
        bounds_mm=((-7.5, -2.3, 37.7), (-4.5, 2.3, 42.3))),)
    plan.add(
        "route-wire", "配線を保持台の切欠きへ通す",
        "柔らかい配線を本体より先に下側から上げる。保持台を避けるため-Yへ12mm寄せ、所定高さで切欠きへ戻す。",
        "配線の剛体近似を、逃がした上昇経路と切欠きまでの横移動の両方で外装へ照合する。曲げやすさは実物未検証。",
        ("servo_wire",), join_paths(
            translated_group({"servo_wire": IDENTITY}, (0, -12, -36), (0, -12, 0)),
            translated_group({"servo_wire": IDENTITY}, (0, -12, 0), (0, 0, 0))),
    )
    plan.add(
        "servo-body", "SG92R本体を入れる",
        "配線を切欠きに通した状態で、SG92R本体を下側から保持台へ入れる。ホーンはまだ付けない。",
        "本体が外装と先に通した配線を通り抜けず保持位置へ入る。",
        ("servo_body",), translated_group({"servo_body": IDENTITY}, (0, 0, -36), (0, 0, 0)),
    )
    clip_strain = 1.5 * P.SERVO_CLIP_T * P.SERVO_CLIP_HOOK / P.SERVO_CLIP_FLEX_L ** 2 * 100.0
    plan.add(
        "servo-clip", "サーボ保持具を入れる",
        "サーボ保持具を下側から押し込み、指定された爪だけをしならせる。",
        "爪の局所変形は既存判定範囲内で、PLAひずみ2%以下である。",
        ("servo_clip",), translated_group({"servo_clip": IDENTITY}, (0, 0, -24), (0, 0, 0)),
        (Allowance(("servo_body", "servo_clip"), "snap", zone="servo_clip",
                   deflection_mm=P.SERVO_CLIP_HOOK * 1000.0,
                   strain_percent=clip_strain),),
    )
    plan.add(
        "horn-at-90", "付属ホーンを90度で付ける",
        "SG92Rを電源で中央の90度へ合わせる。電源を切ってから付属ホーンを+X側から出力軸へ付ける。実物でのホーン装着と通電は未検証。",
        "SG92R正本の本体とホーンの小さな重なりは参照部品内部として記録し、印刷部品の干渉と分ける。",
        ("servo_horn",), translated_group({"servo_horn": pose_90}, (12, 0, 0), (0, 0, 0)),
        reference_allowances,
    )
    plan.add(
        "coupler-at-90", "ホーン受けを90度で入れる",
        "印刷したホーン受けを+X側から90度の付属ホーンへ差し込む。",
        "ホーン受けが外装とSG92Rを通り抜けず終点へ入る。",
        ("horn_coupler",), translated_group({"horn_coupler": pose_90}, (12, 0, 0), (0, 0, 0)),
        reference_allowances,
    )
    center_path = join_paths(
        translated_group({"cam_center": pose_90}, (15, 0, -32), (15, 0, 0)),
        translated_group({"cam_center": pose_90}, (15, 0, 0), (0, 0, 0)))
    plan.add(
        "cam_center", "中心カムをL字経路で90度位置へ入れる",
        "中心カムを箱内で+Xへ15mm逃がして下側から軸高さまで上げ、その高さで-Xへ滑らせて90度位置へ置く。",
        "ホーン受けを避ける上昇と横移動を連続表示し、全既設部品へ照合する。",
        ("cam_center",), center_path, reference_allowances,
    )
    for name, label in (("cam_inner", "内環カム"), ("cam_outer", "外環カム")):
        plan.add(
            name, f"{label}を90度で置く",
            f"{label}を90度位相のまま下側から最終の軸位置へ入れる。",
            "既設部品との全組み合わせを同じ上昇経路で検査する。",
            (name,), translated_group({name: pose_90}, (0, 0, -32), (0, 0, 0)),
            reference_allowances,
        )
    plan.add(
        "camshaft-at-90", "主軸を+X側から通す",
        "六角主軸を+X側から右軸受け、3個のカム、ホーン受けへ通す。",
        "主軸が90度位相の全カムと受けを通り、既設部品と干渉しない。",
        ("camshaft",), translated_group({"camshaft": pose_90}, (42, 0, 0), (0, 0, 0)),
        reference_allowances,
    )
    keeper_pivot = (0.0, P.CAM_AXIS_Z * 1000.0)
    insert_path = translated_group(
        {"bearing_keeper": rotate_x_about(90.0, *keeper_pivot)}, (12, 0, 0), (0, 0, 0))
    turn_path = rotation_group(
        {"bearing_keeper": lambda angle: rotate_x_about(angle, *keeper_pivot)}, 90.0, 0.0)
    keeper_strain = 1.5 * P.KEEPER_DETENT_ARM_T * P.KEEPER_DETENT_INTERFERENCE / P.KEEPER_DETENT_ARM_L ** 2 * 100.0
    plan.add(
        "keeper-bayonet", "軸受け保持具をバヨネット固定する",
        "保持具を90度に合わせて+X側から入れる。その位置のままX軸回りに0度まで戻して板ばねを凹みへ掛ける。",
        "+X挿入と90度から0度への回転を連続表示し、指定した板ばね領域だけの変形を許す。",
        ("bearing_keeper",), join_paths(insert_path, turn_path),
        (Allowance(("bearing_keeper", "housing"), "snap", zone="keeper_detent",
                   deflection_mm=P.KEEPER_DETENT_INTERFERENCE * 1000.0,
                   strain_percent=keeper_strain),),
    )
    mechanism = ("servo_horn", "horn_coupler", "camshaft", "cam_center", "cam_inner", "cam_outer")
    plan.add(
        "return-to-10", "機構を10度へ戻す",
        "ホーンと主軸一式を90度からデモ開始角10度へ一緒に低速で戻す。案内枠と格子はこの後に入れる。",
        "90度で組んだ実形状を1度刻みで10度へ戻し、固定部品との干渉がない。",
        mechanism,
        rotation_group({name: mechanism_pose for name in mechanism}, 90.0, P.SERVO_MIN_DEG),
        reference_allowances,
    )
    plan.add(
        "stage-guide-frame", "案内枠を箱の上へ仮置きする",
        "案内枠を箱より十分上の+90mm位置へ下ろし、箱外で格子を組む台にする。",
        "案内枠は+110mmから+90mmまで周囲の全既設部品と照合する。",
        ("guide_frame",), translated_group({"guide_frame": IDENTITY}, (0, 0, 110), (0, 0, 90)),
    )
    plan.add(
        "center-into-guide", "中心格子を+X側から入れる",
        "中心格子を+90mm位置で+X側から案内枠のC形開口へ水平に入れる。",
        "中心格子を案内枠と箱内の全既設部品に対して検査する。",
        ("carrier_center",), translated_group({"carrier_center": IDENTITY}, (12, 0, 90), (0, 0, 90)),
    )
    plan.add(
        "inner-into-guide", "内環格子を案内枠へ入れる",
        "中心格子を入れた後、内環格子をZ上側から+90mm位置の案内枠へ下ろす。",
        "内環格子を中心格子、案内枠、箱内の全既設部品に対して検査する。",
        ("carrier_inner",), translated_group({"carrier_inner": IDENTITY}, (0, 0, 110), (0, 0, 90)),
    )
    plan.add(
        "outer-into-guide", "外環格子を案内枠へ入れる",
        "中心格子と内環格子を入れた後、外環格子をZ上側から+90mm位置の案内枠へ下ろす。",
        "外環格子を中心、内環、案内枠、箱内の全既設部品に対して検査する。",
        ("carrier_outer",), translated_group({"carrier_outer": IDENTITY}, (0, 0, 110), (0, 0, 90)),
    )
    group = ("guide_frame", "carrier_outer", "carrier_inner", "carrier_center")
    plan.add(
        "lower-guide-group", "格子4部品一式を箱へ下ろす",
        "箱外で組んだ案内枠、外環、内環、中心格子の相対位置を保ったまま+90mmから箱へ下ろす。",
        "4部品相互と箱内の全既設部品を、同じ1mm刻みの下降フレームで検査する。",
        group, translated_group({name: IDENTITY for name in group}, (0, 0, 90), (0, 0, 0)),
    )
    face_strain = 1.5 * 1.8 * 0.4 / 14.0 ** 2 * 100.0
    plan.add(
        "faceplate", "天板を上から付ける",
        "天板を上から下ろし、指定した4箇所の爪だけをしならせて外装へ掛ける。",
        "天板の爪領域だけを許し、格子と案内枠を含む全既設部品へ照合する。",
        ("faceplate",), translated_group({"faceplate": IDENTITY}, (0, 0, 20), (0, 0, 0)),
        (Allowance(("faceplate", "housing"), "snap", zone="faceplate",
                   deflection_mm=0.4, strain_percent=face_strain),),
    )
    bottom_strain = 1.5 * P.BOTTOM_TAB_T * max(0.0, P.BOTTOM_TAB_HOOK - P.BOTTOM_GAP) / P.BOTTOM_TAB_L ** 2 * 100.0
    plan.add(
        "bottom", "底板を下から付ける",
        "底板を下から上げ、指定した爪だけをしならせて外装へ掛ける。",
        "底板の爪領域だけを許し、SG92Rと保持具を含む全既設部品へ照合する。",
        ("bottom",), translated_group({"bottom": IDENTITY}, (0, 0, -20), (0, 0, 0)),
        (Allowance(("bottom", "housing"), "snap", zone="bottom",
                   deflection_mm=max(0.0, P.BOTTOM_TAB_HOOK - P.BOTTOM_GAP) * 1000.0,
                   strain_percent=bottom_strain),),
    )
    raw_calibration = verify.exact_volume_calibration()
    calibration = {"positiveCommonVolumeMm3": raw_calibration["positive_common_volume_mm3"],
                   "negativeCommonVolumeMm3": raw_calibration["negative_common_volume_mm3"],
                   "pass": raw_calibration["pass"]}
    run(plan, verify, HERE / "build", verify.load, calibration)


if __name__ == "__main__":
    main()
