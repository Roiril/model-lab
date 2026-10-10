import assert from 'node:assert/strict';
import { frameAt, quintic } from './motion.mjs';
import { workspaceHref } from '../shared/workspace.mjs';

const frames = [
  { servo_deg: 10, transforms: { top: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1] } },
  { servo_deg: 11, transforms: { top: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 2, 4, 6, 1] } },
];
assert.equal(frameAt(frames, 0), frames[0]);
assert.equal(frameAt(frames, 20), frames[1]);
assert.deepEqual(frameAt(frames, 10.5).transforms.top.slice(12, 15), [1, 2, 3]);
assert.equal(quintic(0), 0);
assert.equal(quintic(0.5), 0.5);
assert.equal(quintic(1), 1);
for (const model of ['mystery-box-sg92r-c3', 'mystery-box-sg92r-c4']) {
  for (const mode of ['physics', 'assembly']) {
    const url = new URL(workspaceHref(mode, model), 'http://localhost:3000');
    assert.equal(url.pathname, '/viewer/lattice/index.html');
    assert.equal(url.searchParams.get('model'), model);
    assert.equal(url.searchParams.get('mode'), mode);
  }
}
console.log('lattice motion: endpoints, midpoint, quintic easing, and workspace routing passed');
