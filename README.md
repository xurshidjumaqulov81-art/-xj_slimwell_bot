# XJ SlimWell Telegram Bot

Premium ko‘rinishdagi Telegram sog‘lom odatlar yordamchisi.

## Funksiyalar

- Profil: avtomatik 7 xonali SlimWell ID, ism, yosh, jins, bo‘y, vazn, maqsad
- BMI, sog‘lom vazn oralig‘i va taxminiy kaloriya ehtiyoji
- 3 mahal kunlik va 7 kunlik ovqatlanish rejasi
- Ovqat suratini OpenAI orqali taxminiy tahlil qilish
- Suv, qadam, uyqu va mashqlarni qayd etish
- SlimWell katalog ma’lumotlari
- Natijalar va admin kuzatuvi

## Railway Variables

```env
BOT_TOKEN=Telegram BotFather tokeni
OPENAI_API_KEY=OpenAI API kaliti
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=Railway PostgreSQL bergan URL
ADMIN_IDS=telegram_id_1,telegram_id_2
START_ID=12345
```

`DATABASE_URL` `postgres://` yoki `postgresql://` bilan boshlansa, dastur avtomatik ravishda asyncpg formatiga o‘giradi.

## Ishga tushirish

```bash
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

## Muhim

- Token va API kalitini GitHub’ga yuklamang.
- Ovqat rasmi va kaloriyalar taxminiy hisoblanadi.
- Bot tibbiy tashxis bermaydi.
- 18 yoshdan kichik foydalanuvchilarga vazn kamaytirish kaloriyasi avtomatik berilmaydi.
