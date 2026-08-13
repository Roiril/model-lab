# -*- coding: utf-8 -*-
"""「あと6画のくま」コンポーネント設定（Blender 内部単位: m）。

2人で共通のお題を表現する、完全協力型の制約付きお絵描きゲーム。
「まるを描く人」は、まんまるい〇を2つと自由なだ円を1つ描ける。
「線を描く人」は、直線を2本と1回だけ折れる折れ線を1本描ける。
"""

TITLE_JA = "あと6画のくま"
TITLE_EN = "Six Strokes, One Bear"
TAGLINE = "ふたりの線で、きもちを描く。"

TARGET_AGE = "8歳以上"
PLAYERS = 2
PLAY_MINUTES = 15
ROUND_SECONDS = 180
STROKES_PER_ROLE = 3

# --- 描画シート / パッド -------------------------------------------------
# A5からA4へ拡大。面積がちょうど約2倍になり、2人が同時に指差しやすい。
SHEET_W = 0.210       # 210mm（A4）
SHEET_H = 0.297       # 297mm（A4）
SHEET_T = 0.0006      # 0.6mm（GLB 表示用の単紙厚）
PAD_T = 0.0045        # 4.5mm（30枚パッドの表示厚）
SHEET_R = 0.006       # 6mm 角丸
PAD_SHEETS = 30
SHEET_VARIANTS = [
    {"id": "sheet_bear", "ja": "クマ輪郭シート", "count": 30},
]

# --- カード ---------------------------------------------------------------
PROMPT_W = 0.063      # 63mm
PROMPT_H = 0.088      # 88mm
PROMPT_T = 0.0012     # 1.2mm（GLB 表示用）
PROMPT_R = 0.004      # 4mm

ROLE_W = 0.070        # 70mm
ROLE_H = 0.120        # 120mm
ROLE_T = 0.0015       # 1.5mm
ROLE_R = 0.005        # 5mm

STAR_CARD_W = 0.088   # 88mm（横向き）
STAR_CARD_H = 0.063   # 63mm
STAR_CARD_T = 0.0012  # 1.2mm
STAR_CARD_R = 0.004   # 4mm

RULE_W = 0.105        # 105mm（A6）
RULE_H = 0.148        # 148mm（A6）
RULE_T = 0.0012       # 1.2mm
RULE_R = 0.005        # 5mm

# --- トークン / ペン / 砂時計 --------------------------------------------
# 3歳未満向けではないが、最小外形も約35mm以上にして扱いやすくする。
CIRCLE_TOKEN_D = 0.036    # 36mm 円（2個）
OVAL_TOKEN_W = 0.044      # 44mm
OVAL_TOKEN_H = 0.034      # 34mm
STRAIGHT_TOKEN_W = 0.044  # 44mm
STRAIGHT_TOKEN_H = 0.030  # 30mm
BEND_TOKEN_W = 0.040      # 40mm
BEND_TOKEN_H = 0.036      # 36mm
STROKE_TOKEN_T = 0.004    # 4mm
STAR_TOKEN_D = 0.036      # 36mm 外接円
STAR_TOKEN_T = 0.004      # 4mm

PEN_LENGTH = 0.142        # 142mm
PEN_DIAMETER = 0.0095     # 9.5mm

TIMER_W = 0.030           # 30mm
TIMER_D = 0.030           # 30mm
TIMER_H = 0.070           # 70mm

# --- sRGB 配色（0-255）---------------------------------------------------
COLORS = {
    "paper": (255, 248, 232),
    "paper_alt": (248, 239, 218),
    "ink": (37, 50, 56),
    "muted": (115, 112, 103),
    "bear_guide": (200, 189, 174),
    "circle": (217, 91, 82),
    "circle_dark": (158, 55, 51),
    "segment": (20, 118, 111),
    "segment_dark": (12, 76, 73),
    "honey": (226, 170, 53),
    "honey_dark": (151, 101, 22),
    "deep_teal": (39, 67, 74),
    "easy": (239, 186, 85),
    "medium": (102, 169, 151),
    "hard": (116, 102, 151),
    "white": (255, 255, 252),
    "glass": (188, 226, 224),
}


