# Redmi Pad SE スタンド（横置き・60度・一体）

2026-11-14 に作り直した Redmi Pad SE 11 インチ用のスタンド。横置き専用。旧版 `tablet-stand-45` の形にはよらない。
材料の量は問わない依頼なので、使いやすさ・置きやすさ・倒れにくさ・刷りやすさ・見た目を優先した。
穴・溝・窓は無い。

## 形

側面の輪郭を左右へ押し出した一体の塊。部品は 1 つで、組み立ては無い。

- 画面は机から 60°。動画や閲覧で座った目線に向く角度
- 前の返しは丸い先端。受け口は 12mm と広く、上から落とすだけで入る
- 背面の支えは本体の下端から 97mm。本体の高さの 58% を受ける
- 頂部から後ろへ凹んだ曲面で下り、薄い尾が奥まで伸びる。尾が後ろへ倒れるのを止める
- 左右の面は上へ向けてすぼめてある（机で 150mm、頂部で 132mm）。上の縁は半径 4mm で丸め、机に接する下の縁は直角
- 幅 150mm は本体 255mm の中央だけを受ける。両端のスピーカーと USB-C はふさがない

## 寸法

| 項目 | 値 |
|---|---:|
| 外形 W × D × H | 150 × 192 × 108.6 mm |
| 机に接する面積 | 287.9 cm² |
| 画面の傾き | 60°（机から） |
| 受け口の幅 | 12.0 mm（支えに垂直）。裸の本体 7.36 mm、ケース込み 11.5 mm まで |
| 返しの高さ | 6.0 mm（支えに沿って）。額縁 9.5 mm の内側 |
| 本体の下端の高さ | 20 mm |

本体の寸法は [Xiaomi 公式仕様](https://www.mi.com/jp/product/redmi-pad-se/specs/)（255.53 × 167.08 × 7.36 mm、478 g）。
額縁の幅は 11 インチ 16:10 の表示域 236.8 × 148.0 mm からの推定。寸法の正本は `params.py`。

## 刷り方

`prints/redmi-pad-stand/` に置いてある。

- `redmi-pad-stand-PLA.gcode.3mf`：X1C 用 PLA。583.01 g、18 時間 46 分
- `redmi-pad-stand-PETG.gcode.3mf`：X1C 用 PETG。560.68 g、19 時間 14 分
- `redmi-pad-stand-layout.3mf`：スライス前の配置。別の設定で切り直すときはこれ
- `redmi-pad-stand.stl`：単位 mm、机に接する面が下

使っているときと同じ向き（底面を下）で刷る。サポートは要らない（45° を超えて下を向く面は 0 mm²）。
X1C 0.4mm・Textured PEI・0.20mm Standard。外周 4 周（外側 80 mm/s）、上面 6 層・下面 5 層、充填 30% ジャイロイド。
重いほど倒れにくいので充填を多めにした。外側にブリム 5 mm。

## 確かめたこと

`py -3.11 models/redmi-pad-stand/verify.py --stand-mass 0.56068` が出す（PETG の重量で計算）。

- メッシュは閉じた一体。非多様体の辺 0、面積 0 の三角形 0
- 計器の校正: 上下を反転した形は張り出し 11,915 mm² を検出し、2 mm 沈めた本体は 2.0 mm の食い込みを検出した。その上で本番は張り出し 0、食い込み 0
- 本体の断面（角の丸み 1 mm と仮定）が受け口に当たらず、40 mm 持ち上げるまで引っかからない。11.5 mm のケース込みでも当たらない
- 返しが画面を隠す量: 画面に正対して 6.0 mm、目が法線より 15° 低くて 9.05 mm（額縁 9.54 mm より内側）
- 画面に垂直に押して後ろへ浮き始める力: 上端で 10.2 N、画面中央で 46.3 N
- 上端を押して滑るより先に倒れるには、机との摩擦係数が 1.75 以上要る。普通の机では倒れる前に滑る
- スライスした G-code で、下に支えの無い外周は PLA・PETG とも 0 mm

転倒はスタンドを均一な密度とみなした重心で計算した。実物の重心は充填でずれる。

## 実物で確かめること

1. 最初の層の密着と、台の四隅の反り
2. 本体を落とし込んだときの入りやすさと、受け口のがたつき
3. ケースを付けたまま入るか（11.5 mm まで）
4. 机の上で押したときに滑らないか

合わないときに変える `params.py` の定数:

- 角度: `ANGLE_DEG`（45〜75）
- ケースが入らない: `GROOVE_MM`（1 mm 刻み）
- 画面の下端が隠れる: `LIP_H_MM`（0.5 mm 刻みで下げる）
- 滑る・倒れる: `DEPTH_MM` を伸ばすか、スライスの充填を上げる

## 再生成

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/redmi-pad-stand/model.py
py -3.11 models/redmi-pad-stand/plate.py
py -3.11 models/redmi-pad-stand/verify.py --stand-mass 0.56068
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/redmi-pad-stand/render_preview.py
node tools/catalog.js check
```

描画・検証・スライスの出力は `G:\マイドライブ\shubie\renders\2026-11-14_redmi-pad-stand\`。
`stand.png` `front.png` `rear.png` `side.png` `in-use.png` `in-use-side.png` が外観、
`verification.json` が検証、`slice_report.json` がスライスの記録。

Studio: http://localhost:3000/?model=redmi-pad-stand
