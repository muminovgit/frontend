# Davo Delivery — animatsiyali splash

| Fayl | Nima |
|---|---|
| `davo-splash.json` | **Lottie animatsiya** (24 KB, vektor, foni shaffof). Dasturchiga shu fayl beriladi. |
| `davo-splash-preview.mp4` | Ko'rib chiqish uchun video (1080×1920). |
| `davo-splash-final-frame.png` | Oxirgi kadr: animatsiya tugagandagi holat. |
| `build_lottie.py` | JSON'ni qayta yasaydigan skript (rang, o'lcham, vaqtni o'zgartirish uchun). |

**Animatsiya:** 4 ta gulbarg markazdan birma-bir otilib chiqadi (sariq → pushti → yashil → binafsha), oq xoch aylanib joyiga tushadi, logo bir marta "nafas oladi", "Davo Delivery" yozuvi harfma-harf ko'tarilib chiqadi. Davomiyligi 2 soniya (60 fps), 1.3 soniyada tugaydi va qotib turadi. Kanvas 800×800, logo va yozuv markazda.

## Dasturchi uchun (ilovaga qo'yish)

Tizimning o'z splash ekrani (iOS LaunchScreen, Android 12+ SplashScreen API) animatsiyani qo'llamaydi. Shuning uchun:

1. **Tizim splash ekrani** — faqat oq fon (logosiz yoki faqat ilova ikonkasi). Shunda keyingi animatsiyaga o'tishda "sakrash" bo'lmaydi.
2. **Birinchi ekran (login oldidan)** — oq fon ustida markazda `davo-splash.json` bir marta o'ynatiladi (loop yo'q), tugagach login/asosiy sahifaga o'tiladi. Kenglik: ekran kengligining ~70–85%.

Kutubxonalar:
- **Flutter:** `lottie` — `Lottie.asset('assets/davo-splash.json', repeat: false, onLoaded: ...)`
- **React Native:** `lottie-react-native` — `<LottieView source={require('./davo-splash.json')} autoPlay loop={false} onAnimationFinish={...} />`
- **Android (native):** `com.airbnb.android:lottie` — `LottieAnimationView`, `app:lottie_rawRes`, `app:lottie_loop="false"`
- **iOS (native):** `lottie-ios` — `LottieAnimationView(name: "davo-splash")`, `loopMode = .playOnce`

Shrift kerak emas: yozuv harflari vektor shaklga aylantirilgan.

---

# 2-variant: "Dive" — to'liq ekranli yorqin splash (`davo-splash-dive.json`)

Dcard splash uslubida, Davo brendida. 1080×2340 (telefon ekrani), 2.6 soniya, 60 fps.

1. Logo va "Davo Delivery" bir qatorda turadi → harflar oxiridan boshlab logoga "so'riladi".
2. Logo markazga suzib kelib kattalashadi, bir lahza "cho'kadi" (sakrashga tayyorlanadi).
3. Kamera yashil gulbargning ichiga sho'ng'iydi: sariq, pushti, binafsha gulbarglar va oq xoch butun ekranni kesib o'tadi.
4. Ekran yashil; markazdan oq "+" xochlar va sariq nuqtalar to'lqin bo'lib portlab chiqadi.
5. Hammasi oqarib ketadi → ilovaning birinchi ekrani ochiladi (crossfade).

Ilovaga qo'yish: to'liq ekran, `scaleType="centerCrop"` (Android) / `contentMode = .scaleAspectFill` (iOS) / `fit: BoxFit.cover` (Flutter) / `resizeMode="cover"` (React Native). Bir marta o'ynatiladi, oxirida ekran oq bo'ladi — shu payt asosiy ekranga o'ting.
Hajmi ~390 KB. Ko'rish uchun: `davo-splash-dive-preview.mp4`. Qayta yasash: `python3 build_splash_dive.py`.

---

# 3 ta qo'shimcha uslub (`build_splash_styles.py`)

Hammasi 1080×2340, 60 fps, to'liq ekran (cover / centerCrop), oxirida logo + yozuv qotib turadi.

| Fayl | Uslub | Fon | Davomiyligi | Hajmi |
|---|---|---|---|---|
| `davo-splash-drop.json` | **Tomchi**: sariq tomchi tushadi → yerga urilib siqiladi, to'lqin halqa → 3 ta tomchi sachrab gulbarglarga aylanadi → oq xoch kesib o'tadi → yozuv pastdan ko'tariladi | oq | 2.5 s | 24 KB |
| `davo-splash-route.json` | **Yetkazish yo'li**: shahar xaritasi ustida kurer nuqtasi egri yo'l bo'ylab tezlashib kelib markazda tormozlaydi → yo'l orqasidan yig'iladi → logo portlab ochiladi, konfetti → yozuv o'ngdan suriladi | och havorang | 2.6 s | 60 KB |
| `davo-splash-capsule.json` | **Kapsula**: ikki rangli kapsula aylanib tushadi, qo'nadi, 0.45 s jimlik → chok bo'ylab nur → ochilib ketadi, ichidan logo va oq xochchalar otilib chiqadi → yozuv | to'q binafsha | 2.7 s | 41 KB |

Ko'rish: `davo-splash-3-styles.mp4` (uchalasi yonma-yon) yoki har birining `-preview.mp4` fayli.
Qayta yasash: `python3 build_splash_styles.py` (umumiy yordamchilar — `splash_lib.py`).

## Variantlar (har bir uslubdan 3 tadan)

