import React, { useState } from 'react';
import { ArrowSquareOut, CheckCircle, CircleNotch, DownloadSimple, Info, Key, Lightning, Play, ShieldCheck, WarningCircle, X, XCircle } from '@phosphor-icons/react';
import { channelOf, Stage, STAGE_HELP } from '../lib/channels';
import { useActions, Task } from '../context/ActionsContext';
import { githubUrl } from '../lib/actions';
import { ago } from '../lib/journey';

// ---------- layout ----------
export const Page: React.FC<{ title: React.ReactNode; sub?: React.ReactNode; actions?: React.ReactNode; children: React.ReactNode; wide?: boolean }> =
  ({ title, sub, actions, children, wide }) => (
    <div className="pg">
      <div className={`pg-in${wide ? ' wide' : ''}`}>
        <div className="pg-head">
          <div style={{ minWidth: 0 }}>
            <h1 className="pg-t">{title}</h1>
            {sub && <div className="pg-sub">{sub}</div>}
          </div>
          {actions && <div className="pg-act">{actions}</div>}
        </div>
        {children}
      </div>
    </div>
  );

export const Section: React.FC<{ title: React.ReactNode; hint?: React.ReactNode; right?: React.ReactNode; children: React.ReactNode }> =
  ({ title, hint, right, children }) => (
    <section className="sec">
      <div className="sec-h"><div><h2 className="sec-t">{title}</h2>{hint && <div className="sec-hint">{hint}</div>}</div>{right}</div>
      {children}
    </section>
  );

export const Empty: React.FC<{ icon?: React.ReactNode; title: string; text?: React.ReactNode; action?: React.ReactNode }> = ({ icon, title, text, action }) => (
  <div className="empty">
    <div className="empty-ic">{icon || <Info size={20} weight="duotone" />}</div>
    <b>{title}</b>
    {text && <p>{text}</p>}
    {action}
  </div>
);

export const Tabs: React.FC<{ tabs: { key: string; label: string; count?: number }[]; value: string; onChange: (k: string) => void }> = ({ tabs, value, onChange }) => (
  <div className="tabs" role="tablist">
    {tabs.map(t => (
      <button key={t.key} role="tab" aria-selected={value === t.key} className={value === t.key ? 'on' : ''} onClick={() => onChange(t.key)}>
        {t.label}{t.count != null && <span className="n">{t.count}</span>}
      </button>
    ))}
  </div>
);

// ---------- channel + stage marks ----------
export const LaneBadge: React.FC<{ code?: string | null; full?: boolean }> = ({ code, full }) => {
  const ch = channelOf(code);
  if (!ch) return null;
  return (
    <span className="lane" style={{ ['--lc' as any]: ch.color }} title={ch.name}>
      <i />{full ? ch.name : ch.code}
    </span>
  );
};

const STAGE_CLASS: Record<string, string> = { Picked: '', Making: 'run', Review: 'rev', Approved: 'ok', Posted: 'ok', Skipped: 'mute' };
export const StageChip: React.FC<{ stage?: string | null; label?: string }> = ({ stage, label }) =>
  stage ? <span className={`chip ${STAGE_CLASS[stage] || ''}`} title={STAGE_HELP[stage as Stage] || ''}>{label || stage}</span> : null;

export const Score: React.FC<{ v?: number | null; size?: 'sm' | 'lg' }> = ({ v, size = 'sm' }) => {
  if (v == null) return null;
  const tone = v >= 8 ? 'ok' : v >= 6 ? 'rev' : 'bad';
  return <span className={`score ${tone} ${size}`} title="The AI reviewer's score out of 10 (its guess at reaching 250K+ views)">{v.toFixed(v % 1 ? 1 : 0)}<small>/10</small></span>;
};

// ---------- video ----------
/** Plays a video stored in a GitHub release. Release files are served as downloads; most browsers still play them.
 *  If one does not (some iPhones), the person gets clear buttons to open or download it instead. */
