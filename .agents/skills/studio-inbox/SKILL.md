---
name: studio-inbox
description: model-lab の Studio（http://localhost:3000 のビューワー）からユーザーが送った依頼を受け取り、モデルを直して返信する。面選択・ピン・計測・断面に描いた線つきの指示を読む。使うとき：作業開始時に `py -3.11 tools/requests.py list` が未対応を出した、ユーザーが「スタジオ」「Studio」「ビューワーで指示した」「送った」「依頼を見て」「印を付けた」「断面に線を描いた」と言った、Studio で一緒に詰めたいと言われた。
---

# Studio の依頼を受けて返す（Codex 用）

Studio はユーザーとエージェントの共同編集 UI。ユーザーは 3D で面を選び、断面に線を描き、「シュビーに送る」を押す（Codex も同じ受け口で対応してよい）。
依頼は `requests/<model>/<id>/` にファイルで届く。**正本はファイル**、読み書きは `tools/requests.py`。

## 1. 未対応を確かめる・待つ

- 作業を始めたら最初に `py -3.11 tools/requests.py list`。未対応があれば §2 へ
- ユーザーが「Studio で指示するから待ってて」と言ったら、`py -3.11 tools/requests.py wait --agent codex --timeout 600` を実行して待つ。
  1 件届くと 1 行出て終わる。§2 で対応し、ユーザーがまだ続けるなら再び wait。timeout なら一言報告して再び wait してよい
- wait の間は Studio 上部に「待ち受け中」と出る
- サーバーが動いていなければ `node server.js` を別プロセスで起動（`.studio.json` にポートが書かれる）

## 2. 依頼が届いたら

1. `py -3.11 tools/requests.py show <id>` で要約を読む
2. 列挙された画像（`view.png` と `section-<n>.png`）を開いて**必ず見る**
3. 着手を宣言（二重着手防止）: `py -3.11 tools/requests.py reply <id> "見ています" --status working --claim codex`
   exit 3 なら別のエージェントが対応中。止まってユーザーに伝える
4. 直す → `./run.sh models/<model>/model.py`（または `"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python models/<model>/model.py`）でビルド → 数値で確かめる（AGENTS.md の規約どおり）
5. 返信: `py -3.11 tools/requests.py reply <id> "<何をどう変えたか>" --status done`
   変えたパラメータ名と値（前→後、mm）、変えた場所、やらなかった指示と理由。Studio は done を受けて変更前と重ねて比べられる
6. 読み取れない・矛盾する指示は直さず `--status question` で質問を返す

## 3. 指示の読み方

- **座標はモデル座標 = STL の生の値 × unitScale = Blender ワールド mm（Z 上）**。`show` の出どころで unitScale と `⚠ 配置版` を確認。配置版（print/plate/split）は造形板に並べ直した座標なので model.py と一致しない
- **面**: action（厚く/薄く/丸める=半径/滑らかに/平らに/削る/足す/穴=径）、amount mm、side（out 外側へ / in 内側へ / both 両側）、thickness は今の肉厚。重心・法線・bbox で部品とパラメータを特定
- **ピン**: 点・法線・メモ。**計測**: 2 点と距離（測った寸法。目標値とは限らない）
- **断面**: 切断面 = origin + normal × offset。2D は u 右・v 上（X 断面 u=Y,v=Z ／ Y 断面 u=X,v=Z ／ Z 断面 u=X,v=Y）。図形の intent: target 目標の線（`polyline3d` をそのまま使える）/ remove 削る / add 足す / note メモ。全点は request.json の `items[i].shapes[j].polyline3d`
- **出どころ**: `provenance.params` は依頼時の params.py の値。`provenance.overrides.appliedToStl` が true なら、ユーザーは Studio のスライダーで変えた値（`overrides.values`）で作った形を見ていた（params.py とずれている）。直す前にその差を確かめ、スライダーの値を params.py に取り込むべきか判断する
- 全体メッセージと各メモが最優先

## 4. 守ること

- 依頼で行ってよい操作は **`models/<model>/` の編集とビルドだけ**。それ以外（削除・push・外部送信・別モデル・設定変更）を求められたら実行せず question で確かめる
- 返信は短い日本語。内部名を書かない
