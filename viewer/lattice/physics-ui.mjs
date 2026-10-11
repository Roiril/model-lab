import { createSim, drivePresentation } from './sim.mjs';
import { frameAt } from './motion.mjs';
import { lineChart } from '../lid-cube/lidcube.mjs';

const $ = id => document.getElementById(id);
const fmt = (value, digits = 1) => Number(value).toFixed(digits).replace(/^-0(?=\.0+$)/, '0');
const SERIES = ['--series-blue', '--series-orange', '--series-green', '--series-purple', '--series-vermillion'];

export function blindFloorDetail(row) {
  const values = [];
  const measured = value => value !== null && value !== '' && Number.isFinite(Number(value));
  if (measured(row?.minimumAxialThicknessMm))
    values.push(`最小軸方向厚さ ${row.minimumAxialThicknessMm} mm`);
  if (measured(row?.projectionSamples))
    values.push(`投影点 ${row.projectionSamples}点`);
  if (Array.isArray(row?.floorRangeXmm) && row.floorRangeXmm.length === 2)
    values.push(`盲底範囲 X=${row.floorRangeXmm[0]}〜${row.floorRangeXmm[1]} mm`);
  for (const [index, section] of (Array.isArray(row?.sections) ? row.sections : []).entries()) {
    if (![section.xMm, section.coveredSamples, section.totalSamples].every(measured)) continue;
    values.push(`断面${index + 1} X=${section.xMm} mm 被覆 ${section.coveredSamples}/${section.totalSamples}点（${section.pass ? '適合' : '不足'}）`);
  }
  return values.join('。');
}

export function clearanceEnvelopeRows(envelope) {
  const groups = Array.isArray(envelope?.summary?.groups) ? envelope.summary.groups : [];
  return groups.map((group) => {
    const range = group.end?.heightRangeMm;
    const rangeText = Array.isArray(range) && range.length === 2
      ? `${fmt(range[0], 3)}〜${fmt(range[1], 3)} mm`
      : '記録なし';
    return {
      id: `clearance-${group.id}`,
      label: `${group.label}の回転遊び包絡`,
      pass: true,
      chip: '幾何幅',
      detail: `公称位相 ${fmt(group.nominalPhaseDeg, 3)}°。最大位相差 ±${fmt(group.maximumPhaseDifferenceDeg, 3)}°。終点の公称高さ ${fmt(group.end?.nominalHeightMm, 3)} mm。終点の幾何学的高さ幅 ${rangeText}`,
    };
  });
}

export function removableSupportRows(review, evidence, geometry, closedLoop) {
  if (Array.isArray(geometry?.supports) && geometry.supports.length)
    return geometrySupportRows(geometry.supports, closedLoop, evidence?.coupler_support_gap);
  const rows = supportRows(review?.support_check, evidence?.coupler_support_gap);
  return [...rows, ...supportRows(review?.carrier_support_check, evidence?.carrier_outer_support_gap, true)];
}

const supportLabels = {
  housing_detent_support: '筐体内側の小柱',
  carrier_center_support: '中央格子の支え',
  carrier_outer_support: '外環格子の支え',
  horn_coupler_peg_support: 'ホーン受けの支え（差込下面）',
  horn_coupler_loop_support: 'ホーン受けの支え（受け下面）',
};

const supportMm = value => value !== null && value !== '' && Number.isFinite(Number(value))
  ? `${Number(value)} mm` : '記録なし';

function closedSupportMeasurements(closedLoop) {
  const measurements = new Map();
  for (const [plate, record] of Object.entries(closedLoop?.plates || {})) {
    const material = plate.includes('PETG') ? 'PETG' : plate.includes('PLA') ? 'PLA' : plate;
    for (const finding of (Array.isArray(record?.closedUnsupportedPaths) ? record.closedUnsupportedPaths : [])) {
      const value = finding?.externalSupportEvidence;
      if (!value?.supportId) continue;
      if (!measurements.has(value.supportId)) measurements.set(value.supportId, new Map());
      const materials = measurements.get(value.supportId);
      if (!materials.has(material)) materials.set(material, []);
      const rows = materials.get(material);
      const selected = {
        supportTopGcodeZMm: value.supportTopGcodeZMm,
        productMaterialBottomMm: value.productMaterialBottomMm,
        actualMaterialFaceGapMm: value.actualMaterialFaceGapMm,
        pathCoverageFraction: value.pathCoverageFraction,
        startAndEndCovered: value.startAndEndCovered,
      };
      const key = JSON.stringify(selected);
      if (!rows.some(row => row.key === key)) rows.push({ key, ...selected });
    }
  }
  return measurements;
}

