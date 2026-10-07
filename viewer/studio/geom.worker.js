// 面の道具のための前処理を、画面を止めずに行う Worker。import 無しの素の JS。
//
// 入力  { id, positions: Float32Array（非 index の三角形。9 個 = 3 頂点 × xyz。モデル座標 mm）, smooth?: boolean }
//       positions は transfer される（呼び出し側は複製を渡すこと）
// 出力  { id, ok: true, triCount, vertCount,
//         triVerts: Int32Array(3T)       溶接後の頂点 id（三角形ごとに 3 個）
//         adjOffsets: Int32Array(T + 1)  隣接三角形の CSR（三角形 t の隣は adj[adjOffsets[t] .. adjOffsets[t + 1]) ）
//         adj: Int32Array
//         normals: Float32Array(3T)      面法線（単位。面積 0 の三角形は 0,0,0）
//         centroids: Float32Array(3T)
//         areas: Float32Array(T)
//         cornerNormals?: Float32Array(9T)  smooth のとき。溶接した頂点ごとの面積加重法線
//         ms }
//       失敗は { id, ok: false, error }
//
// 溶接は位置だけで行う（法線は使わない）。1e-4 mm の格子に丸めて同一視する。
// 辺で共有する三角形が 3 枚以上（非多様体）でも、互いを隣として扱う。

const QUANT = 1e4; // 1 / 1e-4 mm

function pow2AtLeast(n) {
  let c = 1;
  while (c < n) c <<= 1;
  return c;
}

