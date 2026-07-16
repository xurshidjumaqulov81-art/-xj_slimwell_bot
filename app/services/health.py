from dataclasses import dataclass

from app.content import BMI_PLANS
from app.database.models import User


ACTIVITY_FACTORS: dict[str, float] = {
    "low": 1.20,
    "light": 1.375,
    "medium": 1.55,
    "high": 1.725,
}


@dataclass(frozen=True)
class BodyMetrics:
    bmi: float
    category_key: str

    normal_min_weight: float
    normal_max_weight: float
    ideal_weight: float

    bmr: int
    maintenance_kcal: int
    target_kcal: int | None

    protein_g: int
    fat_g: int
    carbs_g: int


def get_bmi_category_key(
    bmi: float,
) -> str:
    if bmi < 18.5:
        return "underweight"

    if bmi < 25:
        return "normal"

    if bmi < 30:
        return "overweight"

    if bmi < 35:
        return "obesity_1"

    if bmi < 40:
        return "obesity_2"

    return "obesity_3"


def validate_profile(
    user: User,
) -> None:
    required_values = {
        "age": user.age,
        "gender": user.gender,
        "height_cm": user.height_cm,
        "current_weight_kg": user.current_weight_kg,
    }

    missing_fields = [
        field
        for field, value in required_values.items()
        if value is None
    ]

    if missing_fields:
        raise ValueError(
            "Profil ma’lumotlari to‘liq emas."
        )

    if user.gender not in {
        "male",
        "female",
    }:
        raise ValueError(
            "Jins noto‘g‘ri ko‘rsatilgan."
        )

    if not 120 <= user.height_cm <= 230:
        raise ValueError(
            "Bo‘y qiymati noto‘g‘ri."
        )

    if not 30 <= user.current_weight_kg <= 300:
        raise ValueError(
            "Vazn qiymati noto‘g‘ri."
        )

    if not 13 <= user.age <= 100:
        raise ValueError(
            "Yosh qiymati noto‘g‘ri."
        )


def calculate_body_metrics(
    user: User,
) -> BodyMetrics:
    validate_profile(user)

    height_m = user.height_cm / 100

    bmi_value = (
        user.current_weight_kg
        / (
            height_m ** 2
        )
    )

    category_key = get_bmi_category_key(
        bmi_value
    )

    normal_min_weight = (
        18.5
        * (
            height_m ** 2
        )
    )

    normal_max_weight = (
        24.9
        * (
            height_m ** 2
        )
    )

    ideal_weight = (
        22
        * (
            height_m ** 2
        )
    )

    if user.gender == "male":
        gender_adjustment = 5
    else:
        gender_adjustment = -161

    bmr_value = (
        10
        * user.current_weight_kg
        + 6.25
        * user.height_cm
        - 5
        * user.age
        + gender_adjustment
    )

    activity_factor = ACTIVITY_FACTORS.get(
        user.activity or "low",
        1.20,
    )

    maintenance_kcal = round(
        bmr_value
        * activity_factor
    )

    target_kcal = calculate_target_calories(
        user=user,
        maintenance_kcal=maintenance_kcal,
    )

    calories_for_macros = (
        target_kcal
        if target_kcal is not None
        else maintenance_kcal
    )

    protein_g = calculate_protein(
        user.current_weight_kg
    )

    fat_g = calculate_fat(
        user.current_weight_kg
    )

    carbs_g = calculate_carbs(
        calories=calories_for_macros,
        protein_g=protein_g,
        fat_g=fat_g,
    )

    return BodyMetrics(
        bmi=round(
            bmi_value,
            2,
        ),
        category_key=category_key,
        normal_min_weight=round(
            normal_min_weight,
            1,
        ),
        normal_max_weight=round(
            normal_max_weight,
            1,
        ),
        ideal_weight=round(
            ideal_weight,
            1,
        ),
        bmr=round(
            bmr_value,
        ),
        maintenance_kcal=maintenance_kcal,
        target_kcal=target_kcal,
        protein_g=protein_g,
        fat_g=fat_g,
        carbs_g=carbs_g,
    )


def calculate_target_calories(
    user: User,
    maintenance_kcal: int,
) -> int | None:
    if user.age < 18:
        return None

    if user.goal == "lose":
        calorie_deficit = 650

        minimum_kcal = (
            1500
            if user.gender == "male"
            else 1200
        )

        return max(
            round(
                maintenance_kcal
                - calorie_deficit
            ),
            minimum_kcal,
        )

    if user.goal == "habits":
        calorie_deficit = 250

        minimum_kcal = (
            1500
            if user.gender == "male"
            else 1200
        )

        return max(
            round(
                maintenance_kcal
                - calorie_deficit
            ),
            minimum_kcal,
        )

    return maintenance_kcal


def calculate_protein(
    weight_kg: float,
) -> int:
    protein = weight_kg * 1.4

    return round(
        min(
            max(
                protein,
                80,
            ),
            180,
        )
    )


def calculate_fat(
    weight_kg: float,
) -> int:
    fat = weight_kg * 0.7

    return round(
        min(
            max(
                fat,
                45,
            ),
            120,
        )
    )


def calculate_carbs(
    calories: int,
    protein_g: int,
    fat_g: int,
) -> int:
    protein_calories = (
        protein_g * 4
    )

    fat_calories = (
        fat_g * 9
    )

    remaining_calories = (
        calories
        - protein_calories
        - fat_calories
    )

    carbs_g = round(
        remaining_calories / 4
    )

    return max(
        carbs_g,
        80,
    )


def get_bmi_plan(
    user: User,
    language: str,
) -> tuple[
    BodyMetrics,
    dict[str, object],
]:
    metrics = calculate_body_metrics(
        user
    )

    selected_language = (
        language
        if language in {
            "uz",
            "ru",
        }
        else "uz"
    )

    plan = BMI_PLANS[
        metrics.category_key
    ][selected_language]

    return (
        metrics,
        plan,
    )


def calculate_remaining_weight(
    user: User,
    metrics: BodyMetrics,
) -> float:
    remaining_weight = (
        user.current_weight_kg
        - metrics.normal_max_weight
    )

    return round(
        max(
            remaining_weight,
            0,
        ),
        1,
    )


def get_calorie_text(
    metrics: BodyMetrics,
    language: str,
) -> str:
    if metrics.target_kcal is None:
        if language == "ru":
            return (
                "Для пользователей младше 18 лет "
                "автоматическая цель по снижению "
                "калорий не рассчитывается."
            )

        return (
            "18 yoshgacha bo‘lgan foydalanuvchi "
            "uchun avtomatik kaloriya kamaytirish "
            "maqsadi hisoblanmaydi."
        )

    if language == "ru":
        return (
            "🎯 Дневная цель:\n"
            f"<b>{metrics.target_kcal} ккал</b>\n\n"
            f"🥩 Белок: "
            f"<b>{metrics.protein_g} г</b>\n"
            f"🥑 Жиры: "
            f"<b>{metrics.fat_g} г</b>\n"
            f"🍚 Углеводы: "
            f"<b>{metrics.carbs_g} г</b>"
        )

    return (
        "🎯 Kunlik maqsad:\n"
        f"<b>{metrics.target_kcal} kkal</b>\n\n"
        f"🥩 Oqsil: "
        f"<b>{metrics.protein_g} g</b>\n"
        f"🥑 Yog‘: "
        f"<b>{metrics.fat_g} g</b>\n"
        f"🍚 Uglevod: "
        f"<b>{metrics.carbs_g} g</b>"
    )

