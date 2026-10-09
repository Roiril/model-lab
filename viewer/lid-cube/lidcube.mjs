// サーボ 1 個と 4 節リンクで蓋を開くモデル（開閉キューブ・住人の箱）の物理検証・組み立て画面で共有する部品。
// データ: assets/<モデル名>.json（models/<モデル名>/export_web.py が書く）。外部ライブラリは使わず WebGL2 で描く。
// どのモデルを開くかは URL の ?model= で決める。
import { themePalette, watchTheme } from "../shared/workspace.mjs";

export const MODEL = (typeof location !== "undefined" && new URLSearchParams(location.search).get("model")) || "servo-lid-cube";
const R = Math.PI / 180;

export async function loadData() {
  if (!/^[a-z0-9-]+$/.test(MODEL)) throw new Error(`モデル名が不正です（${MODEL}）`);
  const res = await fetch(`assets/${MODEL}.json`);
  if (!res.ok) throw new Error(`assets/${MODEL}.json を読めません（${res.status}）`);
  const D = await res.json();
  applyMeta(D.meta);
  return D;
}

// 見出し・タブの題をモデルのデータから入れる
function applyMeta(meta) {
  if (!meta || typeof document === "undefined") return;
  const page = document.body.dataset.page === "assembly" ? "組み立て" : "物理検証";
  document.title = `${meta.title}の${page} · model-lab`;
  const head = document.querySelector(".workspace-model");
  if (head) {
    head.querySelector("strong").textContent = meta.title;
    head.querySelector("small").textContent = meta.summary;
  }
  const brand = document.querySelector(".workspace-brand");
  if (brand) brand.href = `/?model=${encodeURIComponent(MODEL)}`;
}

// 部品の色は Okabe-Ito（部品の区別。テーマに依らず同じ色）。データに無い部品は表示しない
export const PARTS = [
  ["box", "箱", "#bdb4a6"], ["lid", "蓋", "#56b4e9"], ["crank", "クランク", "#e69f00"], ["link", "リンク", "#009e73"],
  ["pin", "蝶番ピン", "#4d4d4d"], ["clip", "押さえクリップ", "#cc79a7"], ["ref_body", "SG92R", "#0072b2"],
  ["ref_horn", "付属ホーン", "#2a2a2a"], ["ref_wire", "配線", "#d55e00"], ["ref_speaker", "スピーカー（参考）", "#f0e442"],
];
export const ALL = new Set(PARTS.map((p) => p[0]));
export const partsIn = (D) => PARTS.filter(([k]) => D.meshes[k]);

/* ---------- 行列（列優先） ---------- */
export const I4 = () => new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
export function mul(a, b) {
  const o = new Float32Array(16);
  for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) {
    let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k]; o[c * 4 + r] = s;
  }
  return o;
}
export const T = (x, y, z) => { const m = I4(); m[12] = x; m[13] = y; m[14] = z; return m; };
export function RX(deg, cy, cz) {
  const c = Math.cos(deg * R), s = Math.sin(deg * R);
  return mul(T(0, cy, cz), mul(new Float32Array([1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, 0, 0, 1]), T(0, -cy, -cz)));
}
export function RA(ax, deg, p) {
  const c = Math.cos(deg * R), s = Math.sin(deg * R), t = 1 - c, [x, y, z] = ax;
  const r = new Float32Array([t * x * x + c, t * x * y + s * z, t * x * z - s * y, 0, t * x * y - s * z, t * y * y + c, t * y * z + s * x, 0,
    t * x * z + s * y, t * y * z - s * x, t * z * z + c, 0, 0, 0, 0, 1]);
  return mul(T(p[0], p[1], p[2]), mul(r, T(-p[0], -p[1], -p[2])));
}
function persp(fov, asp, n, f) {
  const q = 1 / Math.tan(fov / 2), m = new Float32Array(16);
  m[0] = q / asp; m[5] = q; m[10] = (f + n) / (n - f); m[11] = -1; m[14] = (2 * f * n) / (n - f); return m;
}
function look(e, c, u) {
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const nrm = (a) => { const l = Math.hypot(...a); return a.map((v) => v / l); };
  const cr = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const dt = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const z = nrm(sub(e, c)), x = nrm(cr(u, z)), y = cr(z, x);
  return new Float32Array([x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dt(x, e), -dt(y, e), -dt(z, e), 1]);
}

