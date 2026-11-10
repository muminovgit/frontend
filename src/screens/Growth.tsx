import { useState } from 'react';
import { useStore } from '../store';
import { useLang, useT } from '../useT';
import { HeightRuler, LineChart, type HeightMark } from '../components/Giraffe';
import { formatDate, todayIso, uid } from '../utils';

export function Growth() {
  const { state, update } = useStore();
  const t = useT();
  const lang = useLang();
  const child = state.child!;
  const [date, setDate] = useState(todayIso());
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [milestone, setMilestone] = useState('');

  const measurements = state.measurements
    .filter((m) => m.childId === child.id)
    .sort((a, b) => a.date.localeCompare(b.date));
  const withHeight = measurements.filter((m) => m.heightCm !== undefined);
  const withWeight = measurements.filter((m) => m.weightKg !== undefined);
  const latestHeight = withHeight.at(-1);
  const latestWeight = withWeight.at(-1);

  const marks: HeightMark[] = withHeight.slice(-3).map((m, i, arr) => ({
    cm: m.heightCm!,
    label: `${m.heightCm} ${t('unit.cm')}`,
    current: i === arr.length - 1,
  }));

  const h = Number(height);
  const w = Number(weight);
  const canSave = (height !== '' && h >= 30 && h <= 150) || (weight !== '' && w >= 1 && w <= 80);

  const saveMeasurement = () => {
    if (!canSave) return;
    update((s) => ({
      ...s,
      measurements: [
        ...s.measurements,
        { id: uid(), childId: child.id, date, heightCm: height !== '' ? h : undefined, weightKg: weight !== '' ? w : undefined },
      ],
    }));
    setHeight('');
    setWeight('');
  };

  const addMilestone = () => {
    if (milestone.trim() === '') return;
    update((s) => ({
      ...s,
      milestones: [...s.milestones, { id: uid(), childId: child.id, date, title: milestone.trim() }],
    }));
    setMilestone('');
  };

  const milestones = state.milestones.filter((m) => m.childId === child.id).sort((a, b) => b.date.localeCompare(a.date));

  return (
    <div className="screen">
      <div className="row between">
        <h2>{t('growth.title')}</h2>
        {latestHeight && <span className="pill sky tabular">{latestHeight.heightCm} {t('unit.cm')}</span>}
      </div>

      <div className="row" style={{ gap: 12 }}>
        <div className="card grow">
          <div className="label">{t('growth.height')}</div>
          <div className="tabular" style={{ fontSize: 30, fontWeight: 800, marginTop: 4 }}>
            {latestHeight ? latestHeight.heightCm : '—'} <span style={{ fontSize: 14 }}>{t('unit.cm')}</span>
          </div>
        </div>
        <div className="card grow">
          <div className="label">{t('growth.weight')}</div>
          <div className="tabular" style={{ fontSize: 30, fontWeight: 800, marginTop: 4 }}>
            {latestWeight ? latestWeight.weightKg : '—'} <span style={{ fontSize: 14 }}>{t('unit.kg')}</span>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: 6 }}>{t('growth.ruler_title')}</h3>
        {latestHeight ? (
          <HeightRuler heightCm={latestHeight.heightCm!} marks={marks} />
        ) : (
          <p className="muted small">{t('growth.ruler_empty')}</p>
        )}
      </div>

      <div className="card stack" style={{ gap: 14 }}>
        <h3>{t('growth.new')}</h3>
        <label className="field">
          <span>{t('growth.date')}</span>
          <input className="input" type="date" value={date} max={todayIso()} onChange={(e) => setDate(e.target.value)} />
        </label>
        <div className="row" style={{ gap: 12 }}>
          <label className="field grow">
            <span>{t('growth.height_in')}</span>
            <input className="input tabular" inputMode="decimal" value={height} onChange={(e) => setHeight(e.target.value)} placeholder="86" />
          </label>
          <label className="field grow">
            <span>{t('growth.weight_in')}</span>
            <input className="input tabular" inputMode="decimal" value={weight} onChange={(e) => setWeight(e.target.value)} placeholder="12.4" />
          </label>
        </div>
        <button className="btn" onClick={saveMeasurement} disabled={!canSave}>{t('common.save')}</button>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: 6 }}>{t('growth.weight_chart')}</h3>
        <LineChart
          points={withWeight.slice(-8).map((m) => ({ label: formatDate(lang, m.date).replace(/,? \d{4}$/, '').replace(/ \d{4}$/, ''), value: m.weightKg! }))}
          unit={t('growth.weight')}
          color="var(--accent)"
        />
      </div>

      <div className="card stack" style={{ gap: 12 }}>
        <h3>{t('growth.ms_title')}</h3>
        <p className="muted small">{t('growth.ms_sub')}</p>
        <div className="row" style={{ gap: 8 }}>
          <input className="input grow" value={milestone} onChange={(e) => setMilestone(e.target.value)} placeholder={t('growth.ms_ph')} maxLength={80} />
          <button className="btn small-btn" onClick={addMilestone} disabled={milestone.trim() === ''}>{t('common.add')}</button>
        </div>
        {milestones.length === 0 && <p className="muted small">{t('growth.ms_none')}</p>}
        {milestones.map((m) => (
          <div key={m.id} className="row between" style={{ borderTop: '1px solid var(--border)', paddingTop: 10 }}>
            <div>
              <b>{m.title}</b>
              <div className="muted small">{formatDate(lang, m.date)}</div>
            </div>
            <span className="pill sage">{t('growth.achieved')}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
