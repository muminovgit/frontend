import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { navigation, type NavItem } from '../data/navigation';

interface Props {
  activeKey: string;
  collapsed: boolean;
  onOpen: (key: string, label: string) => void;
}

export function Sidebar({ activeKey, collapsed, onOpen }: Props) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ "Muddatli to'lovlar": true });

  const renderItem = (item: NavItem, depth = 0) => {
    const Icon = item.icon;
    const hasChildren = !!item.children?.length;
    const isOpen = expanded[item.label];
    const isActive = item.key === activeKey;

    return (
      <li key={`${depth}-${item.label}`}>
        <button
          type="button"
          className={`nav-item depth-${depth} ${isActive ? 'active' : ''}`}
          title={collapsed ? item.label : undefined}
          onClick={() => {
            if (hasChildren) {
              setExpanded((s) => ({ ...s, [item.label]: !isOpen }));
            } else if (item.key) {
              onOpen(item.key, item.label);
            }
          }}
        >
          <Icon size={18} aria-hidden />
          {!collapsed && <span className="nav-label">{item.label}</span>}
          {!collapsed && hasChildren && (isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />)}
        </button>
        {hasChildren && isOpen && !collapsed && (
          <ul className="nav-children">{item.children!.map((c) => renderItem(c, depth + 1))}</ul>
        )}
      </li>
    );
  };

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="brand">
        <span className="brand-dot" aria-hidden />
        {!collapsed && <span>Revo</span>}
      </div>
      <nav>
        <ul className="nav-list">{navigation.map((i) => renderItem(i))}</ul>
      </nav>
    </aside>
  );
}
