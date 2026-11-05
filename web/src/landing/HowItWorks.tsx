import React, { useState, useEffect, useRef } from 'react';
import {
  LightbulbFilament,
  FileText,
  Palette,
  FilmReel,
  SealCheck,
  Eye,
  CheckCircle,
  WarningCircle,
  Mouse,
} from '@phosphor-icons/react';

interface HowItWorksProps {
  standalone?: boolean;
}

export const HowItWorks: React.FC<HowItWorksProps> = ({ standalone = false }) => {
  const wrapRef = useRef<HTMLElement>(null);
  const [activeStep, setActiveStep] = useState(2); // Step 3 (0-indexed: 2) as in reference

  // Pinned scroll behavior for landing page
  useEffect(() => {
    if (standalone) return;

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
  }, [standalone]);

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
            {activeStep === 0 && (
              <div>
                <div className="sh">
                  <b>Topic Selection</b>
                  <span className="faint">Hidden Reasons Queue</span>
                </div>
                <div
                  style={{
                    padding: '28px',
                    borderRadius: '14px',
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid var(--line)',
                    marginTop: '20px',
                  }}
                >
                  <span style={{ fontSize: '12px', color: 'var(--amber2)', textTransform: 'uppercase', fontWeight: 650 }}>
                    Selected Topic
                  </span>
                  <h3 style={{ fontSize: '26px', color: 'var(--tx)', marginTop: '8px', marginBottom: '16px' }}>
                    "Why did doctors refuse to wash their hands?"
                  </h3>
                  <p style={{ fontSize: '14px', color: 'var(--tx2)', lineHeight: 1.6 }}>
                    Vienna, 1847. Ignaz Semmelweis discovers that doctors dissecting cadavers carry lethal infection to mothers giving birth in the First Clinic.
                  </p>
                </div>
              </div>
            )}

            {activeStep === 1 && (
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
            )}

            {(activeStep === 2 || activeStep === 3) && (
              <div>
                <div className="sh">
                  <b>{activeStep === 3 ? 'Motion & Sound' : 'Painting shots'}</b>
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
                        transform: activeStep === 3 && i < 3 ? 'scale(1.05)' : 'none',
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
              </div>
            )}

            {activeStep === 4 && (
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
                    marginTop: '20px',
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
            )}
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
