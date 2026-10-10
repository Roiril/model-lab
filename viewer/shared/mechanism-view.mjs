export const MECHANISM_VERTEX_SHADER = `#version 300 es
in vec3 aPos; uniform mat4 uVP; uniform mat4 uM; out vec3 vW;
void main(){ vec4 w = uM * vec4(aPos, 1.0); vW = w.xyz; gl_Position = uVP * w; }`;

export const MECHANISM_FRAGMENT_SHADER = `#version 300 es
precision highp float; in vec3 vW; uniform vec3 uCol; uniform vec3 uEye; uniform float uCutX; uniform float uCut; out vec4 o;
void main(){
  if (uCut > 0.5 && vW.x > uCutX) discard;
  vec3 n = normalize(cross(dFdx(vW), dFdy(vW)));
  if (dot(n, normalize(uEye - vW)) < 0.0) n = -n;
  float d = 0.48 + 0.45 * max(dot(n, normalize(vec3(0.45, 0.75, 1.0))), 0.0) + 0.20 * max(dot(n, normalize(vec3(-0.8, -0.3, 0.35))), 0.0);
  o = vec4(min(uCol * d, vec3(1.0)), 1.0);
}`;

export const MECHANISM_VIEW_CONTROLS = Object.freeze({
  homeAz: -35,
  homeEl: 24,
  fovDeg: 32,
  dragDegPerPixel: 0.4,
  minPitchDeg: -80,
  maxPitchDeg: 85,
  wheelFactor: 0.001,
  referenceDist: 250,
  minDist: 90,
  maxDist: 600,
});

// 単位はmm。C1の実データ assets/mystery-box-sg92r-c1.json のviewを基準にする。
// 他の箱は外形幅に対する比率を保つ。C1の汎用fallback値とは区別する。
export const C1_REFERENCE_VIEW = Object.freeze({
  width: 70,
  centerZ: 35,
  targetZ: 50,
  dist: 300,
  cutX: 14,
});
