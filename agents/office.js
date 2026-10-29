// Agentlar uchun kichik klient. Ishlatish:
//   const office = require('./office');
//   await office.start('coder', 'Bug fix');
//   await office.progress('coder', 0.5);
//   const ok = await office.askApproval('coder', 'PR #12 ni yuborishga ruxsat?');
//   await office.done('coder');
// CLI: node agents/office.js start coder "Bug fix"
const BASE = process.env.OFFICE_URL || 'http://localhost:3000';
const headers = { 'content-type': 'application/json', ...(process.env.OFFICE_TOKEN && { authorization: `Bearer ${process.env.OFFICE_TOKEN}` }) };

async function send(e) {
  const r = await fetch(`${BASE}/event`, { method: 'POST', headers, body: JSON.stringify(e) });
  return r.json();
}
const office = {
  start: (agent, task) => send({ type: 'start', agent, task }),
  progress: (agent, value) => send({ type: 'progress', agent, value }),
  done: agent => send({ type: 'done', agent }),
  error: (agent, message) => send({ type: 'error', agent, message }),
  idle: agent => send({ type: 'idle', agent }),
  // Sizning qaroringizni kutadi; true = tasdiqlandi, false = rad etildi
  async askApproval(agent, task) {
    const { itemId } = await send({ type: 'needApproval', agent, task });
    for (;;) {
      const r = await fetch(`${BASE}/decision/${itemId}?wait=1`, { headers });
      const { status } = await r.json();
      if (status !== 'pending') return status === 'approved';
    }
  },
};
module.exports = office;

if (require.main === module) {
  const [cmd, agent, arg] = process.argv.slice(2);
  if (!office[cmd]) { console.error('start|progress|done|error|idle|askApproval <agent> [arg]'); process.exit(1); }
  const val = cmd === 'progress' ? Number(arg) : arg;
  office[cmd](agent, val).then(r => { console.log(r); if (cmd === 'askApproval') process.exitCode = r ? 0 : 2; });
}
