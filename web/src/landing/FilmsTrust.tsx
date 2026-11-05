import React, { useState } from 'react';
import {
  PlayCircle,
  Books,
  Eye,
  HandPalm,
  CurrencyDollar,
} from '@phosphor-icons/react';
import { useStudio } from '../context/StudioContext';

export const FilmsTrust: React.FC = () => {
  const { films, navigate } = useStudio();
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  // Take up to 5 finished or available films
  const displayFilms = films.slice(0, 5);
  // Fallbacks if not enough films loaded yet
  const fallbackStills = [
    { title: 'Why Doctors Were Ordered to Wash Their Hands', img: '/img/hook.jpg', dur: '0:58' },
    { title: "Why a Surgeon Wrapped a Boy's Leg in Acid", img: '/img/lister2c.jpg', dur: '0:52' },
    { title: 'Women begged on their knees', img: '/img/begging.jpg', dur: 'clip' },
    { title: "Pasteur's germ theory", img: '/img/pasteur.jpg', dur: 'clip' },
    { title: 'Born in the street', img: '/img/street.jpg', dur: 'clip' },
  ];

  return (
    <section
      className="films-trust-sec"
      style={{
        position: 'relative',
        minHeight: '900px',
        width: '100%',
        overflow: 'hidden',
      }}
    >
      <div className="grain" />

      <div style={{ maxWidth: '1440px', margin: '0 auto', height: '100%', minHeight: '900px', position: 'relative' }}>
        {/* Header */}
        <div className="fhead">
          <div className="eyebrow">Made with Candela</div>
          <h2>
            Real films. <span className="serif">Not slideshows.</span>
          </h2>
        </div>

        {/* 5 Film Cards Gallery */}
        <div className="fgal">
          {(displayFilms.length >= 3 ? displayFilms : fallbackStills).map((item: any, idx) => {
            const isHovered = hoveredIdx === idx;
            const isFirst = idx === 0;
            const imgSrc = item.img || item.contact?.url || item.video?.poster || '/img/hook.jpg';
            const videoUrl = item.video?.url;
            const title = item.title || item.name;

            return (
              <div
                key={idx}
                className={`fv ${isFirst ? 'big' : ''}`}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
                onClick={() => {
                  if (item.id) navigate(`/films/${item.id}`);
                  else navigate('/films');
                }}
                style={{
                  cursor: 'pointer',
                  transform: isHovered ? 'translateY(-4px)' : 'none',
                  transition: 'transform 200ms ease, box-shadow 200ms ease',
                }}
              >
                {videoUrl && isHovered ? (
                  <video
                    src={videoUrl}
                    autoPlay
                    muted
                    loop
                    playsInline
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  <img src={imgSrc} alt={title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                )}

                <div className="fo">
                  <b>{title}</b>
                  <span>
                    <PlayCircle size={15} weight="duotone" className="ic" />
                    {item.dur || '0:58'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* 4 Guardrails */}
        <div className="guards">
          <div className="gd">
            <Books size={22} weight="duotone" className="ic" />
            <b>Every claim has a source</b>
            <p>A second AI checks each sentence against the saved sources.</p>
          </div>
          <div className="gd">
            <Eye size={22} weight="duotone" className="ic" />
            <b>Every picture is checked</b>
            <p>A vision model rejects wrong poses, text and modern objects, then repaints.</p>
          </div>
          <div className="gd">
            <HandPalm size={22} weight="duotone" className="ic" />
            <b>You stay in control</b>
            <p>Weak films are held for review. Nothing is ever posted for you.</p>
          </div>
          <div className="gd">
            <CurrencyDollar size={22} weight="duotone" className="ic" />
            <b>Free to run</b>
            <p>Free AI models, free GPUs, free hosting. $0 a month.</p>
          </div>
        </div>

        {/* Final CTA band */}
        <div className="cta">
          <div className="ctx">
            <h3>Your first film is one topic away.</h3>
            <button
              onClick={() => navigate('/app')}
              className="btn pri"
              style={{ height: '44px', padding: '0 22px', fontSize: '15px', cursor: 'pointer' }}
            >
              Start free
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};
