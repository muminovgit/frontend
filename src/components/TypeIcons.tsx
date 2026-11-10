import type { ReactElement } from 'react';

/** Qo'shish turlari uchun oddiy, bir xil uslubdagi ikonkalar (24×24, chiziqli). */
export type IconName = 'step' | 'word' | 'funny' | 'important' | 'photo' | 'video' | 'audio' | 'note';

const PATHS: Record<IconName, ReactElement> = {
  step: (
    <>
      <ellipse cx="9" cy="15" rx="2.2" ry="3.4" />
      <ellipse cx="16" cy="9" rx="2.2" ry="3.4" />
    </>
  ),
  word: <path d="M4 5h16v11H9l-5 4V5z" />,
  funny: (
    <>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M8.5 14c1 1.6 2.2 2.4 3.5 2.4s2.5-.8 3.5-2.4" />
      <circle cx="9" cy="10" r="0.8" fill="currentColor" />
      <circle cx="15" cy="10" r="0.8" fill="currentColor" />
    </>
  ),
  important: <path d="M12 3.5l2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.9 6.8 19.5l1-5.8-4.2-4.1 5.8-.8z" />,
  photo: (
    <>
      <rect x="3" y="7" width="18" height="13" rx="3" />
      <path d="M9 7l1.5-2.5h3L15 7" />
      <circle cx="12" cy="13.5" r="3.2" />
    </>
  ),
  video: (
    <>
      <rect x="3" y="6.5" width="13" height="11" rx="2.5" />
      <path d="M16 10.5l5-3v9l-5-3" />
    </>
  ),
  audio: (
    <>
      <rect x="9" y="3" width="6" height="11" rx="3" />
      <path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3" />
    </>
  ),
  note: (
    <>
      <rect x="5" y="3.5" width="14" height="17" rx="2.5" />
      <path d="M8.5 8.5h7M8.5 12h7M8.5 15.5h4" />
    </>
  ),
};

export function TypeIcon({ name, size = 22 }: { name: IconName; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {PATHS[name]}
    </svg>
  );
}
