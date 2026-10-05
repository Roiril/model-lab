# 曲面を残した一体型リボンPCスタンド

元の有機的な胴体と細い受け面を保つ。
肩だけを曲面でつなぎ直す。受け面の下の空間と下側の穴は残す。
画像を参考にした形状。寸法は実測値ではない。

## 形状

- 外形は幅84.994 × 奥行279.000 × 高さ150.892mm。
- 受け面の設計幅24mm。設計厚6mm。先端の立ち上がり9mm。
- 肩の接続体は胴の内部から始める。奥行52mm位置で受け面へ接線を合わせる。
- 受け面の丸い後端を接続体の内部へ埋める。
- 0.45mmの解像度で表面を再構成する。肩周辺だけを平滑化する。
- 体積576.830cm³。変更前の曲面モデル577.030cm³に対する比は0.99965。

`exports/laptop-stand-ribbon.stl` は両側が曲面のモデル。座標単位はmm。
`exports/laptop-stand-ribbon.blend` はm単位。
ビューワー: http://localhost:3000/?model=laptop-stand-ribbon

このモデルを使用姿勢のまま印刷すると最大89.890度の下向き面がある。
直立姿勢で45度以内にするための全面壁化は採用しない。
サポートを使わずに45度以内へ収める版は次のSTLを用いる。

## 横置きで印刷する一体版

`export_onepiece.py` が片側平面の一体版を作る。
中心で切った片側を幅方向へ2倍にする。
幅を維持して反対側の曲面を残す。分割と接着は不要。

片側は平らになる。受け面は平らな側へ寄る。
両側曲面モデルとは断面が異なる。外形は同じ約85 × 279 × 151mm。
受け面の設計厚6mmと先端の立ち上がり9mmを維持する。
体積は元モデルの1.000055倍。実物の荷重試験は未実施。

| ファイル | 用途 | 使用時の外形 W × D × H |
|---|---|---|
| `onepiece/usage-full.stl` | 片側平面の形の確認 | 84.996 × 279.000 × 150.892mm |
| `onepiece/print-full.stl` | 原寸の一体印刷 | 84.996 × 279.000 × 150.892mm |
| `onepiece/print-256.stl` | 256mm角用の縮小印刷 | 75.491 × 247.799 × 134.017mm |

上表のパスは `exports/laptop-stand-ribbon/` からの相対パス。
印刷用のSTLは平らな側面が造形台に接する向きへ回転済み。
原寸版の印刷時寸法は276.975 × 276.828 × 84.996mm。
5mmのブリム込みで286.975mm四方を必要とする。
256mm角版は88.817%へ縮小する。設計厚は約5.329mmになる。
印刷時寸法246.000 × 245.870 × 75.491mm。5mmのブリム込みで256.000mm四方。
スライサーの印刷禁止範囲は別に確認する。

角度は造形台に垂直な方向から測る。水平な下面は90度。
接地面を除いた下向き面の最大角度は原寸版3.150度。縮小版3.150度。
45度超の面は両方とも0枚。超過面積0mm²。
原寸版の平らな接地面は14,837.918mm²。
横置きによって肩から受け面までが同じ高さで印刷される。
曲面を保つ代わりに片側を平面とする判断を採用した。
実際の印刷とスライサーでの積層確認は未実施。

既存の `print/` と `large-bed/` と配布用ZIPは変更前の分割モデル。
今回の一体モデルの印刷には使用しない。

## 再生成と検証

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-ribbon/model.py
py -3.11 models/laptop-stand-ribbon/verify.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-ribbon/export_onepiece.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-ribbon/render_preview.py
```

`build.json` に生成結果を保存する。
`verification.json` に元STLの閉じ方と寸法の検査結果を保存する。
元STLの直立印刷判定は `print_ready_upright: false`。
印刷用STLは角度検査を必須にする。45度超なら生成を失敗させる。
`onepiece/verification.json` に入力STLの指紋と印刷版の独立検査を保存する。
原寸版は546,100三角形。連結成分1。非多様体辺0。向き不整合辺0。面積ゼロの面0。

検査器は空メッシュと開いた面を拒否する。閉じた四面体を受け入れる。
42度と45度を合格にする。46度と89度を不合格にする。
閉じていても45度を超える張り出しを持つ形状は印刷用検査で拒否する。
自己交差の完全な検査と強度試験は含まれない。
寸法調整後は印刷用STLも再生成する。

## 微小面の検査記録

以前の全面壁形状へBEVELを適用した際、微小な面が折り返した。
51.556度と56.761度の超過面が出た。水密性は合格したが角度検査で止めた。
面が微小でも45度超を合格にしない。
