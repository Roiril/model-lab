// node viewer/studio/slice.test.mjs
// 断面の輪郭が正しいかを数値で確かめる。
//  1. 合成した直方体・中空の箱・八面体（頂点が平面ちょうどに載る）で、幅・面積・閉じ方を厳密に
//  2. exports/ の実在する STL で、メッシュの体積（発散定理）と断面積の積分が一致するか
//  3. 109 万三角形の STL を全三角形で切った時間（BVH 無しの総当たり = 上限値）
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { makePlane, uvToModel } from "./frames.js";
import { slicePositions, loopsBounds, loopArea, loopSignedArea } from "./slice.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const exportsDir = path.resolve(here, "../../exports");

let pass = 0, fail = 0;
function ok(cond, name, detail = "") {
  if (cond) { pass++; console.log(`OK   ${name}`); }
  else { fail++; console.log(`FAIL ${name} ${detail}`); }
}
const near = (a, b, e = 1e-6) => Math.abs(a - b) <= e;

// --- 合成メッシュ ---------------------------------------------------------
// 直方体 [x0,x1]×[y0,y1]×[z0,z1]。面は外向き CCW。inward=true で内向き（空洞用）
function boxTris(x0, y0, z0, x1, y1, z1, inward = false) {
  const v = (x, y, z) => [x, y, z];
  const p = [
    v(x0, y0, z0), v(x1, y0, z0), v(x1, y1, z0), v(x0, y1, z0),
    v(x0, y0, z1), v(x1, y0, z1), v(x1, y1, z1), v(x0, y1, z1),
  ];
  const quads = [
    [0, 3, 2, 1], // -z
    [4, 5, 6, 7], // +z
    [0, 1, 5, 4], // -y
    [2, 3, 7, 6], // +y
    [1, 2, 6, 5], // +x
    [3, 0, 4, 7], // -x
  ];
  const tris = [];
  for (const [a, b, c, d] of quads) {
    tris.push([p[a], p[b], p[c]], [p[a], p[c], p[d]]);
  }
  return inward ? tris.map(([a, b, c]) => [a, c, b]) : tris;
}
function toPositions(tris) {
  const f = new Float32Array(tris.length * 9);
  tris.forEach((t, i) => t.forEach((p, k) => f.set(p, i * 9 + k * 3)));
  return f;
}
const loopWidths = (loops) => {
  const b = loopsBounds(loops);
  return b ? [b.max[0] - b.min[0], b.max[1] - b.min[1]] : [0, 0];
};

// 1-a. 直方体の幅
{
  const X0 = 5, Y0 = -3, Z0 = 2, W = 10, D = 20, H = 30;
  const pos = toPositions(boxTris(X0, Y0, Z0, X0 + W, Y0 + D, Z0 + H));
  const cases = [
    { axis: "x", at: X0 + W / 2, want: [D, H] },   // u = Y, v = Z
    { axis: "y", at: Y0 + D / 2, want: [W, H] },   // u = X, v = Z
    { axis: "z", at: Z0 + H / 2, want: [W, D] },   // u = X, v = Y
  ];
  for (const c of cases) {
    const point = [0, 0, 0]; point["xyz".indexOf(c.axis)] = c.at;
    const plane = makePlane(c.axis, point, null);
    // 面の位置 = 法線方向の座標。y 面は normal=-Y なので offset の符号に注意して、
    // 原点基準の点 point を通る面を origin に作ってある（makePlane が正しければ offset 0）
    const loops = slicePositions(pos, null, plane, 0, 1);
    const [w, h] = loopWidths(loops);
    ok(loops.length === 1 && loops[0].closed, `直方体 ${c.axis} 面: 輪郭 1 本・閉じている`, `本数 ${loops.length}`);
    ok(near(w, c.want[0]) && near(h, c.want[1]), `直方体 ${c.axis} 面: 幅 ${c.want[0]} × ${c.want[1]}`, `実際 ${w} × ${h}`);
    ok(near(loopArea(loops[0].points), c.want[0] * c.want[1]), `直方体 ${c.axis} 面: 面積`, String(loopArea(loops[0].points)));
    // 輪郭の点をモデル座標へ戻すと、全部が切断面の上
    const onPlane = loops[0].points.every((q) => near(uvToModel(plane, 0, q)["xyz".indexOf(c.axis)], c.at, 1e-5));
    ok(onPlane, `直方体 ${c.axis} 面: 輪郭が切断面の上にある`);
  }
  // offset
  const plane = makePlane("z", [0, 0, Z0 + 1], null);
  const l1 = slicePositions(pos, null, plane, 0, 1);
  const l2 = slicePositions(pos, null, plane, 7, 1);
  ok(l1.length === 1 && l2.length === 1 && near(loopArea(l2[0].points), W * D), "offset を動かしても同じ断面（直方体）");
  const l3 = slicePositions(pos, null, plane, H + 5, 1);   // 立体の外
  ok(l3.length === 0, "立体の外では輪郭なし");
  // 立体の側面に沿った面（x = X0 + W ちょうど）でも壊れない
  const edge = slicePositions(pos, null, makePlane("x", [X0 + W, 0, 0], null), 0, 1);
  ok(edge.every((l) => l.closed), "面ちょうど（x = 右面）で例外なし・閉じた輪郭のみ", `本数 ${edge.length}`);
  // triIds
  const some = slicePositions(pos, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], plane, 0, 1);
  ok(some.length === 1 && some[0].closed, "triIds に全三角形を渡しても同じ");
  const none = slicePositions(pos, [], plane, 0, 1);
  ok(none.length === 0, "triIds が空なら輪郭なし");
}

