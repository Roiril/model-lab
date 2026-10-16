import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  buildTree, commonMode, displayLabel, duplicateLabels, isPartDerivedFile, isRenamed, itemPartText, ledgerUrl, matchPart,
  normalizeLedger, normalizePartNames, partName, partNamesForRequest, partNamesKey, partRefForFile, systemLabelOf,
  withModes, withPartName, withPartRefs,
} from "./parts.js";

const raw = {
  version: 1, model: "box",
  groups: [{ id: "shell", label: "外装", color: "#d8d4cc" }, { id: "cam", label: "板カム", color: "#56b4e9" }, { id: "empty", label: "空", color: "#000000" }],
  parts: [
    { id: "housing", label: "外装（底と四方の壁）", systemLabel: "外装（底と四方の壁）", group: "shell", kind: "printed", file: "box-part-housing.stl", aliases: ["箱"], color: "#d8d4cc" },
    { id: "cam_0", label: "カム 0", systemLabel: "カム 0", group: "cam", kind: "printed", file: "box-part-cam_0.stl", aliases: [] },
    { id: "cam_1", label: "ピクセル", systemLabel: "カム 1", group: "cam", kind: "printed", file: "box-part-cam_1.stl", aliases: ["いち"] },
    { id: "servo", label: "サーボ", systemLabel: "サーボ", group: "ghost-group", kind: "stock", file: "box-part-servo.stl" },
    { id: "front/panel", label: "空の面板", systemLabel: "空の面板", group: "shell", kind: "jig", file: "box-part-front__panel.stl" },
    { id: "back/panel", label: "空の面板", systemLabel: "空の面板", group: "cam", kind: "printed", file: "box-part-back__panel.stl" },
  ],
};
const ledger = normalizeLedger(raw, "box");

// 台帳の読み込み: 形が違えば null
assert.equal(normalizeLedger(raw, "other"), null);
assert.equal(normalizeLedger({ ...raw, version: 2 }, "box"), null);
assert.equal(normalizeLedger({ ...raw, parts: [] }, "box"), null);
assert.equal(normalizeLedger(null, "box"), null);
assert.equal(ledger.parts.length, 6);
// 台帳に無い群を指す部品は「その他」へ
assert.equal(ledger.byId.get("servo").group, "__other");
assert.equal(ledger.groups.at(-1).id, "__other");
assert.equal(ledger.byFile.get("box-part-front__panel.stl").id, "front/panel");
assert.equal(ledger.byId.get("housing").kind, "printed");
assert.equal(ledger.byId.get("front/panel").kind, "jig");
assert.equal(ledgerUrl("tangible-pixel-cube"), "/viewer/studio/parts/tangible-pixel-cube.json");
assert.equal(partNamesKey("box"), "studio.partNames.box");
assert.equal(isPartDerivedFile("box-part-cam_0.stl"), true);
assert.equal(isPartDerivedFile("box.stl"), false);

// 呼び名: 台帳の label が表示名。上書きは台帳の名前と同じなら消える
const cam1 = ledger.byId.get("cam_1");
assert.equal(systemLabelOf(cam1), "カム 1");
assert.equal(isRenamed(cam1, {}), true);          // 台帳側が既にユーザーの呼び名
assert.equal(isRenamed(ledger.byId.get("cam_0"), {}), false);
assert.equal(displayLabel(ledger.byId.get("cam_0"), { cam_0: { label: "最初のカム" } }), "最初のカム");
let names = withPartName({}, ledger.byId.get("cam_0"), "  最初のカム ");
assert.deepEqual(names, { cam_0: { label: "最初のカム" } });
assert.deepEqual(withPartName(names, ledger.byId.get("cam_0"), "カム 0"), {});
assert.deepEqual(withPartName(names, ledger.byId.get("cam_0"), ""), {});
assert.deepEqual(normalizePartNames({ a: { label: "x" }, b: { label: "" }, c: 3, d: null }), { a: { label: "x" } });
assert.deepEqual(normalizePartNames([1]), {});

// 依頼の partNames: 台帳の名前と違うものだけ。systemLabel は台帳の systemLabel
assert.deepEqual(partNamesForRequest({ cam_0: { label: "最初のカム" }, cam_1: { label: "ピクセル" }, gone: { label: "x" } }, ledger),
  { cam_0: { label: "最初のカム", systemLabel: "カム 0" } });
assert.deepEqual(partNamesForRequest({ cam_0: { label: "最初のカム" } }, null), {});

// 同じ名前の部品は群名を添える
const dup = duplicateLabels(ledger, {});
assert.equal(dup.has("空の面板"), true);
assert.equal(partName(ledger, {}, ledger.byId.get("front/panel"), dup), "空の面板（外装）");
assert.equal(partName(ledger, {}, ledger.byId.get("back/panel"), dup), "空の面板（板カム）");
assert.equal(partName(ledger, {}, ledger.byId.get("housing"), dup), "外装（底と四方の壁）");

