"""Japanese self-contained guide and dimension/operation figures, frozen B3."""
from pathlib import Path
import base64,json,hashlib,html,shutil,struct
import numpy as np
R=Path(__file__).resolve().parent;D=R/'docs';D.mkdir(exist_ok=True)
SHA=hashlib.sha256((R/'editable_cube_B3.blend').read_bytes()).hexdigest()
assert SHA=='1ababb93dba4ef81368ba7767d3b13f180b4e43a407c336acef9d6a9150ac4c6'
def data(p):
 p=Path(p);return 'data:'+('image/svg+xml' if p.suffix=='.svg' else 'image/png')+';base64,'+base64.b64encode(p.read_bytes()).decode()
def fig(p,caption):return f'<figure><img src="{data(p)}" alt="{html.escape(caption)}"><figcaption>{caption}</figcaption></figure>'
def svg_start(w=240,h=176):return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#ffffff"/><g font-family="Arial, Meiryo, sans-serif" font-size="3.2" fill="#222222">']
def txt(s,x,y,t,size=3.2):s.append(f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(t)}</text>')
def line(s,a,b,col='#222222',sw=.3):s.append(f'<path d="M{a[0]:.3f},{a[1]:.3f} L{b[0]:.3f},{b[1]:.3f}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
def save(s,name):
 p=D/name;p.write_text(''.join(s)+'</g></svg>',encoding='utf8');return p
def img(s,p,x,y,w,h):s.append(f'<image href="{data(p)}" x="{x}" y="{y}" width="{w}" height="{h}"/>')
# Dimension photograph-style callouts use actual camera-projected endpoints.
s=svg_start();txt(s,5,7,'B3設計・印刷用候補 / 閉じた外形',4)
img(s,R/'preview_closed.png',5,10,190,139.333)
pts=json.loads((R/'camera_projected_dimensions.json').read_text())
def cp(v):return [5+v[0]*190/1500,10+v[1]*190/1500]
for kind,label in [('width','70 mm'),('depth','70 mm'),('height','70 mm')]:
 a,b=cp(pts[kind+'_start']),cp(pts[kind+'_end']);line(s,a,b)
 for p in [a,b]:line(s,[p[0]-1,p[1]-1.7],[p[0]+1,p[1]+1.7])
 if kind=='width':txt(s,(a[0]+b[0])/2-5,(a[1]+b[1])/2+7,label)
 elif kind=='depth':txt(s,(a[0]+b[0])/2+3,(a[1]+b[1])/2+5,label)
 else:txt(s,a[0]+4,(a[1]+b[1])/2,label)
txt(s,5,164,'壁・蓋スキン 2.4 mm / 軽い蓋03 約10.0 g（均一PLA換算）')
txt(s,5,171,'SG92R付属ホーンを使用 / スピーカー予約 Ø25 × H10 mm / 実機未検証')
dim=save(s,'B3_dimensions.svg')
s=svg_start();txt(s,5,7,'底の操作 — 通常の分解では22を解除しない',4)
img(s,R/'preview_bottom.png',5,15,113,77.688)
txt(s,5,101,'底の部分拡大。外周は表示範囲外。')
txt(s,124,20,'13 橙：本体キー')
txt(s,124,27,'20 青緑：短いボルト')
txt(s,124,34,'22 灰：キャップの独立止め')
line(s,[124,41],[232,41],'#aaaaaa')
txt(s,124,49,'通常のカセット取り出し')
txt(s,124,57,'① 20を +Z 1.8 mm 押す')
txt(s,124,65,'② 20を +X 5.9 mm 移す')
txt(s,124,73,'③ 横力を抜き、1.8 mm 下げる')
txt(s,124,81,'④ 13を +90° 回す → 下へ抜く')
txt(s,124,89,'⑤ 固定部を支え、ユニットを上へ')
txt(s,5,115,'LOCKの成立：13が0°、かつ20が左・下のL位置。20の半端位置は不合格。')
txt(s,5,124,'復帰：13を挿入して0° → 20を1.8 mm押し上げ → −X 5.9 mm → 下げる。')
txt(s,5,139,'22の初期組立・交換だけ：+Z 1.8 mm → 90°回転 → 下へ15 mm抜く。')
txt(s,5,148,'引っ掛かり、戻らない、欠け、割れがあれば中止。工具でこじらない。')
txt(s,5,162,'+Zは箱の内側、+Xは図の左向き。蓋とリンクを持ち上げ用の取っ手にしない。')
txt(s,5,171,'実物の重力戻り・指の入りやすさ・振動保持は未確認。必ず試験片から確認する。')
operation=save(s,'B3_bottom_operation.svg')
# Actual triangle-plane sections, manually clipped to the drawing bounds.
s=svg_start();txt(s,5,7,'B3の保持断面 — 最新CADの三角形と断面平面の交線',4)
sections=json.loads((R/'actual_sections.json').read_text())['plane_sections'];colors={'01_body':'#777777','13_body_cross_key':'#e69f00','20_short_body_bolt':'#0072b2','21_separate_bolt_cap':'#222222','22_symmetric_cap_stop':'#444444'}
def clipped(a,b,lo,hi):
 a=np.array(a,float);b=np.array(b,float);v=b-a;t0=0;t1=1
 for k in range(2):
  if abs(v[k])<1e-10:
   if a[k]<lo[k] or a[k]>hi[k]:return
  else:
   q0=(lo[k]-a[k])/v[k];q1=(hi[k]-a[k])/v[k];t0=max(t0,min(q0,q1));t1=min(t1,max(q0,q1))
 if t1<t0:return
 return a+t0*v,a+t1*v
for y,lo,hi,x0 in [('26.5',(30,0),(51,18),8),('12.5',(40,0),(64,19),125)]:
 txt(s,x0,18,'キー/ボルト Y26.5 mm' if y=='26.5' else '独立止め/キャップ Y12.5 mm')
 for n,segments in sections[y].items():
  for a,b in segments:
   pair=clipped(a,b,lo,hi)
   if pair:
    aa,bb=pair;line(s,[x0+(aa[0]-lo[0])*4,108-(aa[1]-lo[1])*4],[x0+(bb[0]-lo[0])*4,108-(bb[1]-lo[1])*4],colors[n],.28)
txt(s,8,119,'20：足の高さ 1.6 mm / 押上げ 1.8 mm')
txt(s,125,119,'22：耳の厚さ 2.0 mm / 襟の厚さ 1.2 mm')
txt(s,8,128,'通常時のキー鼻の重なり：約1.96 mm※')
txt(s,125,128,'21：板厚1.8 mm / 22上昇時の隙間0.2 mm')
for i,(n,col) in enumerate(colors.items()):
 x=7+i*46;line(s,[x,142],[x+6,142],col,.6);txt(s,x+8,143,n[:2])
txt(s,5,158,'※キーXY半径0.339 mmと仮定した遊びの条件下。公差全自由度の保証ではない。')
txt(s,5,168,'押上げ量は20・22とも1.8 mm。小さい足が欠けると保持条件が失われる。')
retention=save(s,'B3_actual_retention_sections.svg')
s=svg_start();txt(s,5,7,'底を開けた作業台 — 台の位置は仮定、安定性は実物で確認',4)
# To scale front XZ projection, assumed bench blocks shown cropped laterally.
sc=1.1;x=lambda v:80+v*sc;z=lambda v:36-v*sc
for xa,xb in [(-45,3),(67,112)]:s.append(f'<rect x="{x(xa)}" y="{z(0)}" width="{(xb-xa)*sc}" height="110" fill="#cccccc" stroke="#777777" stroke-width=".3"/>')
s.append(f'<rect x="{x(0)}" y="{z(70)}" width="77" height="77" fill="none" stroke="#222222" stroke-width=".4"/>') # box extends above frame; replace immediately
s[-1]=f'<rect x="{x(0)}" y="{12}" width="77" height="24" fill="#eeeeee" stroke="#222222" stroke-width=".4"/>'
txt(s,84,26,'70 mm箱（高さを省略）')
line(s,[x(3),48],[x(67),48]);txt(s,100,55,'中央の開き 64 mm')
line(s,[x(34),60],[x(34),130]);txt(s,122,100,'工具空間 ≥85 mm')
txt(s,122,109,'図の台高さ：100 mm')
txt(s,5,154,'接触は底外縁 X0..3 / X67..70 mmだけ。前後は箱より広い安定した台を使う。')
txt(s,5,163,'台を動かない配置にして滑り・傾きを確認。底の可動部・キーに台を当てない。')
txt(s,5,172,'細い3 mmの位置合わせが難しい場合は作業を中止。手のアクセスと転倒は未検証。')
bench=save(s,'B3_bench_support.svg')
old=R.parent/'sg92r_v6_revision3_20261008'
for n in ['step_01_rear_frame.png','step_02_local_capture.png','step_03_lid_front_entry.png','step_04_complete_cassette.png']:shutil.copy2(old/n,D/n)
names=['箱本体','固定後部カバー','軽い平面蓋','主カセット','前側閉じ板','ホーンカップ・ジャーナル','後側ロッカー','前側ロッカー','リンク','ヒンジ軸','駆動軸','リンク軸','底の本体キー','サーボ上押さえ','前側スペーサー','後側スペーサー','局所カップ保持板','前側保持止め','後側保持止め','短い本体ボルト','独立ボルトキャップ','対称キャップ止め']
man=json.loads((R/'assembly_manifest.json').read_text());partrows=''.join('<tr><td>'+p['name']+'</td><td>'+names[i]+'</td><td>'+' × '.join(f'{v:.2f}' for v in p['print_bounds_mm'])+'</td><td>1</td></tr>' for i,p in enumerate(man['parts']))
plates=json.loads((R/'plate_manifest.json').read_text());platerows=''.join(f'<tr><td>{p["plate"]}</td><td>{", ".join("test_"+x["name"].split("_")[1] if x["name"].startswith("test_") else x["name"].split("_")[0] for x in p["parts"])}</td><td>{"04/06相当のみ手動支持" if p["manual_support"] else "支持なし"}</td><td>{p["occupied_mm"][0]:.1f} × {p["occupied_mm"][1]:.1f}</td></tr>' for p in plates)
rootlines=R/'slice_root_lines.svg';q=rootlines.read_text(encoding='utf8')
for a,b in [('#fbfbf8','#ffffff'),('#20313d','#222222'),('#d3dbe0','#cccccc'),('#1d667b','#0072b2'),('#bf7139','#d55e00'),('font-size:5px','font-size:4px')]:q=q.replace(a,b)
rootlines.write_text(q,encoding='utf8')
css=Path(r'C:\Users\kouga\.agents\skills\visual-deliverable\assets\report.css').read_text(encoding='utf8')
body=f'''<header><p class="eyebrow">住人の箱 / B3-integrated-3 / 2026-10-08</p><h1>試験片から進める<br>設計・印刷用候補</h1><p>70 × 70 × 70 mm。SG92Rと付属ホーンで軽い蓋をゆっくり開く物理デモ。主機構22部品。会話や謎解きソフトは含みません。</p><p><strong>デジタルの設計レビュー済み。実物の印刷、嵌合、通電、重力戻り、振動・強度は未検証です。</strong> 本体をまとめて印刷する前に、下記の試験片で合否を確認してください。</p></header>
{fig(R/'preview_open65.png','全体の65°開蓋プレビュー。実写ではなく最新CADのレンダリング。')}
<h2>寸法と必要な物</h2>{fig(dim,'閉じた外形70 mm角。開蓋時は高さが増えるため、上の空間を空ける。')}
<p>壁と蓋スキン2.4 mm。03の換算質量約10.0 g。移動する蓋・ロッカー・軸12の合計約13.4 g。クランク半径14 mm、リンク中心間29.259 mm。蓋0..65°で、設計上のサーボ角は−10..55.578°（ストローク65.578°）。この角度は実機の制御パルスではありません。</p>
<p>印刷以外に、確認済み形状のSG92R本体、対応する付属ホーン、制御基板、実物の定格に合う独立サーボ電源、配線・接続器具が必要です。任意の小型スピーカーはØ25 × H10 mmを予約しています。接着剤や金属軸・ねじ・ばねを前提としない設計ですが、実物でねじなしホーン保持が成立するかは試験が必要です。</p>
<p>正本はユーザー確認の <code>model-lab/models/sg92r-photo</code>。参照CADの胴23 × 12 × 22 mm、取付耳全長32 mm、穴中心間28.84 mm、付属ホーンの長腕範囲−18..+16 mm。メーカーの最新寸法を再調査した値ではありません。互換品・SG90への交換を保証しません。付属ホーンを使い、独自スプラインを印刷したり無理に圧入したりしないでください。</p>
<h2>最初は必要な試験片だけ</h2>
<p>00の3MFは全7点の配置例です。まず段階Aだけを選択して印刷できます。00全点と04全点の同時印刷を必須にしていません。</p>
<table><thead><tr><th>順</th><th>選ぶ試験片</th><th>合格条件 / 進めない条件</th></tr></thead><tbody>
<tr><td>A / 実物部品</td><td>01 servo_cradle、02 actual_horn_pocketの2点</td><td>手持ちSG92Rが台座に上から入り、付属ホーンがポケットへ軽く入る。押し込み・削ってスプラインを合わせる必要があれば不合格。ケース後部の停止位置と耳・配線の逃げも確認。</td></tr>
<tr><td>B / 底の操作</td><td>30 local_bottom_lock、33 actual_key、40 actual_bolt、41 actual_cap、42 actual_stopの5点</td><td>30は50 × 48 × 18 mmの実際の底切り出し。20/22の押上げ1.8 mmと20の横移動5.9 mmを確かめる。横力を抜くと端ポケットまで完全に下がること。途中でLOCKに見える、こじる必要がある、21/22が意図せず抜ける、足が割れる場合は不合格。キーZ遊び−0.3..+0.2 mm・20の仮定遊びを実物で点検。13とカセット足の完全な捕捉は本体仮組みで別確認。</td></tr>
<tr><td>C / 支持材</td><td>25 actual_U_supportを04の前に。26 actual_cup_with_supportは06の支持確認として</td><td>許可面だけから支持が無理なく除去できる。円筒・穴・推力面・ホーン面に溶着や傷がないこと。26は06の実部品そのもの。01/02の嵌合が通った後に進む。除去が難しい場合は本体印刷を止めて再スライス。</td></tr>
</tbody></table>
<p>33/40/41/42と26は本体の13/20/21/22と06へ再利用できます。合格品を二重に印刷する必要はありません。全9点の用途とSHA256は <code>coupon_inventory.json</code> にあります。試験片だけでは全体の強度・振動保持・カセット足の捕捉は合格と判定できません。</p>
<h2>6枚の配置と印刷条件</h2><table><thead><tr><th>200 mm級配置</th><th>部品 / 試験片</th><th>支持</th><th>占有 X × Y mm</th></tr></thead><tbody>{platerows}</tbody></table>
<p>STLはmm、1個ずつ分離済み。配置3MFは200 × 200 mm、占有はいずれも180 mm以内です。保存された向きのまま読み込み、100%で使ってください。実際のベッドとブリム・外周の余裕を確認します。3MFの支持ペイントが読み取られないスライサーでは図を使って手動で指定し、実機用に再スライスしてください。</p>
<p>診断スライスは Bambu Studio 02.03.01.51 / X1 Carbon / 0.4 mmノズル / PLA Basic。層0.2 mm、壁4周、充填20%、上下面5層、象の足補正0.15 mm、ブリム3 mm・隙間0.1 mm。実際のプリンターは未指定なので、そのまま使える実機設定ではありません。付属JSONは再現用の診断設定です。機種固有G-codeは収録していません。</p>
<p>01は底をベッドへ。02/03は外観の平面をベッドへ。04は背面側を下にした既定向き、06はジャーナル端を下にした既定向き。軸10/11/12と14..19は保存された平らな面を下に置きます。20/21/22は既定向きで支持なしです。自動回転・自動全支持を使う前に、機能面の向きが変わっていないか確認してください。</p>
<h3>支持材を許す面 / 保護する面</h3>
<div class="grid">{fig(R/'support_04_under.png','04：橙のU受け背面だけに支持を付ける。機能の推力面は反対側で保護。')}{fig(R/'support_04_top.png','04：青緑は支持柱の着地点。ケース位置決め面から2.3 mm奥の凹み。')}{fig(R/'support_06_under.png','06：橙の外側パッドに支持。灰色のジャーナル・保持環・穴は保護。')}{fig(R/'support_06_top.png','06：ホーンポケットと上側の機能面を保護。先に支持を外してからホーンを入れる。')}</div>
<p>04の強制指定は印刷Z27.3 mmの下向き面。柱が着くのはZ2.7の凹み、Z5.0の配線側ランド、Z8.4の配線端面です。実物のケースを止める面、押さえ溝、軸受、前側推力面へ支持を付けません。06の強制指定は印刷Z11.5 mmの外側パッド。機能の保持環R6.3..8.5 mmを避け、使わない外側遷移帯R8.65 mm以外へ着地させません。25/26は同じ対応面。05と他の部品は全支持禁止または支持なしです。</p>
<p>手動支持は上下面のZ隙間0.2 mm、XY隙間0.35 mm、独立支持層高を無効にした診断条件。ベッド限定を外し、図の凹んだ非機能面への柱の着地を許可しています。02/03の外観面、滑動部、軸受・ホーン面、保持の足・溝に支持を付けないでください。</p>
<p>最終の実スライスで04/05/06、別配置25/26の支持・界面・遷移経路を0.1 mm以下で検査し、公称ビードと保護面の交差を検出していません。06では界面が保持環の下へ投影される箇所があり、公称縦隙間の最小は約0.5 mmでした。熱変形・垂れ・溶着は検証できていません。外観01/02/03は支持経路なし。実機で再スライスした後にも同じ確認が必要です。</p>
<p>除去は電子部品の組込み前。04の支持柱は3..5 mmほどに分割して開いた台座の上または配線側から取り出します。06の輪状支持は2片以上に分割し、R10 mmより外へ剥がします。軸受・推力面・ホーン面をてこにしません。溶着していれば中止して設定を調整します。取り外し操作の力・工具アクセスは実物未確認です。</p>
<div class="grid">{''.join(fig(R/'print_qa'/(p['plate']+'_top_1.png'),p['plate']+' / 実際の診断スライスの上面プレビュー') for p in plates)}</div>
<h2>組立 — 電源を切ったまま</h2>
<p>Xはカセットの前後板を結ぶ軸、+Zは箱の上です。位置は正本CADの全体座標。工程写真の02..19の形状は旧修正3と同一で、底の新しい13/20/21/22は下のB3図に従います。旧版の底パーツを混ぜないでください。</p>
<h3>1 / 空の箱へ底の保持部を入れる</h3>{fig(R/'preview_local.png','最新B3の局所切り出し。橙13、青緑20、灰21/22。外壁の一部は説明のため非表示。')}
<ol><li>箱内部が空の状態で20を上から入れる。基準に対しX−1、Y+1.6、Z+20 mmからZ+3.7 mmまで下げ、Yを0へ戻し、Xを0へ戻してからZを0へ下げる。これはデジタルで確認した挿入の一例。台座を無理に押し広げない。</li><li>21をX+6.8 mmから基準位置へ横に滑らせる。右側内壁までの公称余裕は0.6 mm。箱の外側から押し込む工程ではない。</li><li>22を90°向きで下から挿入。1.8 mm押し上げて0°へ回し、1.8 mm下げる。耳が厚さ1.2 mmの襟に捕捉され、意図せず下へ抜けないことを確認。21が浮いたり横に抜けたりしないことも確認する。</li></ol>
{fig(retention,'断面は実際の最新CAD。色は部品13/20/21/22の区別にだけ用いる。')}
<h3>2 / 箱の外でカセットを作る</h3>
<div class="grid">{fig(D/'step_01_rear_frame.png','a / 04と15/16の剛体枠。前側からスペーサーを入れる。')}{fig(D/'step_02_local_capture.png','b / 06と独立保持17/18/19。既定の局所保持は省略しない。')}{fig(D/'step_03_lid_front_entry.png','c / 03を前側から差す。屋根の一体突起を捕捉する。')}{fig(D/'step_04_complete_cassette.png','d / 02・05を閉じたカセット。配線は無理なく案内する。')}</div>
<ol><li>04へ15/16を+X側から差し、SG92Rを上から置く。配線を台座の出口へ逃がす。</li><li>付属ホーンを実物のサーボ軸へ装着。歯形の適合は実物で確認。ホーンの位相と制御の対応は後で無負荷で校正する。06を+X側からホーンへかぶせる。軸を力で逆駆動しない。</li><li>17を+X側から置き、18と19を上から入れる。14を+X側から入れ、サーボ上部を押さえる。金属のホーン中心ねじを使わない前提なので、17/18/19を抜いたまま動かさない。</li><li>10を後側ヒンジ穴に置く。07を通し、12で09をつなぎ、11を06と09へ入れる。03を+Y側から差し、08の一体屋根突起を+X側から入れて捕捉する。</li><li>02を+X側から入れ、05を同じ側から閉じる。全ての軸・スペーサー・14・18/19が両板に捕捉されていることを確認。支持を除去した穴で軸が指で軽く動くこと。</li></ol>
<h3>3 / スピーカーと配線、箱への取り付け</h3>
<p>スピーカー予約は中心X17 / Y45、底Z2.9 mmのØ25 × H10 mm。端子は6 × 4 × 3 mmの仮定領域、線はØ2 mm想定をØ2.2 mmで検査。曲げ半径のサンプル最小18.65 mm。実物の端子位置、固定方法、束の太さ、張力止めは未確定です。型番に合わせて調整し、保持キーの掃引範囲へ線を入れないでください。滑らかな案内だけでは張力止めになりません。</p>
<ol><li>蓋を閉じて支え、20をR（横へ5.9 mm移動して下がった状態）にする。13は取り外したまま。</li><li>固定カバー02とカセット04/05の剛体部分を持ち、組立済みユニットを垂直に下ろす。01側の受けに足が完全に入ることを確認。移動する蓋03やリンク09を取っ手にしない。</li><li>13を90°向きで下から挿入し0°へ回す。20を1.8 mm押し上げ、−Xへ5.9 mm戻し、横力を抜いて1.8 mm下げる。13=0°かつ20=L・下をLOCKとする。半端位置・単に蓋が閉じている状態はLOCKではない。</li><li>通電前に安全な手動確認。ホーンをサーボから外した独立機構で0..65°の可動を試し、サーボを接続した後は無理に歯車を逆駆動しない。蓋の端・リンク・キーに線が触れず、剛体捕捉が成立することを確認する。</li></ol>
<h2>分解と支え方</h2>{fig(operation,'通常の分解は20→13。22は独立して箱に残し、21を捕捉したままにする。')}
{fig(R/'preview_support.png','2台の仮定作業台。箱が安定して支えられることを示す実機試験ではない。')}{fig(bench,'薄い外縁3 mmの位置合わせ、台の滑り・転倒と手のアクセスは実物で確認する。')}
<p>安定した硬い台2つで底の外縁X0..3 / X67..70 mmだけを支えます。中央開口64 mm、底下工具空間85 mm以上（検査の仮定台高さ100 mm）。前後に十分広い台を使い、台が横滑りしないよう置いてから、電源なし・蓋を閉じた状態で傾きや転倒を点検します。キー13や20/22を台に当てません。3 mmの縁に確実に合わせられない場合は、この支え方では作業を進めないでください。指の形状と摩擦・転倒は検査していません。</p>
<ol><li>全電源を切り、配線コネクタを抜く。蓋を閉じて支える。片手で02/04/05の固定部分を支え、可動蓋・リンクを持たない。</li><li>工具で20を+Z1.8 mm、+X5.9 mm、横力を抜いて−Z1.8 mm。端まで下がらない場合は止める。</li><li>13を+90°回して下へ抜く。22は触らない。</li><li>Ø3 mmの押し棒を底からX36.5 / Y16.4へ入れ、剛体ユニットを上へ押す。剛体押し棒との最初の上昇20 mmはデジタル確認済み。持ち直しと手のアクセスは未確認。ユニットの固定部分を受けて持ち上げる。</li><li>箱外で05→02→08→03の順に開く。支持している軸が落ちないよう受ける。14、18/19、17を外してから06、付属ホーン、サーボを取り出す。力をかけて抜かない。</li></ol>
<p>20/21の交換だけならユニットを外して箱内から初期組立の逆順。22を交換する場合だけ、+Z1.8 mm→90°→下へ15 mm。細い工具の仮定断面：20は0.8 × 2.2 mm、13は3 × 0.8 mm、22は1.6 × 0.6 mm、工具軸Ø2.5 mm / 持ち手Ø10 mm。実際の工具と指で無理なく届くかは試験片で確認します。</p>
<h2>ゆっくり開くデモ</h2>
<p><code>slow_open_demo/slow_open_demo.ino</code> は基板未指定の参考コードです。未コンパイル・未駆動。初期値は <code>CALIBRATED=false</code>、パルス値0で動作を無効にしています。実物のボードと電源に合わせ、サーボ単体を無負荷で校正してからホーン位相と蓋の開始位置を合わせます。電源GNDと制御GNDは共通にします。供給電圧・容量・信号ピンは実際の部品の定格に従ってください。</p>
<p>まず端点を避けた約1..63°の蓋範囲で確認します。シリアル <code>a</code>で始動、<code>o</code>開、<code>c</code>閉、<code>x</code>解除。2 μs / 20 msのパルス変化で緩やかに動かす例です。始動時の飛び、閉じ際の接触、うなり・停止を確認して端点を詰めます。低速化はサーボの停止力を制限しません。指を挟む場所に手を置かず、蓋に物を載せません。電源断で蓋が閉じる可能性があります。</p>
<h2>検証済みの範囲 / 実物へ残る範囲</h2>
<table><thead><tr><th>PC上で確認</th><th>この結果から保証できないこと</th></tr></thead><tbody>
<tr><td>22 STL + 9試験片 + 6配置の計62保存メッシュ。正体積、連結1、非多様体辺・ゼロ面積・向きエラーなし。6スライス完了、配置入力の頂点一致も確認。</td><td>印刷の収縮、象の足、層間接着、穴寸法、支持の熱溶着。寸法・LOCK・重力戻りを試験片で確認。</td></tr>
<tr><td>蓋0..65°を0.5°刻み131姿勢。19工程のカセット挿入。通常と初期組立819姿勢、工具334姿勢、押し棒上昇21姿勢に検出干渉なし。</td><td>姿勢間の連続全空間、手と摩擦、サーボ歯形の実嵌合、実際の取り回し。理想軸・理想剛体の検査。</td></tr>
<tr><td>通常負方向の有限体積接触はボルト4.215°、本体4.662°、スピーカー9.585°の順。キーXY半径0.339 mmの43成立始点では先にスピーカーに接触せず、構造接触時の最小隙間1.726 mm。</td><td>キーZとボルトの全遊びを接触順へ同時に入れた全掃引は未実施。XYZ/角度/変形を自由に組み合わせた外力への保証ではない。</td></tr>
<tr><td>仮定したキーZ−0.3..+0.2 mm、XY半径0.339 mm、ボルトX移動5.6 mm・Y±0.3 mm・Z+0.15 mmで2108解除姿勢に検出干渉なし。キャップ/止めの125複合始点のうち5成立始点から3方向の抜けを阻止。</td><td>重力戻り、振動での押上げ/回転、摩耗、任意の複合抜け経路。左右対称の22でも振動保持は証明しない。足が欠けると保持が成立しなくなる。</td></tr>
<tr><td>理想重力の保守上限約0.00701 N·m（0.0714 kgf·cm）。角度は単調でトグルから離れている。</td><td>摩擦・始動・配線抵抗・実サーボ能力は含まない。サーボ定格比較から駆動可と判定した値ではない。</td></tr>
</tbody></table>
<p>20の足根2.0 × 1.6 mm、22の足根2.6 × 1.6 mm以上、01のT受け根1.2 mm、22捕捉襟1.2 mm。診断G-codeの中心線は該当部へ出ていますが、線の本数は有効断面・強度の実測ではありません。衝撃や輸送保持の合格基準は未設定です。</p>
{fig(R/'slice_root_lines.svg','実際の診断G-code中心線。線幅が変わるため、強度や全面充填の証明にしない。')}
<h2>22部品の一覧と編集</h2><table><thead><tr><th>STL名</th><th>用途</th><th>印刷時の外接 X × Y × Z mm</th><th>数</th></tr></thead><tbody>{partrows}</tbody></table>
<p><code>editable_cube_B3.blend</code> はBlender 5.1.1の編集原本。<code>model.py</code> は <code>params.py</code> と同梱ソースから22部品を再構築します。長さパラメータはm。主な項目はSIZE、WALL、LID_SKIN、OPEN_DEG、CRANK_R、FIT、RUNNING、EXCITER_D/H/X/Y、BOLT_LIFT/TRAVEL、STOP22_LIFT。局所の固定座標もソースに残るため、SIZEを変えるだけで全てが追従する汎用スケールモデルではありません。変更後は可動・組立・メッシュ・支持を再検証してください。</p>
<pre>blender --background --python-exit-code 1 --python model.py
blender --background --python-exit-code 1 --python verify_motion.py
blender --background --python-exit-code 1 --python check_local.py
blender --background --python-exit-code 1 --python check_assembly_revision.py
python make_plates.py
python slice_plates.py  # インストール済みBambu Studioで診断のみ</pre>
<p>正式な新候補IDは <code>mystery-box-sg92r-b3-candidate</code>。model-labではケース・ディスプレイ分類から日本語「住人の箱」「B3」で検索できます。旧v6修正3、B2、B3中間資料は保持。新候補の全体STLは表示専用で、印刷は <code>stl/</code> の分離22点を使います。</p>
<footer><p>凍結CAD SHA256: <code>{SHA}</code></p><p>試験片を経て本体へ進める設計・印刷用候補。実物で組める保証、低速による力制限、振動/輸送の安全保持を示す完成品ではありません。</p></footer>'''
doc='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>住人の箱 B3 — 印刷・組立手順</title><style>'+css+'''\nbody{margin:0}.report{max-width:1080px;margin:auto;padding:32px}img{max-width:100%;height:auto}figure{margin:20px 0}figcaption{font-size:.85rem;color:var(--mute)}table{width:100%;border-collapse:collapse;display:block;overflow-x:auto}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}code{overflow-wrap:anywhere}p,li{line-height:1.8}h2{margin-top:64px}h3{margin-top:32px}footer{border-top:1px solid #ccc;margin-top:48px;font-size:.8rem}@media(max-width:650px){.report{padding:18px}.grid{grid-template-columns:1fr}h1{font-size:2rem}td,th{min-width:90px}}@media print{.report{padding:0}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}figure,tr{break-inside:avoid}h2,h3{break-after:avoid}}</style></head><body><main class="report">'''+body+'</main></body></html>'
(R/'B3_print_assembly_guide.html').write_text(doc,encoding='utf8')
inventory=[]
for p in sorted((R/'coupons').glob('*.stl')):
 dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')]);v=np.frombuffer(p.read_bytes(),dtype=dt,offset=84)['v'].reshape(-1,3)
 num=int(p.name.split('_')[1]);inventory.append({'name':p.name,'stage':'A' if num in [1,2] else 'C' if num in [25,26] else 'B','bounds_mm':(v.max(axis=0)-v.min(axis=0)).tolist(),'reusable_part':{26:'06',33:'13',40:'20',41:'21',42:'22'}.get(num),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'unconditional_all_print_required':False})
(R/'coupon_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf8')
(R/'README.md').write_text('# 住人の箱 B3-integrated-3\n\n試験片から進める設計・印刷用候補。70 mm角、SG92R、主機構22点。実物未検証。\n\nまず B3_print_assembly_guide.html をブラウザーで開いてください。STLはmm。\n印刷 stl/、段階的試験片 coupons/、200 mm級の配置 plates/。\n編集原本 editable_cube_B3.blend（Blender5.1.1）。params.py と model.py から再構築可能。\n旧版の底パーツと混ぜないでください。20/22の押上げは共に1.8 mmです。\n付属ホーン使用、独自スプラインや無理な圧入は不可。\n\nG-codeは収録せず、実機に合わせて再スライスします。診断設定JSONはユーザープリンター指定ではありません。\n',encoding='utf8')
(R/'catalog.json').write_text(json.dumps({'schemaVersion':1,'title':'住人の箱 — B3設計・印刷用候補（試験片から）','description':'70mm角・SG92R・22部品。蓋0〜65°。B3-integrated-3、試験片先行、実機未検証。旧v6修正3/B2とは別候補。','categoryId':'cases-displays','projectId':None,'tags':['住人の箱','B3','SG92R','開蓋','試験片','22部品'],'status':'active'},ensure_ascii=False,indent=2),encoding='utf8')
print('FINAL GUIDE',len(doc),'SOURCE',SHA,flush=True)
