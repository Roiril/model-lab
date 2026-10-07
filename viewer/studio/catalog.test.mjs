import assert from "node:assert/strict";
import {
  filterModels,
  groupModels,
  normalizeSearchText,
  parseFavorites,
  selectModels,
} from "./catalog.js";

let count = 0;
function test(name, run) {
  run();
  count += 1;
  console.log(`OK ${name}`);
}

const models = [
  {
    name: "pipe-corner-inner",
    title: "パイプ用の内角継手",
    description: "棚の角を内側からつなぐ部品",
    category: "家具・収納",
    categoryId: "furniture",
    project: "手すり試作",
    projectId: "pipe-rail",
    tags: ["継手", "28mm"],
    status: "active",
    organized: true,
    available: true,
  },
  {
    name: "pipe-foot-reference",
    title: "パイプ脚の参考形状",
    description: "床との接点を確認する資料",
    category: "家具・収納",
    categoryId: "furniture",
    project: "手すり試作",
    projectId: "pipe-rail",
    tags: ["脚"],
    status: "reference",
    organized: true,
    available: true,
  },
  {
    name: "legacy-holder",
    title: "旧ホルダー",
    description: "保管中の試作",
    category: "治具",
    categoryId: "jig",
    project: "旧作",
    projectId: "legacy",
    tags: [],
    status: "archived",
    organized: true,
    available: true,
  },
  {
    name: "future-format",
    title: "変換待ちのモデル",
    description: "別の形式で保存されている",
    organized: false,
    available: false,
    unavailableReason: "STL への変換が必要です",
  },
];

test("NFKC で全角英数と区切りを揃える", () => {
  assert.equal(normalizeSearchText("ＰＩＰＥ_corner"), "pipe corner");
});

test("日本語の題名と説明を検索できる", () => {
  assert.deepEqual(filterModels(models, { query: "パイプ" }).map((model) => model.name), [
    "pipe-corner-inner", "pipe-foot-reference",
  ]);
});

test("空白で区切った語は AND 検索になる", () => {
  assert.deepEqual(filterModels(models, { query: "pipe 継手" }).map((model) => model.name), ["pipe-corner-inner"]);
  assert.deepEqual(filterModels(models, { query: "手すり 参考" }).map((model) => model.name), ["pipe-foot-reference"]);
});

test("最近開いたグループは重複せず、プロジェクト側にも再掲しない", () => {
  const groups = groupModels(models.slice(0, 3), { recent: ["pipe-foot-reference", "pipe-foot-reference", "pipe-corner-inner"] });
  assert.deepEqual(groups[0].models.map((model) => model.name), ["pipe-foot-reference", "pipe-corner-inner"]);
  assert.deepEqual(groups.flatMap((group) => group.models).map((model) => model.name), [
    "pipe-foot-reference", "pipe-corner-inner", "legacy-holder",
  ]);
});

test("関連プロジェクトが無いモデルは用途ごとに分かれる", () => {
  const groups = groupModels([
    { name: "a", title: "A", category: "治具", categoryId: "jig", project: "関連プロジェクトなし", projectId: null, organized: true },
    { name: "b", title: "B", category: "家具・収納", categoryId: "furniture", project: "関連プロジェクトなし", projectId: null, organized: true },
  ]);
  assert.deepEqual(groups.map((group) => group.title), ["治具", "家具・収納"]);
  assert.deepEqual(groups.map((group) => group.models.length), [1, 1]);
  const selected = selectModels([
    { name: "a", title: "A", category: "治具", categoryId: "jig", project: "関連プロジェクトなし", projectId: null },
    { name: "b", title: "B", category: "家具・収納", categoryId: "furniture", project: "関連プロジェクトなし", projectId: null },
  ], { view: "all" });
  assert.deepEqual(selected.groups.map((group) => group.title), ["家具・収納", "治具"]);
});

test("未整理と開けないモデルも一覧から消えない", () => {
  const result = filterModels(models);
  const unavailable = result.find((model) => model.name === "future-format");
  assert.ok(unavailable);
  assert.equal(unavailable.categoryId, "unorganized");
  assert.equal(unavailable.category, "未整理");
  assert.equal(unavailable.available, false);
});

test("保管中は初期表示から隠れ、検索と全件と保管から届く", () => {
  assert.equal(filterModels(models).some((model) => model.name === "legacy-holder"), false);
  assert.equal(filterModels(models, { query: "旧ホルダー" }).some((model) => model.name === "legacy-holder"), true);
  assert.equal(filterModels(models, { view: "all" }).some((model) => model.name === "legacy-holder"), true);
  assert.deepEqual(filterModels(models, { view: "archived" }).map((model) => model.name), ["legacy-holder"]);
  assert.equal(selectModels(models).categories.some((category) => category.id === "jig"), false);
});

test("分類 ID は表示名ではなく ID で絞る", () => {
  assert.deepEqual(filterModels(models, { categoryId: "furniture" }).map((model) => model.name), [
    "pipe-corner-inner", "pipe-foot-reference",
  ]);
  assert.deepEqual(filterModels(models, { categoryId: "家具・収納" }), []);
});

test("1回に30件ずつ表示する", () => {
  const many = Array.from({ length: 65 }, (_, index) => ({ name: `model-${index}`, projectId: "p", project: "試作" }));
  const first = selectModels(many, { page: 1 });
  const second = selectModels(many, { page: 2 });
  const third = selectModels(many, { page: 3 });
  assert.equal(first.items.length, 30);
  assert.equal(first.remaining, 35);
  assert.equal(second.items.length, 60);
  assert.equal(second.remaining, 5);
  assert.equal(third.items.length, 65);
  assert.equal(third.hasMore, false);
});

test("用途、関連プロジェクト、表示名の順に並べてからページを切る", () => {
  const unordered = [
    { name: "z", title: "う", category: "治具", categoryId: "jig", project: "乙", projectId: "b" },
    { name: "a", title: "い", category: "家具", categoryId: "furniture", project: "甲", projectId: "a" },
    { name: "b", title: "あ", category: "家具", categoryId: "furniture", project: "甲", projectId: "a" },
  ];
  assert.deepEqual(selectModels(unordered, { view: "all", pageSize: 2 }).items.map((model) => model.name), ["b", "a"]);
});

test("お気に入りの壊れた値と不正な要素を捨てる", () => {
  assert.deepEqual(parseFavorites("not-json"), []);
  assert.deepEqual(parseFavorites('["a", 2, "", "a", "b"]'), ["a", "b"]);
  assert.deepEqual(parseFavorites('["a", "c"]', ["a", "b"]), ["a"]);
});

console.log(`${count} tests passed`);
