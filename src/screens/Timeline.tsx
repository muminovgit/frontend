import { useState } from 'react';
import { useStore } from '../store';
import { useLang, useT } from '../useT';
import { MemoryMedia } from '../components/MemoryMedia';
import { deleteMedia } from '../storage';
import { ageText, countdown, formatDate, formatDay, isLockedNow, memoryUnlockDate, schoolDate, todayIso, uid, unlockDate } from '../utils';
import type { Album, Child, Memory } from '../types';

type Entry =
  | { type: 'memory'; key: string; date: string; createdAt: string; memory: Memory }
  | { type: 'milestone'; key: string; date: string; createdAt: string; title: string };

export function Timeline() {
  const { state, update } = useStore();
  const t = useT();
  const lang = useLang();
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
    if (!window.confirm(t('timeline.delete_q'))) return;
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
            <p className="muted">{ageText(lang, child.birthDate)} · {t('hero.count', { n: state.memories.length })}</p>
          </div>
        </div>
        <button className="btn small-btn" style={{ marginTop: 12 }} onClick={() => { window.location.hash = '#/child3d'; }}>{t('hero.3d')}</button>
      </div>

      {entries.length === 0 && albums.length === 0 && (
        <div className="card empty">
          <h3>{t('timeline.empty_t')}</h3>
          <p className="muted small" style={{ marginTop: 6 }}>{t('timeline.empty_s')}</p>
        </div>
      )}

      {[...grouped.entries()].map(([date, list]) => (
        <section key={date} className="stack" style={{ gap: 12 }}>
          <div className="day">{formatDay(lang, date)}</div>
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
          <div className="day">{t('timeline.albums')}</div>
          {albums.map((a) => {
            const items = state.memories.filter((m) => m.albumId === a.id);
            const open = openAlbum === a.id;
            return (
              <div key={a.id} className="card stack" style={{ gap: 12 }}>
                <button className="album-head" onClick={() => setOpenAlbum(open ? null : a.id)} aria-expanded={open}>
                  <span><b>{a.name}</b> <span className="muted small">· {t('timeline.album_count', { n: items.length })}</span></span>
                  <span aria-hidden="true">{open ? '▴' : '▾'}</span>
                </button>
                {open && items.map((m) => <MemoryCard key={m.id} {...cardProps(m)} />)}
                {open && items.length === 0 && <p className="muted small">{t('timeline.album_empty')}</p>}
              </div>
            );
          })}
        </section>
      )}
    </div>
  );
}

function MilestoneCard({ title }: { title: string }) {
  const t = useT();
  return (
    <article className="card row between">
      <div>
        <span className="pill sage">{t('timeline.milestone')}</span>
        <h3 style={{ marginTop: 8 }}>{title}</h3>
      </div>
      <span aria-hidden="true" style={{ fontSize: 26 }}>★</span>
    </article>
  );
}

/** Zaman kapsulasi: yopiq xotira konvert ko'rinishida, ochilishigacha teskari hisob bilan. */
function Capsule({ child, memory }: { child: Child; memory: Memory }) {
  const t = useT();
  const lang = useLang();
  const until = memoryUnlockDate(child, memory)!;
  const left = countdown(todayIso(), until);
  const when =
    until === unlockDate(child) ? t('capsule.when18')
    : until === schoolDate(child) ? t('capsule.whenSchool')
    : t('capsule.whenDate', { date: formatDate(lang, until) });

  return (
    <div className="capsule">
      <div className="capsule-env">
        <div className="capsule-lock" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="11" width="14" height="10" rx="2.5" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /></svg>
        </div>
        <p className="capsule-msg">{t('timeline.capsule_msg', { name: child.name, when })}</p>
      </div>
      <div className="capsule-count">
        <span className="small muted">{t('timeline.opens')}</span>
        <b className="tabular">{t('timeline.countdown', left)}</b>
      </div>
    </div>
  );
}

interface MemoryCardProps {
  memory: Memory;
  child: Child;
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
  const t = useT();
  const { memory, child } = p;
  const locked = isLockedNow(child, memory);

  return (
    <article className="card stack" style={{ gap: 12 }}>
      {locked ? (
        <Capsule child={child} memory={memory} />
      ) : (
        <>
          <MemoryMedia memory={memory} />
          {memory.text && <p>{memory.text}</p>}
        </>
      )}

      <div className="row between">
        <div className="row wrap">
          <span className="pill">{memory.tag ? t(`add.type.${memory.tag}`) : t('timeline.kind_note')}</span>
        </div>
        <button className="more-btn" onClick={p.onToggleMenu} aria-label={t('timeline.menu')} aria-expanded={p.menuOpen}>⋯</button>
      </div>

      {p.menuOpen && (
        <div className="menu" role="menu">
          <button className="menu-item" role="menuitem" onClick={p.onTogglePick}>{t('timeline.move')}</button>
          {memory.albumId && (
            <button className="menu-item" role="menuitem" onClick={() => p.onMove(undefined)}>{t('timeline.back_main')}</button>
          )}
          <button className="menu-item danger" role="menuitem" onClick={p.onRemove}>{t('common.delete')}</button>
        </div>
      )}

      {p.menuOpen && p.pickOpen && (
        <div className="stack" style={{ gap: 8 }}>
          <div className="row wrap" role="group" aria-label={t('timeline.albums')}>
            {p.albums.map((a) => (
              <button key={a.id} className="chip" aria-pressed={memory.albumId === a.id} onClick={() => p.onMove(a.id)}>{a.name}</button>
            ))}
          </div>
          <div className="row" style={{ gap: 8 }}>
            <input className="input grow" value={p.newAlbumName} onChange={(e) => p.onNewAlbumName(e.target.value)} placeholder={t('timeline.new_album')} maxLength={40} aria-label={t('timeline.new_album')} />
            <button className="btn small-btn" onClick={p.onCreateAlbum} disabled={p.newAlbumName.trim() === ''}>{t('common.create')}</button>
          </div>
        </div>
      )}
    </article>
  );
}
