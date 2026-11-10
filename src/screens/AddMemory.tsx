import { useEffect, useRef, useState } from 'react';
import { useStore } from '../store';
import { useT } from '../useT';
import { putMedia } from '../storage';
import { TypeIcon, type IconName } from '../components/TypeIcons';
import { schoolDate, todayIso, uid, unlockDate } from '../utils';
import type { MemoryKind } from '../types';

interface TypeDef {
  id: string;
  icon: IconName;
  tint: string;
  milestone?: boolean;
  kind?: MemoryKind;
  tag?: string; // ko'rinadigan yorliq (tilga bog'liq bo'lmagan qiymat)
}

const TYPES: TypeDef[] = [
  { id: 'step', icon: 'step', tint: '#FFE38A', milestone: true },
  { id: 'word', icon: 'word', tint: '#DDF6FD', milestone: true },
  { id: 'funny', icon: 'funny', tint: '#FFD6DF', kind: 'note', tag: 'funny' },
  { id: 'important', icon: 'important', tint: '#ECE6FA', kind: 'note', tag: 'important' },
  { id: 'photo', icon: 'photo', tint: '#D6F5F1', kind: 'photo' },
  { id: 'video', icon: 'video', tint: '#DDF6FD', kind: 'video' },
  { id: 'audio', icon: 'audio', tint: '#ECE6FA', kind: 'audio' },
  { id: 'note', icon: 'note', tint: '#FFF6DA', kind: 'note' },
];

const ACCEPT: Record<string, string> = { photo: 'image/*', video: 'video/*', audio: 'audio/*' };

type Capsule = 'open' | '18' | 'school' | 'custom';

function pickMime(): string | undefined {
  if (typeof MediaRecorder === 'undefined' || !MediaRecorder.isTypeSupported) return undefined;
  return ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'].find((m) => MediaRecorder.isTypeSupported(m));
}

/** Ilovaning ichida ovoz yozish. Mikrofon ruxsati kerak (https yoki localhost). */
function VoiceRecorder({ onRecorded }: { onRecorded: (blob: Blob | null) => void }) {
  const t = useT();
  const [status, setStatus] = useState<'idle' | 'recording' | 'done'>('idle');
  const [seconds, setSeconds] = useState(0);
  const [url, setUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | undefined>(undefined);

  const cleanupStream = () => {
    streamRef.current?.getTracks().forEach((tr) => tr.stop());
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
      setError(t('add.no_rec'));
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
      setError(t('add.mic_denied'));
    }
  };

  const stop = () => recorderRef.current?.stop();

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
          <button className="rec-btn" onClick={start} aria-label={t('add.record_start')}>●</button>
          <p className="muted small">{t('add.record_hint')}</p>
        </>
      )}
      {status === 'recording' && (
        <>
          <button className="rec-btn on" onClick={stop} aria-label={t('add.stop')}>■</button>
          <p style={{ fontWeight: 800 }} className="tabular">{t('add.recording', { t: fmt(seconds) })}</p>
        </>
      )}
      {status === 'done' && (
        <div className="stack" style={{ gap: 8, width: '100%' }}>
          {url && <audio controls src={url} style={{ width: '100%' }} />}
          <div className="row" style={{ justifyContent: 'center' }}>
            <button className="chip" onClick={redo}>{t('add.redo')}</button>
          </div>
        </div>
      )}
      {error && <p className="small" style={{ color: 'var(--accent)', textAlign: 'center' }}>{error}</p>}
    </div>
  );
}

export function AddMemory({ onDone }: { onDone: () => void }) {
  const { update, state } = useStore();
  const t = useT();
  const child = state.child!;
  const [selected, setSelected] = useState<string>('photo');
  const [date, setDate] = useState(todayIso());
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [recorded, setRecorded] = useState<Blob | null>(null);
  const [capsule, setCapsule] = useState<Capsule>('open');
  const [customDate, setCustomDate] = useState('');
  const [saving, setSaving] = useState(false);
  const [resetKey, setResetKey] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  const type = TYPES.find((x) => x.id === selected)!;
  const isMilestone = Boolean(type.milestone);
  const needsMedia = !isMilestone && type.kind !== 'note';
  const media: Blob | null = file ?? recorded;
  const unlockAt: string | undefined =
    capsule === 'open' ? undefined
    : capsule === '18' ? unlockDate(child)
    : capsule === 'school' ? schoolDate(child)
    : customDate || undefined;
  const capsuleValid = capsule !== 'custom' || (customDate !== '' && customDate > todayIso());
  const canSave =
    !saving && capsuleValid &&
    (isMilestone ? true : needsMedia ? media !== null : text.trim().length > 0);

  const typeLabel = (id: string) => t(`add.type.${id}`);

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
        milestones: [...s.milestones, { id, childId: child.id, date, title: text.trim() || typeLabel(type.id) }],
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
            locked: false,
            unlockAt,
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
      <h2>{t('add.title')}</h2>

      <div className="type-grid" role="group" aria-label={t('add.title')}>
        {TYPES.map((x) => (
          <button key={x.id} className={`type-tile${selected === x.id ? ' on' : ''}`} aria-pressed={selected === x.id} onClick={() => choose(x.id)}>
            <span className="type-ico" style={{ background: x.tint }}><TypeIcon name={x.icon} /></span>
            <span className="type-label">{typeLabel(x.id)}</span>
          </button>
        ))}
      </div>

      <div className="card stack" style={{ gap: 14 }}>
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <span className="label">{typeLabel(type.id)}</span>
          {needsMedia && (
            <div className="attach-row">
              {(['photo', 'video', 'audio'] as const).map((k) => {
                const x = TYPES.find((y) => y.id === k)!;
                return (
                  <button key={k} className={`attach${selected === k ? ' on' : ''}`} aria-label={typeLabel(k)} onClick={() => choose(k)}>
                    <TypeIcon name={x.icon} size={18} />
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
            {file ? t('add.file_chosen', { name: file.name }) : selected === 'audio' ? t('add.pick_file') : t('add.pick', { type: typeLabel(type.id) })}
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
          <span>{isMilestone ? t('add.izoh_milestone') : needsMedia ? t('add.izoh_media') : t('add.text')}</span>
          <textarea
            className="input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={isMilestone ? typeLabel(type.id) : t('add.text_ph')}
            maxLength={1000}
          />
        </label>

        <label className="field">
          <span>{t('add.date')}</span>
          <input className="input" type="date" value={date} max={todayIso()} onChange={(e) => setDate(e.target.value)} />
        </label>

        {!isMilestone && (
          <div className="stack" style={{ gap: 10 }}>
            <div>
              <b>{t('add.capsule')}</b>
              <p className="muted small">{t('add.capsule_hint')}</p>
            </div>
            <div className="row wrap" role="group" aria-label={t('add.capsule')}>
              {([
                ['open', 'add.capsule_open'],
                ['18', 'add.capsule_18'],
                ['school', 'add.capsule_school'],
                ['custom', 'add.capsule_custom'],
              ] as [Capsule, string][]).map(([id, key]) => (
                <button key={id} className="chip" aria-pressed={capsule === id} onClick={() => setCapsule(id)}>{t(key)}</button>
              ))}
            </div>
            {capsule === 'custom' && (
              <input className="input" type="date" value={customDate} min={todayIso()} onChange={(e) => setCustomDate(e.target.value)} aria-label={t('add.capsule_custom')} />
            )}
          </div>
        )}
      </div>

      <button className="btn" onClick={save} disabled={!canSave}>{saving ? t('common.saving') : t('common.save')}</button>
      <p className="note">{t('add.footer')}</p>
    </div>
  );
}
