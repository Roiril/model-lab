// 三角形メッシュを平面で切った輪郭を作る。three 非依存（node でそのままテストできる）。
//
//   slicePositions(positions, triIds, plane, offset, scale) -> [{ points: [[u, v], ...], closed }]
//
// - positions: 非 index の三角形（9 個の数値 = 3 頂点 × xyz ずつ）。STL の生の座標でよい
// - triIds: 切る三角形の番号（Iterable）。null なら全部。BVH で絞った候補を渡す
// - plane: frames.js の { origin, normal, u, v }。実際の切断面は origin + normal * offset
// - scale: positions に掛けるとモデル座標（mm）になる倍率
//
// 輪郭の向き: 材料が進行方向の左側になる向きに揃える（外周は反時計回り、穴は時計回り。
// 平面の normal 側から見て、(u, v) 平面での符号つき面積の合計 = 材料の面積）。
//
// 頂点が平面の上にちょうど載る場合は「平面を法線の逆向きへ無限小ずらした」ものとして扱う
// （s >= 0 を上側とする）。これで頂点を通っても線分が重複せず、閉じたメッシュなら
// 必ず閉じた輪郭になる。平面に完全に載った面は何も出さない（隣の面の縁が輪郭になる）。

import { planeAt, dot } from "./frames.js";

const QUANT = 1e-4;           // 端点をつなぐ量子化の幅（mm）
const INV_QUANT = 1 / QUANT;
const JOIN_TOL = 0.01;        // 開いたままの鎖の端をつなぐ許容（mm）。ほぼ重なった別頂点のずれ吸収用
const KEY_LIMIT = 33554432;   // 2^25。これ以内なら数値キー、超えたら文字列キー

function binKey(ku, kv) {
  if (ku > -KEY_LIMIT && ku < KEY_LIMIT && kv > -KEY_LIMIT && kv < KEY_LIMIT) {
    return (ku + KEY_LIMIT) * 67108864 + (kv + KEY_LIMIT);
  }
  return ku + "," + kv;
}

