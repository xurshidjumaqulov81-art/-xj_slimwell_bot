# GitHub va Railway

1. ZIP ichidagi asosiy papkani oching.
2. Uning ichidagi `app`, `requirements.txt`, `Dockerfile`, `railway.json`
   va boshqa root fayllarni GitHub repository ildiziga yuklang.
3. Railway → Deploy from GitHub.
4. PostgreSQL qo‘shing.
5. Variables kiriting:
   - BOT_TOKEN
   - OPENAI_API_KEY
   - OPENAI_MODEL
   - DATABASE_URL
   - ADMIN_IDS
6. Deploy tugagach botga `/start` yuboring.

Eski database bilan ustunlar mos kelmasa, test bosqichida eski SQLite faylni
o‘chiring yoki yangi PostgreSQL bazadan foydalaning.
