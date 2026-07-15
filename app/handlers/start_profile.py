from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.repository import get_or_create_user, get_user, update_user, add_weight
from app.database.session import SessionFactory
from app.keyboards.menus import gender_menu, goal_menu, main_menu, profile_menu
from app.states.forms import EditProfile, Onboarding
from app.utils.texts import TERMS, card

router = Router()
settings = get_settings()


async def session_user(message: Message):
    async with SessionFactory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.username)
        return user


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    user = await session_user(message)
    if not user.accepted_terms:
        from app.keyboards.menus import inline_menu
        await message.answer(
            TERMS,
            reply_markup=inline_menu([("✅ Roziman va davom etaman", "terms:accept")]),
        )
        return
    if not user.name:
        await message.answer("Ismingizni kiriting:")
        await state.set_state(Onboarding.name)
        return
    await message.answer(
        card("✨ SLIMWELL", f"Xush kelibsiz, <b>{user.name}</b>!\nKerakli bo‘limni tanlang."),
        reply_markup=main_menu(message.from_user.id in settings.admins),
    )


@router.callback_query(F.data == "terms:accept")
async def accept_terms(callback: CallbackQuery, state: FSMContext):
    async with SessionFactory() as session:
        user = await get_or_create_user(session, callback.from_user.id, callback.from_user.username)
        await update_user(session, user, accepted_terms=True)
    await callback.message.edit_text(card("✅ TASDIQLANDI", "Endi profilingizni to‘ldiramiz."))
    await callback.message.answer("Ismingizni kiriting:")
    await state.set_state(Onboarding.name)
    await callback.answer()


@router.message(Onboarding.name)
async def set_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if len(name) < 2 or len(name) > 50:
        await message.answer("Ism 2–50 ta belgidan iborat bo‘lsin.")
        return
    await state.update_data(name=name)
    await message.answer("Yoshingizni kiriting (masalan, 28):")
    await state.set_state(Onboarding.age)


@router.message(Onboarding.age)
async def set_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if not 13 <= age <= 100:
            raise ValueError
    except (TypeError, ValueError):
        await message.answer("Yoshni 13 dan 100 gacha raqam bilan kiriting.")
        return
    await state.update_data(age=age)
    await message.answer("Jinsingizni tanlang:", reply_markup=gender_menu())
    await state.set_state(Onboarding.gender)


@router.callback_query(Onboarding.gender, F.data.startswith("set_gender:"))
async def set_gender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data.split(":", 1)[1]
    await state.update_data(gender=gender)
    await callback.message.edit_text(f"Jins: <b>{gender}</b>")
    await callback.message.answer("Bo‘yingizni santimetrda kiriting (masalan, 170):")
    await state.set_state(Onboarding.height)
    await callback.answer()


@router.message(Onboarding.height)
async def set_height(message: Message, state: FSMContext):
    try:
        height = float((message.text or "").replace(",", "."))
        if not 120 <= height <= 230:
            raise ValueError
    except ValueError:
        await message.answer("Bo‘yni 120–230 sm oralig‘ida kiriting.")
        return
    await state.update_data(height_cm=height)
    await message.answer("Vazningizni kilogrammda kiriting (masalan, 75.5):")
    await state.set_state(Onboarding.weight)


@router.message(Onboarding.weight)
async def set_weight(message: Message, state: FSMContext):
    try:
        weight = float((message.text or "").replace(",", "."))
        if not 30 <= weight <= 300:
            raise ValueError
    except ValueError:
        await message.answer("Vaznni 30–300 kg oralig‘ida kiriting.")
        return
    await state.update_data(weight=weight)
    await message.answer("Maqsadingizni tanlang:", reply_markup=goal_menu())
    await state.set_state(Onboarding.goal)


@router.callback_query(Onboarding.goal, F.data.startswith("set_goal:"))
async def set_goal(callback: CallbackQuery, state: FSMContext):
    goal = callback.data.split(":", 1)[1]
    data = await state.get_data()
    async with SessionFactory() as session:
        user = await get_or_create_user(session, callback.from_user.id, callback.from_user.username)
        await update_user(
            session, user, name=data["name"], age=data["age"], gender=data["gender"],
            height_cm=data["height_cm"], current_weight_kg=data["weight"], goal=goal
        )
        await add_weight(session, user, data["weight"])
        slim_id = user.slimwell_id
    await state.clear()
    await callback.message.edit_text(
        card("✅ PROFIL TAYYOR", f"Sizning SlimWell ID raqamingiz: <b>{slim_id}</b>")
    )
    await callback.message.answer(
        "Asosiy menyu ochildi.",
        reply_markup=main_menu(callback.from_user.id in settings.admins),
    )
    await callback.answer()


