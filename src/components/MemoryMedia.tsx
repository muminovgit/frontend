import { useEffect, useState } from 'react';
import type { Memory } from '../types';
import { getMedia } from '../storage';
import { useT } from '../useT';

/** Xotiraning media faylini IndexedDB'dan olib ko'rsatadi. */
export function MemoryMedia({ memory }: { memory: Memory }) {
  const t = useT();
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!memory.hasMedia) return;
    let objectUrl: string | null = null;
    let alive = true;
    getMedia(memory.id).then((blob) => {
      if (!alive || !blob) return;
      objectUrl = URL.createObjectURL(blob);
      setUrl(objectUrl);
    });
    return () => {
      alive = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [memory.id, memory.hasMedia]);

  if (!memory.hasMedia) return null;
  if (!url) return <div className="media">{t('common.loading')}</div>;

  if (memory.kind === 'photo') return <div className="media"><img src={url} alt="" /></div>;
  if (memory.kind === 'video') return <div className="media"><video src={url} controls playsInline /></div>;
  if (memory.kind === 'audio') return <div className="media"><audio src={url} controls /></div>;
  return null;
}
