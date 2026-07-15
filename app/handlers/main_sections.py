from pathlib import Path
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message, BufferedInputFile
from app.config import ASSETS_DIR, get_settings
from app.content import PRODUCT
from app.database.crud import (
    get_user, update_user, add_weight, add_water, add_steps, add_sleep,
    add_food, add_exercise, get_weight_history, today_totals
)
from app.database.db import SessionFactory
from app.keyboards import (
    main_menu, profile_menu, body_menu, meal_menu, slimwell_menu,
    habits_menu, results_menu, inline, gender_menu, goal_menu
)
from app.services.health import calculate, plan_for, capsule_schedule
from app.services.visuals import generate_bmi_gif
from app.services.openai_service import meal_plan, analyze_food
from app.states import EditProfile, HabitInput, FoodScan
from app.utils.text import card, progress

router = Router()
settings = get_settings()

MAIN_TEXTS = {
    "👤 Mening profilim", "📊 Tana tahlili", "🥗 Shaxsiy ovqatlanish",
    "📸 Ovqatni tahlil qilish", "💧 Sog‘lom odatlar", "💪 Mashqlar",
    "💊 SlimWell", "📈 Natijalar",
    "👤 Мой профиль", "📊 Анализ тела", "🥗 Питание",
    "📸 Анализ еды", "💧 Полезные привычки", "💪 Упражнения",
    "📈 Результаты",
}


async def user_for(tid):
    async with SessionFactory() as s:
        return await get_user(s, tid)


@router.message(F.text.in_(MAIN_TEXTS))
async def clear_old_state(message: Message, state: FSMContext):
    await state.clear()
    # Dispatcher continues only if handlers below are registered earlier? This handler itself
    # serves as a safe reset; sections are dispatched by direct checks below through manual call.
    text = message.text
    if text in {"👤 Mening profilim", "👤 Мой профиль"}:
        await profile_root(message)
    elif text in {"📊 Tana tahlili", "📊 Анализ тела"}:
        await body_root(message)
    elif text in {"🥗 Shaxsiy ovqatlanish", "🥗 Питание"}:
        await meal_root(message)
    elif text in {"📸 Ovqatni tahlil qilish", "📸 Анализ еды"}:
        await food_root(message, state)
    elif text in {"💧 Sog‘lom odatlar", "💧 Полезные привычки"}:
        await habits_root(message)
    elif text in {"💪 Mashqlar", "💪 Упражнения"}:
        await exercise_root(message)
    elif text == "💊 SlimWell":
        await slim_root(message)
    elif text in {"📈 Natijalar", "📈 Результаты"}:
        await results_root(message)


async def profile_root(message):
    u = await user_for(message.from_user.id)
    await message.answer(card("👤 PROFIL" if u.language=="uz" else "👤 ПРОФИЛЬ",
        "Ma’lumotlaringizni ko‘ring yoki yangilang." if u.language=="uz" else "Просмотр и изменение данных."),
        reply_markup=profile_menu(u.language))


@router.callback_query(F.data == "profile:view")
async def profile_view(c: CallbackQuery):
    u = await user_for(c.from_user.id)
    gender = ("Erkak" if u.gender=="male" else "Ayol") if u.language=="uz" else ("Мужчина" if u.gender=="male" else "Женщина")
    body = (
        f"🆔 ID: <b>{u.personal_id}</b>\n👤 <b>{u.name}</b>\n"
        f"🎂 {u.age}\n⚧ {gender}\n📏 {u.height_cm:g} sm\n⚖️ {u.current_weight_kg:g} kg"
    )
    await c.message.edit_text(card("👤 PROFIL" if u.language=="uz" else "👤 ПРОФИЛЬ", body),
                              reply_markup=profile_menu(u.language))
    await c.answer()


