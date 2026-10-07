// Studio の状態と出来事の受け渡し。モジュール同士は直接呼び合わず、ここを通す。
// 契約の説明は CONTRACT.md。ここを変えるときは CONTRACT.md も直す。

// --- 共有の定数 -------------------------------------------------------------

// 2D 断面に描く図形の意図。色は 3D の重ね描きと 2D で共通
export const INTENTS = {
  target: { label: "目標の線", hint: "この形にしたい", color: "#ff6b4a" },
  remove: { label: "削る",     hint: "囲った所を取り除く", color: "#ffb020" },
  add:    { label: "足す",     hint: "囲った所を盛る", color: "#2fd08f" },
  note:   { label: "メモ",     hint: "説明・参考", color: "#4cc3ff" },
};

// 面選択に付ける動作。signed=量に符号がある（厚く+1.5 / 薄く 1.0 は大きさだけ）
export const ACTIONS = {
  thicken: { label: "厚く",     amount: true },
  thin:    { label: "薄く",     amount: true },
  round:   { label: "丸める",   amount: true },   // 量 = 半径 mm
  smooth:  { label: "滑らかに", amount: false },
  flatten: { label: "平らに",   amount: false },
  cut:     { label: "削る",     amount: true },
  add:     { label: "足す",     amount: true },
  hole:    { label: "穴",       amount: true },   // 量 = 径 mm
  other:   { label: "その他",   amount: false },
};

// 指示カードの色（面・断面に順番に割り当てる）。ピンと計測は固定色
export const ITEM_COLORS = ["#c792ea", "#5ad1e6", "#f7c35f", "#8fd16a", "#ff8fb1", "#7aa2ff"];
export const PIN_COLOR = "#ffd166";
export const MEASURE_COLOR = "#e6e8ea";
export const SELECTION_COLOR = "#7c9cff"; // 確定前の選択（= UI のアクセント）

export const TOOLS = ["view", "faces", "pin", "measure", "section"];
export const SKETCH_TOOLS = ["select", "pen", "line", "curve", "rect", "ellipse", "arrow", "text", "dim"];

// --- store ----------------------------------------------------------------

const listeners = new Map();
const undoStack = [];
const redoStack = [];
const UNDO_MAX = 100;

function clone(x) { return JSON.parse(JSON.stringify(x)); }
function uid(prefix = "i") { return prefix + Math.random().toString(36).slice(2, 8); }

