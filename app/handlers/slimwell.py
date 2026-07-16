from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    Message,
)

from app.config import ASSETS_DIR
from app.content import PRODUCT_CONTENT
from app.database.crud import get_user
from app.database.db import SessionFactory
from app.keyboards import slimwell_menu
from app.services.health import get_bmi_plan


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


def find_first_existing(
    paths: list[Path],
) -> Path | None:
    for path in paths:
        if path.exists() and path.is_file():
            return path

    return None


def get_product_image() -> Path | None:
    return find_first_existing(
        [
            ASSETS_DIR / "product" / "slimwell.png",
            ASSETS_DIR / "product" / "slimwell.jpg",
            ASSETS_DIR / "product" / "package.png",
            ASSETS_DIR / "product.png",
            ASSETS_DIR / "slimwell.png",
        ]
    )


def get_certificate_files() -> list[tuple[str, Path]]:
    certificate_directory = (
        ASSETS_DIR / "certificates"
    )

    possible_files = [
        (
            "🏅 ISO 22000",
            certificate_directory / "iso22000.jpg",
        ),
        (
            "🏅 ISO 22000",
            certificate_directory / "iso22000.png",
        ),
        (
            "🏭 GMP",
            certificate_directory / "gmp.jpg",
        ),
        (
            "🏭 GMP",
            certificate_directory / "gmp.png",
        ),
        (
            "🛡 HACCP",
            certificate_directory / "haccp.jpg",
        ),
        (
            "🛡 HACCP",
            certificate_directory / "haccp.png",
        ),
        (
            "🌿 HALAL",
            certificate_directory / "halal.jpg",
        ),
        (
            "🌿 HALAL",
            certificate_directory / "halal.png",
        ),
        (
            "🌍 FSSAI",
            certificate_directory / "fssai.jpg",
        ),
        (
            "🌍 FSSAI",
            certificate_directory / "fssai.png",
        ),
    ]

    result: list[tuple[str, Path]] = []
    used_names: set[str] = set()

    for title, path in possible_files:
        if (
            path.exists()
            and path.is_file()
            and title not in used_names
        ):
            result.append(
                (
                    title,
                    path,
                )
            )
            used_names.add(title)

    combined_file = find_first_existing(
        [
            ASSETS_DIR / "certificates.png",
            certificate_directory
            / "certificates.png",
            certificate_directory
            / "all_certificates.jpg",
        ]
    )

    if combined_file is not None:
        return [
            (
                "🏅 XJ SlimWell sertifikatlari",
                combined_file,
            )
        ]

    return result


