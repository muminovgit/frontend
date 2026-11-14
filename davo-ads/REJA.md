# Davo Delivery — 13 ta motion kreativ: reja (v1)

Manba: mijozning texnik topshirig'i (13 sarlavha, 3 punkt, CTA) + 5 ta referens banner. Odam ishtirok etmaydi.

## 1. Format
| | |
|---|---|
| Asosiy | 9:16 (1080×1920) Reels / Stories / TikTok, **8 s**, loop bo'ladigan oxir |
| Qo'shimcha | 4:5 (1080×1350) lenta uchun — xuddi shu animatsiya, boshqa joylashuv |
| Bonus | har videoning "asosiy kadri" → statik banner (PNG), TZ ga to'liq mos |
| Jami | 13 × (9:16 + 4:5) = 26 video + 13 banner |

## 2. Har bir videoning skeleti (8 s)
| Vaqt | Beat | Nima bo'ladi |
|---|---|---|
| 0.0–0.3 | **Hook-zarba** | ekran keskin ochiladi: kinetik so'z yoki emoji-stiker "urilib" tushadi, kamera silkinishi + tovush |
| 0.3–2.2 | **Sarlavha** | asosiy sarlavha so'zma-so'z (word-pop), katta, o'qishga oson; kalit so'z rang bilan ajratiladi |
| 2.2–5.0 | **Isbot / demo** | 3D telefon (haqiqiy ilova ekranlari) + mavzuga mos motion: narx bar-poygasi, xarita pinlari, kategoriya renderlari, yetkazish taymeri |
| 5.0–6.6 | **3 punkt** | `⏱ 30 daqiqada yetkazib beramiz` · `✓ Faqat litsenziyali mahsulotlar` · `📍 200+ rasmiy dorixona` — glass-kartochkalar birma-bir "chiqib keladi" |
| 6.6–8.0 | **CTA** | logo + "Ilovani yuklab oling" tugmasi pulsatsiya + App Store / Google Play; oxirgi kadr 1-kadrga mos → cheksiz loop |

Sarlavha matni TZ dagidek, so'zlari o'zgartirilmaydi; uzun sarlavhalar (2, 6) ikki beatga bo'linadi.

## 3. Shablonlar (4 tur) va sarlavhalar
| Shablon | Asosiy motion | Sarlavhalar |
|---|---|---|
| **A · Narx solishtirish** | bitta dori kartochkasi → 3 dorixona narxi "poyga" bar-chart bo'lib o'sadi, eng arzoni yashil "✓ eng arzon" belgisi bilan yonadi | 1, 5, 6, 13 |
| **B · Vaziyat → yechim** | katta emoji-stiker (🤧 tumov, 🤢 zaharlanish, 🏠 uy, 🔁 har hafta) → telefon ichida buyurtma → kuryer marshruti xaritada → eshik "ding" | 3, 8, 11, 12 |
| **C · Kategoriya** | saytdagi 3D renderlar (aptechka, vitaminlar, chaqaloq, kosmetika) orbitada aylanib, telefonga "tushadi" | 7, 9, 10 |
| **D · Qidiruv demo** | haqiqiy qidiruv maydoniga yozish → natijalar → "30:00" taymer pastga sanaladi | 2, 4 |

## 4. Viral motion texnikalari (hammasi bizning pipelineda)
1. **0.3 s hook-zarba** + sound-sync — skrollni to'xtatadi.
2. **Kinetik tipografiya** (word-pop, squash/stretch, kalit so'z rangda) — ovozsiz ham tushunarli (Reels ko'p ovozsiz ko'riladi).
3. **3D telefon tilt + "zoom-through"** — kamera ekran ichiga kirib keyingi sahnaga o'tadi (match-cut).
4. **Ma'lumot-animatsiya**: narx bar-poygasi, sanovchi raqamlar, xarita pin-yomg'iri.
5. **Glassmorphism kartochkalar** — referenslardagi uslub, lekin harakatda.
6. **Loop oxiri** — video qayta boshlanganini sezdirmaydi → ko'rish vaqti oshadi.
7. **Har bir harakatga tovush** (pop, whoosh, tick, ding) + energik bit; ixtiyoriy o'zbekcha diktor.

## 5. Brend
Logo vektorda (avvalgi reeldan): sariq `#FFCE68`, pushti `#FB4669`, binafsha `#5E3A9A`, yashil `#01BDAC`. Shriftlar: Montserrat / Inter. Fon variantlari: to'q binafsha (referens 1) va och (referens 2–5) — A/B test uchun ikkalasi.

## 6. Ishlab chiqarish
1. Bitta parametrli shablon (`seek(t)` HTML) + `variants.json` (13 sarlavha, shablon turi, ranglar).
2. Avval **3 ta pilot**: #1 (A), #8 (B), #2 (D) — tasdiqdan keyin qolgan 10 tasi.
3. Batch render 60fps motion blur, −14 LUFS, kadrma-kadr tekshiruv.

## 7. Mijozdan tasdiq kerak
1. **200+ yoki 2000+?** TZ: "200+ rasmiy dorixona"; referens 1: "2000+". Bitta raqam kerak.
2. **"30 daqiqada"** — butun Toshkent bo'ylab kafolatmi? Aks holda pastda kichik izoh ("Toshkent bo'ylab, o'rtacha").
3. **#9 Bolalar tovarlari** — ilovada "Chaqaloqlar uchun" bo'limi avval "tez orada" edi. Hozir ishlayaptimi?
4. **#7 Tibbiy qurilma va testlar** — ilovada bormi (skrinshot)?
5. **Narx solishtirish (A)** — haqiqiy misol narxlar (dori nomi + 3 dorixona narxi) yoki "namuna" deb belgilaymizmi?
6. Referensdagi "Birinchi 3 ta buyurtma — yetkazib berish BEPUL" aksiyasi hozir amaldami? (TZ da yo'q — ishlatmaymiz)
7. Diktor ovozi kerakmi? (bepul TTS reklama uchun litsenziyasiz → Azure yoki haqiqiy diktor)
