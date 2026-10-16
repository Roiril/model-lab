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
- `state.layout` は組立表示で `{kind:"assembled"}`、印刷プレート表示で §6 の manifest。座標系は組立が `frame:"blender-mm"`、印刷プレートが `frame:"plate-mm"`
- 組立の下書きキーは従来どおり `studio.draft.<model>`。印刷プレートは `studio.draft.<model>.plate.<manifest.id>`。切替時に undo / redo も空にし、互いの指示を混ぜない
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
| `section:create` | `{axis?,point?,normal?,file?,copyFrom?,replaceActive?}` | app / panels | 中央、選んだ面、または複製元から断面を作る。`replaceActive` は空の断面だけ同じ ID で更新する |
| `section:created` | `{id,replaced,copyFrom}` | section | 作成または向き変更が終わった |
| `section:transform` | `{mode:"translate"|"rotate"|"off"}` | panels / app | 3D 上の断面調整を始める、または終える |
| `section:copy-required` | `{id,mode}` | section | 図形付き断面を残して複製してから調整する必要がある |
| `popover` | 下記 | picking | 確定待ちの入力を UI に出してほしい |
| `popover:close` | — | picking / panels | サイドの編集欄を閉じ、仮置きのピンを消す |
| `status` | `{text, kind}` | 誰でも | 右下の状態表示 |
| `toast` | `{text, action?}` | 誰でも | 一時通知 |
| `viewport:pointer` | `{point \| null}` | viewport | 3D でカーソル下のモデル座標（ヒント行の座標表示用、間引いて出す） |

`popover` payload:
- 面: `{kind:"faces", x, y, file, faceIds, summary}`（x,y は画面座標 px）。UI は自由メモだけを受け、`store.addItem({type:"faces", file, faceIds, summary, note})` → `store.set({selection: []})`。従来の `action / amount / side` は読み取り互換を保つ
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
  setPrintPlate({width, depth} | null),             // 256×256 mm の床と枠。getMeshes / pick / section の対象外
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
- 断面を選んだ最初の時は、モデル中央に `view` 断面を 1 枚作る。アクティブな断面があれば再利用する
- 向き変更は `section:create {axis,replaceActive:true}`。図形のない断面は更新する。図形があれば元を残して空の断面を作る
- 移動は平面の法線方向。回転は平面の局所 XYZ。Shift 中は 15° 刻みにする。道具、モデル、表示方法を替える時は `off` に戻す

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
- container の中にエディタ一式（上の道具バー・断面の自由メモ・位置入力・片側を隠す切替・閉じる、下の座標表示）を自分で作る
- 表示するのは `state.activeSectionId` の断面。`section:loops` を受けて描き直す
- 図形の編集は `store.updateItem(id, {shapes})`。ドラッグ開始で `store.checkpoint()`、ドラッグ中は `{history:false}`
- 新しい図形は `intent:"note"`。既存の図形に保存された従来の intent は描画と送信で維持する
- 位置入力は空の断面だけを直接動かす。図形がある場合は `section:copy-required` を出し、元の断面を残す
- 位置入力は `planePosition(plane, offset)` の原点から法線方向への絶対位置を表示する。入力値から `dot(plane.origin, plane.normal)` を引いた値を offset にする
- モデルと交差する輪郭が 0 本なら位置調整の案内を表示する。描画操作は止めない
- キー: `handleKey(e)` で V P L B R O A T、Delete/Backspace、Enter、Esc、Space（パン）、F（全体表示）を処理して true を返す。Ctrl+Z は返さない（app.js が store.undo）。テキスト入力中は app.js が呼ばない
- 断面が無いとき container は空でよい（app.js が表示を切り替える）

### api.js / bundle.js / panels.js / app.js / index.html / styles.css（担当 D）
- api.js: fetch の薄い包み＋ WS（再接続つき）。WS の URL は `ws://127.0.0.1:<port>`。ポートは `GET /api/config` → `{ws}`
- 上部に「シュビー」の在席表示: `GET /api/listener` → `{listening, agent, at}`（WS の `listener` でも届く）。待ち受け中 / 不在
- bundle.js: `async buildRequest({store, viewport, sections, sketch}) -> {request, images}`（faceIds を落とす、section に loops / 画像名、shape に polyline / polyline3d を足す、view.png）
- panels.js: topbar、左レール、ヒント行（道具ごとの説明と、角度・半径・軸の切替）、インスペクタ（指示 / パラメータ / 履歴）、コマンドパレット、ポップオーバー、トースト
- 履歴の見出しはメッセージ、最初の自由メモ、種類別件数の順で選ぶ。展開時は自由メモと断面画像を先に表示し、`request.json` から図形の `kind / name / text / note` だけを遅延読込する
- app.js: 起動・モデル読み込み（旧 viewer/index.html の STL 選びの規則をそのまま移植）・キーボード・配線

