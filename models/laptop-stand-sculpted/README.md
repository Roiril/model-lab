# 画像を基準にした有機的なPCスタンド

元画像の前景左の大きな単体を主な基準にする。
`design/original.png` は元画像。`isolated.png` と `views-inferred.png` は画像生成による推定資料。
生成画像の裏面や上面を確定形状とは扱わない。実寸も画像からは決まらない。

## 造形方法

1. 外周と下部の穴を別々の周期三次Bスプラインで記録する。投影画像を側面図と取り違えない。
2. 曲線に囲まれた側面領域で `-Δu=1` を解く。境界は `u=0`。
3. 横方向の半幅を `h=W(y,z)√(u/(u+c))` とする。幅 `W` は足と肩へ滑らかに移す。
4. 輪郭と格子の距離を使った境界条件を入れる。格子の階段状の凹凸を減らす。
5. 格子を同じ順番の四面体へ分けて表面を抽出する。法線は外向きに再計算する。
6. 底面を平らにする。厚み5mmの上レールをEXACTで結合する。前端は6mm上向きに立ち上げる。

外周と穴を一点ずつ対応させる断面は使わない。C字の肩で対応が折れやすいため。
厚みの中心線へ距離を取る方法も使わない。複数の距離が切り替わる場所に筋が残るため。
輪郭の個別点を高自由度で最適化しない。輪郭の重なりだけが良くなっても曲面が波打つため。

`params.py` の長さはm。`POISSON_SHAPE_SCALE` だけは面積なのでm²。
`poisson_body.py` の数値計算はmm。メッシュ生成後にmへ戻す。
`fit_thickness.py` は幅と滑らかな輪郭補正の少数の値だけを調整する補助。
補助の近似値は合否に使わず `compare.py` の全STL三角形の投影を採用する。

## 最終寸法と検証

単体: 約37.5 × 291.9 × 151.0mm。左右の中心間隔200mm。
二本を配置した全体: 約237.5 × 291.9 × 151.0mm。
PCを置く高さ145mm。上面の幅24mm。レールの長さ227mm。厚み5mm。
これらは再現用に置いた寸法。写真の実測値ではない。

2026-10-04の出力STLを直接解析した結果:

- 単体は227,864三角形。一つの閉じた連結成分。非多様体辺0。面積ゼロの三角形0。
- 二本は455,728三角形。二つの連結成分。単体の体積275.48cm³。底面はZ=0。
- 1µmを超える交差深さの自己交差候補0。正常形状と故意の交差で検出を校正した。
- 0.5mmと0.25mmの計算間隔で胴体の体積差0.452%。最大横半幅差0.138mm。
- 平滑化の最大変位0.372mm。面数削減の標本最大変位0.011mm。
- 元画像の手動輪郭との重なり率（IoU）86.29%。縦横別の引き伸ばしは使わない。
- 輪郭間の平均距離5.93px。95パーセンタイル16.97px。元画像の大きさで測定。

輪郭は元画像を手で記録したもの。約3pxの読み取り誤差がある。
カメラは方位54°と仰角12°に固定する。比較時は同じ高さへ等倍縮尺で合わせる。
微小な位置合わせだけを許す。裏面の一致や実物の強度をこの数値から断定しない。
内周付近には格子由来の小さな陰影が残る。背面と横幅は推定。
これは形状再現のモデル。荷重試験と実機での滑り止め確認は未実施。

## 再実行

PowerShellでリポジトリ直下から実行する。BlenderのPython例外を終了コードへ反映する。

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-sculpted/model.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-sculpted/verify.py
py -3.11 models/laptop-stand-sculpted/convergence.py
py -3.11 models/laptop-stand-sculpted/compare.py --fixed
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-sculpted/render_preview.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-sculpted/render_preview.py -- studio
py -3.11 models/laptop-stand-sculpted/build_report.py
```

`exports/laptop-stand-sculpted-unit.stl` が単体。`exports/laptop-stand-sculpted.stl` が二本。
設計資料は `exports/laptop-stand-sculpted/design-report.html`。画像を埋め込んだ単一HTML。
ビューワー: http://localhost:3000/?model=laptop-stand-sculpted
`qa_browser.cjs` はPlaywrightを使う。既存のCodex同梱ライブラリで実行できる。
