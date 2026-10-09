// 蓋の開閉の運動方程式（1 自由度、一般化座標はサーボ角 α）。
// models/servo-lid-cube/simulate.py と同じ式。表（M・G・腕の長さ）は simulate.py が書き出した値を線形補間する。
// サーボ: τ = τ_stall·clamp((α_cmd − α)/帯, ±1) − (τ_stall/ω0)·α̇ を ±τ_stall で切る。
// 摩擦: ギア（一定）＋ ピン（リンク軸力 × 半径 × μ）。蓋が縁（θ<0）に入ると硬いばね＋減衰。
const RAD = Math.PI / 180;
const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));

export function createSim(tables) {
  const rows = tables.rows;
  const C = tables.const;
  const a0 = rows[0][0];
  const step = rows[1][0] - rows[0][0];
  function at(alphaDeg) {
    let f = (alphaDeg - a0) / step;
    f = clamp(f, 0, rows.length - 1.0001);
    const i = Math.floor(f), t = f - i, r0 = rows[i], r1 = rows[i + 1];
    const v = (k) => r0[k] + (r1[k] - r0[k]) * t;
    return { theta: v(1), mRest: v(2), mLid: v(3), gRest: v(4), gLid: v(5), dth: v(6), arm: v(7) };
  }
  // cmd(t) は目標のサーボ角（度）。返り値の trace は [t, θ, α, τ] を record 秒ごと。
  function run({ cmd, tEnd, alphaStart, stallScale = 1, massScale = 1, record = 0.005, dt = C.dt }) {
    const stall = C.stall * stallScale;
    let alpha = alphaStart * RAD, w = 0, t = 0, next = 0;
    let impact = 0, peakTau = 0;
    const trace = [];
    while (t < tEnd) {
      const e = at(alpha / RAD);
      const m = e.mRest + massScale * e.mLid;
      const g = e.gRest + massScale * e.gLid;
      const u = clamp((cmd(t) * RAD - alpha) / C.band, -1, 1);
      const tau = clamp(stall * u - (stall / C.omega0) * w, -stall, stall);
      const fl = e.arm > 1e-6 ? Math.abs(g) / e.arm : 0;
      const fr = C.servo_fric + C.mu * fl * C.pin_r * 2 * 0.5;
      let rim = 0;
      if (e.theta < 0) {
        rim = -(C.k_rim * e.theta * RAD + C.c_rim * w * e.dth) * e.dth;
        if (w * e.dth < 0) impact = Math.max(impact, Math.abs(w * e.dth));
      }
      let net = tau - g + rim;
      if (Math.abs(w) > 1e-4) net -= Math.sign(w) * fr;
      else if (Math.abs(net) <= fr) { net = 0; w = 0; }
      w += (net / m) * dt;
      alpha += w * dt;
      t += dt;
      peakTau = Math.max(peakTau, Math.abs(tau));
      if (t >= next) { trace.push([t, at(alpha / RAD).theta, alpha / RAD, tau]); next += record; }
    }
    return { trace, impact, peakTau, final: { theta: at(alpha / RAD).theta, alpha: alpha / RAD } };
  }
  // 重力だけを支えるトルク（サーボ側、N·m）。G の符号は「閉じる向きへ戻そうとする」側が正
  function holdTorque(alphaDeg, massScale = 1) {
    const e = at(alphaDeg);
    return e.gRest + massScale * e.gLid;
  }
  return { at, run, holdTorque, alphaClosed: tables.alpha_closed, alphaOpen: tables.alpha_open, const: C };
}

// 目標角の動かし方。kind = "step"（一気に切り替える）/ "ease"（始めと終わりをゆっくり）
export function profile(kind, from, to, t0 = 0, dur = 0.8) {
  if (kind === "step") return (t) => (t < t0 ? from : to);
  return (t) => {
    const x = clamp((t - t0) / dur, 0, 1);
    return from + (to - from) * x * x * (3 - 2 * x);
  };
}
