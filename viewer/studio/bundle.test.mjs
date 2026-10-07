import assert from 'node:assert/strict';
import { buildRequest } from './bundle.js';

let release;
const pendingImage = new Promise(resolve => { release = resolve; });
const state = {
  model: 'round-bot', frame: 'stl-mm-zup', files: [],
  draft: { message: '送信時の内容', items: [
    { id: 'section-1', type: 'section', plane: {}, shapes: [], offset: 0 },
    { id: 'pin-1', type: 'pin', note: '最初のメモ' },
  ] },
};
const viewport = { getMeshes: () => [], screenshot: () => '3d-image', cameraInfo: () => ({}) };
const sections = { getLoops: () => ({ loops: [] }) };
const sketch = { exportPNG: () => pendingImage, exportSVG: () => '<svg/>' };
const resultPromise = buildRequest({ store: { state, status() {} }, viewport, sections, sketch });
// 断面画像を待つ間に入力とモデルが変わっても、送る内容が混ざらない。
state.model = 'pipe-joint';
state.frame = 'preview-m-yup';
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
console.log('bundle: 6 assertions passed');
