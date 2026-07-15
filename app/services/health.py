from dataclasses import dataclass


@dataclass
class BodyMetrics:
    bmi: float
    min_weight: float
    max_weight: float
    reference_weight: float
    maintenance_kcal: int
    target_kcal: int | None


def calculate_metrics(
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    goal: str,
) -> BodyMetrics:
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)

    # Kattalar uchun umumiy BMI 18.5–24.9 oralig‘i.
    min_weight = 18.5 * height_m ** 2
    max_weight = 24.9 * height_m ** 2

    # Katalogdagi namuna formulasi: 22 × bo‘y².
    reference_weight = 22 * height_m ** 2

    # Mifflin–St Jeor. Faollik profilda olinmagani uchun yengil koeffitsiyent.
    sex_adjustment = 5 if gender == "Erkak" else -161
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + sex_adjustment
    maintenance = round(bmr * 1.35)

    target = maintenance
    if age >= 18 and goal == "Vaznni kamaytirish":
        # Keskin cheklovsiz, umumiy mo‘tadil farq.
        target = max(round(maintenance - 300), 1200 if gender == "Ayol" else 1500)
    elif age < 18 and goal == "Vaznni kamaytirish":
        target = None

    return BodyMetrics(
        bmi=round(bmi, 1),
        min_weight=round(min_weight, 1),
        max_weight=round(max_weight, 1),
        reference_weight=round(reference_weight, 1),
        maintenance_kcal=maintenance,
        target_kcal=target,
    )


def bmi_label(bmi: float) -> str:
    if bmi < 18.5:
        return "Kam vazn"
    if bmi < 25.0:
        return "Me’yoriy vazn"
    if bmi < 30.0:
        return "Ortiqcha vazn"
    if bmi < 35.0:
        return "1-darajali semizlik"
    if bmi < 40.0:
        return "2-darajali semizlik"
    return "3-darajali semizlik"


def bmi_guidance(bmi: float) -> str:
    if bmi < 18.5:
        return (
            "Muvozanatli ovqatlanish va yetarli energiya olishga e’tibor bering. "
            "Sababsiz vazn yo‘qotish bo‘lsa, mutaxassis bilan maslahatlashish muhim."
        )
    if bmi < 25.0:
        return (
            "Muntazam 3 mahal ovqatlanish, yetarli uyqu, suv va kundalik harakatni davom ettiring."
        )
    if bmi < 30.0:
        return (
            "Porsiyalarni nazorat qilish, shirin ichimliklarni kamaytirish va muntazam yurish foydali."
        )
    if bmi < 35.0:
        return (
            "Ovqatlanish va harakat rejasini bosqichma-bosqich yaxshilang. "
            "Sog‘liq muammolari bo‘lsa, mutaxassis bilan maslahatlashish tavsiya etiladi."
        )
    if bmi < 40.0:
        return (
            "Past zarbli mashqlar va muvozanatli ovqatlanishni tanlang. "
            "Shaxsiy reja uchun shifokor yoki dietolog bilan maslahatlashish ma’qul."
        )
    return (
        "Sog‘liq xavflarini baholash va xavfsiz reja tuzish uchun shifokor nazorati muhim. "
        "Keskin parhez yoki yuqori zo‘riqishli mashqlardan saqlaning."
    )
