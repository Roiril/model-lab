const assert = require("node:assert/strict");
const { sourceUnit, decorateControls } = require("../lib/parameter_units");
assert.equal(sourceUnit("# 寸法 (m)"), "m");
assert.equal(sourceUnit("# 単位 mm。 model.pyでmへ変換"), "mm");
assert.equal(sourceUnit("# units: meters"), "m");
assert.equal(sourceUnit("# 未宣言"), null);
const input = [
  { name: "BODY_R", value: .028, label: "胴の半径", isInt: false },
  { name: "COUPLING_GAP", value: 0, label: "ホーン結合面の微調整", isInt: true },
  { name: "SERVO_SCREWS", value: 0, label: "サーボ固定ねじ穴 1=開ける", isInt: true },
  { name: "ANGLE", value: 45, label: "傾斜角度", isInt: true },
  { name: "SCALE", value: .8, label: "倍率", isInt: false },
];
const controls = decorateControls(input, "# 単位: m");
assert.equal(controls[0].value * controls[0].displayScale, 28);
assert.equal(controls[0].value, .028);
assert.equal(controls[1].isInt, false);
assert.equal(controls[2].unit, "");
assert.equal(controls[2].isInt, true);
assert.equal(controls[3].unit, "°");
assert.equal(controls[4].unit, "");
assert.equal(decorateControls(input, "未宣言")[0].displayScale, 1);
assert.equal(decorateControls(input, "# 単位: mm")[0].displayScale, 1);
console.log("parameter units: 13 assertions passed");
