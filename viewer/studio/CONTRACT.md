# Studio モジュール契約

設計の全体は `.agent/plans/2026-10-07_studio.md`。ここは**モジュール間の約束だけ**を書く。
実装者は自分の担当ファイル以外に書かない。契約に無いものが要るなら、自分のモジュール内で完結させるか、報告に「契約に足してほしい点」として書く。

## 0. 共通

- ビルドなし ES modules。importmap（index.html）:
  - `three` → `https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js`
  - `three/addons/` → `https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/`
  - `three-mesh-bvh` → `https://cdn.jsdelivr.net/npm/three-mesh-bvh@0.9.15/build/index.module.js`
- 状態と出来事は `store.js` の `store`（読むだけ。変更しない）。定数 `INTENTS` `ACTIONS` `ITEM_COLORS` `PIN_COLOR` `MEASURE_COLOR` `SELECTION_COLOR` もそこから import する
- **座標**: 指示の座標はすべて「モデル座標」= STL の生の値（通常 Blender ワールド mm、Z 上）。`[x,y,z]` の配列で持つ（THREE.Vector3 を store に入れない）。**変換はすべて `frames.js` に置き、他のファイルで行列や基底を書かない**
- STL の単位は 1 ファイルずつ推定する（bbox の最大寸法が 2 未満なら m 単位とみなし表示倍率 1000 倍）。推定結果は mesh.userData.unitScale（mm/STL単位）に持ち、依頼に残す。モデル座標は常に「STL の生の値 × unitScale」= mm
- **preview モジュール表示中（frame === "preview-m-yup"）は指示の道具を使えない**。ヒント行に「指示を付けるには STL を表示」と出し、STL 表示へ切り替えるボタンを出す
- **faceId = STL ファイル内の三角形の順番**（0 始まり）。BVH は `indirect: true` で作り index を並べ替えさせない
- **キー入力は app.js が一括で受ける**。2D エディタ上にポインタがある（または最後に触った）ときは `sketch.handleKey(e)` に先に渡し、true が返れば終わり。そうでなければ 3D の道具キー
- 画面の文字は日本語。短く、実装の呼び名（faceId, bvh, loop 等）を出さない
- エラーは握りつぶさず `store.status(text, "err")` と `console.error`

## 1. store の出来事

| 名前 | payload | 誰が出す | 意味 |
|---|---|---|---|
| `change:<key>` / `change` | 新しい値 / 変わったキー配列 | store.set | state の変化 |
| `items` | `{reason, id}` | store | 下書きの指示が増減・変化（undo 含む） |
| `item:focus` | `{id}` | panels | その指示が見えるようにカメラを合わせてほしい（viewport が受ける） |
| `mesh:loaded` | `{meshes, frame}` | viewport | 表示メッシュが入れ替わった |
| `ghost:loaded` | `{geometry \| null}` | viewport | 比較用ゴーストが入れ替わった（geometry はモデル座標） |
| `section:loops` | `{id, loops, ghostLoops, bounds}` | section | 断面を切り直した。loops = `[{points:[[u,v],...], closed}]`、bounds = `{min:[u,v], max:[u,v]}` |
| `popover` | 下記 | picking | 確定待ちの入力を UI に出してほしい |
| `popover:close` | — | picking / panels | サイドの編集欄を閉じ、仮置きのピンを消す |
| `status` | `{text, kind}` | 誰でも | 右下の状態表示 |
| `toast` | `{text, action?}` | 誰でも | 一時通知 |
| `viewport:pointer` | `{point \| null}` | viewport | 3D でカーソル下のモデル座標（ヒント行の座標表示用、間引いて出す） |

`popover` payload:
- 面: `{kind:"faces", x, y, file, faceIds, summary}`（x,y は画面座標 px）。UI が確定したら `store.addItem({type:"faces", file, faceIds, summary, action, amount, note})` → `store.set({selection: []})`
- ピン: `{kind:"pin", x, y, file, point, normal}`。UI が確定したら `store.addItem({type:"pin", file, point, normal, note})`

面とピンの編集欄は `#inspector` 内へ表示する。3D画面を覆わず、操作を無効にしない。小画面ではモデルと編集欄を上下に分ける。面の再選択では件数と範囲だけ更新し、入力中の内容を保つ。通常クリックでモデルに当たらなければ既存の面選択処理で解除する。Shift/Alt と視点ドラッグの動作は変えない。

`state.showFaceOutlines`（既定 false）は表示だけの設定。上部「面の輪郭」で切り替える。viewport が STL とプレビューの全三角形の辺を描く。比較用モデルと選択の重ね描きは対象外。断面とモデルの再読込にも追従する。

## 2. 指示（draft.items）の形

