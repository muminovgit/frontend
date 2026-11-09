import { useMemo, useState } from 'react';
import { tariffs } from '../data/mock';
import { fmtNum, money } from '../lib/format';

export function Calculator() {
  const [amount, setAmount] = useState(10_000_000);
  const [tariffId, setTariffId] = useState(tariffs[1].id);
  const tariff = tariffs.find((t) => t.id === tariffId) ?? tariffs[0];

  const result = useMemo(() => {
    const total = amount * (1 + tariff.percent / 100);
    const monthly = total / tariff.termMonths;
    return { total, monthly, profit: total - amount };
  }, [amount, tariff]);

  return (
    <section className="page">
      <div className="page-head">
        <div>
          <h1>Kalkulyator</h1>
          <p className="muted">Oylik to'lovni hisoblash</p>
        </div>
      </div>
      <div className="grid-2">
        <div className="card form">
          <label>
            Summa (so'm)
            <input
              className="input"
              type="number"
              min={0}
              value={amount}
              onChange={(e) => setAmount(Math.max(0, Number(e.target.value) || 0))}
            />
          </label>
          <label>
            Tarif
            <select className="input" value={tariffId} onChange={(e) => setTariffId(e.target.value)}>
              {tariffs.map((t) => (
                <option key={t.id} value={t.id}>{t.name} ({t.percent}%)</option>
              ))}
            </select>
          </label>
          <p className="muted small">Minimal summa: {money(tariff.minAmount)}</p>
        </div>
        <div className="card list-card">
          <div className="metric"><span className="muted">Jami to'lov</span><strong>{money(result.total)}</strong></div>
          <div className="metric"><span className="muted">Oylik to'lov</span><strong>{money(result.monthly)}</strong></div>
          <div className="metric"><span className="muted">Foyda</span><strong>{fmtNum(result.profit)} so'm</strong></div>
        </div>
      </div>
    </section>
  );
}
