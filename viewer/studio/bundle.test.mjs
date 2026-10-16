import assert from 'node:assert/strict';
import { buildRequest } from './bundle.js';
import { normalizeLedger } from './parts.js';

let release;
const pendingImage = new Promise(resolve => { release = resolve; });
const state = {
  partModes: { 'round-bot-studio-plate-plate-lid-3.stl': 'ghost', 'unloaded.stl': 'hidden' },
  model: 'round-bot', frame: 'stl-mm-zup', files: [],
  layout: {
    kind: 'plate', id: 'plate-sha', source3mf: 'round-bot-PLA.gcode.3mf', source3mfSha256: 'plate-sha',
    parts: [{ file: 'round-bot-studio-plate-plate-lid-3.stl', sourcePart: 'lid', sourceFile: 'round-bot-lid.stl', objectId: '3', buildTransform: [1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 0], sha256: 'part-sha' }],
  },
  draft: { message: '送信時の内容', items: [
    { id: 'section-1', type: 'section', plane: {}, shapes: [{ id: 'shape-1', kind: 'text', intent: 'target', nodes: [], text: '旧図形', note: '旧意図を維持' }], offset: 0 },
    { id: 'pin-1', type: 'pin', file: 'round-bot-studio-plate-plate-lid-3.stl', note: '最初のメモ' },
  ] },
};
const viewport = {
  getMeshes: () => [{ userData: { file: 'round-bot-studio-plate-plate-lid-3.stl', unitScale: 1, bbox: { min: [0, 0, 0], max: [1, 1, 1] }, placed: true } }],
  screenshot: () => '3d-image', cameraInfo: () => ({}),
};
const sections = { getLoops: () => ({ loops: [] }) };
const sketch = { exportPNG: () => pendingImage, exportSVG: () => '<svg/>' };
const resultPromise = buildRequest({ store: { state, status() {} }, viewport, sections, sketch });
// 断面画像を待つ間に入力とモデルが変わっても、送る内容が混ざらない。
state.model = 'pipe-joint';
state.frame = 'preview-m-yup';
state.layout = { kind: 'assembled' };
state.draft.message = '後から書いた内容';
state.draft.items[1].note = '後からのメモ';
state.draft.items.push({ id: 'pin-2', type: 'pin' });
release('section-image');
const { request } = await resultPromise;
assert.equal(request.model, 'round-bot');
assert.equal(request.frame, 'stl-mm-zup');
assert.equal(request.message, '送信時の内容');
assert.equal(request.items.length, 2);
assert.equal(request.items[1].note, '最初のメモ');
assert.equal(state.draft.items[1].note, '後からのメモ');
assert.deepEqual(request.layout, { kind: 'plate', id: 'plate-sha', source3mf: 'round-bot-PLA.gcode.3mf', source3mfSha256: 'plate-sha', manifestVersion: 1 });
assert.equal(request.files[0].sourcePart, 'lid');
assert.equal(request.files[0].objectId, '3');
assert.deepEqual(request.files[0].buildTransform, [1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 0]);
assert.equal(request.files[0].sourceFile, 'round-bot-lid.stl');
assert.equal(request.files[0].sha256, 'part-sha');
assert.equal(request.items[1].sourcePart, 'lid');
assert.equal(request.items[1].objectId, '3');
assert.deepEqual(request.items[1].buildTransform, [1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 0]);
assert.equal(request.items[1].sourceFile, 'round-bot-lid.stl');
assert.equal(request.items[0].shapes[0].intent, 'target');
assert.equal(request.items[0].shapes[0].text, '旧図形');
assert.equal(request.items[0].shapes[0].note, '旧意図を維持');
// 送る時点で透過・非表示だった読み込み済みの STL を残す（読み込んでいない STL は書かない）
assert.deepEqual(request.partModes, { 'round-bot-studio-plate-plate-lid-3.stl': 'ghost' });

// 部品台帳があるとき: 指示に部品の id と名前、依頼に呼び名の変更を入れる。見え方のキーは部品 id
const ledger = normalizeLedger({
  version: 1, model: 'box',
  groups: [{ id: 'shell', label: '外装', color: '#ccc' }],
  parts: [
    { id: 'housing', label: '外装', systemLabel: '外装', group: 'shell', kind: 'printed', file: 'box-part-housing.stl' },
    { id: 'cam_0', label: 'カム 0', systemLabel: 'カム 0', group: 'shell', kind: 'printed', file: 'box-part-cam_0.stl' },
  ],
}, 'box');
let hoverCleared = false;
const ledgerState = {
  model: 'box', frame: 'blender-mm', files: [], layout: { kind: 'assembled' },
  ledger,
  partNames: { cam_0: { label: '最初のカム' }, housing: { label: '外装' }, gone: { label: '消えた部品' } },
  partModes: { housing: 'ghost', cam_0: 'hidden', unloaded: 'ghost' },
  draft: { message: '', items: [
    { id: 'f1', type: 'faces', file: 'box-part-cam_0.stl', summary: {}, faceIds: [1, 2], note: '' },
    { id: 'm1', type: 'measure', file: 'box-part-cam_0.stl', fileB: 'box-part-housing.stl', a: [0, 0, 0], b: [1, 0, 0], distance: 1 },
    { id: 'p1', type: 'pin', file: 'plain.stl', point: [0, 0, 0], normal: [0, 0, 1] },
  ] },
};
const ledgerViewport = {
  getMeshes: () => [
    { userData: { file: 'box-part-housing.stl', partId: 'housing', unitScale: 1, bbox: { min: [0, 0, 0], max: [1, 1, 1] } } },
    { userData: { file: 'box-part-cam_0.stl', partId: 'cam_0', unitScale: 1, bbox: { min: [0, 0, 0], max: [1, 1, 1] } } },
  ],
  screenshot: () => '3d-image', cameraInfo: () => ({}), setHoverParts: (keys) => { hoverCleared = keys.length === 0; },
};
const ledgerResult = await buildRequest({ store: { state: ledgerState, status() {} }, viewport: ledgerViewport, sections, sketch });
assert.equal(hoverCleared, true);
const [face, measure, pin] = ledgerResult.request.items;
assert.equal(face.partId, 'cam_0');
assert.equal(face.partLabel, '最初のカム');
assert.equal(face.partSystemLabel, 'カム 0');
assert.equal(measure.partIdB, 'housing');
assert.equal(measure.partLabelB, '外装');
assert.equal('partId' in pin, false);
assert.equal(ledgerResult.request.files[1].partId, 'cam_0');
assert.equal(ledgerResult.request.files[1].partLabel, '最初のカム');
assert.deepEqual(ledgerResult.request.partModes, { housing: 'ghost', cam_0: 'hidden' });
assert.deepEqual(ledgerResult.request.partNames, { cam_0: { label: '最初のカム', systemLabel: 'カム 0' } });
// 呼び名を変えていなければ partNames は入れない（台帳が無いときも）
ledgerState.partNames = {};
assert.equal('partNames' in (await buildRequest({ store: { state: ledgerState, status() {} }, viewport: ledgerViewport, sections, sketch })).request, false);
assert.equal('partNames' in request, false);
console.log('bundle: 33 assertions passed');