export const Player: React.FC<{ src?: string | null; vertical?: boolean; poster?: string | null; title?: string }> = ({ src, vertical, poster, title }) => {
  const [failed, setFailed] = useState(false);
  const [on, setOn] = useState(false);
  if (!src) return <div className={`player none${vertical ? ' v' : ''}`}><span>No video file yet</span></div>;
  return (
    <div className={`player${vertical ? ' v' : ''}`}>
      {failed ? (
        <div className="player-fail">
          <WarningCircle size={22} />
          <p>This browser won't play the file here.</p>
          <a className="btn sec" href={src} target="_blank" rel="noopener noreferrer"><DownloadSimple size={16} /> Open or download</a>
        </div>
      ) : on ? (
        <video src={src} controls autoPlay playsInline preload="metadata" poster={poster || undefined} aria-label={title} onError={() => setFailed(true)} />
      ) : (
        <button className="player-start" onClick={() => setOn(true)} aria-label={`Play ${title || 'video'}`}
                style={poster ? { backgroundImage: `url(${poster})` } : undefined}>
          <span className="pl"><Play size={22} weight="fill" /></span>
        </button>
      )}
    </div>
  );
};

// ---------- actions ----------
/** A button that DOES something. Without a GitHub connection on this device it explains and opens the connect panel. */
export const ActButton: React.FC<{
  onRun: () => Promise<any> | any; children: React.ReactNode; variant?: 'pri' | 'sec' | 'ghost' | 'danger';
  confirm?: string; disabled?: boolean; title?: string; small?: boolean;
}> = ({ onRun, children, variant = 'sec', confirm, disabled, title, small }) => {
  const { hasToken, setNeedToken } = useActions();
  const [busy, setBusy] = useState(false);
  return (
    <button className={`btn ${variant}${small ? ' sm' : ''}`} disabled={disabled || busy} title={title}
      onClick={async e => {
        e.stopPropagation();
        if (!hasToken) { setNeedToken(true); return; }
        if (confirm && !window.confirm(confirm)) return;
        setBusy(true);
        try { await onRun(); } finally { setBusy(false); }
      }}>
      {busy ? <CircleNotch size={15} className="spin" /> : null}{children}
    </button>
  );
};

export const ExtLink: React.FC<{ href: string; children: React.ReactNode; className?: string }> = ({ href, children, className }) => (
  <a href={href} target="_blank" rel="noopener noreferrer" className={className || 'xl'}>{children}<ArrowSquareOut size={13} /></a>
);

// ---------- the activity tray: what you started, live ----------
const TASK_ICON: Record<string, React.ReactNode> = {
  sending: <CircleNotch size={16} className="spin" />, queued: <CircleNotch size={16} className="spin" />, running: <CircleNotch size={16} className="spin" />,
  success: <CheckCircle size={16} weight="fill" color="var(--ok)" />, done: <CheckCircle size={16} weight="fill" color="var(--ok)" />,
  failure: <XCircle size={16} weight="fill" color="var(--bad)" />, error: <XCircle size={16} weight="fill" color="var(--bad)" />,
  cancelled: <XCircle size={16} color="var(--tx3)" />,
};
const TASK_WORD: Record<string, string> = { sending: 'Sending…', queued: 'Starting', running: 'Running', success: 'Done', done: 'Done',
  failure: 'Failed', error: 'Did not start', cancelled: 'Stopped' };

export const ActivityTray: React.FC<{ onOpen?: (route: string) => void }> = ({ onOpen }) => {
  const { tasks, dismiss } = useActions();
  const [open, setOpen] = useState(true);
  const recent = tasks.filter(t => !t.finished || Date.now() - t.finished < 30 * 60e3).slice(0, 5);
  if (!recent.length) return null;
  const live = recent.filter(t => !t.finished).length;
  return (
    <div className="tray" role="status" aria-live="polite">
      <button className="tray-h" onClick={() => setOpen(!open)}>
        <Lightning size={15} weight="duotone" />
        <b>{live ? `${live} running` : 'Your recent actions'}</b>
        <span className="faint">{open ? 'Hide' : 'Show'}</span>
      </button>
      {open && recent.map((t: Task) => (
        <div key={t.id} className={`tray-i ${t.state}`}>
          {TASK_ICON[t.state]}
          <div className="tray-b">
            <div className="tray-l">{t.label}</div>
            <div className="tray-s">
              {TASK_WORD[t.state]}{t.progress && !t.finished ? ` · step ${t.progress[0]} of ${t.progress[1]}` : ''}
              {t.step && !t.finished ? ` · ${t.step}` : ''}{t.finished ? ` · ${ago(new Date(t.finished).toISOString())}` : ''}
            </div>
            {t.error && <div className="tray-e">{t.error}</div>}
            {(t.state === 'success' || t.state === 'done') && t.next && <div className="tray-n">{t.next}</div>}
            <div className="tray-a">
              {t.runId && onOpen && <button onClick={() => onOpen(`/app/runs/${t.runId}`)}>Follow it</button>}
              {t.runUrl && <a href={t.runUrl} target="_blank" rel="noopener noreferrer">On GitHub</a>}
              {t.target && t.finished && onOpen && <button onClick={() => onOpen(t.target!)}>Open</button>}
            </div>
          </div>
          {t.finished && <button className="tray-x" aria-label="Dismiss" onClick={() => dismiss(t.id)}><X size={13} /></button>}
        </div>
      ))}
    </div>
  );
};