```js
// 共通: { id, type, color, note, file }
{ type:"faces",   action, amount /* mm | null */, side /* "out"|"in"|"both"、厚く・薄くのとき */, faceIds:[...], summary }
{ type:"pin",     point:[x,y,z], normal:[x,y,z] }
{ type:"measure", a:[x,y,z], b:[x,y,z], distance /* mm */ }
{ type:"section", plane:{axis, origin:[x,y,z], normal:[x,y,z], u:[x,y,z], v:[x,y,z]}, offset /* mm */, clip:false, shapes:[Shape] }
```

`summary` = `{ faceCount, area /* mm² */, thickness:{min, median} | null /* 内向きの raycast で測った今の肉厚 mm（最大 20 点） */, centroid:[x,y,z], normal:[x,y,z] /* 面積加重平均の単位ベクトル */, bbox:{min:[x,y,z], max:[x,y,z]}, samples:[[x,y,z,nx,ny,nz], ...最大 300] }`

断面の平面: `normal = u × v`。実際の切断面は `origin + normal * offset`。2D 点 `[u0,v0]` のモデル座標は `origin + normal*offset + u*u0 + v*v0`。
軸ごとの固定基底（正面図・側面図・上面図と同じ向き）:
- `x`: u=(0,1,0) v=(0,0,1) → normal=(1,0,0)
- `y`: u=(1,0,0) v=(0,0,1) → normal=(0,-1,0)
- `z`: u=(1,0,0) v=(0,1,0) → normal=(0,0,1)
- `view`: u=カメラ右, v=カメラ上（モデル座標に直したもの）
- `auto`: 視線方向に最も近い軸を x/y/z から選ぶ

## 3. Shape（2D 図形、単位 mm、断面の (u,v)、v が上）

```js
{ id, kind:"pen"|"line"|"curve"|"rect"|"ellipse"|"arrow"|"text"|"dim",
  intent:"target"|"remove"|"add"|"note",
  nodes:[{ p:[u,v], in:[u,v]|null, out:[u,v]|null }],  // in/out はベジェのハンドル（絶対座標）
  closed:false, text:"", note:"" }
```
- line / arrow / dim: 2 節点（始点・終点）。dim は距離ラベルを自動表示
- rect / ellipse: 対角 2 節点
- pen / curve: ベジェ節点列。closed で閉曲線
- text: 1 節点、text に本文

## 4. モジュールの API

### frames.js（担当 B）— 座標変換の唯一の置き場。three を import しない純関数
```js
export const AXES = { x:{u:[0,1,0], v:[0,0,1]}, y:{u:[1,0,0], v:[0,0,1]}, z:{u:[1,0,0], v:[0,1,0]} };
export function makePlane(axis, point, cameraAxes) -> { axis, origin, normal, u, v }   // auto/view を含む §2
export function uvToModel(plane, offset, [u, v]) -> [x, y, z]
export function modelToUv(plane, offset, [x, y, z]) -> [u, v]
export function planeAt(plane, offset) -> { origin, normal }                     // 実際の切断面
// ベクトル小物: add sub scale dot cross norm len
```
数値テスト `viewer/studio/frames.test.mjs`（`node viewer/studio/frames.test.mjs` で全件 OK を出す。往復変換・normal=u×v・軸ごとの基底）

### viewport.js（担当 B）
```js
export function createViewport(container, store) -> {
  THREE, renderer, scene, camera, controls, canvas,
  modelRoot,     // Group。子はモデル座標（mm, Z 上）。rotation.x=-PI/2, scale 0.001, position でグリッドに載せる
  overlay,       // Group（modelRoot の子）。指示の可視化をモデル座標で置く
  labels,        // { add(el, [x,y,z]) -> {setPos([x,y,z]), remove()} }  画面上の HTML ラベル（CSS2DRenderer）
  async loadSTLs([{name, url}], {fit}) -> meshes,  // 各 mesh: userData.file、geometry は index 付き＋boundsTree 済み
  setPreviewGroup(group, {fit}),                    // preview モード。frame を "preview-m-yup" に
  getMeshes() -> [Mesh],
  async setGhost(url | null),                       // 比較用 STL を半透明で。ghost:loaded を出す
  getGhostGeometry() -> BufferGeometry | null,
  pick(clientX, clientY) -> { mesh, file, faceIndex, point:[x,y,z], normal:[x,y,z] } | null,
  toModel(Vector3 world) -> [x,y,z],  toWorld([x,y,z]) -> Vector3,
  modelBox() -> { min:[x,y,z], max:[x,y,z] },
  viewPreset("front"|"back"|"left"|"right"|"top"|"bottom"|"iso"),
  frameModelBox({min, max}),
  cameraInfo() -> { position, target, up, fov },   // モデル座標
  cameraAxes() -> { right:[x,y,z], up:[x,y,z], forward:[x,y,z] },  // モデル座標の単位ベクトル
  setClipPlane({origin, normal} | null),            // モデル座標。normal 側を隠す
  setControlsEnabled(bool),
  onFrame(fn) -> unsubscribe,
  screenshot({ width = 1600 } = {}) -> dataURL,      // ラベル込みでなくてよい。overlay は写る
  applyViewerConfig(cfg | null),                    // models/<name>/viewer.json（後述）
}
```
- 大きい STL（~109 万三角形、54MB）で使える速さにする。表示は STL のまま（非 index）で即出す。BVH は `computeBoundsTree({indirect:true})`。**溶接（法線を捨てて位置だけで同一視、型付き配列のハッシュ）と隣接表は Worker で、面の道具を初めて使う時に作る**（`geom.worker.js`、import 無しの素の JS、typed array を transfer）
- 面ごとの法線は位置から計算する（STL の法線を信用しない）
- 表示は `flatShading: true` を既定（機械部品の稜線を保つ）。`viewer.json` の `smoothNormals: true` なら滑らか
- `viewer.json`: `{ camera:{azimuth, elevation, fov, distance}, material:{color, roughness, metalness}, smoothNormals }`（azimuth/elevation は Blender の Z 上系で度。distance は最大寸法の倍率）

