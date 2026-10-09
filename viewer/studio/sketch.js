// Studio の 2D 断面エディタ（Figma 風の SVG）。契約は CONTRACT.md §3 §4。
// 図形データは常に断面の (u, v)（mm、v が上）。SVG は y が下なので描画の時だけ反転する。
// トップレベルでは DOM を触らない（sampleShape を node から import して試せるように）。

import { INTENTS, uid } from "./store.js";
import { watchTheme } from "../shared/workspace.mjs";

// ===========================================================================
// 純粋な幾何
// ===========================================================================

const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
const lerp2 = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));
const r2 = (x) => Math.round(x * 100) / 100;
const clone = (x) => JSON.parse(JSON.stringify(x));

function bez(p0, p1, p2, p3, t) {
  const m = 1 - t;
  const a = m * m * m, b = 3 * m * m * t, c = 3 * m * t * t, d = t * t * t;
  return [a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]];
}

const segIsLine = (a, b) => !a.out && !b.in;
const segCtrl = (a, b) => [a.p, a.out || a.p, b.in || b.p, b.p];

// 節点列をベジェとして密な折れ線に。閉じるなら最後が始点に戻る
function flattenNodes(nodes, closed, perSeg) {
  const pts = [];
  const n = nodes.length;
  if (!n) return pts;
  pts.push(nodes[0].p.slice());
  const segs = closed ? n : n - 1;
  for (let i = 0; i < segs; i++) {
    const a = nodes[i], b = nodes[(i + 1) % n];
    if (segIsLine(a, b)) { pts.push(b.p.slice()); continue; }
    const [p0, p1, p2, p3] = segCtrl(a, b);
    const poly = dist(p0, p1) + dist(p1, p2) + dist(p2, p3);
    const k = clamp(Math.ceil(poly / perSeg), 8, 400);
    for (let j = 1; j <= k; j++) pts.push(j === k ? p3.slice() : bez(p0, p1, p2, p3, j / k));
  }
  return pts;
}

// 弧長で等間隔に取り直す（端点は必ず含む）
function resample(pts, step) {
  if (pts.length < 2) return pts.map((p) => p.slice());
  const cum = [0];
  for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + dist(pts[i - 1], pts[i]));
  const total = cum[cum.length - 1];
  if (total < 1e-9) return [pts[0].slice()];
  const n = Math.max(1, Math.ceil(total / step - 1e-9));
  const out = [pts[0].slice()];
  let j = 1;
  for (let k = 1; k < n; k++) {
    const d = (total * k) / n;
    while (j < cum.length - 1 && cum[j] < d) j++;
    const seg = cum[j] - cum[j - 1];
    out.push(lerp2(pts[j - 1], pts[j], seg > 0 ? (d - cum[j - 1]) / seg : 0));
  }
  out.push(pts[pts.length - 1].slice());
  return out;
}

// 頂点を保ったまま各辺を step 以下に分割
function subdivide(pts, step) {
  if (!pts.length) return [];
  const out = [pts[0].slice()];
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1], b = pts[i];
    const n = Math.max(1, Math.ceil(dist(a, b) / step - 1e-9));
    for (let k = 1; k < n; k++) out.push(lerp2(a, b, k / n));
    out.push(b.slice());
  }
  return out;
}

function rectCorners(sh) {
  const a = sh.nodes[0].p, b = sh.nodes[1].p;
  const x0 = Math.min(a[0], b[0]), x1 = Math.max(a[0], b[0]);
  const y0 = Math.min(a[1], b[1]), y1 = Math.max(a[1], b[1]);
  return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
}

// 図形を step mm 間隔の折れ線に。閉じた図形（rect / ellipse / closed な曲線）は最後に始点を繰り返す
export function sampleShape(shape, step = 0.5) {
  const nodes = shape.nodes || [];
  const st = Math.max(step, 1e-3);
  switch (shape.kind) {
    case "text":
      return nodes[0] ? [nodes[0].p.slice()] : [];
    case "line": case "arrow": case "dim":
      if (nodes.length < 2) return nodes.map((n) => n.p.slice());
      return subdivide([nodes[0].p, nodes[1].p], st);
    case "rect": {
      if (nodes.length < 2) return nodes.map((n) => n.p.slice());
      const c = rectCorners(shape);
      return subdivide([c[0], c[1], c[2], c[3], c[0]], st);
    }
    case "ellipse": {
      if (nodes.length < 2) return nodes.map((n) => n.p.slice());
      const a = nodes[0].p, b = nodes[1].p;
      const cx = (a[0] + b[0]) / 2, cy = (a[1] + b[1]) / 2;
      const rx = Math.abs(a[0] - b[0]) / 2, ry = Math.abs(a[1] - b[1]) / 2;
      const fine = [];
      const N = 720;
      for (let i = 0; i <= N; i++) {
        const t = (i / N) * Math.PI * 2;
        fine.push([cx + rx * Math.cos(t), cy + ry * Math.sin(t)]);
      }
      fine[N] = fine[0].slice();
      return resample(fine, st);
    }
    default: { // pen / curve
      if (nodes.length < 2) return nodes.map((n) => n.p.slice());
      return resample(flattenNodes(nodes, !!shape.closed, Math.max(st * 0.25, 0.02)), st);
    }
  }
}

function ptSegDist(p, a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const l2 = dx * dx + dy * dy;
  let t = l2 > 0 ? ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2 : 0;
  t = clamp(t, 0, 1);
  return Math.hypot(p[0] - (a[0] + dx * t), p[1] - (a[1] + dy * t));
}

