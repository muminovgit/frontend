import type { ReactElement } from 'react';

/**
 * Bo'y ko'rsatkichi: 70–100 sm oralig'idagi vertikal o'lchagich va jirafa.
 * Jirafaning bosh uchi berilgan bo'yga aynan to'g'ri keladi (masshtab haqiqiy).
 */

const MIN = 70;
const MAX = 100;
const TOP = 20;
const BOTTOM = 240;
const PX_PER_CM = (BOTTOM - TOP) / (MAX - MIN);

const yFor = (cm: number) => BOTTOM - (cm - MIN) * PX_PER_CM;

/** Yozuvlar bir-biriga tegmasligi uchun ularni kamida 14px oraliqda joylaydi. */
function labelPositions(marks: HeightMark[]) {
  const sorted = marks
    .map((mark) => ({ mark, y: yFor(mark.cm) }))
    .sort((a, b) => a.y - b.y);
  let prev = -Infinity;
  return sorted.map((item) => {
    const labelY = Math.max(item.y - 6, prev + 14);
    prev = labelY;
    return { ...item, labelY };
  });
}

export interface HeightMark {
  cm: number;
  label: string;
  current?: boolean;
}

export function HeightRuler({ heightCm, marks = [] }: { heightCm: number; marks?: HeightMark[] }) {
  const clamped = Math.min(MAX, Math.max(MIN, heightCm));
  const topY = yFor(clamped);
  // Jirafa lokal koordinatada: feet y=200, top y≈-2 (202 birlik). Shu masshtab bilan topY ga cho'zamiz.
  const scale = (BOTTOM - topY) / 202;

  const ticks: ReactElement[] = [];
  for (let cm = MIN; cm <= MAX; cm += 5) {
    const y = yFor(cm);
    const major = cm % 10 === 0;
    ticks.push(<line key={`t${cm}`} x1={40} y1={y} x2={major ? 52 : 48} y2={y} stroke="var(--muted)" strokeWidth={1.2} />);
    if (major) {
      ticks.push(
        <text key={`l${cm}`} x={34} y={y + 3.5} fontSize={10} textAnchor="end" fill="var(--muted)">
          {cm}
        </text>,
      );
    }
  }

  return (
    <svg className="chart" viewBox="0 0 300 250" role="img" aria-label={`Bo'y ${clamped} sm`}>
      <line x1={40} y1={TOP} x2={40} y2={BOTTOM} stroke="var(--muted)" strokeWidth={1.5} />
      <line x1={40} y1={BOTTOM} x2={290} y2={BOTTOM} stroke="var(--border)" strokeWidth={1.5} />
      {ticks}

      {labelPositions(marks).map(({ mark: m, y, labelY }) => (
        <g key={`${m.cm}-${m.label}`}>
          <line x1={52} y1={y} x2={270} y2={y} stroke={m.current ? 'var(--accent)' : 'var(--border)'} strokeWidth={m.current ? 1.5 : 1} strokeDasharray="4 4" />
          <circle cx={46} cy={y} r={m.current ? 4.5 : 3.5} fill={m.current ? 'var(--accent)' : 'var(--muted)'} />
          <text x={296} y={labelY} fontSize={m.current ? 12 : 10} fontWeight={m.current ? 800 : 700} textAnchor="end" fill={m.current ? 'var(--brand)' : 'var(--muted)'}>
            {m.label}
          </text>
        </g>
      ))}

      <g transform={`translate(70 ${BOTTOM}) scale(${scale.toFixed(4)}) translate(0 -200)`} aria-hidden="true">
        <path d="M30 104 Q12 120 18 152" fill="none" stroke="#C98A3D" strokeWidth={4} strokeLinecap="round" />
        <g fill="#FFD56B">
          <rect x={30} y={140} width={13} height={60} rx={6} />
          <rect x={48} y={140} width={13} height={60} rx={6} />
          <rect x={72} y={140} width={13} height={60} rx={6} />
          <rect x={90} y={140} width={13} height={60} rx={6} />
        </g>
        <g fill="#8A4E22">
          <rect x={30} y={193} width={13} height={7} rx={3} />
          <rect x={48} y={193} width={13} height={7} rx={3} />
          <rect x={72} y={193} width={13} height={7} rx={3} />
          <rect x={90} y={193} width={13} height={7} rx={3} />
        </g>
        <ellipse cx={60} cy={122} rx={48} ry={30} fill="#FFD56B" />
        <path d="M86 108 L100 34" stroke="#FFD56B" strokeWidth={22} strokeLinecap="round" />
        <ellipse cx={106} cy={28} rx={15} ry={12} fill="#FFD56B" />
        <ellipse cx={118} cy={34} rx={8} ry={6} fill="#FFD56B" />
        <ellipse cx={96} cy={22} rx={7} ry={4} fill="#FFD56B" transform="rotate(-20 96 22)" />
        <line x1={100} y1={16} x2={99} y2={2} stroke="#8A4E22" strokeWidth={3} strokeLinecap="round" />
        <line x1={112} y1={16} x2={113} y2={2} stroke="#8A4E22" strokeWidth={3} strokeLinecap="round" />
        <circle cx={99} cy={1} r={3.5} fill="#8A4E22" />
        <circle cx={113} cy={1} r={3.5} fill="#8A4E22" />
        <circle cx={110} cy={24} r={2.6} fill="#2A2140" />
        <circle cx={122} cy={33} r={1.4} fill="#8A4E22" />
        <g fill="#C98A3D">
          <circle cx={48} cy={112} r={7} />
          <circle cx={70} cy={100} r={6} />
          <circle cx={60} cy={136} r={8} />
          <circle cx={84} cy={128} r={6} />
          <circle cx={38} cy={128} r={5} />
          <circle cx={92} cy={84} r={5} />
          <circle cx={98} cy={60} r={5} />
          <circle cx={104} cy={44} r={3.5} />
        </g>
      </g>
    </svg>
  );
}

