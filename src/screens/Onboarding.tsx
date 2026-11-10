import { useState } from 'react';
import { useStore } from '../store';
import { useT } from '../useT';
import { LangSwitch } from '../components/LangSwitch';
import { todayIso, uid } from '../utils';

export function Onboarding() {
  const { update } = useStore();
  const t = useT();
  const [step, setStep] = useState(0);
  const [name, setName] = useState('');
  const [birthDate, setBirthDate] = useState('');

  const canFinish = name.trim().length > 0 && birthDate !== '' && birthDate <= todayIso();

  const finish = () => {
    if (!canFinish) return;
    update((s) => ({ ...s, child: { id: uid(), name: name.trim(), birthDate } }));
  };

  if (step === 0) {
    return (
      <div className="screen" style={{ paddingTop: 36 }}>
        <LangSwitch />
        <div className="dots"><span className="on" /><span /><span /></div>
        <div className="onboard-hero" aria-hidden="true">
          <div className="float a"><div className="label">{t('onboard.card1_t')}</div><p style={{ marginTop: 6 }}>{t('onboard.card1_s')}</p></div>
          <div className="float b"><div className="label">{t('onboard.card2_t')}</div><p style={{ marginTop: 6 }}>{t('onboard.card2_s')}</p></div>
          <div className="float c"><div className="row"><div className="avatar sm">✦</div><div><div>{t('onboard.card3_t')}</div><div className="muted small">{t('onboard.card3_s')}</div></div></div></div>
        </div>
        <h1>
          {(() => {
            const [before, after = ''] = t('onboard.h1', { hl: '\u0000' }).split('\u0000');
            return <>{before}<span className="hl">{t('onboard.hl')}</span>{after}</>;
          })()}
        </h1>
        <p className="muted">{t('onboard.p1')}</p>
        <div style={{ marginTop: 16 }} className="stack">
          <button className="btn" onClick={() => setStep(1)}>{t('common.continue')}</button>
        </div>
      </div>
    );
  }

  return (
    <div className="screen" style={{ paddingTop: 36 }}>
      <LangSwitch />
      <div className="dots"><span /><span className="on" /><span /></div>
      <h1>{t('onboard.h2')}</h1>
      <p className="muted">{t('onboard.p2')}</p>

      <div className="card stack" style={{ gap: 16 }}>
        <label className="field">
          <span>{t('onboard.name')}</span>
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder={t('onboard.name_ph')} maxLength={40} autoComplete="off" />
        </label>
        <label className="field">
          <span>{t('onboard.birth')}</span>
          <input className="input" type="date" value={birthDate} max={todayIso()} onChange={(e) => setBirthDate(e.target.value)} />
        </label>
      </div>

      <div className="stack" style={{ marginTop: 8 }}>
        <button className="btn" onClick={finish} disabled={!canFinish}>{t('onboard.start')}</button>
        <button className="btn ghost" onClick={() => setStep(0)}>{t('common.back')}</button>
      </div>
    </div>
  );
}
