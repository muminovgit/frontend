import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

interface Props {
  label: string;
  value: ReactNode;
  icon?: LucideIcon;
  hint?: ReactNode;
  tone?: 'default' | 'danger' | 'success';
}

export function StatCard({ label, value, icon: Icon, hint, tone = 'default' }: Props) {
  return (
    <div className={`stat-card tone-${tone}`}>
      <div className="stat-head">
        <span>{label}</span>
        {Icon && <Icon size={16} aria-hidden />}
      </div>
      <div className="stat-value">{value}</div>
      {hint && <div className="stat-hint">{hint}</div>}
    </div>
  );
}
