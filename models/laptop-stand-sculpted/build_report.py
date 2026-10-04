"""Create a self-contained, source-grounded design report with current evidence."""
import sys,json,base64,html,hashlib,subprocess,os
from io import BytesIO
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'exports/laptop-stand-sculpted'


def figure(path,caption,crop=None):
    assert path.is_file(),str(path)
    image=Image.open(path).convert('RGB')
    if crop:image=image.crop(crop)
    image.thumbnail((1200,1200))
    stream=BytesIO();image.save(stream,format='PNG')
    uri='data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()
    return f'<figure><img src="{uri}" alt="{html.escape(caption)}"><figcaption>{html.escape(caption)}</figcaption></figure>'


def git(*args):
    return subprocess.run(['git',*args],cwd=ROOT,capture_output=True,encoding='utf-8',errors='replace',check=True).stdout


def main():
    validation=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
    compare=json.loads((OUT/'comparison.json').read_text(encoding='utf-8'))
    convergence=json.loads((OUT/'convergence.json').read_text(encoding='utf-8'))
    build=json.loads((OUT/'build.json').read_text(encoding='utf-8'))
    unit=validation['laptop-stand-sculpted-unit.stl']
    pair=validation['laptop-stand-sculpted.stl']
    assert abs(unit['volume_cm3']-build['volume_cm3'])<.001
    stl=ROOT/'exports/laptop-stand-sculpted-unit.stl'
    for name in ['studio-unit.png','studio-pair.png','side.png','reverse.png','top.png','overlay.png','validation.json','comparison.json']:
        assert (OUT/name).stat().st_mtime>=stl.stat().st_mtime,name+' is stale'
    css=Path.home()/'Projects/Web/claude-global/skills/visual-deliverable/assets/report.css'
    styles=css.read_text(encoding='utf-8')
    styles+='\nimg{display:block;width:100%;height:auto} pre{font-family:var(--mono);font-size:var(--fs-xs);white-space:pre-wrap;overflow-wrap:anywhere;max-height:24rem;overflow:auto} details{margin:var(--sp-6) 0} summary{cursor:pointer} td{vertical-align:top} .pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--sp-4)} @media(max-width:600px){.pair{grid-template-columns:1fr}}'
    dims=' × '.join(f'{v:.1f}' for v in unit['dimensions_mm'])
    pairdims=' × '.join(f'{v:.1f}' for v in pair['dimensions_mm'])
    content=f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>画像から再現したPCスタンド</title><style>{styles}</style></head><body><main class="wrap">
