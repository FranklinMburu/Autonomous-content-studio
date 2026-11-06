import React, { useState, useEffect } from 'react';
import {
  Eye,
  CheckCircle,
  Warning,
  ArrowSquareOut,
  Copy,
  MagicWand,
  Books,
  Check,
  ArrowLeft,
} from '@phosphor-icons/react';
import { Chip } from '../../ui/Chip';
import { useStudio } from '../../context/StudioContext';
import { sourceSummary } from '../../lib/github-data.js';

export interface ReviewViewProps {
  initialIssueId?: string;
  onBack?: () => void;
  onSelectIssue?: (issueId: string) => void;
}

export const ReviewView: React.FC<ReviewViewProps> = ({
  initialIssueId,
  onBack,
  onSelectIssue,
}) => {
  const { reviewItems, polishItems, films, studio } = useStudio();
  const [selectedIssue, setSelectedIssue] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (initialIssueId) {
      const match = reviewItems.find(
        r => String(r.number || r.id) === String(initialIssueId) || r.episode === initialIssueId
      );
      if (match) setSelectedIssue(match);
    } else if (!selectedIssue && reviewItems.length > 0) {
      setSelectedIssue(reviewItems[0]);
    }
  }, [reviewItems, initialIssueId]);

  const activeIssue = selectedIssue || reviewItems[0];
  // the film this review issue is about: same release tag, else the same episode folder
  const relatedFilm = films.find(f => (activeIssue?.tag && f.release?.tag === activeIssue.tag) ||
    (activeIssue?.episode && String(activeIssue.episode).endsWith(f.id)));
  // the polish box only appears when a real polish issue exists for this episode (no invented prompt)
  const polishIssue = polishItems.find(p => p.episode && p.episode === activeIssue?.episode);
  const polishPrompt: string = polishIssue?.polishPrompt || '';
  // the exact release this issue points at (its run), else the newest run of the same film
  const [rels, setRels] = useState<any[]>([]);
  useEffect(() => { studio.releases().then(setRels).catch(() => {}); }, [studio]);
  const rel: any = rels.find(r => r.tag === activeIssue?.tag) || relatedFilm?.release || null;
  const sources = sourceSummary(rel?.sources || []);
  const failed: string[] = activeIssue?.failedShots?.length ? activeIssue.failedShots
    : ((rel?.problems || '').match(/picture check:\s*(.+)$/) || [, ''])[1].split(',').map((x: string) => x.trim()).filter(Boolean);
  const len = ((rel?.checks || '').match(/length\s+([\d.]+)\s*s/) || [])[1];
  const lufs = ((rel?.checks || '').match(/loudness\s+(-?[\d.]+)\s*LUFS/) || [])[1];
  const videoUrl = rel?.video?.url || relatedFilm?.video?.url;
  const contactUrl = rel?.contact || (typeof relatedFilm?.contact === 'string' ? relatedFilm.contact : null);

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
          {videoUrl ? (
            <video
              src={videoUrl}
              controls
              playsInline
              preload="metadata"
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          ) : contactUrl ? (
            <img src={contactUrl} alt={activeIssue.title} />
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
            {failed.length
              ? `${failed.length} ${failed.length === 1 ? 'shot' : 'shots'} still failed the picture check after 3 tries. Everything else passed.`
              : 'The film failed a final check and is held until you decide.'}
          </p>

          {/* Checks passed */}
          <div className="checks">
            <div>
              <CheckCircle size={16} weight="duotone" className="ic" />
              <span>{sources.length ? `${sources.length} ${sources.length === 1 ? 'source' : 'sources'} saved with the script` : 'Sources: see the release notes'}</span>
            </div>
            <div>
              <CheckCircle size={16} weight="duotone" className="ic" />
              <span>{len ? `Length ${len} s` : 'Length —'}{lufs ? ` · loudness ${lufs.replace('-', '−')} LUFS` : ''}</span>
            </div>
            <div className="w">
              <Warning size={16} weight="duotone" className="ic" color="var(--amber2)" />
              <span>{failed.length} weak {failed.length === 1 ? 'shot' : 'shots'}</span>
            </div>
          </div>

          {/* Weak shots: the real names from the issue / release notes; the contact sheet shows the pictures */}
          {failed.length > 0 && (
            <div className="wks" style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {failed.map(n => (
                <span key={n} className="chip rev" style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                  <Warning size={12} /> {n.replace(/_/g, ' ')}
                </span>
              ))}
              {contactUrl && (
                <a href={contactUrl} target="_blank" rel="noopener noreferrer" className="chip" style={{ textDecoration: 'none' }}>Contact sheet ↗</a>
              )}
            </div>
          )}

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
              <span>{failed.length ? `Repaint ${failed.length} ${failed.length === 1 ? 'shot' : 'shots'} ↗` : 'Repaint ↗'}</span>
            </a>
          </div>

          {/* Polish with Claude: only when a real polish issue exists for this episode */}
          {polishPrompt && (
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
          )}

          {/* Sources behind every line */}
          <div className="srcs">
            <div className="ph2" style={{ marginBottom: '6px' }}>
              <Books size={16} weight="duotone" />
              <b>Sources behind every line</b>
            </div>
            {sources.length === 0 ? (
              <div className="src"><div><span>No sources listed in this film's release notes.</span></div></div>
            ) : sources.map((src: any, i: number) => (
              <a key={src.url} className="src" href={src.url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', color: 'inherit' }}>
                <span className="n">{i + 1}</span>
                <div>
                  <b>{src.host}</b>
                  <span>{src.claims} claim{src.claims === 1 ? '' : 's'} · {src.url.replace(/^https?:\/\/(www\.)?/, '').slice(0, 60)}</span>
                </div>
                <ArrowSquareOut size={13} className="ic faint" />
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
