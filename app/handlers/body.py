from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.crud import get_user
from app.database.db import SessionFactory
from app.keyboards import body_menu
from app.services.health import (
    calculate_remaining_weight,
    get_bmi_plan,
    get_calorie_text,
)


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


def get_gender_text(
    gender: str | None,
    language: str,
) -> str:
    if language == "ru":
        return (
            "Мужчина"
            if gender == "male"
            else "Женщина"
        )

    return (
        "Erkak"
        if gender == "male"
        else "Ayol"
    )


@router.message(
    F.text.in_({
        "📊 Tana tahlili",
        "📊 Анализ тела",
    })
)
async def body_section(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()

    async with SessionFactory() as session:
        user = await get_user(
            session,
            message.from_user.id,
        )

    if user is None:
        await message.answer(
            "Profil topilmadi. / Профиль не найден."
        )
        return

    language = user.language or "uz"

    try:
        metrics, plan = get_bmi_plan(
            user,
            language,
        )
    except ValueError:
        await message.answer(
            (
                "Profil ma’lumotlari to‘liq emas."
                if language == "uz"
                else
                "Данные профиля заполнены не полностью."
            )
        )
        return

    if language == "ru":
        body = (
            f"👤 <b>{user.name}</b>\n"
            f"⚧ {get_gender_text(user.gender, language)}\n"
            f"📏 Рост: <b>{user.height_cm:g} см</b>\n"
            f"⚖️ Вес: <b>{user.current_weight_kg:g} кг</b>\n\n"
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Категория: <b>{plan['title']}</b>\n\n"
            "Выберите нужный показатель."
        )

        title = "📊 АНАЛИЗ ТЕЛА"
    else:
        body = (
            f"👤 <b>{user.name}</b>\n"
            f"⚧ {get_gender_text(user.gender, language)}\n"
            f"📏 Bo‘y: <b>{user.height_cm:g} sm</b>\n"
            f"⚖️ Vazn: <b>{user.current_weight_kg:g} kg</b>\n\n"
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Holat: <b>{plan['title']}</b>\n\n"
            "Kerakli ko‘rsatkichni tanlang."
        )

        title = "📊 TANA TAHLILI"

    await message.answer(
        card(
            title,
            body,
        ),
        reply_markup=body_menu(language),
    )


@router.callback_query(
    F.data == "body:bmi"
)
async def show_bmi(
    callback: CallbackQuery,
) -> None:
    async with SessionFactory() as session:
        user = await get_user(
            session,
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
        metrics, plan = get_bmi_plan(
            user,
            language,
        )
    except ValueError:
        await callback.answer(
            "Profil ma’lumotlari to‘liq emas.",
            show_alert=True,
        )
        return

    if language == "ru":
        body = (
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n\n"
            f"🎯 Категория:\n"
            f"<b>{plan['title']}</b>\n\n"
            "🌿 Каждый шаг приближает вас к результату."
        )

        title = "📊 РЕЗУЛЬТАТ BMI"
    else:
        body = (
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n\n"
            f"🎯 Holat:\n"
            f"<b>{plan['title']}</b>\n\n"
            "🌿 Har bir kichik qadam natijaga olib keladi."
        )

        title = "📊 BMI NATIJASI"

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=body_menu(language),
    )

    await callback.answer()


@router.callback_query(
    F.data == "body:calories"
)
async def show_calories(
    callback: CallbackQuery,
) -> None:
    async with SessionFactory() as session:
        user = await get_user(
            session,
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
        metrics, _ = get_bmi_plan(
            user,
            language,
        )
    except ValueError:
        await callback.answer(
            "Profil ma’lumotlari to‘liq emas.",
            show_alert=True,
        )
        return

    if language == "ru":
        body = (
            f"🧍 Базовый обмен: "
            f"<b>{metrics.bmr} ккал</b>\n"
            f"⚖️ Поддержание веса: "
            f"<b>{metrics.maintenance_kcal} ккал</b>\n\n"
            f"{get_calorie_text(metrics, language)}"
        )

        title = "⚡ ДНЕВНАЯ ЭНЕРГИЯ"
    else:
        body = (
            f"🧍 Bazal almashinuv: "
            f"<b>{metrics.bmr} kkal</b>\n"
            f"⚖️ Vaznni saqlash: "
            f"<b>{metrics.maintenance_kcal} kkal</b>\n\n"
            f"{get_calorie_text(metrics, language)}"
        )

        title = "⚡ KUNLIK ENERGIYA"

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=body_menu(language),
    )

    await callback.answer()


@router.callback_query(
    F.data == "body:range"
)
async def show_weight_range(
    callback: CallbackQuery,
) -> None:
    async with SessionFactory() as session:
        user = await get_user(
            session,
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
        metrics, _ = get_bmi_plan(
            user,
            language,
        )
    except ValueError:
        await callback.answer(
            "Profil ma’lumotlari to‘liq emas.",
            show_alert=True,
        )
        return

    remaining_weight = calculate_remaining_weight(
        user,
        metrics,
    )

    if language == "ru":
        body = (
            f"📏 Рост: <b>{user.height_cm:g} см</b>\n"
            f"⚖️ Текущий вес: "
            f"<b>{user.current_weight_kg:g} кг</b>\n\n"
            f"✅ <b>{metrics.normal_min_weight}–"
            f"{metrics.normal_max_weight} кг</b> — "
            "диапазон нормального веса\n\n"
            f"⭐ <b>{metrics.ideal_weight} кг</b> — "
            "идеальный вес"
        )

        if remaining_weight > 0:
            body += (
                "\n\n"
                f"🎯 До верхней границы нормы:\n"
                f"<b>{remaining_weight} кг</b>"
            )

        title = "🎯 НОРМА И ИДЕАЛЬНЫЙ ВЕС"
    else:
        body = (
            f"📏 Bo‘yingiz: <b>{user.height_cm:g} sm</b>\n"
            f"⚖️ Hozirgi vazningiz: "
            f"<b>{user.current_weight_kg:g} kg</b>\n\n"
            f"✅ <b>{metrics.normal_min_weight}–"
            f"{metrics.normal_max_weight} kg</b> — "
            "norma vazn oralig‘i\n\n"
            f"⭐ <b>{metrics.ideal_weight} kg</b> — "
            "ideal vazn"
        )

        if remaining_weight > 0:
            body += (
                "\n\n"
                f"🎯 Norma oralig‘ining yuqori "
                f"chegarasigacha:\n"
                f"<b>{remaining_weight} kg</b>"
            )

        title = "🎯 NORMA VA IDEAL VAZN"

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=body_menu(language),
    )

    await callback.answer()


@router.callback_query(
    F.data == "body:full"
)
async def show_full_analysis(
    callback: CallbackQuery,
) -> None:
    async with SessionFactory() as session:
        user = await get_user(
            session,
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
        metrics, plan = get_bmi_plan(
            user,
            language,
        )
    except ValueError:
        await callback.answer(
            "Profil ma’lumotlari to‘liq emas.",
            show_alert=True,
        )
        return

    remaining_weight = calculate_remaining_weight(
        user,
        metrics,
    )

    calorie_value = (
        metrics.target_kcal
        if metrics.target_kcal is not None
        else metrics.maintenance_kcal
    )

    if language == "ru":
        body = (
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Категория: <b>{plan['title']}</b>\n\n"
            f"✅ {metrics.normal_min_weight}–"
            f"{metrics.normal_max_weight} кг — "
            "диапазон нормы\n"
            f"⭐ {metrics.ideal_weight} кг — "
            "идеальный вес\n"
            f"⚡ {calorie_value} ккал — "
            "дневная цель\n"
            f"💧 Вода: {plan['water']}\n"
            f"👣 Шаги: {plan['steps']}\n"
            f"🌙 Сон: {plan['sleep']}"
        )

        if remaining_weight > 0:
            body += (
                "\n\n"
                f"🎯 До верхней границы нормы: "
                f"<b>{remaining_weight} кг</b>"
            )

        body += (
            "\n\n"
            "🌿 Продолжайте — каждый шаг "
            "приближает вас к цели."
        )

        title = "🧍 ПОЛНЫЙ АНАЛИЗ ТЕЛА"
    else:
        body = (
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Holat: <b>{plan['title']}</b>\n\n"
            f"✅ {metrics.normal_min_weight}–"
            f"{metrics.normal_max_weight} kg — "
            "norma vazn oralig‘i\n"
            f"⭐ {metrics.ideal_weight} kg — "
            "ideal vazn\n"
            f"⚡ {calorie_value} kkal — "
            "kunlik maqsad\n"
            f"💧 Suv: {plan['water']}\n"
            f"👣 Qadamlar: {plan['steps']}\n"
            f"🌙 Uyqu: {plan['sleep']}"
        )

        if remaining_weight > 0:
            body += (
                "\n\n"
                f"🎯 Norma chegarasigacha: "
                f"<b>{remaining_weight} kg</b>"
            )

        body += (
            "\n\n"
            "🌿 Siz to‘g‘ri yo‘ldasiz. "
            "Har bir kichik qadam natijaga olib keladi."
        )

        title = "🧍 TO‘LIQ TANA TAHLILI"

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=body_menu(language),
    )

    await callback.answer()