<p class="eyebrow">model-lab · 2026-10-04</p><h1>画像から再現したPCスタンド</h1>
<p class="sub">元画像の輪郭を基準にした造形方法と出力モデル</p>
<div class="lead"><p>長い上面と上向きの先端を再現した。肩から斜めの帯を前足へつなげた。下部には涙形の穴を残した。</p><p>形状はコードから再生成できる。単体の寸法は {dims} mm。実寸と背面は推定。</p></div>
{figure(OUT/'studio-pair.png','出力したSTLの描画。二本の中心間隔は200mm。画像生成した完成予想図ではない。')}
<h2>1. 元画像と再現モデル</h2><div class="pair">
{figure(HERE/'design/original.png','元画像の前景左。大きな単体を主な基準にした。',(50,195,710,870))}
{figure(OUT/'studio-unit.png','同じ方向を向けたSTL。見えない奥行きの曲率は推定。')}
</div><p>細いレールと厚い胴体を分けた。平らな接触面を保ちながら、下部を連続した曲面にした。</p>
<h2>2. 参考画像の具体化</h2>
{figure(HERE/'design/isolated.png','画像生成による単体の推定画像。肩と前足の流れを読むために使用。')}
{figure(HERE/'design/views-inferred.png','画像生成による別方向の推定画像。裏面と横幅はこの画像だけでは確定できない。')}
<p>生成画像の側面では上面が傾いている。元画像の大きな単体では、上面と接地線がほぼ平行に見える。この差は生成画像の解釈として扱った。上面は水平にした。</p>
<h2>3. 輪郭の特徴をコードで表す</h2><div class="tblwrap"><table><thead><tr><th>元画像の特徴</th><th>再現方法</th></tr></thead><tbody>
<tr><td>細く長い上面</td><td>幅24mm。厚み5mm。端を丸めた断面を水平に並べる。</td></tr>
<tr><td>上向きに返った先端</td><td>最後の17mmで滑らかに上げる。立ち上がりは6mm。</td></tr>
<tr><td>C字にくぼむ肩</td><td>側面の外周に凹みを記録する。肩を別部材で貼り付けない。</td></tr>
<tr><td>斜めの帯から広がる前足</td><td>外周の曲線をつなぐ。横幅は前足へ徐々に広げる。</td></tr>
<tr><td>涙形の下部の穴</td><td>外周とは独立した閉じた曲線で定義する。</td></tr>
<tr><td>薄く連続した接地部分</td><td>形状をZ=0で切る。底面の接触面積も数値で確認する。</td></tr>
</tbody></table></div>
<h2>4. 曲面を作る手順</h2>
<p>側面の外周と穴から、肉がある領域を決める。その内部で、境界から滑らかに増える値を計算する。肩と足の幅を少数の値で決める。輪郭付近では横幅を連続的にゼロへ近づける。</p>
<p>格子と輪郭の距離を境界条件に入れた。表面は格子を四面体へ分けて取り出した。底面を平らにしてから上レールを結合した。</p>
<details><summary>数式と実装の参照先</summary><p>側面領域内で −Δu = 1。境界で u = 0。横半幅 h = W(y,z)√(u/(u+c))。c = 10mm²。Wは肩と前足へ滑らかに変化する。</p><p>輪郭と寸法は params.py。厚みは poisson_body.py。面の生成は surface.py。上レールと結合は model.py。</p><p>外周と穴を一点ずつ対応させる断面では、C字の肩を作ると対応が折れる場合があった。独立した二つの境界を扱う方法を採用した。</p></details>
<div class="pair">{figure(OUT/'side.png','STLの側面。水平の上面と上向きの先端。')}{figure(OUT/'reverse.png','STLの裏側。前足と戻り柱の接続を確認。')}</div>
{figure(OUT/'top.png','STLの上面。細い上レールと足の横幅。')}
<h2>5. 元画像との比較と検証</h2>
{figure(OUT/'overlay.png','橙は元画像の輪郭だけにある部分。青はSTLの投影だけにある部分。色の無い部分は一致。')}
<p>元画像の前景左を手で記録した輪郭と比較した。カメラは方位54°と仰角12°に固定した。同じ高さに合わせる等倍の縮尺を使った。縦横を別々に引き伸ばしていない。</p>
<div class="tblwrap"><table><tbody>
<tr><th>輪郭の重なり率</th><td>{compare['silhouette_iou']*100:.2f}%。二つの面積の共通部分を全体の面積で割る値。</td></tr>
<tr><th>輪郭間の平均距離</th><td>{compare['mean_contour_distance_original_px']:.2f}px。元画像の大きさで測定。</td></tr>
<tr><th>輪郭距離の95パーセンタイル</th><td>{compare['p95_contour_distance_original_px']:.2f}px。手動記録には約3pxの誤差がある。</td></tr>
<tr><th>単体の閉じ方</th><td>{unit['components']}個の連結した形。非多様体辺 {unit['non_manifold_edges']}。面積ゼロの三角形 {unit['zero_area_triangles']}。</td></tr>
<tr><th>面の交差</th><td>1µmを超える交差深さの候補 {validation['surface']['intersection_check']['above_1_micron']}。</td></tr>
<tr><th>計算間隔を細かくした差</th><td>0.5mm → 0.25mm。胴体の体積差 {convergence['body_volume_relative_difference']*100:.3f}%。横半幅の最大差 {convergence['transverse_radius_difference_max_mm']:.3f}mm。</td></tr>
<tr><th>形状を滑らかにした変位</th><td>平均 {build['thickness_field']['mean_smoothing_shift_mm']:.3f}mm。最大 {build['thickness_field']['max_smoothing_shift_mm']:.3f}mm。</td></tr>
<tr><th>面数を減らした変位</th><td>標本での最大 {build['thickness_field']['simplification_max_sampled_deviation_mm']:.3f}mm。</td></tr>
</tbody></table></div>
<p>検査には、通る正常形状と止まる異常形状を先に流した。検証は生成スクリプトの返事だけで判断せず、出力STLの三角形を直接読んだ。</p>
<h2>6. 出力と残る推定</h2><p>単体: {dims} mm。二本を配置した全体: {pairdims} mm。PCを置く高さ145mm。単体の体積 {unit['volume_cm3']:.2f}cm³。</p>
<p>単体STLを二本使う形。左右の距離はPCに合わせて動かせる。画像には実測寸法が無いため、サイズは再現用に設定した。</p>
<p>内周付近には小さな陰影が残る。背面の曲率と横幅は推定。輪郭が一致しても、見えない形が一致した証明にはならない。荷重試験と実機での滑り止め確認は未実施。</p>
<p><a href="http://localhost:3000/?model=laptop-stand-sculpted">3Dビューワーで回転して見る</a></p>
<details><summary>検証対象とGitの記録</summary><p>単体STLのSHA-256</p><pre>{hashlib.sha256(stl.read_bytes()).hexdigest()}</pre>
<p>git status --short</p><pre>{html.escape(git('status','--short'))}</pre><p>git diff --stat</p><pre>{html.escape(git('diff','--stat'))}</pre>
<p>git log --oneline -3</p><pre>{html.escape(git('log','--oneline','-3'))}</pre></details>
</main></body></html>'''
    target=OUT/'design-report.html';temp=target.with_suffix('.tmp')
    temp.write_text(content,encoding='utf-8',newline='\n');os.replace(temp,target)
    print(json.dumps({'report':str(target),'bytes':target.stat().st_size,'iou':compare['silhouette_iou']}))


if __name__=='__main__':main()
