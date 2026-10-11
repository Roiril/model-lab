const RAD = Math.PI / 180;
const clamp = (value, low, high) => Math.max(low, Math.min(high, value));

const measured = value => value !== null && value !== '' && Number.isFinite(Number(value)) ? String(value) : null;
const detailText = value => {
  if (typeof value === 'string' && value) return value;
  if (value && typeof value === 'object') return JSON.stringify(value);
  return null;
};

export function driveCalibrationDetail(row) {
  const detail = row?.detail;
  if (!detail || typeof detail !== 'object')
    return detailText(detail) || '校正の測定記録がありません。';
  if (row.id === 'solid-input-geometry') {
    return [
      `検査 ${detail.filesChecked}ファイル`,
      `欠落 ${detail.missingFiles}`,
      `無効な閉じた形状 ${detail.invalidClosedSolids}`,
      `非隣接面の実交差 ${detail.properNonadjacentIntersections}`,
      `入力形状の校正 ${detail.calibrationPass === true ? '適合' : '不適合'}`,
    ].join('。');
  }
  if (row.id === 'canonical-surface') {
    return [
      `同じ実面の再三角化距離 ${detail.sameSurfaceRetriangulatedDistanceMm} mm`,
      `同じ実面の面積差 ${detail.sameSurfaceAreaDifferenceMm2} mm²`,
      `面欠落の実面距離 ${detail.missingFaceDistanceMm} mm`,
      `移動した実面の距離 ${detail.shiftedSurfaceDistanceMm} mm`,
      `細長い同一面の距離 ${detail.skinnyIdenticalDistanceMm} mm`,
      `細長い面を移動した距離 ${detail.skinnyShiftedDistanceMm} mm`,
    ].join('。');
  }
  if (row.id === 'shaft-cap-positive-volume') {
    const section = detail.independentSection || {};
    const exact = detail.solvers?.EXACT || {};
    const manifold = detail.solvers?.MANIFOLD || {};
    return [
      `検査 ${detail.id}`,
      `サーボ角 ${detail.servoDeg}°`,
      `回転角 ${detail.rotationDeg}°`,
      `移動量 ${detail.travelMm} mm`,
      `移動方向 ${JSON.stringify(detail.direction)}`,
      `移動側SHA ${detail.sourceStlSha256?.moving}`,
      `固定側SHA ${detail.sourceStlSha256?.fixed}`,
      `キャップ材開始X ${section.capMaterialStartsXmm} mm`,
      `移動後の六角端X ${section.shiftedShaftKeyedEndXmm} mm`,
      `一定六角断面の侵入 ${section.constantHexAxialPenetrationMm} mm`,
      `六角断面積 ${section.shaftHexAreaMm2} mm²`,
      `48角穴面積 ${section.capBore48GonAreaMm2} mm²`,
      `材料重なり面積 ${section.materialOverlapAreaMm2} mm²`,
      `独立断面の体積下限 ${section.volumeLowerBoundMm3} mm³`,
      `EXACT 頂点 ${exact.vertices}、面 ${exact.faces}、非多様体辺 ${exact.nonmanifoldEdges}、閉境界体積 ${exact.closedBoundaryVolumeMm3} mm³、エラー ${exact.error === null ? 'なし' : exact.error}`,
      `MANIFOLD 頂点 ${manifold.vertices}、面 ${manifold.faces}、非多様体辺 ${manifold.nonmanifoldEdges}、閉境界体積 ${manifold.closedBoundaryVolumeMm3} mm³、エラー ${manifold.error === null ? 'なし' : manifold.error}`,
    ].join('。');
  }
  return JSON.stringify(detail);
}