## 4.1 実装後に足されたもの（2026-10-07 結合時）

- viewport: `invalidate()`（描画は要るときだけ。3D を変えたら呼ぶ）、`toScreen`、`size`、`geomInfo`、`hasGeomInfo`、`clipMaterial` / `unclipMaterial`、`dispose`。`viewPreset` は向きの配列も受ける。`screenshot` はモデルの範囲に切り詰め、ピン番号・計測値のラベルを焼き込む
- frames: `planePosition(plane, offset)`。軸平面の origin は法線成分だけを持つ点（(u,v) がそのまま人の読むモデル座標になる）
- picking: `cancel()`。popover の x,y は client 座標
- slice.js の輪郭は材料が左（外周は反時計回り、穴は時計回り）。sampleShape は閉じた図形の最後に始点を繰り返す
- app.js は `window.__studio = { store, viewport, picking, sections, sketch }` を出す（動作確認用）

## 4.2 部品の見え方（通常 / 透過 / 非表示。2026-10-16）

- 状態は `store.state.partModes = { "<キー>": "ghost" | "hidden" }`（通常はキーを持たない）。**キーは部品台帳（§7）があれば部品 id、台帳が無ければ STL 名**（`part-modes.js` の `partKey(mesh.userData)`）。変更は `store.setPartMode(file, mode)` / `setPartModes` / `resetPartModes`、読み込みは `loadPartModes()`（モデルを開くたび。保存先は localStorage `studio.partModes.<model>`。下書きや undo には入れない）。純関数は `part-modes.js`
- viewport: `change:partModes` と STL 読み込みで反映する。透過 = 不透明度 0.2・深度書き込みオフ・稜線を薄く残す。非表示 = 描かない。`modelBox` は変えない
- レイキャスト: `pick(x, y, {includeGhost})` は透過・非表示の部品を素通りする（picking / section の面・ピン・測定・断面の位置決めはすべて `pick` 経由）。`pickParts(x, y)` は透過も含めてカーソル下の部品を手前から返す（`[{key, file, mode, distance}]`。右クリックメニュー用）。`getSliceMeshes()` は断面で切る部品（非表示を除く。透過は切る）。`getMeshes()` は従来どおり全部
- 操作: 3D の右クリック（動かさずに離す）でカーソル下の部品のメニュー、T でカーソル下の最も手前の部品を透過 ⇄ 通常、Shift+T で全部戻す（`part-menu.js`）。右パネルの「部品」タブ（§8）にも 3 択がある。台帳が無く STL が複数あるモデルでは、上部「パーツ」メニューの各行にも 3 択がある。部品を隠すと、その部品の未確定の面選択は外れる
- 依頼: `request.partModes`（`bundle.js`）。いま読み込んでいる部品のうち通常でないものだけを `{キー: "ghost"|"hidden"}` で入れる（台帳があれば部品 id、無ければ STL 名）。後方互換のため無くても読める

## 5. 共通 workspace と見た目

