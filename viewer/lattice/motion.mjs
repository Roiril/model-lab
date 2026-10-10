export function quintic(t) {
  const x = Math.max(0, Math.min(1, Number(t) || 0));
  return x * x * x * (x * (x * 6 - 15) + 10);
}

export function identity4() {
  return new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
}

// 現在の機構はX軸回転と並進だけを使う。同じ回転中心を保つ剛体補間。
// 行列要素をそのまま混ぜると、回転中に部品が縮むため使わない。
export function interpolateRigid(a, b, fraction) {
  const f = Math.max(0, Math.min(1, fraction));
  if (f === 0) return Array.from(a);
  if (f === 1) return Array.from(b);
  const angleA = Math.atan2(a[6], a[5]), angleB = Math.atan2(b[6], b[5]);
  const delta = Math.atan2(Math.sin(angleB - angleA), Math.cos(angleB - angleA));
  const angle = angleA + delta * f, c = Math.cos(angle), s = Math.sin(angle);
  const out = [1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, 0, 0, 1];
  out[12] = a[12] + (b[12] - a[12]) * f;
  if (Math.abs(delta) < 1e-8) {
    out[13] = a[13] + (b[13] - a[13]) * f;
    out[14] = a[14] + (b[14] - a[14]) * f;
    return out;
  }
  const cd = Math.cos(delta), sd = Math.sin(delta);
  const ty = b[13] - (cd * a[13] - sd * a[14]);
  const tz = b[14] - (sd * a[13] + cd * a[14]);
  const d = (1 - cd) ** 2 + sd ** 2;
  const py = ((1 - cd) * ty - sd * tz) / d;
  const pz = (sd * ty + (1 - cd) * tz) / d;
  const cf = Math.cos(delta * f), sf = Math.sin(delta * f);
  out[13] = cf * a[13] - sf * a[14] + (1 - cf) * py + sf * pz;
  out[14] = sf * a[13] + cf * a[14] - sf * py + (1 - cf) * pz;
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
