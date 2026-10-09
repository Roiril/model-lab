// サーボで蓋を開くモデルの組み立て画面（?model= で選ぶ）。工程ごとの部品の動きは models/<モデル>/verify.py の経路と同じ。
import { createWorkspaceNav } from "../shared/workspace.mjs";
import { MODEL, ALL, loadData, createKinematics, createViewer, buildLegend, mul, T } from "./lidcube.mjs";

const $ = (id) => document.getElementById(id);
const V = (...k) => new Set(k);
const ease = (p) => p * p * (3 - 2 * p);

let stop = () => {};
const nav = createWorkspaceNav({ active: "assembly", model: MODEL, onNavigate: () => stop() });
$("workspaceHeader").insertBefore(nav.element, $("loading"));
nav.setModel(MODEL);

try {
  const D = await loadData();
  const k = createKinematics(D.kin);
  const A = D.verify.assembly;
  // 工程の動かし方（mm・度）。値はモデルの verify.py の経路と同じ（export_web.py が書く）
  const G = D.assembly;
  const OPEN = D.kin.open_theta;
  const AM = k.alphaOf(D.kin.mid_theta), TM = D.kin.mid_theta;
  const BACK = G.lid_back_deg, UP = G.unit_lift_mm;
  const UNIT = ["ref_body", "ref_wire", "ref_horn", "crank"];
  // 任意のスピーカーがあるモデルは、最初に箱へ貼って、そのあとずっと見せる
  const SPK = D.meshes.ref_speaker ? ["ref_speaker"] : [];
  const above = (dz, extra = {}) => {
    const u = T(0, 0, dz);
    return { ref_body: u, ref_wire: u, ref_horn: mul(u, k.poseCrank(AM)), crank: mul(u, k.poseCrank(AM)), ...extra };
  };
  const relOp = ((k.linkAng(AM, TM) - AM + 540) % 360) - 180;
  const STEPS = [
    ...(SPK.length ? [{ t: G.speaker_step, r: G.speaker_check,
      f: (p) => ({ vis: V("box", ...SPK), M: { ref_speaker: T(-G.speaker_travel_mm * (1 - p), 0, 0) } }) }] : []),
    { t: "蓋を箱に載せ、節をそろえる", r: `蓋の節（中央）が箱の節（両端）の間に ${G.knuckle_gap_mm}mm ずつの隙間で入る`,
      f: (p) => ({ vis: V("box", ...SPK, "lid"), M: { lid: T(0, 0, 30 * (1 - p)) } }) },
    { t: "蝶番ピンを右側面から差し込む。奥に当たると端が角の丸みと面一になる",
      r: `当たるのは先端の割りと左の止まり穴だけ（食い込み ${A.A_hinge_pin_insert.worst["pin-box"].depth}mm＝設計した圧入）`,
      f: (p) => ({ vis: V("box", ...SPK, "lid", "pin"), M: { pin: T(G.pin_travel_mm * (1 - p), 0, 0) } }) },
    { t: "箱の外で、90° にしたサーボへホーンを押し込み、クランクをかぶせる", r: `クランクを ${G.crank_push_mm}mm 手前から押し込む経路で当たりなし`,
      f: (p) => ({ vis: V("box", ...SPK, "lid", "pin", ...UNIT), M: above(UP, { crank: mul(T(0, 0, UP), mul(T((G.crank_push_mm + 6) * (1 - p), 0, 0), k.poseCrank(AM))) }) }) },
    { t: "リンクの穴の切り欠きをピン A の爪に合わせて差し、回して戻す", r: "差す・回すとも当たりなし。動作範囲では 1mm 引くと爪に当たる（抜けない）",
      f: (p) => {
        let rel = D.kin.key_rel, dx = 0;
        if (p < 0.5) dx = 12 * (1 - p / 0.5); else rel = D.kin.key_rel + (relOp - D.kin.key_rel) * ((p - 0.5) / 0.5);
        return { vis: V("box", ...SPK, "lid", "pin", ...UNIT, "link"), M: above(UP, { link: mul(T(0, 0, UP), mul(T(dx, 0, 0), k.poseLinkAt(AM, AM + rel))) }) };
      } },
    { t: "蓋を後ろへ倒しておく", r: `蓋だけなら ${D.verify.free_open}° まで箱に当たらずに開く`,
      f: (p) => ({ vis: V("box", ...SPK, "lid", "pin", ...UNIT, "link"), M: above(UP, { lid: k.poseLid(BACK * p), link: mul(T(0, 0, UP), k.poseLink(AM, TM)) }) }) },
    { t: "サーボ一式を上から台へ下ろす。クランクの軸が受けの U 溝に入る。配線は台の端の切り欠きへ", r: `${G.lower_from_mm}mm 上から下ろす経路で当たりなし（蓋は ${BACK}° に倒した状態）`,
      f: (p) => { const dz = UP * (1 - p); return { vis: V("box", ...SPK, "lid", "pin", ...UNIT, "link"), M: above(dz, { lid: k.poseLid(BACK), link: mul(T(0, 0, dz), k.poseLink(AM, TM)) }) }; } },
    { t: "押さえクリップを上から押し込み、爪を台の溝に掛ける", r: `爪が台の角を乗り越えるときの食い込み ${A.E_clip_press.worst["clip-box"].depth}mm（脚のたわみ）。ほかの当たりなし`,
      f: (p) => ({ vis: ALL, M: above(0, { clip: T(0, 0, (G.clip_from_mm + 3) * (1 - p)), lid: k.poseLid(BACK), link: k.poseLink(AM, TM) }) }) },
    { t: `リンクの先をサーボ側へ ${A.F_lid_down_with_link_bent.b_end_shift_mm}mm 曲げたまま蓋を下ろし、穴が合ったら離す`, r: `蓋を下ろす間の当たりなし。曲げのひずみ ${A.F_link_bend_strain_pct}%。離すとピン B が耳の穴に入る`,
      f: (p) => {
        let th = TM, b = 1;
        if (p < 0.7) th = BACK + (TM - BACK) * (p / 0.7); else b = 1 - (p - 0.7) / 0.3;
        return { vis: ALL, M: above(0, { lid: k.poseLid(th), link: mul(k.bend(AM, TM, b), k.poseLink(AM, TM)) }) };
      } },
    { t: "サーボを動かして閉じる（角度は右の手順で決める）", r: `0〜${OPEN}° の ${D.verify.motion.steps} 姿勢で部品どうしの当たり ${D.verify.motion.poses_with_hits.length} 件`,
      f: (p) => ({ vis: ALL, M: k.pose(TM * (1 - p)) }) },
  ];
  $("eyebrow").textContent = D.meta.eyebrow;
  $("howto").replaceChildren(...D.meta.howto.map((s) => Object.assign(document.createElement("li"), { textContent: s })));
  $("untested").textContent = D.meta.untested;

  const url = new URL(location.href);
  let idx = Math.min(STEPS.length - 1, Math.max(0, (parseInt(url.searchParams.get("step"), 10) || 1) - 1));
  let prog = 1;
  const viewer = createViewer($("gl"), D, () => ({ ...STEPS[idx].f(ease(prog)), cut: $("cut").checked }));
  buildLegend($("legend"), viewer);
  $("cut").addEventListener("change", viewer.draw);
  $("home").addEventListener("click", viewer.home);

  const list = $("steps");
  list.replaceChildren(...STEPS.map((s, i) => {
    const li = document.createElement("li");
    const b = document.createElement("button");
    b.type = "button";
    b.innerHTML = `<span class="n">${i + 1}</span><span>${s.t}</span>`;
    b.addEventListener("click", () => { stop(); show(i, 1); });
    li.append(b);
    return li;
  }));
  function show(i, p) {
    idx = i; prog = p;
    list.querySelectorAll("button").forEach((b, j) => (j === idx ? b.setAttribute("aria-current", "step") : b.removeAttribute("aria-current")));
    $("stepnow").innerHTML = `<div><span class="n">工程 ${idx + 1} / ${STEPS.length}</span>　${STEPS[idx].t}</div><div class="res">検証: ${STEPS[idx].r}</div>`;
    $("prev").disabled = idx === 0; $("next").disabled = idx === STEPS.length - 1;
    const u = new URL(location.href); u.searchParams.set("step", idx + 1); history.replaceState(history.state, "", u);
    viewer.draw();
  }
  let anim = 0;
  function play(i, done) {
    cancelAnimationFrame(anim);
    show(i, 0);
    const dur = 1800 / +$("speed").value, t0 = performance.now();
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const step = (now) => {
      prog = reduce ? 1 : Math.min(1, (now - t0) / dur);
      viewer.draw();
      if (prog < 1) anim = requestAnimationFrame(step); else if (done) done();
    };
    anim = requestAnimationFrame(step);
  }
  stop = () => { cancelAnimationFrame(anim); $("all").textContent = "全部を順に再生"; allOn = false; };
  let allOn = false;
  $("prev").addEventListener("click", () => { stop(); play(idx - 1); });
  $("next").addEventListener("click", () => { stop(); play(idx + 1); });
  $("play").addEventListener("click", () => { stop(); play(idx); });
  $("all").addEventListener("click", () => {
    if (allOn) { stop(); return; }
    allOn = true; $("all").textContent = "止める";
    const chain = (i) => play(i, () => { if (allOn && i + 1 < STEPS.length) setTimeout(() => allOn && chain(i + 1), 400); else stop(); });
    chain(0);
  });

  const empty = (w) => !w || Object.keys(w).length === 0;
  const rows = [
    ...(SPK.length ? [["スピーカーを貼る", `${G.speaker_travel_mm}mm 左から`, G.speaker_result]] : []),
    ["蝶番ピンを差す", `右側面から ${G.pin_path_mm}mm`, `先端の圧入 ${A.A_hinge_pin_insert.worst["pin-box"].depth}mm のみ`],
    ["クランクをホーンへ", `${G.crank_push_mm}mm 手前から`, empty(A.B_crank_onto_horn.worst) ? "当たりなし" : "当たりあり"],
    ["リンクをピン A へ", "鍵溝の角度で差し、回す", empty(A.C1_link_push_at_key.worst) && empty(A.C2_link_turn_to_operating.worst) ? "当たりなし" : "当たりあり"],
    ["抜け止め", "動作範囲の 3 姿勢で 1mm 引く", A.C3_bayonet_lock.operating.every((r) => r.pulled_1mm_hits > 0) ? "3 姿勢とも爪に当たる" : "抜ける姿勢あり"],
    ["サーボ一式を下ろす", `${G.lower_from_mm}mm 上から`, empty(A.D_servo_unit_lower.worst) ? "当たりなし" : "当たりあり"],
    ["クリップを押し込む", `${G.clip_from_mm}mm 上から`, `爪の食い込み ${A.E_clip_press.worst["clip-box"].depth}mm のみ`],
    ["ピン B を入れる", `蓋 ${BACK}° → ${TM}°`, empty(A.F_lid_down_with_link_bent.hits) ? `当たりなし（ひずみ ${A.F_link_bend_strain_pct}%）` : "当たりあり"],
  ];
  $("summary").innerHTML = "<thead><tr><th>工程</th><th>動かした範囲</th><th>結果</th></tr></thead><tbody>" +
    rows.map((r) => `<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td></tr>`).join("") + "</tbody>";
  $("loading").textContent = "";
  show(idx, 1);
} catch (err) {
  console.error(err);
  $("fatal").hidden = false;
  $("fatalMessage").textContent = `${err.message}。WebGL2 が使えるブラウザーで開き直してください。`;
  $("loading").textContent = "読み込めませんでした";
}
