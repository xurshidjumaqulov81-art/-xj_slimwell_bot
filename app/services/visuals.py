from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Final

from PIL import Image, ImageDraw, ImageFont

from app.config import ASSETS_DIR


OUTPUT_DIR: Final[Path] = ASSETS_DIR / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CARD_WIDTH: Final[int] = 1600
CARD_HEIGHT: Final[int] = 1067

GREEN: Final[tuple[int, int, int]] = (26, 128, 38)
DARK_GREEN: Final[tuple[int, int, int]] = (13, 106, 25)
LIGHT_GREEN: Final[tuple[int, int, int]] = (239, 249, 239)
BORDER_GREEN: Final[tuple[int, int, int]] = (31, 137, 55)
BLACK: Final[tuple[int, int, int]] = (25, 25, 25)
WHITE: Final[tuple[int, int, int]] = (255, 255, 255)


def _font_candidates(bold: bool) -> list[Path]:
    filenames = (
        [
            "DejaVuSans-Bold.ttf",
            "LiberationSans-Bold.ttf",
            "Arial Bold.ttf",
            "Arial-Bold.ttf",
        ]
        if bold
        else [
            "DejaVuSans.ttf",
            "LiberationSans-Regular.ttf",
            "Arial.ttf",
        ]
    )

    roots = [
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path("/usr/local/lib"),
        Path("/opt"),
    ]

    candidates: list[Path] = []

    for root in roots:
        if not root.exists():
            continue

        for filename in filenames:
            try:
                candidates.extend(root.rglob(filename))
            except OSError:
                continue

    return candidates