// 指示への部品名
assert.deepEqual(partRefForFile(ledger, {}, "box-part-cam_0.stl"), { partId: "cam_0", partLabel: "カム 0" });
assert.deepEqual(partRefForFile(ledger, {}, "box-part-cam_1.stl"), { partId: "cam_1", partLabel: "ピクセル", partSystemLabel: "カム 1" });
assert.equal(partRefForFile(ledger, {}, "other.stl"), null);
assert.equal(partRefForFile(null, {}, "box-part-cam_0.stl"), null);
const faces = withPartRefs({ type: "faces", file: "box-part-cam_0.stl", note: "n" }, ledger, { cam_0: { label: "最初のカム" } });
assert.equal(faces.partId, "cam_0");
assert.equal(faces.partLabel, "最初のカム");
assert.equal(faces.partSystemLabel, "カム 0");
const meas = withPartRefs({ type: "measure", file: "box-part-cam_0.stl", fileB: "box-part-housing.stl" }, ledger, {});
assert.equal(meas.partIdB, "housing");
assert.equal(meas.partLabelB, "外装（底と四方の壁）");
assert.equal("partIdB" in withPartRefs({ type: "measure", file: "box-part-cam_0.stl", fileB: "box-part-cam_0.stl" }, ledger, {}), false);
assert.deepEqual(withPartRefs({ type: "pin", file: "x.stl" }, ledger, {}), { type: "pin", file: "x.stl" });
assert.equal(itemPartText({ type: "faces", file: "box-part-housing.stl" }, ledger, {}), "外装（底と四方の壁）");
assert.equal(itemPartText({ type: "faces", file: "box-part-front__panel.stl" }, ledger, {}), "空の面板（外装）");
assert.equal(itemPartText({ type: "measure", file: "box-part-cam_0.stl", fileB: "box-part-housing.stl" }, ledger, {}), "カム 0 ↔ 外装（底と四方の壁）");
assert.equal(itemPartText({ type: "faces", file: "nope.stl" }, ledger, {}), null);

// 絞り込み: 名前・シュビーの名前・別名・id・群名。空白で分けた語は全部入っていること
const housing = ledger.byId.get("housing");
assert.equal(matchPart(housing, {}, "外装", "外装"), true);
assert.equal(matchPart(housing, {}, "外装", "箱"), true);            // 別名
assert.equal(matchPart(cam1, {}, "板カム", "カム 1"), true);          // シュビーの名前
assert.equal(matchPart(cam1, {}, "板カム", "ピクセル"), true);
assert.equal(matchPart(cam1, {}, "板カム", "cam_1"), true);           // id
assert.equal(matchPart(cam1, {}, "板カム", "板カム ピクセル"), true);  // 群名と名前
assert.equal(matchPart(cam1, {}, "板カム", "外装"), false);
assert.equal(matchPart(cam1, { cam_1: { label: "ひとつ目" } }, "板カム", "ひとつ"), true);
assert.equal(matchPart(housing, {}, "外装", ""), true);
assert.equal(matchPart(housing, {}, "外装", "ＣＡＭ"), false);
assert.equal(matchPart(cam1, {}, "板カム", "ＣＡＭ_1"), true);        // 全角英数も同じ

// 群ごとの木: 部品が無い群は出ない。台帳の群の順
assert.deepEqual(buildTree(ledger, {}).map((n) => [n.group.id, n.parts.length]), [["shell", 2], ["cam", 3], ["__other", 1]]);
assert.deepEqual(buildTree(ledger, {}, "いち").map((n) => [n.group.id, n.parts.map((p) => p.id)]), [["cam", ["cam_1"]]]);
assert.deepEqual(buildTree(ledger, {}, "ありえない"), []);
assert.deepEqual(buildTree(null, {}), []);

// 見え方: 群のまとめ
assert.equal(commonMode(["a", "b"], {}), "normal");
assert.equal(commonMode(["a", "b"], { a: "ghost", b: "ghost" }), "ghost");
assert.equal(commonMode(["a", "b"], { a: "ghost" }), "mixed");
assert.equal(commonMode([], {}), "normal");
assert.deepEqual(withModes({ x: "hidden" }, ["a", "b"], "ghost"), { x: "hidden", a: "ghost", b: "ghost" });
assert.deepEqual(withModes({ a: "ghost", b: "hidden" }, ["a", "b"], "normal"), {});
const before = { a: "ghost" };
withModes(before, ["b"], "hidden");
assert.deepEqual(before, { a: "ghost" });

// 本物の台帳（部品台帳の担当が書き出したもの）が読める。全部品が群に属し、同じ名前は群名で見分けられる
for (const model of ["tangible-pixel-cube", "mystery-box-sg92r-f1", "flag-box"]) {
  const real = normalizeLedger(JSON.parse(readFileSync(new URL(`./parts/${model}.json`, import.meta.url), "utf8")), model);
  assert.ok(real, `${model} の台帳が読める`);
  const ids = new Set(real.groups.map((g) => g.id));
  assert.ok(real.parts.every((p) => ids.has(p.group)), `${model}: 全部品が群に属す`);
  assert.equal(buildTree(real, {}).reduce((n, g) => n + g.parts.length, 0), real.parts.length);
  const d = duplicateLabels(real, {});
  const shown = real.parts.map((p) => partName(real, {}, p, d));
  assert.equal(new Set(shown).size, shown.length, `${model}: 画面に出す名前が重ならない`);
}

console.log("parts: 78 assertions passed");
