import React, { useState, useRef, useEffect } from 'react';
import { Lock, CaretRight } from '@phosphor-icons/react';
import { AppShell } from '../app/AppShell';
import { useStudio } from '../context/StudioContext';

interface StudioPanelProps {
  embeddedRoute: string;
  onEmbeddedRouteChange: (r: string) => void;
}

export const StudioPanel: React.FC<StudioPanelProps> = ({
  embeddedRoute,
  onEmbeddedRouteChange,
}) => {
  const { navigate } = useStudio();
  const [hintsVisible, setHintsVisible] = useState(true);
  const [scale, setScale] = useState(0.8611);
  const containerRef = useRef<HTMLDivElement>(null);
  const frameRef = useRef<HTMLDivElement>(null);
  const [inView, setInView] = useState(false);

  // Resize calculation to keep scaling crisp
  useEffect(() => {
    const updateScale = () => {
      if (frameRef.current) {
        const frameW = frameRef.current.clientWidth;
        setScale(frameW / 1440);
      }
    };
    updateScale();
    window.addEventListener('resize', updateScale);
    return () => window.removeEventListener('resize', updateScale);
  }, []);

  // Intersection observer for entrance
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting) {
          setInView(true);
        }
      },
      { threshold: 0.2 }
    );
    if (containerRef.current) observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const handleFirstClick = () => {
    setHintsVisible(false);
  };

  const getUrlPath = () => {
    return embeddedRoute.replace('/app', '') || '/films';
  };

  const isSegmentActive = (seg: string) => {
    return embeddedRoute.includes(seg.toLowerCase());
  };

  return (
    <section
      id="studio-panel-section"
      ref={containerRef}
      className="sheet"
      style={{
        position: 'relative',
        minHeight: '1080px',
        width: '100%',
        paddingBottom: '60px',
      }}
    >
      <div className="sunres" />

      {/* Section Title */}
      <div className="ptitle">
        <div className="eyebrow">Inside the studio</div>
        <h2>
          Take a look <span className="serif">inside.</span>
        </h2>
        <p>This is the real studio, live. Click anything.</p>
      </div>

      {/* Frame Container */}
      <div
        ref={frameRef}
        className="frame"
        style={{
          width: 'clamp(340px, 86vw, 1240px)',
          height: 'clamp(500px, 56vw, 806px)',
          left: '50%',
          transform: `translateX(-50%) ${inView ? 'translateY(0) scale(1)' : 'translateY(48px) scale(0.97)'}`,
          opacity: inView ? 1 : 0,
          transition: 'transform 700ms cubic-bezier(0.2, 0.7, 0.2, 1), opacity 700ms ease',
        }}
        onClick={handleFirstClick}
      >
        {/* Top Browser Bar */}
        <div className="fbar">
          <i />
          <i />
          <i />

          {/* URL Pill */}
          <div className="url">
            <Lock size={11} className="ic" />
            <span>studio.candela.film{getUrlPath()}</span>
          </div>

          {/* Segmented control: Films | Runs | Review | Polish */}
          <div className="fseg">
            <span
              className={isSegmentActive('film') ? 'on' : ''}
              onClick={() => onEmbeddedRouteChange('/app/films')}
              style={{ cursor: 'pointer' }}
            >
              Films
            </span>
            <span
              className={isSegmentActive('run') ? 'on' : ''}
              onClick={() => onEmbeddedRouteChange('/app/runs')}
              style={{ cursor: 'pointer' }}
            >
              Runs
            </span>
            <span
              className={isSegmentActive('review') ? 'on' : ''}
              onClick={() => onEmbeddedRouteChange('/app/review')}
              style={{ cursor: 'pointer' }}
            >
              Review
            </span>
            <span
              className={isSegmentActive('polish') ? 'on' : ''}
              onClick={() => onEmbeddedRouteChange('/app/polish')}
              style={{ cursor: 'pointer' }}
            >
              Polish
            </span>
          </div>
        </div>

        {/* Scaled AppShell inside frame */}
        <div
          className="fview"
          style={{
            position: 'absolute',
            top: '42px',
            left: 0,
            right: 0,
            bottom: 0,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: '1440px',
              height: '887px',
              transform: `scale(${scale})`,
              transformOrigin: '0 0',
              position: 'relative',
            }}
          >
            <AppShell
              embedded
              embeddedRoute={embeddedRoute}
              onEmbeddedRouteChange={onEmbeddedRouteChange}
              onFirstInteraction={handleFirstClick}
            />
          </div>
        </div>
      </div>

      {/* Floating Hint Pills (Fade out after first interaction) */}
      {hintsVisible && (
        <div style={{ transition: 'opacity 300ms ease', pointerEvents: 'none' }}>
          <div className="phint" style={{ left: 'clamp(20px, 32vw, 470px)', top: '515px' }}>
            <i />
            <span>Click a film to watch it</span>
          </div>
          <div className="phint" style={{ left: 'clamp(10px, 12vw, 150px)', top: '370px' }}>
            <i />
            <span>Every menu item works</span>
          </div>
          <div className="phint" style={{ left: 'clamp(40px, 72vw, 1060px)', top: '455px' }}>
            <i />
            <span>Live from our GitHub</span>
          </div>
        </div>
      )}

      {/* Panel Footer */}
      <div className="pfoot">
        <span>Live data</span>
        <i />
        <span>Read-only</span>
        <i />
        <span
          className="go"
          onClick={() => navigate('/app')}
          style={{ cursor: 'pointer' }}
        >
          <span>Make your own film</span>
          <CaretRight size={12} />
        </span>
      </div>
    </section>
  );
};
