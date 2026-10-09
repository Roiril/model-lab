export const B3_MODEL = 'mystery-box-sg92r-b3-candidate';
const THEME_KEY = 'model-lab.theme';
export function resolveTheme(urlTheme, savedTheme) {
  return [urlTheme, savedTheme].find(value => value === 'light' || value === 'dark') ?? null;
}
function savedTheme() {
  try { return localStorage.getItem(THEME_KEY); } catch { return null; }
}
// URLの指定、保存した選択、OSの配色の順で使う。
if (typeof document !== 'undefined' && typeof location !== 'undefined') {
  const theme = resolveTheme(new URLSearchParams(location.search).get('theme'), savedTheme());
  if (theme) document.documentElement.dataset.theme = theme;
}
export const WORKSPACES = Object.freeze([
  { id: 'studio', label: '伝える' },
  { id: 'physics', label: '物理検証' },
  { id: 'assembly', label: '組み立て' },
]);

// 物理検証・組み立ての画面を持つモデル。ここに無いモデルではタブを押せない表示にする。
export const WORKSPACE_PAGES = Object.freeze({
  [B3_MODEL]: Object.freeze({ physics: '/viewer/physics-box/index.html', assembly: '/viewer/assembly-box/index.html' }),
  'servo-lid-cube': Object.freeze({ physics: '/viewer/lid-cube/physics.html', assembly: '/viewer/lid-cube/assembly.html' }),
});

export function hasWorkspace(mode, model) {
  return mode === 'studio' || Boolean(WORKSPACE_PAGES[model]?.[mode]);
}

export function workspaceHref(mode, model = B3_MODEL) {
  if (!WORKSPACES.some(item => item.id === mode)) throw new RangeError('Unknown workspace');
  if (mode === 'studio') return `/?model=${encodeURIComponent(model || B3_MODEL)}`;
  const target = WORKSPACE_PAGES[model]?.[mode] ? model : B3_MODEL;
  return `${WORKSPACE_PAGES[target][mode]}?model=${encodeURIComponent(target)}`;
}

export function createWorkspaceNav({ active, model = B3_MODEL, onNavigate } = {}) {
  const element = document.createElement('nav');
  element.className = 'workspace-nav';
  element.setAttribute('aria-label', '作業画面');
  const themeButton = document.createElement('button');
  themeButton.type = 'button';
  themeButton.className = 'workspace-theme';
  const updateThemeButton = palette => {
    themeButton.textContent = palette.dark ? '明るく' : '暗く';
    themeButton.setAttribute('aria-label', palette.dark ? '明るい配色に切り替える' : '暗い配色に切り替える');
  };
  const disposeTheme = watchTheme(updateThemeButton);
  addEventListener('pagehide', event => { if (!event.persisted) disposeTheme(); });
  function updateLinks() {
    const theme = resolveTheme(document.documentElement.dataset.theme, null);
    for (const link of element.querySelectorAll('a[data-workspace]')) {
      link.href = workspaceHref(link.dataset.workspace, model) + (theme ? `&theme=${theme}` : '');
    }
    const skip = document.querySelector('.workspace-skip');
    if (skip) skip.href = `${location.pathname}${location.search}#stage`;
  }
  themeButton.addEventListener('click', () => {
    const theme = themePalette().dark ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem(THEME_KEY, theme); } catch { /* 保存できなくても切り替える。 */ }
    const url = new URL(location.href);
    url.searchParams.set('theme', theme);
    history.replaceState(history.state, '', url);
    updateLinks();
    updateThemeButton(themePalette());
  });
  let renderedModel;
  function setModel(next) {
    if (next === renderedModel && element.childElementCount) return;
    renderedModel = next;
    model = next;
    element.replaceChildren(...WORKSPACES.map(item => {
      const available = hasWorkspace(item.id, model);
      const link = document.createElement(available ? 'a' : 'span');
      link.className = 'workspace-link';
      link.dataset.workspace = item.id;
      link.textContent = item.label;
      if (item.id === active) link.setAttribute('aria-current', 'page');
      if (available) {
        link.href = workspaceHref(item.id, model);
        const theme = resolveTheme(document.documentElement.dataset.theme, null);
        if (theme === 'light' || theme === 'dark') link.href += `&theme=${theme}`;
        link.addEventListener('click', event => {
          if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
          if (item.id === active) { event.preventDefault(); return; }
          onNavigate?.(item.id);
          window.dispatchEvent(new CustomEvent('workspace:navigate', { detail: { from: active, to: item.id, model } }));
        });
      } else {
        link.setAttribute('aria-disabled', 'true');
        link.setAttribute('aria-label', `${item.label}。このモデルにはまだありません`);
        link.title = 'このモデルにはまだありません';
        const note = document.createElement('small');
        note.textContent = '未対応';
        link.append(note);
      }
      return link;
    }), themeButton);
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
