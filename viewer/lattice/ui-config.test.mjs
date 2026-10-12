import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { createSim, drivePresentation } from './sim.mjs';
import {
  DEFAULT_MODEL, calibrationLimitText, legendEntries, modelEntries, normalizeUi, physicsSeries, physicsText, posedTransforms, resolveModel, uiSource,
} from './ui-config.mjs';

const asset = name => JSON.parse(readFileSync(new URL(`./assets/${name}.json`, import.meta.url), 'utf8'));
const close = (a, b, label, tolerance = 1e-9) => assert.ok(Math.abs(a - b) < tolerance, `${label}: ${a} != ${b}`);
const RAD = Math.PI / 180;

test('model names: any asset name is accepted, path tricks fall back', () => {
  assert.equal(resolveModel('tangible-pixel-cube'), 'tangible-pixel-cube');
  assert.equal(resolveModel('mystery-box-sg92r-c4-2'), 'mystery-box-sg92r-c4-2');
  for (const bad of [null, '', '../secret', 'a/b', 'a\\b', '.hidden', 'x..y', 'a b', 'x'.repeat(81)]) assert.equal(resolveModel(bad), DEFAULT_MODEL, String(bad));
});

// 書き出し済みの 3 モデルは ui 節を持たず（過去モデルの監査がバイト一致を見る）、モデル名から以前の固定値を引く。
const FORMER = {
  'mystery-box-sg92r-c3': { label: 'C3', title: '立方格子の波', nav: 'C3 立方格子', open: '波を進める', base: 'exports', rotation: 5, dims: '76〜80 mm（生成値を優先）', setup: /^箱の外でSG92Rを90°にして付属ホーンと駆動歯車を付けます/ },
  'mystery-box-sg92r-c4': { label: 'C4-1', title: '六角格子の呼吸', nav: 'C4-1 六角格子', open: '持ち上げる', base: 'exports', rotation: 5, dims: '76 × 76 mm（設計値）', setup: /^SG92Rを90°にして付属ホーンを付けます/ },
  'mystery-box-sg92r-c4-2': { label: 'C4-2', title: '六角格子の凹み', nav: 'C4-2 六角格子', open: '次の場所へ', base: 'prints', rotation: 1, dims: '76〜80 mm（生成値を優先）', setup: /^箱の外で付属ホーンをホーン受けへ入れます/ },
};
for (const [model, former] of Object.entries(FORMER)) {
  test(`${model}: legacy ui reproduces the former fixed values`, () => {
    const data = asset(model);
    assert.equal('ui' in data, false, 'committed asset carries no ui node');
    const ui = normalizeUi(uiSource(data, model), { model, partIds: data.parts.map(part => part.id), groupIds: data.simTables.groups.map(group => group.id) });
    assert.equal(ui.label, former.label);
    assert.equal(ui.displayName, `住人の箱 ${former.label}`);
    assert.equal(ui.navLabel, former.nav);
    assert.equal(ui.physics.title, former.title);
    assert.equal(ui.physics.playback, 'group-lift');
    assert.equal(ui.physics.term, '格子');
    assert.equal(ui.print.downloadBase, former.base);
    assert.equal(ui.dimensionsFallback, former.dims);
    assert.match(ui.assembly.servoSetup, former.setup);
    assert.match(calibrationLimitText(ui.assembly), new RegExp(`^1mm以下の並進と${former.rotation}°以下の回転で検査しています。$`));
    const hasPatterns = Array.isArray(data.motion.patterns) && data.motion.patterns.length > 0;
    const text = physicsText(ui, hasPatterns);
    assert.equal(text.openLabel, former.open);
    assert.equal(text.closeLabel, '戻す');
    assert.equal(text.liftLabel, hasPatterns ? '格子の上下（凹みは−）' : '格子の上昇');
    assert.equal(text.chartLabel, hasPatterns ? '各格子の凹みの時間変化' : '各格子の上昇の時間変化');
    assert.equal(text.chartAxis, hasPatterns ? '上下 (mm)' : '上昇 (mm)');
    // 折れ線は全群（5本以内）で、凡例は1部品ずつ。
    assert.deepEqual(ui.physics.seriesIndices, data.simTables.groups.map((_, index) => index));
    assert.equal(legendEntries(ui, data.parts).length, data.parts.length);
    assert.deepEqual(ui.colors, {});
  });
}