@router.callback_query(F.data.startswith("profile:edit:"))
async def profile_edit(c: CallbackQuery, state: FSMContext):
    u = await user_for(c.from_user.id)
    field = c.data.split(":")[-1]
    await state.update_data(field=field)
    await state.set_state(EditProfile.value)
    if field == "goal":
        await c.message.answer("Maqsadni tanlang:" if u.language=="uz" else "Выберите цель:", reply_markup=goal_menu(u.language))
    else:
        await c.message.answer("Yangi qiymatni kiriting:" if u.language=="uz" else "Введите новое значение:")
    await c.answer()


@router.callback_query(EditProfile.value, F.data.startswith("goal:"))
async def edit_goal(c: CallbackQuery, state: FSMContext):
    async with SessionFactory() as s:
        u = await get_user(s, c.from_user.id)
        await update_user(s, u, goal=c.data.split(":")[1])
    await state.clear()
    await c.message.answer("✅ Saqlandi")
    await c.answer()


@router.message(EditProfile.value)
async def edit_value(m: Message, state: FSMContext):
    data = await state.get_data(); field = data["field"]; raw = (m.text or "").strip()
    try:
        if field=="name": values={"name":raw}
        elif field=="age": values={"age":int(raw)}
        elif field=="height_cm": values={"height_cm":float(raw.replace(",","."))}
        elif field=="weight": values={"current_weight_kg":float(raw.replace(",","."))}
        else: raise ValueError
    except Exception:
        await m.answer("Qiymat noto‘g‘ri. / Неверное значение.")
        return
    async with SessionFactory() as s:
        u = await get_user(s, m.from_user.id)
        if field=="weight": await add_weight(s, u, values["current_weight_kg"])
        else: await update_user(s, u, **values)
    await state.clear()
    await m.answer("✅ Saqlandi / Сохранено")


async def body_root(message):
    u = await user_for(message.from_user.id)
    metrics, plan = plan_for(u, u.language)
    body = (
        f"👤 {u.name}\n📏 {u.height_cm:g} sm   ⚖️ {u.current_weight_kg:g} kg\n"
        f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n🎯 {plan['title']}"
    )
    image = ASSETS_DIR / ("body_male.png" if u.gender=="male" else "body_female.png")
    if image.exists():
        await message.answer_photo(FSInputFile(image), caption=card("📊 TANA TAHLILI" if u.language=="uz" else "📊 АНАЛИЗ ТЕЛА", body),
                                   reply_markup=body_menu(u.language))
    else:
        await message.answer(card("📊 TANA TAHLILI", body), reply_markup=body_menu(u.language))


