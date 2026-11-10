import { useRef, useState } from 'react';
import { useStore } from '../store';
import { putMedia } from '../storage';
import { TypeIcon, type IconName } from '../components/TypeIcons';
import { todayIso, uid } from '../utils';
import type { MemoryKind } from '../types';

interface TypeDef {
  id: string;
  label: string;
  icon: IconName;
  /** milestone bo'lsa — "O'sish"ga emas, lentaga milestone sifatida tushadi */
  milestone?: boolean;
  /** xotira turi (foto, video, ovoz yoki matn) */
  kind?: MemoryKind;
  /** ko'rinadigan yorliq */
  tag?: string;
}

const TYPES: TypeDef[] = [
  { id: 'step', label: 'Birinchi qadam', icon: 'step', milestone: true },
  { id: 'word', label: 'Birinchi so\'z', icon: 'word', milestone: true },
  { id: 'funny', label: 'Komik an', icon: 'funny', kind: 'note', tag: 'Komik an' },
  { id: 'important', label: 'Muhim kun', icon: 'important', kind: 'note', tag: 'Muhim kun' },
  { id: 'photo', label: 'Foto', icon: 'photo', kind: 'photo' },
  { id: 'video', label: 'Video', icon: 'video', kind: 'video' },
  { id: 'audio', label: 'Ovoz', icon: 'audio', kind: 'audio' },
  { id: 'note', label: 'Matn', icon: 'note', kind: 'note' },
];

const ACCEPT: Record<string, string> = { photo: 'image/*', video: 'video/*', audio: 'audio/*' };

export function AddMemory({ onDone }: { onDone: () => void }) {
  const { update, state } = useStore();
  const child = state.child!;
  const [selected, setSelected] = useState<string>('photo');
  const [date, setDate] = useState(todayIso());
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [locked, setLocked] = useState(false);
  const [saving, setSaving] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const type = TYPES.find((t) => t.id === selected)!;
  const isMilestone = Boolean(type.milestone);
  const needsFile = !isMilestone && type.kind !== 'note';
  const canSave = !saving && (isMilestone ? true : needsFile ? file !== null : text.trim().length > 0);

  const choose = (id: string) => {
    setSelected(id);
    setFile(null);
    if (fileRef.current) fileRef.current.value = '';
  };

  const save = async () => {
    if (!canSave) return;
    setSaving(true);
    const id = uid();
    if (isMilestone) {
      update((s) => ({
        ...s,
        milestones: [...s.milestones, { id, childId: child.id, date, title: text.trim() || type.label }],
      }));
    } else {
      if (file) await putMedia(id, file);
      update((s) => ({
        ...s,
        memories: [
          ...s.memories,
          {
            id,
            childId: s.child!.id,
            date,
            kind: type.kind!,
            text: text.trim(),
            hasMedia: file !== null,
            locked,
            tag: type.tag,
            createdAt: new Date().toISOString(),
          },
        ],
      }));
    }
    setSaving(false);
    onDone();
  };

  return (
    <div className="screen">
      <h2>Bugun nima bo'ldi?</h2>

      <div className="type-grid" role="group" aria-label="Qo'shish turi">
        {TYPES.map((t) => (
          <button
            key={t.id}
            className={`type-tile${selected === t.id ? ' on' : ''}`}
            aria-pressed={selected === t.id}
            onClick={() => choose(t.id)}
          >
            <span className="type-ico"><TypeIcon name={t.icon} /></span>
            <span className="type-label">{t.label}</span>
          </button>
        ))}
      </div>

      <div className="card stack" style={{ gap: 14 }}>
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <span className="label">{type.label}</span>
          {!isMilestone && type.kind !== 'note' && (
            <div className="attach-row" aria-label="Biriktirish">
              {(['photo', 'video', 'audio'] as const).map((k) => (
                <button
                  key={k}
                  className={`attach${selected === k ? ' on' : ''}`}
                  aria-label={TYPES.find((t) => t.id === k)!.label}
                  onClick={() => choose(k)}
                >
                  <TypeIcon name={TYPES.find((t) => t.id === k)!.icon} size={18} />
                </button>
              ))}
            </div>
          )}
        </div>

        {needsFile && (
          <label className="btn ghost" style={{ cursor: 'pointer' }}>
            {file ? `Tanlandi: ${file.name}` : `${type.label} tanlash`}
            <input
              ref={fileRef}
              type="file"
              accept={ACCEPT[type.id]}
              hidden
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
        )}

        <label className="field">
          <span>{isMilestone ? "Izoh (masalan, \"dada\")" : needsFile ? 'Izoh (ixtiyoriy)' : 'Matn'}</span>
          <textarea
            className="input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={isMilestone ? type.label : 'Bugun nima bo\'ldi?'}
            maxLength={1000}
          />
        </label>

        <label className="field">
          <span>Sana</span>
          <input className="input" type="date" value={date} max={todayIso()} onChange={(e) => setDate(e.target.value)} />
        </label>

        {!isMilestone && (
          <label className="switch">
            <span>
              <b>18 yoshgacha qulflash</b>
              <span className="muted small" style={{ display: 'block' }}>Bu xotira bola 18 yoshga to'lguncha ko'rinmaydi.</span>
            </span>
            <input type="checkbox" checked={locked} onChange={(e) => setLocked(e.target.checked)} />
          </label>
        )}
      </div>

      <button className="btn" onClick={save} disabled={!canSave}>{saving ? 'Saqlanmoqda…' : 'Saqlash'}</button>
      <p className="note">Foto va videolar shu qurilmada saqlanadi. Oila bilan ulashish keyingi bosqichda.</p>
    </div>
  );
}
