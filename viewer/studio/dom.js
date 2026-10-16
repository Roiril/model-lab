// Studio の画面部品で共有する小さな DOM 道具とアイコン。panels.js と parts-panel.js が使う。

export function h(tag, props, ...kids) {
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
export function add(el, kids) {
  for (const k of kids.flat(Infinity)) {
    if (k === undefined || k === null || k === false) continue;
    el.append(k.nodeType ? k : document.createTextNode(String(k)));
  }
  return el;
}
export const $ = (sel) => document.querySelector(sel);

// アイコン: 20px の枠、線 1.5px、自作。外部のアイコンフォントは使わない
export const ICONS = {
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
  pencil: '<path d="M12.5 4.5l3 3L7 16H4v-3z"/><path d="M11 6l3 3"/>',
  info: '<circle cx="10" cy="10" r="7"/><path d="M10 9v4.5M10 6.5v.2"/>',
};
export function icon(name, cls = "") {
  const span = document.createElement("span");
  span.className = `ic ${cls}`.trim();
  span.setAttribute("aria-hidden", "true");
  span.innerHTML = `<svg viewBox="0 0 20 20" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">${ICONS[name] || ""}</svg>`;
  return span;
}
export function tip(el, name, key) {
  el.dataset.tip = name;
  if (key) el.dataset.key = key;
  if (!el.getAttribute("aria-label")) el.setAttribute("aria-label", key ? `${name} ${key}` : name);
  return el;
}
export function kbd(text) { return h("kbd", { class: "kbd" }, text); }

export function composing(e) { return e.isComposing || e.keyCode === 229; }
