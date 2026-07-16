from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import get_settings
from app.database.crud import (
    get_user_by_personal_id,
    get_users_count,
)
from app.database.db import SessionFactory
from app.keyboards import admin_menu
from app.services.health import get_bmi_plan
from app.states import AdminState


router = Router()
settings = get_settings()


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


def is_admin(
    telegram_id: int,
) -> bool:
    return telegram_id in settings.admins


@router.message(
    F.text == "🛡 Admin panel"
)
async def open_admin_panel(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()

    if not is_admin(
        message.from_user.id
    ):
        await message.answer(
            "Bu bo‘lim faqat admin uchun."
        )
        return

    async with SessionFactory() as session:
        users_count = await get_users_count(
            session
        )

    await message.answer(
        card(
            "🛡 ADMIN PANEL",
            (
                f"👥 Jami foydalanuvchilar: "
                f"<b>{users_count}</b>\n\n"
                "Kerakli amalni tanlang."
            ),
        ),
        reply_markup=admin_menu(),
    )


@router.callback_query(
    F.data == "admin:stats"
)
async def admin_statistics(
    callback: CallbackQuery,
) -> None:
    if not is_admin(
        callback.from_user.id
    ):
        await callback.answer(
            "Ruxsat yo‘q.",
            show_alert=True,
        )
        return

    async with SessionFactory() as session:
        users_count = await get_users_count(
            session
        )

    await callback.message.answer(
        card(
            "📊 STATISTIKA",
            (
                f"👥 Jami foydalanuvchilar: "
                f"<b>{users_count}</b>"
            ),
        ),
        reply_markup=admin_menu(),
    )

    await callback.answer()


@router.callback_query(
    F.data == "admin:search"
)
async def start_admin_search(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not is_admin(
        callback.from_user.id
    ):
        await callback.answer(
            "Ruxsat yo‘q.",
            show_alert=True,
        )
        return

    await state.clear()
    await state.set_state(
        AdminState.search
    )

    await callback.message.answer(
        (
            "🔍 Foydalanuvchining 7 xonali "
            "shaxsiy ID raqamini kiriting.\n\n"
            "Masalan: <b>0012345</b>"
        )
    )

    await callback.answer()


@router.message(
    AdminState.search
)
async def search_user_by_id(
    message: Message,
    state: FSMContext,
) -> None:
    if not is_admin(
        message.from_user.id
    ):
        await state.clear()
        return

    personal_id = (
        message.text or ""
    ).strip()

    if not (
        personal_id.isdigit()
        and len(personal_id) == 7
    ):
        await message.answer(
            (
                "ID aynan 7 ta raqamdan "
                "iborat bo‘lishi kerak."
            )
        )
        return

    async with SessionFactory() as session:
        user = await get_user_by_personal_id(
            session,
            personal_id,
        )

    if user is None:
        await message.answer(
            card(
                "🔍 QIDIRUV NATIJASI",
                (
                    f"<b>{personal_id}</b> ID bilan "
                    "foydalanuvchi topilmadi."
                ),
            ),
            reply_markup=admin_menu(),
        )

        await state.clear()
        return

    try:
        metrics, plan = get_bmi_plan(
            user,
            user.language or "uz",
        )

        bmi_text = f"{metrics.bmi:.2f}"
        category_text = str(
            plan["title"]
        )
    except ValueError:
        bmi_text = "—"
        category_text = "Profil to‘liq emas"

    registered_at = (
        user.registered_at.strftime(
            "%d.%m.%Y %H:%M"
        )
        if user.registered_at
        else "—"
    )

    last_active_at = (
        user.last_active_at.strftime(
            "%d.%m.%Y %H:%M"
        )
        if user.last_active_at
        else "—"
    )

    body = (
        f"🆔 Shaxsiy ID: "
        f"<b>{user.personal_id or '—'}</b>\n"
        f"👤 Ism: <b>{user.name or '—'}</b>\n"
        f"📱 Telegram ID: "
        f"<b>{user.telegram_id}</b>\n"
        f"🎂 Yosh: <b>{user.age or '—'}</b>\n"
        f"📏 Bo‘y: "
        f"<b>{user.height_cm or '—'} sm</b>\n"
        f"⚖️ Vazn: "
        f"<b>{user.current_weight_kg or '—'} kg</b>\n"
        f"📊 BMI: <b>{bmi_text}</b>\n"
        f"🎯 Holat: <b>{category_text}</b>\n\n"
        f"📅 Ro‘yxatdan o‘tgan:\n"
        f"<b>{registered_at}</b>\n\n"
        f"🕒 Oxirgi faollik:\n"
        f"<b>{last_active_at}</b>"
    )

    await message.answer(
        card(
            "👤 FOYDALANUVCHI",
            body,
        ),
        reply_markup=admin_menu(),
    )

    await state.clear()

