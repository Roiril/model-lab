const RAD = Math.PI / 180;
const clamp = (value, low, high) => Math.max(low, Math.min(high, value));

function number(value, fallback) {
  return Number.isFinite(Number(value)) ? Number(value) : fallback;
}

export function createSim(tables) {
  if (!tables?.rows?.length || tables.rows.length < 2) throw new Error("sim table needs at least two rows");
  const rows = tables.rows;
  const C = tables.const;
  const [low, high] = tables.limitsDeg;
  const step = rows[1].servoDeg - rows[0].servoDeg;

  function at(deg) {
    const servoDeg = clamp(number(deg, low), low, high);
    const f = clamp((servoDeg - low) / step, 0, rows.length - 1.000000001);
    const index = Math.min(Math.floor(f), rows.length - 2);
    const u = f - index;
    const a = rows[index], b = rows[index + 1];
    const mix = (key) => a[key] + (b[key] - a[key]) * u;
    const mixArray = (key) => a[key].map((value, i) => value + (b[key][i] - value) * u);
    const liftsMm = mixArray("liftsMm");
    return {
      servoDeg,
      inertiaRestKgm2: mix("inertiaRestKgm2"),
      inertiaGroupsKgm2: mix("inertiaGroupsKgm2"),
      dMGroupsDqKgm2PerRad: mix("dMGroupsDqKgm2PerRad"),
      gravityRestNm: mix("gravityRestNm"),
      gravityGroupsNm: mix("gravityGroupsNm"),
      liftsMm,
      dLiftDqMPerRad: mixArray("dLiftDqMPerRad"),
      d2LiftDq2MPerRad2: mixArray("d2LiftDq2MPerRad2"),
      contactActive: tables.contactModel === "gravity_one_sided"
        ? liftsMm.map(() => true)
        : liftsMm.map((value) => value > 1e-7),
    };
  }

  function holdTorque(deg, massScale = 1) {
    const state = at(deg);
    return state.gravityRestNm + state.gravityGroupsNm * clamp(number(massScale, 1), 0.5, 4);
  }

  function run({ from, to, kind = "ease", stallScale = 1, massScale = 1, duration = tables.duration_s } = {}) {
    duration = Math.max(number(duration, tables.duration_s), C.dtS);
    stallScale = clamp(number(stallScale, 1), 0, 1);
    massScale = clamp(number(massScale, 1), 0.5, 4);
    const requestedFrom = number(from, low), requestedTo = number(to, high);
    const start = clamp(requestedFrom, low, high), target = clamp(requestedTo, low, high);
    const clippedToLimits = start !== requestedFrom || target !== requestedTo;
    let q = start * RAD, velocity = 0, t = 0, nextRecord = C.recordS;
    const endTime = duration + C.settleS;
    let peakTorqueNm = 0, maxContactSpeedMmS = 0, minNormalForceN = Infinity, lastTau = 0;
    const liftOff = new Set();
    const trace = [];
    let previousActive = at(start).contactActive;

    const command = (now) => {
      if (kind === "step") return target;
      const x = clamp(now / duration, 0, 1);
      const eased = x ** 3 * (10 + x * (-15 + 6 * x));
      return start + (target - start) * eased;
    };
    const record = (now, cmd, state, torque) => trace.push({
      t: now,
      commandDeg: cmd,
      servoDeg: q / RAD,
      torqueNm: torque,
      liftsMm: [...state.liftsMm],
    });

    record(0, command(0), at(start), 0);
    while (t < endTime - C.dtS * 0.5) {
      const state = at(q / RAD);
      const cmd = command(t);
      const inertia = C.motorInertiaKgm2 + state.inertiaRestKgm2 + massScale * state.inertiaGroupsKgm2;
      const gravity = state.gravityRestNm + massScale * state.gravityGroupsNm;
      const dMass = massScale * state.dMGroupsDqKgm2PerRad;
      const stall = C.stallTorqueNm * stallScale;
      const effort = clamp((cmd * RAD - q) / C.controlBandRad, -1, 1);
      const tau = clamp(stall * effort - stall / C.noLoadSpeedRadS * velocity, -stall, stall);
      let net = tau - gravity - 0.5 * dMass * velocity * velocity;
      if (Math.abs(velocity) > 1e-4) net -= Math.sign(velocity) * C.servoFrictionNm;
      else if (Math.abs(net) <= C.servoFrictionNm) { net = 0; velocity = 0; }
      else net -= Math.sign(net) * C.servoFrictionNm;
      const acceleration = net / inertia;
      state.contactActive.forEach((active, index) => {
        if (active) {
          const carrierMass = tables.groups[index].massKg * massScale;
          const verticalAcceleration = state.dLiftDqMPerRad[index] * acceleration
            + state.d2LiftDq2MPerRad2[index] * velocity * velocity;
          const normal = carrierMass * (C.gravityMS2 + verticalAcceleration);
          minNormalForceN = Math.min(minNormalForceN, normal);
          if (normal < -C.contactToleranceN) liftOff.add(index);
        }
        if (active && !previousActive[index]) {
          maxContactSpeedMmS = Math.max(maxContactSpeedMmS,
            Math.abs(state.dLiftDqMPerRad[index] * velocity) * 1000);
        }
      });
      previousActive = state.contactActive;
      const previousQ = q, previousVelocity = velocity;
      velocity += acceleration * C.dtS;
      q += velocity * C.dtS;
      if (q < low * RAD) { q = low * RAD; velocity = Math.max(0, velocity); }
      else if (q > high * RAD) { q = high * RAD; velocity = Math.min(0, velocity); }
      maxContactSpeedMmS = Math.max(maxContactSpeedMmS,
        boundaryCrossingSpeedMmS(previousQ / RAD, q / RAD, previousVelocity, velocity,
          tables.contactBoundariesDeg ?? []));
      t += C.dtS;
      lastTau = tau;
      peakTorqueNm = Math.max(peakTorqueNm, Math.abs(tau));
      if (t + 1e-12 >= nextRecord) {
        record(t, command(t), at(q / RAD), tau);
        nextRecord += C.recordS;
      }
    }
    const finalState = at(q / RAD);
    if (Math.abs(trace.at(-1).t - t) > C.dtS) record(t, command(t), finalState, lastTau);
    const final = {
      t,
      commandDeg: command(t),
      servoDeg: q / RAD,
      torqueNm: lastTau,
      liftsMm: [...finalState.liftsMm],
    };
    return {
      trace,
      final,
      peakTorqueNm,
      maxContactSpeedMmS,
      contactFeasible: liftOff.size === 0,
      minNormalForceN: Number.isFinite(minNormalForceN) ? minNormalForceN : null,
      possibleLiftOffGroups: [...liftOff].sort((a, b) => a - b).map((index) => tables.groups[index].label),
      clippedToLimits,
    };
  }

  return { at, run, holdTorque, model: tables.model, limitsDeg: [...tables.limitsDeg], groups: tables.groups, const: C };
}

export function profile(kind, from, to, duration) {
  const safeDuration = Math.max(Number(duration) || 0, Number.EPSILON);
  return (time) => {
    if (kind === "step") return to;
    const x = clamp(time / safeDuration, 0, 1);
    return from + (to - from) * x ** 3 * (10 + x * (-15 + 6 * x));
  };
}

export function boundaryCrossingSpeedMmS(q0Deg, q1Deg, w0, w1, groups) {
  if (q0Deg === q1Deg) return 0;
  const low = Math.min(q0Deg, q1Deg), high = Math.max(q0Deg, q1Deg);
  let maximum = 0;
  for (const boundaries of groups) {
    for (const boundary of boundaries) {
      if (boundary.deg >= low && boundary.deg <= high) {
        const fraction = (boundary.deg - q0Deg) / (q1Deg - q0Deg);
        const crossingVelocity = w0 + (w1 - w0) * fraction;
        maximum = Math.max(maximum, Math.abs(boundary.slopeMPerRad * crossingVelocity) * 1000);
      }
    }
  }
  return maximum;
}
