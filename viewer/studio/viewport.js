// 3D ビューポート。STL を表示し、カメラ・グリッド・視点ボタン・ラベルを持つ。
// 契約は CONTRACT.md §4。座標は frames.js の約束（モデル座標 = STL の生の値 × unitScale、通常 Blender mm・Z 上）。
//
// 契約に足したもの（このモジュールの内側で使う / picking・section が使う）:
//   invalidate()                 再描画を頼む（描画は要るときだけ）
//   clipMaterial(mat) / unclipMaterial(mat)   片側を隠す平面を、その材質にも効かせる
//   toScreen([x,y,z]) -> {x, y, visible}      画面の座標（client 座標）。ポップオーバーの位置用
//   size() -> {width, height}                 canvas の CSS 寸法
//   geomInfo(mesh, {smooth}) / hasGeomInfo(mesh)   Worker で作る溶接・隣接の情報（キャッシュ）
//   viewPreset は ["x","y","z"] の配列（視点→対象の向き、モデル座標）も受ける
//   dispose()

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";
import { computeBoundsTree, disposeBoundsTree, acceleratedRaycast } from "three-mesh-bvh";

THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;

const MM = 0.001;                 // モデル座標（mm）→ three（m）
const DEFAULT_COLOR = "#c9ced6";
const GHOST_COLOR = "#9db4ff";
const PLACED_RE = /print|plate|split/i;

// --- STL ----------------------------------------------------------------

// バイナリ / ASCII の STL を、非 index の位置（9 個 = 3 頂点 × xyz）に読む
export function parseSTL(buffer) {
  const bytes = new Uint8Array(buffer);
  if (bytes.length >= 84) {
    const dv = new DataView(buffer);
    const n = dv.getUint32(80, true);
    const head = String.fromCharCode(...bytes.subarray(0, 5));
    if (84 + n * 50 === bytes.length || (head !== "solid" && 84 + n * 50 <= bytes.length)) {
      const pos = new Float32Array(n * 9);
      for (let i = 0; i < n; i++) {
        const o = 84 + i * 50 + 12;
        const b = i * 9;
        pos[b] = dv.getFloat32(o, true); pos[b + 1] = dv.getFloat32(o + 4, true); pos[b + 2] = dv.getFloat32(o + 8, true);
        pos[b + 3] = dv.getFloat32(o + 12, true); pos[b + 4] = dv.getFloat32(o + 16, true); pos[b + 5] = dv.getFloat32(o + 20, true);
        pos[b + 6] = dv.getFloat32(o + 24, true); pos[b + 7] = dv.getFloat32(o + 28, true); pos[b + 8] = dv.getFloat32(o + 32, true);
      }
      return pos;
    }
  }
  const text = new TextDecoder().decode(bytes);
  const re = /vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)/g;
  const out = [];
  let m;
  while ((m = re.exec(text))) out.push(+m[1], +m[2], +m[3]);
  if (!out.length || out.length % 9) throw new Error("STL として読めません");
  return new Float32Array(out);
}

function boundsOf(pos) {
  let x0 = Infinity, y0 = Infinity, z0 = Infinity, x1 = -Infinity, y1 = -Infinity, z1 = -Infinity;
  for (let i = 0; i < pos.length; i += 3) {
    const x = pos[i], y = pos[i + 1], z = pos[i + 2];
    if (x < x0) x0 = x; if (x > x1) x1 = x;
    if (y < y0) y0 = y; if (y > y1) y1 = y;
    if (z < z0) z0 = z; if (z > z1) z1 = z;
  }
  return { min: [x0, y0, z0], max: [x1, y1, z1] };
}

// 単位の推定: bbox の最大寸法が 2 未満なら m とみなす（表示は 1000 倍して mm にそろえる）
function inferUnitScale(pos) {
  const b = boundsOf(pos);
  const dim = Math.max(b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]);
  return dim < 2 ? 1000 : 1;
}

// 次の描画を待つ。裏のタブでは requestAnimationFrame が止まるので、時間でも抜ける
const nextFrame = () => new Promise((r) => {
  const t = setTimeout(r, 120);
  requestAnimationFrame(() => { clearTimeout(t); r(); });
});
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));

function cssVar(el, name, fallback) {
  try {
    const v = getComputedStyle(el).getPropertyValue(name).trim();
    return v || fallback;
  } catch { return fallback; }
}

// 視点ボタンの見た目（styles.css とは独立に動くよう、ここで入れる）
const STYLE = `
.vp-views{position:absolute;top:10px;right:10px;display:grid;grid-template-columns:repeat(4,auto);gap:3px;padding:4px;
  background:var(--panel,#15181c);border:1px solid var(--line,#2a3038);border-radius:var(--radius,6px);z-index:5;user-select:none}
.vp-views button{font:inherit;font-size:12px;line-height:1;padding:6px 8px;min-width:34px;color:var(--text-2,#aab2bc);
  background:var(--raised,#1c2026);border:1px solid transparent;border-radius:var(--radius-sm,4px);cursor:pointer}
.vp-views button:hover{background:var(--hover,#232830);color:var(--text,#e6e8ea)}
.vp-views button:active{background:var(--accent,#7c9cff);color:var(--accent-ink,#0b1020)}
.vp-views button.wide{grid-column:span 2}
`;
function ensureStyle() {
  if (document.getElementById("vp-style")) return;
  const s = document.createElement("style");
  s.id = "vp-style";
  s.textContent = STYLE;
  document.head.appendChild(s);
}

