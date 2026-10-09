import assert from 'node:assert/strict';
import { B3_MODEL, WORKSPACES, WORKSPACE_PAGES, hasWorkspace, workspaceHref, readSession, writeSession, resolveTheme } from './workspace.mjs';

assert.equal(resolveTheme('dark', 'light'), 'dark');
assert.equal(resolveTheme(null, 'light'), 'light');
assert.equal(resolveTheme('invalid', 'dark'), 'dark');
assert.equal(resolveTheme(null, null), null);
assert.equal(resolveTheme('system', 'invalid'), null);

assert.equal(new Set(WORKSPACES.map(item => item.id)).size, 3);
assert.equal(workspaceHref('studio', 'box with space/&'), '/?model=box%20with%20space%2F%26');
for (const mode of ['physics', 'assembly']) {
  const url = new URL(workspaceHref(mode, 'another-model'), 'http://localhost:3000');
  assert.equal(url.searchParams.get('model'), B3_MODEL);
  assert.equal(url.pathname, `/viewer/${mode}-box/index.html`);
}
assert.throws(() => workspaceHref('unknown'), RangeError);
// 画面を登録したモデルは自分の画面へ。登録していないモデルは押せない
for (const mode of ['physics', 'assembly']) {
  const url = new URL(workspaceHref(mode, 'servo-lid-cube'), 'http://localhost:3000');
  assert.equal(url.pathname, WORKSPACE_PAGES['servo-lid-cube'][mode]);
  assert.equal(url.searchParams.get('model'), 'servo-lid-cube');
  assert.equal(hasWorkspace(mode, 'servo-lid-cube'), true);
  assert.equal(hasWorkspace(mode, B3_MODEL), true);
  assert.equal(hasWorkspace(mode, 'another-model'), false);
}
assert.equal(hasWorkspace('studio', 'another-model'), true);
const memory = new Map();
globalThis.sessionStorage = { getItem: key => memory.get(key) ?? null, setItem: (key, value) => memory.set(key, value) };
assert.equal(readSession('missing', 'fallback'), 'fallback');
assert.equal(writeSession('assembly', { fraction: .4 }), true);
assert.deepEqual(readSession('assembly'), { fraction: .4 });
memory.set('model-lab.assembly', 'broken');
assert.equal(readSession('assembly', 'fallback'), 'fallback');
globalThis.sessionStorage = { getItem() { throw Error('blocked'); }, setItem() { throw Error('blocked'); } };
assert.equal(readSession('assembly', 'fallback'), 'fallback');
assert.equal(writeSession('assembly', {}), false);
console.log('workspace: routing and session storage passed');
