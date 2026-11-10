import { useState } from 'react';
import { useStore } from '../store';
import { MemoryMedia } from '../components/MemoryMedia';
import { deleteMedia } from '../storage';
import { ageText, formatDay, isLockedNow, unlockDate, formatDate } from '../utils';
import type { Memory } from '../types';

const KIND_LABEL: Record<Memory['kind'], string> = {
  photo: 'Foto',
  video: 'Video',
  audio: 'Ovoz',
  note: 'Matn',
};

type Entry =
  | { type: 'memory'; key: string; date: string; createdAt: string; memory: Memory }
  | { type: 'milestone'; key: string; date: string; createdAt: string; title: string };

export function Timeline() {
  const { state, update } = useStore();
  const child = state.child!;
  const [menuFor, setMenuFor] = useState<string | null>(null);

  const milestones = state.milestones.filter((m) => m.childId === child.id);

  const entries: Entry[] = [
    ...state.memories.map<Entry>((m) => ({ type: 'memory', key: `m-${m.id}`, date: m.date, createdAt: m.createdAt, memory: m })),
    ...milestones.map<Entry>((m) => ({ type: 'milestone', key: `s-${m.id}`, date: m.date, createdAt: '', title: m.title })),
  ].sort((a, b) => {
    if (a.date !== b.date) return a.date < b.date ? 1 : -1;
    if (a.type !== b.type) return a.type === 'milestone' ? -1 : 1;
    return b.createdAt.localeCompare(a.createdAt);
  });

  const grouped = new Map<string, Entry[]>();
  for (const e of entries) {
    const list = grouped.get(e.date) ?? [];
    list.push(e);
    grouped.set(e.date, list);
  }

  const remove = async (id: string) => {
    if (!window.confirm("Bu xotirani butunlay o'chirasizmi?")) return;
    await deleteMedia(id);
    update((s) => ({ ...s, memories: s.memories.filter((m) => m.id !== id) }));
    setMenuFor(null);
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

      {entries.length === 0 && (
        <div className="card empty">
          <h3>Birinchi xotirani qo'shing</h3>
          <p className="muted small" style={{ marginTop: 6 }}>Foto, video, ovoz yoki qisqa matn. Pastdagi "+" tugmasini bosing.</p>
        </div>
      )}

      {[...grouped.entries()].map(([date, list]) => (
        <section key={date} className="stack" style={{ gap: 12 }}>
          <div className="day">{formatDay(date)}</div>
          {list.map((e) =>
            e.type === 'milestone' ? (
              <MilestoneCard key={e.key} title={e.title} />
            ) : (
              <MemoryCard
                key={e.key}
                memory={e.memory}
                child={child}
                menuOpen={menuFor === e.memory.id}
                onToggleMenu={() => setMenuFor(menuFor === e.memory.id ? null : e.memory.id)}
                onRemove={() => remove(e.memory.id)}
              />
            ),
          )}
        </section>
      ))}
    </div>
  );
}

function MilestoneCard({ title }: { title: string }) {
  return (
    <article className="card row between">
      <div>
        <span className="pill sage">Milestone</span>
        <h3 style={{ marginTop: 8 }}>{title}</h3>
      </div>
      <span aria-hidden="true" style={{ fontSize: 26 }}>★</span>
    </article>
  );
}

interface MemoryCardProps {
  memory: Memory;
  child: { id: string; name: string; birthDate: string };
  menuOpen: boolean;
  onToggleMenu: () => void;
  onRemove: () => void;
}

function MemoryCard({ memory, child, menuOpen, onToggleMenu, onRemove }: MemoryCardProps) {
  const locked = isLockedNow(child, memory.locked);

  return (
    <article className="card stack" style={{ gap: 12 }}>
      {locked ? (
        <div className="lock">
          <span className="pill accent">18 yoshda ochiladi</span>
          <p style={{ marginTop: 10, fontWeight: 700 }}>Bu xotira {formatDate(unlockDate(child))} kuni ochiladi.</p>
        </div>
      ) : (
        <>
          <MemoryMedia memory={memory} />
          {memory.text && <p>{memory.text}</p>}
        </>
      )}

      <div className="row between">
        <div className="row wrap">
          <span className="pill">{KIND_LABEL[memory.kind]}</span>
          {memory.locked && <span className="pill lav">Qulflangan</span>}
        </div>
        <button className="more-btn" onClick={onToggleMenu} aria-label="Amallar" aria-expanded={menuOpen}>⋯</button>
      </div>

      {menuOpen && (
        <div className="menu" role="menu">
          <button className="menu-item danger" role="menuitem" onClick={onRemove}>O'chirish</button>
        </div>
      )}
    </article>
  );
}
