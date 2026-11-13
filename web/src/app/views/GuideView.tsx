import React from 'react';
import { Robot, User, Laptop, ArrowRight, Bell, Key, Kanban, FilmSlate, House, Plus, Books, GithubLogo, NotionLogo } from '@phosphor-icons/react';
import { CHANNELS, STAGES, STAGE_HELP } from '../../lib/channels';
import { ExtLink, LaneBadge, Page, Section } from '../kit';

const Who: React.FC<{ who: string }> = ({ who }) => who === 'you' ? <span className="who you"><User size={12} /> You</span>
  : who === 'laptop' ? <span className="who laptop"><Laptop size={12} /> Laptop</span> : <span className="who ai"><Robot size={12} /> AI</span>;

export const GuideView: React.FC<{ onNavigate: (r: string) => void }> = ({ onNavigate }) => (
  <Page title="How the studio works" sub="Five minutes to understand everything. No technical words needed.">
    <Section title="In one sentence">
      <p className="lead">Free AI makes videos for four YouTube channels on its own; you only make the few decisions that need taste, and you post.</p>
      <div className="gflow">
        <div><b>1. Pick</b><span>What to make: a topic queue, or who is hot today</span></div><ArrowRight size={16} />
        <div><b>2. Make</b><span>AI researches, writes, edits, renders and checks</span></div><ArrowRight size={16} />
        <div><b>3. Review</b><span>You watch and decide: approve or skip</span></div><ArrowRight size={16} />
        <div><b>4. Post</b><span>You post approved videos on YouTube</span></div>
      </div>
      <p className="muted">It costs $0: everything runs on free tiers (GitHub runs the work, free AI models think, a free GPU paints films).</p>
    </Section>

    <Section title="The channels" hint="Each channel is its own YouTube channel with its own kind of video. Tap one to open it.">
      <div className="guide-ch">
        {CHANNELS.map(c => (
          <div key={c.code} className="gch" style={{ ['--lc' as any]: c.color }}>
            <div className="gch-h"><LaneBadge code={c.code} /><b>{c.name}</b><span className="faint">{c.status}</span></div>
            <p className="muted">{c.short}. One video = {c.makes}.</p>
            <ol className="gsteps">{c.steps.map(s => <li key={s.name}><Who who={s.who} /><b>{s.name}</b> {s.text}</li>)}</ol>
            <button className="lnk" onClick={() => onNavigate(`/app/c/${c.code}`)}>Open {c.name} <ArrowRight size={13} /></button>
          </div>
        ))}
      </div>
    </Section>

    <Section title="The board: every video has a stage" hint="The same six stages here, on GitHub's side, and on your Notion Studio Board.">
      <div className="stages">{STAGES.map(s => <div key={s}><b>{s}</b><span>{STAGE_HELP[s]}</span></div>)}</div>
    </Section>

    <Section title="Where things are in this app">
      <div className="tiles">
        <button onClick={() => onNavigate('/app')}><House size={18} weight="duotone" /><b>Home</b><span>What needs you, what is being made, what comes next</span></button>
        <button onClick={() => onNavigate('/app/board')}><Kanban size={18} weight="duotone" /><b>Board</b><span>Every video by stage, like Notion</span></button>
        <button onClick={() => onNavigate('/app/library')}><Books size={18} weight="duotone" /><b>Library</b><span>Watch every video made</span></button>
        <button onClick={() => onNavigate('/app/make')}><Plus size={18} weight="duotone" /><b>Make</b><span>Start anything</span></button>
        <button onClick={() => onNavigate('/app/runs')}><FilmSlate size={18} weight="duotone" /><b>Runs</b><span>Each step of each run, live</span></button>
      </div>
    </Section>

    <Section title="App, GitHub and Notion: the same studio, three windows">
      <div className="three">
        <div><b>This app</b><p className="muted">The easiest window: watch, decide, start. It reads the studio every 30 minutes and after each run; what you start here is followed live.</p></div>
        <div><b><GithubLogo size={14} /> GitHub</b><p className="muted">Where the work really runs and is stored (the engine room). Every button here does exactly what you could do there.</p></div>
        <div><b><NotionLogo size={14} /> Notion</b><p className="muted">Your Studio Board. Clips cards are written by the pipeline; Hidden Reasons and Tech Education cards follow GitHub automatically. Moves made here reach Notion within a minute.</p></div>
      </div>
      <p className="fine">If the app and Notion ever disagree, GitHub is the truth: a moved Notion card for a Hidden Reasons film stays until something real happens to that film.</p>
    </Section>

    <Section title="Doing things from here">
      <div className="two">
        <div className="gbox"><Key size={18} weight="duotone" /><div><b>Connect GitHub once per device</b><p className="muted">Watching needs nothing. To approve, skip or start videos, connect GitHub in Settings (about 2 minutes). The key can only start the studio's work and comment; it never touches your files directly.</p>
          <button className="lnk" onClick={() => onNavigate('/app/settings')}>Open Settings <ArrowRight size={13} /></button></div></div>
        <div className="gbox"><Bell size={18} weight="duotone" /><div><b>Get told on your phone</b><p className="muted">Install the free GitHub app and turn on notifications for this repository: reviews, polishes and failures arrive as notifications, then open this app to act.</p>
          <ExtLink href="https://github.com/mobile">GitHub mobile</ExtLink></div></div>
      </div>
    </Section>

    <Section title="Questions you might have">
      <details className="faq"><summary>Why did the Notion cards change from Kai Cenat to N3on?</summary><p>They are different batches, not a replacement. The first batch (6 Shorts) came from Kai Cenat's Japan stream, which we used to prove the engine finds what fans clip. The next batches came from N3on's streams as a test of "a fresh stream, right after it ends". Every batch keeps its own cards; the newest are on top.</p></details>
      <details className="faq"><summary>What does "Not reviewed by the AI" mean?</summary><p>The free AI reviewer has a daily limit. When it runs out mid-run, the Short is still made, but unscored; it goes to Review so you decide. The limit resets every day at about 11:00 Nairobi time.</p></details>
      <details className="faq"><summary>Is anything posted to YouTube automatically?</summary><p>No. Nothing is posted without you. Approved videos wait for you to post them, and the rights of every clip are checked before posting.</p></details>
      <details className="faq"><summary>Why does World Clips need my laptop?</summary><p>YouTube blocks downloads from cloud servers. Your laptop helper (a small free program on your laptop) downloads only the few minutes we need, from your home connection, every 10 minutes while the laptop is on.</p></details>
      <details className="faq"><summary>Does this cost anything?</summary><p>No. GitHub runs the work free for this public repository, the AI models are free tiers, and the film GPU is Kaggle's free weekly hours. The studio stops itself before any limit.</p></details>
    </Section>
  </Page>
);
