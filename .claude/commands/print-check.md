モデル「$ARGUMENTS」の3Dプリント適性をチェックしてください。

## チェック手順

### 1. STLファイルの存在確認
`exports/$ARGUMENTS.stl` が存在するか確認する。
なければ先に `/build $ARGUMENTS` を実行するよう伝える。

### 2. 寸法チェック（params.py を読む）
以下を確認してレポートする:
- 外形寸法（W × D × H mm）
- 最小肉厚（WALL, TOP の値）
- クリアランス値

**基準:**
- 肉厚 < 1.2mm → 警告（FDMでは薄すぎる）
- 肉厚 < 0.8mm → エラー（印刷不可能な可能性）

### 3. Blenderで多様体チェック
以下のBlenderスクリプトを一時ファイルとして実行する:

```python
import bpy, bmesh, sys

bpy.ops.wm.stl_import(filepath=r"PATH_TO_STL")
obj = bpy.context.selected_objects[0]
bm = bmesh.new()
bm.from_mesh(obj.data)
non_manifold = [e for e in bm.edges if not e.is_manifold]
print(f"NON_MANIFOLD_EDGES: {len(non_manifold)}")
bm.free()
```

`NON_MANIFOLD_EDGES: 0` なら多様体OK。

### 4. レポート形式

```
## プリントチェック: <name>

寸法:     W×D×H mm
最小肉厚: X mm  [OK / 警告]
多様体:   OK / NG (N edges)
推定体積: Xcm³（参考）

問題なし → プリント可能
問題あり → [修正提案]
```
