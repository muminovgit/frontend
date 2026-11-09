import { useStore } from '../store';
import { MemoryMedia } from '../components/MemoryMedia';
import { ageText, formatDay, isLockedNow, unlockDate, formatDate } from '../utils';
import type { Memory } from '../types';

const KIND_LABEL: Record<Memory['kind'], string> = {
  photo: 'Foto',
  video: 'Video',
  audio: 'Ovoz',
  note: 'Matn',
};

export function Timeline() {
  const { state, update } = useStore();
  const child = state.child!;

  const memories = [...state.memories].sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : b.createdAt.localeCompare(a.createdAt)));

  const grouped = new Map<string, Memory[]>();
  for (const m of memories) {
    const list = grouped.get(m.date) ?? [];
    list.push(m);
    grouped.set(m.date, list);
  }

  const remove = (id: string) => {
    if (!window.confirm("Bu xotirani o'chirasizmi?")) return;
    update((s) => ({ ...s, memories: s.memories.filter((m) => m.id !== id) }));
  };

  return (
    <div className="screen">
      <div className="hero">
        <div className="row">
          <div className="avatar">{child.name.charAt(0).toUpperCase()}</div>
          <div className="grow">
            <h2>{child.name}</h2>
            <p className="muted">{ageText(child.birthDate)} · {state.memories.length} ta xotira</p>
          </div>
        </div>
        <button className="btn small-btn" style={{ marginTop: 12 }} onClick={() => { window.location.hash = '#/child3d'; }}>3D bola va ovozlar ›</button>
      </div>

      {memories.length === 0 && (
        <div className="card empty">
          <h3>Birinchi xotirani qo'shing</h3>
          <p className="muted small" style={{ marginTop: 6 }}>Foto, video, ovoz yoki qisqa matn. Pastdagi "+" tugmasini bosing.</p>
        </div>
      )}

      {[...grouped.entries()].map(([date, list]) => (
        <section key={date} className="stack" style={{ gap: 12 }}>
          <div className="day">{formatDay(date)}</div>
          {list.map((m) => {
            const locked = isLockedNow(child, m.locked);
            return (
              <article key={m.id} className="card stack" style={{ gap: 12 }}>
                {locked ? (
                  <div className="lock">
                    <span className="pill accent">18 yoshda ochiladi</span>
                    <p style={{ marginTop: 10, fontWeight: 700 }}>Bu xotira {formatDate(unlockDate(child))} kuni ochiladi.</p>
                  </div>
                ) : (
                  <>
                    <MemoryMedia memory={m} />
                    {m.text && <p>{m.text}</p>}
                  </>
                )}
                <div className="row wrap between">
                  <div className="row wrap">
                    <span className="pill">{KIND_LABEL[m.kind]}</span>
                    {m.locked && <span className="pill lav">Qulflangan</span>}
                  </div>
                  <button className="btn ghost small-btn" onClick={() => remove(m.id)} aria-label="Xotirani o'chirish">O'chirish</button>
                </div>
              </article>
            );
          })}
        </section>
      ))}
    </div>
  );
}
