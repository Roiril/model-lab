#!/usr/bin/env node
// Project-specific PreToolUse guard.
// 汎用不可逆操作ガードはグローバル ~/.claude/hooks/pre-tool-use-guard.js
// で実施済み。ここにはプロジェクト固有のチェックだけを追加する。
// 例：自動生成ファイルの手動編集ガード、特定ディレクトリ保護、など。
let buf = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', d => (buf += d));
process.stdin.on('end', () => {
  try {
    const j = JSON.parse(buf || '{}');
    const tool = j.tool_name || '';
    const input = j.tool_input || {};
    const reasons = [];

    // TODO: プロジェクト固有のガードをここに追加
    // 例:
    // if (tool === 'Write' || tool === 'Edit') {
    //   const fp = String(input.file_path || '');
    //   if (/generated[\\/]/.test(fp)) reasons.push('generated/ の手動編集');
    // }

    if (reasons.length) {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: {
          hookEventName: 'PreToolUse',
          permissionDecision: 'ask',
          permissionDecisionReason: '⚠️ ' + reasons.join(' / ')
        }
      }));
    }
  } catch {
    // never block on hook error
  }
});
