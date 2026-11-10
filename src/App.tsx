import { lazy, Suspense, useEffect, useState } from 'react';
import { useStore } from './store';
import { Onboarding } from './screens/Onboarding';
import { Timeline } from './screens/Timeline';
import { AddMemory } from './screens/AddMemory';
import { Growth } from './screens/Growth';
import { Family } from './screens/Family';
const Child3D = lazy(() => import('./screens/Child3D').then((m) => ({ default: m.Child3D })));
import { TabBar, type TabId } from './components/TabBar';

type Route = TabId | 'child3d';

const ROUTES: Route[] = ['timeline', 'growth', 'add', 'family', 'child3d'];

function routeFromHash(): Route {
  const h = window.location.hash.replace('#/', '') as Route;
  return ROUTES.includes(h) ? h : 'timeline';
}

export function App() {
  const { state } = useStore();
  const [route, setRoute] = useState<Route>(routeFromHash);

  useEffect(() => {
    const onHash = () => setRoute(routeFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const go = (id: Route) => {
    window.location.hash = `#/${id}`;
    setRoute(id);
    window.scrollTo({ top: 0 });
  };

  if (!state.child) {
    return (
      <div className="app">
        <Onboarding />
      </div>
    );
  }

  const screen = {
    timeline: <Timeline />,
    growth: <Growth />,
    add: <AddMemory onDone={() => go('timeline')} />,
    family: <Family />,
    child3d: (
      <Suspense fallback={<p className="muted">Yuklanmoqda…</p>}>
        <Child3D />
      </Suspense>
    ),
  }[route];

  return (
    <div className="app">
      {screen}
      <TabBar current={route === 'child3d' ? 'timeline' : route} onChange={(id) => go(id)} />
    </div>
  );
}
