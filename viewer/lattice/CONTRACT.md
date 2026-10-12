# viewer/lattice の入力契約

物理検証・組み立てのページ（`viewer/lattice/index.html?model=<名前>&mode=physics|assembly`）に載せるモデルが用意するもの。
ページのコードにモデル名は無い。**`models/<名前>/build/` に下のファイルを置き、書き出しを 1 回流せば載る。**

```
py -3.11 tools/lattice_web.py <名前>
```

- 出力: `viewer/lattice/assets/<名前>.json`（表示データ）と `assets/index.json`（旧 3 モデル以外のモデル切り替えの一覧）
- 必須ファイルが 1 つでも無ければ何も書かずに終了コード 2。形の問題（下の必須キー・ui 節）は全部まとめて日本語で出す
- Studio のタブに出すには `viewer/shared/workspace.mjs` の `WORKSPACE_PAGES` へ登録する（物理 `/viewer/lattice/index.html?mode=physics`、組み立て `...?mode=assembly`）
- ⚠ 触らない: `viewer/lattice/sim.mjs` と `tools/lattice_simulation.py`（C4-2 が SHA を記録しており `c42-sim.test.mjs` が見張っている）

## 1. 単位と座標

| 量 | 単位 |
|---|---|
| STL・行列の並進・`liftsMm` | mm。Z が上。 |
| サーボ角（`servo_deg` / `servoDeg` / `limitsDeg`） | 度 |
| 行列 | 長さ 16 の配列。4×4 の列優先（要素 12,13,14 が並進 X,Y,Z）。剛体のみ（拡大縮小は不可） |
| `massKg` / `Kgm2` / `Nm` / `*MPerRad` | kg / kg·m² / N·m / m·rad⁻¹ |
| 時間 | 秒 |

## 2. build/ の必須ファイル

| ファイル | 内容 |
|---|---|
| `manifest.json` | 部品表。下の表 |
| `motion.json` | サーボ角から全部品の姿勢を引く表 |
| `sim_tables.json` | 物理計算の入力表（`sim.mjs` の `createSim` がそのまま読む） |
| `simulate_report.json` | 計算結果の合否 |
| `drive_report.json` | 駆動接続（歯車・嵌合）の形状検査 |
| `assembly.json` | 組み立て工程と経路 |
| `boolean_evidence.json` | 体積計算の根拠。中身は読まず、そのまま表示データへ入れる（`{}` でも可） |
| 各部品の組立 STL | `manifest.parts[].assembly` のパス（`fit_only` の部品は不要） |

任意（あれば表示する。無ければ画面の該当行が「記録なし」）: `verify_report.json` `delivery_report.json` `print_path_review.json` `print_path_evidence.json` `hole_clearance.json` `closed_loop_support_evidence.json` `print_support_geometry.json` `continuous_path_support_evidence.json` `first_layer_contact_evidence.json` `ui.json`（4 章）。

### manifest.json

```
{ "meta": {...}, "parts": [ {...} ] }
```

| キー | 型 | 必須 | 意味 |
|---|---|---|---|
| `parts[].id` | string | ○ | 部品 id。`motion` / `assembly` の `transforms` のキーと一致させる |
| `parts[].assembly` | string | ○ | 組立姿勢の STL（binary）。モデル直下からの相対パス（`build/xxx.stl`）。mm |
| `parts[].label` | string |  | 凡例の名前（無ければ id） |
| `parts[].print` | string |  | 印刷用 STL。あれば「印刷 N 点」に数える |
| `parts[].color` | `#rrggbb` |  | 既定の色（4 章の `colors` / `legendGroups` が優先） |
| `parts[].exterior` | bool |  | true なら「箱の右半分を隠す」で切る外装。無ければ `meta.exterior_parts` か、id に box/body/bottom/shell/facade/wall/case/housing/enclosure/roof/frame/base を含むか（`servo_` `ref_` 始まりは除く） |
| `parts[].fit_only` | bool |  | true なら表示から除く |
| `meta.dimensions_mm` | `[w,d,h]` |  | ヘッダの外形寸法。無ければ ui の `dimensionsFallback` |
| `meta.exterior_parts` | string[] |  | 外装の id 一覧 |
| `meta.description` `decisions` `limitations` | |  | そのまま表示データに載る |

### motion.json（物理検証の姿勢。`motion-frames` 再生はこれだけで全部品を動かす）

