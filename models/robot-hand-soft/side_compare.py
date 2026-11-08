"""横からの参考画像とモデルの厚みを、同じ計器で測って並べる。py -3.11 で動かす。

py -3.11 models/robot-hand-soft/side_compare.py <モデルの横の画像.png> <出力.png>

- 大きさは人差し指の長さ（指先の頂点から関節 j3 まで）でそろえる
- 人差し指の軸に垂直な線で、黒い部分の長さを測る
  指の奥行き: 指先から 0.16 / 0.50 / 0.85 の位置（指先の節・中の節・根元側の節の中ほど）
  手のひらの厚み: 関節 j3 から手首の側へ 0.30 / 0.60 の位置
- 計器の校正: 同じ画像を 2 回測って一致すること、太さの分かっている帯（合成画像）を測って合うこと
- 参考画像は横から 1 枚なので、指の幅は写らない。幅との比はモデルの寸法から出す
"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P

REF = r"C:\Users\kouga\Pictures\Screenshots\スクリーンショット 2026-11-08 100411.png"
REF_UP = 5                      # 参考画像を拡大してから測る倍率
# 参考画像の人差し指の先の頂点と関節 j3 の断面の中心（元の画像の px。5 倍に拡大した画像で、光の反射で切れていない列の輪郭の中点を結んだ線から読んだ）
REF_TIP = (5.0, 88.4)
REF_J3 = (82.0, 80.0)
THRESH = 150                    # 灰色の値がこれより暗い画素を手とする（参考の背景は 205 前後）
FINGER_AT = (0.16, 0.50, 0.85)
PALM_AT = (0.30, 0.60)
FONT = r"C:\Windows\Fonts\BIZ-UDGothicB.ttc"
SHOW_L = 420
GAP = 0.03                      # 明るい切れ目をまたぐ幅（指の長さとの比）。参考はつやのある金属で、反射が指を横切る                    # 並べる画像での指の長さ [px]


def mask_of(gray):
    m = (gray < THRESH).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    h, w = m.shape
    ff = np.pad(1 - m, 1, constant_values=1).astype(np.uint8)
    seed = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(ff, seed, (0, 0), 2)
    return ff[1:-1, 1:-1] != 2


def run_length(mask, p, n, gap, step=0.25):
    """点 p から ±n の向きへ、手の画素が続く長さ [px]。gap 以下の明るい切れ目（光の反射）はまたぐ。"""
    h, w = mask.shape
    ends = []
    for sgn in (1, -1):
        t, last = 0.0, 0.0
        while True:
            t += step
            q = p + sgn * n * t
            x, y = int(round(q[0])), int(round(q[1]))
            if not (0 <= x < w and 0 <= y < h):
                break
            if mask[y, x]:
                last = t
            elif t - last > gap:
                break
        ends.append(p + sgn * n * last)
    return float(np.linalg.norm(ends[0] - ends[1])), ends


def measure(mask, tip, j3):
    tip, j3 = np.array(tip, float), np.array(j3, float)
    L = float(np.linalg.norm(j3 - tip))
    a = (j3 - tip) / L
    n = np.array([-a[1], a[0]])
    if n[1] > 0:
        n = -n          # n は画面の上（手の甲の側）を向く
    gap = GAP * L
    out = {"L_px": L, "finger": [], "palm": [], "up": [], "segs": []}
    for f in FINGER_AT:
        p = tip + a * f * L
        d, e = run_length(mask, p, n, gap)
        out["finger"].append(d / L)
        out["up"].append(float(np.linalg.norm(e[0] - p)) / L)
        out["segs"].append(e)
    for k in PALM_AT:
        p = j3 + a * k * L
        d, e = run_length(mask, p, n, gap)
        out["palm"].append(d / L)
        out["up"].append(float(np.linalg.norm(e[0] - p)) / L)
        out["segs"].append(e)
    return out


def calibrate():
    """太さの分かっている帯を測る。帯の太さ / 長さ = 0.20 になるはず。"""
    img = np.full((400, 800), 205, np.uint8)
    cv2.line(img, (100, 200), (500, 160), 20, 81)
    tip, j3 = (100, 200), (500, 160)
    L = np.hypot(400, 40)
    r = measure(mask_of(img), tip, j3)
    want = 81 / L
    ok = all(abs(v - want) < 0.01 for v in r["finger"][1:])
    same = measure(mask_of(img), tip, j3)["finger"] == r["finger"]
    return ok and same, f"校正: 太さ {want:.3f} の帯を {', '.join(f'{v:.3f}' for v in r['finger'][1:])} と読んだ / 同じ画像を 2 回測って一致 {same}"


def scaled(rgb, tip, j3, segs):
    L = np.linalg.norm(np.array(j3) - np.array(tip))
    s = SHOW_L / L
    im = Image.fromarray(rgb).resize((max(1, int(rgb.shape[1] * s)), max(1, int(rgb.shape[0] * s))), Image.LANCZOS)
    dr = ImageDraw.Draw(im)
    for i, (e0, e1) in enumerate(segs):
        col = (220, 40, 40) if i < len(FINGER_AT) else (40, 90, 230)
        dr.line([tuple(e0 * s), tuple(e1 * s)], fill=col, width=4)
    dr.line([tuple(np.array(tip) * s), tuple(np.array(j3) * s)], fill=(30, 170, 60), width=2)
    return im, s


def main():
    model_png, out_png = sys.argv[1], sys.argv[2]
    log = []
    ok, msg = calibrate()
    log.append(msg)
    ref = Image.open(REF).convert("RGB")
    ref = np.array(ref.resize((ref.width * REF_UP, ref.height * REF_UP), Image.LANCZOS))
    rtip = tuple(np.array(REF_TIP) * REF_UP)
    rj3 = tuple(np.array(REF_J3) * REF_UP)
    rm = measure(mask_of(ref.mean(2)), rtip, rj3)
    mod = np.array(Image.open(model_png).convert("RGB"))[:, ::-1]      # 左右を反転して指先を左へ
    meta = json.load(open(model_png + ".json", encoding="utf-8"))
    w = mod.shape[1]
    mtip = (w - 1 - meta["index_tip"][0], meta["index_tip"][1])
    mj3 = (w - 1 - meta["index_j3"][0], meta["index_j3"][1])
    mm = measure(mask_of(mod.mean(2)), mtip, mj3)
    # 表
    rows = []
    names = ["指先の節", "中の節", "根元側の節 ※", "手のひら（j3 から 0.30）※", "手のひら（j3 から 0.60）※"]
    vals_r = rm["finger"] + rm["palm"]
    vals_m = mm["finger"] + mm["palm"]
    Lmm = meta["finger_len_mm"]
    for nm, a, b, ua, ub in zip(names, vals_r, vals_m, rm["up"], mm["up"]):
        rows.append((nm, a, b, ua, ub))
        log.append(f"{nm} / 指の長さ: 全体 参考 {a:.3f} モデル {b:.3f} / 軸から甲側の面まで 参考 {ua:.3f} モデル {ub:.3f}"
                   f"（モデル {b * Lmm:.1f}mm と {ub * Lmm:.1f}mm、参考の比をこのモデルの大きさに直すと {a * Lmm:.1f}mm と {ua * Lmm:.1f}mm）")
    B = P.SEG_BACK
    w0 = P.FINGERS["index"]["width"]
    tw = P.FINGERS["index"]["tip_width"]
    dw = [("根元側の節", B["seg1"] - P.SEG_FRONT, w0), ("中の節", B["seg2"] - P.SEG_FRONT, w0), ("指先の節", B["tip"] - P.TIP_FRONT, tw)]
    for nm, d, ww in dw:
        log.append(f"モデルの人差し指 {nm}: 奥行き {d:.2f}mm / 幅 {ww:.1f}mm = {d / ww:.2f}")
    # 並べた画像
    ri, rs = scaled(ref, rtip, rj3, rm["segs"])
    mi, ms = scaled(mod, mtip, mj3, mm["segs"])
    # 指の関節 j3 の位置をそろえて切り出す
    def crop(im, j3, s):
        cx, cy = j3[0] * s, j3[1] * s
        box = (int(cx - 520), int(cy - 300), int(cx + 420), int(cy + 420))
        c = Image.new("RGB", (box[2] - box[0], box[3] - box[1]), (205, 205, 205))
        c.paste(im.crop((max(box[0], 0), max(box[1], 0), min(box[2], im.width), min(box[3], im.height))),
                (max(-box[0], 0), max(-box[1], 0)))
        return c
    a, b = crop(ri, rj3, rs), crop(mi, mj3, ms)
    f = ImageFont.truetype(FONT, 24)
    fs = ImageFont.truetype(FONT, 21)
    tbl_h = 40 + 32 * (len(rows) + 2) + 32 * len(dw)
    canvas = Image.new("RGB", (a.width + b.width + 30, a.height + 70 + tbl_h), "white")
    canvas.paste(a, (0, 60))
    canvas.paste(b, (a.width + 30, 60))
    dr = ImageDraw.Draw(canvas)
    dr.text((10, 14), "参考（スクリーンショット 2026-11-08 100411、5 倍に拡大）", fill=(20, 20, 20), font=f)
    dr.text((a.width + 40, 14), "モデル（親指の側から直交投影、左右反転）", fill=(20, 20, 20), font=f)
    y = a.height + 80
    dr.text((10, y), "人差し指の長さ（指先〜関節 j3）で大きさをそろえた。赤=指の奥行き 青=手のひらの厚み 緑=指の軸", fill=(60, 60, 60), font=fs)
    y += 36
    dr.text((10, y), "測った場所（値は指の長さとの比）", fill=(20, 20, 20), font=fs)
    dr.text((470, y), "全体の厚み 参考 / モデル / 差", fill=(20, 20, 20), font=fs)
    dr.text((930, y), "軸から甲側の面まで 参考 / モデル / 差", fill=(20, 20, 20), font=fs)
    for nm, r_, m_, ur, um in rows:
        y += 32
        dr.text((10, y), nm, fill=(20, 20, 20), font=fs)
        dr.text((470, y), f"{r_:.3f} / {m_:.3f} / {m_ - r_:+.3f}", fill=(20, 20, 20), font=fs)
        dr.text((930, y), f"{ur:.3f} / {um:.3f} / {um - ur:+.3f}", fill=(20, 20, 20), font=fs)
    y += 32
    dr.text((10, y), "※ 全体の厚みは下に曲げた指と親指を含む（参考と同じ指さしの姿勢で撮った）", fill=(60, 60, 60), font=fs)
    for nm, d, ww in dw:
        y += 32
        dr.text((10, y), f"モデルの{nm}の奥行き / 幅: {d:.2f} / {ww:.1f} = {d / ww:.2f}（参考は横からの 1 枚で幅が写らない）", fill=(60, 60, 60), font=fs)
    tmp = out_png + ".tmp.png"
    canvas.save(tmp)
    os.replace(tmp, out_png)
    with open(out_png + ".json", "w", encoding="utf-8") as fp:
        json.dump({"log": log, "ref": vals_r, "model": vals_m}, fp, ensure_ascii=False, indent=1)
    print("\n".join(log))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
