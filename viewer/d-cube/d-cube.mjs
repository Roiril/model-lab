import { createKinematics, createViewer, buildLegend, ALL, I4, mul, T } from "../lid-cube/lidcube.mjs";

export { createKinematics, createViewer, buildLegend, ALL, I4, mul, T };

export const MODEL = (typeof location !== "undefined" && new URLSearchParams(location.search).get("model")) || "mystery-box-sg92r-d1";
export const MODEL_IDS = Object.freeze(["mystery-box-sg92r-d1", "mystery-box-sg92r-d2"]);
export const REPORT_SECTIONS = Object.freeze([
  ["geometry", "形状"],
  ["motion", "動き"],
  ["assembly", "組み立て"],
  ["physics", "力と速度"],
  ["printing", "印刷"],
  ["notes", "注記"],
]);

const defaults = {
  "mystery-box-sg92r-d1": { title: "D1 隠し蝶番キューブ", summary: "80mm角・広い蓋" },
  "mystery-box-sg92r-d2": { title: "D2 隠し蝶番キューブ", summary: "80mm角・前側の蓋" },
};

export function isMissing(value) {
  if (value == null || value === "") return true;
  if (Array.isArray(value)) return value.length === 0;
  return typeof value === "object" && Object.keys(value).length === 0;
}

export function reportState(report = {}) {
  return REPORT_SECTIONS.map(([key, label]) => ({ key, label, value: report[key], verified: !isMissing(report[key]) }));
}

export function validateData(data) {
  if (!data || !Number.isFinite(data.q) || data.q <= 0) throw new Error("形状データの縮尺 q がありません");
  if (!data.meshes || typeof data.meshes !== "object") throw new Error("形状データ meshes がありません");
  const missing = ["box", "lid", "roof", "crank", "link", "pin", "clip", "speaker_clip", "ref_body", "ref_horn", "ref_wire", "ref_speaker"]
    .filter((name) => !data.meshes[name]);
  if (missing.length) throw new Error(`形状データが不足しています（${missing.join("、")}）`);
  const k = data.kin;
  if (!k || !Array.isArray(k.H) || !Array.isArray(k.O) || !Array.isArray(k.A0) || !Array.isArray(k.B0) || !Array.isArray(k.table) || k.table.length < 2) {
    throw new Error("4節リンクの運動データ kin が不足しています");
  }
  for (const key of ["a", "l", "alpha0", "mid_theta", "open_theta", "key_rel", "bend_deg"]) {
    if (!Number.isFinite(k[key])) throw new Error(`運動データ kin.${key} がありません`);
  }
  return data;
}

export async function loadData() {
  if (!MODEL_IDS.includes(MODEL)) throw new Error(`D1/D2のモデル名ではありません（${MODEL}）`);
  const response = await fetch(`assets/${MODEL}.json`);
  if (!response.ok) throw new Error(`assets/${MODEL}.json を読めません（${response.status}）`);
  const data = validateData(await response.json());
  applyMeta(data.meta);
  return data;
}

function applyMeta(meta = {}) {
  if (typeof document === "undefined") return;
  const fallback = defaults[MODEL] || defaults[MODEL_IDS[0]];
  const title = meta.title || fallback.title;
  const summary = meta.summary || fallback.summary;
  const page = document.body.dataset.page === "assembly" ? "組み立て" : "物理検証";
  document.title = `${title}の${page} · model-lab`;
  const head = document.querySelector(".workspace-model");
  if (head) {
    head.querySelector("strong").textContent = title;
    head.querySelector("small").textContent = summary;
  }
  const brand = document.querySelector(".workspace-brand");
  if (brand) brand.href = `/?model=${encodeURIComponent(MODEL)}`;
}

const n = (value, digits = 1) => !isMissing(value) && Number.isFinite(Number(value)) ? Number(value).toFixed(digits).replace(/\.0+$/, "") : null;
const result = (value) => value === true ? "確認" : value === false ? "要確認" : "未検証";
const supportLabel = (value) => value === true || value === "true" ? "使用" : value === false || value === "false" ? "不使用" : "未検証";
const count = (value) => Array.isArray(value) ? `${value.length}件` : !isMissing(value) && Number.isFinite(Number(value)) ? `${value}件` : "未検証";
const seconds = (value) => {
  if (isMissing(value) || !Number.isFinite(Number(value))) return "未検証";
  const minutes = Math.round(Number(value) / 60);
  return minutes >= 60 ? `${Math.floor(minutes / 60)}時間${minutes % 60}分` : `${minutes}分`;
};
const size = (value) => {
  const values = Array.isArray(value) ? value : value && typeof value === "object" ? Object.values(value) : [];
  return values.length && values.every((item) => Number.isFinite(Number(item))) ? `${values.map((item) => n(item)).join(" × ")} mm` : "未検証";
};
const row = (label, value) => ({ label, value: isMissing(value) ? "未検証" : String(value) });

