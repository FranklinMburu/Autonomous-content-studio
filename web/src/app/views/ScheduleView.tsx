import React from 'react';
import { CalendarDots, Clock, ArrowSquareOut } from '@phosphor-icons/react';
import { useStudio } from '../../context/StudioContext';

export const ScheduleView: React.FC = () => {
  const { nextSlots, topics, studio } = useStudio();

  const days = ['Today', 'Tomorrow', 'Day after tomorrow'];
  const slotsPerDay = 5;

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
        {days.map((dayLabel, dIdx) => (
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
              <b style={{ fontSize: '14.5px', color: 'var(--tx)' }}>{dayLabel}</b>
              <span style={{ fontSize: '11.5px', color: 'var(--tx3)' }}>5 films</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {Array.from({ length: slotsPerDay }, (_, sIdx) => {
                const topicIndex = dIdx * slotsPerDay + sIdx;
                const topic = topics[topicIndex] || `Queued story slot #${topicIndex + 1}`;
                const rawSlot: any = nextSlots[dIdx * slotsPerDay + sIdx] || nextSlots[sIdx];
                const timeSlot =
                  rawSlot instanceof Date
                    ? rawSlot.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
                    : (rawSlot ? String(rawSlot) : `${(8 + sIdx * 3).toString().padStart(2, '0')}:00`);
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
                        Slot {sIdx + 1}
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
