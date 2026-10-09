export const SESSION_VERSION = 2;

const SPEEDS = new Set([0.5, 1, 2, 4, 8]);
const DWELLS = new Set([0.5, 2, 4, 8]);
const SHELLS = new Set(['solid', 'transparent', 'hidden']);

export function parseStepParam(value, count) {
  if (typeof value !== 'string' || !/^\d+$/.test(value)) return null;
  const index = Number(value);
  return Number.isSafeInteger(index) && index >= 0 && index < count ? index : null;
}

export function restoreSession(value, { cadSha, steps, partIds, gateTitles = [] }) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  if (![1, SESSION_VERSION].includes(value.version) || value.cadSha !== cadSha) return null;
  if (typeof value.stepTitle !== 'string') return null;
  const index = steps.findIndex(step => step.title === value.stepTitle);
  if (index < 0 || !Number.isFinite(value.fraction) || value.fraction < 0 || value.fraction > 1) return null;
  if (value.selected !== null && !partIds.includes(value.selected)) return null;
  if (!SPEEDS.has(value.speed) || !DWELLS.has(value.dwell) || !SHELLS.has(value.shell)) return null;
  if (typeof value.wires !== 'boolean' || typeof value.autoCamera !== 'boolean') return null;
  const bypass = value.version === 1 && value.bypass === undefined ? false : value.bypass;
  if (typeof bypass !== 'boolean') return null;
  const gate = value.mode === 'auto' && value.phase === 'gate';
  if (gate && !gateTitles.includes(value.stepTitle)) return null;
  return {
    index,
    fraction: value.fraction,
    selected: value.selected,
    speed: value.speed,
    dwell: value.dwell,
    shell: value.shell,
    wires: value.wires,
    autoCamera: value.autoCamera,
    bypass,
    mode: gate ? 'auto' : 'single',
    phase: gate ? bypass ? 'dwell' : 'gate' : value.fraction < 1 ? 'motion' : 'settled',
  };
}

export function createSession({ cadSha, stepTitle, fraction, selected, speed, dwell, shell, wires, autoCamera, bypass, mode, phase }) {
  return { version: SESSION_VERSION, cadSha, stepTitle, fraction, selected, speed, dwell, shell, wires, autoCamera, bypass, mode, phase };
}
