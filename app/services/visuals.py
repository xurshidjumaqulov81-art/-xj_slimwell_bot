from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Final

from PIL import Image, ImageDraw, ImageFont

from app.config import ASSETS_DIR


OUTPUT_DIR: Final[Path] = ASSETS_DIR / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH: Final[int] = 1600
HEIGHT: Final[int] = 1000

WHITE = (255, 255, 255)
BLACK = (24, 24, 24)
GREEN = (18, 127, 33)
DARK_GREEN = (10, 98, 24)
LIGHT_GREEN = (236, 247, 235)
BORDER_GREEN = (31, 137, 55)


def _find_font(bold: bool) -> Path | None:
    names = (
        ("DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf")
        if bold
        else ("DejaVuSans.ttf", "LiberationSans-Regular.ttf")
    )

    roots = (
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path("/usr/local/lib/python3.12/site-packages/PIL"),
        Path("/usr/local/lib/python3.11/site-packages/PIL"),
    )

    for root in roots:
        if not root.exists():
            continue

        for name in names:
            try:
                matches = list(root.rglob(name))
            except OSError:
                matches = []

            if matches:
                return matches[0]

    return None


_FONT_REGULAR = _find_font(False)
_FONT_BOLD = _find_font(True)


def _font(
    size: int,
    bold: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    selected = _FONT_BOLD if bold else _FONT_REGULAR

    if selected is not None:
        return ImageFont.truetype(
            str(selected),
            size=size,
        )

    for fallback in (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "Arial.ttf",
    ):
        try:
            return ImageFont.truetype(
                fallback,
                size=size,
            )
        except OSError:
            continue

    return ImageFont.load_default()


def _text_box(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    spacing: int = 4,
) -> tuple[int, int]:
    box = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=spacing,
        align="center",
    )

    return (
        box[2] - box[0],
        box[3] - box[1],
    )


def _center_text(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    spacing: int = 4,
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int] | None = None,
) -> None:
    w, h = _text_box(
        draw,
        text,
        font,
        spacing,
    )

    draw.multiline_text(
        (
            int(x - w / 2),
            int(y - h / 2),
        ),
        text,
        font=font,
        fill=fill,
        spacing=spacing,
        align="center",
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def _category_title(
    key: str,
    language: str,
) -> str:
    data = {
        "uz": {
            "underweight": "KAM VAZN",
            "normal": "ME’YORIY VAZN",
            "overweight": "ORTIQCHA VAZN",
            "obesity_1": "1-DARAJALI SEMIZLIK",
            "obesity_2": "2-DARAJALI SEMIZLIK",
            "obesity_3": "3-DARAJALI SEMIZLIK",
        },
        "ru": {
            "underweight": "НЕДОСТАТОЧНЫЙ ВЕС",
            "normal": "НОРМАЛЬНЫЙ ВЕС",
            "overweight": "ИЗБЫТОЧНЫЙ ВЕС",
            "obesity_1": "ОЖИРЕНИЕ 1 СТЕПЕНИ",
            "obesity_2": "ОЖИРЕНИЕ 2 СТЕПЕНИ",
            "obesity_3": "ОЖИРЕНИЕ 3 СТЕПЕНИ",
        },
    }

    return data.get(
        language,
        data["uz"],
    ).get(
        key,
        key.upper(),
    )


def _badge_color(
    key: str,
) -> tuple[int, int, int]:
    return {
        "underweight": (32, 137, 229),
        "normal": (68, 181, 46),
        "overweight": (235, 169, 0),
        "obesity_1": (241, 90, 18),
        "obesity_2": (218, 49, 30),
        "obesity_3": (184, 0, 0),
    }.get(
        key,
        GREEN,
    )


def _bmi_to_angle(
    bmi: float,
) -> float:
    minimum = 14.0
    maximum = 45.0
    value = min(
        max(bmi, minimum),
        maximum,
    )
    ratio = (
        value - minimum
    ) / (
        maximum - minimum
    )

    return 180.0 + ratio * 180.0


def _point(
    cx: float,
    cy: float,
    radius: float,
    angle_deg: float,
) -> tuple[float, float]:
    angle = math.radians(angle_deg)

    return (
        cx + math.cos(angle) * radius,
        cy + math.sin(angle) * radius,
    )


def _ring_segment(
    image: Image.Image,
    center: tuple[int, int],
    outer_radius: int,
    inner_radius: int,
    start_angle: float,
    end_angle: float,
    color: tuple[int, int, int],
) -> None:
    overlay = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0),
    )
    draw = ImageDraw.Draw(overlay)

    cx, cy = center

    draw.pieslice(
        (
            cx - outer_radius,
            cy - outer_radius,
            cx + outer_radius,
            cy + outer_radius,
        ),
        start=start_angle,
        end=end_angle,
        fill=(*color, 255),
    )

    draw.pieslice(
        (
            cx - inner_radius,
            cy - inner_radius,
            cx + inner_radius,
            cy + inner_radius,
        ),
        start=start_angle - 1,
        end=end_angle + 1,
        fill=(255, 255, 255, 255),
    )

    image.alpha_composite(overlay)


