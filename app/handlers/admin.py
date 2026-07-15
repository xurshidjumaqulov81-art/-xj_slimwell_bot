from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from app.config import get_settings
from app.database.crud import admin_stats, find_by_personal_id
from app.database.db import SessionFactory
from app.keyboards import inline
from app.services.health import calculate
from app.states import AdminSearch
from app.utils.text import card

router=Router(); settings=get_settings()


@router.message(F.text=="🛡 Admin panel")
async def root(m:Message):
    if m.from_user.id not in settings.admins:return
    await m.answer(card("🛡 ADMIN PANEL","Foydalanuvchilarni kuzatish."),
        reply_markup=inline([("📊 Statistika","admin:stats"),("🔍 ID qidirish","admin:search")]))


@router.callback_query(F.data=="admin:stats")
async def stats(c:CallbackQuery):
    if c.from_user.id not in settings.admins:return
    async with SessionFactory() as s:d=await admin_stats(s)
    await c.message.answer(card("📊 STATISTIKA",f"👥 Jami: {d['total']}\n✅ Profil to‘liq: {d['completed']}"));await c.answer()


@router.callback_query(F.data=="admin:search")
async def search(c:CallbackQuery,state:FSMContext):
    if c.from_user.id not in settings.admins:return
    await state.set_state(AdminSearch.personal_id);await c.message.answer("7 xonali shaxsiy ID ni kiriting:");await c.answer()


@router.message(AdminSearch.personal_id)
async def found(m:Message,state:FSMContext):
    if m.from_user.id not in settings.admins:return
    async with SessionFactory() as s:u=await find_by_personal_id(s,(m.text or "").strip())
    await state.clear()
    if not u:await m.answer("Topilmadi.");return
    mm=calculate(u)
    await m.answer(card("👤 FOYDALANUVCHI",
        f"🆔 {u.personal_id}\n👤 {u.name}\n🎂 {u.age}\n📏 {u.height_cm:g} sm\n"
        f"⚖️ {u.current_weight_kg:g} kg\n📊 BMI {mm.bmi:.2f}\n🕒 {u.last_active_at:%d.%m.%Y %H:%M}"))
