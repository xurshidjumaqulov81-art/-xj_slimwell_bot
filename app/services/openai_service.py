import base64
import json
import re

from openai import AsyncOpenAI

from app.config import get_settings
from app.database.base import User

settings = get_settings()


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def generate_meal_plan(user: User, days: int = 1) -> str:
    if not settings.openai_api_key:
        return fallback_meal_plan(days)

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    age_rule = (
        "Foydalanuvchi 18 yoshdan kichik. Kaloriya tanqisligi yoki ozish dietasi bermang; "
        "faqat muvozanatli 3 mahal ovqatlanish va umumiy sog‘lom odatlar bering."
        if (user.age or 0) < 18 else
        "Reja keskin cheklovsiz va xavfsiz, barqaror tamoyillarga asoslangan bo‘lsin."
    )
    prompt = f'''
O‘zbek tilida {days} kunlik, har kuni faqat 3 mahal: nonushta, tushlik, kechki ovqat va suv tavsiyasi tuzing.
Profil: yosh {user.age}, jins {user.gender}, bo‘y {user.height_cm} sm, vazn {user.current_weight_kg} kg,
maqsad: {user.goal}. {age_rule}
Har ovqat uchun taom, porsiya, taxminiy kkal va qisqa tayyorlash usulini yozing.
O‘zbekistonda topiladigan oddiy mahsulotlardan foydalaning. Juda uzun yozmang.
'''
    response = await client.responses.create(
        model=settings.openai_model,
        input=prompt,
        max_output_tokens=1800 if days == 7 else 700,
    )
    return response.output_text.strip()


async def analyze_food_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY kiritilmagan.")

    encoded = base64.b64encode(image_bytes).decode("ascii")
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    prompt = '''
Rasmdagi ovqatni taxminiy tahlil qil. Faqat JSON qaytar:
{
  "title": "taom nomi",
  "portion": "taxminiy porsiya",
  "calories": 0,
  "protein_g": 0,
  "fat_g": 0,
  "carbs_g": 0,
  "confidence": "past/o‘rta/yuqori",
  "note": "aniqlikka ta’sir qiluvchi qisqa izoh"
}
Bitta rasmdan aniq bilib bo‘lmaydigan yog‘, sous va porsiya bo‘yicha ehtiyotkor taxmin qil.
'''
    response = await client.responses.create(
        model=settings.openai_model,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:{mime_type};base64,{encoded}"},
            ],
        }],
        max_output_tokens=500,
    )
    return _extract_json(response.output_text)


def fallback_meal_plan(days: int) -> str:
    one = (
        "🍳 <b>Nonushta:</b> 2 dona tuxum, sabzavot va 1 bo‘lak butun donli non — ~400 kkal\n\n"
        "🍲 <b>Tushlik:</b> 150 g tovuq yoki loviya, 120 g guruch/grechka, salat — ~650 kkal\n\n"
        "🥗 <b>Kechki ovqat:</b> 150 g baliq yoki tvorog, ko‘p sabzavot — ~450 kkal\n\n"
        "💧 <b>Suv:</b> Kun davomida muntazam iching; chanqoq va ob-havoga qarab moslang."
    )
    if days == 1:
        return one
    return "\n\n".join([f"<b>{i}-kun</b>\n{one}" for i in range(1, 8)])

