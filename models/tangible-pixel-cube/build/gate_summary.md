# ゲート: tangible-pixel-cube

- 判定: **合格**（2026-10-17T15:45:30）
- 止めている検査: なし

## 要件

| 要件 | 内容 | 検査 | 結果 | 実物で確かめること |
|---|---|---|---|---|
| R0 | SG92R 1 台で、外から見て一辺 10cm 以下の立方体 | assembly.envelope, motion.torque | ○ |  |
| R0b | 天面の小さな正方形が、後から表で決めた形にボコボコ動く | motion.interference, interface.coverage, interface.drive | ○ | 実機でサーボを回し、表どおりの高さになるか |
| R1 | 見える面にサポートなしできれいに刷れる | print.grounding, print.slender, parts.components, parts.self_intersection | ○ | 見える面の仕上がり |
| R2 | SG92R の寸法は models/sg92r-photo を使う | unknowns.resolved | ○ |  |
| R3 | 組立は印刷部品だけ（工具・ねじ・接着なし） | assembly.path, interface.retention | ○ | 潰しリブとスナップを手で押し込めるか |
| R4 | PLA/PETG で薄いと揺れる。スライスは不要 | parts.topology | ○ | 立てて刷る薄い部品が揺れないか |
| R5 | 物理検証と組立検証 | motion.interference, assembly.path, interface.drive | ○ |  |

## 検査

| 検査 | 結果 | 内容 |
|---|---|---|
| harness.calibrated | ○ | selftest を通った版 |
| spec.valid | ○ | 宣言はハーネスの上限の中 |
| contract.files | ○ | そろっている |
| instrument.calibration | ○ | 正負の形がすべて期待どおり |
| parts.topology | ○ | 90 個の STL を検査（既製部品の正本 1 個に面積 0 の三角形。閉じているので計器には使える） |
| parts.components | ○ | 刷る部品 44 点 |
| parts.self_intersection | ○ | 刷る STL 44 点 |
| print.grounding | ○ | 接地 10.0mm² 以上・浮いた成分なし |
| print.slender | ○ | 高さ / 接地の短辺 ≤ 5.0 |
| assembly.envelope | ○ | 組んだ外形 96.0 x 96.0 x 96.0mm（上限 [100, 100, 100]） |
| motion.resolution | ○ | motion.json の最大の刻み 1.000°（161 姿勢） |
| motion.interference | ○ | 45 部品・990 組 x 161 姿勢（10.0〜170.0°、どの点も姿勢の間で 1.0mm 以内。補間 0） |
| motion.torque | ○ | 重力の必要トルク最大 7.9 mN·m（97.0°）/ 停動 0.245 N·m = 3.2%（摩擦・圧入・ばねは含まない下限の見積もり） |
| interface.coverage | ○ | 動く塊 31 個のうち 31 個がアクチュエータから駆動の界面でつながる |
| interface.drive | ○ | 界面 31 個 |
| interface.retention | ○ | 抜け止め 12 個 |
| assembly.path | ○ | 17 工程（補間で足した姿勢 0） |
| unknowns.resolved | ○ | 未確認 7 件の扱いが決まっている |
| print.slice | 外した: 依頼 ④「スライスは不要」 | prints/tangible-pixel-cube/ にスライス済みの 3mf が無い |

## モデル側が宣言したもの（合格の理由ではない。読む人が確かめる）