export function driveMeasurementDetail(row) {
  const values = [];
  const angles = row?.contactAnglesDeg;
  if (Array.isArray(angles) && angles.length === 2) {
    const reverse = measured(angles[0]), forward = measured(angles[1]);
    if (reverse !== null) values.push(`逆方向の接触角 ${reverse}°`);
    if (forward !== null) values.push(`正方向の接触角 ${forward}°`);
  }
  const gap = measured(row?.nearestGapMm);
  if (gap !== null) values.push(`最小隙間 ${gap} mm`);

  if (row?.id === 'gear-mesh') {
    const teeth = (Array.isArray(row.actualTeeth) ? row.actualTeeth : [])
      .map(value => measured(value)).filter(value => value !== null);
    if (teeth.length) values.push(`実歯数 ${teeth.join(' / ')}`);
    for (const [key, label, unit] of [
      ['faceWidthOverlapMm', '歯幅の重なり', ' mm'],
      ['minimumRetainedFaceOverlapMm', '保持後の最小歯幅重なり', ' mm'],
      ['contactRatio', 'かみ合い率', ''],
      ['maximumTotalAngularPlayDeg', '最大自由角', '°'],
    ]) {
      const value = measured(row[key]);
      if (value !== null) values.push(`${label} ${value}${unit}`);
    }
  } else if (row?.id === 'servo-seat') {
    for (const [key, label] of [
      ['nominalEngagementMm', '公称差込'],
      ['minimumRetainedEngagementMm', '保持後の最小差込'],
      ['minimumArmEngagementMm', 'ホーン腕の最小差込'],
    ]) {
      const value = measured(row[key]);
      if (value !== null) values.push(`${label} ${value} mm`);
    }
  } else if (row?.id === 'retention') {
    for (const item of Array.isArray(row.cases) ? row.cases : []) {
      const value = measured(item.maximumTravelMm);
      if (value !== null) values.push(`${item.label || '保持経路'} 最初に止まるまで最大 ${value} mm`);
      if (item.method === 'rear-surface-first-contact')
        values.push('ホーン後端は実面の初接触を測定。軸ソケットの体積干渉は未確認');
    }
    const total = measured(row.axialStack?.totalFreeTravelMm);
    if (total !== null) values.push(`軸方向の総遊び ${total} mm`);
  } else if (row?.id === 'cam-followers') {
    const value = measured(row.maximumActiveGapMm);
    if (value !== null) values.push(`最大実隙間 ${value} mm`);
  } else if (row?.id === 'canonical-reference') {
    const surfaceDifferences = (Array.isArray(row.parts) ? row.parts : [])
      .map(item => measured(item.maximumSurfaceDistanceMm ?? item.maximumSurfaceDifferenceMm))
      .filter(value => value !== null).map(Number);
    if (surfaceDifferences.length) values.push(`最大実面差 ${Math.max(...surfaceDifferences)} mm`);
    else values.push('最大実面差の記録なし');
    const vertexDifferences = (Array.isArray(row.parts) ? row.parts : [])
      .map(item => measured(item.maximumVertexDifferenceMm)).filter(value => value !== null).map(Number);
    if (vertexDifferences.length) values.push(`最大頂点差 ${Math.max(...vertexDifferences)} mm（参考）`);
  }
  return values.join('。') || detailText(row?.detail) || row?.basis || '測定値は保存した検証記録に収録しています。';
}

export function drivePresentation(drive, simulation) {
  const interfaces = Array.isArray(drive?.interfaces) ? drive.interfaces : [];
  const interfaceRows = interfaces.map((row) => ({
    id: row.id,
    label: row.label || row.id || '接続',
    status: row.status,
    result: row.status === 'pass' ? '形状適合' : row.status === 'unknown' ? '実機未確認' : '接続未成立',
    detail: driveMeasurementDetail(row),
  }));
  const geometryPass = drive?.overall?.geometryPass === true
    && simulation?.driveGeometry?.geometryPass === true
    && simulation?.driveGeometry?.sourceHashesFresh === true
    && interfaceRows.length > 0
    && interfaceRows.every((row) => row.status === 'pass' || row.status === 'unknown');
  const calculationPass = geometryPass && simulation?.overall?.calculationPass === true;
  return {
    geometryPass,
    calculationPass,
    status: calculationPass ? 'conditional' : 'fail',
    summary: calculationPass
      ? '計算内成立。接続形状は確認済みです。スプライン嵌合と材料は実機未確認です。'
      : '接続未成立。駆動接続の形状検査が揃うまで力学計算を成立扱いにしません。',
    interfaceRows: interfaceRows.length ? interfaceRows : [{
      id: 'drive-report-missing', label: '駆動接続の形状検査', status: 'fail',
      result: '接続未成立', detail: '接続形状の記録がありません。',
    }],
    calibrationRows: (Array.isArray(drive?.calibration) ? drive.calibration : []).map((row, index) => ({
      id: row.id || `calibration-${index}`,
      label: row.label || '接続計器の校正',
      pass: row.pass === true,
      detail: driveCalibrationDetail(row),
    })),
    hardwareUnknown: Array.isArray(drive?.hardwareUnknown) ? drive.hardwareUnknown : [],
  };
}

