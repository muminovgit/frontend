import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { useStore } from '../store';
import { getMedia, putMedia } from '../storage';
import { animateFigure, buildFigure, type Figure, type Zone } from '../components/figure3d';

const ZONES: Record<Zone, { label: string; dat: string; word: string; anim: string; freq: number }> = {
  head: { label: 'Bosh', dat: 'boshiga', word: 'Dada!', anim: 'nod', freq: 330 },
  hand: { label: "Qo'l", dat: "qo'liga", word: 'Onajon!', anim: 'wave', freq: 440 },
  body: { label: 'Tana', dat: 'tanasiga', word: 'Sevaman!', anim: 'happy', freq: 520 },
};

const DEFAULT_HEIGHT = 86;
const STEPS = ['Fon olib tashlanmoqda', '3D model yaratilmoqda', "Rig va animatsiya qo'shilmoqda"];
const MEMBERS_SAMPLE = ['Asadbek', 'Madina', 'Buvi'];

function beep(freq: number) {
  try {
    const ac = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
    const o = ac.createOscillator();
    const g = ac.createGain();
    o.type = 'sine';
    o.frequency.value = freq;
    o.connect(g);
    g.connect(ac.destination);
    g.gain.setValueAtTime(0.18, ac.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + 0.45);
    o.start();
    o.stop(ac.currentTime + 0.45);
  } catch {
    /* audio ishlamasa e'tiborsiz */
  }
}

