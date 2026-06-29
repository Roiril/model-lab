# 海底探検 (Deep Sea Adventure) — テクスチャ付きコンポーネント

ボードゲーム「海底探検」の全コンポーネントを、テクスチャ付き 3D モデル（GLB）として
再構築したもの。3D プリント用 STL とは別ラインで、**Unity 取り込み**を想定している。
裏面は未作成（写真の見えている面＝表のみ）。

## パイプライン

```
gen_textures.py   PIL でクリーンなベクター調テクスチャを描画 → exports/deep-sea/tex/*.png
                  各ピースの 2D アウトラインを exports/deep-sea/outlines.json に出力
build_glb.py      Blender(bpy) が JSON を読み、UV 付き薄板メッシュを生成・テクスチャ貼付
                  → glb/<name>.glb（単体） + deep-sea-adventure.glb（俯瞰一括）
render_preview.py 俯瞰 GLB を EEVEE でレンダ → _preview.png（目視確認用）
```

実行（model-lab ルートで）:

```bash
python models/deep-sea-adventure/gen_textures.py
./run.sh models/deep-sea-adventure/build_glb.py        # = blender --background --python ...
./run.sh models/deep-sea-adventure/render_preview.py   # 任意（確認用）
```

## 閲覧（model-lab ギャラリー）

```bash
node server.js
# → http://localhost:3000/viewer/deep-sea.html
```

左サイドバーから全 26 種を個別に / 俯瞰一括で閲覧できる（Three.js + GLTFLoader）。

## コンポーネント一覧（全 26 種）

| 種別 | 形状 | 数 | 値/内容 | 厚み |
|---|---|---|---|---|
| 宝物 L1 | 三角 | 4 | 0–3 | 2.4mm |
| 宝物 L2 | 四角 | 4 | 4–7 | 2.4mm |
| 宝物 L3 | 五角 | 4 | 8–11 | 2.4mm |
| 宝物 L4 | 六角 | 4 | 12–15 | 2.4mm |
| 裏トークン | 円(+)/三角/四角/五角/六角 | 5 | レベル指標ドット | 2.4mm |
| 空気マーカー | 円 | 1 | 赤チップ | 6mm |
| 潜水艦ボード | 潜水艦シルエット | 1 | 25→1 トラック + ダイブ点 | 3mm |
| 潜水士（駒） | 人型シルエット | 2 | 紫 / 赤 | 8mm |
| サイコロ | ラウンドキューブ | 1 | 1–6 の目（木目） | 16mm |

寸法は実物に近い概算（メートル単位でモデリング: 例 三角チップ約 33mm）。

## Unity への取り込み

- `exports/deep-sea/glb/*.glb` をそのまま Assets にドラッグ（テクスチャは GLB に埋め込み済み）。
- ランタイム読込なら **glTFast**、エディタ取込なら glTFast / UnityGLTF を推奨。
- 単位はメートル（Unity 1 unit = 1m）。スケール感はチップ約 0.03 unit。
  ボードゲーム用に拡大したい場合は取り込み後にまとめてスケール。

## 既知の制限・TODO

- 裏面は未作成（全ピース表のみ）。両面化するなら裏テクスチャを足してボトム面に割当。
- 潜水艦ボードのトラックは写真を参考にした再現で、実物の升目数・配置と厳密一致ではない。
- 数字フォントは Bodoni（宝物）/ Georgia（ボード）。実物の書体とは別。