export const store = {
  state: {
    model: null,            // モデル名
    frame: "blender-mm",    // 指示座標の系。"blender-mm"（STL 生座標）| "preview-m-yup"
    files: [],              // 表示中の STL [{name, mtime}]
    tool: "view",           // TOOLS のどれか
    faceMode: "smart",      // "smart"（塗り広げ）| "brush"
    faceAngle: 20,          // 塗り広げの角度閾値（度）
    brushRadius: 5,         // ブラシ半径（mm）
    sectionAxis: "auto",    // "auto" | "x" | "y" | "z" | "view"
    selection: [],          // 確定前の選択 [faceIndex]
    selectionFile: null,    // 選択中の STL 名
    activeItemId: null,     // インスペクタで開いている指示
    activeSectionId: null,  // 2D エディタで開いている断面
    sketchTool: "select",   // SKETCH_TOOLS のどれか
    intent: "target",       // 次に描く図形の意図
    compare: null,          // 比較表示中 {label, url} | null
    draft: { message: "", items: [] },
  },

  // 購読。戻り値を呼ぶと解除
  on(evt, fn) {
    if (!listeners.has(evt)) listeners.set(evt, new Set());
    listeners.get(evt).add(fn);
    return () => listeners.get(evt)?.delete(fn);
  },
  emit(evt, payload) {
    for (const fn of listeners.get(evt) || []) {
      try { fn(payload); } catch (e) { console.error(`[store] ${evt}`, e); }
    }
  },

  // state の浅い更新。値が変わったキーごとに "change:<key>"、最後に "change"
  set(patch) {
    const changed = [];
    for (const [k, v] of Object.entries(patch)) {
      if (this.state[k] !== v) { this.state[k] = v; changed.push(k); }
    }
    for (const k of changed) this.emit(`change:${k}`, this.state[k]);
    if (changed.length) this.emit("change", changed);
  },

  // --- 下書きの指示 ---
  getItem(id) { return this.state.draft.items.find((it) => it.id === id) || null; },

  nextColor() {
    const used = this.state.draft.items.filter((it) => it.type === "faces" || it.type === "section").length;
    return ITEM_COLORS[used % ITEM_COLORS.length];
  },

  addItem(item) {
    this.checkpoint();
    const it = { id: uid(), note: "", ...item };
    if (!it.color) {
      it.color = it.type === "pin" ? PIN_COLOR : it.type === "measure" ? MEASURE_COLOR : this.nextColor();
    }
    if (it.type === "section" && !it.shapes) it.shapes = [];
    this.state.draft.items.push(it);
    this._itemsChanged("add", it.id);
    return it.id;
  },

  // history:false はドラッグ中の連続更新用。呼ぶ側がドラッグ開始時に checkpoint() する
  updateItem(id, patch, { history = true } = {}) {
    const it = this.getItem(id);
    if (!it) return;
    if (history) this.checkpoint();
    Object.assign(it, patch);
    this._itemsChanged("update", id);
  },

  removeItem(id) {
    if (!this.getItem(id)) return;
    this.checkpoint();
    this.state.draft.items = this.state.draft.items.filter((it) => it.id !== id);
    if (this.state.activeSectionId === id) this.set({ activeSectionId: null });
    if (this.state.activeItemId === id) this.set({ activeItemId: null });
    this._itemsChanged("remove", id);
  },

  setMessage(text) {
    this.state.draft.message = text;
    this._save();
  },

  clearDraft() {
    this.checkpoint();
    this.state.draft = { message: "", items: [] };
    this.set({ activeSectionId: null, activeItemId: null, selection: [] });
    this._itemsChanged("clear", null);
  },

  // --- undo / redo（下書きの items 全体のスナップショット）---
  checkpoint() {
    undoStack.push(clone(this.state.draft.items));
    if (undoStack.length > UNDO_MAX) undoStack.shift();
    redoStack.length = 0;
  },
  canUndo() { return undoStack.length > 0; },
  canRedo() { return redoStack.length > 0; },
  undo() {
    if (!undoStack.length) return false;
    redoStack.push(clone(this.state.draft.items));
    this.state.draft.items = undoStack.pop();
    this._afterRestore();
    return true;
  },
  redo() {
    if (!redoStack.length) return false;
    undoStack.push(clone(this.state.draft.items));
    this.state.draft.items = redoStack.pop();
    this._afterRestore();
    return true;
  },
  _afterRestore() {
    const ids = new Set(this.state.draft.items.map((it) => it.id));
    if (this.state.activeSectionId && !ids.has(this.state.activeSectionId)) this.set({ activeSectionId: null });
    if (this.state.activeItemId && !ids.has(this.state.activeItemId)) this.set({ activeItemId: null });
    this._itemsChanged("restore", null);
  },

  _itemsChanged(reason, id) {
    this._save();
    this.emit("items", { reason, id });
  },

  // --- 下書きの保存（モデル単位、localStorage）---
  _key() { return `studio.draft.${this.state.model}`; },
  _save() {
    if (!this.state.model) return;
    try { localStorage.setItem(this._key(), JSON.stringify(this.state.draft)); } catch { /* 無くても動く */ }
  },
  loadDraft() {
    undoStack.length = 0; redoStack.length = 0;
    let d = null;
    try { d = JSON.parse(localStorage.getItem(this._key()) || "null"); } catch { d = null; }
    this.state.draft = d && Array.isArray(d.items)
      ? { message: typeof d.message === "string" ? d.message : "", items: d.items.filter((it) => it && typeof it === "object" && typeof it.id === "string" && typeof it.type === "string") }
      : { message: "", items: [] };
    this.set({ activeSectionId: null, activeItemId: null, selection: [] });
    this.emit("items", { reason: "load", id: null });
  },

  // 右下の状態表示とトースト
  status(text, kind = "") { this.emit("status", { text, kind }); },  // kind: "" | "busy" | "ok" | "err"
  toast(text, opts = {}) { this.emit("toast", { text, ...opts }); },  // opts.action = {label, run}
};

export { uid };
