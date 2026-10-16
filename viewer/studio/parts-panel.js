// 右パネルの「部品」タブ。部品を日本語の名前で並べ、透過・隠す・呼び名の書き換えを受ける。
// 台帳（store.state.ledger）があれば群ごとの木、無ければ読み込み中の STL 名を平らに並べる。
// 状態は store（partModes / partNames / partHover）。3D への強調は store.hoverParts → app.js → viewport。
// 純関数は parts.js。ここは画面だけ。

import { h, icon, composing } from "./dom.js";
import { PART_MODES, PART_MODE_LABELS, countPartModes, modeOf } from "./part-modes.js";
import { KIND_LABELS, buildTree, commonMode, displayLabel, isRenamed, matchPart, systemLabelOf, withModes } from "./parts.js";

const lsKey = (model) => `studio.partGroups.${model}`;
function lsGet(key, fallback) {
  try { const v = localStorage.getItem(key); return v === null ? fallback : JSON.parse(v); } catch { return fallback; }
}
function lsSet(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch { /* 無くても動く */ } }

const DEFAULT_OPEN_MAX = 6;   // これ以下の部品数の群は最初から開く

// getFiles() -> 台帳が無いときに並べる、読み込み中の STL 名の配列
export function createPartsPanel({ store, getFiles }) {
  let query = "";
  let expanded = {};            // { groupId: true | false }。無い群は部品数で決める
  let expandedModel = null;
  let editingKey = null;
  let pending = false;
  let listPointer = false;      // 一覧の上にポインタがある（3D 側の指示で一覧を勝手に動かさない）
  const hoverKeysOf = new WeakMap();

  // --- 部品 ---
  const search = h("input", {
    type: "search", class: "field part-search", placeholder: "名前や別名で絞り込む",
    "aria-label": "部品を絞り込む", autocomplete: "off", spellcheck: "false",
  });
  const summary = h("span", { class: "part-summary" });
  const resetModes = h("button", { type: "button", class: "btn sm subtle", onclick: () => store.resetPartModes() }, icon("reset", "sm"), "すべて戻す");
  const list = h("div", { class: "part-list", role: "tree", "aria-label": "部品" });
  const names = h("div", { class: "part-names", hidden: true });
  const el = h("div", { class: "part-tab" },
    h("div", { class: "part-tools" }, search, h("div", { class: "part-meta" }, summary, resetModes)),
    h("div", { class: "scroll part-scroll" }, list),
    names);

  const ledger = () => store.state.ledger;
  const nameMap = () => store.state.partNames;

  function ensureExpanded() {
    if (expandedModel === store.state.model) return;
    expandedModel = store.state.model;
    expanded = lsGet(lsKey(expandedModel), {}) || {};
  }
  const isOpen = (group, count) => {
    if (query.trim()) return true;
    if (typeof expanded[group.id] === "boolean") return expanded[group.id];
    return count <= DEFAULT_OPEN_MAX;
  };
  function toggleGroup(group, count) {
    if (query.trim()) return;
    ensureExpanded();
    expanded = { ...expanded, [group.id]: !isOpen(group, count) };
    lsSet(lsKey(store.state.model), expanded);
    render();
  }

  function modeSeg(keys, label, mode) {
    const seg = h("div", { class: "seg part-seg", role: "group", "aria-label": `${label}の見え方` });
    for (const v of PART_MODES) {
      seg.append(h("button", {
        type: "button", class: "seg-btn", "aria-pressed": String(mode === v), "aria-label": `${label}の見え方: ${PART_MODE_LABELS[v]}`,
        onclick: (e) => { e.stopPropagation(); store.setPartModes(withModes(store.state.partModes, keys, v)); },
      }, PART_MODE_LABELS[v]));
    }
    return seg;
  }

  // --- 名前の書き換え ---
  function nameBlock(entry) {
    const { part, label } = entry;
    const box = h("div", { class: "pn" });
    if (part && editingKey === entry.key) {
      const input = h("input", {
        type: "text", class: "field pn-input", value: label, maxlength: "60",
        "aria-label": `${label}の呼び名`, autocomplete: "off",
      });
      let done = false;
      const finish = (commit) => {
        if (done) return;
        done = true;
        editingKey = null;
        const value = input.value;
        if (document.activeElement === input) input.blur();   // 入力中でなくしてから作り直す（schedule が待たない）
        if (commit && value.trim() !== label) store.setPartName(part, value);
        else render();
      };
      input.addEventListener("keydown", (e) => {
        if (composing(e)) return;
        if (e.key === "Enter") { e.preventDefault(); finish(true); }
        else if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); finish(false); }
      });
      input.addEventListener("blur", () => finish(true));
      box.append(input, h("div", { class: "pn-sub" }, "Enter で決める。Esc でやめる"));
      queueMicrotask(() => { input.focus(); input.select(); });
      return box;
    }
    const title = h("span", { class: "pn-label", title: part ? `${label}（ダブルクリックで書き換え）` : label }, label);
    const line = h("div", { class: "pn-line" }, title);
    if (part) {
      const edit = h("button", {
        type: "button", class: "icon-btn xs pn-edit", "aria-label": `${label}の呼び名を書き換える`, "data-tip": "呼び名を書き換える",
        onclick: (e) => { e.stopPropagation(); startEdit(entry.key); },
      }, icon("pencil"));
      line.append(edit);
      title.addEventListener("dblclick", () => startEdit(entry.key));
    }
    box.append(line);
    const sub = h("div", { class: "pn-sub" });
    if (part && isRenamed(part, nameMap())) sub.append(h("span", { class: "pn-sys" }, `シュビー: ${systemLabelOf(part)}`));
    if (part && KIND_LABELS[part.kind] && part.kind !== "printed") sub.append(h("span", { class: "tag" }, KIND_LABELS[part.kind]));
    sub.append(h("span", { class: "pn-id mono" }, entry.id));
    box.append(sub);
    return box;
  }
  function startEdit(key) {
    editingKey = key;
    render();
  }

  // --- 行 ---
  function rowFor(entry) {
    const mode = modeOf(store.state.partModes, entry.key);
    const row = h("div", { class: "pr", role: "treeitem", "data-key": entry.key, "data-mode": mode, "aria-selected": "false" },
      h("span", { class: `swatch${entry.color ? "" : " none"}`, style: entry.color ? `--c:${entry.color}` : null, "aria-hidden": "true" }),
      nameBlock(entry),
      modeSeg([entry.key], entry.label, mode));
    hoverKeysOf.set(row, [entry.key]);
    return row;
  }

  function groupBlock(node) {
    const keys = node.parts.map((p) => p.id);
    const open = isOpen(node.group, node.parts.length);
    const head = h("div", { class: "pg-head" });
    const toggle = h("button", {
      type: "button", class: "pg-toggle", "aria-expanded": String(open), "aria-label": `${node.group.label}（${node.parts.length} 部品）`,
      onclick: () => toggleGroup(node.group, node.parts.length),
    },
    icon("chevron", "sm chev"),
    h("span", { class: `swatch${node.group.color ? "" : " none"}`, style: node.group.color ? `--c:${node.group.color}` : null, "aria-hidden": "true" }),
    h("span", { class: "pg-label" }, node.group.label),
    h("span", { class: "pg-count mono" }, String(node.parts.length)));
    head.append(toggle, modeSeg(keys, node.group.label, commonMode(keys, store.state.partModes)));
    hoverKeysOf.set(head, keys);
    const box = h("section", { class: "pg", "data-group": node.group.id, "data-open": String(open) }, head);
    if (!open) box.append(h("div", { class: "pg-hot", hidden: true }));
    if (open) {
      const rows = h("div", { class: "pg-rows", role: "group" });
      for (const p of node.parts) {
        rows.append(rowFor({
          key: p.id, id: p.id, part: p, label: displayLabel(p, nameMap()), color: p.color || node.group.color,
        }));
      }
      box.append(rows);
    }
    return box;
  }

  // --- 描画 ---
  function entriesFlat() {
    const q = query.trim();
    return (getFiles() || []).filter((f) => matchPart({ id: f, label: f, aliases: [] }, {}, "", q)).map((f) => ({ key: f, id: f, part: null, label: f, color: null }));
  }

  function render() {
    pending = false;
    ensureExpanded();
    const led = ledger();
    const modes = store.state.partModes;
    list.replaceChildren();
    let total = 0;
    let shown = 0;
    let keysAll = [];
    if (led) {
      total = led.parts.length;
      keysAll = led.parts.map((p) => p.id);
      const tree = buildTree(led, nameMap(), query);
      shown = tree.reduce((n, g) => n + g.parts.length, 0);
      for (const node of tree) list.append(groupBlock(node));
    } else {
      const all = getFiles() || [];
      total = all.length;
      keysAll = all;
      const rows = entriesFlat();
      shown = rows.length;
      if (all.length) list.append(h("p", { class: "empty" }, "このモデルには部品の名前表がまだありません。ファイル名のまま並べています。"));
      const box = h("div", { class: "pg-rows flat", role: "group" });
      for (const r of rows) box.append(rowFor(r));
      list.append(box);
    }
    if (!shown) list.append(h("p", { class: "empty" }, total ? "一致する部品がありません。" : "表示している部品がありません。"));

    const { ghost, hidden } = countPartModes(modes, keysAll);
    const parts = [query.trim() ? `${shown} / ${total} 部品` : `${total} 部品`];
    if (ghost) parts.push(`透過 ${ghost}`);
    if (hidden) parts.push(`隠す ${hidden}`);
    summary.textContent = parts.join(" · ");
    resetModes.hidden = ghost + hidden === 0;

    const changed = led ? Object.keys(nameMap()).filter((id) => led.byId.has(id) && nameMap()[id].label !== led.byId.get(id).label) : [];
    names.hidden = changed.length === 0;
    names.replaceChildren();
    if (changed.length) {
      names.append(
        h("p", {}, `呼び名を変えた部品 ${changed.length} 件。次に送る依頼でシュビーに伝わります。`),
        h("button", { type: "button", class: "btn sm subtle", onclick: () => store.resetPartNames() }, icon("reset", "sm"), "呼び名を元に戻す"));
    }
    markHot();
  }

  // 入力中の欄がある間は作り直さない（打っている途中の文字を消さない）
  function schedule() {
    const a = document.activeElement;
    if (a && el.contains(a) && a.matches("input")) { pending = true; return; }
    render();
  }
  el.addEventListener("focusout", () => {
    if (pending) setTimeout(() => { if (pending && !el.contains(document.activeElement)) render(); }, 0);
  });

  // --- 指している部品 ---
  function markHot() {
    const hot = new Set(store.state.partHover || []);
    let first = null;
    for (const row of list.querySelectorAll(".pr")) {
      const on = hot.has(row.dataset.key);
      row.classList.toggle("hot", on);
      if (on && !first) first = row;
    }
    for (const box of list.querySelectorAll(".pg")) {
      const keys = hoverKeysOf.get(box.querySelector(".pg-head")) || [];
      const inside = keys.some((k) => hot.has(k));
      const closedHot = inside && box.dataset.open !== "true";
      box.classList.toggle("has-hot", closedHot);
      box.querySelector(".pg-head").classList.toggle("hot", inside && keys.every((k) => hot.has(k)) && keys.length > 1);
      // 閉じた群の中の部品を指しているときは、その名前を群の下に出す
      const line = box.querySelector(".pg-hot");
      if (line) {
        const led = ledger();
        const hotKeys = closedHot && led ? keys.filter((k) => hot.has(k)) : [];
        line.hidden = !hotKeys.length;
        if (hotKeys.length) line.textContent = displayLabel(led.byId.get(hotKeys[0]), nameMap()) + (hotKeys.length > 1 ? ` ほか ${hotKeys.length - 1} 件` : "");
      }
    }
    if (first && !listPointer) first.scrollIntoView({ block: "nearest" });
  }
  const hoverFrom = (target) => {
    const node = target && target.closest ? target.closest(".pr, .pg-head") : null;
    store.hoverParts(node ? hoverKeysOf.get(node) || [] : []);
  };
  list.addEventListener("pointerover", (e) => { listPointer = true; hoverFrom(e.target); });
  list.addEventListener("pointerleave", () => { listPointer = false; store.hoverParts([]); });
  list.addEventListener("focusin", (e) => { hoverFrom(e.target); });
  list.addEventListener("focusout", (e) => { if (!list.contains(e.relatedTarget)) store.hoverParts([]); });

  search.addEventListener("input", () => { query = search.value; render(); });
  search.addEventListener("keydown", (e) => { if (e.key === "Escape" && search.value) { e.stopPropagation(); search.value = ""; query = ""; render(); } });

  const subs = [
    store.on("change:partModes", schedule),
    store.on("change:partNames", schedule),
    store.on("change:ledger", () => { editingKey = null; render(); }),
    store.on("change:partHover", markHot),
    store.on("change:model", () => { editingKey = null; query = ""; search.value = ""; expandedModel = null; }),
  ];

  render();
  return {
    el,
    refresh: schedule,
    // 部品タブを出す価値があるか（台帳があるか、組立の STL が複数あるか。印刷プレートは派生 STL の名前なので出さない）
    hasList: () => !!ledger() || (store.state.layout?.kind !== "plate" && (getFiles() || []).length > 1),
    dispose() { for (const off of subs) off(); },
  };
}
