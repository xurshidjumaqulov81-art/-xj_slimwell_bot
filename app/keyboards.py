from aiogram.types import (
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_menu(
    items: list[tuple[str, str]],
    columns: int = 1,
) -> InlineKeyboardMarkup:
    """
    Inline tugmalarni yaratadi.

    items:
        [
            ("Tugma nomi", "callback:data"),
            ...
        ]

    columns:
        Bir qatordagi tugmalar soni.
    """
    builder = InlineKeyboardBuilder()

    for text, callback_data in items:
        builder.button(
            text=text,
            callback_data=callback_data,
        )

    builder.adjust(columns)

    return builder.as_markup()


# =========================================================
# TIL TANLASH
# =========================================================

def language_menu() -> InlineKeyboardMarkup:
    return inline_menu(
        [
            (
                "🇺🇿 O‘zbekcha",
                "lang:uz",
            ),
            (
                "🇷🇺 Русский",
                "lang:ru",
            ),
        ],
        columns=2,
    )


# =========================================================
# ASOSIY MENYU
# =========================================================

def main_menu(
    language: str,
    is_admin: bool = False,
) -> ReplyKeyboardMarkup:
    """
    Asosiy ReplyKeyboard menyusi.

    Tugma matnlarini o‘zgartirmang:
    handlerlar aynan shu matnlar orqali ishlaydi.
    """

    if language == "ru":
        rows = [
            [
                KeyboardButton(
                    text="💊 SlimWell"
                ),
                KeyboardButton(
                    text="📊 Анализ тела"
                ),
            ],
            [
                KeyboardButton(
                    text="👤 Мой профиль"
                ),
                KeyboardButton(
                    text="🥗 Питание"
                ),
            ],
            [
                KeyboardButton(
                    text="📸 Анализ еды"
                ),
                KeyboardButton(
                    text="💧 Полезные привычки"
                ),
            ],
            [
                KeyboardButton(
                    text="💪 Упражнения"
                ),
                KeyboardButton(
                    text="📈 Результаты"
                ),
            ],
            [
                KeyboardButton(
                    text="🌐 Изменить язык"
                ),
            ],
        ]

    else:
        rows = [
            [
                KeyboardButton(
                    text="💊 SlimWell"
                ),
                KeyboardButton(
                    text="📊 Tana tahlili"
                ),
            ],
            [
                KeyboardButton(
                    text="👤 Mening profilim"
                ),
                KeyboardButton(
                    text="🥗 Shaxsiy ovqatlanish"
                ),
            ],
            [
                KeyboardButton(
                    text="📸 Ovqatni tahlil qilish"
                ),
                KeyboardButton(
                    text="💧 Sog‘lom odatlar"
                ),
            ],
            [
                KeyboardButton(
                    text="💪 Mashqlar"
                ),
                KeyboardButton(
                    text="📈 Natijalar"
                ),
            ],
            [
                KeyboardButton(
                    text="🌐 Tilni o‘zgartirish"
                ),
            ],
        ]

    if is_admin:
        rows.append(
            [
                KeyboardButton(
                    text="🛡 Admin panel"
                ),
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder=(
            "Kerakli bo‘limni tanlang"
            if language == "uz"
            else
            "Выберите нужный раздел"
        ),
    )


# =========================================================
# JINS TANLASH
# =========================================================

def gender_menu(
    language: str,
) -> InlineKeyboardMarkup:
    if language == "ru":
        items = [
            (
                "🚹 Мужчина",
                "gender:male",
            ),
            (
                "🚺 Женщина",
                "gender:female",
            ),
        ]
    else:
        items = [
            (
                "🚹 Erkak",
                "gender:male",
            ),
            (
                "🚺 Ayol",
                "gender:female",
            ),
        ]

    return inline_menu(
        items,
        columns=2,
    )


# =========================================================
# MAQSAD TANLASH
# =========================================================

def goal_menu(
    language: str,
) -> InlineKeyboardMarkup:
    if language == "ru":
        items = [
            (
                "⚖️ Сохранить вес",
                "goal:maintain",
            ),
            (
                "📉 Снизить вес",
                "goal:lose",
            ),
            (
                "💚 Улучшить полезные привычки",
                "goal:habits",
            ),
        ]
    else:
        items = [
            (
                "⚖️ Vaznni saqlash",
                "goal:maintain",
            ),
            (
                "📉 Vaznni kamaytirish",
                "goal:lose",
            ),
            (
                "💚 Sog‘lom odatlarni yaxshilash",
                "goal:habits",
            ),
        ]

    return inline_menu(
        items,
        columns=1,
    )


# =========================================================
# FAOLLIK TANLASH
# =========================================================

def activity_menu(
    language: str,
) -> InlineKeyboardMarkup:
    if language == "ru":
        items = [
            (
                "🪑 Низкая активность",
                "activity:low",
            ),
            (
                "🚶 Лёгкая активность",
                "activity:light",
            ),
            (
                "🏃 Средняя активность",
                "activity:medium",
            ),
            (
                "🏋️ Высокая активность",
                "activity:high",
            ),
        ]
    else:
        items = [
            (
                "🪑 Kam harakat",
                "activity:low",
            ),
            (
                "🚶 Yengil faol",
                "activity:light",
            ),
            (
                "🏃 O‘rtacha faol",
                "activity:medium",
            ),
            (
                "🏋️ Juda faol",
                "activity:high",
            ),
        ]

    return inline_menu(
        items,
        columns=1,
    )


# =========================================================
# PROFIL MENYUSI
# =========================================================

def profile_menu(
    language: str,
) -> InlineKeyboardMarkup:
    if language == "ru":
        items = [
            (
                "👁 Посмотреть профиль",
                "profile:view",
            ),
            (
                "✏️ Изменить имя",
                "profile:edit:name",
            ),
            (
                "🎂 Изменить возраст",
                "profile:edit:age",
            ),
            (
                "📏 Изменить рост",
                "profile:edit:height_cm",
            ),
            (
                "⚖️ Изменить вес",
                "profile:edit:weight",
            ),
            (
                "🎯 Изменить цель",
                "profile:edit:goal",
            ),
            (
                "🏠 Главное меню",
                "home",
            ),
        ]
    else:
        items = [
            (
                "👁 Profilimni ko‘rish",
                "profile:view",
            ),
            (
                "✏️ Ismni o‘zgartirish",
                "profile:edit:name",
            ),
            (
                "🎂 Yoshni o‘zgartirish",
                "profile:edit:age",
            ),
            (
                "📏 Bo‘yni o‘zgartirish",
                "profile:edit:height_cm",
            ),
            (
                "⚖️ Vaznni o‘zgartirish",
                "profile:edit:weight",
            ),
            (
                "🎯 Maqsadni o‘zgartirish",
                "profile:edit:goal",
            ),
            (
                "🏠 Asosiy menyu",
                "home",
            ),
        ]

    return inline_menu(
        items,
        columns=1,
    )


# =========================================================
# TANA TAHLILI / BMI MENYUSI
# =========================================================

def body_menu(
    language: str,
) -> InlineKeyboardMarkup:
    if language == "ru":
        items = [
            (
                "📊 Мой BMI",
                "body:bmi",
            ),
            (
                "⚡ Дневная энергия",
                "body:calories",
            ),
            (
                "🎯 Норма и идеальный вес",
                "body:range",
            ),
            (
                "🧍 Полный анализ тела",
                "body:full",
            ),
            (
                "🏠 Главное меню",
                "home",
            ),
        ]
    else:
        items = [
            (
                "📊 BMI natijam",
                "body:bmi",
            ),
            (
                "⚡ Kunlik energiya",
                "body:calories",
            ),
            (
                "🎯 Norma va ideal vazn",
                "body:range",
            ),
            (
                "🧍 To‘liq tana tahlili",
                "body:full",
            ),
            (
                "🏠 Asosiy menyu",
                "home",
            ),
        ]

    return inline_menu(
        items,
        columns=2,
    )


# =========================================================
# SLIMWELL MENYUSI
# =========================================================

def slimwell_menu(
    language: str,
) -> InlineKeyboardMarkup:
    if language == "ru":
        items = [
            (
                "⏰ Как принимать?",
                "slim:usage",
            ),
            (
                "📅 Мой режим приёма",
                "slim:plan",
            ),
            (
                "💎 О продукте",
                "slim:about",
            ),
            (
                "🧪 Состав и свойства",
                "slim:ingredients",
            ),
            (
                "🏅 Сертификаты",
                "slim:certs",
            ),
            (
                "📦 Хранение",
                "slim:storage",
            ),
            (
                "💚 Напоминание",
                "slim:warnings",
            ),
            (
                "❓ Рекомендации",
                "slim:faq",
            ),
            (
                "🏠 Главное меню",
                "home",
            ),
        ]
    else:
        items = [
            (
                "⏰ Qanday ichiladi?",
                "slim:usage",
            ),
            (
                "📅 Mening qabul rejam",
                "slim:plan",
            ),
            (
                "💎 Mahsulot haqida",
                "slim:about",
            ),
            (
                "🧪 Tarkibi va foydasi",
                "slim:ingredients",
            ),
            (
                "🏅 Sertifikatlar",
                "slim:certs",
            ),
            (
                "📦 Saqlash shartlari",
                "slim:storage",
            ),
            (
                "💚 Eslatma",
                "slim:warnings",
            ),
            (
                "❓ Tavsiyalar",
                "slim:faq",
            ),
            (
                "🏠 Asosiy menyu",
                "home",
            ),
        ]

    return inline_menu(
        items,
        columns=2,
    )


# =========================================================
# OVQATLANISH MENYUSI
# =========================================================

def meal_menu(
    language: str,
) -> InlineKeyboardMarkup:
    if language == "ru":
        items = [
            (
                "☀️ Меню на сегодня",
                "meal:today",
            ),
            (
                "📅 Меню на 7 дней",
                "meal:week",
            ),
            (
                "🛒 Список покупок",
                "meal:shopping",
            ),
            (
                "🏠 Главное меню",
                "home",
            ),
        ]
    else:
        items = [
            (
                "☀️ Bugungi menyu",
                "meal:today",
            ),
            (
                "📅 7 kunlik menyu",
                "meal:week",
            ),
            (
                "🛒 Xarid ro‘yxati",
                "meal:shopping",
            ),
            (
                "🏠 Asosiy menyu",
                "home",
            ),
        ]

    return inline_menu(
        items,
        columns=1,
    )


# =========================================================
# SOG‘LOM ODATLAR MENYUSI
# =========================================================

def habits_menu(
    language: str,
) -> InlineKeyboardMarkup:
    if language == "ru":
        items = [
            (
                "💧 +250 мл воды",
                "habit:water:250",
            ),
            (
                "🥤 +500 мл воды",
                "habit:water:500",
            ),
            (
                "✍️ Другое количество",
                "habit:water:custom",
            ),
            (
                "👣 Ввести шаги",
                "habit:steps",
            ),
            (
                "🌙 Ввести сон",
                "habit:sleep",
            ),
            (
                "📊 Отчёт за день",
                "habit:today",
            ),
            (
                "🏠 Главное меню",
                "home",
            ),
        ]
    else:
        items = [
            (
                "💧 +250 ml suv",
                "habit:water:250",
            ),
            (
                "🥤 +500 ml suv",
                "habit:water:500",
            ),
            (
                "✍️ Boshqa miqdor",
                "habit:water:custom",
            ),
            (
                "👣 Qadamlarni kiritish",
                "habit:steps",
            ),
            (
                "🌙 Uyquni kiritish",
                "habit:sleep",
            ),
            (
                "📊 Bugungi hisobot",
                "habit:today",
            ),
            (
                "🏠 Asosiy menyu",
                "home",
            ),
        ]

    return inline_menu(
        items,
        columns=2,
    )


# =========================================================
# NATIJALAR MENYUSI
# =========================================================

def results_menu(
    language: str,
) -> InlineKeyboardMarkup:
    if language == "ru":
        items = [
            (
                "⚖️ Вес сегодня",
                "result:add",
            ),
            (
                "📈 Динамика веса",
                "result:history",
            ),
            (
                "🎯 До цели",
                "result:goal",
            ),
            (
                "📊 Отчёт за день",
                "result:today",
            ),
            (
                "🏠 Главное меню",
                "home",
            ),
        ]
    else:
        items = [
            (
                "⚖️ Bugungi vaznni kiritish",
                "result:add",
            ),
            (
                "📈 Vazn dinamikasi",
                "result:history",
            ),
            (
                "🎯 Maqsadgacha qoldi",
                "result:goal",
            ),
            (
                "📊 Bugungi hisobot",
                "result:today",
            ),
            (
                "🏠 Asosiy menyu",
                "home",
            ),
        ]

    return inline_menu(
        items,
        columns=1,
    )


# =========================================================
# OVQAT TAHLILI NATIJASI
# =========================================================

def food_result_menu(
    language: str,
) -> InlineKeyboardMarkup:
    if language == "ru":
        items = [
            (
                "➕ Добавить в дневной отчёт",
                "food:save",
            ),
            (
                "❌ Отмена",
                "food:cancel",
            ),
        ]
    else:
        items = [
            (
                "➕ Kunlik hisobga qo‘shish",
                "food:save",
            ),
            (
                "❌ Bekor qilish",
                "food:cancel",
            ),
        ]

    return inline_menu(
        items,
        columns=1,
    )


# =========================================================
# MASHQ BAJARILDI TUGMASI
# =========================================================

def exercise_done_menu(
    exercise_index: int,
    language: str,
) -> InlineKeyboardMarkup:
    text = (
        "✅ Выполнено"
        if language == "ru"
        else "✅ Bajarildi"
    )

    return inline_menu(
        [
            (
                text,
                f"exercise:done:{exercise_index}",
            ),
            (
                (
                    "🏠 Главное меню"
                    if language == "ru"
                    else "🏠 Asosiy menyu"
                ),
                "home",
            ),
        ],
        columns=1,
    )


# =========================================================
# ADMIN MENYUSI
# =========================================================

def admin_menu() -> InlineKeyboardMarkup:
    return inline_menu(
        [
            (
                "📊 Statistika",
                "admin:stats",
            ),
            (
                "🔍 Shaxsiy ID orqali qidirish",
                "admin:search",
            ),
            (
                "🏠 Asosiy menyu",
                "home",
            ),
        ],
        columns=1,
    )

