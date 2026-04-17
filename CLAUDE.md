# model-lab — Agent Instructions

3Dプリンター用モデルをBlender Python API (`bpy`) でコード化するプロジェクト。
ユーザーはモデルのアイデアを伝え、Claudeがスクリプトを書いて即座にブラウザで確認できる。

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
  model.py     # bpyスクリプト本体
lib/
  blender_utils.py   # clear_scene(), export_stl()
exports/             # 出力STLファイル（ビューワーが監視）
viewer/index.html    # Three.js リアルタイムビューワー
server.js            # HTTP + WebSocket サーバー
```

---

## モデル作成ワークフロー

新しいモデルを作るとき、必ずこの順番で進める。

1. **寸法調査** — 実物がある場合は公式スペックを確認する
2. **`params.py` を先に書く** — 寸法・クリアランス・肉厚を定数化する
3. **`model.py` を書く** — `params.py` をインポートして使う
4. **ビルド実行** — `./run.sh models/<name>/model.py`
5. **ビューワー確認** — サーバーが起動していなければ `node server.js` を起動する
6. **ユーザーへ報告** — 外形寸法・肉厚・設計上の判断を明示する

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
