# ゲート: mystery-box-sg92r-f1/checks/top

- 判定: **不合格**（2026-10-15T23:20:35）
- 止めている検査: print.slice

## 要件

| 要件 | 内容 | 検査 | 結果 | 実物で確かめること |
|---|---|---|---|---|
| R1 | 閉状態の外形は100 × 100 × 100mm | assembly.envelope | ○ |  |
| R2 | 正面の蓋・上面の3画素・右面の旗を各SG92Rで動かし、背面・左面・底面を空の面とする | interface.coverage, interface.drive, motion.torque | ○ |  |
| R3 | 他面を変更せずキーを解除して40mm以上直線で引き抜く | assembly.path, interface.retention | ○ | 他面を残して配線を切り離し交換する |
| R4 | 動作中もサーボと伝達部品を外から見せない |  | — | 閉端・中間・開端を斜め方向から見て遮蔽を確認 |
| R5 | 印刷部品とSG92R・付属ホーンだけで工具なしに組み分解する | assembly.path, interface.retention | ○ | 工具なしで組立と分解 |
| R6 | 外装2mm・荷重部3mm以上でサポートなしに見える面を刷る | print.slice, print.grounding, print.slender, parts.topology | × |  |
| R7 | 全動作と交換経路で干渉しない。製造余裕0.25mmを含む占有領域を検査する | motion.interference, assembly.path | ○ | verify_envelopes.pyの未証明範囲を確認 |
| R8 | 既製部品の仮値は本体形状から作る試片で扱う | unknowns.resolved | ○ | 実物適合と20回着脱を記録 |
| R9 | 新しい面は独立したfacesディレクトリとslots.jsonで追加する |  | — | verify_contract.pyで規格と依存鮮度を検査 |
| front/lid-motion | C節の4節リンクで36×30×2mmの蓋を0〜60度開く | motion.interference, motion.torque, interface.drive | ○ |  |
| front/lid-assembly | 90度で組み、閉姿勢へ戻す。工具とねじなしで分解 | assembly.path, interface.retention | ○ | 実物で両ピンの先端と解除腕を押して外す |
| front/lid-shield | 開いた蓋の奥を無地の壁で遮る |  | — | 0度・30度・60度を正面と斜めから見る |
| right/flag-motion | 14×28×2mmの旗をm1.5・18歯相当・軸間27mmの歯車で0〜60度起こす | motion.interference, motion.torque, interface.drive | ○ |  |
| right/flag-envelope | 公差片側0.25mm込みで7段の占有と外部76×76×32mmを守る | assembly.envelope | ○ | check_local.pyの全角度の占有結果を合成担当が確認 |
| right/flag-assembly | 90度で組み閉姿勢へ戻す。工具・ねじ・接着剤なしで分解できる | assembly.path, interface.retention | ○ | 爪を指で解除して20回着脱 |
| right/flag-shield | 旗が面一に閉じ、固定壁と重なったカラーで歯車・サーボ・ホーン・内部キー・ピンを隠す |  | — | check_shield.pyの既定585225本と追加31851655本が0件。実物も正面と斜めから確認 |
| right/flag-print | 見える面にサポートを付けずPLAとPETGで刷れる | print.slice, print.grounding, print.slender | × |  |
| back/blank-closed | 空の面を3点の座へ固定し、キーを外して面法線方向へ抜ける | assembly.path, interface.retention | ○ |  |
| left/blank-closed | 空の面を3点の座へ固定し、キーを外して面法線方向へ抜ける | assembly.path, interface.retention | ○ |  |
| top/pixels-table | patterns.jsonから53mmの上下カムを作り、14mm角の3画素を0〜3mm押し引きする | motion.interference, interface.drive, motion.torque | ○ |  |
| top/pixels-fit | 7段の占有と外部動作域を守り、側面でも重力に頼らず動く | assembly.envelope, interface.retention | ○ | 実機を上向きと横向きで動かす |
| top/pixels-assembly | サーボ90度で組み、印刷部品と付属ホーンだけで保持する | assembly.path, interface.retention | ○ | 工具なしで組立と取り外し |
| top/pixels-shield | 8mmのスカートで画素穴の奥を隠す |  | — | 0mmと3mmで斜めから内部が見えないこと |
| bottom/blank-closed | 空の面を3点の座へ固定し、キーを外して面法線方向へ抜ける | assembly.path, interface.retention | ○ |  |

