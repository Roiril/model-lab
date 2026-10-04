#!/usr/bin/env bash
# 参考画像のカメラから見た輪郭を合わせ直して、STL を作り直す。
#   fit/cma_state.json（最適化の結果）→ export_fit.py → fit_state.json → model.py（歪み無し）
#   → warp_fit.py（歪みを求める）→ model.py（歪みを再生）→ verify.py / measure.py
set -e
cd "$(dirname "$0")/../../.."
BLENDER="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
rm -f models/laptop-stand-flow/fit/view_warp.npz
./run.sh models/laptop-stand-flow/model.py | grep -E "unit size"
SIGMA1=${SIGMA1:-40} NIT=${NIT:-60} "$BLENDER" --background --python models/laptop-stand-flow/fit/warp_fit.py -- /tmp/_warp.png | grep -E "iter (0|20|40|60) "
./run.sh models/laptop-stand-flow/model.py | grep -E "unit size|view warp"
./run.sh models/laptop-stand-flow/verify.py | grep -E "stl:|RESULT"
"$BLENDER" --background --python models/laptop-stand-flow/fit/measure.py -- "$PWD/exports/laptop-stand-flow-unit.stl" "$PWD/exports/laptop-stand-flow/measure" | grep MEASURE
