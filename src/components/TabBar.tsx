export type TabId = 'timeline' | 'growth' | 'add' | 'family' | 'book';

const TABS: { id: TabId; label: string }[] = [
  { id: 'timeline', label: 'Xotira' },
  { id: 'growth', label: "O'sish" },
  { id: 'add', label: 'Qo\'shish' },
  { id: 'family', label: 'Oila' },
  { id: 'book', label: 'Kitob' },
];

export function TabBar({ current, onChange }: { current: TabId; onChange: (id: TabId) => void }) {
  return (
    <nav className="tabbar" aria-label="Asosiy menyu">
      {TABS.map((t) => {
        const isAdd = t.id === 'add';
        return (
          <button
            key={t.id}
            className={`tab${isAdd ? ' add' : ''}`}
            aria-current={current === t.id ? 'page' : undefined}
            onClick={() => onChange(t.id)}
          >
            <span className="ico" aria-hidden="true">{isAdd ? '+' : ''}</span>
            <span>{t.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