## 検査

| 検査 | 結果 | 内容 |
|---|---|---|
| harness.calibrated | ○ | selftest を通った版 |
| spec.valid | ○ | 宣言はハーネスの上限の中 |
| contract.files | ○ | そろっている |
| instrument.calibration | ○ | 正負の形がすべて期待どおり |
| parts.topology | ○ | 114 個の STL を検査 |
| parts.components | ○ | 刷る部品 54 点 |
| parts.self_intersection | ○ | 刷る STL 54 点 |
| print.grounding | ○ | 接地 10.0mm² 以上・浮いた成分なし |
| print.slender | ○ | 高さ / 接地の短辺 ≤ 5.0 |
| assembly.envelope | ○ | 組んだ外形 100.0 x 100.0 x 100.0mm（上限 [100, 100, 100]） |
| motion.resolution | ○ | motion.json の最大の刻み 1.000°（61 姿勢） |
| motion.interference | ○ | 60 部品・1770 組 x 61 姿勢（60.0〜120.0°、どの点も姿勢の間で 1.0mm 以内。補間 0） |
| motion.torque | ○ | 重力の必要トルク最大 0.4 mN·m（105.0°）/ 停動 0.245 N·m = 0.2%（摩擦・圧入・ばねは含まない下限の見積もり） |
| interface.coverage | ○ | 動く塊 4 個のうち 4 個がアクチュエータから駆動の界面でつながる |
| interface.drive | ○ | 界面 9 個 |
| interface.retention | ○ | 抜け止め 91 個 |
| assembly.path | ○ | 120 工程（補間で足した姿勢 0） |
| unknowns.resolved | ○ | 未確認 7 件の扱いが決まっている |
| print.slice | × | 5 枚・66 物体。外の支えなし押し出し ≤ 2.0mm、41 件超過 |

## モデル側が宣言したもの（合格の理由ではない。読む人が確かめる）

