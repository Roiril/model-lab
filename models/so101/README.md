# so101 — SO-101 ロボットアーム

TheRobotStudio の SO-101（5 自由度、STS3215 サーボ 6 個）を URDF どおりに組み立てたモデル。
実機とシミュレータは mycobot-lab にある（シミュレータ http://localhost:8025/ のヘッダから、ここへのリンクがある）。

## 作り直す

```bash
./run.sh models/so101/model.py          # build/ と exports/so101.stl
py -3.11 tools/studio_parts.py so101     # Studio の部品台帳と exports/so101-part-*.stl
```

`edits.py` か `params.py` を変えたら、必ず 2 つとも回す（台帳の sha256 が古いと Studio が部品を読み直さない）。

## どこを変えるか

| 変えたいもの | 場所 |
|---|---|
| 組み立てた姿勢（関節角） | `params.py`。角度の向きと 0 点はシミュレータと同じ |
| 部品の形（穴・厚み・削る・足す） | `edits.py` の `apply(parts)`。部品は自分の座標（m）で渡る |
| 部品の名前・群 | `model.py` の `PARTS` / `GROUPS` |

`source/` の STL と URDF は上流のまま。書き換えない（Apache-2.0、`source/ATTRIBUTION.md`）。

## 確かめたこと

READY 姿勢（0, −35, 45, −15, 0）で、部品ごとの外形が MuJoCo（mycobot-lab の物理）と 0.001 mm 以内で一致した（2026-10-24）。
