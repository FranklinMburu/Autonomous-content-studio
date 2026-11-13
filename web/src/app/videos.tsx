import React, { useState } from 'react';
import { CheckCircle, DotsThree, FilmSlate, Play, Prohibit, ArrowCounterClockwise, UploadSimple, Sparkle, ArrowRight } from '@phosphor-icons/react';
import { Item } from '../lib/items';
import { LaneBadge, Score, StageChip } from './kit';
import { useActions } from '../context/ActionsContext';
import { useStudio } from '../context/StudioContext';
import { closeIssue } from '../lib/actions';
import { STAGES, Stage } from '../lib/channels';
import { ago } from '../lib/journey';

/** The moves that make sense for one video, each doing the same thing on GitHub and on the Notion board. */
export function useItemMoves(item: Item) {
  const { start, act } = useActions();
  const { uploadItems } = useStudio();
  const moves: { key: string; label: string; icon: React.ReactNode; run?: () => Promise<any>; route?: string; tone?: 'ok' | 'bad' }[] = [];
  if (item.kind === 'short' && !item.raw.dup) {
    const id = item.raw.videoId;
    const go = (stage: Stage, label: string) => () => start(`${label}: ${item.title.slice(0, 50)}`, 'studio-action.yml', {
      action: 'board-move', args: JSON.stringify({ video_id: id, stage }) }, { next: 'The board (here and in Notion) shows it in ' + stage + '.', target: item.route || undefined });
    if (item.stage !== 'Approved') moves.push({ key: 'ap', label: 'Approve', icon: <CheckCircle size={16} />, run: go('Approved', 'Approve'), tone: 'ok' });
    if (item.stage === 'Approved') moves.push({ key: 'po', label: 'Mark as posted', icon: <UploadSimple size={16} />, run: go('Posted', 'Posted') });
    if (item.stage !== 'Skipped') moves.push({ key: 'sk', label: 'Skip', icon: <Prohibit size={16} />, run: go('Skipped', 'Skip'), tone: 'bad' });
    if (item.stage !== 'Review') moves.push({ key: 'rv', label: 'Back to review', icon: <ArrowCounterClockwise size={16} />, run: go('Review', 'Back to review') });
  } else if (item.kind === 'film') {
    const f = item.raw;
    if (f.status === 'review' && f.reviewIssue) moves.push({ key: 'rv', label: 'Approve or repaint', icon: <Sparkle size={16} />, route: `/app/review/${f.reviewIssue.number}` });
    if (f.status === 'polish' || f.status === 'draft') moves.push({ key: 'pl', label: 'Polish it', icon: <Sparkle size={16} />, route: '/app/polish' });
    const up = f.status === 'ready' && uploadItems.find((u: any) => u.title.toLowerCase().replace(/[^a-z0-9]/g, '') === f.title.toLowerCase().replace(/[^a-z0-9]/g, ''));
    if (up) moves.push({ key: 'up', label: 'Mark as uploaded', icon: <UploadSimple size={16} />, tone: 'ok',
      run: () => act(`Uploaded: ${f.title.slice(0, 50)}`, () => closeIssue(up.number), { next: 'It moves to Posted here and on the board.' }) });
  } else if (item.kind === 'pick' && item.lane === 'SC' && item.source && /kick\.com\/([A-Za-z0-9_-]+)/.test(item.source)) {
    moves.push({ key: 'mk', label: 'Make Shorts from this', icon: <Play size={16} />, route: `/app/make?lane=SC&src=${encodeURIComponent(item.source)}&who=${encodeURIComponent((item.raw.who || '').split(' (')[0])}` });
  }
  return moves;
}

export const VideoCard: React.FC<{ item: Item; onOpen: (route: string) => void; compact?: boolean; showLane?: boolean; showStage?: boolean }> = ({ item, onOpen, compact, showLane = true, showStage = true }) => {
  const moves = useItemMoves(item);
  const [menu, setMenu] = useState(false);
  const clickable = !!item.route;
  return (
    <div className={`vcard${compact ? ' compact' : ''}${clickable ? ' click' : ''}`} onClick={() => clickable && onOpen(item.route!)}
         role={clickable ? 'link' : undefined} tabIndex={clickable ? 0 : undefined}
         onKeyDown={e => { if (clickable && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); onOpen(item.route!); } }}>
      {!compact && (
        <div className={`vthumb${item.vertical ? ' v' : ''}`} style={item.poster ? { backgroundImage: `url(${item.poster})` } : undefined}>
          {item.video ? <span className="vplay"><Play size={14} weight="fill" /></span> : <span className="vnone"><FilmSlate size={20} weight="duotone" /></span>}
          {item.score != null && <span className="vscore"><Score v={item.score} /></span>}
        </div>
      )}
      <div className="vbody">
        <div className="vmeta">{showLane && <LaneBadge code={item.lane} />}{showStage && (item.kind === 'lab' ? <span className="chip mute">Lab</span> : <StageChip stage={item.stage} />)}{item.at && <span className="faint">{ago(item.at)}</span>}</div>
        <div className="vtitle">{item.title}</div>
        {item.sub && <div className="vsub">{item.sub}</div>}
        {item.needsYou && <div className="vneed"><ArrowRight size={12} /> {item.needsYou}</div>}
        {!item.route && item.source && <a className="vsrc" href={item.source} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}>Source</a>}
        {moves.length > 0 && (
          <div className="vmoves" onClick={e => e.stopPropagation()}>
            {moves.slice(0, compact ? 1 : 2).map(m => (
              <button key={m.key} className={`mv ${m.tone || ''}`} onClick={() => (m.route ? onOpen(m.route) : m.run?.())}>{m.icon}{m.label}</button>
            ))}
            {moves.length > (compact ? 1 : 2) && (
              <span style={{ position: 'relative' }}>
                <button className="mv" aria-label="More actions" onClick={() => setMenu(!menu)}><DotsThree size={16} weight="bold" /></button>
                {menu && (
                  <div className="menu" onMouseLeave={() => setMenu(false)}>
                    {moves.slice(compact ? 1 : 2).map(m => (
                      <button key={m.key} onClick={() => { setMenu(false); m.route ? onOpen(m.route) : m.run?.(); }}>{m.icon}{m.label}</button>
                    ))}
                  </div>
                )}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export const STAGE_ORDER: Stage[] = [...STAGES];
