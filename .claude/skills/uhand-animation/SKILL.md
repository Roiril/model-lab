---
name: uhand-animation
description: model-lab の Hiwonder uHand（5 本指ロボットハンド）の動きを足す・直す・確かめる・Unity へ渡す。クリップは JSON でサーボ 6 個ぶんの量を時刻ごとに書くだけで、関節と銀の板の動きは機構の計算が出す。「uHand」「ロボットハンドのアニメーション」「手の動きを足して」「ジェスチャーを追加」「握る・開く・指を立てる」「クリップ」「Unity で動かす」「FBX を書き出す」「指の曲がり方を直して」で発動。形そのもの（寸法・部品）を直すときも、動きに響くのでここを読む。
---

# uHand の動き

正本は `models/hiwonder-uhand/`。入口は 1 本にまとめてある。

```bash
py -3.11 models/hiwonder-uhand/anim.py check            # 定義と機構の検査。exit 0 で合格
py -3.11 models/hiwonder-uhand/anim.py build            # 検査 → exports/hiwonder-uhand-rigged.{fbx,glb,json}
py -3.11 models/hiwonder-uhand/anim.py preview <clip> [front|palm|back|side]   # 8 コマの絵と動画
py -3.11 models/hiwonder-uhand/anim.py pose <姿勢> [view]                       # 姿勢 1 枚
py -3.11 models/hiwonder-uhand/anim.py dofs index=1,thumb=0.5 [view]           # 量を直に決めて 1 枚
py -3.11 models/hiwonder-uhand/anim.py unity-test       # Unity の空プロジェクトで読み込み・組み立て・照合
py -3.11 models/hiwonder-uhand/anim.py unity <project>  # 使うプロジェクトへ入れる
```

絵と動画は `exports/uhand-anim-preview/`。ブラウザは http://localhost:3000/viewer/uhand-anim.html（`?clip=<名前>` で指定。クリップの再生と、サーボごとのつまみ）。

## 1. 動かせる量は 6 個

実物のサーボ 6 個と同じ。クリップも Unity の操作も、この 6 個の数だけを扱う。

| 量 | 範囲 | 意味 |
|---|---|---|
| `little` `ring` `middle` `index` | 0〜1 | 0 が寸法図の姿勢（開いた手）、1 が握りきり |
| `thumb` | 0〜1 | 0 が寸法図の姿勢、1 が手のひらへ倒しきり |
| `wrist` | -1〜1 | 手首の回転。0 が正面、±1 が ±90 度 |

指は量 1 個から、付け根・次の関節・指先の 3 つの角度と、銀の板 2 枚と引き棒の姿勢が決まる（`kin.py` が実物と同じ 4 節リンクを解く）。握りきりで関節は 60 / 約 75 / 約 62 度。**関節の角度を個別に書く口は無い。** 実物に無い動きを作らないため。

## 2. クリップを足す

1. `anim/clips/<名前>.json` を書く（名前は英小文字・数字・`_`。`dof_` で始めない）
2. `anim.py check` → `anim.py preview <名前>` で絵を見る（`front` と `side` の両方）
3. `anim.py build`
4. Unity で使うなら `anim.py unity <project>` のあと、Unity で Tools > uHand > Build Animator Controller

```json
{
  "description": "何をする動きか（1 文。ブラウザと目録に出る）",
  "loop": false,
  "keys": [
    {"t": 0.0, "pose": "open"},
    {"t": 0.6, "pose": "peace"},
    {"t": 1.0, "pose": "peace", "set": {"wrist": 0.2}, "ease": "smooth"},
    {"t": 1.6, "pose": "open"}
  ]
}
```

- `t` は秒。最初は 0。`pose` は `anim/poses.json` の名前、`set` で量を上書きする。どちらも無い量は 0
- `ease` はそのキーへ向かう区間の進み方。`smooth`（既定）/ `linear` / `in`（だんだん速く）/ `out`（だんだん遅く）/ `hold`（直前まで動かず切り替わる）
- `loop: true` は最初と最後の姿勢を同じにする（検査が見る）
- 姿勢を止めて見せたいときは、同じ姿勢のキーを 2 つ並べる
- よく使う形は `poses.json` に名前を付けて足す。クリップの中に同じ数を何度も書かない

