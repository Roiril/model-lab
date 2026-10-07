// 3D 上の指示の道具（面の選択・ピン・計測）と、その重ね描き。契約は CONTRACT.md §4。
//
// 契約に足したもの:
//   cancel()   途中の計測（1 点目）とピンの仮置きをやめる
// 動作の補足:
//   - popover の x, y は client 座標（clientX / clientY と同じ系。position: fixed にそのまま使える）
//   - 角度のスライダー（state.faceAngle）を動かすと、直前に「塗り広げ」で選んだ面を選び直し、
//     popover を同じ形でもう一度出す（250ms 間引き）。UI は新しい popover で置き換えること

import * as THREE from "three";
import { SELECTION_COLOR, PIN_COLOR, MEASURE_COLOR } from "./store.js";

const CLICK_PX = 4;
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));

export function createPicking(viewport, store) {
  const { canvas, overlay } = viewport;
  const group = new THREE.Group();
  group.name = "picking";
  overlay.add(group);

  // ---- 小物 ---------------------------------------------------------------
  const isPreview = () => store.state.frame === "preview-m-yup";
  const toolActive = () => !isPreview() && (store.state.tool === "faces" || store.state.tool === "pin" || store.state.tool === "measure");
  const meshByFile = (file) => viewport.getMeshes().find((m) => m.userData.file === file) || null;

  function unit() {
    const b = viewport.modelBox();
    const d = Math.max(b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]);
    return clamp(d * 0.012, 0.4, 5);
  }

  function disposeObj(o) {
    o.traverse((c) => {
      if (c.geometry) c.geometry.dispose();
      if (c.material) {
        viewport.unclipMaterial(c.material);
        c.material.dispose();
      }
    });
    if (o.parent) o.parent.remove(o);
  }

  // 選んだ三角形だけの Mesh（モデル座標。ずらして手前に描く）
  function trianglesMesh(mesh, ids, color, opacity) {
    const src = mesh.geometry.attributes.position.array;
    const out = new Float32Array(ids.length * 9);
    for (let i = 0; i < ids.length; i++) {
      const s = ids[i] * 9, d = i * 9;
      out[d] = src[s]; out[d + 1] = src[s + 1]; out[d + 2] = src[s + 2];
      out[d + 3] = src[s + 3]; out[d + 4] = src[s + 4]; out[d + 5] = src[s + 5];
      out[d + 6] = src[s + 6]; out[d + 7] = src[s + 7]; out[d + 8] = src[s + 8];
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(out, 3));
    const mat = new THREE.MeshBasicMaterial({
      color: new THREE.Color(color), transparent: true, opacity, depthWrite: false,
      side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
    });
    viewport.clipMaterial(mat);
    const m = new THREE.Mesh(g, mat);
    m.renderOrder = 2;
    m.raycast = () => {};
    m.frustumCulled = false;
    return m;
  }

  function badge(text, { bg, fg, mono = false, round = false }) {
    const el = document.createElement("div");
    el.textContent = text;
    Object.assign(el.style, {
      background: bg, color: fg, font: `600 11px/1 ${mono ? "ui-monospace, Consolas, monospace" : "system-ui, sans-serif"}`,
      padding: round ? "0" : "3px 6px", borderRadius: round ? "50%" : "4px",
      width: round ? "20px" : "auto", height: round ? "20px" : "auto",
      display: "flex", alignItems: "center", justifyContent: "center",
      border: "1px solid rgba(0,0,0,.35)", whiteSpace: "nowrap", pointerEvents: "none",
    });
    return el;
  }

  const addVec = (a, b, s = 1) => [a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s];
  const distance = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

  // ---- 面の情報（Worker）--------------------------------------------------
  async function ensureInfo(mesh) {
    if (viewport.hasGeomInfo(mesh)) return viewport.geomInfo(mesh);
    const t0 = performance.now();
    store.status("面の情報を準備中 …", "busy");
    try {
      const info = await viewport.geomInfo(mesh);
      store.status(`面の情報を準備しました · ${((performance.now() - t0) / 1000).toFixed(1)} 秒`, "ok");
      return info;
    } catch (e) {
      console.error("[picking] 面の情報", e);
      store.status(`面の情報を作れませんでした: ${e.message}`, "err");
      return null;
    }
  }
  function prefetch() {
    if (!toolActive() || store.state.tool !== "faces") return;
    for (const m of viewport.getMeshes()) {
      if (!viewport.hasGeomInfo(m)) ensureInfo(m);
    }
  }

  // ---- 選択 ---------------------------------------------------------------
  // マスク（三角形ごとの 0/1）を持つ。state.selection は三角形番号の配列
  let selMesh = null;
  let selMask = null;
  let ownSelection = null;          // 自分で入れた配列（外から差し替えられたか見分ける）
  let selObj = null;                // 確定前の選択の重ね描き
  let lastSmart = null;             // { mesh, seed }

  function maskToList(mask) {
    const out = [];
    for (let i = 0; i < mask.length; i++) if (mask[i]) out.push(i);
    return out;
  }

  function drawSelection(mesh, ids) {
    if (selObj) { disposeObj(selObj); selObj = null; }
    if (mesh && ids && ids.length) {
      selObj = trianglesMesh(mesh, ids, SELECTION_COLOR, 0.55);
      group.add(selObj);
    }
    viewport.invalidate();
  }

  function setSelection(mesh, mask, { quiet = false } = {}) {
    const list = mask ? maskToList(mask) : [];
    selMesh = list.length ? mesh : null;
    selMask = list.length ? mask : null;
    ownSelection = list;
    store.set({ selection: list, selectionFile: list.length ? mesh.userData.file : null });
    if (!list.length) lastSmart = null;
    drawSelection(selMesh, list);
    return list;
  }

  // state.selection が外から変わった（Esc で空にした / カード化した）とき
  const offSel = store.on("change:selection", (sel) => {
    if (sel === ownSelection) return;
    if (!sel.length) {
      selMesh = null; selMask = null; ownSelection = sel; lastSmart = null;
      drawSelection(null, null);
      store.emit("popover:close");
      return;
    }
    const mesh = meshByFile(store.state.selectionFile);
    if (!mesh) return;
    const mask = new Uint8Array(mesh.userData.triangles);
    for (const i of sel) if (i < mask.length) mask[i] = 1;
    selMesh = mesh; selMask = mask; ownSelection = sel;
    drawSelection(mesh, sel);
  });

  // ---- 塗り広げ（種の面の法線との角で止める）-------------------------------
  function growRegion(info, seed, angleDeg) {
    const { adjOffsets, adj, normals, triCount } = info;
    const out = [seed];
    const sx = normals[seed * 3], sy = normals[seed * 3 + 1], sz = normals[seed * 3 + 2];
    if (sx === 0 && sy === 0 && sz === 0) return out;                // 面積 0 の面
    const cosThr = Math.cos((angleDeg * Math.PI) / 180);
    const seen = new Uint8Array(triCount);
    seen[seed] = 1;
    const stack = [seed];
    while (stack.length) {
      const t = stack.pop();
      for (let i = adjOffsets[t], e = adjOffsets[t + 1]; i < e; i++) {
        const n = adj[i];
        if (seen[n]) continue;
        seen[n] = 1;
        if (normals[n * 3] * sx + normals[n * 3 + 1] * sy + normals[n * 3 + 2] * sz >= cosThr) {
          out.push(n);
          stack.push(n);
        }
      }
    }
    return out;
  }

  function combine(mesh, ids, mode) {
    const T = mesh.userData.triangles;
    let mask;
    if (mode === "replace" || selMesh !== mesh || !selMask) {
      mask = new Uint8Array(T);
      if (mode === "remove") return setSelection(null, null);
    } else {
      mask = selMask.slice();
    }
    const v = mode === "remove" ? 0 : 1;
    for (let i = 0; i < ids.length; i++) mask[ids[i]] = v;
    return setSelection(mesh, mask);
  }

  const modeOf = (e) => (e.shiftKey ? "add" : e.altKey ? "remove" : "replace");

  // ---- ブラシ ---------------------------------------------------------------
  const _sphere = new THREE.Sphere();
  const _c = new THREE.Vector3();
  const _p = new THREE.Vector3();
  const _n = new THREE.Vector3();
  const _cam = new THREE.Vector3();

  function dab(mesh, mask, center, radius, value) {
    const bvh = mesh.geometry.boundsTree;
    if (!bvh) return false;
    _c.set(center[0], center[1], center[2]);
    _sphere.set(_c, radius);
    const r2 = radius * radius;
    const cam = viewport.toModel(viewport.camera.position);
    _cam.set(cam[0], cam[1], cam[2]);
    let changed = false;
    bvh.shapecast({
      intersectsBounds: (box) => box.intersectsSphere(_sphere),
      intersectsTriangle: (tri, index) => {
        tri.closestPointToPoint(_c, _p);
        if (_p.distanceToSquared(_c) > r2) return false;
        tri.getNormal(_n);
        // 法線がカメラ側を向く面だけ（裏側は塗らない）
        if (_n.dot(_p.copy(tri.a).sub(_cam)) >= 0) return false;
        if (mask[index] !== value) { mask[index] = value; changed = true; }
        return false;
      },
    });
    return changed;
  }

  // ブラシの輪（カーソル）
  let ring = null;
  function updateRing(hit) {
    const show = hit && store.state.tool === "faces" && store.state.faceMode === "brush" && !isPreview();
    if (!show) {
      if (ring && ring.visible) { ring.visible = false; viewport.invalidate(); }
      return;
    }
    const r = store.state.brushRadius;
    if (!ring || ring.userData.r !== r) {
      if (ring) disposeObj(ring);
      const pts = [];
      for (let i = 0; i < 64; i++) pts.push(new THREE.Vector3(Math.cos((i / 64) * Math.PI * 2) * r, Math.sin((i / 64) * Math.PI * 2) * r, 0));
      ring = new THREE.LineLoop(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: new THREE.Color(SELECTION_COLOR), depthTest: false, transparent: true }),
      );
      ring.userData.r = r;
      ring.renderOrder = 10;
      ring.raycast = () => {};
      ring.frustumCulled = false;
      group.add(ring);
    }
    const n = new THREE.Vector3(hit.normal[0], hit.normal[1], hit.normal[2]);
    ring.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), n);
    ring.position.set(hit.point[0], hit.point[1], hit.point[2]).addScaledVector(n, 0.05);
    ring.visible = true;
    viewport.invalidate();
  }

  // ---- 面の要約 -------------------------------------------------------------
  function summarizeFaces(mesh, faceIds) {
    const p = mesh.geometry.attributes.position.array;
    const n = faceIds.length;
    let area = 0, nx = 0, ny = 0, nz = 0, cx = 0, cy = 0, cz = 0;
    let x0 = Infinity, y0 = Infinity, z0 = Infinity, x1 = -Infinity, y1 = -Infinity, z1 = -Infinity;
    for (let k = 0; k < n; k++) {
      const b = faceIds[k] * 9;
      const ax = p[b], ay = p[b + 1], az = p[b + 2];
      const bx = p[b + 3], by = p[b + 4], bz = p[b + 5];
      const qx = p[b + 6], qy = p[b + 7], qz = p[b + 8];
      const ex = bx - ax, ey = by - ay, ez = bz - az, fx = qx - ax, fy = qy - ay, fz = qz - az;
      const gx = ey * fz - ez * fy, gy = ez * fx - ex * fz, gz = ex * fy - ey * fx;    // 面積 × 2 × 法線
      const a = Math.hypot(gx, gy, gz) / 2;
      area += a; nx += gx; ny += gy; nz += gz;
      cx += a * (ax + bx + qx) / 3; cy += a * (ay + by + qy) / 3; cz += a * (az + bz + qz) / 3;
      for (let v = 0; v < 9; v += 3) {
        const x = p[b + v], y = p[b + v + 1], z = p[b + v + 2];
        if (x < x0) x0 = x; if (x > x1) x1 = x;
        if (y < y0) y0 = y; if (y > y1) y1 = y;
        if (z < z0) z0 = z; if (z > z1) z1 = z;
      }
    }
    const nl = Math.hypot(nx, ny, nz) || 1;
    const centroid = area > 0 ? [cx / area, cy / area, cz / area] : [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2];

    const triNormal = (id) => {
      const b = id * 9;
      const ex = p[b + 3] - p[b], ey = p[b + 4] - p[b + 1], ez = p[b + 5] - p[b + 2];
      const fx = p[b + 6] - p[b], fy = p[b + 7] - p[b + 1], fz = p[b + 8] - p[b + 2];
      const gx = ey * fz - ez * fy, gy = ez * fx - ex * fz, gz = ex * fy - ey * fx;
      const l = Math.hypot(gx, gy, gz);
      return l > 0 ? [gx / l, gy / l, gz / l] : null;
    };
    const triCentroid = (id) => {
      const b = id * 9;
      return [(p[b] + p[b + 3] + p[b + 6]) / 3, (p[b + 1] + p[b + 4] + p[b + 7]) / 3, (p[b + 2] + p[b + 5] + p[b + 8]) / 3];
    };
    const r = (x) => Math.round(x * 1000) / 1000;

    // 重心・法線つきの標本（最大 300）
    const samples = [];
    const stride = Math.max(1, Math.floor(n / 300));
    for (let k = 0; k < n && samples.length < 300; k += stride) {
      const id = faceIds[k];
      const tn = triNormal(id);
      if (!tn) continue;
      const c = triCentroid(id);
      samples.push([r(c[0]), r(c[1]), r(c[2]), r(tn[0]), r(tn[1]), r(tn[2])]);
    }

    // 今の肉厚: 標本の点から法線の逆向きに撃ち、最初に当たる裏面までの距離
    let thickness = null;
    const bvh = mesh.geometry.boundsTree;
    if (bvh && samples.length) {
      const ds = [];
      const step = Math.max(1, Math.floor(samples.length / 20));
      const ray = new THREE.Ray();
      for (let k = 0; k < samples.length && ds.length < 20; k += step) {
        const s = samples[k];
        const EPS = 0.01;                                       // 面の少し内側から始める（自分自身に当たらない）
        ray.origin.set(s[0] - s[3] * EPS, s[1] - s[4] * EPS, s[2] - s[5] * EPS);
        ray.direction.set(-s[3], -s[4], -s[5]);
        const hit = bvh.raycastFirst(ray, THREE.BackSide);
        if (hit) ds.push(hit.distance + EPS);
      }
      if (ds.length) {
        ds.sort((a, b) => a - b);
        const mid = ds.length % 2 ? ds[(ds.length - 1) / 2] : (ds[ds.length / 2 - 1] + ds[ds.length / 2]) / 2;
        thickness = { min: Math.round(ds[0] * 100) / 100, median: Math.round(mid * 100) / 100 };
      }
    }
    return {
      faceCount: n,
      area: Math.round(area * 100) / 100,
      thickness,
      centroid: centroid.map(r),
      normal: [r(nx / nl), r(ny / nl), r(nz / nl)],
      bbox: { min: [x0, y0, z0].map(r), max: [x1, y1, z1].map(r) },
      samples,
    };
  }

  function openFacesPopover(mesh, list, fallback) {
    if (!list.length) { store.emit("popover:close"); return; }
    const summary = summarizeFaces(mesh, list);
    let x = fallback.x, y = fallback.y;
    const s = viewport.toScreen(summary.centroid);
    const rect = canvas.getBoundingClientRect();
    if (s.visible && s.x > rect.left && s.x < rect.right && s.y > rect.top && s.y < rect.bottom) { x = s.x; y = s.y; }
    store.emit("popover", { kind: "faces", x, y, file: mesh.userData.file, faceIds: list, summary });
  }

  // ---- 指示の重ね描き（faces / pin / measure）--------------------------------
  const itemVis = new Map();       // id -> { key, objs: [Object3D], handles: [label handle] }

  function removeVis(vis) {
    for (const o of vis.objs) disposeObj(o);
    for (const h of vis.handles) h.remove();
  }

  function lineBetween(a, b, color) {
    const g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a), new THREE.Vector3(...b)]);
    const l = new THREE.Line(g, new THREE.LineBasicMaterial({ color: new THREE.Color(color), depthTest: false, transparent: true }));
    l.renderOrder = 8;
    l.raycast = () => {};
    l.frustumCulled = false;
    return l;
  }
  function sphereAt(p, r, color, depthTest = true) {
    const m = new THREE.Mesh(
      new THREE.SphereGeometry(r, 16, 12),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(color), depthTest, transparent: !depthTest }),
    );
    m.position.set(p[0], p[1], p[2]);
    m.renderOrder = 8;
    m.raycast = () => {};
    return m;
  }

  function buildPin(it, index, active) {
    const u = unit();
    const n = it.normal || [0, 0, 1];
    const tip = addVec(it.point, n, u * 3);
    const objs = [lineBetween(it.point, tip, PIN_COLOR), sphereAt(tip, u * (active ? 1.3 : 1), PIN_COLOR)];
    for (const o of objs) group.add(o);
    const el = badge(String(index), { bg: PIN_COLOR, fg: "#1a1400", round: true });
    if (active) el.style.boxShadow = "0 0 0 2px #fff";
    return { objs, handles: [viewport.labels.add(el, tip)] };
  }

  function buildMeasure(it, active) {
    const u = unit();
    const mid = [(it.a[0] + it.b[0]) / 2, (it.a[1] + it.b[1]) / 2, (it.a[2] + it.b[2]) / 2];
    const d = it.distance != null ? it.distance : distance(it.a, it.b);
    const objs = [lineBetween(it.a, it.b, MEASURE_COLOR), sphereAt(it.a, u * 0.55, MEASURE_COLOR, false), sphereAt(it.b, u * 0.55, MEASURE_COLOR, false)];
    for (const o of objs) group.add(o);
    const el = badge(`${d.toFixed(1)} mm`, { bg: "rgba(21,24,28,.92)", fg: "#e6e8ea", mono: true });
    if (active) el.style.outline = "1px solid #fff";
    return { objs, handles: [viewport.labels.add(el, mid)] };
  }

  function syncItems() {
    const items = store.state.draft.items;
    const active = store.state.activeItemId;
    const alive = new Set();
    let pinNo = 0;
    for (const it of items) {
      if (it.type === "pin") pinNo++;
      if (it.type !== "faces" && it.type !== "pin" && it.type !== "measure") continue;
      alive.add(it.id);
      const isActive = it.id === active;
      let key, mesh = null;
      if (it.type === "faces") {
        mesh = meshByFile(it.file);
        key = [it.color, isActive, mesh && mesh.id, it.faceIds && it.faceIds.length, it.faceIds && it.faceIds[0], it.faceIds && it.faceIds[it.faceIds.length - 1]].join("|");
      } else if (it.type === "pin") {
        key = [pinNo, isActive, it.point.join(), (it.normal || []).join()].join("|");
      } else {
        key = [isActive, it.a.join(), it.b.join(), it.distance].join("|");
      }
      key += "|" + unit().toFixed(3);
      let vis = itemVis.get(it.id);
      if (vis && vis.key === key && vis.faceIds === it.faceIds) continue;
      if (vis) { removeVis(vis); itemVis.delete(it.id); }
      if (it.type === "faces") {
        if (!mesh || !Array.isArray(it.faceIds) || !it.faceIds.length) continue;
        const T = mesh.userData.triangles;
        if (it.faceIds.some((i) => i >= T)) continue;               // STL が作り直されて番号が合わない
        const o = trianglesMesh(mesh, it.faceIds, it.color, isActive ? 0.8 : 0.5);
        group.add(o);
        vis = { objs: [o], handles: [] };
      } else if (it.type === "pin") {
        vis = buildPin(it, pinNo, isActive);
      } else {
        vis = buildMeasure(it, isActive);
      }
      vis.key = key;
      vis.faceIds = it.faceIds;
      itemVis.set(it.id, vis);
    }
    for (const [id, vis] of itemVis) {
      if (!alive.has(id)) { removeVis(vis); itemVis.delete(id); }
    }
    viewport.invalidate();
  }

  // ---- ピン（仮置き）と計測（1 点目）-----------------------------------------
  let pendingPin = null;      // { objs, handles }
  function clearPendingPin() {
    if (!pendingPin) return;
    removeVis(pendingPin);
    pendingPin = null;
    viewport.invalidate();
  }
  function showPendingPin(point, normal) {
    clearPendingPin();
    const u = unit();
    const tip = addVec(point, normal, u * 3);
    const objs = [lineBetween(point, tip, PIN_COLOR), sphereAt(tip, u, PIN_COLOR)];
    for (const o of objs) group.add(o);
    const el = badge("+", { bg: PIN_COLOR, fg: "#1a1400", round: true });
    pendingPin = { objs, handles: [viewport.labels.add(el, tip)] };
    viewport.invalidate();
  }

  let measureA = null;        // { file, a }
  let rubber = null;          // { line, endA, endB, handle }
  function clearRubber() {
    if (rubber) {
      disposeObj(rubber.line); disposeObj(rubber.dotA); disposeObj(rubber.dotB);
      rubber.handle.remove();
      rubber = null;
    }
    measureA = null;
    viewport.invalidate();
  }
  function snapAxis(a, b) {
    const d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
    let k = 0;
    for (let i = 1; i < 3; i++) if (Math.abs(d[i]) > Math.abs(d[k])) k = i;
    const out = a.slice();
    out[k] = b[k];
    return out;
  }
  // ---- ポインタ ---------------------------------------------------------------
  let down = null;            // { id, x, y, moved, button, mode }
  let stroke = null;          // ブラシ中 { mesh, mask, mode, lastDraw }
  let busyClick = false;

  // 1 回分の塗り。前の位置から今の位置までを 8px 刻みでつないで、速く動かしても途切れないようにする
  function strokeAt(e) {
    const from = stroke.last || { x: e.clientX, y: e.clientY };
    const dist = Math.hypot(e.clientX - from.x, e.clientY - from.y);
    const steps = clamp(Math.ceil(dist / 8), 1, 60);
    let changed = false, lastHit = null;
    for (let i = 1; i <= steps; i++) {
      const x = from.x + ((e.clientX - from.x) * i) / steps;
      const y = from.y + ((e.clientY - from.y) * i) / steps;
      const hit = viewport.pick(x, y);
      if (!hit) continue;
      if (!stroke.mesh) {
        stroke.mesh = hit.mesh;
        const T = hit.mesh.userData.triangles;
        if (stroke.mode === "replace" || selMesh !== hit.mesh || !selMask) stroke.mask = new Uint8Array(T);
        else stroke.mask = selMask.slice();
      } else if (hit.mesh !== stroke.mesh) {
        continue;
      }
      if (dab(stroke.mesh, stroke.mask, hit.point, store.state.brushRadius, stroke.mode === "remove" ? 0 : 1)) changed = true;
      lastHit = hit;
    }
    stroke.last = { x: e.clientX, y: e.clientY };
    if (lastHit) updateRing(lastHit);
    const now = performance.now();
    if (changed && now - stroke.lastDraw > 60) {
      stroke.lastDraw = now;
      drawSelection(stroke.mesh, maskToList(stroke.mask));
    }
  }

  function onDown(e) {
    if (!toolActive() || e.button !== 0) return;
    down = { id: e.pointerId, x: e.clientX, y: e.clientY, moved: false, mode: modeOf(e) };
    if (store.state.tool === "faces" && store.state.faceMode === "brush") {
      e.stopImmediatePropagation();             // 視点回転を始めさせない
      viewport.setControlsEnabled(false);
      try { canvas.setPointerCapture(e.pointerId); } catch { /* 無くても動く */ }
      stroke = { mesh: null, mask: null, mode: down.mode, lastDraw: 0 };
      strokeAt(e);
    }
  }

  let hoverRaf = 0;
  function onMove(e) {
    if (!toolActive()) { updateRing(null); return; }
    if (down && down.id === e.pointerId && !down.moved) {
      if (Math.hypot(e.clientX - down.x, e.clientY - down.y) >= CLICK_PX) down.moved = true;
    }
    if (stroke) { strokeAt(e); return; }
    if (e.buttons) return;
    const tool = store.state.tool;
    if (tool === "measure" && measureA || (tool === "faces" && store.state.faceMode === "brush")) {
      if (hoverRaf) return;
      const shift = e.shiftKey, cx = e.clientX, cy = e.clientY;
      hoverRaf = requestAnimationFrame(() => {
        hoverRaf = 0;
        const hit = viewport.pick(cx, cy);
        if (tool === "measure" && measureA) {
          if (hit) updateRubberTo(shift ? snapAxis(measureA.a, hit.point) : hit.point);
        } else {
          updateRing(hit);
        }
      });
    }
  }

  function updateRubberTo(b) {
    const a = measureA.a;
    const u = unit();
    const text = `${distance(a, b).toFixed(1)} mm`;
    const mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2];
    if (!rubber) {
      rubber = {
        line: lineBetween(a, b, MEASURE_COLOR),
        dotA: sphereAt(a, u * 0.55, MEASURE_COLOR, false),
        dotB: sphereAt(b, u * 0.55, MEASURE_COLOR, false),
        el: badge(text, { bg: "rgba(21,24,28,.92)", fg: "#e6e8ea", mono: true }),
        handle: null,
      };
      rubber.handle = viewport.labels.add(rubber.el, mid);
      group.add(rubber.line); group.add(rubber.dotA); group.add(rubber.dotB);
    }
    const pos = rubber.line.geometry.attributes.position;
    pos.setXYZ(0, a[0], a[1], a[2]); pos.setXYZ(1, b[0], b[1], b[2]);
    pos.needsUpdate = true;
    rubber.dotB.position.set(b[0], b[1], b[2]);
    rubber.el.textContent = text;
    rubber.handle.setPos(mid);
    viewport.invalidate();
  }

  function onUp(e) {
    if (!down || down.id !== e.pointerId) return;
    const d = down;
    down = null;
    if (stroke) {
      const s = stroke;
      stroke = null;
      viewport.setControlsEnabled(true);
      try { canvas.releasePointerCapture(e.pointerId); } catch { /* 無くても動く */ }
      if (s.mesh && s.mask) {
        const list = setSelection(s.mesh, s.mask);
        openFacesPopover(s.mesh, list, { x: e.clientX, y: e.clientY });
      } else if (d.mode === "replace") {
        setSelection(null, null);
        store.emit("popover:close");
      }
      return;
    }
    if (d.moved) return;
    onClick(e, d.mode);
  }
  function onCancel(e) {
    if (down && down.id === e.pointerId) down = null;
    if (stroke) {
      stroke = null;
      viewport.setControlsEnabled(true);
      drawSelection(selMesh, selMask ? maskToList(selMask) : null);
    }
  }

  async function onClick(e, mode) {
    if (!toolActive()) return;
    const tool = store.state.tool;
    const hit = viewport.pick(e.clientX, e.clientY);

    if (tool === "faces") {
      if (!hit) {
        if (mode === "replace") {
          setSelection(null, null);
          store.emit("popover:close");
          store.status("選択を解除しました", "ok");
        }
        return;
      }
      if (busyClick) return;
      busyClick = true;
      try {
        const info = await ensureInfo(hit.mesh);
        if (!info) return;
        const ids = growRegion(info, hit.faceIndex, store.state.faceAngle);
        if (mode === "replace") lastSmart = { mesh: hit.mesh, seed: hit.faceIndex };
        const list = combine(hit.mesh, ids, mode);
        store.status(list.length ? `面 ${list.length.toLocaleString("ja-JP")} 枚を選択` : "選択を空にしました", "ok");
        openFacesPopover(hit.mesh, list, { x: e.clientX, y: e.clientY });
      } finally { busyClick = false; }
      return;
    }

    if (!hit) return;
    if (tool === "pin") {
      showPendingPin(hit.point, hit.normal);
      store.emit("popover", { kind: "pin", x: e.clientX, y: e.clientY, file: hit.file, point: hit.point, normal: hit.normal });
      return;
    }
    if (tool === "measure") {
      if (!measureA) {
        measureA = { file: hit.file, a: hit.point };
        updateRubberTo(hit.point);
        return;
      }
      const b = e.shiftKey ? snapAxis(measureA.a, hit.point) : hit.point;
      const a = measureA.a;
      const file = measureA.file;
      clearRubber();
      store.addItem({ type: "measure", file, a, b, distance: Math.round(distance(a, b) * 100) / 100 });
    }
  }

  canvas.addEventListener("pointerdown", onDown, true);
  canvas.addEventListener("pointermove", onMove);
  canvas.addEventListener("pointerup", onUp);
  canvas.addEventListener("pointercancel", onCancel);

  // ---- 購読 -------------------------------------------------------------------
  let cursorOwned = false;
  function updateCursor() {
    if (toolActive()) { canvas.style.cursor = "crosshair"; cursorOwned = true; }
    else if (cursorOwned) { canvas.style.cursor = ""; cursorOwned = false; }
  }

  function cancel() {
    clearRubber();
    clearPendingPin();
    updateRing(null);
  }

  let angleTimer = 0;
  const subs = [
    offSel,
    store.on("items", ({ reason, id }) => {
      if (reason === "add" && id) {
        const it = store.getItem(id);
        if (it && it.type === "pin") clearPendingPin();
      }
      syncItems();
    }),
    store.on("change:activeItemId", syncItems),
    store.on("popover:close", clearPendingPin),
    store.on("change:tool", () => {
      cancel();
      updateCursor();
      prefetch();
    }),
    store.on("change:frame", () => { cancel(); updateCursor(); }),
    store.on("change:faceMode", () => { updateRing(null); }),
    store.on("change:brushRadius", () => { if (ring && ring.visible) { ring.visible = false; viewport.invalidate(); } }),
    store.on("change:faceAngle", () => {
      if (!lastSmart || !selMask || store.state.tool !== "faces" || store.state.faceMode !== "smart") return;
      clearTimeout(angleTimer);
      angleTimer = setTimeout(async () => {
        if (!lastSmart || !viewport.getMeshes().includes(lastSmart.mesh)) return;
        const info = await ensureInfo(lastSmart.mesh);
        if (!info || !lastSmart) return;
        const ids = growRegion(info, lastSmart.seed, store.state.faceAngle);
        const mesh = lastSmart.mesh;
        const list = combine(mesh, ids, "replace");
        store.status(`面 ${list.length.toLocaleString("ja-JP")} 枚を選択（${store.state.faceAngle}°）`, "ok");
        openFacesPopover(mesh, list, { x: canvas.getBoundingClientRect().left + 40, y: canvas.getBoundingClientRect().top + 40 });
      }, 250);
    }),
    store.on("mesh:loaded", () => {
      // 形が入れ替わったので、番号が合わない選択・重ね描きは作り直す
      cancel();
      selMesh = null; selMask = null; lastSmart = null;
      if (store.state.selection.length) store.set({ selection: [], selectionFile: null });
      drawSelection(null, null);
      for (const vis of itemVis.values()) removeVis(vis);
      itemVis.clear();
      syncItems();
      prefetch();
    }),
    store.on("item:focus", ({ id }) => {
      const it = store.getItem(id);
      if (!it) return;
      if (it.type === "faces" && it.summary && it.summary.bbox) viewport.frameModelBox(it.summary.bbox);
      else if (it.type === "pin") {
        const u = unit() * 8;
        viewport.frameModelBox({ min: addVec(it.point, [1, 1, 1], -u), max: addVec(it.point, [1, 1, 1], u) });
      } else if (it.type === "measure") {
        const u = unit() * 4;
        viewport.frameModelBox({
          min: [Math.min(it.a[0], it.b[0]) - u, Math.min(it.a[1], it.b[1]) - u, Math.min(it.a[2], it.b[2]) - u],
          max: [Math.max(it.a[0], it.b[0]) + u, Math.max(it.a[1], it.b[1]) + u, Math.max(it.a[2], it.b[2]) + u],
        });
      }
    }),
  ];
  updateCursor();
  syncItems();

  function dispose() {
    for (const off of subs) off();
    clearTimeout(angleTimer);
    cancel();
    for (const vis of itemVis.values()) removeVis(vis);
    itemVis.clear();
    if (selObj) disposeObj(selObj);
    if (ring) disposeObj(ring);
    canvas.removeEventListener("pointerdown", onDown, true);
    canvas.removeEventListener("pointermove", onMove);
    canvas.removeEventListener("pointerup", onUp);
    canvas.removeEventListener("pointercancel", onCancel);
    if (cursorOwned) canvas.style.cursor = "";
    overlay.remove(group);
  }

  return { summarizeFaces, cancel, dispose };
}
