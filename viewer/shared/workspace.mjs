export const B3_MODEL = 'mystery-box-sg92r-b3-candidate';
// テーマを指定した共有URLにも対応する。通常はOSの配色に従う。
if (typeof document !== 'undefined' && typeof location !== 'undefined') {
  const theme = new URLSearchParams(location.search).get('theme');
  if (theme === 'light' || theme === 'dark') document.documentElement.dataset.theme = theme;
}
export const WORKSPACES = Object.freeze([
  { id: 'studio', label: '伝える' },
  { id: 'physics', label: '物理検証' },
  { id: 'assembly', label: '組み立て' },
]);

export function workspaceHref(mode, model = B3_MODEL) {
  if (!WORKSPACES.some(item => item.id === mode)) throw new RangeError('Unknown workspace');
  if (mode === 'studio') return `/?model=${encodeURIComponent(model || B3_MODEL)}`;
  return `/viewer/${mode}-box/index.html?model=${encodeURIComponent(B3_MODEL)}`;
}

export function createWorkspaceNav({ active, model = B3_MODEL, onNavigate } = {}) {
  const element = document.createElement('nav');
  element.className = 'workspace-nav';
  element.setAttribute('aria-label', '作業画面');
  let renderedModel;
  function setModel(next) {
    if (next === renderedModel && element.childElementCount) return;
    renderedModel = next;
    model = next;
    element.replaceChildren(...WORKSPACES.map(item => {
      const available = item.id === 'studio' || model === B3_MODEL;
      const link = document.createElement(available ? 'a' : 'span');
      link.className = 'workspace-link';
      link.dataset.workspace = item.id;
      link.textContent = item.label;
      if (item.id === active) link.setAttribute('aria-current', 'page');
      if (available) {
        link.href = workspaceHref(item.id, model);
        const theme = new URLSearchParams(location.search).get('theme');
        if (theme === 'light' || theme === 'dark') link.href += `&theme=${theme}`;
        link.addEventListener('click', event => {
          if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
          if (item.id === active) { event.preventDefault(); return; }
          onNavigate?.(item.id);
          window.dispatchEvent(new CustomEvent('workspace:navigate', { detail: { from: active, to: item.id, model } }));
        });
      } else {
        link.setAttribute('aria-disabled', 'true');
        link.setAttribute('aria-label', `${item.label}。B3の箱で使えます`);
        const note = document.createElement('small');
        note.textContent = 'B3用';
        link.append(note);
      }
      return link;
    }));
  }
  setModel(model);
  return { element, setModel };
}

export function readSession(key, fallback = null) {
  try { const value = sessionStorage.getItem(`model-lab.${key}`); return value === null ? fallback : JSON.parse(value); }
  catch { return fallback; }
}
export function writeSession(key, value) {
  try { sessionStorage.setItem(`model-lab.${key}`, JSON.stringify(value)); return true; }
  catch { return false; }
}

export function themePalette() {
  const style = getComputedStyle(document.documentElement);
  const value = name => style.getPropertyValue(`--${name}`).trim();
  return {
    paper: value('paper'), card: value('card'), ink: value('ink'), mute: value('mute'), line: value('line'),
    accent: value('accent'), accentStrong: value('accent-strong'),
    dark: style.colorScheme.includes('dark'),
  };
}
export function watchTheme(callback) {
  const media = matchMedia('(prefers-color-scheme: dark)');
  const update = () => callback(themePalette());
  media.addEventListener('change', update);
  const observer = new MutationObserver(update);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  update();
  return () => { media.removeEventListener('change', update); observer.disconnect(); };
}