- 外した検査 print.slice: 依頼 ④「スライスは不要」
- 許可 press_fit 5 組 {'insertion_mm': 1.5}: 継ぎ目の雌穴の潰しリブ 3 本（潰し 0.18mm）。当たるのは差し込みの最後の 1.5mm だけ（gear_hole(): リブ長さ 1.5）
- 許可 static_fit 5 組 {'max_mm3': 0.4}: 組んだ後も潰しリブ 3 本が重なったまま残る。1 本 = 幅 0.6 x（傾き部分 0.5 x 0.18^2 + 平ら部分 0.18 x 1.12）で合計 0.392mm3（verify_report の理論値 0.392、許容 0.353〜0.400）
- 許可 press_fit 2 組 {'insertion_mm': 2.0}: 押さえ棒の Y 端のリブ（各端 2 本、高さ 0.25、食い込み 0.05）が外装の Y 止めの面を擦る。擦るのは差し込みの最後の 2.0mm だけ（assembly_report の allowedInsertionWindowMm 2.0）
- 許可 static_fit 2 組 {'max_mm3': 0.15}: 組んだ後も押さえ棒の Y 端のリブが重なったまま残る。理論値 0.120mm3（各端 2 本、食い込み 0.05）、許容 0.096〜0.154
- 許可 snap 1 組 {'engage_mm': 12.0, 'strain_percent': 1.606, 'deflection_mm': 0.15}: 押さえ棒の爪（出っ張り 0.45）が外装の面に乗り上げて腕（長さ 4.1、厚さ 1.2）がしなる。しなり 0.15mm、梁の見積り 3tδ/(2L^2) でひずみ 1.606%（assembly_report capSnap）
- 許可 snap 1 組 {'engage_mm': 12.0, 'strain_percent': 1.531, 'deflection_mm': 0.15}: 押さえ棒の爪（出っ張り 0.45）が外装の面に乗り上げて腕（長さ 4.2、厚さ 1.2）がしなる。しなり 0.15mm、梁の見積り 3tδ/(2L^2) でひずみ 1.531%（assembly_report capSnap）
- 許可 snap 1 組 {'engage_mm': 10.5, 'strain_percent': 0.362, 'deflection_mm': 0.3}: 押さえクリップの脚が爪の分だけしなって受けの側面を通る。爪が相手の面に乗り上げて進む距離 10.5mm（ゲートの実測 5.4〜10.8mm から）
- 許可 snap 1 組 {'engage_mm': 10.5, 'strain_percent': 0.362, 'deflection_mm': 0.3}: 押さえクリップの脚が爪の分だけしなって受けの側面を通る。爪が相手の面に乗り上げて進む距離 10.5mm（ゲートの実測 5.4〜10.8mm から）
- 許可 snap 1 組 {'engage_mm': 11.0, 'strain_percent': 0.997, 'deflection_mm': 0.4}: 案内板の舌の爪が端壁の内面を押して、舌が面内にしなる。爪が相手の面に乗り上げて進む距離 11.0mm（ゲートの実測 5.4〜10.8mm から）
- 許可 snap 1 組 {'engage_mm': 6.0, 'strain_percent': 1.709, 'deflection_mm': 0.35}: ベゼルの爪が端壁の内面を押して壁がたわむ（片持ち梁の最悪見積り）。爪が相手の面に乗り上げて進む距離 6.0mm（ゲートの実測 5.4〜10.8mm から）
- 許可 reference_internal 1 組 {'max_mm3': 0.05}: 正本 SG92R の出力軸（径 4.6）とホーン穴は 64 角形どうしで頂点が辺へ入る。スプライン歯は正本に無い
- 未確認 sg92r.horn_arm_lengths: trial_part = prints/tangible-pixel-cube/trial/horn_coupler.stl
- 未確認 sg92r.horn_hole_positions: not_applicable = 受けのポケットはホーンの腕の外形で回す。穴の位置に依存しない
- 未確認 sg92r.output_spline: not_applicable = 付属ホーンを付属のまま使い、スプラインに印刷部品が触れない
- 未確認 sg92r.shaft_height: trial_part = prints/tangible-pixel-cube/trial/horn_coupler.stl
- 未確認 sg92r.cover_circle: trial_part = prints/tangible-pixel-cube/trial/housing_servo_block_minusY.stl
- 未確認 sg92r.wire: accepted_risk = 配線は柔らかく、窓 11 x 7mm に対して 4mm 幅。試し刷りの小片に窓は無い
- 未確認 sg92r.connector: accepted_risk = 試し刷りの小片に配線の窓が無い。初版の窓は実物で通らず 11 x 7mm に広げた（e8b4c65）。広げた窓も実物では未確認
- 動作の検査から除いた部品 phase_comb: 組立の途中だけに置く位相合わせの治具。動作の前に外す（assembly の phase-comb-remove）
