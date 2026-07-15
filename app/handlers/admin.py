from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import get_settings
from app.database.repository import admin_stats, search_user_by_slimwell_id
from app.database.session import SessionFactory
from app.keyboards.menus import admin_menu
from app.services.health import calculate_metrics
from app.states.forms import AdminSearch
from app.utils.texts import card

router = Router()
settings = get_settings()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admins


@router.message(F.text == "🛡 Admin panel")
async def admin_root(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(card("🛡 ADMIN PANEL", "Foydalanuvchilar va statistika."), reply_markup=admin_menu())


@router.callback_query(F.data == "admin:stats")
async def stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q.", show_alert=True)
        return
    async with SessionFactory() as session:
        data = await admin_stats(session)
    await callback.message.edit_text(
        card("📊 UMUMIY STATISTIKA", f"👥 Jami: <b>{data['total']}</b>\n🟢 Oxirgi 7 kun faol: <b>{data['active']}</b>"),
        reply_markup=admin_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:search")
async def search_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminSearch.slimwell_id)
    await callback.message.answer("7 xonali SlimWell ID ni kiriting:")
    await callback.answer()


@router.message(AdminSearch.slimwell_id)
async def search_result(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    sid = (message.text or "").strip()
    async with SessionFactory() as session:
        user = await search_user_by_slimwell_id(session, sid)
    await state.clear()
    if not user:
        await message.answer(card("🔍 QIDIRUV", "Foydalanuvchi topilmadi."), reply_markup=admin_menu())
        return
    bmi = "—"
    if all([user.age, user.gender, user.height_cm, user.current_weight_kg, user.goal]):
        bmi = calculate_metrics(user.age, user.gender, user.height_cm, user.current_weight_kg, user.goal).bmi
    body = (
        f"🆔 ID: <b>{user.slimwell_id}</b>\n"
        f"👤 Ism: <b>{user.name}</b>\n"
        f"🎂 Yosh: <b>{user.age}</b>\n"
        f"⚧ Jins: <b>{user.gender}</b>\n"
        f"📏 Bo‘y: <b>{user.height_cm} sm</b>\n"
        f"⚖️ Vazn: <b>{user.current_weight_kg} kg</b>\n"
        f"📊 BMI: <b>{bmi}</b>\n"
        f"🎯 Maqsad: <b>{user.goal}</b>\n"
        f"🕒 Oxirgi faollik: <b>{user.last_active_at:%d.%m.%Y %H:%M}</b>"
    )
    await message.answer(card("👤 FOYDALANUVCHI KARTASI", body), reply_markup=admin_menu())

