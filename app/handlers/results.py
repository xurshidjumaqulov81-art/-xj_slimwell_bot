from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    Message,
)

from app.database.crud import (
    add_weight,
    get_user,
    get_weight_history,
    update_user,
)
from app.database.db import SessionFactory
from app.keyboards import results_menu
from app.services.health import (
    calculate_remaining_weight,
    get_bmi_plan,
)
from app.services.results_visuals import (
    create_progress_bar,
    create_weight_chart,
)
from app.states import HabitInput


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
        "📈 Natijalar",
        "📈 Результаты",
    })
)
async def results_section(
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

    remaining_weight = calculate_remaining_weight(
        user,
        metrics,
    )

    if language == "ru":
        title = "📈 РЕЗУЛЬТАТЫ"

        body = (
            f"👤 <b>{user.name}</b>\n"
            f"⚖️ Текущий вес: "
            f"<b>{user.current_weight_kg:g} кг</b>\n"
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Категория: <b>{plan['title']}</b>\n\n"
        )

        if remaining_weight > 0:
            body += (
                "🎯 Для достижения здорового веса:\n"
                f"Необходимо снизить ещё "
                f"<b>{remaining_weight} кг</b>.\n\n"
            )
        else:
            body += (
                "💚 Ваш вес находится "
                "в здоровом диапазоне.\n\n"
            )

        body += (
            "Выберите нужный раздел."
        )
    else:
        title = "📈 NATIJALAR"

        body = (
            f"👤 <b>{user.name}</b>\n"
            f"⚖️ Hozirgi vazn: "
            f"<b>{user.current_weight_kg:g} kg</b>\n"
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Holat: <b>{plan['title']}</b>\n\n"
        )

        if remaining_weight > 0:
            body += (
                "🎯 Sog‘lom vaznga erishish uchun:\n"
                f"Siz yana <b>{remaining_weight} kg</b> "
                "vazn tashlashingiz kerak.\n\n"
            )
        else:
            body += (
                "💚 Vazningiz sog‘lom oraliqda.\n\n"
            )

        body += (
            "Kerakli bo‘limni tanlang."
        )

    await message.answer(
        card(
            title,
            body,
        ),
        reply_markup=results_menu(
            language
        ),
    )


@router.callback_query(
    F.data == "result:add"
)
async def start_weight_input(
    callback: CallbackQuery,
    state: FSMContext,
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

    await state.clear()
    await state.set_state(
        HabitInput.weight
    )

    await callback.message.answer(
        (
            "⚖️ Bugungi vazningizni kilogrammda kiriting.\n\n"
            "Masalan: <b>105.5</b>"
            if language == "uz"
            else
            "⚖️ Введите сегодняшний вес в килограммах.\n\n"
            "Например: <b>105.5</b>"
        )
    )

    await callback.answer()


@router.message(
    HabitInput.weight
)
async def save_today_weight(
    message: Message,
    state: FSMContext,
) -> None:
    user = await load_user(
        message.from_user.id,
    )

    if user is None:
        await state.clear()

        await message.answer(
            "Profil topilmadi. / Профиль не найден."
        )
        return

    language = user.language or "uz"

    try:
        weight = float(
            (message.text or "")
            .strip()
            .replace(",", ".")
        )

        if not 30 <= weight <= 300:
            raise ValueError

    except (TypeError, ValueError):
        await message.answer(
            (
                "Vaznni 30–300 kg oralig‘ida kiriting."
                if language == "uz"
                else
                "Введите вес от 30 до 300 кг."
            )
        )
        return

    old_weight = float(
        user.current_weight_kg
    )

    async with SessionFactory() as session:
        database_user = await get_user(
            session,
            message.from_user.id,
        )

        if database_user is None:
            await state.clear()

            await message.answer(
                "Profil topilmadi. / Профиль не найден."
            )
            return

        await update_user(
            session,
            message.from_user.id,
            current_weight_kg=weight,
        )

        await add_weight(
            session,
            database_user.id,
            weight,
        )

    await state.clear()

    difference = round(
        weight - old_weight,
        1,
    )

    if language == "ru":
        if difference < 0:
            result_text = (
                f"📉 Изменение: "
                f"<b>−{abs(difference):g} кг</b>"
            )
        elif difference > 0:
            result_text = (
                f"📈 Изменение: "
                f"<b>+{difference:g} кг</b>"
            )
        else:
            result_text = (
                "➖ Вес не изменился."
            )

        body = (
            f"⚖️ Новый вес: "
            f"<b>{weight:g} кг</b>\n\n"
            f"{result_text}\n\n"
            "🌿 Продолжайте двигаться к своей цели."
        )

        title = "✅ ВЕС СОХРАНЁН"
    else:
        if difference < 0:
            result_text = (
                f"📉 O‘zgarish: "
                f"<b>−{abs(difference):g} kg</b>"
            )
        elif difference > 0:
            result_text = (
                f"📈 O‘zgarish: "
                f"<b>+{difference:g} kg</b>"
            )
        else:
            result_text = (
                "➖ Vazn o‘zgarmadi."
            )

        body = (
            f"⚖️ Yangi vazn: "
            f"<b>{weight:g} kg</b>\n\n"
            f"{result_text}\n\n"
            "🌿 Maqsadingiz sari davom eting."
        )

        title = "✅ VAZN SAQLANDI"

    await message.answer(
        card(
            title,
            body,
        ),
        reply_markup=results_menu(
            language
        ),
    )


@router.callback_query(
    F.data == "result:history"
)
async def show_weight_history(
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

    async with SessionFactory() as session:
        records = await get_weight_history(
            session,
            user.id,
        )

    # CRUD tarixni yangidan eskiga qaytaradi.
    # Grafik uchun eski yozuvdan yangi yozuvga o‘giramiz.
    chronological_records = list(
        reversed(records)
    )

    if not chronological_records:
        await callback.message.answer(
            (
                "Hali vazn tarixi mavjud emas."
                if language == "uz"
                else
                "История веса пока отсутствует."
            ),
            reply_markup=results_menu(
                language
            ),
        )

        await callback.answer()
        return

    try:
        chart_path = create_weight_chart(
            records=chronological_records,
            current_weight=float(
                user.current_weight_kg
            ),
            normal_max_weight=(
                metrics.normal_max_weight
            ),
            ideal_weight=(
                metrics.ideal_weight
            ),
            language=language,
        )
    except Exception:
        chart_path = None

    recent_records = list(
        reversed(
            chronological_records[-10:]
        )
    )

    history_lines: list[str] = []

    for record in recent_records:
        history_lines.append(
            f"• {record.recorded_at:%d.%m.%Y}: "
            f"<b>{record.weight_kg:g} "
            f"{'кг' if language == 'ru' else 'kg'}</b>"
        )

    if language == "ru":
        title = "📈 ДИНАМИКА ВЕСА"
        body = (
            "Последние записи:\n\n"
            + "\n".join(history_lines)
        )
    else:
        title = "📈 VAZN DINAMIKASI"
        body = (
            "Oxirgi yozuvlar:\n\n"
            + "\n".join(history_lines)
        )

    if chart_path is not None:
        await callback.message.answer_photo(
            photo=FSInputFile(
                chart_path
            ),
            caption=card(
                title,
                body,
            ),
            reply_markup=results_menu(
                language
            ),
        )
    else:
        await callback.message.answer(
            card(
                title,
                body,
            ),
            reply_markup=results_menu(
                language
            ),
        )

    await callback.answer()


@router.callback_query(
    F.data == "result:goal"
)
async def show_goal_progress(
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

    async with SessionFactory() as session:
        records = await get_weight_history(
            session,
            user.id,
        )

    chronological_records = list(
        reversed(records)
    )

    if chronological_records:
        start_weight = float(
            chronological_records[0].weight_kg
        )
    else:
        start_weight = float(
            user.current_weight_kg
        )

    current_weight = float(
        user.current_weight_kg
    )

    # Maqsad sifatida sog‘lom vazn oralig‘ining
    # yuqori chegarasi olinadi.
    target_weight = float(
        metrics.normal_max_weight
    )

    remaining_weight = max(
        round(
            current_weight - target_weight,
            1,
        ),
        0,
    )

    lost_weight = round(
        start_weight - current_weight,
        1,
    )

    try:
        progress_path = create_progress_bar(
            current_weight=current_weight,
            start_weight=start_weight,
            target_weight=target_weight,
            language=language,
        )
    except Exception:
        progress_path = None

    if language == "ru":
        title = "🎯 ДО ЦЕЛИ"

        body = (
            f"🚩 Начальный вес: "
            f"<b>{start_weight:g} кг</b>\n"
            f"⚖️ Текущий вес: "
            f"<b>{current_weight:g} кг</b>\n"
            f"✅ Граница здорового веса: "
            f"<b>{target_weight:g} кг</b>\n\n"
        )

        if lost_weight > 0:
            body += (
                f"📉 Уже снижено: "
                f"<b>{lost_weight:g} кг</b>\n"
            )

        if remaining_weight > 0:
            body += (
                f"🎯 Осталось до здорового веса: "
                f"<b>{remaining_weight:g} кг</b>"
            )
        else:
            body += (
                "💚 Вы достигли здорового диапазона веса."
            )
    else:
        title = "🎯 MAQSADGACHA QOLDI"

        body = (
            f"🚩 Boshlang‘ich vazn: "
            f"<b>{start_weight:g} kg</b>\n"
            f"⚖️ Hozirgi vazn: "
            f"<b>{current_weight:g} kg</b>\n"
            f"✅ Sog‘lom vazn chegarasi: "
            f"<b>{target_weight:g} kg</b>\n\n"
        )

        if lost_weight > 0:
            body += (
                f"📉 Hozirgacha kamaygan: "
                f"<b>{lost_weight:g} kg</b>\n"
            )

        if remaining_weight > 0:
            body += (
                f"🎯 Sog‘lom vazngacha qolgan: "
                f"<b>{remaining_weight:g} kg</b>"
            )
        else:
            body += (
                "💚 Siz sog‘lom vazn oralig‘iga erishdingiz."
            )

    if progress_path is not None:
        await callback.message.answer_photo(
            photo=FSInputFile(
                progress_path
            ),
            caption=card(
                title,
                body,
            ),
            reply_markup=results_menu(
                language
            ),
        )
    else:
        await callback.message.answer(
            card(
                title,
                body,
            ),
            reply_markup=results_menu(
                language
            ),
        )

    await callback.answer()


@router.callback_query(
    F.data == "result:today"
)
async def show_today_result(
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

    if language == "ru":
        title = "📊 ТЕКУЩИЙ РЕЗУЛЬТАТ"

        body = (
            f"⚖️ Вес: "
            f"<b>{user.current_weight_kg:g} кг</b>\n"
            f"📊 BMI: "
            f"<b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Категория: "
            f"<b>{plan['title']}</b>\n"
            f"⭐ Идеальный вес: "
            f"<b>{metrics.ideal_weight:g} кг</b>\n\n"
        )

        if remaining_weight > 0:
            body += (
                "Для достижения здорового веса "
                f"необходимо снизить ещё "
                f"<b>{remaining_weight:g} кг</b>."
            )
        else:
            body += (
                "💚 Вес находится в здоровом диапазоне."
            )
    else:
        title = "📊 HOZIRGI NATIJA"

        body = (
            f"⚖️ Vazn: "
            f"<b>{user.current_weight_kg:g} kg</b>\n"
            f"📊 BMI: "
            f"<b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Holat: "
            f"<b>{plan['title']}</b>\n"
            f"⭐ Ideal vazn: "
            f"<b>{metrics.ideal_weight:g} kg</b>\n\n"
        )

        if remaining_weight > 0:
            body += (
                "Sog‘lom vaznga erishish uchun "
                f"siz yana <b>{remaining_weight:g} kg</b> "
                "vazn tashlashingiz kerak."
            )
        else:
            body += (
                "💚 Vazningiz sog‘lom oraliqda."
            )

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=results_menu(
            language
        ),
    )

    await callback.answer()
