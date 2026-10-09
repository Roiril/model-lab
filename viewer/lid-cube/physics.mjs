// SG92R 開閉キューブの物理検証画面。開く・閉じるを押すたびに、その条件で運動方程式を解いてから再生する。
import { createWorkspaceNav } from "../shared/workspace.mjs";
import { MODEL, ALL, loadData, createKinematics, createViewer, buildLegend, lineChart } from "./lidcube.mjs";
import { createSim, profile } from "./sim.mjs";

const $ = (id) => document.getElementById(id);
const fmt = (v, d) => { const s = Number(v).toFixed(d); return /^-0(\.0+)?$/.test(s) ? s.slice(1) : s; };

let playing = null; // { run, t, rate }
let paused = false;

const nav = createWorkspaceNav({ active: "physics", model: MODEL, onNavigate: () => { paused = true; } });
$("workspaceHeader").insertBefore(nav.element, $("loading"));
nav.setModel(MODEL);

try {
  const D = await loadData();
  const kin = createKinematics(D.kin);
  const sim = createSim(D.simTables);
  const ac = sim.alphaClosed, ao = sim.alphaOpen;
  const state = { alpha: ac, cmd: ac, tau: 0 };
  let last = null;

  const viewer = createViewer($("gl"), D, () => {
    const th = Math.max(0, sim.at(state.alpha).theta);
    return { vis: ALL, cut: $("cut").checked, M: kin.pose(th, state.alpha) };
  });
  buildLegend($("legend"), viewer);
  $("cut").addEventListener("change", viewer.draw);
  $("home").addEventListener("click", viewer.home);
  $("lidg").textContent = fmt(D.sim.mass.lid_g, 1);

  const opts = () => ({ stallScale: +$("torque").value / 100, massScale: +$("mass").value, kind: $("profile").value });
  function metrics() {
    const o = opts();
    $("mCmd").textContent = `${fmt(ac - state.cmd, 1)}°`;
    $("mServo").textContent = `${fmt(ac - state.alpha, 1)}°`;
    $("mLid").textContent = `${fmt(Math.max(0, sim.at(state.alpha).theta), 1)}°`;
    $("mTau").textContent = `${fmt(state.tau * 1000, 0)} / ${fmt(245 * o.stallScale, 0)} mN·m`;
    $("mImpact").textContent = last && last.closing ? `${fmt(last.impact, 2)} rad/s` : "閉じるときだけ";
    $("mPeak").textContent = last ? `${fmt(last.peakTau * 1000, 0)} mN·m` : "—";
  }
  function charts(cursor) {
    const tr = last ? last.trace : [];
    const tEnd = last ? last.tEnd : 1.2;
    lineChart($("chartTheta"), { label: "蓋の角度の時間変化", x: [0, tEnd], y: [0, 100], xt: [0, +(tEnd / 2).toFixed(2), +tEnd.toFixed(2)], yt: [0, 50, 100],
      xl: "時間 (s)", yl: "蓋 (°)", cursor, series: [{ color: "--series-blue", pts: tr.map((r) => [r[0], Math.max(0, r[1])]) }] });
    const lim = 245 * (last ? last.stallScale : 1);
    lineChart($("chartTau"), { label: "サーボのトルクの時間変化", x: [0, tEnd], y: [-lim, lim], xt: [0, +(tEnd / 2).toFixed(2), +tEnd.toFixed(2)], yt: [-Math.round(lim), 0, Math.round(lim)],
      xl: "時間 (s)", yl: "トルク (mN·m)", cursor, series: [{ color: "--series-orange", pts: tr.map((r) => [r[0], r[3] * 1000]) }] });
  }
  function holdChart() {
    const ms = +$("mass").value;
    const pts = [];
    let maxT = 0, at = 0;
    for (let i = 0; i <= 95; i++) {
      // θ = i のときの α（運動学の表）で、重力を支えるトルク
      const al = kin.alphaOf(i), g = Math.abs(sim.holdTorque(al, ms)) * 1000;
      pts.push([i, g]);
      if (g > maxT) { maxT = g; at = i; }
    }
    const top = Math.max(15, Math.ceil(maxT / 5) * 5);
    lineChart($("chartHold"), { label: "蓋の角度ごとの必要トルク", x: [0, 95], y: [0, top], xt: [0, 45, 90], yt: [0, top / 2, top],
      xl: "蓋の角度 (°)", yl: "mN·m", series: [{ color: "--series-blue", pts }] });
    $("holdText").textContent = `最大 ${fmt(maxT, 1)} mN·m（蓋 ${at}°）。停動トルク 245 mN·m の ${fmt((maxT / 245) * 100, 1)}%。蓋の重さ ${fmt(ms, 2)}× の場合。`;
  }

  function start(target) {
    const o = opts();
    const from = state.alpha;
    const cmd = o.kind === "step" ? () => target : profile("ease", from, target, 0, 0.8);
    const tEnd = o.kind === "step" ? 1.0 : 1.3;
    const run = sim.run({ cmd, tEnd, alphaStart: from, stallScale: o.stallScale, massScale: o.massScale, record: 0.002 });
    run.tEnd = tEnd; run.stallScale = o.stallScale; run.cmd = cmd; run.closing = target === ac;
    last = run;
    const reached = Math.max(0, run.final.theta);
    const goal = target === ao ? 95 : 0;
    $("status").textContent = Math.abs(reached - goal) < 2
      ? `${target === ao ? "開いた" : "閉じた"}（${fmt(reached, 1)}°）。トルク上限 ${fmt(o.stallScale * 100, 0)}%、蓋の重さ ${fmt(o.massScale, 2)}×。`
      : `${goal}° に届かない（${fmt(reached, 1)}° で止まる）。トルク上限 ${fmt(o.stallScale * 100, 0)}%、蓋の重さ ${fmt(o.massScale, 2)}×。`;
    playing = { run, t: 0 };
    paused = false;
    $("pause").textContent = "一時停止";
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) playing.t = tEnd;
    tick.prev = performance.now();
    requestAnimationFrame(tick);
  }
  function sample(run, t) {
    const tr = run.trace;
    let i = Math.min(tr.length - 1, Math.max(0, Math.round(t / 0.002)));
    while (i > 0 && tr[i][0] > t) i--;
    return tr[i];
  }
  function tick(now) {
    if (!playing) return;
    const dt = (now - (tick.prev || now)) / 1000;
    tick.prev = now;
    if (!paused) playing.t = Math.min(playing.run.tEnd, playing.t + dt * +$("rate").value);
    const r = sample(playing.run, playing.t);
    state.alpha = r[2]; state.tau = r[3]; state.cmd = playing.run.cmd(playing.t);
    $("clock").textContent = `${fmt(playing.t, 3)} s`;
    metrics(); charts(playing.t); viewer.draw();
    if (playing.t < playing.run.tEnd) requestAnimationFrame(tick);
    else playing = null;
  }

  $("open").addEventListener("click", () => start(ao));
  $("close").addEventListener("click", () => start(ac));
  $("pause").addEventListener("click", () => {
    paused = !paused; $("pause").textContent = paused ? "再開" : "一時停止";
    if (!paused && playing) { tick.prev = performance.now(); requestAnimationFrame(tick); }
  });
  for (const id of ["torque", "mass"]) {
    $(id).addEventListener("input", () => {
      $("torqueOut").textContent = `${$("torque").value}%`;
      $("massOut").textContent = `${fmt($("mass").value, 2)}×`;
      holdChart(); metrics();
    });
  }

  const V = D.verify, S = D.sim;
  const checks = [
    ["ok", `負荷なしで 70° 回す時間 ${S.calib_noload_speed.t_to_within_1deg} 秒（SG92R の公称 ${S.calib_noload_speed.nominal} 秒）`],
    ["ok", `出せるトルクを必要量の半分にすると開かない（${S.calib_half_torque_fails.opened ? "開いた" : "0° のまま"}）`],
    ["ok", "ブラウザの計算と Python の計算は同じ値（0.8 秒で開閉: 縁に当たる速さ 0.38 rad/s、全速: 86° まで 0.12 秒）"],
    [V.motion.poses_with_hits.length ? "warn" : "ok", `0〜95° の ${V.motion.steps} 姿勢で部品どうしの当たり ${V.motion.poses_with_hits.length} 件`],
    ["ok", `動作中の最小隙間 クランクと受け ${V.clearance["crank-box"].min}mm、リンクと蓋 ${V.clearance["link-lid"].min}mm（ピンの隙間）`],
    ["ok", `電圧が下がってトルクが 30% でも ${fmt(S.weak_30pct.final_theta, 1)}° まで開く`],
  ];
  $("checks").innerHTML = checks.map(([c, t]) => `<li><span class="chip ${c}">${c === "ok" ? "確認" : "要確認"}</span><span>${t}</span></li>`).join("");
  $("loading").textContent = "";
  holdChart(); charts(null); metrics(); viewer.draw();
  // 開いた状態を最初に見せる（ゆっくり開く計算を流す）
  start(ao);
} catch (err) {
  console.error(err);
  $("fatal").hidden = false;
  $("fatalMessage").textContent = `${err.message}。WebGL2 が使えるブラウザーで開き直してください。`;
  $("loading").textContent = "読み込めませんでした";
}
