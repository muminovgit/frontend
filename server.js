// Agent Ofis serveri — qo'shimcha paket kerak emas: `node server.js`
// Agentlar POST /event yuboradi, brauzer GET /events (SSE) orqali tinglaydi.
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

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

function remember(e) {
  if (!e.agent) return;
  if (e.type === 'start') last[e.agent] = { start: e, progress: null };
  else if (e.type === 'progress' && last[e.agent]) last[e.agent].progress = e;
  else if (['done', 'error', 'idle'].includes(e.type)) delete last[e.agent];
  if (e.type === 'needApproval') pending[e.itemId] = e;
}

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
    if (url.pathname === '/ping') return json(res, 200, { office: true, locked: !!TOKEN });

    if (url.pathname === '/events') {
      if (!authed(req, url)) return json(res, 401, { error: 'token' });
      res.writeHead(200, { 'content-type': 'text/event-stream', 'cache-control': 'no-cache', connection: 'keep-alive' });
      // Joriy holatni qayta yuboramiz
      Object.values(last).forEach(l => { res.write(`data: ${JSON.stringify(l.start)}\n\n`); if (l.progress) res.write(`data: ${JSON.stringify(l.progress)}\n\n`); });
      Object.values(pending).forEach(p => res.write(`data: ${JSON.stringify(p)}\n\n`));
      clients.add(res);
      const ka = setInterval(() => res.write(': ka\n\n'), 25000);
      req.on('close', () => { clients.delete(res); clearInterval(ka); });
      return;
    }

    // Agent hodisa yuboradi. needApproval bo'lsa javobda itemId qaytadi.
    if (req.method === 'POST' && url.pathname === '/event') {
      if (!authed(req, url)) return json(res, 401, { error: 'token' });
      const e = await body(req);
      if (!e.type) return json(res, 400, { error: 'type kerak' });
      if (e.type === 'needApproval') e.itemId = crypto.randomUUID();
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
