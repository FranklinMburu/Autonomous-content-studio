import React, { useState } from 'react';
import { Plus, Trash, ArrowRight, Fire, Lightning, Eye, MagicWand, UploadSimple, CalendarDots, Archive, Laptop } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';
import { useActions } from '../../context/ActionsContext';
import { channelOf, LaneCode } from '../../lib/channels';
import { useItems } from '../../lib/items';
import { workflowInfo, ago } from '../../lib/journey';
import { ActButton, Empty, LaneBadge, Page, Section, Tabs, ExtLink } from '../kit';
import { VideoCard } from '../videos';
import { BoardView } from './BoardView';

export const ChannelView: React.FC<{ code: string; onNavigate: (r: string) => void }> = ({ code, onNavigate }) => {
  const ch = channelOf(code);
  const items = useItems();
  const { runs, topics, isTopicMade, hot, nextSlots, scheduleData, board } = useStudio();
  const { start } = useActions();
  const q = new URLSearchParams(window.location.search);
  const [tab, setTabState] = useState(q.get('tab') || 'overview');
  const [newTopic, setNewTopic] = useState('');
  const setTab = (t: string) => { setTabState(t); window.history.replaceState({}, '', window.location.pathname + (t === 'overview' ? '' : `?tab=${t}`)); };
  if (!ch) return <Page title="Channel"><Empty title="No such channel" action={<button className="btn sec" onClick={() => onNavigate('/app')}>Home</button>} /></Page>;

  const mine = items.filter(i => i.lane === ch.code);
  const videos = mine.filter(i => i.video);
  const need = mine.filter(i => i.needsYou);
  const myRuns = runs.filter((r: any) => workflowInfo(r.workflow).lane === ch.code);
  const queue = ch.code === 'HR' ? topics.filter((t: string) => !isTopicMade(t)) : [];

  const ideas = () => {
    if (ch.code === 'HR') return (
      <>
        <Section title="Topic queue" hint={`The timer makes these in order${nextSlots[0] ? `; the next one starts at ${nextSlots[0].toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : ''}. ${scheduleData?.utc?.length || 5} a day at most.`}>
          <div className="addrow">
            <input value={newTopic} onChange={e => setNewTopic(e.target.value)} placeholder="Add a topic, e.g. Why sailors feared whistling at sea" maxLength={160} aria-label="New topic" />
            <ActButton variant="pri" disabled={newTopic.trim().length < 3} onRun={async () => {
              await start(`Add topic: ${newTopic.trim().slice(0, 50)}`, 'studio-action.yml', { action: 'topic-add', args: JSON.stringify({ channel: 'HR', topic: newTopic.trim() }) },
                { next: 'It is now at the end of the queue.' });
              setNewTopic('');
            }}><Plus size={15} /> Add</ActButton>
          </div>
          <ol className="queue">
            {queue.map((t: string, i: number) => (
              <li key={t}><span className="qn">{i + 1}</span><span className="qt">{t}</span>
                <ActButton small variant="ghost" title="Remove from the queue" confirm={`Remove "${t}" from the queue?`}
                  onRun={() => start(`Remove topic: ${t.slice(0, 50)}`, 'studio-action.yml', { action: 'topic-remove', args: JSON.stringify({ channel: 'HR', topic: t }) })}>
                  <Trash size={14} /></ActButton>
                <ActButton small variant="ghost" title="Make this one now" onRun={() => start(`Make now: ${t.slice(0, 50)}`, 'story-schedule.yml', { topic: t }, { next: 'A draft appears in Polish when it is written (about 30-45 min).' })}>
                  <Lightning size={14} /> Now</ActButton>
              </li>
            ))}
            {!queue.length && <Empty title="The queue is empty" text="Add a topic above; when empty, the timer asks the AI for new ideas." />}
          </ol>
        </Section>
      </>
    );
    if (ch.code === 'SC') {
      const list = (hot?.streamers || []).filter((r: any) => r.in_our_lane !== false).slice(0, 15);
      return (
        <Section title="Who's hot right now" hint={hot?.at ? `Ranked ${ago(hot.at)} by what is getting views (gambling and off-niche skipped).` : 'Run who\'s hot to rank today\'s streamers.'}
          right={<ActButton variant="sec" onRun={() => start("Who's hot: rank today's streams and stories", 'clips-hot.yml', {}, { next: 'New picks are on the board and here.' })}><Fire size={15} /> Run who's hot</ActButton>}>
          {list.length ? (
            <div className="rows">
              {list.map((r: any, i: number) => (
                <div key={r.login} className="row">
                  <span className="qn">{i + 1}</span>
                  <div className="row-b"><b>{r.login} <span className="faint">({r.site})</span></b>
                    <span className="faint">score {r.score}{(r.ref_titles || r.kick_top || [])[0] ? ' · ' + String((r.ref_titles || r.kick_top)[0]).slice(0, 90) : ''}</span></div>
                  {r.site === 'kick' && <button className="btn sec sm" onClick={() => onNavigate(`/app/make?lane=SC&src=${encodeURIComponent('https://kick.com/' + r.login)}&who=${encodeURIComponent(r.login)}`)}>Make Shorts <ArrowRight size={13} /></button>}
                </div>
              ))}
            </div>
          ) : <Empty icon={<Fire size={20} weight="duotone" />} title="No ranking saved yet" text="Who's hot now saves its lists for this page. Run it once (about 5 minutes)." />}
          {(board || []).filter((c: any) => c.lane === 'SC' && c.stage === 'Picked').length > 0 && (
            <>
              <h3 className="h3">Picked on the board</h3>
              <div className="vlist">{mine.filter(i => i.kind === 'pick').map(i => <VideoCard key={i.key} item={i} onOpen={onNavigate} />)}</div>
            </>
          )}
        </Section>
      );
    }
    if (ch.code === 'WC') {
      const list = (hot?.world?.sources || []).slice(0, 15);
      return (
        <>
          <div className="banner"><Laptop size={18} weight="duotone" /><div><b>World Clips needs your laptop on.</b> <span className="muted">YouTube blocks cloud servers, so your laptop helper downloads only the minutes we need (every 10 minutes when on). Making Shorts for this lane is the next step being connected.</span></div></div>
          <Section title="What the world is watching" hint={hot?.at ? `Ranked ${ago(hot.at)}: videos far above their show's usual views, plus Google Trends and Wikipedia.` : ''}
            right={<ActButton variant="sec" onRun={() => start("Who's hot: rank today's streams and stories", 'clips-hot.yml', {}, { next: 'New picks are on the board and here.' })}><Fire size={15} /> Run who's hot</ActButton>}>
            {list.length ? (
              <div className="rows">{list.map((e: any, i: number) => (
                <a key={e.url || i} className="row" href={e.url} target="_blank" rel="noopener noreferrer">
                  <span className="qn">{i + 1}</span>
                  <div className="row-b"><b>{e.title}</b><span className="faint">{e.channel || e.handle} · {Number(e.views || 0).toLocaleString()} views · {e.lift}x usual{e.trend_match?.length ? ' · trend: ' + e.trend_match.join(', ') : ''}</span></div>
                </a>
              ))}</div>
            ) : <div className="vlist">{mine.filter(i => i.kind === 'pick').map(i => <VideoCard key={i.key} item={i} onOpen={onNavigate} />)}
                  {!mine.filter(i => i.kind === 'pick').length && <Empty title="No picks yet" text="Run who's hot." />}</div>}
          </Section>
        </>
      );
    }
    if (ch.code === 'TE') return (
      <Section title="Episodes" hint="Each episode is a folder with its script and visual plan. Start a new one from Make.">
        <div className="rows">
          <div className="row"><LaneBadge code="TE" /><div className="row-b"><b>001 · What is an API?</b><span className="faint">The approved first episode (engine v3)</span></div>
            <ActButton variant="sec" small onRun={() => start('Make: What is an API? (Tech Education)', 'make-motion.yml', { episode: 'episodes/tech_education/001-what-is-an-api' }, { next: 'The video appears in Tech Education → Videos.' })}>Make it</ActButton></div>
        </div>
        <button className="btn pri" style={{ marginTop: 12 }} onClick={() => onNavigate('/app/make?lane=TE')}><Plus size={15} /> New episode from a topic</button>
      </Section>
    );
    return <Empty title="Paused" text="The Body Science pilot is paused; its finished videos are under Videos." />;
  };

  return (
    <Page wide
      title={<span className="chtitle"><LaneBadge code={ch.code} /> {ch.name}</span>}
      sub={`${ch.short}. ${ch.status}.`}
      actions={ch.makeWorkflow || ch.code === 'SC' ? <button className="btn pri" onClick={() => onNavigate(`/app/make?lane=${ch.code}`)}><Plus size={15} weight="bold" /> Make {ch.format === 'Short' ? 'Shorts' : 'a video'}</button> : null}>
      <Tabs value={tab} onChange={setTab} tabs={[
        { key: 'overview', label: 'Overview' }, { key: 'board', label: 'Board', count: mine.filter(i => i.kind !== 'topic').length },
        { key: 'videos', label: 'Videos', count: videos.length }, { key: 'ideas', label: ch.ideasLabel },
        { key: 'runs', label: 'Runs', count: myRuns.length }]} />

      {tab === 'overview' && (
        <>
          <div className="chstats">
            <div><b>{videos.length}</b><span>videos made</span></div>
            <div className={need.length ? 'hot' : ''}><b>{need.length}</b><span>need you</span></div>
            <div><b>{myRuns.filter((r: any) => r.state === 'running' || r.state === 'queued').length}</b><span>running now</span></div>
            <div><b>{ch.cadence}</b><span>how often</span></div>
          </div>
          {need.length > 0 && <Section title="Needs you"><div className="vlist">{need.slice(0, 6).map(i => <VideoCard key={i.key} item={i} onOpen={onNavigate} showLane={false} />)}</div></Section>}
          <Section title="How a video is made here" hint={`One ${ch.makes}.`}>
            <ol className="journey">{ch.steps.map((st, i) => <li key={i} className={st.who}><b>{st.name}</b><span>{st.text}</span><em>{st.who === 'you' ? 'You' : st.who === 'laptop' ? 'Your laptop' : 'AI'}</em></li>)}</ol>
          </Section>
          {ch.code === 'HR' && (
            <Section title="Film desk" hint="The Hidden Reasons steps that need a person.">
              <div className="tiles">
                <button onClick={() => onNavigate('/app/review')}><Eye size={18} weight="duotone" /><b>Review</b><span>Approve or repaint weak shots</span></button>
                <button onClick={() => onNavigate('/app/polish')}><MagicWand size={18} weight="duotone" /><b>Polish</b><span>Copy to Claude, paste back</span></button>
                <button onClick={() => onNavigate('/app/upload')}><UploadSimple size={18} weight="duotone" /><b>Upload</b><span>Finished films to post</span></button>
                <button onClick={() => onNavigate('/app/schedule')}><CalendarDots size={18} weight="duotone" /><b>Schedule</b><span>The 5 daily start times</span></button>
                <button onClick={() => onNavigate('/app/memory')}><Archive size={18} weight="duotone" /><b>Memory</b><span>Cast, places, music used</span></button>
              </div>
            </Section>
          )}
          <Section title="Latest videos" right={<button className="lnk" onClick={() => setTab('videos')}>All {videos.length} <ArrowRight size={13} /></button>}>
            {videos.length ? <div className="vgrid">{videos.slice(0, 4).map(i => <VideoCard key={i.key} item={i} onOpen={onNavigate} showLane={false} />)}</div>
              : <Empty title="No videos yet" text={ch.code === 'WC' ? 'This lane makes picks so far; Shorts come next.' : 'Start one with Make.'} />}
          </Section>
        </>
      )}
      {tab === 'board' && <BoardView onNavigate={onNavigate} lane={ch.code as LaneCode} embedded />}
      {tab === 'videos' && (videos.length ? <div className="vgrid" style={{ marginTop: 16 }}>{videos.map(i => <VideoCard key={i.key} item={i} onOpen={onNavigate} showLane={false} />)}</div>
        : <Empty title="No videos yet" />)}
      {tab === 'ideas' && ideas()}
      {tab === 'runs' && (
        <div className="rows" style={{ marginTop: 16 }}>
          {myRuns.map((r: any) => (
            <button key={r.id} className="row" onClick={() => onNavigate(`/app/runs/${r.id}`)}>
              <span className={`sdot ${r.state}`} />
              <div className="row-b"><b>{workflowInfo(r.workflow).what}</b><span className="faint">{r.title !== r.workflow ? r.title.slice(0, 90) + ' · ' : ''}{ago(r.started)} · {r.minutes} min</span></div>
              <span className={`chip ${r.state === 'success' ? 'ok' : r.state === 'failure' ? 'bad' : 'run'}`}>{({ success: 'Done', failure: 'Failed', running: 'Running', queued: 'Waiting', cancelled: 'Stopped' } as any)[r.state] || r.state}</span>
            </button>
          ))}
          {!myRuns.length && <Empty title="No recent runs" text="The last 30 runs of the whole studio are kept here." />}
          <ExtLink href="https://github.com/FranklinMburu/Autonomous-content-studio/actions">All runs on GitHub</ExtLink>
        </div>
      )}
    </Page>
  );
};
