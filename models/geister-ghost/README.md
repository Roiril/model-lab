# ガイスター (Geister) — おばけコマ

ボードゲーム「ガイスター」の駒（おばけ）を Unity 表示用 GLB として再構築したもの。
盤面（[models/geister](../geister/)）と同じコレクション。

弾丸型（丸い頭 → 下に広がる裾）の白い本体に、正面の目2つ、裏面の丸マーカー（赤/青）、
下半分の縦ひだ（シーツの襞）となみなみの裾を再現。実物写真（正面・側面・裏の3枚）から採寸。

## パイプライン

```
ref_front/side/back.jpg   実物3面写真（採寸元・黒背景）
build_glb.py              楕円ロフト本体＋目(boolean)＋ひだ(boolean)＋なみなみ裾＋マーカー
                          → ghost_blue.glb / ghost_red.glb / geister-ghost.glb（青赤2体）
render_preview.py         正面・側面・裏の3アングルを EEVEE でレンダ → _v_*.png
```

実行（model-lab ルートで）:

```bash
./run.sh models/geister-ghost/build_glb.py
./run.sh models/geister-ghost/render_preview.py   # 任意（確認用）
```

## 閲覧

```bash
node server.js
# → http://localhost:3000/viewer/geister-ghost.html
```

## 形状・寸法メモ

- 高さ **50mm**（実測）、幅 ≈ 24mm、断面は円形（奥行き = 幅、側面も正面と同じ丸み）
- シルエットは数式生成の滑らかな1本曲線: 丸くブラントな頭（`DOME_POW`）＋ 底のスカート状フレア（`FLARE_FOOT`）
- 本体は中身の詰まったソリッド（Unity 表示用。実物は中空シェルだが表示用途では不要）
- 正面の目: 掘り込み穴＋穴底の暗色ディスク（貫通させず暗く見せる）
- 裏マーカー: 赤 (198,42,40) / 青 (24,96,176) の丸（直径 ≈ 5.2mm）を平らな座ぐりに埋め込み（出っ張らない）
- 裏のひだ: 縦の半円溝 4本（`FLUTE_N`）を boolean で彫る。上端は球で丸めてフェード、
  下端は底面まで到達（底面は平ら）。開始位置はマーカーに被らないよう下げる
- 単位はメートル（Unity 1 unit = 1m）。高さ = 0.05 unit

## 調整ポイント（params.py）

- `HEIGHT` / `RX_BASE` / `DEPTH_RATIO` — 全体サイズと断面の丸み（1.0=円形）
- `SHOULDER_T` / `SHOULDER_REL` / `BODY_FLARE_POW` / `DOME_POW` / `FLARE_FOOT` / `FOOT_WIDTH` — シルエット曲線
- `EYE_*` — 目の位置・大きさ・深さ
- `MARK_*` — マーカーの位置・径・座ぐり深さ・埋め込み量
- `FLUTE_N` / `FLUTE_TOP` / `FLUTE_R` — 裏ひだの本数・高さ・深さ

## 既知の制限・TODO

- 裏のひだは実物のドレープを様式化した近似（写真からの厳密復元ではない）
- 中空シェル版・両面テクスチャは未対応（表示ソリッドのみ）
- 実ゲームは赤8体＋青8体。ここでは各色1体の代表モデル（`geister-ghost.glb` に青赤並べて収録）