// 1-b. 中空の箱（外 10×20×30、空洞 6×16×26）: 外周 + 内周の 2 本
{
  const pos = toPositions([
    ...boxTris(0, 0, 0, 10, 20, 30),
    ...boxTris(2, 2, 2, 8, 18, 28, true),
  ]);
  const plane = makePlane("z", [0, 0, 15], null);
  const loops = slicePositions(pos, null, plane, 0, 1);
  ok(loops.length === 2 && loops.every((l) => l.closed), "中空の箱: 輪郭 2 本・どちらも閉じている", `本数 ${loops.length}`);
  const areas = loops.map((l) => loopArea(l.points)).sort((a, b) => b - a);
  ok(near(areas[0], 200) && near(areas[1], 96), "中空の箱: 外周 200 / 内周 96", JSON.stringify(areas));
  ok(near(areas[0] - areas[1], 104), "中空の箱: 材料の面積 = 外 - 内 = 104");
  const signed = loops.map((l) => loopSignedArea(l.points)).sort((a, b) => b - a);
  ok(near(signed[0], 200) && near(signed[1], -96), "中空の箱: 外周は反時計回り(+200)、穴は時計回り(-96)", JSON.stringify(signed));
  ok(near(loops.reduce((s, l) => s + loopSignedArea(l.points), 0), 104), "中空の箱: 符号つき面積の合計 = 材料の面積");
}

// 1-b2. 向きは 3 軸すべてで外周が反時計回り（平面の normal 側から見て）
{
  const pos = toPositions(boxTris(0, 0, 0, 10, 20, 30));
  for (const [axis, c] of [["x", [5, 0, 0]], ["y", [0, 10, 0]], ["z", [0, 0, 15]]]) {
    const loops = slicePositions(pos, null, makePlane(axis, c, null), 0, 1);
    ok(loops.length === 1 && loopSignedArea(loops[0].points) > 0, `直方体 ${axis} 面: 外周は反時計回り（符号つき面積が正）`);
  }
}

// 1-c. 八面体: 赤道の 4 頂点が平面ちょうどに載る
{
  const r = 7;
  const P = { px: [r, 0, 0], nx: [-r, 0, 0], py: [0, r, 0], ny: [0, -r, 0], pz: [0, 0, r], nz: [0, 0, -r] };
  const tris = [];
  for (const [a, b] of [["px", "py"], ["py", "nx"], ["nx", "ny"], ["ny", "px"]]) {
    tris.push([P[a], P[b], P.pz]);
    tris.push([P[b], P[a], P.nz]);
  }
  const pos = toPositions(tris);
  const loops = slicePositions(pos, null, makePlane("z", [0, 0, 0], null), 0, 1);
  ok(loops.length === 1 && loops[0].closed, "八面体 赤道（頂点が面の上）: 1 本・閉じている", `本数 ${loops.length}`);
  ok(loops[0] && near(loopArea(loops[0].points), 2 * r * r), "八面体 赤道: 面積 2r²", loops[0] ? String(loopArea(loops[0].points)) : "");
  ok(loops[0] && loops[0].points.length === 4, "八面体 赤道: 点は 4 個（重複なし）", loops[0] ? String(loops[0].points.length) : "");
  // 頂点を通る縦の面（x = 0 は py, ny, pz, nz を通る）
  const vert = slicePositions(pos, null, makePlane("x", [0, 0, 0], null), 0, 1);
  ok(vert.length === 1 && vert[0].closed && near(loopArea(vert[0].points), 2 * r * r), "八面体 縦断（4 頂点が面の上）", `本数 ${vert.length}`);
  // 頂点の少し上下
  const up = slicePositions(pos, null, makePlane("z", [0, 0, 2], null), 0, 1);
  ok(up.length === 1 && near(loopArea(up[0].points), 2 * (r - 2) * (r - 2)), "八面体 z=2: 面積 2(r-2)²", up[0] ? String(loopArea(up[0].points)) : "");
}