### picking.js（担当 B）
```js
export function createPicking(viewport, store) -> {
  summarizeFaces(mesh, faceIds) -> summary,
  dispose(),
}
```
- tool が `faces` / `pin` / `measure` のときだけ canvas のポインタを解釈する。クリック（移動 4px 未満）で動作し、左ドラッグは視点回転のまま。ブラシ中だけ左ドラッグで塗る（その間 controls 無効）
- faces: smart = **種にした面の法線との角**が `state.faceAngle` 以内の面を、隣接をたどって塗り広げ（隣どうしの角で比べると滑らかな形では全体が選ばれる）。brush = 半径 `state.brushRadius` mm 内で法線がカメラ側を向く面。Shift 追加 / Alt 除外。`state.selection` と `selectionFile` を更新し、ポインタを離したら `popover {kind:"faces"}`
- pin: クリックで `popover {kind:"pin"}`
- measure: 1 点目→2 点目で `store.addItem({type:"measure", ...})`。Shift で軸に揃える
- 3D の重ね描き: 確定前の選択（SELECTION_COLOR）、faces 指示（item.color）、ピン（番号付きラベル）、計測（線＋mm ラベル）。`items` と `change:selection` を購読して描き直す
- Esc で選択解除（keydown は app.js が `store.set({selection: []})` する）
- `item:focus` を受けて faces / pin / measure をフレームに収める（section は section.js）

### section.js（担当 B）
```js
export function createSections(viewport, store) -> { getLoops(id) /* {loops, ghostLoops, bounds} | null */, dispose() }
export function sliceGeometry(geometry, plane, offset, bvh?) -> loops  // geometry はモデル座標。frames.js を使う
```
- tool が `section` のとき、クリックで面を拾い `makePlane(state.sectionAxis, point, viewport.cameraAxes())` → `store.addItem({type:"section", plane, offset:0, clip:false})` → `store.set({activeSectionId: id})`
- 断面ごとに 3D で半透明の平面（モデルの大きさに合わせる）と輪郭線。アクティブを強調。アクティブで `clip` なら `viewport.setClipPlane`
- plane / offset が変わったら切り直す（ドラッグ中は 60ms 程度で間引く）。メッシュ・ゴーストの差し替えでも切り直す。結果を `section:loops` で出す
- 1M 三角形で 1 回の切断が 150ms 以内を目安（BVH の shapecast で平面と交わる三角形だけ見る）
- `item:focus` が section なら平面を正面から見るカメラにする

### sketch.js（担当 C）
```js
export function createSketch(container, store, { modelBox } = {}) -> {   // modelBox: () => viewport.modelBox()（位置スライダーの範囲）
  fit(), resize(),
  exportSVG(sectionId) -> string,                 // 輪郭・ゴースト・図形・寸法・スケールバー入り、単体で開ける SVG
  async exportPNG(sectionId, { width = 1400 }) -> dataURL,
}
export function sampleShape(shape, step = 0.5) -> [[u, v], ...]   // 図形を step mm 間隔の折れ線に
// 返り値のオブジェクトには handleKey(e) -> bool と isFocused() -> bool も含める
```
- v1 の道具: select / pen / line / curve / rect / ellipse / arrow / text（dim は作らない。寸法は 3D の「測る」）
- container の中にエディタ一式（上の道具バー・意図の切替・断面の位置 mm 入力とスライダー・片側を隠す切替・閉じる、下の座標表示）を自分で作る
- 表示するのは `state.activeSectionId` の断面。`section:loops` を受けて描き直す
- 図形の編集は `store.updateItem(id, {shapes})`。ドラッグ開始で `store.checkpoint()`、ドラッグ中は `{history:false}`
- 位置スライダーは `store.updateItem(id, {offset}, {history:false})`（開始時 checkpoint）
- キー: `handleKey(e)` で V P L B R O A T、Delete/Backspace、Enter、Esc、Space（パン）、F（全体表示）を処理して true を返す。Ctrl+Z は返さない（app.js が store.undo）。テキスト入力中は app.js が呼ばない
- 断面が無いとき container は空でよい（app.js が表示を切り替える）

