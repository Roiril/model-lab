---
name: mechanism-gate
description: model-lab で動く部品・組み立て・既製部品（サーボ等）の嵌め合いがあるモデルを作る・直すときの手順と完了条件。spec.json に依頼の要件を写し、build/ に部品表・動作・組立の姿勢を書き出し、tools/mechgate.py のゲート（ハーネスが持つ校正済みの計器）を exit 0 で通すまでを 1 本の流れにする。「箱」「機構」「サーボで動く」「開閉」「カム」「歯車」「組み立て検証」「物理検証」「刷れるか」「住人の箱」「C1」「C2」「C4」で発動。動かない置物には使わない。
---

# 刷れる機構をゲートで仕上げる

C1・C2（Codex 製）と C4-3 タンジブル画素キューブ（Claude 製）の作り方から抜き出した手順。
**完了かどうかは `py -3.11 tools/mechgate.py check <名前>` の終了コードで決まる。**
自前の検証スクリプトの「合格」や、報告の文章では決まらない。

なぜこうしたか: 過去の失敗はどれも、作った側の検査が「合格」と言っていた所で起きた。

- C3 は歯車が STL から消えていたのに「共通体積 0」で駆動成立とした
- C4-3 は潰しリブの許可を挿入の全行程に広げていて、87mm の軸が実物で通らなかった
- C4-3 の配線の窓は、コネクタ寸法を仮定したまま作って実物で通らなかった

ゲートはこの 3 つをそれぞれ落とす（`tools/mechgate_lib/selftest.py`）。

## 0. 先に読む

1. 依頼文と `.agent/rules/model-request.md`（共通条件・既定値・報告の欄）
2. サーボを使うなら `.claude/skills/servo-robot-design/SKILL.md`
3. 機構の方式・継ぎ手・刷り方は共通スキル `printable-mechanism-design`（`~/.agents/skills/` = `~/.claude/skills/`）の
   SKILL.md と、場面ごとの `joints.md` `cams.md` `printing.md`。`verification.md` は計器を自作するときの資料で、
   ゲートを使うなら読まなくてよい

## 1. 手順

| 段 | やること | コマンド・ファイル |
|---|---|---|
| 1 | spec の雛形を作り、依頼の要件を 1 行ずつ写す。各要件に検査 id を割り当てる。数で確かめられないものは `manual:<実物での確かめ方>` | `py -3.11 tools/mechgate.py new <名前>` → `models/<名前>/spec.json` |
| 2 | 使う既製部品を `uses` に書き、台帳の仮値をすべて `unknowns` で扱う（試し刷りを最優先） | `lib/printmech/parts_ledger.json` |
| 3 | 寸法を `params.py` に書く。既製部品は正本を import し、書き写さない | `models/sg92r-photo/params.py` |
| 4 | 方式を数で比べて決める（伝達角・トルク・部品数）。運動学は形と別のモジュールにする | 実例 `models/servo-lid-cube/linkage.py` |
| 5 | 形を作り、build/ に契約のファイルを書き出す | `lib/printmech/geometry.py`、`lib/printmech/contract.py` |
| 6 | 当たってよい所（圧入・スナップ・正本どうし）だけを `allowances` に、力を伝える所を `interfaces` に宣言する | §3 |
| 7 | 途中は速い検査で回す | `py -3.11 tools/mechgate.py check <名前> --no-blender` |
| 8 | 刷るプレートを作ってスライスし、`prints/<名前>/` に置く | `printable-mechanism-design/printing.md`、`tools/plate_3mf.py` |
| 9 | 全検査を流し、exit 0 にする。赤なら形を直す（許可を広げない） | `py -3.11 tools/mechgate.py check <名前>` |
| 10 | 報告は `build/gate_summary.md` の数字を写す。手で数え直さない | §5 |

build/ の契約（`viewer/lattice/CONTRACT.md` と同じ形。Studio の物理検証・組み立てタブもこれを読む）:

- `manifest.json`: 部品表。`print` があれば刷る部品（刷る向きの STL）。無ければ既製部品。
  **`label` に人が分かる日本語の名前を必ず書く**。書き出したら `py -3.11 tools/studio_parts.py <名前>` で Studio の部品台帳を作る
  （ユーザーとの呼び名のすり合わせ。`.agent/rules/model-request.md` §7「部品の呼び名」）
- `motion.json`: サーボ角ごとの全部品の姿勢。刻みは 2.5° 以下
- `assembly.json`: 組立工程ごとの姿勢の列。最後は全部品が単位行列（組んだ位置）。1 フレームの移動は 1mm・5° 以下

`contract.py` の `write_manifest` `write_motion` `AssemblyPlan` `straight_path` で書ける。

## 2. ゲートが測るもの

| 検査 id | 何を | 落ちたときに直す所 |
|---|---|---|
| `parts.topology` `parts.components` `parts.self_intersection` | 閉じた多様体・連結成分の数（既定 1）・自己交差 | boolean の後の掃除。離れた成分は腕の付け根を確かめる |
| `print.grounding` `print.slender` | 接地 10mm² 以上・浮いた成分なし・高さ / 接地の短辺 ≤ 5 | 刷る向き、寝かせる |
| `assembly.envelope` | 組んだ外形が `envelope_mm` 以下 | 外形 |
| `motion.interference` | 全角度・全部品の組の共通体積（許可の外は 0） | 形。許可は広げない |
| `motion.torque` | 重力の必要トルク ≤ 停動の 1/3（下限の見積もり） | 方式・重さ |
| `interface.coverage` | 動く部品がすべて、駆動の界面でアクチュエータにつながる | `interfaces` に界面を書く（ゲートが形で確かめる） |
| `interface.drive` | 従動側を動きの前後へ押すと、遊び（≤5° / 1mm）の中で駆動側に当たる | 噛み合い・鍵・カムの形 |
| `interface.retention` | 外れる向きへ動かすと、上限（≤3mm、噛み合いの深さ）までに止まる | 抜け止めの形 |
| `assembly.path` | 各工程で許可の外の当たりが無い。圧入は最後の `insertion_mm`（≤6mm）だけ。スナップはひずみ ≤2% で最後の姿勢に重なりを残さない | 経路・形 |
| `unknowns.resolved` | 既製部品の仮値をすべて扱った | 試し刷りの部品を作る |
| `print.slice` | スライス済みの 3mf で、外に見える支えの無い押し出し ≤ 2mm、サポート無し | 刷る向き・形 |

閾値は `tools/mechgate_lib/limits.py`。**モデルの作業の中でここと計器（`tools/mechgate*`・`lib/printmech/solid_meter.py`）を変えない。**
変えるとゲートは「ハーネスが未校正」で全モデルを落とす。ハーネスを直すのは別の作業として行い、
`py -3.11 tools/mechgate.py selftest`（故障を注入した版が狙った検査で落ちるか）を通す。

## 3. spec.json の書き方

