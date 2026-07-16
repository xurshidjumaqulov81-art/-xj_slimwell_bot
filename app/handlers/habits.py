from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.crud import (
    add_water,
    get_today_summary,
    get_user,
)
from app.database.db import SessionFactory
from app.keyboards import habits_menu
from app.states import HabitInput


router = Router()


def card(
    title: str,
    body: str,
) -> str:
    return (
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>{title}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{body}"
    )


async def load_user(
    telegram_id: int,
):
    async with SessionFactory() as session:
        return await get_user(
            session,
            telegram_id,
        )


def progress_bar(
    current: float,
    target: float,
    length: int = 10,
) -> str:
    if target <= 0:
        return "░" * length

    ratio = min(
        max(current / target, 0),
        1,
    )

    filled = round(
        ratio * length
    )

    return (
        "█" * filled
        + "░" * (length - filled)
    )


def water_target_ml(
    weight_kg: float | None,
) -> int:
    if weight_kg is None:
        return 2000

    target = round(
        weight_kg * 30
    )

    return max(
        1800,
        min(target, 3500),
    )


@router.message(
    F.text.in_({
        "💧 Sog‘lom odatlar",
        "💧 Полезные привычки",
    })
)
async def habits_section(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()

    user = await load_user(
        message.from_user.id,
    )

    if user is None:
        await message.answer(
            "Profil topilmadi. / Профиль не найден."
        )
        return

    language = user.language or "uz"

    async with SessionFactory() as session:
        summary = await get_today_summary(
            session,
            user.id,
        )

    current_water = int(
        summary["water_ml"]
    )

    target_water = water_target_ml(
        user.current_weight_kg
    )

    water_percent = min(
        round(
            current_water
            / target_water
            * 100
        ),
        100,
    )

    bar = progress_bar(
        current_water,
        target_water,
    )

    if language == "ru":
        title = "💧 ПОЛЕЗНЫЕ ПРИВЫЧКИ"

        body = (
            "Отслеживайте воду, шаги и сон.\n\n"
            f"💧 Вода сегодня:\n"
            f"<b>{current_water} / {target_water} мл</b>\n"
            f"{bar} {water_percent}%\n\n"
            "Выберите действие."
        )
    else:
        title = "💧 SOG‘LOM ODATLAR"

        body = (
            "Suv, qadam va uyqu natijalarini kuzating.\n\n"
            f"💧 Bugungi suv:\n"
            f"<b>{current_water} / {target_water} ml</b>\n"
            f"{bar} {water_percent}%\n\n"
            "Kerakli amalni tanlang."
        )

    await message.answer(
        card(
            title,
            body,
        ),
        reply_markup=habits_menu(
            language
        ),
    )


@router.callback_query(
    F.data.in_({
        "habit:water:250",
        "habit:water:500",
    })
)
async def add_quick_water(
    callback: CallbackQuery,
) -> None:
    user = await load_user(
        callback.from_user.id,
    )

    if user is None:
        await callback.answer(
            "Profil topilmadi.",
            show_alert=True,
        )
        return

    language = user.language or "uz"

    try:
        amount = int(
            callback.data.rsplit(
                ":",
                1,
            )[1]
        )
    except (TypeError, ValueError):
        await callback.answer(
            "Noto‘g‘ri miqdor.",
            show_alert=True,
        )
        return

    async with SessionFactory() as session:
        await add_water(
            session=session,
            user_id=user.id,
            amount=amount,
        )

        summary = await get_today_summary(
            session,
            user.id,
        )

    current_water = int(
        summary["water_ml"]
    )

    target_water = water_target_ml(
        user.current_weight_kg
    )

    water_percent = min(
        round(
            current_water
            / target_water
            * 100
        ),
        100,
    )

    bar = progress_bar(
        current_water,
        target_water,
    )

    if language == "ru":
        title = "✅ ВОДА ДОБАВЛЕНА"

        body = (
            f"Добавлено: <b>{amount} мл</b>\n\n"
            f"💧 Сегодня:\n"
            f"<b>{current_water} / {target_water} мл</b>\n"
            f"{bar} {water_percent}%"
        )
    else:
        title = "✅ SUV QO‘SHILDI"

        body = (
            f"Qo‘shildi: <b>{amount} ml</b>\n\n"
            f"💧 Bugun:\n"
            f"<b>{current_water} / {target_water} ml</b>\n"
            f"{bar} {water_percent}%"
        )

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=habits_menu(
            language
        ),
    )

    await callback.answer(
        (
            f"{amount} ml suv qo‘shildi ✅"
            if language == "uz"
            else
            f"{amount} мл воды добавлено ✅"
        )
    )


