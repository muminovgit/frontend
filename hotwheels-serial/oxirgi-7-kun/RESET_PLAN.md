# Oxirgi 7 kun — qayta boshlash rejasi

## 1. Animatsiya skilli tekshiruvi (cartoon-3d-short)
- Skill ishlaydi: Remotion + three.js, kadrlar chiqadi.
- **Asosiy muammo:** skill 3D binolar va jihozlar uchun Kenney to'plamlarini (`public/bridge/kenney/*.glb`, ~1.3 GB) talab qiladi.
  - Ular bizning muhitda yo'q edi: kenney.nl 403 qaytaradi.
  - Shuning uchun hovli, garaj, mashina va odamlar oddiy qutilardan yasalgan va xunuk chiqqan.
- Skill **multfilm uslubi** uchun yozilgan: 2D tekis qahramonlar, qora chiziqlar. Realistik uslub uchun mos emas.

## 2. GitHub'dan topilgan skillar (yuklab olinib o'qildi)
| Repo | Nima | Bizga |
|---|---|---|
| mromidev/claude-animated-shorts ★4.6k | Bizdagi cartoon-3d-short skilining aynan o'zi | Yangi narsa yo'q |
| mromidev/claude-blender-skills ★193 | Realistik Blender filmlari: blender-car-film, blender-forest, blender-film | Eng mos (haqiqiy mashina modeli, PBR, HDRI). Lekin GPU va Blender kerak |
| artemnovitckii/claude-animation-skills ★1.1k | 11 ta reels uslubi: low-poly, kurzgesagt, stick-figure... | Grafika uchun, realistik emas |
| viettranx/3dviz-pro-max ★1.5k | Three.js/Blender 3D vizualizatsiya | Mahsulot va sahna ko'rsatish uchun |

**Cheklov:** bu muhitda GPU yo'q (4 ta CPU, 15 GB RAM).
- Blender'ni yuklab olishga ruxsat berilmadi (avtomatik xavfsizlik tekshiruvi).
- Blender Cycles CPU'da 65 soniyalik video uchun 15–20+ soat ketadi.

## 3. Realistik yo'l (sinab ko'rildi, ishlaydi)
Hozirgi Remotion + three.js'da, lekin **haqiqiy PBR modellar** bilan:
- **Poly Haven (CC0):** "The Shed" ustaxona to'plami (stol, gira, asbob qutisi, javonlar, karton qutilar, chiroq, shina) va haqiqiy garaj HDRI yorug'ligi (`autoshop_01`).
- **Mashina:** haqiqiy avtomobil modeli 1:64 masshtabda (7.5 sm), yaltiroq "Spectraflame" bo'yog'i (metall + clearcoat).
- Sinov kadri: `ep1/look_test_v1.png`. Bitta kadr ~20 soniya, 65 soniyalik video ~3 soat.
- **Keyingi qadamlar:**
  - 1968-yil uslubidagi klassik mashina modelini topish (sinovdagi zamonaviy sport mashinasi faqat sinov uchun).
  - Stol yuzasiga makro tekstura qo'shish.
  - Orqa fondagi javonlarni to'ldirish.

## 4. Qahramonlar
Realistik odamni CPU'da, yuz mimikasi bilan qilish sifatsiz chiqadi.

**Taklif:**
- Kamera "o'yinchoq dunyosi" ichida bo'ladi: makro kadrlar, qo'llar, soyalar, siluetlar, xat va hujjatlar.
- Odamlar faqat qo'l, orqa yoki silueti bilan ko'rinadi.
- Bu realistik filmlarda ko'p ishlatiladigan usul (blender-car-film ham "odamsiz" film).

## 5. Yangi 1-qism ssenariysi
`ep1/SCRIPT_v2.md` faylida.
