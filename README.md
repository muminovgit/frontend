# Silikon Minora (Agent Ofis)

Agentlaringiz ishini vizual ko'rish uchun ofis paneli: har bir agent o'z stolida ishlaydi,
tasdiq kerak bo'lsa sizning navbatingizga keladi, siz ✓ / ✕ bosasiz.

## Ishga tushirish
```bash
node server.js          # http://localhost:3000
node agents/demo.js     # (ixtiyoriy) namunaviy agentlar serverga ulanadi
```
Faqat `index.html` ni ochsangiz — ichki demo simulyatsiya ishlaydi.

## Agentni ulash
Har qanday til/tool HTTP orqali:
```bash
curl -X POST localhost:3000/event -d '{"type":"start","agent":"coder","task":"Bug fix"}'
curl -X POST localhost:3000/event -d '{"type":"progress","agent":"coder","value":0.5}'
curl -X POST localhost:3000/event -d '{"type":"needApproval","agent":"coder","task":"PR yuborilsinmi?"}'  # -> {"itemId":"..."}
curl "localhost:3000/decision/<itemId>?wait=1"   # -> {"status":"approved"|"rejected"|"pending"}
curl -X POST localhost:3000/event -d '{"type":"done","agent":"coder"}'
```
Node'da: `agents/office.js` (`start`, `progress`, `askApproval`, `done`, `error`).
CLI: `node agents/office.js start coder "Bug fix"`.

