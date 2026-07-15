import base64, json, re
from openai import AsyncOpenAI
from app.config import get_settings
from app.services.health import calculate

settings = get_settings()


def _json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def meal_plan(user, days: int) -> str:
    m = calculate(user)
    lang = "Russian" if user.language == "ru" else "Uzbek"
    if not settings.openai_api_key:
        if user.language == "ru":
            return "🍳 Завтрак: яйца, овощи и цельнозерновой хлеб\n\n🍲 Обед: курица/бобовые, крупа и салат\n\n🥗 Ужин: рыба/творог и овощи\n\n💧 Вода: по вашему плану."
        return "🍳 Nonushta: tuxum, sabzavot va butun donli non\n\n🍲 Tushlik: tovuq/loviya, donli garnir va salat\n\n🥗 Kechki ovqat: baliq/tvorog va sabzavot\n\n💧 Suv: rejangiz bo‘yicha."
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    prompt = f'''
Write in {lang}. Create a {days}-day meal plan with exactly 3 meals per day:
breakfast, lunch, dinner, plus water. Profile: age {user.age}, sex {user.gender},
height {user.height_cm}, weight {user.current_weight_kg}, target calories {m.target_kcal or m.maintenance_kcal}.
Use common foods available in Uzbekistan. Give portions and approximate calories.
No extreme restriction and no guaranteed weight-loss claims.
'''
    r = await client.responses.create(model=settings.openai_model, input=prompt, max_output_tokens=1800 if days == 7 else 700)
    return r.output_text.strip()


async def analyze_food(image: bytes) -> dict:
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI key missing")
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    data = base64.b64encode(image).decode()
    prompt = '''Return only JSON:
{"title":"","portion":"","calories":0,"protein_g":0,"fat_g":0,"carbs_g":0,"confidence":"","note":""}
Estimate food from the image cautiously.'''
    r = await client.responses.create(
        model=settings.openai_model,
        input=[{"role":"user","content":[
            {"type":"input_text","text":prompt},
            {"type":"input_image","image_url":f"data:image/jpeg;base64,{data}"}
        ]}],
        max_output_tokens=400,
    )
    return _json(r.output_text)