# お題面には解釈を固定する例示を印刷しない。
# circle_cues / segment_cues は役割バランス検証用の設計メモで、カード面には出さない。
PROMPTS = [
    {
        "id": "01_sleepy",
        "ja": "眠そうなクマ",
        "en": "A Sleepy Bear",
        "difficulty": 1,
        "practice": True,
        "circle_cues": ["丸い月", "丸いあくび口", "だ円のまくら"],
        "segment_cues": ["直線の閉じた目2本", "1回折れた毛布の角"],
    },
    {
        "id": "02_cold",
        "ja": "寒そうなクマ",
        "en": "A Freezing Bear",
        "difficulty": 1,
        "practice": False,
        "circle_cues": ["丸い雪玉", "丸いボタン", "だ円のマフラー"],
        "segment_cues": ["直線の震え線2本", "1回折れたマフラー端"],
    },
    {
        "id": "03_hungry",
        "ja": "お腹が空いたクマ",
        "en": "A Hungry Bear",
        "difficulty": 1,
        "practice": False,
        "circle_cues": ["丸い皿", "丸い食べ物", "だ円の口"],
        "segment_cues": ["直線の視線2本", "1回折れたお腹向きの矢印"],
    },
    {
        "id": "04_surprised",
        "ja": "びっくりしたクマ",
        "en": "A Surprised Bear",
        "difficulty": 1,
        "practice": False,
        "circle_cues": ["丸い目2つ", "だ円の開いた口"],
        "segment_cues": ["直線の驚き線2本", "1回折れた上がり眉"],
    },
    {
        "id": "05_waiting",
        "ja": "待ちくたびれたクマ",
        "en": "A Bear Tired of Waiting",
        "difficulty": 2,
        "practice": False,
        "circle_cues": ["丸い時計", "丸い目", "だ円のため息"],
        "segment_cues": ["直線の目2本", "1回折れた時計の針"],
    },
    {
        "id": "06_troubled",
        "ja": "困っているクマ",
        "en": "A Bear in a Bind",
        "difficulty": 2,
        "practice": False,
        "circle_cues": ["丸い汗2つ", "だ円の考えごと"],
        "segment_cues": ["直線の困り眉2本", "1回折れた口元"],
    },
    {
        "id": "07_attention",
        "ja": "かまってほしいクマ",
        "en": "A Bear Asking for Attention",
        "difficulty": 2,
        "practice": False,
        "circle_cues": ["丸い目", "丸いボール", "だ円の吹き出し"],
        "segment_cues": ["直線の呼びかけ線2本", "1回折れたひじ"],
    },
    {
        "id": "08_joy",
        "ja": "うれしくてたまらないクマ",
        "en": "A Bear Bursting with Joy",
        "difficulty": 2,
        "practice": False,
        "circle_cues": ["丸い風船2つ", "だ円の笑顔"],
        "segment_cues": ["直線の輝き2本", "1回折れた跳ねる腕"],
    },
    {
        "id": "09_hiding",
        "ja": "何かを隠しているクマ",
        "en": "A Bear Hiding Something",
        "difficulty": 3,
        "practice": False,
        "circle_cues": ["丸い横目2つ", "だ円のポケット"],
        "segment_cues": ["直線の視線2本", "1回折れた隠す腕"],
    },
    {
        "id": "10_brave",
        "ja": "こわいのに\n強がっているクマ",
        "en": "A Bear Pretending to Be Brave",
        "difficulty": 3,
        "practice": False,
        "circle_cues": ["丸い頬2つ", "だ円のメダル"],
        "segment_cues": ["直線の強い眉2本", "1回折れた固い口元"],
    },
    {
        "id": "11_awkward",
        "ja": "気まずそうなクマ",
        "en": "An Awkward Bear",
        "difficulty": 3,
        "practice": False,
        "circle_cues": ["丸い赤らみ2つ", "だ円の言いよどみ"],
        "segment_cues": ["直線のそらした目2本", "1回折れた固い口"],
    },
    {
        "id": "12_make_up",
        "ja": "仲直りしたいのに\n言い出せないクマ",
        "en": "A Bear Who Wants to Make Up",
        "difficulty": 3,
        "practice": False,
        "circle_cues": ["丸い目2つ", "だ円の仲直り印"],
        "segment_cues": ["直線の視線2本", "1回折れたためらう腕"],
    },
]


ROLE_CARDS = [
    {
        "id": "role_circle",
        "ja": "まるを描く人",
        "en": "まる",
        "color": "circle",
        "rule": "まんまるい〇を2つ、\n自由なだ円を1つ。",
        "examples": ["〇", "〇", "だ円"],
        "loadout": "〇×2 ＋ だ円×1",
    },
    {
        "id": "role_segment",
        "ja": "線を描く人",
        "en": "せん",
        "color": "segment",
        "rule": "直線を2本、\n1回だけ折れる折れ線を1本。",
        "examples": ["直線", "直線", "1折"],
        "loadout": "直線×2 ＋ 1折×1",
    },
]


# 1ゲームごとに確認する共有達成条件。個人得点・対立・秘密目標はない。
ACHIEVEMENTS = [
    {
        "id": "together",
        "title": "協力して完成できた",
        "body": "まる役と線役が、それぞれ1画以上描いて完成させた。",
    },
    {
        "id": "comfortable",
        "title": "余裕をもってクリアできた",
        "body": "能力を1つ以上残したまま、2人で完成を宣言できた。",
    },
    {
        "id": "guessed",
        "title": "お題を当ててもらえた",
        "body": "完成した絵を2人以外の人に見せ、お題を当ててもらえた。",
    },
]


SESSION_FLOW = [
    ("お題と役割を準備", "約30秒"),
    ("相談しながら描く", "3分"),
    ("達成条件を確認", "約30秒"),
    ("役割とペンを交換", "次のゲームへ"),
]
