import React from 'react';
import { UploadSimple, DownloadSimple, ArrowSquareOut, CheckCircle, VideoCamera } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const UploadView: React.FC = () => {
  const { uploadItems, uploadedItems, films, studio } = useStudio();

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <h1 className="pt">Upload</h1>
        <span style={{ fontSize: '13px', color: 'var(--tx3)' }}>
          {uploadItems.length} ready to upload
        </span>
      </div>

      {uploadItems.length === 0 ? (
        <div
          style={{
            padding: '40px',
            textAlign: 'center',
            background: 'var(--s1)',
            borderRadius: '16px',
            boxShadow: '0 0 0 1px var(--line) inset',
            color: 'var(--tx3)',
            marginBottom: '32px',
          }}
        >
          <CheckCircle size={40} color="#3FB950" weight="duotone" style={{ margin: '0 auto 12px' }} />
          <p style={{ color: 'var(--tx)', fontSize: '15px', fontWeight: 600, marginBottom: '4px' }}>
            Nothing waiting
          </p>
          <p style={{ fontSize: '13px' }}>Finished films approved by you appear here.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '36px' }}>
          {uploadItems.map(item => {
            const film = films.find(f => f.episode === item.episode || f.title === item.title);
            return (
              <div
                key={item.number}
                style={{
                  display: 'flex',
                  gap: '24px',
                  padding: '20px',
                  borderRadius: '16px',
                  background: 'var(--s1)',
                  boxShadow: '0 0 0 1px var(--line) inset',
                }}
              >
                {/* Thumbnail */}
                <div
                  style={{
                    width: '180px',
                    height: '240px',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    background: '#07080D',
                    flexShrink: 0,
                    boxShadow: '0 0 0 1px var(--line2)',
                  }}
                >
                  {film?.video?.url ? (
                    <video
                      src={film.video.url}
                      controls
                      playsInline
                      preload="metadata"
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : film?.contact?.url ? (
                    <img src={film.contact.url} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    <div style={{ width: '100%', height: '100%', display: 'grid', placeItems: 'center', color: 'var(--tx3)' }}>
                      <VideoCamera size={36} weight="duotone" />
                    </div>
                  )}
                </div>

                {/* Details & Actions */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span className="chip ok">Ready to upload</span>
                    <span style={{ fontSize: '12px', color: 'var(--tx3)' }}>Issue #{item.number}</span>
                  </div>

                  <b style={{ fontSize: '18px', marginBottom: '8px' }}>{item.title}</b>
                  <p style={{ fontSize: '13px', color: 'var(--tx2)', lineHeight: 1.5, marginBottom: '16px', flex: 1 }}>
                    Suggested description: {item.body ? item.body.slice(0, 160) + '...' : 'Short film with fact-checked sources.'}
                  </p>

                  <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                    {film?.video?.url && (
                      <a
                        href={film.video.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn sec"
                        style={{ height: '36px', fontSize: '13px', textDecoration: 'none' }}
                      >
                        <DownloadSimple size={15} />
                        <span>Download video</span>
                      </a>
                    )}
                    <a
                      href="https://studio.youtube.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn pri"
                      style={{ height: '36px', fontSize: '13px', textDecoration: 'none' }}
                    >
                      <UploadSimple size={15} />
                      <span>Open YouTube Studio</span>
                      <ArrowSquareOut size={13} />
                    </a>
                    <a
                      href={item.url || studio.links.issue(item.number)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn sec"
                      style={{ height: '36px', fontSize: '13px', textDecoration: 'none' }}
                    >
                      <span>Mark uploaded on GitHub</span>
                      <ArrowSquareOut size={13} />
                    </a>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Uploaded History */}
      <div>
        <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', color: 'var(--tx2)' }}>
          Uploaded recently
        </h2>
        {uploadedItems.length === 0 ? (
          <div style={{ color: 'var(--tx3)', fontSize: '13px', padding: '16px 0' }}>
            No uploads completed yet.
          </div>
        ) : (
          <div
            style={{
              borderRadius: '14px',
              background: 'var(--s1)',
              boxShadow: '0 0 0 1px var(--line) inset',
              overflow: 'hidden',
            }}
          >
            {uploadedItems.slice(0, 20).map((up, i) => (
              <div
                key={up.number || i}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  borderTop: i > 0 ? '1px solid var(--line)' : 'none',
                  fontSize: '13px',
                }}
              >
                <CheckCircle size={16} color="#3FB950" weight="duotone" />
                <span style={{ flex: 1, color: 'var(--tx)' }}>{up.title}</span>
                <span style={{ fontSize: '12px', color: 'var(--tx3)' }}>
                  {up.closed_at ? new Date(up.closed_at).toLocaleDateString() : 'Uploaded'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
