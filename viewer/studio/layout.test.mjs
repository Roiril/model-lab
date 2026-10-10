import assert from "node:assert/strict";
import {
  createLatestGate, plateDraftKey, plateLayoutSnapshot, plateManifestStale, validPlateManifest,
} from "./layout.js";

const part = {
  file: "box-studio-plate-abc-lid-4.stl", sourcePart: "lid", sourceFile: "box_lid.stl", objectId: "4",
  buildTransform: [1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 0], sha256: "part-sha", size: 12,
  bbox: { min: [0, 0, 0], max: [1, 1, 1] }, source: { file: "box_lid.stl", sha256: "source-sha", size: 10, mtime: 1000.4 },
};
const manifest = { version: 1, model: "box", kind: "plate", id: "full-sha", source3mf: "box.gcode.3mf", source3mfSha256: "full-sha", bed: { width: 256, depth: 256 }, parts: [part] };

assert.equal(validPlateManifest(manifest, "box"), true);
assert.equal(plateManifestStale(manifest, [{ name: "box_lid.stl", size: 10, mtime: 1001.3 }]), false);
assert.equal(plateManifestStale(manifest, [{ name: "box_lid.stl", size: 11, mtime: 1000.4 }]), true);
assert.equal(plateDraftKey("box", { kind: "assembled" }), "studio.draft.box");
assert.equal(plateDraftKey("box", manifest), "studio.draft.box.plate.full-sha");
assert.deepEqual(plateLayoutSnapshot(manifest), { kind: "plate", id: "full-sha", source3mf: "box.gcode.3mf", source3mfSha256: "full-sha", manifestVersion: 1 });
const gate = createLatestGate();
const old = gate.next(), latest = gate.next();
assert.equal(gate.isCurrent(old), false);
assert.equal(gate.isCurrent(latest), true);
console.log("layout: 8 assertions passed");
