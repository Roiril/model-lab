import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { boundaryCrossingSpeedMmS, createSim } from "./sim.mjs";

const root = new URL("../../", import.meta.url);
const models = ["mystery-box-sg92r-c3", "mystery-box-sg92r-c4"];
const close = (actual, expected, tolerance, label) =>
  assert.ok(Math.abs(actual - expected) <= tolerance, `${label}: ${actual} vs ${expected}`);

function synthetic(gravityNm = 0, frictionNm = 0) {
  const row = (servoDeg) => ({
    servoDeg, inertiaRestKgm2: 0, inertiaGroupsKgm2: 0, dMGroupsDqKgm2PerRad: 0,
    gravityRestNm: gravityNm, gravityGroupsNm: 0,
    liftsMm: [0], dLiftDqMPerRad: [0], d2LiftDq2MPerRad2: [0],
  });
  return {
    model: "calibration", limitsDeg: [0, 60], duration_s: 0.2,
    contactModel: "gravity_one_sided", groups: [{ id: "cal", label: "cal", massKg: 0.001 }],
    contactBoundariesDeg: [],
    rows: [row(0), row(60)],
    const: {
      stallTorqueNm: 0.245, noLoadSpeedRadS: Math.PI / 0.3,
      controlBandRad: 4 * Math.PI / 180, motorInertiaKgm2: 5e-6,
      servoFrictionNm: frictionNm, gravityMS2: 9.80665,
      dtS: 5e-5, recordS: 0.001, settleS: 0.1, contactToleranceN: 1e-8,
    },
  };
}

// 計器校正。負荷なしの 60° は公称 0.1 秒付近、静荷重の半分とトルク 0 では目標へ届かない。
const noLoad = createSim(synthetic()).run({ from: 0, to: 60, kind: "step", duration: 0.2 });
const reached = noLoad.trace.find((row) => row.servoDeg >= 59)?.t;
assert.ok(reached !== undefined && Math.abs(reached - 0.1) <= 0.02, `no-load speed: ${reached}`);
const required = 0.05;
const half = createSim(synthetic(required)).run({
  from: 0, to: 60, kind: "step", stallScale: required * 0.5 / 0.245, duration: 0.4,
});
assert.ok(half.final.servoDeg < 1, `half static torque reached ${half.final.servoDeg}`);
const zero = createSim(synthetic()).run({ from: 0, to: 60, kind: "step", stallScale: 0, duration: 0.2 });
close(zero.final.servoDeg, 0, 1e-12, "zero torque");
close(boundaryCrossingSpeedMmS(20, 40, 1, 3, [[{ deg: 30, slopeMPerRad: 0.005 }]]),
  10, 1e-12, "synthetic contact boundary");

for (const model of models) {
  const dir = new URL(`models/${model}/build/`, root);
  const tables = JSON.parse(readFileSync(new URL("sim_tables.json", dir), "utf8"));
  const report = JSON.parse(readFileSync(new URL("simulate_report.json", dir), "utf8"));
  const sim = createSim(tables);
  const [low, high] = tables.limitsDeg;
  const scenarios = {
    standard: { from: low, to: high, kind: "ease" },
    reverse: { from: high, to: low, kind: "ease" },
    lowPower: { from: low, to: high, kind: "ease", stallScale: 0.30 },
    heavy: { from: low, to: high, kind: "ease", massScale: 4.0 },
    fullSpeed: { from: low, to: high, kind: "step" },
  };
  assert.equal(sim.groups.length, tables.groups.length);
  assert.equal(sim.at(low - 100).servoDeg, low, `${model}: lower limit`);
  assert.equal(sim.at(high + 100).servoDeg, high, `${model}: upper limit`);
  const clipped = sim.run({ from: low - 100, to: high + 100, kind: "ease", duration: 0.01 });
  assert.equal(clipped.clippedToLimits, true, `${model}: range clipping`);
  assert.ok(clipped.trace.every((row) => row.servoDeg >= low - 1e-9 && row.servoDeg <= high + 1e-9));

  for (const [name, options] of Object.entries(scenarios)) {
    const js = sim.run(options), py = report.scenarios[name];
    close(js.final.servoDeg, py.final.servoDeg, 2e-8, `${model}/${name} final servo`);
    close(js.peakTorqueNm, py.peakTorqueNm, 2e-10, `${model}/${name} peak torque`);
    close(js.maxContactSpeedMmS, py.maxContactSpeedMmS, 2e-8, `${model}/${name} contact speed`);
    assert.equal(js.contactFeasible, py.contactFeasible, `${model}/${name} contact feasible`);
    js.final.liftsMm.forEach((value, index) =>
      close(value, py.final.liftsMm[index], 2e-8, `${model}/${name} lift ${index}`));
    assert.deepEqual(Object.keys(js.trace[0]), ["t", "commandDeg", "servoDeg", "torqueNm", "liftsMm"]);
    assert.equal(js.trace.length, py.trace.length, `${model}/${name} trace length`);
    js.trace.forEach((row, traceIndex) => {
      const expected = py.trace[traceIndex];
      for (const key of ["t", "commandDeg", "servoDeg", "torqueNm"])
        close(row[key], expected[key], 2e-8, `${model}/${name} trace ${traceIndex} ${key}`);
      row.liftsMm.forEach((value, liftIndex) =>
        close(value, expected.liftsMm[liftIndex], 2e-8,
          `${model}/${name} trace ${traceIndex} lift ${liftIndex}`));
    });
  }
  const scale = 2.5;
  const middle = sim.at((low + high) / 2);
  close(sim.holdTorque((low + high) / 2, scale),
    middle.gravityRestNm + middle.gravityGroupsNm * scale,
    1e-12, `${model}: hold torque`);
  console.log(`${model}: Python/JS match`, {
    standardFinalDeg: report.scenarios.standard.final.servoDeg,
    peakTorqueNm: report.scenarios.standard.peakTorqueNm,
    contactFeasible: report.scenarios.standard.contactFeasible,
    maxContactSpeedMmS: report.scenarios.standard.maxContactSpeedMmS,
  });
}
