import React, { useState } from 'react';
import { ArrowLeft, Broadcast } from '@phosphor-icons/react';
import { FilmsView } from './FilmsView';
import { TopicsView } from './TopicsView';
import { ScheduleView } from './ScheduleView';
import { MemoryView } from './MemoryView';

interface ChannelDetailViewProps {
  channelCode: string;
  onBack: () => void;
  onSelectFilm: (id: string) => void;
  onNavigate: (path: string) => void;
}

export const ChannelDetailView: React.FC<ChannelDetailViewProps> = ({
  channelCode,
  onBack,
  onSelectFilm,
  onNavigate,
}) => {
  const [tab, setTab] = useState<'films' | 'topics' | 'schedule' | 'memory'>('films');

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <button
        onClick={onBack}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          background: 'none',
          border: 'none',
          color: 'var(--tx3)',
          cursor: 'pointer',
          fontSize: '13px',
          marginBottom: '16px',
          padding: 0,
        }}
      >
        <ArrowLeft size={16} />
        <span>Back to Channels</span>
      </button>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <div
          style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: 'rgba(245,165,36,0.12)',
            display: 'grid',
            placeItems: 'center',
            color: 'var(--amber2)',
          }}
        >
          <Broadcast size={22} weight="duotone" />
        </div>
        <div>
          <h1 className="pt" style={{ margin: 0, fontSize: '24px' }}>Hidden Reasons</h1>
          <span style={{ fontSize: '12.5px', color: 'var(--tx3)' }}>
            Code: {channelCode} · True stories behind history's strangest acts
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs" style={{ marginBottom: '20px', width: 'fit-content' }}>
        <span className={tab === 'films' ? 'on' : ''} onClick={() => setTab('films')} style={{ cursor: 'pointer' }}>
          Films
        </span>
        <span className={tab === 'topics' ? 'on' : ''} onClick={() => setTab('topics')} style={{ cursor: 'pointer' }}>
          Topics
        </span>
        <span className={tab === 'schedule' ? 'on' : ''} onClick={() => setTab('schedule')} style={{ cursor: 'pointer' }}>
          Schedule
        </span>
        <span className={tab === 'memory' ? 'on' : ''} onClick={() => setTab('memory')} style={{ cursor: 'pointer' }}>
          Memory
        </span>
      </div>

      {tab === 'films' && <FilmsView onSelectFilm={onSelectFilm} onNavigate={onNavigate} />}
      {tab === 'topics' && <TopicsView />}
      {tab === 'schedule' && <ScheduleView />}
      {tab === 'memory' && <MemoryView />}
    </div>
  );
};
