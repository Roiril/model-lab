// Studio のモデル一覧。絞り込みは純関数に分け、画面は #layer-palette だけを使う。

const FAVORITES_KEY = "studio.favorites";
const PAGE_SIZE = 30;

const VIEW_LABELS = [
  ["browse", "通常"],
  ["all", "全件"],
  ["recent", "最近"],
  ["favorites", "お気に入り"],
  ["archived", "保管"],
];

export function normalizeSearchText(value) {
  return String(value ?? "")
    .normalize("NFKC")
    .toLocaleLowerCase("ja")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function text(value, fallback = "") {
  const s = String(value ?? "").trim();
  return s || fallback;
}

function ids(value) {
  const list = Array.isArray(value) ? value : [];
  const seen = new Set();
  return list.filter((item) => {
    if (typeof item !== "string") return false;
    const id = item.trim();
    if (!id || seen.has(id)) return false;
    seen.add(id);
    return true;
  }).map((item) => item.trim());
}

export function parseFavorites(value, validNames = null) {
  let parsed = value;
  if (typeof value === "string") {
    try { parsed = JSON.parse(value); } catch { return []; }
  }
  const valid = validNames ? new Set(ids(validNames)) : null;
  return ids(parsed).filter((name) => !valid || valid.has(name));
}

function taxonomyId(value, label, fallback) {
  const id = text(value);
  if (id) return id;
  const normalized = normalizeSearchText(label).replace(/\s+/g, "-");
  return normalized ? `label:${normalized}` : fallback;
}

function modelInfo(model, index = 0) {
  const raw = model && typeof model === "object" ? model : {};
  const name = text(raw.name);
  const declaredCategoryId = text(raw.categoryId);
  const organized = raw.organized !== false && declaredCategoryId !== "unorganized";
  const category = organized ? text(raw.category, "その他") : "未整理";
  const categoryId = organized
    ? taxonomyId(declaredCategoryId, category, "other")
    : "unorganized";
  const project = text(raw.project, "関連プロジェクトなし");
  const projectId = taxonomyId(raw.projectId, project, "unassigned");
  const hasProject = typeof raw.hasProject === "boolean" ? raw.hasProject : !!text(raw.projectId);
  const tags = ids(raw.tags);
  const status = ["active", "reference", "archived"].includes(raw.status) ? raw.status : "active";
  const title = text(raw.title, name || "名前のないモデル");
  const available = raw.available !== false && !!name;
  const unavailableReason = available
    ? ""
    : text(raw.unavailableReason, name ? "この一覧からは開けません" : "識別子がありません");
  const searchText = normalizeSearchText([
    title, raw.description, category, categoryId, project, projectId, tags.join(" "), name,
  ].join(" "));
  return {
    ...raw,
    _index: index,
    name,
    title,
    description: text(raw.description),
    category,
    categoryId,
    project,
    projectId,
    hasProject,
    tags,
    status,
    organized,
    available,
    unavailableReason,
    preview: !!raw.preview,
    searchText,
  };
}

function uniqueModels(models) {
  const seen = new Set();
  return (Array.isArray(models) ? models : []).map(modelInfo).filter((model, index) => {
    const key = model.name || `missing:${index}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function filterModels(models, filters = {}) {
  const all = uniqueModels(models);
  const view = filters.view || "browse";
  const query = normalizeSearchText(filters.query);
  const terms = query.split(" ").filter(Boolean);
  const favorites = new Set(parseFavorites(filters.favorites));
  const recent = ids(filters.recent);
  const recentOrder = new Map(recent.map((name, index) => [name, index]));
  const categoryId = text(filters.categoryId);
  const projectId = text(filters.projectId);

  const result = all.filter((model) => {
    if (view === "archived" && model.status !== "archived") return false;
    if (view === "favorites" && !favorites.has(model.name)) return false;
    if (view === "recent" && !recentOrder.has(model.name)) return false;
    if (view === "browse" && !terms.length && model.status === "archived") return false;
    if (categoryId && model.categoryId !== categoryId) return false;
    if (projectId && model.projectId !== projectId) return false;
    return terms.every((term) => model.searchText.includes(term));
  });

  if (view === "recent") {
    result.sort((a, b) => recentOrder.get(a.name) - recentOrder.get(b.name));
  }
  return result;
}

export function groupModels(models, { recent = [] } = {}) {
  const all = uniqueModels(models);
  const byName = new Map(all.map((model) => [model.name, model]));
  const grouped = [];
  const used = new Set();
  const recentModels = ids(recent).map((name) => byName.get(name)).filter((model) => {
    if (!model || used.has(model.name)) return false;
    used.add(model.name);
    return true;
  });
  if (recentModels.length) grouped.push({ id: "recent", title: "最近開いた", models: recentModels });

  const projects = new Map();
  for (const model of all) {
    const key = model.name || `missing:${model._index}`;
    if (used.has(key)) continue;
    used.add(key);
    const groupId = `${model.categoryId}:${model.projectId}`;
    if (!projects.has(groupId)) {
      projects.set(groupId, {
        id: groupId,
        title: model.hasProject ? model.project : model.category,
        models: [],
      });
    }
    projects.get(groupId).models.push(model);
  }
  grouped.push(...projects.values());
  return grouped;
}

function facets(models) {
  const categories = new Map();
  const projects = new Map();
  for (const model of uniqueModels(models)) {
    const category = categories.get(model.categoryId) || { id: model.categoryId, label: model.category, count: 0 };
    category.count += 1;
    categories.set(model.categoryId, category);
    const project = projects.get(model.projectId) || { id: model.projectId, label: model.project, count: 0 };
    project.count += 1;
    projects.set(model.projectId, project);
  }
  const sort = (a, b) => a.label.localeCompare(b.label, "ja");
  return {
    categories: [...categories.values()].sort(sort),
    projects: [...projects.values()].sort(sort),
  };
}

export function selectModels(models, options = {}) {
  const pageSize = Math.max(1, Number(options.pageSize) || PAGE_SIZE);
  const page = Math.max(1, Number(options.page) || 1);
  const filtered = filterModels(models, options);
  if ((options.view || "browse") !== "recent") {
    const collator = new Intl.Collator("ja", { numeric: true, sensitivity: "base" });
    filtered.sort((a, b) =>
      collator.compare(a.category, b.category)
      || collator.compare(a.project, b.project)
      || collator.compare(a.title, b.title)
      || collator.compare(a.name, b.name));
  }
  const shown = filtered.slice(0, page * pageSize);
  const recentForGroup = options.includeRecentGroup === false ? [] : options.recent;
  const facetModels = filterModels(models, { ...options, categoryId: "", projectId: "" });
  const { categories, projects } = facets(facetModels);
  return {
    items: shown,
    total: filtered.length,
    page,
    pageSize,
    hasMore: shown.length < filtered.length,
    remaining: Math.max(0, filtered.length - shown.length),
    groups: groupModels(shown, { recent: recentForGroup }),
    categories,
    projects,
  };
}

function h(tag, props, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(props || {})) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "class") el.className = value;
    else if (key === "text") el.textContent = value;
    else if (key.startsWith("on")) el.addEventListener(key.slice(2).toLowerCase(), value);
    else if (key in el && !key.startsWith("aria") && !["translate", "spellcheck"].includes(key)) el[key] = value;
    else el.setAttribute(key, value === true ? "" : String(value));
  }
  for (const child of children.flat(Infinity)) {
    if (child === undefined || child === null || child === false) continue;
    el.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return el;
}

function statusLabel(status) {
  return status === "reference" ? "参考" : status === "archived" ? "保管" : "利用中";
}

function setBackgroundInert(layer, inert) {
  if (!inert) return;
  const changed = [];
  for (const el of document.body.children) {
    if (el === layer || el.tagName === "SCRIPT" || el.tagName === "NOSCRIPT") continue;
    changed.push({ el, had: el.hasAttribute("inert") });
    el.inert = true;
  }
  return () => {
    for (const { el, had } of changed) {
      if (!had) el.inert = false;
    }
  };
}

function focusable(dialog) {
  return [...dialog.querySelectorAll("button:not(:disabled), input:not(:disabled), select:not(:disabled), [tabindex]:not([tabindex='-1'])")]
    .filter((el) => !el.hidden && el.getAttribute("aria-hidden") !== "true");
}

export function createCatalog({ store, onOpen, getModels, getRecent, onClose } = {}) {
  const layer = document.querySelector("#layer-palette");
  if (!layer) throw new Error("#layer-palette がありません");
  if (typeof onOpen !== "function") throw new TypeError("onOpen が必要です");

  let opened = null;
  const state = { view: "browse", query: "", categoryId: "", projectId: "", page: 1 };

  function readFavorites(models) {
    const names = uniqueModels(models).map((model) => model.name).filter(Boolean);
    try { return parseFavorites(localStorage.getItem(FAVORITES_KEY), names); } catch { return []; }
  }

  function writeFavorites(favorites) {
    try { localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites)); } catch { /* 保存できなくても一覧は使える */ }
  }

  function close() {
    if (!opened) return;
    const { previousFocus, restoreInert } = opened;
    opened = null;
    layer.replaceChildren();
    restoreInert?.();
    if (previousFocus && document.contains(previousFocus)) previousFocus.focus({ preventScroll: true });
    onClose?.();
  }

  function resetFilters() {
    Object.assign(state, { view: "browse", query: "", categoryId: "", projectId: "", page: 1 });
  }

  function openModel(name) {
    if (!name) return;
    close();
    Promise.resolve(onOpen(name)).catch((error) => {
      console.error(error);
      store?.status?.(`モデルを開けませんでした: ${error.message || error}`, "err");
    });
  }

  function buildDialog(session) {
    const titleId = "catalog-title";
    const resultId = "catalog-results";
    const closeButton = h("button", { type: "button", class: "catalog-close", "aria-label": "モデル一覧を閉じる", onclick: close }, "×");
    const search = h("input", {
      type: "search", class: "catalog-search", name: "model-search", autocomplete: "off", spellcheck: "false",
      value: state.query, placeholder: "名前・説明・タグで探す…", "aria-label": "モデルを検索", "aria-controls": resultId,
    });
    const viewButtons = h("div", { class: "catalog-views", "aria-label": "表示するモデル" });
    const categoryButtons = h("div", { class: "catalog-categories", "aria-label": "用途カテゴリ" });
    const categorySelect = h("select", { class: "catalog-select", name: "category", "aria-label": "用途カテゴリで絞る" });
    const projectSelect = h("select", { class: "catalog-select", name: "project", "aria-label": "関連プロジェクトで絞る" });
    const clearSearch = h("button", { type: "button", class: "catalog-action", onclick: () => {
      state.query = ""; state.page = 1; search.value = ""; render(); search.focus();
    } }, "検索を消す");
    const reset = h("button", { type: "button", class: "catalog-action", onclick: () => {
      resetFilters(); search.value = ""; render(); search.focus();
    } }, "条件を戻す");
    const live = h("p", { class: "catalog-count", role: "status", "aria-live": "polite", "aria-atomic": "true" });
    const list = h("div", { class: "catalog-list", id: resultId, tabindex: "-1" });
    const footer = h("div", { class: "catalog-footer" });
    const body = h("div", { class: "catalog-body" },
      h("div", { class: "catalog-tools" },
        search,
        viewButtons,
        h("div", { class: "catalog-purpose" }, h("p", { class: "catalog-label" }, "用途カテゴリ"), categoryButtons),
        h("div", { class: "catalog-selects" }, categorySelect, projectSelect),
        h("div", { class: "catalog-summary" }, live, h("div", { class: "catalog-actions" }, clearSearch, reset)),
      ),
      list,
      footer,
    );
    const dialog = h("section", { class: "catalog-dialog", role: "dialog", "aria-modal": "true", "aria-labelledby": titleId, tabindex: -1 },
      h("header", { class: "catalog-head" },
        h("div", {}, h("h1", { id: titleId }, "モデルを開く"), h("p", {}, "用途と関連プロジェクトから選べます")),
        closeButton,
      ),
      body,
    );
    const backdrop = h("div", { class: "catalog-backdrop", onclick: (event) => { if (event.target === backdrop) close(); } }, dialog);
    session.refs = { dialog, search, viewButtons, categoryButtons, categorySelect, projectSelect, clearSearch, reset, live, list, footer };

    let composing = false;
    search.addEventListener("compositionstart", () => { composing = true; });
    search.addEventListener("compositionend", () => { composing = false; });
    search.addEventListener("input", () => { state.query = search.value; state.page = 1; render(); });
    search.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        const buttons = [...list.querySelectorAll(".catalog-open:not(:disabled)")];
        const target = event.key === "ArrowDown" ? buttons[0] : buttons.at(-1);
        if (target) { event.preventDefault(); target.focus(); }
      } else if (event.key === "Enter" && !composing && !event.isComposing && event.keyCode !== 229) {
        const target = list.querySelector(".catalog-open:not(:disabled)");
        if (target) { event.preventDefault(); target.click(); }
      }
    });
    dialog.addEventListener("keydown", (event) => {
      if (event.key === "Escape") { event.preventDefault(); close(); return; }
      if (event.key !== "Tab") return;
      const controls = focusable(dialog);
      if (!controls.length) { event.preventDefault(); dialog.focus(); return; }
      const first = controls[0];
      const last = controls.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    layer.append(backdrop);

    for (const [value, label] of VIEW_LABELS) {
      viewButtons.append(h("button", { type: "button", class: "catalog-view", "data-view": value, onclick: () => {
        state.view = value; state.page = 1; render();
      } }, label));
    }
    return dialog;
  }

  function renderOptions(select, items, firstLabel, value) {
    select.replaceChildren(h("option", { value: "" }, firstLabel));
    for (const item of items) select.append(h("option", { value: item.id }, `${item.label}（${item.count}）`));
    select.value = value;
  }

  function renderRow(model, session) {
    const current = store?.state?.model === model.name;
    const favorite = session.favorites.includes(model.name);
    const badges = [
      h("span", { class: "catalog-chip" }, model.project),
      h("span", { class: "catalog-chip" }, model.category),
      model.preview ? h("span", { class: "catalog-chip" }, "すぐ見られる") : null,
      model.status !== "active" ? h("span", { class: "catalog-chip" }, statusLabel(model.status)) : null,
      current ? h("span", { class: "catalog-chip current" }, "表示中") : null,
      ...model.tags.map((tag) => h("span", { class: "catalog-chip tag" }, tag)),
    ];
    const content = [
      h("span", { class: "catalog-title" }, model.title),
      model.description ? h("span", { class: "catalog-description" }, model.description) : null,
      h("span", { class: "catalog-meta" }, badges),
      h("span", { class: "catalog-id", translate: "no" }, model.name || "識別子なし"),
    ];
    const unavailableLabel = "別の形式で作成";
    const reason = normalizeSearchText(model.unavailableReason) === normalizeSearchText(unavailableLabel)
      ? ""
      : model.unavailableReason;
    const primary = model.available
      ? h("button", { type: "button", class: "catalog-open", "aria-label": `${model.title}を開く`, onclick: () => openModel(model.name) }, content)
      : h("div", { class: "catalog-unavailable" }, content,
          h("span", { class: "catalog-unavailable-note" }, unavailableLabel, reason ? ` — ${reason}` : ""));
    const favoriteButton = model.name ? h("button", {
      type: "button", class: "catalog-favorite", "aria-label": favorite ? `${model.title}をお気に入りから外す` : `${model.title}をお気に入りに入れる`,
      "aria-pressed": String(favorite), onclick: () => {
        session.favorites = favorite
          ? session.favorites.filter((name) => name !== model.name)
          : [...session.favorites, model.name];
        writeFavorites(session.favorites);
        render();
      },
    }, favorite ? "★" : "☆") : null;
    return h("article", { class: `catalog-row${model.available ? "" : " unavailable"}` }, primary, favoriteButton);
  }

  function bindRowKeys(list, search) {
    const buttons = [...list.querySelectorAll(".catalog-open:not(:disabled)")];
    buttons.forEach((button, index) => button.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
      event.preventDefault();
      const next = event.key === "ArrowDown" ? index + 1 : index - 1;
      if (next < 0) search.focus();
      else if (next >= buttons.length) buttons[0]?.focus();
      else buttons[next].focus();
    }));
  }

  function render() {
    const session = opened;
    if (!session?.refs) return;
    const refs = session.refs;
    const recent = ids(session.recent);
    const noExtraFilters = state.view === "browse" && !normalizeSearchText(state.query) && !state.categoryId && !state.projectId;
    const selected = selectModels(session.models, {
      ...state,
      favorites: session.favorites,
      recent,
      pageSize: PAGE_SIZE,
      includeRecentGroup: noExtraFilters || state.view === "recent",
    });

    refs.viewButtons.querySelectorAll("button").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.view === state.view));
    });
    const categoryTotal = selected.categories.reduce((sum, category) => sum + category.count, 0);
    refs.categoryButtons.replaceChildren(h("button", {
      type: "button", class: "catalog-category", "aria-pressed": String(!state.categoryId), onclick: () => {
        state.categoryId = ""; state.page = 1; render();
      },
    }, `すべて ${categoryTotal}`));
    for (const category of selected.categories) {
      refs.categoryButtons.append(h("button", {
        type: "button", class: "catalog-category", "aria-pressed": String(state.categoryId === category.id), onclick: () => {
          state.categoryId = category.id; state.page = 1; render();
        },
      }, `${category.label} ${category.count}`));
    }
    renderOptions(refs.categorySelect, selected.categories, "すべての用途", state.categoryId);
    renderOptions(refs.projectSelect, selected.projects, "すべての関連プロジェクト", state.projectId);
    refs.categorySelect.onchange = () => { state.categoryId = refs.categorySelect.value; state.page = 1; render(); };
    refs.projectSelect.onchange = () => { state.projectId = refs.projectSelect.value; state.page = 1; render(); };
    refs.clearSearch.hidden = !state.query;
    refs.reset.disabled = noExtraFilters;
    refs.live.textContent = `${selected.total.toLocaleString("ja-JP")}件。${selected.items.length.toLocaleString("ja-JP")}件を表示中`;
    refs.list.replaceChildren();

    if (!selected.total) {
      refs.list.append(h("div", { class: "catalog-empty" },
        h("p", {}, "該当するモデルがありません"),
        h("button", { type: "button", class: "catalog-reset", onclick: () => {
          resetFilters(); refs.search.value = ""; render(); refs.search.focus();
        } }, "全件に戻す"),
      ));
    } else {
      for (const group of selected.groups) {
        const section = h("section", { class: "catalog-group", "aria-labelledby": `catalog-group-${group.id}` },
          h("h2", { id: `catalog-group-${group.id}` }, group.title, h("span", {}, `${group.models.length}件`)),
        );
        for (const model of group.models) section.append(renderRow(model, session));
        refs.list.append(section);
      }
    }
    bindRowKeys(refs.list, refs.search);
    refs.footer.replaceChildren();
    if (selected.hasMore) {
      refs.footer.append(h("button", { type: "button", class: "catalog-more", onclick: () => {
        state.page += 1; render();
      } }, `続きを表示（残り${selected.remaining.toLocaleString("ja-JP")}件）`));
    } else if (selected.total) {
      refs.footer.append(h("p", {}, `${selected.total.toLocaleString("ja-JP")}件を表示しました`));
    }
  }

  async function open() {
    if (opened) return;
    resetFilters();
    const session = { previousFocus: document.activeElement, models: [], recent: [], favorites: [], refs: null, restoreInert: null };
    opened = session;
    const dialog = buildDialog(session);
    session.restoreInert = setBackgroundInert(layer, true);
    session.refs.list.append(h("p", { class: "catalog-loading" }, "モデルを読み込み中…"));
    const desktop = typeof matchMedia !== "function" || matchMedia("(min-width: 761px)").matches;
    queueMicrotask(() => (desktop ? session.refs.search : dialog).focus());
    try {
      const readModels = async () => {
        let value = await Promise.resolve(typeof getModels === "function" ? getModels() : []);
        for (let attempt = 0; opened === session && (!Array.isArray(value) || !value.length) && attempt < 20; attempt += 1) {
          await new Promise((resolve) => setTimeout(resolve, 75));
          value = await Promise.resolve(typeof getModels === "function" ? getModels() : []);
        }
        return value;
      };
      const [models, recent] = await Promise.all([
        readModels(),
        Promise.resolve(typeof getRecent === "function" ? getRecent() : []),
      ]);
      if (opened !== session) return;
      session.models = Array.isArray(models) ? models : [];
      session.recent = ids(recent);
      session.favorites = readFavorites(session.models);
      render();
    } catch (error) {
      if (opened !== session) return;
      console.error(error);
      session.refs.list.replaceChildren(h("div", { class: "catalog-empty" },
        h("p", {}, "モデルの一覧を読み込めませんでした"),
        h("p", { class: "catalog-error" }, text(error?.message, "時間をおいて開き直してください")),
      ));
      session.refs.live.textContent = "一覧を読み込めませんでした";
    }
  }

  store?.on?.("change:model", () => { if (opened) render(); });
  return { open, close, isOpen: () => !!opened };
}