// 1-d. scale（STL が m 単位のとき）
{
  const pos = toPositions(boxTris(0, 0, 0, 0.01, 0.02, 0.03));
  const loops = slicePositions(pos, null, makePlane("z", [0, 0, 15], null), 0, 1000);
  const [w, h] = loopWidths(loops);
  ok(loops.length === 1 && near(w, 10, 1e-4) && near(h, 20, 1e-4), "scale=1000: m の STL を mm の面で切る", `${w} × ${h}`);
}

// --- STL を読む -----------------------------------------------------------
function readSTL(file) {
  const buf = fs.readFileSync(file);
  const n = buf.readUInt32LE(80);
  if (buf.length !== 84 + n * 50) throw new Error(`バイナリ STL ではない: ${file}`);
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  const pos = new Float32Array(n * 9);
  for (let i = 0; i < n; i++) {
    const o = 84 + i * 50 + 12;
    for (let k = 0; k < 9; k++) pos[i * 9 + k] = dv.getFloat32(o + k * 4, true);
  }
  return pos;
}
function bboxOf(pos) {
  const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < pos.length; i += 3) {
    for (let k = 0; k < 3; k++) {
      const x = pos[i + k];
      if (x < min[k]) min[k] = x;
      if (x > max[k]) max[k] = x;
    }
  }
  return { min, max };
}
// 符号つき体積（発散定理）
function meshVolume(pos) {
  let vol = 0;
  for (let i = 0; i < pos.length; i += 9) {
    const ax = pos[i], ay = pos[i + 1], az = pos[i + 2];
    const bx = pos[i + 3], by = pos[i + 4], bz = pos[i + 5];
    const cx = pos[i + 6], cy = pos[i + 7], cz = pos[i + 8];
    vol += (ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx)) / 6;
  }
  return vol;
}
// 辺がちょうど 2 枚の三角形に共有されるか（位置で溶接）
function isWatertight(pos, sc = 1) {
  const ids = new Map();
  const vid = (i) => {
    const k = `${Math.round(pos[i] * sc * 1e4)},${Math.round(pos[i + 1] * sc * 1e4)},${Math.round(pos[i + 2] * sc * 1e4)}`;
    let id = ids.get(k);
    if (id === undefined) { id = ids.size; ids.set(k, id); }
    return id;
  };
  const edges = new Map();
  for (let t = 0; t < pos.length / 9; t++) {
    const v = [vid(t * 9), vid(t * 9 + 3), vid(t * 9 + 6)];
    for (let e = 0; e < 3; e++) {
      const a = v[e], b = v[(e + 1) % 3];
      if (a === b) continue;
      const k = a < b ? a * 4294967296 + b : b * 4294967296 + a;
      edges.set(k, (edges.get(k) || 0) + 1);
    }
  }
  for (const c of edges.values()) if (c !== 2) return false;
  return true;
}
// 材料の面積 = 符号つき面積の合計（外周は正、穴は負。slice.js が向きを揃える）
function materialArea(loops) {
  return loops.reduce((sum, l) => sum + loopSignedArea(l.points), 0);
}

// --- 2. 実在の STL: 体積 = 断面積の積分 -----------------------------------
// exports/ の三角形が少ないものから、閉じたメッシュ（水密）を最大 4 つ選ぶ
function candidates() {
  return fs.readdirSync(exportsDir)
    .filter((f) => f.endsWith(".stl") && !f.startsWith("_"))
    .map((f) => ({ f, size: fs.statSync(path.join(exportsDir, f)).size }))
    .filter((x) => x.size > 3000 && x.size < 3_000_000)
    .sort((a, b) => b.size - a.size);
}
// STL の単位の推定（viewport.js と同じ規則: bbox の最大寸法が 2 未満なら m）
function unitScaleOf(pos) {
  const bb = bboxOf(pos);
  return Math.max(...bb.max.map((x, i) => x - bb.min[i])) < 2 ? 1000 : 1;
}
function integrate(pos, axis, slices, scale) {
  const bb = bboxOf(pos);
  const k = "xyz".indexOf(axis);
  const lo = bb.min[k] * scale, hi = bb.max[k] * scale;
  let vol = 0, closedAll = true, maxLoops = 0;
  for (let i = 0; i < slices; i++) {
    const z = lo + ((i + 0.5) / slices) * (hi - lo);
    const point = [0, 0, 0]; point[k] = axis === "y" ? z : z;
    const plane = makePlane(axis, point, null);
    // y 面は normal = -Y。origin は point の法線成分なので、面は y = z を通る（offset 0）
    const loops = slicePositions(pos, null, plane, 0, scale);
    for (const l of loops) if (!l.closed) closedAll = false;
    maxLoops = Math.max(maxLoops, loops.length);
    vol += materialArea(loops) * ((hi - lo) / slices);
  }
  return { vol, closedAll, maxLoops };
}
{
  let used = 0;
  const tried = [];
  for (const { f } of candidates()) {
    if (used >= 4) break;
    const pos = readSTL(path.join(exportsDir, f));
    const tri = pos.length / 9;
    if (tri > 200_000) continue;
    if (!isWatertight(pos, unitScaleOf(pos))) { tried.push(`${f}(水密でない)`); continue; }
    const sc = unitScaleOf(pos);
    const truth = meshVolume(pos) * sc ** 3;
    if (truth <= 0) { tried.push(`${f}(体積が負)`); continue; }
    used++;
    for (const axis of ["x", "y", "z"]) {
      const r = integrate(pos, axis, 400, sc);
      const rel = Math.abs(r.vol - truth) / truth;
      ok(r.closedAll, `${f} ${axis} 軸 400 枚: 全輪郭が閉じている`);
      ok(rel < 0.01, `${f} ${axis} 軸: 断面積の積分 = メッシュ体積（誤差 ${(rel * 100).toFixed(3)}%, 単位 x${sc}）`,
        `積分 ${r.vol.toFixed(2)} / 体積 ${truth.toFixed(2)} mm³ 三角形 ${tri}`);
    }
  }
  ok(used >= 2, `水密な実 STL を 2 つ以上確かめた（${used} 個）`, tried.join(", "));
}

