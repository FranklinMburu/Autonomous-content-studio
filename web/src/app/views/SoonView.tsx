import React from 'react';
import {
  ChartLineUp,
  TrendUp,
  PaperPlaneTilt,
  ImageSquare,
  MicrophoneStage,
  Translate,
  Wrench,
  ArrowLeft,
  ArrowSquareOut,
  GithubLogo,
} from '@phosphor-icons/react';

interface SoonViewProps {
  page: 'analytics' | 'trends' | 'publish' | 'thumbnails' | 'voices' | 'languages';
  onBackToFilms?: () => void;
}

const SOON_CONFIGS: Record<
  string,
  {
    title: string;
    icon: any;
    line: string;
    rows: Array<{ title: string; desc: string }>;
    needs: string;
  }
> = {
  analytics: {
    title: 'Analytics',
    icon: ChartLineUp,
    line: 'See how every film performs on YouTube, and let the studio learn what your audience loves.',
    rows: [
      { title: 'Views and watch time per film', desc: 'Which stories people finish, rewatch and share.' },
      { title: 'Learns from results', desc: 'The topic list moves the best kinds of story to the front.' },
      { title: 'Weekly digest', desc: 'One short summary every Monday, in the app and on GitHub.' },
    ],
    needs: 'a read-only YouTube Analytics connection (free). Nothing here is live yet; no numbers are shown until it is.',
  },
  trends: {
    title: 'Trends',
    icon: TrendUp,
    line: 'Find true stories people are searching for, before you run out of topics.',
    rows: [
      { title: 'Rising history searches', desc: 'Queries gaining traction on search engines and social platforms.' },
      { title: 'Checked against the channel memory', desc: 'Discards topics already covered or planned.' },
      { title: 'One click to queue', desc: 'Adds the verified story directly into the daily cron pipeline.' },
    ],
    needs: 'a free trends source and a topic-scoring step in the pipeline.',
  },
  publish: {
    title: 'Publish',
    icon: PaperPlaneTilt,
    line: 'Upload finished films to YouTube for you, after you approve them.',
    rows: [
      { title: 'Approve once, upload automatically', desc: 'Hands-off publishing directly to YouTube Shorts.' },
      { title: 'Title, description and sources filled in', desc: 'Metadata formatted and tagged automatically.' },
      { title: 'Never posts without you', desc: 'Zero unapproved drafts ever leave the studio.' },
    ],
    needs: 'the YouTube Data API upload scope and a sign-in.',
  },
  thumbnails: {
    title: 'Thumbnails',
    icon: ImageSquare,
    line: 'A cover for every film, painted from its strongest shot.',
    rows: [
      { title: 'Three options per film', desc: 'High-contrast 9:16 vertical cover variations.' },
      { title: 'Same faces as the film', desc: 'InstantID character consistency enforced on covers.' },
      { title: 'Text kept short and readable', desc: 'Designed for high mobile click-through rates.' },
    ],
    needs: 'a thumbnail step in the Lab.',
  },
  voices: {
    title: 'Voices',
    icon: MicrophoneStage,
    line: 'Choose and test narrator voices for each channel.',
    rows: [
      { title: 'Listen side by side', desc: 'Compare tone, cadence and historic gravitas.' },
      { title: 'One voice per channel', desc: 'Distinct sonic identity across entire episode series.' },
      { title: 'Free, open models only', desc: 'Zero per-minute audio generation fees.' },
    ],
    needs: 'a voice library page in the Lab.',
  },
  languages: {
    title: 'Languages',
    icon: Translate,
    line: 'The same film in more languages, with the same facts.',
    rows: [
      { title: 'Translated and re-checked script', desc: 'Culturally adapted and verified narrative.' },
      { title: 'New narration', desc: 'Native-speaker audio generation per language.' },
      { title: 'Subtitles included', desc: 'Synchronized multi-language captions.' },
    ],
    needs: 'a translation step + voice per language.',
  },
};

export const SoonView: React.FC<SoonViewProps> = ({ page, onBackToFilms }) => {
  const cfg = SOON_CONFIGS[page] || SOON_CONFIGS.analytics;
  const IconComp = cfg.icon;

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="soonpage">
        <div className="sic">
          <IconComp size={30} weight="duotone" />
        </div>

        <span className="chip" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--tx2)' }}>
          Planned
        </span>

        <h1 className="st1">{cfg.title}</h1>
        <p className="sp1">{cfg.line}</p>

        <div className="srows">
          {cfg.rows.map((row, idx) => (
            <div key={idx} className="sr2">
              <IconComp size={20} weight="duotone" className="ic" />
              <div>
                <b>{row.title}</b>
                <span>{row.desc}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="needs">
          <Wrench size={16} weight="duotone" className="ic" />
          <span>
            <b>What it needs:</b> {cfg.needs}
          </span>
        </div>

        <div className="sbtns">
          <a
            href="https://github.com/FranklinMburu/Autonomous-content-studio"
            target="_blank"
            rel="noopener noreferrer"
            className="btn sec"
            style={{ textDecoration: 'none' }}
          >
            <GithubLogo size={16} />
            <span>Follow on GitHub</span>
          </a>
          {onBackToFilms && (
            <button className="btn sec" onClick={onBackToFilms} style={{ cursor: 'pointer' }}>
              <ArrowLeft size={15} />
              <span>Back to Films</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
