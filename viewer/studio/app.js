// Studio の起動と配線。モデルを開く・STL を選ぶ・依頼を送る・キー入力を一括で受ける。
// 画面の部品は panels.js、3D は viewport / picking / section、2D は sketch、通信は api.js。

import { store, TOOLS } from "./store.js";
import { api, connectWS, requestStatus, requestBefore } from "./api.js";
import { createViewport } from "./viewport.js";
import { createPicking } from "./picking.js";
import { createSections } from "./section.js";
import { createSketch } from "./sketch.js";
import { createPanels } from "./panels.js";
import { buildRequest } from "./bundle.js";
import { filesForModel, selectModelFile } from "./model-files.js";

const $ = (sel) => document.querySelector(sel);
const VIEW_ORDER = ["front", "back", "left", "right", "top", "bottom", "iso"];
const PLACED_RE = /print|plate|split/i;

function lsGet(key, fallback) {
  try { const v = localStorage.getItem(key); return v === null ? fallback : JSON.parse(v); } catch { return fallback; }
}
function lsSet(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch { /* 無くても動く */ } }
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

// --- 3D / 2D の部品 ------------------------------------------------------------

const stageEl = $("#stage");
const sketchEl = $("#sketch");
const splitterEl = $("#splitter");
const viewportEl = $("#viewport");

const viewport = createViewport(viewportEl, store);
const picking = createPicking(viewport, store);
const sections = createSections(viewport, store);
const sketch = createSketch(sketchEl, store, { modelBox: () => viewport.modelBox() });
// 動作確認用（ブラウザのコンソールや自動操作から状態を読む）
window.__studio = { store, viewport, picking, sections, sketch };

// --- 状態（app だけが持つもの）--------------------------------------------------

let models = [];
let stlList = [];            // [{name, mtime, size}] 新しい順
let stlNames = [];
let modelName = null;
let mode = "none";           // "stl" | "preview" | "none"
let previewBuild = null;
let shownFiles = [];
let partsCustom = false;
let loadedMtimes = new Map();
let requests = [];
const prevStatus = new Map();
let listenerInfo = null;
let sending = false;
let opening = false;
let booted = false;
let openSeq = 0;
let loadSeq = 0;
let fitSketchFor = null;

const mtimeOf = (name) => (stlList.find((f) => f.name === name) || {}).mtime ?? 0;

// --- STL の選び方（旧 viewer/index.html の loadLatestStlFor と同じ規則）---------

// モデル名と STL 名は「-」と「_」が混在している（pipe-foot-pair → pipe_foot_pair.stl）。揃えてから比べる
const norm = (s) => s.toLowerCase().replace(/-/g, "_");

function headsFor(name, files) {
  return filesForModel(name, files, models.map((m) => m.name));
}

// files は新しい順
function pickStl(name, files) {
  return selectModelFile(name, files, models.map((m) => m.name));
}

// 自動で選ぶ表示対象。preview があり、このモデルの STL が無いときは STL を出さない
function autoNames() {
  if (!modelName) return [];
  const pick = pickStl(modelName, stlNames);
  if (!pick) return [];
  const matched = headsFor(modelName, stlNames).length > 0;
  if (!matched && previewBuild) return [];
  return [pick];
}

async function refreshStls() {
  try {
    stlList = await api.stls();
    stlNames = stlList.map((f) => f.name);
  } catch (e) {
    console.error(e);
    store.status(`STL の一覧を読めませんでした: ${e.message}`, "err");
  }
}

// --- 画面とのやり取り（panels に渡す）------------------------------------------

function syncPanels() {
  const heads = modelName ? headsFor(modelName, stlNames) : [];
  const auto = autoNames();
  const candidates = [...new Set([...heads, ...auto, ...shownFiles])];
  panels.setParts({ candidates, shown: shownFiles, custom: partsCustom });
  panels.setMode({ mode, hasStl: heads.length > 0 || auto.length > 0, hasPreview: !!previewBuild });
}

function placedFiles() {
  return viewport.getMeshes()
    .filter((m) => (m.userData.placed ?? PLACED_RE.test(m.userData.file || "")))
    .map((m) => m.userData.file);
}

function modeStlAction() {
  const auto = autoNames();
  return auto.length ? { label: "STL を表示", run: () => showStl() } : null;
}

