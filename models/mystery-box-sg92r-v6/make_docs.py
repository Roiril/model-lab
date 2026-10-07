"""Japanese instructions and figures based on the actual CAD exports."""
from pathlib import Path
import json,math,html,base64,struct,zipfile,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent
D=json.loads((R/'assembly_manifest.json').read_text('utf8'));M=json.loads((R/'mechanics_report.json').read_text('utf8'))
parts=[('01','箱本体','01_body'),('02','後部固定カバー','02_fixed_rear_cover'),('03','平板の軽量蓋','03_planar_lid'),('04','一体カセット','04_main_cassette'),('05','前側閉鎖板','05_front_closure'),('06','ホーンカップ・D12ジャーナル','06_horn_cup_journal'),('07','後側ロッカー','07_rear_rocker'),('08','一体ペグ付き前側ロッカー','08_front_rocker'),('09','連結リンク','09_link'),('10','ヒンジ軸 D6 × 16.4','10_hinge_axle'),('11','駆動軸 D5 × 14.6','11_drive_axle'),('12','リンク軸 D5 × 7.6','12_link_axle'),('13','箱固定横キー','13_body_cross_key')]
table='\n'.join(f'{n}  {ja}：stl/{fn}.stl × 1' for n,ja,fn in parts)
guide=f'''住人の箱 — SG92R 一体カセット開蓋試作 v6
作成日 2026-10-07 UTC／実物印刷・実機駆動・実機組立は未実施

今回の範囲
閉じた外形70 × 70 × 70 mmの箱を、軽い蓋だけ0〜65°開く物理デモです。後部の固定カバー、斜め切りの平板蓋、厚い軸を使う4節リンク、一体カセットを採用しました。曲面のスカートはありません。謎解き、会話、音声再生ソフトは含みません。
本体・付属ホーンは、ユーザーが確定した model-lab/models/sg92r-photo のSG92R参照形状をそのまま使用しています。SG90や他の互換サーボを無条件に装着できるモデルではありません。

1. ファイルの使い分け
・stl/：本組立に使う13部品。mm単位、印刷向き・底面Z=0に設定済み。自動回転は使わず、まずこの向きで確認。
・plates/：200 × 200 mmベッド上に並べた形状3MF。00は任意の事前試験、01〜03が本組立の13部品。02には手動支持の許可・禁止面情報があります。G-codeやプリンターへの送信データは含みません。
・coupons/：12種類の嵌合試験片。必須の追加組立部品ではありません。test04・05・08は実部品そのもので、適合すれば本組立へ再利用できます。
・editable_cube_v6.blend：組立位置の編集可能CAD。青は参照サーボ、黒は参照ホーン・配線と仮の振動スピーカーです。REFERENCEで始まるオブジェクトは印刷しません。
・params.py / model.py / cad_utils.py：Blender 5.1.1で生成・再編集できるパラメトリックソース。
・assembly_guide.html：画像付きの日本語説明。オフラインで開けます。
・各検査JSON：幾何・スライスの計算結果。実機の適合を保証する書類ではありません。

2. 印刷する部品（各1個、合計13個、軸3本を含む）
{table}

3. 追加部材
・手元のSG92R 1個、実機に付属する十字ホーン1個と中心ねじ1本。ホーンのスプラインを印刷しません。中心ねじの規格や締付トルクは実物付属品に合わせます。
・サーボを制御できるボード、配線、実機仕様に適合する安定した電源。例のスケッチはArduino Servoライブラリ用の参考です。5 V使用可否・極性・必要電流は手元のサーボ仕様を確認してください。ボードのGPIOから給電しないでください。電源と制御ボードのGNDを共通にします。
・任意：小型の振動スピーカー／エキサイター、適したアンプ、接着材。仮置きはD25 × 高さ10 mm、接着層0.5 mm、底面中心X17/Y45 mm。配線や端子の突出は仮モデルにありません。一般的なコーン型スピーカーの取付穴や音響開口は作っていません。
・任意：横キーの仮止め用の低粘着テープ。キーの振動保持は実機未確認です。
新たな金属ヒンジやリンクねじは使わない構成です。スピーカー・制御基板の実物保持方法は機種未指定なので未設計です。

4. 印刷条件と向き
一般的な200 mm級ベッドを想定。最大占有は試験プレート00の約172.45 × 67.60 mm、本組立の最大は01の148.00 × 104.80 mmです。ブリム等を加えても余裕を確認してください。
計算に使ったオフライン設定：Bambu Studio 2.3.1.51、X1 Carbon 0.4 mm、Bambu PLA Basic、積層0.20 mm、壁4周、上下面5層、充填20%、外壁60 mm/s。これは利用可能なプロファイルによる確認で、ユーザーのプリンター・材料の現物確認ではありません。寸法補正と温度はご自身の機械に合わせます。
01：箱は底面を下。固定カバー・蓋は外側の平面を下、内側のドックを上。支持なし。
02：カセット04は後側の広い平面を下、閉鎖板05は前側の広い平面を下。カップ06は付属ホーンを入れる口を上、D12ジャーナル先端を下。支持は次項の2箇所だけ。
03：ロッカーとリンクは広い面を下、一体ペグは上。3本の軸は長手方向をベッドに寝かせ、平らに切った面を下。細い縦軸として印刷しません。横キーも広い面を下。支持なし。
浮き上がり・糸引き・象の足が出たら、まず印刷条件を直して試験片で確認してください。重要な穴や軸に付いた支持材を無理に削って合わせる前提にはしていません。

5. 支持材の範囲
plates/plate_02_cassette.3mfの手動支持情報を使い、自動の全面支持は無効にします。通常支持、上下面隙間0.20 mm、XY隙間0.35 mm、ブリム3 mmで確認しました。取り込んだスライサーで橙色の許可面と禁止面を目視確認してください。手動支持情報を読めないソフトでは support_faces.png を見て同じ2面だけに支持を設定し、再スライスが必要です。
04：U形の後側受けの、サーボやカップに当たらない裏側面（世界X31.3、印刷Z27.3 mm）。支持の足場は奥へ下げた非機能面X6.7（Y24.5〜55.5/Z27〜41）と、配線入口の非接触端面X12.4のみ。支持はサーボ挿入前に除去します。
06：カップの前側の内側環状面X46.1（印刷Z11.9 mm）。端面は軸受けに触れず、軸先端との隙間で前後位置を制限します。D12軸・ホーンポケット・A軸受けの穴面は支持禁止。
05の軸受け、03のドック、固定カバーの菱形穴、ロッカーの嵌合面、各軸にも支持禁止。カップのD5.6盲穴天井は短い橋渡し、箱側面キー入口は10.2 mm橋渡しです。試験片とスライスのプレビューで垂れを確認してください。
支持インターフェースのG-code押出終点を3MFの元部品座標に戻し、許可された足場への着地を確認しています。この解析は全フィラメント接触や実際の除去性を証明しません。

6. 本体を刷る前の試験片
最優先：test01でサーボ本体・取付耳・配線を上から入れられること、test02で付属十字ホーンがカップへ押し込まずに入ることを確認します。ホーンの向きと長い腕の非対称形状に注意。
test03と04/05/06でD5.6/D6.6/D12.6の穴と対応軸が指で軽く回ることを確認。ノミナル隙間は半径0.3 mm、直径差0.6 mmです。軸は2面を平らにしてあります。
test07と08で屋根ドック／一体ペグ、test09と10で固定カバーの穴／ペグ、test11と12で側面キー入口／頭部を確認。菱形穴の斜面方向の隙間は約0.21 mmです（対角半径差0.3 mm）。強い圧入はしません。
付属ホーン外形には写真推定値が含まれます。合わない場合は参照実測値とポケットを更新して再生成してください。互換品ごとのケース、耳、ホーン、配線出口の違いを無視しないでください。

7. 組立順序（画像の番号を参照）
座標はX＝軸方向、Y＝後から前、Z＝底から上。後部固定カバーの帯がある側が後ろです。最初は箱01に入れず、机上でカセットを組みます。
① 印刷品を冷まして支持材・ブリムを除去。04の奥の支持と06の環状面の支持を先に取り除きます。軸・穴・ペグの試験を済ませます。
② サーボをまだ付けず、ヒンジ軸10、後側ロッカー07、リンク09、リンク軸12、前側ロッカー08と蓋03を仮組みします。07/08の広い上部を蓋内側の開いたドックに合わせ、08の一体菱形ペグを蓋と07へ横から通します。12はリンク上側の穴と両ロッカーの盲穴の間に収めます。ヒンジ軸10は04の後側盲穴、両ロッカーのヒンジ穴、05の前側盲穴で捕捉されます。
③ 06のA軸盲穴へ駆動軸11を入れ、09の下側穴を11へ通します。06のD12ジャーナルを05のD12.6盲穴へ合わせ、11の先端を05の開いた円弧溝へ合わせます。05を横から寄せ、蓋0〜65°を手で軽く動かして確認します。軸を落とさないよう保持してください。
④ このサーボなしの仮組みで渋さ、引っ掛かり、端点、蓋と固定帯の干渉を確認。蓋の閉端では箱の座に載る構成です。機構を無理に回さず、いったん05を外します。
⑤ 機構から外したサーボだけを安全な中立パルスへ動かし、電源を切って付属ホーンを取り付けます。閉状態のCADではカップの駆動腕はY方向から−10°、長いホーン腕は+35°です（カップとホーンの位相差45°）。実機のスプライン刻みとパルス方向に合わせて較正します。初期中立がCADの閉位置に一致するとは限りません。付属中心ねじで固定します。
⑥ 04の床へSG92Rを上から下ろします。ケース、耳、配線は上入れの開口へ通し、配線を前側の切欠きへ逃がします。06を横から実ホーンへ被せます。無通電でサーボのギアを手で強制回転させないでください。③のリンク・蓋ユニットを閉位置で合わせます。
⑦ 後部カバー02を横から04の一体ペグへ通します。05を反対側から寄せ、その一体ペグで02を捕捉します。同時にヒンジ軸10、D12ジャーナル、11の円弧溝、サーボ上部押さえの先端が04のポケットに入ることを確認。カセット下部の2本の一体スペーサーは05の内側へ収まります。サーボは床・側壁・剛体の上部／軸方向押さえで保持されます。
⑧ 任意のエキサイターを箱底へ仮配置。D25 × 10 mmに端子・配線が加わった実外形を確認し、リンクやカセットに触れないよう固定。コーン型スピーカーなら別の取付設計が必要です。
⑨ 蓋・後部カバーを含む完成カセットを箱01へ真上から下ろし、4つの受けに04/05を通します。底の配線口へ配線を逃がし、挟まないでください。
⑩ 右側の入口から横キー13を水平に通し、箱の受け・04・05を捕捉します。側面の頭部は外面とほぼ同面。緩ければ試作では低粘着テープで仮止めし、実機で保持方法を確認します。

8. ゆっくり開くデモと安全な較正
スケッチ slow_open_demo/slow_open_demo.ino は未コンパイル・未実行の参考コードです。ボード未指定のため、そのまま使える保証はありません。Servoライブラリ、信号ピン9、外部電源と共通GNDを前提にしています。
まず機構から外したサーボで、中立1500 µs、短い移動、回転方向、安定した電源を確認。コードの初期開位置1700 µsは慎重な小範囲の例で、65°に達する値ではありません。oで開、cで閉、sで現在位置を保持。初期は1 µs/20 ms、200 µsの移動で約4秒。電源投入時のサーボの最初の移動は速度制御できません。
閉位置を較正してからホーンを取り付け、少しずつ開位置を増やします。CADの必要サーボ角は−10.000〜+55.578°、ストローク65.578°。角度からµsへ一律換算しないでください。動く方向も実機で確認します。
開閉端では機械的に強く押し当てず、少し手前で停止。唸り・振動・電源降下・引っ掛かりがあれば直ちに電源を切ります。蓋に装飾や重い物を載せないでください。
指を蓋の縁、リンク、軸周りへ入れないでください。低力を意図した試作であり、センサーや力制限、指挟み防止機能はありません。電源を切ると重力で蓋が閉じる可能性があります。開状態でもサーボは重力負荷を支えます。

9. 設計値と検証の範囲
外形70³ mm、壁・蓋スキン2.4 mm、固定帯26.8 mm、可動蓋奥行42.4 mm、外側の前後隙間0.8 mm。蓋後端は内外で3.4 mmずらした面取り。
ヒンジ H(Y22/Z61.8)、サーボ O(Y40/Z37)、クランク半径14、ロッカー先端H+(14,−4)、リンク軸間29.258694 mm。ピン径6/5/5、ジャーナル径12、軸受け内径6.6/5.6/12.6 mm。
PLA密度{M['assumed_density_g_cm3']:.2f} g/cm³の均一な全充填計算では、蓋に連動する4部品（03/07/08/12）の質量は約{M['moving_solid_mass_g']:.2f} g。重力だけの保守的サーボ負荷は約{M['conservative_gravity_bound_kgf_cm']:.3f} kgf·cm。サーボの実効トルク、摩擦、加速、バックラッシュ、印刷変形や疲労は含まず、実機能力との比較保証はしていません。
計算確認：STL13＋試験片12＋3MF内25個のメッシュ計50件で閉じた多様体・向き・ゼロ面積面・体積を直接検査。可動は0〜65°を0.5°刻み131姿勢、組立の主要7経路は2 mm刻みで交差を確認。離散サンプルのため連続全位置や実機の公差・配線の柔軟性を証明しません。
スライス4プレートはオフラインで実行。G-codeは評価内部だけで使用し、配布ZIPには含みません。最終JSONには成功・不成功と検査条件を記録します。
未確認：実物印刷、寸法再現、ホーン実物の嵌合、支持材除去性、ブリッジ垂れ、軸の摩擦・保持、サーボ駆動と電源、トルク余裕、繰返し耐久、騒音、スピーカー／アンプ／基板の保持。必ず試験片とサーボなしの手動確認から始めてください。

10. 編集と再生成
Blender 5.1.1で model.py をバックグラウンド実行すると、編集CADとstl/が生成されます。params.pyの長さはメートル（0.001＝1 mm）、角度は度。model.pyの構築ヘルパーにはmmの局所値もあります。
FIT（ホーン外形・菱形ペグのノミナル隙間）とRUNNING（軸受け半径隙間）は0.0003。EXCITER_D/H/X/Y、LID_SKIN、OPEN_DEGなどを編集できます。SIZEを変えるだけで全機構が比例拡大する設計ではありません。サーボ位置、軸位置、固定座標、リンク長、受けとドックを一緒に調整してください。
変更後は verify_motion.py / check_assembly.py、make_coupons.py→make_plates.py→audit_all.py、スライスと支持接触を再確認します。0.3 mmは印刷後の実測隙間ではありません。
参照SG92Rの寸法・測定／推定の区別は reference/SOURCE_README.md とreference/dimensions.jsonへ記録。ケース23×12×22 mm、耳32×12×2 mm、取付穴ピッチ28.84 mm、ギアカバー全幅14 mm、ホーン34×17 mm／腕厚1.5 mm。写真推定・仮定が混在し、メーカー公差の保証ではありません。
model-labの旧v5とSG92R正本は更新せず、新規v6フォルダーへ保存します。
'''
(R/'README_日本語.txt').write_text(guide,encoding='utf8')
(R/'README.md').write_text('# 住人の箱 — SG92R v6\n\n70 × 70 × 70 mm、軽量蓋0〜65°、13印刷部品。実機未検証。\n\n日本語の全説明：[README_日本語.txt](README_日本語.txt)。画像付き：[assembly_guide.html](assembly_guide.html)。\n\n`stl/` は印刷部品、`coupons/` は事前試験、`plates/` は形状3MFです。参照サーボは印刷しません。組立全体のSTLを一括印刷しないでください。\n\n編集は `params.py` と `model.py`、または `editable_cube_v6.blend`。Blender 5.1.1 / Python API。寸法はm、局所ヘルパーはmm。\n\n生成例：`blender --background --python-exit-code 1 --python model.py`\n\n検査：`verify_motion.py` / `check_assembly.py`、`make_coupons.py` → `make_plates.py` → `audit_all.py`。スライス確認はローカルのBambu Studioプロファイルが必要です。配布にG-codeは含めません。\n',encoding='utf8')
rows=''.join('<tr><td>'+n+'</td><td>'+html.escape(ja)+'</td><td>'+fn+'.stl</td><td>1</td></tr>' for n,ja,fn in parts)
images=[('assembly_overview.png','組立と65°開蓋のプレビュー'),('dimensions.png','主要寸法'),('exploded_actual3d.png','実CADの分解図：位置だけを離して表示'),('print_plates.png','200 mmベッドの印刷プレート'),('support_faces.png','許可する支持面'),('section_side_actual3d.png','X=49.8 mmで実際に切った断面：赤は切断面')]
figs=''.join(f'<figure><img src="{fn}" alt="{caption}"><figcaption>{caption}</figcaption></figure>' for fn,caption in images)
sections=[]
for block in guide.split('\n\n'):
    sections.append('<p>'+html.escape(block).replace('\n','<br>')+'</p>')
