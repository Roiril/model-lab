"""SG92R photo-reference dimensions. All values are metres."""

# 単位: m

# Photo-derived dimensions (92-1.png / 92-2.png)
BODY_L = 0.023  # 本体の長さ（23mm）
BODY_W = 0.012  # 本体の奥行（12mm）
BODY_H = 0.022  # 本体ケース上面までの高さ（22mm）

FLANGE_L = 0.032  # 取付耳の全長（32mm）
FLANGE_W = 0.012  # 取付耳の奥行（12mm）
FLANGE_BOTTOM_Z = 0.016  # 本体底から取付耳下面までの高さ（16mm）
FLANGE_T = 0.002  # 取付耳の厚み（2mm）

GEAR_COVER_L = 0.014  # 上面カバーの全長（14mm、訂正画像）
GEAR_COVER_W = 0.012  # 上面カバーの円形部分の直径（12mm、写真からの推定）
GEAR_NECK_DIA = 0.004  # 上面カバーの細い部分の幅（4mm）
GEAR_COVER_BOTTOM_Z = 0.022  # 本体底からギアカバー下面までの高さ（22mm）
GEAR_COVER_H = 0.005  # ギアカバーの高さ（5mm）

SHAFT_DIA = 0.0046  # 出力軸の直径（4.6mm）
SHAFT_BOTTOM_Z = 0.027  # 本体底から出力軸下面までの高さ（27mm）
SHAFT_H = 0.0035  # 出力軸の高さ（3.5mm、ホーン位置に合わせた仮値）

HORN_LEFT_X = -0.018  # 軸原点から長腕左端までのX距離（-18mm）
HORN_RIGHT_X = 0.016  # 軸原点から長腕右端までのX距離（16mm）
HORN_SPAN_Y = 0.017  # 短腕の全長（17mm）
HORN_ROOT_W = 0.007  # 長腕根元の幅（7mm）
HORN_TIP_W = 0.004  # 長腕先端の幅（4mm）
HORN_SHORT_W = 0.004  # 短腕の幅（4mm）
HORN_ARM_BOTTOM_Z = 0.0305  # 本体底からホーン腕下面までの高さ（30.5mm）
HORN_ARM_T = 0.0015  # ホーンの腕厚（1.5mm）
HORN_HUB_DIA = 0.007  # ホーンハブの直径（7mm）
HORN_HUB_BOTTOM_Z = 0.0275  # 本体底からホーンハブ下面までの高さ（27.5mm）
HORN_TOP_Z = 0.032  # 本体底からホーン最上面までの高さ（32mm）

# Existing physical measurements, kept separate from the shared servo profile
BODY_CENTER_X = -0.005  # 軸原点から本体中心までのX距離（-5mm、既存の計測値）
MOUNT_HOLE_SPACING = 0.02884  # 取付穴の中心間ピッチ（28.84mm）
MOUNT_HOLE_DIA = 0.002  # 取付穴の直径（2mm）
MOUNT_SLOT_W = 0.001  # 取付穴から外端へ開く溝の幅（1mm）

# 配線の全幅は写真由来。表示長、1本の太さ、出口高さは仮置き
WIRE_W = 0.004  # 3本配線の全幅（4mm）
WIRE_LENGTH = 0.008  # 配線の表示長さ（8mm、仮置き）
WIRE_T = 0.0016  # 1本の配線直径（1.6mm、仮置き）
WIRE_EXIT_Z = 0.005  # 本体底から配線中心までの高さ（5mm、仮置き）

# Provisional dimensions not visible in the photos
HORN_SOCKET_DIA = 0.0046  # 軸用ソケットの直径（4.6mm、スプライン歯は省略）
HORN_SOCKET_TOP_Z = 0.031  # 本体底から軸用ソケット上端までの高さ（31mm）
CENTER_HOLE_DIA = 0.0024  # センター穴の直径（2.4mm）
ARM_HOLE_DIA = 0.001  # 腕穴の直径（1mm）
ARM_HOLES_X_LEFT = (-0.0165, -0.0145, -0.0125, -0.0105, -0.0085, -0.0065, -0.0045)  # 長腕左側の穴X位置（-16.5〜-4.5mm）
ARM_HOLES_X_RIGHT = (0.005, 0.007, 0.009, 0.011, 0.013, 0.015)  # 長腕右側の穴X位置（5〜15mm）
ARM_HOLES_Y = (-0.0068, -0.0048, 0.0048, 0.0068)  # 短腕の穴Y位置（±4.8mm、±6.8mm）

try:
    from param_override import apply_overrides
    apply_overrides(globals())
except Exception:
    pass
