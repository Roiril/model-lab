import { createSim, drivePresentation } from './sim.mjs';
import { physicsSeries, physicsText, posedTransforms } from './ui-config.mjs';
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
  const axis = Array.isArray(row?.floorRangeZmm) ? 'Z' : 'X';
  const floorRange = row?.[`floorRange${axis}mm`];
  if (Array.isArray(floorRange) && floorRange.length === 2)
    values.push(`盲底範囲 ${axis}=${floorRange[0]}〜${floorRange[1]} mm`);
  for (const [index, section] of (Array.isArray(row?.sections) ? row.sections : []).entries()) {
    const coordinate = section[`${axis.toLowerCase()}Mm`];
    if (![coordinate, section.coveredSamples, section.totalSamples].every(measured)) continue;
    values.push(`断面${index + 1} ${axis}=${coordinate} mm 被覆 ${section.coveredSamples}/${section.totalSamples}点（${section.pass ? '適合' : '不足'}）`);
  }
  return values.join('。');
}

function positionalRetentionDetail(row) {
  if (!row) return '';
  const cases = row.interfaces || row.directions;
  if (!Array.isArray(cases)) return '';
  const rows = cases.filter(item => Number.isFinite(item.contact?.contactTravelMm));
  if (!rows.length) return '';
  const directionLabels = { 'x-minus': '−X', 'x-plus': '+X', 'y-minus': '−Y', 'y-plus': '+Y', 'z-minus': '−Z', 'z-plus': '+Z' };
  const values = rows.map(item => `${item.label || directionLabels[item.direction] || item.direction || '保持面'} 初接触 ${fmt(item.contact.contactTravelMm, 3)} mm`);
  if (Array.isArray(row.trackContainment)) {
    const margins = row.trackContainment.map(item => item.remainingRadialMarginMm).filter(Number.isFinite);
    if (margins.length) values.push(`接点とトラック端の最小残量 ${fmt(Math.min(...margins), 3)} mm`);
  }
  if (row.retentionChain?.totalDownwardPlayMm != null) {
    const chain = row.retentionChain;
    values.push(`本体と底板の遊び ${fmt(chain.bodyToBottomNominalGapMm, 3)} mm。底板と外装の初接触 ${fmt(chain.bottomToHousingContact.contactTravelMm, 3)} mm。外装まで含む下方の総遊び ${fmt(chain.totalDownwardPlayMm, 3)} mm。底板の爪の保持力は実物未確認`);
  }
  if (row.upperRetentionChain?.faceplateSnapContact?.contactTravelMm != null)
    values.push(`天板の爪から外装への初接触 ${fmt(row.upperRetentionChain.faceplateSnapContact.contactTravelMm, 3)} mm。案内枠の上方向の保持力は実物未確認`);
  return values.join('。');
}

