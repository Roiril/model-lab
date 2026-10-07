#!/usr/bin/env node
const path = require("path");
const { checkCatalog } = require("../lib/model_catalog");

function runCheck(root = path.resolve(__dirname, "..")) {
  const modelsDir = path.join(root, "models");
  const previewDir = path.join(root, "viewer", "preview");
  const result = checkCatalog({ modelsDir, previewDir });
  if (result.errors.length) {
    for (const error of result.errors) console.error(error);
    console.error(`catalog check: ${result.errors.length} 件の問題`);
    return 1;
  }
  const available = result.items.filter((item) => item.available).length;
  console.log(`catalog check: OK (${result.modelNames.length} models, ${available} available)`);
  return 0;
}

if (require.main === module) {
  const command = process.argv[2] || "check";
  if (command !== "check") {
    console.error("使い方: node tools/catalog.js check");
    process.exitCode = 2;
  } else {
    process.exitCode = runCheck();
  }
}

module.exports = { runCheck };
