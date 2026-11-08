# シンプル黒ロボットハンド

5 本指の黒い艶消しのロボットハンドの、手の部分だけ（指・親指・手のひら・関節）。手首と前腕は無い。

- 出どころ: `models/robot-hand-soft/` の 8f3e445 から手首と前腕を外したもの（`models/robot-hand-v2/seed/` と同じ形）
- ビルド: `./run.sh models/simple-black-hand/model.py` → `exports/simple-black-hand.stl`
- `model.build_hand()` が部品ごとのオブジェクトと関節（`index_j3` など、`thumb_cmc`）を返す。根は `palm`
- 握る動き・GLB の書き出しの作り方は `models/robot-hand-soft/animate.py` を参照