| キー | 型 | 必須 | 意味 |
|---|---|---|---|
| `frames[]` | array | ○ | `{ "servo_deg": number, "transforms": { "<id>": matrix16 } }`。`servo_deg` は昇順（書き出し側が並べ直す）。範囲は `sim_tables.limitsDeg` 以上をカバーする |
| `home_servo_deg` | number |  | 基準角（回転の 0°）。表示では使わない |
| `duration_s` `easing` | |  | 記録用 |
| `patterns[]` | `{id, label, servo_deg}` |  | あれば「凹む場所」のボタンが出る。ボタンはその角へ動かす |

- 隣り合う `frames` の間は剛体補間（X 軸・Z 軸まわり、およびそれ以外の任意の軸まわりの回転 + 並進）。回転の途中で部品が縮まない。1° 刻みでも 10° 刻みでもよいが、**途中で軸方向の並進が非線形に変わる部品は刻みを細かくする**
- `transforms` に無い部品は単位行列（動かない）として描く
- 画素のように上下する部品は、Z 並進（要素 14）を `frames` に直接書く

### sim_tables.json

| キー | 型 | 必須 | 意味 |
|---|---|---|---|
| `limitsDeg` | `[low, high]` | ○ | サーボの可動範囲。`rows[0].servoDeg` と `low` が一致 |
| `duration_s` | number | ○ | 「ゆっくり」の所要時間 |
| `groups[]` | `{id, label, massKg}` | ○ | 追従して動く部品の群。`liftsMm` などの配列はこの順 |
| `rows[]` | array（2 行以上） | ○ | `servoDeg` が**一定刻み**で増える。キーは下 |
| `const` | object | ○ | `stallTorqueNm noLoadSpeedRadS controlBandRad motorInertiaKgm2 servoFrictionNm gravityMS2 dtS recordS settleS contactToleranceN` |
| `contactModel` | string |  | `"gravity_one_sided"` なら常に接触扱い。それ以外は `liftsMm > 1e-7` で接触 |
| `contactBoundariesDeg` | array |  | 接触の切り替わり角（衝撃速度の見積もり用）。無ければ `[]` |

`rows[]` のキー。数値: `servoDeg` `inertiaRestKgm2` `inertiaGroupsKgm2` `dMGroupsDqKgm2PerRad` `gravityRestNm` `gravityGroupsNm`、任意で `contactFrictionGroupsNm`。**`groups` と同じ長さの配列**: `liftsMm`（群ごとの高さ。mm。凹みは負）`dLiftDqMPerRad` `d2LiftDq2MPerRad2`。

### simulate_report.json / drive_report.json（物理検証が有効になる条件）

次が**すべて**満たされると計算が走る。1 つでも崩れると「接続未成立」を出して計算しない。

| 場所 | 条件 |
|---|---|
| `drive_report.overall.geometryPass` | `true` |
| `simulate_report.driveGeometry.geometryPass` / `.sourceHashesFresh` | ともに `true` |
| `drive_report.interfaces[]` | 1 件以上。各 `{id, label, status}` の `status` が `"pass"` か `"unknown"` |
| `simulate_report.overall.calculationPass` | `true` |

`drive_report.interfaces[]` の `status` が `"fail"` なら接続未成立。任意で `drive_report.calibration[]`（`{id,label,pass,detail}`）、`hardwareUnknown`（string[]）、`simulate_report.calibration`（`{id,label,pass,detail}` の配列、または id をキーにしたオブジェクト）、`simulate_report.clearanceEnvelope` を読む。

### assembly.json

| キー | 型 | 必須 | 意味 |
|---|---|---|---|
| `steps[]` | array（1 件以上） | ○ | 工程。下の表 |
| `pass` | bool | ○ | 全工程の判定 |
| `calibration` | `{pass or ok: bool}` | ○ | 検査器の校正。無いと「判定は未確認」になる |

`steps[]`: `title`（string）、`instruction`（string）、`checkText`（string）、`moving`（string[]・動く部品 id。凡例の強調に使う）、`frames`（`{ "progress": 0〜1 昇順, "transforms": { id: matrix16 } }` の配列）、`report.samples`（number・検査した姿勢の数）。`installed`（string[]）は任意。

- **その工程の `frames` の `transforms` に載っている部品だけが描かれる**（据え済みの部品も毎工程 `transforms` に入れる）
- 補間は motion と同じ剛体補間（任意軸の回転に対応）。再生は 1 工程 1.8 秒の quintic

## 3. 出力される表示データ（assets/<名前>.json）

`model` `meta` `parts[]`（`mesh: {vertices, triangles}` 付き）`motion` `simTables` `sim` `assembly` `drive` `verify` `delivery` `boolean_evidence` ほか任意の報告、そして `ui`。`meta.assembly_steps` は工程の `instruction` 一覧に書き換えられる。