// ---------- connect GitHub (once per device) ----------
export const ConnectPanel: React.FC<{ compact?: boolean }> = ({ compact }) => {
  const { connection, connecting, connectError, connect, disconnect, hasToken } = useActions();
  const [val, setVal] = useState('');
  if (hasToken && connection) {
    return (
      <div className="connect ok">
        <ShieldCheck size={22} weight="duotone" color="var(--ok)" />
        <div style={{ flex: 1 }}>
          <b>Connected as {connection.login || 'you'}</b>
          <p className="muted">{connection.canAct ? 'Buttons in the app act for you on GitHub (start videos, approve, move cards).' : 'Connected, but this token cannot start workflows: see the steps below.'}
            {connection.expires ? ` The token expires ${new Date(connection.expires).toLocaleDateString()}.` : ''}</p>
        </div>
        <button className="btn sec" onClick={disconnect}>Forget on this device</button>
      </div>
    );
  }
  return (
    <div className="connect">
      {!compact && <p className="muted" style={{ marginBottom: 12 }}>Watching needs nothing. To <b>act</b> from here (start a video, approve, move a card), connect GitHub once on this device. It takes about 2 minutes.</p>}
      <ol className="steps">
        <li>Open <ExtLink href="https://github.com/settings/personal-access-tokens/new">GitHub → new fine-grained token</ExtLink> (sign in if asked).</li>
        <li>Name it <b>Studio app</b>. Expiration: <b>90 days</b>.</li>
        <li>Repository access: <b>Only select repositories</b> → <b>Autonomous-content-studio</b>.</li>
        <li>Permissions → Repository: <b>Actions: Read and write</b> and <b>Issues: Read and write</b>. Nothing else.</li>
        <li>Press <b>Generate token</b>, copy it, and paste it below.</li>
      </ol>
      <div className="connect-row">
        <Key size={16} className="faint" />
        <input type="password" autoComplete="off" spellCheck={false} placeholder="Paste the token (github_pat_…)" value={val}
               onChange={e => setVal(e.target.value)} aria-label="GitHub token" />
        <button className="btn pri" disabled={!val.trim() || connecting} onClick={() => connect(val).then(ok => ok && setVal(''))}>
          {connecting ? <CircleNotch size={15} className="spin" /> : null}Connect
        </button>
      </div>
      {connectError && <div className="err"><WarningCircle size={15} /> {connectError}</div>}
      <p className="fine">The token stays in this browser only and is sent only to GitHub. It can start workflows and comment on issues in this one repository, nothing else; every change to files or to Notion is checked by a workflow first. Remove it any time here or on GitHub.</p>
    </div>
  );
};

export const ConnectSheet: React.FC = () => {
  const { needToken, setNeedToken, hasToken, connection } = useActions();
  if (!needToken || (hasToken && connection?.canAct)) return null;
  return (
    <div className="sheet-bg" onClick={() => setNeedToken(false)}>
      <div className="sheet" role="dialog" aria-modal="true" aria-label="Connect GitHub" onClick={e => e.stopPropagation()}>
        <div className="sheet-h"><b>Connect GitHub to do this from here</b><button aria-label="Close" onClick={() => setNeedToken(false)}><X size={16} /></button></div>
        <ConnectPanel compact />
        <p className="fine">Prefer not to? Every action can also be done on <ExtLink href={githubUrl('/actions')}>GitHub</ExtLink>.</p>
      </div>
    </div>
  );
};
