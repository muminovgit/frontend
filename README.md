# Agent Ofis

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

## Railway ga qo'yish
1. railway.com → **New Project → Deploy from GitHub repo** → `muminovgit/frontend` (branch: `claude/vibrant-gates-2d29le`, yoki avval `main` ga merge qiling).
2. **Variables** ga `OFFICE_TOKEN` = o'zingiz o'ylab topgan uzun maxfiy kalit qo'shing.
3. **Settings → Networking → Generate Domain** — `https://xxx.up.railway.app` olasiz. (`railway.json` tayyor, PORT ni Railway o'zi beradi.)
4. Ofisni oching: `https://xxx.up.railway.app/?key=MAXFIY_KALIT`

## Claude Code ni ulash
1. `agents/hook.js` ni kompyuteringizga oling (masalan `~/agent-office/agents/hook.js`).
2. `claude-hooks.example.json` ni `~/.claude/settings.json` ga qo'shing (URL va kalitni o'zgartiring).
3. Endi Claude Code ishlaganda "Dasturchi" stolida vazifa va progress ko'rinadi, tugagach "Tayyor".
   Bir nechta sessiya/stol uchun `OFFICE_AGENT` ni o'zgartiring (`research`, `writer`, ...).

