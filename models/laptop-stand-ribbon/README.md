# 曲面の構成から作ったPCスタンド

`reference.png` の形を参考にした新規モデル。
画像から寸法や荷重性能は確定できない。数値は形を確認するために設定した。

## 形の考え方

- 上面は細い直線にする。厚い本体との違いを残す。
- 後ろの丸い肩から前の低い足へ、厚い面を一続きにする。
- 後ろの短い支えと底をつなぐ。その内側を低い涙滴状の穴にする。
- 足を横に広げる。肩と途中の幅は絞る。
- 接地面は平らにする。先端だけ短く上へ返す。

これは輪郭点の最適化ではなく、少数の曲面区間から構成する方法。
胴体に細い上面を含めず、肩・後ろの支え・底・斜面の順に区間を対応させる。
外周と穴を周期三次Bスプラインで補間する。
対応する二曲線間を楕円断面でつなぐ。幅を区間ごとに変える。
投影した面の向きが反転した場合は生成を止める。
Subdivisionで整えた後に接地面を切る。上面はEXACTで結合する。

## 出力と寸法

- `exports/laptop-stand-ribbon.stl`: 単体。STLの座標はmm。
- `exports/laptop-stand-ribbon.blend`: 元のm単位の立体。
- 外形: 幅84.922 × 奥行き278.965 × 高さ150.966mm。
- 上面: 幅24mm。公称厚み6mm。傾き約10°。
- 先端の立ち上がり: 9mm。
- はめ込み部品なし。一体の形状試作。荷重試験は未実施。

ビューワー: http://localhost:3000/?model=laptop-stand-ribbon
Blenderのwatch.pyを使う場合は `MODEL = "laptop-stand-ribbon"` に変更して再実行する。

## 検証

2026-10-04のSTLを自前パースした結果:
88,492三角形。一つの連結成分。非多様体辺0。向き不整合辺0。面積ゼロの三角形0。
体積602.524cm³。底のZ座標0mm。平坦な接地面の面積10,607.709mm²。
空メッシュと開いた三角形を不合格にする。閉じた四面体を合格にして検査を校正する。
検査結果は `exports/laptop-stand-ribbon/verification.json`。
自己交差の完全な検査と荷重試験は、この検査に含まれない。

## 再生成

リポジトリ直下のPowerShellで実行する。

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-ribbon/model.py
py -3.11 models/laptop-stand-ribbon/verify.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-ribbon/render_preview.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-ribbon/render_preview.py -- studio
py -3.11 models/laptop-stand-ribbon/build_preview.py
```

`params.py` の寸法を変えて再生成する。
ビューワー経由の寸法変更も `MODEL_PARAMS_JSON` から受け取る。
別セッションの既存モデルとビューワーのコードは変更しない。
