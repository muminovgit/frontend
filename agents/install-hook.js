#!/usr/bin/env node
// Claude Code hook'ini ~/.claude/settings.json ga qo'shadi (mavjud sozlamalarga tegmaydi).
//   node agents/install-hook.js [agent]      # agent: dilnoza (default) yoki roster.json dagi istalgan xodim id si
//   node agents/install-hook.js --remove
const fs = require('fs'), os = require('os'), path = require('path');
const file = path.join(os.homedir(), '.claude', 'settings.json');
const hook = path.join(__dirname, 'hook.js');
const MARK = 'agent-office-hook';
const events = ['UserPromptSubmit', 'PostToolUse', 'Stop'];

let cfg = {};
try { cfg = JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { if (e.code !== 'ENOENT') { console.error('settings.json o\'qilmadi:', e.message); process.exit(1); } }
cfg.hooks = cfg.hooks || {};
for (const ev of events) cfg.hooks[ev] = (cfg.hooks[ev] || []).filter(g => !JSON.stringify(g).includes(MARK));

if (process.argv[2] !== '--remove') {
  const agent = process.argv[2] || 'dilnoza';
  const env = ['OFFICE_URL', 'OFFICE_TOKEN'].filter(k => process.env[k]).map(k => `${k}='${process.env[k]}'`).join(' ');
  const cmd = `${env} OFFICE_AGENT=${agent} node "${hook}" # ${MARK}`.trim();
  for (const ev of events) cfg.hooks[ev].push({ hooks: [{ type: 'command', command: cmd }] });
}
for (const ev of events) if (!cfg.hooks[ev].length) delete cfg.hooks[ev];

fs.mkdirSync(path.dirname(file), { recursive: true });
fs.writeFileSync(file, JSON.stringify(cfg, null, 2));
console.log(process.argv[2] === '--remove' ? 'Hook o\'chirildi' : 'Hook o\'rnatildi', '→', file);
