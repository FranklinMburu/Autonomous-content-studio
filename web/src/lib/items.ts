import { useMemo } from 'react';
import { useStudio } from '../context/StudioContext';
import { FILM_STAGE, LaneCode, Stage } from './channels';

// One list of every video (made, being made, or picked to make) across all channels. Home, Board and Library all
// read it, so a video looks and behaves the same everywhere.
export interface Item {
  key: string;
  lane: LaneCode;
  kind: 'short' | 'film' | 'motion' | 'pick' | 'topic' | 'lab';
  title: string;
  stage: Stage;
  at: string;
  route: string | null;          // where clicking it goes inside the app
  video: string | null;
  poster: string | null;
  vertical: boolean;
  score: number | null;
  reviewed: boolean;
  sub: string;                   // one line under the title
  needsYou: string | null;       // the one thing the owner should do, in words
  source: string | null;         // where it came from (stream, show, release)
  raw: any;
}

const NEEDS: Record<string, string> = { polish: 'Polish it (copy, paste)', review: 'Approve or repaint', ready: 'Upload it' };

export function useItems(): Item[] {
  const { films, shorts, motionVideos, labVideos, board, topics, isTopicMade } = useStudio();
  return useMemo(() => {
    const out: Item[] = [];
    for (const f of films) {
      const lane = (f.lane || 'HR') as LaneCode;
      out.push({
        key: `film:${f.id}`, lane, kind: 'film', title: f.title, stage: FILM_STAGE[f.status] || 'Making', at: f.at,
        route: `/app/films/${f.id}`, video: f.video?.url || null, poster: f.contact || null, vertical: false,
        score: null, reviewed: true, sub: f.style === 'explainer' ? 'Explainer' : f.status === 'draft' || f.status === 'polish' ? 'Draft' : 'Film',
        needsYou: NEEDS[f.status] || null, source: f.release?.url || null, raw: f,
      });
    }
    for (const s of shorts) {
      const reviewed = s.scores && s.scores.overall != null && s.checks?.length > 0;
      out.push({
        key: `short:${s.id}`, lane: s.lane, kind: 'short', title: s.title, stage: (s.stage || 'Review') as Stage, at: s.at,
        route: `/app/v/${encodeURIComponent(s.id)}`, video: s.video?.url || null, poster: s.poster || null, vertical: true,
        score: reviewed ? s.overall : null, reviewed: !!reviewed,
        sub: [s.streamer, s.seconds ? `${Math.round(s.seconds)} s` : '', s.dup ? 'earlier test batch' : ''].filter(Boolean).join(' · '),
        needsYou: s.dup ? null : s.stage === 'Review' ? (reviewed ? 'Watch and decide' : 'Not reviewed by the AI: watch and decide') : null,
        source: s.source?.vod || null, raw: s,
      });
    }
    for (const m of motionVideos) {
      out.push({
        key: `motion:${m.tag}`, lane: 'TE', kind: 'motion', title: m.title, stage: m.held ? 'Review' : 'Approved', at: m.at,
        route: `/app/v/${encodeURIComponent(m.tag)}`, video: m.video?.url || null, poster: m.contact || null, vertical: false,
        score: null, reviewed: true, sub: 'Motion explainer', needsYou: m.held ? 'A check failed: look and decide' : null, source: m.url, raw: m,
      });
    }
    // lab videos: early versions made in the lab before the workflows; never on the board, always marked Lab
    for (const v of labVideos) {
      out.push({
        key: v.id, lane: v.lane, kind: 'lab', title: v.title, stage: 'Approved', at: v.at, route: `/app/v/${encodeURIComponent(v.id)}`,
        video: v.video?.url || null, poster: v.poster || null, vertical: false, score: null, reviewed: true,
        sub: `Lab · ${v.note}`, needsYou: null, source: v.release, raw: v,
      });
    }
        // picks on the board that are not made yet (who's hot): SC / WC
    for (const c of board || []) {
      if (c.stage !== 'Picked' || c.videoId || !['SC', 'WC'].includes(c.lane)) continue;
      out.push({
        key: `pick:${c.lane}:${c.title}`, lane: c.lane, kind: 'pick', title: c.title, stage: 'Picked', at: c.date || '',
        route: null, video: null, poster: null, vertical: false, score: null, reviewed: true, sub: c.who || '',
        needsYou: null, source: c.source || null, raw: c,
      });
    }
    // the next Hidden Reasons topics in the queue: what the channel makes next
    topics.filter((t: string) => !isTopicMade(t)).slice(0, 5).forEach((t: string, i: number) => {
      out.push({
        key: `topic:${t}`, lane: 'HR', kind: 'topic', title: t, stage: 'Picked', at: '', route: '/app/topics', video: null,
        poster: null, vertical: false, score: null, reviewed: true, sub: i === 0 ? 'Next in the queue' : `#${i + 1} in the queue`,
        needsYou: null, source: null, raw: t,
      });
    });
    return out.sort((a, b) => (b.at || '').localeCompare(a.at || ''));
  }, [films, shorts, motionVideos, labVideos, board, topics, isTopicMade]);
}