function setTool(t) {
  if (sending) return;
  if (!TOOLS.includes(t)) return;
  if (store.state.frame === "preview-m-yup" && t !== "view") {
    store.toast("プレビュー表示中は指示を付けられません。STL を表示してください", { action: modeStlAction() || undefined });
    return;
  }
  store.set({ tool: t });
}

const ctx = {
  setTool,
  viewPreset: (name) => viewport.viewPreset(name),
  openModel: (name) => openModel(name),
  setParts,
  showStl: () => showStl(),
  showPreview: () => showPreview({ fit: false }),
  paramsChanged,
  exportStl,
  send: sendRequest,
  compare: compareWith,
  clearCompare,
  replyRequest,
  closeRequest: (id) => setRequestStatus(id, "closed"),
  reopenRequest: (id) => setRequestStatus(id, "open"),
  placedFiles,
};
const panels = createPanels({ store, ctx });

// --- STL / プレビューの表示 ------------------------------------------------------

async function showStl(names, { fit = false } = {}) {
  const list = names && names.length ? names : (partsCustom && shownFiles.length ? shownFiles : autoNames());
  if (!list.length) {
    store.status("表示できる STL がありません。パラメータの「STL 生成」で作れます", "err");
    return;
  }
  const seq = ++loadSeq;
  const t0 = performance.now();
  const label = list.length > 1 ? `${list.length} 個の STL` : list[0];
  store.status(`${label} を読み込み中…`, "busy");
  try {
    const items = list.map((n) => ({ name: n, url: `/exports/${encodeURIComponent(n)}?v=${mtimeOf(n)}` }));
    await viewport.loadSTLs(items, { fit });
    if (seq !== loadSeq) return;
    shownFiles = list.slice();
    loadedMtimes = new Map(list.map((n) => [n, mtimeOf(n)]));
    mode = "stl";
    store.set({ frame: "blender-mm", files: list.map((n) => ({ name: n, mtime: mtimeOf(n) })) });
    syncPanels();
    store.status(`${label} · ${((performance.now() - t0) / 1000).toFixed(1)} 秒`, "ok");
  } catch (e) {
    if (seq !== loadSeq) return;
    console.error(e);
    store.status(`STL を読み込めませんでした: ${e.message}`, "err");
  }
}

function showPreview({ fit = false } = {}) {
  if (!previewBuild) return;
  try {
    const group = previewBuild(panels.getParams(), viewport.THREE);
    viewport.setPreviewGroup(group, { fit });
    const wasPreview = mode === "preview";
    mode = "preview";
    shownFiles = [];
    loadedMtimes = new Map();
    if (!wasPreview) {
      store.emit("popover:close");
      clearCompare();
      store.set({ selection: [], tool: "view" });
    }
    store.set({ frame: "preview-m-yup", files: [] });
    syncPanels();
    store.status("プレビューを更新しました", "ok");
  } catch (e) {
    console.error(e);
    store.status(`プレビューを作れませんでした: ${e.message}`, "err");
  }
}

async function setParts(names) {
  if (!modelName) return;
  if (!names) {
    partsCustom = false;
    const auto = autoNames();
    if (!auto.length) return;
    await showStl(auto, { fit: false });
  } else {
    partsCustom = true;
    await showStl(names, { fit: false });
  }
}

// --- パラメータ・STL 生成 --------------------------------------------------------

let rebuildTimer = null;
function paramsChanged() {
  if (!previewBuild) return;
  if (mode !== "preview") {
    showPreview({ fit: false });
    store.toast("プレビューに切り替えました。指示を付けるときは STL を表示してください", { action: modeStlAction() || undefined });
    return;
  }
  clearTimeout(rebuildTimer);
  rebuildTimer = setTimeout(() => showPreview({ fit: false }), 30);
}

async function exportStl() {
  if (!modelName) return;
  const name = modelName;
  panels.setExporting(true);
  store.status("STL を作っています（Blender）…", "busy");
  try {
    const r = await api.exportModel(name, panels.getParams());
    if (r && r.ok) {
      store.status("STL を作りました", "ok");
      if (mode !== "stl" && name === modelName) {
        const act = modeStlAction();
        store.toast("STL を作りました", act ? { action: act } : {});
      }
    } else {
      const why = (r && (r.error || (r.code !== undefined ? `終了コード ${r.code}` : ""))) || "原因不明";
      console.error("[export]", r);
      store.status(`STL を作れませんでした（${why}）`, "err");
    }
  } catch (e) {
    console.error(e);
    store.status(`STL を作れませんでした: ${e.message}`, "err");
  } finally {
    panels.setExporting(false);
  }
}

