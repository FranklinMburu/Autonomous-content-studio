import React, { useMemo, useState } from 'react';
import { ArrowSquareOut } from '@phosphor-icons/react';
import { useItems } from '../../lib/items';
import { CHANNELS, STAGES, STAGE_HELP, LaneCode } from '../../lib/channels';
import { Page, Tabs } from '../kit';
import { VideoCard } from '../videos';
import { useStudio } from '../../context/StudioContext';
import { ago } from '../../lib/journey';

const NOTION_BOARD = 'https://www.notion.so/654c7f0514f0448f8c8e79752c604dbc';

export const BoardView: React.FC<{ onNavigate: (r: string) => void; lane?: LaneCode; embedded?: boolean }> = ({ onNavigate, lane: fixedLane, embedded }) => {
  const all = useItems();
  const { board, feedBuilt } = useStudio();
  const q = new URLSearchParams(window.location.search);
  const [lane, setLane] = useState<string>(fixedLane || q.get('lane') || 'all');
  const [onlyNeeds, setOnlyNeeds] = useState(q.get('stage') === 'needs');
  const [showSkipped, setShowSkipped] = useState(false);
  const items = useMemo(() => all.filter(i => (lane === 'all' || i.lane === lane) && (!onlyNeeds || i.needsYou) && i.kind !== 'topic' && i.kind !== 'lab'), [all, lane, onlyNeeds]);
  const stages = STAGES.filter(s => s !== 'Skipped' || showSkipped);

  const body = (
    <>
      <div className="board-bar">
        {!fixedLane && (
          <Tabs value={lane} onChange={setLane} tabs={[{ key: 'all', label: 'All channels', count: all.filter(i => i.kind !== 'topic' && i.kind !== 'lab').length },
            ...CHANNELS.map(c => ({ key: c.code, label: c.name, count: all.filter(i => i.lane === c.code && i.kind !== 'topic' && i.kind !== 'lab').length }))]} />
        )}
        <div className="board-tg">
          <label><input type="checkbox" checked={onlyNeeds} onChange={e => setOnlyNeeds(e.target.checked)} /> Only what needs me</label>
          <label><input type="checkbox" checked={showSkipped} onChange={e => setShowSkipped(e.target.checked)} /> Show skipped</label>
        </div>
      </div>
      <div className="board">
        {stages.map(s => {
          const col = items.filter(i => i.stage === s);
          return (
            <div key={s} className="col">
              <div className="col-h" title={STAGE_HELP[s]}><b>{s}</b><span className="n">{col.length}</span></div>
              <div className="col-hint">{STAGE_HELP[s]}</div>
              <div className="col-b">
                {col.slice(0, 40).map(i => <VideoCard key={i.key} item={i} onOpen={onNavigate} compact showLane={lane === 'all'} showStage={false} />)}
                {col.length > 40 && <button className="lnk" onClick={() => onNavigate('/app/library')}>{col.length - 40} more in the Library</button>}
                {!col.length && <div className="col-empty">Nothing here</div>}
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
  if (embedded) return body;
  return (
    <Page title="Board" wide
      sub={<>Every video of every channel, by stage: the same board as in Notion. Moving a card here moves it there too.
        {board === null ? ' (The Notion stages arrive with the next data refresh.)' : feedBuilt ? ` Synced ${ago(feedBuilt)}.` : ''}</>}
      actions={<a className="btn sec" href={NOTION_BOARD} target="_blank" rel="noopener noreferrer">Open in Notion <ArrowSquareOut size={14} /></a>}>
      {body}
    </Page>
  );
};
