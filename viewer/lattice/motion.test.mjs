import assert from 'node:assert/strict';
import { frameAt, quintic, identity4, interpolateRigid } from './motion.mjs';
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
const rotate = (deg, z) => {
  const a = deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
  return [1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, s * z, (1 - c) * z, 1];
};
for (const fraction of [0.1, 0.5, 0.9]) {
  const actual = interpolateRigid(rotate(0, 40), rotate(90, 40), fraction);
  const expected = rotate(90 * fraction, 40);
  actual.forEach((value, index) => assert.ok(Math.abs(value - expected[index]) < 1e-9));
  assert.ok(Math.abs(actual[5] * actual[10] - actual[6] * actual[9] - 1) < 1e-12);
}
assert.deepEqual(interpolateRigid(identity4(), frames[1].transforms.top, .5).slice(12, 15), [1, 2, 3]);
const rotateZ = (deg, px = 0, py = 0) => {
  const a = deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
  return [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0,
    (1 - c) * px + s * py, -s * px + (1 - c) * py, 0, 1];
};
for (const [start, end] of [[0, 150], [150, 0], [149, 150], [-120, 30]]) {
  for (const fraction of [.1, .5, .761, .9]) {
    const actual = interpolateRigid(rotateZ(start, 12, -7), rotateZ(end, 12, -7), fraction);
    const expected = rotateZ(start + (end - start) * fraction, 12, -7);
    actual.forEach((value, index) => assert.ok(Math.abs(value - expected[index]) < 1e-9,
      `Z rotation ${start} to ${end} at ${fraction}, element ${index}`));
    const point = [49, 0, 50];
    const transformedZ = actual[2] * point[0] + actual[6] * point[1] + actual[10] * point[2] + actual[14];
    assert.equal(transformedZ, 50, 'cam height must stay fixed throughout Z rotation');
  }
}
const zFrames = [149, 150].map(degree => ({ servo_deg: degree + 15,
  transforms: { cam_disk: rotateZ(degree) } }));
const disk = frameAt(zFrames, 164.761).transforms.cam_disk;
assert.ok(Math.abs(disk[0] - Math.cos(149.761 * Math.PI / 180)) < 1e-12);
assert.equal(disk[10], 1, 'C4-2 cam must not flip below the box at a fractional servo angle');
for (const model of ['mystery-box-sg92r-c3', 'mystery-box-sg92r-c4', 'mystery-box-sg92r-c4-2']) {
  for (const mode of ['physics', 'assembly']) {
    const url = new URL(workspaceHref(mode, model), 'http://localhost:3000');
    assert.equal(url.pathname, '/viewer/lattice/index.html');
    assert.equal(url.searchParams.get('model'), model);
    assert.equal(url.searchParams.get('mode'), mode);
  }
}
console.log('lattice motion: endpoints, midpoint, quintic easing, and workspace routing passed');
