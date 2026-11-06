import React from 'react';
import { Nav } from '../landing/Nav';
import { HowItWorks } from '../landing/HowItWorks';
import { Footer } from '../landing/Footer';

export const HowItWorksPage: React.FC = () => {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)' }}>
      <Nav />
      <main style={{ flex: 1, paddingTop: '68px' }}>
        <HowItWorks standalone />
      </main>
      <Footer />
    </div>
  );
};