/* ---------- 運動学（linkage.py と同じ） ---------- */
export function createKinematics(K) {
  function alphaOf(th) {
    const t = K.table;
    if (th <= t[0][0]) return t[0][1];
    for (let i = 1; i < t.length; i++) {
      if (th <= t[i][0]) { const f = (th - t[i - 1][0]) / (t[i][0] - t[i - 1][0]); return t[i - 1][1] + f * (t[i][1] - t[i - 1][1]); }
    }
    return t[t.length - 1][1];
  }
  const pinA = (al) => [K.O[0] + K.a * Math.cos(al * R), K.O[1] + K.a * Math.sin(al * R)];
  function pinB(th) {
    const dy = K.B0[0] - K.H[0], dz = K.B0[1] - K.H[1], c = Math.cos(th * R), s = Math.sin(th * R);
    return [K.H[0] + dy * c - dz * s, K.H[1] + dy * s + dz * c];
  }
  const linkAng = (al, th) => { const a = pinA(al), b = pinB(th); return Math.atan2(b[1] - a[1], b[0] - a[0]) / R; };
  const LAM0 = linkAng(K.alpha0, 0);
  const poseLid = (th) => RX(th, K.H[0], K.H[1]);
  const poseCrank = (al) => RX(al - K.alpha0, K.O[0], K.O[1]);
  function poseLinkAt(al, lam) { const a = pinA(al); return mul(T(0, a[0] - K.A0[0], a[1] - K.A0[1]), RX(lam - LAM0, K.A0[0], K.A0[1])); }
  const poseLink = (al, th) => poseLinkAt(al, linkAng(al, th));
  // リンクの B 端を -X へ逃がす曲げ（A を通り、リンクに直角な軸まわりの回転で近似）
  function bend(al, th, f) {
    const a = pinA(al), b = pinB(th), d = [b[0] - a[0], b[1] - a[1]], n = Math.hypot(d[0], d[1]);
    const ax = [0, -d[1] / n, d[0] / n];
    let deg = K.bend_deg * f;
    const probe = mul(RA(ax, deg, [0.3, a[0], a[1]]), T(0, b[0], b[1]));
    if (probe[12] > 0.3) deg = -deg;
    return RA(ax, deg, [0.3, a[0], a[1]]);
  }
  // 蓋角 θ の姿勢（組んだ状態）
  function pose(th, al = alphaOf(th)) {
    return { lid: poseLid(th), crank: poseCrank(al), ref_horn: poseCrank(al), link: poseLink(al, th) };
  }
  return { alphaOf, pinA, pinB, linkAng, poseLid, poseCrank, poseLinkAt, poseLink, bend, pose, K };
}

/* ---------- 3D 表示 ---------- */
function b64(s) { const bin = atob(s), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u.buffer; }
const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
function cssHex(c) {
  if (c.startsWith("#")) return c.length === 4 ? "#" + [...c.slice(1)].map((x) => x + x).join("") : c.slice(0, 7);
  const m = c.match(/\d+/g) || [0, 0, 0]; return "#" + m.slice(0, 3).map((v) => (+v).toString(16).padStart(2, "0")).join("");
}

