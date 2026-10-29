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

## Claude Code bilan
`.claude/settings.json` ga hook qo'shsangiz, Claude Code sessiyasi "coder" stolida ko'rinadi:
```json
{ "hooks": {
  "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": "node agents/office.js start coder \"Claude Code ishlayapti\"" }] }],
  "Stop": [{ "hooks": [{ "type": "command", "command": "node agents/office.js done coder" }] }]
} }
```

## Internetga chiqarish
`OFFICE_TOKEN=maxfiy node server.js` — agentlar `Authorization: Bearer maxfiy` yuborishi kerak
(`office.js` `OFFICE_TOKEN` va `OFFICE_URL` env larini o'qiydi). Serverni VPS/Render/Railway ga qo'ying.