function nowHm() {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

export function Child3D() {
  const { state } = useStore();
  const child = state.child!;
  const latest = state.measurements
    .filter((m) => m.childId === child.id && m.heightCm !== undefined)
    .sort((a, b) => a.date.localeCompare(b.date))
    .at(-1);

  const [height, setHeight] = useState<number>(latest?.heightCm ?? DEFAULT_HEIGHT);
  const [consent, setConsent] = useState(false);
  const [photoName, setPhotoName] = useState<string | null>(null);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [gen, setGen] = useState<{ running: boolean; pct: number; done: boolean }>({ running: false, pct: 0, done: false });
  const [voiceNames, setVoiceNames] = useState<Partial<Record<Zone, string>>>({});
  const [bubble, setBubble] = useState<string | null>(null);
  const [events, setEvents] = useState<{ text: string; time: string }[]>([]);
  const [sendStatus, setSendStatus] = useState('');

  const stageRef = useRef<HTMLDivElement>(null);
  const figureRef = useRef<Figure | null>(null);
  const modeRef = useRef<{ name: string; start: number }>({ name: 'idle', start: 0 });
  const clockRef = useRef<{ getElapsedTime: () => number } | null>(null);
  const audioRef = useRef<Partial<Record<Zone, HTMLAudioElement>>>({});
  const bubbleTimer = useRef<number | undefined>(undefined);

  const addEvent = (text: string) => setEvents((prev) => [{ text, time: nowHm() }, ...prev].slice(0, 6));

  const showBubble = (text: string) => {
    setBubble(text);
    window.clearTimeout(bubbleTimer.current);
    bubbleTimer.current = window.setTimeout(() => setBubble(null), 1800);
  };

  const setMode = (name: string) => {
    if (!clockRef.current) return;
    modeRef.current = { name, start: clockRef.current.getElapsedTime() };
  };

  const playVoice = (zone: Zone) => {
    const a = audioRef.current[zone];
    if (a) {
      a.currentTime = 0;
      a.play().catch(() => beep(ZONES[zone].freq));
    } else {
      beep(ZONES[zone].freq);
    }
  };

  const zoneTap = (zone: Zone) => {
    const z = ZONES[zone];
    setMode(z.anim);
    playVoice(zone);
    showBubble(z.word);
    addEvent(`${child.name} ${z.dat} tegdi`);
  };

  const remoteTouch = (name: string) => {
    setMode('happy');
    playVoice('head');
    showBubble(`${name} tegdi!`);
    addEvent(`${name} ${child.name}ga tegdi · qurilmada ovoz chiqdi`);
    setSendStatus(`${name}ga tegish yuborildi (namuna).`);
  };

  // Sahna: bir marta quriladi, animatsiya va tegishni boshqaradi.
  useEffect(() => {
    const container = stageRef.current;
    if (!container) return;
    const w = container.clientWidth || 320;
    const h = container.clientHeight || 300;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(w, h);
    container.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(32, w / h, 0.1, 100);
    camera.position.set(0, 1.9, 8.2);
    camera.lookAt(0, 1.45, 0);
    scene.add(new THREE.HemisphereLight(0xffffff, 0xd9d2ff, 1.7));
    const sun = new THREE.DirectionalLight(0xffffff, 1.1);
    sun.position.set(3, 6, 5);
    scene.add(sun);

    const figure = buildFigure();
    scene.add(figure.root);
    figureRef.current = figure;
    const t0 = performance.now();
    const clock = { getElapsedTime: () => (performance.now() - t0) / 1000 };
    clockRef.current = clock;

    let raf = 0;
    const frame = () => {
      raf = requestAnimationFrame(frame);
      const t = clock.getElapsedTime();
      const { name, start } = modeRef.current;
      const e = t - start;
      const mode = name !== 'idle' && e > 2.2 ? 'idle' : name;
      animateFigure(figure, mode, t, e);
      renderer.render(scene, camera);
    };
    frame();

    const ray = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    let downX = 0;
    let moved = 0;
    let dragging = false;

    const onDown = (ev: PointerEvent) => {
      dragging = true;
      downX = ev.clientX;
      moved = 0;
    };
    const onUp = () => {
      dragging = false;
    };
    const onMove = (ev: PointerEvent) => {
      if (!dragging) return;
      const dx = ev.clientX - downX;
      downX = ev.clientX;
      moved += Math.abs(dx);
      figure.root.rotation.y += dx * 0.012;
    };
    const onClick = (ev: MouseEvent) => {
      if (moved >= 6) return;
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
      ray.setFromCamera(pointer, camera);
      const hit = ray.intersectObjects(figure.pickables, false)[0];
      const zone = hit?.object.userData.zone as Zone | undefined;
      if (zone) {
        zoneTapRef.current(zone);
      } else {
        setMode(['wave', 'nod', 'jump', 'happy'][Math.floor(Math.random() * 4)]);
        showBubble('Salom!');
      }
    };

    const el = renderer.domElement;
    el.addEventListener('pointerdown', onDown);
    el.addEventListener('pointermove', onMove);
    el.addEventListener('click', onClick);
    window.addEventListener('pointerup', onUp);

    return () => {
      cancelAnimationFrame(raf);
      el.removeEventListener('pointerdown', onDown);
      el.removeEventListener('pointermove', onMove);
      el.removeEventListener('click', onClick);
      window.removeEventListener('pointerup', onUp);
      renderer.dispose();
      el.remove();
      figureRef.current = null;
      clockRef.current = null;
    };
    // zoneTapRef orqali eng so'nggi funksiyaga murojaat qilinadi
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Har doim eng so'nggi zoneTap'ga murojaat qilish uchun ref.
  const zoneTapRef = useRef(zoneTap);
  zoneTapRef.current = zoneTap;

  // Ovozlarni qurilmadan yuklash
  useEffect(() => {
    let alive = true;
    const urls: string[] = [];
    (['head', 'hand', 'body'] as Zone[]).forEach(async (zone) => {
      const blob = await getMedia(`voice:${zone}`);
      if (!alive || !blob) return;
      const url = URL.createObjectURL(blob);
      urls.push(url);
      audioRef.current[zone] = new Audio(url);
      setVoiceNames((prev) => ({ ...prev, [zone]: 'Saqlangan ovoz' }));
    });
    return () => {
      alive = false;
      urls.forEach((u) => URL.revokeObjectURL(u));
    };
  }, []);

  // Bo'y o'zgarganda modelning masshtabi ham o'zgaradi
  useEffect(() => {
    figureRef.current?.root.scale.setScalar(height / DEFAULT_HEIGHT);
  }, [height]);

  // Foto → 3D: simulyatsiya
  const startGeneration = () => {
    if (!consent || gen.running) return;
    setGen({ running: true, pct: 0, done: false });
    let p = 0;
    const timer = window.setInterval(() => {
      p = Math.min(100, p + 2);
      setGen({ running: p < 100, pct: p, done: p >= 100 });
      if (p >= 100) {
        window.clearInterval(timer);
        setMode('jump');
        showBubble('Men tayyorman!');
        addEvent('3D model yaratildi');
      }
    }, 90);
  };

  const onPhoto = (file: File | undefined) => {
    if (!file) return;
    setPhotoName(file.name);
    setPhotoUrl(URL.createObjectURL(file));
  };

  const onVoice = async (zone: Zone, file: File | undefined) => {
    if (!file) return;
    await putMedia(`voice:${zone}`, file);
    audioRef.current[zone] = new Audio(URL.createObjectURL(file));
    setVoiceNames((prev) => ({ ...prev, [zone]: file.name }));
    addEvent(`${ZONES[zone].label} ovozi yangilandi`);
  };

  return (
    <div className="screen">
      <div className="row between">
        <h2>3D {child.name}</h2>
        <span className="pill sky tabular">{height} sm</span>
      </div>
      <p className="muted">Fotodan 3D model yarating, tegib ko'ring, ovozini eshiting.</p>

      <div className="card stack" style={{ gap: 12 }}>
        <div className="label">1 · Foto va rozilik</div>
        <label className="switch" style={{ alignItems: 'flex-start', justifyContent: 'flex-start' }}>
          <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} style={{ marginTop: 3 }} />
          <span>Ota-onaman. Bolaning fotosini 3D model yaratish uchun yuborishga roziman.</span>
        </label>
        <label className="btn ghost" style={{ cursor: 'pointer' }}>
          {photoName ? `Tanlandi: ${photoName}` : 'Foto tanlash'}
          <input type="file" accept="image/*" hidden onChange={(e) => onPhoto(e.target.files?.[0])} />
        </label>
        <div className="row">
          {photoUrl && <img src={photoUrl} alt="Tanlangan foto" style={{ width: 64, height: 64, borderRadius: 16, objectFit: 'cover' }} />}
          <p className="muted small">{photoName ? 'Foto tayyor' : 'Foto tanlanmagan'}</p>
        </div>
        <button className="btn" onClick={startGeneration} disabled={!consent || !photoName || gen.running}>
          {gen.done ? 'Qayta yaratish' : gen.running ? 'Yaratilmoqda' : '3D model yaratish'}
        </button>
        {(gen.running || gen.done) && (
          <div className="stack" style={{ gap: 8 }}>
            <div className="row between">
              <span style={{ fontWeight: 800, fontSize: 14 }}>
                {gen.done ? 'Model tayyor' : STEPS[Math.min(STEPS.length - 1, Math.floor(gen.pct / 34))]}
              </span>
              <span className="label tabular">{gen.pct}%</span>
            </div>
            <div className="bar"><span style={{ width: `${gen.pct}%` }} /></div>
          </div>
        )}
        <p className="note">Namuna: haqiqiy 3D xizmat ulanmagan. Jarayon simulyatsiya qilinadi.</p>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden', position: 'relative' }}>
        <div ref={stageRef} style={{ height: 300, background: 'radial-gradient(circle at 50% 35%, #FFFFFF, #EAF9FE 70%)' }} />
        {bubble && (
          <span className="pill accent" style={{ position: 'absolute', top: 14, left: 14, fontSize: 15 }}>{bubble}</span>
        )}
      </div>
      <p className="muted small" style={{ textAlign: 'center' }}>Bosh, qo'l yoki tanaga teging. Aylantirish uchun suring.</p>

      <div className="card stack" style={{ gap: 10 }}>
        <div className="row between">
          <span className="label">Bo'y</span>
          <b className="tabular">{height} sm</b>
        </div>
        <input
          type="range"
          min={70}
          max={100}
          value={height}
          onChange={(e) => setHeight(Number(e.target.value))}
          aria-label="Bo'y, sm"
          style={{ width: '100%', accentColor: 'var(--brand)' }}
        />
        <div className="row between">
          <span className="muted small">70 sm</span>
          <span className="muted small">100 sm</span>
        </div>
      </div>

      <div className="row wrap">
        {[
          ['wave', 'Salom'],
          ['nod', 'Onaylash'],
          ['jump', 'Sakrash'],
          ['happy', 'Quvonch'],
        ].map(([anim, label]) => (
          <button key={anim} className="chip" onClick={() => { setMode(anim); showBubble(`${label}!`); }}>{label}</button>
        ))}
      </div>

      <div className="card stack" style={{ gap: 12 }}>
        <div className="label">2 · Ovozlar</div>
        {(['head', 'hand', 'body'] as Zone[]).map((zone) => (
          <div key={zone} className="row between" style={{ gap: 10 }}>
            <div className="grow">
              <b>{ZONES[zone].label}</b>
              <div className="muted small">{voiceNames[zone] ?? `Standart ovoz · "${ZONES[zone].word}"`}</div>
            </div>
            <label className="chip" style={{ cursor: 'pointer' }}>
              Yuklash
              <input type="file" accept="audio/*" hidden onChange={(e) => onVoice(zone, e.target.files?.[0])} />
            </label>
          </div>
        ))}
      </div>

      <div className="card stack" style={{ gap: 12 }}>
        <div className="label">3 · Ota-onalar</div>
        {MEMBERS_SAMPLE.map((name) => (
          <div key={name} className="member">
            <div className="avatar sm">{name.charAt(0)}</div>
            <div className="who"><h3>{name}</h3></div>
            <button className="chip" onClick={() => remoteTouch(name)}>Tegish</button>
          </div>
        ))}
        {sendStatus && <p className="muted small" aria-live="polite">{sendStatus}</p>}
      </div>

      <div className="card stack" style={{ gap: 10 }}>
        <div className="label">Bildirishnomalar</div>
        {events.length === 0 && <p className="muted small">Hozircha tegish yo'q.</p>}
        {events.map((ev, i) => (
          <div key={`${ev.time}-${i}`} className="card" style={{ padding: '12px 14px', boxShadow: 'none' }}>
            <div style={{ fontWeight: 700, fontSize: 14 }}>{ev.text}</div>
            <div className="muted small" style={{ marginTop: 4 }}>{ev.time} · Ota-onalarga yetkazildi</div>
          </div>
        ))}
      </div>
    </div>
  );
}
