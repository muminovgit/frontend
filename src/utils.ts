import type { Child } from './types';

export function uid(): string {
  return Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

export function todayIso(): string {
  const d = new Date();
  return toIso(d);
}

export function toIso(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function parseIso(iso: string): Date {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, m - 1, d);
}

/** Bola necha yosh va necha oy ekanini matn qilib qaytaradi. */
export function ageText(birthIso: string, now: Date = new Date()): string {
  const birth = parseIso(birthIso);
  let months = (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth());
  if (now.getDate() < birth.getDate()) months -= 1;
  if (months < 0) months = 0;
  const years = Math.floor(months / 12);
  const rest = months % 12;
  if (years === 0) return `${rest} oy`;
  return rest === 0 ? `${years} yosh` : `${years} yosh ${rest} oy`;
}

/** 18 yoshga to'lgan sana. */
export function unlockDate(child: Child): string {
  const b = parseIso(child.birthDate);
  return toIso(new Date(b.getFullYear() + 18, b.getMonth(), b.getDate()));
}

export function isLockedNow(child: Child, memoryLocked: boolean, today: string = todayIso()): boolean {
  return memoryLocked && today < unlockDate(child);
}

export function formatDate(iso: string): string {
  const d = parseIso(iso);
  const months = ['yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr'];
  return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
}

export function formatDay(iso: string): string {
  const days = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba'];
  return `${formatDate(iso)} · ${days[parseIso(iso).getDay()]}`;
}
