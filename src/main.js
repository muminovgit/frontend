import './style.css';
import { renderTimeline } from './timeline.js';

const app = document.getElementById('app');

const routes = {
  '/timeline': renderTimeline,
};

function route() {
  const path = location.hash.replace(/^#/, '') || '/timeline';
  const view = routes[path];
  if (!view) {
    location.hash = '#/timeline';
    return;
  }
  view(app);
  window.scrollTo(0, 0);
}

window.addEventListener('hashchange', route);
route();
