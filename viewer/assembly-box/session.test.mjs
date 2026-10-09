import test from 'node:test';
import assert from 'node:assert/strict';
import { SESSION_VERSION, createSession, parseStepParam, restoreSession } from './session.mjs';
import { SHA, STEPS } from './steps.mjs';

const partIds = [...Array.from({ length: 22 }, (_, index) => String(index + 1).padStart(2, '0')), 'S1', 'S2', 'S3'];
const valid = createSession({ cadSha: SHA, stepTitle: STEPS[4].title, fraction: 0.35, selected: '22', speed: 2, dwell: 4, shell: 'transparent', wires: true, autoCamera: false, mode: 'single', phase: 'motion' });
const gateTitles = [STEPS[9].title, STEPS[23].title, STEPS[24].title];
const restore = value => restoreSession(value, { cadSha: SHA, steps: STEPS, partIds, gateTitles });

test('手順タイトルは復元用の安定キーとして一意', () => {
  assert.equal(new Set(STEPS.map(step => step.title)).size, STEPS.length);
});

test('有効なセッションを停止状態へ復元する', () => {
  assert.deepEqual(restore(valid), { index: 4, fraction: 0.35, selected: '22', speed: 2, dwell: 4, shell: 'transparent', wires: true, autoCamera: false, mode: 'single', phase: 'motion' });
});

test('不正な値、破損値、版違いを無効にする', () => {
  assert.equal(restore(null), null);
  assert.equal(restore('broken'), null);
  assert.equal(restore({ ...valid, version: SESSION_VERSION + 1 }), null);
  assert.equal(restore({ ...valid, cadSha: 'old' }), null);
  assert.equal(restore({ ...valid, fraction: 1.1 }), null);
});

test('未知の手順と部品を無効にする', () => {
  assert.equal(restore({ ...valid, stepTitle: '削除された手順' }), null);
  assert.equal(restore({ ...valid, selected: '99' }), null);
});

test('自動再生の確認待ちは解除せず復元する', () => {
  const state = restore({ ...valid, stepTitle: STEPS[9].title, mode: 'auto', phase: 'gate' });
  assert.equal(state.mode, 'auto');
  assert.equal(state.phase, 'gate');
  assert.equal(restore({ ...valid, mode: 'auto', phase: 'gate' }), null);
});

test('URLのstepは10進整数かつ範囲内だけ受け付ける', () => {
  assert.equal(parseStepParam('4', STEPS.length), 4);
  for (const value of ['', '-1', '1.5', '2x', String(STEPS.length)]) assert.equal(parseStepParam(value, STEPS.length), null);
});