@router.callback_query(F.data.startswith("body:"))
async def body_action(c: CallbackQuery):
    u = await user_for(c.from_user.id)
    m, plan = plan_for(u, u.language)
    action = c.data.split(":")[1]
    if action == "bmi":
        gif = generate_bmi_gif(m.bmi, Path("/tmp") / f"bmi_{c.from_user.id}.gif")
        caption = f"📊 <b>BMI: {m.bmi:.2f}</b>\n🎯 {plan['title']}"
        await c.message.answer_animation(FSInputFile(gif), caption=caption)
    elif action == "calories":
        target = m.target_kcal or m.maintenance_kcal
        body = (
            f"⚡ <b>{target} kkal</b>\n\n"
            f"🥩 Oqsil: {m.protein_g} g\n🥑 Yog‘: {m.fat_g} g\n🍚 Uglevod: {m.carbs_g} g"
            if u.language=="uz" else
            f"⚡ <b>{target} ккал</b>\n\nБелок: {m.protein_g} г\nЖиры: {m.fat_g} г\nУглеводы: {m.carbs_g} г"
        )
        await c.message.answer(card("⚡ KUNLIK ENERGIYA" if u.language=="uz" else "⚡ ДНЕВНАЯ ЭНЕРГИЯ", body))
    elif action == "range":
        if u.language=="uz":
            body = (f"✅ <b>{m.normal_min}–{m.normal_max} kg — norma vazn oralig‘i</b>\n"
                    f"⭐ <b>{m.ideal_weight} kg — ideal vazn</b>")
        else:
            body = (f"✅ <b>{m.normal_min}–{m.normal_max} кг — диапазон нормы</b>\n"
                    f"⭐ <b>{m.ideal_weight} кг — идеальный вес</b>")
        await c.message.answer(card("🎯 VAZN KO‘RSATKICHLARI" if u.language=="uz" else "🎯 ПОКАЗАТЕЛИ ВЕСА", body))
    else:
        body = (
            f"📊 BMI: <b>{m.bmi:.2f}</b>\n🎯 {plan['title']}\n\n"
            f"✅ {m.normal_min}–{m.normal_max} kg — norma vazn oralig‘i\n"
            f"⭐ {m.ideal_weight} kg — ideal vazn\n"
            f"⚡ {m.target_kcal or m.maintenance_kcal} kkal — kunlik maqsad\n\n"
            f"🌿 Siz to‘g‘ri yo‘ldasiz. Har bir kichik qadam natijaga olib keladi."
            if u.language=="uz" else
            f"📊 BMI: <b>{m.bmi:.2f}</b>\n🎯 {plan['title']}\n\n"
            f"✅ {m.normal_min}–{m.normal_max} кг — норма\n"
            f"⭐ {m.ideal_weight} кг — идеальный вес\n"
            f"⚡ {m.target_kcal or m.maintenance_kcal} ккал — цель\n\n"
            f"🌿 Каждый шаг приближает вас к результату."
        )
        await c.message.answer(card("🧍 TO‘LIQ TAHLIL" if u.language=="uz" else "🧍 ПОЛНЫЙ АНАЛИЗ", body))
    await c.answer()


async def slim_root(message):
    u = await user_for(message.from_user.id)
    image = ASSETS_DIR / "product.png"
    caption = ("SlimWell bo‘limida qabul tartibi va mahsulot ma’lumotlari." if u.language=="uz"
               else "Режим приёма и информация о продукте.")
    if image.exists():
        await message.answer_photo(FSInputFile(image), caption=card("💊 XJ SLIMWELL", caption), reply_markup=slimwell_menu(u.language))
    else:
        await message.answer(card("💊 XJ SLIMWELL", caption), reply_markup=slimwell_menu(u.language))


@router.callback_query(F.data.startswith("slim:"))
async def slim_action(c: CallbackQuery):
    u = await user_for(c.from_user.id)
    action = c.data.split(":")[1]
    m, plan = plan_for(u, u.language)
    if action in {"usage", "plan"}:
        schedule = capsule_schedule(plan["capsules"], u.language)
        body = (
            f"🎯 BMI: <b>{m.bmi:.2f}</b> — {plan['title']}\n"
            f"💊 Kuniga: <b>{plan['capsules']} kapsula</b>\n\n{schedule}\n\n"
            f"💧 Har qabulda suv bilan iching.\n📅 Kurs: maqsad vaznga yetguncha reja bo‘yicha davom ettiriladi."
            if u.language=="uz" else
            f"🎯 BMI: <b>{m.bmi:.2f}</b> — {plan['title']}\n"
            f"💊 В день: <b>{plan['capsules']} капсулы</b>\n\n{schedule}\n\n"
            f"💧 Принимайте с водой.\n📅 Курс продолжается по плану до целевого веса."
        )
        await c.message.answer(card("⏰ QABUL REJASI" if u.language=="uz" else "⏰ РЕЖИМ ПРИЁМА", body))
    elif action == "certs":
        cert = ASSETS_DIR / "certificates.png"
        if cert.exists():
            await c.message.answer_photo(FSInputFile(cert), caption=PRODUCT[u.language]["certs"])
        else:
            await c.message.answer(PRODUCT[u.language]["certs"])
    else:
        key = {"about":"about","ingredients":"ingredients","storage":"storage","warnings":"warnings","faq":"faq"}[action]
        await c.message.answer(card("💊 SLIMWELL", PRODUCT[u.language][key]))
    await c.answer()


