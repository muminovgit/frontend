export const USD_RATE = 12600; // soxta kurs, prototip uchun

export function fmtNum(n: number, digits = 0): string {
  return n.toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export type Currency = 'UZS' | 'USD';

export function money(amountUzs: number, currency: Currency = 'UZS'): string {
  if (currency === 'USD') {
    return `${fmtNum(amountUzs / USD_RATE, 2)} USD`;
  }
  return `${fmtNum(amountUzs)} so'm`;
}

export function mln(amountUzs: number, currency: Currency = 'UZS'): string {
  if (currency === 'USD') {
    return `${fmtNum(amountUzs / USD_RATE / 1e6, 1)} mln USD`;
  }
  return `${fmtNum(amountUzs / 1e6, 1)} mln UZS`;
}

export function fmtDate(iso: string): string {
  const d = new Date(iso);
  const months = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun', 'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'];
  return `${String(d.getDate()).padStart(2, '0')}-${months[d.getMonth()]} ${d.getFullYear()}`;
}

export function daysUntil(iso: string, today = new Date()): number {
  const ms = new Date(iso).getTime() - today.getTime();
  return Math.ceil(ms / 86_400_000);
}
