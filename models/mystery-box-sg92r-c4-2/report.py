"""最新の検査結果と実CAD画像から単一ファイルの納品説明を作る。"""
from pathlib import Path
import base64
import html
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
TARGET = ROOT / "reports/2026-10-11_c4-2.html"
STYLE = Path("C:/Users/kouga/Projects/Web/claude-global/skills/visual-deliverable/assets/report.css")


def read(name):
    return json.loads((BUILD / name).read_text(encoding="utf-8"))


def esc(value):
    return html.escape(str(value))


def table(headings, rows):
    return '<div class="tblwrap"><table><thead><tr>' + ''.join(
        f'<th>{esc(value)}</th>' for value in headings) + '</tr></thead><tbody>' + ''.join(
        '<tr>' + ''.join(f'<td>{esc(value)}</td>' for value in row) + '</tr>' for row in rows
    ) + '</tbody></table></div>'


def image(name, caption):
    path = BUILD / name
    if not path.is_file():
        raise FileNotFoundError(path)
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<figure><img src="data:image/png;base64,{data}" alt="{esc(caption)}"><figcaption>{esc(caption)}</figcaption></figure>'


def verdict(value):
    return "適合" if value is True else "未成立"


def main():
    verify = read("verify_report.json")
    drive = read("drive_report.json")
    assembly = read("assembly_report.json")
    sim = read("simulate_report.json")
    delivery = read("delivery_report.json")
    support_geometry = read("print_support_geometry.json")
    audit = read("delivery_audit.json")
    manifest = read("manifest.json")
    holes = read("hole_clearance.json")
    assembly_steps = read("assembly.json")["steps"]
    demo = read("demo_compile_report.json")
    contact_table = read("contact_envelope_evidence.json")
    required = (verify["pass"], drive["overall"]["geometryPass"], assembly["pass"],
                sim["overall"]["calculationPass"], support_geometry["overall"]["pass"],
                demo["pass"], contact_table["pass"], delivery["status"] == "layout_only", audit["pass"])
    if not all(required):
        raise RuntimeError("検査が未成立のため完成報告を生成しない")
    topology = verify["stl_direct_parse"]
    scene = verify["exact_scene"]
    contact = verify["camFollowerActualHeight"]
    foot_clearance = min(row["actualMinimumPerSideClearanceMm"]
                         for row in contact["footGuidePassage"]["cases"])
    stat = sim["static"]
    rows = []
    for identifier, label, angle in (("flat", "平面", 15), ("upper_left", "左上", 50),
                                     ("center", "中央", 90), ("upper_right", "右上", 130),
                                     ("lower_pair", "下側の二か所", 165)):
        state = next(row for row in verify["stateBounds"]["states"] if row["id"] == identifier)
        shifts = [state["carriers"][group]["actualShiftFromFlatMm"]
                  for group in ("center", "upper_left", "upper_right", "lower_pair")]
        rows.append((label, f"{angle}°", " / ".join(f"{v:g}" for v in shifts) + " mm"))
    plate_rows = []
    for kind, plate in delivery["plates"].items():
        label = "試片" if kind == "fit_test" else "本体 1" if kind == "full" else f"本体 {kind.removeprefix('full_')}"
        plate_rows.append((label, Path(plate["layout"]["file"]).name))
    parts = [part for part in manifest["parts"] if part.get("print") and not part.get("fit_only")]
    evidence = table(("検査", "実測・判定"), (
        ("組立・印刷STL", f"{len(parts)}種類の印刷部品。連結成分・閉境界・正体積を検査"),
        ("運動中の干渉", f"{scene['poseSamples']}姿勢 / {scene['uniquePairs']}組。許可範囲外の干渉 {len(scene['violations'])}件"),
        ("カムと受けの接触", f"{len(contact['samples'])}組。許容する面間隔0.03mm以内"),
        ("接触足の組立時の通過", f"4群。角穴の四辺に対する最小片側隙間{foot_clearance:.3f}mm。要求0.20mm以上"),
        ("表示する高さと実STLの照合", f"{contact_table['interpolation']['totalSamples']}点。最大誤差{max(abs(contact_table['interpolation']['minimumInterpolatedMinusActualMm']), abs(contact_table['interpolation']['maximumInterpolatedMinusActualMm'])):.8f}mm"),
        ("六角穴の開口", f"{holes['clearance']['cellsPerState']}セル × {holes['clearance']['states']}状態。7高さの実断面を検査。{verdict(holes['pass'])}"),
        ("駆動の接続と保持", verdict(drive["overall"]["geometryPass"])),
        ("累積組立・逆分解", verdict(assembly["pass"])),
        ("検査と配布ファイルの照合", f"{audit['referenceCount']}参照。古い形状と検査の取り違え0件"),
        ("摩擦を含む最大静的トルク", f"{stat['maximumRequiredTorqueNm']*1000:.2f} mN·m / 停動トルクの{stat['fractionOfStall']*100:.1f}%"),
        ("ゆっくり動かした最大トルク", f"{stat['peakLowSpeedTorqueNm']*1000:.2f} mN·m。停動トルクの1/3以下"),
        ("印刷用の支えの形状", f"{len(support_geometry['parts'])}種類の部品。実STLの接続と部位ごとの面間隔を検査。{verdict(support_geometry['overall']['pass'])}"),
        ("スライスと印刷経路", "ユーザーがBambu Studioで実施。印刷経路と初層の接着は未検証"),
        ("デモのコンパイル", f"Arduino Uno。Flash {demo['flashBytes']} / {demo['flashMaximumBytes']} bytes。RAM {demo['ramBytes']} / {demo['ramMaximumBytes']} bytes。書き込みと通電は未実施"),
    ))
    downloads = []
    editable_downloads = []
    for kind, plate in delivery["plates"].items():
        layout_name = Path(plate["layout"]["file"]).name
        downloads.append(f'<li><a href="../prints/mystery-box-sg92r-c4-2/{esc(layout_name)}">{esc(layout_name)}</a></li>')
    for artifact in delivery["artifacts"]:
        filename = Path(artifact["file"]).name
        if filename.endswith(".stl"):
            editable_downloads.append(f'<li><a href="../prints/mystery-box-sg92r-c4-2/{esc(filename)}">{esc(filename)}</a></li>')
    snapshots = ''.join(image(f"preview_{identifier}.png", label)
                        for identifier, label, _ in (("flat", "平面", 15), ("upper_left", "左上の3枚が凹む", 50),
                                                    ("center", "中央の1枚が凹む", 90), ("upper_right", "右上の3枚が凹む", 130),
                                                    ("lower_pair", "下側の左右6枚が凹む", 165)))
    git_status = subprocess.run(["git", "status", "--short"], cwd=ROOT, check=True,
                                capture_output=True, encoding="utf-8").stdout
    git_diff = subprocess.run(["git", "diff", "--stat"], cwd=ROOT, check=True,
                              capture_output=True, encoding="utf-8").stdout
    content = f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>C4-2 凹む六角格子</title><style>{STYLE.read_text(encoding="utf-8")}