## 3. 直すときにどこを触るか

| 直したいこと | 触る場所 |
|---|---|
| クリップの間・順番・速さ | `anim/clips/<名前>.json` |
| 「握った形」「ピースの形」そのもの | `anim/poses.json` |
| 指の曲がりの深さ（全クリップに効く） | `kin.py` の `FINGER_MCP_MAX` `THUMB_PROX_MAX` `THUMB_TIP_MAX` |
| 関節どうしの連動の比 | `params.py` の `F_G`（S 字の板の上端）と `F_A` `F_D`（銀の連結板の両端）。形も一緒に変わる |
| 部品の形・位置 | `model.py` `params.py`。変えたら `anim.py build` まで通す |
| どの部品がどの骨に付くか | `anim_build.py` の `RULES`。当たらない部品があると止まる |
| 骨の親子・回転の中心 | `kin.py` の `bones()` |

`params.py` の指の点（`F_MCP` `F_PIP` `F_DIP` `F_G` `F_A` `F_D`）を動かすと連結が解けなくなることがある。`anim.py check` が「届かない」「曲げが戻る」で止める。

## 4. 仕組み

- `kin.py`（bpy 無し）: 量 → 骨ごとの 4x4 行列。Blender の書き出しと検査が同じ関数を呼ぶ
- `anim_lib.py`（bpy 無し）: クリップの読み込み・書式の検査・時刻ごとの量
- `anim_build.py`（Blender）: 部品を骨ごとに 1 メッシュへまとめて骨に直接ぶら下げ（スキン無し）、30fps で 1 フレームずつ焼く
- 量を 1 個ずつ端から端へ動かすクリップ `dof_<量>` を自動で作る。その量の骨だけにキーがある
- Unity の `UHand.controller` は、層 0 がクリップの再生、その上に量ごとの層が 6 枚。量の層は `dof_<量>` を数値で時刻引きする（Motion Time）。`UHandDriver` が層の重みを切り替える
- 目録 `exports/hiwonder-uhand-rigged.json` に、骨どうしの距離の目印（`probes`）が入る。Unity 側の Verify がこれと比べる

## 5. 完了の条件

- `anim.py check` が exit 0
- `anim.py build` が通り、`anim.py status` が「書き出しは最新」
- 足した・直したクリップを `preview` で見た（`front` だけで決めない。指の重なりは `side` で分かる）
- Unity に関わる変更（骨・クリップ名・`unity/` のスクリプト）は `anim.py unity-test` が合格
- 作業を終えるとき、検査が赤か書き出しが古いと Stop hook（`.claude/hooks/stop.js`）が 1 回止める

## 6. 知っておくこと

- **親指の銀のクランクは伸び縮みで合わせている**（最大 1.33 倍）。資料から仕組みが読めず、固定側から親指を追わせているため。検査の幅は `anim_check.py` の `CRANK_STRETCH`。仕組みが分かったら `kin.thumb_pose` を直して幅を狭める
- 指の引き棒も伸び縮み（最大 1.12 倍）。手のひらの中にほぼ隠れる
- S 字の板の上端 `F_G` は、連動が成り立つ位置を計算で探して決めた（関節の 15mm 下）。寸法図の側面で板が上端をまたいで後ろへ下りる形とは合うが、留め位置そのものは図から読めていない
- 書き出し（FBX・GLB・目録）と確認用の絵は git に入れない。別の PC では `anim.py build` で作る
- Bash の heredoc で `\n` を含む置換を書くと 1 段消える。JS や JSON を直すときは Edit ツールを使う
- Blender 5.1 で通している。骨の姿勢は `matrix_basis = 休み⁻¹ · 親の動き⁻¹ · 自分の動き · 休み` で入れる（`anim_build.apply_pose`）
- Unity は 2022.3.62f2 で確かめた。`UNITY` 環境変数で別の版の `Unity.exe` を渡せる