@router.message(F.text == "👤 Mening profilim")
async def profile_root(message: Message):
    await message.answer(card("👤 MENING PROFILIM", "Profil ma’lumotlarini ko‘ring yoki tahrirlang."), reply_markup=profile_menu())


@router.callback_query(F.data == "profile:view")
async def profile_view(callback: CallbackQuery):
    async with SessionFactory() as session:
        user = await get_user(session, callback.from_user.id)
    if not user:
        await callback.answer("Profil topilmadi.", show_alert=True)
        return
    body = (
        f"🆔 ID: <b>{user.slimwell_id}</b>\n"
        f"👤 Ism: <b>{user.name}</b>\n"
        f"🎂 Yosh: <b>{user.age}</b>\n"
        f"⚧ Jins: <b>{user.gender}</b>\n"
        f"📏 Bo‘y: <b>{user.height_cm:g} sm</b>\n"
        f"⚖️ Vazn: <b>{user.current_weight_kg:g} kg</b>\n"
        f"🎯 Maqsad: <b>{user.goal}</b>"
    )
    await callback.message.edit_text(card("👤 MENING PROFILIM", body), reply_markup=profile_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("profile:edit:"))
async def profile_edit(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split(":")[-1]
    if field == "gender":
        await state.update_data(edit_field=field)
        await state.set_state(EditProfile.field_value)
        await callback.message.answer("Jinsni tanlang:", reply_markup=gender_menu())
    elif field == "goal":
        await state.update_data(edit_field=field)
        await state.set_state(EditProfile.field_value)
        await callback.message.answer("Maqsadni tanlang:", reply_markup=goal_menu())
    else:
        labels = {"name": "yangi ism", "age": "yangi yosh", "height_cm": "yangi bo‘y (sm)", "weight": "yangi vazn (kg)"}
        await state.update_data(edit_field=field)
        await state.set_state(EditProfile.field_value)
        await callback.message.answer(f"{labels[field]}ni kiriting:")
    await callback.answer()


@router.callback_query(EditProfile.field_value, F.data.startswith("set_gender:"))
async def edit_gender(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":", 1)[1]
    async with SessionFactory() as session:
        user = await get_user(session, callback.from_user.id)
        await update_user(session, user, gender=value)
    await state.clear()
    await callback.message.edit_text(card("✅ SAQLANDI", f"Jins: <b>{value}</b>"), reply_markup=profile_menu())
    await callback.answer()


@router.callback_query(EditProfile.field_value, F.data.startswith("set_goal:"))
async def edit_goal(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":", 1)[1]
    async with SessionFactory() as session:
        user = await get_user(session, callback.from_user.id)
        await update_user(session, user, goal=value)
    await state.clear()
    await callback.message.edit_text(card("✅ SAQLANDI", f"Maqsad: <b>{value}</b>"), reply_markup=profile_menu())
    await callback.answer()


@router.message(EditProfile.field_value)
async def edit_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("edit_field")
    raw = (message.text or "").strip()
    try:
        if field == "name":
            if not 2 <= len(raw) <= 50: raise ValueError
            values = {"name": raw}
        elif field == "age":
            val = int(raw)
            if not 13 <= val <= 100: raise ValueError
            values = {"age": val}
        elif field == "height_cm":
            val = float(raw.replace(",", "."))
            if not 120 <= val <= 230: raise ValueError
            values = {"height_cm": val}
        elif field == "weight":
            val = float(raw.replace(",", "."))
            if not 30 <= val <= 300: raise ValueError
            values = {"current_weight_kg": val}
        else:
            raise ValueError
    except ValueError:
        await message.answer("Qiymat noto‘g‘ri. Qayta kiriting.")
        return

    async with SessionFactory() as session:
        user = await get_user(session, message.from_user.id)
        if field == "weight":
            await add_weight(session, user, values["current_weight_kg"])
        else:
            await update_user(session, user, **values)
    await state.clear()
    await message.answer(card("✅ SAQLANDI", "Profil ma’lumoti yangilandi."), reply_markup=profile_menu())
