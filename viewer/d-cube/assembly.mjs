import { createWorkspaceNav } from "../shared/workspace.mjs";
import { MODEL, ALL, loadData, createKinematics, createViewer, buildLegend, renderReport, groupedPose, I4, mul, T } from "./d-cube.mjs";

const $ = (id) => document.getElementById(id);
const visible = (...names) => new Set(names);
const ease = (p) => p * p * (3 - 2 * p);
let stop = () => {};
const nav = createWorkspaceNav({ active: "assembly", model: MODEL, onNavigate: () => stop() });
$("workspaceHeader").insertBefore(nav.element, $("loading"));
nav.setModel(MODEL);

try {
  const data = await loadData();
  const kin = createKinematics(data.kin);
  const middle = data.kin.mid_theta;
  const open = data.kin.open_theta;
  const base = kin.pose(open);
  const unit = ["lid", "crank", "link", "ref_horn", "ref_body", "ref_wire", "pin", "roof"];
  const fixed = ["box", "clip", "speaker_clip", "ref_speaker"];
  const lifted = (dz) => ({ ...groupedPose(base, unit, dz), ref_body: T(0, 0, dz), ref_wire: T(0, 0, dz), pin: T(0, 0, dz), roof: T(0, 0, dz) });
  const full = visible(...ALL);
  const steps = [
    {
      title: "箱の外で蓋とリンクを組む。天面と蝶番ピンを合わせる",
      result: "先に単独の蓋へリンクを組みます。その後65°開いた姿勢で固定天面を合わせます。ピンは右から通します。実物の固さは未確認です。",
      pose(p) {
        const z = 52;
        return { vis: visible("box", "roof", "lid", "pin", "crank", "link"), M: {
          roof: T(0, 0, z + 14 * (1 - p)),
          pin: T(60 * (1 - p), 0, z),
          lid: mul(T(-18 * (1 - p), 0, z), base.lid),
          crank: mul(T(28 * (1 - p), 0, z), base.crank),
          link: mul(T(18 * (1 - p), 0, z), base.link),
        } };
      },
    },
    {
      title: "蓋を65°開く。SG92Rを90°に合わせて取り付ける",
      result: "付属ホーンの歯の刻みでずれる分はソフトの角度で合わせます。実物の保持力は未確認です。",
      pose(p) {
        const M = lifted(52);
        M.ref_body = T(-18 * (1 - p), 0, 52);
        M.ref_wire = T(-18 * (1 - p), 0, 52);
        return { vis: visible("box", ...unit), M };
      },
    },
    {
      title: "内側の爪を押す。一式を箱へ下ろして留める",
      result: "爪を内側へ1.12mm押して下ろします。着座してから爪を戻します。配線と指の収まりは実物で確認します。",
      pose(p) { return { vis: visible(...[...ALL].filter((name) => name !== "clip")), M: { ...base, ...groupedPose({ ...base, ref_body: I4(), ref_wire: I4(), pin: I4(), roof: I4() }, unit, 80 * (1 - p)) } }; },
    },
    {
      title: "蓋を開いたままサーボ押さえを入れる",
      result: "配置の説明です。押し込み力と繰り返し使ったときの保持力は実物で確かめます。",
      pose(p) {
        return { vis: full, M: { ...base, clip: T(0, 0, 24 * (1 - p)) } };
      },
    },
    {
      title: "ゆっくり閉じて開く。配線を挟まないことを確かめる",
      result: "閉位置は1°ずつ探します。縁に触れた先へ押し込まない設定にします。実物の動作は未確認です。",
      pose(p) { return { vis: full, M: kin.pose(open * (1 - Math.sin(Math.PI * p))) }; },
    },
  ];
  renderReport($("report"), data.report);
  const url = new URL(location.href);
  let index = Math.min(steps.length - 1, Math.max(0, (parseInt(url.searchParams.get("step"), 10) || 1) - 1));
  let progress = 1;
  const viewer = createViewer($("gl"), { ...data, view: { ...data.view, target: [0, 0, 108], dist: 460 } },
    () => ({ ...steps[index].pose(ease(progress)), cut: $("cut").checked }));
  buildLegend($("legend"), viewer);
  $("cut").addEventListener("change", viewer.draw);
  $("home").addEventListener("click", viewer.home);

  const list = $("steps");
  list.replaceChildren(...steps.map((step, i) => {
    const li = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    const number = document.createElement("span");
    number.className = "n";
    number.textContent = String(i + 1);
    const text = document.createElement("span");
    text.textContent = step.title;
    button.append(number, text);
    button.addEventListener("click", () => { stop(); show(i, 1); });
    li.append(button);
    return li;
  }));
  function show(next, p) {
    index = next;
    progress = p;
    list.querySelectorAll("button").forEach((button, i) => i === index ? button.setAttribute("aria-current", "step") : button.removeAttribute("aria-current"));
    $("stepnow").replaceChildren();
    const title = document.createElement("div");
    const number = document.createElement("span");
    number.className = "n";
    number.textContent = `工程 ${index + 1} / ${steps.length}`;
    title.append(number, `　${steps[index].title}`);
    const result = document.createElement("div");
    result.className = "res";
    result.textContent = steps[index].result;
    $("stepnow").append(title, result);
    $("prev").disabled = index === 0;
    $("next").disabled = index === steps.length - 1;
    const nextUrl = new URL(location.href);
    nextUrl.searchParams.set("step", String(index + 1));
    history.replaceState(history.state, "", nextUrl);
    viewer.draw();
  }
  let frame = 0;
  let allPlaying = false;
  function play(i, done) {
    cancelAnimationFrame(frame);
    show(i, 0);
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) { show(i, 1); done?.(); return; }
    const duration = 1800 / +$("speed").value;
    const started = performance.now();
    const tick = (now) => {
      progress = Math.min(1, (now - started) / duration);
      viewer.draw();
      if (progress < 1) frame = requestAnimationFrame(tick);
      else done?.();
    };
    frame = requestAnimationFrame(tick);
  }
  stop = () => { cancelAnimationFrame(frame); frame = 0; allPlaying = false; $("all").textContent = "順に再生"; };
  $("prev").addEventListener("click", () => { stop(); play(index - 1); });
  $("next").addEventListener("click", () => { stop(); play(index + 1); });
  $("play").addEventListener("click", () => { stop(); play(index); });
  $("all").addEventListener("click", () => {
    if (allPlaying) { stop(); return; }
    allPlaying = true;
    $("all").textContent = "止める";
    const chain = (i) => play(i, () => {
      if (allPlaying && i + 1 < steps.length) setTimeout(() => allPlaying && chain(i + 1), 300);
      else stop();
    });
    chain(0);
  });
  $("loading").textContent = "";
  show(index, 1);
} catch (error) {
  console.error(error);
  $("fatal").hidden = false;
  $("fatalMessage").textContent = `${error.message}。WebGL2が使えるブラウザーで開き直してください。`;
  $("loading").textContent = "読み込めませんでした";
}
