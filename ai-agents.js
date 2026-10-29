// Haqiqiy agentlar: Claude API orqali ishlaydi. Faqat ANTHROPIC_API_KEY bo'lsa yoqiladi.
// Agentlar bir-biri bilan `ask_teammate` vositasi orqali gaplashadi (so'rov -> javob -> keyingi savol).
// Agentlar faqat MATN tayyorlaydi (tashqi tizimga hech narsa yubormaydi) — natijani siz ko'rib tasdiqlaysiz.
const crypto = require('crypto');
const Anthropic = require('@anthropic-ai/sdk');

const enabled = !!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);
const client = enabled ? new Anthropic() : null;
const MODEL = process.env.AGENT_MODEL || 'claude-sonnet-5-5';     // kuchliroq: claude-opus-5-5; arzonroq: claude-haiku-5-5
const MAX_PER_DAY = Number(process.env.MAX_TASKS_PER_DAY || 40);  // xarajatni cheklash
const MAX_DEPTH = Number(process.env.MAX_TALK_DEPTH || 2);        // hamkasbning hamkasbiga so'rovi zanjiri
const MAX_CALLS = Number(process.env.MAX_TALK_CALLS || 8);        // bitta vazifa uchun jami hamkasb so'rovlari
const MAX_REVISIONS = 2;

const BASE = 'Siz kichik jamoadagi mutaxassis agentsiz. Boss (foydalanuvchi) vazifa beradi, siz natijani tayyorlaysiz. ' +
  'Foydalanuvchi qaysi tilda yozsa, shu tilda javob bering (odatda o\'zbek tilida). Qisqa, aniq va amaliy yozing. ' +
  'Siz hech qanday tashqi amal bajarmaysiz (email yubormaysiz, kod deploy qilmaysiz) — faqat tayyor natija/qoralama berasiz. ' +
  'Bilmagan narsangizni o\'ylab topmang, aniq ayting.';
const AGENTS = {
  manager:  { name: 'Menejer',     web: false, role: 'jamoa menejeri: vazifani qismlarga bo\'lib, kerakli hamkasblarga topshiradi va natijalarni bitta yakuniy javobga birlashtiradi. Murakkab vazifalarda albatta hamkasblarga topshiring; bir-biriga bog\'liq bo\'lmagan so\'rovlarni bir vaqtda yuboring.' },
  research: { name: 'Tadqiqotchi', web: true,  role: 'bozor va raqobat tadqiqotchisi. Veb-qidiruvdan foydalaning, faktlarni manba havolasi bilan bering, oxirida qisqa xulosa va tavsiyalar yozing.' },
  writer:   { name: 'Kontent',     web: false, role: 'kontent yozuvchi (blog, email, ssenariy, post). Auditoriya va ohangga mos, tayyor matn bering.' },
  sales:    { name: 'Sotuv',       web: true,  role: 'sotuv yordamchisi. Lead tahlili, taklif matni, follow-up xabarlari qoralamasini tayyorlang. Haqiqiy kompaniya ma\'lumoti kerak bo\'lsa veb-qidiruvdan foydalaning.' },
  coder:    { name: 'Dasturchi',   web: false, role: 'senior dasturchi. Kod yozing yoki ko\'rib chiqing; kodni markdown blokda bering, qisqa izoh qo\'shing, xavf/kamchiliklarni ayting.' },
  support:  { name: 'Support',     web: false, role: 'mijozlar yordami. Mijozga yuboriladigan xushmuomala, aniq javob qoralamasini yozing; kerak bo\'lsa ichki eslatma qo\'shing.' },
};
const NAMES = Object.fromEntries(Object.entries(AGENTS).map(([k, v]) => [k, v.name]));

