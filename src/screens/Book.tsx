import { useState } from 'react';
import { useStore } from '../store';
import { uid } from '../utils';

const OPTIONS = [
  { id: 'hard', label: 'Qattiq muqova', detail: '24 sahifa · 20×20 sm', price: 189000 },
  { id: 'soft', label: 'Yumshoq muqova', detail: '24 sahifa · 20×20 sm', price: 129000 },
];

export function Book() {
  const { state, update } = useStore();
  const [option, setOption] = useState(OPTIONS[0].id);
  const [done, setDone] = useState(false);
  const child = state.child!;
  const selected = OPTIONS.find((o) => o.id === option)!;
  const photoCount = state.memories.filter((m) => m.hasMedia && m.kind === 'photo' && !m.locked).length;

  const order = () => {
    update((s) => ({
      ...s,
      orders: [...s.orders, { id: uid(), createdAt: new Date().toISOString(), option: selected.label, price: selected.price }],
    }));
    setDone(true);
  };

  return (
    <div className="screen">
      <h2>Xotira kitobi</h2>
      <p className="muted">{child.name} uchun chop etilgan kitob.</p>

      <div className="card">
        <div className="row" style={{ alignItems: 'flex-end', justifyContent: 'center', gap: 10, height: 180 }} aria-hidden="true">
          <div style={{ width: 90, height: 140, borderRadius: 10, background: 'var(--lavender)', border: '1px solid var(--border)' }} />
          <div style={{ width: 104, height: 170, borderRadius: 10, background: 'var(--peach)', border: '1px solid var(--border)' }} />
          <div style={{ width: 90, height: 140, borderRadius: 10, background: 'var(--sky)', border: '1px solid var(--border)' }} />
        </div>
        <p className="muted small" style={{ textAlign: 'center', marginTop: 10 }}>
          Kitobga {photoCount} ta foto kiradi (qulflanganlar kirmaydi).
        </p>
      </div>

      <div className="card stack" style={{ gap: 4 }}>
        {OPTIONS.map((o) => (
          <button
            key={o.id}
            onClick={() => setOption(o.id)}
            className="row between"
            style={{ background: 'none', border: 0, borderBottom: '1px solid var(--border)', padding: '12px 0', textAlign: 'left' }}
            aria-pressed={option === o.id}
          >
            <span>
              <b>{o.label}</b>
              <span className="muted small" style={{ display: 'block' }}>{o.detail}</span>
            </span>
            <span className="row" style={{ gap: 8 }}>
              <b className="tabular">{o.price.toLocaleString('uz-UZ')} so'm</b>
              <span className="pill" style={{ background: option === o.id ? 'var(--brand)' : 'var(--border)', color: option === o.id ? '#fff' : 'var(--fg)' }}>{option === o.id ? 'Tanlandi' : 'Tanlash'}</span>
            </span>
          </button>
        ))}
      </div>

      <div className="card row between">
        <div>
          <p className="muted small">Jami</p>
          <b className="tabular" style={{ fontSize: 20 }}>{selected.price.toLocaleString('uz-UZ')} so'm</b>
        </div>
        <button className="btn small-btn" onClick={order} disabled={done || photoCount === 0}>
          {done ? 'Buyurtma qabul qilindi' : 'Buyurtma berish'}
        </button>
      </div>

      {photoCount === 0 && <p className="note">Buyurtma uchun kamida bitta ochiq foto kerak.</p>}
      {done && <p className="note">Buyurtma shu qurilmada saqlandi. To'lov va yetkazish keyingi bosqichda ulanadi.</p>}
      <p className="note">Narxlar namuna. Haqiqiy narx buyurtma paytida hisoblanadi.</p>
    </div>
  );
}
