import html
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.repository import (
    add_exercise, add_food, add_sleep, add_steps, add_water, add_weight,
    get_user, today_totals, weight_history
)
from app.database.session import SessionFactory
from app.keyboards.menus import (
    body_menu, exercise_menu, habits_menu, inline_menu, main_menu,
    meal_menu, results_menu, slimwell_menu
)
from app.services.health import bmi_guidance, bmi_label, calculate_metrics
from app.services.openai_service import analyze_food_image, generate_meal_plan
from app.states.forms import FoodScan, HabitInput, WeightInput
from app.utils.texts import SLIMWELL, card

router = Router()


async def require_profile(telegram_id: int):
    async with SessionFactory() as session:
        return await get_user(session, telegram_id)


@router.callback_query(F.data == "home")
async def home(callback: CallbackQuery):
    from app.config import get_settings
    await callback.message.answer("Asosiy menyu", reply_markup=main_menu(callback.from_user.id in get_settings().admins))
    await callback.answer()


@router.message(F.text == "📊 Tana tahlili")
async def body_root(message: Message):
    await message.answer(card("📊 TANA TAHLILI", "Profilingiz asosida kerakli tahlilni tanlang."), reply_markup=body_menu())


@router.callback_query(F.data.startswith("body:"))
async def body_action(callback: CallbackQuery):
    user = await require_profile(callback.from_user.id)
    if not user or not all([user.age, user.gender, user.height_cm, user.current_weight_kg, user.goal]):
        await callback.answer("Avval profilni to‘ldiring.", show_alert=True)
        return
    m = calculate_metrics(user.age, user.gender, user.height_cm, user.current_weight_kg, user.goal)
    action = callback.data.split(":")[1]
    if action == "bmi":
        body = f"⚖️ BMI: <b>{m.bmi}</b>\n📌 Izoh: {bmi_label(m.bmi)}"
    elif action == "calories":
        target = (
            f"{m.target_kcal} kkal"
            if m.target_kcal is not None
            else "18 yoshgacha avtomatik ozish kaloriyasi berilmaydi"
        )
        body = f"🔥 Vaznni saqlash: <b>~{m.maintenance_kcal} kkal</b>\n🎯 Maqsad uchun: <b>{target}</b>"
    elif action == "range":
        body = (f"🎯 Umumiy sog‘lom BMI oralig‘iga mos vazn: <b>{m.min_weight}–{m.max_weight} kg</b>\\n"        f"📐 Katalogdagi 22 × bo‘y² formulasi bo‘yicha namuna vazn: <b>{m.reference_weight} kg</b>")
    else:
        target = f"{m.target_kcal} kkal" if m.target_kcal else "umumiy sog‘lom reja"
        body = (
            f"⚖️ BMI: <b>{m.bmi}</b> — {bmi_label(m.bmi)}\n"
            f"🎯 Vazn oralig‘i: <b>{m.min_weight}–{m.max_weight} kg</b>\n"
            f"🔥 Saqlash kaloriyasi: <b>~{m.maintenance_kcal} kkal</b>\n"
            f"🥗 Maqsad rejasi: <b>{target}</b>\\n\\n{bmi_guidance(m.bmi)}"
        )
    await callback.message.edit_text(card("📊 TANA TAHLILI", body + "\n\n<i>Bu umumiy hisob-kitob, tibbiy tashxis emas.</i>"), reply_markup=body_menu())
    await callback.answer()


@router.message(F.text == "🥗 Shaxsiy ovqatlanish")
async def meal_root(message: Message):
    await message.answer(card("🥗 SHAXSIY OVQATLANISH", "3 mahal ovqatlanish rejasini tanlang."), reply_markup=meal_menu())


