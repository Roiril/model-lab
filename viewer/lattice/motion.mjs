export function quintic(t) {
  const x = Math.max(0, Math.min(1, Number(t) || 0));
  return x * x * x * (x * (x * 6 - 15) + 10);
}

export function identity4() {
  return new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
}

export function frameAt(frames, servoDeg) {
  if (!Array.isArray(frames) || frames.length === 0) return { servo_deg: servoDeg, transforms: {} };
  if (servoDeg <= frames[0].servo_deg) return frames[0];
  const last = frames[frames.length - 1];
  if (servoDeg >= last.servo_deg) return last;
  let high = 1;
  while (high < frames.length && servoDeg > frames[high].servo_deg) high += 1;
  const a = frames[high - 1], b = frames[high];
  const fraction = (servoDeg - a.servo_deg) / (b.servo_deg - a.servo_deg || 1);
  const transforms = {};
  const ids = new Set([...Object.keys(a.transforms || {}), ...Object.keys(b.transforms || {})]);
  for (const id of ids) {
    const ma = a.transforms?.[id] || identity4();
    const mb = b.transforms?.[id] || identity4();
    transforms[id] = Array.from({ length: 16 }, (_, index) => ma[index] + (mb[index] - ma[index]) * fraction);
  }
  return { servo_deg: servoDeg, transforms };
}
