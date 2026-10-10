import assert from "node:assert/strict";
import { createKinematics, isMissing, reportState, reportSummary, validateData } from "./d-cube.mjs";

assert.equal(isMissing(undefined), true);
assert.equal(isMissing(null), true);
assert.equal(isMissing(""), true);
assert.equal(isMissing([]), true);
assert.equal(isMissing({}), true);
assert.equal(isMissing(0), false);
assert.equal(isMissing(false), false);
assert.equal(isMissing("0"), false);

const report = reportState({ geometry: { non_manifold: 0 }, motion: null, physics: false });
assert.equal(report.find((entry) => entry.key === "geometry").verified, true);
assert.equal(report.find((entry) => entry.key === "motion").verified, false);
assert.equal(report.find((entry) => entry.key === "assembly").verified, false);
assert.equal(report.find((entry) => entry.key === "physics").verified, true);
const summary = reportSummary({
  geometry: { exterior: { ok: true, size_mm: [80, 80, 80], checked: 3, passed: 3, failures: [] }, topology: { box: { ok: true } }, calibration: { ok: true } },
  motion: { ok: true, samples: 27, step_deg: 2.5, intersection_tests: 54, min_clearance_mm: { "lid-roof": 0 }, failures: [] },
  physics: { mass: { lid_g: 12.3 }, static: { max_torque_Nm: 0.003, ratio_to_stall: 0.012 }, eased: { peak_torque_Nm: 0.008, lid_impact_rad_s: 0 }, weak_30pct: { opened: false } },
});
assert.equal(summary.find((entry) => entry.key === "geometry").rows[0].value, "80 × 80 × 80 mm");
assert.equal(summary.find((entry) => entry.key === "motion").rows.find((item) => item.label === "蓋と固定天面の隙間").value, "0 mm");
assert.equal(summary.find((entry) => entry.key === "physics").rows.some((item) => item.value.includes("trace")), false);
const missingPhysics = reportSummary({ physics: { static: { max_torque_Nm: null } } }).find((entry) => entry.key === "physics");
assert.equal(missingPhysics.rows.find((item) => item.label === "重力を支える最大トルク").value, "未検証");

const mesh = { pos: "", ind: "", nv: 0, nt: 0 };
const meshes = Object.fromEntries(["box", "lid", "roof", "crank", "link", "pin", "clip", "speaker_clip", "ref_body", "ref_horn", "ref_wire", "ref_speaker"].map((name) => [name, mesh]));
const data = { q: 0.005, meshes, kin: { H: [-30, 65], O: [3, 30.6], a: 1, l: 1, alpha0: 0, A0: [0, 0], B0: [0, 0], table: [[0, 0], [65, 1]], key_rel: 0, mid_theta: 30, open_theta: 65, bend_deg: 0 } };
assert.equal(validateData(data), data);
assert.throws(() => validateData({ ...data, q: 0 }), /q/);
assert.throws(() => validateData({ ...data, meshes: { ...meshes, lid: undefined } }), /lid/);
assert.throws(() => validateData({ ...data, kin: { ...data.kin, table: [[0, 0]] } }), /kin/);
const kinematics = createKinematics(data.kin);
assert.equal(kinematics.alphaOf(32.5), 0.5);
assert.deepEqual(Object.keys(kinematics.pose(30)).sort(), ["crank", "lid", "link", "ref_horn"]);
console.log("d-cube: data contract and missing report values passed");
