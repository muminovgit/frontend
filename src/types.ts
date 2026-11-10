export type MemoryKind = 'photo' | 'video' | 'audio' | 'note';

export interface Child {
  id: string;
  name: string;
  birthDate: string; // YYYY-MM-DD
}

export interface Memory {
  id: string;
  childId: string;
  date: string; // YYYY-MM-DD
  kind: MemoryKind;
  text: string;
  hasMedia: boolean;
  locked: boolean; // eski belgi: 18 yoshgacha qulflangan
  unlockAt?: string; // zaman kapsulasi: ochiladigan sana (YYYY-MM-DD)
  tag?: string; // tur kaliti: 'funny' | 'important' (tilga qarab ko'rsatiladi)
  albumId?: string; // bo'lsa, asosiy lentadan pastdagi albomlar bo'limiga o'tadi
  createdAt: string;
}

export interface Album {
  id: string;
  childId: string;
  name: string;
}

export interface Measurement {
  id: string;
  childId: string;
  date: string;
  heightCm?: number;
  weightKg?: number;
}

export interface Milestone {
  id: string;
  childId: string;
  date: string;
  title: string;
}

export type MemberRole = 'Ota' | 'Ona' | 'Buvi' | 'Bobo' | 'Boshqa';
export type MemberAccess = 'tahrirlay oladi' | "ko'ra oladi";

export interface Member {
  id: string;
  name: string;
  role: MemberRole;
  access: MemberAccess;
}

export interface AppState {
  lang: 'uz' | 'ru' | 'en';
  child: Child | null;
  memories: Memory[];
  measurements: Measurement[];
  milestones: Milestone[];
  members: Member[];
  albums: Album[];
}
