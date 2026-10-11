import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import test from 'node:test';

import { createSim } from './sim.mjs';

const viewerDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(viewerDir, '../..');
const simulate = path.join(root, 'models', 'mystery-box-sg92r-c4-2', 'simulate.py');
const buildDir = path.dirname(simulate) + path.sep + 'build';
const process = spawnSync('py', ['-3.11', simulate, '--probe-json'], {
  cwd: root,
  encoding: 'utf8',
  maxBuffer: 32 * 1024 * 1024,
});
assert.equal(process.status, 0, process.stderr);
const probe = JSON.parse(process.stdout);

const readJson = (file) => JSON.parse(readFileSync(file, 'utf8'));
const sha256 = (file) => createHash('sha256').update(readFileSync(file)).digest('hex');

const tolerance = 2e-9;
const close = (actual, expected, label) => {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${label}: ${actual} != ${expected}`);
};

function compareArray(actual, expected, label) {
  assert.equal(actual.length, expected.length, `${label} length`);
  actual.forEach((value, index) => close(value, expected[index], `${label}[${index}]`));
}

function compareState(actual, expected, label) {
  for (const key of [
    'servoDeg', 'inertiaRestKgm2', 'inertiaGroupsKgm2',
    'dMGroupsDqKgm2PerRad', 'gravityRestNm', 'gravityGroupsNm',
    'contactFrictionGroupsNm',
  ]) close(actual[key], expected[key], `${label}.${key}`);
  for (const key of ['liftsMm', 'dLiftDqMPerRad', 'd2LiftDq2MPerRad2']) {
    compareArray(actual[key], expected[key], `${label}.${key}`);
  }
  assert.deepEqual(actual.contactActive, expected.contactActive, `${label}.contactActive`);
}

function compareRun(actual, expected, label) {
  assert.equal(actual.trace.length, expected.trace.length, `${label}.trace length`);
  actual.trace.forEach((row, index) => {
    const reference = expected.trace[index];
    for (const key of ['t', 'commandDeg', 'servoDeg', 'torqueNm']) {
      close(row[key], reference[key], `${label}.trace[${index}].${key}`);
    }
    compareArray(row.liftsMm, reference.liftsMm, `${label}.trace[${index}].liftsMm`);
  });
  for (const key of ['t', 'commandDeg', 'servoDeg', 'torqueNm']) {
    close(actual.final[key], expected.final[key], `${label}.final.${key}`);
  }
  compareArray(actual.final.liftsMm, expected.final.liftsMm, `${label}.final.liftsMm`);
  for (const key of ['peakTorqueNm', 'maxContactSpeedMmS', 'minNormalForceN']) {
    close(actual[key], expected[key], `${label}.${key}`);
  }
  assert.equal(actual.contactFeasible, expected.contactFeasible, `${label}.contactFeasible`);
  assert.deepEqual(actual.possibleLiftOffGroups, expected.possibleLiftOffGroups,
    `${label}.possibleLiftOffGroups`);
}

test('Python tables and browser simulation agree at every recorded time', () => {
  const sim = createSim(probe.tables);
  for (const sample of probe.samples) compareState(sim.at(sample.degree), sample.state, `at(${sample.degree})`);
  const cases = {
    standard: { from: 15, to: 165, kind: 'ease' },
    reverse: { from: 165, to: 15, kind: 'ease' },
    zeroTorque: { from: 15, to: 165, kind: 'ease', stallScale: 0 },
    halfRequired: {
      from: 15,
      to: 165,
      kind: 'ease',
      stallScale: probe.negative.halfRequiredStallScale,
    },
  };
  for (const [id, options] of Object.entries(cases)) {
    compareRun(sim.run(options), probe.runs[id], id);
  }
});

test('five pattern stops keep contact and select the expected dent', () => {
  const sim = createSim(probe.tables);
  const stops = [
    { degree: 15, selected: null },
    { degree: 50, selected: 1 },
    { degree: 90, selected: 0 },
    { degree: 130, selected: 2 },
    { degree: 165, selected: 3 },
  ];
  for (const { degree, selected } of stops) {
    const run = sim.run({ from: 15, to: degree, kind: 'ease' });
    assert.ok(Math.abs(run.final.servoDeg - degree) <= 1, `${degree} degree reached`);
    assert.equal(run.contactFeasible, true, `${degree} degree run contact`);
    const reverse = sim.run({ from: degree, to: 15, kind: 'ease' });
    assert.ok(Math.abs(reverse.final.servoDeg - 15) <= 1, `${degree} degree reverse reached`);
    assert.equal(reverse.contactFeasible, true, `${degree} degree reverse contact`);
    const state = sim.at(degree);
    assert.ok(state.contactActive.every(Boolean), `${degree} degree contact`);
    assert.ok(state.liftsMm.every((value) => value <= tolerance), `${degree} degree nonpositive lifts`);
    if (selected === null) assert.ok(state.liftsMm.every((value) => Math.abs(value) <= tolerance));
    else {
      assert.ok(state.liftsMm[selected] < -3.99, `${degree} degree selected dent`);
      state.liftsMm.forEach((value, index) => {
        if (index !== selected) assert.ok(Math.abs(value) <= tolerance,
          `${degree} degree unselected group ${index}`);
      });
    }
  }
});

test('force shortage is rejected and normal forces stay nonnegative', () => {
  assert.ok(probe.runs.zeroTorque.final.servoDeg < 164);
  assert.ok(probe.runs.halfRequired.final.servoDeg < 164);
  for (const id of ['standard', 'reverse', 'zeroTorque', 'halfRequired']) {
    assert.equal(probe.runs[id].contactFeasible, true, `${id} contact`);
    assert.ok(probe.runs[id].minNormalForceN >= 0, `${id} normal force`);
  }
});

test('dt/2 convergence evidence is reproduced by createSim', () => {
  const base = createSim(probe.tables).run({ from: 15, to: 165, kind: 'ease' });
  const halfTables = structuredClone(probe.tables);
  halfTables.const.dtS /= 2;
  const half = createSim(halfTables).run({ from: 15, to: 165, kind: 'ease' });
  assert.equal(base.trace.length, half.trace.length);
  const differences = {
    finalServoDeg: Math.abs(base.final.servoDeg - half.final.servoDeg),
    maxTraceServoDeg: Math.max(...base.trace.map((row, index) =>
      Math.abs(row.servoDeg - half.trace[index].servoDeg))),
    maxTraceTorqueNm: Math.max(...base.trace.map((row, index) =>
      Math.abs(row.torqueNm - half.trace[index].torqueNm))),
    maxTraceLiftMm: Math.max(...base.trace.flatMap((row, index) =>
      row.liftsMm.map((value, group) => Math.abs(value - half.trace[index].liftsMm[group])))),
    peakTorqueNm: Math.abs(base.peakTorqueNm - half.peakTorqueNm),
    maxContactSpeedMmS: Math.abs(base.maxContactSpeedMmS - half.maxContactSpeedMmS),
  };
  for (const [key, value] of Object.entries(differences)) {
    close(value, probe.convergence.observedAbsoluteDifference[key], `convergence.${key}`);
    assert.ok(value <= probe.convergence.reportedUpperBound[key] + tolerance,
      `convergence bound ${key}`);
  }
});

test('production tables are bound to final STL and accepted drive geometry', () => {
  const tablesFile = path.join(buildDir, 'sim_tables.json');
  const reportFile = path.join(buildDir, 'simulate_report.json');
  const driveFile = path.join(buildDir, 'drive_report.json');
  assert.ok(existsSync(tablesFile), 'final sim_tables.json is required');
  assert.ok(existsSync(reportFile), 'final simulate_report.json is required');
  assert.ok(existsSync(driveFile), 'final drive_report.json is required');

  const tables = readJson(tablesFile);
  const report = readJson(reportFile);
  const drive = readJson(driveFile);
  assert.equal(report.overall.calculationPass, true);
  assert.equal(report.overall.geometryPass, true);
  assert.equal(report.overall.status, 'conditional');
  assert.equal(report.overall.pass, false, 'physical verification remains conditional');
  assert.equal(report.driveGeometry.geometryPass, true);
  assert.equal(report.driveGeometry.sourceHashesFresh, true);
  assert.equal(drive.overall.geometryPass, true);
  assert.equal(report.driveGeometry.driveReportSha256, sha256(driveFile));
  assert.match(report.overall.basis, /接続形状確認済み/);
  assert.deepEqual(tables.sourceHashes, report.sourceHashes);

  for (const [relative, expected] of Object.entries(report.sourceHashes)) {
    const source = path.join(root, ...relative.split('/'));
    assert.ok(existsSync(source), `missing source bound to report: ${relative}`);
    assert.equal(sha256(source), expected, `stale source hash: ${relative}`);
  }
});
