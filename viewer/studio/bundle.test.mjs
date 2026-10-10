import assert from 'node:assert/strict';
import { buildRequest } from './bundle.js';

let release;
const pendingImage = new Promise(resolve => { release = resolve; });
const state = {
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
console.log('bundle: 19 assertions passed');
