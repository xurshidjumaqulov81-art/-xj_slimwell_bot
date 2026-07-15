TRANSLATIONS: dict[str, dict[str, str]] = {
    "uz": {
        "welcome": (
            "XJ SlimWell shaxsiy yordamchisiga xush kelibsiz."
        ),
        "choose_language": (
            "Davom etish uchun tilni tanlang."
        ),
        "enter_personal_id": (
            "7 xonali shaxsiy ID raqamingizni kiriting.\n\n"
            "Masalan: <b>0012345</b>"
        ),
        "invalid_personal_id": (
            "ID aynan 7 ta raqamdan iborat bo‘lishi kerak.\n\n"
            "Masalan: <b>0012345</b>"
        ),
        "personal_id_exists": (
            "Bu ID boshqa profilga biriktirilgan.\n"
            "Iltimos, boshqa ID kiriting."
        ),
        "enter_name": "Ismingizni kiriting:",
        "invalid_name": (
            "Ism 2–50 ta belgidan iborat bo‘lsin."
        ),
        "enter_age": "Yoshingizni kiriting:",
        "invalid_age": (
            "Yoshni 13–100 oralig‘ida kiriting."
        ),
        "choose_gender": "Jinsingizni tanlang:",
        "enter_height": (
            "Bo‘yingizni santimetrda kiriting.\n\n"
            "Masalan: <b>180</b>"
        ),
        "invalid_height": (
            "Bo‘yni 120–230 sm oralig‘ida kiriting."
        ),
        "enter_weight": (
            "Vazningizni kilogrammda kiriting.\n\n"
            "Masalan: <b>85.5</b>"
        ),
        "invalid_weight": (
            "Vaznni 30–300 kg oralig‘ida kiriting."
        ),
        "choose_goal": "Maqsadingizni tanlang:",
        "choose_activity": (
            "Kundalik faollik darajangizni tanlang:"
        ),
        "profile_ready": (
            "Profilingiz muvaffaqiyatli yaratildi."
        ),
        "main_menu_prompt": (
            "Kerakli bo‘limni tanlang."
        ),
        "saved": "Ma’lumot saqlandi.",
        "cancelled": "Amal bekor qilindi.",
        "not_found": "Ma’lumot topilmadi.",
        "temporary_error": (
            "Xizmat vaqtincha ishlamadi.\n"
            "Iltimos, birozdan keyin qayta urinib ko‘ring."
        ),
    },
    "ru": {
        "welcome": (
            "Добро пожаловать в персонального помощника XJ SlimWell."
        ),
        "choose_language": (
            "Выберите язык, чтобы продолжить."
        ),
        "enter_personal_id": (
            "Введите ваш личный ID из 7 цифр.\n\n"
            "Например: <b>0012345</b>"
        ),
        "invalid_personal_id": (
            "ID должен состоять ровно из 7 цифр.\n\n"
            "Например: <b>0012345</b>"
        ),
        "personal_id_exists": (
            "Этот ID уже привязан к другому профилю.\n"
            "Введите другой ID."
        ),
        "enter_name": "Введите ваше имя:",
        "invalid_name": (
            "Имя должно содержать от 2 до 50 символов."
        ),
        "enter_age": "Введите ваш возраст:",
        "invalid_age": (
            "Введите возраст от 13 до 100 лет."
        ),
        "choose_gender": "Выберите пол:",
        "enter_height": (
            "Введите рост в сантиметрах.\n\n"
            "Например: <b>180</b>"
        ),
        "invalid_height": (
            "Введите рост от 120 до 230 см."
        ),
        "enter_weight": (
            "Введите вес в килограммах.\n\n"
            "Например: <b>85.5</b>"
        ),
        "invalid_weight": (
            "Введите вес от 30 до 300 кг."
        ),
        "choose_goal": "Выберите вашу цель:",
        "choose_activity": (
            "Выберите уровень ежедневной активности:"
        ),
        "profile_ready": (
            "Ваш профиль успешно создан."
        ),
        "main_menu_prompt": (
            "Выберите нужный раздел."
        ),
        "saved": "Данные сохранены.",
        "cancelled": "Действие отменено.",
        "not_found": "Данные не найдены.",
        "temporary_error": (
            "Сервис временно недоступен.\n"
            "Пожалуйста, повторите попытку позже."
        ),
    },
}