@router.callback_query(F.data.startswith("meal:"))
async def meal_action(callback: CallbackQuery):
    user = await require_profile(callback.from_user.id)
    if not user or not user.name:
        await callback.answer("Avval profilni to‘ldiring.", show_alert=True)
        return
    action = callback.data.split(":")[1]
    await callback.message.edit_text(card("⏳ TAYYORLANMOQDA", "Reja yaratilmoqda..."))
    try:
        if action in {"today", "week"}:
            text = await generate_meal_plan(user, 7 if action == "week" else 1)
        elif action == "shopping":
            text = "Tuxum, tovuq/baliq, loviya, guruch yoki grechka, butun donli non, qatiq/tvorog, mavsumiy sabzavot va mevalar."
        else:
            text = (
                "🥗 Tez salat: pomidor, bodring, ko‘kat, limon.\n"
                "🍳 Sabzavotli omlet: 2 tuxum va sabzavot.\n"
                "🍲 Tovuqli grechka: qaynatilgan tovuq, grechka va salat."
            )
    except Exception:
        text = "Reja yaratishda xatolik yuz berdi. OPENAI_API_KEY va model sozlamalarini tekshiring."
    await callback.message.edit_text(card("🥗 SHAXSIY OVQATLANISH", text), reply_markup=meal_menu())
    await callback.answer()


@router.message(F.text == "📸 Ovqatni tahlil qilish")
async def food_root(message: Message, state: FSMContext):
    await state.set_state(FoodScan.waiting_photo)
    await message.answer(card("📸 OVQATNI TAHLIL QILISH", "Ovqatning aniq va yorug‘ suratini yuboring. Natija taxminiy bo‘ladi."))


@router.message(FoodScan.waiting_photo, F.photo)
async def food_photo(message: Message, state: FSMContext):
    await message.answer("⏳ Surat tahlil qilinmoqda...")
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    buffer = await message.bot.download_file(file.file_path)
    try:
        result = await analyze_food_image(buffer.read())
        await state.update_data(food_result=result)
        await state.set_state(FoodScan.waiting_save)
        body = (
            f"🍽 Taom: <b>{html.escape(str(result.get('title', 'Noma’lum')))}</b>\n"
            f"⚖️ Porsiya: {html.escape(str(result.get('portion', 'taxminiy')))}\n"
            f"🔥 Kaloriya: <b>~{result.get('calories', 0)} kkal</b>\n"
            f"🥩 Oqsil: {result.get('protein_g', 0)} g\n"
            f"🥑 Yog‘: {result.get('fat_g', 0)} g\n"
            f"🍞 Uglevod: {result.get('carbs_g', 0)} g\n"
            f"🎯 Aniqlik: {html.escape(str(result.get('confidence', 'o‘rta')))}\n\n"
            f"<i>{html.escape(str(result.get('note', 'Surat asosidagi taxmin.')))}</i>"
        )
        await message.answer(card("📸 TAHLIL NATIJASI", body), reply_markup=inline_menu([
            ("➕ Kunlik hisobga qo‘shish", "food:save"),
            ("❌ Hisobga qo‘shmaslik", "food:cancel"),
        ]))
    except Exception as exc:
        await state.clear()
        await message.answer(card("⚠️ XATOLIK", "Surat tahlil qilinmadi. OpenAI kaliti va modelni tekshiring."))


@router.message(FoodScan.waiting_photo)
async def food_need_photo(message: Message):
    await message.answer("Iltimos, ovqat suratini yuboring.")


