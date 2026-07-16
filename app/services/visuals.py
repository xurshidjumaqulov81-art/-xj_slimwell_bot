from __future__ import annotations

import math
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import ASSETS_DIR


OUTPUT_DIR = ASSETS_DIR / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []

    if bold:
        candidates.extend(
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            ]
        )

    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)

    return ImageFont.load_default()


def _category_title(category_key: str, language: str) -> str:
    titles = {
        "uz": {
            "underweight": "Kam vazn",
            "normal": "Me’yoriy vazn",
            "overweight": "Ortiqcha vazn",
            "obesity_1": "1-darajali semizlik",
            "obesity_2": "2-darajali semizlik",
            "obesity_3": "3-darajali semizlik",
        },
        "ru": {
            "underweight": "Недостаточный вес",
            "normal": "Нормальный вес",
            "overweight": "Избыточный вес",
            "obesity_1": "Ожирение 1 степени",
            "obesity_2": "Ожирение 2 степени",
            "obesity_3": "Ожирение 3 степени",
        },
    }

    return titles.get(language, titles["uz"]).get(
        category_key,
        category_key,
    )


def _bmi_to_angle(bmi: float) -> float:
    minimum_bmi = 14.0
    maximum_bmi = 45.0

    limited_bmi = max(
        minimum_bmi,
        min(bmi, maximum_bmi),
    )

    ratio = (
        limited_bmi - minimum_bmi
    ) / (
        maximum_bmi - minimum_bmi
    )

    return 180 - (ratio * 180)


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
) -> None:
    box = draw.textbbox(
        (0, 0),
        text,
        font=font,
    )

    width = box[2] - box[0]
    height = box[3] - box[1]

    x = xy[0] - width // 2
    y = xy[1] - height // 2

    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
    )


def create_bmi_card(
    bmi: float,
    category_key: str,
    normal_min_weight: float,
    normal_max_weight: float,
    ideal_weight: float,
    remaining_weight: float,
    language: str = "uz",
) -> Path:
    width = 1200
    height = 1200

    image = Image.new(
        "RGB",
        (width, height),
        (245, 249, 245),
    )

    draw = ImageDraw.Draw(image)

    title_font = _load_font(58, bold=True)
    large_font = _load_font(94, bold=True)
    medium_font = _load_font(42, bold=True)
    normal_font = _load_font(34)
    small_font = _load_font(27)

    draw.rounded_rectangle(
        (35, 35, width - 35, height - 35),
        radius=45,
        fill=(255, 255, 255),
        outline=(38, 146, 75),
        width=6,
    )

    title = (
        "BMI TAHLILI"
        if language == "uz"
        else "АНАЛИЗ BMI"
    )

    _draw_centered_text(
        draw,
        (width // 2, 105),
        title,
        title_font,
        (24, 100, 48),
    )

    center_x = width // 2
    center_y = 610

    outer_radius = 420
    inner_radius = 265

    zones = [
        (14.0, 18.5, (85, 170, 235)),
        (18.5, 25.0, (45, 180, 95)),
        (25.0, 30.0, (250, 205, 55)),
        (30.0, 35.0, (245, 145, 45)),
        (35.0, 40.0, (225, 75, 65)),
        (40.0, 45.0, (155, 30, 30)),
    ]

    for start_bmi, end_bmi, color in zones:
        start_angle = _bmi_to_angle(start_bmi)
        end_angle = _bmi_to_angle(end_bmi)

        draw.arc(
            (
                center_x - outer_radius,
                center_y - outer_radius,
                center_x + outer_radius,
                center_y + outer_radius,
            ),
            start=end_angle,
            end=start_angle,
            fill=color,
            width=outer_radius - inner_radius,
        )

    for value in [18.5, 25, 30, 35, 40]:
        angle = math.radians(
            _bmi_to_angle(value)
        )

        label_radius = 355

        x = center_x + (
            math.cos(angle) * label_radius
        )

        y = center_y - (
            math.sin(angle) * label_radius
        )

        _draw_centered_text(
            draw,
            (int(x), int(y)),
            str(value),
            small_font,
            (40, 40, 40),
        )

    needle_angle = math.radians(
        _bmi_to_angle(bmi)
    )

    needle_length = 310

    end_x = center_x + (
        math.cos(needle_angle) * needle_length
    )

    end_y = center_y - (
        math.sin(needle_angle) * needle_length
    )

    draw.line(
        (
            center_x,
            center_y,
            int(end_x),
            int(end_y),
        ),
        fill=(25, 25, 25),
        width=22,
    )

    arrow_size = 35

    left_angle = needle_angle + math.radians(150)
    right_angle = needle_angle - math.radians(150)

    left_x = end_x + math.cos(left_angle) * arrow_size
    left_y = end_y - math.sin(left_angle) * arrow_size

    right_x = end_x + math.cos(right_angle) * arrow_size
    right_y = end_y - math.sin(right_angle) * arrow_size

    draw.polygon(
        [
            (int(end_x), int(end_y)),
            (int(left_x), int(left_y)),
            (int(right_x), int(right_y)),
        ],
        fill=(25, 25, 25),
    )

    draw.ellipse(
        (
            center_x - 30,
            center_y - 30,
            center_x + 30,
            center_y + 30,
        ),
        fill=(40, 40, 40),
    )

    _draw_centered_text(
        draw,
        (center_x, 710),
        f"BMI {bmi:.2f}",
        large_font,
        (20, 80, 40),
    )

    category = _category_title(
        category_key,
        language,
    )

    _draw_centered_text(
        draw,
        (center_x, 805),
        category,
        medium_font,
        (40, 40, 40),
    )

    if language == "ru":
        range_text = (
            f"Нормальный диапазон: "
            f"{normal_min_weight:.1f}–"
            f"{normal_max_weight:.1f} кг"
        )

        ideal_text = (
            f"Идеальный вес: "
            f"{ideal_weight:.1f} кг"
        )

        remaining_text = (
            f"До здорового веса: "
            f"{remaining_weight:.1f} кг"
            if remaining_weight > 0
            else "Ваш вес находится в здоровом диапазоне"
        )
    else:
        range_text = (
            f"Norma vazn oralig‘i: "
            f"{normal_min_weight:.1f}–"
            f"{normal_max_weight:.1f} kg"
        )

        ideal_text = (
            f"Ideal vazn: "
            f"{ideal_weight:.1f} kg"
        )

        remaining_text = (
            f"Sog‘lom vazngacha: "
            f"{remaining_weight:.1f} kg"
            if remaining_weight > 0
            else "Vazningiz sog‘lom oraliqda"
        )

    _draw_centered_text(
        draw,
        (center_x, 900),
        range_text,
        normal_font,
        (40, 40, 40),
    )

    _draw_centered_text(
        draw,
        (center_x, 955),
        ideal_text,
        normal_font,
        (40, 40, 40),
    )

    draw.rounded_rectangle(
        (150, 1010, width - 150, 1105),
        radius=30,
        fill=(228, 245, 232),
    )

    _draw_centered_text(
        draw,
        (center_x, 1058),
        remaining_text,
        medium_font,
        (24, 110, 50),
    )

    filename = (
        f"bmi_{bmi:.2f}_"
        f"{category_key}_"
        f"{language}.png"
    ).replace(".", "_")

    output_path = OUTPUT_DIR / filename

    image.save(
        output_path,
        format="PNG",
        optimize=True,
    )

    return output_path
