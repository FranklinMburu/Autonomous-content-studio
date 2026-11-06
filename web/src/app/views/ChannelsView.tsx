import React from 'react';
import { Broadcast, Plus, ArrowRight } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';
import { DEFAULTS } from '../../lib/github-data.js';

interface ChannelsViewProps {
  onSelectChannel: (code: string) => void;
}

export const ChannelsView: React.FC<ChannelsViewProps> = ({ onSelectChannel }) => {
  const { films, reviewItems, polishItems, topics, statusBoardData } = useStudio();

  const madeCount = films.length;
  const reviewCount = reviewItems.length;
  const polishCount = polishItems.length;
  const queuedCount = topics.length;

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <div>
          <h1 className="pt">Channels</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            One niche, one voice, five films a day
          </p>
        </div>
        <button
          className="btn sec"
          disabled
          style={{ opacity: 0.6, cursor: 'not-allowed', height: '34px', fontSize: '12.5px' }}
        >
          <Plus size={14} />
          <span>Add channel (Soon)</span>
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        {/* Hidden Reasons Channel Card */}
        {DEFAULTS.channels.map(ch => (
          <div
            key={ch.code}
            onClick={() => onSelectChannel(ch.code)}
            style={{
              padding: '24px',
              borderRadius: '16px',
              background: 'var(--s1)',
              boxShadow: '0 0 0 1px var(--line) inset',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              transition: 'transform 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    background: 'rgba(245,165,36,0.12)',
                    display: 'grid',
                    placeItems: 'center',
                    color: 'var(--amber2)',
                  }}
                >
                  <Broadcast size={20} weight="duotone" />
                </div>
                <div>
                  <b style={{ fontSize: '16px' }}>{ch.name}</b>
                  <div style={{ fontSize: '12px', color: 'var(--tx3)' }}>{ch.niche}</div>
                </div>
              </div>
              <span
                style={{
                  fontSize: '11.5px',
                  fontWeight: 700,
                  color: 'var(--amber2)',
                  background: 'rgba(245,165,36,0.1)',
                  padding: '3px 8px',
                  borderRadius: '6px',
                }}
              >
                {ch.code}
              </span>
            </div>

            <div style={{ display: 'flex', gap: '8px', fontSize: '12px' }}>
              <span className="chip ok" style={{ height: '22px' }}>Film style</span>
              <span
                style={{
                  padding: '2px 8px',
                  borderRadius: '99px',
                  background: 'rgba(255,255,255,0.04)',
                  color: 'var(--tx2)',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                5 films a day
              </span>
            </div>

            {/* Counts grid */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '8px',
                padding: '12px',
                borderRadius: '10px',
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--line)',
                textAlign: 'center',
              }}
            >
              <div>
                <b style={{ display: 'block', fontSize: '18px' }}>{madeCount}</b>
                <span style={{ fontSize: '11px', color: 'var(--tx3)' }}>Made</span>
              </div>
              <div>
                <b style={{ display: 'block', fontSize: '18px', color: reviewCount ? 'var(--amber2)' : 'inherit' }}>
                  {reviewCount}
                </b>
                <span style={{ fontSize: '11px', color: 'var(--tx3)' }}>Review</span>
              </div>
              <div>
                <b style={{ display: 'block', fontSize: '18px' }}>{polishCount}</b>
                <span style={{ fontSize: '11px', color: 'var(--tx3)' }}>Polish</span>
              </div>
              <div>
                <b style={{ display: 'block', fontSize: '18px' }}>{queuedCount}</b>
                <span style={{ fontSize: '11px', color: 'var(--tx3)' }}>Queued</span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12.5px', color: 'var(--amber2)', marginTop: 'auto' }}>
              <span>Open channel workspace</span>
              <ArrowRight size={13} />
            </div>
          </div>
        ))}

        {/* Second Card: Explainer pipeline */}
        <div
          style={{
            padding: '24px',
            borderRadius: '16px',
            background: 'var(--s1)',
            boxShadow: '0 0 0 1px var(--line) inset',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  background: 'rgba(255,255,255,0.04)',
                  display: 'grid',
                  placeItems: 'center',
                  color: 'var(--tx2)',
                }}
              >
                <Broadcast size={20} weight="duotone" />
              </div>
              <div>
                <b style={{ fontSize: '16px' }}>Explainer pipeline</b>
                <div style={{ fontSize: '12px', color: 'var(--tx3)' }}>Body Science pilot</div>
              </div>
            </div>
            <span
              style={{
                fontSize: '11.5px',
                fontWeight: 600,
                color: 'var(--tx3)',
                background: 'rgba(255,255,255,0.04)',
                padding: '3px 8px',
                borderRadius: '6px',
              }}
            >
              PILOT
            </span>
          </div>

          <p style={{ fontSize: '13px', color: 'var(--tx2)', lineHeight: 1.5 }}>
            The older explainer style (icons and captions). Its live status board, rewritten after every run:
          </p>

          <div
            style={{
              padding: '12px',
              borderRadius: '10px',
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid var(--line)',
            }}
          >
            {(statusBoardData?.rows || []).length === 0 && (
              <div style={{ fontSize: '12px', color: 'var(--tx3)' }}>{statusBoardData === null ? 'No status board yet.' : 'Loading…'}</div>
            )}
            {(statusBoardData?.rows || []).map((r: any, i: number) => (
              <div key={i} title={r.meaning} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginTop: i ? '8px' : 0 }}>
                <span style={{ color: 'var(--tx3)' }}>{r.stage}</span>
                <span>{r.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