@router.callback_query(FoodScan.waiting_save, F.data == "food:save")
async def food_save(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    r = data["food_result"]
    async with SessionFactory() as session:
        user = await get_user(session, callback.from_user.id)
        await add_food(
            session, user, str(r.get("title", "Ovqat")), float(r.get("calories", 0)),
            float(r.get("protein_g", 0)), float(r.get("fat_g", 0)),
            float(r.get("carbs_g", 0)), str(r.get("note", ""))
        )
    await state.clear()
    await callback.message.edit_text(card("✅ SAQLANDI", "Ovqat bugungi hisobga qo‘shildi."))
    await callback.answer()


@router.callback_query(FoodScan.waiting_save, F.data == "food:cancel")
async def food_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(card("🗑 BEKOR QILINDI", "Natija saqlanmadi."))
    await callback.answer()


@router.message(F.text == "💧 Sog‘lom odatlar")
async def habits_root(message: Message):
    await message.answer(card("💧 SOG‘LOM ODATLAR", "Suv, qadam va uyqu qaydlarini boshqaring."), reply_markup=habits_menu())


@router.callback_query(F.data.startswith("habit:water:"))
async def water_action(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":")[-1]
    if value == "custom":
        await state.set_state(HabitInput.custom_water)
        await callback.message.answer("Suv miqdorini ml da kiriting:")
    else:
        async with SessionFactory() as session:
            user = await get_user(session, callback.from_user.id)
            await add_water(session, user, int(value))
        await callback.answer(f"+{value} ml qo‘shildi", show_alert=True)
    await callback.answer()


@router.message(HabitInput.custom_water)
async def custom_water(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        if not 1 <= amount <= 5000: raise ValueError
    except ValueError:
        await message.answer("1–5000 ml oralig‘ida kiriting.")
        return
    async with SessionFactory() as session:
        user = await get_user(session, message.from_user.id)
        await add_water(session, user, amount)
    await state.clear()
    await message.answer(card("✅ SAQLANDI", f"{amount} ml suv qo‘shildi."), reply_markup=habits_menu())


@router.callback_query(F.data == "habit:steps")
async def ask_steps(callback: CallbackQuery, state: FSMContext):
    await state.set_state(HabitInput.steps)
    await callback.message.answer("Bugungi qadam sonini kiriting:")
    await callback.answer()


@router.message(HabitInput.steps)
async def save_steps(message: Message, state: FSMContext):
    try:
        steps = int(message.text)
        if not 0 <= steps <= 100000: raise ValueError
    except ValueError:
        await message.answer("0–100000 oralig‘ida kiriting.")
        return
    async with SessionFactory() as session:
        user = await get_user(session, message.from_user.id)
        await add_steps(session, user, steps)
    await state.clear()
    await message.answer(card("✅ SAQLANDI", f"{steps} qadam qo‘shildi."), reply_markup=habits_menu())


@router.callback_query(F.data == "habit:sleep")
async def ask_sleep(callback: CallbackQuery, state: FSMContext):
    await state.set_state(HabitInput.sleep)
    await callback.message.answer("Uyqu davomiyligini soatda kiriting (masalan, 7.5):")
    await callback.answer()


@router.message(HabitInput.sleep)
async def save_sleep(message: Message, state: FSMContext):
    try:
        hours = float(message.text.replace(",", "."))
        if not 0 <= hours <= 24: raise ValueError
    except ValueError:
        await message.answer("0–24 soat oralig‘ida kiriting.")
        return
    async with SessionFactory() as session:
        user = await get_user(session, message.from_user.id)
        await add_sleep(session, user, hours)
    await state.clear()
    await message.answer(card("✅ SAQLANDI", f"{hours:g} soat uyqu qayd etildi."), reply_markup=habits_menu())


@router.callback_query(F.data == "habit:today")
async def habit_today(callback: CallbackQuery):
    async with SessionFactory() as session:
        user = await get_user(session, callback.from_user.id)
        totals = await today_totals(session, user)
    body = (
        f"💧 Suv: <b>{totals['water']} ml</b>\n"
        f"🚶 Qadamlar: <b>{totals['steps']}</b>\n"
        f"💪 Mashq: <b>{totals['exercise']} daqiqa</b>\n"
        f"🔥 Ovqat: <b>~{totals['calories']:.0f} kkal</b>"
    )
    await callback.message.edit_text(card("📋 BUGUNGI ODATLAR", body), reply_markup=habits_menu())
    await callback.answer()


@router.message(F.text == "💪 Mashqlar")
async def exercise_root(message: Message):
    await message.answer(card("💪 MASHQLAR", "Darajangizga mos yengil va xavfsiz reja tanlang."), reply_markup=exercise_menu())


@router.callback_query(F.data.startswith("exercise:"))
async def exercise_action(callback: CallbackQuery):
    action = callback.data.split(":")[1]
    plans = {
        "home": ("Uyda mashq", "5 daqiqa qizish, 3×8 o‘tirib-turish, 3×8 devorga suyanib push-up, 3×20 soniya plank.", 20),
        "light": ("Yengil faollik", "20–30 daqiqa qulay tezlikda piyoda yurish.", 25),
        "cardio": ("Kardio", "5 daqiqa qizish, 15 daqiqa tez yurish, 5 daqiqa sovush.", 25),
        "stretch": ("Cho‘zilish", "Bo‘yin, yelka, bel va oyoqlar uchun 10 daqiqa yumshoq cho‘zilish.", 10),
        "week": ("Haftalik reja", "Du/Chor/Juma — 20 daqiqa uy mashqi. Se/Pay/Shan — 25 daqiqa yurish. Yakshanba — yengil dam.", 0),
    }
    title, text, minutes = plans[action]
    buttons = [("✅ Bajarildi deb belgilash", f"exercise_done:{action}")] if minutes else []
    buttons.append(("⬅️ Mashqlar menyusi", "exercise_menu"))
    await callback.message.edit_text(card(f"💪 {title.upper()}", text + "\n\n<i>Og‘riq yoki bosh aylanishi bo‘lsa, to‘xtang.</i>"), reply_markup=inline_menu(buttons))
    await callback.answer()


@router.callback_query(F.data == "exercise_menu")
async def exercise_back(callback: CallbackQuery):
    await callback.message.edit_text(card("💪 MASHQLAR", "Kerakli rejani tanlang."), reply_markup=exercise_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("exercise_done:"))
async def exercise_done(callback: CallbackQuery):
    action = callback.data.split(":")[1]
    data = {"home": ("Uyda mashq",20), "light":("Yengil faollik",25), "cardio":("Kardio",25), "stretch":("Cho‘zilish",10)}
    title, minutes = data[action]
    async with SessionFactory() as session:
        user = await get_user(session, callback.from_user.id)
        await add_exercise(session, user, title, minutes)
    await callback.answer("Mashq natijalarga qo‘shildi.", show_alert=True)


@router.message(F.text == "💊 SlimWell")
async def slim_root(message: Message):
    await message.answer(card("💊 SLIMWELL", "Rasmiy yorliq va katalog asosidagi bo‘lim."), reply_markup=slimwell_menu())


@router.callback_query(F.data.startswith("slim:"))
async def slim_action(callback: CallbackQuery):
    action = callback.data.split(":")[1]
    await callback.message.edit_text(card("💊 SLIMWELL", SLIMWELL[action]), reply_markup=slimwell_menu())
    await callback.answer()


@router.message(F.text == "📈 Natijalar")
async def results_root(message: Message):
    await message.answer(card("📈 NATIJALAR", "Kundalik va vazn natijalarini ko‘ring."), reply_markup=results_menu())


@router.callback_query(F.data == "results:add_weight")
async def ask_weight(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WeightInput.weight)
    await callback.message.answer("Yangi vaznni kg da kiriting:")
    await callback.answer()


@router.message(WeightInput.weight)
async def save_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
        if not 30 <= weight <= 300: raise ValueError
    except ValueError:
        await message.answer("30–300 kg oralig‘ida kiriting.")
        return
    async with SessionFactory() as session:
        user = await get_user(session, message.from_user.id)
        await add_weight(session, user, weight)
    await state.clear()
    await message.answer(card("✅ SAQLANDI", f"Yangi vazn: <b>{weight:g} kg</b>"), reply_markup=results_menu())


@router.callback_query(F.data == "results:weights")
async def results_weights(callback: CallbackQuery):
    async with SessionFactory() as session:
        user = await get_user(session, callback.from_user.id)
        rows = await weight_history(session, user)
    text = "\n".join(f"• {r.recorded_at:%d.%m.%Y}: <b>{r.weight_kg:g} kg</b>" for r in rows) or "Hali ma’lumot yo‘q."
    await callback.message.edit_text(card("📉 VAZN TARIXI", text), reply_markup=results_menu())
    await callback.answer()


@router.callback_query(F.data == "results:bmi")
async def results_bmi(callback: CallbackQuery):
    user = await require_profile(callback.from_user.id)
    m = calculate_metrics(user.age, user.gender, user.height_cm, user.current_weight_kg, user.goal)
    await callback.message.edit_text(card("📊 BMI NATIJASI", f"Joriy BMI: <b>{m.bmi}</b>\n{bmi_label(m.bmi)}"), reply_markup=results_menu())
    await callback.answer()


@router.callback_query(F.data == "results:today")
async def results_today(callback: CallbackQuery):
    async with SessionFactory() as session:
        user = await get_user(session, callback.from_user.id)
        totals = await today_totals(session, user)
    body = (
        f"🔥 Kaloriya: <b>~{totals['calories']:.0f} kkal</b>\n"
        f"💧 Suv: <b>{totals['water']} ml</b>\n"
        f"🚶 Qadamlar: <b>{totals['steps']}</b>\n"
        f"💪 Mashq: <b>{totals['exercise']} daqiqa</b>"
    )
    await callback.message.edit_text(card("📋 BUGUNGI HISOBOT", body), reply_markup=results_menu())
    await callback.answer()
