// Agent Ofis serveri — qo'shimcha paket kerak emas: `node server.js`
// Agentlar POST /event yuboradi, brauzer GET /events (SSE) orqali tinglaydi.
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const ai = require('./ai-agents');

const PORT = process.env.PORT || 3000;
const TOKEN = process.env.OFFICE_TOKEN || ''; // ixtiyoriy: agentlar uchun maxfiy kalit
const clients = new Set();
const last = {};        // agent -> oxirgi start/progress hodisasi (yangi ochilgan sahifa uchun)
const pending = {};     // itemId -> needApproval hodisasi
const decisions = {};   // itemId -> 'approved' | 'rejected'

function broadcast(e) {
  const line = `data: ${JSON.stringify(e)}\n\n`;
  clients.forEach(res => res.write(line));
}

const lastReal = {};    // agent -> haqiqiy hodisa vaqti (demo shu stolni 2 daqiqa tegmaydi)

function remember(e) {
  if (!e.agent) return;
  if (e.type === 'start') last[e.agent] = { start: e, progress: null };
  else if (e.type === 'progress' && last[e.agent]) last[e.agent].progress = e;
  else if (['done', 'error', 'idle'].includes(e.type)) delete last[e.agent];
  if (e.type === 'needApproval') pending[e.itemId] = e;
}

const emit = e => { if (e.agent) lastReal[e.agent] = Date.now(); remember(e); broadcast(e); };

function body(req) {
  return new Promise((ok, fail) => {
    let b = '';
    req.on('data', c => { b += c; if (b.length > 1e5) req.destroy(); });
    req.on('end', () => { try { ok(JSON.parse(b || '{}')); } catch (err) { fail(err); } });
  });
}

const json = (res, code, obj) => { res.writeHead(code, { 'content-type': 'application/json', 'access-control-allow-origin': '*' }); res.end(JSON.stringify(obj)); };
// Agentlar: Authorization: Bearer <token>. Brauzer: ?key=<token>
const authed = (req, url) => !TOKEN || req.headers.authorization === `Bearer ${TOKEN}` || url.searchParams.get('key') === TOKEN;

http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  if (req.method === 'OPTIONS') {
    res.writeHead(204, { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'GET,POST' });
    return res.end();
  }
  try {
    if (req.method === 'GET' && url.pathname === '/') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      return res.end(fs.readFileSync(path.join(__dirname, 'index.html')));
    }
    if (url.pathname === '/ping') return json(res, 200, { office: true, locked: !!TOKEN, ai: ai.enabled, model: ai.enabled ? ai.MODEL : null });

    if (url.pathname === '/events') {
      if (!authed(req, url)) return json(res, 401, { error: 'token' });
      res.writeHead(200, { 'content-type': 'text/event-stream', 'cache-control': 'no-cache', connection: 'keep-alive' });
      // Joriy holatni qayta yuboramiz
      Object.values(last).forEach(l => { res.write(`data: ${JSON.stringify(l.start)}\n\n`); if (l.progress) res.write(`data: ${JSON.stringify(l.progress)}\n\n`); });
      ai.list().forEach(r => res.write(`data: ${JSON.stringify(r)}\n\n`));
      Object.values(pending).forEach(p => res.write(`data: ${JSON.stringify(p)}\n\n`));
      clients.add(res);
      const ka = setInterval(() => res.write(': ka\n\n'), 25000);
      req.on('close', () => { clients.delete(res); clearInterval(ka); });
      return;
    }

    // Haqiqiy AI agentga vazifa berish (brauzerdan)
    if (req.method === 'POST' && url.pathname === '/task') {
      if (!authed(req, url)) return json(res, 401, { error: 'token' });
      const { agent, task } = await body(req);
      const r = ai.start({ agent, task, emit, waitDecision });
      return json(res, r.code, r);
    }
    const rm = url.pathname.match(/^\/result\/([\w-]+)$/);
    if (req.method === 'GET' && rm) {
      if (!authed(req, url)) return json(res, 401, { error: 'token' });
      const r = ai.getResult(rm[1]);
      return r ? json(res, 200, r) : json(res, 404, { error: 'topilmadi' });
    }

    // Agent hodisa yuboradi. needApproval bo'lsa javobda itemId qaytadi.
    if (req.method === 'POST' && url.pathname === '/event') {
      if (!authed(req, url)) return json(res, 401, { error: 'token' });
      const e = await body(req);
      if (!e.type) return json(res, 400, { error: 'type kerak' });
      if (e.type === 'needApproval') e.itemId = crypto.randomUUID();
      if (e.agent) lastReal[e.agent] = Date.now();
      remember(e); broadcast(e);
      return json(res, 200, { ok: true, itemId: e.itemId });
    }

    // Brauzerdan (siz) qaror
    if (req.method === 'POST' && url.pathname === '/decision') {
      if (!authed(req, url)) return json(res, 401, { error: 'token' });
      const { itemId, ok } = await body(req);
      if (!pending[itemId]) return json(res, 404, { error: 'topilmadi' });
      delete pending[itemId];
      decisions[itemId] = ok ? 'approved' : 'rejected';
      broadcast({ type: 'decide', itemId, ok: !!ok });
      return json(res, 200, { ok: true });
    }

    // Agent qarorni so'raydi: ?wait=1 bo'lsa 55 soniyagacha kutadi
    const m = url.pathname.match(/^\/decision\/([\w-]+)$/);
    if (req.method === 'GET' && m) {
      if (!authed(req, url)) return json(res, 401, { error: 'token' });
      const id = m[1], until = Date.now() + (url.searchParams.get('wait') ? 55000 : 0);
      while (!decisions[id] && Date.now() < until) await new Promise(r => setTimeout(r, 500));
      return json(res, 200, { status: decisions[id] || 'pending' });
    }
    json(res, 404, { error: 'yo\'q' });
  } catch (err) { json(res, 500, { error: String(err) }); }
}).listen(PORT, () => console.log(`Agent Ofis: http://localhost:${PORT}`));