export function clearanceEnvelopeRows(envelope) {
  const groups = Array.isArray(envelope?.summary?.groups) ? envelope.summary.groups : [];
  if (!groups.length && Array.isArray(envelope?.groups)) {
    return envelope.groups.map(group => {
      const ranges = group.samples.flatMap(sample => sample.heightRangeMm);
      return {
        id: `clearance-${group.id}`, label: `${group.label}の回転遊びによる上下幅`,
        pass: true, chip: '幾何幅',
        detail: `実STLの接触角から求めた最大位相差 ±${fmt(group.maximumPhaseDifferenceDeg, 3)}°。全停止角を含む高さ範囲 ${fmt(Math.min(...ranges), 3)}〜${fmt(Math.max(...ranges), 3)} mm。停止位置ごとの幅は詳細に記録しています。`,
      };
    });
  }
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

export function removableSupportRows(review, evidence, geometry, closedLoop, firstLayer) {
  if (geometry?.parts && typeof geometry.parts === 'object') {
    const measured = Object.entries(geometry.parts).flatMap(([partId, part]) =>
      (part.supports || []).map(support => ({
        attachment: 'separate', pass: support.decision === 'accepted',
        removalPhysicallyVerified: false,
        supportProductCommonVolumeMm3: support.nominalProductCommonManifoldMm3,
        printComponentMinimumZMm: [support.actualComponent?.bedMinZMm],
        heights: (support.regionalContactEvidence?.length
          ? support.regionalContactEvidence
          : [{ support_top_z_mm: support.supportTopZMm,
            product_first_z_mm: support.productFirstZMm,
            declaredGeometricClearanceMm: support.geometricClearanceMm }]
        ).map(region => ({ support_id: support.id, part_id: partId,
          region: region.region,
          support_top_z_mm: region.support_top_z_mm,
          product_first_z_mm: region.product_first_z_mm,
          geometric_clearance_mm: region.declaredGeometricClearanceMm,
          measured_geometric_clearance_mm: region.independentFirstZ?.actualGapMm,
          target_gcode_gap_mm: support.materialFaceGapMm })),
      })));
    return geometrySupportRows(measured, closedLoop, evidence?.coupler_support_gap, firstLayer);
  }
  if (Array.isArray(geometry?.supports) && geometry.supports.length)
    return geometrySupportRows(geometry.supports, closedLoop, evidence?.coupler_support_gap, firstLayer);
  const rows = supportRows(review?.support_check, evidence?.coupler_support_gap);
  return [...rows, ...supportRows(review?.carrier_support_check, evidence?.carrier_outer_support_gap, true)];
}

const supportLabels = {
  housing_detent_support: '筐体内側の小柱',
  carrier_center_support: '中央格子の支え',
  carrier_outer_support: '外環格子の支え',
  horn_coupler_peg_support: 'ホーン受けの支え（差込下面）',
  horn_coupler_loop_support: 'ホーン受けの支え（受け下面）',
  housing_flange_left_print_support: '外装の左取付部の支え',
  housing_flange_right_print_support: '外装の右取付部の支え',
  housing_coupler_stop_print_support: 'ホーン受け止め板の印刷用の支え',
  carrier_center_arm_print_support: '中央格子の梁の支え',
  guide_frame_print_support: '案内枠の支え',
  guide_center_stop_print_support: '中央の円形案内の支え',
  guide_key_arm_print_support: '中央の止め板の支え',
  guide_spoke_print_support: '案内枠の四方の梁の支え',
};

function supportLabel(id) {
  if (supportLabels[id]) return supportLabels[id];
  if (/^guide_sleeve_print_support/.test(id)) return '格子の角柱案内の支え';
  const carrier = /^carrier_(center|upper_left|upper_right|lower_pair)_web(?:_(inner|outer))?_print_support(?:_(\d+))?$/.exec(id);
  if (carrier) {
    const group = { center: '中央', upper_left: '左上', upper_right: '右上', lower_pair: '下側' }[carrier[1]];
    const position = carrier[2] === 'inner' ? '内側' : carrier[2] === 'outer' ? '外側' : '梁';
    return `${group}の格子の${position}の支え${carrier[3] ? ` ${carrier[3]}` : ''}`;
  }
  return id;
}

const supportMm = value => value !== null && value !== '' && Number.isFinite(Number(value))
  ? `${Number(value)} mm` : '記録なし';

const supportRegionLabels = { key_stop_arm: '中央の止め板',
  four_outer_spokes: '四方の梁', outer_frame: '外周の枠' };

function gcodeSupportMeasurements(closedLoop, firstLayer) {
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
  for (const [plate, record] of Object.entries(firstLayer?.plates || {})) {
    const material = plate.includes('PETG') ? 'PETG' : plate.includes('PLA') ? 'PLA' : plate;
    for (const object of record.objects || []) {
      for (const footprint of object.componentStability?.supportFootprints || []) {
        if (!footprint.supportId) continue;
        if (!measurements.has(footprint.supportId)) measurements.set(footprint.supportId, new Map());
        const materials = measurements.get(footprint.supportId);
        if (!materials.has(material)) materials.set(material, []);
        const rows = materials.get(material);
        const regional = Array.isArray(footprint.regions) && footprint.regions.length > 0;
        for (const measurement of (regional ? footprint.regions : [footprint])) {
          const selected = {
            region: regional ? measurement.id : null,
            actualSupportLastExtrusionZMm: measurement.actualSupportLastExtrusionZMm,
            actualProductFirstExtrusionZMm: measurement.actualProductFirstExtrusionZMm,
            actualMaterialFaceGapMm: measurement.actualMaterialFaceGapMm,
            actualBedAreaMm2: footprint.footprint?.depositedAreaEstimateMm2,
            stableToContact: footprint.decision === 'accepted' && measurement.decision === 'accepted',
          };
          const key = JSON.stringify(selected);
          if (!rows.some(row => row.key === key)) rows.push({ key, ...selected });
        }
      }
    }
  }
  return measurements;
}

function gcodeSupportText(supportId, measurements, legacyCoupler, region = null) {
  const materialRows = measurements.get(supportId);
  const values = [];
  if (materialRows) {
    for (const [material, rows] of materialRows) {
      const regionalRows = region ? rows.filter(row => row.region === region) : [];
      const shownRows = regionalRows.length ? regionalRows : rows;
      shownRows.forEach((row, index) => {
        const endpoints = Array.isArray(row.startAndEndCovered)
          ? row.startAndEndCovered.map(value => value ? '被覆' : '未被覆').join(' / ') : '記録なし';
        const suffix = row.region ? `（${supportRegionLabels[row.region] || row.region}）`
          : shownRows.length > 1 ? ` ${index + 1}` : '';
        if (row.actualSupportLastExtrusionZMm != null) {
          values.push(`${material} G-code測定${suffix}: 支え最終押出Z ${supportMm(row.actualSupportLastExtrusionZMm)}。製品初層Z ${supportMm(row.actualProductFirstExtrusionZMm)}。実材料面空隙 ${supportMm(row.actualMaterialFaceGapMm)}。初層の接地面積 ${row.actualBedAreaMm2 ?? '記録なし'} mm²。製品と接する高さまでの安定性 ${row.stableToContact ? '適合' : '要確認'}`);
        } else {
          values.push(`${material} G-code測定${suffix}: 支え上端Z ${supportMm(row.supportTopGcodeZMm)}。製品材料下面 ${supportMm(row.productMaterialBottomMm)}。実材料面空隙 ${supportMm(row.actualMaterialFaceGapMm)}。経路被覆率 ${row.pathCoverageFraction ?? '記録なし'}。始点 / 終点 ${endpoints}`);
        }
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

function geometrySupportRows(supports, closedLoop, legacyCoupler, firstLayer) {
  const measurements = gcodeSupportMeasurements(closedLoop, firstLayer);
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
      const measured = gcodeSupportText(supportId, measurements, legacyCoupler, height.region);
      const isGeometric = height.geometric_clearance_mm != null;
      const regionLabel = supportRegionLabels[height.region];
      const gapText = isGeometric
        ? `STLの設計隙間 ${supportMm(height.geometric_clearance_mm)}。実STLで測った隙間 ${supportMm(height.measured_geometric_clearance_mm)}。G-codeで必要な材料面隙間 ${supportMm(height.target_gcode_gap_mm)}`
        : `材料面空隙 ${supportMm(height.material_face_gap_mm)}`;
      rows.push({
        id: `print-support-${supportId}${height.region ? `-${height.region}` : ''}`,
        label: supportLabel(supportId) + (regionLabel ? `（${regionLabel}）` : ''),
        pass: geometryPass && verified,
        chip: !geometryPass ? '形状要確認' : verified ? '除去確認' : '実物未確認',
        detail: `形状検査 ${geometryPass ? '適合' : '要確認'}。接続方式 ${attachment}。製品との共通体積 ${support.supportProductCommonVolumeMm3 ?? '記録なし'} mm³。印刷成分の最小Z ${minimumZ}。公称形状: 支え上端Z ${supportMm(height.support_top_z_mm)}。製品下面Z ${supportMm(height.product_first_z_mm)}。${gapText}。${measured.join('。') || 'G-code測定なし'}。除去力と傷は実物未確認`,
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

function calculationDetail(row) {
  const value = row.detail;
  if (!value || typeof value !== 'object') return value || '';
  if (row.id === 'signed-mass')
    return `${value.knownBoxMm.join(' × ')} mmの箱。期待体積 ${fmt(value.expectedVolumeMm3, 0)} mm³。測定 ${fmt(value.positiveSignedVolumeMm3, 0)} mm³。面を裏返した測定 ${fmt(value.reversedSignedVolumeMm3, 0)} mm³。開いた形状の境界 ${value.openMeshBadEdges}辺を検出。`;
  if (row.id === 'dynamic-negative') {
    const runs = value.patternStopRuns || [];
    const passed = runs.reduce((count, run) => count + Number(run.forwardReached && run.forwardContactFeasible) + Number(run.reverseReached && run.reverseContactFeasible), 0);
    const errors = runs.flatMap(run => [run.forwardErrorDeg, run.reverseErrorDeg]);
    return `必要静的トルク ${fmt(value.requiredTorqueNm * 1000, 2)} mN·m。その半分 ${fmt(value.halfAvailableTorqueNm * 1000, 2)} mN·mでの終角 ${fmt(value.halfRequiredFinalServoDeg, 2)}°。トルク0での終角 ${fmt(value.zeroTorqueFinalServoDeg, 2)}°。五つの停止位置の往復 ${passed} / ${runs.length * 2}回が到達と接触を満たします。最大角度誤差 ${fmt(Math.max(...errors), 3)}°。`;
  }
  if (row.id === 'guide-angle')
    return `接点の最大傾き ${value.alphaMaximumDeg}°。摩擦係数と傾きから求めた値 ${fmt(value.muTanAlpha, 3)}。案内での摩擦を含む荷重の増加率 ${fmt(value.amplification, 3)}倍。`;
  return JSON.stringify(value);
}

export function setupPhysics({ data, state, renderer }) {
  if (!data.simTables || !data.sim) throw new Error('物理計算データがありません');
  const tables = data.simTables, sim = createSim(tables), [minimum, maximum] = tables.limitsDeg;
  const groups = tables.groups;
  const ui = data.ui, hasPatterns = Array.isArray(data.motion.patterns) && data.motion.patterns.length > 0;
  const text = physicsText(ui, hasPatterns), term = text.term;
  // 折れ線・凡例・「格子の上下」の欄に出す群。sim_tables.groups の中での位置。
  const series = physicsSeries(ui, groups.map(group => group.id));
  const patternButtons = [];
  const drive = drivePresentation(data.drive, data.sim);
  let last = null, animation = 0, paused = false, time = 0, previous = 0;
  const opts = () => ({ stallScale: Number($('torque').value) / 100, massScale: Number($('mass').value), kind: $('profile').value });
  $('profile').querySelector('[value="ease"]').textContent = `${tables.duration_s} 秒でゆっくり`;
  $('open').textContent = text.openLabel;
  $('close').textContent = text.closeLabel;
  $('massLabel').textContent = `${term}の重さ`;
  $('actions').setAttribute('aria-label', `${term}の操作`);
  if (ui.physics.patternNote) $('patternNote').textContent = ui.physics.patternNote;
  const massTotal = fmt(groups.reduce((n, g) => n + g.massKg, 0) * 1000);
  if (ui.physics.massNote) {
    // 新モデルは質量と摩擦の前提を ui.physics.massNote で書く。旧 3 モデルは下の固定文のまま
    $('massNote').textContent = `トルク100%は停動トルク ${fmt(tables.const.stallTorqueNm * 1000, 0)} mN·m（4.8V）。重さ1×は${term}合計 ${massTotal} g。${ui.physics.massNote}`;
  } else {
    $('massNote').textContent = `トルク100%は停動トルク ${fmt(tables.const.stallTorqueNm * 1000, 0)} mN·m（4.8V）。重さ1×は中実PLAの${term}合計 ${massTotal} g。カム接点の摩擦係数は0.30です。`;
    if (hasPatterns) $('massNote').textContent += ' 円盤外周の支持面と格子の案内にも摩擦を見込みます。中央の円形案内が受ける横荷重も計算に含めます。';
  }
  const fields = [['mCmd', '指令角'], ['mServo', 'サーボ角'], ['mLift', text.liftLabel], ['mTau', 'トルク / 上限'], ['mImpact', '再接触の速さ'], ['mPeak', 'この動作の最大トルク']];
  $('metrics').replaceChildren(...fields.map(([id, label]) => {
    const div = document.createElement('div'), span = document.createElement('span'), output = document.createElement('output');
    span.textContent = label; output.id = id; div.append(span, output); return div;
  }));
  $('liftLegend').replaceChildren(...series.map((groupIndex, position) => {
    const span = document.createElement('span'); span.style.color = `var(${SERIES[position]})`; span.textContent = groups[groupIndex].label; return span;
  }));

  function show(row) {
    state.servoDeg = row.servoDeg;
    state.transforms = posedTransforms(data.motion.frames, row, ui, groups);
    $('mCmd').textContent = `${fmt(row.commandDeg)}°`;
    $('mServo').textContent = `${fmt(row.servoDeg)}°`;
    $('mLift').textContent = series.map(index => fmt(row.liftsMm[index], 2)).join(' / ') + ' mm';
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
    const allLifts = ui.physics.playback === 'group-lift'
      ? data.motion.frames.flatMap(f => series.map(index => f.transforms[groups[index].id]?.[14] || 0))
      : tables.rows.flatMap(row => series.map(index => row.liftsMm[index]));
    const peakLift = Math.max(1, ...allLifts);
    const liftTop = Math.ceil(peakLift);
    const liftBottom = Math.min(0, Math.floor(Math.min(...allLifts)));
    lineChart($('chartLift'), { label: text.chartLabel, x, xt, y: [liftBottom, liftTop], yt: [liftBottom, (liftBottom + liftTop) / 2, liftTop], xl: '時間 (s)', yl: text.chartAxis, cursor,
      series: series.map((groupIndex, position) => ({ color: SERIES[position], pts: trace.map(row => [row.t, row.liftsMm[groupIndex]]) })) });
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
    $('holdText').textContent = `最大 ${fmt(maximumTorque, 2)} mN·m（${at}°）。停動トルクの ${fmt(maximumTorque / (tables.const.stallTorqueNm * 1000) * 100, 2)}%。${term}の重さ ${fmt(massScale, 2)}×。静止中の摩擦方向は決まらないため、この図には含めません。`;
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
    const contact = last.contactFeasible ? '計算上の接触反力は非負です。接触時の衝撃は未計算です。' : `${term}がカムから離れる可能性があります。表示は接触を仮定した形です。`;
    $('status').textContent = `条件付き計算。${reached ? '計算上は目標に到達' : '計算上も目標に届かない'}（${fmt(last.final.servoDeg)}°）。トルク上限 ${fmt(options.stallScale * 100, 0)}%。${term}の重さ ${fmt(options.massScale, 2)}×。${contact} スプライン嵌合と材料は実機未確認です。`;
    $('gl').dataset.driveStatus = 'conditional';
    $('gl').dataset.contactFeasible = String(last.contactFeasible);
    $('gl').dataset.targetDeg = String(target);
    patternButtons.forEach(({ button, pattern }) => button.setAttribute('aria-pressed', String(pattern.servo_deg === target)));
    time = 0; paused = false; $('pause').textContent = '一時停止'; $('pause').disabled = false;
    charts(0); show(last.trace[0]);
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) { show(last.final); charts(last.final.t); $('pause').disabled = true; return; }
    previous = performance.now(); animation = requestAnimationFrame(tick);
  }
  if (hasPatterns) {
    $('patternControls').hidden = false;
    for (const pattern of data.motion.patterns) {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'lc-btn'; button.textContent = pattern.label;
      button.disabled = !drive.calculationPass;
      button.setAttribute('aria-pressed', String(pattern.servo_deg === minimum));
      button.addEventListener('click', () => start(pattern.servo_deg));
      patternButtons.push({ button, pattern });
    }
    $('patternButtons').replaceChildren(...patternButtons.map(item => item.button));
  }
  $('open').addEventListener('click', () => {
    const target = hasPatterns
      ? (data.motion.patterns.find(pattern => pattern.servo_deg > state.servoDeg + 1)?.servo_deg ?? minimum)
      : maximum;
    start(target);
  });
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
    const measured = row.id === 'coupler-structure' ? blindFloorDetail(rawInterfaces.get(row.id)) : positionalRetentionDetail(rawInterfaces.get(row.id));
    return { ...row, detail: measured || row.detail, pass: row.status === 'pass', chip: row.result };
  });
  const driveCalibrationRows = drive.calibrationRows.map(row => ({
    ...row, chip: row.pass ? '計器確認' : '計器要確認',
  }));
  if (!Array.isArray(data.drive?.calibration) && data.drive?.calibration?.meshContact) {
    const contact = data.drive.calibration.meshContact;
    driveCalibrationRows.push({ id: 'c42-contact-calibration', label: '実体積の接触計器',
      pass: contact.pass === true, chip: contact.pass ? '計器確認' : '計器要確認',
      detail: `既知の重複 ${fmt(contact.positiveCommonVolumeMm3, 3)} mm³（期待16）。離隔 ${fmt(contact.negativeCommonVolumeMm3, 3)} mm³（期待0）。` });
  }
  const hardwareRows = drive.hardwareUnknown.map((detail, index) => ({
    id: `hardware-${index}`, label: detail, pass: false, chip: '実機未確認', detail: '',
  }));
  const clearanceRows = clearanceEnvelopeRows(data.sim.clearanceEnvelope);
  const supportRows = removableSupportRows(data.print_path_review, data.print_path_evidence,
    data.print_support_geometry, data.closed_loop_support_evidence, data.first_layer_contact_evidence);
  const measuredRows = [];
  if (hasPatterns && data.verify?.exact_scene) {
    const scene = data.verify.exact_scene;
    measuredRows.push({ id: 'c42-shape', label: '動作中の実STLの干渉',
      pass: data.verify.pass === true, chip: data.verify.pass ? '形状適合' : '形状要確認',
      detail: `${scene.poseSamples}姿勢。${scene.uniquePairs}組。許可範囲外の干渉 ${(scene.violations || []).length}件。停止位置だけでなく切替途中も検査しています。` });
  }
  if (hasPatterns && data.continuous_path_support_evidence?.overall) {
    const paths = data.continuous_path_support_evidence.overall;
    measuredRows.push({ id: 'c42-extrusion', label: '実G-codeの押出経路の支持',
      pass: paths.pass === true, chip: paths.pass ? '経路適合' : '経路要確認',
      detail: `${paths.findingCount}区間。支持が成立しない区間 ${paths.failedFindingCount}件。実線幅と印刷順序を使って検査しています。` });
  }
  if (hasPatterns && data.first_layer_contact_evidence?.overall) {
    const bed = data.first_layer_contact_evidence.overall;
    measuredRows.push({ id: 'c42-bed', label: '実G-codeの初層の接地',
      pass: bed.pass === true, chip: bed.pass ? '接地適合' : '接地要確認',
      detail: `${bed.objectMaterialCount}部品・材料の組。接地と支えの形状が成立しない組 ${bed.failedObjectMaterialCount}件。取り外す力とベッドへの接着力は実物未確認です。` });
  }
  const checkRows = [
    { id: 'drive-overall', label: '駆動接続と1自由度計算', pass: drive.calculationPass,
      chip: drive.calculationPass ? '計算内成立' : '接続未成立', detail: drive.summary },
    ...measuredRows, ...clearanceRows, ...supportRows, ...connectionRows, ...driveCalibrationRows, ...hardwareRows,
    ...calculationRows.map(row => ({ ...row, detail: calculationDetail(row), chip: row.pass ? '計算確認' : '計算要確認' })),
  ];
  $('checks').replaceChildren(...checkRows.map(row => {
    const li = document.createElement('li'), chip = document.createElement('span'), text = document.createElement('span');
    chip.className = `chip ${row.pass ? 'ok' : 'warn'}`; chip.textContent = row.chip; text.textContent = row.label + (row.detail ? `。${row.detail}` : ''); li.append(chip, text); return li;
  }));
  $('simLimits').textContent = ui.physics.simLimits ?? '接続形状の検査を前提にした条件付きの1自由度計算です。計算と表示する動作形状は公称位相のままです。回転遊びは実STLの接触角を1:1で足した保守的な±位相差と、その範囲の幾何学的高さ幅だけを示します。位置精度は保証しません。スプライン嵌合と材料は含めません。この高さ幅の動的計算と全組み合わせ干渉は未検証です。格子の自重によるカム接点摩擦を含めます。案内の横予圧は不明です。追従の可否は鉛直加速度から判定します。浮き上がり後の飛行や衝撃は解きません。剛体のたわみ、破損、熱は扱いません。Pythonとブラウザの同じ条件の計算を数値で照合しています。';
  if (hasPatterns) $('simLimits').textContent = ui.physics.simLimits ?? '接続形状の検査を前提にした条件付きの計算です。実STLから質量と慣性を求めています。摩擦係数0.30を仮定します。格子の接点摩擦と案内の横荷重を含めます。円盤外周の支持面にも摩擦を見込みます。天面上向きで自重により追従する設計です。負の接触反力が必要な動作は不成立とします。回転遊びによる高さ幅は幾何学的な値です。その全組み合わせの動的干渉は未検証です。スプライン嵌合と保持力は実物で確かめる必要があります。';
  for (const id of ['open', 'close', 'profile', 'torque', 'mass']) $(id).disabled = !drive.calculationPass;
  holdChart(); charts();
  if (drive.calculationPass && !hasPatterns) start(maximum);
  else {
    $('status').textContent = drive.summary;
    $('gl').dataset.driveStatus = drive.calculationPass ? 'conditional' : 'fail';
    show({ t: 0, commandDeg: minimum, servoDeg: minimum, torqueNm: 0, liftsMm: sim.at(minimum).liftsMm });
  }
  addEventListener('pagehide', stop, { once: true });
}