function nearestOnSeg(p, a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const l2 = dx * dx + dy * dy;
  const t = l2 > 0 ? clamp(((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2, 0, 1) : 0;
  return [a[0] + dx * t, a[1] + dy * t];
}

function polyDist(poly, p) {
  if (poly.length === 1) return dist(poly[0], p);
  let d = Infinity;
  for (let i = 1; i < poly.length; i++) d = Math.min(d, ptSegDist(p, poly[i - 1], poly[i]));
  return d;
}

function pointInPoly(p, poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const a = poly[i], b = poly[j];
    if ((a[1] > p[1]) !== (b[1] > p[1]) && p[0] < ((b[0] - a[0]) * (p[1] - a[1])) / (b[1] - a[1]) + a[0]) inside = !inside;
  }
  return inside;
}

function segSegHit(p, q, r, s) {
  const o = (a, b, c) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
  const d1 = o(p, q, r), d2 = o(p, q, s), d3 = o(r, s, p), d4 = o(r, s, q);
  return d1 * d2 < 0 && d3 * d4 < 0;
}

function segHitsRect(a, b, rc) {
  const inR = (p) => p[0] >= rc.x0 && p[0] <= rc.x1 && p[1] >= rc.y0 && p[1] <= rc.y1;
  if (inR(a) || inR(b)) return true;
  const c = [[rc.x0, rc.y0], [rc.x1, rc.y0], [rc.x1, rc.y1], [rc.x0, rc.y1]];
  for (let i = 0; i < 4; i++) if (segSegHit(a, b, c[i], c[(i + 1) % 4])) return true;
  return false;
}

// Ramer–Douglas–Peucker
function rdp(pts, tol) {
  const n = pts.length;
  if (n < 3) return pts.map((p) => p.slice());
  const keep = new Uint8Array(n);
  keep[0] = keep[n - 1] = 1;
  const stack = [[0, n - 1]];
  while (stack.length) {
    const [i, j] = stack.pop();
    let md = 0, mi = -1;
    for (let k = i + 1; k < j; k++) {
      const d = ptSegDist(pts[k], pts[i], pts[j]);
      if (d > md) { md = d; mi = k; }
    }
    if (mi >= 0 && md > tol) { keep[mi] = 1; stack.push([i, mi], [mi, j]); }
  }
  const out = [];
  for (let i = 0; i < n; i++) if (keep[i]) out.push(pts[i].slice());
  return out;
}

// 通る点列から滑らかなベジェ節点へ（Catmull-Rom 風。ハンドルは隣との距離の 1/3 で行き過ぎない）
function smoothNodes(pts, closed) {
  const n = pts.length;
  const nodes = pts.map((p) => ({ p: p.slice(), in: null, out: null }));
  if (n < 2) return nodes;
  for (let i = 0; i < n; i++) {
    const prev = closed ? pts[(i - 1 + n) % n] : i > 0 ? pts[i - 1] : null;
    const next = closed ? pts[(i + 1) % n] : i < n - 1 ? pts[i + 1] : null;
    const p = pts[i];
    if (prev && next) {
      const tx = next[0] - prev[0], ty = next[1] - prev[1];
      const tl = Math.hypot(tx, ty);
      if (tl > 1e-9) {
        const ux = tx / tl, uy = ty / tl;
        const dOut = dist(p, next) / 3, dIn = dist(p, prev) / 3;
        nodes[i].out = [p[0] + ux * dOut, p[1] + uy * dOut];
        nodes[i].in = [p[0] - ux * dIn, p[1] - uy * dIn];
      }
    } else if (next) {
      nodes[i].out = [p[0] + (next[0] - p[0]) / 3, p[1] + (next[1] - p[1]) / 3];
    } else if (prev) {
      nodes[i].in = [p[0] - (p[0] - prev[0]) / 3, p[1] - (p[1] - prev[1]) / 3];
    }
  }
  return nodes;
}

// 1 節点だけ、隣から滑らかなハンドルを作る（Alt+クリックで出す時）
function autoHandles(nodes, i, closed) {
  const n = nodes.length;
  const p = nodes[i].p;
  const prev = closed ? nodes[(i - 1 + n) % n].p : i > 0 ? nodes[i - 1].p : null;
  const next = closed ? nodes[(i + 1) % n].p : i < n - 1 ? nodes[i + 1].p : null;
  const out = { in: null, out: null };
  if (prev && next) {
    const tx = next[0] - prev[0], ty = next[1] - prev[1];
    const tl = Math.hypot(tx, ty);
    if (tl > 1e-9) {
      out.out = [p[0] + (tx / tl) * (dist(p, next) / 3), p[1] + (ty / tl) * (dist(p, next) / 3)];
      out.in = [p[0] - (tx / tl) * (dist(p, prev) / 3), p[1] - (ty / tl) * (dist(p, prev) / 3)];
    }
  } else if (next) {
    out.out = [p[0] + (next[0] - p[0]) / 3, p[1] + (next[1] - p[1]) / 3];
  } else if (prev) {
    out.in = [p[0] - (p[0] - prev[0]) / 3, p[1] - (p[1] - prev[1]) / 3];
  }
  return out;
}

function isCollinear(n) {
  if (!n.in || !n.out) return false;
  const a = [n.in[0] - n.p[0], n.in[1] - n.p[1]], b = [n.out[0] - n.p[0], n.out[1] - n.p[1]];
  const la = Math.hypot(a[0], a[1]), lb = Math.hypot(b[0], b[1]);
  if (la < 1e-9 || lb < 1e-9) return false;
  return (a[0] * b[0] + a[1] * b[1]) / (la * lb) < -0.995;
}

function angleSnap(a, w, stepDeg = 15) {
  const dx = w[0] - a[0], dy = w[1] - a[1];
  const d = Math.hypot(dx, dy);
  if (d < 1e-9) return w;
  const st = (stepDeg * Math.PI) / 180;
  const ang = Math.round(Math.atan2(dy, dx) / st) * st;
  return [a[0] + Math.cos(ang) * d, a[1] + Math.sin(ang) * d];
}

const isClosedShape = (sh) => sh.kind === "rect" || sh.kind === "ellipse" || ((sh.kind === "pen" || sh.kind === "curve") && !!sh.closed);
const isBezKind = (k) => k === "pen" || k === "curve";

function translateShape(sh, du, dv) {
  const mv = (q) => (q ? [q[0] + du, q[1] + dv] : null);
  return { ...sh, nodes: sh.nodes.map((n) => ({ p: mv(n.p), in: mv(n.in), out: mv(n.out) })) };
}

function textWidthPx(text, ui = 1) {
  let w = 0;
  for (const ch of String(text || "")) w += (ch.charCodeAt(0) > 255 ? 1 : 0.6) * 13 * ui;
  return w;
}

// 図形の範囲 {min:[u,v], max:[u,v]}（mm）
function shapeBounds(sh) {
  const pts = sampleShape(sh, 1);
  if (!pts.length) return null;
  const min = [Infinity, Infinity], max = [-Infinity, -Infinity];
  for (const p of pts) {
    min[0] = Math.min(min[0], p[0]); min[1] = Math.min(min[1], p[1]);
    max[0] = Math.max(max[0], p[0]); max[1] = Math.max(max[1], p[1]);
  }
  return { min, max };
}

function unionBounds(a, b) {
  if (!a) return b;
  if (!b) return a;
  return { min: [Math.min(a.min[0], b.min[0]), Math.min(a.min[1], b.min[1])], max: [Math.max(a.max[0], b.max[0]), Math.max(a.max[1], b.max[1])] };
}

// ===========================================================================
// 断面のキャッシュ（section:loops）
// ===========================================================================

function loopPathD(loops) {
  let fill = "", stroke = "";
  for (const lp of loops) {
    const pts = lp.points;
    if (pts.length < 2) continue;
    let d = "M" + pts.map((p) => `${r2(p[0])} ${r2(p[1])}`).join("L");
    if (lp.closed) { d += "Z"; fill += d; }
    stroke += d;
  }
  return { fill, stroke };
}

function prepareLoops(loops) {
  return (Array.isArray(loops) ? loops : [])
    .filter((lp) => lp && Array.isArray(lp.points) && lp.points.length)
    .map((lp) => {
      const bb = [Infinity, Infinity, -Infinity, -Infinity];
      for (const p of lp.points) {
        bb[0] = Math.min(bb[0], p[0]); bb[1] = Math.min(bb[1], p[1]);
        bb[2] = Math.max(bb[2], p[0]); bb[3] = Math.max(bb[3], p[1]);
      }
      return { points: lp.points, closed: !!lp.closed, bb };
    });
}

function boundsOfCache(c) {
  let b = null;
  if (c) {
    for (const lp of c.loops) b = unionBounds(b, { min: [lp.bb[0], lp.bb[1]], max: [lp.bb[2], lp.bb[3]] });
    if (c.bounds && c.bounds.min && c.bounds.max) b = unionBounds(b, { min: c.bounds.min.slice(), max: c.bounds.max.slice() });
  }
  return b;
}

function contentBounds(c, shapes) {
  let b = boundsOfCache(c);
  for (const sh of shapes) b = unionBounds(b, shapeBounds(sh));
  return b;
}

// ===========================================================================
// 見た目
// ===========================================================================

const FONT = '"Noto Sans JP","Yu Gothic UI",Meiryo,sans-serif';
const MONO = 'ui-monospace,"Cascadia Code",Consolas,monospace';
const DEFAULT_THEME = { panel: "#f5efe2", raised: "#ece4d4", line: "#d8cdb8", text: "#2b2723", text2: "#6a6257", mute: "#6a6257", accent: "#a8493c", accentInk: "#f5efe2" };
const STEPS = [0.1, 0.5, 1, 5, 10, 50, 100, 500, 1000, 5000];
const PX_PER_MM_100 = 96 / 25.4; // 倍率 100% = 実寸（96dpi）
const AXIS_NAMES = { x: "X 断面（側面）", y: "Y 断面（正面）", z: "Z 断面（上面）", view: "視線断面" };

function readTheme(el) {
  try {
    const cs = getComputedStyle(el);
    const g = (n, d) => cs.getPropertyValue(n).trim() || d;
    return {
      panel: g("--panel", DEFAULT_THEME.panel), raised: g("--raised", DEFAULT_THEME.raised), line: g("--line", DEFAULT_THEME.line),
      text: g("--text", DEFAULT_THEME.text), text2: g("--text-2", DEFAULT_THEME.text2), mute: g("--mute", DEFAULT_THEME.mute),
      accent: g("--accent", DEFAULT_THEME.accent), accentInk: g("--accent-ink", DEFAULT_THEME.accentInk),
    };
  } catch { return { ...DEFAULT_THEME }; }
}

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const axisName = (plane) => AXIS_NAMES[plane?.axis] || (plane?.axis ? `${String(plane.axis).toUpperCase()} 断面` : "断面");
const fmtOffset = (o) => `${o >= 0 ? "+" : "−"}${Math.abs(o || 0).toFixed(1)} mm`;
// 軸断面なら切断面のモデル座標（例「Y = 49.9 mm」）。視線断面は通る点からの移動量だけ
function planeWhere(plane, offset) {
  const k = { x: 0, y: 1, z: 2 }[plane && plane.axis];
  if (k === undefined || !plane.origin || !plane.normal) return `位置 ${fmtOffset(offset)}`;
  const val = plane.origin[k] + plane.normal[k] * (offset || 0);
  return `${plane.axis.toUpperCase()} = ${val.toFixed(1)} mm`;
}

function nodesPathD(nodes, closed, P) {
  const n = nodes.length;
  if (!n) return "";
  const f = (q) => { const s = P(q); return `${r2(s[0])} ${r2(s[1])}`; };
  let d = `M${f(nodes[0].p)}`;
  const segs = closed ? n : n - 1;
  for (let i = 0; i < segs; i++) {
    const a = nodes[i], b = nodes[(i + 1) % n];
    d += segIsLine(a, b) ? `L${f(b.p)}` : `C${f(a.out || a.p)} ${f(b.in || b.p)} ${f(b.p)}`;
  }
  return closed ? d + "Z" : d;
}

function shapeD(sh, P) {
  const nd = sh.nodes || [];
  switch (sh.kind) {
    case "line": case "arrow": case "dim": {
      if (nd.length < 2) return "";
      const a = P(nd[0].p), b = P(nd[1].p);
      return `M${r2(a[0])} ${r2(a[1])}L${r2(b[0])} ${r2(b[1])}`;
    }
    case "rect": {
      if (nd.length < 2) return "";
      return "M" + rectCorners(sh).map((c) => { const s = P(c); return `${r2(s[0])} ${r2(s[1])}`; }).join("L") + "Z";
    }
    case "ellipse": {
      if (nd.length < 2) return "";
      const a = P(nd[0].p), b = P(nd[1].p);
      const cx = (a[0] + b[0]) / 2, cy = (a[1] + b[1]) / 2;
      const rx = Math.abs(a[0] - b[0]) / 2, ry = Math.abs(a[1] - b[1]) / 2;
      if (rx < 0.01 || ry < 0.01) return "";
      return `M${r2(cx - rx)} ${r2(cy)}A${r2(rx)} ${r2(ry)} 0 1 0 ${r2(cx + rx)} ${r2(cy)}A${r2(rx)} ${r2(ry)} 0 1 0 ${r2(cx - rx)} ${r2(cy)}Z`;
    }
    case "text": return "";
    default: return nodesPathD(nd, !!sh.closed, P);
  }
}

function intentStyle(intent, ui) {
  const col = (INTENTS[intent] || INTENTS.target).color;
  const sw = ({ target: 2.5, remove: 2, add: 2, note: 1.3 }[intent] || 2.5) * ui;
  let dash = "", cap = "round";
  if (intent === "remove") dash = `${7 * ui} ${5 * ui}`;
  if (intent === "note") dash = `${0.1} ${4 * ui}`;
  return { col, sw, dash, cap };
}

function hatchDefs(prefix, ui) {
  const one = (intent) => {
    const col = INTENTS[intent].color;
    const g = 7 * ui;
    return `<pattern id="${prefix}h-${intent}" patternUnits="userSpaceOnUse" width="${g}" height="${g}" patternTransform="rotate(45)">` +
      `<rect width="${g}" height="${g}" fill="${col}" fill-opacity=".08"/>` +
      `<line x1="0" y1="0" x2="0" y2="${g}" stroke="${col}" stroke-width="${1.2 * ui}" stroke-opacity=".75"/></pattern>`;
  };
  return `<defs>${one("remove")}${one("add")}</defs>`;
}

// 1 つの図形を描く。P: (u,v) -> 画面 [x,y]
function shapeSVG(sh, c) {
  const { P, T, prefix, ui } = c;
  const { col, sw, dash, cap } = intentStyle(sh.intent, ui);
  const nd = sh.nodes || [];
  if (!nd.length) return "";
  let out = "";
  const halo = (d, alpha) =>
    `<path d="${d}" fill="none" stroke="${T.accent}" stroke-opacity="${alpha}" stroke-width="${sw + 6 * ui}" stroke-linecap="round" stroke-linejoin="round"/>`;

  if (sh.kind === "text") {
    const p = P(nd[0].p);
    const wd = textWidthPx(sh.text, ui);
    if (c.selected || c.hover) out += `<rect x="${r2(p[0] - 4)}" y="${r2(p[1] - 16 * ui)}" width="${r2(wd + 8)}" height="${r2(22 * ui)}" rx="3" fill="${T.accent}" fill-opacity="${c.selected ? 0.22 : 0.12}"/>`;
    out += `<text x="${r2(p[0])}" y="${r2(p[1])}" fill="${col}" font-size="${13 * ui}" font-family='${FONT}' stroke="${T.panel}" stroke-width="${3 * ui}" paint-order="stroke" stroke-linejoin="round">${esc(sh.text)}</text>`;
    return out;
  }

  const d = shapeD(sh, P);
  if (!d) return "";
  if (c.selected) out += halo(d, 0.35);
  else if (c.hover) out += halo(d, 0.18);
  const closed = isClosedShape(sh);
  const fill = closed && (sh.intent === "remove" || sh.intent === "add") ? `url(#${prefix}h-${sh.intent})` : "none";
  let pathD = d;
  let head = "";

  if (sh.kind === "arrow" && nd.length >= 2) {
    const a = P(nd[0].p), b = P(nd[1].p);
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (len > 1) {
      const ux = (b[0] - a[0]) / len, uy = (b[1] - a[1]) / len;
      const hl = Math.min(12 * ui, len * 0.8), hw = 5 * ui;
      const bx = b[0] - ux * hl, by = b[1] - uy * hl;
      pathD = `M${r2(a[0])} ${r2(a[1])}L${r2(bx + ux * 1.5)} ${r2(by + uy * 1.5)}`;
      head = `<path d="M${r2(b[0])} ${r2(b[1])}L${r2(bx - uy * hw)} ${r2(by + ux * hw)}L${r2(bx + uy * hw)} ${r2(by - ux * hw)}Z" fill="${col}" stroke="${col}" stroke-width="1" stroke-linejoin="round"/>`;
    }
  }
  out += `<path d="${pathD}" fill="${fill}" stroke="${col}" stroke-width="${sw}"${dash ? ` stroke-dasharray="${dash}"` : ""} stroke-linecap="${cap}" stroke-linejoin="round"/>`;
  out += head;

  if (sh.kind === "dim" && nd.length >= 2) {
    const a = P(nd[0].p), b = P(nd[1].p);
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
    const nx = -(b[1] - a[1]) / len * 6 * ui, ny = (b[0] - a[0]) / len * 6 * ui;
    out += `<path d="M${r2(a[0] - nx)} ${r2(a[1] - ny)}L${r2(a[0] + nx)} ${r2(a[1] + ny)}M${r2(b[0] - nx)} ${r2(b[1] - ny)}L${r2(b[0] + nx)} ${r2(b[1] + ny)}" stroke="${col}" stroke-width="${sw}" fill="none"/>`;
    out += `<text x="${r2((a[0] + b[0]) / 2)}" y="${r2((a[1] + b[1]) / 2 - 7 * ui)}" text-anchor="middle" fill="${col}" font-size="${12 * ui}" font-family='${MONO}' stroke="${T.panel}" stroke-width="${3 * ui}" paint-order="stroke">${dist(nd[0].p, nd[1].p).toFixed(1)} mm</text>`;
  }
  return out;
}

// 適応グリッド。8px 以上になる最小の段を細線、次の段を濃い線に
function gridSVG(view, size, T, ui) {
  const { s, tx, ty } = view;
  const gi = STEPS.findIndex((g) => g * s >= 8 * ui);
  if (gi < 0) return "";
  const g0 = STEPS[gi];
  const g1 = STEPS[gi + 1] || g0 * 5;
  const ratio = Math.max(1, Math.round(g1 / g0));
  const umin = (0 - tx) / s, umax = (size.w - tx) / s;
  const vmin = (ty - size.h) / s, vmax = ty / s;
  const i0 = Math.ceil(umin / g0), i1 = Math.floor(umax / g0);
  const j0 = Math.ceil(vmin / g0), j1 = Math.floor(vmax / g0);
  if (i1 - i0 > 800 || j1 - j0 > 800) return "";
  let minor = "", major = "";
  for (let i = i0; i <= i1; i++) {
    const x = Math.round(i * g0 * s + tx) + 0.5;
    const seg = `M${x} 0V${size.h}`;
    if (i % ratio === 0) major += seg; else minor += seg;
  }
  for (let j = j0; j <= j1; j++) {
    const y = Math.round(ty - j * g0 * s) + 0.5;
    const seg = `M0 ${y}H${size.w}`;
    if (j % ratio === 0) major += seg; else minor += seg;
  }
  let out = "";
  if (minor) out += `<path d="${minor}" stroke="${T.text}" stroke-opacity=".07" stroke-width="1" fill="none"/>`;
  if (major) out += `<path d="${major}" stroke="${T.text}" stroke-opacity=".15" stroke-width="1" fill="none"/>`;
  const ox = tx, oy = ty, arm = 14 * ui;
  if (ox > -arm && ox < size.w + arm && oy > -arm && oy < size.h + arm) {
    out += `<path d="M${r2(ox - arm)} ${r2(oy)}H${r2(ox + arm)}M${r2(ox)} ${r2(oy - arm)}V${r2(oy + arm)}" stroke="${T.text2}" stroke-width="${1.2 * ui}" fill="none"/>`;
  }
  return out;
}

// 断面の材料・輪郭・ゴースト（輪郭は拡大しても太らない）
function sectionSVG(view, c, T, ui) {
  if (!c) return "";
  const { s, tx, ty } = view;
  const m = `matrix(${s} 0 0 ${-s} ${tx} ${ty})`;
  let out = `<g transform="${m}">`;
  if (c.ghostD) out += `<path d="${c.ghostD}" fill="none" stroke="${T.mute}" stroke-width="${1.2 * ui}" stroke-dasharray="${5 * ui} ${4 * ui}" vector-effect="non-scaling-stroke" stroke-linejoin="round"/>`;
  if (c.fillD) out += `<path d="${c.fillD}" fill="${T.text}" fill-opacity=".08" fill-rule="evenodd" stroke="none"/>`;
  if (c.strokeD) out += `<path d="${c.strokeD}" fill="none" stroke="${T.text}" stroke-width="${1.5 * ui}" vector-effect="non-scaling-stroke" stroke-linejoin="round" stroke-linecap="round"/>`;
  return out + "</g>";
}

function noteNumbers(shapes) {
  const map = new Map();
  let n = 0;
  for (const sh of shapes) if (sh.note && String(sh.note).trim()) map.set(sh.id, ++n);
  return map;
}

function badgeSVG(sh, num, P, T, ui) {
  // 図形の上で右上に一番近い点の少し外側に置く（離れすぎると何のメモか分からない）
  const pts = sampleShape(sh, 1);
  if (!pts.length) return "";
  let best = pts[0];
  for (const p of pts) if (p[0] + p[1] > best[0] + best[1]) best = p;
  const q = P(best);
  let x = q[0] + 10 * ui;
  if (sh.kind === "text") x = q[0] + textWidthPx(sh.text, ui) + 12 * ui;
  const y = q[1] - 10 * ui;
  const col = (INTENTS[sh.intent] || INTENTS.target).color;
  return `<circle cx="${r2(x)}" cy="${r2(y)}" r="${8 * ui}" fill="${col}"/>` +
    `<text x="${r2(x)}" y="${r2(y + 4 * ui)}" text-anchor="middle" font-size="${11 * ui}" font-weight="700" font-family='${FONT}' fill="${T.accentInk}">${num}</text>`;
}

function niceScaleLen(s, targetPx) {
  const nice = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000];
  let best = nice[0];
  for (const v of nice) if (v * s <= targetPx) best = v;
  return best;
}