export function slicePositions(positions, triIds, plane, offset = 0, scale = 1) {
  const at = planeAt(plane, offset);
  const n = at.normal, o = at.origin;
  const U = plane.u, V = plane.v;
  const nx = n[0] * scale, ny = n[1] * scale, nz = n[2] * scale;
  const d0 = dot(n, o);
  const ox = o[0], oy = o[1], oz = o[2];

  // --- 端点（量子化して同一視）---
  const nodeU = [], nodeV = [];
  const bins = new Map();                 // binKey -> node id
  const adj = [];                         // node id -> [segment id]
  const segA = [], segB = [];
  const segSeen = new Set();

  function nodeAt(u, v) {
    const ku = Math.round(u * INV_QUANT), kv = Math.round(v * INV_QUANT);
    let id = bins.get(binKey(ku, kv));
    if (id !== undefined) return id;
    // 量子化の境目をまたいだ近傍も見る（別々の頂点が 1e-4 mm 以内でずれている場合）
    for (let du = -1; du <= 1; du++) {
      for (let dv = -1; dv <= 1; dv++) {
        if (!du && !dv) continue;
        const j = bins.get(binKey(ku + du, kv + dv));
        if (j !== undefined && Math.abs(nodeU[j] - u) < QUANT && Math.abs(nodeV[j] - v) < QUANT) return j;
      }
    }
    id = nodeU.length;
    nodeU.push(u); nodeV.push(v); adj.push([]);
    bins.set(binKey(ku, kv), id);
    return id;
  }

  // 辺 a-b と平面の交点を (u, v) で返す。端点の並びを固定して、隣の三角形から見ても
  // ビットまで同じ値になるようにする
  const out = [0, 0];
  function edgePoint(ax, ay, az, sa, bx, by, bz, sb) {
    if (ax > bx || (ax === bx && (ay > by || (ay === by && az > bz)))) {
      let t;
      t = ax; ax = bx; bx = t; t = ay; ay = by; by = t; t = az; az = bz; bz = t; t = sa; sa = sb; sb = t;
    }
    const t = sa / (sa - sb);
    const px = (ax + (bx - ax) * t) * scale - ox;
    const py = (ay + (by - ay) * t) * scale - oy;
    const pz = (az + (bz - az) * t) * scale - oz;
    out[0] = px * U[0] + py * U[1] + pz * U[2];
    out[1] = px * V[0] + py * V[1] + pz * V[2];
  }

  function addSegment(a, b) {
    if (a === b) return;
    const key = a < b ? a * 4294967296 + b : b * 4294967296 + a;
    if (segSeen.has(key)) return;
    segSeen.add(key);
    const id = segA.length;
    segA.push(a); segB.push(b);
    adj[a].push(id); adj[b].push(id);
  }

  function doTriangle(t) {
    const b = t * 9;
    const x0 = positions[b], y0 = positions[b + 1], z0 = positions[b + 2];
    const x1 = positions[b + 3], y1 = positions[b + 4], z1 = positions[b + 5];
    const x2 = positions[b + 6], y2 = positions[b + 7], z2 = positions[b + 8];
    const s0 = nx * x0 + ny * y0 + nz * z0 - d0;
    const s1 = nx * x1 + ny * y1 + nz * z1 - d0;
    const s2 = nx * x2 + ny * y2 + nz * z2 - d0;
    const a0 = s0 >= 0, a1 = s1 >= 0, a2 = s2 >= 0;
    if (a0 === a1 && a1 === a2) return;
    // 1 つだけ側が違う頂点 = k。残りの 2 頂点との辺が平面と交わる
    let id1, id2;
    if (a0 !== a1 && a0 !== a2) {
      edgePoint(x0, y0, z0, s0, x1, y1, z1, s1); id1 = nodeAt(out[0], out[1]);
      edgePoint(x0, y0, z0, s0, x2, y2, z2, s2); id2 = nodeAt(out[0], out[1]);
    } else if (a1 !== a0 && a1 !== a2) {
      edgePoint(x1, y1, z1, s1, x0, y0, z0, s0); id1 = nodeAt(out[0], out[1]);
      edgePoint(x1, y1, z1, s1, x2, y2, z2, s2); id2 = nodeAt(out[0], out[1]);
    } else {
      edgePoint(x2, y2, z2, s2, x0, y0, z0, s0); id1 = nodeAt(out[0], out[1]);
      edgePoint(x2, y2, z2, s2, x1, y1, z1, s1); id2 = nodeAt(out[0], out[1]);
    }
    // 材料が左側になる向きに（d = n × 三角形の法線 を (u, v) に落として比べる）
    const tx = (y1 - y0) * (z2 - z0) - (z1 - z0) * (y2 - y0);
    const ty = (z1 - z0) * (x2 - x0) - (x1 - x0) * (z2 - z0);
    const tz = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0);
    const dx = n[1] * tz - n[2] * ty, dy = n[2] * tx - n[0] * tz, dz = n[0] * ty - n[1] * tx;
    const du = dx * U[0] + dy * U[1] + dz * U[2];
    const dv = dx * V[0] + dy * V[1] + dz * V[2];
    const eu = nodeU[id2] - nodeU[id1], ev = nodeV[id2] - nodeV[id1];
    if (du * eu + dv * ev >= 0) addSegment(id1, id2); else addSegment(id2, id1);
  }

  if (triIds) {
    for (const t of triIds) doTriangle(t);
  } else {
    const count = Math.floor(positions.length / 9);
    for (let t = 0; t < count; t++) doTriangle(t);
  }

  // --- 線分をつないで輪郭にする ---
  const used = new Uint8Array(segA.length);
  const chains = [];   // { ids: [node id], closed }

  function walk(start) {
    const ids = [start];
    let cur = start, fwd = 0, bwd = 0;
    for (;;) {
      let seg = -1;
      const list = adj[cur];
      for (let i = 0; i < list.length; i++) {
        if (!used[list[i]]) { seg = list[i]; break; }
      }
      if (seg < 0) break;
      used[seg] = 1;
      let next;
      if (segA[seg] === cur) { next = segB[seg]; fwd++; } else { next = segA[seg]; bwd++; }
      ids.push(next);
      cur = next;
      if (cur === start) break;
    }
    const closed = ids.length > 2 && ids[ids.length - 1] === start;
    if (closed) ids.pop();
    if (ids.length < 2) return;
    if (bwd > fwd) ids.reverse();
    chains.push({ ids, closed });
  }

  // 開いた鎖は端（次数 1）から辿る。それ以外は閉じた輪になる
  for (let i = 0; i < adj.length; i++) {
    if (adj[i].length === 1 && !used[adj[i][0]]) walk(i);
  }
  for (let s = 0; s < segA.length; s++) {
    if (!used[s]) walk(segA[s]);
  }

  joinOpenChains(chains, nodeU, nodeV);

  return chains.map((c) => ({ points: c.ids.map((i) => [nodeU[i], nodeV[i]]), closed: c.closed }));
}

