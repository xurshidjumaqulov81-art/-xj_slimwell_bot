from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import get_settings
from app.content import TRANSLATIONS
from app.database.crud import (
    add_weight,
    create_user,
    get_user,
    get_user_by_personal_id,
    update_user,
)
from app.database.db import SessionFactory
from app.keyboards import (
    activity_menu,
    gender_menu,
    goal_menu,
    language_menu,
    main_menu,
)
from app.states import Onboarding


router = Router()
settings = get_settings()


def card(title: str, body: str) -> str:
    return (
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>{title}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{body}"
    )


@router.message(CommandStart())
async def start_command(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()

    async with SessionFactory() as session:
        user = await get_user(
            session,
            message.from_user.id,
        )

    if user and user.personal_id and user.name:
        language = user.language or "uz"
        text = TRANSLATIONS[language]

        await message.answer(
            card(
                "✨ XJ SLIMWELL",
                (
                    f"{text['welcome']}\n\n"
                    f"👤 <b>{user.name}</b>\n"
                    f"🆔 <b>{user.personal_id}</b>\n\n"
                    f"{text['main_menu_prompt']}"
                ),
            ),
            reply_markup=main_menu(
                language,
                message.from_user.id in settings.admins,
            ),
        )
        return

    await state.set_state(Onboarding.language)

    await message.answer(
        card(
            "✨ XJ SLIMWELL",
            (
                "Xush kelibsiz! / Добро пожаловать!\n\n"
                "Davom etish uchun tilni tanlang.\n"
                "Выберите язык, чтобы продолжить."
            ),
        ),
        reply_markup=language_menu(),
    )


@router.callback_query(
    Onboarding.language,
    F.data.startswith("lang:"),
)
async def choose_language(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    language = callback.data.split(":", 1)[1]

    if language not in TRANSLATIONS:
        await callback.answer(
            "Til topilmadi / Язык не найден",
            show_alert=True,
        )
        return

    async with SessionFactory() as session:
        user = await get_user(
            session,
            callback.from_user.id,
        )

        if user is None:
            await create_user(
                session,
                telegram_id=callback.from_user.id,
                username=callback.from_user.username,
                language=language,
            )
        else:
            await update_user(
                session,
                callback.from_user.id,
                language=language,
                username=callback.from_user.username,
            )

    await state.update_data(language=language)
    await state.set_state(Onboarding.personal_id)

    await callback.message.edit_text(
        card(
            "🆔 ID",
            TRANSLATIONS[language]["enter_personal_id"],
        )
    )

    await callback.answer()


@router.message(Onboarding.personal_id)
async def enter_personal_id(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    text = TRANSLATIONS[language]

    personal_id = (message.text or "").strip()

    if not (
        personal_id.isdigit()
        and len(personal_id) == 7
    ):
        await message.answer(
            text["invalid_personal_id"],
        )
        return

    async with SessionFactory() as session:
        existing_user = await get_user_by_personal_id(
            session,
            personal_id,
        )

    if (
        existing_user is not None
        and existing_user.telegram_id != message.from_user.id
    ):
        await message.answer(
            text["personal_id_exists"],
        )
        return

    await state.update_data(
        personal_id=personal_id,
    )
    await state.set_state(Onboarding.name)

    await message.answer(
        text["enter_name"],
    )


@router.message(Onboarding.name)
async def enter_name(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    text = TRANSLATIONS[language]

    name = (message.text or "").strip()

    if not 2 <= len(name) <= 50:
        await message.answer(
            text["invalid_name"],
        )
        return

    await state.update_data(name=name)
    await state.set_state(Onboarding.age)

    await message.answer(
        text["enter_age"],
    )


@router.message(Onboarding.age)
async def enter_age(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    text = TRANSLATIONS[language]

    try:
        age = int(message.text or "")

        if not 13 <= age <= 100:
            raise ValueError
    except (TypeError, ValueError):
        await message.answer(
            text["invalid_age"],
        )
        return

    await state.update_data(age=age)
    await state.set_state(Onboarding.gender)

    await message.answer(
        text["choose_gender"],
        reply_markup=gender_menu(language),
    )


@router.callback_query(
    Onboarding.gender,
    F.data.startswith("gender:"),
)
async def choose_gender(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    text = TRANSLATIONS[language]

    gender = callback.data.split(":", 1)[1]

    if gender not in {"male", "female"}:
        await callback.answer(
            "Noto‘g‘ri tanlov / Неверный выбор",
            show_alert=True,
        )
        return

    await state.update_data(gender=gender)
    await state.set_state(Onboarding.height)

    await callback.message.edit_text(
        text["enter_height"],
    )

    await callback.answer()


@router.message(Onboarding.height)
async def enter_height(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    text = TRANSLATIONS[language]

    try:
        height = float(
            (message.text or "").replace(",", ".")
        )

        if not 120 <= height <= 230:
            raise ValueError
    except (TypeError, ValueError):
        await message.answer(
            text["invalid_height"],
        )
        return

    await state.update_data(height=height)
    await state.set_state(Onboarding.weight)

    await message.answer(
        text["enter_weight"],
    )


@router.message(Onboarding.weight)
async def enter_weight(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    text = TRANSLATIONS[language]

    try:
        weight = float(
            (message.text or "").replace(",", ".")
        )

        if not 30 <= weight <= 300:
            raise ValueError
    except (TypeError, ValueError):
        await message.answer(
            text["invalid_weight"],
        )
        return

    await state.update_data(weight=weight)
    await state.set_state(Onboarding.goal)

    await message.answer(
        text["choose_goal"],
        reply_markup=goal_menu(language),
    )


@router.callback_query(
    Onboarding.goal,
    F.data.startswith("goal:"),
)
async def choose_goal(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    text = TRANSLATIONS[language]

    goal = callback.data.split(":", 1)[1]

    if goal not in {"maintain", "lose", "habits"}:
        await callback.answer(
            "Noto‘g‘ri tanlov / Неверный выбор",
            show_alert=True,
        )
        return

    await state.update_data(goal=goal)
    await state.set_state(Onboarding.activity)

    await callback.message.edit_text(
        text["choose_activity"],
        reply_markup=activity_menu(language),
    )

    await callback.answer()


@router.callback_query(
    Onboarding.activity,
    F.data.startswith("activity:"),
)
async def choose_activity(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    language = data.get("language", "uz")
    text = TRANSLATIONS[language]

    activity = callback.data.split(":", 1)[1]

    if activity not in {
        "low",
        "light",
        "medium",
        "high",
    }:
        await callback.answer(
            "Noto‘g‘ri tanlov / Неверный выбор",
            show_alert=True,
        )
        return

    async with SessionFactory() as session:
        user = await get_user(
            session,
            callback.from_user.id,
        )

        if user is None:
            user = await create_user(
                session,
                telegram_id=callback.from_user.id,
                username=callback.from_user.username,
                language=language,
            )

        await update_user(
            session,
            callback.from_user.id,
            personal_id=data["personal_id"],
            username=callback.from_user.username,
            language=language,
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            height_cm=data["height"],
            current_weight_kg=data["weight"],
            goal=data["goal"],
            activity=activity,
            accepted_terms=True,
        )

        user = await get_user(
            session,
            callback.from_user.id,
        )

        await add_weight(
            session,
            user.id,
            data["weight"],
        )

    await state.clear()

    await callback.message.edit_text(
        card(
            "✅ XJ SLIMWELL",
            (
                f"{text['profile_ready']}\n\n"
                f"🆔 <b>{data['personal_id']}</b>\n"
                f"👤 <b>{data['name']}</b>\n"
                f"📏 <b>{data['height']:g} sm</b>\n"
                f"⚖️ <b>{data['weight']:g} kg</b>"
            ),
        )
    )

    await callback.message.answer(
        text["main_menu_prompt"],
        reply_markup=main_menu(
            language,
            callback.from_user.id in settings.admins,
        ),
    )

    await callback.answer()

