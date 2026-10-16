import assert from "node:assert/strict";
import {
  countPartModes, modeOf, normalizePartModes, partKey, partModesForRequest, partModesKey, pickTargets, sliceTargets, toggledGhost, withPartMode,
} from "./part-modes.js";

const mesh = (file, partMode) => ({ userData: { file, ...(partMode ? { partMode } : {}) } });
const housing = mesh("housing.stl", "ghost");
const cam = mesh("cam.stl");
const lid = mesh("lid.stl", "hidden");
const meshes = [housing, cam, lid];

// レイキャストの対象: 透過した部品は素通り、隠した部品は常に除く
assert.deepEqual(pickTargets(meshes).map((m) => m.userData.file), ["cam.stl"]);
assert.deepEqual(pickTargets(meshes, { includeGhost: true }).map((m) => m.userData.file), ["housing.stl", "cam.stl"]);
assert.deepEqual(pickTargets([mesh("a.stl"), mesh("b.stl")]).length, 2);
// 断面: 隠した部品だけ除く（透過した部品は切る）
assert.deepEqual(sliceTargets(meshes).map((m) => m.userData.file), ["housing.stl", "cam.stl"]);

// 状態の読み書き
assert.equal(modeOf({ "a.stl": "ghost" }, "a.stl"), "ghost");
assert.equal(modeOf({ "a.stl": "ghost" }, "b.stl"), "normal");
assert.equal(modeOf(undefined, "b.stl"), "normal");
assert.equal(modeOf({ "a.stl": "bogus" }, "a.stl"), "normal");
assert.deepEqual(normalizePartModes({ a: "ghost", b: "hidden", c: "normal", d: 3 }), { a: "ghost", b: "hidden" });
assert.deepEqual(normalizePartModes(null), {});
assert.deepEqual(normalizePartModes([1, 2]), {});
assert.deepEqual(withPartMode({ a: "ghost" }, "b", "hidden"), { a: "ghost", b: "hidden" });
assert.deepEqual(withPartMode({ a: "ghost" }, "a", "normal"), {});
const before = { a: "ghost" };
withPartMode(before, "b", "hidden");
assert.deepEqual(before, { a: "ghost" });
assert.equal(toggledGhost("normal"), "ghost");
assert.equal(toggledGhost("ghost"), "normal");
assert.equal(toggledGhost("hidden"), "ghost");
assert.equal(partModesKey("tangible-pixel-cube"), "studio.partModes.tangible-pixel-cube");

// 依頼 JSON: 読み込み中の STL のうち通常でないものだけ
const modes = { "housing.stl": "ghost", "lid.stl": "hidden", "gone.stl": "ghost" };
assert.deepEqual(partModesForRequest(modes, ["housing.stl", "cam.stl", "lid.stl"]), { "housing.stl": "ghost", "lid.stl": "hidden" });
assert.deepEqual(partModesForRequest({}, ["a.stl"]), {});
assert.deepEqual(partModesForRequest(undefined, undefined), {});
assert.deepEqual(countPartModes(modes, ["housing.stl", "cam.stl", "lid.stl"]), { ghost: 1, hidden: 1 });

// 見え方のキー: 台帳の部品は部品 id、台帳が無い STL は STL 名
assert.equal(partKey({ file: "a.stl", partId: "housing" }), "housing");
assert.equal(partKey({ file: "a.stl" }), "a.stl");
assert.equal(partKey(undefined), "");
assert.deepEqual(partModesForRequest({ housing: "ghost", cam: "hidden" }, ["housing", "cam", "lid"]), { housing: "ghost", cam: "hidden" });

console.log("part-modes: 26 assertions passed");
