# Revo Dashboard

Muddatli to'lovlar, CRM va boshqaruv paneli uchun frontend prototipi.
Ma'lumotlar `src/data/mock.ts` da soxta (mock) ko'rinishda. Haqiqiy API ulanmagan.

## Ishga tushirish

```bash
cd revo-dashboard
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Bo'limlar

- Bosh sahifa: portfel va risk ko'rsatkichlari
- Muddatli to'lovlar: statistika, filtrlar, jadval, CSV eksport
- Nasiya ochish: ochiq limitlar holati
- Tariflar
- Kalkulyator: oylik to'lovni hisoblash
- Boshqa bo'limlar: "tez orada" sahifasi

## Tuzilma

```
src/
  components/   Sidebar, Topbar, TabBar
  pages/        Har bir bo'lim sahifasi
  data/         Mock ma'lumotlar va navigatsiya
  lib/          Formatlash yordamchilari
```
