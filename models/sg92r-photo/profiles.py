"""SG92Rの承認済み寸法と、実物で未確認のC2試験寸法。単位m。"""
from types import SimpleNamespace


C2_TRIAL = {
    "BODY_L": 0.0225, "BODY_W": 0.0118, "BODY_H": 0.0227,
    "BODY_CENTER_X": -0.00535,
    "FLANGE_L": 0.032, "FLANGE_W": 0.0118,
    "FLANGE_BOTTOM_Z": 0.0159, "FLANGE_T": 0.0025,
    "GEAR_COVER_L": 0.0147, "GEAR_COVER_W": 0.0118,
    "GEAR_NECK_DIA": 0.005, "GEAR_COVER_BOTTOM_Z": 0.0227,
    "GEAR_COVER_H": 0.004,
    "SHAFT_DIA": 0.0046, "SHAFT_BOTTOM_Z": 0.0267, "SHAFT_H": 0.0032,
    # 同じクロスホーンの図がないため、承認済み積層をギア頂部差だけ移す。
    "HORN_ARM_BOTTOM_Z": 0.0302, "HORN_HUB_BOTTOM_Z": 0.0272,
    "HORN_TOP_Z": 0.0317, "HORN_SOCKET_TOP_Z": 0.0307,
    # 取付穴ピッチと配線外形は既存実測・仮値を保つ。C2の位置決めには使わない。
}


def load_profile(name, base):
    source = base if isinstance(base, dict) else vars(base)
    values = {key: value for key, value in source.items() if key.isupper()}
    if name == "approved":
        values.update(PROFILE_ID=name, REFERENCE_PREFIX="sg92r-photo")
    elif name == "c2-drawing-trial":
        values.update(C2_TRIAL)
        values.update(
            PROFILE_ID=name,
            REFERENCE_PREFIX="sg92r-photo-c2-drawing-trial",
            PHYSICAL_FIT_CONFIRMED=False,
            PROFILE_SOURCE="servo-mini-towerpro-sg92r-details.jpg; images.png; SG92R_2.jpg",
            PROFILE_HORN_NOTE="クロスホーン上端31.7mmは積層を保った仮値。実物組立前。",
        )
    else:
        raise ValueError(f"Unknown SG92R profile: {name}")
    return SimpleNamespace(**values)


def profile_record(profile):
    """C2レポートで使う採用値と留保。"""
    return dict(
        id=profile.PROFILE_ID,
        physical_fit_confirmed=getattr(profile, "PHYSICAL_FIT_CONFIRMED", False),
        source=getattr(profile, "PROFILE_SOURCE", "approved params.py"),
        body_mm=[round(getattr(profile, name) * 1000, 4)
                 for name in ("BODY_L", "BODY_W", "BODY_H")],
        shaft_near_end_mm=round((profile.BODY_CENTER_X + profile.BODY_L / 2) * 1000, 4),
        shaft_far_end_mm=round((profile.BODY_L / 2 - profile.BODY_CENTER_X) * 1000, 4),
        flange_bottom_mm=round(profile.FLANGE_BOTTOM_Z * 1000, 4),
        flange_thickness_mm=round(profile.FLANGE_T * 1000, 4),
        gear_top_mm=round((profile.GEAR_COVER_BOTTOM_Z + profile.GEAR_COVER_H) * 1000, 4),
        bare_shaft_top_mm=round((profile.SHAFT_BOTTOM_Z + profile.SHAFT_H) * 1000, 4),
        cross_horn_top_mm=round(profile.HORN_TOP_Z * 1000, 4),
        horn_note=getattr(profile, "PROFILE_HORN_NOTE", ""),
        confirmation="サーボ座試片とC2の印刷・組立が成功した後に実物適合を記録する。",
    )
