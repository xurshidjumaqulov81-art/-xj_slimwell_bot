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
        "enter_name": (
            "Ismingizni kiriting:"
        ),
        "invalid_name": (
            "Ism 2–50 ta belgidan iborat bo‘lsin."
        ),
        "enter_age": (
            "Yoshingizni kiriting:"
        ),
        "invalid_age": (
            "Yoshni 13–100 oralig‘ida kiriting."
        ),
        "choose_gender": (
            "Jinsingizni tanlang:"
        ),
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
        "choose_goal": (
            "Maqsadingizni tanlang:"
        ),
        "choose_activity": (
            "Kundalik faollik darajangizni tanlang:"
        ),
        "profile_ready": (
            "Profilingiz muvaffaqiyatli yaratildi."
        ),
        "main_menu_prompt": (
            "Kerakli bo‘limni tanlang."
        ),
        "saved": (
            "Ma’lumot saqlandi."
        ),
        "cancelled": (
            "Amal bekor qilindi."
        ),
        "not_found": (
            "Ma’lumot topilmadi."
        ),
        "temporary_error": (
            "Xizmat vaqtincha ishlamadi.\n"
            "Birozdan keyin qayta urinib ko‘ring."
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
        "enter_name": (
            "Введите ваше имя:"
        ),
        "invalid_name": (
            "Имя должно содержать от 2 до 50 символов."
        ),
        "enter_age": (
            "Введите ваш возраст:"
        ),
        "invalid_age": (
            "Введите возраст от 13 до 100 лет."
        ),
        "choose_gender": (
            "Выберите пол:"
        ),
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
        "choose_goal": (
            "Выберите вашу цель:"
        ),
        "choose_activity": (
            "Выберите уровень ежедневной активности:"
        ),
        "profile_ready": (
            "Ваш профиль успешно создан."
        ),
        "main_menu_prompt": (
            "Выберите нужный раздел."
        ),
        "saved": (
            "Данные сохранены."
        ),
        "cancelled": (
            "Действие отменено."
        ),
        "not_found": (
            "Данные не найдены."
        ),
        "temporary_error": (
            "Сервис временно недоступен.\n"
            "Повторите попытку позже."
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
            "steps": "7 000–9 000",
            "sleep": "7.5–8.5 soat",
        },
        "ru": {
            "title": "Ожирение 1 степени",
            "water": "2.5–3 литра",
            "steps": "7 000–9 000",
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
            "<b>XJ SlimWell</b> — sog‘lom vazn nazoratini "
            "qo‘llab-quvvatlash uchun ishlab chiqilgan "
            "nutrikosmetik kompleks.\n\n"

            "🌿 <b>Asosiy yo‘nalishlari</b>\n"
            "• Ishtahani nazorat qilishga yordam beradi.\n"
            "• Ortiqcha tamaddi qilish istagini kamaytirishga "
            "ko‘maklashadi.\n"
            "• Modda almashinuvini qo‘llab-quvvatlaydi.\n"
            "• Kundalik energiya va faollikni saqlashga yordam beradi.\n"
            "• Muvozanatli ovqatlanish va jismoniy faollik bilan "
            "birgalikda vazn nazoratini qo‘llab-quvvatlaydi.\n\n"

            "💧 Eng yaxshi natija uchun tavsiya etilgan qabul "
            "tartibiga amal qiling, yetarli suv iching va kundalik "
            "harakatni davom ettiring."
        ),

        "ingredients": (
            "🧪 <b>Tarkibi va foydasi</b>\n\n"

            "🌿 <b>Glukomannan</b>\n"
            "To‘qlik hissini qo‘llab-quvvatlaydi.\n\n"

            "🍃 <b>Yashil choy ekstrakti</b>\n"
            "Metabolik faollik va tetiklikni qo‘llab-quvvatlaydi.\n\n"

            "🌾 <b>Psyllium Husk</b>\n"
            "Hazm jarayonini qo‘llab-quvvatlaydi.\n\n"

            "🟡 <b>Berberine HCl</b>\n"
            "Uglevod almashinuvini qo‘llab-quvvatlaydi.\n\n"

            "⚡ <b>L-Carnitine</b>\n"
            "Energiya almashinuvida ishtirok etadi.\n\n"

            "🌱 <b>Gymnema Sylvestre</b>\n"
            "Shirinlikka bo‘lgan istakni nazorat qilishga "
            "ko‘maklashadi.\n\n"

            "☕ <b>Caffeine Anhydrous</b>\n"
            "Tetiklikni qo‘llab-quvvatlaydi.\n\n"

            "🧘 <b>L-Theanine</b>\n"
            "Diqqat va xotirjamlik muvozanatini "
            "qo‘llab-quvvatlaydi.\n\n"

            "🍊 <b>Vitamin C</b>\n"
            "Antioksidant qo‘llab-quvvatlash beradi.\n\n"

            "🌶 <b>Capsicum Extract</b>\n"
            "Termogenez jarayonlarini qo‘llab-quvvatlaydi.\n\n"

            "⚫ <b>Black Pepper Extract</b>\n"
            "Faol moddalarning singishini qo‘llab-quvvatlaydi.\n\n"

            "💎 <b>Chromium Picolinate</b>\n"
            "Glyukoza almashinuvini qo‘llab-quvvatlaydi.\n\n"

            "📦 Aniq miqdorlar mahsulotning rasmiy yorlig‘i "
            "bo‘yicha tekshiriladi."
        ),

        "storage": (
            "📦 <b>Saqlash shartlari</b>\n\n"
            "• Quruq va salqin joyda saqlang.\n"
            "• To‘g‘ridan-to‘g‘ri quyosh nuridan himoyalang.\n"
            "• Issiqlik va namlikdan uzoqda saqlang.\n"
            "• Bolalar ololmaydigan joyda saqlang."
        ),

        "warnings": (
            "💚 <b>Eslatma</b>\n\n"
            "• Mahsulotni tavsiya etilgan tartibda qabul qiling.\n"
            "• Rasmiy yorliqda ko‘rsatilgan miqdordan oshirmang.\n"
            "• Kun davomida yetarli suv iching.\n"
            "• 18 yoshgacha bo‘lganlar uchun bot kapsula "
            "miqdorini avtomatik belgilamaydi."
        ),

        "faq": (
            "❓ <b>Tavsiyalar</b>\n\n"
            "✅ Tavsiya etilgan qabul rejasiga muntazam amal qiling.\n"
            "✅ Kun davomida muvozanatli ovqatlaning.\n"
            "✅ Yetarli miqdorda suv iching.\n"
            "✅ Har kuni o‘zingizga mos jismoniy faollik qiling.\n"
            "✅ Vazn va natijalaringizni haftalik kuzatib boring."
        ),

        "usage": (
            "⏰ <b>Qabul qilish tartibi</b>\n\n"
            "Kapsulalar ovqatdan oldin suv bilan qabul qilinadi.\n\n"
            "Shaxsiy miqdor va vaqtlar "
            "<b>Mening qabul rejam</b> bo‘limida ko‘rsatiladi."
        ),

        "certificates": (
            "🏅 ISO 22000\n"
            "🏭 GMP\n"
            "🛡 HACCP\n"
            "🌿 HALAL\n"
            "🌍 FSSAI"
        ),
    },

    "ru": {
        "about": (
            "<b>XJ SlimWell</b> — нутрикосметический комплекс, "
            "разработанный для поддержки контроля веса.\n\n"

            "🌿 <b>Основные направления</b>\n"
            "• Поддержка контроля аппетита.\n"
            "• Помощь в уменьшении желания частых перекусов.\n"
            "• Поддержка обменных процессов.\n"
            "• Поддержка ежедневной энергии и активности.\n"
            "• Поддержка контроля веса вместе со сбалансированным "
            "питанием и движением.\n\n"

            "💧 Для лучшего результата соблюдайте рекомендуемый "
            "режим приёма, пейте достаточно воды и сохраняйте "
            "ежедневную активность."
        ),

        "ingredients": (
            "🧪 <b>Состав и свойства</b>\n\n"

            "🌿 <b>Глюкоманнан</b>\n"
            "Поддерживает чувство сытости.\n\n"

            "🍃 <b>Экстракт зелёного чая</b>\n"
            "Поддерживает обменные процессы и бодрость.\n\n"

            "🌾 <b>Psyllium Husk</b>\n"
            "Поддерживает пищеварение.\n\n"

            "🟡 <b>Berberine HCl</b>\n"
            "Поддерживает обмен углеводов.\n\n"

            "⚡ <b>L-Carnitine</b>\n"
            "Участвует в энергетическом обмене.\n\n"

            "🌱 <b>Gymnema Sylvestre</b>\n"
            "Помогает контролировать тягу к сладкому.\n\n"

            "☕ <b>Caffeine Anhydrous</b>\n"
            "Поддерживает бодрость.\n\n"

            "🧘 <b>L-Theanine</b>\n"
            "Поддерживает баланс концентрации и спокойствия.\n\n"

            "🍊 <b>Vitamin C</b>\n"
            "Обеспечивает антиоксидантную поддержку.\n\n"

            "🌶 <b>Capsicum Extract</b>\n"
            "Поддерживает процессы термогенеза.\n\n"

            "⚫ <b>Black Pepper Extract</b>\n"
            "Поддерживает усвоение активных веществ.\n\n"

            "💎 <b>Chromium Picolinate</b>\n"
            "Поддерживает обмен глюкозы.\n\n"

            "📦 Точные количества проверяются по официальной "
            "этикетке продукта."
        ),

        "storage": (
            "📦 <b>Условия хранения</b>\n\n"
            "• Храните в сухом прохладном месте.\n"
            "• Берегите от прямого солнечного света.\n"
            "• Берегите от тепла и влаги.\n"
            "• Храните в недоступном для детей месте."
        ),

        "warnings": (
            "💚 <b>Напоминание</b>\n\n"
            "• Соблюдайте рекомендуемый режим приёма.\n"
            "• Не превышайте количество, указанное на этикетке.\n"
            "• Пейте достаточно воды в течение дня.\n"
            "• Для пользователей младше 18 лет бот не определяет "
            "количество капсул автоматически."
        ),

        "faq": (
            "❓ <b>Рекомендации</b>\n\n"
            "✅ Регулярно соблюдайте персональный режим приёма.\n"
            "✅ Придерживайтесь сбалансированного питания.\n"
            "✅ Пейте достаточно воды.\n"
            "✅ Ежедневно поддерживайте подходящую активность.\n"
            "✅ Отслеживайте вес и результаты каждую неделю."
        ),

        "usage": (
            "⏰ <b>Режим приёма</b>\n\n"
            "Капсулы принимаются перед едой и запиваются водой.\n\n"
            "Персональное количество и время указаны в разделе "
            "<b>Мой режим приёма</b>."
        ),

        "certificates": (
            "🏅 ISO 22000\n"
            "🏭 GMP\n"
            "🛡 HACCP\n"
            "🌿 HALAL\n"
            "🌍 FSSAI"
        ),
    },
}