@router.message(
    F.text == "💊 SlimWell"
)
async def slimwell_section(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()

    async with SessionFactory() as session:
        user = await get_user(
            session,
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
            f"🎯 Категория: "
            f"<b>{plan['title']}</b>\n\n"
            "Здесь вы найдёте режим приёма, "
            "состав, сертификаты и рекомендации."
        )
    else:
        title = "💊 XJ SLIMWELL"

        body = (
            f"👤 <b>{user.name}</b>\n"
            f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
            f"🎯 Holat: "
            f"<b>{plan['title']}</b>\n\n"
            "Bu bo‘limda mahsulotning qabul "
            "tartibi, tarkibi, sertifikatlari "
            "va tavsiyalarini ko‘rishingiz mumkin."
        )

    product_image = get_product_image()

    if product_image is not None:
        await message.answer_photo(
            photo=FSInputFile(product_image),
            caption=card(
                title,
                body,
            ),
            reply_markup=slimwell_menu(
                language
            ),
        )
    else:
        await message.answer(
            card(
                title,
                body,
            ),
            reply_markup=slimwell_menu(
                language
            ),
        )


@router.callback_query(
    F.data.in_({
        "slim:usage",
        "slim:plan",
    })
)
async def slimwell_usage(
    callback: CallbackQuery,
) -> None:
    async with SessionFactory() as session:
        user = await get_user(
            session,
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
            "Profil ma’lumotlari to‘liq emas.",
            show_alert=True,
        )
        return

    if user.age is not None and user.age < 18:
        if language == "ru":
            body = (
                f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
                f"🎯 Категория: "
                f"<b>{plan['title']}</b>\n\n"
                "Для пользователей младше 18 лет "
                "бот не назначает количество капсул.\n\n"
                "Используйте продукт только согласно "
                "официальной инструкции и с участием "
                "родителя или ответственного взрослого."
            )

            title = "⏰ РЕЖИМ ПРИЁМА"
        else:
            body = (
                f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
                f"🎯 Holat: "
                f"<b>{plan['title']}</b>\n\n"
                "18 yoshgacha bo‘lgan foydalanuvchiga "
                "bot kapsula miqdorini belgilamaydi.\n\n"
                "Mahsulotdan faqat rasmiy yo‘riqnoma "
                "va ota-ona yoki mas’ul katta ishtirokida "
                "foydalaning."
            )

            title = "⏰ QABUL QILISH TARTIBI"
    else:
        if language == "ru":
            body = (
                f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
                f"🎯 Категория: "
                f"<b>{plan['title']}</b>\n\n"
                "💊 <b>Размер порции по этикетке: "
                "3 капсулы</b>\n\n"
                "🌅 1 капсула перед завтраком\n"
                "☀️ 1 капсула перед обедом\n"
                "🌙 1 капсула перед ужином\n\n"
                "💧 Запивайте водой.\n"
                "📦 Не превышайте количество, "
                "указанное на официальной этикетке."
            )

            title = "⏰ РЕЖИМ ПРИЁМА"
        else:
            body = (
                f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
                f"🎯 Holat: "
                f"<b>{plan['title']}</b>\n\n"
                "💊 <b>Yorliqdagi porsiya miqdori: "
                "3 kapsula</b>\n\n"
                "🌅 1 kapsula — nonushtadan oldin\n"
                "☀️ 1 kapsula — tushlikdan oldin\n"
                "🌙 1 kapsula — kechki ovqatdan oldin\n\n"
                "💧 Suv bilan iching.\n"
                "📦 Rasmiy yorliqda ko‘rsatilgan "
                "miqdordan oshirmang."
            )

            title = "⏰ QABUL QILISH TARTIBI"

    await callback.message.answer(
        card(
            title,
            body,
        ),
        reply_markup=slimwell_menu(
            language
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data == "slim:about"
)
async def slimwell_about(
    callback: CallbackQuery,
) -> None:
    await send_product_content(
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
    await send_product_content(
        callback=callback,
        content_key="ingredients",
        uz_title="🧪 TARKIBI VA FOYDASI",
        ru_title="🧪 СОСТАВ",
    )


@router.callback_query(
    F.data == "slim:storage"
)
async def slimwell_storage(
    callback: CallbackQuery,
) -> None:
    await send_product_content(
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
    await send_product_content(
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
    await send_product_content(
        callback=callback,
        content_key="faq",
        uz_title="❓ TAVSIYALAR",
        ru_title="❓ РЕКОМЕНДАЦИИ",
    )


async def send_product_content(
    callback: CallbackQuery,
    content_key: str,
    uz_title: str,
    ru_title: str,
    include_product_image: bool = False,
) -> None:
    async with SessionFactory() as session:
        user = await get_user(
            session,
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

    body = PRODUCT_CONTENT[
        language
    ][content_key]

    product_image = (
        get_product_image()
        if include_product_image
        else None
    )

    if product_image is not None:
        await callback.message.answer_photo(
            photo=FSInputFile(
                product_image
            ),
            caption=card(
                title,
                body,
            ),
            reply_markup=slimwell_menu(
                language
            ),
        )
    else:
        await callback.message.answer(
            card(
                title,
                body,
            ),
            reply_markup=slimwell_menu(
                language
            ),
        )

    await callback.answer()


@router.callback_query(
    F.data == "slim:certs"
)
async def slimwell_certificates(
    callback: CallbackQuery,
) -> None:
    async with SessionFactory() as session:
        user = await get_user(
            session,
            callback.from_user.id,
        )

    if user is None:
        await callback.answer(
            "Profil topilmadi.",
            show_alert=True,
        )
        return

    language = user.language or "uz"
    certificate_files = (
        get_certificate_files()
    )

    if language == "ru":
        title = "🏅 СЕРТИФИКАТЫ"
        intro = (
            "ISO 22000 · GMP · HACCP · "
            "HALAL · FSSAI"
        )
    else:
        title = "🏅 SERTIFIKATLAR"
        intro = (
            "ISO 22000 · GMP · HACCP · "
            "HALAL · FSSAI"
        )

    if not certificate_files:
        await callback.message.answer(
            card(
                title,
                intro,
            ),
            reply_markup=slimwell_menu(
                language
            ),
        )

        await callback.answer()
        return

    await callback.message.answer(
        card(
            title,
            intro,
        )
    )

    for certificate_title, file_path in (
        certificate_files
    ):
        await callback.message.answer_photo(
            photo=FSInputFile(
                file_path
            ),
            caption=certificate_title,
        )

    await callback.message.answer(
        (
            "Kerakli bo‘limni tanlang."
            if language == "uz"
            else
            "Выберите нужный раздел."
        ),
        reply_markup=slimwell_menu(
            language
        ),
    )

    await callback.answer()