export function createViewer(canvas, D, getState) {
  const gl = canvas.getContext("webgl2", { antialias: true });
  if (!gl) throw new Error("WebGL2 が使えません");
  const vs = `#version 300 es
in vec3 aPos; uniform mat4 uVP; uniform mat4 uM; out vec3 vW;
void main(){ vec4 w = uM * vec4(aPos, 1.0); vW = w.xyz; gl_Position = uVP * w; }`;
  const fs = `#version 300 es
precision highp float; in vec3 vW; uniform vec3 uCol; uniform vec3 uEye; uniform float uCutX; uniform float uCut; out vec4 o;
void main(){
  if (uCut > 0.5 && vW.x > uCutX) discard;
  vec3 n = normalize(cross(dFdx(vW), dFdy(vW)));
  if (dot(n, normalize(uEye - vW)) < 0.0) n = -n;
  float d = 0.48 + 0.45 * max(dot(n, normalize(vec3(0.45, 0.75, 1.0))), 0.0) + 0.20 * max(dot(n, normalize(vec3(-0.8, -0.3, 0.35))), 0.0);
  o = vec4(min(uCol * d, vec3(1.0)), 1.0);
}`;
  const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x);
    if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(x)); return x; };
  const prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, fs));
  gl.bindAttribLocation(prog, 0, "aPos"); gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  const U = {};
  for (const n of ["uVP", "uM", "uCol", "uEye", "uCutX", "uCut"]) U[n] = gl.getUniformLocation(prog, n);
  const bufs = {};
  const shown = partsIn(D);
  for (const [k] of shown) {
    const m = D.meshes[k];
    const p16 = new Int16Array(b64(m.pos)), pos = new Float32Array(p16.length);
    for (let i = 0; i < p16.length; i++) pos[i] = p16[i] * D.q;
    const vao = gl.createVertexArray(); gl.bindVertexArray(vao);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer()); gl.bufferData(gl.ARRAY_BUFFER, pos, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, gl.createBuffer()); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(b64(m.ind)), gl.STATIC_DRAW);
    bufs[k] = { vao, n: m.nt * 3 };
  }
  // 視点と「右半分を隠す」の境はモデルの大きさで決まる（データの view）
  const view = { target: [0, 0, 40], dist: 250, cutX: 6.0, ...(D.view || {}) };
  const HOME = { az: -35, el: 24, dist: view.dist };
  const cam = { ...HOME, tgt: view.target };
  const hidden = new Set();
  let bg = [1, 1, 1];
  let queued = false;
  function draw() {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; render(); });
  }
  // watchTheme は登録した時点で 1 度呼ぶので、draw を定義してから登録する
  watchTheme((p) => { bg = hex(cssHex(p.paper || themePalette().paper)); draw(); });
  function render() {
    const w = canvas.clientWidth, h = canvas.clientHeight, dpr = Math.min(2, window.devicePixelRatio || 1);
    if (!w || !h) return;
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) { canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr); }
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(bg[0], bg[1], bg[2], 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT); gl.enable(gl.DEPTH_TEST);
    const ce = Math.cos(cam.el * R);
    const eye = [cam.tgt[0] + cam.dist * ce * Math.cos(cam.az * R), cam.tgt[1] + cam.dist * ce * Math.sin(cam.az * R), cam.tgt[2] + cam.dist * Math.sin(cam.el * R)];
    gl.useProgram(prog);
    gl.uniformMatrix4fv(U.uVP, false, mul(persp(32 * R, canvas.width / canvas.height, 5, 2000), look(eye, cam.tgt, [0, 0, 1])));
    gl.uniform3fv(U.uEye, eye);
    const st = getState();
    for (const [k, , col] of shown) {
      if (hidden.has(k) || !st.vis.has(k)) continue;
      gl.uniformMatrix4fv(U.uM, false, (st.M && st.M[k]) || I4());
      gl.uniform3fv(U.uCol, hex(col));
      gl.uniform1f(U.uCut, st.cut && (k === "box" || k === "lid" || k === "pin") ? 1 : 0);
      gl.uniform1f(U.uCutX, view.cutX);
      gl.bindVertexArray(bufs[k].vao); gl.drawElements(gl.TRIANGLES, bufs[k].n, gl.UNSIGNED_SHORT, 0);
    }
  }
  // ドラッグで回転、ホイールかピンチで拡大
  const ptrs = new Map(); let pinch = 0;
  canvas.addEventListener("pointerdown", (e) => { canvas.setPointerCapture(e.pointerId); ptrs.set(e.pointerId, [e.clientX, e.clientY]); });
  const up = (e) => { ptrs.delete(e.pointerId); pinch = 0; };
  canvas.addEventListener("pointerup", up); canvas.addEventListener("pointercancel", up);
  canvas.addEventListener("pointermove", (e) => {
    if (!ptrs.has(e.pointerId)) return;
    const p = ptrs.get(e.pointerId), dx = e.clientX - p[0], dy = e.clientY - p[1];
    ptrs.set(e.pointerId, [e.clientX, e.clientY]);
    if (ptrs.size === 1) { cam.az -= dx * 0.4; cam.el = Math.max(-80, Math.min(85, cam.el + dy * 0.4)); }
    else if (ptrs.size === 2) {
      const [a, b] = [...ptrs.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]);
      if (pinch) cam.dist = Math.max(90, Math.min(600, (cam.dist * pinch) / d)); pinch = d;
    }
    draw();
  });
  canvas.addEventListener("wheel", (e) => { e.preventDefault(); cam.dist = Math.max(90, Math.min(600, cam.dist * Math.exp(e.deltaY * 0.001))); draw(); }, { passive: false });
  new ResizeObserver(draw).observe(canvas);
  return {
    draw,
    parts: shown,
    home() { Object.assign(cam, HOME); cam.tgt = view.target; draw(); },
    setHidden(k, on) { on ? hidden.add(k) : hidden.delete(k); draw(); },
  };
}

