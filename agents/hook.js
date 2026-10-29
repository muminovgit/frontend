#!/usr/bin/env node
// Claude Code hook -> Agent Ofis. Fayl faqat Node kerak, boshqa narsa emas.
// Env: OFFICE_URL (https://....up.railway.app), OFFICE_TOKEN, OFFICE_AGENT (default: coder)
const fs = require('fs'), os = require('os'), path = require('path');
const BASE = (process.env.OFFICE_URL || 'http://localhost:3000').replace(/\/$/, '');
const AGENT = process.env.OFFICE_AGENT || 'dilnoza';
const headers = { 'content-type': 'application/json', ...(process.env.OFFICE_TOKEN && { authorization: `Bearer ${process.env.OFFICE_TOKEN}` }) };
const send = e => fetch(`${BASE}/event`, { method: 'POST', headers, body: JSON.stringify({ agent: AGENT, ...e }), signal: AbortSignal.timeout(4000) }).catch(() => {});

let raw = ''; process.stdin.on('data', c => raw += c);
process.stdin.on('end', async () => {
  let h = {}; try { h = JSON.parse(raw); } catch {}
  const f = path.join(os.tmpdir(), `office-${h.session_id || 'x'}.json`);
  const st = (() => { try { return JSON.parse(fs.readFileSync(f)); } catch { return { n: 0 }; } })();
  switch (h.hook_event_name) {
    case 'UserPromptSubmit':
      fs.writeFileSync(f, JSON.stringify({ n: 0 }));
      await send({ type: 'start', task: String(h.prompt || 'Claude Code').replace(/\s+/g, ' ').slice(0, 40) });
      break;
    case 'PostToolUse':
      st.n++; fs.writeFileSync(f, JSON.stringify(st));
      await send({ type: 'progress', value: 1 - 1 / (1 + st.n / 6) }); // 0 dan 1 ga yaqinlashadi
      break;
    case 'Stop': await send({ type: 'done' }); break;
    case 'StopFailure': await send({ type: 'error', message: 'Claude Code xato' }); break;
  }
});
