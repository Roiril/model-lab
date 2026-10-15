"""ゲートの閾値。ハーネスの定数であり、モデル側（spec.json・params.py）から変えられない。

ここを変えるのはハーネスの改修だけ。変えたら `py -3.11 tools/mechgate.py selftest` を流し直す
（selftest が通るまで、ゲートは「ハーネスが未校正」として全モデルを不合格にする）。
値の出どころは .agent/rules/model-request.md と printable-mechanism-design/verification.md。
"""

# 共通体積の床。これを超えたら当たり（lib/printmech/solid_meter.py の校正で固定）
VOLUME_FLOOR_MM3 = 0.001

# 動作の当たりは 2.5° 刻み以下で全範囲を見る（model-request §6）
MOTION_MAX_STEP_DEG = 2.5

# 当たりを測る姿勢の密度。どの部品のどの点も、隣の姿勢との間で 1mm を超えて動かない。
# モデルの書き出した刻みが粗ければ、ゲートがフレームの間を剛体補間して足す（刻みを信じない）
SWEEP_MAX_DISPLACEMENT_MM = 1.0

# 圧入・潰しリブ: 当たってよいのは差し込みの最後の insertion_mm だけ。宣言できる上限
# （C4-3 の板カムは全行程 87mm の擦れを許可して、実物で軸が通らなかった）
PRESS_FIT_MAX_INSERTION_MM = 6.0
# スナップ: ひずみの上限（PLA）と、爪が相手の面に乗り上げて進む距離の上限。最後の姿勢では重なりを残さない。
# 弾性のしなりで擦るだけなので圧入より長く取る。tangible の押さえクリップと案内板の舌は 10〜11mm 乗り上げる（実物未確認）
SNAP_MAX_STRAIN_PERCENT = 2.0
SNAP_MAX_ENGAGE_MM = 12.0
# 組んだ状態で重なったまま固定される嵌合（潰しリブの圧入など）。相対姿勢が全角度で一定であること
STATIC_FIT_MAX_MM3 = 5.0
# 既製部品の正本メッシュどうしの内部の重なり（出力軸とホーンの穴など）
REFERENCE_INTERNAL_MAX_MM3 = 0.5

# 駆動の界面: 従動側を押し戻したとき、この遊びの中で駆動側に当たること（歯車の欠落・離れを捕まえる）
DRIVE_MAX_PLAY_DEG = 5.0
DRIVE_MAX_PLAY_MM = 1.0
DRIVE_SAMPLES = 12

# 抜け止め: 外れる向きに動かしたとき、この距離までに止まること
RETENTION_MAX_FREE_MM = 3.0

# 印刷: 接地
GROUND_TOL_MM = 0.02
MIN_BED_CONTACT_MM2 = 10.0
# 立てて刷る部品の高さ / 接地の短辺（model-request §3「高さを太さの 5 倍以内」）
SLENDER_MAX = 5.0

# トルク: 必要トルクは停動トルクの 1/3 以下（model-request §5）。重力だけの下限の見積もり
TORQUE_MAX_FRACTION = 1.0 / 3.0
PRINT_DENSITY_G_CM3 = 1.24   # PLA。中実で見積もり、上限側に倒す
GRAVITY = 9.81

# スライス結果: 外に見える押し出しで支えの無いものの許容長さ（mm、部品ごと）
SLICE_MAX_EXTERNAL_UNSUPPORTED_MM = 2.0
