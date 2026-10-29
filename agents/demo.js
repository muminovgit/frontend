// Serverga haqiqiy HTTP orqali ulangan namunaviy agent (simulyatsiya emas, kod misoli).
// node server.js  (bir terminalda)   node agents/demo.js  (boshqasida)
const office = require('./office');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const work = [['research', 'Bozor tahlili'], ['writer', 'Blog post'], ['sales', 'Lead topish'], ['coder', 'Bug fix'], ['support', 'Ticket javob']];

async function run([agent, task]) {
  for (;;) {
    await office.start(agent, task);
    for (let p = 0.1; p <= 1; p += 0.1) { await sleep(600 + Math.random() * 900); await office.progress(agent, p); }
    if (Math.random() < 0.6) {
      const ok = await office.askApproval(agent, task);
      if (!ok) continue; // rad etildi — qayta urinadi
    }
    await office.done(agent);
    await sleep(3000 + Math.random() * 4000);
  }
}
work.forEach(run);
