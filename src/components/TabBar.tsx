import { useT } from '../useT';

export type TabId = 'timeline' | 'growth' | 'add' | 'family';

const TABS: { id: TabId; key: string }[] = [
  { id: 'timeline', key: 'tab.timeline' },
  { id: 'growth', key: 'tab.growth' },
  { id: 'add', key: 'tab.add' },
  { id: 'family', key: 'tab.family' },
];

export function TabBar({ current, onChange }: { current: TabId; onChange: (id: TabId) => void }) {
  const t = useT();
  return (
    <nav className="tabbar" aria-label="Menu">
      {TABS.map((tab) => {
        const isAdd = tab.id === 'add';
        return (
          <button
            key={tab.id}
            className={`tab${isAdd ? ' add' : ''}`}
            aria-current={current === tab.id ? 'page' : undefined}
            onClick={() => onChange(tab.id)}
          >
            <span className="ico" aria-hidden="true">{isAdd ? '+' : ''}</span>
            <span>{t(tab.key)}</span>
          </button>
        );
      })}
    </nav>
  );
}