BMI_PLANS: dict[str, dict[str, dict[str, object]]] = {
    "underweight": {
        "uz": {
            "title": "Kam vazn",
            "water": "2–2.5 litr",
            "steps": "6 000–8 000",
            "sleep": "7–9 soat",
        },
        "ru": {
            "title": "Недостаточный вес",
            "water": "2–2.5 литра",
            "steps": "6 000–8 000",
            "sleep": "7–9 часов",
        },
    },
    "normal": {
        "uz": {
            "title": "Me’yoriy vazn",
            "water": "2–2.5 litr",
            "steps": "8 000–10 000",
            "sleep": "7–8 soat",
        },
        "ru": {
            "title": "Нормальный вес",
            "water": "2–2.5 литра",
            "steps": "8 000–10 000",
            "sleep": "7–8 часов",
        },
    },
    "overweight": {
        "uz": {
            "title": "Ortiqcha vazn",
            "water": "2–2.5 litr",
            "steps": "8 000–10 000",
            "sleep": "7–8 soat",
        },
        "ru": {
            "title": "Избыточный вес",
            "water": "2–2.5 литра",
            "steps": "8 000–10 000",
            "sleep": "7–8 часов",
        },
    },
    "obesity_1": {
        "uz": {
            "title": "1-darajali semizlik",
            "water": "2.5–3 litr",
            "steps": "8 000–10 000",
            "sleep": "7.5–8.5 soat",
        },
        "ru": {
            "title": "Ожирение 1 степени",
            "water": "2.5–3 литра",
            "steps": "8 000–10 000",
            "sleep": "7.5–8.5 часов",
        },
    },
    "obesity_2": {
        "uz": {
            "title": "2-darajali semizlik",
            "water": "2.5–3 litr",
            "steps": "6 000–8 000",
            "sleep": "8 soat",
        },
        "ru": {
            "title": "Ожирение 2 степени",
            "water": "2.5–3 литра",
            "steps": "6 000–8 000",
            "sleep": "8 часов",
        },
    },
    "obesity_3": {
        "uz": {
            "title": "3-darajali semizlik",
            "water": "2.5–3 litr",
            "steps": "Bosqichma-bosqich oshiriladi",
            "sleep": "8–9 soat",
        },
        "ru": {
            "title": "Ожирение 3 степени",
            "water": "2.5–3 литра",
            "steps": "Увеличивать постепенно",
            "sleep": "8–9 часов",
        },
    },
}