/** Oddiy chiziqli grafik (vazn uchun). */
export function LineChart({ points, unit, color }: { points: { label: string; value: number }[]; unit: string; color: string }) {
  if (points.length === 0) return <p className="muted small">Hozircha ma'lumot yo'q.</p>;
  const W = 300, H = 140, PAD_L = 36, PAD_R = 12, PAD_T = 12, PAD_B = 26;
  const values = points.map((p) => p.value);
  const min = Math.min(...values) - 1;
  const max = Math.max(...values) + 1;
  const x = (i: number) => (points.length === 1 ? (PAD_L + W - PAD_R) / 2 : PAD_L + (i * (W - PAD_L - PAD_R)) / (points.length - 1));
  const y = (v: number) => PAD_T + (H - PAD_T - PAD_B) * (1 - (v - min) / (max - min || 1));
  const line = points.map((p, i) => `${x(i)},${y(p.value)}`).join(' ');

  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${unit} grafigi`}>
      <line x1={PAD_L} y1={H - PAD_B} x2={W - PAD_R} y2={H - PAD_B} stroke="var(--border)" />
      <text x={0} y={y(max) + 4} fontSize={10} fill="var(--muted)">{max.toFixed(0)}</text>
      <text x={0} y={y(min) + 4} fontSize={10} fill="var(--muted)">{min.toFixed(0)}</text>
      {points.length > 1 && <polyline points={line} fill="none" stroke={color} strokeWidth={3} strokeLinejoin="round" strokeLinecap="round" />}
      {points.map((p, i) => (
        <g key={`${p.label}-${i}`}>
          <circle cx={x(i)} cy={y(p.value)} r={4.5} fill={color} />
          <text x={x(i)} y={H - 8} fontSize={10} textAnchor="middle" fill="var(--muted)">{p.label}</text>
        </g>
      ))}
    </svg>
  );
}
