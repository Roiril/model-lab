---
name: feedback-no-mystery-box-reference
description: SG92R の箱・開閉機構を作るとき、住人の箱（models/mystery-box-sg92r-*）の形と機構を参考にしない。Studio の物理検証・組み立てタブは使い、新モデルの検証もそこから見せる
metadata:
  node_type: memory
  type: feedback
  originSessionId: dcd1b2d5-5b38-444e-94b5-c438cbb1727e
  modified: 2026-10-09T14:09:51.053Z
---

SG92R で面を開閉する箱を作るとき、過去の「住人の箱」（`models/mystery-box-sg92r-v5` / `-v6` / `-b3-candidate`）の
**形・機構・部品の分け方**を設計の参考にしない。

ただし Studio 上部の「物理検証」「組み立て」タブ（もとは B3 用の `viewer/physics-box` / `viewer/assembly-box`）は
**参照禁止の対象に含めない**。新しいモデルの検証結果も、別ページだけでなくこのタブから見られるようにする。

**Why:** 2026-10-09、ユーザーが新しい開閉キューブの依頼で明示した（「住人の箱という過去に作った施策があるが、これは参考にしない事」）。
住人の箱は 19〜22 部品の複雑な構成だった。
最初の版のこのメモは「検証の道具も住人の箱のものを使わず作る」と範囲を広げて書いており、検証結果が Artifact の別ページにだけ出た。
タブは B3 専用のまま押せず、ユーザーから「そこから検証など見れるといいんだけど」と指摘された（同日）。

**How to apply:** SG92R の寸法は `models/sg92r-photo`（確定版）から取る。検証の計算は
`models/servo-lid-cube/verify.py` `simulate.py` `slice_check.py` が実例。画面側は `viewer/lid-cube/` が実例で、
モデルごとにタブへ登録する（`viewer/shared/workspace.mjs`）。設計の知見は
`.claude/skills/servo-robot-design` §9.5 にある。関連: [[blender-live-booth-scene]]
