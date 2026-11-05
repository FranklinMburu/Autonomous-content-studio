import React from 'react';
import { LightbulbFilament, ArrowSquareOut, MapPin } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';
import placesData from '../../lib/places.json';

export const TopicsView: React.FC = () => {
  const { topics, films, studio } = useStudio();

  const getPlaceInfo = (topic: string) => {
    const p = placesData.topics.find(t => topic.toLowerCase().includes(t.match.toLowerCase()));
    return p && p.name ? `${p.name} · ${p.year}` : null;
  };

  const isMade = (topic: string) => {
    return films.some(f => (f.title || '').toLowerCase().includes(topic.toLowerCase().split(' ').slice(1, 3).join(' ')));
  };

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <div>
          <h1 className="pt">Topics</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            Queue of true stories · When fewer than 5 are left, the free models suggest new ones.
          </p>
        </div>
        <a
          href={studio.links.topicsFile()}
          target="_blank"
          rel="noopener noreferrer"
          className="btn pri"
          style={{ height: '34px', fontSize: '13px', textDecoration: 'none' }}
        >
          <span>Edit topics</span>
          <ArrowSquareOut size={14} />
        </a>
      </div>

      <div
        style={{
          borderRadius: '16px',
          background: 'var(--s1)',
          boxShadow: '0 0 0 1px var(--line) inset',
          overflow: 'hidden',
        }}
      >
        {topics.length === 0 ? (
          <div style={{ padding: '36px', textAlign: 'center', color: 'var(--tx3)', fontSize: '13.5px' }}>
            Loading topic queue...
          </div>
        ) : (
          topics.map((t, idx) => {
            const place = getPlaceInfo(t);
            const made = isMade(t);
            return (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  padding: '14px 20px',
                  borderTop: idx > 0 ? '1px solid var(--line)' : 'none',
                  fontSize: '13.5px',
                }}
              >
                <span
                  style={{
                    fontVariantNumeric: 'tabular-nums',
                    fontSize: '12px',
                    color: 'var(--amber2)',
                    fontWeight: 700,
                    width: '28px',
                  }}
                >
                  {String(idx + 1).padStart(2, '0')}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <b style={{ color: 'var(--tx)', fontWeight: 550 }}>{t}</b>
                  {place && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11.5px', color: 'var(--tx3)', marginTop: '2px' }}>
                      <MapPin size={12} color="var(--amber2)" />
                      <span>{place}</span>
                    </div>
                  )}
                </div>
                {made ? (
                  <span className="chip ok" style={{ height: '22px', fontSize: '11px' }}>
                    Film made
                  </span>
                ) : (
                  <span
                    style={{
                      fontSize: '11px',
                      color: 'var(--tx3)',
                      padding: '2px 8px',
                      borderRadius: '99px',
                      background: 'rgba(255,255,255,0.04)',
                    }}
                  >
                    Queued
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