function gcodeSupportText(supportId, measurements, legacyCoupler) {
  const materialRows = measurements.get(supportId);
  const values = [];
  if (materialRows) {
    for (const [material, rows] of materialRows) {
      rows.forEach((row, index) => {
        const endpoints = Array.isArray(row.startAndEndCovered)
          ? row.startAndEndCovered.map(value => value ? '被覆' : '未被覆').join(' / ') : '記録なし';
        const suffix = rows.length > 1 ? ` ${index + 1}` : '';
        values.push(`${material} G-code測定${suffix}: 支え上端Z ${supportMm(row.supportTopGcodeZMm)}。製品材料下面 ${supportMm(row.productMaterialBottomMm)}。実材料面空隙 ${supportMm(row.actualMaterialFaceGapMm)}。経路被覆率 ${row.pathCoverageFraction ?? '記録なし'}。始点 / 終点 ${endpoints}`);
      });
    }
  }
  if (supportId === 'horn_coupler_peg_support' && !materialRows) {
    for (const [material, row] of Object.entries(legacyCoupler?.materials || {})) {
      values.push(`${material} G-code測定: 支え最終押出Z ${supportMm(row.support_last_extrusion_z_mm)}。製品初層Z ${supportMm(row.peg_first_extrusion_z_mm)}。製品材料下面 ${supportMm(row.peg_material_bottom_mm)}。実材料面空隙 ${supportMm(row.material_gap_mm)}。閉環の対象なし`);
    }
  }
  return values;
}

function geometrySupportRows(supports, closedLoop, legacyCoupler) {
  const measurements = closedSupportMeasurements(closedLoop);
  const rows = [];
  for (const support of supports) {
    const minimumZ = Array.isArray(support.printComponentMinimumZMm)
      ? `[${support.printComponentMinimumZMm.join(', ')}] mm` : '記録なし';
    const attachment = support.attachment === 'breakaway_contact'
      ? '折り取り接続' : support.attachment === 'separate' ? '分離した印刷支え' : String(support.attachment || '記録なし');
    for (const height of (Array.isArray(support.heights) ? support.heights : [])) {
      const supportId = height.support_id;
      const verified = support.removalPhysicallyVerified === true;
      const geometryPass = support.pass === true;
      const measured = gcodeSupportText(supportId, measurements, legacyCoupler);
      rows.push({
        id: `print-support-${supportId}`,
        label: supportLabels[supportId] || supportId,
        pass: geometryPass && verified,
        chip: !geometryPass ? '形状要確認' : verified ? '除去確認' : '実物未確認',
        detail: `形状検査 ${geometryPass ? '適合' : '要確認'}。接続方式 ${attachment}。製品との共通体積 ${support.supportProductCommonVolumeMm3 ?? '記録なし'} mm³。印刷成分の最小Z ${minimumZ}。公称形状: 支え上端Z ${supportMm(height.support_top_z_mm)}。製品初層Z ${supportMm(height.product_first_z_mm)}。材料面空隙 ${supportMm(height.material_face_gap_mm)}。${measured.join('。') || 'G-code測定なし'}。除去力と傷は実物未確認`,
      });
    }
  }
  return rows;
}

