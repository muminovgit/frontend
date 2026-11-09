export type InstallmentStatus = 'active' | 'inactive' | 'frozen' | 'closed' | 'cancelled';

export interface Installment {
  id: number;
  customer: string;
  phone: string;
  branch: string;
  plan: string;
  termMonths: number;
  percent: number;
  currency: 'UZS' | 'USD';
  total: number;        // jami summa (UZS)
  paid: number;         // to'langan summa (UZS)
  status: InstallmentStatus;
  inDebt: boolean;
  debtAmount: number;   // UZS
  manager: string;
  cardLinked: boolean;
  nextDate: string | null; // ISO
  nextAmount: number;
}

export const installments: Installment[] = [
  { id: 1001, customer: 'Test Mijoz Bir', phone: '+998 90 000-00-01', branch: 'Asosiy filial', plan: 'Dullor', termMonths: 12, percent: 5, currency: 'USD', total: 252_000_000, paid: 0, status: 'inactive', inDebt: false, debtAmount: 0, manager: 'Operator A', cardLinked: false, nextDate: null, nextAmount: 0 },
  { id: 1002, customer: 'Test Mijoz Ikki', phone: '+998 90 000-00-02', branch: 'Asosiy filial', plan: '6 oylik', termMonths: 6, percent: 10, currency: 'UZS', total: 3_000_000, paid: 0, status: 'cancelled', inDebt: true, debtAmount: 3_300_000, manager: 'Operator B', cardLinked: false, nextDate: null, nextAmount: 0 },
  { id: 1003, customer: 'Test Mijoz Uch', phone: '+998 90 000-00-03', branch: 'Asosiy filial', plan: 'Imtiyozli 12 oy', termMonths: 12, percent: 0, currency: 'UZS', total: 2_500_000, paid: 625_000, status: 'active', inDebt: false, debtAmount: 0, manager: 'Operator A', cardLinked: false, nextDate: '2027-03-03', nextAmount: 208_333, },
  { id: 1004, customer: 'Test Mijoz To\'rt', phone: '+998 90 000-00-04', branch: 'Filial 2', plan: '6 oylik 2', termMonths: 6, percent: 15, currency: 'UZS', total: 4_800_000, paid: 0, status: 'frozen', inDebt: true, debtAmount: 4_800_000, manager: 'Operator C', cardLinked: true, nextDate: '2026-12-03', nextAmount: 800_000 },
  { id: 1005, customer: 'Test Mijoz Besh', phone: '+998 90 000-00-05', branch: 'Filial 2', plan: '12 oylik', termMonths: 12, percent: 8, currency: 'UZS', total: 12_000_000, paid: 12_000_000, status: 'closed', inDebt: false, debtAmount: 0, manager: 'Operator B', cardLinked: true, nextDate: null, nextAmount: 0 },
  { id: 1006, customer: 'Test Mijoz Olti', phone: '+998 90 000-00-06', branch: 'Asosiy filial', plan: '3 oylik', termMonths: 3, percent: 4, currency: 'UZS', total: 6_000_000, paid: 2_000_000, status: 'active', inDebt: true, debtAmount: 1_000_000, manager: 'Operator A', cardLinked: false, nextDate: '2026-11-20', nextAmount: 2_080_000 },
  { id: 1007, customer: 'Test Mijoz Yetti', phone: '+998 90 000-00-07', branch: 'Filial 3', plan: '9 oylik', termMonths: 9, percent: 12, currency: 'UZS', total: 9_000_000, paid: 1_000_000, status: 'active', inDebt: false, debtAmount: 0, manager: 'Operator C', cardLinked: true, nextDate: '2026-12-15', nextAmount: 1_000_000 },
];

export const openLimits: { id: number; customer: string; limit: number; used: number }[] = [];

export const tariffs = [
  { id: 't1', name: '3 oylik', termMonths: 3, percent: 4, minAmount: 1_000_000 },
  { id: 't2', name: '6 oylik', termMonths: 6, percent: 10, minAmount: 2_000_000 },
  { id: 't3', name: '9 oylik', termMonths: 9, percent: 12, minAmount: 3_000_000 },
  { id: 't4', name: '12 oylik', termMonths: 12, percent: 15, minAmount: 5_000_000 },
  { id: 't5', name: 'Imtiyozli 12 oy', termMonths: 12, percent: 0, minAmount: 2_000_000 },
];

export const homeStats = {
  portfolioTotal: 395_000_000,
  portfolioMonth: 22_700_000,
  paymentsTotal: 643_500_000,
  paymentsCount: 714,
  paymentsMonthCount: 13,
  paymentsMonthAmount: 661_000,
  futureProfit: 60_900_000,
  futureProfitMonth: 49_500_000,
  overdueAmount: 239_100_000,
  overdueCount: 81,
  npl30: 46.76,
  npl60: 46.51,
};
