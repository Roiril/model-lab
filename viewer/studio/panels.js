// Studio の画面部品。上部バー・左レール・ヒント行・インスペクタ・サイドの編集欄・
// コマンドパレット・トースト・ツールチップ。状態は store、モデルや 3D への働きかけは ctx（app.js）経由。
// 画面の文字は日本語で短く。実装の呼び名は出さない。

import { ACTIONS, SELECTION_COLOR } from "./store.js";
import { REQUEST_STATUS, requestStatus, requestBefore } from "./api.js";
import { createCatalog } from "./catalog.js";

// --- 小さな DOM 道具 ----------------------------------------------------------

function h(tag, props, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "style") el.style.cssText = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "value" || k === "checked" || k === "disabled" || k === "hidden") el[k] = v;
    else el.setAttribute(k, v === true ? "" : v);
  }
  add(el, kids);
  return el;
}
function add(el, kids) {
  for (const k of kids.flat(Infinity)) {
    if (k === undefined || k === null || k === false) continue;
    el.append(k.nodeType ? k : document.createTextNode(String(k)));
  }
  return el;
}
const $ = (sel) => document.querySelector(sel);

// アイコン: 20px の枠、線 1.5px、自作。外部のアイコンフォントは使わない
const ICONS = {
  logo: '<path d="M10 2.5l6.5 3.6v7.8L10 17.5l-6.5-3.6V6.1z"/><path d="M3.5 6.1L10 9.8l6.5-3.7M10 9.8v7.7"/>',
  view: '<path d="M2 10c2-3.4 4.6-5.2 8-5.2s6 1.8 8 5.2c-2 3.4-4.6 5.2-8 5.2S4 13.4 2 10z"/><circle cx="10" cy="10" r="2.4"/>',
  faces: '<path d="M10 2.5l6.5 3.6v7.8L10 17.5l-6.5-3.6V6.1z"/><path d="M3.5 6.1L10 9.8l6.5-3.7M10 9.8v7.7"/><path d="M10 2.5L3.5 6.1 10 9.8l6.5-3.7z" fill="currentColor" fill-opacity=".22"/>',
  pin: '<path d="M10 17.5s5-4.4 5-8.5a5 5 0 10-10 0c0 4.1 5 8.5 5 8.5z"/><circle cx="10" cy="9" r="1.8"/>',
  measure: '<path d="M3 13.5L13.5 3 17 6.5 6.5 17z"/><path d="M5.5 11l1.6 1.6M8.25 8.25l1.6 1.6M11 5.5l1.6 1.6"/>',
  section: '<path d="M2.5 11.5L10 8l7.5 3.5L10 15z" fill="currentColor" fill-opacity=".18"/><path d="M2.5 11.5L10 8l7.5 3.5L10 15z"/><path d="M10 2.5v5.5M10 15v2.5"/>',
  close: '<path d="M5 5l10 10M15 5L5 15"/>',
  trash: '<path d="M4.5 6h11M8 6V4h4v2M6 6l.7 10h6.6L14 6M8.5 9v4.5M11.5 9v4.5"/>',
  chevron: '<path d="M5.5 8l4.5 4.5L14.5 8"/>',
  search: '<circle cx="9" cy="9" r="5"/><path d="M13 13l4 4"/>',
  send: '<path d="M17.5 2.5L2.5 8.5l5.5 2 2 5.5z"/><path d="M8 10.5l9.5-8"/>',
  undo: '<path d="M7 4L3.5 7.5 7 11"/><path d="M3.5 7.5H12a4.5 4.5 0 010 9H8"/>',
  redo: '<path d="M13 4l3.5 3.5L13 11"/><path d="M16.5 7.5H8a4.5 4.5 0 000 9h4"/>',
  focus: '<circle cx="10" cy="10" r="3"/><path d="M10 2.5v3M10 14.5v3M2.5 10h3M14.5 10h3"/>',
  plus: '<path d="M10 4v12M4 10h12"/>',
  minus: '<path d="M4 10h12"/>',
  copy: '<rect x="7" y="7" width="9" height="9" rx="1.5"/><path d="M13 7V5.5A1.5 1.5 0 0011.5 4h-6A1.5 1.5 0 004 5.5v6A1.5 1.5 0 005.5 13H7"/>',
  reset: '<path d="M4 10a6 6 0 101.8-4.3"/><path d="M4 3.5v3.5h3.5"/>',
  layers: '<path d="M10 3l7 3.5-7 3.5-7-3.5z"/><path d="M3 10l7 3.5 7-3.5M3 13.5l7 3.5 7-3.5"/>',
  check: '<path d="M4.5 10.5l3.5 3.5 7.5-8"/>',
  note: '<path d="M4 4.5h12v8H9l-3.5 3v-3H4z"/>',
  build: '<path d="M6 4l10 6-10 6z"/>',
  info: '<circle cx="10" cy="10" r="7"/><path d="M10 9v4.5M10 6.5v.2"/>',
};
function icon(name, cls = "") {
  const span = document.createElement("span");
  span.className = `ic ${cls}`.trim();
  span.setAttribute("aria-hidden", "true");
  span.innerHTML = `<svg viewBox="0 0 20 20" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">${ICONS[name] || ""}</svg>`;
  return span;
}
function tip(el, name, key) {
  el.dataset.tip = name;
  if (key) el.dataset.key = key;
  if (!el.getAttribute("aria-label")) el.setAttribute("aria-label", key ? `${name} ${key}` : name);
  return el;
}
function kbd(text) { return h("kbd", { class: "kbd" }, text); }

