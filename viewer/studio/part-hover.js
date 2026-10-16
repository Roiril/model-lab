// 3D でカーソルの下にある部品を一覧と同期する。
//   カーソルの下の部品（クリックで指示が付く部品）を store.hoverParts に流す → 一覧の行と 3D の強調が追従する
//   カーソルのそばに部品の名前を出す
// 反対向き（一覧 → 3D）は parts-panel.js が store.hoverParts を呼び、app.js が viewport.setHoverParts に渡す。

import { partKey } from "./part-modes.js";

const GAP = 14;

// describe(key, file) -> { name, group? }。台帳があれば日本語の名前、無ければ STL 名
export function createPartHover(viewport, store, { host, describe }) {
  const { canvas } = viewport;
  const nameEl = document.createElement("span");
  nameEl.className = "part-tag-name";
  const groupEl = document.createElement("span");
  groupEl.className = "part-tag-group";
  const tag = document.createElement("div");
  tag.className = "part-tag";
  tag.hidden = true;
  tag.setAttribute("aria-hidden", "true");
  tag.append(nameEl, groupEl);
  host.append(tag);

  let raf = 0;
  let last = null;

  function hide() { tag.hidden = true; }
  function clear() {
    last = null;
    hide();
    store.hoverParts([]);
  }

  function place(e) {
    const r = host.getBoundingClientRect();
    tag.hidden = false;
    const w = tag.offsetWidth, h = tag.offsetHeight;
    let x = e.clientX - r.left + GAP;
    let y = e.clientY - r.top + GAP;
    if (x + w > r.width - 4) x = e.clientX - r.left - w - GAP;
    if (y + h > r.height - 4) y = e.clientY - r.top - h - GAP;
    tag.style.left = `${Math.max(4, x)}px`;
    tag.style.top = `${Math.max(4, y)}px`;
  }

  function update() {
    raf = 0;
    const e = last;
    if (!e) return;
    if (store.state.frame === "preview-m-yup" || !viewport.getMeshes().length) { clear(); return; }
    const hit = viewport.pick(e.clientX, e.clientY);
    if (!hit) { hide(); store.hoverParts([]); return; }
    const key = partKey(hit.mesh.userData);
    store.hoverParts([key]);
    // 部品が 1 つしかないモデルでは、名前を出しても情報が増えない
    if (viewport.getMeshes().length < 2) { hide(); return; }
    const d = describe(key, hit.file);
    nameEl.textContent = d.name;
    groupEl.textContent = d.group || "";
    groupEl.hidden = !d.group;
    place(e);
  }

  const onMove = (e) => {
    if (e.buttons) { hide(); return; }            // 視点を動かしている間は出さない
    last = e;
    if (!raf) raf = requestAnimationFrame(update);
  };
  canvas.addEventListener("pointermove", onMove);
  canvas.addEventListener("pointerleave", clear);
  canvas.addEventListener("pointerdown", hide);

  function dispose() {
    cancelAnimationFrame(raf);
    canvas.removeEventListener("pointermove", onMove);
    canvas.removeEventListener("pointerleave", clear);
    canvas.removeEventListener("pointerdown", hide);
    tag.remove();
  }
  return { dispose };
}
