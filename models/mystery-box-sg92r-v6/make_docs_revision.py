"""Japanese revision3 guide and SVG composites of actual CAD renders."""
from pathlib import Path
import json,html,base64,math,subprocess
R=Path(__file__).resolve().parent
D=json.loads((R/'assembly_manifest.json').read_text('utf8'));M=json.loads((R/'mechanics_report.json').read_text('utf8'))
names=['箱本体','後部固定カバー','平板蓋','後板・サーボ台・局所レール','前板・軸受・ストッパー保持棚','付属ホーン用カップ／D12ジャーナル','後ロッカー','前ロッカー／一体ペグ','曲線リンク','H軸 D6×18.9','A軸 D5×15.8','B軸 D5×9.5','底面回転キー','独立サーボ上押さえ','前スペーサー','後スペーサー','局所カップ保持具','前ストッパー','後ストッパー']
partlines='\n'.join(f"{i:02d} {name}：stl/{row['name']}.stl ×1" for i,(name,row) in enumerate(zip(names,D['parts']),1))
guide=f'''見えない住人の箱 — SG92R 開蓋デモ v6 修正3
親レビュー用CAD試作。実物印刷・組立・通電は未実施です。

1. 寸法と条件
本体と閉じた蓋は70×70×70mm。側面は無地でキーの突起や穴を除きました。底面に配線溝とキー用の操作窓があります。底面キーの頭は0.2mm内側に収まります。開閉は0〜65度。承認済みSG92R参照を使う試作で、SG90や互換品がそのまま適合する保証はありません。
サーボの参照はケース23×12×22mm、耳32×12×2mm、穴ピッチ28.84mm、ホーン34×17mm／腕幅1.5mm。写真からの推定と元モデルの値をreferenceに保存しています。新たなメーカー保証値として扱いません。独自スプラインを印刷せず、実サーボと付属ホーンを使用します。実際の歯の掛かり、ハブ・耳・配線・前後遊びを現物で確認してください。

2. 印刷する19部品
stl/はmm単位、印刷姿勢・Z=0を設定済みです。
{partlines}
部品13は厚い横棒と底の角形頭が一体のキーです。04/05にはキーが掛かる足を一体化しました。14〜19は修正2で加えた保持具を継続しています。修正3の部品だけで組み、他の版と混ぜません。
coupons/には28個の実形状試験片、plates/には200mm級ベッド用の5枚の形状3MFがあります。試験片は全てを必ず追加組立する部品ではありません。適合するキー・軸・保持具等は本体へ再利用できます。

3. 追加の物と工具
必要なのはSG92R、付属ホーン、制御基板、適切な外部サーボ電源と配線です。機械部分に市販のばね・結束バンド・ねじ・金属ピンを要求しません。任意の振動スピーカーはD25×H10mm、接着層0.5mmの仮空間を底X17/Y45に確保しました。コーン用バッフル・音孔、基板/アンプ固定、端子や音響の設計は未実施です。
ノギス、先細ピンセット、2mmL字フック2本、キー溝に軽く入る既存の薄い平工具、8mm以上の柔らかい台を使います。仮組中は両板を支えます。仮止め帯を使う場合も常設の機械部材ではありません。キー溝は14×2mm、深さ1.15mmで、工具をてこにして大きな力を掛けません。

4. 試験片と印刷
00は支持無しの26試験片、04は手U受け25とカップ26の支持除去試験です。11は底の実回転座と挿入窓、12は実キー、27/28は左右の保持足です。床座とキーを手で回し、次に両足を含む全カセットを箱に入れて掛かりを確認します。無理な圧入、穴の貫通化、支持面を削って合わせる方法は使いません。
Bambu Studio2.3.1.51、X1 Carbon0.4mm、PLA、0.20mm層、壁4周、上下5層、充填20%をオフライン確認用に選びます。実プリンター用の設定保証ではありません。04/06だけ指定面へ手動支持。独立支持層高は無効、Z間隔0.2、XY0.35mm。保護するのは軸穴・盲穴床・ホーンポケット・保持環・keeper受け等です。底キー座の橋渡し、長いキーと保持足の反り/層強度も試験片から確認します。
25/26で支持を少しずつ割って開いた側へ外し、機能面に工具を当てないでください。06の保護面へ支持の投影が接近するところは約0.5mmの上下間隔です。名目吐出包絡の非交差は、実際の融着・支持除去・表面精度を保証しません。

5. サーボ無しで組立
①後板04を下にし、8mm以上の柔らかい台で支えます。15/16を04へ入れます。
②06を入れ、17を軸方向から両足溝へ入れます。18/19を落として抜け止めを作り、14を入れます。17だけを片足で曲げません。
③H軸10、後ロッカー07、A軸11、リンク09、B軸12を順に入れます。蓋03を前(+Y)から後ロッカーの屋根ペグへ滑らせます。
④前ロッカー08を軸方向から入れ、屋根ペグ・B軸を受けます。カバー02を入れ、05を前から滑らせて軸端、14〜16、18/19、カバーペグを捕捉します。両板を支えて閉状態へ戻します。
⑤完成カセットを箱01のreceiverへ上から下ろします。底の荷重支持パッドと新しい保持足の座りを確かめます。箱を起立させたまま、高さ40mm以上の柔らかい2台で左右端を支え、底中央を空けます。蓋を閉じ、底からキー13を入れます。キーを入れる前の箱を裏返しません。挿入時は横棒をY方向（90度）、底の工具溝もY方向にし、頭が底のくぼみへ届いてから0度まで90度回します。係止時は横棒と工具溝がX方向です。回転端へ軽く当てるだけにします。
底の角形頭と床の肩、横棒と両足が上下の抜けを止めます。キーはばねで戻さず、逆方向の90度回転は手動解除として残します。角度の自動固定、輸送/振動で戻らないことは未検証です。動作中は底キーへ触れず、使用前にX方向の溝と両板の座りを確認します。輸送用のロックとして保証しません。
⑥箱・カバー・05・底キーまで揃え、蓋を支えながら0〜65度へゆっくり手動で往復します。軸の抜け、保持足の浮き、接触、たわみがあれば通電しません。

6. 分解とサーボ校正
電源を切り、箱を同じ2台で水平に支え、底キーを90度へ戻し、下へ抜きます。キー解除後も箱を裏返しません。蓋を約65度で支え、内側から04/05の工具穴Y61.5/Z59.5（対角5）に2mmLフックを差し、両板を一緒に持ち上げます。蓋やリンクだけで持ち上げません。実工具の曲げ・握り・引張り強度は未確認です。
取り出したカセットを後板04が下になる台へ戻してから05を外します。軸を受け皿へ回収し、取付の逆順で分解します。裸のカセットを裏返しません。
単体サーボを無負荷で校正して電源を切ります。ケースと配線を04の上から入れ、付属ホーンを軸方向へ座らせ、06をかぶせます。ホーン付きケースを押し込む方法やサーボの無理な逆駆動は行いません。閉状態のホーン長軸は+Yから+Zへ35度、18mm腕が後下・16mm腕が前上です。歯の割出しで姿勢が変わるので実物で合わせます。

7. 配線と遅い開閉デモ
底の入口X35〜47/Y60.5〜69は12×8.5mm。D3/R6ケーブル包絡と8×5×15コネクターの通過を確認します。ラッチや端子は未モデル化です。コネクターを通してから箱の中で線を滑らかな2本のガイドへ置き、十分な余長を残して底の幅7/深さ3.3mm溝から後へ出します。ガイドは引掛かりを減らす位置案内で、引張りクランプの強度を保証しません。配線を引っ張ったり蓋の可動域へ置いたりしません。
設計上のサーボ角は−10〜55.58度ですが、固定パルスへ直接変換しません。slow_open_demoは未校正ではattachせず、単体で実測した3つのパルス幅を設定してから使う参考です。実ボード未指定・未コンパイルです。初めは蓋1〜63度程度の狭い範囲で校正します。
サーボはGPIOから給電せず適切な外部電源と共通GNDを使います。遅く動かしても停止トルクは制限されません。前縁・ヒンジ・リンクに指を入れず、唸り/停止/接触で直ちに電源を切ります。力制限・指挟みセンサーはありません。電源断で蓋が閉じることに注意します。

8. 検証と未確認
メッシュ、131姿勢、19組立経路、底キーの挿入/回転/引抜き止め、工具と配線の名目包絡を検査します。逆経路は同じ幾何経路です。参照の滑らかな軸/穴の接合部3ケースは別記し、実際のスプライン係合と区別します。支持は実スライスの通常/接触層/移行層を層高・幅付きで照合します。検証記録と修正対応はQA_SUMMARY/REVIEW_RESPONSEに載せます。
PLA密度1.26の均質全充填計算で動く蓋/ロッカー/B軸は約{M['moving_solid_mass_g']:.2f}g、重力だけの保守的トルク上限約{M['conservative_gravity_bound_kgf_cm']:.3f}kgf·cm。5MPa仮許容/25N等の単純梁計算は材料・層接着・ノッチ・疲労や実サーボの停止荷重を評価していません。軸の実掛かり・最大遊び・支持パッドへの座りを現物で確認します。
実物印刷、嵌合、支持除去、歯の掛かり、工具の操作、配線ラッチ/引張り、電源/駆動、耐久/振動は未検証です。実機で組める保証はありません。

9. 編集
editable_cube_v6.blendとparams.py/model.py/cad_utils.pyはBlender5.1.1で再生成できるCADです。params.pyはメートル、局所構造はmm。BOTTOM_KEY_*、FIT、RUNNING、EXCITER_*等を調整できます。SIZEだけで全機構を拡縮せず、受け・軸・リンク・蓋座標も一緒に調整して検証を再実行します。
model→make_coupons→make_plates→audit_all、verify_motion、check_assembly_revision、verify_key_cable、verify_tool_access、verify_revision_capture、offline slice→check_support_revision、render→make_docs_revisionが現行手順です。既存ポートフォリオ/v5/承認参照には触りません。修正2は旧版として履歴保存、修正3試作・実機未検証としてLibraryへ保存します。保存と最終承認は別で、ユーザーへの受け渡しは親レビュー後です。
'''
(R/'README_日本語.txt').write_text(guide,encoding='utf8')
(R/'README.md').write_text('''# SG92R 開蓋デモ v6 修正3

70×70×70mm、底キー込み70×70×70mm、0〜65度、19印刷部品。CAD検証済み／実物印刷・駆動未検証の試作です。

[日本語の印刷・組立説明](README_日本語.txt) ／ [画像付きガイド](assembly_guide.html) ／ [レビュー対応](REVIEW_RESPONSE_日本語.md)

先に28試験片の関連する小部品を確認し、サーボ無しで箱・固定カバー・キーまで組んで手動確認してください。初版の部品を混ぜないでください。中心ねじの代わりに局所捕捉を使うため、実ホーン歯の掛かりを確認できなければ通電しません。

`stl/` 印刷姿勢済み19部品、`coupons/` 試験片、`plates/` 200mm形状3MF、`.blend` とPythonが編集CADです。参考サーボ/ホーン/配線は印刷しません。G-codeは含めません。
''',encoding='utf8')
def svg(name,w,h,items):
 s=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#f4f7fa"/><g font-family="Yu Gothic,Meiryo,sans-serif" fill="#172d3c">'+''.join(items)+'</g></svg>'
 (R/(name+'.svg')).write_text(s,encoding='utf8')
