import type { LucideIcon } from 'lucide-react';
import {
  LayoutDashboard, PieChart, Users, Megaphone, Briefcase, Send, Smartphone,
  UsersRound, PhoneCall, Contact, Globe, Store, Wallet, Settings, User, BadgeDollarSign,
} from 'lucide-react';

export interface NavItem {
  label: string;
  icon: LucideIcon;
  key?: string;            // ochiladigan tab kaliti
  children?: NavItem[];
}

export const navigation: NavItem[] = [
  { label: 'Bosh sahifa', icon: LayoutDashboard, key: 'home' },
  {
    label: "Muddatli to'lovlar", icon: PieChart,
    children: [
      { label: 'Statistika', icon: PieChart, key: 'home' },
      { label: "Muddatli to'lovlar", icon: PieChart, key: 'installments' },
      { label: 'Naqd savdo', icon: Wallet, key: 'cash-sales' },
      { label: "Kutilayotgan to'lovlar", icon: Wallet, key: 'pending' },
      { label: 'Undiruv doskasi', icon: Wallet, key: 'collection' },
      { label: 'Tariflar', icon: Wallet, key: 'tariffs' },
      { label: 'Kalkulyator', icon: Wallet, key: 'calculator' },
      { label: "To'lov usullari", icon: Wallet, key: 'payment-methods' },
      { label: "To'lovlar", icon: Wallet, key: 'payments' },
      { label: 'Qora ro\'yxat', icon: Wallet, key: 'blacklist' },
      { label: 'Sozlamalar', icon: Settings, key: 'installment-settings' },
      { label: 'Telegram sozlamalari', icon: Send, key: 'telegram-settings' },
    ],
  },
  { label: 'Skoring', icon: BadgeDollarSign, key: 'scoring' },
  { label: 'Hamkorlar', icon: Briefcase, key: 'partners' },
  { label: 'Tashqi tizimlar', icon: Globe, key: 'external' },
  { label: 'Mijozlar', icon: Users, key: 'customers' },
  { label: 'Marketing', icon: Megaphone, key: 'marketing' },
  { label: 'Nasiya ochish', icon: Briefcase, key: 'open-installment' },
  { label: 'Telegram boshqaruv', icon: Send, key: 'telegram' },
  { label: 'Qurilmalar', icon: Smartphone, key: 'devices' },
  { label: 'HR', icon: UsersRound, key: 'hr' },
  { label: 'Call-center', icon: PhoneCall, key: 'call-center' },
  { label: 'CRM', icon: Contact, key: 'crm' },
  { label: 'Bronlash', icon: Globe, key: 'booking' },
  { label: "Do'kon", icon: Store, key: 'shop' },
  { label: 'Investorlar', icon: Briefcase, key: 'investors' },
  { label: 'Boshqaruv', icon: Settings, key: 'admin' },
  { label: 'Profil', icon: User, key: 'profile' },
];

export const tabLabels: Record<string, string> = {
  home: 'Bosh sahifa',
  installments: "Muddatli to'lovlar",
  'open-installment': 'Nasiya ochish',
  tariffs: 'Tariflar',
  calculator: 'Kalkulyator',
};

export function labelFor(key: string): string {
  if (tabLabels[key]) return tabLabels[key];
  const find = (items: NavItem[]): string | undefined => {
    for (const it of items) {
      if (it.key === key) return it.label;
      if (it.children) {
        const r = find(it.children);
        if (r) return r;
      }
    }
    return undefined;
  };
  return find(navigation) ?? key;
}
