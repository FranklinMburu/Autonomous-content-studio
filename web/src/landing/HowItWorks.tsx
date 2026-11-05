import React, { useState, useEffect, useRef } from 'react';
import {
  LightbulbFilament,
  FileText,
  Palette,
  FilmReel,
  SealCheck,
  Eye,
  CheckCircle,
  Mouse,
} from '@phosphor-icons/react';

interface HowItWorksProps {
  standalone?: boolean;
}

export const HowItWorks: React.FC<HowItWorksProps> = ({ standalone = false }) => {
  const wrapRef = useRef<HTMLElement>(null);
  const [activeStep, setActiveStep] = useState(2); // Step 3 (0-indexed: 2) as in reference
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 640);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  // Pinned scroll behavior for desktop landing page
  useEffect(() => {
    if (standalone || isMobile) return;

    const handleScroll = () => {
      if (!wrapRef.current) return;
      const rect = wrapRef.current.getBoundingClientRect();
      const wrapTop = window.scrollY + rect.top;
      const progress = Math.max(0, Math.min(1, (window.scrollY - wrapTop) / (4 * 500)));
      const stepIdx = Math.min(4, Math.floor(progress * 5));
      setActiveStep(stepIdx);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [standalone, isMobile]);

  const steps = [
    { num: '01', title: 'Topic', sub: 'A true story worth a minute', icon: LightbulbFilament },
    { num: '02', title: 'Script', sub: 'Written, then every claim checked', icon: FileText },
    { num: '03', title: '30 painted shots', sub: 'Same faces in every shot', icon: Palette },
    { num: '04', title: 'Motion & music', sub: 'Clips, camera moves, real sound', icon: FilmReel },
    { num: '05', title: 'Review & upload', sub: 'You approve. Nothing posts alone', icon: SealCheck },
  ];

  const shotImages = [
    '/img/hook.jpg',
    '/img/bleach.jpg',
    '/img/mother.jpg',
    '/img/offended.jpg',
    '/img/gentlemen.jpg',
    '/img/clinic.jpg',
    '/img/three.jpg',
    '/img/begging.jpg',
    '/img/street.jpg',
    '/img/friend.jpg',
    '/img/scalpel.jpg',
    '/img/morning.jpg',
  ];

  const renderStepContent = (stepIdx: number) => {
    switch (stepIdx) {
      case 0:
        return (
          <div>
            <div className="sh">
              <b>Topic Selection</b>
              <span className="faint">Hidden Reasons Queue</span>
            </div>
            <div
              style={{
                padding: '24px',
                borderRadius: '14px',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid var(--line)',
                marginTop: '16px',
              }}
            >
              <span style={{ fontSize: '12px', color: 'var(--amber2)', textTransform: 'uppercase', fontWeight: 650 }}>
                Selected Topic
              </span>
              <h3 style={{ fontSize: '22px', color: 'var(--tx)', marginTop: '8px', marginBottom: '14px' }}>
                "Why did doctors refuse to wash their hands?"
              </h3>
              <p style={{ fontSize: '13.5px', color: 'var(--tx2)', lineHeight: 1.6 }}>
                Vienna, 1847. Ignaz Semmelweis discovers that doctors dissecting cadavers carry lethal infection to mothers giving birth in the First Clinic.
              </p>
            </div>
          </div>
        );
      case 1:
        return (
          <div>
            <div className="sh">
              <b>Fact-Checked Script</b>
              <span className="faint">4 models · 100% claims verified</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '16px' }}>
              <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--line)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <b style={{ fontSize: '13px', color: 'var(--amber2)' }}>BEAT 1 · HOOK</b>
                  <span className="chip ok" style={{ height: '20px', fontSize: '11px' }}>supported</span>
                </div>
                <p style={{ fontSize: '13.5px', color: 'var(--tx)', lineHeight: 1.5 }}>
                  "In 1847, women in Vienna begged on their knees not to be admitted to the First Maternity Clinic."
                </p>
              </div>
              <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--line)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <b style={{ fontSize: '13px', color: 'var(--amber2)' }}>BEAT 2 · REVELATION</b>
                  <span className="chip ok" style={{ height: '20px', fontSize: '11px' }}>supported</span>
                </div>
                <p style={{ fontSize: '13.5px', color: 'var(--tx)', lineHeight: 1.5 }}>
                  "Midwives had a 2% death rate. Doctors had 16%. The only difference? Doctors came straight from the morgue."
                </p>
              </div>
            </div>
          </div>
        );
      case 2:
      case 3:
        return (
          <div>
            <div className="sh">
              <b>{stepIdx === 3 ? 'Motion & Sound' : 'Painting shots'}</b>
              <span className="faint">Lab · free GPU · 9 of 12 shown</span>
            </div>

            {/* 12 shot grid */}
            <div className="sg">
              {shotImages.map((src, i) => (
                <img
                  key={i}
                  src={src}
                  alt={`Shot ${i + 1}`}
                  className={i < 9 ? 'lit' : ''}
                  style={{
                    animationDelay: `${i * 0.1}s`,
                    transform: stepIdx === 3 && i < 3 ? 'scale(1.05)' : 'none',
                    transition: 'transform 3s ease',
                  }}
                />
              ))}
            </div>

            {/* Cast row */}
            <div className="cast">
              <span className="faint" style={{ fontSize: '12px' }}>
                Same cast in every shot
              </span>
              <div className="cm">
                <img src="/img/hook.jpg" alt="Semmelweis" />
                <span>Semmelweis</span>
              </div>
              <div className="cm">
                <img src="/img/mother.jpg" alt="Mother" />
                <span>Mother</span>
              </div>
              <div className="cm">
                <img src="/img/friend.jpg" alt="Kolletschka" />
                <span>Kolletschka</span>
              </div>
              <div className="cm">
                <img src="/img/pasteur.jpg" alt="Pasteur" />
                <span>Pasteur</span>
              </div>
            </div>

            {/* Picture checker */}
            <div className="checker">
              <div className="ck">
                <Eye size={17} weight="duotone" className="ic" />
                <div>
                  <b>Picture checker</b>
                  <span>Looks at every shot before it is used</span>
                </div>
              </div>
              <div className="ckr">
                <span>Is a woman kneeling?</span>
                <span className="chip ok">yes</span>
              </div>
              <div className="ckr">
                <span>Any text in the picture?</span>
                <span className="chip ok">no</span>
              </div>
              <div className="ckr">
                <span>Anything modern in 1847?</span>
                <span className="chip bad">yes · repainting</span>
              </div>
            </div>

            {stepIdx === 3 && (
              <div style={{ marginTop: '16px', padding: '12px 16px', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--line)', display: 'flex', alignItems: 'center', gap: '14px' }}>
                <FilmReel size={20} weight="duotone" color="var(--amber2)" />
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '3px', height: '20px' }}>
                  {[12, 18, 8, 22, 14, 28, 20, 16, 24, 10, 18, 30, 22, 14, 26, 16, 12, 20, 28, 14, 8, 22, 18, 12, 24, 16, 10, 20].map((h, i) => (
                    <span key={i} style={{ flex: 1, height: `${h}px`, borderRadius: '2px', background: i < 18 ? 'var(--amber2)' : 'rgba(255,255,255,0.15)' }} />
                  ))}
                </div>
                <span style={{ fontSize: '11px', color: 'var(--tx3)' }}>-14 LUFS</span>
              </div>
            )}
          </div>
        );
      case 4:
        return (
          <div>
            <div className="sh">
              <b>Review Gate</b>
              <span className="faint">Final human sign-off</span>
            </div>
            <div
              style={{
                padding: '24px',
                borderRadius: '16px',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid var(--line)',
                marginTop: '16px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <CheckCircle size={20} color="#3FB950" weight="duotone" />
                <b style={{ fontSize: '16px' }}>Ready to upload</b>
              </div>
              <p style={{ fontSize: '13.5px', color: 'var(--tx2)', lineHeight: 1.5, marginBottom: '20px' }}>
                Film assembled with 1080x1920 vertical format, synchronized historic soundtrack, voice narration at -14 LUFS, and 100% verified primary sources.
              </p>
              <div style={{ display: 'flex', gap: '12px' }}>
                <span className="btn pri" style={{ height: '38px', padding: '0 18px', fontSize: '13px' }}>
                  Approve film
                </span>
                <span className="btn sec" style={{ height: '38px', padding: '0 18px', fontSize: '13px' }}>
                  Preview clip
                </span>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  // Mobile layout: Stacked steps with their panels underneath
  if (isMobile) {
    return (
      <section className="how-it-works-wrap" style={{ position: 'relative', width: '100%', padding: '40px 0 60px' }}>
        <div className="grain" />
        <div style={{ padding: '0 20px', textAlign: 'center', marginBottom: '24px' }}>
          <div className="eyebrow">How a film is made</div>
          <h2 style={{ fontSize: '32px', letterSpacing: '-0.04em', lineHeight: 1.1, marginTop: '12px' }}>
            From a topic to a film <span className="serif">in one hour.</span>
          </h2>
          <p className="muted" style={{ fontSize: '15px', marginTop: '10px' }}>
            Every step plays out in the studio below.
          </p>
        </div>

        <div style={{ padding: '0 16px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {steps.map((st, idx) => {
            const IconComp = st.icon;
            return (
              <div
                key={st.num}
                style={{
                  borderRadius: '18px',
                  background: 'rgba(16,19,29,0.85)',
                  boxShadow: '0 0 0 1px var(--line2)',
                  padding: '18px',
                  overflow: 'hidden',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '14px' }}>
                  <span style={{ fontSize: '12px', fontVariantNumeric: 'tabular-nums', color: 'var(--amber2)', fontWeight: 700 }}>
                    {st.num}
                  </span>
                  <IconComp size={18} weight="duotone" color="var(--amber2)" />
                  <div>
                    <b style={{ fontSize: '15px', color: 'var(--tx)' }}>{st.title}</b>
                    <span style={{ fontSize: '12px', color: 'var(--tx3)', display: 'block' }}>{st.sub}</span>
                  </div>
                </div>

                <div style={{ paddingTop: '10px', borderTop: '1px solid var(--line)' }}>
                  {renderStepContent(idx)}
                </div>
              </div>
            );
          })}
        </div>
      </section>
    );
  }

  // Desktop layout: Pinned interactive scroll story
  return (
    <section
      ref={wrapRef}
      className="how-it-works-wrap"
      style={{
        position: 'relative',
        height: standalone ? 'auto' : 'calc(100vh + 2000px)',
        width: '100%',
        padding: standalone ? '80px 0' : 0,
      }}
    >
      <div
        className="how-it-works-stage"
        style={{
          position: standalone ? 'relative' : 'sticky',
          top: 0,
          height: standalone ? 'auto' : '100vh',
          width: '100%',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div className="grain" />

        <div style={{ width: '100%', maxWidth: '1440px', height: '100%', position: 'relative' }}>
          {/* Left panel: Step indicator list */}
          <div className="hw-left" style={{ top: '120px' }}>
            <div className="eyebrow">How a film is made</div>
            <h2>
              From a topic to a film <span className="serif">in one hour.</span>
            </h2>
            <p className="muted">Scroll, and each step plays out in the app on the right.</p>

            <div className="hsteps">
              {steps.map((st, idx) => {
                const IconComp = st.icon;
                const isDone = idx < activeStep;
                const isOn = idx === activeStep;
                return (
                  <div
                    key={st.num}
                    className={`hs ${isDone ? 'done' : ''} ${isOn ? 'on' : ''}`}
                    onClick={() => setActiveStep(idx)}
                    style={{ cursor: 'pointer' }}
                  >
                    <span className="n">{st.num}</span>
                    <IconComp size={19} weight="duotone" className="ic" />
                    <div>
                      <b>{st.title}</b>
                      <span>{st.sub}</span>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="scrollhint">
              <Mouse size={16} className="ic" />
              <span>Smooth scroll · step {activeStep + 1} of 5</span>
            </div>
          </div>

          {/* Right stage: Animated interactive demonstration */}
          <div className="stage" style={{ top: '96px' }}>
            {renderStepContent(activeStep)}
          </div>

          {/* Vertical scroll progress rail */}
          <div className="progressrail">
            <i style={{ height: `${((activeStep + 1) / 5) * 100}%` }} />
          </div>
        </div>
      </div>
    </section>
  );
};