htmltext='<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>住人の箱 SG92R v6 組立説明</title><style>body{font:16px/1.75 system-ui,sans-serif;max-width:1050px;margin:35px auto;padding:0 22px;color:#172635;background:#fafafa}h1{font-size:28px}img{max-width:100%;height:auto}figure{margin:30px 0;background:white;border:1px solid #d5dee4;padding:14px}figcaption{font-size:14px;color:#536776}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #c7d4db;padding:8px}p{margin:24px 0}</style><h1>住人の箱 — SG92R v6</h1><p>70 × 70 × 70 mm・0〜65°開蓋・13印刷部品。実機印刷と駆動は未実施。</p>'+figs+'<table><tr><th>番号</th><th>部品</th><th>STL</th><th>数</th></tr>'+rows+'</table>'+''.join(sections)+'</html>'
(R/'assembly_guide.html').write_text(htmltext,encoding='utf8')
(R/'slow_open_demo').mkdir(exist_ok=True)
(R/'slow_open_demo/slow_open_demo.ino').write_text('''// Reference only: board unspecified; not compiled or physically tested.
// Test the unloaded servo first. Supply servo from a suitable external source.
// Common GND with controller. Calibrate actual direction and endpoints.
#include <Servo.h>
Servo opener;
const uint8_t SIGNAL_PIN = 9;
const int CLOSED_US = 1500; // Set only after unloaded calibration.
const int OPEN_US = 1700;   // Small initial trial, NOT the CAD 65 degree endpoint.
const int LOWER_US = 1200, UPPER_US = 1800;
const unsigned long STEP_MS = 20;
int currentUs = CLOSED_US, targetUs = CLOSED_US;
unsigned long previousStep = 0;
void setup() {
  Serial.begin(115200);
  // First power-on motion cannot be slowed by this loop. Keep servo unloaded.
  opener.writeMicroseconds(currentUs);
  opener.attach(SIGNAL_PIN, 1000, 2000);
  opener.writeMicroseconds(currentUs);
  Serial.println("o=open, c=close, s=hold current position");
}
void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    if (command == 'o') targetUs = constrain(OPEN_US, LOWER_US, UPPER_US);
    if (command == 'c') targetUs = constrain(CLOSED_US, LOWER_US, UPPER_US);
    if (command == 's') targetUs = currentUs; // Still energized: holds position.
  }
  unsigned long now = millis();
  if (now - previousStep >= STEP_MS) {
    previousStep = now;
    if (currentUs < targetUs) ++currentUs;
    else if (currentUs > targetUs) --currentUs;
    opener.writeMicroseconds(currentUs);
  }
}
''',encoding='utf8')

