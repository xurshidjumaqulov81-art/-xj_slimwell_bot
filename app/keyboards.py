from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline(items, columns=1):
    b = InlineKeyboardBuilder()
    for text, data in items:
        b.button(text=text, callback_data=data)
    b.adjust(columns)
    return b.as_markup()


def language_menu():
    return inline([("🇺🇿 O‘zbekcha", "lang:uz"), ("🇷🇺 Русский", "lang:ru")], 2)


def main_menu(lang: str, admin=False):
    if lang == "ru":
        rows = [
            ["💊 SlimWell", "📊 Анализ тела"],
            ["👤 Мой профиль", "🥗 Питание"],
            ["📸 Анализ еды", "💧 Полезные привычки"],
            ["💪 Упражнения", "📈 Результаты"],
            ["🌐 Изменить язык"],
        ]
    else:
        rows = [
            ["💊 SlimWell", "📊 Tana tahlili"],
            ["👤 Mening profilim", "🥗 Shaxsiy ovqatlanish"],
            ["📸 Ovqatni tahlil qilish", "💧 Sog‘lom odatlar"],
            ["💪 Mashqlar", "📈 Natijalar"],
            ["🌐 Tilni o‘zgartirish"],
        ]
    if admin:
        rows.append(["🛡 Admin panel"])
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=x) for x in row] for row in rows],
        resize_keyboard=True, is_persistent=True
    )


def gender_menu(lang):
    return inline([
        ("🚹 Erkak" if lang=="uz" else "🚹 Мужчина", "gender:male"),
        ("🚺 Ayol" if lang=="uz" else "🚺 Женщина", "gender:female"),
    ], 2)


def goal_menu(lang):
    return inline([
        ("⚖️ Vaznni saqlash" if lang=="uz" else "⚖️ Сохранить вес", "goal:maintain"),
        ("📉 Vaznni kamaytirish" if lang=="uz" else "📉 Снизить вес", "goal:lose"),
        ("💚 Sog‘lom odatlar" if lang=="uz" else "💚 Полезные привычки", "goal:habits"),
    ])


def activity_menu(lang):
    labels = [
        ("🪑 Kam harakat" if lang=="uz" else "🪑 Низкая", "activity:low"),
        ("🚶 Yengil faol" if lang=="uz" else "🚶 Лёгкая", "activity:light"),
        ("🏃 O‘rtacha faol" if lang=="uz" else "🏃 Средняя", "activity:medium"),
        ("🏋️ Juda faol" if lang=="uz" else "🏋️ Высокая", "activity:high"),
    ]
    return inline(labels)


def profile_menu(lang):
    return inline([
        ("👁 Profilim" if lang=="uz" else "👁 Профиль", "profile:view"),
        ("✏️ Ism" if lang=="uz" else "✏️ Имя", "profile:edit:name"),
        ("✏️ Yosh" if lang=="uz" else "✏️ Возраст", "profile:edit:age"),
        ("✏️ Bo‘y" if lang=="uz" else "✏️ Рост", "profile:edit:height_cm"),
        ("✏️ Vazn" if lang=="uz" else "✏️ Вес", "profile:edit:weight"),
        ("🎯 Maqsad" if lang=="uz" else "🎯 Цель", "profile:edit:goal"),
        ("🏠 Asosiy menyu" if lang=="uz" else "🏠 Главное меню", "home"),
    ])


def body_menu(lang):
    return inline([
        ("📊 BMI natijam" if lang=="uz" else "📊 Мой BMI", "body:bmi"),
        ("⚡ Kunlik energiya" if lang=="uz" else "⚡ Дневная энергия", "body:calories"),
        ("🎯 Norma va ideal vazn" if lang=="uz" else "🎯 Норма и идеальный вес", "body:range"),
        ("🧍 To‘liq tana tahlili" if lang=="uz" else "🧍 Полный анализ", "body:full"),
        ("🏠 Asosiy menyu" if lang=="uz" else "🏠 Главное меню", "home"),
    ])


def meal_menu(lang):
    return inline([
        ("☀️ Bugungi menyu" if lang=="uz" else "☀️ Меню на сегодня", "meal:today"),
        ("📅 7 kunlik menyu" if lang=="uz" else "📅 Меню на 7 дней", "meal:week"),
        ("🛒 Xarid ro‘yxati" if lang=="uz" else "🛒 Список покупок", "meal:shopping"),
        ("🏠 Asosiy menyu" if lang=="uz" else "🏠 Главное меню", "home"),
    ])


def slimwell_menu(lang):
    return inline([
        ("⏰ Qanday ichiladi?" if lang=="uz" else "⏰ Как принимать?", "slim:usage"),
        ("📅 Mening qabul rejam" if lang=="uz" else "📅 Мой режим", "slim:plan"),
        ("💎 Mahsulot haqida" if lang=="uz" else "💎 О продукте", "slim:about"),
        ("🧪 Tarkibi va foydasi" if lang=="uz" else "🧪 Состав", "slim:ingredients"),
        ("🏅 Sertifikatlar" if lang=="uz" else "🏅 Сертификаты", "slim:certs"),
        ("📦 Saqlash" if lang=="uz" else "📦 Хранение", "slim:storage"),
        ("💚 Eslatma" if lang=="uz" else "💚 Напоминание", "slim:warnings"),
        ("❓ Tavsiyalar" if lang=="uz" else "❓ Рекомендации", "slim:faq"),
        ("🏠 Asosiy menyu" if lang=="uz" else "🏠 Главное меню", "home"),
    ])


def habits_menu(lang):
    return inline([
        ("💧 +250 ml", "habit:water:250"),
        ("🥤 +500 ml", "habit:water:500"),
        ("✍️ Boshqa miqdor" if lang=="uz" else "✍️ Другое количество", "habit:water:custom"),
        ("👣 Qadamlar" if lang=="uz" else "👣 Шаги", "habit:steps"),
        ("🌙 Uyqu" if lang=="uz" else "🌙 Сон", "habit:sleep"),
        ("📊 Bugungi hisobot" if lang=="uz" else "📊 Отчёт за день", "habit:today"),
        ("🏠 Asosiy menyu" if lang=="uz" else "🏠 Главное меню", "home"),
    ])


def results_menu(lang):
    return inline([
        ("⚖️ Bugungi vazn" if lang=="uz" else "⚖️ Вес сегодня", "result:add"),
        ("📈 Vazn dinamikasi" if lang=="uz" else "📈 Динамика веса", "result:history"),
        ("🎯 Maqsadgacha qoldi" if lang=="uz" else "🎯 До цели", "result:goal"),
        ("📊 Bugungi hisobot" if lang=="uz" else "📊 Отчёт за день", "result:today"),
        ("🏠 Asosiy menyu" if lang=="uz" else "🏠 Главное меню", "home"),
    ])
