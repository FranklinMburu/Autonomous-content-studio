import React, { useState } from 'react';
import { FilmSlate, Code, Broadcast, Fire, ArrowsClockwise, Globe, Info, Laptop } from '@phosphor-icons/react';
import { useActions } from '../../context/ActionsContext';
import { useStudio } from '../../context/StudioContext';
import { ActButton, LaneBadge, Page } from '../kit';

const Card: React.FC<{ icon: React.ReactNode; lane?: string; title: string; text: React.ReactNode; children?: React.ReactNode; time?: string; id?: string }> =
  ({ icon, lane, title, text, children, time, id }) => (
    <div className="mk" id={id}>
      <div className="mk-h">{icon}<div><b>{title}</b>{lane && <LaneBadge code={lane} full />}</div></div>
      <p className="muted">{text}</p>
      {time && <p className="fine">{time}</p>}
      {children}
    </div>
  );

export const MakeView: React.FC<{ onNavigate: (r: string) => void }> = ({ onNavigate }) => {
  const { start, tasks } = useActions();
  const { topics, isTopicMade } = useStudio();
  const q = new URLSearchParams(window.location.search);
  const lane = q.get('lane');
  const src = q.get('src') || '';
  const kickFromSrc = (src.match(/kick\.com\/([A-Za-z0-9_-]+)/) || [])[1] || '';
  const [hrTopic, setHrTopic] = useState('');
  const [teTopic, setTeTopic] = useState('');
  const [platform, setPlatform] = useState<'kick' | 'twitch'>(/twitch\.tv/.test(src) ? 'twitch' : 'kick');
  const [channel, setChannel] = useState(platform === 'twitch' ? src : kickFromSrc);
  const [streamer, setStreamer] = useState(q.get('who') || kickFromSrc);
  const [top, setTop] = useState('8');
  const busy = (wf: string) => tasks.some(t => t.workflow === wf && !t.finished);
  const next = topics.find((t: string) => !isTopicMade(t));
  const scOk = streamer.trim().length > 0 && (platform === 'kick' ? /^[A-Za-z0-9_-]{2,40}$/.test(channel.trim()) : /^https:\/\/(www\.)?twitch\.tv\/videos\/\d+/.test(channel.trim()));

  React.useEffect(() => { if (lane) document.getElementById(`mk-${lane}`)?.scrollIntoView({ block: 'start' }); }, [lane]);

  return (
    <Page wide title="Make" sub="Start anything here. Each button starts the real pipeline on GitHub (free), and you can follow it live in the tray and under Runs.">
      <div className="mkgrid">
        <Card id="mk-SC" icon={<Broadcast size={22} weight="duotone" />} lane="SC" title="Shorts from a stream"
          text="Give a streamer's channel: the engine takes their newest real stream (skips gambling and short ones), finds the best moments, makes each Short and puts them on your board for review."
          time="About 25 minutes for 8-12 Shorts. Uses the free Gemini quota (it resets at 11:00 Nairobi time).">
          <div className="form">
            <label>Platform
              <select value={platform} onChange={e => setPlatform(e.target.value as any)}><option value="kick">Kick</option><option value="twitch">Twitch</option></select>
            </label>
            <label>{platform === 'kick' ? 'Kick channel name' : 'Twitch video link'}
              <input value={channel} onChange={e => setChannel(e.target.value)} placeholder={platform === 'kick' ? 'n3on' : 'https://www.twitch.tv/videos/…'} />
            </label>
            <label>Name viewers know
              <input value={streamer} onChange={e => setStreamer(e.target.value)} placeholder="N3on" maxLength={40} />
            </label>
            <label>How many Shorts
              <select value={top} onChange={e => setTop(e.target.value)}>{['4', '6', '8', '10', '12', '15'].map(n => <option key={n}>{n}</option>)}</select>
            </label>
          </div>
          <ActButton variant="pri" disabled={!scOk || busy('clips-stream.yml')} onRun={() => start(`Shorts from ${streamer.trim()}'s stream`, 'clips-stream.yml',
            { platform, channel: channel.trim(), vod: '', streamer: streamer.trim(), lane: 'SC', top },
            { next: 'The Shorts are on your board in Review (and in Streamer Clips → Videos).', target: '/app/c/SC?tab=videos' })}>
            {busy('clips-stream.yml') ? 'Making Shorts…' : 'Make Shorts'}
          </ActButton>
          <p className="fine">Not sure who? <button className="lnk" onClick={() => onNavigate('/app/c/SC?tab=ideas')}>See who's hot</button>.</p>
        </Card>

        <Card id="mk-HR" icon={<FilmSlate size={22} weight="duotone" />} lane="HR" title="A Hidden Reasons film"
          text={<>The timer already makes up to 5 a day from the queue. Start one now: {next ? <>the next topic is <b>{next}</b></> : 'the AI will pick a topic'}, or type another.</>}
          time="The draft is written in about 30-45 minutes, then waits for your polish. The same safety limits as the timer apply (no more than 2 waiting, 36 a week).">
          <div className="form one"><label>Topic (optional)<input value={hrTopic} onChange={e => setHrTopic(e.target.value)} placeholder={next || 'Why …'} maxLength={160} /></label></div>
          <ActButton variant="pri" disabled={busy('story-schedule.yml')} onRun={() => start(`Hidden Reasons: ${(hrTopic.trim() || next || 'next topic').slice(0, 60)}`, 'story-schedule.yml',
            hrTopic.trim() ? { topic: hrTopic.trim() } : {}, { next: 'Its draft will appear under Hidden Reasons → Polish.', target: '/app/polish' })}>Start it now</ActButton>
        </Card>

        <Card id="mk-TE" icon={<Code size={22} weight="duotone" />} lane="TE" title="A Tech Education video"
          text="Give a topic; the AI writes the script and a visual plan and the motion engine renders it with the channel's locked voice."
          time="About 1-2 hours. A failed check holds it for your review.">
          <div className="form one"><label>Topic<input value={teTopic} onChange={e => setTeTopic(e.target.value)} placeholder="What is a database?" maxLength={120} /></label></div>
          <ActButton variant="pri" disabled={teTopic.trim().length < 4 || busy('make-motion.yml')} onRun={() => start(`Tech Education: ${teTopic.trim().slice(0, 60)}`, 'make-motion.yml',
            { topic: teTopic.trim() }, { next: 'The video appears under Tech Education → Videos.', target: '/app/c/TE?tab=videos' })}>Make the video</ActButton>
        </Card>

        <Card icon={<Fire size={22} weight="duotone" />} title="Who's hot today"
          text="Ranks today's streamers (Streamer Clips) and the stories the world is watching (World Clips), and puts the top picks on the board."
          time="About 5 minutes.">
          <ActButton variant="sec" disabled={busy('clips-hot.yml')} onRun={() => start("Who's hot: rank today's streams and stories", 'clips-hot.yml', {},
            { next: 'Fresh picks are on the board and in each channel\'s Who\'s hot tab.', target: '/app/c/SC?tab=ideas' })}>Run who's hot</ActButton>
        </Card>

        <Card id="mk-WC" icon={<Globe size={22} weight="duotone" />} lane="WC" title="World Clips Shorts"
          text={<>Not startable yet, honestly: this lane picks stories today (see <button className="lnk" onClick={() => onNavigate('/app/c/WC?tab=ideas')}>its picks</button>), and its Shorts maker is being connected to your laptop helper, which downloads from YouTube from your home connection.</>}>
          <p className="fine"><Laptop size={13} /> When it is connected, this card starts it, and it will say when your laptop needs to be on.</p>
        </Card>

        <Card icon={<ArrowsClockwise size={22} weight="duotone" />} title="Refresh what the app shows"
          text="The app's data refreshes by itself every 30 minutes and after every run. Use this if you changed something on GitHub or in Notion and want it here now."
          time="About 1 minute.">
          <ActButton variant="sec" disabled={busy('site-feed.yml')} onRun={() => start('Refresh the app data', 'site-feed.yml', {}, { next: 'Reload the page to see the newest data.' })}>Refresh now</ActButton>
        </Card>
      </div>
      <p className="fine center"><Info size={13} /> Starting things needs GitHub connected on this device (Settings). Everything here is free.</p>
    </Page>
  );
};