def _needle(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    angle_deg: float,
    length: int,
) -> None:
    cx, cy = center
    angle = math.radians(angle_deg)
    perpendicular = angle + math.pi / 2

    tip = (
        cx + math.cos(angle) * length,
        cy + math.sin(angle) * length,
    )
    shoulder_distance = length - 55
    shoulder = (
        cx + math.cos(angle) * shoulder_distance,
        cy + math.sin(angle) * shoulder_distance,
    )

    base_half = 18
    shoulder_half = 9

    points = [
        (
            cx + math.cos(perpendicular) * base_half,
            cy + math.sin(perpendicular) * base_half,
        ),
        (
            shoulder[0] + math.cos(perpendicular) * shoulder_half,
            shoulder[1] + math.sin(perpendicular) * shoulder_half,
        ),
        tip,
        (
            shoulder[0] - math.cos(perpendicular) * shoulder_half,
            shoulder[1] - math.sin(perpendicular) * shoulder_half,
        ),
        (
            cx - math.cos(perpendicular) * base_half,
            cy - math.sin(perpendicular) * base_half,
        ),
    ]

    draw.polygon(
        [(int(x), int(y)) for x, y in points],
        fill=(22, 22, 22),
    )

    draw.ellipse(
        (
            cx - 34,
            cy - 34,
            cx + 34,
            cy + 34,
        ),
        fill=(25, 25, 25),
        outline=(70, 70, 70),
        width=6,
    )
    draw.ellipse(
        (
            cx - 19,
            cy - 19,
            cx + 19,
            cy + 19,
        ),
        fill=(85, 85, 85),
    )


def _metric_icon(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    code: str,
    color: tuple[int, int, int],
) -> None:
    pale = (
        min(color[0] + 205, 255),
        min(color[1] + 205, 255),
        min(color[2] + 205, 255),
    )

    draw.rounded_rectangle(
        (
            x - 34,
            y - 34,
            x + 34,
            y + 34,
        ),
        radius=17,
        fill=pale,
    )

    icon_font = _font(
        27 if len(code) > 1 else 40,
        bold=True,
    )

    _center_text(
        draw,
        x,
        y,
        code,
        icon_font,
        color,
    )


def _metric_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    value: str,
    color: tuple[int, int, int],
    icon_code: str,
) -> None:
    left, top, right, bottom = box
    center_x = (left + right) // 2

    draw.rounded_rectangle(
        box,
        radius=20,
        fill=WHITE,
        outline=(215, 232, 215),
        width=3,
    )

    _metric_icon(
        draw,
        center_x,
        top + 45,
        icon_code,
        color,
    )

    title_font = _font(
        24,
        bold=True,
    )
    value_font = _font(
        38,
        bold=True,
    )

    _center_text(
        draw,
        center_x,
        top + 110,
        title,
        title_font,
        BLACK,
        spacing=2,
    )
    _center_text(
        draw,
        center_x,
        top + 156,
        value,
        value_font,
        color,
        spacing=2,
    )