// ===========================================================================
// DOM（ここから先は createSketch の中だけで使う）
// ===========================================================================

const ICONS = {
  select: '<path d="M5 3.5v12l3.2-3 2.4 4.6 2-1-2.4-4.5H15z" fill="currentColor" stroke="none"/>',
  pen: '<path d="M4 16l.9-3.6L13 4.3l2.7 2.7-8.1 8.1z"/><path d="M11.6 5.7l2.7 2.7"/>',
  line: '<path d="M4.5 15.5l11-11"/><circle cx="4.5" cy="15.5" r="1.4" fill="currentColor"/><circle cx="15.5" cy="4.5" r="1.4" fill="currentColor"/>',
  curve: '<path d="M4.5 14.5C6 4 11 17 15.5 5.5"/><rect x="3" y="13" width="3" height="3" fill="currentColor" stroke="none"/><rect x="14" y="4" width="3" height="3" fill="currentColor" stroke="none"/>',
  rect: '<rect x="4" y="5.5" width="12" height="9" rx="1"/>',
  ellipse: '<ellipse cx="10" cy="10" rx="6.5" ry="5"/>',
  arrow: '<path d="M4.5 15.5l10-10"/><path d="M8.5 5H15v6.5"/>',
  text: '<path d="M5 5.5h10M10 5.5v10M8 15.5h4"/>',
  trash: '<path d="M5 6.5h10M8.5 6.5V4.5h3v2M6.5 6.5l.6 9h5.8l.6-9"/>',
  fit: '<path d="M4 8V4h4M16 8V4h-4M4 12v4h4M16 12v4h-4"/>',
  close: '<path d="M5.5 5.5l9 9M14.5 5.5l-9 9"/>',
  half: '<rect x="4" y="4.5" width="12" height="11" rx="1"/><path d="M10 4.5v11"/><path d="M4 8l3-3.5M4 12l6-7.5" stroke-width="1"/>',
};
const icon = (name) => `<svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name]}</svg>`;

const TOOL_DEFS = [
  { id: "select", key: "V", label: "選択", hint: "クリックで選ぶ。Shift で複数。空白をドラッグで範囲選択。節点をドラッグで形を直す。Space+ドラッグで画面を動かす" },
  { id: "pen", key: "P", label: "ペン", hint: "ドラッグで描く。離すと滑らかな曲線になる" },
  { id: "line", key: "L", label: "直線", hint: "ドラッグで直線。Shift で 15° 刻み" },
  { id: "curve", key: "B", label: "曲線", hint: "クリックで角の節点。ドラッグでハンドル付きの節点。始点をクリックで閉じる。Enter で終了" },
  { id: "rect", key: "R", label: "四角", hint: "ドラッグで四角。Shift で正方形" },
  { id: "ellipse", key: "O", label: "楕円", hint: "ドラッグで楕円。Shift で円" },
  { id: "arrow", key: "A", label: "矢印", hint: "ドラッグで矢印。Shift で 15° 刻み" },
  { id: "text", key: "T", label: "文字", hint: "クリックした位置に文字を入れる。Enter で確定" },
];
const KEY_TOOL = Object.fromEntries(TOOL_DEFS.map((t) => [t.key.toLowerCase(), t.id]));

