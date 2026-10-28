---
name: mechanism-gate-harness
description: 機構モデルの完了は tools/mechgate.py のゲートで決める。作った理由、計器の持ち主、閾値を決めた根拠、tangible で見つかったこと
metadata:
  node_type: memory
  type: project
  originSessionId: ba747b01-29fa-41c8-b58e-fb015c705e12
  modified: 2026-10-15T02:02:58.852Z
---

2026-10-15、ユーザー依頼「C1・C2・タンジブル UI 機構の箱の作り方を通して、Claude 以外（Codex 等）でも同等以上の品質が出るハーネス」で作った。

- 方針は「モデルはデータを出し、計器はハーネスが持ち、完了はゲートの exit code で決める」。design-critic 2 体が独立に同じ結論へ収束した
  - 根拠: 散文の規則は Opus でも守られなかった（model-request §6 の「圧入は最後だけ許可」が入った翌々日に C4-3 が全行程を許可）
  - C1 は Codex 製、C4-3 は Claude 製で、失敗の型は同じ（駆動を仮定する検証、許可の広げすぎ、既製部品の仮値）。モデル差よりハーネス差
- 手順書の正本は `.claude/skills/mechanism-gate/SKILL.md`（2026-10-28 に .claude/ へ一本化。Codex は .agents/skills の junction から同じ物を読む）。閾値は `tools/mechgate_lib/limits.py`、既製部品の台帳は `lib/printmech/parts_ledger.json`
- **Why:** 作った側の自己検査が「合格」と言っていた箇所で、実物の失敗が起きていた
- **How to apply:** 機構の依頼では spec.json を最初に書き、ゲートを exit 0 にする。サブエージェントや Codex の「合格」も、親がゲートを流し直して確かめる

## 決めた閾値の根拠

- スナップの乗り上げ上限 12mm は、tangible の押さえクリップと案内板の舌が 10〜11mm 乗り上げるため。初めに置いた 6mm には根拠が無かった
- 組立・動作の姿勢の密度は、モデルの刻みを信じず、ゲートが剛体補間で「どの点も 1mm 以内」にそろえる。selftest に、10mm 刻みで 0.6mm の板をすり抜ける負例がある
- 抜け止めの相手の既定は「動作中に動かない部品」。重力で載るだけの画素を相手に数えると、軸が画素で止まったことになる

## 踏んだこと

- core.autocrlf=true なので、別の作業ツリーではテキストが CRLF になる。SHA は改行を LF にそろえて取る（直す前は全モデルが「未校正」になった）
- tangible には配線の窓とコネクタの試し刷りが無い。spec では accepted_risk として報告の先頭に出している（実物で窓が通らなかった箇所）

関連: [[tangible-pixel-cube-design]] [[lattice-verified-assembly]] [[sg92r-horn-orientation]]