PRODUCT_CONTENT: dict[str, dict[str, str]] = {
    "uz": {
        "about": (
            "<b>XJ SlimWell</b> — vazn nazoratini qo‘llab-quvvatlash "
            "uchun yaratilgan nutrikosmetik kompleks.\n\n"
            "🍽 Ishtahani nazorat qilishga ko‘maklashadi\n"
            "⚡ Kunlik faollik va tetiklikni qo‘llab-quvvatlaydi\n"
            "🌿 Metabolik jarayonlarni qo‘llab-quvvatlaydi\n"
            "💚 Ovqatlanish, suv va harakat rejasi bilan uyg‘un ishlaydi"
        ),
        "ingredients": (
            "🌿 <b>Glukomannan — 300 mg</b>\n"
            "To‘qlik hissini qo‘llab-quvvatlaydi.\n\n"
            "🍃 <b>Yashil choy ekstrakti — 200 mg</b>\n"
            "Metabolik faollikni qo‘llab-quvvatlaydi.\n\n"
            "🌾 <b>Psyllium Husk — 150 mg</b>\n"
            "Hazm jarayonini qo‘llab-quvvatlaydi.\n\n"
            "🟡 <b>Berberine HCl — 100 mg</b>\n"
            "Uglevod almashinuvini qo‘llab-quvvatlaydi.\n\n"
            "⚡ <b>L-Carnitine — 100 mg</b>\n"
            "Energiya almashinuvida ishtirok etadi.\n\n"
            "🌱 <b>Gymnema Sylvestre — 75 mg</b>\n"
            "Shirinlikka bo‘lgan istakni nazorat qilishga ko‘maklashadi.\n\n"
            "☕ <b>Caffeine Anhydrous — 75 mg</b>\n"
            "Tetiklikni qo‘llab-quvvatlaydi.\n\n"
            "🧘 <b>L-Theanine — 50 mg</b>\n"
            "Diqqat va xotirjamlik muvozanatini qo‘llab-quvvatlaydi.\n\n"
            "🍊 <b>Vitamin C — 50 mg</b>\n"
            "Antioksidant qo‘llab-quvvatlash beradi.\n\n"
            "🌶 <b>Capsicum Extract — 15 mg</b>\n"
            "Termogenez jarayonlarini qo‘llab-quvvatlaydi.\n\n"
            "⚫ <b>Black Pepper Extract — 2.5 mg</b>\n"
            "Faol moddalarning singishini qo‘llab-quvvatlaydi.\n\n"
            "💎 <b>Chromium Picolinate — 100 mcg</b>\n"
            "Glyukoza almashinuvini qo‘llab-quvvatlaydi."
        ),
        "usage": (
            "⏰ <b>QABUL QILISH TARTIBI</b>\n\n"
            "Mahsulotni faqat uning rasmiy yorlig‘i yoki tasdiqlangan "
            "yo‘riqnomasidagi miqdorda qabul qiling.\n\n"
            "💧 Har bir qabulda yetarli suv iching.\n"
            "📅 Kurs davomiyligi mahsulot yo‘riqnomasi asosida belgilanadi."
        ),
        "storage": (
            "📦 Salqin, quruq va quyosh nuri tushmaydigan joyda saqlang.\n"
            "🌡 Issiqlik va namlikdan himoya qiling."
        ),
        "warnings": (
            "👨‍👩‍👧 Bolalar ololmaydigan joyda saqlang.\n"
            "💚 Maxsus holatlarda mutaxassis tavsiyasi bilan foydalaning."
        ),
        "certificates": (
            "🏅 ISO 22000\n"
            "🏭 GMP\n"
            "🛡 HACCP\n"
            "🌿 HALAL\n"
            "🌍 FSSAI"
        ),
        "faq": (
            "✅ Tavsiya etilgan qabul tartibiga muntazam amal qiling.\n"
            "🥗 Kun davomida 3 mahal muvozanatli ovqatlaning.\n"
            "💧 Kunlik suv rejasini bajaring.\n"
            "🚶 Harakatni kundalik odatga aylantiring.\n"
            "📈 Natijalarni haftalik kuzatib boring."
        ),
    },
    "ru": {
        "about": (
            "<b>XJ SlimWell</b> — нутрикосметический комплекс "
            "для поддержки контроля веса.\n\n"
            "🍽 Помогает контролировать аппетит\n"
            "⚡ Поддерживает бодрость и ежедневную активность\n"
            "🌿 Поддерживает обменные процессы\n"
            "💚 Сочетается с режимом питания, воды и движения"
        ),
        "ingredients": (
            "🌿 <b>Глюкоманнан — 300 мг</b>\n"
            "Поддерживает чувство сытости.\n\n"
            "🍃 <b>Экстракт зелёного чая — 200 мг</b>\n"
            "Поддерживает обменные процессы.\n\n"
            "🌾 <b>Psyllium Husk — 150 мг</b>\n"
            "Поддерживает пищеварение.\n\n"
            "🟡 <b>Berberine HCl — 100 мг</b>\n"
            "Поддерживает обмен углеводов.\n\n"
            "⚡ <b>L-Carnitine — 100 мг</b>\n"
            "Участвует в энергетическом обмене.\n\n"
            "🌱 <b>Gymnema Sylvestre — 75 мг</b>\n"
            "Помогает контролировать тягу к сладкому.\n\n"
            "☕ <b>Caffeine Anhydrous — 75 мг</b>\n"
            "Поддерживает бодрость.\n\n"
            "🧘 <b>L-Theanine — 50 мг</b>\n"
            "Поддерживает концентрацию и спокойствие.\n\n"
            "🍊 <b>Vitamin C — 50 мг</b>\n"
            "Антиоксидантная поддержка.\n\n"
            "🌶 <b>Capsicum Extract — 15 мг</b>\n"
            "Поддерживает процессы термогенеза.\n\n"
            "⚫ <b>Black Pepper Extract — 2.5 мг</b>\n"
            "Поддерживает усвоение активных веществ.\n\n"
            "💎 <b>Chromium Picolinate — 100 мкг</b>\n"
            "Поддерживает обмен глюкозы."
        ),
        "usage": (
            "⏰ <b>РЕЖИМ ПРИЁМА</b>\n\n"
            "Принимайте продукт только в количестве, указанном "
            "на официальной этикетке или в утверждённой инструкции.\n\n"
            "💧 Запивайте достаточным количеством воды.\n"
            "📅 Продолжительность курса определяется инструкцией продукта."
        ),
        "storage": (
            "📦 Храните в прохладном сухом месте без прямого солнечного света.\n"
            "🌡 Берегите от тепла и влаги."
        ),
        "warnings": (
            "👨‍👩‍👧 Храните в недоступном для детей месте.\n"
            "💚 В особых случаях используйте по рекомендации специалиста."
        ),
        "certificates": (
            "🏅 ISO 22000\n"
            "🏭 GMP\n"
            "🛡 HACCP\n"
            "🌿 HALAL\n"
            "🌍 FSSAI"
        ),
        "faq": (
            "✅ Соблюдайте рекомендованный режим приёма.\n"
            "🥗 Питайтесь 3 раза в день.\n"
            "💧 Соблюдайте питьевой режим.\n"
            "🚶 Поддерживайте ежедневную активность.\n"
            "📈 Отслеживайте результат еженедельно."
        ),
    },
}