- `index.html` は `../shared/workspace.css` を Studio の CSS より先に読む。
- `../shared/workspace.mjs` の `createWorkspaceNav({active:"studio", model})` を使う。モデル変更時は返り値の `setModel(model)` を呼ぶ。
- 物理検証・組み立ての画面はモデルごとに `WORKSPACE_PAGES`（`workspace.mjs`）へ登録する。登録が無いモデルではタブを「未対応」として押せなくする。登録済み: `mystery-box-sg92r-b3-candidate`（`/viewer/physics-box`・`/viewer/assembly-box`）、`servo-lid-cube`（`/viewer/lid-cube/physics.html`・`assembly.html`）。
- 上部は `.workspace-header` と、その下の `.studio-toolbar` に分ける。共通ヘッダーには `.workspace-brand`、`.workspace-model`、`.workspace-nav` を置く。
- 送信操作は右の「指示」パネル下部に一つだけ置く。スクロール中も送信ボタンを表示する。在席と処理状態も同じパネルに置く。
- 視点は3D右上の「視点」から開く。選んだら閉じる。数字キーでも切り替えられる。
- OS の配色変更は共通 CSS と `watchTheme(callback)` に追従する。Canvas / WebGL で色が要る場合は `themePalette()` の `paper / card / ink / mute / line / accent / accentStrong` を使う。
- 共通ナビの「暗く／明るく」で配色を切り替える。選択は `model-lab.theme` に保存する。URLの `theme` 指定を優先する。画面を切り替えても選択を保つ。

### モデル一覧と保存（2026-10-07 更新）

- `/api/models` はモデルディレクトリ全件を返す。既存 `name / preview / category` を維持する。`title / description / categoryId / projectId / project / tags / status / organized / available / unavailableReason` を追加する。
- 分類は `models/catalog-groups.json`。モデルの表示情報は `models/<id>/catalog.json`。不正や欠損は未整理として表示する。`available:false` も一覧から除外しない。
- `catalog.js` の `createCatalog({store,onOpen,getModels,getRecent})` がモデルを選ぶ画面を管理する。`onOpen(name)` は永続IDを渡す。お気に入りは `studio.favorites`。最近開いたモデルは `studio.recent`。
- 寸法入力は controls の `unit / displayScale` を使う。表示値は `value * displayScale`。APIへは元の単位で送る。不明な単位は「元の値」と表示する。
- 調整した値は `studio.params.<id>` にモデル別で保存する。モデルの切替でも維持する。下書きは既存 `studio.draft.<id>`。
- 送信中は入力とモデル切替を止める。送信した後の下書きが送信開始時と一致する場合だけ空にする。
- 狭幅では `#app[data-inspector="open"]` で指示・設定を開く。道具は下部へ移す。断面は3Dの下に表示する。

Studio 内の既存名は共通トークンへの別名として残す。

```css
--bg:var(--paper); --panel:var(--paper); --raised:var(--card);
--text:var(--ink); --text-2:var(--mute);
--accent:var(--accent-strong); --accent-ink:var(--paper);
--radius:0; --radius-sm:0; --shadow:none;
font: var(--fs-sm)/1.5 var(--font-ui); 数値は var(--font-mono)
```
- 罫線は 1px。基本余白は 16px / 24px。見出しは `var(--font-heading)`。
- 3D と 2D の背景は `paper`。グリッドは `line`。材料の陰影は維持する。輪郭線は `ink`。ゴーストは `mute` の点線。
- 375px 幅では操作対象を 44px 以上にする。入力は 16px 以上。共通ヘッダー、3D、編集欄、下部の道具が重ならないようにする。

## 6. 印刷プレート

- manifest は `GET /viewer/studio/plates/<model>.json` を `cache:"no-cache"` で読む。404 はプレート未作成として扱う
- 形は `{version:1, model, kind:"plate", id, source3mf, source3mfSha256, bed:{width,depth}, parts:[...]}`
- 各 part は `{file, sourcePart, sourceFile, objectId, buildTransform, sha256, size, bbox, source:{file,sha256,size,mtime}}`。`buildTransform` は 12 数値
- `source.file / size / mtime` を `/api/stls` の一覧と照合する。時刻差は 1.1 ms まで許容する。古ければ切替と指示送信を止め、「印刷プレートを更新してください」と表示する
- 組立表示の STL 候補から `-studio-plate-` を含む派生 STL を除く。印刷プレート表示の候補は manifest の parts だけ
- `request.layout` は組立なら `{kind:"assembled"}`。印刷プレートなら `{kind:"plate",id,source3mf,source3mfSha256,manifestVersion:1}`
- 印刷プレートの `request.files` と各 item には、該当 part の `sourcePart / objectId / buildTransform / sourceFile` を写す。files には `sha256` も写す

## 7. 部品台帳（部品を人の分かる名前で扱う。2026-10-16）

