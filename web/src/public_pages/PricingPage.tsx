import React from 'react';
import { CheckCircle, ShieldCheck, Sparkle } from '@phosphor-icons/react';
import { Nav } from '../landing/Nav';
import { Footer } from '../landing/Footer';
import { useStudio } from '../context/StudioContext';

export const PricingPage: React.FC = () => {
  const { navigate } = useStudio();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)' }}>
      <Nav />
      <div className="grain" />

      <main style={{ flex: 1, padding: '120px clamp(20px, 6.6vw, 96px) 60px', maxWidth: '1080px', margin: '0 auto', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '56px' }}>
          <div className="eyebrow">Pricing</div>
          <h1 style={{ fontSize: '46px', fontWeight: 700, letterSpacing: '-0.035em', marginTop: '10px' }}>
            Free while we build.
          </h1>
          <p style={{ color: 'var(--tx2)', fontSize: '17px', marginTop: '8px', maxWidth: '580px', margin: '8px auto 0' }}>
            Candela runs on free-tier APIs and open models today. No subscriptions, no hidden tokens.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '40px' }}>
          {/* Builder Tier (Current, 100% Free) */}
          <div
            style={{
              padding: '32px 28px',
              borderRadius: '20px',
              background: 'linear-gradient(180deg, #161A26, #10121A)',
              boxShadow: '0 0 0 1px rgba(245,165,36,0.3) inset, 0 20px 50px -20px rgba(245,165,36,0.2)',
              display: 'flex',
              flexDirection: 'column',
              gap: '20px',
            }}
          >
            <div>
              <span className="chip ok" style={{ marginBottom: '10px' }}>CURRENT TIER</span>
              <h2 style={{ fontSize: '26px', fontWeight: 700 }}>Open Studio</h2>
              <div style={{ fontSize: '36px', fontWeight: 800, marginTop: '8px', letterSpacing: '-0.03em' }}>
                $0 <span style={{ fontSize: '14px', color: 'var(--tx3)', fontWeight: 500 }}>/ month</span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--tx2)', marginTop: '8px' }}>
                Full access to our open-source autonomous pipeline on GitHub Actions.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13.5px', color: 'var(--tx2)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={16} color="#3FB950" weight="duotone" />
                <span>5 true-story films per day</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={16} color="#3FB950" weight="duotone" />
                <span>Fact-checking against primary sources</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={16} color="#3FB950" weight="duotone" />
                <span>Kaggle T4 × 2 GPU painting engine</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={16} color="#3FB950" weight="duotone" />
                <span>Vision model picture checks</span>
              </div>
            </div>

            <button
              onClick={() => navigate('/app')}
              className="btn pri"
              style={{ marginTop: 'auto', height: '42px', justifyContent: 'center', cursor: 'pointer' }}
            >
              Start using Studio
            </button>
          </div>

          {/* Planned Pro Tier */}
          <div
            style={{
              padding: '32px 28px',
              borderRadius: '20px',
              background: 'var(--s1)',
              boxShadow: '0 0 0 1px var(--line) inset',
              display: 'flex',
              flexDirection: 'column',
              gap: '20px',
              opacity: 0.85,
            }}
          >
            <div>
              <span className="chip" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--tx2)', marginBottom: '10px' }}>
                PLANNED
              </span>
              <h2 style={{ fontSize: '26px', fontWeight: 700 }}>Pro Studio</h2>
              <div style={{ fontSize: '36px', fontWeight: 800, marginTop: '8px', letterSpacing: '-0.03em', color: 'var(--tx3)' }}>
                TBD <span style={{ fontSize: '14px', color: 'var(--tx3)', fontWeight: 500 }}>once launched</span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--tx2)', marginTop: '8px' }}>
                For multi-channel creator teams needing automated direct YouTube publishing.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13.5px', color: 'var(--tx2)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkle size={16} color="var(--amber2)" weight="duotone" />
                <span>Unlimited channels & custom voices</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkle size={16} color="var(--amber2)" weight="duotone" />
                <span>Direct 1-click YouTube Studio upload</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkle size={16} color="var(--amber2)" weight="duotone" />
                <span>Multi-language script localization</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkle size={16} color="var(--amber2)" weight="duotone" />
                <span>YouTube Analytics audience learning</span>
              </div>
            </div>

            <button
              disabled
              className="btn sec"
              style={{ marginTop: 'auto', height: '42px', justifyContent: 'center', cursor: 'not-allowed', opacity: 0.6 }}
            >
              Coming soon
            </button>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};
