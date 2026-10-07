// 下書きの指示を、サーバーへ送る 1 つの依頼（request.json の元 + 画像）にまとめる。
// 形は tools/request.example.json。座標の変換は frames.js だけで行う。

import { uvToModel } from "./frames.js";
import { sampleShape } from "./sketch.js";

const POLYLINE_STEP = 0.5; // mm

function clone(x) { return JSON.parse(JSON.stringify(x)); }

function meshFileInfo(mesh, fileInfos) {
  const file = mesh.userData.file;
  const unitScale = mesh.userData.unitScale ?? 1;
  let bbox = mesh.userData.bbox || null;
  if (!bbox && mesh.geometry) {
    if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
    const b = mesh.geometry.boundingBox;
    if (b) {
      bbox = {
        min: [b.min.x * unitScale, b.min.y * unitScale, b.min.z * unitScale],
        max: [b.max.x * unitScale, b.max.y * unitScale, b.max.z * unitScale],
      };
    }
  }
  const placed = mesh.userData.placed ?? /print|plate|split/i.test(file || "");
  const info = fileInfos.find((f) => f.name === file);
  return { file, unitScale, bbox, placed: !!placed, mtime: info ? info.mtime : null };
}

// 戻り値: { request, images } | null（指示もメッセージも無いときは送らないので null）
export async function buildRequest({ store, viewport, sections, sketch }) {
  const draft = store.state.draft;
  const message = (draft.message || "").trim();
  if (!draft.items.length && !message) return null;

  const images = {};
  const fileInfos = store.state.files || [];
  const files = viewport.getMeshes().map((m) => meshFileInfo(m, fileInfos));

  // 3D の見た目（指示の重ね描き込み）
  try {
    images["view.png"] = viewport.screenshot();
  } catch (e) {
    console.error("[bundle] 3D の画像を作れませんでした", e);
    store.status("3D の画像を付けられませんでした。指示だけ送ります", "err");
  }

  const round2 = (p) => p.map((x) => Math.round(x * 100) / 100);
  const items = [];
  let sectionNo = 0;
  for (const src of draft.items) {
    const it = clone(src);
    delete it.faceIds; // ビューワー内だけで使う。要約（summary）だけを送る

    if (it.type === "section") {
      sectionNo += 1;
      // getLoops は {loops, ghostLoops, bounds}。送るのは依頼時の輪郭だけ（0.01mm に丸めて軽くする）
      const sliced = sections ? sections.getLoops(it.id) : null;
      it.loops = ((sliced && sliced.loops) || []).map((lp) => ({ ...lp, points: lp.points.map(round2) }));
      const plane = it.plane;
      const offset = it.offset || 0;
      for (const shape of it.shapes || []) {
        try {
          shape.polyline = sampleShape(shape, POLYLINE_STEP).map(round2);
          shape.polyline3d = shape.polyline.map((p) => round2(uvToModel(plane, offset, p)));
        } catch (e) {
          console.error("[bundle] 図形を折れ線にできませんでした", shape, e);
          shape.polyline = [];
          shape.polyline3d = [];
        }
      }
      const png = `section-${sectionNo}.png`;
      const svg = `section-${sectionNo}.svg`;
      try {
        images[png] = await sketch.exportPNG(it.id);
        it.image = png;
      } catch (e) {
        console.error("[bundle] 断面の PNG を作れませんでした", e);
      }
      try {
        images[svg] = sketch.exportSVG(it.id);
        it.svg = svg;
      } catch (e) {
        console.error("[bundle] 断面の SVG を作れませんでした", e);
      }
    }
    items.push(it);
  }

  const request = {
    model: store.state.model,
    message,
    frame: store.state.frame,
    files,
    camera: viewport.cameraInfo(),
    images: Object.keys(images),
    items,
  };
  return { request, images };
}
