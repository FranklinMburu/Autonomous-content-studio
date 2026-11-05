import React from 'react';
import { Brain, Sparkle, ShieldCheck } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const BrainView: React.FC = () => {
  const { modelsData } = useStudio();

  // Model list
  const modelsList = modelsData?.story_script_models || [
    { provider: 'Google', model: 'gemini-2.5-flash', role: 'writer', tier: 'free tier' },
    { provider: 'Groq', model: 'llama-3.3-70b-versatile', role: 'writer', tier: 'free tier' },
    { provider: 'Mistral', model: 'mistral-large-latest', role: 'writer', tier: 'free tier' },
    { provider: 'Cerebras', model: 'llama-3.1-70b', role: 'checker', tier: 'free tier' },
  ];

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <div>
          <h1 className="pt">Candela Brain</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            Four free models write each script; the best draft wins.
          </p>
        </div>
      </div>

      <div
        style={{
          borderRadius: '16px',
          background: 'var(--s1)',
          boxShadow: '0 0 0 1px var(--line) inset',
          overflow: 'hidden',
          maxWidth: '840px',
        }}
      >
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1.5fr 2fr 1.5fr 1fr',
            padding: '14px 20px',
            borderBottom: '1px solid var(--line)',
            fontSize: '11px',
            fontWeight: 700,
            color: 'var(--tx3)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
          }}
        >
          <span>Provider</span>
          <span>Model</span>
          <span>Role</span>
          <span style={{ textAlign: 'right' }}>Tier</span>
        </div>

        {modelsList.map((m: any, i: number) => (
          <div
            key={i}
            style={{
              display: 'grid',
              gridTemplateColumns: '1.5fr 2fr 1.5fr 1fr',
              alignItems: 'center',
              padding: '16px 20px',
              borderTop: i > 0 ? '1px solid var(--line)' : 'none',
              fontSize: '13.5px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkle size={16} color="var(--amber2)" />
              <b>{m.provider}</b>
            </div>
            <code style={{ fontFamily: 'ui-monospace, Menlo, monospace', fontSize: '12.5px', color: 'var(--tx2)' }}>
              {m.model}
            </code>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              {m.role === 'checker' ? (
                <ShieldCheck size={16} color="#3FB950" />
              ) : (
                <Brain size={16} color="var(--amber2)" />
              )}
              <span style={{ textTransform: 'capitalize', color: 'var(--tx)' }}>{m.role}</span>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span className="chip ok" style={{ fontSize: '11px', height: '22px' }}>
                {m.tier || 'Free tier'}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div
        style={{
          marginTop: '24px',
          padding: '16px 20px',
          borderRadius: '12px',
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid var(--line)',
          maxWidth: '840px',
          fontSize: '13px',
          color: 'var(--tx2)',
          lineHeight: 1.5,
        }}
      >
        <b style={{ color: 'var(--tx)', display: 'block', marginBottom: '4px' }}>Draft Arbitration</b>
        Each writer model drafts a complete storyboard script citing exact claims from primary sources. The checker model audits each line: statements without verified source references are rejected, and the highest-scoring verified draft is scheduled for painting in the Lab.
      </div>
    </div>
  );
};
