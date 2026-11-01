# Invirep — 3D reklama v2 ("Bir tomchining yo'li"), Seedance 2.0

## Referensdan nimasi yaxshiroq
| Referens video | v2 |
|---|---|
| Bitta xona, qahramon 15 s davomida poza beradi | 7 shot, 4 joy: dala → uy → oshxona → dorixona; har shotda yangi voqea |
| Kamera deyarli turg'un, oddiy kesishlar | Har shotda kamera harakati + **match-cut** o'tishlar (tomchi → shudring, o't → flakon, flakon → quti) |
| Syujet yo'q, umumiy "himoya" | Aniq hikoya: **tarkibi o'tlardan → chayqating → suvga tomizing → shifokor bilan maslahat** — hammasi yo'riqnomadan |
| Esda qolarlik lahza yo'q | **"Chayqating!" raqsi** — doira ritmida qahramon o'zini chayqatadi (yo'riqnomada: ishlatishdan oldin chayqatish, jele suyuladi) — hook va meme |
| Odamlar yo'q | O'zbek oilasi, farmatsevt Dilnoza, Doktor Sardor — iliqlik va ishonch |
| 4 s statik yakun kartasi | Qahramon haqiqiy qutiga sakraydi → animatsion packshot + SP FARM kartasi (montajda biz) |
| Viruslar, gumbaz = himoya da'vosi | Qo'rqitish va da'vo yo'q — yuristdan oson o'tadi |

Format: 9:16, 1080p, 7 shot ≈ 25 s. Har shot 5 s generatsiya qilinadi, montajda kesiladi.

## Ishlab chiqarish qoidalari (sifat shu yerda hal bo'ladi)
1. **Avval qahramon varag'i**: SHOT 0 promptidan bitta rasm (front/side/back) — keyingi barcha shotlarga referens.
2. **Har shotga 2 referens**: qahramon varag'i + haqiqiy flakon packshoti (yorliq buzilmasligi uchun).
3. **Match-cut uchun**: oldingi klipning oxirgi kadrini keyingisining birinchi kadri (first frame) qilib bering.
4. 1080p, bir xil seed, har shotdan 2–3 variant — eng yaxshisini tanlaymiz.
5. Ovoz, musiqa, subtitr, rang (grade) — montajda biz.

## CHARACTER BLOCK (har promptning boshiga)
```
CHARACTERS (identical in every shot):
HERO "Invirep": a living 30 ml amber-brown glass medicine bottle, premium Pixar-quality 3D. White ribbed screw cap is its head, with a friendly expressive cartoon face (big warm brown eyes, thick dark eyebrows, rosy cheeks). White label on the body exactly like the reference image: teal-green Cyrillic "Инвиреп", pink gradient hand-holding-hand emblem, small teal "SPRING PHARMACEUTIC" logo. Slim segmented translucent amber-glass arms and legs, soft matte pink hands (#F2A7C3), small white sneakers. Proportions: compact and cute, not muscular. Inside the glass: dark-green liquid that glows softly.
PHARMACIST "Dilnoza": Uzbek woman, 30s, warm smile, dark hair in a neat bun, small gold earrings, white coat over a teal (#0E5E57) blouse, pink name badge.
DOCTOR "Sardor": Uzbek man, 40s, short dark hair, neatly trimmed beard, rectangular glasses, white coat, teal tie, grey stethoscope.
```

## SHOT 0 — qahramon varag'i (rasm, video emas)
```
[CHARACTER BLOCK — HERO only]
Character turnaround sheet of the HERO: front view, three-quarter view, side view, back view, plus three facial expressions (happy, surprised, determined), on a clean light grey background, even studio lighting, Pixar-quality 3D render, consistent proportions, label sharp and identical in every view. No other text.
```

## SHOT 1 (0–3 s) — Hook: tomchi
```
[CHARACTER BLOCK]
Vertical 9:16, 5 seconds. Extreme macro, ultra slow motion: a single glowing dark-green drop falls from above and lands in a white-and-blue Uzbek cotton-pattern piyola filled with clear water, forming a perfect crown splash. Camera then dives INTO the water surface, the water turns into a morning dew drop. Lighting: crisp backlight, sparkling highlights, deep black background. Colors: emerald green, clear water, cobalt blue pattern. Hyper-detailed, cinematic.
```

## SHOT 2 (3–6 s) — Dala o'tlari (tarkib)
```
[CHARACTER BLOCK]
Vertical 9:16, 5 seconds. Starts on a dew drop hanging on a blade of wild meadow grass, then the camera pulls back fast and rises like a drone over a golden sunrise meadow of tall wild field grasses with soft feathery seed heads, gentle hills and distant mountains of the Fergana valley, morning mist. Camera: macro-to-wide pull-back, then smooth drone rise. Lighting: golden-hour sun low on the horizon, volumetric rays through the mist. Colors: gold, fresh green, soft blue sky. Epic, calm, beautiful.
```

## SHOT 3 (6–10 s) — Tug'ilish
```
[CHARACTER BLOCK]
Vertical 9:16, 5 seconds. Grass blades and green light swirl in the wind and spiral together into the shape of the amber HERO bottle standing on a wooden windowsill of a cozy Tashkent apartment; outside the window, a rainy autumn evening with yellow trees and city lights. The glow fades, the hero blinks, opens its eyes, looks at the camera and smiles warmly. Camera: tight spiral orbit that slows down and settles on a front close-up. Lighting: warm interior lamp light vs cool blue rainy window. Colors: amber, warm yellow, cool blue, green glow.
```

## SHOT 4 (10–14 s) — "Chayqating!" (hook-lahza)
```
[CHARACTER BLOCK]
Vertical 9:16, 5 seconds. On the kitchen table, the HERO does a funny, rhythmic shake dance to an Uzbek doira drum beat: wiggles its body side to side, shakes its arms, spins once; the dark-green liquid inside swirls and sparkles, tiny glowing bubbles rise. Ends with a playful pose and a wink. Camera: low angle, handheld energy, quick push-in on the final pose. Lighting: warm kitchen light, sparkle highlights on the glass. Colors: amber, emerald sparkles, warm cream kitchen with blue-and-white Uzbek ceramics in the background. Comedic, joyful, high energy.
```

## SHOT 5 (14–18 s) — Oila oshxonasi: to'g'ri qabul qilish
```
[CHARACTER BLOCK]
Vertical 9:16, 5 seconds. Cozy Uzbek family kitchen in the evening, steam from a pot on the stove, fresh bread (non) on the table. A young Uzbek mother sits at the table holding a tablespoon of water; the HERO stands beside the spoon and carefully lets drops fall from its cap into the spoon, counting with its fingers; the mother smiles at the hero; a small wall clock is visible in the background. Camera: slow push-in over the table to a close-up of the spoon. Lighting: warm, homely, soft key light. Colors: warm amber and cream, teal accents.
```

## SHOT 6 (18–22 s) — Dorixona: shifokor maslahati
```
[CHARACTER BLOCK]
Vertical 9:16, 5 seconds. A bright, clean modern pharmacy with white and teal (#0E5E57) shelves (no readable brand names) and soft pink accents. DOCTOR Sardor and PHARMACIST Dilnoza stand together behind the counter; the HERO stands on the counter between them. The doctor speaks calmly and gestures toward the hero, the pharmacist nods and smiles, the hero gives a confident thumbs-up. Camera: smooth arc around the counter ending on a centered three-shot, all faces clearly visible. Lighting: soft bright daylight, gentle rim light. Colors: white coats, teal, soft pink, amber.
```

## SHOT 7 (22–25 s) — Qutiga sakrash (final)
```
[CHARACTER BLOCK]
Vertical 9:16, 4 seconds. Clean soft off-white studio background (#F5F5F7) with a subtle pink radial glow. The HERO waves goodbye to the camera, jumps up and lands inside an open white medicine box standing next to it, the box lid closes neatly, everything settles perfectly still, front-facing and centered. Leave the top and bottom thirds of the frame empty for text. Camera: locked-off, static. Lighting: soft studio key, clean reflections.
```

## Har promptning oxiriga
```
The bottle label and logo must stay exactly the same in every frame, no warping, no changed letters. No subtitles, no captions, no extra text, no watermark, no other brand logos. Smooth natural motion, consistent characters, cinematic quality.
```

## Montaj (biz)
- Match-cut o'tishlar, bitta rang grade (iliq, kinematografik), 1080×1920.
- Musiqa: zamonaviy o'zbekcha ritm (doira + sintez), SFX har harakatga, −14 LUFS.
- Ovozlar: Qahramon / Dilnoza / Sardor (matn — yo'riqnomadan, tibbiy bo'lim tasdig'i bilan).
- Animatsion o'zbekcha subtitrlar.
- Yakun: haqiqiy packshot + SP FARM kartasi (telefonlar, @spfarmmchj, spfarm.uz) + "Retsept bo'yicha beriladi. Qo'llashdan oldin yo'riqnomani o'qing."

## Ovoz matni (taklif)
| Vaqt | Kim | Matn |
|---|---|---|
| 0–3 | Qahramon | Bir tomchi... |
| 3–6 | Qahramon | ...yo'lini dala o'tlaridan boshlaydi. |
| 6–10 | Qahramon | Salom! Men — Invirep. Tarkibim ikki dala o'tining ekstrakti. |
| 10–14 | Qahramon | Ishlatishdan oldin — chayqating! |
| 14–18 | Dilnoza | Tomchilarni bir-ikki osh qoshiq suvga tomizing, ovqatdan 10–15 daqiqa oldin. |
| 18–22 | Sardor | Dozasi yoshga qarab — yo'riqnomaga qarang. Shifokor bilan maslahatlashing. |
| 22–25 | Uchalasi | Invirep. SP Farm. |
