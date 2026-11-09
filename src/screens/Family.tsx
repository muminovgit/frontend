import { useState } from 'react';
import { useStore } from '../store';
import { uid } from '../utils';
import type { MemberAccess, MemberRole } from '../types';

const ROLES: MemberRole[] = ['Ota', 'Ona', 'Buvi', 'Bobo', 'Boshqa'];
const ACCESS: MemberAccess[] = ['tahrirlay oladi', "ko'ra oladi"];

export function Family() {
  const { state, update } = useStore();
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
    const link = `${window.location.origin}${window.location.pathname}#/family?invite=${code}`;
    setInviteLink(link);
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

  return (
    <div className="screen">
      <h2>Oila</h2>
      <p className="muted">Kim ko'radi va kim qo'sha oladi. Xotiralar faqat taklif qilingan a'zolarga ko'rinadi.</p>

      <div className="stack">
        {state.members.length === 0 && <div className="card"><p className="muted small">Hozircha a'zo yo'q. Pastdan qo'shing.</p></div>}
        {state.members.map((m) => (
          <div key={m.id} className="card member">
            <div className="avatar sm">{m.name.charAt(0).toUpperCase()}</div>
            <div className="who">
              <h3>{m.name}</h3>
              <p className="muted small">{m.role}</p>
            </div>
            <span className="pill lav">{m.access === 'tahrirlay oladi' ? 'Tahrirlay oladi' : "Ko'ra oladi"}</span>
            <button className="btn ghost small-btn" onClick={() => remove(m.id)} aria-label={`${m.name}ni olib tashlash`}>×</button>
          </div>
        ))}
      </div>

      <div className="card stack" style={{ gap: 14 }}>
        <h3>A'zo qo'shish</h3>
        <label className="field">
          <span>Ismi</span>
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Masalan, Madina" maxLength={40} />
        </label>
        <div className="row wrap" role="group" aria-label="Qarindoshlik">
          {ROLES.map((r) => (
            <button key={r} className="chip" aria-pressed={role === r} onClick={() => setRole(r)}>{r}</button>
          ))}
        </div>
        <div className="row wrap" role="group" aria-label="Huquq">
          {ACCESS.map((a) => (
            <button key={a} className="chip" aria-pressed={access === a} onClick={() => setAccess(a)}>{a}</button>
          ))}
        </div>
        <button className="btn" onClick={add} disabled={name.trim() === ''}>Qo'shish</button>
      </div>

      <div className="card stack" style={{ gap: 12 }}>
        <h3>Taklif havolasi</h3>
        <p className="muted small">Havolani oila a'zosiga yuboring. Hozircha havola faqat shu qurilmada ishlaydi, serverga ulash keyingi bosqichda.</p>
        <button className="btn ghost" onClick={makeInvite}>Havola yaratish</button>
        {inviteLink && (
          <>
            <p className="small" style={{ wordBreak: 'break-all', background: 'var(--lavender)', padding: 10, borderRadius: 12 }}>{inviteLink}</p>
            <button className="btn" onClick={copy}>{copied ? 'Nusxalandi' : 'Nusxa olish'}</button>
          </>
        )}
      </div>
    </div>
  );
}
