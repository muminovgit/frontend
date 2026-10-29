// Haqiqiy agentlar: Claude API orqali ishlaydi. Faqat ANTHROPIC_API_KEY bo'lsa yoqiladi.
// Agentlar faqat MATN tayyorlaydi (tashqi tizimga hech narsa yubormaydi) — natijani siz ko'rib tasdiqlaysiz.
const crypto = require('crypto');
const Anthropic = require('@anthropic-ai/sdk');

const enabled = !!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);
const client = enabled ? new Anthropic() : null;
const MODEL = process.env.AGENT_MODEL || 'claude-opus-5-5';       // arzonroq: claude-sonnet-5-5 yoki claude-haiku-5-5
const MAX_PER_DAY = Number(process.env.MAX_TASKS_PER_DAY || 40);  // xarajatni cheklash
const MAX_REVISIONS = 2;

const BASE = 'Siz kichik jamoadagi mutaxassis agentsiz. Boss (foydalanuvchi) vazifa beradi, siz natijani tayyorlaysiz. ' +
  'Foydalanuvchi qaysi tilda yozsa, shu tilda javob bering (odatda o\'zbek tilida). Qisqa, aniq va amaliy yozing. ' +
  'Siz hech qanday tashqi amal bajarmaysiz (email yubormaysiz, kod deploy qilmaysiz) — faqat tayyor natija/qoralama berasiz. ' +
  'Bilmagan narsangizni o\'ylab topmang, aniq ayting.';
const AGENTS = {
  research: { web: true,  system: BASE + ' Rolingiz: bozor va raqobat tadqiqotchisi. Veb-qidiruvdan foydalaning, faktlarni manba havolasi bilan bering, oxirida qisqa xulosa va tavsiyalar yozing.' },
  writer:   { web: false, system: BASE + ' Rolingiz: kontent yozuvchi (blog, email, ssenariy, post). Auditoriya va ohangga mos, tayyor matn bering.' },
  sales:    { web: true,  system: BASE + ' Rolingiz: sotuv yordamchisi. Lead tahlili, taklif matni, follow-up xabarlari qoralamasini tayyorlang. Haqiqiy kompaniya ma\'lumoti kerak bo\'lsa veb-qidiruvdan foydalaning.' },
  coder:    { web: false, system: BASE + ' Rolingiz: senior dasturchi. Kod yozing yoki ko\'rib chiqing; kodni markdown blokda bering, qisqa izoh qo\'shing, xavf/kamchiliklarni ayting.' },
  support:  { web: false, system: BASE + ' Rolingiz: mijozlar yordami. Mijozga yuboriladigan xushmuomala, aniq javob qoralamasini yozing; kerak bo\'lsa ichki eslatma qo\'shing.' },
};

const results = new Map();   // resultId -> { id, agent, task, text, status }
const busy = new Set();
let day = '', count = 0;

const meta = r => ({ type: 'result', resultId: r.id, agent: r.agent, task: r.task, status: r.status });
const list = () => [...results.values()].map(meta);
const getText = id => (results.get(id) || {}).text;

async function generate(agent, messages, onText, note, noTools) {
  const def = AGENTS[agent];
  const tools = def.web && !noTools ? [{ type: 'web_search_20260209', name: 'web_search', max_uses: 5 }] : undefined;
  let msgs = messages, text = '', inTok = 0, outTok = 0;
  for (let turn = 0; turn < 6; turn++) {
    let msg;
    try {
      const stream = client.messages.stream({
        model: MODEL, max_tokens: 16000, thinking: { type: 'adaptive' },
        system: def.system, tools, messages: msgs,
      });
      stream.on('text', onText);
      msg = await stream.finalMessage();
    } catch (err) {
      // Veb-qidiruv yoqilmagan/ruxsat yo'q bo'lsa, qidiruvsiz qayta urinamiz
      if (tools && err.status === 400) {
        note(`Veb-qidiruv ishlamadi (${String(err.message).slice(0, 140)}). Qidiruvsiz davom etaman.`);
        return generate(agent, messages, onText, note, true);
      }
      throw err;
    }
    inTok += msg.usage.input_tokens; outTok += msg.usage.output_tokens;
    text += msg.content.filter(b => b.type === 'text').map(b => b.text).join('');
    if (msg.stop_reason === 'refusal') throw new Error('Model javob berishdan bosh tortdi');
    if (msg.stop_reason === 'pause_turn') { msgs = [...msgs, { role: 'assistant', content: msg.content }]; continue; }
    return { text: text.trim(), inTok, outTok };
  }
  return { text: text.trim(), inTok, outTok };
}

async function run({ agent, task, emit, waitDecision }) {
  const res = { id: crypto.randomUUID(), agent, task, text: '', status: 'working' };
  results.set(res.id, res);
  while (results.size > 30) results.delete(results.keys().next().value);
  try {
    emit({ type: 'start', agent, task: task.slice(0, 60) });
    let messages = [{ role: 'user', content: task }];
    for (let rev = 0; rev <= MAX_REVISIONS; rev++) {
      let chars = 0, lastEmit = 0;
      const out = await generate(agent, messages, t => {
        chars += t.length;
        if (Date.now() - lastEmit > 900) { lastEmit = Date.now(); emit({ type: 'progress', agent, value: Math.min(0.95, 1 - Math.exp(-chars / 2500)) }); }
      }, m => emit({ type: 'log', agent, message: m }));
      res.text = out.text; res.status = 'review';
      emit({ type: 'progress', agent, value: 1 });
      emit({ type: 'log', agent, message: `${out.inTok} kirish / ${out.outTok} chiqish token` });
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

module.exports = { enabled, MODEL, start, list, getText };
