const assert = require("assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const test = require("node:test");
const { checkCatalog, listModelCatalog } = require("../lib/model_catalog");
const { runCheck } = require("./catalog");

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(value), "utf8");
}

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "model-catalog-"));
  t.after(() => {
    assert.equal(path.dirname(path.resolve(root)), path.resolve(os.tmpdir()));
    assert.ok(path.basename(root).startsWith("model-catalog-"));
    fs.rmSync(root, { recursive: true, force: true });
  });
  const modelsDir = path.join(root, "models");
  const previewDir = path.join(root, "viewer", "preview");
  fs.mkdirSync(path.join(modelsDir, "alpha"), { recursive: true });
  fs.mkdirSync(path.join(modelsDir, "new-model"), { recursive: true });
  fs.mkdirSync(previewDir, { recursive: true });
  fs.writeFileSync(path.join(modelsDir, "alpha", "params.py"), "# CATEGORY: 旧分類\n", "utf8");
  fs.writeFileSync(path.join(modelsDir, "alpha", "model.py"), "", "utf8");
  fs.writeFileSync(path.join(previewDir, "new-model.js"), "", "utf8");
  writeJson(path.join(modelsDir, "catalog-groups.json"), {
    schemaVersion: 1,
    categories: [{ id: "robots", title: "ロボット" }],
    projects: [{ id: "robot-family", title: "ロボット系列", categoryId: "robots" }],
  });
  writeJson(path.join(modelsDir, "alpha", "catalog.json"), {
    schemaVersion: 1,
    title: "アルファ",
    description: "検証用モデルです。",
    categoryId: "robots",
    projectId: "robot-family",
    tags: ["検証"],
    status: "active",
  });
  return { root, modelsDir, previewDir };
}

test("有効な metadata を分類名とプロジェクト名へ解決する", (t) => {
  const f = fixture(t);
  const items = listModelCatalog(f);
  assert.equal(items.length, 2);
  assert.deepEqual(items[0], {
    name: "alpha", preview: false, category: "ロボット", title: "アルファ",
    description: "検証用モデルです。", categoryId: "robots", projectId: "robot-family",
    project: "ロボット系列", tags: ["検証"], status: "active", organized: true,
    available: true, unavailableReason: null, catalogErrors: [],
  });
});

test("metadata の無い新規モデルを除外せず未整理として返す", (t) => {
  const f = fixture(t);
  const item = listModelCatalog(f).find((candidate) => candidate.name === "new-model");
  assert.equal(item.title, "new-model");
  assert.equal(item.organized, false);
  assert.equal(item.available, true);
  assert.equal(item.preview, true);
  assert.match(item.catalogErrors[0], /ファイルがありません/);
});

test("分類が一致しない projectId を検証エラーにする", (t) => {
  const f = fixture(t);
  const groupsFile = path.join(f.modelsDir, "catalog-groups.json");
  const groups = JSON.parse(fs.readFileSync(groupsFile, "utf8"));
  groups.categories.push({ id: "games", title: "ゲーム" });
  writeJson(groupsFile, groups);
  const catalogFile = path.join(f.modelsDir, "alpha", "catalog.json");
  const metadata = JSON.parse(fs.readFileSync(catalogFile, "utf8"));
  metadata.categoryId = "games";
  writeJson(catalogFile, metadata);
  const result = checkCatalog(f);
  assert.ok(result.errors.some((error) => error.includes("分類が categoryId と一致しません")));
  const item = listModelCatalog(f).find((candidate) => candidate.name === "alpha");
  assert.equal(item.organized, false);
  assert.equal(item.category, "旧分類");
  const originalError = console.error;
  console.error = () => {};
  try {
    assert.equal(runCheck(f.root), 1);
  } finally {
    console.error = originalError;
  }
});

test("参照用と保管用の状態を失わず一覧へ返す", (t) => {
  const f = fixture(t);
  const file = path.join(f.modelsDir, "alpha", "catalog.json");
  const metadata = JSON.parse(fs.readFileSync(file, "utf8"));
  for (const status of ["reference", "archived"]) {
    writeJson(file, { ...metadata, status });
    const item = listModelCatalog(f).find(candidate => candidate.name === "alpha");
    assert.equal(item.organized, true);
    assert.equal(item.status, status);
    assert.equal(item.title, "アルファ");
  }
});

test("リポジトリの全モデルが過不足なく検証を通る", () => {
  const root = path.resolve(__dirname, "..");
  const result = checkCatalog({
    modelsDir: path.join(root, "models"),
    previewDir: path.join(root, "viewer", "preview"),
  });
  assert.deepEqual(result.errors, []);
  const expected = fs.readdirSync(path.join(root, "models"), { withFileTypes: true })
    .filter(entry => entry.isDirectory()).map(entry => entry.name).sort();
  assert.ok(expected.length > 0);
  assert.deepEqual(result.modelNames, expected);
  assert.deepEqual(result.items.map(item => item.name), expected);
  assert.equal(result.items.filter(item => item.organized).length, expected.length);
  const originalLog = console.log;
  console.log = () => {};
  try {
    assert.equal(runCheck(root), 0);
  } finally {
    console.log = originalLog;
  }
});
