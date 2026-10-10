"""C3/C4の成果物と検証結果を単一HTMLにまとめる。"""
from __future__ import annotations

import base64
from html import escape
import json
import os
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
STYLE = Path.home() / "Projects/Web/claude-global/skills/visual-deliverable/assets/report.css"


def image(path, caption):
    if not path.exists():
        raise FileNotFoundError(path)
    src = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<figure><img src="data:image/png;base64,{src}" alt="{escape(caption)}"><figcaption>{escape(caption)}</figcaption></figure>'


def value_rows(data, prefix=""):
    """限定した検証JSONの数値を、値を隠さず表へ出す。"""
    rows = []
    for key, value in data.items():
        label = f"{prefix} / {key}" if prefix else key
        if isinstance(value, dict):
            rows.extend(value_rows(value, label))
        elif not isinstance(value, list) or len(value) <= 6:
            rows.append(f'<tr><td>{escape(label)}</td><td>{escape(str(value))}</td></tr>')
    return rows


def main():
    sections = []
    for variant, title, desc in (
        ("c3", "C3 · 立方格子の波", "25枚の正方形を5列に分けた。中央から外へ隆起が移る。平らな面に隠れていた規則が動きとして現れる。"),
        ("c4", "C4 · 六角格子の呼吸", "19個の六角形を中心と2つの環へ分けた。中心ほど深く持ち上がる。格子の輪郭と空隙の影が変わる。"),
    ):
        model = f"mystery-box-sg92r-{variant}"
        folder = ROOT / "models" / model
        manifest = json.loads((folder / "build/manifest.json").read_text(encoding="utf-8"))
        meta = manifest.get("meta", {})
        verify = json.loads((folder / "build/verify_report.json").read_text(encoding="utf-8"))
        delivery = json.loads((folder / "build/delivery_report.json").read_text(encoding="utf-8"))
        integration = json.loads((folder / "build/integration_report.json").read_text(encoding="utf-8"))
        review_path = folder / "build/print_review.json"
        print_review = json.loads(review_path.read_text(encoding="utf-8")) if review_path.exists() else None
        path_review_file = folder / "build/print_path_review.json"
        path_review = json.loads(path_review_file.read_text(encoding="utf-8")) if path_review_file.exists() else None
        dimensions = " × ".join(str(x) for x in meta.get("dimensions_mm", []))
        model_url = f"http://localhost:3000/?model={model}"
        motion_url = f"http://localhost:3000/viewer/lattice/index.html?model={model}&amp;mode=physics"
        photos = image(folder / "build/hero-rest.png", "低い位置。格子の並びを見る。")
        raised_image = "hero-center.png" if variant == "c3" else "hero-raised.png"
        raised_caption = "中央の列が持ち上がった位置。実部品のSTLから描画。" if variant == "c3" else "中心と2つの環が持ち上がった位置。実部品のSTLから描画。"
        photos += image(folder / "build" / raised_image, raised_caption)
        steps = meta.get("assembly_steps", [])
        step_html = "".join(f"<li>{escape(str(step).replace('列キャリア', '格子列').replace('片道2秒のquintic補間で', '始めと終わりをゆっくり動かしながら片道2秒で'))}</li>" for step in steps)
        parts = "".join(f'<tr><td>{escape(p["label"])}</td><td>{"印刷する" if p.get("print") else "既製部品"}</td></tr>' for p in manifest["parts"])
        downloads = "".join(f'<li><a href="../prints/{model}/{escape(p.name)}">{escape(p.name)}</a></li>' for p in sorted((ROOT / "prints" / model).glob("*.3mf")))
        limitations = meta.get("limitations", [])
        if isinstance(limitations, str):
            limitations = [limitations]
        limitations_html = "".join(f"<li>{escape(str(x))}</li>" for x in limitations)
        decisions_html = "".join(f"<li>{escape(str(x))}</li>" for x in meta.get("decisions", []))
        totals = "".join(f'<tr><td>{escape(material)}</td><td>{round(result["prediction_s"]/60)}分</td><td>{result["weight_g"]:.1f} g</td></tr>' for material, result in delivery["plates"]["full"]["materials"].items())
        fit_totals = "".join(f'<tr><td>{escape(material)}</td><td>{round(result["prediction_s"]/60)}分</td><td>{result["weight_g"]:.1f} g</td></tr>' for material, result in delivery["plates"]["fit_test"]["materials"].items())
        print_notes = ""
        if print_review:
            print_notes = '<h4>印刷する向きと橋渡し</h4><ul>' + ''.join(
                f'<li>{escape(str(row.get("surface", "")))} {escape(str(row.get("decision", "")))}</li>'
                for row in print_review.get("parts", [])) + '</ul>'
        status = "記録した計算検査は適合。" if verify.get("ok", verify.get("pass")) else "計算検査に未解決の項目がある。"
        if not integration["ok"]:
            raise ValueError(f"Final artifact audit failed: {model}")
        print_status = "記録した印刷経路の検査は適合。" if delivery["status"] == "ok" else "印刷経路に要確認箇所がある。詳細は末尾の検証記録を参照。"
        if path_review and path_review.get("status") == "accepted_with_fit_test":
            print_status = "スライスの警告が残る箇所は寸法で確認した。短い橋渡し等をサポートなしで造形する。実物の試し刷りは未実施。"
        part_count = sum(bool(p.get("print")) and not p.get("fit_only", False) for p in manifest["parts"])
        requirement_rows = (
            ("依頼の動き", "25枚の正方形が5列ごとに最大3mm持ち上がる。" if variant == "c3" else "19個の六角リングが3群で最大5.909／3.939／1.970mm持ち上がる。"),
            ("印刷", f"本体は{part_count}部品を1枚に配置。PLAとPETGの印刷データを用意。サポートなし。"),
            ("組み立て", "印刷部品とSG92R付属ホーンを使用。挿入経路と固定部の干渉を計算。保持力と着脱感は未実測。"),
            ("動く範囲", "15〜165°を2.5°刻みで検査。片道2秒。" if variant == "c3" else "10〜170°を2.5°刻みで検査。片道1.5秒。"),
            ("検証", ("全210組を61姿勢で確認。" if variant == "c3" else "全136組を65姿勢で確認。") + "指定した圧入・ばね以外の干渉は基準内。必要トルクの概算は停動トルクの1/3以内。実物の摩擦は未測定。"),
        )
        requirements = ''.join(f'<tr><th>{escape(label)}</th><td>{escape(result)}</td></tr>' for label, result in requirement_rows)
        sections.append(f'''<section>
<h2>{title}</h2><p>{desc}</p><p class="numbers">閉じた外形 {dimensions} mm。動作中の最大高さ {integration['max_height_mm']:.3f} mm。</p>
<p><a href="{model_url}">Studioで形を見る</a>　<a href="{motion_url}">動きを再生する</a></p>
<div class="pair">{photos}</div>
<h3>要件ごとの結果</h3><p>幾何学の規則を持つ可動天面。SG92R一台で駆動する。上向きで使用する。印刷部品と付属ホーンで組み立てる。</p>
<div class="tblwrap"><table><tbody>{requirements}</tbody></table></div>
<p>{status}詳細な合否と測定値は専用画面に表示する。検証JSONはこのHTMLにも埋め込んだ。実物での動作は未確認。</p>
<h3>決めたこと</h3><ul>{decisions_html}</ul>
<p>寸法を変更するときの定数名と刻みは<a href="../models/{model}/README.md">組み立て説明</a>に記載。<a href="../models/{model}/params.py">寸法の設定ファイル</a>から調整できる。</p>
<h3>部品と組み立て</h3><div class="tblwrap"><table><thead><tr><th>部品</th><th>準備</th></tr></thead><tbody>{parts}</tbody></table></div><ol>{step_html}</ol>
<p><a href="../models/{model}/demo/demo.ino">Arduinoの制御例</a>。起動時は90°で停止する。ホーンの向きを合わせてからシリアルモニターでgを送る。sで現在位置に止める。実機への書き込みと動作確認は未実施。</p>
<h3>印刷するファイル</h3><p>X1 Carbon。0.4mmノズル。積層ピッチ0.2mm。Textured PEIプレート。{print_status}</p><div class="tblwrap"><table><thead><tr><th>材料</th><th>全体の予測時間</th><th>全体の使用量</th></tr></thead><tbody>{totals}</tbody></table></div><div class="tblwrap"><table><thead><tr><th>材料</th><th>試片の予測時間</th><th>試片の使用量</th></tr></thead><tbody>{fit_totals}</tbody></table></div>{print_notes}<ul>{downloads}</ul>
<h3>実物で確かめること</h3><ul>{limitations_html}</ul>
<p>初めに嵌合用の試片を刷る。ホーンの左右を合わせる。次にガイドの滑りを手で確かめる。最後に低速でサーボを動かす。</p>
<details><summary>保存した数値と検証記録</summary><pre>{escape(json.dumps({'integration':integration,'verify':verify,'delivery':delivery,'print_review':print_review,'print_path_review':path_review}, ensure_ascii=False, indent=2))}</pre></details>
</section>''')
    css = STYLE.read_text(encoding="utf-8")
    output = f'''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>住人の箱 C3・C4 — 格子が動く面</title><style>{css}
.wrap{{max-width:68rem}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}img{{width:100%;height:auto;display:block}}figure{{margin:0}}section{{padding-block:32px;border-top:2px solid var(--line)}}h3{{font-size:var(--fs-md)}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:var(--fs-xs)}}.numbers{{font-variant-numeric:tabular-nums}}@media(max-width:600px){{.pair{{grid-template-columns:1fr}}}}
</style><main class="wrap"><p class="eyebrow">MODEL-LAB · 2026-10-10</p><h1>住人の箱 C3・C4</h1><p class="sub">内側から押されるように変わる2つの格子。</p>
<div class="lead"><p>C3は正方形の波。C4は六角形の段階的な盛り上がり。どちらもSG92R一台で動かす。面の並びと陰影の変化を見せる卓上デモ。</p></div>
<p>画像の色は表示用。用意した印刷データは単色で、実際の色は使うフィラメントで決まる。</p>
<h2>決めたこと</h2><p>可動面を上向きにした。戻る力には自重を使う。ばねは付けない。形はC1・C2と同じ立方体を出発点にした。</p>
<h2>譲ったこと</h2><p>各セルを別々に命令する機能は持たない。1台のサーボから決まった変形を作る。指で押した場所の検出も含めない。サーボに加えて電源と制御用の回路が必要。</p>
{''.join(sections)}
<p class="note">サーボの形はリポジトリ内のSG92R正本を使用。公称の停動トルク2.5kg·cmと速度0.1秒/60°は<a href="https://towerpro.com.tw/product/sg92r-7/">TowerProの仕様</a>を参照。C4の格子は「プロジェクト・ヘイル・メアリー」からの着想。映画小道具の再現寸法ではない。</p></main></html>'''
    path = ROOT / "reports/2026-10-10_lattice-c3-c4.html"
    temp = path.with_suffix(".tmp")
    temp.write_text(output, encoding="utf-8", newline="\n")
    os.replace(temp, path)
    print(path)


if __name__ == "__main__":
    main()
