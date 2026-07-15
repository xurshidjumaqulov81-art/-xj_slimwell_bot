LINE = "━━━━━━━━━━━━━━━━━━━━"


def card(title: str, body: str) -> str:
    return f"{LINE}\n<b>{title}</b>\n{LINE}\n\n{body}"


TERMS = card(
    "🔐 FOYDALANISH SHARTLARI",
    "Botdagi hisob-kitoblar umumiy va taxminiydir. Ular tibbiy tashxis o‘rnini bosmaydi. "
    "Ovqat suratidan aniqlangan kaloriyalar porsiya va tayyorlash usuliga qarab farq qilishi mumkin.\n\n"
    "Davom etish orqali profilingiz va kundalik qaydlaringiz bot bazasida saqlanishiga rozilik bildirasiz."
)

SLIMWELL = {
    "about": "XJ SlimWell — sog‘lom vaznni qo‘llab-quvvatlash uchun mo‘ljallangan nutrikosmetik qo‘shimcha. Dori vositasi emas.",
    "ingredients": (
        "Glukomannan — 300 mg\nGreen Tea Extract — 200 mg\nPsyllium Husk — 150 mg\n"
        "Berberine HCl — 100 mg\nL-Carnitine — 100 mg\nGymnema Sylvestre Extract — 75 mg\n"
        "Caffeine Anhydrous — 75 mg\nL-Theanine — 50 mg\nVitamin C — 50 mg\n"
        "Capsicum Extract — 15 mg\nBlack Pepper Extract — 2.5 mg\nChromium Picolinate — 100 mcg"
    ),
    "usage": (
        "Yorliqda porsiya hajmi 3 kapsula deb ko‘rsatilgan. Aniq qabul qilish tartibi sog‘liq holatiga "
        "va mutaxassis tavsiyasiga bog‘liq. Yorliqdan tashqari doza qabul qilmang."
    ),
    "warnings": (
        "Bolalardan yiroqda saqlang. Homiladorlik, emizish, dori qabul qilish, kuchli allergiya yoki "
        "surunkali kasallik bo‘lsa, ishlatishdan oldin shifokor bilan maslahatlashish kerak."
    ),
    "storage": "Salqin, quruq va qorong‘i joyda saqlang. To‘g‘ridan-to‘g‘ri quyosh nuri va issiqlikdan himoya qiling.",
    "certificates": "Katalogda FSSAI, ISO, GMP, HACCP va Halal belgilariga oid ma’lumotlar ko‘rsatilgan.",
    "faq": (
        "• Mahsulot dori emas.\n• Natija kafolatlanmaydi va odamlarda turlicha bo‘ladi.\n"
        "• Sog‘lom ovqatlanish, uyqu va harakat bilan birga qo‘llash muhim.\n"
        "• Noqulaylik kuzatilsa, qabul qilishni to‘xtatib mutaxassisga murojaat qiling."
    ),
}
