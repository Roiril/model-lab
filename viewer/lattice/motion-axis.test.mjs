import assert from 'node:assert/strict';
import test from 'node:test';
import { interpolateRigid, transformsAt } from './motion.mjs';

const close = (a, b, label, tolerance = 1e-9) => assert.ok(Math.abs(a - b) < tolerance, `${label}: ${a} != ${b}`);
const closeMatrix = (actual, expected, label) => expected.forEach((value, index) => close(actual[index], value, `${label}[${index}]`));

// 軸（単位ベクトル）まわりの回転 + 点 pivot を不動点にする並進。列優先。
function rotateAbout(axis, deg, pivot = [0, 0, 0], slide = 0) {
  const a = deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a), t = 1 - c;
  const [x, y, z] = axis;
  const R = [[c + x * x * t, x * y * t - z * s, x * z * t + y * s],
    [y * x * t + z * s, c + y * y * t, y * z * t - x * s],
    [z * x * t - y * s, z * y * t + x * s, c + z * z * t]];
  const t3 = [0, 1, 2].map(i => pivot[i] - (R[i][0] * pivot[0] + R[i][1] * pivot[1] + R[i][2] * pivot[2]) + axis[i] * slide);
  return [R[0][0], R[1][0], R[2][0], 0, R[0][1], R[1][1], R[2][1], 0, R[0][2], R[1][2], R[2][2], 0, t3[0], t3[1], t3[2], 1];
}

function assertRigid(m, label) {
  const col = k => [m[k * 4], m[k * 4 + 1], m[k * 4 + 2]];
  for (const k of [0, 1, 2]) close(Math.hypot(...col(k)), 1, `${label} column ${k} length`, 1e-12);
  for (const [i, j] of [[0, 1], [0, 2], [1, 2]]) close(col(i).reduce((n, v, r) => n + v * col(j)[r], 0), 0, `${label} columns ${i}.${j}`, 1e-12);
}

test('Y-axis rotation about a pivot keeps rotating (the former code dropped it)', () => {
  const pivot = [4, 0, 20];
  for (const fraction of [0.1, 0.25, 0.5, 0.9]) {
    const actual = interpolateRigid(rotateAbout([0, 1, 0], 0, pivot), rotateAbout([0, 1, 0], 80, pivot), fraction);
    assertRigid(actual, `y ${fraction}`);
    closeMatrix(actual, rotateAbout([0, 1, 0], 80 * fraction, pivot), `y ${fraction}`);
  }
});

test('oblique axis with a slide along the axis is a screw motion', () => {
  const axis = [1, 2, 2].map(n => n / 3), pivot = [3, -2, 5];
  const a = rotateAbout(axis, 10, pivot, 1), b = rotateAbout(axis, 130, pivot, 7);
  for (const fraction of [0.2, 0.5, 0.8]) {
    const actual = interpolateRigid(a, b, fraction);
    assertRigid(actual, `oblique ${fraction}`);
    // 同じ軸まわりの回転と並進は、角度と並進量が割合に比例する。
    closeMatrix(actual, rotateAbout(axis, 10 + 120 * fraction, pivot, 1 + 6 * fraction), `oblique ${fraction}`);
  }
});

test('half-turn and pure translation are handled', () => {
  const half = interpolateRigid(rotateAbout([0, 1, 0], 0, [0, 0, 10]), rotateAbout([0, 1, 0], 180, [0, 0, 10]), 0.5);
  closeMatrix(half, rotateAbout([0, 1, 0], 90, [0, 0, 10]), 'half turn');
  const slid = interpolateRigid(rotateAbout([0, 1, 0], 30), [...rotateAbout([0, 1, 0], 30)].map((v, i) => i === 13 ? v + 6 : v), 0.5);
  close(slid[13], 3, 'translation along Y');
});

test('X and Z paths still produce their former results', () => {
  const x = (deg, z) => { const a = deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a); return [1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, s * z, (1 - c) * z, 1]; };
  closeMatrix(interpolateRigid(x(0, 40), x(90, 40), 0.3), x(27, 40), 'x');
  const zr = deg => { const a = deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a); return [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; };
  closeMatrix(interpolateRigid(zr(0), zr(60), 0.5), zr(30), 'z');
});

test('transformsAt mixes parts that rotate about different axes', () => {
  const frames = [0, 20].map(deg => ({ progress: deg / 20, transforms: {
    gear: rotateAbout([0, 0, 1], deg, [10, 5, 0]),
    shaft: rotateAbout([0, 1, 0], 2 * deg, [0, 0, 20]),
    pixel: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 3, 4, deg / 10, 1],
  } }));
  const out = transformsAt(frames, 0.5);
  closeMatrix(out.gear, rotateAbout([0, 0, 1], 10, [10, 5, 0]), 'gear');
  closeMatrix(out.shaft, rotateAbout([0, 1, 0], 20, [0, 0, 20]), 'shaft');
  close(out.pixel[14], 1, 'pixel lift');
});
