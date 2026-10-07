const fs = require("fs");
const path = require("path");

const SCHEMA_VERSION = 1;
const ACTIVE_STATUS = "active";
const MODEL_STATUSES = new Set([ACTIVE_STATUS, "reference", "archived"]);
const DEFAULT_CATEGORY = "その他";

function readJson(file) {
  try {
    return { value: JSON.parse(fs.readFileSync(file, "utf8")), error: null };
  } catch (error) {
    return { value: null, error: error.code === "ENOENT" ? "ファイルがありません" : `JSON を読めません: ${error.message}` };
  }
}

function validateGroups(value) {
  const errors = [];
  if (!value || typeof value !== "object" || Array.isArray(value)) return ["ルートはオブジェクトにしてください"];
  if (value.schemaVersion !== SCHEMA_VERSION) errors.push(`schemaVersion は ${SCHEMA_VERSION} にしてください`);
  for (const key of ["categories", "projects"]) {
    if (!Array.isArray(value[key])) errors.push(`${key} は配列にしてください`);
  }
  if (errors.length) return errors;

  const categoryIds = new Set();
  for (const [index, category] of value.categories.entries()) {
    if (!category || typeof category !== "object" || Array.isArray(category)) {
      errors.push(`categories[${index}] はオブジェクトにしてください`);
      continue;
    }
    if (typeof category.id !== "string" || !category.id.trim()) errors.push(`categories[${index}].id が空です`);
    else if (categoryIds.has(category.id)) errors.push(`category id が重複しています: ${category.id}`);
    else categoryIds.add(category.id);
    if (typeof category.title !== "string" || !category.title.trim()) errors.push(`categories[${index}].title が空です`);
    else if (!/[ぁ-んァ-ヶ一-龠々]/.test(category.title)) errors.push(`categories[${index}].title に日本語を含めてください`);
  }

  const projectIds = new Set();
  for (const [index, project] of value.projects.entries()) {
    if (!project || typeof project !== "object" || Array.isArray(project)) {
      errors.push(`projects[${index}] はオブジェクトにしてください`);
      continue;
    }
    if (typeof project.id !== "string" || !project.id.trim()) errors.push(`projects[${index}].id が空です`);
    else if (projectIds.has(project.id)) errors.push(`project id が重複しています: ${project.id}`);
    else projectIds.add(project.id);
    if (typeof project.title !== "string" || !project.title.trim()) errors.push(`projects[${index}].title が空です`);
    else if (!/[ぁ-んァ-ヶ一-龠々]/.test(project.title)) errors.push(`projects[${index}].title に日本語を含めてください`);
    if (!categoryIds.has(project.categoryId)) errors.push(`projects[${index}].categoryId が未定義です: ${project.categoryId}`);
  }
  return errors;
}

function loadGroups(modelsDir) {
  const file = path.join(modelsDir, "catalog-groups.json");
  const { value, error } = readJson(file);
  const errors = error ? [error] : validateGroups(value);
  const categories = new Map();
  const projects = new Map();
  if (!errors.length) {
    for (const category of value.categories) categories.set(category.id, category);
    for (const project of value.projects) projects.set(project.id, project);
  }
  return { file, value, errors, categories, projects };
}

function validateModelMetadata(value, groups) {
  const errors = [];
  if (!value || typeof value !== "object" || Array.isArray(value)) return ["ルートはオブジェクトにしてください"];
  if (value.schemaVersion !== SCHEMA_VERSION) errors.push(`schemaVersion は ${SCHEMA_VERSION} にしてください`);
  for (const key of ["title", "description", "categoryId"]) {
    if (typeof value[key] !== "string" || !value[key].trim()) errors.push(`${key} が空です`);
  }
  if (typeof value.title === "string" && !/[ぁ-んァ-ヶ一-龠々]/.test(value.title)) {
    errors.push("title に日本語を含めてください");
  }
  if (!Object.prototype.hasOwnProperty.call(value, "projectId") ||
      (value.projectId !== null && (typeof value.projectId !== "string" || !value.projectId.trim()))) {
    errors.push("projectId は文字列または null にしてください");
  }
  if (!Array.isArray(value.tags) || value.tags.some((tag) => typeof tag !== "string" || !tag.trim())) {
    errors.push("tags は空でない文字列の配列にしてください");
  }
  if (!MODEL_STATUSES.has(value.status)) errors.push("status は active / reference / archived にしてください");
  if (!groups.errors.length) {
    if (!groups.categories.has(value.categoryId)) errors.push(`categoryId が未定義です: ${value.categoryId}`);
    if (value.projectId !== null) {
      const project = groups.projects.get(value.projectId);
      if (!project) errors.push(`projectId が未定義です: ${value.projectId}`);
      else if (project.categoryId !== value.categoryId) errors.push(`projectId の分類が categoryId と一致しません: ${value.projectId}`);
    }
  } else {
    errors.push("catalog-groups.json が不正です");
  }
  return errors;
}