`davo-splash-variants-grid.mp4` — 12 tasi bir ekranda (qator: Tomchi / Yetkazish yo'li / Kapsula; 1-ustun — asl variant).

| Fayl | Nima o'zgargan |
|---|---|
| `drop-rain` | 4 ta tomchi birma-bir o'z joyiga tushadi, har birining rangli to'lqini bor (oq fon) |
| `drop-night` | Tomchi, to'q fon, oq halqa va oq yozuv |
| `drop-sky` | Tomchi, ilovaning havorang foni, oq halqa |
| `route-night` | "24/7" tungi yetkazish: to'q xarita, sariq yo'l, oq yozuv |
| `route-pin` | Oq xarita, binafsha yo'l, kurer — xarita pini, yo'l o'ngdan keladi |
| `route-cream` | Iliq krem xarita, pushti yo'l, yashil kurer, yo'l tepadan keladi |
| `capsule-light` | Kapsula, och lavanda fon, to'q yozuv, binafsha uchqunlar |
| `capsule-roll` | Kapsula chapdan dumalab keladi, yotgan holda chap-o'ngga ochiladi; to'q yashil fon; sariq-pushti kapsula |
| `capsule-sky` | Kapsula, havorang fon, pushti-sariq kapsula |

---

# 9 ta har xil animatsiya g'oyasi (`build_splash_nine.py`)

Ranglar ataylab bir xil — farq faqat harakat g'oyasida. Tanlangandan keyin ranglar moslanadi.
Hammasini bir ekranda ko'rish: `davo-splash-nine-grid.mp4`.

| Fayl | G'oya |
|---|---|
| `n1-orbit` | Gulbarglar katta spiral bo'ylab ikki aylanib keladi, ortidan "iz" qoladi, joyiga tushganda logo siqilib "zarb" beradi, xoch aylanib kiradi |
| `n2-heartbeat` | EKG chizig'i ekranni kesib o'tadi; puls cho'qqisida logo "tuk-tuk" ikki marta uradi, har zarbda to'lqin |
| `n3-tiles` | 4 ta kvadrat to'rt tomondan uchib kelib to'qnashadi, keyin burchaklari yumaloqlanib doiraga aylanadi |
| `n4-draw` | Logo avval chiziq bo'lib chiziladi, keyin har doira rang bilan to'ladi |
| `n5-flip` | Ilova ikonkasi tushadi va tobora tezroq aylanadi: sariq → pushti → yashil → binafsha → logo |
| `n6-type` | "Davo Delivery" yozuv mashinkasidek teriladi; "o" harfi kattalashib logoga aylanadi, yozuv pastga tushadi |
| `n7-liquid` | Bo'sh doiralar to'lqinli suyuqlik bilan birma-bir to'ladi |
| `n8-notification` | "Davo Delivery — Buyurtmangiz yetib keldi!" bildirishnomasi tushadi, keyin ilova ikonkasiga aylanadi |
| `n9-particles` | Ekran bo'ylab sochilgan rangli nuqtalar oqib kelib logoni yig'adi |

---

# Dasturchi taklifi bo'yicha prototiplar (`build_splash_proposal.py`)

Faqat logotip elementlari (4 doira + oq xoch), oq fon, logo markazda, yozuvsiz. Hammasini bir ekranda: `davo-splash-proposal-grid.mp4`.

| Fayl | G'oya | Davomiyligi |
|---|---|---|
| `p1-bloom` ⭐ | **Gul ochilishi.** Kirish: ekranda faqat xoch (brend `#09BBD4` rangida, oq fonda ko'rinishi uchun), orqasidan 4 doira 60 ms oraliq bilan ochiladi (sariq → pushti → yashil → binafsha), ozgina sakrab o'tiradi, xoch oqaradi. Kutish: doiralar xoch atrofida sekin aylanadi (3 s/aylanish, uzluksiz). Chiqish: xoch kattalashib butun ekranni oq qiladi | kirish 0.7 s · kutish ∞ · chiqish 0.35 s |
| `p2-pulse` | **Puls.** Xoch bir lahza qisiladi, so'ng yurakdek "uriladi" (125%), shu kadrda 4 doira o'z rangidagi to'lqin bilan otilib chiqadi | 1.0 s |
| `p3-route` | **Yetkazish yo'li.** `#09BBD4` chiziq ekran bo'ylab chiziladi, oxiridagi nuqta logotipga aylanib ochiladi | 1.6 s |
| `p4-capsule` | **Kapsula.** Kapsula tushadi, chok bo'ylab nur, ochiladi — ichidan 4 doira | 1.8 s |
| `p5-minimal` | **Minimal.** Yumshoq paydo bo'lish + 0.95 → 1 masshtab | 0.6 s |

**p1 Lottie markerlari:** `intro` (0–42), `loop` (42–222), `outro` (222–243). Ilova: `intro`ni o'ynat → tayyor bo'lmasa `loop`ni takrorla → tayyor bo'lganda `outro`ni o'ynat va bosh sahifaga o't. Flutter'da: `lottie` paketi + `controller.animateTo` / segmentlar; yoki xuddi shu vaqtlar bilan `AnimationController + CustomPainter`.

**Native splash:** oq fonda faqat `#09BBD4` xoch (p1 va p2 ning birinchi kadri aynan shu) — animatsiya shu kadrdan sakrashsiz boshlanadi.
Eslatma: taklifda "oq fondagi oq xoch" deyilgan — oq fonda oq xoch ko'rinmaydi, shuning uchun xoch boshida brend rangida, doiralar orqasidan chiqqanda oqaradi.
Haptic: p1 da doiralar o'tirgan payt ≈ 0.55 s (33-kadr); p2 da zarb ≈ 0.33 s (20-kadr).
