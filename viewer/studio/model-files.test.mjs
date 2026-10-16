import assert from "node:assert/strict";
import { filesForModel, selectModelFile } from "./model-files.js";
const models = ["pipe-foot", "pipe-foot-corner", "round-bot"];
const files = ["pipe_foot_corner_a.stl", "round-bot.stl", "pipe_foot.stl", "pipe_foot_asm.stl"];
assert.deepEqual(filesForModel("pipe-foot", files, models), ["pipe_foot.stl", "pipe_foot_asm.stl"]);
assert.equal(selectModelFile("pipe-foot", files, models), "pipe_foot_asm.stl");
assert.equal(selectModelFile("missing", files, models), null);
assert.equal(selectModelFile("round-bot", files, models), "round-bot.stl");
assert.equal(selectModelFile("pipe-foot", ["pipe_foot_corner_a.stl"], models), null);
assert.deepEqual(filesForModel("pipe-foot", ["pipe_foot-studio-plate-abc-lid-1.stl"], models), []);
assert.equal(selectModelFile("pipe-foot", ["pipe_foot-studio-plate-abc-lid-1.stl"], models), null);
// 部品台帳の STL（-part-）は組立の候補に入れない（台帳の部品として別に読む）
assert.deepEqual(filesForModel("pipe-foot", ["pipe_foot_asm.stl", "pipe-foot-part-lid.stl", "pipe_foot_part_lid.stl"], models), ["pipe_foot_asm.stl", "pipe_foot_part_lid.stl"]);
assert.equal(selectModelFile("pipe-foot", ["pipe-foot-part-lid.stl"], models), null);
console.log("model files: 9 assertions passed");
