import {BufferGeometry,Float32BufferAttribute} from './vendor/three.module.js';
// 描画用だけに三角形の頂点を分け、隣り合う面の法線を平均しない。
// 元CADの頂点、三角形、配置は変更しない。
export function meshGeometry(part,center){
  const indexed=new BufferGeometry();
  indexed.setAttribute('position',new Float32BufferAttribute(part.vertices.map((n,i)=>n-center[i%3]),3));
  indexed.setIndex(part.indices);
  const geometry=indexed.toNonIndexed();indexed.dispose();
  geometry.computeVertexNormals();
  return geometry;
}