def create_bmi_card(
    bmi: float,
    category_key: str,
    normal_min_weight: float,
    normal_max_weight: float,
    ideal_weight: float,
    remaining_weight: float,
    language: str = "uz",
    current_weight: float | None = None,
    height_cm: float | None = None,
) -> Path:
    language = (
        language
        if language in {"uz", "ru"}
        else "uz"
    )

    if height_cm is None:
        height_cm = (
            math.sqrt(
                max(
                    ideal_weight,
                    1,
                )
                / 22.0
            )
            * 100.0
        )

    if current_weight is None:
        current_weight = (
            normal_max_weight
            + remaining_weight
            if remaining_weight > 0
            else ideal_weight
        )

    image = Image.new(
        "RGBA",
        (
            WIDTH,
            HEIGHT,
        ),
        (248, 251, 248, 255),
    )
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (
            8,
            8,
            WIDTH - 8,
            HEIGHT - 8,
        ),
        radius=42,
        fill=WHITE,
        outline=BORDER_GREEN,
        width=6,
    )

    title = (
        "BMI TAHLILI"
        if language == "uz"
        else "АНАЛИЗ BMI"
    )

    _center_text(
        draw,
        WIDTH / 2,
        55,
        title,
        _font(74, bold=True),
        DARK_GREEN,
    )

    center = (
        WIDTH // 2,
        575,
    )
    outer_radius = 535
    inner_radius = 350

    zones = [
        (
            "underweight",
            14.0,
            18.5,
            (32, 137, 229),
            "KAM VAZN\n< 18.5",
            "НЕДОСТАТОЧНЫЙ\nВЕС\n< 18.5",
            WHITE,
        ),
        (
            "normal",
            18.5,
            25.0,
            (67, 181, 46),
            "ME’YORIY VAZN\n18.5 – 24.9",
            "НОРМАЛЬНЫЙ ВЕС\n18.5 – 24.9",
            WHITE,
        ),
        (
            "overweight",
            25.0,
            30.0,
            (255, 211, 0),
            "ORTIQCHA VAZN\n25 – 29.9",
            "ИЗБЫТОЧНЫЙ ВЕС\n25 – 29.9",
            BLACK,
        ),
        (
            "obesity_1",
            30.0,
            35.0,
            (255, 137, 0),
            "1-DARAJALI\nSEMIZLIK\n30 – 34.9",
            "ОЖИРЕНИЕ\n1 СТЕПЕНИ\n30 – 34.9",
            WHITE,
        ),
        (
            "obesity_2",
            35.0,
            40.0,
            (239, 55, 23),
            "2-DARAJALI\nSEMIZLIK\n35 – 39.9",
            "ОЖИРЕНИЕ\n2 СТЕПЕНИ\n35 – 39.9",
            WHITE,
        ),
        (
            "obesity_3",
            40.0,
            45.0,
            (192, 0, 0),
            "3-DARAJALI\nSEMIZLIK\n≥ 40",
            "ОЖИРЕНИЕ\n3 СТЕПЕНИ\n≥ 40",
            WHITE,
        ),
    ]

    for _, start, end, color, *_ in zones:
        _ring_segment(
            image,
            center,
            outer_radius,
            inner_radius,
            _bmi_to_angle(start),
            _bmi_to_angle(end),
            color,
        )

    draw = ImageDraw.Draw(image)

    for boundary in (
        18.5,
        25.0,
        30.0,
        35.0,
        40.0,
    ):
        angle = _bmi_to_angle(boundary)

        p1 = _point(
            center[0],
            center[1],
            inner_radius - 2,
            angle,
        )
        p2 = _point(
            center[0],
            center[1],
            outer_radius + 2,
            angle,
        )

        draw.line(
            (
                int(p1[0]),
                int(p1[1]),
                int(p2[0]),
                int(p2[1]),
            ),
            fill=WHITE,
            width=5,
        )

    segment_fonts = {
        "underweight": _font(34, bold=True),
        "normal": _font(34, bold=True),
        "overweight": _font(34, bold=True),
        "obesity_1": _font(31, bold=True),
        "obesity_2": _font(31, bold=True),
        "obesity_3": _font(31, bold=True),
    }

    for key, start, end, _, uz_text, ru_text, text_color in zones:
        angle = _bmi_to_angle(
            (
                start + end
            )
            / 2
        )
        x, y = _point(
            center[0],
            center[1],
            440,
            angle,
        )

        _center_text(
            draw,
            x,
            y,
            (
                uz_text
                if language == "uz"
                else ru_text
            ),
            segment_fonts[key],
            text_color,
            spacing=4,
            stroke_width=0,
        )

    boundary_font = _font(
        49,
        bold=True,
    )

    for boundary in (
        18.5,
        25,
        30,
        35,
        40,
    ):
        angle = _bmi_to_angle(
            float(boundary)
        )
        x, y = _point(
            center[0],
            center[1],
            outer_radius + 45,
            angle,
        )

        _center_text(
            draw,
            x,
            y,
            str(boundary),
            boundary_font,
            BLACK,
        )

    for index in range(25):
        angle = (
            180
            + index
            / 24
            * 180
        )
        major = index % 4 == 0

        p1 = _point(
            center[0],
            center[1],
            inner_radius - (
                44
                if major
                else 29
            ),
            angle,
        )
        p2 = _point(
            center[0],
            center[1],
            inner_radius - 10,
            angle,
        )

        draw.line(
            (
                int(p1[0]),
                int(p1[1]),
                int(p2[0]),
                int(p2[1]),
            ),
            fill=(
                BLACK
                if major
                else (145, 145, 145)
            ),
            width=(
                5
                if major
                else 2
            ),
        )

    _needle(
        draw,
        center,
        _bmi_to_angle(bmi),
        320,
    )

    _center_text(
        draw,
        center[0],
        615,
        "BMI",
        _font(36, bold=True),
        BLACK,
    )
    _center_text(
        draw,
        center[0],
        680,
        f"{bmi:.2f}",
        _font(112, bold=True),
        GREEN,
    )

    badge_text = _category_title(
        category_key,
        language,
    )
    badge_font = _font(
        31,
        bold=True,
    )
    badge_width = max(
        390,
        _text_box(
            draw,
            badge_text,
            badge_font,
        )[0] + 80,
    )

    draw.rounded_rectangle(
        (
            int(center[0] - badge_width / 2),
            738,
            int(center[0] + badge_width / 2),
            794,
        ),
        radius=28,
        fill=_badge_color(
            category_key
        ),
    )
    _center_text(
        draw,
        center[0],
        766,
        badge_text,
        badge_font,
        WHITE,
    )

    if language == "uz":
        titles = (
            "Sizning vazningiz",
            "Sizning bo‘yingiz",
            "BMI ko‘rsatkichi",
            "Ideal vazn",
            "Normal vazn oralig‘i",
            "Yo‘qotish kerak",
        )
        kg = "kg"
        cm = "cm"
    else:
        titles = (
            "Ваш вес",
            "Ваш рост",
            "Показатель BMI",
            "Идеальный вес",
            "Нормальный диапазон",
            "Нужно снизить",
        )
        kg = "кг"
        cm = "см"

    values = (
        f"{current_weight:.1f} {kg}",
        f"{height_cm:.1f} {cm}",
        f"{bmi:.2f}",
        f"{ideal_weight:.1f} {kg}",
        (
            f"{normal_min_weight:.1f} – "
            f"{normal_max_weight:.1f} {kg}"
        ),
        (
            f"{remaining_weight:.1f} {kg}"
            if remaining_weight > 0
            else f"0 {kg}"
        ),
    )

    value_colors = (
        (24, 139, 38),
        (24, 139, 38),
        (31, 110, 205),
        (236, 108, 0),
        (87, 31, 174),
        (184, 20, 20),
    )
    icon_codes = (
        "W",
        "H",
        "BMI",
        "I",
        "N",
        "−",
    )

    margin = 24
    gap = 5
    top = 810
    bottom = 965
    card_width = (
        WIDTH
        - margin * 2
        - gap * 5
    ) // 6

    for index in range(6):
        left = (
            margin
            + index
            * (
                card_width
                + gap
            )
        )
        right = left + card_width

        _metric_card(
            draw,
            (
                left,
                top,
                right,
                bottom,
            ),
            titles[index],
            values[index],
            value_colors[index],
            icon_codes[index],
        )

    draw.rounded_rectangle(
        (
            24,
            974,
            WIDTH - 24,
            992,
        ),
        radius=9,
        fill=LIGHT_GREEN,
    )

    footer_text = (
        "Sog‘lom va baxtli hayot sari yana bir qadam!"
        if language == "uz"
        else
        "Ещё один шаг к здоровой и счастливой жизни!"
    )

    _center_text(
        draw,
        WIDTH / 2,
        983,
        footer_text,
        _font(22, bold=True),
        DARK_GREEN,
    )

    filename = (
        "bmi_card_"
        f"{category_key}_"
        f"{datetime.utcnow():%Y%m%d%H%M%S%f}"
        ".png"
    )

    output_path = OUTPUT_DIR / filename

    image.convert("RGB").save(
        output_path,
        format="PNG",
        optimize=True,
    )

    return output_path

