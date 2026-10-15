# v2-A 共通取付の実測

候補: `build/v2-mount-interface.json`。interface.json本体と骨格はこの作業では変更していません。
面固有の支持・サーボ座・駆動部は保持し、sector_flagの共通キー掃引だけをloft断面頂点へ対応しました。

## メッシュと経路

実行: `blender.exe --background --python-exit-code 1 --python models/mystery-box-sg92r-f1/build/v2-mount-probe.py`
終了コード0。最終行 `V2_MOUNT_PROBE_PASS`。

- blank/template/link_lid/three_pixels/sector_flagのpanel/key_l/key_r、計15メッシュは全てtopology pass・連結成分1。
- キーは各272.502mm3。Rx180、d=8mmを床にした接地39mm2、接地短辺3mm、高さ8mm、高さ/短辺2.667。
- blank/link_lid/three_pixels/sector_flagの左右キーについて、40mm挿入161姿勢と解除から固定への回転21姿勢を測定。全1456姿勢で面板との共通体積0mm3。
- 数値は既存meshcheckおよびsolid_meterで取得。全モデルの認証ゲートの代替ではありません。
- receiver自体のoperationsを全5readerへ対応。`v2-mount-reader-check.py` は終了コード0、最終行 `V2_NESTED_RECEIVER_READERS_PASS`。frame候補の左右latchを各readerで生成した10個ともtopology pass・1成分・体積164.70626484mm3で、凹み差分の実在を確認しました。

## 実スライス

`py -3.11 models/mystery-box-sg92r-f1/build/v2-mount-slice.py --common-only`: 終了コード0。
X1C 0.4、Textured PEI、0.20mm Standard、PLA、壁2、充填15%、補正0.15mm、サポート無し。
プロファイルは既存plate.py経由でbambu_profiles.resolveを使用。計器と閾値は未変更です。

| 部品 | 外側の未支持押出しmm | 閾値2mm以内 |
|---|---:|---|
| blank/key_l | 0.00 | 合格 |
| blank/key_r | 0.00 | 合格 |
| blank/panel | 1.87 | 合格 |
| three_pixels/panel | 1.87 | 合格 |
| sector_flag/panel | 1.87 | 合格 |

面固有の残存を含む `py -3.11 models/mystery-box-sg92r-f1/build/v2-mount-slice.py` は終了コード1。
link_lid/panelは28.79mmで不合格です。z=2.0mm/2.4mmの面固有の屋根を変更していません。
共通の指掛けに由来するz=0.6mmの1.87mmは他面と同じです。
全6部品のスライスは6076秒、60.09g、support=falseです。印刷時間と重量はBambuの予測です。

## 判断と未確認

- 指掛けはu=±36/v=-22mm、2×2mm、深さ0.95mmの全側45°くぼみ。終端0.1×0.1mmで頂点重複を避けます。
- 4×7mmのV断面は新生薄壁で17.32mm、単純貫通は11.91mm、元の浅いくぼみは25.96mmでした。
- 2×2mmくぼみの1.87mmは既存基準2mm以内。実測0mmと表記しません。
- 頭外端u=34.8mm、頭穴外端35.0mm、くぼみ開始35.0mm。爪先で外縁を内側へ押して解除する想定です。操作感と20回着脱、10N保持は未確認です。
- 頭の遊び0.2mmと爪の遊び0.25mmの直列合計0.45mm。ばね自由長18mm、厚1.6mm、変位0.6mm、計算ひずみ0.4444%を保持。
- 骨格受けとの整合・他面を含む全モデル認証は親の統合作業で実行します。

## 保存先

検証ログと実測JSONは `G:/マイドライブ/shubie/reports/` の `mystery-box-sg92r-f1-v2-mount*`。
最終ログは `mystery-box-sg92r-f1-v2-mount-final-probe.log`、`mystery-box-sg92r-f1-v2-mount-final-slice.log`、`mystery-box-sg92r-f1-v2-mount-common-slice.log`。
receiver reader追加検証は `mystery-box-sg92r-f1-v2-mount-reader-check-final.log`。
共通部だけの実測JSONは `mystery-box-sg92r-f1-v2-mount-common-slice.json`。
作業中のSTLと3mfは `build/v2-mount-probe/` と `build/v2-mount-slice/` に置いています。
