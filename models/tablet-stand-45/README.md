# Redmi Pad SE 45度スタンド

2026-10-30改修。細いフレーム版の印刷失敗を受け、全面の台座と厚い左右の支えへ変更した。
Redmi Pad SE 11インチの裸本体を横向きに置く。一体印刷で組み立ては不要。
45度の傾きと中央の開いた受け口は維持した。三角窓の輪郭と台座の丸みを揃えた。

## 変更した寸法

| 項目 | 失敗したフレーム版 | 補強版 |
|---|---:|---:|
| 外形 W × D × H | 180 × 210 × 119.96 mm | 212 × 220 × 121.65 mm |
| 左右の支え幅 | 各18 mm | 各28 mm |
| 底の厚さ | 4 mmの枠 | 6 mmの全面台座 |
| 床との接地面積 | 102.56 cm² | 465.16 cm²（4.54倍） |
| 背面支えの実測断面厚さの最小値 | 約5 mm | 36.06 mm（指定位置の光線測定） |
| 後脚の実測断面厚さの最小値 | 約6 mm | 29.01 mm（指定位置の光線測定） |
| 返しの厚さ | 3.2 mm | 4 mm |
| 台座の平面の角丸 | ― | 半径12 mm |

三角窓は高さ66 mm以下で閉じる。窓の上を厚い肉でつなぎ、印刷途中の独立した支柱を短くした。
窓の斜面は45度。頂部の丸みによる短い橋渡しのY方向幅は約1.13 mm。
寸法の正本は `params.py`。接地面は平らで、底の縁を丸めて面積を削らない。
追加の側面面取りはBoolean後に微小面を生じたため外した。受け口と外周の丸みは輪郭に持たせてある。

本体寸法は255.53 × 167.08 × 7.36 mm、478 g。受け口は9.2 mm。
寸法の出典は[Xiaomi公式仕様](https://www.mi.com/jp/product/redmi-pad-se/specs/)。
既存の背面保護材0.8 mmを想定しても厚さ方向に1.04 mm余る。ケース付きの適合は未確認。

## 印刷ファイル

`prints/tablet-stand-45/` に次の4ファイルを置く。

- `tablet-stand-45-PLA.gcode.3mf`：X1C用PLA。370.92 g、23時間21分45秒。
- `tablet-stand-45-PETG.gcode.3mf`：X1C用PETG。356.72 g、23時間23分58秒。
- `tablet-stand-45-layout.3mf`：スライス前の配置。別のプリンタや銘柄へ設定を変える場合はこちら。
- `tablet-stand-45.stl`：平らな台座を下にした単一部品。単位mm。

X1 Carbon・0.4 mmノズル・Textured PEI Plate・0.20 mm層でスライス済み。
材料プロファイルはBambu PLA Basic / Bambu PETG Basic。異なる材料銘柄では再スライスする。
外周4周、上下面5層、18%ジャイロイド充填。サポートなし、外側ブリム8 mm。
外周40 mm/s、内周65 mm/s、通常加速度1000 mm/s²。継ぎ目は後ろへ寄せる。
100%充填は使わない。形状の体積759.36 cm³とフィラメント量は異なる。
部品はX=28..240、Y=18..238 mmへ配置。ブリム込みでも256 mmベッドと左前の除外域に干渉しない。

## 確認したことと未確認のこと

- STLは連結した一部品。非多様体エッジ0、零面積の三角形0。
- 本体と従来の保護材を想定した16,968点で、真上50 mmの取り外し経路に干渉なし。
- PLA / PETGとも608層。保存された材料設定・印刷設定・配置を3mfから再読込して照合した。
- G-codeの外周に下層の支えがない押し出しは両材料とも0 mm。既存の共有計器を使用。
- 内部充填の上のブリッジは別集計。外周の支持不足0はベッド定着や材料強度の保証ではない。
- PETGのスライス重量356.72 gを使用した剛体計算では、画面を垂直に押した際の後方転倒は約25.13 N、横転は約32.23 N。

転倒計算は平らな机と台座の平面接触を仮定する。重心は均一密度からの推定に後方10 mmの誤差を見込む。
10 Nの押下に対し滑りに1.5倍の余裕を持たせるには摩擦係数約0.70が必要。机との摩擦は未測定。
接地面積を広げても滑らないとは限らない。追加の接着具を前提にした設計ではない。
物理的な再印刷は未実施。前回の失敗箇所が不明なため、スパゲッティの原因確定と再発防止の保証はできない。
最初の層の密着、台座の反り、窓の頂部、上端付近の揺れの順で実物を確認する。
プレートの洗浄と第一層の確認は[Prusaの失敗対策](https://help.prusa3d.com/article/spaghetti-monster_1999)も参照。

## 再生成

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/tablet-stand-45/model.py
py -3.11 models/tablet-stand-45/plate.py
py -3.11 models/tablet-stand-45/verify.py --stand-mass 0.35672
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/tablet-stand-45/render_preview.py
node tools/catalog.js check
```

`--stand-mass` はkg単位。印刷後は実測重量へ置き換える。満充填の体積から重量を仮定しない。
検証出力・ログ・比較用の旧版画像は `G:\マイドライブ\shubie\renders\2026-10-30_redmi-stand\` に保存。
`slice_report.json` に両材料の重量・時間・配置・押し出し検査を記録する。
`verification.json` に形状・取り外し経路・接地面積・転倒計算を記録する。
`stand.png`、`in-use.png`、`side.png`、`underside.png`、`print.png` が今回の外観画像。

Studio: http://localhost:3000/?model=tablet-stand-45
生成画像は確認済み。Computer Useのアプリ承認がタイムアウトしたため、実ブラウザの描画は未確認。
