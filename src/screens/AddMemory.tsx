import { useEffect, useRef, useState } from 'react';
import { useStore } from '../store';
import { putMedia } from '../storage';
import { TypeIcon, type IconName } from '../components/TypeIcons';
import { todayIso, uid } from '../utils';
import type { MemoryKind } from '../types';

interface TypeDef {
  id: string;
  label: string;
  icon: IconName;
  /** Ikonka fonining rangi (ilova palitrasidan) */
  tint: string;
  milestone?: boolean;
  kind?: MemoryKind;
  tag?: string;
}

const TYPES: TypeDef[] = [
  { id: 'step', label: 'Birinchi qadam', icon: 'step', tint: '#FFE38A', milestone: true },
  { id: 'word', label: "Birinchi so'z", icon: 'word', tint: '#DDF6FD', milestone: true },
  { id: 'funny', label: 'Qiziqarli onlar', icon: 'funny', tint: '#FFD6DF', kind: 'note', tag: 'Qiziqarli onlar' },
  { id: 'important', label: 'Muhim kun', icon: 'important', tint: '#ECE6FA', kind: 'note', tag: 'Muhim kun' },
  { id: 'photo', label: 'Foto', icon: 'photo', tint: '#D6F5F1', kind: 'photo' },
  { id: 'video', label: 'Video', icon: 'video', tint: '#DDF6FD', kind: 'video' },
  { id: 'audio', label: 'Ovoz', icon: 'audio', tint: '#ECE6FA', kind: 'audio' },
  { id: 'note', label: 'Matn', icon: 'note', tint: '#FFF6DA', kind: 'note' },
];

const ACCEPT: Record<string, string> = { photo: 'image/*', video: 'video/*', audio: 'audio/*' };

function pickMime(): string | undefined {
  if (typeof MediaRecorder === 'undefined' || !MediaRecorder.isTypeSupported) return undefined;
  return ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'].find((m) => MediaRecorder.isTypeSupported(m));
}

/** Ilovaning ichida ovoz yozish. Mikrofon ruxsati kerak (https yoki localhost). */
function VoiceRecorder({ onRecorded }: { onRecorded: (blob: Blob | null) => void }) {
  const [status, setStatus] = useState<'idle' | 'recording' | 'done'>('idle');
  const [seconds, setSeconds] = useState(0);
  const [url, setUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | undefined>(undefined);

  const cleanupStream = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    window.clearInterval(timerRef.current);
  };

  useEffect(() => () => {
    cleanupStream();
    if (url) URL.revokeObjectURL(url);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const start = async () => {
    setError(null);
    if (!navigator.mediaDevices?.getUserMedia) {
      setError("Bu brauzerda ovoz yozish qo'llab-quvvatlanmaydi. Faylni tanlang.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mime = pickMime();
      const rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
      chunksRef.current = [];
      rec.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      rec.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: rec.mimeType || mime || 'audio/webm' });
        cleanupStream();
        if (url) URL.revokeObjectURL(url);
        setUrl(URL.createObjectURL(blob));
        setStatus('done');
        onRecorded(blob);
      };
      recorderRef.current = rec;
      rec.start();
      setSeconds(0);
      setStatus('recording');
      timerRef.current = window.setInterval(() => setSeconds((s) => s + 1), 1000);
    } catch {
      setError("Mikrofonga ruxsat berilmadi. Brauzer sozlamalaridan ruxsat bering yoki faylni tanlang.");
    }
  };

  const stop = () => {
    recorderRef.current?.stop();
  };

  const redo = () => {
    if (url) URL.revokeObjectURL(url);
    setUrl(null);
    setStatus('idle');
    onRecorded(null);
  };

  const fmt = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;

  return (
    <div className="stack" style={{ gap: 10, alignItems: 'center' }}>
      {status === 'idle' && (
        <>
          <button className="rec-btn" onClick={start} aria-label="Ovoz yozishni boshlash">●</button>
          <p className="muted small">Yozishni boshlash uchun bosing</p>
        </>
      )}
      {status === 'recording' && (
        <>
          <button className="rec-btn on" onClick={stop} aria-label="Yozishni to'xtatish">■</button>
          <p style={{ fontWeight: 800 }} className="tabular">Yozilmoqda · {fmt(seconds)}</p>
        </>
      )}
      {status === 'done' && (
        <div className="stack" style={{ gap: 8, width: '100%' }}>
          {url && <audio controls src={url} style={{ width: '100%' }} />}
          <div className="row" style={{ justifyContent: 'center' }}>
            <button className="chip" onClick={redo}>Qayta yozish</button>
          </div>
        </div>
      )}
      {error && <p className="small" style={{ color: 'var(--accent)', textAlign: 'center' }}>{error}</p>}
    </div>
  );
}

export function AddMemory({ onDone }: { onDone: () => void }) {
  const { update, state } = useStore();
  const child = state.child!;
  const [selected, setSelected] = useState<string>('photo');
  const [date, setDate] = useState(todayIso());
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [recorded, setRecorded] = useState<Blob | null>(null);
  const [locked, setLocked] = useState(false);
  const [saving, setSaving] = useState(false);
  const [resetKey, setResetKey] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  const type = TYPES.find((t) => t.id === selected)!;
  const isMilestone = Boolean(type.milestone);
  const needsMedia = !isMilestone && type.kind !== 'note';
  const media: Blob | null = file ?? recorded;
  const canSave = !saving && (isMilestone ? true : needsMedia ? media !== null : text.trim().length > 0);

  const choose = (id: string) => {
    setSelected(id);
    setFile(null);
    setRecorded(null);
    setResetKey((k) => k + 1);
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
      if (media) await putMedia(id, media);
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
            hasMedia: media !== null,
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
            <span className="type-ico" style={{ background: t.tint }}><TypeIcon name={t.icon} /></span>
            <span className="type-label">{t.label}</span>
          </button>
        ))}
      </div>

      <div className="card stack" style={{ gap: 14 }}>
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <span className="label">{type.label}</span>
          {needsMedia && (
            <div className="attach-row" aria-label="Biriktirish">
              {(['photo', 'video', 'audio'] as const).map((k) => {
                const t = TYPES.find((x) => x.id === k)!;
                return (
                  <button key={k} className={`attach${selected === k ? ' on' : ''}`} aria-label={t.label} onClick={() => choose(k)}>
                    <TypeIcon name={t.icon} size={18} />
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {selected === 'audio' && (
          <VoiceRecorder key={resetKey} onRecorded={(b) => { setRecorded(b); setFile(null); }} />
        )}

        {needsMedia && (
          <label className="btn ghost" style={{ cursor: 'pointer' }}>
            {file ? `Tanlandi: ${file.name}` : selected === 'audio' ? "Fayldan tanlash" : `${type.label} tanlash`}
            <input
              ref={fileRef}
              type="file"
              accept={ACCEPT[type.id]}
              hidden
              onChange={(e) => {
                setFile(e.target.files?.[0] ?? null);
                setRecorded(null);
              }}
            />
          </label>
        )}

        <label className="field">
          <span>{isMilestone ? 'Izoh (masalan, "dada")' : needsMedia ? 'Izoh (ixtiyoriy)' : 'Matn'}</span>
          <textarea
            className="input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={isMilestone ? type.label : "Bugun nima bo'ldi?"}
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
      <p className="note">Foto, video va ovozlar shu qurilmada saqlanadi. Oila bilan ulashish keyingi bosqichda.</p>
    </div>
  );
}
