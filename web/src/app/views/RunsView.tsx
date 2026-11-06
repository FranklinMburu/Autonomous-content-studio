import React, { useState, useEffect } from 'react';
import { CaretRight, ArrowSquareOut, Clock, ArrowLeft } from '@phosphor-icons/react';
import { Chip } from '../../ui/Chip';
import { useStudio } from '../../context/StudioContext';
import { topicMade } from '../../lib/github-data.js';

export interface RunsViewProps {
  initialRunId?: string;
  onBack?: () => void;
  onSelectRun?: (runId: string) => void;
}

export const RunsView: React.FC<RunsViewProps> = ({
  initialRunId,
  onBack,
  onSelectRun,
}) => {
  const { runs, films, topics, nextSlots, studio } = useStudio();
  const [filter, setFilter] = useState<'all' | 'making' | 'needs_you' | 'failed'>('all');
  const [selectedRun, setSelectedRun] = useState<any>(null);
  const [timelineSteps, setTimelineSteps] = useState<any[]>([]);
  const [mobileDetailOpen, setMobileDetailOpen] = useState(false);

  useEffect(() => {
    if (initialRunId) {
      const match = runs.find(r => String(r.id) === String(initialRunId));
      if (match) {
        setSelectedRun(match);
        setMobileDetailOpen(true);
      }
    } else if (!selectedRun && runs.length > 0) {
      setSelectedRun(runs[0]);
    }
  }, [runs, initialRunId]);

  useEffect(() => {
    if (selectedRun && selectedRun.id) {
      const live = selectedRun.state === 'running' || selectedRun.state === 'queued';
      setTimelineSteps([]);
      studio.runSteps(selectedRun.id, live).then(setTimelineSteps).catch(() => setTimelineSteps([]));
    }
  }, [selectedRun, studio]);

  // step bars for the rows: real steps for the newest runs (they come from the feed, no extra GitHub calls)
  const [rowSteps, setRowSteps] = useState<Record<string, any[]>>({});
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const out: Record<string, any[]> = {};
      for (const r of runs.slice(0, 12)) {
        try { out[r.id] = await studio.runSteps(r.id); } catch { /* not in the feed: the bar shows the state only */ }
      }
      if (!cancelled) setRowSteps(out);
    })();
    return () => { cancelled = true; };
  }, [runs, studio]);

  const makingCount = runs.filter(r => r.state === 'running' || r.state === 'queued' || r.state === 'in_progress').length;
  const failedCount = runs.filter(r => r.state === 'failure' || r.state === 'cancelled').length;

  const filteredRuns = runs.filter(r => {
    if (filter === 'making') return r.state === 'running' || r.state === 'queued' || r.state === 'in_progress';
    if (filter === 'failed') return r.state === 'failure' || r.state === 'cancelled';
    return true;
  });

  const formatSlot = (slot: any, fallback = '—') => {
    if (!slot) return fallback;
    if (slot instanceof Date) return slot.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    return String(slot);
  };

  const isMobile = typeof window !== 'undefined' && window.innerWidth < 640;

  if (isMobile && mobileDetailOpen && selectedRun) {
    return (
      <div className="content" style={{ overflowY: 'auto' }}>
        <button
          onClick={() => {
            setMobileDetailOpen(false);
            if (onBack) onBack();
          }}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'none',
            border: 'none',
            color: 'var(--tx3)',
            cursor: 'pointer',
            fontSize: '13px',
            marginBottom: '16px',
            padding: 0,
          }}
        >
          <ArrowLeft size={16} />
          <span>Back to Runs</span>
        </button>

        <div className="detail" style={{ width: '100%' }}>
          <div className="dtop">
            <b style={{ fontSize: '15px' }}>{selectedRun.title || selectedRun.workflow}</b>
            <Chip status={selectedRun.state} />
          </div>
          <div className="meta">
            <span>Started: {selectedRun.started ? new Date(selectedRun.started).toLocaleTimeString() : '—'}</span>
            <span>Duration: {selectedRun.minutes ? `${selectedRun.minutes} min` : '—'}</span>
          </div>

          <div style={{ marginTop: '16px' }}>
            <b style={{ fontSize: '13px', color: 'var(--tx)', display: 'block', marginBottom: '10px' }}>
              Steps
            </b>
            <Timeline steps={timelineSteps} />
          </div>

          {selectedRun.url && (
            <div style={{ marginTop: '24px' }}>
              <a
                href={selectedRun.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn sec"
                style={{ width: '100%', justifyContent: 'center', height: '36px', fontSize: '13px', textDecoration: 'none' }}
              >
                <span>Open on GitHub</span>
                <ArrowSquareOut size={14} />
              </a>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <h1 className="pt">Runs</h1>
        <div className="filters">
          <span className={filter === 'all' ? 'on' : ''} onClick={() => setFilter('all')} style={{ cursor: 'pointer' }}>
            All {runs.length}
          </span>
          <span className={filter === 'making' ? 'on' : ''} onClick={() => setFilter('making')} style={{ cursor: 'pointer' }}>
            Making {makingCount}
          </span>
          <span className={filter === 'failed' ? 'on' : ''} onClick={() => setFilter('failed')} style={{ cursor: 'pointer' }}>
            Failed {failedCount}
          </span>
        </div>
      </div>

      <div className="split">
        {/* Runs List */}
        <div className="list">
          {filteredRuns.length === 0 ? (
            <div style={{ padding: '36px', textAlign: 'center', color: 'var(--tx3)', fontSize: '13.5px' }}>
              No runs yet today. Next film starts at {formatSlot(nextSlots[0])}.
            </div>
          ) : (
            filteredRuns.map(run => {
              const isSelected = selectedRun?.id === run.id;
              const isRunning = run.state === 'running' || run.state === 'in_progress';
              return (
                <div
                  key={run.id}
                  className="runrow"
                  onClick={() => {
                    setSelectedRun(run);
                    setMobileDetailOpen(true);
                    if (onSelectRun) onSelectRun(String(run.id));
                  }}
                  style={{
                    cursor: 'pointer',
                    background: isSelected ? 'rgba(245,165,36,0.08)' : undefined,
                  }}
                >
                  <div className="rt">
                    <b>{run.title || run.workflow}</b>
                    <span>{run.workflow} · {run.started ? new Date(run.started).toLocaleString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' }) : '—'}</span>
                  </div>
                  <Segs steps={rowSteps[run.id]} state={run.state} />
                  <Chip status={run.state} />
                  <span className="dur">{run.minutes ? `${run.minutes} min` : '—'}</span>
                  <CaretRight size={13} className="ic faint" />
                </div>
              );
            })
          )}

          {/* Scheduled future slots */}
          {topics.filter((x: string) => !topicMade(x, films)).slice(0, 3).map((topic, idx) => (
            <div key={idx} className="runrow sched">
              <span className="slot">{formatSlot(nextSlots[idx])}</span>
              <div className="rt">
                <b>{topic}</b>
                <span>Hidden Reasons · Scheduled</span>
              </div>
              <span
                style={{
                  fontSize: '11.5px',
                  color: 'var(--tx3)',
                  padding: '2px 8px',
                  borderRadius: '99px',
                  background: 'rgba(255,255,255,0.04)',
                }}
              >
                Scheduled
              </span>
            </div>
          ))}
        </div>

        {/* Selected Run Detail Timeline */}
        <div className="detail">
          {selectedRun ? (
            <>
              <div className="dtop">
                <b style={{ fontSize: '15px' }}>{selectedRun.title || selectedRun.workflow}</b>
                <Chip status={selectedRun.state} />
              </div>
              <div className="meta">
                <span>Started: {selectedRun.started ? new Date(selectedRun.started).toLocaleTimeString() : '—'}</span>
                <span>Duration: {selectedRun.minutes ? `${selectedRun.minutes} min` : '—'}</span>
              </div>

              <div style={{ marginTop: '16px' }}>
                <b style={{ fontSize: '13px', color: 'var(--tx)', display: 'block', marginBottom: '10px' }}>
                  Steps
                </b>
                <Timeline steps={timelineSteps} />
              </div>

              {selectedRun.url && (
                <div style={{ marginTop: '24px' }}>
                  <a
                    href={selectedRun.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn sec"
                    style={{ width: '100%', justifyContent: 'center', height: '36px', fontSize: '13px', textDecoration: 'none' }}
                  >
                    <span>Open on GitHub</span>
                    <ArrowSquareOut size={14} />
                  </a>
                </div>
              )}
            </>
          ) : (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--tx3)', fontSize: '13px' }}>
              Select a run to view its details
            </div>
          )}
        </div>
      </div>
    </div>
  );
};


const STATE_LABEL: Record<string, string> = { done: 'Done', running: 'Running', waiting: 'Waiting', failed: 'Failed', skipped: 'Skipped' };

const fmtSeconds = (s: number | null | undefined) =>
  s == null ? '—' : s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${String(s % 60).padStart(2, '0')}s`;

/** The real steps of one GitHub Actions run (DATA_CONTRACT: runSteps). */
const Timeline: React.FC<{ steps: any[] }> = ({ steps }) => {
  if (!steps.length) return <div className="ds-empty">Steps load from GitHub…</div>;
  return (
    <div className="dsl">
      {steps.map((st, i) => (
        <div key={i} className={`ds ${st.state === 'done' ? 'ok' : st.state === 'running' ? 'now' : st.state === 'failed' ? 'bad' : ''}`}>
          <span className="b" />
          <b title={st.name}>{st.name}</b>
          <span className="m">{STATE_LABEL[st.state] || st.state}</span>
          <span className="t">{fmtSeconds(st.seconds)}</span>
        </div>
      ))}
    </div>
  );
};

/** Step bar of a run row: one segment per real step (up to 8), or the run's state when steps aren't loaded. */
const Segs: React.FC<{ steps?: any[]; state: string }> = ({ steps, state }) => {
  let cls: string[];
  if (steps && steps.length) {
    const s = steps.filter(x => x.state !== 'skipped');
    const per = Math.max(1, Math.ceil(s.length / 8));
    cls = [];
    for (let i = 0; i < s.length; i += per) {
      const g = s.slice(i, i + per);
      cls.push(g.some(x => x.state === 'failed') ? 's-bad' : g.some(x => x.state === 'running') ? 's-now' : g.every(x => x.state === 'done') ? 's-ok' : '');
    }
  } else {
    const n = 8;
    cls = Array.from({ length: n }, (_, i) =>
      state === 'success' ? 's-ok' : state === 'failure' ? (i === n - 1 ? 's-bad' : '') : state === 'running' ? (i === 0 ? 's-now' : '') : '');
  }
  return <div className="segs">{cls.map((c, i) => <i key={i} className={c} />)}</div>;
};
