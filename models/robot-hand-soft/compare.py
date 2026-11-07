"""参考画像とモデルの描画を比べる。py -3.11 で動かす。

- 計器の校正: 同じ画像同士 / 指を 1 本塗りつぶした画像
- 視点ごとの IoU（全体と、台座を除いた手だけ）
- 比較画像（参考 / モデル / 差）。ファイルが 1 つでも欠けたら落ちる。
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import metrics as MT

VIEWS = ["front", "oblique", "rear"]
LABEL = {"front": "正面", "oblique": "斜め後ろ", "rear": "真後ろ"}
TARGET = {"front": 0.90, "oblique": 0.85, "rear": 0.90}
# 指を塗りつぶす帯（u0,v0,u1,v1,太さ）。参考画像の px。計器の校正だけに使う。
ERASE = {
    "front": (1085, 245, 880, 600, 110),      # 小指
    "oblique": (260, 240, 420, 600, 120),     # 小指
    "rear": (195, 245, 400, 600, 120),        # 小指
}
FONT = r"C:\Windows\Fonts\BIZ-UDGothicB.ttc"


def erase_finger(rgb, band):
    """指の帯を、壁の色で塗る。"""
    out = rgb.copy()
    u0, v0, u1, v1, w = band
    wall = rgb[60, 60].tolist()
    cv2.line(out, (u0, v0), (u1, v1), wall, w)
    return out


def calibrate(log):
    ok = True
    for v in VIEWS:
        rgb = MT.load_rgb(os.path.join(MT.REF_DIR, MT.REFS[v]))
        m = MT.hand_mask(rgb)
        same = MT.iou(m, MT.hand_mask(rgb.copy()))
        gone = MT.iou(m, MT.hand_mask(erase_finger(rgb, ERASE[v])))
        lost = 1 - m.sum() and (m.sum() - MT.hand_mask(erase_finger(rgb, ERASE[v])).sum()) / m.sum()
        log.append(f"校正 {LABEL[v]}: 同じ画像 {same:.4f} / 小指を消した画像 {gone:.4f}（面積 {lost*100:.1f}% 減）")
        ok &= same > 0.999 and gone < 0.98
    return ok


def side_by_side(view, ref_rgb, mod_rgb, ref_m, mod_m, score, score_hand, out_path, ref_name, mod_name):
    h, w = ref_rgb.shape[:2]
    # 差: 灰=一致、赤=参考にだけある、青=モデルにだけある
    d = np.full((h, w, 3), 245, np.uint8)
    d[ref_m & mod_m] = (150, 150, 150)
    d[ref_m & ~mod_m] = (220, 40, 40)
    d[~ref_m & mod_m] = (40, 80, 230)
    canvas = np.full((h + 90, w * 3 + 40, 3), 255, np.uint8)
    for i, a in enumerate((ref_rgb, mod_rgb, d)):
        canvas[90:90 + h, i * (w + 20):i * (w + 20) + w] = a
    im = Image.fromarray(canvas)
    dr = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 26)
    dr.text((10, 10), f"参考: {ref_name}", fill=(20, 20, 20), font=f)
    dr.text((w + 30, 10), f"モデル: {mod_name}", fill=(20, 20, 20), font=f)
    dr.text((2 * w + 50, 10), f"{LABEL[view]} IoU 全体 {score:.3f} / 台座を除く {score_hand:.3f}", fill=(20, 20, 20), font=f)
    dr.text((2 * w + 50, 48), "赤=参考だけ 青=モデルだけ", fill=(90, 90, 90), font=f)
    tmp = out_path + ".tmp.png"
    im.save(tmp)
    os.replace(tmp, out_path)


def main():
    render_dir = sys.argv[1] if len(sys.argv) > 1 else MT.RENDER_DIR
    paths = {}
    for v in VIEWS:
        r = os.path.join(MT.REF_DIR, MT.REFS[v])
        m = os.path.join(render_dir, f"model-{v}.png")
        for p in (r, m):
            if not os.path.isfile(p):
                sys.exit(f"ファイルがありません: {p}")
        paths[v] = (r, m)
    log = []
    cal = calibrate(log)
    log.append("校正 " + ("合格" if cal else "不合格"))
    res = {}
    allok = cal
    for v in VIEWS:
        rgb_r, rgb_m = MT.load_rgb(paths[v][0]), MT.load_rgb(paths[v][1])
        if rgb_m.shape != rgb_r.shape:
            rgb_m = cv2.resize(rgb_m, rgb_r.shape[1::-1], interpolation=cv2.INTER_AREA)
        mr, mm = MT.hand_mask(rgb_r), MT.hand_mask(rgb_m)
        # 手首のヒンジより上だけ（参考画像の手のひら下端の行）
        rows = np.where(mr.sum(1) > 0)[0]
        cut = int({"front": 940, "oblique": 925, "rear": 940}[v])
        s = MT.iou(mr, mm)
        sh = MT.iou(mr[:cut], mm[:cut])
        res[v] = {"iou": round(s, 4), "iou_hand_only": round(sh, 4)}
        allok &= s >= TARGET[v]
        log.append(f"{LABEL[v]}: IoU 全体 {s:.4f}（目標 {TARGET[v]:.2f}）/ 台座を除く {sh:.4f}")
        for nm, rgn in (("壁", (20, 200, 20, 200)), ("机", (1040, 1200, 20, 200)), ("手のひら", (640, 720, 640, 760))):
            a, b, c, e = rgn
            log.append(f"  色 {nm}: 参考 {rgb_r[a:b, c:e].mean((0, 1)).round().astype(int)} モデル {rgb_m[a:b, c:e].mean((0, 1)).round().astype(int)}")
        side_by_side(v, rgb_r, rgb_m, mr, mm, s, sh, os.path.join(render_dir, f"compare-{v}.png"),
                     os.path.basename(paths[v][0]), os.path.basename(paths[v][1]))
    print("\n".join(log))
    with open(os.path.join(render_dir, "iou.json.tmp"), "w", encoding="utf-8") as f:
        json.dump({"calibration": log, "views": res}, f, ensure_ascii=False, indent=1)
    os.replace(os.path.join(render_dir, "iou.json.tmp"), os.path.join(render_dir, "iou.json"))
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
