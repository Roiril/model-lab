---
name: blender-live-booth-scene
description: 起動中の Blender（MCP :9876）には IVRC ブースのパイプ骨組みが入っている。clear_scene 厳禁
metadata: 
  node_type: memory
  type: project
  originSessionId: da53c0ea-5e54-41ee-87c8-7843b7afd399
  modified: 2026-08-14T08:51:26.553Z
---

MCP でつながる Blender のシーンには、ユーザーが組んだ **IVRC ブースのパイプ骨組み**が入っている
（`A_*` `B_*` `P_*` `C_*` の各コレクション。Φ28 パイプ、L 字の 2 面。上のレールは z=966.6mm）。
`sketch_ref` コレクションは下絵。

- **`lib/blender_utils.clear_scene()` を MCP 経由で呼んではいけない。** ブースごと消える。
  ライブのシーンには自分のコレクションを作り、その中だけを消して作り直す
  （実装例: `models/pipe-phone-clamp/live.py`）
- **`Cube.005` はユーザーが手で置いた板**で、取り付け物の姿勢の指定そのもの（振り 45°・伏せ 45°）。
  位置と回転を実物から読んで仕様に使う。動かさない
- `Cube.006` は前スレッドが作ったホルダーの STL。作り直す時は隠すだけにする
- ヘッドレス（`./run.sh`）は別プロセスなのでライブのシーンに影響しない。STL の書き出しはこちら

関連: [[pipe-phone-clamp-design]]