// --- 3. 109 万三角形を全部切る ---------------------------------------------
{
  const file = path.join(exportsDir, "laptop-stand-ribbon.stl");
  if (!fs.existsSync(file)) {
    console.log("SKIP laptop-stand-ribbon.stl が無い");
  } else {
    let t0 = performance.now();
    const pos = readSTL(file);
    const readMs = performance.now() - t0;
    const tri = pos.length / 9;
    const bb = bboxOf(pos);
    console.log(`INFO ribbon: ${tri} 三角形 読み込み ${readMs.toFixed(0)} ms bbox ${JSON.stringify(bb.min.map((x) => +x.toFixed(2)))} → ${JSON.stringify(bb.max.map((x) => +x.toFixed(2)))}`);
    const times = [];
    for (const axis of ["x", "y", "z"]) {
      const k = "xyz".indexOf(axis);
      const mid = (bb.min[k] + bb.max[k]) / 2;
      const point = [0, 0, 0]; point[k] = mid;
      const plane = makePlane(axis, point, null);
      t0 = performance.now();
      const loops = slicePositions(pos, null, plane, 0, 1);
      const ms = performance.now() - t0;
      times.push(ms);
      const b = loopsBounds(loops);
      const npts = loops.reduce((s, l) => s + l.points.length, 0);
      console.log(`INFO ribbon ${axis}=${mid.toFixed(2)}: ${ms.toFixed(0)} ms / 輪郭 ${loops.length} 本 / 点 ${npts} / 閉 ${loops.filter((l) => l.closed).length}`);
      ok(loops.length > 0, `ribbon ${axis} 面: 輪郭が出る`);
      ok(loops.every((l) => l.closed), `ribbon ${axis} 面: 全部閉じている`, `開 ${loops.filter((l) => !l.closed).length}`);
      // 輪郭の範囲はモデルの範囲に収まる（u, v の軸に対応する範囲）
      const U = plane.u, V = plane.v;
      const ui = U.findIndex((x) => x === 1), vi = V.findIndex((x) => x === 1);
      const within = b.min[0] >= bb.min[ui] - 1e-3 && b.max[0] <= bb.max[ui] + 1e-3
        && b.min[1] >= bb.min[vi] - 1e-3 && b.max[1] <= bb.max[vi] + 1e-3;
      ok(within, `ribbon ${axis} 面: 輪郭がモデルの範囲に収まる`, JSON.stringify(b));
    }
    console.log(`INFO ribbon 全三角形の総当たり 3 回: ${times.map((x) => x.toFixed(0)).join(" / ")} ms（最大 ${Math.max(...times).toFixed(0)} ms）`);
    // 断面積の積分 = 体積（水密なら）
    const wt = isWatertight(pos);
    console.log(`INFO ribbon 水密: ${wt}`);
    if (wt) {
      const truth = meshVolume(pos);
      t0 = performance.now();
      const r = integrate(pos, "z", 60, 1);
      const rel = Math.abs(r.vol - truth) / truth;
      console.log(`INFO ribbon z 軸 60 枚の積分 ${r.vol.toFixed(0)} / 体積 ${truth.toFixed(0)} mm³ 誤差 ${(rel * 100).toFixed(2)}% (${(performance.now() - t0).toFixed(0)} ms)`);
      ok(rel < 0.03, "ribbon: 断面積の積分 ≈ 体積（60 枚、3% 以内）");
    }
  }
}

console.log(`\n${pass} OK / ${fail} FAIL`);
process.exit(fail ? 1 : 0);
