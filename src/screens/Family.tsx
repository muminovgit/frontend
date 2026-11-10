import { useState } from 'react';
import { useStore } from '../store';
import { useT } from '../useT';
import { LangSwitch } from '../components/LangSwitch';
import { uid } from '../utils';
import type { MemberAccess, MemberRole } from '../types';

const ROLES: MemberRole[] = ['Ota', 'Ona', 'Buvi', 'Bobo', 'Boshqa'];
const ACCESS: MemberAccess[] = ['tahrirlay oladi', "ko'ra oladi"];

export function Family() {
  const { state, update } = useStore();
  const t = useT();
  const [name, setName] = useState('');
  const [role, setRole] = useState<MemberRole>('Ota');
  const [access, setAccess] = useState<MemberAccess>('tahrirlay oladi');
  const [inviteLink, setInviteLink] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const add = () => {
    if (name.trim() === '') return;
    update((s) => ({ ...s, members: [...s.members, { id: uid(), name: name.trim(), role, access }] }));
    setName('');
  };

  const remove = (id: string) => {
    update((s) => ({ ...s, members: s.members.filter((m) => m.id !== id) }));
  };

  const makeInvite = () => {
    const code = uid();
    setInviteLink(`${window.location.origin}${window.location.pathname}#/family?invite=${code}`);
    setCopied(false);
  };

  const copy = async () => {
    if (!inviteLink) return;
    try {
      await navigator.clipboard.writeText(inviteLink);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  };

  const accessLabel = (a: MemberAccess) => (a === 'tahrirlay oladi' ? t('family.edit') : t('family.view'));

  return (
    <div className="screen">
      <LangSwitch />
      <h2>{t('family.title')}</h2>
      <p className="muted">{t('family.sub')}</p>

      <div className="stack">
        {state.members.length === 0 && <div className="card"><p className="muted small">{t('family.none')}</p></div>}
        {state.members.map((m) => (
          <div key={m.id} className="card member">
            <div className="avatar sm">{m.name.charAt(0).toUpperCase()}</div>
            <div className="who">
              <h3>{m.name}</h3>
              <p className="muted small">{t(`family.role.${m.role}`)}</p>
            </div>
            <span className="pill lav">{accessLabel(m.access)}</span>
            <button className="btn ghost small-btn" onClick={() => remove(m.id)} aria-label={t('family.remove', { name: m.name })}>×</button>
          </div>
        ))}
      </div>

      <div className="card stack" style={{ gap: 14 }}>
        <h3>{t('family.add_t')}</h3>
        <label className="field">
          <span>{t('family.name')}</span>
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder={t('family.name_ph')} maxLength={40} />
        </label>
        <div className="row wrap" role="group" aria-label={t('family.relation')}>
          {ROLES.map((r) => (
            <button key={r} className="chip" aria-pressed={role === r} onClick={() => setRole(r)}>{t(`family.role.${r}`)}</button>
          ))}
        </div>
        <div className="row wrap" role="group" aria-label={t('family.rights')}>
          {ACCESS.map((a) => (
            <button key={a} className="chip" aria-pressed={access === a} onClick={() => setAccess(a)}>{accessLabel(a)}</button>
          ))}
        </div>
        <button className="btn" onClick={add} disabled={name.trim() === ''}>{t('common.add')}</button>
      </div>

      <div className="card stack" style={{ gap: 12 }}>
        <h3>{t('family.invite_t')}</h3>
        <p className="muted small">{t('family.invite_s')}</p>
        <button className="btn ghost" onClick={makeInvite}>{t('family.make')}</button>
        {inviteLink && (
          <>
            <p className="small" style={{ wordBreak: 'break-all', background: 'var(--lavender)', padding: 10, borderRadius: 12 }}>{inviteLink}</p>
            <button className="btn" onClick={copy}>{copied ? t('common.copied') : t('common.copy')}</button>
          </>
        )}
      </div>
    </div>
  );
}