async def meal_root(message):
    u = await user_for(message.from_user.id)
    await message.answer(card("🥗 SHAXSIY OVQATLANISH" if u.language=="uz" else "🥗 ПИТАНИЕ",
                              "3 mahal ovqatlanish rejasini tanlang." if u.language=="uz" else "Выберите план на 3 приёма пищи."),
                         reply_markup=meal_menu(u.language))


@router.callback_query(F.data.startswith("meal:"))
async def meal_action(c: CallbackQuery):
    u = await user_for(c.from_user.id)
    action = c.data.split(":")[1]
    if action=="shopping":
        text = "Tuxum, tovuq/baliq, loviya, grechka/guruch, qatiq/tvorog, sabzavot va mevalar." if u.language=="uz" else "Яйца, курица/рыба, бобовые, крупы, творог, овощи и фрукты."
    else:
        await c.message.answer("⏳ Reja tayyorlanmoqda..." if u.language=="uz" else "⏳ План готовится...")
        text = await meal_plan(u, 7 if action=="week" else 1)
    await c.message.answer(card("🥗 MENYU" if u.language=="uz" else "🥗 МЕНЮ", text))
    await c.answer()


async def food_root(message, state):
    u = await user_for(message.from_user.id)
    await state.set_state(FoodScan.photo)
    text = ("Ovqatingizning aniq va yorug‘ suratini yuboring.\n\nMasalan: 🥗 Tovuq va guruch · 🍚 Osh · 🍕 Pizza"
            if u.language=="uz" else "Отправьте чёткое фото еды.\n\nНапример: салат с курицей · плов · пицца")
    await message.answer(card("📸 OVQAT TAHLILI" if u.language=="uz" else "📸 АНАЛИЗ ЕДЫ", text))


@router.message(FoodScan.photo, F.photo)
async def food_photo(m: Message, state: FSMContext):
    u = await user_for(m.from_user.id)
    await m.answer("⏳ Surat tahlil qilinmoqda..." if u.language=="uz" else "⏳ Анализируем фото...")
    f = await m.bot.get_file(m.photo[-1].file_id)
    buf = await m.bot.download_file(f.file_path)
    try:
        r = await analyze_food(buf.read())
    except Exception:
        await state.clear()
        await m.answer("📸 Surat tahlili vaqtincha ishlamadi.\nBoshqa surat yuboring yoki birozdan keyin qayta urinib ko‘ring."
                       if u.language=="uz" else "📸 Анализ временно недоступен.\nПопробуйте другое фото или повторите позже.")
        return
    await state.update_data(food=r)
    await state.set_state(FoodScan.confirm)
    body = (f"🍽 <b>{r.get('title')}</b>\n⚖️ {r.get('portion')}\n"
            f"⚡ ~{r.get('calories')} kkal\n🥩 {r.get('protein_g')} g · 🥑 {r.get('fat_g')} g · 🍚 {r.get('carbs_g')} g")
    await m.answer(card("📸 NATIJA" if u.language=="uz" else "📸 РЕЗУЛЬТАТ", body),
                   reply_markup=inline([("➕ Saqlash" if u.language=="uz" else "➕ Сохранить","food:save"),
                                        ("❌ Bekor qilish" if u.language=="uz" else "❌ Отмена","food:cancel")]))


@router.callback_query(FoodScan.confirm, F.data.startswith("food:"))
async def food_confirm(c: CallbackQuery, state: FSMContext):
    if c.data=="food:save":
        data = await state.get_data()
        async with SessionFactory() as s:
            u = await get_user(s, c.from_user.id)
            await add_food(s, u, data["food"])
        await c.message.edit_text("✅ Saqlandi / Сохранено")
    else:
        await c.message.edit_text("Bekor qilindi / Отменено")
    await state.clear(); await c.answer()


