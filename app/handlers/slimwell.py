from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.config import ASSETS_DIR
from app.content import PRODUCT_CONTENT
from app.database.crud import get_user
from app.database.db import SessionFactory
from app.keyboards import slimwell_menu
from app.services.health import get_bmi_plan


router = Router()

TELEGRAM_PHOTO_LIMIT = 10 * 1024 * 1024

# Bu qiymat mahsulotning tasdiqlangan rasmiy yorlig‘idan olinadi.
MAX_DAILY_CAPSULES = 3


def card(title: str, body: str) -> str:
    return (
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>{title}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{body}"
    )


async def load_user(telegram_id: int):
    async with SessionFactory() as session:
        return await get_user(
            session,
            telegram_id,
        )


def first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists() and path.is_file():
            return path

    return None


def is_valid_photo(path: Path | None) -> bool:
    if path is None:
        return False

    try:
        return (
            path.exists()
            and path.is_file()
            and path.stat().st_size <= TELEGRAM_PHOTO_LIMIT
        )
    except OSError:
        return False


def get_product_image() -> Path | None:
    return first_existing(
        [
            ASSETS_DIR / "product" / "slimwell_about.jpg",
            ASSETS_DIR / "product" / "slimwell_about.png",
            ASSETS_DIR / "product" / "slimwell.jpg",
            ASSETS_DIR / "product" / "slimwell.png",
            ASSETS_DIR / "product" / "product.jpg",
            ASSETS_DIR / "product" / "product.png",
            ASSETS_DIR / "product.png",
        ]
    )


def get_certificate_images() -> list[tuple[str, Path]]:
    directory = ASSETS_DIR / "certificates"

    possible_files = [
        (
            "🏅 ISO 22000",
            [
                directory / "iso22000.jpg",
                directory / "iso22000.png",
                directory / "iso_22000.jpg",
                directory / "iso_22000.png",
            ],
        ),
        (
            "🏭 GMP",
            [
                directory / "gmp.jpg",
                directory / "gmp.png",
            ],
        ),
        (
            "🛡 HACCP",
            [
                directory / "haccp.jpg",
                directory / "haccp.png",
            ],
        ),
        (
            "🌿 HALAL",
            [
                directory / "halal.jpg",
                directory / "halal.png",
            ],
        ),
        (
            "🌍 FSSAI",
            [
                directory / "fssai.jpg",
                directory / "fssai.png",
            ],
        ),
    ]

    images: list[tuple[str, Path]] = []

    combined = first_existing(
        [
            directory / "certificates.jpg",
            directory / "certificates.png",
            directory / "all_certificates.jpg",
            directory / "all_certificates.png",
            ASSETS_DIR / "certificates.jpg",
            ASSETS_DIR / "certificates.png",
        ]
    )

    if is_valid_photo(combined):
        return [
            (
                "🏅 ISO 22000 · GMP · HACCP · HALAL · FSSAI",
                combined,
            )
        ]

    for title, paths in possible_files:
        image = first_existing(paths)

        if is_valid_photo(image):
            images.append(
                (
                    title,
                    image,
                )
            )

    return images


def get_personal_capsules(
    bmi: float,
    age: int | None,
) -> int | None:
    if age is None or age < 18:
        return None

    # Tasdiqlangan ichish tartibingizga mos diapazon.
    # Hech qachon MAX_DAILY_CAPSULES dan oshmaydi.
    if bmi < 25:
        return 2

    if bmi < 30:
        return 2

    return min(
        3,
        MAX_DAILY_CAPSULES,
    )


def get_schedule_uz(capsules: int) -> str:
    if capsules == 1:
        return (
            "🌅 1 kapsula — nonushtadan oldin"
        )

    if capsules == 2:
        return (
            "🌅 1 kapsula — nonushtadan oldin\n"
            "☀️ 1 kapsula — tushlikdan oldin"
        )

    return (
        "🌅 1 kapsula — nonushtadan oldin\n"
        "☀️ 1 kapsula — tushlikdan oldin\n"
        "🌙 1 kapsula — kechki ovqatdan oldin"
    )


