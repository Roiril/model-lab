# ガイスター (Geister) — 一式（盤 + コマ）

ボードゲーム「ガイスター」の盤とコマ16体を、実ゲームの開始配置で 1 つの GLB に
まとめたセット。他ゲームと同様、盤・コマを個別に作り、このセットで合体させる。

- 盤: [models/geister](../geister/) の `geister.glb`
- コマ: [models/geister-ghost](../geister-ghost/) の `ghost_blue.glb` / `ghost_red.glb`

## パイプライン

`build_set.py` は造形をせず、**書き出し済みの GLB を読み込んで配置するだけ**
（盤・コマの形はそれぞれのモデル側が正）。

```
build_set.py   geister.glb（盤）＋ ghost_blue/red.glb（コマ）を読み込み
               → 開始配置に並べて exports/geister-set/geister-set.glb を出力
```

実行（model-lab ルートで。先に盤とコマをビルドしておくこと）:

```bash
./run.sh models/geister/build_glb.py          # 盤
./run.sh models/geister-ghost/build_glb.py    # コマ（単体GLBが要る）
./run.sh models/geister-set/build_set.py      # 一式に合体
```

## 閲覧

```bash
node server.js
# → http://localhost:3000/viewer/geister-set.html
```

## 配置メモ

- 盤は 6×6・65mm 角マス。開始配置は実ゲームどおり **中央 4 列 × 各陣 2 段 = 8 マス**
  （四隅の脱出マス＝矢印は空ける）
- 手前プレイヤー = **青 8 体**（マーカーが手前＝自陣向き）
- 奥プレイヤー = **赤 8 体**（180°回転。顔が手前＝相手向き、マーカーは奥）
- コマはメッシュ共有のリンク複製 + テクスチャ JPEG 埋め込みで、盤込み約 2.3MB
- 単位はメートル（Unity 1 unit = 1m）

## 既知の制限・TODO

- 実ゲームは各プレイヤーが青4+赤4を混ぜて配置するが、ここでは色でチームを分けた
  分かりやすい展示配置にしている（青チーム vs 赤チーム）
- コマの底は盤上面 z=2mm にぴったり接地（めり込み・浮きなし）
