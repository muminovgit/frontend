import type { Currency } from '../lib/format';

interface Props {
  value: Currency;
  onChange: (c: Currency) => void;
}

export function CurrencyToggle({ value, onChange }: Props) {
  return (
    <div className="seg" role="group" aria-label="Valyuta">
      {(['UZS', 'USD'] as Currency[]).map((c) => (
        <button key={c} className={value === c ? 'active' : ''} onClick={() => onChange(c)} aria-pressed={value === c}>
          {c}
        </button>
      ))}
    </div>
  );
}
