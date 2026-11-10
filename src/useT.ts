import { useCallback } from 'react';
import { useStore } from './store';
import { translate, type Lang } from './i18n';

/** Joriy til bo'yicha tarjima funksiyasi. */
export function useT() {
  const { state } = useStore();
  const lang = state.lang;
  return useCallback((key: string, vars?: Record<string, string | number>) => translate(lang, key, vars), [lang]);
}

export function useLang(): Lang {
  return useStore().state.lang;
}
