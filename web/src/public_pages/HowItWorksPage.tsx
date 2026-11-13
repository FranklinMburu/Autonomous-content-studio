import React from 'react';
import { Nav } from '../landing/Nav';
import { HowItWorks } from '../landing/HowItWorks';
import { Footer } from '../landing/Footer';
import { GuideView } from '../app/views/GuideView';
import { useStudio } from '../context/StudioContext';

// The public "How it works": the same guide as inside the app (all channels, the board, who does what), then the
// film walkthrough.
export const HowItWorksPage: React.FC = () => {
  const { navigate } = useStudio();
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)' }}>
      <Nav />
      <main style={{ flex: 1, paddingTop: '68px' }} className="public-guide">
        <GuideView onNavigate={navigate} />
        <HowItWorks standalone />
      </main>
      <Footer />
    </div>
  );
};