function build(positions, smooth) {
  const t0 = performance.now();
  const triCount = Math.floor(positions.length / 9);
  const N = triCount * 3;

  // --- 溶接 ---
  const cap = pow2AtLeast(Math.max(16, N * 2));
  const mask = cap - 1;
  const table = new Int32Array(cap).fill(-1);
  const qx = new Int32Array(N), qy = new Int32Array(N), qz = new Int32Array(N);
  const triVerts = new Int32Array(N);
  let vertCount = 0;
  for (let i = 0; i < N; i++) {
    const kx = Math.round(positions[i * 3] * QUANT);
    const ky = Math.round(positions[i * 3 + 1] * QUANT);
    const kz = Math.round(positions[i * 3 + 2] * QUANT);
    let h = Math.imul(kx, 73856093) ^ Math.imul(ky, 19349663) ^ Math.imul(kz, 83492791);
    h ^= h >>> 15; h = Math.imul(h, 0x2c1b3c6d); h ^= h >>> 12;
    h &= mask;
    for (;;) {
      const id = table[h];
      if (id < 0) {
        table[h] = vertCount;
        qx[vertCount] = kx; qy[vertCount] = ky; qz[vertCount] = kz;
        triVerts[i] = vertCount++;
        break;
      }
      if (qx[id] === kx && qy[id] === ky && qz[id] === kz) { triVerts[i] = id; break; }
      h = (h + 1) & mask;
    }
  }

  // --- 面法線・重心・面積 ---
  const normals = new Float32Array(N);
  const centroids = new Float32Array(N);
  const areas = new Float32Array(triCount);
  for (let t = 0; t < triCount; t++) {
    const b = t * 9;
    const ax = positions[b], ay = positions[b + 1], az = positions[b + 2];
    const e1x = positions[b + 3] - ax, e1y = positions[b + 4] - ay, e1z = positions[b + 5] - az;
    const e2x = positions[b + 6] - ax, e2y = positions[b + 7] - ay, e2z = positions[b + 8] - az;
    const cx = e1y * e2z - e1z * e2y, cy = e1z * e2x - e1x * e2z, cz = e1x * e2y - e1y * e2x;
    const l = Math.sqrt(cx * cx + cy * cy + cz * cz);
    areas[t] = l * 0.5;
    if (l > 1e-12) { normals[t * 3] = cx / l; normals[t * 3 + 1] = cy / l; normals[t * 3 + 2] = cz / l; }
    centroids[t * 3] = (ax + positions[b + 3] + positions[b + 6]) / 3;
    centroids[t * 3 + 1] = (ay + positions[b + 4] + positions[b + 7]) / 3;
    centroids[t * 3 + 2] = (az + positions[b + 5] + positions[b + 8]) / 3;
  }

  // --- 辺 → 三角形（半辺 h = 3t + e の鎖）---
  const ecap = pow2AtLeast(Math.max(16, N * 2));
  const emask = ecap - 1;
  const etable = new Int32Array(ecap).fill(-1);   // 辺 id
  const eLo = new Int32Array(N), eHi = new Int32Array(N);
  const eHead = new Int32Array(N).fill(-1);
  const eCount = new Int32Array(N);
  const heEdge = new Int32Array(N).fill(-1);       // 半辺 → 辺 id（退化した辺は -1）
  const heNext = new Int32Array(N).fill(-1);
  let edgeCount = 0;
  for (let t = 0; t < triCount; t++) {
    for (let e = 0; e < 3; e++) {
      const a = triVerts[t * 3 + e], b = triVerts[t * 3 + (e + 1) % 3];
      if (a === b) continue;
      const lo = a < b ? a : b, hi = a < b ? b : a;
      let h = Math.imul(lo, 73856093) ^ Math.imul(hi, 19349663);
      h ^= h >>> 15; h = Math.imul(h, 0x2c1b3c6d); h ^= h >>> 12;
      h &= emask;
      let eid;
      for (;;) {
        eid = etable[h];
        if (eid < 0) {
          eid = edgeCount++;
          etable[h] = eid;
          eLo[eid] = lo; eHi[eid] = hi;
          break;
        }
        if (eLo[eid] === lo && eHi[eid] === hi) break;
        h = (h + 1) & emask;
      }
      const he = t * 3 + e;
      heEdge[he] = eid;
      heNext[he] = eHead[eid];
      eHead[eid] = he;
      eCount[eid]++;
    }
  }

  // --- CSR ---
  const adjOffsets = new Int32Array(triCount + 1);
  for (let t = 0; t < triCount; t++) {
    let d = 0;
    for (let e = 0; e < 3; e++) {
      const eid = heEdge[t * 3 + e];
      if (eid >= 0) d += eCount[eid] - 1;
    }
    adjOffsets[t + 1] = adjOffsets[t] + d;
  }
  const adj = new Int32Array(adjOffsets[triCount]);
  for (let t = 0; t < triCount; t++) {
    let p = adjOffsets[t];
    for (let e = 0; e < 3; e++) {
      const he = t * 3 + e;
      const eid = heEdge[he];
      if (eid < 0) continue;
      for (let hh = eHead[eid]; hh >= 0; hh = heNext[hh]) {
        if (hh !== he) adj[p++] = (hh / 3) | 0;
      }
    }
  }

  // --- 滑らかな法線（viewer.json の smoothNormals 用）---
  let cornerNormals = null;
  if (smooth) {
    const vn = new Float32Array(vertCount * 3);
    for (let t = 0; t < triCount; t++) {
      // 面積加重 = 正規化していない外積（面積 × 2 × 法線）を足す
      const w = areas[t];
      const nx = normals[t * 3] * w, ny = normals[t * 3 + 1] * w, nz = normals[t * 3 + 2] * w;
      for (let k = 0; k < 3; k++) {
        const v = triVerts[t * 3 + k] * 3;
        vn[v] += nx; vn[v + 1] += ny; vn[v + 2] += nz;
      }
    }
    cornerNormals = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      const v = triVerts[i] * 3;
      const x = vn[v], y = vn[v + 1], z = vn[v + 2];
      const l = Math.sqrt(x * x + y * y + z * z) || 1;
      cornerNormals[i * 3] = x / l; cornerNormals[i * 3 + 1] = y / l; cornerNormals[i * 3 + 2] = z / l;
    }
  }

  return {
    ok: true, triCount, vertCount, triVerts, adjOffsets, adj, normals, centroids, areas, cornerNormals,
    ms: performance.now() - t0,
  };
}

self.onmessage = (ev) => {
  const { id, positions, smooth } = ev.data;
  try {
    const r = build(positions, !!smooth);
    r.id = id;
    const transfer = [r.triVerts.buffer, r.adjOffsets.buffer, r.adj.buffer, r.normals.buffer, r.centroids.buffer, r.areas.buffer];
    if (r.cornerNormals) transfer.push(r.cornerNormals.buffer);
    self.postMessage(r, transfer);
  } catch (e) {
    self.postMessage({ id, ok: false, error: String((e && e.message) || e) });
  }
};
