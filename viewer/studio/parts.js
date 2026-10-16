// 部品台帳（viewer/studio/parts/<model>.json）と、ユーザーの呼び名。three も DOM も使わない純関数だけ。
// 形は CONTRACT.md §7。部品の見え方（透過・隠す）のキーは、台帳があれば部品 id、無ければ STL 名。
// 呼び名の保存は store.js（localStorage studio.partNames.<model>）、画面は panels.js のパーツ一覧。

export const OTHER_GROUP_ID = "__other";
export const OTHER_GROUP_LABEL = "その他";
export const KIND_LABELS = { printed: "印刷", stock: "既製品", jig: "治具" };
const NAME_MAX = 60;

export function ledgerUrl(model) { return `/viewer/studio/parts/${encodeURIComponent(model)}.json`; }
export function partNamesKey(model) { return `studio.partNames.${model}`; }

// 台帳の STL 名。台帳があるモデルの組立では、この名前を候補の選び方から除く
const PART_FILE_RE = /-part-/i;
export function isPartDerivedFile(name) { return PART_FILE_RE.test(String(name || "")); }

const str = (v) => typeof v === "string" && v.length > 0;

// 読み込んだ JSON を使える形にする。形が違えば null（台帳なしとして扱う）。
// 戻り値: { model, sourceSha256, groups:[{id,label,color}], parts:[...], byId:Map, byFile:Map }
export function normalizeLedger(raw, model) {
  if (!raw || typeof raw !== "object" || raw.version !== 1) return null;
  if (model !== undefined && raw.model !== model) return null;
  if (!Array.isArray(raw.parts) || !raw.parts.length) return null;
  const groups = [];
  const seenGroup = new Set();
  for (const g of Array.isArray(raw.groups) ? raw.groups : []) {
    if (!g || !str(g.id) || seenGroup.has(g.id)) continue;
    seenGroup.add(g.id);
    groups.push({ id: g.id, label: str(g.label) ? g.label : g.id, color: str(g.color) ? g.color : null });
  }
  const parts = [];
  const byId = new Map();
  const byFile = new Map();
  for (const p of raw.parts) {
    if (!p || !str(p.id) || !str(p.file) || byId.has(p.id)) continue;
    const label = str(p.label) ? p.label : p.id;
    const part = {
      id: p.id,
      label,
      systemLabel: str(p.systemLabel) ? p.systemLabel : label,
      group: str(p.group) ? p.group : OTHER_GROUP_ID,
      kind: p.kind === "stock" || p.kind === "jig" ? p.kind : "printed",
      file: p.file,
      aliases: Array.isArray(p.aliases) ? p.aliases.filter(str) : [],
      color: str(p.color) ? p.color : null,
      size: Number.isFinite(p.size) ? p.size : null,
      sha256: str(p.sha256) ? p.sha256 : null,
    };
    parts.push(part);
    byId.set(part.id, part);
    byFile.set(part.file, part);
  }
  if (!parts.length) return null;
  // 台帳に無い群を指す部品は「その他」へ
  let needOther = false;
  for (const p of parts) {
    if (!seenGroup.has(p.group)) { p.group = OTHER_GROUP_ID; needOther = true; }
  }
  if (needOther && !groups.some((g) => g.id === OTHER_GROUP_ID)) {
    groups.push({ id: OTHER_GROUP_ID, label: OTHER_GROUP_LABEL, color: null });
  }
  return { model: raw.model, sourceSha256: str(raw.sourceSha256) ? raw.sourceSha256 : null, groups, parts, byId, byFile };
}

export const partByFile = (ledger, file) => (ledger ? ledger.byFile.get(file) || null : null);
export const partById = (ledger, id) => (ledger ? ledger.byId.get(id) || null : null);
export const groupOf = (ledger, part) => (ledger && part ? ledger.groups.find((g) => g.id === part.group) || null : null);

// --- 呼び名 -------------------------------------------------------------------

// 保存データを { id: {label} } に直す。形が違えば空
export function normalizePartNames(raw) {
  const out = {};
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return out;
  for (const [id, v] of Object.entries(raw)) {
    const label = v && typeof v === "object" ? v.label : null;
    if (typeof label === "string" && label.trim()) out[id] = { label: label.trim().slice(0, NAME_MAX) };
  }
  return out;
}

export const systemLabelOf = (part) => part.systemLabel || part.label;
export const displayLabel = (part, names) => (names && names[part.id] && names[part.id].label) || part.label;
// シュビーの名前と違う名前で呼んでいるか（台帳に書き戻し済みの呼び名も含む）
export const isRenamed = (part, names) => displayLabel(part, names) !== systemLabelOf(part);

// 呼び名を 1 つ変えた新しい names。台帳の名前と同じ（空も含む）なら上書きを消す
export function withPartName(names, part, text) {
  const out = normalizePartNames(names);
  const label = String(text ?? "").trim().slice(0, NAME_MAX);
  if (!label || label === part.label) delete out[part.id];
  else out[part.id] = { label };
  return out;
}

