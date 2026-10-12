"""既定の「プログラム」: サーボ角ごとの 5 x 5 の高さ表 [mm]。単位 mm、表の添字は table[j][i]（j = 行 = Y、i = 列 = X）。

K 枚（params.K = 5）。表 k はサーボ角 params.TABLE_THETA[k] で表示される。
THETA_FLAT（90 度）の表 = 全部 0（平らな表）。= 組立角。ここを変える前に cams.py が拒否しないか確かめる:
  py -3.11 models/tangible-pixel-cube/test_cams.py（既定の表が作れるか、校正も一緒に走る）

作れる表の制約（cams.py が CamError で拒否する。停止区間 ±13.0 度、足の横ずれ上限 9mm の下で実測）:
- 高さは -3..+3mm
- 隣り合う表（サーボ角で 34 度 = 軸で 76 度）で、同じ画素の高さの組が作れる最大: 低い方 -3 -> 高い方 +0.3、-2 -> +1.9、-1 以上 -> +3
  （面一の 0 から -3 へも +3 へも可。-3 から +3 は不可）
- 軸が一周すると端の表 0 と表 4 が 56 度で隣り合う。この組はさらに厳しい: -3 -> -2.0、-2 -> -0.9、-1 -> +0.3、0 -> +1.5、+1 -> +2.7
  （端の 2 枚は、その画素で似た高さにしておく）
- 表の間隔は軸で 2w = 26 度以上
- 既定の表は 13.25 度まで通る（13.5 度から作れない）。停止区間 13.0 度は、位相誤差の余裕 1.0 度以上のために、通る範囲の最大に近く取った
表を変えたら刷り直すのはカム 25 枚だけ（kinematics・歯車・他の部品は共通）。
"""
import math

N = 5


def _grid(f):
    return [[f(i - 2, j - 2) for i in range(N)] for j in range(N)]


def _q(v):
    """0.5mm 刻みに丸める"""
    return round(v * 2) / 2


def flat():
    return _grid(lambda x, y: 0.0)


def dip(depth=-3.0, ring=-1.5, diag=-1.0, rest=-0.5):
    """中央が一番凹み、周囲が少し凹む"""
    def f(x, y):
        r = math.hypot(x, y)
        if r < 0.5:
            return depth
        if r < 1.2:
            return ring
        if r < 1.5:
            return diag
        return rest
    return _grid(f)


def bump(height=3.0, ring=1.5, diag=1.0, rest=0.5):
    """内側から押されてぼこっと出る"""
    def f(x, y):
        r = math.hypot(x, y)
        if r < 0.5:
            return height
        if r < 1.2:
            return ring
        if r < 1.5:
            return diag
        return rest
    return _grid(f)


def corners(top=1.5, near=0.5):
    """四隅だけが出る（位置が動く例）"""
    def f(x, y):
        if abs(x) == 2 and abs(y) == 2:
            return top
        if (abs(x) == 2 and abs(y) == 1) or (abs(x) == 1 and abs(y) == 2):
            return near
        return 0.0
    return _grid(f)


def wave(amp=0.9, mask_with=None):
    """斜めに進む波。mask_with の表で正の画素は 0 にする（端の表との角度差を守るため）"""
    t = _grid(lambda x, y: _q(amp * math.sin(2 * math.pi * (x + 0.5 * y) / 5)))
    if mask_with is not None:
        for j in range(N):
            for i in range(N):
                if mask_with[j][i] > 0:
                    t[j][i] = 0.0
    return t


_T_CORNERS = corners()

# 並び順 = サーボ角の昇順（TABLE_THETA に対応）。表 2 が平ら（サーボ 90 度）
TABLES = [
    wave(0.9, mask_with=_T_CORNERS),   # 表 0 サーボ 22 度: 波
    dip(),                             # 表 1 サーボ 56 度: 中央が一番凹み周囲が少し凹む
    flat(),                            # 表 2 サーボ 90 度: 平ら（組立角）
    bump(),                            # 表 3 サーボ 124 度: 内側から押してぼこっと出る
    _T_CORNERS,                        # 表 4 サーボ 158 度: 四隅が出る
]
NAMES = ["wave", "dip", "flat", "bump", "corners"]
LABELS_JA = ["波", "中央が凹む", "平ら", "中央がぼこっと出る", "四隅が出る"]
