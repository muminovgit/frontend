import type { Child, Memory } from './types';
import type { Lang } from './i18n';
import { translate } from './i18n';

export function uid(): string {
  return Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

export function todayIso(): string {
  return toIso(new Date());
}

export function toIso(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export function parseIso(iso: string): Date {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d);
}

/** Bola necha yosh va necha oy ekanini tilga mos matn qilib qaytaradi. */
export function ageText(lang: Lang, birthIso: string, now: Date = new Date()): string {
  const birth = parseIso(birthIso);
  let months = (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth());
  if (now.getDate() < birth.getDate()) months -= 1;
  if (months < 0) months = 0;
  const years = Math.floor(months / 12);
  const rest = months % 12;
  if (years === 0) return translate(lang, 'age.m', { m: rest });
  return rest === 0 ? translate(lang, 'age.y', { y: years }) : translate(lang, 'age.ym', { y: years, m: rest });
}

/** 18 yoshga to'lgan sana. */
export function unlockDate(child: Child): string {
  const b = parseIso(child.birthDate);
  return toIso(new Date(b.getFullYear() + 18, b.getMonth(), b.getDate()));
}

/** Maktabga kirish yoshi (7) sanasi. */
export function schoolDate(child: Child): string {
  const b = parseIso(child.birthDate);
  return toIso(new Date(b.getFullYear() + 7, b.getMonth(), b.getDate()));
}

/** Xotira qachon ochiladi: aniq sana yoki eski "18 yosh" belgisi bo'yicha. */
export function memoryUnlockDate(child: Child, m: Memory): string | undefined {
  if (m.unlockAt) return m.unlockAt;
  if (m.locked) return unlockDate(child);
  return undefined;
}

export function isLockedNow(child: Child, m: Memory, today: string = todayIso()): boolean {
  const until = memoryUnlockDate(child, m);
  return until !== undefined && today < until;
}

/** Ochilishigacha qolgan vaqt: yil, oy, kun. */
export function countdown(from: string, to: string): { y: number; m: number; d: number } {
  const a = parseIso(from);
  const b = parseIso(to);
  let y = b.getFullYear() - a.getFullYear();
  let m = b.getMonth() - a.getMonth();
  let d = b.getDate() - a.getDate();
  if (d < 0) {
    m -= 1;
    const prevMonth = new Date(b.getFullYear(), b.getMonth(), 0).getDate();
    d += prevMonth;
  }
  if (m < 0) {
    y -= 1;
    m += 12;
  }
  return { y: Math.max(0, y), m: Math.max(0, m), d: Math.max(0, d) };
}

export function formatDate(lang: Lang, iso: string): string {
  const d = parseIso(iso);
  const month = translate(lang, `month.${d.getMonth() + 1}`);
  return lang === 'en' ? `${month} ${d.getDate()}, ${d.getFullYear()}` : `${d.getDate()} ${month} ${d.getFullYear()}`;
}

export function formatDay(lang: Lang, iso: string): string {
  return `${formatDate(lang, iso)} · ${translate(lang, `wd.${parseIso(iso).getDay()}`)}`;
}