// 依頼 JSON の partNames。台帳の名前と違うものだけ { id: {label, systemLabel} }
export function partNamesForRequest(names, ledger) {
  const out = {};
  if (!ledger) return out;
  for (const [id, v] of Object.entries(normalizePartNames(names))) {
    const part = ledger.byId.get(id);
    if (!part || v.label === part.label) continue;
    out[id] = { label: v.label, systemLabel: systemLabelOf(part) };
  }
  return out;
}

// 同じ名前の部品が複数あるか（F1 の「空の面板」など）。選ぶ画面では群名を添える
export function duplicateLabels(ledger, names) {
  const count = new Map();
  for (const p of ledger ? ledger.parts : []) {
    const l = displayLabel(p, names);
    count.set(l, (count.get(l) || 0) + 1);
  }
  return new Set([...count].filter(([, n]) => n > 1).map(([l]) => l));
}

// 一覧・メニュー・3D のラベルに出す名前。重複しているときだけ群名を添える
export function partName(ledger, names, part, dup = duplicateLabels(ledger, names)) {
  const label = displayLabel(part, names);
  if (!dup.has(label)) return label;
  const g = groupOf(ledger, part);
  return g ? `${label}（${g.label}）` : label;
}

// --- 指示への部品名 -----------------------------------------------------------

// 指示の file から、依頼に入れる部品の印。台帳が無い・当たらなければ null
export function partRefForFile(ledger, names, file) {
  const part = partByFile(ledger, file);
  if (!part) return null;
  const ref = { partId: part.id, partLabel: displayLabel(part, names) };
  const sys = systemLabelOf(part);
  if (sys !== ref.partLabel) ref.partSystemLabel = sys;
  return ref;
}

// 依頼の 1 指示に partId / partLabel（計測は 2 点目の部品が違うときだけ partIdB / partLabelB）を足す
export function withPartRefs(item, ledger, names) {
  const out = { ...item };
  const a = partRefForFile(ledger, names, item.file);
  if (a) Object.assign(out, a);
  if (item.type === "measure" && item.fileB && item.fileB !== item.file) {
    const b = partRefForFile(ledger, names, item.fileB);
    if (b) { out.partIdB = b.partId; out.partLabelB = b.partLabel; }
  }
  return out;
}

// 下書きカードの表示用。「外装 の面」のように名前で出す。無ければ null
export function itemPartText(item, ledger, names) {
  const dup = duplicateLabels(ledger, names);
  const part = partByFile(ledger, item.file);
  if (!part) return null;
  let t = partName(ledger, names, part, dup);
  if (item.type === "measure" && item.fileB && item.fileB !== item.file) {
    const b = partByFile(ledger, item.fileB);
    if (b) t += ` ↔ ${partName(ledger, names, b, dup)}`;
  }
  return t;
}

// --- 一覧 ---------------------------------------------------------------------

const fold = (s) => String(s).normalize("NFKC").toLowerCase().replace(/\s+/g, "");

// 名前・シュビーの名前・別名・id・群名のどれかに、空白で分けた語が全部入っているか
export function matchPart(part, names, groupLabel, query) {
  const tokens = String(query || "").normalize("NFKC").toLowerCase().split(/\s+/).filter(Boolean);
  if (!tokens.length) return true;
  const hay = [displayLabel(part, names), part.label, systemLabelOf(part), part.id, ...part.aliases, groupLabel || ""].map(fold).join("\n");
  return tokens.every((t) => hay.includes(fold(t)));
}

// 群ごとの木。絞り込み中は一致した部品が無い群を出さない。戻り値: [{group, parts}]
export function buildTree(ledger, names, query = "") {
  if (!ledger) return [];
  const q = String(query || "").trim();
  const out = [];
  for (const group of ledger.groups) {
    const parts = ledger.parts.filter((p) => p.group === group.id && matchPart(p, names, group.label, q));
    if (parts.length) out.push({ group, parts });
  }
  return out;
}

// 部品の一覧が全部同じ見え方ならそれ、混ざっていれば "mixed"
export function commonMode(keys, modes) {
  let found = null;
  for (const k of keys) {
    const m = (modes && modes[k]) === "ghost" || (modes && modes[k]) === "hidden" ? modes[k] : "normal";
    if (found === null) found = m;
    else if (found !== m) return "mixed";
  }
  return found || "normal";
}

// 複数の部品の見え方を 1 度に変えた新しい modes（normal ならキーを消す）
export function withModes(modes, keys, mode) {
  const out = {};
  for (const [k, v] of Object.entries(modes || {})) if (v === "ghost" || v === "hidden") out[k] = v;
  for (const k of keys) {
    if (mode === "ghost" || mode === "hidden") out[k] = mode;
    else delete out[k];
  }
  return out;
}
