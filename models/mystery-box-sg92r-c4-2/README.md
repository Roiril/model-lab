# 住人の箱 C4-2・凹む六角格子

外形は110 × 110 × 110mm。19枚の六角環のうち四つの群が4mm沈む。旧モデルID `mystery-box-sg92r-c4` はC4-1として残す。

| 選択 | サーボ角 | 沈むセル |
|---|---:|---:|
| 平面 | 15° | 0 |
| 左上 | 50° | 3 |
| 中央 | 90° | 1 |
| 右上 | 130° | 3 |
| 下側の二か所 | 165° | 6 |

切り替え途中は二つの凹みが滑らかに入れ替わる。指で押した入力は検出しない。天面上向き専用。電源を切った後の位置は保証しない。

## 部品表

| 印刷部品 | 数 | 印刷の向き |
|---|---:|---|
| 外装 housing | 1 | 下端をベッドへ |
| 六角格子の天板 faceplate | 1 | 見える天面をベッドへ |
| 案内枠 guide_frame | 1 | build/print_guide_frame.stlの向き |
| 底板 bottom | 1 | 外側の底面をベッドへ |
| 中央 carrier_center | 1 | 見える六角面をベッドへ |
| 左上 carrier_upper_left | 1 | 見える六角面をベッドへ |
| 右上 carrier_upper_right | 1 | 見える六角面をベッドへ |
| 下側 carrier_lower_pair | 1 | 見える六角面をベッドへ |
| 四群円盤カム cam_disk | 1 | 平らな円盤下面をベッドへ |
| ホーン受け horn_coupler | 1 | 上面をベッドへ |
| 角形駆動キー drive_key | 1 | build/print_drive_key.stlの向き |
| 円盤止め輪 cam_keeper | 1 | build/print_cam_keeper.stlの向き |
| ホーン受け・キー・案内・接点・止め爪・円形案内の試片 print_test | 9点 | 納品STLの向き |

既製部品はSG92R 1台と付属ホーン。正本は `models/sg92r-photo/`。付属ホーンのスプラインを造形部品で置き換えない。制御用マイコンと外部の安定化4.8V電源が必要。SG92RとマイコンのGNDを共通にする。信号線はデモのD9へつなぐ。

`prints/mystery-box-sg92r-c4-2/` に13個の部品STLと4個の配置3MFを置く。本体は3プレート。試片は別プレート。スライスはユーザーがBambu Studioで行う。印刷時間と材料量と印刷経路は未検証。配置の正本は `build/delivery_report.json`。

外装と案内枠のSTLには印刷用の支えを含む。四つの可動部にも梁を支える形状を含む。製品との公称面間隔は部位ごとに設定する。寸法の正本は `build/manifest.json`。実STLによる測定は `build/print_support_geometry.json`。スライス後の材料面の隙間と初層の接地はBambu Studioで確認する。印刷後に薄いへらで支えを外す。取り外す力と表面の傷は実物未確認。

## 組み立て

表示の正本は `build/assembly.json`。同じ変換列を使った累積組立と逆分解の検査は `build/assembly_report.json`。工程の順番はその表示に従う。

1. 箱の外で付属ホーンをホーン受けへ入れる。この一式を底側の+X寄りから所定高さへ上げる。中央へ移す。
2. 配線の自由端を+X側の出口へ通す。
3. 箱の外でホーン未装着のSG92Rを起動する。90°で静止させる。
4. SG92R本体を下側から案内へ入れる。出力軸を先に入れた付属ホーンへ差す。スプラインの嵌まりは実物で確認する。
5. 円盤を外周の支持環へ載せる。円盤の角穴を受けの盲穴へ合わせる。
6. 円盤の上から角キーを入れる。円盤止め輪を押し込む。
7. 駆動一式を15°へ戻す。
8. 箱の上で案内枠へ四群の格子を通す。組んだ一式を箱へ下ろす。
9. 天板を付ける。底板を閉じる。

案内枠は外装の四隅の棚へ直接載せる。対角二か所のL字の壁が横ずれを止める。片側の遊びは0.2mm。天板裏の四本の柱が上方向を0.3mmで止める。柱から天板の爪を通して外装へ保持力を伝える。案内枠だけを箱へ入れた段階では上方向の保持は完成していない。

SG92R本体のX両端は底板の壁で止める。底板の爪を通して外装へ保持力を伝える。Y両側と取付耳上方は外装で止める。底板を閉じるまで本体の保持は完成していない。

底板の爪は配線出口と別の二面へ置く。底板の下方遊びは0.2mm。本体から底板までの0.35mmと合わせると、本体の下方遊びは最大0.55mm。天板の爪は上側の受け面へ直接掛ける。円盤止め輪の四つの爪は支柱を避けて45度ずらす。爪厚は1.2mm。最大撓みは0.5mm。材料の保持力は実物未確認。

分解は表示工程の逆順。爪の押し方と保持力は実物で確かめる。無理に引き抜かない。

接触足の厚さは4.8mm。足の上の角形案内棒の下端は55.9mm。4mm下降した状態で51.9mmとなる。カムの谷の外の平面51.3mmから0.6mm離す。斜めの位置にある角棒は径方向の幅がトラックより広いため、接触足だけの照合とは別に全形状の干渉を調べる。

足の径方向幅は2.0mm。周方向長さは2.4mm。案内の角穴は3.6mm。斜めの位置でも足の通過余裕が片側0.2mm以上になるよう実STLを測る。接触面の摩耗は実物で確かめる。

## デモ

`demo/demo.ino` はArduinoのServoライブラリを使用。起動時は90°。組み立て前に起動する。シリアルモニターは115200bps。

