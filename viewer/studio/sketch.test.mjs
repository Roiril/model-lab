import assert from "node:assert/strict";
import { createDrawingShape } from "./sketch.js";

const shape = createDrawingShape("line", [{ p: [0, 0] }, { p: [1, 1] }], { intent: "remove", note: "自由メモ" });
assert.equal(shape.kind, "line");
assert.equal(shape.intent, "note");
assert.equal(shape.note, "自由メモ");
assert.equal(shape.nodes.length, 2);
console.log("sketch: 4 assertions passed");