def txt(x,y,s,size=24,color='#183348',weight='normal'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(s)}</text>'
def pic(fn,x,y,w,h):
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="{fn}"/>'
def svg(name,w,h,content):
    (R/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><style>text{{font-family:Meiryo,"Yu Gothic",sans-serif}}</style><rect width="100%" height="100%" fill="#f7f9fa"/>'+content+'</svg>',encoding='utf8')
def line(a,b,color='#25768b',width=3):return f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{color}" stroke-width="{width}"/>'
def dim(a,b,label):
    dx=b[0]-a[0];dy=b[1]-a[1];dd=math.hypot(dx,dy);nx=-dy/dd*10;ny=dx/dd*10
    t=lambda p:f'{p[0]},{p[1]}'
    arrow=''
    for e,sign in [(a,1),(b,-1)]:
        mid=[e[0]+sign*dx/dd*15,e[1]+sign*dy/dd*15];points=[e,[mid[0]+nx,mid[1]+ny],[mid[0]-nx,mid[1]-ny]];arrow+='<polygon points="'+' '.join(t(p) for p in points)+'" fill="#25768b"/>'
    return line(a,b)+arrow+txt((a[0]+b[0])/2+18,(a[1]+b[1])/2+30,label,31,'#25768b','bold')
cam=json.loads((R/'camera_projected_dimensions.json').read_text());content=txt(65,65,'住人の箱 — SG92R v6 主要寸法',38,weight='bold')+txt(65,110,'実CADの閉状態／単位 mm／実機未検証',24)+pic('preview_closed.png',0,155,1500,1100)
for k in ['width','depth','height']:
    a=cam[k+'_start'];b=cam[k+'_end'];content+=dim([a[0],a[1]+155],[b[0],b[1]+155],'70 mm')
content+=txt(65,1370,'壁・蓋スキン 2.4  ｜  固定帯 26.8  ｜  可動蓋奥行 42.4',28)+txt(65,1420,'蓋 0〜65°  ｜  外側隙間 0.8  ｜  スピーカー仮置き D25 × 10',27)+txt(65,1470,'ヒンジ軸 D6・リンク軸 D5 ／ 軸受け直径差 0.6 ／ クランク半径14',24)
svg('dimensions',1500,1530,content)
content=txt(60,60,'住人の箱 — SG92R v6 組立プレビュー',38,weight='bold')+txt(60,108,'70 × 70 × 70 mm・軽量蓋65°・13部品（軸3本を含む）・実物印刷／駆動は未実施',24)
for fn,x,y,label in [('preview_closed.png',45,175,'閉状態：後部固定帯と平板蓋'),('preview_open65.png',790,175,'65°開：斜めの後端が固定帯をかわす'),('section_side_actual3d.png',45,820,'実断面 X=49.8：赤は切断面'),('preview_mechanism65.png',790,820,'内部機構：外装・閉鎖板を非表示')]:
    content+=txt(x+12,y-15,label,25,weight='bold')+pic(fn,x,y,700,550)
content+=txt(60,1445,'青：確定SG92R参照形状　橙：蓋ロッカー／カップ　紫：リンク　黒：仮のD25 × 10エキサイター',23)+txt(60,1490,'カップは付属ホーンを使用。支持は内側の非機能面のみ。スプラインは印刷しません。',23)
svg('assembly_overview',1530,1540,content)
P=json.loads((R/'plate_manifest.json').read_text());content=txt(50,60,'印刷プレート — 200 × 200 mm想定',38,weight='bold')+txt(50,107,'00は任意の事前試験。01〜03で本組立13部品。参照サーボは印刷しません。',25)
for i,entry in enumerate(P):
    x=50+(i%2)*720;y=180+(i//2)*705
    label=['00｜嵌合試験12種（任意）','01｜箱・固定カバー・蓋 × 各1','02｜カセット・閉鎖板・カップ × 各1','03｜ロッカー2・リンク・軸3・横キー'][i]
    content+=txt(x,y-15,label,25,weight='bold')+pic(entry['plate']+'_preview.png',x,y,670,610)+txt(x+10,y+640,'占有 %.2f × %.2f mm ／ %s'%(tuple(entry['occupied_mm'])+('内側2面のみ手動支持' if i==2 else '支持なし',)),23)
content+=txt(50,1580,'STLは印刷向きに配置済み。02の支持許可／禁止情報は3MFに保存。必ずスライスのプレビューを確認。',22)
svg('print_plates',1500,1640,content)

# Exact mesh facets from geometry 3MF. X-ray projection keeps marked interior faces visible.
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
content=txt(45,62,'支持を許可する内側の非機能面',36,weight='bold')+txt(45,108,'実STLの面を透視表示。橙の2領域のみ支持許可。他の面は支持禁止。',24)
with zipfile.ZipFile(R/'plates/plate_02_cassette.3mf') as z:
    root=ET.fromstring(z.read('3D/3dmodel.model'))
    obs=root.findall('m:resources/m:object',ns)
    for idx,obj in enumerate([obs[0],obs[2]]):
        verts=[[float(v.get(k)) for k in ('x','y','z')] for v in obj.findall('m:mesh/m:vertices/m:vertex',ns)]
        tris=obj.findall('m:mesh/m:triangles/m:triangle',ns)
        proj=[[.80*x-.60*y,.28*x+.37*y-.85*zz] for x,y,zz in verts]
        xs=[a[0] for a in proj];ys=[a[1] for a in proj];scale=min(600/(max(xs)-min(xs)),660/(max(ys)-min(ys)));cx=50+idx*730;cy=190
        points=[[cx+(a[0]-min(xs))*scale,cy+(a[1]-min(ys))*scale] for a in proj]
        orange=[]
        for t in tris:
            ids=[int(t.get(k)) for k in ('v1','v2','v3')];ps=' '.join('%.2f,%.2f'%tuple(points[j]) for j in ids)
            poly=f'<polygon points="{ps}" fill="#7895a5" fill-opacity="0.055" stroke="#63808e" stroke-opacity="0.12" stroke-width="0.7"/>'
            content+=poly
            if t.get('paint_supports')=='4':orange.append(f'<polygon points="{ps}" fill="#ee8431" fill-opacity="0.83" stroke="#bf5d18" stroke-width="0.7"/>')
        content+=''.join(orange)
        if idx==0:
            content+=txt(cx,900,'04：U形受けの裏側 X31.3',27,weight='bold')+txt(cx,943,'支持の足場：奥へ下げたX6.7面と',23)+txt(cx,980,'配線入口の非接触端面X12.4だけ',23)
        else:content+=txt(cx,900,'06：前側の非接触環状面 X46.1',27,weight='bold')+txt(cx,943,'D12軸、ホーンポケット、D5.6穴は',23)+txt(cx,980,'支持禁止。カップの口を上に印刷。',23)
content+=txt(45,1060,'通常支持：上下面隙間0.20／XY隙間0.35 mm。支持の足場も取付・嵌合面から外しています。',23)+txt(45,1105,'面情報を読めないスライサーでは再設定。実際の支持除去性・穴の仕上がりは未検証。',23)
svg('support_faces',1500,1160,content)
print('DOCS written: Japanese guide, offline HTML, reference sketch, 4 SVG figures')
