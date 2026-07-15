from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.content import TRANSLATIONS
from app.keyboards import language_menu, main_menu
from app.states import Onboarding


router = Router()


@router.message(CommandStart())
async def start_command(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await state.set_state(Onboarding.language)

    await message.answer(
        (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<b>✨ XJ SLIMWELL</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Xush kelibsiz! / Добро пожаловать!\n\n"
            "Davom etish uchun tilni tanlang.\n"
            "Выберите язык, чтобы продолжить."
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

    await state.update_data(language=language)

    text = TRANSLATIONS[language]

    await callback.message.edit_text(
        (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<b>✅ XJ SLIMWELL</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{text['welcome']}"
        )
    )

    await callback.message.answer(
        text["enter_personal_id"],
    )

    await state.set_state(Onboarding.personal_id)
    await callback.answer()


@router.message(Onboarding.personal_id)
async def temporary_personal_id_handler(
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

    await state.update_data(
        personal_id=personal_id,
    )

    await message.answer(
        (
            f"✅ ID: <b>{personal_id}</b>\n\n"
            "1-bosqich muvaffaqiyatli ishladi."
            if language == "uz"
            else
            f"✅ ID: <b>{personal_id}</b>\n\n"
            "Первый этап успешно работает."
        ),
        reply_markup=main_menu(language),
    )

    await state.clear()
