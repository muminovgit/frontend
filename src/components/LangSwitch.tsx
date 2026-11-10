import { LANGS, type Lang } from '../i18n';
import { useStore } from '../store';
import { useT } from '../useT';

/** Tilni tanlash: O'zbekcha / Русский / English */
export function LangSwitch() {
  const { state, update } = useStore();
  const t = useT();
  const set = (lang: Lang) => update((s) => ({ ...s, lang }));
  return (
    <div className="row wrap" role="group" aria-label={t('lang.label')}>
      {LANGS.map((l) => (
        <button key={l.id} className="chip" aria-pressed={state.lang === l.id} onClick={() => set(l.id)}>{l.label}</button>
      ))}
    </div>
  );
}
