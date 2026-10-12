export function quintic(t) {
  const x = Math.max(0, Math.min(1, Number(t) || 0));
  return x * x * x * (x * (x * 6 - 15) + 10);
}

export function identity4() {
  return new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
}

// 回転軸が X でも Z でもない行列（Y 軸や斜め軸の回転）を剛体のまま補間する。
// 2 つの姿勢の差 D = B·A⁻¹ をらせん運動（軸まわりの回転 + 軸方向の並進）として分け、
// 回転角と並進を同じ割合 f で進める。行列要素を混ぜると回転中に部品が縮む。
const matrixRotation = m => [[m[0], m[4], m[8]], [m[1], m[5], m[9]], [m[2], m[6], m[10]]];
const matrixProduct = (p, q) => p.map((row, i) => [0, 1, 2].map(j => row[0] * q[0][j] + row[1] * q[1][j] + row[2] * q[2][j]));
const matrixTranspose = m => [0, 1, 2].map(i => [m[0][i], m[1][i], m[2][i]]);
const matrixVector = (m, v) => m.map(row => row[0] * v[0] + row[1] * v[1] + row[2] * v[2]);
const cross3 = (u, v) => [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
const dot3 = (u, v) => u[0] * v[0] + u[1] * v[1] + u[2] * v[2];

function axisRotation(axis, angle) {
  const c = Math.cos(angle), s = Math.sin(angle), t = 1 - c, [x, y, z] = axis;
  return [[c + x * x * t, x * y * t - z * s, x * z * t + y * s],
    [y * x * t + z * s, c + y * y * t, y * z * t - x * s],
    [z * x * t - y * s, z * y * t + x * s, c + z * z * t]];
}

function axisAngle(R) {
  const w = [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]];
  const sine = Math.hypot(...w) / 2, cosine = (R[0][0] + R[1][1] + R[2][2] - 1) / 2;
  const angle = Math.atan2(sine, cosine);
  if (sine > 1e-9) return { axis: w.map(n => n / (2 * sine)), angle };
  if (cosine > 0) return { axis: [0, 0, 1], angle: 0 };
  // 180°に近いときは対称成分から軸を取り、向きは非対角要素の符号で決める。
  const u = [0, 1, 2].map(i => Math.sqrt(Math.max(0, (R[i][i] - cosine) / (1 - cosine))));
  const major = u.indexOf(Math.max(...u));
  for (const i of [0, 1, 2]) if (i !== major && R[major][i] + R[i][major] < 0) u[i] = -u[i];
  return { axis: u, angle };
}

function interpolateScrew(a, b, f) {
  const Ra = matrixRotation(a), Rb = matrixRotation(b), ta = a.slice(12, 15), tb = b.slice(12, 15);
  const Rd = matrixProduct(Rb, matrixTranspose(Ra));
  const rotatedStart = matrixVector(Rd, ta);
  const td = [0, 1, 2].map(i => tb[i] - rotatedStart[i]);
  const { axis, angle } = axisAngle(Rd);
  if (angle < 1e-8) {
    const out = Array.from(a);
    for (const i of [12, 13, 14]) out[i] = a[i] + (b[i] - a[i]) * f;
    return out;
  }
  const along = dot3(td, axis), parallel = axis.map(n => n * along);
  const perpendicular = td.map((n, i) => n - parallel[i]);
  const turn = cross3(axis, perpendicular), cot = 1 / Math.tan(angle / 2);
  const pivot = perpendicular.map((n, i) => (n + cot * turn[i]) / 2);
  const Rf = axisRotation(axis, angle * f), R = matrixProduct(Rf, Ra);
  const spun = matrixVector(Rf, ta), pivoted = matrixVector(Rf, pivot);
  const t = [0, 1, 2].map(i => spun[i] + pivot[i] - pivoted[i] + parallel[i] * f);
  return [R[0][0], R[1][0], R[2][0], 0, R[0][1], R[1][1], R[2][1], 0, R[0][2], R[1][2], R[2][2], 0, t[0], t[1], t[2], 1];
}

// C3/C4-1はX回転、C4-2はZ回転。どちらも回転中心を保つ剛体補間。
// それ以外の軸（Y軸・斜め軸）は interpolateScrew へ回す。
// 行列要素をそのまま混ぜると、回転中に部品が縮むため使わない。
export function interpolateRigid(a, b, fraction) {
  const f = Math.max(0, Math.min(1, fraction));
  if (f === 0) return Array.from(a);
  if (f === 1) return Array.from(b);
  const aroundZ = [a, b].every(matrix => Math.abs(matrix[10] - 1) < 1e-9
    && [2, 6, 8, 9].every(index => Math.abs(matrix[index]) < 1e-9));
  const aroundX = [a, b].every(matrix => Math.abs(matrix[0] - 1) < 1e-6
    && [1, 2, 4, 8].every(index => Math.abs(matrix[index]) < 1e-6));
  if (!aroundZ && !aroundX) return interpolateScrew(a, b, f);
  const angleA = aroundZ ? Math.atan2(a[1], a[0]) : Math.atan2(a[6], a[5]);
  const angleB = aroundZ ? Math.atan2(b[1], b[0]) : Math.atan2(b[6], b[5]);
  const delta = Math.atan2(Math.sin(angleB - angleA), Math.cos(angleB - angleA));
  const angle = angleA + delta * f, c = Math.cos(angle), s = Math.sin(angle);
  const out = aroundZ
    ? [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    : [1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, 0, 0, 1];
  const first = aroundZ ? 12 : 13, second = aroundZ ? 13 : 14;
  const axial = aroundZ ? 14 : 12;
  out[axial] = a[axial] + (b[axial] - a[axial]) * f;
  if (Math.abs(delta) < 1e-8) {
    out[first] = a[first] + (b[first] - a[first]) * f;
    out[second] = a[second] + (b[second] - a[second]) * f;
    return out;
  }
  const cd = Math.cos(delta), sd = Math.sin(delta);
  const ty = b[first] - (cd * a[first] - sd * a[second]);
  const tz = b[second] - (sd * a[first] + cd * a[second]);
  const d = (1 - cd) ** 2 + sd ** 2;
  const py = ((1 - cd) * ty - sd * tz) / d;
  const pz = (sd * ty + (1 - cd) * tz) / d;
  const cf = Math.cos(delta * f), sf = Math.sin(delta * f);
  out[first] = cf * a[first] - sf * a[second] + (1 - cf) * py + sf * pz;
  out[second] = sf * a[first] + cf * a[second] - sf * py + (1 - cf) * pz;
  return out;
}

export function transformsAt(frames, value, key = 'progress') {
  if (!frames?.length) return {};
  if (value <= frames[0][key]) return frames[0].transforms;
  if (value >= frames.at(-1)[key]) return frames.at(-1).transforms;
  let high = 1;
  while (value > frames[high][key]) high++;
  const a = frames[high - 1], b = frames[high];
  const f = (value - a[key]) / (b[key] - a[key]);
  const result = {};
  for (const id of new Set([...Object.keys(a.transforms), ...Object.keys(b.transforms)])) {
    result[id] = interpolateRigid(a.transforms[id] || identity4(), b.transforms[id] || identity4(), f);
  }
  return result;
}

export function frameAt(frames, servoDeg) {
  if (!Array.isArray(frames) || frames.length === 0) return { servo_deg: servoDeg, transforms: {} };
  if (servoDeg <= frames[0].servo_deg) return frames[0];
  const last = frames[frames.length - 1];
  if (servoDeg >= last.servo_deg) return last;
  return { servo_deg: servoDeg, transforms: transformsAt(frames, servoDeg, 'servo_deg') };
}
