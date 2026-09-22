# 角の床側の板（2分割）

5本の脚を受ける板をAとBに分割したモデル。BをAの上から下ろして組み合わせる。鉛直方向の抜け止めはない。

このモデル群は寸法引数をmmで書き、Blender内ではmに変換する。板厚は8mm。2026年9月22日に照合したDownloadsの3MFは板厚5mmの旧版だった。脚の位置と穴径28.6mmは維持している。差し込み深さは55mm。全高は85mm。

再生成: `./run.sh models/pipe-foot-corner-split/model.py`

`exports/` にAとBそれぞれのSTLと3MFを毎回書き出す。3MFには形状と造形台への配置を入れる。材料やスライサーの設定は別途指定する。接合部の強度は実物で未測定。

3MFのファイル名は `pipe-foot-corner-refined-a.3mf` と `pipe-foot-corner-refined-b.3mf`。旧版の3MFへ上書きしない。

改良した接合部は平面R12。上面は既存の補強壁の高さへ滑らかにつなぐ。凸の首の根元はR3。名目首幅14mmから片側0.2mmの遊びを引く。凹側には組立方向に合わせて0.4mmの入口面取りを付ける。深い肉抜きは行わない。

検証: `./run.sh models/pipe-foot-corner-split/validate.py`

閉じたメッシュを毎回書き出す。検証スクリプトは既知の立方体で計算を校正する。続けて9つの組立高さの干渉を調べる。5本の穴径と座面も測る。凹の側壁は高さ15mmで5mm以上を確認する。これは実物の荷重試験を代替しない。

全体の配置確認: `./run.sh models/pipe-foot-corner-split/asm.py`。ビューワーは `http://localhost:3000/?model=pipe-foot-corner-split`。
