# ガイスター (Geister) — 盤面ボード

ボードゲーム「ガイスター」の盤面（6×6 マス）を、実物写真をトップ面テクスチャに
した薄板 3D モデル（GLB）として再構築したもの。海底探検・アルゴと同じライン
（テクスチャ画像 → bpy でテクスチャ付き薄板メッシュ → GLB）で、**Unity 取り込み**を想定。

正方形の板の上面に盤面写真を貼り、側面・裏面は黒マテリアル。

## パイプライン

```
board_photo.jpg   実物盤面の真上撮影（KOD KOD 版・3072px）
gen_texture.py    PIL で黒布背景を切り落とし正方形化 → exports/geister/tex/board.jpg (2048²)
build_glb.py      bpy で UV 付き薄板メッシュ生成・テクスチャ貼付 → exports/geister/geister.glb
render_preview.py GLB を EEVEE でレンダ → _preview.png（目視確認用）
```

実行（model-lab ルートで）:

```bash
python models/geister/gen_texture.py
./run.sh models/geister/build_glb.py
./run.sh models/geister/render_preview.py   # 任意（確認用）
```

## 閲覧

```bash
node server.js
# → http://localhost:3000/viewer/geister.html
```

## 寸法・設計メモ

- 盤サイズ: **390 × 390 mm**、厚み 2mm（厚紙ボード相当）
  - 実測系ソース（組立時 391×391mm・箱 224mm 四方の四つ折り）を丸めた値。公式公表値ではない
- 単位はメートル（Unity 1 unit = 1m）。盤幅 = 0.39 unit
- 表面のみ写真テクスチャ。側面・裏は黒ソリッド (18,18,20)
- テクスチャは GLB に JPEG 埋め込み（GLB ≈ 1.1MB）

## 既知の制限・TODO

- 写真は手持ち撮影のトリミングのみ（射影補正なし）。わずかな歪み・照明ムラは写真由来
- 折り目・凹凸は再現していない（完全な平板）
- オバケコマ（赤/青）は未作成。次のステップ候補
