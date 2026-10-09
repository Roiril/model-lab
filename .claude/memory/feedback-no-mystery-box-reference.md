---
name: feedback-no-mystery-box-reference
description: SG92R の箱・開閉機構を作るとき、住人の箱（models/mystery-box-sg92r-*、viewer/assembly-box・physics-box）を設計の参考にしない
metadata:
  node_type: memory
  type: feedback
  originSessionId: dcd1b2d5-5b38-444e-94b5-c438cbb1727e
  modified: 2026-10-09T10:03:29.749Z
---

SG92R で面を開閉する箱を作るとき、過去の「住人の箱」（`models/mystery-box-sg92r-v5` / `-v6` / `-b3-candidate`、
B3 用の `viewer/assembly-box` と `viewer/physics-box`）を設計の参考にしない。

**Why:** 2026-10-09、ユーザーが新しい開閉キューブの依頼で明示した（「住人の箱という過去に作った施策があるが、これは参考にしない事」）。
住人の箱は 19〜22 部品の複雑な構成だった。

**How to apply:** SG92R の寸法は `models/sg92r-photo`（確定版）から取る。検証の道具は住人の箱のものを使わず作る
（実例: `models/servo-lid-cube/verify.py` `simulate.py` `slice_check.py`）。設計の知見は
`.claude/skills/servo-robot-design` §9.5 にある。関連: [[blender-live-booth-scene]]
