// ロボットの「気分」と、ファームの返事の読み取り。画面に依らないのでここだけ node で試せる。

export const LINES = Object.freeze({
  hello: 'やっと起こしたね。',
  stopped: '止まった。止まりたかったし。',
  hot: 'モーターが熱い。今日はここまで。',
  jammed: 'どこかに引っかかった。力を抜いたよ。',
  obey: Object.freeze({
    W: '前ね。今そっちへ行こうと思ってた。',
    B: '後ろへ。下がるのは作戦だから。',
    L: '左。そっちの方が景色がいい。',
    R: '右。別に言われたからじゃない。',
  }),
  refuse: Object.freeze(['今は歩く気分じゃない。', 'もう一回頼んでみて。', 'なんで今なの。']),
  gaveIn: '分かった。今回だけだよ。',
  poked: Object.freeze(['つつかないで。', '今の、覚えておくからね。', '画面は指紋がつくんだけど。']),
});

const REFUSE_CHANCE = 0.25;
const MAX_REFUSALS = 2;       // これ以上は断らない。動かないロボットは試験できない

/** 頼まれたときに聞くかどうか。random は 0〜1。止める操作はここを通らない。 */
export function decide(command, { moody = true, refused = 0, random = 1 } = {}) {
  if (refused > 0 && refused >= MAX_REFUSALS) {
    return { obey: true, refused: 0, mood: '得意', line: LINES.gaveIn };
  }
  if (moody && (refused > 0 || random < REFUSE_CHANCE)) {
    const line = LINES.refuse[refused % LINES.refuse.length];
    return { obey: false, refused: refused + 1, mood: '不満', line };
  }
  return { obey: true, refused: 0, mood: '得意', line: LINES.obey[command] ?? '' };
}

const TRIM_GAIN = 1.0;        // sim_gait.py の yaw_kp と同じ
const TRIM_LIMIT = 8;

/** 向きのずれ [deg] から操舵 [deg] を出す。左回りのずれには右へ切る。 */
export function trimFromYaw(yawDeg, flip = false) {
  const value = -TRIM_GAIN * yawDeg * (flip ? -1 : 1);
  const trim = Math.round(Math.max(-TRIM_LIMIT, Math.min(TRIM_LIMIT, value)));
  return trim === 0 ? 0 : trim;   // -0 を送らない
}

/** ファームの 1 行を読む。JSON でなければ null。 */
export function parseState(line) {
  if (!line.startsWith('{')) return null;
  try {
    return JSON.parse(line);
  } catch {
    return null;
  }
}

function describeLeg(name, leg) {
  if (leg === null) return `${name}: 見つかりません`;
  const volts = (leg.dV / 10).toFixed(1);
  return `${name}: ${leg.deg.toFixed(1)}° ${leg.tempC}℃ ${volts}V 番号 ${leg.id} 生の値 ${leg.raw} 異常 ${leg.status}`;
}

/** 状態の 1 行を読みやすくする。脚の情報が無い返事なら前の表示を残す。 */
export function describeState(state, previous = '') {
  if (state.left === undefined && state.right === undefined) return previous;
  return [describeLeg('左脚', state.left), describeLeg('右脚', state.right)].join('\n');
}
