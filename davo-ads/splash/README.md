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
