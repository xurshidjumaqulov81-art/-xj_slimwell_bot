from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


MAIN_ROWS = [
    ["👤 Mening profilim", "📊 Tana tahlili"],
    ["🥗 Shaxsiy ovqatlanish", "📸 Ovqatni tahlil qilish"],
    ["💧 Sog‘lom odatlar", "💪 Mashqlar"],
    ["💊 SlimWell", "📈 Natijalar"],
]


def main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=x) for x in row] for row in MAIN_ROWS]
    if is_admin:
        rows.append([KeyboardButton(text="🛡 Admin panel")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


def inline_menu(items: list[tuple[str, str]], columns: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, data in items:
        builder.button(text=text, callback_data=data)
    builder.adjust(columns)
    return builder.as_markup()


def profile_menu():
    return inline_menu([
        ("👁 Profilimni ko‘rish", "profile:view"),
        ("✏️ Ismni o‘zgartirish", "profile:edit:name"),
        ("✏️ Yoshni o‘zgartirish", "profile:edit:age"),
        ("✏️ Jinsni o‘zgartirish", "profile:edit:gender"),
        ("✏️ Bo‘yni o‘zgartirish", "profile:edit:height_cm"),
        ("✏️ Vaznni o‘zgartirish", "profile:edit:weight"),
        ("🎯 Maqsadni o‘zgartirish", "profile:edit:goal"),
        ("🏠 Asosiy menyu", "home"),
    ])


def body_menu():
    return inline_menu([
        ("⚖️ BMI hisoblash", "body:bmi"),
        ("🔥 Kunlik kaloriya", "body:calories"),
        ("🎯 Sog‘lom vazn oralig‘i", "body:range"),
        ("📋 To‘liq tana tahlili", "body:full"),
        ("🏠 Asosiy menyu", "home"),
    ])


def meal_menu():
    return inline_menu([
        ("☀️ Bugungi menyu", "meal:today"),
        ("📅 7 kunlik menyu", "meal:week"),
        ("🛒 Xarid ro‘yxati", "meal:shopping"),
        ("🥘 Retseptlar", "meal:recipes"),
        ("🔄 Menyuni qayta tuzish", "meal:today"),
        ("🏠 Asosiy menyu", "home"),
    ])


def habits_menu():
    return inline_menu([
        ("💧 +250 ml", "habit:water:250"),
        ("💧 +500 ml", "habit:water:500"),
        ("✏️ Boshqa suv miqdori", "habit:water:custom"),
        ("🚶 Qadamlarni kiritish", "habit:steps"),
        ("😴 Uyquni kiritish", "habit:sleep"),
        ("📋 Bugungi odatlar", "habit:today"),
        ("🏠 Asosiy menyu", "home"),
    ])


def exercise_menu():
    return inline_menu([
        ("🏠 Uyda mashq", "exercise:home"),
        ("🚶 Yengil faollik", "exercise:light"),
        ("🏃 Kardio", "exercise:cardio"),
        ("🧘 Cho‘zilish", "exercise:stretch"),
        ("📅 Haftalik reja", "exercise:week"),
        ("🏠 Asosiy menyu", "home"),
    ])


def slimwell_menu():
    return inline_menu([
        ("📖 Mahsulot haqida", "slim:about"),
        ("🧪 Tarkibi", "slim:ingredients"),
        ("🕒 Qabul qilish tartibi", "slim:usage"),
        ("⚠️ Ogohlantirishlar", "slim:warnings"),
        ("📦 Saqlash shartlari", "slim:storage"),
        ("📄 Sertifikatlar", "slim:certificates"),
        ("❓ Ko‘p beriladigan savollar", "slim:faq"),
        ("🏠 Asosiy menyu", "home"),
    ])


def results_menu():
    return inline_menu([
        ("⚖️ Vazn kiritish", "results:add_weight"),
        ("📉 Vazn tarixi", "results:weights"),
        ("📊 BMI o‘zgarishi", "results:bmi"),
        ("📋 Bugungi hisobot", "results:today"),
        ("🏠 Asosiy menyu", "home"),
    ])


def gender_menu():
    return inline_menu([("🚹 Erkak", "set_gender:Erkak"), ("🚺 Ayol", "set_gender:Ayol")], 2)


def goal_menu():
    return inline_menu([
        ("⚖️ Vaznni saqlash", "set_goal:Vaznni saqlash"),
        ("📉 Vaznni kamaytirish", "set_goal:Vaznni kamaytirish"),
        ("💪 Sog‘lom odatlarni yaxshilash", "set_goal:Sog‘lom odatlarni yaxshilash"),
    ])


def admin_menu():
    return inline_menu([
        ("👥 Foydalanuvchilar statistikasi", "admin:stats"),
        ("🔍 ID bo‘yicha qidirish", "admin:search"),
        ("🏠 Asosiy menyu", "home"),
    ])
