from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from app.config import get_settings
from app.content import TRANSLATIONS
from app.database.crud import get_or_create_user, personal_id_exists, update_user, add_weight
from app.database.db import SessionFactory
from app.keyboards import language_menu, main_menu, gender_menu, goal_menu, activity_menu
from app.states import Onboarding
from app.utils.text import card

router = Router()
settings = get_settings()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    async with SessionFactory() as s:
        user = await get_or_create_user(s, message.from_user.id, message.from_user.username)
    if not user.personal_id:
        await state.set_state(Onboarding.language)
        await message.answer(
            card("✨ XJ SLIMWELL", "Xush kelibsiz! / Добро пожаловать!\n\nTilni tanlang / Выберите язык"),
            reply_markup=language_menu(),
        )
        return
    t = TRANSLATIONS[user.language]
    await message.answer(card("✨ XJ SLIMWELL", f"{t['welcome']}\n\n{t['main_prompt']}"),
                         reply_markup=main_menu(user.language, message.from_user.id in settings.admins))


@router.callback_query(Onboarding.language, F.data.startswith("lang:"))
async def set_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    async with SessionFactory() as s:
        user = await get_or_create_user(s, callback.from_user.id, callback.from_user.username)
        await update_user(s, user, language=lang)
    await state.update_data(language=lang)
    await state.set_state(Onboarding.personal_id)
    await callback.message.edit_text(card("🆔 ID", TRANSLATIONS[lang]["enter_id"]))
    await callback.answer()


@router.message(Onboarding.personal_id)
async def personal_id(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    value = (message.text or "").strip()
    if not (value.isdigit() and len(value) == 7):
        await message.answer(TRANSLATIONS[lang]["bad_id"])
        return
    async with SessionFactory() as s:
        if await personal_id_exists(s, value, message.from_user.id):
            await message.answer(TRANSLATIONS[lang]["used_id"])
            return
    await state.update_data(personal_id=value)
    await state.set_state(Onboarding.name)
    await message.answer(TRANSLATIONS[lang]["enter_name"])


@router.message(Onboarding.name)
async def name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    value = (message.text or "").strip()
    if not 2 <= len(value) <= 50:
        await message.answer("Ismni qayta kiriting." if lang=="uz" else "Введите имя ещё раз.")
        return
    await state.update_data(name=value)
    await state.set_state(Onboarding.age)
    await message.answer(TRANSLATIONS[lang]["enter_age"])


@router.message(Onboarding.age)
async def age(message: Message, state: FSMContext):
    data = await state.get_data(); lang = data["language"]
    try:
        value = int(message.text)
        if not 13 <= value <= 100: raise ValueError
    except Exception:
        await message.answer("13–100 oralig‘ida kiriting." if lang=="uz" else "Введите число от 13 до 100.")
        return
    await state.update_data(age=value)
    await state.set_state(Onboarding.gender)
    await message.answer(TRANSLATIONS[lang]["choose_gender"], reply_markup=gender_menu(lang))


@router.callback_query(Onboarding.gender, F.data.startswith("gender:"))
async def gender(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data(); lang = data["language"]
    await state.update_data(gender=callback.data.split(":")[1])
    await state.set_state(Onboarding.height)
    await callback.message.edit_text(TRANSLATIONS[lang]["enter_height"])
    await callback.answer()


@router.message(Onboarding.height)
async def height(message: Message, state: FSMContext):
    data = await state.get_data(); lang = data["language"]
    try:
        value = float(message.text.replace(",", "."))
        if not 120 <= value <= 230: raise ValueError
    except Exception:
        await message.answer("120–230 sm oralig‘ida kiriting." if lang=="uz" else "Введите рост 120–230 см.")
        return
    await state.update_data(height=value)
    await state.set_state(Onboarding.weight)
    await message.answer(TRANSLATIONS[lang]["enter_weight"])


@router.message(Onboarding.weight)
async def weight(message: Message, state: FSMContext):
    data = await state.get_data(); lang = data["language"]
    try:
        value = float(message.text.replace(",", "."))
        if not 30 <= value <= 300: raise ValueError
    except Exception:
        await message.answer("30–300 kg oralig‘ida kiriting." if lang=="uz" else "Введите вес 30–300 кг.")
        return
    await state.update_data(weight=value)
    await state.set_state(Onboarding.goal)
    await message.answer(TRANSLATIONS[lang]["choose_goal"], reply_markup=goal_menu(lang))


@router.callback_query(Onboarding.goal, F.data.startswith("goal:"))
async def goal(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data(); lang = data["language"]
    await state.update_data(goal=callback.data.split(":")[1])
    await state.set_state(Onboarding.activity)
    await callback.message.edit_text(TRANSLATIONS[lang]["choose_activity"], reply_markup=activity_menu(lang))
    await callback.answer()


@router.callback_query(Onboarding.activity, F.data.startswith("activity:"))
async def activity(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    activity_value = callback.data.split(":")[1]
    async with SessionFactory() as s:
        user = await get_or_create_user(s, callback.from_user.id, callback.from_user.username)
        await update_user(s, user,
            personal_id=data["personal_id"], name=data["name"], age=data["age"],
            gender=data["gender"], height_cm=data["height"],
            current_weight_kg=data["weight"], goal=data["goal"],
            activity=activity_value, language=lang, accepted_terms=True
        )
        await add_weight(s, user, data["weight"])
    await state.clear()
    await callback.message.edit_text(card("✅", f"{TRANSLATIONS[lang]['profile_ready']}\n🆔 <b>{data['personal_id']}</b>"))
    await callback.message.answer(TRANSLATIONS[lang]["main_prompt"],
        reply_markup=main_menu(lang, callback.from_user.id in settings.admins))
    await callback.answer()


@router.message(F.text.in_({"🌐 Tilni o‘zgartirish", "🌐 Изменить язык"}))
async def change_language(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Tilni tanlang / Выберите язык", reply_markup=language_menu())


@router.callback_query(F.data.startswith("lang:"))
async def change_language_callback(callback: CallbackQuery):
    lang = callback.data.split(":")[1]
    async with SessionFactory() as s:
        user = await get_or_create_user(s, callback.from_user.id, callback.from_user.username)
        await update_user(s, user, language=lang)
    await callback.message.answer(TRANSLATIONS[lang]["main_prompt"],
        reply_markup=main_menu(lang, callback.from_user.id in settings.admins))
    await callback.answer()

