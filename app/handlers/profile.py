from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.content import TRANSLATIONS
from app.database.crud import (
    add_weight,
    get_user,
    update_user,
)
from app.database.db import SessionFactory
from app.keyboards import (
    goal_menu,
    main_menu,
    profile_menu,
)
from app.states import EditProfile


router = Router()


def card(title: str, body: str) -> str:
    return (
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>{title}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{body}"
    )


def gender_name(
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


def goal_name(
    goal: str | None,
    language: str,
) -> str:
    names = {
        "uz": {
            "maintain": "Vaznni saqlash",
            "lose": "Vaznni kamaytirish",
            "habits": "Sog‘lom odatlarni yaxshilash",
        },
        "ru": {
            "maintain": "Сохранить вес",
            "lose": "Снизить вес",
            "habits": "Улучшить привычки",
        },
    }

    return names[language].get(
        goal or "",
        "—",
    )


@router.message(
    F.text.in_({
        "👤 Mening profilim",
        "👤 Мой профиль",
    })
)
async def profile_section(
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

    title = (
        "👤 MENING PROFILIM"
        if language == "uz"
        else "👤 МОЙ ПРОФИЛЬ"
    )

    description = (
        "Profil ma’lumotlaringizni ko‘ring yoki yangilang."
        if language == "uz"
        else
        "Просматривайте и изменяйте данные профиля."
    )

    await message.answer(
        card(
            title,
            description,
        ),
        reply_markup=profile_menu(language),
    )


@router.callback_query(
    F.data == "profile:view"
)
async def view_profile(
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

    if language == "ru":
        body = (
            f"🆔 ID: <b>{user.personal_id}</b>\n"
            f"👤 Имя: <b>{user.name}</b>\n"
            f"🎂 Возраст: <b>{user.age}</b>\n"
            f"⚧ Пол: <b>{gender_name(user.gender, language)}</b>\n"
            f"📏 Рост: <b>{user.height_cm:g} см</b>\n"
            f"⚖️ Вес: <b>{user.current_weight_kg:g} кг</b>\n"
            f"🎯 Цель: <b>{goal_name(user.goal, language)}</b>"
        )

        title = "👤 МОЙ ПРОФИЛЬ"
    else:
        body = (
            f"🆔 ID: <b>{user.personal_id}</b>\n"
            f"👤 Ism: <b>{user.name}</b>\n"
            f"🎂 Yosh: <b>{user.age}</b>\n"
            f"⚧ Jins: <b>{gender_name(user.gender, language)}</b>\n"
            f"📏 Bo‘y: <b>{user.height_cm:g} sm</b>\n"
            f"⚖️ Vazn: <b>{user.current_weight_kg:g} kg</b>\n"
            f"🎯 Maqsad: <b>{goal_name(user.goal, language)}</b>"
        )

        title = "👤 MENING PROFILIM"

    await callback.message.edit_text(
        card(
            title,
            body,
        ),
        reply_markup=profile_menu(language),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("profile:edit:")
)
async def start_edit_profile(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    field = callback.data.split(":")[-1]

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

    await state.clear()
    await state.update_data(
        edit_field=field,
        language=language,
    )

    if field == "goal":
        await state.set_state(
            EditProfile.value
        )

        await callback.message.answer(
            (
                "Yangi maqsadni tanlang:"
                if language == "uz"
                else
                "Выберите новую цель:"
            ),
            reply_markup=goal_menu(language),
        )

        await callback.answer()
        return

    prompts = {
        "uz": {
            "name": "Yangi ismingizni kiriting:",
            "age": "Yangi yoshingizni kiriting:",
            "height_cm": (
                "Yangi bo‘yingizni santimetrda kiriting:"
            ),
            "weight": (
                "Yangi vazningizni kilogrammda kiriting:"
            ),
        },
        "ru": {
            "name": "Введите новое имя:",
            "age": "Введите новый возраст:",
            "height_cm": (
                "Введите новый рост в сантиметрах:"
            ),
            "weight": (
                "Введите новый вес в килограммах:"
            ),
        },
    }

    if field not in prompts[language]:
        await callback.answer(
            "Noto‘g‘ri tanlov.",
            show_alert=True,
        )
        return

    await state.set_state(
        EditProfile.value
    )

    await callback.message.answer(
        prompts[language][field],
    )

    await callback.answer()


@router.callback_query(
    EditProfile.value,
    F.data.startswith("goal:"),
)
async def save_new_goal(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    field = data.get("edit_field")

    if field != "goal":
        await callback.answer(
            "Noto‘g‘ri amal.",
            show_alert=True,
        )
        return

    goal = callback.data.split(":", 1)[1]

    if goal not in {
        "maintain",
        "lose",
        "habits",
    }:
        await callback.answer(
            "Noto‘g‘ri tanlov.",
            show_alert=True,
        )
        return

    async with SessionFactory() as session:
        await update_user(
            session,
            callback.from_user.id,
            goal=goal,
        )

    await state.clear()

    text = TRANSLATIONS[language]

    await callback.message.edit_text(
        card(
            "✅",
            (
                f"{text['saved']}\n\n"
                f"🎯 <b>{goal_name(goal, language)}</b>"
            ),
        ),
        reply_markup=profile_menu(language),
    )

    await callback.answer()


@router.message(
    EditProfile.value
)
async def save_profile_value(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()

    field = data.get("edit_field")
    language = data.get("language", "uz")

    raw_value = (
        message.text or ""
    ).strip()

    try:
        if field == "name":
            if not 2 <= len(raw_value) <= 50:
                raise ValueError

            update_values = {
                "name": raw_value,
            }

        elif field == "age":
            age = int(raw_value)

            if not 13 <= age <= 100:
                raise ValueError

            update_values = {
                "age": age,
            }

        elif field == "height_cm":
            height = float(
                raw_value.replace(",", ".")
            )

            if not 120 <= height <= 230:
                raise ValueError

            update_values = {
                "height_cm": height,
            }

        elif field == "weight":
            weight = float(
                raw_value.replace(",", ".")
            )

            if not 30 <= weight <= 300:
                raise ValueError

            update_values = {
                "current_weight_kg": weight,
            }

        else:
            raise ValueError

    except (TypeError, ValueError):
        error_text = (
            "Qiymat noto‘g‘ri. Qayta kiriting."
            if language == "uz"
            else
            "Неверное значение. Введите ещё раз."
        )

        await message.answer(
            error_text,
        )
        return

    async with SessionFactory() as session:
        user = await get_user(
            session,
            message.from_user.id,
        )

        if user is None:
            await state.clear()

            await message.answer(
                "Profil topilmadi. / Профиль не найден."
            )
            return

        await update_user(
            session,
            message.from_user.id,
            **update_values,
        )

        if field == "weight":
            await add_weight(
                session,
                user.id,
                update_values[
                    "current_weight_kg"
                ],
            )

    await state.clear()

    text = TRANSLATIONS[language]

    await message.answer(
        card(
            "✅",
            text["saved"],
        ),
        reply_markup=profile_menu(language),
    )


@router.callback_query(
    F.data == "home"
)
async def return_home(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.clear()

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

    await callback.message.answer(
        TRANSLATIONS[language][
            "main_menu_prompt"
        ],
        reply_markup=main_menu(language),
    )

    await callback.answer()

