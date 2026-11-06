import React, { useState } from 'react';
import { MagicWand, Copy, Check, ArrowSquareOut, CheckCircle } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const PolishView: React.FC = () => {
  const { polishItems, studio } = useStudio();
  const [selectedIssue, setSelectedIssue] = useState<any>(polishItems[0] || null);
  const [copied, setCopied] = useState(false);

  const activeIssue = selectedIssue || polishItems[0];
  const polishPrompt = activeIssue?.polishPrompt || (activeIssue ? `You are the polish step of YouTube Shorts studio for "${activeIssue.title}". Refine narration and pacing.` : '');

  const handleCopy = () => {
    navigator.clipboard.writeText(polishPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!activeIssue) {
    return (
      <div className="content" style={{ overflowY: 'auto' }}>
        <h1 className="pt" style={{ marginBottom: '16px' }}>Polish</h1>
        <div
          style={{
            padding: '48px',
            textAlign: 'center',
            background: 'var(--s1)',
            borderRadius: '16px',
            boxShadow: '0 0 0 1px var(--line) inset',
            color: 'var(--tx3)',
            maxWidth: '560px',
            margin: '40px auto',
          }}
        >
          <CheckCircle size={40} color="#3FB950" weight="duotone" style={{ margin: '0 auto 12px' }} />
          <p style={{ color: 'var(--tx)', fontSize: '15px', fontWeight: 600, marginBottom: '6px' }}>
            No polish needed right now
          </p>
          <p style={{ fontSize: '13px' }}>All drafts have been processed and approved.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <h1 className="pt">Polish</h1>
        <span style={{ fontSize: '12.5px', color: 'var(--tx3)' }}>{polishItems.length} draft waiting for polish</span>
      </div>

      <div style={{ display: 'flex', gap: '24px' }}>
        {/* Left list if multiple */}
        {polishItems.length > 1 && (
          <div style={{ width: '280px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {polishItems.map(item => (
              <div
                key={item.number}
                onClick={() => setSelectedIssue(item)}
                style={{
                  padding: '12px 14px',
                  borderRadius: '12px',
                  background: item.number === activeIssue.number ? 'rgba(245,165,36,0.1)' : 'var(--s1)',
                  boxShadow: item.number === activeIssue.number ? '0 0 0 1px rgba(245,165,36,0.25) inset' : '0 0 0 1px var(--line) inset',
                  cursor: 'pointer',
                  fontSize: '13px',
                }}
              >
                <b>{item.title}</b>
                <span style={{ display: 'block', fontSize: '11.5px', color: 'var(--tx3)', marginTop: '4px' }}>
                  Issue #{item.number}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Main 4-step polish guide */}
        <div style={{ flex: 1, maxWidth: '780px' }}>
          <div
            style={{
              padding: '24px',
              borderRadius: '16px',
              background: 'var(--s1)',
              boxShadow: '0 0 0 1px var(--line) inset',
              marginBottom: '20px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <MagicWand size={20} weight="duotone" color="var(--amber2)" />
              <b style={{ fontSize: '17px' }}>{activeIssue.title}</b>
            </div>

            <p style={{ fontSize: '13.5px', color: 'var(--tx2)', lineHeight: 1.5, marginBottom: '20px' }}>
              Polish this draft with Claude in 4 steps. The AI will sharpen the narration while keeping every fact true.
            </p>

            {/* 4 steps */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '24px' }}>
              <div style={{ padding: '12px', borderRadius: '10px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--line)' }}>
                <span style={{ fontSize: '11px', color: 'var(--amber2)', fontWeight: 700 }}>STEP 1</span>
                <p style={{ fontSize: '13px', fontWeight: 600, marginTop: '4px' }}>Copy prompt</p>
                <span style={{ fontSize: '12px', color: 'var(--tx3)' }}>From the box below</span>
              </div>
              <div style={{ padding: '12px', borderRadius: '10px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--line)' }}>
                <span style={{ fontSize: '11px', color: 'var(--amber2)', fontWeight: 700 }}>STEP 2</span>
                <p style={{ fontSize: '13px', fontWeight: 600, marginTop: '4px' }}>Open claude.ai</p>
                <span style={{ fontSize: '12px', color: 'var(--tx3)' }}>Paste and run</span>
              </div>
              <div style={{ padding: '12px', borderRadius: '10px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--line)' }}>
                <span style={{ fontSize: '11px', color: 'var(--amber2)', fontWeight: 700 }}>STEP 3</span>
                <p style={{ fontSize: '13px', fontWeight: 600, marginTop: '4px' }}>Copy answer</p>
                <span style={{ fontSize: '12px', color: 'var(--tx3)' }}>From Claude</span>
              </div>
              <div style={{ padding: '12px', borderRadius: '10px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--line)' }}>
                <span style={{ fontSize: '11px', color: 'var(--amber2)', fontWeight: 700 }}>STEP 4</span>
                <p style={{ fontSize: '13px', fontWeight: 600, marginTop: '4px' }}>Paste back</p>
                <span style={{ fontSize: '12px', color: 'var(--tx3)' }}>Comment on issue</span>
              </div>
            </div>

            {/* Prompt Box */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', color: 'var(--tx3)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Prompt for Claude
                </span>
                <button
                  className="btn sec"
                  onClick={handleCopy}
                  style={{ height: '30px', fontSize: '12px', padding: '0 12px', cursor: 'pointer' }}
                >
                  {copied ? <Check size={14} color="#3FB950" /> : <Copy size={14} />}
                  <span>{copied ? 'Copied' : 'Copy prompt'}</span>
                </button>
              </div>
              <textarea
                readOnly
                value={polishPrompt}
                style={{
                  width: '100%',
                  height: '140px',
                  background: '#07080D',
                  border: '1px solid var(--line)',
                  borderRadius: '10px',
                  padding: '12px',
                  fontFamily: 'ui-monospace, Menlo, monospace',
                  fontSize: '12px',
                  lineHeight: 1.45,
                  color: 'var(--tx2)',
                  resize: 'none',
                  outline: 'none',
                }}
              />
            </div>

            {/* Action buttons */}
            <div style={{ display: 'flex', gap: '12px' }}>
              <a
                href="https://claude.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="btn pri"
                style={{ height: '40px', padding: '0 18px', textDecoration: 'none', fontSize: '13px' }}
              >
                <span>Open claude.ai</span>
                <ArrowSquareOut size={15} />
              </a>
              <a
                href={activeIssue.url || studio.links.issue(activeIssue.number)}
                target="_blank"
                rel="noopener noreferrer"
                className="btn sec"
                style={{ height: '40px', padding: '0 18px', textDecoration: 'none', fontSize: '13px' }}
              >
                <span>Paste Claude's answer on GitHub</span>
                <ArrowSquareOut size={15} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
