import React, { useEffect, useMemo, useRef, useState } from 'react';
import { CaretRight, FilmStrip } from '@phosphor-icons/react';
import { Mark } from '../ui/Mark';
import { Chip } from '../ui/Chip';
import { useStudio } from '../context/StudioContext';
import { createEarth, pickTags } from '../lib/earth.js';
import { buildGlobe } from '../lib/github-data.js';
import placesData from '../lib/places.json';

interface HeroProps {
  onSelectFilmForPanel?: (filmId: string) => void;
}

const CARD_W = 262;
const SCROLL_ROOM = 800; // px of scroll over which the sun rises (BUILD_SPEC 4.1)

// Scroll: 0-800 px the sun rises; then the hero stays pinned one more screen while section 2 (.sheet, pulled up
// with margin-top: -100vh) slides over it like a sheet of glass, and the hero sinks and dims (--hp, portfolio pattern).
// The globe draws 60 times a second. Cards, dashed lines and name tags follow it by writing their positions
// straight to the DOM from earth.js's onPlace callback: no React state per frame (that made the page stutter).
export const Hero: React.FC<HeroProps> = ({ onSelectFilmForPanel }) => {
  const { films, topics, navigate } = useStudio();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wrapRef = useRef<HTMLElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const cardRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const lineRefs = useRef<Record<string, SVGPathElement | null>>({});
  const tagRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const earthRef = useRef<any>(null);
  const [globeLoaded, setGlobeLoaded] = useState(false);

  const globe = useMemo(() => (films.length || topics.length ? buildGlobe(films, topics, placesData) : { stories: [], arcs: [] }),
    [films, topics]);
  const cardStories = globe.stories.filter((s: any) => s.card);
  const tagStories = globe.stories.filter((s: any) => !s.card);

  // Numbers row: computed from real data only ("—" until loaded; never a default number)
  const made = films.filter(f => ['ready', 'uploaded', 'finished', 'review'].includes(f.status));
  const filmsMade = made.length;
  const factsChecked = made.reduce((acc, f) => acc + (f.release?.sources?.length || 0), 0);
  const storiesQueued = topics.length;
  const newestFilm = made.find(f => f.video?.url);

  useEffect(() => {
    let cancelled = false;
    let earth: any = null;
    (async () => {
      try {
        const resp = await fetch('/earth.json');
        if (!resp.ok) return;
        const data = await resp.json();
        if (cancelled || !canvasRef.current) return;
        earth = createEarth(canvasRef.current, data, globe.stories, {
          arcs: globe.arcs,
          onPlace: (places: any[]) => {
            const W = canvasRef.current?.clientWidth || window.innerWidth;
            const phone = W < 640;
            const rects: any[] = [];
            for (const p of places) {
              if (!p.card) continue;
              const el = cardRefs.current[p.n];
              const ln = lineRefs.current[p.n];
              if (!el) continue;
              if (phone) { el.style.display = 'none'; if (ln) ln.style.display = 'none'; continue; }
              const left = p.card === 'left' ? p.x - 300 : p.x + 150;
              const top = p.y - 150;
              el.style.display = '';
              el.style.transform = `translate3d(${left.toFixed(1)}px, ${top.toFixed(1)}px, 0)`;
              const h = el.offsetHeight || 86;
              rects.push({ l: left, t: top, r: left + CARD_W, b: top + h });
              if (ln) {
                ln.style.display = '';
                const tx = p.card === 'left' ? left + CARD_W : left;
                ln.setAttribute('d', `M${p.x.toFixed(1)} ${p.y.toFixed(1)} L${tx.toFixed(1)} ${(top + h - 10).toFixed(1)}`);
              }
            }
            const shown = phone
              ? pickTags(places.filter(p => p.kind === 'made'), { width: W, maxY: (canvasRef.current?.clientHeight || 800) - 40 })
              : pickTags(places, { blocked: rects, width: W });
            const on = new Set(shown.map((t: any) => t.n));
            for (const s of tagStories) {
              const el = tagRefs.current[s.n];
              if (el && !on.has(s.n)) el.style.opacity = '0';
            }
            for (const t of shown) {
              const el = tagRefs.current[t.n];
              if (!el) continue;
              el.style.opacity = '1';
              el.style.transform = `translate3d(${t.left.toFixed(1)}px, ${t.top.toFixed(1)}px, 0)`;
            }
          },
        });
        earthRef.current = earth;
        setGlobeLoaded(true);
        onScroll();
      } catch (err) {
        console.warn('Globe could not load:', err);
      }
    })();
    return () => {
      cancelled = true;
      if (earth) earth.destroy();
      earthRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [globe]);

  // Scroll: sunrise progress, text parallax/fade, and the --hp sheet variable. Direct style writes, one per frame.
  const onScroll = () => {
    const wrap = wrapRef.current;
    if (!wrap) return;
    const wrapTop = wrap.getBoundingClientRect().top + window.scrollY;
    const y = window.scrollY - wrapTop;
    const p = Math.max(0, Math.min(1, y / SCROLL_ROOM));
    earthRef.current?.setProgress(p);
    if (textRef.current) {
      const opacity = p < 0.55 ? 1 : Math.max(0, 1 - (p - 0.55) / 0.45);
      textRef.current.style.transform = `translate3d(0, ${(-0.25 * Math.max(0, y)).toFixed(1)}px, 0)`;
      textRef.current.style.opacity = opacity.toFixed(3);
      textRef.current.style.pointerEvents = opacity < 0.05 ? 'none' : 'auto';
    }
    if (stageRef.current) {
      const hp = Math.max(0, Math.min(1, (y - SCROLL_ROOM) / (window.innerHeight || 900)));
      stageRef.current.style.setProperty('--hp', hp.toFixed(4));
    }
  };

  useEffect(() => {
    let frame = 0;
    const request = () => { if (!frame) frame = requestAnimationFrame(() => { frame = 0; onScroll(); }); };
    window.addEventListener('scroll', request, { passive: true });
    window.addEventListener('resize', request);
    onScroll();
    // pause the globe when the hero is off-screen
    const io = new IntersectionObserver(([e]) => earthRef.current?.setActive(e.isIntersecting), { threshold: 0 });
    if (stageRef.current) io.observe(stageRef.current);
    return () => {
      window.removeEventListener('scroll', request);
      window.removeEventListener('resize', request);
      cancelAnimationFrame(frame);
      io.disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section ref={wrapRef} className="hero-wrap" aria-label="Candela Studio" style={{ height: `calc(200vh + ${SCROLL_ROOM}px)`, position: 'relative' }}>
      <div ref={stageRef} className="hero-stage" style={{ position: 'sticky', top: 0, height: '100vh', overflow: 'hidden', width: '100%' }}>
        <div className="grain" />
        <div className="topglow" />

        <div className="hero-sink" style={{ position: 'absolute', inset: 0 }}>
          <canvas
            ref={canvasRef}
            className="earth"
            aria-hidden="true"
            style={{ position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', opacity: globeLoaded ? 1 : 0, transition: 'opacity 600ms ease' }}
          />

          <svg className="lns" aria-hidden="true" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
            {cardStories.map((s: any) => (
              <path key={s.n} ref={el => { lineRefs.current[s.n] = el; }} stroke="rgba(255,255,255,0.22)" strokeWidth="1" strokeDasharray="2 3" fill="none" style={{ display: 'none' }} />
            ))}
          </svg>

          <div className="story-cards-layer" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
            {cardStories.map((s: any) => {
              const film = s.film;
              return (
                <a
                  key={s.n}
                  href={film ? `/films/${film.id}` : undefined}
                  ref={el => { cardRefs.current[s.n] = el as unknown as HTMLDivElement; }}
                  className="lb"
                  onClick={e => {
                    e.preventDefault();
                    if (film && onSelectFilmForPanel) onSelectFilmForPanel(film.id);
                    else if (film) navigate(`/films/${film.id}`);
                  }}
                  style={{ left: 0, top: 0, display: 'none', pointerEvents: 'auto', cursor: 'pointer', willChange: 'transform', textDecoration: 'none', color: 'inherit' }}
                >
                  {film?.video?.url ? (
                    <video src={`${film.video.url}#t=0.5`} preload="metadata" muted playsInline style={{ width: 44, height: 58, borderRadius: 8, objectFit: 'cover', flexShrink: 0 }} />
                  ) : (
                    <div className="noposter"><FilmStrip size={20} weight="duotone" /></div>
                  )}
                  <div>
                    <span className="pl">{s.n} · {s.y}</span>
                    <b>{film?.title || s.n}</b>
                    {film && <Chip status={film.status} />}
                  </div>
                </a>
              );
            })}
          </div>

          <div className="tags-layer" aria-hidden="true" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
            {tagStories.map((s: any) => (
              <div key={s.n} ref={el => { tagRefs.current[s.n] = el; }} className="tag2" style={{ left: 0, top: 0, opacity: 0, willChange: 'transform' }}>
                {s.n} <span>{s.y}</span>
              </div>
            ))}
          </div>
        </div>

        <div ref={textRef} className="hero" style={{ willChange: 'transform, opacity' }}>
          <div className="pname">
            <Mark size={30} />
            <span>Candela Studio</span>
          </div>
          <h1>
            History,<br className="mobile-break" /> <span className="serif">in motion.</span>
          </h1>
          <p>Short films about true stories. Researched, checked and painted for you.</p>
          <div className="ctas">
            <button onClick={() => navigate('/app')} className="btn pri" style={{ height: 44, padding: '0 22px', fontSize: 15, borderRadius: 999, cursor: 'pointer' }}>
              Make a film
            </button>
            <a
              href={newestFilm ? `/films/${newestFilm.id}` : '/films'}
              onClick={e => { e.preventDefault(); navigate(newestFilm ? `/films/${newestFilm.id}` : '/films'); }}
              className="lnk"
            >
              <span>Watch a film</span>
              <CaretRight size={13} weight="bold" />
            </a>
          </div>
        </div>

        <div className="foot">
          <div><b>{filmsMade || '—'}</b><span>films made</span></div>
          <i />
          <div><b>{filmsMade ? factsChecked : '—'}</b><span>facts checked</span></div>
          <i />
          <div><b>{storiesQueued || '—'}</b><span>stories queued</span></div>
          <i />
          <div><b>$0</b><span>to run</span></div>
        </div>

        <div className="scroll"><span />Scroll</div>
      </div>
    </section>
  );
};
