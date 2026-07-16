from pathlib import Path

from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    Message,
)

from app.config import EXERCISES_ASSETS_DIR
from app.database.crud import (
    add_exercise,
    get_user,
)
from app.database.db import SessionFactory
from app.keyboards import (
    exercise_done_menu,
    main_menu,
)
from app.services.health import get_bmi_plan


router = Router()

TELEGRAM_PHOTO_LIMIT = 10 * 1024 * 1024


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


def first_existing(
    paths: list[Path],
) -> Path | None:
    for path in paths:
        if (
            path.exists()
            and path.is_file()
        ):
            return path

    return None


def valid_photo(
    path: Path | None,
) -> bool:
    if path is None:
        return False

    try:
        return (
            path.exists()
            and path.is_file()
            and path.stat().st_size
            <= TELEGRAM_PHOTO_LIMIT
        )
    except OSError:
        return False


def exercise_image(
    name: str,
) -> Path | None:
    aliases = {
        "walking": [
            "walking.png",
            "walk.png",
            "walking.jpg",
            "walk.jpg",
        ],
        "squat": [
            "squat.png",
            "squat.jpg",
        ],
        "plank": [
            "plank.png",
            "plank.jpg",
        ],
    }

    filenames = aliases.get(
        name,
        [],
    )

    return first_existing(
        [
            EXERCISES_ASSETS_DIR
            / filename
            for filename in filenames
        ]
    )


def get_exercises(
    category_key: str,
    language: str,
) -> list[dict[str, object]]:
    if language == "ru":
        if category_key in {
            "obesity_2",
            "obesity_3",
        }:
            return [
                {
                    "title": "Спокойная ходьба",
                    "description": (
                        "Ходите в удобном темпе "
                        "без резких ускорений."
                    ),
                    "amount": "15–20 минут",
                    "minutes": 18,
                    "image": "walking",
                },
                {
                    "title": "Приседание к стулу",
                    "description": (
                        "Медленно садитесь на стул "
                        "и спокойно вставайте."
                    ),
                    "amount": "2 подхода по 8 раз",
                    "minutes": 8,
                    "image": "squat",
                },
                {
                    "title": "Планка у стены",
                    "description": (
                        "Упритесь руками в стену "
                        "и держите корпус ровно."
                    ),
                    "amount": "3 раза по 20 секунд",
                    "minutes": 4,
                    "image": "plank",
                },
            ]

        if category_key == "obesity_1":
            return [
                {
                    "title": "Ходьба",
                    "description": (
                        "Ходите в среднем темпе."
                    ),
                    "amount": "20–30 минут",
                    "minutes": 25,
                    "image": "walking",
                },
                {
                    "title": "Приседание к стулу",
                    "description": (
                        "Держите спину ровно "
                        "и двигайтесь плавно."
                    ),
                    "amount": "3 подхода по 10 раз",
                    "minutes": 10,
                    "image": "squat",
                },
                {
                    "title": "Планка у стены",
                    "description": (
                        "Не задерживайте дыхание."
                    ),
                    "amount": "3 раза по 25 секунд",
                    "minutes": 5,
                    "image": "plank",
                },
            ]

        return [
            {
                "title": "Быстрая ходьба",
                "description": (
                    "Поддерживайте удобный "
                    "и активный темп."
                ),
                "amount": "30 минут",
                "minutes": 30,
                "image": "walking",
            },
            {
                "title": "Приседания",
                "description": (
                    "Держите спину ровно, "
                    "колени направляйте вперёд."
                ),
                "amount": "3 подхода по 12 раз",
                "minutes": 12,
                "image": "squat",
            },
            {
                "title": "Планка",
                "description": (
                    "Держите корпус ровно "
                    "и спокойно дышите."
                ),
                "amount": "3 раза по 30 секунд",
                "minutes": 5,
                "image": "plank",
            },
        ]

    if category_key in {
        "obesity_2",
        "obesity_3",
    }:
        return [
            {
                "title": "Sekin yurish",
                "description": (
                    "O‘zingizga qulay tezlikda, "
                    "keskin zo‘riqmasdan yuring."
                ),
                "amount": "15–20 daqiqa",
                "minutes": 18,
                "image": "walking",
            },
            {
                "title": "Stulga o‘tirib-turish",
                "description": (
                    "Stulga sekin o‘tiring va "
                    "tayanch bilan qayta turing."
                ),
                "amount": "2 set × 8 marta",
                "minutes": 8,
                "image": "squat",
            },
            {
                "title": "Devorga plank",
                "description": (
                    "Qo‘llarni devorga tirab, "
                    "gavdani tekis ushlang."
                ),
                "amount": "3 × 20 soniya",
                "minutes": 4,
                "image": "plank",
            },
        ]

    if category_key == "obesity_1":
        return [
            {
                "title": "Yurish",
                "description": (
                    "O‘rtacha tezlikda muntazam yuring."
                ),
                "amount": "20–30 daqiqa",
                "minutes": 25,
                "image": "walking",
            },
            {
                "title": "Stulga o‘tirib-turish",
                "description": (
                    "Belni tik tutib, harakatni "
                    "sekin bajaring."
                ),
                "amount": "3 set × 10 marta",
                "minutes": 10,
                "image": "squat",
            },
            {
                "title": "Devorga plank",
                "description": (
                    "Nafasni ushlab qolmang."
                ),
                "amount": "3 × 25 soniya",
                "minutes": 5,
                "image": "plank",
            },
        ]

    return [
        {
            "title": "Tez yurish",
            "description": (
                "Qulay va faol tezlikda yuring."
            ),
            "amount": "30 daqiqa",
            "minutes": 30,
            "image": "walking",
        },
        {
            "title": "Squat",
            "description": (
                "Belni tik tuting va tizzalarni "
                "oldinga yo‘naltiring."
            ),
            "amount": "3 set × 12 marta",
            "minutes": 12,
            "image": "squat",
        },
        {
            "title": "Plank",
            "description": (
                "Gavdani tekis tuting va "
                "tinch nafas oling."
            ),
            "amount": "3 × 30 soniya",
            "minutes": 5,
            "image": "plank",
        },
    ]


