import React, { useMemo, useState } from 'react';
import { MagnifyingGlass } from '@phosphor-icons/react';
import { useItems } from '../../lib/items';
import { CHANNELS, STAGES } from '../../lib/channels';
import { Empty, Page, Tabs } from '../kit';
import { VideoCard } from '../videos';

export const LibraryView: React.FC<{ onNavigate: (r: string) => void }> = ({ onNavigate }) => {
  const all = useItems().filter(i => i.video);
  const q0 = new URLSearchParams(window.location.search);
  const [lane, setLane] = useState(q0.get('lane') || 'all');
  const [stage, setStage] = useState('all');
  const [q, setQ] = useState('');
  const list = useMemo(() => all.filter(i => (lane === 'all' || i.lane === lane) && (stage === 'all' || i.stage === stage)
    && (!q || i.title.toLowerCase().includes(q.toLowerCase()) || (i.sub || '').toLowerCase().includes(q.toLowerCase()))), [all, lane, stage, q]);
  return (
    <Page wide title="Library" sub="Every video the studio has made, newest first. Tap one to watch it.">
      <div className="board-bar">
        <Tabs value={lane} onChange={setLane} tabs={[{ key: 'all', label: 'All', count: all.length },
          ...CHANNELS.filter(c => all.some(i => i.lane === c.code)).map(c => ({ key: c.code, label: c.name, count: all.filter(i => i.lane === c.code).length }))]} />
        <div className="lfilters">
          <select value={stage} onChange={e => setStage(e.target.value)} aria-label="Stage">
            <option value="all">Any stage</option>{STAGES.map(s => <option key={s}>{s}</option>)}
          </select>
          <label className="srch"><MagnifyingGlass size={14} /><input value={q} onChange={e => setQ(e.target.value)} placeholder="Search titles" aria-label="Search" /></label>
        </div>
      </div>
      {list.length ? <div className="vgrid">{list.map(i => <VideoCard key={i.key} item={i} onOpen={onNavigate} />)}</div>
        : <Empty title="No videos match" text="Try another channel or stage." />}
    </Page>
  );
};
