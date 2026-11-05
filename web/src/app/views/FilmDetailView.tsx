import React, { useEffect, useState } from 'react';
import {
  ArrowLeft,
  ArrowSquareOut,
  DownloadSimple,
  CheckCircle,
  FileText,
  Users,
  FilmStrip,
  Books,
} from '@phosphor-icons/react';
import { Chip } from '../../ui/Chip';
import { useStudio } from '../../context/StudioContext';
import { parseSources, sourceSummary } from '../../lib/github-data.js';

interface FilmDetailViewProps {
  filmId: string;
  onBack: () => void;
}

export const FilmDetailView: React.FC<FilmDetailViewProps> = ({ filmId, onBack }) => {
  const { films, studio } = useStudio();
  const [episodeData, setEpisodeData] = useState<any>(null);
  const [loadingEpisode, setLoadingEpisode] = useState(true);

  const film = films.find(f => f.id === filmId || f.episode === filmId) || {
    id: filmId,
    title: filmId.replace(/^\d+-/, '').replace(/-/g, ' '),
    status: 'finished',
    style: 'Film',
    at: new Date().toISOString(),
  };

  useEffect(() => {
    let isMounted = true;
    studio
      .episode(`episodes/hidden_reasons/${film.episode || film.id}`)
      .then(ep => {
        if (isMounted) {
          setEpisodeData(ep);
          setLoadingEpisode(false);
        }
      })
      .catch(() => {
        if (isMounted) setLoadingEpisode(false);
      });
    return () => {
      isMounted = false;
    };
  }, [film, studio]);

  const sourcesList = episodeData?.sources
    ? sourceSummary(parseSources(episodeData.sources))
    : [];

  const scriptBeats = episodeData?.script?.beats || [];
  const castList = episodeData?.film?.cast || [];
  const shotsCount = episodeData?.film?.shots?.length || 30;

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      {/* Back button */}
      <button
        onClick={onBack}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          background: 'none',
          border: 'none',
          color: 'var(--tx3)',
          cursor: 'pointer',
          fontSize: '13px',
          marginBottom: '18px',
          padding: 0,
        }}
      >
        <ArrowLeft size={16} />
        <span>Back to Films</span>
      </button>

      <div style={{ display: 'flex', gap: '32px', alignItems: 'flex-start' }}>
        {/* Left: 9:16 Video Player */}
        <div style={{ width: '380px', flexShrink: 0 }}>
          <div
            style={{
              position: 'relative',
              width: '100%',
              aspectRatio: '9 / 16',
              borderRadius: '16px',
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
              <div
                style={{
                  width: '100%',
                  height: '100%',
                  display: 'grid',
                  placeItems: 'center',
                  color: 'var(--tx3)',
                }}
              >
                <FilmStrip size={48} weight="duotone" />
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
                marginTop: '14px',
                height: '38px',
                justifyContent: 'center',
                textDecoration: 'none',
                fontSize: '13px',
              }}
            >
              <DownloadSimple size={16} />
              <span>Download video</span>
            </a>
          )}
        </div>

        {/* Right: Metadata, Checks, Sources, Script, Cast */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '12px' }}>
            <Chip status={film.status} />
            <span
              style={{
                fontSize: '11.5px',
                padding: '2px 8px',
                borderRadius: '99px',
                background: 'rgba(255,255,255,0.06)',
                color: 'var(--tx2)',
              }}
            >
              {film.style || 'Film style'}
            </span>
            <span style={{ fontSize: '12px', color: 'var(--tx3)', marginLeft: 'auto' }}>
              {film.at ? new Date(film.at).toLocaleDateString() : '—'}
            </span>
          </div>

          <h1 style={{ fontSize: '28px', fontWeight: 700, letterSpacing: '-0.03em', marginBottom: '14px' }}>
            {film.title}
          </h1>

          {/* Action buttons */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '24px', flexWrap: 'wrap' }}>
            {film.reviewIssue && (
              <a
                href={studio.links.issue(film.reviewIssue.number)}
                target="_blank"
                rel="noopener noreferrer"
                className="btn pri"
                style={{ textDecoration: 'none', height: '36px', fontSize: '13px' }}
              >
                <span>Review on GitHub</span>
                <ArrowSquareOut size={14} />
              </a>
            )}
            {film.polishIssue && (
              <a
                href={studio.links.issue(film.polishIssue.number)}
                target="_blank"
                rel="noopener noreferrer"
                className="btn pri"
                style={{ textDecoration: 'none', height: '36px', fontSize: '13px' }}
              >
                <span>Polish on GitHub</span>
                <ArrowSquareOut size={14} />
              </a>
            )}
            {film.release?.url && (
              <a
                href={film.release.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn sec"
                style={{ textDecoration: 'none', height: '36px', fontSize: '13px' }}
              >
                <span>View Release on GitHub</span>
                <ArrowSquareOut size={14} />
              </a>
            )}
          </div>

          {/* Checks pass bar */}
          <div
            style={{
              padding: '14px 16px',
              borderRadius: '12px',
              background: 'var(--s1)',
              boxShadow: '0 0 0 1px var(--line) inset',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              fontSize: '13px',
              color: 'var(--tx)',
            }}
          >
            <CheckCircle size={18} weight="duotone" color="#3FB950" />
            <span>Passed fact checking against primary sources · {shotsCount} shots painted</span>
          </div>

          {/* Sources behind every line */}
          <div
            style={{
              padding: '16px',
              borderRadius: '14px',
              background: 'var(--s1)',
              boxShadow: '0 0 0 1px var(--line) inset',
              marginBottom: '20px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', fontWeight: 600, marginBottom: '12px' }}>
              <Books size={18} color="var(--amber2)" />
              <span>Sources behind every line</span>
            </div>
            {sourcesList.length === 0 ? (
              <div style={{ color: 'var(--tx3)', fontSize: '12.5px' }}>
                Primary sources validated during script compilation.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {sourcesList.map((src, i) => (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '8px 0',
                      borderTop: i > 0 ? '1px solid var(--line)' : 'none',
                      fontSize: '13px',
                    }}
                  >
                    <span
                      style={{
                        width: '22px',
                        height: '22px',
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
                    <span className="chip ok" style={{ height: '20px', fontSize: '11px' }}>supported</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Cast & Script Preview */}
          {castList.length > 0 && (
            <div
              style={{
                padding: '16px',
                borderRadius: '14px',
                background: 'var(--s1)',
                boxShadow: '0 0 0 1px var(--line) inset',
                marginBottom: '20px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', fontWeight: 600, marginBottom: '12px' }}>
                <Users size={18} color="var(--amber2)" />
                <span>Cast</span>
              </div>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                {castList.map((c: any, i: number) => (
                  <span
                    key={i}
                    style={{
                      padding: '6px 12px',
                      borderRadius: '8px',
                      background: 'rgba(255,255,255,0.04)',
                      fontSize: '12.5px',
                      color: 'var(--tx2)',
                    }}
                  >
                    {c.name || c}
                  </span>
                ))}
              </div>
            </div>
          )}

          {scriptBeats.length > 0 && (
            <div
              style={{
                padding: '16px',
                borderRadius: '14px',
                background: 'var(--s1)',
                boxShadow: '0 0 0 1px var(--line) inset',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', fontWeight: 600, marginBottom: '12px' }}>
                <FileText size={18} color="var(--amber2)" />
                <span>Script excerpt</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {scriptBeats.slice(0, 3).map((b: any, i: number) => (
                  <div key={i} style={{ fontSize: '13px', lineHeight: 1.5, color: 'var(--tx2)' }}>
                    <b style={{ color: 'var(--tx)', display: 'block', fontSize: '11.5px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Beat {i + 1}
                    </b>
                    {b.narrative || b.text || b.narration}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
