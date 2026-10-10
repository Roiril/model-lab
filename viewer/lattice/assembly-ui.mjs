import { transformsAt, quintic } from './motion.mjs';

const $ = id => document.getElementById(id);

export function setupAssembly({ data, state, renderer }) {
  const assembly = data.assembly;
  if (!assembly?.steps?.length) throw new Error('工程と経路のデータがありません');
  const steps = assembly.steps;
  let index = Math.max(0, Math.min(steps.length - 1, Number(new URLSearchParams(location.search).get('step') || 1) - 1));
  let animation = 0, sequential = false, progress = 0;
  const duration = 1.8;
  const stop = () => { cancelAnimationFrame(animation); animation = 0; sequential = false; $('play').textContent = 'この工程を再生'; $('all').textContent = '全部を順に再生'; };
  function draw(fraction) {
    progress = Math.max(0, Math.min(1, fraction));
    const step = steps[index];
    state.transforms = transformsAt(step.frames, progress);
    state.present = new Set(Object.keys(state.transforms));
    $('gl').dataset.assemblyStep = String(index + 1);
    $('gl').dataset.assemblyProgress = progress.toFixed(5);
    $('gl').dataset.activeParts = step.moving.join(',');
    renderer.draw();
  }
  function select(next, end = false) {
    index = next;
    const step = steps[index];
    $('stepNumber').textContent = `工程 ${index + 1} / ${steps.length}`;
    $('stepTitle').textContent = step.title;
    $('stepInstruction').textContent = step.instruction;
    $('stepResult').textContent = `検証: ${step.checkText}`;
    $('prev').disabled = index === 0; $('next').disabled = index === steps.length - 1;
    $('steps').querySelectorAll('button').forEach((button, i) => {
      if (i === index) button.setAttribute('aria-current', 'step'); else button.removeAttribute('aria-current');
    });
    for (const label of $('legend').querySelectorAll('label')) label.classList.toggle('active', step.moving.includes(label.dataset.part));
    renderer.fit(step.frames);
    const url = new URL(location.href); url.searchParams.set('step', String(index + 1)); history.replaceState(null, '', url);
    draw(end ? 1 : 0);
  }
  function play(all = false) {
    stop(); sequential = all;
    $('play').textContent = '停止'; $('all').textContent = all ? '停止' : '全部を順に再生';
    let previous = performance.now(), elapsed = 0;
    draw(0);
    const tick = now => {
      elapsed += Math.min(.1, (now - previous) / 1000) * Number($('speed').value); previous = now;
      draw(quintic(Math.min(1, elapsed / duration)));
      if (elapsed < duration) animation = requestAnimationFrame(tick);
      else if (sequential && index < steps.length - 1) {
        select(index + 1); elapsed = 0; animation = requestAnimationFrame(tick);
      } else stop();
    };
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
      if (all) select(steps.length - 1, true); else draw(1); stop(); return;
    }
    animation = requestAnimationFrame(tick);
  }
  $('steps').replaceChildren(...steps.map((step, i) => {
    const li = document.createElement('li'), button = document.createElement('button'), number = document.createElement('span'), title = document.createElement('span');
    button.type = 'button'; number.className = 'n'; number.textContent = String(i + 1); title.textContent = step.title;
    button.append(number, title); button.addEventListener('click', () => { stop(); select(i); play(); }); li.append(button); return li;
  }));
  $('prev').addEventListener('click', () => { stop(); select(index - 1); play(); });
  $('next').addEventListener('click', () => { stop(); select(index + 1); play(); });
  $('play').addEventListener('click', () => { if (animation) stop(); else play(); });
  $('all').addEventListener('click', () => { if (sequential) stop(); else { select(0); play(true); } });
  $('assemblyRows').replaceChildren(...steps.map(step => {
    const tr = document.createElement('tr');
    for (const value of [step.title, `${step.report.samples}姿勢`, step.checkText]) { const td = document.createElement('td'); td.textContent = value; tr.append(td); }
    return tr;
  }));
  $('assemblyCalibration').textContent = assembly.calibration?.pass || assembly.calibration?.ok
    ? '検査前に、既知の重なりを検出することと、離した部品を通すことを確認しました。表示と検査は同じ部品位置を使います。1mm以下の並進と5°以下の回転で検査しています。'
    : '干渉検査の校正結果を確認できません。判定は未確認です。';
  $('servoSetup').textContent = data.model.endsWith('c4')
    ? 'SG92Rを90°にして付属ホーンを付けます。ホーン受けとカムを90°の位相で組みます。右の保持具を留めたらhで10°へ戻して停止します。格子はその後に入れます。gで10〜170°を片道1.5秒で動かします。分解時は格子を外した後にcで90°へ戻します。'
    : '箱の外でSG92Rを90°にして付属ホーンと駆動歯車を付けます。カムと軸を90°の位相で入れます。格子を入れる前にhで15°へ戻して停止します。gで15〜165°を片道2秒で動かします。分解時は格子を外した後にcで90°へ戻します。';
  select(index); play();
  addEventListener('pagehide', stop, { once: true });
}