### api.js / bundle.js / panels.js / app.js / index.html / styles.css（担当 D）
- api.js: fetch の薄い包み＋ WS（再接続つき）。WS の URL は `ws://127.0.0.1:<port>`。ポートは `GET /api/config` → `{ws}`
- 上部に「シュビー」の在席表示: `GET /api/listener` → `{listening, agent, at}`（WS の `listener` でも届く）。待ち受け中 / 不在
- bundle.js: `async buildRequest({store, viewport, sections, sketch}) -> {request, images}`（faceIds を落とす、section に loops / 画像名、shape に polyline / polyline3d を足す、view.png）
- panels.js: topbar、左レール、ヒント行（道具ごとの説明と、角度・半径・軸の切替）、インスペクタ（指示 / パラメータ / 履歴）、コマンドパレット、ポップオーバー、トースト
- app.js: 起動・モデル読み込み（旧 viewer/index.html の STL 選びの規則をそのまま移植）・キーボード・配線

## 4.1 実装後に足されたもの（2026-10-07 結合時）

- viewport: `invalidate()`（描画は要るときだけ。3D を変えたら呼ぶ）、`toScreen`、`size`、`geomInfo`、`hasGeomInfo`、`clipMaterial` / `unclipMaterial`、`dispose`。`viewPreset` は向きの配列も受ける。`screenshot` はモデルの範囲に切り詰め、ピン番号・計測値のラベルを焼き込む
- frames: `planePosition(plane, offset)`。軸平面の origin は法線成分だけを持つ点（(u,v) がそのまま人の読むモデル座標になる）
- picking: `cancel()`。popover の x,y は client 座標
- slice.js の輪郭は材料が左（外周は反時計回り、穴は時計回り）。sampleShape は閉じた図形の最後に始点を繰り返す
- app.js は `window.__studio = { store, viewport, picking, sections, sketch }` を出す（動作確認用）

## 5. デザイントークン（styles.css が正本。JS で色が要る時は store.js の定数）

### モデル一覧と保存（2026-10-07 更新）

- `/api/models` はモデルディレクトリ全件を返す。既存 `name / preview / category` を維持する。`title / description / categoryId / projectId / project / tags / status / organized / available / unavailableReason` を追加する。
- 分類は `models/catalog-groups.json`。モデルの表示情報は `models/<id>/catalog.json`。不正や欠損は未整理として表示する。`available:false` も一覧から除外しない。
- `catalog.js` の `createCatalog({store,onOpen,getModels,getRecent})` がモデルを選ぶ画面を管理する。`onOpen(name)` は永続IDを渡す。お気に入りは `studio.favorites`。最近開いたモデルは `studio.recent`。
- 寸法入力は controls の `unit / displayScale` を使う。表示値は `value * displayScale`。APIへは元の単位で送る。不明な単位は「元の値」と表示する。
- 調整した値は `studio.params.<id>` にモデル別で保存する。モデルの切替でも維持する。下書きは既存 `studio.draft.<id>`。
- 送信中は入力とモデル切替を止める。送信した後の下書きが送信開始時と一致する場合だけ空にする。
- 狭幅では `#app[data-inspector="open"]` で指示・設定を開く。道具は下部へ移す。断面は3Dの下に表示する。

以下の色は既存 Studio の正本。小さい補助文字は読みやすさのため `--text-2` と同じ明るさに揃えた。

```css
--bg:#0e1013;  --panel:#15181c; --raised:#1c2026; --hover:#232830;
--line:#2a3038; --line-strong:#3a424d;
--text:#e6e8ea; --text-2:#aab2bc; --mute:var(--text-2);
--accent:#7c9cff; --accent-ink:#0b1020;
--ok:#2fd08f; --warn:#ffb020; --err:#ff6b6b;
--radius:6px; --radius-sm:4px;
font: 13px/1.5 "Inter", "Noto Sans JP", "Yu Gothic UI", system-ui, sans-serif;  数値は ui-monospace
```
- 影は浮いているもの（ポップオーバー・パレット・トースト）だけ。`0 8px 24px rgba(0,0,0,.45)`
- 3D の背景は `--bg`。2D キャンバスの地は `--panel`、材料の塗りは `rgba(230,232,234,.10)`、輪郭線は `--text`、ゴーストは `--mute` 点線
