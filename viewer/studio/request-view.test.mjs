import assert from "node:assert/strict";
import { requestDetailUrl, requestImages, requestShapeDetails, requestTitle } from "./request-view.js";

const request = {
  message: "", items: [
    { type: "pin", note: "" },
    { type: "section", note: "断面の自由メモ" },
    { type: "section", note: "二枚目" },
  ],
  images: ["/r/view.png", "/r/section-1.png", "/r/section-1.svg", "/r/section-2.png"],
};
assert.equal(requestTitle(request), "断面の自由メモ");
assert.equal(requestTitle({ message: " 一行目\n二行目", items: request.items }), "一行目");
const mapped = requestImages(request);
assert.equal(mapped.view, "/r/view.png");
assert.equal(mapped.items[1].image, "/r/section-1.png");
assert.equal(mapped.items[1].svg, "/r/section-1.svg");
assert.equal(mapped.items[2].image, "/r/section-2.png");
assert.equal(requestDetailUrl({ model: "箱 1", id: "a/b" }), "/requests/%E7%AE%B1%201/a%2Fb/request.json");
assert.deepEqual(requestShapeDetails({ items: [{ type: "section", shapes: [
  { kind: "text", text: "ここ", note: "補足" },
  { kind: "line", text: "", note: "" },
] }] }), [{ kind: "text", name: "", text: "ここ", note: "補足" }]);
const missing = requestImages({ items: [{ type: "section" }, { type: "section" }], images: ["/r/section-2.png"] });
assert.equal(missing.items[0].image, null);
assert.equal(missing.items[1].image, "/r/section-2.png");
console.log("request view: 9 assertions passed");
