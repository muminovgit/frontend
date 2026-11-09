import { tariffs } from '../data/mock';
import { money } from '../lib/format';

export function Tariffs() {
  return (
    <section className="page">
      <div className="page-head">
        <div>
          <h1>Tariflar</h1>
          <p className="muted">Muddatli to'lov tariflari va foiz stavkalari</p>
        </div>
      </div>
      <div className="card table-card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Nomi</th><th>Muddat</th><th>Foiz</th><th>Minimal summa</th></tr>
            </thead>
            <tbody>
              {tariffs.map((t) => (
                <tr key={t.id}>
                  <td className="strong">{t.name}</td>
                  <td>{t.termMonths} oy</td>
                  <td>{t.percent}%</td>
                  <td>{money(t.minAmount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
