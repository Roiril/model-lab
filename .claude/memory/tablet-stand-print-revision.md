---
name: redmi-stand-history
description: Redmi Pad SEスタンドの経緯。45度版の印刷失敗と補強、2026-11-14にredmi-pad-standへ作り直し。横置き専用で穴は不要。
metadata:
  node_type: memory
  type: project
  originSessionId: 64a93352-622f-48ff-8fba-f7b1974ef232
  modified: 2026-11-14T06:24:22.437Z
---

- ユーザー報告: 使用フィラメントを抑えたRedmiスタンドが印刷中にスパゲッティで失敗。失敗層・剥がれの位置は不明。
- `models/tablet-stand-45/` を同IDで更新。212×220×121.65mm、全面6mm台座、左右28mm幅、三角窓は66mm以下で閉じる。
- 満充填ではなく18%gyroid。X1C用PLA/PETGのスライス済みファイルは `prints/tablet-stand-45/`。
- 凹断面の蓋は明示三角化。その後のBoolean＋側面0.6mm bevelで微小三角形の検査が2回失敗した。追加bevelを外すと零面積0・非多様体0になった。検査閾値は変えていない。
- 形の丸みはプロファイルと台座XY輪郭に持たせた。使用しない `_chamfer_side_edges` と定数は削除。
- `verify.py` の転倒計算は旧4枚パッド位置から台座の内接長方形へ更新。低充填モデルなので `--stand-mass` を必須にした。
- `plate.py` は共有のG-code計器を利用。旧Bambu CLIでは物体ラベルがなく `None` に全部品の経路が入るため、このキーも必ず検査する。
- 生成ログと検証出力: `G:\マイドライブ\shubie\renders\2026-10-30_redmi-stand\`。詳細・コマンドはモデルREADME。
- 実印刷による改修版の確認は未実施。計算の合格を「スパゲッティ再発なし」とは扱わない。
- 2026-11-14 ユーザー依頼で `models/redmi-pad-stand/` へ根本から作り直し（60°・側面輪郭の押し出し一体・後ろへ流れる尾）。tablet-stand-45 は catalog で archived。
- ユーザーは**横置き専用**で使う。縦置き用のケーブル溝などの穴は「不要な穴」として外すよう指示された（2026-11-14）。
