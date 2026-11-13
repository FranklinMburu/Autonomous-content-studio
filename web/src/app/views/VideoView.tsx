import React, { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, CheckCircle, Copy, XCircle, ArrowSquareOut, DownloadSimple, Info } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';
import { useItems } from '../../lib/items';
import { channelOf } from '../../lib/channels';
import { ago, plainJob, plainStep, workflowInfo, dur } from '../../lib/journey';
import { ActButton, Empty, ExtLink, LaneBadge, Page, Player, Score, Section, StageChip } from '../kit';
import { useItemMoves } from '../videos';

const SCORE_WORDS: Record<string, string> = { moment: 'The moment itself', hook: 'First seconds', title: 'Title', framing: 'Framing', captions: 'Text on screen',
  audio: 'Sound', pacing: 'Pace', ending: 'Ending', originality: 'Originality', overall: 'Overall' };
const CHECK_WORDS: Record<string, string> = { hook: 'Grabs you in 3 seconds', tension: 'Real stakes or surprise', real: 'Real people, not a game',
  share: 'Worth sending to a friend', minors: 'No minors shown wrongly', honest: 'Title matches what happens', layout: 'Clear on a phone' };

const Copyable: React.FC<{ label: string; text: string }> = ({ label, text }) => {
  const [ok, setOk] = useState(false);
  return (
    <div className="copy">
      <div className="copy-h"><span className="faint">{label}</span>
        <button className="lnk" onClick={() => { navigator.clipboard?.writeText(text).then(() => { setOk(true); setTimeout(() => setOk(false), 1500); }); }}>
          <Copy size={13} /> {ok ? 'Copied' : 'Copy'}</button></div>
      <div className="copy-b">{text}</div>
    </div>
  );
};

