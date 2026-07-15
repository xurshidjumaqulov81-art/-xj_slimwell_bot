TRANSLATIONS = {
    "uz": {
        "welcome": "XJ SlimWell shaxsiy yordamchisiga xush kelibsiz.",
        "choose_language": "Davom etish uchun tilni tanlang.",
        "enter_id": "7 xonali shaxsiy ID raqamingizni kiriting.\n\nMasalan: <b>0012345</b>",
        "bad_id": "ID aynan 7 ta raqamdan iborat bo‘lsin.\nMasalan: <b>0012345</b>",
        "used_id": "Bu ID boshqa profilga biriktirilgan. Boshqa ID kiriting.",
        "enter_name": "Ismingizni kiriting:",
        "enter_age": "Yoshingizni kiriting:",
        "enter_height": "Bo‘yingizni santimetrda kiriting:",
        "enter_weight": "Vazningizni kilogrammda kiriting:",
        "choose_gender": "Jinsingizni tanlang:",
        "choose_goal": "Maqsadingizni tanlang:",
        "choose_activity": "Kundalik faolligingizni tanlang:",
        "profile_ready": "Profilingiz tayyor.",
        "main_prompt": "Kerakli bo‘limni tanlang.",
    },
    "ru": {
        "welcome": "Добро пожаловать в персонального помощника XJ SlimWell.",
        "choose_language": "Выберите язык, чтобы продолжить.",
        "enter_id": "Введите ваш личный ID из 7 цифр.\n\nНапример: <b>0012345</b>",
        "bad_id": "ID должен состоять ровно из 7 цифр.\nНапример: <b>0012345</b>",
        "used_id": "Этот ID уже привязан к другому профилю. Введите другой ID.",
        "enter_name": "Введите ваше имя:",
        "enter_age": "Введите ваш возраст:",
        "enter_height": "Введите рост в сантиметрах:",
        "enter_weight": "Введите вес в килограммах:",
        "choose_gender": "Выберите пол:",
        "choose_goal": "Выберите цель:",
        "choose_activity": "Выберите уровень активности:",
        "profile_ready": "Профиль готов.",
        "main_prompt": "Выберите нужный раздел.",
    }
}

# Katalog rejasi: yorliqdagi 3 kapsulalik porsiyadan oshmaydi.
BMI_PLANS = {
    "normal": {
        "uz": {"title": "Me’yoriy vazn", "capsules": 2, "water": "2–2.5 litr", "steps": "8 000–10 000", "sleep": "7–8 soat"},
        "ru": {"title": "Нормальный вес", "capsules": 2, "water": "2–2.5 литра", "steps": "8 000–10 000", "sleep": "7–8 часов"},
    },
    "overweight": {
        "uz": {"title": "Ortiqcha vazn", "capsules": 2, "water": "2–2.5 litr", "steps": "8 000–10 000", "sleep": "7–8 soat"},
        "ru": {"title": "Избыточный вес", "capsules": 2, "water": "2–2.5 литра", "steps": "8 000–10 000", "sleep": "7–8 часов"},
    },
    "obesity1": {
        "uz": {"title": "1-darajali semizlik", "capsules": 3, "water": "2.5–3 litr", "steps": "8 000–10 000", "sleep": "7.5–8.5 soat"},
        "ru": {"title": "Ожирение 1 степени", "capsules": 3, "water": "2.5–3 литра", "steps": "8 000–10 000", "sleep": "7.5–8.5 часов"},
    },
    "obesity2": {
        "uz": {"title": "2-darajali semizlik", "capsules": 3, "water": "2.5–3 litr", "steps": "6 000–8 000", "sleep": "8 soat"},
        "ru": {"title": "Ожирение 2 степени", "capsules": 3, "water": "2.5–3 литра", "steps": "6 000–8 000", "sleep": "8 часов"},
    },
    "obesity3": {
        "uz": {"title": "3-darajali semizlik", "capsules": 3, "water": "2.5–3 litr", "steps": "bosqichma-bosqich", "sleep": "8–9 soat"},
        "ru": {"title": "Ожирение 3 степени", "capsules": 3, "water": "2.5–3 литра", "steps": "постепенно", "sleep": "8–9 часов"},
    },
}

