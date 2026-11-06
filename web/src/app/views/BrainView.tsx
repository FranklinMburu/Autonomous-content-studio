import React from 'react';
import { Brain, Sparkle, ShieldCheck } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const BrainView: React.FC = () => {
  const { modelsData } = useStudio();

  // Real lists from pipeline/config.json ("provider:model" strings). Tried in order: when one free quota runs out,
  // the next model takes over, so a film never stops for quota.
  const PROV: Record<string, string> = { google: 'Google', groq: 'Groq', nvidia: 'NVIDIA', openrouter: 'OpenRouter' };
  const rows = (list: any, role: string) => (Array.isArray(list) ? list : []).map((id: string, i: number) => {
    const [prov, ...rest] = String(id).split(':');
    return { provider: PROV[prov] || prov, model: rest.join(':'), role, order: i + 1 };
  });
  const modelsList = [
    ...rows(modelsData?.story_script_models, 'Script writer'),
    ...rows(modelsData?.story_storyboard_models, 'Storyboard'),
    ...rows(modelsData?.draft_models, 'Explainer draft'),
  ];

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <div>
          <h1 className="pt">Candela Brain</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            Free models write the scripts and storyboards. If one runs out of free quota, the next one in the list takes over.
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

        {modelsList.length === 0 && (
          <div style={{ padding: '18px 20px', fontSize: '13px', color: 'var(--tx3)' }}>Loading the model list from GitHub…</div>
        )}
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
              {m.role === 'Storyboard' ? (
                <ShieldCheck size={16} color="#3FB950" />
              ) : (
                <Brain size={16} color="var(--amber2)" />
              )}
              <span style={{ color: 'var(--tx)' }}>{m.role} · #{m.order}</span>
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
        <b style={{ color: 'var(--tx)', display: 'block', marginBottom: '4px' }}>How a script is checked</b>
        The writer may use only facts from the saved sources. Every line is then checked against those sources; a script with unsupported lines is rewritten, or held as a polish ticket for you, Claude or Codex. The list comes from pipeline/config.json on GitHub.
      </div>
    </div>
  );
};
