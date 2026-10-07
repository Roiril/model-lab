// 断面。平面を作り、3D に半透明の面と輪郭線を出し、2D エディタ用の輪郭を section:loops で渡す。
// 契約は CONTRACT.md §4。座標の約束は frames.js。

import * as THREE from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { makePlane, planeAt, uvToModel, modelToUv, dot } from "./frames.js";
import { slicePositions, loopsBounds } from "./slice.js";

const CLICK_PX = 4;
const THROTTLE_MS = 60;

// geometry（モデル座標・非 index）を平面で切る。BVH があれば平面と交わる範囲だけ見る
export function sliceGeometry(geometry, plane, offset, bvh) {
  const pos = geometry.attributes.position.array;
  const tree = bvh || geometry.boundsTree;
  let ids = null;
  if (tree) {
    const at = planeAt(plane, offset);
    const tp = new THREE.Plane(new THREE.Vector3(at.normal[0], at.normal[1], at.normal[2]), -dot(at.normal, at.origin));
    ids = [];
    tree.shapecast({
      intersectsBounds: (box) => box.intersectsPlane(tp),
      intersectsTriangle: (tri, index) => { ids.push(index); return false; },
    });
  }
  return slicePositions(pos, ids, plane, offset, 1);
}

export function createSections(viewport, store) {
  const { canvas, overlay } = viewport;
  const group = new THREE.Group();
  group.name = "sections";
  overlay.add(group);

  const secs = new Map();      // id -> { sig, loops, ghostLoops, bounds, vis, timer, last }
  let version = 0;             // メッシュ・ゴーストが入れ替わるたびに増やす（切り直しの合図）

  const isPreview = () => store.state.frame === "preview-m-yup";

  // ---- 平面の枠（モデルを囲む長方形）---------------------------------------
  function modelCorners() {
    const b = viewport.modelBox();
    const out = [];
    for (const x of [b.min[0], b.max[0]]) for (const y of [b.min[1], b.max[1]]) for (const z of [b.min[2], b.max[2]]) out.push([x, y, z]);
    return out;
  }
  function planeRect(plane, offset) {
    let u0 = Infinity, v0 = Infinity, u1 = -Infinity, v1 = -Infinity;
    for (const c of modelCorners()) {
      const [u, v] = modelToUv(plane, offset, c);
      if (u < u0) u0 = u; if (u > u1) u1 = u;
      if (v < v0) v0 = v; if (v > v1) v1 = v;
    }
    const m = Math.max(u1 - u0, v1 - v0, 1) * 0.06;
    return { u0: u0 - m, u1: u1 + m, v0: v0 - m, v1: v1 + m };
  }

  // ---- 3D の見た目 ----------------------------------------------------------
  function makeVis(color) {
    const col = new THREE.Color(color);
    const fill = new THREE.Mesh(
      new THREE.BufferGeometry(),
      new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.12, side: THREE.DoubleSide, depthWrite: false }),
    );
    fill.renderOrder = 3;
    fill.raycast = () => {};
    fill.frustumCulled = false;
    const border = new THREE.LineLoop(
      new THREE.BufferGeometry(),
      new THREE.LineBasicMaterial({ color: col, transparent: true, opacity: 1, depthWrite: false }),
    );
    border.renderOrder = 4;
    border.raycast = () => {};
    border.frustumCulled = false;
    const g = new THREE.Group();
    g.add(fill, border);
    group.add(g);
    const { width, height } = viewport.size();
    const lineMat = new LineMaterial({
      color: col, linewidth: 3, transparent: true, opacity: 1, depthTest: false, worldUnits: false,
      resolution: new THREE.Vector2(width || 1, height || 1),
    });
    return { group: g, fill, border, lines: null, lineMat, color };
  }

  function disposeVis(vis) {
    vis.fill.geometry.dispose(); vis.fill.material.dispose();
    vis.border.geometry.dispose(); vis.border.material.dispose();
    if (vis.lines) { vis.lines.geometry.dispose(); }
    vis.lineMat.dispose();
    group.remove(vis.group);
  }

  function updatePlaneGeometry(vis, item) {
    const r = planeRect(item.plane, item.offset || 0);
    const P = [[r.u0, r.v0], [r.u1, r.v0], [r.u1, r.v1], [r.u0, r.v1]].map((uv) => uvToModel(item.plane, item.offset || 0, uv));
    const pos = new Float32Array(P.flat());
    vis.border.geometry.dispose();
    vis.border.geometry = new THREE.BufferGeometry();
    vis.border.geometry.setAttribute("position", new THREE.BufferAttribute(pos.slice(), 3));
    vis.fill.geometry.dispose();
    vis.fill.geometry = new THREE.BufferGeometry();
    vis.fill.geometry.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    vis.fill.geometry.setIndex([0, 1, 2, 0, 2, 3]);
  }

  function updateLines(vis, item, loops) {
    if (vis.lines) { vis.group.remove(vis.lines); vis.lines.geometry.dispose(); vis.lines = null; }
    const seg = [];
    for (const l of loops) {
      const pts = l.points.map((uv) => uvToModel(item.plane, item.offset || 0, uv));
      const n = pts.length;
      for (let i = 0; i < n - 1; i++) seg.push(...pts[i], ...pts[i + 1]);
      if (l.closed && n > 2) seg.push(...pts[n - 1], ...pts[0]);
    }
    if (!seg.length) return;
    const g = new LineSegmentsGeometry();
    g.setPositions(new Float32Array(seg));
    const ls = new LineSegments2(g, vis.lineMat);
    ls.renderOrder = 6;
    ls.raycast = () => {};
    ls.frustumCulled = false;
    vis.group.add(ls);
    vis.lines = ls;
  }

  function restyle() {
    const active = store.state.activeSectionId;
    for (const [id, s] of secs) {
      const it = store.getItem(id);
      if (!it || !s.vis) continue;
      const on = id === active;
      const col = new THREE.Color(it.color);
      s.vis.fill.material.color.copy(col);
      s.vis.fill.material.opacity = on ? 0.12 : 0.05;
      s.vis.border.material.color.copy(col);
      s.vis.border.material.opacity = on ? 1 : 0.4;
      s.vis.lineMat.color.copy(col);
      s.vis.lineMat.linewidth = on ? 3.2 : 1.6;
      s.vis.lineMat.opacity = on ? 1 : 0.5;
      s.vis.lineMat.depthTest = false;
    }
    viewport.invalidate();
  }

  // 太い線は画面の大きさを知る必要がある
  const offFrame = viewport.onFrame(() => {
    const { width, height } = viewport.size();
    for (const s of secs.values()) {
      if (!s.vis) continue;
      const r = s.vis.lineMat.resolution;
      if (r.x !== width || r.y !== height) r.set(width, height);
    }
  });

  // ---- 切断 -----------------------------------------------------------------
  function emptyBounds(plane, offset) {
    const r = planeRect(plane, offset);
    return { min: [r.u0, r.v0], max: [r.u1, r.v1] };
  }

  function run(id) {
    const s = secs.get(id);
    const item = store.getItem(id);
    if (!s || !item || item.type !== "section" || !item.plane) return;
    s.last = performance.now();
    const offset = item.offset || 0;
    let loops = [];
    for (const m of viewport.getMeshes()) loops = loops.concat(sliceGeometry(m.geometry, item.plane, offset));
    let ghostLoops = [];
    const gg = viewport.getGhostGeometry();
    if (gg) ghostLoops = sliceGeometry(gg, item.plane, offset);

    const a = loopsBounds(loops), b = loopsBounds(ghostLoops);
    let bounds;
    if (a && b) {
      bounds = { min: [Math.min(a.min[0], b.min[0]), Math.min(a.min[1], b.min[1])], max: [Math.max(a.max[0], b.max[0]), Math.max(a.max[1], b.max[1])] };
    } else {
      bounds = a || b || emptyBounds(item.plane, offset);
    }
    s.loops = loops; s.ghostLoops = ghostLoops; s.bounds = bounds;

    if (!s.vis) s.vis = makeVis(item.color);
    updatePlaneGeometry(s.vis, item);
    updateLines(s.vis, item, loops);
    restyle();
    store.emit("section:loops", { id, loops, ghostLoops, bounds });
  }

  // ドラッグ中の連続更新は間引く（先頭を即実行し、間に来た分は最後の 1 回にまとめる）
  function schedule(id) {
    const s = secs.get(id);
    if (!s || s.timer) return;
    const wait = THROTTLE_MS - (performance.now() - s.last);
    if (wait <= 0) { run(id); return; }
    s.timer = setTimeout(() => { s.timer = 0; run(id); }, wait);
  }

  function signature(item) {
    return JSON.stringify([item.plane, item.offset || 0, version]);
  }

  // items と secs を突き合わせる
  function sync() {
    const alive = new Set();
    for (const it of store.state.draft.items) {
      if (it.type !== "section" || !it.plane) continue;
      alive.add(it.id);
      let s = secs.get(it.id);
      if (!s) {
        s = { sig: "", loops: [], ghostLoops: [], bounds: null, vis: null, timer: 0, last: 0 };
        secs.set(it.id, s);
      }
      const sig = signature(it);
      if (sig !== s.sig) {
        s.sig = sig;
        schedule(it.id);
      }
    }
    for (const [id, s] of [...secs]) {
      if (alive.has(id)) continue;
      clearTimeout(s.timer);
      if (s.vis) disposeVis(s.vis);
      secs.delete(id);
    }
    restyle();
    syncClip();
  }

  // アクティブな断面が「片側を隠す」なら、その面で隠す
  function syncClip() {
    if (isPreview()) { viewport.setClipPlane(null); return; }
    const it = store.getItem(store.state.activeSectionId);
    if (it && it.type === "section" && it.clip && it.plane) viewport.setClipPlane(planeAt(it.plane, it.offset || 0));
    else viewport.setClipPlane(null);
  }

  // ---- クリックで断面を作る ---------------------------------------------------
  let down = null;
  const onDown = (e) => {
    if (e.button !== 0 || store.state.tool !== "section" || isPreview()) { down = null; return; }
    down = { id: e.pointerId, x: e.clientX, y: e.clientY };
  };
  const onMove = (e) => {
    if (down && down.id === e.pointerId && Math.hypot(e.clientX - down.x, e.clientY - down.y) >= CLICK_PX) down = null;
  };
  const onUp = (e) => {
    if (!down || down.id !== e.pointerId) return;
    const d = down;
    down = null;
    if (Math.hypot(e.clientX - d.x, e.clientY - d.y) >= CLICK_PX) return;
    if (store.state.tool !== "section" || isPreview()) return;
    const hit = viewport.pick(e.clientX, e.clientY);
    if (!hit) return;
    let plane;
    try {
      plane = makePlane(store.state.sectionAxis, hit.point, viewport.cameraAxes());
    } catch (err) {
      console.error("[section] 平面を作れません", err);
      store.status("断面の平面を作れませんでした", "err");
      return;
    }
    const id = store.addItem({ type: "section", file: hit.file, plane, offset: 0, clip: false });
    store.set({ activeSectionId: id });
  };
  canvas.addEventListener("pointerdown", onDown);
  canvas.addEventListener("pointermove", onMove);
  canvas.addEventListener("pointerup", onUp);
  canvas.addEventListener("pointercancel", () => { down = null; });

  let cursorOwned = false;
  function updateCursor() {
    if (store.state.tool === "section" && !isPreview()) { canvas.style.cursor = "crosshair"; cursorOwned = true; }
    else if (cursorOwned) { canvas.style.cursor = ""; cursorOwned = false; }
  }

  // ---- 購読 -------------------------------------------------------------------
  const subs = [
    store.on("items", sync),
    store.on("change:activeSectionId", () => { restyle(); syncClip(); }),
    store.on("change:tool", updateCursor),
    store.on("change:frame", () => { updateCursor(); syncClip(); }),
    store.on("mesh:loaded", () => {
      version++;
      for (const s of secs.values()) s.sig = "";
      sync();
    }),
    store.on("ghost:loaded", () => {
      version++;
      for (const s of secs.values()) s.sig = "";
      sync();
    }),
    store.on("item:focus", ({ id }) => {
      const it = store.getItem(id);
      if (!it || it.type !== "section" || !it.plane) return;
      // 平面を正面から見る。z 面は上から見たときの画面の上が v になるよう、わずかに手前へずらす
      const n = it.plane.normal, v = it.plane.v;
      viewport.viewPreset([n[0] - v[0] * 0.001, n[1] - v[1] * 0.001, n[2] - v[2] * 0.001]);
    }),
  ];
  updateCursor();
  sync();

  function getLoops(id) {
    const s = secs.get(id);
    return s ? { loops: s.loops, ghostLoops: s.ghostLoops, bounds: s.bounds } : null;
  }

  function dispose() {
    for (const off of subs) off();
    offFrame();
    for (const s of secs.values()) {
      clearTimeout(s.timer);
      if (s.vis) disposeVis(s.vis);
    }
    secs.clear();
    viewport.setClipPlane(null);
    canvas.removeEventListener("pointerdown", onDown);
    canvas.removeEventListener("pointermove", onMove);
    canvas.removeEventListener("pointerup", onUp);
    if (cursorOwned) canvas.style.cursor = "";
    overlay.remove(group);
  }

  return { getLoops, dispose };
}