- 許可 reference_internal 1 組 {'max_mm3': 0.05}: 正本の円筒近似スプライン同士のみ。印刷部品には適用しない。
- 許可 snap 1 組 {'engage_mm': 4.5, 'deflection_mm': 0.15, 'strain_percent': 1.563}: Aピンは頭半径2.85/穴半径2.7。座金の先からの自由長4.8mm・片脚t1.6mm以下・δ0.15mm。1.5tδ/L²=1.563%。
- 許可 snap 1 組 {'engage_mm': 4.5, 'deflection_mm': 0.15, 'strain_percent': 1.778}: Bピン先端半径2.85/穴半径2.7、δ0.15mm。自由長4.5mm・t1.6mm、1.5tδ/L²=1.778%。実物の着脱で確認。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.444}: 支持座の解除腕自由長18mm以上・t1.6mm・δ0.6mm、上限1.5tδ/L²=0.444%。終端に重なりを残さない。
- 許可 reference_internal 1 組 {'max_mm3': 0.05}: SG92R正本の円筒近似した軸とソケットだけ。印刷部品の干渉には適用しない。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.454489}: 面板を留める腕の自由長L17.8mm・t1.6mm。δ0.6mm。外面の窓から解除。
- 許可 reference_internal 1 組 {'max_mm3': 0.05}: 正本の円筒近似スプラインのみ。印刷部品への除外はない。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.444}: 自由長18mm、厚さ1.6mm、片側0.6mm。1.5tδ/L²。
- 許可 snap 1 組 {'engage_mm': 4.5, 'deflection_mm': 5, 'strain_percent': 1.94}: 右腕は自由長22mm・厚さ1.2mm・先端5mm。中心線の長さを保った曲げで最大ひずみ1.938%以下。左腕は17.5mm・1.6mm・0.6mmで0.471%以下。着座まで指で開いて保持し、着座後に戻す。実形状を曲げた通過検査はcheck_localのelastic_cap。
- 許可 snap 2 組 {'engage_mm': 4.5, 'deflection_mm': 0.15, 'strain_percent': 0.67}: 二股脚厚1.2mm、自由長6.35mm、片側0.15mm。1.5tδ/L²。
- 許可 snap 1 組 {'engage_mm': 9, 'deflection_mm': 5, 'strain_percent': 1.94}: 右腕は自由長22mm・厚さ1.2mm・先端5mm。中心線の長さを保った曲げで最大ひずみ1.938%以下。左腕は17.5mm・1.6mm・0.6mmで0.471%以下。着座まで指で開いて保持し、着座後に戻す。実形状を曲げた通過検査はcheck_localのelastic_cap。
- 許可 snap 2 組 {'engage_mm': 11, 'deflection_mm': 0.15, 'strain_percent': 0.67}: 下カムを留める二股の爪が上カムの四角穴を通る間も片側0.15mm縮む。自由長6.35mm、厚さ1.2mm。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'region_mm': [[-46.7, -48.0, -47.1], [-43.5, -42.0, -43.9]], 'step': 'frame/insert-post_0'}: 自由長18mm、厚1.6mm、解除0.6mm。角の爪だけ。完成姿勢に重なりを残さない。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'region_mm': [[-46.7, -48.0, 43.9], [-43.5, -42.0, 47.1]], 'step': 'frame/upper-frame'}: 自由長18mm、厚1.6mm、解除0.6mm。角の爪だけ。完成姿勢に重なりを残さない。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'region_mm': [[43.5, -48.0, -47.1], [46.7, -42.0, -43.9]], 'step': 'frame/insert-post_1'}: 自由長18mm、厚1.6mm、解除0.6mm。角の爪だけ。完成姿勢に重なりを残さない。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'region_mm': [[43.5, -48.0, 43.9], [46.7, -42.0, 47.1]], 'step': 'frame/upper-frame'}: 自由長18mm、厚1.6mm、解除0.6mm。角の爪だけ。完成姿勢に重なりを残さない。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'region_mm': [[43.5, 42.0, -47.1], [46.7, 48.0, -43.9]], 'step': 'frame/insert-post_2'}: 自由長18mm、厚1.6mm、解除0.6mm。角の爪だけ。完成姿勢に重なりを残さない。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'region_mm': [[43.5, 42.0, 43.9], [46.7, 48.0, 47.1]], 'step': 'frame/upper-frame'}: 自由長18mm、厚1.6mm、解除0.6mm。角の爪だけ。完成姿勢に重なりを残さない。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'region_mm': [[-46.7, 42.0, -47.1], [-43.5, 48.0, -43.9]], 'step': 'frame/insert-post_3'}: 自由長18mm、厚1.6mm、解除0.6mm。角の爪だけ。完成姿勢に重なりを残さない。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'region_mm': [[-46.7, 42.0, 43.9], [-43.5, 48.0, 47.1]], 'step': 'frame/upper-frame'}: 自由長18mm、厚1.6mm、解除0.6mm。角の爪だけ。完成姿勢に重なりを残さない。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'front/key_l_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'front/exchange_key_0_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'front/key_r_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'front/exchange_key_1_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'right/key_l_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'right/exchange_key_0_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'right/key_r_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'right/exchange_key_1_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'back/key_l_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'back/exchange_key_0_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'back/key_r_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'back/exchange_key_1_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'left/key_l_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'left/exchange_key_0_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'left/key_r_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'left/exchange_key_1_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'top/key_l_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'top/exchange_key_0_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'top/key_r_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'top/exchange_key_1_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'bottom/key_l_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'bottom/exchange_key_0_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'bottom/key_r_lock'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 許可 snap 1 組 {'engage_mm': 2.4, 'deflection_mm': 0.6, 'strain_percent': 0.4444444444, 'step': 'bottom/exchange_key_1_in'}: 規格のキー先端だけ。L18mm・t1.6mm・δ0.6mm、ε=1.5tδ/L²=0.444%。完成姿勢に重なりなし。
- 未確認 sg92r.horn_arm_lengths: trial_part = prints/mystery-box-sg92r-f1/trial/front/horn_fit.stl
- 未確認 sg92r.horn_hole_positions: not_applicable = ホーンの既存穴は使わない。
- 未確認 sg92r.output_spline: not_applicable = 実物の付属ホーンを使い、印刷スプラインは作らない。
- 未確認 sg92r.shaft_height: trial_part = prints/mystery-box-sg92r-f1/trial/front/horn_fit.stl
- 未確認 sg92r.cover_circle: trial_part = prints/mystery-box-sg92r-f1/trial/front/servo_fit.stl
- 未確認 sg92r.wire: trial_part = prints/mystery-box-sg92r-f1/trial/front/servo_fit.stl
- 未確認 sg92r.connector: trial_part = prints/mystery-box-sg92r-f1/trial/front/connector_nest.stl