img{{display:block;width:100%;height:auto}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-family:var(--mono);font-size:var(--fs-xs)}}details{{margin-block:var(--sp-6)}}.patterns{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,20rem),1fr));gap:var(--sp-4)}}
</style><div class="wrap"><p class="eyebrow">model-lab · 2026-10-11</p><h1>C4-2 凹む六角格子</h1>
<p class="sub">110 × 110 × 110 mm。SG92R 1台で四つの場所を選ぶ。</p>
{image('hero.png', '110mm角のC4-2。六角格子は同じ形で揃える。')}
<div class="lead"><p>現在の六角格子はC4-1として残しました。C4-2は中央・左上・右上・下側の二か所が選択的に4mm沈みます。平面へ戻す位置もあります。</p><p>実STLによる接続と組立を検査しました。動作計算は摩擦の仮定を含む条件付きの結果です。実物の印刷と通電は未実施です。</p></div>
<p><a href="http://localhost:3000/viewer/lattice/index.html?model=mystery-box-sg92r-c4-2">物理検証とパターン選択</a> · <a href="http://localhost:3000/viewer/lattice/index.html?model=mystery-box-sg92r-c4-2&amp;mode=assembly">組み立て表示</a></p>
<h2>1. 凹む場所</h2><p>19枚の六角環は同じ輪郭です。貫通穴を残します。画像は天面の近接表示です。切り替える途中は二つの凹みが滑らかに入れ替わります。表の順は中央 / 左上 / 右上 / 下側です。</p>
{table(("選択", "サーボ角", "平面からの上下"), rows)}<div class="patterns">{snapshots}</div>
<h2>2. 力が伝わる構造</h2><p>付属ホーンを形に合わせた受けへ入れます。角形キーが受けと円盤をつなぎます。円盤の四つの同心トラックがそれぞれの受けを支えます。格子は二本の案内で上下します。</p>
<p>円盤の外周は外装の支持環へ載ります。円盤止め輪が上方への抜けを止めます。天面上向き専用です。電源を切った後の位置は保証しません。</p>
<p>カムに接する足は4.8mm厚です。周方向の長さは2.4mmです。案内穴を通す最小片側隙間は実STLで{foot_clearance:.3f}mmです。斜めの位置にある角棒がトラックの谷からはみ出すため、棒の下端を高くしました。4mm下降時も谷外の平面から0.6mm離れます。足底の接触とは別に、案内棒を含む全可動部を干渉検査します。</p>
<p>案内枠は外装の四隅の棚へ直接載ります。対角二か所のL字の壁が横ずれを0.2mmで止めます。天板裏の四本の柱が浮き上がりを0.3mmで止めます。上方の力は柱から天板の爪を通して外装へ伝わります。保持面ごとの初接触と、保持面を退避した負例を実STLで検査します。</p>
<p>SG92R本体のX両端は底板の壁で止めます。底板の爪を通して外装へ保持力を伝えます。付属ホーンと受けを先に入れます。90度にした本体を後から底側へ通します。底板を閉じるまで本体の保持は完成していません。</p>
<p>本体から底板までの下方遊びは0.35mmです。底板自体の遊び0.2mmも含めると合計0.55mmです。天板の爪は上側の受け面へ直接掛けます。円盤止め輪の爪は支持柱を避けて45度ずらしています。爪の厚さは1.2mmです。挿入時の最大撓みは0.5mmです。</p>
{image('cutaway.png', '外装の右側をX=22mmで隠した実CAD。内部は不透明。')}
<h2>3. 検証結果</h2><p>計器は接触する正例と離れた負例で校正します。通るはずの形状と止まるはずの形状が両方期待どおりになることを前提にしています。形状上の保持と実物の保持力は別に記録します。</p>{evidence}
<p>材料は中実PLAとして計算しました。接点と支持面の摩擦係数は0.30を仮定します。SG92Rの停動トルクは4.8Vで245 mN·mとしました。ゆっくり動かす条件は3秒です。</p>
<p>足の有限な面とカム三角形が重なる範囲の最高点から格子の高さを求めます。表示用の角度表は最大0.05°間隔です。変化が細かい区間を追加分割します。表の間も25%・50%・75%で実STLと照合しました。この有限個の姿勢検査を、全ての連続姿勢の衝突証明とは区別します。</p>
<p class="note">サーボ仕様: <a href="https://towerpro.com.tw/product/sg92r-7/">TowerPro SG92R</a>。カム設計の参照: <a href="https://www.cs.cmu.edu/~rapidproto/mechanisms/chpt6.html">CMU Mechanisms: Cams</a>。実物部品の形はmodels/sg92r-photoを使用。</p>
<h2>4. 印刷と組み立て</h2>{table(("プレート", "配置3MF"), plate_rows)}
<p>印刷部品は{len(parts)}種類です。試片を含めた13個のSTLと4個の配置3MFを提供します。スライスはBambu Studioで行ってください。印刷時間と材料量と印刷経路は未検証です。</p>
<p>外装と案内枠には印刷用の支えがあります。四つの可動部にも梁を支える形状があります。部位ごとの面間隔を実STLで測ります。印刷後に薄いへらで外します。スライス後の材料面の隙間と初層の接地をBambu Studioで確認してください。外す力と面の傷は実物未確認です。</p>
<p>付属ホーンを使います。試片でホーン受けと角キーの嵌まりを先に確かめます。初期角度90°で組み立てます。格子を載せる前に15°へ戻します。ホーンの装着角がずれる場合は、デモの共通角度補正を1°ずつ調整します。凹む角度の区間の中央へ合わせます。初期補正は0°。補正の上限は±10°です。実物で五つの停止位置を確かめます。</p>
<ol>{''.join(f'<li>{esc(step["instruction"])}</li>' for step in assembly_steps)}</ol><ul>{''.join(downloads)}</ul>
<details><summary>部品STL</summary><ul>{''.join(editable_downloads)}</ul></details>
<p><a href="../models/mystery-box-sg92r-c4-2/README.md">部品表と再生成手順</a> · <a href="../models/mystery-box-sg92r-c4-2/demo/demo.ino">SG92Rのデモ</a></p>
<h2>5. 要件ごとの結果</h2>{table(("要件", "結果"), (
('現在のモデルをC4-1として残す', 'モデルIDと形状を保存。表示名をC4-1へ変更。'),
('中央以外も凹む', '左上3枚・中央1枚・右上3枚・下側6枚。平面を含む5停止位置。'),
('少し大きくしてよい', '110mm角。円盤外径98mm。'),
('SG92Rだけで機構を動かす', 'SG92R 1台と付属ホーン。制御用マイコンと外部4.8V電源は必要。'),
('C1と同じ物理検証と組立表示', '同じ操作形式。累積工程と逆分解を同じフレームで検査。'),
('C1と同じ透過仕様', '外装の右側をX=22mmで隠す。内部は不透明で表示。'),
('印刷して組めるデータ', '13個のSTLと4個の配置3MF。試片を含む。スライスと実印刷はユーザーが実施。'),
))}
<h2>6. 決めたこと</h2><p>四つの群は独立した半径33 / 37 / 41 / 45mmのトラックへ割り当てました。穴の形を揃えるため六角環はすべて同じ対辺寸法です。外装の肉厚は2.4mmです。荷重を受ける板は3.2mmです。格子周囲の片側隙間は0.35mmです。</p>
<h2>7. 譲ったこと</h2><p>部品を小さくすることより、案内と接点を分離して組めることを優先しました。本体は複数プレートです。上向き面のデモに限定しました。指で押した入力は検出しません。</p>
<h2>8. 実物で確かめること</h2><ol><li>付属ホーンと受け。角キーの試片。実物のスプラインへの取付け。</li><li>印刷用の支えの取り外し。面の傷。止め輪と外装の着脱。爪の保持力。案内の滑り。</li><li>4.8Vでゆっくり通電。五つの停止位置の4mm段差。擦れと引っ掛かり。</li><li>繰り返し動作による摩耗。爪の白化や割れ。電源を切った後の挙動。</li></ol>
<details><summary>検査データの原文</summary><pre>{esc(json.dumps({'verify': verify, 'drive': drive, 'assembly': assembly, 'simulate': sim, 'printSupportGeometry': support_geometry, 'contactEnvelope': contact_table}, ensure_ascii=False, indent=2))}</pre></details>
<details><summary>Gitの物証</summary><p>取得時点の作業ツリー全体。別作業の変更を含みます。</p><pre>git status --short\n{esc(git_status)}\ngit diff --stat\n{esc(git_diff)}</pre></details></div></html>'''
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    temporary = TARGET.with_suffix(".html.tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, TARGET)
    print(json.dumps({"path": str(TARGET), "bytes": TARGET.stat().st_size}))


if __name__ == "__main__":
    main()
