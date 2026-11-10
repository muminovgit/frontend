// Demo ma'lumotlar. Haqiqiy ma'lumot o'rniga keyin API yoki baza ulanadi.
export const child = {
  name: 'Aziza',
  birthDate: '2025-03-14',
  unlockAge: 18,
};

// type: photo | video | voice | milestone
export const entries = [
  { id: 1, date: '2025-03-14', type: 'video', title: 'Birinchi kun', text: 'Kasalxonadan uyga qaytgan kun.' },
  { id: 2, date: '2025-04-01', type: 'milestone', title: 'Birinchi kulgi', text: 'Otasi bilan o\'ynayotganda birinchi marta kuldi.' },
  { id: 3, date: '2025-07-20', type: 'voice', title: 'Birinchi bo\'g\'in', text: '"Ma-ma" deb aytdi.', duration: '0:42' },
  { id: 4, date: '2025-10-05', type: 'photo', title: 'Birinchi qadam', text: 'Divanni ushlab, bir qadam tashladi.' },
  { id: 5, date: '2026-02-11', type: 'milestone', title: 'Birinchi so\'z', text: '"Ona" deb aytdi.' },
  { id: 6, date: '2026-06-01', type: 'video', title: 'Bog\'cha bog\'i', text: 'Bog\'chadagi birinchi kuni.' },
  { id: 7, date: '2026-09-02', type: 'photo', title: 'Yangi qo\'g\'irchoq', text: 'Bobosi sovg\'a qildi.' },
  { id: 8, date: '2043-03-14', type: 'video', title: '18 yoshingiz', text: 'Bu xotira 18 yoshda ochiladi.', locked: true },
];

// Vazn (kg) va bo'y (sm) yozuvlari
export const measurements = [
  { date: '2025-03-14', weight: 3.4, height: 50 },
  { date: '2025-06-14', weight: 6.1, height: 60 },
  { date: '2025-12-14', weight: 8.9, height: 72 },
  { date: '2026-06-14', weight: 10.8, height: 79 },
  { date: '2026-11-01', weight: 11.6, height: 82 },
];