@router.callback_query(
    F.data == "habit:water:custom"
)
async def start_custom_water(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    user = await load_user(
        callback.from_user.id,
    )

    if user is None:
        await callback.answer(
            "Profil topilmadi.",
            show_alert=True,
        )
        return

    language = user.language or "uz"

    await state.clear()
    await state.set_state(
        HabitInput.water
    )

    await callback.message.answer(
        (
            "💧 Ichgan suv miqdorini millilitrda kiriting.\n\n"
            "Masalan: <b>350</b>"
            if language == "uz"
            else
            "💧 Введите количество воды в миллилитрах.\n\n"
            "Например: <b>350</b>"
        )
    )

    await callback.answer()


@router.message(
    HabitInput.water
)
async def save_custom_water(
    message: Message,
    state: FSMContext,
) -> None:
    user = await load_user(
        message.from_user.id,
    )

    if user is None:
        await state.clear()

        await message.answer(
            "Profil topilmadi. / Профиль не найден."
        )
        return

    language = user.language or "uz"

    try:
        amount = int(
            (message.text or "").strip()
        )

        if not 50 <= amount <= 3000:
            raise ValueError

    except (TypeError, ValueError):
        await message.answer(
            (
                "Suv miqdorini 50–3000 ml oralig‘ida kiriting."
                if language == "uz"
                else
                "Введите количество воды от 50 до 3000 мл."
            )
        )
        return

    async with SessionFactory() as session:
        await add_water(
            session=session,
            user_id=user.id,
            amount=amount,
        )

        summary = await get_today_summary(
            session,
            user.id,
        )

    await state.clear()

    current_water = int(
        summary["water_ml"]
    )

    target_water = water_target_ml(
        user.current_weight_kg
    )

    water_percent = min(
        round(
            current_water
            / target_water
            * 100
        ),
        100,
    )

    bar = progress_bar(
        current_water,
        target_water,
    )

    if language == "ru":
        title = "✅ ВОДА СОХРАНЕНА"

        body = (
            f"Добавлено: <b>{amount} мл</b>\n\n"
            f"💧 Сегодня:\n"
            f"<b>{current_water} / {target_water} мл</b>\n"
            f"{bar} {water_percent}%"
        )
    else:
        title = "✅ SUV SAQLANDI"

        body = (
            f"Qo‘shildi: <b>{amount} ml</b>\n\n"
            f"💧 Bugun:\n"
            f"<b>{current_water} / {target_water} ml</b>\n"
            f"{bar} {water_percent}%"
        )

    await message.answer(
        card(
            title,
            body,
        ),
        reply_markup=habits_menu(
            language
        ),
    )
from app.database.crud import (
    add_sleep,
    add_steps,
)


@router.callback_query(
    F.data == "habit:steps"
)
async def start_steps_input(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    user = await load_user(
        callback.from_user.id,
    )

    if user is None:
        await callback.answer(
            "Profil topilmadi.",
            show_alert=True,
        )
        return

    language = user.language or "uz"

    await state.clear()
    await state.set_state(
        HabitInput.steps
    )

    await callback.message.answer(
        (
            "👣 Bugungi qadamlar sonini kiriting.\n\n"
            "Masalan: <b>6500</b>"
            if language == "uz"
            else
            "👣 Введите количество шагов за сегодня.\n\n"
            "Например: <b>6500</b>"
        )
    )

    await callback.answer()


@router.message(
    HabitInput.steps
)
async def save_steps(
    message: Message,
    state: FSMContext,
) -> None:
    user = await load_user(
        message.from_user.id,
    )

    if user is None:
        await state.clear()
        await message.answer(
            "Profil topilmadi. / Профиль не найден."
        )
        return

    language = user.language or "uz"

    try:
        steps = int(
            (message.text or "").strip()
        )

        if not 0 <= steps <= 100000:
            raise ValueError

    except (TypeError, ValueError):
        await message.answer(
            (
                "Qadamlar sonini 0–100000 oralig‘ida kiriting."
                if language == "uz"
                else
                "Введите число шагов от 0 до 100000."
            )
        )
        return

    async with SessionFactory() as session:
        await add_steps(
            session=session,
            user_id=user.id,
            steps=steps,
        )

    await state.clear()

    await message.answer(
        card(
            (
                "✅ QADAMLAR SAQLANDI"
                if language == "uz"
                else "✅ ШАГИ СОХРАНЕНЫ"
            ),
            (
                f"👣 Bugungi qadamlar: <b>{steps}</b>"
                if language == "uz"
                else
                f"👣 Шаги за сегодня: <b>{steps}</b>"
            ),
        ),
        reply_markup=habits_menu(
            language
        ),
    )


@router.callback_query(
    F.data == "habit:sleep"
)
async def start_sleep_input(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    user = await load_user(
        callback.from_user.id,
    )

    if user is None:
        await callback.answer(
            "Profil topilmadi.",
            show_alert=True,
        )
        return

    language = user.language or "uz"

    await state.clear()
    await state.set_state(
        HabitInput.sleep
    )

    await callback.message.answer(
        (
            "🌙 Necha soat uxlaganingizni kiriting.\n\n"
            "Masalan: <b>7.5</b>"
            if language == "uz"
            else
            "🌙 Введите количество часов сна.\n\n"
            "Например: <b>7.5</b>"
        )
    )

    await callback.answer()


@router.message(
    HabitInput.sleep
)
async def save_sleep(
    message: Message,
    state: FSMContext,
) -> None:
    user = await load_user(
        message.from_user.id,
    )

    if user is None:
        await state.clear()
        await message.answer(
            "Profil topilmadi. / Профиль не найден."
        )
        return

    language = user.language or "uz"

    try:
        hours = float(
            (message.text or "")
            .strip()
            .replace(",", ".")
        )

        if not 0 <= hours <= 24:
            raise ValueError

    except (TypeError, ValueError):
        await message.answer(
            (
                "Uyqu vaqtini 0–24 soat oralig‘ida kiriting."
                if language == "uz"
                else
                "Введите время сна от 0 до 24 часов."
            )
        )
        return

    async with SessionFactory() as session:
        await add_sleep(
            session=session,
            user_id=user.id,
            hours=hours,
        )

    await state.clear()

    await message.answer(
        card(
            (
                "✅ UYQU SAQLANDI"
                if language == "uz"
                else "✅ СОН СОХРАНЁН"
            ),
            (
                f"🌙 Bugungi uyqu: <b>{hours:g} soat</b>"
                if language == "uz"
                else
                f"🌙 Сон сегодня: <b>{hours:g} часов</b>"
            ),
        ),
        reply_markup=habits_menu(
            language
        ),
    )


@router.callback_query(
    F.data == "habit:today"
)
async def show_today_habits(
    callback: CallbackQuery,
) -> None:
    user = await load_user(
        callback.from_user.id,
    )

    if user is None:
        await callback.answer(
            "Profil topilmadi.",
            show_alert=True,
        )
        return

    language = user.language or "uz"

    async with SessionFactory() as session:
        summary = await get_today_summary(
            session,
            user.id,
        )

    water = int(
        summary["water_ml"]
    )
    steps = int(
        summary["steps"]
    )
    sleep = float(
        summary["sleep_hours"]
    )
    exercise = int(
        summary["exercise_minutes"]
    )

    target_water = water_target_ml(
        user.current_weight_kg
    )

    water_percent = min(
        round(
            water / target_water * 100
        ),
        100,
    )

    steps_percent = min(
        round(
            steps / 10000 * 100
        ),
        100,
    )

    sleep_percent = min(
        round(
            sleep / 8 * 100
        ),
        100,
    )

    daily_score = round(
        (
            water_percent
            + steps_percent
            + sleep_percent
        )
        / 3
    )

    if language == "ru":
        title = "📊 ОТЧЁТ ЗА СЕГОДНЯ"

        body = (
            f"💧 Вода: <b>{water} / {target_water} мл</b>\n"
            f"👣 Шаги: <b>{steps} / 10000</b>\n"
            f"🌙 Сон: <b>{sleep:g} / 8 часов</b>\n"
            f"💪 Упражнения: <b>{exercise} минут</b>\n\n"
            f"⭐ Результат дня: <b>{daily_score}%</b>"
        )
    else:
        title = "📊 BUGUNGI HISOBOT"

        body = (
            f"💧 Suv: <b>{water} / {target_water} ml</b>\n"
            f"👣 Qadam: <b>{steps} / 10000</b>\n"
            f"🌙 Uyqu: <b>{sleep:g} / 8 soat</b>\n"
            f"💪 Mashq: <b>{exercise} daqiqa</b>\n\n"
            f"⭐ Kunlik natija: <b>{daily_score}%</b>"
        )

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=habits_menu(
            language
        ),
    )

    await callback.answer()

