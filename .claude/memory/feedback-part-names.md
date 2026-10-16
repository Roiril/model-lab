---
name: feedback-part-names
description: 部品は id やファイル名でなく、Studio の台帳の日本語の名前（ユーザーが付け直した呼び名を優先）で呼ぶ
metadata:
  node_type: memory
  type: feedback
  originSessionId: 517a4558-6e3c-45ad-b093-65228a7cb0de
  modified: 2026-10-16T13:43:03.214Z
---

ユーザーとシュビーの間で、部品を同じ名前で呼ぶ。id（`cam_2_2`）や STL のファイル名を会話・報告・Studio の返信の主語にしない。

**Why:** 2026-10-16 ユーザー指示。「パーツを、シュビーがどういう名前で認識しているかと、私がどう呼ぶかを、すり合わせる必要がある」。Studio の部品一覧と透過の選択も、モデル名やファイル名では分かりにくいと言われた。

**How to apply:** 部品の名前の正本は `build/manifest.json` の `parts[].label`。ユーザーが Studio で付け直した名前は依頼の `partNames` で届くので、`models/<name>/part-names.json` に書き戻し、`tools/studio_parts.py <name>` で `viewer/studio/parts/<name>.json` を作り直す。以後はその呼び名を使う。新しいモデルでは最初から label を書く（`.agent/rules/model-request.md` §7）。関連: [[mechanism-gate-harness]]