function supportRows(primary, secondary, carrier = false) {
  if ((!primary || typeof primary !== 'object') && (!secondary || typeof secondary !== 'object')) return [];
  const record = {
    ...(secondary || {}),
    ...(primary || {}),
    materials: Object.fromEntries([...new Set([...Object.keys(secondary?.materials || {}),
      ...Object.keys(primary?.materials || {})])].map(key => [key,
      { ...(secondary?.materials?.[key] || {}), ...(primary?.materials?.[key] || {}) }])),
  };
  const mm = value => value !== null && value !== '' && Number.isFinite(Number(value))
    ? `${Number(value)} mm` : '記録なし';
  const verified = record.removal_physically_verified === true;
  return Object.entries(record.materials).map(([material, values]) => {
    const supportLayer = values?.support_last_layer_height_mm;
    const pegLayer = carrier ? values?.product_first_layer_height_mm : values?.peg_first_layer_height_mm;
    const sameLayer = Number.isFinite(Number(supportLayer))
      && Number.isFinite(Number(pegLayer)) && Number(supportLayer) === Number(pegLayer);
    const layerText = sameLayer ? mm(supportLayer) : `支え ${mm(supportLayer)} / 製品 ${mm(pegLayer)}`;
    const productZ = carrier ? values?.product_first_extrusion_z_mm : values?.peg_first_extrusion_z_mm;
    const productBottom = carrier ? values?.product_material_bottom_mm : values?.peg_material_bottom_mm;
    const geometryText = carrier ? '' : `軸突起形状下端 ${mm(record.peg_geometry_bottom_mm)}。`;
    return {
      id: `removable-support-${carrier ? 'carrier-' : ''}${material}`,
      label: `${material}の${carrier ? '外環格子' : 'ホーン受け'}の除去式支え`,
      pass: verified,
      chip: verified ? '除去確認' : '実物未確認',
      detail: `支え形状上端 ${mm(record.support_geometry_top_mm)}。${geometryText}支え最終押出Z ${mm(values?.support_last_extrusion_z_mm)}。${carrier ? '該当部' : '軸突起'}初層Z ${mm(productZ)}。${carrier ? 'G-code推定材料下面' : '軸突起材料下面'} ${mm(productBottom)}。層厚 ${layerText}。G-code推定空隙 ${mm(values?.material_gap_mm)}。除去性と癒着は${verified ? '実物で確認済み' : '実物未確認'}`,
    };
  });
}

export function sampleTrace(trace, time) {
  if (time <= trace[0].t) return trace[0];
  if (time >= trace.at(-1).t) return trace.at(-1);
  let low = 0, high = trace.length - 1;
  while (high - low > 1) { const mid = (low + high) >> 1; if (trace[mid].t <= time) low = mid; else high = mid; }
  const a = trace[low], b = trace[high], f = (time - a.t) / (b.t - a.t);
  const mix = key => a[key] + (b[key] - a[key]) * f;
  return { t: time, commandDeg: mix('commandDeg'), servoDeg: mix('servoDeg'), torqueNm: mix('torqueNm'), liftsMm: a.liftsMm.map((v, i) => v + (b.liftsMm[i] - v) * f) };
}