@router.message(
    F.text.in_({
        "💪 Mashqlar",
        "💪 Упражнения",
    })
)
async def exercises_section(
    message: Message,
) -> None:
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

    exercises = get_exercises(
        metrics.category_key,
        language,
    )

    if language == "ru":
        await message.answer(
            card(
                "💪 УПРАЖНЕНИЯ",
                (
                    f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
                    f"🎯 Категория: "
                    f"<b>{plan['title']}</b>\n\n"
                    "Для вас подготовлены 3 домашних "
                    "упражнения.\n\n"
                    "Выполняйте движения плавно "
                    "и в удобном темпе."
                ),
            )
        )
    else:
        await message.answer(
            card(
                "💪 UY MASHQLARI",
                (
                    f"📊 BMI: <b>{metrics.bmi:.2f}</b>\n"
                    f"🎯 Holat: "
                    f"<b>{plan['title']}</b>\n\n"
                    "Siz uchun uy sharoitiga mos "
                    "3 ta mashq tayyorlandi.\n\n"
                    "Harakatlarni sekin va o‘zingizga "
                    "qulay tezlikda bajaring."
                ),
            )
        )

    for index, exercise in enumerate(
        exercises,
        start=1,
    ):
        image = exercise_image(
            str(exercise["image"])
        )

        if language == "ru":
            title = (
                f"{index}️⃣ {exercise['title']}"
            )

            body = (
                f"📝 {exercise['description']}\n\n"
                f"⏱ <b>{exercise['amount']}</b>"
            )
        else:
            title = (
                f"{index}️⃣ {exercise['title']}"
            )

            body = (
                f"📝 {exercise['description']}\n\n"
                f"⏱ <b>{exercise['amount']}</b>"
            )

        if valid_photo(image):
            await message.answer_photo(
                photo=FSInputFile(image),
                caption=card(
                    title,
                    body,
                ),
                reply_markup=exercise_done_menu(
                    exercise_index=index,
                    language=language,
                ),
            )
        else:
            await message.answer(
                card(
                    title,
                    body,
                ),
                reply_markup=exercise_done_menu(
                    exercise_index=index,
                    language=language,
                ),
            )


@router.callback_query(
    F.data.startswith("exercise:done:")
)
async def exercise_done(
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

        exercises = get_exercises(
            metrics.category_key,
            language,
        )

        index = int(
            callback.data.rsplit(
                ":",
                1,
            )[1]
        )

        exercise = exercises[
            index - 1
        ]

    except (
        ValueError,
        IndexError,
        TypeError,
    ):
        await callback.answer(
            (
                "Mashq topilmadi."
                if language == "uz"
                else
                "Упражнение не найдено."
            ),
            show_alert=True,
        )
        return

    async with SessionFactory() as session:
        await add_exercise(
            session=session,
            user_id=user.id,
            title=str(
                exercise["title"]
            ),
            minutes=int(
                exercise["minutes"]
            ),
        )

    await callback.answer(
        (
            "Mashq bajarildi va saqlandi ✅"
            if language == "uz"
            else
            "Упражнение выполнено и сохранено ✅"
        ),
        show_alert=True,
    )


@router.callback_query(
    F.data == "home"
)
async def exercises_home(
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

    await callback.message.answer(
        (
            "Kerakli bo‘limni tanlang."
            if language == "uz"
            else
            "Выберите нужный раздел."
        ),
        reply_markup=main_menu(
            language,
        ),
    )

    await callback.answer()
