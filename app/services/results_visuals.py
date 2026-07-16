from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

from app.config import GENERATED_ASSETS_DIR


WIDTH = 1200
HEIGHT = 900

MARGIN_LEFT = 120
MARGIN_RIGHT = 70
MARGIN_TOP = 190
MARGIN_BOTTOM = 160


def load_font(
    size: int,
    bold: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for font_path in candidates:
        path = Path(font_path)

        if path.exists():
            return ImageFont.truetype(
                str(path),
                size=size,
            )

    return ImageFont.load_default()


def centered_text(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
) -> None:
    box = draw.textbbox(
        (0, 0),
        text,
        font=font,
    )

    text_width = box[2] - box[0]

    draw.text(
        (
            x - text_width // 2,
            y,
        ),
        text,
        font=font,
        fill=fill,
    )


def format_weight(
    value: float,
) -> str:
    if value.is_integer():
        return str(int(value))

    return f"{value:.1f}"


def create_weight_chart(
    records: Sequence[object],
    current_weight: float,
    normal_max_weight: float,
    ideal_weight: float,
    language: str = "uz",
) -> Path:
    """
    records elementlarida quyidagi qiymatlar bo‘lishi kerak:

    record.weight_kg
    record.recorded_at
    """

    GENERATED_ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = Image.new(
        "RGB",
        (
            WIDTH,
            HEIGHT,
        ),
        (
            244,
            249,
            244,
        ),
    )

    draw = ImageDraw.Draw(image)

    title_font = load_font(
        52,
        bold=True,
    )

    subtitle_font = load_font(
        30,
    )

    value_font = load_font(
        35,
        bold=True,
    )

    label_font = load_font(
        25,
    )

    small_font = load_font(
        21,
    )

    draw.rounded_rectangle(
        (
            30,
            30,
            WIDTH - 30,
            HEIGHT - 30,
        ),
        radius=45,
        fill=(
            255,
            255,
            255,
        ),
        outline=(
            36,
            144,
            73,
        ),
        width=5,
    )

    if language == "ru":
        title = "ДИНАМИКА ВЕСА"
        subtitle = "Изменение веса по вашим записям"
    else:
        title = "VAZN DINAMIKASI"
        subtitle = "Kiritilgan vaznlar bo‘yicha o‘zgarish"

    centered_text(
        draw,
        WIDTH // 2,
        70,
        title,
        title_font,
        (
            25,
            102,
            50,
        ),
    )

    centered_text(
        draw,
        WIDTH // 2,
        135,
        subtitle,
        subtitle_font,
        (
            80,
            90,
            80,
        ),
    )

    usable_records = list(records)[-12:]

    if not usable_records:
        usable_records = []

    chart_left = MARGIN_LEFT
    chart_top = MARGIN_TOP
    chart_right = WIDTH - MARGIN_RIGHT
    chart_bottom = HEIGHT - MARGIN_BOTTOM

    draw.rounded_rectangle(
        (
            chart_left,
            chart_top,
            chart_right,
            chart_bottom,
        ),
        radius=25,
        fill=(
            248,
            252,
            248,
        ),
        outline=(
            210,
            225,
            212,
        ),
        width=3,
    )

    weights = [
        float(record.weight_kg)
        for record in usable_records
    ]

    if not weights:
        weights = [
            float(current_weight),
        ]

    reference_values = (
        weights
        + [
            float(normal_max_weight),
            float(ideal_weight),
        ]
    )

    min_weight = min(reference_values)
    max_weight = max(reference_values)

    padding = max(
        2.0,
        (
            max_weight - min_weight
        )
        * 0.15,
    )

    y_min = max(
        0,
        min_weight - padding,
    )

    y_max = max_weight + padding

    if y_max == y_min:
        y_max += 1

    grid_lines = 5

    for index in range(
        grid_lines + 1
    ):
        ratio = (
            index / grid_lines
        )

        y = int(
            chart_bottom
            - (
                ratio
                * (
                    chart_bottom
                    - chart_top
                )
            )
        )

        value = (
            y_min
            + (
                ratio
                * (
                    y_max - y_min
                )
            )
        )

        draw.line(
            (
                chart_left,
                y,
                chart_right,
                y,
            ),
            fill=(
                224,
                232,
                225,
            ),
            width=2,
        )

        draw.text(
            (
                45,
                y - 14,
            ),
            f"{value:.1f}",
            font=small_font,
            fill=(
                90,
                100,
                90,
            ),
        )

    def weight_to_y(
        weight: float,
    ) -> int:
        ratio = (
            weight - y_min
        ) / (
            y_max - y_min
        )

        return int(
            chart_bottom
            - ratio
            * (
                chart_bottom
                - chart_top
            )
        )

    normal_y = weight_to_y(
        normal_max_weight
    )

    ideal_y = weight_to_y(
        ideal_weight
    )

    draw.line(
        (
            chart_left,
            normal_y,
            chart_right,
            normal_y,
        ),
        fill=(
            245,
            166,
            35,
        ),
        width=4,
    )

    draw.line(
        (
            chart_left,
            ideal_y,
            chart_right,
            ideal_y,
        ),
        fill=(
            55,
            170,
            90,
        ),
        width=4,
    )

    normal_label = (
        "Norma chegarasi"
        if language == "uz"
        else "Граница нормы"
    )

    ideal_label = (
        "Ideal vazn"
        if language == "uz"
        else "Идеальный вес"
    )

    draw.text(
        (
            chart_right - 230,
            normal_y - 35,
        ),
        (
            f"{normal_label}: "
            f"{normal_max_weight:.1f}"
        ),
        font=small_font,
        fill=(
            180,
            105,
            15,
        ),
    )

    draw.text(
        (
            chart_right - 210,
            ideal_y + 8,
        ),
        (
            f"{ideal_label}: "
            f"{ideal_weight:.1f}"
        ),
        font=small_font,
        fill=(
            25,
            125,
            60,
        ),
    )

    points: list[
        tuple[int, int]
    ] = []

    record_count = len(
        usable_records
    )

    for index, record in enumerate(
        usable_records
    ):
        if record_count <= 1:
            x = (
                chart_left
                + chart_right
            ) // 2
        else:
            x = int(
                chart_left
                + (
                    index
                    / (
                        record_count - 1
                    )
                )
                * (
                    chart_right
                    - chart_left
                )
            )

        weight = float(
            record.weight_kg
        )

        y = weight_to_y(
            weight
        )

        points.append(
            (
                x,
                y,
            )
        )

    if len(points) >= 2:
        draw.line(
            points,
            fill=(
                32,
                132,
                68,
            ),
            width=8,
            joint="curve",
        )

    for index, (
        point,
        record,
    ) in enumerate(
        zip(
            points,
            usable_records,
        )
    ):
        x, y = point

        draw.ellipse(
            (
                x - 11,
                y - 11,
                x + 11,
                y + 11,
            ),
            fill=(
                255,
                255,
                255,
            ),
            outline=(
                25,
                125,
                62,
            ),
            width=6,
        )

        weight = float(
            record.weight_kg
        )

        centered_text(
            draw,
            x,
            y - 48,
            format_weight(
                weight
            ),
            small_font,
            (
                35,
                70,
                42,
            ),
        )

        recorded_at = getattr(
            record,
            "recorded_at",
            None,
        )

        if isinstance(
            recorded_at,
            datetime,
        ):
            date_text = recorded_at.strftime(
                "%d.%m"
            )
        else:
            date_text = str(
                index + 1
            )

        centered_text(
            draw,
            x,
            chart_bottom + 18,
            date_text,
            small_font,
            (
                80,
                90,
                80,
            ),
        )

    first_weight = float(
        weights[0]
    )

    last_weight = float(
        weights[-1]
    )

    difference = round(
        last_weight - first_weight,
        1,
    )

    if language == "ru":
        current_label = "Текущий вес"
        change_label = "Изменение"
        kg_text = "кг"
    else:
        current_label = "Hozirgi vazn"
        change_label = "O‘zgarish"
        kg_text = "kg"

    draw.rounded_rectangle(
        (
            120,
            770,
            545,
            845,
        ),
        radius=25,
        fill=(
            232,
            246,
            235,
        ),
    )

    draw.text(
        (
            145,
            785,
        ),
        f"{current_label}:",
        font=label_font,
        fill=(
            50,
            80,
            55,
        ),
    )

    draw.text(
        (
            365,
            780,
        ),
        (
            f"{format_weight(last_weight)} "
            f"{kg_text}"
        ),
        font=value_font,
        fill=(
            24,
            112,
            52,
        ),
    )

    if difference < 0:
        change_value = (
            f"−{abs(difference):.1f}"
        )
    elif difference > 0:
        change_value = (
            f"+{difference:.1f}"
        )
    else:
        change_value = "0"

    draw.rounded_rectangle(
        (
            620,
            770,
            1080,
            845,
        ),
        radius=25,
        fill=(
            242,
            247,
            235,
        ),
    )

    draw.text(
        (
            650,
            785,
        ),
        f"{change_label}:",
        font=label_font,
        fill=(
            50,
            80,
            55,
        ),
    )

    draw.text(
        (
            850,
            780,
        ),
        (
            f"{change_value} "
            f"{kg_text}"
        ),
        font=value_font,
        fill=(
            24,
            112,
            52,
        ),
    )

    filename = (
        f"weight_chart_"
        f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        ".png"
    )

    output_path = (
        GENERATED_ASSETS_DIR
        / filename
    )

    image.save(
        output_path,
        format="PNG",
        optimize=True,
    )

    return output_path


def create_progress_bar(
    current_weight: float,
    start_weight: float,
    target_weight: float,
    language: str = "uz",
) -> Path:
    width = 1200
    height = 500

    image = Image.new(
        "RGB",
        (
            width,
            height,
        ),
        (
            247,
            250,
            247,
        ),
    )

    draw = ImageDraw.Draw(image)

    title_font = load_font(
        50,
        bold=True,
    )

    value_font = load_font(
        38,
        bold=True,
    )

    normal_font = load_font(
        29,
    )

    draw.rounded_rectangle(
        (
            30,
            30,
            width - 30,
            height - 30,
        ),
        radius=45,
        fill=(
            255,
            255,
            255,
        ),
        outline=(
            38,
            146,
            75,
        ),
        width=5,
    )

    title = (
        "MAQSADGACHA NATIJA"
        if language == "uz"
        else "ПРОГРЕСС К ЦЕЛИ"
    )

    centered_text(
        draw,
        width // 2,
        65,
        title,
        title_font,
        (
            25,
            105,
            52,
        ),
    )

    total_to_lose = max(
        start_weight - target_weight,
        0.1,
    )

    lost_weight = max(
        start_weight - current_weight,
        0,
    )

    progress = min(
        max(
            lost_weight
            / total_to_lose,
            0,
        ),
        1,
    )

    percentage = round(
        progress * 100
    )

    bar_left = 120
    bar_top = 225
    bar_right = width - 120
    bar_bottom = 300

    draw.rounded_rectangle(
        (
            bar_left,
            bar_top,
            bar_right,
            bar_bottom,
        ),
        radius=32,
        fill=(
            225,
            232,
            225,
        ),
    )

    progress_right = int(
        bar_left
        + progress
        * (
            bar_right
            - bar_left
        )
    )

    if progress_right > bar_left:
        draw.rounded_rectangle(
            (
                bar_left,
                bar_top,
                progress_right,
                bar_bottom,
            ),
            radius=32,
            fill=(
                42,
                163,
                81,
            ),
        )

    centered_text(
        draw,
        width // 2,
        230,
        f"{percentage}%",
        value_font,
        (
            255,
            255,
            255,
        )
        if percentage >= 15
        else (
            35,
            90,
            45,
        ),
    )

    if language == "ru":
        start_text = (
            f"Старт: {start_weight:.1f} кг"
        )

        current_text = (
            f"Сейчас: {current_weight:.1f} кг"
        )

        target_text = (
            f"Цель: {target_weight:.1f} кг"
        )
    else:
        start_text = (
            f"Boshlanish: {start_weight:.1f} kg"
        )

        current_text = (
            f"Hozir: {current_weight:.1f} kg"
        )

        target_text = (
            f"Maqsad: {target_weight:.1f} kg"
        )

    draw.text(
        (
            120,
            355,
        ),
        start_text,
        font=normal_font,
        fill=(
            60,
            70,
            60,
        ),
    )

    centered_text(
        draw,
        width // 2,
        355,
        current_text,
        normal_font,
        (
            30,
            110,
            50,
        ),
    )

    target_box = draw.textbbox(
        (
            0,
            0,
        ),
        target_text,
        font=normal_font,
    )

    target_width = (
        target_box[2]
        - target_box[0]
    )

    draw.text(
        (
            width
            - 120
            - target_width,
            355,
        ),
        target_text,
        font=normal_font,
        fill=(
            60,
            70,
            60,
        ),
    )

    filename = (
        f"progress_"
        f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        ".png"
    )

    output_path = (
        GENERATED_ASSETS_DIR
        / filename
    )

    image.save(
        output_path,
        format="PNG",
        optimize=True,
    )

    return output_path