test('model switch: the three legacy models always, new ones from index.json, in navOrder', () => {
  const plain = modelEntries(null, 'mystery-box-sg92r-c3');
  assert.deepEqual(plain.map(entry => entry.id), Object.keys(FORMER));
  assert.deepEqual(plain.map(entry => entry.navLabel), Object.values(FORMER).map(former => former.nav));
  const withNew = modelEntries([{ id: 'tangible-pixel-cube', navLabel: 'TPC', navOrder: 40 }, { id: '../x', navLabel: 'bad' }, { id: 'late', navLabel: 'L' }], 'tangible-pixel-cube');
  assert.deepEqual(withNew.map(entry => entry.id), [...Object.keys(FORMER), 'tangible-pixel-cube', 'late']);
  assert.deepEqual(modelEntries([], 'not-listed').at(-1), { id: 'not-listed', navLabel: 'not-listed', navOrder: 100 });
});

test('an unknown model whose asset has no ui is refused with a clear message', () => {
  assert.equal(uiSource({}, 'mystery-box-sg92r-c4').label, 'C4-1');
  assert.throws(() => normalizeUi(uiSource({}, 'tangible-pixel-cube'), { model: 'x' }), /lattice_web\.py/);
});

const pixelIds = Array.from({ length: 25 }, (_, i) => `pixel_${Math.floor(i / 5)}_${i % 5}`);
const parts = [
  ...['body', 'bezel', 'servo_gear', 'camshaft_0', 'camshaft_1'].map(id => ({ id })),
  ...pixelIds.map(id => ({ id })),
];

test('new model ui: five of 25 pixel groups are charted, order follows the data', () => {
  const ui = normalizeUi({ label: 'TPC', physics: { playback: 'motion-frames', term: '画素', chartSeries: ['pixel_2_2', 'pixel_0_0', 'pixel_4_4'] } },
    { model: 'tangible-pixel-cube', partIds: parts.map(part => part.id), groupIds: pixelIds });
  assert.deepEqual(ui.physics.seriesIndices, [12, 0, 24]);
  assert.equal(ui.displayName, 'TPC');
  assert.equal(physicsText(ui, false).liftLabel, '画素の上昇');
  assert.equal(ui.print.downloadBase, 'prints');
  assert.equal(calibrationLimitText(ui.assembly), '');
});

test('chart series: refuses what the chart cannot draw', () => {
  const ui = chartSeries => ({ physics: { chartSeries } });
  const ctx = { model: 'm', partIds: [], groupIds: pixelIds };
  assert.throws(() => normalizeUi({ label: 'm' }, ctx), /25個.*5本まで/);
  assert.throws(() => normalizeUi(ui(pixelIds.slice(0, 6)), ctx), /1〜5個/);
  assert.throws(() => normalizeUi(ui([]), ctx), /1〜5個/);
  assert.throws(() => normalizeUi(ui(['pixel_0_0', 'pixel_0_0']), ctx), /2回/);
  assert.throws(() => normalizeUi(ui(['pixel_9_9']), ctx), /pixel_9_9/);
  assert.equal(normalizeUi(ui(pixelIds.slice(0, 5)), ctx).physics.seriesIndices.length, 5);
  assert.deepEqual(physicsSeries({ physics: { chartSeries: null } }, ['a', 'b']), [0, 1]);
});

