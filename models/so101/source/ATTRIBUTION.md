# SO-101 の元データ

- 出所: TheRobotStudio / SO-ARM100 — https://github.com/TheRobotStudio/SO-ARM100
- パス: `Simulation/SO101/`（`so101_new_calib.urdf` と `assets/*.stl`）
- ライセンス: Apache-2.0
- 取得: mycobot-lab の `src/robots/so101/`（2026-06-04 に上流から取得したもの）を 2026-10-24 にコピー

STL は URDF の各リンク座標で書かれていて、単位は m。
`model.py` はこれを読むだけで書き換えない。形の変更は `edits.py` に書く。
