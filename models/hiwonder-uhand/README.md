# Hiwonder uHand 再現（表示用）

Hiwonder の 5 本指ハンド uHand（LFD-01 サーボ 6 個）を写真から再現した形。印刷用ではない。

## 寸法の出し方

- サーボの底面（約 21 x 45mm）を物差しにして写真の画素を mm に換算した。実物の採寸ではない
- 手のひら・紺色の板の上端・指の付け根と長さは、正面の実物写真を逆算したカメラで板の面へ逆投影して読んだ（同じ写真のサーボが物差し）
- `silhouette.py` で写真とレンダーの黒い部分を重ね、IoU を見ながら合わせた（最終 0.674）

## 道具

```bash
# 5 方向のレンダー
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python models/hiwonder-uhand/render_views.py -- --out <dir>
# 写真と並べる（servo と back は右手の写真なので左右反転して並べる）
py -3.11 models/hiwonder-uhand/compare.py <dir> <out.png>
# 正面写真との輪郭の重なり
py -3.11 models/hiwonder-uhand/silhouette.py <dir>/front.png models/hiwonder-uhand/ref/ref_front.png <out.png>
```

## 写真と同じ画角で見比べる（2026-11-10）

写真の目印（サーボのねじ・紺の板のねじ・甲の板の角）とモデル上の同じ点から、写真を撮ったカメラを逆算して同じ画角で描く。

```bash
py -3.11 models/hiwonder-uhand/camfit.py front          # points/front.json → points/front_cam.json
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python models/hiwonder-uhand/render_views.py -- --out <dir> --views servo,front,back --fit
py -3.11 models/hiwonder-uhand/overlay.py <dir> <dir>   # 写真 / レンダー / 写真にレンダーの輪郭（赤）
```

- 目印がほぼ 1 平面に乗るので焦点距離は決まりにくい。`points/<view>.json` の `"f"` で固定している（servo・front 1300px、back 1100px）
- カメラは手でも合わせられる。`node server.js` のあと http://localhost:3000/viewer/uhand-camera.html を開き、
  写真に重ねたモデルを回して赤い点（モデル）を緑の点（写真）に重ね、「このカメラを保存」で `points/<view>_cam.json` が書き換わる
- servo と back は商品ページの写真で、指の付け根の板が黒い版。front は実物写真で紺の板。モデルは紺で作っている

## 参照写真

`ref/` は商品ページと実物写真のスクリーンショットから切り出したもので、公開リポジトリには入れていない（.gitignore）。
元のファイルは `C:\Users\kouga\Pictures\Screenshots\` の 2026-11-09 165824 / 165841 / 232714 / 234027。

## レビューの記録

Codex（gpt-6.1-sol）に 12 回採点させた。最高は 81 点。
同じ製品の写真どうしを同じ手順で採点させると 82 点だった。
レンダーと記録は `G:\マイドライブ\shubie\renders\hiwonder-uhand\` にある。
