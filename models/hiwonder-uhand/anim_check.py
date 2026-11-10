"""uHand の動きの定義と機構の計算を検査する。bpy は要らない。

py -3.11 models/hiwonder-uhand/anim_check.py [--json]
exit 0 なら合格。クリップを足したり kin.py・params.py を変えたりしたら、書き出す前に必ず通す。
  1. クリップの定義（anim/poses.json・anim/clips/*.json）の書式と値の範囲
  2. 量を端から端まで動かしたとき、指の連結が解けて、曲げが途中で戻らないこと
  3. 指の引き棒が端から端まで届くこと。伸び縮みで合わせている親指のクランクの伸びが決めた幅に収まること
  4. すべてのクリップのすべてのフレームで姿勢が計算できること
"""
import json
import math
import sys

import anim_lib
import kin

CRANK_STRETCH = (0.75, 1.35)   # 親指の銀のクランク。資料から仕組みが読めず、固定側から親指を追わせて伸びで合わせている（今の最大は 1.33）
SWEEP = 40


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    errors, report = [], {}
    clips, err = anim_lib.load_all()
    errors += err

    # 指: 曲げの連動
    for i, nm in enumerate(kin.FINGERS):
        prev, rows, rs = None, [], []
        try:
            for k in range(SWEEP + 1):
                s = kin.finger_solve(i, k / SWEEP)
                cur = (s["prox"], s["mid"] - s["prox"], s["tip"] - s["mid"])
                if prev and any(c < p - 1e-6 for c, p in zip(cur, prev)):
                    errors.append(f"{nm}: u = {k / SWEEP:.3f} で曲げが戻る")
                prev = cur
                rows.append(cur)
                _, _, g = kin.finger_horn(i, kin.finger_pose(i, k / SWEEP)[f"{nm}_prox"])
                rs.append(math.degrees(g))
        except ValueError as e:
            errors.append(str(e))
            continue
        report[nm] = dict(full_deg=[round(math.degrees(a), 1) for a in rows[-1]],
                          horn_deg=[round(min(rs), 1), round(max(rs), 1)])
        if any(abs(b - a) > 6.0 for a, b in zip(rs, rs[1:])):
            errors.append(f"{nm}: ホーンの角度が途中で飛ぶ")
    # 親指
    try:
        cs, hs = [], []
        for k in range(SWEEP + 1):
            _, info = kin.thumb_pose(k / SWEEP)
            cs.append(info["crank_stretch"])
            hs.append(math.degrees(info["horn"]))
        report["thumb"] = dict(horn_deg=[round(min(hs), 1), round(max(hs), 1)],
                               crank_stretch=[round(min(cs), 3), round(max(cs), 3)])
        if min(cs) < CRANK_STRETCH[0] or max(cs) > CRANK_STRETCH[1]:
            errors.append(f"thumb: クランクの伸びが {min(cs):.2f}〜{max(cs):.2f}（許す幅 {CRANK_STRETCH}）")
    except ValueError as e:
        errors.append(str(e))

    # クリップの全フレーム
    report["clips"] = {}
    for clip in clips:
        try:
            fr = anim_lib.frames(clip)
            for d in fr:
                kin.pose(d)
            report["clips"][clip["name"]] = dict(frames=len(fr), seconds=round((len(fr) - 1) / anim_lib.FPS, 2),
                                                 loop=clip["loop"])
        except ValueError as e:
            errors.append(f"{clip['name']}: {e}")

    report["errors"] = errors
    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        for nm in kin.FINGERS:
            if nm in report:
                r = report[nm]
                print(f"{nm:7s} 握りきったときの関節 {r['full_deg']} 度 / ホーンの角度 {r['horn_deg']} 度")
        if "thumb" in report:
            print(f"thumb   ホーンの角度 {report['thumb']['horn_deg']} 度 / クランクの伸び {report['thumb']['crank_stretch']}")
        for name, c in report["clips"].items():
            print(f"clip {name:18s} {c['frames']:4d} フレーム {c['seconds']:5.2f} 秒{' 繰り返し' if c['loop'] else ''}")
        for e in errors:
            print("NG:", e)
        print("合格" if not errors else f"不合格（{len(errors)} 件）")
    sys.exit(1 if errors else 0)


main()
