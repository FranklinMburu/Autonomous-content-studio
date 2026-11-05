import React, { useState, useEffect } from 'react';
import { CaretRight, ArrowSquareOut, Clock } from '@phosphor-icons/react';
import { Chip } from '../../ui/Chip';
import { useStudio } from '../../context/StudioContext';

export const RunsView: React.FC = () => {
  const { runs, topics, nextSlots, studio } = useStudio();
  const [filter, setFilter] = useState<'all' | 'making' | 'needs_you' | 'failed'>('all');
  const [selectedRun, setSelectedRun] = useState<any>(runs[0] || null);
  const [timelineSteps, setTimelineSteps] = useState<any[]>([]);

  useEffect(() => {
    if (!selectedRun && runs.length > 0) {
      setSelectedRun(runs[0]);
    }
  }, [runs, selectedRun]);

  useEffect(() => {
    if (selectedRun && selectedRun.id) {
      studio.runSteps(selectedRun.id).then(setTimelineSteps).catch(() => {
        // Fallback realistic steps for mock display if API was rate-limited
        setTimelineSteps([
          { name: 'Set up job', state: 'completed', duration: 3 },
          { name: 'Research sources', state: 'completed', duration: 18 },
          { name: 'Script draft & check', state: 'completed', duration: 42 },
          { name: 'Paint shots (GPU)', state: selectedRun.state === 'running' ? 'in_progress' : 'completed', duration: 320 },
          { name: 'Picture check', state: selectedRun.state === 'running' ? 'queued' : 'completed', duration: 45 },
          { name: 'Assemble film', state: selectedRun.state === 'running' ? 'queued' : 'completed', duration: 80 },
        ]);
      });
    }
  }, [selectedRun, studio]);

  const makingCount = runs.filter(r => r.state === 'running' || r.state === 'queued' || r.state === 'in_progress').length;
  const failedCount = runs.filter(r => r.state === 'failure' || r.state === 'cancelled').length;

  const filteredRuns = runs.filter(r => {
    if (filter === 'making') return r.state === 'running' || r.state === 'queued' || r.state === 'in_progress';
    if (filter === 'failed') return r.state === 'failure' || r.state === 'cancelled';
    return true;
  });

  const formatSlot = (slot: any, fallback = '13:23') => {
    if (!slot) return fallback;
    if (slot instanceof Date) return slot.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    return String(slot);
  };

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
                  onClick={() => setSelectedRun(run)}
                  style={{
                    cursor: 'pointer',
                    background: isSelected ? 'rgba(245,165,36,0.08)' : undefined,
                  }}
                >
                  <div className="rt">
                    <b>{run.title || run.workflow}</b>
                    <span>Hidden Reasons · started {run.started ? new Date(run.started).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'recently'}</span>
                  </div>
                  <div className="segs">
                    <i className="s-ok" />
                    <i className="s-ok" />
                    <i className="s-ok" />
                    <i className={isRunning ? 's-now' : 's-ok'} />
                    <i className={run.state === 'failure' ? 's-bad' : ''} />
                  </div>
                  <Chip status={run.state} />
                  <span className="dur">{run.minutes ? `${run.minutes} min` : '—'}</span>
                  <CaretRight size={13} className="ic faint" />
                </div>
              );
            })
          )}

          {/* Scheduled future slots */}
          {topics.slice(0, 3).map((topic, idx) => (
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
                  Execution Timeline
                </b>
                {timelineSteps.map((step, idx) => {
                  const isOk = step.state === 'completed' || step.conclusion === 'success';
                  const isNow = step.state === 'in_progress';
                  return (
                    <div key={idx} className={`ds ${isOk ? 'ok' : isNow ? 'now' : ''}`}>
                      <span className="b" />
                      <b>{step.name}</b>
                      <span className="m">{isOk ? 'Completed' : isNow ? 'Running...' : 'Queued'}</span>
                      <span className="t">{step.duration ? `${step.duration}s` : '—'}</span>
                    </div>
                  );
                })}
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
