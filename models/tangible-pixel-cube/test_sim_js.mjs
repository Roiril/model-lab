// Python（tools/lattice_simulation.py の TableSim）と JS（viewer/lattice/sim.mjs の createSim）が同じ表で全時刻一致するかを調べる。
//   node --test models/tangible-pixel-cube/test_sim_js.mjs   または   node models/tangible-pixel-cube/test_sim_js.mjs
// 入力: build/sim_tables.json, build/sim_js_reference.json（simulate.py が書く Python の軌跡）
// 出力: build/sim_js_parity.json（simulate.py が校正の結果として読む）
import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createSim } from '../../viewer/lattice/sim.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const build = path.join(here, 'build');
const tablesPath = path.join(build, 'sim_tables.json');
const referencePath = path.join(build, 'sim_js_reference.json');
const parityPath = path.join(build, 'sim_js_parity.json');

const TOL = { t: 1e-9, servoDeg: 1e-6, commandDeg: 1e-6, torqueNm: 1e-9, liftsMm: 1e-6, scalar: 1e-6 };

const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const sha256 = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const absDiff = (a, b) => Math.abs(Number(a) - Number(b));

function compareRun(sim, ref) {
  const js = sim.run(ref.args);
  const out = { name: ref.name, points: ref.trace.length, jsPoints: js.trace.length, ok: true, problems: [] };
  const maxima = { t: 0, servoDeg: 0, commandDeg: 0, torqueNm: 0, liftsMm: 0 };
  if (js.trace.length !== ref.trace.length) {
    out.ok = false;
    out.problems.push(`軌跡の長さが違う（Python ${ref.trace.length}、JS ${js.trace.length}）`);
    return { ...out, maxima };
  }
  ref.trace.forEach((row, index) => {
    const other = js.trace[index];
    for (const key of ['t', 'servoDeg', 'commandDeg', 'torqueNm']) maxima[key] = Math.max(maxima[key], absDiff(row[key], other[key]));
    row.liftsMm.forEach((value, i) => { maxima.liftsMm = Math.max(maxima.liftsMm, absDiff(value, other.liftsMm[i])); });
  });
  for (const key of Object.keys(maxima)) {
    if (!(maxima[key] <= TOL[key])) { out.ok = false; out.problems.push(`${key} の最大差 ${maxima[key]} が許容 ${TOL[key]} を超える`); }
  }
  const scalars = {
    finalServoDeg: [ref.final.servoDeg, js.final.servoDeg],
    finalTorqueNm: [ref.final.torqueNm, js.final.torqueNm],
    peakTorqueNm: [ref.peakTorqueNm, js.peakTorqueNm],
    maxContactSpeedMmS: [ref.maxContactSpeedMmS, js.maxContactSpeedMmS],
    minNormalForceN: [ref.minNormalForceN, js.minNormalForceN],
  };
  out.scalarDiffs = {};
  for (const [key, [a, b]] of Object.entries(scalars)) {
    if (a === null || b === null) {
      if (a !== b) { out.ok = false; out.problems.push(`${key}: Python ${a}、JS ${b}`); }
      continue;
    }
    out.scalarDiffs[key] = absDiff(a, b);
    if (!(out.scalarDiffs[key] <= TOL.scalar)) { out.ok = false; out.problems.push(`${key} の差 ${out.scalarDiffs[key]}`); }
  }
  if (ref.contactFeasible !== js.contactFeasible) { out.ok = false; out.problems.push(`contactFeasible: Python ${ref.contactFeasible}、JS ${js.contactFeasible}`); }
  if (JSON.stringify(ref.possibleLiftOffGroups) !== JSON.stringify(js.possibleLiftOffGroups)) {
    out.ok = false;
    out.problems.push('possibleLiftOffGroups が違う');
  }
  return { ...out, maxima };
}

let result;
try {
  const tables = readJson(tablesPath);
  const reference = readJson(referencePath);
  const sim = createSim(tables);
  const runs = reference.runs.map((ref) => compareRun(sim, ref));
  const shaMatches = reference.tablesSha256 === sha256(tablesPath);
  result = {
    pass: shaMatches && runs.length > 0 && runs.every((run) => run.ok),
    node: process.version, tolerance: TOL, tablesSha256Matches: shaMatches, runs,
  };
} catch (error) {
  result = { pass: false, node: process.version, error: String(error && error.message || error), runs: [] };
}
fs.writeFileSync(`${parityPath}.tmp`, `${JSON.stringify(result, null, 1)}\n`);
fs.renameSync(`${parityPath}.tmp`, parityPath);

test('Python の軌跡の表が現在の sim_tables.json と同じ', () => {
  assert.equal(result.error, undefined, result.error);
  assert.equal(result.tablesSha256Matches, true);
});

for (const run of result.runs) {
  test(`${run.name}: Python と JS の全時刻が一致（${run.points} 点）`, () => {
    assert.deepEqual(run.problems, []);
    assert.equal(run.ok, true);
  });
}

test('createSim: 行の角度ちょうどで表の高さを返す', () => {
  const tables = readJson(tablesPath);
  const sim = createSim(tables);
  for (const index of [0, 1, 100, 320, tables.rows.length - 1]) {
    const row = tables.rows[index];
    const state = sim.at(row.servoDeg);
    state.liftsMm.forEach((value, i) => assert.ok(absDiff(value, row.liftsMm[i]) < 1e-6, `行 ${index} 群 ${i}`));
    assert.ok(absDiff(state.inertiaRestKgm2, row.inertiaRestKgm2) < 1e-15);
  }
});

test('createSim: 停動の 0 倍では目標へ動かない（計器の負例）', () => {
  const tables = readJson(tablesPath);
  const sim = createSim(tables);
  const run = sim.run({ from: tables.limitsDeg[0], to: tables.limitsDeg[1], stallScale: 0 });
  assert.ok(run.final.servoDeg < tables.limitsDeg[1] - 1, `最終 ${run.final.servoDeg}`);
});

test('simulate.py が表を作った記録（parity）が通っている', () => {
  assert.equal(result.pass, true);
});