const STYLE_ID = "sk-style";
const CSS = `
.sk-root{position:relative;display:flex;flex-direction:column;width:100%;height:100%;min-width:0;min-height:0;background:var(--panel,#f5efe2);color:var(--text,#2b2723);font:14px/1.5 var(--font-ui,"Noto Sans JP","Yu Gothic UI",sans-serif);user-select:none;-webkit-user-select:none;overflow:hidden;outline:none}
.sk-bar{display:flex;flex-direction:column;gap:6px;padding:6px 8px;border-bottom:1px solid var(--line,#d8cdb8);background:var(--raised,#ece4d4);flex:none}
.sk-row{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px;min-width:0}
.sk-sep{width:1px;height:20px;background:var(--line-strong,#3a424d);flex:none}
.sk-tool{display:inline-flex;align-items:center;justify-content:center;width:30px;height:28px;padding:0;border:1px solid transparent;border-radius:var(--radius-sm,4px);background:transparent;color:var(--text-2,#aab2bc);cursor:pointer}
.sk-tool:hover{background:var(--hover,#232830);color:var(--text,#e6e8ea)}
.sk-tool[aria-pressed=true]{background:var(--accent,#7c9cff);color:var(--accent-ink,#0b1020)}
.sk-chip{display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 10px 0 8px;border:1px solid var(--line,#d8cdb8);border-radius:0;background:transparent;color:var(--text-2,#6a6257);font:inherit;font-size:12px;cursor:pointer;white-space:nowrap}
.sk-chip:hover{background:var(--hover,#232830);color:var(--text,#e6e8ea)}
.sk-chip[aria-pressed=true]{border-color:var(--accent,#7c9cff);color:var(--text,#e6e8ea);background:var(--hover,#232830)}
.sk-dot{width:10px;height:10px;border-radius:50%;flex:none}
.sk-btn{display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 10px;border:1px solid var(--line,#2a3038);border-radius:var(--radius-sm,4px);background:transparent;color:var(--text-2,#aab2bc);font:inherit;font-size:12px;cursor:pointer;white-space:nowrap}
.sk-btn:hover{background:var(--hover,#232830);color:var(--text,#e6e8ea)}
.sk-btn[aria-pressed=true]{border-color:var(--accent,#7c9cff);color:var(--text,#e6e8ea);background:var(--hover,#232830)}
.sk-btn:disabled{opacity:.4;cursor:default}
.sk-lbl{color:var(--mute,#78818c);font-size:12px}
.sk-num{width:68px;height:26px;padding:0 6px;border:1px solid var(--line,#2a3038);border-radius:var(--radius-sm,4px);background:var(--panel,#15181c);color:var(--text,#e6e8ea);font:12px ui-monospace,"Cascadia Mono",Consolas,monospace;text-align:right;user-select:text;-webkit-user-select:text}
.sk-num:focus,.sk-note:focus,.sk-textin:focus{outline:none;border-color:var(--accent,#7c9cff)}
.sk-range{flex:1 1 90px;min-width:70px;max-width:260px;accent-color:var(--accent,#7c9cff)}
.sk-spacer{flex:1 1 0}
.sk-body{position:relative;flex:1 1 0;min-height:0;overflow:hidden}
.sk-svg{position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:none}
.sk-empty{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--mute,#78818c);pointer-events:none;text-align:center;padding:24px}
.sk-foot{flex:none;display:flex;flex-direction:column;gap:2px;padding:5px 10px 6px;border-top:1px solid var(--line,#2a3038);background:var(--raised,#1c2026);font-size:12px}
.sk-hint{color:var(--text-2,#aab2bc);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sk-stat{display:flex;flex-wrap:wrap;align-items:center;gap:2px 14px;color:var(--mute,#78818c)}
.sk-stat b{font-weight:400;color:var(--text-2,#aab2bc);font-family:ui-monospace,"Cascadia Mono",Consolas,monospace}
.sk-stat .sk-btn{height:20px;padding:0 8px;font-size:11px}
.sk-pop{position:absolute;z-index:3;display:flex;align-items:center;gap:6px;padding:6px;background:var(--raised,#ece4d4);border:1px solid var(--line-strong,#a99e90);border-radius:var(--radius,0);box-shadow:none}
.sk-pop[hidden]{display:none}
.sk-pdot{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;padding:0;border:1px solid transparent;border-radius:50%;background:transparent;cursor:pointer}
.sk-pdot:hover{background:var(--hover,#232830)}
.sk-pdot[aria-pressed=true]{border-color:var(--accent,#7c9cff)}
.sk-note{width:150px;height:26px;padding:0 8px;border:1px solid var(--line,#2a3038);border-radius:var(--radius-sm,4px);background:var(--panel,#15181c);color:var(--text,#e6e8ea);font:inherit;font-size:12px;user-select:text;-webkit-user-select:text}
.sk-textin{position:absolute;z-index:4;min-width:120px;height:26px;padding:0 8px;border:1px solid var(--accent,#a8493c);border-radius:var(--radius-sm,0);background:var(--raised,#ece4d4);color:var(--text,#2b2723);font:14px var(--font-ui,"Noto Sans JP","Yu Gothic UI",sans-serif);user-select:text;-webkit-user-select:text}
`;

function injectStyle() {
  if (document.getElementById(STYLE_ID)) return;
  const el = document.createElement("style");
  el.id = STYLE_ID;
  el.textContent = CSS;
  document.head.appendChild(el);
}

function h(tag, props = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "html") el.innerHTML = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (v === true) el.setAttribute(k, "");
    else el.setAttribute(k, v);
  }
  for (const kid of kids) if (kid != null) el.append(kid);
  return el;
}

let instanceSeq = 0;