function loadModelMetadata(modelsDir, modelName, groups = loadGroups(modelsDir)) {
  const file = path.join(modelsDir, modelName, "catalog.json");
  const { value, error } = readJson(file);
  const errors = error ? [error] : validateModelMetadata(value, groups);
  return { file, value, errors, organized: errors.length === 0 };
}

function readLegacyCategory(modelsDir, modelName) {
  try {
    const text = fs.readFileSync(path.join(modelsDir, modelName, "params.py"), "utf8");
    const match = text.match(/#\s*CATEGORY:\s*(.+)/);
    if (match) return match[1].trim();
  } catch { /* フォールバックへ進む */ }
  return DEFAULT_CATEGORY;
}

function listModelDirectories(modelsDir) {
  if (!fs.existsSync(modelsDir)) return [];
  return fs.readdirSync(modelsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function unavailableReason(modelDir) {
  const hasParams = fs.existsSync(path.join(modelDir, "params.py"));
  const hasModel = fs.existsSync(path.join(modelDir, "model.py"));
  if (hasParams || hasModel || fs.readdirSync(modelDir).some((name) => /\.(py|js|glb|stl)$/i.test(name))) {
    return "別の形式で作成";
  }
  return "生成ファイルがありません";
}

function modelCatalogItem({ modelsDir, previewDir, modelName, groups }) {
  const modelDir = path.join(modelsDir, modelName);
  const metadata = loadModelMetadata(modelsDir, modelName, groups);
  const hasPair = fs.existsSync(path.join(modelDir, "params.py")) && fs.existsSync(path.join(modelDir, "model.py"));
  const preview = fs.existsSync(path.join(previewDir, `${modelName}.js`));
  const available = hasPair || preview;
  const value = metadata.organized ? metadata.value : null;
  const category = value ? groups.categories.get(value.categoryId) : null;
  const project = value && value.projectId ? groups.projects.get(value.projectId) : null;
  return {
    name: modelName,
    preview,
    category: category ? category.title : readLegacyCategory(modelsDir, modelName),
    title: value ? value.title : modelName,
    description: value ? value.description : "",
    categoryId: value ? value.categoryId : null,
    projectId: value ? value.projectId : null,
    project: project ? project.title : null,
    tags: value ? value.tags : [],
    status: value ? value.status : ACTIVE_STATUS,
    organized: metadata.organized,
    available,
    unavailableReason: available ? null : unavailableReason(modelDir),
    catalogErrors: metadata.errors,
  };
}

function listModelCatalog({ modelsDir, previewDir }) {
  const groups = loadGroups(modelsDir);
  return listModelDirectories(modelsDir).map((modelName) =>
    modelCatalogItem({ modelsDir, previewDir, modelName, groups }));
}

function checkCatalog({ modelsDir, previewDir }) {
  const errors = [];
  const groups = loadGroups(modelsDir);
  for (const error of groups.errors) errors.push(`models/catalog-groups.json: ${error}`);
  const modelNames = listModelDirectories(modelsDir);
  for (const modelName of modelNames) {
    const metadata = loadModelMetadata(modelsDir, modelName, groups);
    for (const error of metadata.errors) errors.push(`models/${modelName}/catalog.json: ${error}`);
  }
  const items = modelNames.map((modelName) => modelCatalogItem({ modelsDir, previewDir, modelName, groups }));
  return { errors, modelNames, items, groups };
}

module.exports = {
  ACTIVE_STATUS,
  DEFAULT_CATEGORY,
  SCHEMA_VERSION,
  checkCatalog,
  listModelCatalog,
  listModelDirectories,
  loadGroups,
  loadModelMetadata,
  modelCatalogItem,
  readLegacyCategory,
  validateGroups,
  validateModelMetadata,
};