PRODUCT = {
    "uz": {
        "about": (
            "<b>XJ SlimWell</b> — vazn nazoratini qo‘llab-quvvatlash uchun yaratilgan "
            "nutrikosmetik kompleks.\n\n"
            "🍽 Ishtahani nazorat qilishga ko‘maklashadi\n"
            "⚡ Kunlik faollik va tetiklikni qo‘llab-quvvatlaydi\n"
            "🌿 Metabolik jarayonlarni qo‘llab-quvvatlaydi\n"
            "💚 Ovqatlanish, suv va harakat rejasi bilan uyg‘un ishlaydi"
        ),
        "ingredients": (
            "🌿 <b>Glukomannan — 300 mg</b>\nTo‘qlik hissini qo‘llab-quvvatlaydi.\n\n"
            "🍃 <b>Yashil choy ekstrakti — 200 mg</b>\nMetabolik faollikni qo‘llab-quvvatlaydi.\n\n"
            "🌾 <b>Psyllium Husk — 150 mg</b>\nHazm jarayonini qo‘llab-quvvatlaydi.\n\n"
            "🟡 <b>Berberine HCl — 100 mg</b>\nUglevod almashinuvini qo‘llab-quvvatlaydi.\n\n"
            "⚡ <b>L-Carnitine — 100 mg</b>\nEnergiya almashinuvida ishtirok etadi.\n\n"
            "🌱 <b>Gymnema — 75 mg</b>\nShirinlik istagini nazorat qilishga ko‘maklashadi.\n\n"
            "☕ <b>Caffeine — 75 mg</b>\nTetiklikni qo‘llab-quvvatlaydi.\n\n"
            "🧘 <b>L-Theanine — 50 mg</b>\nDiqqat va xotirjamlik muvozanatini qo‘llab-quvvatlaydi.\n\n"
            "🍊 <b>Vitamin C — 50 mg</b>\nAntioksidant qo‘llab-quvvatlash.\n\n"
            "🌶 <b>Capsicum — 15 mg</b>\nTermogenez jarayonini qo‘llab-quvvatlaydi.\n\n"
            "⚫ <b>Black Pepper — 2.5 mg</b>\nFaol moddalarning singishini qo‘llab-quvvatlaydi.\n\n"
            "💎 <b>Chromium Picolinate — 100 mcg</b>\nGlyukoza almashinuvini qo‘llab-quvvatlaydi."
        ),
        "storage": "📦 Salqin, quruq va quyosh nuri tushmaydigan joyda saqlang.\n🌡 Issiqlik va namlikdan himoya qiling.",
        "warnings": "👨‍👩‍👧 Bolalar ololmaydigan joyda saqlang.\n💚 Maxsus holatlarda mutaxassis tavsiyasi bilan foydalaning.",
        "certs": "🏅 ISO 22000\n🏭 GMP\n🛡 HACCP\n🌿 HALAL\n🌍 FSSAI",
        "faq": (
            "✅ Tavsiya etilgan qabul tartibiga muntazam amal qiling.\n"
            "🥗 3 mahal muvozanatli ovqatlaning.\n"
            "💧 Kunlik suv rejasini bajaring.\n"
            "🚶 Harakatni kundalik odatga aylantiring.\n"
            "📈 Natijalarni haftalik kuzatib boring."
        ),
    },
    "ru": {
        "about": (
            "<b>XJ SlimWell</b> — нутрикосметический комплекс для поддержки контроля веса.\n\n"
            "🍽 Помогает контролировать аппетит\n"
            "⚡ Поддерживает активность и бодрость\n"
            "🌿 Поддерживает обменные процессы\n"
            "💚 Сочетается с режимом питания, воды и движения"
        ),
        "ingredients": "Состав и краткое описание компонентов указаны на этикетке продукта.",
        "storage": "📦 Храните в прохладном сухом месте без прямого солнечного света.\n🌡 Берегите от тепла и влаги.",
        "warnings": "👨‍👩‍👧 Храните в недоступном для детей месте.\n💚 В особых случаях используйте по рекомендации специалиста.",
        "certs": "🏅 ISO 22000\n🏭 GMP\n🛡 HACCP\n🌿 HALAL\n🌍 FSSAI",
        "faq": "✅ Соблюдайте режим приёма.\n🥗 Питайтесь 3 раза в день.\n💧 Соблюдайте питьевой режим.\n🚶 Поддерживайте ежедневную активность.\n📈 Отслеживайте результат еженедельно.",
    }
}
