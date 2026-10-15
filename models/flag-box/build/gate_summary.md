# ゲート: flag-box

- 判定: **合格**（2026-10-15T11:30:22）
- 止めている検査: なし

## 要件

| 要件 | 内容 | 検査 | 結果 | 実物で確かめること |
|---|---|---|---|---|
| R1 | ① 閉じた外形70mm以下の立方体。SG92R1台で旗0〜90度。 | motion.interference, interface.drive, assembly.envelope, motion.torque | ○ | 実機でソフトの角度端点を合わせる |
| R2 | ④⑤ 工具とねじを使わず組めて動き、分解できる。 | assembly.path, interface.retention, instrument.calibration | ○ | 爪を指で押し3回着脱する。摩擦と破損を確かめる |
| C3 | ②⑥ PLA。X1C用gcode.3mf。見える面をサポート無しできれいに刷る。外装3mm。 | print.slice, print.grounding, print.slender | ○ |  |
| C4 | ③ SG92Rとホーンの正本をimport。配線は上開き窓へ置く。 | assembly.path, unknowns.resolved | ○ | 試し刷りで個体差と配線経路を確認する |

## 検査

| 検査 | 結果 | 内容 |
|---|---|---|
| harness.calibrated | ○ | selftest を通った版 |
| spec.valid | ○ | 宣言はハーネスの上限の中 |
| contract.files | ○ | そろっている |
| instrument.calibration | ○ | 正負の形がすべて期待どおり |
| parts.topology | ○ | 14 個の STL を検査 |
| parts.components | ○ | 刷る部品 6 点 |
| parts.self_intersection | ○ | 刷る STL 6 点 |
| print.grounding | ○ | 接地 10.0mm² 以上・浮いた成分なし |
| print.slender | ○ | 高さ / 接地の短辺 ≤ 5.0 |
| assembly.envelope | ○ | 組んだ外形 68.0 x 68.0 x 68.0mm（上限 [70, 70, 70]） |
| motion.resolution | ○ | motion.json の最大の刻み 1.000°（91 姿勢） |
| motion.interference | ○ | 8 部品・28 組 x 91 姿勢（45.0〜135.0°、どの点も姿勢の間で 1.0mm 以内。補間 0） |
| motion.torque | ○ | 重力の必要トルク最大 0.3 mN·m（45.0°）/ 停動 0.245 N·m = 0.1%（摩擦・圧入・ばねは含まない下限の見積もり） |
| interface.coverage | ○ | 動く塊 1 個のうち 1 個がアクチュエータから駆動の界面でつながる |
| interface.drive | ○ | 界面 2 個 |
| interface.retention | ○ | 抜け止め 6 個 |
| assembly.path | ○ | 9 工程（補間で足した姿勢 0） |
| unknowns.resolved | ○ | 未確認 7 件の扱いが決まっている |
| print.slice | ○ | 1 枚・6 物体。外の支えなし押し出し ≤ 2.0mm |

## モデル側が宣言したもの（合格の理由ではない。読む人が確かめる）

- 許可 reference_internal 1 組 {'max_mm3': 0.05}: 正本どうしの同軸嵌合。円筒近似のスプラインとソケットは同径。浮動小数点メッシュの共通体積最大0.029983mm3。印刷部品には適用しない。
- 許可 snap 2 組 {'engage_mm': 6, 'deflection_mm': 0.3, 'strain_percent': 1.6333}: 別刷りの留め具だけ。L5.75mm、t1.2mm、δ0.3mm。ε=1.5tδ/L²=1.6333%。層内で曲がる向きに寝かせて刷る。最後に重なりを残さない。
- 未確認 sg92r.horn_arm_lengths: trial_part = prints/flag-box/horn-fit-trial.stl
- 未確認 sg92r.horn_hole_positions: not_applicable = ホーンの穴を使わず腕の外形で駆動する。
- 未確認 sg92r.output_spline: not_applicable = 付属ホーンを実物のスプラインへ付ける。印刷で歯を作らない。
- 未確認 sg92r.shaft_height: trial_part = prints/flag-box/horn-fit-trial.stl
- 未確認 sg92r.cover_circle: trial_part = prints/flag-box/servo-fit-trial.stl
- 未確認 sg92r.wire: accepted_risk = 出口高さは仮値。上開き14mm幅の切欠きを設ける。線の経路は実物で確認する。
- 未確認 sg92r.connector: not_applicable = コネクタを閉じた穴に通さない。天板を外して線だけを上開き切欠きへ置く。
