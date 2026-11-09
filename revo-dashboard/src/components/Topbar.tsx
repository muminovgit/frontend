import { useEffect, useRef, useState } from 'react';
import { Bell, Calculator, Download, Moon, PanelLeft, RefreshCw, Search, Sparkles, Sun, Wallet } from 'lucide-react';
import { fmtNum } from '../lib/format';

interface Props {
  breadcrumb: string;
  onToggleSidebar: () => void;
  onOpenCalculator: () => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export function Topbar({ breadcrumb, onToggleSidebar, onOpenCalculator, theme, onToggleTheme }: Props) {
  const [lang, setLang] = useState('UZ');
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="icon-btn" onClick={onToggleSidebar} aria-label="Menyuni yig'ish">
          <PanelLeft size={18} />
        </button>
        <span className="breadcrumb">{breadcrumb}</span>
        <label className="search">
          <Search size={16} />
          <input ref={inputRef} value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Qidirish" />
          <kbd>Ctrl K</kbd>
        </label>
      </div>
      <div className="topbar-right">
        <button className="icon-btn" onClick={onToggleTheme} aria-label="Mavzu">
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button className="icon-btn" aria-label="Yangilash" onClick={() => window.location.reload()}>
          <RefreshCw size={18} />
        </button>
        <button className="icon-btn badge-wrap" aria-label="Bildirishnomalar">
          <Bell size={18} />
          <span className="badge">9+</span>
        </button>
        <select className="lang" value={lang} onChange={(e) => setLang(e.target.value)} aria-label="Til">
          <option>UZ</option>
          <option>RU</option>
          <option>EN</option>
        </select>
        <button className="icon-btn" aria-label="AI yordamchi"><Sparkles size={18} /></button>
        <button className="icon-btn" aria-label="Eksport" onClick={() => window.print()}><Download size={18} /></button>
        <button className="icon-btn" aria-label="Kalkulyator" onClick={onOpenCalculator}><Calculator size={18} /></button>
        <div className="balance"><Wallet size={16} /> {fmtNum(-12_315_819)} UZS</div>
        <div className="user"><span className="avatar">AB</span><span>Foydalanuvchi</span></div>
      </div>
    </header>
  );
}