const VIEWS = [
  ["front", "正面"], ["back", "背面"], ["left", "左"], ["right", "右"],
  ["top", "上"], ["bottom", "下"], ["iso", "斜め"],
];
// 視点 → 対象の向き（モデル座標。Blender の前面 = -Y 側から見る）
const VIEW_DIRS = {
  front: [0, -1, 0], back: [0, 1, 0], left: [-1, 0, 0], right: [1, 0, 0],
  top: [0, -0.001, 1], bottom: [0, -0.001, -1], iso: [0.55, -0.8, 0.5],
};

export function createViewport(container, store) {
  ensureStyle();
  if (getComputedStyle(container).position === "static") container.style.position = "relative";
  container.style.overflow = "hidden";

  const bgColor = cssVar(container, "--bg", "#0e1013");
  const lineColor = cssVar(container, "--line", "#2a3038");
  const lineStrong = cssVar(container, "--line-strong", "#3a424d");

  // --- renderer / scene / camera ---
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.localClippingEnabled = true;
  const canvas = renderer.domElement;
  canvas.style.display = "block";
  canvas.style.width = "100%";
  canvas.style.height = "100%";
  canvas.style.touchAction = "none";
  canvas.style.outline = "none";
  container.appendChild(canvas);

  const css2d = new CSS2DRenderer();
  Object.assign(css2d.domElement.style, { position: "absolute", top: "0", left: "0", pointerEvents: "none" });
  container.appendChild(css2d.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(bgColor);

  const camera = new THREE.PerspectiveCamera(40, 1, 0.001, 100);
  camera.position.set(0.2, 0.2, 0.3);

  // 灯りはカメラに付ける（どの向きから見ても暗くならない）
  scene.add(camera);
  camera.add(new THREE.AmbientLight(0xffffff, 0.9));
  const key = new THREE.DirectionalLight(0xffffff, 1.7);
  key.position.set(-1, 1.4, 1.2);
  camera.add(key);
  camera.add(key.target);
  key.target.position.set(0, 0, -1);
  const fill = new THREE.DirectionalLight(0xbfd0ff, 0.55);
  fill.position.set(1.2, -0.4, 0.8);
  camera.add(fill);
  camera.add(fill.target);
  fill.target.position.set(0, 0, -1);

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.12;
  controls.screenSpacePanning = true;
  controls.zoomToCursor = true;
  controls.mouseButtons = { LEFT: THREE.MOUSE.ROTATE, MIDDLE: THREE.MOUSE.PAN, RIGHT: THREE.MOUSE.PAN };

  const modelRoot = new THREE.Group();
  modelRoot.rotation.x = -Math.PI / 2;
  modelRoot.scale.setScalar(MM);
  scene.add(modelRoot);
  const overlay = new THREE.Group();
  overlay.name = "overlay";
  modelRoot.add(overlay);

  const gridGroup = new THREE.Group();
  scene.add(gridGroup);

  // --- 状態 ---
  let meshes = [];
  let ghost = null;
  let previewGroup = null;
  let previewBox = null;            // three（m）
  let viewerCfg = null;
  let clip = null;                  // モデル座標 {origin, normal}
  const clipArr = [];               // 材質が共有する平面の配列（0 または 1 個）
  const clipMaterials = new Set();
  let radiusWorld = 0.1;            // モデル全体を囲む球の半径（three の m）
  let dirty = true;
  let tween = null;
  let loadGen = 0;
  const frameCbs = new Set();
  const geomCache = new WeakMap();  // geometry -> { promise, result, smooth }

  const invalidate = () => { dirty = true; };
  controls.addEventListener("change", invalidate);
  controls.addEventListener("start", () => { tween = null; });

  // --- 大きさに追従 ---
  function resize() {
    const w = container.clientWidth, h = container.clientHeight;
    if (w < 2 || h < 2) return;
    renderer.setSize(w, h, false);
    css2d.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    invalidate();
  }
  const ro = new ResizeObserver(resize);
  ro.observe(container);
  resize();

  // --- 座標 ---
  const _v = new THREE.Vector3();
  const _inv = new THREE.Matrix4();
  function toModel(world) {
    modelRoot.updateMatrixWorld();
    _v.copy(world);
    modelRoot.worldToLocal(_v);
    return [_v.x, _v.y, _v.z];
  }
  function toWorld(p) {
    modelRoot.updateMatrixWorld();
    return modelRoot.localToWorld(new THREE.Vector3(p[0], p[1], p[2]));
  }
  function dirToModel(worldDir) {
    modelRoot.updateMatrixWorld();
    _inv.copy(modelRoot.matrixWorld).invert();
    const d = worldDir.clone().transformDirection(_inv);
    return [d.x, d.y, d.z];
  }
  function dirToWorld(p) {
    modelRoot.updateMatrixWorld();
    return new THREE.Vector3(p[0], p[1], p[2]).transformDirection(modelRoot.matrixWorld);
  }

  function modelBox() {
    if (previewGroup && previewBox) {
      return {
        min: [previewBox.min.x / MM, previewBox.min.y / MM, previewBox.min.z / MM],
        max: [previewBox.max.x / MM, previewBox.max.y / MM, previewBox.max.z / MM],
      };
    }
    if (!meshes.length) return { min: [0, 0, 0], max: [0, 0, 0] };
    const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
    for (const m of meshes) {
      const b = m.userData.bbox;
      for (let k = 0; k < 3; k++) {
        if (b.min[k] < min[k]) min[k] = b.min[k];
        if (b.max[k] > max[k]) max[k] = b.max[k];
      }
    }
    return { min, max };
  }

  // --- グリッド（mm 目盛り）---
  function rebuildGrid(maxDimMm) {
    for (const c of [...gridGroup.children]) {
      gridGroup.remove(c);
      c.geometry.dispose();
      c.material.dispose();
    }
    const dim = Math.max(maxDimMm, 1);
    const step = dim < 60 ? 1 : dim < 600 ? 10 : 100;      // 細かい線の間隔（mm）
    const major = step * 10;
    const sizeMm = Math.max(Math.ceil((dim * 2.2) / major) * major, major * 2);
    const make = (divisions, color, opacity) => {
      const g = new THREE.GridHelper(sizeMm * MM, divisions, color, color);
      g.material.transparent = true;
      g.material.opacity = opacity;
      g.material.depthWrite = false;
      g.position.y = -dim * MM * 0.0005;
      return g;
    };
    gridGroup.add(make(sizeMm / step, lineColor, 0.9));
    gridGroup.add(make(sizeMm / major, lineStrong, 1));
    gridGroup.userData = { step, major, sizeMm };
  }

  // --- 配置: モデルの底面が y=0、水平中心が原点 ---
  function updatePlacement() {
    if (previewGroup) {
      modelRoot.visible = false;
      return;
    }
    modelRoot.visible = true;
    if (!meshes.length) { modelRoot.position.set(0, 0, 0); modelRoot.updateMatrixWorld(true); return; }
    const b = modelBox();
    const cx = (b.min[0] + b.max[0]) / 2, cy = (b.min[1] + b.max[1]) / 2;
    modelRoot.position.set(-cx * MM, -b.min[2] * MM, cy * MM);
    modelRoot.updateMatrixWorld(true);
  }

  function updateScale() {
    const b = modelBox();
    const dx = (b.max[0] - b.min[0]) * MM, dy = (b.max[1] - b.min[1]) * MM, dz = (b.max[2] - b.min[2]) * MM;
    radiusWorld = Math.max(Math.hypot(dx, dy, dz) / 2, 0.005);
    controls.minDistance = radiusWorld * 0.02;
    controls.maxDistance = radiusWorld * 40;
    rebuildGrid(Math.max(dx, dy, dz) / MM);
    applyClip();
  }

  function worldCenter() {
    const b = modelBox();
    return toWorld([(b.min[0] + b.max[0]) / 2, (b.min[1] + b.max[1]) / 2, (b.min[2] + b.max[2]) / 2]);
  }

  // --- カメラ ---
  function fitDistance(radius) {
    const vfov = THREE.MathUtils.degToRad(camera.fov);
    const hfov = 2 * Math.atan(Math.tan(vfov / 2) * Math.max(camera.aspect, 0.2));
    return (radius / Math.sin(Math.min(vfov, hfov) / 2)) * 1.08;
  }

  function placeCamera(targetWorld, dirWorld, dist, animate = true) {
    const dir = dirWorld.clone().normalize();
    const pos = targetWorld.clone().add(dir.multiplyScalar(dist));
    if (!animate) {
      camera.position.copy(pos);
      controls.target.copy(targetWorld);
      controls.update();
      tween = null;
      invalidate();
      return;
    }
    const t0v = controls.target.clone();
    const off0 = camera.position.clone().sub(t0v);
    const len0 = off0.length() || 1;
    const dir0 = off0.clone().divideScalar(len0);
    const off1 = pos.clone().sub(targetWorld);
    const len1 = off1.length();
    const dir1 = off1.clone().divideScalar(len1 || 1);
    tween = {
      start: performance.now(), ms: 240, t0: t0v, t1: targetWorld.clone(),
      dir0, len0, dir1, len1,
      q: new THREE.Quaternion().setFromUnitVectors(dir0, dir1),
    };
    invalidate();
  }
  function stepTween(now) {
    const k = clamp((now - tween.start) / tween.ms, 0, 1);
    const e = 1 - Math.pow(1 - k, 3);
    const q = new THREE.Quaternion().slerp(tween.q, e);
    const dir = tween.dir0.clone().applyQuaternion(q);
    const len = tween.len0 + (tween.len1 - tween.len0) * e;
    const target = tween.t0.clone().lerp(tween.t1, e);
    camera.position.copy(target).add(dir.multiplyScalar(len));
    controls.target.copy(target);
    controls.update();
    if (k >= 1) tween = null;
    invalidate();
  }

  function viewPreset(nameOrDir) {
    const d = Array.isArray(nameOrDir) ? nameOrDir : VIEW_DIRS[nameOrDir];
    if (!d) return;
    const dirWorld = dirToWorld(d);
    placeCamera(worldCenter(), dirWorld, fitDistance(radiusWorld));
  }

  function frameModelBox(box) {
    const min = box.min, max = box.max;
    const c = toWorld([(min[0] + max[0]) / 2, (min[1] + max[1]) / 2, (min[2] + max[2]) / 2]);
    const r = Math.max(Math.hypot(max[0] - min[0], max[1] - min[1], max[2] - min[2]) * MM / 2, radiusWorld * 0.03);
    const dir = camera.position.clone().sub(controls.target);
    if (dir.lengthSq() < 1e-12) dir.set(0.5, 0.5, 1);
    placeCamera(c, dir, Math.min(fitDistance(r * 1.25), radiusWorld * 30));
  }

  // 取り込み直後の視点。viewer.json の camera があれば従う
  function fit() {
    const cam = viewerCfg && viewerCfg.camera;
    if (cam && cam.fov) { camera.fov = cam.fov; camera.updateProjectionMatrix(); }
    const b = modelBox();
    const maxDim = Math.max(b.max[0] - b.min[0], b.max[1] - b.min[1], b.max[2] - b.min[2]) * MM;
    let dir = [0.55, -0.8, 0.5], dist = fitDistance(radiusWorld);
    if (cam && typeof cam.azimuth === "number" && typeof cam.elevation === "number") {
      const az = THREE.MathUtils.degToRad(cam.azimuth), el = THREE.MathUtils.degToRad(cam.elevation);
      dir = [Math.cos(el) * Math.cos(az), Math.cos(el) * Math.sin(az), Math.sin(el)];
      if (cam.distance) dist = cam.distance * maxDim;
    }
    placeCamera(worldCenter(), dirToWorld(dir), dist, false);
  }

  // --- 描画に使う値 ---
  function updateNearFar() {
    const d = camera.position.distanceTo(controls.target);
    const R = radiusWorld;
    camera.near = Math.max(R * 0.002, (d - R * 1.2) * 0.5);
    camera.far = Math.max(d + R * 4, R * 10);
    camera.updateProjectionMatrix();
  }

  function render(now) {
    if (tween) stepTween(now);
    if (controls.update()) dirty = true;
    if (!dirty) return;
    dirty = false;
    const w = container.clientWidth, h = container.clientHeight;
    if (w < 2 || h < 2) return;
    updateNearFar();
    renderer.render(scene, camera);
    css2d.render(scene, camera);
    for (const fn of frameCbs) {
      try { fn(); } catch (e) { console.error("[viewport] onFrame", e); }
    }
  }
  let raf = 0;
  const loop = (now) => { raf = requestAnimationFrame(loop); render(now); };
  raf = requestAnimationFrame(loop);

  function onFrame(fn) {
    frameCbs.add(fn);
    return () => frameCbs.delete(fn);
  }

  // --- 材質 ---
  function cfgMaterial() {
    const m = (viewerCfg && viewerCfg.material) || {};
    return {
      color: m.color != null ? m.color : DEFAULT_COLOR,
      roughness: m.roughness != null ? m.roughness : 0.65,
      metalness: m.metalness != null ? m.metalness : 0.0,
    };
  }
  function makeMaterial() {
    const c = cfgMaterial();
    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(c.color), roughness: c.roughness, metalness: c.metalness,
      flatShading: true, side: THREE.FrontSide,
    });
    mat.clippingPlanes = clipArr;
    clipMaterials.add(mat);
    return mat;
  }

  // --- 片側を隠す ---
  function applyClip() {
    const was = clipArr.length;
    clipArr.length = 0;
    if (clip) {
      const n = dirToWorld(clip.normal).negate();                // normal 側を隠す = 反対側を残す
      const plane = new THREE.Plane().setFromNormalAndCoplanarPoint(n, toWorld(clip.origin));
      clipArr.push(plane);
    }
    if (was !== clipArr.length) {
      for (const mat of clipMaterials) mat.needsUpdate = true;     // 平面の数が変わると shader を作り直す
    }
    // 切り口から中が見えるよう、隠している間は裏面も描く
    const side = clip ? THREE.DoubleSide : THREE.FrontSide;
    for (const m of meshes) {
      if (m.material.side !== side) { m.material.side = side; m.material.needsUpdate = true; }
    }
    invalidate();
  }
  function setClipPlane(p) {
    clip = p ? { origin: p.origin.slice(), normal: p.normal.slice() } : null;
    applyClip();
  }
  function clipMaterial(mat) {
    clipMaterials.add(mat);
    mat.clippingPlanes = clipArr;
    mat.needsUpdate = true;
  }
  function unclipMaterial(mat) {
    clipMaterials.delete(mat);
    mat.clippingPlanes = null;
  }

  // --- Worker（溶接・隣接）---
  let worker = null;
  let workerSeq = 0;
  const pending = new Map();
  function getWorker() {
    if (worker) return worker;
    worker = new Worker(new URL("./geom.worker.js", import.meta.url));
    worker.onmessage = (ev) => {
      const p = pending.get(ev.data.id);
      if (!p) return;
      pending.delete(ev.data.id);
      if (ev.data.ok) p.resolve(ev.data); else p.reject(new Error(ev.data.error || "geom worker"));
    };
    worker.onerror = (ev) => {
      console.error("[viewport] geom worker", ev);
      for (const p of pending.values()) p.reject(new Error("geom worker が止まりました"));
      pending.clear();
      worker = null;
    };
    return worker;
  }
  function runWorker(positions, smooth) {
    const id = ++workerSeq;
    return new Promise((resolve, reject) => {
      pending.set(id, { resolve, reject });
      const copy = positions.slice();      // transfer すると元が空になるので複製を渡す
      getWorker().postMessage({ id, positions: copy, smooth }, [copy.buffer]);
    });
  }
  function hasGeomInfo(mesh) {
    const c = geomCache.get(mesh.geometry);
    return !!(c && c.result);
  }
  function geomInfo(mesh, { smooth = false } = {}) {
    const g = mesh.geometry;
    const c = geomCache.get(g);
    if (c && (!smooth || c.smooth)) return c.promise;
    const entry = { smooth, result: null, promise: null };
    entry.promise = runWorker(g.attributes.position.array, smooth).then((r) => { entry.result = r; return r; });
    entry.promise.catch(() => { if (geomCache.get(g) === entry) geomCache.delete(g); });
    geomCache.set(g, entry);
    return entry.promise;
  }

  // --- 滑らかな法線（viewer.json の smoothNormals）---
  async function applySmooth(mesh, on) {
    const g = mesh.geometry, mat = mesh.material;
    if (on) {
      const r = await geomInfo(mesh, { smooth: true });
      if (!meshes.includes(mesh) || !r.cornerNormals) return;
      g.setAttribute("normal", new THREE.BufferAttribute(r.cornerNormals, 3));
      mat.flatShading = false;
    } else {
      g.deleteAttribute("normal");
      mat.flatShading = true;
    }
    mat.needsUpdate = true;
    invalidate();
  }

  // --- メッシュ ---
  function buildMesh(name, positions, unitScale, material) {
    if (unitScale !== 1) {
      const scaled = new Float32Array(positions.length);
      for (let i = 0; i < positions.length; i++) scaled[i] = positions[i] * unitScale;
      positions = scaled;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    g.computeBoundingBox();
    g.computeBoundingSphere();
    const mesh = new THREE.Mesh(g, material);
    const bb = g.boundingBox;
    mesh.userData = {
      file: name, unitScale,
      bbox: { min: [bb.min.x, bb.min.y, bb.min.z], max: [bb.max.x, bb.max.y, bb.max.z] },
      placed: PLACED_RE.test(name),
      triangles: positions.length / 9,
    };
    mesh.name = name;
    return mesh;
  }

  function disposeMesh(mesh) {
    mesh.geometry.disposeBoundsTree && mesh.geometry.disposeBoundsTree();
    mesh.geometry.dispose();
    if (mesh.material) { clipMaterials.delete(mesh.material); mesh.material.dispose(); }
    modelRoot.remove(mesh);
  }
  function clearMeshes() {
    for (const m of meshes) disposeMesh(m);
    meshes = [];
  }
  function clearPreview() {
    if (!previewGroup) return;
    scene.remove(previewGroup);
    previewGroup = null;
    previewBox = null;
  }

  async function fetchSTL(url) {
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.arrayBuffer();
  }

  async function loadSTLs(files, { fit: doFit = false } = {}) {
    const gen = ++loadGen;
    if (!files.length) {                               // 空 = 表示を空にする
      clearPreview();
      clearMeshes();
      updatePlacement();
      updateScale();
      invalidate();
      store.emit("mesh:loaded", { meshes: [], frame: store.state.frame });
      return [];
    }
    const t0 = performance.now();
    store.status(`読み込み中 ${files.map((f) => f.name).join(", ")} …`, "busy");
    const loaded = [];
    for (const f of files) {
      try {
        const buf = await fetchSTL(f.url);
        if (gen !== loadGen) return [];
        const pos = parseSTL(buf);
        loaded.push({ name: f.name, pos, unitScale: inferUnitScale(pos) });
      } catch (e) {
        console.error(`[viewport] ${f.name}`, e);
        store.status(`${f.name} を読めませんでした: ${e.message}`, "err");
      }
    }
    if (gen !== loadGen) return [];
    if (!loaded.length && files.length) return [];

    clearPreview();
    clearMeshes();
    for (const l of loaded) {
      const mesh = buildMesh(l.name, l.pos, l.unitScale, makeMaterial());
      meshes.push(mesh);
      modelRoot.add(mesh);
    }
    store.set({ frame: "blender-mm" });
    updatePlacement();
    updateScale();
    if (doFit) fit();
    invalidate();

    // 形を先に 1 フレーム出してから、重い索引（BVH）を作る
    await nextFrame();
    if (gen !== loadGen) return [];
    for (const m of meshes) {
      m.geometry.computeBoundsTree({ indirect: true });
    }
    if (viewerCfg && viewerCfg.smoothNormals) {
      try { await Promise.all(meshes.map((m) => applySmooth(m, true))); } catch (e) { console.error("[viewport] smooth", e); }
    }
    if (gen !== loadGen) return [];

    const tris = meshes.reduce((s, m) => s + m.userData.triangles, 0);
    const sec = ((performance.now() - t0) / 1000).toFixed(1);
    const notes = [];
    if (meshes.some((m) => m.userData.unitScale !== 1)) notes.push("m 単位とみなして 1000 倍");
    store.status(`${tris.toLocaleString("ja-JP")} 三角形 · ${sec} 秒${notes.length ? " · " + notes.join(" · ") : ""}`, "ok");
    store.emit("mesh:loaded", { meshes: meshes.slice(), frame: "blender-mm" });
    return meshes.slice();
  }

  // preview モジュール（three の m・Y 上）を置く
  function setPreviewGroup(group, { fit: doFit = false } = {}) {
    loadGen++;
    clearMeshes();
    clearPreview();
    if (ghost) setGhost(null);
    previewGroup = group;
    scene.add(group);
    group.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(group);
    group.position.y -= box.min.y;
    group.position.x -= (box.min.x + box.max.x) / 2;
    group.position.z -= (box.min.z + box.max.z) / 2;
    group.updateMatrixWorld(true);
    previewBox = new THREE.Box3().setFromObject(group);
    store.set({ frame: "preview-m-yup" });
    updatePlacement();
    updateScale();
    if (doFit) {
      const c = previewBox.getCenter(new THREE.Vector3());
      const dir = new THREE.Vector3(0.55, 0.5, 0.8);
      placeCamera(c, dir, fitDistance(radiusWorld), false);
    }
    invalidate();
    store.emit("mesh:loaded", { meshes: [], frame: "preview-m-yup" });
  }

  // --- ゴースト（比較用）---
  let ghostGen = 0;
  async function setGhost(url) {
    const gen = ++ghostGen;
    if (ghost) {
      for (const c of [...ghost.children]) { c.geometry && c.geometry.dispose(); c.material && c.material.dispose(); }
      ghost.geometry.disposeBoundsTree && ghost.geometry.disposeBoundsTree();
      ghost.geometry.dispose();
      clipMaterials.delete(ghost.material);
      ghost.material.dispose();
      modelRoot.remove(ghost);
      ghost = null;
    }
    if (!url) {
      invalidate();
      store.emit("ghost:loaded", { geometry: null });
      return;
    }
    if (previewGroup) {
      store.toast("プレビュー表示中は重ねて比べられません。STL 表示に切り替えてください");
      store.emit("ghost:loaded", { geometry: null });
      return;
    }
    const t0 = performance.now();
    store.status("比較用の形を読み込み中 …", "busy");
    try {
      const buf = await fetchSTL(url);
      if (gen !== ghostGen) return;
      const pos = parseSTL(buf);
      const mat = new THREE.MeshStandardMaterial({
        color: new THREE.Color(GHOST_COLOR), roughness: 0.8, metalness: 0, flatShading: true,
        transparent: true, opacity: 0.25, depthWrite: false, side: THREE.DoubleSide,
      });
      mat.clippingPlanes = clipArr;
      clipMaterials.add(mat);
      const mesh = buildMesh("ghost", pos, inferUnitScale(pos), mat);
      mesh.renderOrder = 1;
      mesh.raycast = () => {};                       // ゴーストは拾わない
      // 輪郭の稜線（少なめ）。三角形が多いと作るのに時間がかかるので小さい形だけ
      if (mesh.userData.triangles <= 150000) {
        const edges = new THREE.LineSegments(
          new THREE.EdgesGeometry(mesh.geometry, 35),
          new THREE.LineBasicMaterial({ color: new THREE.Color(GHOST_COLOR), transparent: true, opacity: 0.35, depthWrite: false }),
        );
        edges.raycast = () => {};
        mesh.add(edges);
      }
      modelRoot.add(mesh);
      ghost = mesh;
      await nextFrame();
      if (gen !== ghostGen) return;
      mesh.geometry.computeBoundsTree({ indirect: true });
      invalidate();
      store.status(`比較用の形: ${mesh.userData.triangles.toLocaleString("ja-JP")} 三角形 · ${((performance.now() - t0) / 1000).toFixed(1)} 秒`, "ok");
      store.emit("ghost:loaded", { geometry: mesh.geometry });
    } catch (e) {
      console.error("[viewport] ghost", e);
      store.status(`比較用の形を読めませんでした: ${e.message}`, "err");
      store.emit("ghost:loaded", { geometry: null });
    }
  }
  const getGhostGeometry = () => (ghost ? ghost.geometry : null);

  // --- ピック ---
  const raycaster = new THREE.Raycaster();
  const _ndc = new THREE.Vector2();
  function faceNormal(mesh, faceIndex) {
    const p = mesh.geometry.attributes.position.array;
    const b = faceIndex * 9;
    const e1x = p[b + 3] - p[b], e1y = p[b + 4] - p[b + 1], e1z = p[b + 5] - p[b + 2];
    const e2x = p[b + 6] - p[b], e2y = p[b + 7] - p[b + 1], e2z = p[b + 8] - p[b + 2];
    const x = e1y * e2z - e1z * e2y, y = e1z * e2x - e1x * e2z, z = e1x * e2y - e1y * e2x;
    const l = Math.hypot(x, y, z) || 1;
    return [x / l, y / l, z / l];
  }
  function pick(clientX, clientY) {
    if (!meshes.length) return null;
    const rect = canvas.getBoundingClientRect();
    if (rect.width < 1 || rect.height < 1) return null;
    _ndc.set(((clientX - rect.left) / rect.width) * 2 - 1, -((clientY - rect.top) / rect.height) * 2 + 1);
    camera.updateMatrixWorld();
    raycaster.setFromCamera(_ndc, camera);
    raycaster.firstHitOnly = !clip;
    const hits = raycaster.intersectObjects(meshes, false);
    for (const h of hits) {
      const p = toModel(h.point);
      if (clip) {
        const d = (p[0] - clip.origin[0]) * clip.normal[0] + (p[1] - clip.origin[1]) * clip.normal[1] + (p[2] - clip.origin[2]) * clip.normal[2];
        if (d > 1e-6) continue;                         // 隠れている側
      }
      return {
        mesh: h.object, file: h.object.userData.file, faceIndex: h.faceIndex,
        point: p, normal: faceNormal(h.object, h.faceIndex),
      };
    }
    return null;
  }

  function toScreen(p) {
    const w = toWorld(p).project(camera);
    const rect = canvas.getBoundingClientRect();
    return {
      x: rect.left + (w.x * 0.5 + 0.5) * rect.width,
      y: rect.top + (-w.y * 0.5 + 0.5) * rect.height,
      visible: w.z > -1 && w.z < 1,
    };
  }

  function cameraInfo() {
    camera.updateMatrixWorld();
    const up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
    return {
      position: toModel(camera.position),
      target: toModel(controls.target),
      up: dirToModel(up),
      fov: camera.fov,
    };
  }
  function cameraAxes() {
    camera.updateMatrixWorld();
    const right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0);
    const up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
    const back = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 2);
    return { right: dirToModel(right), up: dirToModel(up), forward: dirToModel(back.negate()) };
  }

  // --- ラベル（CSS2D）---
  const labels = {
    add(el, pos) {
      el.style.pointerEvents = "none";
      const obj = new CSS2DObject(el);
      obj.position.set(pos[0], pos[1], pos[2]);
      overlay.add(obj);
      invalidate();
      return {
        setPos(p) { obj.position.set(p[0], p[1], p[2]); invalidate(); },
        remove() { overlay.remove(obj); el.remove(); invalidate(); },
      };
    },
  };

  // --- スクリーンショット ---
  // 依頼に付ける 3D 画像は、モデル（と指示の重ね描き）が写っている範囲に切り詰める。
  // 画面いっぱいの床や余白を送っても読みにくいだけなので。
  function cropToModel(W, H) {
    const b = modelBox();
    if (!isFinite(b.min[0]) || b.max[0] - b.min[0] <= 0) return null;
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (let i = 0; i < 8; i++) {
      const p = toWorld([i & 1 ? b.max[0] : b.min[0], i & 2 ? b.max[1] : b.min[1], i & 4 ? b.max[2] : b.min[2]]);
      p.project(camera);
      if (p.z > 1) return null; // 箱の一部がカメラの後ろ。切らずにそのまま送る
      const sx = (p.x * 0.5 + 0.5) * W, sy = (1 - (p.y * 0.5 + 0.5)) * H;
      x0 = Math.min(x0, sx); x1 = Math.max(x1, sx); y0 = Math.min(y0, sy); y1 = Math.max(y1, sy);
    }
    const m = 0.12 * Math.max(x1 - x0, y1 - y0, 200);
    x0 = Math.max(0, Math.floor(x0 - m)); y0 = Math.max(0, Math.floor(y0 - m));
    x1 = Math.min(W, Math.ceil(x1 + m)); y1 = Math.min(H, Math.ceil(y1 + m));
    const w = x1 - x0, h = y1 - y0;
    if (w < 64 || h < 64 || (w >= W * 0.9 && h >= H * 0.9)) return null;
    const c2 = document.createElement("canvas");
    c2.width = w; c2.height = h;
    const g = c2.getContext("2d");
    g.drawImage(canvas, x0, y0, w, h, 0, 0, w, h);
    drawLabels(g, W, H, x0, y0);
    return c2.toDataURL("image/png");
  }

  // ピン番号・計測値などの HTML ラベルは WebGL の絵に入らないので、画像へ描き足す
  function drawLabels(g, W, H, ox, oy) {
    const fs = Math.max(14, Math.round(W / 70));
    g.font = `600 ${fs}px ui-monospace, Consolas, monospace`;
    g.textBaseline = "middle";
    overlay.traverse((o) => {
      if (!o.isCSS2DObject || !o.visible) return;
      const text = (o.element.textContent || "").trim();
      if (!text) return;
      const p = o.getWorldPosition(new THREE.Vector3()).project(camera);
      if (p.z > 1) return;
      const x = (p.x * 0.5 + 0.5) * W - ox, y = (1 - (p.y * 0.5 + 0.5)) * H - oy;
      const tw = g.measureText(text).width, pad = fs * 0.4;
      g.fillStyle = "rgba(14,16,19,0.85)";
      g.fillRect(x + fs * 0.6, y - fs * 0.75, tw + pad * 2, fs * 1.5);
      g.fillStyle = "#e6e8ea";
      g.fillText(text, x + fs * 0.6 + pad, y);
    });
  }

  function screenshot({ width = 1600 } = {}) {
    const cw = container.clientWidth, ch = container.clientHeight;
    if (cw < 2 || ch < 2) return null;
    const W = Math.round(width), H = Math.max(1, Math.round((width * ch) / cw));
    const pr = renderer.getPixelRatio();
    renderer.setPixelRatio(1);
    renderer.setSize(W, H, false);
    updateNearFar();
    renderer.render(scene, camera);
    const url = cropToModel(W, H) || canvas.toDataURL("image/png");
    renderer.setPixelRatio(pr);
    renderer.setSize(cw, ch, false);
    invalidate();
    return url;
  }

  // --- viewer.json ---
  function applyViewerConfig(cfg) {
    const prev = viewerCfg;
    viewerCfg = cfg || null;
    const c = cfgMaterial();
    for (const m of meshes) {
      m.material.color.set(c.color);
      m.material.roughness = c.roughness;
      m.material.metalness = c.metalness;
    }
    if (viewerCfg && viewerCfg.camera && viewerCfg.camera.fov) {
      camera.fov = viewerCfg.camera.fov;
      camera.updateProjectionMatrix();
    }
    const wasSmooth = !!(prev && prev.smoothNormals), isSmooth = !!(viewerCfg && viewerCfg.smoothNormals);
    if (meshes.length && wasSmooth !== isSmooth) {
      Promise.all(meshes.map((m) => applySmooth(m, isSmooth)))
        .catch((e) => console.error("[viewport] smooth", e));
    }
    invalidate();
  }

  // --- 視点ボタン ---
  const views = document.createElement("div");
  views.className = "vp-views";
  for (const [id, label] of VIEWS) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = label;
    b.title = `${label}から見る`;
    if (id === "iso") b.classList.add("wide");
    b.addEventListener("click", () => viewPreset(id));
    views.appendChild(b);
  }
  container.appendChild(views);

  // --- カーソル下の座標（80ms 間引き）---
  let lastPointer = 0, pointerWasOn = false;
  const onMove = (e) => {
    if (e.buttons) return;
    const now = performance.now();
    if (now - lastPointer < 80) return;
    lastPointer = now;
    const hit = pick(e.clientX, e.clientY);
    pointerWasOn = !!hit;
    store.emit("viewport:pointer", { point: hit ? hit.point : null });
  };
  const onLeave = () => {
    if (pointerWasOn) { pointerWasOn = false; store.emit("viewport:pointer", { point: null }); }
  };
  canvas.addEventListener("pointermove", onMove);
  canvas.addEventListener("pointerleave", onLeave);

  // 断面などで平面の向きが変わったら、片側を隠す平面もモデルの動きに合わせ直す
  const offMesh = store.on("mesh:loaded", () => applyClip());

  function dispose() {
    cancelAnimationFrame(raf);
    ro.disconnect();
    offMesh();
    canvas.removeEventListener("pointermove", onMove);
    canvas.removeEventListener("pointerleave", onLeave);
    clearMeshes();
    clearPreview();
    controls.dispose();
    renderer.dispose();
    if (worker) worker.terminate();
    views.remove();
    canvas.remove();
    css2d.domElement.remove();
  }

  return {
    THREE, renderer, scene, camera, controls, canvas, modelRoot, overlay, labels,
    loadSTLs, setPreviewGroup,
    getMeshes: () => meshes,
    setGhost, getGhostGeometry,
    pick, toModel, toWorld, modelBox,
    viewPreset, frameModelBox, cameraInfo, cameraAxes,
    setClipPlane,
    setControlsEnabled: (on) => { controls.enabled = !!on; },
    onFrame, screenshot, applyViewerConfig,
    // 足したもの
    invalidate, clipMaterial, unclipMaterial, toScreen,
    size: () => ({ width: container.clientWidth, height: container.clientHeight }),
    geomInfo, hasGeomInfo, dispose,
  };
}
