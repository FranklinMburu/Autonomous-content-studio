import React from 'react';
import { Archive, ArrowSquareOut, Users, MapPin, MusicNotes } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const MemoryView: React.FC = () => {
  const { memorySeedData } = useStudio();

  // Real data: episodes/hidden_reasons/memory_seed.json (what earlier films already used), never invented lists.
  const eps: any[] = Array.isArray(memorySeedData?.episodes) ? memorySeedData.episodes : [];
  const cast = eps.flatMap(e => Object.entries(e.cast || {}).map(([role, desc]) => ({ role, desc: String(desc), ep: e.episode })));
  const places = eps.map(e => ({ topic: e.topic, shots: (e.places || []).length, ep: e.episode }));
  const music = eps.filter(e => e.music).map(e => ({ track: String(e.music).replace(/\.mp3$/i, ''), ep: e.episode }));
  const epNo = (ep: string) => (ep || '').slice(0, 3);
  const empty = (txt: string) => <div style={{ fontSize: '13px', color: 'var(--tx3)' }}>{memorySeedData ? txt : 'Loading from GitHub…'}</div>;

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <div>
          <h1 className="pt">Channel Memory</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            What earlier films already used (faces, scenes, music), so the next film doesn't repeat them.
          </p>
        </div>
        <a
          href="https://github.com/FranklinMburu/Autonomous-content-studio/releases/tag/channel-memory"
          target="_blank"
          rel="noopener noreferrer"
          className="btn sec"
          style={{ height: '34px', fontSize: '12.5px', textDecoration: 'none' }}
        >
          <span>Latest memory on GitHub</span>
          <ArrowSquareOut size={13} />
        </a>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '18px' }}>
        {/* Cast list */}
        <div
          style={{
            padding: '20px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
            <Users size={18} color="var(--amber2)" weight="duotone" />
            <b style={{ fontSize: '15px' }}>Cast already used</b>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {cast.length === 0 && empty('No cast saved yet.')}
            {cast.map((item: any, i: number) => (
              <div
                key={i}
                style={{
                  padding: '8px 12px',
                  borderRadius: '8px',
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid var(--line)',
                  fontSize: '13px',
                  color: 'var(--tx)',
                }}
              >
                <b style={{ textTransform: 'capitalize' }}>{item.role}</b> <span style={{ color: 'var(--tx3)' }}>· ep {epNo(item.ep)}</span>
                <div style={{ color: 'var(--tx2)', fontSize: '12px', marginTop: '3px', lineHeight: 1.45 }}>{item.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Places list */}
        <div
          style={{
            padding: '20px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
            <MapPin size={18} color="var(--amber2)" weight="duotone" />
            <b style={{ fontSize: '15px' }}>Stories and painted shots</b>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {places.length === 0 && empty('No stories saved yet.')}
            {places.map((item: any, i: number) => (
              <div
                key={i}
                style={{
                  padding: '8px 12px',
                  borderRadius: '8px',
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid var(--line)',
                  fontSize: '13px',
                  color: 'var(--tx)',
                }}
              >
                {item.topic}
                <div style={{ color: 'var(--tx3)', fontSize: '12px', marginTop: '3px' }}>ep {epNo(item.ep)} · {item.shots} shot prompts saved</div>
              </div>
            ))}
          </div>
        </div>

        {/* Music list */}
        <div
          style={{
            padding: '20px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
            <MusicNotes size={18} color="var(--amber2)" weight="duotone" />
            <b style={{ fontSize: '15px' }}>Music already used</b>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {music.length === 0 && empty('No music saved yet.')}
            {music.map((item: any, i: number) => (
              <div
                key={i}
                style={{
                  padding: '8px 12px',
                  borderRadius: '8px',
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid var(--line)',
                  fontSize: '13px',
                  color: 'var(--tx)',
                }}
              >
                {item.track} <span style={{ color: 'var(--tx3)' }}>· ep {epNo(item.ep)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
