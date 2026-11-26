Salom! Avvalgi chatdagi loyihani davom ettiramiz. Men bilan o'zbek tilida gaplash.

## Loyiha
"Mashina tarixi" — o'zbek tilidagi animatsion qisqa videolar seriyasi (avtomobillar tarixidagi haqiqiy, qiziq voqealar, 60–85 s, vertikal 1080×1920). Maqsad: Instagram (asosiy), YouTube Shorts, Telegram (sotuv) va Facebook'da auditoriya yig'ish, keyin Telegram orqali Hot Wheels o'yinchoq mashinalar sotish, so'ngra homiylik va raqamli mahsulot.

## Hamma narsa repoda
Repo: `muminovgit/frontend`, branch: `claude/elegant-bohr-7bjc15`. Avval shuni o'qi:
- `hotwheels-serial/STRATEGIYA.md` — bozor tahlili, kontent strategiyasi, 12 ta mavzu, daromad modeli, avtomatlashtirish rejasi.
- `hotwheels-serial/mashina-tarixi/01-svetofor/` — 1-qism "Portlagan svetofor" (TAYYOR):
  - `video/portlagan_svetofor_1qism.mp4` — yakuniy video, mening ovozim bilan (84 s).
  - `video/src/` — butun pipeline: `beats.py` (sahnalar + ovoz uzunligiga moslash), `build_pages.py` (har bir joy uchun HTML/SVG sahifa + animatsiya JS), `capture.mjs` (Playwright bilan kadr-ma-kadr), `audio.py` (o'zimiz yozgan musiqa + SFX + ovoz, ducking), `assemble.py` (ffmpeg), `tighten.py` (ovozdagi uzun pauzalarni qisqartirish), `make_jobs.py`.
  - `video/voice/b1..b13.wav` — mening ovozim (tozalangan), keyingi qismlarda klonlash uchun namuna.
  - `characters/` — 7 ta rig qilingan 2D SVG qahramon (`gen_characters.py` generator; bo'g'imlar: `<id>_arm_L/R`, `forearm`, `hand`, `leg`, `shin`, `foot`, `head`, `torso`; har bir guruh o'z pivotiga translate qilingan, animatsiya uchun faqat `rotate()` qo'shiladi).
  - `city/` — 1868 Vestminster fon (kunduzi/kechasi), `gen_city.py`; rig qilingan Nayt svetofori.
  - `OVOZ_SSENARIYSI.md`, `SCRIPT.md`.
- `.claude/skills/` — o'rnatilgan 32 ta skill (instagram-growth, youtube-shorts, hook-writer, reels-script, content-calendar, competitor-analysis, creator-monetization, postiz, claude-youtube va boshqalar).

## Uslub (o'zgarmasin)
Toza 2D vektor (SVG), kontur `#221d1a`, krem fon `#f3ead8`, chapdan/pastdan soya + o'ngdan yengil yorug'lik, multfilm qahramonlar. Subtitrlar to'q fon ustida, yuqorida. Boshida katta HOOK yozuvi, burchakda "MASHINA TARIXI · #N" brend belgisi, oxirida "Obuna bo'l — do'stingga yubor" kartasi.

## Muhim qoidalar
- Faktlar har doim internetdan tekshiriladi va manbasi bilan yoziladi. Afsona bo'lsa, ochiq "afsona" deb aytiladi.
- Ovoz: sun'iy TTS ovozlari (Silero, OmniVoice dizayn, Microsoft) menga yoqmagan — "sun'iy, zerikarli, emotsiyasiz". Yoki men o'zim yozaman, yoki mening yozuvlarimdan OmniVoice (k2-fsa/OmniVoice) bilan klon qilinadi. OmniVoice modeli CC-BY-NC (notijoriy) — tijoratga o'tganda boshqa yechim kerak.
- Real odamlar ovozi/qiyofasi ruxsatsiz klonlanmaydi.
- Commit va push faqat `claude/elegant-bohr-7bjc15` branchiga. PR ochilmaydi (men so'ramagunimcha).

## Texnik eslatmalar (yangi konteynerda qayta o'rnatish kerak bo'lishi mumkin)
- Kadrlar Playwright + Chromium bilan olinadi (`capture.mjs`), Node'da `playwright` kerak.
- OmniVoice: alohida venv (`python3 -m venv ov && ov/bin/pip install omnivoice`), CPU'da ishlaydi; model Hugging Face'dan yuklanadi — "frontend" muhitida huggingface.co, us.aws.cdn.hf.co, cas-server.xethub.hf.co va boshqa HF hostlari ruxsat etilgan. Ovoz klonida `create_voice_clone_prompt(..., preprocess_prompt=False)` ishlatish kerak.
- Ovozni gaplarga bo'lishda filtrlarni bitta zanjirda afade bilan birga ishlatma (ovoz o'chib qolgan xato bo'lgan): avval kes → keyin tozalash → loudnorm linear → keyin fade.
- 1-qismda video ~84 s chiqdi; keyingilarda ~60 s ga yaqinlashtirish kerak.

## Keyingi vazifalar
1. Instagram (Business), YouTube va Telegram akkauntlari uchun nom, avatar, bio va muqova dizaynini tayyorlash (akkauntlarni men ochaman).
2. 2-qism: "Birinchi tezlik jarimasi (1896)" — fakt tekshirish (Snopes ba'zi tafsilotlarga shubha bildiradi), ssenariy, ovoz ssenariysi, keyin video. Shu pipeline'ni qayta ishlat; yangi joy/qahramonlar `characters/` va `city/` uslubida.
3. STRATEGIYA.md'dagi "Videoda nima kam" bo'limidagi yaxshilanishlar: tezroq kesmalar (har 2–3 s), karaoke (so'zma-so'z) subtitr, qahramon yuz ifodalari va lab harakati, loop yakun.
4. Keyinroq: Postiz/Zapier orqali post joylashni ulash va haftalik tahlil hisoboti.

Boshlashdan oldin repodagi fayllarni ko'rib chiq va menga qisqacha holatni ayt, keyin 1-vazifadan boshla.
