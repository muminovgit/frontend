import { Briefcase } from 'lucide-react';
import { openLimits } from '../data/mock';
import { money } from '../lib/format';

export function OpenInstallment() {
  return (
    <section className="page">
      <div className="page-head">
        <div>
          <h1>Nasiya ochish</h1>
          <p className="muted">Ochiq muddatli to'lov shartnomalari va limitlar boshqaruvi.</p>
        </div>
      </div>

      <div className="card empty-state">
        {openLimits.length === 0 ? (
          <>
            <div className="empty-icon"><Briefcase size={28} /></div>
            <h3>Ochiq limitlar</h3>
            <p className="muted">Foydalanuvchilarning to'lov limitlari va mavjud shartnomalarini shu bo'limda boshqaring.</p>
          </>
        ) : (
          <table className="simple-table">
            <thead><tr><th>Mijoz</th><th>Limit</th><th>Ishlatilgan</th></tr></thead>
            <tbody>
              {openLimits.map((l) => (
                <tr key={l.id}>
                  <td>{l.customer}</td>
                  <td>{money(l.limit)}</td>
                  <td>{money(l.used)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