def get_schedule_ru(capsules: int) -> str:
    if capsules == 1:
        return (
            "🌅 1 капсула — перед завтраком"
        )

    if capsules == 2:
        return (
            "🌅 1 капсула — перед завтраком\n"
            "☀️ 1 капсула — перед обедом"
        )

    return (
        "🌅 1 капсула — перед завтраком\n"
        "☀️ 1 капсула — перед обедом\n"
        "🌙 1 капсула — перед ужином"
    )


async def answer_with_optional_photo(
    message: Message,
    title: str,
    body: str,
    language: str,
    photo: Path | None = None,
) -> None:
    if is_valid_photo(photo):
        await message.answer_photo(
            photo=FSInputFile(photo),
            caption=card(
                title,
                body,
            ),
            reply_markup=slimwell_menu(language),
        )
        return

    await message.answer(
        card(
            title,
            body,
        ),
        reply_markup=slimwell_menu(language),
    )


@router.message(
    F.text == "💊 SlimWell"
)
async def slimwell_section(
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

    if language == "ru":
        title = "💊 XJ SLIMWELL"

        body = (
            f"👤 <b>{user.name}</b>\n"
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Категория: <b>{plan['title']}</b>\n\n"
            "Здесь вы найдёте информацию о продукте, "
            "способ применения, персональный режим, "
            "состав и сертификаты.\n\n"
            "Выберите нужный раздел."
        )
    else:
        title = "💊 XJ SLIMWELL"

        body = (
            f"👤 <b>{user.name}</b>\n"
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Holat: <b>{plan['title']}</b>\n\n"
            "Bu bo‘limda mahsulot haqida ma’lumot, "
            "qanday ichilishi, shaxsiy qabul rejasi, "
            "tarkibi va sertifikatlarini ko‘rishingiz mumkin.\n\n"
            "Kerakli bo‘limni tanlang."
        )

    await answer_with_optional_photo(
        message=message,
        title=title,
        body=body,
        language=language,
        photo=get_product_image(),
    )


@router.callback_query(
    F.data == "slim:usage"
)
async def slimwell_usage(
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

    if language == "ru":
        title = "⏰ КАК ПРИНИМАТЬ?"

        body = (
            "💊 Капсулы принимаются перед едой.\n\n"
            "🌅 Перед завтраком\n"
            "☀️ Перед обедом\n"
            "🌙 Перед ужином\n\n"
            "💧 Запивайте достаточным количеством воды.\n"
            "📦 Не превышайте количество, указанное "
            "на официальной этикетке."
        )
    else:
        title = "⏰ QANDAY ICHILADI?"

        body = (
            "💊 Kapsulalar ovqatdan oldin qabul qilinadi.\n\n"
            "🌅 Nonushtadan oldin\n"
            "☀️ Tushlikdan oldin\n"
            "🌙 Kechki ovqatdan oldin\n\n"
            "💧 Har safar yetarli miqdorda suv bilan iching.\n"
            "📦 Rasmiy yorliqda ko‘rsatilgan miqdordan oshirmang."
        )

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=slimwell_menu(language),
    )

    await callback.answer()


@router.callback_query(
    F.data == "slim:plan"
)
async def slimwell_plan(
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

    capsules = get_personal_capsules(
        bmi=metrics.bmi,
        age=user.age,
    )

    if capsules is None:
        if language == "ru":
            title = "📅 МОЙ РЕЖИМ ПРИЁМА"

            body = (
                f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
                f"🎯 Категория: <b>{plan['title']}</b>\n\n"
                "Для пользователей младше 18 лет "
                "бот не рассчитывает количество капсул."
            )
        else:
            title = "📅 MENING QABUL REJAM"

            body = (
                f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
                f"🎯 Holat: <b>{plan['title']}</b>\n\n"
                "18 yoshgacha bo‘lgan foydalanuvchi "
                "uchun bot kapsula miqdorini hisoblamaydi."
            )
    elif language == "ru":
        title = "📅 МОЙ РЕЖИМ ПРИЁМА"

        body = (
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Категория: <b>{plan['title']}</b>\n\n"
            f"💊 <b>Ваш режим: {capsules} капсулы в день</b>\n\n"
            f"{get_schedule_ru(capsules)}\n\n"
            "💧 Запивайте водой.\n"
            f"📦 Максимум по настройке продукта: "
            f"{MAX_DAILY_CAPSULES} капсулы."
        )
    else:
        title = "📅 MENING QABUL REJAM"

        body = (
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Holat: <b>{plan['title']}</b>\n\n"
            f"💊 <b>Siz uchun: kuniga {capsules} kapsula</b>\n\n"
            f"{get_schedule_uz(capsules)}\n\n"
            "💧 Har safar suv bilan iching.\n"
            f"📦 Mahsulot sozlamasidagi maksimal miqdor: "
            f"{MAX_DAILY_CAPSULES} kapsula."
        )

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=slimwell_menu(language),
    )

    await callback.answer()


@router.callback_query(
    F.data == "slim:about"
)
async def slimwell_about(
    callback: CallbackQuery,
) -> None:
    await send_content(
        callback=callback,
        content_key="about",
        uz_title="💎 MAHSULOT HAQIDA",
        ru_title="💎 О ПРОДУКТЕ",
        include_product_image=True,
    )


@router.callback_query(
    F.data == "slim:ingredients"
)
async def slimwell_ingredients(
    callback: CallbackQuery,
) -> None:
    await send_content(
        callback=callback,
        content_key="ingredients",
        uz_title="🧪 TARKIBI VA FOYDASI",
        ru_title="🧪 СОСТАВ И СВОЙСТВА",
    )


@router.callback_query(
    F.data == "slim:storage"
)
async def slimwell_storage(
    callback: CallbackQuery,
) -> None:
    await send_content(
        callback=callback,
        content_key="storage",
        uz_title="📦 SAQLASH SHARTLARI",
        ru_title="📦 УСЛОВИЯ ХРАНЕНИЯ",
    )


@router.callback_query(
    F.data == "slim:warnings"
)
async def slimwell_warnings(
    callback: CallbackQuery,
) -> None:
    await send_content(
        callback=callback,
        content_key="warnings",
        uz_title="💚 ESLATMA",
        ru_title="💚 НАПОМИНАНИЕ",
    )


@router.callback_query(
    F.data == "slim:faq"
)
async def slimwell_faq(
    callback: CallbackQuery,
) -> None:
    await send_content(
        callback=callback,
        content_key="faq",
        uz_title="❓ TAVSIYALAR",
        ru_title="❓ РЕКОМЕНДАЦИИ",
    )


async def send_content(
    callback: CallbackQuery,
    content_key: str,
    uz_title: str,
    ru_title: str,
    include_product_image: bool = False,
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

    title = (
        ru_title
        if language == "ru"
        else uz_title
    )

    try:
        body = PRODUCT_CONTENT[
            language
        ][content_key]
    except KeyError:
        body = (
            "Ma’lumot vaqtincha topilmadi."
            if language == "uz"
            else
            "Информация временно недоступна."
        )

    photo = (
        get_product_image()
        if include_product_image
        else None
    )

    await answer_with_optional_photo(
        message=callback.message,
        title=title,
        body=body,
        language=language,
        photo=photo,
    )

    await callback.answer()


@router.callback_query(
    F.data == "slim:certs"
)
async def slimwell_certificates(
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

    title = (
        "🏅 СЕРТИФИКАТЫ"
        if language == "ru"
        else "🏅 SERTIFIKATLAR"
    )

    names = (
        "ISO 22000 · GMP · HACCP · HALAL · FSSAI"
    )

    images = get_certificate_images()

    if not images:
        await callback.message.answer(
            card(
                title,
                names,
            ),
            reply_markup=slimwell_menu(language),
        )

        await callback.answer()
        return

    await callback.message.answer(
        card(
            title,
            names,
        )
    )

    for image_title, image_path in images:
        await callback.message.answer_photo(
            photo=FSInputFile(image_path),
            caption=image_title,
        )

    await callback.message.answer(
        (
            "Kerakli bo‘limni tanlang."
            if language == "uz"
            else
            "Выберите нужный раздел."
        ),
        reply_markup=slimwell_menu(language),
    )

    await callback.answer()