export function reportSummary(report = {}) {
  const geometry = report.geometry;
  const exterior = geometry?.exterior;
  const topology = geometry?.topology;
  const topologyParts = topology && typeof topology === "object" ? Object.entries(topology).filter(([, value]) => value && typeof value === "object") : [];
  const badTopology = topologyParts.filter(([, value]) => value.ok === false).map(([name]) => name);
  const motion = report.motion;
  const assembly = report.assembly;
  const physics = report.physics;
  const plate = report.printing?.plate;
  const slice = report.printing?.slice;
  const slicedParts = slice?.parts && typeof slice.parts === "object" ? Object.values(slice.parts) : [];
  const unsupported = slicedParts.filter((part) => Number(part?.floating?.external_unsupported_mm) > 0).length;
  const noteRows = typeof report.notes === "string"
    ? [row("記録", report.notes)]
    : Array.isArray(report.notes)
      ? report.notes.slice(0, 6).map((value, index) => row(`注記 ${index + 1}`, value))
      : [];
  return [
    { key: "geometry", label: "形状", rows: geometry ? [
      row("外形", size(exterior?.size_mm)),
      row("外形の判定", result(exterior?.ok)),
      row("外形の検査", n(exterior?.checked, 0) != null ? `${exterior.passed ?? "—"} / ${exterior.checked}件` : "未検証"),
      row("外形の不一致", count(exterior?.failures)),
      row("メッシュ", topologyParts.length ? `${topologyParts.length}部品を検査` : "未検証"),
      row("非多様体など", topologyParts.length ? (badTopology.length ? `${badTopology.join("、")}を要確認` : "全対象で確認") : "未検証"),
      row("検査器の校正", result(geometry?.calibration?.ok)),
    ] : [] },
    { key: "motion", label: "動き", rows: motion ? [
      row("動作範囲の判定", result(motion.ok)),
      row("調べた姿勢", n(motion.samples, 0) != null ? `${motion.samples}姿勢` : "未検証"),
      row("角度の刻み", n(motion.step_deg) == null ? "未検証" : `${n(motion.step_deg)}°`),
      row("干渉を調べた組み合わせ", n(motion.intersection_tests, 0) != null ? `${motion.intersection_tests}組` : "未検証"),
      ...Object.entries(motion.min_clearance_mm || {}).map(([pair, gap]) => row(
        ({ "lid-roof": "蓋と固定天面の隙間", "link-lid": "リンクと蓋の隙間", "link-crank": "リンクとクランクの隙間" })[pair] || "隙間",
        n(gap, 2) == null ? "未検証" : `${n(gap, 2)} mm`)),
      row("不合格", count(motion.failures)),
    ] : [] },
    { key: "assembly", label: "組み立て", rows: assembly ? [
      row("組み立ての判定", result(assembly.ok)),
      row("検証状態", ({ verified: "計算上の経路を確認", failed: "修正が必要", partial: "一部を確認" })[assembly.status] || "未検証"),
      row("工程の検査", n(assembly.checked, 0) != null ? `${assembly.passed ?? "—"} / ${assembly.checked}件` : "未検証"),
      row("不合格", count(assembly.failures)),
      row("実物", assembly.physical_tested === true ? "確認済み" : "未確認"),
    ] : [] },
    { key: "physics", label: "力と速度", rows: physics ? [
      row("蓋の重さ", n(physics.mass?.lid_g, 1) == null ? "未検証" : `${n(physics.mass.lid_g, 1)} g`),
      row("ゆっくり動かす時間", n(physics.motion_time_s, 2) == null ? "未検証" : `${n(physics.motion_time_s, 2)} 秒`),
      row("重力を支える最大トルク", n(physics.static?.max_torque_Nm) == null ? "未検証" : `${n(physics.static.max_torque_Nm * 1000, 1)} mN·m`),
      row("停動トルクに対する割合", n(physics.static?.ratio_to_stall) == null ? "未検証" : `${n(physics.static.ratio_to_stall * 100, 1)}%`),
      row("ゆっくり動かした最大トルク", n(physics.eased?.peak_torque_Nm) == null ? "未検証" : `${n(physics.eased.peak_torque_Nm * 1000, 1)} mN·m`),
      row("閉じる端の速さ", n(physics.eased?.lid_impact_rad_s, 2) == null ? "未検証" : `${n(physics.eased.lid_impact_rad_s, 2)} rad/s`),
      row("トルク30%で開く", physics.weak_30pct ? result(physics.weak_30pct.opened) : "未検証"),
      row("速度計算の校正", physics.calib_noload_speed ? `${n(physics.calib_noload_speed.t_to_within_1deg, 3)}秒 / 公称${n(physics.calib_noload_speed.nominal, 3)}秒` : "未検証"),
    ] : [] },
    { key: "printing", label: "印刷", rows: report.printing ? [
      row("PLAプレート", plate?.PLA ? `${seconds(plate.PLA.prediction_s)}・${n(plate.PLA.weight_g, 1) ?? "—"} g` : "未検証"),
      row("PETGプレート", plate?.PETG ? `${seconds(plate.PETG.prediction_s)}・${n(plate.PETG.weight_g, 1) ?? "—"} g` : "未検証"),
      row("PLAのサポート", supportLabel(plate?.PLA?.support_used)),
      row("PETGのサポート", supportLabel(plate?.PETG?.support_used)),
      row("スライス検査の校正", result(slice?.calibration?.ok)),
      row("部品別スライス", slicedParts.length ? `${slicedParts.length}件` : "未検証"),
      row("支えを要確認の部品", slicedParts.length ? `${unsupported}件。内側の橋渡しを含む` : "未検証"),
    ] : [] },
    { key: "notes", label: "注記", rows: noteRows },
  ];
}

export function renderReport(container, report) {
  container.replaceChildren(...reportSummary(report).map((entry) => {
    const section = document.createElement("section");
    section.className = "report-section";
    const heading = document.createElement("h2");
    heading.textContent = entry.label;
    const list = document.createElement("dl");
    const rows = entry.rows.length ? entry.rows : [row("状態", "未検証")];
    for (const item of rows) {
      const dt = document.createElement("dt");
      dt.textContent = item.label;
      const dd = document.createElement("dd");
      dd.textContent = item.value;
      if (item.value === "未検証" || item.value === "未確認") dd.className = "unverified";
      list.append(dt, dd);
    }
    section.append(heading, list);
    return section;
  }));
}

export function groupedPose(base, names, dz) {
  return Object.fromEntries(names.map((name) => [name, mul(T(0, 0, dz), base[name] || I4())]));
}
