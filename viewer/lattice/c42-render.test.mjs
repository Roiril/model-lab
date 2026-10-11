import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { frameAt, interpolateRigid } from './motion.mjs';

const build = new URL('../../models/mystery-box-sg92r-c4-2/build/', import.meta.url);
const motion = JSON.parse(readFileSync(new URL('motion.json', build), 'utf8'));
const assembly = JSON.parse(readFileSync(new URL('assembly.json', build), 'utf8'));
const rotating = ['cam_disk', 'horn_coupler', 'drive_key', 'servo_horn'];
const close = (a, b, label) => assert.ok(Math.abs(a - b) < 1e-9, `${label}: ${a} != ${b}`);

function assertZRotation(matrix, label) {
  for (const index of [2, 6, 8, 9]) close(matrix[index], 0, `${label}[${index}]`);
  close(matrix[10], 1, `${label} Z direction`);
  close(matrix[14], 0, `${label} Z displacement`);
  close(matrix[0] * matrix[5] - matrix[1] * matrix[4], 1, `${label} determinant`);
}

test('render meter rejects the former X-flip and stationary-disk failures', () => {
  const flipped = [1, 0, 0, 0, 0, -1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1];
  assert.throws(() => assertZRotation(flipped, 'known X flip'));
  const stationary = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
  assertZRotation(stationary, 'known horizontal plane');
  assert.throws(() => close(stationary[0], Math.cos(35 * Math.PI / 180), 'known missing Z rotation'));
});

test('all production motion intervals preserve the cam plane and actual Z rotation', () => {
  let checked = 0;
  for (let index = 1; index < motion.frames.length; index++) {
    const left = motion.frames[index - 1], right = motion.frames[index];
    for (const fraction of [.25, .5, .75]) {
      const degree = left.servo_deg + (right.servo_deg - left.servo_deg) * fraction;
      const angle = (degree - motion.home_servo_deg) * Math.PI / 180;
      for (const part of rotating) {
        const matrix = interpolateRigid(left.transforms[part], right.transforms[part], fraction);
        assertZRotation(matrix, `${part} at ${degree}`);
        close(matrix[0], Math.cos(angle), `${part} cosine`);
        close(matrix[1], Math.sin(angle), `${part} sine`);
        checked++;
      }
    }
  }
  assert.equal(checked, (motion.frames.length - 1) * 3 * rotating.length);
  for (const degree of [49.761, 89.713, 129.837, 164.761]) {
    const frame = frameAt(motion.frames, degree);
    for (const part of rotating) {
      assertZRotation(frame.transforms[part], `${part} at selected noninteger ${degree}`);
      close(frame.transforms[part][1], Math.sin((degree - motion.home_servo_deg) * Math.PI / 180), 'selected angle');
    }
  }
});

test('production assembly return-home keeps the rotating parts at their installed height', () => {
  const step = assembly.steps.find(row => row.id === 'return-home');
  assert.ok(step, 'return-home assembly step exists');
  let checked = 0;
  for (let i = 1; i < step.frames.length; i++) {
    for (const fraction of [.25, .5, .75]) {
      for (const part of rotating) {
        const a = step.frames[i - 1].transforms[part];
        const b = step.frames[i].transforms[part];
        const matrix = interpolateRigid(a, b, fraction);
        assertZRotation(matrix, `${part} assembly frame ${i}`);
        const angleA = Math.atan2(a[1], a[0]);
        const angleB = Math.atan2(b[1], b[0]);
        const expected = angleA + (angleB - angleA) * fraction;
        close(matrix[0], Math.cos(expected), 'assembly cosine');
        close(matrix[1], Math.sin(expected), 'assembly sine');
        checked++;
      }
    }
  }
  assert.ok(checked > 500, 'dense assembly interpolation was exercised');
});