def _load_font(
    size: int,
    bold: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in _font_candidates(bold):
        try:
            return ImageFont.truetype(
                str(path),
                size=size,
            )
        except OSError:
            continue

    # Ko‘p Linux serverlarda bu nom Pillow orqali topiladi.
    fallback_names = (
        ["DejaVuSans-Bold.ttf", "Arial.ttf"]
        if bold
        else ["DejaVuSans.ttf", "Arial.ttf"]
    )

    for name in fallback_names:
        try:
            return ImageFont.truetype(
                name,
                size=size,
            )
        except OSError:
            continue

    return ImageFont.load_default()


def _text_size(
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
    width, height = _text_size(
        draw,
        text,
        font,
        spacing,
    )

    draw.multiline_text(
        (
            int(x - width / 2),
            int(y - height / 2),
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
    category_key: str,
    language: str,
) -> str:
    values = {
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

    return values.get(
        language,
        values["uz"],
    ).get(
        category_key,
        category_key.upper(),
    )


def _category_badge_color(
    category_key: str,
) -> tuple[int, int, int]:
    return {
        "underweight": (32, 137, 229),
        "normal": (68, 181, 46),
        "overweight": (241, 171, 0),
        "obesity_1": (240, 87, 20),
        "obesity_2": (221, 48, 28),
        "obesity_3": (183, 0, 0),
    }.get(
        category_key,
        (35, 130, 55),
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

    # PIL burchagi: 180° chap, 270° tepa, 360° o‘ng.
    return 180.0 + ratio * 180.0


def _point_on_circle(
    center_x: float,
    center_y: float,
    radius: float,
    angle_deg: float,
) -> tuple[float, float]:
    angle = math.radians(angle_deg)

    return (
        center_x + math.cos(angle) * radius,
        center_y + math.sin(angle) * radius,
    )


def _draw_ring_segment(
    image: Image.Image,
    center: tuple[int, int],
    outer_radius: int,
    inner_radius: int,
    start_angle: float,
    end_angle: float,
    color: tuple[int, int, int],
) -> None:
    layer = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0),
    )
    layer_draw = ImageDraw.Draw(layer)

    cx, cy = center

    outer_box = (
        cx - outer_radius,
        cy - outer_radius,
        cx + outer_radius,
        cy + outer_radius,
    )
    inner_box = (
        cx - inner_radius,
        cy - inner_radius,
        cx + inner_radius,
        cy + inner_radius,
    )

    layer_draw.pieslice(
        outer_box,
        start=start_angle,
        end=end_angle,
        fill=(*color, 255),
    )
    layer_draw.pieslice(
        inner_box,
        start=start_angle - 1,
        end=end_angle + 1,
        fill=(255, 255, 255, 255),
    )

    image.alpha_composite(layer)


def _draw_leaf(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    flip: bool = False,
) -> None:
    direction = -1 if flip else 1

    draw.ellipse(
        (
            x - 22,
            y - 12,
            x + 20,
            y + 18,
        ),
        fill=(55, 164, 45),
    )

    draw.line(
        (
            x - 20 * direction,
            y + 18,
            x + 24 * direction,
            y - 18,
        ),
        fill=(25, 115, 35),
        width=5,
    )


def _draw_needle(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    angle_deg: float,
    length: int,
) -> None:
    cx, cy = center
    angle = math.radians(angle_deg)

    tip_x = cx + math.cos(angle) * length
    tip_y = cy + math.sin(angle) * length

    perpendicular = angle + math.pi / 2
    base_half = 16
    shoulder_half = 9

    base_left = (
        cx + math.cos(perpendicular) * base_half,
        cy + math.sin(perpendicular) * base_half,
    )
    base_right = (
        cx - math.cos(perpendicular) * base_half,
        cy - math.sin(perpendicular) * base_half,
    )

    shoulder_distance = length - 55
    shoulder_x = cx + math.cos(angle) * shoulder_distance
    shoulder_y = cy + math.sin(angle) * shoulder_distance

    shoulder_left = (
        shoulder_x + math.cos(perpendicular) * shoulder_half,
        shoulder_y + math.sin(perpendicular) * shoulder_half,
    )
    shoulder_right = (
        shoulder_x - math.cos(perpendicular) * shoulder_half,
        shoulder_y - math.sin(perpendicular) * shoulder_half,
    )

    draw.polygon(
        [
            (int(base_left[0]), int(base_left[1])),
            (int(shoulder_left[0]), int(shoulder_left[1])),
            (int(tip_x), int(tip_y)),
            (int(shoulder_right[0]), int(shoulder_right[1])),
            (int(base_right[0]), int(base_right[1])),
        ],
        fill=(22, 22, 22),
    )

    draw.ellipse(
        (
            cx - 30,
            cy - 30,
            cx + 30,
            cy + 30,
        ),
        fill=(20, 20, 20),
        outline=(55, 55, 55),
        width=6,
    )
    draw.ellipse(
        (
            cx - 17,
            cy - 17,
            cx + 17,
            cy + 17,
        ),
        fill=(65, 65, 65),
    )


def _draw_metric_icon(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    center_y: int,
    kind: str,
    color: tuple[int, int, int],
) -> None:
    draw.rounded_rectangle(
        (
            center_x - 36,
            center_y - 36,
            center_x + 36,
            center_y + 36,
        ),
        radius=18,
        fill=(
            min(color[0] + 205, 255),
            min(color[1] + 205, 255),
            min(color[2] + 205, 255),
        ),
    )

    icon_font = _load_font(
        45,
        bold=True,
    )

    symbols = {
        "weight": "⚖",
        "height": "↕",
        "bmi": "BMI",
        "ideal": "◎",
        "range": "⚖",
        "remaining": "🔥",
    }

    symbol = symbols.get(
        kind,
        "•",
    )

    symbol_font = (
        _load_font(24, bold=True)
        if kind == "bmi"
        else icon_font
    )

    _center_text(
        draw,
        center_x,
        center_y,
        symbol,
        symbol_font,
        color,
    )


def _draw_metric_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    value: str,
    value_color: tuple[int, int, int],
    icon_kind: str,
) -> None:
    left, top, right, bottom = box

    draw.rounded_rectangle(
        box,
        radius=22,
        fill=(255, 255, 255),
        outline=(218, 235, 218),
        width=3,
    )

    center_x = (left + right) // 2

    _draw_metric_icon(
        draw,
        center_x,
        top + 55,
        icon_kind,
        value_color,
    )

    title_font = _load_font(
        21,
        bold=True,
    )
    value_font = _load_font(
        31,
        bold=True,
    )

    _center_text(
        draw,
        center_x,
        top + 123,
        title,
        title_font,
        (25, 25, 25),
    )
    _center_text(
        draw,
        center_x,
        top + 165,
        value,
        value_font,
        value_color,
    )


def _format_number(
    value: float,
    digits: int = 1,
) -> str:
    return f"{value:.{digits}f}"


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
    """
    Premium BMI kartasini yaratadi.

    `current_weight` va `height_cm` eski body.py bilan moslik uchun
    ixtiyoriy. Berilmasa, mavjud metrikalardan taxmin qilinadi.
    """

    selected_language = (
        language
        if language in {"uz", "ru"}
        else "uz"
    )

    if height_cm is None:
        # health.py ideal vaznni BMI 22 bo‘yicha hisoblaydi.
        height_cm = (
            math.sqrt(
                max(ideal_weight, 1) / 22.0
            )
            * 100.0
        )

    if current_weight is None:
        if remaining_weight > 0:
            current_weight = (
                normal_max_weight
                + remaining_weight
            )
        else:
            current_weight = ideal_weight

    image = Image.new(
        "RGBA",
        (
            CARD_WIDTH,
            CARD_HEIGHT,
        ),
        (248, 251, 248, 255),
    )
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (
            8,
            8,
            CARD_WIDTH - 8,
            CARD_HEIGHT - 8,
        ),
        radius=45,
        fill=(255, 255, 255),
        outline=BORDER_GREEN,
        width=6,
    )

    title_font = _load_font(
        72,
        bold=True,
    )

    title = (
        "BMI TAHLILI"
        if selected_language == "uz"
        else "АНАЛИЗ BMI"
    )

    _center_text(
        draw,
        CARD_WIDTH / 2,
        60,
        title,
        title_font,
        DARK_GREEN,
    )
    _draw_leaf(
        draw,
        525,
        58,
        flip=True,
    )
    _draw_leaf(
        draw,
        1075,
        58,
        flip=False,
    )

    center = (
        CARD_WIDTH // 2,
        585,
    )
    outer_radius = 545
    inner_radius = 355

    zones = [
        {
            "key": "underweight",
            "start": 14.0,
            "end": 18.5,
            "color": (32, 137, 229),
            "uz": "KAM VAZN\n< 18.5",
            "ru": "НЕДОСТАТОЧНЫЙ\nВЕС\n< 18.5",
            "text_color": WHITE,
        },
        {
            "key": "normal",
            "start": 18.5,
            "end": 25.0,
            "color": (67, 181, 46),
            "uz": "ME’YORIY VAZN\n18.5 – 24.9",
            "ru": "НОРМАЛЬНЫЙ ВЕС\n18.5 – 24.9",
            "text_color": WHITE,
        },
        {
            "key": "overweight",
            "start": 25.0,
            "end": 30.0,
            "color": (255, 211, 0),
            "uz": "ORTIQCHA VAZN\n25 – 29.9",
            "ru": "ИЗБЫТОЧНЫЙ ВЕС\n25 – 29.9",
            "text_color": BLACK,
        },
        {
            "key": "obesity_1",
            "start": 30.0,
            "end": 35.0,
            "color": (255, 137, 0),
            "uz": "1-DARAJALI\nSEMIZLIK\n30 – 34.9",
            "ru": "ОЖИРЕНИЕ\n1 СТЕПЕНИ\n30 – 34.9",
            "text_color": WHITE,
        },
        {
            "key": "obesity_2",
            "start": 35.0,
            "end": 40.0,
            "color": (239, 55, 23),
            "uz": "2-DARAJALI\nSEMIZLIK\n35 – 39.9",
            "ru": "ОЖИРЕНИЕ\n2 СТЕПЕНИ\n35 – 39.9",
            "text_color": WHITE,
        },
        {
            "key": "obesity_3",
            "start": 40.0,
            "end": 45.0,
            "color": (192, 0, 0),
            "uz": "3-DARAJALI\nSEMIZLIK\n≥ 40",
            "ru": "ОЖИРЕНИЕ\n3 СТЕПЕНИ\n≥ 40",
            "text_color": WHITE,
        },
    ]

    for zone in zones:
        _draw_ring_segment(
            image,
            center,
            outer_radius,
            inner_radius,
            _bmi_to_angle(zone["start"]),
            _bmi_to_angle(zone["end"]),
            zone["color"],
        )

    draw = ImageDraw.Draw(image)

    # Segment chegaralari.
    for boundary in [
        18.5,
        25.0,
        30.0,
        35.0,
        40.0,
    ]:
        angle = _bmi_to_angle(boundary)
        inner_point = _point_on_circle(
            center[0],
            center[1],
            inner_radius - 2,
            angle,
        )
        outer_point = _point_on_circle(
            center[0],
            center[1],
            outer_radius + 2,
            angle,
        )

        draw.line(
            (
                int(inner_point[0]),
                int(inner_point[1]),
                int(outer_point[0]),
                int(outer_point[1]),
            ),
            fill=WHITE,
            width=5,
        )

    # Segment ichidagi matnlar.
    segment_font = _load_font(
        28,
        bold=True,
    )
    segment_font_small = _load_font(
        25,
        bold=True,
    )

    for zone in zones:
        middle_bmi = (
            zone["start"]
            + zone["end"]
        ) / 2
        middle_angle = _bmi_to_angle(
            middle_bmi
        )
        text_radius = (
            inner_radius
            + (
                outer_radius
                - inner_radius
            )
            * 0.55
        )

        text_x, text_y = _point_on_circle(
            center[0],
            center[1],
            text_radius,
            middle_angle,
        )

        font = (
            segment_font_small
            if zone["key"] in {
                "obesity_1",
                "obesity_2",
                "obesity_3",
            }
            else segment_font
        )

        _center_text(
            draw,
            text_x,
            text_y,
            zone[selected_language],
            font,
            zone["text_color"],
            spacing=5,
        )

    # Chegara raqamlari.
    boundary_font = _load_font(
        43,
        bold=True,
    )

    for boundary in [
        18.5,
        25,
        30,
        35,
        40,
    ]:
        angle = _bmi_to_angle(
            float(boundary)
        )
        x, y = _point_on_circle(
            center[0],
            center[1],
            outer_radius + 48,
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

    # Ichki shkala chiziqlari.
    for index in range(25):
        ratio = index / 24
        angle = 180 + ratio * 180

        major = (
            index % 4 == 0
        )
        outer_tick = inner_radius - 12
        inner_tick = (
            inner_radius - 42
            if major
            else inner_radius - 28
        )

        start = _point_on_circle(
            center[0],
            center[1],
            inner_tick,
            angle,
        )
        end = _point_on_circle(
            center[0],
            center[1],
            outer_tick,
            angle,
        )

        draw.line(
            (
                int(start[0]),
                int(start[1]),
                int(end[0]),
                int(end[1]),
            ),
            fill=(
                (25, 25, 25)
                if major
                else (150, 150, 150)
            ),
            width=(
                5
                if major
                else 2
            ),
        )

    _draw_needle(
        draw,
        center,
        _bmi_to_angle(bmi),
        325,
    )

    # Markaziy BMI.
    bmi_label_font = _load_font(
        34,
        bold=True,
    )
    bmi_value_font = _load_font(
        96,
        bold=True,
    )
    badge_font = _load_font(
        27,
        bold=True,
    )

    _center_text(
        draw,
        center[0],
        625,
        "BMI",
        bmi_label_font,
        BLACK,
    )
    _center_text(
        draw,
        center[0],
        685,
        f"{bmi:.2f}",
        bmi_value_font,
        GREEN,
    )

    badge_text = _category_title(
        category_key,
        selected_language,
    )
    badge_color = _category_badge_color(
        category_key
    )

    badge_width = max(
        360,
        _text_size(
            draw,
            badge_text,
            badge_font,
        )[0] + 70,
    )
    badge_left = int(
        center[0] - badge_width / 2
    )
    badge_right = int(
        center[0] + badge_width / 2
    )

    draw.rounded_rectangle(
        (
            badge_left,
            735,
            badge_right,
            785,
        ),
        radius=25,
        fill=badge_color,
    )
    _center_text(
        draw,
        center[0],
        760,
        badge_text,
        badge_font,
        WHITE,
    )

    # Pastdagi 6 ta ko‘rsatkich kartasi.
    if selected_language == "ru":
        titles = [
            "Ваш вес",
            "Ваш рост",
            "Показатель BMI",
            "Идеальный вес",
            "Нормальный диапазон",
            "Нужно снизить",
        ]
        unit_kg = "кг"
        unit_cm = "см"
    else:
        titles = [
            "Sizning vazningiz",
            "Sizning bo‘yingiz",
            "BMI ko‘rsatkichi",
            "Ideal vazn",
            "Normal vazn oralig‘i",
            "Yo‘qotish kerak",
        ]
        unit_kg = "kg"
        unit_cm = "cm"

    values = [
        f"{_format_number(current_weight)} {unit_kg}",
        f"{_format_number(height_cm)} {unit_cm}",
        f"{bmi:.2f}",
        f"{_format_number(ideal_weight)} {unit_kg}",
        (
            f"{_format_number(normal_min_weight)} – "
            f"{_format_number(normal_max_weight)} {unit_kg}"
        ),
        (
            f"{_format_number(remaining_weight)} {unit_kg}"
            if remaining_weight > 0
            else (
                "0 kg"
                if selected_language == "uz"
                else "0 кг"
            )
        ),
    ]

    value_colors = [
        (24, 139, 38),
        (24, 139, 38),
        (31, 110, 205),
        (236, 108, 0),
        (87, 31, 174),
        (184, 20, 20),
    ]
    icon_kinds = [
        "weight",
        "height",
        "bmi",
        "ideal",
        "range",
        "remaining",
    ]

    margin_x = 28
    gap = 5
    cards_top = 810
    cards_bottom = 1000
    available_width = (
        CARD_WIDTH
        - margin_x * 2
        - gap * 5
    )
    card_width = available_width // 6

    for index in range(6):
        left = (
            margin_x
            + index * (
                card_width + gap
            )
        )
        right = left + card_width

        _draw_metric_card(
            draw,
            (
                left,
                cards_top,
                right,
                cards_bottom,
            ),
            titles[index],
            values[index],
            value_colors[index],
            icon_kinds[index],
        )

    # Pastki motivatsion banner.
    draw.rounded_rectangle(
        (
            28,
            1012,
            CARD_WIDTH - 28,
            1050,
        ),
        radius=18,
        fill=(236, 247, 235),
    )

    footer_bold = _load_font(
        22,
        bold=True,
    )
    footer_regular = _load_font(
        17,
        bold=False,
    )

    footer_title = (
        "Sog‘lom va baxtli hayot sari yana bir qadam!"
        if selected_language == "uz"
        else
        "Ещё один шаг к здоровой и счастливой жизни!"
    )
    footer_subtitle = (
        "To‘g‘ri ovqatlaning, faol bo‘ling va o‘zingizni seving!"
        if selected_language == "uz"
        else
        "Питайтесь правильно, будьте активны и любите себя!"
    )

    draw.ellipse(
        (
            390,
            1018,
            422,
            1048,
        ),
        fill=(34, 139, 48),
    )
    _center_text(
        draw,
        900,
        1025,
        footer_title,
        footer_bold,
        DARK_GREEN,
    )
    _center_text(
        draw,
        900,
        1043,
        footer_subtitle,
        footer_regular,
        BLACK,
    )

    filename = (
        "bmi_card_"
        f"{category_key}_"
        f"{bmi:.2f}_"
        f"{datetime.utcnow():%Y%m%d%H%M%S%f}"
        ".png"
    ).replace(
        ".",
        "_",
    )

    # Oxirgi kengaytmani qayta tiklaymiz.
    filename = (
        filename[:-4] + ".png"
        if filename.endswith("_png")
        else filename
    )

    output_path = OUTPUT_DIR / filename

    image.convert("RGB").save(
        output_path,
        format="PNG",
        optimize=True,
    )

    return output_path