// 凡例（チェックで表示を切り替える）
export function buildLegend(el, viewer) {
  el.replaceChildren(...viewer.parts.map(([k, name, col]) => {
    const lb = document.createElement("label");
    const cb = document.createElement("input");
    cb.type = "checkbox"; cb.checked = true; cb.addEventListener("change", () => viewer.setHidden(k, !cb.checked));
    const sw = document.createElement("i"); sw.style.background = col;
    lb.append(cb, sw, name);
    return lb;
  }));
}

// 簡単な時系列グラフ（SVG）。series: [{name, color(css var), pts:[[x,y]...]}]
export function lineChart(el, o) {
  const W = 360, H = 180, m = { l: 40, r: 12, t: 10, b: 30 }, pw = W - m.l - m.r, ph = H - m.t - m.b;
  const sx = (x) => m.l + ((x - o.x[0]) / (o.x[1] - o.x[0])) * pw;
  const sy = (y) => m.t + ph - ((y - o.y[0]) / (o.y[1] - o.y[0])) * ph;
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${o.label}">`;
  for (const v of o.yt) s += `<line x1="${m.l}" x2="${m.l + pw}" y1="${sy(v)}" y2="${sy(v)}" class="grid"/><text x="${m.l - 5}" y="${sy(v) + 4}" text-anchor="end">${v}</text>`;
  for (const v of o.xt) s += `<text x="${sx(v)}" y="${m.t + ph + 14}" text-anchor="middle">${v}</text>`;
  s += `<line x1="${m.l}" x2="${m.l + pw}" y1="${m.t + ph}" y2="${m.t + ph}" class="axis"/>`;
  s += `<text x="${m.l + pw}" y="${H - 2}" text-anchor="end">${o.xl}</text><text x="${m.l}" y="${m.t - 1}" text-anchor="start" dy="-0">${o.yl}</text>`;
  for (const se of o.series) {
    if (!se.pts.length) continue;
    const d = se.pts.map((p, i) => (i ? "L" : "M") + sx(Math.min(o.x[1], Math.max(o.x[0], p[0]))).toFixed(1) + " " + sy(Math.min(o.y[1], Math.max(o.y[0], p[1]))).toFixed(1)).join("");
    s += `<path d="${d}" fill="none" stroke="var(${se.color})" stroke-width="2" stroke-linejoin="round" ${se.dash ? 'stroke-dasharray="4 3"' : ""}/>`;
  }
  if (o.cursor != null) s += `<line x1="${sx(o.cursor)}" x2="${sx(o.cursor)}" y1="${m.t}" y2="${m.t + ph}" class="cursor"/>`;
  s += "</svg>";
  el.innerHTML = s;
}