function number(value, fallback) {
  return Number.isFinite(Number(value)) ? Number(value) : fallback;
}

export function createSim(tables) {
  if (!tables?.rows?.length || tables.rows.length < 2) throw new Error("sim table needs at least two rows");
  const rows = tables.rows;
  const C = tables.const;
  const [low, high] = tables.limitsDeg;
  const step = rows[1].servoDeg - rows[0].servoDeg;

  function at(deg) {
    const servoDeg = clamp(number(deg, low), low, high);
    const f = clamp((servoDeg - low) / step, 0, rows.length - 1.000000001);
    const index = Math.min(Math.floor(f), rows.length - 2);
    const u = f - index;
    const a = rows[index], b = rows[index + 1];
    const mix = (key) => a[key] + (b[key] - a[key]) * u;
    const mixArray = (key) => a[key].map((value, i) => value + (b[key][i] - value) * u);
    const liftsMm = mixArray("liftsMm");
    return {
      servoDeg,
      inertiaRestKgm2: mix("inertiaRestKgm2"),
      inertiaGroupsKgm2: mix("inertiaGroupsKgm2"),
      dMGroupsDqKgm2PerRad: mix("dMGroupsDqKgm2PerRad"),
      gravityRestNm: mix("gravityRestNm"),
      gravityGroupsNm: mix("gravityGroupsNm"),
      contactFrictionGroupsNm: a.contactFrictionGroupsNm === undefined
        ? 0 : mix("contactFrictionGroupsNm"),
      liftsMm,
      dLiftDqMPerRad: mixArray("dLiftDqMPerRad"),
      d2LiftDq2MPerRad2: mixArray("d2LiftDq2MPerRad2"),
      contactActive: tables.contactModel === "gravity_one_sided"
        ? liftsMm.map(() => true)
        : liftsMm.map((value) => value > 1e-7),
    };
  }

  function holdTorque(deg, massScale = 1) {
    const state = at(deg);
    return state.gravityRestNm + state.gravityGroupsNm * clamp(number(massScale, 1), 0.5, 4);
  }

  function run({ from, to, kind = "ease", stallScale = 1, massScale = 1, duration = tables.duration_s } = {}) {
    duration = Math.max(number(duration, tables.duration_s), C.dtS);
    stallScale = clamp(number(stallScale, 1), 0, 1);
    massScale = clamp(number(massScale, 1), 0.5, 4);
    const requestedFrom = number(from, low), requestedTo = number(to, high);
    const start = clamp(requestedFrom, low, high), target = clamp(requestedTo, low, high);
    const clippedToLimits = start !== requestedFrom || target !== requestedTo;
    let q = start * RAD, velocity = 0, t = 0, nextRecord = C.recordS;
    const endTime = duration + C.settleS;
    let peakTorqueNm = 0, maxContactSpeedMmS = 0, minNormalForceN = Infinity, lastTau = 0;
    const liftOff = new Set();
    const trace = [];
    let previousActive = at(start).contactActive;

    const command = (now) => {
      if (kind === "step") return target;
      const x = clamp(now / duration, 0, 1);
      const eased = x ** 3 * (10 + x * (-15 + 6 * x));
      return start + (target - start) * eased;
    };
    const record = (now, cmd, state, torque) => trace.push({
      t: now,
      commandDeg: cmd,
      servoDeg: q / RAD,
      torqueNm: torque,
      liftsMm: [...state.liftsMm],
    });

    record(0, command(0), at(start), 0);
    while (t < endTime - C.dtS * 0.5) {
      const state = at(q / RAD);
      const cmd = command(t);
      const inertia = C.motorInertiaKgm2 + state.inertiaRestKgm2 + massScale * state.inertiaGroupsKgm2;
      const gravity = state.gravityRestNm + massScale * state.gravityGroupsNm;
      const dMass = massScale * state.dMGroupsDqKgm2PerRad;
      const stall = C.stallTorqueNm * stallScale;
      const effort = clamp((cmd * RAD - q) / C.controlBandRad, -1, 1);
      const tau = clamp(stall * effort - stall / C.noLoadSpeedRadS * velocity, -stall, stall);
      let net = tau - gravity - 0.5 * dMass * velocity * velocity;
      const friction = C.servoFrictionNm + massScale * state.contactFrictionGroupsNm;
      if (Math.abs(velocity) > 1e-4) net -= Math.sign(velocity) * friction;
      else if (Math.abs(net) <= friction) { net = 0; velocity = 0; }
      else net -= Math.sign(net) * friction;
      const acceleration = net / inertia;
      state.contactActive.forEach((active, index) => {
        if (active) {
          const carrierMass = tables.groups[index].massKg * massScale;
          const verticalAcceleration = state.dLiftDqMPerRad[index] * acceleration
            + state.d2LiftDq2MPerRad2[index] * velocity * velocity;
          const normal = carrierMass * (C.gravityMS2 + verticalAcceleration);
          minNormalForceN = Math.min(minNormalForceN, normal);
          if (normal < -C.contactToleranceN) liftOff.add(index);
        }
        if (active && !previousActive[index]) {
          maxContactSpeedMmS = Math.max(maxContactSpeedMmS,
            Math.abs(state.dLiftDqMPerRad[index] * velocity) * 1000);
        }
      });
      previousActive = state.contactActive;
      const previousQ = q, previousVelocity = velocity;
      velocity += acceleration * C.dtS;
      q += velocity * C.dtS;
      if (q < low * RAD) { q = low * RAD; velocity = Math.max(0, velocity); }
      else if (q > high * RAD) { q = high * RAD; velocity = Math.min(0, velocity); }
      maxContactSpeedMmS = Math.max(maxContactSpeedMmS,
        boundaryCrossingSpeedMmS(previousQ / RAD, q / RAD, previousVelocity, velocity,
          tables.contactBoundariesDeg ?? []));
      t += C.dtS;
      lastTau = tau;
      peakTorqueNm = Math.max(peakTorqueNm, Math.abs(tau));
      if (t + 1e-12 >= nextRecord) {
        record(t, command(t), at(q / RAD), tau);
        nextRecord += C.recordS;
      }
    }
    const finalState = at(q / RAD);
    if (Math.abs(trace.at(-1).t - t) > C.dtS) record(t, command(t), finalState, lastTau);
    const final = {
      t,
      commandDeg: command(t),
      servoDeg: q / RAD,
      torqueNm: lastTau,
      liftsMm: [...finalState.liftsMm],
    };
    return {
      trace,
      final,
      peakTorqueNm,
      maxContactSpeedMmS,
      contactFeasible: liftOff.size === 0,
      minNormalForceN: Number.isFinite(minNormalForceN) ? minNormalForceN : null,
      possibleLiftOffGroups: [...liftOff].sort((a, b) => a - b).map((index) => tables.groups[index].label),
      clippedToLimits,
    };
  }

  return { at, run, holdTorque, model: tables.model, limitsDeg: [...tables.limitsDeg], groups: tables.groups, const: C };
}

export function profile(kind, from, to, duration) {
  const safeDuration = Math.max(Number(duration) || 0, Number.EPSILON);
  return (time) => {
    if (kind === "step") return to;
    const x = clamp(time / safeDuration, 0, 1);
    return from + (to - from) * x ** 3 * (10 + x * (-15 + 6 * x));
  };
}

export function boundaryCrossingSpeedMmS(q0Deg, q1Deg, w0, w1, groups) {
  if (q0Deg === q1Deg) return 0;
  const low = Math.min(q0Deg, q1Deg), high = Math.max(q0Deg, q1Deg);
  let maximum = 0;
  for (const boundaries of groups) {
    for (const boundary of boundaries) {
      if (boundary.deg >= low && boundary.deg <= high) {
        const fraction = (boundary.deg - q0Deg) / (q1Deg - q0Deg);
        const crossingVelocity = w0 + (w1 - w0) * fraction;
        maximum = Math.max(maximum, Math.abs(boundary.slopeMPerRad * crossingVelocity) * 1000);
      }
    }
  }
  return maximum;
}
