# -*- coding: utf-8 -*-
"""「あと6画のくま」の印刷面テクスチャと GLB 用 manifest を生成する。

文字・カード・記号は Pillow で再現可能に描画する。クマの下絵だけは、
組み込み画像生成AIで作った「輪郭のみ」の原画を読み込んで配置する。
お題カードには解答例を載せず、2人の解釈と相談を固定しない。
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *  # noqa: F403


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "exports", "six-strokes-bear"))
TEX = os.path.join(OUT, "tex")
AI_BEAR_SOURCE = os.path.join(HERE, "assets", "bear_outline_ai_source.png")
os.makedirs(TEX, exist_ok=True)

# 約203dpi。2倍で描いて縮小し、細い日本語と曲線を滑らかにする。
PX_PER_MM = 8
SS = 2

JP_REGULAR_CANDIDATES = [
    r"C:/Windows/Fonts/YuGothM.ttc",
    r"C:/Windows/Fonts/meiryo.ttc",
]
JP_BOLD_CANDIDATES = [
    r"C:/Windows/Fonts/YuGothB.ttc",
    r"C:/Windows/Fonts/meiryob.ttc",
]


def _font_path(candidates: Iterable[str]) -> str:
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("日本語フォントが見つかりません: " + ", ".join(candidates))


FONT_REGULAR = _font_path(JP_REGULAR_CANDIDATES)
FONT_BOLD = _font_path(JP_BOLD_CANDIDATES)


def rgb(name: str) -> tuple[int, int, int]:
    return tuple(COLORS[name])  # noqa: F405


def px(mm: float) -> int:
    return max(1, round(mm * PX_PER_MM * SS))


def dimensions_px(w_m: float, h_m: float) -> tuple[int, int]:
    return px(w_m * 1000), px(h_m * 1000)


def font(size_px: float, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, max(8, int(size_px)))


def new_canvas(w_m: float, h_m: float, color: tuple[int, int, int]) -> Image.Image:
    w, h = dimensions_px(w_m, h_m)
    img = Image.new("RGB", (w, h), color)
    add_paper_fibres(img, seed=w * 31 + h)
    return img


def add_paper_fibres(img: Image.Image, seed: int) -> None:
    """低コントラストの短い紙繊維。文字より先に描く。"""
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    w, h = img.size
    base = rgb("paper_alt")
    count = max(180, int(w * h / 22000))
    for _ in range(count):
        x = rnd.randrange(0, w)
        y = rnd.randrange(0, h)
        length = rnd.randrange(max(2, w // 400), max(4, w // 120))
        shift = rnd.choice((-5, -3, 3, 5))
        col = tuple(max(0, min(255, c + shift)) for c in base)
        d.line((x, y, min(w, x + length), y + rnd.choice((-1, 0, 1))), fill=col, width=1)


def save(img: Image.Image, name: str) -> str:
    final = img.resize((img.width // SS, img.height // SS), Image.Resampling.LANCZOS)
    path = os.path.join(TEX, name + ".png")
    final.save(path, optimize=True)
    return os.path.basename(path)


def fit_font(
    d: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    start_size: int,
    min_size: int,
    bold: bool = False,
    spacing: int = 4,
) -> ImageFont.FreeTypeFont:
    size = start_size
    while size >= min_size:
        f = font(size, bold)
        box = d.multiline_textbbox((0, 0), text, font=f, spacing=spacing, align="center")
        if box[2] - box[0] <= max_width:
            return f
        size -= max(1, start_size // 30)
    return font(min_size, bold)


def wrap_text(d: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, max_width: int) -> str:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for char in paragraph:
            trial = current + char
            if current and d.textlength(trial, font=f) > max_width:
                lines.append(current)
                current = char
            else:
                current = trial
        if current:
            lines.append(current)
    return "\n".join(lines)


def cubic(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    steps: int = 48,
) -> list[tuple[float, float]]:
    out = []
    for i in range(steps + 1):
        t = i / steps
        q = 1.0 - t
        out.append((
            q**3 * p0[0] + 3 * q * q * t * p1[0] + 3 * q * t * t * p2[0] + t**3 * p3[0],
            q**3 * p0[1] + 3 * q * q * t * p1[1] + 3 * q * t * t * p2[1] + t**3 * p3[1],
        ))
    return out


def ellipse_points(box: tuple[float, float, float, float], steps: int = 120) -> list[tuple[float, float]]:
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    return [
        (cx + rx * math.cos(2 * math.pi * i / steps), cy + ry * math.sin(2 * math.pi * i / steps))
        for i in range(steps + 1)
    ]


def draw_dashed_path(
    d: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    fill: tuple[int, int, int],
    width: int,
    dash: float,
    gap: float,
) -> None:
    """任意の点列に距離基準の破線を描く。"""
    if len(points) < 2:
        return
    draw_on = True
    remaining = dash
    for a, b in zip(points, points[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        seg_len = math.hypot(dx, dy)
        if seg_len == 0:
            continue
        pos = 0.0
        while pos < seg_len:
            take = min(remaining, seg_len - pos)
            t0, t1 = pos / seg_len, (pos + take) / seg_len
            if draw_on:
                p0 = (a[0] + dx * t0, a[1] + dy * t0)
                p1 = (a[0] + dx * t1, a[1] + dy * t1)
                d.line((p0, p1), fill=fill, width=width)
            pos += take
            remaining -= take
            if remaining <= 1e-6:
                draw_on = not draw_on
                remaining = dash if draw_on else gap


def draw_circle_icon(
    d: ImageDraw.ImageDraw,
    center: tuple[float, float],
    radius: float,
    color: tuple[int, int, int],
    width: int,
) -> None:
    cx, cy = center
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=color, width=width)


def draw_oval_icon(
    d: ImageDraw.ImageDraw,
    center: tuple[float, float],
    width_px: float,
    height_px: float,
    color: tuple[int, int, int],
    stroke: int,
) -> None:
    cx, cy = center
    d.ellipse(
        (cx - width_px / 2, cy - height_px / 2, cx + width_px / 2, cy + height_px / 2),
        outline=color,
        width=stroke,
    )


def _draw_open_endpoints(
    d: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    color: tuple[int, int, int],
    stroke: int,
) -> None:
    d.line(points, fill=color, width=stroke, joint="curve")
    radius = max(2, round(stroke * 0.68))
    for x, y in (points[0], points[-1]):
        d.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def draw_straight_icon(
    d: ImageDraw.ImageDraw,
    center: tuple[float, float],
    width_px: float,
    color: tuple[int, int, int],
    stroke: int,
) -> None:
    cx, cy = center
    _draw_open_endpoints(
        d,
        [(cx - width_px / 2, cy), (cx + width_px / 2, cy)],
        color,
        stroke,
    )


def draw_bend_icon(
    d: ImageDraw.ImageDraw,
    center: tuple[float, float],
    width_px: float,
    height_px: float,
    color: tuple[int, int, int],
    stroke: int,
) -> None:
    cx, cy = center
    _draw_open_endpoints(
        d,
        [
            (cx - width_px / 2, cy + height_px / 2),
            (cx, cy - height_px / 2),
            (cx + width_px / 2, cy + height_px / 2),
        ],
        color,
        stroke,
    )


def star_points(cx: float, cy: float, outer: float, inner: float, points: int = 5) -> list[tuple[float, float]]:
    result = []
    for i in range(points * 2):
        radius = outer if i % 2 == 0 else inner
        a = -math.pi / 2 + math.pi * i / points
        result.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return result


def draw_paw(
    d: ImageDraw.ImageDraw,
    center: tuple[float, float],
    radius: float,
    color: tuple[int, int, int],
) -> None:
    cx, cy = center
    d.ellipse((cx - radius * 0.52, cy - radius * 0.1, cx + radius * 0.52, cy + radius * 0.62), fill=color)
    for ox, oy in [(-0.48, -0.40), (-0.16, -0.58), (0.16, -0.58), (0.48, -0.40)]:
        rr = radius * 0.22
        x, y = cx + ox * radius, cy + oy * radius
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=color)


def draw_honey_drops(
    d: ImageDraw.ImageDraw,
    difficulty: int,
    start: tuple[float, float],
    radius: float,
) -> None:
    x0, y0 = start
    for i in range(3):
        x = x0 + i * radius * 2.2
        fill = rgb("honey") if i < difficulty else rgb("bear_guide")
        pts = [
            (x, y0 - radius * 1.15),
            (x - radius * 0.78, y0),
            (x - radius * 0.55, y0 + radius * 0.70),
            (x, y0 + radius),
            (x + radius * 0.55, y0 + radius * 0.70),
            (x + radius * 0.78, y0),
        ]
        d.polygon(pts, fill=fill)


def draw_brand(d: ImageDraw.ImageDraw, w: int, y: int, dark: bool = True, compact: bool = False) -> None:
    ink = rgb("ink") if dark else rgb("white")
    icon_r = w * (0.022 if compact else 0.027)
    cx = w * 0.11
    stroke = max(2, round(w * 0.006))
    draw_circle_icon(d, (cx, y), icon_r, rgb("circle"), stroke)
    draw_bend_icon(
        d,
        (cx + icon_r * 3.1, y),
        icon_r * 2.2,
        icon_r * 1.35,
        rgb("segment"),
        stroke,
    )
    f = font(w * (0.032 if compact else 0.038), bold=True)
    d.text((cx + icon_r * 4.8, y), TITLE_JA, fill=ink, font=f, anchor="lm")  # noqa: F405


def draw_ai_bear_outline(img: Image.Image) -> None:
    """画像生成AIの原画から白地を落とし、輪郭線だけを薄く合成する。"""
    if not os.path.exists(AI_BEAR_SOURCE):
        raise FileNotFoundError("AI生成クマ輪郭が見つかりません: " + AI_BEAR_SOURCE)

    w, h = img.size
    source = Image.open(AI_BEAR_SOURCE).convert("L")
    alpha = source.point(lambda value: 0 if value >= 245 else min(255, (245 - value) * 7))
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError("AI生成クマ輪郭に描画線がありません")
    alpha = alpha.crop(bbox)

    drawing_top = int(h * 0.16)
    drawing_bottom = int(h * 0.84)
    max_w = int(w * 0.68)
    max_h = drawing_bottom - drawing_top
    scale = min(max_w / alpha.width, max_h / alpha.height)
    target = (
        max(1, round(alpha.width * scale)),
        max(1, round(alpha.height * scale)),
    )
    alpha = alpha.resize(target, Image.Resampling.LANCZOS)
    line_layer = Image.new("RGB", target, rgb("bear_guide"))
    x = (w - target[0]) // 2
    y = drawing_top + (max_h - target[1]) // 2
    img.paste(line_layer, (x, y), alpha)


def draw_sheet_base(demo: bool = False) -> Image.Image:
    img = new_canvas(SHEET_W, SHEET_H, rgb("paper"))  # noqa: F405
    d = ImageDraw.Draw(img)
    w, h = img.size

    border = max(3, round(w * 0.004))
    inset = round(w * 0.025)
    d.rounded_rectangle(
        (inset, inset, w - inset, h - inset),
        radius=round(w * 0.035),
        outline=rgb("paper_alt"),
        width=border,
    )
    draw_brand(d, w, round(h * 0.075), compact=True)

    draw_ai_bear_outline(img)
    hintf = font(w * 0.022)
    d.text(
        (w * 0.5, h * 0.885),
        "薄い下絵は画数に数えません",
        fill=rgb("muted"),
        font=hintf,
        anchor="mm",
    )

    # 各役割の能力内訳を示す凡例。実物トークンも同じ形にする。
    dock_y = h * 0.942
    label_f = font(w * 0.019, bold=True)
    icon_stroke = max(2, round(w * 0.003))
    d.text((w * 0.08, dock_y), "まる", fill=rgb("circle_dark"), font=label_f, anchor="lm")
    draw_circle_icon(d, (w * 0.23, dock_y), w * 0.019, rgb("circle"), icon_stroke)
    draw_circle_icon(d, (w * 0.30, dock_y), w * 0.019, rgb("circle"), icon_stroke)
    draw_oval_icon(d, (w * 0.40, dock_y), w * 0.058, w * 0.035, rgb("circle"), icon_stroke)
    d.text((w * 0.52, dock_y), "せん", fill=rgb("segment_dark"), font=label_f, anchor="lm")
    draw_straight_icon(d, (w * 0.67, dock_y), w * 0.052, rgb("segment"), icon_stroke)
    draw_straight_icon(d, (w * 0.75, dock_y), w * 0.052, rgb("segment"), icon_stroke)
    draw_bend_icon(d, (w * 0.87, dock_y), w * 0.070, w * 0.035, rgb("segment"), icon_stroke)

    if demo:
        # 〇2・だ円1・直線2・1折れ線1だけで「眠そう」を描いた表示用例。
        circle_col = rgb("circle")
        segment_col = rgb("segment")
        lw = max(5, round(w * 0.008))
        # まる役: 鼻の〇、月の〇、あくび口のだ円。
        draw_circle_icon(d, (w * 0.50, h * 0.365), w * 0.019, circle_col, lw)
        draw_circle_icon(d, (w * 0.78, h * 0.205), w * 0.038, circle_col, lw)
        draw_oval_icon(d, (w * 0.50, h * 0.435), w * 0.065, w * 0.040, circle_col, lw)
        # 線役: 左右の閉じた目を直線1本ずつ、毛布上辺を角1つの折れ線で描く。
        draw_straight_icon(d, (w * 0.425, h * 0.325), w * 0.060, segment_col, lw)
        draw_straight_icon(d, (w * 0.575, h * 0.325), w * 0.060, segment_col, lw)
        _draw_open_endpoints(
            d,
            [
                (w * 0.30, h * 0.655),
                (w * 0.50, h * 0.625),
                (w * 0.70, h * 0.655),
            ],
            segment_col,
            lw,
        )

        badge_f = font(w * 0.024, bold=True)
        d.rounded_rectangle((w * 0.06, h * 0.11, w * 0.28, h * 0.155), radius=round(w * 0.015), fill=rgb("honey"))
        d.text((w * 0.17, h * 0.1325), "プレイ例", fill=rgb("ink"), font=badge_f, anchor="mm")
    return img


def draw_common_back(w_m: float, h_m: float, name: str, subtitle: str) -> str:
    img = new_canvas(w_m, h_m, rgb("deep_teal"))
    d = ImageDraw.Draw(img)
    w, h = img.size
    # 〇 / 1折れ線の反復模様。
    for row in range(6):
        for col in range(4):
            cx = w * (0.14 + col * 0.24)
            cy = h * (0.12 + row * 0.16)
            if (row + col) % 2 == 0:
                draw_circle_icon(d, (cx, cy), w * 0.045, (82, 112, 116), max(2, round(w * 0.008)))
            else:
                draw_bend_icon(
                    d,
                    (cx, cy),
                    w * 0.10,
                    w * 0.07,
                    (82, 112, 116),
                    max(2, round(w * 0.008)),
                )
    plate = (w * 0.10, h * 0.37, w * 0.90, h * 0.63)
    d.rounded_rectangle(plate, radius=round(w * 0.05), fill=rgb("paper"))
    f1 = fit_font(d, TITLE_JA, int(w * 0.70), int(w * 0.10), int(w * 0.06), bold=True)  # noqa: F405
    d.text((w * 0.5, h * 0.465), TITLE_JA, fill=rgb("ink"), font=f1, anchor="mm")  # noqa: F405
    f2 = font(w * 0.042, bold=True)
    d.text((w * 0.5, h * 0.56), subtitle, fill=rgb("muted"), font=f2, anchor="mm")
    return save(img, name)


def draw_prompt(prompt: dict) -> str:
    difficulty = prompt["difficulty"]
    tier_name = {1: "easy", 2: "medium", 3: "hard"}[difficulty]
    img = new_canvas(PROMPT_W, PROMPT_H, rgb("paper"))  # noqa: F405
    d = ImageDraw.Draw(img)
    w, h = img.size
    tier = rgb(tier_name)
    d.rounded_rectangle((0, 0, w, h), radius=round(w * 0.065), fill=rgb("paper"))
    d.rounded_rectangle((w * 0.035, h * 0.025, w * 0.965, h * 0.22), radius=round(w * 0.045), fill=tier)
    draw_honey_drops(d, difficulty, (w * 0.12, h * 0.12), w * 0.025)
    num_f = font(w * 0.042, bold=True)
    d.text((w * 0.88, h * 0.12), prompt["id"][:2], fill=rgb("ink"), font=num_f, anchor="mm")

    text = prompt["ja"]
    title_f = fit_font(d, text, int(w * 0.78), int(w * 0.095), int(w * 0.060), bold=True, spacing=int(w * 0.015))
    d.multiline_text(
        (w * 0.5, h * 0.46),
        text,
        fill=rgb("ink"),
        font=title_f,
        anchor="mm",
        align="center",
        spacing=int(w * 0.016),
    )
    en_f = font(w * 0.034, bold=False)
    en = wrap_text(d, prompt["en"], en_f, int(w * 0.72))
    d.multiline_text(
        (w * 0.5, h * 0.68),
        en,
        fill=rgb("muted"),
        font=en_f,
        anchor="mm",
        align="center",
        spacing=int(w * 0.012),
    )
    d.line((w * 0.16, h * 0.78, w * 0.84, h * 0.78), fill=rgb("bear_guide"), width=max(2, round(w * 0.004)))
    instruction_f = font(w * 0.030)
    d.text((w * 0.5, h * 0.855), "2人とも同じお題を見ます", fill=rgb("muted"), font=instruction_f, anchor="mm")
    if prompt.get("practice"):
        d.rounded_rectangle((w * 0.23, h * 0.90, w * 0.77, h * 0.96), radius=round(w * 0.025), fill=rgb("honey"))
        practice_f = font(w * 0.031, bold=True)
        d.text((w * 0.5, h * 0.93), "練習におすすめ", fill=rgb("ink"), font=practice_f, anchor="mm")
    else:
        draw_brand(d, w, round(h * 0.935), compact=True)
    return save(img, "prompt_" + prompt["id"])


def draw_role(role: dict) -> str:
    role_color = rgb(role["color"])
    dark = rgb(role["color"] + "_dark")
    img = new_canvas(ROLE_W, ROLE_H, role_color)
    d = ImageDraw.Draw(img)
    w, h = img.size
    d.rounded_rectangle((w * 0.035, h * 0.025, w * 0.965, h * 0.975), radius=round(w * 0.06), outline=rgb("white"), width=max(3, round(w * 0.012)))

    icon_y = h * 0.19
    icon_stroke = max(4, round(w * 0.017))
    if role["id"] == "role_circle":
        draw_circle_icon(d, (w * 0.31, icon_y), w * 0.080, rgb("white"), icon_stroke)
        draw_circle_icon(d, (w * 0.50, icon_y), w * 0.080, rgb("white"), icon_stroke)
        draw_oval_icon(d, (w * 0.74, icon_y), w * 0.19, w * 0.115, rgb("white"), icon_stroke)
    else:
        draw_straight_icon(d, (w * 0.27, icon_y), w * 0.18, rgb("white"), icon_stroke)
        draw_straight_icon(d, (w * 0.50, icon_y), w * 0.18, rgb("white"), icon_stroke)
        draw_bend_icon(d, (w * 0.76, icon_y), w * 0.19, w * 0.12, rgb("white"), icon_stroke)

    en_f = font(w * 0.095, bold=True)
    d.text((w * 0.5, h * 0.34), role["en"], fill=rgb("white"), font=en_f, anchor="mm")
    ja_f = font(w * 0.068, bold=True)
    d.text((w * 0.5, h * 0.43), role["ja"], fill=rgb("white"), font=ja_f, anchor="mm")

    d.rounded_rectangle((w * 0.10, h * 0.51, w * 0.90, h * 0.74), radius=round(w * 0.045), fill=rgb("paper"))
    rule_f = font(w * 0.044, bold=True)
    wrapped = wrap_text(d, role["rule"], rule_f, int(w * 0.68))
    d.multiline_text((w * 0.5, h * 0.625), wrapped, fill=dark, font=rule_f, anchor="mm", align="center", spacing=int(w * 0.012))

    ex_f = font(w * 0.035)
    d.text((w * 0.5, h * 0.81), "例：" + "・".join(role["examples"]), fill=rgb("white"), font=ex_f, anchor="mm")
    count_f = fit_font(d, role["loadout"], int(w * 0.80), int(w * 0.052), int(w * 0.038), bold=True)
    d.text((w * 0.5, h * 0.90), role["loadout"], fill=rgb("white"), font=count_f, anchor="mm")
    return save(img, role["id"])


def draw_stroke_token(kind: str) -> str:
    dimensions = {
        "circle": (CIRCLE_TOKEN_D, CIRCLE_TOKEN_D),  # noqa: F405
        "oval": (OVAL_TOKEN_W, OVAL_TOKEN_H),  # noqa: F405
        "straight": (STRAIGHT_TOKEN_W, STRAIGHT_TOKEN_H),  # noqa: F405
        "bend": (BEND_TOKEN_W, BEND_TOKEN_H),  # noqa: F405
    }
    if kind not in dimensions:
        raise ValueError("未対応の能力トークン: " + kind)
    w_m, h_m = dimensions[kind]
    body = rgb("circle" if kind in {"circle", "oval"} else "segment")
    img = new_canvas(w_m, h_m, body)
    d = ImageDraw.Draw(img)
    w, h = img.size
    d.rounded_rectangle((0, 0, w, h), radius=min(w, h) // 2, fill=body)
    stroke = max(3, round(min(w, h) * 0.075))
    if kind == "circle":
        draw_circle_icon(d, (w / 2, h / 2), min(w, h) * 0.25, rgb("white"), stroke)
    elif kind == "oval":
        draw_oval_icon(d, (w / 2, h / 2), w * 0.52, h * 0.40, rgb("white"), stroke)
    elif kind == "straight":
        draw_straight_icon(d, (w / 2, h / 2), w * 0.54, rgb("white"), stroke)
    else:
        draw_bend_icon(d, (w / 2, h / 2), w * 0.52, h * 0.38, rgb("white"), stroke)
    return save(img, "stroke_" + kind)


def draw_achievement_card() -> tuple[str, str]:
    img = new_canvas(STAR_CARD_W, STAR_CARD_H, rgb("paper"))  # noqa: F405
    d = ImageDraw.Draw(img)
    w, h = img.size
    d.rounded_rectangle(
        (w * 0.025, h * 0.035, w * 0.975, h * 0.965),
        radius=round(h * 0.07),
        outline=rgb("honey"),
        width=max(3, round(h * 0.013)),
    )
    title_f = font(h * 0.078, bold=True)
    d.text((w * 0.5, h * 0.105), "3つの達成条件", fill=rgb("ink"), font=title_f, anchor="mm")
    sub_f = font(h * 0.030, bold=True)
    d.text((w * 0.5, h * 0.165), "1ゲームごとに確認", fill=rgb("muted"), font=sub_f, anchor="mm")
    d.line((w * 0.08, h * 0.205, w * 0.92, h * 0.205), fill=rgb("paper_alt"), width=max(2, round(h * 0.007)))

    body_f = font(h * 0.027)
    for i, item in enumerate(ACHIEVEMENTS):  # noqa: F405
        cy = h * (0.315 + i * 0.225)
        if i:
            divider_y = h * (0.425 + (i - 1) * 0.225)
            d.line((w * 0.18, divider_y, w * 0.91, divider_y), fill=rgb("paper_alt"), width=max(1, round(h * 0.004)))
        pts = star_points(w * 0.10, cy, h * 0.068, h * 0.031)
        d.polygon(pts, fill=rgb("honey"))
        draw_paw(d, (w * 0.10, cy), h * 0.025, rgb("paper"))
        title_f = fit_font(
            d,
            item["title"],
            int(w * 0.70),
            int(h * 0.047),
            int(h * 0.035),
            bold=True,
        )
        d.text((w * 0.19, cy - h * 0.036), item["title"], fill=rgb("ink"), font=title_f, anchor="lm")
        body = wrap_text(d, item["body"], body_f, int(w * 0.69))
        d.multiline_text(
            (w * 0.19, cy + h * 0.030),
            body,
            fill=rgb("muted"),
            font=body_f,
            anchor="lm",
            spacing=int(h * 0.007),
        )
    front = save(img, "achievement_card")

    back_img = new_canvas(STAR_CARD_W, STAR_CARD_H, rgb("deep_teal"))
    bd = ImageDraw.Draw(back_img)
    bw, bh = back_img.size
    for i in range(3):
        cx = bw * (0.23 + i * 0.27)
        pts = star_points(cx, bh * 0.42, bh * 0.18, bh * 0.08)
        bd.polygon(pts, fill=rgb("honey"))
        draw_paw(bd, (cx, bh * 0.42), bh * 0.065, rgb("deep_teal"))
    f = fit_font(bd, "達成できたらトークンを置く", int(bw * 0.78), int(bh * 0.063), int(bh * 0.045), bold=True)
    bd.text((bw * 0.5, bh * 0.74), "達成できたらトークンを置く", fill=rgb("white"), font=f, anchor="mm")
    back = save(back_img, "achievement_card_back")
    return front, back


def draw_achievement_token() -> str:
    size_m = STAR_TOKEN_D  # noqa: F405
    img = new_canvas(size_m, size_m, rgb("deep_teal"))
    d = ImageDraw.Draw(img)
    w, h = img.size
    pts = star_points(w / 2, h / 2, w * 0.48, w * 0.22)
    d.polygon(pts, fill=rgb("honey"))
    draw_paw(d, (w / 2, h / 2), w * 0.14, rgb("deep_teal"))
    return save(img, "achievement_token")


def draw_rule_card() -> tuple[str, str]:
    front_img = new_canvas(RULE_W, RULE_H, rgb("paper"))  # noqa: F405
    d = ImageDraw.Draw(front_img)
    w, h = front_img.size
    draw_brand(d, w, round(h * 0.065))
    title_f = font(w * 0.060, bold=True)
    d.text((w * 0.08, h * 0.145), "1ゲームの遊び方", fill=rgb("ink"), font=title_f, anchor="lm")
    steps = [
        ("1", "お題を1枚めくり、2人で確認"),
        ("2", "役割を決め、能力トークンを準備する"),
        ("3", "3分間、相談しながら順番自由で描く"),
        ("4", "完成後、達成条件を確認する"),
        ("5", "役割とペンを交換し、次のゲームへ"),
    ]
    step_f = font(w * 0.036, bold=True)
    num_f = font(w * 0.043, bold=True)
    for i, (number, label) in enumerate(steps):
        cy = h * (0.25 + i * 0.125)
        col = rgb("circle") if i % 2 == 0 else rgb("segment")
        r = w * 0.036
        d.ellipse((w * 0.10 - r, cy - r, w * 0.10 + r, cy + r), fill=col)
        d.text((w * 0.10, cy), number, fill=rgb("white"), font=num_f, anchor="mm")
        wrapped = wrap_text(d, label, step_f, int(w * 0.72))
        d.multiline_text((w * 0.17, cy), wrapped, fill=rgb("ink"), font=step_f, anchor="lm", spacing=int(w * 0.012))
    footer_f = font(w * 0.032, bold=True)
    d.rounded_rectangle((w * 0.08, h * 0.885, w * 0.92, h * 0.95), radius=round(w * 0.02), fill=rgb("honey"))
    d.text((w * 0.5, h * 0.917), "2人とも同じチーム。勝敗・個人得点はありません。", fill=rgb("ink"), font=footer_f, anchor="mm")
    front = save(front_img, "rule_front")

    back_img = new_canvas(RULE_W, RULE_H, rgb("paper"))
    bd = ImageDraw.Draw(back_img)
    bw, bh = back_img.size
    title = font(bw * 0.060, bold=True)
    bd.text((bw * 0.08, bh * 0.09), "能力のルール", fill=rgb("ink"), font=title, anchor="lm")
    rules = [
        ("〇×2", "縦横がほぼ同じ、角・交差・塗りなしの閉じた1本線。手描きのゆれは可。", "circle"),
        ("だ円×1", "長い軸と短い軸が分かる滑らかな閉じた1本線。向きと比率は自由。", "circle"),
        ("直線×2", "ペンを離すまで方向が変わらない1本線。", "segment"),
        ("1折×1", "直線2辺を角1つでつなぐ。曲線・2回以上の折れ・なぞり直しは不可。", "segment"),
        ("共通", "新しい線だけを判定。下絵や既存線への接触・交差は可。使い切らなくてもよい。", "honey"),
    ]
    head_f = font(bw * 0.043, bold=True)
    body_f = font(bw * 0.032)
    for i, (head, body, color) in enumerate(rules):
        cy = bh * (0.19 + i * 0.15)
        col = rgb(color)
        bd.rounded_rectangle((bw * 0.08, cy - bh * 0.035, bw * 0.25, cy + bh * 0.035), radius=round(bh * 0.018), fill=col)
        bd.text((bw * 0.165, cy), head, fill=rgb("white") if color != "honey" else rgb("ink"), font=head_f, anchor="mm")
        wrapped = wrap_text(bd, body, body_f, int(bw * 0.62))
        bd.multiline_text((bw * 0.29, cy), wrapped, fill=rgb("ink"), font=body_f, anchor="lm", spacing=int(bw * 0.008))
    note_f = font(bw * 0.030)
    bd.text((bw * 0.5, bh * 0.94), "1画＝ペンを紙につけてから離すまで。相談や指差しは自由。", fill=rgb("muted"), font=note_f, anchor="mm")
    back = save(back_img, "rule_back")
    return front, back


def component_panel(
    component_id: str,
    label: str,
    group: str,
    w_m: float,
    h_m: float,
    t_m: float,
    r_m: float,
    face_tex: str,
    back_tex: str,
    side_color: tuple[int, int, int],
    description: str,
    included_count: int = 1,
    display_only: bool = False,
) -> dict:
    return {
        "id": component_id,
        "label": label,
        "group": group,
        "kind": "panel",
        "width_mm": round(w_m * 1000, 2),
        "height_mm": round(h_m * 1000, 2),
        "thick_mm": round(t_m * 1000, 2),
        "corner_r_mm": round(r_m * 1000, 2),
        "face_tex": face_tex,
        "back_tex": back_tex,
        "side_color": list(side_color),
        "description": description,
        "included_count": included_count,
        "display_only": display_only,
        "glb": "glb/" + component_id + ".glb",
    }


# ---------------------------------------------------------------- textures
sheet_back = draw_common_back(SHEET_W, SHEET_H, "sheet_back", "DRAWING PAD")  # noqa: F405
sheet_textures: dict[str, str] = {}
for variant in SHEET_VARIANTS:  # noqa: F405
    sheet_textures[variant["id"]] = save(draw_sheet_base(), variant["id"])
demo_tex = save(draw_sheet_base(demo=True), "sheet_sleepy_demo")

prompt_back = draw_common_back(PROMPT_W, PROMPT_H, "prompt_back", "PROMPT")  # noqa: F405
prompt_textures = {p["id"]: draw_prompt(p) for p in PROMPTS}  # noqa: F405

role_back = draw_common_back(ROLE_W, ROLE_H, "role_back", "PUBLIC ROLE")  # noqa: F405
role_textures = {role["id"]: draw_role(role) for role in ROLE_CARDS}  # noqa: F405

stroke_textures = {
    kind: draw_stroke_token(kind)
    for kind in ("circle", "oval", "straight", "bend")
}
achievement_card_front, achievement_card_back = draw_achievement_card()
achievement_token_tex = draw_achievement_token()
rule_front, rule_back = draw_rule_card()


# ---------------------------------------------------------------- manifest
components: dict[str, dict] = {}

components["drawing_pad"] = component_panel(
    "drawing_pad",
    "クマ描画パッド（30枚）",
    "描画シート",
    SHEET_W, SHEET_H, PAD_T, SHEET_R,  # noqa: F405
    sheet_textures["sheet_bear"],
    sheet_back,
    rgb("paper_alt"),
    "画像生成AIで作ったクマ輪郭だけを薄く印刷したA4パッド30枚。A5版の約2倍の描画面積。",
)

for variant in SHEET_VARIANTS:  # noqa: F405
    components[variant["id"]] = component_panel(
        variant["id"],
        variant["ja"],
        "描画シート",
        SHEET_W, SHEET_H, SHEET_T, SHEET_R,  # noqa: F405
        sheet_textures[variant["id"]],
        sheet_back,
        rgb("paper_alt"),
        "顔・表情・持ち物・文字・背景を含まない、AI生成クマ輪郭だけのA4用紙。",
        included_count=variant["count"],
    )
    components[variant["id"]]["contained_in"] = "drawing_pad"

components["sheet_sleepy_demo"] = component_panel(
    "sheet_sleepy_demo",
    "プレイ例：眠そうなクマ",
    "プレイ例",
    SHEET_W, SHEET_H, SHEET_T, SHEET_R,  # noqa: F405
    demo_tex,
    sheet_back,
    rgb("paper_alt"),
    "〇2つ・だ円1つ・直線2本・1回折れる折れ線1本だけで描いた表示用例。製品枚数には含まれない。",
    included_count=0,
    display_only=True,
)

for prompt in PROMPTS:  # noqa: F405
    cid = "prompt_" + prompt["id"]
    components[cid] = component_panel(
        cid,
        prompt["ja"].replace("\n", ""),
        "お題・ハチミツ" + str(prompt["difficulty"]),
        PROMPT_W, PROMPT_H, PROMPT_T, PROMPT_R,  # noqa: F405
        prompt_textures[prompt["id"]],
        prompt_back,
        rgb("paper_alt"),
        f"難度{prompt['difficulty']}。2人とも同じお題を見る共有カード。",
    )

for role in ROLE_CARDS:  # noqa: F405
    components[role["id"]] = component_panel(
        role["id"],
        role["ja"] + " / " + role["en"],
        "公開役割",
        ROLE_W, ROLE_H, ROLE_T, ROLE_R,  # noqa: F405
        role_textures[role["id"]],
        role_back,
        rgb(role["color"] + "_dark"),
        role["rule"] + " 役割は1ゲームごとに交換する。",
    )

components["stroke_circle"] = {
    "id": "stroke_circle",
    "label": "まんまるい〇トークン",
    "group": "描画道具",
    "kind": "token_round",
    "diameter_mm": CIRCLE_TOKEN_D * 1000,  # noqa: F405
    "thick_mm": STROKE_TOKEN_T * 1000,  # noqa: F405
    "face_tex": stroke_textures["circle"],
    "side_color": list(rgb("circle_dark")),
    "description": "まる役が使える、縦横がほぼ同じ閉じた〇。1個につき1画。",
    "included_count": 2,
    "display_only": False,
    "glb": "glb/stroke_circle.glb",
}
components["stroke_oval"] = {
    "id": "stroke_oval",
    "label": "自由なだ円トークン",
    "group": "描画道具",
    "kind": "token_oval",
    "width_mm": OVAL_TOKEN_W * 1000,  # noqa: F405
    "height_mm": OVAL_TOKEN_H * 1000,  # noqa: F405
    "thick_mm": STROKE_TOKEN_T * 1000,  # noqa: F405
    "face_tex": stroke_textures["oval"],
    "side_color": list(rgb("circle_dark")),
    "description": "まる役が使える、長軸と短軸のある自由なだ円。1個につき1画。",
    "included_count": 1,
    "display_only": False,
    "glb": "glb/stroke_oval.glb",
}
components["stroke_straight"] = {
    "id": "stroke_straight",
    "label": "直線トークン",
    "group": "描画道具",
    "kind": "token_rect",
    "width_mm": STRAIGHT_TOKEN_W * 1000,  # noqa: F405
    "height_mm": STRAIGHT_TOKEN_H * 1000,  # noqa: F405
    "thick_mm": STROKE_TOKEN_T * 1000,  # noqa: F405
    "corner_r_mm": STRAIGHT_TOKEN_H * 500,  # noqa: F405
    "face_tex": stroke_textures["straight"],
    "side_color": list(rgb("segment_dark")),
    "description": "線役が使える、方向を変えない直線。1個につき1画。",
    "included_count": 2,
    "display_only": False,
    "glb": "glb/stroke_straight.glb",
}
components["stroke_bend"] = {
    "id": "stroke_bend",
    "label": "1回折れる折れ線トークン",
    "group": "描画道具",
    "kind": "token_rect",
    "width_mm": BEND_TOKEN_W * 1000,  # noqa: F405
    "height_mm": BEND_TOKEN_H * 1000,  # noqa: F405
    "thick_mm": STROKE_TOKEN_T * 1000,  # noqa: F405
    "corner_r_mm": 0.006 * 1000,
    "face_tex": stroke_textures["bend"],
    "side_color": list(rgb("segment_dark")),
    "description": "線役が使える、直線2辺を角1つでつないだ折れ線。1個につき1画。",
    "included_count": 1,
    "display_only": False,
    "glb": "glb/stroke_bend.glb",
}

for kind, color, label in [
    ("circle", "circle", "まる役ペン"),
    ("segment", "segment", "線役ペン"),
]:
    cid = "marker_" + kind
    components[cid] = {
        "id": cid,
        "label": label,
        "group": "描画道具",
        "kind": "marker",
        "length_mm": PEN_LENGTH * 1000,  # noqa: F405
        "diameter_mm": PEN_DIAMETER * 1000,  # noqa: F405
        "color": list(rgb(color)),
        "description": "役割色の細字ペン。非毒性・低臭の水性ペンを別途調達するための外形参照モデル。",
        "off_the_shelf_reference": True,
        "included_count": 1,
        "display_only": False,
        "glb": "glb/" + cid + ".glb",
    }

components["timer_3min"] = {
    "id": "timer_3min",
    "label": "3分砂時計",
    "group": "描画道具",
    "kind": "timer",
    "width_mm": TIMER_W * 1000,  # noqa: F405
    "depth_mm": TIMER_D * 1000,  # noqa: F405
    "height_mm": TIMER_H * 1000,  # noqa: F405
    "description": "1問3分を測る、市販3分砂時計の外形参照モデル。",
    "off_the_shelf_reference": True,
    "included_count": 1,
    "display_only": False,
    "glb": "glb/timer_3min.glb",
}

components["achievement_card"] = component_panel(
    "achievement_card",
    "3つの達成条件",
    "達成条件",
    STAR_CARD_W, STAR_CARD_H, STAR_CARD_T, STAR_CARD_R,  # noqa: F405
    achievement_card_front,
    achievement_card_back,
    rgb("honey_dark"),
    "1ゲームごとに2人で確認する共有達成条件カード。勝敗や個人得点には使わない。",
)
components["achievement_token"] = {
    "id": "achievement_token",
    "label": "達成トークン",
    "group": "達成条件",
    "kind": "token_star",
    "diameter_mm": STAR_TOKEN_D * 1000,  # noqa: F405
    "thick_mm": STAR_TOKEN_T * 1000,  # noqa: F405
    "face_tex": achievement_token_tex,
    "side_color": list(rgb("honey_dark")),
    "description": "満たした条件1つにつき1個、条件文を隠さないようカードの下へ置く。",
    "included_count": 3,
    "display_only": False,
    "glb": "glb/achievement_token.glb",
}
components["rule_card"] = component_panel(
    "rule_card",
    "両面ルールカード",
    "ルール",
    RULE_W, RULE_H, RULE_T, RULE_R,  # noqa: F405
    rule_front,
    rule_back,
    rgb("paper_alt"),
    "表に1ゲームの流れ、裏に〇・だ円・直線・1折れ線の判定をまとめたA6カード。",
)


set_counts = {
    "drawing_pad": 1,
    **{"prompt_" + p["id"]: 1 for p in PROMPTS},  # noqa: F405
    "role_circle": 1,
    "role_segment": 1,
    "stroke_circle": 2,
    "stroke_oval": 1,
    "stroke_straight": 2,
    "stroke_bend": 1,
    "marker_circle": 1,
    "marker_segment": 1,
    "timer_3min": 1,
    "achievement_card": 1,
    "achievement_token": 3,
    "rule_card": 1,
}

manifest = {
    "title_ja": TITLE_JA,  # noqa: F405
    "title_en": TITLE_EN,  # noqa: F405
    "tagline": TAGLINE,  # noqa: F405
    "players": PLAYERS,  # noqa: F405
    "minutes": PLAY_MINUTES,  # noqa: F405
    "fully_cooperative": True,
    "bear_outline": {
        "origin": "OpenAI built-in image generation",
        "source": "models/six-strokes-bear/assets/bear_outline_ai_source.png",
        "content": "bear outline only",
    },
    "overview_glb": "six-strokes-bear.glb",
    "groups": [
        "俯瞰",
        "プレイ例",
        "描画シート",
        "お題・ハチミツ1",
        "お題・ハチミツ2",
        "お題・ハチミツ3",
        "公開役割",
        "描画道具",
        "達成条件",
        "ルール",
    ],
    "components": components,
    "set_counts": set_counts,
    "achievements": ACHIEVEMENTS,  # noqa: F405
}

with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("DONE textures:", len([n for n in os.listdir(TEX) if n.endswith(".png")]))
print("components:", len(components))
print("OUT:", OUT)
