// Keep a missing model from silently showing a different model's geometry.
export const normalizeModelName = (s) => String(s).toLowerCase().replace(/-/g, "_");
export function filesForModel(name, files, modelNames = []) {
  const want = normalizeModelName(name);
  return files.filter((file) => {
    const f = normalizeModelName(file);
    if (!(f === `${want}.stl` || f.startsWith(`${want}_`))) return false;
    return !modelNames.some((other) => {
      const n = normalizeModelName(other);
      return n.length > want.length && (f === `${n}.stl` || f.startsWith(`${n}_`));
    });
  }).sort((a, b) => a.length - b.length || a.localeCompare(b));
}
export function selectModelFile(name, files, modelNames = []) {
  const heads = filesForModel(name, files, modelNames);
  return heads.find((x) => /[_-]asm\.stl$/i.test(x))
    || heads.find((x) => normalizeModelName(x) === `${normalizeModelName(name)}.stl`)
    || heads[0] || null;
}