| コマンド | 動作 |
|---|---|
| h | 平面へ戻す |
| 1 / 2 / 3 / 4 | 左上 / 中央 / 右上 / 下側 |
| c | 組み立て用の90°へ |
| g | 五つの位置を順番に再生 |
| s | 現在の指令角で停止 |

切り替えは3秒。連続再生の停止時間は1.6秒。位置や押す力のフィードバックは無い。Arduino Uno向けの実コンパイルは合格。書き込みとSG92R通電は未実施。

付属ホーンの装着位相は実物で調整する。`PHASE_TRIM_DEG` の初期値は0°。四つの停止位置で4mmの凹みを実測する。十分沈む角度の区間の中央へ合わせる。補正は1°ずつ変えて再コンパイルする。同じ補正を組立角とホーム角にも加えるため、停止位置の間隔は変わらない。許容補正は±10°。超える場合はホーンの取付け向きを確かめて組み直す。補正後の指令角は5〜175°以内。5停止位置の接触と擦れは実物で再確認する。

Arduino CLI 1.5.1 / arduino:avr 1.8.8 / Servo 1.3.0で確認した。Flashは5128 / 32256 bytes。RAMは272 / 2048 bytes。補正±10°のコンパイルは通る。±11°は範囲外の診断で止まる。正本のSHAと実出力は `build/demo_compile_report.json` に記録する。公式CLIはD配下へ隔離した。既存PATHとArduino設定は変更していない。

コンパイルしたHEXは `build/demo.ino.hex`。標準出力と標準エラーは `build/demo_compile_stdout.txt` と `build/demo_compile_stderr.txt` に保存する。

再コンパイルの検査は `compile_demo.py`。既存の公式Arduino CLIと隔離した設定ファイルを渡す。`--cli` と `--config` と `--work-directory` の3引数を指定する。境界4例を先にコンパイルする。正本のHEXと実出力を保存する。マイコンへ書き込まない。

## 試し刷りと調整

試片で付属ホーンの向きを先に確認する。ホーン受けがきつければ `HORN_CLR` を片側0.05mmずつ増やす。角キーがきつければ `KEY_SOCKET_FLAT` を0.1mmずつ増やす。増やすと回転遊びも増える。駆動と高さ幅を再検証する。

次に円盤止め輪を刷る。爪の白化と割れを調べる。案内がきつければ `GUIDE_CLR` を片側0.05mmずつ増やす。爪の変形量は `KEEPER_TAB_DEFLECTION`。厚さは `KEEPER_TAB_T`。自由長は `KEEPER_TAB_FREE_L`。寸法変更後に同じ検査を再実行する。

中央の円形案内は半径10mmのカムを内半径10.2mmの穴で保持する。径方向の遊びは0.2mm。格子の案内は片側0.2mm。トラック幅3.6mmに接点幅2.0mmを組み合わせる。案内の隙間を増やすと接点がトラック端へ近づくため、径方向の保持と接点の余裕も再検証する。

## 再生成

PowerShellでリポジトリのルートから実行する。BlenderとBambu Studioの一時ファイル置き場には空き領域のある場所を使う。

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/sg92r-photo/model.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/mystery-box-sg92r-c4-2/model.py
py -3.11 models/mystery-box-sg92r-c4-2/print_delivery.py --layout-only
py -3.11 models/mystery-box-sg92r-c4-2/boolean_evidence.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/mystery-box-sg92r-c4-2/print_support_geometry.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/mystery-box-sg92r-c4-2/drive.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/mystery-box-sg92r-c4-2/assembly.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/mystery-box-sg92r-c4-2/verify.py
py -3.11 models/mystery-box-sg92r-c4-2/contact_envelope_evidence.py
py -3.11 models/mystery-box-sg92r-c4-2/simulate.py
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --python-exit-code 1 --python models/mystery-box-sg92r-c4-2/render_preview.py
py -3.11 tools/lattice_web.py mystery-box-sg92r-c4-2
node --test viewer/lattice/motion.test.mjs viewer/lattice/sim.test.mjs viewer/lattice/c42-sim.test.mjs viewer/lattice/c42-render.test.mjs viewer/lattice/c42-support-ui.test.mjs
node tools/catalog.js check
py -3.11 models/mystery-box-sg92r-c4-2/audit.py
py -3.11 models/mystery-box-sg92r-c4-2/report.py
```

穴の検査は19セルと5停止位置を組み合わせる。対辺9.3mmの穴を7高さで測る。納品時の記録をSHAだけ差し替えて流用しない。

## 確認範囲

幾何検査は実STLを使う。多様体だけでなく連結成分を数える。ホーンと角キーの正逆接触を測る。保持具と外装までの接触を調べる。円盤と受けは有限面の最高高さを照合する。組立は途中姿勢と先に入れた部品を含める。

動作表の高さも実STLから求める。足の頂点だけではなく、カム三角形の頂点と足の外周との交点を含める。角度表の最大間隔は0.05°。各区間の25%・50%・75%で表示の線形補間を照合する。誤差が0.00002mmを超える区間は二分する。結果は `build/contact_envelope_evidence.json`。これは有限個の計算。全ての連続姿勢の衝突証明とは区別する。

動作計算は接続形状が成立する場合の条件付き計算。実STLの質量とZ回転の慣性を使う。摩擦係数0.30は仮値。接点の摩擦と案内の横荷重を含める。円盤外周の支持面の摩擦も含める。負の接触反力が必要な動作は不成立。

実物の印刷と通電は未実施。付属ホーンの嵌まりと印刷収縮を試片で確認する。保持力と摩耗と耐久性も実物未確認。