export const VideoView: React.FC<{ id: string; onNavigate: (r: string) => void }> = ({ id, onNavigate }) => {
  const { studio, runs, loading } = useStudio();
  const items = useItems();
  const item = items.find(i => (i.kind === 'short' && i.raw.id === id) || (i.kind === 'motion' && i.raw.tag === id));
  const moves = useItemMoves(item || ({ kind: 'none', raw: {} } as any));
  const [steps, setSteps] = useState<any[] | null>(null);

  // the run that made it: recorded in the Short (new runs), else the clips run that finished just before its release
  const run = useMemo(() => {
    if (!item) return null;
    if (item.raw.run) return runs.find((r: any) => r.id === item.raw.run) || { id: item.raw.run, workflow: item.kind === 'short' ? 'Clips, a fresh stream to Shorts (find -> make -> review)' : '' };
    const t = new Date(item.at).getTime();
    return runs.filter((r: any) => workflowInfo(r.workflow).lane === item.lane && new Date(r.started).getTime() < t && t - new Date(r.updated).getTime() < 20 * 60e3)
      .sort((a: any, b: any) => b.started.localeCompare(a.started))[0] || null;
  }, [item, runs]);

  useEffect(() => {
    if (!run) return;
    studio.runSteps(run.id).then(setSteps).catch(() => setSteps([]));
  }, [run?.id]);

  if (!item) {
    return <Page title="Video"><Empty title={loading ? 'Loading…' : 'This video is not in the studio data'} text="It may be very new (data refreshes every 30 minutes) or removed."
      action={<button className="btn sec" onClick={() => onNavigate('/app/library')}>Open the Library</button>} /></Page>;
  }
  const s = item.raw;
  const ch = channelOf(item.lane)!;
  const vertical = item.vertical;
  const journey = (steps || []).map(x => ({ ...x, plain: plainStep(run?.workflow || '', x.name) })).filter(x => x.plain);

  return (
    <Page wide
      title={<span className="vv-title">{item.title}</span>}
      sub={<span className="vmeta"><LaneBadge code={item.lane} full /><StageChip stage={item.stage} />{item.at && <span className="faint">made {ago(item.at)}</span>}</span>}
>
      <button className="lnk back" onClick={() => window.history.length > 1 ? window.history.back() : onNavigate(`/app/c/${item.lane}`)}><ArrowLeft size={14} /> Back</button>
      <div className={`vv${vertical ? ' v' : ''}`}>
        <div className="vv-player">
          <Player src={item.video} vertical={vertical} poster={item.poster} title={item.title} />
          <div className="vv-dl">
            {item.video && <a className="lnk" href={item.video} target="_blank" rel="noopener noreferrer"><DownloadSimple size={14} /> Download</a>}
            {s.release && <ExtLink href={s.release}>Release on GitHub</ExtLink>}
            {s.url && <ExtLink href={s.url}>Release on GitHub</ExtLink>}
            {s.card?.url && <ExtLink href={s.card.url}>Card in Notion</ExtLink>}
          </div>
        </div>
        <div className="vv-side">
          <div className="decide">
            <div className="decide-h">
              {item.score != null ? <><Score v={item.score} size="lg" /><div><b>{s.band || ''}</b><span className="faint">The AI reviewer's guess at reaching 250K+ views (not a measurement)</span></div></>
                : item.kind === 'short' ? <div><b>Not scored</b><span className="faint">The AI reviewer could not watch this one (its free daily quota ran out). Watch it and decide yourself.</span></div>
                : <div><b>{ch.name}</b><span className="faint">{ch.makes}</span></div>}
            </div>
            {item.needsYou && <div className="vneed big">{item.needsYou}</div>}
            <div className="decide-b">
              {moves.map(m => m.route
                ? <button key={m.key} className={`btn ${m.tone === 'ok' ? 'pri' : 'sec'}`} onClick={() => onNavigate(m.route!)}>{m.icon}{m.label}</button>
                : <ActButton key={m.key} variant={m.tone === 'ok' ? 'pri' : m.tone === 'bad' ? 'danger' : 'sec'} onRun={() => m.run!()}>{m.icon}{m.label}</ActButton>)}
              {!moves.length && <span className="faint">Nothing to decide here.</span>}
            </div>
            {item.kind === 'short' && <p className="fine">Approve, skip and posted move the card here and on the Notion board. Nothing is posted to YouTube by the app: you post approved Shorts yourself.</p>}
          </div>

          {s.note && <div className="note"><Info size={15} /><div><b>Before you post</b><p>{s.note}</p></div></div>}

          {item.kind === 'short' && (
            <>
              <Copyable label="Title" text={s.title} />
              {s.description && <Copyable label="Description and hashtags" text={s.description} />}
            </>
          )}
          {s.source?.vod && (
            <p className="muted small">From <ExtLink href={`${s.source.vod}${s.source.vod.includes('?') ? '&' : '?'}t=${Math.round(s.source.start)}`}>{s.streamer || 'the stream'} at {dur(s.source.start)}</ExtLink>
              {s.seconds ? ` · ${Math.round(s.seconds)} s long` : ''}</p>
          )}
        </div>
      </div>

      {item.kind === 'short' && s.scores && s.scores.overall != null && (
        <Section title="What the AI reviewer saw" hint="A second AI that did not make the Short watched it with sound and judged it against the best clip channels.">
          <div className="two">
            <div className="rchecks">
              {(s.checks || []).map((c: any) => (
                <div key={c.name} className="check">{c.passed ? <CheckCircle size={16} weight="fill" color="var(--ok)" /> : <XCircle size={16} weight="fill" color="var(--bad)" />}
                  <div><b>{CHECK_WORDS[c.name] || c.name}</b><span className="faint">{c.evidence}</span></div></div>
              ))}
            </div>
            <div>
              <div className="sbars">
                {Object.entries(s.scores).filter(([k]) => k !== 'overall').map(([k, v]: any) => (
                  <div key={k} className="bar-r"><span>{SCORE_WORDS[k] || k}</span><div className="bar-t"><i style={{ width: `${(v || 0) * 10}%` }} /></div><b>{v}</b></div>
                ))}
              </div>
              {s.fix && <div className="note"><Info size={15} /><div><b>What would make it better</b><p>{s.fix}</p></div></div>}
            </div>
          </div>
        </Section>
      )}

      <Section title="Its journey" hint={run ? `How this ${ch.format.toLowerCase()} was made, step by step (run #${run.number || run.id}).` : 'The steps that made it.'}
               right={run ? <button className="lnk" onClick={() => onNavigate(`/app/runs/${run.id}`)}>Open the run</button> : null}>
        <ol className="journey">
          {ch.steps.map((st, i) => <li key={i} className={st.who}><b>{st.name}</b><span>{st.text}</span><em>{st.who === 'you' ? 'You' : st.who === 'laptop' ? 'Your laptop' : 'AI'}</em></li>)}
        </ol>
        {journey.length > 0 && (
          <details className="raw-steps"><summary>The exact steps of the run ({journey.length})</summary>
            <ul>{journey.map((x, i) => <li key={i} className={x.state}><span>{plainJob(x.job)}</span> {x.plain} <em>{x.seconds != null ? dur(x.seconds) : x.state}</em></li>)}</ul>
          </details>
        )}
      </Section>
      <a className="lnk" href={s.release || s.url} target="_blank" rel="noopener noreferrer">All files of this batch <ArrowSquareOut size={12} /></a>
    </Page>
  );
};