```json
{
 "model": "<名前>",
 "request": "依頼文の原文",
 "requirements": [{"id": "R1", "text": "蓋が 95° 開く", "checks": ["motion.interference", "interface.drive"]}],
 "envelope_mm": [100, 100, 100],
 "uses": ["sg92r"],
 "parts": {"components": {"pins": 4}, "jigs": ["phase_comb"], "slender_ok": {"<id>": "理由"}},
 "motion": {"actuator": "sg92r_horn", "servo": "sg92r", "exclude": [{"part": "phase_comb", "reason": "治具"}]},
 "allowances": [
  {"type": "press_fit", "pairs": [["cam_1", "shaft"]], "insertion_mm": 2.8, "basis": "潰しリブ 3 本。最後の 2.8mm だけ擦る"},
  {"type": "static_fit", "pairs": [["cam_1", "shaft"]], "max_mm3": 1.0, "basis": "組んだ後に残るリブの重なり 0.91mm3"},
  {"type": "snap", "pairs": [["clip", "housing"]], "engage_mm": 2.0, "strain_percent": 1.2, "deflection_mm": 0.3, "basis": "ε=1.5·t·δ/L² の計算"},
  {"type": "reference_internal", "pairs": [["sg92r", "sg92r_horn"]], "max_mm3": 0.05, "basis": "正本どうしの出力軸の重なり"}
 ],
 "interfaces": [
  {"id": "horn-crank", "type": "drive", "driver": "sg92r_horn", "driven": "crank", "sides": "both", "max_play_deg": 3},
  {"id": "cam-pixel", "type": "drive", "driver": "cam_1", "driven": "pixel_1", "sides": "one_sided", "max_play_mm": 0.5},
  {"id": "lid-up", "type": "retention", "parts": ["lid"], "direction": [0, 0, 1], "max_free_mm": 1.0, "engage_depth_mm": 2.25}
 ],
 "unknowns": [
  {"id": "sg92r.connector", "trial_part": "prints/<名前>/trial/wire_window.stl"},
  {"id": "sg92r.output_spline", "not_applicable": "付属ホーンを付属のまま使う"},
  {"id": "sg92r.wire", "accepted_risk": "理由"}
 ],
 "waivers": [{"check": "print.slice", "reason": "依頼に「スライス不要」"}]
}
```

- `sides`: 歯車・鍵・ピンは `both`（正逆どちらに押しても当たる）。重力やばねで戻るカムの従動子は `one_sided`
- 宣言（許可・例外・外した検査・未確認の扱い）は、報告の先頭に全部並ぶ。合格の理由にはならない。読む人が確かめる
- 外せない検査: `spec.valid` `contract.files` `parts.topology` `motion.interference` `interface.coverage`
  `interface.drive` `assembly.path` `unknowns.resolved` ほか（`gate.py` の `NON_WAIVABLE`）

## 4. ゲートが見ないもの（自分で数を出して報告に書く）

C4-3 で親（指揮役）が止めた項目。ゲートでは数にならないので、報告の「決めたこと」に式と数を書く。

- **力の釣り合い**: 歯車の分離力・カムの反力と、それを押さえる物（自重・押さえ・爪）。押さえまでの距離 < 噛み合いの深さ
- **遊びの鎖**: 界面ごとの遊びを足した最悪（栓 → 案内板 → ベゼル）。界面ごとの合格では見えない
- **代わりの指標**: 余裕が赤くなったら基準を緩めず、本来の要求（停止したときの出力の高さの誤差など）を直接測る
- **式の単位**: 変速を挟むトルクは仕事で換算する（τ_servo = τ_out · g / η）。ゲートの `motion.torque`（重力だけ）と桁が違えば式を疑う
- **下限ちょうどの値**: 最小肉厚 1.2mm・隙間の下限ちょうどは、製造誤差の余裕が無いと書く
- **実物で通った値を使う**: 台帳の `printed_ok`（例: SG92R の耳の溝は片側 0.25mm・リブ無し）。作り直さない

## 5. 報告

`model-request.md` §8 の欄で書く。数字は `build/gate_summary.md` から写す。

- **ゲート**: 合格か、止めている検査の id（赤のまま渡すなら、そう書く）
- **要件ごとの結果**: gate_summary の「要件」表
- **宣言したもの**: 許可・例外・外した検査・未確認の扱い（gate_summary の最後の節）
- **実物で確かめること**: requirements の `manual:` と unknowns の試し刷り、§4 の数
- Studio は `http://localhost:3000/?model=<名前>` を開いた状態で渡す

## 6. やってはいけないこと

- 許可（`allowances`）を広げてゲートを通す。当たりが出たら形を直す
- 計器・閾値を同じ作業の中で変える
- `--no-blender` の結果で「合格」と言う
- 自前の verify.py の合格をゲートの代わりに報告する（自前の検証は作ってよいが、完了の条件ではない）
- 既製部品の仮値（台帳の `estimated` / `assumed` / `missing`）を、試し刷り無しで本体に使う
