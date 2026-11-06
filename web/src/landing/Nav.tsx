import React, { useState, useEffect } from 'react';
import { CaretDown, Broadcast, FilmStrip, Brain, Flask, ShieldCheck } from '@phosphor-icons/react';
import { Mark } from '../ui/Mark';
import { useStudio } from '../context/StudioContext';

interface NavProps {
  onSelectFamily?: (key: string) => void;
}

export const Nav: React.FC<NavProps> = ({ onSelectFamily }) => {
  const { navigate } = useStudio();
  const [scrolled, setScrolled] = useState(false);
  const [productMenuOpen, setProductMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 40);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const familyItems = [
    { name: 'Candela Studio', desc: 'Your films, runs and reviews', icon: FilmStrip, key: 'studio' },
    { name: 'Candela Brain', desc: 'Free AI models, checked and kept honest', icon: Brain, key: 'brain' },
    { name: 'Candela Lab', desc: 'Paints and animates on free GPUs', icon: Flask, key: 'lab' },
    { name: 'Candela Guard', desc: 'Fact check, picture check, review gate', icon: ShieldCheck, key: 'guard' },
    { name: 'Candela Channels', desc: 'One niche, one voice, 5 films a day', icon: Broadcast, key: 'channels' },
  ];

  return (
    <nav
      className="nav"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: '68px',
        display: 'flex',
        alignItems: 'center',
        padding: '0 clamp(20px, 4vw, 56px)',
        zIndex: 50,
        transition: 'background 200ms ease, backdrop-filter 200ms ease, box-shadow 200ms ease',
        background: scrolled ? 'rgba(11,11,15,0.75)' : 'transparent',
        backdropFilter: scrolled ? 'blur(14px)' : 'none',
        WebkitBackdropFilter: scrolled ? 'blur(14px)' : 'none',
        boxShadow: scrolled ? '0 1px 0 var(--line)' : 'none',
      }}
    >
      {/* Brand logo */}
      <div
        className="lg"
        onClick={() => navigate('/')}
        style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px' }}
      >
        <Mark size={26} />
        <b>Candela</b>
      </div>

      {/* Nav Links */}
      <div className="links" style={{ display: 'flex', gap: '30px', margin: '0 auto', fontSize: '14px', color: 'var(--tx2)' }}>
        <div style={{ position: 'relative' }}>
          <span
            onClick={() => setProductMenuOpen(!productMenuOpen)}
            style={{
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              color: productMenuOpen ? 'var(--tx)' : 'inherit',
            }}
          >
            Product <CaretDown size={11} />
          </span>

          {productMenuOpen && (
            <div
              style={{
                position: 'absolute',
                top: '32px',
                left: '-20px',
                width: '320px',
                background: 'var(--s1)',
                boxShadow: '0 0 0 1px var(--line2), 0 20px 40px rgba(0,0,0,0.85)',
                borderRadius: '14px',
                padding: '8px',
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
                zIndex: 100,
              }}
            >
              {familyItems.map(item => {
                const IconComp = item.icon;
                return (
                  <div
                    key={item.key}
                    onClick={() => {
                      setProductMenuOpen(false);
                      if (onSelectFamily) {
                        onSelectFamily(item.key);
                      } else {
                        navigate('/app/' + (item.key === 'studio' ? 'films' : item.key));
                      }
                    }}
                    style={{
                      padding: '10px 12px',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      transition: 'background 120ms ease',
                    }}
                    onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.04)')}
                    onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                  >
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '8px',
                        background: 'rgba(245,165,36,0.1)',
                        color: 'var(--amber2)',
                        display: 'grid',
                        placeItems: 'center',
                        flexShrink: 0,
                      }}
                    >
                      <IconComp size={18} weight="duotone" />
                    </div>
                    <div>
                      <b style={{ display: 'block', fontSize: '13px', color: 'var(--tx)' }}>{item.name}</b>
                      <span style={{ fontSize: '11.5px', color: 'var(--tx3)' }}>{item.desc}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <span onClick={() => navigate('/films')} style={{ cursor: 'pointer' }}>
          Films
        </span>
        <span onClick={() => navigate('/how-it-works')} style={{ cursor: 'pointer' }}>
          How it works
        </span>
        <span onClick={() => navigate('/pricing')} style={{ cursor: 'pointer' }}>
          Pricing
        </span>
        <a
          href="https://github.com/FranklinMburu/Autonomous-content-studio#readme"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: 'inherit', textDecoration: 'none' }}
        >
          Docs
        </a>
      </div>

      {/* Right side CTAs */}
      <div className="right" style={{ display: 'flex', alignItems: 'center', gap: '22px', fontSize: '14px' }}>
        <span
          onClick={() => navigate('/app')}
          className="muted"
          style={{ cursor: 'pointer' }}
        >
          Sign in
        </span>
        <button
          onClick={() => navigate('/app')}
          className="btn pri"
          style={{ height: '36px', padding: '0 16px', fontSize: '13.5px', cursor: 'pointer' }}
        >
          Start free
        </button>
      </div>
    </nav>
  );
};
