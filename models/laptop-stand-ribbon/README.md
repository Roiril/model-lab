# 一体型リボンPCスタンド

受け面と下側の支えを連続した壁でつなぐ。
底を下にした使用姿勢のまま印刷する。
画像の形を参考にしている。寸法は実測値ではない。

## 形状と印刷

- 奥行きの基準280mm。高さの基準152mm。足幅の基準84mm。
- 上側の最小幅は24mm。受け面の傾きは約10度。前端は9mm立ち上がる。
- 側面には一つの貫通穴を設ける。穴の天井は左右の斜面が尖った頂点で交わる。
- 角度は造形面に垂直な方向から測る。水平な下面は90度になる。
- 底面を除いた下向き面は45度以下にする。設計には42度を用いる。
- 高い位置ほど幅を絞る。受け面だけが壁の上に張り出す形を避ける。

`exports/laptop-stand-ribbon.stl` が現在の一体モデル。座標単位はmm。
`exports/laptop-stand-ribbon.blend` はm単位の元データ。
ビューワー: http://localhost:3000/?model=laptop-stand-ribbon

分割や接着は不要。STLの底を造形台へ置く。
外形は幅84 × 奥行280 × 高さ152mm。
台の上で45度回すと245.265mm四方に収まる。
各側5mmのブリムを含めると255.265mm四方になる。
256mm角の台に収まるが、スライサー上の印刷禁止範囲は別途確認する。
穴の頂点を丸めると下向き面の角度が増えるため、頂点は尖らせる。
荷重試験と実際の印刷は未実施。
45度は材料と印刷設定に左右される目安なので、スライサーの積層表示も確認する。
参考: [Prusaの造形設計資料](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)

既存の `print/` と `large-bed/` および配布用ZIPは変更前の分割モデル。
現在の一体モデルの印刷には使用しない。

## 検証と再生成

外形と体積は `exports/laptop-stand-ribbon/build.json` に保存する。
STLを直接読み取る独立検査は `verification.json` に保存する。
辺の閉じ方と連結成分を検査する。下向き面の角度を全三角形で検査する。
造形台に置いたまま回転した場合の必要寸法も計算する。
空メッシュと開いた面を不合格にする。閉じた四面体を合格にする。
角度検査は42度と45度を合格にする。46度と89度を不合格にする。
自己交差の完全な検査と強度試験は含まれない。

2026-10-04の出力は29,580三角形。連結成分1。
非多様体辺0。向き不整合辺0。面積ゼロの三角形0。
最大の下向き角度41.091774度。45度超の面積0mm²。
底の最も薄い部分は12mm。体積937.360cm³。

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-ribbon/model.py
py -3.11 models/laptop-stand-ribbon/verify.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/laptop-stand-ribbon/render_preview.py
```

寸法は `params.py` で変更する。
ビューワーからの変更は `MODEL_PARAMS_JSON` で受け取る。
角度や閉じ方が不合格の場合は書き出しを止める。

## 縁の丸みと角度検査の記録

この拘束三角形分割の側面へBEVELを適用すると微小な面が折り返した。
床と穴頂点を除外した試行では最大51.556度。超過面積は0.000064mm²。
穴の輪郭全体を除外した試行でも最大56.761度。超過面積は0.000003mm²。
どちらも水密性は合格した。角度検査が書き出し前に止めた。
丸めを取り除いた出力は独立したSTL検査でも45度超の面が0枚になった。
印刷角度の制限がある場合は微小な面も検査する。微小であることを合格理由にしない。
