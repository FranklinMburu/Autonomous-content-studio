import React, { useState } from 'react';
import {
  Eye,
  CheckCircle,
  Warning,
  ArrowSquareOut,
  Copy,
  MagicWand,
  Books,
  Check,
} from '@phosphor-icons/react';
import { Chip } from '../../ui/Chip';
import { useStudio } from '../../context/StudioContext';

export const ReviewView: React.FC = () => {
  const { reviewItems, polishItems, films, studio } = useStudio();
  const [selectedIssue, setSelectedIssue] = useState<any>(reviewItems[0] || null);
  const [copied, setCopied] = useState(false);

  const activeIssue = selectedIssue || reviewItems[0];
  const relatedFilm = films.find(f => f.episode === activeIssue?.episode || f.title === activeIssue?.title);

  const polishPrompt =
    polishItems.find(p => p.episode === activeIssue?.episode)?.polishPrompt ||
    `You are the polish step of a YouTube Shorts studio (channel: Hidden Reasons).\nEpisode: ${activeIssue?.title || 'Review'}\nPlease polish narration and pacing for maximum audience retention.`;

  const handleCopy = () => {
    navigator.clipboard.writeText(polishPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!activeIssue) {
    return (
      <div className="content" style={{ overflowY: 'auto' }}>
        <h1 className="pt" style={{ marginBottom: '16px' }}>Review</h1>
        <div
          style={{
            padding: '48px',
            textAlign: 'center',
            background: 'var(--s1)',
            borderRadius: '16px',
            boxShadow: '0 0 0 1px var(--line) inset',
            color: 'var(--tx3)',
            maxWidth: '560px',
            margin: '40px auto',
          }}
        >
          <CheckCircle size={40} color="#3FB950" weight="duotone" style={{ margin: '0 auto 12px' }} />
          <p style={{ color: 'var(--tx)', fontSize: '15px', fontWeight: 600, marginBottom: '6px' }}>
            Nothing to review
          </p>
          <p style={{ fontSize: '13px' }}>Every film passed its checks and vision guards.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="rv">
        {/* Left: Player */}
        <div className="player">
          {relatedFilm?.video?.url ? (
            <video
              src={relatedFilm.video.url}
              controls
              playsInline
              preload="metadata"
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          ) : relatedFilm?.contact?.url ? (
            <img src={relatedFilm.contact.url} alt={activeIssue.title} />
          ) : (
            <div
              style={{
                width: '100%',
                height: '100%',
                background: '#0D0E14',
                display: 'grid',
                placeItems: 'center',
                color: 'var(--tx3)',
              }}
            >
              <Eye size={48} weight="duotone" />
            </div>
          )}
          <div className="ctl">
            <i />
            <span>0:21 / 0:52</span>
          </div>
        </div>

        {/* Right: Review details & Actions */}
        <div className="rp">
          <div className="badge">
            <Eye size={15} weight="duotone" />
            <span>Held for review</span>
          </div>

          <h1 className="pt" style={{ fontSize: '24px', margin: '10px 0 6px' }}>
            {activeIssue.title}
          </h1>
          <p className="muted" style={{ fontSize: '13.5px', marginBottom: '18px' }}>
            26 of 28 shots passed every check. Two were repainted 3 times and are still weak.
          </p>

          {/* Checks passed */}
          <div className="checks">
            <div>
              <CheckCircle size={16} weight="duotone" className="ic" />
              <span>8 sources · every claim supported</span>
            </div>
            <div>
              <CheckCircle size={16} weight="duotone" className="ic" />
              <span>Length 50.3 s · loudness −14.1 LUFS</span>
            </div>
            <div className="w">
              <Warning size={16} weight="duotone" className="ic" color="var(--amber2)" />
              <span>2 weak shots</span>
            </div>
          </div>

          {/* Weak shots */}
          <div className="wks">
            <div className="wk">
              <div style={{ width: '62px', height: '96px', background: '#1C1618', borderRadius: '8px', display: 'grid', placeItems: 'center', color: 'var(--amber2)' }}>
                <Warning size={20} />
              </div>
              <div>
                <b>irritated</b>
                <span>"Are there red hands?"</span>
                <span className="ans">checker: no</span>
              </div>
            </div>
            <div className="wk">
              <div style={{ width: '62px', height: '96px', background: '#1C1618', borderRadius: '8px', display: 'grid', placeItems: 'center', color: 'var(--amber2)' }}>
                <Warning size={20} />
              </div>
              <div>
                <b>hook</b>
                <span>"Is a man wrapping a leg in towels?"</span>
                <span className="ans">checker: no</span>
              </div>
            </div>
          </div>

          {/* Action buttons (Approve / Repaint) */}
          <div className="acts">
            <a
              href={activeIssue.url || studio.links.issue(activeIssue.number)}
              target="_blank"
              rel="noopener noreferrer"
              className="btn pri"
              style={{ height: '44px', flex: 1, justifyContent: 'center', textDecoration: 'none' }}
              title="Comment approve on GitHub"
            >
              <CheckCircle size={15} weight="bold" />
              <span>Approve ↗</span>
            </a>
            <a
              href={activeIssue.url || studio.links.issue(activeIssue.number)}
              target="_blank"
              rel="noopener noreferrer"
              className="btn sec"
              style={{ height: '44px', flex: 1, justifyContent: 'center', textDecoration: 'none' }}
              title="Comment repaint on GitHub"
            >
              <MagicWand size={16} weight="duotone" />
              <span>Repaint 2 shots · ~15 min ↗</span>
            </a>
          </div>

          {/* Polish with Claude */}
          <div className="polish">
            <div className="ph2">
              <MagicWand size={16} weight="duotone" />
              <b>Or polish with Claude</b>
              <span className="faint">copy → paste in claude.ai → paste back</span>
            </div>
            <div className="copybox">
              <code>{polishPrompt}</code>
              <button
                className="btn sec"
                onClick={handleCopy}
                style={{ height: '30px', fontSize: '12.5px', cursor: 'pointer' }}
              >
                {copied ? <Check size={14} color="#3FB950" /> : <Copy size={14} />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
          </div>

          {/* Sources behind every line */}
          <div className="srcs">
            <div className="ph2" style={{ marginBottom: '6px' }}>
              <Books size={16} weight="duotone" />
              <b>Sources behind every line</b>
            </div>
            <div className="src">
              <span className="n">1</span>
              <div>
                <b>Phenol</b>
                <span>en.wikipedia.org · 4 claims</span>
              </div>
              <span className="chip ok">supported</span>
            </div>
            <div className="src">
              <span className="n">2</span>
              <div>
                <b>Joseph Lister</b>
                <span>en.wikipedia.org · 3 claims</span>
              </div>
              <span className="chip ok">supported</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
