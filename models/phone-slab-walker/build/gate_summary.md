# ゲート: phone-slab-walker

- 判定: **合格**（2026-11-06T23:10:45）
- 止めている検査: なし

## 要件

| 要件 | 内容 | 検査 | 結果 | 実物で確かめること |
|---|---|---|---|---|
| R1 | スマホを体にして、左右の脚をモーター 1 個ずつで動かす | motion.interference, motion.torque, interface.coverage, interface.drive | ○ | 実機で歩かせ、30cm を 10 回中 9 回転ばずに進むか |
| R2 | SO-101 の STS3215 を使い、Arduino Leonardo R3 を載せる | assembly.path | ○ | サーボを穴へ入れ、Leonardo から角度と電圧を読めるか |
| R3 | スマホと有線で繋ぎ、電源線か電池で動かす |  | — | USB-C と micro-B のケーブルを足の部屋に収めて閉じられるか; 12V の線を背中の口から通せるか |
| C3 | 共通条件 §3 見える面をサポート無しできれいに刷る | print.slice, print.grounding, print.slender | ○ |  |
| C4 | 共通条件 §4 工具なしで組み、壊さず分解できる（ホーンのねじ 4 本 x 2 だけ例外） | assembly.path, interface.retention | ○ |  |

## 検査

| 検査 | 結果 | 内容 |
|---|---|---|
| harness.calibrated | ○ | selftest を通った版 |
| spec.valid | ○ | 宣言はハーネスの上限の中 |
| contract.files | ○ | そろっている |
| instrument.calibration | ○ | 正負の形がすべて期待どおり |
| parts.topology | ○ | 19 個の STL を検査 |
| parts.components | ○ | 刷る部品 6 点 |
| parts.self_intersection | ○ | 刷る STL 6 点 |
| print.grounding | ○ | 接地 10.0mm² 以上・浮いた成分なし |
| print.slender | ○ | 高さ / 接地の短辺 ≤ 5.0 |
| assembly.envelope | ○ | 組んだ外形 143.4 x 60.0 x 248.4mm（上限 [145, 62, 250]） |
| motion.resolution | ○ | motion.json の最大の刻み 2.500°（37 姿勢） |
| motion.interference | ○ | 13 部品・78 組 x 397 姿勢（-45.0〜45.0°、どの点も姿勢の間で 1.0mm 以内。補間 360） |
| motion.torque | ○ | 重力の必要トルク最大 408.7 mN·m（45.0°）/ 停動 2.94 N·m = 13.9%（摩擦・圧入・ばねは含まない下限の見積もり） |
| interface.coverage | ○ | 動く塊 1 個のうち 1 個がアクチュエータから駆動の界面でつながる |
| interface.drive | ○ | 界面 4 個 |
| interface.retention | ○ | 抜け止め 9 個 |
| assembly.path | ○ | 11 工程（補間で足した姿勢 0） |
| unknowns.resolved | ○ | 未確認 3 件の扱いが決まっている |
| print.slice | ○ | 4 枚・9 物体。外の支えなし押し出し ≤ 2.0mm |

## モデル側が宣言したもの（合格の理由ではない。読む人が確かめる）

- 許可 snap 1 組 {'engage_mm': 11.6, 'strain_percent': 0.6, 'deflection_mm': 1.0}: 足のふたの腕 t=2.5、L≈31、たわみ 1.0mm。ε=1.5·t·δ/L²≈0.4%。爪の上の斜面がトレイの下端からトレイ内壁を押して進み、窓で戻る
- 未確認 sts3215.horn_screw: trial_part = prints/phone-slab-walker/trial/horn_seat.stl
- 未確認 sts3215.connector: trial_part = prints/phone-slab-walker/trial/servo_pocket.stl
- 未確認 sts3215.pocket_fit: trial_part = prints/phone-slab-walker/trial/servo_pocket.stl
