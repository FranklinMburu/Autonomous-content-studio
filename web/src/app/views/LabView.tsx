import React from 'react';
import { Flask, Cpu, FilmReel, ArrowSquareOut } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const LabView: React.FC = () => {
  const { labRunsData } = useStudio();

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <div>
          <h1 className="pt">Candela Lab</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            Painting and motion experiments on Kaggle's free weekly GPU hours. Each run is published as a GitHub pre-release.
          </p>
        </div>
      </div>

      {/* Lab Engine Specs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '28px' }}>
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
            <Cpu size={18} color="var(--amber2)" weight="duotone" />
            <b style={{ fontSize: '15px' }}>Kaggle free GPU</b>
          </div>
          <span style={{ fontSize: '13px', color: 'var(--tx2)', lineHeight: 1.5 }}>
            Kaggle's free weekly GPU hours. A GitHub workflow starts the notebook and collects what it made.
          </span>
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
            <Flask size={18} color="var(--amber2)" weight="duotone" />
            <b style={{ fontSize: '15px' }}>SDXL + IP-Adapter</b>
          </div>
          <span style={{ fontSize: '13px', color: 'var(--tx2)', lineHeight: 1.5 }}>
            Stable Diffusion XL paints every shot; IP-Adapter keeps each character's face the same from shot to shot.
          </span>
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
            <FilmReel size={18} color="var(--amber2)" weight="duotone" />
            <b style={{ fontSize: '15px' }}>LTX-Video clips</b>
          </div>
          <span style={{ fontSize: '13px', color: 'var(--tx2)', lineHeight: 1.5 }}>
            Turns chosen 'clip' shots into short moving clips; the other shots get depth-based camera moves.
          </span>
        </div>
      </div>

      {/* Lab Runs History */}
      <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '14px', color: 'var(--tx2)' }}>
        Lab Experiment Releases
      </h2>
      <div
        style={{
          borderRadius: '16px',
          background: 'var(--s1)',
          boxShadow: '0 0 0 1px var(--line) inset',
          overflow: 'hidden',
        }}
      >
        {labRunsData.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: 'var(--tx3)', fontSize: '13px' }}>
            No isolated lab releases recorded yet.
          </div>
        ) : (
          [...labRunsData].sort((a: any, b: any) => (parseInt(String(b.tag).match(/(\d+)$/)?.[1] || '0') - parseInt(String(a.tag).match(/(\d+)$/)?.[1] || '0'))).map((lr, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '14px 20px',
                borderTop: i > 0 ? '1px solid var(--line)' : 'none',
                fontSize: '13.5px',
              }}
            >
              <div>
                <b>{lr.tag}</b>
                <span style={{ fontSize: '12px', color: 'var(--tx3)', display: 'block', marginTop: '2px' }}>
                  {lr.at ? new Date(lr.at).toLocaleDateString() : 'Recent'} · {lr.assets?.length || 0} artifacts
                </span>
              </div>
              <a
                href={lr.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn sec"
                style={{ height: '32px', fontSize: '12px', textDecoration: 'none' }}
              >
                <span>View artifacts</span>
                <ArrowSquareOut size={12} />
              </a>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
