# -*- coding: utf-8 -*-
"""バンディド (Bandido) カードの寸法・設定（単位: m）。

協力ゲーム「バンディド」は全てカード。トンネル札で脱獄路をふさぐ。
実物写真（白背景に1枚ずつ）から輪郭抽出したカード面画像をテクスチャに使う。
写真実測でカードは 1:2 の縦長（long/short = 2.00）。
"""

# --- カード寸法 -----------------------------------------------------------
CARD_W = 0.044      # 44mm 幅（写真アスペクト 1:2 に合わせた縦長カード短辺）
CARD_H = 0.088      # 88mm 高さ（長辺 = 短辺 x2）
CARD_T = 0.0015     # 厚み 1.5mm（表示用。実カードより厚め）

# 角丸半径: テクスチャのアルファ半径（短辺の 6.6%）と物理的に一致させる。
#   tex は 短辺 TEX_W px に対し半径 CORNER_FRAC*TEX_W px の角丸。
#   px/mm は縦横同一（TEX_W/44 = TEX_H/88）なので mm 半径も縦横一致する。
CORNER_FRAC = 0.066
CARD_R = CARD_W * CORNER_FRAC     # ≈ 2.9mm

# --- テクスチャ解像度（縦長 1:2）----------------------------------------
TEX_W = 800
TEX_H = 1600

# --- 入力（git 管理外・ユーザーの生写真）--------------------------------
# 白背景にカード1枚を撮った JPG 群。ファイル名がカード名になる。
RAW_DIR = r"C:/Users/kouga/Downloads/bandyd"

# --- カードの分類（表示グループ用）-------------------------------------
# g1..g24 = トンネル札 / l1..l7 = 人物入り特殊札 / bandy = 開始札 / ura = 共通の裏
TUNNEL = [f"g{i}" for i in range(1, 25)]
SPECIAL = [f"l{i}" for i in range(1, 8)]
START = ["bandy"]
BACK = "ura"                       # 全カード共通の裏面テクスチャ

# 表面を持つ全カード（裏 ura は面テクスチャとして共有）
FACE_CARDS = TUNNEL + SPECIAL + START

# --- デッキ構成（実物の同梱枚数）---------------------------------------
# トンネル札 g* は各 2 枚、特殊札 l* は各 3 枚、開始札 bandy は 1 枚。
# 俯瞰（一覧）GLB はこの実枚数で並べる。単体 GLB は種類ごと 1 つ。
TUNNEL_COPIES = 2
SPECIAL_COPIES = 3
START_COPIES = 1


def copies_of(name):
    if name in TUNNEL:
        return TUNNEL_COPIES
    if name in SPECIAL:
        return SPECIAL_COPIES
    return START_COPIES

# --- 側面色（テクスチャ外周から自動採色できないとき用のフォールバック）--
SIDE_FALLBACK = (58, 42, 30)       # 暗い木目茶（sRGB 0-255）
