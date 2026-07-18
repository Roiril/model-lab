# アルゴ (algo) — 数字カード

ボードゲーム「アルゴ」の数字カードを、テクスチャ付き 3D モデル（GLB）として
再構築したもの。海底探検 (deep-sea-adventure) と同じライン（PIL でテクスチャ描画 →
bpy でテクスチャ付き薄板メッシュ → GLB）で、**Unity 取り込み**を想定している。

角丸長方形のカード面に数字を刷り、白カード（白地・黒数字）と黒カード（黒地・白数字）を
0〜11 まで。実物写真に倣い、6 のカードのみ小さな "a.lgo" ワードマークを添える。

## パイプライン

```
gen_textures.py   PIL で角丸長方形＋数字を描画 → exports/algo/tex/*.png
                  カード外形（角丸長方形）を exports/algo/outlines.json に出力
build_glb.py      bpy が JSON を読み、UV 付き薄板メッシュを生成・テクスチャ貼付
                  → glb/<name>.glb（単体） + algo.glb（俯瞰一括：白/黒 2 段）
render_preview.py 俯瞰 GLB を EEVEE でレンダ → _preview.png（目視確認用）
```

実行（model-lab ルートで）:

```bash
python models/algo/gen_textures.py
./run.sh models/algo/build_glb.py
./run.sh models/algo/render_preview.py   # 任意（確認用）
```

## 閲覧（model-lab ギャラリー）

```bash
node server.js
# → http://localhost:3000/viewer/algo.html
```

左サイドバーから 24 枚を個別に / 俯瞰一括で閲覧できる（Three.js + GLTFLoader）。

## 構成（全 24 枚）

| 種別 | 地色 | 数字色 | 値 |
|---|---|---|---|
| 白カード | オフホワイト | 黒 | 0–11 |
| 黒カード | オフブラック | 白 | 0–11 |

- カード寸法: **42 × 62 mm**（角丸半径 3.5mm）、厚み 2.0mm（Unity 表示用。実カードより厚め）
- 単位はメートル（Unity 1 unit = 1m）。カード幅 ≈ 0.042 unit。

## 設計メモ

- 数字フォントは **Jost**（Futura 系の幾何学サンセリフ）。実物の書体を近似したもので厳密一致ではない。
- 表面のみテクスチャ。側面・裏は地色ソリッド（裏面の数字・模様は未作成）。
- テクスチャは GLB に埋め込み済み。Unity へは glb をそのままドラッグ（ランタイム読込は glTFast 推奨）。

## 既知の制限・TODO

- 裏面デザインは未作成（表のみ）。両面化するなら裏テクスチャを足してボトム面に割当。
- カード寸法・フォントは実物の概算・近似。正確な公式寸法が判明したら params.py を更新する。
- 実物の 6 のロゴ位置（数字の中）とは異なり、下部に簡略配置している。
