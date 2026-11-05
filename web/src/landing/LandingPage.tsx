import React, { useState, useEffect } from 'react';
import { Nav } from './Nav';
import { Hero } from './Hero';
import { StudioPanel } from './StudioPanel';
import { Family } from './Family';
import { HowItWorks } from './HowItWorks';
import { StudioWorld } from './StudioWorld';
import { FilmsTrust } from './FilmsTrust';
import { Footer } from './Footer';
import { startSmoothScroll } from '../lib/smooth-scroll.js';

export const LandingPage: React.FC = () => {
  const [panelRoute, setPanelRoute] = useState('/app/films');
  const [activeFamilyKey, setActiveFamilyKey] = useState('studio');

  // Smooth scroll init from kit/smooth-scroll.js
  useEffect(() => {
    const stopScroll = startSmoothScroll();
    return () => {
      if (typeof stopScroll === 'function') stopScroll();
    };
  }, []);

  const handleSelectFamily = (key: string) => {
    setActiveFamilyKey(key);
    switch (key) {
      case 'studio':
        setPanelRoute('/app/films');
        break;
      case 'brain':
        setPanelRoute('/app/brain');
        break;
      case 'lab':
        setPanelRoute('/app/lab');
        break;
      case 'guard':
        setPanelRoute('/app/guard');
        break;
      case 'channels':
        setPanelRoute('/app/channels');
        break;
      default:
        setPanelRoute('/app/films');
        break;
    }
  };

  const handleSelectFilmForPanel = (filmId: string) => {
    setPanelRoute(`/app/films/${filmId}`);
    const panelEl = document.getElementById('studio-panel-section');
    if (panelEl) {
      panelEl.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', minHeight: '100vh', background: 'var(--bg)' }}>
      {/* 4.0 Nav */}
      <Nav onSelectFamily={handleSelectFamily} />

      {/* 4.1 Section 1: Hero with the Earth globe */}
      <Hero onSelectFilmForPanel={handleSelectFilmForPanel} />

      {/* 4.2 Section 2: The live studio panel (clickable app inside browser frame) */}
      <StudioPanel
        embeddedRoute={panelRoute}
        onEmbeddedRouteChange={setPanelRoute}
      />

      {/* 4.3 Section 3: The family (5 parts) */}
      <Family activeKey={activeFamilyKey} onSelectFamily={handleSelectFamily} />

      {/* 4.4 Section 4: How a film is made */}
      <HowItWorks />

      {/* 4.5 Section 5: The Studio World sphere */}
      <StudioWorld />

      {/* 4.6 Section 6: Films and trust */}
      <FilmsTrust />

      {/* 4.7 Footer */}
      <Footer />
    </div>
  );
};
