import { createSim } from './sim.mjs';
import { frameAt } from './motion.mjs';
import { lineChart } from '../lid-cube/lidcube.mjs';

const $ = id => document.getElementById(id);
const fmt = (value, digits = 1) => Number(value).toFixed(digits).replace(/^-0(?=\.0+$)/, '0');
const SERIES = ['--series-blue', '--series-orange', '--series-green', '--series-purple', '--series-vermillion'];

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
  let last = null, animation = 0, paused = false, time = 0, previous = 0;
  const opts = () => ({ stallScale: Number($('torque').value) / 100, massScale: Number($('mass').value), kind: $('profile').value });
  $('profile').querySelector('[value="ease"]').textContent = `${tables.duration_s} 秒でゆっくり`;
  $('open').textContent = data.model.endsWith('c4') ? '持ち上げる' : '波を進める';
  $('close').textContent = '戻す';
  $('massNote').textContent = `トルク100%は停動トルク ${fmt(tables.const.stallTorqueNm * 1000, 0)} mN·m（4.8V）。重さ1×は中実PLAの格子合計 ${fmt(groups.reduce((n, g) => n + g.massKg, 0) * 1000)} g。`;
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
    $('holdText').textContent = `最大 ${fmt(maximumTorque, 2)} mN·m（${at}°）。停動トルクの ${fmt(maximumTorque / (tables.const.stallTorqueNm * 1000) * 100, 2)}%。格子の重さ ${fmt(massScale, 2)}×。摩擦はこの図に含めません。`;
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
    const options = opts();
    last = { ...sim.run({ from: state.servoDeg, to: target, ...options, duration: tables.duration_s }), ...options };
    const reached = Math.abs(last.final.servoDeg - target) < 1;
    const contact = last.contactFeasible ? '計算上の接触反力は非負です。接触時の衝撃は未計算です。' : '格子がカムから離れる可能性があります。表示は接触を仮定した形です。';
    $('status').textContent = `${reached ? '目標に到達' : '目標に届かない'}（${fmt(last.final.servoDeg)}°）。トルク上限 ${fmt(options.stallScale * 100, 0)}%。格子の重さ ${fmt(options.massScale, 2)}×。${contact}`;
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
  const checkRows = Array.isArray(data.sim.calibration) ? data.sim.calibration : Object.entries(data.sim.calibration || {}).map(([id, row]) => ({ id, ...row }));
  $('checks').replaceChildren(...checkRows.map(row => {
    const li = document.createElement('li'), chip = document.createElement('span'), text = document.createElement('span');
    chip.className = `chip ${row.pass ? 'ok' : 'warn'}`; chip.textContent = row.pass ? '確認' : '要確認'; text.textContent = row.label + (row.detail ? `。${row.detail}` : ''); li.append(chip, text); return li;
  }));
  $('simLimits').textContent = '格子をカムに接触させた1自由度の近似です。追従の可否は鉛直加速度から判定します。浮き上がり後の飛行や衝撃は解きません。C3の接触切替では再接触速度を別に出します。摩擦とモーター慣性は仮定です。剛体のたわみ、破損、熱は扱いません。Pythonとブラウザの同じ条件の計算を数値で照合しています。';
  holdChart(); charts(); start(maximum);
  addEventListener('pagehide', stop, { once: true });
}
