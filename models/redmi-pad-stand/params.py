"""Redmi Pad SE 11 インチ用スタンドの寸法。

この部品は側面の輪郭（Y-Z 断面）を X 方向へ押し出した一体物。
輪郭の計算は mm で行い（profile.py）、Blender へ渡すときに m へ直す。
座標: X = 左右（中央 0）、Y = 奥行き（前端 0、奥が +）、Z = 高さ（机 0）。
"""

MODEL_NAME = "redmi-pad-stand"

# --- 本体（出典: Xiaomi 公式仕様 https://www.mi.com/jp/product/redmi-pad-se/specs/） ---
TABLET_W_MM = 255.53     # 長辺
TABLET_H_MM = 167.08     # 短辺
TABLET_T_MM = 7.36       # 厚さ
TABLET_MASS_KG = 0.478
# 11 インチ 16:10 の表示域 236.8 x 148.0 mm から求めた額縁の幅（下端）
TABLET_BEZEL_MM = (TABLET_H_MM - 148.0) / 2.0   # 9.54mm

# --- 置く角度と受け口 ---
ANGLE_DEG = 60.0         # 机から測った画面の傾き。動画・閲覧向け
SEAT_Z_MM = 20.0         # 本体の背面下端の高さ（画面を持ち上げる）
GROOVE_MM = 12.0         # 受け口の幅（背面の支えに垂直に測る）。裸の本体 7.36mm と薄いケースが入る
LIP_H_MM = 6.0           # 前の返しの高さ（支えに沿って測る）。額縁 9.5mm より低くして画面を隠さない
LIP_T_MM = 12.0          # 返しの厚さ（丸い先端を作るため厚くする）
LIP_FRONT_Y_MM = 20.0    # 返しの外側の角の前後位置。前面の傾き（約 63°）を決める
FRONT_STEP_MM = 2.0      # 前の下端の立ち上がり。60°の刃にしない
SUPPORT_MM = 115.0       # 背面の支えの長さ（頂部の丸めの前の仮想の角まで）

# --- 後ろへ流れる形 ---
BACK_DEG = 63.0          # 頂部から後ろへ下りる面の角度（水平から）
TAIL_H_MM = 10.0         # 後ろの尾の厚さ
DEPTH_MM = 192.0         # 奥行き（前端から尾の端まで）
WIDTH_MM = 150.0         # 机に接する横幅。横置き専用。本体 255mm の両端のスピーカーをふさがない幅
TOP_WIDTH_MM = 132.0     # 頂部の横幅。左右の面を上へ向けてすぼめる（台形に見せる。サポート不要）

# --- 丸め ---
R_FRONT_MM = 5.0         # 前の下端の立ち上がりから斜面への角
R_TOP_MM = 10.0          # 支えの頂部
R_KNEE_MM = 50.0         # 後ろの面が尾へ流れ込む凹んだ曲がり
R_TAIL_MM = 6.0          # 尾の上の角
R_LIP_OUT_MM = 6.0       # 返しの外側の角
R_LIP_IN_MM = 4.2        # 返しの内側の角
R_GROOVE_FRONT_MM = 1.5  # 受け口の前の隅（凹）
R_GROOVE_BACK_MM = 1.0   # 受け口の奥の隅（凹）。本体の角が座る
R_SIDE_MM = 4.0          # 左右の面の縁の丸め（机に接する下の縁は丸めない）
SIDE_STEPS = 8           # 縁の丸めの分割数

# 円弧の分割
ARC_STEP_DEG = 3.0
ARC_MAX_CHORD_MM = 0.6


def validate():
    for name, value in dict(
        SEAT_Z_MM=SEAT_Z_MM, GROOVE_MM=GROOVE_MM, LIP_H_MM=LIP_H_MM, LIP_T_MM=LIP_T_MM,
        SUPPORT_MM=SUPPORT_MM, TAIL_H_MM=TAIL_H_MM, DEPTH_MM=DEPTH_MM, WIDTH_MM=WIDTH_MM,
        R_SIDE_MM=R_SIDE_MM,
    ).items():
        if value <= 0:
            raise ValueError(f"{name} must be positive")
    if not 45.0 <= ANGLE_DEG <= 75.0:
        raise ValueError("ANGLE_DEG must be within 45..75")
    if GROOVE_MM <= TABLET_T_MM + 1.0:
        raise ValueError("groove must leave at least 1mm around the bare tablet")
    if LIP_H_MM >= TABLET_BEZEL_MM:
        raise ValueError("lip must stay below the screen bezel")
    # 縁の丸めで凸の角が潰れないこと
    if min(R_TOP_MM, R_TAIL_MM, R_LIP_OUT_MM, R_LIP_IN_MM, R_FRONT_MM) <= R_SIDE_MM:
        raise ValueError("convex corner radii must exceed R_SIDE_MM")


validate()
