import { useState } from 'react';
import { AlertTriangle, Briefcase, PieChart, TrendingUp, Wallet } from 'lucide-react';
import { homeStats } from '../data/mock';
import { mln, fmtNum, type Currency } from '../lib/format';
import { CurrencyToggle } from '../components/CurrencyToggle';
import { StatCard } from '../components/StatCard';

export function Home() {
  const [cur, setCur] = useState<Currency>('UZS');
  const s = homeStats;

  return (
    <section className="page">
      <div className="page-head">
        <div>
          <h1>Bosh sahifa</h1>
          <p className="muted">To'lovlar, portfel va risk ko'rsatkichlari bir joyda</p>
        </div>
        <CurrencyToggle value={cur} onChange={setCur} />
      </div>

      <div className="grid-2">
        <div className="card portfolio">
          <div className="portfolio-icon"><Briefcase size={22} /></div>
          <div className="muted">Muddatli to'lov portfeli</div>
          <div className="big-number">{mln(s.portfolioTotal, cur)}</div>
          <div className="portfolio-foot">
            <span className="muted">Noyabr</span>
            <strong>{mln(s.portfolioMonth, cur)}</strong>
          </div>
        </div>

        <div className="card list-card">
          <div className="metric">
            <div>
              <div className="muted"><Wallet size={14} /> To'lovlarning umumiy miqdori</div>
              <div className="sub">Noyabr: {fmtNum(s.paymentsMonthAmount)} UZS</div>
            </div>
            <strong>{mln(s.paymentsTotal, cur)}</strong>
          </div>
          <div className="metric">
            <div>
              <div className="muted"><PieChart size={14} /> To'lovlarning umumiy soni</div>
              <div className="sub">Noyabr: {s.paymentsMonthCount}</div>
            </div>
            <strong>{fmtNum(s.paymentsCount)}</strong>
          </div>
          <div className="metric">
            <div>
              <div className="muted"><TrendingUp size={14} /> Kelajakdagi davrlarning foydasi</div>
              <div className="sub">Noyabr: {mln(s.futureProfitMonth, cur)}</div>
            </div>
            <strong>{mln(s.futureProfit, cur)}</strong>
          </div>
        </div>
      </div>

      <h2>Risk va kechikishlar</h2>
      <div className="grid-4">
        <div className="card danger-card">
          <div className="danger-title"><AlertTriangle size={18} /> Muddati o'tgan to'lovlar miqdori</div>
          <div className="big-number">{mln(s.overdueAmount, cur)}</div>
          <div className="muted">Muddati o'tgan to'lovlar soni: <strong>{s.overdueCount}</strong></div>
        </div>
        <StatCard label="NPL (30 kunlik)" value={`${s.npl30.toFixed(2)}%`} hint="O'tgan haftadan beri" tone="danger" />
        <StatCard label="NPL (60 kunlik)" value={`${s.npl60.toFixed(2)}%`} hint="O'tgan haftadan beri" tone="danger" />
      </div>
    </section>
  );
}
