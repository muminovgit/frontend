import { useRef, useState } from 'react';
import { useStore } from '../store';
import { putMedia } from '../storage';
import { todayIso, uid } from '../utils';
import type { MemoryKind } from '../types';

const KINDS: { id: MemoryKind; label: string; accept?: string }[] = [
  { id: 'photo', label: 'Foto', accept: 'image/*' },
  { id: 'video', label: 'Video', accept: 'video/*' },
  { id: 'audio', label: 'Ovoz', accept: 'audio/*' },
  { id: 'note', label: 'Matn' },
];

export function AddMemory({ onDone }: { onDone: () => void }) {
  const { update } = useStore();
  const [kind, setKind] = useState<MemoryKind>('photo');
  const [date, setDate] = useState(todayIso());
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [locked, setLocked] = useState(false);
  const [saving, setSaving] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const current = KINDS.find((k) => k.id === kind)!;
  const needsFile = kind !== 'note';
  const canSave = !saving && (needsFile ? file !== null : text.trim().length > 0);

  const chooseKind = (k: MemoryKind) => {
    setKind(k);
    setFile(null);
    if (fileRef.current) fileRef.current.value = '';
  };

  const save = async () => {
    if (!canSave) return;
    setSaving(true);
    const id = uid();
    if (file) await putMedia(id, file);
    update((s) => ({
      ...s,
      memories: [
        ...s.memories,
        {
          id,
          childId: s.child!.id,
          date,
          kind,
          text: text.trim(),
          hasMedia: file !== null,
          locked,
          createdAt: new Date().toISOString(),
        },
      ],
    }));
    setSaving(false);
    onDone();
  };

  return (
    <div className="screen">
      <h2>Yangi xotira</h2>

      <div className="row wrap" role="group" aria-label="Turi">
        {KINDS.map((k) => (
          <button key={k.id} className="chip" aria-pressed={kind === k.id} onClick={() => chooseKind(k.id)}>
            {k.label}
          </button>
        ))}
      </div>

      <div className="card stack" style={{ gap: 14 }}>
        {needsFile && (
          <label className="btn ghost" style={{ cursor: 'pointer' }}>
            {file ? `Tanlandi: ${file.name}` : `${current.label} tanlash`}
            <input
              ref={fileRef}
              type="file"
              accept={current.accept}
              hidden
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
        )}

        <label className="field">
          <span>{needsFile ? 'Izoh (ixtiyoriy)' : 'Matn'}</span>
          <textarea
            className="input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Bugun nima bo'ldi?"
            maxLength={1000}
          />
        </label>

        <label className="field">
          <span>Sana</span>
          <input className="input" type="date" value={date} max={todayIso()} onChange={(e) => setDate(e.target.value)} />
        </label>

        <label className="switch">
          <span>
            <b>18 yoshgacha qulflash</b>
            <span className="muted small" style={{ display: 'block' }}>Bu xotira bola 18 yoshga to'lguncha ko'rinmaydi.</span>
          </span>
          <input type="checkbox" checked={locked} onChange={(e) => setLocked(e.target.checked)} />
        </label>
      </div>

      <button className="btn" onClick={save} disabled={!canSave}>{saving ? 'Saqlanmoqda…' : 'Saqlash'}</button>
      <p className="note">Foto va videolar shu qurilmada saqlanadi. Oila bilan ulashish keyingi bosqichda.</p>
    </div>
  );
}
