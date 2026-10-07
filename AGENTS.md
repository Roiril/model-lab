# model-lab — Agent Instructions

3Dプリンター用モデルをBlender Python API (`bpy`) でコード化するプロジェクト。
ユーザーはモデルのアイデアを伝え、Codexがスクリプトを書いて即座にブラウザで確認できる。

---

## 環境

| 項目 | 値 |
|------|-----|
| Blender | `C:/Program Files/Blender Foundation/Blender 5.1/blender.exe` |
| 実行 | `./run.sh models/<name>/model.py` |
| ビューワー起動 | `node server.js` |
| ビューワーURL | http://localhost:3000 |

---

## ディレクトリ構成

```
models/<name>/
  params.py    # 寸法・定数のみ（単位: m）
  model.py     # bpyスクリプト本体（複数パーツは base.py / module.py など分割可）
lib/
  blender_utils.py   # clear_scene(), export_stl()
exports/             # 出力STLファイル（ビューワーが監視）
viewer/studio/       # Studio（共同編集 UI。/ で開く）。旧ビューワーは viewer/index.html（/legacy）
requests/            # Studio から届いた依頼（git 管理外）
tools/requests.py    # 依頼の一覧・要約・返信・待ち受け
server.js            # HTTP + WebSocket サーバー
```

---

## モデル作成ワークフロー

モデルを作成・派生・追加するときは先に [.agents/skills/model-catalog/SKILL.md](.agents/skills/model-catalog/SKILL.md) を読む。表示名と用途を `models/<name>/catalog.json` に記録する。分類の正本は `models/catalog-groups.json`。完了前に `node tools/catalog.js check` を実行する。既存のモデルIDを改名せず整理する。

SG92Rサーボと付属ホーンの正本は `models/sg92r-photo/`。2026-10-07にユーザーが形状を確定した。寸法は同フォルダの `params.py`、出典と仮値は `README.md` を参照する。旧 `models/sg92r/` と `models/horn/` は削除済み。単独の実寸モデルや計測UIを作り直さず、正本を更新する。古いスキルの計測UI手順よりこの指定を優先する。既存ロボットが使う `lib/servo_core.py` の値を正本として扱わない。既存ロボットの形状変更はその依頼の範囲で行う。

新しいモデルを作るとき、必ずこの順番で進める。

1. **寸法調査** — 実物がある場合は公式スペックを確認する
2. **`params.py` を先に書く** — 寸法・クリアランス・肉厚を定数化する
3. **`model.py` を書く** — `params.py` をインポートして使う
4. **ビルド実行** — `./run.sh models/<name>/model.py`（または下記の watch.py 経由）
5. **ビューワー確認** — サーバーが起動していなければ `node server.js` を起動する
6. **ユーザーへ報告** — 外形寸法・肉厚・設計上の判断を明示する

---

## インタラクティブ・モデリング（Blender 共同編集）

ユーザーが Blender で目視確認しながら一緒に詰めるときのワークフロー。

### 役割分担

- **Codex**: コード編集後に `./run.sh models/<name>/model.py` を実行してビルド
- **Blender 側 watch.py**: `exports/<MODEL>.stl` の mtime を監視し、変化したらシーンをクリアして STL を再読込

ソース（`model.py` / `params.py`）の import キャッシュ問題が起きないよう、**watch.py はビルド成果物（STL）のみを監視**する設計。

### ユーザー側のセットアップ手順

1. Blender 起動
2. **Scripting** タブ → テキストエディタで [lib/watch.py](lib/watch.py) を Open
3. 上部の `MODEL = "<name>"` を編集対象モデル名に書き換え
4. **Run Script**（`Alt+P`）
5. コンソールに `[watch] watching ...` と出れば常駐開始
6. 以降、Codex がビルドする度に Blender のシーンが自動更新される

### Codex 側の振る舞い

- 編集後は **必ず** `./run.sh models/<name>/model.py` を実行する（watch.py は STL の mtime 変化でしか発火しない）
- ユーザーが「壊れた」「見えなくなった」等と言ったらすぐ前の状態に戻せるよう、大きな構造変更は段階的に行う
- 別モデルに切り替えるときは「watch.py の `MODEL` 定数を書き換えて Run Script し直してください」と案内する

### 注意

- watch.py は Blender 起動中のみ有効。Blender を閉じたら次回また Run Script 必要
- 再読込時は **シーン内の全オブジェクトが削除されて STL がインポートされる**。ユーザーが Blender で手動編集中の内容は失われる。手動で形をいじっているときはビルドを保留する
- ビューワー（http://localhost:3000）でも同じ STL を見られるので、Blender を閉じたいときはビューワーで代替可

---

## bpy スクリプト規約

### ファイルの先頭テンプレート

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
sys.path.insert(0, os.path.dirname(__file__))

import bpy
from blender_utils import clear_scene, export_stl
from params import *

clear_scene()
# --- modeling ---
export_stl("<model_name>")
```

### 単位

- Blender内部単位はメートル。`1mm = 0.001`
- `params.py` の定数はすべてメートルで書く
- コメントでmm値を併記する: `WALL = 0.002  # 2mm`

### Boolean 操作

```python
mod = base.modifiers.new("cut", "BOOLEAN")
mod.operation = "DIFFERENCE"
mod.object = cutter
mod.solver = "EXACT"          # EXACT を使う（FASTは非多様体が出やすい）
bpy.ops.object.modifier_apply(modifier="cut")
bpy.data.objects.remove(cutter, do_unlink=True)
```

