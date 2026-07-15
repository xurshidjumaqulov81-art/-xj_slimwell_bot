# GitHub va Railway bo‘yicha ketma-ketlik

1. ZIP faylni kompyuterda oching.
2. Ichidagi barcha fayl va papkalarni GitHub repository ildiziga yuklang.
3. Railway → New Project → Deploy from GitHub Repo.
4. Repository sifatida `-xj_slimwell_bot` ni tanlang.
5. Railway ichida PostgreSQL qo‘shing.
6. Bot service Variables bo‘limiga quyidagilarni kiriting:
   - `BOT_TOKEN`
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL=gpt-4o-mini`
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}` (Postgres service nomiga mos)
   - `ADMIN_IDS` — o‘zingizning Telegram raqamli ID’ingiz
   - `START_ID=12345`
7. Deploy logida `Start polling`ga yaqin yozuvlar chiqishini kuting.
8. Telegram botga `/start` yuboring.

Tokenlar va kalitlarni GitHub fayllariga yozmang.
