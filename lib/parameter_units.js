// Presentation only. Raw parameter values sent to Blender remain unchanged.
function sourceUnit(text) {
  const head = String(text).slice(0, 2500);
  const candidates = [
    ...head.matchAll(/単位(?:はすべて)?\s*[:：]?\s*(mm|m)(?=$|[\s）).。/])/g),
    ...head.matchAll(/[（(](mm|m)[）)]/g),
  ].sort((a, b) => a.index - b.index);
  if (candidates.length) return candidates[0][1];
  if (/meters|メートル/.test(head)) return "m";
  return null;
}
function decorateControls(controls, text) {
  const baseUnit = sourceUnit(text);
  return controls.map((c) => {
    const label = c.label || "";
    const angle = /(?:度|°|角度|azimuth|elevation)/i.test(label) || /(?:ANGLE|AZIMUTH|ELEVATION)$/.test(c.name);
    const count = /(?:個数|枚数|分割数|解像度|周方向分割|1=|倍率|比率|係数)/.test(label)
      || /(?:_SEG|_SEGS|_SEGMENTS|_COUNT|_SCREWS|_RATIO|_SCALE)$/.test(c.name);
    const length = !angle && !count && (
      /(?:幅|高さ|半径|直径|肉厚|板厚|厚み|長さ|奥行|深さ|径|すき間|隙間|クリアランス|距離|長辺|短辺|半辺|配線逃げ|結合面の微調整)/.test(label)
      || /(?:_W|_H|_D|_R|_T|_DX|_DY|_DZ|_CLR|_GAP|_WIDTH|_HEIGHT|_DEPTH|_THICKNESS|_RADIUS|_LENGTH)$/.test(c.name)
      || /\d\s*mm/.test(label)
    );
    if (angle) return { ...c, unit: "°", displayScale: 1, isInt: false };
    if (length && baseUnit) return { ...c, unit: "mm", displayScale: baseUnit === "m" ? 1000 : 1, isInt: false };
    return { ...c, unit: "", displayScale: 1 };
  });
}
module.exports = { sourceUnit, decorateControls };
