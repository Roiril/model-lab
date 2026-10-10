export function requestTitle(request) {
  const message = String(request?.message || "").split(/\r?\n/).find((line) => line.trim());
  if (message) return message.trim();
  const note = (request?.items || []).map((item) => String(item?.note || "").trim()).find(Boolean);
  return note || "";
}

export function requestDetailUrl(request) {
  if (!request?.model || !request?.id) return null;
  return `/requests/${encodeURIComponent(request.model)}/${encodeURIComponent(request.id)}/request.json`;
}

export function requestShapeDetails(request) {
  const details = [];
  for (const item of request?.items || []) {
    if (item?.type !== "section") continue;
    for (const shape of item.shapes || []) {
      const note = String(shape?.note || "").trim();
      const text = String(shape?.text || "").trim();
      if (!note && !text) continue;
      details.push({ kind: String(shape?.kind || "shape"), name: String(shape?.name || ""), note, text });
    }
  }
  return details;
}

export function requestImages(request) {
  const images = request?.images || [];
  const view = images.find((url) => /(?:^|\/)view\.png(?:\?|$)/i.test(url)) || null;
  const sections = new Map();
  for (const url of images) {
    const match = url.match(/(?:^|\/)section-(\d+)\.png(?:\?|$)/i);
    if (match) sections.set(Number(match[1]), url);
  }
  let sectionIndex = 0;
  const items = (request?.items || []).map((item) => ({
    ...item,
    image: item?.type === "section" ? (sections.get(++sectionIndex) || null) : null,
  }));
  for (const item of items) {
    if (item.image) item.svg = images.find((url) => url === item.image.replace(/\.png(?:\?|$)/i, ".svg")) || null;
  }
  return { view, items };
}
