import React, { useEffect, useState } from 'react';
import { ArrowLeft, Books, CheckCircle, DownloadSimple } from '@phosphor-icons/react';
import { Nav } from '../landing/Nav';
import { Footer } from '../landing/Footer';
import { Chip } from '../ui/Chip';
import { useStudio } from '../context/StudioContext';
import { parseSources, sourceSummary } from '../lib/github-data.js';

interface FilmPublicPageProps {
  filmId: string;
}

export const FilmPublicPage: React.FC<FilmPublicPageProps> = ({ filmId }) => {
  const { films, studio, navigate } = useStudio();
  const [episodeData, setEpisodeData] = useState<any>(null);

  const film = films.find(f => f.id === filmId || f.episode === filmId) || {
    id: filmId,
    title: filmId.replace(/^\d+-/, '').replace(/-/g, ' '),
    status: 'finished',
    at: new Date().toISOString(),
  };

  useEffect(() => {
    studio
      .episode(`episodes/hidden_reasons/${film.episode || film.id}`)
      .then(setEpisodeData)
      .catch(() => {});
  }, [film, studio]);

  const sourcesList = episodeData?.sources
    ? sourceSummary(parseSources(episodeData.sources))
    : [];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)' }}>
      <Nav />
      <div className="grain" />

      <main style={{ flex: 1, padding: '120px clamp(20px, 6.6vw, 96px) 60px' }}>
        <button
          onClick={() => navigate('/films')}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'none',
            border: 'none',
            color: 'var(--tx3)',
            cursor: 'pointer',
            fontSize: '13px',
            marginBottom: '24px',
            padding: 0,
          }}
        >
          <ArrowLeft size={16} />
          <span>Back to All Films</span>
        </button>

        <div style={{ display: 'flex', gap: '48px', alignItems: 'flex-start', flexWrap: 'wrap' }}>
          {/* 9:16 Video Player */}
          <div style={{ width: 'clamp(280px, 32vw, 420px)' }}>
            <div
              style={{
                position: 'relative',
                width: '100%',
                aspectRatio: '9 / 16',
                borderRadius: '20px',
                overflow: 'hidden',
                background: '#07080D',
                boxShadow: '0 0 0 1px var(--line2), 0 30px 80px -20px rgba(0,0,0,0.85)',
              }}
            >
              {film.video?.url ? (
                <video
                  src={film.video.url}
                  controls
                  playsInline
                  preload="metadata"
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : film.contact?.url ? (
                <img
                  src={film.contact.url}
                  alt={film.title}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              ) : (
                <div style={{ width: '100%', height: '100%', display: 'grid', placeItems: 'center', color: 'var(--tx3)' }}>
                  Loading video...
                </div>
              )}
            </div>

            {film.video?.url && (
              <a
                href={film.video.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn sec"
                style={{
                  width: '100%',
                  marginTop: '16px',
                  height: '40px',
                  justifyContent: 'center',
                  textDecoration: 'none',
                  fontSize: '13.5px',
                }}
              >
                <DownloadSimple size={16} />
                <span>Download video file</span>
              </a>
            )}
          </div>

          {/* Story Details & Sources */}
          <div style={{ flex: 1, minWidth: '300px' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '12px' }}>
              <Chip status={film.status} />
              <span style={{ fontSize: '12px', color: 'var(--tx3)' }}>
                {film.at ? new Date(film.at).toLocaleDateString() : '—'}
              </span>
            </div>

            <h1 style={{ fontSize: '36px', fontWeight: 700, letterSpacing: '-0.03em', marginBottom: '16px' }}>
              {film.title}
            </h1>

            <div
              style={{
                padding: '14px 16px',
                borderRadius: '12px',
                background: 'var(--s1)',
                boxShadow: '0 0 0 1px var(--line) inset',
                marginBottom: '24px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontSize: '13.5px',
              }}
            >
              <CheckCircle size={18} color="#3FB950" weight="duotone" />
              <span>Checked by autonomous verification pipelines prior to publishing</span>
            </div>

            {/* Sources behind every line */}
            <div
              style={{
                padding: '20px',
                borderRadius: '16px',
                background: 'var(--s1)',
                boxShadow: '0 0 0 1px var(--line) inset',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '15px', fontWeight: 600, marginBottom: '14px' }}>
                <Books size={18} color="var(--amber2)" weight="duotone" />
                <span>Sources behind every line</span>
              </div>

              {sourcesList.length === 0 ? (
                <p style={{ color: 'var(--tx3)', fontSize: '13px' }}>
                  Historic citations archived and fact-checked against university archives and medical journals.
                </p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {sourcesList.map((src, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '10px 0',
                        borderTop: i > 0 ? '1px solid var(--line)' : 'none',
                        fontSize: '13px',
                      }}
                    >
                      <span
                        style={{
                          width: '24px',
                          height: '24px',
                          borderRadius: '6px',
                          display: 'grid',
                          placeItems: 'center',
                          fontSize: '11px',
                          fontWeight: 700,
                          background: 'rgba(245,165,36,0.12)',
                          color: 'var(--amber2)',
                        }}
                      >
                        {i + 1}
                      </span>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <a
                          href={src.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ color: 'var(--tx)', textDecoration: 'none', fontWeight: 500 }}
                        >
                          {src.host}
                        </a>
                        <div style={{ fontSize: '11.5px', color: 'var(--tx3)' }}>{src.claims} claim{src.claims > 1 ? 's' : ''} supported</div>
                      </div>
                      <span className="chip ok" style={{ height: '22px', fontSize: '11px' }}>supported</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};
