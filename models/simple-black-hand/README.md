# シンプル黒ロボットハンド

5 本指の黒い艶消しのロボットハンドの、手の部分だけ（指・親指・手のひら・関節）。手首と前腕は無い。

- 出どころ: `models/robot-hand-soft/` の 8f3e445 から手首と前腕を外したもの（`models/robot-hand-v2/seed/` と同じ形）
- ビルド: `./run.sh models/simple-black-hand/model.py` → `exports/simple-black-hand.stl`
- `model.build_hand()` が部品ごとのオブジェクトと関節（`index_j3` など、`thumb_cmc`）を返す。根は `palm`
- 握る動き・GLB の書き出しの作り方は `models/robot-hand-soft/animate.py` を参照

## 関節（2026-11-09 作り直し）

- 甲側に出ていた円柱の胴、左右へはみ出す長円の板、手のひら側の横棒をやめた
- 各節は角を丸めた 1 つの殻。遠位の端は関節の軸を中心にした丸い拳骨で終わり、次の節の近位の端はその拳骨と同心にえぐる。継ぎ目は 0.4mm の弧で、曲げても幅が変わらない
- 軸は手のひら側の面から 8mm（`AXIS_Y = 0.5`）。軸から手のひら側の面までを a、拳骨の半径を R とすると、a√2 < R + 継ぎ目 のとき曲げても前後の節が重ならない
- 関節の横の面には軸のふたの浅いくぼみ（半径 3.2mm・深さ 0.35mm）だけを残した
- 握りで中指と薬指の指先が当たったので、薬指の握りを j2 60° / j1 34° に変えた
- 検査: `blender --background --python models/simple-black-hand/check_collisions.py`（開いた手から握りまで 5 姿勢で、部品同士の三角形の交差が 0 なら exit 0）
- 静止画: `blender --background --python models/simple-black-hand/render_views.py -- [--pose fist] [--views close,side]` → `G:\マイドライブ\shubie\renders\simple-black-hand\`