// --- モデルを開く ------------------------------------------------------------------

async function openModel(name, { fromHistory = false } = {}) {
  if (sending) return false;
  const info = models.find((m) => m.name === name);
  if (!info) { store.status(`モデル「${name}」が見つかりません`, "err"); return false; }
  if (info.available === false) { store.toast(info.unavailableReason || "このモデルは別の形式で作成されています"); return false; }
  const seq = ++openSeq;
  opening = true;
  try {
    clearTimeout(rebuildTimer);
    store.emit("popover:close");
    if (store.state.compare) { store.set({ compare: null }); }
    try { await viewport.setGhost(null); } catch (e) { console.error(e); }
    partsCustom = false;
    shownFiles = [];
    loadedMtimes = new Map();
    requests = [];
    prevStatus.clear();
    panels.setRequests([]);
    modelName = name;
    store.set({ model: name, files: [], selection: [], activeItemId: null, activeSectionId: null });
    store.loadDraft();
    if (!fromHistory) {
      const url = `${location.pathname}?model=${encodeURIComponent(name)}`;
      if (booted) history.pushState(null, "", url);
      else history.replaceState(null, "", url);
    }
    document.title = `${info.title || name} · model-lab`;
    store.status(`${name} を読み込み中…`, "busy");
    loadRequests(); // 3D の読み込みを待たずに依頼の一覧を出す

    let data;
    try { data = await api.params(name); } catch (e) {
      console.error(e);
      store.status(`${name} の設定を読めませんでした: ${e.message}`, "err");
      return false;
    }
    if (seq !== openSeq) return false;
    viewport.applyViewerConfig(data.viewer || null);
    panels.setParams(data);

    previewBuild = null;
    if (data.preview) {
      try {
        const mod = await import(`/preview/${name}.js`);
        previewBuild = mod.build;
      } catch (e) {
        console.error(e);
        store.toast("プレビューを読み込めませんでした。STL を生成すると表示できます");
      }
    }
    if (seq !== openSeq) return false;

    await refreshStls();
    if (seq !== openSeq) return false;

    const names = autoNames();
    if (names.length) {
      const matched = headsFor(name, stlNames).length > 0;
      if (!matched) store.toast(`${name} の STL が見つからないので、いちばん新しい STL（${names[0]}）を表示しています`);
      await showStl(names, { fit: true });
    } else if (previewBuild) {
      showPreview({ fit: true });
    } else {
      mode = "none";
      try { await viewport.loadSTLs([], { fit: false }); } catch (e) { console.error(e); }
      store.set({ frame: "blender-mm" });
      syncPanels();
      store.status("STL がまだありません。パラメータの「STL 生成」で作れます", "");
    }
    if (seq !== openSeq) return false;
    panels.noteOpened(name);
    return true;
  } finally {
    if (seq === openSeq) opening = false;
  }
}

// --- STL の更新通知 ------------------------------------------------------------------

let updTimer = null;
function scheduleStlUpdate() {
  clearTimeout(updTimer);
  updTimer = setTimeout(handleStlUpdate, 400); // 書き込み中の通知が続くので、静まってから読む
}

async function handleStlUpdate() {
  if (!modelName || opening) return;
  await refreshStls();
  if (mode === "stl") {
    const names = partsCustom ? shownFiles.filter((n) => stlNames.includes(n)) : autoNames();
    if (!names.length) return syncPanels();
    const changed = names.length !== shownFiles.length
      || names.some((n, i) => n !== shownFiles[i])
      || names.some((n) => mtimeOf(n) !== loadedMtimes.get(n));
    if (changed) await showStl(names, { fit: false });
    else syncPanels();
  } else if (mode === "none") {
    const names = autoNames();
    if (names.length) await showStl(names, { fit: true });
    else syncPanels();
  } else {
    syncPanels();
  }
}

