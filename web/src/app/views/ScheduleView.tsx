import React from 'react';
import { CalendarDots, Clock, ArrowSquareOut } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const ScheduleView: React.FC = () => {
  const { nextSlots, topics, isTopicMade } = useStudio();

  // Real slots (Date objects in your local time) grouped by calendar day; each slot takes the next topic that is
  // not made yet, in queue order (what the schedule workflow does).
  const queue = topics.filter(t => !isTopicMade(t));
  const dayKey = (d: Date) => d.toDateString();
  const today = new Date();
  const tomorrow = new Date(Date.now() + 86400000);
  const groups: { label: string; slots: { at: Date; topic?: string; n: number }[] }[] = [];
  nextSlots.slice(0, 15).forEach((at: Date, i: number) => {
    const k = dayKey(at);
    let g = groups.find(x => (x as any).k === k);
    if (!g) {
      const label = k === dayKey(today) ? 'Today' : k === dayKey(tomorrow) ? 'Tomorrow' : at.toLocaleDateString([], { weekday: 'long', day: 'numeric', month: 'short' });
      g = { label, slots: [] }; (g as any).k = k; groups.push(g);
    }
    g.slots.push({ at, topic: queue[i], n: i + 1 });
  });
  const days = groups.slice(0, 3);

  return (
    <div className="content" style={{ overflowY: 'auto' }}>
      <div className="hd">
        <div>
          <h1 className="pt">Schedule</h1>
          <p style={{ color: 'var(--tx3)', fontSize: '13px', marginTop: '4px' }}>
            5 daily slots · Times come from the story schedule on GitHub.
          </p>
        </div>
        <a
          href="https://github.com/FranklinMburu/Autonomous-content-studio/blob/main/.github/workflows/story-schedule.yml"
          target="_blank"
          rel="noopener noreferrer"
          className="btn sec"
          style={{ height: '34px', fontSize: '12.5px', textDecoration: 'none' }}
        >
          <span>Workflow schedule</span>
          <ArrowSquareOut size={13} />
        </a>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
        {days.length === 0 && (
          <div style={{ color: 'var(--tx3)', fontSize: '13px' }}>Loading the schedule from GitHub…</div>
        )}
        {days.map((g, dIdx) => (
          <div
            key={dIdx}
            style={{
              borderRadius: '16px',
              background: 'var(--s1)',
              boxShadow: '0 0 0 1px var(--line) inset',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '10px',
                borderBottom: '1px solid var(--line)',
              }}
            >
              <b style={{ fontSize: '14.5px', color: 'var(--tx)' }}>{g.label}</b>
              <span style={{ fontSize: '11.5px', color: 'var(--tx3)' }}>{g.slots.length} {g.slots.length === 1 ? 'film' : 'films'}</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {g.slots.map((sl, sIdx) => {
                const topic = sl.topic || 'A new topic (the AI suggests one when the queue runs low)';
                const timeSlot = sl.at.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
                return (
                  <div
                    key={sIdx}
                    style={{
                      padding: '10px 12px',
                      borderRadius: '10px',
                      background: 'rgba(255,255,255,0.02)',
                      border: '1px solid var(--line)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span
                        style={{
                          fontSize: '11.5px',
                          fontWeight: 700,
                          color: 'var(--amber2)',
                          fontVariantNumeric: 'tabular-nums',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                        }}
                      >
                        <Clock size={12} />
                        {timeSlot}
                      </span>
                      <span
                        style={{
                          fontSize: '10.5px',
                          color: 'var(--tx3)',
                          textTransform: 'uppercase',
                        }}
                      >
                        #{sl.n}
                      </span>
                    </div>
                    <span style={{ fontSize: '12.5px', color: 'var(--tx2)', lineHeight: 1.4 }}>
                      {topic}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