// ---- Ichki demo agentlar (DEMO=0 bilan o'chiriladi) ----
// Hamma stol ishlab tursin; haqiqiy agent ulansa, shu stol uchun demo to'xtaydi.
// Kutilgan qarorni kutadi: 'approved' | 'rejected' | 'expired'
async function waitDecision(itemId, ms) {
  const until = Date.now() + ms;
  while (!decisions[itemId] && pending[itemId] && Date.now() < until) await new Promise(r => setTimeout(r, 500));
  if (decisions[itemId]) return decisions[itemId];
  if (pending[itemId]) { delete pending[itemId]; broadcast({ type: 'decide', itemId, ok: true }); }
  return 'expired';
}

const DEMO = [
  ['research', ['Bozor tahlili', 'Raqobatchilar', 'Trend qidiruv']],
  ['writer',   ['Blog post', 'Email kampaniya', 'Reels ssenariy']],
  ['sales',    ['Lead topish', 'Taklif yuborish', 'Follow-up']],
  ['coder',    ['Bug fix', 'Yangi funksiya', 'Code review']],
  ['support',  ['Ticket javob', 'FAQ yangilash', 'Shikoyat']],
];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const real = a => Date.now() - (lastReal[a] || 0) < 120000;

async function demoAgent(agent, tasks) {
  await sleep(Math.random() * 5000);
  for (;;) {
    if (real(agent)) { await sleep(5000); continue; }
    const task = tasks[Math.floor(Math.random() * tasks.length)];
    emit({ type: 'start', agent, task });
    for (let p = 0.1; p <= 1.001 && !real(agent); p += 0.1) { await sleep(700 + Math.random() * 1100); emit({ type: 'progress', agent, value: Math.min(p, 1) }); }
    if (real(agent)) continue;
    const r = Math.random();
    if (r < 0.06) emit({ type: 'error', agent, message: 'API xatosi' });
    else if (r < 0.6) {
      const itemId = crypto.randomUUID();
      emit({ type: 'needApproval', agent, task, itemId });
      const until = Date.now() + 10 * 60000;       // siz bosmasangiz 10 daqiqadan keyin o'zi davom etadi
      while (!decisions[itemId] && pending[itemId] && Date.now() < until) await sleep(500);
      if (pending[itemId]) { delete pending[itemId]; broadcast({ type: 'decide', itemId, ok: true }); continue; }
      if (decisions[itemId] === 'rejected') continue;   // rad etildi -> qayta urinadi
      emit({ type: 'done', agent });
    } else emit({ type: 'done', agent });
    await sleep(3000 + Math.random() * 5000);
  }
}
// Haqiqiy AI yoqilgan bo'lsa demo o'chadi (DEMO=1 bilan majburan yoqish mumkin)
if (process.env.DEMO === '1' || (process.env.DEMO !== '0' && !ai.enabled)) DEMO.forEach(([a, t]) => demoAgent(a, t));
