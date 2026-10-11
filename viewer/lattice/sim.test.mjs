import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { boundaryCrossingSpeedMmS, createSim, driveMeasurementDetail, drivePresentation } from "./sim.mjs";

const root = new URL("../../", import.meta.url);
const models = ["mystery-box-sg92r-c3", "mystery-box-sg92r-c4"];
const close = (actual, expected, tolerance, label) =>
  assert.ok(Math.abs(actual - expected) <= tolerance, `${label}: ${actual} vs ${expected}`);
const numericLeaves = value => typeof value === "number" ? [value]
  : Array.isArray(value) ? value.flatMap(numericLeaves)
    : value && typeof value === "object" ? Object.values(value).flatMap(numericLeaves) : [];

function synthetic(gravityNm = 0, frictionNm = 0, contactFrictionNm = 0) {
  const row = (servoDeg) => ({
    servoDeg, inertiaRestKgm2: 0, inertiaGroupsKgm2: 0, dMGroupsDqKgm2PerRad: 0,
    gravityRestNm: gravityNm, gravityGroupsNm: 0,
    contactFrictionGroupsNm: contactFrictionNm,
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
const camFriction = 0.05;
const frictionHalf = createSim(synthetic(0, 0, camFriction)).run({
  from: 0, to: 60, kind: "step", stallScale: camFriction * 0.5 / 0.245, duration: 0.4,
});
assert.ok(frictionHalf.final.servoDeg < 1, `half cam friction reached ${frictionHalf.final.servoDeg}`);
close(boundaryCrossingSpeedMmS(20, 40, 1, 3, [[{ deg: 30, slopeMPerRad: 0.005 }]]),
  10, 1e-12, "synthetic contact boundary");

// 接続が無い負例は、レポート側が誤って geometryPass=true でも表示と計算の両方で落とす。
const missingConnection = drivePresentation({
  overall: { geometryPass: true }, interfaces: [], hardwareUnknown: ["スプライン嵌合"],
}, { overall: { calculationPass: true } });
assert.equal(missingConnection.geometryPass, false);
assert.equal(missingConnection.calculationPass, false);
assert.equal(missingConnection.status, "fail");
assert.match(missingConnection.summary, /接続未成立/);
assert.equal(missingConnection.interfaceRows[0].result, "接続未成立");

const failedConnection = drivePresentation({
  overall: { geometryPass: false },
  interfaces: [{ id: "horn", label: "ホーンと受け", status: "fail", detail: "共通長さなし" }],
}, {
  overall: { calculationPass: true },
  driveGeometry: { geometryPass: false, sourceHashesFresh: true },
});
assert.equal(failedConnection.calculationPass, false);
assert.equal(failedConnection.interfaceRows[0].result, "接続未成立");

const staleDriveSources = drivePresentation({
  overall: { geometryPass: true },
  interfaces: [{ id: "horn", label: "ホーンと受け", status: "pass" }],
}, {
  overall: { calculationPass: true },
  driveGeometry: { geometryPass: true, sourceHashesFresh: false },
});
assert.equal(staleDriveSources.geometryPass, false);
assert.equal(staleDriveSources.calculationPass, false);
assert.equal(staleDriveSources.status, "fail");
assert.match(staleDriveSources.summary, /接続未成立/);

const missingDriveGeometry = drivePresentation({
  overall: { geometryPass: true },
  interfaces: [{ id: "horn", label: "ホーンと受け", status: "pass" }],
}, { overall: { calculationPass: true } });
assert.equal(missingDriveGeometry.geometryPass, false);
assert.equal(missingDriveGeometry.calculationPass, false);

const hardwareConditional = drivePresentation({
  overall: { geometryPass: true },
  interfaces: [{ id: "spline", label: "サーボとホーン", status: "unknown" }],
  hardwareUnknown: ["スプライン嵌合"],
}, {
  overall: { calculationPass: true },
  driveGeometry: { geometryPass: true, sourceHashesFresh: true },
});
assert.equal(hardwareConditional.calculationPass, true);
assert.equal(hardwareConditional.status, "conditional");
assert.equal(hardwareConditional.interfaceRows[0].result, "実機未確認");

assert.match(driveMeasurementDetail({
  id: "shaft-cam", contactAnglesDeg: [1.25, 2.5], nearestGapMm: 0.2,
}), /逆方向の接触角 1.25°。正方向の接触角 2.5°。最小隙間 0.2 mm/);
assert.match(driveMeasurementDetail({
  id: "gear-mesh", actualTeeth: [30, 30], faceWidthOverlapMm: 4,
  minimumRetainedFaceOverlapMm: 2.1, contactRatio: 1.45, maximumTotalAngularPlayDeg: 2.038839,
}), /実歯数 30 \/ 30。歯幅の重なり 4 mm。保持後の最小歯幅重なり 2.1 mm。かみ合い率 1.45。最大自由角 2.038839°/);
assert.match(driveMeasurementDetail({
  id: "servo-seat", nominalEngagementMm: 2.5,
  minimumRetainedEngagementMm: 2, minimumArmEngagementMm: 1.2,
}), /公称差込 2.5 mm。保持後の最小差込 2 mm。ホーン腕の最小差込 1.2 mm/);
const retentionDetail = driveMeasurementDetail({
  id: "retention",
  cases: [{ id: "drive-plus", label: "駆動歯車の前向き抜け止め", maximumTravelMm: 0.375 }],
  axialStack: { totalFreeTravelMm: 0.6 },
});
assert.match(retentionDetail, /駆動歯車の前向き抜け止め 最初に止まるまで最大 0.375 mm。軸方向の総遊び 0.6 mm/);
assert.doesNotMatch(retentionDetail, /drive-plus|axialStack/);
assert.equal(driveMeasurementDetail({ id: "cam-followers", maximumActiveGapMm: 0.007073 }), "最大実隙間 0.007073 mm");
assert.equal(driveMeasurementDetail({
  id: "canonical-reference",
  parts: [
    { maximumVertexDifferenceMm: 0.001, maximumSurfaceDifferenceMm: 0.000002 },
    { maximumVertexDifferenceMm: 0.003, maximumSurfaceDistanceMm: 0.000004 },
  ],
}), "最大実面差 0.000004 mm。最大頂点差 0.003 mm（参考）");
assert.equal(driveMeasurementDetail({
  id: "canonical-reference",
  parts: [{ maximumVertexDifferenceMm: 0.003 }],
}), "最大実面差の記録なし。最大頂点差 0.003 mm（参考）");
assert.doesNotMatch(driveMeasurementDetail({
  id: "servo-seat", nominalEngagementMm: 3,
  minimumRetainedEngagementMm: null, minimumArmEngagementMm: null,
}), /保持後|ホーン腕| 0 mm/);

const evidencePresentation = drivePresentation({
  overall: { geometryPass: true },
  interfaces: [{
    id: "gear-mesh", label: "歯車のかみ合い", status: "pass", actualTeeth: [30, 30],
    faceWidthOverlapMm: 4, minimumRetainedFaceOverlapMm: 2.1,
    contactRatio: 1.45, maximumTotalAngularPlayDeg: 2.038839,
  }],
  calibration: [{ id: "known-gap", label: "既知の隙間", pass: true, detail: "0.2 mmを検出" }],
}, {
  overall: { calculationPass: true },
  driveGeometry: { geometryPass: true, sourceHashesFresh: true },
});
assert.match(evidencePresentation.interfaceRows[0].detail, /30.*4 mm.*2.1 mm.*1.45.*2.038839°/);
assert.deepEqual(evidencePresentation.calibrationRows[0], {
  id: "known-gap", label: "既知の隙間", pass: true, detail: "0.2 mmを検出",
});

const structuredCalibration = drivePresentation({
  calibration: [{
    id: "solid-input-geometry", pass: true,
    detail: { calibrationPass: true, filesChecked: 69, missingFiles: 0,
      invalidClosedSolids: 0, properNonadjacentIntersections: 0 },
  }, {
    id: "canonical-surface", pass: true,
    detail: { sameSurfaceRetriangulatedDistanceMm: 0, sameSurfaceAreaDifferenceMm2: 0,
      missingFaceDistanceMm: 0.23570226039551587, shiftedSurfaceDistanceMm: 0.5,
      skinnyIdenticalDistanceMm: 0, skinnyShiftedDistanceMm: 0.020000000000003126 },
  }, {
    id: "shaft-cap-positive-volume", pass: true,
    detail: { id: "shaft-plus", servoDeg: 15, rotationDeg: 0, travelMm: 0.25,
      direction: [1, 0, 0], sourceStlSha256: { moving: "move-sha", fixed: "fixed-sha" },
      independentSection: { capMaterialStartsXmm: 38.75, shiftedShaftKeyedEndXmm: 38.85,
        constantHexAxialPenetrationMm: 0.1, shaftHexAreaMm2: 21.650635094610966,
        capBore48GonAreaMm2: 12.530514453124951, materialOverlapAreaMm2: 9.120120641486015,
        volumeLowerBoundMm3: 0.9120120641486145 },
      solvers: {
        EXACT: { vertices: 573, faces: 449, nonmanifoldEdges: 0,
          closedBoundaryVolumeMm3: 1.0576445191582586, error: null },
        MANIFOLD: { vertices: 573, faces: 449, nonmanifoldEdges: 0,
          closedBoundaryVolumeMm3: 1.0576428111119105, error: null },
      } },
  }, { id: "future-object", pass: true, detail: { value: 7, range: [1, 2] } }],
}, {});
const [solidDetail, surfaceDetail, shaftDetail, fallbackDetail] =
  structuredCalibration.calibrationRows.map(row => row.detail);
assert.match(solidDetail, /69ファイル.*欠落 0.*無効な閉じた形状 0.*実交差 0.*適合/);
assert.match(surfaceDetail, /0 mm.*0 mm².*0.23570226039551587 mm.*0.5 mm.*0 mm.*0.020000000000003126 mm/);
assert.match(shaftDetail, /shaft-plus.*15°.*0°.*0.25 mm.*\[1,0,0\].*move-sha.*fixed-sha/);
assert.match(shaftDetail, /38.75 mm.*38.85 mm.*0.1 mm.*21.650635094610966 mm².*12.530514453124951 mm².*9.120120641486015 mm².*0.9120120641486145 mm³/);
assert.match(shaftDetail, /EXACT 頂点 573、面 449、非多様体辺 0、閉境界体積 1.0576445191582586 mm³、エラー なし/);
assert.match(shaftDetail, /MANIFOLD 頂点 573、面 449、非多様体辺 0、閉境界体積 1.0576428111119105 mm³、エラー なし/);
assert.equal(fallbackDetail, '{"value":7,"range":[1,2]}');
assert.ok(structuredCalibration.calibrationRows.every(row => !row.detail.includes("[object Object]")));

for (const model of models) {
  const dir = new URL(`models/${model}/build/`, root);
  const tables = JSON.parse(readFileSync(new URL("sim_tables.json", dir), "utf8"));
  const report = JSON.parse(readFileSync(new URL("simulate_report.json", dir), "utf8"));
  const drive = JSON.parse(readFileSync(new URL("drive_report.json", dir), "utf8"));
  const presentation = drivePresentation(drive, report);
  assert.ok(presentation.calibrationRows.every(row => typeof row.detail === "string"));
  assert.ok(presentation.calibrationRows.every(row => !row.detail.includes("[object Object]")));
  for (const [index, source] of (drive.calibration || []).entries()) {
    if (!source.detail || typeof source.detail !== "object") continue;
    const rendered = presentation.calibrationRows[index].detail;
    for (const value of numericLeaves(source.detail))
      assert.ok(rendered.includes(String(value)), `${model}/${source.id}: missing ${value} in ${rendered}`);
  }
  const canonical = presentation.interfaceRows.find(row => row.id === "canonical-reference");
  assert.match(canonical.detail, /最大実面差/);
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
