import { X } from 'lucide-react';

export interface Tab {
  key: string;
  label: string;
}

interface Props {
  tabs: Tab[];
  activeKey: string;
  onSelect: (key: string) => void;
  onClose: (key: string) => void;
}

export function TabBar({ tabs, activeKey, onSelect, onClose }: Props) {
  return (
    <div className="tabbar" role="tablist">
      {tabs.map((t) => (
        <div
          key={t.key}
          role="tab"
          aria-selected={t.key === activeKey}
          tabIndex={0}
          className={`tab ${t.key === activeKey ? 'active' : ''}`}
          onClick={() => onSelect(t.key)}
          onKeyDown={(e) => e.key === 'Enter' && onSelect(t.key)}
        >
          <span>{t.label}</span>
          {t.key !== 'home' && (
            <button
              className="tab-close"
              aria-label={`${t.label}ni yopish`}
              onClick={(e) => {
                e.stopPropagation();
                onClose(t.key);
              }}
            >
              <X size={14} />
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