async def habits_root(message):
    u = await user_for(message.from_user.id)
    text = ("Har kuni suv, qadam va uyqu maqsadlaringizni kuzating. Kichik odatlar katta natijalarga olib keladi."
            if u.language=="uz" else "Следите за водой, шагами и сном. Маленькие привычки ведут к большому результату.")
    await message.answer(card("💧 SOG‘LOM ODATLAR" if u.language=="uz" else "💧 ПОЛЕЗНЫЕ ПРИВЫЧКИ", text),
                         reply_markup=habits_menu(u.language))


@router.callback_query(F.data.startswith("habit:"))
async def habit_action(c: CallbackQuery, state: FSMContext):
    u = await user_for(c.from_user.id)
    parts = c.data.split(":")
    if parts[1]=="water" and parts[2] in {"250","500"}:
        async with SessionFactory() as s:
            dbu=await get_user(s,c.from_user.id); await add_water(s,dbu,int(parts[2]))
        await c.answer(f"+{parts[2]} ml", show_alert=True); return
    if c.data=="habit:water:custom":
        await state.set_state(HabitInput.water); await c.message.answer("Miqdorni ml da kiriting:"); await c.answer(); return
    if c.data=="habit:steps":
        await state.set_state(HabitInput.steps); await c.message.answer("Qadam sonini kiriting:"); await c.answer(); return
    if c.data=="habit:sleep":
        await state.set_state(HabitInput.sleep); await c.message.answer("Uyqu soatini kiriting:"); await c.answer(); return
    async with SessionFactory() as s:
        dbu=await get_user(s,c.from_user.id); t=await today_totals(s,dbu)
    water_target = 2500
    body=(f"💧 {progress(t['water'],water_target)} {t['water']}/{water_target} ml\n"
          f"👣 {progress(t['steps'],10000)} {t['steps']}/10000\n"
          f"💪 {t['exercise']} daqiqa\n⚡ ~{t['calories']:.0f} kkal")
    await c.message.answer(card("📊 BUGUNGI HISOBOT",body)); await c.answer()


@router.message(HabitInput.water)
async def custom_water(m: Message, state: FSMContext):
    try: v=int(m.text); assert 1<=v<=5000
    except: await m.answer("1–5000 ml kiriting."); return
    async with SessionFactory() as s:
        u=await get_user(s,m.from_user.id); await add_water(s,u,v)
    await state.clear(); await m.answer("✅ Saqlandi")


@router.message(HabitInput.steps)
async def custom_steps(m: Message, state: FSMContext):
    try: v=int(m.text); assert 0<=v<=100000
    except: await m.answer("Qadamni raqam bilan kiriting."); return
    async with SessionFactory() as s:
        u=await get_user(s,m.from_user.id); await add_steps(s,u,v)
    await state.clear(); await m.answer("✅ Saqlandi")


@router.message(HabitInput.sleep)
async def custom_sleep(m: Message, state: FSMContext):
    try: v=float(m.text.replace(",",".")); assert 0<=v<=24
    except: await m.answer("0–24 oralig‘ida kiriting."); return
    async with SessionFactory() as s:
        u=await get_user(s,m.from_user.id); await add_sleep(s,u,v)
    await state.clear(); await m.answer("✅ Saqlandi")


EXERCISES = {
    "overweight":[("Tez yurish","30–40 daqiqa","walk.gif",35),("Squat","3 × 15","squat.gif",12),("Plank","3 × 30 soniya","plank.gif",5)],
    "obesity1":[("Yurish","30 daqiqa","walk.gif",30),("Stulga o‘tirib-turish","3 × 12","squat.gif",12),("Joyida qadam","3 × 2 daqiqa","march.gif",6)],
    "obesity2":[("Sekin yurish","20–30 daqiqa","walk.gif",25),("O‘tirib oyoq ko‘tarish","3 × 12","leg_raise.gif",10),("Qo‘l aylantirish","3 × 20","arms.gif",8)],
    "obesity3":[("Sekin yurish","15–20 daqiqa","walk.gif",18),("O‘tirgan holda oyoq mashqi","3 × 10","leg_raise.gif",8),("Nafas mashqi","5 daqiqa","breath.gif",5)],
    "normal":[("Tez yurish","30 daqiqa","walk.gif",30),("Squat","3 × 15","squat.gif",12),("Plank","3 × 30 soniya","plank.gif",5)],
}


