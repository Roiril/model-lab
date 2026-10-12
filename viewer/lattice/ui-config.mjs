import { frameAt } from './motion.mjs';

// 検証ページ（物理検証・組み立て）の、モデルごとの違いを集めたモジュール。
// 違いは assets/<model>.json の `ui` 節に置き、ページのコードにモデル名を書かない。
// 形の定義と必須ファイルは viewer/lattice/CONTRACT.md。

export const DEFAULT_MODEL = 'mystery-box-sg92r-c3';
export const MAX_SERIES = 5;
// group-lift: 計算した高さで群の部品をZ方向に動かす（C3 / C4-1 / C4-2）。
// motion-frames: サーボ角で motion.frames を補間し、全部品をそのまま動かす。
export const PLAYBACKS = Object.freeze(['group-lift', 'motion-frames']);
export const DOWNLOAD_BASES = Object.freeze(['exports', 'prints']);

// 書き出し済みの表示データに ui 節を持たない 3 モデルの見せ方（書き出し側の文言をそのまま保つ）。
// 表示データ自体は変えない（過去モデルの監査がバイト一致を見る）。新しいモデルは build/ui.json から ui 節が入る。
export const LEGACY_UI = Object.freeze({
  'mystery-box-sg92r-c3': {
    label: 'C3', displayName: '住人の箱 C3', navLabel: 'C3 立方格子', navOrder: 10,
    dimensionsFallback: '76〜80 mm（生成値を優先）',
    physics: { title: '立方格子の波', playback: 'group-lift', term: '格子', openLabel: '波を進める', closeLabel: '戻す' },
    assembly: {
      servoSetup: '箱の外でSG92Rを90°にして付属ホーンと駆動歯車を付けます。カムと軸を90°の位相で入れます。格子を入れる前にhで15°へ戻して停止します。gで15〜165°を片道2秒で動かします。分解時は格子を外した後にcで90°へ戻します。',
      maxTranslationMm: 1, maxRotationDeg: 5,
    },
    print: { downloadBase: 'exports' },
  },
  'mystery-box-sg92r-c4': {
    label: 'C4-1', displayName: '住人の箱 C4-1', navLabel: 'C4-1 六角格子', navOrder: 20,
    dimensionsFallback: '76 × 76 mm（設計値）',
    physics: { title: '六角格子の呼吸', playback: 'group-lift', term: '格子', openLabel: '持ち上げる', closeLabel: '戻す' },
    assembly: {
      servoSetup: 'SG92Rを90°にして付属ホーンを付けます。ホーン受けとカムを90°の位相で組みます。右の保持具を留めたらhで10°へ戻して停止します。格子はその後に入れます。gで10〜170°を片道1.5秒で動かします。分解時は格子を外した後にcで90°へ戻します。',
      maxTranslationMm: 1, maxRotationDeg: 5,
    },
    print: { downloadBase: 'exports' },
  },
  'mystery-box-sg92r-c4-2': {
    label: 'C4-2', displayName: '住人の箱 C4-2', navLabel: 'C4-2 六角格子', navOrder: 30,
    dimensionsFallback: '76〜80 mm（生成値を優先）',
    physics: { title: '六角格子の凹み', playback: 'group-lift', term: '格子', openLabel: '次の場所へ', closeLabel: '戻す' },
    assembly: {
      servoSetup: '箱の外で付属ホーンをホーン受けへ入れます。この一式を底側から先に入れます。配線を通します。SG92Rをcで90°にして底側からホーンへ差します。円盤と角キーと止め輪を組みます。格子を入れる前にhで15°へ3秒かけて戻します。その後に格子と天板を留めます。最後に底板を閉じます。1で左上50°、2で中央90°、3で右上130°、4で下側165°を選びます。gで五つの形を順に動かします。分解は工程の逆順です。格子を外した後にcで90°へ戻します。',
      maxTranslationMm: 1, maxRotationDeg: 1,
    },
    print: { downloadBase: 'prints' },
  },
});

// 表示データの ui 節。無ければ旧 3 モデルはモデル名から引く。
export function uiSource(data, model) {
  return data?.ui ?? LEGACY_UI[model];
}

// モデル切り替えの一覧。旧 3 モデルは常に載り、ほかは assets/index.json の中身を足す。
// 今開いているモデルが一覧に無くても載せる（書き出し直し前の確認用）。
export function modelEntries(listed, current) {
  const entries = new Map(Object.entries(LEGACY_UI).map(([id, ui]) => [id, { id, navLabel: ui.navLabel, navOrder: ui.navOrder }]));
  for (const entry of Array.isArray(listed) ? listed : []) {
    if (entry && typeof entry.id === 'string' && MODEL_ID.test(entry.id)) {
      entries.set(entry.id, { id: entry.id, navLabel: String(entry.navLabel || entry.id), navOrder: Number.isFinite(entry.navOrder) ? entry.navOrder : 100 });
    }
  }
  if (current && !entries.has(current)) entries.set(current, { id: current, navLabel: current, navOrder: 100 });
  return [...entries.values()].sort((a, b) => a.navOrder - b.navOrder || a.id.localeCompare(b.id));
}