const num = (n) => String(Number(Number(n).toFixed(2)));
const num1 = (n) => (Math.round(n * 10) / 10).toFixed(1);
function fmtTime(iso) {
  const d = new Date(iso);
  if (!iso || Number.isNaN(d.getTime())) return "";
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getMonth() + 1}/${d.getDate()} ${p(d.getHours())}:${p(d.getMinutes())}`;
}
function fmtClock(iso) {
  const d = new Date(iso);
  if (!iso || Number.isNaN(d.getTime())) return "";
  const p = (n) => String(n).padStart(2, "0");
  return `${p(d.getHours())}:${p(d.getMinutes())}`;
}
function firstLine(s) { return String(s || "").split(/\r?\n/).find((l) => l.trim()) || ""; }
function composing(e) { return e.isComposing || e.keyCode === 229; }
function lsGet(key, fallback) {
  try { const v = localStorage.getItem(key); return v === null ? fallback : JSON.parse(v); } catch { return fallback; }
}
function lsSet(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch { /* 無くても動く */ } }
function lsRemove(key) { try { localStorage.removeItem(key); } catch { /* 無くても動く */ } }

// 道具。ショートカットは app.js が受ける
const TOOL_DEFS = [
  { id: "view",    label: "見る",     key: "V", icon: "view" },
  { id: "faces",   label: "面を選ぶ", key: "F", icon: "faces" },
  { id: "pin",     label: "ピン",     key: "P", icon: "pin" },
  { id: "measure", label: "測る",     key: "M", icon: "measure" },
  { id: "section", label: "断面",     key: "S", icon: "section" },
];
const TYPE_LABEL = { faces: "面", pin: "ピン", measure: "計測", section: "断面" };
const DEFAULT_AMOUNT = { thicken: 1.5, thin: 1, round: 2, cut: 1, add: 1, hole: 3 };
const AMOUNT_LABEL = { thicken: "厚くする量", thin: "薄くする量", round: "半径", cut: "削る量", add: "足す量", hole: "径" };
const SIDES = [["out", "外側"], ["in", "内側"], ["both", "両側"]];
function sideLabel(s) { return (SIDES.find(([v]) => v === s) || SIDES[0])[1]; }
function actionText(it) {
  const a = ACTIONS[it.action];
  if (!a) return "";
  let s = a.label;
  if (a.amount && it.amount != null) {
    if (it.action === "thicken") s += ` +${num(it.amount)}mm`;
    else if (it.action === "round") s += ` 半径 ${num(it.amount)}mm`;
    else if (it.action === "hole") s += ` 径 ${num(it.amount)}mm`;
    else s += ` ${num(it.amount)}mm`;
  }
  if ((it.action === "thicken" || it.action === "thin") && it.side) s += ` ${sideLabel(it.side)}`;
  return s;
}

// =============================================================================

export function createPanels({ store, ctx }) {
  // --- 状態（画面側だけで持つもの）---
  let models = [];
  let recent = lsGet("studio.recent", []);
  let controlsDef = [];
  let values = {};
  let defaults = {};
  let hasPreview = false;
  let mode = "none";           // "stl" | "preview" | "none"
  let hasStl = false;
  let parts = { candidates: [], shown: [], custom: false };
  let requests = [];
  let listener = null;
  let exporting = false;
  let sending = false;
  let wsUp = false;
  let tab = "notes";
  let pendingItems = false;
  let pendingReq = false;
  const expanded = new Map();
  const replyDrafts = new Map();

  const keyOf = (c) => (c.index === undefined ? c.name : `${c.name}__${c.index}`);
  const paramsKey = () => `studio.params.${store.state.model}`;
  const catalog = createCatalog({
    store,
    onOpen: (name) => ctx.openModel(name),
    getModels: () => models,
    getRecent: () => recent,
  });

  function openPalette() {
    closePopover();
    closeMenu();
    catalog.open();
  }
  function closePalette() { catalog.close(); }

  // ===========================================================================
  // ツールチップ
  // ===========================================================================
  const tooltip = h("div", { class: "tooltip", role: "tooltip" });
  document.body.append(tooltip);
  {
    let timer = null;
    let cur = null;
    const hide = () => { clearTimeout(timer); cur = null; tooltip.classList.remove("on"); };
    const show = (el) => {
      tooltip.replaceChildren(el.dataset.tip || "");
      if (el.dataset.key) tooltip.append(" ", h("kbd", { class: "kbd" }, el.dataset.key));
      tooltip.classList.add("on");
      const r = el.getBoundingClientRect();
      const tw = tooltip.offsetWidth, th = tooltip.offsetHeight;
      let x, y;
      if (el.dataset.tipPos === "right") { x = r.right + 8; y = r.top + (r.height - th) / 2; }
      else { x = r.left + (r.width - tw) / 2; y = r.bottom + 8; if (y + th > innerHeight - 8) y = r.top - th - 8; }
      x = Math.min(Math.max(8, x), innerWidth - tw - 8);
      y = Math.min(Math.max(8, y), innerHeight - th - 8);
      tooltip.style.left = `${x}px`;
      tooltip.style.top = `${y}px`;
    };
    document.addEventListener("pointerover", (e) => {
      const t = e.target.closest ? e.target.closest("[data-tip]") : null;
      if (t === cur) return;
      hide();
      cur = t;
      if (t) timer = setTimeout(() => show(t), 350);
    });
    document.addEventListener("pointerdown", hide, true);
    document.addEventListener("keydown", hide, true);
    document.addEventListener("scroll", hide, true);
    document.addEventListener("focusin", (e) => {
      const t = e.target.closest ? e.target.closest("[data-tip]") : null;
      if (t && t.matches(":focus-visible")) { hide(); cur = t; show(t); }
    });
    document.addEventListener("focusout", hide);
  }

  // ===========================================================================
  // 上部バー
  // ===========================================================================
  const topbar = $("#topbar");
  const modelNameEl = h("span", { class: "sel-name" }, "モデルを選ぶ");
  const modelBtn = h("button", { type: "button", class: "sel-btn model-select", "aria-haspopup": "dialog", onclick: () => openPalette() },
    modelNameEl, icon("chevron", "sm"), kbd("Ctrl K"));
  tip(modelBtn, "モデルを選ぶ", "Ctrl+K");
  const partsLabel = h("span", {}, "パーツ");
  const partsBtn = h("button", { type: "button", class: "sel-btn parts-select", "aria-haspopup": "menu", onclick: () => togglePartsMenu() },
    icon("layers", "sm"), partsLabel, icon("chevron", "sm"));
  partsBtn.setAttribute("aria-expanded", "false");
  tip(partsBtn, "同じモデルの STL を選んで表示する");
  const listenerDot = h("span", { class: "dot-live" });
  const listenerText = h("span", { class: "lbl-text" }, "シュビー 確認中");
  const listenerPill = h("button", { type: "button", class: "pill", "data-state": "unknown", onclick: () => noteListener() }, listenerDot, listenerText);
  const statusDot = h("span", { class: "dot-live" });
  const statusText = h("span", { class: "stat-text" }, "準備中…");
  const statusEl = h("div", { class: "stat", "data-kind": "busy", role: "status" }, statusDot, statusText);
  const sendCount = h("span", { class: "count" }, "0");
  const sendBtn = h("button", { type: "button", class: "btn primary send-btn", onclick: () => ctx.send() }, icon("send", "sm"), h("span", { class: "lbl" }, "シュビーに送る"), sendCount);
  tip(sendBtn, "下書きの指示をシュビーに送る", "Ctrl+Enter");
  const undoBtn = h("button", { type: "button", class: "icon-btn", onclick: () => store.undo() }, icon("undo"));
  const redoBtn = h("button", { type: "button", class: "icon-btn", onclick: () => store.redo() }, icon("redo"));
  const outlinesBtn = h("button", {
    type: "button", class: "btn outlines-toggle", "aria-pressed": "false",
    onclick: () => store.set({ showFaceOutlines: !store.state.showFaceOutlines }),
  }, "面の輪郭");
  tip(outlinesBtn, "すべての面の輪郭を表示");
  const inspectorToggle = h("button", {
    type: "button", class: "btn inspector-toggle", id: "inspector-toggle",
    "aria-controls": "inspector", "aria-expanded": "true",
    onclick: () => {
      const app = $("#app");
      app.dataset.inspector = app.dataset.inspector === "closed" ? "open" : "closed";
      inspectorToggle.setAttribute("aria-expanded", String(app.dataset.inspector === "open"));
    },
  }, "指示・設定");
  tip(undoBtn, "元に戻す", "Ctrl+Z");
  tip(redoBtn, "やり直す", "Ctrl+Shift+Z");

  const physicsLink = h("a", { class: "sel-btn", href: "/viewer/physics-box/index.html", hidden: true }, "物理検証");
  tip(physicsLink, "B3の蓋を物理計算で動かす");
  const assemblyLink = h("a", { class: "sel-btn", href: "/viewer/assembly-box/index.html", hidden: true }, "組立ガイド");
  tip(assemblyLink, "B3の部品を順に組む");
  topbar.append(
    h("div", { class: "logo" }, icon("logo", "logo-mark"), h("span", {}, "model-lab")),
    modelBtn, partsBtn, outlinesBtn, physicsLink, assemblyLink,
    h("div", { class: "sp" }),
    listenerPill, statusEl,
    h("div", { class: "tb-group" }, undoBtn, redoBtn),
    inspectorToggle,
    sendBtn,
  );
  if (!$("#app").dataset.inspector) $("#app").dataset.inspector = "open";
  inspectorToggle.setAttribute("aria-expanded", String($("#app").dataset.inspector !== "closed"));

  function noteListener() {
    if (listener && listener.listening) store.toast(`シュビーが待ち受けています${listener.agent ? `（${listener.agent}）` : ""}`);
    else store.toast("シュビーが待ち受けていません。チャットで「スタジオの依頼を見て」と伝えてください");
  }

  function syncTopbar() {
    physicsLink.hidden = store.state.model !== "mystery-box-sg92r-b3-candidate";
    assemblyLink.hidden = store.state.model !== "mystery-box-sg92r-b3-candidate";
    const model = models.find((m) => m.name === store.state.model);
    modelNameEl.textContent = model ? (model.title || model.name) : (store.state.model || "モデルを選ぶ");
    const n = store.state.draft.items.length;
    sendCount.textContent = String(n);
    sendCount.hidden = n === 0;
    const empty = n === 0 && !store.state.draft.message.trim();
    sendBtn.disabled = sending || empty;
    sendBtn.classList.toggle("busy", sending);
    sendBtn2.disabled = sendBtn.disabled;
    modelBtn.disabled = sending;
    messageBox.disabled = sending;
    for (const note of itemList.querySelectorAll("textarea.note")) note.disabled = sending;
    undoBtn.disabled = !(store.canUndo?.() ?? false);
    redoBtn.disabled = !(store.canRedo?.() ?? false);
    outlinesBtn.setAttribute("aria-pressed", String(!!store.state.showFaceOutlines));

    const c = parts.candidates.length;
    partsBtn.disabled = c === 0;
    partsLabel.textContent = c > 1 ? `パーツ ${parts.shown.length}/${c}` : "パーツ";
  }

  function syncListener() {
    let on = !!(listener && listener.listening);
    if (on && listener.at) {
      const t = Date.parse(listener.at);
      if (Number.isFinite(t) && Date.now() - t > 30000) on = false;
    }
    listenerPill.dataset.state = listener === null ? "unknown" : on ? "on" : "off";
    listenerText.textContent = listener === null ? "シュビー 確認中" : on ? "シュビー 待ち受け中" : "シュビー 不在";
    syncSendNote(on);
  }

  // ===========================================================================
  // 左レール
  // ===========================================================================
  const rail = $("#rail");
  const railBtns = new Map();
  for (const t of TOOL_DEFS) {
    const b = h("button", { type: "button", class: "rail-btn", "data-tool": t.id, onclick: () => ctx.setTool(t.id) },
      icon(t.icon), h("span", { class: "tool-label" }, t.label), h("span", { class: "key" }, t.key));
    tip(b, t.label, t.key);
    b.dataset.tipPos = "right";
    railBtns.set(t.id, b);
    rail.append(b);
  }
  function syncRail() {
    const preview = store.state.frame === "preview-m-yup";
    for (const [id, b] of railBtns) {
      b.setAttribute("aria-pressed", String(store.state.tool === id));
      b.classList.toggle("locked", preview && id !== "view");
    }
  }

  // ===========================================================================
  // 3D 上の小物（視点ボタン・比較の表示）
  // ===========================================================================
  // 視点ボタンは viewport.js が 3D の右上に自分で出す。ここは比較表示の印だけ
  const viewtools = $("#viewtools");
  const compareLabel = h("span", {}, "");
  const compareChip = h("div", { class: "compare-chip", hidden: true },
    icon("layers", "sm"), compareLabel,
    h("button", { type: "button", class: "link", onclick: () => ctx.clearCompare() }, "解除"));
  viewtools.append(compareChip);
  function syncCompare() {
    const c = store.state.compare;
    compareChip.hidden = !c;
    if (c) compareLabel.textContent = `${c.label || "変更前"}を重ねて表示中`;
    refreshRequestButtons();
  }

  // ===========================================================================
  // ヒント行
  // ===========================================================================
  const hintbar = $("#hintbar");
  const hintMain = h("div", { class: "hint-main" });
  const hintSet = h("div", { class: "hint-set" });
  const selEl = h("span", { class: "sel-count", hidden: true });
  const warnEl = h("span", { class: "warn-chip", hidden: true });
  const coordEl = h("span", { class: "coord mono" }, "");
  hintbar.append(hintMain, hintSet, h("div", { class: "hint-right" }, selEl, warnEl, coordEl));
  let hintKey = "";
  let hintSyncs = [];

  function segmented(opts, get, set, label) {
    const el = h("div", { class: "seg", role: "group", "aria-label": label });
    const btns = opts.map(([v, text, tipText]) => {
      const b = h("button", { type: "button", class: "seg-btn", onclick: () => set(v) }, text);
      if (tipText) tip(b, tipText);
      el.append(b);
      return [v, b];
    });
    const sync = () => { for (const [v, b] of btns) b.setAttribute("aria-pressed", String(get() === v)); };
    sync();
    return { el, sync };
  }

  function stepper(get, set, { min, max, step, unit }) {
    const input = h("input", { type: "number", class: "field num", min: String(min), max: String(max), step: String(step), "aria-label": "ブラシの半径" });
    const clamp = (v) => Math.min(max, Math.max(min, v));
    const minus = h("button", { type: "button", class: "icon-btn sm", onclick: () => set(clamp(get() - step)) }, icon("minus"));
    const plus = h("button", { type: "button", class: "icon-btn sm", onclick: () => set(clamp(get() + step)) }, icon("plus"));
    tip(minus, "小さく", "[");
    tip(plus, "大きく", "]");
    input.addEventListener("change", () => { const v = parseFloat(input.value); if (!Number.isNaN(v)) set(clamp(v)); else input.value = get(); });
    const el = h("div", { class: "stepper" }, minus, input, h("span", { class: "unit" }, unit), plus);
    const sync = () => { if (document.activeElement !== input) input.value = get(); };
    sync();
    return { el, sync };
  }

  function renderHint() {
    const s = store.state;
    const preview = s.frame === "preview-m-yup";
    const key = `${s.tool}|${preview}|${s.faceMode}|${hasStl}`;
    if (key !== hintKey) {
      hintKey = key;
      hintSyncs = [];
      hintMain.replaceChildren();
      hintSet.replaceChildren();
      const tool = TOOL_DEFS.find((t) => t.id === s.tool) || TOOL_DEFS[0];
      if (preview) {
        hintMain.append(icon("info", "sm"), h("span", { class: "hint-text" }, "プレビュー表示中は指示を付けられません。指示を付けるには STL を表示します。"));
        const b = h("button", { type: "button", class: "btn sm", disabled: !hasStl, onclick: () => ctx.showStl() }, icon("faces", "sm"), hasStl ? "STL を表示" : "STL がまだありません");
        hintMain.append(b);
      } else {
        hintMain.append(icon(tool.icon, "sm"), h("span", { class: "hint-text" }, hintText(s)));
        if (s.tool === "faces") {
          const mode = segmented([["smart", "塗り広げ"], ["brush", "ブラシ"]], () => store.state.faceMode, (v) => store.set({ faceMode: v }), "選び方");
          hintSyncs.push(mode.sync);
          hintSet.append(mode.el);
          if (s.faceMode === "smart") {
            const val = h("span", { class: "val mono" }, "");
            const slider = h("input", { type: "range", class: "slider", min: "5", max: "60", step: "1", "aria-label": "つながりの角度" });
            slider.addEventListener("input", () => store.set({ faceAngle: parseFloat(slider.value) }));
            tip(slider, "この角度までなら同じ面として選ぶ");
            hintSet.append(h("label", { class: "set-item" }, h("span", { class: "set-label" }, "角度"), slider, val));
            hintSyncs.push(() => { if (parseFloat(slider.value) !== store.state.faceAngle) slider.value = store.state.faceAngle; val.textContent = `${store.state.faceAngle}°`; });
          } else {
            const st = stepper(() => store.state.brushRadius, (v) => store.set({ brushRadius: v }), { min: 1, max: 100, step: 1, unit: "mm" });
            hintSet.append(h("div", { class: "set-item" }, h("span", { class: "set-label" }, "半径"), st.el, kbd("[ ]")));
            hintSyncs.push(st.sync);
          }
        } else if (s.tool === "section") {
          const ax = segmented(
            [["auto", "自動"], ["x", "X"], ["y", "Y"], ["z", "Z"], ["view", "視線"]],
            () => store.state.sectionAxis, (v) => store.set({ sectionAxis: v }), "切る向き");
          hintSyncs.push(ax.sync);
          hintSet.append(h("div", { class: "set-item" }, h("span", { class: "set-label" }, "向き"), ax.el));
        }
      }
    }
    for (const f of hintSyncs) f();
    const n = s.selection.length;
    selEl.hidden = n === 0;
    if (n) selEl.textContent = `選択 ${n.toLocaleString("ja-JP")} 面`;
  }
  function hintText(s) {
    switch (s.tool) {
      case "faces":
        return s.faceMode === "brush"
          ? "ドラッグで面を塗る。Shift で追加、Alt で外す。B で塗り広げに戻す"
          : "クリックで滑らかにつながった面を選ぶ。Shift で追加、Alt で外す。B でブラシ";
      case "pin": return "面をクリックしてピンを立てる。メモを書いて追加します";
      case "measure": return "2 点をクリックして距離を測る。Shift で X・Y・Z のどれかに揃える";
      case "section": return "面をクリックして、その位置で切る。向きは右のボタンで選ぶ";
      default: return "ドラッグで回す。右ドラッグで動かす。ホイールで拡大縮小。数字キーで視点を切り替え";
    }
  }
  function syncWarn() {
    const placed = ctx.placedFiles ? ctx.placedFiles() : [];
    warnEl.hidden = placed.length === 0;
    if (placed.length) {
      warnEl.textContent = "配置済みの STL かもしれません";
      warnEl.title = `印刷用に並べ直した形の可能性があります（${placed.join(", ")}）。指示の座標は並べ直した後の位置になります`;
    }
  }

  // ===========================================================================
  // インスペクタ
  // ===========================================================================
  const inspector = $("#inspector");
  const tabNotesBtn = h("button", { type: "button", role: "tab", id: "tab-notes-btn", "aria-controls": "tab-notes", onclick: () => setTab("notes") },
    "指示", h("span", { class: "tab-count", hidden: true }));
  const tabParamsBtn = h("button", { type: "button", role: "tab", id: "tab-params-btn", "aria-controls": "tab-params", onclick: () => setTab("params") }, "寸法・設定");
  const tabButtons = [tabNotesBtn, tabParamsBtn];
  const tabCount = tabNotesBtn.querySelector(".tab-count");

  // 指示タブ
  const itemList = h("div", { class: "cards" });
  const draftCount = h("span", { class: "sec-count" }, "");
  const messageBox = h("textarea", { class: "field msg", rows: "3", placeholder: "全体へのメッセージ（例: 付け根をもう少し太くして）", "aria-label": "全体のメッセージ" });
  messageBox.addEventListener("input", () => { store.setMessage(messageBox.value); syncTopbar(); });
  const sendNote = h("p", { class: "send-note", "data-state": "unknown" }, "");
  const sendBtn2 = h("button", { type: "button", class: "btn primary block", onclick: () => ctx.send() }, icon("send", "sm"), "シュビーに送る", kbd("Ctrl Enter"));
  const reqList = h("div", { class: "cards" });
  const reqCount = h("span", { class: "sec-count" }, "");
  const notesPanel = h("div", { class: "tabpanel", id: "tab-notes", role: "tabpanel", "aria-labelledby": "tab-notes-btn" },
    h("div", { class: "scroll" },
      h("div", { class: "sec-head" }, h("h2", {}, "下書き"), draftCount),
      itemList,
      h("div", { class: "msg-box" }, messageBox, sendBtn2, sendNote),
      h("div", { class: "sec-head" }, h("h2", {}, "これまでの依頼"), reqCount),
      reqList));

  function setTab(t) {
    tab = t;
    tabNotesBtn.setAttribute("aria-selected", String(t === "notes"));
    tabParamsBtn.setAttribute("aria-selected", String(t === "params"));
    tabNotesBtn.tabIndex = t === "notes" ? 0 : -1;
    tabParamsBtn.tabIndex = t === "params" ? 0 : -1;
    notesPanel.hidden = t !== "notes";
    paramsPanel.hidden = t !== "params";
  }
  for (const [index, button] of tabButtons.entries()) {
    button.addEventListener("keydown", (e) => {
      let next = index;
      if (e.key === "ArrowRight") next = (index + 1) % tabButtons.length;
      else if (e.key === "ArrowLeft") next = (index - 1 + tabButtons.length) % tabButtons.length;
      else if (e.key === "Home") next = 0;
      else if (e.key === "End") next = tabButtons.length - 1;
      else return;
      e.preventDefault();
      setTab(next === 0 ? "notes" : "params");
      tabButtons[next].focus();
    });
  }

  // --- 下書きの指示カード ---
  function itemSummary(it, pinNo) {
    switch (it.type) {
      case "faces": {
        const n = (it.summary && it.summary.faceCount) ?? (it.faceIds ? it.faceIds.length : 0);
        const th = it.summary && it.summary.thickness;
        return {
          t1: `面 ${n.toLocaleString("ja-JP")} 枚 · ${actionText(it)}`,
          t2: th ? `今の肉厚 ${num1(th.min)}〜${num1(th.median)} mm` : "",
        };
      }
      case "pin": return { t1: `ピン ${pinNo}`, t2: "" };
      case "measure": return { t1: `計測 ${num1(it.distance || 0)} mm`, t2: "" };
      case "section": {
        const axis = it.plane && it.plane.axis;
        const label = axis === "view" ? "視線" : (axis || "").toUpperCase();
        const t2 = it.offset ? `位置 ${it.offset > 0 ? "+" : ""}${num1(it.offset)} mm` : "";
        return { t1: `${label} 断面 · 図形 ${(it.shapes || []).length}`, t2 };
      }
      default: return { t1: it.type, t2: "" };
    }
  }

  function itemCard(it, pinNo) {
    const sum = itemSummary(it, pinNo);
    const note = h("textarea", { class: "field note", rows: "1", placeholder: "メモ", "aria-label": "この指示のメモ", value: it.note || "", disabled: sending });
    let checkpointed = false;
    note.addEventListener("focus", () => { checkpointed = false; });
    note.addEventListener("input", () => {
      if (!checkpointed) { store.checkpoint(); checkpointed = true; }
      store.updateItem(it.id, { note: note.value }, { history: false });
    });
    note.addEventListener("keydown", (e) => { if (e.key === "Escape") note.blur(); });

    const focusBtn = h("button", { type: "button", class: "icon-btn sm", onclick: () => store.emit("item:focus", { id: it.id }) }, icon("focus"));
    tip(focusBtn, "この指示が見える向きにする");
    const delBtn = h("button", { type: "button", class: "icon-btn sm danger", onclick: () => store.removeItem(it.id) }, icon("trash"));
    tip(delBtn, "この指示を消す", "Delete");

    const opener = h("button", { type: "button", class: "card-opener", "aria-label": `${sum.t1} を開く` },
      h("span", { class: "dot", style: `--c:${it.color}` }),
      icon(it.type, "type-ic"),
      h("div", { class: "card-title" }, h("div", { class: "t1" }, sum.t1), sum.t2 ? h("div", { class: "t2" }, sum.t2) : null));
    const head = h("div", { class: "card-head" }, opener, h("div", { class: "card-actions" }, focusBtn, delBtn));
    const activate = () => {
      store.set({ activeItemId: it.id });
      if (it.type === "section") store.set({ activeSectionId: it.id });
    };
    opener.addEventListener("click", activate);
    return h("article", { class: "card item", "data-id": it.id, "data-type": it.type, style: `--c:${it.color}` }, head, note);
  }

  function renderItems() {
    pendingItems = false;
    const items = store.state.draft.items;
    itemList.replaceChildren();
    if (!items.length) {
      itemList.append(h("p", { class: "empty" }, "左の道具で面・ピン・断面を選ぶと、ここに指示が並びます。"));
    }
    let pinNo = 0;
    for (const it of items) {
      if (it.type === "pin") pinNo += 1;
      itemList.append(itemCard(it, pinNo));
    }
    syncCounts();
    markActive(false);
  }
  function syncCounts() {
    const n = store.state.draft.items.length;
    draftCount.textContent = n ? `${n} 件` : "";
    tabCount.hidden = n === 0;
    tabCount.textContent = String(n);
    syncTopbar();
  }
  function markActive(scroll) {
    const id = store.state.activeItemId;
    for (const el of itemList.querySelectorAll(".card.item")) {
      const on = el.dataset.id === id;
      el.classList.toggle("active", on);
      if (on && scroll) el.scrollIntoView({ block: "nearest" });
    }
  }
  function onItems({ reason }) {
    if (reason === "load" || reason === "clear" || reason === "restore") messageBox.value = store.state.draft.message;
    const a = document.activeElement;
    if (reason === "update" && a && itemList.contains(a) && a.matches(".note")) {
      pendingItems = true;
      syncCounts();
      return;
    }
    renderItems();
  }
  itemList.addEventListener("focusout", () => { if (pendingItems) setTimeout(() => { if (pendingItems && !itemList.contains(document.activeElement)) renderItems(); }, 0); });

  function syncSendNote(on) {
    if (listener === null) {
      sendNote.dataset.state = "unknown"; sendNote.textContent = "";
    } else if (on) {
      sendNote.dataset.state = "on";
      sendNote.textContent = "シュビーが待ち受けています。送るとすぐ対応が始まります。";
    } else {
      sendNote.dataset.state = "off";
      sendNote.textContent = "シュビーが待ち受けていません。チャットで「スタジオの依頼を見て」と伝えてください。";
    }
  }

  // --- 依頼の一覧 ---
  function statusLine(line, index) {
    const who = line.from === "shubie" ? "シュビー" : "あなた";
    switch (line.status) {
      case "open": return index > 0 ? `${who}が開き直しました` : null;
      case "working": return line.claim ? `${line.claim} が対応を始めました` : "シュビーが対応を始めました";
      case "done": return "シュビーが直しました";
      case "question": return "シュビーから質問があります";
      case "closed": return `${who}が閉じました`;
      default: return null;
    }
  }
  function bubble(from, text, at) {
    const mine = from !== "shubie";
    return h("div", { class: `bubble ${mine ? "me" : "shubie"}` },
      h("div", { class: "bubble-meta" }, mine ? "あなた" : "シュビー", h("span", { class: "mono" }, fmtClock(at))),
      h("div", { class: "bubble-text" }, text));
  }
  function typeSummary(r) {
    const count = {};
    for (const it of r.items || []) count[it.type] = (count[it.type] || 0) + 1;
    const parts2 = Object.entries(count).map(([t, n]) => `${TYPE_LABEL[t] || t} ${n} 件`);
    return parts2.length ? parts2.join(" · ") : (r.itemCount ? `指示 ${r.itemCount} 件` : "メッセージのみ");
  }

  function requestCard(r, newestOpenId) {
    const st = requestStatus(r);
    const def = REQUEST_STATUS[st] || { label: st };
    const defaultOpen = st === "working" || st === "question" || r.id === newestOpenId;
    const isOpen = expanded.has(r.id) ? expanded.get(r.id) : defaultOpen;
    const el = h("article", { class: "req", "data-st": st, "data-open": String(isOpen), "data-id": r.id });
    el.append(h("button", {
      type: "button", class: "req-head", "aria-expanded": String(isOpen),
      onclick: () => { expanded.set(r.id, !isOpen); renderRequests(true); },
    },
    h("span", { class: "badge", "data-st": st }, def.label),
    h("span", { class: "req-msg" }, firstLine(r.message) || typeSummary(r)),
    h("span", { class: "req-time mono" }, fmtTime(r.createdAt)),
    icon("chevron", "sm chev")));
    if (!isOpen) return el;

    const body = h("div", { class: "req-body" });
    if (firstLine(r.message)) body.append(h("div", { class: "req-meta" }, typeSummary(r)));
    const thread = h("div", { class: "thread" });
    if (r.message) thread.append(bubble("user", r.message, r.createdAt));
    (r.thread || []).forEach((line, i) => {
      if (line.kind === "message") thread.append(bubble(line.from, line.text, line.at));
      else if (line.kind === "status") {
        const t = statusLine(line, i);
        if (t) thread.append(h("div", { class: "tl-line" }, t, h("span", { class: "mono" }, fmtClock(line.at))));
      }
    });
    body.append(thread);

    if (st === "question") body.append(h("p", { class: "ask-note" }, "シュビーが質問しています。下に返事を書いてください。"));

    if (st === "closed") {
      body.append(h("div", { class: "req-actions" },
        h("button", { type: "button", class: "btn sm", onclick: () => ctx.reopenRequest(r.id) }, "開き直す")));
    } else {
      const reply = h("textarea", { class: "field reply", rows: "2", placeholder: "追記する（Enter で送る、Shift+Enter で改行）", "aria-label": "追記" });
      reply.value = replyDrafts.get(r.id) || "";
      reply.addEventListener("input", () => replyDrafts.set(r.id, reply.value));
      const submit = () => {
        const text = reply.value.trim();
        if (!text) return;
        replyDrafts.delete(r.id);
        reply.value = "";
        ctx.replyRequest(r.id, text);
      };
      reply.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && e.ctrlKey && !composing(e)) { e.preventDefault(); e.stopPropagation(); submit(); }
        else if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !composing(e)) { e.preventDefault(); submit(); }
        else if (e.key === "Escape") reply.blur();
      });
      body.append(h("div", { class: "reply-row" }, reply, h("button", { type: "button", class: "btn sm", onclick: submit }, "追記")));
      const actions = h("div", { class: "req-actions" });
      actions.append(compareButton(r, st));
      actions.append(h("button", { type: "button", class: "btn sm subtle", onclick: () => ctx.closeRequest(r.id) }, "閉じる"));
      body.append(actions);
    }
    el.append(body);
    return el;
  }

  function compareButton(r, st) {
    const shown = (store.state.files || []).map((f) => f.name);
    if (!requestBefore(r, shown)) return h("span", { class: "muted sm" }, "変更前の STL はありません");
    const comparing = store.state.compare && store.state.compare.id === r.id;
    const b = h("button", {
      type: "button", "data-compare": r.id,
      class: `btn sm ${!comparing && st === "done" ? "primary" : ""}`,
      onclick: () => (comparing ? ctx.clearCompare() : ctx.compare(r)),
    }, icon("layers", "sm"), comparing ? "比較を解除" : "変更前と重ねる");
    return b;
  }
  // 比較の状態が変わったとき、一覧を作り直さずにボタンだけ直す
  function refreshRequestButtons() {
    for (const b of reqList.querySelectorAll("[data-compare]")) {
      const r = requests.find((x) => x.id === b.dataset.compare);
      if (!r) continue;
      const st = requestStatus(r);
      b.replaceWith(compareButton(r, st));
    }
  }

  function renderRequests(force) {
    const a = document.activeElement;
    if (!force && a && reqList.contains(a) && a.matches("textarea")) { pendingReq = true; return; }
    pendingReq = false;
    reqList.replaceChildren();
    reqCount.textContent = requests.length ? `${requests.length} 件` : "";
    if (!requests.length) {
      reqList.append(h("p", { class: "empty" }, "まだ送った依頼はありません。"));
      return;
    }
    const newestOpen = requests.find((r) => requestStatus(r) !== "closed");
    for (const r of requests) reqList.append(requestCard(r, newestOpen && newestOpen.id));
  }
  reqList.addEventListener("focusout", () => {
    if (pendingReq) setTimeout(() => { if (pendingReq && !reqList.contains(document.activeElement)) renderRequests(true); }, 0);
  });

  // --- パラメータタブ ---
  const modeNote = h("div", { class: "mode-note" });
  const ctrlList = h("div", { class: "params" });
  const paramFields = new Map();
  const exportBtn = h("button", { type: "button", class: "btn primary block", onclick: () => { if (validateParams()) ctx.exportStl(); } }, icon("build", "sm"), "STL 生成");
  const resetBtn = h("button", { type: "button", class: "btn", onclick: () => resetParams() }, icon("reset", "sm"), "既定に戻す");
  const copyBtn = h("button", { type: "button", class: "btn", onclick: () => copyParams() }, icon("copy", "sm"), "コピー");
  const paramsPanel = h("div", { class: "tabpanel", id: "tab-params", role: "tabpanel", "aria-labelledby": "tab-params-btn", hidden: true },
    h("div", { class: "scroll" }, modeNote, ctrlList),
    h("div", { class: "params-foot" }, h("div", { class: "row2" }, resetBtn, copyBtn), exportBtn));

  inspector.append(
    h("div", { class: "tabs", role: "tablist" }, tabNotesBtn, tabParamsBtn),
    notesPanel, paramsPanel);

  function rangeFor(c) {
    const v = c.value;
    if (c.isInt) return { min: Math.max(0, Math.round(v) - Math.max(1, Math.abs(v))), max: Math.round(v) * 3 || 10, step: 1 };
    if (v === 0) return { min: -0.05, max: 0.05, step: 0.0005 };
    const a = Math.abs(v);
    const min = v > 0 ? 0 : v - 2 * a;
    const max = v > 0 ? v * 2.5 : 0;
    return { min, max, step: (max - min) / 200 };
  }

  function displayScaleFor(c) {
    const scale = Number(c.displayScale);
    return c.unit === "mm" && Number.isFinite(scale) && scale > 0 ? scale : 1;
  }
  function toDisplay(c, raw) { return raw * displayScaleFor(c); }
  function toRaw(c, display) { return display / displayScaleFor(c); }
  function cleanNumber(v) { return Number(Number(v).toPrecision(12)); }
  function displayStepFor(c, rawStep) {
    if (c.isInt) return 1;
    if (c.unit === "mm") return 0.01;
    if (c.unit === "°") return 0.1;
    return cleanNumber(rawStep * displayScaleFor(c));
  }
  function alignedDisplayRange(c, rawRange, current) {
    const scale = displayScaleFor(c);
    const step = displayStepFor(c, rawRange.step);
    const min = current + Math.floor((rawRange.min * scale - current) / step) * step;
    const max = current + Math.ceil((rawRange.max * scale - current) / step) * step;
    return { min: cleanNumber(Math.min(min, current)), max: cleanNumber(Math.max(max, current)), step };
  }
  function savedParams() {
    const saved = lsGet(paramsKey(), null);
    return saved && saved.values && typeof saved.values === "object" ? saved.values : null;
  }
  function saveParams() {
    if (store.state.model) lsSet(paramsKey(), { values: collectParams() });
  }

  function collectParams() {
    const out = {};
    for (const c of controlsDef) {
      if (c.index === undefined) out[c.name] = values[keyOf(c)];
      else { (out[c.name] ||= [])[c.index] = values[keyOf(c)]; }
    }
    return out;
  }

  function buildParams() {
    ctrlList.replaceChildren();
    paramFields.clear();
    if (!controlsDef.length) {
      ctrlList.append(h("p", { class: "empty" }, "このモデルには調整できる数値がありません。"));
      return;
    }
    for (const [index, c] of controlsDef.entries()) {
      const key = keyOf(c);
      const r = rangeFor(c);
      const dispName = c.index === undefined ? c.name : `${c.name}[${c.index}]`;
      const currentDisplay = cleanNumber(toDisplay(c, values[key]));
      const unit = c.unit || "元の値";
      const displayRange = alignedDisplayRange(c, r, currentDisplay);
      const errorId = `param-error-${index}`;
      const numIn = h("input", {
        type: "number", class: "field num", step: "any", value: String(currentDisplay),
        "aria-label": `${c.label || dispName} の値（${unit}）`, "aria-describedby": errorId,
      });
      const slider = h("input", {
        type: "range", class: "slider", min: String(displayRange.min), max: String(displayRange.max),
        step: String(displayRange.step), value: String(currentDisplay), "aria-label": `${c.label || dispName} のスライダー（${unit}）`,
      });
      const error = h("p", { class: "field-error", id: errorId, role: "alert", hidden: true }, "数値を入力してください。");
      const rowReset = h("button", { type: "button", class: "icon-btn xs", onclick: () => { setRawValue(defaults[key]); } }, icon("reset"));
      tip(rowReset, "この値だけ既定に戻す");
      const row = h("div", { class: "p-row" },
        h("div", { class: "p-head" },
          h("div", { class: "p-name", title: dispName },
            h("span", { class: "p-label" }, c.label || dispName),
            c.label && c.label !== dispName ? h("span", { class: "p-key mono" }, dispName) : null),
          rowReset, h("div", { class: "p-input" }, numIn, h("span", { class: "unit" }, unit))),
        slider, error);
      const syncChanged = () => { row.classList.toggle("changed", values[key] !== defaults[key]); };
      const setInvalid = (invalid) => {
        numIn.setAttribute("aria-invalid", String(invalid));
        error.hidden = !invalid;
      };
      const alignSliderRange = (display) => {
        const step = Number(slider.step);
        const min = display + Math.floor((Number(slider.min) - display) / step) * step;
        const max = display + Math.ceil((Number(slider.max) - display) / step) * step;
        slider.min = String(cleanNumber(Math.min(min, display)));
        slider.max = String(cleanNumber(Math.max(max, display)));
      };
      const commitRaw = (raw, { syncInput = true } = {}) => {
        if (!Number.isFinite(raw)) { setInvalid(true); return false; }
        const next = c.isInt ? Math.round(raw) : raw;
        values[key] = cleanNumber(next);
        const display = cleanNumber(toDisplay(c, values[key]));
        alignSliderRange(display);
        slider.value = String(display);
        if (syncInput || c.isInt) numIn.value = String(display);
        setInvalid(false);
        syncChanged();
        saveParams();
        ctx.paramsChanged();
        return true;
      };
      const validate = ({ commit = true } = {}) => {
        const display = numIn.value.trim() === "" ? NaN : Number(numIn.value);
        if (!Number.isFinite(display)) { setInvalid(true); return false; }
        if (!commit) { setInvalid(false); return true; }
        return commitRaw(toRaw(c, display), { syncInput: false });
      };
      function setRawValue(raw) { commitRaw(raw); }
      slider.addEventListener("input", () => commitRaw(toRaw(c, Number(slider.value))));
      numIn.addEventListener("input", validate);
      numIn.addEventListener("change", () => {
        if (validate({ commit: false })) numIn.value = String(cleanNumber(toDisplay(c, values[key])));
      });
      paramFields.set(key, { input: numIn, validate: () => validate({ commit: false }) });
      setInvalid(false);
      syncChanged();
      ctrlList.append(row);
    }
  }
  function validateParams() {
    let first = null;
    for (const field of paramFields.values()) {
      if (!field.validate() && !first) first = field.input;
    }
    if (first) {
      first.focus({ preventScroll: true });
      first.scrollIntoView({ block: "nearest" });
      return false;
    }
    return true;
  }
  function resetParams() {
    lsRemove(paramsKey());
    for (const c of controlsDef) values[keyOf(c)] = defaults[keyOf(c)];
    buildParams();
    ctx.paramsChanged();
  }
  async function copyParams() {
    const p = collectParams();
    const lines = [`# ${store.state.model} params`];
    for (const [k, v] of Object.entries(p)) lines.push(`${k} = ${Array.isArray(v) ? `(${v.join(", ")})` : v}`);
    const text = lines.join("\n");
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = h("textarea", { value: text, style: "position:fixed;left:-999px" });
      document.body.append(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
    }
    store.toast("パラメータをコピーしました");
  }

  function syncModeNote() {
    modeNote.replaceChildren();
    modeNote.hidden = false;
    if (hasPreview && mode === "preview") {
      modeNote.append(h("p", {}, "スライダーを動かすとすぐ見た目に反映されます。指示を付けるときは STL を表示します。"),
        h("button", { type: "button", class: "btn sm", disabled: !hasStl, onclick: () => ctx.showStl() }, icon("faces", "sm"), hasStl ? "指示を付けるには STL を表示" : "STL がまだありません"));
    } else if (hasPreview && mode === "stl") {
      modeNote.append(h("p", {}, "STL を表示中です。スライダーを動かすとプレビューに切り替わります。"),
        h("button", { type: "button", class: "btn sm", onclick: () => ctx.showPreview() }, icon("view", "sm"), "プレビューを表示"));
    } else {
      modeNote.append(h("p", {}, "このモデルには即時プレビューがありません。値を変えたら「STL 生成」で作り直します。"));
    }
    modeNote.append(h("p", { class: "saved-note" }, "調整値はモデルごとにこのブラウザへ保存されます。"));
    exportBtn.disabled = exporting || !store.state.model;
    exportBtn.replaceChildren(icon("build", "sm"), exporting ? "生成中…（Blender）" : "STL 生成");
    exportBtn.classList.toggle("busy", exporting);
  }

  // ===========================================================================
  // パーツのメニュー
  // ===========================================================================
  let menuEl = null;
  let menuOrigin = null;
  function closeMenu({ restoreFocus = true } = {}) {
    if (!menuEl) return;
    menuEl.remove(); menuEl = null;
    partsBtn.setAttribute("aria-expanded", "false");
    const origin = menuOrigin;
    menuOrigin = null;
    if (restoreFocus && origin && origin.focus && document.contains(origin)) origin.focus({ preventScroll: true });
  }
  function togglePartsMenu() {
    if (menuEl) { closeMenu(); return; }
    menuOrigin = document.activeElement;
    renderPartsMenu({ initial: true });
  }
  function renderPartsMenu({ initial = false } = {}) {
    const prev = menuEl;
    const scrollTop = prev ? prev.scrollTop : 0;
    const focusedPart = prev && prev.contains(document.activeElement) ? document.activeElement.dataset.part : null;
    if (prev) prev.remove();
    const el = h("div", { class: "menu", role: "menu", "aria-label": "表示するパーツ" });
    const options = [];
    el.append(h("div", { class: "menu-head" }, "表示するパーツ"));
    if (!parts.candidates.length) el.append(h("p", { class: "empty" }, "STL がまだありません。"));
    for (const name of parts.candidates) {
      const on = parts.shown.includes(name);
      const row = h("button", {
        type: "button", class: "menu-row", role: "menuitemcheckbox", "aria-checked": String(on),
        tabindex: "-1", "data-part": name,
        onclick: () => {
          let next = on ? parts.shown.filter((n) => n !== name) : [...parts.shown, name];
          if (!next.length) return; // 1 つは残す
          next = parts.candidates.filter((n) => next.includes(n));
          ctx.setParts(next);
        },
      }, h("span", { class: "check" }, on ? icon("check", "sm") : null), h("span", { class: "menu-name mono" }, name));
      el.append(row);
      options.push(row);
    }
    if (parts.custom) {
      const reset = h("button", { type: "button", class: "menu-row reset", role: "menuitem", tabindex: "-1", "data-part": "__auto", onclick: () => ctx.setParts(null) }, icon("reset", "sm"), "自動で選ぶ");
      el.append(reset);
      options.push(reset);
    }
    el.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !composing(e)) {
        e.preventDefault(); e.stopPropagation(); closeMenu(); return;
      }
      if (!options.length) return;
      const current = options.indexOf(document.activeElement);
      let next = current < 0 ? 0 : current;
      if (e.key === "ArrowDown") next = (next + 1) % options.length;
      else if (e.key === "ArrowUp") next = (next - 1 + options.length) % options.length;
      else if (e.key === "Home") next = 0;
      else if (e.key === "End") next = options.length - 1;
      else return;
      e.preventDefault();
      options.forEach((option, i) => { option.tabIndex = i === next ? 0 : -1; });
      options[next].focus();
    });
    document.body.append(el);
    const r = partsBtn.getBoundingClientRect();
    el.style.left = `${Math.min(r.left, innerWidth - el.offsetWidth - 8)}px`;
    el.style.top = `${r.bottom + 6}px`;
    el.scrollTop = scrollTop;
    menuEl = el;
    partsBtn.setAttribute("aria-expanded", "true");
    const target = options.find((option) => option.dataset.part === focusedPart)
      || options.find((option) => option.getAttribute("aria-checked") === "true")
      || options[0];
    if (target) {
      target.tabIndex = 0;
      if (initial || focusedPart) target.focus({ preventScroll: true });
    }
  }
  document.addEventListener("pointerdown", (e) => {
    if (menuEl && !menuEl.contains(e.target) && !partsBtn.contains(e.target)) closeMenu();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && menuEl && !composing(e)) { e.preventDefault(); closeMenu(); }
  });

  // ===========================================================================
  // サイドの編集欄（面の動作・ピンのメモ）。3D の操作を妨げない。
  // ===========================================================================
  const popLayer = $("#layer-popover");
  inspector.prepend(popLayer);
  let pop = null;

  function closePopover({ restoreFocus = true, notify = true } = {}) {
    if (!pop) return;
    const { prevFocus } = pop;
    pop.el.remove();
    pop = null;
    delete inspector.dataset.editing;
    // 仮ピンも消す。イベントから呼ばれたときは再通知しない。
    if (notify) store.emit("popover:close");
    if (restoreFocus && prevFocus && prevFocus.focus && document.contains(prevFocus)) prevFocus.focus({ preventScroll: true });
  }
  function showEditor(kind) {
    inspector.dataset.editing = kind;
    $("#app").dataset.inspector = "open";
    inspectorToggle.setAttribute("aria-expanded", "true");
    popLayer.scrollTop = 0;
  }
  function cancelPopover() {
    store.set({ selection: [], selectionFile: null });
    store.emit("popover:close");
  }

  function handlePopoverKeydown(e, { cancel, confirm, enterTargets }) {
    if (e.key === "Escape" && !composing(e)) {
      e.preventDefault(); e.stopPropagation(); cancel(); return;
    }
    if (e.key === "Enter" && !e.shiftKey && !composing(e) && enterTargets.includes(e.target)) {
      e.preventDefault(); confirm();
    }
  }

  function popFoot(onCancel, onAdd) {
    return h("div", { class: "pop-foot" },
      h("button", { type: "button", class: "btn sm subtle", onclick: onCancel }, "取り消し", kbd("Esc")),
      h("button", { type: "button", class: "btn sm primary", onclick: onAdd }, "追加", kbd("Enter")));
  }

  function openFacesPopover(p) {
    closePalette();
    const prevFocus = document.activeElement;
    let action = lsGet("studio.lastAction", "thicken");
    if (!ACTIONS[action]) action = "thicken";
    let amount = DEFAULT_AMOUNT[action] ?? null;
    let amountEdited = false;
    let side = "both";

    const chips = h("div", { class: "chips", role: "radiogroup", "aria-label": "動作" });
    const chipBtns = Object.entries(ACTIONS).map(([id, a]) => {
      const b = h("button", { type: "button", class: "chip", role: "radio", onclick: () => { setAction(id); } }, a.label);
      chips.append(b);
      return [id, b];
    });
    const amountErrorId = "face-amount-error";
    const amountInput = h("input", { type: "number", class: "field num", min: "0.1", step: "0.1", "aria-label": "量（mm）", "aria-describedby": amountErrorId });
    const amountLabel = h("span", { class: "set-label" }, "量");
    const amountError = h("p", { class: "field-error", id: amountErrorId, role: "alert", hidden: true }, "0 より大きい数値を入力してください。");
    const setAmountInvalid = (invalid) => {
      amountInput.setAttribute("aria-invalid", String(invalid));
      amountError.hidden = !invalid;
    };
    const stepBy = (d) => {
      const cur = parseFloat(amountInput.value);
      const base = Number.isNaN(cur) ? (amount ?? 1) : cur;
      amount = Math.max(0.1, Math.round((base + d) * 100) / 100);
      amountEdited = true;
      amountInput.value = amount;
      setAmountInvalid(false);
    };
    const minus = h("button", { type: "button", class: "icon-btn sm", onclick: () => stepBy(-0.5) }, icon("minus"));
    const plus = h("button", { type: "button", class: "icon-btn sm", onclick: () => stepBy(0.5) }, icon("plus"));
    tip(minus, "0.5 減らす");
    tip(plus, "0.5 増やす");
    amountInput.addEventListener("input", () => {
      amountEdited = true;
      const v = amountInput.value.trim() === "" ? NaN : Number(amountInput.value);
      if (Number.isFinite(v) && v > 0) { amount = v; setAmountInvalid(false); }
    });
    const amountRow = h("div", { class: "pop-row" }, amountLabel, h("div", { class: "stepper" }, minus, amountInput, h("span", { class: "unit" }, "mm"), plus), amountError);

    const sideSeg = segmented(SIDES, () => side, (v) => { side = v; sideSeg.sync(); }, "どちら側");
    const sideRow = h("div", { class: "pop-row" }, h("span", { class: "set-label" }, "どちら側"), sideSeg.el);
    const note = h("textarea", { class: "field", rows: "2", placeholder: "メモ（任意）", "aria-label": "メモ" });

    function setAction(id) {
      action = id;
      const a = ACTIONS[id];
      if (a.amount && !amountEdited) amount = DEFAULT_AMOUNT[id] ?? 1;
      sync();
    }
    function sync() {
      for (const [id, b] of chipBtns) b.setAttribute("aria-checked", String(id === action));
      const a = ACTIONS[action];
      amountRow.hidden = !a.amount;
      amountLabel.textContent = AMOUNT_LABEL[action] || "量";
      if (a.amount && document.activeElement !== amountInput) amountInput.value = amount ?? "";
      sideRow.hidden = !(action === "thicken" || action === "thin");
    }
    const confirm = () => {
      const a = ACTIONS[action];
      let amt = null;
      if (a.amount) {
        const v = amountInput.value.trim() === "" ? NaN : Number(amountInput.value);
        if (!Number.isFinite(v) || v <= 0) {
          setAmountInvalid(true);
          amountInput.focus({ preventScroll: true });
          return;
        }
        amt = v;
      }
      const item = { type: "faces", file: p.file, faceIds: p.faceIds, summary: p.summary, action, amount: amt, note: note.value.trim() };
      if (action === "thicken" || action === "thin") item.side = side;
      lsSet("studio.lastAction", action);
      const id = store.addItem(item);
      store.set({ selection: [], activeItemId: id });
      closePopover();
      setTab("notes");
      markActive(true);
    };

    const count = h("span", {});
    const area = h("span", { class: "muted mono" });
    const thickness = h("div", { class: "pop-sub" });
    const updateSelection = (next) => {
      p = next;
      const sum = p.summary || {};
      const n = sum.faceCount ?? p.faceIds?.length ?? 0;
      count.textContent = `面 ${n.toLocaleString("ja-JP")} 枚`;
      area.textContent = sum.area == null ? "" : `${Math.round(sum.area).toLocaleString("ja-JP")} mm²`;
      thickness.hidden = !sum.thickness;
      thickness.textContent = sum.thickness ? `今の肉厚 ${num1(sum.thickness.min)}〜${num1(sum.thickness.median)} mm` : "";
    };
    const el = h("div", { class: "popover", role: "region", "aria-label": "選んだ面への指示" },
      h("h2", { class: "editor-title" }, "選んだ面への指示"),
      h("div", { class: "pop-head" },
        h("span", { class: "dot", style: `--c:${SELECTION_COLOR}` }),
        count, area),
      thickness,
      chips, amountRow, sideRow, note,
      popFoot(cancelPopover, confirm));
    el.addEventListener("keydown", (e) => handlePopoverKeydown(e, { cancel: cancelPopover, confirm, enterTargets: [note, amountInput] }));
    popLayer.append(el);
    updateSelection(p);
    sync();
    pop = { el, kind: "faces", file: p.file, prevFocus, updateSelection };
    showEditor("faces");
    note.focus({ preventScroll: true });
  }

  function openPinPopover(p) {
    closePalette();
    const prevFocus = document.activeElement;
    const no = store.state.draft.items.filter((it) => it.type === "pin").length + 1;
    const note = h("textarea", { class: "field", rows: "3", placeholder: "この点について（例: ここの角を丸く）", "aria-label": "ピンのメモ" });
    const confirm = () => {
      const id = store.addItem({ type: "pin", file: p.file, point: p.point, normal: p.normal, note: note.value.trim() });
      store.set({ activeItemId: id });
      closePopover();
      setTab("notes");
      markActive(true);
    };
    const el = h("div", { class: "popover", role: "region", "aria-label": "ピンのメモ" },
      h("div", { class: "pop-head" }, icon("pin", "sm"), h("b", {}, `ピン ${no}`)),
      note,
      popFoot(cancelPopover, confirm));
    el.addEventListener("keydown", (e) => handlePopoverKeydown(e, { cancel: cancelPopover, confirm, enterTargets: [note] }));
    popLayer.append(el);
    pop = { el, kind: "pin", prevFocus };
    showEditor("pin");
    note.focus({ preventScroll: true });
  }

  store.on("popover", (p) => {
    if (p?.kind === "faces" && pop?.kind === "faces" && pop.file === p.file) {
      pop.updateSelection(p);
      return;
    }
    // ピンは picking が次の仮置きを描いた後にここへ届く。
    // 編集欄の置き換えで、その新しい仮置きを消さない。
    closePopover({ restoreFocus: false, notify: false });
    if (!p) return;
    if (p.kind === "faces") openFacesPopover(p);
    else if (p.kind === "pin") openPinPopover(p);
  });
  store.on("popover:close", () => closePopover({ notify: false }));

  function noteOpened(name) {
    recent = [name, ...recent.filter((n) => n !== name)].slice(0, 12);
    lsSet("studio.recent", recent);
  }

  // ===========================================================================
  // トースト・状態
  // ===========================================================================
  const toasts = $("#toasts");
  store.on("toast", ({ text, action, kind }) => {
    const el = h("div", { class: `toast ${kind || ""}`.trim() });
    const close = () => { el.classList.add("out"); setTimeout(() => el.remove(), 180); };
    add(el, [h("span", { class: "toast-text" }, text)]);
    if (action) {
      el.append(h("button", { type: "button", class: "btn sm primary", onclick: () => { try { action.run(); } finally { close(); } } }, action.label));
    }
    el.append(h("button", { type: "button", class: "icon-btn xs", "aria-label": "閉じる", onclick: close }, icon("close")));
    toasts.append(el);
    while (toasts.children.length > 4) toasts.firstChild.remove();
    setTimeout(close, action ? 12000 : 5000);
  });

  let statusTimer = null;
  store.on("status", ({ text, kind }) => {
    clearTimeout(statusTimer);
    statusText.textContent = text || "";
    statusText.title = text || "";
    statusEl.dataset.kind = kind || "";
    if (kind === "ok") statusTimer = setTimeout(() => { statusEl.dataset.kind = ""; }, 4000);
  });

  // ===========================================================================
  // 購読
  // ===========================================================================
  store.on("items", onItems);
  store.on("change:activeItemId", () => markActive(true));
  store.on("change:tool", () => { syncRail(); renderHint(); });
  store.on("change:frame", () => { syncRail(); renderHint(); });
  store.on("change:faceMode", renderHint);
  store.on("change:faceAngle", renderHint);
  store.on("change:brushRadius", renderHint);
  store.on("change:sectionAxis", renderHint);
  store.on("change:selection", renderHint);
  store.on("change:compare", syncCompare);
  store.on("change:showFaceOutlines", syncTopbar);
  store.on("change:model", () => { syncTopbar(); closePopover(); });
  store.on("change:files", () => { syncWarn(); refreshRequestButtons(); });
  store.on("mesh:loaded", () => { syncWarn(); refreshRequestButtons(); });
  store.on("viewport:pointer", ({ point }) => {
    coordEl.textContent = point ? `X ${num1(point[0])}  Y ${num1(point[1])}  Z ${num1(point[2])} mm` : "";
  });

  // 初期描画
  setTab("notes");
  syncRail();
  renderHint();
  renderItems();
  renderRequests(true);
  syncCompare();
  syncListener();
  syncModeNote();
  syncTopbar();
  buildParams();

  // ===========================================================================
  // app.js から使う口
  // ===========================================================================
  return {
    setModels(list) { models = list || []; syncTopbar(); },
    noteOpened,
    openPalette, closePalette,
    isPaletteOpen: () => catalog.isOpen(),
    showTab: setTab,

    setParams({ controls, preview }) {
      controlsDef = controls || [];
      values = {};
      defaults = {};
      const saved = savedParams();
      for (const c of controlsDef) {
        const key = keyOf(c);
        defaults[key] = c.value;
        const restored = c.index === undefined ? saved?.[c.name] : saved?.[c.name]?.[c.index];
        values[key] = Number.isFinite(restored) ? restored : c.value;
      }
      hasPreview = !!preview;
      buildParams();
      syncModeNote();
    },
    getParams: collectParams,
    setExporting(b) { exporting = !!b; syncModeNote(); },
    setSending(b) { sending = !!b; if (sending) closePalette(); syncTopbar(); },

    setMode(m) {
      if (m.mode !== undefined) mode = m.mode;
      if (m.hasStl !== undefined) hasStl = m.hasStl;
      if (m.hasPreview !== undefined) hasPreview = m.hasPreview;
      hintKey = ""; // 文言とボタンを作り直す
      renderHint();
      syncModeNote();
      syncRail();
    },
    setParts(p) {
      parts = { candidates: p.candidates || [], shown: p.shown || [], custom: !!p.custom };
      syncTopbar();
      if (menuEl) renderPartsMenu();
    },
    setRequests(list) {
      requests = list || [];
      renderRequests(false);
    },
    setListener(info) { listener = info || { listening: false }; syncListener(); },
    setConnection(up) {
      wsUp = !!up;
      if (!wsUp) store.status("サーバーとつながっていません。つなぎ直しています…", "err");
    },
    syncAll() { renderItems(); syncTopbar(); syncCompare(); },
    isConnected: () => wsUp,
    messageBox,
  };
}
