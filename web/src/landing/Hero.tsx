import React, { useEffect, useRef, useState } from 'react';
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

export const Hero: React.FC<HeroProps> = ({ onSelectFilmForPanel }) => {
  const { films, topics, navigate } = useStudio();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wrapRef = useRef<HTMLElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);

  const [earthInstance, setEarthInstance] = useState<any>(null);
  const [placedStories, setPlacedStories] = useState<any[]>([]);
  const [tags, setTags] = useState<any[]>([]);
  const [globeLoaded, setGlobeLoaded] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);

  // Compute numbers for numbers row
  const filmsMadeCount = films.filter(
    f => f.status === 'ready' || f.status === 'uploaded' || f.status === 'finished' || f.status === 'review'
  ).length;
  const factsCheckedCount = films.reduce((acc, f) => {
    return acc + (f.release?.sources?.length || 4);
  }, 0);
  const storiesQueuedCount = topics.length;

  // Newest finished film for "Watch a film"
  const newestFilm = films.find(f => f.video?.url) || films[0];

  useEffect(() => {
    let earth: any = null;
    let isCancelled = false;

    const initGlobe = async () => {
      try {
        const resp = await fetch('/earth.json');
        if (!resp.ok) return;
        const earthData = await resp.json();
        if (isCancelled || !canvasRef.current) return;

        const { stories, arcs } = buildGlobe(films, topics, placesData);

        earth = createEarth(canvasRef.current, earthData, stories, {
          arcs,
          onPlace: (places: any[]) => {
            setPlacedStories(places);
            // Block cards
            const cardRects = places
              .filter(p => p.card)
              .map(p => {
                const isLeft = p.card === 'left';
                const left = isLeft ? p.x - 300 : p.x + 150;
                const top = p.y - 150;
                return { l: left, t: top, r: left + 262, b: top + 86, n: p.n };
              });

            const clientW = canvasRef.current?.clientWidth || window.innerWidth;
            const isMob = clientW < 640;
            const picked = isMob
              ? pickTags(places.filter((p: any) => p.kind === 'made'), { width: clientW, maxY: 470 })
              : pickTags(places, { blocked: cardRects, width: clientW });
            setTags(picked);
          },
        });

        setEarthInstance(earth);
        setGlobeLoaded(true);
      } catch (err) {
        console.warn('Globe data load fallback:', err);
      }
    };

    initGlobe();

    return () => {
      isCancelled = true;
      if (earth) earth.destroy();
    };
  }, [films, topics]);

  // Scroll listener for sunrise progress & text parallax
  useEffect(() => {
    const handleScroll = () => {
      if (!wrapRef.current) return;
      const rect = wrapRef.current.getBoundingClientRect();
      const wrapTop = window.scrollY + rect.top;
      const p = Math.max(0, Math.min(1, (window.scrollY - wrapTop) / 800));
      setScrollProgress(p);

      if (earthInstance) {
        earthInstance.setProgress(p);
      }

      // Set CSS var --hp on stage for the sheet effect
      if (stageRef.current) {
        const hp = Math.max(0, (window.scrollY - 800) / (stageRef.current.offsetHeight || 900));
        stageRef.current.style.setProperty('--hp', String(hp));
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, [earthInstance]);

  // Card items: the two newest made films with places
  const cardStories = placedStories.filter(p => p.card);

  // Parallax calculations for the hero text
  const textTranslateY = scrollProgress * -120; // 0.25x speed over 800px approx
  const textOpacity = scrollProgress < 0.55 ? 1 : Math.max(0, 1 - (scrollProgress - 0.55) / 0.45);

  return (
    <section ref={wrapRef} className="hero-wrap" style={{ height: 'calc(100vh + 800px)', position: 'relative' }}>
      <div
        ref={stageRef}
        className="hero-stage"
        style={{
          position: 'sticky',
          top: 0,
          height: '100vh',
          overflow: 'hidden',
          width: '100%',
        }}
      >
        <div className="grain" />
        <div className="topglow" />

        {/* Hero Canvas */}
        <canvas
          ref={canvasRef}
          className="earth"
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            width: '100%',
            height: '100%',
            opacity: globeLoaded ? 1 : 0,
            transition: 'opacity 600ms ease',
          }}
        />

        {/* SVG connecting dashed lines for cards */}
        <svg
          className="lns"
          style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' }}
        >
          {cardStories.map(story => {
            const isLeft = story.card === 'left';
            const cardLeft = isLeft ? story.x - 300 : story.x + 150;
            const cardTop = story.y - 150;
            const targetX = isLeft ? cardLeft + 262 : cardLeft;
            const targetY = cardTop + 45;
            return (
              <path
                key={story.n}
                d={`M${story.x} ${story.y} L${targetX} ${targetY}`}
                stroke="rgba(255,255,255,0.22)"
                strokeWidth="1"
                strokeDasharray="2 3"
                fill="none"
              />
            );
          })}
        </svg>

        {/* Story Cards placed over globe */}
        <div className="story-cards-layer" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
          {cardStories.map(story => {
            const isLeft = story.card === 'left';
            const cardLeft = isLeft ? story.x - 300 : story.x + 150;
            const cardTop = story.y - 150;
            const film = story.film;

            return (
              <div
                key={story.n}
                className="lb"
                onClick={() => {
                  if (film && onSelectFilmForPanel) onSelectFilmForPanel(film.id);
                  else if (film) navigate(`/app/films/${film.id}`);
                }}
                style={{
                  left: `${cardLeft}px`,
                  top: `${cardTop}px`,
                  pointerEvents: 'auto',
                  cursor: 'pointer',
                }}
              >
                {film?.video?.url ? (
                  <video
                    src={`${film.video.url}#t=0.5`}
                    preload="metadata"
                    muted
                    playsInline
                    style={{ width: '44px', height: '58px', borderRadius: '8px', objectFit: 'cover', flexShrink: 0 }}
                  />
                ) : film?.contact?.url ? (
                  <img src={film.contact.url} alt={story.n} style={{ width: '44px', height: '58px', borderRadius: '8px', objectFit: 'cover', flexShrink: 0 }} />
                ) : (
                  <div className="noposter">
                    <FilmStrip size={20} weight="duotone" />
                  </div>
                )}
                <div>
                  <span className="pl">
                    {story.n} · {story.y}
                  </span>
                  <b>{film?.title || story.topic || story.n}</b>
                  <Chip status={film?.status || 'review'} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Name tags without collision */}
        <div className="tags-layer" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
          {tags.map(t => (
            <div
              key={`${t.n}-${t.year}`}
              className="tag2"
              style={{
                left: `${t.left}px`,
                top: `${t.top}px`,
              }}
            >
              {t.n} <span>{t.year}</span>
            </div>
          ))}
        </div>

        {/* Centered Hero Text Block */}
        <div
          className="hero"
          style={{
            transform: `translateY(${textTranslateY}px)`,
            opacity: textOpacity,
            pointerEvents: textOpacity <= 0.05 ? 'none' : 'auto',
            transition: 'opacity 120ms ease-out',
          }}
        >
          <div className="pname">
            <Mark size={30} />
            <span>Candela Studio</span>
          </div>

          <h1>
            History,<br className="mobile-break" /> <span className="serif">in motion.</span>
          </h1>

          <p>Short films about true stories. Researched, checked and painted for you.</p>

          <div className="ctas">
            <button
              onClick={() => navigate('/app')}
              className="btn pri"
              style={{ height: '44px', padding: '0 22px', fontSize: '15px', borderRadius: '999px', cursor: 'pointer' }}
            >
              Make a film
            </button>
            <span
              onClick={() => {
                if (newestFilm) navigate(`/films/${newestFilm.id}`);
                else navigate('/films');
              }}
              className="lnk"
              style={{ cursor: 'pointer' }}
            >
              <span>Watch a film</span>
              <CaretRight size={13} weight="bold" />
            </span>
          </div>
        </div>

        {/* Numbers Row */}
        <div className="foot">
          <div>
            <b>{filmsMadeCount || '—'}</b>
            <span>films made</span>
          </div>
          <i />
          <div>
            <b>{factsCheckedCount || '—'}</b>
            <span>facts checked</span>
          </div>
          <i />
          <div>
            <b>{storiesQueuedCount || '—'}</b>
            <span>stories queued</span>
          </div>
          <i />
          <div>
            <b>$0</b>
            <span>to run</span>
          </div>
        </div>

        {/* Scroll Cue */}
        <div className="scroll">
          <span />
          Scroll
        </div>
      </div>
    </section>
  );
};
