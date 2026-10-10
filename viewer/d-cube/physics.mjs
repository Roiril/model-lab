import { createWorkspaceNav } from "../shared/workspace.mjs";
import { MODEL, ALL, loadData, createKinematics, createViewer, buildLegend, renderReport } from "./d-cube.mjs";

const $ = (id) => document.getElementById(id);
const fmt = (value, digits = 1) => Number(value).toFixed(digits).replace(/^-0(\.0+)?$/, (_, zeros = "") => `0${zeros}`);
let animation = 0;
const nav = createWorkspaceNav({ active: "physics", model: MODEL, onNavigate: () => cancelAnimationFrame(animation) });
$("workspaceHeader").insertBefore(nav.element, $("loading"));
nav.setModel(MODEL);

try {
  const data = await loadData();
  const kin = createKinematics(data.kin);
  const open = data.kin.open_theta;
  const initial = Number(new URL(location.href).searchParams.get("theta"));
  const state = { theta: Number.isFinite(initial) ? Math.max(0, Math.min(open, initial)) : 0 };
  $("theta").max = String(open);
  $("mRange").textContent = `0〜${fmt(open, 0)}°`;
  const viewer = createViewer($("gl"), data, () => ({ vis: ALL, cut: $("cut").checked, M: kin.pose(state.theta) }));
  buildLegend($("legend"), viewer);
  renderReport($("report"), data.report);

  function show(theta, message, writeUrl = true) {
    state.theta = Math.max(0, Math.min(open, theta));
    const alpha = kin.alphaOf(state.theta);
    $("theta").value = String(state.theta);
    $("thetaOut").textContent = `${fmt(state.theta)}°`;
    $("mTheta").textContent = `${fmt(state.theta)}°`;
    $("mAlpha").textContent = `${fmt(alpha)}°`;
    if (message) $("status").textContent = message;
    if (writeUrl) {
      const url = new URL(location.href);
      url.searchParams.set("theta", fmt(state.theta));
      history.replaceState(history.state, "", url);
    }
    viewer.draw();
  }
  function stop() {
    if (animation) cancelAnimationFrame(animation);
    animation = 0;
    $("replay").textContent = "開閉を再生";
  }
  function replay() {
    if (animation) { stop(); return; }
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      show(open, "動きを省略して開いた姿勢を表示しました。");
      return;
    }
    const started = performance.now();
    $("replay").textContent = "止める";
    const frame = (now) => {
      const elapsed = (now - started) / 1000;
      const phase = Math.min(1, elapsed / (2 * (data.report.physics?.motion_time_s || 1.2)));
      const wave = phase < 0.5 ? phase * 2 : (1 - phase) * 2;
      const eased = wave * wave * (3 - 2 * wave);
      show(open * eased, phase < 0.5 ? "開いています。" : "閉じています。", false);
      if (phase < 1) animation = requestAnimationFrame(frame);
      else { stop(); show(0, "開閉の再生が終わりました。"); }
    };
    animation = requestAnimationFrame(frame);
  }
  $("theta").addEventListener("input", () => { stop(); show(+$("theta").value, "スライダーで姿勢を動かしています。"); });
  $("closed").addEventListener("click", () => { stop(); show(0, "閉じた姿勢です。"); });
  $("opened").addEventListener("click", () => { stop(); show(open, "開いた姿勢です。"); });
  $("replay").addEventListener("click", replay);
  $("cut").addEventListener("change", viewer.draw);
  $("home").addEventListener("click", viewer.home);
  $("loading").textContent = "";
  show(state.theta, state.theta === 0 ? "閉じた姿勢です。"
    : state.theta === open ? "開いた姿勢です。" : "指定された角度の姿勢です。");
} catch (error) {
  console.error(error);
  $("fatal").hidden = false;
  $("fatalMessage").textContent = `${error.message}。WebGL2が使えるブラウザーで開き直してください。`;
  $("loading").textContent = "読み込めませんでした";
}