## 4. ui 節（モデルごとの見せ方）

`models/<名前>/build/ui.json`（任意）に書くと、書き出し時に表示データの `ui` へ入る。書かないキーは既定値。C3 / C4-1 / C4-2 の表示データには ui 節を足さない（過去モデルの監査が表示データのバイト一致を見るため）。この 3 つの見せ方は `ui-config.mjs` の `LEGACY_UI` がモデル名から引く。`build/ui.json` はこの 3 つでは無視される。

```
{
  "label": "TPC",                       // 短い名前。無ければモデル名
  "displayName": "触れる画素の立方体",  // ヘッダとタブの題。無ければ label
  "navLabel": "TPC 画素の立方体",       // モデル切り替えのリンク。無ければ label
  "navOrder": 40,                       // 切り替えの並び（小さい順）。既定 100
  "dimensionsFallback": "…",            // meta.dimensions_mm が無いときの寸法表示
  "physics": {
    "title": "画素の上下",              // 物理検証の見出し。無ければ displayName
    "playback": "motion-frames",        // "group-lift"（既定）か "motion-frames"
    "term": "画素",                     // 動く部品の呼び名。「〇〇の重さ」「〇〇の操作」等に入る。既定「可動部」
    "chartSeries": ["pixel_0_0", "pixel_2_2", "pixel_4_4"],   // 折れ線に出す群の id（sim_tables.groups の id）。1〜5 個
    "openLabel": "進める",              // 「進める」ボタン。無ければ patterns があれば「次の場所へ」、無ければ「波を進める」
    "closeLabel": "戻す",
    "liftLabel": "…", "chartLabel": "…", "chartAxis": "…",   // 数値欄・折れ線の題・縦軸。無ければ term から作る
    "patternNote": "…",                 // 「凹む場所」の注記を置き換える
    "simLimits": "…"                    // 「確認範囲」の文章を置き換える。新モデルは自分の仮定を書くこと
  },
  "assembly": {
    "servoSetup": "…",                  // 「サーボの角度を決める」の説明
    "maxTranslationMm": 1, "maxRotationDeg": 1   // 干渉検査の許容。無ければ文を出さない
  },
  "print": { "downloadBase": "prints" },   // 印刷データの置き場。"prints"（/prints/<モデル>/）か "exports"（/exports/）。既定 prints
  "legendGroups": [                     // 凡例を束ねる（任意）。部品は最初に載った群へ入る。残りは 1 部品ずつ
    { "label": "画素", "prefix": "pixel_", "color": "#e69f00" },     // prefix か parts（id の配列）
    { "label": "カム軸", "parts": ["camshaft_0", "camshaft_1"] }
  ],
  "colors": { "body": "#cccccc" }       // 部品 id → 色。legendGroups の color より優先
}
```

### 再生の仕方（`physics.playback`）

| 値 | 動かし方 | 使うモデル |
|---|---|---|
| `group-lift` | サーボ角で `motion.frames` を補間し、さらに `groups` の部品の Z を計算した `liftsMm` に置き換える | C3 / C4-1 / C4-2 |
| `motion-frames` | サーボ角で `motion.frames` を補間するだけ。**全部品が `frames` のとおり動く**（Z の置き換えなし） | 画素・歯車・軸を持つ新モデル |

どちらも、再生の時刻はシミュレーション（`createSim`）の結果で、各瞬間のサーボ角が姿勢を決める。折れ線・凡例・「格子の上昇」欄に出すのは `chartSeries` の群だけ（指定が無ければ全群。その場合 `groups` が 6 個以上だとエラー）。

`motion-frames` では折れ線の高さ（`liftsMm`）と画面の部品の高さ（`frames` の Z）は別のデータ。**同じ値になるよう作る**（食い違いは画面では見えない）。

### 組み立て

工程再生は `assembly.json` だけで動く（`ui` に再生方式は無い）。66 部品でも同じ。

## 5. 書き出し時の検査

`tools/lattice_web.py` が止める条件（すべて日本語で列挙）: 必須ファイル欠落 / `motion.frames` の行列が 16 要素でない / `sim_tables` の `rows` が一定刻みでない・必要キー欠落・配列の長さが群数と違う / `const` の欠落 / `assembly.steps` の必須キー欠落 / `ui` の列挙値・色・`chartSeries`（0 個、6 個以上、重複、未知の id）・`legendGroups`・`colors` の不正。

ページ側（`viewer/lattice/ui-config.mjs` の `normalizeUi`）も同じ規則で検査し、壊れた設定は黙って直さずエラー画面にする。旧 3 モデル以外で `ui` が無い表示データは「書き出し直してください」と出る。
