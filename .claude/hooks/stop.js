#!/usr/bin/env node
// Stop hook（Claude Code と Codex の両方から呼ぶ）: 機構モデルのゲートが古い・赤のまま作業を終えようとしたら知らせる。
//
// 動きの定義を持つモデル（models/<名前>/anim.py）は、検査が赤・書き出しが定義より古いときも知らせる。
//
// 対象は spec.json を持つモデルのうち、未コミットの変更か未 push のコミットがあるもの。
// 判定は `py -3.11 tools/mechgate.py fresh <名前>`（入力の SHA を比べるだけ。Blender は使わない）。
// 知らせるのはセッションにつき 1 回（ループと過剰な割り込みを防ぐ）。エラー時は素通し。
//
//   Claude Code: .claude/settings.json の Stop から `node .claude/hooks/stop.js`
//                → {"decision":"block","reason":...}（1 回だけ止めて、ゲートを流すか赤と報告させる）
//   Codex:       ~/.codex/hooks/stop-guard.js がリポジトリのこのファイルを `--codex` で呼ぶ
//                → {"systemMessage": ...}
const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const codex = process.argv.includes('--codex');

function git(cwd, args) {
  try {
    return execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 8000 });
  } catch {
    return '';
  }
}

let buf = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (d) => (buf += d));
process.stdin.on('end', () => {
  try {
    const input = JSON.parse(buf || '{}');
    if (input.stop_hook_active) return;
    const root = git(input.cwd || process.cwd(), ['rev-parse', '--show-toplevel']).trim();
    if (!root || !fs.existsSync(path.join(root, 'tools', 'mechgate.py'))) return;

    const stateDir = path.join(os.tmpdir(), 'mechgate-stop');
    const stateFile = input.session_id ? path.join(stateDir, `${input.session_id}.json`) : null;
    if (stateFile && fs.existsSync(stateFile)) return;

    const touched = new Set();
    const collect = (text, strip) => {
      for (const line of text.split('\n')) {
        const p = strip ? line.slice(3) : line;
        const m = /^"?models\/([^/]+)\//.exec(p.trim());
        if (m) touched.add(m[1]);
      }
    };
    collect(git(root, ['status', '--porcelain', '--', 'models']), true);
    collect(git(root, ['diff', '--name-only', '@{u}..HEAD', '--', 'models']), false);

    const problems = [];
    const animProblems = [];
    for (const model of touched) {
      // 動きの定義を持つモデル（anim.py）: 検査が赤、または書き出しが定義より古いまま終えようとしている
      const anim = path.join('models', model, 'anim.py');
      if (fs.existsSync(path.join(root, anim))) {
        for (const sub of ['check', 'status']) {
          try {
            execFileSync('py', ['-3.11', anim, sub],
              { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 20000 });
          } catch (e) {
            const tail = (e.stdout || '').toString().trim().split('\n').slice(-3).join(' / ');
            animProblems.push(`${model}: anim.py ${sub} が通らない。${tail}`);
            break;
          }
        }
      }
      if (!fs.existsSync(path.join(root, 'models', model, 'spec.json'))) continue;
      let out = '';
      let ok = true;
      try {
        out = execFileSync('py', ['-3.11', 'tools/mechgate.py', 'fresh', model],
          { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 15000 });
      } catch (e) {
        ok = false;
        out = (e.stdout || '').toString();
      }
      if (!ok) problems.push(out.trim() || `${model}: 判定できない`);
    }
    if (!problems.length && !animProblems.length) return;

    if (stateFile) {
      fs.mkdirSync(stateDir, { recursive: true });
      fs.writeFileSync(stateFile, JSON.stringify({ at: new Date().toISOString(), problems, animProblems }));
    }
    const lines = [];
    if (problems.length) {
      lines.push(
        '[mechgate] 機構モデルのゲートが合格・最新ではない:',
        ...problems.map((p) => '  ' + p),
        '`py -3.11 tools/mechgate.py check <名前>` を流して exit 0 にする。',
        '赤のまま終えるなら、報告の先頭に「ゲート不合格」と止めている検査 id を書く（.claude/skills/mechanism-gate/SKILL.md §5）。',
      );
    }
    if (animProblems.length) {
      lines.push(
        '[anim] 動きの定義が検査を通っていない、または書き出しが古い:',
        ...animProblems.map((p) => '  ' + p),
        '`py -3.11 models/<名前>/anim.py build` を流す（.claude/skills/uhand-animation/SKILL.md）。',
      );
    }
    const message = lines.join('\n');
    if (codex) {
      process.stdout.write(JSON.stringify({ systemMessage: message }));
    } else {
      process.stdout.write(JSON.stringify({ decision: 'block', reason: message }));
    }
  } catch {
    // 素通し
  }
});
