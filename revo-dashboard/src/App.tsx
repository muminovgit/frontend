import { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { TabBar, type Tab } from './components/TabBar';
import { Home } from './pages/Home';
import { Installments } from './pages/Installments';
import { OpenInstallment } from './pages/OpenInstallment';
import { Tariffs } from './pages/Tariffs';
import { Calculator } from './pages/Calculator';
import { Placeholder } from './pages/Placeholder';
import { labelFor } from './data/navigation';

const HOME: Tab = { key: 'home', label: 'Bosh sahifa' };

function getInitialTheme(): 'light' | 'dark' {
  try {
    const saved = localStorage.getItem('revo-theme');
    if (saved === 'light' || saved === 'dark') return saved;
  } catch {
    /* localStorage ishlamasa, tizim mavzusidan foydalanamiz */
  }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export default function App() {
  const [tabs, setTabs] = useState<Tab[]>([HOME]);
  const [activeKey, setActiveKey] = useState('home');
  const [collapsed, setCollapsed] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>(getInitialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem('revo-theme', theme);
    } catch {
      /* ignore */
    }
  }, [theme]);

  const openTab = (key: string, label?: string) => {
    setTabs((prev) => (prev.some((t) => t.key === key) ? prev : [...prev, { key, label: label ?? labelFor(key) }]));
    setActiveKey(key);
  };

  const closeTab = (key: string) => {
    setTabs((prev) => {
      const next = prev.filter((t) => t.key !== key);
      if (key === activeKey) setActiveKey(next[next.length - 1]?.key ?? 'home');
      return next;
    });
  };

  const renderPage = () => {
    switch (activeKey) {
      case 'home':
        return <Home />;
      case 'installments':
        return <Installments onOpenNew={() => openTab('open-installment')} />;
      case 'open-installment':
        return <OpenInstallment />;
      case 'tariffs':
        return <Tariffs />;
      case 'calculator':
        return <Calculator />;
      default:
        return <Placeholder title={labelFor(activeKey)} />;
    }
  };

  const activeLabel = tabs.find((t) => t.key === activeKey)?.label ?? 'Bosh sahifa';

  return (
    <div className={`app ${collapsed ? 'is-collapsed' : ''}`}>
      <Sidebar activeKey={activeKey} collapsed={collapsed} onOpen={(k, l) => openTab(k, l)} />
      <div className="main">
        <Topbar
          breadcrumb={activeLabel}
          onToggleSidebar={() => setCollapsed((c) => !c)}
          onOpenCalculator={() => openTab('calculator')}
          theme={theme}
          onToggleTheme={() => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))}
        />
        <TabBar tabs={tabs} activeKey={activeKey} onSelect={setActiveKey} onClose={closeTab} />
        <main className="content">{renderPage()}</main>
      </div>
    </div>
  );
}