シュビーとユーザーが同じ名前で部品を呼ぶためのデータ。モデル名ではなく**部品の名前**で透過・非表示・指示の対象を選べるようにする。書き出しは `py -3.11 tools/studio_parts.py [<model> ...]`（引数なしなら `models/*/build/manifest.json` を持つ全モデル）。

- 台帳は `GET /viewer/studio/parts/<model>.json`（`cache:"no-cache"`）。404 は台帳なしとして扱い、従来どおり `exports/` の STL を名前で拾う。台帳は 1 モデル 1 ファイル。ビューワーは読むだけ
- 部品の STL は `GET /exports/<file>`。`/api/stls` の一覧にも `<model>-part-<id>.stl` として並ぶ。**組立の STL 候補を選ぶ規則からは `-part-` を含む名前を除く**（台帳に載る部品として扱う。`-studio-plate-` と同じ扱い）
- 台帳が見つかったら、組立表示は「まとめた 1 個の STL」ではなく `parts[].file` を全部読んで重ねる。座標は組み立てた位置のままの mm（STL の生の値）。台帳の STL は必ず mm なので、単位を bbox から推定せず `unitScale` は 1 に固定する

```
{ "version": 1, "model": "<name>", "source": "models/<name>/build/manifest.json", "sourceSha256": "...",
  "groups": [ {"id": "pixel", "label": "画素", "color": "#e69f00"} ],
  "parts": [ {"id": "housing", "label": "外装（底と四方の壁）", "systemLabel": "外装（底と四方の壁）",
              "group": "shell", "kind": "printed", "file": "<name>-part-housing.stl",
              "sha256": "...", "size": 143484, "aliases": [], "color": "#d8d4cc"} ] }
```

| キー | 型 | 意味 |
|---|---|---|
| `version` | 1 | 形の版 |
| `model` | string | モデル名 |
| `source` / `sourceSha256` | string | 元の manifest.json と、その中身の SHA-256 |
| `groups[]` | `{id, label, color}` | 部品の群。`label` は日本語。`color` は `#rrggbb`。並びは表示順。部品が 1 個も無い群は出さない |
| `parts[]` | 配列 | manifest の `parts` と同じ並び。全部の部品が `groups` のどれかに属す |
| `parts[].id` | string | 部品の id（manifest の id そのまま。`front/panel` のように `/` を含むことがある） |
| `parts[].label` | string | **画面に出す名前**。ユーザーの呼び名があればそれ、なければ `systemLabel` |
| `parts[].systemLabel` | string | シュビーが付けた名前（manifest の label）。常にある。ユーザーの呼び名と並べて見せるときに使う |
| `parts[].group` | string | `groups[].id` のどれか |
| `parts[].kind` | `"printed"` / `"stock"` / `"jig"` | 印刷する部品 / 買ってくる既製部品（サーボなど。manifest に `print` が無い、または `stock:true`）/ 組立のときだけ使う治具（`jig:true`） |
| `parts[].file` | string | `exports/` にある組立姿勢の STL 名。`<model>-part-<id>.stl`（id の `/` は `__`） |
| `parts[].sha256` / `size` | string / number | その STL の SHA-256 とバイト数。ファイルが古いかの照合に使う |
| `parts[].aliases` | string[] | ユーザーが別の呼び方をしていた語。検索・突き合わせ用。無ければ空 |
| `parts[].color` | `#rrggbb`（任意） | manifest の色。無い部品はキーが無い |

- **群の作り方**: `models/<model>/build/ui.json` の `legendGroups` があればそれ（先に載せた群が優先。`id` は prefix か部品 id の共通の先頭から作る）。群に入らなかった部品は `jig`（組立治具）・`stock`（既製部品）・`shell`（外装）・`other`（その他）に入る。`legendGroups` が無いモデルは部品 id の接頭辞（`front/panel` の `front`、または 2 個以上が共有する `key_left` の `key`）で作り、日本語名は `tools/studio_parts.py` の `PREFIX_LABELS`。接頭辞を持たない部品は `other`
- **ユーザーの呼び名**: `models/<model>/part-names.json` = `{ "<id>": { "label": "ユーザーの呼び名", "aliases": ["別の呼び方"] } }`。どちらのキーも省略できる。ファイルが無ければ全部シュビーの名前。ユーザーが名付けたときに作る（雛形は置かない）。台帳を書き出すと `label` が置き換わり、元の名前が `systemLabel` に残る。manifest に無い id や使えないキーは書き出しが失敗する
- 同じ `label` の部品がある（F1 の「空の面板」など）。選ぶ画面では群の名前を添えて見分けること
- 台帳は `part-names.json` や manifest.json を変えたら書き出し直す。台帳の `sourceSha256` と manifest.json の SHA-256 が違えば古い