// --- 依頼 ----------------------------------------------------------------------------

function fmtTime(iso) {
  const d = new Date(iso);
  if (!iso || Number.isNaN(d.getTime())) return "";
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getMonth() + 1}/${d.getDate()} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

async function loadRequests() {
  const name = modelName;
  if (!name) return;
  try {
    const list = await api.requests(name);
    if (name !== modelName) return;
    handleRequests(list);
  } catch (e) {
    console.error(e);
    store.status(`依頼の一覧を読めませんでした: ${e.message}`, "err");
  }
}

function handleRequests(list) {
  requests = [...list].sort((a, b) => (a.id < b.id ? 1 : a.id > b.id ? -1 : 0));
  for (const r of requests) {
    const st = requestStatus(r);
    const old = prevStatus.get(r.id);
    if (old !== undefined && old !== st) {
      if (st === "done") {
        store.toast("シュビーが直しました", { action: { label: "変更前と重ねる", run: () => compareWith(r) } });
      } else if (st === "question") {
        store.toast("シュビーから質問があります");
        panels.showTab("notes");
      }
    }
    prevStatus.set(r.id, st);
  }
  panels.setRequests(requests);
}

async function compareWith(r) {
  const shown = (store.state.files || []).map((f) => f.name);
  const b = requestBefore(r, shown);
  if (!b) { store.toast("この依頼には変更前の STL がありません"); return; }
  try {
    store.status("変更前を読み込み中…", "busy");
    await viewport.setGhost(b.url);
    store.set({ compare: { id: r.id, label: `${fmtTime(r.createdAt)} の依頼の変更前`, url: b.url, file: b.file } });
    store.status("変更前を重ねて表示しています", "ok");
  } catch (e) {
    console.error(e);
    store.status(`変更前を読み込めませんでした: ${e.message}`, "err");
  }
}

async function clearCompare() {
  if (!store.state.compare) return;
  store.set({ compare: null });
  try { await viewport.setGhost(null); } catch (e) { console.error(e); }
}

async function replyRequest(id, text) {
  try {
    await api.sendMessage(id, text);
    store.status("追記しました", "ok");
    await loadRequests();
  } catch (e) {
    console.error(e);
    store.status(`追記できませんでした: ${e.message}`, "err");
  }
}

async function setRequestStatus(id, status) {
  try {
    await api.setRequestStatus(id, status);
    if (status === "closed" && store.state.compare && store.state.compare.id === id) await clearCompare();
    await loadRequests();
  } catch (e) {
    console.error(e);
    store.status(`状態を変えられませんでした: ${e.message}`, "err");
  }
}

async function sendRequest() {
  if (sending || !store.state.model) return;
  const model = store.state.model;
  const sentDraft = JSON.stringify(store.state.draft);
  sending = true;
  panels.setSending(true);
  try {
    store.status("送る内容をまとめています…", "busy");
    const bundle = await buildRequest({ store, viewport, sections, sketch });
    if (!bundle) {
      store.status("", "");
      store.toast("指示かメッセージを入れてから送ってください");
      return;
    }
    store.status("送っています…", "busy");
    await api.createRequest({ model, request: bundle.request, images: bundle.images });
    // Keep any input made while image capture / network submission was running.
    if (store.state.model === model && JSON.stringify(store.state.draft) === sentDraft) store.clearDraft();
    panels.syncAll();
    panels.showTab("notes");
    store.status("送りました", "ok");
    store.toast(listenerInfo && listenerInfo.listening
      ? "送りました。シュビーが見ると対応が始まります"
      : "送りました。シュビーが待ち受けていないので、チャットで「スタジオの依頼を見て」と伝えてください");
    await loadRequests();
  } catch (e) {
    console.error(e);
    store.status(`送れませんでした: ${e.message}`, "err");
    store.toast(`送れませんでした: ${e.message}`, { kind: "err" });
  } finally {
    sending = false;
    panels.setSending(false);
  }
}

// --- 在席表示 ------------------------------------------------------------------------

async function pollListener() {
  try {
    listenerInfo = await api.listener();
  } catch {
    listenerInfo = { listening: false };
  }
  panels.setListener(listenerInfo);
}

// --- 2D の表示と、3D との境目 -----------------------------------------------------------

