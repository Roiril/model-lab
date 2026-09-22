# 手すりのM字と90度カーブ

2026-09-22 改良。M字の先端の絞りを廃止し、両端の外角を小さく丸めた。
カーブの下面を円の接線と平底へ整理した。穴と芯線は維持している。

## 配置と寸法

- M字は脚2本を160mm間隔で受ける。レールは中央と左右の3本。
- 左右レールの高さは中央レールから62.3mm。レール内径28.6mm。脚穴28.9mm。
- 角の脚は `(-74.7,0),(-234.7,0),(0,-74.7),(0,-234.7)` mm。
- カーブは内側R25と外側R185。同心の中心は `(-49.7,-49.7)` mm。
- 中央レールと5本目の接続は既存の市販継手の参照形状を維持する。
- 内側カーブの口はM字の端面に着座する。外側には従来どおり1.5mmの目地を残す。

各口に丸めた短い舌を2本設けた。M字側の受けは深さ6mm。
舌の断面は2.3×4mm。片側の隙間0.25mm。内側は5.3mm、外側は4mm入る。
受けとパイプ穴の間には半径方向に1.2mmの肉を残す。
外側は目地が0.3mmまで狭まっても、受けの奥に0.8mmの余裕がある。
舌は位置決め専用。ロックは設けず、組み立て後に外周へテープを巻く。

## 組み立て順

1. 脚へ載せる前に、片方のM字へ内外のカーブを差し込む。
2. もう片方のM字を、カーブの空いている2つの口へ同じ方向から差し込む。
3. 水平パイプをM字の外側から通す。内側の端面と外側の目地を確認し、テープを巻く。
4. 上部をまとめて脚パイプへ載せる。中央の市販継手は既存の組み方に従う。

M字を両方とも脚へ固定した後では、直交する2つの口にカーブを同時に差し込めない。
先に上部を組む前提は、従来のパイプ差し込み構造と共通。

## 印刷ファイル

| ファイル | 個数 | 印刷時の外形 W×D×H mm |
|---|---:|---:|
| `exports/pipe-joint-refined.3mf` | 2 | 106.10×196.60×54.00 |
| `exports/pipe-corner-inner-refined.3mf` | 1 | 78.60×78.60×35.60 |
| `exports/pipe-corner-outer-refined.3mf` | 1 | 237.30×237.30×35.60 |

M字は-X端を下にした向きを3MFへ格納する。カーブは平底を下へ置く。
カーブの舌の下面だけに局所サポートを付ける。
3MFは形状と向きのみ。材料と壁数などのスライサー設定は含まない。
受けの短い橋渡し部分と丸めた底の造形はスライス画面で確認する。
表示用の `pipe_foot_corner_split_asm.stl` は印刷しない。

カーブ本体の幅と高さは変更していない。部品の外形に増えた長さは、
M字の内側に入る舌の分。組み上げたときのパイプ間隔と角の位置は従来どおり。

## 再生成と検査

Blender 5.1で順に実行する。

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/pipe-joint/model.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/pipe-corner/model.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/pipe-corner/validate.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/pipe-foot-corner-split/asm.py
```

検査結果は `exports/pipe-handrail-validation.json`。
STLを自前で解析し、閉じたメッシュであることと面の重複がないことを確かめる。
穴径と座面を実メッシュから測定する。
エルボの穴は従来の多角形を維持するため、水平方向の実測は約28.583mm。
設計内径28.6mmとの差は円の分割によるもの。

干渉は頂点と三角形中心を相互に検査する。許容0.001mm。
接触面のBoolean演算は同一平面で不安定になるため、3方向の交差回数も使って内外を判定する。
故意に2mm食い込ませた部品が検出されることも確認する。
この検査は連続した組立動作全体の保証でも、荷重の検証でもない。
実物の嵌合と手すりとしての耐荷重は未検証。

既存モデルに合わせ、寸法定義はmm。形状生成時に0.001を掛けてmへ変換する。
