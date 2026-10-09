// ブラウザの計算（sim.mjs）が Python の計算（simulate.py）と同じ結果を出すか。
//   node viewer/lid-cube/sim.test.mjs
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createSim, profile } from "./sim.mjs";

const data = JSON.parse(readFileSync(new URL("./assets/data.json", import.meta.url), "utf8"));
const sim = createSim(data.simTables);
const py = data.sim;
const ac = sim.alphaClosed, ao = sim.alphaOpen;

// 1. ゆっくり開いて閉じる（simulate.py の "eased" と同じ指令）
const ease = (t) => (t < 1.5 ? profile("ease", ac, ao, 0)(t) : profile("ease", ao, ac, 1.5)(t));
const e = sim.run({ cmd: ease, tEnd: 3.0, alphaStart: ac });
const at15 = e.trace.find((r) => r[0] >= 1.499)[1];
assert.ok(Math.abs(at15 - py.eased.theta_at_1_5s) < 0.5, `eased θ@1.5s ${at15} vs ${py.eased.theta_at_1_5s}`);
assert.ok(Math.abs(e.final.theta - py.eased.final_theta) < 0.3, `eased final ${e.final.theta}`);
assert.ok(Math.abs(e.impact - py.eased.lid_impact_rad_s) < 0.15, `eased impact ${e.impact} vs ${py.eased.lid_impact_rad_s}`);

// 2. 全速（0 秒で開、1 秒で閉）
const step = (t) => (t < 1.0 ? ao : ac);
const f = sim.run({ cmd: step, tEnd: 2.0, alphaStart: ac });
const t90 = f.trace.find((r) => r[1] > 0.9 * 95)[0];
assert.ok(Math.abs(t90 - py.full_speed.t_open_90pct) < 0.015, `t90 ${t90} vs ${py.full_speed.t_open_90pct}`);
assert.ok(Math.abs(f.impact - py.full_speed.lid_impact_rad_s) / py.full_speed.lid_impact_rad_s < 0.1, `impact ${f.impact}`);

// 3. 校正: トルクを静的必要量の半分にすると開かない。30% なら開く
const need = py.static.max_torque_Nm;
const half = sim.run({ cmd: () => ao, tEnd: 1.5, alphaStart: ac, stallScale: (need * 0.5) / sim.const.stall });
assert.ok(half.final.theta < 5, `half torque opened to ${half.final.theta}`);
const weak = sim.run({ cmd: () => ao, tEnd: 1.5, alphaStart: ac, stallScale: 0.3 });
assert.ok(weak.final.theta > 94, `30% torque reached ${weak.final.theta}`);

console.log("lid-cube sim matches simulate.py:",
  { eased_theta_1_5s: +at15.toFixed(2), eased_impact: +e.impact.toFixed(3), full_t90: +t90.toFixed(3), full_impact: +f.impact.toFixed(2) });
