# "Mashina tarixi": akkauntlar uchun brend to'plami

Hamma rasm `png/` papkasida, yuklashga tayyor. Ularning manbasi `svg/` papkasida.
O'zgartirish kerak bo'lsa: `src/gen_brand.py` ni tahrirlang, keyin quyidagilarni ishga tushiring:
```
python3 src/gen_brand.py && src/render.sh
```

Uslub videodagi bilan bir xil: kontur #221d1a, krem fon #f3ead8, qizil #c8352f, sariq #ffd34a va yakuniy kartadagi qizil mashina.

---

## 1. Nom va manzil (handle)

| | Instagram | YouTube | Telegram |
|---|---|---|---|
| **Ko'rinadigan nom** | `Mashina tarixi · Hot Wheels` | `Mashina tarixi` | `Mashina tarixi` |
| **Handle (1-variant)** | `@mashina.tarixi` | `@mashinatarixi` | `@mashinatarixi` |
| **Agar band bo'lsa** | `@mashinatarixi.uz` → `@mashina_tarixi` | `@mashinatarixi.uz` → `@mashina_tarixi` | `@mashina_tarixi` → `@mashinatarixi_uz` |

- Telegram username'da nuqta ishlatib bo'lmaydi, shuning uchun hamma joyda **`mashinatarixi`** shaklini qo'yish eng xavfsiz yo'l.
- Instagram'da "Name" maydoni qidiruvda ham ishlaydi. "Hot Wheels" so'zi shu maydonda tursa, o'yinchoq izlaganlar ham sahifani topadi.
- Handle'lar band yoki bo'shligini tekshira olmadim (Instagram login so'raydi). Akkaunt ochayotganda tekshirasiz.

## 2. Bio va tavsif

**Instagram bio** (150 belgigacha, bu matn 118 belgi):
```
🚗 Mashinalar tarixidagi haqiqiy, qiziq voqealar
🎬 Har hafta yangi animatsion qism
🏎 Hot Wheels: buyurtma Telegram'da 👇
```
- Havola: Telegram kanal (`t.me/mashinatarixi`).
- Kategoriya: **Video Creator** yoki **Education**.
- "Contact" tugmasi: Telegram.

**Telegram kanal tavsifi** (255 belgigacha, bu matn 168 belgi):
```
Avtomobillar tarixidagi haqiqiy va qiziq voqealar, o'zbek tilida va animatsiyada.
🎬 Har hafta yangi qism
🏎 Hot Wheels mashinalari sotuvda
Buyurtma: @mashinatarixi_admin
```
`@mashinatarixi_admin` o'rniga buyurtma qabul qiladigan akkaunt yoki botni qo'ying.

**YouTube tavsifi:**
```
Mashina tarixi: avtomobillar tarixidagi haqiqiy, hayratlanarli voqealar, o'zbek tilida, qisqa animatsiyalarda.

🚦 Dunyodagi birinchi svetofor nega portlab ketgan?
🚓 Birinchi tezlik jarimasi qancha bo'lgan?
🏎 Hot Wheels qanday tug'ilgan?

Har hafta yangi qism. Har bir videodagi faktlar tekshiriladi, manbalari tavsifda beriladi. Afsona bo'lsa, ochiq "afsona" deymiz.

📲 Telegram (Hot Wheels buyurtma): t.me/mashinatarixi
📸 Instagram: instagram.com/mashina.tarixi
```
- Kalit so'zlar (Settings → Channel → Basic info): `mashina tarixi, avtomobil tarixi, mashinalar, hot wheels, o'zbekcha multfilm, qiziq faktlar, svetofor, avto`.

## 3. Fayllar va qayerga yuklanadi

| Fayl | O'lcham | Qayerga |
|---|---|---|
| `png/avatar.png` | 1080×1080 | **Instagram, YouTube va Telegram profil rasmi** (hammasida bir xil). Kichkina doirada ham mashina tanilib turadi. |
| `png/avatar_yozuvli.png` | 1080×1080 | Zaxira variant: Telegram post muqovalari yoki katta ko'rinadigan joylar uchun. Profil rasmi uchun mos emas, chunki kichik doirada yozuv o'qilmaydi. |
| `png/youtube_banner.png` | 2560×1440 | **YouTube banner.** Yozuvlar markazdagi 1546×423 xavfsiz zonada, shuning uchun telefonda ham ko'rinadi. Qahramonlar kompyuter va televizorda chiqadi. |
| `png/muqova_01.png` | 1080×1920 | **1-qism muqovasi** (Reels "Cover" va Shorts thumbnail). Instagram profil to'rida 3:4 kesiladi, matn shu zona ichida turadi. |
| `png/highlight_*.png` | 1080×1920 | **Instagram Highlights muqovalari:** Qismlar, Hot Wheels, Buyurtma, Savollar, Manbalar. Highlight → Edit → Edit cover. |

**Keyingi qism muqovasi uchun:** epizoddan subtitrsiz kadr oling. Uni `src/kadr_NN.jpg` qilib saqlang va `src/gen_brand.py` dagi `EPISODES` ro'yxatiga bitta qator qo'shing.

## 4. Akkaunt ochish tartibi (sizning qadamlaringiz)
1. **Telegram kanal:** nom, username, tavsif va avatar. Hammasidan oldin ochiladi, chunki boshqa platformalardagi havolalar shunga ishora qiladi.
2. **Instagram:** oching → Settings → "Switch to professional account" → **Business** → Facebook sahifaga ulang. Post joylashni API orqali avtomatlashtirish uchun bu kerak.
3. **YouTube:** kanal yarating → avatar, banner, tavsif va handle qo'ying → Shorts'ga 1-qismni `muqova_01.png` bilan yuklang.
4. Uchala platformada ham nom va avatar **bir xil** bo'lsin.

## Eslatma
- Sarlavhalarda `Arial Black` shrifti ishlatilgan. Videodagi DejaVu Sans Bold bu Mac'da o'rnatilmagan, shuning uchun harflar videodagidan biroz qalinroq. Bir xil bo'lishi kerak bo'lsa, DejaVu Sans'ni o'rnating, `src/gen_brand.py` dagi `FONT` qatorida uni birinchi qo'ying va qayta render qiling.
