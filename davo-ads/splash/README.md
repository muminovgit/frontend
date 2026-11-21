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