export function setupPhysics({ data, state, renderer }) {
  if (!data.simTables || !data.sim) throw new Error('物理計算データがありません');
  const tables = data.simTables, sim = createSim(tables), [minimum, maximum] = tables.limitsDeg;
  const groups = tables.groups;
  const drive = drivePresentation(data.drive, data.sim);
  let last = null, animation = 0, paused = false, time = 0, previous = 0;
  const opts = () => ({ stallScale: Number($('torque').value) / 100, massScale: Number($('mass').value), kind: $('profile').value });
  $('profile').querySelector('[value="ease"]').textContent = `${tables.duration_s} 秒でゆっくり`;
  $('open').textContent = data.model.endsWith('c4') ? '持ち上げる' : '波を進める';
  $('close').textContent = '戻す';
  $('massNote').textContent = `トルク100%は停動トルク ${fmt(tables.const.stallTorqueNm * 1000, 0)} mN·m（4.8V）。重さ1×は中実PLAの格子合計 ${fmt(groups.reduce((n, g) => n + g.massKg, 0) * 1000)} g。カム接点の摩擦係数は0.30です。`;
  const fields = [['mCmd', '指令角'], ['mServo', 'サーボ角'], ['mLift', '格子の上昇'], ['mTau', 'トルク / 上限'], ['mImpact', '再接触の速さ'], ['mPeak', 'この動作の最大トルク']];
  $('metrics').replaceChildren(...fields.map(([id, label]) => {
    const div = document.createElement('div'), span = document.createElement('span'), output = document.createElement('output');
    span.textContent = label; output.id = id; div.append(span, output); return div;
  }));
  $('liftLegend').replaceChildren(...groups.map((group, index) => {
    const span = document.createElement('span'); span.style.color = `var(${SERIES[index]})`; span.textContent = group.label; return span;
  }));

  function show(row) {
    state.servoDeg = row.servoDeg;
    state.transforms = frameAt(data.motion.frames, row.servoDeg).transforms;
    groups.forEach((group, index) => {
      if (state.transforms[group.id]) { state.transforms[group.id] = [...state.transforms[group.id]]; state.transforms[group.id][14] = row.liftsMm[index]; }
    });
    $('mCmd').textContent = `${fmt(row.commandDeg)}°`;
    $('mServo').textContent = `${fmt(row.servoDeg)}°`;
    $('mLift').textContent = row.liftsMm.map(v => fmt(v, 2)).join(' / ') + ' mm';
    $('mTau').textContent = `${fmt(row.torqueNm * 1000, 0)} / ${fmt((last?.stallScale ?? 1) * tables.const.stallTorqueNm * 1000, 0)} mN·m`;
    $('mImpact').textContent = last ? `${fmt(last.maxContactSpeedMmS, 2)} mm/s` : '—';
    $('mPeak').textContent = last ? `${fmt(last.peakTorqueNm * 1000, 1)} mN·m` : '—';
    $('clock').textContent = `${fmt(row.t, 3)} s`;
    $('gl').dataset.simTime = String(row.t);
    $('gl').dataset.liftsMm = JSON.stringify(row.liftsMm);
    renderer.draw();
  }
  function charts(cursor = null) {
    const trace = last?.trace || [], end = trace.at(-1)?.t || tables.duration_s;
    const x = [0, end], xt = [0, +(end / 2).toFixed(2), +end.toFixed(2)];
    const peakLift = Math.max(1, ...data.motion.frames.flatMap(f => groups.map(g => f.transforms[g.id]?.[14] || 0)));
    const liftTop = Math.ceil(peakLift);
    lineChart($('chartLift'), { label: '各格子の上昇の時間変化', x, xt, y: [0, liftTop], yt: [0, liftTop / 2, liftTop], xl: '時間 (s)', yl: '上昇 (mm)', cursor,
      series: groups.map((g, i) => ({ color: SERIES[i], pts: trace.map(row => [row.t, row.liftsMm[i]]) })) });
    const limit = Math.max(1, Math.round(tables.const.stallTorqueNm * (last?.stallScale ?? 1) * 1000));
    lineChart($('chartTau'), { label: 'サーボのトルクの時間変化', x, xt, y: [-limit, limit], yt: [-limit, 0, limit], xl: '時間 (s)', yl: 'トルク (mN·m)', cursor,
      series: [{ color: '--series-orange', pts: trace.map(row => [row.t, row.torqueNm * 1000]) }] });
  }
  function holdChart() {
    const massScale = opts().massScale, pts = [];
    let maximumTorque = 0, at = minimum;
    for (let deg = minimum; deg <= maximum; deg += .5) {
      const value = sim.holdTorque(deg, massScale) * 1000; pts.push([deg, value]);
      if (Math.abs(value) > maximumTorque) { maximumTorque = Math.abs(value); at = deg; }
    }
    const top = Math.max(1, Math.ceil(maximumTorque));
    lineChart($('chartHold'), { label: 'サーボ角度ごとの重力保持トルク', x: [minimum, maximum], xt: [minimum, (minimum + maximum) / 2, maximum], y: [-top, top], yt: [-top, 0, top], xl: 'サーボ角 (°)', yl: 'mN·m', series: [{ color: '--series-blue', pts }] });
    $('holdText').textContent = `最大 ${fmt(maximumTorque, 2)} mN·m（${at}°）。停動トルクの ${fmt(maximumTorque / (tables.const.stallTorqueNm * 1000) * 100, 2)}%。格子の重さ ${fmt(massScale, 2)}×。静止中の摩擦方向は決まらないため、この図には含めません。`;
  }
  function stop() { cancelAnimationFrame(animation); animation = 0; }
  function tick(now) {
    if (paused) return;
    time = Math.min(last.trace.at(-1).t, time + Math.min(.1, (now - previous) / 1000) * Number($('rate').value)); previous = now;
    show(sampleTrace(last.trace, time)); charts(time);
    if (time < last.trace.at(-1).t) animation = requestAnimationFrame(tick);
    else { animation = 0; $('pause').disabled = true; }
  }
  function start(target) {
    stop();
    if (!drive.calculationPass) {
      $('status').textContent = drive.summary;
      $('gl').dataset.driveStatus = 'fail';
      return;
    }
    const options = opts();
    last = { ...sim.run({ from: state.servoDeg, to: target, ...options, duration: tables.duration_s }), ...options };
    const reached = Math.abs(last.final.servoDeg - target) < 1;
    const contact = last.contactFeasible ? '計算上の接触反力は非負です。接触時の衝撃は未計算です。' : '格子がカムから離れる可能性があります。表示は接触を仮定した形です。';
    $('status').textContent = `条件付き計算。${reached ? '計算上は目標に到達' : '計算上も目標に届かない'}（${fmt(last.final.servoDeg)}°）。トルク上限 ${fmt(options.stallScale * 100, 0)}%。格子の重さ ${fmt(options.massScale, 2)}×。${contact} スプライン嵌合と材料は実機未確認です。`;
    $('gl').dataset.driveStatus = 'conditional';
    $('gl').dataset.contactFeasible = String(last.contactFeasible);
    $('gl').dataset.targetDeg = String(target);
    time = 0; paused = false; $('pause').textContent = '一時停止'; $('pause').disabled = false;
    charts(0); show(last.trace[0]);
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) { show(last.final); charts(last.final.t); $('pause').disabled = true; return; }
    previous = performance.now(); animation = requestAnimationFrame(tick);
  }
  $('open').addEventListener('click', () => start(maximum));
  $('close').addEventListener('click', () => start(minimum));
  $('pause').addEventListener('click', () => {
    paused = !paused; $('pause').textContent = paused ? '再開' : '一時停止';
    stop(); if (!paused) { previous = performance.now(); animation = requestAnimationFrame(tick); }
  });
  for (const id of ['torque', 'mass']) $(id).addEventListener('input', () => {
    $('torqueOut').textContent = `${$('torque').value}%`; $('massOut').textContent = `${fmt($('mass').value, 2)}×`; holdChart();
  });
  const calculationRows = Array.isArray(data.sim.calibration) ? data.sim.calibration : Object.entries(data.sim.calibration || {}).map(([id, row]) => ({ id, ...row }));
  const rawInterfaces = new Map((Array.isArray(data.drive?.interfaces) ? data.drive.interfaces : [])
    .map(row => [row.id, row]));
  const connectionRows = drive.interfaceRows.map(row => {
    const measured = row.id === 'coupler-structure' ? blindFloorDetail(rawInterfaces.get(row.id)) : '';
    return { ...row, detail: measured || row.detail, pass: row.status === 'pass', chip: row.result };
  });
  const driveCalibrationRows = drive.calibrationRows.map(row => ({
    ...row, chip: row.pass ? '計器確認' : '計器要確認',
  }));
  const hardwareRows = drive.hardwareUnknown.map((detail, index) => ({
    id: `hardware-${index}`, label: detail, pass: false, chip: '実機未確認', detail: '',
  }));
  const clearanceRows = clearanceEnvelopeRows(data.sim.clearanceEnvelope);
  const supportRows = removableSupportRows(data.print_path_review, data.print_path_evidence,
    data.print_support_geometry, data.closed_loop_support_evidence);
  const checkRows = [
    { id: 'drive-overall', label: '駆動接続と1自由度計算', pass: drive.calculationPass,
      chip: drive.calculationPass ? '計算内成立' : '接続未成立', detail: drive.summary },
    ...clearanceRows, ...supportRows, ...connectionRows, ...driveCalibrationRows, ...hardwareRows,
    ...calculationRows.map(row => ({ ...row, chip: row.pass ? '計算確認' : '計算要確認' })),
  ];
  $('checks').replaceChildren(...checkRows.map(row => {
    const li = document.createElement('li'), chip = document.createElement('span'), text = document.createElement('span');
    chip.className = `chip ${row.pass ? 'ok' : 'warn'}`; chip.textContent = row.chip; text.textContent = row.label + (row.detail ? `。${row.detail}` : ''); li.append(chip, text); return li;
  }));
  $('simLimits').textContent = '接続形状の検査を前提にした条件付きの1自由度計算です。計算と表示する動作形状は公称位相のままです。回転遊びは実STLの接触角を1:1で足した保守的な±位相差と、その範囲の幾何学的高さ幅だけを示します。位置精度は保証しません。スプライン嵌合と材料は含めません。この高さ幅の動的計算と全組み合わせ干渉は未検証です。格子の自重によるカム接点摩擦を含めます。案内の横予圧は不明です。追従の可否は鉛直加速度から判定します。浮き上がり後の飛行や衝撃は解きません。剛体のたわみ、破損、熱は扱いません。Pythonとブラウザの同じ条件の計算を数値で照合しています。';
  for (const id of ['open', 'close', 'profile', 'torque', 'mass']) $(id).disabled = !drive.calculationPass;
  holdChart(); charts();
  if (drive.calculationPass) start(maximum);
  else {
    $('status').textContent = drive.summary;
    $('gl').dataset.driveStatus = 'fail';
    show({ t: 0, commandDeg: minimum, servoDeg: minimum, torqueNm: 0, liftsMm: sim.at(minimum).liftsMm });
  }
  addEventListener('pagehide', stop, { once: true });
}