Agent id lari: `research, writer, sales, coder, support` (`index.html` dagi `AGENTS` massivida o'zgartiring).

## Claude Code ni ulash (lokal)
```bash
node server.js                      # 1-terminal: ofis http://localhost:3000
node agents/install-hook.js coder   # bir marta: hook ni ~/.claude/settings.json ga qo'shadi
```
Endi Claude Code ishlaganda "Dasturchi" stolida vazifa va progress ko'rinadi, tugagach "Tayyor".
Boshqa stol uchun: `node agents/install-hook.js research`. O'chirish: `node agents/install-hook.js --remove`.
Server boshqa joyda bo'lsa `OFFICE_URL` / `OFFICE_TOKEN` env larini qo'ying (Railway shart emas).

## Railway (ixtiyoriy, masofadan ko'rish uchun)
1. railway.com → **New Project → Deploy from GitHub repo** → `muminovgit/frontend` (branch `claude/vibrant-gates-2d29le`).
2. **Variables**: `OFFICE_TOKEN` = uzun maxfiy kalit. **Settings → Networking → Generate Domain**.
3. Ofis: `https://xxx.up.railway.app/?key=KALIT`
4. Hook ni shu serverga ulash:
   `OFFICE_URL=https://xxx.up.railway.app OFFICE_TOKEN=KALIT node agents/install-hook.js coder`

## Ichki demo agentlar
Server ishga tushganda 5 ta agent o'zi ishlab turadi (ofis doim tirik). Haqiqiy hodisa (hook, curl, n8n) kelgan stol
2 daqiqa demo'dan chiqadi. O'chirish: `DEMO=0 node server.js` (Railway Variables ga `DEMO=0`).

## Haqiqiy AI agentlar (Claude API)
Agentlar Claude API orqali haqiqiy ish qiladi: siz vazifa berasiz, agent natijani tayyorlaydi, siz ko'rib ✓/✕ bosasiz
(✕ bo'lsa agent 2 martagacha qayta urinadi). Agentlar faqat **matn tayyorlaydi** — email yubormaydi, kod deploy qilmaydi.
Tadqiqotchi va Sotuv veb-qidiruvdan foydalanadi.

Railway → Variables:
| O'zgaruvchi | Ma'nosi |
|---|---|
| `ANTHROPIC_API_KEY` | **Majburiy.** console.anthropic.com dan oling |
| `AGENT_MODEL` | Ixtiyoriy. Default `claude-sonnet-5-5`; kuchliroq (qimmatroq): `claude-opus-5-5`; eng arzon: `claude-haiku-5-5` |
| `MAX_TASKS_PER_DAY` | Ixtiyoriy. Kunlik vazifa limiti (default 40) — xarajatni nazorat qilish uchun |

Kalit qo'yilgach demo agentlar o'chadi va ofisda vazifa kiritish paneli chiqadi. Natijalar serverda xotirada
turadi (oxirgi 30 ta), server qayta ishga tushsa o'chadi. Veb-qidiruv ishlamasa, Console → Settings da yoqilganini tekshiring.

## Agentlar o'zaro muloqoti
Har bir agent `ask_teammate` vositasi bilan hamkasbidan yordam so'ray oladi (masalan, Menejer Tadqiqotchi va Kontentga
parallel topshiriq beradi, Sotuv Tadqiqotchidan ma'lumot so'raydi). Hamkasb javob beradi, kerak bo'lsa keyingi savol ham mumkin.
Ofisda agent hamkasbi stoliga borib gapini aytadi; natijadagi **👁** da to'liq muloqot tarixi ko'rinadi.
Vazifani odatda **🧭 Menejer**ga bering — u o'zi kerakli hamkasblarni jalb qiladi.

Xarajat nazorati (Railway Variables): `MAX_TALK_CALLS` (bitta vazifada jami hamkasb so'rovlari, default 8),
`MAX_TALK_DEPTH` (so'rov zanjiri chuqurligi, default 2). Har so'rov alohida API chaqiruvi — muloqot ko'p bo'lsa, xarajat ham ko'p.

## Silikon Minora — qavatlar, xodimlar, loyiha jarayoni
Bitta bino, 5 qavat, 12 ta xodim (har birining o'z xarakteri, tashqi ko'rinishi va odatlari — `roster.json`). Xodimlar stolda ishlaydi,
kofe-mashinaga, suv avtomatiga, doskaga boradi, bir-biri bilan suhbatlashadi, qavatlararo **lift**da yuradi.

| Qavat | Xodimlar |
|---|---|
| 5 · Nazorat (Penthouse) | Madina (direktor) + siz (Boss) |
| 4 · Risk va Sifat | Kamola (risk), Timur (qoidalar/huquq) |
| 3 · Sotuv | Rustam (boshliq), Nigora (outreach), Otabek (muzokarachi) |
| 2 · Marketing | Jasur (direktor), Malika (kontent), Sardor (SMM) |
| 1 · Tadqiqot | Aziza (bosh tadqiqotchi), Bobur (skaner), Dilnoza (ma'lumotlar) |

**To'liq loyiha** (vazifa panelida "🏢 Butun minora"): brief yozasiz → Tadqiqot → Marketing → Sotuv → Risk → Nazorat.
Har qavat yozma HANDOFF beradi (topilmalar, noma'lumlar, qaror GO/WAIT/REJECT), siz har bosqichni ko'rib tasdiqlaysiz (✓/✕),
dalil yetishmasa jarayon WAIT bilan to'xtaydi, Nazorat yakuniy qaror beradi va **Qaror jurnali**ga yoziladi (CSV yuklab olinadi).
Mantiq TOWER qo'llanmasiga asoslangan: bosqichma-bosqich, dalil-asosli, odam tasdig'i bilan; hech qanday tashqi amal bajarilmaydi.
Bitta xodimga alohida vazifa ham berish mumkin; xodimlar `ask_teammate` orqali bir-biridan yordam so'raydi.
Loyiha = 5 birlik (`MAX_TASKS_PER_DAY`, default 40), bitta bosqichda hamkasb so'rovlari `MAX_TALK_CALLS` (default 6).
Claude Code hook'i endi `dilnoza` stolida ko'rinadi (`node agents/install-hook.js <xodim-id>` bilan o'zgartiring).
Eslatma: ofis serverdan `roster.json` ni oladi, shuning uchun `index.html` ni faqat fayl sifatida ochib bo'lmaydi — `node server.js` kerak.
