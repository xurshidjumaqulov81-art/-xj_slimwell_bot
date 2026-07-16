from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    Message,
)

from app.config import ASSETS_DIR
from app.database.crud import get_user
from app.database.db import SessionFactory
from app.keyboards import body_menu
from app.services.health import (
    calculate_remaining_weight,
    get_bmi_plan,
    get_calorie_text,
)
from app.services.visuals import create_bmi_card


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


def get_body_image(
    gender: str | None,
) -> Path | None:
    if gender == "female":
        possible_paths = [
            ASSETS_DIR / "body" / "female.png",
            ASSETS_DIR / "body" / "body_female.png",
            ASSETS_DIR / "body_female.png",
        ]
    else:
        possible_paths = [
            ASSETS_DIR / "body" / "male.png",
            ASSETS_DIR / "body" / "body_male.png",
            ASSETS_DIR / "body_male.png",
        ]

    for path in possible_paths:
        if path.exists() and path.is_file():
            return path

    return None


async def load_user(
    telegram_id: int,
):
    async with SessionFactory() as session:
        return await get_user(
            session,
            telegram_id,
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

    user = await load_user(
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
        title = "📊 АНАЛИЗ ТЕЛА"

        body = (
            f"👤 <b>{user.name}</b>\n"
            f"⚧ Пол: "
            f"<b>{get_gender_text(user.gender, language)}</b>\n"
            f"📏 Рост: <b>{user.height_cm:g} см</b>\n"
            f"⚖️ Вес: "
            f"<b>{user.current_weight_kg:g} кг</b>\n\n"
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Категория: "
            f"<b>{plan['title']}</b>\n\n"
            "Выберите нужный показатель."
        )
    else:
        title = "📊 TANA TAHLILI"

        body = (
            f"👤 <b>{user.name}</b>\n"
            f"⚧ Jins: "
            f"<b>{get_gender_text(user.gender, language)}</b>\n"
            f"📏 Bo‘y: <b>{user.height_cm:g} sm</b>\n"
            f"⚖️ Vazn: "
            f"<b>{user.current_weight_kg:g} kg</b>\n\n"
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Holat: "
            f"<b>{plan['title']}</b>\n\n"
            "Kerakli ko‘rsatkichni tanlang."
        )

    body_image = get_body_image(
        user.gender,
    )

    if body_image is not None:
        await message.answer_photo(
            photo=FSInputFile(body_image),
            caption=card(
                title,
                body,
            ),
            reply_markup=body_menu(language),
        )
    else:
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
        metrics, plan = get_bmi_plan(
            user,
            language,
        )
    except ValueError:
        await callback.answer(
            (
                "Profil ma’lumotlari to‘liq emas."
                if language == "uz"
                else
                "Данные профиля заполнены не полностью."
            ),
            show_alert=True,
        )
        return

    remaining_weight = calculate_remaining_weight(
        user,
        metrics,
    )

    try:
        bmi_image = create_bmi_card(
            bmi=metrics.bmi,
            category_key=metrics.category_key,
            normal_min_weight=(
                metrics.normal_min_weight
            ),
            normal_max_weight=(
                metrics.normal_max_weight
            ),
            ideal_weight=(
                metrics.ideal_weight
            ),
            remaining_weight=remaining_weight,
            language=language,
        )
    except Exception:
        bmi_image = None

    if language == "ru":
        title = "📊 РЕЗУЛЬТАТ BMI"

        body = (
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Категория: "
            f"<b>{plan['title']}</b>\n\n"
            f"✅ <b>{metrics.normal_min_weight}–"
            f"{metrics.normal_max_weight} кг</b> — "
            "диапазон нормального веса\n\n"
            f"⭐ Идеальный вес: "
            f"<b>{metrics.ideal_weight} кг</b>"
        )

        if remaining_weight > 0:
            body += (
                "\n\n"
                "🎯 Для достижения здорового веса:\n\n"
                f"Вам необходимо сбросить ещё "
                f"<b>{remaining_weight} кг</b>."
            )
        else:
            body += (
                "\n\n"
                "💚 Ваш вес находится "
                "в здоровом диапазоне."
            )
    else:
        title = "📊 BMI NATIJASI"

        body = (
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Holat: "
            f"<b>{plan['title']}</b>\n\n"
            f"✅ <b>{metrics.normal_min_weight}–"
            f"{metrics.normal_max_weight} kg</b> — "
            "norma vazn oralig‘i\n\n"
            f"⭐ Ideal vazn: "
            f"<b>{metrics.ideal_weight} kg</b>"
        )

        if remaining_weight > 0:
            body += (
                "\n\n"
                "🎯 Sog‘lom vaznga erishish uchun:\n\n"
                f"Siz yana <b>{remaining_weight} kg</b> "
                "vazn tashlashingiz kerak."
            )
        else:
            body += (
                "\n\n"
                "💚 Vazningiz sog‘lom oraliqda."
            )

    if bmi_image is not None:
        await callback.message.answer_photo(
            photo=FSInputFile(bmi_image),
            caption=card(
                title,
                body,
            ),
            reply_markup=body_menu(language),
        )
    else:
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
        metrics, _ = get_bmi_plan(
            user,
            language,
        )
    except ValueError:
        await callback.answer(
            (
                "Profil ma’lumotlari to‘liq emas."
                if language == "uz"
                else
                "Данные профиля заполнены не полностью."
            ),
            show_alert=True,
        )
        return

    if language == "ru":
        title = "⚡ ДНЕВНАЯ ЭНЕРГИЯ"

        body = (
            "🔥 Основной расход энергии организма:\n"
            f"<b>{metrics.bmr} ккал</b>\n\n"
            "⚖️ Для поддержания текущего веса:\n"
            f"<b>{metrics.maintenance_kcal} ккал</b>\n\n"
            f"{get_calorie_text(metrics, language)}"
        )
    else:
        title = "⚡ KUNLIK ENERGIYA"

        body = (
            "🔥 Tananing asosiy energiya sarfi:\n"
            f"<b>{metrics.bmr} kkal</b>\n\n"
            "⚖️ Hozirgi vaznni saqlash uchun:\n"
            f"<b>{metrics.maintenance_kcal} kkal</b>\n\n"
            f"{get_calorie_text(metrics, language)}"
        )

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
        metrics, _ = get_bmi_plan(
            user,
            language,
        )
    except ValueError:
        await callback.answer(
            (
                "Profil ma’lumotlari to‘liq emas."
                if language == "uz"
                else
                "Данные профиля заполнены не полностью."
            ),
            show_alert=True,
        )
        return

    remaining_weight = calculate_remaining_weight(
        user,
        metrics,
    )

    if language == "ru":
        title = "🎯 НОРМА И ИДЕАЛЬНЫЙ ВЕС"

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
                "🎯 Для достижения здорового веса:\n\n"
                f"Вам необходимо сбросить ещё "
                f"<b>{remaining_weight} кг</b>."
            )
    else:
        title = "🎯 NORMA VA IDEAL VAZN"

        body = (
            f"📏 Bo‘yingiz: "
            f"<b>{user.height_cm:g} sm</b>\n"
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
                "🎯 Sog‘lom vaznga erishish uchun:\n\n"
                f"Siz yana <b>{remaining_weight} kg</b> "
                "vazn tashlashingiz kerak."
            )

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
        metrics, plan = get_bmi_plan(
            user,
            language,
        )
    except ValueError:
        await callback.answer(
            (
                "Profil ma’lumotlari to‘liq emas."
                if language == "uz"
                else
                "Данные профиля заполнены не полностью."
            ),
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
        title = "🧍 ПОЛНЫЙ АНАЛИЗ ТЕЛА"

        body = (
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Категория: "
            f"<b>{plan['title']}</b>\n\n"
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
                "🎯 Для достижения здорового веса:\n\n"
                f"Вам необходимо сбросить ещё "
                f"<b>{remaining_weight} кг</b>."
            )

        body += (
            "\n\n"
            "🌿 Продолжайте — каждый шаг "
            "приближает вас к цели."
        )
    else:
        title = "🧍 TO‘LIQ TANA TAHLILI"

        body = (
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Holat: "
            f"<b>{plan['title']}</b>\n\n"
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
                "🎯 Sog‘lom vaznga erishish uchun:\n\n"
                f"Siz yana <b>{remaining_weight} kg</b> "
                "vazn tashlashingiz kerak."
            )

        body += (
            "\n\n"
            "🌿 Siz to‘g‘ri yo‘ldasiz. "
            "Har bir kichik qadam natijaga olib keladi."
        )

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=body_menu(language),
    )

    await callback.answer()
