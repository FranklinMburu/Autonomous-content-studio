import React, { useState } from 'react';
import { FilmStrip, Brain, Flask, ShieldCheck, Broadcast, ArrowRight } from '@phosphor-icons/react';

interface FamilyProps {
  activeKey: string;
  onSelectFamily: (key: string) => void;
}

export const Family: React.FC<FamilyProps> = ({ activeKey, onSelectFamily }) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  const cards = [
    {
      key: 'studio',
      name: 'Studio',
      desc: 'Your films, runs and reviews in one place',
      icon: FilmStrip,
      route: '/app/films',
    },
    {
      key: 'brain',
      name: 'Brain',
      desc: 'Free AI models, checked and kept honest',
      icon: Brain,
      route: '/app/brain',
    },
    {
      key: 'lab',
      name: 'Lab',
      desc: 'Paints and animates every shot on free GPUs',
      icon: Flask,
      route: '/app/lab',
    },
    {
      key: 'guard',
      name: 'Guard',
      desc: 'Fact check, picture check, review gate',
      icon: ShieldCheck,
      route: '/app/guard',
    },
    {
      key: 'channels',
      name: 'Channels',
      desc: 'One niche, one voice, five films a day',
      icon: Broadcast,
      route: '/app/channels',
    },
  ];

  const handleClick = (key: string) => {
    onSelectFamily(key);
    // Smooth scroll up to section 2 panel
    const panelEl = document.getElementById('studio-panel-section');
    if (panelEl) {
      panelEl.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section
      style={{
        position: 'relative',
        minHeight: '560px',
        padding: '70px 0 60px',
        width: '100%',
        overflow: 'hidden',
      }}
    >
      <div className="grain" />

      {/* Background SVG flow curves */}
      <svg
        className="flow"
        width="1440"
        height="560"
        viewBox="0 0 1440 560"
        style={{
          position: 'absolute',
          left: '50%',
          top: 0,
          transform: 'translateX(-50%)',
          pointerEvents: 'none',
        }}
      >
        <defs>
          <linearGradient id="hotg" x1="0" x2="1">
            <stop offset="0" stopColor="rgba(255,200,97,0)" />
            <stop offset="0.55" stopColor="#FFC861" />
            <stop offset="1" stopColor="rgba(121,192,255,0.2)" />
          </linearGradient>
        </defs>
        <path d="M -40 454.0 C 360.0 174.0, 792.0 478.0, 1480 254.0" stroke="rgba(245,165,36,0.03)" strokeWidth="1" fill="none" />
        <path d="M -40 486.0 C 360.0 218.0, 792.0 499.2, 1480 286.0" stroke="rgba(245,165,36,0.04)" strokeWidth="1" fill="none" />
        <path d="M -40 518.0 C 360.0 262.0, 792.0 520.4, 1480 318.0" stroke="url(#hotg)" strokeWidth="1.6" fill="none" />
        <path d="M -40 550.0 C 360.0 306.0, 792.0 541.6, 1480 350.0" stroke="rgba(245,165,36,0.07)" strokeWidth="1" fill="none" />
        <path d="M -40 582.0 C 360.0 350.0, 792.0 562.8, 1480 382.0" stroke="rgba(245,165,36,0.05)" strokeWidth="1" fill="none" />
        <path d="M -40 614.0 C 360.0 394.0, 792.0 584.0, 1480 414.0" stroke="rgba(245,165,36,0.04)" strokeWidth="1" fill="none" />
      </svg>

      {/* Heading */}
      <div className="sec">
        <div className="eyebrow">One studio, five parts</div>
        <h2>
          Everything a film needs. <span className="serif">Nothing</span> it doesn't.
        </h2>
      </div>

      {/* Five Product Cards */}
      <div className="fams">
        {cards.map((c, i) => {
          const isSelected = activeKey === c.key;
          const IconComp = c.icon;
          return (
            <div
              key={c.key}
              className={`fcard ${isSelected ? 'on' : ''}`}
              onClick={() => handleClick(c.key)}
              onMouseEnter={() => setHoveredIdx(i)}
              onMouseLeave={() => setHoveredIdx(null)}
              style={{ cursor: 'pointer' }}
            >
              <div className="fi">
                <IconComp size={22} weight="duotone" />
              </div>
              <b>
                Candela <span className="serif">{c.name}</span>
              </b>
              <p>{c.desc}</p>
              <span className="more">
                <span>{isSelected ? 'You are here' : 'Open'}</span>
                <ArrowRight size={12} />
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
};
