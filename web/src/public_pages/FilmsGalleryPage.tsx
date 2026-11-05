import React from 'react';
import { PlayCircle, FilmStrip } from '@phosphor-icons/react';
import { Nav } from '../landing/Nav';
import { Footer } from '../landing/Footer';
import { Chip } from '../ui/Chip';
import { useStudio } from '../context/StudioContext';

export const FilmsGalleryPage: React.FC = () => {
  const { films, navigate } = useStudio();
  const finishedFilms = films.filter(
    f => f.status === 'ready' || f.status === 'uploaded' || f.status === 'finished'
  );

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)' }}>
      <Nav />
      <div className="grain" />

      <main style={{ flex: 1, padding: '120px clamp(20px, 6.6vw, 96px) 60px' }}>
        <div style={{ marginBottom: '36px' }}>
          <div className="eyebrow">Public Gallery</div>
          <h1 style={{ fontSize: '42px', fontWeight: 700, letterSpacing: '-0.03em', marginTop: '8px' }}>
            Finished Films
          </h1>
          <p style={{ color: 'var(--tx2)', fontSize: '16px', marginTop: '6px' }}>
            History in motion. True stories researched, checked and painted.
          </p>
        </div>

        {finishedFilms.length === 0 ? (
          <div
            style={{
              padding: '60px',
              textAlign: 'center',
              borderRadius: '16px',
              background: 'var(--s1)',
              boxShadow: '0 0 0 1px var(--line) inset',
              color: 'var(--tx3)',
            }}
          >
            <FilmStrip size={40} weight="duotone" style={{ margin: '0 auto 12px' }} />
            <p>Loading films from GitHub releases...</p>
          </div>
        ) : (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
              gap: '24px',
            }}
          >
            {finishedFilms.map(film => (
              <div
                key={film.id}
                onClick={() => navigate(`/films/${film.id}`)}
                style={{
                  cursor: 'pointer',
                  borderRadius: '16px',
                  overflow: 'hidden',
                  background: 'var(--s1)',
                  boxShadow: '0 0 0 1px var(--line) inset',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 200ms ease',
                }}
              >
                <div style={{ position: 'relative', width: '100%', height: '340px', overflow: 'hidden' }}>
                  {film.video?.url ? (
                    <video
                      src={`${film.video.url}#t=0.5`}
                      preload="metadata"
                      muted
                      playsInline
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : film.contact?.url ? (
                    <img
                      src={film.contact.url}
                      alt={film.title}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : (
                    <div
                      style={{
                        width: '100%',
                        height: '100%',
                        display: 'grid',
                        placeItems: 'center',
                        color: 'var(--tx3)',
                      }}
                    >
                      <FilmStrip size={36} weight="duotone" />
                    </div>
                  )}
                  <Chip
                    status={film.status}
                    style={{ position: 'absolute', top: '10px', left: '10px' }}
                  />
                  <div
                    style={{
                      position: 'absolute',
                      inset: 0,
                      background: 'rgba(0,0,0,0.2)',
                      display: 'grid',
                      placeItems: 'center',
                      opacity: 0.8,
                    }}
                  >
                    <PlayCircle size={44} weight="duotone" color="#FFF" />
                  </div>
                </div>

                <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <b style={{ fontSize: '14.5px', color: 'var(--tx)' }}>{film.title}</b>
                  <span style={{ fontSize: '12px', color: 'var(--tx3)' }}>
                    {film.at ? new Date(film.at).toLocaleDateString() : '—'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};
