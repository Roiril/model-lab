"""joint-test — レーザー嵌合キャリブレーション治具（3Dの servo-test 相当）。

実機の最初のテストカット用。本体(laser-bot)を切る前にこれだけ切って、
フィンガーの押し込み具合から KERF を実測 → laser_core.KERF に焼き込む。

KERF を 3 通り（0.0 / 0.1 / 0.2mm）並べて出し、一番気持ちよく嵌るものを採用する。

実行: python models/laser-joint-test/build.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
import laser_core as lc

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "exports", "laser")
os.makedirs(OUT_DIR, exist_ok=True)

A = 44.0   # 嵌合エッジ長 mm
B = 16.0   # 帯の幅 mm
KERFS = [0.0, 0.1, 0.2]   # 試すカーフ


def strip(fingered_edge, male, kerf):
    """A x B の短冊。fingered_edge だけフィンガー、他3辺は直線。"""
    edges = {e: True for e in ("bottom", "right", "top", "left")}  # 直線(n=1 male)
    plain = {e: 1 for e in edges}                                  # n=1 で直線
    edges[fingered_edge] = male
    plain[fingered_edge] = lc.finger_count(A if fingered_edge in ("bottom", "top") else B)
    return lc.rect_panel(A, B, edges, n_over=plain, kerf=kerf)


def main():
    cut = []
    eng = []
    y = 0.0
    for k in KERFS:
        x = 0.0
        # male（凸コーム） bottom 辺
        cut.append((strip("bottom", True, k), x, y)); x += A + 10
        # female（凹コーム） top 辺（押し込むと male と噛む）
        cut.append((strip("top", False, k), x, y))
        # ラベル代わりにカーフ値を小さな円で（0個=0.0, 1=0.1, 2=0.2）… は省略、座標で識別
        y += B + 14
    path = os.path.join(OUT_DIR, "joint-test.svg")
    sheet = lc.write_svg(path, cut, eng)
    print(f"joint-test: kerfs {KERFS}  (上から 0.0 / 0.1 / 0.2mm)")
    print(f"  各行: 左=male  右=female。2枚を 90°に組んでフィンガーの噛み/ガタを確認")
    print(f"  t={lc.MAT_T}mm  finger {lc.finger_count(A)} / edge {A}mm")
    print(f"  sheet {sheet[0]:.1f} x {sheet[1]:.1f} mm")
    print(f"  wrote {path}")


if __name__ == "__main__":
    main()