const MODEL_ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$/;
const HEX_COLOR = /^#[0-9a-f]{6}$/i;
const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);

// URL の model 値。assets/<model>.json を読めればどのモデルでも開く。
// パスを抜ける文字や空は既定モデルへ戻す。
export function resolveModel(value) {
  return typeof value === 'string' && MODEL_ID.test(value) && !value.includes('..') ? value : DEFAULT_MODEL;
}

function text(value, path, fallback) {
  if (value === undefined || value === null) return fallback;
  if (typeof value !== 'string' || !value.trim()) throw new TypeError(`ui.${path} は空でない文字列にしてください`);
  return value;
}

function positive(value, path, fallback) {
  if (value === undefined || value === null) return fallback;
  if (!Number.isFinite(value) || value <= 0) throw new TypeError(`ui.${path} は正の数にしてください`);
  return value;
}

// ui 節を検査して、既定値を埋めた形にする。壊れた設定は黙って直さず例外にする。
export function normalizeUi(raw, { model, partIds = [], groupIds = [] } = {}) {
  if (!isObject(raw)) throw new TypeError('表示設定（ui）がありません。tools/lattice_web.py で書き出し直してください');
  const label = text(raw.label, 'label', model);
  const displayName = text(raw.displayName, 'displayName', label);
  const physics = raw.physics ?? {}, assembly = raw.assembly ?? {}, print = raw.print ?? {};
  for (const [name, value] of [['physics', physics], ['assembly', assembly], ['print', print]])
    if (!isObject(value)) throw new TypeError(`ui.${name} はオブジェクトにしてください`);
  const playback = physics.playback ?? 'group-lift';
  if (!PLAYBACKS.includes(playback)) throw new RangeError(`ui.physics.playback は ${PLAYBACKS.join(' / ')} のどれかにしてください（${playback}）`);
  const downloadBase = print.downloadBase ?? 'prints';
  if (!DOWNLOAD_BASES.includes(downloadBase)) throw new RangeError(`ui.print.downloadBase は ${DOWNLOAD_BASES.join(' / ')} のどれかにしてください（${downloadBase}）`);
  let chartSeries = null;
  if (physics.chartSeries !== undefined && physics.chartSeries !== null) {
    if (!Array.isArray(physics.chartSeries) || physics.chartSeries.some(id => typeof id !== 'string'))
      throw new TypeError('ui.physics.chartSeries は群 id の配列にしてください');
    chartSeries = [...physics.chartSeries];
  }
  const ui = {
    label,
    displayName,
    navLabel: text(raw.navLabel, 'navLabel', label),
    navOrder: Number.isFinite(raw.navOrder) ? raw.navOrder : 100,
    dimensionsFallback: text(raw.dimensionsFallback, 'dimensionsFallback', '未記録'),
    physics: {
      title: text(physics.title, 'physics.title', displayName),
      playback,
      term: text(physics.term, 'physics.term', '可動部'),
      openLabel: text(physics.openLabel, 'physics.openLabel', null),
      closeLabel: text(physics.closeLabel, 'physics.closeLabel', null),
      liftLabel: text(physics.liftLabel, 'physics.liftLabel', null),
      chartLabel: text(physics.chartLabel, 'physics.chartLabel', null),
      chartAxis: text(physics.chartAxis, 'physics.chartAxis', null),
      patternNote: text(physics.patternNote, 'physics.patternNote', null),
      simLimits: text(physics.simLimits, 'physics.simLimits', null),
      massNote: text(physics.massNote, 'physics.massNote', null),
      chartSeries,
    },
    assembly: {
      servoSetup: text(assembly.servoSetup, 'assembly.servoSetup', '手順は各工程の説明に従います。'),
      maxTranslationMm: positive(assembly.maxTranslationMm, 'assembly.maxTranslationMm', null),
      maxRotationDeg: positive(assembly.maxRotationDeg, 'assembly.maxRotationDeg', null),
    },
    print: { downloadBase },
    legendGroups: [],
    colors: {},
  };
  if (groupIds.length) ui.physics.seriesIndices = physicsSeries(ui, groupIds);
  const known = new Set(partIds);
  const claimed = new Set();
  const colors = {};
  for (const [index, group] of (raw.legendGroups ?? []).entries()) {
    if (!isObject(group)) throw new TypeError(`ui.legendGroups[${index}] はオブジェクトにしてください`);
    const name = text(group.label, `legendGroups[${index}].label`, null);
    if (!name) throw new TypeError(`ui.legendGroups[${index}].label がありません`);
    if (group.color !== undefined && !HEX_COLOR.test(group.color)) throw new TypeError(`ui.legendGroups[${index}].color は #rrggbb にしてください`);
    const wanted = Array.isArray(group.parts) ? group.parts
      : typeof group.prefix === 'string' && group.prefix ? partIds.filter(id => id.startsWith(group.prefix)) : null;
    if (!wanted) throw new TypeError(`ui.legendGroups[${index}] には parts（id の配列）か prefix（文字列）が要ります`);
    for (const id of wanted) if (partIds.length && !known.has(id)) throw new RangeError(`ui.legendGroups[${index}] の部品 ${id} が表示データにありません`);
    // 部品は最初に載せた群へ入る。
    const ids = wanted.filter(id => !claimed.has(id));
    if (!ids.length) throw new RangeError(`ui.legendGroups[${index}]（${name}）に該当する部品がありません`);
    ids.forEach(id => claimed.add(id));
    ui.legendGroups.push({ label: name, ids, color: group.color ?? null });
    if (group.color) for (const id of ids) colors[id] = group.color;
  }
  if (raw.colors !== undefined) {
    if (!isObject(raw.colors)) throw new TypeError('ui.colors は {部品id: "#rrggbb"} にしてください');
    for (const [id, color] of Object.entries(raw.colors)) {
      if (!HEX_COLOR.test(color)) throw new TypeError(`ui.colors.${id} は #rrggbb にしてください`);
      if (partIds.length && !known.has(id)) throw new RangeError(`ui.colors の部品 ${id} が表示データにありません`);
      colors[id] = color;
    }
  }
  ui.colors = colors;
  return ui;
}