// 開いたままの鎖の端どうしが JOIN_TOL 以内なら、つないで 1 本にする（同じ鎖の両端なら閉じる）。
// ほぼ同じ位置の別頂点（溶接されていない STL）で、交点がわずかにずれた時の後始末
function joinOpenChains(chains, nodeU, nodeV) {
  const dist = (a, b) => Math.hypot(nodeU[a] - nodeU[b], nodeV[a] - nodeV[b]);
  for (;;) {
    const open = [];
    chains.forEach((c, idx) => { if (!c.closed) open.push(idx); });
    if (!open.length) return;
    let best = null, bestD = JOIN_TOL;
    for (let a = 0; a < open.length; a++) {
      const ca = chains[open[a]];
      const aEnds = [ca.ids[0], ca.ids[ca.ids.length - 1]];
      for (let b = a; b < open.length; b++) {
        const cb = chains[open[b]];
        const bEnds = [cb.ids[0], cb.ids[cb.ids.length - 1]];
        for (let ea = 0; ea < 2; ea++) {
          for (let eb = 0; eb < 2; eb++) {
            if (a === b && ea >= eb) continue;               // 同じ鎖は 先頭-末尾 の 1 通りだけ
            const d = dist(aEnds[ea], bEnds[eb]);
            if (d < bestD) { bestD = d; best = { a: open[a], b: open[b], ea, eb }; }
          }
        }
      }
    }
    if (!best) return;
    const ca = chains[best.a];
    if (best.a === best.b) {
      if (ca.ids.length > 2) ca.closed = true;
      else chains.splice(best.a, 1);                         // 2 点だけの鎖が閉じる = 退化。捨てる
      continue;
    }
    const cb = chains[best.b];
    // ca の末尾 と cb の先頭 が隣り合う形に並べて連結
    const A = best.ea === 1 ? ca.ids : ca.ids.slice().reverse();
    const B = best.eb === 0 ? cb.ids : cb.ids.slice().reverse();
    ca.ids = A.concat(B);
    chains.splice(best.b, 1);
  }
}

// 輪郭の範囲 { min:[u,v], max:[u,v] }。無ければ null
export function loopsBounds(loops) {
  let u0 = Infinity, v0 = Infinity, u1 = -Infinity, v1 = -Infinity;
  for (const l of loops) {
    for (const [u, v] of l.points) {
      if (u < u0) u0 = u; if (u > u1) u1 = u;
      if (v < v0) v0 = v; if (v > v1) v1 = v;
    }
  }
  return u0 === Infinity ? null : { min: [u0, v0], max: [u1, v1] };
}

// 輪郭の符号つき面積（シューレース）。反時計回りが正 = 外周、時計回りが負 = 穴
export function loopSignedArea(points) {
  let a = 0;
  for (let i = 0, n = points.length; i < n; i++) {
    const p = points[i], q = points[(i + 1) % n];
    a += p[0] * q[1] - q[0] * p[1];
  }
  return a / 2;
}

// 輪郭の符号なし面積
export function loopArea(points) {
  return Math.abs(loopSignedArea(points));
}