function systemFor(agent, canAsk) {
  const d = AGENTS[agent];
  let s = `${BASE} Sizning ismingiz: ${d.name}. Rolingiz: ${d.role}`;
  if (canAsk) {
    const mates = Object.entries(AGENTS).filter(([k]) => k !== agent).map(([k, v]) => `${k} (${v.name})`).join(', ');
    s += ` Jamoadoshlaringiz: ${mates}. Boshqa mutaxassis bilimi kerak bo'lsa, ask_teammate vositasi bilan so'rang: ` +
      'so\'rovni to\'liq va o\'zi-o\'zidan tushunarli yozing (hamkasbingiz sizning suhbatingizni ko\'rmaydi), javob yetarli bo\'lmasa keyingi savol bering. ' +
      'O\'zingiz qila oladigan ishni hamkasbga topshirmang.';
  } else s += ' Sizga hamkasbingiz yordam so\'radi: qisqa, aniq va to\'g\'ridan-to\'g\'ri javob bering.';
  return s;
}
const askTool = self => ({
  name: 'ask_teammate', strict: true,
  description: 'Jamoadoshingizdan yordam so\'rang va uning javobini oling. Hamkasb sizning suhbatingizni ko\'rmaydi — so\'rovni to\'liq yozing.',
  input_schema: {
    type: 'object', additionalProperties: false, required: ['teammate', 'message'],
    properties: {
      teammate: { type: 'string', enum: Object.keys(AGENTS).filter(k => k !== self), description: 'Hamkasb identifikatori' },
      message: { type: 'string', description: 'Hamkasbga to\'liq so\'rov' },
    },
  },
});

const results = new Map();   // resultId -> { id, agent, task, text, status, talk }
const busy = new Set();
let day = '', count = 0;

const meta = r => ({ type: 'result', resultId: r.id, agent: r.agent, task: r.task, status: r.status });
const list = () => [...results.values()].map(meta);
const getResult = id => { const r = results.get(id); return r && { text: r.text, talk: r.talk }; };

async function askTeammate(ctx, from, input, depth) {
  const to = input && input.teammate;
  const message = String((input && input.message) || '').slice(0, 3000);
  if (!AGENTS[to] || to === from || !message) return { error: true, text: 'so\'rov noto\'g\'ri: hamkasb yoki xabar yo\'q' };
  if (ctx.calls >= MAX_CALLS) return { error: true, text: 'hamkasb so\'rovlari limiti tugadi; qolganini o\'zingiz yakunlang' };
  ctx.calls++;
  const entry = { from, to, ask: message, reply: null };
  ctx.talk.push(entry);
  ctx.emit({ type: 'talk', agent: from, to, kind: 'ask', message });
  const thread = ctx.threads[to] = ctx.threads[to] || [];
  thread.push({ role: 'user', content: `${NAMES[from]} sizdan yordam so'rayapti:\n\n${message}` });
  try {
    const out = (await generate(ctx, to, thread, { depth: depth + 1 })) || '(javob bo\'sh)';
    thread.push({ role: 'assistant', content: out });
    entry.reply = out;
    ctx.emit({ type: 'talk', agent: to, to: from, kind: 'reply', message: out });
    return { text: out };
  } catch (err) {
    thread.pop();
    entry.reply = 'XATO: ' + String(err.message || err).slice(0, 200);
    ctx.emit({ type: 'talk', agent: to, to: from, kind: 'reply', message: entry.reply });
    return { error: true, text: 'hamkasb xato berdi: ' + String(err.message || err).slice(0, 200) };
  }
}

async function generate(ctx, agent, messages, opts) {
  const { onText, depth, noWeb } = opts;
  const def = AGENTS[agent];
  const canAsk = depth < MAX_DEPTH;
  const tools = [];
  if (def.web && !noWeb) tools.push({ type: 'web_search_20260209', name: 'web_search', max_uses: 5 });
  if (canAsk) tools.push(askTool(agent));
  let msgs = messages, text = '';
  for (let turn = 0; turn < 12; turn++) {
    let msg;
    try {
      const stream = client.messages.stream({
        model: MODEL, max_tokens: 16000, thinking: { type: 'adaptive' },
        system: systemFor(agent, canAsk), tools: tools.length ? tools : undefined, messages: msgs,
      });
      if (onText) stream.on('text', onText);
      msg = await stream.finalMessage();
    } catch (err) {
      // Veb-qidiruv yoqilmagan/ruxsat yo'q bo'lsa, qidiruvsiz qayta urinamiz
      if (def.web && !noWeb && err.status === 400) {
        ctx.emit({ type: 'log', agent, message: `Veb-qidiruv ishlamadi (${String(err.message).slice(0, 140)}). Qidiruvsiz davom etaman.` });
        return generate(ctx, agent, messages, { ...opts, noWeb: true });
      }
      throw err;
    }
    ctx.inTok += msg.usage.input_tokens; ctx.outTok += msg.usage.output_tokens;
    text += msg.content.filter(b => b.type === 'text').map(b => b.text).join('');
    if (msg.stop_reason === 'refusal') throw new Error('Model javob berishdan bosh tortdi');
    if (msg.stop_reason === 'pause_turn') { msgs = [...msgs, { role: 'assistant', content: msg.content }]; continue; }
    if (msg.stop_reason === 'tool_use') {
      const uses = msg.content.filter(b => b.type === 'tool_use');
      const out = await Promise.all(uses.map(async u => {
        const r = u.name === 'ask_teammate' ? await askTeammate(ctx, agent, u.input, depth) : { error: true, text: 'noma\'lum vosita' };
        return { type: 'tool_result', tool_use_id: u.id, content: r.text, ...(r.error && { is_error: true }) };
      }));
      msgs = [...msgs, { role: 'assistant', content: msg.content }, { role: 'user', content: out }];
      text = '';   // yakuniy javob faqat oxirgi bosqichdan olinadi
      continue;
    }
    return text.trim();
  }
  return text.trim();
}