EXERCISE_PLANS: dict[str, list[dict[str, object]]] = {
    "normal": [
        {
            "title_uz": "Tez yurish",
            "title_ru": "Быстрая ходьба",
            "amount_uz": "30 daqiqa",
            "amount_ru": "30 минут",
            "asset": "walk.gif",
            "minutes": 30,
        },
        {
            "title_uz": "Squat",
            "title_ru": "Приседания",
            "amount_uz": "3 × 15",
            "amount_ru": "3 × 15",
            "asset": "squat.gif",
            "minutes": 12,
        },
        {
            "title_uz": "Plank",
            "title_ru": "Планка",
            "amount_uz": "3 × 30 soniya",
            "amount_ru": "3 × 30 секунд",
            "asset": "plank.gif",
            "minutes": 5,
        },
    ],
    "overweight": [
        {
            "title_uz": "Tez yurish",
            "title_ru": "Быстрая ходьба",
            "amount_uz": "30–40 daqiqa",
            "amount_ru": "30–40 минут",
            "asset": "walk.gif",
            "minutes": 35,
        },
        {
            "title_uz": "Squat",
            "title_ru": "Приседания",
            "amount_uz": "3 × 15",
            "amount_ru": "3 × 15",
            "asset": "squat.gif",
            "minutes": 12,
        },
        {
            "title_uz": "Plank",
            "title_ru": "Планка",
            "amount_uz": "3 × 30 soniya",
            "amount_ru": "3 × 30 секунд",
            "asset": "plank.gif",
            "minutes": 5,
        },
    ],
    "obesity_1": [
        {
            "title_uz": "Yurish",
            "title_ru": "Ходьба",
            "amount_uz": "30 daqiqa",
            "amount_ru": "30 минут",
            "asset": "walk.gif",
            "minutes": 30,
        },
        {
            "title_uz": "Stulga o‘tirib-turish",
            "title_ru": "Подъём со стула",
            "amount_uz": "3 × 12",
            "amount_ru": "3 × 12",
            "asset": "chair_squat.gif",
            "minutes": 12,
        },
        {
            "title_uz": "Joyida qadam",
            "title_ru": "Шаги на месте",
            "amount_uz": "3 × 2 daqiqa",
            "amount_ru": "3 × 2 минуты",
            "asset": "march.gif",
            "minutes": 6,
        },
    ],
    "obesity_2": [
        {
            "title_uz": "Sekin yurish",
            "title_ru": "Спокойная ходьба",
            "amount_uz": "20–30 daqiqa",
            "amount_ru": "20–30 минут",
            "asset": "walk.gif",
            "minutes": 25,
        },
        {
            "title_uz": "O‘tirib oyoq ko‘tarish",
            "title_ru": "Подъём ног сидя",
            "amount_uz": "3 × 12",
            "amount_ru": "3 × 12",
            "asset": "leg_raise.gif",
            "minutes": 10,
        },
        {
            "title_uz": "Qo‘l aylantirish",
            "title_ru": "Вращение руками",
            "amount_uz": "3 × 20",
            "amount_ru": "3 × 20",
            "asset": "arms.gif",
            "minutes": 8,
        },
    ],
    "obesity_3": [
        {
            "title_uz": "Sekin yurish",
            "title_ru": "Медленная ходьба",
            "amount_uz": "15–20 daqiqa",
            "amount_ru": "15–20 минут",
            "asset": "walk.gif",
            "minutes": 18,
        },
        {
            "title_uz": "O‘tirgan holda oyoq mashqi",
            "title_ru": "Упражнение для ног сидя",
            "amount_uz": "3 × 10",
            "amount_ru": "3 × 10",
            "asset": "leg_raise.gif",
            "minutes": 8,
        },
        {
            "title_uz": "Nafas mashqi",
            "title_ru": "Дыхательное упражнение",
            "amount_uz": "5 daqiqa",
            "amount_ru": "5 минут",
            "asset": "breathing.gif",
            "minutes": 5,
        },
    ],
}
