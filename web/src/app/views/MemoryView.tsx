import React from 'react';
import { Archive, ArrowSquareOut, Users, MapPin, MusicNotes } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const MemoryView: React.FC = () => {
  const { memorySeedData } = useStudio();

  const cast = memorySeedData?.cast || ['Ignaz Semmelweis', 'Joseph Lister', 'John Snow', 'Louis Pasteur'];
  const places = memorySeedData?.places || ['Vienna General Hospital', 'Glasgow Royal Infirmary', 'Soho Broad Street, London'];
  const music = memorySeedData?.music || ['Melancholic cello', 'Tense string quartet', '19th century medical hall atmosphere'];

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <div>
          <h1 className="pt">Channel Memory</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            Prevents repeating the same faces, places and soundtrack across adjacent films.
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
            <b style={{ fontSize: '15px' }}>Cast already featured</b>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
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
                {typeof item === 'string' ? item : item.name || item.character || 'Cast member'}
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
            <b style={{ fontSize: '15px' }}>Historical locations used</b>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
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
                {typeof item === 'string' ? item : item.place || item.name || 'Location'}
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
            <b style={{ fontSize: '15px' }}>Music tracks selected</b>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
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
                {typeof item === 'string' ? item : item.title || item.mood || 'Theme'}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
