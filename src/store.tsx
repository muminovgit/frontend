import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import type { AppState } from './types';
import { loadState, saveState } from './storage';

interface StoreValue {
  state: AppState;
  update: (fn: (prev: AppState) => AppState) => void;
  reset: () => void;
}

const StoreContext = createContext<StoreValue | null>(null);

export function StoreProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppState>(() => loadState());

  useEffect(() => {
    saveState(state);
  }, [state]);

  const update = useCallback((fn: (prev: AppState) => AppState) => {
    setState((prev) => fn(prev));
  }, []);

  const reset = useCallback(() => {
    try {
      localStorage.removeItem('xotira-hayot:v1');
    } catch {
      /* e'tiborsiz */
    }
    setState(loadState());
  }, []);

  const value = useMemo(() => ({ state, update, reset }), [state, update, reset]);
  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore(): StoreValue {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error('useStore StoreProvider ichida ishlatilishi kerak');
  return ctx;
}
