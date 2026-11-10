import { useState } from 'react';
import { useStore } from '../store';
import { MemoryMedia } from '../components/MemoryMedia';
import { deleteMedia } from '../storage';
import { ageText, formatDay, isLockedNow, unlockDate, formatDate, uid } from '../utils';
import type { Album, Memory } from '../types';

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
  const [pickFor, setPickFor] = useState<string | null>(null);
  const [openAlbum, setOpenAlbum] = useState<string | null>(null);
  const [newAlbumName, setNewAlbumName] = useState('');

  const albums = state.albums.filter((a) => a.childId === child.id);
  const mainMemories = state.memories.filter((m) => !m.albumId);
  const milestones = state.milestones.filter((m) => m.childId === child.id);

  const entries: Entry[] = [
    ...mainMemories.map<Entry>((m) => ({ type: 'memory', key: `m-${m.id}`, date: m.date, createdAt: m.createdAt, memory: m })),
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

  const moveTo = (memoryId: string, albumId: string | undefined) => {
    update((s) => ({ ...s, memories: s.memories.map((m) => (m.id === memoryId ? { ...m, albumId } : m)) }));
    setPickFor(null);
    setMenuFor(null);
  };

  const createAlbumAndMove = (memoryId: string) => {
    const name = newAlbumName.trim();
    if (!name) return;
    const id = uid();
    update((s) => ({
      ...s,
      albums: [...s.albums, { id, childId: child.id, name }],
      memories: s.memories.map((m) => (m.id === memoryId ? { ...m, albumId: id } : m)),
    }));
    setNewAlbumName('');
    setPickFor(null);
    setMenuFor(null);
  };

  const remove = async (id: string) => {
    if (!window.confirm("Bu xotirani butunlay o'chirasizmi?")) return;
    await deleteMedia(id);
    update((s) => ({ ...s, memories: s.memories.filter((m) => m.id !== id) }));
    setMenuFor(null);
  };

  const cardProps = (memory: Memory) => ({
    memory,
    child,
    albums,
    menuOpen: menuFor === memory.id,
    pickOpen: pickFor === memory.id,
    newAlbumName,
    onNewAlbumName: setNewAlbumName,
    onToggleMenu: () => {
      setPickFor(null);
      setMenuFor(menuFor === memory.id ? null : memory.id);
    },
    onTogglePick: () => setPickFor(pickFor === memory.id ? null : memory.id),
    onMove: (albumId: string | undefined) => moveTo(memory.id, albumId),
    onCreateAlbum: () => createAlbumAndMove(memory.id),
    onRemove: () => remove(memory.id),
  });

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

      {entries.length === 0 && albums.length === 0 && (
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
              <MemoryCard key={e.key} {...cardProps(e.memory)} />
            ),
          )}
        </section>
      ))}

      {albums.length > 0 && (
        <section className="stack" style={{ gap: 10 }}>
          <div className="day">Albomlar</div>
          {albums.map((a) => {
            const items = state.memories.filter((m) => m.albumId === a.id);
            const open = openAlbum === a.id;
            return (
              <div key={a.id} className="card stack" style={{ gap: 12 }}>
                <button className="album-head" onClick={() => setOpenAlbum(open ? null : a.id)} aria-expanded={open}>
                  <span><b>{a.name}</b> <span className="muted small">· {items.length} ta</span></span>
                  <span aria-hidden="true">{open ? '▴' : '▾'}</span>
                </button>
                {open && items.map((m) => <MemoryCard key={m.id} {...cardProps(m)} />)}
                {open && items.length === 0 && <p className="muted small">Bu albom bo'sh.</p>}
              </div>
            );
          })}
        </section>
      )}
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
  albums: Album[];
  menuOpen: boolean;
  pickOpen: boolean;
  newAlbumName: string;
  onNewAlbumName: (v: string) => void;
  onToggleMenu: () => void;
  onTogglePick: () => void;
  onMove: (albumId: string | undefined) => void;
  onCreateAlbum: () => void;
  onRemove: () => void;
}

function MemoryCard(p: MemoryCardProps) {
  const { memory, child } = p;
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
          <span className="pill">{memory.tag ?? KIND_LABEL[memory.kind]}</span>
          {memory.locked && <span className="pill lav">Qulflangan</span>}
        </div>
        <button className="more-btn" onClick={p.onToggleMenu} aria-label="Amallar" aria-expanded={p.menuOpen}>⋯</button>
      </div>

      {p.menuOpen && (
        <div className="menu" role="menu">
          <button className="menu-item" role="menuitem" onClick={p.onTogglePick}>Albomga tashlash</button>
          {memory.albumId && (
            <button className="menu-item" role="menuitem" onClick={() => p.onMove(undefined)}>Asosiy lentaga qaytarish</button>
          )}
          <button className="menu-item danger" role="menuitem" onClick={p.onRemove}>O'chirish</button>
        </div>
      )}

      {p.menuOpen && p.pickOpen && (
        <div className="stack" style={{ gap: 8 }}>
          <div className="row wrap" role="group" aria-label="Albom tanlash">
            {p.albums.map((a) => (
              <button key={a.id} className="chip" aria-pressed={memory.albumId === a.id} onClick={() => p.onMove(a.id)}>{a.name}</button>
            ))}
          </div>
          <div className="row" style={{ gap: 8 }}>
            <input className="input grow" value={p.newAlbumName} onChange={(e) => p.onNewAlbumName(e.target.value)} placeholder="Yangi albom nomi" maxLength={40} aria-label="Yangi albom nomi" />
            <button className="btn small-btn" onClick={p.onCreateAlbum} disabled={p.newAlbumName.trim() === ''}>Yaratish</button>
          </div>
        </div>
      )}
    </article>
  );
}
