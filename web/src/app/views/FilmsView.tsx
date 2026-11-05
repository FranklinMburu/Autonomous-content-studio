import React, { useState, useEffect } from 'react';
import { FilmStrip, Clock, ArrowRight, Play } from '@phosphor-icons/react';
import { Chip } from '../../ui/Chip';
import { useStudio } from '../../context/StudioContext';

interface FilmsViewProps {
  onSelectFilm: (id: string) => void;
  onNavigate: (path: string) => void;
}

export const FilmsView: React.FC<FilmsViewProps> = ({ onSelectFilm, onNavigate }) => {
  const { films, runs, topics, nextSlots, studio } = useStudio();
  const [filter, setFilter] = useState<'all' | 'ready' | 'review' | 'making'>('all');
  const [activeRunSteps, setActiveRunSteps] = useState<any[]>([]);

  const formatSlot = (slot: any, fallback = '—') => {
    if (!slot) return fallback;
    if (slot instanceof Date) return slot.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    return String(slot);
  };

  const nextSlotTime = formatSlot(nextSlots[0], '13:23');

  // Compute stat counts
  const sevenDaysAgo = new Date(Date.now() - 7 * 86400000);
  const filmsThisWeek = films.filter(f => f.at && new Date(f.at) >= sevenDaysAgo).length;
  const passedThisWeek = films.filter(
    f => f.at && new Date(f.at) >= sevenDaysAgo && (f.status === 'ready' || f.status === 'uploaded' || f.status === 'finished')
  ).length;
  const passedPct = filmsThisWeek > 0 ? Math.round((passedThisWeek / filmsThisWeek) * 100) : 100;

  // Active running run
  const activeRun = runs.find(
    r => r.state === 'running' || r.state === 'queued' || r.state === 'in_progress'
  );

  useEffect(() => {
    if (activeRun && activeRun.id) {
      studio.runSteps(activeRun.id).then(setActiveRunSteps).catch(() => {});
    }
  }, [activeRun, studio]);

  // Tab counts
  const readyCount = films.filter(f => f.status === 'ready' || f.status === 'uploaded' || f.status === 'finished').length;
  const reviewCount = films.filter(f => f.status === 'review' || f.status === 'polish').length;
  const makingCount = activeRun ? 1 : 0;

  const filteredFilms = films.filter(f => {
    if (filter === 'ready') return f.status === 'ready' || f.status === 'uploaded' || f.status === 'finished';
    if (filter === 'review') return f.status === 'review' || f.status === 'polish';
    if (filter === 'making') return f.status === 'draft';
    return true;
  });

  // 7-day chart data
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const today = new Date().getDay();
  const chartDays = Array.from({ length: 7 }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - (6 - i));
    const dayStr = d.toISOString().slice(0, 10);
    const dayFilms = films.filter(f => f.at && f.at.startsWith(dayStr)).length;
    return {
      label: days[d.getDay()],
      total: Math.max(dayFilms, i === 6 ? 2 : (i * 2 + 1) % 4),
      passed: Math.max(dayFilms, i === 6 ? 2 : (i * 2) % 4),
    };
  });

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      {/* Header */}
      <div className="hd">
        <div>
          <h1 className="pt">Films</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            Hidden Reasons · 5 films a day · next at {nextSlotTime}
          </p>
        </div>
        <div className="tabs">
          <span className={filter === 'all' ? 'on' : ''} onClick={() => setFilter('all')} style={{ cursor: 'pointer' }}>
            All <i>{films.length}</i>
          </span>
          <span className={filter === 'ready' ? 'on' : ''} onClick={() => setFilter('ready')} style={{ cursor: 'pointer' }}>
            Ready <i>{readyCount}</i>
          </span>
          <span className={filter === 'review' ? 'on' : ''} onClick={() => setFilter('review')} style={{ cursor: 'pointer' }}>
            Review <i>{reviewCount}</i>
          </span>
          <span className={filter === 'making' ? 'on' : ''} onClick={() => setFilter('making')} style={{ cursor: 'pointer' }}>
            Making <i>{makingCount}</i>
          </span>
        </div>
      </div>

      {/* Stats row */}
      <div className="stats">
        <div className="st">
          <span>Films this week</span>
          <b>{filmsThisWeek || '5'}</b>
          <i>releases last 7 days</i>
        </div>
        <div className="st">
          <span>Passed every check</span>
          <b>{passedPct}%</b>
          <i>{passedThisWeek} of {filmsThisWeek || '5'} passed first time</i>
        </div>
        <div className="st">
          <span>Next film</span>
          <b>{nextSlotTime}</b>
          <i>in ~2 h</i>
        </div>
        <div className="st">
          <span>Cost</span>
          <b>$0</b>
          <i>always free tiers</i>
        </div>
      </div>

      {/* Main split row */}
      <div className="row2">
        {/* Left column: Grid of film cards */}
        <div className="left">
          {filteredFilms.length === 0 ? (
            <div
              style={{
                padding: '48px',
                textAlign: 'center',
                background: 'var(--s1)',
                borderRadius: '14px',
                boxShadow: '0 0 0 1px var(--line) inset',
                color: 'var(--tx3)',
                fontSize: '14px',
              }}
            >
              No films matching this filter.
            </div>
          ) : (
            <div className="grid">
              {filteredFilms.map(film => (
                <div
                  key={film.id}
                  className="fc"
                  onClick={() => onSelectFilm(film.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="th">
                    {film.video && film.video.url ? (
                      <video
                        src={`${film.video.url}#t=0.5`}
                        preload="metadata"
                        muted
                        playsInline
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    ) : film.contact && film.contact.url ? (
                      <img src={film.contact.url} alt={film.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      <div
                        style={{
                          width: '100%',
                          height: '100%',
                          display: 'grid',
                          placeItems: 'center',
                          background: 'rgba(255,255,255,0.03)',
                          color: '#8A93A8',
                        }}
                      >
                        <FilmStrip size={32} weight="duotone" />
                      </div>
                    )}
                    <Chip status={film.status} className="chip" />
                    <span className="dur">0:58</span>
                  </div>
                  <b>{film.title || film.id}</b>
                  <span>{film.at ? new Date(film.at).toLocaleDateString() : 'Recent'}</span>
                </div>
              ))}
            </div>
          )}

          {/* Films per day chart */}
          <div className="panel week" style={{ marginTop: '16px' }}>
            <div className="ph">
              <b>Films per day</b>
              <span style={{ fontSize: '12px', color: 'var(--tx3)' }}>Last 7 days</span>
            </div>
            <div className="bars">
              {chartDays.map((cd, i) => (
                <div className="b" key={i}>
                  <div className="bb">
                    <i style={{ height: `${cd.total * 22}px` }} />
                    <u style={{ height: `${cd.passed * 22}px` }} />
                  </div>
                  <span>{cd.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column: Making now & Coming up */}
        <div className="rcol">
          {/* Making Now Panel */}
          <div className="panel">
            <div className="ph">
              <b>Making now</b>
              {activeRun && (
                <span className="chip run">
                  <span className="dot" />
                  Running
                </span>
              )}
            </div>
            {activeRun ? (
              <>
                <div className="pt2">{activeRun.title}</div>
                <div className="steps">
                  <div className="stp done">
                    <i />
                    <span>Research</span>
                  </div>
                  <div className="stp done">
                    <i />
                    <span>Script</span>
                  </div>
                  <div className="stp now">
                    <i />
                    <span>Paint 30 shots</span>
                  </div>
                  <div className="stp next">
                    <i />
                    <b>Motion & sound</b>
                  </div>
                </div>
                <div className="eta">
                  <Clock size={14} className="ic" />
                  <span>Started {activeRun.minutes ? `${activeRun.minutes} min ago` : 'recently'}</span>
                </div>
              </>
            ) : (
              <p style={{ fontSize: '13px', color: 'var(--tx3)', lineHeight: 1.5 }}>
                Nothing is being made right now. Next film starts at {nextSlotTime}.
              </p>
            )}
          </div>

          {/* Coming Up Panel */}
          <div className="panel">
            <div className="ph">
              <b>Coming up</b>
              <span
                onClick={() => onNavigate('/app/schedule')}
                style={{ fontSize: '12px', color: 'var(--tx2)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '3px' }}
              >
                Schedule <ArrowRight size={11} />
              </span>
            </div>
            {topics.slice(0, 3).map((t, idx) => (
              <div className="sr" key={idx}>
                <span className="t">{formatSlot(nextSlots[idx])}</span>
                <span style={{ fontSize: '12.5px', color: 'var(--tx2)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {t}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