async def exercise_root(message):
    u=await user_for(message.from_user.id); m=calculate(u)
    title="💪 UY SHAROITIDAGI 3 TA MASHQ" if u.language=="uz" else "💪 3 УПРАЖНЕНИЯ ДОМА"
    await message.answer(card(title, "Mashqni tanlang — animatsiya va tartibi chiqadi." if u.language=="uz" else "Выберите упражнение."))
    for idx,(name,amount,gif,minutes) in enumerate(EXERCISES[m.category_key],1):
        path=ASSETS_DIR/"exercises"/gif
        caption=f"<b>{idx}. {name}</b>\n⏱ {amount}"
        kb=inline([("✅ Bajarildi" if u.language=="uz" else "✅ Выполнено",f"exercise_done:{idx-1}")])
        if path.exists(): await message.answer_animation(FSInputFile(path),caption=caption,reply_markup=kb)
        else: await message.answer(caption,reply_markup=kb)


@router.callback_query(F.data.startswith("exercise_done:"))
async def exercise_done(c: CallbackQuery):
    u=await user_for(c.from_user.id); m=calculate(u); idx=int(c.data.split(":")[1])
    name,_,_,minutes=EXERCISES[m.category_key][idx]
    async with SessionFactory() as s:
        dbu=await get_user(s,c.from_user.id); await add_exercise(s,dbu,name,minutes)
    await c.answer("Ajoyib! Natijaga qo‘shildi. 🎉",show_alert=True)


async def results_root(message):
    u=await user_for(message.from_user.id)
    await message.answer(card("📈 NATIJALAR" if u.language=="uz" else "📈 РЕЗУЛЬТАТЫ",
        "Har bir o‘zgarishni kuzating va maqsadingizga yaqinlashing." if u.language=="uz" else "Следите за прогрессом."),
        reply_markup=results_menu(u.language))


@router.callback_query(F.data.startswith("result:"))
async def result_action(c: CallbackQuery, state: FSMContext):
    u=await user_for(c.from_user.id); action=c.data.split(":")[1]
    if action=="add":
        await state.set_state(HabitInput.weight); await c.message.answer("Yangi vaznni kiriting:"); await c.answer(); return
    async with SessionFactory() as s:
        dbu=await get_user(s,c.from_user.id)
        if action=="history":
            rows=await get_weight_history(s,dbu)
            text="\n".join(f"• {x.recorded_at:%d.%m.%Y}: <b>{x.weight_kg:g} kg</b>" for x in rows) or "Hali ma’lumot yo‘q."
        elif action=="today":
            t=await today_totals(s,dbu); text=f"💧 {t['water']} ml\n👣 {t['steps']}\n💪 {t['exercise']} daqiqa\n⚡ ~{t['calories']:.0f} kkal"
        else:
            mm=calculate(dbu); remaining=max(dbu.current_weight_kg-mm.normal_max,0)
            text=f"⚖️ Hozirgi vazn: {dbu.current_weight_kg:g} kg\n🎯 Norma chegarasigacha: <b>{remaining:.1f} kg</b>\n🌿 Davom eting, siz to‘g‘ri yo‘ldasiz!"
    await c.message.answer(card("📈 NATIJA",text)); await c.answer()


@router.message(HabitInput.weight)
async def result_weight(m: Message, state: FSMContext):
    try:v=float(m.text.replace(",","."));assert 30<=v<=300
    except:await m.answer("30–300 kg oralig‘ida kiriting.");return
    async with SessionFactory() as s:
        u=await get_user(s,m.from_user.id);await add_weight(s,u,v)
    await state.clear();await m.answer("🎉 Vazn yangilandi. Davom eting!")