test('ui validation: playback, colors and legend groups', () => {
  const ctx = { model: 'm', partIds: parts.map(part => part.id), groupIds: [] };
  assert.throws(() => normalizeUi({ physics: { playback: 'spin' } }, ctx), /playback/);
  assert.throws(() => normalizeUi({ print: { downloadBase: 'tmp' } }, ctx), /downloadBase/);
  assert.throws(() => normalizeUi({ colors: { body: 'red' } }, ctx), /#rrggbb/);
  assert.throws(() => normalizeUi({ colors: { nothing: '#112233' } }, ctx), /nothing/);
  assert.throws(() => normalizeUi({ legendGroups: [{ label: 'x' }] }, ctx), /parts.*prefix/);
  assert.throws(() => normalizeUi({ legendGroups: [{ label: 'x', prefix: 'zzz' }] }, ctx), /該当する部品がありません/);
  assert.throws(() => normalizeUi({ legendGroups: [{ label: 'x', parts: ['ghost'] }] }, ctx), /ghost/);
});

test('legend groups collapse the 25 pixels into one entry and colour them', () => {
  const ui = normalizeUi({ legendGroups: [
    { label: '画素', prefix: 'pixel_', color: '#e69f00' },
    { label: 'カム軸', parts: ['camshaft_0', 'camshaft_1'] },
  ], colors: { body: '#cccccc' } }, { model: 'm', partIds: parts.map(part => part.id), groupIds: [] });
  const entries = legendEntries(ui, parts);
  assert.deepEqual(entries.map(entry => entry.label), ['画素', 'カム軸', 'body', 'bezel', 'servo_gear']);
  assert.equal(entries[0].ids.length, 25);
  assert.equal(ui.colors.pixel_3_1, '#e69f00');
  assert.equal(ui.colors.body, '#cccccc');
});

// サーボ角の時系列から、全部品を motion.frames の補間で動かす。
const rotateZAbout = (deg, px, py) => {
  const a = deg * RAD, c = Math.cos(a), s = Math.sin(a);
  return [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, (1 - c) * px + s * py, -s * px + (1 - c) * py, 0, 1];
};
const rotateYAbout = (deg, pz) => {
  const a = deg * RAD, c = Math.cos(a), s = Math.sin(a);
  return [c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, -pz * s, 0, pz * (1 - c), 1];
};
const height = (i, deg) => (1 + (i % 5)) * deg / 90;   // mm。画素ごとに傾きが違う。
const frameAtDeg = deg => ({ servo_deg: deg, transforms: {
  servo_gear: rotateZAbout(deg, 10, 5), camshaft_0: rotateYAbout(2 * deg, 20),
  ...Object.fromEntries(pixelIds.map((id, i) => [id, [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, i, 0, height(i, deg), 1]])),
} });
const frames = Array.from({ length: 10 }, (_, k) => frameAtDeg(k * 10));   // 10°刻み。間は補間。
const tables = {
  model: 'synthetic', limitsDeg: [0, 90], duration_s: 0.6, contactModel: 'gravity_one_sided', contactBoundariesDeg: [],
  groups: pixelIds.map(id => ({ id, label: id, massKg: 0.001 })),
  rows: Array.from({ length: 91 }, (_, deg) => ({
    servoDeg: deg, inertiaRestKgm2: 1e-6, inertiaGroupsKgm2: 1e-7, dMGroupsDqKgm2PerRad: 0, gravityRestNm: 0, gravityGroupsNm: 0,
    liftsMm: pixelIds.map((_, i) => height(i, deg)),
    dLiftDqMPerRad: pixelIds.map((_, i) => (1 + (i % 5)) / 90 / RAD / 1000), d2LiftDq2MPerRad2: pixelIds.map(() => 0),
  })),
  const: { stallTorqueNm: 0.245, noLoadSpeedRadS: Math.PI / 0.3, controlBandRad: 4 * RAD, motorInertiaKgm2: 5e-6, servoFrictionNm: 0.001,
    gravityMS2: 9.80665, dtS: 1e-4, recordS: 0.01, settleS: 0.1, contactToleranceN: 1e-8 },
};

test('motion-frames playback follows the simulated servo angle for every part', () => {
  const ui = normalizeUi({ physics: { playback: 'motion-frames', chartSeries: ['pixel_0_0', 'pixel_0_4'] } },
    { model: 'm', partIds: parts.map(part => part.id), groupIds: pixelIds });
  const result = createSim(tables).run({ from: 0, to: 90, duration: tables.duration_s });
  assert.ok(result.trace.length > 20);
  let nonInteger = 0;
  for (const row of result.trace) {
    const out = posedTransforms(frames, row, ui, tables.groups);
    const deg = Math.min(90, Math.max(0, row.servoDeg));
    if (Math.abs(deg - Math.round(deg)) > 0.01) nonInteger += 1;
    pixelIds.forEach((id, i) => close(out[id][14], height(i, deg), `${id} height at ${deg}`, 1e-9));
    rotateZAbout(deg, 10, 5).forEach((value, k) => close(out.servo_gear[k], value, `gear[${k}] at ${deg}`));
    rotateYAbout(2 * deg, 20).forEach((value, k) => close(out.camshaft_0[k], value, `camshaft[${k}] at ${deg}`));
  }
  assert.ok(nonInteger > 5, 'trace samples fall between frames');
});

test('group-lift playback overrides the group Z and leaves the frames untouched', () => {
  const ui = normalizeUi({ physics: { playback: 'group-lift', chartSeries: pixelIds.slice(0, 5) } },
    { model: 'm', partIds: parts.map(part => part.id), groupIds: pixelIds });
  const before = JSON.stringify(frames);
  const row = { servoDeg: 0, liftsMm: pixelIds.map((_, i) => 7 + i) };   // frames の高さ（0）とは別の値
  const out = posedTransforms(frames, row, ui, tables.groups);
  pixelIds.forEach((id, i) => assert.equal(out[id][14], 7 + i));
  assert.equal(JSON.stringify(frames), before);
  assert.equal(out.servo_gear, frames[0].transforms.servo_gear);
});

test('drive checks stay closed when the report is missing (new models do not bypass them)', () => {
  assert.equal(drivePresentation(undefined, undefined).calculationPass, false);
});
