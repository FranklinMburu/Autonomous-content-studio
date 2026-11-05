import React from 'react';
import { ShieldCheck, Eye, Warning, CheckCircle, ArrowSquareOut } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const GuardView: React.FC = () => {
  const { reviewItems, alerts } = useStudio();

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <div>
          <h1 className="pt">Candela Guard</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            Fact check, vision inspection, and review gates before any film can be uploaded.
          </p>
        </div>
      </div>

      {/* Three Guard cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '32px' }}>
        <div
          style={{
            padding: '20px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle size={18} color="#3FB950" weight="duotone" />
            <b style={{ fontSize: '15px' }}>Fact Check Gate</b>
          </div>
          <span style={{ fontSize: '13px', color: 'var(--tx2)', lineHeight: 1.5 }}>
            Every narrative line must cite primary literature (Wikipedia, PubMed, archives). Audited prior to shot planning.
          </span>
          <span className="chip ok" style={{ alignSelf: 'flex-start', marginTop: '4px' }}>100% verified</span>
        </div>

        <div
          style={{
            padding: '20px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Eye size={18} color="var(--amber2)" weight="duotone" />
            <b style={{ fontSize: '15px' }}>Picture Checker</b>
          </div>
          <span style={{ fontSize: '13px', color: 'var(--tx2)', lineHeight: 1.5 }}>
            Vision model interrogates each frame: correct pose, text leakage, anachronistic objects, face fidelity.
          </span>
          <span className="chip rev" style={{ alignSelf: 'flex-start', marginTop: '4px' }}>Auto-repainting active</span>
        </div>

        <div
          style={{
            padding: '20px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={18} color="var(--amber2)" weight="duotone" />
            <b style={{ fontSize: '15px' }}>Review Gate</b>
          </div>
          <span style={{ fontSize: '13px', color: 'var(--tx2)', lineHeight: 1.5 }}>
            Films with any remaining uncertainty are held for human approval. Zero films post autonomously without sign-off.
          </span>
          <span className="chip rev" style={{ alignSelf: 'flex-start', marginTop: '4px' }}>
            {reviewItems.length} held for review
          </span>
        </div>
      </div>

      {/* Alerts Section */}
      <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', color: 'var(--tx2)' }}>
        Pipeline Alerts
      </h2>
      <div
        style={{
          borderRadius: '16px',
          background: 'var(--s1)',
          boxShadow: '0 0 0 1px var(--line) inset',
          overflow: 'hidden',
        }}
      >
        {alerts.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: 'var(--tx3)', fontSize: '13px' }}>
            No alerts open. All guards reporting normal operations.
          </div>
        ) : (
          alerts.map((al, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '14px 20px',
                borderTop: idx > 0 ? '1px solid var(--line)' : 'none',
                fontSize: '13.5px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Warning size={18} color="#F85149" weight="duotone" />
                <div>
                  <b>{al.title || al.body}</b>
                  <span style={{ fontSize: '12px', color: 'var(--tx3)', display: 'block', marginTop: '2px' }}>
                    {al.at ? new Date(al.at).toLocaleString() : 'Recent'}
                  </span>
                </div>
              </div>
              {al.url && (
                <a
                  href={al.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn sec"
                  style={{ height: '32px', fontSize: '12px', textDecoration: 'none' }}
                >
                  <span>View on GitHub</span>
                  <ArrowSquareOut size={12} />
                </a>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
