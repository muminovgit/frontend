// Serverga haqiqiy HTTP orqali ulangan namunaviy xodimlar (kod misoli).
// node server.js  (bir terminalda)   node agents/demo.js  (boshqasida)
const office = require('./office');
const roster = require('../roster.json');
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function run(emp) {
  for (;;) {
    const task = emp.demo[Math.floor(Math.random() * emp.demo.length)];
    await office.start(emp.id, task);
    for (let p = 0.1; p <= 1; p += 0.1) { await sleep(600 + Math.random() * 900); await office.progress(emp.id, p); }
    if (Math.random() < 0.4 && !(await office.askApproval(emp.id, task))) continue; // rad etildi — qayta urinadi
    await office.done(emp.id);
    await sleep(3000 + Math.random() * 4000);
  }
}
roster.employees.slice(0, 5).forEach(run);
