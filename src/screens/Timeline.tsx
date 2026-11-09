import { useState } from 'react';
import { useStore } from '../store';
import { MemoryMedia } from '../components/MemoryMedia';
import { deleteMedia } from '../storage';
import { ageText, formatDay, isLockedNow, unlockDate, formatDate, uid } from '../utils';
import type { Memory } from '../types';

const KIND_LABEL: Record<Memory['kind'], string> = {
  photo: 'Foto',
  video: 'Video',
  audio: 'Ovoz',
  note: 'Matn',
};

const MAIN = 'main';

type Entry =
  | { type: 'memory'; key: string; date: string; createdAt: string; memory: Memory }
  | { type: 'milestone'; key: string; date: string; createdAt: string; title: string };

export function Timeline() {
  const { state, update } = useStore();
  const child = state.child!;

  const [view, setView] = useState<string>(MAIN); // 'main' yoki albom id
  const [menuFor, setMenuFor] = useState<string | null>(null);
  const [pickFor, setPickFor] = useState<string | null>(null);
  const [albumName, setAlbumName] = useState('');

  const albums = state.albums.filter((a) => a.childId === child.id);
  const inMain = view === MAIN;

  const visibleMemories = state.memories.filter((m) => (inMain ? !m.albumId : m.albumId === view));
  const milestones = inMain ? state.milestones.filter((m) => m.childId === child.id) : [];

  const entries: Entry[] = [
    ...visibleMemories.map<Entry>((m) => ({ type: 'memory', key: `m-${m.id}`, date: m.date, createdAt: m.createdAt, memory: m })),
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

  const addAlbum = () => {
    const name = albumName.trim();
    if (!name) return;
    const id = uid();
    update((s) => ({ ...s, albums: [...s.albums, { id, childId: child.id, name }] }));
    setAlbumName('');
    setView(id);
  };

  const moveTo = (memoryId: string, albumId: string | undefined) => {
    update((s) => ({
      ...s,
      memories: s.memories.map((m) => (m.id === memoryId ? { ...m, albumId } : m)),
    }));
    setMenuFor(null);
    setPickFor(null);
  };

  const remove = async (id: string) => {
    if (!window.confirm("Bu xotirani butunlay o'chirasizmi?")) return;
    await deleteMedia(id);
    update((s) => ({ ...s, memories: s.memories.filter((m) => m.id !== id) }));
    setMenuFor(null);
  };

  const currentAlbum = albums.find((a) => a.id === view);

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

      <div className="row wrap" role="tablist" aria-label="Lenta va albomlar">
        <button className="chip" aria-pressed={inMain} onClick={() => setView(MAIN)}>Asosiy</button>
        {albums.map((a) => (
          <button key={a.id} className="chip" aria-pressed={view === a.id} onClick={() => setView(a.id)}>{a.name}</button>
        ))}
      </div>

      <div className="row" style={{ gap: 8 }}>
        <input className="input grow" value={albumName} onChange={(e) => setAlbumName(e.target.value)} placeholder="Yangi albom nomi" maxLength={40} aria-label="Yangi albom nomi" />
        <button className="btn small-btn" onClick={addAlbum} disabled={albumName.trim() === ''}>+ Albom</button>
      </div>

      {!inMain && currentAlbum && (
        <p className="muted small">"{currentAlbum.name}" albomidagi xotiralar. Asosiy lentada ko'rinmaydi.</p>
      )}

      {entries.length === 0 && (
        <div className="card empty">
          <h3>{inMain ? "Birinchi xotirani qo'shing" : "Bu albom bo'sh"}</h3>
          <p className="muted small" style={{ marginTop: 6 }}>
            {inMain ? 'Foto, video, ovoz yoki qisqa matn. Pastdagi "+" tugmasini bosing.' : "Xotiraning ⋯ menyusidan uni shu albomga qo'shing."}
          </p>
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
                albums={albums}
                currentView={view}
                menuOpen={menuFor === e.memory.id}
                pickOpen={pickFor === e.memory.id}
                onToggleMenu={() => {
                  setPickFor(null);
                  setMenuFor(menuFor === e.memory.id ? null : e.memory.id);
                }}
                onTogglePick={() => setPickFor(pickFor === e.memory.id ? null : e.memory.id)}
                onMove={(albumId) => moveTo(e.memory.id, albumId)}
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
  albums: { id: string; name: string }[];
  currentView: string;
  menuOpen: boolean;
  pickOpen: boolean;
  onToggleMenu: () => void;
  onTogglePick: () => void;
  onMove: (albumId: string | undefined) => void;
  onRemove: () => void;
}

function MemoryCard(p: MemoryCardProps) {
  const { memory, child } = p;
  const locked = isLockedNow(child, memory.locked);
  const inAlbum = Boolean(memory.albumId);

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
        <button className="more-btn" onClick={p.onToggleMenu} aria-label="Amallar" aria-expanded={p.menuOpen}>⋯</button>
      </div>

      {p.menuOpen && (
        <div className="menu" role="menu">
          <button className="menu-item" role="menuitem" onClick={p.onTogglePick}>Albomga qo'shish</button>
          {inAlbum && (
            <button className="menu-item" role="menuitem" onClick={() => p.onMove(undefined)}>Albomdan olish (asosiy lentaga)</button>
          )}
          <button className="menu-item danger" role="menuitem" onClick={p.onRemove}>O'chirish</button>
        </div>
      )}

      {p.menuOpen && p.pickOpen && (
        <div className="row wrap" role="group" aria-label="Albom tanlash">
          {p.albums.length === 0 && <p className="muted small">Avval yuqorida albom yarating.</p>}
          {p.albums.map((a) => (
            <button key={a.id} className="chip" aria-pressed={memory.albumId === a.id} onClick={() => p.onMove(a.id)}>{a.name}</button>
          ))}
        </div>
      )}
    </article>
  );
}
