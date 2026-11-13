import React from 'react';
import { ArrowRight, CheckCircle, Lightning, Plus, BookOpenText, WarningCircle } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';
import { useActions } from '../../context/ActionsContext';
import { useItems } from '../../lib/items';
import { CHANNELS } from '../../lib/channels';
import { workflowInfo, ago } from '../../lib/journey';
import { Empty, LaneBadge, Page, Section } from '../kit';
import { VideoCard } from '../videos';

export const HomeView: React.FC<{ onNavigate: (r: string) => void }> = ({ onNavigate }) => {
  const { runs, loading, nextSlots, topics, isTopicMade, reviewItems, polishItems, uploadItems, alerts, feedBuilt } = useStudio();
  const { hasToken } = useActions();
  const items = useItems();
  const needs = items.filter(i => i.needsYou);
  const making = runs.filter((r: any) => r.state === 'running' || r.state === 'queued');
  const made = items.filter(i => i.video && i.kind !== 'pick').slice(0, 8);
  const nextTopics = topics.filter((t: string) => !isTopicMade(t)).slice(0, 3);
  const picks = items.filter(i => i.kind === 'pick').slice(0, 4);
  const hour = new Date().getHours();
  const hello = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  return (
    <Page
      title={`${hello}, Franklin`}
      sub={loading ? 'Loading your studio…' : needs.length ? `${needs.length} thing${needs.length > 1 ? 's' : ''} need${needs.length > 1 ? '' : 's'} you. Everything else is running on its own.` : 'Nothing needs you right now. Everything is running on its own.'}
      actions={<><button className="btn sec" onClick={() => onNavigate('/app/guide')}><BookOpenText size={16} /> How it works</button>
               <button className="btn pri" onClick={() => onNavigate('/app/make')}><Plus size={16} weight="bold" /> Make something</button></>}
      wide
    >
      {!hasToken && (
        <div className="banner" onClick={() => onNavigate('/app/settings')} role="button" tabIndex={0}>
          <Lightning size={18} weight="duotone" />
          <div><b>You can watch everything. To act from here, connect GitHub once on this device.</b>
            <span className="muted"> Approve, skip, start videos and move cards with one tap. About 2 minutes.</span></div>
          <ArrowRight size={16} />
        </div>
      )}
      {alerts.length > 0 && (
        <div className="banner bad" onClick={() => onNavigate('/app/guard')} role="button" tabIndex={0}>
          <WarningCircle size={18} weight="duotone" /><div><b>A run needs attention.</b> <span className="muted">{String(alerts[0].text || '').split('\n')[0].slice(0, 140)}</span></div><ArrowRight size={16} />
        </div>
      )}

      <div className="chgrid">
        {CHANNELS.map(c => {
          const mine = items.filter(i => i.lane === c.code && i.kind !== 'topic');
          const need = mine.filter(i => i.needsYou).length;
          return (
            <button key={c.code} className="chcard" style={{ ['--lc' as any]: c.color }} onClick={() => onNavigate(`/app/c/${c.code}`)}>
              <div className="chcard-h"><LaneBadge code={c.code} /><b>{c.name}</b></div>
              <div className="chcard-s">{c.short}</div>
              <div className="chcard-n">
                <span><b>{mine.filter(i => i.video).length}</b> made</span>
                <span className={need ? 'hot' : ''}><b>{need}</b> need you</span>
              </div>
              <div className="chcard-st">{c.status}</div>
            </button>
          );
        })}
      </div>

      <Section title="Needs you" hint="Each one is a single decision. The rest of the studio keeps going meanwhile."
               right={needs.length > 6 ? <button className="lnk" onClick={() => onNavigate('/app/board?stage=needs')}>See all {needs.length} <ArrowRight size={13} /></button> : null}>
        {needs.length ? (
          <div className="vlist">{needs.slice(0, 6).map(i => <VideoCard key={i.key} item={i} onOpen={onNavigate} />)}</div>
        ) : (
          <Empty icon={<CheckCircle size={20} weight="duotone" color="var(--ok)" />} title="All clear"
                 text={`Reviews ${reviewItems.length}, polishes ${polishItems.length}, uploads ${uploadItems.length}: nothing waiting on you.`} />
        )}
      </Section>

      <div className="two">
        <Section title="Making now" hint="Live from GitHub. Tap one to follow each step."
                 right={<button className="lnk" onClick={() => onNavigate('/app/runs')}>All runs <ArrowRight size={13} /></button>}>
          {making.length ? (
            <div className="rows">
              {making.slice(0, 5).map((r: any) => {
                const w = workflowInfo(r.workflow);
                return (
                  <button key={r.id} className="row" onClick={() => onNavigate(`/app/runs/${r.id}`)}>
                    <span className="live-dot" />
                    <div className="row-b"><b>{w.what}</b><span className="faint">{r.title !== r.workflow ? r.title.slice(0, 80) + ' · ' : ''}started {ago(r.started)}</span></div>
                    {w.lane && <LaneBadge code={w.lane} />}
                  </button>
                );
              })}
            </div>
          ) : <Empty title="Nothing running this minute" text="Hidden Reasons starts on its timer; anything you start appears here within a minute." />}
        </Section>

        <Section title="Coming next" hint="What the studio will make, in order.">
          <div className="rows">
            {nextSlots[0] && nextTopics[0] && (
              <button className="row" onClick={() => onNavigate('/app/topics')}>
                <LaneBadge code="HR" />
                <div className="row-b"><b>{nextTopics[0]}</b><span className="faint">Hidden Reasons · next timer at {nextSlots[0].toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span></div>
              </button>
            )}
            {nextTopics.slice(1).map((t: string) => (
              <button key={t} className="row" onClick={() => onNavigate('/app/topics')}><LaneBadge code="HR" /><div className="row-b"><b>{t}</b><span className="faint">Hidden Reasons · in the queue</span></div></button>
            ))}
            {picks.map(p => (
              <div key={p.key} className="row"><LaneBadge code={p.lane} /><div className="row-b"><b>{p.title}</b><span className="faint">Picked by who's hot{p.sub ? ' · ' + p.sub : ''}</span></div></div>
            ))}
            {!nextTopics.length && !picks.length && <Empty title="The queues are empty" text="Add a topic or run who's hot from Make." />}
          </div>
        </Section>
      </div>

      <Section title="Just made" hint="Tap any video to watch it here." right={<button className="lnk" onClick={() => onNavigate('/app/library')}>Library <ArrowRight size={13} /></button>}>
        {made.length ? <div className="vgrid">{made.map(i => <VideoCard key={i.key} item={i} onOpen={onNavigate} />)}</div>
          : <Empty title="No videos yet" />}
      </Section>
      {feedBuilt && <p className="fine center">Data refreshed {ago(feedBuilt)} (it refreshes every 30 minutes and after every run).</p>}
    </Page>
  );
};