let sketchFrac = clamp(Number(lsGet("studio.sketchFrac", 0.45)) || 0.45, 0.25, 0.75);

function applySketchWidth() {
  stageEl.style.setProperty("--sketch-w", `${(sketchFrac * 100).toFixed(1)}%`);
}

function layoutChanged() {
  requestAnimationFrame(() => {
    if (typeof viewport.resize === "function") viewport.resize();
    else window.dispatchEvent(new Event("resize"));
    if (!sketchEl.hidden) sketch.resize();
  });
}

function syncSketch() {
  const id = store.state.activeSectionId;
  const show = !!id && !!store.getItem(id);
  const wasHidden = sketchEl.hidden;
  sketchEl.hidden = !show;
  splitterEl.hidden = !show;
  if (show) {
    applySketchWidth();
    fitSketchFor = id;
    // 輪郭が先に届いていて section:loops を待っても来ない場合の保険
    setTimeout(() => {
      if (fitSketchFor === id && store.state.activeSectionId === id) {
        fitSketchFor = null;
        sketch.resize();
        sketch.fit();
      }
    }, 250);
  } else {
    fitSketchFor = null;
  }
  if (show || !wasHidden) layoutChanged();
}

store.on("change:activeSectionId", syncSketch);
store.on("section:loops", ({ id }) => {
  if (id && id === fitSketchFor) {
    fitSketchFor = null;
    requestAnimationFrame(() => { sketch.resize(); sketch.fit(); });
  }
});

splitterEl.addEventListener("pointerdown", (e) => {
  e.preventDefault();
  splitterEl.setPointerCapture(e.pointerId);
  splitterEl.classList.add("drag");
  const rect = stageEl.getBoundingClientRect();
  const move = (ev) => {
    sketchFrac = clamp((rect.right - ev.clientX) / rect.width, 0.25, 0.75);
    applySketchWidth();
    layoutChanged();
  };
  const up = () => {
    splitterEl.classList.remove("drag");
    splitterEl.removeEventListener("pointermove", move);
    splitterEl.removeEventListener("pointerup", up);
    splitterEl.removeEventListener("pointercancel", up);
    lsSet("studio.sketchFrac", sketchFrac);
  };
  splitterEl.addEventListener("pointermove", move);
  splitterEl.addEventListener("pointerup", up);
  splitterEl.addEventListener("pointercancel", up);
});
splitterEl.addEventListener("keydown", (e) => {
  if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
  e.preventDefault();
  sketchFrac = clamp(sketchFrac + (e.key === "ArrowLeft" ? 0.02 : -0.02), 0.25, 0.75);
  applySketchWidth();
  lsSet("studio.sketchFrac", sketchFrac);
  layoutChanged();
});
splitterEl.addEventListener("dblclick", () => {
  sketchFrac = 0.45;
  applySketchWidth();
  lsSet("studio.sketchFrac", sketchFrac);
  layoutChanged();
});

window.addEventListener("resize", layoutChanged);
if (typeof ResizeObserver === "function") {
  new ResizeObserver(layoutChanged).observe(viewportEl);
}

// --- 道具を替えたら、確定前の選択とポップオーバーは捨てる ------------------------------------

store.on("change:tool", () => {
  store.emit("popover:close");
  if (store.state.selection.length) store.set({ selection: [] });
});

// --- キー入力（一括）----------------------------------------------------------------------

function isTextTarget(t) {
  return !!(t && t.closest && t.closest(
    "input:not([type=range]):not([type=checkbox]):not([type=radio]), textarea, select, [contenteditable=''], [contenteditable='true']"));
}

let bHold = null;

