// 3D 上から部品の見え方（通常 / 透過 / 隠す）を切り替える。
//   右クリック（動かさずに離す）: カーソルの下にある部品を手前から並べたメニュー。透過した部品も出る
//   T: カーソルの下の最も手前の部品を 透過 ⇄ 通常。Shift+T: すべて戻す
//   3D の左下: 透過・隠している部品の数と「すべて戻す」
// 右ドラッグ（視点の移動）は今までどおり。状態は store.state.partModes、反映は viewport.js。

import { PART_MODES, PART_MODE_LABELS, countPartModes, modeOf, toggledGhost } from "./part-modes.js";

const CLICK_PX = 4;

function el(tag, props = {}, ...kids) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const kid of kids) if (kid != null) node.append(kid);
  return node;
}

export function createPartMenu(viewport, store, { chipHost } = {}) {
  const { canvas } = viewport;

  // ---- 左下の印（透過・隠している部品があるときだけ）-------------------------------
  const chipText = el("span", {}, "");
  const chip = el("div", { class: "compare-chip part-chip", hidden: "" },
    chipText,
    el("button", { type: "button", class: "link", onclick: () => store.resetPartModes() }, "すべて戻す"));
  if (chipHost) chipHost.append(chip);

  function loadedFiles() { return viewport.getMeshes().map((m) => m.userData.file); }
  function syncChip() {
    const { ghost, hidden } = countPartModes(store.state.partModes, loadedFiles());
    chip.hidden = ghost + hidden === 0;
    const parts = [];
    if (ghost) parts.push(`透過 ${ghost}`);
    if (hidden) parts.push(`隠す ${hidden}`);
    chipText.textContent = `部品の見え方: ${parts.join(" · ")}`;
  }

  // ---- 右クリックのメニュー ------------------------------------------------------------
  let menu = null;
  let hits = [];
  function closeMenu() {
    if (!menu) return;
    menu.remove();
    menu = null;
  }

  function renderMenu(x, y) {
    const prev = menu;
    const scrollTop = prev ? prev.scrollTop : 0;
    if (prev) prev.remove();
    const m = el("div", { class: "menu part-ctx", role: "group", "aria-label": "この位置の部品" });
    m.append(el("div", { class: "menu-head" }, hits.length ? "この位置の部品（手前から）" : "この位置に部品はありません"));
    for (const hit of hits) {
      const mode = modeOf(store.state.partModes, hit.file);
      const seg = el("div", { class: "seg", role: "group", "aria-label": `${hit.file} の見え方` });
      for (const v of PART_MODES) {
        const b = el("button", {
          type: "button", class: "seg-btn", "aria-pressed": String(mode === v),
          onclick: () => { store.setPartMode(hit.file, v); renderMenu(x, y); },
        }, PART_MODE_LABELS[v]);
        seg.append(b);
      }
      m.append(el("div", { class: "part-row" }, el("span", { class: "menu-name mono", title: hit.file }, hit.file), seg));
    }
    const { ghost, hidden } = countPartModes(store.state.partModes, loadedFiles());
    if (ghost + hidden > 0) {
      m.append(el("button", {
        type: "button", class: "menu-row reset",
        onclick: () => { store.resetPartModes(); closeMenu(); },
      }, "透過・隠した部品をすべて戻す"));
    }
    document.body.append(m);
    m.style.left = `${Math.max(8, Math.min(x, innerWidth - m.offsetWidth - 8))}px`;
    m.style.top = `${Math.max(8, Math.min(y, innerHeight - m.offsetHeight - 8))}px`;
    m.scrollTop = scrollTop;
    menu = m;
  }

  function openMenu(x, y) {
    hits = viewport.pickParts(x, y);
    if (!hits.length && !countPartModes(store.state.partModes, loadedFiles()).hidden) { closeMenu(); return; }
    renderMenu(x, y);
  }

  // ---- ポインタ -------------------------------------------------------------------------
  let down = null;
  const onDown = (e) => {
    closeMenu();
    if (e.button !== 2) { down = null; return; }
    down = { id: e.pointerId, x: e.clientX, y: e.clientY };
  };
  const onMoveTrack = (e) => {
    cursor = { x: e.clientX, y: e.clientY };
    if (down && down.id === e.pointerId && Math.hypot(e.clientX - down.x, e.clientY - down.y) >= CLICK_PX) down = null;
  };
  const onUp = (e) => {
    if (!down || down.id !== e.pointerId || e.button !== 2) return;
    const d = down;
    down = null;
    if (Math.hypot(e.clientX - d.x, e.clientY - d.y) >= CLICK_PX) return;
    if (store.state.frame === "preview-m-yup") return;
    openMenu(e.clientX, e.clientY);
  };
  let cursor = null;                 // キャンバス上の最後のポインタ位置（T キー用）
  const onLeave = () => { cursor = null; };
  canvas.addEventListener("pointerdown", onDown);
  canvas.addEventListener("pointermove", onMoveTrack);
  canvas.addEventListener("pointerup", onUp);
  canvas.addEventListener("pointercancel", () => { down = null; });
  canvas.addEventListener("pointerleave", onLeave);

  const onDocDown = (e) => { if (menu && !menu.contains(e.target) && e.target !== canvas) closeMenu(); };
  const onKey = (e) => { if (e.key === "Escape" && menu) { closeMenu(); e.stopPropagation(); } };
  document.addEventListener("pointerdown", onDocDown, true);
  document.addEventListener("keydown", onKey, true);

  // ---- キー（app.js が呼ぶ）-------------------------------------------------------------
  // カーソルの下の最も手前の部品を 透過 ⇄ 通常。戻り値は何かした（true）かどうか
  function toggleUnderCursor() {
    if (!cursor || store.state.frame === "preview-m-yup") return false;
    const first = viewport.pickParts(cursor.x, cursor.y)[0];
    if (!first) return false;
    store.setPartMode(first.file, toggledGhost(first.mode));
    return true;
  }

  const subs = [
    store.on("change:partModes", syncChip),
    store.on("mesh:loaded", syncChip),
  ];
  syncChip();

  function dispose() {
    closeMenu();
    for (const off of subs) off();
    canvas.removeEventListener("pointerdown", onDown);
    canvas.removeEventListener("pointermove", onMoveTrack);
    canvas.removeEventListener("pointerup", onUp);
    canvas.removeEventListener("pointerleave", onLeave);
    document.removeEventListener("pointerdown", onDocDown, true);
    document.removeEventListener("keydown", onKey, true);
    chip.remove();
  }

  return { toggleUnderCursor, resetAll: () => store.resetPartModes(), close: closeMenu, dispose };
}
