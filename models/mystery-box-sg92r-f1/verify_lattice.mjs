// Browser-independent checks of the real workspace routes, served assets and shared JS solver.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createSim, drivePresentation } from '../../viewer/lattice/sim.mjs';
import { posedTransforms } from '../../viewer/lattice/ui-config.mjs';
import { hasWorkspace, workspaceHref } from '../../viewer/shared/workspace.mjs';

const model = 'mystery-box-sg92r-f1';
const build = new URL('./build/', import.meta.url);
const read = async name => JSON.parse(await fs.readFile(new URL(name, build), 'utf8'));
const source = JSON.parse(await fs.readFile(new URL(`../../viewer/lattice/assets/${model}.json`, import.meta.url), 'utf8'));
const report = { model, pass: false, browserRendered: false, routes: [], faces: {} };
for (const mode of ['physics', 'assembly']) {
  assert.equal(hasWorkspace(mode, model), true);
  const href = workspaceHref(mode, model);
  assert.ok(href.includes(`model=${model}`));
  assert.ok(href.includes(`mode=${mode}`));
  const response = await fetch(new URL(href, 'http://localhost:3000'));
  assert.equal(response.status, 200);
  assert.match(await response.text(), /lattice\.mjs/);
  report.routes.push({ mode, href, status: response.status });
}
const response = await fetch(`http://localhost:3000/viewer/lattice/assets/${model}.json`);
assert.equal(response.status, 200);
const data = await response.json();
assert.deepEqual(data, source);
assert.equal(data.model, model);
const cases = await read('cases.json');
const rootGate = await read('gate_report.json');
let gatesPass = rootGate.pass === true;
assert.equal(data.sim.composition.fresh, true);
assert.equal(data.sim.driveGeometry.sourceHashesFresh, true);
assert.deepEqual(Object.keys(data.sim.faceReports).sort(), cases.models.map(id => id.split('/').at(-1)).sort());
for (const id of cases.models) {
  const slot = id.split('/').at(-1);
  const gate = await read(`../checks/${slot}/build/gate_report.json`);
  const evidence = data.sim.faceReports[slot].gate;
  assert.equal(evidence.fresh, true);
  assert.equal(evidence.status, gate.pass ? 'pass' : 'fail');
  assert.deepEqual(evidence.checks, Object.fromEntries(gate.checks.map(row => [row.id, row])));
  gatesPass &&= gate.pass === true;
}
const printCheck = rootGate.checks.find(row => row.id === 'print.slice');
const printDisplay = data.drive.calibration.find(row => row.id === 'print.slice');
assert.equal(printDisplay.pass, printCheck.pass);
assert.equal(printDisplay.detail, printCheck.summary);
const expectedPlayback = gatesPass && data.sim.contract.pass && data.sim.calibration.every(row => row.pass);
assert.equal(drivePresentation(data.drive, data.sim).calculationPass, expectedPlayback);
report.gatesPass = gatesPass;
report.rootBlocking = rootGate.blocking;
report.physicsControlsDisabled = !expectedPlayback;
assert.equal(data.assembly.pass, true);
assert.equal(data.assembly.calibration.pass, true);
assert.ok(data.assembly.steps.every(step => step.report.pass && step.report.samples > 0));
for (const [slot, face] of Object.entries(data.sim.faceReports)) {
  const tables = await read(`lattice_cases/${slot}/sim_tables.json`);
  const sim = createSim(tables);
  let error = 0;
  for (const expected of face.calculation.runs) {
    const actual = sim.run({ from: expected.fromDeg, to: expected.toDeg });
    assert.equal(actual.trace.length, expected.trace.length);
    for (let n = 0; n < actual.trace.length; n++) {
      for (const key of ['t', 'servoDeg', 'commandDeg', 'torqueNm'])
        error = Math.max(error, Math.abs(actual.trace[n][key] - expected.trace[n][key]));
      for (let k = 0; k < tables.groups.length; k++)
        error = Math.max(error, Math.abs(actual.trace[n].liftsMm[k] - expected.trace[n].liftsMm[k]));
    }
    assert.ok(Math.abs(actual.final.servoDeg - expected.toDeg) < 1);
  }
  assert.ok(error < 1e-7, `${slot}: Python/JS mismatch ${error}`);
  report.faces[slot] = { groups: tables.groups.length, rows: tables.rows.length, maximumPythonJsError: error };
}
// Verify that live playback moves the representative parts and holds other faces closed.
const rep = data.sim.representativeSlot;
let representativeMoves = false;
for (const frame of data.motion.frames) {
  const transforms = posedTransforms(data.motion.frames, { servoDeg: frame.servo_deg }, data.ui, data.simTables.groups);
  for (const part of data.parts) {
    const expected = frame.transforms[part.id];
    assert.ok(expected);
    transforms[part.id].forEach((value, index) => assert.ok(Math.abs(value - expected[index]) < 1e-6));
    const identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
    const moving = expected.some((value, index) => Math.abs(value - identity[index]) > 1e-8);
    if (part.id.startsWith(`${rep}/`)) representativeMoves ||= moving;
    else assert.equal(moving, false, `${part.id} moved in representative playback`);
  }
}
assert.equal(representativeMoves, true);
const stale = structuredClone(data.sim);
stale.driveGeometry.sourceHashesFresh = false;
assert.equal(drivePresentation(data.drive, stale).calculationPass, false);
report.parts = data.parts.length;
report.assemblySteps = data.assembly.steps.length;
report.staleEvidenceDisablesPlayback = true;
// pass means the served data and controls agree with the measured result,
// including a disabled replay when an actual gate failed. It is not certification.
report.pass = true;
const target = new URL('lattice_verification.json', build);
const temporary = fileURLToPath(target) + '.tmp';
await fs.writeFile(temporary, JSON.stringify(report, null, 1) + '\n', 'utf8');
await fs.rename(temporary, target);
console.log(JSON.stringify(report));
