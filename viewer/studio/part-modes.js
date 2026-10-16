// 部品ごとの見え方（通常 / 透過 / 非表示）。three を import しない純関数だけ。
// 状態は store.state.partModes = { "<STL 名>": "ghost" | "hidden" }（通常の部品はキーを持たない）。
// 3D への反映は viewport.js、操作は part-menu.js と panels.js のパーツ一覧、保存は store.js。

export const PART_MODES = ["normal", "ghost", "hidden"];
export const PART_MODE_LABELS = { normal: "通常", ghost: "透過", hidden: "隠す" };

export const GHOST_OPACITY = 0.2;       // 透過した部品の不透明度（0.15〜0.25）
export const GHOST_EDGE_OPACITY = 0.3;  // 輪郭線の濃さ

export function partModesKey(model) { return `studio.partModes.${model}`; }

export function modeOf(modes, file) {
  const m = modes && modes[file];
  return m === "ghost" || m === "hidden" ? m : "normal";
}

// 保存データや外から来た値を { file: "ghost"|"hidden" } に直す。形が違えば空
export function normalizePartModes(raw) {
  const out = {};
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return out;
  for (const [file, m] of Object.entries(raw)) {
    if (m === "ghost" || m === "hidden") out[file] = m;
  }
  return out;
}

// 1 部品の状態を変えた新しいオブジェクトを返す（normal ならキーを消す）
export function withPartMode(modes, file, mode) {
  const out = normalizePartModes(modes);
  if (mode === "ghost" || mode === "hidden") out[file] = mode;
  else delete out[file];
  return out;
}

// 透過 ⇄ 通常（右クリックメニューの 1 キー切り替え用。隠れている部品は通常に戻す）
export function toggledGhost(mode) { return mode === "ghost" ? "normal" : "ghost"; }

// レイキャストの対象にする部品。隠した部品は常に除く。透過した部品は includeGhost のときだけ含める。
// メッシュは userData.partMode（viewport が書く）を見る。無ければ通常
export function pickTargets(meshes, { includeGhost = false } = {}) {
  return meshes.filter((m) => {
    const mode = (m.userData && m.userData.partMode) || "normal";
    if (mode === "hidden") return false;
    if (mode === "ghost") return includeGhost;
    return true;
  });
}

// 断面で切る部品。隠した部品は切らない（見えていない形の輪郭を出さない）
export function sliceTargets(meshes) {
  return meshes.filter((m) => ((m.userData && m.userData.partMode) || "normal") !== "hidden");
}

// 依頼 JSON に残す形。いま読み込んでいる STL のうち、通常ではないものだけ
export function partModesForRequest(modes, files) {
  const out = {};
  for (const file of files || []) {
    const m = modeOf(modes, file);
    if (m !== "normal") out[file] = m;
  }
  return out;
}

export function countPartModes(modes, files) {
  let ghost = 0, hidden = 0;
  for (const file of files || []) {
    const m = modeOf(modes, file);
    if (m === "ghost") ghost += 1;
    else if (m === "hidden") hidden += 1;
  }
  return { ghost, hidden };
}
