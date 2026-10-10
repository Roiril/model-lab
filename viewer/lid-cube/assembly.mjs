// サーボで蓋を開くモデルの組み立て画面（?model= で選ぶ）。工程ごとの部品の動きは models/<モデル>/verify.py の経路と同じ。
import { createWorkspaceNav } from "../shared/workspace.mjs";
import { MODEL, ALL, loadData, createKinematics, createViewer, buildLegend, mul, T, RX, I4 } from "./lidcube.mjs";

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
  const hingeCheck = A.E_hinge_pin_insert || A.A_hinge_pin_insert;
  // 工程の動かし方（mm・度）。値はモデルの verify.py の経路と同じ（export_web.py が書く）
  const G = D.assembly;
  const clipDepth = A.E_clip_press.worst["clip-box"].depth;
  const servoSpring = D.servo_fit?.spring;
  const clipCheck = servoSpring
    ? `爪の押込み ${clipDepth}mm（脚の推定ひずみ ${A.clip_snap_strain_pct}%）。長手押さえの押込み ${servoSpring.intent_mesh_mm}mm（推定ひずみ ${servoSpring.nominal_strain_pct}%）。保持力は実物で確認`
    : `爪の食い込み ${clipDepth}mm のみ`;
  const lidPlaceCheck = A.G_lid_place_after_servo || { worst: {} };
  const OPEN = D.kin.open_theta;
  const AM = k.alphaOf(D.kin.mid_theta), TM = D.kin.mid_theta;
  const BACK = G.lid_back_deg, UP = G.unit_lift_mm;
  const ASSEMBLED = new Set([...ALL].filter((name) => name !== "roof"));
  const UNIT = ["ref_body", "ref_wire", "ref_horn", "crank"];
  const HINGED = G.unit_first ? [] : ["lid", "pin"];
  // 任意のスピーカーがあるモデルは、最初に箱へ入れて、そのあとずっと見せる。
  const SPK = ["ref_speaker", "speaker_clip"].filter((name) => D.meshes[name]);
  const above = (dz, extra = {}) => {
    const u = T(0, 0, dz);
    return { ref_body: u, ref_wire: u, ref_horn: mul(u, k.poseCrank(AM)), crank: mul(u, k.poseCrank(AM)), ...extra };
  };
  const relOp = ((k.linkAng(AM, TM) - AM + 540) % 360) - 180;
  const speakerStep = SPK.length ? { t: G.speaker_step, r: G.speaker_check,
    f: (p) => {
      const split = 0.55;
      const speakerZ = p < split ? G.speaker_travel_mm * (1 - p / split) : 0;
      const clipZ = p < split ? G.speaker_travel_mm : G.speaker_travel_mm * (1 - (p - split) / (1 - split));
      return { vis: V("box", ...SPK), M: { ref_speaker: T(0, 0, speakerZ), speaker_clip: T(0, 0, clipZ) } };
    } } : null;
  const lidFirst = { t: "蓋を箱に載せ、節をそろえる", r: `蓋の節（中央）が箱の節（両端）の間に ${G.knuckle_gap_mm}mm ずつの隙間で入る`,
    f: (p) => ({ vis: V("box", ...SPK, "lid"), M: { lid: T(0, 0, 30 * (1 - p)) } }) };
  const hingePin = { t: G.pin_flat_ends
      ? "蝶番ピンを右から差し込む。両端は平らで、抜くときは左から押して右端をつまむ"
      : G.pin_through
      ? "蝶番ピンを右から差し込む。両端は貫通しており、抜くときは左から押して右端をつまむ"
      : "蝶番ピンを右側面から差し込む。奥に当たると端が角の丸みと面一になる",
    r: G.pin_flat_ends
      ? (hingeCheck.note || `右から ${G.pin_path_mm}mm 通す経路を検証`)
      : G.pin_through
      ? `右から ${G.pin_path_mm}mm 通す。先端の割りが穴に ${hingeCheck.worst["pin-box"].depth}mm 食い込んで留まる`
      : `当たるのは先端の割りと左の止まり穴だけ（食い込み ${hingeCheck.worst["pin-box"].depth}mm＝設計した圧入）`,
    f: (p) => ({ vis: V("box", ...SPK, "lid", "pin"), M: { pin: T(G.pin_travel_mm * (1 - p), 0, 0) } }) };
  const hornNote = G.horn_orientation_note ? `。${G.horn_orientation_note}` : "";
  const hornCheck = D.horn_orientation?.ok ? "。逆向きと、外形を合わせた逆向きは奥まで入らない" : "";
  const buildUnit = { t: `箱の外で、90° にしたサーボへホーンを押し込み、クランクをかぶせる${hornNote}`, r: `クランクを ${G.crank_push_mm}mm 手前から押し込む経路で当たりなし${hornCheck}`,
    f: (p) => ({ vis: V("box", ...SPK, ...HINGED, ...UNIT), M: above(UP, { crank: mul(T(0, 0, UP), mul(T((G.crank_push_mm + 6) * (1 - p), 0, 0), k.poseCrank(AM))) }) }) };
  const attachLink = { t: "リンクの穴の切り欠きをピン A の爪に合わせて差し、回して戻す",
    r: `差す・回すとも当たりなし。動作範囲では ${A.C3_bayonet_lock.pull_check_mm ?? 1}mm 引くと爪に当たる（抜けない）`,
    f: (p) => {
      let rel = D.kin.key_rel, dx = 0;
      if (p < 0.5) dx = 12 * (1 - p / 0.5); else rel = D.kin.key_rel + (relOp - D.kin.key_rel) * ((p - 0.5) / 0.5);
      return { vis: V("box", ...SPK, ...HINGED, ...UNIT, "link"), M: above(UP, { link: mul(T(0, 0, UP), mul(T(dx, 0, 0), k.poseLinkAt(AM, AM + rel))) }) };
    } };
  const lidBack = { t: "蓋を後ろへ倒しておく", r: `蓋だけなら ${D.verify.free_open}° まで箱に当たらずに開く`,
    f: (p) => ({ vis: V("box", ...SPK, "lid", "pin", ...UNIT, "link"), M: above(UP, { lid: k.poseLid(BACK * p), link: mul(T(0, 0, UP), k.poseLink(AM, TM)) }) }) };
  const lowerUnit = { t: G.unit_first
      ? "サーボ一式を上から台へ下ろす。クランクの軸を受けへ入れ、配線を台の切り欠きへ通す"
      : "サーボ一式を上から台へ下ろす。クランクの軸が受けの U 溝に入る。配線は台の端の切り欠きへ",
    r: G.unit_first ? `${G.lower_from_mm}mm 上から下ろす経路を検証` : `${G.lower_from_mm}mm 上から下ろす経路で当たりなし（蓋は ${BACK}° に倒した状態）`,
    f: (p) => { const dz = UP * (1 - p); return { vis: V("box", ...SPK, ...HINGED, ...UNIT, "link"), M: above(dz, {
      ...(G.unit_first ? {} : { lid: k.poseLid(BACK) }), link: mul(T(0, 0, dz), k.poseLink(AM, TM)) }) }; } };
  const servoClip = { t: G.unit_first ? "サーボ押さえを上から押し込み、爪を台の溝に掛ける" : "押さえクリップを上から押し込み、爪を台の溝に掛ける", r: servoSpring ? clipCheck : `爪が台の角を乗り越えるときの食い込み ${clipDepth}mm（脚のたわみ）。ほかの当たりなし`,
    f: (p) => ({ vis: V("box", ...SPK, ...HINGED, ...UNIT, "link", "clip"), M: above(0, {
      clip: T(0, 0, (G.clip_from_mm + 3) * (1 - p)), ...(G.unit_first ? {} : { lid: k.poseLid(BACK) }), link: k.poseLink(AM, TM) }) }) };
  const placeLid = { t: `蓋を ${BACK}° 開いた姿勢にし、箱の ${G.lid_place_from_mm}mm 上から節がそろうまで下ろす`,
    r: `${G.lid_place_from_mm}mm 上から下ろす経路で当たり ${Object.keys(lidPlaceCheck.worst).length} 件`,
    f: (p) => ({ vis: V("box", ...SPK, ...UNIT, "link", "clip", "lid"),
      M: above(0, { lid: mul(T(0, 0, G.lid_place_from_mm * (1 - p)), k.poseLid(BACK)), link: k.poseLink(AM, TM) }) }) };
  const linkB = { t: `リンクの先をサーボ側へ ${A.F_lid_down_with_link_bent?.b_end_shift_mm}mm 曲げ、蓋を ${BACK}° から ${TM}° へ下ろす。穴が合ったら離す`,
    r: `蓋を下ろす間の当たりなし。曲げのひずみ ${A.F_link_bend_strain_pct}%。離すとピン B が耳の穴に入る`,
    f: (p) => {
      let th = TM, bend = 1;
      if (p < 0.7) th = BACK + (TM - BACK) * (p / 0.7); else bend = 1 - (p - 0.7) / 0.3;
      if (D.meshes.link_bend_0) {
        return { vis: ASSEMBLED, mesh: {link: `link_bend_${Math.round((1 - bend) * 10)}`},
          M: above(0, {lid: k.poseLid(th), link: I4()}) };
      }
      return { vis: ASSEMBLED, M: above(0, { lid: k.poseLid(th), link: mul(k.bend(AM, TM, bend), k.poseLink(AM, TM)) }) };
    } };
  const roofLower = A.J_roof_lower;
  const roofStrain = A.J_roof_press_strain_pct;
  const roofRelease = A.J_roof_release;
  const roofLatch = roofLower?.worst?.["roof-box"];
  const roofUnexpected = Object.entries(roofLower?.worst || {}).filter(([name]) => name !== "roof-box");
  const roofReleases = roofRelease && Object.values(roofRelease.worst || {}).every((hit) => hit.depth <= 0.001);
  const roofStep = D.meshes.roof ? {
    t: `蓋を ${G.roof_lid_deg ?? TM}° に保つ。固定天面を上から下ろす。左右の解除つまみを箱の中央へ押してから離す`,
    r: roofLower
      ? `${G.roof_from_mm ?? 45}mm 上から下ろす。爪が壁へ ${roofLatch?.depth ?? "未計測"}mm 掛かる。他の当たり ${roofUnexpected.length} 件。脚のひずみ ${roofStrain ?? "未計測"}%${roofReleases ? "。解除つまみを内へ押すと同じ経路で外せる" : ""}`
      : "固定天面の組み立て検証値は生成後に表示する",
    f: (p) => ({ vis: new Set([...ASSEMBLED, "roof"]), M: { ...k.pose(G.roof_lid_deg ?? TM), roof: T(0, 0, (G.roof_from_mm ?? 45) * (1 - p)) } }),
  } : null;
  const closeLid = { t: "サーボを動かして閉じる（角度は右の手順で決める）", r: `0〜${OPEN}° の ${D.verify.motion.steps} 姿勢で部品どうしの当たり ${D.verify.motion.poses_with_hits.length} 件`,
    f: (p) => ({ vis: ALL, M: k.pose(TM * (1 - p)) }) };
  const retained = G.joint_b_retained;
  const AB = G.setup_alpha_deg, LB = retained ? k.linkAng(AB, BACK) : 0;
  const PA = retained ? k.pinA(AB) : [0, 0], PB = retained ? k.pinB(BACK) : [0, 0];
  const retainedPose = retained ? k.pose(BACK, AB) : {};
  const lift = (M, dz = UP) => Object.fromEntries(Object.entries(M).map(([name, m]) => [name, mul(T(0, 0, dz), m)]));
  const joinedOutside = { lid: retainedPose.lid, link: retainedPose.link, crank: retainedPose.crank };
  const bKeyLink = A.B_retainer_turn?.from_link_deg ?? BACK + G.joint_b_key_deg + 180;
  const bTurn = A.B_retainer_turn?.chosen_delta_deg ?? LB - bKeyLink;
  const bJoin = { t: "箱の外で、緑のピンの爪を水色の蓋の切り欠きに通す。リンクを下側へ回して留める",
    r: "爪を通して回す経路を検証。リンクを曲げずに組む",
    f: (p) => {
      const lam = p < .5 ? bKeyLink : bKeyLink + bTurn * ((p - .5) / .5);
      const dx = p < .5 ? (A.B_retainer_insert?.from_x_mm ?? -8) * (1 - p / .5) : 0;
      return { vis: V("lid", "link"), M: lift({ lid: retainedPose.lid,
        link: mul(T(dx, 0, 0), mul(RX(lam - LB, ...PB), retainedPose.link)) }) };
    } };
  const aJoin = { t: `黄色の爪を緑のリンクの切り欠きに通す。黄色の部品を回して、蓋が${BACK}°開く姿勢にする`,
    r: "蓋とリンクを動かさずにクランクを差して回す経路を検証",
    f: (p) => {
      const keyAlpha = LB - D.kin.key_rel;
      const al = p < .5 ? keyAlpha : keyAlpha + (AB - keyAlpha) * ((p - .5) / .5);
      const dx = p < .5 ? (A.C_retainer_crank_insert?.from_x_mm ?? -8) * (1 - p / .5) : 0;
      return { vis: V("lid", "link", "crank"), M: lift({ ...joinedOutside,
        crank: mul(T(dx, 0, 0), mul(RX(al - AB, ...PA), retainedPose.crank)) }) };
    } };
  const retainedHorn = { t: `箱の外でサーボを90°にする。付属ホーンを付け、つないだ3部品をかぶせる${hornNote}`,
    r: `蓋を${BACK}°に保ち、${G.crank_push_mm}mm手前から差す経路を検証${hornCheck}`,
    f: (p) => ({ vis: V(...UNIT, "lid", "link"), M: lift({ ...joinedOutside,
      ...Object.fromEntries(Object.entries(joinedOutside).map(([name, m]) => [name, mul(T(G.crank_push_mm * (1 - p), 0, 0), m)])),
      ref_body: I4(), ref_wire: I4(), ref_horn: retainedPose.ref_horn }) }) };
  const retainedLower = { t: `蓋を${BACK}°に保ち、蓋付きのサーボ一式を上から箱へ下ろす。配線を切り欠きへ通す`,
    r: `蓋を含む一式を${G.lower_from_mm}mm上から下ろす経路を検証`,
    f: (p) => ({ vis: V("box", ...SPK, ...UNIT, "link", "lid"),
      M: lift({ ...retainedPose, ref_body: I4(), ref_wire: I4() }, UP * (1 - p)) }) };
  const retainedClip = { ...servoClip,
    f: (p) => ({ vis: V("box", ...SPK, ...UNIT, "link", "lid", "clip"),
      M: { ...retainedPose, clip: T(0, 0, G.clip_from_mm * (1 - p)) } }) };
  const retainedPin = { ...hingePin,
    f: (p) => ({ vis: ASSEMBLED, M: { ...retainedPose, pin: T(G.pin_travel_mm * (1 - p), 0, 0) } }) };
  const retainedReturn = { t: `蝶番ピンを入れたら、蓋を${BACK}°から${TM}°へ戻す。サーボをゆっくり動かす`,
    r: `蓋${BACK}°から中央姿勢までの延長範囲も検証。緑と水色の接合を曲げる工程は不要`,
    f: (p) => ({ vis: ASSEMBLED, M: k.pose(BACK + (TM - BACK) * p) }) };
  const STEPS = retained
    ? [speakerStep, bJoin, aJoin, retainedHorn, retainedLower, retainedClip, retainedPin, retainedReturn, roofStep, closeLid].filter(Boolean)
    : G.unit_first
    ? [speakerStep, buildUnit, attachLink, lowerUnit, servoClip, placeLid, hingePin, linkB, roofStep, closeLid].filter(Boolean)
    : [speakerStep, lidFirst, hingePin, buildUnit, attachLink, lidBack, lowerUnit, servoClip, linkB, roofStep, closeLid].filter(Boolean);
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
  const clear = (w) => !w || Object.values(w).every((hit) => hit.depth <= 0.003);
  const rows = [
    ...(SPK.length ? [["エキサイターと押さえ", `${G.speaker_travel_mm}mm 上から`, G.speaker_check]] : []),
    ["蝶番ピンを差す", `右側面から ${G.pin_path_mm}mm`, G.pin_flat_ends ? (hingeCheck.note || "経路を検証") : `先端の圧入 ${hingeCheck.worst["pin-box"].depth}mm のみ`],
    ["クランクをホーンへ", `${G.crank_push_mm}mm 手前から`, (retained ? clear(A.C_retainer_horn_insert.worst) : empty(A.B_crank_onto_horn.worst)) ? "当たりなし" : "当たりあり"],
    ["リンクをピン A へ", "鍵溝の角度で差し、回す", (retained ? clear(A.C_retainer_crank_insert.worst) && clear(A.C_retainer_crank_turn.worst) : empty(A.C1_link_push_at_key.worst) && empty(A.C2_link_turn_to_operating.worst)) ? "当たりなし" : "当たりあり"],
    ["黄色と緑の抜け止め", `動作範囲の 3 姿勢で ${A.C3_bayonet_lock.pull_check_mm ?? 2}mm 引く`, (A.C3_bayonet_lock.ok ?? A.C3_bayonet_lock.operating.every((r) =>
      r.first_contact_mm != null ? r.first_contact_mm <= (A.C3_bayonet_lock.pull_check_mm ?? 2) : (r.pulled_2mm_hits ?? r.pulled_1mm_hits) > 0)) ? "3 姿勢とも爪に当たる" : "抜ける姿勢あり"],
    ["サーボ一式を下ろす", `${G.lower_from_mm}mm 上から`, empty(A.D_servo_unit_lower.worst) ? "当たりなし" : "当たりあり"],
    ["クリップを押し込む", `${G.clip_from_mm}mm 上から`, clipCheck],
    ...(!retained && G.unit_first ? [["蓋を後から載せる", `${G.lid_place_from_mm}mm 上から。蓋 ${BACK}°`, empty(lidPlaceCheck.worst) ? "当たりなし" : "当たりあり"]] : []),
    ...(retained ? [["緑と水色の抜け止め", "0〜65°で横方向へ引く", A.B_retainer_lock?.ok ? "爪に当たり、抜ける前に止まる" : "検証結果を確認"],
      ["箱の外でピンBを留める", "切り欠きを通して回す", clear(A.B_retainer_insert?.worst) && A.B_retainer_turn?.ok ? "当たりなし。曲げ不要" : "当たりあり"]]
      : [["ピン B を入れる", `蓋 ${BACK}° → ${TM}°`, empty(A.F_lid_down_with_link_bent.hits) ? `当たりなし（ひずみ ${A.F_link_bend_strain_pct}%）` : "当たりあり"]]),
    ...(D.meshes.roof ? [["固定天面を付ける", `${G.roof_from_mm ?? 45}mm 上から。蓋 ${G.roof_lid_deg ?? TM}°`,
      roofLower && !roofUnexpected.length ? `爪 ${roofLatch?.depth ?? "未計測"}mm、ほかの当たりなし（脚のひずみ ${roofStrain ?? "未計測"}%）` : "検証値を確認"]] : []),
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