async function run({ agent, task, emit, waitDecision }) {
  const res = { id: crypto.randomUUID(), agent, task, text: '', status: 'working', talk: [] };
  results.set(res.id, res);
  while (results.size > 30) results.delete(results.keys().next().value);
  const ctx = { emit, calls: 0, talk: res.talk, threads: {}, inTok: 0, outTok: 0 };
  try {
    emit({ type: 'start', agent, task: task.slice(0, 60) });
    let messages = [{ role: 'user', content: task }];
    for (let rev = 0; rev <= MAX_REVISIONS; rev++) {
      let chars = 0, lastEmit = 0; ctx.calls = 0;
      const text = await generate(ctx, agent, messages, {
        depth: 0,
        onText: t => {
          chars += t.length;
          if (Date.now() - lastEmit > 900) { lastEmit = Date.now(); emit({ type: 'progress', agent, value: Math.min(0.95, 1 - Math.exp(-chars / 2500)) }); }
        },
      });
      res.text = text; res.status = 'review';
      emit({ type: 'progress', agent, value: 1 });
      emit({ type: 'log', agent, message: `${ctx.inTok} kirish / ${ctx.outTok} chiqish token, ${res.talk.length} ta hamkasb muloqoti` });
      emit(meta(res));
      const itemId = crypto.randomUUID();
      emit({ type: 'needApproval', agent, task: task.slice(0, 60), itemId, resultId: res.id });
      const decision = await waitDecision(itemId, 60 * 60000);
      if (decision === 'approved' || decision === 'expired') {
        res.status = decision === 'approved' ? 'approved' : 'expired'; emit(meta(res)); return; // stol holatini 'decide' hodisasi o'zi yangilaydi
      }
      if (rev === MAX_REVISIONS) break;
      res.status = 'working'; emit(meta(res));
      emit({ type: 'start', agent, task: task.slice(0, 50) + ' (qayta)' });
      messages = [...messages, { role: 'assistant', content: res.text },
        { role: 'user', content: 'Boss bu natijani rad etdi. Vazifani qayta o\'qing va yaxshilab, to\'liq yangi variantni bering.' }];
    }
    res.status = 'rejected'; emit(meta(res)); emit({ type: 'idle', agent });
  } catch (err) {
    res.status = 'error'; emit(meta(res));
    const full = String(err.message || err);
    console.error(`[${agent}] xato:`, full);
    emit({ type: 'log', agent, message: 'XATO: ' + full.slice(0, 300) });
    emit({ type: 'error', agent, message: full.slice(0, 60) });
  } finally { busy.delete(agent); }
}

function start({ agent, task, emit, waitDecision }) {
  if (!enabled) return { code: 503, error: 'ANTHROPIC_API_KEY o\'rnatilmagan' };
  if (!AGENTS[agent]) return { code: 400, error: 'agent topilmadi' };
  task = String(task || '').trim();
  if (!task) return { code: 400, error: 'vazifa bo\'sh' };
  if (task.length > 4000) return { code: 400, error: 'vazifa 4000 belgidan oshmasin' };
  if (busy.has(agent)) return { code: 409, error: 'agent band, tugashini kuting' };
  const today = new Date().toISOString().slice(0, 10);
  if (day !== today) { day = today; count = 0; }
  if (count >= MAX_PER_DAY) return { code: 429, error: `kunlik limit (${MAX_PER_DAY}) tugadi` };
  count++; busy.add(agent);
  run({ agent, task, emit, waitDecision });
  return { code: 200, ok: true };
}

module.exports = { enabled, MODEL, start, list, getResult };
