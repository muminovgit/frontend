import { useEffect, useState } from 'react';
import { useStore } from './store';
import { Onboarding } from './screens/Onboarding';
import { Timeline } from './screens/Timeline';
import { AddMemory } from './screens/AddMemory';
import { Growth } from './screens/Growth';
import { Family } from './screens/Family';
import { Book } from './screens/Book';
import { TabBar, type TabId } from './components/TabBar';

const ROUTES: TabId[] = ['timeline', 'growth', 'add', 'family', 'book'];

function routeFromHash(): TabId {
  const h = window.location.hash.replace('#/', '') as TabId;
  return ROUTES.includes(h) ? h : 'timeline';
}

export function App() {
  const { state } = useStore();
  const [route, setRoute] = useState<TabId>(routeFromHash);

  useEffect(() => {
    const onHash = () => setRoute(routeFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const go = (id: TabId) => {
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
    book: <Book />,
  }[route];

  return (
    <div className="app">
      {screen}
      <TabBar current={route} onChange={go} />
    </div>
  );
}