## 8. 部品の呼び名と右パネル（2026-10-16）

シュビーとユーザーが同じ名前で部品を呼ぶための画面側の約束。台帳の形は §7。純関数は `parts.js`、画面は `parts-panel.js`（右の「部品」タブ）と `part-hover.js`（3D のカーソルのそば）、共有の DOM 道具は `dom.js`。

### 組立表示と台帳

- 組立表示で台帳が見つかったら、`parts[].file` を全部読む。`viewport.loadSTLs` の項目は `{name, url, partId, unitScale: 1, color}`。mesh には `userData.partId` が付く（`placed` は false）。`store.state.ledger` が表示中の台帳（`normalizeLedger` の戻り値。印刷プレート・プレビュー・台帳なしでは null）
- 台帳の STL が `exports/` に 1 つも無ければ台帳なしとして従来の選び方に戻す。一部が無ければ状態表示で知らせ、あるものだけ読む
- 組立の STL 候補から `-part-` を含む名前を除く（`model-files.js`）。台帳があるモデルでは上部の「パーツ」メニューを隠す

### 呼び名

- ユーザーの呼び名は `store.state.partNames = { "<部品 id>": {label} }`（モデルごとに localStorage `studio.partNames.<model>`。下書きや undo には入れない）。`store.setPartName(part, text)` / `resetPartNames()` / `loadPartNames()`。台帳の `label` と同じ名前にすると上書きが消える
- 画面に出す名前は 呼び名 > 台帳の `label`。台帳の `systemLabel`（シュビーの名前）が違えば「シュビー: …」と小さく併記する。同じ名前の部品が複数あれば群名を添える（メニュー・カーソルのそば・下書き。`partName()`）
- 依頼 `request.partNames = { "<部品 id>": {label, systemLabel} }`。台帳の `label` と違うものだけ入る（無ければキー自体が無い）。`systemLabel` は台帳の `systemLabel`。受け手は `models/<name>/part-names.json` の `{id: {label}}` に書き戻し、`py -3.11 tools/studio_parts.py <model>` で台帳を書き出し直す

### 依頼の印

- `request.items[]` の各指示（faces / pin / measure / section）に、当たった部品を足す: `partId`（台帳の部品 id）、`partLabel`（いまの呼び名）、呼び名がシュビーの名前と違えば `partSystemLabel`。`file` は今までどおり残る
- 計測は 2 点目の部品が 1 点目と違うときだけ `partIdB` / `partLabelB` を足す。下書きの measure 指示は `fileB`（2 点目の STL 名）を持つ
- `request.files[]` にも `partId` / `partLabel`（台帳の部品のとき）。台帳が無い・当たらなければ、どのキーも付かない
- 送るときは 3D の強調（一覧で指している部品）を外してから `view.png` を撮る

### 右パネル（`#inspector`）

- タブは「指示」「部品」「寸法」。「部品」は台帳があるか、組立の STL が複数あるときだけ出す。「指示」の下には送信欄（在席と処理状態・送るボタン）を 1 つだけ置く
- 部品タブ: 群ごとの木（開閉は localStorage `studio.partGroups.<model>`。部品数が 6 以下の群は最初から開く）、行ごとに 通常 / 透過 / 隠す、群ごとの一括切り替え、名前・別名・id・群名での絞り込み、行の鉛筆かダブルクリックで呼び名の書き換え（Enter で決める、Esc でやめる）。台帳が無いモデルは読み込み中の STL 名を平らに並べ、書き換えはできない
- 指している部品: `store.state.partHover`（部品のキーの配列。`store.hoverParts(keys)`）。一覧の行・群の上、3D のカーソルの下（クリックで指示が付く部品）のどちらでも立つ。`viewport.setHoverParts(keys)` が 3D で強調する（隠した部品も指している間だけ薄く見せる。拾う対象にはしない）。3D では `part-hover.js` がカーソルのそばに名前と群名を出す