// 凡例の並び。群にまとめた部品を先に出し、残りは 1 部品ずつ。
export function legendEntries(ui, parts) {
  const grouped = new Set(ui.legendGroups.flatMap(group => group.ids));
  const byId = new Map(parts.map(part => [part.id, part]));
  return [
    ...ui.legendGroups.map(group => ({ label: group.label, ids: group.ids.filter(id => byId.has(id)) })),
    ...parts.filter(part => !grouped.has(part.id)).map(part => ({ label: part.label || part.id, ids: [part.id] })),
  ].filter(entry => entry.ids.length);
}

// 折れ線に出す群の番号（sim_tables.groups の並びの中での位置）。
// 指定が無ければ全部。折れ線は MAX_SERIES 本まで。
export function physicsSeries(ui, groupIds) {
  const wanted = ui.physics.chartSeries;
  if (wanted === null) {
    if (groupIds.length > MAX_SERIES)
      throw new RangeError(`群が${groupIds.length}個あり折れ線は${MAX_SERIES}本までです。ui.physics.chartSeries で表示する群を選んでください`);
    return groupIds.map((_, index) => index);
  }
  if (!wanted.length || wanted.length > MAX_SERIES) throw new RangeError(`ui.physics.chartSeries は1〜${MAX_SERIES}個にしてください（${wanted.length}個）`);
  if (new Set(wanted).size !== wanted.length) throw new RangeError('ui.physics.chartSeries に同じ群が2回あります');
  return wanted.map(id => {
    const index = groupIds.indexOf(id);
    if (index < 0) throw new RangeError(`ui.physics.chartSeries の ${id} が sim_tables.groups にありません`);
    return index;
  });
}

// 物理画面の文言。ui に書いてあればそれ、無ければ term と凹みの有無から作る。
export function physicsText(ui, hasPatterns) {
  const { term } = ui.physics;
  return {
    term,
    openLabel: ui.physics.openLabel ?? (hasPatterns ? '次の場所へ' : '波を進める'),
    closeLabel: ui.physics.closeLabel ?? '戻す',
    liftLabel: ui.physics.liftLabel ?? (hasPatterns ? `${term}の上下（凹みは−）` : `${term}の上昇`),
    chartLabel: ui.physics.chartLabel ?? (hasPatterns ? `各${term}の凹みの時間変化` : `各${term}の上昇の時間変化`),
    chartAxis: ui.physics.chartAxis ?? (hasPatterns ? '上下 (mm)' : '上昇 (mm)'),
  };
}

export function calibrationLimitText(assembly) {
  const parts = [];
  if (assembly.maxTranslationMm !== null) parts.push(`${assembly.maxTranslationMm}mm以下の並進`);
  if (assembly.maxRotationDeg !== null) parts.push(`${assembly.maxRotationDeg}°以下の回転`);
  return parts.length ? `${parts.join('と')}で検査しています。` : '';
}

// 再生中の 1 コマの姿勢。サーボ角で motion.frames を補間する。
// group-lift は、その上で群の部品のZを計算した高さに置き換える（元の frames は書き換えない）。
// motion-frames は置き換えず、画素・歯車・軸など全部品を frames のまま動かす。
export function posedTransforms(frames, row, ui, groups) {
  const transforms = frameAt(frames, row.servoDeg).transforms;
  if (ui.physics.playback !== 'group-lift') return transforms;
  const out = { ...transforms };
  groups.forEach((group, index) => {
    if (out[group.id]) { out[group.id] = [...out[group.id]]; out[group.id][14] = row.liftsMm[index]; }
  });
  return out;
}