### Transform の適用

スケール変更後は必ず `bpy.ops.object.transform_apply(scale=True)` を実行する。
Boolean前に適用しないと寸法がずれる。

### bmesh で手動メッシュを作るとき

`bm.faces.new()` の頂点順は **外側から見て反時計回り（CCW）** にする。
間違えると法線が内向きになり、Boolean EXACT が無効になる（削れない・結合されない）。
作成後に `bmesh.ops.recalc_face_normals(bm, faces=bm.faces)` を呼ぶと安全。

```python
bm = bmesh.new()
v = [bm.verts.new(c) for c in coords]
# 頂点順: 外から見てCCW
bm.faces.new([v[0], v[1], v[2], v[3]])
# ...
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)  # 法線を外向きに強制
bm.to_mesh(mesh)
bm.free()
```

### Boolean カッターの配置

カッターの面がターゲットと **面一（coplanar）** だと Boolean が不安定になる。
カッターをターゲット表面より **0.5mm 程度突き出して** 配置する。

```python
# 悪い例: カッター上面 = ベース上面（面一）
dt.location = (0, 0, COVER_H)

# 良い例: カッターをわずかに突き出す
dt.location = (0, 0, COVER_H + 0.0005)
```

---

## 3Dプリント向け設計ガイドライン

| 項目 | 推奨値 |
|------|--------|
| 最小肉厚 | 1.2mm 以上（FDM）|
| クリアランス（はめ込み） | 0.2〜0.4mm per side |
| クリアランス（ゆるい） | 0.5〜0.8mm per side |
| Boolean solver | EXACT |
| メッシュ | 多様体（manifold）であること |
| エクスポート | `export_stl()` を使う（`bpy.ops.wm.stl_export`） |

---

## Studio（ユーザーと一緒に形を詰める UI）

http://localhost:3000 が Studio。ユーザーは面を選んで「ここを厚く」、断面に線を描いて「この線に沿って」と指示し、
「シュビーに送る」を押す。依頼は `requests/<model>/<id>/` に届く。

- **作業を始めたら最初に `py -3.11 tools/requests.py list` を実行する**。未対応があればスキル `studio-inbox` に従う。ユーザーが Studio で指示すると言ったら `tools/requests.py wait --agent codex` で待つ
- 受け方・読み方・返し方は **`.agents/skills/studio-inbox/SKILL.md`**（座標系・意図の意味・返信の書き方・やってよい操作の範囲）
- 直したら `py -3.11 tools/requests.py reply <id> "<何をどう変えたか>" --status done`。Studio 側で変更前と重ねて比べられる
- 設計の正本は `.agent/plans/2026-10-07_studio.md`、モジュールの約束は `viewer/studio/CONTRACT.md`

---

## ユーザーへの見せ方

モデルを作成・更新した後、必ず以下を伝える。

1. **ビューワーURL**: http://localhost:3000 を開くよう促す
2. **外形寸法**: W × D × H mm で明記する
3. **設計上の判断**: クリアランス・肉厚・特記事項を簡潔に説明する
4. **次のアクション**: 「フィットが合わなければクリアランスを変えます」など

サーバーが起動していない場合は先に `node server.js` を起動する。

---

## スキル一覧

| コマンド | 用途 |
|----------|------|
| `/new-model <name>` | 新モデルのスキャフォールドを生成 |
| `/build <name>` | モデルをビルドしてビューワーに反映 |
| `/print-check <name>` | 3Dプリント適性チェック |

---

## Codex ハーネス (.Codex/)

- **[memory/](.Codex/memory/)** — 自動メモリ（`MEMORY.md` がインデックス、topic ごとに分割）
- **[skills/](.Codex/skills/)** — `servo-robot-design`：1サーボ・ロボット（round/square-bot 等）とサーボ/ホーン嵌合部品・アクセサリの設計原則・落とし穴・ワークフロー集（サーボ機構/ホーン結合/配線/目耳/単位/boolean/検証/印刷分割を扱う。サーボ系を触る前に必読）
- **[hooks/](.Codex/hooks/)** — プロジェクト固有 PreToolUse ガード
- **[settings.json](.Codex/settings.json)** — `bypassPermissions`（書き込み前承認なし）
- **[settings.local.json](.Codex/settings.local.json)** — ローカル個別 allow リスト
- **[commands/](.Codex/commands/)** — `/new-model` `/build` `/print-check` の本体

汎用 hook（SessionStart 状態注入 / 不可逆操作ガード / Windows エンコーディング修正）とスラッシュコマンド（`/commit`, `/plan`）は `~/.Codex/` にグローバル配置済み。

## 共有ハーネス (.agent/)

`.agent/` 配下は他エージェント (Cline / Roo Code) 用の資産だが、**領域別ルールと計画は Codex からも参照する**。

### 領域別ルール（該当領域の作業前に読む）

- [model-lab](.agent/rules/model-lab.md) — bpy / Blender 周りの全規約（このファイルの主要部と同期）
- [global](.agent/rules/global.md) — 他エージェント向け汎用規約（参考）

### その他

- **ワークフロー**: `.agent/workflows/` — 他エージェント用（Codex は `.Codex/commands/` を使う）
- **計画**: `.agent/plans/` — 実装計画（`YYYY-MM-DD_<slug>.md`）。`/plan <slug>` で作成
- **タスク**: `.agent/tasks/` — チェックリスト

動作モードはグローバル `~/.Codex/AGENTS.md` 参照（書き込み前承認なし、git コミット規約 等）。