def text(x,y,s,size=26,color='#172d3c'):return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{html.escape(s)}</text>'
def img(fn,x,y,w,h):return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,{base64.b64encode((R/fn).read_bytes()).decode()}"/>'
def line(x1,y1,x2,y2,color='#546d7e',width=2):return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'
def rect(x,y,w,h,fill='#fff',stroke='#c9d6df'):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>'
items=[text(45,65,'見えない住人の箱',40),text(45,105,'SG92R · v6 修正3 · 70mm角 · CAD検証済み試作',24),text(45,140,'実物印刷・組立・駆動は未実施。実形状試験片から確認してください。',22)]
for x,fn,cap in [(35,'preview_closed.png','閉状態：箱70×70×70mm／底キー込み70×70×70mm'),(815,'preview_open65.png','開状態：蓋65度／軽い蓋専用')]:items +=[rect(x,175,750,610),img(fn,x+5,180,740,550),text(x+25,760,cap,24)]
items +=[img('preview_mechanism65.png',35,810,620,440),text(700,890,'19点の印刷部品',30),text(700,950,'付属ホーン + 局所保持 + 底面キー',24),text(700,1010,'上押さえ・スペーサーは平置き印刷',24),text(700,1070,'サーボ無しで箱まで組み、先に手動確認',24),text(700,1150,'全印刷製の係止／追加ばね・結束不要',23),text(700,1200,'力制限・指挟み検知はありません',23)]
svg('assembly_overview',1600,1300,items)
items=[text(45,65,'主要寸法と開閉リンク',38),text(45,110,'単位mm。図は設計値の説明で、実物嵌合・強度を保証しません。',23)]
# True dimensional schematic: top and side views with independently labelled axes.
x,y,k=90,170,6;items +=[rect(x,y,70*k,70*k,'#e8eef1'),rect(x,y,70*k,26.8*k,'#d2dee5'),line(x,y+27.6*k,x+70*k,y+27.6*k),text(x,y-20,'上面：後部固定帯と蓋',26),text(x+25,y+80,'固定帯 26.8',23),text(x+25,y+290,'蓋の前後幅 42.4',23),text(x+25,y+345,'前後の継ぎ目 0.8',23)]
items +=[line(x,y+445,x+420,y+445),line(x,y+435,x,y+455),line(x+420,y+435,x+420,y+455),text(x+145,y+480,'70',26),line(x-25,y,x-25,y+420),line(x-35,y,x-15,y),line(x-35,y+420,x-15,y+420),text(x-68,y+220,'70',23),text(555,260,'壁 / 蓋スキン 2.4',24),text(555,305,'外形 70×70×70',24),text(555,350,'D25×H10 エキサイター仮空間',23),text(555,395,'配線入口 12×8.5',23),text(555,440,'底裏溝 幅7 / 深さ3.3',23),text(555,485,'工具穴：Y61.5/Z59.5、対角5',23)]
x,y,k=910,600,6
def yz(pt):return (x+pt[0]*k,y-pt[1]*k)
items +=[rect(x,y-70*k,70*k,70*k,'#e8eef1'),text(x,y-440,'側面 Y→ / Z↑',26)]
items +=[line(x+445,y-420,x+445,y),line(x+435,y-420,x+455,y-420),line(x+435,y,x+455,y),text(x+465,y-205,'70',25)]
O=D['O'];H=D['H'];uv=D['rocker_local_mm'];r=D['crank_r_mm'];th=math.radians(D['servo_range_deg'][0]);A=[O[0]+r*math.cos(th),O[1]+r*math.sin(th)];B=[H[0]+uv[0],H[1]+uv[1]]
for a,b,c in [(O,A,'#cf7928'),(A,B,'#854293'),(B,H,'#cf7928')]:items.append(line(*yz(a),*yz(b),c,8))
for label,pt in [('O',O),('H',H),('A',A),('B',B)]:u,v=yz(pt);items +=[f'<circle cx="{u}" cy="{v}" r="7" fill="#172d3c"/>',text(u+12,v-10,label,23)]
items +=[text(90,745,'H = (Y22, Z61.8) · O = (Y40, Z37)',26),text(90,795,'クランクR14 · ロッカーH+(14,−4) · リンク29.2587',25),text(90,845,'蓋0〜65度 ⇄ サーボ約−10〜55.58度（実機のパルス校正が必要）',24),text(90,910,'H軸 D6×18.9 / A軸 D5×15.8 / B軸 D5×9.5',25),text(90,960,'軸受穴 D6.6 / D5.6 / D12.6（半径方向公称遊び0.3）',24),text(90,1010,'上押さえ全長52.7、片側0.3の独立ポケット、端面面取り0.45',24),text(90,1070,'SIZEだけで全機構は拡縮しません。局所座標・リンク・受けを一緒に調整します。',22)]
svg('dimensions',1500,1140,items)
items=[text(45,65,'組立方向を間違えないための5段階',36),text(45,110,'図は実CAD。作業は後板を上向きにした台上で、まずサーボ無し。',23)]
for i,(fn,cap) in enumerate([('step_01_rear_frame.png','①04 + 横置き15/16'),('step_02_local_capture.png','②06 + 局所保持17〜19 + 上押さえ14'),('step_03_lid_front_entry.png','③軸とリンク → 蓋を前(+Y)からスライド'),('step_04_complete_cassette.png','④前ロッカー/カバー → 05で軸端を捕捉'),('step_05_manual_box.png','⑤箱receiver + 底面回転キー → 手動確認')]):
 x=40+(i%3)*510;y=155+(i//3)*475;items +=[rect(x,y,490,450),img(fn,x+5,y+5,480,385),text(x+15,y+420,cap,19)]
items +=[text(1060,700,'分解は電源を切り、逆順。',24),text(1060,750,'05を開く前に後板を下へ。',22),text(1060,800,'軸を受け皿へ回収します。',22),text(1060,860,'裸カセットを裏返しません。',22),text(1060,920,'箱からは両板の工具穴を使用。',20)]
svg('assembly_steps',1600,1140,items)
items=[text(45,65,'中心ねじに頼らない、短い局所捕捉',36),text(45,110,'実CADのY40断面。歯を省略した参照は実スプラインの掛かりを証明しません。',22),img('capture_axis_actual_section.png',25,135,1550,680),text(55,835,'ケース後止め → ケース → 付属ホーン → カップ天井 → 17 → 18/19 → 同じ04の止め',24),text(55,890,'公称遊び0.70mm。仮の製造/内部遊び/変形/傾き予算を足すと2.0mm。',24),text(55,945,'実際の歯の掛かりE − 実測最大逃げ ≧ 1mmを暫定確認。未測定なら通電しません。',23),text(55,1000,'1mmはメーカー強度保証値ではありません。実サーボ・実印刷での確認が必要です。',22)]
svg('horn_capture',1600,1070,items)
items=[text(45,65,'支持を許可する面と保護する面',36),text(45,110,'赤：手動支持を塗る実STL面。全面自動支持は使いません。',23)]
for x,fn,title in [(30,'support_04_actual.png','04 U受け：非機能裏面 X31.3'),(815,'support_06_actual.png','06 外周パッド：X46.5 / R10以上')]:items +=[rect(x,145,750,585),img(fn,x,150,750,535),text(x+25,708,title,24)]
items +=[text(55,795,'保護：サーボ基準面・keeper溝・H/A軸受・D12ジャーナル・ホーンポケット・R6.3〜8.5捕捉面',22),text(55,855,'04：支持柱を小分けして開いた台へ。06：支持の輪を割って外へ剥がす。',24),text(55,915,'25/26の実形状試験片で除去性・傷・内周ブリッジを確認してから本体を印刷。',23),text(55,975,'名目包絡の照合は実物の垂れ・糸引き・融合・剥がす力を評価していません。',22)]
svg('support_faces',1600,1040,items)
items=[text(45,65,'200mmベッドの形状プレート',36),text(45,110,'00/04は試験片。01〜03が19本体部品。REFERENCEを印刷しません。',23)]
for i,row in enumerate(json.loads((R/'plate_manifest.json').read_text())):
 x=30+(i%3)*515;y=150+(i//3)*495;fn=row['plate']+'_preview.png';items +=[rect(x,y,490,470),img(fn,x+5,y+5,480,415),text(x+18,y+450,row['plate'].replace('plate_','')+' · '+('手動支持' if row['manual_support'] else '支持なし'),21)]
svg('print_plates',1600,1170,items)
items=[text(45,65,'底面の印刷キーで両フレームを捕捉',36),text(45,110,'修正3試作・実機未検証。解除方向への回転は手動で可能。自動戻り止めなし。',22),img('bottom_assembled_actual.png',30,140,750,600),img('bottom_key_capture_actual.png',815,140,750,600),text(45,790,'閉状態は全印刷部品が70mm角内。頭の下面Z0.2／工具溝14×2×深さ1.15',23),text(45,845,'係止0度では下抜き不可。解除は0→90度へ回し、下へ抜く。押込操作なし。',23),text(45,900,'横棒厚さ4.5／足厚さ6／名目上側隙間0.3。実層強度・掛かりは試験片11/12/27/28から。',22)]
items +=[rect(40,940,490,240,'#fff'),rect(555,940,490,240,'#fff'),rect(1070,940,490,240,'#fff'),text(65,980,'① 係止0度：溝X／下抜き不可',23),rect(215,1030,110,52,'#bec77c'),rect(235,1051,70,10,'#566021'),text(65,1145,'横棒と両足、頭と床の肩で上下を捕捉',19),text(580,980,'② 手で90度まで回す：溝Y',23),rect(770,1001,52,110,'#bec77c'),rect(791,1021,10,70,'#566021'),text(580,1145,'解除方向の回転は自動固定しません',19),text(1095,980,'③ 90度にしてから下へ抜く',23),text(1240,1075,'↓',60),text(1095,1145,'追加の押込操作は不要',20),text(45,1230,'X＝両フレームを結ぶ方向。Y＝配線出口へ向く方向。模式図は工具溝の向きを示します。',21)]
svg('bottom_key_operation',1600,1280,items)
for name in ['bottom_key_operation','assembly_overview','dimensions','assembly_steps','horn_capture','support_faces','print_plates']:
 subprocess.run([r'C:\Program Files\Inkscape\bin\inkscape.exe',str(R/(name+'.svg')),'--export-type=png','--export-filename='+str(R/(name+'.png'))],check=True,capture_output=True)
images=[('bottom_key_operation.png','底面キーの操作と捕捉'),('assembly_overview.png','全体と開蓋'),('dimensions.png','寸法'),('assembly_steps.png','組立方向'),('horn_capture.png','局所捕捉'),('support_faces.png','支持と保護面'),('print_plates.png','5枚の配置'),('exploded_actual3d.png','19部品の実CAD分解図')]
figs=''.join(f'<figure><img src="{fn}" alt="{cap}"><figcaption>{cap}</figcaption></figure>' for fn,cap in images)
blocks=''.join('<p>'+html.escape(b).replace('\n','<br>')+'</p>' for b in guide.split('\n\n'))
out='<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SG92R 開蓋デモ 修正3</title><style>body{font:16px/1.8 system-ui,sans-serif;max-width:1050px;margin:30px auto;padding:0 22px;background:#f8fafb;color:#172d3c}img{width:100%;height:auto}figure{margin:24px 0;background:white;border:1px solid #d2dee6;padding:12px}p{margin:24px 0}figcaption{font-size:14px}</style><h1>SG92R 開蓋デモ v6 修正3</h1><p>CAD検証済みの試作。実物印刷・通電未実施。</p>'+figs+blocks+'</html>'
(R/'assembly_guide.html').write_text(out,encoding='utf8')
print('Japanese revision3 guide /6figures generated',flush=True)
