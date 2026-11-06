import React from 'react';
import { Mark } from '../ui/Mark';
import { useStudio } from '../context/StudioContext';

export const Footer: React.FC = () => {
  const { navigate } = useStudio();

  return (
    <footer
      style={{
        height: '64px',
        borderTop: '1px solid var(--line)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 clamp(20px, 6.6vw, 96px)',
        fontSize: '13px',
        color: 'var(--tx3)',
      }}
    >
      <div
        onClick={() => navigate('/')}
        style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--tx)' }}
      >
        <Mark size={20} />
        <b>Candela</b>
      </div>

      <div style={{ display: 'flex', gap: '24px' }}>
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
        <a
          href="https://github.com/FranklinMburu/Autonomous-content-studio"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: 'inherit', textDecoration: 'none' }}
        >
          GitHub
        </a>
      </div>

      <span>© 2026 Candela</span>
    </footer>
  );
};