window.addEventListener("keydown", (e) => {
  const mod = e.ctrlKey || e.metaKey;
  const k = e.key;
  const lk = k.length === 1 ? k.toLowerCase() : k;

  if (e.defaultPrevented || e.isComposing || e.keyCode === 229) return;

  if (mod && !e.altKey && lk === "k") { e.preventDefault(); panels.openPalette(); return; }
  if (panels.isPaletteOpen()) return; // パレットの中は自分でキーを受ける
  if (mod && !e.altKey && k === "Enter") {
    // Follow-up fields own their submission. Only the overall draft uses this shortcut.
    if (isTextTarget(e.target) && e.target !== panels.messageBox) return;
    e.preventDefault(); sendRequest(); return;
  }
  if (e.isComposing || isTextTarget(e.target)) return;

  if (!sketchEl.hidden && sketch.isFocused() && sketch.handleKey(e)) { e.preventDefault(); return; }

  if (mod && !e.altKey) {
    if (lk === "z") { e.preventDefault(); if (e.shiftKey) store.redo(); else store.undo(); }
    else if (lk === "y") { e.preventDefault(); store.redo(); }
    return;
  }
  if (e.altKey) return;

  switch (lk) {
    case "v": setTool("view"); break;
    case "f": setTool("faces"); break;
    case "p": setTool("pin"); break;
    case "m": setTool("measure"); break;
    case "s": setTool("section"); break;
    case "b":
      if (e.repeat || store.state.tool !== "faces") break;
      // 押して離すと切り替え、押し続けている間だけならブラシ（離すと元に戻る）
      bHold = { prev: store.state.faceMode, at: performance.now() };
      store.set({ faceMode: bHold.prev === "brush" ? "smart" : "brush" });
      break;
    case "[":
    case "]": {
      if (store.state.tool !== "faces") break;
      const r = store.state.brushRadius;
      const step = r < 10 ? 1 : 5;
      store.set({ brushRadius: clamp(r + (lk === "]" ? step : -step), 1, 100) });
      break;
    }
    case "Escape":
      store.set({ selection: [] });
      store.emit("popover:close");
      break;
    case "Delete": {
      const id = store.state.activeItemId;
      if (id) store.removeItem(id);
      break;
    }
    default:
      if (/^[1-7]$/.test(lk)) viewport.viewPreset(VIEW_ORDER[Number(lk) - 1]);
      else return;
  }
  e.preventDefault();
});

window.addEventListener("keyup", (e) => {
  if ((e.key === "b" || e.key === "B") && bHold) {
    if (performance.now() - bHold.at > 350) store.set({ faceMode: bHold.prev });
    bHold = null;
  }
});

// --- 起動 -------------------------------------------------------------------------------------

window.addEventListener("error", (e) => {
  console.error(e.error || e.message);
  store.status(`エラー: ${e.message}`, "err");
});
window.addEventListener("unhandledrejection", (e) => {
  console.error(e.reason);
  store.status(`エラー: ${(e.reason && e.reason.message) || e.reason}`, "err");
});

async function boot() {
  store.status("準備中…", "busy");
  let cfg = null;
  try { cfg = await api.config(); } catch (e) { console.error(e); }
  const wsPort = (cfg && cfg.ws) || (Number(location.port) + 1);
  const ws = connectWS(`ws://127.0.0.1:${wsPort}`);

  let wasUp = false;
  ws.onState((up) => {
    panels.setConnection(up);
    if (up && wasUp === false && booted) {
      store.status("サーバーにつながりました", "ok");
      scheduleStlUpdate();
      loadRequests();
      pollListener();
    }
    if (up) wasUp = true;
    else wasUp = false;
  });
  ws.on("update", scheduleStlUpdate);
  ws.on("requests", (m) => { if (!m.model || m.model === modelName) loadRequests(); });
  ws.on("listener", (m) => {
    listenerInfo = { listening: !!m.listening, agent: m.agent ?? null, at: m.at ?? null };
    panels.setListener(listenerInfo);
  });

  try {
    models = await api.models();
  } catch (e) {
    console.error(e);
    store.status(`モデルの一覧を読めませんでした: ${e.message}`, "err");
    return;
  }
  panels.setModels(models);

  const want = new URLSearchParams(location.search).get("model");
  const recent = lsGet("studio.recent", []);
  const byName = (n) => models.find((m) => m.name === n && m.available !== false);
  const start = byName(want) || byName(Array.isArray(recent) && recent[0]) || byName("round-bot") || models.find((m) => m.available !== false);
  if (want && !byName(want) && start) store.toast(`モデル「${want}」が見つからないので ${start.name} を開きます`);
  if (start) await openModel(start.name);
  booted = true;

  await pollListener();
  setInterval(pollListener, 10000);
}

boot();

window.addEventListener("popstate", () => {
  const name = new URLSearchParams(location.search).get("model");
  if (name && name !== modelName) openModel(name, { fromHistory: true });
});
