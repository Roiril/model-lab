# 流れるS字のPCスタンド

2026-10-03。ユーザーの「巨匠がデザインしたみたいな流れるような滑らかでスマートで曲線美のあるデザイン」を画像生成から探索した。
組み込みのimage_genを使用。CLIは使用していない。

## 生成画像と実装

- `concept-flow-original.png`: 最初の形の探索。高さと上面の傾きは実寸ではない。
- `concept-flow-proportions.png`: 低く長い比率と水平支持へ修正した概念画像。
- 実装は98 mmの本体へ上下各1 mmのパッドを足す。支持高さ100 mm。
- 最大底面は左右の配置で420 × 275 mm。左右同じ形の一体造形を二つ置く。
- 長いS字の支柱と湾曲した後脚を採用する。前側の空間は外へ開く。
- 画像の薄い首と前方の返しは採用しない。上の受けには20 mmの厚みを取る。
- 底面を丸い稜線へ絞る。S字の支えと後脚の付け根は融合後に平滑化する。
- 支柱の付け根へ厚みを持たせる。生成画像は耐荷重や印刷適性の証拠ではない。
- 曲線を守るため内側のサポートを許す。実物の耐荷重は未試験。

## 最初のプロンプト

```text
Use case: product-mockup. Asset type: industrial design concept reference, for a real 3D-printable laptop stand. Visual style first: restrained high-end museum product photography, matte sculptural surfaces, soft diffuse light, clear contour and flowing broad gradients, no glossy highlights or decorative texture. Explore an original, fluid, beautifully proportioned laptop stand as if conceived by a master furniture designer. Treat the silhouette as a continuous flowing ribbon or a wind-carved crescent, with changing thickness and a broad grounded sweep. A single generous organic negative space per side support. The two support bodies are a matched left/right pair; each is a seamless monolith, without a separate pedestal or obvious frame. The surfaces should flow from a low broad planted footprint through curving load-bearing stems into horizontal narrow laptop contact surfaces, so the laptop rests horizontally 100 mm above the desk. For a large laptop approximately 400 mm wide by 330 mm deep and 3–4 kg, overall support footprint approximately 420 by 275 mm. Show intentional asymmetry along each side support's front-to-back silhouette, a confident long curve and refined rounded edges, not a regular triangular cutout. Be inventive within these functions. Show the coherent same concept in two views on one landscape composition: dominant three-quarter view of the bare pair so all the curves can be seen; a smaller side view with a plain unbranded dark laptop resting on it to explain its function. Matte warm ivory stand on a continuous neutral light warm-gray background. No text, no logos, no dimension arrows, no people, no decorative props. Keep all objects entirely in frame. Do not mimic the current two-triangle-window stand, rectangular perforated walls, rigid triangular braces, bulky plinths, or spindly unsafe supports. This is concept art, not a claim of engineering validation.
```

## 比率修正のプロンプト

入力は `concept-flow-original.png`。形のイメージを維持した編集。

```text
Use case: precise-object-edit. This is the design reference for an actual laptop stand. Preserve the sweeping organic S-shaped load-bearing ribbon, flowing rear stem, broad flared planted feet, matte ivory material, seamless connections, large softly edged organic open space and understated studio product photography of the reference image. Correct only its functional proportions and contact surface. Each support must be LOW AND LONG: physical body height 98 mm, front-to-back footprint 275 mm, maximum side-to-side base width 100 mm. Thus each support's true side silhouette is almost three times longer than it is tall. The two bodies support a large 400 x 330 mm laptop with its underside horizontal at 100 mm above the desk. Both top contact strips are perfectly horizontal and flat along their full length, without a raised retaining lip. Keep generous continuous rounded curves and a slender, confident sculptural gesture as the form becomes lower and longer. Do not return to a rectangle with two regular triangle holes. Same scene composition: large bare pair in three-quarter view, smaller complete laptop-in-use side view of the same corrected stand on the right. Neutral background, soft light, no glossy highlights, no labels or text, no dimensions, no logos, no extra objects. This is a functional proportion correction to the same design rather than a new style.
```
