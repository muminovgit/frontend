import { child, entries, measurements } from './data.js';

const MONTHS = [
  'yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun',
  'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr',
];

const TYPE_LABELS = {
  photo: 'Foto',
  video: 'Video',
  voice: 'Ovoz',
  milestone: 'Milestone',
};

const FILTERS = [
  ['all', 'Hammasi'],
  ['photo', 'Foto'],
  ['video', 'Video'],
  ['voice', 'Ovoz'],
  ['milestone', 'Milestone'],
];

let activeFilter = 'all';

function esc(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function parseDate(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d);
}

function formatDate(iso) {
  const d = parseDate(iso);
  return `${d.getDate()}-${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}

function monthKey(iso) {
  const d = parseDate(iso);
  return `${d.getFullYear()} ${MONTHS[d.getMonth()]}`;
}

function ageText(birthIso, todayDate = new Date()) {
  const b = parseDate(birthIso);
  let months = (todayDate.getFullYear() - b.getFullYear()) * 12 + (todayDate.getMonth() - b.getMonth());
  if (todayDate.getDate() < b.getDate()) months -= 1;
  const years = Math.floor(months / 12);
  const rest = months % 12;
  if (years === 0) return `${rest} oy`;
  return `${years} yil ${rest} oy`;
}

function unlockDate(birthIso, unlockAge) {
  const b = parseDate(birthIso);
  return new Date(b.getFullYear() + unlockAge, b.getMonth(), b.getDate());
}

function weightChart(points) {
  const W = 320;
  const H = 120;
  const pad = 16;
  const ws = points.map((p) => p.weight);
  const min = Math.min(...ws) - 0.5;
  const max = Math.max(...ws) + 0.5;
  const t0 = parseDate(points[0].date).getTime();
  const t1 = parseDate(points[points.length - 1].date).getTime();
  const xy = points.map((p) => {
    const x = pad + ((parseDate(p.date).getTime() - t0) / (t1 - t0 || 1)) * (W - pad * 2);
    const y = H - pad - ((p.weight - min) / (max - min || 1)) * (H - pad * 2);
    return [x.toFixed(1), y.toFixed(1)];
  });
  const line = xy.map(([x, y], i) => `${i === 0 ? 'M' : 'L'}${x},${y}`).join(' ');
  const dots = xy
    .map(([x, y]) => `<circle cx="${x}" cy="${y}" r="4" class="dot" />`)
    .join('');
  return `
    <svg viewBox="0 0 ${W} ${H}" class="chart" role="img" aria-label="Vazn o'sish grafigi">
      <path d="${line}" class="chart-line" fill="none" />
      ${dots}
    </svg>`;
}

function entryCard(e, today) {
  const isLocked = e.locked && parseDate(e.date) > today;
  const media = `<div class="media media-${e.type}" aria-hidden="true"></div>`;
  const lock = isLocked
    ? `<div class="lock">Qulflangan: ${esc(formatDate(e.date))} kuni ochiladi</div>`
    : '';
  const duration = e.duration ? ` · ${esc(e.duration)}` : '';
  return `
    <article class="card entry ${isLocked ? 'is-locked' : ''}">
      ${isLocked ? '' : media}
      <div class="entry-body">
        <div class="entry-meta">
          <span class="badge badge-${e.type}">${TYPE_LABELS[e.type]}${duration}</span>
          <time>${esc(formatDate(e.date))}</time>
        </div>
        <h3>${esc(e.title)}</h3>
        <p>${esc(e.text)}</p>
        ${lock}
      </div>
    </article>`;
}

function groupedEntries(list, today) {
  const sorted = [...list].sort((a, b) => (a.date < b.date ? 1 : -1));
  const groups = new Map();
  for (const e of sorted) {
    const key = monthKey(e.date);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(e);
  }
  if (groups.size === 0) {
    return '<p class="empty">Bu filtr bo\'yicha xotira yo\'q.</p>';
  }
  return [...groups.entries()]
    .map(
      ([key, items]) => `
      <section class="group">
        <h2 class="group-title">${esc(key)}</h2>
        ${items.map((e) => entryCard(e, today)).join('')}
      </section>`,
    )
    .join('');
}

function render(app) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const unlock = unlockDate(child.birthDate, child.unlockAge);
  const filtered =
    activeFilter === 'all' ? entries : entries.filter((e) => e.type === activeFilter);
  const last = measurements[measurements.length - 1];

  app.innerHTML = `
    <main class="page">
      <header class="hero">
        <p class="kicker">Xotira-hayot</p>
        <h1>${esc(child.name)}</h1>
        <p class="sub">Yoshi: ${esc(ageText(child.birthDate))} · Tug'ilgan: ${esc(formatDate(child.birthDate))}</p>
        <p class="sub small">18 yoshga to'lganda qulflangan xotiralar ochiladi: ${esc(formatDate(unlock.toISOString().slice(0, 10)))}</p>
      </header>

      <section class="card growth">
        <div class="growth-head">
          <div>
            <p class="label">Vazn</p>
            <p class="value">${last.weight} kg</p>
          </div>
          <div>
            <p class="label">Bo'y</p>
            <p class="value">${last.height} sm</p>
          </div>
        </div>
        ${weightChart(measurements)}
        <p class="caption">${esc(formatDate(measurements[0].date))} dan ${esc(formatDate(last.date))} gacha</p>
      </section>

      <nav class="filters" aria-label="Filtr">
        ${FILTERS.map(
          ([key, label]) =>
            `<button type="button" data-filter="${key}" class="chip ${key === activeFilter ? 'is-active' : ''}">${esc(label)}</button>`,
        ).join('')}
      </nav>

      <div class="timeline">
        ${groupedEntries(filtered, today)}
      </div>
    </main>`;

  app.querySelectorAll('[data-filter]').forEach((btn) => {
    btn.addEventListener('click', () => {
      activeFilter = btn.dataset.filter;
      render(app);
    });
  });
}

export function renderTimeline(app) {
  render(app);
}
