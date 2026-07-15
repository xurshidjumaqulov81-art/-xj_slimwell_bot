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


def calculate_body_metrics(
    user: User,
) -> BodyMetrics:
    if not all(
        [
            user.age,
            user.gender,
            user.height_cm,
            user.current_weight_kg,
        ]
    ):
        raise ValueError(
            "Profil ma’lumotlari to‘liq emas."
        )

    height_m = user.height_cm / 100

    bmi_value = (
        user.current_weight_kg
        / (height_m ** 2)
    )

    category_key = get_bmi_category_key(
        bmi_value
    )

    normal_min_weight = (
        18.5 * (height_m ** 2)
    )

    normal_max_weight = (
        24.9 * (height_m ** 2)
    )

    # Foydalanuvchi so‘ragan ideal vazn:
    # BMI 22 asosidagi markaziy ko‘rsatkich.
    ideal_weight = (
        22 * (height_m ** 2)
    )

    if user.gender == "male":
        gender_adjustment = 5
    else:
        gender_adjustment = -161

    # Mifflin–St Jeor formulasi.
    bmr_value = (
        10 * user.current_weight_kg
        + 6.25 * user.height_cm
        - 5 * user.age
        + gender_adjustment
    )

    activity_factor = (
        ACTIVITY_FACTORS.get(
            user.activity or "low",
            1.20,
        )
    )

    maintenance_kcal = round(
        bmr_value * activity_factor
    )

    target_kcal: int | None

    if user.age < 18:
        # Voyaga yetmagan foydalanuvchiga
        # avtomatik keskin kaloriya tanqisligi berilmaydi.
        target_kcal = None

    elif user.goal == "lose":
        minimum_kcal = (
            1500
            if user.gender == "male"
            else 1200
        )

        target_kcal = max(
            round(
                maintenance_kcal - 700
            ),
            minimum_kcal,
        )

    elif user.goal == "habits":
        minimum_kcal = (
            1500
            if user.gender == "male"
            else 1200
        )

        target_kcal = max(
            round(
                maintenance_kcal - 300
            ),
            minimum_kcal,
        )

    else:
        target_kcal = maintenance_kcal

    calories_for_macros = (
        target_kcal
        if target_kcal is not None
        else maintenance_kcal
    )

    protein_g = round(
        min(
            max(
                user.current_weight_kg * 1.4,
                80,
            ),
            180,
        )
    )

    fat_g = round(
        max(
            user.current_weight_kg * 0.7,
            45,
        )
    )

    protein_calories = protein_g * 4
    fat_calories = fat_g * 9

    carbs_g = round(
        (
            calories_for_macros
            - protein_calories
            - fat_calories
        )
        / 4
    )

    carbs_g = max(
        carbs_g,
        80,
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


def get_bmi_plan(
    user: User,
    language: str,
) -> tuple[BodyMetrics, dict[str, object]]:
    metrics = calculate_body_metrics(
        user
    )

    plan = BMI_PLANS[
        metrics.category_key
    ][language]

    return metrics, plan


def calculate_remaining_weight(
    user: User,
    metrics: BodyMetrics,
) -> float:
    remaining = (
        user.current_weight_kg
        - metrics.normal_max_weight
    )

    return round(
        max(
            remaining,
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
                "автоматический дефицит калорий не рассчитывается."
            )

        return (
            "18 yoshgacha avtomatik kaloriya "
            "tanqisligi hisoblanmaydi."
        )

    if language == "ru":
        return (
            f"⚡ Дневная цель: "
            f"<b>{metrics.target_kcal} ккал</b>\n\n"
            f"🥩 Белок: <b>{metrics.protein_g} г</b>\n"
            f"🥑 Жиры: <b>{metrics.fat_g} г</b>\n"
            f"🍚 Углеводы: <b>{metrics.carbs_g} г</b>"
        )

    return (
        f"⚡ Kunlik maqsad: "
        f"<b>{metrics.target_kcal} kkal</b>\n\n"
        f"🥩 Oqsil: <b>{metrics.protein_g} g</b>\n"
        f"🥑 Yog‘: <b>{metrics.fat_g} g</b>\n"
        f"🍚 Uglevod: <b>{metrics.carbs_g} g</b>"
    )
