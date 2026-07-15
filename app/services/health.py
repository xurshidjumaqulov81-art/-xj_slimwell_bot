from dataclasses import dataclass
from app.content import BMI_PLANS


ACTIVITY = {
    "low": 1.2,
    "light": 1.375,
    "medium": 1.55,
    "high": 1.725,
}


@dataclass(frozen=True)
class Metrics:
    bmi: float
    category_key: str
    normal_min: float
    normal_max: float
    ideal_weight: float
    maintenance_kcal: int
    target_kcal: int | None
    protein_g: int
    fat_g: int
    carbs_g: int


def category_key(bmi: float) -> str:
    if bmi < 18.5:
        return "normal"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "overweight"
    if bmi < 35:
        return "obesity1"
    if bmi < 40:
        return "obesity2"
    return "obesity3"


def calculate(user) -> Metrics:
    h = user.height_cm / 100
    bmi = user.current_weight_kg / (h * h)
    normal_min = 18.5 * h * h
    normal_max = 24.9 * h * h
    ideal = 22 * h * h

    sex = 5 if user.gender == "male" else -161
    bmr = 10 * user.current_weight_kg + 6.25 * user.height_cm - 5 * user.age + sex
    maintenance = round(bmr * ACTIVITY.get(user.activity or "low", 1.2))

    target = maintenance
    if user.goal == "lose":
        if user.age < 18:
            target = None
        else:
            floor = 1500 if user.gender == "male" else 1200
            target = max(round(maintenance - 700), floor)
    elif user.goal == "habits":
        target = max(round(maintenance - 300), 1300)

    macro_kcal = target or maintenance
    protein = round(min(max(user.current_weight_kg * 1.4, 80), 180))
    fat = round(max(user.current_weight_kg * 0.7, 45))
    carbs = max(round((macro_kcal - protein * 4 - fat * 9) / 4), 80)

    return Metrics(
        bmi=round(bmi, 2),
        category_key=category_key(bmi),
        normal_min=round(normal_min, 1),
        normal_max=round(normal_max, 1),
        ideal_weight=round(ideal, 1),
        maintenance_kcal=maintenance,
        target_kcal=target,
        protein_g=protein,
        fat_g=fat,
        carbs_g=carbs,
    )


def plan_for(user, lang: str):
    metrics = calculate(user)
    return metrics, BMI_PLANS[metrics.category_key][lang]



def capsule_schedule(capsules: int, lang: str) -> str:
    if lang == "ru":
        if capsules == 2:
            return "🌅 1 капсула перед завтраком\n☀️ 1 капсула перед обедом"
        return "🌅 1 капсула перед завтраком\n☀️ 1 капсула перед обедом\n🌙 1 капсула перед ужином"
    if capsules == 2:
        return "🌅 1 kapsula nonushtadan oldin\n☀️ 1 kapsula tushlikdan oldin"
    return "🌅 1 kapsula nonushtadan oldin\n☀️ 1 kapsula tushlikdan oldin\n🌙 1 kapsula kechki ovqatdan oldin"
