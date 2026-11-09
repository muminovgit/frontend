import { useState } from 'react';
import { useStore } from '../store';
import { todayIso, uid } from '../utils';

export function Onboarding() {
  const { update } = useStore();
  const [step, setStep] = useState(0);
  const [name, setName] = useState('');
  const [birthDate, setBirthDate] = useState('');

  const canFinish = name.trim().length > 0 && birthDate !== '' && birthDate <= todayIso();

  const finish = () => {
    if (!canFinish) return;
    const id = uid();
    update((s) => ({ ...s, child: { id, name: name.trim(), birthDate } }));
  };

  if (step === 0) {
    return (
      <div className="screen" style={{ paddingTop: 36 }}>
        <div className="dots"><span className="on" /><span /><span /></div>
        <div className="onboard-hero" aria-hidden="true">
          <div className="float a"><div className="label">Birinchi qadam</div><p style={{ marginTop: 6 }}>Bog'da yurdi</p></div>
          <div className="float b"><div className="label">Ovoz</div><p style={{ marginTop: 6 }}>0:42 · buvisi yozdi</p></div>
          <div className="float c"><div className="row"><div className="avatar sm">X</div><div><div>Xotira</div><div className="muted small">Bolangiz uchun</div></div></div></div>
        </div>
        <h1>Har bir kun, <span className="hl">esda qoladigan</span> bo'lsin</h1>
        <p className="muted">Bolangizning rasmlari, ovozi va o'sishi bir joyda, oilangiz bilan birga saqlanadi.</p>
        <div style={{ marginTop: 16 }} className="stack">
          <button className="btn" onClick={() => setStep(1)}>Davom etish</button>
        </div>
      </div>
    );
  }

  return (
    <div className="screen" style={{ paddingTop: 36 }}>
      <div className="dots"><span /><span className="on" /><span /></div>
      <h1>Bola profilini yarating</h1>
      <p className="muted">Ism va tug'ilgan sana kerak. Keyin istalgan vaqtda o'zgartirish mumkin.</p>

      <div className="card stack" style={{ gap: 16 }}>
        <label className="field">
          <span>Ismi</span>
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Masalan, Oisha" maxLength={40} autoComplete="off" />
        </label>
        <label className="field">
          <span>Tug'ilgan sana</span>
          <input className="input" type="date" value={birthDate} max={todayIso()} onChange={(e) => setBirthDate(e.target.value)} />
        </label>
      </div>

      <div className="stack" style={{ marginTop: 8 }}>
        <button className="btn" onClick={finish} disabled={!canFinish}>Boshlash</button>
        <button className="btn ghost" onClick={() => setStep(0)}>Orqaga</button>
      </div>
    </div>
  );
}
