import { useMemo, useState } from 'react';
import { Download, Filter, Plus } from 'lucide-react';
import { installments as all, type Installment, type InstallmentStatus } from '../data/mock';
import { daysUntil, fmtDate, fmtNum, money, type Currency } from '../lib/format';
import { CurrencyToggle } from '../components/CurrencyToggle';
import { StatCard } from '../components/StatCard';

const STATUS_LABEL: Record<InstallmentStatus, string> = {
  active: 'Faol',
  inactive: 'Faol emas',
  frozen: 'Muzlatilgan',
  closed: 'Yopilgan',
  cancelled: 'Bekor qilingan',
};

type Filter = 'all' | InstallmentStatus | 'debtors';
const FILTERS: { key: Filter; label: string }[] = [
  { key: 'all', label: 'Hammasi' },
  { key: 'active', label: 'Faol' },
  { key: 'inactive', label: 'Faol emas' },
  { key: 'frozen', label: 'Muzlatilgan' },
  { key: 'closed', label: 'Yopilgan' },
  { key: 'debtors', label: 'Qarzdorlar' },
  { key: 'cancelled', label: 'Bekor qilingan' },
];

function matches(i: Installment, f: Filter, name: string, phone: string): boolean {
  if (f === 'debtors' && !i.inDebt) return false;
  if (f !== 'all' && f !== 'debtors' && i.status !== f) return false;
  if (name && !i.customer.toLowerCase().includes(name.toLowerCase())) return false;
  if (phone && !i.phone.replace(/\D/g, '').includes(phone.replace(/\D/g, ''))) return false;
  return true;
}

function exportCsv(rows: Installment[]) {
  const header = ['id', 'customer', 'phone', 'plan', 'total_uzs', 'paid_uzs', 'status', 'debt_uzs'];
  const lines = rows.map((r) => [r.id, r.customer, r.phone, r.plan, r.total, r.paid, r.status, r.debtAmount].join(','));
  const blob = new Blob([[header.join(','), ...lines].join('\n')], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'installments.csv';
  a.click();
  URL.revokeObjectURL(url);
}

interface Props {
  onOpenNew: () => void;
}

export function Installments({ onOpenNew }: Props) {
  const [cur, setCur] = useState<Currency>('UZS');
  const [filter, setFilter] = useState<Filter>('all');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');

  const rows = useMemo(() => all.filter((i) => matches(i, filter, name, phone)), [filter, name, phone]);

  const totalAmount = rows.reduce((s, r) => s + r.total, 0);
  const remaining = rows.reduce((s, r) => s + (r.total - r.paid), 0);
  const profit = rows.reduce((s, r) => s + (r.total * r.percent) / 100, 0);

  return (
    <section className="page">
      <div className="page-head">
        <div>
          <h1>Muddatli to'lovlar</h1>
          <p className="muted">Muddatli to'lovlar, qarzdorlik va keyingi to'lovlarni boshqaring</p>
        </div>
        <div className="actions">
          <button className="btn ghost" onClick={() => exportCsv(rows)}><Download size={16} /> Eksport</button>
          <button className="btn primary" onClick={onOpenNew}><Plus size={16} /> Qo'shish</button>
        </div>
      </div>

      <div className="grid-4">
        <StatCard label="Soni" value={fmtNum(rows.length)} />
        <StatCard label="Miqdori" value={money(totalAmount, cur)} />
        <StatCard label="Qoldiq" value={money(remaining, cur)} />
        <StatCard label="Foyda miqdori" value={money(profit, cur)} />
      </div>

      <div className="card table-card">
        <div className="filters">
          <button className="btn ghost"><Filter size={16} /> Filtrlar</button>
          <CurrencyToggle value={cur} onChange={setCur} />
          <input className="input" placeholder="To'liq ismi" value={name} onChange={(e) => setName(e.target.value)} />
          <input className="input" placeholder="+998 (00) 000-00-00" value={phone} onChange={(e) => setPhone(e.target.value)} />
        </div>
        <div className="chips">
          {FILTERS.map((f) => (
            <button key={f.key} className={`chip ${filter === f.key ? 'active' : ''}`} onClick={() => setFilter(f.key)}>
              {f.label}
            </button>
          ))}
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>To'liq ismi</th>
                <th>Muddatli to'lov</th>
                <th>To'lov holati</th>
                <th>Keyingi to'lov</th>
                <th>Holat va qarz</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 && (
                <tr><td colSpan={5} className="empty">Ma'lumot topilmadi</td></tr>
              )}
              {rows.map((r) => {
                const pct = r.total ? Math.round((r.paid / r.total) * 100) : 0;
                const days = r.nextDate ? daysUntil(r.nextDate) : null;
                return (
                  <tr key={r.id}>
                    <td>
                      <div className="customer">
                        <span className="avatar sm">{r.customer.split(' ').map((w) => w[0]).slice(0, 2).join('')}</span>
                        <div>
                          <div className="strong">{r.customer}</div>
                          <div className="muted small">{r.phone} · #{r.id}</div>
                          <div className="muted small">{r.branch}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="strong">{r.plan}</div>
                      <div className="pills">
                        <span className="pill neutral">{r.termMonths} oy</span>
                        <span className="pill neutral">{r.percent}%</span>
                      </div>
                      <div className="muted small">{fmtDate(r.nextDate ?? '2026-11-04')}</div>
                    </td>
                    <td>
                      <div className="strong">{money(r.total, cur)}</div>
                      <div className="progress"><span style={{ width: `${pct}%` }} /></div>
                      <div className="muted small">{pct}% · Qoldiq {money(r.total - r.paid, cur)}</div>
                    </td>
                    <td>
                      {r.nextDate ? (
                        <>
                          <div className="strong">{fmtDate(r.nextDate)}</div>
                          <div className="small">{money(r.nextAmount, cur)}</div>
                          {days !== null && <span className="pill neutral">{days} kun ichida</span>}
                        </>
                      ) : (
                        <span className="muted">—</span>
                      )}
                    </td>
                    <td>
                      <span className={`pill status-${r.status}`}>{STATUS_LABEL[r.status]}</span>
                      <div className="small">{r.cardLinked ? 'Kartali' : 'Kartsiz'}</div>
                      <div className="small">
                        {r.inDebt ? <span className="debt">Qarz: {money(r.debtAmount, cur)}</span> : 'Qarz yo\'q'} · {r.manager}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
