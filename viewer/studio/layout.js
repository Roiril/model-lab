const PLATE_FILE_RE = /-studio-plate-/i;

export function isPlateDerivedFile(name) {
  return PLATE_FILE_RE.test(String(name || ""));
}

export function plateDraftKey(model, layout) {
  if (layout && layout.kind === "plate" && layout.id) {
    return `studio.draft.${model}.plate.${layout.id}`;
  }
  return `studio.draft.${model}`;
}

export function validPlateManifest(value, model) {
  if (!value || value.version !== 1 || value.kind !== "plate" || value.model !== model) return false;
  if (typeof value.id !== "string" || !value.id
    || typeof value.source3mf !== "string" || !value.source3mf
    || typeof value.source3mfSha256 !== "string" || !value.source3mfSha256
    || !Array.isArray(value.parts) || !value.parts.length) return false;
  if (!value.bed || !Number.isFinite(value.bed.width) || !Number.isFinite(value.bed.depth)) return false;
  const vector3 = (v) => Array.isArray(v) && v.length === 3 && v.every(Number.isFinite);
  return value.parts.every((part) => part && typeof part.file === "string" && part.file
    && typeof part.sourcePart === "string" && typeof part.sourceFile === "string"
    && typeof part.objectId === "string" && Array.isArray(part.buildTransform)
    && part.buildTransform.length === 12 && part.buildTransform.every(Number.isFinite)
    && typeof part.sha256 === "string" && Number.isFinite(part.size)
    && part.bbox && vector3(part.bbox.min) && vector3(part.bbox.max)
    && part.source && typeof part.source.file === "string"
    && typeof part.source.sha256 === "string"
    && Number.isFinite(part.source.size) && Number.isFinite(part.source.mtime));
}

export function plateManifestStale(manifest, inventory, toleranceMs = 1.1) {
  if (!manifest) return true;
  const byName = new Map((inventory || []).map((file) => [file.name, file]));
  return manifest.parts.some((part) => {
    const source = part.source || {};
    const actual = byName.get(source.file);
    return !actual || actual.size !== source.size
      || !Number.isFinite(actual.mtime) || Math.abs(actual.mtime - source.mtime) > toleranceMs;
  });
}

export function plateLayoutSnapshot(layout) {
  if (!layout || layout.kind !== "plate") return { kind: "assembled" };
  return {
    kind: "plate",
    id: layout.id,
    source3mf: layout.source3mf,
    source3mfSha256: layout.source3mfSha256,
    manifestVersion: 1,
  };
}

export function platePartForFile(layout, file) {
  if (!layout || layout.kind !== "plate") return null;
  return (layout.parts || []).find((part) => part.file === file) || null;
}

export function createLatestGate() {
  let current = 0;
  return {
    next() { current += 1; return current; },
    isCurrent(token) { return token === current; },
  };
}
