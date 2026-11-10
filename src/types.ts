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
  locked: boolean; // 18 yoshgacha qulflangan
  createdAt: string;
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

export interface Order {
  id: string;
  createdAt: string;
  option: string;
  price: number;
}

export interface AppState {
  child: Child | null;
  memories: Memory[];
  measurements: Measurement[];
  milestones: Milestone[];
  members: Member[];
  orders: Order[];
}