export function createSketch(container, store, opts = {}) {
  injectStyle();
  const instance = ++instanceSeq;
  const prefix = `sk${instance}-`;

  // ---- 状態 ------------------------------------------------------------------
  const view = { s: 4, tx: 0, ty: 0 }; // 画面 x = u*s+tx, y = ty - v*s
  let size = { w: 0, h: 0 };
  let theme = { ...DEFAULT_THEME };
  const cache = new Map();             // 断面 id -> {loops, ghostLoops, bounds, fillD, strokeD, ghostD}
  const fitted = new Set();
  let pendingFit = null;
  let needFit = false;
  let selection = [];                  // 図形 id
  let hoverId = null;
  let cursorW = null;                  // [u,v] | null
  let cursorSnap = null;               // スナップ点 [u,v] | null
  let snapOn = true;
  let spaceDown = false;
  let gesture = null;
  let curveDraft = null;               // {nodes}
  let textEdit = null;                 // {el, w, id}
  let pointerInside = false;
  let lastInside = false;
  let lastDown = { t: 0, x: 0, y: 0, id: null };
  let offsetEditing = false;
  let noteEditing = false;
  let nudgeAt = 0;
  let raf = 0;
  let disposed = false;

  const activeId = () => store.state.activeSectionId;
  const activeItem = () => {
    const it = activeId() ? store.getItem(activeId()) : null;
    return it && it.type === "section" ? it : null;
  };
  const shapesOf = () => activeItem()?.shapes || [];
  const toW = (x, y) => [(x - view.tx) / view.s, (view.ty - y) / view.s];
  const toS = (p) => [p[0] * view.s + view.tx, view.ty - p[1] * view.s];

  // ---- DOM -------------------------------------------------------------------
  const toolBtns = TOOL_DEFS.map((t) => {
    const button = h("button", { class: "sk-tool", type: "button", "data-tool": t.id, title: `${t.label} (${t.key})`, "aria-label": t.label, "aria-pressed": "false", html: icon(t.id) });
    button.append(h("span", { class: "sk-tool-label" }, t.label));
    return button;
  });
  const intentBtns = Object.entries(INTENTS).map(([id, def]) =>
    h("button", { class: "sk-chip", type: "button", "data-intent": id, title: def.hint, "aria-pressed": "false" },
      h("span", { class: "sk-dot", style: `background:${def.color}` }), def.label));

  const offsetNum = h("input", { class: "sk-num", type: "number", step: "0.1", value: "0", "aria-label": "断面の位置（mm）", title: "断面の位置（法線方向、mm）" });
  const offsetRange = h("input", { class: "sk-range", type: "range", step: "0.1", min: "-100", max: "100", value: "0", "aria-label": "断面の位置" });
  const clipBtn = h("button", { class: "sk-btn", type: "button", title: "断面の手前側を 3D で隠す", "aria-pressed": "false", html: `${icon("half")}片側を隠す` });
  const fitBtn = h("button", { class: "sk-btn", type: "button", title: "全体表示 (F)", html: `${icon("fit")}全体表示` });
  const closeBtn = h("button", { class: "sk-btn", type: "button", title: "2D を閉じる", html: `${icon("close")}閉じる` });

  const bar = h("div", { class: "sk-bar" },
    h("div", { class: "sk-row" }, ...toolBtns, h("span", { class: "sk-sep" }), ...intentBtns),
    h("div", { class: "sk-row" },
      h("span", { class: "sk-lbl" }, "位置"), offsetNum, h("span", { class: "sk-lbl" }, "mm"), offsetRange, clipBtn,
      h("span", { class: "sk-spacer" }), fitBtn, closeBtn));

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "sk-svg");
  svg.setAttribute("tabindex", "-1");
  svg.style.outline = "none";
  const emptyMsg = h("div", { class: "sk-empty" }, "断面がありません。3D の「断面」で面をクリックすると、ここに断面が出ます");

  // 選択中の図形 1 つに出る小パネル
  const popDots = Object.entries(INTENTS).map(([id, def]) =>
    h("button", { class: "sk-pdot", type: "button", "data-intent": id, title: def.label, "aria-pressed": "false" },
      h("span", { class: "sk-dot", style: `background:${def.color}` })));
  const popNote = h("input", { class: "sk-note", type: "text", placeholder: "メモ（シュビーへの説明）", "aria-label": "図形のメモ" });
  const popDel = h("button", { class: "sk-tool", type: "button", title: "削除 (Delete)", "aria-label": "削除", html: icon("trash") });
  const pop = h("div", { class: "sk-pop", hidden: true }, ...popDots, popNote, popDel);

  const body = h("div", { class: "sk-body" }, svg, emptyMsg, pop);

  const hintEl = h("div", { class: "sk-hint" });
  const curEl = h("b", {}, "—");
  const zoomEl = h("b", {}, "100%");
  const snapBtn = h("button", { class: "sk-btn", type: "button", title: "輪郭の頂点と線上に吸い付く（Alt で一時的に解除）", "aria-pressed": "true" }, "スナップ ON");
  const axisEl = h("span", {}, "");
  const foot = h("div", { class: "sk-foot" }, hintEl,
    h("div", { class: "sk-stat" }, h("span", {}, "カーソル ", curEl), h("span", {}, "倍率 ", zoomEl), snapBtn, h("span", { class: "sk-spacer" }), axisEl));

  const root = h("div", { class: "sk-root", tabindex: "-1" }, bar, body, foot);
  container.append(root);

  // ---- 状態の同期（道具バー・位置・小パネル・状態行）-------------------------
  function offsetBounds(item) {
    let lo = -100, hi = 100;
    try {
      const b = opts.modelBox ? opts.modelBox() : null;
      if (b && item.plane) {
        let mn = Infinity, mx = -Infinity;
        const o = item.plane.origin, nrm = item.plane.normal;
        for (const x of [b.min[0], b.max[0]]) for (const y of [b.min[1], b.max[1]]) for (const z of [b.min[2], b.max[2]]) {
          const d = (x - o[0]) * nrm[0] + (y - o[1]) * nrm[1] + (z - o[2]) * nrm[2];
          mn = Math.min(mn, d); mx = Math.max(mx, d);
        }
        if (Number.isFinite(mn) && Number.isFinite(mx) && mx > mn) { lo = Math.floor(mn); hi = Math.ceil(mx); }
      }
    } catch (e) { console.error("[sketch] modelBox", e); }
    const off = Number(item.offset) || 0;
    return [Math.min(lo, off), Math.max(hi, off)];
  }

  function syncUI() {
    const item = activeItem();
    const tool = store.state.sketchTool;
    toolBtns.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.tool === tool)));
    intentBtns.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.intent === store.state.intent)));
    const def = TOOL_DEFS.find((t) => t.id === tool);
    hintEl.textContent = def ? def.hint : "";
    hintEl.title = def ? def.hint : "";
    snapBtn.textContent = snapOn ? "スナップ ON" : "スナップ OFF";
    snapBtn.setAttribute("aria-pressed", String(snapOn));
    for (const el of [offsetNum, offsetRange, clipBtn]) el.disabled = !item;
    if (!item) { axisEl.textContent = ""; return; }
    const off = Number(item.offset) || 0;
    const [lo, hi] = offsetBounds(item);
    offsetRange.min = String(lo); offsetRange.max = String(hi);
    if (document.activeElement !== offsetNum) offsetNum.value = String(r2(off));
    offsetRange.value = String(off);
    clipBtn.setAttribute("aria-pressed", String(!!item.clip));
    axisEl.textContent = axisName(item.plane);
  }

  // ---- 描画 ---------------------------------------------------------------
  function requestRender() {
    if (disposed || raf) return;
    raf = requestAnimationFrame(() => { raf = 0; draw(); });
  }

  function handlesOf(sh) {
    if (sh.kind === "text" || !sh.nodes?.length) return [];
    if (sh.kind === "rect" || sh.kind === "ellipse") {
      return rectCorners(sh).map((p, i) => ({ part: "corner", i, p }));
    }
    const hs = [];
    sh.nodes.forEach((n, i) => {
      if (isBezKind(sh.kind)) {
        if (n.in) hs.push({ part: "in", i, p: n.in });
        if (n.out) hs.push({ part: "out", i, p: n.out });
      }
      hs.push({ part: "p", i, p: n.p });
    });
    return hs;
  }

  function overlaySVG(item, shapes) {
    const T = theme;
    const P = toS;
    let out = "";
    // 選択中の図形の節点とハンドル
    for (const sh of shapes) {
      if (!selection.includes(sh.id)) continue;
      const hs = handlesOf(sh);
      for (const hd of hs) {
        if (hd.part === "in" || hd.part === "out") {
          const n = sh.nodes[hd.i];
          const a = P(n.p), b = P(hd.p);
          out += `<path d="M${r2(a[0])} ${r2(a[1])}L${r2(b[0])} ${r2(b[1])}" stroke="${T.accent}" stroke-width="1" fill="none"/>`;
        }
      }
      for (const hd of hs) {
        const q = P(hd.p);
        if (hd.part === "in" || hd.part === "out") {
          out += `<circle cx="${r2(q[0])}" cy="${r2(q[1])}" r="3.5" fill="${T.panel}" stroke="${T.accent}" stroke-width="1.5"/>`;
        } else {
          out += `<rect x="${r2(q[0] - 4)}" y="${r2(q[1] - 4)}" width="8" height="8" fill="${T.accent}" stroke="${T.panel}" stroke-width="1.5"/>`;
        }
      }
    }
    // 描きかけ
    const intent = store.state.intent;
    const ctx = { P, T, prefix, ui: 1, selected: false, hover: false };
    const preview = (sh) => `<g opacity=".85">${shapeSVG(sh, ctx)}</g>`;
    const g = gesture;
    if (g?.type === "pen" && g.pts.length > 1) {
      const { col, sw, cap } = intentStyle(intent, 1);
      out += `<path d="M${g.pts.map((p) => { const q = P(p); return `${r2(q[0])} ${r2(q[1])}`; }).join("L")}" fill="none" stroke="${col}" stroke-width="${sw}" stroke-linecap="${cap}" stroke-linejoin="round" opacity=".85"/>`;
    } else if (g?.type === "two") {
      const mk = { id: "_", kind: g.kind, intent, nodes: [{ p: g.a, in: null, out: null }, { p: g.b, in: null, out: null }], closed: g.kind === "rect" || g.kind === "ellipse", text: "", note: "" };
      out += preview(mk);
    } else if (g?.type === "marquee") {
      const a = P(g.a), b = P(g.b);
      out += `<rect x="${r2(Math.min(a[0], b[0]))}" y="${r2(Math.min(a[1], b[1]))}" width="${r2(Math.abs(a[0] - b[0]))}" height="${r2(Math.abs(a[1] - b[1]))}" fill="${T.accent}" fill-opacity=".08" stroke="${T.accent}" stroke-width="1" stroke-dasharray="4 3"/>`;
    }
    if (curveDraft && curveDraft.nodes.length) {
      const nodes = curveDraft.nodes.map((n) => ({ p: n.p, in: n.in, out: n.out }));
      let all = nodes;
      if (cursorW && !(gesture?.type === "curve")) all = [...nodes, { p: cursorW, in: null, out: null }];
      out += preview({ id: "_", kind: "curve", intent, nodes: all, closed: false, text: "", note: "" });
      curveDraft.nodes.forEach((n, i) => {
        const q = P(n.p);
        const near = i === 0 && curveDraft.nodes.length >= 3 && cursorW && dist(P(cursorW), q) <= 9;
        out += `<rect x="${r2(q[0] - 4)}" y="${r2(q[1] - 4)}" width="8" height="8" fill="${near ? T.accent : T.panel}" stroke="${T.accent}" stroke-width="1.5"/>`;
        if (n.out) { const o = P(n.out); out += `<path d="M${r2(q[0])} ${r2(q[1])}L${r2(o[0])} ${r2(o[1])}" stroke="${T.accent}" stroke-width="1"/><circle cx="${r2(o[0])}" cy="${r2(o[1])}" r="3" fill="${T.accent}"/>`; }
        if (n.in) { const o = P(n.in); out += `<path d="M${r2(q[0])} ${r2(q[1])}L${r2(o[0])} ${r2(o[1])}" stroke="${T.accent}" stroke-width="1"/><circle cx="${r2(o[0])}" cy="${r2(o[1])}" r="3" fill="${T.accent}"/>`; }
      });
    }
    // スナップ点
    if (cursorSnap) {
      const q = P(cursorSnap);
      out += `<circle cx="${r2(q[0])}" cy="${r2(q[1])}" r="5" fill="none" stroke="${T.accent}" stroke-width="1.5"/><circle cx="${r2(q[0])}" cy="${r2(q[1])}" r="1.8" fill="${T.accent}"/>`;
    }
    return out;
  }

  function draw() {
    if (disposed) return;
    const item = activeItem();
    emptyMsg.style.display = item ? "none" : "";
    svg.style.cursor = cursorFor();
    if (!item || !size.w || !size.h) {
      svg.innerHTML = "";
      pop.hidden = true;
      updateStatus();
      return;
    }
    const shapes = item.shapes || [];
    const T = theme;
    const ctxBase = { P: toS, T, prefix, ui: 1 };
    let html = hatchDefs(prefix, 1);
    html += gridSVG(view, size, T, 1);
    html += sectionSVG(view, cache.get(item.id), T, 1);
    for (const sh of shapes) html += shapeSVG(sh, { ...ctxBase, selected: selection.includes(sh.id), hover: sh.id === hoverId && !selection.includes(sh.id) && store.state.sketchTool === "select" });
    const nums = noteNumbers(shapes);
    for (const sh of shapes) if (nums.has(sh.id)) html += badgeSVG(sh, nums.get(sh.id), toS, T, 1);
    html += overlaySVG(item, shapes);
    svg.innerHTML = html;
    updateStatus();
    updatePop(item, shapes);
  }

  function updateStatus() {
    curEl.textContent = cursorW ? `u ${cursorW[0].toFixed(2)}  v ${cursorW[1].toFixed(2)} mm` : "—";
    zoomEl.textContent = `${Math.round((view.s / PX_PER_MM_100) * 100)}%`;
  }

  function cursorFor() {
    if (gesture?.type === "pan") return "grabbing";
    if (spaceDown) return "grab";
    const tool = store.state.sketchTool;
    if (tool === "select") return gesture?.type === "move" || gesture?.type === "node" ? "move" : hoverId ? "move" : "default";
    return tool === "text" ? "text" : "crosshair";
  }

  function updatePop(item, shapes) {
    const sel = selection.length === 1 ? shapes.find((s) => s.id === selection[0]) : null;
    const moving = gesture && (gesture.type === "move" || gesture.type === "node") && gesture.moved;
    if (!sel || moving || textEdit) { if (!noteEditing) pop.hidden = true; return; }
    pop.hidden = false;
    popDots.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.intent === sel.intent)));
    if (document.activeElement !== popNote) popNote.value = sel.note || "";
    // 図形の下に出す。入りきらなければ上
    const b = shapeBounds(sel);
    if (!b) { pop.hidden = true; return; }
    const lo = toS([b.min[0], b.min[1]]), hi = toS([b.max[0], b.max[1]]);
    const cx = (lo[0] + hi[0]) / 2;
    const pw = pop.offsetWidth || 270, ph = pop.offsetHeight || 40;
    let x = clamp(cx - pw / 2, 6, Math.max(6, size.w - pw - 6));
    let y = Math.max(lo[1], hi[1]) + 14;
    if (y + ph > size.h - 6) y = Math.min(lo[1], hi[1]) - ph - 14;
    y = clamp(y, 6, Math.max(6, size.h - ph - 6));
    pop.style.left = `${Math.round(x)}px`;
    pop.style.top = `${Math.round(y)}px`;
  }

  // ---- 表示範囲 ----------------------------------------------------------------
  function fit() {
    const item = activeItem();
    if (!size.w || !size.h) { needFit = true; return; }
    const b = item ? contentBounds(cache.get(item.id), item.shapes || []) : null;
    let min, max;
    if (b) { min = b.min; max = b.max; } else { min = [-50, -50]; max = [50, 50]; }
    const ew = Math.max(max[0] - min[0], 2), eh = Math.max(max[1] - min[1], 2);
    const m = Math.max(30, Math.min(size.w, size.h) * 0.08);
    const s = clamp(Math.min((size.w - 2 * m) / ew, (size.h - 2 * m) / eh), 0.1, 4000);
    const cx = (min[0] + max[0]) / 2, cy = (min[1] + max[1]) / 2;
    view.s = s;
    view.tx = size.w / 2 - cx * s;
    view.ty = size.h / 2 + cy * s;
    requestRender();
  }

  function resize() {
    const r = body.getBoundingClientRect();
    const w = Math.round(r.width), h = Math.round(r.height);
    theme = readTheme(root);
    if (w === size.w && h === size.h) return;
    if (size.w > 0 && size.h > 0 && w > 0 && h > 0) { view.tx += (w - size.w) / 2; view.ty += (h - size.h) / 2; }
    size = { w, h };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    if (needFit && w > 0 && h > 0) { needFit = false; fit(); }
    requestRender();
  }

  function zoomAt(px, factor) {
    const w = toW(px.x, px.y);
    const s = clamp(view.s * factor, 0.1, 4000);
    view.s = s;
    view.tx = px.x - w[0] * s;
    view.ty = px.y + w[1] * s;
    requestRender();
  }

  // ---- 図形の更新 -----------------------------------------------------------------
  function commitShapes(shapes, { history = true } = {}) {
    const id = activeId();
    if (id) store.updateItem(id, { shapes }, { history });
  }
  function addShape(sh) {
    commitShapes([...shapesOf(), sh]);
    selection = [sh.id];
  }
  function newShape(kind, nodes, extra = {}) {
    return { id: uid("s"), kind, intent: store.state.intent, nodes, closed: false, text: "", note: "", ...extra };
  }
  function patchShape(id, patch, history = true) {
    commitShapes(shapesOf().map((s) => (s.id === id ? { ...s, ...patch } : s)), { history });
  }
  function deleteSelection() {
    if (!selection.length) return false;
    const ids = new Set(selection);
    selection = [];
    commitShapes(shapesOf().filter((s) => !ids.has(s.id)));
    return true;
  }

  // ---- スナップ -------------------------------------------------------------------
  function snapTo(w, e) {
    if (!snapOn || (e && e.altKey)) return null;
    const c = cache.get(activeId());
    if (!c) return null;
    const R = 8 / view.s;
    let vBest = null, vd = R, sBest = null, sd = R;
    for (const lp of c.loops) {
      const bb = lp.bb;
      if (w[0] < bb[0] - R || w[0] > bb[2] + R || w[1] < bb[1] - R || w[1] > bb[3] + R) continue;
      const pts = lp.points, n = pts.length;
      for (let i = 0; i < n; i++) {
        const d = dist(pts[i], w);
        if (d < vd) { vd = d; vBest = pts[i]; }
        const j = i + 1 < n ? i + 1 : lp.closed ? 0 : -1;
        if (j < 0 || j === i) continue;
        const q = nearestOnSeg(w, pts[i], pts[j]);
        const dq = dist(q, w);
        if (dq < sd) { sd = dq; sBest = q; }
      }
    }
    if (vBest && vd <= sd + 1.5 / view.s) return { p: vBest.slice(), kind: "vertex" };
    if (sBest) return { p: sBest, kind: "edge" };
    return null;
  }

  function drawPoint(e, constrainFrom = null) {
    const px = local(e);
    let w = toW(px.x, px.y);
    let snap = null;
    if (constrainFrom && e.shiftKey) w = angleSnap(constrainFrom, w);
    else snap = snapTo(w, e);
    if (snap) w = snap.p;
    cursorSnap = snap ? snap.p : null;
    return { w, px, snap };
  }

  function local(e) {
    const r = svg.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  }

  // ---- 当たり判定 -----------------------------------------------------------------
  function hitHandle(px, shapes) {
    let best = null, bd = 9;
    for (const sh of shapes) {
      if (!selection.includes(sh.id)) continue;
      for (const hd of handlesOf(sh)) {
        const q = toS(hd.p);
        const d = Math.hypot(q[0] - px.x, q[1] - px.y) - (hd.part === "p" || hd.part === "corner" ? 0 : 1);
        if (d < bd) { bd = d; best = { shape: sh, ...hd }; }
      }
    }
    return best;
  }

  function hitShapeAt(px, shapes) {
    const w = toW(px.x, px.y);
    const tol = 6 / view.s;
    for (let i = shapes.length - 1; i >= 0; i--) {
      const sh = shapes[i];
      if (!sh.nodes?.length) continue;
      if (sh.kind === "text") {
        const q = toS(sh.nodes[0].p);
        if (px.x >= q[0] - 3 && px.x <= q[0] + textWidthPx(sh.text) + 3 && px.y >= q[1] - 15 && px.y <= q[1] + 5) return sh;
        continue;
      }
      const poly = sampleShape(sh, Math.max(3 / view.s, 0.02));
      if (!poly.length) continue;
      if (polyDist(poly, w) <= tol) return sh;
      if (isClosedShape(sh) && (sh.intent === "remove" || sh.intent === "add") && pointInPoly(w, poly)) return sh;
    }
    return null;
  }

  function shapesInRect(a, b, shapes) {
    const rc = { x0: Math.min(a[0], b[0]), x1: Math.max(a[0], b[0]), y0: Math.min(a[1], b[1]), y1: Math.max(a[1], b[1]) };
    const out = [];
    for (const sh of shapes) {
      if (!sh.nodes?.length) continue;
      const pts = sampleShape(sh, Math.max(2 / view.s, 0.05));
      let hit = false;
      if (pts.length === 1) hit = pts[0][0] >= rc.x0 && pts[0][0] <= rc.x1 && pts[0][1] >= rc.y0 && pts[0][1] <= rc.y1;
      for (let i = 1; i < pts.length && !hit; i++) hit = segHitsRect(pts[i - 1], pts[i], rc);
      if (hit) out.push(sh.id);
    }
    return out;
  }

  // ---- ポインタ操作 -----------------------------------------------------------------
  function onPointerDown(e) {
    lastInside = true;
    // preventDefault するので自動では外れない入力欄のフォーカスを手で外す
    if (document.activeElement === popNote || document.activeElement === offsetNum) document.activeElement.blur();
    commitText();
    if (!activeItem()) return;
    const px = local(e);
    try { svg.setPointerCapture(e.pointerId); } catch { /* 無くても動く */ }
    if (e.button === 1 || e.button === 2 || (e.button === 0 && spaceDown)) {
      e.preventDefault();
      gesture = { type: "pan", sx: px.x, sy: px.y, tx: view.tx, ty: view.ty };
      requestRender();
      return;
    }
    if (e.button !== 0) return;
    e.preventDefault();
    const tool = store.state.sketchTool;
    const now = performance.now();
    const dbl = now - lastDown.t < 350 && Math.hypot(px.x - lastDown.x, px.y - lastDown.y) < 6;
    const prevDown = lastDown;
    lastDown = { t: now, x: px.x, y: px.y, id: null };

    if (tool === "select") return selectDown(e, px, dbl, prevDown);
    if (tool === "pen") {
      const { w, snap } = drawPoint(e);
      gesture = { type: "pen", pts: [w], lastPx: px, snapStart: !!snap };
    } else if (tool === "line" || tool === "arrow" || tool === "rect" || tool === "ellipse") {
      const { w } = drawPoint(e);
      gesture = { type: "two", kind: tool, a: w, b: w, startPx: px };
    } else if (tool === "curve") {
      curveDown(e, px, dbl);
    } else if (tool === "text") {
      openTextEdit(toW(px.x, px.y), "", null, px);
    }
    requestRender();
  }

  function selectDown(e, px, dbl, prevDown) {
    const shapes = shapesOf();
    const hd = hitHandle(px, shapes);
    if (hd) {
      if (hd.part === "p" && e.altKey && isBezKind(hd.shape.kind)) { toggleHandles(hd.shape.id, hd.i); return; }
      gesture = { type: "node", id: hd.shape.id, i: hd.i, part: hd.part, start: clone(shapes), startPx: px, moved: false };
      requestRender();
      return;
    }
    const hit = hitShapeAt(px, shapes);
    if (hit) {
      lastDown.id = hit.id;
      if (dbl && hit.kind === "text" && prevDown.id === hit.id) {
        selection = [hit.id];
        const q = toS(hit.nodes[0].p);
        openTextEdit(hit.nodes[0].p, hit.text, hit.id, { x: q[0], y: q[1] });
        requestRender();
        return;
      }
      let narrow = null;
      if (e.shiftKey) {
        selection = selection.includes(hit.id) ? selection.filter((i) => i !== hit.id) : [...selection, hit.id];
      } else if (!selection.includes(hit.id)) {
        selection = [hit.id];
      } else if (selection.length > 1) {
        narrow = hit.id;
      }
      if (selection.includes(hit.id)) {
        gesture = { type: "move", ids: new Set(selection), start: clone(shapes), startPx: px, moved: false, narrow };
      }
      requestRender();
      return;
    }
    const w = toW(px.x, px.y);
    const base = e.shiftKey ? selection.slice() : [];
    selection = base.slice();
    gesture = { type: "marquee", a: w, b: w, base, startPx: px };
    requestRender();
  }

  function curveDown(e, px, dbl) {
    if (curveDraft && dbl) { finishCurve(false); return; }
    const { w } = drawPoint(e);
    if (!curveDraft) curveDraft = { nodes: [] };
    const nodes = curveDraft.nodes;
    if (nodes.length >= 3) {
      const f = toS(nodes[0].p);
      if (Math.hypot(f[0] - px.x, f[1] - px.y) <= 9) { finishCurve(true); return; }
    }
    nodes.push({ p: w, in: null, out: null });
    gesture = { type: "curve", idx: nodes.length - 1, startPx: px, dragged: false };
  }

  function finishCurve(closed) {
    const d = curveDraft;
    curveDraft = null;
    if (gesture?.type === "curve") gesture = null;
    if (!d) return;
    const tol = 4 / view.s;
    const nodes = [];
    for (const n of d.nodes) {
      const last = nodes[nodes.length - 1];
      if (last && dist(last.p, n.p) < tol) { if (n.in) last.in = n.in; continue; }
      nodes.push({ p: n.p, in: n.in, out: n.out });
    }
    if (closed && nodes.length > 1 && dist(nodes[0].p, nodes[nodes.length - 1].p) < tol) nodes.pop();
    if (nodes.length < 2) { requestRender(); return; }
    if (!closed) { nodes[0].in = null; nodes[nodes.length - 1].out = null; }
    addShape(newShape("curve", nodes, { closed }));
    requestRender();
  }

  function finishPen(g) {
    const pts = g.pts.map((p) => p.slice());
    let len = 0;
    for (let i = 1; i < pts.length; i++) len += dist(pts[i - 1], pts[i]);
    if (pts.length < 2 || len * view.s < 6) return;
    let closed = false;
    if (pts.length >= 8 && dist(pts[0], pts[pts.length - 1]) * view.s <= 10 && len * view.s > 60) {
      closed = true;
      pts.pop();
    } else {
      // 始点と終点は輪郭に吸い付ける
      const s0 = snapTo(pts[0], { altKey: false }), s1 = snapTo(pts[pts.length - 1], { altKey: false });
      if (s0) pts[0] = s0.p;
      if (s1) pts[pts.length - 1] = s1.p;
    }
    let simp = rdp(closed ? [...pts, pts[0]] : pts, 1.8 / view.s);
    if (closed) simp.pop();
    if (simp.length < 2) return;
    addShape(newShape("pen", smoothNodes(simp, closed), { closed }));
  }

  function toggleHandles(id, i) {
    const shapes = shapesOf();
    const sh = shapes.find((s) => s.id === id);
    if (!sh) return;
    const nodes = clone(sh.nodes);
    const n = nodes[i];
    if (n.in || n.out) { n.in = null; n.out = null; }
    else { const a = autoHandles(nodes, i, !!sh.closed); n.in = a.in; n.out = a.out; }
    commitShapes(shapes.map((s) => (s.id === id ? { ...s, nodes } : s)));
    selection = [id];
    requestRender();
  }

  function onPointerMove(e) {
    const px = local(e);
    const g = gesture;
    const tool = store.state.sketchTool;
    if (g?.type === "pan") {
      view.tx = g.tx + (px.x - g.sx);
      view.ty = g.ty + (px.y - g.sy);
      requestRender();
      return;
    }
    let w = toW(px.x, px.y);
    // ヒント: 描く道具・節点ドラッグ中だけスナップ点を出す
    const drawing = tool !== "select" && tool !== "text";
    if (drawing && !g) {
      const sn = snapTo(w, e);
      cursorSnap = sn ? sn.p : null;
      if (sn) w = sn.p;
    } else if (!g) {
      cursorSnap = null;
    }
    cursorW = w;

    if (!g) {
      if (tool === "select") {
        const hit = hitHandle(px, shapesOf()) ? null : hitShapeAt(px, shapesOf());
        hoverId = hit ? hit.id : null;
      }
      requestRender();
      return;
    }

    if (g.type === "pen") {
      const rawW = toW(px.x, px.y);
      if (Math.hypot(px.x - g.lastPx.x, px.y - g.lastPx.y) >= 2.5) { g.pts.push(rawW); g.lastPx = px; }
      cursorSnap = null;
    } else if (g.type === "two") {
      if (g.kind === "line" || g.kind === "arrow") {
        g.b = drawPoint(e, g.a).w;
      } else {
        let b = drawPoint(e).w;
        if (e.shiftKey) {
          const du = b[0] - g.a[0], dv = b[1] - g.a[1];
          const m = Math.max(Math.abs(du), Math.abs(dv));
          b = [g.a[0] + (du < 0 ? -m : m), g.a[1] + (dv < 0 ? -m : m)];
          cursorSnap = null;
        }
        g.b = b;
      }
      cursorW = g.b;
    } else if (g.type === "curve") {
      if (!g.dragged && Math.hypot(px.x - g.startPx.x, px.y - g.startPx.y) > 3) g.dragged = true;
      if (g.dragged && curveDraft) {
        const n = curveDraft.nodes[g.idx];
        const o = toW(px.x, px.y);
        n.out = o;
        n.in = [2 * n.p[0] - o[0], 2 * n.p[1] - o[1]];
        cursorW = o;
      }
    } else if (g.type === "marquee") {
      g.b = toW(px.x, px.y);
      selection = [...new Set([...g.base, ...shapesInRect(g.a, g.b, shapesOf())])];
    } else if (g.type === "move") {
      if (!g.moved) {
        if (Math.hypot(px.x - g.startPx.x, px.y - g.startPx.y) < 3) return;
        g.moved = true;
        store.checkpoint();
      }
      const w0 = toW(g.startPx.x, g.startPx.y), w1 = toW(px.x, px.y);
      let du = w1[0] - w0[0], dv = w1[1] - w0[1];
      if (e.shiftKey) { if (Math.abs(du) > Math.abs(dv)) dv = 0; else du = 0; }
      commitShapes(g.start.map((s) => (g.ids.has(s.id) ? translateShape(s, du, dv) : s)), { history: false });
    } else if (g.type === "node") {
      if (!g.moved) {
        if (Math.hypot(px.x - g.startPx.x, px.y - g.startPx.y) < 3) return;
        g.moved = true;
        store.checkpoint();
      }
      applyNodeDrag(g, e, px);
    }
    requestRender();
  }

  function applyNodeDrag(g, e, px) {
    const sh0 = g.start.find((s) => s.id === g.id);
    if (!sh0) return;
    let w = toW(px.x, px.y);
    const sh = clone(sh0);
    if (g.part === "corner") {
      const cs = rectCorners(sh0);
      const opp = cs[(g.i + 2) % 4];
      let q = w;
      const sn = snapTo(w, e);
      if (sn) q = sn.p;
      cursorSnap = sn ? sn.p : null;
      if (e.shiftKey) {
        const du = q[0] - opp[0], dv = q[1] - opp[1];
        const m = Math.max(Math.abs(du), Math.abs(dv));
        q = [opp[0] + (du < 0 ? -m : m), opp[1] + (dv < 0 ? -m : m)];
        cursorSnap = null;
      }
      sh.nodes = [{ p: opp, in: null, out: null }, { p: q, in: null, out: null }];
    } else if (g.part === "p") {
      const o = sh0.nodes[g.i];
      if ((sh.kind === "line" || sh.kind === "arrow") && e.shiftKey) {
        w = angleSnap(sh0.nodes[1 - g.i].p, w);
        cursorSnap = null;
      } else {
        const sn = snapTo(w, e);
        if (sn) w = sn.p;
        cursorSnap = sn ? sn.p : null;
      }
      const du = w[0] - o.p[0], dv = w[1] - o.p[1];
      const n = sh.nodes[g.i];
      n.p = w;
      if (o.in) n.in = [o.in[0] + du, o.in[1] + dv];
      if (o.out) n.out = [o.out[0] + du, o.out[1] + dv];
    } else {
      const o = sh0.nodes[g.i];
      const other = g.part === "in" ? "out" : "in";
      const n = sh.nodes[g.i];
      n[g.part] = w;
      if (o[other] && isCollinear(o)) {
        const L = dist(o[other], o.p);
        const dx = o.p[0] - w[0], dy = o.p[1] - w[1];
        const dl = Math.hypot(dx, dy);
        if (dl > 1e-9) n[other] = [o.p[0] + (dx / dl) * L, o.p[1] + (dy / dl) * L];
      }
    }
    commitShapes(g.start.map((s) => (s.id === g.id ? sh : s)), { history: false });
    cursorW = w;
  }

  function onPointerUp(e) {
    const g = gesture;
    try { svg.releasePointerCapture(e.pointerId); } catch { /* 無くても動く */ }
    if (!g) return;
    const px = local(e);
    if (g.type === "pan") { gesture = null; requestRender(); return; }
    if (g.type === "curve") { gesture = null; requestRender(); return; }
    gesture = null;
    if (g.type === "pen") finishPen(g);
    else if (g.type === "two") {
      if (Math.hypot(px.x - g.startPx.x, px.y - g.startPx.y) >= 4 && dist(g.a, g.b) * view.s >= 3) {
        const nodes = [{ p: g.a, in: null, out: null }, { p: g.b, in: null, out: null }];
        addShape(newShape(g.kind, nodes, { closed: g.kind === "rect" || g.kind === "ellipse" }));
      }
    } else if (g.type === "move") {
      if (!g.moved && g.narrow) selection = [g.narrow];
    } else if (g.type === "marquee") {
      /* 選択は move 中に反映済み */
    }
    cursorSnap = null;
    requestRender();
  }

  function onWheel(e) {
    if (!activeItem()) return;
    e.preventDefault();
    let dy = e.deltaY;
    if (e.deltaMode === 1) dy *= 16; else if (e.deltaMode === 2) dy *= 100;
    const k = e.ctrlKey ? 0.01 : 0.0016;
    zoomAt(local(e), Math.exp(-dy * k));
  }

  // ---- 文字 -------------------------------------------------------------------------
  function openTextEdit(w, value, id, px) {
    commitText();
    const el = h("input", { class: "sk-textin", type: "text", value, placeholder: "文字を入力", "aria-label": "図形の文字" });
    el.style.left = `${Math.round(px.x)}px`;
    el.style.top = `${Math.round(px.y - 13)}px`;
    el.addEventListener("keydown", (ev) => {
      ev.stopPropagation();
      if (ev.key === "Enter" && !ev.isComposing) { ev.preventDefault(); commitText(); }
      else if (ev.key === "Escape") { ev.preventDefault(); cancelText(); }
    });
    el.addEventListener("blur", () => commitText());
    body.append(el);
    textEdit = { el, w, id };
    requestAnimationFrame(() => { el.focus(); el.select(); });
  }
  function closeTextEl() {
    const t = textEdit;
    textEdit = null;
    if (t) { t.el.remove(); }
    return t;
  }
  function commitText() {
    if (!textEdit) return;
    const { el, w, id } = textEdit;
    const val = el.value.trim();
    textEdit = null;
    el.remove();
    if (id) {
      if (val) patchShape(id, { text: val });
      else { selection = []; commitShapes(shapesOf().filter((s) => s.id !== id)); }
    } else if (val) {
      addShape(newShape("text", [{ p: w, in: null, out: null }], { text: val }));
    }
    requestRender();
  }
  function cancelText() {
    closeTextEl();
    requestRender();
  }

  // ---- キー -------------------------------------------------------------------------
  function setTool(t) {
    if (curveDraft) finishCurve(false);
    commitText();
    store.set({ sketchTool: t });
  }

  function handleKey(e) {
    if (e.ctrlKey || e.metaKey) return false;
    if (!activeItem()) return false;
    const ae = document.activeElement;
    if (ae && root.contains(ae) && (ae.tagName === "INPUT" || ae.tagName === "TEXTAREA")) return false;
    const key = e.key;
    const done = () => { e.preventDefault(); return true; };
    if (key === " " || key === "Spacebar") { if (!spaceDown) { spaceDown = true; requestRender(); } return done(); }
    if (key === "Escape") {
      if (curveDraft) { finishCurve(false); return done(); }
      if (gesture && gesture.type !== "pan") {
        // ドラッグ中の Esc は元に戻す
        if ((gesture.type === "move" || gesture.type === "node") && gesture.moved) commitShapes(gesture.start, { history: false });
        gesture = null; cursorSnap = null; requestRender();
        return done();
      }
      if (selection.length) { selection = []; requestRender(); return done(); }
      if (store.state.sketchTool !== "select") { setTool("select"); return done(); }
      return false;
    }
    if (key === "Enter") {
      if (curveDraft) { finishCurve(false); return done(); }
      return false;
    }
    if (key === "Delete" || key === "Backspace") {
      if (curveDraft) {
        curveDraft.nodes.pop();
        if (!curveDraft.nodes.length) curveDraft = null;
        requestRender();
        return done();
      }
      return deleteSelection() ? done() : false;
    }
    if (key.startsWith("Arrow")) {
      if (!selection.length) return false;
      const st = e.shiftKey ? 1 : 0.1;
      const du = key === "ArrowLeft" ? -st : key === "ArrowRight" ? st : 0;
      const dv = key === "ArrowDown" ? -st : key === "ArrowUp" ? st : 0;
      const now = performance.now();
      const ids = new Set(selection);
      const history = now - nudgeAt > 600;
      nudgeAt = now;
      commitShapes(shapesOf().map((s) => (ids.has(s.id) ? translateShape(s, du, dv) : s)), { history });
      return done();
    }
    if (e.altKey) return false;
    let k = key.length === 1 ? key.toLowerCase() : "";
    if (!k && /^Key[A-Z]$/.test(e.code || "")) k = e.code.slice(3).toLowerCase();
    if (k === "f") { fit(); return done(); }
    if (KEY_TOOL[k]) { setTool(KEY_TOOL[k]); return done(); }
    return false;
  }

  function isFocused() { return pointerInside || lastInside; }

  // ---- 書き出し ---------------------------------------------------------------------
  function buildExport(id, width) {
    const item = store.getItem(id);
    if (!item || item.type !== "section") throw new Error(`断面が見つかりません: ${id}`);
    const T = readTheme(root);
    const c = cache.get(id);
    const shapes = item.shapes || [];
    const ui = clamp(width / 1100, 1, 3);
    const pad = 44 * ui;
    const b = contentBounds(c, shapes) || { min: [-50, -50], max: [50, 50] };
    const ew = Math.max(b.max[0] - b.min[0], 2), eh = Math.max(b.max[1] - b.min[1], 2);
    const W = Math.round(width);
    const Hd = Math.round(clamp((W - 2 * pad) * (eh / ew) + 2 * pad, 480 * ui, W * 1.3));
    const s = Math.min((W - 2 * pad) / ew, (Hd - 2 * pad) / eh);
    const cx = (b.min[0] + b.max[0]) / 2, cy = (b.min[1] + b.max[1]) / 2;
    const v = { s, tx: W / 2 - cx * s, ty: Hd / 2 + cy * s };
    const P = (p) => [p[0] * v.s + v.tx, v.ty - p[1] * v.s];
    const nums = noteNumbers(shapes);
    const noted = shapes.filter((sh) => nums.has(sh.id));
    const lineH = 24 * ui;
    const stripH = noted.length ? noted.length * lineH + 20 * ui : 0;
    const H = Hd + stripH;
    const prefixX = `skx${instance}-`;
    let out = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family='${FONT}'>`;
    out += `<rect width="${W}" height="${H}" fill="${T.panel}"/>`;
    out += hatchDefs(prefixX, ui);
    out += gridSVG(v, { w: W, h: Hd }, T, ui);
    out += sectionSVG(v, c, T, ui);
    const ctx = { P, T, prefix: prefixX, ui, selected: false, hover: false };
    for (const sh of shapes) out += shapeSVG(sh, ctx);
    for (const sh of noted) out += badgeSVG(sh, nums.get(sh.id), P, T, ui);
    // スケールバーと軸名（右下）
    const len = niceScaleLen(v.s, 150 * ui);
    const bx2 = W - pad * 0.7, bx1 = bx2 - len * v.s, by = Hd - pad * 0.95;
    out += `<path d="M${r2(bx1)} ${r2(by)}H${r2(bx2)}M${r2(bx1)} ${r2(by - 5 * ui)}V${r2(by + 5 * ui)}M${r2(bx2)} ${r2(by - 5 * ui)}V${r2(by + 5 * ui)}" stroke="${T.text}" stroke-width="${1.5 * ui}" fill="none"/>`;
    out += `<text x="${r2((bx1 + bx2) / 2)}" y="${r2(by - 9 * ui)}" text-anchor="middle" font-size="${12 * ui}" fill="${T.text}" font-family='${MONO}'>${len} mm</text>`;
    out += `<text x="${r2(bx2)}" y="${r2(by + 22 * ui)}" text-anchor="end" font-size="${12 * ui}" fill="${T.text2}">${esc(axisName(item.plane))}　${esc(planeWhere(item.plane, Number(item.offset) || 0))}</text>`;
    if (noted.length) {
      out += `<path d="M${r2(pad * 0.5)} ${r2(Hd)}H${r2(W - pad * 0.5)}" stroke="${T.line}" stroke-width="${ui}"/>`;
      noted.forEach((sh, i) => {
        const y = Hd + 12 * ui + i * lineH + lineH / 2;
        const col = (INTENTS[sh.intent] || INTENTS.target).color;
        out += `<circle cx="${r2(pad * 0.5 + 9 * ui)}" cy="${r2(y)}" r="${8 * ui}" fill="${col}"/>`;
        out += `<text x="${r2(pad * 0.5 + 9 * ui)}" y="${r2(y + 4 * ui)}" text-anchor="middle" font-size="${11 * ui}" font-weight="700" fill="${T.accentInk}">${nums.get(sh.id)}</text>`;
        out += `<text x="${r2(pad * 0.5 + 26 * ui)}" y="${r2(y + 4.5 * ui)}" font-size="${13 * ui}" fill="${T.text}">${esc(sh.note)}</text>`;
      });
    }
    return { svg: out + "</svg>", w: W, h: H };
  }

  function exportSVG(sectionId) {
    return buildExport(sectionId, 1400).svg;
  }

  async function exportPNG(sectionId, { width = 1400 } = {}) {
    const { svg: str, w, h } = buildExport(sectionId, width);
    const img = new Image();
    await new Promise((res, rej) => {
      img.onload = res;
      img.onerror = () => rej(new Error("断面の画像を作れませんでした"));
      img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(str);
    });
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    canvas.getContext("2d").drawImage(img, 0, 0, w, h);
    return canvas.toDataURL("image/png");
  }

  // ---- 配線 -------------------------------------------------------------------------
  const disposers = [];
  disposers.push(watchTheme(() => { theme = readTheme(root); requestRender(); }));
  const on = (target, type, fn, o) => { target.addEventListener(type, fn, o); disposers.push(() => target.removeEventListener(type, fn, o)); };

  on(svg, "pointerdown", onPointerDown);
  on(svg, "pointermove", onPointerMove);
  on(svg, "pointerup", onPointerUp);
  on(svg, "pointercancel", (e) => { gesture = null; try { svg.releasePointerCapture(e.pointerId); } catch { /* */ } requestRender(); });
  on(svg, "wheel", onWheel, { passive: false });
  on(svg, "contextmenu", (e) => e.preventDefault());
  on(svg, "pointerenter", () => { pointerInside = true; });
  on(svg, "pointerleave", () => { pointerInside = false; cursorW = null; cursorSnap = null; hoverId = null; requestRender(); });
  on(root, "pointerenter", () => { pointerInside = true; });
  on(root, "pointerleave", () => { pointerInside = false; });
  on(root, "pointerdown", () => { lastInside = true; }, true);
  on(document, "pointerdown", (e) => { if (!root.contains(e.target)) lastInside = false; }, true);
  on(window, "keyup", (e) => { if (e.key === " " && spaceDown) { spaceDown = false; requestRender(); } });
  on(window, "blur", () => { if (spaceDown) { spaceDown = false; requestRender(); } });

  toolBtns.forEach((b) => on(b, "click", () => { setTool(b.dataset.tool); b.blur(); }));
  intentBtns.forEach((b) => on(b, "click", () => { store.set({ intent: b.dataset.intent }); b.blur(); }));
  on(fitBtn, "click", () => { fit(); fitBtn.blur(); });
  on(closeBtn, "click", () => store.set({ activeSectionId: null }));
  on(snapBtn, "click", () => { snapOn = !snapOn; syncUI(); snapBtn.blur(); });
  on(clipBtn, "click", () => {
    const it = activeItem();
    if (it) store.updateItem(it.id, { clip: !it.clip });
    clipBtn.blur();
  });

  // 位置: 操作の始まりで 1 回だけ checkpoint し、途中は履歴に積まない
  function setOffset(v) {
    const it = activeItem();
    if (!it || !Number.isFinite(v)) return;
    if (!offsetEditing) { store.checkpoint(); offsetEditing = true; }
    store.updateItem(it.id, { offset: v }, { history: false });
  }
  on(offsetNum, "input", () => { setOffset(parseFloat(offsetNum.value)); });
  on(offsetNum, "change", () => { offsetEditing = false; });
  on(offsetNum, "blur", () => { offsetEditing = false; syncUI(); });
  on(offsetNum, "keydown", (e) => { e.stopPropagation(); if (e.key === "Enter") offsetNum.blur(); });
  on(offsetRange, "input", () => { setOffset(parseFloat(offsetRange.value)); });
  on(offsetRange, "change", () => { offsetEditing = false; offsetRange.blur(); });

  // 小パネル
  popDots.forEach((b) => on(b, "click", () => {
    if (selection.length === 1) patchShape(selection[0], { intent: b.dataset.intent });
    b.blur();
  }));
  on(popDel, "click", () => { deleteSelection(); popDel.blur(); });
  on(popNote, "input", () => {
    if (selection.length !== 1) return;
    if (!noteEditing) { store.checkpoint(); noteEditing = true; }
    patchShape(selection[0], { note: popNote.value }, false);
  });
  on(popNote, "blur", () => { noteEditing = false; });
  on(popNote, "keydown", (e) => { e.stopPropagation(); if (e.key === "Enter" || e.key === "Escape") popNote.blur(); });

  function onLoops(p) {
    if (!p || !p.id) return;
    const loops = prepareLoops(p.loops);
    const ghost = prepareLoops(p.ghostLoops);
    const a = loopPathD(loops), g = loopPathD(ghost);
    cache.set(p.id, { loops, ghostLoops: ghost, bounds: p.bounds || null, fillD: a.fill, strokeD: a.stroke, ghostD: g.stroke });
    if (pendingFit === p.id && p.id === activeId()) { pendingFit = null; fitted.add(p.id); fit(); }
    requestRender();
  }

  function onActiveChanged() {
    selection = [];
    hoverId = null;
    gesture = null;
    curveDraft = null;
    cursorSnap = null;
    closeTextEl();
    pendingFit = null;
    const id = activeId();
    if (id && activeItem() && !fitted.has(id)) {
      if (cache.has(id)) { fitted.add(id); fit(); } else pendingFit = id; // 輪郭が届いたら onLoops で全体表示
    }
    syncUI();
    requestRender();
  }

  disposers.push(store.on("section:loops", onLoops));
  disposers.push(store.on("items", () => {
    const ids = new Set(shapesOf().map((s) => s.id));
    selection = selection.filter((i) => ids.has(i));
    if (hoverId && !ids.has(hoverId)) hoverId = null;
    syncUI();
    requestRender();
  }));
  disposers.push(store.on("change:activeSectionId", onActiveChanged));
  disposers.push(store.on("change:sketchTool", () => { syncUI(); requestRender(); }));
  disposers.push(store.on("change:intent", () => syncUI()));

  let ro = null;
  if (typeof ResizeObserver !== "undefined") { ro = new ResizeObserver(() => resize()); ro.observe(body); }
  on(window, "resize", resize);

  function dispose() {
    disposed = true;
    if (raf) cancelAnimationFrame(raf);
    if (ro) ro.disconnect();
    closeTextEl();
    for (const d of disposers.splice(0)) d();
    root.remove();
  }

  resize();
  syncUI();
  if (activeItem()) onActiveChanged();
  requestRender();

  return { fit, resize, exportSVG, exportPNG, handleKey, isFocused, dispose };
}
