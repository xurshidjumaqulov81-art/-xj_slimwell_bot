# XJ SlimWell Bot v3

Ixcham, menyuli Telegram bot.

## Asosiy imkoniyatlar

- `/start` dan keyin O‘zbek/Rus tilini tanlash
- Foydalanuvchi o‘zi kiritadigan noyob 7 xonali shaxsiy ID
- Profil: ism, yosh, jins, bo‘y, vazn, maqsad, faollik
- BMI ikki xonali aniqlikda
- Animatsion BMI o‘lchagich va jinsga mos tana rasmi
- Norma vazn oralig‘i (BMI 18.5–24.9) va ideal vazn (BMI 22)
- Faollikka mos kaloriya hisobi
- 3 mahal kunlik/haftalik menyu
- Ovqat suratidan taxminiy kaloriya
- SlimWell bo‘limi: qabul rejasi, tarkib, saqlash, sertifikatlar
- BMI ga mos 3 ta uy mashqi va animatsiyalar
- Suv, qadam, uyqu, vazn va natijalar
- Admin: foydalanuvchini 7 xonali ID bilan topish

## Railway Variables

```env
BOT_TOKEN=...
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=...
ADMIN_IDS=123456789
```

`DATABASE_URL` Railway PostgreSQL bergan qiymat bo‘lishi mumkin.
Token va kalitlarni GitHub kodiga yozmang.

## Muhim sozlama

SlimWell qabul rejasi `app/content.py` ichida. Hozir u katalogdan olingan
2 yoki 3 kapsulalik reja bilan cheklangan va yorliqdagi 3 kapsuladan oshmaydi.
Mahsulotning tasdiqlangan yo‘riqnomasi o‘zgarsa, shu fayl yangilanadi.
